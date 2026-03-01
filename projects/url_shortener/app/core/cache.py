"""Redis cache client and helper functions."""

import redis
from redis.exceptions import RedisError
from app.core.config import settings
from app.utils.logger import logger

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,  # Automatically decode bytes to strings
    socket_connect_timeout=1,  # Fast timeout for connection attempts
    socket_timeout=1,
)

# Key prefix to namespace our cache
KEY_PREFIX = "URL_SHORTENER:"


def is_redis_available() -> bool:
    """Check if Redis is available."""
    try:
        redis_client.ping()
        return True
    except RedisError:
        return False


def get_url_cache_key(short_code: str) -> str:
    """Generate a cache key for a given short code."""
    return f"{KEY_PREFIX}{short_code}"


def cache_url(short_code: str, original_url: str, ttl: int = 3600) -> None:
    """
    Cache the original URL with the short code as key.
    Fails silently if Redis is unavailable (fail-open pattern).
    
    Args:
        short_code: The short code to use as cache key.
        original_url: The original URL to cache.
        ttl: Time to live for the cache entry in seconds (default: 1 hour).
    """
    try:
        key = get_url_cache_key(short_code)
        redis_client.set(key, original_url, ex=ttl)
    except RedisError as e:
        logger.warning(f"Redis unavailable, skipping cache write: {e}")


def get_cached_url(short_code: str) -> str | None:
    """
    Get cached original url for a given short code.
    Returns None if Redis is unavailable (fail-open pattern).
    
    Args:
        short_code: The short code to look up in cache.
    """
    try:
        key = get_url_cache_key(short_code)
        return redis_client.get(key)
    except RedisError as e:
        logger.warning(f"Redis unavailable, cache miss: {e}")
        return None


def invalidate_cache(short_code: str) -> None:
    """
    Invalidate the cache entry for a given short code.
    Fails silently if Redis is unavailable.
    
    Args:
        short_code: The short code whose cache entry should be invalidated.
    """
    try:
        key = get_url_cache_key(short_code)
        redis_client.delete(key)
    except RedisError as e:
        logger.warning(f"Redis unavailable, skipping cache invalidation: {e}")