"""Repository for URL database operations."""
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.url import URL


class URLRepository:
    """Repository for URL database operations."""

    @staticmethod
    def create(db: Session, *, original_url: str, short_code: str) -> URL:
        """Create a new URL record."""
        url = URL(
            original_url=original_url,
            short_code=short_code,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        db.add(url)
        db.commit()
        db.refresh(url)
        return url

    @staticmethod
    def get_by_code(db: Session, short_code: str) -> Optional[URL]:
        """Get URL by short code."""
        return db.execute(
            select(URL).where(URL.short_code == short_code, URL.is_active == True)
        ).scalar_one_or_none()

    @staticmethod
    def get_by_original_url(db: Session, original_url: str) -> Optional[URL]:
        """Get URL by original URL."""
        return db.execute(
            select(URL).where(URL.original_url == original_url, URL.is_active == True)
        ).scalar_one_or_none()

    @staticmethod
    def exists_by_code(db: Session, short_code: str) -> bool:
        """Check if short code exists."""
        return db.execute(
            select(URL.short_code).where(URL.short_code == short_code)
        ).scalar_one_or_none() is not None
        
    @staticmethod
    def increment_fetch_count(db: Session, short_code: str) -> None:
        """Increment the fetch count for a URL."""
        url = db.execute(
            select(URL).where(URL.short_code == short_code, URL.is_active == True)
        ).scalar_one_or_none()
        if url:
            url.fetch_count += 1
            url.updated_at = datetime.now(UTC)
            db.commit()

url_repository = URLRepository()