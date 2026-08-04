import pytest

from test_cartographer.guided_intake.parser import GuidanceParseError, parse_guided_plan


def test_parser_rejects_markdown_fences() -> None:
    with pytest.raises(GuidanceParseError, match="Markdown"):
        parse_guided_plan("```json\n{}\n```")


def test_parser_rejects_duplicate_keys() -> None:
    raw = '{"schema_version":"0.1","schema_version":"0.1","phase":"collection","questions":[]}'
    with pytest.raises(GuidanceParseError) as exc:
        parse_guided_plan(raw)
    assert exc.value.code == "duplicate_key"
