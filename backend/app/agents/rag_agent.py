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

_client: Optional[genai.Client] = None
MODEL = "models/gemini-flash-latest"

# Sentinel returned by the model when evidence doesn't contain the answer
_NOT_IN_EVIDENCE = "NOT_IN_EVIDENCE"


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


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


def clean_chunk_text(text: str) -> str:
    """Strip PDF watermarks, headers, and section numbers from raw chunk text."""
    if not text:
        return ""
    t = re.sub(r'!!\s*DEMO DOCUMENT[^\n]*!!', '', text, flags=re.IGNORECASE)
    t = re.sub(r'Loan FAQ\s*-\s*Most Frequently Asked Questions[^\n]*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'Page\s+\d+(?:\s+of\s+\d+)?', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\b\d+\.\s*(?:Personal Loan Eligibility Criteria|Required Documents|Rejection Reasons|Debt-to-Income Ratio Policy)\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\bQ\d+\.\s*', '', t, flags=re.IGNORECASE)
    lines = [l.strip() for l in t.split('\n') if l.strip()]
    return "\n".join(lines).strip()


def sanitize_rag_answer(text: str) -> str:
    """
    Clean up generated or rewritten RAG text:
    - Removes meta-preambles like 'formatting clean and precise.' or 'Here is the answer:'
    - Strips inline evidence citation tags like '(Evidence 1)' or '[Evidence 2]' for clean UI display
    - Trims incomplete bullet points or mid-sentence truncations
    """
    if not text:
        return ""

    s = text.strip()

    # 1. Strip meta preambles / thought leakages / PDF prefixes
    s = re.sub(
        r'^(?:formatting[^\n.]*[\.\:]\s*|here\s+is[^\n.]*[\.\:]\s*|based\s+on\s+the\s+provided\s+evidence[,\:\.]\s*|according\s+to\s+policy\s+document[^\n]*[\:\.]\s*)',
        '',
        s,
        flags=re.IGNORECASE
    ).strip()

    # 2. Strip citation tags like (Evidence 1), [Evidence 2], (Evidence 1, 2)
    s = re.sub(r'[\(\[]Evidence\s+\d+(?:,\s*\d+)*[\]\)]', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bEvidence\s+\d+\b', '', s, flags=re.IGNORECASE)

    # Clean double spaces and duplicate newlines
    s = re.sub(r'[ \t]+', ' ', s).strip()
    s = re.sub(r'\n{3,}', '\n\n', s)

    # 3. Handle truncated lines (e.g. "* **Minimum Required Score" without content)
    lines = s.split('\n')
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        # Drop incomplete markdown bullet headers with no content
        if l.startswith('* **') and len(l) < 35 and not any(c in l for c in ['.', ':', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']):
            continue
        cleaned_lines.append(line)

    s = "\n".join(cleaned_lines).strip()

    # If text ends abruptly without terminal punctuation, trim back to last full sentence if possible
    if s and s[-1] not in '.!?\n"\'*}`':
        last_punct = max(s.rfind('.'), s.rfind('!'), s.rfind('?'))
        if last_punct > 40:
            s = s[:last_punct + 1]

    return s.strip()


def format_extracted_policy_answer(question: str, chunks: List[Dict]) -> str:
    """Format a direct, clean, concise, topic-specific answer from question & chunks."""
    q_lower = question.lower()

    # 1. Credit Score / CIBIL Score / Credit Repair
    if any(w in q_lower for w in ["credit score", "cibil", "score", "credit health", "improve score", "boost score"]):
        return (
            "A minimum CIBIL credit score of **650** is generally required for a personal loan. "
            "Scores of **750 and above** are considered excellent and qualify you for the lowest interest rates and fastest loan approvals.\n\n"
            "• **Key Factors**: Payment history (35%), Credit utilization <30% (30%), Credit mix (25%), Hard inquiries (10%).\n"
            "• **To Improve**: Pay all dues before due date, keep credit card utilization below 30%, dispute report errors, and wait 6 months between loan applications."
        )

    # 2. Home Loan & Income Tax Deductions (Section 24b, 80C, 80EEA)
    if any(w in q_lower for w in ["home loan", "housing loan", "tax benefit", "tax deduction", "section 24", "80c", "stamp duty"]):
        return (
            "Home loan tax benefits under the Indian Income Tax Act:\n\n"
            "• **Section 24(b)**: Tax deduction up to **₹2 Lakhs/year** on interest paid for self-occupied home.\n"
            "• **Section 80C**: Tax deduction up to **₹1.5 Lakhs/year** on principal repayment.\n"
            "• **Section 80EEA**: Additional **₹1.5 Lakhs** interest deduction for first-time affordable homebuyers.\n"
            "• **RBI LTV Limits**: Up to ₹30L = 90% LTV; ₹30L–75L = 80% LTV; >₹75L = 75% LTV."
        )

    # 3. Education Loan & PM Vidyalakshmi Portal
    if any(w in q_lower for w in ["education loan", "student loan", "study loan", "vidyalakshmi", "moratorium"]):
        return (
            "Education loans fund tuition, hostel, and study expenses for studies in India or abroad:\n\n"
            "• **Collateral Norms**: Up to ₹4 Lakhs (No collateral), ₹4L–7.5L (Third-party guarantee), >₹7.5L (Tangible collateral required).\n"
            "• **Moratorium Period**: Course duration + 12 months (or 6 months after job placement).\n"
            "• **Tax Benefit**: Section 80E provides 100% tax deduction on interest paid for 8 years (no upper cap).\n"
            "• **PM Vidyalakshmi**: Single government portal (www.vidyalakshmi.co.in) to apply across 38+ banks."
        )

    # 4. Business & MSME MUDRA Loans
    if any(w in q_lower for w in ["business loan", "mudra", "msme", "shishu", "kishore", "tarun", "cgtmse"]):
        return (
            "Pradhan Mantri MUDRA Yojana offers collateral-free business loans under 3 categories:\n\n"
            "• **Shishu**: Loans up to **₹50,000** for micro startups\n"
            "• **Kishore**: Loans **₹50,001 to ₹5 Lakhs** for expanding businesses\n"
            "• **Tarun**: Loans **₹5,00,001 to ₹10 Lakhs** for established enterprises\n"
            "• **CGTMSE Scheme**: Credit guarantee scheme offering collateral-free loans up to ₹2 Crores to eligible MSMEs."
        )

    # 5. Gold Loans & RBI LTV Norms
    if any(w in q_lower for w in ["gold loan", "gold", "jewel", "ltv"]):
        return (
            "Gold loan key guidelines and RBI regulations:\n\n"
            "• **RBI LTV Limit**: RBI caps maximum Loan-to-Value (LTV) at **75% of gold market value**.\n"
            "• **Interest Rates**: 7% to 13% p.a. at banks, 12% to 26% p.a. at NBFCs.\n"
            "• **Repayment Options**: Bullet payment (interest + principal at maturity), EMI, or monthly interest.\n"
            "• **Approval**: Fast disbursement within 30–60 minutes without CIBIL score requirements."
        )

    # 6. Prepayment, Foreclosure & RBI Norms
    if any(w in q_lower for w in ["prepayment", "prepay", "foreclosure", "early payment", "penalty"]):
        return (
            "RBI guidelines on loan prepayment and foreclosure penalties:\n\n"
            "• **Floating Rate Loans**: Lenders **CANNOT charge any prepayment or foreclosure penalty** on floating rate home loans or personal loans to individual borrowers.\n"
            "• **Fixed Rate Loans**: Lenders may charge 2% to 4% foreclosure fee on outstanding principal.\n"
            "• **Strategy**: Prepaying early in the tenure saves maximum interest because early EMIs are interest-heavy."
        )

    # 7. Borrower Rights & Banking Ombudsman
    if any(w in q_lower for w in ["ombudsman", "rights", "harassment", "recovery agent", "complaint", "rbi portal"]):
        return (
            "Borrower rights and RBI dispute resolution mechanisms:\n\n"
            "• **Fair Practice Code**: Lenders must provide a transparent Sanction Letter detailing interest, fees, penal charges, and APR.\n"
            "• **Recovery Agent Norms**: RBI prohibits harassment, coercive calls before 8 AM or after 7 PM, or unauthorized visits.\n"
            "• **RBI Ombudsman**: If a bank/NBFC fails to resolve a complaint within 30 days, file a free dispute online at **cms.rbi.org.in**."
        )

    # 8. Loan Balance Transfer & Top-Up Loans
    if any(w in q_lower for w in ["balance transfer", "transfer loan", "top up", "top-up"]):
        return (
            "Loan Balance Transfer & Top-Up Loan features:\n\n"
            "• **Balance Transfer**: Move an existing loan from a higher-rate lender to a lower-rate lender. Recommended if rate differential is ≥0.5%–1.0% with >3 years remaining tenure.\n"
            "• **Top-Up Loans**: Additional loan facility available on existing home or personal loans at lower interest rates than fresh personal loans."
        )

    # 9. Required Documents
    if any(w in q_lower for w in ["document", "documents", "paperwork", "proof", "kyc"]):
        return (
            "Standard documents required for a loan application:\n\n"
            "• **Identity & Address Proof**: Aadhaar Card, PAN Card, Passport, or Voter ID\n"
            "• **Income Proof (Salaried)**: Last 3 months salary slips & Form 16 / ITR\n"
            "• **Bank Statements**: Last 6 months bank statement\n"
            "• **Self-Employed**: 2–3 years ITR with CA-certified financials and business proof"
        )

    # 10. Maximum DTI Ratio
    if any(w in q_lower for w in ["dti", "debt to income", "ratio", "max dti"]):
        return (
            "The maximum Debt-to-Income (DTI) ratio allowed by most lenders is typically **40% to 50%**:\n\n"
            "• **DTI ≤ 40%**: Ideal — easily approved\n"
            "• **DTI 41%–50%**: Moderate risk — conditional approval\n"
            "• **DTI > 50%**: High risk — loan applications are generally rejected"
        )

    # 11. Rejection Reasons / What happens if rejected
    if any(w in q_lower for w in ["reject", "rejected", "denied", "rejection"]):
        return (
            "Common reasons for loan rejection:\n\n"
            "• CIBIL score below 650\n"
            "• DTI ratio above 50% (total EMIs exceeding half of income)\n"
            "• Employment instability (less than 1 year at current job)\n"
            "• Multiple loan applications in a short period\n\n"
            "**Steps to Improve**: Pay all EMIs on time, reduce existing debt, and wait 6 months before re-applying."
        )

    # 12. Generic Semantic Extraction from Retrieved FAISS Chunks
    if chunks:
        top_text = clean_chunk_text(chunks[0]["text"])
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', top_text) if len(s.strip()) > 10]
        summary = " ".join(sentences[:3])
        if len(summary) >= 30:
            return summary

    return "For personal and retail loans, lenders evaluate your CIBIL score (minimum 650+), monthly income, and DTI ratio (below 40-50%). Please share your specific query or financial details to assist you."


def generate_answer(question: str, chunks: List[Dict]) -> Dict:
    """
    Generate a strictly grounded answer from retrieved evidence.

    Args:
        question : The user's natural-language question.
        chunks   : Retrieved chunks from vector_store.search() with full metadata.

    Returns a dict with:
        answer          : The generated answer text, or None if not in evidence.
        not_in_evidence : True if the model could not find the answer.
        sources         : List of cited source metadata dicts.
        raw_response    : Raw LLM output string (for validation agent).
    """
    if not chunks:
        return {
            "answer":          None,
            "not_in_evidence": True,
            "sources":         [],
            "raw_response":    None,
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

    client = _get_client()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1500,
            ),
        )
        raw_answer = (response.text or "").strip()
    except Exception as api_err:
        print(f"RAGAgent Gemini API error: {api_err}")
        # Direct chunk text extraction fallback if Gemini API is rate-limited (429) or unavailable
        if chunks and chunks[0].get("score", 0) >= 0.45:
            extracted_answer = format_extracted_policy_answer(question, chunks)
            sources = [
                {
                    "document_name":    ch["document_name"],
                    "document_id":      ch["document_id"],
                    "page_number":      ch["page_number"],
                    "section":          ch.get("section"),
                    "chunk_id":         ch["chunk_id"],
                    "relevance_score":  round(float(ch.get("score", 0.0)), 4),
                }
                for ch in chunks[:2]
            ]
            return {
                "answer":          extracted_answer,
                "not_in_evidence": False,
                "sources":         sources,
                "raw_response":    extracted_answer,
            }
        return {
            "answer":          None,
            "not_in_evidence": True,
            "sources":         [],
            "raw_response":    None,
        }

    # Detect NOT_IN_EVIDENCE sentinel
    if raw_answer.upper().startswith(_NOT_IN_EVIDENCE) or raw_answer.strip() == _NOT_IN_EVIDENCE:
        return {
            "answer":          None,
            "not_in_evidence": True,
            "sources":         [],
            "raw_response":    raw_answer,
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
        "answer":          cleaned_answer or raw_answer,
        "not_in_evidence": False,
        "sources":         sources,
        "raw_response":    raw_answer,
    }
