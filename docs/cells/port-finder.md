# Port Finder

Cell `goga_tool_viewer/server/port_finder` — free TCP port discovery on localhost.

## Function find_free_port

```python
find_free_port(min_port: int, max_port: int) -> int
```

Finds a free TCP port in the range `[min_port, max_port]`. Picks a random port from the range and checks availability via socket.

- `min_port` — lower bound of the range (recommended: 49152)
- `max_port` — upper bound of the range (recommended: 65535)
- Returns a free port number
- Raises `OSError` if all ports are occupied

## Usage

```python
from goga_tool_viewer.server.port_finder import find_free_port

port = find_free_port(49152, 65535)
print(f"Free port: {port}")
```

## Recommended Range

49152–65535 — ephemeral port range, recommended for dynamic allocation.