MODEL = "gemini-flash-lite-latest"

def _get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "dummy":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


class CreditImprovementAgent:
    """
    Credit Improvement & Advisory Agent

    Responsibilities:
    1. Deterministically identify improvement factors from the financial assessment
    2. Use Gemini LLM ONLY to personalize advice (no math / decision logic)
    """

    @staticmethod
    def get_improvement_factors(loan_input, eligibility_result):
        """
        Identifies standardized improvement factors deterministically.
        """
        factors = []
        assessment = eligibility_result.assessment

        if loan_input.monthly_income < 30000:
            factors.append("LOW_INCOME")

        if assessment:
            if assessment.projected_foir_pct > 50.0:
                factors.append("HIGH_FOIR_OVERBURDENED")
            elif assessment.current_foir_pct > 35.0:
                factors.append("HIGH_EXISTING_DEBT")

            if assessment.credit_score < 650:
                factors.append("LOW_CIBIL_SCORE")
            elif assessment.credit_score < 720:
                factors.append("AVERAGE_CIBIL_SCORE")

            if assessment.eligibility_gap < 0:
                factors.append("REQUEST_EXCEEDS_CAPACITY")
        else:
            if eligibility_result.dti_ratio > 0.5:
                factors.append("HIGH_DTI")

        if eligibility_result.risk_probability > 0.5:
            factors.append("ELEVATED_RISK_PROFILE")

        if not factors:
            factors.append("GENERAL_IMPROVEMENT")

        return factors

    @staticmethod
    def generate_personalized_advice(factors, loan_input, assessment=None):
        """
        Uses Gemini to generate personalized, empathetic,
        RBI-compliant credit improvement advice.
        """
        assessment_context = ""
        if assessment:
            assessment_context = f"""
- Estimated Monthly EMI: ₹{assessment.estimated_emi:,.0f}
- Current FOIR: {assessment.current_foir_pct:.1f}% | Projected FOIR: {assessment.projected_foir_pct:.1f}%
- Max Safe Loan Capacity: ₹{assessment.estimated_max_loan_eligibility:,.0f}
- Credit Score: {assessment.credit_score}
- Loan Purpose: {assessment.loan_purpose}
"""

        prompt = f"""You are a caring and expert financial advisor in India.
Your client has applied for a loan but needs assistance optimizing their financial profile.

Financial Profile:
- Monthly income: ₹{loan_input.monthly_income:,.0f}
- Existing EMI: ₹{loan_input.existing_emi:,.0f}
- Requested loan: ₹{loan_input.loan_amount:,.0f} for {loan_input.tenure_months} months
{assessment_context}
- Improvement factors: {", ".join(factors)}

TASK:
Write a warm, supportive, and actionable advisory paragraph (1-2 natural paragraphs):
1. Directly acknowledge their figures (income, EMI, requested amount) so they feel heard.
2. Clearly explain the financial principle (e.g. keeping total monthly debt obligations within 40-50% of income, improving CIBIL).
3. Provide 2-3 specific, realistic suggestions (e.g. extending tenure to reduce EMI, consolidating or paying off smaller existing loans, applying with a co-borrower, or borrowing up to the safe capacity of ₹{assessment.estimated_max_loan_eligibility:,.0f} if applicable).
4. Tone: Encouraging, constructive, professional. Do not use bullet points or tables.
"""

        client = _get_genai_client()
        if not client:
            return "To enhance your loan eligibility, we recommend reducing existing short-term debt to lower your FOIR below 40%, considering a longer repayment tenure to decrease your monthly EMI, and consistently paying credit dues on time to boost your CIBIL score."

        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"CreditImprovementAgent Error: {e}")
            return "To enhance your loan eligibility, we recommend reducing existing short-term debt to lower your FOIR below 40%, considering a longer repayment tenure to decrease your monthly EMI, and consistently paying credit dues on time to boost your CIBIL score."
