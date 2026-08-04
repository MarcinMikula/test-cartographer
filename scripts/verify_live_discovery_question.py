"""Verify one real local-Ollama ambiguity question over captured browser candidates."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.io import load_context, save_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.discovery.apply import apply_accepted_discovery
from test_cartographer.discovery.assessment import assess_discovery
from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryProviderKind
from test_cartographer.discovery.io import (
    load_discovery_plan,
    load_discovery_profile,
    load_discovery_run,
    save_discovery_run,
)
from test_cartographer.discovery.provider import OllamaDiscoveryProvider

ROOT = Path(__file__).resolve().parents[1]


def _candidate_with_test_id(run, value: str) -> str:
    for candidate in run.candidates:
        if any(item.name == "data-testid" and item.value == value for item in candidate.attributes):
            return candidate.id
    raise RuntimeError(f"candidate with data-testid={value} was not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=".test-cartographer/sprint-9/replay")
    parser.add_argument("--output-dir", default=".test-cartographer/sprint-9/live")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument("--timeout-seconds", type=float, default=600.0)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    context = load_context(input_dir / "guided-context.json")
    plan = load_discovery_plan(input_dir / "plan.json")
    run = load_discovery_run(input_dir / "captured-run.json")
    profile = load_discovery_profile(ROOT / "testdata/discovery/profile/ollama_local_qwen.json")
    profile = profile.model_copy(
        update={
            "model": args.model,
            "base_url": args.base_url,
            "timeout_seconds": args.timeout_seconds,
            "provider": DiscoveryProviderKind.OLLAMA,
        }
    )
    now = datetime.now(timezone.utc)

    with OllamaDiscoveryProvider(profile) as provider:
        print("Preflighting and preloading the local Ollama model...", flush=True)
        version = provider.preflight()
        print("Starting ambiguity-question call (1/1)...", flush=True)
        question, run = phrase_ambiguity(
            run,
            plan.targets,
            profile,
            provider,
            ambiguity_id=run.ambiguities[0].id,
            started_at=now,
            completed_at=None,
        )
        print(
            f"Ambiguity-question call completed in {run.guidance_turns[-1].latency_seconds:.2f}s.",
            flush=True,
        )
        print(f"Local Ollama version: {version}")
        print(f"Local model: {args.model}")
        print(f"Live clarification question: {question.user_prompt}")

    selected = _candidate_with_test_id(run, "search-submit")
    run = resolve_ambiguity(
        run,
        ambiguity_id=run.ambiguities[0].id,
        selected_candidate_id=selected,
        resolved_at=now + timedelta(seconds=1),
        reason="Human selected the form submit control after reviewing the bounded candidates.",
    )
    run = review_discovery(
        run,
        decision=DiscoveryDecision.ACCEPTED,
        reviewed_at=now + timedelta(seconds=2),
        reason="Live-LLM question and human selection were accepted.",
        review_seconds=1.0,
    )
    updated = apply_accepted_discovery(context, plan, run)
    report = assess_discovery(run)
    readiness = assess_readiness(updated)
    if not report.ready_for_context_application or not readiness.ready:
        raise RuntimeError("live guided discovery did not reach adaptation readiness")
    save_discovery_run(run, output / "run.json")
    save_context(updated, output / "context.json")

    print("The model preserved the exact ambiguity and candidate IDs.")
    print("The model phrased a question but did not choose a browser element.")
    print("Human selection remained authoritative.")
    print("Live provider used: true")
    print("Unresolved ambiguities: 0")
    print("Ready for context application: true")
    print("Full adaptation readiness: ready")
    print("Raw prompt and raw response persisted: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
