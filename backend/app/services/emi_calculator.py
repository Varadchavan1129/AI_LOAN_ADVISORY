"""
EMI Calculator Service — Phase 2
All calculations are deterministic Python math.
NO Gemini / LLM is used for any financial calculation.

Formula:  EMI = P * r * (1+r)^n / ((1+r)^n - 1)
  P = principal
  r = monthly interest rate  (annual_rate / 12 / 100)
  n = tenure in months
"""


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> dict:
    """
    Calculate monthly EMI and total cost of loan.

    Args:
        principal:      Loan amount in ₹
        annual_rate:    Annual interest rate as percentage (e.g. 10 for 10%)
        tenure_months:  Loan duration in months

    Returns:
        dict with monthly_emi, total_interest, total_repayment
    """
    monthly_rate = annual_rate / (12 * 100)

    if monthly_rate == 0:
        # Zero-interest loan
        emi = principal / tenure_months
    else:
        factor = (1 + monthly_rate) ** tenure_months
        emi = principal * monthly_rate * factor / (factor - 1)

    total_repayment = round(emi * tenure_months, 2)
    total_interest  = round(total_repayment - principal, 2)

    return {
        "monthly_emi":      round(emi, 2),
        "total_interest":   total_interest,
        "total_repayment":  total_repayment,
        "principal":        round(principal, 2),
        "annual_rate":      annual_rate,
        "tenure_months":    tenure_months,
    }


def calculate_max_loan(
    monthly_income: float,
    existing_emi: float,
    annual_rate: float,
    tenure_months: int,
) -> dict:
    """
    Calculate maximum loan amount a user can safely take.

    Uses the standard 40% DTI rule:
      Max total EMI  = 40% of monthly income
      Available EMI  = Max total EMI - Existing EMI
      Max Loan       = Available EMI * ((1+r)^n - 1) / (r * (1+r)^n)

    Args:
        monthly_income: Monthly gross income in ₹
        existing_emi:   Current monthly EMI obligations in ₹
        annual_rate:    Assumed annual interest rate for new loan (%)
        tenure_months:  Assumed tenure for new loan (months)

    Returns:
        dict with max_loan, available_emi, max_total_emi
    """
    max_total_emi = monthly_income * 0.40          # 40% DTI threshold
    available_emi = max_total_emi - existing_emi

    if available_emi <= 0:
        return {
            "max_loan":      0,
            "available_emi": 0,
            "max_total_emi": round(max_total_emi, 2),
            "annual_rate":   annual_rate,
            "tenure_months": tenure_months,
            "note": "Existing EMI already exceeds the recommended 40% of monthly income.",
        }

    monthly_rate = annual_rate / (12 * 100)

    if monthly_rate == 0:
        max_loan = available_emi * tenure_months
    else:
        factor   = (1 + monthly_rate) ** tenure_months
        max_loan = available_emi * (factor - 1) / (monthly_rate * factor)

    return {
        "max_loan":      round(max_loan, 2),
        "available_emi": round(available_emi, 2),
        "max_total_emi": round(max_total_emi, 2),
        "annual_rate":   annual_rate,
        "tenure_months": tenure_months,
    }


def calculate_dti(
    monthly_income: float,
    existing_emi: float,
    new_loan_amount: float = 0,
    new_tenure_months: int = 60,
    new_annual_rate: float = 10.0,
) -> dict:
    """
    Calculate current and projected DTI ratio.

    Args:
        monthly_income:   Monthly gross income in ₹
        existing_emi:     Current monthly EMI obligations in ₹
        new_loan_amount:  Proposed new loan amount (optional)
        new_tenure_months: Tenure for new loan in months
        new_annual_rate:  Interest rate for new loan (%)

    Returns:
        dict with current_dti, projected_dti, status
    """
    current_dti = existing_emi / monthly_income if monthly_income > 0 else 0

    projected_dti = current_dti
    new_emi = 0.0
    if new_loan_amount > 0:
        emi_result = calculate_emi(new_loan_amount, new_annual_rate, new_tenure_months)
        new_emi    = emi_result["monthly_emi"]
        projected_dti = (existing_emi + new_emi) / monthly_income

    def _status(ratio: float) -> str:
        if ratio <= 0.35:
            return "excellent"
        elif ratio <= 0.43:
            return "good"
        elif ratio <= 0.50:
            return "acceptable"
        else:
            return "high"

    return {
        "current_dti":       round(current_dti, 4),
        "current_dti_pct":   round(current_dti * 100, 1),
        "current_status":    _status(current_dti),
        "projected_dti":     round(projected_dti, 4),
        "projected_dti_pct": round(projected_dti * 100, 1),
        "projected_status":  _status(projected_dti),
        "new_emi":           round(new_emi, 2),
        "existing_emi":      existing_emi,
        "monthly_income":    monthly_income,
    }
