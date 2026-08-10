"""Build and independently verify bounded validation evidence packages."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
)
from test_cartographer.validation.fingerprints import (
    validate_run_fingerprint,
    validate_target_fingerprint,
)
from test_cartographer.validation.io import (
    load_validation_evidence_manifest,
    load_validation_run,
    load_validation_target_profile,
    save_validation_evidence_manifest,
    save_validation_run,
    save_validation_target_profile,
)
from test_cartographer.validation.models import (
    ValidationEvidenceEntry,
    ValidationEvidenceManifest,
    ValidationRun,
    ValidationTargetProfile,
)
from test_cartographer.validation.service import (
    create_validation_evidence_manifest,
)

CORE_TARGET_FILE = "validation-target-profile.json"
CORE_RUN_FILE = "validation-run.json"
CORE_MANIFEST_FILE = "evidence-manifest.json"

DEFAULT_ALLOWED_SENSITIVITIES = (
    SensitivityLevel.PUBLIC,
    SensitivityLevel.INTERNAL,
)
DEFAULT_MAX_EVIDENCE_FILES = 50
DEFAULT_MAX_EVIDENCE_FILE_BYTES = 2_000_000
DEFAULT_MAX_TOTAL_EVIDENCE_BYTES = 10_000_000

_ALLOWED_ARTEFACT_KIND_VALUES = frozenset(kind.value for kind in ValidationArtefactKind)


@dataclass(frozen=True, slots=True)
class ValidationPackageSource:
    """Runtime-only source descriptor; absolute source paths are never persisted."""

    source_path: Path
    relative_path: str
    artefact_kind: ValidationArtefactKind | str
    sensitivity: SensitivityLevel
    producer: ValidationArtefactProducer
    finding_ids: tuple[str, ...] = ()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _coerce_allowed_kind(value: ValidationArtefactKind | str) -> ValidationArtefactKind:
    raw = str(value)
    if raw not in _ALLOWED_ARTEFACT_KIND_VALUES:
        raise ValueError(f"validation package artefact kind is not allowed: {raw}")
    return ValidationArtefactKind(raw)


def _validate_package_policy(
    *,
    artefact_kind: ValidationArtefactKind,
    sensitivity: SensitivityLevel,
    allowed_sensitivities: tuple[SensitivityLevel, ...],
) -> None:
    if artefact_kind.value not in _ALLOWED_ARTEFACT_KIND_VALUES:
        raise ValueError(
            f"validation package artefact kind is not allowed: {artefact_kind.value}"
        )
    if sensitivity not in allowed_sensitivities:
        raise ValueError(
            "validation package sensitivity is not allowed by current package policy: "
            f"{sensitivity.value}"
        )


def _validated_relative_evidence_path(value: str) -> str:
    # Reuse the persisted contract validation, then apply the package-layout rule.
    probe = ValidationEvidenceEntry(
        relative_path=value,
        sha256="0" * 64,
        artefact_kind=ValidationArtefactKind.OPERATOR_SUMMARY,
        sensitivity=SensitivityLevel.INTERNAL,
        producer=ValidationArtefactProducer.SYSTEM,
    )
    if not probe.relative_path.startswith("evidence/"):
        raise ValueError("validation package evidence path must start with 'evidence/'")
    return probe.relative_path


def build_validation_evidence_package(
    *,
    destination: str | Path,
    target_profile: ValidationTargetProfile,
    run: ValidationRun,
    sources: tuple[ValidationPackageSource, ...],
    manifest_id: str,
    allowed_sensitivities: tuple[SensitivityLevel, ...] = DEFAULT_ALLOWED_SENSITIVITIES,
    max_evidence_files: int = DEFAULT_MAX_EVIDENCE_FILES,
    max_evidence_file_bytes: int = DEFAULT_MAX_EVIDENCE_FILE_BYTES,
    max_total_evidence_bytes: int = DEFAULT_MAX_TOTAL_EVIDENCE_BYTES,
) -> ValidationEvidenceManifest:
    """Materialize one immutable package without persisting source absolute paths."""

    validate_target_fingerprint(target_profile)
    validate_run_fingerprint(run)
    if run.target_profile_id != target_profile.id:
        raise ValueError("validation run target_profile_id does not match target profile")
    if run.target_profile_fingerprint != target_profile.target_fingerprint:
        raise ValueError(
            "validation run target_profile_fingerprint does not match target profile"
        )
    if not sources:
        raise ValueError("validation evidence package requires at least one evidence source")
    if len(sources) > max_evidence_files:
        raise ValueError("validation evidence package exceeds file-count budget")
    if not allowed_sensitivities:
        raise ValueError("validation package allowed_sensitivities must not be empty")
    if len(allowed_sensitivities) != len(set(allowed_sensitivities)):
        raise ValueError("validation package allowed_sensitivities must be unique")

    destination_path = Path(destination)
    if destination_path.exists():
        raise FileExistsError(
            f"validation evidence package destination already exists: {destination_path}"
        )
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    finding_ids = {finding.id for finding in run.findings}
    prepared: list[
        tuple[ValidationPackageSource, ValidationEvidenceEntry, int]
    ] = []
    seen_relative_paths: set[str] = set()
    total_bytes = 0

    for source in sources:
        kind = _coerce_allowed_kind(source.artefact_kind)
        _validate_package_policy(
            artefact_kind=kind,
            sensitivity=source.sensitivity,
            allowed_sensitivities=allowed_sensitivities,
        )
        relative_path = _validated_relative_evidence_path(source.relative_path)
        if relative_path in seen_relative_paths:
            raise ValueError(
                f"validation evidence source path is duplicated: {relative_path}"
            )
        seen_relative_paths.add(relative_path)

        source_path = Path(source.source_path)
        if source_path.is_symlink():
            raise ValueError("validation evidence source must not be a symlink")
        if not source_path.is_file():
            raise FileNotFoundError(
                f"validation evidence source is missing or not a file: {source_path}"
            )
        file_size = source_path.stat().st_size
        if file_size > max_evidence_file_bytes:
            raise ValueError(
                f"validation evidence source exceeds per-file budget: {relative_path}"
            )
        total_bytes += file_size
        if total_bytes > max_total_evidence_bytes:
            raise ValueError("validation evidence package exceeds total byte budget")

        unknown_finding_ids = sorted(set(source.finding_ids) - finding_ids)
        if unknown_finding_ids:
            raise ValueError(
                "validation evidence source references unknown run finding IDs: "
                + ", ".join(unknown_finding_ids)
            )

        entry = ValidationEvidenceEntry(
            relative_path=relative_path,
            sha256=_sha256_file(source_path),
            artefact_kind=kind,
            sensitivity=source.sensitivity,
            producer=source.producer,
            finding_ids=source.finding_ids,
        )
        prepared.append((source, entry, file_size))

    temp_path = Path(
        tempfile.mkdtemp(
            prefix=f".{destination_path.name}.building-",
            dir=str(destination_path.parent),
        )
    )
    try:
        save_validation_target_profile(
            target_profile,
            temp_path / CORE_TARGET_FILE,
        )
        save_validation_run(
            run,
            temp_path / CORE_RUN_FILE,
        )

        entries: list[ValidationEvidenceEntry] = []
        for source, entry, _ in prepared:
            target_path = temp_path / entry.relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source.source_path, target_path)
            if _sha256_file(target_path) != entry.sha256:
                raise ValueError(
                    f"validation evidence hash changed during copy: {entry.relative_path}"
                )
            entries.append(entry)

        manifest = create_validation_evidence_manifest(
            manifest_id=manifest_id,
            target_profile=target_profile,
            run=run,
            entries=tuple(entries),
        )
        save_validation_evidence_manifest(
            manifest,
            temp_path / CORE_MANIFEST_FILE,
        )

        # Verify the completed temporary package through the independent read path.
        verify_validation_evidence_package(
            temp_path,
            allowed_sensitivities=allowed_sensitivities,
            max_evidence_files=max_evidence_files,
            max_evidence_file_bytes=max_evidence_file_bytes,
            max_total_evidence_bytes=max_total_evidence_bytes,
        )

        temp_path.rename(destination_path)
        return manifest
    except Exception:
        shutil.rmtree(temp_path, ignore_errors=True)
        raise


def verify_validation_evidence_package(
    package_directory: str | Path,
    *,
    allowed_sensitivities: tuple[SensitivityLevel, ...] = DEFAULT_ALLOWED_SENSITIVITIES,
    max_evidence_files: int = DEFAULT_MAX_EVIDENCE_FILES,
    max_evidence_file_bytes: int = DEFAULT_MAX_EVIDENCE_FILE_BYTES,
    max_total_evidence_bytes: int = DEFAULT_MAX_TOTAL_EVIDENCE_BYTES,
) -> ValidationEvidenceManifest:
    """Fail closed on identity drift, file drift, policy drift, or hidden files."""

    package_path = Path(package_directory)
    if not package_path.is_dir():
        raise FileNotFoundError(
            f"validation evidence package directory is missing: {package_path}"
        )
    if not allowed_sensitivities:
        raise ValueError("validation package allowed_sensitivities must not be empty")

    target_profile = load_validation_target_profile(
        package_path / CORE_TARGET_FILE
    )
    run = load_validation_run(package_path / CORE_RUN_FILE)
    manifest = load_validation_evidence_manifest(
        package_path / CORE_MANIFEST_FILE
    )

    if run.target_profile_id != target_profile.id:
        raise ValueError("validation package run target ID does not match target profile")
    if run.target_profile_fingerprint != target_profile.target_fingerprint:
        raise ValueError(
            "validation package run target fingerprint does not match target profile"
        )
    if manifest.target_profile_id != target_profile.id:
        raise ValueError("validation manifest target ID does not match target profile")
    if manifest.target_profile_fingerprint != target_profile.target_fingerprint:
        raise ValueError(
            "validation manifest target fingerprint does not match target profile"
        )
    if manifest.validation_run_id != run.id:
        raise ValueError("validation manifest run ID does not match validation run")
    if manifest.validation_run_fingerprint != run.run_fingerprint:
        raise ValueError(
            "validation manifest run fingerprint does not match validation run"
        )

    if len(manifest.entries) > max_evidence_files:
        raise ValueError("validation evidence package exceeds file-count budget")

    finding_ids = {finding.id for finding in run.findings}
    expected_files = {
        CORE_TARGET_FILE,
        CORE_RUN_FILE,
        CORE_MANIFEST_FILE,
    }
    total_bytes = 0

    for entry in manifest.entries:
        _validate_package_policy(
            artefact_kind=entry.artefact_kind,
            sensitivity=entry.sensitivity,
            allowed_sensitivities=allowed_sensitivities,
        )
        if not entry.relative_path.startswith("evidence/"):
            raise ValueError(
                "validation manifest evidence path must start with 'evidence/'"
            )
        unknown_finding_ids = sorted(set(entry.finding_ids) - finding_ids)
        if unknown_finding_ids:
            raise ValueError(
                "validation manifest references unknown run finding IDs: "
                + ", ".join(unknown_finding_ids)
            )

        evidence_path = package_path / entry.relative_path
        if evidence_path.is_symlink():
            raise ValueError("validation packaged evidence must not be a symlink")
        if not evidence_path.is_file():
            raise FileNotFoundError(
                f"validation packaged evidence is missing: {entry.relative_path}"
            )
        file_size = evidence_path.stat().st_size
        if file_size > max_evidence_file_bytes:
            raise ValueError(
                f"validation packaged evidence exceeds per-file budget: "
                f"{entry.relative_path}"
            )
        total_bytes += file_size
        if total_bytes > max_total_evidence_bytes:
            raise ValueError("validation evidence package exceeds total byte budget")

        actual_sha = _sha256_file(evidence_path)
        if actual_sha != entry.sha256:
            raise ValueError(
                "validation packaged evidence SHA-256 mismatch: "
                f"{entry.relative_path}"
            )
        expected_files.add(entry.relative_path)

    actual_files = {
        path.relative_to(package_path).as_posix()
        for path in package_path.rglob("*")
        if path.is_file()
    }
    hidden_or_unmanifested = sorted(actual_files - expected_files)
    missing_expected = sorted(expected_files - actual_files)
    if missing_expected:
        raise FileNotFoundError(
            "validation evidence package is missing expected files: "
            + ", ".join(missing_expected)
        )
    if hidden_or_unmanifested:
        raise ValueError(
            "validation evidence package contains unmanifested files: "
            + ", ".join(hidden_or_unmanifested)
        )

    return manifest
