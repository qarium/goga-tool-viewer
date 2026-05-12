from dataclasses import FrozenInstanceError

import pytest
from goga_tool_viewer.models import CellData, CellGraph, DependencyInfo


class TestDependencyInfo:
    def test_create_with_all_fields(self):
        d = DependencyInfo(from_cell="a", to_cell="b", types=["T"], usages=["u"])
        assert d.from_cell == "a"
        assert d.to_cell == "b"
        assert d.types == ["T"]
        assert d.usages == ["u"]

    def test_default_empty_collections(self):
        d = DependencyInfo(from_cell="a", to_cell="b")
        assert d.types == []
        assert d.usages == []

    def test_immutable(self):
        d = DependencyInfo(from_cell="a", to_cell="b")
        with pytest.raises(FrozenInstanceError):
            d.from_cell = "other"

    def test_facade_import(self):
        from goga_tool_viewer.models import DependencyInfo as FacadeDep  # noqa: PLC0415

        assert FacadeDep is DependencyInfo


class TestCellData:
    def test_create_with_all_fields(self):
        c = CellData(
            name="x",
            description="desc",
            types=["T"],
            usages=["u"],
            children=[],
            dependencies=[],
        )
        assert c.name == "x"
        assert c.description == "desc"

    def test_create_minimal(self):
        c = CellData(name="root", description="desc")
        assert c.name == "root"

    def test_with_children(self):
        child = CellData(name="child", description="c")
        parent = CellData(name="parent", description="p", children=[child])
        assert parent.children[0].name == "child"
        assert parent.children[0] is child

    def test_immutable(self):
        c = CellData(name="x", description="desc")
        with pytest.raises(FrozenInstanceError):
            c.name = "other"

    def test_facade_import(self):
        from goga_tool_viewer.models import CellData as FacadeCell  # noqa: PLC0415

        assert FacadeCell is CellData


class TestCellGraph:
    def test_create_empty(self):
        g = CellGraph()
        assert g.cells == []
        assert g.edges == []

    def test_create_with_data(self):
        g = CellGraph(cells=[], edges=[])
        assert g.cells == []
        assert g.edges == []

    def test_facade_import(self):
        from goga_tool_viewer.models import CellGraph as FacadeGraph  # noqa: PLC0415

        assert FacadeGraph is CellGraph
