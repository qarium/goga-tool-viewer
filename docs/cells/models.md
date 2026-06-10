# Models

Cell `goga_tool_viewer/models` — data structures for representing cells from JSON.

## Types

### DependencyInfo

Describes a single dependency between two cells.

| Property | Type | Description |
|----------|------|-------------|
| `from_cell` | `str` | Path to the source cell |
| `to_cell` | `str` | Path to the cell being depended on |
| `types` | `list[str]` | List of imported types |
| `usages` | `list[str]` | List of imported usages |

### CellData

Complete representation of a single cell from JSON.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Cell name (the `"cell"` field in JSON) |
| `description` | `str` | Cell description |
| `types` | `list[str]` | Types the cell provides |
| `usages` | `list[str]` | Usages the cell provides |
| `children` | `list[CellData]` | Nested cells (children) |
| `dependencies` | `list[DependencyInfo]` | Dependencies on other cells |

### CellGraph

Complete project graph — all cells and all dependency edges.

| Property | Type | Description |
|----------|------|-------------|
| `cells` | `list[CellData]` | Flat list of all cells (including nested) |
| `edges` | `list[DependencyInfo]` | Flat list of all dependency edges |
| `project_root` | `str` | Absolute path to the project root directory |

## JSON Format

A cell JSON object contains the following fields:

```json
{
  "cell": "name",
  "description": "...",
  "types": ["TypeA", "TypeB"],
  "usages": ["usage_one"],
  "children": [...],
  "dependencies": {
    "path/to/cell": { "types": ["TypeA"], "usages": [] }
  }
}
```

Dependencies in JSON are a dict where the key is the cell path and the value is `{types: [], usages: []}`. Each key is converted to a `DependencyInfo` during parsing.

## Implementation

- Dataclasses with `frozen=True` for immutability
- `kw_only=True` on all classes
- Structures with empty defaults