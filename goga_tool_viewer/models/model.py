"""Data models for cell dependency graphs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class DependencyInfo:
    """Represent a directed dependency edge between two cells.

    Args:
        from_cell: Name of the source cell.
        to_cell: Name of the target cell.
        types: List of dependency type labels.
        usages: List of usage descriptors.
    """

    from_cell: str
    to_cell: str
    types: list[str] = field(default_factory=list)
    usages: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class CellData:
    """Represent a single cell with metadata, children, and dependencies.

    Args:
        name: Unique cell identifier.
        description: Human-readable cell description.
        types: List of cell type labels.
        usages: List of usage descriptors.
        children: Nested child cells.
        dependencies: Outgoing dependency edges.
    """

    name: str
    description: str
    types: list[str] = field(default_factory=list)
    usages: list[str] = field(default_factory=list)
    children: list[CellData] = field(default_factory=list)
    dependencies: list[DependencyInfo] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class CellGraph:
    """Root container holding all cells and their dependency edges.

    Args:
        cells: Flat list of all cells in the graph.
        edges: Flat list of all dependency edges.
        project_root: Absolute path to the project root directory.
    """

    cells: list[CellData] = field(default_factory=list)
    edges: list[DependencyInfo] = field(default_factory=list)
    project_root: str = ""
