#!/usr/bin/env python3
"""
Bangla News Scraper - Main Entry Point

A simple command-line tool to scrape news articles from Bangladeshi news websites.

Usage:
    python news_scraper.py --run --site=prothom-alo --limit=5 --output=json
    python news_scraper.py -r -s prothom-alo -l 10 -o csv

Author: Rayat Chowdhury
Version: 1.0.0
"""

import sys
import os

# Add current directory to Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main

if __name__ == '__main__':
    main()