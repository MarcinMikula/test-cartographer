import pytest

from test_cartographer.expansion.enums import ExpansionDisposition, ExpansionPlanStatus
from test_cartographer.expansion.planner import build_expansion_plan
from test_cartographer.proactive_regression.enums import AutomationImpact, ChangeDisposition


def test_stale_mapped_sort_is_reobserved_not_reused(expansion_plan):
    target = next(item for item in expansion_plan.items if item.source_id == "el_sort_results")
    assert target.disposition is ExpansionDisposition.REOBSERVE
    assert expansion_plan.reobserve_count == 1
    assert expansion_plan.blocked_count == 0


def test_bootstrap_is_reused_but_new_process_meaning_is_not_inherited(expansion_plan):
    assert expansion_plan.bootstrap_questions_repeated is False
    assert expansion_plan.reuse_count >= 6
    assert expansion_plan.ask_human_count == 3
    process_name = next(item for item in expansion_plan.items if item.id == "exp_process_name")
    assert process_name.disposition is ExpansionDisposition.REVIEW


def test_base_context_fingerprint_drift_is_rejected(
    expansion_request,
    base_context,
    framework_snapshot,
    observation_inventory,
    drift_report,
    fixed_now,
):
    changed = base_context.model_copy(update={"title": "Changed after request"})
    with pytest.raises(ValueError, match="fingerprint changed"):
        build_expansion_plan(
            expansion_request,
            changed,
            framework_snapshot,
            plan_id="exp_changed",
            created_at=fixed_now,
            inventory=observation_inventory,
            change_report=drift_report,
        )


def test_missing_proactive_target_blocks_expansion(
    expansion_request,
    base_context,
    framework_snapshot,
    observation_inventory,
    drift_report,
    drift_observation,
    fixed_now,
):
    missing = drift_observation.model_copy(
        update={
            "disposition": ChangeDisposition.MISSING,
            "automation_impact": AutomationImpact.MAPPED_CONTEXT_STALE,
            "expected_locator_visible_count": 0,
            "semantic_visible_count": 0,
            "current_locator_strategy": None,
            "current_locator_value": None,
            "observed_attributes": (),
        }
    )
    report = drift_report.model_copy(
        update={
            "observations": (missing,),
            "locator_drift_count": 0,
            "missing_count": 1,
            "mapped_context_stale_count": 1,
        }
    )
    plan = build_expansion_plan(
        expansion_request,
        base_context,
        framework_snapshot,
        plan_id="exp_missing",
        created_at=fixed_now,
        inventory=observation_inventory,
        change_report=report,
    )
    assert plan.status is ExpansionPlanStatus.BLOCKED
    assert plan.blocked_count == 1


def test_mapped_target_absent_from_base_context_is_observe_new(
    expansion_request,
    base_context,
    framework_snapshot,
    observation_inventory,
    fixed_now,
):
    request = expansion_request.model_copy(update={"proactive_report_id": None})
    plan = build_expansion_plan(
        request,
        base_context,
        framework_snapshot,
        plan_id="exp_observe_new",
        created_at=fixed_now,
        inventory=observation_inventory,
        change_report=None,
    )
    target = next(item for item in plan.items if item.source_id == "el_sort_results")
    assert target.disposition is ExpansionDisposition.OBSERVE_NEW
    assert plan.observe_new_count == 1
