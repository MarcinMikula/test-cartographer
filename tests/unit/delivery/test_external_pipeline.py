from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationReviewDecision, AdaptationTargetKind
from test_cartographer.adaptation.io import load_workspace_profile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.enums import ActionKind
from test_cartographer.creation_flow.external_template import (
    render_external_single_page_proposal,
)
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.io import load_generation_profile
from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision
from test_cartographer.synthesis.io import load_synthesis_request
from test_cartographer.synthesis.models import BoundedSynthesisRequest
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[3]
FRAMEWORK_ROOT = ROOT / "testdata/framework/reference"


def _external_request() -> BoundedSynthesisRequest:
    source = load_synthesis_request(ROOT / "testdata/synthesis/request/public_search.json")
    navigate = source.steps[0]
    read = source.steps[-1].model_copy(update={"order": 2})
    assert navigate.action.kind is ActionKind.NAVIGATE
    assert read.action.kind is ActionKind.READ

    heading = next(item for item in source.elements if item.id == "el_results_heading")
    heading = heading.model_copy(
        update={
            "id": "el_expected_heading",
            "name": heading.name.model_copy(update={"value": "Driving licence codes"}),
            "semantic_role": heading.semantic_role.model_copy(update={"value": "heading"}),
            "primary_locator": heading.primary_locator.model_copy(
                update={
                    "id": "loc_expected_heading",
                    "value": heading.primary_locator.value.model_copy(
                        update={"value": "heading:Driving licence codes"}
                    ),
                }
            ),
        }
    )
    read = read.model_copy(
        update={
            "action": read.action.model_copy(
                update={"target_element_id": heading.id, "test_data_id": None}
            )
        }
    )
    outcome = source.outcomes[0].model_copy(
        update={"related_element_ids": (heading.id,)}
    )
    page = source.pages[0].model_copy(
        update={
            "name": source.pages[0].name.model_copy(
                update={"value": "Driving licence codes"}
            ),
            "component_ids": (),
            "element_ids": (heading.id,),
        }
    )
    updated = source.model_copy(
        update={
            "process_name": source.process_name.model_copy(
                update={"value": "Driving licence codes"}
            ),
            "steps": (navigate, read),
            "outcomes": (outcome,),
            "pages": (page,),
            "components": (),
            "elements": (heading,),
            "test_data": (),
        }
    )
    return BoundedSynthesisRequest.model_validate(updated.model_dump(mode="python"))


def test_external_single_page_reaches_exact_source_patch_without_catalog_assumptions():
    now = datetime(2026, 8, 12, 14, 0, tzinfo=timezone.utc)
    request = _external_request()

    synthesis = run_synthesis(
        request,
        ReplaySynthesisAdapter(render_external_single_page_proposal(request)),
        run_id="syn_external_pipeline",
        started_at=now,
        completed_at=now,
    )
    synthesis = review_synthesis_run(
        synthesis,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=now,
        reason="Test operator accepted the deterministic external proposal.",
    )

    workspace = load_workspace_profile(
        ROOT / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    snapshot = inspect_framework(
        FRAMEWORK_ROOT,
        workspace,
        snapshot_id="snapshot_external_pipeline",
        captured_at=now,
    )
    plan = build_adaptation_plan(
        synthesis,
        workspace,
        snapshot,
        plan_id="adapt_external_pipeline",
        created_at=now,
    )
    plan = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=now,
        reason="Test operator accepted the deterministic repository plan.",
    )
    generation = load_generation_profile(
        ROOT / "profiles/delivery/external_public_single_page.json"
    )

    patch = build_code_patch(
        synthesis,
        plan,
        workspace,
        generation,
        snapshot,
        FRAMEWORK_ROOT,
        patch_id="patch_external_pipeline",
        created_at=now,
    )

    changed_kinds = {change.target_kind for change in patch.changes}
    assert AdaptationTargetKind.PAGE in changed_kinds
    assert AdaptationTargetKind.TEST in changed_kinds
    assert AdaptationTargetKind.COMPONENT not in changed_kinds

    combined = "\n".join(change.content for change in patch.changes)
    assert "DrivingLicenceCodesPage" in combined
    assert "get_by_role('heading', name='Driving licence codes')" in combined
    assert "to_be_visible()" in combined
    assert "expected_value = 'Driving licence codes'" in combined
    assert "assert str(read_expected_heading_value).strip() == expected_value" in combined
    assert "TEST_CARTOGRAPHER_TARGET_URL" in combined
    assert "CatalogSearchForm" not in combined
    assert "search_query" not in combined


def test_external_rich_single_page_reaches_component_and_result_assertion_patch():
    now = datetime(2026, 8, 16, 8, 0, tzinfo=timezone.utc)
    source = load_synthesis_request(
        ROOT / "testdata/synthesis/request/public_search.json"
    )
    result_list = next(item for item in source.elements if item.id == "el_results_list")
    outcome = source.outcomes[0].model_copy(
        update={"related_element_ids": (result_list.id,)}
    )
    request = BoundedSynthesisRequest.model_validate(
        source.model_copy(update={"outcomes": (outcome,)}).model_dump(mode="python")
    )

    synthesis = run_synthesis(
        request,
        ReplaySynthesisAdapter(render_external_single_page_proposal(request)),
        run_id="syn_external_rich_pipeline",
        started_at=now,
        completed_at=now,
    )
    synthesis = review_synthesis_run(
        synthesis,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=now,
        reason="Test operator accepted the deterministic rich external proposal.",
    )

    workspace = load_workspace_profile(
        ROOT / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    snapshot = inspect_framework(
        FRAMEWORK_ROOT,
        workspace,
        snapshot_id="snapshot_external_rich_pipeline",
        captured_at=now,
    )
    plan = build_adaptation_plan(
        synthesis,
        workspace,
        snapshot,
        plan_id="adapt_external_rich_pipeline",
        created_at=now,
    )
    plan = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=now,
        reason="Test operator accepted the deterministic repository plan.",
    )
    generation = load_generation_profile(
        ROOT / "testdata/delivery/profile/public_search_generation.json"
    )

    patch = build_code_patch(
        synthesis,
        plan,
        workspace,
        generation,
        snapshot,
        FRAMEWORK_ROOT,
        patch_id="patch_external_rich_pipeline",
        created_at=now,
    )

    changed_kinds = {change.target_kind for change in patch.changes}
    assert AdaptationTargetKind.PAGE in changed_kinds
    assert AdaptationTargetKind.COMPONENT in changed_kinds
    assert AdaptationTargetKind.TEST in changed_kinds

    combined = "\n".join(change.content for change in patch.changes)
    assert "CatalogSearchPage" in combined
    assert "CatalogSearchFormComponent" in combined
    assert ".fill(value)" in combined
    assert ".click()" in combined
    assert ".inner_text()" in combined
    assert "assert expected_fragment in" in combined
    assert "TEST_CARTOGRAPHER_CATALOG_URL" in combined
