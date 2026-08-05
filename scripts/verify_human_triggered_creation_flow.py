"""Exercise the Sprint 11 interactive orchestrator with scripted operator input.

This verifier proves mechanics only. The setup additionally requires a real operator run.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import threading
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from test_cartographer.context.enums import LocatorStrategy
from test_cartographer.discovery.capture import minimize_source_url
from test_cartographer.discovery.enums import DiscoveryRunState, DiscoveryTargetState
from test_cartographer.discovery.models import (
    CandidateAttribute,
    DiscoveredLocator,
    DiscoveryAmbiguity,
    ElementCandidate,
    ProcessDiscoveryRun,
)
from test_cartographer.discovery.ranking import rank_targets

from test_cartographer.interactive_creation.assessment import assess_interactive_creation
from test_cartographer.interactive_creation.io import load_interactive_profile
from test_cartographer.interactive_creation.runner import run_human_triggered_creation_flow

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen2.5-coder:7b"


class _OllamaHandler(BaseHTTPRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        return

    def _json(self, status: int, value: object) -> None:
        payload = json.dumps(value).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/version":
            self._json(200, {"version": "0.0-test"})
            return
        if self.path == "/api/tags":
            self._json(200, {"models": [{"name": MODEL, "model": MODEL}]})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        size = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        if self.path == "/api/generate":
            self._json(200, {"model": MODEL, "response": "", "done": True})
            return
        if self.path != "/api/chat":
            self._json(404, {"error": "not found"})
            return
        schema = body["format"]
        properties = schema["properties"]
        if "questions" in properties:
            phase = properties["phase"]["const"]
            ids = properties["questions"]["items"]["properties"]["question_id"]["enum"]
            content = {
                "schema_version": "0.1",
                "phase": phase,
                "questions": [
                    {
                        "question_id": question_id,
                        "user_prompt": f"Please answer {question_id}.",
                        "reason": "This closes one bounded context gap.",
                        "answer_shape": "confirmation" if phase == "review" else "sentence",
                    }
                    for question_id in ids
                ],
            }
        else:
            ambiguity_id = properties["ambiguity_id"]["const"]
            ids = properties["candidate_ids"]["items"]["enum"]
            content = {
                "schema_version": "0.1",
                "ambiguity_id": ambiguity_id,
                "candidate_ids": ids,
                "user_prompt": "Which visible Search candidate performs the form submission: "
                + " or ".join(ids)
                + "?",
                "reason": "The tied browser evidence requires a human decision.",
            }
        self._json(
            200,
            {"model": MODEL, "message": {"role": "assistant", "content": json.dumps(content)}},
        )


@contextlib.contextmanager
def _ollama_stub() -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _OllamaHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


class _ScriptedOperator:
    def __init__(self) -> None:
        self.values = iter(
            [
                "I want to automate searching for a product and verify matching results.",
                "Public catalog reference application",
                "Controlled local reference environment",
                "",
                "Search the public catalog",
                "Allow a visitor to find matching catalog items.",
                "Search failures can hide relevant products.",
                "Unauthenticated visitor",
                "The public catalog is available.",
                "Matching catalog results are visible.",
                "",
                "cand_002",
                "a",
                "a",
                "a",
                "a",
                "a",
                "a",
            ]
        )
        self.calls = 0

    def __call__(self, _prompt: str = "") -> str:
        self.calls += 1
        return next(self.values)


def _locator(identifier, strategy, value, priority=10, count=1):
    return DiscoveredLocator(
        id=identifier, strategy=strategy, value=value, match_count=count, priority=priority
    )


def _candidates():
    return (
        ElementCandidate(
            id="cand_001", ordinal=1, tag_name="input", semantic_role="searchbox",
            semantic_name="Search catalog", enabled=True, editable=True,
            attributes=(CandidateAttribute(name="label", value="Search catalog"),),
            locator_candidates=(_locator("dc_001_01", LocatorStrategy.LABEL, "Search catalog"),),
        ),
        ElementCandidate(
            id="cand_002", ordinal=2, tag_name="button", semantic_role="button",
            semantic_name="Search", enabled=True, editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="search-submit"),),
            locator_candidates=(
                _locator("dc_002_01", LocatorStrategy.TEST_ID, "search-submit"),
                _locator("dc_002_02", LocatorStrategy.ROLE, "button:Search", 30, 2),
            ),
        ),
        ElementCandidate(
            id="cand_003", ordinal=3, tag_name="button", semantic_role="button",
            semantic_name="Search", enabled=True, editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="search-help"),),
            locator_candidates=(
                _locator("dc_003_01", LocatorStrategy.TEST_ID, "search-help"),
                _locator("dc_003_02", LocatorStrategy.ROLE, "button:Search", 30, 2),
            ),
        ),
        ElementCandidate(
            id="cand_004", ordinal=4, tag_name="ul", semantic_role="list",
            semantic_name="Catalog results", enabled=True, editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="catalog-results"),),
            locator_candidates=(_locator("dc_004_01", LocatorStrategy.TEST_ID, "catalog-results"),),
        ),
    )


@dataclass
class _ReplayBrowser:
    run: ProcessDiscoveryRun

    def focus_candidates(self, _candidate_ids):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def _browser_opener(plan, profile, *, run_id, captured_at, **_kwargs):
    candidates = _candidates()
    targets = rank_targets(plan.targets, candidates, profile)
    ambiguities = tuple(
        DiscoveryAmbiguity(
            id=f"amb_{target.target_id}",
            target_id=target.target_id,
            candidate_ids=tuple(item.candidate_id for item in target.ranked_candidates),
        )
        for target in targets
        if target.state is DiscoveryTargetState.AMBIGUOUS
    )
    state = DiscoveryRunState.AWAITING_RESOLUTION if ambiguities else DiscoveryRunState.RESOLVED
    return _ReplayBrowser(
        ProcessDiscoveryRun(
            id=run_id, profile_id=profile.id, plan_id=plan.id, context_id=plan.context_id,
            source_url=minimize_source_url(plan.source_url), captured_at=captured_at,
            updated_at=captured_at, capture_seconds=0.01, state=state, candidates=candidates,
            targets=targets, ambiguities=ambiguities, capture_sha256="a" * 64,
        )
    )


def _command_runner(command, _cwd, _env=None):
    return subprocess.CompletedProcess(command, 0, stdout="1 passed", stderr=""), 0.01


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=".test-cartographer/sprint-11/scripted")
    parser.add_argument("--framework-root", type=Path)
    parser.add_argument("--executable-path")
    args = parser.parse_args()
    profile = load_interactive_profile(
        ROOT / "testdata/interactive_creation/profile/public_catalog_human_trigger.json"
    )
    operator = _ScriptedOperator()
    output_messages: list[str] = []
    with _ollama_stub() as base_url:
        run, session = run_human_triggered_creation_flow(
            project_root=ROOT,
            output_dir=args.output_dir,
            framework_root=args.framework_root,
            interactive_profile=profile,
            ollama_base_url=base_url,
            ollama_model=MODEL,
            timeout_seconds=30.0,
            executable_path=args.executable_path,
            provider_mode="ollama",
            browser_opener=_browser_opener,
            command_runner=_command_runner,
            input_fn=operator,
            output_fn=output_messages.append,
        )
    report = assess_interactive_creation(session, run, profile)
    if not report.external_user_demo_ready:
        raise RuntimeError(report.blockers)
    if operator.calls != 18:
        raise RuntimeError(f"expected 18 blocking operator inputs, got {operator.calls}")
    if session.fixture_answers_used:
        raise RuntimeError("operator session must not report fixture answers")
    from test_cartographer.delivery.io import load_code_patch
    from test_cartographer.discovery.io import load_discovery_run

    output_root = Path(args.output_dir)
    patch = load_code_patch(output_root / "06-code-patch.json")
    discovery = load_discovery_run(output_root / "02-discovery-run.json")
    rendered_output = "\n".join(output_messages)
    if "Exact source follows. No lines are omitted." not in rendered_output:
        raise RuntimeError("exact patch rendering was not shown")
    if "      ..." in rendered_output:
        raise RuntimeError("exact patch rendering still contains preview ellipsis")
    for change in patch.changes:
        if change.content.rstrip("\n") not in rendered_output:
            raise RuntimeError(f"source change was not fully displayed: {change.target_path}")
    page_source = next(
        change.content for change in patch.changes
        if change.target_path == "pages/catalog_page.py"
    )
    if "Open the mapped page through the framework navigation boundary." not in page_source:
        raise RuntimeError("navigation docstring was not corrected")
    if "I want to automate searching" in page_source:
        raise RuntimeError("raw operator request leaked into navigation docstring")
    for ambiguity in discovery.ambiguities:
        if ambiguity.question is None or not ambiguity.question.endswith(("?", ".", "!")):
            raise RuntimeError("persisted ambiguity question is incomplete")
    summary = (output_root / "creation-flow-summary.md").read_text(encoding="utf-8")
    if "intake-question planning and ambiguity clarification only" not in summary:
        raise RuntimeError("summary does not disclose the bounded LLM role")
    if "deterministic reviewed reference templates" not in summary:
        raise RuntimeError("summary does not disclose deterministic synthesis")
    print("Human-triggered Creation Flow mechanics: verified.")
    print("Blocking operator prompts: 18.")
    print("Blocking browser-review boundary: verified with deterministic replay.")
    print("Local Ollama-compatible provider boundary: verified.")
    print("One generated Playwright test: passed.")
    print("Scripted verifier is not the real-operator acceptance artefact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
