from test_cartographer.cli import main
from test_cartographer.creation_flow.io import save_creation_flow_run
from test_cartographer.interactive_creation.io import (
    save_interactive_profile,
    save_operator_session,
)


def test_interactive_status_reports_real_human_boundary(
    tmp_path,
    interactive_profile,
    interactive_creation_run,
    operator_session,
    capsys,
) -> None:
    profile_path = tmp_path / "profile.json"
    session_path = tmp_path / "operator-session.json"
    run_path = tmp_path / "creation-flow-run.json"
    save_interactive_profile(interactive_profile, profile_path)
    save_operator_session(operator_session, session_path)
    save_creation_flow_run(interactive_creation_run, run_path)

    result = main(
        [
            "creation",
            "interactive-status",
            "--profile",
            str(profile_path),
            "--session",
            str(session_path),
            "--run",
            str(run_path),
        ]
    )
    output = capsys.readouterr().out
    assert result == 0
    assert "Fixture-assisted reference flow: false" in output
    assert "Interactive human trigger used: true" in output
    assert "Fixture answers used: false" in output
    assert "Headed browser used: true" in output
    assert "Real operator actions: 18" in output
    assert "Intake answers: 9" in output
    assert "Context-summary confirmations: 1" in output
    assert "Human-trigger blockers: none" in output
    assert "Human trigger verified: true" in output
    assert "Ready for external user demonstration: true" in output


def test_patch_rereview_status_reports_exact_review_proof(tmp_path, capsys) -> None:
    from datetime import datetime, timedelta, timezone

    from test_cartographer.interactive_creation.io import save_patch_rereview_report
    from test_cartographer.interactive_creation.models import ExactPatchRereviewReport

    started = datetime(2026, 8, 5, 16, 0, tzinfo=timezone.utc)
    report = ExactPatchRereviewReport(
        id="patch_rereview_report_cli",
        creation_flow_run_id="creation_flow_interactive_test",
        original_patch_id="patch_original",
        corrected_patch_id="patch_corrected",
        started_at=started,
        completed_at=started + timedelta(seconds=5),
        decision="accepted",
        ambiguity_question_deterministically_completed=True,
        change_count=4,
        operator_review_seconds=4.0,
        collected_test_count=1,
        passed_test_count=1,
    )
    path = tmp_path / "report.json"
    save_patch_rereview_report(report, path)
    result = main(
        ["creation", "patch-rereview-status", "--report", str(path)]
    )
    output = capsys.readouterr().out
    assert result == 0
    assert "Exact source displayed: true" in output
    assert "Omitted source lines: false" in output
    assert "LLM role disclosed: true" in output
    assert "Deterministic synthesis disclosed: true" in output
    assert "Exact patch re-review verified: true" in output
