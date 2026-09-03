from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CalculationAssumption(BaseModel):
    label: str
    description: str

class FinancialAssessmentData(BaseModel):
    # Profile echo
    monthly_income: float
    existing_emi: float
    requested_loan_amount: float
    tenure_months: int
    employment_type: str
    age: int
    credit_score: int
    loan_purpose: str
    annual_rate: float

    # Deterministic Assessment Metrics
    estimated_emi: float
    total_interest: float
    total_repayment: float
    total_monthly_obligations: float
    disposable_income: float

    # Affordability / FOIR
    current_foir_pct: float
    projected_foir_pct: float
    foir_benchmark_pct: float
    affordability_status: str  # comfortable, manageable, tight, high_risk
    
    # Loan Eligibility
    max_permissible_emi: float
    available_emi_capacity: float
    estimated_max_loan_eligibility: float
    eligibility_gap: float  # difference between max eligibility and requested amount

    # Estimated Eligibility Decision (advisory only — NOT a lender approval)
    decision: str  # likely_eligible, review_needed, unlikely_eligible
    eligibility_score: float
    risk_probability: float
    reason: Optional[str] = None
    improvement_factors: Optional[List[str]] = None

    # Disclaimer
    disclaimer: Optional[str] = None

    # Transparent Assumptions
    assumptions: List[CalculationAssumption] = []

class EligibilityResult(BaseModel):
    decision: str  # likely_eligible / review_needed / unlikely_eligible
    dti_ratio: float
    eligibility_score: float
    risk_probability: float
    reason: Optional[str] = None
    assessment: Optional[FinancialAssessmentData] = None
