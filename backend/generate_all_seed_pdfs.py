"""
Generate 13 comprehensive Educational Knowledge PDFs for Tata Mitra RAG pipeline.
Output directory: backend/uploads_educational/
Run: python generate_all_seed_pdfs.py
"""
import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "uploads_educational")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class EduPDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.doc_title = title

    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(24, 76, 120)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  [EDUCATIONAL GUIDE] {self.doc_title}", border=0, ln=1, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def chapter(self, title, body):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, title, border=0, ln=1, fill=True)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, body)
        self.ln(4)

# 1. Personal Loan Policy Guide
def create_personal_loan_pdf():
    pdf = EduPDF("Personal Loan Policy Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Overview", "A personal loan is an unsecured loan provided by banks and NBFCs for personal expenses like travel, weddings, emergencies, or debt consolidation. No collateral is required.")
    pdf.chapter("2. Eligibility Criteria", "Age: 21 to 60 years. Minimum income: Rs. 20,000/month. CIBIL score: Minimum 650+ (750+ for best interest rates). Employment: Minimum 2 years total experience, 1 year at current employer.")
    pdf.chapter("3. Interest Rates and Fees", "Interest rates range from 10.5% to 24% p.a. Processing fee: 1% to 3%. Prepayment penalty: 2% to 5% of principal after lock-in period.")
    pdf.chapter("4. Required Documents", "KYC (Aadhaar, PAN), last 3 months salary slips, 6 months bank statement, Form 16.")
    pdf.output(os.path.join(OUTPUT_DIR, "01_Personal_Loan_Policy_Guide.pdf"))

# 2. Home Loan Tax and LTV Guide
def create_home_loan_pdf():
    pdf = EduPDF("Home Loan Tax Benefits and LTV Guide")
    pdf.add_page()
    pdf.chapter("1. Overview & LTV Limits", "Home loans fund purchase, construction, or renovation of residential property. RBI LTV limits: Up to Rs. 30 Lakhs loan = 90% LTV; Rs. 30L-75L = 80% LTV; Above Rs. 75L = 75% LTV.")
    pdf.chapter("2. Income Tax Benefits", "Section 24(b): Deduction up to Rs. 2 Lakhs per fiscal year on interest paid for self-occupied property.\nSection 80C: Tax deduction up to Rs. 1.5 Lakhs on principal repayment.\nSection 80EEA: Additional Rs. 1.5 Lakhs deduction on interest for first-time affordable homebuyers.")
    pdf.chapter("3. Tenures & Rates", "Tenures up to 30 years (360 months). Interest rates range between 8.35% and 10.5% p.a.")
    pdf.output(os.path.join(OUTPUT_DIR, "02_Home_Loan_Tax_and_LTV_Guide.pdf"))

# 3. Financial Literacy & Credit Management
def create_financial_literacy_pdf():
    pdf = EduPDF("Financial Literacy and Debt Management")
    pdf.add_page()
    pdf.chapter("1. Understanding Debt-to-Income", "DTI ratio measures total monthly EMI obligations against gross monthly income. Lenders cap DTI at 40% to 50% for responsible lending.")
    pdf.chapter("2. Emergency Fund & Planning", "Borrowers should maintain 6 months of living expenses in liquid funds before taking long-term debt.")
    pdf.chapter("3. Snowball vs Avalanche Method", "Avalanche method pays highest interest loans first; Snowball pays smallest balance first for psychological momentum.")
    pdf.output(os.path.join(OUTPUT_DIR, "03_Financial_Literacy_and_Debt_Management.pdf"))

# 4. Loan FAQ & Common Questions
def create_loan_faq_pdf():
    pdf = EduPDF("Loan FAQ and Essential Guide")
    pdf.add_page()
    pdf.chapter("1. Credit Score FAQ", "Can I get a loan without a CIBIL score? New-to-credit borrowers can get loans via FD-backed credit cards, NBFCs, or fintechs using bank statement analytics.")
    pdf.chapter("2. Prepayment FAQ", "Is prepayment beneficial? Yes, prepaying early in the tenure saves maximum interest because EMIs in initial years are interest-heavy.")
    pdf.output(os.path.join(OUTPUT_DIR, "04_Loan_FAQ_and_Essential_Guide.pdf"))

# 5. Tata Mitra Policy Guidelines
def create_tata_mitra_guidelines_pdf():
    pdf = EduPDF("Tata Mitra Advisory Guidelines")
    pdf.add_page()
    pdf.chapter("1. Responsible Lending", "Total EMI obligations across all active loans must not exceed 50% of gross monthly income.")
    pdf.chapter("2. Verification Standards", "Income proof, bank statements, and credit score verification are mandatory before final loan approval.")
    pdf.output(os.path.join(OUTPUT_DIR, "05_Tata_Mitra_Advisory_Guidelines.pdf"))

# 6. Education Loan & PM Vidyalakshmi
def create_education_loan_pdf():
    pdf = EduPDF("Education Loan and PM Vidyalakshmi Portal Guide")
    pdf.add_page()
    pdf.chapter("1. Education Loan Basics", "Funds tuition, hostel, books, and study expenses in India or abroad for students aged 16-35.")
    pdf.chapter("2. Collateral Norms", "Loans up to Rs. 4 Lakhs: No collateral required.\nLoans Rs. 4L to 7.5L: Co-applicant + third-party guarantee.\nLoans above Rs. 7.5L: Tangible collateral (property, FD, LIC) required.")
    pdf.chapter("3. Moratorium & Tax Benefits", "Moratorium Period: Course duration + 12 months (or 6 months after getting job). Section 80E provides 100% tax deduction on interest paid for 8 years with no upper cap.")
    pdf.chapter("4. PM Vidyalakshmi Portal", "Single window portal (www.vidyalakshmi.co.in) to apply to 38+ banks simultaneously. Full interest subsidy under CSIS for EWS families (income below Rs. 4.5L).")
    pdf.output(os.path.join(OUTPUT_DIR, "06_Education_Loan_and_PM_Vidyalakshmi_Guide.pdf"))

# 7. Gold Loan and LTV Rules
def create_gold_loan_pdf():
    pdf = EduPDF("Gold Loan and RBI LTV Rules")
    pdf.add_page()
    pdf.chapter("1. Gold Loan Basics", "Secured loan obtained by pledging gold ornaments (18 to 24 karat). Fast approval within 30-60 minutes.")
    pdf.chapter("2. RBI LTV Rules", "RBI caps maximum Loan-to-Value (LTV) at 75% of gold market value. Purity evaluated via karat meter.")
    pdf.chapter("3. Rates & Repayment", "Interest rates: 7% to 13% at banks, 12% to 26% at NBFCs. Options: Bullet payment (pay total interest + principal at end), EMI, or monthly interest payment. No CIBIL score required.")
    pdf.output(os.path.join(OUTPUT_DIR, "07_Gold_Loan_and_LTV_Rules.pdf"))

# 8. Business & MSME MUDRA Loan Guide
def create_business_loan_pdf():
    pdf = EduPDF("Business and MSME MUDRA Loan Guide")
    pdf.add_page()
    pdf.chapter("1. MUDRA Loan Categories", "Pradhan Mantri MUDRA Yojana offers collateral-free business loans under 3 categories:\n- Shishu: Loans up to Rs. 50,000 for micro startups\n- Kishore: Loans Rs. 50,001 to Rs. 5 Lakhs for expanding units\n- Tarun: Loans Rs. 5,00,001 to Rs. 10 Lakhs for established enterprises")
    pdf.chapter("2. CGTMSE Scheme", "Credit Guarantee Fund Trust for Micro and Small Enterprises provides collateral-free loans up to Rs. 2 Crores to eligible MSMEs with government guarantee coverage.")
    pdf.chapter("3. Documents Required", "Business registration, GST returns, 2 years ITR, audited balance sheet, 12 months bank statement.")
    pdf.output(os.path.join(OUTPUT_DIR, "08_Business_and_MSME_MUDRA_Loan_Guide.pdf"))

# 9. Credit Score Repair & CIBIL Guide
def create_cibil_guide_pdf():
    pdf = EduPDF("Credit Score Repair and CIBIL Master Guide")
    pdf.add_page()
    pdf.chapter("1. Credit Score Ranges", "300-549: Poor; 550-649: Fair; 650-749: Good; 750-900: Excellent (qualifies for lowest interest rates).")
    pdf.chapter("2. Factors Influencing Score", "Repayment History (35%), Credit Utilization Ratio (30% - keep below 30%), Credit Mix (25%), Hard Inquiries (10%).")
    pdf.chapter("3. How to Improve CIBIL Score", "Pay all EMIs and credit card bills before due date. Keep credit utilization below 30%. Rectify errors on CIBIL report via dispute resolution. Do not apply for multiple loans simultaneously. Wait 6 months between applications.")
    pdf.output(os.path.join(OUTPUT_DIR, "09_Credit_Score_Repair_and_CIBIL_Guide.pdf"))

# 10. Loan Prepayment & RBI Rules
def create_prepayment_pdf():
    pdf = EduPDF("Loan Prepayment and RBI Penalty Rules")
    pdf.add_page()
    pdf.chapter("1. RBI Guidelines on Foreclosure", "RBI Rules: Lenders CANNOT charge prepayment or foreclosure penalties on floating rate home loans and floating rate personal loans to individual borrowers.")
    pdf.chapter("2. Fixed Rate Loan Charges", "Fixed rate loans may attract 2% to 4% foreclosure charges on outstanding principal balance if prepaid before tenure maturity.")
    pdf.chapter("3. Prepayment Strategy", "Part-prepaying early in loan tenure reduces principal faster and saves substantial interest compared to prepaying near loan maturity.")
    pdf.output(os.path.join(OUTPUT_DIR, "10_Loan_Prepayment_and_RBI_Rules.pdf"))

# 11. Debt to Income DTI Master Guide
def create_dti_guide_pdf():
    pdf = EduPDF("Debt to Income DTI Master Guide")
    pdf.add_page()
    pdf.chapter("1. DTI Formula", "DTI Ratio = (Total Monthly EMI Obligations / Gross Monthly Income) * 100.")
    pdf.chapter("2. Benchmark Levels", "Below 35%: Healthy debt load.\n35% to 50%: Acceptable limit for most banks.\nAbove 50%: High risk - loan approval difficult or rejected.")
    pdf.chapter("3. Reducing DTI", "Pay off small credit card balances, consolidate debt into a lower-rate personal loan, or increase tenure to lower monthly EMI.")
    pdf.output(os.path.join(OUTPUT_DIR, "11_Debt_to_Income_DTI_Master_Guide.pdf"))

# 12. Borrower Rights & Banking Ombudsman
def create_ombudsman_pdf():
    pdf = EduPDF("Borrower Rights and Banking Ombudsman Guide")
    pdf.add_page()
    pdf.chapter("1. Fair Practice Code", "Lenders must provide transparent Sanction Letters detailing interest rates, processing fees, penal charges, and APR before disbursement.")
    pdf.chapter("2. Recovery Agent Guidelines", "RBI guidelines prohibit harassment, coercive calls before 8 AM or after 7 PM, or unauthorized visits by recovery agents.")
    pdf.chapter("3. RBI Ombudsman Dispute Process", "If a bank/NBFC does not resolve a grievance within 30 days, borrowers can file a free complaint online at cms.rbi.org.in under the Integrated Ombudsman Scheme.")
    pdf.output(os.path.join(OUTPUT_DIR, "12_Borrower_Rights_and_Banking_Ombudsman.pdf"))

# 13. Loan Balance Transfer and Top-Up Guide
def create_balance_transfer_pdf():
    pdf = EduPDF("Loan Balance Transfer and Top-Up Guide")
    pdf.add_page()
    pdf.chapter("1. Balance Transfer Overview", "Transferring an existing loan from a higher-interest lender to a lower-interest lender to reduce monthly EMI and overall interest payout.")
    pdf.chapter("2. When to Opt for Balance Transfer", "Beneficial if the interest rate differential is at least 0.5% to 1.0% and remaining loan tenure is longer than 3-5 years.")
    pdf.chapter("3. Top-Up Loans", "Additional loan facility offered over an existing home or personal loan at lower interest rates than fresh personal loans.")
    pdf.output(os.path.join(OUTPUT_DIR, "13_Loan_Balance_Transfer_and_TopUp_Guide.pdf"))

if __name__ == "__main__":
    create_personal_loan_pdf()
    create_home_loan_pdf()
    create_financial_literacy_pdf()
    create_loan_faq_pdf()
    create_tata_mitra_guidelines_pdf()
    create_education_loan_pdf()
    create_gold_loan_pdf()
    create_business_loan_pdf()
    create_cibil_guide_pdf()
    create_prepayment_pdf()
    create_dti_guide_pdf()
    create_ombudsman_pdf()
    create_balance_transfer_pdf()
    print("Successfully generated all 13 Educational Knowledge PDFs in backend/uploads_educational/")
