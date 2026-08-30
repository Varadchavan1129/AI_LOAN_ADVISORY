"""
NLU Agent — Phase 2
Uses Gemini to detect user intent and extract financial entities from
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

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = "models/gemini-flash-latest"

# ---------------------------------------------------------------------------
# INTENT DETECTION
# ---------------------------------------------------------------------------

_INTENT_PROMPT = """You are a JSON-only intent parser for an Indian loan advisory chatbot.

Analyse the user message and extract entities.

INTENTS:
- eligibility_check: Asking about approval chances or status with specific personal values (e.g., "Can I get a loan?", "Will I qualify for 5 lakhs with 50k income?")
- emi_calculation: Asking for monthly payment calculations with specific numbers (e.g., "What is the EMI for 2 lakhs over 2 years at 10%?")
- max_loan_query: Asking for personal borrowing limit with income (e.g., "What is the maximum loan I can get with 50k income?")
- dti_query: Asking about personal debt-to-income ratio calculation with personal financial numbers provided.
- rejection_reason: Asking why a loan was denied or how to improve (e.g., "Why was my loan rejected?", "How to boost my score?")
- general_question: Any general loan-related policy questions, rules, limits, or definitions (e.g., "What is the maximum DTI ratio allowed?", "What documents are required?", "Is Aadhaar mandatory?", "What is DTI?")

EXTRACTION RULES:
- Convert amounts: "5 lakh" -> 500000, "1 crore" -> 10000000.
- Convert time: "5 years" -> 60 months, "2 years" -> 24 months.
- Interest rate: Extract as float (e.g., "10%" -> 10.0).
- Entity Assignment:
    - monthly_income: Only user earnings.
    - existing_emi: Only current debt obligations.
    - loan_amount: Only the principal being requested.
    - If entity is not present, use null.
- DISAMBIGUATION: If the user asks general definitions or policy benchmarks (e.g. "What is the maximum DTI ratio allowed?"), classify as general_question.

User message: "{message}"

Respond with ONLY valid JSON:
{{
  "intent": "<intent_name>",
  "entities": {{
    "monthly_income": <int or null>,
    "existing_emi": <int or null>,
    "loan_amount": <int or null>,
    "tenure_months": <int or null>,
    "interest_rate": <float or null>
  }},
  "confidence": <0.0-1.0>
}}"""


def parse_intent(message: str) -> dict:
    """Detect intent and extract entities using Gemini, with regex fallback."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=_INTENT_PROMPT.format(message=message),
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        result = json.loads(response.text)
        # Ensure entities key exists
        if "entities" not in result:
            result["entities"] = _empty_entities()
        return result
    except Exception as e:
        print(f"NLUAgent parse_intent error: {e}")
        return _regex_fallback(message)


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
    """Use Gemini to answer general loan knowledge questions."""
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=_GENERAL_QA_PROMPT.format(message=message),
        )
        return response.text.strip()
    except Exception as e:
        print(f"NLUAgent answer_general_question error: {e}")
        # Comprehensive topic-aware fallback for all 15 document categories.
        # When Gemini is unavailable, return useful static answers by topic.
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
        elif any(w in m for w in ["loan against property", "lap", "mortgage loan", "property as collateral"]):
            return (
                "Loan Against Property (LAP) lets you borrow against residential or commercial property. "
                "You can get 60-70% of property value as loan. "
                "Interest rates: 9% to 14% p.a. Tenure up to 15-20 years. "
                "Can be used for any purpose: business, medical, education, or debt consolidation."
            )
        elif any(w in m for w in ["balance transfer", "loan transfer", "refinanc", "switch loan"]):
            return (
                "A balance transfer moves your existing loan to a new lender at a lower interest rate. "
                "Saves money when rate difference is 0.5-1% or more and tenure remaining is significant. "
                "Process: Get foreclosure letter → apply to new lender → new lender pays old lender. "
                "Takes 15-30 working days. You can also get a top-up loan during transfer."
            )
        elif any(w in m for w in ["business loan", "msme", "mudra", "startup loan", "working capital"]):
            return (
                "Business loans include term loans, working capital, and MUDRA loans. "
                "MUDRA Shishu: up to Rs. 50,000; Kishore: Rs. 50,000-5 lakh; Tarun: up to Rs. 10 lakh. "
                "Unsecured business loans: 14-26% p.a. Secured: 10-18% p.a. "
                "Minimum business vintage: 2 years. CIBIL score 700+ required for unsecured."
            )
        elif any(w in m for w in ["agriculture", "kisan", "kcc", "crop loan", "farmer loan"]):
            return (
                "Kisan Credit Card (KCC) provides revolving credit for crop cultivation at 7% p.a. "
                "With prompt repayment bonus of 3%, effective rate can be as low as 4% p.a. "
                "KCC up to Rs. 1.6 lakh needs no collateral. "
                "MUDRA loans are also available for agri-allied activities."
            )
        elif any(w in m for w in ["car loan", "vehicle loan", "auto loan", "two wheeler", "bike loan", "scooter"]):
            return (
                "New car loans: 7-12% p.a., up to 90% of ex-showroom price, tenure up to 7 years. "
                "Used car loans: 12-18% p.a., up to 80% of market value. "
                "Two-wheeler loans: 10-16% p.a., min CIBIL 600. "
                "Down payment: minimum 10-20% of on-road price. CIBIL 650+ recommended."
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
        elif any(w in m for w in ["document", "documents", "required", "paperwork", "kyc", "proof"]):
            return (
                "Common documents for most loans: Aadhaar + PAN (KYC), last 3 months salary slips, "
                "Form 16, 6 months bank statements, and 2 passport photos. "
                "For home/LAP loans: Add property documents, sale agreement, approved plan. "
                "For self-employed: ITR for 2-3 years and CA-certified financials."
            )
        elif any(w in m for w in ["reject", "rejected", "denied", "why loan", "improve credit", "improve score", "low score"]):
            return (
                "Common loan rejection reasons: Low CIBIL score (below 650), high DTI ratio (above 50%), "
                "unstable employment (less than 1 year), insufficient income, or incomplete documents. "
                "To improve: pay all EMIs on time, reduce existing debt, avoid multiple applications, "
                "and wait 6 months before reapplying. Consider applying with a co-applicant."
            )
        elif any(w in m for w in ["rbi", "regulation", "rule", "right", "ombudsman", "prepayment", "penalty", "foreclosure"]):
            return (
                "Key RBI borrower rights: No prepayment penalty on floating-rate personal/home loans. "
                "Recovery calls only between 8 AM and 7 PM. All loan terms must be disclosed in writing. "
                "You can approach Banking Ombudsman for disputes at cms.rbi.org.in. "
                "Digital loans must be disbursed directly to your bank account."
            )
        elif any(w in m for w in ["emi", "instalment", "monthly payment", "repayment"]):
            return (
                "EMI = P × r × (1+r)^n / ((1+r)^n - 1) where P=principal, r=monthly rate, n=months. "
                "Use the EMI calculator in this app for exact figures. "
                "Tip: Shorter tenure = higher EMI but less total interest. "
                "Longer tenure = lower EMI but significantly more total interest paid."
            )
        else:
            from app.agents import rag_agent
            return rag_agent.format_extracted_policy_answer(message, [])


# ---------------------------------------------------------------------------
# REGEX FALLBACK
# ---------------------------------------------------------------------------

def _regex_fallback(message: str) -> dict:
    """Keyword + regex intent detection when Gemini is unavailable."""
    msg = message.lower()
    entities = _extract_entities_regex(message)

    intent = "general_question"

    # 1. General DTI, product, portal, tax, and rule questions should be general_question
    if any(phrase in msg for phrase in [
        "what is the maximum dti", "maximum dti ratio allowed", "max dti allowed",
        "maximum dti", "what is dti", "define dti", "explain dti", "dti limit", "dti ratio allowed",
        "vidyalakshmi", "subsidy", "interest subsidy", "who is eligible for", "eligible for interest",
        "eligible for subsidy", "pm vidyalakshmi"
    ]):
        intent = "general_question"
    # 2. Check max_loan_query FIRST for "how much loan", "how much can i get", "how much loan can i get"
    elif any(w in msg for w in [
        "how much loan", "how much can i", "maximum loan", "max loan",
        "how much home loan", "how much personal loan", "how much car loan",
        "how much can i borrow", "how much loan can i get", "maximum amount",
        "how much am i eligible", "maximum i can",
        "how much i can get", "how much i can borrow", "how much loan i can", "how much loan can"
    ]):
        intent = "max_loan_query"
    # 3. Check ELIGIBILITY CHECK for "am i eligible", "qualify", "can i get 5 lakh"
    elif any(w in msg for w in [
        "eligible", "eligibility", "qualify", "can i get", "will i get",
        "approve", "am i eligible", "loan approved"
    ]):
        intent = "eligibility_check"
    # 4. EMI Calculation
    elif any(w in msg for w in [
        "emi", "monthly payment", "monthly installment", "how much per month",
        "monthly repayment", "instalment", "per month"
    ]):
        intent = "emi_calculation"
    # 5. DTI Query
    elif any(w in msg for w in [
        "dti", "debt to income", "debt-to-income", "ratio", "income ratio"
    ]):
        intent = "dti_query"
    # 6. Rejection Reason
    elif any(w in msg for w in [
        "rejected", "rejection", "loan rejected", "why denied", "not approved",
        "improve eligibility", "increase eligibility", "improve my score",
        "improve credit", "credit improve", "how to get loan", "loan denied",
        "why my loan", "loan not approved", "increase cibil", "boost score",
    ]):
        intent = "rejection_reason"

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

    # --- Monthly income with Lakh / K (e.g. "1.5 lakh income", "earn 1.5 lakh", "60k salary") ---
    m_inc_lakh = re.search(r'(?:earn|income|salary|make)[^\d₹]*([\d.]+)\s*lakh', msg) or re.search(r'([\d.]+)\s*lakh[^\d₹]*(?:income|salary|earn)', msg)
    if m_inc_lakh:
        e["monthly_income"] = int(float(m_inc_lakh.group(1)) * 100_000)

    m_inc_k = re.search(r'(?:earn|income|salary|make)[^\d₹]*(\d+)\s*k\b', msg) or re.search(r'(\d+)\s*k\b[^\d₹]*(?:income|salary|earn)', msg)
    if m_inc_k and e["monthly_income"] is None:
        e["monthly_income"] = int(m_inc_k.group(1)) * 1000

    # Standard Monthly income patterns (number before OR after income/salary/earn)
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

    # --- Plain rupee amounts (fallback, only if no lakh/crore found) ---
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
    }
