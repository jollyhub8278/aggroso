# Expense Claim Policy Review Assistant

A full-stack expense claim review tool that combines deterministic validation with AI-assisted policy interpretation.

## Live Demo

- **Frontend:** https://frontend-njk5.vercel.app
- **Backend API:** https://aggroso-api.onrender.com
- **API Docs:** https://aggroso-api.onrender.com/docs

## Features

- Create and review expense claims
- AI-assisted expense category classification
- Policy retrieval and evidence
- Compliance and clarification checks
- Missing receipt and duplicate claim detection
- Spending-limit and date validation
- Approve, reject, or request clarification
- Override AI classification with a reason
- Review decision history
- Dashboard with claim and review statistics
- Local fallback when OpenAI API is unavailable

## Tech Stack

- **Frontend:** React, Vite, JavaScript, CSS
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** SQLite
- **AI:** OpenAI API + local fallback
- **Testing:** Pytest
- **Deployment:** Vercel + Render

## Project Structure

```text
aggroso/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   └── services/
│   ├── tests/
│   ├── seed.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   └── package.json
└── README.md
```

## Run Locally

### Backend

```bash
cd backend

python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Seed demo data:

```bash
python seed.py
```

Start the server:

```bash
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

### Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Optional OpenAI Configuration

The application works without an OpenAI API key.

To enable OpenAI-powered classification/review, create `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
```

Without an API key, the application uses a lightweight local keyword-based classifier.

## Demo Claims

The seed script creates three example claims:

- **Business Meals:** INR 12,500 — exceeds category limit
- **Transportation:** INR 850 — missing receipt
- **Travel:** INR 4,200 — compliant

## API Endpoints

```text
GET  /claims
GET  /claims/{claim_id}
POST /claims
POST /reviews/{claim_id}
```

Supported review actions:

```text
approve
reject
clarification
override
```

## Testing

Run:

```bash
cd backend
python -m pytest -v
```

The test suite contains **21 tests** covering claim validation, duplicate detection, policy retrieval, AI review fields, reviewer actions, and review history.

## Scope

This project focuses on expense claim review and does not include:

- Reimbursements
- Payroll
- Payment processing
- Tax calculations
- Receipt OCR
- Accounting integrations
