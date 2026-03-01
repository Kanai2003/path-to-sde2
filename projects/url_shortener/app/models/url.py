from datetime import datetime, UTC
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class URL(Base):
    """URL model for storing shortened URLs."""
    
    __tablename__ = "urls"

    short_code: Mapped[str] = mapped_column(
        String(10), primary_key=True
    )
    original_url: Mapped[str] = mapped_column(
        nullable=False,
        index=True
    )
    
    fetch_count: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<URL(short_code={self.short_code})>"
