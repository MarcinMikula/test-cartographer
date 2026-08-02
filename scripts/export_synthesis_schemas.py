"""Export bounded synthesis JSON Schemas version 0.1."""

from pathlib import Path

from test_cartographer.synthesis.io import (
    export_proposal_schema,
    export_request_schema,
    export_run_schema,
)


if __name__ == "__main__":
    targets = (
        (export_request_schema, Path("schemas/synthesis-request-v0.1.schema.json")),
        (export_proposal_schema, Path("schemas/pom-proposal-v0.1.schema.json")),
        (export_run_schema, Path("schemas/synthesis-run-v0.1.schema.json")),
    )
    for exporter, target in targets:
        exporter(target)
        print(f"Exported {target}")
