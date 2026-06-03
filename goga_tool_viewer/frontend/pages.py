"""HTML page generators for the graph visualization frontend."""

import base64
import json
from pathlib import Path

_STATIC = Path(__file__).parent / "static"


def _read_static(filename: str) -> str:
    return (_STATIC / filename).read_text(encoding="utf-8")


def _read_static_bytes(filename: str) -> bytes:
    return (_STATIC / filename).read_bytes()


_SVG_TELEGRAM = _read_static("icon-telegram.svg")
_SVG_GITHUB = _read_static("icon-github.svg")
_SVG_EMAIL = _read_static("icon-email.svg")


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
      z-index: 1000;
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 20px;
      background: rgba(10, 14, 26, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    header img {{ height: 28px; }}
    header .logo-text {{ font-size: 18px; font-weight: 600; }}
    header .logo-text .teal {{ color: var(--color-brand-teal); }}
    header .logo-text .white {{ color: var(--color-brand-text); }}
    header .contact-icons {{
      margin-left: auto;
      display: flex;
      gap: 12px;
      align-items: center;
    }}
    header .contact-icons a {{
      opacity: 0.6;
      transition: opacity 0.2s;
      display: flex;
      align-items: center;
    }}
    header .contact-icons a:hover {{ opacity: 1; }}
    header .contact-icons svg {{ width: 20px; height: 20px; fill: var(--color-brand-text); }}
    main {{
      position: relative;
      flex: 1;
      min-height: 0;
      margin-top: 50px;
      overflow: hidden;
    }}
    #sidebar {{
      position: absolute;
      top: 8px;
      left: 8px;
      bottom: 8px;
      width: 260px;
      background: #0f172a;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      z-index: 5;
    }}
    #sidebar-title {{
      padding: 8px 12px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      font-weight: 600;
      color: var(--color-brand-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      text-align: center;
      background: #1e293b;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    #sidebar-tree {{
      flex: 1;
      overflow-y: auto;
      padding: 4px 0;
    }}
    #sidebar-tree::-webkit-scrollbar {{
      width: 4px;
    }}
    #sidebar-tree::-webkit-scrollbar-track {{
      background: transparent;
    }}
    #sidebar-tree::-webkit-scrollbar-thumb {{
      background: rgba(255, 255, 255, 0.1);
      border-radius: 2px;
    }}
    .tree-node {{
      padding: 5px 16px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      color: var(--color-brand-text);
      cursor: pointer;
      border-left: 3px solid transparent;
      transition: background 0.15s, border-color 0.15s;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .tree-node:hover {{
      background: rgba(32, 212, 191, 0.08);
    }}
    .tree-node.active {{
      border-left-color: var(--color-brand-teal);
      background: rgba(32, 212, 191, 0.12);
    }}
    #sidebar-footer {{
      padding: 8px 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .tree-show-all {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 11px;
      color: var(--color-brand-muted);
      cursor: pointer;
      transition: color 0.15s;
    }}
    .tree-show-all:hover {{
      color: var(--color-brand-teal);
    }}
    #cy {{
      position: absolute;
      top: 0;
      left: 276px;
      right: 0;
      bottom: 0;
      background: var(--color-brand-bg);
      animation: fadeIn 0.6s ease-out;
    }}
    #info-wrapper {{
      position: absolute;
      top: 8px;
      right: 8px;
      bottom: 8px;
      width: 25%;
      min-width: 280px;
      max-width: 420px;
      display: flex;
      flex-direction: column;
      background: #0f172a;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      z-index: 10;
    }}
    #info-wrapper.hidden {{ display: none !important; }}
    #info-titlebar {{
      display: flex;
      align-items: center;
      padding: 8px 12px;
      background: #1e293b;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    #info-titlebar .title {{
      flex: 1;
      text-align: center;
      font-size: 12px;
      color: var(--color-brand-muted);
      font-family: ui-monospace, SFMono-Regular, monospace;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      min-width: 0;
    }}
    #info-close {{
      background: none;
      border: none;
      color: var(--color-brand-muted);
      font-size: 16px;
      cursor: pointer;
      padding: 0 4px;
      line-height: 1;
    }}
    #info-close:hover {{ color: var(--color-brand-text); }}
    #info {{
      overflow-y: auto;
      padding: 16px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 13px;
      line-height: 1.6;
      color: #94a3b8;
      flex: 1;
    }}
    #info .yaml-key {{ color: var(--color-brand-teal); }}
    #info .yaml-string {{ color: #a5f3fc; }}
    #info .yaml-null {{ color: var(--color-brand-muted); font-style: italic; }}
    footer {{
      padding: 10px 20px;
      display: flex;
      align-items: center;
      color: var(--color-brand-muted);
      font-size: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}
    footer img {{ height: 20px; }}
    footer .copyright {{ margin-left: auto; }}
    .dimmed {{ opacity: 0.15; transition: opacity 0.3s ease, transform 0.3s ease; }}
    .highlight {{ background-color: #20d4bf; }}
    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}
  </style>
  <script>{cytoscape_js}</script>
  <script>{dagre_js}</script>
  <script>{cytoscape_dagre_js}</script>
</head>
<body>
  <header>
    <img src="data:image/png;base64,{logo_b64}" alt="QArium">
    <span class="logo-text"><span class="teal">QA</span><span class="white">rium</span></span>
    <div class="contact-icons">
      <a href="https://t.me/QAriumCommunity" target="_blank" rel="noopener" title="Telegram">
        {_SVG_TELEGRAM}
      </a>
      <a href="https://github.com/qarium" target="_blank" rel="noopener" title="GitHub">
        {_SVG_GITHUB}
      </a>
      <a href="mailto:info@qarium.ru" title="Email">
        {_SVG_EMAIL}
      </a>
    </div>
  </header>
  <main>
    <div id="sidebar">
      <div id="sidebar-title">Cells</div>
      <div id="sidebar-tree"></div>
      <div id="sidebar-footer"><span class="tree-show-all">Show all</span></div>
    </div>
    <div id="cy"></div>
    <div id="info-wrapper" class="hidden">
      <div id="info-titlebar">
        <span class="title" id="info-title">cell info</span>
        <button id="info-close">&times;</button>
      </div>
      <div id="info"></div>
    </div>
  </main>
  <footer>
    <img src="data:image/png;base64,{logo_b64}" alt="QArium">
    <span class="copyright">© 2026 QArium. All rights reserved.</span>
  </footer>
  <script>
    fetch({json.dumps(graph_json_url)})
      .then(r => r.json())
      .then(graph => {{
        requestAnimationFrame(function() {{
          const cy = render_graph("cy", graph);
          render_tree("sidebar-tree", graph, cy);
          document.querySelector('.tree-show-all').addEventListener('click', function() {{
            cy.elements().removeClass('dimmed highlight highlighted');
            document.querySelectorAll('.tree-node.active').forEach(function(n) {{ n.classList.remove('active'); }});
          }});
          cy.on('tap', 'node', function(e) {{
            show_cell_info(e.target.id(), graph);
            document.getElementById("info-wrapper").classList.remove("hidden");
          }});
          cy.on('mouseover', 'node', function(e) {{
            highlight_cell(e.target.id(), cy);
          }});
          cy.on('mouseout', 'node', function() {{
            cy.elements().removeClass('dimmed highlight');
          }});
        }});
      }})
      .catch(function() {{
        document.getElementById("cy").innerHTML =
          "<p style='padding:20px;color:#a0aec0'>Failed to load graph data.</p>";
      }});

    document.getElementById("info-close").addEventListener("click", function() {{
      document.getElementById("info-wrapper").classList.add("hidden");
    }});

    function render_graph(container_id, graph) {{
      const nodes = graph.cells.map(c => ({{
        data: {{ id: c.name, label: c.name.replace(/\\//g, '/\\n'), description: c.description }}
      }}));
      const edges = graph.edges.map(e => ({{
        data: {{ source: e.from_cell, target: e.to_cell }}
      }}));
      const cy = cytoscape({{
        container: document.getElementById(container_id),
        elements: nodes.concat(edges),
        autoungrabify: true,
        autounselectify: true,
        style: [
          {{
            selector: 'node',
            style: {{
              'label': 'data(label)',
              'text-valign': 'center',
              'text-halign': 'center',
              'shape': 'round-rectangle',
              'background-fill': 'linear-gradient',
              'background-gradient-direction': 'to bottom',
              'background-gradient-stop-colors': '#0f172a #162040',
              'border-color': '#20d4bf',
              'border-width': 1,
              'color': '#fff',
              'text-wrap': 'wrap',
              'text-max-width': '320px',
              'width': 120,
              'padding': '12px',
              'font-size': 10,
              'text-outline-width': 0,
              'shadow-blur': 8,
              'shadow-color': 'rgba(32, 212, 191, 0.15)',
              'shadow-offset-x': 0,
              'shadow-offset-y': 2,
              'transition-property': 'shadow-blur, border-width, border-color',
              'transition-duration': '0.3s'
            }}
          }},
          {{
            selector: 'edge',
            style: {{
              'curve-style': 'bezier',
              'line-color': 'rgba(32, 212, 191, 0.5)',
              'target-arrow-color': '#20d4bf',
              'target-arrow-shape': 'triangle',
              'width': 0.8,
              'transition-property': 'line-color, width',
              'transition-duration': '0.3s'
            }}
          }},
          {{
            selector: 'edge.highlighted',
            style: {{
              'line-color': '#20d4bf',
              'width': 1.5
            }}
          }},
          {{
            selector: '.dimmed',
            style: {{
              'opacity': 0.15
            }}
          }},
          {{
            selector: '.highlight',
            style: {{
              'shadow-blur': 20,
              'shadow-color': 'rgba(32, 212, 191, 0.4)',
              'border-width': 2,
              'border-color': '#20d4bf'
            }}
          }}
        ],
        layout: {{ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }}
      }});
      return cy;
    }}

    function highlight_cell(cell_name, cy) {{
      cy.elements().removeClass('highlight highlighted').addClass('dimmed');
      const node = cy.getElementById(cell_name);
      node.removeClass('dimmed').addClass('highlight');
      node.connectedEdges().removeClass('dimmed').addClass('highlighted');
      node.connectedEdges().connectedNodes().removeClass('dimmed');
    }}

    function _esc(s) {{
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
    }}

    function _yamlValue(v) {{
      if (v === null || v === undefined) return '<span class="yaml-null">null</span>';
      return '<span class="yaml-string">' + _esc(String(v)) + '</span>';
    }}

    function _yamlList(items) {{
      if (!items || items.length === 0) return '<span class="yaml-null">[]</span>';
      return items.map(i => '  - ' + _yamlValue(i)).join('<br>');
    }}

    function render_tree(container_id, graph, cy_instance) {{
      const container = document.getElementById(container_id);
      container.innerHTML = '';
      const allNames = new Set(graph.cells.map(function(c) {{ return c.name; }}));
      const childNames = new Set();
      graph.cells.forEach(function(cell) {{
        if (cell.children) {{
          cell.children.forEach(function(ch) {{ childNames.add(ch.name); }});
        }}
      }});
      const roots = graph.cells.filter(function(c) {{ return !childNames.has(c.name); }});
      function build_node(cell, depth) {{
        const div = document.createElement('div');
        div.className = 'tree-node';
        div.style.paddingLeft = (16 + depth * 16) + 'px';
        div.textContent = cell.name.split('/').pop();
        div.setAttribute('data-cell-name', cell.name);
        div.addEventListener('click', function() {{
          document.querySelectorAll('.tree-node.active').forEach(function(n) {{ n.classList.remove('active'); }});
          div.classList.add('active');
          highlight_cell(cell.name, cy_instance);
        }});
        container.appendChild(div);
        if (cell.children && cell.children.length > 0) {{
          cell.children.forEach(function(child) {{ build_node(child, depth + 1); }});
        }}
      }}
      roots.forEach(function(root) {{ build_node(root, 0); }});
    }}

    function show_cell_info(cell_name, graph) {{
      const cell = graph.cells.find(c => c.name === cell_name);
      if (!cell) {{
        document.getElementById("info").innerHTML = "<p>Cell not found</p>";
        document.getElementById("info-title").textContent = "cell info";
        return;
      }}
      document.getElementById("info-title").textContent = cell.name;
      const consumers = graph.edges
        .filter(e => e.to_cell === cell_name)
        .map(e => e.from_cell);
      const deps = (cell.dependencies || []).map(d => d.to_cell);
      document.getElementById("info").innerHTML =
        '<span class="yaml-key">name:</span> ' + _yamlValue(cell.name) + '<br>' +
        '<span class="yaml-key">description:</span> ' + _yamlValue(cell.description || null) + '<br>' +
        '<br>' +
        '<span class="yaml-key">types:</span><br>' + _yamlList(cell.types || []) + '<br>' +
        '<br>' +
        '<span class="yaml-key">consumers:</span><br>' + _yamlList(consumers) + '<br>' +
        '<br>' +
        '<span class="yaml-key">dependencies:</span><br>' + _yamlList(deps);
    }}
  </script>
</body>
</html>"""
