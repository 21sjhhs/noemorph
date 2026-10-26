/* Noemorph Knowledge Map — local, dependency-free HTML visualization plugin. */
(async function () {
  'use strict';
  const G = window.NoemorphGraph, $ = id => document.getElementById(id);
  const I = window.NoemorphI18n, L = window.NoemorphLanguages, T = value => I.t(value);
  const NS = 'http://www.w3.org/2000/svg';
  const symbols = { question: 'n', direction: '✧', concept: '◇', finding: '·', frontier: '?' };
  let model, positions, shown, selected, inspectorTab = 'insight', sceneBounds;
  let languagePack, contentLanguage = 'auto';
  let state = { mode: 'overview', expanded: new Set(), revealed: new Set(), roles: new Set(Object.keys(G.ROLES)), round: 0, status: 'all' };
  let camera = { x: 0, y: 0, k: 1 }, animation = 0, toastTimer, miniTransform;
  let drag = null, suppressClick = 0, dragDepth = 0, frame = 0, cameraFrame = 0;
  let areaSize = { width: 0, height: 0 };
  const pointers = new Map();
  const graph = $('graph'), area = $('map-area'), viewport = $('viewport');
  const nodeElements = new Map(), nodeAnnotations = new Map(), edgeElements = new Map();
  function el(tag, attrs = {}, ...children) {
    const n = document.createElement(tag);
    for (const [key, val] of Object.entries(attrs)) {
      if (key === 'class') n.className = val;
      else if (key.startsWith('on')) n.addEventListener(key.slice(2), val);
      else n.setAttribute(key, String(val));
    }
    for (const c of children.flat()) if (c != null) n.append(c instanceof Node ? c : document.createTextNode(String(c)));
    return n;
  }
  function svg(tag, attrs = {}, text) {
    const n = document.createElementNS(NS, tag);
    for (const [key, val] of Object.entries(attrs)) n.setAttribute(key, String(val));
    if (text != null) n.textContent = text;
    return n;
  }
  function toast(message) { $('toast').textContent = T(message); $('toast').hidden = false; clearTimeout(toastTimer); toastTimer = setTimeout(() => $('toast').hidden = true, 4500); }
  function format(value) { return typeof value === 'string' ? value : value == null ? '' : JSON.stringify(value, null, 2); }
  function text(id, value) { $(id).textContent = ['project-title','question-title'].includes(id) ? value : T(value); }
  function radius(n) { return n.type === 'question' ? 37 : n.importance >= 4 ? 23 : n.type === 'finding' ? 13 : 16; }
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function isMobileInspector() { return matchMedia('(max-width:1060px)').matches; }
  function setInspector(open) { $('workspace').classList.toggle('inspector-closed', !open); $('inspector').hidden = !open; $('reopen-inspector').hidden = open; }
  async function mount(data) {
    // Validate before replacing the current, usable document.
    if (data.schema_version === '1.0' && data.meta?.translation && languagePack) {
      if (data.meta.translation.source_fingerprint !== languagePack.sourceFingerprint) throw new Error(T('语言版本与当前研究不匹配。请先打开对应原图。'));
      const code = L.tag(data.meta.language), graphs = languagePack.data.graphs.filter(g => g.meta.language !== code);
      const nextPack = await L.prepare({ ...languagePack.data, graphs: [...graphs, data] });
      languagePack = nextPack; contentLanguage = code; switchContent(); toast(I.t('已加入 {language} 图谱版本。', { language: languageName(code) })); return;
    }
    const nextPack = await L.prepare(data), view = nextPack.data.view || {};
    const requested = nextPack.models.has(view.content_language) ? view.content_language : 'auto';
    const next = nextPack.models.get(L.resolve(nextPack, requested, I.getLanguage()));
    const nextPositions = G.layout(next, view.positions);
    languagePack = nextPack; contentLanguage = requested; model = next; positions = nextPositions;
    state = { mode: ['overview', 'all', 'frontier'].includes(view.mode) ? view.mode : 'overview',
      expanded: new Set((Array.isArray(view.expanded) ? view.expanded : []).filter(id => model.byId.has(id))),
      revealed: new Set((Array.isArray(view.revealed) ? view.revealed : []).filter(id => model.byId.has(id))),
      roles: new Set(Object.keys(G.ROLES)), round: 0, status: 'all' };
    selected = model.byId.has(view.selected) ? view.selected : model.root.id;
    inspectorTab = 'insight';
    $('status-filter').value = 'all'; $('search-input').value = ''; $('search-results').hidden = true;
    refreshHeader(); buildLanguageControl(); I.applyStatic(document); buildFilters(); render(); renderInspector(); fit(false);
    const { width, height } = area.getBoundingClientRect(); areaSize = { width, height };
    const missing = L.missingLanguages(languagePack);
    if (missing.length) toast(I.t('图谱缺少完整语言版本：{languages}。请生成并导入翻译。', { languages: missing.join(', ') }));
  }
  function refreshHeader() {
    text('project-title', model.data.meta.title || T('知识探索地图'));
    text('project-subtitle', T(`${model.data.meta.rounds || Math.max(0, ...model.data.nodes.map(n => Number(n.round) || 0))} 轮探索 · ${model.data.nodes.length} 个节点`));
    text('question-title', model.data.meta.question || model.root.label);
    text('stat-nodes', model.data.nodes.length); text('stat-links', model.data.edges.length);
    text('stat-frontier', model.data.nodes.filter(n => n.type === 'direction' && n.status === 'frontier').length);
    $('demo-notice').hidden = !model.data.meta.demo;
    text('overview-count', model.data.nodes.filter(n => n.importance >= 4).length);
    text('all-count', model.data.nodes.length); text('frontier-count', model.data.nodes.filter(G.isFrontier).length);
    const warnings = model.data.meta.warnings || [];
    text('status-message', model.data.meta.demo ? T('交互演示 · 所有示例发现仅用于展示界面') : warnings.length ? T(`已载入研究记录 · ${warnings.length} 条导入说明，详见主问题节点`) : T('本地图谱 · 阅读优先级与证据等级分别呈现'));
    document.title = `${model.data.meta.title || 'Knowledge map'} · Noemorph — Multi-Agent Knowledge Exploration`;
    graph.setAttribute('aria-label', T('知识图谱。拖动空白移动，滚轮缩放；Tab 选择节点，Enter 打开详情。'));
    document.querySelectorAll('[data-ui-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.uiLang === I.getLanguage())));
    const miniHidden = $('minimap').hasAttribute('hidden');
    $('minimap-toggle').setAttribute('aria-label', T(miniHidden ? '展开缩略导航' : '收起缩略导航'));
  }
  function languageName(code) {
    if (code === 'und') return T('原始记录（混合 / 未标注）');
    const variant = languagePack?.data.graphs.find(g => g.meta.language === code);
    return variant?.meta.language_label || code;
  }
  function buildLanguageControl() {
    const control = $('content-language');
    control.replaceChildren(el('option', { value: 'auto' }, T('跟随界面') + ' · ' + languageName(model.data.meta.language)),
      ...[...languagePack.models.keys()].map(code => el('option', { value: code }, languageName(code) + (code === 'und' ? '' : ` [${code}]`))));
    control.value = contentLanguage; control.title = T('图谱内容语言') + ': ' + languageName(model.data.meta.language); control.setAttribute('aria-label', T('图谱内容语言'));
  }
  function switchContent() {
    cancelAnimationFrame(animation);
    model = languagePack.models.get(L.resolve(languagePack, contentLanguage, I.getLanguage()));
    refreshHeader(); buildLanguageControl(); buildFilters(); render(); renderInspector();
  }
  function changeInterfaceLanguage(code) {
    I.setLanguage(code); I.applyStatic(document); switchContent();
    if (contentLanguage === 'auto' && model.data.meta.language.split('-')[0] !== code.split('-')[0]) toast(I.t('此语言版本尚未生成，内容继续使用 {language}。', { language: languageName(model.data.meta.language) }));
  }
  function buildFilters() {
    const filters = $('role-filters'); filters.replaceChildren();
    for (const [role, info] of Object.entries(G.ROLES)) {
      const count = model.data.nodes.filter(n => n.role === role).length;
      if (!count) continue;
      const button = el('button', { class: 'role-filter', 'data-role': role, 'aria-pressed': state.roles.has(role), onclick: () => {
        state.roles.has(role) ? state.roles.delete(role) : state.roles.add(role); buildFilters(); render(); fit();
      } }, el('span', { class: 'role-dot', style: `--role:${info.color}` }), T(info.label),
        el('span', { class: 'role-count' }, count), el('span', { class: 'role-check', 'aria-hidden': true }, state.roles.has(role) ? '✓' : ''));
      filters.append(button);
    }
    const rounds = [...new Set(model.data.nodes.map(n => Number(n.round)).filter(n => n > 0))].sort((a, b) => a - b);
    $('round-filters').replaceChildren(...[0, ...rounds].map(round => el('button', {
      class: state.round === round ? 'active' : '', 'aria-pressed': state.round === round,
      onclick: () => { state.round = round; buildFilters(); render(); fit(); }
    }, round ? `R${String(round).padStart(2, '0')}` : T('全部'))));
    text('round-caption', state.round ? `ROUND ${state.round}` : 'ALL ROUNDS');
  }
  function setMode(mode) { state.mode = mode; state.expanded.clear(); state.revealed.clear(); render(); renderInspector(); fit(); $('workspace').classList.remove('sidebar-open'); }
  function resetFilters() { state.roles = new Set(Object.keys(G.ROLES)); state.round = 0; state.status = 'all'; $('status-filter').value = 'all'; buildFilters(); render(); fit(); }
  function render() {
    shown = G.visibleGraph(model, state);
    $('edge-layer').replaceChildren(); $('node-layer').replaceChildren(); nodeElements.clear(); nodeAnnotations.clear(); edgeElements.clear();
    document.querySelectorAll('[data-view]').forEach(b => { b.classList.toggle('active', b.dataset.view === state.mode); b.setAttribute('aria-pressed', String(b.dataset.view === state.mode)); });
    const names = { overview: T('主要发现'), all: T('完整网络'), frontier: T('待探索分支') };
    text('view-title', names[state.mode]); text('visible-count', `${shown.nodes.length} / ${model.data.nodes.length}`);
    $('empty-state').hidden = shown.nodes.some(n => n.id !== model.root.id) || model.data.nodes.length === 1;
    for (const e of shown.edges) {
      const group = svg('g', { class: 'edge' });
      const path = svg('path', { class: `edge-path ${e.kind}`, 'marker-end': 'url(#edge-arrow)' });
      const label = svg('text', { class: 'edge-label' }, G.wrapLabel(e.label, 18, 1)[0]);
      group.append(path, label); $('edge-layer').append(group); edgeElements.set(e.id, { group, path, label, e });
    }
    for (const n of shown.nodes) {
      const r = radius(n), role = G.ROLES[n.role];
      const group = svg('g', { class: `node ${n.type} ${n.status}${n.importance >= 4 ? ' primary' : ''}`, 'data-node-id': n.id, tabindex: '0', role: 'button', 'aria-label': `${n.label}，${T(G.STATUSES[n.status])}，${T(G.EVIDENCE[n.evidence])}`, style: `--node-color:${role.color}` });
      group.append(svg('title', {}, n.label), svg('circle', { class: 'halo', r: r + 20, filter: 'url(#node-glow)' }),
        svg('circle', { class: 'orbit', r: r + 9 }), svg('circle', { class: 'disc', r }), svg('circle', { class: 'inner-disc', r: r - 4 }),
        svg('text', { class: 'node-symbol', y: n.type === 'question' ? -1 : 0 }, symbols[n.type] || '◇'));
      const lines = G.wrapLabel(n.label, n.type === 'question' ? 25 : 26, 3);
      const annotation = svg('g', { class: 'node-annotation' });
      const label = svg('text', { class: 'node-label', y: 0 });
      lines.forEach((line, i) => label.append(svg('tspan', { x: 0, dy: i ? 16 : 0 }, line)));
      annotation.append(label, svg('text', { class: 'node-meta', y: 3 + lines.length * 16 }, n.type === 'question' ? T('原始问题') : `${n.round ? `R${n.round} · ` : ''}${n.type === 'finding' ? T(G.EVIDENCE[n.evidence]) : T(G.STATUSES[n.status])}`));
      group.append(annotation); nodeAnnotations.set(n.id, { element: annotation, label, node: n, offset: r + 23, compact: null });
      const children = model.children.get(n.id) || [], hidden = children.filter(id => !shown.ids.has(id));
      if (children.length && (hidden.length || state.expanded.has(n.id))) {
        const badge = svg('g', { class: 'expand-badge', transform: `translate(${r - 1},${-r + 1})`, role: 'button', tabindex: '0', 'aria-label': hidden.length ? T(`展开 ${hidden.length} 个下级线索`) : T('收起下级线索') });
        badge.append(svg('circle', { r: 10 }), svg('text', {}, hidden.length ? `+${hidden.length}` : '−'));
        badge.addEventListener('pointerdown', event => { event.stopPropagation(); cancelAnimationFrame(animation); });
        badge.addEventListener('click', event => { event.stopPropagation(); if (Date.now() < suppressClick) return; toggleExpand(n.id); });
        badge.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); event.stopPropagation(); toggleExpand(n.id); } });
        group.append(badge);
      }
      const jump = n.links.find(l => G.safeURL(l.url) && l.kind === 'source') || n.links.find(l => G.safeURL(l.url));
      if (jump) {
        const a = svg('a', { class: 'node-link-button', href: jump.url, target: '_blank', rel: 'noopener noreferrer', transform: `translate(${-r - 7},${-r + 2})`, 'aria-label': T(`打开${jump.label || T('参考资料')}`) });
        a.append(svg('title', {}, jump.label || T('打开参考资料')), svg('circle', { r: 9 }), svg('text', {}, '↗'));
        a.addEventListener('click', event => event.stopPropagation()); group.append(a);
      }
      group.addEventListener('click', event => { if (Date.now() < suppressClick || event.target.closest('a')) return; select(n.id, false); });
      group.addEventListener('dblclick', event => { event.preventDefault(); if (!event.target.closest('a')) toggleExpand(n.id); });
      group.addEventListener('keydown', event => {
        if (event.target !== group) return;
        if (event.key === 'Enter') { event.preventDefault(); select(n.id, false); }
        if (event.key === ' ') { event.preventDefault(); toggleExpand(n.id); }
      });
      group.addEventListener('mouseenter', () => highlight(n.id)); group.addEventListener('mouseleave', () => highlight(selected));
      $('node-layer').append(group); nodeElements.set(n.id, group);
    }
    updateGeometry(); updateCamera(); highlight(selected);
  }
  function updateGeometry() {
    for (const [id, element] of nodeElements) { const p = positions.get(id); element.setAttribute('transform', `translate(${p.x},${p.y})`); }
    for (const { e, path, label } of edgeElements.values()) {
      const a = positions.get(e.source), b = positions.get(e.target), dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy) || 1;
      const ra = radius(model.byId.get(e.source)) + 4, rb = radius(model.byId.get(e.target)) + 7;
      const x1 = a.x + dx / distance * ra, y1 = a.y + dy / distance * ra, x2 = b.x - dx / distance * rb, y2 = b.y - dy / distance * rb;
      const bend = e.kind === 'path' ? .07 : .23, cx = (x1 + x2) / 2 - dy * bend, cy = (y1 + y2) / 2 + dx * bend;
      path.setAttribute('d', `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`);
      label.setAttribute('x', (x1 + x2 + 2 * cx) / 4); label.setAttribute('y', (y1 + y2 + 2 * cy) / 4 - 7);
    }
    sceneBounds = G.bounds(shown.nodes, positions); drawMinimap();
  }
  function highlight(id) {
    const connected = new Set([id]);
    for (const e of shown.edges) if (e.source === id || e.target === id) { connected.add(e.source); connected.add(e.target); }
    for (const [nid, element] of nodeElements) { element.classList.toggle('selected', nid === selected); element.classList.toggle('dim', id !== model.root.id && shown.ids.has(id) && !connected.has(nid)); }
    for (const { e, path, group } of edgeElements.values()) { const active = e.source === id || e.target === id; path.classList.toggle('highlight', active); group.classList.toggle('dim', id !== model.root.id && shown.ids.has(id) && !active); }
  }
  function select(id, center = true) {
    if (!model.byId.has(id)) return;
    selected = id; inspectorTab = 'insight';
    if (!shown.ids.has(id)) {
      state.revealed.add(id);
      state.roles.add(model.byId.get(id).role); state.round = 0; state.status = 'all'; $('status-filter').value = 'all';
      buildFilters(); render();
    }
    setInspector(true); renderInspector(); highlight(id);
    if (center) { const p = positions.get(id), rect = area.getBoundingClientRect(); moveCamera({ x: rect.width / 2 - p.x * Math.max(.65, camera.k), y: rect.height * .44 - p.y * Math.max(.65, camera.k), k: Math.max(.65, camera.k) }); }
  }
  function toggleExpand(id) {
    if (!(model.children.get(id) || []).length) { select(id, false); toast(T('这是当前记录的末端线索。下一问可在节点详情中查看。')); return; }
    if (state.mode === 'all') state.mode = 'overview';
    if (state.expanded.has(id)) { state.expanded.delete(id); for (const descendant of G.descendants(model, id)) { state.expanded.delete(descendant); state.revealed.delete(descendant); } }
    else { state.revealed.add(id); state.expanded.add(id); }
    selected = id; render(); renderInspector(); fit();
  }
  function renderInspector() {
    const n = model.byId.get(selected) || model.root, info = G.ROLES[n.role], container = $('inspector-content'); container.replaceChildren();
    container.append(el('div', { class: 'node-kicker' }, el('span', { class: 'role-dot', style: `--role:${info.color}` }), T(info.label),
      el('span', { class: 'node-number' }, `${String(model.data.nodes.indexOf(n) + 1).padStart(2, '0')} / ${model.data.nodes.length}`)), el('h2', {}, n.label));
    container.append(el('div', { class: 'node-badges' }, el('span', { class: 'badge' }, n.type === 'question' ? T('研究起点') : T(G.STATUSES[n.status])),
      ...(n.type === 'question' ? [] : [el('span', { class: `badge ${['verified_direct', 'supported_with_limits'].includes(n.evidence) ? 'evidence' : 'uncertain'}` }, T(G.EVIDENCE[n.evidence]))]),
      ...(n.round ? [el('span', { class: 'badge' }, T(`第 ${n.round} 轮`))] : [])));
    const connections = model.data.edges.filter(e => e.source === n.id || e.target === n.id);
    container.append(el('div', { class: 'inspector-tabs' }, ...[['insight', T('线索详情')], ['connections', T(`连接 · ${connections.length}`)]].map(([tab, label]) =>
      el('button', { class: inspectorTab === tab ? 'active' : '', 'aria-pressed': inspectorTab === tab, onclick: () => { inspectorTab = tab; renderInspector(); } }, label))));
    if (inspectorTab === 'connections') {
      for (const e of connections) {
        const other = model.byId.get(e.source === n.id ? e.target : e.source);
        container.append(el('button', { class: 'connection-card', onclick: () => select(other.id) }, el('small', {}, T(`${e.source === n.id ? '→' : '←'} ${e.label} · ${e.kind === 'path' ? T('记录中的探索路径') : e.kind}`)), other.label));
      }
      if (!connections.length) container.append(el('p', { class: 'reference-empty' }, T('当前没有记录关联。')));
      return;
    }
    container.append(el('p', { class: 'inspector-description' }, format(n.summary) || T('此节点保留为研究线索；尚未记录详细结论。')));
    const scale = el('div', { class: 'importance-scale', 'aria-label': T(`阅读优先级 ${n.importance} / 5`) }, ...[1, 2, 3, 4, 5].map(i => el('i', { class: i <= n.importance ? 'filled' : '' })));
    container.append(el('section', { class: 'inspector-section' }, el('h3', {}, T('图谱中的阅读优先级'), el('span', {}, `${n.importance} / 5`)), scale, el('div', { class: 'importance-note' }, T('表示展示主次，不代表证据更强。'))));
    const path = G.ancestors(model, n.id).reverse();
    if (path.length) container.append(el('section', { class: 'inspector-section' }, el('h3', {}, T('回溯研究路径')), el('div', { class: 'path-crumbs' }, ...path.flatMap(id => [el('button', { onclick: () => select(id) }, model.byId.get(id).label), el('span', {}, '›')]), el('span', {}, T('当前线索')))));
    const links = el('section', { class: 'inspector-section' }, el('h3', {}, T('参考资料与原始文件'), el('span', {}, String(n.links.length).padStart(2, '0'))));
    for (const link of n.links) {
      const url = G.safeURL(link.url), card = el('div', { class: 'reference-card' }, el('div', { class: 'reference-title' }, el('span', {}, link.kind === 'file' ? '▤' : '↗'), el('span', {}, link.label || T('参考资料'))));
      if (url) {
        let domain = T('本地研究文件');
        try { const u = new URL(url, document.baseURI); if (/^https?:$/.test(u.protocol) && /^https?:/i.test(url)) domain = u.hostname; } catch (_) { /* validated above */ }
        card.append(el('small', {}, domain), el('a', { href: url, target: '_blank', rel: 'noopener noreferrer' }, link.kind === 'file' ? T('打开文件') : T('打开来源'), ' ↗'));
      } else card.append(el('small', {}, link.note || T('来源标识尚未解析为链接')));
      links.append(card);
    }
    if (!n.links.length) links.append(el('p', { class: 'reference-empty' }, T('尚无可跳转的资料。此处不会自动生成引用或补造来源。')));
    container.append(links);
    const kids = model.children.get(n.id) || [], hidden = kids.filter(id => !shown.ids.has(id));
    if (n.next_question || hidden.length) container.append(el('div', { class: 'next-question' }, el('span', {}, T('下一问')),
      el('p', {}, format(n.next_question) || T(`${hidden.length} 条已记录的下级线索尚未展开。它们会把这个问题带向哪里？`)),
      ...(hidden.length ? [el('button', { onclick: () => toggleExpand(n.id) }, T(`展开 ${hidden.length} 条线索 →`))] : [])));
    container.append(el('div', { class: 'inspector-actions' }, el('button', { onclick: () => select(n.id) }, T('定位此节点 ⌖')),
      el('button', { onclick: () => toggleExpand(n.id), ...(kids.length && (hidden.length || state.expanded.has(n.id)) ? {} : { disabled: true }) }, !kids.length ? T('无下级线索') : hidden.length ? T('展开下级 +') : state.expanded.has(n.id) ? T('收起下级 −') : T('下级已展示'))));
    if (n.details && Object.keys(n.details).length) container.append(el('details', { class: 'inspector-details' }, el('summary', {}, T('查看原始逻辑与边界记录')), el('dl', {}, ...Object.entries(n.details).flatMap(([k, v]) => [el('dt', {}, k), el('dd', {}, format(v))]))));
    if (n.id === model.root.id && (model.data.meta.warnings || []).length) container.append(el('details', { class: 'inspector-details' }, el('summary', {}, T(`导入说明 · ${model.data.meta.warnings.length}`)), ...model.data.meta.warnings.map(w => el('p', { class: 'importance-note' }, w))));
    container.append(el('div', { class: 'origin-id' }, `NODE / ${n.id}`, el('br'), T(`ORIGIN / ${(n.origin_ids || []).join(' · ') || T('原始问题')}`)));
  }
  function scheduleCamera() {
    if (!cameraFrame) cameraFrame = requestAnimationFrame(() => { cameraFrame = 0; updateCamera(); });
  }
  function updateCamera() {
    cancelAnimationFrame(cameraFrame); cameraFrame = 0;
    viewport.setAttribute('transform', `translate(${camera.x},${camera.y}) scale(${camera.k})`);
    const labelScale = Math.max(.7, Math.min(2.2, 1 / camera.k)), compact = camera.k < .82;
    graph.classList.toggle('lod-compact', compact);
    for (const info of nodeAnnotations.values()) {
      if (info.compact !== compact) {
        const lines = G.wrapLabel(info.node.label, info.node.type === 'question' ? 25 : 26, compact ? 2 : 3);
        info.label.replaceChildren(...lines.map((line, i) => svg('tspan', { x: 0, dy: i ? 16 : 0 }, line)));
        info.lines = lines.length; info.compact = compact;
      }
      const above = compact && positions.get(info.node.id).y < positions.get(model.root.id).y - 30;
      const offset = above ? -radius(info.node) - 16 - (info.lines - 1) * 16 * labelScale : info.offset;
      const transform = `translate(0,${offset}) scale(${labelScale})`;
      if (info.transform !== transform) { info.element.setAttribute('transform', transform); info.transform = transform; }
    }
    text('zoom-level', `${Math.round(camera.k * 100)}%`); graph.classList.toggle('lod-low', camera.k < .55); updateMiniViewport();
  }
  function moveCamera(target, animate = true) {
    cancelAnimationFrame(animation);
    target.k = Math.min(3.5, Math.max(.08, target.k));
    if (!animate || matchMedia('(prefers-reduced-motion:reduce)').matches) { camera = target; updateCamera(); return; }
    const start = { ...camera }, time = performance.now();
    function tick(now) { const progress = Math.min(1, (now - time) / 280), t = 1 - (1 - progress) ** 3;
      camera = { x: start.x + (target.x - start.x) * t, y: start.y + (target.y - start.y) * t, k: start.k + (target.k - start.k) * t }; updateCamera(); if (progress < 1) animation = requestAnimationFrame(tick); }
    animation = requestAnimationFrame(tick);
  }
  function fit(animate = true) {
    if (!shown) return;
    const rect = area.getBoundingClientRect(), b = G.bounds(shown.nodes, positions), padX = rect.width < 600 ? 35 : 65, padY = 140;
    const k = Math.min(1.3, Math.max(.08, Math.min((rect.width - padX * 2) / b.width, (rect.height - padY) / b.height)));
    moveCamera({ k, x: rect.width / 2 - (b.x + b.width / 2) * k, y: rect.height * .47 - (b.y + b.height / 2) * k }, animate);
  }
  function zoom(factor, point, defer = false) {
    cancelAnimationFrame(animation);
    const rect = area.getBoundingClientRect(), at = point || { x: rect.width / 2, y: rect.height / 2 }, k = Math.max(.08, Math.min(3.5, camera.k * factor));
    camera = { x: at.x - (at.x - camera.x) * k / camera.k, y: at.y - (at.y - camera.y) * k / camera.k, k }; defer ? scheduleCamera() : updateCamera();
  }
  function localPoint(event) { const r = graph.getBoundingClientRect(); return { x: event.clientX - r.left, y: event.clientY - r.top }; }
  function worldPoint(event) { const p = localPoint(event); return { x: (p.x - camera.x) / camera.k, y: (p.y - camera.y) / camera.k }; }
  function drawMinimap() {
    if (!shown) return;
    const mini = $('minimap'); mini.replaceChildren(); const b = sceneBounds, k = Math.min(166 / b.width, 96 / b.height);
    miniTransform = { k, x: 90 - (b.x + b.width / 2) * k, y: 56 - (b.y + b.height / 2) * k };
    const point = p => ({ x: p.x * k + miniTransform.x, y: p.y * k + miniTransform.y });
    for (const e of shown.edges) { const a = point(positions.get(e.source)), z = point(positions.get(e.target)); mini.append(svg('line', { x1: a.x, y1: a.y, x2: z.x, y2: z.y, stroke: css('--edge-color'), 'stroke-width': .5 })); }
    for (const n of shown.nodes) { const p = point(positions.get(n.id)); mini.append(svg('circle', { cx: p.x, cy: p.y, r: n.id === model.root.id ? 2.5 : n.importance >= 4 ? 1.8 : 1, fill: css(G.ROLES[n.role].color.slice(4, -1)) })); }
    mini.append(svg('rect', { id: 'mini-viewport', class: 'minimap-viewport' })); updateMiniViewport();
  }
  function updateMiniViewport() {
    const box = $('mini-viewport'); if (!box || !miniTransform) return;
    const { k, x, y } = miniTransform, rect = area.getBoundingClientRect();
    const left = Math.max(0, -camera.x / camera.k * k + x), top = Math.max(0, -camera.y / camera.k * k + y);
    const right = Math.min(180, (rect.width - camera.x) / camera.k * k + x), bottom = Math.min(112, (rect.height - camera.y) / camera.k * k + y);
    box.setAttribute('x', left); box.setAttribute('y', top); box.setAttribute('width', Math.max(0, right - left)); box.setAttribute('height', Math.max(0, bottom - top));
  }
  // Normalize pixel/line/page devices, bound extreme deltas, and paint at most once per frame.
  area.addEventListener('wheel', event => {
    event.preventDefault();
    if (!Number.isFinite(event.deltaY) || event.deltaY === 0) return;
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? graph.clientHeight : 1;
    const delta = Math.max(-240, Math.min(240, event.deltaY * unit));
    zoom(Math.exp(-delta * .0014), localPoint(event), true);
  }, { passive: false });
  graph.addEventListener('pointerdown', event => {
    if (event.button !== 0 || event.target.closest('a')) return;
    cancelAnimationFrame(animation); pointers.set(event.pointerId, localPoint(event));
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()]; drag = { type: 'pinch', distance: Math.hypot(a.x - b.x, a.y - b.y), center: { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, camera: { ...camera }, moved: true }; return;
    }
    const node = event.target.closest('.node'), p = worldPoint(event);
    drag = { type: node && !event.target.closest('.expand-badge') ? 'node' : 'pan', id: node?.dataset.nodeId,
      start: localPoint(event), world: p, camera: { ...camera }, position: node ? { ...positions.get(node.dataset.nodeId) } : null, moved: false };
  });
  graph.addEventListener('pointermove', event => {
    if (!drag || !pointers.has(event.pointerId)) return;
    const p = localPoint(event); pointers.set(event.pointerId, p);
    if (drag.type === 'pinch' && pointers.size >= 2) {
      const [a, b] = [...pointers.values()], mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }, k = Math.max(.08, Math.min(3.5, drag.camera.k * Math.hypot(a.x - b.x, a.y - b.y) / (drag.distance || 1)));
      camera = { k, x: mid.x - (drag.center.x - drag.camera.x) * k / drag.camera.k, y: mid.y - (drag.center.y - drag.camera.y) * k / drag.camera.k }; scheduleCamera(); return;
    }
    if (drag.type === 'pinch') return;
    const dx = p.x - drag.start.x, dy = p.y - drag.start.y;
    if (Math.hypot(dx, dy) > 4) { drag.moved = true; graph.setPointerCapture(event.pointerId); graph.classList.add('dragging'); }
    if (!drag.moved) return;
    if (drag.type === 'pan') { camera.x = drag.camera.x + dx; camera.y = drag.camera.y + dy; scheduleCamera(); }
    else { positions.set(drag.id, { x: drag.position.x + dx / camera.k, y: drag.position.y + dy / camera.k });
      if (!frame) frame = requestAnimationFrame(() => { frame = 0; updateGeometry(); }); }
  });
  function endPointer(event) {
    if (drag?.moved) suppressClick = Date.now() + 200;
    pointers.delete(event.pointerId); if (graph.hasPointerCapture(event.pointerId)) graph.releasePointerCapture(event.pointerId);
    if (pointers.size === 0) { drag = null; graph.classList.remove('dragging'); }
  }
  graph.addEventListener('pointerup', endPointer); graph.addEventListener('pointercancel', endPointer);
  $('minimap').addEventListener('click', event => {
    const rect = $('minimap').getBoundingClientRect(), x = (event.clientX - rect.left) / rect.width * 180, y = (event.clientY - rect.top) / rect.height * 112;
    const world = { x: (x - miniTransform.x) / miniTransform.k, y: (y - miniTransform.y) / miniTransform.k }, a = area.getBoundingClientRect();
    moveCamera({ ...camera, x: a.width / 2 - world.x * camera.k, y: a.height / 2 - world.y * camera.k });
  });
  $('minimap').addEventListener('keydown', event => { if (event.key === 'Enter') fit(); });
  $('minimap-toggle').onclick = () => { const hidden = !$('minimap').hasAttribute('hidden'); $('minimap').toggleAttribute('hidden', hidden); $('minimap-toggle').setAttribute('aria-expanded', String(!hidden)); $('minimap-toggle').setAttribute('aria-label', hidden ? T('展开缩略导航') : T('收起缩略导航')); $('minimap-toggle').textContent = hidden ? '+' : '−'; };
  document.querySelectorAll('[data-view]').forEach(b => b.addEventListener('click', () => setMode(b.dataset.view)));
  $('reset-filters').onclick = resetFilters; $('empty-reset').onclick = resetFilters;
  $('status-filter').onchange = event => { state.status = event.target.value; if (state.status !== 'all') state.mode = 'all'; render(); renderInspector(); fit(); };
  $('fit-button').onclick = () => fit(); $('zoom-in').onclick = () => zoom(1.25); $('zoom-out').onclick = () => zoom(.8); $('zoom-level').onclick = () => zoom(1 / camera.k);
  $('labels-button').onclick = () => { const hidden = graph.classList.toggle('hide-edge-labels'); $('labels-button').classList.toggle('active', !hidden); $('labels-button').setAttribute('aria-pressed', String(!hidden)); };
  $('close-inspector').onclick = () => setInspector(false); $('reopen-inspector').onclick = () => setInspector(true);
  $('menu-button').onclick = () => $('workspace').classList.toggle('sidebar-open');
  $('brand-home').onclick = event => { event.preventDefault(); resetFilters(); setMode('overview'); select(model.root.id, false); };
  $('project-home').onclick = () => select(model.root.id);
  $('help-button').onclick = () => $('help-dialog').showModal(); $('close-help').onclick = () => $('help-dialog').close();
  $('help-dialog').onclick = event => { if (event.target === $('help-dialog')) { const b = $('help-dialog').getBoundingClientRect(); if (event.clientX < b.left || event.clientX > b.right || event.clientY < b.top || event.clientY > b.bottom) $('help-dialog').close(); } };
  $('theme-button').onclick = () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; try { localStorage.setItem('noemorph-theme', theme); } catch (_) {} drawMinimap(); };
  $('fullscreen-button').onclick = async () => { try { if (document.fullscreenElement) await document.exitFullscreen(); else if (area.requestFullscreen) await area.requestFullscreen(); else toast(T('当前浏览器不支持全屏，可使用窗口最大化。')); } catch (_) { toast(T('当前浏览器未允许全屏。')); } };
  document.addEventListener('fullscreenchange', () => fit());
  $('search-input').addEventListener('input', () => {
    const input = $('search-input'), results = $('search-results'), matches = G.search(model, input.value); results.replaceChildren(); results.hidden = !input.value.trim();
    for (const n of matches) results.append(el('button', { role: 'option', onclick: () => { results.hidden = true; input.value = ''; input.blur(); select(n.id); } },
      el('span', { class: 'role-dot', style: `--role:${G.ROLES[n.role].color};margin-top:5px` }), el('span', {}, n.label, el('small', {}, T(`${T(G.ROLES[n.role].label)} · ${T(G.STATUSES[n.status])}${shown.ids.has(n.id) ? '' : T(' · 当前已折叠')}`)))));
    if (!matches.length) results.append(el('p', {}, T('没有找到匹配的线索。试试原始方向 ID。')));
  });
  $('search-input').addEventListener('keydown', event => { if (event.key === 'ArrowDown') { event.preventDefault(); $('search-results').querySelector('button')?.focus(); } if (event.key === 'Enter') $('search-results').querySelector('button')?.click(); });
  $('search-results').addEventListener('keydown', event => { const buttons = [...$('search-results').querySelectorAll('button')], i = buttons.indexOf(document.activeElement); if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); buttons[(i + (event.key === 'ArrowDown' ? 1 : buttons.length - 1)) % buttons.length]?.focus(); } });
  document.addEventListener('keydown', event => {
    const editing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName);
    if (event.key === 'Escape') { $('search-results').hidden = true; $('export-menu').hidden = true; $('workspace').classList.remove('sidebar-open'); if (!$('help-dialog').open && !$('run-dialog').open) setInspector(false); }
    if (editing || $('help-dialog').open || $('run-dialog').open) return;
    if (event.key === '/') { event.preventDefault(); $('search-input').focus(); }
    if (event.key.toLowerCase() === 'f' && !event.ctrlKey && !event.metaKey) { event.preventDefault(); fit(); }
  });
  document.addEventListener('click', event => { if (!event.target.closest('.search-box')) $('search-results').hidden = true; if (!event.target.closest('.topbar-actions')) { $('export-menu').hidden = true; $('export-button').setAttribute('aria-expanded', 'false'); } });
  async function importFile(file) {
    if (!file) return;
    if (file.size > 25 * 1024 * 1024) { toast(T('文件超过 25 MB，请按研究批次导出。')); return; }
    try { const data = JSON.parse(await file.text()); await mount(data); setInspector(!isMobileInspector()); toast(T(`已打开 ${model.data.nodes.length} 个知识节点，完整数据保留在本地。`)); }
    catch (error) { toast(T(`导入失败：${error.message}`)); }
    finally { $('file-input').value = ''; }
  }
  $('import-button').onclick = () => $('file-input').click(); $('file-input').onchange = event => importFile(event.target.files[0]);
  document.addEventListener('dragenter', event => { if (!event.dataTransfer?.types.includes('Files')) return; event.preventDefault(); dragDepth++; $('drop-target').hidden = false; });
  document.addEventListener('dragover', event => { if (event.dataTransfer?.types.includes('Files')) event.preventDefault(); });
  document.addEventListener('dragleave', () => { if (--dragDepth <= 0) { dragDepth = 0; $('drop-target').hidden = true; } });
  document.addEventListener('drop', event => { event.preventDefault(); dragDepth = 0; $('drop-target').hidden = true; importFile(event.dataTransfer?.files[0]); });
  function snapshot() {
    return { ...languagePack.data, view: { mode: state.mode, selected, expanded: [...state.expanded], revealed: [...state.revealed], positions: Object.fromEntries(positions), theme: document.documentElement.dataset.theme, ui_language: I.getLanguage(), content_language: contentLanguage } };
  }
  function download(content, type, filename) {
    const blob = new Blob([content], { type }), url = URL.createObjectURL(blob), link = el('a', { href: url, download: filename }); document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
  async function exportHTML() {
    const clone = document.documentElement.cloneNode(true);
    for (const stylesheet of clone.querySelectorAll('link[rel="stylesheet"]')) {
      const response = await fetch(new URL(stylesheet.getAttribute('href'), document.baseURI)); if (!response.ok) throw new Error(T('无法读取样式'));
      const style = document.createElement('style'); style.textContent = await response.text(); stylesheet.replaceWith(style);
    }
    for (const script of clone.querySelectorAll('script[src]')) {
      if (script.getAttribute('src').endsWith('demo.js')) { script.remove(); continue; }
      const response = await fetch(new URL(script.getAttribute('src'), document.baseURI)); if (!response.ok) throw new Error(T('无法读取插件'));
      script.textContent = (await response.text()).replaceAll('</script', '<\\/script'); script.removeAttribute('src');
    }
    clone.querySelector('#graph-data').textContent = JSON.stringify(snapshot()).replaceAll('<', '\\u003c');
    clone.querySelector('#export-menu').hidden = true; clone.querySelector('#toast').hidden = true;
    clone.querySelector('#search-results').hidden = true; clone.querySelector('#help-dialog').removeAttribute('open');
    clone.querySelector('#run-dialog').removeAttribute('open'); clone.querySelector('#run-dialog-form').replaceChildren();
    clone.querySelector('#node-layer').replaceChildren(); clone.querySelector('#edge-layer').replaceChildren();
    download('<!doctype html>\n' + clone.outerHTML, 'text/html;charset=utf-8', 'noemorph-knowledge-map.html');
  }
  function exportSVG() {
    const clone = graph.cloneNode(true), rect = graph.getBoundingClientRect(), originals = [graph, ...graph.querySelectorAll('*')], copies = [clone, ...clone.querySelectorAll('*')];
    const properties = ['fill', 'fill-opacity', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-dasharray', 'opacity', 'font-family', 'font-size', 'font-style', 'font-weight', 'text-anchor', 'dominant-baseline', 'paint-order', 'stroke-linejoin', 'display'];
    originals.forEach((node, i) => { const computed = getComputedStyle(node); for (const prop of properties) copies[i].style.setProperty(prop, computed.getPropertyValue(prop)); copies[i].removeAttribute('tabindex'); });
    clone.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`); clone.setAttribute('width', rect.width); clone.setAttribute('height', rect.height);
    clone.insertBefore(svg('rect', { width: '100%', height: '100%', fill: css('--canvas') }), clone.firstChild);
    download(new XMLSerializer().serializeToString(clone), 'image/svg+xml;charset=utf-8', 'noemorph-current-view.svg');
  }
  $('export-button').onclick = () => { $('export-menu').hidden = !$('export-menu').hidden; $('export-button').setAttribute('aria-expanded', String(!$('export-menu').hidden)); };
  document.querySelectorAll('[data-export]').forEach(button => button.addEventListener('click', async () => {
    $('export-menu').hidden = true; $('export-button').setAttribute('aria-expanded', 'false');
    try {
      if (button.dataset.export === 'json') download(JSON.stringify(snapshot(), null, 2), 'application/json;charset=utf-8', 'noemorph.graph.json');
      else if (button.dataset.export === 'current-json') download(JSON.stringify({ ...languagePack.data.graphs.find(g => g.meta.language === model.data.meta.language), view: snapshot().view }, null, 2), 'application/json;charset=utf-8', `noemorph.${model.data.meta.language}.graph.json`);
      else if (button.dataset.export === 'svg') exportSVG(); else await exportHTML();
    } catch (error) { toast(T('当前文件模式无法打包外部资源。请运行 scripts/knowledge_map.py 生成独立 HTML，或通过本地服务打开。')); }
  }));
  let resizeFrame;
  new ResizeObserver(() => {
    cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
      const { width, height } = area.getBoundingClientRect(), previous = areaSize;
      areaSize = { width, height };
      if (!model || !width || !height || width === previous.width && height === previous.height) return;
      // Keep the same world point at the center when panels or the window resize.
      if (previous.width && previous.height) {
        camera.x += (width - previous.width) / 2; camera.y += (height - previous.height) / 2;
      }
      updateCamera();
    });
  }).observe(area);
  document.querySelectorAll('[data-ui-lang]').forEach(button => button.addEventListener('click', () => changeInterfaceLanguage(button.dataset.uiLang)));
  $('content-language').onchange = event => { contentLanguage = event.target.value; switchContent(); };
  $('run-settings-button').onclick = () => { window.NoemorphSettings.mount($('run-dialog-form'), { question: languagePack.data.graphs[0].meta.question || model.root.label, macro_rounds: model.data.meta.rounds || 3, ui_language: I.getLanguage() }); $('run-dialog').showModal(); };
  $('close-run-dialog').onclick = () => $('run-dialog').close();
  try {
    const initial = JSON.parse($('graph-data').textContent) || window.NOEMORPH_DEMO;
    try { const theme = initial?.view?.theme || localStorage.getItem('noemorph-theme'); if (['dark', 'light'].includes(theme)) document.documentElement.dataset.theme = theme; } catch (_) {}
    let uiLanguage = initial?.view?.ui_language || initial?.run_config?.ui_language;
    try { uiLanguage ||= localStorage.getItem('noemorph-ui-language'); } catch (_) {}
    I.setLanguage(uiLanguage || 'zh-CN'); I.applyStatic(document);
    setInspector(!isMobileInspector()); await mount(initial);
  } catch (error) { text('question-title', T('图谱未能打开')); toast(error.message); }
})();
