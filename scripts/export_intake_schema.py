"""Export the committed JSON Schema for intake session contract version 0.1."""

import json
from pathlib import Path

from test_cartographer.intake.models import IntakeSession


def main() -> None:
    target = Path("schemas/intake-session-v0.1.schema.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        IntakeSession.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
    print(f"Exported {target}")


if __name__ == "__main__":
    main()
