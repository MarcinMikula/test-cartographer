"""Deterministic constructors for validation contracts with canonical fingerprints."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationAuthenticationRequirement,
    ValidationRunCompletion,
    ValidationStopCondition,
    ValidationTargetControl,
    ValidationTargetDifficulty,
    ValidationWorkflowKind,
)
from test_cartographer.validation.fingerprints import (
    compute_package_fingerprint,
    compute_run_fingerprint,
    compute_target_fingerprint,
    validate_run_fingerprint,
    validate_target_fingerprint,
)
from test_cartographer.validation.models import (
    ValidationEvidenceEntry,
    ValidationEvidenceManifest,
    ValidationFinding,
    ValidationFindingReference,
    ValidationOperatorAssessment,
    ValidationProductReference,
    ValidationRun,
    ValidationRuntimeEnvironment,
    ValidationTargetProfile,
    ValidationTiming,
)


def create_validation_target_profile(
    *,
    profile_id: str,
    label: str,
    target_url: str,
    difficulty: ValidationTargetDifficulty,
    control: ValidationTargetControl,
    authentication: ValidationAuthenticationRequirement,
    process_label: str,
    allowed_actions: tuple[str, ...],
    authorization_statement: str,
    operator_authorization_confirmed: bool,
    prohibited_actions: tuple[str, ...] = (),
    cleanup_requirement: str | None = None,
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
) -> ValidationTargetProfile:
    draft = ValidationTargetProfile(
        id=profile_id,
        label=label,
        target_url=target_url,
        difficulty=difficulty,
        control=control,
        authentication=authentication,
        process_label=process_label,
        allowed_actions=allowed_actions,
        prohibited_actions=prohibited_actions,
        cleanup_requirement=cleanup_requirement,
        authorization_statement=authorization_statement,
        operator_authorization_confirmed=operator_authorization_confirmed,
        sensitivity=sensitivity,
        target_fingerprint="0" * 64,
    )
    return draft.model_copy(
        update={"target_fingerprint": compute_target_fingerprint(draft)}
    )


def create_validation_run(
    *,
    run_id: str,
    target_profile: ValidationTargetProfile,
    workflow: ValidationWorkflowKind,
    started_at: datetime,
    finished_at: datetime,
    runtime: ValidationRuntimeEnvironment,
    timing: ValidationTiming,
    findings: tuple[ValidationFinding, ...],
    completion: ValidationRunCompletion,
    operator_assessment: ValidationOperatorAssessment,
    product_ref: ValidationProductReference | None = None,
    predecessor_run_id: str | None = None,
    addressed_findings: tuple[ValidationFindingReference, ...] = (),
    stop_condition: ValidationStopCondition | None = None,
) -> ValidationRun:
    validate_target_fingerprint(target_profile)
    draft = ValidationRun(
        id=run_id,
        target_profile_id=target_profile.id,
        target_profile_fingerprint=target_profile.target_fingerprint,
        workflow=workflow,
        product_ref=product_ref,
        predecessor_run_id=predecessor_run_id,
        addressed_findings=addressed_findings,
        started_at=started_at,
        finished_at=finished_at,
        runtime=runtime,
        timing=timing,
        findings=findings,
        completion=completion,
        stop_condition=stop_condition,
        operator_assessment=operator_assessment,
        run_fingerprint="0" * 64,
    )
    return draft.model_copy(update={"run_fingerprint": compute_run_fingerprint(draft)})


def create_validation_evidence_manifest(
    *,
    manifest_id: str,
    target_profile: ValidationTargetProfile,
    run: ValidationRun,
    entries: tuple[ValidationEvidenceEntry, ...],
) -> ValidationEvidenceManifest:
    validate_target_fingerprint(target_profile)
    validate_run_fingerprint(run)
    if run.target_profile_id != target_profile.id:
        raise ValueError("validation run target_profile_id does not match target profile")
    if run.target_profile_fingerprint != target_profile.target_fingerprint:
        raise ValueError(
            "validation run target_profile_fingerprint does not match target profile"
        )
    run_finding_ids = {finding.id for finding in run.findings}
    for entry in entries:
        unknown = sorted(set(entry.finding_ids) - run_finding_ids)
        if unknown:
            raise ValueError(
                "validation evidence references unknown run finding IDs: "
                + ", ".join(unknown)
            )
    ordered_entries = tuple(sorted(entries, key=lambda item: item.relative_path))
    draft = ValidationEvidenceManifest(
        id=manifest_id,
        target_profile_id=target_profile.id,
        target_profile_fingerprint=target_profile.target_fingerprint,
        validation_run_id=run.id,
        validation_run_fingerprint=run.run_fingerprint,
        entries=ordered_entries,
        package_fingerprint="0" * 64,
    )
    return draft.model_copy(
        update={"package_fingerprint": compute_package_fingerprint(draft)}
    )
