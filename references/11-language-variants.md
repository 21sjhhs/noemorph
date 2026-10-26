# 研究后的图谱语言版本

本阶段只翻译已有输出，不改变原研究问题的求解过程、检索范围或任何结论。先完成原报告与原始 `graph.json`，再读取本次 `run-config.json` 中的 `presentation_languages`。无论卡片历史选择如何，每次都必须交付英文 `en`，并补齐用户选择的其他语言。

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


## 完整性与旧图谱

可展示文字包括节点正文、摘要、边标签、资料标题和说明，以及节点和边的 details 中嵌套的自然语言（包括边的自然语言证据说明）。不能只翻译标题或把英文研究记录原封不动留在中文详情中。字段键、原始标识符、typed_queries、formal_logic、DOI、完整 URL（包括数组里的直接链接）和机器枚举保持不变；这些不是叙述性正文。文献标题可给目标语言译名，来源 URL 保留。

翻译绑定会检查明显的语言残留：英文展示字段含汉字、中文展示字段含八个以上英文词且无汉字时拒绝。该启发式只捕获明显遗漏，不是语义翻译质量证明；仍需翻译 Agent 和主 Agent 逐项核对。合法专名/术语需人工检查，不能通过删除原文、略去限定或统一贴标签来规避。

网页载入明显混合、却错误标注语言的旧原图时，将其显示为 `und`（原始记录），并提示缺失版本；不冒充翻译。新最终导出始终检查必备英文，并在未传 `--config` 时也读取图谱内嵌的 `run_config`。仅供查看原始记录时，可显式使用 `--allow-incomplete-languages`；预览不代表语言交付已完成。混合原图使用 `--language und`，所有翻译仍绑定同一原始内容指纹。


## 最终语言交付门槛

在主 Agent 声明图谱已完成之前，执行以下核对；发现问题应修复后重新验证，不能只改语言标签：

1. 核对必备集合：英文 `en` 加用户请求的其他语言。原始混合记录 `und` 不计作任何目标版本；不能因旧配置只选中文就省略英文。每个缺失版本按本文件要求实际委派独立翻译 Agent。
2. 翻译 Agent 与主 Agent 逐字段核对标题、标签、摘要、下一问、参考资料说明，以及节点和边 details 中的自然语言。中文句子里夹杂的短英语名词、动词和短语也需翻译；即使不足八个英文词，或同一句已有汉字，也不能据此视为已完成。保留必要技术缩写、作者/机构正名、拉丁学名、单位、URL、DOI、逻辑公式和机器字段；术语需保留原文时提供中文译名或说明。
3. 运行翻译绑定与最终导出，确认源指纹、节点/边结构、标识符、来源链接和证据状态一致；复核数字、单位、否定及适用条件没有被遗漏。最终交付不得使用 `--allow-incomplete-languages` 绕过缺失版本；未完成时明确列出缺失项，并将已有结果标为预览。
4. 打开最终生成的 HTML，用内容语言下拉框逐一检查全部目标版本，并在“跟随界面”模式下检查中英界面切换时实际内容随对应版本切换；检查节点详情和连接详情，并保留布局、选择及缩放。若浏览器验证不可用，说明未执行的检查，不得报告已经通过。

自动语言残留检查只能识别明显遗漏；结构与指纹验证也不能证明翻译语义正确。两者通过后，仍需上述逐字段复核。
