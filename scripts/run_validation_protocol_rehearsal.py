import argparse
from pathlib import Path

from test_cartographer.validation.operator_acceptance import (
    run_rehearsal,
    verify_rehearsal,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--repository-root", default=".")
    verify = sub.add_parser("verify")
    verify.add_argument("artifact_root")
    args = parser.parse_args()
    if args.command == "run":
        return run_rehearsal(Path(args.repository_root))
    return verify_rehearsal(Path(args.artifact_root))


if __name__ == "__main__":
    raise SystemExit(main())
