/* A host-neutral parameter card. Saves configuration; never starts research. */
(function (root, factory) {
  const api = factory(root.SocratesI18n);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.SocratesSettings = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (I) {
  'use strict';
  const defaults = { schema_version: 'noemorph-run-config/1.0', question: '', scope: '', macro_rounds: 3,
    max_parallel_agents: null, top_n: null, depth_hops: 3, presentation_languages: ['zh-CN','en'],
    ui_language: 'zh-CN', research_language_policy: 'unconstrained', logical_roles: 5, breadth_per_role: 5 };
  function languageTag(value) {
    if (typeof value !== 'string' || !/^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$/.test(value) || value.toLowerCase() === 'und') throw new Error('语言标签无效：' + value);
    return value.split('-').map((p, i) => !i ? p.toLowerCase() : p.length === 2 ? p.toUpperCase() : p.length === 4 ? p[0].toUpperCase() + p.slice(1).toLowerCase() : p.toLowerCase()).join('-');
  }
  function validate(value) {
    if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).some(key => !Object.hasOwn(defaults, key))) throw new Error('Invalid run configuration fields.');
    const c = { ...defaults, ...value };
    if (typeof c.question !== 'string' || !c.question.trim()) throw new Error('请填写研究问题。');
    c.question = c.question.trim();
    if (typeof c.scope !== 'string') throw new Error('scope must be text');
    c.scope = c.scope.trim();
    if (c.schema_version === 'socrates-run-config/1.0') c.schema_version = defaults.schema_version;
    if (!Number.isInteger(c.macro_rounds) || c.macro_rounds < 1 || c.macro_rounds > 1000) throw new Error('轮数必须是 1–1000 的整数。');
    if (c.max_parallel_agents !== null && (!Number.isInteger(c.max_parallel_agents) || c.max_parallel_agents < 1 || c.max_parallel_agents > 5)) throw new Error('并发上限必须是自动或 1–5。');
    if (c.top_n !== null && (!Number.isInteger(c.top_n) || c.top_n < 1 || c.top_n > 20)) throw new Error('深入路径数必须是自动或 1–20。');
    if (!Number.isInteger(c.depth_hops) || c.depth_hops < 3 || c.depth_hops > 20) throw new Error('深度尝试次数必须是 3–20 的整数。');
    if (!Array.isArray(c.presentation_languages) || !c.presentation_languages.length) throw new Error('请至少选择一种最终呈现语言。');
    c.presentation_languages = [...new Set(c.presentation_languages.map(languageTag))];
    if (c.schema_version !== defaults.schema_version || !['zh-CN','en'].includes(c.ui_language) || c.research_language_policy !== 'unconstrained' || c.logical_roles !== 5 || c.breadth_per_role !== 5) throw new Error('Invalid fixed workflow settings.');
    return c;
  }
  function mount(container, initial = {}, options = {}) {
    const T = I.t, c = { ...defaults, ...initial };
    function h(tag, attrs = {}, ...children) {
      const element = document.createElement(tag);
      for (const [name, value] of Object.entries(attrs)) {
        if (name.startsWith('on')) element.addEventListener(name.slice(2), value);
        else element.setAttribute(name, String(value));
      }
      for (const child of children.flat()) if (child != null) element.append(child instanceof Node ? child : document.createTextNode(T(String(child))));
      return element;
    }
    const controls = {};
    const form = h('form', { class: 'settings-form', novalidate: '' });
    function field(name, label, input, wide = false) {
      input.id = 'setting-' + name; input.name = name; controls[name] = input;
      return h('div', { class: 'setting-field' + (wide ? ' setting-wide' : '') }, h('label', { for: input.id }, label), input);
    }
    const question = h('textarea', { rows: 3, placeholder: T('写下本次研究问题…'), required: '' }); question.value = c.question;
    const scope = h('textarea', { rows: 2, placeholder: T('可选：允许扩展的范围、必须排除的主题或限制条件') }); scope.value = c.scope;
    const rounds = h('input', { type: 'number', min: 1, max: 1000, step: 1, value: c.macro_rounds });
    const parallel = h('select', {}, h('option', { value: '' }, '自动适配软件能力'), ...[1,2,3,4,5].map(n => h('option', { value: n }, String(n)))); parallel.value = c.max_parallel_agents ?? '';
    const top = h('input', { type: 'number', min: 1, max: 20, step: 1, placeholder: T('自动筛选'), value: c.top_n ?? '' });
    const hops = h('input', { type: 'number', min: 3, max: 20, step: 1, value: c.depth_hops });
    form.append(field('question', '研究问题', question, true), field('scope', '研究范围与排除项', scope, true), h('div', { class: 'settings-grid' },
      field('macro_rounds','思考轮数',rounds), field('max_parallel_agents','并行子代理上限',parallel),
      field('top_n','每轮深入路径数',top), field('depth_hops','每条路径最少推进次数',hops)));
    form.append(h('p', { class: 'setting-note' }, '五个逻辑角色保持不变。这里设置并发上限，实际并发还受本地软件能力限制。'));
    const languages = h('fieldset', { class: 'setting-languages' }, h('legend', {}, '最终内容呈现语言'));
    const checks = {};
    for (const [code, name] of [['zh-CN','简体中文'], ['en','英语']]) {
      const check = h('input', { type: 'checkbox', value: code, name: 'presentation_language' }); check.checked = c.presentation_languages.includes(code); checks[code] = check;
      languages.append(h('label', { class: 'language-choice' }, check, h('span', {}, name), h('code', { 'data-i18n-skip': '' }, code)));
    }
    const other = h('input', { type: 'text', placeholder: T('例如 ja、de、fr，多个用逗号分隔') }); other.value = c.presentation_languages.filter(code => !checks[code]).join(', ');
    languages.append(field('other_languages','其他语言标签（可选）',other,true));
    form.append(languages, h('p', { class: 'setting-note language-policy' }, '内容语言仅用于研究完成后的独立翻译子 Agent；不规定研究与思考使用的语言。'));
    const error = h('p', { class: 'setting-error', role: 'alert', hidden: '' }), status = h('p', { class: 'setting-saved', role: 'status', hidden: '' });
    const preview = h('pre', { class: 'config-preview', 'data-i18n-skip': '' });
    const details = h('details', { class: 'settings-preview' }, h('summary', {}, '参数预览'), preview);
    function read() {
      return validate({ ...defaults, question: question.value, scope: scope.value, macro_rounds: Number(rounds.value), max_parallel_agents: parallel.value ? Number(parallel.value) : null,
        top_n: top.value ? Number(top.value) : null, depth_hops: Number(hops.value), ui_language: I.getLanguage(),
        presentation_languages: [...Object.entries(checks).filter(([,el]) => el.checked).map(([code]) => code), ...other.value.split(/[,，\s]+/).filter(Boolean)] });
    }
    function updatePreview() { try { preview.textContent = JSON.stringify(read(), null, 2); } catch (_) { preview.textContent = ''; } }
    form.addEventListener('input', updatePreview); form.addEventListener('change', updatePreview);
    function fail(err) { error.textContent = T(err.message); error.hidden = false; status.hidden = true; }
    function saveFile(value) {
      const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2) + '\n'], { type: 'application/json' }));
      const link = h('a', { href: url, download: 'run-config.json' }); document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 30000);
    }
    form.addEventListener('submit', async event => {
      event.preventDefault(); error.hidden = true;
      try {
        const value = read();
        if (options.onSubmit) await options.onSubmit(value); else saveFile(value);
        status.textContent = T('参数已保存，返回 Agent 即可继续。'); status.hidden = false;
      } catch (err) { fail(err); }
    });
    const actions = h('div', { class: 'settings-actions' }, h('button', { type: 'submit', class: 'button setting-primary' }, options.onSubmit ? '保存并返回 Agent' : '下载配置 JSON'),
      h('button', { type: 'button', class: 'button', onclick: async () => {
        try { const value = read(); await navigator.clipboard.writeText(JSON.stringify(value, null, 2)); error.hidden = true; status.textContent = T('配置已复制。'); status.hidden = false; }
        catch (err) { if (err.message && /[\u3400-\u9fff]/.test(err.message)) fail(err); else { status.textContent = T('复制未成功，可下载 JSON。'); status.hidden = false; } }
      } }, '复制配置'));
    form.append(error, status, actions, details, h('p', { class: 'setting-note' }, '这张卡片只保存参数，不会自行开始研究。'));
    container.replaceChildren(form); updatePreview();
    return { read, form, refresh: updatePreview };
  }
  return { defaults, validate, languageTag, mount };
});
