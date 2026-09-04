"""
Centralised text-generation helper.

Text generation (intent parsing, general answers, RAG answer generation,
validation, empathy, credit advice) is routed through the Emergent Universal
Key (Gemini) which is reliable regardless of the user's personal Gemini
free-tier text quota.

If the universal key is unavailable it falls back to the user's own
GEMINI_API_KEY (google.genai). Embeddings continue to use the user's key
directly (see services/vector_store.py).

All callers are synchronous FastAPI handlers, so the async LlmChat call is
wrapped with asyncio.run in a dedicated thread-safe manner.
"""
import os
import re
import json
import uuid
import asyncio
import logging

logger = logging.getLogger("tata_mitra.llm")

_EMERGENT_KEY = os.getenv("EMERGENT_LLM_KEY", "")
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = "gemini-2.5-flash"


def _run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(lambda: asyncio.run(coro)).result()
    except RuntimeError:
        pass
    return asyncio.run(coro)


async def _emergent_complete(system_message: str, user_text: str) -> str:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    chat = LlmChat(
        api_key=_EMERGENT_KEY,
        session_id=f"tata-mitra-{uuid.uuid4()}",
        system_message=system_message or "You are a helpful assistant.",
    ).with_model("gemini", GEMINI_MODEL)
    resp = await chat.send_message(UserMessage(text=user_text))
    return resp if isinstance(resp, str) else str(resp)


def complete(user_text: str, system_message: str = "") -> str | None:
    """Return generated text, or None if all providers fail."""
    # Primary: Emergent Universal Key (Gemini)
    if _EMERGENT_KEY:
        try:
            return _run_async(_emergent_complete(system_message, user_text)).strip()
        except Exception as e:
            logger.warning(f"Universal-key text gen failed: {e}")

    # Fallback: user's own Gemini key via google.genai
    if _GEMINI_KEY and _GEMINI_KEY != "dummy":
        try:
            from google import genai
            client = genai.Client(api_key=_GEMINI_KEY)
            contents = (f"{system_message}\n\n{user_text}" if system_message else user_text)
            r = client.models.generate_content(model="models/gemini-flash-latest", contents=contents)
            return (r.text or "").strip()
        except Exception as e:
            logger.warning(f"User-key text gen failed: {e}")

    return None


def complete_json(user_text: str, system_message: str = "") -> dict | None:
    """Return a parsed JSON object from the model, or None on failure."""
    raw = complete(
        user_text,
        (system_message or "") + "\n\nRespond with ONLY valid JSON. No markdown, no code fences.",
    )
    if not raw:
        return None
    text = raw.strip()
    # Strip code fences if the model added them
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    # Extract the first {...} block if extra prose surrounds it
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        text = m.group(0)
    try:
        return json.loads(text)
    except Exception as e:
        logger.warning(f"JSON parse failed: {e}")
        return None


def is_available() -> bool:
    return bool(_EMERGENT_KEY or (_GEMINI_KEY and _GEMINI_KEY != "dummy"))


def translate(text: str, target_language: str) -> str | None:
    """Translate user-facing conversation text into the target language.

    Preserves all numbers, currency amounts (₹), percentages, dates and
    proper nouns. Does NOT add, remove or invent any facts — this is a pure
    language rendering step for the conversation layer only.
    """
    if not text or not text.strip():
        return text
    system = (
        f"You are a professional translator. Translate the user's text into {target_language}. "
        "STRICT RULES: Keep the exact meaning; do NOT add, remove, or invent any information. "
        "Preserve ALL numbers, currency symbols and amounts (like ₹5,00,000), percentages, dates, "
        "URLs, and English proper nouns / brand names (e.g. SBI, HDFC, CIBIL, RBI, EMI, FOIR, DTI) as-is. "
        "Preserve Markdown formatting (bullets, bold, headings). "
        "Output ONLY the translated text with no preamble or explanation."
    )
    out = complete(text, system)
    return out or text
