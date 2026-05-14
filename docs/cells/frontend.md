# Frontend

Cell `goga_tool_viewer/frontend` — SPA application for rendering the cell dependency graph.

## Function index_page

```python
index_page(graph_json_url: str) -> str
```

Generates an SPA HTML page. Includes styles, markup, and a JS script for loading data from `graph_json_url`.

- `graph_json_url` — API endpoint URL (typically `/api/graph`)
- Returns the complete HTML page as a string

## SPA Structure

The SPA consists of a single HTML file with embedded CSS and JS. No build step — JS libraries are inlined from `static/`.

### Layout

- **Graph container** — 80% width, left side
- **Info panel** — 20% width, right side
- Graph fills the full viewport height
- Panel scrolls on overflow

### Cytoscape.js

[Cytoscape.js](https://js.cytoscape.org/) is used for visualization with the dagre layout for hierarchical display. The library is inlined into HTML from `static/cytoscape.min.js`.

### JS Functions

The SPA contains inline JS functions:

| Function | Description |
|----------|-------------|
| `render_graph(container_id, graph)` | Initializes Cytoscape.js, creates nodes and edges |
| `highlight_cell(cell_name)` | Highlights the cell and all its connections, dims the rest |
| `show_cell_info(cell_name, graph)` | Shows panel with cell info |

### Graph Data Structure

Received from the `/api/graph` API:

```json
{
  "cells": [
    {
      "name": "...",
      "description": "...",
      "types": [],
      "usages": [],
      "children": [],
      "dependencies": [{ "from_cell": "", "to_cell": "", "types": [], "usages": [] }]
    }
  ],
  "edges": [{ "from_cell": "", "to_cell": "", "types": [], "usages": [] }]
}
```

## Visual Styles

- Nodes: rounded rectangles with cell name
- Edges: directed arrows
- Highlight: yellow for selected node, gray for the rest