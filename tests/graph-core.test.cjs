const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const G = require('../plugins/knowledge-map/graph-core.js');
const data = () => JSON.parse(fs.readFileSync(path.join(__dirname, '../examples/demo.graph.json'), 'utf8'));
const state = extra => ({ mode: 'overview', expanded: new Set(), revealed: new Set(), roles: new Set(Object.keys(G.ROLES)), round: 0, status: 'all', ...extra });

test('overview preserves the complete model while revealing only major findings', () => {
  const model = G.normalize(data());
  assert.equal(G.visibleGraph(model, state()).nodes.length, 5);
  assert.equal(model.data.nodes.length, 21);
  assert.equal(G.visibleGraph(model, state({ mode: 'all' })).nodes.length, 21);
});
test('expansion reveals one level; targeted reveal avoids opening sibling branches', () => {
  const model = G.normalize(data());
  const shown = G.visibleGraph(model, state({ expanded: new Set(['process']) }));
  assert.equal(shown.nodes.length, 8);
  assert.ok(!shown.ids.has('process:1:next'));
  const revealed = G.visibleGraph(model, state({ revealed: new Set(['process:1:next']) }));
  assert.ok(revealed.ids.has('process:1:next'));
  assert.ok(!revealed.ids.has('process:2'));
});
test('search covers hidden nodes and preserves original IDs', () => {
  const model = G.normalize(data());
  assert.ok(G.search(model, 'process:1:next').some(n => n.id === 'process:1:next'));
  assert.equal(G.search(model, 'no-such-question').length, 0);
});
test('filters operate on the full network and frontier keeps context', () => {
  const model = G.normalize(data());
  const result = G.visibleGraph(model, state({ mode: 'all', roles: new Set(['predicate']), round: 2 }));
  assert.ok(result.nodes.every(n => n.id === model.root.id || n.role === 'predicate' && n.round === 2));
  const frontier = G.visibleGraph(model, state({ mode: 'frontier' }));
  assert.ok(frontier.ids.has('process:1:next'));
  assert.ok(frontier.ids.has('process:1'));
});
test('malformed imports and executable link protocols are rejected', () => {
  for (const url of ['javascript:alert(1)', 'data:text/html,test', '//evil.test', '\\evil', 'https://a/\nx']) assert.equal(G.safeURL(url), null);
  assert.equal(G.safeURL('../notes/paper.md'), '../notes/paper.md');
  const bad = data(); bad.nodes[0].parent_id = 'process'; assert.throws(() => G.normalize(bad), /循环/);
  const dangling = data(); dangling.edges[0].target = 'missing'; assert.throws(() => G.normalize(dangling), /端点/);
  for (const patch of [{role:'__proto__'}, {evidence:'constructor'}, {origin_ids:'invalid'}, {tags:{bad:true}}, {parent_id:42}]) {
    const malformed = data(); Object.assign(malformed.nodes[1], patch); assert.throws(() => G.normalize(malformed));
  }
});
test('layout is deterministic, finite and restores manually adjusted positions', () => {
  const model = G.normalize(data()), first = G.layout(model), second = G.layout(model);
  assert.deepEqual(first, second);
  for (const p of first.values()) { assert.ok(Number.isFinite(p.x)); assert.ok(Number.isFinite(p.y)); }
  const changed = G.layout(model, { process: { x: 123, y: 456 } }); assert.deepEqual(changed.get('process'), { x: 123, y: 456 });
  const bounds = G.bounds(model.data.nodes, first); assert.ok(bounds.width > 0 && bounds.height > 0);
});
test('label truncation does not break non-BMP characters', () => {
  assert.ok(G.wrapLabel('甲乙丙丁戊己庚辛壬癸'.repeat(10), 12, 2).join('').endsWith('…'));
  assert.ok(G.wrapLabel('A😀B😀C', 7, 2).every(s => !/[\uD800-\uDBFF]$/.test(s)));
  assert.ok(!/[\uD800-\uDBFF](?![\uDC00-\uDFFF])/.test(G.wrapLabel('😀'.repeat(20), 4, 2).join('')));
});
