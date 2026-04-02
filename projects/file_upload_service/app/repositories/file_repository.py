from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileRepository:
    """File repository for database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> File:
        """Create new file record."""
        file_obj = File(**kwargs)
        self.db.add(file_obj)
        await self.db.commit()
        await self.db.refresh(file_obj)
        logger.info(f"Created file record: {file_obj.id}")
        return file_obj

    async def get_by_id(self, file_id: int) -> File | None:
        """Get file by ID."""
        result = await self.db.execute(
            select(File).where(File.id == file_id, File.is_deleted == 0)
        )
        return result.scalar_one_or_none()

    async def get_by_stored_filename(self, filename: str) -> File | None:
        """Get file by stored filename."""
        result = await self.db.execute(
            select(File).where(
                File.stored_filename == filename, File.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: str, skip: int = 0, limit: int = 10
    ) -> tuple[list[File], int]:
        """List files by user."""
        query = select(File).where(
            File.user_id == user_id, File.is_deleted == 0
        )

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(File).where(
                File.user_id == user_id, File.is_deleted == 0
            )
        )
        total = count_result.scalar()

        # Get paginated results
        result = await self.db.execute(
            query.order_by(desc(File.created_at)).offset(skip).limit(limit)
        )
        files = result.scalars().all()
        return files, total

    async def update(self, file_id: int, **kwargs) -> File | None:
        """Update file record."""
        file_obj = await self.get_by_id(file_id)
        if not file_obj:
            return None

        for key, value in kwargs.items():
            setattr(file_obj, key, value)

        await self.db.commit()
        await self.db.refresh(file_obj)
        logger.info(f"Updated file record: {file_id}")
        return file_obj

    async def soft_delete(self, file_id: int) -> bool:
        """Soft delete file record."""
        file_obj = await self.get_by_id(file_id)
        if not file_obj:
            return False

        file_obj.is_deleted = 1
        await self.db.commit()
        logger.info(f"Soft deleted file: {file_id}")
        return True

    async def get_by_hash(self, file_hash: str, user_id: str) -> File | None:
        """Get file by hash for deduplication."""
        result = await self.db.execute(
            select(File).where(
                File.file_hash == file_hash,
                File.user_id == user_id,
                File.is_deleted == 0,
            )
        )
        return result.scalar_one_or_none()
