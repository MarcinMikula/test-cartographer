from pathlib import Path
import os
import subprocess
import sys

from test_cartographer.cli import main

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "testdata/execution/bundle/reference_outcomes.json"


def _module_environment() -> dict[str, str]:
    environment = os.environ.copy()
    source_root = str(ROOT / "src")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        source_root if not existing else os.pathsep.join((source_root, existing))
    )
    return environment


def test_evidence_status_reports_three_outcomes(capsys):
    assert main(["evidence", "status", "--bundle", str(BUNDLE)]) == 0
    output = capsys.readouterr().out
    assert "Passed: 1" in output
    assert "Test failures: 1" in output
    assert "Infrastructure errors: 1" in output
    assert "Raw artifacts persisted: false" in output


def test_evidence_assess_reports_reactive_maintenance_readiness(capsys):
    assert main(["evidence", "assess", "--bundle", str(BUNDLE)]) == 0
    output = capsys.readouterr().out
    assert "Actionable failures: 2" in output
    assert "Issues: none" in output
    assert "Ready for reactive maintenance: true" in output


def test_evidence_status_module_entrypoint_reports_three_outcomes():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "test_cartographer.cli",
            "evidence",
            "status",
            "--bundle",
            str(BUNDLE),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_module_environment(),
    )

    assert result.returncode == 0, result.stderr
    assert "Passed: 1" in result.stdout
    assert "Test failures: 1" in result.stdout
    assert "Infrastructure errors: 1" in result.stdout


def test_evidence_assess_module_entrypoint_reports_readiness():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "test_cartographer.cli",
            "evidence",
            "assess",
            "--bundle",
            str(BUNDLE),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env=_module_environment(),
    )

    assert result.returncode == 0, result.stderr
    assert "Actionable failures: 2" in result.stdout
    assert "Ready for reactive maintenance: true" in result.stdout
