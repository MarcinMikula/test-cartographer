"""Standalone pytest reference collector for TestCartographer evidence v0.1.

This file intentionally does not import TestCartographer. A framework can emit
provider-neutral JSON while normal execution remains independent from the
engineering and maintenance module.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import pytest

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|secret|authorization|api[_-]?key|credential)\b"
    r"\s*[:=]\s*([^\s,;]+)"
)
_ACTIVE_COLLECTOR: "_Collector | None" = None

_REQUIRED_TRACEABILITY = (
    "context_id",
    "process_id",
    "synthesis_run_id",
    "adaptation_plan_id",
    "code_patch_id",
)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("test-cartographer execution evidence")
    group.addoption("--execution-evidence-profile", action="store")
    group.addoption("--execution-evidence-output", action="store")
    group.addoption("--execution-run-id", action="store")


def pytest_configure(config: pytest.Config) -> None:
    global _ACTIVE_COLLECTOR
    config.addinivalue_line(
        "markers",
        "cartographer(**ids): non-secret traceability for execution evidence",
    )
    profile_path = config.getoption("--execution-evidence-profile")
    output_path = config.getoption("--execution-evidence-output")
    run_id = config.getoption("--execution-run-id")
    supplied = [profile_path is not None, output_path is not None, run_id is not None]
    if not any(supplied):
        return
    if not all(supplied):
        raise pytest.UsageError(
            "execution evidence requires --execution-evidence-profile, "
            "--execution-evidence-output, and --execution-run-id"
        )
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8"))
    collector = _Collector(
        config=config,
        profile=profile,
        output_path=Path(output_path),
        run_id=run_id,
    )
    setattr(config, "_test_cartographer_execution_collector", collector)
    _ACTIVE_COLLECTOR = collector


@pytest.fixture
def execution_probe(request: pytest.FixtureRequest) -> "_ExecutionProbe":
    collector = getattr(request.config, "_test_cartographer_execution_collector", None)
    if collector is None:
        return _ExecutionProbe(None, request.node.nodeid)
    return collector.probe_for(request.node)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    result = yield
    report = result.get_result()
    collector = getattr(item.config, "_test_cartographer_execution_collector", None)
    if collector is not None:
        collector.record_report(item, call, report)


def pytest_collectreport(report: pytest.CollectReport) -> None:
    if _ACTIVE_COLLECTOR is not None and report.failed:
        _ACTIVE_COLLECTOR.record_collection_failure(report)


def pytest_unconfigure(config: pytest.Config) -> None:
    global _ACTIVE_COLLECTOR
    _ACTIVE_COLLECTOR = None


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    collector = getattr(session.config, "_test_cartographer_execution_collector", None)
    if collector is not None:
        collector.finish(exitstatus)


@dataclass
class _State:
    item: pytest.Item
    reports: dict[str, pytest.TestReport] = field(default_factory=dict)
    failures: dict[str, dict[str, Any]] = field(default_factory=dict)
    steps: list[dict[str, Any]] = field(default_factory=list)
    finalized: bool = False


class _ExecutionProbe:
    def __init__(self, collector: "_Collector | None", nodeid: str) -> None:
        self._collector = collector
        self._nodeid = nodeid

    def record_step(
        self,
        *,
        step_id: str,
        page_object: str,
        method_name: str,
        action: str,
        target_element_id: str | None = None,
        locator_id: str | None = None,
        url: str | None = None,
    ) -> None:
        """Record structure only; values and method arguments are not accepted."""
        if self._collector is None:
            return
        self._collector.record_step(
            self._nodeid,
            step_id=step_id,
            page_object=page_object,
            method_name=method_name,
            action=action,
            target_element_id=target_element_id,
            locator_id=locator_id,
            url=url,
        )


class _Collector:
    def __init__(
        self,
        *,
        config: pytest.Config,
        profile: dict[str, Any],
        output_path: Path,
        run_id: str,
    ) -> None:
        self.config = config
        self.root = Path(str(config.rootpath)).resolve()
        self.profile = profile
        self.output_path = output_path
        self.run_id = run_id
        self.started_at = datetime.now(timezone.utc)
        self.states: dict[str, _State] = {}
        self.records: list[dict[str, Any]] = []
        self.collection_records: list[dict[str, Any]] = []
        self.secret_values = tuple(
            value
            for name in profile.get("secret_environment_variable_names", [])
            if (value := os.environ.get(name))
        )
        self.max_records = int(profile.get("max_records", 100))
        self.max_steps = int(profile.get("max_steps_per_test", 8))
        self.max_failure_chars = int(profile.get("max_failure_text_characters", 2000))

    def probe_for(self, item: pytest.Item) -> _ExecutionProbe:
        self._state(item)
        return _ExecutionProbe(self, item.nodeid)

    def record_step(self, nodeid: str, **payload: Any) -> None:
        state = self.states.get(nodeid)
        if state is None or len(state.steps) >= self.max_steps:
            return
        step: dict[str, Any] = {
            "sequence": len(state.steps) + 1,
            "step_id": payload["step_id"],
            "page_object": payload["page_object"],
            "method_name": payload["method_name"],
            "action": payload["action"],
            "target_element_id": payload.get("target_element_id"),
            "locator_id": payload.get("locator_id"),
            "location": _sanitize_url(payload.get("url")),
            "input_value_persisted": False,
            "method_arguments_persisted": False,
        }
        state.steps.append(step)

    def record_report(
        self,
        item: pytest.Item,
        call: pytest.CallInfo[Any],
        report: pytest.TestReport,
    ) -> None:
        state = self._state(item)
        state.reports[report.when] = report
        if call.excinfo is not None:
            state.failures[report.when] = self._failure(call, report)
        if report.when == "teardown":
            self._finalize_state(state)

    def record_collection_failure(self, report: pytest.CollectReport) -> None:
        longrepr = str(report.longrepr)
        redacted, redactions = _redact(longrepr, self.secret_values)
        bounded = redacted[: self.max_failure_chars]
        relative = _relative_path(report.nodeid.split("::", 1)[0], self.root) or "collection.py"
        record = {
            "schema_version": "0.1",
            "id": _record_id(self.run_id, report.nodeid, "infrastructure_error"),
            "run_id": self.run_id,
            "profile_id": self.profile["id"],
            "captured_at": _now(),
            "outcome": "infrastructure_error",
            "test": {
                "nodeid": report.nodeid or relative,
                "relative_path": relative,
                "test_name": "collection_error",
                "line_number": 1,
                "marker_names": [],
            },
            "traceability": self._traceability(None),
            "environment": self._environment(),
            "duration_seconds": 0.0,
            "steps": [],
            "failure": {
                "phase": "collection",
                "exception_type": "CollectionError",
                "safe_summary": "CollectionError during collection",
                "message_sha256": _digest(bounded),
                "traceback_sha256": _digest(bounded),
                "redaction_count": redactions,
                "message_truncated": len(redacted) > self.max_failure_chars,
                "location": None,
                "raw_message_persisted": False,
                "raw_traceback_persisted": False,
                "captured_output_persisted": False,
                "expected_actual_values_persisted": False,
            },
            **self._privacy_fields(),
        }
        self.collection_records.append(record)

    def finish(self, exitstatus: int) -> None:
        for state in self.states.values():
            if not state.finalized:
                self._finalize_state(state)
        records = self.collection_records + self.records
        records.sort(key=lambda item: item["test"]["nodeid"])
        truncated = max(0, len(records) - self.max_records)
        records = records[: self.max_records]
        passed = sum(item["outcome"] == "passed" for item in records)
        failed = sum(item["outcome"] == "test_failure" for item in records)
        infrastructure = sum(
            item["outcome"] == "infrastructure_error" for item in records
        )
        bundle = {
            "schema_version": "0.1",
            "id": _bundle_id(self.run_id),
            "run_id": self.run_id,
            "profile_id": self.profile["id"],
            "started_at": self.started_at.isoformat(),
            "completed_at": _now(),
            "records": records,
            "passed_count": passed,
            "test_failure_count": failed,
            "infrastructure_error_count": infrastructure,
            "truncated_record_count": truncated,
            "collector_name": "test_cartographer_pytest_reference",
            "collector_version": "0.1",
            "framework_execution_independent": True,
            "cartographer_runtime_required": False,
            "raw_artifacts_persisted": False,
            "live_llm_used": False,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            json.dumps(bundle, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    def _state(self, item: pytest.Item) -> _State:
        state = self.states.get(item.nodeid)
        if state is None:
            state = _State(item=item)
            self.states[item.nodeid] = state
        return state

    def _finalize_state(self, state: _State) -> None:
        if state.finalized:
            return
        state.finalized = True
        setup = state.reports.get("setup")
        call = state.reports.get("call")
        teardown = state.reports.get("teardown")
        if setup is not None and setup.failed:
            outcome, phase = "infrastructure_error", "setup"
        elif teardown is not None and teardown.failed:
            outcome, phase = "infrastructure_error", "teardown"
        elif call is not None and call.failed:
            outcome, phase = "test_failure", "call"
        elif call is not None and call.passed:
            outcome, phase = "passed", "call"
        else:
            return
        if outcome == "passed" and not self.profile.get("include_passed", True):
            return
        failure = state.failures.get(phase)
        durations = sum(
            float(report.duration)
            for report in state.reports.values()
            if report is not None
        )
        item = state.item
        markers = sorted({marker.name for marker in item.iter_markers()})
        location = item.location
        record = {
            "schema_version": "0.1",
            "id": _record_id(self.run_id, item.nodeid, outcome),
            "run_id": self.run_id,
            "profile_id": self.profile["id"],
            "captured_at": _now(),
            "outcome": outcome,
            "test": {
                "nodeid": item.nodeid,
                "relative_path": _relative_path(item.path, self.root) or item.path.name,
                "test_name": item.name.split("[", 1)[0],
                "line_number": int(location[1]) + 1,
                "marker_names": markers,
            },
            "traceability": self._traceability(item),
            "environment": self._environment(),
            "duration_seconds": durations,
            "steps": state.steps,
            "failure": failure,
            **self._privacy_fields(),
        }
        self.records.append(record)

    def _failure(
        self,
        call: pytest.CallInfo[Any],
        report: pytest.TestReport,
    ) -> dict[str, Any]:
        assert call.excinfo is not None
        message = str(call.excinfo.value)
        traceback_text = str(report.longrepr)
        message_redacted, message_count = _redact(message, self.secret_values)
        trace_redacted, trace_count = _redact(traceback_text, self.secret_values)
        bounded_message = message_redacted[: self.max_failure_chars]
        bounded_trace = trace_redacted[: self.max_failure_chars]
        location = None
        traceback = list(call.excinfo.traceback)
        if traceback:
            frame = traceback[-1]
            relative = _relative_path(frame.path, self.root)
            if relative is not None:
                location = {
                    "relative_path": relative,
                    "line_number": int(frame.lineno),
                    "function_name": frame.name,
                }
        return {
            "phase": report.when,
            "exception_type": call.excinfo.typename,
            "safe_summary": f"{call.excinfo.typename} during {report.when}",
            "message_sha256": _digest(bounded_message),
            "traceback_sha256": _digest(bounded_trace),
            "redaction_count": message_count + trace_count,
            "message_truncated": len(message_redacted) > self.max_failure_chars,
            "location": location,
            "raw_message_persisted": False,
            "raw_traceback_persisted": False,
            "captured_output_persisted": False,
            "expected_actual_values_persisted": False,
        }

    def _traceability(self, item: pytest.Item | None) -> dict[str, Any]:
        values = {
            "context_id": self.profile.get("default_context_id"),
            "process_id": self.profile.get("default_process_id"),
            "synthesis_run_id": self.profile.get("default_synthesis_run_id"),
            "adaptation_plan_id": self.profile.get("default_adaptation_plan_id"),
            "code_patch_id": self.profile.get("default_code_patch_id"),
        }
        source_ids: list[str] = []
        if item is not None:
            marker = item.get_closest_marker("cartographer")
            if marker is not None:
                for key in _REQUIRED_TRACEABILITY:
                    if marker.kwargs.get(key) is not None:
                        values[key] = marker.kwargs[key]
            module_trace = getattr(getattr(item, "module", None), "TRACEABILITY", ())
            if isinstance(module_trace, (tuple, list)):
                source_ids.extend(str(value) for value in module_trace)
        source_ids = list(dict.fromkeys(source_ids))
        missing = [key for key in _REQUIRED_TRACEABILITY if values.get(key) is None]
        return {
            **values,
            "source_ids": source_ids,
            "complete": not missing,
            "missing_fields": missing,
        }

    def _environment(self) -> dict[str, Any]:
        return {
            "framework_id": self.profile["framework_id"],
            "environment_label": self.profile["environment_label"],
            "python_version": platform.python_version(),
            "pytest_version": pytest.__version__,
            "playwright_version": _package_version("playwright"),
            "platform_system": platform.system(),
            "host_name_persisted": False,
            "environment_values_persisted": False,
        }

    def _privacy_fields(self) -> dict[str, Any]:
        return {
            "sensitivity": self.profile.get("sensitivity", "internal"),
            "raw_page_persisted": False,
            "input_values_persisted": False,
            "credentials_persisted": False,
            "raw_exception_messages_persisted": False,
            "raw_tracebacks_persisted": False,
            "captured_stdout_persisted": False,
            "captured_stderr_persisted": False,
            "html_persisted": False,
            "screenshots_persisted": False,
            "traces_persisted": False,
            "framework_execution_independent": True,
            "cartographer_runtime_required": False,
            "live_llm_used": False,
        }


def _sanitize_url(url: str | None) -> dict[str, Any] | None:
    if not url:
        return None
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = f":{parsed.port}" if parsed.port is not None else ""
    return {
        "origin": f"{parsed.scheme}://{host}{port}",
        "path": parsed.path or "/",
        "credentials_persisted": False,
        "query_persisted": False,
        "fragment_persisted": False,
    }


def _redact(text: str, secret_values: tuple[str, ...]) -> tuple[str, int]:
    rendered = text
    count = 0
    for secret in sorted((value for value in secret_values if value), key=len, reverse=True):
        occurrences = rendered.count(secret)
        if occurrences:
            rendered = rendered.replace(secret, "<redacted>")
            count += occurrences

    def replace(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}=<redacted>"

    return _SECRET_ASSIGNMENT.sub(replace, rendered), count


def _relative_path(path: str | Path, root: Path) -> str | None:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve().relative_to(root).as_posix()
    except (OSError, ValueError):
        return None


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _record_id(run_id: str, nodeid: str, outcome: str) -> str:
    digest = hashlib.sha256(f"{run_id}|{nodeid}|{outcome}".encode()).hexdigest()[:16]
    return f"exe_{digest}"


def _bundle_id(run_id: str) -> str:
    digest = hashlib.sha256(run_id.encode()).hexdigest()[:16]
    return f"bundle_{digest}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None
