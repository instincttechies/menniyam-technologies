from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256


class Status(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


def fingerprint(platform: str, account_id: str, caption: str, media_url: str | None) -> str:
    value = "\\x00".join((platform, account_id, caption, media_url or ""))
    return sha256(value.encode("utf-8")).hexdigest()


@dataclass
class MarketingDraft:
    platform: str
    account_id: str
    caption: str
    media_url: str | None = None
    status: Status = Status.DRAFT
    approver_user_id: str | None = None
    approved_fingerprint: str | None = None
    approved_at: datetime | None = None
    scheduled_for: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def content_fingerprint(self) -> str:
        return fingerprint(self.platform, self.account_id, self.caption, self.media_url)


def request_approval(draft: MarketingDraft) -> None:
    if draft.status not in (Status.DRAFT, Status.REJECTED):
        raise ValueError("Only drafts or rejected posts can be submitted for approval")
    draft.status = Status.PENDING_APPROVAL


def approve(draft: MarketingDraft, user_id: str) -> None:
    if draft.status != Status.PENDING_APPROVAL:
        raise ValueError("Post must be pending approval")
    draft.approver_user_id = user_id
    draft.approved_fingerprint = draft.content_fingerprint()
    draft.approved_at = datetime.now(timezone.utc)
    draft.status = Status.APPROVED


def reject(draft: MarketingDraft) -> None:
    if draft.status != Status.PENDING_APPROVAL:
        raise ValueError("Post must be pending approval")
    draft.status = Status.REJECTED
    draft.approver_user_id = None
    draft.approved_fingerprint = None
    draft.approved_at = None


def edit(draft: MarketingDraft, caption: str, media_url: str | None) -> None:
    if draft.status == Status.PUBLISHED:
        raise ValueError("Published posts cannot be edited")
    draft.caption = caption
    draft.media_url = media_url
    draft.status = Status.DRAFT
    draft.approver_user_id = None
    draft.approved_fingerprint = None
    draft.approved_at = None
    draft.scheduled_for = None


def approval_guard(draft: MarketingDraft) -> None:
    if draft.status not in (Status.APPROVED, Status.SCHEDULED):
        raise PermissionError("Explicit approval required before scheduling or publishing")
    if not draft.approver_user_id or draft.approved_fingerprint != draft.content_fingerprint():
        raise PermissionError("Content has changed since approval; submit for approval again")


def schedule(draft: MarketingDraft, when: datetime) -> None:
    approval_guard(draft)
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("Schedule must include a timezone")
    if when.astimezone(timezone.utc) <= datetime.now(timezone.utc):
        raise ValueError("Schedule must be in the future")
    draft.scheduled_for = when.astimezone(timezone.utc)
    draft.status = Status.SCHEDULED


def publish_guard(draft: MarketingDraft) -> None:
    approval_guard(draft)
    # No live publishing until OAuth, verified account ownership, persistent storage,
    # platform permissions and an idempotent publisher are configured and tested.
    raise NotImplementedError("Social publishing is disabled until provider integration is configured")
