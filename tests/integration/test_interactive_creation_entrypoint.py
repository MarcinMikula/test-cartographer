import os
import subprocess
import sys


def test_python_m_entrypoint_exposes_interactive_creation_help() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [sys.executable, "-m", "test_cartographer.cli", "creation", "interactive", "--help"],
        cwd=".",
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "usage: test-cartographer creation interactive" in result.stdout
    assert "--ollama-model" in result.stdout
    assert "--output-dir" in result.stdout
