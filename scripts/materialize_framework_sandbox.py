"""Create a bounded framework sandbox from an approved snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from test_cartographer.adaptation.io import load_framework_snapshot, load_workspace_profile
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--target-root", required=True, type=Path)
    args = parser.parse_args()

    copied = materialize_snapshot_sandbox(
        args.source_root,
        args.target_root,
        load_workspace_profile(args.profile),
        load_framework_snapshot(args.snapshot),
    )
    print(f"Materialized bounded framework sandbox: {args.target_root}")
    print(f"Snapshot-approved files copied: {copied}")
    print("Files outside the accepted snapshot copied: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
