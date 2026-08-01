from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.observation.io import load_observation, save_observation
from test_cartographer.observation.models import (
    BrowserObservation,
    ElementSnapshot,
    LocatorVerification,
)


def test_observation_round_trip_is_deterministic(tmp_path: Path) -> None:
    observation = BrowserObservation(
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
        capture_sha256="c" * 64,
    )
    path = tmp_path / "observation.json"

    save_observation(observation, path)

    assert load_observation(path) == observation
    assert path.read_bytes().endswith(b"\n")


def test_committed_replay_fixtures_load() -> None:
    root = Path(__file__).resolve().parents[3]

    pending = load_observation(
        root / "testdata/observation/pending/search_submit.json"
    )
    accepted = load_observation(
        root / "testdata/observation/accepted/search_submit.json"
    )

    assert pending.decision.value == "pending"
    assert accepted.decision.value == "accepted"
    assert pending.capture_sha256 == accepted.capture_sha256
