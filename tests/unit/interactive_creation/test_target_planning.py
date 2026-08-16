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
    ExternalTargetDiagnosticCategory,
    ExternalTargetProposalState,
    ReplayExternalTargetProposalProvider,
    begin_external_target_proposal,
    parse_external_target_payload,
    plan_external_target_proposal,
    render_external_target_prompt,
    repair_external_target_proposal,
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
    assert run.schema_version == "0.2"
    assert len(run.attempts) == 1
    assert run.attempts[0].valid is True
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


def test_invalid_provider_semantics_await_bounded_repair_authority(replay_profile):
    actions = _valid_actions()
    actions[-1]["action_kind"] = "click"
    actions[-1]["expected_roles"] = ["button"]
    context = _context()

    run = plan_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        ReplayExternalTargetProposalProvider(outputs=[_payload(actions)]),
        run_id="target_plan_repairable",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert run.state is ExternalTargetProposalState.AWAITING_REPAIR
    assert run.targets == ()
    assert run.blocker == "invalid_final_read"
    assert run.diagnostic.category is ExternalTargetDiagnosticCategory.SEMANTIC_SEQUENCE
    assert run.diagnostic.path == "actions[-1]"
    assert run.diagnostic.rule_code == "final_read_outcome"
    assert run.diagnostic.repairable is True
    assert len(run.prompt_sha256) == 64
    assert len(run.response_sha256) == 64


def test_invalid_proposal_stops_runner_before_browser(
    tmp_path,
    replay_profile,
    interactive_profile,
):
    actions = _valid_actions()
    actions[0]["name"] = "css=#search-query"
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
    assert proposal["blocker"] == "locator_like_name"
    assert proposal["diagnostic"]["repairable"] is False
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

@pytest.mark.parametrize(
    ("raw_output", "blocker", "category"),
    (
        ("{", "invalid_json", ExternalTargetDiagnosticCategory.JSON_SYNTAX),
        (
            '{"schema_version":"0.1","schema_version":"0.1","actions":[]}',
            "duplicate_json_key",
            ExternalTargetDiagnosticCategory.DUPLICATE_KEY,
        ),
        (
            _payload(
                [
                    {
                        **_valid_actions()[0],
                        "name": "css=#search-query",
                    },
                    _valid_actions()[1],
                ]
            ),
            "locator_like_name",
            ExternalTargetDiagnosticCategory.UNSAFE_LOCATOR,
        ),
    ),
)
def test_nonrepairable_outputs_fail_closed_without_retry(
    replay_profile,
    raw_output,
    blocker,
    category,
):
    run = plan_external_target_proposal(
        _context(),
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        ReplayExternalTargetProposalProvider(outputs=[raw_output]),
        run_id="target_plan_nonrepairable",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert run.state is ExternalTargetProposalState.BLOCKED
    assert run.blocker == blocker
    assert run.diagnostic.category is category
    assert run.diagnostic.repairable is False
    assert len(run.attempts) == 1


def test_missing_field_has_safe_repairable_diagnostic(replay_profile):
    actions = _valid_actions()
    del actions[0]["expected_roles"]

    run = plan_external_target_proposal(
        _context(),
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        ReplayExternalTargetProposalProvider(outputs=[_payload(actions)]),
        run_id="target_plan_missing_field",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert run.state is ExternalTargetProposalState.AWAITING_REPAIR
    assert run.blocker == "invalid_target_contract"
    assert run.diagnostic.category is ExternalTargetDiagnosticCategory.SCHEMA
    assert run.diagnostic.path == "actions[0].expected_roles"
    assert run.diagnostic.rule_code == "required_field"
    assert run.diagnostic.repairable is True


def test_unallowlisted_validation_rule_is_not_repairable(replay_profile):
    actions = _valid_actions()
    actions[0]["name"] = "x" * 161

    run = plan_external_target_proposal(
        _context(),
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        ReplayExternalTargetProposalProvider(outputs=[_payload(actions)]),
        run_id="target_plan_unknown_rule",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert run.state is ExternalTargetProposalState.BLOCKED
    assert run.blocker == "invalid_target_contract"
    assert run.diagnostic.category is ExternalTargetDiagnosticCategory.SCHEMA
    assert run.diagnostic.rule_code == "unsupported_validation_rule"
    assert run.diagnostic.repairable is False


def test_one_repair_turn_can_reach_human_review(replay_profile):
    context = _context()
    invalid_actions = _valid_actions()
    del invalid_actions[0]["expected_roles"]
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(invalid_actions), _payload(_valid_actions())]
    )
    initial_prompt = render_external_target_prompt(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
    )
    planning = begin_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        run_id="target_plan_repaired",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    repaired = repair_external_target_proposal(
        planning,
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert provider.prompts[0] == initial_prompt
    assert provider.call_count == 2
    assert repaired.run.state is ExternalTargetProposalState.READY_FOR_REVIEW
    assert repaired.run.repair_authorized is True
    assert [attempt.phase for attempt in repaired.run.attempts] == [
        "initial",
        "repair",
    ]
    assert [attempt.valid for attempt in repaired.run.attempts] == [False, True]
    assert repaired.run.diagnostic is None


def test_repair_rejects_a_different_provider_instance(replay_profile):
    context = _context()
    invalid_actions = _valid_actions()
    del invalid_actions[0]["expected_roles"]
    original_provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(invalid_actions)]
    )
    replacement_provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(_valid_actions())]
    )
    planning = begin_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        original_provider,
        run_id="target_plan_same_provider",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    with pytest.raises(ValueError, match="original provider instance"):
        repair_external_target_proposal(
            planning,
            context,
            "Find hammer products and show cheapest suitable results first.",
            replay_profile,
            replacement_provider,
            started_at=NOW,
            completed_at_fn=lambda: NOW,
        )

    assert original_provider.call_count == 1
    assert replacement_provider.call_count == 0


def test_second_invalid_output_exhausts_repair_budget(replay_profile):
    context = _context()
    first = _valid_actions()
    del first[0]["expected_roles"]
    second = _valid_actions()
    second[-1]["action_kind"] = "click"
    second[-1]["expected_roles"] = ["button"]
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(first), _payload(second), _payload(_valid_actions())]
    )
    planning = begin_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        run_id="target_plan_exhausted",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )
    repaired = repair_external_target_proposal(
        planning,
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )

    assert repaired.run.state is ExternalTargetProposalState.BLOCKED
    assert repaired.run.blocker == "invalid_final_read"
    assert len(repaired.run.attempts) == 2
    assert repaired.run.repair_authorized is True
    assert provider.call_count == 2
    with pytest.raises(ValueError, match="not awaiting repair"):
        repair_external_target_proposal(
            repaired,
            context,
            "Find hammer products and show cheapest suitable results first.",
            replay_profile,
            provider,
            started_at=NOW,
            completed_at_fn=lambda: NOW,
        )
    assert provider.call_count == 2


def test_persisted_attempts_exclude_raw_invalid_and_repaired_content(
    tmp_path,
    replay_profile,
):
    context = _context()
    first = _valid_actions()
    del first[0]["expected_roles"]
    initial_raw = _payload(first)
    repaired_raw = _payload(_valid_actions())
    provider = ReplayExternalTargetProposalProvider(
        outputs=[initial_raw, repaired_raw]
    )
    planning = begin_external_target_proposal(
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        run_id="target_plan_private_repair",
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )
    repaired = repair_external_target_proposal(
        planning,
        context,
        "Find hammer products and show cheapest suitable results first.",
        replay_profile,
        provider,
        started_at=NOW,
        completed_at_fn=lambda: NOW,
    )
    path = tmp_path / "repair-proposal.json"
    save_external_target_proposal_run(repaired.run, path)
    saved = path.read_text(encoding="utf-8")

    assert len(repaired.run.attempts) == 2
    assert initial_raw not in saved
    assert repaired_raw not in saved
    assert all(prompt not in saved for prompt in provider.prompts)
    assert "invalid_proposal" not in saved
    assert saved.count('"raw_response_persisted": false') == 3


def _runner_values(*extra):
    return iter(
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
            *extra,
        )
    )


def test_runner_requires_explicit_retry_before_repaired_human_review(
    tmp_path,
    interactive_profile,
):
    first = _valid_actions()
    del first[0]["expected_roles"]
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(first), _payload(_valid_actions())]
    )
    values = _runner_values("retry", "")
    browser_plans = []

    def browser_opener(plan, *args, **kwargs):
        browser_plans.append(plan)
        raise RuntimeError("repaired discovery-plan boundary reached")

    output = tmp_path / "repaired-target-run"
    with pytest.raises(RuntimeError, match="repaired discovery-plan boundary"):
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
    assert provider.call_count == 2
    assert proposal["state"] == "accepted"
    assert proposal["repair_authorized"] is True
    assert [attempt["phase"] for attempt in proposal["attempts"]] == [
        "initial",
        "repair",
    ]
    assert len(browser_plans) == 1


def test_runner_quit_pauses_before_repair_provider_call(
    tmp_path,
    interactive_profile,
):
    first = _valid_actions()
    del first[0]["expected_roles"]
    provider = ReplayExternalTargetProposalProvider(
        outputs=[_payload(first), _payload(_valid_actions())]
    )
    values = _runner_values("quit")
    browser_calls = []

    def browser_opener(*args, **kwargs):
        browser_calls.append((args, kwargs))
        raise AssertionError("browser must not start after repair quit")

    output = tmp_path / "repair-quit-run"
    with pytest.raises(InteractiveFlowStopped, match="paused.*repair"):
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
    assert session.state is InteractiveSessionState.PAUSED
    assert proposal["state"] == "awaiting_repair"
    assert proposal["repair_authorized"] is False
    assert provider.call_count == 1
    assert browser_calls == []
