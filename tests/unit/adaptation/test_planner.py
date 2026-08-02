from datetime import datetime, timezone

import pytest

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    PythonSymbolKind,
)
from test_cartographer.adaptation.models import FrameworkSnapshot
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.synthesis.enums import ProposalReviewDecision, SynthesisRunStatus


def _build(run, profile, snapshot):
    return build_adaptation_plan(
        run,
        profile,
        snapshot,
        plan_id="adapt_public_search",
        created_at=datetime(2026, 8, 2, 12, 5, tzinfo=timezone.utc),
    )


def test_plan_maps_accepted_proposal_to_exact_framework_targets(
    accepted_synthesis_run,
    workspace_profile,
    framework_snapshot,
):
    plan = _build(accepted_synthesis_run, workspace_profile, framework_snapshot)
    actual = [
        (item.kind.value, item.target_path, item.symbol_name)
        for item in plan.operations
    ]
    assert actual == [
        ("create_file", "pages/catalog_page.py", "CatalogPage"),
        ("create_file", "components/catalog_search_form.py", "CatalogSearchForm"),
        ("add_symbol", "tests/e2e/conftest.py", "catalog_context"),
        ("create_file", "tests/e2e/test_search_catalog.py", "test_search_catalog"),
    ]
    assert plan.operations[-1].depends_on == (
        "adapt_page_01",
        "adapt_component_01",
        "adapt_fixture_01",
    )
    assert plan.framework_files_modified is False
    assert plan.generated_source_included is False


def test_plan_requires_accepted_synthesis_run(
    accepted_synthesis_run,
    workspace_profile,
    framework_snapshot,
):
    pending = accepted_synthesis_run.model_copy(
        update={
            "status": SynthesisRunStatus.READY_FOR_REVIEW,
            "decision": ProposalReviewDecision.PENDING,
            "reviewed_at": None,
            "review_reason": None,
            "review_seconds": 0.0,
        }
    )
    pending = type(accepted_synthesis_run).model_validate(pending.model_dump(mode="python"))
    with pytest.raises(ValueError, match="accepted synthesis run"):
        _build(pending, workspace_profile, framework_snapshot)


def test_plan_rejects_snapshot_from_other_profile(
    accepted_synthesis_run,
    workspace_profile,
    framework_snapshot,
):
    other = framework_snapshot.model_copy(update={"profile_id": "workspace_other"})
    other = FrameworkSnapshot.model_validate(other.model_dump(mode="python"))
    with pytest.raises(ValueError, match="does not belong"):
        _build(accepted_synthesis_run, workspace_profile, other)


def test_existing_target_symbol_is_reused(
    accepted_synthesis_run,
    workspace_profile,
    framework_snapshot,
):
    extra = {
        "path": "pages/catalog_page.py",
        "kind": "file",
        "size_bytes": 20,
        "sha256": "1" * 64,
        "python_symbols": [
            {
                "kind": PythonSymbolKind.CLASS.value,
                "name": "CatalogPage",
                "bases": ["BasePage"],
                "method_names": [],
            }
        ],
    }
    payload = framework_snapshot.model_dump(mode="json")
    payload["entries"].append(extra)
    snapshot = FrameworkSnapshot.model_validate(payload)
    plan = _build(accepted_synthesis_run, workspace_profile, snapshot)
    assert plan.operations[0].kind is AdaptationOperationKind.REUSE_SYMBOL


def test_existing_file_without_target_symbol_gets_add_symbol(
    accepted_synthesis_run,
    workspace_profile,
    framework_snapshot,
):
    plan = _build(accepted_synthesis_run, workspace_profile, framework_snapshot)
    fixture = next(
        item for item in plan.operations
        if item.target_path == "tests/e2e/conftest.py"
    )
    assert fixture.kind is AdaptationOperationKind.ADD_SYMBOL
