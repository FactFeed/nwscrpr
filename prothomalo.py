"""Prothom Alo Daily News Scraper
=================================

Purpose:
	Collect today's published news articles from https://www.prothomalo.com
	extracting for each article:
		- title
		- full text (concatenated paragraphs)
		- publication date/time (ISO 8601, Asia/Dhaka timezone)
		- list of image URLs found inside the article body (unique, absolute)
		- article URL
		- section / category (if discoverable)

Features:
	* Respects (basic) robots.txt crawl-delay if present.
	* Rotating realistic User-Agent headers per request.
	* Retry logic with exponential backoff (HTTP + network errors).
	* Graceful error handling & logging with clear diagnostics.
	* Filtering so only articles whose published date is today (local BD) are kept.
	* Optional concurrency using ThreadPoolExecutor (configurable workers).
	* Randomized polite delays between requests (jitter) to reduce block risk.
	* CLI arguments for flexibility (output formats, limits, workers, etc.).
	* Dry-run mode for fast testing without network calls (validates pipeline).
	* Saves structured output to JSON and/or CSV with deterministic filenames.

Dependencies (see requirements.txt):
	requests, beautifulsoup4

Usage Examples (PowerShell):
	# Scrape up to 50 articles (default), output both formats
	python prothomalo.py --formats json csv

	# Limit to 15 articles, JSON only, custom output dir
	python prothomalo.py --limit 15 --formats json --output-dir data

	# Faster test with no network
	python prothomalo.py --dry-run

Notes:
	- This script only stores image URLs, not the binary image data.
	- Site structure may change; adjust CSS selectors in parse_article if needed.
	- Always verify scraping aligns with the website's Terms of Service.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime, date, timezone
from typing import Iterable, List, Optional, Set, Dict, Any, Tuple

try:  # Python 3.9+
	from zoneinfo import ZoneInfo  # type: ignore
except Exception:  # pragma: no cover - fallback for older Python
	try:
		from pytz import timezone as ZoneInfo  # type: ignore
	except Exception:
		ZoneInfo = None  # type: ignore

import requests
from bs4 import BeautifulSoup, SoupStrainer


# ----------------------------- Configuration ---------------------------------

BASE_URL = "https://www.prothomalo.com"
# Default seed paths ("/latest" removed after repeated 404 responses). Users can override via --seeds.
DEFAULT_SEED_PATHS = [
	"/",  # homepage
	"/bangladesh",
	"/world",
	"/sports",
	"/entertainment",
	"/business",
	"/technology",
]

DEFAULT_MIN_DELAY = 0.6  # seconds between requests (minimum)
DEFAULT_MAX_DELAY = 1.5  # seconds (maximum) -> jitter introduces randomness

# Crawl settings (for --mode crawl/hybrid)
DEFAULT_MAX_CRAWL_PAGES = 80  # maximum non-article pages to fetch
DEFAULT_MAX_CRAWL_DEPTH = 2   # BFS depth for internal pages
SITEMAP_URL_HINT_PATTERN = re.compile(r"sitemap", re.IGNORECASE)

def is_article_path(path: str) -> bool:
	if not path.startswith('/'):
		return False
	return bool(ARTICLE_URL_PATTERN.match(path))

REQUEST_TIMEOUT = 12  # seconds for individual HTTP requests
MAX_RETRIES = 3
BACKOFF_BASE = 1.7  # exponential backoff multiplier

# Some realistic desktop & mobile user-agents (short curated list)
USER_AGENTS = [
	# Desktop Chrome variants
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
	# Desktop Firefox
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
	# Mobile Chrome (Android)
	"Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36",
	# Mobile Safari (iPhone)
	"Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

HEADERS_BASE = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
	"Accept-Language": "bn-BD,bn;q=0.9,en-US;q=0.8,en;q=0.7",
	"Connection": "close",
}

ARTICLE_URL_PATTERN = re.compile(r"^/[-a-z0-9/]+/[a-z0-9]{6,}$")
PUBLISHED_META_NAMES = [
	("meta", {"property": "article:published_time"}),
	("meta", {"name": "pubdate"}),
]

BD_TZ_NAME = "Asia/Dhaka"
BD_TZ = ZoneInfo(BD_TZ_NAME) if ZoneInfo else None  # type: ignore

# Global runtime switches (set via CLI flags)
EXTRA_IMAGES = False  # when True, attempt broader image harvesting beyond article container


# ------------------------------- Data Models ----------------------------------

@dataclass
class Article:
	url: str
	title: str
	published: Optional[str]
	text: str
	images: List[str]
	section: Optional[str]
	scraped_at: str


# --------------------------- Utility Functions --------------------------------

def log_setup(verbosity: int) -> None:
	"""Configure logging level & formatting."""
	level = logging.WARNING
	if verbosity == 1:
		level = logging.INFO
	elif verbosity >= 2:
		level = logging.DEBUG
	logging.basicConfig(
		level=level,
		format="%(asctime)s | %(levelname)-8s | %(message)s",
		datefmt="%H:%M:%S",
	)


def random_user_agent() -> str:
	return random.choice(USER_AGENTS)


def polite_sleep(min_delay: float, max_delay: float) -> None:
	"""Sleep a random time between min & max to reduce request burstiness."""
	if max_delay <= 0:
		return
	time.sleep(random.uniform(min_delay, max_delay))


def read_crawl_delay(base_url: str) -> Optional[float]:
	"""Attempt to parse crawl-delay from robots.txt for User-agent: *.

	Returns float seconds or None if not specified / error.
	"""
	robots_url = base_url.rstrip("/") + "/robots.txt"
	try:
		resp = requests.get(robots_url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": random_user_agent(), **HEADERS_BASE})
		if resp.status_code != 200:
			return None
		ua_block = False
		for line in resp.text.splitlines():
			l = line.strip()
			if not l or l.startswith('#'):
				continue
			if l.lower().startswith("user-agent:"):
				ua = l.split(":",1)[1].strip()
				ua_block = (ua == '*' )
			elif ua_block and l.lower().startswith("crawl-delay:"):
				try:
					return float(l.split(":",1)[1].strip())
				except ValueError:
					return None
		return None
	except Exception as e:  # network failure: not critical
		logging.debug("robots.txt fetch failed: %s", e)
		return None


def build_headers(referer: Optional[str] = None) -> Dict[str, str]:
	h = dict(HEADERS_BASE)
	h["User-Agent"] = random_user_agent()
	if referer:
		h["Referer"] = referer
	return h


def request_with_retries(url: str, *, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
	"""GET request with retry + backoff.

	Returns Response or None if all attempts fail.
	"""
	for attempt in range(1, retries + 1):
		try:
			resp = requests.get(url, headers=build_headers(), timeout=REQUEST_TIMEOUT)
			if resp.status_code in (404, 410):
				# Permanent not found / gone: don't retry further
				logging.warning("Permanent status %s for %s; not retrying", resp.status_code, url)
				return None
			if resp.status_code == 429:  # Too Many Requests -> backoff stronger
				wait = BACKOFF_BASE ** attempt + random.random()
				logging.warning("429 received for %s; backing off %.1fs", url, wait)
				time.sleep(wait)
				continue
			if 200 <= resp.status_code < 400:
				return resp
			logging.warning("Non-success status %s for %s", resp.status_code, url)
		except requests.RequestException as e:
			logging.info("Request error (%s) attempt %d/%d: %s", url, attempt, retries, e)
		# Exponential backoff with jitter
		wait = (BACKOFF_BASE ** attempt) + random.uniform(0, 0.5)
		polite_sleep(wait, wait + 0.2)
	return None


def discover_links(html: str) -> Tuple[Set[str], Set[str]]:
	"""Extract (article_links, page_links) from a page's HTML.

	page_links are internal non-article paths suitable for further crawling.
	Returns tuple of absolute URL sets.
	"""
	article_links: Set[str] = set()
	page_links: Set[str] = set()
	for a in BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("a")):
		if not a or not a.has_attr("href"):
			continue
		href = a["href"].strip()
		if not href:
			continue
		if href.startswith('#') or href.startswith('mailto:'):
			continue
		# Normalize
		if href.startswith(BASE_URL):
			path = href[len(BASE_URL):]
		else:
			path = href
		if not path.startswith('/'):
			continue
		if is_article_path(path):
			article_links.add(BASE_URL.rstrip('/') + path)
		else:
			# basic heuristic to avoid adding assets or js/css
			if re.search(r"\.(?:jpg|jpeg|png|gif|svg|css|js)(?:\?|$)", path, re.IGNORECASE):
				continue
			page_links.add(BASE_URL.rstrip('/') + path)
	return article_links, page_links
def discover_article_links(html: str) -> Set[str]:  # backward compatibility old call sites
	arts, _ = discover_links(html)
	return arts

def crawl_for_article_urls(seeds: List[str], limit: int, max_pages: int, max_depth: int) -> Set[str]:
	"""Breadth-first crawl of internal pages to collect article URLs.

	limit <=0 means unlimited (subject to max_pages constraint for page fetches).
	Returns set of article absolute URLs.
	"""
	visited_pages: Set[str] = set()
	article_urls: Set[str] = set()
	queue: List[tuple[str,int]] = []
	for s in seeds:
		if not s.startswith('/'):
			continue
		queue.append((BASE_URL.rstrip('/') + s, 0))

	while queue:
		url, depth = queue.pop(0)
		if url in visited_pages or depth > max_depth:
			continue
		visited_pages.add(url)
		if len(visited_pages) > max_pages:
			logging.info("Reached max crawl pages (%d)", max_pages)
			break
		resp = request_with_retries(url)
		if not resp:
			continue
		arts, pages = discover_links(resp.text)
		before = len(article_urls)
		article_urls.update(arts)
		new_arts = len(article_urls) - before
		if new_arts:
			logging.debug("+%d articles from %s (depth %d) total=%d", new_arts, url, depth, len(article_urls))
		# Queue next-level pages
		if depth < max_depth:
			for p in pages:
				if p not in visited_pages:
					queue.append((p, depth + 1))
		if limit > 0 and len(article_urls) >= limit * 4:  # gather cushion
			break
	return article_urls


def parse_robots_for_sitemaps(text: str) -> List[str]:
	urls: List[str] = []
	for line in text.splitlines():
		line = line.strip()
		if not line or line.startswith('#'):
			continue
		if line.lower().startswith('sitemap:'):
			url = line.split(':',1)[1].strip()
			if url:
				urls.append(url)
	return urls


def fetch_sitemap_urls() -> List[str]:
	robots_url = BASE_URL.rstrip('/') + '/robots.txt'
	resp = request_with_retries(robots_url)
	if not resp:
		return []
	sitemap_urls = parse_robots_for_sitemaps(resp.text)
	# Deduplicate & prefer those containing 'news'
	prioritized = sorted(sitemap_urls, key=lambda u: (0 if 'news' in u.lower() else 1, u))
	return prioritized


def gather_articles_from_sitemaps(limit: int) -> Set[str]:
	"""Parse sitemap XML files to collect today's article URLs.

	limit <=0 means unlimited.
	"""
	urls = fetch_sitemap_urls()
	if not urls:
		logging.info("No sitemap URLs found in robots.txt")
		return set()
	today_bd = datetime.now(BD_TZ).date() if BD_TZ else date.today()
	article_urls: Set[str] = set()
	for sm_url in urls:
		if limit > 0 and len(article_urls) >= limit * 4:
			break
		resp = request_with_retries(sm_url)
		if not resp:
			continue
		text = resp.text
		# Very lightweight XML parsing without extra dependency
		# Extract <loc> and optional <lastmod> or <news:publication_date>
		locs = re.findall(r"<loc>(.*?)</loc>", text)
		pub_dates = re.findall(r"<news:publication_date>(.*?)</news:publication_date>", text)
		# Fallback lastmod mapping
		lastmods = re.findall(r"<lastmod>(.*?)</lastmod>", text)
		# We will pair by index heuristically if counts match; otherwise process locs individually.
		for idx, loc in enumerate(locs):
			loc_url = loc.strip()
			if not loc_url.startswith('http'):
				continue
			# Attempt associated date
			raw_dt = None
			if idx < len(pub_dates):
				raw_dt = pub_dates[idx].strip()
			elif idx < len(lastmods):
				raw_dt = lastmods[idx].strip()
			if raw_dt:
				iso = parse_datetime_iso(raw_dt)
				if iso:
					try:
						dt = datetime.fromisoformat(iso)
						if dt.tzinfo is None and BD_TZ:
							dt = dt.replace(tzinfo=BD_TZ)
						if dt.astimezone(BD_TZ).date() != today_bd if BD_TZ else dt.date() != today_bd:
							continue
					except Exception:
						pass
			# Filter to prothomalo domain & article-like paths
			if loc_url.startswith(BASE_URL) and is_article_path(loc_url[len(BASE_URL):]):
				article_urls.add(loc_url)
		logging.info("Sitemap %s yielded %d candidate today URLs (running total %d)", sm_url, len(article_urls), len(article_urls))
	return article_urls



def parse_datetime_iso(raw: str) -> Optional[str]:
	"""Attempt to parse a datetime string and return ISO 8601 (with tz if available)."""
	raw = raw.strip()
	# Common patterns (example: 2025-08-18T05:30:00+06:00)
	try:
		dt = datetime.fromisoformat(raw.replace('Z', '+00:00'))
	except ValueError:
		# Fallback heuristic: extract digits
		m = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+\-]\d{2}:?\d{2})?", raw)
		if not m:
			return None
		frag = m.group(0)
		try:
			dt = datetime.fromisoformat(frag)
		except Exception:
			return None
	if dt.tzinfo is None and BD_TZ:
		dt = dt.replace(tzinfo=BD_TZ)
	return dt.isoformat()


def article_is_today(published_iso: Optional[str]) -> bool:
	if not published_iso:
		return False
	try:
		dt = datetime.fromisoformat(published_iso)
	except Exception:
		return False
	if dt.tzinfo is None and BD_TZ:  # assume BD if missing
		dt = dt.replace(tzinfo=BD_TZ)
	today_bd = datetime.now(BD_TZ).date() if BD_TZ else date.today()
	return dt.astimezone(BD_TZ).date() == today_bd if BD_TZ else dt.date() == today_bd


def extract_article(html: str, url: str) -> Optional[Article]:
	"""Parse article HTML -> Article dataclass or None if not an article."""
	soup = BeautifulSoup(html, "html.parser")
	# Prefer semantic <article>; fallback to common container heuristics
	container = soup.find("article") or soup.find(
		"div",
		{"class": re.compile(r"(content|story|article|details|body|news)", re.IGNORECASE)},
	)

	# Title
	title_tag = (container.find("h1") if container else None) or soup.find("h1")
	title_text = title_tag.get_text(strip=True) if title_tag else ""
	if not title_text:
		return None

	# Publication date/time
	published_iso: Optional[str] = None
	for name, attrs in PUBLISHED_META_NAMES:
		meta = soup.find(name, attrs=attrs)
		if meta and meta.get("content"):
			published_iso = parse_datetime_iso(meta["content"]) or published_iso
	if not published_iso:
		time_tag = soup.find("time")
		if time_tag and time_tag.get("datetime"):
			published_iso = parse_datetime_iso(time_tag["datetime"]) or published_iso

	def resolve_image(img_tag) -> Optional[str]:
		# Collect candidate URLs from various lazy-load attributes / srcset
		attr_order = ["data-src", "data-original", "data-lazy", "data-url", "data-srcset", "srcset", "src"]
		candidates: List[str] = []
		for attr in attr_order:
			val = img_tag.get(attr)
			if not val:
				continue
			if attr.endswith("srcset"):
				parts = [p.strip() for p in val.split(',') if p.strip()]
				best_url = None
				best_w = -1
				for part in parts:
					seg = part.split()
					if not seg:
						continue
					cand_url = seg[0]
					w = -1
					if len(seg) > 1 and seg[1].endswith('w'):
						try:
							w = int(seg[1][:-1])
						except Exception:
							w = -1
					if w > best_w:
						best_w = w
						best_url = cand_url
				if best_url:
					candidates.append(best_url)
			else:
				candidates.append(val)
		for raw in candidates:
			raw = raw.strip()
			if raw.startswith("//"):
				raw = "https:" + raw
			elif raw.startswith("/"):
				raw = BASE_URL.rstrip('/') + raw
			if raw.startswith("http"):
				return raw
		return None

	root = container or soup
	paragraphs: List[str] = []
	for p in root.find_all("p"):
		txt = p.get_text(" ", strip=True)
		if len(txt) >= 25:
			paragraphs.append(txt)
	body_text = "\n\n".join(paragraphs)
	if len(body_text) < 80:
		return None

	images: List[str] = []
	seen: Set[str] = set()

	def add_image(u: Optional[str]):
		if not u:
			return
		if u.startswith("//"):
			u = "https:" + u
		elif u.startswith("/"):
			u = BASE_URL.rstrip('/') + u
		if u.startswith("http") and u not in seen:
			seen.add(u)
			images.append(u)

	# 1. Images within root container
	for img in root.find_all("img"):
		add_image(resolve_image(img))

	# 2. <picture><source srcset=...>
	for source in root.find_all("source"):
		srcset = source.get("srcset")
		if not srcset:
			continue
		# choose largest width
		best = None; best_w = -1
		for part in [p.strip() for p in srcset.split(',') if p.strip()]:
			seg = part.split()
			if not seg:
				continue
			url_part = seg[0]
			w = -1
			if len(seg) > 1 and seg[1].endswith('w'):
				try: w = int(seg[1][:-1])
				except Exception: w = -1
			if w > best_w:
				best_w = w; best = url_part
		add_image(best)

	# 3. JSON-LD structured data images
	for script in soup.find_all("script", {"type": "application/ld+json"}):
		try:
			content = script.string or script.get_text()
			if not content:
				continue
			import json as _json
			data = _json.loads(content)
			def extract_from(obj):
				if isinstance(obj, dict):
					if "image" in obj:
						img_field = obj["image"]
						if isinstance(img_field, str):
							add_image(img_field)
						elif isinstance(img_field, dict):
							add_image(img_field.get("url"))
						elif isinstance(img_field, list):
							for it in img_field:
								if isinstance(it, str): add_image(it)
								elif isinstance(it, dict): add_image(it.get("url"))
					for v in obj.values():
						extract_from(v)
				elif isinstance(obj, list):
					for v in obj:
						extract_from(v)
			extract_from(data)
		except Exception:
			continue

	# 4. Background-image styles (only if extra flag)
	if EXTRA_IMAGES:
		for tag in (root if not EXTRA_IMAGES else soup).find_all(style=True):
			style = tag.get("style", "")
			for m in re.finditer(r"background-image\s*:\s*url\((['\"]?)([^)'\"]+)\1\)", style, re.IGNORECASE):
				add_image(m.group(2))

	# 5. If we still have none and extra mode, scan whole document <img>
	if EXTRA_IMAGES and not images:
		for img in soup.find_all("img"):
			add_image(resolve_image(img))

	if not images:
		logging.debug("No images extracted for %s (after extended checks)", url)

	section = None
	sec_meta = soup.find("meta", {"property": "article:section"})
	if sec_meta and sec_meta.get("content"):
		section = sec_meta["content"].strip() or None
	if not section:
		breadcrumb = soup.select_one("nav a")
		if breadcrumb:
			section = breadcrumb.get_text(strip=True) or None

	scraped_at = datetime.now(timezone.utc).isoformat()
	return Article(
		url=url,
		title=title_text,
		published=published_iso,
		text=body_text,
		images=images,
		section=section,
		scraped_at=scraped_at,
	)


def fetch_and_parse(url: str, *, min_delay: float, max_delay: float) -> Optional[Article]:
	"""Full pipeline for a single article URL: request -> parse -> filter by date."""
	polite_sleep(min_delay, max_delay)
	resp = request_with_retries(url)
	if not resp:
		logging.error("Failed to fetch %s", url)
		return None
	art = extract_article(resp.text, url)
	if not art:
		return None
	if not article_is_today(art.published):
		logging.debug("Skipping (not today): %s", url)
		return None
	return art


def save_json(articles: Iterable[Article], path: str) -> None:
	data = [asdict(a) for a in articles]
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(articles: Iterable[Article], path: str) -> None:
	articles_list = list(articles)
	if not articles_list:
		logging.warning("No articles to write to CSV.")
		return
	fieldnames = ["url", "title", "published", "section", "scraped_at", "text", "images"]
	with open(path, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames)
		writer.writeheader()
		for a in articles_list:
			row = asdict(a)
			row["images"] = "|".join(a.images)
			writer.writerow(row)


# ------------------------------ Main Routine ----------------------------------

def scrape_today(limit: int, max_workers: int, formats: List[str], output_dir: str, min_delay: float, max_delay: float, dry_run: bool, seeds: Optional[List[str]] = None, mode: str = "simple", max_crawl_pages: int = DEFAULT_MAX_CRAWL_PAGES, max_crawl_depth: int = DEFAULT_MAX_CRAWL_DEPTH) -> List[Article]:
	"""Scrape today's articles and persist them in requested formats.

	Returns list of Article objects kept.
	"""
	if dry_run:
		logging.info("Dry-run: generating fake sample articles (no network)")
		sample = [
			Article(
				url=f"{BASE_URL}/sample/{i}",
				title=f"Sample Article {i}",
				published=datetime.now(BD_TZ).isoformat() if BD_TZ else datetime.now(timezone.utc).isoformat(),
				text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 4,
				images=["https://example.com/image1.jpg"],
				section="sample",
				scraped_at=datetime.now(timezone.utc).isoformat(),
			)
			for i in range(min(limit, 3))
		]
		persist(sample, formats, output_dir)
		return sample

	# Adjust delays if robots defines a larger crawl-delay
	cd = read_crawl_delay(BASE_URL)
	if cd and cd > max_delay:
		logging.info("Applying robots crawl-delay %.2fs", cd)
		min_delay = max(min_delay, cd)
		max_delay = max(max_delay, cd + 0.3)

	seed_paths = seeds if seeds else DEFAULT_SEED_PATHS
	logging.info("Mode=%s | seeds=%d | limit=%s", mode, len(seed_paths), 'unlimited' if limit <=0 else limit)

	candidate_urls: Set[str] = set()
	if mode in ("simple", "hybrid", "crawl"):
		# Seed discovery (shallow)
		for path in seed_paths:
			if not path.startswith('/'):
				continue
			seed_url = BASE_URL.rstrip('/') + path
			resp = request_with_retries(seed_url)
			if not resp:
				continue
			new_links = discover_article_links(resp.text)
			candidate_urls.update(new_links)
			if limit > 0 and len(candidate_urls) >= limit * 4:
				break

	if mode in ("crawl", "hybrid"):
		crawl_urls = crawl_for_article_urls(seed_paths, limit, max_crawl_pages, max_crawl_depth)
		candidate_urls.update(crawl_urls)

	if mode in ("sitemap", "hybrid"):
		sm_urls = gather_articles_from_sitemaps(limit)
		candidate_urls.update(sm_urls)

	logging.info("Total candidate article URLs gathered: %d", len(candidate_urls))
	if not candidate_urls:
		logging.warning("No candidate article URLs found.")
		return []

	articles: List[Article] = []
	# Use concurrency for fetching/parsing
	# Prepare fetch list; if limit>0 we still may fetch more because some will be filtered (not today)
	fetch_list = list(candidate_urls)
	if limit > 0:
		fetch_cap = min(len(fetch_list), limit * 6)
		fetch_list = fetch_list[:fetch_cap]

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		future_map = {
			executor.submit(fetch_and_parse, url, min_delay=min_delay, max_delay=max_delay): url
			for url in fetch_list
		}
		for future in as_completed(future_map):
			url = future_map[future]
			try:
				art = future.result()
			except Exception as e:
				logging.error("Unhandled error for %s: %s", url, e)
				continue
			if art:
				articles.append(art)
				logging.info("Collected (%d): %s", len(articles), art.title[:60])
				if limit > 0 and len(articles) >= limit:
					break

	articles.sort(key=lambda a: a.published or "", reverse=True)
	persist(articles, formats, output_dir)
	return articles


def persist(articles: List[Article], formats: List[str], output_dir: str) -> None:
	os.makedirs(output_dir, exist_ok=True)
	today_str = datetime.now(BD_TZ).strftime("%Y%m%d") if BD_TZ else date.today().strftime("%Y%m%d")
	base_filename = f"prothomalo_articles_{today_str}"
	if "json" in formats:
		json_path = os.path.join(output_dir, base_filename + ".json")
		save_json(articles, json_path)
		logging.info("Saved JSON -> %s", json_path)
	if "csv" in formats:
		csv_path = os.path.join(output_dir, base_filename + ".csv")
		save_csv(articles, csv_path)
		logging.info("Saved CSV  -> %s", csv_path)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Scrape today's Prothom Alo news articles.")
	parser.add_argument("--limit", type=int, default=50, help="Maximum number of articles to collect (<=0 for unlimited, default: 50)")
	parser.add_argument("--formats", nargs="+", choices=["json", "csv"], default=["json"], help="Output format(s)")
	parser.add_argument("--output-dir", default="output", help="Directory to write output files")
	parser.add_argument("--max-workers", type=int, default=6, help="Thread pool workers (default: 6)")
	parser.add_argument("--min-delay", type=float, default=DEFAULT_MIN_DELAY, help="Minimum delay between requests (seconds)")
	parser.add_argument("--max-delay", type=float, default=DEFAULT_MAX_DELAY, help="Maximum delay between requests (seconds)")
	parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase log verbosity (-v, -vv)")
	parser.add_argument("--dry-run", action="store_true", help="Generate sample output without network requests")
	parser.add_argument("--seeds", nargs="+", default=None, help="Custom seed paths (override defaults). Example: --seeds / /world /sports")
	parser.add_argument("--mode", choices=["simple","crawl","sitemap","hybrid"], default="simple", help="Discovery mode: simple(seeds only), crawl(BFS), sitemap(sitemap XML), hybrid(all).")
	parser.add_argument("--extra-images", action="store_true", help="Broader image harvesting (background-image styles, JSON-LD, full-page fallback)")
	parser.add_argument("--max-crawl-pages", type=int, default=DEFAULT_MAX_CRAWL_PAGES, help="Max non-article pages to fetch in crawl/hybrid mode")
	parser.add_argument("--max-crawl-depth", type=int, default=DEFAULT_MAX_CRAWL_DEPTH, help="Max BFS depth for crawl/hybrid mode")
	return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)
	log_setup(args.verbose)
	logging.info("Starting Prothom Alo scraper")
	global EXTRA_IMAGES
	EXTRA_IMAGES = bool(getattr(args, "extra_images", False))
	try:
		articles = scrape_today(
			limit=args.limit,
			max_workers=max(1, args.max_workers),
			formats=args.formats,
			output_dir=args.output_dir,
			min_delay=args.min_delay,
			max_delay=max(args.min_delay, args.max_delay),
			dry_run=args.dry_run,
			seeds=args.seeds,
			mode=args.mode,
			max_crawl_pages=args.max_crawl_pages,
			max_crawl_depth=args.max_crawl_depth,
		)
	except KeyboardInterrupt:
		logging.warning("Interrupted by user")
		return 130
	except Exception as e:
		logging.exception("Fatal error: %s", e)
		return 1
	print(f"Collected {len(articles)} article(s).")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

