import inspect

import pytest
from goga_tool_viewer.frontend import index_page
from goga_tool_viewer.frontend.pages import _STATIC, _read_static_bytes


@pytest.fixture
def static_with_assets(tmp_path, monkeypatch):
    """Create a temporary static directory with minimal PNG and JS files."""
    static = tmp_path / "static"
    static.mkdir()
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

    def test_index_page_contains_dark_theme_css_link(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<link rel="stylesheet" href="/static/style.css">' in html

    def test_index_page_contains_js_script_link(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<script src="/static/app.js">' in html

    def test_index_page_contains_header_with_logo(self):
        html = index_page(graph_json_url="/api/graph")
        assert "<header" in html
        assert "QArium" in html
        assert "data:image/png;base64" in html

    def test_index_page_contains_footer_with_copyright(self):
        html = index_page(graph_json_url="/api/graph")
        assert "<footer" in html
        assert "QArium" in html

    def test_index_page_contains_favicon_link(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<link rel="icon"' in html
        assert "data:image/png;base64" in html

    def test_index_page_passes_api_url_via_data_attribute(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'data-api-url="/api/graph"' in html


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

    def test_contains_cytoscape_script_tag(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<script src="/static/cytoscape.min.js">' in html

    def test_contains_dagre_script_tags(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<script src="/static/dagre.min.js">' in html
        assert '<script src="/static/cytoscape-dagre.min.js">' in html

    def test_uses_graph_json_url(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'data-api-url="/api/graph"' in html

        html2 = index_page(graph_json_url="/custom/api")
        assert 'data-api-url="/custom/api"' in html2

    def test_available_from_facade(self):
        from goga_tool_viewer.frontend import index_page as facade_index_page  # noqa: PLC0415

        assert facade_index_page is index_page


class TestIndexPageIntegration:
    """Integration tests for full HTML page generation."""

    def test_index_page_full_html_structure(self):
        html = index_page(graph_json_url="/api/graph")
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "<header" in html
        assert "<main>" in html
        assert "<footer" in html
        head_pos = html.index("<head>")
        header_pos = html.index("<header")
        main_pos = html.index("<main>")
        footer_pos = html.index("<footer")
        close_body = html.index("</body>")
        assert head_pos < header_pos < main_pos < footer_pos < close_body

    def test_index_page_css_custom_properties_for_icons(self):
        html = index_page(graph_json_url="/api/graph")
        assert "--icon-name:" in html
        assert "--icon-description:" in html
        assert "--icon-types:" in html
        assert "--icon-consumers:" in html
        assert "--icon-dependencies:" in html
        assert "--icon-folder:" in html
        assert "--icon-layers:" in html
        assert "--icon-code:" in html
        assert "--icon-reset:" in html

    def test_no_inline_cytoscape_js(self, static_with_assets):
        html = index_page(graph_json_url="/api/graph")
        assert "/* cytoscape */" not in html
        assert "/* dagre */" not in html
        assert "/* cyto-dagre */" not in html

    def test_js_libraries_loaded_via_script_src(self, static_with_assets):
        html = index_page(graph_json_url="/api/graph")
        assert '<script src="/static/cytoscape.min.js">' in html
        assert '<script src="/static/dagre.min.js">' in html
        assert '<script src="/static/cytoscape-dagre.min.js">' in html


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
        assert 'data-api-url="/api/graph?param=value&other=test"' in html

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

    def test_info_panel_close_handler_in_external_js(self):
        html = index_page(graph_json_url="/api/graph")
        assert '<script src="/static/app.js">' in html


class TestIndexPageSidebar:
    """Tests for sidebar with cell hierarchy tree."""

    def test_sidebar_html_structure(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'id="sidebar"' in html
        assert 'id="sidebar-title"' in html
        assert 'id="sidebar-tree"' in html
        assert 'id="sidebar-footer"' in html

    def test_sidebar_title_text(self):
        html = index_page(graph_json_url="/api/graph")
        assert ">Cells<" in html

    def test_sidebar_reset_button(self):
        html = index_page(graph_json_url="/api/graph")
        assert "tree-show-all" in html
        assert "Reset" in html

    def test_sidebar_reset_button_has_icon(self):
        html = index_page(graph_json_url="/api/graph")
        assert "tree-show-all" in html
        assert "Reset" in html
        assert "link-icon" in html


class TestIndexPageCodemanifest:
    """Contract tests for CODEMANIFEST viewer in frontend."""

    def test_index_page_has_codemanifest_panel_html(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'id="info-footer"' in html
        assert "codemanifest-link" not in html


class TestStaticFiles:
    """Tests for external CSS and JS static files."""

    def test_style_css_exists(self):
        assert (_STATIC / "style.css").is_file()

    def test_app_js_exists(self):
        assert (_STATIC / "app.js").is_file()

    def test_style_css_contains_key_selectors(self):
        css = (_STATIC / "style.css").read_text(encoding="utf-8")
        assert ":root" in css
        assert "--color-brand-bg" in css
        assert "#sidebar" in css
        assert "#codemanifest-panel" in css
        assert ".tree-node" in css

    def test_app_js_contains_key_functions(self):
        js = (_STATIC / "app.js").read_text(encoding="utf-8")
        assert "function render_graph" in js
        assert "function highlight_cell" in js
        assert "function render_tree" in js
        assert "function show_cell_info" in js
        assert "function show_codemanifest" in js
        assert "function _init_custom_scroll" in js
        assert "function apply_filter" in js
        assert "function reset_filter" in js

    def test_app_js_reads_api_url_from_data_attribute(self):
        js = (_STATIC / "app.js").read_text(encoding="utf-8")
        assert "data-api-url" in js

    def test_app_js_reads_icons_from_css_vars(self):
        js = (_STATIC / "app.js").read_text(encoding="utf-8")
        assert "--icon-folder" in js
        assert "--icon-layers" in js
        assert "--icon-code" in js

    def test_style_css_uses_icon_custom_properties(self):
        css = (_STATIC / "style.css").read_text(encoding="utf-8")
        assert "var(--icon-name)" in css
        assert "var(--icon-description)" in css
        assert "var(--icon-types)" in css
        assert "var(--icon-consumers)" in css
        assert "var(--icon-dependencies)" in css
