"""Verify the complete Sprint 5 read-only framework adaptation boundary."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationReviewDecision
from test_cartographer.adaptation.io import load_workspace_profile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.synthesis.io import load_synthesis_run

ROOT = Path(__file__).resolve().parents[1]


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    profile = load_workspace_profile(
        ROOT / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    run = load_synthesis_run(
        ROOT / "testdata/synthesis/run/accepted_public_search.json"
    )

    with tempfile.TemporaryDirectory() as temporary:
        framework = Path(temporary) / "qa-automation-framework"
        shutil.copytree(ROOT / "testdata/framework/reference", framework)
        before = _tree_hash(framework)

        snapshot = inspect_framework(
            framework,
            profile,
            snapshot_id="snapshot_verify_reference",
            captured_at=datetime(2026, 8, 2, 13, 0, tzinfo=timezone.utc),
        )
        plan = build_adaptation_plan(
            run,
            profile,
            snapshot,
            plan_id="adapt_verify_public_search",
            created_at=datetime(2026, 8, 2, 13, 1, tzinfo=timezone.utc),
        )
        accepted = review_adaptation_plan(
            plan,
            decision=AdaptationReviewDecision.ACCEPTED,
            reviewed_at=datetime(2026, 8, 2, 13, 2, tzinfo=timezone.utc),
            reason="Reference targets match the controlled framework structure.",
            review_seconds=6.0,
        )
        after = _tree_hash(framework)

    assert before == after
    assert snapshot.source_contents_persisted is False
    assert snapshot.absolute_paths_persisted is False
    assert snapshot.secret_values_persisted is False
    assert accepted.framework_files_modified is False
    assert accepted.generated_source_included is False
    assert [item.target_path for item in accepted.operations] == [
        "pages/catalog_page.py",
        "components/catalog_search_form.py",
        "tests/e2e/conftest.py",
        "tests/e2e/test_search_catalog.py",
    ]

    print("Controlled qa-automation-framework workspace inspected read-only.")
    print("Only relative paths, file hashes, sizes, and Python symbols were persisted.")
    print("Accepted POM proposal mapped to exact page, component, fixture, and test targets.")
    print("Human acceptance changed only the adaptation-plan state.")
    print("No generated source code was included and no framework file was modified.")


if __name__ == "__main__":
    main()
