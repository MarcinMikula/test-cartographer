"""Verify that a framework snapshot exposes the primitives used by Sprint 6 templates."""

from __future__ import annotations

import argparse
from pathlib import Path

from test_cartographer.adaptation.io import load_framework_snapshot
from test_cartographer.delivery.framework_contract import (
    validate_generation_framework_contract,
)
from test_cartographer.delivery.io import load_generation_profile


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--generation-profile", required=True, type=Path)
    args = parser.parse_args()

    snapshot = load_framework_snapshot(args.snapshot)
    profile = load_generation_profile(args.generation_profile)
    validate_generation_framework_contract(snapshot, profile)

    print("Framework generation contract: compatible.")
    for requirement in profile.required_framework_symbols:
        print(
            f"  {requirement.path}::{requirement.symbol_name} "
            f"({requirement.symbol_kind.value})"
        )
    print("No source patch was generated and no framework file was modified.")


if __name__ == "__main__":
    main()
