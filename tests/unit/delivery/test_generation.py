import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.enums import (
    AdaptationPlanStatus,
    AdaptationReviewDecision,
)
from test_cartographer.adaptation.models import AdaptationPlan, FrameworkSnapshot
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.generation import _render_method
from test_cartographer.delivery.models import GenerationProfile
from test_cartographer.context.enums import ActionKind
from test_cartographer.synthesis.enums import ProposalOwnerKind
from test_cartographer.synthesis.models import ProposedAction, ProposedMethod

ROOT = Path(__file__).resolve().parents[3]


def _build(run, plan, workspace_profile, generation_profile, snapshot, root):
    return build_code_patch(
        run,
        plan,
        workspace_profile,
        generation_profile,
        snapshot,
        root,
        patch_id="patch_test_public_search",
        created_at=datetime(2026, 8, 2, 13, 0, tzinfo=timezone.utc),
    )


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_build_maps_every_accepted_operation_to_exact_source_change(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    before = _tree_hash(framework)
    patch = _build(
        accepted_run,
        accepted_plan,
        workspace_profile,
        generation_profile,
        framework_snapshot,
        framework,
    )
    assert [(item.kind.value, item.target_path, item.symbol_name) for item in patch.changes] == [
        ("create_file", "pages/catalog_page.py", "CatalogPage"),
        ("create_file", "components/catalog_search_form.py", "CatalogSearchForm"),
        ("append_symbol", "tests/e2e/conftest.py", "catalog_context"),
        ("create_file", "tests/e2e/test_search_catalog.py", "test_search_catalog"),
    ]
    assert patch.framework_files_modified is False
    assert patch.live_llm_used is False
    assert patch.secret_values_included is False
    assert _tree_hash(framework) == before


def test_generated_source_uses_observed_locators_and_test_owned_assertion(pending_patch):
    rendered = {item.target_path: item.content for item in pending_patch.changes}
    assert "get_by_label('Search catalog')" in rendered["components/catalog_search_form.py"]
    assert "get_by_role('button', name='Search')" in rendered["components/catalog_search_form.py"]
    assert "get_by_test_id('catalog-results')" in rendered["pages/catalog_page.py"]
    assert "get_by_role('heading', name='Search results')" in rendered["pages/catalog_page.py"]
    assert "assert expected_fragment in" in rendered["tests/e2e/test_search_catalog.py"]
    assert "TEST_CARTOGRAPHER_CATALOG_URL" in rendered["tests/e2e/conftest.py"]
    assert "http://" not in "\n".join(rendered.values())
    assert "password" not in "\n".join(rendered.values()).casefold()


def test_generation_requires_human_accepted_plan(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    payload = accepted_plan.model_dump(mode="json")
    payload.update(
        status=AdaptationPlanStatus.READY_FOR_REVIEW.value,
        decision=AdaptationReviewDecision.PENDING.value,
        reviewed_at=None,
        review_reason=None,
        review_seconds=0.0,
    )
    pending = AdaptationPlan.model_validate(payload)
    with pytest.raises(ValueError, match="human-accepted"):
        _build(
            accepted_run,
            pending,
            workspace_profile,
            generation_profile,
            framework_snapshot,
            framework,
        )


def test_generation_rejects_framework_fingerprint_drift(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    (framework / "pages/base_page.py").write_text("# changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="fingerprint changed"):
        _build(
            accepted_run,
            accepted_plan,
            workspace_profile,
            generation_profile,
            framework_snapshot,
            framework,
        )


def test_generation_rejects_missing_explicit_test_data_binding(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    payload = generation_profile.model_dump(mode="json")
    payload["test_data_bindings"] = [
        {
            "test_data_id": "data_other",
            "fixture_key": "other",
            "value": "Other",
            "sensitivity": "public",
            "secret": False,
        }
    ]
    other = GenerationProfile.model_validate(payload)
    with pytest.raises(ValueError, match="missing test-data bindings"):
        _build(
            accepted_run,
            accepted_plan,
            workspace_profile,
            other,
            framework_snapshot,
            framework,
        )


def test_generation_rejects_snapshot_from_another_profile(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    payload = framework_snapshot.model_dump(mode="json")
    payload["profile_id"] = "workspace_other"
    other = FrameworkSnapshot.model_validate(payload)
    with pytest.raises(ValueError, match="does not belong"):
        _build(
            accepted_run,
            accepted_plan,
            workspace_profile,
            generation_profile,
            other,
            framework,
        )


def test_navigation_docstring_describes_method_not_raw_operator_request(
    tmp_path,
    accepted_run,
    accepted_plan,
    workspace_profile,
    generation_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    proposal = accepted_run.proposal
    methods = tuple(
        method.model_copy(
            update={
                "intent": "I want to automate searching for a product and verify results."
            }
        )
        if method.name == "open_catalog"
        else method
        for method in proposal.methods
    )
    updated_proposal = proposal.model_copy(update={"methods": methods})
    updated_run = accepted_run.model_copy(update={"proposal": updated_proposal})
    patch = _build(
        updated_run,
        accepted_plan,
        workspace_profile,
        generation_profile,
        framework_snapshot,
        framework,
    )
    page_source = next(
        change.content
        for change in patch.changes
        if change.target_path == "pages/catalog_page.py"
    )
    assert '"""Open the mapped page through the framework navigation boundary."""' in page_source
    assert "I want to automate searching" not in page_source


def test_exact_patch_formatter_includes_every_source_line(pending_patch) -> None:
    from test_cartographer.interactive_creation.runner import _format_code_patch

    rendered = _format_code_patch(pending_patch)
    assert "Exact source follows. No lines are omitted." in rendered
    assert "End of exact code patch." in rendered
    assert "      ..." not in rendered
    for change in pending_patch.changes:
        assert change.content.rstrip("\n") in rendered
        assert change.content_sha256 in rendered


@pytest.mark.parametrize(
    ("kind", "expected_line", "test_data_id"),
    (
        (ActionKind.SELECT, "self.sort_control.select_option(value)", "data_sort"),
        (ActionKind.CHECK, "self.sort_control.check()", None),
        (ActionKind.UNCHECK, "self.sort_control.uncheck()", None),
    ),
)
def test_generated_method_supports_bounded_rich_external_actions(
    kind,
    expected_line,
    test_data_id,
):
    method = ProposedMethod(
        id=f"method_{kind.value}",
        name=f"{kind.value}_sort",
        owner_kind=ProposalOwnerKind.COMPONENT,
        owner_source_id="cmp_controls",
        intent=f"Use the reviewed {kind.value} action.",
        actions=(
            ProposedAction(
                step_id=f"step_{kind.value}",
                kind=kind,
                target_element_id="el_sort_control",
                locator_id="loc_sort_control",
                test_data_id=test_data_id,
            ),
        ),
    )

    rendered = "\n".join(_render_method(method, None, indent="    "))

    assert expected_line in rendered
