# Expense Claim Policy Review Assistant

A small internal review tool that combines deterministic expense validation with AI-assisted policy interpretation.

## Features

- Review employee expense claims
- Classify ambiguous descriptions into policy categories
- Retrieve relevant policy sections
- Explain potential compliance issues
- Highlight missing information
- Cite configured policy evidence
- Detect duplicate claims
- Check receipts, dates, required fields and category limits
- Approve, reject or request clarification
- Override AI classification with a reason through the review API
- View reviewer decision history
- Works without an OpenAI API key using a simple local classification fallback

## Tech stack

- React + Vite
- FastAPI
- SQLAlchemy
- SQLite by default
- OpenAI API (optional)

## Run locally

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env # macOS/Linux

python seed.py
uvicorn app.main:app --reload
```

Backend: http://localhost:8000
API docs: http://localhost:8000/docs

If you want model-based review, put your OpenAI API key in `backend/.env`:

```env
OPENAI_API_KEY=your_key_here
```

Without it, the app uses a small local keyword classifier so the project remains runnable.

### 2. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Example claims

The seed script creates a few claims covering:

- Business meal over the configured limit
- Transportation claim with a missing receipt
- Normal travel claim

## API overview

`GET /claims` - list claims

`GET /claims/{id}` - claim details, validation results and review history

`POST /claims` - create and automatically review a claim

`POST /reviews/{claim_id}` - save a reviewer action

Review actions:

- `approve`
- `reject`
- `clarification`
- `override` (requires a reason)

## Design decision

The system deliberately separates deterministic checks from AI reasoning.

Rules such as duplicate detection, receipt checks and configured spending limits are handled in code. AI is used for ambiguous classification and policy interpretation. This makes the result easier to audit and explain.

## Scope

This project does not process reimbursements, payroll, payments, tax advice, receipt OCR or external accounting integrations.
