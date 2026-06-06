"""HTML page generators for the graph visualization frontend."""

import base64
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
_ICON_CODE = _svg_data_uri("icon-code.svg")
_ICON_RESET = _svg_data_uri("icon-reset.svg")


def index_page(graph_json_url: str) -> str:
    """Generate the main HTML page with embedded graph visualization.

    Args:
        graph_json_url: URL path to the graph JSON API endpoint.

    Returns:
        Complete HTML document as a string referencing external CSS and JS.
    """
    logo_data = _read_static_bytes("logo.png")
    favicon_data = _read_static_bytes("favicon.png")
    logo_b64 = base64.b64encode(logo_data).decode("ascii")
    favicon_b64 = base64.b64encode(favicon_data).decode("ascii")

    return f"""<!DOCTYPE html>
<html data-api-url="{graph_json_url}">
<head>
  <meta charset="utf-8">
  <link rel="icon" href="data:image/png;base64,{favicon_b64}">
  <link rel="stylesheet" href="/static/style.css">
  <style>
    :root {{
      --icon-name: url("{_ICON_NAME}");
      --icon-description: url("{_ICON_DESCRIPTION}");
      --icon-types: url("{_ICON_TYPES}");
      --icon-consumers: url("{_ICON_CONSUMERS}");
      --icon-dependencies: url("{_ICON_DEPENDENCIES}");
      --icon-folder: url("{_ICON_FOLDER}");
      --icon-layers: url("{_ICON_LAYERS}");
      --icon-code: url("{_ICON_CODE}");
      --icon-reset: url("{_ICON_RESET}");
    }}
  </style>
  <script src="/static/cytoscape.min.js"></script>
  <script src="/static/dagre.min.js"></script>
  <script src="/static/cytoscape-dagre.min.js"></script>
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
      <div id="sidebar-tree"><div class="scroll-content"></div
        ><div class="scroll-bar"><div class="scroll-thumb"></div></div></div>
      <div id="sidebar-footer"><span class="tree-show-all"><img
        class="link-icon" src="{_ICON_RESET}" alt="">Reset</span></div>
    </div>
    <div id="cy"></div>
    <div id="info-wrapper" class="hidden">
      <div id="info-titlebar">
        <span class="title" id="info-title">cell info</span>
        <button id="info-close">&times;</button>
      </div>
      <div id="info"><div class="scroll-content"></div
        ><div class="scroll-bar"><div class="scroll-thumb"></div></div></div>
      <div id="info-footer"></div>
    </div>
  </main>
  <footer>
    <img src="data:image/png;base64,{logo_b64}" alt="QArium">
    <span class="copyright">&copy; 2026 QArium. All rights reserved.</span>
  </footer>
  <script src="/static/app.js"></script>
</body>
</html>"""
