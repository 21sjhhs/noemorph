# 研究输出的交互知识图谱

仅在本次研究成果已经形成后读取本文件。保留全部既有研究、审计与报告流程。可视化本身不触发新的检索或研究轮次；按本次语言选择执行的独立翻译委派见 `11-language-variants.md`。

## 交付

除原有综合报告、知识地图与研究目录外，生成 `knowledge-map.html` 与 `knowledge-map.graph.json`。使用本 skill 目录中的 `scripts/knowledge_map.py`；不要覆盖输入文件。

```sh
python3 <skill-dir>/scripts/knowledge_map.py \
  --input <run-dir>/state.json --allow-incomplete-languages \
  --output <run-dir>/knowledge-map.html
```

如果具体方向、逐跳发现和引用只在 Markdown 台账中，附加 `--breadth-ledger`、`--depth-ledger`、`--report`。适配器支持原生 `history` 结构和历史 `rounds / direction_ids` 结构。遇到其他格式时，按 `docs/graph-format.md` 从**已有本轮成果**生成标准图谱 JSON，再传给同一个导出器；不得通过猜测补齐缺失结论或来源。

## 数据组织

- 保留原问题、概念锚点、每轮全部原始广度方向、全部逐级推进记录、已记录的跨分支联系与未解决前沿。
- `origin_ids` 保存原始 ID；合并展示时保留每个来源 ID。
- `parent_id` 是渐进展开的阅读层级。实际关系放入 `edges`；不能因树状展示丢弃已记录的其他联系。
- `importance` 只表示阅读优先级。优先展示原问题和主要方向，其他方向折叠保留；未入选深度研究不等于删除。
- `status` 表示探索进度，`evidence` 表示证据强度，分别记录。不能因为做过深度探索就升级证据等级。
- 每个线索节点应带有已存在的原始文件或参考来源入口。用简洁 `label` 和按钮显示链接；未知来源保留标识并说明未解析，不构造假链接。
- 原始局部资料使用相对路径。CLI 会重算输入目录与导出目录之间的路径；分享时连同附件交付。
- 不把图中并排、相似形态或共同关键词自动解释成因果、同构或机制等价。

## 预览与检查

打开导出的 HTML，核对方向总数、深度记录数、原始 ID、证据状态和文件入口。默认看到主问题与主要方向，点击 `+n` 或双击逐级展开；完整网络与搜索能够访问折叠节点。图谱仅作为研究阅读界面，不替代原报告的完整性审计。

`plugins/knowledge-map/` 为配套静态 HTML 插件，可离线打开；`examples/` 只用于前端演示，**不得读入真实研究的冷启动或委派上下文**。

存在最终内容语言选择时，先执行 `11-language-variants.md` 的翻译与绑定，再通过 `--translation` / `--config` 打包全部语言。原图与翻译 JSON 各自保留；网页不会在切换界面语言时临时生成研究翻译。


仅查看尚未翻译的原始记录时，命令添加 `--allow-incomplete-languages`，混合原图声明 `--language und`。最终交付不使用该预览选项，必须按 `11-language-variants.md` 打包英文及其他请求语言。滚轮事件按动画帧更新；像素、行、页单位均归一化。窗口或详情面板改变尺寸时保留当前缩放，点击“适应窗口”才重新适配。
