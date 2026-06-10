# Architecture

goga-tool-viewer is built on a cell architecture with clear separation of concerns.

## Dependency Graph

```
goga_tool_viewer (CLI)
├── server
│   ├── models
│   ├── parser → models
│   ├── frontend
│   ├── loader
│   └── port_finder
├── parser → models
└── frontend
```

## Data Flow

1. **CLI** (`main`) receives argv: path to JSON or pipe from stdin
2. **Server** (`run_server`) loads JSON, finds a free port, starts HTTP server
3. **Parser** converts JSON into `CellGraph`
4. **Models** define data structures: `CellData`, `DependencyInfo`, `CellGraph`
5. **Frontend** generates SPA page with Cytoscape.js and dark theme
6. **Loader** reads CODEMANIFEST and usage files from the filesystem
7. **Port Finder** finds a free TCP port

## Cells

| Cell | Purpose | Dependencies |
|------|---------|-------------|
| `goga_tool_viewer` | CLI facade, entry point | server, frontend |
| `server` | HTTP server, routing | models, parser, frontend, loader, port_finder |
| `parser` | JSON to model parsing | models |
| `models` | Data structures (dataclasses) | — |
| `frontend` | SPA generation (HTML+CSS+JS) | — |
| `loader` | Project file loading | — |
| `port_finder` | Free TCP port discovery | — |

## Principles

- **Python 3.10+** — no external dependencies, stdlib only
- **Relative imports** — strictly within the package
- **Dataclasses** — immutable models with `frozen=True`
- **SPA without build** — external CSS and JS files served from static/