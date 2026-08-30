from pydantic import BaseModel

class LoanInput(BaseModel):
    monthly_income: int
    existing_emi: int
    loan_amount: int
    tenure_months: int
