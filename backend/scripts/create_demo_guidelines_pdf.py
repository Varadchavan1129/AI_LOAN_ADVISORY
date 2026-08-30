"""
Demo Financial Guidelines PDF Generator — Phase 4 Multi-Document Testing

Creates a second clearly-labelled DEMO PDF about general financial guidelines,
distinct from the loan policy document, to test multi-document retrieval.

!! THIS IS NOT AN OFFICIAL FINANCIAL DOCUMENT !!
All content is fictional and for technical testing only.

Run: python backend/scripts/create_demo_guidelines_pdf.py
Output: backend/uploads/DEMO_financial_guidelines.pdf
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    print("ERROR: fpdf2 is not installed.")
    sys.exit(1)

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "uploads", "DEMO_financial_guidelines.pdf"
)

SECTIONS = [
    {
        "title": "DEMO DOCUMENT -- NOT AN OFFICIAL FINANCIAL POLICY",
        "body": (
            "This document is a synthetic demo created for technical testing "
            "of the Tata Mitra RAG pipeline. It simulates a 'General Financial "
            "Guidelines' document. All content is fictional and does not represent "
            "any bank, NBFC, or regulatory body. Do NOT use this as financial advice."
        ),
    },
    {
        "title": "Section 1. EMI Calculation Standards",
        "body": (
            "Equated Monthly Instalment (EMI) is calculated using the standard "
            "reducing-balance method. The formula is: EMI = P * r * (1+r)^n / ((1+r)^n - 1), "
            "where P is the principal, r is the monthly interest rate (annual rate / 12 / 100), "
            "and n is the tenure in months. All financial institutions are expected to use this "
            "formula consistently. EMI must be disclosed clearly to the borrower before loan "
            "disbursal. Any pre-closure or part-payment adjustments should be recalculated "
            "using the same reducing-balance method."
        ),
    },
    {
        "title": "Section 2. Responsible Lending Principles",
        "body": (
            "Lenders must assess borrower affordability before sanctioning a loan. "
            "The total monthly EMI obligation of a borrower including the new loan "
            "must not exceed 50 percent of their gross monthly income. "
            "Lenders must verify income documents including salary slips, bank statements, "
            "and Income Tax Returns. Employment stability of at least 12 months at the current "
            "employer is a standard requirement for salaried borrowers. For self-employed "
            "borrowers, a minimum of 2 years of business continuity must be demonstrated."
        ),
    },
    {
        "title": "Section 3. Interest Rate Transparency",
        "body": (
            "All interest rates must be quoted on an annualised basis. Lenders must clearly "
            "disclose the Annual Percentage Rate (APR) which includes the base interest rate, "
            "processing fees, and all other charges. Variable interest rates must clearly state "
            "the benchmark rate (such as repo rate) and the spread above it. Borrowers must be "
            "informed of any rate revision at least 30 days in advance. Hidden charges, delayed "
            "payment penalties, and pre-closure fees must all be disclosed in the loan agreement "
            "upfront."
        ),
    },
    {
        "title": "Section 4. Credit Bureau Reporting",
        "body": (
            "All loan accounts must be reported to at least one approved credit bureau "
            "within 30 days of account opening. Payment history, defaults, and settlements "
            "must be updated monthly. Credit scores are calculated on a scale of 300 to 900. "
            "A score above 750 is generally considered good for loan eligibility. "
            "Lenders must provide borrowers with a credit bureau score upon request. "
            "Any dispute raised by the borrower regarding their credit record must be "
            "resolved within 30 working days."
        ),
    },
    {
        "title": "Section 5. Grievance Redressal",
        "body": (
            "Every lender must have a documented grievance redressal policy. "
            "Complaints must be acknowledged within 3 working days. "
            "Resolution must be provided within 30 working days of complaint receipt. "
            "If a borrower is not satisfied with the lender's resolution, they may escalate "
            "to the Banking Ombudsman (for banks) or the Reserve Bank of India Integrated "
            "Ombudsman Scheme (RBI IOS) for regulated entities. "
            "Lenders must publish their Grievance Redressal Officer details prominently."
        ),
    },
    {
        "title": "Section 6. Loan Restructuring Guidelines",
        "body": (
            "Loan restructuring may be offered to borrowers facing genuine financial distress. "
            "This includes tenure extension, EMI reduction, or temporary moratorium on payments. "
            "Restructuring must be documented and borrowers must be informed of the impact on "
            "total interest outgo. Restructured loans may be reported differently to credit "
            "bureaus and may affect the borrower's credit score. Lenders must not impose "
            "additional charges beyond standard processing fees for restructuring requests."
        ),
    },
    {
        "title": "Section 7. Digital Lending Norms",
        "body": (
            "Digital lending applications must disclose all fees and charges upfront before "
            "loan disbursal. Data collection must be limited to what is required for credit "
            "assessment. Borrower consent must be obtained for each data access. "
            "Loan agreements must be available in digital format and signed with OTP or "
            "e-signature. Disbursal must happen only to the verified bank account of the "
            "borrower and not to any third-party account. Recovery agents must follow the "
            "Fair Practices Code and must not resort to intimidation."
        ),
    },
]


def create_guidelines_pdf(output_path: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for i, section in enumerate(SECTIONS):
        pdf.add_page()

        # Warning banner
        pdf.set_fill_color(200, 230, 255)
        pdf.set_draw_color(0, 100, 200)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(0, 60, 150)
        pdf.cell(
            0, 8,
            "!! DEMO DOCUMENT -- NOT AN OFFICIAL FINANCIAL POLICY !!",
            border=1, fill=True, align="C",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT
        )
        pdf.ln(4)

        # Section title
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 60, 100)
        pdf.multi_cell(0, 8, section["title"])
        pdf.ln(4)

        # Body
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 7, section["body"])

        # Page number
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, f"Page {i + 1} of {len(SECTIONS)}", align="C")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"Guidelines PDF created: {output_path}")
    print(f"    Pages: {len(SECTIONS)}")


if __name__ == "__main__":
    create_guidelines_pdf(OUTPUT_PATH)
