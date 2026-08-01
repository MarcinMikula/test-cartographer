"""Export context contract version 0.1 as JSON Schema."""

from pathlib import Path

from test_cartographer.context.io import export_json_schema


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    target = root / "schemas" / "context-bundle-v0.1.schema.json"
    export_json_schema(target)
    print(f"Exported {target.relative_to(root)}")
