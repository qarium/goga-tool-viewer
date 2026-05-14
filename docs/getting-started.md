# Getting Started

## Installation

goga-tool-viewer is part of the goga ecosystem and is installed as a plugin tool.

## Running

### Via pipe

```bash
goga schema | goga tool viewer
```

### From file

```bash
goga tool viewer path/to/schema.json
```

Outputs the server URL: `http://localhost:PORT`

### Via Python API

```python
from goga_tool_viewer import main

main(["path/to/data.json"])  # from file
main([])                     # from stdin
```

## Web API

After launch, an HTTP server is available with two endpoints:

| Endpoint | Description |
|-----------|------------|
| `GET /` | SPA page with interactive graph |
| `GET /api/graph` | JSON with graph data (CellGraph format) |

## Interface

A web page opens with an interactive dependency graph:

- **Graph** (80% width) — nodes represent cells, edges represent dependencies
- **Info panel** (20% width) — details of the selected cell: types, consumers, dependencies

Clicking a cell highlights its connections; remaining nodes are dimmed.