"""Validation of framework primitives required by source-generation templates."""

from __future__ import annotations

from test_cartographer.adaptation.enums import RepositoryEntryKind
from test_cartographer.adaptation.models import FrameworkSnapshot
from test_cartographer.delivery.models import GenerationProfile


def missing_framework_requirements(
    snapshot: FrameworkSnapshot,
    generation_profile: GenerationProfile,
) -> tuple[str, ...]:
    """Return precise missing file/symbol requirements without reading source text."""

    entries = {entry.path: entry for entry in snapshot.entries}
    missing: list[str] = []
    for requirement in generation_profile.required_framework_symbols:
        entry = entries.get(requirement.path)
        if entry is None or entry.kind is not RepositoryEntryKind.FILE:
            missing.append(
                f"missing file {requirement.path} required for "
                f"{requirement.symbol_kind.value} {requirement.symbol_name}"
            )
            continue
        matching = [
            symbol
            for symbol in entry.python_symbols
            if symbol.name == requirement.symbol_name
            and symbol.kind is requirement.symbol_kind
        ]
        if not matching:
            missing.append(
                f"missing {requirement.symbol_kind.value} {requirement.symbol_name} "
                f"in {requirement.path}"
            )
    return tuple(missing)


def validate_generation_framework_contract(
    snapshot: FrameworkSnapshot,
    generation_profile: GenerationProfile,
) -> None:
    """Block deterministic generation when its declared framework API is absent."""

    missing = missing_framework_requirements(snapshot, generation_profile)
    if missing:
        details = "; ".join(missing)
        raise ValueError(
            "framework snapshot is incompatible with the selected generation profile: "
            f"{details}. Select or update a compatible qa-automation-framework checkout "
            "before reviewing an adaptation plan or source patch"
        )
