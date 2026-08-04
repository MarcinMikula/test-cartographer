"""Export JSON Schemas for guided-intake contracts version 0.1."""

from test_cartographer.guided_intake.io import export_guided_schemas


def main() -> None:
    export_guided_schemas("schemas")
    for name in (
        "minimal-context-seed-v0.1.schema.json",
        "guided-intake-profile-v0.1.schema.json",
        "guided-intake-run-v0.1.schema.json",
    ):
        print(f"Exported schemas/{name}")


if __name__ == "__main__":
    main()
