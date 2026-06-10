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

After launch, an HTTP server is available with the following endpoints:

| Endpoint | Description |
|-----------|------------|
| `GET /` | SPA page with interactive graph |
| `GET /static/*` | Static files (CSS, JS, images) |
| `GET /api/graph` | JSON with graph data (CellGraph format) |
| `GET /api/codemanifest?cell=<path>` | CODEMANIFEST content for a cell |
| `GET /api/usage?path=<path>` | Usage `.md` file content |

## Interface

A web page opens with an interactive dependency graph in dark theme:

- **Sidebar** (260px left) — fully expanded cell tree with click-to-filter
- **Graph** (center) — nodes represent cells, edges represent dependencies
- **Info panel** (right) — details of the selected cell: types, usages, consumers, dependencies
- **CODEMANIFEST panel** (center overlay) — YAML view with syntax highlighting

Clicking a cell highlights its connections; remaining nodes are dimmed. Type links navigate to CODEMANIFEST. Usage links open a modal with rendered Markdown.