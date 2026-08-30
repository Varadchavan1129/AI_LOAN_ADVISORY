"""
Generate 8 more comprehensive PDFs for Tata Mitra RAG pipeline.
Run: python generate_more_pdfs.py
"""
import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads_seed2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class PDF(FPDF):
    def __init__(self, title):
        super().__init__()
        self.doc_title = title

    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(20, 80, 140)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  {self.doc_title}", border=0, ln=1, fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def chapter(self, title, body):
        self.set_font("Helvetica", "B", 11)
        self.set_fill_color(220, 235, 255)
        self.cell(0, 8, title, border=0, ln=1, fill=True)
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, body)
        self.ln(4)


# ─────────────────────────────────────────────────────────────────────────────
# PDF 1: Education Loan Guide
# ─────────────────────────────────────────────────────────────────────────────
def create_education_loan_pdf():
    pdf = PDF("Education Loan Complete Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. What is an Education Loan",
        "An education loan (student loan) is a type of loan designed to help students fund their higher "
        "education expenses including tuition fees, hostel charges, books, laptops, and other study-related "
        "costs. Education loans are available for studies in India and abroad. The interest on education "
        "loans is eligible for tax deduction under Section 80E of the Income Tax Act for 8 years from the "
        "year repayment begins. No tax deduction limit applies under Section 80E."
    )
    pdf.chapter("2. Education Loan Eligibility",
        "Who can apply for an education loan:\n"
        "- Student must be an Indian citizen\n"
        "- Age: 16 to 35 years at time of application\n"
        "- Must have secured admission in a recognised institution (Indian or foreign)\n"
        "- Co-applicant: Parent, guardian, or spouse must co-apply\n"
        "- Co-applicant income is considered for repayment assessment\n"
        "- Academic performance: Some lenders require minimum 50-60% marks in previous qualifying exam\n"
        "- Accepted courses: Graduate, post-graduate, PhD, professional courses (MBA, MBBS, Engineering, Law)"
    )
    pdf.chapter("3. Education Loan Amounts",
        "Education loan limits in India:\n"
        "- Loans up to Rs. 4 lakh: No collateral required, no co-applicant income requirement\n"
        "- Loans Rs. 4 lakh to Rs. 7.5 lakh: Third-party guarantee required (no collateral)\n"
        "- Loans above Rs. 7.5 lakh: Tangible collateral required (property, FD, NSC, LIC policy)\n"
        "- Studies in India: Typically up to Rs. 10-20 lakh\n"
        "- Studies Abroad: Up to Rs. 1.5 crore depending on course and institution\n"
        "- Premier institutions (IIT, IIM, AIIMS): Higher loan amounts available with better terms\n"
        "- Coverage: Tuition fees, exam fees, library fees, hostel charges, books, laptop, travel expenses"
    )
    pdf.chapter("4. Education Loan Interest Rates and Repayment",
        "Interest rate structure:\n"
        "- Base interest rate: 8.15% to 15% per annum depending on lender and course\n"
        "- Concession: 0.5% to 1% interest reduction for girl students at most banks\n"
        "- Vidya Lakshmi scheme: Government portal for education loans with subsidised rates\n"
        "- Central Scheme for Interest Subsidy (CSIS): Full interest subsidy during moratorium for EWS students\n\n"
        "Moratorium Period:\n"
        "- Course duration + 12 months, or 6 months after getting a job, whichever is earlier\n"
        "- During moratorium: Simple interest accrues; no EMI required\n"
        "- Repayment tenure: 5 to 15 years after moratorium ends\n"
        "- Pre-payment: No penalty for early repayment of education loans"
    )
    pdf.chapter("5. Education Loan Documents Required",
        "Documents needed for education loan:\n"
        "KYC: Aadhaar, PAN, passport photos of student and co-applicant\n"
        "Academic: 10th, 12th, graduation marksheets, entrance exam scorecard\n"
        "Admission: Admission letter from institution, fee structure, prospectus\n"
        "Income of Co-applicant: Salary slips, ITR, bank statements (last 6 months)\n"
        "Collateral (if applicable): Property documents, FD receipts, LIC policy\n"
        "Institution: Recognition certificate, NAAC/NBA accreditation if applicable"
    )
    pdf.chapter("6. PM Vidyalakshmi Scheme",
        "Government education loan portal details:\n"
        "- Single portal for applying to education loans from multiple banks simultaneously\n"
        "- Available at www.vidyalakshmi.co.in\n"
        "- 38+ banks registered on the portal including SBI, PNB, Bank of Baroda\n"
        "- Loans up to Rs. 10 lakh without collateral under Central Sector Scheme\n"
        "- Interest subsidy for students from economically weaker sections (family income below Rs. 4.5 lakh)\n"
        "- Moratorium interest fully covered by government under CSIS scheme"
    )
    pdf.chapter("7. Education Loan Repayment Tips",
        "Managing education loan repayment:\n"
        "- Start partial repayment during moratorium to reduce total interest burden\n"
        "- Use Section 80E tax benefit (entire interest is deductible, no cap)\n"
        "- If employed, set up auto-debit to avoid missed payments\n"
        "- Consider employer education assistance programs if available\n"
        "- For STEM courses: Higher salary expectation means shorter effective repayment\n"
        "- Default consequences: Co-applicant credit score gets impacted; collateral may be seized\n"
        "- Restructuring: Available for genuine financial hardship; contact bank early"
    )
    out_path = os.path.join(OUTPUT_DIR, "education_loan_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 2: Gold Loan Guide
# ─────────────────────────────────────────────────────────────────────────────
def create_gold_loan_pdf():
    pdf = PDF("Gold Loan Complete Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. What is a Gold Loan",
        "A gold loan is a secured loan where the borrower pledges gold jewellery or ornaments as "
        "collateral and receives a loan against it. The lender holds the gold safely until the loan "
        "is fully repaid. Gold loans are one of the fastest-approved loans in India, often disbursed "
        "within 30-60 minutes. They are ideal for short-term financial emergencies."
    )
    pdf.chapter("2. Gold Loan Eligibility",
        "Gold loan eligibility is very simple compared to other loans:\n"
        "- Age: 18 to 75 years\n"
        "- No minimum income requirement\n"
        "- No CIBIL score requirement (fully secured by gold)\n"
        "- No employment proof required\n"
        "- Gold must be 18 to 22 karat purity (minimum 18 karat)\n"
        "- Gold coins accepted at most lenders (up to 50 grams per RBI guidelines)\n"
        "- Gold bars and bullion: Not accepted by most banks; may be accepted by NBFCs\n"
        "- Jewellery with precious stones: Value assessed for gold part only"
    )
    pdf.chapter("3. Gold Loan Amount and LTV",
        "How much you can borrow against gold:\n"
        "- LTV (Loan-to-Value): As per RBI mandate, maximum 75% of gold value\n"
        "- Example: Gold worth Rs. 1 lakh -> Maximum loan = Rs. 75,000\n"
        "- Gold valuation: Done at lender's premises by certified appraiser at current market rate\n"
        "- Minimum loan: Rs. 1,000 to Rs. 10,000 depending on lender\n"
        "- Maximum loan: Rs. 1.5 crore at banks; NBFCs may offer higher\n"
        "- Muthoot Finance, Manappuram: Specialised NBFCs with quick gold loans\n"
        "- Bullet repayment option: Pay only interest monthly, principal at end of tenure"
    )
    pdf.chapter("4. Gold Loan Interest Rates",
        "Interest rates and charges for gold loans:\n"
        "- Banks: 7% to 13% per annum (SBI, HDFC, ICICI, Axis)\n"
        "- NBFCs (Muthoot, Manappuram): 12% to 26% per annum (higher but faster)\n"
        "- Processing fee: Rs. 0 to Rs. 500 (very low or nil)\n"
        "- Valuation fee: Rs. 250 to Rs. 500 typically\n"
        "- Storage charges: Usually nil for banks; may apply for NBFCs\n"
        "- Repayment methods: Monthly interest payment, bullet repayment, or EMI\n"
        "- Tenure: 3 months to 36 months"
    )
    pdf.chapter("5. Gold Loan vs Personal Loan Comparison",
        "When to choose gold loan over personal loan:\n"
        "Gold Loan Advantages:\n"
        "- No CIBIL score needed\n"
        "- Disbursed within 30-60 minutes\n"
        "- Interest rate 7-13% (lower than personal loan 12-24%)\n"
        "- No income proof required\n"
        "- Flexible repayment options\n\n"
        "Gold Loan Disadvantages:\n"
        "- Gold is at risk if you cannot repay\n"
        "- Maximum 75% of gold value only\n"
        "- Shorter tenure (max 3 years)\n"
        "- Risk of gold auction if defaulted\n\n"
        "Choose gold loan when: You have gold, need money urgently, have low credit score\n"
        "Choose personal loan when: You don't have gold to pledge, need longer tenure"
    )
    pdf.chapter("6. Gold Auction and Default",
        "What happens if you cannot repay a gold loan:\n"
        "- If EMI/interest missed for 90 days: Loan becomes NPA (Non-Performing Asset)\n"
        "- Lender sends notice to repay within 15 days\n"
        "- If not repaid after notice: Lender can AUCTION the gold\n"
        "- Auction proceeds first cover loan + interest + penalty; surplus returned to borrower\n"
        "- Credit score impact: Default is reported and reduces CIBIL score significantly\n"
        "- To avoid auction: Communicate with lender early; request restructuring or time extension"
    )
    out_path = os.path.join(OUTPUT_DIR, "gold_loan_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 3: Loan Against Property
# ─────────────────────────────────────────────────────────────────────────────
def create_lap_pdf():
    pdf = PDF("Loan Against Property (LAP) Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. What is Loan Against Property",
        "Loan Against Property (LAP) or Mortgage Loan is a secured loan where you pledge your "
        "residential or commercial property as collateral. Unlike a home loan (which is for buying "
        "property), LAP can be used for any purpose: business expansion, medical expenses, education, "
        "debt consolidation, or personal needs. The property remains yours; you just pledge it as security."
    )
    pdf.chapter("2. LAP Eligibility",
        "Who can apply for Loan Against Property:\n"
        "- Age: 25 to 70 years at loan maturity\n"
        "- Salaried: Minimum income Rs. 30,000/month; at least 3 years work experience\n"
        "- Self-Employed: Minimum 3 years business continuity with ITR showing profit\n"
        "- CIBIL Score: Minimum 650; above 700 preferred\n"
        "- Property: Must be free from any existing mortgage or legal disputes\n"
        "- Property types: Residential flat, house, commercial shop, office space, industrial property\n"
        "- Property age: Generally not more than 30-40 years old"
    )
    pdf.chapter("3. LAP Loan Amount and LTV",
        "How much you can borrow against property:\n"
        "- Residential property: Up to 60-70% of property market value\n"
        "- Commercial property: Up to 55-65% of property market value\n"
        "- Industrial property: Up to 50-60% of property value\n"
        "- Minimum loan: Rs. 10 lakh\n"
        "- Maximum loan: Rs. 10 crore (some lenders offer more)\n"
        "- LTV example: Property worth Rs. 1 crore -> Maximum LAP = Rs. 60-70 lakh\n"
        "- Property valuation done by bank-empanelled independent valuer at borrower's cost"
    )
    pdf.chapter("4. LAP Interest Rates and Tenure",
        "Loan Against Property pricing:\n"
        "- Interest rate: 9% to 14% per annum (between home loan and personal loan rates)\n"
        "- Floating rate: Linked to MCLR or repo rate\n"
        "- Fixed rate: 10% to 15% per annum\n"
        "- Maximum tenure: 15 to 20 years\n"
        "- Processing fee: 0.5% to 1.5% of loan amount\n"
        "- Property valuation fee: Rs. 5,000 to Rs. 15,000\n"
        "- Legal charges: Rs. 5,000 to Rs. 20,000 for title search\n"
        "- Prepayment: 2% to 4% penalty on floating rate loans; nil after 3 years at some lenders"
    )
    pdf.chapter("5. LAP Documents Required",
        "Documents for Loan Against Property:\n"
        "KYC: PAN, Aadhaar, passport photos\n"
        "Property: Title deed, sale agreement, approved building plan, encumbrance certificate, "
        "property tax receipts, NOC from housing society\n"
        "Income (Salaried): Last 3 months salary slips, Form 16, 6 months bank statements\n"
        "Income (Self-Employed): ITR for 3 years, CA-certified financials, GST returns\n"
        "Other: Property insurance copy, no objection from existing occupants"
    )
    pdf.chapter("6. LAP vs Home Loan vs Personal Loan",
        "Comparison of LAP with other loan types:\n"
        "LAP vs Home Loan:\n"
        "- Home loan: Only for buying/building a home; LAP: Any purpose\n"
        "- Home loan: Interest from 8.5%; LAP: Interest from 9%\n"
        "- Home loan: Tax benefits under 80C and 24(b); LAP: No tax benefit unless used for business\n\n"
        "LAP vs Personal Loan:\n"
        "- LAP: Secured (lower rate 9-14%); Personal loan: Unsecured (higher rate 12-24%)\n"
        "- LAP: Longer tenure up to 15-20 years; Personal loan: Max 5-7 years\n"
        "- LAP: Higher loan amount; Personal loan: Limited to Rs. 40 lakh usually\n"
        "- LAP: Property at risk; Personal loan: No asset at risk"
    )
    out_path = os.path.join(OUTPUT_DIR, "loan_against_property_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 4: Loan FAQ - Common Questions and Answers
# ─────────────────────────────────────────────────────────────────────────────
def create_faq_pdf():
    pdf = PDF("Loan FAQ - Most Frequently Asked Questions - Tata Mitra")
    pdf.add_page()
    pdf.chapter("Q1. What is the minimum salary needed to get a personal loan?",
        "Most banks and NBFCs require a minimum monthly salary of Rs. 15,000 to Rs. 25,000 for personal "
        "loans in metro cities. For non-metro areas, the minimum may be lower at Rs. 12,000 to Rs. 15,000. "
        "Some digital lenders may offer loans to individuals earning as low as Rs. 10,000/month. "
        "The higher your salary, the larger the loan amount you can qualify for."
    )
    pdf.chapter("Q2. Can I get a loan without a CIBIL score?",
        "Yes, it is possible to get loans without a CIBIL score in certain situations:\n"
        "- Gold Loan: No CIBIL score required (100% secured by gold)\n"
        "- Secured loans against FD, PPF, insurance policy: No or low score acceptable\n"
        "- NBFC and fintech lenders: May use alternative credit scoring (bank statement analysis)\n"
        "- Co-applicant: Applying with someone who has a good score improves chances\n"
        "- Salary account: Having a long relationship with your bank helps\n"
        "However, for unsecured personal loans at banks, CIBIL score of 650+ is typically mandatory."
    )
    pdf.chapter("Q3. How much loan can I get on a salary of Rs. 30,000 per month?",
        "With a monthly salary of Rs. 30,000, your maximum loan eligibility depends on intent:\n"
        "Personal Loan: Typically 10-15x net monthly salary = Rs. 3 lakh to Rs. 4.5 lakh\n"
        "Home Loan: Typically 60x monthly salary = up to Rs. 18 lakh (at 9%, 20 years)\n"
        "Car Loan: Up to 80-90% of ex-showroom price, EMI limited to 40-50% of income = Rs. 12,000-15,000/month\n"
        "Maximum EMI rule: Total EMIs should not exceed 40-50% of income = Rs. 12,000 to Rs. 15,000/month max EMI capacity"
    )
    pdf.chapter("Q4. What happens if I miss an EMI payment?",
        "Consequences of missing an EMI payment:\n"
        "- Penalty: Late payment charge of Rs. 500 to Rs. 2,000 or 2-3% of overdue EMI\n"
        "- Credit Score Impact: Reduces CIBIL score by 50-100 points immediately\n"
        "- 30 days late: Marked as 'late payment' in credit bureau report\n"
        "- 90 days late: Loan marked as NPA (Non-Performing Asset)\n"
        "- Legal action: Lender may initiate recovery proceedings after 90+ days\n"
        "- Collection calls: Recovery agents may contact you\n"
        "Solution: Contact lender BEFORE missing EMI; request restructuring or moratorium"
    )
    pdf.chapter("Q5. Can I have multiple loans at the same time?",
        "Yes, you can have multiple loans simultaneously, but:\n"
        "- All EMIs combined must be within 50% of your monthly income (DTI limit)\n"
        "- Each new loan application adds a hard inquiry reducing CIBIL score slightly\n"
        "- Lenders check all active loans before approving new ones\n"
        "- Too many loans signal credit stress and may lead to rejection\n"
        "- Manageable combinations: Home loan + car loan + credit card (if DTI is within limits)\n"
        "- Avoid: Multiple personal loans simultaneously as it signals financial distress"
    )
    pdf.chapter("Q6. How long does loan approval take?",
        "Loan approval timelines vary by loan type:\n"
        "- Gold Loan: 30 to 60 minutes (same day)\n"
        "- Personal Loan (digital): 2 to 24 hours (instant to next day)\n"
        "- Personal Loan (bank): 2 to 7 working days\n"
        "- Car Loan: 1 to 3 working days\n"
        "- Home Loan: 7 to 21 working days (includes property legal verification)\n"
        "- Loan Against Property: 10 to 30 working days\n"
        "- Business Loan: 3 to 15 working days\n"
        "- Education Loan: 7 to 15 working days"
    )
    pdf.chapter("Q7. What is the difference between fixed and floating interest rates?",
        "Fixed Rate:\n"
        "- Interest rate remains constant throughout the loan tenure\n"
        "- EMI amount never changes\n"
        "- Suitable when interest rates are expected to rise\n"
        "- Usually 0.5% to 1% higher than floating rates\n\n"
        "Floating Rate:\n"
        "- Interest rate changes with market (RBI repo rate changes)\n"
        "- EMI may change when rate is revised\n"
        "- Suitable when interest rates are expected to fall\n"
        "- Lower starting rate than fixed\n"
        "- RBI has mandated: No prepayment penalty on floating rate retail loans"
    )
    pdf.chapter("Q8. Can NRI (Non-Resident Indian) apply for loans in India?",
        "NRIs can avail several loan products in India:\n"
        "- NRI Home Loan: To buy property in India; repayment from NRE/NRO account\n"
        "- NRI Personal Loan: Offered by select banks; usually needs co-applicant in India\n"
        "- Loan Against NRI Property: If NRI owns property in India\n"
        "- Loan Against NRE/NRO FD: Up to 90% of FD value; low interest rate\n"
        "Requirements for NRI loans: Passport, visa, overseas address proof, Indian address proof, "
        "salary certificate in foreign currency, NRE/NRO bank account, Power of Attorney to a resident Indian"
    )
    out_path = os.path.join(OUTPUT_DIR, "loan_faq_common_questions.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 5: RBI Guidelines and Banking Regulations
# ─────────────────────────────────────────────────────────────────────────────
def create_rbi_guidelines_pdf():
    pdf = PDF("RBI Guidelines and Banking Regulations for Borrowers - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Key RBI Borrower Rights",
        "As a borrower, you have these rights under RBI guidelines:\n"
        "- Right to receive all loan terms in writing before signing\n"
        "- Right to a copy of the loan agreement at no extra charge\n"
        "- Right to be informed of all fees and charges upfront\n"
        "- Right to receive one free CIBIL report per year\n"
        "- Right to approach Banking Ombudsman for complaints\n"
        "- Right to pre-close any floating-rate loan without penalty\n"
        "- Right to know reason for loan rejection in writing (if requested)\n"
        "- Protection from abusive debt collection practices"
    )
    pdf.chapter("2. RBI Interest Rate Regulations",
        "RBI mandated rules on interest rates:\n"
        "- Benchmark: All floating rate loans must be linked to external benchmarks (repo rate, MCLR)\n"
        "- Transparency: Annual Percentage Rate (APR) must be disclosed including all charges\n"
        "- No hidden charges: All fees must be disclosed in the loan sanction letter\n"
        "- Prepayment: No prepayment penalty on floating-rate personal loans and home loans for individuals\n"
        "- Rate revision: Banks must notify borrowers 30 days before changing interest rate\n"
        "- Base rate: Banks cannot lend below their base rate (MCLR) to most retail borrowers\n"
        "- Penal interest: Limited to reasonable amounts; cannot be charged compoundingly"
    )
    pdf.chapter("3. EMI Moratorium Rules",
        "RBI guidelines on loan moratorium:\n"
        "- Banks must offer moratorium in genuine financial hardship cases\n"
        "- During moratorium: No EMI required but interest continues to accrue\n"
        "- Post-moratorium: Accrued interest can be added to principal or paid separately\n"
        "- Moratorium does not improve credit score but should not reduce it if granted officially\n"
        "- Maximum moratorium: Typically 3 to 6 months; extended periods need lender approval\n"
        "- Restructuring: Lenders must offer restructuring options before classifying as NPA"
    )
    pdf.chapter("4. Loan Recovery and Collection Rules",
        "RBI guidelines on debt recovery:\n"
        "- Recovery agents must carry valid ID and authorization from lender\n"
        "- No harassment, intimidation, or public shaming allowed\n"
        "- Collection calls only between 8 AM and 7 PM\n"
        "- Contacting employer or family members is restricted\n"
        "- Borrower has right to request communication only in writing\n"
        "- Complaint mechanism: Each bank must have Grievance Redressal Officer\n"
        "- Escalation: Banking Ombudsman -> RBI Integrated Ombudsman Scheme (IOS)\n"
        "- Helpline: RBI Complaint portal at cms.rbi.org.in"
    )
    pdf.chapter("5. Digital Lending Regulations (2022)",
        "RBI digital lending guidelines effective 2022:\n"
        "- All digital loans must be disbursed directly to bank account of borrower\n"
        "- No disbursement to third parties allowed\n"
        "- Digital lending apps must display all APR, processing fees, cooling-off period\n"
        "- Cooling-off period: Borrower can cancel loan within 3 days for loans up to 3 months tenure\n"
        "- Data collection: Only with explicit borrower consent; data sharing restricted\n"
        "- Lending apps must be registered with RBI or partner with registered NBFC/bank\n"
        "- Unregistered lending apps are illegal; report them to RBI"
    )
    pdf.chapter("6. Credit Score and Credit Bureau Regulations",
        "RBI rules on credit bureaus and credit scores:\n"
        "- Four licensed credit bureaus in India: TransUnion CIBIL, Experian, Equifax, CRIF High Mark\n"
        "- Banks must report all loan accounts within 30 days of opening\n"
        "- Monthly updates on payment status mandatory\n"
        "- Dispute resolution: Credit bureau must resolve disputes within 30 days\n"
        "- Free annual report: Every individual gets one free report per year from each bureau\n"
        "- Inquiry retention: Hard inquiries visible for 2 years; soft inquiries not visible to lenders\n"
        "- Negative information: Defaults and settlements remain on report for 7 years"
    )
    out_path = os.path.join(OUTPUT_DIR, "rbi_guidelines_borrower_rights.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 6: Balance Transfer and Loan Refinancing
# ─────────────────────────────────────────────────────────────────────────────
def create_balance_transfer_pdf():
    pdf = PDF("Balance Transfer and Loan Refinancing Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. What is Loan Balance Transfer",
        "A loan balance transfer (also called refinancing) is transferring your existing loan from one "
        "lender to another for better terms - typically a lower interest rate. The new lender pays off "
        "your existing loan and you repay the new lender. Balance transfer is most beneficial for home "
        "loans and large personal loans where even a 0.5% rate reduction saves significant money."
    )
    pdf.chapter("2. When to Consider Balance Transfer",
        "Ideal situations for balance transfer:\n"
        "- Interest rate offered by new lender is at least 0.5% to 1% lower than current rate\n"
        "- You have a large outstanding loan amount (higher savings from lower rate)\n"
        "- Remaining tenure is substantial (more remaining tenure = more savings)\n"
        "- Your credit score has improved since you took the original loan\n"
        "- Current lender refuses to reduce rate despite repo rate cuts\n"
        "- You want to consolidate multiple high-interest loans into one lower-rate loan\n\n"
        "Avoid balance transfer if:\n"
        "- Only 12-24 months of tenure remaining (savings won't cover transfer costs)\n"
        "- Processing fees of new lender are very high\n"
        "- Prepayment penalty on current loan is substantial"
    )
    pdf.chapter("3. Balance Transfer Calculation",
        "How to calculate if balance transfer is beneficial:\n"
        "Example: Rs. 50 lakh home loan, 15 years remaining, current rate 9.5%, new rate 8.75%\n"
        "- Current EMI at 9.5%: Rs. 52,200/month, Total interest remaining: Rs. 43.9 lakh\n"
        "- New EMI at 8.75%: Rs. 49,700/month, Total interest remaining: Rs. 39.5 lakh\n"
        "- Monthly savings: Rs. 2,500, Annual savings: Rs. 30,000\n"
        "- Total savings over 15 years: Rs. 4.5 lakh\n"
        "- Transfer costs: Processing fee (Rs. 25,000) + legal charges (Rs. 15,000) = Rs. 40,000\n"
        "- Net savings: Rs. 4.5 lakh - Rs. 40,000 = Rs. 4.1 lakh - Highly beneficial!"
    )
    pdf.chapter("4. Balance Transfer Process",
        "Steps to complete a balance transfer:\n"
        "1. Get Foreclosure letter from current lender (states exact outstanding amount)\n"
        "2. Apply to new lender with all documents + foreclosure letter\n"
        "3. New lender processes application and sanctions loan\n"
        "4. New lender pays current lender directly (you don't receive cash)\n"
        "5. Current lender provides NOC (No Objection Certificate) and releases property documents\n"
        "6. New lender registers the mortgage\n"
        "7. Start repaying new lender from next month\n"
        "Timeline: 15 to 30 working days typically"
    )
    pdf.chapter("5. Top-Up Loan at Transfer",
        "Getting additional funds during balance transfer:\n"
        "- Top-up loan: Additional loan sanctioned over and above the balance transfer amount\n"
        "- Amount: Up to 70-80% of property value minus existing outstanding\n"
        "- Rate: Usually 0.25% to 0.5% higher than home loan transfer rate\n"
        "- Use: Any purpose - renovation, education, medical, business\n"
        "- Single EMI: Top-up and balance transfer merged into one EMI\n"
        "- Advantage: Better rate than personal loan for the additional funds needed"
    )
    pdf.chapter("6. Personal Loan Balance Transfer",
        "Balance transfer for personal loans:\n"
        "- Transfer outstanding balance to new lender at lower rate\n"
        "- Example: Rs. 3 lakh personal loan at 20% transferred to 14% saves Rs. 15,000-20,000\n"
        "- Eligibility: Good repayment track record with current lender (12+ months)\n"
        "- Minimum outstanding: Most lenders require Rs. 50,000+ to be worth transferring\n"
        "- New lender's criteria: CIBIL 700+, stable employment, income as per guidelines\n"
        "- Documents: Current loan NOC, outstanding statement, 6 months bank statements showing EMI"
    )
    out_path = os.path.join(OUTPUT_DIR, "balance_transfer_refinancing_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 7: Agriculture and Kisan Loan Guide
# ─────────────────────────────────────────────────────────────────────────────
def create_agriculture_loan_pdf():
    pdf = PDF("Agriculture Loan and Kisan Credit Card Guide - Tata Mitra")
    pdf.add_page()
    pdf.chapter("1. Agriculture Loan Overview",
        "Agriculture loans are credit facilities provided to farmers, agricultural workers, and agri-businesses "
        "for farming-related expenses. These include crop loans, farm equipment loans, land development loans, "
        "and post-harvest loans. The Government of India provides interest subvention on short-term crop loans "
        "to make agriculture credit affordable."
    )
    pdf.chapter("2. Kisan Credit Card (KCC)",
        "Kisan Credit Card is the most popular agriculture credit product:\n"
        "- Purpose: Revolving credit for crop cultivation, maintenance, post-harvest expenses, and farm asset maintenance\n"
        "- Eligibility: All farmers - individual, joint cultivators, sharecroppers, tenant farmers\n"
        "- Limit: Based on scale of finance for crops, land holding, and repayment capacity\n"
        "- Typical limit: Rs. 1.6 lakh to Rs. 3 lakh for small farmers; higher for larger holdings\n"
        "- Interest rate: 7% per annum (with government interest subvention of 2%)\n"
        "- Effective rate: As low as 4% per annum with timely repayment bonus (3% additional subvention)\n"
        "- Repayment: Aligned with crop harvest cycle; flexible 12-month revolving facility\n"
        "- Collateral: Not required for KCC up to Rs. 1.6 lakh"
    )
    pdf.chapter("3. Crop Loan (Short-term)",
        "Short-term crop loans for seasonal agricultural needs:\n"
        "- Purpose: Seeds, fertilizers, pesticides, labour, irrigation for one crop cycle\n"
        "- Tenor: 6 to 18 months (one crop season)\n"
        "- Interest: 7% per annum with 2% interest subvention from government\n"
        "- Additional subvention: 3% for prompt repayment (effective rate can be 4%)\n"
        "- Amount: Based on crop-specific Scale of Finance approved by District Level Technical Committee\n"
        "- Eligibility: Land ownership records (7/12 extract), no default on existing agricultural loans\n"
        "- Banks: SBI, cooperative banks, regional rural banks, commercial banks all offer crop loans"
    )
    pdf.chapter("4. Farm Equipment and Agricultural Term Loans",
        "Long-term agricultural loans for asset creation:\n"
        "- Tractor Loan: For buying tractors; up to 90% of cost; 5-7 years tenure\n"
        "- Pump Sets and Irrigation: For bore wells, drip irrigation, sprinkler systems\n"
        "- Dairy Loan: For purchasing milch animals (cows, buffaloes); under Dairy Development schemes\n"
        "- Poultry Loan: For setting up poultry units under NABARD schemes\n"
        "- Land Development: For levelling, bunding, terracing land\n"
        "- Interest rate: 9% to 12% for agricultural term loans\n"
        "- NABARD refinancing: Banks get refinance from NABARD for agricultural loans"
    )
    pdf.chapter("5. PM-Kisan and Government Agriculture Schemes",
        "Government support schemes for farmers:\n"
        "- PM-Kisan: Direct income support of Rs. 6,000/year to small and marginal farmers\n"
        "- Pradhan Mantri Fasal Bima Yojana (PMFBY): Crop insurance at subsidised premium\n"
        "- PM Krishi Sinchai Yojana: Irrigation development with government subsidy\n"
        "- MUDRA for Agri-Allied: Loans for activities related to agriculture via MUDRA scheme\n"
        "- Interest subvention scheme: Government pays 2% interest on behalf of farmers on KCC\n"
        "- NABARD: National Bank for Agriculture and Rural Development provides refinancing and policy support"
    )
    pdf.chapter("6. Agriculture Loan Eligibility and Documents",
        "Eligibility for agriculture loans:\n"
        "- Must be engaged in agriculture, horticulture, sericulture, animal husbandry, or fisheries\n"
        "- Own or lease agricultural land\n"
        "- No wilful default on any existing bank loan\n\n"
        "Documents required:\n"
        "- Land ownership records: 7/12 extract, land passbook, or patta\n"
        "- Identity proof: Aadhaar Card and PAN\n"
        "- KCC application form with details of land, crop, and estimated expenses\n"
        "- Photograph of farmer and guarantor (if applicable)"
    )
    out_path = os.path.join(OUTPUT_DIR, "agriculture_kisan_loan_guide.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


# ─────────────────────────────────────────────────────────────────────────────
# PDF 8: Loan Glossary and Terminology
# ─────────────────────────────────────────────────────────────────────────────
def create_glossary_pdf():
    pdf = PDF("Loan Terminology and Glossary - Tata Mitra")
    pdf.add_page()
    pdf.chapter("A to E - Key Loan Terms",
        "APR (Annual Percentage Rate): Total cost of borrowing expressed as yearly rate, including interest "
        "and all fees. More accurate measure of loan cost than interest rate alone.\n\n"
        "Amortisation: The process of paying off a loan through scheduled instalments (EMI). Each payment "
        "reduces the principal while also covering interest.\n\n"
        "Co-applicant: A second person who jointly applies for a loan and is equally liable for repayment. "
        "Improves eligibility and loan amount.\n\n"
        "Collateral: An asset pledged by the borrower to secure the loan. If borrower defaults, lender can "
        "seize and sell collateral. Examples: property, gold, FD.\n\n"
        "Credit Score / CIBIL Score: 3-digit number (300-900) representing creditworthiness. Above 750 "
        "is good; above 800 is excellent.\n\n"
        "DTI (Debt-to-Income Ratio): Total monthly EMI obligations divided by gross monthly income. "
        "Lenders prefer DTI below 40-50%.\n\n"
        "EMI (Equated Monthly Instalment): Fixed monthly payment that includes both principal and interest "
        "components. Calculated using reducing-balance method."
    )
    pdf.chapter("F to L - Key Loan Terms",
        "Fixed Rate: Interest rate that remains constant for the entire loan tenure.\n\n"
        "Floating Rate: Interest rate that changes with market benchmark (repo rate or MCLR).\n\n"
        "Foreclosure: Fully repaying a loan before its scheduled end date. May attract prepayment penalty.\n\n"
        "Guarantor: A third party who guarantees loan repayment if the borrower defaults.\n\n"
        "Hard Inquiry: A credit check made by a lender when you apply for a loan. Temporarily reduces "
        "credit score by 5-10 points. Visible on credit report for 2 years.\n\n"
        "Interest: The cost of borrowing money, expressed as a percentage of principal per annum.\n\n"
        "KYC (Know Your Customer): Mandatory identity and address verification process for financial services.\n\n"
        "LTV (Loan to Value): Ratio of loan amount to the appraised value of the collateral asset.\n\n"
        "Lien: A legal claim on an asset used as collateral for a loan until it is fully repaid."
    )
    pdf.chapter("M to R - Key Loan Terms",
        "MCLR (Marginal Cost of Lending Rate): Benchmark interest rate below which banks cannot lend "
        "to most retail borrowers.\n\n"
        "Moratorium: A temporary suspension of EMI payments granted by a lender during financial hardship. "
        "Interest continues to accrue during moratorium.\n\n"
        "NPA (Non-Performing Asset): A loan where EMI has not been received for 90 or more days. Severely "
        "impacts borrower's credit score.\n\n"
        "NOC (No Objection Certificate): Certificate issued by lender confirming a loan is fully repaid.\n\n"
        "Part-Payment: Paying an extra amount beyond the regular EMI to reduce outstanding principal.\n\n"
        "Pre-approved Loan: A loan offer made by a lender based on existing relationship and credit profile, "
        "without a formal application.\n\n"
        "Principal: The original loan amount borrowed, excluding interest.\n\n"
        "Processing Fee: One-time fee charged by lender for processing loan application. Typically 0.5-3% of loan amount.\n\n"
        "Repo Rate: Rate at which RBI lends money to banks. Changes in repo rate directly affect floating loan rates."
    )
    pdf.chapter("S to Z - Key Loan Terms",
        "Sanction Letter: Official document from lender confirming loan approval with all terms and conditions.\n\n"
        "Secured Loan: Loan backed by collateral (home loan, car loan, gold loan, LAP). Lower interest rates.\n\n"
        "Soft Inquiry: A credit check that does NOT affect credit score. Self-checks and pre-approval checks.\n\n"
        "Subvention: Government subsidy on loan interest, reducing the effective interest rate for borrowers.\n\n"
        "Tenure: The duration of a loan, typically expressed in months or years.\n\n"
        "Top-up Loan: Additional loan given over and above an existing loan (usually home loan) for any purpose.\n\n"
        "Unsecured Loan: Loan given without any collateral, based purely on creditworthiness. Higher interest rates.\n\n"
        "Write-off: When a lender decides a bad loan is unlikely to be recovered and removes it from books. "
        "Does not mean borrower's obligation ends.\n\n"
        "Zero-Cost EMI: Loan scheme where processing fee paid by merchant/seller so customer pays no interest. "
        "Common in consumer durables."
    )
    out_path = os.path.join(OUTPUT_DIR, "loan_terminology_glossary.pdf")
    pdf.output(out_path)
    print(f"Created: {out_path}")


if __name__ == "__main__":
    print("Generating 8 additional comprehensive loan PDFs...")
    create_education_loan_pdf()
    create_gold_loan_pdf()
    create_lap_pdf()
    create_faq_pdf()
    create_rbi_guidelines_pdf()
    create_balance_transfer_pdf()
    create_agriculture_loan_pdf()
    create_glossary_pdf()
    print(f"\nAll 8 PDFs created in: {OUTPUT_DIR}")
