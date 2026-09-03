import os
import joblib
from app.schemas.loan_input import LoanInput
from app.schemas.eligibility import EligibilityResult, FinancialAssessmentData, CalculationAssumption
from app.ml.feature_builder import build_ml_features
from app.services.financial_assessment import compute_deterministic_assessment

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "risk_model.pkl"
)

# Standard disclaimer — not a lender, not an approval
ASSESSMENT_DISCLAIMER = (
    "This is an estimated assessment based on the information provided and "
    "standard calculation assumptions. Final eligibility, interest rates, and "
    "approval are determined by the lender after full verification."
)


class EligibilityAgent:
    """
    Hybrid Eligibility & Assessment Agent:
    - Pure deterministic financial calculations (EMI, FOIR, Max Loan)
    - Rule-based policy checks (Income, CIBIL, FOIR, Age)
    - ML-assisted default risk estimation (Scikit-Learn pipeline)

    IMPORTANT: This agent produces ESTIMATED eligibility, NOT a lender approval.
    All decisions are advisory-only and clearly labeled as estimates.
    """

    model = joblib.load(MODEL_PATH)

    @staticmethod
    def evaluate(loan_input: LoanInput) -> EligibilityResult:
        # -------------------------------------------------
        # 1. DETERMINISTIC FINANCIAL ASSESSMENT
        # -------------------------------------------------
        assessment_dict = compute_deterministic_assessment(loan_input)

        income = assessment_dict["monthly_income"]
        projected_foir = assessment_dict["projected_foir_pct"]
        credit_score = assessment_dict["credit_score"]
        age = assessment_dict["age"]
        loan_amount = assessment_dict["requested_loan_amount"]
        affordability = assessment_dict["affordability_status"]
        eligibility_gap = assessment_dict["eligibility_gap"]

        # -------------------------------------------------
        # 2. COMPOSITE SCORING (Additive, not "start at 100")
        #
        # The score is built from positive contributions so
        # that a "good" profile earns a realistic ~72-82, not
        # a perfect 100. Only truly exceptional profiles can
        # approach 90+. This avoids the previous problem of
        # trivially awarding 100/100 with no deductions.
        # -------------------------------------------------
        score = 0.0
        reasons = []
        improvement_factors = []

        # ── A. FOIR / Affordability tier (0-35 pts) ──────────
        if projected_foir <= 30.0:
            score += 35          # very comfortable
        elif projected_foir <= 40.0:
            score += 28          # comfortable
        elif projected_foir <= 45.0:
            score += 20          # manageable
        elif projected_foir <= 50.0:
            score += 10          # tight
            reasons.append(f"Projected FOIR ({projected_foir:.1f}%) is in the tight 45-50% bracket")
        else:
            score += 0
            reasons.append(f"Projected FOIR ({projected_foir:.1f}%) exceeds the 50% prudential debt limit")
            improvement_factors.append("HIGH_DTI")

        # ── B. Credit score tier (0-30 pts) ──────────────────
        if credit_score >= 800:
            score += 30
        elif credit_score >= 750:
            score += 25
        elif credit_score >= 720:
            score += 20
        elif credit_score >= 680:
            score += 14
        elif credit_score >= 650:
            score += 8
            reasons.append(f"Credit score ({credit_score}) is in the lower-acceptable range (650-680)")
        else:
            score += 0
            reasons.append(f"Credit score ({credit_score}) is below the recommended 650 threshold")
            improvement_factors.append("LOW_CREDIT_SCORE")

        # ── C. Income adequacy (0-15 pts) ────────────────────
        if income >= 75000:
            score += 15
        elif income >= 50000:
            score += 12
        elif income >= 30000:
            score += 8
        elif income >= 25000:
            score += 5
        else:
            score += 0
            reasons.append("Monthly income is below the standard minimum of ₹25,000")
            improvement_factors.append("LOW_INCOME")

        # ── D. Loan-to-capacity headroom (0-10 pts) ──────────
        if eligibility_gap >= 0:
            gap_ratio = eligibility_gap / max(1, loan_amount)
            if gap_ratio >= 0.5:
                score += 10      # >50% headroom
            elif gap_ratio >= 0.2:
                score += 7
            elif gap_ratio >= 0:
                score += 4
        else:
            score += 0
            reasons.append("Requested loan exceeds estimated maximum eligibility based on income capacity")
            improvement_factors.append("HIGH_LOAN_AMOUNT")

        # ── E. Age within typical lending window (0-5 pts) ───
        if 25 <= age <= 55:
            score += 5
        elif 21 <= age <= 65:
            score += 3
        else:
            score += 0
            reasons.append(f"Age ({age}) is outside typical retail borrowing limits (21-65 years)")
            improvement_factors.append("AGE_RESTRICTION")

        # ── F. Employment type bonus (0-5 pts) ───────────────
        emp = (loan_input.employment_type or "salaried").lower()
        if emp in ("salaried", "professional"):
            score += 5
        elif emp in ("self_employed", "business"):
            score += 3
        else:
            score += 2

        # -------------------------------------------------
        # 3. ML RISK ESTIMATION
        # -------------------------------------------------
        try:
            ml_input = build_ml_features(loan_input)
            risk_probability = float(EligibilityAgent.model.predict_proba(ml_input)[0][1])
        except Exception as e:
            print(f"ML Risk Prediction fallback: {e}")
            risk_probability = 0.35

        # ML risk penalty (subtracts from the built score)
        if risk_probability > 0.6:
            score -= 15
            improvement_factors.append("HIGH_RISK_PROFILE")
        elif risk_probability > 0.4:
            score -= 8
        elif risk_probability > 0.25:
            score -= 3

        score = max(0, min(100, round(score, 1)))

        # -------------------------------------------------
        # 4. ESTIMATED ELIGIBILITY DECISION
        #    (Advisory only — not a lender approval)
        # -------------------------------------------------
        if score >= 65 and projected_foir <= 50.0 and credit_score >= 650:
            decision = "likely_eligible"
        elif score >= 45 and projected_foir <= 55.0:
            decision = "review_needed"
        else:
            decision = "unlikely_eligible"

        if not reasons:
            reasons.append("Financial profile appears within standard lending parameters")

        primary_reason = "; ".join(reasons)

        # Build structured assessment object
        assessment_obj = FinancialAssessmentData(
            monthly_income=assessment_dict["monthly_income"],
            existing_emi=assessment_dict["existing_emi"],
            requested_loan_amount=assessment_dict["requested_loan_amount"],
            tenure_months=assessment_dict["tenure_months"],
            employment_type=assessment_dict["employment_type"],
            age=assessment_dict["age"],
            credit_score=assessment_dict["credit_score"],
            loan_purpose=assessment_dict["loan_purpose"],
            annual_rate=assessment_dict["annual_rate"],

            estimated_emi=assessment_dict["estimated_emi"],
            total_interest=assessment_dict["total_interest"],
            total_repayment=assessment_dict["total_repayment"],
            total_monthly_obligations=assessment_dict["total_monthly_obligations"],
            disposable_income=assessment_dict["disposable_income"],

            current_foir_pct=assessment_dict["current_foir_pct"],
            projected_foir_pct=assessment_dict["projected_foir_pct"],
            foir_benchmark_pct=assessment_dict["foir_benchmark_pct"],
            affordability_status=assessment_dict["affordability_status"],

            max_permissible_emi=assessment_dict["max_permissible_emi"],
            available_emi_capacity=assessment_dict["available_emi_capacity"],
            estimated_max_loan_eligibility=assessment_dict["estimated_max_loan_eligibility"],
            eligibility_gap=assessment_dict["eligibility_gap"],

            decision=decision,
            eligibility_score=float(score),
            risk_probability=round(float(risk_probability), 2),
            reason=primary_reason,
            improvement_factors=improvement_factors,
            disclaimer=ASSESSMENT_DISCLAIMER,

            assumptions=[CalculationAssumption(**a) for a in assessment_dict["assumptions"]],
        )

        return EligibilityResult(
            decision=decision,
            dti_ratio=round(projected_foir / 100, 4),
            eligibility_score=float(score),
            risk_probability=round(float(risk_probability), 2),
            reason=primary_reason,
            assessment=assessment_obj,
        )
