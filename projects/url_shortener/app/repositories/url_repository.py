"""
Async repository for URL database operations.

All database operations are now non-blocking for high concurrency.
"""

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL, Url


class URLRepository:
    """Async repository for URL database operations."""

    @staticmethod
    async def create(db: AsyncSession, *, original_url: str, short_code: str) -> Url:
        """Create a new URL record."""
        url = URL(
            original_url=original_url,
            short_code=short_code,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        db.add(url)
        await db.commit()
        await db.refresh(url)
        return url

    @staticmethod
    async def get_by_code(db: AsyncSession, short_code: str) -> Url | None:
        """Get URL by short code."""
        result = await db.execute(
            select(URL).where(URL.short_code == short_code, URL.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_original_url(db: AsyncSession, original_url: str) -> Url | None:
        """Get URL by original URL."""
        result = await db.execute(
            select(URL).where(URL.original_url == original_url, URL.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def exists_by_code(db: AsyncSession, short_code: str) -> bool:
        """Check if short code exists."""
        result = await db.execute(
            select(URL.short_code).where(URL.short_code == short_code)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def increment_fetch_count_by(
        db: AsyncSession, short_code: str, count: int
    ) -> None:
        """
        Increment the fetch count for a URL by a specific amount.
        Uses atomic UPDATE for safety under concurrent access.
        """
        await db.execute(
            update(URL)
            .where(URL.short_code == short_code, URL.is_active.is_(True))
            .values(
                fetch_count=URL.fetch_count + count,
                updated_at=datetime.now(UTC),
            )
        )
        # Note: Commit handled by caller for transaction control


url_repository = URLRepository()
