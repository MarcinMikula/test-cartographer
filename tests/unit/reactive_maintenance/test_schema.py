import json

from test_cartographer.reactive_maintenance.io import export_reactive_maintenance_schemas


def test_reactive_maintenance_schemas_export(tmp_path) -> None:
    paths = export_reactive_maintenance_schemas(tmp_path)
    assert len(paths) == 5
    for path in paths:
        schema = json.loads(path.read_text(encoding="utf-8"))
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
