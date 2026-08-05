"""Verify the reactive-maintenance engine without claiming real operator acceptance."""

from __future__ import annotations

import argparse
from pathlib import Path

from test_cartographer.reactive_maintenance.runner import run_scripted_maintenance_mechanics

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".test-cartographer/sprint-12/replay")
    parser.add_argument("--executable-path")
    args = parser.parse_args()
    run_scripted_maintenance_mechanics(
        maintenance_profile_path=ROOT / "testdata/maintenance/profile/reactive_catalog.json",
        execution_profile_path=ROOT / "testdata/maintenance/evidence/strict_internal.json",
        workspace_profile_path=ROOT / "testdata/maintenance/workspace/qa_automation_framework.json",
        framework_root=ROOT / "testdata/maintenance/framework",
        application_root=ROOT / "testdata/maintenance/browser",
        output_dir=args.output_dir,
        executable_path=args.executable_path,
    )
    print("Reactive-maintenance mechanics: verified.")
    print("One real framework test failed before repair and passed after sandbox repair.")
    print("Infrastructure error was excluded before re-observation.")
    print("Failed test was not classified as an application bug.")
    print("Changed locator candidate was discovered from the current page.")
    print("Original framework remained unchanged.")
    print("No live LLM was used.")
    print("Scripted verifier is not the real-operator acceptance artefact.")


if __name__ == "__main__":
    main()
