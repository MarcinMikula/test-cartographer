import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.io import load_framework_snapshot, load_workspace_profile
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.io import load_code_patch
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox
from test_cartographer.observation.reference import serve_reference_directory

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.browser
def test_accepted_patch_creates_one_runnable_framework_test(tmp_path) -> None:
    framework = tmp_path / "framework"
    workspace_profile = load_workspace_profile(ROOT / "testdata/adaptation/profile/qa_automation_framework.json")
    framework_snapshot = load_framework_snapshot(ROOT / "testdata/adaptation/snapshot/qa_automation_framework.json")
    materialize_snapshot_sandbox(
        ROOT / "testdata/framework/reference",
        framework,
        workspace_profile,
        framework_snapshot,
    )
    report = apply_code_patch(
        load_code_patch(ROOT / "testdata/delivery/patch/accepted_public_search.json"),
        workspace_profile,
        framework_snapshot,
        framework,
        application_id="apply_real_browser_public_search",
        applied_at=datetime(2026, 8, 2, 14, 0, tzinfo=timezone.utc),
    )
    assert len(report.changes) == 4

    with serve_reference_directory(ROOT / "testdata/browser") as base_url:
        env = os.environ.copy()
        env["TEST_CARTOGRAPHER_CATALOG_URL"] = f"{base_url}/public_catalog.html"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/e2e/test_search_catalog.py",
            ],
            cwd=framework,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    output = f"{result.stdout}\n{result.stderr}"
    if result.returncode != 0 and any(
        marker in output
        for marker in (
            "Executable doesn't exist",
            "Failed to launch",
            "ERR_BLOCKED_BY_ADMINISTRATOR",
        )
    ):
        pytest.skip(f"Controlled Chromium execution is unavailable: {output}")
    assert result.returncode == 0, output
    assert "1 passed" in output
