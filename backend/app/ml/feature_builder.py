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

def build_ml_features(loan_input):
    """
    Builds a complete ML feature row.
    Uses safe defaults for unavailable attributes.
    """

    annual_income = loan_input.monthly_income * 12

    data = {
        # ---- DEMOGRAPHICS (defaults) ----
        "person_age": 30,
        "person_gender": "male",
        "person_education": "Bachelor",
        "person_emp_exp": 5,
        "person_home_ownership": "RENT",

        # ---- FINANCIALS (from API) ----
        "person_income": annual_income,
        "loan_amnt": loan_input.loan_amount,
        "loan_percent_income": loan_input.loan_amount / annual_income,
        "loan_int_rate": 12.0,

        # ---- CREDIT HISTORY (defaults) ----
        "cb_person_cred_hist_length": 6,
        "cb_person_default_on_file": "N",
        "previous_loan_defaults_on_file": "N",
        "credit_score": 650,

        # ---- LOAN METADATA (defaults) ----
        "loan_intent": "PERSONAL",
        "loan_grade": "B"
    }

    # Force column order + completeness
    return pd.DataFrame([[data[col] for col in TRAINING_COLUMNS]],
                        columns=TRAINING_COLUMNS)
