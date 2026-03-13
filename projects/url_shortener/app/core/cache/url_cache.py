"""
Async URL cache for high-performance URL lookups.

Performance: Redis GET is ~0.1ms vs PostgreSQL SELECT ~5ms = 50x faster
"""

from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.cache.base_cache import BaseCache


class URLCache(BaseCache):
    """Async cache implementation for URL shortener using Redis."""

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client, key_prefix="URL_SHORTENER")

    async def cache_url(self, short_code: str, original_url: str, ttl: int = 3600) -> None:
        """
        Cache the original URL with the short code as key.

        Args:
            short_code: The short code to use as cache key.
            original_url: The original URL to cache.
            ttl: Time to live in seconds (default: 1 hour).
        """
        try:
            key = self._make_key(short_code)
            await self.redis.set(key, original_url, ex=ttl)
        except RedisError as e:
            self._handle_redis_error(e, "cache_url")

    async def get_cached_url(self, short_code: str) -> Optional[str]:
        """
        Get cached original URL for a given short code.

        Args:
            short_code: The short code to look up in cache.
            
        Returns:
            The original URL if cached, None otherwise.
        """
        try:
            key = self._make_key(short_code)
            return await self.redis.get(key)
        except RedisError as e:
            self._handle_redis_error(e, "get_cached_url")
            return None

    async def invalidate_cache(self, short_code: str) -> None:
        """
        Invalidate the cache entry for a given short code.

        Args:
            short_code: The short code whose cache entry should be invalidated.
        """
        try:
            key = self._make_key(short_code)
            await self.redis.delete(key)
        except RedisError as e:
            self._handle_redis_error(e, "invalidate_cache")


# Note: Singleton is now created lazily after Redis pools are initialized
# Use get_url_cache() from cache/__init__.py instead
