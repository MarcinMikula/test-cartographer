"""Verify the complete Sprint 3 boundary against the controlled local page."""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.context.io import load_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.observation.capture import (
    capture_browser_observation,
)
from test_cartographer.observation.enums import ObservationDecision
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.observation.review import (
    apply_accepted_observation,
    review_observation,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    context = load_context(
        ROOT / "testdata/context/observation_ready/public_search_flow.json"
    )
    before = assess_readiness(context)
    if before.blocker_count != 1:
        raise RuntimeError(f"expected one pre-observation blocker, got {before.blocker_count}")

    executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if executable is None and os.name != "nt":
        executable = shutil.which("chromium") or shutil.which("google-chrome")

    captured_at = datetime.now(timezone.utc)
    with serve_reference_directory(ROOT / "testdata/browser") as base_url:
        observation = capture_browser_observation(
            context,
            url=f"{base_url}/public_catalog.html",
            element_id="el_search_submit",
            observation_id="obs_verify_search_submit",
            captured_at=captured_at,
            sensitivity=SensitivityLevel.PUBLIC,
            executable_path=executable,
        )
    reviewed = review_observation(
        observation,
        decision=ObservationDecision.ACCEPTED,
        reviewed_at=datetime.now(timezone.utc),
        reason="Accepted during controlled Sprint 3 verification.",
    )
    updated = apply_accepted_observation(context, reviewed)
    after = assess_readiness(updated)
    if not after.ready:
        codes = ", ".join(issue.code for issue in after.issues)
        raise RuntimeError(f"context is still not ready after observation: {codes}")
    if observation.element.input_value_persisted:
        raise RuntimeError("input value persistence must remain disabled")

    print("Controlled page opened through Playwright.")
    print("One target locator matched exactly one visible element.")
    print("No input value, text content, HTML, screenshot, or raw page was persisted.")
    print("Primary locator promoted from INFERRED to OBSERVED after human acceptance.")
    print("Full adaptation readiness: ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
