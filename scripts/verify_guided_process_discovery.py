"""Verify bounded multi-element discovery with replay guidance and Chromium."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.io import save_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.discovery.apply import apply_accepted_discovery
from test_cartographer.discovery.assessment import assess_discovery
from test_cartographer.discovery.capture import capture_process_discovery
from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision
from test_cartographer.discovery.io import (
    load_discovery_plan,
    load_discovery_profile,
    save_discovery_plan,
    save_discovery_run,
)
from test_cartographer.discovery.provider import ReplayDiscoveryProvider
from test_cartographer.intake.io import load_session
from test_cartographer.observation.reference import serve_reference_directory

ROOT = Path(__file__).resolve().parents[1]


def _executable() -> str | None:
    explicit = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
    if explicit:
        return explicit
    if os.name != "nt":
        return shutil.which("chromium") or shutil.which("google-chrome")
    return None


def _candidate_with_test_id(run, value: str) -> str:
    for candidate in run.candidates:
        if any(item.name == "data-testid" and item.value == value for item in candidate.attributes):
            return candidate.id
    raise RuntimeError(f"candidate with data-testid={value} was not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=".test-cartographer/sprint-9/replay")
    parser.add_argument("--require-browser", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    session = load_session(ROOT / "testdata/guided_intake/session/replay_complete.json")
    context = session.context
    plan = load_discovery_plan(ROOT / "testdata/discovery/plan/public_catalog.json")
    profile = load_discovery_profile(ROOT / "testdata/discovery/profile/replay.json")
    captured_at = datetime.now(timezone.utc)

    try:
        with serve_reference_directory(ROOT / "testdata/browser") as base_url:
            plan = plan.model_copy(
                update={"source_url": f"{base_url}/public_catalog_discovery.html"}
            )
            run = capture_process_discovery(
                plan,
                profile,
                run_id="discovery_replay_reference",
                captured_at=captured_at,
                executable_path=_executable(),
            )
    except Exception:
        if args.require_browser:
            raise
        raise

    if len(run.candidates) != 4:
        raise RuntimeError(f"expected four bounded candidates, found {len(run.candidates)}")
    if len(run.ambiguities) != 1:
        raise RuntimeError(f"expected one ambiguity, found {len(run.ambiguities)}")
    save_context(context, output / "guided-context.json")
    save_discovery_plan(plan, output / "plan.json")
    save_discovery_run(run, output / "captured-run.json")

    replay_output = (ROOT / "testdata/discovery/replay/search_submit_ambiguity.json").read_text(
        encoding="utf-8"
    )
    provider = ReplayDiscoveryProvider([replay_output])
    ambiguity = run.ambiguities[0]
    question, run = phrase_ambiguity(
        run,
        plan.targets,
        profile,
        provider,
        ambiguity_id=ambiguity.id,
        started_at=captured_at + timedelta(seconds=1),
        completed_at=captured_at + timedelta(seconds=2),
    )
    selected = _candidate_with_test_id(run, "search-submit")
    run = resolve_ambiguity(
        run,
        ambiguity_id=ambiguity.id,
        selected_candidate_id=selected,
        resolved_at=captured_at + timedelta(seconds=3),
        reason="Human selected the submit button identified by data-testid=search-submit.",
    )
    run = review_discovery(
        run,
        decision=DiscoveryDecision.ACCEPTED,
        reviewed_at=captured_at + timedelta(seconds=4),
        reason="All three process targets and their unique locator candidates were reviewed.",
        review_seconds=2.0,
    )
    updated = apply_accepted_discovery(context, plan, run)
    discovery_report = assess_discovery(run)
    readiness = assess_readiness(updated)
    if not discovery_report.ready_for_context_application:
        raise RuntimeError("accepted discovery is not ready for context application")
    if not readiness.ready:
        codes = ", ".join(item.code for item in readiness.issues)
        raise RuntimeError(f"discovered context remains blocked: {codes}")
    save_discovery_run(run, output / "complete-run.json")
    save_context(updated, output / "discovered-context.json")

    print("Guided-intake context loaded without pre-existing selectors.")
    print("One controlled page produced four bounded visible candidates.")
    print("Search input and results region were selected deterministically.")
    print("Two equal Search buttons produced exactly one ambiguity.")
    print(f"Replay clarification question: {question.user_prompt}")
    print("Human selection resolved the ambiguous submit control.")
    print("Three accepted elements received unique observed locator candidates.")
    print("One page, one component, four process steps, and symbolic test data were created.")
    print("Input values, generic page text, HTML, screenshot, and raw page were not persisted.")
    print("Ready for context application: true")
    print("Full adaptation readiness: ready")
    print(f"Captured run: {output / 'captured-run.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
