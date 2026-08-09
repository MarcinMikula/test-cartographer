"""Deterministic assessment for controlled incremental expansion."""

from test_cartographer.expansion.enums import ExpansionRunStatus
from test_cartographer.expansion.models import ExpansionAssessment, ExpansionRun


def assess_expansion_run(run: ExpansionRun) -> ExpansionAssessment:
    blockers: list[str] = []
    if run.status is not ExpansionRunStatus.PASSED:
        blockers.append("run did not finish in passed state")
    if run.bootstrap_questions_repeated:
        blockers.append("bootstrap questions were repeated")
    if run.reused_knowledge_item_count < 1:
        blockers.append("no accepted application knowledge was reused")
    if run.reobservation_count < 1:
        blockers.append("no stale expansion evidence was re-observed")
    if run.blocked_item_count:
        blockers.append("expansion retained blocked items")
    if not run.candidate_context_reviewed:
        blockers.append("candidate expanded context was not reviewed")
    if not run.existing_creation_pipeline_reused:
        blockers.append("existing creation/adaptation/delivery pipeline was not reused")
    if run.framework_symbols_extended < 1 or not run.existing_page_object_extended:
        blockers.append("existing Page Object was not extended")
    if not run.method_property_collision_protection:
        blockers.append("method/property collision protection was not evidenced")
    if not run.hash_bound_source_replacement_used:
        blockers.append("hash-bound existing-file replacement was not evidenced")
    if not run.source_drift_preflight_enforced:
        blockers.append("source-drift preflight enforcement was not evidenced")
    if run.existing_tests_preserved < 1:
        blockers.append("existing framework test was not preserved")
    if run.new_tests_added < 1:
        blockers.append("no new process test was added")
    if not run.framework_execution_independent:
        blockers.append("framework execution was not independent of TestCartographer")
    if not run.base_context_unchanged:
        blockers.append("accepted base context was modified during expansion")
    if not run.original_framework_unchanged:
        blockers.append("original framework checkout was modified")
    if run.stale_knowledge_silently_reused:
        blockers.append("stale knowledge was silently reused")
    if run.automatic_context_write_performed:
        blockers.append("expansion performed an unauthorized automatic context write")
    if run.phoenixqa_healing_used:
        blockers.append("expansion crossed into PhoenixQA-style runtime healing")
    if run.raw_page_persisted:
        blockers.append("expansion persisted raw page content")
    if run.measured_savings_claimed:
        blockers.append("single controlled run made an unsupported savings claim")

    verified = not blockers
    controlled_demo_ready = (
        verified
        and run.interactive_human_trigger_used
        and run.headed_browser_used
        and not run.fixture_decisions_used
    )
    return ExpansionAssessment(
        run_id=run.id,
        blockers=tuple(blockers),
        expansion_verified=verified,
        controlled_demo_ready=controlled_demo_ready,
    )
