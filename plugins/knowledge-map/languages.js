/* Portable multilingual graph contract. UI locale never changes research data. */
(function (root, factory) {
  const api = factory(typeof module === 'object' && module.exports ? require('./graph-core.js') : root.NoemorphGraph);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.NoemorphLanguages = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (G) {
  'use strict';
  const protectedKeys = new Set(['id','ids','origin_ids','anchor_ids','typed_queries','formal_logic','source','target','parent_id','url','href','path','evidence','role','type']);
  const metadata = new Set(['language','language_label','translation']);
  const metaText = new Set(['title','question','description','provenance']);
  const nodeText = new Set(['label','summary','next_question','evidence_note']);
  function tag(value) {
    if (typeof value !== 'string' || !/^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$/.test(value)) throw new Error('Invalid language tag: use zh-CN, en, ja, or und.');
    const parts = value.split('-');
    return parts.map((p, i) => !i ? p.toLowerCase() : p.length === 2 ? p.toUpperCase() : p.length === 4 ? p[0].toUpperCase() + p.slice(1).toLowerCase() : p.toLowerCase()).join('-');
  }
  function stripped(graph) {
    const result = JSON.parse(JSON.stringify(graph)); delete result.view;
    for (const key of metadata) delete result.meta[key];
    return result;
  }
  function canonical(value) {
    if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
    if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
    if (typeof value === 'number') {
      if (!Number.isFinite(value)) throw new Error('Graph numbers must be finite.');
      const bytes = new DataView(new ArrayBuffer(8)); bytes.setFloat64(0, value);
      return 'n' + Array.from({ length: 8 }, (_, i) => bytes.getUint8(i).toString(16).padStart(2, '0')).join('');
    }
    return JSON.stringify(value);
  }
  async function fingerprint(graph) {
    const bytes = new TextEncoder().encode(canonical(stripped(graph)));
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('');
  }
  function displayText(p) {
    if (p[0] === 'meta') return p.length === 2 && metaText.has(p[1]) || p.length === 3 && p[1] === 'warnings';
    if (p[0] === 'nodes') {
      if (p.length === 3 && nodeText.has(p[2]) || p.length === 4 && p[2] === 'tags') return true;
      if (p.length === 5 && p[2] === 'links' && ['label','note'].includes(p[4])) return true;
      if (p[2] === 'details') return !p.slice(3).some(k => protectedKeys.has(k));
    }
    return p.length === 3 && p[0] === 'edges' && p[2] === 'label';
  }
  function lockedProjection(graph) {
    function walk(value, path) {
      if (typeof value === 'string' && value.trim() && displayText(path)) return { $display_text: true };
      if (Array.isArray(value)) return value.map((v, i) => walk(v, [...path, String(i)]));
      if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, walk(v, [...path, k])]));
      return value;
    }
    return canonical(walk(stripped(graph), []));
  }
  async function prepare(input) {
    const data = JSON.parse(JSON.stringify(input));
    const bundled = data.bundle_version === '1.0';
    const graphs = bundled ? data.graphs : [data];
    if (!Array.isArray(graphs) || !graphs.length) throw new Error('The language bundle has no graphs.');
    const models = new Map();
    for (const graph of graphs) {
      G.normalize(graph);
      graph.meta.language = tag(graph.meta.language || 'und');
      if (models.has(graph.meta.language)) throw new Error('Duplicate graph language: ' + graph.meta.language);
      models.set(graph.meta.language, G.normalize(graph));
    }
    const hash = await fingerprint(graphs[0]), projection = lockedProjection(graphs[0]);
    if (bundled && data.source_fingerprint !== hash) throw new Error('The language bundle does not match its source fingerprint.');
    for (const translated of graphs.slice(1)) {
      const info = translated.meta.translation;
      if (translated.meta.language === 'und' || lockedProjection(translated) !== projection) throw new Error('Translation changed graph structure, IDs, URLs, or evidence.');
      if (!info || info.source_fingerprint !== hash || info.target_language !== translated.meta.language || typeof info.translator !== 'string' || !info.translator.trim()) throw new Error('Translation is not bound to this source graph.');
    }
    const defaultLanguage = tag(bundled ? data.default_language : graphs[0].meta.language);
    if (!models.has(defaultLanguage)) throw new Error('The default graph language is unavailable.');
    return { models, sourceFingerprint: hash, data: { bundle_version: '1.0', source_fingerprint: hash, default_language: defaultLanguage, graphs, ...(data.view ? { view: data.view } : {}), ...(data.run_config ? { run_config: data.run_config } : {}) } };
  }
  function resolve(pack, requested, uiLanguage) {
    if (requested !== 'auto' && pack.models.has(requested)) return requested;
    if (requested === 'auto') {
      if (pack.models.has(uiLanguage)) return uiLanguage;
      const primary = uiLanguage.split('-')[0], match = [...pack.models.keys()].find(k => k.split('-')[0] === primary);
      if (match) return match;
    }
    return pack.data.default_language;
  }
  return { tag, canonical, stripped, fingerprint, lockedProjection, prepare, resolve };
});
