import hashlib
import uuid
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import InvalidFileTypeError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_file_extension(filename: str) -> str:
    """Validate file extension against allowed list."""
    ext = Path(filename).suffix.lstrip(".").lower()
    if ext not in settings.allowed_extensions_list:
        raise InvalidFileTypeError(
            f"File type '.{ext}' not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    return ext


def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename preserving extension."""
    ext = Path(original_filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    logger.debug(f"Generated unique filename: {unique_name}")
    return unique_name


def calculate_file_hash(file_data: bytes) -> str:
    """Calculate SHA256 hash of file."""
    return hashlib.sha256(file_data).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"
