"""
Vector Store Service — Phase 4
RAG pipeline: Gemini embeddings + FAISS local vector index.

Architecture:
  Embeddings : Gemini text-embedding-004  (768-dim, normalised → cosine sim)
  Index      : FAISS IndexFlatIP           (dot-product of L2-normalised ≡ cosine)
  Storage    : backend/vector_store/
                 combined.faiss  – serialised FAISS index
                 combined.json   – parallel metadata list

Key behaviours:
  • load()           – called once at app startup; reads persisted index from disk.
                       If none exists, creates an empty index. No re-embedding on restart.
  • add_document()   – embeds chunks, removes any previous entry for the same doc_id,
                       then adds fresh embeddings. Saves to disk.
  • remove_document()– strips a document's entries and rebuilds the index. Saves to disk.
  • search()         – embeds the query, runs FAISS search, returns top-K results with
                       full metadata (doc name, page, section, score).

Gemini is used ONLY for embedding text into float vectors.
All storage, retrieval, and ranking is done locally by FAISS.
"""

import os
import json
import time
import threading
import numpy as np
from typing import List, Dict, Optional

from google import genai
from google.genai import types

# ── Constants ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIM   = 3072                  # gemini-embedding-001 output dimension
EMBED_BATCH     = 20                     # chunks per Gemini API call

VECTOR_DIR  = os.path.join(os.path.dirname(__file__), "..", "..", "vector_store")
INDEX_PATH  = os.path.join(VECTOR_DIR, "combined.faiss")
META_PATH   = os.path.join(VECTOR_DIR, "combined.json")

# ── Module-level state ────────────────────────────────────────────────────────
_lock    = threading.Lock()
_index   = None          # FAISS IndexFlatIP
_chunks  = []            # List[Dict]  — parallel to FAISS row positions
_client  = None          # google.genai.Client (lazy init)


# =============================================================================
# INTERNAL HELPERS
# =============================================================================

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def _embed_single(text: str) -> List[float]:
    """Embed one text string with Gemini. Retries once on transient error."""
    client = _get_client()
    for attempt in range(2):
        try:
            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY"
                ),
            )
            # SDK returns response.embeddings (list) or response.embedding (single)
            if hasattr(response, "embeddings") and response.embeddings:
                return response.embeddings[0].values
            if hasattr(response, "embedding") and response.embedding:
                return response.embedding.values
        except Exception as exc:
            if attempt == 0:
                print(f"VectorStore embed retry after error: {exc}")
                time.sleep(1)
            else:
                raise
    raise RuntimeError("Embedding failed after retry")


def _fallback_local_embed(texts: List[str]) -> np.ndarray:
    """Fast, offline, zero-API local TF-IDF semantic vector generator for FAISS."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    try:
        vec = TfidfVectorizer(max_features=EMBEDDING_DIM, ngram_range=(1,2), sublinear_tf=True)
        X = vec.fit_transform(texts).toarray()
    except Exception:
        X = np.ones((len(texts), EMBEDDING_DIM), dtype=np.float32)
    
    if X.shape[1] < EMBEDDING_DIM:
        pad = np.zeros((X.shape[0], EMBEDDING_DIM - X.shape[1]), dtype=np.float32)
        X = np.hstack([X, pad])
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return (X / np.maximum(norms, 1e-9)).astype(np.float32)


def _embed_texts(texts: List[str]) -> np.ndarray:
    """
    Embed a list of texts, returning a float32 numpy array of shape (N, 3072).
    Vectors are L2-normalised so dot-product ≡ cosine similarity.
    """
    if os.getenv("FORCE_LOCAL_EMBED") == "1":
        return _fallback_local_embed(texts)

    all_values = []
    try:
        # Test first chunk fast
        if texts:
            all_values.append(_embed_single(texts[0]))
        for text in texts[1:]:
            all_values.append(_embed_single(text))

        arr   = np.array(all_values, dtype=np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / np.maximum(norms, 1e-9)
    except Exception as exc:
        print(f"VectorStore Gemini embed fallback ({exc}). Using local TF-IDF vectorizer.")
        return _fallback_local_embed(texts)


def _build_faiss_index(vectors: np.ndarray):
    """Create a fresh FAISS IndexFlatIP and add vectors."""
    import faiss  # local import — loaded only when needed
    idx = faiss.IndexFlatIP(EMBEDDING_DIM)
    if vectors.shape[0] > 0:
        idx.add(vectors)
    return idx


# =============================================================================
# PERSISTENCE
# =============================================================================

def save() -> None:
    """Write FAISS index + metadata to disk."""
    global _index, _chunks
    import faiss
    os.makedirs(VECTOR_DIR, exist_ok=True)
    faiss.write_index(_index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        json.dump(_chunks, fh, ensure_ascii=False, indent=2)


def load() -> None:
    """
    Load persisted FAISS index from disk.
    Called ONCE at application startup. If no index exists, initialise empty.
    """
    global _index, _chunks
    import faiss

    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        try:
            _index = faiss.read_index(INDEX_PATH)
            with open(META_PATH, "r", encoding="utf-8") as fh:
                _chunks = json.load(fh)
            print(
                f"VectorStore: loaded {len(_chunks)} chunks "
                f"({_index.ntotal} vectors) from disk."
            )
            return
        except Exception as exc:
            print(f"VectorStore: could not load from disk ({exc}) — starting fresh.")

    _index  = faiss.IndexFlatIP(EMBEDDING_DIM)
    _chunks = []
    print("VectorStore: initialised empty FAISS index.")


# =============================================================================
# PUBLIC API
# =============================================================================

def add_document(doc_id: str, doc_name: str, chunk_dicts: List[Dict]) -> int:
    """
    Embed all chunks for a document and add them to the FAISS index.

    If the document was previously indexed, its old entries are replaced.
    Persists the updated index to disk.

    Returns:
        Number of chunks added.
    """
    global _index, _chunks

    with _lock:
        # 1. Remove any old entries for this document
        surviving = [c for c in _chunks if c["document_id"] != doc_id]
        old_count = len(_chunks) - len(surviving)

        if not chunk_dicts:
            _chunks = surviving
            _rebuild_index_from_metadata(surviving)
            save()
            return 0

        print(
            f"VectorStore: embedding {len(chunk_dicts)} chunks "
            f"for '{doc_name}' (removed {old_count} old entries)…"
        )

        # 2. Embed chunks
        texts      = [c["text"] for c in chunk_dicts]
        embeddings = _embed_texts(texts)   # shape (N, 768)

        # 3. Rebuild index from surviving + new
        all_chunks = surviving + [
            {
                "chunk_id":      c.get("chunk_id",    ""),
                "document_id":   doc_id,
                "document_name": doc_name,
                "page_number":   c.get("page_number", 0),
                "chunk_index":   c.get("chunk_index", i),
                "section":       c.get("section"),
                "text":          c["text"],
            }
            for i, c in enumerate(chunk_dicts)
        ]

        if surviving:
            surviving_texts = [c["text"] for c in surviving]
            surviving_embs  = _embed_texts(surviving_texts)
            all_embs        = np.vstack([surviving_embs, embeddings])
        else:
            all_embs = embeddings

        _index  = _build_faiss_index(all_embs)
        _chunks = all_chunks

        # 4. Persist
        save()
        print(
            f"VectorStore: index now contains {len(_chunks)} chunks "
            f"across {len(set(c['document_id'] for c in _chunks))} document(s)."
        )
        return len(chunk_dicts)


def remove_document(doc_id: str) -> int:
    """
    Remove all entries for a document and rebuild the index.
    Persists the updated index to disk.

    Returns:
        Number of chunks removed.
    """
    global _index, _chunks

    with _lock:
        surviving = [c for c in _chunks if c["document_id"] != doc_id]
        removed   = len(_chunks) - len(surviving)

        if removed == 0:
            return 0

        _rebuild_index_from_metadata(surviving)
        _chunks = surviving
        save()
        print(f"VectorStore: removed {removed} chunks for doc {doc_id}.")
        return removed


def _rebuild_index_from_metadata(chunk_list: List[Dict]) -> None:
    """Re-embed all chunks in chunk_list and rebuild the FAISS index."""
    global _index

    if not chunk_list:
        import faiss
        _index = faiss.IndexFlatIP(EMBEDDING_DIM)
        return

    texts  = [c["text"] for c in chunk_list]
    embs   = _embed_texts(texts)
    _index = _build_faiss_index(embs)


def search(
    query:         str,
    top_k:         int            = 5,
    filter_doc_id: Optional[str]  = None,
) -> Dict:
    """
    Semantic search over all indexed chunks.

    Steps:
      1. Embed the query with Gemini.
      2. Run FAISS dot-product search (= cosine similarity on normalised vecs).
      3. Filter by document if requested.
      4. Return top-K results with full metadata.

    Args:
        query:         Natural-language search query.
        top_k:         Maximum number of results to return.
        filter_doc_id: If given, only return chunks from that document.

    Returns:
        dict with "results" list and "total_indexed" count.
    """
    global _index, _chunks

    if not _chunks or _index is None or _index.ntotal == 0:
        return {
            "results":       [],
            "total_indexed": 0,
            "message":       "No documents are indexed yet.",
        }

    # Embed query
    query_vec = _embed_texts([query])           # shape (1, 768)

    # Oversample to allow post-filter
    k = min(top_k * 5, _index.ntotal)
    scores, indices = _index.search(query_vec, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        chunk = _chunks[int(idx)]
        if filter_doc_id and chunk["document_id"] != filter_doc_id:
            continue
        results.append({
            "rank":          len(results) + 1,
            "score":         round(float(score), 4),
            "chunk_id":      chunk["chunk_id"],
            "document_id":   chunk["document_id"],
            "document_name": chunk["document_name"],
            "page_number":   chunk["page_number"],
            "section":       chunk.get("section"),
            "text":          chunk["text"],
        })
        if len(results) >= top_k:
            break

    return {
        "results":       results,
        "total_indexed": len(_chunks),
    }


def get_stats() -> Dict:
    """Return summary statistics about the current index state."""
    doc_ids = set(c["document_id"] for c in _chunks)
    per_doc = {
        did: {
            "document_name": next(
                c["document_name"] for c in _chunks if c["document_id"] == did
            ),
            "chunk_count": sum(1 for c in _chunks if c["document_id"] == did),
        }
        for did in doc_ids
    }
    return {
        "total_chunks":    len(_chunks),
        "total_documents": len(doc_ids),
        "index_loaded":    _index is not None,
        "index_vectors":   _index.ntotal if _index else 0,
        "documents":       per_doc,
    }
