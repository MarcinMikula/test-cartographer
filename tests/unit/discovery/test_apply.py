import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.readiness import assess_readiness
from test_cartographer.discovery.apply import apply_accepted_discovery
from test_cartographer.discovery.engine import phrase_ambiguity, resolve_ambiguity, review_discovery
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryRunState
from test_cartographer.discovery.models import DiscoveryAmbiguity, ProcessDiscoveryRun
from test_cartographer.discovery.provider import ReplayDiscoveryProvider
from test_cartographer.discovery.ranking import rank_targets
from test_cartographer.intake.io import load_session

ROOT = Path(__file__).resolve().parents[3]


def _accepted_run(plan, candidates, profile):
    now = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
    run = ProcessDiscoveryRun(
        id="discovery_apply_run",
        profile_id=profile.id,
        plan_id=plan.id,
        context_id=plan.context_id,
        source_url=plan.source_url,
        captured_at=now,
        updated_at=now,
        state=DiscoveryRunState.AWAITING_RESOLUTION,
        candidates=candidates,
        targets=rank_targets(plan.targets, candidates, profile),
        ambiguities=(
            DiscoveryAmbiguity(
                id="amb_target_search_submit",
                target_id="target_search_submit",
                candidate_ids=("cand_002", "cand_003"),
            ),
        ),
        capture_sha256="b" * 64,
    )
    raw = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": "amb_target_search_submit",
            "candidate_ids": ["cand_002", "cand_003"],
            "user_prompt": "Which Search button submits the catalog form?",
            "reason": "Two equal candidates require human confirmation.",
        }
    )
    _, run = phrase_ambiguity(
        run,
        plan.targets,
        profile,
        ReplayDiscoveryProvider([raw]),
        ambiguity_id="amb_target_search_submit",
        started_at=now,
        completed_at=now + timedelta(seconds=1),
    )
    run = resolve_ambiguity(
        run,
        ambiguity_id="amb_target_search_submit",
        selected_candidate_id="cand_002",
        resolved_at=now + timedelta(seconds=2),
        reason="Human selected the submit control.",
    )
    return review_discovery(
        run,
        decision=DiscoveryDecision.ACCEPTED,
        reviewed_at=now + timedelta(seconds=3),
        reason="Reviewed.",
    )


def test_apply_replaces_placeholder_with_process_graph(plan, candidates, profile) -> None:
    context = load_session(
        ROOT / "testdata/guided_intake/session/replay_complete.json"
    ).context
    updated = apply_accepted_discovery(context, plan, _accepted_run(plan, candidates, profile))

    assert [page.id for page in updated.pages] == ["page_catalog"]
    assert [component.id for component in updated.components] == ["comp_catalog_search"]
    assert {element.id for element in updated.elements} == {
        "el_search_query",
        "el_search_submit",
        "el_search_results",
    }
    assert len(updated.process.steps) == 4
    assert updated.test_data[0].symbolic_ref == "catalog_query"
    assert assess_readiness(updated).ready is True


def test_selected_submit_uses_unique_test_id_as_primary(plan, candidates, profile) -> None:
    context = load_session(
        ROOT / "testdata/guided_intake/session/replay_complete.json"
    ).context
    updated = apply_accepted_discovery(context, plan, _accepted_run(plan, candidates, profile))
    submit = next(item for item in updated.elements if item.id == "el_search_submit")
    primary = next(item for item in submit.locator_candidates if item.primary)
    assert primary.strategy.value == "test_id"
    assert primary.value.value == "search-submit"
    assert primary.value.status.value == "observed"
