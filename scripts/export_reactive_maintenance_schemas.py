"""Export deterministic JSON Schemas for Sprint 12 contracts."""

from pathlib import Path

from test_cartographer.reactive_maintenance.io import export_reactive_maintenance_schemas

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for path in export_reactive_maintenance_schemas(ROOT / "schemas"):
        print(f"Exported {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
