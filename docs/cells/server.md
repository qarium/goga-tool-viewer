# Server

Cell `goga_tool_viewer/server` — HTTP server for serving the SPA and graph API.

Depends on: [models](models.md), [parser](parser.md), [frontend](frontend.md), [port-finder](port-finder.md)

## Types

### GraphServer

```python
GraphServer(graph: CellGraph, port: int)
```

HTTP server serving the SPA and API.

- `graph` — project graph to serve via API
- `port` — port number to listen on

#### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `start()` | `void` | Starts the HTTP server. Blocking call |
| `url()` | `str` | Returns the full server URL |

#### Routes

| Route | Description |
|-------|-------------|
| `GET /` | SPA page (HTML) |
| `GET /api/graph` | Graph data (JSON, CellGraph format) |

### run_server

```python
run_server(json_path: str | None) -> None
```

Server entry point: loads JSON, finds a port, starts `GraphServer`.

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

Uses `http.server` from the Python standard library. Custom handler inherits from `BaseHTTPRequestHandler`. MIME types: `text/html` for HTML, `application/json` for JSON.