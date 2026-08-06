"""Bounded proactive frontend/context regression runner."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

from test_cartographer.context.enums import LocatorStrategy
from test_cartographer.proactive_regression.enums import (
    AutomationImpact,
    ChangeDisposition,
    ProactiveRunStatus,
    ReportReviewDecision,
)
from test_cartographer.proactive_regression.io import (
    load_observation_inventory,
    load_proactive_profile,
    save_proactive_run,
)
from test_cartographer.proactive_regression.models import (
    ApprovedObservationItem,
    ElementRegressionObservation,
    FrameworkProbeResult,
    FrontendChangeReport,
    ObservationInventory,
    ObservedAttribute,
    ProactiveRegressionProfile,
    ProactiveRegressionRun,
)

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
NowFn = Callable[[], datetime]


class ProactiveRegressionRejected(RuntimeError):
    """Raised when the operator rejects one required authority transition."""


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


@contextmanager
def serve_reference_directory(root: str | Path) -> Iterator[str]:
    directory = Path(root).resolve()
    handler = partial(_QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _ask_accept(prompt: str, *, input_fn: InputFn, output_fn: OutputFn) -> None:
    answer = input_fn(f"{prompt} [A]ccept / [R]eject: ").strip().casefold()
    if answer not in {"a", "accept"}:
        output_fn("Operator rejected the bounded transition.")
        raise ProactiveRegressionRejected(prompt)


def _bounded_process_text(value: str | None, limit: int = 1500) -> str:
    text = (value or "").replace("\r", " ").replace("\n", " ").strip()
    return text[:limit]


def _framework_source_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    excluded_directories = {".git", ".pytest_cache", "__pycache__"}
    candidates = []
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        relative = item.relative_to(root)
        if any(part in excluded_directories for part in relative.parts):
            continue
        if item.suffix in {".pyc", ".pyo"}:
            continue
        candidates.append(item)
    for path in sorted(candidates, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _parse_junit(path: Path, phase: str) -> FrameworkProbeResult:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(suite.attrib.get("tests", "0")) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", "0")) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", "0")) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", "0")) for suite in suites)
    passed = tests - failures - errors - skipped
    if skipped:
        errors += skipped
        passed = tests - failures - errors
    return FrameworkProbeResult(
        phase=phase,
        collected_test_count=tests,
        passed_test_count=passed,
        failed_test_count=failures,
        infrastructure_error_count=errors,
        passed=tests > 0 and passed == tests and failures == 0 and errors == 0,
    )


def _run_framework_probe(
    framework_root: Path,
    *,
    application_url: str,
    profile: ProactiveRegressionProfile,
    phase: str,
    output_dir: Path,
    executable_path: str | None = None,
) -> FrameworkProbeResult:
    junit_path = output_dir / f"framework-probe-{phase}.xml"
    env = os.environ.copy()
    for inherited_name in ("PYTEST_ADDOPTS", "PYTEST_CURRENT_TEST", "PYTEST_PLUGINS"):
        env.pop(inherited_name, None)
    env[profile.framework_url_environment_variable] = application_url
    if executable_path:
        env["TEST_CARTOGRAPHER_EXECUTABLE_PATH"] = executable_path
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-c",
                str(framework_root / "pytest.ini"),
                "--rootdir",
                str(framework_root),
                profile.framework_test_path,
                "--junitxml",
                str(junit_path),
                "-q",
            ],
            cwd=framework_root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=profile.framework_probe_timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        junit_path.unlink(missing_ok=True)
        raise RuntimeError(
            f"{phase} framework probe exceeded "
            f"{profile.framework_probe_timeout_seconds:.1f} seconds"
        ) from exc
    if not junit_path.exists():
        raise RuntimeError(
            f"{phase} framework probe produced no JUnit report; "
            f"exit={result.returncode}; stdout={_bounded_process_text(result.stdout)!r}; "
            f"stderr={_bounded_process_text(result.stderr)!r}"
        )
    try:
        probe = _parse_junit(junit_path, phase)
    finally:
        junit_path.unlink(missing_ok=True)
    if result.returncode != 0 or not probe.passed:
        raise RuntimeError(
            f"{phase} framework probe was not green; exit={result.returncode}; "
            f"tests={probe.collected_test_count}; passed={probe.passed_test_count}; "
            f"failures={probe.failed_test_count}; errors={probe.infrastructure_error_count}; "
            f"stdout={_bounded_process_text(result.stdout)!r}; "
            f"stderr={_bounded_process_text(result.stderr)!r}"
        )
    return probe


def _locator_for_expected(page: Page, item: ApprovedObservationItem) -> Locator:
    strategy = item.primary_locator_strategy
    value = item.primary_locator_value
    if strategy is LocatorStrategy.TEST_ID:
        return page.get_by_test_id(value)
    if strategy is LocatorStrategy.ROLE:
        return page.get_by_role(item.semantic_role, name=item.accessible_name, exact=True)
    if strategy is LocatorStrategy.LABEL:
        return page.get_by_label(value, exact=True)
    if strategy is LocatorStrategy.TEXT:
        return page.get_by_text(value, exact=True)
    if strategy is LocatorStrategy.CSS:
        return page.locator(value)
    if strategy is LocatorStrategy.XPATH:
        return page.locator(f"xpath={value}")
    raise ValueError(f"unsupported proactive locator strategy: {strategy.value}")


def _visible_count(locator: Locator, maximum: int = 50) -> int:
    count = min(locator.count(), maximum)
    return sum(locator.nth(index).is_visible() for index in range(count))


def _first_visible(locator: Locator, maximum: int = 50) -> Locator:
    count = min(locator.count(), maximum)
    for index in range(count):
        candidate = locator.nth(index)
        if candidate.is_visible():
            return candidate
    raise RuntimeError("semantic locator has no visible target")


def _semantic_locator(page: Page, item: ApprovedObservationItem) -> Locator:
    return page.get_by_role(
        item.semantic_role,
        name=item.accessible_name,
        exact=True,
    )


def _attributes(locator: Locator) -> tuple[ObservedAttribute, ...]:
    result: list[ObservedAttribute] = []
    for name in ("data-testid", "id", "name", "type", "aria-label"):
        value = locator.get_attribute(name)
        if value:
            result.append(ObservedAttribute(name=name, value=value))
    return tuple(result)


def _current_locator(
    attributes: tuple[ObservedAttribute, ...],
) -> tuple[LocatorStrategy | None, str | None]:
    values = {item.name: item.value for item in attributes}
    if values.get("data-testid"):
        return LocatorStrategy.TEST_ID, values["data-testid"]
    if values.get("id"):
        return LocatorStrategy.CSS, f"#{values['id']}"
    return None, None


def _observe_item(page: Page, item: ApprovedObservationItem) -> ElementRegressionObservation:
    expected = _locator_for_expected(page, item)
    semantic = _semantic_locator(page, item)
    expected_count = _visible_count(expected)
    semantic_count = _visible_count(semantic)

    attrs: tuple[ObservedAttribute, ...] = ()
    current_strategy = None
    current_value = None
    if semantic_count == 1:
        target = _first_visible(semantic)
        attrs = _attributes(target)
        current_strategy, current_value = _current_locator(attrs)

    if expected_count == 1 and semantic_count == 1:
        disposition = ChangeDisposition.UNCHANGED
        impact = AutomationImpact.NONE_DETECTED
    elif expected_count == 0 and semantic_count == 1 and current_value is not None:
        disposition = ChangeDisposition.LOCATOR_DRIFT
        impact = (
            AutomationImpact.CURRENT_TEST_RISK
            if item.covered_by_current_framework_test
            else AutomationImpact.MAPPED_CONTEXT_STALE
        )
    elif semantic_count == 0:
        disposition = ChangeDisposition.MISSING
        impact = AutomationImpact.HUMAN_REVIEW_REQUIRED
    else:
        disposition = ChangeDisposition.AMBIGUOUS
        impact = AutomationImpact.HUMAN_REVIEW_REQUIRED

    safe_payload = {
        "item_id": item.id,
        "element_id": item.element_id,
        "disposition": disposition.value,
        "expected_visible_count": expected_count,
        "semantic_visible_count": semantic_count,
        "current_locator_strategy": current_strategy.value if current_strategy else None,
        "current_locator_value": current_value,
        "attributes": [attribute.model_dump(mode="json") for attribute in attrs],
    }
    digest = hashlib.sha256(
        json.dumps(safe_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return ElementRegressionObservation(
        item_id=item.id,
        element_id=item.element_id,
        disposition=disposition,
        automation_impact=impact,
        covered_by_current_framework_test=item.covered_by_current_framework_test,
        expected_locator_strategy=item.primary_locator_strategy,
        expected_locator_value=item.primary_locator_value,
        expected_locator_visible_count=expected_count,
        semantic_visible_count=semantic_count,
        current_locator_strategy=current_strategy,
        current_locator_value=current_value,
        observed_attributes=attrs,
        observation_sha256=digest,
    )


def _build_report(
    *,
    run_id: str,
    inventory: ObservationInventory,
    observations: tuple[ElementRegressionObservation, ...],
    decision: ReportReviewDecision,
    now_fn: NowFn,
) -> FrontendChangeReport:
    return FrontendChangeReport(
        id=f"report_{uuid.uuid4().hex[:12]}",
        run_id=run_id,
        inventory_id=inventory.id,
        generated_at=now_fn(),
        decision=decision,
        observations=observations,
        stable_count=sum(item.disposition is ChangeDisposition.UNCHANGED for item in observations),
        locator_drift_count=sum(item.disposition is ChangeDisposition.LOCATOR_DRIFT for item in observations),
        missing_count=sum(item.disposition is ChangeDisposition.MISSING for item in observations),
        ambiguous_count=sum(item.disposition is ChangeDisposition.AMBIGUOUS for item in observations),
        current_test_risk_count=sum(item.automation_impact is AutomationImpact.CURRENT_TEST_RISK for item in observations),
        mapped_context_stale_count=sum(item.automation_impact is AutomationImpact.MAPPED_CONTEXT_STALE for item in observations),
    )


def _navigate_for_observation(page: Page, url: str, *, timeout_ms: int) -> None:
    """Navigate within one total bounded timeout and wait only for usable DOM."""
    started = time.monotonic()
    page.goto(url, wait_until="commit", timeout=timeout_ms)
    elapsed_ms = int((time.monotonic() - started) * 1000)
    remaining_ms = max(100, timeout_ms - elapsed_ms)
    page.locator("body").wait_for(state="attached", timeout=remaining_ms)


def execute_proactive_regression(
    *,
    inventory: ObservationInventory,
    profile: ProactiveRegressionProfile,
    framework_root: str | Path,
    application_root: str | Path,
    output_dir: str | Path,
    interactive_human_trigger_used: bool,
    fixture_decisions_used: bool,
    headed_browser_used: bool,
    report_decision: ReportReviewDecision | None = None,
    report_review_fn: Callable[
        [FrontendChangeReport, FrameworkProbeResult, FrameworkProbeResult],
        ReportReviewDecision,
    ] | None = None,
    executable_path: str | None = None,
    now_fn: NowFn = lambda: datetime.now(timezone.utc),
) -> ProactiveRegressionRun:
    if (report_decision is None) == (report_review_fn is None):
        raise ValueError("provide exactly one report decision source")
    if profile.inventory_id != inventory.id:
        raise ValueError("profile inventory_id does not match inventory")
    if profile.allowed_origin != inventory.base_origin:
        raise ValueError("profile allowed_origin does not match inventory base_origin")
    required_routes = {
        f"/{profile.baseline_document}",
        f"/{profile.current_document}",
    }
    if not required_routes.issubset(set(inventory.allowed_routes)):
        raise ValueError("profile documents are outside the accepted inventory routes")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    framework = Path(framework_root).resolve()
    application = Path(application_root).resolve()
    framework_fingerprint_before = _framework_source_fingerprint(framework)
    run_id = f"proactive_{uuid.uuid4().hex[:12]}"
    started_at = now_fn()

    with serve_reference_directory(application) as origin:
        if profile.allowed_origin not in {"http://127.0.0.1", origin}:
            raise ValueError("runtime origin is outside the approved local boundary")
        baseline_url = f"{origin}/{profile.baseline_document}"
        current_url = f"{origin}/{profile.current_document}"
        baseline_probe = _run_framework_probe(
            framework,
            application_url=baseline_url,
            profile=profile,
            phase="baseline",
            output_dir=output,
            executable_path=executable_path,
        )
        current_probe = _run_framework_probe(
            framework,
            application_url=current_url,
            profile=profile,
            phase="current",
            output_dir=output,
            executable_path=executable_path,
        )

        launch_args: dict[str, object] = {"headless": not headed_browser_used}
        if executable_path:
            launch_args["executable_path"] = executable_path
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(**launch_args)
            try:
                page = browser.new_page()
                page.set_default_navigation_timeout(inventory.budget.navigation_timeout_ms)
                page.set_default_timeout(inventory.budget.locator_timeout_ms)
                _navigate_for_observation(
                    page,
                    current_url,
                    timeout_ms=inventory.budget.navigation_timeout_ms,
                )
                observations = tuple(_observe_item(page, item) for item in inventory.items)
                pending_report = _build_report(
                    run_id=run_id,
                    inventory=inventory,
                    observations=observations,
                    decision=ReportReviewDecision.PENDING,
                    now_fn=now_fn,
                )
                decision = (
                    report_review_fn(pending_report, baseline_probe, current_probe)
                    if report_review_fn is not None
                    else report_decision
                )
                if decision is None or decision is ReportReviewDecision.PENDING:
                    raise RuntimeError("report decision source returned no final decision")
                report = pending_report.model_copy(update={"decision": decision})
            finally:
                browser.close()

    if report.stable_count != profile.expected_stable_count:
        raise RuntimeError(
            f"expected {profile.expected_stable_count} stable items, got {report.stable_count}"
        )
    if report.locator_drift_count != profile.expected_drift_count:
        raise RuntimeError(
            f"expected {profile.expected_drift_count} locator drifts, got {report.locator_drift_count}"
        )
    framework_fingerprint_after = _framework_source_fingerprint(framework)
    if framework_fingerprint_after != framework_fingerprint_before:
        raise RuntimeError("framework source changed during proactive regression")
    accepted = report.decision is ReportReviewDecision.ACCEPTED
    run = ProactiveRegressionRun(
        id=run_id,
        profile_id=profile.id,
        inventory_id=inventory.id,
        started_at=started_at,
        finished_at=now_fn(),
        status=ProactiveRunStatus.PASSED if accepted else ProactiveRunStatus.REJECTED,
        operator_action_count=3,
        interactive_human_trigger_used=interactive_human_trigger_used,
        fixture_decisions_used=fixture_decisions_used,
        headed_browser_used=headed_browser_used,
        accepted_inventory_reused=True,
        baseline_probe=baseline_probe,
        current_probe=current_probe,
        report=report,
        framework_source_fingerprint_before=framework_fingerprint_before,
        framework_source_fingerprint_after=framework_fingerprint_after,
    )
    save_proactive_run(run, output / "proactive-regression-run.json")
    return run


def _format_inventory(inventory: ObservationInventory) -> str:
    lines = [
        "Approved observation inventory",
        f"Inventory: {inventory.id}",
        f"Context / process: {inventory.context_bundle_id} / {inventory.process_id}",
        f"Origin: {inventory.base_origin}",
        f"Authentication: {inventory.authentication_mode.value}",
        f"Sensitivity: {inventory.sensitivity.value}",
        f"Routes: {', '.join(inventory.allowed_routes)}",
        f"Actions: {', '.join(inventory.allowed_actions)}",
        (
            f"Budget: pages={inventory.budget.max_pages}, "
            f"elements={inventory.budget.max_elements}, "
            f"navigation_timeout_ms={inventory.budget.navigation_timeout_ms}, "
            f"locator_timeout_ms={inventory.budget.locator_timeout_ms}"
        ),
        "Items:",
    ]
    for item in inventory.items:
        coverage = "covered" if item.covered_by_current_framework_test else "mapped but not covered"
        lines.append(
            f"  {item.id}: {item.semantic_role} / {item.accessible_name} / "
            f"{item.primary_locator_strategy.value}={item.primary_locator_value} / {coverage}"
        )
    return "\n".join(lines)


def format_frontend_change_report(report: FrontendChangeReport) -> str:
    lines = [
        "Frontend/context change-impact report",
        f"Stable / locator drift / missing / ambiguous: "
        f"{report.stable_count}/{report.locator_drift_count}/{report.missing_count}/{report.ambiguous_count}",
        f"Current-test risks: {report.current_test_risk_count}",
        f"Mapped-context stale candidates: {report.mapped_context_stale_count}",
    ]
    for observation in report.observations:
        current = (
            f"{observation.current_locator_strategy.value}={observation.current_locator_value}"
            if observation.current_locator_strategy is not None
            else "none"
        )
        lines.append(
            f"  {observation.item_id}: {observation.disposition.value}; "
            f"impact={observation.automation_impact.value}; current={current}"
        )
    lines.extend(
        (
            "Application bug claimed: false",
            "Automatic patch created: false",
            "Context automatically modified: false",
            "Raw page / HTML / screenshot persisted: false/false/false",
            "Live LLM used: false",
        )
    )
    return "\n".join(lines)


def run_human_triggered_proactive_regression(
    *,
    inventory_path: str | Path,
    profile_path: str | Path,
    framework_root: str | Path,
    application_root: str | Path,
    output_dir: str | Path,
    executable_path: str | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
) -> ProactiveRegressionRun:
    inventory = load_observation_inventory(inventory_path)
    profile = load_proactive_profile(profile_path)
    output_fn("TestCartographer - human-triggered Proactive Frontend Regression")
    output_fn("Accepted project/process context and inventory are reused; bootstrap questions do not return.")
    output_fn("A green framework test is not evidence that every mapped frontend element is unchanged.")
    _ask_accept(
        "Start one bounded post-deployment proactive regression run?",
        input_fn=input_fn,
        output_fn=output_fn,
    )
    output_fn("")
    output_fn(_format_inventory(inventory))
    _ask_accept(
        "Authorize this exact inventory and observation budget?",
        input_fn=input_fn,
        output_fn=output_fn,
    )
    def review_report(
        report: FrontendChangeReport,
        baseline_probe: FrameworkProbeResult,
        current_probe: FrameworkProbeResult,
    ) -> ReportReviewDecision:
        output_fn("")
        output_fn(
            "Framework test green on baseline / current: "
            f"{str(baseline_probe.passed).lower()} / "
            f"{str(current_probe.passed).lower()}"
        )
        output_fn(format_frontend_change_report(report))
        _ask_accept(
            "Accept this review-only change-impact report?",
            input_fn=input_fn,
            output_fn=output_fn,
        )
        return ReportReviewDecision.ACCEPTED

    accepted_run = execute_proactive_regression(
        inventory=inventory,
        profile=profile,
        framework_root=framework_root,
        application_root=application_root,
        output_dir=output_dir,
        interactive_human_trigger_used=True,
        fixture_decisions_used=False,
        headed_browser_used=profile.require_headed_browser_for_real_operator,
        report_review_fn=review_report,
        executable_path=executable_path,
    )
    output_fn("")
    output_fn("Proactive Frontend Regression completed successfully.")
    output_fn("Real operator actions: 3")
    output_fn(
        f"Framework tests green before / after: "
        f"{str(accepted_run.baseline_probe.passed).lower()} / "
        f"{str(accepted_run.current_probe.passed).lower()}"
    )
    output_fn(f"Mapped locator drift detected: {accepted_run.report.locator_drift_count}")
    output_fn("Application bug claimed: false")
    output_fn("Automatic repair performed: false")
    output_fn("Live LLM used: false")
    output_fn(f"Artifacts: {Path(output_dir).resolve()}")
    return accepted_run


def run_scripted_proactive_regression(
    *,
    inventory_path: str | Path,
    profile_path: str | Path,
    framework_root: str | Path,
    application_root: str | Path,
    output_dir: str | Path,
    executable_path: str | None = None,
) -> ProactiveRegressionRun:
    return execute_proactive_regression(
        inventory=load_observation_inventory(inventory_path),
        profile=load_proactive_profile(profile_path),
        framework_root=framework_root,
        application_root=application_root,
        output_dir=output_dir,
        interactive_human_trigger_used=False,
        fixture_decisions_used=True,
        headed_browser_used=False,
        report_decision=ReportReviewDecision.ACCEPTED,
        executable_path=executable_path,
    )
