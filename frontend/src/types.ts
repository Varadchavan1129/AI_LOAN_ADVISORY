export type LoanStatus = 'likely_eligible' | 'review_needed' | 'unlikely_eligible';

export interface CalculationAssumption {
  label: string;
  description: string;
}

export interface FinancialAssessmentData {
  monthly_income: number;
  existing_emi: number;
  requested_loan_amount: number;
  tenure_months: number;
  employment_type: string;
  age: number;
  credit_score: number;
  loan_purpose: string;
  annual_rate: number;

  estimated_emi: number;
  total_interest: number;
  total_repayment: number;
  total_monthly_obligations: number;
  disposable_income: number;

  current_foir_pct: number;
  projected_foir_pct: number;
  foir_benchmark_pct: number;
  affordability_status: 'comfortable' | 'manageable' | 'tight' | 'high_risk' | string;

  max_permissible_emi: number;
  available_emi_capacity: number;
  estimated_max_loan_eligibility: number;
  eligibility_gap: number;

  decision: LoanStatus | string;
  eligibility_score: number;
  risk_probability: number;
  reason: string | null;
  improvement_factors?: string[];

  disclaimer?: string;

  assumptions: CalculationAssumption[];
}

export interface UserFinancialProfile {
  monthly_income: number;
  existing_emi: number;
  loan_amount: number;
  tenure_months: number;
  employment_type: string;
  age: number;
  credit_score: number;
  loan_purpose: string;
}

export interface LoanResult {
  status: LoanStatus;
  title: string;
  message: string;
  advice?: string;
  assessment?: FinancialAssessmentData;
  profile?: UserFinancialProfile;
}

// ── Phase 1 & 2: Chat modes ──────────────────────────────────────────────────
/** 'select' = welcome screen, 'chat' = NL free-form, 'apply' = structured wizard */
export type ChatMode = 'select' | 'chat' | 'apply';

// ── Query result types ───────────────────────────────────────────────────────
export type QueryResultType =
  | 'assessment'       // Phase 1: Comprehensive Financial Profile Assessment
  | 'emi'
  | 'eligibility'
  | 'max_loan'
  | 'dti'
  | 'general'
  | 'missing_info'
  | 'error'
  | 'policy';          // Phase 6: RAG-backed policy answer

export interface EMIData {
  monthly_emi: number;
  total_interest: number;
  total_repayment: number;
  principal: number;
  annual_rate: number;
  tenure_months: number;
}

export interface EligibilityData {
  decision: string;
  eligibility_score: number;
  risk_probability: number;
  dti_ratio: number;
  reason: string | null;
  assessment?: FinancialAssessmentData;
}

export interface MaxLoanData {
  max_loan: number;
  available_emi: number;
  max_total_emi: number;
  annual_rate: number;
  tenure_months: number;
}

export interface DTIData {
  current_dti: number;
  current_dti_pct: number;
  current_status: string;
  projected_dti: number;
  projected_dti_pct: number;
  projected_status: string;
  new_emi: number;
  existing_emi: number;
  monthly_income: number;
}

// ── Phase 5/6: RAG policy answer ─────────────────────────────────────────────
export interface RAGSource {
  document_name:   string;
  document_id:     string;
  page_number:     number;
  section:         string | null;
  chunk_id:        string;
  relevance_score: number;
}

export interface RAGData {
  answer:        string;
  sources:       RAGSource[];
  support_level: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED' | 'UNVERIFIED' | 'LOW_CONFIDENCE';
  is_verified:   boolean;
  validation?: {
    verdict:            string;
    reasoning:          string;
    unsupported_claims: string[];
    available?:         boolean;
  };
}

export interface QueryResult {
  type: QueryResultType;
  message: string;
  title?: string;
  status?: LoanStatus | string;
  profile?: UserFinancialProfile;
  advice?: string;
  data?: FinancialAssessmentData | EMIData | EligibilityData | MaxLoanData | DTIData | RAGData | Record<string, unknown> | null;
}

// ── Message Definition ───────────────────────────────────────────────────────
export interface Message {
  id: string;
  type: 'user' | 'bot' | 'result' | 'query_result';
  content: string;
  timestamp: Date;
  result?: LoanResult;
  queryResult?: QueryResult;
}

export type Step =
  | 'income'
  | 'employment'
  | 'age'
  | 'cibil'
  | 'emi'
  | 'amount'
  | 'tenure'
  | 'purpose'
  | 'processing'
  | 'done';

export interface StructuredLoanData {
  income: string;
  employment: string;
  age: string;
  cibil: string;
  emi: string;
  amount: string;
  tenure: string;
  purpose: string;
}

export type LoanData = StructuredLoanData;
