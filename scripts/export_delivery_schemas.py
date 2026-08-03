"""Export controlled source-delivery JSON Schemas."""

from pathlib import Path

from test_cartographer.delivery.io import (
    export_application_report_schema,
    export_code_patch_schema,
    export_creation_evaluation_schema,
    export_generation_profile_schema,
)


if __name__ == "__main__":
    schema_dir = Path("schemas")
    exports = (
        (export_generation_profile_schema, schema_dir / "generation-profile-v0.1.schema.json"),
        (export_code_patch_schema, schema_dir / "code-patch-v0.1.schema.json"),
        (export_application_report_schema, schema_dir / "patch-application-v0.1.schema.json"),
        (export_creation_evaluation_schema, schema_dir / "creation-evaluation-v0.1.schema.json"),
    )
    for export, target in exports:
        export(target)
        print(f"Exported {target}")
