"""
Document DB model — Phase 3
Stores metadata for each uploaded PDF.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base


class Document(Base):
    __tablename__ = "documents"

    id            = Column(String, primary_key=True, index=True)
    original_name = Column(String, nullable=False)      # user-facing name
    stored_name   = Column(String, nullable=False)      # filename on disk
    status        = Column(String, default="pending")   # pending|processing|indexed|failed
    page_count    = Column(Integer, nullable=True)
    chunk_count   = Column(Integer, nullable=True)
    file_size     = Column(Integer, nullable=True)      # bytes
    error_message = Column(Text,    nullable=True)
    uploaded_at   = Column(DateTime(timezone=True), server_default=func.now())
    processed_at  = Column(DateTime(timezone=True), nullable=True)
