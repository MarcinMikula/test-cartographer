from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationReviewDecision
from test_cartographer.adaptation.io import load_workspace_profile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.io import load_context
from test_cartographer.creation_flow.template import render_reference_pom_proposal
from test_cartographer.delivery.enums import PatchReviewDecision
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.io import load_generation_profile
from test_cartographer.delivery.review import review_code_patch
from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import build_synthesis_request
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc)


def test_reference_creation_template_reaches_exact_patch() -> None:
    context = load_context(ROOT / "testdata/context/synthesis_ready/public_search_flow.json")
    request = build_synthesis_request(context, request_id="synreq_creation_test", created_at=NOW)
    run = run_synthesis(
        request,
        ReplaySynthesisAdapter(render_reference_pom_proposal(request)),
        run_id="synrun_creation_test",
        started_at=NOW,
        completed_at=NOW + timedelta(seconds=1),
    )
    run = review_synthesis_run(
        run,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=NOW + timedelta(seconds=2),
        reason="Accepted for integration testing.",
    )
    workspace = load_workspace_profile(ROOT / "testdata/adaptation/profile/qa_automation_framework.json")
    framework = ROOT / "testdata/framework/reference"
    snapshot = inspect_framework(framework, workspace, snapshot_id="snapshot_creation_test", captured_at=NOW)
    plan = build_adaptation_plan(run, workspace, snapshot, plan_id="adapt_creation_test", created_at=NOW)
    plan = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=NOW + timedelta(seconds=3),
        reason="Accepted for integration testing.",
    )
    patch = build_code_patch(
        run,
        plan,
        workspace,
        load_generation_profile(ROOT / "testdata/delivery/profile/public_search_generation.json"),
        snapshot,
        framework,
        patch_id="patch_creation_test",
        created_at=NOW,
    )
    patch = review_code_patch(
        patch,
        decision=PatchReviewDecision.ACCEPTED,
        reviewed_at=NOW + timedelta(seconds=4),
        reason="Accepted for integration testing.",
    )

    assert len(patch.changes) == 4
    assert {change.target_path for change in patch.changes} == {
        "pages/catalog_page.py",
        "components/catalog_search_form.py",
        "tests/e2e/conftest.py",
        "tests/e2e/test_search_catalog.py",
    }
    assert patch.live_llm_used is False


def test_exact_sprint9_context_reaches_patch_after_explicit_handoff() -> None:
    from test_cartographer.creation_flow.handoff import confirm_synthesis_handoff
    from test_cartographer.delivery.models import TestDataBinding

    context = load_context(
        ROOT / "testdata/creation_flow/context/public_catalog_discovered.json"
    )
    context = confirm_synthesis_handoff(
        context,
        confirmed_at=NOW,
    )
    request = build_synthesis_request(
        context,
        request_id="synreq_creation_exact",
        created_at=NOW,
    )
    run = run_synthesis(
        request,
        ReplaySynthesisAdapter(render_reference_pom_proposal(request)),
        run_id="synrun_creation_exact",
        started_at=NOW,
        completed_at=NOW + timedelta(seconds=1),
    )
    run = review_synthesis_run(
        run,
        decision=ProposalReviewDecision.ACCEPTED,
        reviewed_at=NOW + timedelta(seconds=2),
        reason="Accepted exact Sprint 9 handoff for integration testing.",
    )
    workspace = load_workspace_profile(
        ROOT / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    framework = ROOT / "testdata/framework/reference"
    snapshot = inspect_framework(
        framework,
        workspace,
        snapshot_id="snapshot_creation_exact",
        captured_at=NOW,
    )
    plan = build_adaptation_plan(
        run,
        workspace,
        snapshot,
        plan_id="adapt_creation_exact",
        created_at=NOW,
    )
    plan = review_adaptation_plan(
        plan,
        decision=AdaptationReviewDecision.ACCEPTED,
        reviewed_at=NOW + timedelta(seconds=3),
        reason="Accepted exact Sprint 9 handoff for integration testing.",
    )
    generation_profile = load_generation_profile(
        ROOT / "testdata/delivery/profile/public_search_generation.json"
    )
    source_binding = generation_profile.test_data_bindings[0]
    generation_profile = generation_profile.model_copy(
        update={
            "id": "generation_creation_exact",
            "test_data_bindings": (
                TestDataBinding(
                    test_data_id=request.test_data[0].id,
                    fixture_key=source_binding.fixture_key,
                    value=source_binding.value,
                    sensitivity=source_binding.sensitivity,
                    secret=False,
                ),
            ),
        }
    )
    patch = build_code_patch(
        run,
        plan,
        workspace,
        generation_profile,
        snapshot,
        framework,
        patch_id="patch_creation_exact",
        created_at=NOW,
    )

    assert len(request.steps) == 4
    assert len(request.elements) == 3
    assert request.test_data[0].id == "td_catalog_query"
    assert len(patch.changes) == 4
    assert {change.target_path for change in patch.changes} == {
        "pages/catalog_page.py",
        "components/catalog_search_form.py",
        "tests/e2e/conftest.py",
        "tests/e2e/test_search_catalog.py",
    }
