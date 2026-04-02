from enum import Enum


class ErrorCode(str, Enum):
    """Standardized error codes."""

    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    VIRUS_DETECTED = "VIRUS_DETECTED"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    UNAUTHORIZED = "UNAUTHORIZED"
    DATABASE_ERROR = "DATABASE_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"


class APIException(Exception):
    """Custom API exception."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: ErrorCode,
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code.value


class FileNotFoundError(APIException):
    def __init__(self, detail: str = "File not found"):
        super().__init__(404, detail, ErrorCode.FILE_NOT_FOUND)


class InvalidFileTypeError(APIException):
    def __init__(self, detail: str = "Invalid file type"):
        super().__init__(400, detail, ErrorCode.INVALID_FILE_TYPE)


class FileTooLargeError(APIException):
    def __init__(self, detail: str = "File too large"):
        super().__init__(413, detail, ErrorCode.FILE_TOO_LARGE)


class VirusDetectedError(APIException):
    def __init__(self, detail: str = "Virus detected in file"):
        super().__init__(400, detail, ErrorCode.VIRUS_DETECTED)


class UploadFailedError(APIException):
    def __init__(self, detail: str = "Upload failed"):
        super().__init__(500, detail, ErrorCode.UPLOAD_FAILED)


class DownloadFailedError(APIException):
    def __init__(self, detail: str = "Download failed"):
        super().__init__(500, detail, ErrorCode.DOWNLOAD_FAILED)


class UnauthorizedError(APIException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(401, detail, ErrorCode.UNAUTHORIZED)
