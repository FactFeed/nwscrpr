"""
Bangla News Scraper - A Python package for scraping Bangladeshi news websites

Author: Rayat Chowdhury
Version: 1.1.0
"""

__version__ = "1.1.0"
__author__ = "Rayat Chowdhury"
__email__ = "rayat@example.com"

from .scrapers.base import BaseScraper
from .scrapers.prothom_alo import ProthomAloScraper
from .scrapers.ittefaq import IttefaqScraper
from .utils.output import save_to_json, save_to_csv
from .models import Article

__all__ = [
    "BaseScraper",
    "ProthomAloScraper", 
    "IttefaqScraper",
    "save_to_json",
    "save_to_csv",
    "Article"
]