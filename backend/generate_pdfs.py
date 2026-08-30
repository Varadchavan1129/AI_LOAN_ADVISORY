"""
Script to generate 5 comprehensive synthetic PDFs for the Tata Mitra RAG pipeline.
Run from: backend/ with venv activated
python generate_pdfs.py
"""
import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads_seed")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.doc_title = title

    def header(self):
        self.set_font("Arial", "B", 11)
        self.set_fill_color(30, 60, 114)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  {self.doc_title}", border=0, ln=1, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def chapter(self, title, body):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(230, 236, 255)
        self.cell(0, 8, title, border=0, ln=1, fill=True)
        self.set_font("Arial", "", 10)
        self.multi_cell(0, 6, body)
        self.ln(5)


def create_personal_loan_pdf():
    pdf = PDF("Personal Loan Complete Policy Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Personal Loan Overview",
        "A personal loan is an unsecured loan provided by banks and NBFCs to individuals for personal "
        "use such as medical emergencies, travel, home renovation, education, or wedding expenses. "
        "Unlike home or car loans, personal loans do not require any collateral or security. "
        "The loan amount is disbursed directly to the borrower's bank account, usually within 24-72 hours "
        "of approval. Repayment is done through Equated Monthly Instalments (EMIs) over a fixed tenure."
    )
    pdf.chapter("2. Eligibility Criteria for Personal Loan",
        "To qualify for a personal loan in India, applicants must satisfy the following criteria:\n"
        "- Age: Between 21 and 60 years at the time of loan application.\n"
        "- Minimum Monthly Income: Rs. 20,000 for salaried individuals in metro cities; Rs. 15,000 in non-metro.\n"
        "- Work Experience: Minimum 2 years total, with at least 1 year at current employer for salaried.\n"
        "- Self-Employed: Minimum 3 years of business continuity with audited financials.\n"
        "- Credit Score: Minimum CIBIL score of 650 required; score above 750 preferred for best rates.\n"
        "- DTI Ratio: Total EMI obligations including new loan should not exceed 50% of gross monthly income."
    )
    pdf.chapter("3. Loan Amount and Tenure",
        "Personal loans are available in the following ranges:\n"
        "- Minimum Loan Amount: Rs. 50,000\n"
        "- Maximum Loan Amount: Rs. 40,00,000 (Rs. 40 lakh) depending on income and credit profile\n"
        "- Loan-to-Income Ratio: Maximum loan generally capped at 10 to 20 times net monthly salary\n"
        "- Minimum Tenure: 12 months (1 year)\n"
        "- Maximum Tenure: 60 months (5 years); some lenders offer up to 84 months (7 years)\n"
        "- Longer tenures reduce EMI but increase total interest paid significantly."
    )
    pdf.chapter("4. Interest Rates on Personal Loans",
        "Personal loan interest rates vary based on credit profile:\n"
        "- Excellent Credit (CIBIL above 800): 10.5% to 12% per annum\n"
        "- Good Credit (CIBIL 750-800): 12% to 15% per annum\n"
        "- Average Credit (CIBIL 650-750): 15% to 20% per annum\n"
        "- Low Credit (CIBIL 600-649): 20% to 24% per annum (if approved at all)\n"
        "- Processing Fee: 1% to 3% of loan amount, minimum Rs. 500, maximum Rs. 15,000.\n"
        "- Prepayment Charges: 2% to 5% of outstanding principal after lock-in of 6-12 months.\n"
        "- Late Payment Penalty: 2% to 3% per month on overdue EMI amount."
    )
    pdf.chapter("5. Documents Required for Personal Loan",
        "For Salaried Individuals:\n"
        "- Identity Proof: Aadhaar Card, PAN Card, Passport, or Voter ID\n"
        "- Address Proof: Aadhaar Card, Utility bill, Rent agreement, or Passport\n"
        "- Income Proof: Last 3 months salary slips, Form 16, last 6 months bank statements\n"
        "- Employment Proof: Offer letter, appointment letter, or Employee ID card\n\n"
        "For Self-Employed Individuals:\n"
        "- ITR for last 2-3 years\n"
        "- Audited Balance Sheet and Profit and Loss statement\n"
        "- Business continuity proof: GST registration, trade license\n"
        "- Last 12 months bank statements (business and personal)"
    )
    pdf.chapter("6. EMI Calculation for Personal Loans",
        "EMI is calculated using the reducing-balance method:\n"
        "Formula: EMI = P x r x (1+r)^n divided by ((1+r)^n - 1)\n"
        "P = Principal, r = Monthly interest rate (Annual rate / 12 / 100), n = Tenure in months\n\n"
        "Example EMI calculations:\n"
        "- Rs. 5,00,000 at 12% for 36 months: EMI = Rs. 16,607 per month, Total Interest = Rs. 97,852\n"
        "- Rs. 5,00,000 at 15% for 48 months: EMI = Rs. 13,915 per month, Total Interest = Rs. 1,67,920\n"
        "- Rs. 10,00,000 at 11% for 60 months: EMI = Rs. 21,742 per month, Total Interest = Rs. 3,04,520"
    )
    pdf.chapter("7. Reasons for Personal Loan Rejection",
        "Common reasons why personal loan applications get rejected:\n"
        "1. Low CIBIL Score: Score below 650 is the most common reason for rejection.\n"
        "2. High DTI Ratio: Total EMI obligations exceeding 50% of income.\n"
        "3. Unstable Employment: Frequent job changes or less than 1 year at current employer.\n"
        "4. Insufficient Income: Monthly income below the lender's minimum threshold.\n"
        "5. Incomplete Documentation: Missing salary slips, bank statements, or KYC documents.\n"
        "6. Multiple Loan Applications: Hard inquiries from multiple lenders reduce score.\n"
        "7. Existing High Debt: Too many active loans or credit card outstanding balances.\n\n"
        "Steps to improve: Pay all existing EMIs on time, reduce credit card outstanding, "
        "avoid multiple applications, and wait at least 6 months before re-applying."
    )
    pdf.chapter("8. How to Improve Loan Approval Chances",
        "To improve your personal loan approval chances:\n"
        "- Maintain CIBIL score above 750 by paying all dues on time.\n"
        "- Reduce existing EMI burden before applying for a new loan.\n"
        "- Apply with a co-applicant (spouse or parent) to increase combined income.\n"
        "- Avoid applying to multiple lenders simultaneously.\n"
        "- Check your credit report for errors and dispute them 3 months before applying.\n"
        "- Maintain a salary account with the lending bank for faster approval and better rates."
    )
    out_path = os.path.join(OUTPUT_DIR, "personal_loan_complete_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


def create_home_loan_pdf():
    pdf = PDF("Home Loan Policy Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Home Loan Overview",
        "A home loan (housing loan or mortgage) is a secured loan for purchasing, constructing, "
        "renovating, or extending a residential property. The property serves as collateral. "
        "Home loans have longer tenures and lower interest rates compared to personal loans. "
        "Interest paid on home loans is tax-deductible under Section 24(b) up to Rs. 2 lakh per year. "
        "Principal repayment is deductible under Section 80C up to Rs. 1.5 lakh per year."
    )
    pdf.chapter("2. Home Loan Eligibility",
        "Eligibility criteria for home loans:\n"
        "- Age: 21 to 65 years (loan must be repaid before retirement)\n"
        "- Minimum Income: Rs. 25,000 per month for salaried; Rs. 2.5 lakh per year for self-employed\n"
        "- CIBIL Score: Minimum 650, preferred above 750\n"
        "- LTV Ratio: Up to 90% of property value for loans up to Rs. 30 lakh;\n"
        "  80% for loans between Rs. 30-75 lakh; 75% for loans above Rs. 75 lakh.\n"
        "- DTI: Total EMI obligations should not exceed 55% of gross monthly income."
    )
    pdf.chapter("3. Home Loan Amount and Tenure",
        "Home loan specifics:\n"
        "- Minimum Amount: Rs. 2,00,000\n"
        "- Maximum Amount: Up to Rs. 5 crore or more depending on lender and property value\n"
        "- Maximum Tenure: 30 years\n"
        "- Typical Tenure: 15-20 years\n"
        "- Down Payment: Minimum 10-25% of property value must be paid upfront by borrower"
    )
    pdf.chapter("4. Home Loan Interest Rates",
        "Home loan interest rates in India:\n"
        "- Floating Rate: 8.5% to 10.5% per annum (linked to repo rate or MCLR)\n"
        "- Fixed Rate: 9.5% to 12% per annum\n"
        "- CIBIL above 800: Best floating rates starting from 8.5%\n"
        "- CIBIL 750-800: Rates from 8.75% to 9.5%\n"
        "- CIBIL 650-750: Rates from 9.5% to 10.75%\n"
        "- Processing Fee: 0.25% to 1% of loan amount, maximum Rs. 15,000\n"
        "- No prepayment charges on floating rate home loans as per RBI guidelines."
    )
    pdf.chapter("5. Types of Home Loans",
        "Different types of home loans:\n"
        "1. Home Purchase Loan: For buying ready or under-construction property\n"
        "2. Home Construction Loan: For constructing on owned plot\n"
        "3. Home Extension Loan: For adding rooms or floors to existing property\n"
        "4. Home Renovation Loan: For repairing or renovating existing home\n"
        "5. Plot Loan: For purchasing a residential plot\n"
        "6. Balance Transfer: Transferring existing home loan for lower rate\n"
        "7. Top-Up Loan: Additional loan on existing home loan\n"
        "8. NRI Home Loan: For Non-Resident Indians purchasing property in India"
    )
    pdf.chapter("6. Home Loan Documents Required",
        "Documents needed for home loan:\n"
        "KYC Documents: PAN Card, Aadhaar Card, Passport, or Voter ID\n"
        "Income Documents (Salaried): Last 3 salary slips, Form 16, 6 months bank statements\n"
        "Income Documents (Self-Employed): ITR for 3 years, CA-certified financials, GST returns\n"
        "Property Documents: Sale agreement, title deed, approved building plan, NOC from society,\n"
        "encumbrance certificate, and property tax receipts"
    )
    pdf.chapter("7. Home Loan EMI Examples",
        "Sample EMI calculations:\n"
        "- Rs. 30 lakh at 9% for 20 years: EMI = Rs. 26,992, Total Interest = Rs. 34,78,080\n"
        "- Rs. 50 lakh at 8.5% for 25 years: EMI = Rs. 40,260, Total Interest = Rs. 70,78,000\n"
        "- Rs. 75 lakh at 9.5% for 30 years: EMI = Rs. 63,067, Total Interest = Rs. 1,52,04,120\n\n"
        "Making partial prepayments reduces principal faster and saves significant interest. "
        "For floating rate loans, EMI changes with RBI repo rate revisions."
    )
    out_path = os.path.join(OUTPUT_DIR, "home_loan_policy_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


def create_cibil_pdf():
    pdf = PDF("CIBIL Score and Credit Health Complete Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. What is CIBIL Score",
        "CIBIL Score is a 3-digit numeric summary of your credit history, ranging from 300 to 900. "
        "It is calculated based on your credit repayment behaviour across all loans and credit cards. "
        "A higher score indicates better creditworthiness. Most Indian banks use CIBIL score as the "
        "primary credit assessment tool for loan approvals."
    )
    pdf.chapter("2. CIBIL Score Ranges",
        "Score ranges and what they mean:\n"
        "- 300 to 549 (Poor): Very high risk. Most lenders will reject application.\n"
        "- 550 to 649 (Below Average): High risk. Limited options at very high rates.\n"
        "- 650 to 699 (Average): Moderate risk. Eligible for most loans at higher rates.\n"
        "  Minimum acceptable score of 650 required for personal loans.\n"
        "- 700 to 749 (Good): Low-moderate risk. Eligible for most loans at standard rates.\n"
        "- 750 to 799 (Very Good): Low risk. Eligible for best interest rates. Fast approval.\n"
        "- 800 to 900 (Excellent): Very low risk. Best rates, highest loan amounts, fastest approval. "
        "Banks proactively offer pre-approved loans for scores above 800."
    )
    pdf.chapter("3. How CIBIL Score is Calculated",
        "Factors affecting CIBIL score:\n"
        "1. Payment History (35%): Whether you paid EMIs and credit card bills on time.\n"
        "   Even one missed payment can drop score by 50-100 points.\n"
        "2. Credit Utilisation (30%): Keep credit card utilisation below 30% of limit.\n"
        "3. Credit Age (15%): Average age of all credit accounts. Older accounts help score.\n"
        "4. Credit Mix (10%): Balance between secured and unsecured credit.\n"
        "5. New Credit Enquiries (10%): Each loan application reduces score by 5-10 points temporarily."
    )
    pdf.chapter("4. Minimum CIBIL Score by Loan Type",
        "Minimum credit scores required for different loan products:\n"
        "- Personal Loan: Minimum 650-700. Best rates above 750.\n"
        "- Home Loan: Minimum 650. Above 750 for best rates starting at 8.5%.\n"
        "- Car Loan: Minimum 600-650. Secured nature allows slightly lower score.\n"
        "- Business Loan: Minimum 700 for unsecured business loans.\n"
        "- Gold Loan: No minimum score (fully secured by gold).\n"
        "- Education Loan: Minimum 600-650 on co-applicant's score.\n"
        "- Credit Card: Minimum 650-700; premium cards need 750 and above.\n"
        "- Two-Wheeler Loan: Minimum 600 (secured by vehicle)."
    )
    pdf.chapter("5. How to Improve CIBIL Score",
        "Proven strategies to improve your CIBIL score:\n"
        "1. Pay EMIs on Time: Set auto-debit for all loan EMIs. Never miss a due date.\n"
        "2. Pay Credit Card Bills in Full: Pay full statement amount, not just minimum due.\n"
        "3. Keep Credit Utilisation Below 30%: If limit is Rs. 1 lakh, keep below Rs. 30,000.\n"
        "4. Do Not Close Old Accounts: Old credit history improves average credit age.\n"
        "5. Avoid Multiple Loan Applications: Apply to only one lender at a time.\n"
        "6. Dispute Errors: Check credit report annually and dispute incorrect entries.\n"
        "7. Time to Improve: Score can improve by 100-150 points in 12-18 months."
    )
    pdf.chapter("6. How to Check CIBIL Score",
        "Ways to check your CIBIL score:\n"
        "- Free Annual Check: One free credit report per year from CIBIL website www.cibil.com\n"
        "- Bank Apps: Most Indian bank apps show CIBIL score for free.\n"
        "- Third-party apps: Paytm, BankBazaar, OneScore, and CRED show free CIBIL scores.\n"
        "- Soft Inquiry: Self-checking score does NOT affect your score.\n"
        "- Recommended: Check every 3-4 months to catch errors early."
    )
    pdf.chapter("7. CIBIL Score Impact on Interest Rates",
        "Direct impact of CIBIL score on interest rate:\n"
        "Example on Rs. 30 lakh home loan for 20 years:\n"
        "- Score 800+: 8.5% rate -> Total interest Rs. 32.3 lakh\n"
        "- Score 650-700: 10% rate -> Total interest Rs. 41.6 lakh\n"
        "- Difference: Rs. 9.3 lakh extra interest for poor credit!\n\n"
        "For personal loans (Rs. 5 lakh, 3 years):\n"
        "- Score 800: 12% rate -> Total interest Rs. 97,000\n"
        "- Score 650: 20% rate -> Total interest Rs. 1,75,000\n"
        "- Savings: Rs. 78,000 by maintaining a good credit score."
    )
    out_path = os.path.join(OUTPUT_DIR, "cibil_score_credit_health_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


def create_car_loan_pdf():
    pdf = PDF("Car Loan and Vehicle Loan Policy Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Car Loan Overview",
        "A car loan is a secured loan for purchasing new or used vehicles. The vehicle serves as "
        "collateral until the loan is fully repaid. Car loans generally have lower interest rates "
        "than personal loans due to the secured nature. Upon full repayment, the hypothecation "
        "on the vehicle RC book is removed."
    )
    pdf.chapter("2. Car Loan Eligibility",
        "Who can apply for a car loan:\n"
        "- Age: 21 to 65 years at loan maturity\n"
        "- Minimum Income: Rs. 15,000 per month for salaried; Rs. 1.5 lakh per year net profit for self-employed\n"
        "- Credit Score: Minimum 650; best rates above 750\n"
        "- Employment: Minimum 1 year at current job for salaried; 2 years business for self-employed\n"
        "- Down Payment: Minimum 10-20% of on-road vehicle price\n"
        "- LTV: Up to 80-90% of ex-showroom price for new cars; 60-80% for used cars"
    )
    pdf.chapter("3. New vs Used Car Loan",
        "Key differences:\n"
        "New Car Loan:\n"
        "- Loan amount: Up to 90% of ex-showroom price\n"
        "- Interest rate: 7% to 11% per annum\n"
        "- Maximum tenure: 84 months (7 years)\n\n"
        "Used Car Loan:\n"
        "- Loan amount: Up to 80% of market value\n"
        "- Interest rate: 12% to 18% per annum (higher due to depreciation risk)\n"
        "- Maximum tenure: 60 months (5 years)\n"
        "- Vehicle age limit: Most lenders do not finance vehicles older than 5-7 years"
    )
    pdf.chapter("4. Car Loan Interest Rates and Charges",
        "Typical car loan charges:\n"
        "- New Car Interest Rate: 7% to 12% per annum\n"
        "- Used Car Interest Rate: 12% to 18% per annum\n"
        "- Processing Fee: Rs. 500 to Rs. 5,000 or 0.5% to 1% of loan amount\n"
        "- Prepayment Penalty: 3% to 6% of outstanding principal\n"
        "- Late Payment: Rs. 500 to Rs. 2,000 or 2% of overdue amount per month"
    )
    pdf.chapter("5. Car Loan Documents Required",
        "Documents needed:\n"
        "Identity and Address Proof: Aadhaar, PAN, Passport, or Voter ID\n"
        "Income Proof (Salaried): Last 3 salary slips, Form 16, 6 months bank statements\n"
        "Income Proof (Self-Employed): ITR for 2 years, business bank statements\n"
        "Vehicle Documents: Proforma invoice from dealer, vehicle insurance quote"
    )
    pdf.chapter("6. Two-Wheeler Loan",
        "Two-wheeler loan details:\n"
        "- Loan Amount: Rs. 20,000 to Rs. 5,00,000\n"
        "- Down Payment: 10-15% of on-road price\n"
        "- Interest Rate: 10% to 16% per annum\n"
        "- Maximum Tenure: 48 months (4 years)\n"
        "- Credit Score Required: Minimum 600\n"
        "- Minimum Income: Rs. 10,000 per month for salaried applicants"
    )
    pdf.chapter("7. Car Loan EMI Examples",
        "Sample EMI calculations:\n"
        "New Car - Rs. 8 lakh at 8.5% for 60 months: EMI = Rs. 16,427, Total Interest = Rs. 1,85,620\n"
        "New Car - Rs. 12 lakh at 9% for 84 months: EMI = Rs. 19,189, Total Interest = Rs. 4,11,876\n"
        "Used Car - Rs. 5 lakh at 14% for 48 months: EMI = Rs. 13,635, Total Interest = Rs. 1,54,480"
    )
    out_path = os.path.join(OUTPUT_DIR, "car_loan_vehicle_loan_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


def create_business_loan_pdf():
    pdf = PDF("Business Loan and MSME Loan Policy Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Business Loan Overview",
        "A business loan is a credit facility for businesses for working capital, expansion, equipment "
        "purchase, or operational needs. Business loans can be secured (backed by property or stock) "
        "or unsecured (based on business performance and credit history)."
    )
    pdf.chapter("2. Types of Business Loans",
        "Different business loan products:\n"
        "1. Term Loan: Fixed amount for specific purpose; repaid in EMIs over 1-10 years.\n"
        "2. Working Capital Loan: Short-term loan for day-to-day operations; tenure up to 12 months.\n"
        "3. Overdraft Facility: Credit limit against current account.\n"
        "4. Equipment Finance: For purchasing machinery or business equipment.\n"
        "5. MUDRA Loan (Shishu): Up to Rs. 50,000 at subsidised rates without collateral.\n"
        "6. MUDRA Loan (Kishore): Rs. 50,001 to Rs. 5 lakh without collateral.\n"
        "7. MUDRA Loan (Tarun): Rs. 5 lakh to Rs. 10 lakh."
    )
    pdf.chapter("3. Business Loan Eligibility",
        "Eligibility for business loans:\n"
        "- Business Age: Minimum 2-3 years of business operations\n"
        "- Annual Turnover: Minimum Rs. 20 lakh annual turnover\n"
        "- Credit Score: Minimum CIBIL 700 for unsecured; 650 for secured business loans\n"
        "- Profitability: Business should be profitable for at least 1-2 years\n"
        "- GST Registration: Mandatory for turnover above Rs. 40 lakh\n"
        "- ITR Filing: At least 2 years of filed Income Tax Returns required\n"
        "- No Defaults: No loan defaults, bounced cheques, or NPA history"
    )
    pdf.chapter("4. Business Loan Amounts and Rates",
        "Business loan specifics:\n"
        "- Unsecured Business Loan: Rs. 1 lakh to Rs. 50 lakh; interest 14% to 26% per annum\n"
        "- Secured Business Loan: Rs. 5 lakh to Rs. 5 crore; interest 10% to 18% per annum\n"
        "- Processing Fee: 1% to 3% of loan amount\n"
        "- Tenure: Working capital 12 months; term loans 3-7 years"
    )
    pdf.chapter("5. Government MSME Schemes",
        "Key government schemes for MSME financing:\n"
        "1. MUDRA Yojana: Loans up to Rs. 10 lakh for micro enterprises without collateral.\n"
        "2. CGTMSE Scheme: Guarantees up to Rs. 2 crore without collateral for MSMEs.\n"
        "3. Stand-Up India: Loans for SC/ST and women entrepreneurs from Rs. 10 lakh to Rs. 1 crore.\n"
        "Benefits: Lower interest rates of 8-12%, easier collateral norms, government guarantees."
    )
    pdf.chapter("6. Business Loan Documents Required",
        "Documents for business loan:\n"
        "KYC: PAN Card and Aadhaar of proprietor and business\n"
        "Business Registration: GST certificate, Shop Act license, Partnership deed\n"
        "Financial Documents: ITR for 2-3 years, audited balance sheet and P&L statement\n"
        "Bank Statements: Last 12 months business account statements\n"
        "Collateral Documents (if secured): Property documents, stock statements"
    )
    pdf.chapter("7. Reasons for Business Loan Rejection",
        "Why business loan applications fail:\n"
        "- Low Credit History: New businesses without credit track record\n"
        "- Insufficient Business Vintage: Less than 2 years of operations\n"
        "- Low Turnover: Revenue below lender threshold\n"
        "- Losses in Financials: Business showing losses in ITR\n"
        "- Poor Repayment History: Bounced cheques or existing defaults\n"
        "- Low Credit Score: Promoter CIBIL score below 700\n\n"
        "To improve: Maintain separate business bank account, file ITR regularly, "
        "and build credit gradually through smaller loans first."
    )
    out_path = os.path.join(OUTPUT_DIR, "business_loan_msme_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


if __name__ == "__main__":
    print("Generating comprehensive loan PDFs for Tata Mitra...")
    create_personal_loan_pdf()
    create_home_loan_pdf()
    create_cibil_pdf()
    create_car_loan_pdf()
    create_business_loan_pdf()
    print("\nAll 5 PDFs created in: uploads_seed/")
    print("Next: Start backend, then upload via Admin panel OR use the auto-upload script.")
