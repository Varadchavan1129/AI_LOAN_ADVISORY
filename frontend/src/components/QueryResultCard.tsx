import { useState } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import {
  Calculator, CheckCircle, XCircle, AlertCircle,
  TrendingUp, Info, HelpCircle, IndianRupee,
  FileText, ShieldCheck, ShieldAlert, BookOpen,
  ChevronDown, ChevronUp, GitMerge, ArrowDown,
  Zap, Database, MessageSquare, BadgeCheck,
} from 'lucide-react';
import type { QueryResult, EMIData, EligibilityData, MaxLoanData, DTIData, RAGData, FinancialAssessmentData } from '../types';
import { FinancialAssessmentCard } from './FinancialAssessmentCard';

interface Props {
  result: QueryResult;
}

// ─── Helpers ────────────────────────────────────────────────────────────────
const fmt = (n: number) =>
  new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);

const fmtDec = (n: number) =>
  new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);

function StatusBadge({ label, color }: { label: string; color: string }) {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${color}`}>
      {label}
    </span>
  );
}

function DTIBar({ pct, status }: { pct: number; status: string }) {
  const colorMap: Record<string, string> = {
    excellent: 'bg-emerald-500',
    good: 'bg-green-400',
    acceptable: 'bg-yellow-400',
    high: 'bg-red-500',
  };
  const barColor = colorMap[status] ?? 'bg-indigo-400';
  return (
    <div className="w-full bg-white/10 rounded-full h-2 mt-1">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(pct, 100)}%` }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className={`${barColor} h-2 rounded-full`}
      />
    </div>
  );
}

// ─── EMI Card ────────────────────────────────────────────────────────────────
function EMICard({ data }: { data: EMIData; message: string }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
          <Calculator className="w-4 h-4 text-indigo-300" />
        </div>
        <span className="text-sm font-semibold text-white/80">EMI Breakdown</span>
      </div>

      <div className="bg-indigo-500/15 border border-indigo-500/30 rounded-2xl p-4 text-center">
        <p className="text-xs text-white/50 mb-1">Monthly EMI</p>
        <p className="text-3xl font-bold text-white flex items-center justify-center gap-1">
          <IndianRupee className="w-6 h-6" />
          {fmtDec(data.monthly_emi)}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="bg-white/5 rounded-xl p-3 text-center">
          <p className="text-xs text-white/40 mb-1">Total Interest</p>
          <p className="text-sm font-semibold text-yellow-300">₹{fmt(data.total_interest)}</p>
        </div>
        <div className="bg-white/5 rounded-xl p-3 text-center">
          <p className="text-xs text-white/40 mb-1">Total Repayment</p>
          <p className="text-sm font-semibold text-white">₹{fmt(data.total_repayment)}</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-white/40">
        <span>Principal: ₹{fmt(data.principal)}</span>
        <span>·</span>
        <span>Rate: {data.annual_rate}% p.a.</span>
        <span>·</span>
        <span>Tenure: {data.tenure_months} months</span>
      </div>
    </div>
  );
}

// ─── Eligibility Card ────────────────────────────────────────────────────────
function EligibilityCard({ data }: { data: EligibilityData; message: string }) {
  const cfgMap = {
    likely_eligible: {
      icon: CheckCircle, gradient: 'from-emerald-400 to-green-500',
      badge: 'bg-emerald-500/20 text-emerald-300', bg: 'border-emerald-500/30 bg-emerald-500/10',
    },
    review_needed: {
      icon: AlertCircle, gradient: 'from-yellow-400 to-amber-500',
      badge: 'bg-yellow-500/20 text-yellow-300', bg: 'border-yellow-500/30 bg-yellow-500/10',
    },
    unlikely_eligible: {
      icon: XCircle, gradient: 'from-red-400 to-pink-500',
      badge: 'bg-red-500/20 text-red-300', bg: 'border-red-500/30 bg-red-500/10',
    },
  };

  const decisionDisplayMap: Record<string, string> = {
    likely_eligible: 'Potentially Eligible',
    review_needed: 'Review Needed',
    unlikely_eligible: 'Unlikely Eligible',
  };

  const cfg = cfgMap[data.decision as keyof typeof cfgMap] ?? cfgMap.review_needed;
  const Icon = cfg.icon;

  return (
    <div className={`border rounded-2xl p-4 space-y-3 ${cfg.bg}`}>
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${cfg.gradient} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-xs text-white/50">Estimated Eligibility</p>
          <StatusBadge label={decisionDisplayMap[data.decision] || data.decision} color={cfg.badge} />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="bg-white/5 rounded-xl p-2 text-center" title="Internal composite estimate — not a lender score">
          <p className="text-xs text-white/40">Est. Score</p>
          <p className="text-base font-bold text-white">{data.eligibility_score}<span className="text-xs text-white/40">/100</span></p>
        </div>
        <div className="bg-white/5 rounded-xl p-2 text-center">
          <p className="text-xs text-white/40">DTI</p>
          <p className="text-base font-bold text-white">{(data.dti_ratio * 100).toFixed(0)}<span className="text-xs text-white/40">%</span></p>
        </div>
        <div className="bg-white/5 rounded-xl p-2 text-center" title="ML-estimated risk — for indicative purposes only">
          <p className="text-xs text-white/40">Risk Est.</p>
          <p className="text-base font-bold text-white">{(data.risk_probability * 100).toFixed(0)}<span className="text-xs text-white/40">%</span></p>
        </div>
      </div>

      {data.reason && (
        <p className="text-xs text-white/50 flex items-center gap-1">
          <Info className="w-3 h-3 flex-shrink-0" />
          {data.reason}
        </p>
      )}

      <p className="text-[10px] text-white/35 text-center pt-1 border-t border-white/10">
        Based on the information provided and the calculation assumptions. Final eligibility, pricing and approval are determined by the lender.
      </p>
    </div>
  );
}

// ─── Max Loan Card ───────────────────────────────────────────────────────────
function MaxLoanCard({ data }: { data: MaxLoanData }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center">
          <TrendingUp className="w-4 h-4 text-purple-300" />
        </div>
        <span className="text-sm font-semibold text-white/80">Max Loan Capacity</span>
      </div>

      <div className="bg-purple-500/15 border border-purple-500/30 rounded-2xl p-4 text-center">
        <p className="text-xs text-white/50 mb-1">Maximum Loan Amount</p>
        <p className="text-3xl font-bold text-white">₹{fmt(data.max_loan)}</p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="bg-white/5 rounded-xl p-3 text-center">
          <p className="text-xs text-white/40">Available EMI</p>
          <p className="text-sm font-semibold text-purple-300">₹{fmt(data.available_emi)}/mo</p>
        </div>
        <div className="bg-white/5 rounded-xl p-3 text-center">
          <p className="text-xs text-white/40">Max EMI (40% rule)</p>
          <p className="text-sm font-semibold text-white">₹{fmt(data.max_total_emi)}/mo</p>
        </div>
      </div>

      <p className="text-xs text-white/40">@ {data.annual_rate}% p.a. · {data.tenure_months} months</p>
    </div>
  );
}

// ─── DTI Card ────────────────────────────────────────────────────────────────
function DTICard({ data }: { data: DTIData }) {
  const statusColor: Record<string, string> = {
    excellent: 'text-emerald-300',
    good: 'text-green-300',
    acceptable: 'text-yellow-300',
    high: 'text-red-300',
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center">
          <TrendingUp className="w-4 h-4 text-cyan-300" />
        </div>
        <span className="text-sm font-semibold text-white/80">Debt-to-Income Ratio</span>
      </div>

      <div className="space-y-2">
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-white/50">Current DTI</span>
            <span className={`font-semibold ${statusColor[data.current_status] ?? 'text-white'}`}>
              {data.current_dti_pct}% — {data.current_status}
            </span>
          </div>
          <DTIBar pct={data.current_dti_pct} status={data.current_status} />
        </div>

        {data.new_emi > 0 && (
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-white/50">With new loan</span>
              <span className={`font-semibold ${statusColor[data.projected_status] ?? 'text-white'}`}>
                {data.projected_dti_pct}% — {data.projected_status}
              </span>
            </div>
            <DTIBar pct={data.projected_dti_pct} status={data.projected_status} />
          </div>
        )}
      </div>

      <p className="text-xs text-white/40">Ideal DTI: below 40% | Acceptable: below 50%</p>
    </div>
  );
}

// ─── Missing Info Card ───────────────────────────────────────────────────────
function MissingInfoCard({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3 bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4">
      <HelpCircle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
      <p className="text-sm text-white/80">{message}</p>
    </div>
  );
}

// ─── General / Fallback Card ─────────────────────────────────────────────────
function GeneralCard({ message }: { message: string }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
        <HelpCircle className="w-4 h-4 text-indigo-300" />
      </div>
      <p className="text-sm text-white/90 leading-relaxed">{message}</p>
    </div>
  );
}

// ─── Markdown answer renderer (matches dark design language) ────────────────
function MarkdownAnswer({ text }: { text: string }) {
  return (
    <ReactMarkdown
      components={{
        p:      ({ children }) => <p className="text-sm text-white/90 leading-relaxed mb-2.5 last:mb-0">{children}</p>,
        h1:     ({ children }) => <h1 className="text-sm font-bold text-white mb-2 mt-2.5 first:mt-0">{children}</h1>,
        h2:     ({ children }) => <h2 className="text-sm font-bold text-white mb-2 mt-2.5 first:mt-0">{children}</h2>,
        h3:     ({ children }) => <h3 className="text-xs font-semibold text-teal-300 mb-1 mt-2 first:mt-0">{children}</h3>,
        ul:     ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2.5 text-sm text-white/80">{children}</ul>,
        ol:     ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-2.5 text-sm text-white/80">{children}</ol>,
        li:     ({ children }) => <li className="leading-relaxed">{children}</li>,
        strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
        em:     ({ children }) => <em className="italic text-white/70">{children}</em>,
        code:   ({ children }) => <code className="bg-white/10 text-teal-300 rounded px-1 py-0.5 text-xs font-mono">{children}</code>,
        hr:     () => <hr className="border-white/10 my-2" />,
        table:  ({ children }) => (
          <div className="overflow-x-auto mb-2.5">
            <table className="w-full text-xs border-collapse">{children}</table>
          </div>
        ),
        thead:  ({ children }) => <thead className="bg-white/5">{children}</thead>,
        tr:     ({ children }) => <tr className="border-t border-white/10">{children}</tr>,
        th:     ({ children }) => <th className="text-left px-3 py-1.5 text-white/60 font-semibold">{children}</th>,
        td:     ({ children }) => <td className="px-3 py-1.5 text-white/70">{children}</td>,
      }}
    >
      {text}
    </ReactMarkdown>
  );
}

// ─── Policy / RAG Card ───────────────────────────────────────────────────────
function PolicyCard({ data }: { data: RAGData }) {
  const [showPipeline, setShowPipeline] = useState(false);

  const isNotInEvidence =
    data.support_level === 'UNSUPPORTED' ||
    (!data.sources || data.sources.length === 0);

  const verdictCfg = {
    SUPPORTED: {
      Icon: ShieldCheck,
      badge: 'Verified',
      label: 'Verified — Fully supported by document evidence',
      cls: 'bg-emerald-900/50 border-emerald-700/40 text-emerald-300',
    },
    PARTIALLY_SUPPORTED: {
      Icon: ShieldAlert,
      badge: 'Partially Verified',
      label: 'Partially Verified — Some claims confirmed by evidence',
      cls: 'bg-amber-900/50 border-amber-700/40 text-amber-300',
    },
    UNSUPPORTED: {
      Icon: AlertCircle,
      badge: 'Not In Evidence',
      label: 'Not in Evidence — Answer not found in uploaded documents',
      cls: 'bg-red-900/50 border-red-700/40 text-red-300',
    },
    UNVERIFIED: {
      Icon: ShieldAlert,
      badge: 'Not Verified',
      label: 'Not Verified — The validation agent was unavailable, so this answer has NOT been fact-checked',
      cls: 'bg-slate-800/70 border-slate-600/50 text-slate-300',
    },
    LOW_CONFIDENCE: {
      Icon: ShieldAlert,
      badge: 'Low Confidence',
      label: 'Low Confidence — Retrieved evidence was only weakly related to the question',
      cls: 'bg-slate-800/70 border-slate-600/50 text-slate-300',
    },
  }[data.support_level] ?? {
    Icon: HelpCircle,
    badge: 'Unknown',
    label: data.support_level,
    cls: 'bg-gray-700 border-gray-600 text-gray-400',
  };

  const { Icon: VIcon, badge: vBadge, label: vLabel, cls: vCls } = verdictCfg;

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center flex-shrink-0">
          <BookOpen className="w-4 h-4 text-teal-300" />
        </div>
        <span className="text-sm font-semibold text-white/80">Policy Answer</span>
        <span
          data-testid="policy-verdict-badge"
          className={`ml-auto inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${vCls}`}
        >
          <VIcon className="w-3 h-3" />
          {vBadge}
        </span>
      </div>

      {/* NOT_IN_EVIDENCE state */}
      {isNotInEvidence ? (
        <div className="rounded-2xl p-4 border bg-red-950/40 border-red-800/40">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span className="text-xs font-bold text-red-400 uppercase tracking-widest">NOT_IN_EVIDENCE</span>
          </div>
          <p className="text-sm text-white/80 leading-relaxed">
            Information not found in the uploaded policy documents.
          </p>
          <p className="text-xs text-red-400/70 mt-2">
            The system did not fabricate an answer. The retrieved chunks did not contain sufficient evidence.
          </p>
        </div>
      ) : (
        <>
          {/* Answer — Markdown rendered */}
          <div className={`rounded-2xl p-4 border ${
            data.support_level === 'SUPPORTED'
              ? 'bg-teal-950/40 border-teal-800/40'
              : 'bg-amber-950/30 border-amber-800/30'
          }`}>
            <p className="text-[10px] font-semibold text-white/40 uppercase tracking-wider mb-2">Answer</p>
            <div data-testid="policy-answer-text">
              <MarkdownAnswer text={data.answer} />
            </div>
          </div>

          {/* Validation */}
          {data.validation && (
            <div data-testid="policy-validation-block" className={`rounded-xl p-3 border text-xs ${vCls}`}>
              <div className="flex items-start gap-1.5 mb-1 flex-wrap">
                <GitMerge className="w-3 h-3 mt-0.5" />
                <span className="font-bold uppercase tracking-wide">Validation Agent: </span>
                <span className="opacity-80">{vLabel}</span>
              </div>
              {data.validation.reasoning && (
                <p className="opacity-70 leading-relaxed">{data.validation.reasoning}</p>
              )}
              {data.validation.unsupported_claims && data.validation.unsupported_claims.length > 0 && (
                <ul className="mt-1.5 space-y-0.5 list-disc list-inside opacity-70">
                  {data.validation.unsupported_claims.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Sources */}
          {data.sources && data.sources.length > 0 && (
            <div className="space-y-1.5">
              <p className="text-[10px] text-white/40 uppercase tracking-wider font-semibold flex items-center gap-1.5">
                <FileText className="w-3 h-3" /> Source / Evidence
              </p>
              {data.sources.map((src, i) => {
                const barW = Math.min(src.relevance_score * 100, 100);
                return (
                  <div key={i} className="bg-white/5 border border-white/10 rounded-xl px-3 py-2.5 space-y-1.5">
                    <div className="flex items-start gap-2">
                      <div className="w-5 h-5 rounded-full bg-teal-900/60 flex items-center justify-center flex-shrink-0">
                        <span className="text-[9px] font-bold text-teal-300">{i + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-white/80 truncate">{src.document_name}</p>
                        <p className="text-[10px] text-white/40 mt-0.5">
                          Page {src.page_number}{src.section ? ` · ${src.section}` : ''}
                        </p>
                      </div>
                      <span className="text-xs font-bold text-teal-300 flex-shrink-0">
                        {(src.relevance_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${barW}%` }}
                        transition={{ duration: 0.6, ease: 'easeOut' }}
                        className={`h-full rounded-full ${
                          barW >= 80 ? 'bg-emerald-500' : barW >= 60 ? 'bg-teal-500' : 'bg-amber-500'
                        }`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Expandable RAG pipeline */}
          <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowPipeline(p => !p)}
              className="w-full flex items-center justify-between px-3 py-2.5 text-left hover:bg-white/5 transition-colors"
            >
              <div className="flex items-center gap-1.5 text-[11px] text-white/40 hover:text-white/60 transition-colors">
                <Info className="w-3 h-3" />
                How this answer was generated (RAG Pipeline)
              </div>
              {showPipeline
                ? <ChevronUp className="w-3.5 h-3.5 text-white/30" />
                : <ChevronDown className="w-3.5 h-3.5 text-white/30" />
              }
            </button>
            {showPipeline && (
              <div className="px-3 pb-3 space-y-1">
                {[
                  { n: '1', icon: MessageSquare, step: 'User Question', desc: `"${(data as any).question ?? 'Policy question'}"`, col: 'text-indigo-300' },
                  { n: '2', icon: Zap, step: 'Question Embedding', desc: 'Gemini embedding-001 → 3072-dim vector', col: 'text-purple-300' },
                  { n: '3', icon: Database, step: 'FAISS Similarity Search', desc: 'Cosine similarity over indexed document chunks', col: 'text-blue-300' },
                  { n: '4', icon: FileText, step: 'Retrieved Evidence', desc: `${data.sources?.length ?? 0} chunk(s) from uploaded documents`, col: 'text-teal-300' },
                  { n: '5', icon: BookOpen, step: 'Gemini Answer Generation', desc: 'Grounded generation using ONLY retrieved evidence', col: 'text-cyan-300' },
                  { n: '6', icon: GitMerge, step: 'Validation Agent', desc: data.validation?.available === false ? 'Unavailable — answer NOT fact-checked' : `Fact-checked → ${data.support_level}`, col: 'text-amber-300' },
                  { n: '7', icon: BadgeCheck, step: 'Final Answer', desc: data.is_verified ? 'Verified & delivered' : 'Delivered without full verification', col: 'text-emerald-300' },
                ].map(({ n, icon: Icon, step, desc, col }, idx, arr) => (
                  <div key={n}>
                    <div className={`flex items-start gap-2 rounded-lg px-2 py-1.5 ${col}`}>
                      <span className="text-[9px] font-bold opacity-50 flex-shrink-0 w-3 mt-0.5">{n}</span>
                      <Icon className="w-3 h-3 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="text-[11px] font-semibold">{step}</span>
                        <span className="text-[10px] opacity-50"> — {desc}</span>
                      </div>
                    </div>
                    {idx < arr.length - 1 && (
                      <div className="flex justify-center py-0.5">
                        <ArrowDown className="w-2.5 h-2.5 text-white/15" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

// ─── Root Export ─────────────────────────────────────────────────────────────
export const QueryResultCard = ({ result }: Props) => {
  if (result.type === 'assessment' && result.data) {
    return (
      <FinancialAssessmentCard
        data={result.data as FinancialAssessmentData}
        title={result.title}
        message={result.message}
        advice={result.advice}
        profile={result.profile}
      />
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="w-full bg-white/10 backdrop-blur-lg border border-white/15 rounded-3xl p-4"
    >
      {result.type === 'emi' && result.data && (
        <EMICard data={result.data as EMIData} message={result.message} />
      )}
      {result.type === 'eligibility' && result.data && (
        <EligibilityCard data={result.data as EligibilityData} message={result.message} />
      )}
      {result.type === 'max_loan' && result.data && (
        <MaxLoanCard data={result.data as MaxLoanData} />
      )}
      {result.type === 'dti' && result.data && (
        <DTICard data={result.data as DTIData} />
      )}
      {result.type === 'missing_info' && (
        <MissingInfoCard message={result.message} />
      )}
      {result.type === 'policy' && result.data && (
        <PolicyCard data={result.data as RAGData} />
      )}
      {(result.type === 'general' || result.type === 'error') && (
        <GeneralCard message={result.message} />
      )}
    </motion.div>
  );
};
