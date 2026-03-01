from typing import Optional
from app.core.cache.base_cache import BaseCache
from redis.exceptions import RedisError

class URLCache(BaseCache):
    """Cache implementation for URL shortener using Redis."""
    
    def __init__(self):
        super().__init__(key_prefix="URL_SHORTENER")
        
    def cache_url(self, short_code: str, original_url: str, ttl: int = 3600) -> None:
        """
        Cache the original URL with the short code as key.
        
        Args:
            short_code: The short code to use as cache key.
            original_url: The original URL to cache.
            ttl: Time to live for the cache entry in seconds (default: 1 hour).
        
        """
        try:
            key = self._make_key(short_code)
            self.redis_client.set(key, original_url, ex=ttl)
        except RedisError as e:
            self._handle_redis_error(e, "cache_url")
    
    def get_cached_url(self, short_code: str) -> Optional[str]:
        """
        Get cached original url for a given short code.
        
        Args:
            short_code: The short code to look up in cache.
        """
        try:
            key = self._make_key(short_code)
            return self.redis_client.get(key)
        except RedisError as e:
            self._handle_redis_error(e, "get_cached_url")
            return None
        
    def invalidate_cache(self, short_code: str) -> None:
        """
        Invalidate the cache entry for a given short code.
        
        Args:
            short_code: The short code whose cache entry should be invalidated.
        """
        try:
            key = self._make_key(short_code)
            self.redis_client.delete(key)
        except RedisError as e:
            self._handle_redis_error(e, "invalidate_cache")
    
# Singleton instance of URLCache for use across the application
url_cache = URLCache()
