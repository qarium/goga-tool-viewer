from __future__ import annotations

import inspect
import io
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from goga_tool_viewer import main


def _wait_for_url(capfd) -> str:
    """Poll capfd until a localhost URL appears in stdout."""
    deadline = time.monotonic() + 5.0
    url_line = ""
    while time.monotonic() < deadline:
        out, _ = capfd.readouterr()
        for line in reversed(out.strip().splitlines()):
            if line.startswith("http://localhost:"):
                url_line = line
                break
        if url_line:
            break
        time.sleep(0.1)
    return url_line


def _wait_for_server(url: str) -> None:
    """Poll urlopen until the server responds."""
    for _ in range(20):
        try:
            resp = urlopen(url, timeout=2)
            resp.read()
            return
        except (URLError, ConnectionError, OSError):
            time.sleep(0.25)
    raise AssertionError("Server did not start in time")


class TestMain:
    def test_callable(self):
        assert callable(main)

    def test_accepts_argv(self):
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())
        assert params == ["argv"]

    def test_importable_from_facade(self):
        from goga_tool_viewer import main as m  # noqa: PLC0415

        assert m is main


class TestMainWithFileArg:
    def test_with_file_arg(self, tmp_path, capfd, sample_json):
        p = tmp_path / "data.json"
        p.write_text(sample_json, encoding="utf-8")

        t = threading.Thread(target=main, args=([str(p)],), daemon=True)
        t.start()

        url_line = _wait_for_url(capfd)
        assert url_line.startswith("http://localhost:")
        _wait_for_server(url_line)

        with urlopen(url_line, timeout=2) as resp:
            html = resp.read().decode("utf-8")
            assert "cytoscape" in html


class TestMainWithInvalidFile:
    def test_exits_with_error(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            main(["/nonexistent/path.json"])
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert len(captured.err) > 0

    def test_exits_on_invalid_json_structure(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text('{"not": "an array"}', encoding="utf-8")
        with pytest.raises(SystemExit) as exc_info:
            main([str(p)])
        assert exc_info.value.code == 1

    def test_exits_on_empty_stdin(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO(""))
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 1


class TestMainWithStdin:
    def test_reads_from_stdin(self, monkeypatch, capfd, sample_json):
        monkeypatch.setattr(sys, "stdin", io.StringIO(sample_json))

        t = threading.Thread(target=main, args=([],), daemon=True)
        t.start()

        url_line = _wait_for_url(capfd)
        assert url_line.startswith("http://localhost:")
        _wait_for_server(url_line)

        with urlopen(url_line, timeout=2) as resp:
            assert resp.status == 200
