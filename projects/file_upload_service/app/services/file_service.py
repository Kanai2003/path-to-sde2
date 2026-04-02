from io import BytesIO

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import FileTooLargeError, FileNotFoundError
from app.core.storage import storage
from app.core.virus_scanner import virus_scanner
from app.repositories.file_repository import FileRepository
from app.utils.file_utils import (
    calculate_file_hash,
    generate_unique_filename,
    validate_file_extension,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileService:
    """File upload/download service."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FileRepository(db)

    async def upload_file(
        self,
        file_data: BytesIO,
        filename: str,
        user_id: str,
        content_type: str,
        description: str = None,
    ) -> dict:
        """Upload file with virus scanning and metadata storage."""

        # Get file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Seek back to start

        # Validate file size
        if file_size > settings.MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File size {file_size} exceeds maximum {settings.MAX_FILE_SIZE}"
            )

        # Validate extension
        validate_file_extension(filename)

        # Calculate hash for deduplication
        file_bytes = file_data.read()
        file_hash = calculate_file_hash(file_bytes)
        file_data = BytesIO(file_bytes)

        # Check if file already exists (deduplication)
        existing = await self.repo.get_by_hash(file_hash, user_id)
        if existing:
            logger.info(f"File already exists (hash: {file_hash})")
            return {
                "id": existing.id,
                "filename": existing.original_filename,
                "file_size": existing.file_size,
                "file_hash": existing.file_hash,
                "content_type": existing.content_type,
                "created_at": existing.created_at,
                "message": "File already exists (deduplicated)",
            }

        # Scan file for viruses
        scan_result = await virus_scanner.scan_file(file_data)
        logger.info(f"Virus scan result: {scan_result}")

        # Upload to storage backend (MinIO/S3)
        unique_filename = generate_unique_filename(filename)
        await storage.upload_file(
            unique_filename,
            file_data,
            file_size,
            content_type=content_type,
            metadata={
                "original-filename": filename,
                "user-id": user_id,
                "file-hash": file_hash,
            },
        )

        # Create database record
        file_record = await self.repo.create(
            original_filename=filename,
            stored_filename=unique_filename,
            file_hash=file_hash,
            file_size=file_size,
            content_type=content_type,
            user_id=user_id,
            description=description,
        )

        logger.info(f"File uploaded successfully: {filename}")
        return {
            "id": file_record.id,
            "filename": file_record.original_filename,
            "file_size": file_record.file_size,
            "file_hash": file_record.file_hash,
            "content_type": file_record.content_type,
            "created_at": file_record.created_at,
            "message": "File uploaded successfully",
        }

    async def download_file(self, file_id: int, user_id: str) -> tuple[BytesIO, str]:
        """Download file by ID."""
        file_record = await self.repo.get_by_id(file_id)

        if not file_record:
            raise FileNotFoundError("File not found")

        if file_record.user_id != user_id:
            raise FileNotFoundError("File not found")

        # Download from storage backend
        file_data = await storage.download_file(file_record.stored_filename)
        logger.info(f"File downloaded: {file_record.original_filename}")

        return file_data, file_record.original_filename

    async def delete_file(self, file_id: int, user_id: str) -> bool:
        """Delete file (soft delete)."""
        file_record = await self.repo.get_by_id(file_id)

        if not file_record:
            raise FileNotFoundError("File not found")

        if file_record.user_id != user_id:
            raise FileNotFoundError("File not found")

        # Soft delete from database
        await self.repo.soft_delete(file_id)

        # Delete from storage backend
        await storage.delete_file(file_record.stored_filename)

        logger.info(f"File deleted: {file_record.original_filename}")
        return True

    async def get_file_metadata(self, file_id: int, user_id: str) -> dict:
        """Get file metadata."""
        file_record = await self.repo.get_by_id(file_id)

        if not file_record:
            raise FileNotFoundError("File not found")

        if file_record.user_id != user_id:
            raise FileNotFoundError("File not found")

        return {
            "id": file_record.id,
            "filename": file_record.original_filename,
            "file_size": file_record.file_size,
            "content_type": file_record.content_type,
            "file_hash": file_record.file_hash,
            "created_at": file_record.created_at,
            "updated_at": file_record.updated_at,
        }

    async def list_files(
        self, user_id: str, skip: int = 0, limit: int = 10
    ) -> dict:
        """List user files with pagination."""
        files, total = await self.repo.list_by_user(user_id, skip, limit)

        return {
            "items": [
                {
                    "id": f.id,
                    "original_filename": f.original_filename,
                    "file_size": f.file_size,
                    "content_type": f.content_type,
                    "created_at": f.created_at,
                }
                for f in files
            ],
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
        }

    async def get_presigned_download_url(
        self, file_id: int, user_id: str, expiration: int = None
    ) -> str:
        """Generate presigned download URL."""
        file_record = await self.repo.get_by_id(file_id)

        if not file_record:
            raise FileNotFoundError("File not found")

        if file_record.user_id != user_id:
            raise FileNotFoundError("File not found")

        url = await storage.get_presigned_download_url(
            file_record.stored_filename, expiration
        )
        return url

    async def get_presigned_upload_url(
        self, filename: str, expiration: int = None
    ) -> str:
        """Generate presigned upload URL."""
        unique_filename = generate_unique_filename(filename)
        validate_file_extension(filename)

        url = await storage.get_presigned_upload_url(
            unique_filename, expiration
        )
        return url
