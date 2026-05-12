from __future__ import annotations

import threading
import time
from urllib.request import urlopen

import pytest
from goga_tool_viewer.models import CellGraph
from goga_tool_viewer.server import GraphServer


def _wait_for_server(url: str, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.05)
    return False


@pytest.fixture
def running_server():
    def _start(graph: CellGraph, port: int = 0):
        server = GraphServer(graph, port)
        thread = threading.Thread(target=server.start, daemon=True)
        thread.start()
        time.sleep(0.5)
        actual_port = server._server.server_address[1] if server._server else 0
        url = f"http://localhost:{actual_port}"
        if not _wait_for_server(url):
            if server._server:
                server._server.shutdown()
            thread.join(timeout=1)
            raise AssertionError("Server did not start")
        return server, url, thread

    return _start
