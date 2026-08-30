import { motion } from 'framer-motion';
import {
  Calculator, CheckCircle, XCircle, AlertCircle,
  TrendingUp, Info, HelpCircle, IndianRupee,
  FileText, ShieldCheck, ShieldAlert, BookOpen,
} from 'lucide-react';
import type { QueryResult, EMIData, EligibilityData, MaxLoanData, DTIData, RAGData, RAGSource } from '../types';

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
    approved: {
      icon: CheckCircle, gradient: 'from-emerald-400 to-green-500',
      badge: 'bg-emerald-500/20 text-emerald-300', bg: 'border-emerald-500/30 bg-emerald-500/10',
    },
    conditional: {
      icon: AlertCircle, gradient: 'from-yellow-400 to-amber-500',
      badge: 'bg-yellow-500/20 text-yellow-300', bg: 'border-yellow-500/30 bg-yellow-500/10',
    },
    rejected: {
      icon: XCircle, gradient: 'from-red-400 to-pink-500',
      badge: 'bg-red-500/20 text-red-300', bg: 'border-red-500/30 bg-red-500/10',
    },
  };
  const cfg = cfgMap[data.decision as keyof typeof cfgMap] ?? cfgMap.conditional;
  const Icon = cfg.icon;

  return (
    <div className={`border rounded-2xl p-4 space-y-3 ${cfg.bg}`}>
      <div className="flex items-center gap-3">
        <div className={`w-9 h-9 rounded-full bg-gradient-to-br ${cfg.gradient} flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div>
          <p className="text-xs text-white/50">Eligibility Result</p>
          <StatusBadge label={data.decision} color={cfg.badge} />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2">
        <div className="bg-white/5 rounded-xl p-2 text-center">
          <p className="text-xs text-white/40">Score</p>
          <p className="text-base font-bold text-white">{data.eligibility_score}<span className="text-xs text-white/40">/100</span></p>
        </div>
        <div className="bg-white/5 rounded-xl p-2 text-center">
          <p className="text-xs text-white/40">DTI</p>
          <p className="text-base font-bold text-white">{(data.dti_ratio * 100).toFixed(0)}<span className="text-xs text-white/40">%</span></p>
        </div>
        <div className="bg-white/5 rounded-xl p-2 text-center">
          <p className="text-xs text-white/40">Risk</p>
          <p className="text-base font-bold text-white">{(data.risk_probability * 100).toFixed(0)}<span className="text-xs text-white/40">%</span></p>
        </div>
      </div>

      {data.reason && (
        <p className="text-xs text-white/50 flex items-center gap-1">
          <Info className="w-3 h-3 flex-shrink-0" />
          {data.reason}
        </p>
      )}
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

// ─── Policy / RAG Card ───────────────────────────────────────────────────────
function PolicyCard({ data }: { data: RAGData }) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center">
          <BookOpen className="w-4 h-4 text-teal-300" />
        </div>
        <span className="text-sm font-semibold text-white/80">Policy Answer</span>
      </div>

      {/* Answer text */}
      <div className="rounded-2xl p-4 border bg-teal-950/40 border-teal-800/40">
        <p className="text-sm text-white/90 leading-relaxed whitespace-pre-wrap">{data.answer}</p>
      </div>
    </div>
  );
}

// ─── Root Export ─────────────────────────────────────────────────────────────
export const QueryResultCard = ({ result }: Props) => {
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
