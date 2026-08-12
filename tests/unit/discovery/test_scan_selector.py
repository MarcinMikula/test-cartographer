from pathlib import Path

from test_cartographer.discovery.capture import _scan_selector
from test_cartographer.discovery.io import load_discovery_plan

ROOT = Path(__file__).resolve().parents[3]


def test_catalog_plan_keeps_original_bounded_scan_without_native_headings():
    plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")

    selector = _scan_selector(plan)

    assert "h1" not in selector
    assert "h2" not in selector
    assert "input" in selector
    assert "button" in selector


def test_heading_target_expands_bounded_scan_only_when_requested():
    plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")
    first = plan.targets[0].model_copy(update={"expected_roles": ("heading",)})
    plan = plan.model_copy(update={"targets": (first, *plan.targets[1:])})

    selector = _scan_selector(plan)

    assert "h1" in selector
    assert "h6" in selector
    assert "input" in selector
    assert "button" in selector
