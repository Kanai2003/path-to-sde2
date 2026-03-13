"""
Cache module with lazy initialization for async Redis operations.

Usage:
    from app.core.cache import get_url_cache, get_analytics_cache
    
    url_cache = get_url_cache()
    await url_cache.get_cached_url("abc123")
"""

from typing import Optional

from .analytics_cache import AnalyticsCache
from .url_cache import URLCache

# Lazy singletons - initialized after Redis pools are ready
_url_cache: Optional[URLCache] = None
_analytics_cache: Optional[AnalyticsCache] = None


def init_caches() -> None:
    """Initialize cache singletons. Called on app startup after Redis pools init."""
    global _url_cache, _analytics_cache
    
    from app.core.redis_pool import get_cache_redis, get_analytics_redis
    
    _url_cache = URLCache(get_cache_redis())
    _analytics_cache = AnalyticsCache(get_analytics_redis())


def get_url_cache() -> URLCache:
    """Get URL cache singleton."""
    if _url_cache is None:
        raise RuntimeError("Caches not initialized. Call init_caches() on startup.")
    return _url_cache


def get_analytics_cache() -> AnalyticsCache:
    """Get analytics cache singleton."""
    if _analytics_cache is None:
        raise RuntimeError("Caches not initialized. Call init_caches() on startup.")
    return _analytics_cache


__all__ = ["get_url_cache", "get_analytics_cache", "init_caches", "URLCache", "AnalyticsCache"]
