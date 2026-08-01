from datetime import datetime, timezone
from pathlib import Path

from test_cartographer import cli
from test_cartographer.cli import main
from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.io import load_context
from test_cartographer.observation.enums import ObservationDecision
from test_cartographer.observation.io import load_observation
from test_cartographer.observation.models import (
    BrowserObservation,
    ElementSnapshot,
    LocatorVerification,
)

ROOT = Path(__file__).resolve().parents[2]


def _context_path() -> Path:
    return ROOT / "testdata/context/observation_ready/public_search_flow.json"


def _pending() -> BrowserObservation:
    return BrowserObservation(
        id="obs_search_submit",
        context_id="ctx_public_catalog_search_observation_ready",
        target_element_id="el_search_submit",
        target_locator_id="loc_search_submit_role",
        source_url="https://catalog.example.test/catalog",
        captured_at=datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc),
        sensitivity=SensitivityLevel.PUBLIC,
        capture_seconds=0.2,
        locator=LocatorVerification(
            locator_id="loc_search_submit_role",
            strategy=LocatorStrategy.ROLE,
            value="button:Search",
        ),
        element=ElementSnapshot(
            tag_name="button",
            visible=True,
            enabled=True,
            editable=False,
        ),
        capture_sha256="d" * 64,
    )


def test_cli_capture_status_accept_and_context_update(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    observation_path = tmp_path / "observation.json"
    updated_context_path = tmp_path / "context.json"
    monkeypatch.setattr(cli, "capture_browser_observation", lambda *args, **kwargs: _pending())

    assert main(
        [
            "observe",
            "capture",
            "--context",
            str(_context_path()),
            "--url",
            "https://catalog.example.test/catalog?secret=value",
            "--element-id",
            "el_search_submit",
            "--observation",
            str(observation_path),
            "--observation-id",
            "obs_search_submit",
            "--sensitivity",
            "public",
        ]
    ) == 0
    assert main(["observe", "status", "--observation", str(observation_path)]) == 0
    assert main(
        [
            "observe",
            "review",
            "--observation",
            str(observation_path),
            "--decision",
            "accepted",
            "--reason",
            "Target mapping is correct.",
            "--context",
            str(_context_path()),
            "--output-context",
            str(updated_context_path),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Decision: pending" in output
    assert "Decision: accepted" in output
    assert "Full adaptation ready: true" in output
    assert load_observation(observation_path).decision is ObservationDecision.ACCEPTED
    updated = load_context(updated_context_path)
    locator = next(
        candidate
        for element in updated.elements
        if element.id == "el_search_submit"
        for candidate in element.locator_candidates
        if candidate.primary
    )
    assert locator.value.status.value == "observed"


def test_cli_rejection_does_not_require_or_write_context(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    observation_path = tmp_path / "observation.json"
    monkeypatch.setattr(cli, "capture_browser_observation", lambda *args, **kwargs: _pending())
    main(
        [
            "observe",
            "capture",
            "--context",
            str(_context_path()),
            "--url",
            "https://catalog.example.test/catalog",
            "--element-id",
            "el_search_submit",
            "--observation",
            str(observation_path),
        ]
    )

    assert main(
        [
            "observe",
            "review",
            "--observation",
            str(observation_path),
            "--decision",
            "rejected",
            "--reason",
            "The selected target is incorrect.",
        ]
    ) == 0

    assert "Context was not changed." in capsys.readouterr().out
    assert load_observation(observation_path).decision is ObservationDecision.REJECTED
