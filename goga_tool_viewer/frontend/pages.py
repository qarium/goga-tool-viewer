"""HTML page generators for the graph visualization frontend."""

import base64
import json
from pathlib import Path
from urllib.parse import quote as urlquote

_STATIC = Path(__file__).parent / "static"


def _read_static(filename: str) -> str:
    return (_STATIC / filename).read_text(encoding="utf-8")


def _read_static_bytes(filename: str) -> bytes:
    return (_STATIC / filename).read_bytes()


_SVG_TELEGRAM = _read_static("icon-telegram.svg")
_SVG_GITHUB = _read_static("icon-github.svg")
_SVG_EMAIL = _read_static("icon-email.svg")


def _svg_data_uri(filename: str) -> str:
    svg = _read_static(filename).strip()
    return f'data:image/svg+xml,{urlquote(svg, safe="")}'


_ICON_NAME = _svg_data_uri("icon-name.svg")
_ICON_DESCRIPTION = _svg_data_uri("icon-description.svg")
_ICON_TYPES = _svg_data_uri("icon-types.svg")
_ICON_CONSUMERS = _svg_data_uri("icon-consumers.svg")
_ICON_DEPENDENCIES = _svg_data_uri("icon-dependencies.svg")
_ICON_FOLDER = _svg_data_uri("icon-folder.svg")
_ICON_LAYERS = _svg_data_uri("icon-layers.svg")


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
      position: relative;
      padding: 5px 12px 5px 8px;
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      color: var(--color-brand-text);
      cursor: pointer;
      border-left: 3px solid transparent;
      transition: background 0.15s, border-color 0.15s;
      display: flex;
      align-items: center;
    }}
    .tree-guides {{
      display: flex;
      flex-shrink: 0;
    }}
    .tree-guide {{
      width: 16px;
      height: 28px;
      position: relative;
      flex-shrink: 0;
    }}
    .tree-guide.pipe::before {{
      content: '';
      position: absolute;
      left: 7px;
      top: 0;
      bottom: 0;
      width: 1px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .tree-guide.tee::before {{
      content: '';
      position: absolute;
      left: 7px;
      top: 0;
      bottom: 0;
      width: 1px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .tree-guide.tee::after {{
      content: '';
      position: absolute;
      left: 7px;
      top: 50%;
      width: 9px;
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .tree-guide.elbow::before {{
      content: '';
      position: absolute;
      left: 7px;
      top: 0;
      height: 50%;
      width: 1px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .tree-guide.elbow::after {{
      content: '';
      position: absolute;
      left: 7px;
      top: 50%;
      width: 9px;
      height: 1px;
      background: rgba(255, 255, 255, 0.08);
    }}
    .tree-guide.empty {{
      /* no lines — placeholder for spacing */
    }}
    .tree-icon {{
      display: inline-block;
      width: 14px;
      height: 14px;
      background-size: contain;
      background-repeat: no-repeat;
      margin-right: 6px;
      flex-shrink: 0;
    }}
    .tree-name {{
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .tree-badge {{
      font-size: 10px;
      color: var(--color-brand-muted);
      background: rgba(255, 255, 255, 0.06);
      padding: 0 5px;
      border-radius: 8px;
      margin-left: 6px;
      flex-shrink: 0;
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
    #info .section {{
      margin-top: 16px;
      padding-top: 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
    #info .section:first-child {{
      margin-top: 0;
      padding-top: 0;
      border-top: none;
    }}
    #info h2 {{
      font-size: 12px;
      font-weight: 600;
      color: var(--color-brand-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 0 0 6px 0;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    #info h2::before {{
      content: '';
      width: 14px;
      height: 14px;
      display: inline-block;
      flex-shrink: 0;
      background-size: contain;
      background-repeat: no-repeat;
    }}
    #info h2[data-icon="name"]::before {{
      background-image: url("{_ICON_NAME}");
    }}
    #info h2[data-icon="description"]::before {{
      background-image: url("{_ICON_DESCRIPTION}");
    }}
    #info h2[data-icon="types"]::before {{
      background-image: url("{_ICON_TYPES}");
    }}
    #info h2[data-icon="consumers"]::before {{
      background-image: url("{_ICON_CONSUMERS}");
    }}
    #info h2[data-icon="dependencies"]::before {{
      background-image: url("{_ICON_DEPENDENCIES}");
    }}
    #info p {{
      margin: 4px 0;
      color: var(--color-brand-text);
      line-height: 1.5;
    }}
    #info .description {{
      margin: 4px 0;
      padding: 8px 12px;
      border-left: 3px solid var(--color-brand-teal);
      background: rgba(32, 212, 191, 0.05);
      color: var(--color-brand-text);
      line-height: 1.5;
      font-style: italic;
    }}
    #info ul {{
      margin: 4px 0;
      padding-left: 20px;
    }}
    #info li {{
      color: var(--color-brand-text);
      line-height: 1.6;
    }}
    #info li .label {{
      color: #a5f3fc;
    }}
    #info .empty {{ color: var(--color-brand-muted); font-style: italic; }}
    #info-footer {{
      padding: 8px 16px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      flex-shrink: 0;
    }}
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
    #codemanifest-panel {{
      position: absolute;
      top: 8px;
      bottom: 8px;
      left: 276px;
      right: 8px;
      background: #0f172a;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      z-index: 8;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
    }}
    #codemanifest-panel .titlebar {{
      display: flex;
      align-items: center;
      padding: 8px 12px;
      background: #1e293b;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      flex-shrink: 0;
    }}
    #codemanifest-panel .titlebar .title {{
      flex: 1;
      text-align: center;
      font-size: 12px;
      color: var(--color-brand-muted);
      font-family: ui-monospace, SFMono-Regular, monospace;
    }}
    #codemanifest-panel .titlebar .close {{
      background: none;
      border: none;
      color: var(--color-brand-muted);
      font-size: 16px;
      cursor: pointer;
      padding: 0 4px;
      line-height: 1;
    }}
    #codemanifest-panel .titlebar .close:hover {{
      color: var(--color-brand-text);
    }}
    #codemanifest-panel pre code {{
      font-family: ui-monospace, SFMono-Regular, monospace;
      font-size: 12px;
      color: var(--color-brand-text);
      white-space: pre-wrap;
      padding: 16px;
      display: block;
    }}
    .yaml-key {{ color: #20d4bf; }}
    .yaml-comment {{ color: #64748b; }}
    .yaml-delim {{ color: #64748b; }}
    .yaml-literal {{ color: #94a3b8; }}
    .yaml-bool {{ color: #f59e0b; }}
    .yaml-number {{ color: #a78bfa; }}
    .yaml-code {{ color: #a5f3fc; }}
    .codemanifest-link {{
      cursor: pointer;
      color: var(--color-brand-muted);
      font-size: 11px;
      transition: color 0.15s;
    }}
    .codemanifest-link:hover {{
      color: var(--color-brand-teal);
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
      <div id="info-footer"></div>
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
            reset_filter(cy);
          }});
          cy.on('tap', 'node', function(e) {{
            show_cell_info(e.target.id(), graph);
            document.getElementById("info-wrapper").classList.remove("hidden");
          }});
          cy.on('mouseover', 'node', function(e) {{
            highlight_cell(e.target.id(), cy);
          }});
          cy.on('mouseout', 'node', function() {{
            cy.elements().removeClass('dimmed highlight highlighted');
          }});
        }});
      }})
      .catch(function() {{
        document.getElementById("cy").innerHTML =
          "<p style='padding:20px;color:#a0aec0'>Failed to load graph data.</p>";
      }});

    document.getElementById("info-close").addEventListener("click", function() {{
      document.getElementById("info-wrapper").classList.add("hidden");
      var cm = document.getElementById('codemanifest-panel');
      if (cm) cm.remove();
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

    function filter_cell(cell_name, cy) {{
      const node = cy.getElementById(cell_name);
      if (node.length === 0) return;
      const connected = node.connectedEdges().connectedNodes();
      const visibleIds = new Set();
      visibleIds.add(cell_name);
      connected.forEach(function(n) {{ visibleIds.add(n.id()); }});
      cy.elements().removeClass('highlight highlighted dimmed').show();
      cy.nodes().forEach(function(n) {{
        if (!visibleIds.has(n.id())) n.hide();
      }});
      cy.edges().forEach(function(e) {{
        const src = e.source().id();
        const tgt = e.target().id();
        if (!visibleIds.has(src) || !visibleIds.has(tgt)) e.hide();
      }});
      node.addClass('highlight');
      node.connectedEdges().addClass('highlighted');
      cy.layout({{ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }}).run();
    }}

    function reset_filter(cy) {{
      cy.elements().show();
      cy.elements().removeClass('highlight highlighted dimmed');
      document.querySelectorAll('.tree-node.active').forEach(function(n) {{ n.classList.remove('active'); }});
      cy.layout({{ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }}).run();
    }}

    function _esc(s) {{
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
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
      const folderIcon = '{_ICON_FOLDER}';
      const cubeIcon = '{_ICON_LAYERS}';
      function build_guides(ancestorPipes) {{
        let html = '<span class="tree-guides">';
        for (let i = 0; i < ancestorPipes.length; i++) {{
          html += '<span class="tree-guide '
            + (ancestorPipes[i] ? 'pipe' : 'empty') + '"></span>';
        }}
        html += '</span>';
        return html;
      }}
      function build_node(cell, depth, isLast, ancestorPipes) {{
        const div = document.createElement('div');
        div.className = 'tree-node';
        div.setAttribute('data-cell-name', cell.name);
        div.setAttribute('data-depth', depth);
        const hasChildren = cell.children && cell.children.length > 0;
        const icon = hasChildren ? folderIcon : cubeIcon;
        const depCount = (cell.dependencies || []).length;
        let guides = '';
        if (depth > 0) {{
          guides = '<span class="tree-guides">';
          for (let i = 0; i < ancestorPipes.length; i++) {{
            guides += '<span class="tree-guide '
              + (ancestorPipes[i] ? 'pipe' : 'empty') + '"></span>';
          }}
          guides += '<span class="tree-guide '
            + (isLast ? 'elbow' : 'tee') + '"></span>';
          guides += '</span>';
        }}
        let inner = guides;
        inner += '<span class="tree-icon" style="background-image:url('
          + icon + ')"></span>';
        inner += '<span class="tree-name">' + _esc(cell.name.split('/').pop())
          + '</span>';
        if (depCount > 0) {{
          inner += '<span class="tree-badge">' + depCount + '</span>';
        }}
        div.innerHTML = inner;
        div.addEventListener('click', function() {{
          document.querySelectorAll('.tree-node.active').forEach(function(n) {{
            n.classList.remove('active');
          }});
          div.classList.add('active');
          filter_cell(cell.name, cy_instance);
        }});
        container.appendChild(div);
        if (hasChildren) {{
          const childPipes = ancestorPipes.concat([!isLast]);
          cell.children.forEach(function(child, i) {{
            build_node(child, depth + 1, i === cell.children.length - 1,
              childPipes);
          }});
        }}
      }}
      roots.forEach(function(root, i) {{
        build_node(root, 0, i === roots.length - 1, []);
      }});
    }}

    function show_cell_info(cell_name, graph) {{
      var cmPanel = document.getElementById('codemanifest-panel');
      if (cmPanel) cmPanel.remove();
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
      const types = cell.types || [];
      let html = '<div class="section"><h2 data-icon="name">Name</h2><p>' + _esc(cell.name) + '</p></div>';
      html += '<div class="section"><h2 data-icon="description">Description</h2>';
      html += cell.description
        ? '<div class="description">' + _esc(cell.description) + '</div>'
        : '<p class="empty">No description</p>';
      html += '</div>';
      html += '<div class="section"><h2 data-icon="types">Types</h2>';
      html += types.length > 0
        ? '<ul>' + types.map(t => '<li><span class="label">' + _esc(t) + '</span></li>').join('') + '</ul>'
        : '<p class="empty">No types</p>';
      html += '</div>';
      if (consumers.length > 0) {{
        html += '<div class="section"><h2 data-icon="consumers">Consumers</h2><ul>' +
          consumers.map(c => '<li>' + _esc(c) + '</li>').join('') + '</ul></div>';
      }}
      if (deps.length > 0) {{
        html += '<div class="section"><h2 data-icon="dependencies">Dependencies</h2><ul>' +
          deps.map(d => '<li>' + _esc(d) + '</li>').join('') + '</ul></div>';
      }}
      document.getElementById("info").innerHTML = html;
      var infoFooter = document.getElementById("info-footer");
      infoFooter.innerHTML = '<span class="codemanifest-link">CODEMANIFEST</span>';
      infoFooter.querySelector('.codemanifest-link').addEventListener('click', function() {{
        show_codemanifest(cell_name, graph);
      }});
    }}

    function _highlight_yaml(text) {{
      var s = _esc(text);
      var lines = s.split('\\n');
      var literalIndent = -1;
      for (var i = 0; i < lines.length; i++) {{
        var line = lines[i];
        var lineIndent = line.search(/\\S/);
        if (line.trim() === '') lineIndent = 0;
        if (literalIndent >= 0) {{
          if (lineIndent > literalIndent || line.trim() === '') {{
            continue;
          }}
          literalIndent = -1;
        }}
        var commentIdx = line.indexOf('#');
        var delimMatch = line.match(/^(---)(\\s*)$/);
        if (delimMatch) {{
          lines[i] = '<span class="yaml-delim">' + delimMatch[1] + '</span>' + delimMatch[2];
          continue;
        }}
        if (commentIdx === 0) {{
          lines[i] = '<span class="yaml-comment">' + line + '</span>';
          continue;
        }}
        var keyMatch = line.match(/^(\\s*(?:-\\s*)?)("[^"]*"|[\\w][\\w.-]*)(:)(.*)$/);
        if (keyMatch) {{
          var indent = keyMatch[1];
          var key = keyMatch[2];
          var colon = keyMatch[3];
          var rest = keyMatch[4];
          var keyIndent = indent.length;
          var highlighted = indent + '<span class="yaml-key">' + key + '</span>' + colon;
          if (rest) {{
            var litMatch = rest.match(/^\\s*(\\||>)/);
            if (litMatch) {{
              rest = '<span class="yaml-literal">' + rest.trim() + '</span>';
              literalIndent = keyIndent;
            }} else {{
              rest = rest.replace(/\\b(true|false|null)\\b/g, '<span class="yaml-bool">$1</span>');
              rest = rest.replace(/\\b(\\d+)\\b/g, '<span class="yaml-number">$1</span>');
              if (rest.indexOf('#') !== -1) {{
                var ci = rest.indexOf('#');
                rest = rest.substring(0, ci) + '<span class="yaml-comment">' + rest.substring(ci) + '</span>';
              }}
            }}
          }}
          lines[i] = highlighted + rest;
          continue;
        }}
        if (commentIdx > 0) {{
          lines[i] = line.substring(0, commentIdx) + '<span class="yaml-comment">' + line.substring(commentIdx) + '</span>';
          continue;
        }}
      }}
      return lines.join('\\n').replace(/`([^`]+)`/g, '<span class="yaml-code">`$1`</span>');
    }}

    function _show_cm_panel(rawContent) {{
      var existing = document.getElementById('codemanifest-panel');
      if (existing) existing.remove();
      var panel = document.createElement('div');
      panel.id = 'codemanifest-panel';
      panel.innerHTML = '<div class="titlebar"><span class="title">CODEMANIFEST</span>'
        + '<button class="close">&times;</button></div>'
        + '<pre><code>' + _highlight_yaml(rawContent) + '</code></pre>';
      document.querySelector('main').appendChild(panel);
      var infoWrapper = document.getElementById('info-wrapper');
      if (!infoWrapper.classList.contains('hidden')) {{
        var infoRect = infoWrapper.getBoundingClientRect();
        panel.style.right = (window.innerWidth - infoRect.left + 8) + 'px';
      }}
      panel.querySelector('.close').addEventListener('click', function() {{
        panel.remove();
      }});
    }}

    function show_codemanifest(cell_name, graph) {{
      const cell = graph.cells.find(c => c.name === cell_name);
      if (!cell) return;
      fetch('/api/codemanifest?cell=' + encodeURIComponent(cell.name), {{cache: 'no-store'}})
        .then(function(response) {{
          if (response.status === 404) return 'CODEMANIFEST not found';
          if (response.ok) return response.text();
          return 'Failed to load CODEMANIFEST';
        }})
        .then(function(content) {{
          _show_cm_panel(content);
        }})
        .catch(function() {{
          _show_cm_panel('Failed to load CODEMANIFEST');
        }});
    }}
  </script>
</body>
</html>"""
