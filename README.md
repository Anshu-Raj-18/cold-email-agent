# ColdMailer — AI-Powered National Professor Research Matching & RAG Outreach System

An end-to-end, modular Python application that automates academic cold outreach targeting premier faculty across **IIT, IIIT, IISc, NIT, IISER, ISB, and IIM** institutes using Retrieval-Augmented Generation (RAG) powered by **Google Gemini 2.5 Flash**, **ChromaDB**, **ReportLab PDF**, and the **Gmail API**.

Candidate Profile Grounded: **Anshu Raj** (`qismcdeltat@gmail.com` | B.Tech ECE, Heritage Institute of Technology | CGPA: 8.8)

---

## 🏛️ Key Features

- **1,584+ Faculty Excel & Web Catalog Integration:** Auto-ingests all 1,583 IIT/IIIT/NIT professors from `1584 Professors IIT (1).xlsx` and web scrapers into a structured `data/professors.csv` database.
- **Academic Publication Research Fetcher:** Retrieves professor papers & abstracts dynamically via Semantic Scholar and OpenAlex APIs (`src/academic_fetcher.py`).
- **Semantic Overlap & Multi-Factor Scoring (0–100%):** Evaluates research overlap (40%), technical skills (25%), project & dissertation alignment (20%), deep paper synergy (10%), and academic background compatibility (5%).
- **RAG & Factually Grounded Email Generation:** Uses Gemini 2.5 Embeddings (`models/text-embedding-004`) and `gemini-2.5-flash` (low temperature 0.1) to draft concise, highly personalized outreach emails (< 120 words, devoid of sycophantic flattery).
- **Automated ReportLab Cover Letter PDFs:** Auto-generates customized `Cover_Letter_Prof_<Name>.pdf` files matching institutional layout standards.
- **Batch Processing & Human-in-the-Loop Review:** Process 5–10 emails at a time with interactive console confirmation (`[y/d/N]`) before sending.
- **FastAPI Review Dashboard & REST API:** Built-in web dashboard at `http://localhost:8000/dashboard` for visual review, editing, and single-click approval.
- **Data Persistence & CSV Exports:** Automatically syncs `data/agent.db`, `data/professors.csv`, and `data/applications.csv`.

---

## 📁 Project Architecture

```text
ColdMailer/
│
├── .env.example              # Environment variables template
├── .env                      # Local configuration file
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation
├── 1584 Professors IIT (1).xlsx # Master IIT professor Excel catalog
├── n8n_workflow.json         # Ready-to-import n8n automation workflow
│
├── profile/
│   ├── RESUME.pdf            # Original candidate resume PDF
│   ├── RESUME_tcs.odt        # Candidate resume source
│   └── resume_summary.txt   # Ingestible candidate background text
│
├── data/
│   ├── candidate_profile.json # Master JSON profile for Anshu Raj
│   ├── professors.csv        # Auto-generated CSV database of 1,583+ professors
│   ├── applications.csv      # Auto-generated application dispatch tracker
│   └── agent.db              # Persistent SQLite database
│
├── assets/
│   └── Anshu_Raj_Resume.pdf  # Master candidate resume PDF for email attachments
│
├── generated_cover_letters/  # Auto-generated Cover_Letter_Prof_<Name>.pdf files
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Environment config & path management
│   ├── academic_fetcher.py   # Semantic Scholar & OpenAlex API paper query engine
│   ├── scraper.py            # National Faculty scraper & Excel loader
│   ├── matching_engine.py    # Multi-factor candidate-professor match scorer (0-100%)
│   ├── research_analyzer.py  # Deep paper synergy analyzer
│   ├── rag_engine.py         # ChromaDB vector store & Gemini 2.5 RAG chain
│   ├── email_generator.py    # Plain-text email & cover letter payload generator
│   ├── pdf_generator.py      # ReportLab Cover Letter PDF builder
│   ├── email_service.py      # Gmail API OAuth2 dispatcher & draft creator
│   ├── database.py           # SQLite database manager & CSV exporter
│   ├── followup_engine.py    # Automated polite follow-up email generator
│   ├── reply_detector.py     # IMAP inbox reply scanner & status tracker
│   ├── ollama_client.py      # Local Ollama LLM client fallback
│   └── api_server.py         # FastAPI REST backend & Visual Review Dashboard
│
├── main.py                   # Master CLI Orchestrator (Batch mode 5-10 emails)
├── run_server.py             # FastAPI Web Dashboard Server launcher
└── test_pipeline.py          # Automated integration test suite
```

---

## 🚀 Quick Setup & Usage

### 1. Activate Environment & Install Dependencies
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`
Set your Gemini API key in `.env`:
```ini
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=models/text-embedding-004

SENDER_NAME=Anshu Raj
SENDER_EMAIL=qismcdeltat@gmail.com
```

### 3. Run Automated Integration Test Suite
```powershell
python test_pipeline.py
```

### 4. Run CLI Batch Pipeline (5–10 Emails at a time)
```powershell
# Run batch outreach for 5 professors matching your domain
python main.py --domain "Machine Learning Computer Vision Speech AI" --batch-size 5

# Test RAG pipeline without Gmail API sending (Dry Run)
python main.py --tier "IIT" --batch-size 5 --dry-run
```

### 5. Launch Visual Review Dashboard (FastAPI)
```powershell
python run_server.py
```
- **Visual Review Dashboard:** [`http://localhost:8000/dashboard`](http://localhost:8000/dashboard)
- **Interactive API Documentation:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
