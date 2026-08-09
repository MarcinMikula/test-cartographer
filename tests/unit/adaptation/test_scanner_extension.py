from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.adaptation.models import PythonSymbol, WorkspaceProfile
from test_cartographer.adaptation.enums import PythonSymbolKind
from test_cartographer.adaptation.scanner import inspect_framework


def test_scanner_distinguishes_methods_from_properties(tmp_path):
    (tmp_path / "pages").mkdir()
    (tmp_path / "README.md").write_text("# root\n", encoding="utf-8")
    (tmp_path / "pages/example.py").write_text(
        "class ExamplePage:\n"
        "    @property\n"
        "    def results(self):\n"
        "        return None\n\n"
        "    def refresh(self):\n"
        "        return None\n",
        encoding="utf-8",
    )
    profile = WorkspaceProfile(
        id="workspace_property_scan",
        repository_label="property scan",
        root_marker_files=("README.md",),
        allowed_roots=("pages",),
    )
    snapshot = inspect_framework(
        tmp_path,
        profile,
        snapshot_id="snapshot_property_scan",
        captured_at=datetime(2026, 8, 9, tzinfo=timezone.utc),
    )
    symbol = next(
        item
        for entry in snapshot.entries
        if entry.path == "pages/example.py"
        for item in entry.python_symbols
        if item.name == "ExamplePage"
    )
    assert symbol.method_names == ("refresh",)
    assert symbol.property_names == ("results",)


def test_python_symbol_rejects_method_property_name_overlap():
    with pytest.raises(ValidationError, match="method/property names overlap"):
        PythonSymbol(
            kind=PythonSymbolKind.CLASS,
            name="ExamplePage",
            method_names=("results",),
            property_names=("results",),
        )
