from datetime import datetime, timezone

import pytest

from test_cartographer.delivery.enums import CodePatchStatus, PatchReviewDecision
from test_cartographer.delivery.review import review_code_patch


def test_accepting_exact_source_changes_only_patch_state(pending_patch):
    accepted = review_code_patch(
        pending_patch,
        decision=PatchReviewDecision.ACCEPTED,
        reviewed_at=datetime(2026, 8, 2, 13, 10, tzinfo=timezone.utc),
        reason="Exact source matches the accepted adaptation plan.",
        review_seconds=12.5,
    )
    assert accepted.status is CodePatchStatus.ACCEPTED
    assert accepted.decision is PatchReviewDecision.ACCEPTED
    assert accepted.review_seconds == 12.5
    assert accepted.changes == pending_patch.changes


def test_rejection_requires_reason(pending_patch):
    with pytest.raises(ValueError, match="requires a reason"):
        review_code_patch(
            pending_patch,
            decision=PatchReviewDecision.REJECTED,
            reviewed_at=datetime(2026, 8, 2, 13, 10, tzinfo=timezone.utc),
        )


def test_review_cannot_be_repeated(accepted_patch):
    with pytest.raises(ValueError, match="ready_for_review"):
        review_code_patch(
            accepted_patch,
            decision=PatchReviewDecision.ACCEPTED,
            reviewed_at=datetime(2026, 8, 2, 13, 10, tzinfo=timezone.utc),
        )
