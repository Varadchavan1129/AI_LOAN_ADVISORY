import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { API } from '../api';
import {
  Search, CheckCircle, AlertCircle, HelpCircle,
  FileText, Loader, BookOpen, ChevronDown, ChevronUp,
  ShieldCheck, ShieldAlert, ArrowDown, Zap, Database,
  MessageSquare, GitMerge, BadgeCheck,
} from 'lucide-react';

// ── Types ─────────────────────────────────────────────────────────────────────
interface Source {
  document_name:   string;
  document_id:     string;
  page_number:     number;
  section:         string | null;
  chunk_id:        string;
  relevance_score: number;
}

interface EvidencePreview {
  document_name: string;
  page_number:   number;
  section:       string | null;
  score:         number;
  text_preview:  string;
}

interface ValidationResult {
  verdict:            string;
  reasoning:          string;
  unsupported_claims: string[];
}

interface RAGResponse {
  question:         string;
  answer:           string;
  is_verified:      boolean;
  support_level:    'SUPPORTED' | 'PARTIALLY_SUPPORTED' | 'UNSUPPORTED';
  sources:          Source[];
  validation:       ValidationResult;
  retrieved_chunks: number;
  top_evidence:     EvidencePreview[];
}

// ── Support badge ─────────────────────────────────────────────────────────────
function SupportBadge({ level }: { level: string }) {
  const cfg = {
    SUPPORTED: {
      label: 'Verified',
      Icon: ShieldCheck,
      cls: 'bg-emerald-900/70 border-emerald-600/60 text-emerald-300',
    },
    PARTIALLY_SUPPORTED: {
      label: 'Partially Verified',
      Icon: ShieldAlert,
      cls: 'bg-amber-900/70 border-amber-600/60 text-amber-300',
    },
    UNSUPPORTED: {
      label: 'Not In Evidence',
      Icon: AlertCircle,
      cls: 'bg-red-900/70 border-red-600/60 text-red-300',
    },
  }[level] ?? { label: level, Icon: HelpCircle, cls: 'bg-gray-700 border-gray-600 text-gray-400' };

  const { label, Icon, cls } = cfg;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${cls}`}>
      <Icon className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}

// ── Markdown Answer renderer ──────────────────────────────────────────────────
// Styled to match the dark glassmorphism design language.
function MarkdownAnswer({ text }: { text: string }) {
  return (
    <ReactMarkdown
      components={{
        p:      ({ children }) => <p className="text-sm text-gray-200 leading-relaxed mb-3 last:mb-0">{children}</p>,
        h1:     ({ children }) => <h1 className="text-base font-bold text-white mb-2 mt-3 first:mt-0">{children}</h1>,
        h2:     ({ children }) => <h2 className="text-sm font-bold text-white mb-2 mt-3 first:mt-0">{children}</h2>,
        h3:     ({ children }) => <h3 className="text-sm font-semibold text-indigo-300 mb-1 mt-2 first:mt-0">{children}</h3>,
        ul:     ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3 text-sm text-gray-300">{children}</ul>,
        ol:     ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-3 text-sm text-gray-300">{children}</ol>,
        li:     ({ children }) => <li className="leading-relaxed">{children}</li>,
        strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
        em:     ({ children }) => <em className="italic text-gray-300">{children}</em>,
        code:   ({ children }) => <code className="bg-gray-700/60 text-indigo-300 rounded px-1.5 py-0.5 text-xs font-mono">{children}</code>,
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-indigo-500/50 pl-3 my-2 text-gray-400 italic text-sm">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto mb-3">
            <table className="w-full text-xs border-collapse">{children}</table>
          </div>
        ),
        thead: ({ children }) => <thead className="bg-gray-700/50">{children}</thead>,
        tbody: ({ children }) => <tbody>{children}</tbody>,
        tr:    ({ children }) => <tr className="border-t border-gray-700/40">{children}</tr>,
        th:    ({ children }) => <th className="text-left px-3 py-1.5 text-gray-300 font-semibold">{children}</th>,
        td:    ({ children }) => <td className="px-3 py-1.5 text-gray-400">{children}</td>,
        hr:    () => <hr className="border-gray-700/50 my-3" />,
      }}
    >
      {text}
    </ReactMarkdown>
  );
}

// ── Pipeline animated step (loading state) ────────────────────────────────────
function PipelineStep({ label, active, done }: { label: string; active: boolean; done: boolean }) {
  return (
    <div className={`flex items-center gap-2 text-xs font-medium transition-colors ${
      done ? 'text-emerald-400' : active ? 'text-indigo-300' : 'text-gray-600'
    }`}>
      {done
        ? <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
        : active
          ? <Loader className="w-3.5 h-3.5 flex-shrink-0 animate-spin" />
          : <div className="w-3.5 h-3.5 flex-shrink-0 rounded-full border border-current opacity-40" />
      }
      {label}
    </div>
  );
}

// ── Visual RAG Pipeline (post-result, expandable) ─────────────────────────────
function RAGPipelineVisual({
  data,
  showEvidence,
  onToggleEvidence,
}: {
  data: RAGResponse;
  showEvidence: boolean;
  onToggleEvidence: () => void;
}) {
  const [open, setOpen] = useState(false);

  const steps = [
    {
      icon: MessageSquare,
      label: 'User Question',
      color: 'text-indigo-300 bg-indigo-900/40 border-indigo-700/40',
      detail: `"${data.question}"`,
    },
    {
      icon: Zap,
      label: 'Question Embedding',
      color: 'text-purple-300 bg-purple-900/40 border-purple-700/40',
      detail: 'Gemini embedding-001 — question → 3072-dim vector',
    },
    {
      icon: Database,
      label: 'FAISS Similarity Search',
      color: 'text-blue-300 bg-blue-900/40 border-blue-700/40',
      detail: `Cosine similarity over indexed document chunks → ${data.retrieved_chunks} chunk(s) retrieved`,
    },
    {
      icon: FileText,
      label: 'Retrieved Evidence',
      color: 'text-teal-300 bg-teal-900/40 border-teal-700/40',
      detail: data.sources.length > 0
        ? data.sources.map(s => `${s.document_name} (page ${s.page_number}, score ${(s.relevance_score * 100).toFixed(1)}%)`).join(' · ')
        : 'No relevant evidence found in indexed documents',
    },
    {
      icon: BookOpen,
      label: 'Gemini Answer Generation',
      color: 'text-cyan-300 bg-cyan-900/40 border-cyan-700/40',
      detail: 'Grounded generation — answer constructed using ONLY retrieved evidence',
    },
    {
      icon: GitMerge,
      label: 'Validation Agent',
      color: 'text-amber-300 bg-amber-900/40 border-amber-700/40',
      detail: `Fact-check: ${data.validation.reasoning || data.support_level}`,
    },
    {
      icon: BadgeCheck,
      label: 'Final Verified Answer',
      color: data.support_level === 'SUPPORTED'
        ? 'text-emerald-300 bg-emerald-900/40 border-emerald-700/40'
        : data.support_level === 'PARTIALLY_SUPPORTED'
          ? 'text-amber-300 bg-amber-900/40 border-amber-700/40'
          : 'text-red-300 bg-red-900/40 border-red-700/40',
      detail: data.support_level === 'SUPPORTED'
        ? 'All claims verified against evidence — Delivered'
        : data.support_level === 'PARTIALLY_SUPPORTED'
          ? 'Some claims verified — Delivered with partial confidence'
          : 'Evidence insufficient — NOT_IN_EVIDENCE returned',
    },
  ];

  return (
    <div className="bg-gray-800/50 border border-gray-700/60 rounded-2xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-700/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <GitMerge className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-gray-300">How this answer was generated</span>
          <span className="text-[10px] text-gray-600 ml-1">RAG Pipeline</span>
        </div>
        {open
          ? <ChevronUp className="w-4 h-4 text-gray-500" />
          : <ChevronDown className="w-4 h-4 text-gray-500" />
        }
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-1.5">
              {steps.map((s, i) => {
                const Icon = s.icon;
                const isLast = i === steps.length - 1;
                return (
                  <div key={i}>
                    <div className={`flex items-start gap-3 rounded-xl px-3 py-2.5 border ${s.color}`}>
                      <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
                        <span className="text-[10px] font-bold opacity-60 w-3">{i + 1}</span>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <p className="text-xs font-semibold">{s.label}</p>
                        <p className="text-[11px] opacity-60 mt-0.5 leading-relaxed">{s.detail}</p>
                      </div>
                    </div>
                    {!isLast && (
                      <div className="flex items-center justify-center py-0.5">
                        <ArrowDown className="w-3 h-3 text-gray-700" />
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Retrieved evidence raw preview */}
              {data.top_evidence.length > 0 && (
                <div className="mt-3 border-t border-gray-700/40 pt-3">
                  <button
                    onClick={onToggleEvidence}
                    className="flex items-center gap-1.5 text-[11px] text-gray-500 hover:text-gray-300 transition-colors mb-2"
                  >
                    {showEvidence
                      ? <ChevronUp className="w-3 h-3" />
                      : <ChevronDown className="w-3 h-3" />
                    }
                    {showEvidence ? 'Hide' : 'Show'} raw retrieved chunks ({data.top_evidence.length})
                  </button>
                  <AnimatePresence>
                    {showEvidence && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden space-y-2"
                      >
                        {data.top_evidence.map((ev, i) => (
                          <div key={i} className="bg-gray-900/50 border border-gray-700/40 rounded-xl p-3">
                            <div className="flex items-center gap-2 mb-1.5">
                              <span className="bg-indigo-900/60 text-indigo-300 px-2 py-0.5 rounded-full text-[10px] font-bold">
                                Score {(ev.score * 100).toFixed(1)}%
                              </span>
                              <span className="text-[10px] text-gray-500">{ev.document_name}</span>
                              <span className="text-[10px] text-gray-600">· Page {ev.page_number}</span>
                            </div>
                            <p className="text-[11px] text-gray-400 leading-relaxed">{ev.text_preview}</p>
                          </div>
                        ))}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ── Source card ───────────────────────────────────────────────────────────────
function SourceCard({ src, rank }: { src: Source; rank: number }) {
  const pct = (src.relevance_score * 100).toFixed(1);
  const barW = Math.min(src.relevance_score * 100, 100);
  return (
    <div className="bg-gray-700/30 border border-gray-700/50 rounded-xl p-3 space-y-2">
      <div className="flex items-start gap-2.5">
        <div className="w-6 h-6 rounded-full bg-indigo-900/60 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-[10px] font-bold text-indigo-300">{rank}</span>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">{src.document_name}</p>
          <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
            <span>Page {src.page_number}</span>
            {src.section && <><span>·</span><span className="truncate">{src.section}</span></>}
          </div>
        </div>
        <span className="text-xs font-semibold text-indigo-300 flex-shrink-0">{pct}%</span>
      </div>
      {/* Relevance bar */}
      <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${barW}%` }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className={`h-full rounded-full ${
            barW >= 80 ? 'bg-emerald-500' : barW >= 60 ? 'bg-indigo-500' : 'bg-amber-500'
          }`}
        />
      </div>
    </div>
  );
}

// ── Suggestion chips ──────────────────────────────────────────────────────────
const SUGGESTIONS = [
  'What are the eligibility requirements mentioned in this policy?',
  'What documents are required to apply for a loan?',
  'What is the minimum credit score required?',
  'What is the maximum DTI ratio allowed for loan approval?',
  'What happens if my loan application is rejected?',
  'What are the borrower rights mentioned in this policy?',
];

// ── Main Component ────────────────────────────────────────────────────────────
export const PolicyQA = () => {
  const [question, setQuestion]       = useState('');
  const [loading, setLoading]         = useState(false);
  const [result, setResult]           = useState<RAGResponse | null>(null);
  const [error, setError]             = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [topK, setTopK]               = useState(5);

  // Loading animation step: 0=idle 1=retrieve 2=generate 3=validate 4=done
  const [step, setStep] = useState(0);

  const handleAsk = async (q?: string) => {
    const query = (q ?? question).trim();
    if (!query) return;
    if (q) setQuestion(q);

    setLoading(true);
    setResult(null);
    setError(null);
    setShowEvidence(false);
    setStep(1);

    try {
      const stepTimer = setInterval(() => {
        setStep(s => (s < 3 ? s + 1 : s));
      }, 1200);

      const res = await fetch(`${API}/rag/ask`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: query, top_k: topK }),
      });

      clearInterval(stepTimer);
      setStep(4);

      const data: RAGResponse = await res.json();
      if (!res.ok) {
        setError((data as any).detail || 'Request failed');
      } else {
        setResult(data);
      }
    } catch {
      setError('Could not reach the server. Is the backend running?');
    }

    setLoading(false);
    setTimeout(() => setStep(0), 500);
  };

  return (
    <div className="space-y-5">

      {/* ── Input card ─────────────────────────────────────────────────────── */}
      <div className="bg-gray-800 border border-gray-700 rounded-3xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white text-sm">Policy Question & Answer</h3>
          <span className="text-xs text-gray-500 ml-1">— grounded in indexed documents via RAG</span>
        </div>

        {/* Suggestion chips */}
        <div className="flex flex-wrap gap-2 mb-4">
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => handleAsk(s)}
              disabled={loading}
              className="text-xs px-3 py-1.5 bg-gray-700/60 hover:bg-indigo-900/50 border border-gray-600 hover:border-indigo-600 rounded-full text-gray-400 hover:text-indigo-300 transition-all disabled:opacity-40 text-left"
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !loading) handleAsk(); }}
              placeholder="Ask a policy question…"
              className="w-full bg-gray-700/60 border border-gray-600 focus:border-indigo-500 rounded-2xl pl-10 pr-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition-colors"
              disabled={loading}
            />
          </div>
          <select
            value={topK}
            onChange={e => setTopK(Number(e.target.value))}
            disabled={loading}
            className="bg-gray-700/60 border border-gray-600 rounded-2xl px-3 text-sm text-gray-400 outline-none"
          >
            {[3, 5, 8, 10].map(k => (
              <option key={k} value={k}>Top {k}</option>
            ))}
          </select>
          <button
            onClick={() => handleAsk()}
            disabled={loading || !question.trim()}
            className="px-5 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-2xl text-sm font-semibold text-white transition-colors flex items-center gap-2"
          >
            {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Ask
          </button>
        </div>
      </div>

      {/* ── Loading — pipeline progress ────────────────────────────────────── */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y:  0 }}
            exit={{ opacity: 0 }}
            className="bg-gray-800/60 border border-gray-700 rounded-2xl p-4"
          >
            <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wider">
              RAG Pipeline — Processing
            </p>
            <div className="flex flex-wrap gap-x-8 gap-y-2">
              <PipelineStep label="1. Question Embedding + FAISS Search"  active={step === 1} done={step > 1} />
              <PipelineStep label="2. Gemini Grounded Generation" active={step === 2} done={step > 2} />
              <PipelineStep label="3. Validation Agent Fact-Check"     active={step === 3} done={step > 3} />
              <PipelineStep label="4. Source-Backed Final Answer"        active={false}      done={step >= 4} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Error ─────────────────────────────────────────────────────────── */}
      {error && (
        <div className="bg-red-900/30 border border-red-700/50 rounded-2xl p-4 text-sm text-red-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* ── Result card ───────────────────────────────────────────────────── */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y:  0 }}
            className="bg-gray-800 border border-gray-700 rounded-3xl overflow-hidden"
          >
            {/* ── Header: question + verdict ── */}
            <div className="p-5 border-b border-gray-700/60 bg-gray-800/80">
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Question</p>
                  <p className="text-white font-medium text-sm leading-snug">{result.question}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
                  <SupportBadge level={result.support_level} />
                  <span className="text-[10px] text-gray-600">{result.retrieved_chunks} chunks retrieved</span>
                </div>
              </div>
            </div>

            <div className="p-5 space-y-4">

              {/* ── NOT_IN_EVIDENCE banner ── */}
              {result.support_level === 'UNSUPPORTED' && (
                <div className="rounded-2xl p-4 bg-red-950/50 border border-red-800/50">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
                    <span className="text-xs font-bold text-red-400 uppercase tracking-widest">NOT_IN_EVIDENCE</span>
                  </div>
                  <p className="text-sm text-white/80 leading-relaxed">
                    Information not found in the uploaded policy documents.
                  </p>
                  <p className="text-xs text-red-400/60 mt-1.5 leading-relaxed">
                    The system did not fabricate a policy answer. The retrieved document chunks did not
                    contain sufficient evidence to answer this question.
                  </p>
                </div>
              )}

              {/* ── Answer box ── */}
              <div className={`rounded-2xl p-4 border ${
                result.support_level === 'SUPPORTED'
                  ? 'bg-emerald-950/30 border-emerald-800/40'
                  : result.support_level === 'PARTIALLY_SUPPORTED'
                    ? 'bg-amber-950/30 border-amber-800/40'
                    : 'bg-gray-800/40 border-gray-700/50'
              }`}>
                <div className="flex items-center gap-2 mb-3">
                  {result.support_level === 'SUPPORTED'
                    ? <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    : result.support_level === 'PARTIALLY_SUPPORTED'
                      ? <ShieldAlert className="w-4 h-4 text-amber-400" />
                      : <AlertCircle className="w-4 h-4 text-red-400" />
                  }
                  <span className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Answer</span>
                </div>
                {/* ── Markdown-rendered answer ── */}
                <MarkdownAnswer text={result.answer} />
              </div>

              {/* ── Validation box ── */}
              <div className="bg-gray-700/25 border border-gray-700/40 rounded-xl p-3.5">
                <div className="flex items-center gap-2 mb-2">
                  <GitMerge className="w-3.5 h-3.5 text-gray-500" />
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">
                    Validation Agent
                  </p>
                  <SupportBadge level={result.support_level} />
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">{result.validation.reasoning}</p>
                {result.validation.unsupported_claims.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-700/40">
                    <p className="text-xs text-amber-400 font-medium mb-1">Claims removed (not supported by evidence):</p>
                    <ul className="text-xs text-gray-500 space-y-0.5 list-disc list-inside">
                      {result.validation.unsupported_claims.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* ── Sources ── */}
              {result.sources.length > 0 && (
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold mb-2 flex items-center gap-1.5">
                    <FileText className="w-3 h-3" /> Source / Evidence
                  </p>
                  <div className="space-y-2">
                    {result.sources.map((src, i) => (
                      <SourceCard key={src.chunk_id + i} src={src} rank={i + 1} />
                    ))}
                  </div>
                </div>
              )}

              {/* ── RAG Pipeline (expandable) ── */}
              <RAGPipelineVisual
                data={result}
                showEvidence={showEvidence}
                onToggleEvidence={() => setShowEvidence(e => !e)}
              />

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
