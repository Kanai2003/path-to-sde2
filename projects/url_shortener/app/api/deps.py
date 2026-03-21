"""
Dependency injection for FastAPI endpoints.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal, SessionLocal
from app.models.user import User
from app.repositories.user_repository import user_repository


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", auto_error=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency.
    
    Usage in endpoints:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Model))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Sync version for backward compatibility (scheduler, etc.)
def get_sync_db():
    """Sync database session for background jobs."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type="access")
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except InvalidTokenError as exc:
        raise credentials_error from exc

    user = await user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise credentials_error

    return user


async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    token: str | None = Depends(oauth2_scheme_optional),
) -> User | None:
    if not token:
        return None

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token, expected_type="access")
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except InvalidTokenError as exc:
        raise credentials_error from exc

    user = await user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise credentials_error

    return user
