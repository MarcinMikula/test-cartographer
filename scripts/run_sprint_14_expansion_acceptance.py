from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

from test_cartographer.adaptation.enums import AdaptationReviewDecision, PythonSymbolKind
from test_cartographer.adaptation.io import save_adaptation_plan
from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.enums import ActionKind, EvidenceSourceType, KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import Evidence, ExpectedOutcome, KnowledgeText, ProcessContext, ProcessStep, TestDataRequirement, UIAction
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.enums import PatchReviewDecision, SourceChangeKind
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.io import save_application_report, save_code_patch
from test_cartographer.delivery.models import FrameworkSymbolRequirement, GenerationProfile, TestDataBinding
from test_cartographer.delivery.review import review_code_patch
from test_cartographer.expansion.assessment import assess_expansion_run
from test_cartographer.expansion.context_builder import build_candidate_expansion_context, observed_element_from_regression
from test_cartographer.expansion.enums import ExpansionRunStatus
from test_cartographer.expansion.fingerprints import context_sha256
from test_cartographer.expansion.io import (
    save_expansion_assessment, save_expansion_plan, save_expansion_request, save_expansion_run,
)
from test_cartographer.expansion.models import ExpansionRequest, ExpansionRun
from test_cartographer.expansion.planner import build_expansion_plan
from test_cartographer.expansion.review import accept_expansion_plan
from test_cartographer.proactive_regression.enums import AutomationImpact, ChangeDisposition
from test_cartographer.proactive_regression.models import ElementRegressionObservation, FrontendChangeReport, ObservationInventory, ObservedAttribute
from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.enums import ProposalReviewDecision
from test_cartographer.synthesis.io import save_synthesis_run
from test_cartographer.synthesis.pipeline import run_synthesis
from test_cartographer.synthesis.request import build_synthesis_request
from test_cartographer.synthesis.review import review_synthesis_run

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "testdata/expansion/inputs"
BROWSER_ROOT = ROOT / "testdata/expansion/browser"
FRAMEWORK_ROOT = ROOT / "testdata/expansion/framework"
REPLAY = ROOT / "testdata/expansion/replay/sort-proposal.json"

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return

@contextmanager
def serve(root: Path):
    handler = partial(QuietHandler, directory=str(root.resolve()))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)

def now() -> datetime:
    return datetime.now(timezone.utc)

def ask_accept(label: str, *, scripted: bool) -> float:
    start = time.perf_counter()
    if scripted:
        print(f"{label} [scripted ACCEPT]")
        return time.perf_counter() - start

    while True:
        answer = input(f"{label} [A]ccept / [R]eject: ").strip().casefold()

        if answer in {"a", "accept"}:
            return time.perf_counter() - start

        if answer in {"r", "reject"}:
            raise RuntimeError(f"Operator rejected: {label}")

        printable = answer.encode("unicode_escape").decode("ascii")
        print(
            "Unrecognized input "
            f"({printable!r}). No decision was recorded. "
            "Please enter A to accept or R to reject."
        )

def ask_text(label: str, default: str, *, scripted: bool) -> tuple[str, float]:
    start = time.perf_counter()
    if scripted:
        print(f"{label}: {default} [scripted default]")
        return default, time.perf_counter() - start
    value = input(f"{label} [{default}]: ").strip() or default
    return value, time.perf_counter() - start

def save_model(model, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(model.model_dump_json(indent=2) + "\n", encoding="utf-8")

def run_pytest(root: Path, tests: list[str], application_url: str, junit: Path) -> tuple[bool, float, str]:
    env = os.environ.copy()
    for key in ("PYTEST_ADDOPTS", "PYTEST_CURRENT_TEST", "PYTEST_PLUGINS"):
        env.pop(key, None)
    env["TEST_CARTOGRAPHER_CATALOG_URL"] = application_url
    command = [sys.executable, "-m", "pytest", "-c", str(root / "pytest.ini"), "--rootdir", str(root), *tests, "--junitxml", str(junit), "-q"]
    start = time.perf_counter()
    completed = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, check=False, timeout=60)
    elapsed = time.perf_counter() - start
    text = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode == 0, elapsed, text[-4000:]

def fresh_sort_observation(url: str, inventory: ObservationInventory, *, headed: bool) -> tuple[ElementRegressionObservation, float]:
    item = next(i for i in inventory.items if i.element_id == "el_sort_results")
    launch: dict[str, object] = {"headless": not headed}
    executable = os.environ.get("TEST_CARTOGRAPHER_EXECUTABLE_PATH")
    if executable:
        launch["executable_path"] = executable
    start = time.perf_counter()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch)
        try:
            page = browser.new_page()
            page.set_default_navigation_timeout(inventory.budget.navigation_timeout_ms)
            page.set_default_timeout(inventory.budget.locator_timeout_ms)
            page.goto(url, wait_until="domcontentloaded")
            expected = page.get_by_test_id(item.primary_locator_value)
            semantic = page.get_by_role(item.semantic_role, name=item.accessible_name, exact=True)
            expected_count = sum(expected.nth(i).is_visible() for i in range(min(expected.count(), 50)))
            semantic_count = sum(semantic.nth(i).is_visible() for i in range(min(semantic.count(), 50)))
            attrs: list[ObservedAttribute] = []
            current_value = None
            if semantic_count == 1:
                target = next(semantic.nth(i) for i in range(min(semantic.count(), 50)) if semantic.nth(i).is_visible())
                for name in ("data-testid", "id", "name", "type", "aria-label"):
                    value = target.get_attribute(name)
                    if value:
                        attrs.append(ObservedAttribute(name=name, value=value))
                current_value = next((a.value for a in attrs if a.name == "data-testid"), None)
            if expected_count == 0 and semantic_count == 1 and current_value:
                disposition = ChangeDisposition.LOCATOR_DRIFT
                impact = AutomationImpact.MAPPED_CONTEXT_STALE
            elif expected_count == 1 and semantic_count == 1:
                disposition = ChangeDisposition.UNCHANGED
                impact = AutomationImpact.NONE_DETECTED
            elif semantic_count == 0:
                disposition = ChangeDisposition.MISSING
                impact = AutomationImpact.HUMAN_REVIEW_REQUIRED
            else:
                disposition = ChangeDisposition.AMBIGUOUS
                impact = AutomationImpact.HUMAN_REVIEW_REQUIRED
            safe = {
                "item_id": item.id, "element_id": item.element_id, "disposition": disposition.value,
                "expected_visible_count": expected_count, "semantic_visible_count": semantic_count,
                "current_locator_strategy": "test_id" if current_value else None,
                "current_locator_value": current_value,
                "attributes": [a.model_dump(mode="json") for a in attrs],
            }
            digest = hashlib.sha256(json.dumps(safe, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            observation = ElementRegressionObservation(
                item_id=item.id, element_id=item.element_id, disposition=disposition, automation_impact=impact,
                covered_by_current_framework_test=item.covered_by_current_framework_test,
                expected_locator_strategy=item.primary_locator_strategy, expected_locator_value=item.primary_locator_value,
                expected_locator_visible_count=expected_count, semantic_visible_count=semantic_count,
                current_locator_strategy=item.primary_locator_strategy if current_value else None,
                current_locator_value=current_value, observed_attributes=tuple(attrs), observation_sha256=digest,
            )
        finally:
            browser.close()
    return observation, time.perf_counter() - start

def human_k(value: str, evidence_id: str) -> KnowledgeText:
    return KnowledgeText(value=value, status=KnowledgeStatus.CONFIRMED, evidence_ids=(evidence_id,), sensitivity=SensitivityLevel.PUBLIC)

def format_plan(plan) -> str:
    lines = [
        f"Reuse / ask-human / observe-new / reobserve / review / blocked: {plan.reuse_count}/{plan.ask_human_count}/{plan.observe_new_count}/{plan.reobserve_count}/{plan.review_count}/{plan.blocked_count}",
        f"Bootstrap questions repeated: {str(plan.bootstrap_questions_repeated).lower()}",
    ]
    for item in plan.items:
        lines.append(f"  {item.subject_ref}: {item.disposition.value} ({item.reason_code.value})")
    return "\n".join(lines)

def print_patch(patch, framework_root: Path) -> None:
    print("\nExact source patch")
    for change in patch.changes:
        print(f"\n[{change.kind.value}] {change.target_path}")
        print(f"before={change.expected_before_sha256 or 'absent'}")
        print(f"after={change.expected_after_sha256}")
        if change.kind is SourceChangeKind.REPLACE_FILE:
            before = (framework_root / change.target_path).read_text(encoding="utf-8").splitlines()
            after = change.content.splitlines()
            print("\n".join(difflib.unified_diff(before, after, fromfile=f"a/{change.target_path}", tofile=f"b/{change.target_path}", lineterm="")))
        else:
            print(change.content)

def main() -> int:
    parser = argparse.ArgumentParser(description="Sprint 14 controlled real-operator expansion acceptance")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--scripted-smoke", action="store_true", help="Headless auto-accept mechanics proof; not real acceptance")
    args = parser.parse_args()
    scripted = args.scripted_smoke
    out = Path(args.output_dir).resolve(); out.mkdir(parents=True, exist_ok=True)
    started = now(); active_operator = 0.0; browser_seconds = 0.0; verification_seconds = 0.0

    from test_cartographer.context.models import ContextBundle
    base_context = ContextBundle.model_validate_json((INPUTS / "accepted-search-context.json").read_text(encoding="utf-8"))
    inventory = ObservationInventory.model_validate_json((INPUTS / "public-catalog-inventory.json").read_text(encoding="utf-8"))
    prior_report = FrontendChangeReport.model_validate_json((INPUTS / "sprint13-accepted-change-report.json").read_text(encoding="utf-8"))
    workspace = WorkspaceProfile.model_validate_json((INPUTS / "workspace-profile.json").read_text(encoding="utf-8"))
    base_hash_before = context_sha256(base_context)
    snapshot = inspect_framework(FRAMEWORK_ROOT, workspace, snapshot_id="snapshot_sort_expansion", captured_at=now())

    print("TestCartographer - Sprint 14 incremental expansion acceptance")
    print("Existing accepted process: Search catalog")
    print("Requested new process: Sort catalog results")
    print("Bootstrap/project context will be reused; no bootstrap questions are asked.")
    active_operator += ask_accept("1/7 Start this human-triggered expansion?", scripted=scripted)

    request = ExpansionRequest(
        id="exp_request_sort_real" if not scripted else "exp_request_sort_scripted",
        base_context_id=base_context.id, base_context_sha256=base_hash_before,
        workspace_profile_id=workspace.id, framework_snapshot_id=snapshot.id,
        framework_snapshot_fingerprint=snapshot.root_fingerprint,
        target_process_id="proc_sort_catalog", target_process_name="Sort catalog results",
        human_intent="Add a second automated process for sorting catalog results.",
        target_element_ids=("el_sort_results",), requested_at=now(), proactive_report_id=prior_report.id,
    )
    save_expansion_request(request, out / "expansion-request.json")
    plan = build_expansion_plan(request, base_context, snapshot, plan_id="exp_plan_sort_real" if not scripted else "exp_plan_sort_scripted", created_at=now(), inventory=inventory, change_report=prior_report)
    print("\n" + format_plan(plan))
    active_operator += ask_accept("2/7 Accept this reuse/gap plan?", scripted=scripted)
    plan = accept_expansion_plan(plan, reviewed_at=now(), review_seconds=0.0)
    save_expansion_plan(plan, out / "expansion-plan.json")

    with serve(BROWSER_ROOT) as origin:
        current_url = f"{origin}/public_catalog_deployed.html"
        ok, seconds, text = run_pytest(FRAMEWORK_ROOT, ["tests/e2e/test_search_catalog.py"], current_url, out / "search-before.xml")
        verification_seconds += seconds
        if not ok:
            raise RuntimeError("existing Search test is not green before expansion:\n" + text)
        print("Existing Search test before expansion: PASS")

        observation, browser_seconds = fresh_sort_observation(current_url, inventory, headed=not scripted)
        save_model(observation, out / "sort-reobservation.json")
        print(f"Fresh Sort observation: {observation.disposition.value}; current={observation.current_locator_value}")
        if observation.disposition is not ChangeDisposition.LOCATOR_DRIFT or observation.current_locator_value != "catalog-sort-control":
            raise RuntimeError("real headed re-observation did not confirm the expected Sort locator drift")

        purpose, spent = ask_text("Process purpose", "Order visible catalog results alphabetically", scripted=scripted); active_operator += spent
        risk, spent = ask_text("Process risk", "Wrong ordering can mislead the visitor", scripted=scripted); active_operator += spent
        outcome, spent = ask_text("Expected outcome", "Results are shown in alphabetical order", scripted=scripted); active_operator += spent
        human_blob = f"{purpose}\n{risk}\n{outcome}".encode("utf-8")
        human_ev = Evidence(
            id="ev_sort_human", source_type=EvidenceSourceType.HUMAN, source_ref="human:sort-expansion",
            summary="Human-confirmed process-specific Sort context.", captured_at=now(), sensitivity=SensitivityLevel.PUBLIC,
            content_sha256=hashlib.sha256(human_blob).hexdigest(),
        )
        hk = lambda value: human_k(value, human_ev.id)
        target_process = ProcessContext(
            id="proc_sort_catalog", name=hk("Sort catalog results"), purpose=hk(purpose), risk=hk(risk),
            role=base_context.process.role, preconditions=base_context.process.preconditions,
            steps=(
                ProcessStep(id="step_open_catalog_sort", order=1, page_id="page_public_catalog", intent=hk("Open the public catalog"), action=UIAction(kind=ActionKind.NAVIGATE), expected_state=hk("Public catalog is visible")),
                ProcessStep(id="step_apply_sort", order=2, page_id="page_public_catalog", intent=hk("Apply alphabetical result sorting"), action=UIAction(kind=ActionKind.CLICK, target_element_id="el_sort_results"), expected_state=hk("Result order changes")),
                ProcessStep(id="step_read_sorted", order=3, page_id="page_public_catalog", intent=hk("Read the sorted results"), action=UIAction(kind=ActionKind.READ, target_element_id="el_results_list"), expected_state=hk("Sorted results are visible")),
            ),
            expected_outcomes=(ExpectedOutcome(id="out_sorted", statement=hk(outcome), related_element_ids=("el_results_list",)),),
        )
        item = next(i for i in inventory.items if i.element_id == "el_sort_results")
        fresh_sort, app_ev = observed_element_from_regression(item, observation, evidence_id="ev_sort_fresh", observed_at=now())
        test_data = TestDataRequirement(
            id="data_expected_order", name=hk("Expected sorted result"), description=hk("Expected complete visible sorted result"),
            symbolic_ref="expected_sort_order", sensitivity=SensitivityLevel.PUBLIC,
        )
        candidate = build_candidate_expansion_context(
            request, plan, base_context, target_process, candidate_context_id="ctx_sort_candidate", title="Sort expansion candidate",
            created_at=now(), observed_elements=(fresh_sort,), additional_evidence=(app_ev, human_ev), test_data=(test_data,),
        )
        save_model(candidate, out / "candidate-context.json")
        print("\nCandidate context summary")
        print(f"Process: {candidate.process.name.value}")
        print(f"Purpose: {candidate.process.purpose.value}")
        print(f"Risk: {candidate.process.risk.value}")
        print(f"Outcome: {candidate.process.expected_outcomes[0].statement.value}")
        print(f"Fresh Sort locator: {fresh_sort.locator_candidates[0].value.value}")
        active_operator += ask_accept("3/7 Accept this candidate expanded context?", scripted=scripted)

        synth_request = build_synthesis_request(candidate, request_id="synreq_sort_expansion", created_at=now())
        adapter = ReplaySynthesisAdapter(raw_output=REPLAY.read_text(encoding="utf-8"))
        synthesis = run_synthesis(synth_request, adapter, run_id="synrun_sort_expansion", started_at=now(), completed_at=now())
        if synthesis.status.value != "ready_for_review":
            raise RuntimeError(f"deterministic synthesis replay is not reviewable: {synthesis.status.value}")
        print("\nSynthesis proposal")
        print(synthesis.proposal.summary if synthesis.proposal else "<none>")
        active_operator += ask_accept("4/7 Accept the validated synthesis proposal?", scripted=scripted)
        synthesis = review_synthesis_run(synthesis, decision=ProposalReviewDecision.ACCEPTED, reviewed_at=now(), review_seconds=0.0)
        save_synthesis_run(synthesis, out / "synthesis-run.json")

        adapt = build_adaptation_plan(synthesis, workspace, snapshot, plan_id="adapt_sort_expansion", created_at=now())
        print("\nAdaptation plan")
        for op in adapt.operations:
            extra = ""
            if getattr(op, "method_names", ()) or getattr(op, "property_names", ()):
                extra = f" methods={list(op.method_names)} properties={list(op.property_names)}"
            print(f"  {op.kind.value}: {op.target_path} / {op.symbol_name}{extra}")
        active_operator += ask_accept("5/7 Accept this repository-aware adaptation plan?", scripted=scripted)
        adapt = review_adaptation_plan(adapt, decision=AdaptationReviewDecision.ACCEPTED, reviewed_at=now(), review_seconds=0.0)
        save_adaptation_plan(adapt, out / "adaptation-plan.json")

        generation = GenerationProfile(
            id="gen_sort_expansion", workspace_profile_id=workspace.id,
            environment_url_variable="TEST_CARTOGRAPHER_CATALOG_URL",
            required_framework_symbols=(FrameworkSymbolRequirement(path="pages/base_page.py", symbol_name="BasePage", symbol_kind=PythonSymbolKind.CLASS),),
            test_data_bindings=(TestDataBinding(test_data_id="data_expected_order", fixture_key="expected_sort_order", value="Alpha Beta Zulu", sensitivity=SensitivityLevel.PUBLIC),),
            browser_headless=True,
        )
        patch = build_code_patch(synthesis, adapt, workspace, generation, snapshot, FRAMEWORK_ROOT, patch_id="patch_sort_expansion", created_at=now())
        generated_sort_test = next(
            change for change in patch.changes
            if change.target_path == "tests/e2e/test_sort_catalog.py"
        )
        if "explicitly supplied search query" in generated_sort_test.content:
            raise RuntimeError("Sort test contains a stale Search-specific assertion message")
        if "explicitly supplied expected result" not in generated_sort_test.content:
            raise RuntimeError("Sort test does not contain the neutral expected-result assertion message")
        if generation.test_data_bindings[0].value != "Alpha Beta Zulu":
            raise RuntimeError("Sort acceptance must bind the complete controlled expected order")
        print_patch(patch, FRAMEWORK_ROOT)
        active_operator += ask_accept("6/7 Accept these exact source changes?", scripted=scripted)
        patch = review_code_patch(patch, decision=PatchReviewDecision.ACCEPTED, reviewed_at=now(), review_seconds=0.0)
        save_code_patch(patch, out / "code-patch.json")

        active_operator += ask_accept("7/7 Apply the accepted patch to a fresh sandbox and execute Search + Sort?", scripted=scripted)
        sandbox = out / "sandbox-framework"
        if sandbox.exists(): shutil.rmtree(sandbox)
        shutil.copytree(FRAMEWORK_ROOT, sandbox)
        report = apply_code_patch(patch, workspace, snapshot, sandbox, application_id="apply_sort_expansion", applied_at=now())
        save_application_report(report, out / "patch-application.json")
        ok, seconds, text = run_pytest(sandbox, ["tests/e2e/test_search_catalog.py", "tests/e2e/test_sort_catalog.py"], current_url, out / "framework-after.xml")
        verification_seconds += seconds
        print(text)
        if not ok:
            raise RuntimeError("sandbox Search + Sort execution did not pass")

    final_snapshot = inspect_framework(FRAMEWORK_ROOT, workspace, snapshot_id="snapshot_sort_expansion_after", captured_at=now())
    base_hash_after = context_sha256(base_context)
    page_op = next(op for op in adapt.operations if op.symbol_name == "CatalogPage")
    replacement = next(c for c in patch.changes if c.target_path == "pages/catalog_page.py")
    test_change = next(c for c in patch.changes if c.target_path == "tests/e2e/test_sort_catalog.py")
    run = ExpansionRun(
        id="exp_run_sort_real" if not scripted else "exp_run_sort_scripted", request_id=request.id, plan_id=plan.id,
        base_context_id=base_context.id, base_context_sha256=base_hash_before, candidate_context_id=candidate.id,
        candidate_context_sha256=context_sha256(candidate), framework_snapshot_id=snapshot.id,
        framework_snapshot_fingerprint=snapshot.root_fingerprint, started_at=started, finished_at=now(), status=ExpansionRunStatus.PASSED,
        synthesis_run_id=synthesis.id, adaptation_plan_id=adapt.id, code_patch_id=patch.id, application_report_id=report.id,
        target_test="tests/e2e/test_sort_catalog.py", reused_knowledge_item_count=plan.reuse_count,
        process_specific_questions_asked=3, new_observation_count=0, reobservation_count=1,
        review_item_count=plan.review_count, blocked_item_count=plan.blocked_count,
        framework_symbols_reused=sum(op.kind.value == "reuse_symbol" for op in adapt.operations),
        framework_symbols_extended=sum(op.kind.value == "extend_symbol" for op in adapt.operations),
        framework_symbols_added=sum(op.kind.value in {"create_file", "add_symbol"} for op in adapt.operations),
        existing_tests_preserved=1, new_tests_added=1, operator_action_count=7,
        active_operator_seconds=active_operator, browser_seconds=browser_seconds, verification_seconds=verification_seconds,
        live_llm_calls=0, interactive_human_trigger_used=not scripted, headed_browser_used=not scripted,
        fixture_decisions_used=scripted, candidate_context_reviewed=True, existing_creation_pipeline_reused=True,
        existing_page_object_extended=(page_op.kind.value == "extend_symbol"),
        method_property_collision_protection=bool(page_op.method_names and page_op.property_names),
        hash_bound_source_replacement_used=(replacement.kind is SourceChangeKind.REPLACE_FILE and replacement.expected_before_sha256 is not None),
        source_drift_preflight_enforced=report.preflight_passed, framework_execution_independent=True,
        base_context_unchanged=(base_hash_before == base_hash_after),
        original_framework_unchanged=(snapshot.root_fingerprint == final_snapshot.root_fingerprint),
    )
    save_expansion_run(run, out / "expansion-run.json")
    assessment = assess_expansion_run(run)
    save_expansion_assessment(assessment, out / "expansion-assessment.json")

    print("\nSprint 14 Expansion Assessment")
    print(f"Expansion verified: {str(assessment.expansion_verified).lower()}")
    print(f"Controlled demo ready: {str(assessment.controlled_demo_ready).lower()}")
    print(f"Blockers: {list(assessment.blockers)}")
    print(f"Bootstrap questions repeated: {str(run.bootstrap_questions_repeated).lower()}")
    print(f"Process-specific questions asked: {run.process_specific_questions_asked}")
    print(f"Reused knowledge items: {run.reused_knowledge_item_count}")
    print(f"Reobservations: {run.reobservation_count}")
    print(f"Existing Page Object extended: {str(run.existing_page_object_extended).lower()}")
    print(f"Search preserved / Sort added: {run.existing_tests_preserved}/{run.new_tests_added}")
    print(f"Original framework unchanged: {str(run.original_framework_unchanged).lower()}")
    print(f"Live LLM calls: {run.live_llm_calls}")
    print(f"Operator authority transitions: {run.operator_action_count}")
    print(f"Artifacts: {out}")
    if scripted:
        if not assessment.expansion_verified or assessment.controlled_demo_ready:
            return 2
        print("Scripted mechanics verified. This is NOT real-operator acceptance.")
        return 0
    if not assessment.controlled_demo_ready:
        return 3
    print("Sprint 14D real-operator acceptance: VERIFIED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
