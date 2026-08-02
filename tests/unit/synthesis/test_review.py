from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import (
    ProposalReviewDecision,
    SynthesisRunStatus,
)
from test_cartographer.synthesis.io import load_raw_output
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[3]
STARTED = datetime(2026, 8, 2, 12, 0, tzinfo=timezone.utc)
COMPLETED = datetime(2026, 8, 2, 12, 0, 1, tzinfo=timezone.utc)
REVIEWED = datetime(2026, 8, 2, 12, 1, tzinfo=timezone.utc)


def _ready_run(synthesis_request, valid_raw_output):
    return run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter(valid_raw_output),
        run_id="synrun_review",
        started_at=STARTED,
        completed_at=COMPLETED,
    )


def test_validated_proposal_can_be_accepted(
    synthesis_request,
    valid_raw_output,
) -> None:
    run = _ready_run(synthesis_request, valid_raw_output)
    reviewed = review_synthesis_run(
        run,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=REVIEWED,
        reason="Reference architecture accepted.",
        review_seconds=8.0,
    )

    assert reviewed.status is SynthesisRunStatus.ACCEPTED
    assert reviewed.decision is ProposalReviewDecision.ACCEPTED
    assert reviewed.review_reason == "Reference architecture accepted."
    assert reviewed.review_seconds == 8.0


def test_validated_proposal_can_be_rejected_with_reason(
    synthesis_request,
    valid_raw_output,
) -> None:
    run = _ready_run(synthesis_request, valid_raw_output)
    reviewed = review_synthesis_run(
        run,
        decision=ProposalReviewDecision.REJECTED,
        reviewed_at=REVIEWED,
        reason="Component boundary should be reviewed.",
    )

    assert reviewed.status is SynthesisRunStatus.REJECTED
    assert reviewed.decision is ProposalReviewDecision.REJECTED


def test_rejection_requires_reason(synthesis_request, valid_raw_output) -> None:
    run = _ready_run(synthesis_request, valid_raw_output)
    with pytest.raises(ValueError, match="requires a reason"):
        review_synthesis_run(
            run,
            decision=ProposalReviewDecision.REJECTED,
            reviewed_at=REVIEWED,
        )


def test_protocol_error_cannot_be_reviewed(synthesis_request) -> None:
    run = run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter("not-json"),
        run_id="synrun_bad_review",
        started_at=STARTED,
        completed_at=COMPLETED,
    )
    with pytest.raises(ValueError, match="ready_for_review"):
        review_synthesis_run(
            run,
            decision=ProposalReviewDecision.ACCEPTED,
            reviewed_at=REVIEWED,
        )


def test_validation_rejection_cannot_be_reviewed(synthesis_request) -> None:
    raw = load_raw_output(
        ROOT / "testdata/synthesis/raw/overreach_public_search.json"
    )
    run = run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter(raw),
        run_id="synrun_invalid_review",
        started_at=STARTED,
        completed_at=COMPLETED,
    )
    with pytest.raises(ValueError, match="ready_for_review"):
        review_synthesis_run(
            run,
            decision=ProposalReviewDecision.ACCEPTED,
            reviewed_at=REVIEWED,
        )
