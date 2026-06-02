import inspect

import pytest

from goga_tool_viewer.frontend import index_page
from goga_tool_viewer.frontend.pages import _read_static_bytes


@pytest.fixture
def static_with_assets(tmp_path, monkeypatch):
    """Create a temporary static directory with minimal PNG and JS files."""
    static = tmp_path / "static"
    static.mkdir()
    # Minimal valid PNG (1x1 transparent pixel)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    (static / "logo.png").write_bytes(png_bytes)
    (static / "favicon.png").write_bytes(png_bytes)
    (static / "goga.svg").write_text("<svg></svg>", encoding="utf-8")
    (static / "cytoscape.min.js").write_text("/* cytoscape */", encoding="utf-8")
    (static / "dagre.min.js").write_text("/* dagre */", encoding="utf-8")
    (static / "cytoscape-dagre.min.js").write_text("/* cyto-dagre */", encoding="utf-8")
    monkeypatch.setattr("goga_tool_viewer.frontend.pages._STATIC", static)


class TestIndexPageDarkTheme:
    """Contract tests for dark theme features."""

    def test_index_page_contains_dark_theme_css_variables(self):
        html = index_page(graph_json_url="/api/graph")
        assert "--color-brand-bg: #0a0e1a" in html
        assert "--color-brand-card: #121830" in html
        assert "--color-brand-teal: #20d4bf" in html
        assert "--color-brand-blue: #3882f6" in html
        assert "--color-brand-text: #fff" in html
        assert "--color-brand-muted: #a0aec0" in html

    def test_index_page_contains_header_with_logo(self):
        html = index_page(graph_json_url="/api/graph")
        assert "<header" in html
        assert "QArium" in html
        assert "data:image/png;base64" in html
        assert "backdrop-filter" in html

    def test_index_page_contains_footer_with_copyright(self):
        html = index_page(graph_json_url="/api/graph")
        assert "<footer" in html
        assert "© 2026 QArium. All rights reserved." in html

    def test_index_page_contains_favicon_link(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<link rel="icon"' in html
        assert "data:image/png;base64" in html

    def test_index_page_cytoscape_dark_styles(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#121830" in html
        assert "#20d4bf" in html
        assert "round-rectangle" in html
        assert "target-arrow-shape" in html

    def test_index_page_info_panel_card_style(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#info" in html
        assert "rgba(255, 255, 255, 0.05)" in html

    def test_index_page_curly_brace_escaping(self):
        html = index_page(graph_json_url="/api/graph")
        # JS blocks should not contain literal {{ which indicates bad escaping
        # Within the <script> section, single { should appear (from f-string {{ })
        # We check that there are no accidental double-braces in JS
        script_start = html.index("<script>", html.index("</head>"))
        script_end = html.index("</script>", script_start)
        script_block = html[script_start:script_end]
        assert "{{" not in script_block, "JS contains unescaped double braces {{ from f-string"


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


class TestIndexPageLogical:
    """Logical tests for edge cases and error handling."""

    def test_index_page_missing_static_file_raises(self, tmp_path, monkeypatch):
        empty_static = tmp_path / "empty_static"
        empty_static.mkdir()
        monkeypatch.setattr("goga_tool_viewer.frontend.pages._STATIC", empty_static)
        with pytest.raises(FileNotFoundError):
            index_page(graph_json_url="/api/graph")

    def test_index_page_special_chars_in_url(self):
        html = index_page(graph_json_url="/api/graph?param=value&other=test")
        assert isinstance(html, str)
        assert 'fetch("/api/graph?param=value&other=test")' in html

    def test_index_page_empty_graph_url(self):
        html = index_page(graph_json_url="")
        assert isinstance(html, str)
        assert html.startswith("<!DOCTYPE html>")

    def test_read_static_bytes_returns_bytes_for_png(self):
        result = _read_static_bytes("logo.png")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_read_static_bytes_missing_file_raises(self, tmp_path, monkeypatch):
        empty_static = tmp_path / "empty_static"
        empty_static.mkdir()
        monkeypatch.setattr("goga_tool_viewer.frontend.pages._STATIC", empty_static)
        with pytest.raises(FileNotFoundError):
            _read_static_bytes("logo.png")
