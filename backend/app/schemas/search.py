"""
Pydantic schemas for the semantic search endpoint — Phase 4.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class SearchRequest(BaseModel):
    query:         str
    top_k:         int           = Field(default=5, ge=1, le=20)
    filter_doc_id: Optional[str] = None   # restrict search to one document


class ChunkResult(BaseModel):
    rank:          int
    score:         float
    chunk_id:      str
    document_id:   str
    document_name: str
    page_number:   int
    section:       Optional[str]
    text:          str


class SearchResponse(BaseModel):
    query:         str
    results:       List[ChunkResult]
    total_indexed: int
    message:       Optional[str] = None
