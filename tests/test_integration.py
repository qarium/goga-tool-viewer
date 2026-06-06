from __future__ import annotations

import dataclasses
import json
import threading
import time
from textwrap import dedent
from urllib.error import URLError
from urllib.request import urlopen

from goga_tool_viewer import main
from goga_tool_viewer.models import CellGraph
from goga_tool_viewer.parser import parse_json
from goga_tool_viewer.server import GraphServer

SAMPLE_JSON = dedent("""\
    [{
        "cell": "root",
        "description": "Root cell",
        "types": [],
        "usages": [],
        "children": [{
            "cell": "root/child",
            "description": "Child cell",
            "types": ["TypeB"],
            "usages": [],
            "children": [],
            "dependencies": {
                "root/dep": {"types": ["TypeA"], "usages": ["usage1"]}
            }
        }],
        "dependencies": {}
    }]
""")

DEEP_NESTED_JSON = dedent("""\
    [{
        "cell": "a",
        "description": "top",
        "types": [],
        "usages": [],
        "children": [{
            "cell": "a/b",
            "description": "mid",
            "types": [],
            "usages": [],
            "children": [{
                "cell": "a/b/c",
                "description": "leaf",
                "types": ["T1"],
                "usages": ["u1"],
                "children": [],
                "dependencies": {
                    "a": {"types": ["T2"], "usages": []}
                }
            }],
            "dependencies": {
                "a": {"types": ["T1"], "usages": ["u1"]}
            }
        }],
        "dependencies": {}
    }]
""")


def _start_server(graph: CellGraph):
    server = GraphServer(graph, 0)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)
    port = server._server.server_address[1] if server._server else 0
    url = f"http://localhost:{port}"

    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        try:
            urlopen(url, timeout=1)
            break
        except (ConnectionRefusedError, OSError):
            time.sleep(0.05)
    else:
        if server._server:
            server._server.shutdown()
        thread.join(timeout=1)
        raise AssertionError("Server did not start in time")

    return server, url, thread


def _stop_server(server, thread):
    server.stop()
    thread.join(timeout=2)


class TestFullCycle:
    def test_json_to_server(self, tmp_path, sample_json):
        json_file = tmp_path / "data.json"
        json_file.write_text(sample_json, encoding="utf-8")

        graph = parse_json(json_file.read_text(encoding="utf-8"))
        assert len(graph.cells) == 2
        assert len(graph.edges) == 1

        server, url, thread = _start_server(graph)
        try:
            with urlopen(url + "/", timeout=2) as resp:
                html = resp.read().decode("utf-8")
                assert "<!DOCTYPE html>" in html
                assert "cytoscape" in html
                assert "/api/graph" in html
                assert '<script src="/static/app.js">' in html

            with urlopen(url + "/api/graph", timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                assert len(data["cells"]) == 2
                assert len(data["edges"]) == 1
                cell_names = {c["name"] for c in data["cells"]}
                assert cell_names == {"root", "root/child"}
                edge = data["edges"][0]
                assert edge["from_cell"] == "root/child"
                assert edge["to_cell"] == "root/dep"
        finally:
            _stop_server(server, thread)


class TestSerialization:
    def test_nested_children_round_trip(self):
        graph = parse_json(DEEP_NESTED_JSON)
        assert len(graph.cells) == 3
        assert len(graph.edges) == 2

        as_dict = dataclasses.asdict(graph)
        assert "cells" in as_dict
        assert "edges" in as_dict

        root = next(c for c in as_dict["cells"] if c["name"] == "a")
        mid = root["children"][0]
        assert mid["name"] == "a/b"
        leaf = mid["children"][0]
        assert leaf["name"] == "a/b/c"
        assert leaf["types"] == ["T1"]
        assert leaf["usages"] == ["u1"]
        assert leaf["dependencies"][0]["to_cell"] == "a"

        json_str = json.dumps(as_dict)
        restored = json.loads(json_str)
        assert len(restored["cells"]) == 3
        assert len(restored["edges"]) == 2
        assert restored["cells"][0]["name"] == "a"


class TestCliDirect:
    def test_serves_json(self, tmp_path, sample_json, capfd):
        json_file = tmp_path / "graph.json"
        json_file.write_text(sample_json, encoding="utf-8")

        t = threading.Thread(target=main, args=([str(json_file)],), daemon=True)
        t.start()

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

        assert url_line.startswith("http://localhost:")

        for _ in range(20):
            try:
                resp = urlopen(url_line, timeout=2)
                html = resp.read().decode("utf-8")
                assert "cytoscape" in html
                break
            except (URLError, ConnectionError, OSError):
                time.sleep(0.25)
        else:
            raise AssertionError("Server did not start in time")

        api_url = url_line.rstrip("/") + "/api/graph"
        with urlopen(api_url, timeout=2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert len(data["cells"]) == 2
