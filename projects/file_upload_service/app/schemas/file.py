from datetime import datetime

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """File metadata."""

    id: int
    original_filename: str
    stored_filename: str
    file_hash: str
    file_size: int
    content_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """File upload response."""

    id: int
    filename: str = Field(alias="original_filename")
    file_size: int
    file_hash: str
    content_type: str
    created_at: datetime
    message: str = "File uploaded successfully"

    class Config:
        from_attributes = True


class FileDownloadResponse(BaseModel):
    """File download metadata."""

    filename: str
    file_size: int
    content_type: str
    download_url: str


class PresignedURLResponse(BaseModel):
    """Presigned URL response."""

    url: str
    filename: str
    expires_in: int
    url_type: str = Field(description="Either 'download' or 'upload'")


class FileDeleteResponse(BaseModel):
    """File deletion response."""

    message: str
    filename: str


class FileListItem(BaseModel):
    """File list item."""

    id: int
    original_filename: str
    file_size: int
    content_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """File list response."""

    items: list[FileListItem]
    total: int
    page: int
    page_size: int
