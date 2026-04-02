"""Storage abstraction layer - supports MinIO (dev) and AWS S3/DO Spaces (prod)."""

from io import BytesIO
from abc import ABC, abstractmethod

import boto3
from botocore.exceptions import ClientError
from minio import Minio
from minio.error import S3Error

from app.core.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class StorageBackend(ABC):
    """Abstract storage backend."""

    @abstractmethod
    async def upload_file(
        self, file_name: str, file_data: BytesIO, file_size: int, **kwargs
    ) -> str:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, file_name: str) -> BytesIO:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, file_name: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def get_presigned_download_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned download URL."""
        pass

    @abstractmethod
    async def get_presigned_upload_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned upload URL."""
        pass

    @abstractmethod
    async def file_exists(self, file_name: str) -> bool:
        """Check if file exists."""
        pass


class MinIOStorage(StorageBackend):
    """MinIO S3-compatible object storage (development)."""

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
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
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
            logger.info(f"Uploaded to MinIO: {file_name}")
            return file_name
        except S3Error as e:
            logger.error(f"MinIO upload error: {e}")
            raise

    async def download_file(self, file_name: str) -> BytesIO:
        """Download file from MinIO."""
        try:
            response = self.client.get_object(self.bucket_name, file_name)
            file_data = BytesIO(response.read())
            file_data.seek(0)
            logger.info(f"Downloaded from MinIO: {file_name}")
            return file_data
        except S3Error as e:
            logger.error(f"MinIO download error: {e}")
            raise

    async def delete_file(self, file_name: str) -> bool:
        """Delete file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, file_name)
            logger.info(f"Deleted from MinIO: {file_name}")
            return True
        except S3Error as e:
            logger.error(f"MinIO delete error: {e}")
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
            logger.info(f"Generated MinIO presigned download URL")
            return url
        except S3Error as e:
            logger.error(f"MinIO presigned URL error: {e}")
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
            logger.info(f"Generated MinIO presigned upload URL")
            return url
        except S3Error as e:
            logger.error(f"MinIO presigned upload URL error: {e}")
            raise

    async def file_exists(self, file_name: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            self.client.stat_object(self.bucket_name, file_name)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            logger.error(f"MinIO file existence check error: {e}")
            raise


class S3Storage(StorageBackend):
    """AWS S3 and S3-compatible storage (production)."""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT,
            region_name=settings.AWS_S3_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET
        logger.info(f"Initialized S3 storage: {self.bucket}")

    async def upload_file(
        self,
        file_name: str,
        file_data: BytesIO,
        file_size: int,
        content_type: str = "application/octet-stream",
        metadata: dict = None,
    ) -> str:
        """Upload file to S3."""
        try:
            file_data.seek(0)
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_name,
                Body=file_data.getvalue(),
                ContentType=content_type,
                Metadata=metadata or {},
            )
            logger.info(f"Uploaded to S3: {file_name}")
            return file_name
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise

    async def download_file(self, file_name: str) -> BytesIO:
        """Download file from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=file_name)
            file_data = BytesIO(response["Body"].read())
            file_data.seek(0)
            logger.info(f"Downloaded from S3: {file_name}")
            return file_data
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise

    async def delete_file(self, file_name: str) -> bool:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=file_name)
            logger.info(f"Deleted from S3: {file_name}")
            return True
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            raise

    async def get_presigned_download_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned download URL."""
        try:
            expiration = expiration or settings.PRESIGNED_URL_EXPIRATION
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": file_name},
                ExpiresIn=expiration,
            )
            logger.info(f"Generated S3 presigned download URL")
            return url
        except ClientError as e:
            logger.error(f"S3 presigned URL error: {e}")
            raise

    async def get_presigned_upload_url(
        self, file_name: str, expiration: int = None
    ) -> str:
        """Generate presigned upload URL."""
        try:
            expiration = expiration or settings.PRESIGNED_URL_EXPIRATION
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket, "Key": file_name},
                ExpiresIn=expiration,
            )
            logger.info(f"Generated S3 presigned upload URL")
            return url
        except ClientError as e:
            logger.error(f"S3 presigned upload URL error: {e}")
            raise

    async def file_exists(self, file_name: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=file_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error(f"S3 file existence check error: {e}")
            raise


def get_storage_backend() -> StorageBackend:
    """Factory function to get storage backend based on config."""
    storage_type = getattr(settings, "STORAGE_TYPE", "minio").lower()

    if storage_type == "s3":
        return S3Storage()
    else:
        return MinIOStorage()


# Singleton instance
storage = get_storage_backend()
