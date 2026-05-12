import inspect

from goga_tool_viewer.frontend import index_page


class TestIndexPage:
    def test_callable(self):
        assert callable(index_page)

    def test_signature(self):
        sig = inspect.signature(index_page)
        params = list(sig.parameters.keys())
        assert params == ["graph_json_url"]

    def test_returns_str(self):
        result = index_page(graph_json_url="/api/graph")
        assert isinstance(result, str)

    def test_contains_cytoscape(self):
        html = index_page(graph_json_url="/api/graph")
        assert "cytoscape" in html
        assert "/api/graph" in html
        assert "render_graph" in html
        assert "<!DOCTYPE html>" in html
        assert "show_cell_info" in html
        assert "highlight_cell" in html

    def test_contains_layout_styles(self):
        html = index_page(graph_json_url="/api/graph")
        assert "80%" in html
        assert "flex" in html

    def test_uses_graph_json_url(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'fetch("/api/graph")' in html

        html2 = index_page(graph_json_url="/custom/api")
        assert 'fetch("/custom/api")' in html2

    def test_contains_dagre_layout(self):
        html = index_page(graph_json_url="/api/graph")
        assert "dagre" in html
        assert "cytoscape-dagre" in html
        assert "mouseout" in html

    def test_available_from_facade(self):
        from goga_tool_viewer.frontend import index_page as facade_index_page  # noqa: PLC0415

        assert facade_index_page is index_page
