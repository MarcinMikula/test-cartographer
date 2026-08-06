import subprocess
import sys


def test_python_m_exposes_regression_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "test_cartographer.cli", "regression", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "bounded proactive frontend/context regression" in result.stdout
