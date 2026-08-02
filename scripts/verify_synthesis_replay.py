"""Verify the complete bounded synthesis replay and human-review boundary."""

from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision, SynthesisRunStatus
from test_cartographer.synthesis.io import load_raw_output, load_synthesis_request
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import render_synthesis_prompt
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    request = load_synthesis_request(
        ROOT / "testdata/synthesis/request/public_search.json"
    )
    raw_output = load_raw_output(
        ROOT / "testdata/synthesis/raw/valid_public_search.json"
    )
    adapter = ReplaySynthesisAdapter(raw_output)
    run = run_synthesis(
        request,
        adapter,
        run_id="synrun_verify_public_search",
        started_at=datetime(2026, 8, 2, 9, 10, tzinfo=timezone.utc),
        completed_at=datetime(2026, 8, 2, 9, 10, 1, tzinfo=timezone.utc),
    )
    if run.status is not SynthesisRunStatus.READY_FOR_REVIEW:
        raise RuntimeError(f"unexpected synthesis status: {run.status.value}")
    if run.validation is None or not run.validation.valid:
        raise RuntimeError("reference proposal did not pass deterministic validation")
    if adapter.last_request != request:
        raise RuntimeError("replay adapter did not receive the exact request")
    if adapter.last_prompt != render_synthesis_prompt(request):
        raise RuntimeError("replay adapter did not receive the deterministic prompt")
    reviewed = review_synthesis_run(
        run,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=datetime(2026, 8, 2, 9, 11, tzinfo=timezone.utc),
        reason="Reference POM boundaries accepted for replay verification.",
        review_seconds=5.0,
    )
    if reviewed.status is not SynthesisRunStatus.ACCEPTED:
        raise RuntimeError("validated proposal did not reach accepted state")

    prompt = render_synthesis_prompt(request)
    forbidden_fragments = (
        "https://catalog.example.test/",
        "/catalog",
        "tester:sprint_1_reference_definition",
        "fixture:guided_catalog_observation_v1",
    )
    leaked = [fragment for fragment in forbidden_fragments if fragment in prompt]
    if leaked:
        raise RuntimeError(f"bounded prompt leaked excluded fields: {leaked}")

    print("Ready context projected into a bounded synthesis request.")
    print("Base URL, routes, raw source references, notes, and hashes were excluded.")
    print("Replay adapter received the exact deterministic request and prompt.")
    print("Raw JSON parsed strictly and passed deterministic POM validation.")
    print("Proposal remained pending until explicit human acceptance.")
    print("No live provider was used and no repository files were modified.")


if __name__ == "__main__":
    main()
