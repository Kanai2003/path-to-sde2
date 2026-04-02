from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.models.base import Base


class File(Base):
    """File metadata model."""

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), index=True)
    stored_filename = Column(String(255), unique=True, index=True)
    file_hash = Column(String(64), index=True)
    file_size = Column(Integer)
    content_type = Column(String(100))
    user_id = Column(String(100), index=True)
    description = Column(Text, nullable=True)
    is_deleted = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<File(id={self.id}, filename={self.original_filename})>"
