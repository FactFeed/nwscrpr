"""
Abstract base scraper class
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import requests
import time
from bs4 import BeautifulSoup
import re

from ..config import Config
from ..models import Article
from ..exceptions import NetworkException, ParseException
from ..utils import get_logger


class BaseScraper(ABC):
    """Abstract base class for all news scrapers"""
    
    def __init__(self, delay: float = None, max_retries: int = None, timeout: int = None):
        self.delay = delay or Config.DEFAULT_DELAY
        self.max_retries = max_retries or Config.DEFAULT_MAX_RETRIES
        self.timeout = timeout or Config.DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update(Config.DEFAULT_HEADERS)
        self.logger = get_logger(f"{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL of the news site"""
        pass
    
    @property
    @abstractmethod
    def site_name(self) -> str:
        """Name of the news site"""
        pass
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    raise NetworkException(f"Failed to fetch {url}: {e}", url=url)
                time.sleep(self.delay * (attempt + 1))
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        if not url or len(url) < 10:
            return False
        
        # Check against excluded patterns
        for pattern in Config.EXCLUDED_URL_PATTERNS:
            if pattern.endswith('$'):
                if url.endswith(pattern[:-1]):
                    return False
            elif pattern in url.lower():
                return False
        
        return True
    
    def _normalize_url(self, url: str) -> str:
        """Convert relative URLs to absolute URLs"""
        if not url:
            return ""
        
        url = url.strip()
        
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return self.base_url + url
        elif url.startswith('http'):
            return url
        else:
            return self.base_url + '/' + url
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image URL"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Check for image patterns
        image_patterns = [
            '.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg',
            'img.', 'images.', 'photos.', 'cdn.', 'static.', 'assets.',
            'media.', 'uploads.', 'files.'
        ]
        
        has_image_pattern = any(pattern in url_lower for pattern in image_patterns)
        
        if not has_image_pattern:
            # Accept if from same domain
            if self.base_url.split('//')[1] in url_lower:
                has_image_pattern = True
        
        if not has_image_pattern:
            return False
        
        # Filter out excluded patterns
        for pattern in Config.EXCLUDED_IMAGE_PATTERNS:
            if pattern in url_lower:
                return False
        
        return True
    
    def _extract_meta_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract image from meta tags"""
        meta_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'meta[property="twitter:image"]',
            'meta[name="image"]',
            'meta[property="image"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                image_url = element.get('content')
                if image_url and self._is_valid_image_url(image_url):
                    return self._normalize_url(image_url)
        
        return None
    
    @abstractmethod
    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get article links from the site"""
        pass
    
    @abstractmethod
    def scrape_article(self, url: str) -> Optional[Article]:
        """Scrape a single article"""
        pass
    
    @abstractmethod
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        pass
    
    @abstractmethod
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content"""
        pass
    
    @abstractmethod
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        pass
    
    @abstractmethod
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract article date"""
        pass
    
    @abstractmethod
    def _extract_main_image(self, soup: BeautifulSoup, url: str) -> str:
        """Extract main article image"""
        pass
    
    def scrape_articles(self, limit: int = 10) -> List[Article]:
        """Scrape multiple articles"""
        if limit == 0:
            self.logger.info(f"Starting to scrape ALL available articles from {self.site_name}")
        else:
            self.logger.info(f"Starting to scrape {limit} articles from {self.site_name}")
        
        # Get article links
        multiplier = 3 if limit > 0 else 1
        article_links = self.get_article_links(limit * multiplier if limit > 0 else 0)
        articles = []
        
        total_links = len(article_links)
        for i, link in enumerate(article_links):
            if limit > 0 and len(articles) >= limit:
                break
                
            self.logger.info(f"Processing article {i + 1}/{total_links}")
            try:
                article = self.scrape_article(link)
                if article and article.is_valid():
                    articles.append(article)
                    self.logger.debug(f"Successfully scraped: {article.get_title_preview()}")
                else:
                    self.logger.warning(f"Invalid article data for {link}")
            except Exception as e:
                self.logger.error(f"Error scraping article {link}: {e}")
            
            # Respect rate limiting
            time.sleep(self.delay)
        
        self.logger.info(f"Successfully scraped {len(articles)} articles from {self.site_name}")
        return articles