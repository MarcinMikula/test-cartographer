"""Export Sprint 10 creation-flow JSON Schemas."""

from pathlib import Path

from test_cartographer.creation_flow.io import export_json_schemas


if __name__ == "__main__":
    export_json_schemas(Path("schemas"))
    print("Exported schemas/creation-flow-profile-v0.1.schema.json")
    print("Exported schemas/creation-flow-run-v0.1.schema.json")
