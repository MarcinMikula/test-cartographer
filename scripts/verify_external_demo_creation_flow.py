"""Run the fixture-assisted integrated Creation Flow end to end."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationReviewDecision
from test_cartographer.adaptation.io import (
    load_workspace_profile,
    save_adaptation_plan,
    save_framework_snapshot,
)
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.io import save_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.creation_flow.assessment import assess_creation_flow
from test_cartographer.creation_flow.enums import (
    CreationFlowStatus,
    CreationStageKind,
    CreationStageStatus,
)
from test_cartographer.creation_flow.handoff import confirm_synthesis_handoff
from test_cartographer.creation_flow.io import (
    load_creation_flow_profile,
    save_creation_flow_run,
)
from test_cartographer.creation_flow.models import CreationFlowRun, CreationStageRecord
from test_cartographer.creation_flow.template import render_reference_pom_proposal
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.enums import PatchReviewDecision
from test_cartographer.delivery.evaluation import build_creation_evaluation
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.io import (
    load_generation_profile,
    save_application_report,
    save_code_patch,
    save_creation_evaluation,
    save_generation_profile,
)
from test_cartographer.delivery.models import TestDataBinding, VerificationResult
from test_cartographer.delivery.review import review_code_patch
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox
from test_cartographer.discovery.apply import apply_accepted_discovery
from test_cartographer.discovery.assessment import assess_discovery
from test_cartographer.discovery.capture import capture_process_discovery
from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryProviderKind
from test_cartographer.discovery.io import (
    load_discovery_plan,
    load_discovery_profile,
    save_discovery_plan,
    save_discovery_run,
)
from test_cartographer.discovery.provider import OllamaDiscoveryProvider
from test_cartographer.guided_intake.engine import (
    available_questions,
    create_guided_run,
    finish_guided_run,
    plan_next_phase,
)
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.io import (
    load_minimal_seed,
    save_guided_run,
)
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.guided_intake.provider import OllamaGuidanceProvider
from test_cartographer.guided_intake.readiness import assess_guided_intake
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.io import save_session
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.seed import build_minimal_context
from test_cartographer.intake.session import create_session, record_answer
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision, SynthesisRunStatus
from test_cartographer.synthesis.io import save_synthesis_request, save_synthesis_run
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import build_synthesis_request
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[1]
TARGET_TEST = "tests/e2e/test_search_catalog.py"


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    return result, time.perf_counter() - started


def _verification(name: str, command: list[str], result: subprocess.CompletedProcess[str], seconds: float) -> VerificationResult:
    output = f"{result.stdout}\n{result.stderr}"
    return VerificationResult(
        name=name,
        command=" ".join(command),
        exit_code=result.returncode,
        duration_seconds=seconds,
        output_sha256=hashlib.sha256(output.encode("utf-8")).hexdigest(),
        passed=result.returncode == 0,
    )


def _apply_intake(session, plan, answers: dict[str, str], *, confirm: bool, start: datetime):
    current = session
    for index, item in enumerate(plan.questions, start=1):
        question = next(q for q in available_questions(current) if q.id == item.question_id)
        asked = start + timedelta(seconds=index * 2)
        current = record_answer(
            current,
            question=question,
            answer=IntakeAnswer(
                action=IntakeAnswerAction.CONFIRM if confirm else IntakeAnswerAction.PROVIDE,
                value=None if confirm else answers[item.question_id],
            ),
            asked_at=asked,
            answered_at=asked + timedelta(seconds=1),
            active_seconds=1.0,
            allow_reordering=True,
        )
    return current


def _candidate_with_test_id(run, value: str) -> str:
    for candidate in run.candidates:
        if any(item.name == "data-testid" and item.value == value for item in candidate.attributes):
            return candidate.id
    raise RuntimeError(f"candidate with data-testid={value} was not found")


def _stage(kind, started_at, completed_at, *, live=0, deterministic=0, browser=0, human=0, artifacts=(), summary=""):
    return CreationStageRecord(
        kind=kind,
        status=CreationStageStatus.PASSED,
        started_at=started_at,
        completed_at=completed_at,
        duration_seconds=max(0.0, (completed_at - started_at).total_seconds()),
        live_llm_calls=live,
        deterministic_operations=deterministic,
        browser_operations=browser,
        human_actions=human,
        artifact_ids=tuple(artifacts),
        summary=summary,
    )


def _write_summary(run: CreationFlowRun, target: Path) -> None:
    target.write_text(
        "\n".join(
            (
                "# TestCartographer creation-flow result",
                "",
                f"- Status: **{run.status.value}**",
                f"- Time to first runnable test: **{run.total_seconds:.2f}s**",
                f"- Local-LLM calls: **{run.live_llm_call_count}**",
                f"- Local-LLM time: **{run.model_seconds:.2f}s**",
                f"- Human actions represented by fixtures: **{run.total_human_action_count}**",
                f"- Browser candidates / targets: **{run.candidate_count} / {run.target_count}**",
                f"- Generated / modified files: **{run.generated_file_count} / {run.modified_file_count}**",
                f"- Tests collected / passed: **{run.collected_test_count} / {run.passed_test_count}**",
                "- Synthesis source: **deterministic reference template through the existing strict proposal protocol**",
                "- Comparative savings measured: **no**",
                "",
                "This is a fixture-assisted integration proof. Human answers, confirmations,",
                "ambiguity selection, and review decisions are explicit and counted rather than hidden.",
                "Creation mechanics are verified, but no interactive human trigger is exercised.",
                "The flow is ready for human-trigger integration, not yet for an external user demo.",
            )
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    parser.add_argument("--output-dir", default=".test-cartographer/sprint-10/live")
    parser.add_argument("--framework-root", type=Path)
    parser.add_argument("--require-browser", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    source_framework = (args.framework_root or ROOT / "testdata/framework/reference").resolve()
    original_framework_hash = _tree_hash(source_framework)
    profile = load_creation_flow_profile(ROOT / "testdata/creation_flow/profile/public_catalog_demo.json")
    flow_started_perf = time.perf_counter()
    flow_started_at = datetime.now(timezone.utc)
    stages: list[CreationStageRecord] = []

    with serve_reference_directory(ROOT / "testdata/browser") as application_base:
        application_url = f"{application_base}/public_catalog_discovery.html"
        answers = {
            "q_application_name": "Public catalog reference application",
            "q_application_environment": "Controlled local reference environment",
            "q_application_base_url": application_url,
            "q_process_name": "Search the public catalog",
            "q_process_purpose": "Allow a visitor to find matching catalog items.",
            "q_process_risk": "Search failures can hide relevant items.",
            "q_process_role": "Unauthenticated visitor",
            "q_precondition_1": "The catalog is available and contains indexed items.",
            "q_outcome_outcome_target": "Matching product results are visible for the supplied query.",
        }

        intake_started = datetime.now(timezone.utc)
        seed = load_minimal_seed(ROOT / "testdata/guided_intake/seed/product_search.json")
        if seed.initial_request != profile.minimal_request:
            raise RuntimeError("creation profile and minimal seed request differ")
        guided_profile = GuidedIntakeProfile(
            id="guided_creation_demo",
            provider=GuidanceProviderKind.OLLAMA,
            model=args.model,
            base_url=args.base_url,
            timeout_seconds=args.timeout_seconds,
            max_rounds=4,
            allowed_sensitivities=("public", "internal"),
            temperature=0.0,
            seed=42,
        )
        session = create_session(
            build_minimal_context(seed),
            session_id="intake_creation_demo",
            started_at=intake_started,
        )
        guided_run = create_guided_run(
            session,
            seed,
            guided_profile,
            run_id="guided_creation_demo",
            started_at=intake_started,
        )
        with OllamaGuidanceProvider(guided_profile) as provider:
            print("[1/7] Preloading local Ollama for guided intake...", flush=True)
            version = provider.preflight()
            print(f"Local Ollama {version}; model={args.model}")
            print("[1/7] Starting collection planning call (1/3 overall)...", flush=True)
            collection, guided_run = plan_next_phase(
                session,
                guided_run,
                seed,
                guided_profile,
                provider,
                started_at=datetime.now(timezone.utc),
            )
            print(f"Collection plan completed in {guided_run.turns[-1].latency_seconds:.2f}s.")
            session = _apply_intake(session, collection, answers, confirm=False, start=intake_started + timedelta(seconds=10))
            print("[1/7] Starting review planning call (2/3 overall)...", flush=True)
            review, guided_run = plan_next_phase(
                session,
                guided_run,
                seed,
                guided_profile,
                provider,
                started_at=datetime.now(timezone.utc),
            )
            print(f"Review plan completed in {guided_run.turns[-1].latency_seconds:.2f}s.")
            session = _apply_intake(session, review, answers, confirm=True, start=intake_started + timedelta(seconds=50))
        guided_run = finish_guided_run(guided_run, session, updated_at=datetime.now(timezone.utc))
        intake_report = assess_guided_intake(session, guided_run)
        if not intake_report.ready_for_guided_discovery or len(guided_run.turns) != 2:
            raise RuntimeError("guided intake did not reach discovery readiness")
        intake_completed = datetime.now(timezone.utc)
        save_session(session, output / "01-intake-session.json")
        save_guided_run(guided_run, output / "01-guided-intake-run.json")
        stages.append(_stage(
            CreationStageKind.GUIDED_INTAKE,
            intake_started,
            intake_completed,
            live=2,
            deterministic=profile.expected_answer_count + profile.expected_confirmation_count,
            human=profile.expected_answer_count + profile.expected_confirmation_count,
            artifacts=(session.id, guided_run.id),
            summary="Two live local-LLM plans ordered the deterministic collection and review questions; fixture answers remained human-authoritative.",
        ))

        discovery_started = datetime.now(timezone.utc)
        plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")
        plan = plan.model_copy(update={
            "context_id": session.context.id,
            "process_id": session.context.process.id,
            "source_url": application_url,
        })
        discovery_profile = load_discovery_profile(ROOT / "testdata/discovery/profile/ollama_local_qwen.json")
        discovery_profile = discovery_profile.model_copy(update={
            "model": args.model,
            "base_url": args.base_url,
            "timeout_seconds": args.timeout_seconds,
            "provider": DiscoveryProviderKind.OLLAMA,
        })
        discovery_run = capture_process_discovery(
            plan,
            discovery_profile,
            run_id="discovery_creation_demo",
            captured_at=discovery_started,
        )
        if len(discovery_run.ambiguities) != 1:
            raise RuntimeError("creation demo requires one bounded ambiguity")
        with OllamaDiscoveryProvider(discovery_profile) as provider:
            print("[2/7] Starting ambiguity question (3/3 overall)...", flush=True)
            provider.preflight()
            question, discovery_run = phrase_ambiguity(
                discovery_run,
                plan.targets,
                discovery_profile,
                provider,
                ambiguity_id=discovery_run.ambiguities[0].id,
                started_at=datetime.now(timezone.utc),
                completed_at=None,
            )
            print(f"Ambiguity question completed in {discovery_run.guidance_turns[-1].latency_seconds:.2f}s.")
            print(f"Clarification: {question.user_prompt}")
        selected = _candidate_with_test_id(discovery_run, "search-submit")
        discovery_run = resolve_ambiguity(
            discovery_run,
            ambiguity_id=discovery_run.ambiguities[0].id,
            selected_candidate_id=selected,
            resolved_at=datetime.now(timezone.utc),
            reason="Human reference decision selected the form submit button.",
        )
        discovery_run = review_discovery(
            discovery_run,
            decision=DiscoveryDecision.ACCEPTED,
            reviewed_at=datetime.now(timezone.utc),
            reason="All bounded candidates, selections, and locators were reviewed.",
            review_seconds=1.0,
        )
        discovered_context = apply_accepted_discovery(session.context, plan, discovery_run)
        discovery_report = assess_discovery(discovery_run)
        if not discovery_report.ready_for_context_application or not assess_readiness(discovered_context).ready:
            raise RuntimeError("accepted discovery did not reach context readiness")
        discovery_completed = datetime.now(timezone.utc)
        save_discovery_plan(plan, output / "02-discovery-plan.json")
        save_discovery_run(discovery_run, output / "02-discovery-run.json")
        save_context(discovered_context, output / "02-discovered-context.json")
        stages.append(_stage(
            CreationStageKind.BROWSER_DISCOVERY,
            discovery_started,
            discovery_completed,
            live=1,
            deterministic=len(discovery_run.targets) - 1,
            browser=1,
            human=2,
            artifacts=(plan.id, discovery_run.id, discovered_context.id),
            summary="Chromium captured four bounded candidates; rules selected two targets and one human decision resolved the allowlisted ambiguity.",
        ))

        handoff_started = datetime.now(timezone.utc)
        synthesis_context = confirm_synthesis_handoff(discovered_context, confirmed_at=datetime.now(timezone.utc))
        request = build_synthesis_request(
            synthesis_context,
            request_id="synreq_creation_demo",
            created_at=datetime.now(timezone.utc),
        )
        handoff_completed = datetime.now(timezone.utc)
        save_context(synthesis_context, output / "03-synthesis-ready-context.json")
        save_synthesis_request(request, output / "03-synthesis-request.json")
        stages.append(_stage(
            CreationStageKind.SYNTHESIS_HANDOFF,
            handoff_started,
            handoff_completed,
            deterministic=1,
            human=profile.expected_handoff_confirmation_count,
            artifacts=(synthesis_context.id, request.id, "ev_creation_handoff"),
            summary="A separate human handoff confirmed the four remaining synthesis-required PROVIDED values required by the stricter synthesis authority boundary.",
        ))

        synthesis_started = datetime.now(timezone.utc)
        raw_proposal = render_reference_pom_proposal(request)
        adapter = ReplaySynthesisAdapter(raw_proposal)
        synthesis_run = run_synthesis(
            request,
            adapter,
            run_id="synrun_creation_demo",
            started_at=synthesis_started,
            completed_at=datetime.now(timezone.utc),
        )
        if synthesis_run.status is not SynthesisRunStatus.READY_FOR_REVIEW:
            raise RuntimeError(f"reference synthesis failed: {synthesis_run.status.value}")
        synthesis_run = review_synthesis_run(
            synthesis_run,
            decision=ProposalReviewDecision.ACCEPTED,
            reviewed_at=datetime.now(timezone.utc),
            reason="Reference POM boundaries and exact source traceability were reviewed.",
            review_seconds=2.0,
        )
        synthesis_completed = datetime.now(timezone.utc)
        save_synthesis_run(synthesis_run, output / "04-synthesis-run.json")
        stages.append(_stage(
            CreationStageKind.POM_SYNTHESIS,
            synthesis_started,
            synthesis_completed,
            deterministic=1,
            human=1,
            artifacts=(request.id, synthesis_run.id, synthesis_run.proposal.id),
            summary="A deterministic reference template traversed the existing strict POM proposal parser, semantic validator, and human review boundary.",
        ))

        adaptation_started = datetime.now(timezone.utc)
        workspace_profile = load_workspace_profile(ROOT / "testdata/adaptation/profile/qa_automation_framework.json")
        snapshot = inspect_framework(
            source_framework,
            workspace_profile,
            snapshot_id="snapshot_creation_demo",
            captured_at=datetime.now(timezone.utc),
        )
        adaptation_plan = build_adaptation_plan(
            synthesis_run,
            workspace_profile,
            snapshot,
            plan_id="adapt_creation_demo",
            created_at=datetime.now(timezone.utc),
        )
        adaptation_plan = review_adaptation_plan(
            adaptation_plan,
            decision=AdaptationReviewDecision.ACCEPTED,
            reviewed_at=datetime.now(timezone.utc),
            reason="The exact page, component, fixture, and test targets fit the inspected framework.",
            review_seconds=2.0,
        )
        adaptation_completed = datetime.now(timezone.utc)
        save_framework_snapshot(snapshot, output / "05-framework-snapshot.json")
        save_adaptation_plan(adaptation_plan, output / "05-adaptation-plan.json")
        stages.append(_stage(
            CreationStageKind.ADAPTATION_PLANNING,
            adaptation_started,
            adaptation_completed,
            deterministic=len(adaptation_plan.operations),
            human=1,
            artifacts=(snapshot.id, adaptation_plan.id),
            summary="Read-only repository inspection mapped the accepted POM to four exact framework operations before any source write.",
        ))

        delivery_started = datetime.now(timezone.utc)
        generation_profile = load_generation_profile(ROOT / "testdata/delivery/profile/public_search_generation.json")
        source_binding = generation_profile.test_data_bindings[0]
        generation_profile = generation_profile.model_copy(update={
            "id": "generation_creation_demo",
            "test_data_bindings": (
                TestDataBinding(
                    test_data_id=request.test_data[0].id,
                    fixture_key=source_binding.fixture_key,
                    value=source_binding.value,
                    sensitivity=source_binding.sensitivity,
                    secret=False,
                ),
            ),
        })
        patch = build_code_patch(
            synthesis_run,
            adaptation_plan,
            workspace_profile,
            generation_profile,
            snapshot,
            source_framework,
            patch_id="patch_creation_demo",
            created_at=datetime.now(timezone.utc),
        )
        patch = review_code_patch(
            patch,
            decision=PatchReviewDecision.ACCEPTED,
            reviewed_at=datetime.now(timezone.utc),
            reason="Exact generated source was reviewed for the reference demo.",
            review_seconds=2.0,
        )
        sandbox = output / "sandbox" / "qa-automation-framework"
        materialize_snapshot_sandbox(source_framework, sandbox, workspace_profile, snapshot)
        application = apply_code_patch(
            patch,
            workspace_profile,
            snapshot,
            sandbox,
            application_id="apply_creation_demo",
            applied_at=datetime.now(timezone.utc),
        )
        delivery_completed = datetime.now(timezone.utc)
        save_generation_profile(generation_profile, output / "06-generation-profile.json")
        save_code_patch(patch, output / "06-code-patch.json")
        save_application_report(application, output / "06-patch-application.json")
        stages.append(_stage(
            CreationStageKind.SOURCE_DELIVERY,
            delivery_started,
            delivery_completed,
            deterministic=len(patch.changes) + len(patch.reused_targets),
            human=1,
            artifacts=(generation_profile.id, patch.id, application.id),
            summary="The reviewed patch was applied only to a snapshot-bounded sandbox; the original framework remained untouched.",
        ))

        execution_started = datetime.now(timezone.utc)
        compile_command = [sys.executable, "-m", "compileall", "-q", "pages", "components", "tests", "testdata"]
        compile_result, compile_seconds = _run(compile_command, sandbox)
        collect_command = [sys.executable, "-m", "pytest", "--collect-only", "-q", TARGET_TEST]
        collect_result, collect_seconds = _run(collect_command, sandbox)
        env = os.environ.copy()
        env["TEST_CARTOGRAPHER_CATALOG_URL"] = application_url
        test_command = [sys.executable, "-m", "pytest", "-q", TARGET_TEST]
        test_result, test_seconds = _run(test_command, sandbox, env)
        output_text = f"{test_result.stdout}\n{test_result.stderr}"
        browser_unavailable = test_result.returncode != 0 and any(
            marker in output_text
            for marker in ("Executable doesn't exist", "Failed to launch", "ERR_BLOCKED_BY_ADMINISTRATOR")
        )
        if browser_unavailable and not args.require_browser:
            print("External-demo browser gate skipped by environment policy.")
            return 0
        verification_results = (
            _verification("compileall", compile_command, compile_result, compile_seconds),
            _verification("collect_target", collect_command, collect_result, collect_seconds),
            _verification("execute_target", test_command, test_result, test_seconds),
        )
        verification_seconds = compile_seconds + collect_seconds + test_seconds
        creation_evaluation = build_creation_evaluation(
            synthesis_run,
            adaptation_plan,
            patch,
            application,
            evaluation_id="creation_eval_external_demo",
            completed_at=datetime.now(timezone.utc),
            target_test=TARGET_TEST,
            collected_test_count=1 if collect_result.returncode == 0 else 0,
            passed_test_count=1 if test_result.returncode == 0 else 0,
            verification_results=verification_results,
            verification_seconds=verification_seconds,
            time_to_first_runnable_test_seconds=time.perf_counter() - flow_started_perf,
            original_framework_unchanged=_tree_hash(source_framework) == original_framework_hash,
            corrections=(
                "Sprint 10 added a separate synthesis-handoff confirmation because discovery readiness still retained four synthesis-required PROVIDED values.",
                "Reference synthesis remains deterministic and is reported separately from the three live local-LLM interview turns.",
            ),
        )
        execution_completed = datetime.now(timezone.utc)
        save_creation_evaluation(creation_evaluation, output / "07-creation-evaluation.json")
        stages.append(_stage(
            CreationStageKind.FRAMEWORK_EXECUTION,
            execution_started,
            execution_completed,
            deterministic=3,
            browser=1,
            artifacts=(creation_evaluation.id,),
            summary="The generated test compiled, was collected once, and passed in Chromium without TestCartographer or an LLM in the execution process.",
        ))

    flow_completed_at = datetime.now(timezone.utc)
    model_seconds = sum(turn.latency_seconds for turn in guided_run.turns) + sum(
        turn.latency_seconds for turn in discovery_run.guidance_turns
    )
    generated_files = creation_evaluation.generated_file_count
    modified_files = creation_evaluation.modified_file_count
    total_human_actions = (
        profile.expected_answer_count
        + profile.expected_confirmation_count
        + profile.expected_handoff_confirmation_count
        + profile.expected_ambiguity_resolution_count
        + profile.expected_review_decision_count
    )
    run = CreationFlowRun(
        id="creation_flow_external_demo",
        profile_id=profile.id,
        context_id=synthesis_context.id,
        status=CreationFlowStatus.PASSED,
        started_at=flow_started_at,
        completed_at=flow_completed_at,
        target_test=TARGET_TEST,
        stages=tuple(stages),
        total_seconds=time.perf_counter() - flow_started_perf,
        model_seconds=model_seconds,
        browser_seconds=discovery_run.capture_seconds + test_seconds,
        verification_seconds=verification_seconds,
        human_active_seconds=session.metrics.active_seconds + discovery_run.review_seconds + 8.0,
        live_llm_call_count=len(guided_run.turns) + len(discovery_run.guidance_turns),
        deterministic_synthesis_call_count=1,
        human_answer_count=profile.expected_answer_count,
        human_confirmation_count=profile.expected_confirmation_count,
        handoff_confirmation_count=profile.expected_handoff_confirmation_count,
        ambiguity_resolution_count=profile.expected_ambiguity_resolution_count,
        review_decision_count=profile.expected_review_decision_count,
        total_human_action_count=total_human_actions,
        candidate_count=len(discovery_run.candidates),
        target_count=len(discovery_run.targets),
        generated_file_count=generated_files,
        modified_file_count=modified_files,
        reused_symbol_count=creation_evaluation.reused_symbol_count,
        collected_test_count=creation_evaluation.collected_test_count,
        passed_test_count=creation_evaluation.passed_test_count,
        live_llm_used=True,
        framework_execution_independent=creation_evaluation.framework_execution_independent,
        original_framework_unchanged=creation_evaluation.original_framework_unchanged,
        full_traceability=(
            request.context_id == synthesis_run.proposal.context_id
            == adaptation_plan.context_id
            == patch.context_id
            == creation_evaluation.context_id
        ),
    )
    report = assess_creation_flow(run)
    if not report.creation_mechanics_verified:
        raise RuntimeError(
            f"integrated creation mechanics are not verified: {report.mechanics_blockers}"
        )
    if not report.ready_for_human_trigger_integration:
        raise RuntimeError("creation flow is not ready for human-trigger integration")
    if report.ready_for_external_user_demo:
        raise RuntimeError("fixture-assisted verifier must not claim external user-demo readiness")
    save_creation_flow_run(run, output / "creation-flow-run.json")
    _write_summary(run, output / "creation-flow-summary.md")

    print("")
    print("Creation Flow completed successfully.")
    print(f"Short request: {profile.minimal_request}")
    print(f"Time to first runnable test: {run.total_seconds:.2f}s")
    print(f"Local-LLM calls / time: {run.live_llm_call_count} / {run.model_seconds:.2f}s")
    print(f"Human fixture actions: {run.total_human_action_count}")
    print(f"Candidates / targets / human ambiguity decisions: {run.candidate_count} / {run.target_count} / {run.ambiguity_resolution_count}")
    print(f"Generated / modified files: {run.generated_file_count} / {run.modified_file_count}")
    print(f"Tests collected / passed: {run.collected_test_count} / {run.passed_test_count}")
    print("Framework execution independent: true")
    print("Original framework unchanged: true")
    print("Raw prompts and raw responses persisted: false")
    print("Comparative savings measured or claimed: false")
    print("Creation mechanics verified: true")
    print("Ready for human-trigger integration: true")
    print("Interactive human trigger used: false")
    print("Ready for external user demonstration: false")
    print(f"Artifacts: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
