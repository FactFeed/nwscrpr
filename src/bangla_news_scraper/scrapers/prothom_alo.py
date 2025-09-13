"""
Prothom Alo news scraper implementation
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import re

from .base import BaseScraper
from ..models import Article
from ..config import Config


class ProthomAloScraper(BaseScraper):
    """Scraper implementation for Prothom Alo news website"""
    
    @property
    def base_url(self) -> str:
        return Config.get_site_config('prothom-alo')['base_url']
    
    @property 
    def site_name(self) -> str:
        return Config.get_site_config('prothom-alo')['name']
    
    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get article links from the homepage and sections"""
        if limit == 0:
            self.logger.info("Fetching ALL available article links from Prothom Alo...")
        else:
            self.logger.info("Fetching article links from Prothom Alo homepage...")
        
        response = self._make_request(self.base_url)
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = []
        
        # Find all anchor tags and filter for actual article links
        all_links = soup.find_all('a', href=True)
        self.logger.info(f"Found {len(all_links)} total links on homepage")
        
        for link in all_links:
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute
                full_url = self._normalize_url(href)
                
                # Filter for actual article URLs
                if self._is_article_link(full_url) and full_url not in links:
                    links.append(full_url)
                    self.logger.debug(f"Added article link: {full_url}")
                    
                # Only break if limit > 0
                if limit > 0 and len(links) >= limit:
                    break
        
        # If we need more links, try browsing specific sections
        if limit == 0 or len(links) < limit:
            sections = Config.get_site_config('prothom-alo')['sections']
            
            for section in sections:
                if limit > 0 and len(links) >= limit:
                    break
                    
                section_url = self.base_url + section
                self.logger.info(f"Checking section: {section_url}")
                
                section_response = self._make_request(section_url)
                if section_response:
                    section_soup = BeautifulSoup(section_response.content, 'html.parser')
                    section_links = section_soup.find_all('a', href=True)
                    
                    for link in section_links:
                        href = link.get('href')
                        if href:
                            full_url = self._normalize_url(href)
                            
                            if self._is_article_link(full_url) and full_url not in links:
                                links.append(full_url)
                                self.logger.debug(f"Added section article link: {full_url}")
                                
                            if limit > 0 and len(links) >= limit:
                                break
        
        if limit == 0:
            self.logger.info(f"Found {len(links)} total article links (ALL available)")
        else:
            self.logger.info(f"Found {len(links)} article links")
            return links[:limit]
        
        return links
    
    def _is_article_link(self, url: str) -> bool:
        """Check if URL is an actual article link"""
        if not self._is_valid_url(url):
            return False
        
        # Prothom Alo specific excluded patterns
        excluded_patterns = [
            'prothomalo.com/bangladesh$',
            'prothomalo.com/world$',
            'prothomalo.com/sports$',
            'prothomalo.com/entertainment$',
            'prothomalo.com/business$',
            'prothomalo.com/politics$',
            'prothomalo.com/opinion$',
            'prothomalo.com/lifestyle$',
            'prothomalo.com/tech$',
            'prothomalo.com/$',
        ]
        
        for pattern in excluded_patterns:
            if url.endswith(pattern[:-1]):  # Remove $ from pattern
                return False
        
        # Look for actual article patterns
        if len(url.split('/')) >= 5:  # Articles usually have deeper paths
            return True
        
        # Check for date patterns in URL
        if re.search(r'/\d{4}/\d{2}/\d{2}/', url):
            return True
        
        # Check for article ID patterns
        if re.search(r'/\d+/', url):
            return True
        
        # Check if URL has article-like text
        if re.search(r'/[a-zA-Z0-9\-]{20,}/?$', url):
            return True
        
        return False
    
    def scrape_article(self, url: str) -> Optional[Article]:
        """Scrape a single article"""
        self.logger.info(f"Scraping article: {url}")
        
        response = self._make_request(url)
        if not response:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        try:
            article = Article(
                url=url,
                title=self._extract_title(soup),
                content=self._extract_content(soup),
                author=self._extract_author(soup),
                date=self._extract_date(soup),
                image_url=self._extract_main_image(soup, url),
                site_name=self.site_name
            )
            
            if article.is_valid():
                self.logger.info(f"Successfully scraped: {article.get_title_preview()}")
                return article
            else:
                self.logger.warning(f"Incomplete article data for {url}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error extracting article data from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
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
                    if text and len(text) > 50:
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
        self.logger.debug(f"Extracting images for: {article_url}")
        
        # First try meta tags
        meta_image = self._extract_meta_image(soup)
        if meta_image:
            return meta_image
        
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
                            return self._normalize_url(str(image))
            except:
                continue
        
        # Try various image selectors
        image_selectors = [
            'img[width][height]',
            '.story-element img',
            '.article-image img',
            '.content-image img',
            '.featured-image img',
            '.hero-image img',
            'figure img',
            'picture img',
            '.story-content img',
            'article img',
            'main img'
        ]
        
        for selector in image_selectors:
            elements = soup.select(selector)
            for element in elements:
                src = (element.get('src') or element.get('data-src') or 
                      element.get('data-lazy-src') or element.get('data-original'))
                
                if src:
                    normalized_url = self._normalize_url(src)
                    if (self._is_valid_image_url(normalized_url) and 
                        self._is_main_article_image(element, normalized_url)):
                        return normalized_url
        
        return ""
    
    def _is_main_article_image(self, img_element, src: str) -> bool:
        """Check if image is likely the main article image"""
        # Check image dimensions
        width = img_element.get('width')
        height = img_element.get('height')
        
        try:
            if width and height:
                w, h = int(width), int(height)
                if w < 100 or h < 100:
                    return False
                if w > 300 or h > 200:
                    return True
        except (ValueError, TypeError):
            pass
        
        # Check alt text
        alt_text = img_element.get('alt', '').lower()
        if alt_text and len(alt_text) > 5:
            if not any(word in alt_text for word in ['logo', 'icon', 'share', 'social']):
                return True
        
        # Check image filename
        src_lower = src.lower()
        if any(term in src_lower for term in ['main', 'feature', 'hero', 'lead', 'primary']):
            return True
        
        # Check parent elements
        parent_classes = []
        parent = img_element.parent
        level = 0
        while parent and level < 5:
            if hasattr(parent, 'get') and parent.get('class'):
                parent_classes.extend(parent.get('class'))
            parent = getattr(parent, 'parent', None)
            level += 1
        
        parent_class_text = ' '.join(parent_classes).lower()
        article_indicators = ['story', 'article', 'content', 'main', 'featured', 'hero']
        if any(indicator in parent_class_text for indicator in article_indicators):
            return True
        
        return True  # Default to accepting images unless clearly excluded