"""
Demo PDF Generator — Phase 3 Technical Testing

Creates a clearly-labelled DEMO PDF for testing the extraction pipeline.

⚠️  THIS IS NOT AN OFFICIAL BANK POLICY DOCUMENT.
⚠️  DO NOT use this content as financial advice.

Run: python backend/scripts/create_demo_pdf.py
Output: backend/uploads/DEMO_loan_policy.pdf
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from fpdf import FPDF
except ImportError:
    print("ERROR: fpdf2 is not installed. Run: pip install fpdf2")
    sys.exit(1)

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "uploads", "DEMO_loan_policy.pdf"
)

SECTIONS = [
    {
        "title": "DEMO DOCUMENT -- NOT AN OFFICIAL BANK POLICY",
        "body": (
            "This document is a synthetic demo created for technical testing "
            "of the Tata Mitra PDF processing pipeline. All content is fictional "
            "and does not represent the policy of any bank or financial institution. "
            "It must NOT be used as financial advice."
        ),
    },
    {
        "title": "1. Personal Loan Eligibility Criteria",
        "body": (
            "To qualify for a personal loan, applicants must meet the following "
            "general criteria. The minimum monthly income requirement is typically "
            "Rs. 25,000. The applicant's age must be between 21 and 60 years at the "
            "time of loan maturity. A minimum credit score of 650 is generally "
            "required, though higher scores attract better interest rates. "
            "Salaried individuals must have a minimum of 2 years of employment "
            "history, with at least 1 year at their current employer. "
            "Self-employed applicants must demonstrate 3 years of business continuity "
            "and provide audited financials for the past 2 years."
        ),
    },
    {
        "title": "2. Loan Amount and Tenure",
        "body": (
            "Personal loans are typically available from Rs. 50,000 to Rs. 40,00,000 "
            "depending on the applicant's income and creditworthiness. "
            "The standard tenure ranges from 12 months to 60 months. "
            "Some lenders may offer extended tenures of up to 84 months for "
            "high-value loans. The maximum loan amount is generally capped at "
            "10 to 15 times the applicant's net monthly salary. "
            "The loan-to-income (LTI) ratio must not exceed 5x annual income."
        ),
    },
    {
        "title": "3. Debt-to-Income Ratio Policy",
        "body": (
            "The Debt-to-Income (DTI) ratio is a key factor in loan approval. "
            "DTI is calculated as: Total Monthly EMI Obligations divided by "
            "Gross Monthly Income. Most lenders prefer a DTI ratio below 40%. "
            "A DTI between 40% and 50% may lead to conditional approval with "
            "a higher interest rate. Applications with DTI above 50% are "
            "typically rejected. Existing EMIs include home loans, car loans, "
            "credit card dues, and any other active liabilities."
        ),
    },
    {
        "title": "4. Interest Rate Structure",
        "body": (
            "Interest rates on personal loans are typically in the range of "
            "10% to 24% per annum, depending on the applicant's credit profile. "
            "Applicants with a credit score above 750 may qualify for rates as "
            "low as 10.5%. Those with scores between 650 and 750 can expect "
            "rates between 14% and 18%. Processing fees are typically 1% to 2% "
            "of the loan amount, subject to a minimum of Rs. 500 and a maximum "
            "of Rs. 15,000. Prepayment charges may apply after 12 months of "
            "loan disbursement."
        ),
    },
    {
        "title": "5. Required Documents",
        "body": (
            "The following documents are typically required for personal loan "
            "applications: (a) Identity Proof - Aadhaar Card, PAN Card, or Passport. "
            "(b) Address Proof - Utility bill, Bank statement, or Rental agreement. "
            "(c) Income Proof - Last 3 months salary slips, Form 16, or ITR. "
            "(d) Bank Statements - Last 6 months. "
            "(e) Employment Proof - Offer letter or Employee ID. "
            "Self-employed applicants additionally require: Audited Balance Sheet, "
            "Profit and Loss Statement, and GST registration certificate."
        ),
    },
    {
        "title": "6. Credit Score Guidelines",
        "body": (
            "Credit scores are a primary factor in loan decisions. "
            "Scores above 800 are considered excellent and attract the best rates. "
            "Scores between 750 and 800 are very good and generally receive "
            "preferential treatment. Scores between 650 and 750 are acceptable "
            "but may result in higher interest rates or additional documentation. "
            "Scores below 650 typically lead to rejection or requirement of a "
            "co-applicant or guarantor. Applicants are advised to check their credit "
            "report at least 3 months before applying and resolve any disputes."
        ),
    },
    {
        "title": "7. Rejection Reasons and Improvement",
        "body": (
            "Common reasons for loan rejection include: insufficient income, "
            "high existing EMI burden, low credit score, incomplete documentation, "
            "frequent job changes, and multiple recent loan enquiries. "
            "Applicants who are rejected are advised to: reduce existing EMIs, "
            "maintain a consistent repayment history, avoid multiple applications "
            "within a short period, and build credit history through secured cards. "
            "Re-application is typically recommended after 6 months of credit improvement."
        ),
    },
]


def create_demo_pdf(output_path: str) -> None:
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, section in enumerate(SECTIONS):
        pdf.add_page()

        # Warning banner on every page
        pdf.set_fill_color(255, 240, 200)
        pdf.set_draw_color(200, 150, 0)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(150, 80, 0)
        pdf.cell(
            0, 8,
            "!! DEMO DOCUMENT -- NOT AN OFFICIAL BANK POLICY !!",
            border=1, fill=True, align="C",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        pdf.ln(4)

        # Section title
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(30, 30, 80)
        pdf.multi_cell(0, 8, section["title"])
        pdf.ln(4)

        # Body
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 7, section["body"])

        # Page number
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Page {i + 1} of {len(SECTIONS)}", align="C")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"Demo PDF created: {output_path}")
    print(f"    Pages: {len(SECTIONS)}")


if __name__ == "__main__":
    create_demo_pdf(OUTPUT_PATH)
