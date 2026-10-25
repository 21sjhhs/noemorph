# 研究后的图谱语言版本

本阶段只翻译已有输出，不改变原研究问题的求解过程、检索范围或任何结论。先完成原报告与原始 `graph.json`，再读取本次 `run-config.json` 中的 `presentation_languages`。

## 独立翻译委派

每个缺失的目标语言版本交给**一个实际调用的翻译子 Agent**。只传入原始图谱、目标语言标签与下面的约束，不传入新研究任务。可复用工作资源，但要清楚区分翻译阶段；记录实际委派标识，不能用主 Agent 自述扮演冒称真实子 Agent。

推荐委派文本：

> 只读取指定的源 graph.json，生成同一图谱的目标语言完整 JSON 副本。翻译可展示的自然语言：meta 的标题/问题/描述/说明，节点 label/summary/next_question/evidence_note，details 中的自然语言、tags、资料 label/note，以及 edge.label。保留所有节点、边、顺序、字段键、id、parent_id、source/target、origin_ids、链接 url/kind、role/type/status/evidence、importance/depth/round/selected、数字、DOI、公式与逻辑查询。details 中的原始标识符和 typed_queries 不翻译。不要添加结论、重新研究、压缩限定条件或升级证据。原图只读；目标文件声明 meta.language（BCP 47，如 zh-CN、en、ja）和 meta.language_label。先核对结构与引用，再提交目标 JSON 以及真实翻译 Agent 标识。

`meta.language='und'` 表示原始内容混合或未标注，不能把混合中英的原文件直接声明为完整中文或英文。原图已经完全使用某种目标语言时，可以直接把原图作为该语言版本；不必额外委派同语言翻译。

没有真正的翻译子 Agent 能力时，明确说明该阶段未执行，保留原始版本与待执行任务，不能把界面字典替换冒称为研究内容翻译，也不能让界面显示不存在的语言版本。

## 绑定与验证

子 Agent 提交后执行：

```sh
python3 <skill-dir>/scripts/graph_languages.py \
  --source <run-dir>/graph.json \
  --translation <run-dir>/graph.en.draft.json \
  --translator '<actual-translation-agent-id>' \
  --output <run-dir>/graph.en.json
```

这个脚本不翻译文字。它检查只改了允许展示的字符串，并写入原图指纹、源语言、目标语言及翻译者标识。自然语言语义是否准确仍由翻译 Agent 与主 Agent 检查；结构校验不能证明翻译质量。

```json
{
  "meta": {
    "language": "en",
    "language_label": "English",
    "translation": {
      "source_fingerprint": "<sha256 of the current source graph>",
      "source_language": "und",
      "target_language": "en",
      "translator": "<actual delegated agent identity>"
    }
  }
}
```

原图改过任何研究文字后，需要重新生成对应翻译；不能把旧语言版本挂到新结论上。仅改变视图、节点位置或语言声明不改变原图指纹。文件路径重算由导出器对全部版本一致处理。

## 与网页对接

```sh
python3 <skill-dir>/scripts/knowledge_map.py \
  --input <run-dir>/graph.json \
  --translation <run-dir>/graph.zh-CN.json \
  --translation <run-dir>/graph.en.json \
  --config <run-dir>/run-config.json \
  --output <run-dir>/knowledge-map.html \
  --json-output <run-dir>/knowledge-map.bundle.json
```

导出的 HTML 内嵌原图和所有语言版本。JSON 输出是 `bundle_version='1.0'` 的语言包，每个图谱仍是完整的 `schema_version='1.0'` JSON。原始 `graph.json` 和各翻译 JSON 不被覆盖。

网页的“中 / EN”切换操作界面；“图谱内容语言”下拉框选择已经声明的内容版本。选择“跟随界面”时，存在对应版本便同步切换；不存在时保留可用版本并提示。用户可以固定中文内容配英文界面，反之亦然。切换保留节点 ID、手动布局、展开状态、筛选、当前节点和缩放；不会即时调用模型翻译。
