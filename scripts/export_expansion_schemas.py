
"""Export JSON Schemas for Sprint 14 expansion contracts."""

from test_cartographer.expansion.io import (
    export_assessment_schema,
    export_plan_schema,
    export_request_schema,
    export_run_schema,
)


if __name__ == "__main__":
    export_assessment_schema("schemas/expansion-assessment-v0.1.schema.json")
    export_request_schema("schemas/expansion-request-v0.1.schema.json")
    export_plan_schema("schemas/expansion-plan-v0.1.schema.json")
    export_run_schema("schemas/expansion-run-v0.1.schema.json")
    print("Exported schemas/expansion-assessment-v0.1.schema.json")
    print("Exported schemas/expansion-request-v0.1.schema.json")
    print("Exported schemas/expansion-plan-v0.1.schema.json")
    print("Exported schemas/expansion-run-v0.1.schema.json")
