"""Export JSON Schemas for Sprint 5 adaptation contracts."""

from test_cartographer.adaptation.io import export_plan_schema, export_profile_schema, export_snapshot_schema


if __name__ == "__main__":
    export_profile_schema("schemas/workspace-profile-v0.1.schema.json")
    export_snapshot_schema("schemas/framework-snapshot-v0.1.schema.json")
    export_plan_schema("schemas/adaptation-plan-v0.1.schema.json")
    print("Exported schemas/workspace-profile-v0.1.schema.json")
    print("Exported schemas/framework-snapshot-v0.1.schema.json")
    print("Exported schemas/adaptation-plan-v0.1.schema.json")
