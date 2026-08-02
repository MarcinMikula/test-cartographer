import json

from test_cartographer.adaptation.models import AdaptationPlan, FrameworkSnapshot, WorkspaceProfile


def test_committed_adaptation_schemas_match_models(repository_root):
    pairs = [
        (WorkspaceProfile, "workspace-profile-v0.1.schema.json"),
        (FrameworkSnapshot, "framework-snapshot-v0.1.schema.json"),
        (AdaptationPlan, "adaptation-plan-v0.1.schema.json"),
    ]
    for model, filename in pairs:
        committed = json.loads((repository_root / "schemas" / filename).read_text(encoding="utf-8"))
        assert committed == model.model_json_schema()
