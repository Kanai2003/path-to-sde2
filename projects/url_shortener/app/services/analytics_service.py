"""Service for analytics operations using Redis cache."""

from typing import Dict

from sqlalchemy.orm import Session

from app.core.cache.analytics_cache import analytics_cache
from app.repositories.url_repository import url_repository


class AnalyticsService:
    """Service for handling URL analytics with Redis caching."""

    def __init__(self, db: Session):
        self.db = db
        self.cache = analytics_cache
        self.repo = url_repository

    def record_click(self, short_code: str) -> None:
        """
        Record a click for the given short code in Redis.
        This is called on every redirect for real-time analytics.

        Args:
            short_code: The short code that was accessed
        """
        self.cache.increment_click_count(short_code)

    def get_click_count(self, short_code: str) -> int:
        """
        Get the current click count for a short code.
        Returns Redis count + DB count for accuracy.

        Args:
            short_code: The short code to get count for

        Returns:
            Total click count (Redis + DB)
        """
        redis_count = self.cache.get_click_count(short_code)

        # Also get DB count for complete picture
        url_entity = self.repo.get_by_code(self.db, short_code)
        db_count = url_entity.fetch_count if url_entity else 0

        return redis_count + db_count

    def get_all_click_counts(self) -> Dict[str, int]:
        """
        Get all click counts from Redis.
        Used for periodic sync operations.

        Returns:
            Dictionary of short_code -> click_count
        """
        return self.cache.get_all_clicks()

    def sync_clicks_to_database(self) -> int:
        """
        Sync Redis click counts to database and reset Redis counters.
        This should be called periodically (e.g., every 3 minutes).

        Returns:
            Number of URLs updated
        """
        click_data = self.get_all_click_counts()
        updated_count = 0

        if not click_data:
            return 0

        try:
            # Bulk update database
            for short_code, click_count in click_data.items():
                if click_count > 0:
                    self.repo.increment_fetch_count_by(self.db, short_code, click_count)
                    updated_count += 1

            # Reset Redis counters after successful sync
            short_codes_to_reset = list(click_data.keys())
            self.cache.reset_clicks(short_codes_to_reset)

            # Commit all changes
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise e

        return updated_count


def get_analytics_service(db: Session) -> AnalyticsService:
    """Dependency injection helper."""
    return AnalyticsService(db)
