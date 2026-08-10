from datetime import timedelta

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationFindingKind,
    ValidationLifecycleStage,
    ValidationRunCompletion,
    ValidationWorkflowKind,
)
from test_cartographer.validation.fingerprints import (
    validate_package_fingerprint,
    validate_run_fingerprint,
    validate_target_fingerprint,
)
from test_cartographer.validation.models import (
    ValidationEvidenceEntry,
    ValidationFinding,
    ValidationFindingReference,
)
from test_cartographer.validation.service import (
    create_validation_evidence_manifest,
    create_validation_run,
)


def test_target_factory_creates_valid_fingerprint(target_profile):
    validate_target_fingerprint(target_profile)


def test_run_factory_creates_valid_fingerprint(validation_run):
    validate_run_fingerprint(validation_run)


def test_manifest_factory_sorts_entries(target_profile, validation_run):
    entries = (
        ValidationEvidenceEntry(
            relative_path="evidence/z.json",
            sha256="b" * 64,
            artefact_kind=ValidationArtefactKind.OPERATOR_SUMMARY,
            sensitivity=SensitivityLevel.INTERNAL,
            producer=ValidationArtefactProducer.OPERATOR,
        ),
        ValidationEvidenceEntry(
            relative_path="evidence/a.json",
            sha256="a" * 64,
            artefact_kind=ValidationArtefactKind.CONTEXT_BUNDLE,
            sensitivity=SensitivityLevel.INTERNAL,
            producer=ValidationArtefactProducer.TESTCARTOGRAPHER,
        ),
    )
    manifest = create_validation_evidence_manifest(
        manifest_id="validation_manifest",
        target_profile=target_profile,
        run=validation_run,
        entries=entries,
    )
    assert [entry.relative_path for entry in manifest.entries] == [
        "evidence/a.json",
        "evidence/z.json",
    ]
    validate_package_fingerprint(manifest)


def test_rerun_can_reference_predecessor_finding(
    target_profile,
    validation_run,
    accepted_at,
    runtime,
    timing,
    operator_assessment,
    product_ref,
):
    finding = ValidationFinding(
        id="finding_one",
        observed_at=accepted_at,
        lifecycle_stage=ValidationLifecycleStage.BROWSER_DISCOVERY,
        kind=ValidationFindingKind.FAILURE,
        observation="Current browser discovery could not identify a viable target.",
        could_continue=False,
    )
    first = create_validation_run(
        run_id="validation_run_failure",
        target_profile=target_profile,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        started_at=accepted_at,
        finished_at=accepted_at + timedelta(seconds=30),
        runtime=runtime,
        timing=timing,
        findings=(finding,),
        completion=ValidationRunCompletion.INCOMPLETE,
        operator_assessment=operator_assessment,
    )
    second = create_validation_run(
        run_id="validation_run_rerun",
        target_profile=target_profile,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        predecessor_run_id=first.id,
        addressed_findings=(
            ValidationFindingReference(run_id=first.id, finding_id=finding.id),
        ),
        started_at=accepted_at + timedelta(minutes=10),
        finished_at=accepted_at + timedelta(minutes=10, seconds=20),
        runtime=runtime,
        timing=timing.model_copy(update={"elapsed_seconds": 20.0}),
        findings=(),
        completion=ValidationRunCompletion.COMPLETED,
        operator_assessment=operator_assessment,
    )
    assert second.predecessor_run_id == first.id
    assert second.addressed_findings[0].finding_id == finding.id
    assert first.findings[0].kind is ValidationFindingKind.FAILURE


def test_run_factory_rejects_tampered_target(
    target_profile,
    accepted_at,
    runtime,
    timing,
    operator_assessment,
    product_ref,
):
    tampered = target_profile.model_copy(update={"label": "Tampered target"})
    import pytest

    with pytest.raises(ValueError, match="target_fingerprint mismatch"):
        create_validation_run(
            run_id="validation_run_tampered",
            target_profile=tampered,
            workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
            product_ref=product_ref,
            started_at=accepted_at,
            finished_at=accepted_at + timedelta(seconds=30),
            runtime=runtime,
            timing=timing,
            findings=(),
            completion=ValidationRunCompletion.COMPLETED,
            operator_assessment=operator_assessment,
        )


def test_manifest_factory_rejects_unknown_finding_reference(
    target_profile, validation_run
):
    import pytest

    entry = ValidationEvidenceEntry(
        relative_path="evidence/operator-summary.json",
        sha256="c" * 64,
        artefact_kind=ValidationArtefactKind.OPERATOR_SUMMARY,
        sensitivity=SensitivityLevel.INTERNAL,
        producer=ValidationArtefactProducer.OPERATOR,
        finding_ids=("missing_finding",),
    )
    with pytest.raises(ValueError, match="unknown run finding IDs"):
        create_validation_evidence_manifest(
            manifest_id="validation_manifest",
            target_profile=target_profile,
            run=validation_run,
            entries=(entry,),
        )


def test_manifest_factory_rejects_tampered_run(
    target_profile, validation_run, evidence_entry
):
    import pytest

    tampered = validation_run.model_copy(update={"completion": ValidationRunCompletion.INCOMPLETE})
    with pytest.raises(ValueError, match="run_fingerprint mismatch"):
        create_validation_evidence_manifest(
            manifest_id="validation_manifest",
            target_profile=target_profile,
            run=tampered,
            entries=(evidence_entry,),
        )
