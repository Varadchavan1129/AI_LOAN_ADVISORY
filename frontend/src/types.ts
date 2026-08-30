export type LoanStatus = 'approved' | 'rejected' | 'conditional';

export interface LoanResult {
  status: LoanStatus;
  title: string;
  message: string;
  advice?: string;
}

// ── Phase 2: Chat modes ──────────────────────────────────────────────────────
/** 'select' = welcome screen, 'chat' = NL free-form, 'apply' = structured wizard */
export type ChatMode = 'select' | 'chat' | 'apply';

// ── Phase 2: Query result types ───────────────────────────────────────────────
export type QueryResultType =
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
  support_level: 'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED';
  is_verified:   boolean;
  validation: {
    verdict:            string;
    reasoning:          string;
    unsupported_claims: string[];
  };
}

export interface QueryResult {
  type: QueryResultType;
  message: string;
  data?: EMIData | EligibilityData | MaxLoanData | DTIData | RAGData | Record<string, unknown> | null;
}

// ── Updated Message (supports both result + queryResult) ─────────────────────
export interface Message {
  id: string;
  type: 'user' | 'bot' | 'result' | 'query_result';
  content: string;
  timestamp: Date;
  result?: LoanResult;
  queryResult?: QueryResult;
}

export type Step = 'income' | 'emi' | 'amount' | 'tenure' | 'processing' | 'done';

export interface LoanData {
  income: string;
  emi: string;
  amount: string;
  tenure: string;
}
