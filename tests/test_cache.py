"""
Tests for cache functionality
"""

import pytest
import json
import os
from bangla_news_scraper.utils.cache import ArticleCache
from bangla_news_scraper.models import Article
from .conftest import SAMPLE_ARTICLE_DATA


class TestArticleCache:
    """Test ArticleCache functionality"""
    
    def test_cache_creation(self, temp_dir):
        """Test creating cache with custom directory"""
        cache = ArticleCache(cache_dir=temp_dir)
        assert cache.cache_dir == temp_dir
        assert os.path.exists(temp_dir)
    
    def test_cache_key_generation(self, temp_dir):
        """Test cache key generation"""
        cache = ArticleCache(cache_dir=temp_dir)
        url = "https://example.com/article"
        key1 = cache._get_cache_key(url)
        key2 = cache._get_cache_key(url)
        
        assert key1 == key2  # Same URL should generate same key
        assert len(key1) == 32  # MD5 hash length
        assert isinstance(key1, str)
    
    def test_cache_set_and_get(self, temp_dir):
        """Test setting and getting articles from cache"""
        cache = ArticleCache(cache_dir=temp_dir)
        article = Article(**SAMPLE_ARTICLE_DATA)
        url = article.url
        
        # Set article in cache
        cache.set(url, article)
        
        # Get article from cache
        cached_article = cache.get(url)
        
        assert cached_article is not None
        assert cached_article.title == article.title
        assert cached_article.content == article.content
        assert cached_article.url == article.url
    
    def test_cache_miss(self, temp_dir):
        """Test cache miss for non-existent article"""
        cache = ArticleCache(cache_dir=temp_dir)
        url = "https://example.com/nonexistent"
        
        cached_article = cache.get(url)
        assert cached_article is None
    
    def test_cache_clear(self, temp_dir):
        """Test clearing all cache"""
        cache = ArticleCache(cache_dir=temp_dir)
        article = Article(**SAMPLE_ARTICLE_DATA)
        
        # Add some articles to cache
        cache.set("https://example.com/1", article)
        cache.set("https://example.com/2", article)
        
        # Clear cache
        cleared_count = cache.clear()
        
        assert cleared_count == 2
        assert cache.get("https://example.com/1") is None
        assert cache.get("https://example.com/2") is None
    
    def test_cache_stats(self, temp_dir):
        """Test cache statistics"""
        cache = ArticleCache(cache_dir=temp_dir)
        article = Article(**SAMPLE_ARTICLE_DATA)
        
        # Initially empty
        stats = cache.get_cache_stats()
        assert stats['total_files'] == 0
        assert stats['valid_files'] == 0
        
        # Add an article
        cache.set("https://example.com/test", article)
        
        # Check stats
        stats = cache.get_cache_stats()
        assert stats['total_files'] == 1
        assert stats['valid_files'] == 1
        assert stats['total_size_mb'] > 0