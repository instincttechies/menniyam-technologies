from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


@dataclass
class MarketingDraft:
    platform: str
    account_id: str
    caption: str
    status: Status = Status.DRAFT
    approver_user_id: str | None = None


def approve(draft: MarketingDraft, user_id: str) -> MarketingDraft:
    draft.status = Status.APPROVED
    draft.approver_user_id = user_id
    return draft


def publish_guard(draft: MarketingDraft):
    if draft.status != Status.APPROVED:
        raise PermissionError("Draft requires authorized user approval before publishing")
    # TODO: integrate official LinkedIn or Meta APIs after OAuth/app review.
    raise NotImplementedError("Platform API publisher is not yet configured")
