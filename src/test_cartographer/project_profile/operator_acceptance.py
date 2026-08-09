"""Disk-backed real-operator acceptance utility for Sprint 15 ProjectProfile."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from test_cartographer.adaptation.io import load_workspace_profile
from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.io import load_guided_profile
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.interactive_creation.project_profile import (
    apply_persistent_project_bootstrap,
    validate_guided_intake_binding,
    validate_workspace_binding,
)
from test_cartographer.project_profile.enums import (
    AuthenticationDeclarationState,
    ProfileBindingState,
    ProjectProfileEventKind,
    ProjectValueSource,
)
from test_cartographer.project_profile.fingerprints import canonical_model_sha256
from test_cartographer.project_profile.integration import (
    ProjectCompatibilityDisposition,
    assess_project_profile_compatibility,
)
from test_cartographer.project_profile.integration_io import (
    load_project_profile_reference,
    save_project_profile_compatibility,
)
from test_cartographer.project_profile.io import (
    load_project_profile,
    save_project_profile,
)
from test_cartographer.project_profile.models import (
    AuthenticationDeclaration,
    ProjectApplicationBootstrap,
    ProjectDataPolicy,
    ProjectProfileBinding,
    ProjectValue,
)
from test_cartographer.project_profile.readiness import assess_project_profile
from test_cartographer.project_profile.service import (
    create_project_profile,
    revise_project_profile,
)

BOOTSTRAP_IDS = {
    "q_application_name",
    "q_application_environment",
    "q_application_base_url",
}
PROCESS_IDS = {
    "q_process_name",
    "q_process_purpose",
    "q_process_risk",
    "q_process_role",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode",
        choices=("init", "creation-reuse", "expansion-reuse", "change-environment", "verify"),
    )
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--artifact-dir", required=True)
    parser.add_argument("--profile-path", default=".test-cartographer/project-profile.json")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--ollama-base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--provider-mode", choices=("ollama", "replay"), default="replay")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    artifact_dir = Path(args.artifact_dir).resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    profile_path = (root / args.profile_path).resolve()

    workspace = load_workspace_profile(
        root / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    guided = _runtime_guided_profile(
        root,
        model=args.model,
        base_url=args.ollama_base_url,
        timeout_seconds=args.timeout_seconds,
        provider_mode=args.provider_mode,
    )

    if args.mode == "init":
        _init(profile_path, artifact_dir, workspace, guided)
    elif args.mode == "creation-reuse":
        _reuse_probe(
            "creation",
            profile_path,
            artifact_dir,
            workspace,
            guided,
            "Automate catalog search as a later process.",
        )
    elif args.mode == "expansion-reuse":
        _reuse_probe(
            "expansion",
            profile_path,
            artifact_dir,
            workspace,
            guided,
            "Add catalog sorting as a second process.",
        )
    elif args.mode == "change-environment":
        _change_environment(profile_path, artifact_dir, workspace, guided)
    else:
        _verify(profile_path, artifact_dir)
    return 0


def _runtime_guided_profile(
    root: Path,
    *,
    model: str,
    base_url: str,
    timeout_seconds: float,
    provider_mode: str,
):
    base = load_guided_profile(
        root / "testdata/guided_intake/profile/ollama_local_qwen.json"
    )
    return base.model_copy(
        update={
            "id": "guided_interactive_local",
            "model": model,
            "base_url": base_url,
            "timeout_seconds": timeout_seconds,
            "provider": (
                GuidanceProviderKind.OLLAMA
                if provider_mode == "ollama"
                else GuidanceProviderKind.REPLAY
            ),
        }
    )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _project_value(value: str, reviewed_at: datetime, sensitivity: SensitivityLevel):
    return ProjectValue(
        value=value,
        status=KnowledgeStatus.CONFIRMED,
        sensitivity=sensitivity,
        source=ProjectValueSource.HUMAN,
        reviewed_at=reviewed_at,
    )


def _current_binding(model, reviewed_at: datetime) -> ProjectProfileBinding:
    return ProjectProfileBinding(
        profile_id=model.id,
        profile_sha256=canonical_model_sha256(model),
        state=ProfileBindingState.CURRENT,
        reviewed_at=reviewed_at,
    )


def _init(profile_path: Path, artifact_dir: Path, workspace, guided) -> None:
    if profile_path.exists():
        raise SystemExit(
            f"ProjectProfile already exists: {profile_path}. "
            "Archive/remove it only if you intentionally want a fresh bootstrap."
        )

    started = time.perf_counter()
    print("\nSprint 15 — Run A: first persistent project bootstrap")
    name = _read_with_default("Application name", "Public Catalog")
    environment = _read_with_default("Environment", "local_acceptance")
    base_url = _read_url_with_default("Project base URL/origin", "http://127.0.0.1")

    print("\nProjectProfile summary")
    print(f"  application: {name}")
    print(f"  environment: {environment}")
    print(f"  base URL:    {base_url}")
    print(f"  workspace:   {workspace.id}")
    print(f"  guided:      {guided.id} / {guided.provider.value} / {guided.model}")
    print("  auth:        not required")
    print("  secrets:     not stored")
    _accept("Accept and persist this ProjectProfile?")

    accepted_at = _now()
    profile = create_project_profile(
        profile_id="project_public_catalog",
        application=ProjectApplicationBootstrap(
            name=_project_value(name, accepted_at, SensitivityLevel.INTERNAL),
            environment=_project_value(
                environment, accepted_at, SensitivityLevel.INTERNAL
            ),
            base_url=_project_value(
                base_url, accepted_at, SensitivityLevel.CONFIDENTIAL
            ),
        ),
        workspace_binding=_current_binding(workspace, accepted_at),
        guided_intake_binding=_current_binding(guided, accepted_at),
        data_policy=ProjectDataPolicy(),
        authentication=AuthenticationDeclaration(
            state=AuthenticationDeclarationState.NOT_REQUIRED
        ),
        accepted_at=accepted_at,
    )
    report = assess_project_profile(profile)
    if not report.ready_for_bootstrap_reuse:
        raise RuntimeError("accepted profile did not reach bootstrap reuse readiness")

    save_project_profile(profile, profile_path)
    _write_json(
        artifact_dir / "run-a-first-bootstrap.json",
        {
            "run": "A",
            "profile_path": str(profile_path),
            "profile_id": profile.id,
            "revision": profile.revision,
            "configuration_fingerprint": profile.configuration_fingerprint,
            "bootstrap_questions_first_run": 3,
            "profile_ready": True,
            "secret_values_persisted": profile.secret_values_persisted,
            "raw_auth_state_persisted": profile.raw_auth_state_persisted,
            "operator_profile_review_actions": 1,
            "active_profile_review_seconds": round(time.perf_counter() - started, 3),
        },
    )
    print(f"\nPersisted: {profile_path}")
    print("Run A verified: revision=1, ready=true, secrets/auth state absent.")


def _reuse_probe(
    label: str,
    profile_path: Path,
    artifact_dir: Path,
    workspace,
    guided,
    request: str,
) -> None:
    profile = load_project_profile(profile_path)
    validate_workspace_binding(profile, workspace)
    validate_guided_intake_binding(profile, guided)

    now = _now()
    context = build_minimal_context(
        MinimalContextSeed(
            id=f"seed_{label}_reuse",
            context_id=f"ctx_{label}_reuse",
            title=f"Sprint 15 {label} reuse",
            initial_request=request,
            created_at=now,
        )
    )
    run_dir = artifact_dir / f"run-{'b' if label == 'creation' else 'c'}-{label}-reuse"
    run_dir.mkdir(parents=True, exist_ok=True)
    projected, loaded_profile = apply_persistent_project_bootstrap(
        context,
        project_profile_path=profile_path,
        output_dir=run_dir,
        projected_at=now,
    )
    question_ids = {item.id for item in list_questions(projected)}
    bootstrap_remaining = sorted(question_ids & BOOTSTRAP_IDS)
    process_present = sorted(question_ids & PROCESS_IDS)
    if bootstrap_remaining:
        raise RuntimeError(f"bootstrap questions unexpectedly remain: {bootstrap_remaining}")
    if not PROCESS_IDS.issubset(question_ids):
        raise RuntimeError(f"process-specific questions missing: {process_present}")

    letter = "B" if label == "creation" else "C"
    _write_json(
        artifact_dir / f"run-{letter.lower()}-{label}-reuse.json",
        {
            "run": letter,
            "kind": label,
            "profile_loaded_from_disk": True,
            "profile_id": loaded_profile.id,
            "profile_revision_used": loaded_profile.revision,
            "configuration_fingerprint_used": loaded_profile.configuration_fingerprint,
            "bootstrap_questions_asked": 0,
            "bootstrap_questions_remaining": bootstrap_remaining,
            "process_specific_questions_present": process_present,
            "workspace_binding_reused": True,
            "guided_intake_binding_reused": True,
        },
    )
    print(
        f"Run {letter} verified in PID {__import__('os').getpid()}: "
        f"disk profile reuse, bootstrap=0, process-specific intake preserved."
    )


def _change_environment(profile_path: Path, artifact_dir: Path, workspace, guided) -> None:
    profile = load_project_profile(profile_path)
    if profile.revision != 1:
        raise SystemExit(
            f"Run D expects accepted revision 1 before invalidation experiment; got {profile.revision}"
        )
    validate_workspace_binding(profile, workspace)
    validate_guided_intake_binding(profile, guided)
    reference = load_project_profile_reference(
        artifact_dir / "run-b-creation-reuse" / "00-project-profile-reference.json"
    )

    print("\nSprint 15 — Run D: selective environment/base-URL invalidation")
    current_env = profile.application.environment.value or "local_acceptance"
    current_url = profile.application.base_url.value or "http://127.0.0.1"
    new_env = _read_with_default("New environment", f"{current_env}_changed")
    new_url = _read_url_with_default("New project base URL/origin", _next_url(current_url))

    print("\nSelective-change summary")
    print(f"  environment: {current_env} -> {new_env}")
    print(f"  base URL:    {current_url} -> {new_url}")
    print("Expected consequence: browser evidence REOBSERVE; business context stays reusable.")
    _accept("Accept ProjectProfile revision 2?")

    changed_at = _now()
    application = profile.application.model_copy(
        update={
            "environment": _project_value(
                new_env, changed_at, profile.application.environment.sensitivity
            ),
            "base_url": _project_value(
                new_url, changed_at, profile.application.base_url.sensitivity
            ),
        }
    )
    revised = revise_project_profile(
        profile,
        occurred_at=changed_at,
        event_kind=ProjectProfileEventKind.CHANGED,
        affected_paths=("application.environment", "application.base_url"),
        reason_code="sprint15_operator_environment_change",
        application=application,
    )
    save_project_profile(revised, profile_path)

    compatibility = assess_project_profile_compatibility(revised, reference)
    save_project_profile_compatibility(
        compatibility,
        artifact_dir / "run-d-compatibility.json",
    )

    required = (
        compatibility.environment_browser_evidence
        is ProjectCompatibilityDisposition.REOBSERVE
        and compatibility.business_context
        is ProjectCompatibilityDisposition.COMPATIBLE
        and compatibility.workspace
        is ProjectCompatibilityDisposition.COMPATIBLE
        and compatibility.guided_intake
        is ProjectCompatibilityDisposition.COMPATIBLE
        and compatibility.business_context_reuse_allowed
        and compatibility.reobservation_required
        and not compatibility.resnapshot_required
    )
    if not required:
        raise RuntimeError("selective invalidation acceptance conditions were not met")

    _write_json(
        artifact_dir / "run-d-environment-change.json",
        {
            "run": "D",
            "revision_before": 1,
            "revision_after": revised.revision,
            "configuration_fingerprint_changed": (
                revised.configuration_fingerprint != profile.configuration_fingerprint
            ),
            "environment_browser_evidence": compatibility.environment_browser_evidence.value,
            "business_context": compatibility.business_context.value,
            "workspace": compatibility.workspace.value,
            "guided_intake": compatibility.guided_intake.value,
            "business_context_reuse_allowed": compatibility.business_context_reuse_allowed,
            "reobservation_required": compatibility.reobservation_required,
            "resnapshot_required": compatibility.resnapshot_required,
            "unrelated_fields_reasked": 0,
        },
    )
    print("Run D verified: revision=2, REOBSERVE browser evidence, business context retained.")


def _verify(profile_path: Path, artifact_dir: Path) -> None:
    required = [
        artifact_dir / "run-a-first-bootstrap.json",
        artifact_dir / "run-b-creation-reuse.json",
        artifact_dir / "run-c-expansion-reuse.json",
        artifact_dir / "run-d-environment-change.json",
        artifact_dir / "run-d-compatibility.json",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"missing acceptance artifacts: {missing}")

    a = json.loads(required[0].read_text(encoding="utf-8"))
    b = json.loads(required[1].read_text(encoding="utf-8"))
    c = json.loads(required[2].read_text(encoding="utf-8"))
    d = json.loads(required[3].read_text(encoding="utf-8"))
    profile = load_project_profile(profile_path)

    checks = {
        "run_a_revision_1": a["revision"] == 1,
        "run_a_no_secrets": not a["secret_values_persisted"] and not a["raw_auth_state_persisted"],
        "run_b_bootstrap_zero": b["bootstrap_questions_asked"] == 0,
        "run_b_process_questions_preserved": len(b["process_specific_questions_present"]) >= 4,
        "run_c_bootstrap_zero": c["bootstrap_questions_asked"] == 0,
        "run_c_bindings_reused": c["workspace_binding_reused"] and c["guided_intake_binding_reused"],
        "run_d_revision_2": d["revision_after"] == 2 and profile.revision == 2,
        "run_d_reobserve": d["environment_browser_evidence"] == "reobserve",
        "run_d_business_compatible": d["business_context"] == "compatible",
        "run_d_workspace_compatible": d["workspace"] == "compatible",
        "run_d_guided_compatible": d["guided_intake"] == "compatible",
        "run_d_no_unrelated_reask": d["unrelated_fields_reasked"] == 0,
    }
    if not all(checks.values()):
        failed = [key for key, value in checks.items() if not value]
        raise RuntimeError(f"Sprint 15 acceptance verification failed: {failed}")

    _write_json(
        artifact_dir / "sprint-15-acceptance-summary.json",
        {
            "project_profile_verified": True,
            "disk_backed_separate_runs_verified": True,
            "bootstrap_reuse_verified": True,
            "creation_reuse_bootstrap_questions": b["bootstrap_questions_asked"],
            "expansion_reuse_bootstrap_questions": c["bootstrap_questions_asked"],
            "selective_environment_invalidation_verified": True,
            "business_context_preserved": True,
            "workspace_binding_preserved": True,
            "guided_intake_binding_preserved": True,
            "final_profile_revision": profile.revision,
            "measured_savings_claimed": False,
            "checks": checks,
        },
    )
    print("\nSprint 15 persisted ProjectProfile acceptance: VERIFIED")
    print("creation bootstrap questions: 0")
    print("expansion bootstrap questions: 0")
    print("environment/base URL change: REOBSERVE")
    print("business context: COMPATIBLE")
    print("workspace/guided bindings: COMPATIBLE")
    print("measured savings claimed: false")


def _read_with_default(label: str, default: str) -> str:
    while True:
        raw = input(f"{label} [{default}]: ").strip()
        value = raw or default
        if value:
            return value


def _read_url_with_default(label: str, default: str) -> str:
    while True:
        value = _read_with_default(label, default)
        parsed = urlparse(value)
        if (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
        ):
            return value
        print("Enter an absolute HTTP(S) URL without credentials, query or fragment.")


def _accept(prompt: str) -> None:
    while True:
        value = input(f"{prompt} [A=accept / R=reject]: ").strip().lower()
        if value in {"a", "accept"}:
            return
        if value in {"r", "reject"}:
            raise SystemExit("Operator rejected the ProjectProfile action.")
        print("Invalid input. Use A/Accept or R/Reject.")


def _next_url(current: str) -> str:
    parsed = urlparse(current)
    host = parsed.hostname or "127.0.0.1"
    scheme = parsed.scheme or "http"
    port = parsed.port
    if port is None:
        return f"{scheme}://{host}:8766"
    return f"{scheme}://{host}:{port + 1}"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    raise SystemExit(main())
