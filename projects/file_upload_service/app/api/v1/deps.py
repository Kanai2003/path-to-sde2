from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract user ID from token (simplified for testing)."""
    # In production, validate JWT token here
    if not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # For testing: decode simple bearer token as user_id
    return credentials.credentials.split("-")[0] if "-" in credentials.credentials else "default-user"
