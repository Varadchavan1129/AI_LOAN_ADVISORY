import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle, AlertCircle, XCircle, Calculator,
  TrendingUp, ShieldCheck, HelpCircle, ChevronDown,
  ChevronUp, User, Briefcase, Calendar, Sparkles, Lightbulb
} from 'lucide-react';
import type { FinancialAssessmentData, UserFinancialProfile } from '../types';

interface Props {
  data: FinancialAssessmentData;
  title?: string;
  message?: string;
  advice?: string;
  profile?: UserFinancialProfile;
}

const fmt = (n: number) =>
  new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(n);

const fmtDec = (n: number) =>
  new Intl.NumberFormat('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);

export const FinancialAssessmentCard = ({ data, title, message, advice, profile }: Props) => {
  const [showAssumptions, setShowAssumptions] = useState(false);

  const cfgMap = {
    likely_eligible: {
      icon: CheckCircle,
      gradient: 'from-emerald-400 to-green-500',
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
      cardBg: 'bg-emerald-950/20 border-emerald-500/30',
      barColor: 'bg-emerald-400',
      statusText: 'Potentially Eligible',
    },
    review_needed: {
      icon: AlertCircle,
      gradient: 'from-amber-400 to-yellow-500',
      badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
      cardBg: 'bg-amber-950/20 border-amber-500/30',
      barColor: 'bg-amber-400',
      statusText: 'Further Review Needed',
    },
    unlikely_eligible: {
      icon: XCircle,
      gradient: 'from-red-400 to-rose-500',
      badge: 'bg-red-500/20 text-red-300 border-red-500/30',
      cardBg: 'bg-red-950/20 border-red-500/30',
      barColor: 'bg-red-400',
      statusText: 'Unlikely Eligible',
    },
  };

  const decisionKey = (data.decision || 'review_needed').toLowerCase() as keyof typeof cfgMap;
  const cfg = cfgMap[decisionKey] ?? cfgMap.review_needed;
  const Icon = cfg.icon;

  const decisionDisplayMap: Record<string, string> = {
    likely_eligible: 'Potentially Eligible',
    review_needed: 'Review Needed',
    unlikely_eligible: 'Unlikely Eligible',
  };

  const foirStatusColors: Record<string, { badge: string; text: string }> = {
    comfortable: { badge: 'bg-emerald-500/20 text-emerald-300', text: 'Comfortable (≤35%)' },
    manageable: { badge: 'bg-teal-500/20 text-teal-300', text: 'Manageable (36-45%)' },
    tight: { badge: 'bg-amber-500/20 text-amber-300', text: 'Tight Margin (46-50%)' },
    high_risk: { badge: 'bg-red-500/20 text-red-300', text: 'Overburdened (>50%)' },
  };

  const foirTier = foirStatusColors[data.affordability_status] ?? foirStatusColors.manageable;

  return (
    <div className={`border rounded-3xl p-5 md:p-6 space-y-5 ${cfg.cardBg} backdrop-blur-xl shadow-2xl transition-all`}>
      {/* 1. Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${cfg.gradient} flex items-center justify-center shadow-lg flex-shrink-0`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${cfg.badge}`}>
                {decisionDisplayMap[data.decision] || data.decision}
              </span>
              <span className="text-xs text-white/50">Estimated Eligibility</span>
            </div>
            <h3 className="text-lg font-bold text-white mt-0.5">
              {title || `Financial Assessment — ${cfg.statusText}`}
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:self-center">
          <div className="bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-center min-w-[70px]" title="Internal composite score based on FOIR, credit score, income adequacy, and ML risk model. Not a lender score.">
            <p className="text-[10px] uppercase text-white/40 font-semibold">Est. Score</p>
            <p className="text-sm font-bold text-white">{data.eligibility_score}<span className="text-[10px] text-white/40">/100</span></p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-xl px-3 py-1.5 text-center min-w-[70px]" title="ML-estimated default risk probability. For indicative purposes only.">
            <p className="text-[10px] uppercase text-white/40 font-semibold">Risk Est.</p>
            <p className="text-sm font-bold text-white">{(data.risk_probability * 100).toFixed(0)}%</p>
          </div>
        </div>
      </div>

      {/* 2. AI Explanation Narrative */}
      {message && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-3.5 flex items-start gap-3">
          <Sparkles className="w-4 h-4 text-indigo-300 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-white/90 leading-relaxed">{message}</p>
        </div>
      )}

      {/* 3. Core Deterministic Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Estimated EMI */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-3.5 relative overflow-hidden">
          <div className="flex items-center gap-1.5 text-indigo-300 text-xs font-medium mb-1">
            <Calculator className="w-3.5 h-3.5" />
            <span>Estimated EMI</span>
          </div>
          <p className="text-xl font-extrabold text-white">₹{fmt(data.estimated_emi)}</p>
          <p className="text-[11px] text-white/40 mt-0.5">@ {data.annual_rate}% p.a. · {data.tenure_months}m</p>
        </div>

        {/* Disposable Income */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-3.5">
          <div className="flex items-center gap-1.5 text-emerald-300 text-xs font-medium mb-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Disposable Income</span>
          </div>
          <p className={`text-xl font-extrabold ${data.disposable_income < 0 ? 'text-red-400' : 'text-emerald-400'}`}>
            ₹{fmt(data.disposable_income)}
          </p>
          <p className="text-[11px] text-white/40 mt-0.5">after all monthly EMIs</p>
        </div>

        {/* Total Obligations */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-3.5">
          <div className="flex items-center gap-1.5 text-amber-300 text-xs font-medium mb-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Total Obligations</span>
          </div>
          <p className="text-xl font-extrabold text-white">₹{fmt(data.total_monthly_obligations)}</p>
          <p className="text-[11px] text-white/40 mt-0.5">Existing ₹{fmt(data.existing_emi)} + New</p>
        </div>

        {/* Max Loan Eligibility */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-3.5">
          <div className="flex items-center gap-1.5 text-purple-300 text-xs font-medium mb-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Max Eligibility</span>
          </div>
          <p className="text-xl font-extrabold text-white">₹{fmt(data.estimated_max_loan_eligibility)}</p>
          <p className="text-[11px] text-white/40 mt-0.5">
            {data.eligibility_gap >= 0 ? `+₹${fmt(data.eligibility_gap)} headroom` : `-₹${fmt(Math.abs(data.eligibility_gap))} deficit`}
          </p>
        </div>
      </div>

      {/* 4. FOIR / Debt-to-Income Affordability Gauge */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-bold text-white/90">FOIR / Debt-to-Income Ratio</span>
            <span className="text-[11px] text-white/40 ml-2">Benchmark Cap: {data.foir_benchmark_pct}%</span>
          </div>
          <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${foirTier.badge}`}>
            {data.projected_foir_pct.toFixed(1)}% ({foirTier.text})
          </span>
        </div>

        {/* Progress meter */}
        <div className="relative w-full bg-white/10 rounded-full h-3 overflow-hidden">
          {/* 50% Benchmark indicator line */}
          <div className="absolute top-0 bottom-0 left-1/2 w-0.5 bg-white/40 z-10" title="50% Benchmark Cap" />
          
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(data.projected_foir_pct, 100)}%` }}
            transition={{ duration: 0.9, ease: 'easeOut' }}
            className={`h-full rounded-full ${data.projected_foir_pct > 50 ? 'bg-gradient-to-r from-amber-400 to-rose-500' : 'bg-gradient-to-r from-emerald-400 to-teal-400'}`}
          />
        </div>

        <div className="flex justify-between text-[11px] text-white/40">
          <span>Current: {data.current_foir_pct.toFixed(1)}%</span>
          <span>50% Threshold</span>
          <span>Projected: {data.projected_foir_pct.toFixed(1)}%</span>
        </div>
      </div>

      {/* 5. User Financial Profile Snapshot */}
      <div className="flex flex-wrap gap-2 pt-1">
        <span className="inline-flex items-center gap-1 text-xs bg-white/5 border border-white/10 rounded-xl px-2.5 py-1 text-white/70">
          <User className="w-3 h-3 text-indigo-300" /> Income: ₹{fmt(data.monthly_income)}/mo
        </span>
        <span className="inline-flex items-center gap-1 text-xs bg-white/5 border border-white/10 rounded-xl px-2.5 py-1 text-white/70">
          <Briefcase className="w-3 h-3 text-indigo-300" /> {data.employment_type}
        </span>
        <span className="inline-flex items-center gap-1 text-xs bg-white/5 border border-white/10 rounded-xl px-2.5 py-1 text-white/70">
          <Calendar className="w-3 h-3 text-indigo-300" /> Age {data.age}
        </span>
        <span className="inline-flex items-center gap-1 text-xs bg-white/5 border border-white/10 rounded-xl px-2.5 py-1 text-white/70">
          <ShieldCheck className="w-3 h-3 text-indigo-300" /> CIBIL {data.credit_score}
        </span>
        <span className="inline-flex items-center gap-1 text-xs bg-white/5 border border-white/10 rounded-xl px-2.5 py-1 text-white/70">
          Purpose: {data.loan_purpose}
        </span>
      </div>

      {/* 6. Personalized Credit Advisory (if conditional/rejected) */}
      {advice && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-amber-300 text-xs font-bold">
            <Lightbulb className="w-4 h-4" />
            <span>AI Credit Improvement Recommendations</span>
          </div>
          <p className="text-xs text-white/85 leading-relaxed">{advice}</p>
        </div>
      )}

      {/* 7. Transparent Calculation Assumptions Accordion */}
      {data.assumptions && data.assumptions.length > 0 && (
        <div className="pt-2 border-t border-white/10">
          <button
            onClick={() => setShowAssumptions(!showAssumptions)}
            className="flex items-center justify-between w-full text-xs text-white/50 hover:text-white/80 transition-colors py-1"
          >
            <span className="flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5" />
              Calculation Assumptions ({data.assumptions.length})
            </span>
            {showAssumptions ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          <AnimatePresence>
            {showAssumptions && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5 pt-2"
              >
                {data.assumptions.map((asm, idx) => (
                  <div key={idx} className="text-[11px] bg-white/5 border border-white/10 rounded-xl p-2.5 text-white/70">
                    <span className="font-semibold text-white/90">{asm.label}: </span>
                    {asm.description}
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* 8. Lender Disclaimer */}
      <div className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 mt-1">
        <p className="text-[11px] text-white/45 leading-relaxed text-center">
          {data.disclaimer || 'Based on the information provided and the calculation assumptions. Final eligibility, pricing and approval are determined by the lender.'}
        </p>
      </div>
    </div>
  );
};
