"""Human review of deterministically validated POM proposals."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.synthesis.enums import (
    ProposalReviewDecision,
    SynthesisRunStatus,
)
from test_cartographer.synthesis.models import SynthesisRun


def review_synthesis_run(
    run: SynthesisRun,
    *,
    decision: ProposalReviewDecision,
    reviewed_at: datetime,
    reason: str | None = None,
    review_seconds: float = 0.0,
) -> SynthesisRun:
    """Accept or reject only a validated proposal that is ready for review."""

    if run.status is not SynthesisRunStatus.READY_FOR_REVIEW:
        raise ValueError("only a ready_for_review synthesis run can be reviewed")
    if decision is ProposalReviewDecision.PENDING:
        raise ValueError("review decision must be accepted or rejected")
    if decision is ProposalReviewDecision.REJECTED and not reason:
        raise ValueError("rejected proposal requires a reason")

    status = (
        SynthesisRunStatus.ACCEPTED
        if decision is ProposalReviewDecision.ACCEPTED
        else SynthesisRunStatus.REJECTED
    )
    updated = run.model_copy(
        update={
            "status": status,
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_reason": reason,
            "review_seconds": review_seconds,
        }
    )
    return SynthesisRun.model_validate(updated.model_dump(mode="python"))
