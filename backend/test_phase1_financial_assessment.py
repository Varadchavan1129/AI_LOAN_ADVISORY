import os
import sys

# Ensure UTF-8 stdout on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.schemas.loan_input import LoanInput
from app.services.financial_assessment import compute_deterministic_assessment, DEFAULT_BASELINE_RATE, DEFAULT_FOIR_BENCHMARK
from app.ml.feature_builder import build_ml_features, map_loan_intent, get_loan_grade
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.nlu_agent import _extract_entities_regex, parse_intent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.db import SessionLocal
from app.models.loan_application import LoanApplication


def test_deterministic_financial_engine():
    print("\n--- 1. Testing Deterministic Financial Assessment Engine ---")
    
    # Test Profile: Monthly Income 60,000, Existing EMI 8,000, Loan Amount 5,00,000, Tenure 36 months, Baseline Rate 10.5%
    profile = LoanInput(
        monthly_income=60000,
        existing_emi=8000,
        loan_amount=500000,
        tenure_months=36,
        employment_type="salaried",
        age=30,
        credit_score=750,
        loan_purpose="personal",
        annual_rate=10.5
    )
    
    res = compute_deterministic_assessment(profile)
    print(f"Profile: Income = ₹{res['monthly_income']:,.0f}, Existing EMI = ₹{res['existing_emi']:,.0f}, Loan = ₹{res['requested_loan_amount']:,.0f} for {res['tenure_months']}m")
    print(f"-> Estimated EMI: ₹{res['estimated_emi']:,.2f}")
    print(f"-> Total Interest: ₹{res['total_interest']:,.2f}")
    print(f"-> Total Monthly Obligations: ₹{res['total_monthly_obligations']:,.2f}")
    print(f"-> Disposable Income: ₹{res['disposable_income']:,.2f}")
    print(f"-> Current FOIR: {res['current_foir_pct']}% | Projected FOIR: {res['projected_foir_pct']}%")
    print(f"-> Affordability Status: {res['affordability_status']}")
    print(f"-> Max Permissible EMI (50% cap): ₹{res['max_permissible_emi']:,.2f}")
    print(f"-> Available EMI Capacity: ₹{res['available_emi_capacity']:,.2f}")
    print(f"-> Estimated Max Loan Eligibility: ₹{res['estimated_max_loan_eligibility']:,.2f}")
    print(f"-> Assumptions: {[a['label'] for a in res['assumptions']]}")
    
    # Assertions
    # 5L @ 10.5% for 36 months: EMI is approx 16,251
    assert 16000 <= res["estimated_emi"] <= 16500, f"EMI unexpected: {res['estimated_emi']}"
    assert res["total_monthly_obligations"] == round(8000 + res["estimated_emi"], 2)
    assert res["disposable_income"] == round(60000 - res["total_monthly_obligations"], 2)
    assert res["current_foir_pct"] == round((8000 / 60000) * 100, 2)
    assert res["projected_foir_pct"] == round((res["total_monthly_obligations"] / 60000) * 100, 2)
    assert res["affordability_status"] in ["comfortable", "manageable"]
    assert res["estimated_max_loan_eligibility"] > res["requested_loan_amount"]
    print("✓ Deterministic Financial Engine Test PASSED!")


def test_overburdened_and_edge_cases():
    print("\n--- 2. Testing Edge Cases & Overburdened Profiles ---")
    
    # Case A: Existing EMI already exceeds 50% FOIR
    profile_overburdened = LoanInput(
        monthly_income=40000,
        existing_emi=25000, # 62.5% FOIR already
        loan_amount=300000,
        tenure_months=36
    )
    res_ob = compute_deterministic_assessment(profile_overburdened)
    print(f"Overburdened: Projected FOIR = {res_ob['projected_foir_pct']}%, Available Capacity = ₹{res_ob['available_emi_capacity']}, Max Loan = ₹{res_ob['estimated_max_loan_eligibility']}")
    assert res_ob["available_emi_capacity"] == 0.0
    assert res_ob["estimated_max_loan_eligibility"] == 0.0
    assert res_ob["affordability_status"] == "high_risk"
    
    # Case B: Zero existing EMI
    profile_clean = LoanInput(
        monthly_income=100000,
        existing_emi=0,
        loan_amount=1000000,
        tenure_months=60
    )
    res_clean = compute_deterministic_assessment(profile_clean)
    assert res_clean["current_foir_pct"] == 0.0
    assert res_clean["available_emi_capacity"] == 50000.0
    assert res_clean["affordability_status"] == "comfortable"
    print("✓ Edge Cases & Overburdened Profiles Test PASSED!")


def test_ml_feature_builder_and_eligibility():
    print("\n--- 3. Testing ML Feature Builder & Eligibility Agent ---")
    
    profile_good = LoanInput(
        monthly_income=75000,
        existing_emi=5000,
        loan_amount=400000,
        tenure_months=48,
        employment_type="salaried",
        age=29,
        credit_score=780,
        loan_purpose="home renovation"
    )
    
    # Check feature builder
    df_features = build_ml_features(profile_good)
    print("ML Features shape:", df_features.shape)
    assert df_features["person_age"].iloc[0] == 29
    assert df_features["credit_score"].iloc[0] == 780
    assert df_features["loan_intent"].iloc[0] == "HOMEIMPROVEMENT"
    assert df_features["loan_grade"].iloc[0] == "A"
    
    # Check Eligibility decision
    eval_res = EligibilityAgent.evaluate(profile_good)
    print(f"Good Profile: Decision = {eval_res.decision}, Score = {eval_res.eligibility_score}, Risk = {eval_res.risk_probability}")
    assert eval_res.decision == "approved"
    assert eval_res.assessment is not None
    assert eval_res.assessment.estimated_emi > 0
    
    # Check Low Credit Profile (<650 CIBIL)
    profile_low_cibil = LoanInput(
        monthly_income=30000,
        existing_emi=12000,
        loan_amount=500000,
        tenure_months=24,
        employment_type="self_employed",
        age=25,
        credit_score=590,
        loan_purpose="debt consolidation"
    )
    eval_bad = EligibilityAgent.evaluate(profile_low_cibil)
    print(f"Low CIBIL / High FOIR Profile: Decision = {eval_bad.decision}, Score = {eval_bad.eligibility_score}, Risk = {eval_bad.risk_probability}")
    assert eval_bad.decision in ["rejected", "conditional"]
    print("✓ ML Feature Builder & Eligibility Agent Test PASSED!")


def test_nlu_entity_extraction():
    print("\n--- 4. Testing Natural Language Entity Extraction ---")
    
    test_nl_query = "I earn ₹60,000, have an ₹8,000 EMI, CIBIL 750 and need ₹5 lakh for 3 years."
    extracted = _extract_entities_regex(test_nl_query)
    print(f"Query: '{test_nl_query}'")
    print(f"-> Regex Extracted: {extracted}")
    
    assert extracted["monthly_income"] == 60000, f"Expected 60000, got {extracted['monthly_income']}"
    assert extracted["existing_emi"] == 8000, f"Expected 8000, got {extracted['existing_emi']}"
    assert extracted["credit_score"] == 750, f"Expected 750, got {extracted['credit_score']}"
    assert extracted["loan_amount"] == 500000, f"Expected 500000, got {extracted['loan_amount']}"
    assert extracted["tenure_months"] == 36, f"Expected 36, got {extracted['tenure_months']}"

    # Another query: age, purpose, salary
    test_nl_query_2 = "I make 85k as salaried, age 32, CIBIL 780, need 10 lakh for home renovation for 5 years"
    extracted_2 = _extract_entities_regex(test_nl_query_2)
    print(f"Query 2: '{test_nl_query_2}'")
    print(f"-> Regex Extracted: {extracted_2}")
    assert extracted_2["monthly_income"] == 85000
    assert extracted_2["age"] == 32
    assert extracted_2["credit_score"] == 780
    assert extracted_2["loan_amount"] == 1000000
    assert extracted_2["tenure_months"] == 60
    assert extracted_2["loan_purpose"] == "home"
    assert extracted_2["employment_type"] == "salaried"
    print("✓ NLU Entity Extraction Test PASSED!")


def test_orchestrator_and_database_persistence():
    print("\n--- 5. Testing Orchestrator Agent & Database Persistence ---")
    
    profile = LoanInput(
        monthly_income=65000,
        existing_emi=10000,
        loan_amount=600000,
        tenure_months=48,
        employment_type="salaried",
        age=31,
        credit_score=760,
        loan_purpose="medical"
    )
    
    orch_output = OrchestratorAgent.process_loan_application(profile)
    print("Orchestrator Output Status:", orch_output["status"])
    print("Orchestrator Title:", orch_output["title"])
    print("Orchestrator Message:", orch_output["message"])
    assert "session_id" in orch_output
    assert "assessment" in orch_output
    assert orch_output["assessment"]["estimated_emi"] > 0
    assert "profile" in orch_output
    assert orch_output["profile"]["credit_score"] == 760
    
    # Check SQLite DB
    db = SessionLocal()
    try:
        saved_app = db.query(LoanApplication).filter(LoanApplication.session_id == orch_output["session_id"]).first()
        assert saved_app is not None, "Application was not saved to SQLite!"
        print(f"Saved DB Record: App ID={saved_app.application_id}, Income={saved_app.monthly_income}, CIBIL={saved_app.credit_score}, Estimated EMI={saved_app.estimated_emi}, Decision={saved_app.decision}")
        assert saved_app.credit_score == 760
        assert saved_app.monthly_income == 65000
    finally:
        db.close()
    
    print("✓ Orchestrator Agent & Database Persistence Test PASSED!")


if __name__ == "__main__":
    print("==================================================")
    print("STARTING PHASE 1 VERIFICATION TESTS")
    print("==================================================")
    test_deterministic_financial_engine()
    test_overburdened_and_edge_cases()
    test_ml_feature_builder_and_eligibility()
    test_nlu_entity_extraction()
    test_orchestrator_and_database_persistence()
    print("\n==================================================")
    print("ALL PHASE 1 BACKEND TESTS PASSED SUCCESSFULLY!")
    print("==================================================")
