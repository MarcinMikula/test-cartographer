import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.discovery.io import load_discovery_plan, load_discovery_profile
from test_cartographer.interactive_creation.browser import open_interactive_discovery
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
def test_headed_review_labels_bounded_candidates() -> None:
    plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")
    profile = load_discovery_profile(ROOT / "testdata/discovery/profile/replay.json")
    try:
        with serve_reference_directory(ROOT / "testdata/browser") as base_url:
            plan = plan.model_copy(
                update={"source_url": f"{base_url}/public_catalog_discovery.html"}
            )
            with open_interactive_discovery(
                plan,
                profile,
                run_id="interactive_browser_test",
                captured_at=datetime(2026, 8, 4, 18, 0, tzinfo=timezone.utc),
                executable_path=_executable(),
            ) as view:
                assert len(view.run.candidates) == 4
                labels = view.page.locator("[data-test-cartographer-candidate]")
                assert labels.count() == 4
                view.focus_candidates(view.run.ambiguities[0].candidate_ids)
                assert view.page.locator(
                    '[data-test-cartographer-candidate="cand_002"]'
                ).count() == 1
    except Exception as exc:
        if any(
            marker in str(exc)
            for marker in (
                "Executable doesn't exist",
                "Failed to launch",
                "ERR_BLOCKED_BY_ADMINISTRATOR",
                "Target page, context or browser has been closed",
            )
        ):
            pytest.skip(f"Chromium is unavailable for headed review: {exc}")
        raise
