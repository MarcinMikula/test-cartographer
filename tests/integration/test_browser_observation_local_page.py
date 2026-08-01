import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.io import load_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.observation.capture import (
    capture_browser_observation,
)
from test_cartographer.observation.enums import ObservationDecision
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.observation.review import (
    apply_accepted_observation,
    review_observation,
)

ROOT = Path(__file__).resolve().parents[2]


def _executable() -> str | None:
    explicit = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if explicit:
        return explicit
    if os.name != "nt":
        return shutil.which("chromium") or shutil.which("google-chrome")
    return None


@pytest.mark.browser
def test_controlled_local_page_produces_real_browser_evidence() -> None:
    context = load_context(
        ROOT / "testdata/context/observation_ready/public_search_flow.json"
    )
    captured_at = datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc)
    try:
        with serve_reference_directory(ROOT / "testdata/browser") as base_url:
            observation = capture_browser_observation(
                context,
                url=f"{base_url}/public_catalog.html",
                element_id="el_search_submit",
                observation_id="obs_real_search_submit",
                captured_at=captured_at,
                sensitivity=SensitivityLevel.PUBLIC,
                executable_path=_executable(),
            )
    except Exception as exc:
        if any(marker in str(exc) for marker in ("Executable doesn't exist", "Failed to launch", "ERR_BLOCKED_BY_ADMINISTRATOR")):
            pytest.skip(f"Chromium is not installed for Playwright: {exc}")
        raise

    accepted = review_observation(
        observation,
        decision=ObservationDecision.ACCEPTED,
        reviewed_at=captured_at + timedelta(seconds=1),
        reason="Controlled fixture target verified.",
    )
    updated = apply_accepted_observation(context, accepted)

    assert observation.locator.match_count == 1
    assert observation.element.tag_name == "button"
    assert observation.element.visible is True
    assert observation.element.input_value_persisted is False
    assert assess_readiness(updated).ready is True
