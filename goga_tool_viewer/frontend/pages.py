import json
from pathlib import Path

_STATIC = Path(__file__).parent / "static"


def _read_static(filename: str) -> str:
    return (_STATIC / filename).read_text(encoding="utf-8")


def index_page(graph_json_url: str) -> str:
    cytoscape_js = _read_static("cytoscape.min.js")
    dagre_js = _read_static("dagre.min.js")
    cytoscape_dagre_js = _read_static("cytoscape-dagre.min.js")
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ margin: 0; display: flex; height: 100vh; }}
    #cy {{ width: 80%; height: 100%; }}
    #info {{ width: 20%; overflow-y: auto; padding: 10px; }}
    .dimmed {{ opacity: 0.2; }}
    .highlight {{ background-color: yellow; }}
  </style>
  <script>{cytoscape_js}</script>
  <script>{dagre_js}</script>
  <script>{cytoscape_dagre_js}</script>
</head>
<body>
  <div id="cy"></div>
  <div id="info"></div>
  <script>
    fetch({json.dumps(graph_json_url)})
      .then(r => r.json())
      .then(graph => {{
        const cy = render_graph("cy", graph);
        cy.on('tap', 'node', e => show_cell_info(e.target.id(), graph));
        cy.on('mouseover', 'node', e => highlight_cell(e.target.id()));
        cy.on('mouseout', 'node', () => cy.elements().removeClass('dimmed highlight'));
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
              'width': 'label',
              'padding': '10px'
            }}
          }},
          {{
            selector: 'edge',
            style: {{
              'curve-style': 'bezier',
              'target-arrow-shape': 'triangle'
            }}
          }}
        ],
        layout: {{ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }}
      }});
      return cy;
    }}

    function highlight_cell(cell_name) {{
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
