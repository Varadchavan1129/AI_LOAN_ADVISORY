"""
Pydantic schemas for the RAG Ask endpoint — Phase 5.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class RAGRequest(BaseModel):
    question:       str
    top_k:          int   = Field(default=5, ge=1, le=20)
    min_relevance:  float = Field(default=0.70, ge=0.0, le=1.0)
    filter_doc_id:  Optional[str] = None


class SourceCitation(BaseModel):
    document_name:   str
    document_id:     str
    page_number:     int
    section:         Optional[str]
    chunk_id:        str
    relevance_score: float


class EvidencePreview(BaseModel):
    document_name: str
    page_number:   int
    section:       Optional[str]
    score:         float
    text_preview:  str


class ValidationResult(BaseModel):
    verdict:            str          # SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED
    reasoning:          str
    unsupported_claims: List[str]


class RAGResponse(BaseModel):
    question:         str
    answer:           str
    is_verified:      bool
    support_level:    str            # SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED
    sources:          List[SourceCitation]
    validation:       ValidationResult
    retrieved_chunks: int
    top_evidence:     List[EvidencePreview]
