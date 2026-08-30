import os
import joblib
from app.schemas.loan_input import LoanInput
from app.schemas.eligibility import EligibilityResult
from app.ml.feature_builder import build_ml_features

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ml",
    "risk_model.pkl"
)


class EligibilityAgent:
    """
    Hybrid Eligibility Agent:
    - Rule-based policy checks
    - ML-assisted risk estimation
    """

    model = joblib.load(MODEL_PATH)

    @staticmethod
    def evaluate(loan_input: LoanInput) -> EligibilityResult:
        # -------------------------
        # RULE-BASED CALCULATIONS
        # -------------------------
        new_emi = loan_input.loan_amount / loan_input.tenure_months
        total_emi = loan_input.existing_emi + new_emi
        dti_ratio = total_emi / loan_input.monthly_income

        score = 100
        reason = None

        if loan_input.monthly_income < 25000:
            score -= 40
            reason = "Low income"

        if dti_ratio > 0.5:
            score -= 40
            reason = "High EMI burden"

        if loan_input.loan_amount > loan_input.monthly_income * 10:
            score -= 20
            reason = "Loan amount too high"

        # -------------------------
        # ML RISK ESTIMATION
        # -------------------------
        ml_input = build_ml_features(loan_input)
        risk_probability = EligibilityAgent.model.predict_proba(ml_input)[0][1]

        if risk_probability > 0.6:
            score -= 30
        elif risk_probability > 0.4:
            score -= 15

        # -------------------------
        # FINAL DECISION
        # -------------------------
        if score >= 70:
            decision = "approved"
        elif score >= 50:
            decision = "conditional"
        else:
            decision = "rejected"

        return EligibilityResult(
            decision=decision,
            dti_ratio=round(dti_ratio, 2),
            eligibility_score=score,
            risk_probability=round(float(risk_probability), 2),
            reason=reason
        )
