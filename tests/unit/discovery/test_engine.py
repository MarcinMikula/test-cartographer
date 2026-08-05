import json
from datetime import datetime, timedelta, timezone

import pytest

from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryRunState, DiscoveryTargetState, SelectionAuthority
from test_cartographer.discovery.models import DiscoveryAmbiguity, ProcessDiscoveryRun
from test_cartographer.discovery.provider import ReplayDiscoveryProvider
from test_cartographer.discovery.ranking import rank_targets


def _run(plan, candidates, profile):
    targets = rank_targets(plan.targets, candidates, profile)
    ambiguity = DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )
    now = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
    return ProcessDiscoveryRun(
        id="discovery_test_run",
        profile_id=profile.id,
        plan_id=plan.id,
        context_id=plan.context_id,
        source_url=plan.source_url,
        captured_at=now,
        updated_at=now,
        state=DiscoveryRunState.AWAITING_RESOLUTION,
        candidates=candidates,
        targets=targets,
        ambiguities=(ambiguity,),
        capture_sha256="a" * 64,
    )


def test_replay_question_then_human_resolution(plan, candidates, profile) -> None:
    run = _run(plan, candidates, profile)
    now = run.captured_at
    output = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": run.ambiguities[0].id,
            "candidate_ids": list(run.ambiguities[0].candidate_ids),
            "user_prompt": "Which Search button submits the form?",
            "reason": "Two equal candidates require human confirmation.",
        }
    )
    question, run = phrase_ambiguity(
        run,
        plan.targets,
        profile,
        ReplayDiscoveryProvider([output]),
        ambiguity_id=run.ambiguities[0].id,
        started_at=now,
        completed_at=now + timedelta(seconds=1),
    )
    assert "Which Search" in question.user_prompt
    run = resolve_ambiguity(
        run,
        ambiguity_id=run.ambiguities[0].id,
        selected_candidate_id="cand_002",
        resolved_at=now + timedelta(seconds=2),
        reason="Human chose the submit control.",
    )
    target = next(item for item in run.targets if item.target_id == "target_search_submit")
    assert target.state is DiscoveryTargetState.SELECTED
    assert target.selection_authority is SelectionAuthority.HUMAN
    assert run.state is DiscoveryRunState.RESOLVED
    accepted = review_discovery(
        run,
        decision=DiscoveryDecision.ACCEPTED,
        reviewed_at=now + timedelta(seconds=3),
        reason="Reviewed.",
    )
    assert accepted.state is DiscoveryRunState.ACCEPTED


def test_cannot_accept_unresolved_run(plan, candidates, profile) -> None:
    run = _run(plan, candidates, profile)
    with pytest.raises(ValueError, match="fully resolved"):
        review_discovery(
            run,
            decision=DiscoveryDecision.ACCEPTED,
            reviewed_at=run.captured_at + timedelta(seconds=1),
        )


def test_truncated_llm_question_is_deterministically_completed(
    plan, candidates, profile
) -> None:
    run = _run(plan, candidates, profile)
    now = run.captured_at
    output = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": run.ambiguities[0].id,
            "candidate_ids": list(run.ambiguities[0].candidate_ids),
            "user_prompt": "cand_002 has data-testid=search-submit, while",
            "reason": "The tied controls need human confirmation.",
        }
    )
    question, updated = phrase_ambiguity(
        run,
        plan.targets,
        profile,
        ReplayDiscoveryProvider([output]),
        ambiguity_id=run.ambiguities[0].id,
        started_at=now,
        completed_at=now + timedelta(seconds=1),
    )
    assert question.user_prompt.endswith("choose one candidate ID.")
    assert "cand_002 or cand_003" in question.user_prompt
    assert updated.ambiguities[0].question == question.user_prompt
    assert "incomplete" in question.reason
