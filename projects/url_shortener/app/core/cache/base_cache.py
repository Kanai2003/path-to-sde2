from abc import ABC, abstractmethod
import redis
from redis.exceptions import RedisError
from app.core.config import settings
from app.utils.logger import logger

class BaseCache(ABC):
    """Abstract base class for cache implementations."""

    def __init__(self, key_prefix: str=""):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """Generate a namespaced cache key."""
        return f"{self.key_prefix}:{key}" if self.key_prefix else key
    
    def is_available(self) -> bool:
        """Check if Redis is available."""
        try:
            self.redis_client.ping()
            return True
        except RedisError:
            return False
    
    def _handle_redis_error(self, error: RedisError, operation: str) -> None:
        """Log Redis errors with context."""
        logger.warning(f"Redis unavailable during {operation}: {error}")