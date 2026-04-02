from io import BytesIO

import pyclamd

from app.core.config import settings
from app.core.exceptions import VirusDetectedError
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VirusScanner:
    """ClamAV virus scanner integration."""

    def __init__(self):
        try:
            self.clam = pyclamd.ClamD(
                host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT
            )
            if not self.clam.ping():
                logger.warning("ClamAV server is not responding")
        except Exception as e:
            logger.warning(f"Failed to initialize ClamAV: {e}")
            self.clam = None

    async def scan_file(self, file_data: BytesIO) -> dict:
        """Scan file for viruses."""
        if not settings.ENABLE_VIRUS_SCAN:
            logger.debug("Virus scanning is disabled")
            return {"safe": True}

        if not self.clam:
            logger.warning("ClamAV is not available, skipping scan")
            return {"safe": True}

        try:
            file_data.seek(0)
            result = self.clam.scan_stream(file_data.read())

            if result is not None:
                logger.warning(f"Virus detected: {result}")
                raise VirusDetectedError(f"Virus detected: {result}")

            logger.info("File scan completed: safe")
            return {"safe": True}

        except Exception as e:
            if isinstance(e, VirusDetectedError):
                raise
            logger.error(f"Error scanning file: {e}")
            return {"safe": False, "error": str(e)}


# Singleton instance
virus_scanner = VirusScanner()
