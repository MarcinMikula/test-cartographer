from datetime import datetime, timezone

from test_cartographer.discovery.assessment import assess_discovery
from test_cartographer.discovery.enums import DiscoveryRunState
from test_cartographer.discovery.models import DiscoveryAmbiguity, ProcessDiscoveryRun
from test_cartographer.discovery.ranking import rank_targets


def test_unresolved_run_is_not_ready(plan, candidates, profile) -> None:
    now = datetime(2026, 8, 4, 10, 0, tzinfo=timezone.utc)
    run = ProcessDiscoveryRun(
        id="discovery_assessment_run",
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
        capture_sha256="c" * 64,
    )
    report = assess_discovery(run)
    assert report.target_count == 3
    assert report.unresolved_ambiguity_count == 1
    assert report.ready_for_context_application is False
