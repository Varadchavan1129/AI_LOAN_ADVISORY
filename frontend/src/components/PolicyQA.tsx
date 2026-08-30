import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, CheckCircle, AlertCircle, HelpCircle,
  FileText, Loader, BookOpen, ChevronDown, ChevronUp,
  Shield, ShieldCheck, ShieldAlert
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
    SUPPORTED:           { label: 'Verified',          Icon: ShieldCheck, cls: 'bg-emerald-900/60 border-emerald-700/50 text-emerald-300' },
    PARTIALLY_SUPPORTED: { label: 'Partially Verified', Icon: ShieldAlert,  cls: 'bg-amber-900/60 border-amber-700/50 text-amber-300' },
    UNSUPPORTED:         { label: 'Unverified',         Icon: AlertCircle,  cls: 'bg-red-900/60 border-red-700/50 text-red-300' },
  }[level] ?? { label: level, Icon: HelpCircle, cls: 'bg-gray-700 border-gray-600 text-gray-400' };

  const { label, Icon, cls } = cfg;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${cls}`}>
      <Icon className="w-3.5 h-3.5" />
      {label}
    </span>
  );
}

// ── Pipeline step ─────────────────────────────────────────────────────────────
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

// ── Suggestion chips ──────────────────────────────────────────────────────────
const SUGGESTIONS = [
  'What credit score is required for a personal loan?',
  'How is EMI calculated?',
  'What is the maximum DTI ratio allowed?',
  'What documents are needed for a loan?',
  'What happens if my loan is rejected?',
];

// ── Main Component ────────────────────────────────────────────────────────────
export const PolicyQA = () => {
  const [question, setQuestion]       = useState('');
  const [loading, setLoading]         = useState(false);
  const [result, setResult]           = useState<RAGResponse | null>(null);
  const [error, setError]             = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [topK, setTopK]               = useState(5);

  // Pipeline progress states
  const [step, setStep] = useState(0); // 0=idle 1=retrieve 2=generate 3=validate 4=done

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
      // Simulate pipeline step progression for UX
      const stepTimer = setInterval(() => {
        setStep(s => (s < 3 ? s + 1 : s));
      }, 1200);

      const res  = await fetch('/rag/ask', {
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
    } catch (e) {
      setError('Could not reach the server. Is the backend running?');
    }

    setLoading(false);
    setTimeout(() => setStep(0), 500);
  };

  return (
    <div className="space-y-6">

      {/* Question input */}
      <div className="bg-gray-800 border border-gray-700 rounded-3xl p-5">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-indigo-400" />
          <h3 className="font-semibold text-white text-sm">Policy Question & Answer</h3>
          <span className="text-xs text-gray-500 ml-1">— answers grounded in indexed documents</span>
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap gap-2 mb-4">
          {SUGGESTIONS.map(s => (
            <button
              key={s}
              onClick={() => handleAsk(s)}
              disabled={loading}
              className="text-xs px-3 py-1.5 bg-gray-700/60 hover:bg-indigo-900/50 border border-gray-600 hover:border-indigo-600 rounded-full text-gray-400 hover:text-indigo-300 transition-all disabled:opacity-40"
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
              placeholder="Ask a policy question (e.g. What credit score do I need?)…"
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

      {/* Pipeline progress */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y:  0 }}
            exit={{ opacity: 0 }}
            className="bg-gray-800/60 border border-gray-700 rounded-2xl p-4"
          >
            <p className="text-xs text-gray-500 mb-3 font-medium uppercase tracking-wider">RAG Pipeline</p>
            <div className="flex flex-wrap gap-x-6 gap-y-2">
              <PipelineStep label="1. Semantic Retrieval"  active={step === 1} done={step > 1} />
              <PipelineStep label="2. Grounded Generation" active={step === 2} done={step > 2} />
              <PipelineStep label="3. Fact Validation"     active={step === 3} done={step > 3} />
              <PipelineStep label="4. Final Answer"        active={false}      done={step >= 4} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      {error && (
        <div className="bg-red-900/30 border border-red-700/50 rounded-2xl p-4 text-sm text-red-300 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Result card */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y:  0 }}
            className="bg-gray-800 border border-gray-700 rounded-3xl overflow-hidden"
          >
            {/* Answer header */}
            <div className="p-5 border-b border-gray-700/60">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Question</p>
                  <p className="text-white font-medium">{result.question}</p>
                </div>
                <div className="flex-shrink-0 flex flex-col items-end gap-2">
                  <SupportBadge level={result.support_level} />
                  <span className="text-xs text-gray-600">{result.retrieved_chunks} chunks retrieved</span>
                </div>
              </div>
            </div>

            {/* Answer body */}
            <div className="p-5">
              <div className={`rounded-2xl p-4 mb-5 ${
                result.support_level === 'SUPPORTED'
                  ? 'bg-emerald-950/40 border border-emerald-800/40'
                  : result.support_level === 'PARTIALLY_SUPPORTED'
                    ? 'bg-amber-950/40 border border-amber-800/40'
                    : 'bg-red-950/40 border border-red-800/40'
              }`}>
                <div className="flex items-center gap-2 mb-3">
                  {result.support_level === 'SUPPORTED'
                    ? <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    : result.support_level === 'PARTIALLY_SUPPORTED'
                      ? <ShieldAlert className="w-4 h-4 text-amber-400" />
                      : <AlertCircle className="w-4 h-4 text-red-400" />
                  }
                  <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Answer</span>
                </div>
                <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{result.answer}</p>
              </div>

              {/* Sources */}
              {result.sources.length > 0 && (
                <div className="mb-5">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-medium">📌 Sources</p>
                  <div className="space-y-2">
                    {result.sources.map((src, i) => (
                      <div key={src.chunk_id + i} className="flex items-start gap-3 bg-gray-700/40 rounded-xl p-3">
                        <FileText className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-white">{src.document_name}</p>
                          <div className="flex items-center gap-2 mt-0.5 text-xs text-gray-500">
                            <span>Page {src.page_number}</span>
                            {src.section && <span>· {src.section}</span>}
                            <span>· score {src.relevance_score.toFixed(3)}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Validation reasoning */}
              <div className="bg-gray-700/30 rounded-xl p-3 mb-4">
                <p className="text-xs text-gray-500 uppercase tracking-wider mb-1.5 font-medium">Validation</p>
                <p className="text-xs text-gray-400 leading-relaxed">{result.validation.reasoning}</p>
                {result.validation.unsupported_claims.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-amber-400 font-medium mb-1">Unsupported claims removed:</p>
                    <ul className="text-xs text-gray-500 space-y-0.5 list-disc list-inside">
                      {result.validation.unsupported_claims.map((c, i) => (
                        <li key={i}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Evidence preview toggle */}
              {result.top_evidence.length > 0 && (
                <div>
                  <button
                    onClick={() => setShowEvidence(e => !e)}
                    className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors"
                  >
                    {showEvidence ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    {showEvidence ? 'Hide' : 'Show'} retrieved evidence
                  </button>
                  <AnimatePresence>
                    {showEvidence && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden mt-3 space-y-2"
                      >
                        {result.top_evidence.map((ev, i) => (
                          <div key={i} className="bg-gray-700/30 border border-gray-700/50 rounded-xl p-3">
                            <div className="flex items-center gap-2 mb-1.5 text-xs text-gray-500">
                              <span className="bg-indigo-900/50 text-indigo-300 px-2 py-0.5 rounded-full">
                                Score {ev.score.toFixed(3)}
                              </span>
                              <span>{ev.document_name}</span>
                              <span>· Page {ev.page_number}</span>
                            </div>
                            <p className="text-xs text-gray-400 leading-relaxed">{ev.text_preview}</p>
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
};
