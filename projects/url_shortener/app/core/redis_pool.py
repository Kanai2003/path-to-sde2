"""
Async Redis connection pool singleton for high-performance caching.

Why a singleton pool?
- Connection reuse: Creating TCP connections is expensive (~10ms each)
- Backpressure: Pool limits prevent overwhelming Redis
- Resource management: Centralized cleanup on shutdown
"""

from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings
from app.utils.logger import logger


class RedisPoolManager:
    """
    Manages async Redis connection pools for different use cases.
    
    Pools:
    - cache_pool: URL caching (db 0)
    - analytics_pool: Analytics counters (db 1)
    - queue_pool: Message queue (db 2)
    """

    _instance: Optional["RedisPoolManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "RedisPoolManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._cache_pool: Optional[ConnectionPool] = None
        self._analytics_pool: Optional[ConnectionPool] = None
        self._queue_pool: Optional[ConnectionPool] = None
        self._initialized = True

    async def init_pools(self) -> None:
        """Initialize all connection pools. Call on app startup."""
        pool_kwargs = {
            "max_connections": settings.REDIS_MAX_CONNECTIONS,
            "decode_responses": True,
            "socket_connect_timeout": 2,
            "socket_timeout": 2,
            "retry_on_timeout": True,
        }

        self._cache_pool = ConnectionPool.from_url(
            f"{settings.REDIS_URL}/{settings.REDIS_DB_CACHE}",
            **pool_kwargs,
        )
        
        self._analytics_pool = ConnectionPool.from_url(
            f"{settings.REDIS_URL}/{settings.REDIS_DB_ANALYTICS}",
            **pool_kwargs,
        )
        
        self._queue_pool = ConnectionPool.from_url(
            f"{settings.REDIS_URL}/{settings.REDIS_DB_QUEUE}",
            **pool_kwargs,
        )
        
        logger.info("Redis connection pools initialized")

    async def close_pools(self) -> None:
        """Close all connection pools. Call on app shutdown."""
        pools = [self._cache_pool, self._analytics_pool, self._queue_pool]
        for pool in pools:
            if pool:
                await pool.disconnect()
        logger.info("Redis connection pools closed")

    def get_cache_client(self) -> Redis:
        """Get Redis client for URL caching."""
        if not self._cache_pool:
            raise RuntimeError("Redis pools not initialized. Call init_pools() first.")
        return Redis(connection_pool=self._cache_pool)

    def get_analytics_client(self) -> Redis:
        """Get Redis client for analytics."""
        if not self._analytics_pool:
            raise RuntimeError("Redis pools not initialized. Call init_pools() first.")
        return Redis(connection_pool=self._analytics_pool)

    def get_queue_client(self) -> Redis:
        """Get Redis client for message queue."""
        if not self._queue_pool:
            raise RuntimeError("Redis pools not initialized. Call init_pools() first.")
        return Redis(connection_pool=self._queue_pool)


# Singleton instance
redis_pool_manager = RedisPoolManager()


# Convenience functions
def get_cache_redis() -> Redis:
    """Get async Redis client for caching."""
    return redis_pool_manager.get_cache_client()


def get_analytics_redis() -> Redis:
    """Get async Redis client for analytics."""
    return redis_pool_manager.get_analytics_client()


def get_queue_redis() -> Redis:
    """Get async Redis client for message queue."""
    return redis_pool_manager.get_queue_client()
