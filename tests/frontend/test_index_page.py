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
        assert "#info h2" in html
        assert "#info p" in html
        assert "#info ul" in html
        assert "#info .section" in html
        assert "#info .description" in html

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

    def test_markdown_formatting_in_show_cell_info(self):
        html = index_page(graph_json_url="/api/graph")
        assert "function show_cell_info" in html
        assert '<h2 data-icon="name">Name</h2>' in html
        assert '<h2 data-icon="description">Description</h2>' in html
        assert '<h2 data-icon="types">Types</h2>' in html
        assert '<h2 data-icon="consumers">Consumers</h2>' in html
        assert '<h2 data-icon="dependencies">Dependencies</h2>' in html
        assert "section" in html
        assert "description" in html
        assert "_esc" in html

    def test_node_styling_with_border(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#0f172a" in html
        assert "border-width" in html
        assert "text-wrap" in html

    def test_info_panel_opens_on_node_tap(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'classList.remove("hidden")' in html


class TestIndexPageVisualEffects:
    """Tests for visual effects: gradients, shadows, animations."""

    def test_node_gradient_fill(self):
        html = index_page(graph_json_url="/api/graph")
        assert "linear-gradient" in html
        assert "background-gradient-direction" in html
        assert "background-gradient-stop-colors" in html

    def test_node_shadow_glow(self):
        html = index_page(graph_json_url="/api/graph")
        assert "shadow-blur" in html
        assert "shadow-color" in html
        assert "rgba(32, 212, 191, 0.15)" in html

    def test_node_transition_properties(self):
        html = index_page(graph_json_url="/api/graph")
        assert "transition-property" in html
        assert "transition-duration" in html

    def test_fade_in_animation(self):
        html = index_page(graph_json_url="/api/graph")
        assert "@keyframes fadeIn" in html
        assert "fadeIn" in html
        assert "animation:" in html

    def test_edge_highlighted_style(self):
        html = index_page(graph_json_url="/api/graph")
        assert "edge.highlighted" in html

    def test_dimmed_style_class(self):
        html = index_page(graph_json_url="/api/graph")
        assert "'.dimmed'" in html

    def test_highlight_enhanced_glow(self):
        html = index_page(graph_json_url="/api/graph")
        assert "'.highlight'" in html
        assert "rgba(32, 212, 191, 0.4)" in html

    def test_highlight_cell_clears_previous_state(self):
        html = index_page(graph_json_url="/api/graph")
        assert "removeClass('highlight highlighted')" in html


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

    def test_sidebar_show_all_button(self):
        html = index_page(graph_json_url="/api/graph")
        assert "tree-show-all" in html
        assert "Show all" in html

    def test_sidebar_css_width(self):
        html = index_page(graph_json_url="/api/graph")
        assert "width: 260px" in html

    def test_sidebar_css_background(self):
        html = index_page(graph_json_url="/api/graph")
        sidebar_start = html.index("#sidebar")
        sidebar_end = html.index("}", sidebar_start) + 1
        sidebar_css = html[sidebar_start:sidebar_end]
        assert "#0f172a" in sidebar_css

    def test_tree_node_css_styles(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".tree-node" in html
        assert ".tree-node.active" in html
        assert "border-left-color" in html
        assert "cursor: pointer" in html
        assert ".tree-icon" in html
        assert ".tree-name" in html
        assert ".tree-badge" in html
        assert ".tree-guide" in html

    def test_graph_offset_by_sidebar(self):
        html = index_page(graph_json_url="/api/graph")
        cy_start = html.index("#cy")
        cy_end = html.index("}", cy_start) + 1
        cy_css = html[cy_start:cy_end]
        assert "left: 276px" in cy_css

    def test_render_tree_function_exists(self):
        html = index_page(graph_json_url="/api/graph")
        assert "function render_tree(" in html
        assert "build_node" in html
        assert "ancestorPipes" in html

    def test_tree_node_has_icons(self):
        html = index_page(graph_json_url="/api/graph")
        assert "folderIcon" in html
        assert "cubeIcon" in html
        assert "tree-icon" in html
        assert "icon-layers" not in html
        assert "icon-folder" not in html

    def test_tree_node_has_deps_badge(self):
        html = index_page(graph_json_url="/api/graph")
        assert "tree-badge" in html
        assert "depCount" in html

    def test_render_tree_uses_children(self):
        html = index_page(graph_json_url="/api/graph")
        assert "cell.children" in html

    def test_render_tree_called_on_init(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'render_tree("sidebar-tree", graph, cy)' in html

    def test_show_all_resets_highlight(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".tree-show-all" in html
        assert "removeClass('dimmed highlight highlighted')" in html
        assert ".tree-node.active" in html

    def test_sidebar_scrollbar_styles(self):
        html = index_page(graph_json_url="/api/graph")
        assert "::-webkit-scrollbar" in html
        assert "4px" in html


class TestIndexPageCodemanifest:
    """Contract tests for CODEMANIFEST viewer in frontend."""

    def test_index_page_contains_show_codemanifest_function(self):
        html = index_page(graph_json_url="/api/graph")
        assert "function show_codemanifest" in html
        assert "/api/codemanifest" in html

    def test_index_page_contains_codemanifest_panel_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#codemanifest-panel" in html
        assert ".code-content" in html


class TestIndexPageCodemanifestLogical:
    """Logical tests for CODEMANIFEST viewer features."""

    def test_index_page_contains_codemanifest_link_in_info_panel(self):
        html = index_page(graph_json_url="/api/graph")
        assert "codemanifest-link" in html
        assert "show_codemanifest" in html

    def test_index_page_codemanifest_error_messages(self):
        html = index_page(graph_json_url="/api/graph")
        assert "CODEMANIFEST not found" in html
        assert "Failed to load CODEMANIFEST" in html



class TestIndexPageCodemanifestIntegration:
    """Integration test for full CODEMANIFEST viewer markup."""

    def test_index_page_codemanifest_full_markup(self):
        """Verify all CODEMANIFEST viewer components are present in HTML."""
        html = index_page(graph_json_url="/api/graph")
        assert "function show_codemanifest" in html
        assert "#codemanifest-panel" in html
        assert "codemanifest-link" in html
        assert "/api/codemanifest" in html
        assert "CODEMANIFEST not found" in html


class TestIndexPageInfoFooter:
    """Tests for info panel footer with pinned CODEMANIFEST link."""

    def test_info_footer_html_element(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'id="info-footer"' in html

    def test_info_footer_after_info_div(self):
        html = index_page(graph_json_url="/api/graph")
        info_pos = html.index('id="info"')
        footer_pos = html.index('id="info-footer"')
        assert footer_pos > info_pos, "info-footer must come after info div"

    def test_info_footer_css_exists(self):
        html = index_page(graph_json_url="/api/graph")
        assert "#info-footer" in html
        assert "flex-shrink: 0" in html

    def test_info_footer_has_border_top(self):
        html = index_page(graph_json_url="/api/graph")
        footer_start = html.index("#info-footer")
        footer_end = html.index("}", footer_start) + 1
        footer_css = html[footer_start:footer_end]
        assert "border-top" in footer_css

    def test_codemanifest_link_rendered_in_footer_js(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'getElementById("info-footer")' in html

    def test_codemanifest_panel_fills_space_css(self):
        html = index_page(graph_json_url="/api/graph")
        panel_start = html.index("#codemanifest-panel")
        panel_end = html.index("}", panel_start) + 1
        panel_css = html[panel_start:panel_end]
        assert "left: 276px" in panel_css
        assert "right: 8px" in panel_css
        assert "max-width" not in panel_css

    def test_codemanifest_panel_adjusts_right_for_info_wrapper(self):
        html = index_page(graph_json_url="/api/graph")
        assert "getBoundingClientRect" in html
        assert "panel.style.right" in html


class TestYamlHighlighting:
    """Tests for YAML syntax highlighting in CODEMANIFEST panel."""

    def test_highlight_yaml_function_exists(self):
        html = index_page(graph_json_url="/api/graph")
        assert "function _highlight_yaml" in html

    def test_yaml_key_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-key" in html
        assert "#20d4bf" in html

    def test_yaml_comment_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-comment" in html

    def test_yaml_delimiter_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-delim" in html

    def test_yaml_bool_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-bool" in html

    def test_yaml_number_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-number" in html

    def test_yaml_literal_css(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-literal" in html

    def test_show_cm_panel_uses_highlight(self):
        html = index_page(graph_json_url="/api/graph")
        assert "_highlight_yaml(rawContent)" in html


class TestYamlHighlightingQuotedKeys:
    """Tests for YAML highlighting of keys in double quotes."""

    def test_regex_captures_quoted_keys(self):
        html = index_page(graph_json_url="/api/graph")
        assert '"[^"]*"' in html

    def test_regex_allows_quoted_and_plain_keys(self):
        html = index_page(graph_json_url="/api/graph")
        script_start = html.index("<script>", html.index("</head>"))
        script_end = html.index("</script>", script_start)
        script = html[script_start:script_end]
        regex_line = None
        for line in script.split("\n"):
            if "keyMatch" in line and "match" in line:
                regex_line = line
                break
        assert regex_line is not None
        assert "[\\w][\\w.-]*" in regex_line or "[\\\\w][\\\\w.-]*" in regex_line


class TestYamlHighlightingLiteralBlock:
    """Tests for YAML highlighting respecting literal blocks (|, >)."""

    def test_literal_indent_tracking_variable(self):
        html = index_page(graph_json_url="/api/graph")
        assert "literalIndent" in html

    def test_literal_indent_resets_to_negative(self):
        html = index_page(graph_json_url="/api/graph")
        assert "literalIndent = -1" in html

    def test_literal_indent_set_from_key_indent(self):
        html = index_page(graph_json_url="/api/graph")
        assert "literalIndent = keyIndent" in html

    def test_literal_block_continuation_skip(self):
        html = index_page(graph_json_url="/api/graph")
        assert "lineIndent > literalIndent" in html

    def test_literal_operator_match(self):
        html = index_page(graph_json_url="/api/graph")
        assert "litMatch" in html


class TestYamlHighlightingListKeys:
    """Tests for YAML highlighting of keys inside list items (- Key:)."""

    def test_regex_captures_dash_prefix(self):
        html = index_page(graph_json_url="/api/graph")
        assert "-\\\\s*" in html or "-\\s*" in html

    def test_list_key_regex_in_keymatch(self):
        html = index_page(graph_json_url="/api/graph")
        script_start = html.index("<script>", html.index("</head>"))
        script_end = html.index("</script>", script_start)
        script = html[script_start:script_end]
        regex_line = None
        for line in script.split("\n"):
            if "keyMatch" in line and "match" in line:
                regex_line = line
                break
        assert regex_line is not None
        assert "-\\s*" in regex_line or "-\\\\s*" in regex_line


class TestYamlHighlightingInlineCode:
    """Tests for YAML highlighting of inline code in backticks."""

    def test_yaml_code_css_class(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".yaml-code" in html

    def test_yaml_code_css_color(self):
        html = index_page(graph_json_url="/api/graph")
        code_start = html.index(".yaml-code")
        code_end = html.index("}", code_start) + 1
        code_css = html[code_start:code_end]
        assert "#a5f3fc" in code_css

    def test_backtick_replace_in_highlight(self):
        html = index_page(graph_json_url="/api/graph")
        assert "yaml-code" in html
        assert "`$1`" in html


class TestLineNumbers:
    """Tests for line numbers in CODEMANIFEST panel."""

    def test_line_numbers_css_class(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".line-numbers" in html

    def test_code_content_css_class(self):
        html = index_page(graph_json_url="/api/graph")
        assert ".code-content" in html

    def test_line_numbers_muted_color(self):
        html = index_page(graph_json_url="/api/graph")
        ln_start = html.index(".line-numbers")
        ln_end = html.index("}", ln_start) + 1
        ln_css = html[ln_start:ln_end]
        assert "var(--color-brand-muted)" in ln_css

    def test_line_numbers_user_select_none(self):
        html = index_page(graph_json_url="/api/graph")
        ln_start = html.index(".line-numbers")
        ln_end = html.index("}", ln_start) + 1
        ln_css = html[ln_start:ln_end]
        assert "user-select: none" in ln_css

    def test_line_numbers_border_right(self):
        html = index_page(graph_json_url="/api/graph")
        ln_start = html.index(".line-numbers")
        ln_end = html.index("}", ln_start) + 1
        ln_css = html[ln_start:ln_end]
        assert "border-right" in ln_css

    def test_show_cm_panel_generates_line_numbers(self):
        html = index_page(graph_json_url="/api/graph")
        assert 'class="line-numbers"' in html
        assert 'class="code-content"' in html


class TestCodemanifestFixedTitlebar:
    """Tests for fixed titlebar in CODEMANIFEST panel."""

    def test_panel_no_overflow_y_auto(self):
        html = index_page(graph_json_url="/api/graph")
        panel_start = html.index("#codemanifest-panel {")
        panel_end = html.index("}", panel_start) + 1
        panel_css = html[panel_start:panel_end]
        assert "overflow-y: auto" not in panel_css

    def test_panel_has_overflow_hidden(self):
        html = index_page(graph_json_url="/api/graph")
        panel_start = html.index("#codemanifest-panel {")
        panel_end = html.index("}", panel_start) + 1
        panel_css = html[panel_start:panel_end]
        assert "overflow: hidden" in panel_css

    def test_pre_has_overflow_y_auto(self):
        html = index_page(graph_json_url="/api/graph")
        pre_start = html.index("#codemanifest-panel pre {")
        pre_end = html.index("}", pre_start) + 1
        pre_css = html[pre_start:pre_end]
        assert "overflow-y: auto" in pre_css

    def test_pre_has_flex_one(self):
        html = index_page(graph_json_url="/api/graph")
        pre_start = html.index("#codemanifest-panel pre {")
        pre_end = html.index("}", pre_start) + 1
        pre_css = html[pre_start:pre_end]
        assert "flex: 1" in pre_css
