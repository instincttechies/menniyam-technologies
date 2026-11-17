import pytest

from app.workflow import (
    MarketingDraft, Status, approve, edit, publish_guard, reject,
    request_approval, schedule,
)


def make_draft():
    return MarketingDraft(platform="linkedin", account_id="company-test", caption="Python training")


def test_requires_submission_before_approval():
    draft = make_draft()
    with pytest.raises(ValueError):
        approve(draft, "owner")


def test_rejected_post_cannot_publish():
    draft = make_draft()
    request_approval(draft)
    reject(draft)
    with pytest.raises(PermissionError):
        publish_guard(draft)


def test_approved_post_still_cannot_publish_without_provider():
    draft = make_draft()
    request_approval(draft)
    approve(draft, "owner")
    with pytest.raises(NotImplementedError):
        publish_guard(draft)


def test_edit_revokes_approval():
    draft = make_draft()
    request_approval(draft)
    approve(draft, "owner")
    edit(draft, "New content", None)
    assert draft.status == Status.DRAFT
    assert draft.approver_user_id is None
    with pytest.raises(PermissionError):
        publish_guard(draft)


def test_mutation_after_approval_is_detected():
    draft = make_draft()
    request_approval(draft)
    approve(draft, "owner")
    draft.caption = "Tampered"
    with pytest.raises(PermissionError):
        publish_guard(draft)


def test_scheduling_requires_approval():
    from datetime import datetime, timedelta, timezone
    draft = make_draft()
    with pytest.raises(PermissionError):
        schedule(draft, datetime.now(timezone.utc) + timedelta(days=1))


def test_schedule_approved_post():
    from datetime import datetime, timedelta, timezone
    draft = make_draft()
    request_approval(draft)
    approve(draft, "owner")
    schedule(draft, datetime.now(timezone.utc) + timedelta(days=1))
    assert draft.status == Status.SCHEDULED
