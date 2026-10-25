# Knowledge Map 数据契约 · v1.0

这是可视化的独立格式，不改变原研究状态结构。完整可运行样例见 [`examples/demo.graph.json`](../examples/demo.graph.json)。

```json
{
  "schema_version": "1.0",
  "meta": {
    "title": "研究标题",
    "question": "原始问题",
    "language": "zh-CN",
    "language_label": "简体中文",
    "rounds": 1,
    "demo": false,
    "warnings": []
  },
  "nodes": [
    { "id": "question", "label": "原始问题", "type": "question", "importance": 5 },
    {
      "id": "direction:r1:d1",
      "label": "一个待探索方向",
      "summary": "已经取得的发现或当前边界。",
      "parent_id": "question",
      "type": "direction",
      "role": "predicate",
      "status": "frontier",
      "evidence": "unresolved",
      "importance": 2,
      "depth": 1,
      "round": 1,
      "origin_ids": ["d1"],
      "next_question": "下一步需要什么证据？",
      "links": [{ "label": "原始方向", "url": "notes/d1.md", "kind": "file" }]
    }
  ],
  "edges": [
    { "id": "e1", "source": "question", "target": "direction:r1:d1", "label": "广度方向", "kind": "path" }
  ]
}
```

## 节点

| 字段 | 语义 / 取值 |
| --- | --- |
| `id` / `label` | 非空字符串；ID 在整个图谱内唯一 |
| `type` | `question` / `concept` / `direction` / `finding` / `frontier`；默认 `concept` |
| `parent_id` | 渐进展开所用的展示父节点；可为空，必须存在且不能构成环 |
| `role` | `anchor` / `predicate` / `subject` / `predicate_abstraction` / `subject_abstraction`；默认 `anchor` |
| `status` | `discovered` / `explored` / `frontier` / `blocked` / `contradicted`；默认 `discovered` |
| `evidence` | `verified_direct` / `supported_with_limits` / `inferred` / `unresolved` / `contradicted`；默认 `unresolved` |
| `importance` | 1–5，有界数值，默认 2；阅读优先级，与证据无关 |
| `depth` / `round` | 可选的非负层数与研究轮次，默认 0 |
| `origin_ids` | 可选原研究 ID 数组，用于审计与搜索 |
| `summary` / `next_question` | 可选文本；界面用文本节点呈现，不解释为 HTML |
| `details` | 可选原始逻辑、条件与边界；在详情折叠区完整展示 |
| `links` | `{label, url, kind}` 列表，`kind` 为 `source` 或 `file`；未解析来源用 `url: null, note: "原因"` |

图上的 `↗` 优先打开第一个可用的 `source`，没有时打开第一个文件。详情中展示全部入口；不展示完整 URL，只显示标题、域名和跳转按钮。相对链接基于 HTML/JSON 所在位置；通过 CLI 导出时自动从输入目录重算到输出目录。

允许 `https:`、`http:`、`file:` 与普通相对路径，拒绝脚本协议、数据协议和协议相对地址。静态导入不会自动读取链接内容。局部 URL 应进行百分号编码，不要放原始空格或反斜杠。

## 连线与展开

`edges` 决定实际绘制的关系，可以有环。`parent_id` 仅定义展示层级；它必须是一个森林，不能有环。节点可有多个实际关系，但只有一个展示父节点。

`kind` 推荐使用 `path`（研究先后路径）、`contains`、`mechanism`、`analogy`、`transfer`、`related`、`conflict`。`analogy` / `transfer` / `related` 使用虚线，`conflict` 为冲突色。文字 `label` 承担具体的关系语义，不应把所有连线都命名为“导致”。每条边有唯一非空 `id`，端点必须存在。

默认主要发现包含 `importance >= 4` 的节点和必要上级。`+n` 只展开下一级，不从网络生成新知识。“完整网络”始终可以访问全部节点。待探索视图保留 `frontier` / `blocked` 节点及上下文。角色、轮次和状态是独立的筛选条件。

## 保存视图

界面导出会附加可选 `view`：`mode`、`selected`、`expanded`、`revealed`、`positions`（以节点 ID 为键的 `{x,y}`）与 `theme`。它仅影响展示；不会改变研究结论。筛选条件在重新载入时回到全部，以免误以为隐藏数据已经丢失。未提供布局时使用确定性布局；浏览器与 Python 校验器分别检查数据约束。

`view.ui_language` 为操作界面语言（`zh-CN` / `en`）；`view.content_language` 为内容语言标签或 `auto`（跟随界面）。二者互不约束。

此 SVG 阅读器适合数十到数百个节点的精读地图，导入上限为 5,000 个节点 / 20,000 条边；接近上限时建议分批研究与渐进展开，而非一次显示全部节点。

## 多语言包 · v1.0

单图兼容原格式。`meta.language` 用 BCP 47 声明实际内容语言；缺失或混合内容用 `und`，`meta.language_label` 是可选的原生语言显示名。多语言容器如下：

```json
{
  "bundle_version": "1.0",
  "source_fingerprint": "<原图 SHA-256>",
  "default_language": "zh-CN",
  "graphs": [
    {"schema_version": "1.0", "meta": {"language": "zh-CN"}, "nodes": [], "edges": []},
    {"schema_version": "1.0", "meta": {
      "language": "en", "language_label": "English",
      "translation": {
        "source_fingerprint": "<原图 SHA-256>",
        "source_language": "zh-CN", "target_language": "en",
        "translator": "<实际委派标识>"
      }
    }, "nodes": [], "edges": []}
  ]
}
```

此处省略了实际节点；真实文件中的每个 `graphs` 元素均为完整且有效的图谱。第一个元素是原图，后续是独立翻译；每种语言唯一，`default_language` 必须存在。所有版本具有相同节点/边顺序与结构，只允许改展示文字。顶层 `view` 保存跨语言共用的布局；可选 `run_config` 保存运行配置，不触发执行。

允许翻译 `meta.title/question/description/provenance/warnings`、节点 `label/summary/next_question/evidence_note/tags`、资料 `label/note`、边 `label`，以及 `details` 中的自然语言叶值。保留所有字段键、原始标识符、URL、逻辑查询、公式、数值、机器状态及证据值。结构检查不能自动判断文字中数字、公式和语义是否翻译准确；翻译者须核对这些内容。

指纹对原图研究内容整体计算 SHA-256，排除 `view` 与 `meta.language/language_label/translation`。Python 和浏览器使用同一个确定性编码：对象键按 UTF-16 顺序排列，数组保留顺序，字符串采用 JSON 编码，有限数值编码为 `n` 加 IEEE 754 双精度大端字节的 16 位十六进制。此编码只用于哈希，不是文件格式。请调用项目工具生成指纹，不能用普通 `json.dumps` 替代。

原图研究文字改动会使旧翻译绑定失效。导出时所有版本同步重算相对路径，并重新绑定输出原图。浏览器允许导入与当前原图匹配的单独翻译副本，不接受结构不符或缺失绑定的版本。详见 [语言版本流程](../references/11-language-variants.md)。
