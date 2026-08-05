"""Export Sprint 11 human-trigger contracts as JSON Schema."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.interactive_creation.models import (
    ExactPatchRereviewReport,
    InteractiveCreationProfile,
    InteractiveOperatorSession,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    schemas = ROOT / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    values = {
        "interactive-creation-profile-v0.1.schema.json": InteractiveCreationProfile.model_json_schema(),
        "interactive-operator-session-v0.1.schema.json": InteractiveOperatorSession.model_json_schema(),
        "interactive-patch-rereview-v0.1.schema.json": ExactPatchRereviewReport.model_json_schema(),
    }
    for name, schema in values.items():
        target = schemas / name
        target.write_text(
            json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"Exported {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
