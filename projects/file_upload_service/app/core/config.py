from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API
    API_TITLE: str = "File Upload Service"
    API_VERSION: str = "v1"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str = "uploads"
    MINIO_USE_SSL: bool = False

    # ClamAV
    CLAMAV_HOST: str = "localhost"
    CLAMAV_PORT: int = 3310
    ENABLE_VIRUS_SCAN: bool = True

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Upload Limits
    MAX_FILE_SIZE: int = 104857600  # 100MB
    ALLOWED_EXTENSIONS: str = "pdf,jpg,jpeg,png,txt,doc,docx,xls,xlsx,zip"

    # Presigned URL
    PRESIGNED_URL_EXPIRATION: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions."""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    # Storage Backend (minio for dev, s3 for prod)
    STORAGE_TYPE: str = "minio"  # minio or s3

    # AWS S3 / Digital Ocean Spaces
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = ""
    AWS_S3_REGION: str = "us-east-1"
    AWS_S3_ENDPOINT: str = "https://s3.amazonaws.com"

    # VirusTotal API (alternative to ClamAV)
    VIRUSOTAL_API_KEY: str = ""


settings = Settings()
