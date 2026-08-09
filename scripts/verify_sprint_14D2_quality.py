from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

generator = (ROOT / "src/test_cartographer/delivery/generation.py").read_text(encoding="utf-8")
runner = (ROOT / "scripts/run_sprint_14_expansion_acceptance.py").read_text(encoding="utf-8")
fixture = (ROOT / "testdata/expansion/framework/tests/e2e/conftest.py").read_text(encoding="utf-8")
integration = (ROOT / "tests/integration/test_expansion_existing_page_delivery.py").read_text(encoding="utf-8")

assert "The visible results do not contain the explicitly supplied search query." not in generator
assert "The visible results do not contain the explicitly supplied expected result." in generator
assert 'value="Alpha Beta Zulu"' in runner
assert '"expected_sort_order": "Alpha Beta Zulu"' in fixture
assert 'value="Alpha Beta Zulu"' in integration
assert 'assert "explicitly supplied search query" not in test_change.content' in integration
assert 'assert "explicitly supplied expected result" in test_change.content' in integration

print("Sprint 14D.2 acceptance-quality policy: verified")
