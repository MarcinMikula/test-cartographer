from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import ActionKind
from test_cartographer.discovery.enums import DiscoveryProviderKind
from test_cartographer.discovery.models import DiscoveryProfile, DiscoveryTarget, ProcessDiscoveryPlan


def test_ollama_profile_requires_loopback() -> None:
    with pytest.raises(ValidationError, match="loopback"):
        DiscoveryProfile(
            id="discovery_cloud",
            provider=DiscoveryProviderKind.OLLAMA,
            model="qwen2.5-coder:7b",
            base_url="http://example.com:11434",
        )


def test_fill_target_requires_symbolic_test_data() -> None:
    with pytest.raises(ValidationError, match="symbolic test data"):
        DiscoveryTarget(
            id="target_query",
            element_id="el_query",
            owner_id="page_catalog",
            name="Query",
            action_kind=ActionKind.FILL,
            expected_roles=("textbox",),
        )


def test_plan_rejects_unknown_owner(plan: ProcessDiscoveryPlan) -> None:
    payload = plan.model_dump(mode="python")
    payload["targets"][0]["owner_id"] = "comp_missing"
    with pytest.raises(ValidationError, match="not declared"):
        ProcessDiscoveryPlan.model_validate(payload)


def test_plan_rejects_query_data(plan: ProcessDiscoveryPlan) -> None:
    with pytest.raises(ValidationError, match="query"):
        ProcessDiscoveryPlan.model_validate(
            {**plan.model_dump(mode="python"), "source_url": "http://127.0.0.1/page?q=secret"}
        )


def test_accepted_run_requires_every_target_selected(plan, candidates, profile) -> None:
    from datetime import datetime, timezone
    from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryRunState
    from test_cartographer.discovery.models import ProcessDiscoveryRun
    from test_cartographer.discovery.ranking import rank_targets

    now = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="every target selected"):
        ProcessDiscoveryRun(
            id="discovery_invalid_accept",
            profile_id=profile.id,
            plan_id=plan.id,
            context_id=plan.context_id,
            source_url=plan.source_url,
            captured_at=now,
            updated_at=now,
            state=DiscoveryRunState.ACCEPTED,
            candidates=candidates,
            targets=rank_targets(plan.targets, candidates, profile),
            ambiguities=(),
            capture_sha256="f" * 64,
            decision=DiscoveryDecision.ACCEPTED,
            reviewed_at=now,
        )

def test_run_allows_single_target_discovery(plan, candidates, profile) -> None:
    from test_cartographer.discovery.enums import DiscoveryRunState
    from test_cartographer.discovery.models import ProcessDiscoveryRun
    from test_cartographer.discovery.ranking import rank_targets

    payload = plan.model_dump(mode="python")
    payload["targets"] = (payload["targets"][0],)
    single_target_plan = ProcessDiscoveryPlan.model_validate(payload)
    ranked = rank_targets(single_target_plan.targets, candidates, profile)
    assert len(ranked) == 1

    now = datetime(2026, 8, 12, 16, 30, tzinfo=timezone.utc)
    run = ProcessDiscoveryRun(
        id="discovery_single_target",
        profile_id=profile.id,
        plan_id=single_target_plan.id,
        context_id=single_target_plan.context_id,
        source_url=single_target_plan.source_url,
        captured_at=now,
        updated_at=now,
        state=DiscoveryRunState.RESOLVED,
        candidates=candidates,
        targets=ranked,
        capture_sha256="a" * 64,
    )

    assert len(run.targets) == 1
    assert run.targets[0].target_id == single_target_plan.targets[0].id
