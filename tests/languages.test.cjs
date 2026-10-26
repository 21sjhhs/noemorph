const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const L = require('../plugins/knowledge-map/languages.js');
const I = require('../plugins/knowledge-map/i18n.js');
const C = require('../plugins/knowledge-map/settings.js');
const originalBundle = () => JSON.parse(fs.readFileSync(path.join(__dirname,'../examples/knowledge-map.html'),'utf8').match(/<script id="graph-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);

test('browser scripts share the public namespace and load the demo without CommonJS', () => {
  const browser = vm.createContext({ URL });
  browser.window = browser;
  for (const file of ['graph-core.js', 'languages.js', 'i18n.js', 'settings.js', 'demo.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../plugins/knowledge-map', file), 'utf8'), browser, { filename: file });
  }
  const graph = browser.NoemorphGraph.normalize(browser.NOEMORPH_DEMO.graphs[0]);
  assert.equal(graph.data.nodes.length, 21);
  assert.equal(browser.NoemorphLanguages.tag('en'), 'en');
  browser.NoemorphI18n.setLanguage('en');
  assert.equal(browser.NoemorphI18n.t('思考轮数'), 'Research rounds');
  assert.equal(browser.NoemorphSettings.validate({question: 'Q?'}).schema_version, 'noemorph-run-config/1.0');
});

test('Python-exported bundle fingerprints verify in the browser implementation', async () => {
  const pack = await L.prepare(originalBundle());
  assert.deepEqual([...pack.models.keys()],['zh-CN','en']);
  assert.equal(L.canonical(1e-6),'n3eb0c6f7a0b5ed8d');
  assert.equal(L.canonical(1),L.canonical(1.0));
});
test('interface locale and selected content locale remain independent', async () => {
  const data = originalBundle(); data.run_config = C.validate({question:'Q',ui_language:'en',presentation_languages:['zh-CN']});
  const pack = await L.prepare(data);
  assert.deepEqual(pack.data.run_config,data.run_config);
  assert.equal(L.resolve(pack,'zh-CN','en'),'zh-CN');
  assert.equal(L.resolve(pack,'auto','en'),'en');
  assert.equal(L.resolve(pack,'auto','ja'),'zh-CN');
});
test('changed structure, missing provenance, and stale translations are rejected', async () => {
  const wrongURL = originalBundle(); wrongURL.graphs[1].nodes[0].links[0].url='https://elsewhere.test';
  await assert.rejects(L.prepare(wrongURL),/structure/);
  const missing = originalBundle(); delete missing.graphs[1].meta.translation;
  await assert.rejects(L.prepare(missing),/bound/);
  const stale = originalBundle(); stale.graphs[0].nodes[0].summary+=' changed'; stale.source_fingerprint=await L.fingerprint(stale.graphs[0]);
  await assert.rejects(L.prepare(stale),/bound/);
});
test('source graph and translated graph retain the same identifiers and URLs', async () => {
  const pack=await L.prepare(originalBundle()), a=pack.models.get('zh-CN').data,b=pack.models.get('en').data;
  assert.deepEqual(a.nodes.map(n=>n.id),b.nodes.map(n=>n.id));
  assert.deepEqual(a.nodes.flatMap(n=>n.links.map(l=>l.url)),b.nodes.flatMap(n=>n.links.map(l=>l.url)));
});
test('UI localization covers templates and switches back without changing data', () => {
  const graph=originalBundle();const before=JSON.stringify(graph);
  I.setLanguage('en'); assert.equal(I.t('第 3 轮'),'Round 3'); assert.equal(I.t('思考轮数'),'Research rounds');
  assert.equal(I.t('已打开 114 个知识节点，完整数据保留在本地。'),'Opened 114 knowledge nodes. All data stays on this device.');
  I.setLanguage('zh-CN');assert.equal(I.t('Research rounds'),'思考轮数');assert.equal(JSON.stringify(graph),before);
});
test('run settings capture final language choices without constraining research', () => {
  const c=C.validate({question:'Q',ui_language:'en',presentation_languages:['zh-CN'],max_parallel_agents:2});
  assert.equal(c.ui_language,'en');assert.deepEqual(c.presentation_languages,['zh-CN','en']);assert.equal(c.research_language_policy,'unconstrained');
  for(const patch of [{logical_roles:2},{max_parallel_agents:6},{presentation_languages:[]},{schema_version:'other'}]) assert.throws(()=>C.validate({question:'Q',...patch}));
});

test('English is always included in legacy and custom configuration choices', () => {
  assert.deepEqual(C.validate({question:'Q',presentation_languages:['ja']}).presentation_languages,['ja','en']);
  assert.deepEqual(C.validate({question:'Q',presentation_languages:['en','en']}).presentation_languages,['en']);
});
test('legacy mixed content is labeled as source, never as a complete translation', async () => {
  const graph = originalBundle().graphs[0];
  graph.nodes[0].details = { note: 'This entire sentence was left untranslated in the Chinese language graph.', typed_queries:['Original Query(S,P)?'] };
  assert.deepEqual(L.languageIssues(graph), ['nodes.0.details.note']);
  const pack = await L.prepare(graph);
  assert.deepEqual([...pack.models.keys()],['und']);
  assert.deepEqual(L.missingLanguages(pack),['en']);
});
test('a bound English version with untranslated Chinese is rejected', async () => {
  const data = originalBundle(); data.graphs[1].nodes[0].summary='中文原文没有翻译';
  await assert.rejects(L.prepare(data), /display text/);
});

test('edge prose is translated while evidence codes and complete URLs stay protected', () => {
  const source = originalBundle().graphs[0], translated = JSON.parse(JSON.stringify(source));
  source.edges[0].details = {evidence:'只支持这一批次。',direct_url:'https://example.org/a/very/long/url/that/is/a/reference',status:'supported_with_limits'};
  translated.edges[0].details = {...source.edges[0].details,evidence:'Supports this batch only.'};
  assert.equal(L.lockedProjection(source),L.lockedProjection(translated));
  translated.edges[0].details.direct_url='https://elsewhere.example/ref';
  assert.notEqual(L.lockedProjection(source),L.lockedProjection(translated));
  translated.edges[0].details = {...source.edges[0].details,evidence:'inferred'};
  source.edges[0].details.evidence='supported_with_limits';
  assert.notEqual(L.lockedProjection(source),L.lockedProjection(translated));
  assert.deepEqual(L.languageIssues(source),[]);
});
