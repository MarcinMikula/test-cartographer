"""Export committed JSON Schemas for Sprint 13 contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.proactive_regression.models import (
    FrontendChangeReport,
    ObservationInventory,
    ProactiveRegressionProfile,
    ProactiveRegressionRun,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = {
    "observation-inventory-v0.1.schema.json": ObservationInventory,
    "proactive-regression-profile-v0.1.schema.json": ProactiveRegressionProfile,
    "frontend-change-report-v0.1.schema.json": FrontendChangeReport,
    "proactive-regression-run-v0.1.schema.json": ProactiveRegressionRun,
}


def main() -> int:
    schema_dir = ROOT / "schemas"
    schema_dir.mkdir(parents=True, exist_ok=True)
    for filename, model in OUTPUTS.items():
        path = schema_dir / filename
        payload = json.dumps(
            model.model_json_schema(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        path.write_text(payload + "\n", encoding="utf-8", newline="\n")
        print(f"Exported {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
