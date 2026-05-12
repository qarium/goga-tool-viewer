# goga_viewer.models — data models

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class DependencyInfo:
    from_cell: str
    to_cell: str
    types: list[str] = field(default_factory=list)
    usages: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class CellData:
    name: str
    description: str
    types: list[str] = field(default_factory=list)
    usages: list[str] = field(default_factory=list)
    children: list[CellData] = field(default_factory=list)
    dependencies: list[DependencyInfo] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class CellGraph:
    cells: list[CellData] = field(default_factory=list)
    edges: list[DependencyInfo] = field(default_factory=list)
