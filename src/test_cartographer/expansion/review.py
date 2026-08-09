
"""Human review transitions for one expansion plan."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.expansion.enums import (
    ExpansionPlanStatus,
    ExpansionReviewDecision,
)
from test_cartographer.expansion.models import ExpansionPlan


def accept_expansion_plan(
    plan: ExpansionPlan,
    *,
    reviewed_at: datetime,
    review_seconds: float,
) -> ExpansionPlan:
    if plan.status is not ExpansionPlanStatus.READY_FOR_REVIEW:
        raise ValueError("only a ready, unblocked expansion plan can be accepted")
    updated = plan.model_copy(
        update={
            "status": ExpansionPlanStatus.ACCEPTED,
            "decision": ExpansionReviewDecision.ACCEPTED,
            "reviewed_at": reviewed_at,
            "review_seconds": review_seconds,
        }
    )
    return ExpansionPlan.model_validate(updated.model_dump(mode="python"))


def reject_expansion_plan(
    plan: ExpansionPlan,
    *,
    reason: str,
    reviewed_at: datetime,
    review_seconds: float,
) -> ExpansionPlan:
    if plan.status not in {
        ExpansionPlanStatus.READY_FOR_REVIEW,
        ExpansionPlanStatus.BLOCKED,
    }:
        raise ValueError("expansion plan has already been reviewed")
    if not reason.strip():
        raise ValueError("rejected expansion plan requires a reason")
    updated = plan.model_copy(
        update={
            "status": ExpansionPlanStatus.REJECTED,
            "decision": ExpansionReviewDecision.REJECTED,
            "reviewed_at": reviewed_at,
            "review_reason": reason.strip(),
            "review_seconds": review_seconds,
        }
    )
    # A previously blocked plan has PENDING semantics in the strict contract. Rejection
    # converts it into a normal rejected review artefact with no remaining blocked status.
    payload = updated.model_dump(mode="python")
    return ExpansionPlan.model_validate(payload)
