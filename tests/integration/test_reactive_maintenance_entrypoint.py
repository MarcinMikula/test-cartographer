import os
import subprocess
import sys

from test_cartographer.reactive_maintenance.io import save_maintenance_run


def test_real_module_entrypoint_formats_maintenance_run(
    passed_maintenance_run, tmp_path
) -> None:
    run_path = tmp_path / "maintenance-run.json"
    save_maintenance_run(passed_maintenance_run, run_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "test_cartographer.cli",
            "maintenance",
            "assess",
            "--run",
            str(run_path),
        ],
        cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Reactive maintenance verified: true" in result.stdout
