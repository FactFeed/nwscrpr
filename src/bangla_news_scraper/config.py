"""
Configuration settings for Bangla News Scraper
"""

import os
from typing import Dict, List


class Config:
    """Configuration class for the news scraper"""
    
    # Default settings
    DEFAULT_DELAY = 1.0
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 10
    
    # Request headers
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Site configurations
    SITES = {
        'prothom-alo': {
            'name': 'Prothom Alo',
            'base_url': 'https://www.prothomalo.com',
            'sections': [
                '/bangladesh',
                '/world', 
                '/sports',
                '/entertainment',
                '/business',
                '/opinion',
                '/politics',
                '/lifestyle',
                '/tech'
            ]
        },
        'ittefaq': {
            'name': 'The Daily Ittefaq',
            'base_url': 'https://www.ittefaq.com.bd',
            'sections': []
        }
    }
    
    # Content extraction patterns
    EXCLUDED_URL_PATTERNS = [
        '/tag/', '/author/', '/category/', '/search',
        'javascript:', 'mailto:', '#', '/static/',
        '/assets/', '.jpg', '.png', '.gif', '.pdf',
        '/page/', '/archive/', '/contact', '/about',
        'facebook.com', 'twitter.com', 'youtube.com',
        '/api/', '/oauth/', '/auth/', '/login',
        '/collection/', '/latest'
    ]
    
    EXCLUDED_IMAGE_PATTERNS = [
        'logo', 'icon-', 'avatar', 'profile-', 'share-', 'social-',
        'banner-', 'ad-', 'advertisement', 'promo-', 'widget-',
        'placeholder', 'default-', 'blank', '1x1', 'pixel',
        'facebook', 'twitter', 'youtube', 'instagram'
    ]
    
    # Logging configuration
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_LEVEL = 'INFO'
    
    # Cache settings
    CACHE_ENABLED = True
    CACHE_DURATION_HOURS = 24
    CACHE_DIR = os.path.join(os.getcwd(), '.cache')
    
    # Output settings
    DEFAULT_OUTPUT_FORMAT = 'json'
    DEFAULT_OUTPUT_DIR = '.'
    
    @classmethod
    def get_site_config(cls, site_name: str) -> Dict:
        """Get configuration for a specific site"""
        return cls.SITES.get(site_name, {})
    
    @classmethod
    def get_site_names(cls) -> List[str]:
        """Get list of available site names"""
        return list(cls.SITES.keys())