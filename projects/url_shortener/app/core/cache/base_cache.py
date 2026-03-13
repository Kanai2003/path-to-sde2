"""
Async base cache implementation with Redis connection pooling.

All cache operations are now non-blocking for high concurrency.
"""

from abc import ABC
from typing import Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.utils.logger import logger


class BaseCache(ABC):
    """Abstract base class for async cache implementations."""

    def __init__(self, redis_client: Redis, key_prefix: str = ""):
        """
        Initialize cache with a pooled Redis client.
        
        Args:
            redis_client: Async Redis client from connection pool
            key_prefix: Prefix for all keys (namespacing)
        """
        self.redis = redis_client
        self.key_prefix = key_prefix

    def _make_key(self, key: str) -> str:
        """Generate a namespaced cache key."""
        return f"{self.key_prefix}:{key}" if self.key_prefix else key

    async def is_available(self) -> bool:
        """Check if Redis is available."""
        try:
            await self.redis.ping()
            return True
        except RedisError:
            return False

    def _handle_redis_error(self, error: RedisError, operation: str) -> None:
        """Log Redis errors with context."""
        logger.warning(f"Redis unavailable during {operation}: {error}")
