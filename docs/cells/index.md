# Cells

goga-tool-viewer consists of 7 cells — self-contained modules with clear API boundaries.

## Overview

| Cell | Description |
|------|-------------|
| [`goga_tool_viewer`](models.md) | CLI facade, tool entry point |
| [`models`](models.md) | Data structures for representing cells from JSON |
| [`parser`](parser.md) | JSON parsing into CellGraph |
| [`frontend`](frontend.md) | SPA page generation with dark theme |
| [`server`](server.md) | HTTP server for SPA, static files, and API |
| [`loader`](loader.md) | Project file loader (CODEMANIFEST, usage files) |
| [`port_finder`](port-finder.md) | Free TCP port discovery |

## Dependency Graph

```
port_finder ──┐
models ───────┤
frontend ─────┤
              ├──→ server ──→ goga_tool_viewer (CLI)
parser ───────┤
loader ───────┘
     │
     └──→ models
```

Detailed descriptions of each cell are available via the links above.