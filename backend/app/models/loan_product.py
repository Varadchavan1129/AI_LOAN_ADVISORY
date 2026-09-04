"""
Loan Product SQLAlchemy Model — Phase 2
Structured database for verified bank/lender loan products.

Each record stores real, sourced product data with provenance
(source_url, last_verified_at, verification_status) so that
rates and terms can be updated independently of application code.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func
from app.db import Base


class LoanProduct(Base):
    __tablename__ = "loan_products"

    product_id = Column(String, primary_key=True, index=True)

    # ── Lender / Bank ─────────────────────────────────────────────────────
    lender_name = Column(String, nullable=False, index=True)
    product_name = Column(String, nullable=False)
    loan_type = Column(String, nullable=False, index=True)  # personal, home, vehicle, education, business

    # ── Interest Rate ─────────────────────────────────────────────────────
    interest_rate_min = Column(Float, nullable=True)   # % p.a. (lower bound of published range)
    interest_rate_max = Column(Float, nullable=True)   # % p.a. (upper bound, null if single rate)
    rate_type = Column(String, default="floating")     # fixed / floating / linked

    # ── Loan Amount ───────────────────────────────────────────────────────
    min_loan_amount = Column(Float, nullable=True)     # ₹
    max_loan_amount = Column(Float, nullable=True)     # ₹

    # ── Tenure ────────────────────────────────────────────────────────────
    min_tenure_months = Column(Integer, nullable=True)
    max_tenure_months = Column(Integer, nullable=True)

    # ── Eligibility ───────────────────────────────────────────────────────
    min_income = Column(Float, nullable=True)          # ₹ per month
    min_credit_score = Column(Integer, nullable=True)  # CIBIL score (null if not officially stated)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    employment_types = Column(JSON, nullable=True)     # ["salaried", "self_employed"] etc.

    # ── Fees ──────────────────────────────────────────────────────────────
    processing_fee_pct = Column(Float, nullable=True)  # % of loan amount (upper bound of stated range)
    processing_fee_flat = Column(Float, nullable=True) # flat fee ₹ if applicable
    processing_fee_description = Column(String, nullable=True)  # e.g. "Up to 2% of loan amount + GST"

    # ── Eligibility Conditions / Notes ────────────────────────────────────
    key_conditions = Column(JSON, nullable=True)       # list of strings

    # ── Provenance & Verification ─────────────────────────────────────────
    source_url = Column(String, nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(
        String, default="unverified"                   # unverified / verified / needs_review / stale
    )
    verification_notes = Column(Text, nullable=True)   # free-text notes on data quality

    # ── Active / Soft-delete ──────────────────────────────────────────────
    is_active = Column(Boolean, default=True)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
