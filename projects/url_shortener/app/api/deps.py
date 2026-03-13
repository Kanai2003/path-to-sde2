"""
Dependency injection for FastAPI endpoints.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, SessionLocal


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
