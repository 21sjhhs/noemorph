/* Noemorph graph data + deterministic layout. No DOM, network, or dependencies. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SocratesGraph = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const ROLES = {
    anchor: { label: '问题与概念', short: '概念锚点', color: 'var(--teal)', angle: -Math.PI / 2 },
    predicate: { label: '谓词拓展', short: '拓展过程', color: 'var(--teal)', angle: -2.4 },
    subject: { label: '主词替换', short: '替换对象', color: 'var(--blue)', angle: -.75 },
    predicate_abstraction: { label: '谓词抽象', short: '抽象过程', color: 'var(--violet)', angle: .75 },
    subject_abstraction: { label: '主词抽象', short: '抽象对象', color: 'var(--gold)', angle: 2.4 }
  };
  const STATUSES = { discovered: '已发现', explored: '已做深度探索', frontier: '尚未深入', blocked: '未解决 / 受阻', contradicted: '存在反证' };
  const EVIDENCE = { verified_direct: '直接证据', supported_with_limits: '有限支持', inferred: '推断', unresolved: '尚未证实', contradicted: '证据冲突' };
  function safeURL(url) {
    if (typeof url !== 'string' || !url.trim() || /[\x00-\x20\x7f\\]/.test(url) || url.startsWith('//')) return null;
    const scheme = url.match(/^([a-z][a-z\d+.-]*):/i);
    if (scheme && !['http:', 'https:', 'file:'].includes(scheme[0].toLowerCase())) return null;
    try { const u = new URL(url, 'https://local.invalid/'); if (['http:', 'https:'].includes(u.protocol) && !u.hostname) return null; } catch (_) { return null; }
    return url;
  }
  function normalize(input) {
    if (!input || input.schema_version !== '1.0') throw new Error('需要 schema_version 为 1.0 的图谱 JSON。运行状态请先使用 knowledge_map.py 导出。');
    if (!input.meta || typeof input.meta !== 'object' || Array.isArray(input.meta) || !Array.isArray(input.nodes) || !input.nodes.length || !Array.isArray(input.edges)) throw new Error('图谱缺少 meta、nodes 或 edges。');
    if (input.meta.warnings != null && (!Array.isArray(input.meta.warnings) || input.meta.warnings.some(w => typeof w !== 'string'))) throw new Error('meta.warnings 必须是文字数组。');
    if (input.nodes.length > 5000 || input.edges.length > 20000) throw new Error('此阅读器支持最多 5,000 个节点和 20,000 条连线；请按研究批次导出。');
    const graph = JSON.parse(JSON.stringify(input));
    const byId = new Map();
    graph.nodes = graph.nodes.map(n => {
      if (!n || typeof n.id !== 'string' || !n.id.trim() || byId.has(n.id) || typeof n.label !== 'string' || !n.label.trim()) throw new Error('节点 ID / label 为空或 ID 重复。');
      const o = { summary: '', role: 'anchor', status: 'discovered', evidence: 'unresolved', importance: 2, depth: 0, round: 0, type: 'concept', parent_id: null, links: [], origin_ids: [], ...n };
      if (!Object.hasOwn(ROLES, o.role) || !Object.hasOwn(STATUSES, o.status) || !Object.hasOwn(EVIDENCE, o.evidence)) throw new Error(`节点 ${n.id} 的角色、状态或证据等级无效。`);
      if (!Array.isArray(o.origin_ids) || o.origin_ids.some(id => typeof id !== 'string') || (o.tags != null && (!Array.isArray(o.tags) || o.tags.some(t => typeof t !== 'string')))) throw new Error(`节点 ${n.id} 的 origin_ids / tags 必须是文字数组。`);
      if (o.parent_id != null && (typeof o.parent_id !== 'string' || !o.parent_id.trim())) throw new Error(`节点 ${n.id} 的 parent_id 必须为非空 ID 或 null。`);
      if (typeof o.importance !== 'number' || !Number.isFinite(o.importance) || o.importance < 1 || o.importance > 5) throw new Error(`节点 ${n.id} 的 importance 必须在 1–5 之间。`);
      if (!Array.isArray(o.links) || o.links.some(l => !l || typeof l !== 'object' || (l.url != null && !safeURL(l.url)))) throw new Error(`节点 ${n.id} 存在无效链接。`);
      byId.set(o.id, o);
      return o;
    });
    const children = new Map(graph.nodes.map(n => [n.id, []]));
    for (const n of graph.nodes) {
      const visited = new Set([n.id]);
      let p = n.parent_id;
      while (p) {
        if (!byId.has(p)) throw new Error(`父节点 ${p} 不存在。`);
        if (visited.has(p)) throw new Error('parent_id 存在循环。');
        visited.add(p); p = byId.get(p).parent_id;
      }
      if (n.parent_id) children.get(n.parent_id).push(n.id);
    }
    const eids = new Set();
    graph.edges = graph.edges.map(e => {
      if (!e || typeof e.id !== 'string' || !e.id.trim() || eids.has(e.id) || !byId.has(e.source) || !byId.has(e.target)) throw new Error('存在重复连线 ID 或缺失的连线端点。');
      eids.add(e.id); return { label: '探索路径', kind: 'path', ...e };
    });
    const root = graph.nodes.find(n => n.type === 'question') || graph.nodes.find(n => !n.parent_id) || graph.nodes[0];
    return { data: graph, byId, children, root };
  }
  function ancestors(model, id) {
    const out = [];
    let n = model.byId.get(id);
    while (n && n.parent_id) { out.push(n.parent_id); n = model.byId.get(n.parent_id); }
    return out;
  }
  function descendants(model, id) {
    const out = [], stack = [...(model.children.get(id) || [])];
    while (stack.length) { const next = stack.pop(); out.push(next); stack.push(...(model.children.get(next) || [])); }
    return out;
  }
  function isFrontier(n) { return n.status === 'frontier' || n.status === 'blocked'; }
  function visibleGraph(model, state) {
    const ids = new Set([model.root.id]);
    for (const n of model.data.nodes) {
      if (state.mode === 'all' || (state.mode === 'frontier' ? isFrontier(n) : n.importance >= 4 || n.type === 'question')) {
        ids.add(n.id); for (const p of ancestors(model, n.id)) ids.add(p);
      }
    }
    for (const id of state.revealed || []) if (model.byId.has(id)) { ids.add(id); for (const p of ancestors(model, id)) ids.add(p); }
    // Expansion reveals one level at a time; the entire data stays in the model.
    for (const id of state.expanded || []) if (ids.has(id)) for (const child of model.children.get(id) || []) ids.add(child);
    const nodes = model.data.nodes.filter(n => ids.has(n.id) && (n.id === model.root.id ||
      ((!state.roles || state.roles.has(n.role)) && (!state.round || Number(n.round) === state.round || !n.round) &&
       (!state.status || state.status === 'all' || n.status === state.status))));
    const shown = new Set(nodes.map(n => n.id));
    return { nodes, edges: model.data.edges.filter(e => shown.has(e.source) && shown.has(e.target)), ids: shown };
  }
  function search(model, query) {
    const q = query.trim().toLocaleLowerCase();
    if (!q) return [];
    return model.data.nodes.filter(n => [n.label, n.summary, n.id, ...(n.origin_ids || []), ...(n.tags || [])].join(' ').toLocaleLowerCase().includes(q))
      .sort((a, b) => Number(b.label.toLocaleLowerCase().includes(q)) - Number(a.label.toLocaleLowerCase().includes(q)) || b.importance - a.importance).slice(0, 40);
  }
  function layout(model, saved = {}) {
    const positions = new Map(), angles = new Map();
    positions.set(model.root.id, { x: 0, y: 0 }); angles.set(model.root.id, 0);
    const grouped = {};
    for (const n of model.data.nodes) if (n.id !== model.root.id && n.type !== 'finding' && (n.type === 'direction' || !n.parent_id || n.parent_id === model.root.id)) {
      (grouped[n.role] ||= []).push(n);
    }
    for (const [role, group] of Object.entries(grouped)) {
      group.sort((a, b) => b.importance - a.importance || String(a.id).localeCompare(String(b.id)));
      group.forEach((n, i) => {
        const base = ROLES[role].angle;
        const ring = Math.floor(i / 4), slot = i % 4;
        const count = Math.min(4, group.length - ring * 4);
        const angle = base + (slot - (count - 1) / 2) * (role === 'anchor' ? .48 : .31);
        const radius = role === 'anchor' ? 250 + ring * 220 : 410 + ring * 260;
        positions.set(n.id, { x: Math.cos(angle) * radius * 1.15, y: Math.sin(angle) * radius * .85 });
        angles.set(n.id, angle);
      });
    }
    const pending = model.data.nodes.filter(n => !positions.has(n.id));
    for (let pass = 0; pass < model.data.nodes.length && pending.length; pass++) {
      let changed = false;
      for (let i = pending.length - 1; i >= 0; i--) {
        const n = pending[i], parent = positions.get(n.parent_id);
        if (!parent) continue;
        const siblings = model.children.get(n.parent_id) || [];
        const index = siblings.indexOf(n.id), angle = (angles.get(n.parent_id) ?? ROLES[n.role].angle) + (index - (siblings.length - 1) / 2) * .36;
        positions.set(n.id, { x: parent.x + Math.cos(angle) * 235, y: parent.y + Math.sin(angle) * 200 });
        angles.set(n.id, angle); pending.splice(i, 1); changed = true;
      }
      if (!changed) break;
    }
    for (const n of pending) { const i = model.data.nodes.indexOf(n); positions.set(n.id, { x: Math.cos(i * 2.4) * 600, y: Math.sin(i * 2.4) * 600 }); }
    // Resolve label collisions deterministically. Importance never changes evidence.
    const free = model.data.nodes.filter(n => n.id !== model.root.id);
    for (let step = 0; step < 45; step++) {
      const cells = new Map();
      for (let i = 0; i < free.length; i++) {
        const a = positions.get(free[i].id), gx = Math.floor(a.x / 200), gy = Math.floor(a.y / 160);
        const nearby = [];
        for (let x = gx - 1; x <= gx + 1; x++) for (let y = gy - 1; y <= gy + 1; y++) nearby.push(...(cells.get(`${x},${y}`) || []));
        for (const j of nearby) {
        const b = positions.get(free[j].id);
        let dx = a.x - b.x, dy = a.y - b.y;
        if (Math.abs(dx) >= 190 || Math.abs(dy) >= 140) continue;
        if (dx === 0 && dy === 0) { dx = 1; dy = .3; }
        const d = Math.hypot(dx / 1.35, dy), min = 145;
        if (d < min) { const push = (min - d) / min * 5; a.x += dx / (d || 1) * push; a.y += dy / (d || 1) * push; b.x -= dx / (d || 1) * push; b.y -= dy / (d || 1) * push; }
        }
        const key = `${gx},${gy}`; if (!cells.has(key)) cells.set(key, []); cells.get(key).push(i);
      }
    }
    for (const [id, p] of Object.entries(saved || {})) if (positions.has(id) && p && Number.isFinite(p.x) && Number.isFinite(p.y) && Math.abs(p.x) < 1e7 && Math.abs(p.y) < 1e7) positions.set(id, { x: p.x, y: p.y });
    return positions;
  }
  function bounds(nodes, positions) {
    if (!nodes.length) return { x: -100, y: -100, width: 200, height: 200 };
    const ps = nodes.map(n => positions.get(n.id)).filter(Boolean);
    const x = Math.min(...ps.map(p => p.x)) - 110, y = Math.min(...ps.map(p => p.y)) - 70;
    return { x, y, width: Math.max(220, Math.max(...ps.map(p => p.x)) + 110 - x), height: Math.max(200, Math.max(...ps.map(p => p.y)) + 120 - y) };
  }
  function wrapLabel(text, max = 22, lines = 3) {
    const chars = Array.from(String(text)), result = []; let line = '', units = 0;
    const measure = s => Array.from(s).reduce((sum, c) => sum + (c.charCodeAt(0) > 255 ? 2 : 1), 0);
    for (let i = 0; i < chars.length; i++) {
      const c = chars[i], size = c.charCodeAt(0) > 255 ? 2 : 1;
      if (units + size > max && line) {
        const split = line.lastIndexOf(' ');
        if (split > max * .35) { result.push(line.slice(0, split).trim()); line = line.slice(split + 1); units = measure(line); }
        else { result.push(line.trim()); line = ''; units = 0; }
      }
      if (result.length === lines) { result[lines - 1] = Array.from(result[lines - 1]).slice(0, -1).join('') + '…'; return result; }
      line += c; units += size;
    }
    if (line) result.push(line.trim()); return result;
  }
  return { ROLES, STATUSES, EVIDENCE, normalize, safeURL, ancestors, descendants, isFrontier, visibleGraph, search, layout, bounds, wrapLabel };
});
