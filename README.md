# 🏦 AI Loan Advisory Chatbot

> A production-ready, full-stack AI system that answers loan-related questions, checks eligibility, calculates EMIs, and retrieves policy-grounded answers from your own uploaded PDF documents — powered by Google Gemini, FAISS vector search, a scikit-learn ML risk model, and a React frontend.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Key Features](#-key-features)
4. [System Architecture](#-system-architecture)
5. [Tech Stack](#-tech-stack)
6. [Multi-Agent Pipeline](#-multi-agent-pipeline)
7. [RAG Pipeline (Document Q&A)](#-rag-pipeline-document-qa)
8. [Knowledge Base — PDFs Indexed](#-knowledge-base--pdfs-indexed)
9. [Project Structure](#-project-structure)
10. [API Endpoints](#-api-endpoints)
11. [Setup and Installation](#-setup-and-installation)
12. [Running the Project](#-running-the-project)
13. [Adding New PDF Documents](#-adding-new-pdf-documents)
14. [Environment Variables](#-environment-variables)
15. [How Each Question Type is Handled](#-how-each-question-type-is-handled)
16. [Frontend Pages and Components](#-frontend-pages-and-components)
17. [ML Model — Risk Assessment](#-ml-model--risk-assessment)
18. [Known Limitations](#-known-limitations)

---

## 🎯 Project Overview

**Tata Mitra** is an AI-powered loan advisory chatbot built for Indian customers. It can:

- Answer **natural language questions** about loans in Indian context (personal, home, car, gold, education, business, MSME, agriculture)
- **Calculate EMI** accurately using the reducing-balance method
- **Check loan eligibility** using a trained scikit-learn ML model + DTI rules
- **Calculate maximum loan amount** a customer can afford based on their income
- **Answer policy questions** from uploaded PDF documents using a RAG (Retrieval-Augmented Generation) pipeline
- **Administer documents** through a secure admin panel (upload, process, delete PDFs)
- Show a **live dashboard** with system statistics

The system is designed so that **no answer is hallucinated** — policy answers are grounded in uploaded documents, and financial calculations use deterministic math (no AI guessing).

---

## ❗ Problem Statement

Financial institutions handle thousands of loan queries daily. Customers need:

1. **Instant eligibility decisions** based on their financial profile — without visiting a branch
2. **Accurate EMI calculations** without relying on a bank agent
3. **Reliable policy answers** — not guesswork from a general-purpose chatbot
4. **Consistent information** about different loan types (personal, home, car, gold, education, business)

Traditional chatbots hallucinate loan amounts, interest rates, and eligibility criteria. This system solves that by:
- Using **deterministic math** for all financial calculations
- Using **RAG (Retrieval-Augmented Generation)** to ground answers in actual policy documents
- Using a **trained ML model** for risk assessment instead of a fixed rule set

---

## ✨ Key Features

| Feature | Description | Technology |
|---|---|---|
| 💬 Natural Language Chat | Understands loan queries in plain English/Hindi-English mix | Google Gemini + Regex fallback |
| 🔢 EMI Calculator | Exact EMI, total interest, total repayment | Deterministic math |
| ✅ Eligibility Check | Score 0-100, decision (Approved/Conditional/Rejected), risk % | Scikit-learn ML model |
| 📊 Max Loan Calculator | Maximum loan based on income, existing EMI, and DTI limit | Deterministic math |
| 📐 DTI Ratio Calculator | Debt-to-Income ratio with projected impact of new loan | Deterministic math |
| 📄 Document Q&A (RAG) | Answers from uploaded policy PDFs with source citations | FAISS + Gemini |
| 🗂️ Admin Panel | Upload, process, view, delete PDF documents | FastAPI + SQLite |
| 📈 Dashboard | Live stats: total documents, chunks, queries, system health | React + FastAPI |
| 🔒 Admin Authentication | Header-based API key authentication for admin endpoints | FastAPI Depends |
| 🔄 Graceful Degradation | Works even when Gemini API quota is exhausted (regex fallback + static answers) | Python regex |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER (Browser)                             │
│                    http://localhost:5173                             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────────────┐
│                    REACT FRONTEND (Vite + TypeScript)                │
│  ┌─────────────┐ ┌───────────────┐ ┌──────────────┐ ┌───────────┐ │
│  │ ChatInterface│ │  Dashboard    │ │DocumentManager│ │ PolicyQA  │ │
│  └─────────────┘ └───────────────┘ └──────────────┘ └───────────┘ │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP REST API
┌──────────────────────────────▼──────────────────────────────────────┐
│               FASTAPI BACKEND — http://localhost:8000                │
│                                                                      │
│  POST /chat/query          GET /api/dashboard/stats                 │
│  POST /admin/documents/*   GET /search/stats                        │
│  POST /rag/ask             GET /health                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   MULTI-AGENT PIPELINE                       │   │
│  │                                                              │   │
│  │  User Message                                                │   │
│  │       │                                                      │   │
│  │       ▼                                                      │   │
│  │  ┌─────────────┐   Gemini / Regex Fallback                  │   │
│  │  │  NLU Agent  │──→ intent + entities                       │   │
│  │  └──────┬──────┘                                            │   │
│  │         │                                                    │   │
│  │    ┌────▼──────────────────────────────────────────────┐    │   │
│  │    │           Intent Router                            │    │   │
│  │    │  emi_calculation → EMI Calculator (pure math)     │    │   │
│  │    │  eligibility_check → Eligibility Agent (ML model) │    │   │
│  │    │  max_loan_query  → Max Loan Calculator            │    │   │
│  │    │  dti_query       → DTI Calculator                 │    │   │
│  │    │  rejection_reason → RAG Pipeline                  │    │   │
│  │    │  general_question → RAG Pipeline → Gemini QA      │    │   │
│  │    └────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                  RAG PIPELINE                        │   │   │
│  │  │  Query → Gemini Embedding → FAISS Search             │   │   │
│  │  │        → RAG Agent (Gemini) → Answer                 │   │   │
│  │  │        → Validation Agent → Verified Answer          │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────────┐ │
│  │  SQLite DB   │  │  FAISS Index  │  │  PDF Files (uploads/)    │ │
│  │  (documents, │  │  (combined.   │  │  15 policy documents     │ │
│  │   metadata)  │  │  faiss + json)│  │  87 indexed chunks       │ │
│  └──────────────┘  └───────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.13 | Core language |
| **FastAPI** | Latest | REST API framework |
| **Uvicorn** | Latest | ASGI server |
| **Google Gemini** | gemini-flash-latest | NLU, RAG generation, embeddings (gemini-embedding-001) |
| **FAISS** | Latest | Vector similarity search for RAG |
| **scikit-learn** | Latest | ML risk model for loan eligibility |
| **SQLite** | Built-in | Document metadata storage |
| **PyMuPDF (fitz)** | Latest | PDF text extraction |
| **fpdf2** | Latest | PDF generation for seed documents |
| **python-dotenv** | Latest | Environment variable management |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **React** | 18 | UI framework |
| **TypeScript** | Latest | Type-safe frontend |
| **Vite** | 5.4.8 | Build tool and dev server |
| **Framer Motion** | Latest | Animations |
| **Lucide React** | Latest | Icon library |
| **Tailwind CSS** | Latest | Utility CSS framework |

---

## 🤖 Multi-Agent Pipeline

The system uses **6 specialized AI agents**, each with a single responsibility:

### 1. 🧠 NLU Agent (`nlu_agent.py`)
**Role**: Understand what the user is asking and extract key numbers.

- Uses **Google Gemini** to classify intent and extract financial entities from natural language
- Falls back to **regex pattern matching** if Gemini is rate-limited or unavailable
- Detects 6 intents: `emi_calculation`, `eligibility_check`, `max_loan_query`, `dti_query`, `rejection_reason`, `general_question`
- Extracts entities: `monthly_income`, `loan_amount`, `tenure_months`, `interest_rate`, `existing_emi`
- Also handles **general loan knowledge Q&A** with topic-aware fallback answers covering 15 topics

**Example:**
```
User: "I earn ₹60,000 — how much loan can I get?"
→ Intent: max_loan_query
→ Entities: { monthly_income: 60000, loan_amount: null }
```

### 2. ✅ Eligibility Agent (`eligibility_agent.py`)
**Role**: Assess loan eligibility using ML + rule-based logic.

- Runs a **scikit-learn ML model** (trained on synthetic Indian loan data) to predict risk probability
- Applies **rule-based DTI check**: total EMI must be ≤ 50% of income
- Outputs: eligibility score (0–100), decision (approved/conditional/rejected), risk probability, DTI ratio
- **Never uses AI** — fully deterministic and reproducible

### 3. 📚 RAG Agent (`rag_agent.py`)
**Role**: Generate answers from retrieved policy document evidence.

- Receives retrieved document chunks from FAISS vector search
- Sends evidence + user question to **Google Gemini** with a strict prompt
- Only uses evidence from documents — **never invents facts**
- Returns `NOT_IN_EVIDENCE` if no relevant information found
- Cites which evidence block each fact came from
- Handles Gemini API errors gracefully without crashing

### 4. 🔍 Validation Agent (`validation_agent.py`)
**Role**: Independently fact-check the RAG agent's answer.

- Receives: question + proposed answer + original evidence chunks
- Asks Gemini to classify: `SUPPORTED` / `PARTIALLY_SUPPORTED` / `UNSUPPORTED`
- If `PARTIALLY_SUPPORTED`: rewrites the answer removing unsupported claims
- Falls back to `PARTIALLY_SUPPORTED` gracefully if Gemini is unavailable
- Prevents factually wrong answers from reaching the user

### 5. 💡 Credit Improvement Agent (`credit_improvement_agent.py`)
**Role**: Generate personalised credit improvement advice.

- Called when a loan is rejected or conditionally approved
- Analyses the specific weaknesses (low score, high DTI, short employment)
- Generates actionable improvement steps with timeline estimates

### 6. 🤝 Empathy Agent (`empathy_agent.py`)
**Role**: Add emotional context to responses for rejected applicants.

- Wraps negative decisions with empathetic, encouraging language
- Ensures users feel supported rather than just rejected

---

## 📄 RAG Pipeline (Document Q&A)

The RAG (Retrieval-Augmented Generation) pipeline enables the chatbot to answer questions **from your actual uploaded PDF documents**.

### How It Works — Step by Step

```
Step 1: UPLOAD
  Admin uploads a PDF → File saved to uploads/ directory
  → Document record created in SQLite with status "pending"

Step 2: PROCESS (Embed)
  PDF text extracted using PyMuPDF (fitz)
  → Text split into overlapping chunks (~500 tokens each)
  → Each chunk sent to Google Gemini Embedding API (gemini-embedding-001)
  → 3072-dimensional vector created for each chunk
  → Vectors saved to FAISS index (combined.faiss + combined.json)
  → Document status updated to "indexed"

Step 3: QUERY (At chat time)
  User asks a question
  → Question embedded using same Gemini embedding model
  → FAISS performs dot-product similarity search across all 87 chunks
  → Top 5 most similar chunks retrieved (threshold: score ≥ 0.45)
  → RAG Agent sends chunks + question to Gemini text model
  → Gemini generates answer citing evidence block numbers
  → Validation Agent fact-checks the answer
  → Final verified answer returned to user with source citations
```

### Similarity Score Tuning
- Gemini embeddings with FAISS dot-product produce scores in the **0.40–0.65 range** for relevant content
- The threshold is set to **0.45** (was incorrectly 0.70 which filtered all results)
- If no chunks meet the threshold, **best-effort RAG** uses top 3 chunks regardless of score

---

## 📚 Knowledge Base — PDFs Indexed

The system currently has **87 chunks across 15 documents** covering the complete Indian loan ecosystem:

| # | Document | Chunks | Topics Covered |
|---|---|---|---|
| 1 | `personal_loan_complete_guide.pdf` | 7 | Eligibility, rates 10-24%, EMI, documents, rejection |
| 2 | `home_loan_policy_guide.pdf` | 5 | LTV 75-90%, tenure 30yr, tax benefit Sec 24(b), types |
| 3 | `cibil_score_credit_health_guide.pdf` | 5 | Score ranges 300-900, how calculated, how to improve |
| 4 | `car_loan_vehicle_loan_guide.pdf` | 4 | New vs used car, two-wheeler, LTV, rates 7-18% |
| 5 | `business_loan_msme_guide.pdf` | 4 | MUDRA (Shishu/Kishore/Tarun), CGTMSE, MSME eligibility |
| 6 | `education_loan_guide.pdf` | 6 | Moratorium, collateral rules, Vidyalakshmi, Sec 80E |
| 7 | `gold_loan_guide.pdf` | 4 | LTV 75%, no CIBIL needed, auction rules, rates 7-26% |
| 8 | `loan_against_property_guide.pdf` | 4 | LAP LTV 60-70%, tenure 20yr, LAP vs home loan |
| 9 | `loan_faq_common_questions.pdf` | 7 | Min salary, approval time, NRI loans, multiple loans |
| 10 | `rbi_guidelines_borrower_rights.pdf` | 6 | No prepayment penalty, ombudsman, digital lending rules |
| 11 | `balance_transfer_refinancing_guide.pdf` | 6 | Transfer calculation, process, top-up loan |
| 12 | `agriculture_kisan_loan_guide.pdf` | 6 | KCC 4-7% rate, MUDRA, PM-Kisan, crop loan |
| 13 | `loan_terminology_glossary.pdf` | 7 | APR, DTI, EMI, LTV, NPA, MCLR, moratorium definitions |
| 14 | `DEMO_loan_policy.pdf` | 8 | Personal loan base policy rules |
| 15 | `DEMO_financial_guidelines.pdf` | 8 | Financial standards, responsible lending |

---

## 📁 Project Structure

```
AI-LOAN-ADVISORY-CHATBOT/
│
├── README.md                          ← This file
├── .gitignore
│
├── backend/                           ← FastAPI Python backend
│   ├── .env                           ← Environment variables (GEMINI_API_KEY, etc.)
│   ├── requirements.txt               ← Python dependencies
│   ├── generate_pdfs.py               ← Script to generate seed PDF batch 1
│   ├── generate_more_pdfs.py          ← Script to generate seed PDF batch 2
│   ├── upload_seed_pdfs.py            ← Script to upload batch 1 PDFs via API
│   ├── upload_seed2.py                ← Script to upload batch 2 PDFs via API
│   │
│   ├── vector_store/                  ← FAISS index files (auto-created)
│   │   ├── combined.faiss             ← Binary FAISS index
│   │   └── combined.json             ← Chunk metadata (text, doc name, page)
│   │
│   ├── loan_advisor.db                ← SQLite database (auto-created)
│   │
│   └── app/
│       ├── main.py                    ← FastAPI app, all routes, intent router
│       ├── db.py                      ← SQLite connection helper
│       │
│       ├── agents/
│       │   ├── nlu_agent.py           ← Intent detection + entity extraction + general QA
│       │   ├── eligibility_agent.py   ← ML model + DTI rule-based eligibility
│       │   ├── rag_agent.py           ← Evidence-grounded answer generation
│       │   ├── validation_agent.py    ← Fact-checking agent for RAG answers
│       │   ├── credit_improvement_agent.py ← Personalised credit advice
│       │   ├── empathy_agent.py       ← Empathetic response wrapping
│       │   └── orchestrator_agent.py  ← Legacy orchestrator (mostly replaced by main.py routing)
│       │
│       ├── services/
│       │   ├── vector_store.py        ← FAISS index management (load, search, add, persist)
│       │   ├── pdf_processor.py       ← PDF text extraction + chunking
│       │   ├── emi_calculator.py      ← EMI, DTI, max loan calculations
│       │   └── agent_logger.py        ← Logging utility
│       │
│       ├── models/
│       │   └── loan_model.pkl         ← Trained scikit-learn model
│       │
│       ├── ml/
│       │   └── train_model.py         ← Model training script
│       │
│       └── schemas/
│           ├── query.py               ← Pydantic request/response models for chat
│           ├── rag.py                 ← Pydantic models for RAG endpoints
│           └── search.py             ← Pydantic models for search endpoints
│
├── frontend/                          ← React TypeScript frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   │
│   └── src/
│       ├── App.tsx                    ← Root component, routing
│       ├── main.tsx                   ← React entry point
│       ├── types.ts                   ← TypeScript interfaces
│       ├── index.css                  ← Global styles
│       │
│       └── components/
│           ├── ChatInterface.tsx       ← Main chat UI, message send/receive
│           ├── QueryResultCard.tsx    ← Renders different response types (EMI, eligibility, etc.)
│           ├── PolicyQA.tsx           ← Document Q&A interface
│           ├── Dashboard.tsx          ← System stats dashboard
│           ├── DocumentManager.tsx    ← Admin panel for PDF upload/management
│           ├── AdminLogin.tsx         ← Admin authentication screen
│           ├── ImprovementPlan.tsx    ← Credit improvement advice display
│           ├── Message.tsx            ← Individual chat message bubble
│           ├── MessageList.tsx        ← Scrollable list of messages
│           ├── LoadingDots.tsx        ← Typing indicator animation
│           └── ResultCard.tsx         ← Generic result card component
│
├── uploads/                           ← Uploaded PDFs stored here (auto-created)
├── uploads_seed/                      ← Batch 1 generated seed PDFs
└── uploads_seed2/                     ← Batch 2 generated seed PDFs
```

---

## 🔌 API Endpoints

### Chat Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/chat/query` | Main chat endpoint — handles all user questions | None |
| `GET` | `/health` | Health check with Gemini configuration status | None |

**Request body for `/chat/query`:**
```json
{
  "message": "I earn ₹60,000 — how much loan can I get?"
}
```

**Response types:**
- `emi` — EMI calculation result
- `eligibility` — Loan eligibility result with score and decision
- `max_loan` — Maximum borrowable amount
- `dti` — DTI ratio calculation
- `policy` — RAG-sourced policy answer with citations
- `general` — General loan knowledge answer
- `missing_info` — Request for more information
- `error` — Error message

---

### Document Management (Admin)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/admin/documents/upload` | Upload a PDF file | ✅ Admin key |
| `POST` | `/admin/documents/{id}/process` | Embed PDF into vector store | ✅ Admin key |
| `GET` | `/admin/documents` | List all documents | ✅ Admin key |
| `DELETE` | `/admin/documents/{id}` | Delete document + its vectors | ✅ Admin key |

---

### Search & Stats Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/search/stats` | Vector store stats (chunks, documents, index) | None |
| `GET` | `/api/dashboard/stats` | Dashboard statistics | None |
| `POST` | `/rag/ask` | Direct RAG query endpoint | None |

---

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.11 or 3.13
- Node.js 18+
- A **Google Gemini API key** (free at [aistudio.google.com](https://aistudio.google.com))

---

### Backend Setup

```bash
# 1. Navigate to the backend directory
cd AI-LOAN-ADVISORY-CHATBOT/backend

# 2. Create a Python virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create the .env file
touch .env
```

Add the following to your `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
ADMIN_SECRET_KEY=tata-mitra-admin-2024
DATABASE_URL=sqlite:///./loan_advisor.db
```

---

### Frontend Setup

```bash
# Navigate to the frontend directory
cd AI-LOAN-ADVISORY-CHATBOT/frontend

# Install Node dependencies
npm install
```

---

## 🚀 Running the Project

### Start Backend (Terminal 1)

```bash
cd AI-LOAN-ADVISORY-CHATBOT/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Application startup complete.
VectorStore: loaded 87 chunks (87 vectors) from disk.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Start Frontend (Terminal 2)

```bash
cd AI-LOAN-ADVISORY-CHATBOT/frontend
npm run dev
```

You should see:
```
VITE v5.4.8  ready in 202 ms
➜  Local:   http://localhost:5173/
```

### Open the App

Open your browser and go to: **http://localhost:5173**

---

## 📤 Adding New PDF Documents

### Method 1: Via Admin Panel (UI)
1. Open the app at http://localhost:5173
2. Click **Admin** in the navigation
3. Enter the admin password: `tata-mitra-admin-2024`
4. Click **Upload Document** and select your PDF
5. After upload, click **Process** to embed the document into the vector store
6. The document is now available for Q&A immediately

### Method 2: Via Script (Batch Upload)
```bash
# First generate seed PDFs (if not already done)
cd backend
source venv/bin/activate
python generate_pdfs.py        # Creates 5 PDFs in uploads_seed/
python generate_more_pdfs.py   # Creates 8 more PDFs in uploads_seed2/

# Then upload and process all PDFs automatically
# (backend must be running first)
python upload_seed_pdfs.py     # Uploads batch 1
python upload_seed2.py         # Uploads batch 2
```

### Method 3: Via API (curl)
```bash
# Upload a PDF
curl -X POST http://localhost:8000/admin/documents/upload \
  -H "X-Admin-Key: tata-mitra-admin-2024" \
  -F "file=@your_document.pdf"

# Process the uploaded document (use the doc_id from upload response)
curl -X POST http://localhost:8000/admin/documents/{doc_id}/process \
  -H "X-Admin-Key: tata-mitra-admin-2024"
```

---

## 🔐 Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for NLU, RAG, and embeddings | None |
| `ADMIN_SECRET_KEY` | ✅ Yes | API key for admin endpoints (document management) | None |
| `DATABASE_URL` | Optional | SQLite database path | `sqlite:///./loan_advisor.db` |

> **Note on Gemini Free Tier**: The free tier allows **20 text generation requests/day** and **1500 embedding requests/day**. Embedding requests (for PDF processing) and text generation (for chat responses) use separate quotas. The system degrades gracefully when quota is exceeded using regex-based intent detection and static fallback answers.

---

## 💬 How Each Question Type is Handled

### 1. "Calculate my EMI for ₹5 lakh loan at 12% for 3 years"
```
NLU → intent: emi_calculation
     → loan_amount: 500000, rate: 12.0, tenure: 36 months
→ EMI Calculator (pure math, no AI)
→ Result: EMI = ₹16,607.15, Total Interest = ₹97,857, Total = ₹597,857
```

### 2. "I earn ₹60,000 — how much loan can I get?"
```
NLU → intent: max_loan_query
     → monthly_income: 60000, loan_amount: null
→ Max Loan Calculator
→ Available EMI = 40% of income = ₹24,000/month
→ Max loan at 10% for 60 months = ₹11,29,569
```

### 3. "Can I get a ₹5 lakh loan on ₹40,000 salary?"
```
NLU → intent: eligibility_check
     → monthly_income: 40000, loan_amount: 500000
→ Eligibility Agent (ML model)
→ Score: 78/100, Decision: APPROVED, DTI: 22%, Risk: 12%
```

### 4. "What credit score is required for a personal loan?"
```
NLU → intent: general_question
→ RAG Pipeline:
   - Embed question → FAISS search → top 5 chunks from CIBIL guide + loan policy
   - RAG Agent: "A minimum CIBIL score of 650 is required... (Evidence 2)"
   - Validation: SUPPORTED
→ Returns: verified answer with source citation
```

### 5. "What is a gold loan?"
```
NLU → intent: general_question
→ RAG Pipeline → gold_loan_guide.pdf chunks retrieved
→ Answer: "A gold loan is a secured loan where you pledge gold jewellery...
           LTV up to 75%, rates 7-13% at banks..."
```

### 6. (When Gemini quota exhausted)
```
NLU → regex fallback detects intent from keywords
→ answer_general_question → Gemini fails → topic-aware static fallback
→ "Gold loan: secured loan, pledge jewellery, 75% LTV, 7-13% rate, no CIBIL needed..."
```

---

## 🎨 Frontend Pages and Components

### Chat Interface (`/`)
- Main chat UI with gradient purple background
- Sends messages to `/chat/query` API
- Renders different card types based on response `type`:
  - **EMI Card**: Shows monthly EMI, total interest, total repayment
  - **Eligibility Card**: Score gauge, APPROVED/CONDITIONAL/REJECTED badge, DTI, Risk
  - **Max Loan Card**: Maximum borrowable amount with EMI capacity
  - **Policy Card**: Text answer with source document citations
  - **General Card**: Plain text answer
  - **Missing Info Card**: Prompt for more details

### Dashboard (`/dashboard`)
- Live system statistics
- Total documents, total chunks, index status
- API health indicator

### Admin Panel (`/admin`)
- Password-protected admin interface
- Upload new PDF documents (drag & drop or file picker)
- Process documents (embed into vector store)
- View all indexed documents with chunk counts
- Delete documents (removes from vector store + database)

### Policy Q&A (`/policy`)
- Dedicated interface for document-specific questions
- Shows source citations prominently

---

## 🤖 ML Model — Risk Assessment

The eligibility agent uses a **scikit-learn RandomForestClassifier** (or LogisticRegression) trained on synthetic Indian loan data.

### Training Features
- Monthly income
- Loan amount requested
- Loan tenure
- Existing EMI obligations
- DTI ratio (computed)
- Loan-to-income ratio (computed)

### Training Labels
- `1` = approved (low risk)
- `0` = rejected (high risk)

### Training Script
```bash
cd backend
source venv/bin/activate
python app/ml/train_model.py
# Saves model to app/models/loan_model.pkl
```

### Eligibility Score Formula
```
Score = (100 - risk_probability * 100) * DTI_adjustment * income_adjustment
```
- DTI < 30%: +bonus points
- DTI 30-50%: standard scoring
- DTI > 50%: penalised → often REJECTED

---

## ⚠️ Known Limitations

| Limitation | Impact | Workaround |
|---|---|---|
| Gemini Free Tier: 20 requests/day (text gen) | Chat answers via Gemini limited | Regex fallback + static answers cover most cases |
| Gemini Free Tier: 1500 requests/day (embeddings) | PDF processing limited to ~150 PDFs/day | No practical issue for this project scale |
| No authentication for chat endpoint | Any user can query | Add JWT auth if deploying to production |
| SQLite instead of PostgreSQL | Not suitable for high concurrency | Switch `DATABASE_URL` to PostgreSQL for production |
| PDF text extraction quality | Scanned PDFs (image-only) won't extract well | Use OCR (Tesseract) for scanned documents |
| FAISS not distributed | Single-node only | Switch to Pinecone/Weaviate for multi-node |
| No conversation memory | Each message is independent | Add session-based conversation history |

---

## 📊 Sample API Responses

### EMI Calculation Response
```json
{
  "type": "emi",
  "message": "For a ₹5,00,000 loan at 12.0% p.a. over 36 months: Monthly EMI = ₹16,607.15, Total Interest = ₹97,857.47, Total Repayment = ₹5,97,857.47.",
  "data": {
    "monthly_emi": 16607.15,
    "total_interest": 97857.47,
    "total_repayment": 597857.47,
    "principal": 500000,
    "annual_rate": 12.0,
    "tenure_months": 36
  }
}
```

### Eligibility Response
```json
{
  "type": "eligibility",
  "message": "✅ Your loan is APPROVED — Eligibility Score: 82/100, DTI Ratio: 22%, Risk: 14%.",
  "data": {
    "decision": "approved",
    "eligibility_score": 82,
    "risk_probability": 0.14,
    "dti_ratio": 0.22,
    "reason": null
  }
}
```

### Policy Q&A Response
```json
{
  "type": "policy",
  "message": "A minimum CIBIL score of 650 is required for personal loans (Evidence 1). Scores above 750 attract the best interest rates starting from 10.5% p.a. (Evidence 2).",
  "data": {
    "answer": "A minimum CIBIL score of 650...",
    "sources": [
      {
        "document_name": "cibil_score_credit_health_guide.pdf",
        "page_number": 1,
        "relevance_score": 0.587
      }
    ],
    "support_level": "SUPPORTED",
    "is_verified": true
  }
}
```

---

## 👨‍💻 Development Notes

### Adding a New Intent
1. Add the intent name and examples to `_INTENT_PROMPT` in `nlu_agent.py`
2. Add keyword patterns to `_regex_fallback()` in `nlu_agent.py`
3. Add a handler block in `main.py` (follow the pattern of existing intents)
4. Add a response card component in `QueryResultCard.tsx` if needed

### Adding New Topic Fallback Answers
In `nlu_agent.py`, find `answer_general_question()` and add a new `elif` block in the fallback section:
```python
elif any(w in m for w in ["your", "topic", "keywords"]):
    return "Your informative answer here..."
```

### Re-indexing All Documents
If you need to rebuild the vector store from scratch:
```bash
rm backend/vector_store/combined.faiss
rm backend/vector_store/combined.json
# Restart backend — it will start with empty index
# Then re-process all documents via admin panel or upload scripts
```

---

## 🏃 Quick Start Command Reference

```bash
# Backend
cd AI-LOAN-ADVISORY-CHATBOT/backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

# Frontend
cd AI-LOAN-ADVISORY-CHATBOT/frontend && npm run dev

# Generate + upload all seed PDFs (backend must be running)
cd AI-LOAN-ADVISORY-CHATBOT/backend && source venv/bin/activate
python generate_pdfs.py && python generate_more_pdfs.py
python upload_seed_pdfs.py && python upload_seed2.py

# Check index status
curl http://localhost:8000/search/stats

# Test a query
curl -X POST http://localhost:8000/chat/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the minimum CIBIL score for a personal loan?"}'
```

---

## 📝 License

This project is built for educational and demonstration purposes as part of the Celebal Technologies internship program.

---
#   A I _ L O A N _ A D V I S O R Y  
 