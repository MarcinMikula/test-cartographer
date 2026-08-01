"""Controlled local HTTP server used only by the Sprint 3 reference flow."""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        return


@contextlib.contextmanager
def serve_reference_directory(directory: str | Path) -> Iterator[str]:
    """Serve one local fixture directory on an ephemeral loopback port."""

    root = Path(directory).resolve()
    handler = partial(_QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
