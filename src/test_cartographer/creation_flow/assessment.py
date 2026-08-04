"""Deterministic assessment of integrated Creation Flow mechanics and demo readiness."""

from test_cartographer.creation_flow.enums import CreationFlowStatus
from test_cartographer.creation_flow.models import CreationFlowAssessment, CreationFlowRun


def assess_creation_flow(run: CreationFlowRun) -> CreationFlowAssessment:
    mechanics_blockers: list[str] = []
    if run.status is not CreationFlowStatus.PASSED:
        mechanics_blockers.append("flow_not_passed")
    if run.live_llm_call_count < 3:
        mechanics_blockers.append("live_llm_boundary_missing")
    if run.passed_test_count < 1:
        mechanics_blockers.append("runnable_test_missing")
    if not run.full_traceability:
        mechanics_blockers.append("traceability_incomplete")
    if not run.original_framework_unchanged:
        mechanics_blockers.append("source_framework_modified")
    if run.measured_savings_claimed:
        mechanics_blockers.append("unsupported_savings_claim")

    mechanics_verified = not mechanics_blockers
    external_demo_blockers: list[str] = []
    if not mechanics_verified:
        external_demo_blockers.append("creation_mechanics_not_verified")
    if not run.interactive_human_used_during_verifier:
        external_demo_blockers.append("interactive_human_trigger_missing")

    return CreationFlowAssessment(
        run_id=run.id,
        creation_mechanics_verified=mechanics_verified,
        ready_for_human_trigger_integration=mechanics_verified,
        ready_for_external_user_demo=not external_demo_blockers,
        mechanics_blockers=tuple(mechanics_blockers),
        external_demo_blockers=tuple(external_demo_blockers),
        evidence_statements=(
            "The integrated engine begins from one short request.",
            "Three local-LLM turns assist intake and ambiguity phrasing.",
            "Human answers and decisions are represented by explicit fixtures.",
            "The accepted context produces one reviewed patch and one passing test.",
            "The verifier does not include an interactive human trigger.",
            "No percentage of saved work is claimed.",
        ),
    )
