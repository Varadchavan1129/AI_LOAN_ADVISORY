import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  Send, MessageCircle, ClipboardList, ArrowLeft, Sparkles,
  Loader, BookOpen, Calculator, ShieldCheck, UserCheck
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Message, Step, StructuredLoanData, LoanResult, ChatMode, QueryResult } from '../types';
import { MessageList } from './MessageList';
import { QueryResultCard } from './QueryResultCard';
import { API } from '../api';

// ── Structured Wizard Step Questions ─────────────────────────────────────────
const STEP_QUESTIONS: Record<Step, string> = {
  income:      'What is your monthly net income? (in ₹, e.g. 60000)',
  employment:  'What is your employment type? (e.g. Salaried, Self-Employed, Business)',
  age:         'What is your age in years? (e.g. 30)',
  cibil:       'What is your CIBIL / credit score? (300-900, e.g. 750)',
  emi:         'What is your existing total monthly EMI? (₹0 if none)',
  amount:      'How much loan amount do you need? (in ₹, e.g. 500000)',
  tenure:      'What loan tenure are you looking for? (in months, e.g. 36 or 60)',
  purpose:     'What is the purpose of this loan? (e.g. Personal, Home Renovation, Education, Business)',
  processing:  'Processing your financial profile assessment…',
  done:        'Assessment complete!',
};

const STEP_ORDER: Step[] = [
  'income',
  'employment',
  'age',
  'cibil',
  'emi',
  'amount',
  'tenure',
  'purpose',
  'processing',
  'done',
];

// ── Suggested NL Prompts ─────────────────────────────────────────────────────
const SUGGESTIONS = [
  'I earn ₹60,000, have an ₹8,000 EMI, CIBIL 750 and need ₹5 lakh for 3 years.',
  'I make ₹85,000 as salaried, age 32, CIBIL 780, need ₹10 lakh for home renovation.',
  'What EMI for ₹5 lakh at 10.5% for 5 years?',
  'I earn ₹50,000 with ₹10,000 existing EMI — how much loan can I get?',
  'What credit score is required for a personal loan?',
  'What is the maximum DTI / FOIR ratio allowed?',
];

// ── Small inline chat components ─────────────────────────────────────────────
function BotBubble({ text }: { text: string }) {
  return (
    <div className="flex gap-2 items-start">
      <div className="w-8 h-8 rounded-full bg-indigo-500/30 flex items-center justify-center flex-shrink-0">
        <Sparkles className="w-4 h-4 text-indigo-300" />
      </div>
      <div className="max-w-[85%] bg-white/10 border border-white/15 rounded-2xl rounded-tl-none px-4 py-3">
        <p className="text-sm text-white/90 leading-relaxed whitespace-pre-wrap">{text}</p>
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
  const [language, setLanguage] = useState<'en' | 'hi' | 'mr'>('en');
  const [isLoading, setLoading] = useState(false);
  const [loadingHint, setHint]  = useState('Thinking…');
  const bottomRef               = useRef<HTMLDivElement>(null);
  const hintTimerRef            = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── NL Chat state ─────────────────────────────────────────────────────────
  const [chatMessages, setChatMessages] = useState<Message[]>([]);

  // ── Wizard state ──────────────────────────────────────────────────────────
  const [wizardMessages, setWizardMessages] = useState<Message[]>([]);
  const [currentStep, setCurrentStep]       = useState<Step>('income');
  const [loanData, setLoanData]             = useState<StructuredLoanData>({
    income: '',
    employment: 'Salaried',
    age: '30',
    cibil: '750',
    emi: '0',
    amount: '',
    tenure: '60',
    purpose: 'Personal',
  });

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
        content: "Hi! I'm Tata Mitra, your AI Loan Advisor 👋 You can ask any question or share your financial profile (e.g., 'I earn ₹60,000, have an ₹8,000 EMI, CIBIL 750 and need ₹5 lakh for 3 years') for an instant affordability assessment!",
        timestamp: new Date(),
      }]);
    } else if (mode === 'apply') {
      setWizardMessages([
        {
          id: 'w1',
          type: 'bot',
          content: "Welcome to the Structured Financial Profile Assessment! Let's evaluate your eligibility and EMI capacity across 8 quick questions.",
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
      setLoanData({
        income: '',
        employment: 'Salaried',
        age: '30',
        cibil: '750',
        emi: '0',
        amount: '',
        tenure: '60',
        purpose: 'Personal',
      });
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
    setHint('Evaluating financial profile…');
    hintTimerRef.current = setTimeout(() => {
      setHint('Calculating deterministic EMI & FOIR metrics…');
      hintTimerRef.current = setTimeout(() => {
        setHint('Running risk analysis & policy rules…');
      }, 1500);
    }, 1200);
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
      const res = await fetch(`${API}/chat/query`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message: text, language }),
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
  const processLoanApplication = async (data: StructuredLoanData) => {
    startLoading();
    try {
      const res = await fetch(`${API}/financial-profile/assess`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          monthly_income:  parseFloat(data.income) || 0,
          existing_emi:    parseFloat(data.emi) || 0,
          loan_amount:     parseFloat(data.amount) || 0,
          tenure_months:   parseInt(data.tenure) || 60,
          employment_type: data.employment || 'salaried',
          age:             parseInt(data.age) || 30,
          credit_score:    parseInt(data.cibil) || 750,
          loan_purpose:    data.purpose || 'personal',
        }),
      });

      if (!res.ok) throw new Error(`Server error (${res.status}): ${await res.text()}`);

      const resp = await res.json();
      const result: LoanResult = {
        status:     resp.status,
        title:      resp.title,
        message:    resp.message,
        advice:     resp.personalized_improvement_advice,
        assessment: resp.assessment,
        profile:    resp.profile,
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
    } finally {
      stopLoading();
    }
  };

  // ── Wizard: handle each step ───────────────────────────────────────────────
  const handleWizardSend = async () => {
    const text = input.trim();
    if (!text || isLoading || currentStep === 'done') return;

    // Numeric validations for numeric steps
    if (['income', 'age', 'cibil', 'emi', 'amount', 'tenure'].includes(currentStep)) {
      const num = parseFloat(text);
      if (!isFinite(num) || num < 0) {
        setWizardMessages(prev => [...prev, {
          id:        Date.now().toString(),
          type:      'bot',
          content:   'Please enter a valid positive number.',
          timestamp: new Date(),
        }]);
        return;
      }
    }

    setWizardMessages(prev => [...prev, {
      id: Date.now().toString(), type: 'user', content: text, timestamp: new Date(),
    }]);
    setInput('');

    const updated = { ...loanData, [currentStep]: text };
    setLoanData(updated);

    const nextIndex = STEP_ORDER.indexOf(currentStep) + 1;
    const next = STEP_ORDER[nextIndex];

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
      }, 350);
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
              {msg.queryResult.type === 'assessment'
                ? <UserCheck  className="w-4 h-4 text-emerald-300" />
                : msg.queryResult.type === 'policy'
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
            <p className="text-white/60">Your AI Financial Profile &amp; Loan Advisor</p>
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
                  <h2 className="text-white font-semibold text-lg">Chat &amp; Profile Assessment</h2>
                  <p className="text-white/50 text-sm">Ask questions or share financial numbers in natural language</p>
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
                  <h2 className="text-white font-semibold text-lg">Structured Assessment Wizard</h2>
                  <p className="text-white/50 text-sm">Step-by-step 8-point financial profile analysis</p>
                </div>
              </div>
            </motion.button>
          </div>

          {/* Suggestion chips */}
          <div className="mt-8">
            <p className="text-white/30 text-xs mb-3">Try asking in natural language:</p>
            <div className="flex flex-wrap gap-2 justify-center">
              {SUGGESTIONS.slice(0, 3).map(s => (
                <button
                  key={s}
                  onClick={() => { setMode('chat'); setTimeout(() => handleChatSend(s), 300); }}
                  className="text-xs bg-white/10 hover:bg-white/20 border border-white/15 rounded-full px-3 py-1.5 text-white/70 hover:text-white transition-all text-left"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-8">
            <Link to="/admin" className="text-xs text-white/25 hover:text-white/50 transition-colors">
              Employee / Admin Portal
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
      <div className="max-w-3xl mx-auto h-[92vh] flex flex-col">

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
              {mode === 'chat' ? 'Tata Mitra Loan Advisor' : 'Structured Financial Assessment'}
            </h1>
          </div>
          {mode === 'apply' && (
            <span className="ml-auto text-xs text-white/50 border border-white/15 rounded-full px-3 py-1 bg-white/5">
              Step {Math.min(STEP_ORDER.indexOf(currentStep) + 1, 8)} of 8
            </span>
          )}
          {mode === 'chat' && (
            <select
              data-testid="language-selector"
              value={language}
              onChange={e => setLanguage(e.target.value as 'en' | 'hi' | 'mr')}
              className="ml-auto text-xs bg-white/10 border border-white/20 rounded-full px-3 py-1.5 text-white/80 focus:outline-none focus:ring-2 focus:ring-white/30 cursor-pointer [&>option]:text-gray-900"
              title="Response language"
            >
              <option value="en">English</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="mr">मराठी (Marathi)</option>
            </select>
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
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    onClick={() => handleChatSend(s)}
                    className="text-xs bg-white/10 hover:bg-white/20 border border-white/15 rounded-full px-3 py-1 text-white/60 hover:text-white transition-all text-left"
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
                    ? (currentStep === 'done' ? 'Assessment complete' : 'Evaluating…')
                    : mode === 'chat'
                      ? 'Ask anything or share your financial profile…'
                      : `Enter ${currentStep}…`
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
