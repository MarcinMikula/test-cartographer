import json
from pathlib import Path

from test_cartographer.proactive_regression.models import (
    FrontendChangeReport,
    ObservationInventory,
    ProactiveRegressionProfile,
    ProactiveRegressionRun,
)


def test_committed_proactive_schemas_match_models() -> None:
    root = Path(__file__).resolve().parents[3]
    expected = {
        "observation-inventory-v0.1.schema.json": ObservationInventory,
        "proactive-regression-profile-v0.1.schema.json": ProactiveRegressionProfile,
        "frontend-change-report-v0.1.schema.json": FrontendChangeReport,
        "proactive-regression-run-v0.1.schema.json": ProactiveRegressionRun,
    }
    for filename, model in expected.items():
        committed = json.loads((root / "schemas" / filename).read_text(encoding="utf-8"))
        assert committed == model.model_json_schema()
