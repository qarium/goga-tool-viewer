"""CODEMANIFEST and usage file loader."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_codemanifest(cell_path: str, project_root: str = "") -> str:
    """Load CODEMANIFEST file content for a given cell path.

    Safely reads the CODEMANIFEST file located at the given relative
    cell path. Performs path traversal protection at two levels:
    string-level validation and resolve-based verification.

    Args:
        cell_path: Relative path to a cell directory
            (e.g. "goga_tool_viewer/parser").
        project_root: Absolute path to the project root directory.
            When empty, falls back to the current working directory.

    Returns:
        Text content of the CODEMANIFEST file as a string.

    Raises:
        ValueError: If the path contains ".." or starts with "/",
            or if the resolved path escapes the project root.
        FileNotFoundError: If the CODEMANIFEST file does not exist.
    """
    if any(part == ".." for part in cell_path.split("/")):
        raise ValueError("path traversal detected")

    if cell_path.startswith("/"):
        raise ValueError("absolute path not allowed")

    base = Path(project_root).resolve() if project_root else Path.cwd()
    target = (base / cell_path / "CODEMANIFEST").resolve()

    if not target.is_relative_to(base):
        raise ValueError("path escapes project root")

    logger.debug(
        "loading codemanifest",
        extra={"cell_path": cell_path, "target": str(target)},
    )

    content = target.read_text(encoding="utf-8")

    return content


def load_usage_file(usage_path: str, project_root: str = "") -> str:
    """Load usage .md file content for a given relative path.

    Safely reads a Markdown usage file located at the given relative
    path from the project root. Performs path traversal protection
    at two levels: string-level validation and resolve-based verification.

    Args:
        usage_path: Relative path to a usage .md file from project root
            (e.g. ".goga/usages/conventions.md" or
            "goga_tool_viewer/parser/.usages/loading.md").
        project_root: Absolute path to the project root directory.
            When empty, falls back to the current working directory.

    Returns:
        Text content of the usage file as a string.

    Raises:
        ValueError: If the path contains "..", starts with "/",
            escapes the project root, or does not have .md extension.
        FileNotFoundError: If the usage file does not exist.
    """
    if any(part == ".." for part in usage_path.split("/")):
        raise ValueError("path traversal detected")

    if usage_path.startswith("/"):
        raise ValueError("absolute path not allowed")

    if not usage_path.endswith(".md"):
        raise ValueError("only .md files are allowed")

    base = Path(project_root).resolve() if project_root else Path.cwd()
    target = (base / usage_path).resolve()

    if not target.is_relative_to(base):
        raise ValueError("path escapes project root")

    logger.debug(
        "loading usage file",
        extra={"usage_path": usage_path, "target": str(target)},
    )

    content = target.read_text(encoding="utf-8")

    return content
