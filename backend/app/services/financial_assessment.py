"""
Financial Assessment Engine — Phase 1
Deterministic Financial Profiling & Affordability Calculations.
Strictly pure Python mathematics. NO LLM arithmetic.

Formulas & Principles:
1. Standard Reducing-Balance EMI:
   EMI = P * r * (1+r)^n / ((1+r)^n - 1)
   where P = principal, r = monthly interest rate, n = tenure in months

2. Fixed Obligation to Income Ratio (FOIR / DTI):
   Current FOIR   = Existing EMI / Monthly Income
   Projected FOIR = (Existing EMI + New EMI) / Monthly Income

3. Max Permissible Total EMI:
   Max EMI = Monthly Income * 50% (Standard Benchmark)
   Available Capacity = max(0, Max EMI - Existing EMI)

4. Max Eligible Loan:
   Max Loan = Available Capacity * ((1+r)^n - 1) / (r * (1+r)^n)
"""

from typing import Dict, Any, List
from app.schemas.loan_input import LoanInput

# Industry standard baseline defaults (Clearly labeled assumptions)
DEFAULT_BASELINE_RATE = 10.5    # % per annum standard benchmark rate
DEFAULT_FOIR_BENCHMARK = 50.0   # % maximum permissible debt-to-income threshold


def compute_deterministic_assessment(loan_input: LoanInput) -> Dict[str, Any]:
    """
    Executes complete deterministic financial profile assessment.
    
    Args:
        loan_input: Structured financial profile (income, existing EMI, loan amount, tenure, etc.)
        
    Returns:
        Structured dictionary of verified mathematical metrics and assumptions.
    """
    income = float(max(0, loan_input.monthly_income))
    existing_emi = float(max(0, loan_input.existing_emi))
    loan_amount = float(max(0, loan_input.loan_amount))
    tenure_months = int(max(1, loan_input.tenure_months))
    annual_rate = float(loan_input.annual_rate if loan_input.annual_rate is not None and loan_input.annual_rate > 0 else DEFAULT_BASELINE_RATE)
    
    # 1. EMI Calculation (Deterministic Amortization)
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        estimated_emi = loan_amount / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months
        estimated_emi = loan_amount * monthly_rate * factor / (factor - 1)
        
    estimated_emi = round(estimated_emi, 2)
    total_repayment = round(estimated_emi * tenure_months, 2)
    total_interest = round(max(0.0, total_repayment - loan_amount), 2)
    
    # 2. Existing and Projected Obligations
    total_monthly_obligations = round(existing_emi + estimated_emi, 2)
    disposable_income = round(income - total_monthly_obligations, 2)
    
    # 3. FOIR (Fixed Obligation to Income Ratio)
    current_foir_ratio = (existing_emi / income) if income > 0 else 1.0
    current_foir_pct = round(current_foir_ratio * 100, 2)
    
    projected_foir_ratio = (total_monthly_obligations / income) if income > 0 else 1.0
    projected_foir_pct = round(projected_foir_ratio * 100, 2)
    
    # 4. Affordability Status classification
    if projected_foir_pct <= 35.0:
        affordability_status = "comfortable"
    elif projected_foir_pct <= 45.0:
        affordability_status = "manageable"
    elif projected_foir_pct <= 50.0:
        affordability_status = "tight"
    else:
        affordability_status = "high_risk"
        
    # 5. Maximum Permissible Loan Capacity
    max_permissible_emi = round(income * (DEFAULT_FOIR_BENCHMARK / 100), 2)
    available_emi_capacity = round(max(0.0, max_permissible_emi - existing_emi), 2)
    
    if available_emi_capacity <= 0 or monthly_rate <= 0:
        estimated_max_loan = 0.0 if available_emi_capacity <= 0 else round(available_emi_capacity * tenure_months, 2)
    else:
        factor = (1 + monthly_rate) ** tenure_months
        estimated_max_loan = round(available_emi_capacity * (factor - 1) / (monthly_rate * factor), 2)
        
    eligibility_gap = round(estimated_max_loan - loan_amount, 2)
    
    # 6. Explicit Calculation Assumptions
    assumptions: List[Dict[str, str]] = [
        {
            "label": "Baseline Interest Rate",
            "description": f"Assumed baseline annual interest rate of {annual_rate}% p.a. for amortization estimation."
        },
        {
            "label": "Benchmark FOIR Cap",
            "description": f"Standard {DEFAULT_FOIR_BENCHMARK}% FOIR limit applied to assess maximum safe monthly debt obligations."
        },
        {
            "label": "Monthly Reducing Balance",
            "description": "Calculations assume standard reducing-balance compounding with monthly installments."
        }
    ]
    
    return {
        "monthly_income": income,
        "existing_emi": existing_emi,
        "requested_loan_amount": loan_amount,
        "tenure_months": tenure_months,
        "employment_type": loan_input.employment_type or "salaried",
        "age": int(loan_input.age or 30),
        "credit_score": int(loan_input.credit_score or 750),
        "loan_purpose": loan_input.loan_purpose or "personal",
        "annual_rate": annual_rate,
        
        "estimated_emi": estimated_emi,
        "total_interest": total_interest,
        "total_repayment": total_repayment,
        "total_monthly_obligations": total_monthly_obligations,
        "disposable_income": disposable_income,
        
        "current_foir_pct": current_foir_pct,
        "projected_foir_pct": projected_foir_pct,
        "foir_benchmark_pct": DEFAULT_FOIR_BENCHMARK,
        "affordability_status": affordability_status,
        
        "max_permissible_emi": max_permissible_emi,
        "available_emi_capacity": available_emi_capacity,
        "estimated_max_loan_eligibility": estimated_max_loan,
        "eligibility_gap": eligibility_gap,
        
        "assumptions": assumptions,
    }
