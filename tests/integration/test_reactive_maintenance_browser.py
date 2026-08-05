import os
import shutil
from pathlib import Path

import pytest

from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.reactive_maintenance.io import load_maintenance_profile
from test_cartographer.reactive_maintenance.runner import (
    capture_maintenance_candidates,
    matching_maintenance_candidates,
    run_scripted_maintenance_mechanics,
)

ROOT = Path(__file__).resolve().parents[2]


def _executable() -> str | None:
    explicit = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if explicit:
        return explicit
    if os.name != "nt":
        return shutil.which("chromium") or shutil.which("google-chrome")
    return None


def _browser_unavailable(exc: Exception) -> bool:
    return any(
        marker in str(exc)
        for marker in (
            "Executable doesn't exist",
            "Failed to launch",
            "ERR_BLOCKED_BY_ADMINISTRATOR",
            "Target page, context or browser has been closed",
            "browser unavailable during scripted framework setup",
        )
    )


@pytest.mark.browser
def test_current_page_exposes_changed_submit_candidate() -> None:
    profile = load_maintenance_profile(
        ROOT / "testdata/maintenance/profile/reactive_catalog.json"
    )
    try:
        with serve_reference_directory(ROOT / "testdata/maintenance/browser") as base_url:
            run = capture_maintenance_candidates(
                f"{base_url}/public_catalog_changed.html",
                profile,
                headed=False,
                executable_path=_executable(),
            )
            candidates = matching_maintenance_candidates(run, profile, "exe_reference")
    except Exception as exc:
        if _browser_unavailable(exc):
            pytest.skip(f"Chromium is unavailable for maintenance discovery: {exc}")
        raise
    assert {item.locator_value for item in candidates} == {
        "catalog-search-submit",
        "search-help",
    }
    assert all(item.old_locator_absent for item in candidates)


@pytest.mark.browser
def test_scripted_fail_repair_pass_mechanics(tmp_path) -> None:
    try:
        run_scripted_maintenance_mechanics(
            maintenance_profile_path=ROOT / "testdata/maintenance/profile/reactive_catalog.json",
            execution_profile_path=ROOT / "testdata/maintenance/evidence/strict_internal.json",
            workspace_profile_path=ROOT / "testdata/maintenance/workspace/qa_automation_framework.json",
            framework_root=ROOT / "testdata/maintenance/framework",
            application_root=ROOT / "testdata/maintenance/browser",
            output_dir=tmp_path / "replay",
            executable_path=_executable(),
        )
    except Exception as exc:
        if _browser_unavailable(exc):
            pytest.skip(f"Chromium is unavailable for maintenance mechanics: {exc}")
        raise
    assert (tmp_path / "replay/before.json").is_file()
    assert (tmp_path / "replay/after.json").is_file()
    assert "search-submit" in (
        ROOT / "testdata/maintenance/framework/components/catalog_search_form.py"
    ).read_text(encoding="utf-8")
