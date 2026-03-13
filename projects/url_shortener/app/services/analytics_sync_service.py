"""
Async service for syncing analytics data from Redis to database.
"""

from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_analytics_cache
from app.services.analytics_service import get_analytics_service
from app.utils.logger import logger


class AnalyticsSyncService:
    """Async service for periodic syncing of analytics data to database."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = get_analytics_service(db)
        self.cache = get_analytics_cache()

    async def sync_analytics(self) -> Dict[str, int]:
        """
        Sync all pending analytics data from Redis to database.

        Returns:
            Dict with sync statistics:
            - 'urls_updated': Number of URLs that had their counts updated
            - 'total_clicks_synced': Total number of clicks synced
            - 'errors': Number of errors encountered
        """
        stats = {"urls_updated": 0, "total_clicks_synced": 0, "errors": 0}

        try:
            # Get all click data from Redis
            click_data = await self.cache.get_all_clicks()

            if not click_data:
                logger.info("No analytics data to sync")
                return stats

            logger.info(f"Syncing analytics for {len(click_data)} URLs")

            # Sync to database
            urls_updated = await self.analytics_service.sync_clicks_to_database()

            # Calculate total clicks synced
            total_clicks = sum(click_data.values())

            stats["urls_updated"] = urls_updated
            stats["total_clicks_synced"] = total_clicks

            logger.info(
                f"Analytics sync completed: {urls_updated} URLs updated, {total_clicks} clicks synced"
            )

        except Exception as e:
            logger.error(f"Analytics sync failed: {e}")
            stats["errors"] = 1
            # Don't re-raise - we want the sync to be resilient

        return stats

    async def get_sync_status(self) -> Dict[str, int]:
        """
        Get current sync status - how many clicks are pending sync.

        Returns:
            Dict with pending sync information
        """
        try:
            click_data = await self.cache.get_all_clicks()
            total_pending_clicks = sum(click_data.values())

            return {
                "urls_with_pending_clicks": len(click_data),
                "total_pending_clicks": total_pending_clicks,
            }
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            return {"urls_with_pending_clicks": 0, "total_pending_clicks": 0}


def get_analytics_sync_service(db: AsyncSession) -> AnalyticsSyncService:
    """Dependency injection helper."""
    return AnalyticsSyncService(db)
