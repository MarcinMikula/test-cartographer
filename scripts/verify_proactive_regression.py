"""Scripted mechanics verifier for Sprint 13 (not real-operator acceptance)."""

from __future__ import annotations

import argparse
from pathlib import Path

from test_cartographer.proactive_regression.assessment import (
    assess_proactive_regression_run,
)
from test_cartographer.proactive_regression.runner import (
    run_scripted_proactive_regression,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--executable-path")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    run = run_scripted_proactive_regression(
        inventory_path=root / "testdata/proactive/inventory/public_catalog.json",
        profile_path=root / "testdata/proactive/profile/bounded_public.json",
        framework_root=root / "testdata/proactive/framework",
        application_root=root / "testdata/proactive/browser",
        output_dir=args.output_dir,
        executable_path=args.executable_path,
    )
    report = assess_proactive_regression_run(run)
    if not report.proactive_regression_verified:
        raise RuntimeError(f"scripted proactive regression blockers: {report.blockers}")
    print("Proactive-regression mechanics: verified.")
    print("The same framework test passed on baseline and changed frontend.")
    print("One approved mapped element remained stable.")
    print("One approved mapped but uncovered element exposed locator drift.")
    print("No application bug was claimed and no repair was generated.")
    print("The accepted inventory was reused without bootstrap questions.")
    print("No live LLM or raw-page persistence was used.")
    print("Scripted verifier is not the real-operator acceptance artefact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
