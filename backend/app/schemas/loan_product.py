"""
Pydantic schemas for Loan Product CRUD operations — Phase 2
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LoanProductCreate(BaseModel):
    """Schema for creating / upserting a loan product."""
    product_id: Optional[str] = None  # auto-generated if omitted

    lender_name: str
    product_name: str
    loan_type: str = Field(..., description="personal, home, vehicle, education, business")

    interest_rate_min: Optional[float] = None
    interest_rate_max: Optional[float] = None
    rate_type: str = "floating"

    min_loan_amount: Optional[float] = None
    max_loan_amount: Optional[float] = None

    min_tenure_months: Optional[int] = None
    max_tenure_months: Optional[int] = None

    min_income: Optional[float] = None
    min_credit_score: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    employment_types: Optional[List[str]] = None

    processing_fee_pct: Optional[float] = None
    processing_fee_flat: Optional[float] = None
    processing_fee_description: Optional[str] = None

    key_conditions: Optional[List[str]] = None

    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    verification_status: str = "unverified"
    verification_notes: Optional[str] = None

    is_active: bool = True


class LoanProductOut(BaseModel):
    """Schema for reading a loan product from the database."""
    product_id: str

    lender_name: str
    product_name: str
    loan_type: str

    interest_rate_min: Optional[float] = None
    interest_rate_max: Optional[float] = None
    rate_type: str = "floating"

    min_loan_amount: Optional[float] = None
    max_loan_amount: Optional[float] = None

    min_tenure_months: Optional[int] = None
    max_tenure_months: Optional[int] = None

    min_income: Optional[float] = None
    min_credit_score: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    employment_types: Optional[List[str]] = None

    processing_fee_pct: Optional[float] = None
    processing_fee_flat: Optional[float] = None
    processing_fee_description: Optional[str] = None

    key_conditions: Optional[List[str]] = None

    source_url: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    verification_status: str = "unverified"
    verification_notes: Optional[str] = None

    is_active: bool = True

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoanProductFilter(BaseModel):
    """Optional filters for querying loan products."""
    loan_type: Optional[str] = None
    lender_name: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    verification_status: Optional[str] = None
    is_active: Optional[bool] = True
