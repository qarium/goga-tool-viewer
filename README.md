# goga-tool-viewer

Interactive dependency graph viewer for the [goga](https://github.com/qarium/goga) ecosystem.

Visualizes cell dependency graphs as a single-page web application with hierarchical layout and click-to-inspect details. Includes a CODEMANIFEST viewer — click the "CODEMANIFEST" link in the info panel to view the raw YAML manifest for any cell.

**Documentation:** [qarium.github.io/goga-tool-viewer](https://qarium.github.io/goga-tool-viewer/)

## Installation

```bash
pip install goga-tool-viewer
```

Requires Python 3.10+. No external runtime dependencies.

## Quick Start

Run from a JSON file:

```bash
goga tool viewer path/to/schema.json
```

Or pipe data via stdin:

```bash
goga schema | goga tool viewer
```

The tool prints a URL (e.g. `http://localhost:PORT`). Open it in a browser to see the interactive graph.

## Web API

Once started, the HTTP server exposes:

| Endpoint                          | Description                                                      |
|-----------------------------------|------------------------------------------------------------------|
| `GET /`                           | Single-page application with the graph viewer                    |
| `GET /api/graph`                  | JSON data for the dependency graph                               |
| `GET /api/codemanifest?cell=<path>` | CODEMANIFEST file content for a cell (text/plain, 200/400/404) |

## Integration

`goga-tool-viewer` is designed as a tool plugin for the goga CLI:

```bash
goga tool viewer data.json
```

It can also be used as a Python library:

```python
from goga_tool_viewer import main

main(["path/to/data.json"])  # from file
main([])                     # from stdin
```

## Development

Set up the environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Run tests:

```bash
pytest
```

Lint and format:

```bash
ruff check
ruff format
```
