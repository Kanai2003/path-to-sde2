"""
Async analytics cache for real-time click tracking.

Uses Redis Hash for O(1) increment operations.
"""

from typing import Dict, List

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.cache.base_cache import BaseCache


class AnalyticsCache(BaseCache):
    """Async cache for analytics data using Redis Hash."""

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client, key_prefix="URL_ANALYTICS")
        self.CLICK_KEY = self._make_key("click_counts")

    async def increment_click_count(self, short_code: str) -> None:
        """
        Increment the click count for a given short code.
        Uses HINCRBY which is atomic and O(1).

        Args:
            short_code: The short code for which to increment the click count.
        """
        try:
            await self.redis.hincrby(self.CLICK_KEY, short_code, 1)
        except RedisError as e:
            self._handle_redis_error(e, "increment_click_count")

    async def get_click_count(self, short_code: str) -> int:
        """
        Get the click count for a given short code.

        Args:
            short_code: The short code for which to retrieve the click count.
        """
        try:
            count = await self.redis.hget(self.CLICK_KEY, short_code)
            return int(count) if count else 0
        except RedisError as e:
            self._handle_redis_error(e, "get_click_count")
            return 0

    async def get_all_clicks(self) -> Dict[str, int]:
        """Get all click counts for all short codes."""
        try:
            click_data = await self.redis.hgetall(self.CLICK_KEY)
            return {short_code: int(count) for short_code, count in click_data.items()}
        except RedisError as e:
            self._handle_redis_error(e, "get_all_clicks")
            return {}

    async def reset_clicks(self, short_codes: List[str]) -> None:
        """
        Reset the click count for given short codes to zero.

        Args:
            short_codes: The list of short codes for which to reset the click count.
        """
        try:
            if short_codes:
                await self.redis.hdel(self.CLICK_KEY, *short_codes)
        except RedisError as e:
            self._handle_redis_error(e, "reset_clicks")


# Note: Singleton is now created lazily after Redis pools are initialized
# Use get_analytics_cache() from cache/__init__.py instead
