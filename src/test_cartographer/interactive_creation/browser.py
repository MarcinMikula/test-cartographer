"""Visible, non-persistent browser review for bounded discovery candidates."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from test_cartographer.discovery.capture import (
    _capture_digest,
    _collect_candidates,
    _scan_selector,
    minimize_source_url,
)
from test_cartographer.discovery.enums import DiscoveryRunState, DiscoveryTargetState
from test_cartographer.discovery.models import (
    DiscoveryAmbiguity,
    DiscoveryProfile,
    ProcessDiscoveryPlan,
    ProcessDiscoveryRun,
)
from test_cartographer.discovery.ranking import rank_targets


@dataclass
class InteractiveDiscoveryBrowser:
    """Keep a headed browser open while the operator reviews candidates."""

    playwright: Any
    browser: Any
    page: Any
    run: ProcessDiscoveryRun

    def focus_candidates(self, candidate_ids: tuple[str, ...]) -> None:
        self.page.evaluate(
            """
            ids => {
              const selected = new Set(ids);
              document.querySelectorAll('[data-test-cartographer-candidate]').forEach(el => {
                const active = selected.has(el.getAttribute('data-test-cartographer-candidate'));
                el.style.outline = active ? '4px solid #d00000' : '2px solid #1864ab';
                el.style.outlineOffset = '3px';
              });
              const first = document.querySelector(`[data-test-cartographer-candidate="${ids[0]}"]`);
              if (first) first.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
            """,
            list(candidate_ids),
        )

    def close(self) -> None:
        try:
            self.browser.close()
        finally:
            self.playwright.stop()

    def __enter__(self) -> "InteractiveDiscoveryBrowser":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def open_interactive_discovery(
    plan: ProcessDiscoveryPlan,
    profile: DiscoveryProfile,
    *,
    run_id: str,
    captured_at: datetime,
    timeout_ms: int = 10_000,
    executable_path: str | None = None,
) -> InteractiveDiscoveryBrowser:
    """Capture candidates and leave a headed annotated browser open for review."""

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Playwright is required for interactive discovery") from exc

    if plan.sensitivity not in profile.allowed_sensitivities:
        raise ValueError("discovery sensitivity is not allowed by the profile")

    started = time.perf_counter()
    playwright = sync_playwright().start()
    launch: dict[str, object] = {"headless": False}
    if executable_path:
        launch["executable_path"] = executable_path
    browser = None
    try:
        browser = playwright.chromium.launch(**launch)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(plan.source_url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(100)
        selector = _scan_selector(plan)
        candidates = _collect_candidates(page, profile, selector=selector)
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
            if ambiguities
            or any(item.state is DiscoveryTargetState.MISSING for item in targets)
            else DiscoveryRunState.RESOLVED
        )
        minimized = minimize_source_url(plan.source_url)
        capture_seconds = max(0.0, time.perf_counter() - started)
        run = ProcessDiscoveryRun(
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
            capture_sha256=_capture_digest(
                plan=plan,
                profile=profile,
                source_url=minimized,
                captured_at=captured_at,
                candidates=candidates,
                targets=targets,
            ),
        )
        _annotate_candidates(page, candidates, selector=selector)
        return InteractiveDiscoveryBrowser(playwright, browser, page, run)
    except Exception:
        if browser is not None:
            browser.close()
        playwright.stop()
        raise


def _annotate_candidates(page, candidates, *, selector: str) -> None:
    markers = [{"ordinal": item.ordinal, "id": item.id} for item in candidates]
    page.evaluate(
        """
        ({selector, markers}) => {
          document.querySelectorAll('[data-test-cartographer-overlay]').forEach(el => el.remove());
          const elements = Array.from(document.querySelectorAll(selector));
          for (const marker of markers) {
            const el = elements[marker.ordinal - 1];
            if (!el) continue;
            el.setAttribute('data-test-cartographer-candidate', marker.id);
            el.style.outline = '2px solid #1864ab';
            el.style.outlineOffset = '3px';
            const badge = document.createElement('div');
            badge.setAttribute('data-test-cartographer-overlay', marker.id);
            badge.textContent = marker.id;
            const rect = el.getBoundingClientRect();
            Object.assign(badge.style, {
              position: 'fixed',
              left: `${Math.max(0, rect.left)}px`,
              top: `${Math.max(0, rect.top - 22)}px`,
              zIndex: '2147483647',
              background: '#1864ab',
              color: 'white',
              font: 'bold 12px sans-serif',
              padding: '2px 5px',
              borderRadius: '3px',
              pointerEvents: 'none'
            });
            document.body.appendChild(badge);
          }
        }
        """,
        {"selector": selector, "markers": markers},
    )
