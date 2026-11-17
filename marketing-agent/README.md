# Menniyam Marketing Agent (approval-first MVP)

**Targets:** LinkedIn company page + Instagram Professional account. **Cadence:** 2 posts/day/platform. **Publishing:** explicit per-post owner approval only.

This is a developer scaffold, **not a production deployment**. No social accounts are connected and no real platform publishing is enabled. Read [OAuth and approval architecture](./OAUTH_APPROVAL_ARCHITECTURE.md).

## Local run
```bash
cd marketing-agent
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Set AGENT_ADMIN_KEY in your environment to a strong, random value.
uvicorn app.main:app --reload
```

Use `X-Agent-Admin-Key` for draft API operations in this local MVP. Do not use a shared API key as production authentication.

## API flow
1. `POST /drafts` creates a draft.
2. `POST /drafts/{id}/request-approval` submits it for approval.
3. `POST /drafts/{id}/approve` records explicit approval; `/reject` rejects.
4. `POST /drafts/{id}/schedule` records an approved proposed time (no worker).
5. `POST /drafts/{id}/publish` is intentionally disabled and returns HTTP 501 after approval checks.
6. `PATCH /drafts/{id}` resets approval whenever content changes.
7. `GET /drafts` lists the in-memory draft queue.

## Tests
```bash
pytest -q
```

## Production blockers
Implement authenticated OIDC/RBAC users, durable PostgreSQL storage, OAuth state and callback exchange, verified provider account ownership, encrypted token vault, provider API publishers, audit logs, reliable job queue, AI caption/banner generation and approval UI. No secrets in git.
