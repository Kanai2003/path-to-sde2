"""Authentication service (JWT access + refresh token workflows)."""

from __future__ import annotations

from jwt import InvalidTokenError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_token_expiry_datetime,
)
from app.models.user import User
from app.repositories.user_repository import user_repository
from app.schemas.user import TokenResponse, UserCreate, UserLogin


class AuthService:
    """Service layer for authentication and token lifecycle operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = user_repository

    async def register(self, data: UserCreate) -> User | None:
        existing = await self.repo.get_by_email(self.db, data.email)
        if existing:
            return None

        try:
            return await self.repo.create(self.db, data)
        except IntegrityError:
            return None

    async def login(self, data: UserLogin) -> TokenResponse | None:
        user = await self.repo.login(self.db, data.email, data.password)
        if not user:
            return None

        access_token, access_ttl = create_access_token(user.id)
        refresh_token, refresh_ttl = create_refresh_token(user.id)
        refresh_expires_at = get_token_expiry_datetime(refresh_token)

        await self.repo.store_refresh_token(self.db, user.id, refresh_token, refresh_expires_at)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_ttl,
            refresh_expires_in=refresh_ttl,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse | None:
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_id = payload.get("sub")
            if not user_id:
                return None
        except InvalidTokenError:
            return None

        token_row = await self.repo.get_active_refresh_token(self.db, user_id, refresh_token)
        if not token_row:
            return None

        user = await self.repo.get_by_id(self.db, user_id)
        if not user or not user.is_active:
            return None

        await self.repo.logout(self.db, user_id, refresh_token)

        new_access_token, access_ttl = create_access_token(user.id)
        new_refresh_token, refresh_ttl = create_refresh_token(user.id)
        refresh_expires_at = get_token_expiry_datetime(new_refresh_token)
        await self.repo.store_refresh_token(self.db, user.id, new_refresh_token, refresh_expires_at)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=access_ttl,
            refresh_expires_in=refresh_ttl,
        )

    async def logout(self, user_id: str, refresh_token: str) -> bool:
        return await self.repo.logout(self.db, user_id, refresh_token)

    async def logout_all(self, user_id: str) -> int:
        return await self.repo.revoke_all_tokens(self.db, user_id)


def get_auth_service(db: AsyncSession) -> AuthService:
    """Dependency injection helper."""
    return AuthService(db)
