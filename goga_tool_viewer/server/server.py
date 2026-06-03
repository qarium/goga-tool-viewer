"""HTTP server for serving cell dependency graph visualization."""

from __future__ import annotations

import dataclasses
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from ..frontend import index_page
from ..models import CellGraph
from ..parser import load_json_file, load_json_stdin
from .port_finder import find_free_port

logger = logging.getLogger(__name__)


def _to_dict(graph: CellGraph) -> dict[str, Any]:
    """Convert CellGraph to dict for JSON serialization."""
    return dataclasses.asdict(graph)


def _make_handler(graph: CellGraph) -> type[BaseHTTPRequestHandler]:
    """Create a request handler class bound to a specific CellGraph."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/":
                html = index_page("/api/graph")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            elif self.path == "/api/graph":
                data = json.dumps(_to_dict(graph))
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(data.encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format: str, *args: Any) -> None:
            logger.info(
                format % args,
                extra={
                    "client": self.client_address[0],
                    "method": self.command,
                    "path": self.path,
                },
            )

    return Handler


class GraphServer:
    """HTTP server that serves the cell dependency graph visualization."""

    def __init__(self, graph: CellGraph, port: int) -> None:
        """Initialize the server with graph data and port.

        Args:
            graph: Cell graph data to serve.
            port: TCP port number to listen on.
        """
        self.graph = graph
        self.port = port
        self._server: HTTPServer | None = None

    def start(self) -> None:
        """Start the HTTP server (blocking).

        Raises:
            OSError: If the port is already in use.
        """
        handler = _make_handler(self.graph)

        self._server = HTTPServer(("", self.port), handler)
        self._server.serve_forever()

    def stop(self) -> None:
        """Shut down the HTTP server and close the socket."""
        if self._server:
            self._server.shutdown()
            self._server.server_close()

    def url(self) -> str:
        """Return the server URL.

        Returns:
            The full localhost URL string including the port.
        """
        return f"http://localhost:{self.port}"


def run_server(json_path: str | None) -> None:
    """Load graph data and start the server.

    If json_path is provided, loads from file; otherwise reads from stdin.

    Args:
        json_path: Path to a JSON file, or None to read from stdin.
    """
    graph = load_json_file(json_path) if json_path is not None else load_json_stdin()

    port = find_free_port(49152, 65535)
    server = GraphServer(graph, port)
    print(server.url(), flush=True)
    server.start()
