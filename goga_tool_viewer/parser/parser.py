"""Parse JSON cell dependency data into CellGraph models."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ..models import CellData, CellGraph, DependencyInfo


def _parse_cell(item: dict) -> tuple[CellData, list[CellData], list[DependencyInfo]]:
    """Parse a single cell dict into its data, descendants, and edges.

    Recursively parses children, returning this cell, all descendant cells, and all edges.

    Args:
        item: Raw cell dictionary from JSON input.

    Returns:
        A tuple of (CellData, list of all descendant CellData, list of all DependencyInfo).
    """
    if "cell" not in item:
        raise ValueError("Each cell item must have a 'cell' key")

    deps = []

    for target, info in item.get("dependencies", {}).items():
        deps.append(
            DependencyInfo(
                from_cell=item["cell"],
                to_cell=target,
                types=info.get("types", []),
                usages=info.get("usages", []),
            )
        )

    children: list[CellData] = []
    all_descendants: list[CellData] = []
    all_edges: list[DependencyInfo] = list(deps)

    for child_item in item.get("children", []):
        child_cell, child_descendants, child_edges = _parse_cell(child_item)
        children.append(child_cell)
        all_descendants.append(child_cell)
        all_descendants.extend(child_descendants)
        all_edges.extend(child_edges)

    cell_data = CellData(
        name=item["cell"],
        description=item.get("description", ""),
        types=item.get("types", []),
        usages=item.get("usages", []),
        children=children,
        dependencies=deps,
    )
    return cell_data, all_descendants, all_edges


def _collect_all(item: dict, cells: list[CellData], edges: list[DependencyInfo]) -> None:
    """Recursively collect all cells and edges from a cell dict tree.

    Args:
        item: Raw cell dictionary from JSON input.
        cells: Accumulator list for all parsed CellData instances.
        edges: Accumulator list for all parsed DependencyInfo instances.
    """
    cell_data, descendants, cell_edges = _parse_cell(item)
    cells.append(cell_data)
    cells.extend(descendants)
    edges.extend(cell_edges)


def parse_json(json_str: str, project_root: str = "") -> CellGraph:
    """Parse JSON string into CellGraph."""
    data = json.loads(json_str)

    if not isinstance(data, list):
        raise ValueError("Expected a JSON array at the top level")

    cells: list[CellData] = []
    edges: list[DependencyInfo] = []

    for item in data:
        _collect_all(item, cells, edges)

    return CellGraph(cells=cells, edges=edges, project_root=project_root)


def load_json_file(path: str) -> CellGraph:
    """Load JSON from file path into CellGraph."""
    json_str = Path(path).read_text(encoding="utf-8")
    project_root = str(Path(path).resolve().parent)
    return parse_json(json_str, project_root=project_root)


def load_json_stdin() -> CellGraph:
    """Load JSON from stdin into CellGraph."""
    json_str = sys.stdin.read()
    return parse_json(json_str, project_root=str(Path.cwd()))
