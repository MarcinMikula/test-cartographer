from pathlib import Path

from test_cartographer.context.io import load_context
from test_cartographer.context.readiness import assess_readiness

ROOT = Path(__file__).resolve().parents[3]


def _fixture(state: str) -> Path:
    return ROOT / "testdata" / "context" / state / "public_search_flow.json"


def test_complete_reference_context_is_ready() -> None:
    report = assess_readiness(load_context(_fixture("valid")))

    assert report.ready is True
    assert report.blocker_count == 0
    assert report.warning_count == 0
    assert report.issues == ()


def test_incomplete_context_is_valid_but_not_ready() -> None:
    context = load_context(_fixture("incomplete"))
    report = assess_readiness(context)
    codes = {issue.code for issue in report.issues}

    assert context.schema_version == "0.1"
    assert report.ready is False
    assert report.blocker_count >= 4
    assert "risk_not_confirmed" in codes
    assert "outcome_not_confirmed" in codes
    assert "primary_locator_not_observed" in codes
    assert "blocking_question_open" in codes


def test_conflicting_context_is_valid_but_not_ready() -> None:
    context = load_context(_fixture("conflicting"))
    report = assess_readiness(context)
    codes = {issue.code for issue in report.issues}

    assert context.conflicts[0].resolution.status.value == "unknown"
    assert report.ready is False
    assert "primary_locator_not_observed" in codes
    assert "conflict_unresolved" in codes


def test_readiness_report_is_serializable() -> None:
    report = assess_readiness(load_context(_fixture("incomplete")))
    payload = report.model_dump(mode="json")

    assert payload["ready"] is False
    assert payload["blocker_count"] == report.blocker_count
    assert isinstance(payload["issues"], list)
