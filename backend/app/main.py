# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

import os
import re
import uuid
import shutil
import logging
from datetime import datetime, timezone

from app.db import engine
from app.models import session, loan_application, agent_event
from app.models import document as _doc_module
from app.models import document_chunk as _chunk_module
from app.db import Base
from sqlalchemy import inspect
from app.schemas.loan_input import LoanInput
from app.schemas.query import QueryRequest
from app.schemas.search import SearchRequest
from app.schemas.rag import RAGRequest
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents import nlu_agent as NLUAgent
from app.agents import rag_agent
from app.agents import validation_agent
from app.services.emi_calculator import calculate_emi, calculate_max_loan, calculate_dti
from app.services.pdf_processor import process_pdf
from app.services import vector_store
from app.db import SessionLocal
from app.models.agent_event import AgentEvent
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("tata_mitra")

# ── Upload storage directory ──────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Security: startup validation ──────────────────────────────────────────────
_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
if not _GEMINI_KEY:
    logger.warning("WARNING: GEMINI_API_KEY is not set. AI features will fail.")

# Admin secret for server-side endpoint protection.
# In production, rotate this via environment variable ADMIN_SECRET_KEY.
# Default to a secure random-looking fallback so the app still starts.
_ADMIN_SECRET = os.getenv("ADMIN_SECRET_KEY", "tata-mitra-admin-2024")

Base.metadata.create_all(bind=engine)

# ── Lifespan: load FAISS index from disk once at startup ───────────────────
@asynccontextmanager
async def _lifespan(app: FastAPI):
    vector_store.load()   # no-op if no index on disk yet
    yield

app = FastAPI(
    title="Multi-Agent Loan Advisor",
    version="2.0",
    lifespan=_lifespan,
    # Disable auto-generated docs in a production-like configuration
    # (re-enable during development by commenting out these two lines)
    # docs_url=None,
    # redoc_url=None,
)

# ── CORS: restrict to localhost only ──────────────────────────────────────────
_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Key"],
)

# ── Admin auth dependency ────────────────────────────────────────────────────
async def require_admin(request: Request):
    """
    Server-side admin guard.
    Checks X-Admin-Key header against ADMIN_SECRET_KEY env var.
    The frontend sends this key from localStorage (set at login).
    """
    key = request.headers.get("X-Admin-Key", "")
    if key != _ADMIN_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: valid admin credentials required."
        )


@app.get("/health")
def health_check():
    """Public health check endpoint."""
    gemini_configured = bool(_GEMINI_KEY)
    return {
        "status": "ok",
        "gemini_configured": gemini_configured,
    }

# NOTE: /debug/tables, /debug/agent-events, /test/eligibility REMOVED for security.
# These were development-only endpoints that exposed internal DB structure
# and raw financial data snapshots without any authentication.

@app.post("/chat/apply-loan")
def apply_loan(data: LoanInput):
    return OrchestratorAgent.process_loan_application(data)

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    db = SessionLocal()
    try:
        # Total Applications
        total_apps = db.query(AgentEvent).filter(AgentEvent.event_type == "eligibility_decision").count()
        
        # Approval/Rejection Counts
        approved = db.query(AgentEvent).filter(
            AgentEvent.event_type == "eligibility_decision",
            AgentEvent.output_snapshot.like('%"decision": "approved"%')
        ).count()
        
        rejected = db.query(AgentEvent).filter(
            AgentEvent.event_type == "eligibility_decision",
            AgentEvent.output_snapshot.like('%"decision": "rejected"%')
        ).count()
        
        conditional = db.query(AgentEvent).filter(
            AgentEvent.event_type == "eligibility_decision",
            AgentEvent.output_snapshot.like('%"decision": "conditional"%')
        ).count()
        
        # Risk Distribution
        # Note: In a real production app, we would query structured fields. 
        # Here we scrape JSON for simplicity or just return raw events for frontend to process if dataset is small.
        # For now, let's return the last 50 events for client-side detailed charts to keep backend simple
        recent_events = db.query(AgentEvent).filter(
            AgentEvent.event_type == "eligibility_decision"
        ).order_by(AgentEvent.timestamp.desc()).limit(50).all()
        
        events_data = [
            {
                "timestamp": e.timestamp.isoformat(),
                "decision": e.output_snapshot.get("decision"),
                "risk_probability": e.output_snapshot.get("risk_probability"),
                "eligibility_score": e.output_snapshot.get("eligibility_score")
            }
            for e in recent_events
        ]

        return {
            "summary": {
                "total": total_apps,
                "approved": approved,
                "rejected": rejected,
                "conditional": conditional
            },
            "recent_events": events_data
        }
    finally:
        db.close()


# ===========================================================================
# PHASE 2 — NATURAL LANGUAGE QUERY ENDPOINT
# ===========================================================================

_DEFAULT_RATE    = 10.0   # % per annum (fallback when user doesn't specify)
_DEFAULT_TENURE  = 60     # months (5 years, fallback)


@app.post("/chat/query")
def handle_natural_query(data: QueryRequest):
    """
    Natural-language loan query handler.

    1. NLU Agent detects intent + extracts entities (Gemini / regex fallback)
    2. Routes to the correct handler:
       - EMI calculation   → deterministic Python math
       - Eligibility check → existing EligibilityAgent (rules + ML)
       - Max loan          → deterministic Python math
       - DTI query         → deterministic Python math
       - General question  → Gemini general QA

    Gemini is NEVER used for any financial calculation.
    """
    # ── Input validation ─────────────────────────────────────────────────────────
    message = data.message.strip()
    if not message:
        return {
            "type":    "missing_info",
            "message": "Please type a question or request.",
            "data":    {"missing": ["message"]},
        }
    if len(message) > 2000:
        return {
            "type":    "error",
            "message": "Your message is too long. Please keep questions under 2000 characters.",
            "data":    None,
        }

    # ── Check Gemini availability ────────────────────────────────────────────────────
    if not _GEMINI_KEY:
        return {
            "type":    "error",
            "message": "AI features are unavailable: GEMINI_API_KEY is not configured. Contact your administrator.",
            "data":    None,
        }

    # ── Check if message is a pure standalone number or monetary figure (e.g. "100000", "₹100,000", "50k") ──
    msg_lower = message.lower().strip()
    clean_digits = re.sub(r'[^\d]', '', msg_lower)
    is_pure_num = (
        clean_digits.isdigit()
        and len(clean_digits) >= 4
        and len(clean_digits) <= 10
        and not any(w in msg_lower for w in ["what", "how", "why", "can", "is", "where", "when", "calc", "emi", "rate"])
    )
    if is_pure_num:
        val = int(clean_digits)
        # Interpret as monthly income response
        max_safe_emi = int(val * 0.50)
        r = (_DEFAULT_RATE / 100) / 12
        n = _DEFAULT_TENURE
        factor = (r * (1 + r)**n) / (((1 + r)**n) - 1)
        est_max_loan = int(max_safe_emi / factor)

        return {
            "type": "max_loan",
            "message": (
                f"Based on a monthly income of **₹{val:,.0f}**:\n\n"
                f"• **Maximum Safe EMI Capacity (50% DTI Limit)**: ₹{max_safe_emi:,.0f}/month\n"
                f"• **Estimated Max Loan Eligibility**: ~₹{est_max_loan:,.0f} (at {_DEFAULT_RATE}% p.a. over {n} months)\n"
                f"• **DTI Allowance**: Total monthly obligations up to ₹{max_safe_emi:,.0f}\n\n"
                f"Would you like to calculate EMI for a specific loan amount or check full eligibility with existing EMIs?"
            ),
            "data": {
                "monthly_income": val,
                "max_safe_emi": max_safe_emi,
                "estimated_max_loan": est_max_loan
            },
        }

    # ── Check if message is a short tenure input (e.g. "60", "60 months", "5 years") ──
    if clean_digits.isdigit() and 1 <= int(clean_digits) <= 360 and len(clean_digits) <= 3 and not any(w in msg_lower for w in ["what", "how", "why", "income", "salary", "lakh"]):
        val_t = int(clean_digits)
        if val_t <= 30 and "month" not in msg_lower:
            val_t = val_t * 12
        return {
            "type": "emi",
            "message": f"Recorded loan tenure: **{val_t} months** ({val_t // 12} years). Please share your loan amount (e.g. ₹5 Lakhs) or monthly income to calculate your EMI or loan eligibility!",
            "data": {"tenure_months": val_t}
        }

    nlu    = NLUAgent.parse_intent(message)
    intent = nlu.get("intent", "general_question")
    ent    = nlu.get("entities", {})

    # ------------------------------------------------------------------
    # EMI CALCULATION
    # ------------------------------------------------------------------
    if intent == "emi_calculation":
        loan_amount   = ent.get("loan_amount")
        tenure_months = ent.get("tenure_months") or _DEFAULT_TENURE
        interest_rate = ent.get("interest_rate") or _DEFAULT_RATE

        if not loan_amount:
            return {
                "type":    "missing_info",
                "message": (
                    "EMI (Equated Monthly Installment) is calculated using: **EMI = P × r × (1+r)^n / ((1+r)^n - 1)**.\n\n"
                    "To calculate your exact EMI, please share your requested loan amount (e.g. ₹5 Lakhs)!"
                ),
                "data":    {"missing": ["loan_amount"]},
            }

        # Validate ranges
        if loan_amount <= 0:
            return {"type": "error", "message": "Loan amount must be greater than zero.", "data": None}
        if tenure_months <= 0 or tenure_months > 360:
            return {"type": "error", "message": "Tenure must be between 1 and 360 months.", "data": None}
        if interest_rate <= 0 or interest_rate > 100:
            return {"type": "error", "message": "Interest rate must be between 0 and 100%.", "data": None}

        try:
            result = calculate_emi(loan_amount, interest_rate, tenure_months)
        except Exception as exc:
            return {"type": "error", "message": f"EMI calculation failed: {exc}", "data": None}

        return {
            "type": "emi",
            "message": (
                f"For a ₹{loan_amount:,.0f} loan at {interest_rate}% p.a. "
                f"over {tenure_months} months: "
                f"Monthly EMI = ₹{result['monthly_emi']:,.2f}, "
                f"Total Interest = ₹{result['total_interest']:,.2f}, "
                f"Total Repayment = ₹{result['total_repayment']:,.2f}."
            ),
            "data": result,
        }

    # ------------------------------------------------------------------
    # ELIGIBILITY CHECK
    # ------------------------------------------------------------------
    elif intent == "eligibility_check":
        monthly_income = ent.get("monthly_income")
        existing_emi   = ent.get("existing_emi") or 0
        loan_amount    = ent.get("loan_amount")
        tenure_months  = ent.get("tenure_months") or _DEFAULT_TENURE

        missing = []
        if not monthly_income: missing.append("monthly income (e.g. ₹60,000)")
        if not loan_amount:    missing.append("loan amount (e.g. ₹5 lakh)")

        if missing:
            return {
                "type":    "missing_info",
                "message": f"To check eligibility I need your {', '.join(missing)}.",
                "data":    {"missing": missing},
            }

        loan_input    = LoanInput(
            monthly_income=monthly_income,
            existing_emi=existing_emi,
            loan_amount=loan_amount,
            tenure_months=tenure_months,
        )
        eligibility = EligibilityAgent.evaluate(loan_input)

        decision_emoji = {"approved": "✅", "conditional": "⚠️", "rejected": "❌"}
        return {
            "type": "eligibility",
            "message": (
                f"{decision_emoji.get(eligibility.decision, '')} "
                f"Your loan is **{eligibility.decision.upper()}** — "
                f"Eligibility Score: {eligibility.eligibility_score}/100, "
                f"DTI Ratio: {eligibility.dti_ratio:.0%}, "
                f"Risk: {eligibility.risk_probability:.0%}."
                + (f" Reason: {eligibility.reason}." if eligibility.reason else "")
            ),
            "data": {
                "decision":         eligibility.decision,
                "eligibility_score": eligibility.eligibility_score,
                "risk_probability": eligibility.risk_probability,
                "dti_ratio":        eligibility.dti_ratio,
                "reason":           eligibility.reason,
            },
        }

    # ------------------------------------------------------------------
    # MAX LOAN QUERY
    # ------------------------------------------------------------------
    elif intent == "max_loan_query":
        monthly_income = ent.get("monthly_income")
        existing_emi   = ent.get("existing_emi") or 0
        interest_rate  = ent.get("interest_rate") or _DEFAULT_RATE
        tenure_months  = ent.get("tenure_months") or _DEFAULT_TENURE

        if not monthly_income:
            return {
                "type":    "max_loan",
                "message": (
                    "The maximum loan amount you can get depends on your monthly income, existing EMIs, tenure, and interest rate. "
                    "Lenders generally cap your total monthly EMIs at **40% to 50%** of your net monthly income.\n\n"
                    "• **Personal Loans**: Typically up to **₹40–₹50 Lakhs** based on income profile.\n"
                    "• **Home Loans**: Up to **75%–90%** of property value.\n\n"
                    "To calculate your specific maximum loan capacity, please share your monthly income (e.g. ₹60,000)!"
                ),
                "data":    {"missing": ["monthly_income"]},
            }

        result = calculate_max_loan(monthly_income, existing_emi, interest_rate, tenure_months)
        return {
            "type": "max_loan",
            "message": (
                f"Based on your income of ₹{monthly_income:,.0f} and existing EMI of ₹{existing_emi:,.0f}, "
                f"you can borrow up to ₹{result['max_loan']:,.0f} "
                f"at {interest_rate}% p.a. over {tenure_months} months. "
                f"(Available EMI capacity: ₹{result['available_emi']:,.0f}/month)"
            ),
            "data": result,
        }

    # ------------------------------------------------------------------
    # DTI QUERY
    # ------------------------------------------------------------------
    elif intent == "dti_query":
        monthly_income = ent.get("monthly_income")
        existing_emi   = ent.get("existing_emi") or 0
        loan_amount    = ent.get("loan_amount") or 0
        tenure_months  = ent.get("tenure_months") or _DEFAULT_TENURE
        interest_rate  = ent.get("interest_rate") or _DEFAULT_RATE

        if not monthly_income:
            return {
                "type":    "dti",
                "message": (
                    "The maximum Debt-to-Income (DTI) ratio allowed by most banks and financial institutions is typically **40% to 50%**. "
                    "A lower DTI ratio indicates a lower risk profile to lenders.\n\n"
                    "• **DTI ≤ 40%**: Excellent — easily approved for loans\n"
                    "• **DTI 41%–50%**: Moderate risk — conditional approval\n"
                    "• **DTI > 50%**: High risk — loan applications are generally rejected\n\n"
                    "To calculate your personal DTI ratio, please share your monthly income and any existing EMIs!"
                ),
                "data":    {"missing": ["monthly_income"]},
            }

        result = calculate_dti(
            monthly_income, existing_emi,
            loan_amount, tenure_months, interest_rate
        )
        return {
            "type": "dti",
            "message": (
                f"Your current DTI is {result['current_dti_pct']}% ({result['current_status']}). "
                + (
                    f"With the new loan, it would be {result['projected_dti_pct']}% ({result['projected_status']}). "
                    if loan_amount else ""
                )
                + "Lenders generally prefer DTI below 40-43%."
            ),
            "data": result,
        }

    # ------------------------------------------------------------------
    # REJECTION REASON / POLICY QUESTION / GENERAL QUESTION
    # Routes: general_question + rejection_reason both go through RAG
    # first, then fall back to Gemini general QA if not in documents.
    # ------------------------------------------------------------------
    else:
        # Step 1: Try RAG if any documents are indexed
        stats = vector_store.get_stats()
        if stats["total_chunks"] > 0:
            try:
                search_result   = vector_store.search(message, top_k=5)
                # Lowered threshold: Gemini embeddings with FAISS dot-product
                # produce scores typically in 0.40–0.65 for relevant content.
                relevant_chunks = [c for c in search_result["results"] if c["score"] >= 0.45]

                if relevant_chunks:
                    gen_result  = rag_agent.generate_answer(message, relevant_chunks)

                    if not gen_result["not_in_evidence"] and gen_result["answer"]:
                        val = validation_agent.validate_answer(
                            message, gen_result["answer"], relevant_chunks
                        )
                        verdict = val["verdict"]

                        ans_text = rag_agent.sanitize_rag_answer(gen_result["answer"])

                        if verdict == "SUPPORTED":
                            return {
                                "type":    "policy",
                                "message": ans_text,
                                "data": {
                                    "answer":        ans_text,
                                    "sources":       gen_result["sources"],
                                    "support_level": verdict,
                                    "is_verified":   True,
                                    "validation":    val,
                                },
                            }

                        elif verdict == "PARTIALLY_SUPPORTED":
                            unsupported = val.get("unsupported_claims", [])
                            final_ans   = (
                                validation_agent.rewrite_for_partial_support(
                                    message, gen_result["answer"],
                                    relevant_chunks, unsupported
                                )
                                if unsupported else ans_text
                            )
                            final_ans = rag_agent.sanitize_rag_answer(final_ans)
                            return {
                                "type":    "policy",
                                "message": final_ans,
                                "data": {
                                    "answer":        final_ans,
                                    "sources":       gen_result["sources"],
                                    "support_level": verdict,
                                    "is_verified":   False,
                                    "validation":    val,
                                },
                            }

                        else:
                            return {
                                "type":    "policy",
                                "message": ans_text,
                                "data": {
                                    "answer":        ans_text,
                                    "sources":       gen_result["sources"],
                                    "support_level": verdict,
                                    "is_verified":   False,
                                    "validation":    val,
                                },
                            }

                else:
                    # Best-effort RAG: only attempt if top result has at least 0.35 similarity.
                    # Prevents unrelated queries from pulling random PDF chunks.
                    all_results = search_result.get("results", [])
                    if all_results and all_results[0].get("score", 0) >= 0.35:
                        best_effort_chunks = all_results[:3]
                        gen_result = rag_agent.generate_answer(message, best_effort_chunks)
                        if not gen_result["not_in_evidence"] and gen_result["answer"]:
                            be_ans = rag_agent.sanitize_rag_answer(gen_result["answer"])
                            return {
                                "type":    "policy",
                                "message": be_ans,
                                "data": {
                                    "answer":        be_ans,
                                    "sources":       gen_result["sources"],
                                    "support_level": "LOW_CONFIDENCE",
                                    "is_verified":   False,
                                },
                            }
            except Exception as rag_exc:
                print(f"RAG routing error (falling back to general): {rag_exc}")

        # Step 2: Fallback — Gemini general answer
        answer = NLUAgent.answer_general_question(message)
        return {
            "type":    "general",
            "message": answer,
            "data":    None,
        }


# ===========================================================================
# PHASE 3 — DOCUMENT MANAGEMENT ENDPOINTS
# ===========================================================================

_ALLOWED_TYPES = {"application/pdf", "application/x-pdf"}
_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@app.post("/admin/documents/upload")
async def upload_document(file: UploadFile = File(...), _: None = Depends(require_admin)):
    """
    Upload a PDF document.
    Stores the file and creates a 'pending' document record.
    Processing is triggered separately via /admin/documents/{id}/process.
    """
    # ── Validate file type (MIME + extension) ────────────────────────────────────
    if file.content_type not in _ALLOWED_TYPES and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # ── Sanitize filename to prevent path traversal ──────────────────────────
    raw_name  = file.filename or "upload.pdf"
    safe_name = os.path.basename(raw_name).replace("..", "").strip() or "upload.pdf"

    # ── Read and size-check ─────────────────────────────────────────────────
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB limit.")

    # ── Magic byte check: real PDFs start with %PDF- ───────────────────────────
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="File is not a valid PDF (missing PDF header). "
                   "Ensure the file is a real PDF, not a renamed text or image file."
        )

    # ── Save to disk ────────────────────────────────────────────────────────
    doc_id      = str(uuid.uuid4())
    stored_name = f"{doc_id}.pdf"
    filepath    = os.path.join(UPLOAD_DIR, stored_name)

    with open(filepath, "wb") as f:
        f.write(content)

    # ── Create DB record ──────────────────────────────────────────────────────────────
    db = SessionLocal()
    try:
        doc = Document(
            id=doc_id,
            original_name=safe_name,
            stored_name=stored_name,
            status="pending",
            file_size=len(content),
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return {
            "id":            doc.id,
            "original_name": doc.original_name,
            "status":        doc.status,
            "file_size":     doc.file_size,
            "message":       "File uploaded. Use /admin/documents/{id}/process to index it.",
        }
    finally:
        db.close()


@app.get("/admin/documents")
def list_documents(_: None = Depends(require_admin)):
    """List all uploaded documents with their status."""
    db = SessionLocal()
    try:
        docs = db.query(Document).order_by(Document.uploaded_at.desc()).all()
        return {
            "total": len(docs),
            "documents": [
                {
                    "id":            d.id,
                    "original_name": d.original_name,
                    "status":        d.status,
                    "page_count":    d.page_count,
                    "chunk_count":   d.chunk_count,
                    "file_size":     d.file_size,
                    "error_message": d.error_message,
                    "uploaded_at":   d.uploaded_at.isoformat() if d.uploaded_at else None,
                    "processed_at":  d.processed_at.isoformat() if d.processed_at else None,
                }
                for d in docs
            ],
        }
    finally:
        db.close()


@app.post("/admin/documents/{doc_id}/process")
def process_document(doc_id: str, _: None = Depends(require_admin)):
    """
    Run the full PDF processing pipeline on an uploaded document:
    extract → clean → chunk → store chunks in DB.
    """
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        if doc.status == "processing":
            return {"message": "Already processing. Please wait.", "status": "processing"}

        # Mark as processing
        doc.status = "processing"
        doc.error_message = None
        db.commit()

        filepath = os.path.join(UPLOAD_DIR, doc.stored_name)

        try:
            result = process_pdf(filepath, doc.id, doc.original_name)
        except (ValueError, RuntimeError) as exc:
            doc.status        = "failed"
            doc.error_message = str(exc)
            db.commit()
            return {
                "status":        "failed",
                "error_message": str(exc),
            }

        # ── Delete old chunks if reprocessing ──────────────────────────────
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()

        # ── Save new chunks ────────────────────────────────────────────────
        for ch in result["chunks"]:
            chunk = DocumentChunk(
                id=ch["chunk_id"],
                document_id=ch["document_id"],
                document_name=ch["document_name"],
                page_number=ch["page_number"],
                chunk_index=ch["chunk_index"],
                section=ch.get("section"),
                text=ch["text"],
                char_count=ch["char_count"],
            )
            db.add(chunk)

        # ── Update document record ─────────────────────────────────────────
        doc.status       = "indexed"
        doc.page_count   = result["page_count"]
        doc.chunk_count  = result["chunk_count"]
        doc.processed_at = datetime.now(timezone.utc)
        db.commit()

        # ── Phase 4: embed chunks into vector store ───────────────────────
        embed_warnings = []
        try:
            added = vector_store.add_document(doc.id, doc.original_name, result["chunks"])
            print(f"Vector store: embedded {added} chunks for '{doc.original_name}'")
        except Exception as embed_exc:
            embed_warnings.append(f"Embedding warning: {embed_exc}")
            print(f"Vector store embed error: {embed_exc}")

        return {
            "status":      "indexed",
            "page_count":  result["page_count"],
            "chunk_count": result["chunk_count"],
            "warnings":    result.get("warnings", []) + embed_warnings,
            "message":     f"Successfully processed and embedded {result['chunk_count']} chunks from {result['page_count']} pages.",
        }
    finally:
        db.close()


@app.get("/admin/documents/{doc_id}/status")
def get_document_status(doc_id: str, _: None = Depends(require_admin)):
    """Get current processing status of a document."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")
        return {
            "id":            doc.id,
            "original_name": doc.original_name,
            "status":        doc.status,
            "page_count":    doc.page_count,
            "chunk_count":   doc.chunk_count,
            "error_message": doc.error_message,
            "processed_at":  doc.processed_at.isoformat() if doc.processed_at else None,
        }
    finally:
        db.close()


@app.get("/admin/documents/{doc_id}/chunks")
def get_document_chunks(doc_id: str, page: int = 1, page_size: int = 10, _: None = Depends(require_admin)):
    """List chunks for a document with pagination."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        total  = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).count()
        offset = (page - 1) * page_size
        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == doc_id)
            .order_by(DocumentChunk.chunk_index)
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {
            "document_id":   doc_id,
            "document_name": doc.original_name,
            "total_chunks":  total,
            "page":          page,
            "page_size":     page_size,
            "chunks": [
                {
                    "id":          ch.id,
                    "page_number": ch.page_number,
                    "chunk_index": ch.chunk_index,
                    "section":     ch.section,
                    "char_count":  ch.char_count,
                    "text":        ch.text[:300] + "..." if len(ch.text) > 300 else ch.text,
                }
                for ch in chunks
            ],
        }
    finally:
        db.close()


@app.delete("/admin/documents/{doc_id}")
def delete_document(doc_id: str, _: None = Depends(require_admin)):
    """Delete a document: removes DB record, all chunks, file on disk, and vector index entries."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        doc_name = doc.original_name

        # Delete chunks from DB
        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).delete()

        # Delete file from disk
        filepath = os.path.join(UPLOAD_DIR, doc.stored_name)
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete record from DB
        db.delete(doc)
        db.commit()

        # Phase 4: Remove from vector store
        try:
            removed = vector_store.remove_document(doc_id)
            print(f"Vector store: removed {removed} chunks for '{doc_name}'")
        except Exception as ve:
            print(f"Vector store removal warning: {ve}")

        return {"message": f"Document '{doc_name}' deleted successfully."}
    finally:
        db.close()


# ===========================================================================
# PHASE 4 — SEMANTIC SEARCH ENDPOINTS
# ===========================================================================

@app.post("/search")
def semantic_search(data: SearchRequest):
    """
    Semantic search across all indexed documents using FAISS + Gemini embeddings.

    Flow:
      1. Embed query with Gemini text-embedding-004
      2. Cosine similarity search in local FAISS index
      3. Return top-K chunks with document name, page number, section, score

    The FAISS index is loaded from disk at startup — no re-embedding on restart.
    """
    if not data.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = vector_store.search(
        query=data.query,
        top_k=data.top_k,
        filter_doc_id=data.filter_doc_id,
    )
    return {
        "query":         data.query,
        "top_k":         data.top_k,
        "filter_doc_id": data.filter_doc_id,
        **result,
    }


@app.get("/search/stats")
def search_stats():
    """Return vector store statistics: total chunks, documents indexed."""
    return vector_store.get_stats()


# ===========================================================================
# PHASE 5 — RAG: SOURCE-BACKED ANSWERS WITH VALIDATION
# ===========================================================================

# Minimum cosine similarity for a chunk to be considered relevant evidence.
# Gemini embeddings with FAISS dot-product score relevant chunks in 0.40–0.65 range.
_MIN_RELEVANCE_DEFAULT = 0.45

_FALLBACK_ANSWER = (
    "I couldn't verify this information from the available policy documents. "
    "Please consult an official bank representative or provide relevant policy documents."
)


@app.post("/rag/ask")
def rag_ask(data: RAGRequest):
    """
    Full Phase 5 RAG pipeline:

    Step 1 — Retrieve: FAISS semantic search returns top-K evidence chunks.
    Step 2 — Generate: Gemini produces answer grounded ONLY in the evidence.
    Step 3 — Validate: A second Gemini call fact-checks the generated answer.
    Step 4 — Rewrite:  If PARTIALLY_SUPPORTED, strip unsupported claims.

    If evidence is absent or the answer is UNSUPPORTED, a safe fallback is returned.
    """
    question = (data.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    min_relevance = data.min_relevance if data.min_relevance is not None else _MIN_RELEVANCE_DEFAULT

    # ── Step 1: Retrieve relevant evidence ────────────────────────────────
    search_result = vector_store.search(
        query=question,
        top_k=data.top_k,
        filter_doc_id=data.filter_doc_id,
    )
    all_chunks = search_result.get("results", [])

    # Filter by relevance threshold
    relevant_chunks = [c for c in all_chunks if c["score"] >= min_relevance]

    # Build evidence preview (always returned for transparency)
    top_evidence = [
        {
            "document_name": c["document_name"],
            "page_number":   c["page_number"],
            "section":       c.get("section"),
            "score":         round(c["score"], 4),
            "text_preview":  c["text"][:200] + "..." if len(c["text"]) > 200 else c["text"],
        }
        for c in all_chunks[:3]
    ]

    if not relevant_chunks:
        return {
            "question":         question,
            "answer":           _FALLBACK_ANSWER,
            "is_verified":      False,
            "support_level":    "UNSUPPORTED",
            "sources":          [],
            "validation": {
                "verdict":            "UNSUPPORTED",
                "reasoning":          "No evidence with sufficient relevance (>= "
                                      f"{min_relevance:.0%}) found in indexed documents.",
                "unsupported_claims": [],
            },
            "retrieved_chunks": len(all_chunks),
            "top_evidence":     top_evidence,
        }

    # ── Step 2: Generate grounded answer ────────────────────────────────
    gen_result = rag_agent.generate_answer(question, relevant_chunks)

    if gen_result["not_in_evidence"] or not gen_result["answer"]:
        return {
            "question":         question,
            "answer":           _FALLBACK_ANSWER,
            "is_verified":      False,
            "support_level":    "UNSUPPORTED",
            "sources":          [],
            "validation": {
                "verdict":            "UNSUPPORTED",
                "reasoning":          "The retrieved evidence does not contain the answer to this question.",
                "unsupported_claims": [],
            },
            "retrieved_chunks": len(relevant_chunks),
            "top_evidence":     top_evidence,
        }

    candidate_answer = gen_result["answer"]
    candidate_sources = gen_result["sources"]

    # ── Step 3: Validate the generated answer ────────────────────────────
    validation_result = validation_agent.validate_answer(
        question=question,
        answer=candidate_answer,
        chunks=relevant_chunks,
    )
    verdict = validation_result["verdict"]

    # ── Step 4: Handle by verdict ───────────────────────────────────────
    if verdict == "SUPPORTED":
        final_answer  = candidate_answer
        is_verified   = True
        final_sources = candidate_sources

    elif verdict == "PARTIALLY_SUPPORTED":
        # Rewrite to strip unsupported claims
        unsupported_claims = validation_result.get("unsupported_claims", [])
        if unsupported_claims:
            final_answer = validation_agent.rewrite_for_partial_support(
                question=question,
                answer=candidate_answer,
                chunks=relevant_chunks,
                unsupported_claims=unsupported_claims,
            )
        else:
            final_answer = candidate_answer
        is_verified   = False
        final_sources = candidate_sources

    else:  # UNSUPPORTED
        final_answer  = _FALLBACK_ANSWER
        is_verified   = False
        final_sources = []

    return {
        "question":         question,
        "answer":           final_answer,
        "is_verified":      is_verified,
        "support_level":    verdict,
        "sources":          final_sources,
        "validation":       validation_result,
        "retrieved_chunks": len(relevant_chunks),
        "top_evidence":     top_evidence,
    }
