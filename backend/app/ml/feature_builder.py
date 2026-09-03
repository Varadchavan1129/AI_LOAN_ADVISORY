import pandas as pd

# EXACT columns used during training
TRAINING_COLUMNS = [
    "person_age",
    "person_gender",
    "person_education",
    "person_income",
    "person_emp_exp",
    "person_home_ownership",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
    "cb_person_default_on_file",
    "previous_loan_defaults_on_file",
    "credit_score",
    "loan_intent",
    "loan_grade"
]

def map_loan_intent(purpose: str) -> str:
    """Maps free-text loan purpose to ML training categories."""
    p = (purpose or "").lower().strip()
    if any(k in p for k in ["home", "house", "renovat", "property", "repair"]):
        return "HOMEIMPROVEMENT"
    elif any(k in p for k in ["educat", "study", "college", "school", "course", "degree"]):
        return "EDUCATION"
    elif any(k in p for k in ["medic", "health", "hospital", "surgery", "treatment"]):
        return "MEDICAL"
    elif any(k in p for k in ["business", "venture", "startup", "trade", "shop", "msme"]):
        return "VENTURE"
    elif any(k in p for k in ["debt", "consolidat", "refinanc", "card", "payoff"]):
        return "DEBTCONSOLIDATION"
    return "PERSONAL"

def get_loan_grade(credit_score: int) -> str:
    """Maps credit score to loan grade tier."""
    if credit_score >= 780:
        return "A"
    elif credit_score >= 720:
        return "B"
    elif credit_score >= 660:
        return "C"
    elif credit_score >= 600:
        return "D"
    return "E"

def build_ml_features(loan_input):
    """
    Builds a complete ML feature row from structured financial profile.
    Uses real user attributes: age, income, credit_score, loan_intent.
    """
    monthly_income = float(getattr(loan_input, "monthly_income", 50000))
    annual_income = max(1.0, monthly_income * 12)
    loan_amnt = float(getattr(loan_input, "loan_amount", 100000))
    
    age = int(getattr(loan_input, "age", 30) or 30)
    credit_score = int(getattr(loan_input, "credit_score", 750) or 750)
    loan_purpose = str(getattr(loan_input, "loan_purpose", "personal") or "personal")
    annual_rate = float(getattr(loan_input, "annual_rate", None) or 10.5)

    # Derived attributes with safe ranges
    emp_exp = max(1, min(40, age - 22))
    cred_hist_len = max(1, min(30, age - 21))
    default_on_file = "Y" if credit_score < 580 else "N"
    intent = map_loan_intent(loan_purpose)
    grade = get_loan_grade(credit_score)

    data = {
        # ---- DEMOGRAPHICS ----
        "person_age": age,
        "person_gender": "male",
        "person_education": "Bachelor",
        "person_emp_exp": emp_exp,
        "person_home_ownership": "RENT",

        # ---- FINANCIALS ----
        "person_income": annual_income,
        "loan_amnt": loan_amnt,
        "loan_percent_income": min(5.0, loan_amnt / annual_income),
        "loan_int_rate": annual_rate,

        # ---- CREDIT HISTORY ----
        "cb_person_cred_hist_length": cred_hist_len,
        "cb_person_default_on_file": default_on_file,
        "previous_loan_defaults_on_file": default_on_file,
        "credit_score": credit_score,

        # ---- LOAN METADATA ----
        "loan_intent": intent,
        "loan_grade": grade
    }

    # Force column order + completeness
    return pd.DataFrame([[data[col] for col in TRAINING_COLUMNS]],
                        columns=TRAINING_COLUMNS)
