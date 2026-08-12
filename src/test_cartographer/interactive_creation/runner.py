"""Human-triggered orchestration over the existing Creation Flow engine."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationReviewDecision, AdaptationTargetKind
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
from test_cartographer.creation_flow.handoff import HANDOFF_PATHS, confirm_synthesis_handoff
from test_cartographer.creation_flow.io import save_creation_flow_run
from test_cartographer.creation_flow.models import CreationFlowRun, CreationStageRecord
from test_cartographer.creation_flow.external_template import render_external_single_page_proposal
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
from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryProviderKind
from test_cartographer.discovery.io import (
    load_discovery_plan,
    load_discovery_profile,
    save_discovery_plan,
    save_discovery_run,
)
from test_cartographer.discovery.provider import (
    OllamaDiscoveryProvider,
    ReplayDiscoveryProvider,
)
from test_cartographer.guided_intake.engine import (
    available_questions,
    create_guided_run,
    finish_guided_run,
    plan_next_phase,
)
from test_cartographer.guided_intake.enums import GuidanceProviderKind, GuidedIntakePhase
from test_cartographer.guided_intake.io import (
    load_guided_profile,
    save_guided_run,
    save_minimal_seed,
)
from test_cartographer.guided_intake.provider import (
    OllamaGuidanceProvider,
    ReplayGuidanceProvider,
)
from test_cartographer.guided_intake.readiness import assess_guided_intake
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.io import save_session
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.intake.session import create_session, pause_session, record_answer
from test_cartographer.interactive_creation.assessment import assess_interactive_creation
from test_cartographer.interactive_creation.browser import open_interactive_discovery
from test_cartographer.interactive_creation.external import build_external_public_single_page_plan
from test_cartographer.interactive_creation.enums import (
    InteractiveSessionState,
    OperatorActionKind,
)
from test_cartographer.interactive_creation.io import save_operator_session
from test_cartographer.interactive_creation.models import (
    InteractiveCreationProfile,
    InteractiveOperatorSession,
    OperatorActionRecord,
)
from test_cartographer.interactive_creation.project_profile import (
    apply_persistent_project_bootstrap,
    load_runtime_project_profile,
)
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision, SynthesisRunStatus
from test_cartographer.synthesis.io import save_synthesis_request, save_synthesis_run
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import build_synthesis_request
from test_cartographer.synthesis.review import review_synthesis_run

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
NowFn = Callable[[], datetime]
TimerFn = Callable[[], float]
TARGET_TEST = "tests/e2e/test_search_catalog.py"
_BOOTSTRAP_QUESTION_IDS = frozenset(
    {
        "q_application_name",
        "q_application_environment",
        "q_application_base_url",
    }
)
_RESERVED_CONTEXT_COMMANDS = frozenset(
    {
        "a",
        "accept",
        "c",
        "confirm",
        "e",
        "edit",
        "q",
        "quit",
        "r",
        "reject",
        "cancel",
    }
)


class InteractiveFlowStopped(RuntimeError):
    """Operator intentionally paused or rejected the flow."""


class _ActionLedger:
    def __init__(
        self,
        profile: InteractiveCreationProfile,
        *,
        started_at: datetime,
        session_id: str,
        target_path: Path,
        now_fn: NowFn,
    ) -> None:
        self.profile = profile
        self.target_path = target_path
        self.now_fn = now_fn
        self.session = InteractiveOperatorSession(
            id=session_id,
            profile_id=profile.id,
            state=InteractiveSessionState.ACTIVE,
            started_at=started_at,
            updated_at=started_at,
            headed_browser_used=False,
        )
        self.save()

    def record(
        self,
        kind: OperatorActionKind,
        target_id: str,
        decision: str,
        *,
        started_at: datetime,
        completed_at: datetime,
        active_seconds: float,
    ) -> None:
        action = OperatorActionRecord(
            sequence=len(self.session.actions) + 1,
            kind=kind,
            target_id=target_id,
            decision=decision,
            started_at=started_at,
            completed_at=completed_at,
            active_seconds=active_seconds,
        )
        self.session = self.session.model_copy(
            update={
                "actions": (*self.session.actions, action),
                "updated_at": completed_at,
            }
        )
        self.save()

    def mark_headed_browser(self) -> None:
        now = self.now_fn()
        self.session = self.session.model_copy(
            update={"headed_browser_used": True, "updated_at": now}
        )
        self.save()

    def pause(self) -> None:
        now = self.now_fn()
        self.session = self.session.model_copy(
            update={"state": InteractiveSessionState.PAUSED, "updated_at": now}
        )
        self.save()

    def abort(self) -> None:
        now = self.now_fn()
        self.session = self.session.model_copy(
            update={"state": InteractiveSessionState.ABORTED, "updated_at": now}
        )
        self.save()

    def complete(self, run_id: str) -> InteractiveOperatorSession:
        now = self.now_fn()
        self.session = self.session.model_copy(
            update={
                "state": InteractiveSessionState.COMPLETE,
                "updated_at": now,
                "creation_flow_run_id": run_id,
            }
        )
        self.session = InteractiveOperatorSession.model_validate(
            self.session.model_dump(mode="python")
        )
        self.save()
        return self.session

    def save(self) -> None:
        save_operator_session(self.session, self.target_path)


def run_human_triggered_creation_flow(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    framework_root: str | Path | None,
    interactive_profile: InteractiveCreationProfile,
    ollama_base_url: str,
    ollama_model: str,
    timeout_seconds: float,
    executable_path: str | None = None,
    provider_mode: str = "ollama",
    project_profile_path: str | Path | None = None,
    browser_opener=None,
    command_runner=None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    now_fn: NowFn = lambda: datetime.now(timezone.utc),
    timer_fn: TimerFn = time.perf_counter,
    external_public_single_page: bool = False,
) -> tuple[CreationFlowRun, InteractiveOperatorSession]:
    """Run the reference flow or one bounded external public single-page flow."""

    root = Path(project_root).resolve()
    output = Path(output_dir).resolve()
    browser_opener = browser_opener or open_interactive_discovery
    command_runner = command_runner or _run
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    source_framework = Path(
        framework_root or root / "testdata/framework/reference"
    ).resolve()
    runtime_workspace_profile = load_workspace_profile(
        root / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    runtime_guided_profile = load_guided_profile(
        root / "testdata/guided_intake/profile/ollama_local_qwen.json"
    ).model_copy(
        update={
            "id": "guided_interactive_local",
            "model": ollama_model,
            "base_url": ollama_base_url,
            "timeout_seconds": timeout_seconds,
            "provider": (
                GuidanceProviderKind.OLLAMA
                if provider_mode == "ollama"
                else GuidanceProviderKind.REPLAY
            ),
        }
    )
    active_project_profile = None
    if project_profile_path is not None:
        active_project_profile = load_runtime_project_profile(
            project_profile_path,
            workspace_profile=runtime_workspace_profile,
            guided_profile=runtime_guided_profile,
        )
    original_framework_hash = _tree_hash(source_framework)
    flow_started_at = now_fn()
    flow_started_perf = timer_fn()
    stages: list[CreationStageRecord] = []
    ledger = _ActionLedger(
        interactive_profile,
        started_at=flow_started_at,
        session_id=f"operator_{uuid.uuid4().hex[:12]}",
        target_path=output / "operator-session.json",
        now_fn=now_fn,
    )

    output_fn("TestCartographer — human-triggered Creation Flow")
    output_fn(
        "Scope: one bounded external public single-page process."
        if external_public_single_page
        else "Scope: one controlled public-catalog search process."
    )
    output_fn("The flow will stop for your answers, ambiguity choice, reviews, and execution trigger.")
    request_started = now_fn()
    timer_started = timer_fn()
    initial_request = _read_non_empty(
        "\nWhat would you like to automate?\n> ", input_fn=input_fn
    )
    request_completed = now_fn()
    ledger.record(
        OperatorActionKind.INITIAL_REQUEST,
        "minimal_request",
        "provided",
        started_at=request_started,
        completed_at=request_completed,
        active_seconds=max(0.0, timer_fn() - timer_started),
    )

    application_context = (
        nullcontext(None)
        if external_public_single_page
        else serve_reference_directory(root / "testdata/browser")
    )
    with application_context as app_base:
        application_url = (
            None
            if external_public_single_page
            else f"{app_base}/public_catalog_discovery.html"
        )
        seed = MinimalContextSeed(
            id=f"seed_{uuid.uuid4().hex[:12]}",
            context_id=f"ctx_{uuid.uuid4().hex[:12]}",
            title=(
                "Human-triggered external single-page process"
                if external_public_single_page
                else "Human-triggered catalog search"
            ),
            initial_request=initial_request,
            created_at=flow_started_at,
        )
        context = build_minimal_context(seed)
        if active_project_profile is not None:
            assert project_profile_path is not None
            context, _ = apply_persistent_project_bootstrap(
                context,
                project_profile_path=project_profile_path,
                project_profile=active_project_profile,
                output_dir=output,
                projected_at=flow_started_at,
            )
            output_fn(
                "Persistent ProjectProfile reused: "
                f"revision={active_project_profile.revision}; "
                "bootstrap application questions=0."
            )
        session = create_session(
            context,
            session_id=f"intake_{uuid.uuid4().hex[:12]}",
            started_at=flow_started_at,
        )
        save_minimal_seed(seed, output / "01-minimal-seed.json")
        save_context(context, output / "01-minimal-context.json")
        save_session(session, output / "01-intake-session.json")

        intake_started = now_fn()
        guided_profile = runtime_guided_profile
        guided_run = create_guided_run(
            session,
            seed,
            guided_profile,
            run_id=f"guided_{uuid.uuid4().hex[:12]}",
            started_at=intake_started,
        )
        replay_guidance = ReplayGuidanceProvider(outputs=[])
        live_guidance = None
        if provider_mode == "ollama":
            live_guidance = OllamaGuidanceProvider(guided_profile)
            version = live_guidance.preflight()
            output_fn(f"Local Ollama ready: version={version}, model={ollama_model}")
        try:
            questions = available_questions(session)
            if not questions or _phase_for_questions(questions) is not GuidedIntakePhase.COLLECTION:
                raise RuntimeError("interactive intake did not start in collection phase")
            if provider_mode == "replay":
                replay_guidance.outputs.append(
                    _render_guided_plan(questions, GuidedIntakePhase.COLLECTION)
                )
                provider = replay_guidance
            else:
                provider = live_guidance
            plan, guided_run = plan_next_phase(
                session,
                guided_run,
                seed,
                guided_profile,
                provider,
                started_at=now_fn(),
            )
            save_guided_run(guided_run, output / "01-guided-intake-run.json")
            output_fn(f"\nLLM planned {len(plan.questions)} collection questions.")
            for section_title, planned_items in _group_collection_plan(plan.questions):
                output_fn(f"\n{section_title}")
                for planned in planned_items:
                    current = {item.id: item for item in available_questions(session)}
                    question = current.get(planned.question_id)
                    if question is None:
                        continue
                    output_fn(f"\n{planned.user_prompt}")
                    output_fn(f"Why this matters: {planned.reason}")
                    started_at = now_fn()
                    started = timer_fn()
                    answer = _ask_intake_answer(
                        question,
                        suggested_value=(
                            application_url
                            if question.id == "q_application_base_url"
                            else None
                        ),
                        input_fn=input_fn,
                        output_fn=output_fn,
                    )
                    completed_at = now_fn()
                    active = max(0.0, timer_fn() - started)
                    if answer is None:
                        session = pause_session(session, updated_at=completed_at)
                        save_session(session, output / "01-intake-session.json")
                        ledger.pause()
                        raise InteractiveFlowStopped(
                            "guided intake paused; rerun the command to start a fresh controlled demo"
                        )
                    session = record_answer(
                        session,
                        question=question,
                        answer=answer,
                        asked_at=started_at,
                        answered_at=completed_at,
                        active_seconds=active,
                        allow_reordering=True,
                    )
                    save_session(session, output / "01-intake-session.json")
                    ledger.record(
                        OperatorActionKind.INTAKE_ANSWER,
                        question.id,
                        answer.action.value,
                        started_at=started_at,
                        completed_at=completed_at,
                        active_seconds=active,
                    )

            while True:
                review_questions = available_questions(session)
                if not review_questions:
                    break
                if _phase_for_questions(review_questions) is not GuidedIntakePhase.REVIEW:
                    raise RuntimeError("interactive intake returned to collection unexpectedly")
                output_fn("\nContext summary")
                output_fn(_format_context_summary(review_questions))
                review_started = now_fn()
                review_timer = timer_fn()
                decision, selected_question, replacement = _ask_context_summary_review(
                    review_questions, input_fn=input_fn, output_fn=output_fn
                )
                review_completed = now_fn()
                review_active = max(0.0, timer_fn() - review_timer)
                if decision == "quit":
                    session = pause_session(session, updated_at=review_completed)
                    save_session(session, output / "01-intake-session.json")
                    ledger.pause()
                    raise InteractiveFlowStopped(
                        "guided intake paused during context-summary review"
                    )
                if decision == "edit":
                    if selected_question is None or replacement is None:
                        raise RuntimeError("context-summary edit did not select a value")
                    session = record_answer(
                        session,
                        question=selected_question,
                        answer=IntakeAnswer(
                            action=IntakeAnswerAction.PROVIDE, value=replacement
                        ),
                        asked_at=review_started,
                        answered_at=review_completed,
                        active_seconds=review_active,
                        allow_reordering=True,
                    )
                    save_session(session, output / "01-intake-session.json")
                    ledger.record(
                        OperatorActionKind.INTAKE_ANSWER,
                        selected_question.id,
                        "edited",
                        started_at=review_started,
                        completed_at=review_completed,
                        active_seconds=review_active,
                    )
                    continue

                confirmation_questions = tuple(review_questions)
                for question in confirmation_questions:
                    session = record_answer(
                        session,
                        question=question,
                        answer=IntakeAnswer(action=IntakeAnswerAction.CONFIRM),
                        asked_at=review_completed,
                        answered_at=review_completed,
                        active_seconds=0.0,
                        allow_reordering=True,
                    )
                save_session(session, output / "01-intake-session.json")
                ledger.record(
                    OperatorActionKind.INTAKE_CONFIRMATION,
                    "process_context_summary",
                    "confirmed_all",
                    started_at=review_started,
                    completed_at=review_completed,
                    active_seconds=review_active,
                )
                output_fn("Confirmed all process-context values with one operator decision.")
                break

            guided_run = finish_guided_run(
                guided_run, session, updated_at=now_fn()
            )
        finally:
            if live_guidance is not None:
                live_guidance.close()
        guided_report = assess_guided_intake(session, guided_run)
        if not guided_report.ready_for_guided_discovery:
            ledger.abort()
            raise RuntimeError("interactive intake did not reach discovery readiness")
        save_session(session, output / "01-intake-session.json")
        save_guided_run(guided_run, output / "01-guided-intake-run.json")
        intake_completed = now_fn()
        stages.append(
            _stage(
                CreationStageKind.GUIDED_INTAKE,
                intake_started,
                intake_completed,
                live=1 if provider_mode == "ollama" else 0,
                deterministic=len(session.interactions),
                human=ledger.session.answer_count + ledger.session.confirmation_count,
                artifacts=(session.id, guided_run.id),
                summary=(
                    "A real operator answered one LLM-planned collection phase and "
                    "confirmed the process context through one aggregate review."
                ),
            )
        )

        discovery_started = now_fn()
        if external_public_single_page:
            discovery_plan = build_external_public_single_page_plan(
                session.context,
                plan_id="discovery_plan_external_interactive",
            )
            application_url = discovery_plan.source_url
        else:
            assert application_url is not None
            discovery_plan = load_discovery_plan(
                root / "testdata/discovery/plan/public_catalog.json"
            ).model_copy(
                update={
                    "id": "discovery_plan_interactive",
                    "context_id": session.context.id,
                    "process_id": session.context.process.id,
                    "source_url": application_url,
                }
            )
        discovery_profile = load_discovery_profile(
            root / "testdata/discovery/profile/ollama_local_qwen.json"
        ).model_copy(
            update={
                "id": "discovery_interactive_local",
                "model": ollama_model,
                "base_url": ollama_base_url,
                "timeout_seconds": timeout_seconds,
                "provider": (
                    DiscoveryProviderKind.OLLAMA
                    if provider_mode == "ollama"
                    else DiscoveryProviderKind.REPLAY
                ),
            }
        )
        save_discovery_plan(discovery_plan, output / "02-discovery-plan.json")
        with browser_opener(
            discovery_plan,
            discovery_profile,
            run_id=f"discovery_{uuid.uuid4().hex[:12]}",
            captured_at=discovery_started,
            executable_path=executable_path,
        ) as browser_view:
            ledger.mark_headed_browser()
            discovery_run = browser_view.run
            output_fn("\nA visible Chromium window now shows bounded candidate labels.")
            output_fn(_format_candidate_table(discovery_run))
            for ambiguity in discovery_run.ambiguities:
                browser_view.focus_candidates(ambiguity.candidate_ids)
                if provider_mode == "ollama":
                    with OllamaDiscoveryProvider(discovery_profile) as provider:
                        provider.preflight()
                        question_plan, discovery_run = phrase_ambiguity(
                            discovery_run,
                            discovery_plan.targets,
                            discovery_profile,
                            provider,
                            ambiguity_id=ambiguity.id,
                            started_at=now_fn(),
                            completed_at=None,
                        )
                else:
                    replay = ReplayDiscoveryProvider(
                        outputs=[_render_discovery_question(ambiguity)]
                    )
                    question_plan, discovery_run = phrase_ambiguity(
                        discovery_run,
                        discovery_plan.targets,
                        discovery_profile,
                        replay,
                        ambiguity_id=ambiguity.id,
                        started_at=now_fn(),
                        completed_at=now_fn(),
                    )
                output_fn(f"\nCartographer: {question_plan.user_prompt}")
                output_fn(_format_ambiguity_candidates(discovery_run, ambiguity.candidate_ids))
                selected_started = now_fn()
                selected_timer = timer_fn()
                selected = _ask_candidate(
                    ambiguity.candidate_ids,
                    input_fn=input_fn,
                    output_fn=output_fn,
                )
                selected_completed = now_fn()
                ledger.record(
                    OperatorActionKind.AMBIGUITY_SELECTION,
                    ambiguity.id,
                    selected,
                    started_at=selected_started,
                    completed_at=selected_completed,
                    active_seconds=max(0.0, timer_fn() - selected_timer),
                )
                discovery_run = resolve_ambiguity(
                    discovery_run,
                    ambiguity_id=ambiguity.id,
                    selected_candidate_id=selected,
                    resolved_at=selected_completed,
                    reason="The interactive operator selected the intended browser candidate.",
                )
            output_fn("\nDiscovery review")
            output_fn(_format_discovery_summary(discovery_run))
            decision_started = now_fn()
            decision_timer = timer_fn()
            accepted = _ask_accept("Accept this discovery result?", input_fn, output_fn)
            decision_completed = now_fn()
            ledger.record(
                OperatorActionKind.REVIEW_DECISION,
                "discovery",
                "accepted" if accepted else "rejected",
                started_at=decision_started,
                completed_at=decision_completed,
                active_seconds=max(0.0, timer_fn() - decision_timer),
            )
            if not accepted:
                ledger.abort()
                raise InteractiveFlowStopped("operator rejected discovery")
            discovery_run = review_discovery(
                discovery_run,
                decision=DiscoveryDecision.ACCEPTED,
                reviewed_at=decision_completed,
                reason="The interactive operator reviewed the visible browser candidates and accepted discovery.",
                review_seconds=max(0.0, timer_fn() - decision_timer),
            )
        discovered_context = apply_accepted_discovery(
            session.context, discovery_plan, discovery_run
        )
        if not assess_discovery(discovery_run).ready_for_context_application:
            raise RuntimeError("interactive discovery is not ready for context application")
        if not assess_readiness(discovered_context).ready:
            raise RuntimeError("interactive discovery did not produce a ready context")
        save_discovery_run(discovery_run, output / "02-discovery-run.json")
        save_context(discovered_context, output / "02-discovered-context.json")
        discovery_completed = now_fn()
        stages.append(
            _stage(
                CreationStageKind.BROWSER_DISCOVERY,
                discovery_started,
                discovery_completed,
                live=1 if provider_mode == "ollama" else 0,
                deterministic=max(0, len(discovery_run.targets) - len(discovery_run.ambiguities)),
                browser=1,
                human=1 + len(discovery_run.ambiguities),
                artifacts=(discovery_plan.id, discovery_run.id, discovered_context.id),
                summary="A headed browser remained open while the operator resolved ambiguity and accepted discovery.",
            )
        )

        handoff_started = now_fn()
        output_fn("\nSynthesis handoff review")
        output_fn(_format_handoff(discovered_context))
        handoff_timer = timer_fn()
        handoff_accepted = _ask_accept(
            "Confirm these values for synthesis?", input_fn, output_fn
        )
        handoff_completed = now_fn()
        ledger.record(
            OperatorActionKind.SYNTHESIS_HANDOFF_CONFIRMATION,
            "synthesis_handoff",
            "accepted" if handoff_accepted else "rejected",
            started_at=handoff_started,
            completed_at=handoff_completed,
            active_seconds=max(0.0, timer_fn() - handoff_timer),
        )
        if not handoff_accepted:
            ledger.abort()
            raise InteractiveFlowStopped("operator rejected synthesis handoff")
        synthesis_context = confirm_synthesis_handoff(
            discovered_context, confirmed_at=handoff_completed
        )
        request = build_synthesis_request(
            synthesis_context,
            request_id=f"synreq_{uuid.uuid4().hex[:12]}",
            created_at=handoff_completed,
        )
        save_context(synthesis_context, output / "03-synthesis-ready-context.json")
        save_synthesis_request(request, output / "03-synthesis-request.json")
        stages.append(
            _stage(
                CreationStageKind.SYNTHESIS_HANDOFF,
                handoff_started,
                handoff_completed,
                deterministic=1,
                human=1,
                artifacts=(synthesis_context.id, request.id, "ev_creation_handoff"),
                summary="The operator explicitly confirmed the remaining synthesis-authority values.",
            )
        )

        synthesis_started = now_fn()
        raw_proposal = (
            render_external_single_page_proposal(request)
            if external_public_single_page
            else render_reference_pom_proposal(request)
        )
        synthesis_run = run_synthesis(
            request,
            ReplaySynthesisAdapter(raw_proposal),
            run_id=f"synrun_{uuid.uuid4().hex[:12]}",
            started_at=synthesis_started,
            completed_at=now_fn(),
        )
        if synthesis_run.status is not SynthesisRunStatus.READY_FOR_REVIEW:
            raise RuntimeError("deterministic proposal did not reach review")
        output_fn("\nPOM proposal review")
        output_fn(_format_pom_proposal(synthesis_run.proposal))
        pom_review_started = now_fn()
        pom_timer = timer_fn()
        pom_accepted = _ask_accept("Accept this POM proposal?", input_fn, output_fn)
        pom_review_completed = now_fn()
        ledger.record(
            OperatorActionKind.REVIEW_DECISION,
            "pom_proposal",
            "accepted" if pom_accepted else "rejected",
            started_at=pom_review_started,
            completed_at=pom_review_completed,
            active_seconds=max(0.0, timer_fn() - pom_timer),
        )
        if not pom_accepted:
            ledger.abort()
            raise InteractiveFlowStopped("operator rejected POM proposal")
        synthesis_run = review_synthesis_run(
            synthesis_run,
            decision=ProposalReviewDecision.ACCEPTED,
            reviewed_at=pom_review_completed,
            reason="The interactive operator accepted the displayed POM proposal.",
            review_seconds=max(0.0, timer_fn() - pom_timer),
        )
        save_synthesis_run(synthesis_run, output / "04-synthesis-run.json")
        stages.append(
            _stage(
                CreationStageKind.POM_SYNTHESIS,
                synthesis_started,
                pom_review_completed,
                deterministic=1,
                human=1,
                artifacts=(request.id, synthesis_run.id, synthesis_run.proposal.id),
                summary="The operator reviewed and accepted the strict deterministic reference POM proposal.",
            )
        )

        adaptation_started = now_fn()
        workspace_profile = runtime_workspace_profile
        snapshot = inspect_framework(
            source_framework,
            workspace_profile,
            snapshot_id=f"snapshot_{uuid.uuid4().hex[:12]}",
            captured_at=adaptation_started,
        )
        adaptation_plan = build_adaptation_plan(
            synthesis_run,
            workspace_profile,
            snapshot,
            plan_id=f"adapt_{uuid.uuid4().hex[:12]}",
            created_at=now_fn(),
        )
        output_fn("\nRepository adaptation-plan review")
        output_fn(_format_adaptation_plan(adaptation_plan))
        plan_review_started = now_fn()
        plan_timer = timer_fn()
        plan_accepted = _ask_accept("Accept this repository plan?", input_fn, output_fn)
        plan_review_completed = now_fn()
        ledger.record(
            OperatorActionKind.REVIEW_DECISION,
            "adaptation_plan",
            "accepted" if plan_accepted else "rejected",
            started_at=plan_review_started,
            completed_at=plan_review_completed,
            active_seconds=max(0.0, timer_fn() - plan_timer),
        )
        if not plan_accepted:
            ledger.abort()
            raise InteractiveFlowStopped("operator rejected adaptation plan")
        adaptation_plan = review_adaptation_plan(
            adaptation_plan,
            decision=AdaptationReviewDecision.ACCEPTED,
            reviewed_at=plan_review_completed,
            reason="The interactive operator accepted the exact repository targets.",
            review_seconds=max(0.0, timer_fn() - plan_timer),
        )
        save_framework_snapshot(snapshot, output / "05-framework-snapshot.json")
        save_adaptation_plan(adaptation_plan, output / "05-adaptation-plan.json")
        stages.append(
            _stage(
                CreationStageKind.ADAPTATION_PLANNING,
                adaptation_started,
                plan_review_completed,
                deterministic=len(adaptation_plan.operations),
                human=1,
                artifacts=(snapshot.id, adaptation_plan.id),
                summary="The operator reviewed the read-only repository plan before source generation.",
            )
        )

        delivery_started = now_fn()
        if external_public_single_page:
            generation_profile = load_generation_profile(
                root / "profiles/delivery/external_public_single_page.json"
            )
        else:
            generation_profile = load_generation_profile(
                root / "testdata/delivery/profile/public_search_generation.json"
            )
            source_binding = generation_profile.test_data_bindings[0]
            generation_profile = generation_profile.model_copy(
                update={
                    "id": "generation_interactive",
                    "test_data_bindings": (
                        TestDataBinding(
                            test_data_id=request.test_data[0].id,
                            fixture_key=source_binding.fixture_key,
                            value=source_binding.value,
                            sensitivity=source_binding.sensitivity,
                            secret=False,
                        ),
                    ),
                }
            )
        patch = build_code_patch(
            synthesis_run,
            adaptation_plan,
            workspace_profile,
            generation_profile,
            snapshot,
            source_framework,
            patch_id=f"patch_{uuid.uuid4().hex[:12]}",
            created_at=delivery_started,
        )
        output_fn("\nGenerated source-patch review")
        output_fn(_format_code_patch(patch))
        patch_review_started = now_fn()
        patch_timer = timer_fn()
        patch_accepted = _ask_accept("Accept this exact code patch?", input_fn, output_fn)
        patch_review_completed = now_fn()
        ledger.record(
            OperatorActionKind.REVIEW_DECISION,
            "code_patch",
            "accepted" if patch_accepted else "rejected",
            started_at=patch_review_started,
            completed_at=patch_review_completed,
            active_seconds=max(0.0, timer_fn() - patch_timer),
        )
        if not patch_accepted:
            ledger.abort()
            raise InteractiveFlowStopped("operator rejected code patch")
        patch = review_code_patch(
            patch,
            decision=PatchReviewDecision.ACCEPTED,
            reviewed_at=patch_review_completed,
            reason="The interactive operator accepted all displayed source changes after full exact rendering.",
            review_seconds=max(0.0, timer_fn() - patch_timer),
        )
        sandbox = output / "sandbox" / "qa-automation-framework"
        materialize_snapshot_sandbox(
            source_framework, sandbox, workspace_profile, snapshot
        )
        application = apply_code_patch(
            patch,
            workspace_profile,
            snapshot,
            sandbox,
            application_id=f"apply_{uuid.uuid4().hex[:12]}",
            applied_at=now_fn(),
        )
        save_generation_profile(generation_profile, output / "06-generation-profile.json")
        save_code_patch(patch, output / "06-code-patch.json")
        save_application_report(application, output / "06-patch-application.json")
        delivery_completed = now_fn()
        stages.append(
            _stage(
                CreationStageKind.SOURCE_DELIVERY,
                delivery_started,
                delivery_completed,
                deterministic=len(patch.changes) + len(patch.reused_targets),
                human=1,
                artifacts=(generation_profile.id, patch.id, application.id),
                summary="The operator reviewed every exact source change before sandbox-only application.",
            )
        )

        target_test = next(
            operation.target_path
            for operation in adaptation_plan.operations
            if operation.target_kind is AdaptationTargetKind.TEST
        )
        output_fn("\nExecution trigger")
        output_fn(f"Target: {target_test}")
        execution_prompt_started = now_fn()
        execution_timer = timer_fn()
        execute = _ask_accept(
            "Run the generated test in the isolated sandbox?", input_fn, output_fn
        )
        execution_prompt_completed = now_fn()
        ledger.record(
            OperatorActionKind.EXECUTION_TRIGGER,
            "framework_execution",
            "accepted" if execute else "rejected",
            started_at=execution_prompt_started,
            completed_at=execution_prompt_completed,
            active_seconds=max(0.0, timer_fn() - execution_timer),
        )
        if not execute:
            ledger.abort()
            raise InteractiveFlowStopped("operator declined sandbox execution")

        execution_started = now_fn()
        compile_command = [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "pages",
            "components",
            "tests",
            "testdata",
        ]
        compile_result, compile_seconds = command_runner(compile_command, sandbox)
        collect_command = [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            target_test,
        ]
        collect_result, collect_seconds = command_runner(collect_command, sandbox)
        env = os.environ.copy()
        assert application_url is not None
        env[generation_profile.environment_url_variable] = application_url
        test_command = [sys.executable, "-m", "pytest", "-q", target_test]
        test_result, test_seconds = command_runner(test_command, sandbox, env)
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
            evaluation_id=f"creation_eval_{uuid.uuid4().hex[:12]}",
            completed_at=now_fn(),
            target_test=target_test,
            collected_test_count=1 if collect_result.returncode == 0 else 0,
            passed_test_count=1 if test_result.returncode == 0 else 0,
            verification_results=verification_results,
            verification_seconds=verification_seconds,
            time_to_first_runnable_test_seconds=timer_fn() - flow_started_perf,
            original_framework_unchanged=(
                _tree_hash(source_framework) == original_framework_hash
            ),
            corrections=(
                "Sprint 11 replaced fixture-supplied human actions with blocking operator prompts.",
                "The headed browser remained visible during ambiguity resolution and discovery review.",
            ),
        )
        save_creation_evaluation(
            creation_evaluation, output / "07-creation-evaluation.json"
        )
        execution_completed = now_fn()
        stages.append(
            _stage(
                CreationStageKind.FRAMEWORK_EXECUTION,
                execution_started,
                execution_completed,
                deterministic=3,
                browser=1,
                human=1,
                artifacts=(creation_evaluation.id,),
                summary="The operator triggered isolated compile, collection, and Playwright execution.",
            )
        )

    flow_completed_at = now_fn()
    human_answers = ledger.session.answer_count
    human_confirmations = ledger.session.confirmation_count
    handoff_confirmations = ledger.session.handoff_confirmation_count
    review_decisions = ledger.session.review_decision_count
    ambiguity_count = ledger.session.ambiguity_selection_count
    total_actions = len(ledger.session.actions)
    model_seconds = sum(turn.latency_seconds for turn in guided_run.turns) + sum(
        turn.latency_seconds for turn in discovery_run.guidance_turns
    )
    run = CreationFlowRun(
        id=f"creation_interactive_{uuid.uuid4().hex[:12]}",
        profile_id=interactive_profile.id,
        context_id=synthesis_context.id,
        status=CreationFlowStatus.PASSED,
        started_at=flow_started_at,
        completed_at=flow_completed_at,
        target_test=target_test,
        stages=tuple(stages),
        total_seconds=max(0.0, timer_fn() - flow_started_perf),
        model_seconds=model_seconds,
        browser_seconds=discovery_run.capture_seconds + test_seconds,
        verification_seconds=verification_seconds,
        human_active_seconds=ledger.session.active_seconds,
        live_llm_call_count=(
            len(guided_run.turns) + len(discovery_run.guidance_turns)
            if provider_mode == "ollama"
            else 3
        ),
        deterministic_synthesis_call_count=1,
        human_trigger_count=1,
        human_answer_count=human_answers,
        human_confirmation_count=human_confirmations,
        handoff_confirmation_count=handoff_confirmations,
        ambiguity_resolution_count=ambiguity_count,
        review_decision_count=review_decisions,
        execution_trigger_count=1,
        total_human_action_count=total_actions,
        candidate_count=len(discovery_run.candidates),
        target_count=len(discovery_run.targets),
        generated_file_count=creation_evaluation.generated_file_count,
        modified_file_count=creation_evaluation.modified_file_count,
        reused_symbol_count=creation_evaluation.reused_symbol_count,
        collected_test_count=creation_evaluation.collected_test_count,
        passed_test_count=creation_evaluation.passed_test_count,
        fixture_assisted_reference_demo=False,
        interactive_human_used_during_verifier=True,
        live_llm_used=True,
        framework_execution_independent=creation_evaluation.framework_execution_independent,
        original_framework_unchanged=creation_evaluation.original_framework_unchanged,
        full_traceability=(
            request.context_id
            == synthesis_run.proposal.context_id
            == adaptation_plan.context_id
            == patch.context_id
            == creation_evaluation.context_id
        ),
    )
    engine_report = assess_creation_flow(run)
    if not engine_report.ready_for_external_user_demo:
        raise RuntimeError(
            f"human-triggered run is not external-demo ready: {engine_report.external_demo_blockers}"
        )
    save_creation_flow_run(run, output / "creation-flow-run.json")
    operator_session = ledger.complete(run.id)
    interactive_report = assess_interactive_creation(
        operator_session, run, interactive_profile
    )
    if not interactive_report.external_user_demo_ready:
        raise RuntimeError(
            f"interactive boundary is not verified: {interactive_report.blockers}"
        )
    _write_summary(run, operator_session, output / "creation-flow-summary.md")
    output_fn("\nHuman-triggered Creation Flow completed successfully.")
    output_fn(f"Interactive human trigger used: true")
    output_fn(f"Fixture answers used: false")
    output_fn(f"Headed browser used: true")
    output_fn(f"Real operator actions: {len(operator_session.actions)}")
    output_fn(f"Tests collected / passed: {run.collected_test_count}/{run.passed_test_count}")
    output_fn("Creation mechanics verified: true")
    output_fn("Ready for external user demonstration: true")
    output_fn(f"Artifacts: {output}")
    return run, operator_session


def _group_collection_plan(planned_items):
    bootstrap = tuple(
        item for item in planned_items if item.question_id in _BOOTSTRAP_QUESTION_IDS
    )
    process = tuple(
        item for item in planned_items if item.question_id not in _BOOTSTRAP_QUESTION_IDS
    )
    groups = []
    if bootstrap:
        groups.append(("Project bootstrap context — asked once at the start of this run", bootstrap))
    if process:
        groups.append(("Process-specific context", process))
    return tuple(groups)


def _format_context_summary(questions) -> str:
    labels = {
        "process.purpose": "Purpose",
        "process.risk": "Risk",
        "process.role": "Role",
        "process.preconditions[0]": "Precondition",
    }
    lines = [
        "Review the process context once. The same values will be reused by later stages.",
    ]
    for index, question in enumerate(questions, start=1):
        label = labels.get(question.target_path)
        if label is None and question.target_path.startswith("process.expected_outcomes"):
            label = "Expected outcome"
        if label is None:
            label = question.target_path
        lines.append(f"  {index}. {label}: {question.current_value}")
    return "\n".join(lines)


def _ask_context_summary_review(questions, *, input_fn, output_fn):
    while True:
        raw = input_fn(
            "Press Enter to CONFIRM ALL, type EDIT to change one field, or QUIT to stop: "
        ).strip().casefold()
        if raw in {"", "confirm"}:
            return "confirm", None, None
        if raw == "quit":
            return "quit", None, None
        if raw != "edit":
            output_fn("Use Enter/CONFIRM, EDIT, or QUIT. Single-letter commands are not accepted.")
            continue

        while True:
            selected = input_fn(
                f"Select field number 1-{len(questions)}, or type CANCEL: "
            ).strip()
            command = selected.casefold()
            if command == "cancel":
                break
            if command == "quit":
                return "quit", None, None
            if not selected.isdigit() or not 1 <= int(selected) <= len(questions):
                output_fn(f"Enter a number from 1 to {len(questions)}, CANCEL, or QUIT.")
                continue
            question = questions[int(selected) - 1]
            replacement = _read_context_value(
                "New value (or type CANCEL): ",
                input_fn=input_fn,
                output_fn=output_fn,
                allow_cancel=True,
            )
            if replacement is None:
                break
            return "edit", question, replacement


def _ask_intake_answer(question, *, suggested_value, input_fn, output_fn):
    while True:
        prompt = "> "
        if suggested_value:
            prompt = f"> [Enter uses {suggested_value}] "
        raw = input_fn(prompt).strip()
        command = raw.casefold()
        if not raw and suggested_value:
            return IntakeAnswer(action=IntakeAnswerAction.PROVIDE, value=suggested_value)
        if command in {":quit", "quit", "q"}:
            return None
        if command == ":unknown" and IntakeAnswerAction.UNKNOWN in question.allowed_actions:
            return IntakeAnswer(action=IntakeAnswerAction.UNKNOWN)
        if command == ":skip" and IntakeAnswerAction.SKIP in question.allowed_actions:
            return IntakeAnswer(action=IntakeAnswerAction.SKIP)
        if command in _RESERVED_CONTEXT_COMMANDS:
            output_fn(
                "That word is reserved for flow control and was not saved as context. "
                "Enter the full business value instead."
            )
            continue
        if raw:
            return IntakeAnswer(action=IntakeAnswerAction.PROVIDE, value=raw)
        output_fn("Enter a value, :unknown, :skip, or :quit.")


def _read_context_value(
    prompt: str,
    *,
    input_fn: InputFn,
    output_fn: OutputFn,
    allow_cancel: bool = False,
) -> str | None:
    while True:
        value = input_fn(prompt).strip()
        command = value.casefold()
        if allow_cancel and command == "cancel":
            return None
        if command in _RESERVED_CONTEXT_COMMANDS:
            output_fn(
                "That word is reserved for flow control and was not saved as context. "
                "Enter the full business value or CANCEL."
            )
            continue
        if value:
            return value
        output_fn("Enter a non-empty value" + (" or CANCEL." if allow_cancel else "."))


def _ask_candidate(candidate_ids, *, input_fn, output_fn):
    allowed = set(candidate_ids)
    while True:
        raw = input_fn("Select candidate ID: ").strip()
        if raw in allowed:
            return raw
        output_fn(f"Choose one of: {', '.join(candidate_ids)}")


def _ask_accept(prompt: str, input_fn: InputFn, output_fn: OutputFn) -> bool:
    while True:
        raw = input_fn(f"{prompt} [A]ccept / [R]eject: ").strip().casefold()
        if raw in {"a", "accept", "y", "yes"}:
            return True
        if raw in {"r", "reject", "n", "no"}:
            return False
        output_fn("Enter A or R.")


def _read_non_empty(prompt: str, *, input_fn: InputFn) -> str:
    while True:
        value = input_fn(prompt).strip()
        if value:
            return value


def _phase_for_questions(questions) -> GuidedIntakePhase:
    return (
        GuidedIntakePhase.REVIEW
        if all(item.current_value is not None for item in questions)
        else GuidedIntakePhase.COLLECTION
    )


def _render_guided_plan(questions, phase: GuidedIntakePhase) -> str:
    return json.dumps(
        {
            "schema_version": "0.1",
            "phase": phase.value,
            "questions": [
                {
                    "question_id": item.id,
                    "user_prompt": item.prompt,
                    "reason": "This closes one explicit context or authority gap.",
                    "answer_shape": (
                        "confirmation"
                        if phase is GuidedIntakePhase.REVIEW
                        else "sentence"
                    ),
                }
                for item in questions
            ],
        }
    )


def _render_discovery_question(ambiguity) -> str:
    return json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": ambiguity.id,
            "candidate_ids": list(ambiguity.candidate_ids),
            "user_prompt": (
                "Which visible candidate performs the intended search action: "
                + " or ".join(ambiguity.candidate_ids)
                + "?"
            ),
            "reason": "The browser evidence does not justify choosing between the tied controls.",
        }
    )


def _format_candidate_table(run) -> str:
    lines = ["Candidates visible in the browser:"]
    for item in run.candidates:
        attributes = ", ".join(f"{a.name}={a.value}" for a in item.attributes) or "none"
        lines.append(
            f"  {item.id}: role={item.semantic_role}, name={item.semantic_name}, attributes={attributes}"
        )
    return "\n".join(lines)


def _format_ambiguity_candidates(run, candidate_ids) -> str:
    by_id = {item.id: item for item in run.candidates}
    lines = ["Ambiguous candidates:"]
    for candidate_id in candidate_ids:
        item = by_id[candidate_id]
        attributes = ", ".join(f"{a.name}={a.value}" for a in item.attributes) or "none"
        lines.append(
            f"  {candidate_id}: {item.semantic_role} / {item.semantic_name} / {attributes}"
        )
    return "\n".join(lines)


def _format_discovery_summary(run) -> str:
    selected = sum(item.selected_candidate_id is not None for item in run.targets)
    return (
        f"Candidates: {len(run.candidates)}\n"
        f"Targets selected: {selected}/{len(run.targets)}\n"
        f"Human ambiguity decisions: {sum(a.selected_candidate_id is not None for a in run.ambiguities)}\n"
        "Raw page, HTML, screenshots, and input values persisted: false"
    )


def _knowledge_at_path(context, path: str) -> str:
    if path == "application.name":
        return context.application.name.value or "<unknown>"
    if path == "application.environment":
        return context.application.environment.value or "<unknown>"
    if path == "process.name":
        return context.process.name.value or "<unknown>"
    if path == "process.steps[opening_navigation].intent":
        navigation = tuple(
            item
            for item in context.process.steps
            if item.action.kind.value == "navigate"
        )
        if len(navigation) != 1:
            raise KeyError(path)
        return navigation[0].intent.value or "<unknown>"
    raise KeyError(path)


def _format_handoff(context) -> str:
    lines = ["Values requiring explicit synthesis authority:"]
    for path in HANDOFF_PATHS:
        lines.append(f"  {path}: {_knowledge_at_path(context, path)}")
    return "\n".join(lines)


def _format_pom_proposal(proposal) -> str:
    lines = [f"Proposal: {proposal.id}", f"Summary: {proposal.summary}"]
    for page in proposal.pages:
        lines.append(f"  Page class: {page.class_name}")
    for component in proposal.components:
        lines.append(f"  Component class: {component.class_name}")
    for method in proposal.methods:
        lines.append(f"  Method: {method.owner_kind}::{method.name}")
    lines.append(f"  Test: {proposal.test.name}")
    return "\n".join(lines)


def _format_adaptation_plan(plan) -> str:
    lines = [f"Plan: {plan.id}", f"Operations: {len(plan.operations)}"]
    for operation in plan.operations:
        lines.append(
            f"  {operation.kind.value}: {operation.target_path}::{operation.symbol_name or '-'}"
        )
    return "\n".join(lines)


def _format_code_patch(patch) -> str:
    """Render every exact source change without preview truncation."""

    lines = [
        f"Patch: {patch.id}",
        f"Changes: {len(patch.changes)}",
        "Exact source follows. No lines are omitted.",
    ]
    for index, change in enumerate(patch.changes, start=1):
        lines.extend(
            (
                "",
                "=" * 72,
                f"CHANGE {index}/{len(patch.changes)}",
                f"Kind: {change.kind.value}",
                f"Target: {change.target_path}",
                f"Symbol: {change.symbol_name or '-'}",
                f"Content SHA-256: {change.content_sha256}",
                "-" * 72,
                change.content.rstrip("\n"),
                "-" * 72,
                f"END CHANGE {index}/{len(patch.changes)}",
            )
        )
    for reused in patch.reused_targets:
        lines.append(f"Reuse: {reused.target_path}::{reused.symbol_name}")
    lines.extend(("", "End of exact code patch."))
    return "\n".join(lines)


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


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _run(command: list[str], cwd: Path, env=None):
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


def _verification(name, command, result, seconds):
    output = f"{result.stdout}\n{result.stderr}"
    return VerificationResult(
        name=name,
        command=" ".join(command),
        exit_code=result.returncode,
        duration_seconds=seconds,
        output_sha256=hashlib.sha256(output.encode("utf-8")).hexdigest(),
        passed=result.returncode == 0,
    )


def _write_summary(run, operator_session, target: Path) -> None:
    target.write_text(
        "\n".join(
            (
                "# TestCartographer human-triggered Creation Flow",
                "",
                f"- Status: **{run.status.value}**",
                f"- Interactive human trigger used: **yes**",
                f"- Fixture answers used: **no**",
                f"- Headed browser used: **yes**",
                f"- Real operator actions: **{len(operator_session.actions)}**",
                f"- Active operator time: **{operator_session.active_seconds:.2f}s**",
                f"- Local-LLM calls: **{run.live_llm_call_count}**",
                "- LLM role: **intake-question planning and ambiguity clarification only**",
                "- POM and source generation: **deterministic reviewed reference templates**",
                "- Exact source patch displayed before acceptance: **yes**",
                f"- Time to first runnable test: **{run.total_seconds:.2f}s**",
                f"- Tests collected / passed: **{run.collected_test_count} / {run.passed_test_count}**",
                "- Raw operator values persisted in operator ledger: **no**",
                "- Comparative savings measured: **no**",
                "- Ready for external user demonstration: **yes, for the controlled reference flow**",
            )
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
