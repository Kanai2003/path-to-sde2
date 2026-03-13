"""
Async database session management with connection pooling.

Performance optimizations:
- Connection pooling: Reuses connections instead of creating new ones
- pool_pre_ping: Verifies connections before use, prevents stale connection errors
- pool_recycle: Prevents connections from becoming stale
- async: Non-blocking I/O for high concurrency
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=False,  # Set True only for debugging
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,
    autocommit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for async database sessions.
    
    Usage:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# For backward compatibility during migration (sync version)
# TODO: Remove after full migration to async
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
)

SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
