"""
Phase 2 — Verified Loan Product Seed Data
==========================================

This script populates the loan_products table with a small, controlled set
of real loan products from major Indian lenders.

DATA SOURCING NOTES:
- All figures come from official bank websites and publicly available
  product pages as of September 2026.
- Interest rates are published ranges (starting rate to upper bound).
- Where an official minimum credit score is not explicitly stated on
  the product page, the field is left as None (not invented).
- Processing fees reflect the published upper-bound percentage.
- source_url links to the official product page used for verification.

IMPORTANT: These are point-in-time snapshots. Banks update terms frequently.
The verification_status and last_verified_at fields exist precisely so that
stale records can be flagged and refreshed without code changes.
"""

import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.db import SessionLocal, Base, engine
from app.models.loan_product import LoanProduct

# ── Create table if it doesn't exist ─────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Verified Seed Products ────────────────────────────────────────────────────
VERIFIED_PRODUCTS = [
    # ──────────────────────────────────────────────────────────────────────
    # 1. SBI Xpress Credit Personal Loan
    # ──────────────────────────────────────────────────────────────────────
    {
        "product_id": "sbi-xpress-credit-pl",
        "lender_name": "State Bank of India",
        "product_name": "SBI Xpress Credit Personal Loan",
        "loan_type": "personal",
        "interest_rate_min": 10.00,
        "interest_rate_max": 15.50,
        "rate_type": "floating",
        "min_loan_amount": 100000,
        "max_loan_amount": 5000000,
        "min_tenure_months": 6,
        "max_tenure_months": 72,
        "min_income": 20000,        # ₹20k for govt employees, ₹25k for corporate
        "min_credit_score": None,    # Not explicitly published on product page
        "min_age": 21,
        "max_age": 58,
        "employment_types": ["salaried"],
        "processing_fee_pct": 1.50,
        "processing_fee_flat": None,
        "processing_fee_description": "Up to 1.50% of loan amount (min ₹1,000, max ₹15,000) + GST",
        "key_conditions": [
            "Salary account with SBI required for most variants",
            "EMI/NMI ratio capped at 65%",
            "Available via SBI YONO app for instant digital disbursement",
            "Government/defence employees: min ₹20,000 NMI; corporate: min ₹25,000 NMI",
        ],
        "source_url": "https://sbi.co.in/web/personal-banking/loans/personal-loans",
        "last_verified_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "verification_status": "verified",
        "verification_notes": "Rates and terms from SBI official product page. Rate range reflects MCLR-linked spread; actual rate depends on profile.",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 2. HDFC Bank Personal Loan
    # ──────────────────────────────────────────────────────────────────────
    {
        "product_id": "hdfc-personal-loan",
        "lender_name": "HDFC Bank",
        "product_name": "HDFC Bank Personal Loan",
        "loan_type": "personal",
        "interest_rate_min": 9.99,
        "interest_rate_max": 24.00,
        "rate_type": "fixed",
        "min_loan_amount": 50000,
        "max_loan_amount": 4000000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "min_income": 25000,         # ₹25k with salary a/c, ₹50k without
        "min_credit_score": 720,     # Officially recommended on eligibility page
        "min_age": 21,
        "max_age": 60,
        "employment_types": ["salaried"],
        "processing_fee_pct": 2.00,
        "processing_fee_flat": None,
        "processing_fee_description": "Up to 2.00% of loan amount + GST",
        "key_conditions": [
            "Salary account holders: min ₹25,000/month; others: min ₹50,000/month",
            "Min 2 years total work experience, 1 year with current employer",
            "Employee of private limited or PSU/central/state body",
            "CIBIL score of 720+ recommended for favourable terms",
        ],
        "source_url": "https://www.hdfcbank.com/personal/borrow/popular-loans/personal-loan",
        "last_verified_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "verification_status": "verified",
        "verification_notes": "Rates from HDFC Bank official product page. ₹25k income threshold for salary account holders, ₹50k for non-salary. Upper rate of 24% for higher-risk profiles.",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 3. ICICI Bank Personal Loan
    # ──────────────────────────────────────────────────────────────────────
    {
        "product_id": "icici-personal-loan",
        "lender_name": "ICICI Bank",
        "product_name": "ICICI Bank Personal Loan",
        "loan_type": "personal",
        "interest_rate_min": 9.99,
        "interest_rate_max": 18.49,
        "rate_type": "fixed",
        "min_loan_amount": 50000,
        "max_loan_amount": 5000000,
        "min_tenure_months": 12,
        "max_tenure_months": 72,
        "min_income": 30000,
        "min_credit_score": None,     # Not explicitly published as hard floor
        "min_age": 20,
        "max_age": 58,
        "employment_types": ["salaried", "self_employed"],
        "processing_fee_pct": 2.00,
        "processing_fee_flat": None,
        "processing_fee_description": "Up to 2% of loan amount + GST (non-refundable)",
        "key_conditions": [
            "Salaried: min net monthly income ₹30,000",
            "Salaried: age 20-58; Self-employed: age 23-65",
            "Min 2 years work experience for salaried applicants",
            "Zero foreclosure charges after 24 EMIs paid",
        ],
        "source_url": "https://www.icicibank.com/personal-banking/loans/personal-loan",
        "last_verified_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "verification_status": "verified",
        "verification_notes": "Rates and features from ICICI Bank official product page. Self-employed also eligible (age 23-65). Upper rate bound approximate from published rate card.",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 4. Axis Bank Personal Loan
    # ──────────────────────────────────────────────────────────────────────
    {
        "product_id": "axis-personal-loan",
        "lender_name": "Axis Bank",
        "product_name": "Axis Bank Personal Loan",
        "loan_type": "personal",
        "interest_rate_min": 9.99,
        "interest_rate_max": 22.00,
        "rate_type": "fixed",
        "min_loan_amount": 50000,
        "max_loan_amount": 4000000,
        "min_tenure_months": 12,
        "max_tenure_months": 60,
        "min_income": 15000,          # ₹15k for existing customers, ₹25k for new
        "min_credit_score": 720,      # Officially recommended
        "min_age": 21,
        "max_age": 60,
        "employment_types": ["salaried"],
        "processing_fee_pct": 2.00,
        "processing_fee_flat": None,
        "processing_fee_description": "Up to 2% of loan amount + GST",
        "key_conditions": [
            "Existing Axis Bank customers: min ₹15,000/month income",
            "Non-Axis Bank customers: min ₹25,000/month income",
            "CIBIL score 720+ preferred for better terms",
            "Age between 21 and 60 years",
        ],
        "source_url": "https://www.axisbank.com/retail/loans/personal-loan",
        "last_verified_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "verification_status": "verified",
        "verification_notes": "Rates from Axis Bank official product page. Income threshold varies by customer relationship. Upper rate up to 22% per rate card.",
    },

    # ──────────────────────────────────────────────────────────────────────
    # 5. Kotak Mahindra Bank Personal Loan
    # ──────────────────────────────────────────────────────────────────────
    {
        "product_id": "kotak-personal-loan",
        "lender_name": "Kotak Mahindra Bank",
        "product_name": "Kotak Personal Loan",
        "loan_type": "personal",
        "interest_rate_min": 10.99,
        "interest_rate_max": 24.00,
        "rate_type": "fixed",
        "min_loan_amount": 50000,
        "max_loan_amount": 10000000,   # up to ₹1 crore
        "min_tenure_months": 12,
        "max_tenure_months": 72,
        "min_income": 25000,           # ₹25k with salary a/c, ₹30k without
        "min_credit_score": 750,       # Officially recommended
        "min_age": 21,
        "max_age": 60,
        "employment_types": ["salaried", "self_employed"],
        "processing_fee_pct": 5.00,
        "processing_fee_flat": None,
        "processing_fee_description": "Up to 5% of loan amount + GST (deducted from disbursement)",
        "key_conditions": [
            "Salary account holders: min ₹25,000/month; non-account: min ₹30,000/month",
            "Kotak Bank employees: min ₹20,000/month",
            "CIBIL score 750+ recommended for faster approval",
            "Min 1 year work experience; tenure up to 6 years",
        ],
        "source_url": "https://www.kotak.com/en/personal-banking/loans/personal-loan.html",
        "last_verified_at": datetime(2026, 9, 3, tzinfo=timezone.utc),
        "verification_status": "verified",
        "verification_notes": "Rates from Kotak Mahindra Bank official product page. Processing fee up to 5% is notably higher than peers. Max loan up to ₹1 crore for eligible profiles.",
    },
]


def seed_loan_products(force: bool = False):
    """
    Insert verified loan products into the database.

    Args:
        force: If True, replace existing records with same product_id.
               If False (default), skip records that already exist.
    """
    db = SessionLocal()
    inserted = 0
    skipped = 0
    updated = 0

    try:
        for product_data in VERIFIED_PRODUCTS:
            pid = product_data["product_id"]
            existing = db.query(LoanProduct).filter(LoanProduct.product_id == pid).first()

            if existing and not force:
                skipped += 1
                print(f"  SKIP  {pid} (already exists)")
                continue

            if existing and force:
                for key, value in product_data.items():
                    setattr(existing, key, value)
                updated += 1
                print(f"  UPDATE  {pid}")
            else:
                record = LoanProduct(**product_data)
                db.add(record)
                inserted += 1
                print(f"  INSERT  {pid}")

        db.commit()
        print(f"\nSeed complete: {inserted} inserted, {updated} updated, {skipped} skipped.")
    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2 — Seeding Verified Loan Products")
    print("=" * 60)

    force_mode = "--force" in sys.argv
    if force_mode:
        print("Mode: FORCE (will overwrite existing records)\n")
    else:
        print("Mode: SAFE (will skip existing records)\n")

    seed_loan_products(force=force_mode)
