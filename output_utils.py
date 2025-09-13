"""
Output utilities for saving scraped news articles
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def save_to_json(articles: List[Dict], site_name: str, output_dir: str = ".") -> str:
    """Save articles to JSON file with UTF-8 encoding"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"{timestamp}_{site_name}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        raise


def save_to_csv(articles: List[Dict], site_name: str, output_dir: str = ".") -> str:
    """Save articles to CSV file with UTF-8 encoding"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"{timestamp}_{site_name}.csv"
    filepath = os.path.join(output_dir, filename)
    
    if not articles:
        logger.warning("No articles to save")
        return filepath
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all unique keys from articles
        fieldnames = set()
        for article in articles:
            fieldnames.update(article.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                # Clean content for CSV (remove newlines that might break formatting)
                cleaned_article = {}
                for key, value in article.items():
                    if isinstance(value, str):
                        # Replace newlines with spaces for CSV compatibility
                        cleaned_article[key] = value.replace('\n', ' ').replace('\r', ' ')
                    else:
                        cleaned_article[key] = value
                
                writer.writerow(cleaned_article)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        raise


def display_articles_summary(articles: List[Dict]) -> None:
    """Display a summary of scraped articles"""
    if not articles:
        print("No articles found.")
        return
    
    print(f"\n{'='*60}")
    print(f"SCRAPED ARTICLES SUMMARY ({len(articles)} articles)")
    print(f"{'='*60}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get('title', 'No title')[:80]}...")
        print(f"   Author: {article.get('author', 'Unknown')}")
        print(f"   Date: {article.get('date', 'Unknown')}")
        print(f"   URL: {article.get('url', 'Unknown')}")
        print(f"   Image: {article.get('image_url', 'No image') if article.get('image_url') else 'No image'}")
        print(f"   Content length: {len(article.get('content', ''))} characters")
    
    print(f"\n{'='*60}")


def validate_articles(articles: List[Dict]) -> List[Dict]:
    """Validate and clean article data"""
    valid_articles = []
    
    for article in articles:
        # Check if article has minimum required fields
        if not article.get('title') or not article.get('content'):
            logger.warning(f"Skipping invalid article: {article.get('url', 'Unknown URL')}")
            continue
        
        # Clean and validate data
        cleaned_article = {
            'title': str(article.get('title', '')).strip(),
            'content': str(article.get('content', '')).strip(),
            'author': str(article.get('author', 'Unknown')).strip(),
            'date': str(article.get('date', '')).strip(),
            'url': str(article.get('url', '')).strip(),
            'image_url': str(article.get('image_url', '')).strip(),
            'scraped_at': article.get('scraped_at', datetime.now().isoformat())
        }
        
        # Additional validation
        if len(cleaned_article['title']) < 5:
            logger.warning(f"Title too short, skipping: {cleaned_article['url']}")
            continue
        
        if len(cleaned_article['content']) < 50:
            logger.warning(f"Content too short, skipping: {cleaned_article['url']}")
            continue
        
        valid_articles.append(cleaned_article)
    
    logger.info(f"Validated {len(valid_articles)} out of {len(articles)} articles")
    return valid_articles