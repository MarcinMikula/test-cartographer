import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.discovery.capture import capture_process_discovery
from test_cartographer.discovery.enums import DiscoveryTargetState
from test_cartographer.discovery.io import load_discovery_plan, load_discovery_profile
from test_cartographer.observation.reference import serve_reference_directory

ROOT = Path(__file__).resolve().parents[2]


def _executable() -> str | None:
    explicit = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if explicit:
        return explicit
    if os.name != "nt":
        return shutil.which("chromium") or shutil.which("google-chrome")
    return None


@pytest.mark.browser
def test_controlled_page_produces_three_targets_and_one_ambiguity() -> None:
    plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")
    profile = load_discovery_profile(ROOT / "testdata/discovery/profile/replay.json")
    try:
        with serve_reference_directory(ROOT / "testdata/browser") as base_url:
            plan = plan.model_copy(
                update={"source_url": f"{base_url}/public_catalog_discovery.html"}
            )
            run = capture_process_discovery(
                plan,
                profile,
                run_id="discovery_browser_test",
                captured_at=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
                executable_path=_executable(),
            )
    except Exception as exc:
        if any(
            marker in str(exc)
            for marker in (
                "Executable doesn't exist",
                "Failed to launch",
                "ERR_BLOCKED_BY_ADMINISTRATOR",
            )
        ):
            pytest.skip(f"Chromium is not installed for Playwright: {exc}")
        raise

    assert len(run.candidates) == 4
    assert len(run.targets) == 3
    assert [item.state for item in run.targets].count(DiscoveryTargetState.AMBIGUOUS) == 1
    assert len(run.ambiguities) == 1
    assert all(candidate.input_value_persisted is False for candidate in run.candidates)
    assert all(candidate.raw_text_content_persisted is False for candidate in run.candidates)
