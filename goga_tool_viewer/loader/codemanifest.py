"""CODEMANIFEST file loader."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_codemanifest(cell_path: str) -> str:
    """Load CODEMANIFEST file content for a given cell path.

    Safely reads the CODEMANIFEST file located at the given relative
    cell path. Performs path traversal protection at two levels:
    string-level validation and resolve-based verification.

    Args:
        cell_path: Relative path to a cell directory
            (e.g. "goga_tool_viewer/parser").

    Returns:
        Text content of the CODEMANIFEST file as a string.

    Raises:
        ValueError: If the path contains ".." or starts with "/",
            or if the resolved path escapes the project root.
        FileNotFoundError: If the CODEMANIFEST file does not exist.
    """
    if ".." in cell_path:
        raise ValueError("path traversal detected")

    if cell_path.startswith("/"):
        raise ValueError("absolute path not allowed")

    base = Path(__file__).resolve().parent.parent.parent
    target = (base / cell_path / "CODEMANIFEST").resolve()

    if not target.is_relative_to(base):
        raise ValueError("path escapes project root")

    logger.debug(
        "loading codemanifest",
        extra={"cell_path": cell_path, "target": str(target)},
    )

    content = target.read_text(encoding="utf-8")

    return content
