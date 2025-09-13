"""
Simple file-based caching for scraped articles
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Any
from ..config import Config
from ..models import Article
from ..exceptions import CacheException
from ..utils import get_logger

logger = get_logger(__name__)


class ArticleCache:
    """Simple file-based cache for articles"""
    
    def __init__(self, cache_dir: str = None, cache_duration_hours: int = None):
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.cache_duration = timedelta(hours=cache_duration_hours or Config.CACHE_DURATION_HOURS)
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except OSError as e:
            raise CacheException(f"Failed to create cache directory {self.cache_dir}: {e}")
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Check if cache file is still valid (not expired)"""
        if not os.path.exists(cache_path):
            return False
        
        try:
            modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            return datetime.now() - modified_time < self.cache_duration
        except OSError:
            return False
    
    def get(self, url: str) -> Optional[Article]:
        """Get article from cache if available and valid"""
        if not Config.CACHE_ENABLED:
            return None
        
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        if not self._is_cache_valid(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                article = Article.from_dict(data)
                logger.debug(f"Cache hit for {url}")
                return article
        except (OSError, json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to read cache for {url}: {e}")
            # Remove corrupted cache file
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None
    
    def set(self, url: str, article: Article) -> None:
        """Store article in cache"""
        if not Config.CACHE_ENABLED:
            return
        
        cache_key = self._get_cache_key(url)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(article.to_dict(), f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached article: {url}")
        except OSError as e:
            logger.warning(f"Failed to cache article {url}: {e}")
    
    def clear(self) -> int:
        """Clear all cached articles"""
        cleared_count = 0
        
        if not os.path.exists(self.cache_dir):
            return cleared_count
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    try:
                        os.remove(file_path)
                        cleared_count += 1
                    except OSError as e:
                        logger.warning(f"Failed to remove cache file {file_path}: {e}")
        except OSError as e:
            raise CacheException(f"Failed to list cache directory: {e}")
        
        logger.info(f"Cleared {cleared_count} cached articles")
        return cleared_count
    
    def clear_expired(self) -> int:
        """Clear only expired cached articles"""
        cleared_count = 0
        
        if not os.path.exists(self.cache_dir):
            return cleared_count
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    if not self._is_cache_valid(file_path):
                        try:
                            os.remove(file_path)
                            cleared_count += 1
                        except OSError as e:
                            logger.warning(f"Failed to remove expired cache file {file_path}: {e}")
        except OSError as e:
            raise CacheException(f"Failed to list cache directory: {e}")
        
        logger.info(f"Cleared {cleared_count} expired cached articles")
        return cleared_count
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not os.path.exists(self.cache_dir):
            return {
                'total_files': 0,
                'valid_files': 0,
                'expired_files': 0,
                'total_size_mb': 0.0
            }
        
        total_files = 0
        valid_files = 0
        expired_files = 0
        total_size = 0
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_files += 1
                    
                    try:
                        total_size += os.path.getsize(file_path)
                        if self._is_cache_valid(file_path):
                            valid_files += 1
                        else:
                            expired_files += 1
                    except OSError:
                        expired_files += 1
        except OSError:
            pass
        
        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'expired_files': expired_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }