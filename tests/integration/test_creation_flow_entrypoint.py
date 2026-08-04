import os
import subprocess
import sys

from test_cartographer.creation_flow.io import save_creation_flow_run


def test_creation_status_through_python_m(tmp_path, passed_creation_run) -> None:
    target = tmp_path / "run.json"
    save_creation_flow_run(passed_creation_run, target)
    env = os.environ.copy()
    source = str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src")
    env["PYTHONPATH"] = source + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "test_cartographer.cli", "creation", "status", "--run", str(target)],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Creation flow: creation_flow_test" in result.stdout
