"""
Data models for the Bangla News Scraper
"""

from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import re


@dataclass
class Article:
    """Data model for a news article"""
    title: str
    content: str
    url: str
    author: Optional[str] = None
    date: Optional[str] = None
    image_url: Optional[str] = None
    scraped_at: Optional[str] = None
    site_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()
        
        # Clean and validate title
        if self.title:
            self.title = self.title.strip()
        
        # Clean and validate content
        if self.content:
            self.content = self.content.strip()
        
        # Clean and validate author
        if self.author:
            self.author = self.author.strip()
        
        # Clean and validate URL
        if self.url:
            self.url = self.url.strip()
        
        # Clean and validate image URL
        if self.image_url:
            self.image_url = self.image_url.strip()
    
    def is_valid(self) -> bool:
        """Check if the article has minimum required data"""
        return (
            bool(self.title and len(self.title) >= 5) and
            bool(self.content and len(self.content) >= 50) and
            bool(self.url and self._is_valid_url(self.url))
        )
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """Create article from dictionary"""
        return cls(**data)
    
    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a preview of the content"""
        if not self.content:
            return ""
        
        if len(self.content) <= max_length:
            return self.content
        
        return self.content[:max_length].rsplit(' ', 1)[0] + "..."
    
    def get_title_preview(self, max_length: int = 80) -> str:
        """Get a preview of the title"""
        if not self.title:
            return ""
        
        if len(self.title) <= max_length:
            return self.title
        
        return self.title[:max_length].rsplit(' ', 1)[0] + "..."


@dataclass
class ScrapingResult:
    """Result of a scraping operation"""
    articles: list[Article]
    site_name: str
    total_requested: int
    total_found: int
    total_valid: int
    scraped_at: str
    duration_seconds: Optional[float] = None
    
    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()
    
    def get_success_rate(self) -> float:
        """Get the success rate of scraping"""
        if self.total_found == 0:
            return 0.0
        return (self.total_valid / self.total_found) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'articles': [article.to_dict() for article in self.articles],
            'site_name': self.site_name,
            'total_requested': self.total_requested,
            'total_found': self.total_found,
            'total_valid': self.total_valid,
            'scraped_at': self.scraped_at,
            'duration_seconds': self.duration_seconds,
            'success_rate': self.get_success_rate()
        }