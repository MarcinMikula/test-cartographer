from datetime import datetime, timezone

import pytest

from test_cartographer.adaptation.enums import (
    AdaptationPlanStatus,
    AdaptationReviewDecision,
)
from test_cartographer.adaptation.io import load_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan


def test_accept_plan(repository_root):
    plan = load_adaptation_plan(
        repository_root / "testdata/adaptation/plan/pending_public_search.json"
    )
    reviewed = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=datetime(2026, 8, 2, 12, 10, tzinfo=timezone.utc),
        review_seconds=4.5,
    )
    assert reviewed.status is AdaptationPlanStatus.ACCEPTED
    assert reviewed.decision is AdaptationReviewDecision.ACCEPTED
    assert reviewed.framework_files_modified is False


def test_reject_plan_requires_reason(repository_root):
    plan = load_adaptation_plan(
        repository_root / "testdata/adaptation/plan/pending_public_search.json"
    )
    with pytest.raises(ValueError, match="requires a reason"):
        review_adaptation_plan(
            plan,
            decision=AdaptationReviewDecision.REJECTED,
            reviewed_at=datetime.now(timezone.utc),
        )


def test_plan_cannot_be_reviewed_twice(repository_root):
    plan = load_adaptation_plan(
        repository_root / "testdata/adaptation/plan/pending_public_search.json"
    )
    reviewed = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=datetime.now(timezone.utc),
    )
    with pytest.raises(ValueError, match="ready_for_review"):
        review_adaptation_plan(
            reviewed,
            decision=AdaptationReviewDecision.REJECTED,
            reviewed_at=datetime.now(timezone.utc),
            reason="Changed decision.",
        )
