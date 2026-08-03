from pathlib import Path

from test_cartographer.execution.sanitization import (
    bounded_redacted_digest,
    redact_text,
    relative_path_or_none,
    sanitize_application_url,
)


def test_url_minimization_removes_credentials_query_and_fragment():
    location = sanitize_application_url(
        "https://user:password@example.test:8443/catalog?q=Example#results"
    )
    assert location.origin == "https://example.test:8443"
    assert location.path == "/catalog"
    assert location.credentials_persisted is False
    assert location.query_persisted is False
    assert location.fragment_persisted is False


def test_redaction_removes_runtime_secret_and_named_secret_assignment():
    rendered, count = redact_text(
        "token=abc123 password=my-pass runtime=super-secret",
        ("super-secret",),
    )
    assert "abc123" not in rendered
    assert "my-pass" not in rendered
    assert "super-secret" not in rendered
    assert count == 3


def test_bounded_digest_is_stable_after_redaction():
    first = bounded_redacted_digest(
        "authorization=BearerSecret and more text",
        max_characters=20,
    )
    second = bounded_redacted_digest(
        "authorization=BearerSecret and more text",
        max_characters=20,
    )
    assert first == second
    assert first[1] == 1
    assert first[2] is True


def test_relative_path_never_persists_absolute_path(tmp_path):
    root = tmp_path / "repo"
    target = root / "tests" / "test_sample.py"
    target.parent.mkdir(parents=True)
    target.write_text("pass\n", encoding="utf-8")
    assert relative_path_or_none(target, root) == "tests/test_sample.py"
    assert relative_path_or_none(Path(tmp_path).parent / "outside.py", root) is None
