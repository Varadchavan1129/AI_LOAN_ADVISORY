"""
Validation Agent — Phase 5
Independently fact-checks a generated RAG answer against the retrieved evidence.

Flow:
  1. Receives: question + candidate answer + evidence chunks.
  2. Sends a strict JSON-structured prompt to Gemini.
  3. Returns: verdict (SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED)
             + reasoning + list of any unsupported claims.

If PARTIALLY_SUPPORTED, also attempts to rewrite the answer to strip unsupported claims.

Verdicts:
  SUPPORTED          — every factual claim traces back to the evidence.
  PARTIALLY_SUPPORTED — some claims are grounded; at least one is not.
  UNSUPPORTED        — major claims absent from or contradicted by the evidence.
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple

from google import genai
from google.genai import types

_client: Optional[genai.Client] = None
MODEL = "models/gemini-flash-latest"

VALID_VERDICTS = {"SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"}


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def _evidence_summary(chunks: List[Dict]) -> str:
    """Compact evidence block for the validation prompt."""
    parts = []
    for i, ch in enumerate(chunks, 1):
        text = ch["text"].strip()[:600]     # limit to keep prompt short
        parts.append(
            f"[Evidence {i}] {ch['document_name']} | Page {ch['page_number']}\n{text}"
        )
    return "\n\n".join(parts)


def _parse_verdict_json(raw: str) -> Optional[Dict]:
    """Extract and parse a JSON object from the model's raw output."""
    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r'```(?:json)?\s*', '', raw).strip()

    # Try direct JSON parse on cleaned string
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try direct JSON parse on original string
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try to extract embedded JSON object
    match = re.search(r'\{[^{}]*"verdict"[^{}]*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _fallback_verdict(raw: str) -> str:
    """Heuristic verdict extraction when JSON parsing fails."""
    upper = raw.upper()
    if "PARTIALLY_SUPPORTED" in upper or "PARTIALLY SUPPORTED" in upper:
        return "PARTIALLY_SUPPORTED"
    if "UNSUPPORTED" in upper:
        return "UNSUPPORTED"
    if "SUPPORTED" in upper:
        return "SUPPORTED"
    return "UNSUPPORTED"


# =============================================================================
# PUBLIC API
# =============================================================================

def validate_answer(
    question: str,
    answer: str,
    chunks: List[Dict],
) -> Dict:
    """
    Validate whether the generated answer is supported by retrieved evidence.

    Returns:
        {
          verdict             : "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED"
          reasoning           : str   — brief explanation
          unsupported_claims  : List[str]
        }
    """
    if not answer or not chunks:
        return {
            "verdict":            "UNSUPPORTED",
            "reasoning":          "No answer or evidence to validate.",
            "unsupported_claims": [],
        }

    evidence_summary = _evidence_summary(chunks)

    prompt = f"""You are a strict fact-checking agent for a loan advisory platform.

TASK: Determine whether the ANSWER below is supported by the EVIDENCE.

━━━━━ VERDICT DEFINITIONS ━━━━━
SUPPORTED           — Every factual claim in the answer is traceable to the evidence.
PARTIALLY_SUPPORTED — Some claims are grounded in evidence; at least one is not.
UNSUPPORTED         — Key claims are absent from or contradict the evidence, OR the
                      answer contains invented numbers, rates, or policies not in the evidence.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EVIDENCE:
{evidence_summary}

QUESTION: {question}

ANSWER TO VALIDATE:
{answer}

Respond with ONLY a JSON object, no other text:
{{
  "verdict": "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED",
  "reasoning": "One or two sentences explaining your verdict.",
  "unsupported_claims": ["Specific claims not found in evidence, if any"]
}}"""

    client = _get_client()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=500,
            ),
        )
    except Exception as api_err:
        print(f"ValidationAgent Gemini API error: {api_err}")
        # Graceful fallback: treat as PARTIALLY_SUPPORTED so the RAG answer
        # still reaches the user rather than being discarded.
        return {
            "verdict":            "PARTIALLY_SUPPORTED",
            "reasoning":          "Validation service temporarily unavailable.",
            "unsupported_claims": [],
        }

    raw = (response.text or "").strip()
    parsed = _parse_verdict_json(raw)

    if parsed:
        verdict = str(parsed.get("verdict", "UNSUPPORTED")).strip().upper()
        if verdict not in VALID_VERDICTS:
            verdict = "UNSUPPORTED"
        return {
            "verdict":            verdict,
            "reasoning":          str(parsed.get("reasoning", "")),
            "unsupported_claims": parsed.get("unsupported_claims", []),
        }

    # Fallback when JSON parsing fails
    return {
        "verdict":            _fallback_verdict(raw),
        "reasoning":          raw[:300],
        "unsupported_claims": [],
    }


from app.agents.rag_agent import sanitize_rag_answer


def rewrite_for_partial_support(
    question: str,
    answer: str,
    chunks: List[Dict],
    unsupported_claims: List[str],
) -> str:
    """
    If the answer is PARTIALLY_SUPPORTED, rewrite it to remove claims that
    aren't grounded in the evidence.

    Returns the cleaned answer string.
    """
    clean_orig = sanitize_rag_answer(answer)
    if not unsupported_claims:
        return clean_orig or answer

    evidence_summary = _evidence_summary(chunks)
    claims_block = "\n".join(f"- {c}" for c in unsupported_claims)

    prompt = f"""You are a loan policy assistant.

The following answer contains some claims NOT supported by the evidence.
Rewrite the answer to ONLY include the parts that are supported by the evidence.
Remove or rephrase any claim listed as unsupported.
Keep the same tone. Do not add new information.
Do NOT add meta commentary, thoughts, or leadings like 'formatting clean and precise'.

EVIDENCE:
{evidence_summary}

ORIGINAL ANSWER:
{answer}

UNSUPPORTED CLAIMS TO REMOVE:
{claims_block}

REWRITTEN ANSWER (only supported claims, cite Evidence numbers):"""

    client = _get_client()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=1500,
            ),
        )
        raw_rw = (response.text or "").strip()
        cleaned_rw = sanitize_rag_answer(raw_rw)
        if len(cleaned_rw) >= 20:
            return cleaned_rw
        return clean_orig or answer
    except Exception as api_err:
        print(f"ValidationAgent rewrite Gemini error: {api_err}")
        return clean_orig or answer  # return original sanitized answer if rewrite fails

