"""HTML page generators for the graph visualization frontend."""

import base64
import json
from pathlib import Path

_STATIC = Path(__file__).parent / "static"


def _read_static(filename: str) -> str:
    return (_STATIC / filename).read_text(encoding="utf-8")


def _read_static_bytes(filename: str) -> bytes:
    return (_STATIC / filename).read_bytes()


def index_page(graph_json_url: str) -> str:
    """Generate the main HTML page with embedded graph visualization.

    Args:
        graph_json_url: URL path to the graph JSON API endpoint.

    Returns:
        Complete HTML document as a string with embedded JavaScript and CSS.
    """
    cytoscape_js = _read_static("cytoscape.min.js")
    dagre_js = _read_static("dagre.min.js")
    cytoscape_dagre_js = _read_static("cytoscape-dagre.min.js")
    logo_data = _read_static_bytes("logo.png")
    favicon_data = _read_static_bytes("favicon.png")
    logo_b64 = base64.b64encode(logo_data).decode("ascii")
    favicon_b64 = base64.b64encode(favicon_data).decode("ascii")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:image/png;base64,{favicon_b64}">
  <style>
    :root {{
      --color-brand-bg: #0a0e1a;
      --color-brand-card: #121830;
      --color-brand-teal: #20d4bf;
      --color-brand-blue: #3882f6;
      --color-brand-text: #fff;
      --color-brand-muted: #a0aec0;
    }}
    * {{ margin: 0; box-sizing: border-box; }}
    body {{
      font-family: ui-sans-serif, system-ui, sans-serif;
      -webkit-font-smoothing: antialiased;
      background-color: var(--color-brand-bg);
      color: var(--color-brand-text);
      display: flex;
      flex-direction: column;
      height: 100vh;
    }}
    header {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 20px;
      background: rgba(10, 14, 26, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    header img {{ height: 28px; }}
    header span {{ font-size: 18px; font-weight: 600; color: var(--color-brand-teal); }}
    main {{
      display: flex;
      flex: 1;
      margin-top: 50px;
      overflow: hidden;
    }}
    #cy {{ width: 80%; height: 100%; background: var(--color-brand-bg); }}
    #info {{
      width: 20%;
      overflow-y: auto;
      padding: 16px;
      background: var(--color-brand-card);
      border-left: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 8px;
    }}
    footer {{
      padding: 10px 20px;
      text-align: center;
      color: var(--color-brand-muted);
      font-size: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .dimmed {{ opacity: 0.2; }}
    .highlight {{ background-color: #20d4bf; }}
  </style>
  <script>{cytoscape_js}</script>
  <script>{dagre_js}</script>
  <script>{cytoscape_dagre_js}</script>
</head>
<body>
  <header>
    <img src="data:image/png;base64,{logo_b64}" alt="QArium">
    <span>QArium</span>
  </header>
  <main>
    <div id="cy"></div>
    <div id="info"></div>
  </main>
  <footer>
    © 2026 QArium. All rights reserved.
  </footer>
  <script>
    fetch({json.dumps(graph_json_url)})
      .then(r => r.json())
      .then(graph => {{
        const cy = render_graph("cy", graph);
        cy.on('tap', 'node', e => show_cell_info(e.target.id(), graph));
        cy.on('mouseover', 'node', e => highlight_cell(e.target.id(), cy));
        cy.on('mouseout', 'node', () => cy.elements().removeClass('dimmed highlight'));
      }})
      .catch(() => {{
        document.getElementById("cy").innerHTML =
          "<p style='padding:20px;color:#a0aec0'>Failed to load graph data.</p>";
      }});

    function render_graph(container_id, graph) {{
      const nodes = graph.cells.map(c => ({{
        data: {{ id: c.name, label: c.name, description: c.description }}
      }}));
      const edges = graph.edges.map(e => ({{
        data: {{ source: e.from_cell, target: e.to_cell }}
      }}));
      const cy = cytoscape({{
        container: document.getElementById(container_id),
        elements: nodes.concat(edges),
        style: [
          {{
            selector: 'node',
            style: {{
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'shape': 'round-rectangle',
              'background-color': '#121830',
              'border-color': '#20d4bf',
              'color': '#fff',
              'width': 'label',
              'padding': '10px'
            }}
          }},
          {{
            selector: 'edge',
            style: {{
              'curve-style': 'bezier',
              'line-color': '#20d4bf',
              'target-arrow-color': '#20d4bf',
              'target-arrow-shape': 'triangle'
            }}
          }}
        ],
        layout: {{ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }}
      }});
      return cy;
    }}

    function highlight_cell(cell_name, cy) {{
      cy.elements().addClass('dimmed');
      const node = cy.getElementById(cell_name);
      node.removeClass('dimmed').addClass('highlight');
      node.connectedEdges().connectedNodes().removeClass('dimmed');
      node.connectedEdges().removeClass('dimmed');
    }}

    function _esc(s) {{
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
    }}

    function show_cell_info(cell_name, graph) {{
      const cell = graph.cells.find(c => c.name === cell_name);
      if (!cell) {{
        document.getElementById("info").innerHTML = "<p>Cell not found</p>";
        return;
      }}
      const consumers = graph.edges
        .filter(e => e.to_cell === cell_name)
        .map(e => e.from_cell);
      const depList = cell.dependencies.map(d => d.to_cell);
      document.getElementById("info").innerHTML =
        "<h3>" + _esc(cell.name) + "</h3>" +
        "<p>" + _esc(cell.description) + "</p>" +
        "<h4>Types</h4><ul>" +
        cell.types.map(t => "<li>" + _esc(t) + "</li>").join("") +
        "</ul>" +
        "<h4>Consumers</h4><ul>" +
        consumers.map(c => "<li>" + _esc(c) + "</li>").join("") +
        "</ul>" +
        "<h4>Dependencies</h4><ul>" +
        depList.map(d => "<li>" + _esc(d) + "</li>").join("") +
        "</ul>";
    }}
  </script>
</body>
</html>"""
