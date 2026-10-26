/* Interface strings only. Graph translations live in separate declared variants. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.NoemorphI18n = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const pairs = [
    ['研究范围与排除项','Scope and exclusions'],['可选：允许扩展的范围、必须排除的主题或限制条件','Optional: allowed expansion, excluded topics, or constraints'],
    ['Noemorph 首页','Noemorph home'],['中文界面','Chinese interface'],['工作空间','Workspace'],['知识图谱','Knowledge map'],['知识探索地图','Knowledge atlas'],
    ['每一个发现，','Every discovery,'],['都是新的起点。','a new beginning.'],
    ['知识节点','Knowledge nodes'],['探索连接','Connections'],['待深入方向','Open directions'],
    ['浏览图谱','Browse the map'],['主要发现','Key discoveries'],['完整网络','Full network'],['待探索分支','Open branches'],
    ['逻辑探索路径','Logical exploration paths'],['重置','Reset'],['研究轮次','Research rounds'],['探索状态','Exploration status'],
    ['所有状态','All statuses'],['已做深度探索','Explored in depth'],['尚未深入','Not yet explored in depth'],['未解决 / 受阻','Unresolved / blocked'],['存在反证','Contradicted'],
    ['问题与概念','Question & concepts'],['谓词拓展','Predicate expansion'],['主词替换','Subject substitution'],['谓词抽象','Predicate abstraction'],['主词抽象','Subject abstraction'],
    ['已发现','Discovered'],['直接证据','Direct evidence'],['有限支持','Supported with limits'],['推断','Inferred'],['尚未证实','Unverified'],['证据冲突','Conflicting evidence'],
    ['全部','All'],['导出','Export'],['导入研究图谱','Import graph'],['跟随证据，让问题继续生长。','Follow the evidence. Let the question grow.'],
    ['交互演示 · 示例不构成研究证据','Interactive demo · Examples are not research evidence'],
    ['寻找概念、线索或问题…','Find a concept, lead, or question…'],['搜索所有节点','Search all nodes'],
    ['缩小看见联系，靠近看见细节。','Zoom out for connections. Zoom in for detail.'],
    ['这里还没有匹配的线索','No matching leads here yet'],['调整路径、轮次或探索状态，再看看。','Try different paths, rounds, or statuses.'],['重置筛选','Reset filters'],
    ['探索路径','Exploration path'],['类比 / 待验证联系','Analogy / unverified link'],['界面语言','Interface language'],['图谱内容语言','Graph content language'],
    ['跟随界面','Follow interface'],['原始记录（混合 / 未标注）','Source (mixed / untagged)'],['运行参数','Run settings'],
    ['切换明暗主题','Toggle light / dark theme'],['打开操作指南','Open interaction guide'],['操作指南','Interaction guide'],
    ['切换连线标签','Toggle connection labels'],['适应窗口','Fit to window'],['适应窗口 · F','Fit to window · F'],
    ['缩小','Zoom out'],['放大','Zoom in'],['重置缩放','Reset zoom'],['重置为 100%','Reset to 100%'],['全屏图谱','Fullscreen map'],
    ['打开导航','Open navigation'],['收起节点详情','Close node details'],['打开节点详情','Open node details'],
    ['收起缩略导航','Collapse minimap'],['展开缩略导航','Expand minimap'],['缩略导航图，点击定位；按 Enter 适应全部节点','Minimap: click to navigate; Enter to fit all nodes'],
    ['可拖动缩放的交互知识图谱','Interactive knowledge map with pan and zoom'],
    ['知识图谱。拖动空白移动，滚轮缩放；Tab 选择节点，Enter 打开详情。','Knowledge map. Drag the background to pan, scroll to zoom; Tab to choose a node, Enter for details.'],
    ['图谱导航','Map navigation'],['显示范围','View scope'],['节点详情','Node details'],['线索详情','Lead details'],
    ['独立交互 HTML','Standalone interactive HTML'],['可离线打开','Works offline'],['完整图谱 JSON','Complete graph JSON'],['包含全部节点与视图','Includes all nodes and the view'],
    ['当前视图 SVG','Current view as SVG'],['可编辑矢量图','Editable vector image'],['当前语言 JSON','Current language JSON'],['全部语言 JSON','All languages JSON'],
    ['研究记录仅在当前设备中处理','Research records are processed on this device'],['拖动移动 · 滚轮缩放 · 双击节点展开','Drag to pan · Scroll to zoom · Double-click to expand'],
    ['松开以导入图谱 JSON','Drop to import graph JSON'],['探索，从一个问题开始。','Exploration starts with a question.'],['关闭指南','Close guide'],
    ['地图只呈现已有记录。大小与主次表示阅读优先级；证据等级单独标注。未入选纵深研究的发现依然保留。','The map presents existing records. Size indicates reading priority; evidence strength is shown separately. Findings not selected for deeper study are retained.'],
    ['拖动空白','Drag background'],['移动地图','Pan the map'],['滚轮 / 双指','Scroll / pinch'],['以指针为中心缩放；触屏支持双指缩放','Zoom around the pointer; pinch to zoom on touchscreens'],
    ['拖动节点','Drag a node'],['调整位置；导出会保留布局','Adjust its position; exports keep the layout'],['单击 / Enter','Click / Enter'],['查看发现、证据与下一问','Read findings, evidence, and the next question'],
    ['双击 / +n','Double-click / +n'],['展开或收起下一级线索','Expand or collapse the next level'],['搜索完整图谱，包括隐藏节点','Search the whole graph, including hidden nodes'],
    ['适应当前窗口','Fit the current window'],['退出搜索或关闭详情','Exit search or close details'],
    ['“探索路径”是研究记录的先后关系，不自动表示因果。类比、迁移及冲突关系必须以节点记录和原始证据为准。','Exploration paths show the order of research records, not automatic causation. Check node records and original evidence for analogies, transfer, and conflicts.'],
    ['交互演示 · 所有示例发现仅用于展示界面','Interactive demo · All example findings illustrate the interface only'],
    ['本地图谱 · 阅读优先级与证据等级分别呈现','Local graph · Reading priority and evidence strength are separate'],
    ['已载入研究记录 · {count} 条导入说明，详见主问题节点','Research loaded · {count} import notes in the original-question node'],
    ['{rounds} 轮探索 · {nodes} 个节点','{rounds} rounds · {nodes} nodes'],['原始问题','Original question'],['研究起点','Research starting point'],
    ['第 {round} 轮','Round {round}'],['连接 · {count}','Connections · {count}'],['当前没有记录关联。','No connections are recorded yet.'],
    ['记录中的探索路径','Recorded exploration path'],['此节点保留为研究线索；尚未记录详细结论。','This node is retained as a lead; detailed findings are not recorded yet.'],
    ['阅读优先级 {importance} / 5','Reading priority {importance} / 5'],['图谱中的阅读优先级','Reading priority in the map'],['表示展示主次，不代表证据更强。','Display priority does not imply stronger evidence.'],
    ['回溯研究路径','Trace the research path'],['当前线索','Current lead'],['参考资料与原始文件','References & original files'],['参考资料','Reference'],
    ['本地研究文件','Local research file'],['打开文件','Open file'],['打开来源','Open source'],['打开{label}','Open {label}'],
    ['来源标识尚未解析为链接','Source identifier has not been resolved to a link'],['尚无可跳转的资料。此处不会自动生成引用或补造来源。','No source links are available yet. References are never invented here.'],
    ['THE NEXT QUESTION','THE NEXT QUESTION'],['下一问','The next question'],['THE ORIGINAL QUESTION','THE ORIGINAL QUESTION'],
    ['{count} 条已记录的下级线索尚未展开。它们会把这个问题带向哪里？','{count} recorded child leads are still collapsed. Where might they take this question?'],
    ['展开 {count} 条线索 →','Explore {count} leads →'],['展开 {count} 个下级线索','Expand {count} child leads'],['收起下级线索','Collapse child leads'],
    ['定位此节点 ⌖','Locate node ⌖'],['无下级线索','No child leads'],['展开下级 +','Expand children +'],['收起下级 −','Collapse children −'],['下级已展示','Children are visible'],
    ['查看原始逻辑与边界记录','View logic and boundary records'],['导入说明 · {count}','Import notes · {count}'],
    ['这是当前记录的末端线索。下一问可在节点详情中查看。','This is the end of the current recorded path. See node details for the next question.'],
    ['当前浏览器不支持全屏，可使用窗口最大化。','Fullscreen is unavailable in this browser. You can maximize the window.'],['当前浏览器未允许全屏。','The browser did not allow fullscreen.'],
    [' · 当前已折叠',' · Currently collapsed'],['没有找到匹配的线索。试试原始方向 ID。','No matching leads. Try an original direction ID.'],
    ['文件超过 25 MB，请按研究批次导出。','The file exceeds 25 MB. Export smaller research batches.'],
    ['已打开 {count} 个知识节点，完整数据保留在本地。','Opened {count} knowledge nodes. All data stays on this device.'],['导入失败：{error}','Import failed: {error}'],
    ['当前文件模式无法打包外部资源。请运行 scripts/knowledge_map.py 生成独立 HTML，或通过本地服务打开。','External assets cannot be bundled in this file mode. Use scripts/knowledge_map.py to create standalone HTML, or open the viewer through a local server.'],
    ['图谱未能打开','The graph could not be opened'],['此语言版本尚未生成，内容继续使用 {language}。','This language version has not been generated. Content remains in {language}.'],
    ['已加入 {language} 图谱版本。','Added the {language} graph version.'],['语言版本与当前研究不匹配。请先打开对应原图。','This language version belongs to a different study. Open its source graph first.'],
    ['新研究配置','Configure a study'],['开始前，选择你的探索方式。','Choose how to explore before you begin.'],['研究问题','Research question'],['写下本次研究问题…','Enter the research question…'],
    ['思考轮数','Research rounds'],['并行子代理上限','Maximum parallel subagents'],['自动适配软件能力','Adapt to host capabilities'],['每轮深入路径数','Deep paths per round'],['自动筛选','Automatic selection'],
    ['每条路径最少推进次数','Minimum depth attempts per path'],['最终内容呈现语言','Final content languages'],['简体中文','Simplified Chinese'],['英语','English'],['其他语言标签（可选）','Other language tags (optional)'],
    ['例如 ja、de、fr，多个用逗号分隔','For example ja, de, fr; separate tags with commas'],
    ['五个逻辑角色保持不变。这里设置并发上限，实际并发还受本地软件能力限制。','The five logical roles stay fixed. This sets a concurrency ceiling; actual concurrency also depends on the local host.'],
    ['内容语言仅用于研究完成后的独立翻译子 Agent；不规定研究与思考使用的语言。','Content languages apply only to an independent translation subagent after research. They do not constrain the language used to think or investigate.'],
    ['这张卡片只保存参数，不会自行开始研究。','This card saves settings; it does not start research by itself.'],['保存并返回 Agent','Save and return to Agent'],['下载配置 JSON','Download configuration JSON'],['复制配置','Copy configuration'],
    ['参数已保存，返回 Agent 即可继续。','Settings saved. Return to the Agent to continue.'],['配置已复制。','Configuration copied.'],['复制未成功，可下载 JSON。','Copy was unavailable. Download the JSON instead.'],
    ['请填写研究问题。','Enter a research question.'],['轮数必须是 1–1000 的整数。','Rounds must be an integer from 1 to 1000.'],['并发上限必须是自动或 1–5。','Parallelism must be automatic or an integer from 1 to 5.'],
    ['深入路径数必须是自动或 1–20。','Deep paths must be automatic or an integer from 1 to 20.'],['深度尝试次数必须是 3–20 的整数。','Minimum depth attempts must be an integer from 3 to 20.'],['请至少选择一种最终呈现语言。','Choose at least one final content language.'],
    ['语言标签无效：{language}','Invalid language tag: {language}'],['保存失败：{error}','Save failed: {error}'],['关闭参数卡','Close settings card'],['本地参数选择卡','Local run settings card'],
    ['研究阶段语言：自由选择','Research language: unrestricted'],['界面语言与内容语言独立设置。','Interface and content languages are independent.'],['参数预览','Configuration preview']
  ];
  const forward = new Map(pairs), reverse = new Map(pairs.map(([zh, en]) => [en, zh]));
  const escape = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const templates = pairs.filter(([zh]) => zh.includes('{')).map(([zh, en]) => {
    const names = [...zh.matchAll(/\{(\w+)\}/g)].map(m => m[1]);
    const build = s => new RegExp('^' + s.split(/(\{\w+\})/).map(p => /^\{/.test(p) ? '([\\s\\S]*?)' : escape(p)).join('') + '$');
    return { zh, en, names, zhPattern: build(zh), enPattern: build(en) };
  });
  let language = 'zh-CN';
  const sourceNodes = new WeakMap(), sourceAttrs = new WeakMap();
  function t(value, vars = {}) {
    if (typeof value !== 'string') return value;
    let key = reverse.get(value) || value, captured = vars;
    if (!forward.has(key)) {
      for (const entry of templates) {
        const match = entry.zhPattern.exec(value) || entry.enPattern.exec(value);
        if (match) { key = entry.zh; captured = { ...Object.fromEntries(entry.names.map((name, i) => [name, match[i + 1]])), ...vars }; break; }
      }
    }
    const out = language === 'en' ? forward.get(key) || value : key;
    return out.replace(/\{(\w+)\}/g, (all, name) => captured[name] ?? all);
  }
  function setLanguage(next) {
    language = next === 'en' ? 'en' : 'zh-CN';
    if (typeof document !== 'undefined') document.documentElement.lang = language;
    try { localStorage.setItem('noemorph-ui-language', language); } catch (_) {}
    return language;
  }
  function getLanguage() { return language; }
  function applyStatic(root = document) {
    const skip = '#graph,#inspector-content,#project-home,#project-title,#question-title,#role-filters,#round-filters,#search-results,#content-language,[data-i18n-skip]';
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (!node.parentElement || node.parentElement.closest(skip) || ['SCRIPT','STYLE'].includes(node.parentElement.tagName)) continue;
      if (!sourceNodes.has(node)) sourceNodes.set(node, node.textContent);
      const source = sourceNodes.get(node), trimmed = source.trim();
      node.textContent = trimmed ? source.replace(trimmed, t(trimmed)) : source;
    }
    root.querySelectorAll('[title],[placeholder],[aria-label]').forEach(element => {
      if (element.closest(skip)) return;
      if (!sourceAttrs.has(element)) sourceAttrs.set(element, Object.fromEntries(['title','placeholder','aria-label'].filter(a => element.hasAttribute(a)).map(a => [a, element.getAttribute(a)])));
      for (const [attribute, source] of Object.entries(sourceAttrs.get(element))) element.setAttribute(attribute, t(source));
    });
  }
  return { t, setLanguage, getLanguage, applyStatic, pairs };
});
