import os
from datetime import datetime
from hmac import compare_digest
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app.workflow import (
    MarketingDraft, Status, approve, edit, publish_guard, reject,
    request_approval, schedule,
)

app = FastAPI(title="Menniyam Digital Marketing Agent", version="0.2.0")
_drafts: dict[str, MarketingDraft] = {}  # Local development only. Never use for production.


def require_admin(x_agent_admin_key: str | None = Header(default=None)) -> str:
    """MVP-only authentication. Replace with OIDC sessions and RBAC in production."""
    expected = os.environ.get("AGENT_ADMIN_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin authentication not configured")
    if not x_agent_admin_key or not compare_digest(x_agent_admin_key, expected):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return "mvp-admin"


class DraftInput(BaseModel):
    platform: str = Field(pattern="^(linkedin|instagram)$")
    account_id: str = Field(min_length=1)
    caption: str = Field(min_length=1, max_length=3000)
    media_url: str | None = None


class DraftEdit(BaseModel):
    caption: str = Field(min_length=1, max_length=3000)
    media_url: str | None = None


class ScheduleInput(BaseModel):
    scheduled_for: datetime


def get_draft(draft_id: str) -> MarketingDraft:
    draft = _drafts.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft


def apply(action):
    try:
        action()
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc


def summary(draft_id: str, draft: MarketingDraft) -> dict:
    return {
        "id": draft_id,
        "platform": draft.platform,
        "account_id": draft.account_id,
        "caption": draft.caption,
        "media_url": draft.media_url,
        "status": draft.status.value,
        "approved_by": draft.approver_user_id,
        "approved_at": draft.approved_at,
        "scheduled_for": draft.scheduled_for,
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "menniyam-marketing-agent", "publishing_enabled": False}


@app.get("/drafts")
def list_drafts(_user: str = Depends(require_admin)):
    return [summary(draft_id, draft) for draft_id, draft in _drafts.items()]


@app.post("/drafts", status_code=201)
def create_draft(payload: DraftInput, _user: str = Depends(require_admin)):
    draft_id = str(uuid4())
    draft = MarketingDraft(**payload.model_dump())
    _drafts[draft_id] = draft
    return summary(draft_id, draft)


@app.patch("/drafts/{draft_id}")
def edit_draft(draft_id: str, payload: DraftEdit, _user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: edit(draft, payload.caption, payload.media_url))
    return summary(draft_id, draft)


@app.post("/drafts/{draft_id}/request-approval")
def submit_for_approval(draft_id: str, _user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: request_approval(draft))
    return summary(draft_id, draft)


@app.post("/drafts/{draft_id}/approve")
def approve_draft(draft_id: str, user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: approve(draft, user_id=user))
    return summary(draft_id, draft)


@app.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: str, _user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: reject(draft))
    return summary(draft_id, draft)


@app.post("/drafts/{draft_id}/schedule")
def schedule_draft(draft_id: str, payload: ScheduleInput, _user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: schedule(draft, payload.scheduled_for))
    return summary(draft_id, draft)


@app.post("/drafts/{draft_id}/publish")
def publish_draft(draft_id: str, _user: str = Depends(require_admin)):
    draft = get_draft(draft_id)
    apply(lambda: publish_guard(draft))
    return summary(draft_id, draft)
