"""
FastAPI HTTP Endpoints Integration Test for Phase 1
"""

import os
import sys

# Ensure UTF-8 stdout on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_financial_profile_assess():
    print("\n--- 1. Testing POST /api/financial-profile/assess ---")
    payload = {
        "monthly_income": 70000,
        "existing_emi": 5000,
        "loan_amount": 600000,
        "tenure_months": 48,
        "employment_type": "salaried",
        "age": 32,
        "credit_score": 780,
        "loan_purpose": "home"
    }
    response = client.post("/api/financial-profile/assess", json=payload)
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    print("Response status:", data.get("status"))
    print("Response title:", data.get("title"))
    print("Assessment EMI:", data.get("assessment", {}).get("estimated_emi"))
    print("Assessment FOIR:", data.get("assessment", {}).get("projected_foir_pct"))
    assert data.get("status") == "approved"
    assert data.get("assessment", {}).get("estimated_emi") > 0
    assert len(data.get("assessment", {}).get("assumptions", [])) >= 3
    print("✓ POST /api/financial-profile/assess PASSED!")


def test_chat_query_natural_language_assessment():
    print("\n--- 2. Testing POST /chat/query with Natural Language Profile ---")
    nl_query = "I earn ₹60,000, have an ₹8,000 EMI, CIBIL 750 and need ₹5 lakh for 3 years."
    response = client.post("/chat/query", json={"message": nl_query})
    assert response.status_code == 200, f"Failed: {response.text}"
    data = response.json()
    print("Query Response Type:", data.get("type"))
    print("Query Title:", data.get("title"))
    print("Query Message:", data.get("message"))
    print("Data EMI:", data.get("data", {}).get("estimated_emi"))
    print("Data FOIR:", data.get("data", {}).get("projected_foir_pct"))
    assert data.get("type") == "assessment"
    assert data.get("data", {}).get("estimated_emi") > 0
    assert data.get("profile", {}).get("credit_score") == 750
    print("✓ Natural Language Profile Assessment via /chat/query PASSED!")


def test_chat_query_backward_compatibility():
    print("\n--- 3. Testing Backward Compatibility of /chat/query (EMI, Max Loan, DTI) ---")
    
    # EMI Query
    emi_res = client.post("/chat/query", json={"message": "What is the EMI for 3 lakh for 2 years at 10%?"})
    assert emi_res.status_code == 200
    emi_data = emi_res.json()
    print("EMI Query Type:", emi_data.get("type"))
    assert emi_data.get("type") == "emi"
    assert emi_data.get("data", {}).get("monthly_emi") > 0
    
    # Max Loan Query
    max_res = client.post("/chat/query", json={"message": "I earn ₹50,000, how much loan can I get?"})
    assert max_res.status_code == 200
    max_data = max_res.json()
    print("Max Loan Query Type:", max_data.get("type"))
    assert max_data.get("type") == "max_loan"
    assert max_data.get("data", {}).get("max_loan") > 0
    
    # DTI Query
    dti_res = client.post("/chat/query", json={"message": "What is my DTI if my income is 60000 and EMI is 15000?"})
    assert dti_res.status_code == 200
    dti_data = dti_res.json()
    print("DTI Query Type:", dti_data.get("type"))
    assert dti_data.get("type") == "dti"
    assert dti_data.get("data", {}).get("current_dti_pct") == 25.0

    print("✓ Backward Compatibility PASSED!")


if __name__ == "__main__":
    test_api_financial_profile_assess()
    test_chat_query_natural_language_assessment()
    test_chat_query_backward_compatibility()
    print("\n==================================================")
    print("ALL API ENDPOINT INTEGRATION TESTS PASSED!")
    print("==================================================")
