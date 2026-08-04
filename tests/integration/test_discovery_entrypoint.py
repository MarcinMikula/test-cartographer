import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.discovery.enums import DiscoveryRunState
from test_cartographer.discovery.io import save_discovery_run
from test_cartographer.discovery.models import DiscoveryAmbiguity, ProcessDiscoveryRun
from test_cartographer.discovery.ranking import rank_targets

ROOT = Path(__file__).resolve().parents[2]


def test_python_m_discovery_status(tmp_path, plan, candidates, profile) -> None:
    now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
    run = ProcessDiscoveryRun(
        id="discovery_entry_run",
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
        capture_sha256="e" * 64,
    )
    path = tmp_path / "run.json"
    save_discovery_run(run, path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "test_cartographer.cli", "discover", "status", "--run", str(path)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Discovery run: discovery_entry_run" in result.stdout
