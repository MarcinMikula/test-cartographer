"""JSON persistence for human-triggered Creation Flow audit artefacts."""

from pathlib import Path

from test_cartographer.interactive_creation.models import (
    ExactPatchRereviewReport,
    InteractiveCreationProfile,
    InteractiveOperatorSession,
)


def load_interactive_profile(path: str | Path) -> InteractiveCreationProfile:
    return InteractiveCreationProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_interactive_profile(profile: InteractiveCreationProfile, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(profile.model_dump_json(indent=2), encoding="utf-8", newline="\n")


def load_operator_session(path: str | Path) -> InteractiveOperatorSession:
    return InteractiveOperatorSession.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_operator_session(session: InteractiveOperatorSession, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(session.model_dump_json(indent=2), encoding="utf-8", newline="\n")


def load_patch_rereview_report(path: str | Path) -> ExactPatchRereviewReport:
    return ExactPatchRereviewReport.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )


def save_patch_rereview_report(
    report: ExactPatchRereviewReport, path: str | Path
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report.model_dump_json(indent=2), encoding="utf-8", newline="\n")
