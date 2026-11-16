# Menniyam Marketing Agent MVP

FastAPI starter scaffold for a company-owned social marketing agent.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Health endpoint: `GET /health`.

## Current status
Starter scaffold only. It is not production-ready and does not yet publish to social networks. LinkedIn and Meta/Instagram app setup, approved permissions, OAuth state validation/token exchange, authenticated users, encrypted persistent token storage, audit logs, and real API publishing must be implemented and tested. Draft publishing is guarded by explicit approval. Never commit credentials or send them in chat.

## Structure
- `app/main.py`: FastAPI health and draft endpoints
- `app/workflow.py`: draft lifecycle and approval guard
- `app/oauth_notes.md`: provider setup checklist
- `.env.example`: environment variable template
