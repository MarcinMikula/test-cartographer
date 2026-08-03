"""Creation-lifecycle measurement after framework verification."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.adaptation.enums import AdaptationPlanStatus, AdaptationTargetKind
from test_cartographer.adaptation.models import AdaptationPlan
from test_cartographer.delivery.enums import (
    CodePatchStatus,
    CreationEvaluationStatus,
    SourceChangeKind,
)
from test_cartographer.delivery.models import (
    CodePatch,
    CreationEvaluation,
    PatchApplicationReport,
    VerificationResult,
)
from test_cartographer.synthesis.enums import SynthesisRunStatus
from test_cartographer.synthesis.models import SynthesisRun


def build_creation_evaluation(
    run: SynthesisRun,
    plan: AdaptationPlan,
    patch: CodePatch,
    application: PatchApplicationReport,
    *,
    evaluation_id: str,
    completed_at: datetime,
    target_test: str,
    collected_test_count: int,
    passed_test_count: int,
    verification_results: tuple[VerificationResult, ...],
    verification_seconds: float,
    time_to_first_runnable_test_seconds: float,
    original_framework_unchanged: bool,
    corrections: tuple[str, ...] = (),
) -> CreationEvaluation:
    if run.status is not SynthesisRunStatus.ACCEPTED:
        raise ValueError("creation evaluation requires an accepted synthesis run")
    if plan.status is not AdaptationPlanStatus.ACCEPTED:
        raise ValueError("creation evaluation requires an accepted adaptation plan")
    if patch.status is not CodePatchStatus.ACCEPTED:
        raise ValueError("creation evaluation requires an accepted code patch")
    if patch.plan_id != plan.id or patch.synthesis_run_id != run.id:
        raise ValueError("creation evaluation artefacts are not linked")
    if application.patch_id != patch.id:
        raise ValueError("application report does not belong to the code patch")

    target_kinds = {change.target_kind for change in patch.changes}
    all_verification_passed = all(item.passed for item in verification_results)
    architecture_checks = {
        "page_object_generated": AdaptationTargetKind.PAGE in target_kinds,
        "component_generated": AdaptationTargetKind.COMPONENT in target_kinds,
        "fixture_generated": AdaptationTargetKind.FIXTURE in target_kinds,
        "test_generated": AdaptationTargetKind.TEST in target_kinds,
        "meaningful_test_assertion_present": AdaptationTargetKind.TEST in target_kinds,
        "framework_execution_independent": not patch.live_llm_used,
        "original_framework_unchanged": original_framework_unchanged,
    }
    passed = (
        collected_test_count >= 1
        and passed_test_count >= 1
        and all_verification_passed
        and all(architecture_checks.values())
    )
    return CreationEvaluation(
        id=evaluation_id,
        context_id=patch.context_id,
        synthesis_run_id=run.id,
        adaptation_plan_id=plan.id,
        code_patch_id=patch.id,
        application_report_id=application.id,
        completed_at=completed_at,
        status=(CreationEvaluationStatus.PASSED if passed else CreationEvaluationStatus.FAILED),
        target_test=target_test,
        generated_file_count=sum(
            change.kind is SourceChangeKind.CREATE_FILE for change in patch.changes
        ),
        modified_file_count=sum(
            change.kind is SourceChangeKind.APPEND_SYMBOL for change in patch.changes
        ),
        reused_symbol_count=len(patch.reused_targets),
        collected_test_count=collected_test_count,
        passed_test_count=passed_test_count,
        synthesis_review_seconds=run.review_seconds,
        adaptation_review_seconds=plan.review_seconds,
        code_review_seconds=patch.review_seconds,
        application_seconds=application.application_seconds,
        verification_seconds=verification_seconds,
        time_to_first_runnable_test_seconds=time_to_first_runnable_test_seconds,
        verification_results=verification_results,
        corrections=corrections,
        **architecture_checks,
    )
