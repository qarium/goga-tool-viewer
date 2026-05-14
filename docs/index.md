# Goga Tool Viewer

Interactive dependency graph viewer for the [goga](https://github.com/qarium/goga) ecosystem.

Visualizes cell dependency graphs as a single-page web application with hierarchical layout and click-to-inspect details.

## Features

- Interactive cell dependency graph
- Hierarchical layout (Dagre)
- Clickable nodes with detailed information
- Highlighted connections for selected cells
- File or pipe input

## Quick Start

```bash
# From file
goga tool viewer path/to/schema.json

# Via pipe
goga schema | goga tool viewer
```

After launch, an HTTP server starts with a web interface. The URL is printed to the console.

 Learn more: [Getting Started](getting-started.md) | [Architecture](architecture.md) | [Cells](cells/index.md)