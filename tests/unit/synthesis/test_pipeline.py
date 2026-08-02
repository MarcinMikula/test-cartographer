from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import SynthesisRunStatus
from test_cartographer.synthesis.io import load_raw_output
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import render_synthesis_prompt

ROOT = Path(__file__).resolve().parents[3]
STARTED = datetime(2026, 8, 2, 11, 0, tzinfo=timezone.utc)
COMPLETED = datetime(2026, 8, 2, 11, 0, 1, tzinfo=timezone.utc)


def test_successful_replay_preserves_exact_request_prompt_and_raw_output(
    synthesis_request,
    valid_raw_output,
) -> None:
    adapter = ReplaySynthesisAdapter(valid_raw_output)
    run = run_synthesis(
        synthesis_request,
        adapter,
        run_id="synrun_success",
        started_at=STARTED,
        completed_at=COMPLETED,
    )

    assert run.status is SynthesisRunStatus.READY_FOR_REVIEW
    assert run.raw_output == valid_raw_output
    assert adapter.last_request == synthesis_request
    assert adapter.last_prompt == render_synthesis_prompt(synthesis_request)
    assert adapter.call_count == 1
    assert run.validation is not None and run.validation.valid


def test_protocol_failure_is_separate_and_preserves_raw_output(
    synthesis_request,
) -> None:
    raw = "```json\n{}\n```"
    run = run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter(raw),
        run_id="synrun_protocol_error",
        started_at=STARTED,
        completed_at=COMPLETED,
    )

    assert run.status is SynthesisRunStatus.PROTOCOL_ERROR
    assert run.raw_output == raw
    assert run.parse_failure is not None
    assert run.parse_failure.code == "markdown_fence"
    assert run.proposal is None
    assert run.validation is None


def test_substantive_validation_rejection_is_not_parse_failure(
    synthesis_request,
) -> None:
    raw = load_raw_output(
        ROOT / "testdata/synthesis/raw/overreach_public_search.json"
    )
    run = run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter(raw),
        run_id="synrun_overreach",
        started_at=STARTED,
        completed_at=COMPLETED,
    )

    assert run.status is SynthesisRunStatus.VALIDATION_REJECTED
    assert run.proposal is not None
    assert run.parse_failure is None
    assert run.validation is not None
    assert run.validation.error_count == 1
    assert run.validation.issues[0].code == "prohibited_claim"
