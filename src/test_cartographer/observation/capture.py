"""Bounded Playwright capture for one selected context element."""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlsplit, urlunsplit

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.models import ContextBundle, LocatorCandidate, UIElement
from test_cartographer.observation.enums import ObservedAttributeName
from test_cartographer.observation.models import (
    BrowserObservation,
    ElementSnapshot,
    LocatorVerification,
    ObservedAttribute,
)

_EDITABLE_ARIA_ROLES = frozenset(
    {
        "checkbox",
        "combobox",
        "grid",
        "gridcell",
        "listbox",
        "radiogroup",
        "slider",
        "spinbutton",
        "textbox",
        "columnheader",
        "rowheader",
        "searchbox",
        "switch",
        "treegrid",
    }
)

_ATTRIBUTE_MAP: tuple[tuple[ObservedAttributeName, str], ...] = (
    (ObservedAttributeName.ID, "id"),
    (ObservedAttributeName.ROLE, "role"),
    (ObservedAttributeName.ARIA_LABEL, "aria-label"),
    (ObservedAttributeName.NAME, "name"),
    (ObservedAttributeName.PLACEHOLDER, "placeholder"),
    (ObservedAttributeName.TYPE, "type"),
    (ObservedAttributeName.TEST_ID, "data-testid"),
)


class LocatorLike(Protocol):
    def count(self) -> int: ...

    def is_visible(self) -> bool: ...

    def is_enabled(self) -> bool: ...

    def is_editable(self) -> bool: ...

    def evaluate(self, expression: str) -> Any: ...


class PageLike(Protocol):
    url: str

    def get_by_role(self, role: str, **kwargs: Any) -> LocatorLike: ...

    def get_by_label(self, text: str, **kwargs: Any) -> LocatorLike: ...

    def get_by_test_id(self, test_id: str) -> LocatorLike: ...

    def get_by_placeholder(self, text: str, **kwargs: Any) -> LocatorLike: ...

    def get_by_text(self, text: str, **kwargs: Any) -> LocatorLike: ...

    def locator(self, selector: str) -> LocatorLike: ...


def capture_browser_observation(
    context: ContextBundle,
    *,
    url: str,
    element_id: str,
    observation_id: str,
    captured_at: datetime,
    sensitivity: SensitivityLevel,
    headless: bool = True,
    timeout_ms: int = 10_000,
    executable_path: str | None = None,
) -> BrowserObservation:
    """Open one user-authorized page and capture one selected target only."""

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - exercised without browser extra
        raise RuntimeError(
            "Playwright is not installed. Install TestCartographer with [browser]."
        ) from exc

    launch_path = executable_path or os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    started = time.perf_counter()
    with sync_playwright() as playwright:
        launch_options: dict[str, Any] = {"headless": headless}
        if launch_path:
            launch_options["executable_path"] = launch_path
        browser = playwright.chromium.launch(**launch_options)
        try:
            browser_context = browser.new_context()
            page = browser_context.new_page()
            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="domcontentloaded")
            capture_seconds = max(0.0, time.perf_counter() - started)
            return capture_page_observation(
                page,
                context,
                element_id=element_id,
                observation_id=observation_id,
                captured_at=captured_at,
                sensitivity=sensitivity,
                capture_seconds=capture_seconds,
            )
        finally:
            browser.close()


def capture_page_observation(
    page: PageLike,
    context: ContextBundle,
    *,
    element_id: str,
    observation_id: str,
    captured_at: datetime,
    sensitivity: SensitivityLevel,
    capture_seconds: float,
) -> BrowserObservation:
    """Create a minimized observation from an already controlled page."""

    element = _element(context, element_id)
    locator_candidate = _primary_locator(element)
    locator = resolve_locator(page, locator_candidate)
    match_count = locator.count()
    if match_count != 1:
        raise ValueError(
            f"locator {locator_candidate.id} matched {match_count} elements; exactly 1 is required"
        )
    if not locator.is_visible():
        raise ValueError(f"locator {locator_candidate.id} matched a non-visible element")

    raw_snapshot = locator.evaluate(
        """element => ({
            tagName: element.tagName.toLowerCase(),
            id: element.getAttribute('id'),
            role: element.getAttribute('role'),
            ariaLabel: element.getAttribute('aria-label'),
            name: element.getAttribute('name'),
            placeholder: element.getAttribute('placeholder'),
            type: element.getAttribute('type'),
            testId: element.getAttribute('data-testid'),
            contentEditable: element.isContentEditable
        })"""
    )
    if not isinstance(raw_snapshot, Mapping):
        raise ValueError("browser snapshot must be an object")

    attributes = _allowlisted_attributes(raw_snapshot)
    editable = (
        locator.is_editable() if _supports_editability_check(raw_snapshot) else False
    )
    snapshot = ElementSnapshot(
        tag_name=str(raw_snapshot.get("tagName", "")),
        visible=True,
        enabled=locator.is_enabled(),
        editable=editable,
        attributes=attributes,
    )
    verification = LocatorVerification(
        locator_id=locator_candidate.id,
        strategy=locator_candidate.strategy,
        value=locator_candidate.value.value or "",
        match_count=1,
        visible=True,
    )
    minimized_url = minimize_source_url(page.url)
    digest = _capture_digest(
        observation_id=observation_id,
        context_id=context.id,
        element_id=element.id,
        source_url=minimized_url,
        captured_at=captured_at,
        sensitivity=sensitivity,
        locator=verification,
        element=snapshot,
    )
    return BrowserObservation(
        id=observation_id,
        context_id=context.id,
        target_element_id=element.id,
        target_locator_id=locator_candidate.id,
        source_url=minimized_url,
        captured_at=captured_at,
        sensitivity=sensitivity,
        capture_seconds=capture_seconds,
        locator=verification,
        element=snapshot,
        capture_sha256=digest,
    )


def _supports_editability_check(raw_snapshot: Mapping[str, Any]) -> bool:
    """Return whether Playwright can safely evaluate editable state."""

    tag_name = str(raw_snapshot.get("tagName", "")).lower()
    if tag_name in {"input", "textarea", "select"}:
        return True
    if raw_snapshot.get("contentEditable") is True:
        return True
    role = raw_snapshot.get("role")
    return isinstance(role, str) and role in _EDITABLE_ARIA_ROLES


def resolve_locator(page: PageLike, candidate: LocatorCandidate) -> LocatorLike:
    """Resolve the small locator vocabulary without storing Playwright objects."""

    value = candidate.value.value
    if value is None:
        raise ValueError(f"locator {candidate.id} has no usable value")
    if candidate.strategy is LocatorStrategy.ROLE:
        role, separator, name = value.partition(":")
        if not separator or not role or not name:
            raise ValueError("role locator value must use role:name format")
        return page.get_by_role(role, name=name, exact=True)
    if candidate.strategy is LocatorStrategy.LABEL:
        return page.get_by_label(value, exact=True)
    if candidate.strategy is LocatorStrategy.TEST_ID:
        return page.get_by_test_id(value)
    if candidate.strategy is LocatorStrategy.PLACEHOLDER:
        return page.get_by_placeholder(value, exact=True)
    if candidate.strategy is LocatorStrategy.TEXT:
        return page.get_by_text(value, exact=True)
    if candidate.strategy is LocatorStrategy.CSS:
        return page.locator(value)
    if candidate.strategy is LocatorStrategy.XPATH:
        selector = value if value.startswith("xpath=") else f"xpath={value}"
        return page.locator(selector)
    raise ValueError(f"unsupported locator strategy: {candidate.strategy}")


def minimize_source_url(url: str) -> str:
    """Remove credentials, query, and fragment before local persistence."""

    parsed = urlsplit(url)
    if parsed.scheme not in {"file", "http", "https"}:
        raise ValueError("browser source URL must use file, http, or https")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("browser source URL must not contain credentials")
    host = parsed.hostname or ""
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    netloc = host
    return urlunsplit((parsed.scheme, netloc, parsed.path, "", ""))


def _element(context: ContextBundle, element_id: str) -> UIElement:
    try:
        return next(element for element in context.elements if element.id == element_id)
    except StopIteration as exc:
        raise ValueError(f"unknown context element: {element_id}") from exc


def _primary_locator(element: UIElement) -> LocatorCandidate:
    primary = [candidate for candidate in element.locator_candidates if candidate.primary]
    if len(primary) != 1:
        raise ValueError(f"element {element.id} requires exactly one primary locator")
    return primary[0]


def _allowlisted_attributes(
    raw_snapshot: Mapping[str, Any],
) -> tuple[ObservedAttribute, ...]:
    key_map = {
        "id": "id",
        "role": "role",
        "aria-label": "ariaLabel",
        "name": "name",
        "placeholder": "placeholder",
        "type": "type",
        "data-testid": "testId",
    }
    attributes: list[ObservedAttribute] = []
    for attribute_name, _dom_name in _ATTRIBUTE_MAP:
        raw_key = key_map[attribute_name.value]
        value = raw_snapshot.get(raw_key)
        if isinstance(value, str) and value.strip():
            attributes.append(
                ObservedAttribute(name=attribute_name, value=value.strip())
            )
    return tuple(attributes)


def _capture_digest(
    *,
    observation_id: str,
    context_id: str,
    element_id: str,
    source_url: str,
    captured_at: datetime,
    sensitivity: SensitivityLevel,
    locator: LocatorVerification,
    element: ElementSnapshot,
) -> str:
    payload = {
        "observation_id": observation_id,
        "context_id": context_id,
        "element_id": element_id,
        "source_url": source_url,
        "captured_at": captured_at.isoformat(),
        "sensitivity": sensitivity.value,
        "locator": locator.model_dump(mode="json"),
        "element": element.model_dump(mode="json"),
    }
    rendered = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def local_file_url(path: str | Path) -> str:
    """Return a portable file URL for a controlled local fixture."""

    return Path(path).resolve().as_uri()
