"""
DocumentChunk DB model — Phase 3
Stores each text chunk extracted from a PDF, with full metadata.
"""
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.db import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id            = Column(String, primary_key=True, index=True)   # UUID
    document_id   = Column(String, index=True, nullable=False)      # FK → documents.id
    document_name = Column(String, nullable=False)                  # friendly name for retrieval
    page_number   = Column(Integer, nullable=False)
    chunk_index   = Column(Integer, nullable=False)                 # sequential within doc
    section       = Column(String, nullable=True)                   # heading / section title if detected
    text          = Column(Text, nullable=False)
    char_count    = Column(Integer, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
