from pathlib import Path

from test_cartographer.cli import main
from test_cartographer.synthesis.enums import SynthesisRunStatus
from test_cartographer.synthesis.io import (
    load_synthesis_request,
    load_synthesis_run,
)

ROOT = Path(__file__).resolve().parents[2]


def test_cli_builds_replays_and_accepts_reference_proposal(
    tmp_path,
    capsys,
) -> None:
    request_path = tmp_path / "request.json"
    run_path = tmp_path / "run.json"

    assert (
        main(
            [
                "synthesize",
                "request",
                "--context",
                str(
                    ROOT
                    / "testdata/context/synthesis_ready/public_search_flow.json"
                ),
                "--request",
                str(request_path),
                "--request-id",
                "synreq_cli_public_search",
            ]
        )
        == 0
    )
    request = load_synthesis_request(request_path)
    assert request.id == "synreq_cli_public_search"
    request_output = capsys.readouterr().out
    assert "Created synthesis request" in request_output
    assert "Excluded fields: 9" in request_output

    raw = (
        ROOT / "testdata/synthesis/raw/valid_public_search.json"
    ).read_text(encoding="utf-8")
    raw = raw.replace("synreq_public_search", "synreq_cli_public_search")
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(raw, encoding="utf-8")

    assert (
        main(
            [
                "synthesize",
                "replay",
                "--request",
                str(request_path),
                "--raw-output",
                str(raw_path),
                "--run",
                str(run_path),
                "--run-id",
                "synrun_cli_public_search",
            ]
        )
        == 0
    )
    run = load_synthesis_run(run_path)
    assert run.status is SynthesisRunStatus.READY_FOR_REVIEW
    replay_output = capsys.readouterr().out
    assert "Status: ready_for_review" in replay_output
    assert "Validation errors: 0" in replay_output

    assert main(["synthesize", "status", "--run", str(run_path)]) == 0
    assert "Decision: pending" in capsys.readouterr().out

    assert (
        main(
            [
                "synthesize",
                "review",
                "--run",
                str(run_path),
                "--decision",
                "accepted",
                "--reason",
                "Reference POM proposal accepted.",
                "--review-seconds",
                "4.5",
            ]
        )
        == 0
    )
    accepted = load_synthesis_run(run_path)
    assert accepted.status is SynthesisRunStatus.ACCEPTED
    review_output = capsys.readouterr().out
    assert "Status: accepted" in review_output
    assert "Review seconds: 4.500" in review_output


def test_cli_preserves_protocol_failure_as_run(tmp_path, capsys) -> None:
    run_path = tmp_path / "bad-run.json"
    assert (
        main(
            [
                "synthesize",
                "replay",
                "--request",
                str(ROOT / "testdata/synthesis/request/public_search.json"),
                "--raw-output",
                str(
                    ROOT
                    / "testdata/synthesis/raw/markdown_fenced_public_search.txt"
                ),
                "--run",
                str(run_path),
                "--run-id",
                "synrun_cli_protocol_error",
            ]
        )
        == 0
    )
    run = load_synthesis_run(run_path)
    assert run.status is SynthesisRunStatus.PROTOCOL_ERROR
    output = capsys.readouterr().out
    assert "Protocol failure: markdown_fence" in output
    assert "Raw output characters:" in output
