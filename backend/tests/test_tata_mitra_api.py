"""Tata Mitra backend API tests."""
import os
import re
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://60597249-cfec-463d-82f2-41fdebf8f027.preview.emergentagent.com").rstrip("/")
ADMIN_KEY = "tata-mitra-admin-2024"


@pytest.fixture(scope="module")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# Health
def test_health(s):
    r = s.get(f"{BASE_URL}/api/health", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert d["gemini_configured"] is True


# Deterministic EMI
def test_emi_calc(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "What EMI for 5 lakh at 10.5% for 5 years?"}, timeout=60)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "emi"
    data = d.get("data", {})
    for k in ("monthly_emi", "total_interest", "total_repayment"):
        v = data.get(k)
        assert isinstance(v, (int, float)) and v == v and v > 0, f"{k}={v}"


def test_max_loan_missing_income(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "What is the maximum loan I can get?"}, timeout=60)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "max_loan"
    msg = (d.get("message") or "") + str(d.get("data") or "")
    assert "nan" not in msg.lower() and "undefined" not in msg.lower()
    assert "income" in msg.lower()


def test_dti(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "I earn 80000 with 15000 existing EMI, what is my DTI?"}, timeout=60)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "dti"
    assert "current_dti_pct" in (d.get("data") or {})


def test_assessment(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "I earn 80000, have 10000 EMI, CIBIL 780, need 5 lakh for 3 years"}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "assessment"
    assert d.get("title")
    assert d.get("status")
    data = d.get("data") or {}
    assert "estimated_emi" in data or "monthly_emi" in data or data


def test_general_llm(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "Explain what a personal loan is"}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "general"
    msg = d.get("message") or ""
    assert len(msg) > 60


def test_policy_gold_loan_ltv(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "What is the maximum LTV for a gold loan?"}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    assert d.get("type") == "policy", d
    data = d.get("data") or {}
    assert data.get("support_level") == "SUPPORTED", data.get("support_level")
    assert data.get("is_verified") is True
    srcs = data.get("sources") or []
    assert srcs
    for s0 in srcs:
        assert "document_name" in s0 and "page_number" in s0 and "relevance_score" in s0


def test_rag_ask_supported(s):
    r = s.post(f"{BASE_URL}/api/rag/ask", json={"question": "What documents are required for a personal loan?", "top_k": 5}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    assert d.get("support_level") in ("SUPPORTED", "PARTIALLY_SUPPORTED"), d.get("support_level")
    assert d.get("sources")
    assert d.get("top_evidence") is not None


def test_rag_unsupported(s):
    r = s.post(f"{BASE_URL}/api/rag/ask", json={"question": "What is the recipe for chocolate cake?", "top_k": 5}, timeout=60)
    assert r.status_code == 200
    d = r.json()
    assert d.get("support_level") == "UNSUPPORTED"
    assert d.get("sources") == [] or not d.get("sources")


def test_multilingual_hindi(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "What EMI for 5 lakh at 10.5% for 5 years?", "language": "hi"}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    msg = d.get("message") or ""
    # Hindi script (Devanagari) present
    assert re.search(r"[\u0900-\u097F]", msg), f"no devanagari: {msg[:200]}"


def test_multilingual_marathi(s):
    r = s.post(f"{BASE_URL}/api/chat/query", json={"message": "What is a gold loan?", "language": "mr"}, timeout=90)
    assert r.status_code == 200
    d = r.json()
    msg = d.get("message") or ""
    assert re.search(r"[\u0900-\u097F]", msg), f"no devanagari (mr): {msg[:200]}"


def test_loan_products(s):
    r = s.get(f"{BASE_URL}/api/loan-products", timeout=30)
    assert r.status_code == 200
    prods = r.json()
    # Could be list or wrapped
    if isinstance(prods, dict):
        prods = prods.get("products") or prods.get("data") or []
    assert len(prods) >= 5
    banks = {p.get("bank_name", "") for p in prods}
    for expected in ("SBI", "HDFC", "ICICI", "Axis", "Kotak"):
        assert any(expected.lower() in b.lower() for b in banks), f"missing {expected} in {banks}"
    for p in prods:
        assert p.get("verification_status") == "verified", p
        assert p.get("source_url")


def test_search_stats(s):
    r = s.get(f"{BASE_URL}/api/search/stats", timeout=30)
    assert r.status_code == 200
    d = r.json()
    assert d.get("total_documents") == 13, d
    assert d.get("total_chunks", 0) >= 13
    assert d.get("index_loaded") is True


def test_admin_docs_forbidden(s):
    r = requests.get(f"{BASE_URL}/api/admin/documents", timeout=30)
    assert r.status_code == 403


def test_admin_docs_ok(s):
    r = requests.get(f"{BASE_URL}/api/admin/documents", headers={"X-Admin-Key": ADMIN_KEY}, timeout=30)
    assert r.status_code == 200
    d = r.json()
    docs = d if isinstance(d, list) else (d.get("documents") or [])
    assert len(docs) == 13, f"expected 13, got {len(docs)}"
