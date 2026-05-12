import inspect
import socket

import pytest
from goga_tool_viewer.server.port_finder import find_free_port


class TestFindFreePort:
    def test_callable(self):
        assert callable(find_free_port)

    def test_signature(self):
        sig = inspect.signature(find_free_port)
        params = list(sig.parameters.keys())
        assert params == ["min_port", "max_port"]
        assert sig.return_annotation is int

    def test_returns_int_in_range(self):
        port = find_free_port(49152, 65535)
        assert isinstance(port, int)
        assert 49152 <= port <= 65535

    def test_all_occupied_raises_oserror(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        occupied_port = s.getsockname()[1]
        with pytest.raises(OSError, match="No free port found"):
            find_free_port(occupied_port, occupied_port)
        s.close()

    def test_available_from_facade(self):
        from goga_tool_viewer.server.port_finder import find_free_port as ffp  # noqa: PLC0415

        assert ffp is find_free_port
