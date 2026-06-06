"""HTTP server for serving cell dependency graph visualization."""

from __future__ import annotations

import dataclasses
import json
import logging
import mimetypes
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..frontend import index_page
from ..loader import load_codemanifest
from ..models import CellGraph
from ..parser import load_json_file, load_json_stdin
from .port_finder import find_free_port

_MIME_TYPES: dict[str, str] = {
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
}

logger = logging.getLogger(__name__)


def _to_dict(graph: CellGraph) -> dict[str, Any]:
    """Convert CellGraph to dict for JSON serialization."""
    return dataclasses.asdict(graph)


class _GraphHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the cell graph visualization."""

    graph: CellGraph
    static_dir: Path

    def do_GET(self) -> None:
        if self.path == "/":
            self._serve_index()
        elif self.path.startswith("/static/"):
            self._serve_static()
        elif self.path == "/api/graph":
            self._serve_graph()
        elif urlparse(self.path).path == "/api/codemanifest":
            self._serve_codemanifest()
        else:
            self.send_response(404)
            self.end_headers()

    def _send_text(self, code: int, body: str, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _serve_index(self) -> None:
        html = index_page("/api/graph")
        self._send_text(200, html, "text/html; charset=utf-8")

    def _serve_graph(self) -> None:
        data = json.dumps(_to_dict(self.graph))
        self._send_text(200, data, "application/json; charset=utf-8")

    def _serve_static(self) -> None:
        filename = self.path[len("/static/"):]

        if "/" in filename or ".." in filename:
            self._send_text(400, "Invalid static path", "text/plain; charset=utf-8")
            return

        file_path = self.static_dir / filename

        if not file_path.is_file():
            self.send_response(404)
            self.end_headers()
            return

        ext = file_path.suffix.lower()
        content_type = _MIME_TYPES.get(
            ext,
            mimetypes.guess_type(filename)[0] or "application/octet-stream",
        )

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(file_path.read_bytes())

    def _serve_codemanifest(self) -> None:
        params = parse_qs(urlparse(self.path).query)
        cell_path = params.get("cell", [None])[0]

        if cell_path is None or cell_path == "":
            self._send_text(400, "Missing 'cell' parameter", "text/plain; charset=utf-8")
            return

        try:
            content = load_codemanifest(cell_path, project_root=self.graph.project_root)
        except FileNotFoundError:
            self._send_text(404, "CODEMANIFEST not found", "text/plain; charset=utf-8")
            return
        except ValueError:
            self._send_text(400, "Invalid cell path", "text/plain; charset=utf-8")
            return
        except Exception:
            logger.exception("codemanifest read error")
            self._send_text(500, "Internal server error", "text/plain; charset=utf-8")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        logger.info(
            format % args,
            extra={
                "client": self.client_address[0],
                "method": self.command,
                "path": self.path,
            },
        )


class GraphServer:
    """HTTP server that serves the cell dependency graph visualization."""

    def __init__(self, graph: CellGraph, port: int, static_dir: Path | None = None) -> None:
        """Initialize the server with graph data and port.

        Args:
            graph: Cell graph data to serve.
            port: TCP port number to listen on.
            static_dir: Directory with static files. Defaults to
                frontend/static within the package.
        """
        self.graph = graph
        self.port = port

        if static_dir is None:
            static_dir = Path(__file__).resolve().parent.parent / "frontend" / "static"

        self._static_dir = static_dir
        self._server: HTTPServer | None = None

    def get_codemanifest(self, cell_path: str) -> str:
        """Load CODEMANIFEST content for the given cell path.

        Delegates to load_codemanifest for safe file reading with
        path traversal protection.

        Args:
            cell_path: Relative path to a cell directory
                (e.g. "goga_tool_viewer/parser").

        Returns:
            Text content of the CODEMANIFEST file as a string.

        Raises:
            FileNotFoundError: If the CODEMANIFEST file does not exist.
            ValueError: If the cell path is invalid or attempts traversal.
        """
        return load_codemanifest(cell_path, project_root=self.graph.project_root)

    def start(self) -> None:
        """Start the HTTP server (blocking).

        Raises:
            OSError: If the port is already in use.
        """
        handler = type(
            "_BoundHandler",
            (_GraphHandler,),
            {"graph": self.graph, "static_dir": self._static_dir},
        )

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
