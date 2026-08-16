"""Bounded browser scan and deterministic candidate extraction."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from test_cartographer.context.enums import LocatorStrategy
from test_cartographer.discovery.enums import DiscoveryRunState, DiscoveryTargetState
from test_cartographer.discovery.models import (
    CandidateAttribute,
    DiscoveredLocator,
    DiscoveryAmbiguity,
    DiscoveryProfile,
    ElementCandidate,
    ProcessDiscoveryPlan,
    ProcessDiscoveryRun,
)
from test_cartographer.discovery.ranking import rank_targets

_BASE_SCAN_SELECTOR = "input, button, select, textarea, [role], [data-testid], ul, ol, table, [aria-live]"
_HEADING_SCAN_SELECTOR = "h1, h2, h3, h4, h5, h6"


def capture_process_discovery(
    plan: ProcessDiscoveryPlan,
    profile: DiscoveryProfile,
    *,
    run_id: str,
    captured_at: datetime,
    headed: bool = False,
    timeout_ms: int = 10_000,
    executable_path: str | None = None,
) -> ProcessDiscoveryRun:
    """Open one explicit page and collect a bounded semantic candidate set."""

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Playwright is required for process discovery") from exc

    if plan.sensitivity not in profile.allowed_sensitivities:
        raise ValueError("discovery sensitivity is not allowed by the profile")
    started = time.perf_counter()
    with sync_playwright() as playwright:
        launch = {"headless": not headed}
        if executable_path:
            launch["executable_path"] = executable_path
        browser = playwright.chromium.launch(**launch)
        try:
            page = browser.new_page()
            page.goto(plan.source_url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(50)
            candidates = _collect_candidates(
                page,
                profile,
                selector=_scan_selector(plan),
            )
        finally:
            browser.close()
    capture_seconds = max(0.0, time.perf_counter() - started)
    if not candidates:
        raise ValueError("bounded discovery found no visible candidates")

    targets = rank_targets(plan.targets, candidates, profile)
    ambiguities = tuple(
        DiscoveryAmbiguity(
            id=f"amb_{result.target_id}",
            target_id=result.target_id,
            candidate_ids=tuple(item.candidate_id for item in result.ranked_candidates),
        )
        for result in targets
        if result.state is DiscoveryTargetState.AMBIGUOUS
    )
    state = (
        DiscoveryRunState.AWAITING_RESOLUTION
        if ambiguities or any(item.state is DiscoveryTargetState.MISSING for item in targets)
        else DiscoveryRunState.RESOLVED
    )
    minimized = minimize_source_url(plan.source_url)
    digest = _capture_digest(
        plan=plan,
        profile=profile,
        source_url=minimized,
        captured_at=captured_at,
        candidates=candidates,
        targets=targets,
    )
    return ProcessDiscoveryRun(
        id=run_id,
        profile_id=profile.id,
        plan_id=plan.id,
        context_id=plan.context_id,
        source_url=minimized,
        captured_at=captured_at,
        updated_at=captured_at,
        capture_seconds=capture_seconds,
        state=state,
        candidates=candidates,
        targets=targets,
        ambiguities=ambiguities,
        capture_sha256=digest,
    )


def _scan_selector(plan: ProcessDiscoveryPlan) -> str:
    expected_roles = {
        role
        for target in plan.targets
        for role in target.expected_roles
    }
    if "heading" in expected_roles:
        return f"{_BASE_SCAN_SELECTOR}, {_HEADING_SCAN_SELECTOR}"
    return _BASE_SCAN_SELECTOR


def _collect_candidates(
    page,
    profile: DiscoveryProfile,
    *,
    selector: str,
) -> tuple[ElementCandidate, ...]:
    locator = page.locator(selector)
    count = min(locator.count(), profile.max_elements_scanned)
    values: list[ElementCandidate] = []
    for index in range(count):
        item = locator.nth(index)
        if not item.is_visible():
            continue
        raw = item.evaluate(
            """
            el => {
              const label = el.labels && el.labels.length ? el.labels[0].innerText.trim() : null;
              const buttonText = el.tagName.toLowerCase() === 'button' ? el.innerText.trim() : null;
              const headingText = /^h[1-6]$/.test(el.tagName.toLowerCase()) ? el.innerText.trim() : null;
              return {
                tagName: el.tagName.toLowerCase(),
                id: el.getAttribute('id'),
                role: el.getAttribute('role'),
                ariaLabel: el.getAttribute('aria-label'),
                name: el.getAttribute('name'),
                placeholder: el.getAttribute('placeholder'),
                type: el.getAttribute('type'),
                testId: el.getAttribute('data-testid'),
                label,
                buttonText,
                headingText,
                disabled: el.disabled === true,
                contentEditable: el.isContentEditable === true
              };
            }
            """
        )
        role = _semantic_role(raw)
        semantic_name = _semantic_name(raw)
        if not semantic_name:
            continue
        attributes = _attributes(raw)
        discovered_locators = _locator_candidates(page, raw, role, semantic_name, index + 1)
        if not discovered_locators:
            continue
        editable = _editable(raw, role)
        values.append(
            ElementCandidate(
                id=f"cand_{index + 1:03d}",
                ordinal=index + 1,
                tag_name=raw["tagName"],
                semantic_role=role,
                semantic_name=semantic_name[:160],
                enabled=not bool(raw.get("disabled")),
                editable=editable,
                attributes=attributes,
                locator_candidates=discovered_locators,
            )
        )
    return tuple(values)


def _semantic_role(raw: dict[str, Any]) -> str:
    if raw.get("role"):
        return str(raw["role"]).casefold()
    tag = raw["tagName"]
    input_type = str(raw.get("type") or "").casefold()
    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        return "heading"
    if tag == "button":
        return "button"
    if tag == "input" and input_type == "search":
        return "searchbox"
    if tag == "input" and input_type == "checkbox":
        return "checkbox"
    if tag in {"input", "textarea"}:
        return "textbox"
    if tag == "select":
        return "combobox"
    if tag in {"ul", "ol"}:
        return "list"
    if tag == "table":
        return "table"
    return "status" if raw.get("ariaLabel") else "generic"


def _semantic_name(raw: dict[str, Any]) -> str:
    for key in ("ariaLabel", "label", "placeholder", "buttonText", "headingText", "testId", "id", "name"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _attributes(raw: dict[str, Any]) -> tuple[CandidateAttribute, ...]:
    pairs = (
        ("id", raw.get("id")),
        ("data-testid", raw.get("testId")),
        ("name", raw.get("name")),
        ("placeholder", raw.get("placeholder")),
        ("type", raw.get("type")),
        ("aria-label", raw.get("ariaLabel")),
        ("label", raw.get("label")),
    )
    return tuple(
        CandidateAttribute(name=name, value=str(value).strip()[:160])
        for name, value in pairs
        if isinstance(value, str) and value.strip()
    )


def _locator_candidates(page, raw, role: str, semantic_name: str, ordinal: int) -> tuple[DiscoveredLocator, ...]:
    proposals: list[tuple[LocatorStrategy, str, int]] = []
    if raw.get("label"):
        proposals.append((LocatorStrategy.LABEL, raw["label"].strip(), 10))
    if raw.get("testId"):
        proposals.append((LocatorStrategy.TEST_ID, raw["testId"].strip(), 20))
    if role != "generic" and semantic_name:
        proposals.append((LocatorStrategy.ROLE, f"{role}:{semantic_name}", 30))
    if raw.get("placeholder"):
        proposals.append((LocatorStrategy.PLACEHOLDER, raw["placeholder"].strip(), 40))
    if raw.get("id"):
        proposals.append((LocatorStrategy.CSS, f"#{raw['id'].strip()}", 50))

    values = []
    seen: set[tuple[LocatorStrategy, str]] = set()
    for sequence, (strategy, value, priority) in enumerate(proposals, start=1):
        key = (strategy, value)
        if key in seen:
            continue
        seen.add(key)
        values.append(
            DiscoveredLocator(
                id=f"dc_{ordinal:03d}_{sequence:02d}",
                strategy=strategy,
                value=value,
                match_count=_match_count(page, strategy, value),
                priority=priority,
            )
        )
    return tuple(values)


def _match_count(page, strategy: LocatorStrategy, value: str) -> int:
    if strategy is LocatorStrategy.LABEL:
        return page.get_by_label(value, exact=True).count()
    if strategy is LocatorStrategy.TEST_ID:
        return page.get_by_test_id(value).count()
    if strategy is LocatorStrategy.ROLE:
        role, _, name = value.partition(":")
        return page.get_by_role(role, name=name, exact=True).count()
    if strategy is LocatorStrategy.PLACEHOLDER:
        return page.get_by_placeholder(value, exact=True).count()
    if strategy is LocatorStrategy.CSS:
        return page.locator(value).count()
    return 0


def _editable(raw: dict[str, Any], role: str) -> bool:
    return raw["tagName"] in {"input", "textarea", "select"} or bool(
        raw.get("contentEditable")
    ) or role in {"textbox", "searchbox", "combobox"}


def minimize_source_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"file", "http", "https"}:
        raise ValueError("discovery URL must use file, http, or https")
    if parsed.username or parsed.password:
        raise ValueError("discovery URL must not contain credentials")
    host = parsed.hostname or ""
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def _capture_digest(*, plan, profile, source_url, captured_at, candidates, targets) -> str:
    payload = {
        "plan_id": plan.id,
        "profile_id": profile.id,
        "source_url": source_url,
        "captured_at": captured_at.isoformat(),
        "candidates": [value.model_dump(mode="json") for value in candidates],
        "targets": [value.model_dump(mode="json") for value in targets],
    }
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()
