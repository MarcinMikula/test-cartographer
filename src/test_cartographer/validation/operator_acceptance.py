"""Controlled Sprint 16 validation-protocol rehearsal."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationAuthenticationRequirement,
    ValidationFindingKind,
    ValidationLifecycleStage,
    ValidationOperatorDifficulty,
    ValidationResultConfidence,
    ValidationRunCompletion,
    ValidationTargetControl,
    ValidationTargetDifficulty,
    ValidationTargetFamiliarity,
    ValidationWorkflowKind,
    ValidationWorkflowReuseIntent,
)
from test_cartographer.validation.io import load_validation_run
from test_cartographer.validation.models import (
    ValidationFinding,
    ValidationFindingReference,
    ValidationOperatorAssessment,
    ValidationProductReference,
    ValidationRuntimeEnvironment,
    ValidationTiming,
)
from test_cartographer.validation.package import (
    ValidationPackageSource,
    build_validation_evidence_package,
    verify_validation_evidence_package,
)
from test_cartographer.validation.service import (
    create_validation_run,
    create_validation_target_profile,
)

BASE_COMMIT = "f9218bc09e80ba513a485c42864c1ba96dace329"
PRODUCT_VERSION = "0.16.0"
OLD_LOCATOR = "catalog-sort"
CURRENT_LOCATOR = "catalog-sort-control"

SPRINT16_PATHS = (
    "docs/adr-sprint-16-validation-evidence.md",
    "docs/sprint-16-acceptance-blueprint.md",
    "docs/validation-protocol.md",
    "pyproject.toml",
    "schemas/validation-evidence-manifest-v0.1.schema.json",
    "schemas/validation-finding-v0.1.schema.json",
    "schemas/validation-run-v0.1.schema.json",
    "schemas/validation-target-profile-v0.1.schema.json",
    "scripts/export_validation_schemas.py",
    "scripts/run_validation_protocol_rehearsal.py",
    "src/test_cartographer/__init__.py",
    "src/test_cartographer/validation/__init__.py",
    "src/test_cartographer/validation/enums.py",
    "src/test_cartographer/validation/fingerprints.py",
    "src/test_cartographer/validation/io.py",
    "src/test_cartographer/validation/models.py",
    "src/test_cartographer/validation/operator_acceptance.py",
    "src/test_cartographer/validation/package.py",
    "src/test_cartographer/validation/service.py",
    "tests/unit/validation/conftest.py",
    "tests/unit/validation/test_fingerprints.py",
    "tests/unit/validation/test_io.py",
    "tests/unit/validation/test_models.py",
    "tests/unit/validation/test_operator_acceptance.py",
    "tests/unit/validation/test_package.py",
    "tests/unit/validation/test_service.py",
)


def compute_working_tree_fingerprint(
    repository_root: Path,
    relative_paths: tuple[str, ...] = SPRINT16_PATHS,
) -> str:
    digest = hashlib.sha256()
    for relative in sorted(relative_paths):
        path = repository_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"working-tree fingerprint path missing: {relative}"
            )
        name = relative.encode("utf-8")
        data = path.read_bytes()
        digest.update(len(name).to_bytes(4, "big"))
        digest.update(name)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _ask_accept(prompt: str) -> tuple[bool, float, int]:
    started = time.perf_counter()
    invalid = 0
    while True:
        value = input(f"{prompt} [a=accept / r=reject]: ").strip().lower()
        if value in {"a", "accept"}:
            return True, time.perf_counter() - started, invalid
        if value in {"r", "reject"}:
            return False, time.perf_counter() - started, invalid
        invalid += 1
        print("Invalid input. Use only a/accept or r/reject.")


def _ask_choice(
    prompt: str,
    options: dict[str, object],
) -> tuple[object, float, int]:
    started = time.perf_counter()
    invalid = 0
    while True:
        value = input(prompt).strip().lower()
        if value in options:
            return options[value], time.perf_counter() - started, invalid
        invalid += 1
        print("Invalid input. Choose: " + ", ".join(options))


def _assessment() -> tuple[ValidationOperatorAssessment, float, int]:
    difficulty, a, invalid_a = _ask_choice(
        "Difficulty [e=easy / m=moderate / h=hard / b=blocked]: ",
        {
            "e": ValidationOperatorDifficulty.EASY,
            "m": ValidationOperatorDifficulty.MODERATE,
            "h": ValidationOperatorDifficulty.HARD,
            "b": ValidationOperatorDifficulty.BLOCKED,
        },
    )
    confidence, b, invalid_b = _ask_choice(
        "Confidence [l=low / m=medium / h=high]: ",
        {
            "l": ValidationResultConfidence.LOW,
            "m": ValidationResultConfidence.MEDIUM,
            "h": ValidationResultConfidence.HIGH,
        },
    )
    reuse, c, invalid_c = _ask_choice(
        "Would reuse workflow [y=yes / u=uncertain / n=no]: ",
        {
            "y": ValidationWorkflowReuseIntent.YES,
            "u": ValidationWorkflowReuseIntent.UNCERTAIN,
            "n": ValidationWorkflowReuseIntent.NO,
        },
    )
    return (
        ValidationOperatorAssessment(
            difficulty=difficulty,
            confidence_in_result=confidence,
            would_reuse_workflow=reuse,
            prior_target_familiarity=ValidationTargetFamiliarity.AUTOMATED_BEFORE,
        ),
        a + b + c,
        invalid_a + invalid_b + invalid_c,
    )


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _probe(root: Path) -> dict[str, object]:
    inventory = json.loads(
        (root / "testdata/proactive/inventory/public_catalog.json").read_text(
            encoding="utf-8"
        )
    )
    html = (
        root / "testdata/proactive/browser/public_catalog_deployed.html"
    ).read_text(encoding="utf-8")
    item = next(
        row for row in inventory["items"] if row["id"] == "inventory_sort_results"
    )
    if item["primary_locator_value"] != OLD_LOCATOR:
        raise RuntimeError("controlled inventory no longer contains expected locator")
    old_present = f'data-testid="{OLD_LOCATOR}"' in html
    current_present = f'data-testid="{CURRENT_LOCATOR}"' in html
    if old_present or not current_present:
        raise RuntimeError("controlled locator-drift fixture changed unexpectedly")
    return {
        "schema_version": "0.1",
        "kind": "controlled_locator_drift_rehearsal",
        "inventory_id": inventory["id"],
        "inventory_item_id": item["id"],
        "old_locator": OLD_LOCATOR,
        "old_locator_present": old_present,
        "current_locator": CURRENT_LOCATOR,
        "current_locator_present": current_present,
        "raw_html_persisted": False,
        "external_validity_proven": False,
    }


def _target():
    return create_validation_target_profile(
        profile_id="validation_public_catalog_controlled",
        label="Public catalog controlled protocol rehearsal",
        target_url="http://127.0.0.1/public_catalog_deployed.html",
        difficulty=ValidationTargetDifficulty.SIMPLE,
        control=ValidationTargetControl.PROJECT_CONTROLLED,
        authentication=ValidationAuthenticationRequirement.NONE,
        process_label="Observe known sort locator drift",
        allowed_actions=("read controlled inventory", "read controlled page fixture"),
        prohibited_actions=("network crawling", "destructive actions"),
        authorization_statement="Project-controlled fixture approved for Sprint 16 rehearsal.",
        operator_authorization_confirmed=True,
        sensitivity=SensitivityLevel.PUBLIC,
    )


def _runtime() -> ValidationRuntimeEnvironment:
    return ValidationRuntimeEnvironment(
        operating_system=sys.platform,
        python_version=sys.version.split()[0],
    )


def _timing(setup: float, review: float) -> ValidationTiming:
    active = max(0.001, setup + review)
    return ValidationTiming(
        elapsed_seconds=active,
        setup_active_seconds=setup,
        intake_active_seconds=0.0,
        review_active_seconds=review,
        correction_active_seconds=0.0,
        system_wait_seconds=0.0,
    )


def _source(
    path: Path,
    relative: str,
    kind: ValidationArtefactKind,
    *,
    finding_ids: tuple[str, ...] = (),
) -> ValidationPackageSource:
    return ValidationPackageSource(
        source_path=path,
        relative_path=relative,
        artefact_kind=kind,
        sensitivity=SensitivityLevel.PUBLIC,
        producer=ValidationArtefactProducer.SYSTEM,
        finding_ids=finding_ids,
    )


def _artifact_root(repo: Path) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    path = repo.parent / "TestCartographer-local-artifacts" / "sprint-16" / stamp
    path.mkdir(parents=True, exist_ok=False)
    return path


def _order_stable(target, run, a: Path, b: Path) -> bool:
    temp = Path(tempfile.mkdtemp(prefix="tc-validation-order-"))
    try:
        one = build_validation_evidence_package(
            destination=temp / "one",
            target_profile=target,
            run=run,
            sources=(
                _source(b, "evidence/b.json", ValidationArtefactKind.OPERATOR_SUMMARY),
                _source(a, "evidence/a.json", ValidationArtefactKind.OPERATOR_SUMMARY),
            ),
            manifest_id="validation_order_manifest",
        )
        two = build_validation_evidence_package(
            destination=temp / "two",
            target_profile=target,
            run=run,
            sources=(
                _source(a, "evidence/a.json", ValidationArtefactKind.OPERATOR_SUMMARY),
                _source(b, "evidence/b.json", ValidationArtefactKind.OPERATOR_SUMMARY),
            ),
            manifest_id="validation_order_manifest",
        )
        return one.package_fingerprint == two.package_fingerprint
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def _tamper_detected(package: Path) -> bool:
    temp = Path(tempfile.mkdtemp(prefix="tc-validation-tamper-"))
    try:
        copy = temp / "tampered"
        shutil.copytree(package, copy)
        evidence = copy / "evidence" / "controlled-probe.json"
        evidence.write_text('{"tampered":true}\n', encoding="utf-8")
        try:
            verify_validation_evidence_package(copy)
        except ValueError as exc:
            return "SHA-256 mismatch" in str(exc)
        return False
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def run_rehearsal(repository_root: Path) -> int:
    repo = repository_root.resolve()
    if _git_head(repo) != BASE_COMMIT:
        raise RuntimeError("Sprint 16D base HEAD changed unexpectedly")

    product_ref = ValidationProductReference(
        git_commit=BASE_COMMIT,
        version=PRODUCT_VERSION,
        working_tree_fingerprint=compute_working_tree_fingerprint(repo),
    )
    probe = _probe(repo)
    target = _target()

    print("Sprint 16D controlled rehearsal")
    print("External validation: false")
    print(f"Known drift: {OLD_LOCATOR} -> {CURRENT_LOCATOR}")

    ok, setup_one, invalid_one = _ask_accept(
        "Authorize bounded project-controlled rehearsal?"
    )
    if not ok:
        return 2

    print(json.dumps(probe, indent=2))
    ok, review_finding, invalid_two = _ask_accept(
        "Accept this known controlled drift as R1 finding evidence?"
    )
    if not ok:
        return 3

    assessment_one, assessment_time_one, invalid_assessment_one = _assessment()
    root = _artifact_root(repo)
    inputs = root / "inputs"
    probe_one = inputs / "run-one-probe.json"
    note_one = inputs / "run-one-note.json"
    _write_json(probe_one, probe)
    _write_json(
        note_one,
        {
            "finding_recorded_before_fix_design": True,
            "known_controlled_condition": True,
            "external_validity_proven": False,
        },
    )

    now = datetime.now(timezone.utc)
    finding = ValidationFinding(
        id="finding_controlled_locator_drift",
        observed_at=now,
        lifecycle_stage=ValidationLifecycleStage.BROWSER_DISCOVERY,
        kind=ValidationFindingKind.FAILURE,
        observation=(
            "Known controlled inventory locator catalog-sort is absent from the "
            "controlled deployed fixture, which contains catalog-sort-control."
        ),
        evidence_ids=("controlled_probe",),
        could_continue=False,
    )
    timing_one = _timing(setup_one, review_finding + assessment_time_one)
    run_one = create_validation_run(
        run_id="validation_rehearsal_run_one",
        target_profile=target,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        started_at=now,
        finished_at=now + timedelta(seconds=timing_one.elapsed_seconds),
        runtime=_runtime(),
        timing=timing_one,
        findings=(finding,),
        completion=ValidationRunCompletion.INCOMPLETE,
        operator_assessment=assessment_one,
    )
    manifest_one = build_validation_evidence_package(
        destination=root / "run-one",
        target_profile=target,
        run=run_one,
        sources=(
            _source(
                probe_one,
                "evidence/controlled-probe.json",
                ValidationArtefactKind.BROWSER_OBSERVATION,
                finding_ids=(finding.id,),
            ),
            _source(
                note_one,
                "evidence/protocol-note.json",
                ValidationArtefactKind.OPERATOR_SUMMARY,
                finding_ids=(finding.id,),
            ),
        ),
        manifest_id="validation_rehearsal_manifest_one",
    )
    verify_validation_evidence_package(root / "run-one")
    print(f"R1 CLOSED: {root / 'run-one'}")

    ok, setup_two, invalid_three = _ask_accept(
        "Proceed with R2 while keeping R1 immutable?"
    )
    if not ok:
        print("R1 remains closed and verified.")
        return 4

    assessment_two, assessment_time_two, invalid_assessment_two = _assessment()
    probe_two = inputs / "run-two-probe.json"
    note_two = inputs / "run-two-note.json"
    _write_json(
        probe_two,
        {
            **probe,
            "rerun": True,
            "predecessor_run_id": run_one.id,
            "addressed_finding_id": finding.id,
            "product_remediation_proven": False,
        },
    )
    _write_json(
        note_two,
        {
            "predecessor_preserved": True,
            "same_product_state": True,
            "product_fix_claimed": False,
            "external_validity_proven": False,
        },
    )
    now_two = datetime.now(timezone.utc)
    timing_two = _timing(setup_two, assessment_time_two)
    run_two = create_validation_run(
        run_id="validation_rehearsal_run_two",
        target_profile=target,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        predecessor_run_id=run_one.id,
        addressed_findings=(
            ValidationFindingReference(run_id=run_one.id, finding_id=finding.id),
        ),
        started_at=now_two,
        finished_at=now_two + timedelta(seconds=timing_two.elapsed_seconds),
        runtime=_runtime(),
        timing=timing_two,
        findings=(),
        completion=ValidationRunCompletion.COMPLETED,
        operator_assessment=assessment_two,
    )
    manifest_two = build_validation_evidence_package(
        destination=root / "run-two",
        target_profile=target,
        run=run_two,
        sources=(
            _source(
                probe_two,
                "evidence/rerun-probe.json",
                ValidationArtefactKind.BROWSER_OBSERVATION,
            ),
            _source(
                note_two,
                "evidence/rerun-note.json",
                ValidationArtefactKind.OPERATOR_SUMMARY,
            ),
        ),
        manifest_id="validation_rehearsal_manifest_two",
    )

    verified_one = verify_validation_evidence_package(root / "run-one")
    verified_two = verify_validation_evidence_package(root / "run-two")
    persisted_one = load_validation_run(root / "run-one" / "validation-run.json")
    first_finding_preserved = any(x.id == finding.id for x in persisted_one.findings)
    predecessor_link_valid = (
        run_two.predecessor_run_id == run_one.id
        and run_two.addressed_findings
        and run_two.addressed_findings[0].finding_id == finding.id
    )

    order_a = inputs / "order-a.json"
    order_b = inputs / "order-b.json"
    _write_json(order_a, {"value": "a"})
    _write_json(order_b, {"value": "b"})
    order_stable = _order_stable(target, run_two, order_a, order_b)
    tamper = _tamper_detected(root / "run-one")

    final_ok, final_review_seconds, invalid_four = _ask_accept(
        "Are timing categories and stop/review rules practical enough for Sprint 17?"
    )

    summary = {
        "schema_version": "0.1",
        "base_git_commit": product_ref.git_commit,
        "working_tree_fingerprint": product_ref.working_tree_fingerprint,
        "run_one_verified": (
            verified_one.package_fingerprint == manifest_one.package_fingerprint
        ),
        "run_two_verified": (
            verified_two.package_fingerprint == manifest_two.package_fingerprint
        ),
        "first_finding_preserved": first_finding_preserved,
        "predecessor_link_valid": bool(predecessor_link_valid),
        "package_fingerprint_order_stable": order_stable,
        "tamper_detection_fail_closed": tamper,
        "invalid_input_reprompts": (
            invalid_one
            + invalid_two
            + invalid_assessment_one
            + invalid_three
            + invalid_assessment_two
            + invalid_four
        ),
        "final_operator_review_seconds": final_review_seconds,
        "final_operator_review_accepted": final_ok,
        "controlled_target": True,
        "external_application_validity_proven": False,
        "productivity_savings_claimed": False,
        "product_remediation_proven": False,
    }
    _write_json(root / "rehearsal-summary.json", summary)

    print()
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"artifact_root: {root}")

    required = (
        summary["run_one_verified"],
        summary["run_two_verified"],
        summary["first_finding_preserved"],
        summary["predecessor_link_valid"],
        summary["package_fingerprint_order_stable"],
        summary["tamper_detection_fail_closed"],
        summary["final_operator_review_accepted"],
    )
    if not all(required):
        print("Sprint 16D rehearsal: NOT ACCEPTED")
        return 5

    print("Sprint 16D rehearsal: VERIFIED")
    return 0


def verify_rehearsal(artifact_root: Path) -> int:
    root = artifact_root.resolve()
    summary = json.loads(
        (root / "rehearsal-summary.json").read_text(encoding="utf-8")
    )
    one = verify_validation_evidence_package(root / "run-one")
    two = verify_validation_evidence_package(root / "run-two")
    for key in (
        "run_one_verified",
        "run_two_verified",
        "first_finding_preserved",
        "predecessor_link_valid",
        "package_fingerprint_order_stable",
        "tamper_detection_fail_closed",
        "final_operator_review_accepted",
    ):
        if not summary[key]:
            raise ValueError(f"rehearsal summary check failed: {key}")
    if summary["external_application_validity_proven"]:
        raise ValueError("controlled rehearsal must not claim external validity")
    print("Sprint 16D rehearsal artifact: VERIFIED")
    print(f"R1 package fingerprint: {one.package_fingerprint}")
    print(f"R2 package fingerprint: {two.package_fingerprint}")
    print("External application validity proven: false")
    return 0
