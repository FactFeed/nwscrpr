"""
Bangla News Scraper for Prothom Alo
A simple web scraper to extract news articles from Prothom Alo website.
"""

import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProthomAloScraper:
    """Scraper class for Prothom Alo news website"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.base_url = "https://www.prothomalo.com"
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
                time.sleep(self.delay * (attempt + 1))
        return None
    
    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get article links from the homepage"""
        if limit == 0:
            logger.info(f"Fetching ALL available article links from Prothom Alo...")
        else:
            logger.info(f"Fetching article links from Prothom Alo homepage...")
        
        response = self._make_request(self.base_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        
        # Find all anchor tags and filter for actual article links
        all_links = soup.find_all('a', href=True)
        logger.info(f"Found {len(all_links)} total links on homepage")
        
        for link in all_links:
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Filter for actual article URLs (not category pages)
                if self._is_article_link(full_url) and full_url not in links:
                    links.append(full_url)
                    logger.debug(f"Added article link: {full_url}")
                    
                # Only break if limit > 0 (when limit=0, get all articles)
                if limit > 0 and len(links) >= limit:
                    break
        
        # If we don't find enough links (or want all when limit=0), try browsing specific sections
        if limit == 0 or len(links) < limit:
            section_urls = [
                f"{self.base_url}/bangladesh",
                f"{self.base_url}/world",
                f"{self.base_url}/sports",
                f"{self.base_url}/entertainment",
                f"{self.base_url}/business",
                f"{self.base_url}/opinion",
                f"{self.base_url}/politics",
                f"{self.base_url}/lifestyle",
                f"{self.base_url}/tech"
            ]
            
            for section_url in section_urls:
                # Only break if we have enough and limit > 0
                if limit > 0 and len(links) >= limit:
                    break
                    
                logger.info(f"Checking section: {section_url}")
                section_response = self._make_request(section_url)
                if section_response:
                    section_soup = BeautifulSoup(section_response.content, 'html.parser')
                    section_links = section_soup.find_all('a', href=True)
                    
                    for link in section_links:
                        href = link.get('href')
                        if href:
                            if href.startswith('/'):
                                full_url = self.base_url + href
                            elif href.startswith('http'):
                                full_url = href
                            else:
                                continue
                            
                            if self._is_article_link(full_url) and full_url not in links:
                                links.append(full_url)
                                logger.debug(f"Added section article link: {full_url}")
                                
                            # Only break if we have enough and limit > 0
                            if limit > 0 and len(links) >= limit:
                                break
        
        if limit == 0:
            logger.info(f"Found {len(links)} total article links (ALL available)")
        else:
            logger.info(f"Found {len(links)} article links")
            return links[:limit]
        
        return links
    
    def _is_article_link(self, url: str) -> bool:
        """Check if URL is an actual article link (not category/section page)"""
        # Basic validation to filter out navigation and other non-article links
        excluded_patterns = [
            '/tag/', '/author/', '/category/', '/search',
            'javascript:', 'mailto:', '#', '/static/',
            '/assets/', '.jpg', '.png', '.gif', '.pdf',
            '/page/', '/archive/', '/contact', '/about',
            'facebook.com', 'twitter.com', 'youtube.com',
            '/api/', '/oauth/', '/auth/', '/login',
            'prothomalo.com/bangladesh$',  # Category pages end like this
            'prothomalo.com/world$',
            'prothomalo.com/sports$',
            'prothomalo.com/entertainment$',
            'prothomalo.com/business$',
            'prothomalo.com/politics$',
            'prothomalo.com/opinion$',
            'prothomalo.com/lifestyle$',
            'prothomalo.com/tech$',
            'prothomalo.com/$',  # Homepage
            '/collection/',
            '/latest'
        ]
        
        for pattern in excluded_patterns:
            if pattern.endswith('$'):
                # Exact match patterns
                if url.endswith(pattern[:-1]):
                    return False
            elif pattern in url.lower():
                return False
        
        # Look for actual article patterns
        # Articles usually have longer paths with specific patterns
        if len(url.split('/')) >= 5:  # Articles usually have deeper paths
            return True
        
        # Check for date patterns in URL (very common for articles)
        if re.search(r'/\d{4}/\d{2}/\d{2}/', url):
            return True
        
        # Check for article ID patterns
        if re.search(r'/\d+/', url):
            return True
        
        # Check if URL has article-like text (multiple words separated by hyphens)
        if re.search(r'/[a-zA-Z0-9\-]{20,}/?$', url):
            return True
        
        return False

    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL (alias for _is_article_link for backward compatibility)"""
        return self._is_article_link(url)
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape a single article"""
        logger.info(f"Scraping article: {url}")
        
        response = self._make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'author': self._extract_author(soup),
                'date': self._extract_date(soup),
                'image_url': self._extract_main_image(soup, url),
                'scraped_at': datetime.now().isoformat()
            }
            
            # Validate that we got essential data
            if not article_data['title'] or not article_data['content']:
                logger.warning(f"Incomplete article data for {url}")
                return None
            
            logger.info(f"Successfully scraped: {article_data['title'][:50]}...")
            return article_data
            
        except Exception as e:
            logger.error(f"Error extracting article data from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors for title
        selectors = [
            'h1.headline',
            'h1[itemprop="headline"]',
            'h1.entry-title',
            'h1',
            '.headline h1',
            '.story-element-text h1'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return "No title found"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content"""
        # Try multiple selectors for content
        selectors = [
            '.story-element-text',
            '.story-content',
            '.entry-content',
            '[itemprop="articleBody"]',
            '.article-body',
            '.content-body'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content_parts = []
                for element in elements:
                    # Remove script and style elements
                    for script in element(["script", "style"]):
                        script.decompose()
                    
                    text = element.get_text(strip=True)
                    if text and len(text) > 50:  # Filter out very short snippets
                        content_parts.append(text)
                
                if content_parts:
                    return '\n\n'.join(content_parts)
        
        # Fallback: try to find paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    content_parts.append(text)
            
            if content_parts:
                return '\n\n'.join(content_parts)
        
        return "No content found"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        # Try multiple selectors for author
        selectors = [
            '[itemprop="author"]',
            '.author-name',
            '.byline',
            '.reporter-name',
            '.writer-name'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Look for common author patterns in text
        byline_patterns = [
            r'প্রতিবেদক[:\s]*([^\n,]+)',
            r'সংবাদদাতা[:\s]*([^\n,]+)',
            r'স্টাফ রিপোর্টার[:\s]*([^\n,]+)'
        ]
        
        page_text = soup.get_text()
        for pattern in byline_patterns:
            match = re.search(pattern, page_text)
            if match:
                return match.group(1).strip()
        
        return "Unknown"
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract article date"""
        # Try multiple selectors for date
        selectors = [
            '[itemprop="datePublished"]',
            '.publish-date',
            '.date',
            '.timestamp',
            'time'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Try to get datetime attribute first
                date_attr = element.get('datetime') or element.get('content')
                if date_attr:
                    return date_attr
                
                # Otherwise get text content
                date_text = element.get_text(strip=True)
                if date_text:
                    return date_text
        
        # Look for date patterns in meta tags
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]',
            'meta[name="date"]'
        ]
        
        for selector in meta_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get('content')
                if content:
                    return content
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_main_image(self, soup: BeautifulSoup, article_url: str) -> str:
        """Extract the main article image"""
        logger.debug(f"Extracting images for: {article_url}")
        
        # First try Open Graph and Twitter meta tags (most reliable)
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
                logger.debug(f"Found meta image ({selector}): {image_url}")
                if image_url and self._is_valid_image_url(image_url):
                    return self._normalize_image_url(image_url)
        
        # Try JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict):
                    image = data.get('image') or data.get('thumbnailUrl')
                    if image:
                        if isinstance(image, list) and image:
                            image = image[0]
                        if isinstance(image, dict):
                            image = image.get('url') or image.get('@url')
                        if image and self._is_valid_image_url(str(image)):
                            logger.debug(f"Found JSON-LD image: {image}")
                            return self._normalize_image_url(str(image))
            except:
                continue
        
        # Try various image selectors - be more aggressive
        image_selectors = [
            # Look for any img with size attributes (likely main images)
            'img[width][height]',
            
            # Common article image patterns
            '.story-element img',
            '.article-image img', 
            '.content-image img',
            '.featured-image img',
            '.hero-image img',
            '.main-image img',
            '.lead-image img',
            '.post-image img',
            
            # Figure and picture elements
            'figure img',
            'picture img',
            
            # First images in content areas
            '.story-content img',
            '.article-content img',
            '.post-content img',
            '.entry-content img',
            '.content img',
            
            # Any img in article or main content
            'article img',
            'main img',
            '.main img',
            '#main img'
        ]
        
        # Find ALL images first and log them
        all_images = soup.find_all('img')
        logger.debug(f"Total <img> tags found: {len(all_images)}")
        
        # Log first few images for debugging
        for i, img in enumerate(all_images[:5]):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original') or img.get('data-url')
            alt = img.get('alt', '')[:50]
            width = img.get('width', 'unknown')
            height = img.get('height', 'unknown')
            logger.debug(f"Image {i+1}: src='{src}', alt='{alt}', size={width}x{height}")
        
        # Try specific selectors
        for selector in image_selectors:
            elements = soup.select(selector)
            logger.debug(f"Selector '{selector}' found {len(elements)} elements")
            
            for element in elements:
                image_url = element.get('src') or element.get('data-src') or element.get('data-lazy-src') or element.get('data-original') or element.get('data-url')
                
                if image_url:
                    normalized_url = self._normalize_image_url(image_url)
                    logger.debug(f"Checking image from selector '{selector}': {normalized_url}")
                    
                    if self._is_valid_image_url(normalized_url) and self._is_main_article_image(element, normalized_url):
                        logger.debug(f"Found main image via selector: {normalized_url}")
                        return normalized_url
        
        # Fallback: Check ALL images on the page
        for i, img in enumerate(all_images):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original') or img.get('data-url')
            if src:
                normalized_url = self._normalize_image_url(src)
                logger.debug(f"Fallback check image {i+1}: {normalized_url}")
                
                if self._is_valid_image_url(normalized_url) and self._is_main_article_image(img, normalized_url):
                    logger.debug(f"Found fallback main image: {normalized_url}")
                    return normalized_url
        
        logger.debug("No main image found after all attempts")
        return ""
    
    def _normalize_image_url(self, url: str) -> str:
        """Normalize image URL to absolute URL"""
        if not url:
            return ""
        
        url = url.strip()
        
        # Convert relative URLs to absolute
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            return self.base_url + url
        elif url.startswith('http'):
            return url
        else:
            # Relative path without leading slash
            return self.base_url + '/' + url
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image URL"""
        if not url or len(url) < 10:
            return False
        
        url_lower = url.lower()
        
        # Check for common image extensions or patterns
        image_patterns = [
            '.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg',
            'img.', 'images.', 'photos.', 'cdn.', 'static.', 'assets.',
            'media.', 'uploads.', 'files.'
        ]
        
        has_image_pattern = any(pattern in url_lower for pattern in image_patterns)
        
        if not has_image_pattern:
            # Also accept if it's from the same domain and could be an image
            if self.base_url.split('//')[1] in url_lower:
                has_image_pattern = True
        
        if not has_image_pattern:
            return False
        
        # Filter out common non-article images (be less strict)
        excluded_patterns = [
            'logo', 'icon-', 'avatar', 'profile-', 'share-', 'social-',
            'banner-', 'ad-', 'advertisement', 'promo-', 'widget-',
            'placeholder', 'default-', 'blank', '1x1', 'pixel',
            'facebook', 'twitter', 'youtube', 'instagram'
        ]
        
        for pattern in excluded_patterns:
            if pattern in url_lower:
                return False
        
        # Size check - filter out very small images
        if any(size in url_lower for size in ['_16x', '_24x', '_32x', '_50x', '_thumb']):
            return False
        
        return True
    
    def _is_main_article_image(self, img_element, src: str) -> bool:
        """Check if image is likely the main article image"""
        # Be more lenient - accept more images as potential main images
        
        # Check image dimensions if available
        width = img_element.get('width')
        height = img_element.get('height')
        
        try:
            if width and height:
                w, h = int(width), int(height)
                # Main images are usually larger than 100x100
                if w < 100 or h < 100:
                    return False
                # Very large images are likely main images
                if w > 300 or h > 200:
                    return True
        except (ValueError, TypeError):
            pass
        
        # Check alt text for meaningful content
        alt_text = img_element.get('alt', '').lower()
        if alt_text:
            # Images with descriptive alt text are more likely to be main images
            if len(alt_text) > 5 and not any(word in alt_text for word in ['logo', 'icon', 'share', 'social']):
                return True
        
        # Check image file name
        src_lower = src.lower()
        # If filename suggests it's a main image
        if any(term in src_lower for term in ['main', 'feature', 'hero', 'lead', 'primary', 'banner']):
            return True
        
        # Check parent elements for article-related classes
        parent_classes = []
        parent = img_element.parent
        level = 0
        while parent and level < 5:  # Check up to 5 levels up
            if hasattr(parent, 'get') and parent.get('class'):
                parent_classes.extend(parent.get('class'))
            parent = getattr(parent, 'parent', None)
            level += 1
        
        parent_class_text = ' '.join(parent_classes).lower()
        article_indicators = ['story', 'article', 'content', 'main', 'featured', 'hero', 'post', 'entry']
        if any(indicator in parent_class_text for indicator in article_indicators):
            return True
        
        # Check if image has good size attributes or data attributes
        if img_element.get('data-src') or img_element.get('data-lazy-src'):
            return True
        
        # Default to accepting images unless clearly excluded
        return True
    
    def scrape_articles(self, limit: int = 10) -> List[Dict]:
        """Scrape multiple articles"""
        if limit == 0:
            logger.info(f"Starting to scrape ALL available articles from Prothom Alo")
        else:
            logger.info(f"Starting to scrape {limit} articles from Prothom Alo")
        
        # Get more links when limit=0 or when we need buffer for failures
        multiplier = 3 if limit > 0 else 1
        article_links = self.get_article_links(limit * multiplier if limit > 0 else 0)
        articles = []
        
        total_links = len(article_links)
        for i, link in enumerate(article_links):
            # Only break if we have enough and limit > 0
            if limit > 0 and len(articles) >= limit:
                break
                
            logger.info(f"Processing article {i + 1}/{total_links}")
            article_data = self.scrape_article(link)
            
            if article_data:
                articles.append(article_data)
            
            # Respect rate limiting
            time.sleep(self.delay)
        
        if limit == 0:
            logger.info(f"Successfully scraped {len(articles)} articles (ALL available)")
        else:
            logger.info(f"Successfully scraped {len(articles)} articles")
        return articles


class IttefaqScraper:
    """Scraper class for The Daily Ittefaq news website"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.base_url = "https://www.ittefaq.com.bd"
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None
                time.sleep(self.delay * (attempt + 1))
        return None
    
    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get article links from the homepage"""
        if limit == 0:
            logger.info(f"Fetching ALL available article links from Ittefaq...")
        else:
            logger.info(f"Fetching article links from Ittefaq homepage...")
        
        response = self._make_request(self.base_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = []
        
        # Find article links - Ittefaq uses links to individual articles
        # Pattern: //www.ittefaq.com.bd/751813/...
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            
            # Check if it's an article URL (contains number pattern)
            if re.match(r'^//www\.ittefaq\.com\.bd/\d+/', href):
                full_url = 'https:' + href
                if full_url not in article_links:
                    logger.debug(f"Added article link: {full_url}")
                    article_links.append(full_url)
            elif re.match(r'^https://www\.ittefaq\.com\.bd/\d+/', href):
                if href not in article_links:
                    logger.debug(f"Added article link: {href}")
                    article_links.append(href)
            elif href.startswith('/') and re.match(r'^/\d+/', href):
                # Relative URL
                full_url = self.base_url + href
                if full_url not in article_links:
                    logger.debug(f"Added article link: {full_url}")
                    article_links.append(full_url)
        
        logger.info(f"Found {len(article_links)} article links")
        
        # If limit is 0, return all links, otherwise return the requested number
        if limit == 0:
            return article_links
        else:
            return article_links[:limit * 3]  # Get extra links as buffer
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape a single article from the given URL"""
        logger.info(f"Scraping article: {url}")
        
        response = self._make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = self._extract_title(soup)
        if not title:
            logger.warning(f"Could not extract title from {url}")
            return None
        
        # Extract content
        content = self._extract_content(soup)
        if not content:
            logger.warning(f"Could not extract content from {url}")
            return None
        
        # Extract author and date
        author = self._extract_author(soup)
        date = self._extract_date(soup)
        
        # Extract main image
        image_url = self._extract_main_image(soup, url)
        
        article_data = {
            'title': title.strip(),
            'content': content.strip(),
            'author': author.strip() if author else 'ইত্তেফাক ডিজিটাল ডেস্ক',
            'date': date,
            'url': url,
            'image_url': image_url,
            'scraped_at': datetime.now().isoformat()
        }
        
        logger.info(f"Successfully scraped: {title[:50]}...")
        return article_data
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        # Try different title selectors
        selectors = [
            'h1',  # Main heading
            '.article-title',
            'title'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                # Clean up title (remove site name if present)
                if ' - The Daily Ittefaq' in title:
                    title = title.replace(' - The Daily Ittefaq', '')
                if title and len(title) > 10:  # Ensure it's a meaningful title
                    return title
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content"""
        content_parts = []
        
        # Find article content area
        # Based on the webpage structure, content appears to be in paragraph tags
        # Let's look for the main content area
        
        # Try to find paragraphs with actual content
        paragraphs = soup.find_all('p')
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            
            # Skip empty paragraphs, navigation items, and ads
            if (text and len(text) > 20 and 
                not any(skip in text.lower() for skip in [
                    'share', 'facebook', 'twitter', 'ফেসবুক', 'টুইটার',
                    'copyright', 'সর্বস্বত্ব সংরক্ষিত', 'প্রকাশক', 'সম্পাদক',
                    'মুদ্রিত', 'কাওরান বাজার', 'ঢাকা-১২১৫'
                ])):
                content_parts.append(text)
        
        # Join all content parts
        content = '\n\n'.join(content_parts)
        
        # Return content if it's substantial
        if content and len(content) > 100:
            return content
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author"""
        # Look for author information
        author_selectors = [
            '.author',
            '.byline',
            '[class*="author"]'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author = author_elem.get_text(strip=True)
                if author and len(author) < 100:  # Reasonable author name length
                    return author
        
        # Check if author info is in the content itself
        # Look for patterns like "ইত্তেফাক ডিজিটাল ডেস্ক প্রকাশ : ১৩ সেপ্টেম্বর ২০২৫"
        text = soup.get_text()
        author_match = re.search(r'(ইত্তেফাক ডিজিটাল ডেস্ক|ইত্তেফাক[^।\n]*?) প্রকাশ\s*:', text)
        if author_match:
            return author_match.group(1).strip()
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract article date"""
        # Try to find date in meta tags first
        date_meta = soup.find('meta', {'property': 'article:published_time'})
        if date_meta:
            return date_meta.get('content', '')
        
        date_meta = soup.find('meta', {'name': 'publish-date'})
        if date_meta:
            return date_meta.get('content', '')
        
        # Look for date in the text content
        text = soup.get_text()
        
        # Pattern: "প্রকাশ : ১৩ সেপ্টেম্বর ২০২৫, ২৩:১৭"
        date_match = re.search(r'প্রকাশ\s*:\s*([\d\s]*[০-৯\s]*\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)\s*[\d০-৯]+(?:,\s*[\d০-৯:]+)?)', text)
        if date_match:
            bengali_date = date_match.group(1).strip()
            # Convert to ISO format for consistency
            return self._convert_bengali_date(bengali_date)
        
        # Default to current date if no date found
        return datetime.now().isoformat()
    
    def _convert_bengali_date(self, bengali_date: str) -> str:
        """Convert Bengali date to ISO format"""
        # Mapping Bengali numbers to English
        bengali_to_english = {
            '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
            '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9'
        }
        
        # Mapping Bengali months to English
        month_map = {
            'জানুয়ারি': '01', 'ফেব্রুয়ারি': '02', 'মার্চ': '03', 'এপ্রিল': '04',
            'মে': '05', 'জুন': '06', 'জুলাই': '07', 'আগস্ট': '08',
            'সেপ্টেম্বর': '09', 'অক্টোবর': '10', 'নভেম্বর': '11', 'ডিসেম্বর': '12'
        }
        
        # Convert Bengali numerals to English
        english_date = bengali_date
        for bengali, english in bengali_to_english.items():
            english_date = english_date.replace(bengali, english)
        
        # Parse date components
        for bengali_month, month_num in month_map.items():
            if bengali_month in english_date:
                # Extract day, month, year
                parts = english_date.split()
                day = parts[0] if parts else '1'
                year = None
                time_part = ''
                
                for part in parts:
                    if len(part) == 4 and part.isdigit():  # Year
                        year = part
                    elif ':' in part:  # Time
                        time_part = part
                
                if year:
                    day = day.zfill(2)
                    if time_part:
                        # Parse time
                        hour, minute = time_part.split(':')[:2]
                        return f"{year}-{month_num}-{day}T{hour.zfill(2)}:{minute.zfill(2)}:00+06:00"
                    else:
                        return f"{year}-{month_num}-{day}T00:00:00+06:00"
        
        # If parsing fails, return current datetime
        return datetime.now().isoformat()
    
    def _extract_main_image(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Extract the main article image"""
        logger.debug(f"Extracting images for: {url}")
        
        # Try Open Graph image first (most reliable)
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image and og_image.get('content'):
            image_url = og_image.get('content')
            logger.debug(f"Found meta image (meta[property=\"og:image\"]): {image_url}")
            if self._is_valid_image_url(image_url):
                return image_url
        
        # Try Twitter card image
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image.get('content')
            logger.debug(f"Found Twitter image: {image_url}")
            if self._is_valid_image_url(image_url):
                return image_url
        
        # Try to find article images in the content
        images = soup.find_all('img')
        logger.debug(f"Found {len(images)} total images on page")
        
        for img in images:
            src = img.get('src') or img.get('data-src')
            if src and self._is_valid_image_url(src):
                # Make URL absolute if relative
                if src.startswith('/'):
                    src = self.base_url + src
                elif src.startswith('//'):
                    src = 'https:' + src
                
                if self._is_main_article_image(img, src):
                    logger.debug(f"Found main article image: {src}")
                    return src
        
        logger.debug("No suitable main image found")
        return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image URL"""
        if not url:
            return False
        
        # Check for image file extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        url_lower = url.lower()
        
        # Must contain image extension or be from known image domains
        has_extension = any(ext in url_lower for ext in image_extensions)
        is_image_domain = any(domain in url_lower for domain in [
            'media.ittefaq.com', 'images.ittefaq.com', 'img.ittefaq.com',
            'ittefaq.com', 'cloudinary.com', 'imgbb.com'
        ])
        
        return has_extension or is_image_domain
    
    def _is_main_article_image(self, img_tag, src: str) -> bool:
        """Determine if this is likely the main article image"""
        # Check image dimensions
        width = img_tag.get('width')
        height = img_tag.get('height')
        
        if width and height:
            try:
                w, h = int(width), int(height)
                if w > 200 and h > 150:  # Reasonable size for main image
                    return True
            except ValueError:
                pass
        
        # Check for main image indicators in class or attributes
        classes = ' '.join(img_tag.get('class', []))
        alt_text = img_tag.get('alt', '')
        
        main_indicators = ['main', 'hero', 'featured', 'article', 'news']
        if any(indicator in classes.lower() for indicator in main_indicators):
            return True
        
        if any(indicator in alt_text.lower() for indicator in main_indicators):
            return True
        
        # Check if image has substantial alt text (likely main image)
        if alt_text and len(alt_text) > 10:
            return True
        
        return False
    
    def scrape_articles(self, limit: int = 10) -> List[Dict]:
        """Scrape multiple articles"""
        logger.info(f"Starting to scrape {limit if limit > 0 else 'ALL'} articles from Ittefaq")
        
        # Get more links than needed to ensure we have enough valid articles
        multiplier = 3
        article_links = self.get_article_links(limit * multiplier if limit > 0 else 0)
        articles = []
        
        total_links = len(article_links)
        for i, link in enumerate(article_links):
            # Only break if we have enough and limit > 0
            if limit > 0 and len(articles) >= limit:
                break
                
            logger.info(f"Processing article {i + 1}/{total_links}")
            article_data = self.scrape_article(link)
            
            if article_data:
                articles.append(article_data)
            
            # Respect rate limiting
            time.sleep(self.delay)
        
        if limit == 0:
            logger.info(f"Successfully scraped {len(articles)} articles (ALL available)")
        else:
            logger.info(f"Successfully scraped {len(articles)} articles")
        return articles