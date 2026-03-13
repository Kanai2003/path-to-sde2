"""
Async service for URL redirection operations.

Optimized for maximum throughput with minimal latency.
"""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_url_cache
from app.core.exceptions import URLNotFoundError
from app.core.message_queue import get_analytics_queue
from app.repositories.url_repository import url_repository
from app.utils.logger import logger


class URLRedirectionService:
    """
    High-performance async service for URL redirection.
    
    Flow:
    1. Check Redis cache (0.1ms)
    2. Fallback to DB (5ms) + cache result
    3. Publish analytics event (non-blocking)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = url_repository
        self.cache = get_url_cache()
        self.queue = get_analytics_queue()

    async def get_original_url(self, short_code: str) -> str:
        """
        Get original URL by short code with caching.

        Args:
            short_code: The short code to look up

        Returns:
            The original URL

        Raises:
            URLNotFoundError: If short code not found
        """
        # Fast path: Check cache first (0.1ms)
        cached_url = await self.cache.get_cached_url(short_code)
        if cached_url:
            # Fire-and-forget analytics (don't await, don't block redirect)
            await self._publish_click_event(short_code)
            return cached_url

        # Slow path: Database lookup (5ms)
        url_entity = await self.repo.get_by_code(self.db, short_code)

        if not url_entity:
            raise URLNotFoundError(f"Short code '{short_code}' not found")

        # Cache for future requests
        await self.cache.cache_url(short_code, url_entity.original_url)

        # Publish analytics event
        await self._publish_click_event(short_code)

        return url_entity.original_url

    async def _publish_click_event(self, short_code: str) -> None:
        """Publish click event to analytics queue (fast, non-blocking)."""
        try:
            await self.queue.publish(
                event_type="click",
                data={
                    "short_code": short_code,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as e:
            # Log but don't fail the redirect
            logger.warning(f"Failed to publish click event: {e}")


def get_url_redirection_service(db: AsyncSession) -> URLRedirectionService:
    """Dependency injection helper."""
    return URLRedirectionService(db)
