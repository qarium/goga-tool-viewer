from __future__ import annotations

from textwrap import dedent

import pytest
from goga_tool_viewer.models import CellData, CellGraph, DependencyInfo

SAMPLE_JSON = dedent("""\
    [{
        "cell": "root",
        "description": "Root cell",
        "types": [],
        "usages": [],
        "children": [{
            "cell": "root/child",
            "description": "Child cell",
            "types": ["TypeB"],
            "usages": [],
            "children": [],
            "dependencies": {
                "root/dep": {"types": ["TypeA"], "usages": ["usage1"]}
            }
        }],
        "dependencies": {}
    }]
""")


@pytest.fixture
def sample_json() -> str:
    return SAMPLE_JSON


@pytest.fixture
def test_graph() -> CellGraph:
    return CellGraph(
        cells=[
            CellData(name="root", description="Root cell", types=[], usages=[], children=[], dependencies=[]),
            CellData(
                name="root/child",
                description="Child cell",
                types=["TypeB"],
                usages=[],
                children=[],
                dependencies=[
                    DependencyInfo(
                        from_cell="root/child",
                        to_cell="root/dep",
                        types=["TypeA"],
                        usages=["usage1"],
                    )
                ],
            ),
        ],
        edges=[
            DependencyInfo(
                from_cell="root/child",
                to_cell="root/dep",
                types=["TypeA"],
                usages=["usage1"],
            )
        ],
    )


@pytest.fixture
def empty_graph() -> CellGraph:
    return CellGraph()
