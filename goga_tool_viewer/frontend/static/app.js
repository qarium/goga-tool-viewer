(function() {
  function getIcon(prop) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
    var m = v.match(/^url\(["']?(.*?)["']?\)$/);
    return m ? m[1] : v;
  }
  var graphJsonUrl = document.documentElement.getAttribute('data-api-url');
  var codeIcon = getIcon('--icon-code');
  var folderIcon = getIcon('--icon-folder');
  var cubeIcon = getIcon('--icon-layers');
  var resetIcon = getIcon('--icon-reset');

  fetch(graphJsonUrl)
    .then(function(r) { return r.json(); })
    .then(function(graph) {
      requestAnimationFrame(function() {
        var cy = render_graph("cy", graph);
        render_tree("sidebar-tree", graph, cy);
        _init_custom_scroll(document.getElementById('sidebar-tree'));
        _init_custom_scroll(document.getElementById('info'));
        document.querySelector('.tree-show-all').addEventListener('click', function() {
          reset_filter(cy);
        });
        cy.on('tap', 'node', function(e) {
          show_cell_info(e.target.id(), graph);
          document.getElementById("info-wrapper").classList.remove("hidden");
        });
        cy.on('mouseover', 'node', function(e) {
          highlight_cell(e.target.id(), cy);
        });
        cy.on('mouseout', 'node', function() {
          cy.elements().removeClass('dimmed highlight highlighted');
        });
      });
    })
    .catch(function() {
      document.getElementById("cy").innerHTML =
        "<p style='padding:20px;color:#a0aec0'>Failed to load graph data.</p>";
    });

  document.getElementById("info-close").addEventListener("click", function() {
    document.getElementById("info-wrapper").classList.add("hidden");
    var cm = document.getElementById('codemanifest-panel');
    if (cm) cm.remove();
  });

  function render_graph(container_id, graph) {
    var nodes = graph.cells.map(function(c) {
      return {
        data: { id: c.name, label: c.name.replace(/\//g, '/\n'), description: c.description }
      };
    });
    var edges = graph.edges.map(function(e) {
      return { data: { source: e.from_cell, target: e.to_cell } };
    });
    var cy = cytoscape({
      container: document.getElementById(container_id),
      elements: nodes.concat(edges),
      autoungrabify: true,
      autounselectify: true,
      style: [
        {
          selector: 'node',
          style: {
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
          }
        },
        {
          selector: 'edge',
          style: {
            'curve-style': 'bezier',
            'line-color': 'rgba(32, 212, 191, 0.5)',
            'target-arrow-color': '#20d4bf',
            'target-arrow-shape': 'triangle',
            'width': 0.8,
            'transition-property': 'line-color, width',
            'transition-duration': '0.3s'
          }
        },
        {
          selector: 'edge.highlighted',
          style: {
            'line-color': '#20d4bf',
            'width': 1.5
          }
        },
        {
          selector: '.dimmed',
          style: {
            'opacity': 0.15
          }
        },
        {
          selector: '.highlight',
          style: {
            'shadow-blur': 20,
            'shadow-color': 'rgba(32, 212, 191, 0.4)',
            'border-width': 2,
            'border-color': '#20d4bf'
          }
        }
      ],
      layout: { name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }
    });
    return cy;
  }

  function highlight_cell(cell_name, cy) {
    cy.elements().removeClass('highlight highlighted').addClass('dimmed');
    var node = cy.getElementById(cell_name);
    node.removeClass('dimmed').addClass('highlight');
    node.connectedEdges().removeClass('dimmed').addClass('highlighted');
    node.connectedEdges().connectedNodes().removeClass('dimmed');
  }

  var selectedCells = new Set();

  function apply_filter(cy) {
    cy.elements().removeClass('highlight highlighted dimmed').show();
    if (selectedCells.size === 0) {
      cy.layout({ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }).run();
      return;
    }
    var visibleIds = new Set();
    selectedCells.forEach(function(cellName) {
      var node = cy.getElementById(cellName);
      if (node.length === 0) return;
      visibleIds.add(cellName);
      node.connectedEdges().connectedNodes().forEach(function(n) { visibleIds.add(n.id()); });
    });
    cy.nodes().forEach(function(n) {
      if (!visibleIds.has(n.id())) n.hide();
    });
    cy.edges().forEach(function(e) {
      var src = e.source().id();
      var tgt = e.target().id();
      if (!visibleIds.has(src) || !visibleIds.has(tgt)) e.hide();
    });
    selectedCells.forEach(function(cellName) {
      var node = cy.getElementById(cellName);
      node.addClass('highlight');
      node.connectedEdges().addClass('highlighted');
    });
    cy.layout({ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }).run();
  }

  function reset_filter(cy) {
    selectedCells.clear();
    cy.elements().show();
    cy.elements().removeClass('highlight highlighted dimmed');
    document.querySelectorAll('.tree-node.active').forEach(function(n) { n.classList.remove('active'); });
    cy.layout({ name: 'dagre', spacingFactor: 1.5, rankDir: 'LR' }).run();
  }

  function _init_custom_scroll(wrapper) {
    var scrollContent = wrapper.querySelector('.scroll-content');
    var scrollThumb = wrapper.querySelector('.scroll-thumb');
    if (!scrollContent || !scrollThumb) return;
    function updateScrollbar() {
      var ratio = scrollContent.clientHeight / scrollContent.scrollHeight;
      if (ratio >= 1) {
        scrollThumb.style.display = 'none';
        return;
      }
      scrollThumb.style.display = '';
      var thumbH = Math.max(30, scrollContent.clientHeight * ratio);
      var scrollRatio = scrollContent.scrollTop / (scrollContent.scrollHeight - scrollContent.clientHeight);
      var thumbTop = scrollRatio * (scrollContent.clientHeight - thumbH);
      scrollThumb.style.height = thumbH + 'px';
      scrollThumb.style.top = thumbTop + 'px';
    }
    scrollContent.addEventListener('scroll', updateScrollbar);
    updateScrollbar();
    var dragging = false, startY = 0, startTop = 0;
    scrollThumb.addEventListener('mousedown', function(e) {
      dragging = true;
      startY = e.clientY;
      startTop = parseInt(scrollThumb.style.top) || 0;
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      var delta = e.clientY - startY;
      var thumbH = parseInt(scrollThumb.style.height) || 30;
      var maxTop = scrollContent.clientHeight - thumbH;
      var newTop = Math.max(0, Math.min(maxTop, startTop + delta));
      scrollThumb.style.top = newTop + 'px';
      scrollContent.scrollTop = (newTop / maxTop) * (scrollContent.scrollHeight - scrollContent.clientHeight);
    });
    document.addEventListener('mouseup', function() {
      dragging = false;
    });
  }

  function _esc(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function render_tree(container_id, graph, cy_instance) {
    var wrapper = document.getElementById(container_id);
    var container = wrapper.querySelector('.scroll-content');
    container.innerHTML = '';
    var allNames = new Set(graph.cells.map(function(c) { return c.name; }));
    var childNames = new Set();
    graph.cells.forEach(function(cell) {
      if (cell.children) {
        cell.children.forEach(function(ch) { childNames.add(ch.name); });
      }
    });
    var roots = graph.cells.filter(function(c) { return !childNames.has(c.name); });
    function build_guides(ancestorPipes) {
      var html = '<span class="tree-guides">';
      for (var i = 0; i < ancestorPipes.length; i++) {
        html += '<span class="tree-guide '
          + (ancestorPipes[i] ? 'pipe' : 'empty') + '"></span>';
      }
      html += '</span>';
      return html;
    }
    function build_node(cell, depth, isLast, ancestorPipes) {
      var div = document.createElement('div');
      div.className = 'tree-node';
      div.setAttribute('data-cell-name', cell.name);
      div.setAttribute('data-depth', depth);
      var hasChildren = cell.children && cell.children.length > 0;
      var icon = hasChildren ? folderIcon : cubeIcon;
      var depCount = (cell.dependencies || []).length;
      var guides = '';
      if (depth > 0) {
        guides = '<span class="tree-guides">';
        for (var i = 0; i < ancestorPipes.length; i++) {
          guides += '<span class="tree-guide '
            + (ancestorPipes[i] ? 'pipe' : 'empty') + '"></span>';
        }
        guides += '<span class="tree-guide '
          + (isLast ? 'elbow' : 'tee') + '"></span>';
        guides += '</span>';
      }
      var inner = guides;
      inner += '<span class="tree-icon" style="background-image:url('
        + icon + ')"></span>';
      inner += '<span class="tree-name">' + _esc(cell.name.split('/').pop())
        + '</span>';
      if (depCount > 0) {
        inner += '<span class="tree-badge">' + depCount + '</span>';
      }
      div.innerHTML = inner;
      div.addEventListener('click', function() {
        if (selectedCells.has(cell.name)) {
          selectedCells.delete(cell.name);
          div.classList.remove('active');
        } else {
          selectedCells.add(cell.name);
          div.classList.add('active');
        }
        apply_filter(cy_instance);
      });
      container.appendChild(div);
      if (hasChildren) {
        var childPipes = ancestorPipes.concat([!isLast]);
        cell.children.forEach(function(child, i) {
          build_node(child, depth + 1, i === cell.children.length - 1,
            childPipes);
        });
      }
    }
    roots.forEach(function(root, i) {
      build_node(root, 0, i === roots.length - 1, []);
    });
  }

  function show_cell_info(cell_name, graph) {
    var cmPanel = document.getElementById('codemanifest-panel');
    if (cmPanel) cmPanel.remove();
    var cell = graph.cells.find(function(c) { return c.name === cell_name; });
    if (!cell) {
      document.getElementById("info").querySelector('.scroll-content').innerHTML = "<p>Cell not found</p>";
      document.getElementById("info-title").textContent = "cell info";
      return;
    }
    document.getElementById("info-title").textContent = cell.name;
    var consumers = graph.edges
      .filter(function(e) { return e.to_cell === cell_name; })
      .map(function(e) { return e.from_cell; });
    var deps = (cell.dependencies || []).map(function(d) { return d.to_cell; });
    var types = cell.types || [];
    var usages = cell.usages || [];
    var html = '<div class="section"><h2 data-icon="name">Name</h2><p>' + _esc(cell.name) + '</p></div>';
    html += '<div class="section"><h2 data-icon="description">Description</h2>';
    html += cell.description
      ? '<div class="description">' + _esc(cell.description) + '</div>'
      : '<p class="empty">No description</p>';
    html += '</div>';
    html += '<div class="section"><h2 data-icon="types">Types</h2>';
    html += types.length > 0
      ? '<ul>' + types.map(function(t) { return '<li><a class="type-link" data-type="' + _esc(t) + '">' + _esc(t) + '</a></li>'; }).join('') + '</ul>'
      : '<p class="empty">No types</p>';
    html += '</div>';
    if (usages.length > 0) {
      html += '<div class="section"><h2 data-icon="usages">Usages</h2><ul>' +
        usages.map(function(u) {
          var mdPath = cell.name + '/.usages/' + u;
          return '<li><a class="usage-link" data-path="' + _esc(mdPath) + '">' + _esc(u) + '</a></li>';
        }).join('') + '</ul></div>';
    }
    if (consumers.length > 0) {
      html += '<div class="section"><h2 data-icon="consumers">Consumers</h2><ul>' +
        consumers.map(function(c) { return '<li>' + _esc(c) + '</li>'; }).join('') + '</ul></div>';
    }
    if (deps.length > 0) {
      html += '<div class="section"><h2 data-icon="dependencies">Dependencies</h2><ul>' +
        deps.map(function(d) { return '<li>' + _esc(d) + '</li>'; }).join('') + '</ul></div>';
    }
    document.getElementById("info").querySelector('.scroll-content').innerHTML = html;
    document.getElementById("info").querySelector('.scroll-content').scrollTop = 0;
    document.querySelectorAll('#info .usage-link').forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        _open_usage(link.getAttribute('data-path'));
      });
    });
    document.querySelectorAll('#info .type-link').forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        _navigate_to_type(link.getAttribute('data-type'), cell_name, graph);
      });
    });
    var infoFooter = document.getElementById("info-footer");
    infoFooter.innerHTML = '<span class="codemanifest-link">'
      + '<img class="link-icon" src="' + codeIcon + '" alt="">'
      + 'CODEMANIFEST</span>';
    infoFooter.querySelector('.codemanifest-link').addEventListener('click', function() {
      show_codemanifest(cell_name, graph);
    });
  }

  function _highlight_yaml(text) {
    var s = _esc(text);
    var lines = s.split('\n');
    var literalIndent = -1;
    var inUsages = false;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var lineIndent = line.search(/\S/);
      if (line.trim() === '') lineIndent = 0;
      if (literalIndent >= 0) {
        if (lineIndent > literalIndent || line.trim() === '') {
          continue;
        }
        literalIndent = -1;
      }
      var commentIdx = line.indexOf('#');
      var delimMatch = line.match(/^(---)(\s*)$/);
      if (delimMatch) {
        inUsages = false;
        lines[i] = '<span class="yaml-delim">' + delimMatch[1] + '</span>' + delimMatch[2];
        continue;
      }
      if (commentIdx === 0) {
        lines[i] = '<span class="yaml-comment">' + line + '</span>';
        continue;
      }
      var keyMatch = line.match(/^(\s*(?:-\s*)?)("[^"]*"|[\w][\w.\s\-&;]*)(:)(.*)$/);
      if (keyMatch) {
        var indent = keyMatch[1];
        var key = keyMatch[2];
        var colon = keyMatch[3];
        var rest = keyMatch[4];
        var keyIndent = indent.length;
        if (key === 'Usages' && keyIndent === 0) {
          inUsages = true;
        } else if (keyIndent === 0) {
          inUsages = false;
        }
        var highlighted = indent + '<span class="yaml-key">' + key + '</span>' + colon;
        if (rest) {
          var litMatch = rest.match(/^\s*(\||>)/);
          if (litMatch) {
            rest = '<span class="yaml-literal">' + rest.trim() + '</span>';
            literalIndent = keyIndent;
          } else {
            if (inUsages && rest.trim().match(/^[\w\/.\-]+\.md$/)) {
              var mdPath = rest.trim();
              var leadingSpace = rest.substring(0, rest.length - rest.trimStart().length);
              rest = leadingSpace + '<a class="usage-link" data-path="' + mdPath + '">' + mdPath + '</a>';
            } else {
              rest = rest.replace(/\b(true|false|null)\b/g, '<span class="yaml-bool">$1</span>');
              rest = rest.replace(/\b(\d+)\b/g, '<span class="yaml-number">$1</span>');
            }
            if (rest.indexOf('#') !== -1) {
              var ci = rest.indexOf('#');
              if (!rest.substring(ci).match(/<\/span>/)) {
                rest = rest.substring(0, ci) + '<span class="yaml-comment">' + rest.substring(ci) + '</span>';
              }
            }
          }
        }
        lines[i] = highlighted + rest;
        continue;
      }
      if (commentIdx > 0) {
        var before = line.substring(0, commentIdx);
        lines[i] = before + '<span class="yaml-comment">' + line.substring(commentIdx) + '</span>';
        continue;
      }
    }
    return lines.join('\n').replace(/`([^`]+)`/g, '<span class="yaml-code">`$1`</span>');
  }

  function _show_cm_panel(rawContent, highlightType) {
    var existing = document.getElementById('codemanifest-panel');
    if (existing) existing.remove();
    var highlighted = _highlight_yaml(rawContent);
    var lines = highlighted.split('\n');
    var numsHtml = '';
    var codeHtml = '';
    for (var i = 0; i < lines.length; i++) {
      numsHtml += (i + 1) + '\n';
      codeHtml += lines[i] + '\n';
    }
    var panel = document.createElement('div');
    panel.id = 'codemanifest-panel';
    panel.innerHTML = '<div class="titlebar"><span class="title">CODEMANIFEST</span>'
      + '<button class="close">&times;</button></div>'
      + '<div class="cm-scroll-wrap"><div class="cm-scroll"><pre><div class="line-numbers">' + numsHtml + '</div>'
      + '<code class="code-content">' + codeHtml + '</code></pre></div>'
      + '<div class="cm-scroll-bar"><div class="cm-scroll-thumb"></div></div></div>';
    document.querySelector('main').appendChild(panel);
    function updatePanelRight() {
      var iw = document.getElementById('info-wrapper');
      if (!iw.classList.contains('hidden')) {
        var infoRect = iw.getBoundingClientRect();
        panel.style.right = (window.innerWidth - infoRect.left + 8) + 'px';
      } else {
        panel.style.right = '8px';
      }
    }
    updatePanelRight();
    window.addEventListener('resize', updatePanelRight);
    panel.querySelector('.close').addEventListener('click', function() {
      window.removeEventListener('resize', updatePanelRight);
      panel.remove();
    });
    var cmScroll = panel.querySelector('.cm-scroll');
    var cmThumb = panel.querySelector('.cm-scroll-thumb');
    function updateScrollbar() {
      if (!cmScroll || !cmThumb) return;
      var ratio = cmScroll.clientHeight / cmScroll.scrollHeight;
      if (ratio >= 1) {
        cmThumb.style.display = 'none';
        return;
      }
      cmThumb.style.display = '';
      var thumbH = Math.max(30, cmScroll.clientHeight * ratio);
      var scrollRatio = cmScroll.scrollTop / (cmScroll.scrollHeight - cmScroll.clientHeight);
      var thumbTop = scrollRatio * (cmScroll.clientHeight - thumbH);
      cmThumb.style.height = thumbH + 'px';
      cmThumb.style.top = thumbTop + 'px';
    }
    cmScroll.addEventListener('scroll', updateScrollbar);
    updateScrollbar();
    var dragging = false, startY = 0, startTop = 0;
    cmThumb.addEventListener('mousedown', function(e) {
      dragging = true;
      startY = e.clientY;
      startTop = parseInt(cmThumb.style.top) || 0;
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      var delta = e.clientY - startY;
      var thumbH = parseInt(cmThumb.style.height) || 30;
      var maxTop = cmScroll.clientHeight - thumbH;
      var newTop = Math.max(0, Math.min(maxTop, startTop + delta));
      cmThumb.style.top = newTop + 'px';
      cmScroll.scrollTop = (newTop / maxTop) * (cmScroll.scrollHeight - cmScroll.clientHeight);
    });
    document.addEventListener('mouseup', function() {
      dragging = false;
    });
    panel.querySelectorAll('.usage-link').forEach(function(link) {
      link.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        _open_usage(link.getAttribute('data-path'));
      });
    });
    if (highlightType) {
      _highlight_type_line(highlightType);
    }
  }

  function _highlight_type_line(typeName) {
    var codeContent = document.querySelector('#codemanifest-panel .code-content');
    if (!codeContent) return;

    var prev = codeContent.querySelector('.line-highlighted');
    if (prev) {
      prev.outerHTML = prev.innerHTML;
    }

    var lines = codeContent.innerHTML.split('\n');
    var escaped = typeName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    var pattern = new RegExp(escaped + '[^a-zA-Z0-9_]');

    var found = false;
    for (var i = 0; i < lines.length; i++) {
      var temp = document.createElement('div');
      temp.innerHTML = lines[i];
      var text = temp.textContent || temp.innerText || '';
      if (pattern.test(text)) {
        lines[i] = '<span class="line-highlighted">' + lines[i] + '</span>';
        found = true;
        break;
      }
    }

    if (found) {
      codeContent.innerHTML = lines.join('\n');
      var highlighted = codeContent.querySelector('.line-highlighted');
      if (highlighted) {
        highlighted.scrollIntoView({ block: 'center', behavior: 'smooth' });
      }
    }
  }

  function _navigate_to_type(typeName, cellName, graph) {
    var panel = document.getElementById('codemanifest-panel');
    if (!panel) {
      show_codemanifest(cellName, graph, typeName);
      return;
    }
    _highlight_type_line(typeName);
  }

  function _open_usage(mdPath) {
    fetch('/api/usage?path=' + encodeURIComponent(mdPath), {cache: 'no-store'})
      .then(function(response) {
        if (response.status === 404) return 'File not found: ' + mdPath;
        if (response.ok) return response.text();
        return 'Failed to load usage file';
      })
      .then(function(content) {
        _show_usage_modal(mdPath, content);
      })
      .catch(function() {
        _show_usage_modal(mdPath, 'Failed to load usage file');
      });
  }

  function _show_usage_modal(title, markdownContent) {
    var existing = document.getElementById('usage-overlay');
    if (existing) existing.remove();
    var fileName = title.split('/').pop();
    var htmlContent;
    try {
      htmlContent = marked.parse(markdownContent);
    } catch (e) {
      htmlContent = '<p>' + _esc(markdownContent) + '</p>';
    }
    var overlay = document.createElement('div');
    overlay.id = 'usage-overlay';
    var modal = document.createElement('div');
    modal.id = 'usage-modal';
    modal.innerHTML = '<div class="titlebar"><span class="title">' + _esc(fileName) + '</span>'
      + '<button class="close">&times;</button></div>'
      + '<div class="usage-scroll-wrap"><div class="usage-scroll"><div class="usage-content">'
      + '</div></div>'
      + '<div class="usage-scroll-bar"><div class="usage-scroll-thumb"></div></div></div>';
    modal.querySelector('.usage-content').innerHTML = htmlContent;
    overlay.appendChild(modal);
    document.querySelector('main').appendChild(overlay);
    function closeModal() {
      document.removeEventListener('keydown', onEscape);
      overlay.remove();
    }
    function onEscape(e) {
      if (e.key === 'Escape') closeModal();
    }
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) closeModal();
    });
    modal.querySelector('.close').addEventListener('click', closeModal);
    document.addEventListener('keydown', onEscape);
    var uScroll = modal.querySelector('.usage-scroll');
    var uThumb = modal.querySelector('.usage-scroll-thumb');
    function updateScrollbar() {
      if (!uScroll || !uThumb) return;
      var ratio = uScroll.clientHeight / uScroll.scrollHeight;
      if (ratio >= 1) {
        uThumb.style.display = 'none';
        return;
      }
      uThumb.style.display = '';
      var thumbH = Math.max(30, uScroll.clientHeight * ratio);
      var scrollRatio = uScroll.scrollTop / (uScroll.scrollHeight - uScroll.clientHeight);
      var thumbTop = scrollRatio * (uScroll.clientHeight - thumbH);
      uThumb.style.height = thumbH + 'px';
      uThumb.style.top = thumbTop + 'px';
    }
    uScroll.addEventListener('scroll', updateScrollbar);
    updateScrollbar();
    var dragging = false, startY = 0, startTop = 0;
    uThumb.addEventListener('mousedown', function(e) {
      dragging = true;
      startY = e.clientY;
      startTop = parseInt(uThumb.style.top) || 0;
      e.preventDefault();
    });
    document.addEventListener('mousemove', function(e) {
      if (!dragging) return;
      var delta = e.clientY - startY;
      var thumbH = parseInt(uThumb.style.height) || 30;
      var maxTop = uScroll.clientHeight - thumbH;
      var newTop = Math.max(0, Math.min(maxTop, startTop + delta));
      uThumb.style.top = newTop + 'px';
      uScroll.scrollTop = (newTop / maxTop) * (uScroll.scrollHeight - uScroll.clientHeight);
    });
    document.addEventListener('mouseup', function() {
      dragging = false;
    });
  }

  function show_codemanifest(cell_name, graph, highlightType) {
    var cell = graph.cells.find(function(c) { return c.name === cell_name; });
    if (!cell) return;
    fetch('/api/codemanifest?cell=' + encodeURIComponent(cell.name), {cache: 'no-store'})
      .then(function(response) {
        if (response.status === 404) return 'CODEMANIFEST not found';
        if (response.ok) return response.text();
        return 'Failed to load CODEMANIFEST';
      })
      .then(function(content) {
        _show_cm_panel(content, highlightType);
      })
      .catch(function() {
        _show_cm_panel('Failed to load CODEMANIFEST');
      });
  }
})();
