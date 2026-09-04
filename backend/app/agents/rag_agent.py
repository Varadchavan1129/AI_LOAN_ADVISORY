"""
RAG Agent — Phase 5
Generates answers strictly grounded in retrieved policy document evidence.

Design Principles:
  • Uses retrieved chunks (from Phase 4 vector_store) as the ONLY knowledge source.
  • Temperature is set to 0.1 — deterministic, no creative invention.
  • If the answer cannot be found in the evidence, returns NOT_IN_EVIDENCE signal.
  • Extracts which evidence blocks were cited so sources are accurate.
  • Never invents loan limits, rates, DTI thresholds, or eligibility rules.
"""

import os
import re
from typing import List, Dict, Optional

from google import genai
from google.genai import types
from app.services import llm_text

# Sentinel returned by the model when evidence doesn't contain the answer
_NOT_IN_EVIDENCE = "NOT_IN_EVIDENCE"


def _build_evidence_block(chunks: List[Dict]) -> str:
    """Format retrieved chunks as numbered evidence blocks for the prompt."""
    lines = []
    for i, ch in enumerate(chunks, 1):
        lines.append(f"[EVIDENCE {i}]")
        lines.append(f"  Document : {ch['document_name']}")
        lines.append(f"  Page     : {ch['page_number']}")
        if ch.get("section"):
            lines.append(f"  Section  : {ch['section']}")
        lines.append(f"  Text     :\n  {ch['text'].strip()}")
        lines.append("")
    return "\n".join(lines)


def _extract_cited_indices(answer_text: str, num_chunks: int) -> List[int]:
    """
    Find which Evidence numbers were referenced in the answer text.
    Returns a sorted list of 0-based indices.
    """
    indices = set()
    for m in re.finditer(r'\bevidence\s+(\d+)\b', answer_text, re.IGNORECASE):
        idx = int(m.group(1)) - 1          # convert to 0-based
        if 0 <= idx < num_chunks:
            indices.add(idx)
    # Also look for "(Evidence N)" or "[Evidence N]" patterns
    for m in re.finditer(r'[\[\(]Evidence\s+(\d+)[\]\)]', answer_text, re.IGNORECASE):
        idx = int(m.group(1)) - 1
        if 0 <= idx < num_chunks:
            indices.add(idx)
    return sorted(indices)


def sanitize_rag_answer(text: str) -> str:
    """
    Light, non-destructive cleanup of generated / rewritten RAG text.

    Only two things are removed:
      1. Meta preambles the model sometimes leaks ("Here is the answer:").
      2. Inline evidence citation tags — "(Evidence 1)" / "[Evidence 2]" —
         which are an internal prompt convention, not user-facing content.

    Everything else is preserved verbatim. In particular this function NEVER
    truncates, slices or drops content: doing so previously produced corrupted,
    mid-sentence answers in the UI. Markdown structure (headings, bullet
    nesting, bold, blank lines) is preserved.
    """
    if not text:
        return ""

    s = text.strip()

    # 1. Strip a leaked meta preamble on the very first line only
    s = re.sub(
        r'^(?:formatting[^\n.]*[\.\:]\s*|here\s+is[^\n.]*[\.\:]\s*)',
        '',
        s,
        flags=re.IGNORECASE,
    ).strip()

    # 2. Strip citation tags: (Evidence 1), [Evidence 2], (Evidence 1, 2 and 3)
    s = re.sub(
        r'[\(\[]\s*Evidence\s+\d+(?:\s*(?:,|and|&)\s*\d+)*\s*[\]\)]',
        '',
        s,
        flags=re.IGNORECASE,
    )
    s = re.sub(r'\bEvidence\s+\d+\b', '', s, flags=re.IGNORECASE)

    # 3. Per-line tidy-up. Leading indentation is preserved so nested markdown
    #    lists keep rendering correctly.
    out_lines = []
    for line in s.split("\n"):
        m = re.match(r'^([ \t]*)(.*)$', line)
        indent, body = m.group(1), m.group(2)
        body = re.sub(r'[ \t]{2,}', ' ', body)          # collapse runs of spaces
        body = re.sub(r'\(\s*\)|\[\s*\]', '', body)     # empty brackets left by (2)
        body = re.sub(r'[ \t]+([,.;:])', r'\1', body)   # space orphaned before punctuation
        body = body.rstrip()
        # A single leading space is not enough for markdown list nesting
        if indent == " " and re.match(r'^[*\-+]\s', body):
            indent = "  "
        out_lines.append(indent + body)

    s = "\n".join(out_lines)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def generate_answer(question: str, chunks: List[Dict]) -> Dict:
    """
    Generate a strictly grounded answer from retrieved evidence.

    Args:
        question : The user's natural-language question.
        chunks   : Retrieved chunks from vector_store.search() with full metadata.

    Returns a dict with:
        answer            : The generated answer text, or None.
        not_in_evidence   : True if the evidence does not contain the answer.
        generation_failed : True if the LLM provider was unavailable.
        sources           : List of cited source metadata dicts.
        raw_response      : Raw LLM output string (for validation agent).
    """
    if not chunks:
        return {
            "answer":            None,
            "not_in_evidence":   True,
            "generation_failed": False,
            "sources":           [],
            "raw_response":      None,
        }

    evidence_block = _build_evidence_block(chunks)

    prompt = f"""You are a policy assistant for Tata Mitra, a loan advisory system.

Your task: Answer the user's question clearly and completely using the numbered evidence blocks below.

━━━━━━━━ RULES ━━━━━━━━
1. Use ONLY information from the provided evidence. Do NOT use your own general knowledge.
2. Never invent or assume any numbers: no loan limits, interest rates, credit scores,
   DTI ratios, income thresholds, tenure limits, or processing fees unless they appear
   verbatim in the evidence.
3. When you state a fact, reference its evidence block: e.g., "(Evidence 2)".
4. If the evidence contains PARTIAL information, answer with what IS available.
5. ONLY respond with exactly the word {_NOT_IN_EVIDENCE} if the evidence blocks are
   completely unrelated to the question (zero relevant content).
6. Be clear, complete, and direct. Do NOT add meta commentary, thoughts, or preambles like 'formatting clean and precise'.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EVIDENCE:
{evidence_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USER QUESTION: {question}

ANSWER (cite Evidence numbers for every fact you state):"""

    raw_answer = llm_text.complete(prompt)
    if not raw_answer:
        # The generator is unavailable (rate limit / provider error). We do NOT
        # synthesise an answer from raw chunk text — that produced corrupted,
        # mid-sentence output. Surface the failure honestly instead.
        return {
            "answer":            None,
            "not_in_evidence":   False,
            "generation_failed": True,
            "sources":           [],
            "raw_response":      None,
        }

    raw_answer = raw_answer.strip()

    # Detect NOT_IN_EVIDENCE sentinel
    if raw_answer.upper().startswith(_NOT_IN_EVIDENCE) or raw_answer.strip() == _NOT_IN_EVIDENCE:
        return {
            "answer":            None,
            "not_in_evidence":   True,
            "generation_failed": False,
            "sources":           [],
            "raw_response":      raw_answer,
        }

    # Build sources from cited evidence blocks
    cited_indices = _extract_cited_indices(raw_answer, len(chunks))
    if not cited_indices:
        cited_indices = list(range(min(2, len(chunks))))

    sources = [
        {
            "document_name":    chunks[i]["document_name"],
            "document_id":      chunks[i]["document_id"],
            "page_number":      chunks[i]["page_number"],
            "section":          chunks[i].get("section"),
            "chunk_id":         chunks[i]["chunk_id"],
            "relevance_score":  round(float(chunks[i].get("score", 0.0)), 4),
        }
        for i in cited_indices
    ]

    cleaned_answer = sanitize_rag_answer(raw_answer)

    return {
        "answer":            cleaned_answer or raw_answer,
        "not_in_evidence":   False,
        "generation_failed": False,
        "sources":           sources,
        "raw_response":      raw_answer,
    }
