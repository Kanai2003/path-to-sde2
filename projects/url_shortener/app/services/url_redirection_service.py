"""Service for URL redirection operations."""

from datetime import datetime

from app.utils import logger
from sqlalchemy.orm import Session

from app.core.cache.url_cache import url_cache
from app.core.exceptions import URLNotFoundError
from app.repositories.url_repository import url_repository
from app.services.analytics_service import get_analytics_service
from app.core.message_queue.message_queue import analytics_queue


class URLRedirectionService:
    """Optimized service for URL redirection - minimal logic for speed."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = url_repository
        self.analytics = get_analytics_service(db)

    def get_original_url(self, short_code: str) -> str:
        """
        Get original URL by short code.

        Args:
            short_code: The short code to look up

        Returns:
            The original URL

        Raises:
            URLNotFoundError: If short code not found
        """
        # check cache first for faster retrieval
        cached_url = url_cache.get_cached_url(short_code)
        if cached_url:
            if not analytics_queue.publish("click", {"short_code": short_code}):
                # Queue failed - fallback to direct increment
                logger.warning("Queue unavailable, using sync analytics")
                self.analytics.record_click(short_code)
            return cached_url

        # fallback to database lookup if not in cache
        url_entity = self.repo.get_by_code(self.db, short_code)

        if not url_entity:
            raise URLNotFoundError(f"Short code '{short_code}' not found")

        # cache the result for future requests
        url_cache.cache_url(short_code, url_entity.original_url)


        if not analytics_queue.publish("click", {"short_code": short_code}):
                # Queue failed - fallback to direct increment
                logger.warning("Queue unavailable, using sync analytics")
                self.analytics.record_click(short_code)

        return url_entity.original_url


def get_url_redirection_service(db: Session) -> URLRedirectionService:
    """Dependency injection helper."""
    return URLRedirectionService(db)
