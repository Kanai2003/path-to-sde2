"""Background job scheduler for analytics sync."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import AsyncSessionLocal
from app.services.analytics_sync_service import get_analytics_sync_service
from app.utils.logger import logger


class AnalyticsScheduler:
    """Scheduler for periodic analytics sync jobs."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_started = False

    def start(self) -> None:
        """Start the analytics scheduler."""
        if self._is_started:
            return

        # Add analytics sync job - runs every 5 minutes
        self.scheduler.add_job(
            self._sync_analytics_job,
            trigger=IntervalTrigger(minutes=5),
            id="analytics_sync",
            name="Analytics Sync Job",
            max_instances=1,  # Only one instance at a time
            replace_existing=True,
        )

        self.scheduler.start()
        self._is_started = True
        logger.info("Analytics scheduler started - sync every 5 minutes")

    def stop(self) -> None:
        """Stop the analytics scheduler."""
        if self._is_started:
            self.scheduler.shutdown(wait=True)
            self._is_started = False
            logger.info("Analytics scheduler stopped")

    def is_running(self) -> bool:
        """Check if the scheduler is running."""
        return self._is_started

    async def _sync_analytics_job(self) -> None:
        """Background job to sync analytics data."""
        try:
            # Get async database session
            async with AsyncSessionLocal() as db:
                # Create sync service and run sync
                sync_service = get_analytics_sync_service(db)
                stats = await sync_service.sync_analytics()
                logger.info(f"Periodic analytics sync: {stats}")

        except Exception as e:
            logger.error(f"Analytics sync job failed: {e}")


# Global scheduler instance
analytics_scheduler = AnalyticsScheduler()
