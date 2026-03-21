from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> tuple[str, int]:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = _create_token(subject=subject, token_type="access", expires_delta=expires_delta)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(subject: str) -> tuple[str, int]:
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = _create_token(subject=subject, token_type="refresh", expires_delta=expires_delta)
    return token, int(expires_delta.total_seconds())


def decode_token(token: str, expected_type: str | None = None) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    if expected_type and payload.get("type") != expected_type:
        raise InvalidTokenError("Invalid token type")
    return payload


def get_token_expiry_datetime(token: str) -> datetime:
    payload = decode_token(token)
    exp = payload.get("exp")
    if exp is None:
        raise InvalidTokenError("Token missing expiration claim")
    return datetime.fromtimestamp(exp, UTC)
