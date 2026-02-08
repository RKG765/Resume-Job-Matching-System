# Resume-Job Matching System

An AI-powered resume matching system using **Sentence-BERT embeddings** and **skill analysis** to intelligently rank candidates against job descriptions.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **BERT Embeddings** | 384-dimensional semantic vectors that understand context |
| **Hybrid Scoring** | Combines BERT similarity (40%) + skill match (60%) |
| **Skill Extraction** | 400+ technical skills with synonym resolution |
| **Radial Gauge** | Animated score visualization with color coding |
| **LLM Explanations** | AI-generated match analysis (LM Studio) |
| **Live Pipeline** | Real-time visualization of processing steps |

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

## 🎨 UI Theme: Ceramic Light

- **Background**: Warm off-white (`#faf9f7`)
- **Cards**: White with subtle shadows
- **Accent**: Violet (`#7c3aed`)
- **Font**: Inter

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/manual-match` | POST | Match resumes to job |
| `/api/extract-skills` | POST | Extract skills from text |
| `/api/upload-file` | POST | Parse PDF/TXT file |
| `/api/llm/status` | GET | LLM service status |

## 📊 How Scoring Works

```
Final Score = (BERT Semantic × 0.4) + (Skill Match × 0.6)

Classification:
  ≥70% → Strong Fit (Green)
  ≥40% → Partial Fit (Yellow)
  <40% → Needs Work (Red)
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, Framer Motion |
| Backend | FastAPI, Python 3.10+ |
| Database | PostgreSQL + pgvector |
| Embeddings | Sentence-BERT (all-MiniLM-L6-v2) |
| LLM | LM Studio (DeepSeek-R1) |

## 📝 Environment Variables

Create `.env` in `backend/`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/resume_matcher
USE_SQLITE=true  # For local dev without Postgres
LLM_API_URL=http://localhost:1234/v1
LLM_MODEL=deepseek-r1
```

## 📚 Documentation

- [Presentation](present.md)
- [LLM Setup Guide](docs/llm_setup.md)

---
