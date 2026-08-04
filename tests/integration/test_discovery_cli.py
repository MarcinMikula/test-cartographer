from datetime import datetime, timezone

from test_cartographer.cli import main
from test_cartographer.discovery.enums import DiscoveryRunState
from test_cartographer.discovery.io import save_discovery_run
from test_cartographer.discovery.models import DiscoveryAmbiguity, ProcessDiscoveryRun
from test_cartographer.discovery.ranking import rank_targets


def _run(plan, candidates, profile):
    now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
    return ProcessDiscoveryRun(
        id="discovery_cli_run",
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
        capture_sha256="d" * 64,
    )


def test_discovery_status_and_assess_commands(tmp_path, capsys, plan, candidates, profile) -> None:
    path = tmp_path / "run.json"
    save_discovery_run(_run(plan, candidates, profile), path)
    assert main(["discover", "status", "--run", str(path)]) == 0
    status = capsys.readouterr().out
    assert "Candidates: 4" in status
    assert "Unresolved ambiguities: 1" in status
    assert main(["discover", "assess", "--run", str(path)]) == 0
    assessment = capsys.readouterr().out
    assert "Ready for context application: false" in assessment
