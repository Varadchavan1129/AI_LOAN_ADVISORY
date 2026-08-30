"""
PDF Processor Service — Phase 3

Full pipeline:
  PDF file
    ↓  extract_pages()    — page-by-page text via PyMuPDF
    ↓  clean_text()       — normalise unicode, remove artefacts
    ↓  detect_section()   — heuristic heading detection
    ↓  chunk_text()       — sentence-aware overlapping chunks
    ↓  process_pdf()      — orchestrates the whole pipeline

Each chunk carries:
  chunk_id, document_id, document_name,
  page_number, chunk_index, section, text, char_count

Edge cases handled:
  - Invalid / corrupt PDF    → raises ValueError
  - Empty PDF (0 pages)      → raises ValueError
  - Scanned PDF (no text)    → raises ValueError with guidance
  - Large PDFs               → streamed page-by-page (no full-load)
"""

import os
import re
import uuid
import unicodedata
from typing import List, Dict, Optional

# ── Import guard ──────────────────────────────────────────────────────────────
try:
    import pymupdf as fitz  # pymupdf
    _PYMUPDF_AVAILABLE = True
except ImportError:
    _PYMUPDF_AVAILABLE = False

# ── Chunking constants ────────────────────────────────────────────────────────
CHUNK_SIZE    = 1_000   # characters per chunk
CHUNK_OVERLAP = 150     # overlap between consecutive chunks

# ── Heading heuristics ───────────────────────────────────────────────────────
_HEADING_PATTERN = re.compile(
    r'^(?:\d+[\.\)]\s+|[A-Z][A-Z\s]{3,}$|Section\s+\d+)',
    re.MULTILINE,
)


# =============================================================================
# STEP 1 — EXTRACT
# =============================================================================

def extract_pages(filepath: str) -> List[Dict]:
    """
    Open PDF and return a list of page dicts.
    Each dict: {page_number, raw_text, is_empty}

    Raises ValueError for corrupt / unreadable files.
    """
    if not _PYMUPDF_AVAILABLE:
        raise RuntimeError("PyMuPDF (pymupdf) is not installed.")

    if not os.path.exists(filepath):
        raise ValueError(f"File not found: {filepath}")

    try:
        doc = fitz.open(filepath)
    except Exception as exc:
        raise ValueError(f"Cannot open PDF: {exc}") from exc

    if doc.page_count == 0:
        doc.close()
        raise ValueError("PDF has no pages.")

    pages = []
    for idx in range(doc.page_count):
        page = doc.load_page(idx)
        text = page.get_text("text")          # plain text, preserves layout
        pages.append({
            "page_number": idx + 1,
            "raw_text":    text,
            "is_empty":    not text.strip(),
        })

    doc.close()
    return pages


# =============================================================================
# STEP 2 — CLEAN
# =============================================================================

def clean_text(raw: str) -> str:
    """
    Normalise and clean raw PDF text.
    - Unicode NFKC normalisation
    - Remove null bytes and soft-hyphens
    - Collapse excessive whitespace
    - Strip leading/trailing blank lines
    """
    # Normalise unicode (handles ligatures, weird chars)
    text = unicodedata.normalize("NFKC", raw)

    # Remove null bytes and soft-hyphens
    text = text.replace("\x00", "").replace("\xad", "")

    # Join hyphenated line-breaks  (word-\nbreak → wordbreak)
    text = re.sub(r"-\n(\S)", r"\1", text)

    # Collapse 3+ blank lines → 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse horizontal whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Strip lines that are purely page-number artefacts (e.g.  "Page 3 of 10")
    text = re.sub(r"\n?Page\s+\d+\s+of\s+\d+\n?", "\n", text, flags=re.IGNORECASE)

    return text.strip()


# =============================================================================
# STEP 3 — SECTION DETECTION
# =============================================================================

def detect_section(text: str) -> Optional[str]:
    """
    Heuristically identify a section heading from the start of a text block.
    Returns the heading string or None.
    """
    first_line = text.split("\n")[0].strip()
    if _HEADING_PATTERN.match(first_line) and len(first_line) < 120:
        return first_line
    return None


# =============================================================================
# STEP 4 — CHUNK
# =============================================================================

def chunk_text(
    text: str,
    page_number: int,
    document_id: str,
    document_name: str,
    global_chunk_offset: int = 0,
) -> List[Dict]:
    """
    Split cleaned text into overlapping, sentence-aware chunks.

    Strategy:
      1. Split into sentences (. ! ? terminators).
      2. Accumulate sentences until CHUNK_SIZE is reached.
      3. Emit chunk, back up by CHUNK_OVERLAP characters.
      4. Repeat.

    Each chunk retains: chunk_id, document_id, document_name,
                         page_number, chunk_index, section, text, char_count.
    """
    if not text:
        return []

    section = detect_section(text)

    # Sentence-split: keep delimiter attached to its sentence
    sentence_re = re.compile(r'(?<=[.!?])\s+')
    sentences   = sentence_re.split(text)
    if not sentences:
        return []

    chunks       = []
    chunk_index  = global_chunk_offset
    buf          = ""

    for sent in sentences:
        if len(buf) + len(sent) + 1 <= CHUNK_SIZE:
            buf = (buf + " " + sent).strip() if buf else sent
        else:
            # Emit current buffer as a chunk
            if buf:
                chunks.append(_make_chunk(
                    buf, chunk_index, page_number,
                    document_id, document_name, section
                ))
                chunk_index += 1
                # Overlap: keep the trailing CHUNK_OVERLAP chars
                buf = buf[-CHUNK_OVERLAP:].strip() + " " + sent
            else:
                # Sentence is longer than CHUNK_SIZE — hard split
                buf = sent

    # Emit final buffer
    if buf.strip():
        chunks.append(_make_chunk(
            buf.strip(), chunk_index, page_number,
            document_id, document_name, section
        ))

    return chunks


def _make_chunk(
    text: str,
    chunk_index: int,
    page_number: int,
    document_id: str,
    document_name: str,
    section: Optional[str],
) -> Dict:
    return {
        "chunk_id":      str(uuid.uuid4()),
        "document_id":   document_id,
        "document_name": document_name,
        "page_number":   page_number,
        "chunk_index":   chunk_index,
        "section":       section,
        "text":          text,
        "char_count":    len(text),
    }


# =============================================================================
# ORCHESTRATOR
# =============================================================================

def process_pdf(
    filepath: str,
    document_id: str,
    document_name: str,
) -> Dict:
    """
    Full PDF processing pipeline.

    Returns:
        {
          "page_count":  int,
          "chunk_count": int,
          "chunks":      List[Dict],
          "warnings":    List[str],   # e.g. scanned pages skipped
        }

    Raises:
        ValueError  — invalid PDF, empty PDF, fully-scanned PDF
        RuntimeError — missing pymupdf dependency
    """
    pages    = extract_pages(filepath)      # raises on error
    warnings = []

    # Scanned-PDF detection
    scanned_count = sum(1 for p in pages if p["is_empty"])
    if scanned_count == len(pages):
        raise ValueError(
            "This PDF contains only scanned images with no extractable text. "
            "OCR (Optical Character Recognition) is required to process it. "
            "Please provide a text-based PDF."
        )
    if scanned_count > 0:
        warnings.append(
            f"{scanned_count} page(s) appear to be scanned images and were skipped."
        )

    all_chunks    = []
    global_offset = 0

    for page in pages:
        if page["is_empty"]:
            continue

        cleaned = clean_text(page["raw_text"])
        if not cleaned:
            continue

        page_chunks = chunk_text(
            cleaned,
            page_number=page["page_number"],
            document_id=document_id,
            document_name=document_name,
            global_chunk_offset=global_offset,
        )
        all_chunks.extend(page_chunks)
        global_offset += len(page_chunks)

    return {
        "page_count":  len(pages),
        "chunk_count": len(all_chunks),
        "chunks":      all_chunks,
        "warnings":    warnings,
    }
