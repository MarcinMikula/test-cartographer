"""Export Sprint 9 discovery schemas."""

from pathlib import Path

from test_cartographer.discovery.io import export_json_schemas


if __name__ == "__main__":
    target = Path("schemas")
    export_json_schemas(target)
    for name in (
        "discovery-profile-v0.1.schema.json",
        "process-discovery-plan-v0.1.schema.json",
        "process-discovery-run-v0.1.schema.json",
    ):
        print(f"Exported {target / name}")
