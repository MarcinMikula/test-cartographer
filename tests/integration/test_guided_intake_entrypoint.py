import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_python_m_entrypoint_creates_minimal_guided_session(tmp_path: Path) -> None:
    env = os.environ.copy()
    source = str(ROOT / "src")
    env["PYTHONPATH"] = (
        source
        if not env.get("PYTHONPATH")
        else source + os.pathsep + env["PYTHONPATH"]
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "test_cartographer.cli",
            "intake",
            "seed",
            "--seed",
            str(ROOT / "testdata/guided_intake/seed/product_search.json"),
            "--context",
            str(tmp_path / "context.json"),
            "--session",
            str(tmp_path / "session.json"),
            "--session-id",
            "intake_subprocess_guided",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Human-intake blockers: 9" in result.stdout


def test_python_m_entrypoint_shows_guided_readiness() -> None:
    env = os.environ.copy()
    source = str(ROOT / "src")
    env["PYTHONPATH"] = (
        source
        if not env.get("PYTHONPATH")
        else source + os.pathsep + env["PYTHONPATH"]
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "test_cartographer.cli",
            "intake",
            "guide-status",
            "--session",
            str(ROOT / "testdata/guided_intake/session/replay_complete.json"),
            "--run",
            str(ROOT / "testdata/guided_intake/run/replay_complete.json"),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Ready for guided discovery: true" in result.stdout
