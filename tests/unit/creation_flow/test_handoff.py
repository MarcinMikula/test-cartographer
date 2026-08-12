from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.io import load_context
from test_cartographer.creation_flow.handoff import HANDOFF_PATHS, confirm_synthesis_handoff

ROOT = Path(__file__).resolve().parents[3]


def test_handoff_confirms_every_provided_value_required_by_synthesis() -> None:
    context = load_context(
        ROOT / "testdata/creation_flow/context/public_catalog_discovered.json"
    )
    updated = confirm_synthesis_handoff(
        context,
        confirmed_at=datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc),
    )

    opening_step = next(step for step in updated.process.steps if step.id == "step_open_catalog")
    assert HANDOFF_PATHS == (
        "application.name",
        "application.environment",
        "process.name",
        "process.steps[opening_navigation].intent",
    )
    assert updated.application.name.status is KnowledgeStatus.CONFIRMED
    assert updated.application.environment.status is KnowledgeStatus.CONFIRMED
    assert updated.process.name.status is KnowledgeStatus.CONFIRMED
    assert opening_step.intent.status is KnowledgeStatus.CONFIRMED
    assert updated.application.base_url.status is KnowledgeStatus.OBSERVED
    assert updated.process.purpose.status is KnowledgeStatus.CONFIRMED
    assert updated.evidence[-1].id == "ev_creation_handoff"
    assert updated.evidence[-1].content_sha256 is not None
    assert "opening-step intent" in updated.evidence[-1].summary


def test_handoff_rejects_context_before_process_discovery() -> None:
    context = load_context(ROOT / "testdata/guided_intake/context/replay_complete.json")

    with pytest.raises(ValueError, match="opening navigation and discovered process steps"):
        confirm_synthesis_handoff(
            context,
            confirmed_at=datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc),
        )
