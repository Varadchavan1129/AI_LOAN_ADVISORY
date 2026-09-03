from pydantic import BaseModel, Field
from typing import Optional

class LoanInput(BaseModel):
    monthly_income: float = Field(..., description="Net monthly income in INR")
    existing_emi: float = Field(default=0.0, description="Current monthly EMI obligations in INR")
    loan_amount: float = Field(..., description="Desired loan amount in INR")
    tenure_months: int = Field(default=60, description="Desired loan tenure in months")
    
    # Extended Financial Profile fields (Phase 1)
    employment_type: Optional[str] = Field(default="salaried", description="Employment type: salaried, self_employed, business, professional, etc.")
    age: Optional[int] = Field(default=30, description="Age of borrower in years")
    credit_score: Optional[int] = Field(default=750, description="CIBIL / Credit score (300 - 900)")
    loan_purpose: Optional[str] = Field(default="personal", description="Loan purpose: personal, home, education, vehicle, business, medical, etc.")
    annual_rate: Optional[float] = Field(default=None, description="Optional custom annual interest rate (%) for baseline calculation")

class FinancialProfileInput(LoanInput):
    """Alias for structured financial profile input."""
    pass
