import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import ActionKind, KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.io import load_guided_profile
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.interactive_creation.enums import InteractiveSessionState
from test_cartographer.interactive_creation.io import load_operator_session
from test_cartographer.interactive_creation.runner import (
    InteractiveFlowStopped,
    run_human_triggered_creation_flow,
)
from test_cartographer.interactive_creation.target_planning import (
    ExternalTargetProposalState,
    ReplayExternalTargetProposalProvider,
    parse_external_target_payload,
    plan_external_target_proposal,
    review_external_target_proposal,
    review_target_proposal_interactively,
    save_external_target_proposal_run,
)

NOW = datetime(2026, 8, 16, 10, 0, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def replay_profile():
    return load_guided_profile(
        ROOT / "testdata" / "guided_intake" / "profile" / "replay.json"
    )


def _provided(value: str) -> KnowledgeText:
    return KnowledgeText(
        value=value,
        status=KnowledgeStatus.PROVIDED,
        evidence_ids=("ev_initial_request",),
        sensitivity=SensitivityLevel.PUBLIC,
    )


def _context() -> ContextBundle:
    seed = MinimalContextSeed(
        id="seed_target_review",
        context_id="ctx_target_review",
        title="External target review",
        initial_request="Find hammer products and show cheapest suitable results first.",
        created_at=NOW,
        sensitivity=SensitivityLevel.PUBLIC,
    )
    context = build_minimal_context(seed)
    application = context.application.model_copy(
        update={
            "name": _provided("Toolshop"),
            "environment": _provided("public live demo"),
            "base_url": _provided("https://practicesoftwaretesting.com/"),
        }
    )
    outcome = context.process.expected_outcomes[0].model_copy(
        update={
            "statement": _provided(
                "Relevant hammer products are visible in ascending price order."
            )
        }
    )
    process = context.process.model_copy(
        update={
            "name": _provided("Search and filter products"),
            "purpose": _provided("Find relevant products and show cheapest first."),
            "risk": _provided(
                "Relevant products can be missing or incorrectly ordered."
            ),
            "role": _provided("Unauthenticated customer"),
            "preconditions": (_provided("The public catalogue is available."),),
            "expected_outcomes": (outcome,),
        }
    )
    return ContextBundle.model_validate(
        context.model_copy(
            update={"application": application, "process": process}
        ).model_dump(mode="python")
    )


def _payload(actions) -> str:
    return json.dumps({"schema_version": "0.1", "actions": actions})


def _valid_actions():
    return [
        {
            "name": "Catalogue search",
            "action_kind": "fill",
            "expected_roles": ["searchbox", "textbox"],
            "test_data_symbolic_ref": "search_term",
            "outcome_target": False,
        },
        {
            "name": "Visible matching products",
            "action_kind": "read",
            "expected_roles": ["list", "status", "generic"],
            "test_data_symbolic_ref": None,
            "outcome_target": True,
        },
    ]


def _run(replay_profile, run_id="target_plan_reference"):
    context = _context()
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(_valid_actions())]
    )
    run = plan_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        run_id=run_id,
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )
    return context, provider, run


def test_replay_provider_produces_review_only_run(replay_profile):
    _context_value, provider, run = _run(replay_profile)

    assert run.state is ExternalTargetProposalState.READY_FOR_REVIEW
    assert run.provider is GuidanceProviderKind.REPLAY
    assert [item.action_kind for item in run.targets] == [
        ActionKind.FILL,
        ActionKind.READ,
    ]
    assert run.raw_prompt_persisted is False
    assert run.raw_response_persisted is False
    assert provider.call_count == 1


def test_payload_rejects_missing_final_read():
    actions = _valid_actions()
    actions[-1]["action_kind"] = "click"
    actions[-1]["expected_roles"] = ["button"]

    with pytest.raises(ValueError, match="final READ outcome"):
        parse_external_target_payload(_payload(actions))


def test_payload_rejects_locator_like_name():
    actions = _valid_actions()
    actions[0]["name"] = "css=#search-query"

    with pytest.raises(ValueError, match="must not contain a locator"):
        parse_external_target_payload(_payload(actions))


def test_operator_can_insert_missing_sort(replay_profile):
    context, _provider, run = _run(replay_profile, "target_plan_edit")
    answers = iter(
        ("add", "select", "Price ascending sort", "combobox", "sort_order", "")
    )

    decision, targets, edits = review_target_proposal_interactively(
        context,
        run.targets,
        input_fn=lambda _prompt="": next(answers),
        output_fn=lambda _message: None,
    )

    assert decision == "accepted"
    assert edits == 1
    assert [item.action_kind for item in targets] == [
        ActionKind.FILL,
        ActionKind.SELECT,
        ActionKind.READ,
    ]
    assert targets[1].test_data_symbolic_ref == "sort_order"


def test_operator_rejection_never_becomes_authority(replay_profile):
    context, _provider, run = _run(replay_profile, "target_plan_reject")

    decision, targets, edits = review_target_proposal_interactively(
        context,
        run.targets,
        input_fn=lambda _prompt="": "reject",
        output_fn=lambda _message: None,
    )
    rejected = review_external_target_proposal(
        run,
        context,
        targets,
        state=ExternalTargetProposalState.REJECTED,
        reviewed_at=NOW,
        review_seconds=1.0,
        operator_edit_count=edits,
    )

    assert decision == "rejected"
    assert rejected.state is ExternalTargetProposalState.REJECTED


def test_invalid_provider_semantics_leave_blocked_audit_evidence(replay_profile):
    actions = _valid_actions()
    actions[-1]["action_kind"] = "click"
    actions[-1]["expected_roles"] = ["button"]
    context = _context()

    run = plan_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        ReplayExternalTargetProposalProvider(outputs=[_payload(actions)]),
        run_id="target_plan_blocked",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert run.state is ExternalTargetProposalState.BLOCKED
    assert run.targets == ()
    assert run.blocker == "invalid_final_read"
    assert len(run.prompt_sha256) == 64
    assert len(run.response_sha256) == 64


def test_invalid_proposal_stops_runner_before_browser(
    tmp_path,
    replay_profile,
    interactive_profile,
):
    actions = _valid_actions()
    actions[-1]["action_kind"] = "click"
    actions[-1]["expected_roles"] = ["button"]
    provider = ReplayExternalTargetProposalProvider(outputs=[_payload(actions)])
    values = iter(
        (
            "Find hammer products and show cheapest suitable results first.",
            "Toolshop",
            "public live demo",
            "https://practicesoftwaretesting.com/",
            "Search and filter products",
            "Find relevant products and show cheapest first.",
            "Relevant products can be missing or incorrectly ordered.",
            "Unauthenticated customer",
            "The public catalogue is available.",
            "Relevant hammer products are visible in ascending price order.",
            "",
        )
    )
    browser_calls = []

    def browser_opener(*args, **kwargs):
        browser_calls.append((args, kwargs))
        raise AssertionError("browser must not start for a blocked proposal")

    output = tmp_path / "blocked-target-run"
    with pytest.raises(RuntimeError, match="proposal failed closed"):
        run_human_triggered_creation_flow(
            project_root=ROOT,
            output_dir=output,
            framework_root=None,
            interactive_profile=interactive_profile,
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5-coder:7b",
            timeout_seconds=1.0,
            provider_mode="replay",
            browser_opener=browser_opener,
            input_fn=lambda _prompt="": next(values),
            output_fn=lambda _message: None,
            external_public_single_page=True,
            target_proposal_provider=provider,
        )

    session = load_operator_session(output / "operator-session.json")
    proposal = json.loads(
        (output / "02-interaction-target-proposal.json").read_text(
            encoding="utf-8"
        )
    )
    assert session.state is InteractiveSessionState.ABORTED
    assert proposal["state"] == "blocked"
    assert proposal["blocker"] == "invalid_final_read"
    assert browser_calls == []


def test_rejected_proposal_stops_runner_before_browser(
    tmp_path,
    interactive_profile,
):
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(_valid_actions())]
    )
    values = iter(
        (
            "Find hammer products and show cheapest suitable results first.",
            "Toolshop",
            "public live demo",
            "https://practicesoftwaretesting.com/",
            "Search and filter products",
            "Find relevant products and show cheapest first.",
            "Relevant products can be missing or incorrectly ordered.",
            "Unauthenticated customer",
            "The public catalogue is available.",
            "Relevant hammer products are visible in ascending price order.",
            "",
            "reject",
        )
    )
    browser_calls = []

    def browser_opener(*args, **kwargs):
        browser_calls.append((args, kwargs))
        raise AssertionError("browser must not start for a rejected proposal")

    output = tmp_path / "rejected-target-run"
    with pytest.raises(InteractiveFlowStopped, match="rejected external"):
        run_human_triggered_creation_flow(
            project_root=ROOT,
            output_dir=output,
            framework_root=None,
            interactive_profile=interactive_profile,
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5-coder:7b",
            timeout_seconds=1.0,
            provider_mode="replay",
            browser_opener=browser_opener,
            input_fn=lambda _prompt="": next(values),
            output_fn=lambda _message: None,
            external_public_single_page=True,
            target_proposal_provider=provider,
        )

    session = load_operator_session(output / "operator-session.json")
    proposal = json.loads(
        (output / "02-interaction-target-proposal.json").read_text(
            encoding="utf-8"
        )
    )
    assert session.state is InteractiveSessionState.ABORTED
    assert proposal["state"] == "rejected"
    assert browser_calls == []


def test_accepted_proposal_becomes_discovery_plan_authority(
    tmp_path,
    interactive_profile,
):
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(_valid_actions())]
    )
    values = iter(
        (
            "Find hammer products and show cheapest suitable results first.",
            "Toolshop",
            "public live demo",
            "https://practicesoftwaretesting.com/",
            "Search and filter products",
            "Find relevant products and show cheapest first.",
            "Relevant products can be missing or incorrectly ordered.",
            "Unauthenticated customer",
            "The public catalogue is available.",
            "Relevant hammer products are visible in ascending price order.",
            "",
            "",
        )
    )
    browser_plans = []

    def browser_opener(plan, *args, **kwargs):
        browser_plans.append(plan)
        raise RuntimeError("accepted discovery-plan boundary reached")

    output = tmp_path / "accepted-target-run"
    with pytest.raises(RuntimeError, match="discovery-plan boundary reached"):
        run_human_triggered_creation_flow(
            project_root=ROOT,
            output_dir=output,
            framework_root=None,
            interactive_profile=interactive_profile,
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5-coder:7b",
            timeout_seconds=1.0,
            provider_mode="replay",
            browser_opener=browser_opener,
            input_fn=lambda _prompt="": next(values),
            output_fn=lambda _message: None,
            external_public_single_page=True,
            target_proposal_provider=provider,
        )

    proposal = json.loads(
        (output / "02-interaction-target-proposal.json").read_text(
            encoding="utf-8"
        )
    )
    assert proposal["state"] == "accepted"
    assert len(browser_plans) == 1
    assert [target.action_kind for target in browser_plans[0].targets] == [
        ActionKind.FILL,
        ActionKind.READ,
    ]


def test_persistence_excludes_raw_provider_content(
    tmp_path,
    replay_profile,
):
    _context_value, _provider, run = _run(
        replay_profile,
        "target_plan_persistence",
    )
    path = tmp_path / "target-proposal.json"

    save_external_target_proposal_run(run, path)
    saved = path.read_text(encoding="utf-8")

    assert run.prompt_sha256 in saved
    assert run.response_sha256 in saved
    assert "Find hammer products" not in saved
    assert '"raw_prompt_persisted": false' in saved
    assert '"raw_response_persisted": false' in saved
