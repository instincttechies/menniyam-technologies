from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from app.workflow import MarketingDraft, Status, approve, publish_guard

app = FastAPI(title=\"Menniyam Digital Marketing Agent\", version=\"0.1.0\")
_drafts: dict[str, MarketingDraft] = {}  # in-memory MVP only; replace with tenant-scoped database

class DraftInput(BaseModel):
    platform: str = Field(pattern=\"^(linkedin|instagram)$\")
    account_id: str = Field(min_length=1)
    caption: str = Field(min_length=1, max_length=3000)

@app.get(\"/health\")
def health():
    return {\"status\": \"ok\", \"service\": \"menniyam-marketing-agent\"}

@app.post(\"/drafts\")
def create_draft(payload: DraftInput):
    draft_id = str(uuid4())
    _drafts[draft_id] = MarketingDraft(platform=payload.platform, account_id=payload.account_id, caption=payload.caption)
    return {\"id\": draft_id, \"status\": Status.DRAFT.value, \"platform\": payload.platform}

@app.post(\"/drafts/{draft_id}/approve\")
def approve_draft(draft_id: str):
    draft = _drafts.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail=\"Draft not found\")
    # TODO: replace with authenticated approver identity and role checks before production.
    approve(draft, user_id=\"local-mvp-approver\")
    return {\"id\": draft_id, \"status\": draft.status.value}

@app.post(\"/drafts/{draft_id}/publish\")
def publish_draft(draft_id: str):
    draft = _drafts.get(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail=\"Draft not found\")
    try:
        publish_guard(draft)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except NotImplementedError as exc:
        raise HTTPException(status_code=501, detail=str(exc))
