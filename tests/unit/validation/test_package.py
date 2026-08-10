from datetime import timedelta
from pathlib import Path

import pytest

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationFindingKind,
    ValidationLifecycleStage,
    ValidationRunCompletion,
    ValidationWorkflowKind,
)
from test_cartographer.validation.models import ValidationFinding
from test_cartographer.validation.package import (
    CORE_MANIFEST_FILE,
    CORE_RUN_FILE,
    CORE_TARGET_FILE,
    ValidationPackageSource,
    build_validation_evidence_package,
    verify_validation_evidence_package,
)
from test_cartographer.validation.service import create_validation_run


def source(
    path: Path,
    *,
    relative_path: str = "evidence/context-bundle.json",
    kind: ValidationArtefactKind | str = ValidationArtefactKind.CONTEXT_BUNDLE,
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL,
    finding_ids: tuple[str, ...] = (),
) -> ValidationPackageSource:
    return ValidationPackageSource(
        source_path=path,
        relative_path=relative_path,
        artefact_kind=kind,
        sensitivity=sensitivity,
        producer=ValidationArtefactProducer.TESTCARTOGRAPHER,
        finding_ids=finding_ids,
    )


def write_source(tmp_path: Path, name: str = "context.json", body: str = '{"ok":true}\n') -> Path:
    path = tmp_path / "inputs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def build_one(tmp_path, target_profile, validation_run, input_path):
    destination = tmp_path / "package"
    manifest = build_validation_evidence_package(
        destination=destination,
        target_profile=target_profile,
        run=validation_run,
        sources=(source(input_path),),
        manifest_id="validation_manifest",
    )
    return destination, manifest


def test_builder_creates_core_and_evidence_files(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, manifest = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    assert (destination / CORE_TARGET_FILE).is_file()
    assert (destination / CORE_RUN_FILE).is_file()
    assert (destination / CORE_MANIFEST_FILE).is_file()
    assert (destination / "evidence/context-bundle.json").is_file()
    assert manifest.entries[0].relative_path == "evidence/context-bundle.json"


def test_built_package_verifies(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, manifest = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    verified = verify_validation_evidence_package(destination)
    assert verified.package_fingerprint == manifest.package_fingerprint


def test_source_order_does_not_change_package_fingerprint(
    tmp_path, target_profile, validation_run
):
    first = write_source(tmp_path, "a.json", '{"a":1}\n')
    second = write_source(tmp_path, "b.json", '{"b":2}\n')
    a = source(first, relative_path="evidence/a.json")
    b = source(second, relative_path="evidence/b.json")

    manifest_one = build_validation_evidence_package(
        destination=tmp_path / "package-one",
        target_profile=target_profile,
        run=validation_run,
        sources=(b, a),
        manifest_id="validation_manifest",
    )
    manifest_two = build_validation_evidence_package(
        destination=tmp_path / "package-two",
        target_profile=target_profile,
        run=validation_run,
        sources=(a, b),
        manifest_id="validation_manifest",
    )
    assert manifest_one.package_fingerprint == manifest_two.package_fingerprint


def test_builder_refuses_existing_destination(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination = tmp_path / "package"
    destination.mkdir()
    with pytest.raises(FileExistsError):
        build_validation_evidence_package(
            destination=destination,
            target_profile=target_profile,
            run=validation_run,
            sources=(source(input_path),),
            manifest_id="validation_manifest",
        )


def test_builder_requires_evidence_prefix(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    with pytest.raises(ValueError, match="must start"):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(source(input_path, relative_path="context.json"),),
            manifest_id="validation_manifest",
        )


def test_builder_rejects_missing_source(
    tmp_path, target_profile, validation_run
):
    missing = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(source(missing),),
            manifest_id="validation_manifest",
        )


def test_builder_rejects_unapproved_artefact_kind(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    with pytest.raises(ValueError, match="artefact kind is not allowed"):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(source(input_path, kind="screenshot"),),
            manifest_id="validation_manifest",
        )


def test_builder_rejects_confidential_sensitivity_by_default(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    with pytest.raises(ValueError, match="sensitivity is not allowed"):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(
                source(
                    input_path,
                    sensitivity=SensitivityLevel.CONFIDENTIAL,
                ),
            ),
            manifest_id="validation_manifest",
        )


def test_builder_can_explicitly_allow_confidential_sensitivity(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    manifest = build_validation_evidence_package(
        destination=tmp_path / "package",
        target_profile=target_profile,
        run=validation_run,
        sources=(
            source(
                input_path,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
            ),
        ),
        manifest_id="validation_manifest",
        allowed_sensitivities=(
            SensitivityLevel.PUBLIC,
            SensitivityLevel.INTERNAL,
            SensitivityLevel.CONFIDENTIAL,
        ),
    )
    assert manifest.entries[0].sensitivity is SensitivityLevel.CONFIDENTIAL


def test_builder_rejects_per_file_budget(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path, body="x" * 20)
    with pytest.raises(ValueError, match="per-file budget"):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(source(input_path),),
            manifest_id="validation_manifest",
            max_evidence_file_bytes=10,
        )


def test_builder_failure_leaves_no_destination(
    tmp_path, target_profile, validation_run
):
    valid = write_source(tmp_path)
    missing = tmp_path / "missing.json"
    destination = tmp_path / "package"
    with pytest.raises(FileNotFoundError):
        build_validation_evidence_package(
            destination=destination,
            target_profile=target_profile,
            run=validation_run,
            sources=(
                source(valid, relative_path="evidence/valid.json"),
                source(missing, relative_path="evidence/missing.json"),
            ),
            manifest_id="validation_manifest",
        )
    assert not destination.exists()


def test_verifier_rejects_missing_evidence(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, _ = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    (destination / "evidence/context-bundle.json").unlink()
    with pytest.raises(FileNotFoundError):
        verify_validation_evidence_package(destination)


def test_verifier_rejects_hash_drift(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, _ = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    (destination / "evidence/context-bundle.json").write_text(
        '{"tampered":true}\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        verify_validation_evidence_package(destination)


def test_verifier_rejects_unmanifested_file(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, _ = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    (destination / "screenshot.png").write_bytes(b"not really an image")
    with pytest.raises(ValueError, match="unmanifested files"):
        verify_validation_evidence_package(destination)


def test_verifier_rejects_tampered_run(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination, _ = build_one(
        tmp_path, target_profile, validation_run, input_path
    )
    run_path = destination / CORE_RUN_FILE
    text = run_path.read_text(encoding="utf-8")
    run_path.write_text(
        text.replace('"completion":"completed"', '"completion":"incomplete"'),
        encoding="utf-8",
    )
    # Pretty JSON may contain spaces, so ensure an actual mutation occurred.
    if '"completion": "completed"' in text:
        run_path.write_text(
            text.replace(
                '"completion": "completed"',
                '"completion": "incomplete"',
            ),
            encoding="utf-8",
        )
    with pytest.raises(ValueError, match="run_fingerprint mismatch"):
        verify_validation_evidence_package(destination)


def test_builder_accepts_evidence_linked_to_existing_finding(
    tmp_path,
    target_profile,
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
        observation="No viable candidate.",
        could_continue=False,
    )
    run = create_validation_run(
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
    input_path = write_source(tmp_path)
    manifest = build_validation_evidence_package(
        destination=tmp_path / "package",
        target_profile=target_profile,
        run=run,
        sources=(source(input_path, finding_ids=(finding.id,)),),
        manifest_id="validation_manifest",
    )
    assert manifest.entries[0].finding_ids == (finding.id,)


def test_builder_rejects_unknown_finding_reference(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    with pytest.raises(ValueError, match="unknown run finding IDs"):
        build_validation_evidence_package(
            destination=tmp_path / "package",
            target_profile=target_profile,
            run=validation_run,
            sources=(source(input_path, finding_ids=("missing_finding",)),),
            manifest_id="validation_manifest",
        )


def test_verifier_rejects_default_policy_for_confidential_package(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination = tmp_path / "package"
    build_validation_evidence_package(
        destination=destination,
        target_profile=target_profile,
        run=validation_run,
        sources=(
            source(
                input_path,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
            ),
        ),
        manifest_id="validation_manifest",
        allowed_sensitivities=(
            SensitivityLevel.PUBLIC,
            SensitivityLevel.INTERNAL,
            SensitivityLevel.CONFIDENTIAL,
        ),
    )
    with pytest.raises(ValueError, match="sensitivity is not allowed"):
        verify_validation_evidence_package(destination)


def test_verifier_can_use_same_explicit_confidential_policy(
    tmp_path, target_profile, validation_run
):
    input_path = write_source(tmp_path)
    destination = tmp_path / "package"
    policy = (
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
        SensitivityLevel.CONFIDENTIAL,
    )
    build_validation_evidence_package(
        destination=destination,
        target_profile=target_profile,
        run=validation_run,
        sources=(
            source(
                input_path,
                sensitivity=SensitivityLevel.CONFIDENTIAL,
            ),
        ),
        manifest_id="validation_manifest",
        allowed_sensitivities=policy,
    )
    manifest = verify_validation_evidence_package(
        destination,
        allowed_sensitivities=policy,
    )
    assert manifest.entries[0].sensitivity is SensitivityLevel.CONFIDENTIAL
