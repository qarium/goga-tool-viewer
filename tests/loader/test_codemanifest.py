"""Tests for load_codemanifest."""

import pytest
from goga_tool_viewer.loader import load_codemanifest


class TestLoadCodemanifestContract:
    """Contract tests for load_codemanifest facade and signature."""

    def test_load_codemanifest_callable(self):
        """load_codemanifest is importable and callable with one argument."""
        assert callable(load_codemanifest)

    def test_load_codemanifest_signature(self, tmp_path):
        """load_codemanifest returns a str for a valid path with project_root."""
        cell_dir = tmp_path / "goga_tool_viewer" / "parser"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  test: value\n", encoding="utf-8")

        result = load_codemanifest("goga_tool_viewer/parser", project_root=str(tmp_path))
        assert isinstance(result, str)
        assert result == "Usages:\n  test: value\n"


class TestLoadCodemanifestLogic:
    """Logical tests for load_codemanifest behaviour."""

    def test_load_codemanifest_reads_existing_file(self, tmp_path):
        """Reads CODEMANIFEST content from a real cell directory."""
        cell_dir = tmp_path / "goga_tool_viewer" / "parser"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  test: value\n", encoding="utf-8")

        result = load_codemanifest("goga_tool_viewer/parser", project_root=str(tmp_path))
        assert result == "Usages:\n  test: value\n"

    def test_load_codemanifest_rejects_path_traversal(self):
        """Rejects paths containing '..' with ValueError."""
        with pytest.raises(ValueError, match="path traversal"):
            load_codemanifest("../../etc/passwd")

    def test_load_codemanifest_rejects_absolute_path(self):
        """Rejects absolute paths with ValueError."""
        with pytest.raises(ValueError, match="absolute path"):
            load_codemanifest("/etc/passwd")

    def test_load_codemanifest_raises_on_missing_file(self, tmp_path):
        """Raises FileNotFoundError when CODEMANIFEST does not exist."""
        with pytest.raises(FileNotFoundError):
            load_codemanifest("nonexistent/cell", project_root=str(tmp_path))

    def test_load_codemanifest_empty_path(self, tmp_path):
        """Raises FileNotFoundError for empty cell_path."""
        with pytest.raises(FileNotFoundError):
            load_codemanifest("", project_root=str(tmp_path))

    def test_load_codemanifest_path_traversal_encoded(self, tmp_path):
        """Rejects encoded path traversal attempts."""
        with pytest.raises((ValueError, FileNotFoundError)):
            load_codemanifest("cell/..%2F..%2Fsecret", project_root=str(tmp_path))

    def test_load_codemanifest_uses_project_root(self, tmp_path):
        """Finds CODEMANIFEST in the specified project_root, not package dir."""
        cell_dir = tmp_path / "external_project" / "core"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  external: true\n", encoding="utf-8")

        result = load_codemanifest("external_project/core", project_root=str(tmp_path))
        assert "external: true" in result

    def test_load_codemanifest_fallback_to_cwd(self, tmp_path, monkeypatch):
        """Falls back to cwd when project_root is empty."""
        cell_dir = tmp_path / "fallback_cell"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  fallback: yes\n", encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        result = load_codemanifest("fallback_cell")
        assert "fallback: yes" in result


class TestLoadCodemanifestIntegration:
    """Integration tests using the real project filesystem."""

    def test_load_codemanifest_real_project_file(self):
        """Load a real CODEMANIFEST from the project and verify content."""
        result = load_codemanifest("goga_tool_viewer/models")
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Usages:" in result or "Annotations:" in result
