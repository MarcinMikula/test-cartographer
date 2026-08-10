from datetime import timedelta

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationAuthenticationRequirement,
    ValidationFindingKind,
    ValidationLifecycleStage,
    ValidationRunCompletion,
    ValidationStopCondition,
    ValidationTargetControl,
    ValidationTargetDifficulty,
    ValidationWorkflowKind,
)
from test_cartographer.validation.models import (
    ValidationEvidenceEntry,
    ValidationEvidenceManifest,
    ValidationFinding,
    ValidationFindingReference,
    ValidationProductReference,
    ValidationRun,
    ValidationTargetProfile,
    ValidationTiming,
)
from test_cartographer.validation.service import create_validation_run


def target(**updates):
    values = dict(
        id="external_target",
        label="External target",
        target_url="https://example.test/catalog",
        difficulty=ValidationTargetDifficulty.SIMPLE,
        control=ValidationTargetControl.EXTERNAL_STABLE,
        authentication=ValidationAuthenticationRequirement.NONE,
        process_label="Search catalog",
        allowed_actions=("open page",),
        authorization_statement="Bounded public validation approved.",
        operator_authorization_confirmed=True,
        target_fingerprint="0" * 64,
    )
    values.update(updates)
    return ValidationTargetProfile(**values)


def test_target_rejects_non_http_url():
    with pytest.raises(ValidationError):
        target(target_url="file:///tmp/page.html")


def test_target_rejects_credentials():
    with pytest.raises(ValidationError):
        target(target_url="https://user:pass@example.test/catalog")


def test_target_rejects_query():
    with pytest.raises(ValidationError):
        target(target_url="https://example.test/catalog?token=x")


def test_target_rejects_fragment():
    with pytest.raises(ValidationError):
        target(target_url="https://example.test/catalog#results")


def test_target_actions_must_be_unique():
    with pytest.raises(ValidationError):
        target(allowed_actions=("open page", "open page"))


def test_target_requires_explicit_authorization():
    with pytest.raises(ValidationError):
        target(operator_authorization_confirmed=False)


def test_product_ref_requires_exact_git_sha():
    with pytest.raises(ValidationError):
        ValidationProductReference(git_commit="abc123", version="0.16.0")


def test_timing_rejects_negative_value():
    with pytest.raises(ValidationError):
        ValidationTiming(
            elapsed_seconds=1,
            setup_active_seconds=-1,
            intake_active_seconds=0,
            review_active_seconds=0,
            correction_active_seconds=0,
            system_wait_seconds=0,
        )


def test_operator_active_time_is_separate_sum(timing):
    assert timing.operator_active_seconds == 15.0


def test_finding_rejects_duplicate_evidence_ids(accepted_at):
    with pytest.raises(ValidationError):
        ValidationFinding(
            id="finding_one",
            observed_at=accepted_at,
            lifecycle_stage=ValidationLifecycleStage.INTAKE,
            kind=ValidationFindingKind.FRICTION,
            observation="Repeated operator review.",
            evidence_ids=("evidence_one", "evidence_one"),
            could_continue=True,
        )


def test_safety_stop_requires_condition(accepted_at):
    with pytest.raises(ValidationError):
        ValidationFinding(
            id="finding_stop",
            observed_at=accepted_at,
            lifecycle_stage=ValidationLifecycleStage.BROWSER_DISCOVERY,
            kind=ValidationFindingKind.SAFETY_STOP,
            observation="Target left approved boundary.",
            could_continue=False,
        )


def test_safety_stop_must_not_continue(accepted_at):
    with pytest.raises(ValidationError):
        ValidationFinding(
            id="finding_stop",
            observed_at=accepted_at,
            lifecycle_stage=ValidationLifecycleStage.BROWSER_DISCOVERY,
            kind=ValidationFindingKind.SAFETY_STOP,
            observation="Target left approved boundary.",
            could_continue=True,
            stop_condition=ValidationStopCondition.OUTSIDE_APPROVED_TARGET,
        )


def test_non_safety_finding_rejects_stop_condition(accepted_at):
    with pytest.raises(ValidationError):
        ValidationFinding(
            id="finding_failure",
            observed_at=accepted_at,
            lifecycle_stage=ValidationLifecycleStage.BROWSER_DISCOVERY,
            kind=ValidationFindingKind.FAILURE,
            observation="No candidate found.",
            could_continue=False,
            stop_condition=ValidationStopCondition.OUTSIDE_APPROVED_TARGET,
        )


def bare_run(
    *,
    target_profile,
    accepted_at,
    runtime,
    timing,
    operator_assessment,
    product_ref,
    **updates,
):
    values = dict(
        id="validation_run_two",
        target_profile_id=target_profile.id,
        target_profile_fingerprint=target_profile.target_fingerprint,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        started_at=accepted_at,
        finished_at=accepted_at + timedelta(seconds=30),
        runtime=runtime,
        timing=timing,
        findings=(),
        completion=ValidationRunCompletion.COMPLETED,
        operator_assessment=operator_assessment,
        run_fingerprint="0" * 64,
    )
    values.update(updates)
    return ValidationRun(**values)


def test_run_rejects_naive_timestamp(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            started_at=accepted_at.replace(tzinfo=None),
        )


def test_run_rejects_finished_before_start(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            finished_at=accepted_at - timedelta(seconds=1),
        )


def test_testcartographer_run_requires_product_ref(
    target_profile, accepted_at, runtime, timing, operator_assessment
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=None,
        )


def test_baseline_run_rejects_testcartographer_product_ref(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            workflow=ValidationWorkflowKind.MANUAL_AUTOMATION_AIDS,
        )


def test_predecessor_must_differ_from_current_run(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            predecessor_run_id="validation_run_two",
        )


def test_addressed_finding_requires_predecessor(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            addressed_findings=(
                ValidationFindingReference(
                    run_id="validation_run_one", finding_id="finding_one"
                ),
            ),
        )


def test_addressed_finding_must_belong_to_predecessor(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            predecessor_run_id="validation_run_one",
            addressed_findings=(
                ValidationFindingReference(
                    run_id="different_run", finding_id="finding_one"
                ),
            ),
        )


def test_duplicate_finding_ids_are_rejected(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    finding = ValidationFinding(
        id="finding_one",
        observed_at=accepted_at,
        lifecycle_stage=ValidationLifecycleStage.INTAKE,
        kind=ValidationFindingKind.FRICTION,
        observation="Repeated review.",
        could_continue=True,
    )
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            findings=(finding, finding),
        )


def test_stopped_run_requires_condition(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            completion=ValidationRunCompletion.STOPPED,
        )


def test_completed_run_rejects_stop_condition(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            stop_condition=ValidationStopCondition.POLICY_DECISION_REQUIRED,
        )


def test_safety_finding_requires_stopped_run(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    finding = ValidationFinding(
        id="finding_stop",
        observed_at=accepted_at,
        lifecycle_stage=ValidationLifecycleStage.GENERAL,
        kind=ValidationFindingKind.SAFETY_STOP,
        observation="Policy decision required.",
        could_continue=False,
        stop_condition=ValidationStopCondition.POLICY_DECISION_REQUIRED,
    )
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            findings=(finding,),
        )


def test_stopped_run_condition_matches_safety_finding(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    finding = ValidationFinding(
        id="finding_stop",
        observed_at=accepted_at,
        lifecycle_stage=ValidationLifecycleStage.GENERAL,
        kind=ValidationFindingKind.SAFETY_STOP,
        observation="Policy decision required.",
        could_continue=False,
        stop_condition=ValidationStopCondition.POLICY_DECISION_REQUIRED,
    )
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            findings=(finding,),
            completion=ValidationRunCompletion.STOPPED,
            stop_condition=ValidationStopCondition.OUTSIDE_APPROVED_TARGET,
        )



def test_finding_timestamp_must_fall_within_run(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    finding = ValidationFinding(
        id="finding_late",
        observed_at=accepted_at + timedelta(minutes=2),
        lifecycle_stage=ValidationLifecycleStage.GENERAL,
        kind=ValidationFindingKind.FRICTION,
        observation="Observation outside run window.",
        could_continue=True,
    )
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            findings=(finding,),
        )


def test_stopped_run_requires_safety_stop_finding(
    target_profile, accepted_at, runtime, timing, operator_assessment, product_ref
):
    with pytest.raises(ValidationError):
        bare_run(
            target_profile=target_profile,
            accepted_at=accepted_at,
            runtime=runtime,
            timing=timing,
            operator_assessment=operator_assessment,
            product_ref=product_ref,
            completion=ValidationRunCompletion.STOPPED,
            stop_condition=ValidationStopCondition.POLICY_DECISION_REQUIRED,
        )

def evidence(path, *, finding_ids=()):
    return ValidationEvidenceEntry(
        relative_path=path,
        sha256="a" * 64,
        artefact_kind=ValidationArtefactKind.CONTEXT_BUNDLE,
        sensitivity=SensitivityLevel.INTERNAL,
        producer=ValidationArtefactProducer.TESTCARTOGRAPHER,
        finding_ids=finding_ids,
    )


def test_evidence_rejects_absolute_path():
    with pytest.raises(ValidationError):
        evidence("/evidence/context.json")


def test_evidence_rejects_backslash_path():
    with pytest.raises(ValidationError):
        evidence(r"evidence\context.json")


def test_evidence_rejects_parent_traversal():
    with pytest.raises(ValidationError):
        evidence("evidence/../context.json")


def test_evidence_finding_ids_must_be_unique():
    with pytest.raises(ValidationError):
        evidence("evidence/context.json", finding_ids=("finding_one", "finding_one"))


def test_manifest_rejects_duplicate_paths():
    first = evidence("evidence/context.json")
    with pytest.raises(ValidationError):
        ValidationEvidenceManifest(
            id="validation_manifest",
            target_profile_id="external_target",
            target_profile_fingerprint="a" * 64,
            validation_run_id="validation_run",
            validation_run_fingerprint="b" * 64,
            entries=(first, first),
            package_fingerprint="c" * 64,
        )


def test_manifest_requires_sorted_paths():
    with pytest.raises(ValidationError):
        ValidationEvidenceManifest(
            id="validation_manifest",
            target_profile_id="external_target",
            target_profile_fingerprint="a" * 64,
            validation_run_id="validation_run",
            validation_run_fingerprint="b" * 64,
            entries=(
                evidence("evidence/z.json"),
                evidence("evidence/a.json"),
            ),
            package_fingerprint="c" * 64,
        )


def test_contracts_reject_extra_fields():
    with pytest.raises(ValidationError):
        target(unexpected="nope")
