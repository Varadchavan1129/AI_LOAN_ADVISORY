"""
NLU Agent — Phase 1 & 2
Uses Gemini to detect user intent and extract structured financial entities from
natural language. Falls back to regex pattern matching if Gemini is
unavailable or rate-limited.

Gemini is ONLY used for:
  1. Intent classification
  2. Entity extraction
  3. Answering general loan knowledge questions

Gemini is NEVER used for financial calculations.
"""

import os
import re
import json

from google import genai
from google.genai import types
from app.services import llm_text

MODEL = "models/gemini-flash-latest"

def _get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "dummy":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

# ---------------------------------------------------------------------------
# INTENT DETECTION
# ---------------------------------------------------------------------------

_INTENT_PROMPT = """You are a JSON-only financial intent and entity parser for an Indian loan advisory chatbot.

Analyse the user message and extract all available financial profile entities.

INTENTS:
- financial_profile_assessment: User provides their own financial profile details (income, EMI, CIBIL/credit score, loan amount, tenure) to evaluate personal affordability, FOIR, and eligibility. Example: "I earn ₹60,000, have an ₹8,000 EMI, CIBIL 750 and need ₹5 lakh for 3 years".
- eligibility_check: User asks about THEIR OWN personal loan approval chances, typically with personal financial numbers. Examples: "Can I get 5 lakh with 40k income?", "Will I qualify for a personal loan?", "Am I eligible for a home loan?", "Can I get this loan?", "Check my loan eligibility". CRITICAL RULE: Do NOT use eligibility_check if the question asks about rules, criteria, requirements, or policies written IN a document/policy — those are general_question.
- emi_calculation: User asks for a monthly installment calculation. Example: "What is the EMI for 2 lakhs over 2 years at 10%?".
- max_loan_query: User asks for their personal maximum borrowing capacity based on income. Example: "What is the maximum loan I can get with 50k income?".
- dti_query: User asks about their personal debt-to-income or FOIR ratio calculation.
- rejection_reason: User asks why a loan was denied or how to improve their credit profile.
- general_question: Questions about policy content, regulatory rules, document information, definitions, or general loan knowledge. This includes ANY question that references a document or policy ("in this policy", "in this document", "mentioned in", "as per the policy", "according to the document") OR asks about what rules/criteria/requirements/guidelines EXIST in general (not asking about the user's personal eligibility). Examples: "What are the eligibility requirements mentioned in this policy document?", "What are the rules mentioned in this policy?", "What is maximum DTI allowed?", "What documents are required?", "How does CIBIL work?", "What criteria are used for loan approval?", "What are the income requirements for this loan?".

DISAMBIGUATION — eligibility_check vs general_question:
- eligibility_check: The user is asking about THEMSELVES ("Can I...", "Am I...", "Will I...", "Do I qualify...", "Check my...", "My eligibility").
- general_question: The user is asking about what is WRITTEN IN A POLICY/DOCUMENT, or asking about general rules/criteria that exist — NOT about their own personal approval chances.
- If the question mentions "policy", "document", "mentioned in", "as per", "according to", "rules", "criteria" in the context of a document — it is ALWAYS general_question, even if the words "eligible" or "eligibility" appear in the question.

EXTRACTION RULES:
- Convert amounts: "5 lakh" -> 500000, "1.5 lakh" -> 150000, "1 crore" -> 10000000, "50k" -> 50000.
- Convert tenure: "5 years" -> 60 months, "3 years" -> 36 months, "24 months" -> 24.
- Credit Score / CIBIL: Extract as integer (300-900). E.g. "CIBIL 750" -> 750.
- Age: Extract borrower age as integer if mentioned (e.g. "I am 29", "age 35" -> 35).
- Employment Type: Extract as string (e.g. "salaried", "self-employed", "business", "freelance").
- Loan Purpose: Extract purpose if stated (e.g. "home", "renovation", "personal", "car", "education", "business", "medical").
- If entity is not mentioned, use null.

User message: "{message}"

Respond with ONLY valid JSON:
{{
  "intent": "<intent_name>",
  "entities": {{
    "monthly_income": <int or null>,
    "existing_emi": <int or null>,
    "loan_amount": <int or null>,
    "tenure_months": <int or null>,
    "interest_rate": <float or null>,
    "credit_score": <int or null>,
    "age": <int or null>,
    "employment_type": <string or null>,
    "loan_purpose": <string or null>
  }},
  "confidence": <0.0-1.0>
}}"""


# ---------------------------------------------------------------------------
# POLICY/DOCUMENT QUESTION PATTERNS
# These signal that a question is asking about document/policy CONTENT,
# NOT about the user's personal eligibility. Used as a post-LLM safety guard.
# ---------------------------------------------------------------------------

_DOCUMENT_CONTEXT_PHRASES = [
    "in this policy", "in this document", "mentioned in", "as per the policy",
    "as per this policy", "according to the policy", "according to this policy",
    "according to the document", "in the policy", "in the document",
    "in this policy document", "policy document", "policy says", "document says",
    "stated in", "written in", "per the policy", "per this document",
]

_DOCUMENT_INTENT_WORDS = [
    "what are the rules", "what rules", "what are the criteria",
    "what criteria", "what are the requirements", "what requirements",
    "what are the guidelines", "what guidelines", "what are the terms",
    "what terms", "what are the conditions", "what conditions",
    "what does the policy", "what does this policy", "what does the document",
    "explain the policy", "summarize the policy", "what is in the policy",
]


def _is_policy_document_question(message: str) -> bool:
    """
    Returns True if the message is clearly asking about content IN a policy
    or document, rather than asking about the user's personal eligibility.
    Used as a deterministic post-LLM override guard.
    """
    msg = message.lower()
    # Explicit document-context phrases
    if any(phrase in msg for phrase in _DOCUMENT_CONTEXT_PHRASES):
        return True
    # Explicit document-intent question patterns
    if any(phrase in msg for phrase in _DOCUMENT_INTENT_WORDS):
        return True
    return False


def parse_intent(message: str) -> dict:
    """Detect intent and extract financial entities via LLM, with regex fallback."""
    result = llm_text.complete_json(_INTENT_PROMPT.format(message=message))
    if not result or "intent" not in result:
        return _regex_fallback(message)
    if "entities" not in result:
        result["entities"] = _empty_entities()

    # ── Post-LLM safety guard ────────────────────────────────────────────────
    # If Gemini classified this as eligibility_check but the message is clearly
    # asking about a document or policy (not the user's personal eligibility),
    # override the intent to general_question so it takes the RAG path.
    if result.get("intent") == "eligibility_check" and _is_policy_document_question(message):
        result["intent"] = "general_question"
        result["confidence"] = max(result.get("confidence", 0.5), 0.75)

    return result


# ---------------------------------------------------------------------------
# GENERAL QUESTION ANSWERING
# ---------------------------------------------------------------------------

_GENERAL_QA_PROMPT = """You are Tata Mitra, a knowledgeable and helpful loan advisor AI for Indian customers.

Answer the following loan-related question clearly and helpfully.

Guidelines:
- Provide accurate general financial / loan knowledge based on standard Indian banking practices.
- Share typical ranges and general guidelines (e.g. "Most lenders require a credit score above 650-750").
- You MAY use general financial knowledge to give a useful answer.
- Only avoid making up SPECIFIC bank-by-bank policies or guaranteeing loan approvals.
- Mention that exact rates and terms vary by bank when stating specific numbers.
- Keep answer to 3-4 sentences maximum.
- Tone: warm, professional, clear, and genuinely helpful.
- Do NOT deflect or refuse to answer. Always provide useful information.

Question: {message}

Answer:"""


def answer_general_question(message: str) -> str:
    """Use the LLM to answer general loan knowledge questions."""
    answer = llm_text.complete(_GENERAL_QA_PROMPT.format(message=message))
    if answer:
        return answer
    return _fallback_general_answer(message)


def _fallback_general_answer(message: str) -> str:
    m = message.lower()

    if any(w in m for w in ["gold loan", "gold", "ornament", "jewellery", "jewel"]):
        return (
            "A gold loan is a secured loan where you pledge gold jewellery as collateral. "
            "Banks offer up to 75% of gold value (LTV limit set by RBI). "
            "Interest rates range from 7% to 13% at banks; 12-26% at NBFCs like Muthoot/Manappuram. "
            "No CIBIL score required. Disbursed within 30-60 minutes."
        )
    elif any(w in m for w in ["education loan", "student loan", "study loan", "college loan", "vidyalakshmi"]):
        return (
            "Education loans cover tuition, hostel, books, and other study expenses. "
            "Loans up to Rs. 4 lakh need no collateral. Above Rs. 7.5 lakh require tangible security. "
            "Interest rates: 8.15% to 15% p.a. with 0.5% concession for girls. "
            "Repayment starts after course + 12 months (moratorium period). "
            "Interest is tax-deductible under Section 80E."
        )
    elif any(w in m for w in ["home loan", "house loan", "housing loan", "property loan", "mortgage"]):
        return (
            "Home loans are available for purchase, construction, renovation, or extension. "
            "LTV: up to 90% for loans under Rs. 30 lakh; 75% for above Rs. 75 lakh. "
            "Interest rates: 8.5% to 10.5% floating; 9.5% to 12% fixed. "
            "Maximum tenure: 30 years. Tax benefit: Section 24(b) up to Rs. 2 lakh/year on interest."
        )
    elif any(w in m for w in ["credit score", "cibil", "score", "credit report", "creditworthiness"]):
        return (
            "CIBIL score ranges from 300 to 900. Above 750 is considered very good; above 800 is excellent. "
            "Minimum 650 required for personal loans; 700+ for best rates. "
            "Check free at www.cibil.com once per year or via most bank apps. "
            "Improve by: paying EMIs on time, keeping credit card utilisation below 30%, avoiding multiple applications."
        )
    elif any(w in m for w in ["interest rate", "rate of interest", "roi", "% per annum", "interest %"]):
        return (
            "Typical loan interest rates in India: Personal loan 10-24%, Home loan 8.5-10.5%, "
            "Car loan 7-12%, Gold loan 7-13%, Business loan 10-26%, Education loan 8-15% p.a. "
            "Rates depend on CIBIL score, income, lender, and market conditions. "
            "Floating rates change with RBI repo rate; fixed rates remain constant."
        )
    elif any(w in m for w in ["foir", "dti", "debt to income", "obligation"]):
        return (
            "FOIR (Fixed Obligation to Income Ratio) or DTI measures the percentage of your monthly income that goes toward repaying debts. "
            "Most banks prefer a FOIR under 40-50% for loan approvals to ensure you have sufficient disposable income."
        )
    else:
        return (
            "I couldn't reach the AI service just now, so I can't answer that reliably. "
            "Please try again in a moment, or ask me to calculate your EMI, DTI or loan "
            "eligibility — those are computed locally and always available."
        )


# ---------------------------------------------------------------------------
# REGEX FALLBACK
# ---------------------------------------------------------------------------

def _regex_fallback(message: str) -> dict:
    """Keyword + regex intent detection when Gemini is unavailable."""
    msg = message.lower()
    entities = _extract_entities_regex(message)

    intent = "general_question"

    # Multi-attribute profile input
    has_income = entities.get("monthly_income") is not None
    has_amount = entities.get("loan_amount") is not None
    has_cibil  = entities.get("credit_score") is not None
    has_emi    = entities.get("existing_emi") is not None

    # 1. Specific query types first
    if any(phrase in msg for phrase in [
        "what is the maximum dti", "maximum dti ratio allowed", "max dti allowed",
        "maximum dti", "what is dti", "define dti", "explain dti", "dti limit", "dti ratio allowed",
        "vidyalakshmi", "subsidy", "interest subsidy", "who is eligible for", "eligible for interest"
    ]):
        intent = "general_question"
    elif any(w in msg for w in ["policy", "document", "rules", "criteria", "requirements", "guidelines"]):
        intent = "general_question"
    elif any(w in msg for w in [
        "how much loan", "how much can i", "maximum loan", "max loan",
        "how much home loan", "how much personal loan", "how much can i borrow"
    ]):
        intent = "max_loan_query"
    elif any(w in msg for w in [
        "what is my dti", "calculate dti", "my dti", "what is my foir", "my foir", "debt to income ratio", "dti ratio"
    ]):
        intent = "dti_query"
    elif any(w in msg for w in [
        "calculate emi", "what is my emi", "what is the emi", "emi for"
    ]):
        intent = "emi_calculation"
    elif any(w in msg for w in [
        "rejected", "rejection", "why denied", "improve eligibility", "improve score", "boost score"
    ]):
        intent = "rejection_reason"
    elif has_income and (has_amount or has_cibil):
        intent = "financial_profile_assessment"
    elif any(w in msg for w in [
        "eligible", "eligibility", "qualify", "can i get", "will i get", "approve"
    ]):
        # Only classify as eligibility_check if not clearly a policy/document question
        if _is_policy_document_question(message):
            intent = "general_question"
        else:
            intent = "eligibility_check"
    elif any(w in msg for w in [
        "emi", "monthly payment", "monthly installment", "how much per month"
    ]):
        intent = "emi_calculation"
    elif any(w in msg for w in [
        "dti", "foir", "debt to income", "debt-to-income"
    ]):
        intent = "dti_query"

    return {"intent": intent, "entities": entities, "confidence": 0.5}


def _extract_entities_regex(message: str) -> dict:
    """Extract financial values from message using regex patterns."""
    msg = message.lower()
    e = _empty_entities()

    # --- Lakh amounts ---
    for m in re.finditer(r'(?:rs\.?\s*|₹\s*)?([\d.]+)\s*lakh', msg):
        val = int(float(m.group(1)) * 100_000)
        if e["loan_amount"] is None:
            e["loan_amount"] = val

    # --- Crore amounts ---
    for m in re.finditer(r'(?:rs\.?\s*|₹\s*)?([\d.]+)\s*crore', msg):
        e["loan_amount"] = int(float(m.group(1)) * 10_000_000)

    # --- Years → months ---
    m = re.search(r'(\d+)\s*year', msg)
    if m:
        e["tenure_months"] = int(m.group(1)) * 12

    # --- Months ---
    m = re.search(r'(\d+)\s*month', msg)
    if m and e["tenure_months"] is None:
        e["tenure_months"] = int(m.group(1))

    # --- Interest rate % ---
    m = re.search(r'(\d+(?:\.\d+)?)\s*%', message)
    if m:
        e["interest_rate"] = float(m.group(1))

    # --- CIBIL / Credit Score ---
    m_cibil = re.search(r'(?:cibil|credit\s*score|score)[^\d]*(\d{3})\b', msg) or re.search(r'\b(\d{3})\s*(?:cibil|score)', msg)
    if m_cibil:
        c_val = int(m_cibil.group(1))
        if 300 <= c_val <= 900:
            e["credit_score"] = c_val

    # --- Age ---
    m_age = re.search(r'(?:age|aged|i am|i\'m)\s*(\d{2})\b', msg) or re.search(r'\b(\d{2})\s*(?:years?\s*old|yr\s*old)', msg)
    if m_age:
        a_val = int(m_age.group(1))
        if 18 <= a_val <= 80:
            e["age"] = a_val

    # --- Employment Type ---
    if any(k in msg for k in ["salaried", "salary"]):
        e["employment_type"] = "salaried"
    elif any(k in msg for k in ["self employed", "self-employed", "freelance"]):
        e["employment_type"] = "self_employed"
    elif any(k in msg for k in ["business", "businessman", "shopkeeper"]):
        e["employment_type"] = "business"

    # --- Loan Purpose ---
    if any(k in msg for k in ["home", "house", "renovat", "flat", "plot"]):
        e["loan_purpose"] = "home"
    elif any(k in msg for k in ["educat", "study", "college", "mba"]):
        e["loan_purpose"] = "education"
    elif any(k in msg for k in ["car", "bike", "vehicle", "auto"]):
        e["loan_purpose"] = "vehicle"
    elif any(k in msg for k in ["business", "shop", "working capital"]):
        e["loan_purpose"] = "business"
    elif any(k in msg for k in ["medic", "health", "hospital"]):
        e["loan_purpose"] = "medical"
    elif any(k in msg for k in ["personal", "wedding", "travel", "vacation"]):
        e["loan_purpose"] = "personal"

    # --- Monthly income with Lakh / K (e.g. "1.5 lakh income", "earn 1.5 lakh", "60k salary") ---
    m_inc_lakh = re.search(r'(?:earn|income|salary|make)[^\d₹]*([\d.]+)\s*lakh', msg) or re.search(r'([\d.]+)\s*lakh[^\d₹]*(?:income|salary|earn)', msg)
    if m_inc_lakh:
        e["monthly_income"] = int(float(m_inc_lakh.group(1)) * 100_000)

    m_inc_k = re.search(r'(?:earn|income|salary|make)[^\d₹]*(\d+)\s*k\b', msg) or re.search(r'(\d+)\s*k\b[^\d₹]*(?:income|salary|earn)', msg)
    if m_inc_k and e["monthly_income"] is None:
        e["monthly_income"] = int(m_inc_k.group(1)) * 1000

    # Standard Monthly income patterns
    if e["monthly_income"] is None:
        m = re.search(
            r'(?:(?:rs\.?\s*|₹\s*)?([\d,]+)\s*(?:per\s*month\s*)?(?:income|salary|earnings?|earn)|(?:earn|income|salary|make)[^\d₹]*(?:rs\.?\s*|₹\s*)?([\d,]+))',
            msg
        )
        if m:
            raw_val = (m.group(1) or m.group(2)).replace(",", "")
            if raw_val.isdigit():
                e["monthly_income"] = int(raw_val)

    # --- EMI patterns (number before OR after EMI) ---
    m_emi_k = re.search(r'(?:emi|paying|pay)[^\d₹]*(\d+)\s*k\b', msg) or re.search(r'(\d+)\s*k\b[^\d₹]*(?:emi)', msg)
    if m_emi_k:
        e["existing_emi"] = int(m_emi_k.group(1)) * 1000

    if e["existing_emi"] is None:
        m = re.search(
            r'(?:(?:rs\.?\s*|₹\s*)?([\d,]+)\s*(?:existing\s*|current\s*)?emi|(?:emi|existing emi|current emi|paying|pay)[^\d₹]*(?:rs\.?\s*|₹\s*)?([\d,]+))',
            msg
        )
        if m:
            raw_val = (m.group(1) or m.group(2)).replace(",", "")
            if raw_val.isdigit():
                val = int(raw_val)
                if val != e["monthly_income"]:
                    e["existing_emi"] = val

    # --- Plain rupee amounts (fallback for loan amount) ---
    if e["loan_amount"] is None:
        for m in re.finditer(r'(?:rs\.?\s*|₹\s*)([\d,]{4,})', msg):
            val = int(m.group(1).replace(",", ""))
            if val >= 10_000 and val != e["monthly_income"] and val != e["existing_emi"]:
                e["loan_amount"] = val
                break

    return e


def _empty_entities() -> dict:
    return {
        "monthly_income": None,
        "existing_emi":   None,
        "loan_amount":    None,
        "tenure_months":  None,
        "interest_rate":  None,
        "credit_score":   None,
        "age":            None,
        "employment_type": None,
        "loan_purpose":   None,
    }
