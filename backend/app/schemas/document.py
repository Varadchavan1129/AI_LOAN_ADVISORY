"""
Pydantic schemas for document management endpoints — Phase 3.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentOut(BaseModel):
    id:            str
    original_name: str
    status:        str
    page_count:    Optional[int]
    chunk_count:   Optional[int]
    file_size:     Optional[int]
    error_message: Optional[str]
    uploaded_at:   datetime
    processed_at:  Optional[datetime]

    model_config = {"from_attributes": True}


class ChunkOut(BaseModel):
    id:            str
    document_id:   str
    document_name: str
    page_number:   int
    chunk_index:   int
    section:       Optional[str]
    text:          str
    char_count:    int

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    total:     int
    documents: List[DocumentOut]


class ChunkListResponse(BaseModel):
    document_id: str
    total_chunks: int
    page:        int
    page_size:   int
    chunks:      List[ChunkOut]
