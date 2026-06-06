from __future__ import annotations

import io
import json
import sys
from inspect import signature
from textwrap import dedent

import pytest
from goga_tool_viewer.models import CellGraph
from goga_tool_viewer.parser import load_json_file, load_json_stdin, parse_json

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
            "dependencies": {
                "root/dep": {"types": ["TypeA"], "usages": ["usage1"]}
            },
            "children": []
        }],
        "dependencies": {}
    }]
""")


class TestParseJson:
    def test_callable(self):
        assert callable(parse_json)

    def test_signature(self):
        sig = signature(parse_json)
        params = list(sig.parameters.keys())
        assert params == ["json_str", "project_root"]

    def test_returns_cell_graph(self):
        result = parse_json("[]")
        assert isinstance(result, CellGraph)

    def test_facade_import(self):
        from goga_tool_viewer.parser import parse_json as facade_parse  # noqa: PLC0415

        assert facade_parse is parse_json

    def test_project_root_default_empty(self):
        graph = parse_json("[]")
        assert graph.project_root == ""

    def test_project_root_passed_through(self):
        graph = parse_json("[]", project_root="/tmp/test_project")
        assert graph.project_root == "/tmp/test_project"

    def test_happy_path(self):
        graph = parse_json(SAMPLE_JSON)
        assert isinstance(graph, CellGraph)
        assert len(graph.cells) == 2
        assert len(graph.edges) == 1

        root = graph.cells[0]
        assert root.name == "root"
        assert root.description == "Root cell"
        assert root.types == []
        assert len(root.children) == 1

        child = graph.cells[1]
        assert child.name == "root/child"
        assert child.description == "Child cell"
        assert child.types == ["TypeB"]
        assert child.dependencies[0].to_cell == "root/dep"

        edge = graph.edges[0]
        assert edge.from_cell == "root/child"
        assert edge.to_cell == "root/dep"
        assert edge.types == ["TypeA"]
        assert edge.usages == ["usage1"]

    def test_empty_array(self):
        graph = parse_json("[]")
        assert isinstance(graph, CellGraph)
        assert graph.cells == []
        assert graph.edges == []

    def test_cell_no_deps_no_children(self):
        data = '[{"cell": "solo", "description": "A lone cell"}]'
        graph = parse_json(data)
        assert len(graph.cells) == 1
        assert graph.cells[0].name == "solo"
        assert graph.cells[0].description == "A lone cell"
        assert graph.cells[0].children == []
        assert graph.cells[0].dependencies == []
        assert graph.edges == []

    def test_deep_nesting(self):
        deep_json = json.dumps(
            [
                {
                    "cell": "a",
                    "children": [
                        {
                            "cell": "a/b",
                            "children": [
                                {"cell": "a/b/c", "dependencies": {"x": {"types": ["T"], "usages": []}}, "children": []}
                            ],
                            "dependencies": {},
                        }
                    ],
                    "dependencies": {},
                }
            ]
        )
        graph = parse_json(deep_json)
        assert len(graph.cells) == 3
        names = {c.name for c in graph.cells}
        assert names == {"a", "a/b", "a/b/c"}
        assert len(graph.edges) == 1
        assert graph.edges[0].from_cell == "a/b/c"
        assert graph.edges[0].to_cell == "x"

    def test_multiple_top_level_cells(self):
        data = json.dumps(
            [
                {"cell": "a", "dependencies": {}, "children": []},
                {"cell": "b", "dependencies": {"a": {"types": [], "usages": []}}, "children": []},
            ]
        )
        graph = parse_json(data)
        assert len(graph.cells) == 2
        names = {c.name for c in graph.cells}
        assert names == {"a", "b"}
        assert len(graph.edges) == 1
        assert graph.edges[0].from_cell == "b"
        assert graph.edges[0].to_cell == "a"

    def test_cell_with_multiple_dependencies(self):
        data = json.dumps(
            [
                {
                    "cell": "multi",
                    "dependencies": {
                        "dep_a": {"types": ["T1"], "usages": ["u1"]},
                        "dep_b": {"types": ["T2"], "usages": []},
                    },
                    "children": [],
                }
            ]
        )
        graph = parse_json(data)
        assert len(graph.cells) == 1
        assert len(graph.edges) == 2
        targets = {e.to_cell for e in graph.edges}
        assert targets == {"dep_a", "dep_b"}
        types = {e.to_cell: e.types for e in graph.edges}
        assert types["dep_a"] == ["T1"]
        assert types["dep_b"] == ["T2"]

    def test_cell_with_multiple_children(self):
        data = json.dumps(
            [
                {
                    "cell": "parent",
                    "children": [
                        {"cell": "child_a", "dependencies": {}, "children": []},
                        {"cell": "child_b", "dependencies": {}, "children": []},
                    ],
                    "dependencies": {},
                }
            ]
        )
        graph = parse_json(data)
        assert len(graph.cells) == 3
        parent = graph.cells[0]
        assert parent.name == "parent"
        assert len(parent.children) == 2
        assert {c.name for c in parent.children} == {"child_a", "child_b"}


class TestParseJsonInvalid:
    def test_invalid_json(self):
        with pytest.raises(json.JSONDecodeError):
            parse_json("not a json")

    def test_non_array_top_level(self):
        with pytest.raises(ValueError, match="Expected a JSON array"):
            parse_json('{"cell": "test"}')

    def test_missing_cell_key(self):
        with pytest.raises(ValueError, match="must have a 'cell' key"):
            parse_json('[{"name": "no_cell_key"}]')


class TestLoadJsonFile:
    def test_callable(self):
        assert callable(load_json_file)

    def test_signature(self):
        sig = signature(load_json_file)
        params = list(sig.parameters.keys())
        assert params == ["path"]

    def test_reads_file(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text(SAMPLE_JSON, encoding="utf-8")
        graph = load_json_file(str(p))
        assert len(graph.cells) == 2
        assert len(graph.edges) == 1

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_json_file("/nonexistent/path.json")

    def test_facade_import(self):
        from goga_tool_viewer.parser import load_json_file as facade_load_file  # noqa: PLC0415

        assert facade_load_file is load_json_file

    def test_project_root_set_from_file_parent(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text(SAMPLE_JSON, encoding="utf-8")
        graph = load_json_file(str(p))
        assert graph.project_root == str(tmp_path.resolve())


class TestLoadJsonStdin:
    def test_callable(self):
        assert callable(load_json_stdin)

    def test_signature(self):
        sig = signature(load_json_stdin)
        params = list(sig.parameters.keys())
        assert params == []

    def test_reads_stdin(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_JSON))
        graph = load_json_stdin()
        assert len(graph.cells) == 2
        assert len(graph.edges) == 1

    def test_invalid_json(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", io.StringIO("not json"))
        with pytest.raises(json.JSONDecodeError):
            load_json_stdin()

    def test_facade_import(self):
        from goga_tool_viewer.parser import load_json_stdin as facade_load_stdin  # noqa: PLC0415

        assert facade_load_stdin is load_json_stdin

    def test_project_root_set_from_cwd(self, monkeypatch, tmp_path):
        monkeypatch.setattr(sys, "stdin", io.StringIO(SAMPLE_JSON))
        monkeypatch.chdir(tmp_path)
        graph = load_json_stdin()
        assert graph.project_root == str(tmp_path.resolve())
