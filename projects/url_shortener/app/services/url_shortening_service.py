"""
Async service for URL shortening operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_url_cache
from app.core.exceptions import ShortCodeGenerationError
from app.models.url import URL
from app.repositories.url_repository import url_repository
from app.utils.logger import logger
from app.utils.shortener import generate_short_code


class URLShorteningService:
    """Async service for URL shortening operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = url_repository
        self.cache = get_url_cache()

    async def create_short_url(self, original_url: str, user_id: str | None = None) -> URL:
        """
        Create a shortened URL.

        Args:
            original_url: The original URL to shorten

        Returns:
            URL model with generated short_code

        Raises:
            ShortCodeGenerationError: If unable to generate unique code
        """
        # Check if URL already exists (idempotency)
        # existing = await self.repo.get_by_original_url(self.db, original_url)
        # if existing:
        #     return existing

        # Generate unique short code with collision handling
        short_code = await self._generate_unique_code(original_url)

        # Create URL record in database
        created_url = await self.repo.create(
            self.db,
            original_url=original_url,
            short_code=short_code,
            user_id=user_id,
        )

        # Cache the mapping for faster future lookups
        await self.cache.cache_url(short_code, original_url)

        return created_url

    async def _generate_unique_code(self, original_url: str, max_attempts: int = 5) -> str:
        """Generate a unique short code, handling collisions."""
        for attempt in range(max_attempts):
            code = generate_short_code(original_url, salt=attempt)
            if not await self.repo.exists_by_code(self.db, code):
                return code
        logger.error(
            f"Short Code generation failed for URL: {original_url} after {max_attempts} attempts"
        )
        raise ShortCodeGenerationError(
            f"Failed to generate unique code after {max_attempts} attempts"
        )


def get_url_shortening_service(db: AsyncSession) -> URLShorteningService:
    """Dependency injection helper."""
    return URLShorteningService(db)
