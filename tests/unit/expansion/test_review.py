import pytest

from test_cartographer.expansion.enums import ExpansionPlanStatus, ExpansionReviewDecision
from test_cartographer.expansion.review import accept_expansion_plan, reject_expansion_plan


def test_accept_plan_records_explicit_human_review(expansion_plan, fixed_now):
    accepted = accept_expansion_plan(expansion_plan, reviewed_at=fixed_now, review_seconds=2.5)
    assert accepted.status is ExpansionPlanStatus.ACCEPTED
    assert accepted.decision is ExpansionReviewDecision.ACCEPTED
    assert accepted.review_seconds == 2.5


def test_reject_plan_requires_reason(expansion_plan, fixed_now):
    with pytest.raises(ValueError, match="requires a reason"):
        reject_expansion_plan(expansion_plan, reason=" ", reviewed_at=fixed_now, review_seconds=1.0)


def test_plan_cannot_be_accepted_twice(accepted_expansion_plan, fixed_now):
    with pytest.raises(ValueError, match="ready, unblocked"):
        accept_expansion_plan(accepted_expansion_plan, reviewed_at=fixed_now, review_seconds=1.0)
