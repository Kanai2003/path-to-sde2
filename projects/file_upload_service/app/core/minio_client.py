from io import BytesIO

from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class MinIOClient:
    """MinIO S3-compatible object storage client."""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure bucket exists, create if not."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created bucket: {self.bucket_name}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket: {e}")
            raise

    async def upload_file(
        self,
        file_name: str,
        file_data: BytesIO,
        file_size: int,
        content_type: str = "application/octet-stream",
        metadata: dict = None,
    ) -> str:
        """Upload file to MinIO."""
        try:
            file_data.seek(0)
            self.client.put_object(
                self.bucket_name,
                file_name,
                file_data,
                file_size,
                content_type=content_type,
                metadata=metadata or {},
            )
            logger.info(f"Uploaded file: {file_name}")
            return file_name
        except S3Error as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def download_file(self, file_name: str) -> BytesIO:
        """Download file from MinIO."""
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            file_data = BytesIO(response.read())
            file_data.seek(0)
            logger.info(f"Downloaded file: {file_name}")
            return file_data
        except S3Error as e:
            logger.error(f"Error downloading file: {e}")
            raise

    async def delete_file(self, file_name: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"Deleted file: {file_name}")
            return True
        except S3Error as e:
            logger.error(f"Error deleting file: {e}")
            raise

    async def get_presigned_download_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned download URL."""
        try:
            expiration = expiration or settings.PRESIGNED_URL_EXPIRATION
            url = self.client.get_presigned_download_url(
                self.bucket_name, file_name, expires=expiration
            )
            logger.info(f"Generated presigned download URL for: {file_name}")
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise

    async def get_presigned_upload_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned upload URL."""
        try:
            expiration = expiration or settings.PRESIGNED_URL_EXPIRATION
            url = self.client.get_presigned_upload_url(
                self.bucket_name, file_name, expires=expiration
            )
            logger.info(f"Generated presigned upload URL for: {file_name}")
            return url
        except S3Error as e:
            logger.error(f"Error generating presigned upload URL: {e}")
            raise

    async def file_exists(self, file_name: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            self.client.stat_object(self.bucket_name, file_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"Error checking file existence: {e}")
            raise


# Singleton instance
minio_client = MinIOClient()
