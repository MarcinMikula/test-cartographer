"""Deterministic minimization helpers shared by tests and reference tooling."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

from test_cartographer.execution.models import SanitizedApplicationLocation

_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|secret|authorization|api[_-]?key|credential)\b"
    r"\s*[:=]\s*([^\s,;]+)"
)


def sanitize_application_url(url: str) -> SanitizedApplicationLocation:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("application URL must use http or https and contain a host")
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = f":{parsed.port}" if parsed.port is not None else ""
    origin = f"{parsed.scheme}://{host}{port}"
    return SanitizedApplicationLocation(origin=origin, path=parsed.path or "/")


def redact_text(text: str, secret_values: tuple[str, ...] = ()) -> tuple[str, int]:
    rendered = text
    count = 0
    for secret in sorted((value for value in secret_values if value), key=len, reverse=True):
        occurrences = rendered.count(secret)
        if occurrences:
            rendered = rendered.replace(secret, "<redacted>")
            count += occurrences

    def _replace(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}=<redacted>"

    rendered = _SECRET_ASSIGNMENT.sub(_replace, rendered)
    return rendered, count


def bounded_redacted_digest(
    text: str,
    *,
    secret_values: tuple[str, ...] = (),
    max_characters: int,
) -> tuple[str, int, bool]:
    redacted, count = redact_text(text, secret_values)
    truncated = len(redacted) > max_characters
    bounded = redacted[:max_characters]
    return hashlib.sha256(bounded.encode("utf-8")).hexdigest(), count, truncated


def relative_path_or_none(path: str | Path, root: str | Path) -> str | None:
    candidate = Path(path).resolve()
    base = Path(root).resolve()
    try:
        return candidate.relative_to(base).as_posix()
    except ValueError:
        return None
