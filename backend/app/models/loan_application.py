from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db import Base

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    application_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.session_id"))

    monthly_income = Column(Integer)
    existing_emi = Column(Integer)
    loan_amount = Column(Integer)
    tenure_months = Column(Integer)

    dti_ratio = Column(Float)
    eligibility_score = Column(Float)
    decision = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
