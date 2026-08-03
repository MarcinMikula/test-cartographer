from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from test_cartographer.execution.assessment import assess_execution_evidence
from test_cartographer.execution.io import load_execution_bundle

ROOT = Path(__file__).resolve().parents[2]


def test_framework_side_reference_collector_emits_bounded_actionable_bundle(tmp_path):
    output = tmp_path / "execution-evidence-bundle.json"
    env = os.environ.copy()
    env.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTHONPATH=str(ROOT / "testdata/execution/framework_plugin"),
        TEST_CARTOGRAPHER_SECRET="super-secret-123",
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            str(ROOT / "testdata/execution/framework_suite"),
            "-p",
            "execution_evidence_plugin",
            "--execution-evidence-profile",
            str(ROOT / "testdata/execution/profile/strict_internal.json"),
            "--execution-evidence-output",
            str(output),
            "--execution-run-id",
            "run_reference_execution",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    bundle = load_execution_bundle(output)
    assert bundle.passed_count == 1
    assert bundle.test_failure_count == 1
    assert bundle.infrastructure_error_count == 1
    assert bundle.cartographer_runtime_required is False
    assessment = assess_execution_evidence(bundle)
    assert assessment.ready_for_reactive_maintenance is True

    rendered = output.read_text(encoding="utf-8")
    assert "super-secret-123" not in rendered
    assert "user:password" not in rendered
    assert "query=Example" not in rendered
    assert "#results" not in rendered
    assert "catalog result mismatch" not in rendered
    assert "browser service unavailable" not in rendered
    assert '"raw_tracebacks_persisted": false' in rendered
    assert '"captured_stdout_persisted": false' in rendered


def test_collection_error_is_infrastructure_evidence_but_not_maintenance_ready(tmp_path):
    output = tmp_path / "collection-evidence-bundle.json"
    env = os.environ.copy()
    env.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTHONPATH=str(ROOT / "testdata/execution/framework_plugin"),
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            str(ROOT / "testdata/execution/collection_suite"),
            "-p",
            "execution_evidence_plugin",
            "--execution-evidence-profile",
            str(ROOT / "testdata/execution/profile/strict_internal.json"),
            "--execution-evidence-output",
            str(output),
            "--execution-run-id",
            "run_collection_error",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    bundle = load_execution_bundle(output)
    assert bundle.infrastructure_error_count == 1
    record = bundle.records[0]
    assert record.failure is not None
    assert record.failure.phase.value == "collection"
    assert assess_execution_evidence(bundle).ready_for_reactive_maintenance is False
