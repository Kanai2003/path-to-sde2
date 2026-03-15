import hashlib
import hmac
import os
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=UserRepository._hash_password(user_data.password),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> User | None:
        normalized_email = email.strip().lower()
        result = await db.execute(
            select(User).where(User.email == normalized_email, User.is_active.is_(True))
        )
        user = result.scalar_one_or_none()
        if user and UserRepository._verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    async def store_refresh_token(
        db: AsyncSession, user_id: str, refresh_token: str, expires_at: datetime
    ) -> RefreshToken:
        token_row = RefreshToken(
            user_id=user_id,
            token_hash=UserRepository._hash_refresh_token(refresh_token),
            expires_at=expires_at,
        )
        db.add(token_row)
        await db.commit()
        await db.refresh(token_row)
        return token_row

    @staticmethod
    async def logout(db: AsyncSession, user_id: str, refresh_token: str) -> bool:
        token_hash = UserRepository._hash_refresh_token(refresh_token)
        now = datetime.now(UTC)
        result = await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
            .values(revoked=True, updated_at=now)
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def revoke_all_tokens(db: AsyncSession, user_id: str) -> int:
        now = datetime.now(UTC)
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
            .values(revoked=True, updated_at=now)
        )
        await db.commit()
        return result.rowcount or 0

    @staticmethod
    def _hash_password(password: str) -> str:
        iterations = 310_000
        salt = os.urandom(16)
        derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${derived.hex()}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        # Backward compatibility: support legacy unsalted SHA-256 hashes.
        if "$" not in stored_hash:
            legacy = hashlib.sha256((password + "0").encode()).hexdigest()
            return hmac.compare_digest(legacy, stored_hash)

        try:
            scheme, iterations_text, salt_hex, hash_hex = stored_hash.split("$", 3)
            if scheme != "pbkdf2_sha256":
                return False
            iterations = int(iterations_text)
            expected = bytes.fromhex(hash_hex)
            salt = bytes.fromhex(salt_hex)
        except (ValueError, TypeError):
            return False

        calculated = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
        return hmac.compare_digest(calculated, expected)

    @staticmethod
    def _hash_refresh_token(refresh_token: str) -> str:
        return hashlib.sha256(refresh_token.encode()).hexdigest()


user_repository = UserRepository()


# Backward compatibility for existing imports.
USER_REPOSITORY = UserRepository