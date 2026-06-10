# Server

Cell `goga_tool_viewer/server` — HTTP server for serving the SPA, static files, and API.

Depends on: [models](models.md), [parser](parser.md), [frontend](frontend.md), [port-finder](port-finder.md), [loader](loader.md)

## Types

### GraphServer

```python
GraphServer(graph: CellGraph, port: int, static_dir: Path | None = None)
```

HTTP server serving the SPA, static assets, and API routes.

- `graph` — project graph to serve via API
- `port` — port number to listen on
- `static_dir` — directory with static files. Defaults to `frontend/static`

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `port` | `int` | TCP port number the server listens on |

#### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `start()` | `void` | Starts the HTTP server. Blocking call |
| `stop()` | `void` | Stops the HTTP server and closes the socket |
| `url()` | `str` | Returns the full server URL |
| `get_codemanifest(cell_path)` | `str` | Returns CODEMANIFEST content for a cell. 404 if not found |

#### Routes

| Route | Description |
|-------|-------------|
| `GET /` | SPA page (HTML) |
| `GET /static/*` | Static files (CSS, JS, images) |
| `GET /api/graph` | Graph data (JSON, CellGraph format) |
| `GET /api/codemanifest?cell=<path>` | CODEMANIFEST content (text/plain, no-cache) |
| `GET /api/usage?path=<path>` | Usage `.md` file content (text/plain, no-cache) |

### run_server

```python
run_server(json_path: str | None) -> None
```

Server entry point: loads JSON, finds a port, starts `GraphServer`. Handles `Ctrl+C` for graceful shutdown.

- `json_path` — path to the JSON file, or `None` to read from stdin

## Usage

```python
from goga_tool_viewer.server import run_server

# From file
run_server("path/to/data.json")

# From stdin
run_server(None)
```

## Implementation

Uses `http.server` from the Python standard library. Custom handler inherits from `BaseHTTPRequestHandler`. MIME types: `text/html`, `application/json`, `text/css`, `application/javascript`, `image/png`, `image/svg+xml`. Uses `load_codemanifest` and `load_usage_file` from the loader cell for API routes.