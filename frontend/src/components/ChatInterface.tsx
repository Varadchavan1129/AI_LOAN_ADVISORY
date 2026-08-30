import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Send, MessageCircle, ClipboardList, ArrowLeft, Sparkles,
  Loader, BookOpen, Calculator, ShieldCheck,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, Step, LoanData, LoanResult, ChatMode, QueryResult } from '../types';
import { MessageList } from './MessageList';
import { QueryResultCard } from './QueryResultCard';

// ── Wizard step questions ────────────────────────────────────────────────────
const STEP_QUESTIONS: Record<string, string> = {
  income:  'What is your monthly income? (in ₹)',
  emi:     'What is your existing monthly EMI? (₹0 if none)',
  amount:  'How much loan amount do you need? (in ₹)',
  tenure:  'What loan tenure are you looking for? (in months, e.g. 60)',
};

// ── Suggested NL prompts (includes policy questions) ─────────────────────────
const SUGGESTIONS = [
  'What EMI for ₹5 lakh at 10% for 5 years?',
  'I earn ₹60,000 — how much loan can I get?',
  'What credit score is required for a personal loan?',
  'Am I eligible: ₹50,000 income, ₹5,000 EMI, ₹3 lakh loan?',
  'What is the maximum DTI ratio allowed?',
  'What documents are needed to apply for a loan?',
  'What happens if my loan is rejected?',
];

// ── Loading step labels for the typing indicator ──────────────────────────────
const LOADING_HINTS = [
  { icon: Loader,       label: 'Thinking…' },
  { icon: BookOpen,     label: 'Searching policy documents…' },
  { icon: ShieldCheck,  label: 'Verifying answer…' },
];

// ── Small inline chat components ─────────────────────────────────────────────
function BotBubble({ text }: { text: string }) {
  return (
    <div className="flex gap-2 items-start">
      <div className="w-8 h-8 rounded-full bg-indigo-500/30 flex items-center justify-center flex-shrink-0">
        <Sparkles className="w-4 h-4 text-indigo-300" />
      </div>
      <div className="max-w-[85%] bg-white/10 border border-white/15 rounded-2xl rounded-tl-none px-4 py-3">
        <p className="text-sm text-white/90 leading-relaxed">{text}</p>
      </div>
    </div>
  );
}

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[80%] bg-indigo-600/70 border border-indigo-500/40 rounded-2xl rounded-tr-none px-4 py-3">
        <p className="text-sm text-white leading-relaxed">{text}</p>
      </div>
    </div>
  );
}

function LoadingBubble({ hint }: { hint: string }) {
  return (
    <div className="flex gap-2 items-start">
      <div className="w-8 h-8 rounded-full bg-indigo-500/30 flex items-center justify-center flex-shrink-0">
        <Loader className="w-4 h-4 text-indigo-300 animate-spin" />
      </div>
      <div className="bg-white/10 border border-white/15 rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-2">
        <span className="flex gap-1">
          {[0, 1, 2].map(i => (
            <motion.span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-indigo-300"
              animate={{ y: [0, -4, 0] }}
              transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
            />
          ))}
        </span>
        <span className="text-xs text-white/50 ml-1">{hint}</span>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export const ChatInterface = () => {
  // ── Shared state ──────────────────────────────────────────────────────────
  const [mode, setMode]         = useState<ChatMode>('select');
  const [input, setInput]       = useState('');
  const [isLoading, setLoading] = useState(false);
  const [loadingHint, setHint]  = useState('Thinking…');
  const bottomRef               = useRef<HTMLDivElement>(null);
  const hintTimerRef            = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── NL Chat state ─────────────────────────────────────────────────────────
  const [chatMessages, setChatMessages] = useState<Message[]>([]);

  // ── Wizard state ──────────────────────────────────────────────────────────
  const [wizardMessages, setWizardMessages] = useState<Message[]>([]);
  const [currentStep, setCurrentStep]       = useState<Step>('income');
  const [loanData, setLoanData]             = useState<LoanData>({ income: '', emi: '', amount: '', tenure: '' });

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, wizardMessages, isLoading]);

  // Cleanup hint timer on unmount
  useEffect(() => () => { if (hintTimerRef.current) clearTimeout(hintTimerRef.current); }, []);

  // ── Mode entry ────────────────────────────────────────────────────────────
  useEffect(() => {
    if (mode === 'chat') {
      setChatMessages([{
        id: 'c1',
        type: 'bot',
        content: "Hi! I'm Tata Mitra 👋 Ask me anything about loans — eligibility, EMI, DTI, max loan amount, policy rules, and more.",
        timestamp: new Date(),
      }]);
    } else if (mode === 'apply') {
      setWizardMessages([
        {
          id: 'w1',
          type: 'bot',
          content: "Let's check your loan eligibility! I'll ask you 4 quick questions.",
          timestamp: new Date(),
        },
        {
          id: 'w2',
          type: 'bot',
          content: STEP_QUESTIONS.income,
          timestamp: new Date(),
        },
      ]);
      setCurrentStep('income');
      setLoanData({ income: '', emi: '', amount: '', tenure: '' });
    }
  }, [mode]);

  // ── Reset to select screen ────────────────────────────────────────────────
  const goBack = () => {
    setMode('select');
    setInput('');
    setLoading(false);
  };

  // ── Start loading with progressive hints ─────────────────────────────────
  const startLoading = () => {
    setLoading(true);
    setHint('Thinking…');
    // After 1.5s hint: searching policy docs
    hintTimerRef.current = setTimeout(() => {
      setHint('Searching policy documents…');
      // After another 2s hint: verifying
      hintTimerRef.current = setTimeout(() => {
        setHint('Verifying answer…');
      }, 2000);
    }, 1500);
  };

  const stopLoading = () => {
    setLoading(false);
    if (hintTimerRef.current) {
      clearTimeout(hintTimerRef.current);
      hintTimerRef.current = null;
    }
    setHint('Thinking…');
  };

  // ── NL Chat: send message ──────────────────────────────────────────────────
  const handleChatSend = async (overrideText?: string) => {
    const text = (overrideText ?? input).trim();
    if (!text || isLoading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: text,
      timestamp: new Date(),
    };
    setChatMessages(prev => [...prev, userMsg]);
    setInput('');
    startLoading();

    try {
      const res = await fetch('/chat/query', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        const errBody = await res.text().catch(() => '');
        throw new Error(`Server error ${res.status}${errBody ? ': ' + errBody : ''}`);
      }

      const data: QueryResult = await res.json();

      const botMsg: Message = {
        id:          (Date.now() + 1).toString(),
        type:        'query_result',
        content:     data.message,
        timestamp:   new Date(),
        queryResult: data,
      };
      setChatMessages(prev => [...prev, botMsg]);
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : 'Unknown error';
      setChatMessages(prev => [...prev, {
        id:        (Date.now() + 1).toString(),
        type:      'bot',
        content:   `⚠️ Something went wrong: ${errMsg}. Please try again.`,
        timestamp: new Date(),
      }]);
    } finally {
      stopLoading();
    }
  };

  // ── Wizard: process final submission ──────────────────────────────────────
  const processLoanApplication = async (data: LoanData) => {
    startLoading();
    try {
      const res = await fetch('/chat/apply-loan', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          monthly_income: parseFloat(data.income),
          existing_emi:   parseFloat(data.emi),
          loan_amount:    parseFloat(data.amount),
          tenure_months:  parseInt(data.tenure),
        }),
      });

      if (!res.ok) throw new Error(`Server error (${res.status}): ${await res.text()}`);

      const resp = await res.json();
      const result: LoanResult = {
        status:  resp.status,
        title:   resp.title,
        message: resp.message,
        advice:  resp.personalized_improvement_advice,
      };

      setWizardMessages(prev => [...prev, {
        id:        Date.now().toString(),
        type:      'result',
        content:   '',
        timestamp: new Date(),
        result,
      }]);
      setCurrentStep('done');
    } catch (err) {
      setWizardMessages(prev => [...prev, {
        id:        Date.now().toString(),
        type:      'bot',
        content:   `Error: ${(err as Error).message}. Please try again.`,
        timestamp: new Date(),
      }]);
      setCurrentStep('income');
      setLoanData({ income: '', emi: '', amount: '', tenure: '' });
    } finally {
      stopLoading();
    }
  };

  // ── Wizard: handle each step ───────────────────────────────────────────────
  const handleWizardSend = async () => {
    const text = input.trim();
    if (!text || isLoading || currentStep === 'done') return;

    if (!isFinite(parseFloat(text)) || parseFloat(text) < 0) {
      setWizardMessages(prev => [...prev, {
        id:        Date.now().toString(),
        type:      'bot',
        content:   'Please enter a valid number (0 or more).',
        timestamp: new Date(),
      }]);
      return;
    }

    setWizardMessages(prev => [...prev, {
      id: Date.now().toString(), type: 'user', content: text, timestamp: new Date(),
    }]);
    setInput('');

    const updated = { ...loanData, [currentStep]: text };
    setLoanData(updated);

    const order: Step[] = ['income', 'emi', 'amount', 'tenure', 'processing', 'done'];
    const next = order[order.indexOf(currentStep) + 1];

    if (next === 'processing') {
      setCurrentStep('processing');
      await processLoanApplication(updated);
    } else if (next && next !== 'done') {
      setTimeout(() => {
        setWizardMessages(prev => [...prev, {
          id:        Date.now().toString(),
          type:      'bot',
          content:   STEP_QUESTIONS[next],
          timestamp: new Date(),
        }]);
        setCurrentStep(next);
      }, 400);
    }
  };

  // ── Unified send dispatcher ───────────────────────────────────────────────
  const handleSend = () => (mode === 'chat' ? handleChatSend() : handleWizardSend());

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const inputDisabled =
    isLoading ||
    (mode === 'apply' && (currentStep === 'processing' || currentStep === 'done'));

  // ── Render messages for NL chat ───────────────────────────────────────────
  const renderChatMessages = () =>
    chatMessages.map(msg => (
      <div key={msg.id}>
        {msg.type === 'user'         && <UserBubble text={msg.content} />}
        {msg.type === 'bot'          && <BotBubble  text={msg.content} />}
        {msg.type === 'query_result' && msg.queryResult && (
          <div className="flex gap-2 items-start">
            <div className="w-8 h-8 rounded-full bg-indigo-500/30 flex items-center justify-center flex-shrink-0 mt-1">
              {msg.queryResult.type === 'policy'
                ? <BookOpen   className="w-4 h-4 text-teal-300" />
                : msg.queryResult.type === 'emi'
                  ? <Calculator className="w-4 h-4 text-indigo-300" />
                  : <Sparkles   className="w-4 h-4 text-indigo-300" />
              }
            </div>
            <div className="flex-1">
              <QueryResultCard result={msg.queryResult} />
            </div>
          </div>
        )}
      </div>
    ));

  // ─────────────────────────────────────────────────────────────────────────
  // SELECT SCREEN
  // ─────────────────────────────────────────────────────────────────────────
  if (mode === 'select') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 flex flex-col items-center justify-center p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md text-center"
        >
          {/* Logo / header */}
          <div className="mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">Tata Mitra</h1>
            <p className="text-white/60">Your AI Loan Advisor</p>
          </div>

          {/* Mode cards */}
          <div className="space-y-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('chat')}
              className="w-full p-5 rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 hover:bg-white/15 transition-all text-left group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-indigo-500/30 flex items-center justify-center group-hover:bg-indigo-500/50 transition-colors">
                  <MessageCircle className="w-6 h-6 text-indigo-200" />
                </div>
                <div>
                  <h2 className="text-white font-semibold text-lg">Ask a Question</h2>
                  <p className="text-white/50 text-sm">EMI, eligibility, DTI, policy rules &amp; more</p>
                </div>
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('apply')}
              className="w-full p-5 rounded-2xl bg-white/10 backdrop-blur-lg border border-white/20 hover:bg-white/15 transition-all text-left group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/30 flex items-center justify-center group-hover:bg-purple-500/50 transition-colors">
                  <ClipboardList className="w-6 h-6 text-purple-200" />
                </div>
                <div>
                  <h2 className="text-white font-semibold text-lg">Apply for a Loan</h2>
                  <p className="text-white/50 text-sm">Full eligibility check with AI analysis</p>
                </div>
              </div>
            </motion.button>
          </div>

          {/* Suggestion chips */}
          <div className="mt-8">
            <p className="text-white/30 text-xs mb-3">Try asking:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.map(s => (
                <button
                  key={s}
                  onClick={() => { setMode('chat'); setTimeout(() => handleChatSend(s), 300); }}
                  className="text-xs bg-white/10 hover:bg-white/20 border border-white/15 rounded-full px-3 py-1.5 text-white/70 hover:text-white transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <Link to="/admin" className="text-xs text-white/25 hover:text-white/50 transition-colors">
              Employee Login
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // CHAT / APPLY SCREENS (shared shell)
  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-indigo-800 p-4 md:p-8">
      <div className="max-w-2xl mx-auto h-[92vh] flex flex-col">

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={goBack}
            className="p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors border border-white/15"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </button>
          <div className="flex items-center gap-2">
            {mode === 'chat'
              ? <MessageCircle className="w-5 h-5 text-indigo-200" />
              : <ClipboardList className="w-5 h-5 text-purple-200" />
            }
            <h1 className="text-lg font-semibold text-white">
              {mode === 'chat' ? 'Ask Tata Mitra' : 'Loan Application'}
            </h1>
          </div>
          {/* Subtle indicator: policy answers are document-grounded */}
          {mode === 'chat' && (
            <span className="ml-auto flex items-center gap-1.5 text-xs text-white/30 border border-white/10 rounded-full px-2.5 py-1">
              <BookOpen className="w-3 h-3" /> Policy answers sourced from documents
            </span>
          )}
        </div>

        {/* Message area */}
        <div className="flex-1 bg-white/10 backdrop-blur-lg rounded-3xl border border-white/20 shadow-2xl overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">

            {/* NL Chat messages */}
            {mode === 'chat' && renderChatMessages()}

            {/* Wizard messages */}
            {mode === 'apply' && (
              <MessageList messages={wizardMessages} isLoading={isLoading} />
            )}

            {/* Animated loading indicator with progressive hints */}
            <AnimatePresence>
              {isLoading && mode === 'chat' && (
                <motion.div
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <LoadingBubble hint={loadingHint} />
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={bottomRef} />
          </div>

          {/* Input bar */}
          <div className="p-4 border-t border-white/15 bg-white/5">
            {/* Suggestion chips — only in chat mode when few messages */}
            {mode === 'chat' && chatMessages.length <= 1 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {SUGGESTIONS.slice(0, 4).map(s => (
                  <button
                    key={s}
                    onClick={() => handleChatSend(s)}
                    className="text-xs bg-white/10 hover:bg-white/20 border border-white/15 rounded-full px-3 py-1 text-white/60 hover:text-white transition-all"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                disabled={inputDisabled}
                placeholder={
                  inputDisabled
                    ? (currentStep === 'done' ? 'Application complete' : 'Processing…')
                    : mode === 'chat'
                      ? 'Ask anything about loans or policy…'
                      : 'Enter your answer…'
                }
                className="flex-1 px-4 py-3 rounded-xl bg-white/10 backdrop-blur-lg border border-white/20 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-white/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              />
              <button
                onClick={handleSend}
                disabled={inputDisabled || !input.trim()}
                className="px-5 py-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white font-medium hover:from-indigo-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-white/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
              >
                {isLoading && mode === 'chat'
                  ? <Loader className="w-4 h-4 animate-spin" />
                  : <Send className="w-4 h-4" />
                }
                <span className="hidden sm:inline text-sm">Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
