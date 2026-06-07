from goga_tool_viewer.frontend.pages import _STATIC


def _read_js():
    return (_STATIC / "app.js").read_text(encoding="utf-8")


class TestHighlightYamlUsageLinks:
    """Tests for _highlight_yaml turning .md paths into clickable usage links."""

    def test_usages_md_path_becomes_link(self):
        js = _read_js()
        assert 'class="usage-link"' in js
        assert "data-path" in js

    def test_usage_link_click_uses_delegation(self):
        js = _read_js()
        idx = js.index("_show_cm_panel")
        snippet = js[idx : js.index("function _highlight_type_line")]

        assert ".code-content" in snippet
        assert ".closest" in snippet

    def test_no_direct_listener_on_usage_link(self):
        js = _read_js()
        idx = js.index("_show_cm_panel")
        snippet = js[idx : js.index("function _highlight_type_line")]

        assert "querySelectorAll('.usage-link')" not in snippet
