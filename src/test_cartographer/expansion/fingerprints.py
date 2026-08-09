
"""Stable fingerprints used to bind expansion artefacts to accepted context."""

from __future__ import annotations

import hashlib
import json

from test_cartographer.context.models import ContextBundle


def context_sha256(context: ContextBundle) -> str:
    """Hash the complete validated bundle using deterministic canonical JSON."""

    payload = json.dumps(
        context.model_dump(mode="json", exclude_none=False),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
