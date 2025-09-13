"""
Output utilities for saving scraped news articles
"""

import json
import csv
import os
from datetime import datetime
from typing import List, Union
from ..models import Article, ScrapingResult
from ..utils import get_logger

logger = get_logger(__name__)


def save_to_json(
    data: Union[List[Article], ScrapingResult], 
    site_name: str, 
    output_dir: str = "output"
) -> str:
    """Save articles or scraping result to JSON file with UTF-8 encoding"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"{timestamp}_{site_name}.json"
    # Create json subdirectory within output directory
    json_dir = os.path.join(output_dir, "json")
    filepath = os.path.join(json_dir, filename)
    
    try:
        # Ensure output directory exists
        os.makedirs(json_dir, exist_ok=True)
        
        # Convert to dictionary format
        if isinstance(data, ScrapingResult):
            json_data = data.to_dict()
        else:
            json_data = [article.to_dict() for article in data]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        count = len(data.articles) if isinstance(data, ScrapingResult) else len(data)
        logger.info(f"Saved {count} articles to {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving to JSON: {e}")
        raise


def save_to_csv(
    data: Union[List[Article], ScrapingResult], 
    site_name: str, 
    output_dir: str = "output"
) -> str:
    """Save articles to CSV file with UTF-8 encoding"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    filename = f"{timestamp}_{site_name}.csv"
    # Create csv subdirectory within output directory
    csv_dir = os.path.join(output_dir, "csv")
    filepath = os.path.join(csv_dir, filename)
    
    # Extract articles from data
    articles = data.articles if isinstance(data, ScrapingResult) else data
    
    if not articles:
        logger.warning("No articles to save")
        return filepath
    
    try:
        # Ensure output directory exists
        os.makedirs(csv_dir, exist_ok=True)
        
        # Define fieldnames in a specific order
        fieldnames = [
            'title', 'content', 'author', 'date', 'url', 
            'image_url', 'site_name', 'scraped_at'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                # Clean content for CSV (remove newlines that might break formatting)
                article_dict = article.to_dict()
                cleaned_article = {}
                
                for key, value in article_dict.items():
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


def display_articles_summary(data: Union[List[Article], ScrapingResult]) -> None:
    """Display a summary of scraped articles"""
    articles = data.articles if isinstance(data, ScrapingResult) else data
    
    if not articles:
        print("No articles found.")
        return
    
    print(f"\n{'='*60}")
    print(f"SCRAPED ARTICLES SUMMARY ({len(articles)} articles)")
    if isinstance(data, ScrapingResult):
        print(f"Site: {data.site_name}")
        print(f"Success Rate: {data.get_success_rate():.1f}%")
        if data.duration_seconds:
            print(f"Duration: {data.duration_seconds:.2f} seconds")
    print(f"{'='*60}")
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get_title_preview()}")
        print(f"   Author: {article.author or 'Unknown'}")
        print(f"   Date: {article.date or 'Unknown'}")
        print(f"   URL: {article.url or 'Unknown'}")
        print(f"   Image: {'Yes' if article.image_url else 'No'}")
        print(f"   Content length: {len(article.content or '')} characters")
    
    print(f"\n{'='*60}")


def validate_articles(articles: List[Article]) -> List[Article]:
    """Validate and filter article data"""
    valid_articles = []
    
    for article in articles:
        if article.is_valid():
            valid_articles.append(article)
        else:
            logger.warning(f"Skipping invalid article: {article.url}")
    
    logger.info(f"Validated {len(valid_articles)} out of {len(articles)} articles")
    return valid_articles