from __future__ import annotations

import inspect
import json
import urllib.error
import urllib.request

import pytest
from goga_tool_viewer.models import CellGraph
from goga_tool_viewer.server import GraphServer, run_server


class TestGraphServer:
    def test_constructs_with_cellgraph_and_int(self):
        server = GraphServer(CellGraph(), 8080)
        assert isinstance(server, GraphServer)

    def test_has_start_method(self):
        assert hasattr(GraphServer, "start")

    def test_has_url_method(self):
        server = GraphServer(CellGraph(), 8080)
        assert callable(server.url)

    def test_url_returns_correct_url(self):
        server = GraphServer(CellGraph(), 8080)
        result = server.url()
        assert isinstance(result, str)
        assert "localhost" in result
        assert "8080" in result

    def test_serves_html_at_root(self, test_graph, running_server):
        server, url, thread = running_server(test_graph)
        try:
            req = urllib.request.Request(url + "/")
            with urllib.request.urlopen(req, timeout=2) as resp:
                html = resp.read().decode("utf-8")
                assert "<!DOCTYPE html>" in html
                assert '<link rel="stylesheet" href="/static/style.css">' in html
                assert '<script src="/static/app.js">' in html
                assert resp.headers.get_content_type() == "text/html"
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_serves_json_at_api_graph(self, test_graph, running_server):
        server, url, thread = running_server(test_graph)
        try:
            req = urllib.request.Request(url + "/api/graph")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                assert "cells" in data
                assert "edges" in data
                assert len(data["cells"]) == 2
                assert len(data["edges"]) == 1
                assert resp.headers.get_content_type() == "application/json"
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_returns_404_for_unknown(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(urllib.request.Request(url + "/unknown"), timeout=2)
            assert exc_info.value.code == 404
        finally:
            server.stop()
            thread.join(timeout=2)


class TestStaticFilesRoute:
    """Tests for /static/* route."""

    def test_serves_css_file(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(url + "/static/style.css")
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "text/css" in resp.headers.get_content_type()
                body = resp.read().decode("utf-8")
                assert ":root" in body
                assert "--color-brand-bg" in body
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_serves_js_file(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(url + "/static/app.js")
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "javascript" in resp.headers.get_content_type()
                body = resp.read().decode("utf-8")
                assert "function render_graph" in body
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_serves_cytoscape_js(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(url + "/static/cytoscape.min.js")
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "javascript" in resp.headers.get_content_type()
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_serves_png_image(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(url + "/static/logo.png")
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "image/png" in resp.headers.get_content_type()
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_serves_svg_image(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(url + "/static/icon-telegram.svg")
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "image/svg+xml" in resp.headers.get_content_type()
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_returns_404_for_missing_static_file(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(url + "/static/nonexistent.css"),
                    timeout=2,
                )
            assert exc_info.value.code == 404
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_rejects_path_traversal(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(url + "/static/../server.py"),
                    timeout=2,
                )
            assert exc_info.value.code == 400
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_rejects_double_dot_filename(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(url + "/static/..%2fserver.py"),
                    timeout=2,
                )
            assert exc_info.value.code in (400, 404)
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_rejects_subdirectory_path(self, running_server):
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(url + "/static/sub/file.css"),
                    timeout=2,
                )
            assert exc_info.value.code == 400
        finally:
            server.stop()
            thread.join(timeout=2)


class TestCodemanifestRoute:
    """Contract and logical tests for /api/codemanifest route."""

    def test_graphserver_has_get_codemanifest(self):
        """GraphServer must have a callable get_codemanifest method."""
        assert hasattr(GraphServer, "get_codemanifest")
        assert callable(GraphServer.get_codemanifest)

    def test_server_codemanifest_route_returns_content(self, running_server):
        """GET /api/codemanifest?cell=<path> returns 200 text/plain with yaml."""
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(
                url + "/api/codemanifest?cell=goga_tool_viewer/models"
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "text/plain" in resp.headers.get_content_type()
                body = resp.read().decode("utf-8")
                assert isinstance(body, str)
                assert len(body) > 0
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_server_get_codemanifest_returns_404_for_missing(
        self, running_server
    ):
        """GET /api/codemanifest?cell=nonexistent returns 404."""
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(
                        url + "/api/codemanifest?cell=nonexistent/cell"
                    ),
                    timeout=2,
                )
            assert exc_info.value.code == 404
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_server_get_codemanifest_returns_400_without_cell_param(
        self, running_server
    ):
        """GET /api/codemanifest without cell param returns 400."""
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(url + "/api/codemanifest"),
                    timeout=2,
                )
            assert exc_info.value.code == 400
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_server_get_codemanifest_empty_cell_param(self, running_server):
        """GET /api/codemanifest?cell= returns 400."""
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(
                        url + "/api/codemanifest?cell="
                    ),
                    timeout=2,
                )
            assert exc_info.value.code == 400
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_server_get_codemanifest_returns_400_for_traversal(
        self, running_server
    ):
        """GET /api/codemanifest?cell=../../etc/passwd returns 400."""
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(
                        url + "/api/codemanifest?cell=../../etc/passwd"
                    ),
                    timeout=2,
                )
            assert exc_info.value.code == 400
        finally:
            server.stop()
            thread.join(timeout=2)

    def test_server_get_codemanifest_rejects_prefix_collision(
        self, running_server
    ):
        """GET /api/codemanifest_evil returns 404, not 400."""
        server, url, thread = running_server(CellGraph())
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(
                    urllib.request.Request(
                        url + "/api/codemanifest_evil"
                    ),
                    timeout=2,
                )
            assert exc_info.value.code == 404
        finally:
            server.stop()
            thread.join(timeout=2)


class TestCodemanifestIntegration:
    """Integration tests for the full codemanifest HTTP flow."""

    def test_server_codemanifest_full_flow(self, running_server):
        """GET /api/codemanifest?cell=goga_tool_viewer/models returns real content."""
        server, url, thread = running_server(CellGraph())
        try:
            req = urllib.request.Request(
                url + "/api/codemanifest?cell=goga_tool_viewer/models"
            )
            with urllib.request.urlopen(req, timeout=2) as resp:
                assert resp.status == 200
                assert "text/plain" in resp.headers.get_content_type()
                body = resp.read().decode("utf-8")
                assert isinstance(body, str)
                assert len(body) > 0
                assert "Usages:" in body or "Annotations:" in body
        finally:
            server.stop()
            thread.join(timeout=2)


class TestRunServer:
    def test_signature(self):
        sig = inspect.signature(run_server)
        params = list(sig.parameters.keys())
        assert len(params) == 1
        param = sig.parameters[params[0]]
        assert param.annotation in (str, "str | None", str | None, inspect.Parameter.empty)
