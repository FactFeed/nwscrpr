"""
The Daily Ittefaq news scraper implementation
"""

from typing import List, Optional
from bs4 import BeautifulSoup
from datetime import datetime
import re

from .base import BaseScraper
from ..models import Article
from ..config import Config


class IttefaqScraper(BaseScraper):
    """Scraper implementation for The Daily Ittefaq news website"""
    
    @property
    def base_url(self) -> str:
        return Config.get_site_config('ittefaq')['base_url']
    
    @property
    def site_name(self) -> str:
        return Config.get_site_config('ittefaq')['name']
    
    def get_article_links(self, limit: int = 10) -> List[str]:
        """Get article links from the homepage"""
        if limit == 0:
            self.logger.info("Fetching ALL available article links from Ittefaq...")
        else:
            self.logger.info("Fetching article links from Ittefaq homepage...")
        
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
                    self.logger.debug(f"Added article link: {full_url}")
                    article_links.append(full_url)
            elif re.match(r'^https://www\.ittefaq\.com\.bd/\d+/', href):
                if href not in article_links:
                    self.logger.debug(f"Added article link: {href}")
                    article_links.append(href)
            elif href.startswith('/') and re.match(r'^/\d+/', href):
                # Relative URL
                full_url = self.base_url + href
                if full_url not in article_links:
                    self.logger.debug(f"Added article link: {full_url}")
                    article_links.append(full_url)
        
        self.logger.info(f"Found {len(article_links)} article links")
        
        # Return based on limit
        if limit == 0:
            return article_links
        else:
            return article_links[:limit * 3]  # Get extra links as buffer
    
    def scrape_article(self, url: str) -> Optional[Article]:
        """Scrape a single article from the given URL"""
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
                author=self._extract_author(soup) or 'ইত্তেফাক ডিজিটাল ডেস্ক',
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
                if title and len(title) > 10:
                    return title
        
        return "No title found"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article content"""
        content_parts = []
        
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
        
        return "No content found"
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
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
                if author and len(author) < 100:
                    return author
        
        # Check if author info is in the content itself
        text = soup.get_text()
        author_match = re.search(
            r'(ইত্তেফাক ডিজিটাল ডেস্ক|ইত্তেফাক[^।\n]*?) প্রকাশ\s*:', 
            text
        )
        if author_match:
            return author_match.group(1).strip()
        
        return "Unknown"
    
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
        
        # Pattern: "প্রকাশ : ১৩ সেপ্টেম্বর ২০২৫, ২৩:১১"
        date_match = re.search(
            r'প্রকাশ\s*:\s*([\d\s]*[০-৯\s]*\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)\s*[\d০-৯]+(?:,\s*[\d০-৯:]+)?)', 
            text
        )
        if date_match:
            bengali_date = date_match.group(1).strip()
            return self._convert_bengali_date(bengali_date)
        
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
                        hour, minute = time_part.split(':')[:2]
                        return f"{year}-{month_num}-{day}T{hour.zfill(2)}:{minute.zfill(2)}:00+06:00"
                    else:
                        return f"{year}-{month_num}-{day}T00:00:00+06:00"
        
        return datetime.now().isoformat()
    
    def _extract_main_image(self, soup: BeautifulSoup, url: str) -> str:
        """Extract the main article image"""
        self.logger.debug(f"Extracting images for: {url}")
        
        # Try meta tags first
        meta_image = self._extract_meta_image(soup)
        if meta_image:
            return meta_image
        
        # Try to find article images in the content
        images = soup.find_all('img')
        self.logger.debug(f"Found {len(images)} total images on page")
        
        for img in images:
            src = img.get('src') or img.get('data-src')
            if src and self._is_valid_image_url(src):
                # Make URL absolute if relative
                normalized_url = self._normalize_url(src)
                
                if self._is_main_article_image(img, normalized_url):
                    self.logger.debug(f"Found main article image: {normalized_url}")
                    return normalized_url
        
        self.logger.debug("No suitable main image found")
        return ""
    
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
        
        # Check for main image indicators
        classes = ' '.join(img_tag.get('class', []))
        alt_text = img_tag.get('alt', '')
        
        main_indicators = ['main', 'hero', 'featured', 'article', 'news']
        if any(indicator in classes.lower() for indicator in main_indicators):
            return True
        
        if any(indicator in alt_text.lower() for indicator in main_indicators):
            return True
        
        # Check if image has substantial alt text
        if alt_text and len(alt_text) > 10:
            return True
        
        return False