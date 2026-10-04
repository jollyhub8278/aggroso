# Expense Claim Policy Review Assistant

A full-stack internal review tool that combines deterministic expense validation with AI-assisted policy interpretation.

The application helps reviewers evaluate employee expense claims, identify policy issues, retrieve relevant policy evidence, and record reviewer decisions.

## Live Demo

**Frontend:**  
https://frontend-njk5.vercel.app

**Backend API:**  
https://aggroso-api.onrender.com

**API Documentation:**  
https://aggroso-api.onrender.com/docs

**GitHub Repository:**  
https://github.com/jollyhub8278/aggroso

---

## Overview

The Expense Claim Policy Review Assistant is designed to support an internal expense-review workflow.

A submitted expense claim is evaluated through two complementary layers:

1. **Deterministic validation**
   - Required fields
   - Amount validation
   - Future-date validation
   - Missing receipt detection
   - Duplicate claim detection
   - Category spending limits

2. **AI-assisted policy review**
   - Expense category classification
   - Relevant policy retrieval
   - Compliance interpretation
   - Missing information detection
   - Policy evidence
   - Confidence and uncertainty handling

The reviewer can then approve, reject, request clarification, or override the AI classification with a reason.

---

## Features

### Expense Claim Management

- Create new expense claims
- View all submitted claims
- View individual claim details
- Track claim amounts and currencies
- Track receipt availability
- View claim review status

### Policy Review

- Classify ambiguous expense descriptions
- Retrieve relevant policy sections
- Explain potential policy issues
- Highlight missing information
- Provide policy evidence
- Show classification confidence
- Clearly mark uncertain classifications

### Deterministic Validation

The system performs rule-based validation for:

- Required claimant
- Required category
- Required description
- Positive claim amount
- Future claim dates
- Missing receipts
- Duplicate claims
- Category spending limits

### Reviewer Actions

Reviewers can:

- Approve a claim
- Reject a claim
- Request clarification
- Override the AI classification
- Provide a reason for an override
- View review decision history

### Dashboard

The frontend dashboard provides:

- Total claims
- Total claim amount
- Pending review
- Approved claims
- Claims needing attention
- Rejected claims
- Claim list with category, amount, receipt and AI status

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite

### AI

- OpenAI API (optional)
- Local keyword-based classification fallback

### Testing

- Pytest
- FastAPI TestClient

### Deployment

- Vercel — Frontend
- Render — Backend

---

## Project Structure

```text
aggroso/
│
├── backend/
│   │
│   ├── app/
│   │   ├── routes/
│   │   │   ├── claims.py
│   │   │   └── reviews.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_review.py
│   │   │   ├── policy.py
│   │   │   └── validation.py
│   │   │
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   │
│   ├── tests/
│   │   └── test_claims.py
│   │
│   ├── seed.py
│   ├── requirements.txt
│   ├── runtime.txt
│   └── .env.example
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── styles.css
│   │
│   ├── package.json
│   └── ...
│
├── .gitignore
└── README.md
