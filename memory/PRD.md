# Tata Mitra — Product Requirements & Progress

## Original Problem
Upgrade the existing "Tata Mitra" project into a polished, explainable AI loan-advisory
platform: Understand → Calculate → Assess → Retrieve → Recommend → Validate → Explain → Source.
Preserve existing features; never invent bank/RBI policies, rates or data.

## Architecture (preserved from original)
- LLM (language understanding/generation) — Gemini
- Python deterministic math — EMI / DTI / max loan / affordability
- scikit-learn ML — risk estimation (`app/ml/risk_model.pkl`)
- Rules — eligibility / DTI thresholds
- RAG + FAISS — document knowledge (Gemini embeddings 3072-dim)
- Structured DB (SQLite) — verified loan products
- Validation Agent — evidence verification (SUPPORTED / PARTIALLY / UNSUPPORTED)
- Orchestrator — routing

## Tech Stack
- Frontend: React 18 + TypeScript + Vite (port 3000), Tailwind glassmorphism, framer-motion, recharts, react-markdown
- Backend: FastAPI (port 8001, all routes under `/api`), SQLAlchemy + SQLite, FAISS, google-genai
- LLM text: Emergent Universal Key (Gemini `gemini-2.5-flash`) primary → user GEMINI_API_KEY fallback → static
- Embeddings: user GEMINI_API_KEY (`gemini-embedding-001`)
- File storage: Emergent object storage (PDFs)

## Environment migration done (2026-06)
- Added `backend/server.py` (supervisor entrypoint) importing `app.main:app`
- Prefixed ALL backend routes with `/api` for Kubernetes ingress
- CORS opened (header-based admin auth)
- Frontend: added `start` script, vite host/port 3000 + allowedHosts, `envPrefix` REACT_APP_,
  `src/api.ts` centralised base, all fetches use `${API}/...`
- Removed unused `@supabase/supabase-js` (Node22 conflict); added `react-is`; un-excluded lucide-react
- Fixed missing imports in credit_improvement_agent

## Implemented / Verified (2026-06)
- Natural-language chat + intent routing (EMI, eligibility, max loan, DTI, general, policy) ✅
- Deterministic EMI/DTI/max-loan math ✅
- ML + rules eligibility + empathy + credit-improvement ✅
- RAG pipeline: upload → object storage → PyMuPDF → chunk → Gemini embed → FAISS → answer → Validation ✅
  - 13 educational PDFs indexed; SUPPORTED answers with source/page/relevance; NOT_IN_EVIDENCE works ✅
- Verified loan products seeded (SBI/HDFC/ICICI/Axis/Kotak, real source URLs + verification status) ✅
- Multilingual conversation layer (English/Hindi/Marathi) — translates message/title/advice/answer,
  preserves numbers/₹/%/proper nouns; deterministic data untouched ✅
- Admin: upload/process/list/chunks/delete, dashboard stats ✅

## Backlog / Next
- P1: Loan **product discovery + personalized recommendation** chat intent & UI card
  (combine verified product data + estimated EMI + affordability + source/freshness + lender disclaimer)
- P1: UI polish pass on glassmorphism (contrast/readability), recommendation card
- P2: Optional Graph relationships (user→profile→eligibility→product→lender) — only if real benefit
- P2: Refresh/verify loan-product data periodically (verification_status/last_verified_at)

## RAG response corruption fix (2026-06-04)
Root cause (two independent defects, both in the RAG failure path):
1. `rag_agent.generate_answer()` — when the text LLM returned nothing, it fell back to
   `format_extracted_policy_answer()`, which either returned HARDCODED canned answers or
   naively sliced sentences out of `clean_chunk_text()`-mutilated chunk text. The greedy
   `!!DEMO DOCUMENT[^\n]*!!` regex ate mid-line content, producing the corrupted UI output
   ("ial institution. Contents: 1. Eligibility Criteria || 3.").
   Also `sanitize_rag_answer()` truncated at the last `.`/`!`/`?`, dropped short bullet lines
   and collapsed all whitespace (destroying markdown list nesting).
2. `validation_agent.validate_answer()` — on LLM failure it returned a FAKE
   `PARTIALLY_SUPPORTED` verdict, so the UI showed the green/amber "Partially Verified —
   Some claims confirmed by evidence" badge when no fact-check had actually run.

Changes:
- Deleted `format_extracted_policy_answer()` and `clean_chunk_text()` (no hardcoded answers,
  no chunk-slicing fabrication). LLM failure now returns `generation_failed: True`.
- Rewrote `sanitize_rag_answer()`: non-destructive — strips only meta preambles and
  `(Evidence N)` citation tags; NEVER truncates; preserves markdown + list indentation
  (normalises 1-space nested bullets to 2 spaces).
- New `UNVERIFIED` validation state (`available: false`) when the validation LLM is
  unreachable. Answer is still delivered, badge reads "Not Verified".
- `/api/chat/query` returns a clear error on `generation_failed`; `/api/rag/ask` returns 503.
- `_translate_response` reuses one translation for `message`/`data.answer` so they cannot
  diverge; translate prompt now forbids Devanagari numeral conversion.
- Frontend `QueryResultCard`: verdict config for UNVERIFIED / LOW_CONFIDENCE, badge derived
  from config, unsupported claims listed, `data-testid` on badge/answer/validation.
NOT_IN_EVIDENCE behaviour, source/page/relevance metadata, EMI/DTI/max-loan/ML untouched.
