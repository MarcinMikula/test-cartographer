from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.context.enums import LocatorStrategy
from test_cartographer.reactive_maintenance.enums import (
    MaintenanceDecision,
    MaintenanceStatus,
)
from test_cartographer.reactive_maintenance.models import MaintenanceCandidate
from test_cartographer.reactive_maintenance.runner import (
    build_maintenance_diagnosis,
    build_maintenance_patch,
)


def test_build_patch_replaces_exactly_one_stale_locator(
    failure_bundle, maintenance_profile, tmp_path: Path
) -> None:
    framework = tmp_path / "framework"
    target = framework / "components/catalog_search_form.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "class CatalogSearchForm:\n"
        "    @property\n"
        "    def search_submit(self):\n"
        "        return self.page.get_by_test_id('search-submit')\n",
        encoding="utf-8",
    )
    candidate = MaintenanceCandidate(
        id="cand_002",
        semantic_role="button",
        semantic_name="Search",
        locator_strategy=LocatorStrategy.TEST_ID,
        locator_value="catalog-search-submit",
        match_count=1,
        enabled=True,
        source_record_id=failure_bundle.records[0].id,
        old_locator_absent=True,
        deterministic_match=True,
    )
    diagnosis = build_maintenance_diagnosis(
        maintenance_profile,
        failure_bundle,
        candidate,
        candidate_count=2,
        diagnosis_id="diagnosis_test",
    )
    patch = build_maintenance_patch(
        framework,
        maintenance_profile,
        diagnosis,
        patch_id="maintenance_patch_test",
    )
    assert "catalog-search-submit" in patch.full_source
    assert "get_by_test_id('search-submit')" not in patch.full_source
    assert patch.status is MaintenanceStatus.PENDING
    assert patch.decision is MaintenanceDecision.PENDING


def test_expected_failure_validation_uses_evidence_not_exact_windows_exit_code(
    failure_bundle,
) -> None:
    import subprocess

    from test_cartographer.reactive_maintenance.runner import (
        _require_expected_test_failure,
    )

    result = subprocess.CompletedProcess(
        args=("python", "-m", "pytest"),
        returncode=7,
        stdout="one failed",
        stderr="",
    )
    _require_expected_test_failure(result, failure_bundle, label="reference failure")


def test_expected_failure_validation_reports_semantic_counts_on_zero_exit(
    failure_bundle,
) -> None:
    import subprocess

    import pytest

    from test_cartographer.reactive_maintenance.runner import (
        _require_expected_test_failure,
    )

    result = subprocess.CompletedProcess(
        args=("python", "-m", "pytest"),
        returncode=0,
        stdout="unexpected pass wrapper",
        stderr="",
    )
    with pytest.raises(RuntimeError) as exc_info:
        _require_expected_test_failure(result, failure_bundle, label="reference failure")

    message = str(exc_info.value)
    assert "exit=0" in message
    assert "passed=0" in message
    assert "test_failures=1" in message
    assert "infrastructure_errors=0" in message


def test_collect_framework_evidence_selects_framework_pytest_config(
    tmp_path: Path, monkeypatch
) -> None:
    import json
    import subprocess

    from test_cartographer.reactive_maintenance.runner import collect_framework_evidence

    framework = tmp_path / "framework"
    (framework / "tests/e2e").mkdir(parents=True)
    (framework / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    e2e: reference marker\n",
        encoding="utf-8",
    )
    (framework / "tests/e2e/test_search_catalog.py").write_text(
        "def test_placeholder():\n    pass\n",
        encoding="utf-8",
    )
    execution_profile = tmp_path / "profile.json"
    execution_profile.write_text("{}", encoding="utf-8")
    output = tmp_path / "bundle.json"

    captured: dict[str, object] = {}

    def fake_run(args, **kwargs):
        captured["args"] = list(args)
        captured["cwd"] = kwargs["cwd"]
        output.write_text(
            json.dumps(
                {
                    "schema_version": "0.1",
                    "id": "bundle_test",
                    "run_id": "run_test",
                    "profile_id": "profile_test",
                    "created_at": "2026-08-05T18:00:00Z",
                    "records": [],
                    "passed_count": 0,
                    "test_failure_count": 0,
                    "infrastructure_error_count": 0,
                    "truncated": False,
                    "framework_execution_independent": True,
                    "cartographer_runtime_required": False,
                    "raw_artifacts_persisted": False,
                    "live_llm_used": False
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        "test_cartographer.reactive_maintenance.runner.load_execution_bundle",
        lambda path: object(),
    )

    collect_framework_evidence(
        framework,
        application_url="http://127.0.0.1:9000/catalog",
        execution_profile_path=execution_profile,
        output_path=output,
        run_id="run_test",
    )

    args = captured["args"]
    assert args[args.index("-c") + 1] == str((framework / "pytest.ini").resolve())
    assert args[args.index("--rootdir") + 1] == str(framework.resolve())
    assert captured["cwd"] == framework.resolve()
