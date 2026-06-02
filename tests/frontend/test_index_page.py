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
        assert "flex" in html
        assert "flex: 1" in html

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


class TestIndexPageIntegration:
    """Integration tests for full HTML page generation."""

    def test_index_page_full_html_structure(self):
        html = index_page(graph_json_url="/api/graph")
        # All sections present
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "<header" in html
        assert "<main>" in html
        assert "<footer" in html
        # Correct order
        head_pos = html.index("<head>")
        header_pos = html.index("<header")
        main_pos = html.index("<main>")
        footer_pos = html.index("<footer")
        close_body = html.index("</body>")
        assert head_pos < header_pos < main_pos < footer_pos < close_body

    def test_index_page_css_variables_used_in_inline_styles(self):
        html = index_page(graph_json_url="/api/graph")
        # Variables declared in :root
        assert ":root" in html
        for var in [
            "--color-brand-bg",
            "--color-brand-card",
            "--color-brand-teal",
            "--color-brand-blue",
            "--color-brand-text",
            "--color-brand-muted",
        ]:
            assert var in html
        # Variables used via var() in styles
        assert "var(--color-brand-bg)" in html
        assert "var(--color-brand-teal)" in html
        assert "var(--color-brand-text)" in html
        assert "var(--color-brand-muted)" in html

    def test_index_page_embeds_all_js_libraries(self, static_with_assets):
        html = index_page(graph_json_url="/api/graph")
        # Each library is embedded in a <script> tag within <head>
        head_end = html.index("</head>")
        head_section = html[:head_end]
        assert "/* cytoscape */" in head_section
        assert "/* dagre */" in head_section
        assert "/* cyto-dagre */" in head_section
        # Verify they are inside <script> tags
        assert "<script>/* cytoscape */</script>" in head_section
        assert "<script>/* dagre */</script>" in head_section
        assert "<script>/* cyto-dagre */</script>" in head_section


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

    def test_read_static_bytes_returns_bytes_for_png(self, static_with_assets):
        result = _read_static_bytes("logo.png")
        assert isinstance(result, bytes)
        assert result[:4] == b"\x89PNG"

    def test_read_static_bytes_missing_file_raises(self, tmp_path, monkeypatch):
        empty_static = tmp_path / "empty_static"
        empty_static.mkdir()
        monkeypatch.setattr("goga_tool_viewer.frontend.pages._STATIC", empty_static)
        with pytest.raises(FileNotFoundError):
            _read_static_bytes("logo.png")


class TestIndexPageVisualUpdates:
    """Tests for visual updates matching qarium.ru/goga reference."""

    def test_header_two_color_text(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<span class="teal">QA</span>' in html
        assert '<span class="white">rium</span>' in html

    def test_header_contact_icons_present(self):
        html = index_page(graph_json_url="/api/graph")
        assert "t.me/QAriumCommunity" in html
        assert "github.com" in html
        assert "info@qarium.ru" in html
        assert "contact-icons" in html

    def test_footer_has_logo_and_centered_copyright(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<span class="copyright">' in html
        footer_start = html.index("<footer")
        footer_end = html.index("</footer>") + len("</footer>")
        footer = html[footer_start:footer_end]
        assert "data:image/png;base64" in footer

    def test_info_panel_os_window_structure(self):
        html = index_page(graph_json_url="/api/graph")
        assert "info-wrapper" in html
        assert "info-titlebar" in html
        assert "info-close" in html

    def test_info_panel_hidden_by_default(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'class="hidden"' in html

    def test_info_panel_close_handler(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'addEventListener("click"' in html

    def test_yaml_formatting_in_show_cell_info(self):
        html = index_page(graph_json_url="/api/graph")
        assert "yaml-key" in html
        assert "yaml-string" in html
        assert "yaml-null" in html
        assert "_yamlList" in html
        assert "_yamlValue" in html

    def test_node_styling_with_border(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#0f172a" in html
        assert "border-width" in html
        assert "text-wrap" in html

    def test_info_panel_opens_on_node_tap(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'classList.remove("hidden")' in html
