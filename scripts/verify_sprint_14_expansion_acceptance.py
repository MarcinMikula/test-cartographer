from __future__ import annotations
import argparse
from pathlib import Path
from test_cartographer.expansion.assessment import assess_expansion_run
from test_cartographer.expansion.io import load_expansion_assessment, load_expansion_run

p = argparse.ArgumentParser()
p.add_argument("artifact_dir")
p.add_argument("--require-real", action="store_true")
a = p.parse_args()
root = Path(a.artifact_dir)
run = load_expansion_run(root / "expansion-run.json")
assessment = load_expansion_assessment(root / "expansion-assessment.json")
expected = assess_expansion_run(run)
if assessment != expected:
    raise SystemExit("Persisted ExpansionAssessment does not match deterministic reassessment")
if not assessment.expansion_verified:
    raise SystemExit(f"Expansion blockers: {assessment.blockers}")
if a.require_real and not assessment.controlled_demo_ready:
    raise SystemExit("Run verifies mechanics but is not real-operator controlled-demo evidence")
if a.require_real:
    required = {
        "interactive_human_trigger_used": run.interactive_human_trigger_used,
        "headed_browser_used": run.headed_browser_used,
        "fixture_decisions_used_false": not run.fixture_decisions_used,
        "original_framework_unchanged": run.original_framework_unchanged,
        "base_context_unchanged": run.base_context_unchanged,
        "existing_page_object_extended": run.existing_page_object_extended,
        "hash_bound_source_replacement_used": run.hash_bound_source_replacement_used,
        "source_drift_preflight_enforced": run.source_drift_preflight_enforced,
        "framework_execution_independent": run.framework_execution_independent,
    }
    failed = [key for key, value in required.items() if not value]
    if failed:
        raise SystemExit(f"Real acceptance evidence missing: {failed}")
print(f"Expansion verified: {str(assessment.expansion_verified).lower()}")
print(f"Controlled demo ready: {str(assessment.controlled_demo_ready).lower()}")
print(f"Operator actions: {run.operator_action_count}")
print(f"Process-specific questions: {run.process_specific_questions_asked}")
print(f"Reused knowledge items: {run.reused_knowledge_item_count}")
print(f"Reobservations: {run.reobservation_count}")
print(f"Original framework unchanged: {str(run.original_framework_unchanged).lower()}")
