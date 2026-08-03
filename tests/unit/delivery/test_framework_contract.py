from test_cartographer.adaptation.enums import PythonSymbolKind
from test_cartographer.adaptation.models import FrameworkSnapshot
from test_cartographer.delivery.framework_contract import (
    missing_framework_requirements,
    validate_generation_framework_contract,
)


def _without_entry(snapshot: FrameworkSnapshot, path: str) -> FrameworkSnapshot:
    payload = snapshot.model_dump(mode="json")
    payload["entries"] = [entry for entry in payload["entries"] if entry["path"] != path]
    return FrameworkSnapshot.model_validate(payload)


def test_valid_snapshot_satisfies_declared_generation_contract(
    framework_snapshot,
    generation_profile,
):
    assert missing_framework_requirements(framework_snapshot, generation_profile) == ()
    validate_generation_framework_contract(framework_snapshot, generation_profile)


def test_missing_base_component_file_is_reported_before_source_generation(
    framework_snapshot,
    generation_profile,
):
    snapshot = _without_entry(framework_snapshot, "components/base_component.py")
    missing = missing_framework_requirements(snapshot, generation_profile)
    assert missing == (
        "missing file components/base_component.py required for class BaseComponent",
    )


def test_wrong_symbol_kind_is_reported_before_source_generation(
    framework_snapshot,
    generation_profile,
):
    payload = generation_profile.model_dump(mode="json")
    payload["required_framework_symbols"][0]["symbol_kind"] = PythonSymbolKind.FUNCTION.value
    other = generation_profile.__class__.model_validate(payload)
    missing = missing_framework_requirements(framework_snapshot, other)
    assert missing == (
        "missing function BasePage in pages/base_page.py",
    )
