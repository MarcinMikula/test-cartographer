"""Export framework execution-evidence JSON Schemas."""

from pathlib import Path

from test_cartographer.execution.io import (
    export_execution_bundle_schema,
    export_execution_profile_schema,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    targets = (
        (
            export_execution_profile_schema,
            ROOT / "schemas/execution-evidence-profile-v0.1.schema.json",
        ),
        (
            export_execution_bundle_schema,
            ROOT / "schemas/execution-evidence-bundle-v0.1.schema.json",
        ),
    )
    for exporter, target in targets:
        exporter(target)
        print(f"Exported {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
