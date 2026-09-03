from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db import Base

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    application_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=True)

    # Financial Profile
    monthly_income = Column(Float)
    existing_emi = Column(Float, default=0.0)
    loan_amount = Column(Float)
    tenure_months = Column(Integer)
    employment_type = Column(String, default="salaried")
    age = Column(Integer, default=30)
    credit_score = Column(Integer, default=750)
    loan_purpose = Column(String, default="personal")

    # Assessment & Decision Results
    estimated_emi = Column(Float, nullable=True)
    foir_percentage = Column(Float, nullable=True)
    max_eligible_loan = Column(Float, nullable=True)
    dti_ratio = Column(Float, nullable=True)
    eligibility_score = Column(Float, nullable=True)
    risk_probability = Column(Float, nullable=True)
    decision = Column(String)
    reason = Column(String, nullable=True)
    assessment_snapshot = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
