"""Export browser observation JSON Schema version 0.1."""

from pathlib import Path

from test_cartographer.observation.io import export_json_schema


if __name__ == "__main__":
    target = Path("schemas/observation-v0.1.schema.json")
    export_json_schema(target)
    print(f"Exported {target}")
