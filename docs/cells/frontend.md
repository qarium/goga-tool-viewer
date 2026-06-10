# Frontend

Cell `goga_tool_viewer/frontend` — SPA application with dark theme for rendering the cell dependency graph.

## Function index_page

```python
index_page(graph_json_url: str) -> str
```

Generates an SPA HTML page with dark theme. Links to external CSS (`/static/style.css`) and JS (`/static/app.js`). Includes header, sidebar, graph, info panel, CODEMANIFEST panel, and footer.

- `graph_json_url` — API endpoint URL (typically `/api/graph`)
- Returns the complete HTML page as a string

## SPA Structure

The SPA consists of an HTML file with links to external CSS and JS. No build step. Static assets are served from `frontend/static/`:

| File | Purpose |
|------|---------|
| `style.css` | All CSS styles |
| `app.js` | All JS logic |
| `logo.png`, `favicon.png` | Brand assets |
| `goga.svg` | Logo SVG |
| `icon-*.svg` | Section, tree, and action icons |
| `cytoscape.min.js` | Graph visualization library |
| `dagre.min.js`, `cytoscape-dagre.min.js` | Hierarchical layout |
| `marked.min.js` | Markdown rendering |

## Layout

- **Header** — fixed, backdrop-blur, logo "QArium" (QA in teal, rium in white), contact icons (Telegram, GitHub, Email)
- **Sidebar (260px, left)** — OS-window style, fully expanded cell tree, "Show all" button, custom scrollbar
- **Graph (center)** — Cytoscape.js with dagre layout
- **CODEMANIFEST Panel (center overlay)** — YAML with syntax highlighting, line numbers, type highlighting. Opens between sidebar and info panel
- **Info Panel (right)** — OS-window style, sections: Name, Description, Types (clickable links), Usages (clickable links), Consumers, Dependencies. Footer link to CODEMANIFEST
- **Footer** — logo, copyright

## Dark Theme

Design tokens:

| Token | Value | Purpose |
|-------|-------|---------|
| `--color-brand-bg` | `#0a0e1a` | Main background |
| `--color-brand-card` | `#121830` | Cards, panels |
| `--color-brand-teal` | `#20d4bf` | Accents, highlights |
| `--color-brand-blue` | `#3882f6` | Secondary accent |
| `--color-brand-text` | `#fff` | Main text |
| `--color-brand-muted` | `#a0aec0` | Muted text |

## JS Functions

| Function | Description |
|----------|-------------|
| `render_graph(container_id, graph)` | Initializes Cytoscape, creates nodes and edges with dagre layout |
| `highlight_cell(cell_name, cy_instance)` | Highlights cell and connections, dims the rest |
| `apply_filter(cy_instance)` | Filters graph by selected cells (union) |
| `reset_filter(cy_instance)` | Clears selection, shows all elements |
| `show_cell_info(cell_name, graph)` | Shows info panel with cell details |
| `show_codemanifest(cell_name, graph, highlightType)` | Opens CODEMANIFEST panel with YAML highlighting |
| `render_tree(container_id, graph, cy_instance)` | Builds cell tree in sidebar |
| `_init_custom_scroll(wrapper)` | Custom scrollbar with drag support |
| `_highlight_yaml(text)` | YAML syntax highlighting (keys, comments, booleans, numbers, inline code) |
| `_highlight_type_line(typeName)` | Highlights type declaration line in CODEMANIFEST panel |
| `_navigate_to_type(typeName, cellName, graph)` | Opens CODEMANIFEST and highlights type |
| `_open_usage(mdPath)` | Loads usage `.md` file and shows in modal |
| `_show_usage_modal(title, markdownContent)` | Shows usage modal with rendered Markdown |

## Graph Data Structure

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

## Usage Modal

Clicking a usage link opens a centered modal with rendered Markdown content. Closes via overlay click, × button, or Escape key. Custom scrollbar for overflow.

## Visual Styles

- Nodes: rounded rectangles, gradient background (`#0f172a` → `#162040`), teal border, glow shadow
- Edges: directed arrows, teal semi-transparent, highlight on selection
- Fade-in animation on graph load
