"""Tests for load_codemanifest."""

import goga_tool_viewer.loader.codemanifest as codemanifest_mod
import pytest
from goga_tool_viewer.loader import load_codemanifest


def _monkeypatch_file(tmp_path, mod):
    """Set __file__ so that base (parent.parent.parent) equals tmp_path."""
    original = mod.__file__
    mod.__file__ = str(tmp_path / "a" / "b" / "codemanifest.py")
    return original


class TestLoadCodemanifestContract:
    """Contract tests for load_codemanifest facade and signature."""

    def test_load_codemanifest_callable(self):
        """load_codemanifest is importable and callable with one argument."""
        assert callable(load_codemanifest)

    def test_load_codemanifest_signature(self, tmp_path):
        """load_codemanifest returns a str for a valid path."""
        cell_dir = tmp_path / "goga_tool_viewer" / "parser"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  test: value\n", encoding="utf-8")

        original = _monkeypatch_file(tmp_path, codemanifest_mod)
        try:
            result = load_codemanifest("goga_tool_viewer/parser")
            assert isinstance(result, str)
            assert result == "Usages:\n  test: value\n"
        finally:
            codemanifest_mod.__file__ = original


class TestLoadCodemanifestLogic:
    """Logical tests for load_codemanifest behaviour."""

    def test_load_codemanifest_reads_existing_file(self, tmp_path):
        """Reads CODEMANIFEST content from a real cell directory."""
        cell_dir = tmp_path / "goga_tool_viewer" / "parser"
        cell_dir.mkdir(parents=True)
        (cell_dir / "CODEMANIFEST").write_text("Usages:\n  test: value\n", encoding="utf-8")

        original = _monkeypatch_file(tmp_path, codemanifest_mod)
        try:
            result = load_codemanifest("goga_tool_viewer/parser")
            assert result == "Usages:\n  test: value\n"
        finally:
            codemanifest_mod.__file__ = original

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
        original = _monkeypatch_file(tmp_path, codemanifest_mod)
        try:
            with pytest.raises(FileNotFoundError):
                load_codemanifest("nonexistent/cell")
        finally:
            codemanifest_mod.__file__ = original

    def test_load_codemanifest_empty_path(self, tmp_path):
        """Raises FileNotFoundError for empty cell_path."""
        original = _monkeypatch_file(tmp_path, codemanifest_mod)
        try:
            with pytest.raises(FileNotFoundError):
                load_codemanifest("")
        finally:
            codemanifest_mod.__file__ = original

    def test_load_codemanifest_path_traversal_encoded(self, tmp_path):
        """Rejects encoded path traversal attempts."""
        original = _monkeypatch_file(tmp_path, codemanifest_mod)
        try:
            with pytest.raises((ValueError, FileNotFoundError)):
                load_codemanifest("cell/..%2F..%2Fsecret")
        finally:
            codemanifest_mod.__file__ = original
