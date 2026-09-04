import os
import json
from google import genai
from google.genai import types
from app.services import llm_text

MODEL = "gemini-flash-lite-latest"

def _get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "dummy":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


class EmpathyAgent:
    """
    LLM-based agent for empathetic, natural-language explanations
    of deterministic financial assessments.

    Gemini is used ONLY to craft clear, supportive explanations.
    All mathematical figures and decisions come strictly from deterministic code.

    IMPORTANT: Language must reflect that this is an ESTIMATE, not a lender approval.
    """

    @staticmethod
    def generate_response(eligibility_result):
        decision = eligibility_result.decision
        score = eligibility_result.eligibility_score
        risk = eligibility_result.risk_probability
        reason = eligibility_result.reason or "overall financial assessment"

        assessment = eligibility_result.assessment
        assessment_summary = ""
        if assessment:
            assessment_summary = f"""
Financial Assessment Metrics:
- Monthly Income: ₹{assessment.monthly_income:,.0f}
- Existing Monthly EMI: ₹{assessment.existing_emi:,.0f} (Current FOIR: {assessment.current_foir_pct:.1f}%)
- Requested Loan: ₹{assessment.requested_loan_amount:,.0f} for {assessment.tenure_months} months
- Estimated Monthly EMI: ₹{assessment.estimated_emi:,.0f}
- Total Monthly Obligations: ₹{assessment.total_monthly_obligations:,.0f} (Projected FOIR: {assessment.projected_foir_pct:.1f}%)
- Net Disposable Income: ₹{assessment.disposable_income:,.0f}/month
- Maximum Estimated Loan Eligibility: ₹{assessment.estimated_max_loan_eligibility:,.0f}
- Affordability Status: {assessment.affordability_status}
- Credit Score: {assessment.credit_score}
- Employment Type: {assessment.employment_type}
- Loan Purpose: {assessment.loan_purpose}
"""

        # Map decision to user-friendly label for the LLM prompt
        decision_labels = {
            "likely_eligible": "POTENTIALLY ELIGIBLE",
            "review_needed": "NEEDS FURTHER REVIEW",
            "unlikely_eligible": "UNLIKELY ELIGIBLE (needs optimization)",
        }
        decision_label = decision_labels.get(decision, decision.upper())

        prompt = f"""You are Tata Mitra, a helpful and empathetic financial advisor AI in India.

You are providing an ESTIMATED financial assessment — NOT a lender approval.

Explain the following estimated eligibility assessment to the customer in natural, clear language:
- Estimated Eligibility: {decision_label}
- Assessment Score: {score}/100 (internal composite score based on FOIR, credit score, income, and risk model)
- ML Risk Estimate: {risk * 100:.0f}%
- Primary Observations: {reason}
{assessment_summary}

CRITICAL LANGUAGE GUIDELINES:
1. NEVER say "approved", "pre-approved", "confirmed", "guaranteed", or "qualify".
2. USE phrases like "appears affordable", "potentially eligible", "your profile suggests", "estimated assessment indicates".
3. "title": A short 3-5 word header (e.g., "Potentially Eligible — Strong Profile", "Further Review Recommended", "Profile Needs Optimization").
4. "message": A 2-3 sentence natural-language explanation. Mention key metrics (estimated EMI, FOIR affordability) clearly. Emphasize this is an estimate, not a final decision.
5. Tone: Warm, professional, transparent, and encouraging — but honest about limitations.
6. Output strictly valid JSON with "title" and "message".
"""

        parsed = llm_text.complete_json(prompt)
        if parsed and parsed.get("message"):
            return parsed
        return EmpathyAgent._fallback_response(decision, assessment)

    @staticmethod
    def _fallback_response(decision: str, assessment) -> dict:
        if decision == "likely_eligible":
            if assessment:
                msg = (
                    f"Based on our estimated assessment, your financial profile appears well-suited for this loan. "
                    f"With a projected monthly EMI of ₹{assessment.estimated_emi:,.0f} and a FOIR of "
                    f"{assessment.projected_foir_pct:.1f}%, the loan appears affordable within standard lending parameters. "
                    f"Final eligibility and rates will be determined by the lender."
                )
            else:
                msg = "Your financial profile appears to meet standard lending criteria based on our estimates. Final eligibility is determined by the lender."
            title = "Potentially Eligible — Strong Profile"
        elif decision == "review_needed":
            if assessment:
                msg = (
                    f"Your estimated assessment suggests this loan may be feasible with some considerations. "
                    f"Your total monthly obligations would be ₹{assessment.total_monthly_obligations:,.0f} "
                    f"({assessment.projected_foir_pct:.1f}% FOIR). Extending the tenure or reducing the loan amount "
                    f"could strengthen your profile. Final terms depend on lender evaluation."
                )
            else:
                msg = "Your profile shows potential but may benefit from adjustments. We recommend reviewing the improvement suggestions below."
            title = "Further Review Recommended"
        else:
            if assessment:
                msg = (
                    f"Based on our estimated analysis, the requested loan may stretch your monthly obligations "
                    f"beyond recommended thresholds. We suggest exploring a longer tenure or a loan amount closer "
                    f"to your estimated capacity of ₹{assessment.estimated_max_loan_eligibility:,.0f}. "
                    f"A lender may still evaluate your application with additional documentation."
                )
            else:
                msg = "Based on the provided information, we recommend reviewing the improvement suggestions to strengthen your financial profile."
            title = "Profile Optimization Suggested"

        return {
            "title": title,
            "message": msg
        }
