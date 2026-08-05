from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _as_int(value: str | None) -> int:
    return int(value or 0)


def _suite_nodes(root: ET.Element) -> list[ET.Element]:
    tag = root.tag.rsplit("}", 1)[-1]
    if tag == "testsuite":
        return [root]
    direct = [child for child in root if child.tag.rsplit("}", 1)[-1] == "testsuite"]
    if direct:
        return direct
    return [node for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "testsuite"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an exact pytest JUnit result.")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--expected-tests", required=True, type=int)
    parser.add_argument("--expected-skipped", type=int, default=0)
    args = parser.parse_args()

    if not args.report.is_file():
        print(f"Missing JUnit report: {args.report}", file=sys.stderr)
        return 2

    try:
        document = ET.parse(args.report)
    except (ET.ParseError, OSError) as exc:
        print(f"Unable to parse JUnit report: {exc}", file=sys.stderr)
        return 2

    suites = _suite_nodes(document.getroot())
    tests = sum(_as_int(suite.get("tests")) for suite in suites)
    failures = sum(_as_int(suite.get("failures")) for suite in suites)
    errors = sum(_as_int(suite.get("errors")) for suite in suites)
    skipped = sum(_as_int(suite.get("skipped")) for suite in suites)
    passed = tests - failures - errors - skipped

    print(
        "JUnit result: "
        f"tests={tests}; passed={passed}; failures={failures}; "
        f"errors={errors}; skipped={skipped}"
    )

    valid = (
        tests == args.expected_tests
        and passed == args.expected_tests - args.expected_skipped
        and failures == 0
        and errors == 0
        and skipped == args.expected_skipped
    )
    if valid:
        return 0

    print(
        "Expected exact pytest result: "
        f"tests={args.expected_tests}; failures=0; errors=0; "
        f"skipped={args.expected_skipped}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
