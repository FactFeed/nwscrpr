#!/usr/bin/env python3
"""
Bangla News Scraper - Enhanced Version - Main Entry Point

A robust Python package for scraping news articles from Bangladeshi news websites.

Usage:
    python main.py --run --site=prothom-alo --limit=5 --output=json
    python main.py -r -s prothom-alo -l 10 -o csv --verbose

Author: Rayat Chowdhury
Version: 1.1.0 (Enhanced)
"""

import sys
import os

# Add src directory to Python path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.bangla_news_scraper.cli import main

if __name__ == '__main__':
    main()