from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.db.session import get_db
from app.schemas.file import (
    FileDeleteResponse,
    FileDownloadResponse,
    FileListResponse,
    FileUploadResponse,
    PresignedURLResponse,
)
from app.services.file_service import FileService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: str = Query(None),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file with virus scanning."""
    try:
        file_service = FileService(db)
        file_data = await file.read()

        from io import BytesIO

        file_bytes = BytesIO(file_data)

        result = await file_service.upload_file(
            file_bytes,
            file.filename,
            user_id,
            file.content_type or "application/octet-stream",
            description,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/list", response_model=FileListResponse)
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List user files with pagination."""
    try:
        file_service = FileService(db)
        result = await file_service.list_files(user_id, skip, limit)
        return result
    except Exception as e:
        logger.error(f"List files failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list files")


@router.get("/{file_id}", response_model=FileDownloadResponse)
async def get_file_metadata(
    file_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get file metadata."""
    try:
        file_service = FileService(db)
        metadata = await file_service.get_file_metadata(file_id, user_id)

        presigned_url = await file_service.get_presigned_download_url(file_id, user_id)

        return FileDownloadResponse(
            filename=metadata["filename"],
            file_size=metadata["file_size"],
            content_type=metadata["content_type"],
            download_url=presigned_url,
        )
    except Exception as e:
        logger.error(f"Get metadata failed: {str(e)}")
        raise HTTPException(status_code=404, detail="File not found")


@router.delete("/{file_id}", response_model=FileDeleteResponse)
async def delete_file(
    file_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a file."""
    try:
        file_service = FileService(db)
        metadata = await file_service.get_file_metadata(file_id, user_id)
        await file_service.delete_file(file_id, user_id)

        return FileDeleteResponse(
            message="File deleted successfully",
            filename=metadata["filename"],
        )
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}")
        raise HTTPException(status_code=404, detail="File not found")


@router.post("/presigned-download/{file_id}", response_model=PresignedURLResponse)
async def get_presigned_download_url(
    file_id: int,
    expires_in: int = Query(3600, ge=60, le=604800),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate presigned download URL."""
    try:
        file_service = FileService(db)
        metadata = await file_service.get_file_metadata(file_id, user_id)
        url = await file_service.get_presigned_download_url(
            file_id, user_id, expires_in
        )

        return PresignedURLResponse(
            url=url,
            filename=metadata["filename"],
            expires_in=expires_in,
            url_type="download",
        )
    except Exception as e:
        logger.error(f"Presigned URL generation failed: {str(e)}")
        raise HTTPException(status_code=404, detail="File not found")
