import os
from google import genai

# -------------------------------------------------
# GEMINI CONFIGURATION
# -------------------------------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-flash-lite-latest"





class CreditImprovementAgent:
    """
    Credit Improvement & Advisory Agent

    Responsibilities:
    1. Deterministically identify improvement factors (compliance-safe)
    2. Use Gemini LLM ONLY to personalize advice
       - No decision making
       - No guarantees
       - RBI & BFSI compliant
    """

    # =================================================
    # PART 1: DETERMINISTIC IMPROVEMENT FACTORS
    # =================================================
    @staticmethod
    def get_improvement_factors(loan_input, eligibility_result):
        """
        Identifies standardized improvement factors.
        NO LLM usage here.
        """
        factors = []

        if loan_input.monthly_income < 30000:
            factors.append("LOW_INCOME")

        if eligibility_result.dti_ratio > 0.5:
            factors.append("HIGH_DTI")

        if loan_input.loan_amount > loan_input.monthly_income * 10:
            factors.append("HIGH_LOAN_AMOUNT")

        if eligibility_result.risk_probability > 0.6:
            factors.append("HIGH_RISK_PROFILE")

        if not factors:
            factors.append("GENERAL_IMPROVEMENT")

        return factors

    # =================================================
    # PART 2: LLM-BASED PERSONALIZED ADVICE (GEMINI)
    # =================================================
    @staticmethod
    def generate_personalized_advice(factors, loan_input):
        """
        Uses Gemini to generate personalized, empathetic,
        RBI-compliant credit improvement advice as a simple text paragraph.
        """

        prompt = f"""
You are a caring and expert financial advisor in India.
Your client has applied for a loan but faces some challenges.

Context:
- Monthly income: ₹{loan_input.monthly_income}
- Existing EMI: ₹{loan_input.existing_emi}
- Requested loan amount: ₹{loan_input.loan_amount}
- Loan tenure: {loan_input.tenure_months} months
- Challenges identified: {", ".join(factors)}

TASK:
Write a warm, supportive, and personalized advice paragraph (NOT a list).
- Directly reference their income or EMI figures to show you understand their specific situation.
- Explain *why* the rejected/conditional status happened in simple terms.
- Offer 2-3 concrete steps to improve their eligibility for the future.
- Tone: Highly empathetic, encouraging, human-like.
- CONSTRAINT: Do NOT use bullet points or tables. Write as 1-2 natural paragraphs.
- STRICTLY COMPLIANT: No guarantees, no illegal advice.
"""

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"CreditImprovementAgent Error: {e}")
            return "We recommend reducing your current debt obligations and maintaining a healthy credit score to improve future eligibility."
