"""Human review boundary for exact generated source proposals."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.delivery.enums import (
    CodePatchStatus,
    PatchReviewDecision,
)
from test_cartographer.delivery.models import CodePatch


def review_code_patch(
    patch: CodePatch,
    *,
    decision: PatchReviewDecision,
    reviewed_at: datetime,
    reason: str | None = None,
    review_seconds: float = 0.0,
) -> CodePatch:
    if patch.status is not CodePatchStatus.READY_FOR_REVIEW:
        raise ValueError("only a ready_for_review code patch can be reviewed")
    if decision is PatchReviewDecision.PENDING:
        raise ValueError("review decision must be accepted or rejected")
    if decision is PatchReviewDecision.REJECTED and not reason:
        raise ValueError("rejected code patch requires a reason")
    status = (
        CodePatchStatus.ACCEPTED
        if decision is PatchReviewDecision.ACCEPTED
        else CodePatchStatus.REJECTED
    )
    updated = patch.model_copy(
        update={
            "status": status,
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_reason": reason,
            "review_seconds": review_seconds,
        }
    )
    return CodePatch.model_validate(updated.model_dump(mode="python"))
