"""
Create an educational demo PDF for the Tata Mitra RAG pipeline.
This document is NOT an official bank policy.
It is clearly labeled as a NON-OFFICIAL EDUCATIONAL DEMO DOCUMENT throughout.
"""
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "uploads", "Tata_Mitra_Personal_Loan_Policy_DEMO.pdf"
)

# Colours
NAVY    = colors.HexColor("#1a2e5e")
TEAL    = colors.HexColor("#0d6e7a")
AMBER   = colors.HexColor("#c0600a")
RED     = colors.HexColor("#9b1c1c")
LGRAY   = colors.HexColor("#f5f5f5")
DGRAY   = colors.HexColor("#4a4a4a")

def make_styles():
    styles = {}
    styles["watermark"] = ParagraphStyle(
        "watermark", fontSize=9, textColor=RED,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4,
    )
    styles["doc_title"] = ParagraphStyle(
        "doc_title", fontSize=20, textColor=NAVY,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=6,
    )
    styles["doc_subtitle"] = ParagraphStyle(
        "doc_subtitle", fontSize=11, textColor=TEAL,
        alignment=TA_CENTER, fontName="Helvetica-Bold", spaceAfter=4,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading", fontSize=13, textColor=NAVY,
        fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=6,
    )
    styles["sub_heading"] = ParagraphStyle(
        "sub_heading", fontSize=11, textColor=TEAL,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontSize=10, textColor=DGRAY,
        fontName="Helvetica", leading=16, alignment=TA_JUSTIFY, spaceAfter=4,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontSize=10, textColor=DGRAY,
        fontName="Helvetica", leading=15, leftIndent=16, spaceAfter=3,
    )
    styles["note"] = ParagraphStyle(
        "note", fontSize=9, textColor=AMBER,
        fontName="Helvetica-Oblique", leading=13, alignment=TA_CENTER, spaceAfter=4,
    )
    styles["footer"] = ParagraphStyle(
        "footer", fontSize=8, textColor=colors.grey,
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=2,
    )
    return styles


def add_watermark_notice(s):
    return [
        Paragraph(
            "!! DEMO DOCUMENT - NON-OFFICIAL EDUCATIONAL MATERIAL - NOT AN ACTUAL BANK POLICY !!",
            s["watermark"]
        ),
        HRFlowable(width="100%", thickness=0.5, color=RED),
        Spacer(1, 4),
    ]


def build_pdf():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )

    s = make_styles()
    story = []

    # PAGE 1: Cover
    story += add_watermark_notice(s)
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Tata Mitra Loan Advisory Platform", s["doc_subtitle"]))
    story.append(Paragraph("Personal Loan Policy and Eligibility Guide", s["doc_title"]))
    story.append(Paragraph("Educational Reference Document - Version 1.0", s["doc_subtitle"]))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "This document is produced exclusively for educational and demonstration purposes as part of the "
        "Tata Mitra AI Loan Advisory project. It summarises general personal loan eligibility criteria, "
        "documentation requirements, and policy guidelines drawn from publicly available Indian banking "
        "standards. It does not represent the policy of any specific bank or financial institution.",
        s["body"]
    ))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Contents: 1. Eligibility Criteria  |  2. Required Documents  |  3. DTI / FOIR Policy  "
        "|  4. Rejection Reasons  |  5. Credit Score Policy  |  6. Borrower Rights",
        s["note"]
    ))
    story.append(Spacer(1, 1*cm))

    meta = [
        ["Document Type", "Educational Demo - Personal Loan Policy Summary"],
        ["Applicable Loan",  "Unsecured Personal Loan (Retail)"],
        ["Reference Standard", "Indian Banking - General Retail Lending Guidelines"],
        ["Prepared By", "Tata Mitra AI Advisory System"],
        ["Version", "1.0  |  For Demonstration Only"],
        ["Status", "NON-OFFICIAL - NOT LEGALLY BINDING"],
    ]
    tbl = Table(meta, colWidths=[5*cm, 11*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, -1), LGRAY),
        ("TEXTCOLOR",     (0, 0), (0, -1), NAVY),
        ("FONTNAME",      (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [colors.white, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(tbl)
    story.append(PageBreak())

    # PAGE 2: SECTION 1 - ELIGIBILITY CRITERIA
    story += add_watermark_notice(s)
    story.append(Paragraph("1. Personal Loan Eligibility Criteria", s["section_heading"]))
    story.append(Paragraph(
        "To be eligible for a personal loan under this framework, applicants must satisfy all of the "
        "following minimum eligibility requirements. These criteria apply to unsecured retail personal loans.",
        s["body"]
    ))

    story.append(Paragraph("1.1 Age Requirements", s["sub_heading"]))
    story.append(Paragraph("Minimum Age: 21 years at the time of loan application.", s["bullet"]))
    story.append(Paragraph("Maximum Age at Loan Maturity: 60 years for salaried applicants; 65 years for self-employed applicants.", s["bullet"]))
    story.append(Paragraph("Applicants below 21 years of age are not eligible and must apply jointly with a co-borrower.", s["bullet"]))

    story.append(Paragraph("1.2 Employment and Income Eligibility", s["sub_heading"]))
    story.append(Paragraph(
        "Eligible employment categories and corresponding minimum monthly net income requirements are as follows:",
        s["body"]
    ))

    emp_data = [
        ["Employment Category", "Minimum Monthly Net Income", "Minimum Job Stability"],
        ["Salaried - Government / PSU",    "Rs. 15,000 per month", "6 months at current employer"],
        ["Salaried - Private Sector",       "Rs. 20,000 per month", "12 months at current employer"],
        ["Self-Employed - Professional",    "Rs. 25,000 per month", "2 years in current profession"],
        ["Self-Employed - Business Owner", "Rs. 30,000 per month", "3 years of business vintage"],
        ["Freelancer / Gig Worker",         "Rs. 25,000 per month", "2 years consistent income proof"],
    ]
    emp_tbl = Table(emp_data, colWidths=[5.5*cm, 5.5*cm, 5*cm])
    emp_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(emp_tbl)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("1.3 Credit Score (CIBIL Score) Eligibility", s["sub_heading"]))
    story.append(Paragraph(
        "A valid CIBIL / Experian / Equifax credit score is mandatory for all personal loan applications. "
        "The credit score policy is as follows:",
        s["body"]
    ))
    for line in [
        "Minimum Required Score: 650 (on the 300-900 CIBIL scale).",
        "Preferred Score: 750 and above - qualifies for the best interest rates.",
        "Score 700-749: Standard rates apply; additional income verification may be required.",
        "Score 650-699: Conditional approval; higher interest rate bracket; stricter documentation.",
        "Score below 650: Application will be declined. Applicant must improve credit profile before reapplying.",
        "No active defaults, write-offs, or settlements in the last 36 months.",
        "No more than 2 hard credit enquiries in the past 6 months.",
    ]:
        story.append(Paragraph(line, s["bullet"]))

    story.append(PageBreak())

    # PAGE 3: REQUIRED DOCUMENTS
    story += add_watermark_notice(s)
    story.append(Paragraph("2. Required Documents for Loan Application", s["section_heading"]))
    story.append(Paragraph(
        "All applicants must submit the following documents. Incomplete applications will not be processed.",
        s["body"]
    ))

    story.append(Paragraph("2.1 Identity and Address Proof (any one from each category)", s["sub_heading"]))
    story.append(Paragraph("Identity Proof:", s["body"]))
    for d in ["Aadhaar Card", "PAN Card (mandatory for loans above Rs. 50,000)", "Valid Passport", "Voter ID Card"]:
        story.append(Paragraph(d, s["bullet"]))

    story.append(Paragraph("Address Proof:", s["body"]))
    for d in ["Aadhaar Card", "Utility Bill (electricity/water/gas) not older than 3 months",
              "Rent Agreement (registered)", "Bank Statement with address"]:
        story.append(Paragraph(d, s["bullet"]))

    story.append(Paragraph("2.2 Income Documents - Salaried Applicants", s["sub_heading"]))
    for d in [
        "Last 3 months salary slips (salary credited to bank account)",
        "Form 16 or Income Tax Return (ITR) for the last 2 financial years",
        "Bank account statements for the last 6 months showing salary credits",
        "Employer appointment letter (if employed less than 1 year)",
    ]:
        story.append(Paragraph(d, s["bullet"]))

    story.append(Paragraph("2.3 Income Documents - Self-Employed Applicants", s["sub_heading"]))
    for d in [
        "ITR with computation for the last 2-3 financial years",
        "CA-certified Profit and Loss Account and Balance Sheet",
        "Business registration certificate or GST registration",
        "Bank statements for the last 12 months (business and personal accounts)",
        "Professional degree certificate (for doctors, CAs, architects etc.)",
    ]:
        story.append(Paragraph(d, s["bullet"]))

    story.append(PageBreak())

    # PAGE 4: DTI POLICY + REJECTION
    story += add_watermark_notice(s)
    story.append(Paragraph("3. Debt-to-Income Ratio (DTI / FOIR) Policy", s["section_heading"]))
    story.append(Paragraph(
        "The Debt-to-Income (DTI) ratio - also called Fixed Obligation to Income Ratio (FOIR) - "
        "measures the percentage of the applicant gross monthly income that is committed to "
        "existing and proposed loan repayments.",
        s["body"]
    ))

    story.append(Paragraph("3.1 Maximum Permissible DTI", s["sub_heading"]))
    for line in [
        "Maximum DTI for new loan approval: 50% of gross monthly income.",
        "Preferred DTI for best-rate approval: 40% or below.",
        "DTI calculation includes: all existing EMIs (home loan, car loan, education loan, credit card minimum payments) plus proposed new EMI.",
        "Income considered: net monthly salary after tax for salaried; average monthly net profit (3-year average) for self-employed.",
    ]:
        story.append(Paragraph(line, s["bullet"]))

    dti_data = [
        ["DTI Range", "Risk Category", "Lending Decision"],
        ["Below 30%",  "Low Risk",     "Fast Track Approval"],
        ["30% - 40%",  "Moderate",     "Standard Approval"],
        ["40% - 50%",  "Higher Risk",  "Conditional Approval - may require co-borrower"],
        ["Above 50%",  "High Risk",    "Application Declined"],
    ]
    dti_tbl = Table(dti_data, colWidths=[4*cm, 5*cm, 7*cm])
    dti_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), TEAL),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LGRAY]),
        ("GRID",          (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
    ]))
    story.append(dti_tbl)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("4. Loan Rejection Reasons and Remediation", s["section_heading"]))
    reasons = [
        ("CIBIL Score Below 650",
         "Pay all EMIs and credit card dues on time for 6-12 months. Dispute inaccuracies on the CIBIL report."),
        ("DTI Ratio Above 50%",
         "Prepay or close existing loans before applying. Increase income proof or add a co-borrower."),
        ("Insufficient Employment Stability",
         "Salaried applicants must show at least 12 months with the current employer. "
         "Self-employed must show 2-3 years of business continuity."),
        ("Income Below Minimum Threshold",
         "Apply jointly with a co-borrower to combine incomes. Provide all income sources with proper documentation."),
        ("Multiple Hard Credit Enquiries",
         "Avoid applying to multiple lenders simultaneously. Space out applications by at least 6 months."),
        ("Existing Default or Loan Write-Off",
         "Settle any outstanding defaults and obtain a No-Dues Certificate. "
         "Minimum 12-24 months post-settlement clean record required before reapplication."),
    ]
    for i, (reason, remedy) in enumerate(reasons, 1):
        story.append(Paragraph(f"{i}. {reason}", s["sub_heading"]))
        story.append(Paragraph(f"Remediation: {remedy}", s["body"]))

    story.append(PageBreak())

    # PAGE 5: Credit Score + Borrower Rights
    story += add_watermark_notice(s)
    story.append(Paragraph("5. Credit Score Improvement Policy", s["section_heading"]))
    story.append(Paragraph(
        "The following evidence-based steps help improve CIBIL credit scores before applying for a personal loan:",
        s["body"]
    ))
    for step in [
        "Pay 100% of EMI and credit card dues before the due date every month. Payment history accounts for approximately 35% of the credit score.",
        "Keep credit card utilisation below 30% of the credit limit at all times.",
        "Maintain a healthy mix of secured (home loan, car loan) and unsecured (personal loan, credit card) credit.",
        "Do not apply for multiple credit products within 6 months - each hard enquiry temporarily reduces the score.",
        "Regularly check your CIBIL report (free once per year at www.cibil.com) and dispute any incorrect entries immediately.",
        "Allow at least 6-12 months of consistent repayment behaviour before reapplying after a rejection.",
    ]:
        story.append(Paragraph(step, s["bullet"]))

    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("6. Borrower Rights and Grievance Redressal", s["section_heading"]))
    story.append(Paragraph(
        "All borrowers are entitled to the following rights under the RBI Fair Practice Code and the "
        "Banking Codes and Standards Board of India (BCSBI) Code:",
        s["body"]
    ))
    for right in [
        "Receive a transparent Sanction Letter detailing the loan amount, interest rate (APR), fees, charges, EMI schedule, and prepayment terms before disbursement.",
        "Receive a copy of all loan documents including the loan agreement without any additional charge.",
        "Not be subjected to coercive or harassing recovery calls. RBI prohibits contact before 8 AM or after 7 PM.",
        "Prepay floating-rate personal loans at any time without foreclosure penalty as per RBI circular.",
        "File a free grievance with the RBI Integrated Ombudsman if the lender does not resolve a complaint within 30 days at cms.rbi.org.in.",
    ]:
        story.append(Paragraph(right, s["bullet"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "DISCLAIMER: This document is a NON-OFFICIAL EDUCATIONAL DEMO produced for the Tata Mitra AI Buildathon demonstration. "
        "It does not constitute legal, financial, or banking advice. "
        "Always consult your bank official loan policy before making any financial decision.",
        s["note"]
    ))
    story.append(Paragraph("End of Document - Tata Mitra Personal Loan Policy Guide v1.0 (Educational Demo)", s["footer"]))

    doc.build(story)
    print(f"PDF created: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    path = build_pdf()
    size = os.path.getsize(path)
    print(f"File size: {size:,} bytes ({size/1024:.1f} KB)")
