from pathlib import Path

import pytest

from test_cartographer.proactive_regression.enums import ChangeDisposition
from test_cartographer.proactive_regression.runner import run_scripted_proactive_regression

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.browser
def test_green_framework_probe_does_not_hide_uncovered_locator_drift(tmp_path) -> None:
    run = run_scripted_proactive_regression(
        inventory_path=ROOT / "testdata/proactive/inventory/public_catalog.json",
        profile_path=ROOT / "testdata/proactive/profile/bounded_public.json",
        framework_root=ROOT / "testdata/proactive/framework",
        application_root=ROOT / "testdata/proactive/browser",
        output_dir=tmp_path,
    )
    assert run.baseline_probe.passed and run.current_probe.passed
    assert run.report.locator_drift_count == 1


@pytest.mark.browser
def test_reference_scan_keeps_one_mapped_element_stable(tmp_path) -> None:
    run = run_scripted_proactive_regression(
        inventory_path=ROOT / "testdata/proactive/inventory/public_catalog.json",
        profile_path=ROOT / "testdata/proactive/profile/bounded_public.json",
        framework_root=ROOT / "testdata/proactive/framework",
        application_root=ROOT / "testdata/proactive/browser",
        output_dir=tmp_path,
    )
    stable = [item for item in run.report.observations if item.disposition is ChangeDisposition.UNCHANGED]
    assert len(stable) == 1


@pytest.mark.browser
def test_reference_scan_persists_no_raw_frontend_artifact(tmp_path) -> None:
    run_scripted_proactive_regression(
        inventory_path=ROOT / "testdata/proactive/inventory/public_catalog.json",
        profile_path=ROOT / "testdata/proactive/profile/bounded_public.json",
        framework_root=ROOT / "testdata/proactive/framework",
        application_root=ROOT / "testdata/proactive/browser",
        output_dir=tmp_path,
    )
    names = {path.name for path in tmp_path.iterdir()}
    assert names == {"proactive-regression-run.json"}
