"""Human review of a deterministic framework adaptation plan."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.adaptation.enums import (
    AdaptationPlanStatus,
    AdaptationReviewDecision,
)
from test_cartographer.adaptation.models import AdaptationPlan


def review_adaptation_plan(
    plan: AdaptationPlan,
    *,
    decision: AdaptationReviewDecision,
    reviewed_at: datetime,
    reason: str | None = None,
    review_seconds: float = 0.0,
) -> AdaptationPlan:
    if plan.status is not AdaptationPlanStatus.READY_FOR_REVIEW:
        raise ValueError("only a ready_for_review adaptation plan can be reviewed")
    if decision is AdaptationReviewDecision.PENDING:
        raise ValueError("review decision must be accepted or rejected")
    if decision is AdaptationReviewDecision.REJECTED and not reason:
        raise ValueError("rejected adaptation plan requires a reason")
    status = (
        AdaptationPlanStatus.ACCEPTED
        if decision is AdaptationReviewDecision.ACCEPTED
        else AdaptationPlanStatus.REJECTED
    )
    updated = plan.model_copy(
        update={
            "status": status,
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_reason": reason,
            "review_seconds": review_seconds,
        }
    )
    return AdaptationPlan.model_validate(updated.model_dump(mode="python"))
