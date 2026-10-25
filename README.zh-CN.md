# Noemorph

**Multi-Agent Knowledge Exploration · 多 Agent 知识探索**

[English](README.md) · [Skill 入口](SKILL.md) · [架构](references/ARCHITECTURE.md) · [验收报告](QA_REPORT.md)

Noemorph 由现有 Socrates Skill 整理而来，保留原问题解释、谓词拓展、主词替换、谓词抽象、主词抽象五种逻辑角色。目标是从研究问题中发现尚未提出的问题，递归追踪有依据的新方向，而非把主题改写成关键词清单或普通文献综述。

> 发布状态：用户已主动终止研究验收测试，同时要求继续打包发布。[QA_REPORT.md](QA_REPORT.md) 如实保留未完成验收和历史测试结果。CI 仅允许手动运行，发布不会重新启动测试。

[下载 v0.1.0-alpha.1](https://github.com/21sjhhs/noemorph/releases/tag/v0.1.0-alpha.1)：含可安装 ZIP 与 SHA256 校验文件。

## 保留的研究机制

先拆解整体概念、主词、过程、关系、条件与歧义；释义角色完成基础解释后，四种变换角色在共享锚点上独立探索。每个广度角色提交五个不同方向，主 Agent 依据边界拓展、深度、桥接、证据、去重和风险选择 `n` 条，再对每条至少尝试三次连续推进。每轮更新前沿并重新校准原题，直到用户规定的 `N` 轮。未入选纵深的有效发现仍保留在最终目录和图谱中。

**实际默认是五种角色、四个广度提交者、每轮 20 条方向。** 原项目部分旧参考文件和脚本默认值仍按五个广度提交者描述；“五人各五条、共 25 条”并非当前专门化入口的行为。本次记录了差异，未静默改变研究算法。原始研究文件及其哈希基线仍保留。

## 安装与调用

需要兼容 Agent Skills 的客户端。真实研究依赖宿主的检索能力；独立子代理依赖实际委派工具。辅助脚本只需 Python 3.10+ 标准库；HTML 图谱需现代浏览器；开发测试另需 Node.js 18+。本项目没有自带模型 SDK、API Key 或自动研究服务。

公开仓库：[21sjhhs/noemorph](https://github.com/21sjhhs/noemorph)。这是明确披露验收尚未完成的早期版本，具体状态见验收报告。根据客户端选择其中一个安装位置：

```sh
# Codex
mkdir -p ~/.agents/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.agents/skills/noemorph

# Claude Code
mkdir -p ~/.claude/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.claude/skills/noemorph

# Cursor
mkdir -p ~/.cursor/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.cursor/skills/noemorph
```

只执行适用的一组命令。已有同名目录时 `git clone` 会拒绝覆盖。项目级安装改用项目内的 `.agents/skills/noemorph`、`.claude/skills/noemorph` 或 `.cursor/skills/noemorph`。其他客户端按其官方目录规则放置完整文件夹，或明确要求 Agent 读取此项目的 `SKILL.md`。

安装位置与发现机制依据 [OpenAI](https://learn.chatgpt.com/docs/build-skills)、[Claude Code](https://code.claude.com/docs/en/skills)、[Cursor](https://cursor.com/docs/skills) 官方文档核对；这不代表已在三个客户端都完成原生激活测试。必要时刷新或重启客户端，避免同名 Skill 安装到多个发现路径。

离线安装时，可把本地产出的 `noemorph.zip` 解压到上述任一 Skill 根目录，形成 `<skill-root>/noemorph/SKILL.md`；运行其中 `scripts/validate_skill.py` 验证。

调用示例：

> 使用 Noemorph，从我的假设生成被忽略的跨学科研究方向。运行两轮，每轮选择四条深入路径；未入选方向的有效发现也保留。若我还没提供假设和范围，请先收集。

支持显式调用的客户端可从菜单选择 Noemorph；Claude Code 也支持 `/noemorph`。自然语言自动激活取决于宿主与其他 Skill，不保证百分之百触发。

## 参数、范围和兼容降级

以下辅助命令在安装后的 Skill 目录运行，例如 Codex 对应 `cd ~/.agents/skills/noemorph`；其他客户端使用实际安装位置。

配套[参数卡](examples/run-card.html)收集轮数、研究范围与排除项、子代理并发上限、深入路径数、最低推进次数和最终内容语言。宿主原生选择卡优先，无对应控件时使用 HTML、JSON 或编号文字卡。

```sh
python3 scripts/run_card.py serve \
  --question '本次研究问题' --directory runs/current --port 0
```

Agent 将返回的 `card_url` 发送给用户；真实提交后配置保存到 `run-config.json`，程序返回配置并退出。卡片不会自行开始研究。离线卡可复制或下载 JSON；`run_card.py prompt` 提供跨宿主字段协议。

五个逻辑角色不因并发设置而删除。宿主能力不足时分批使用真实子代理；完全没有委派工具时，明确标记 `role_sequential`，使用同一锚点、分开的角色记录，并避免把前一角色发现送入下一角色提示。单一上下文不能保证认知独立，不得声称等同于五个独立 Agent。用户若要求真实隔离，应报告能力缺口并保留待执行任务。

![Noemorph 交互知识图谱——合成演示数据](docs/preview.png)

## 图谱与语言版本

打开 [index.html](index.html) 或[独立演示 HTML](examples/knowledge-map.html)。演示是合成界面数据，不是完成真实研究的证据，也不能作为冷启动上下文。需要本机 HTTP 预览时执行：

```sh
python3 scripts/serve.py --port 8765
python3 scripts/knowledge_map.py \
  --input runs/current/state.json --output runs/current/knowledge-map.html
```

图谱可拖动、缩放、逐级展开、搜索折叠节点，支持角色/轮次/状态筛选、缩略图、资料跳转、明暗主题及 HTML/JSON/SVG 导出。适配器读取原 v4 状态、支持的历史台账或标准图谱，不开展研究、不重新核验引文。资料在 Markdown 中时附加 `--breadth-ledger`、`--depth-ledger`、`--report`。本地附件仍是独立相对文件，分享时一起携带；移动目录后应重新导出以重算路径。

顶栏“中 / EN”控制操作界面，内容语言下拉框控制已有图谱版本。切换保留位置、缩放、分支和当前节点。最终内容语言不限制研究和检索语言；原图冻结后，才委派实际翻译子 Agent 生成完整语言副本，声明 `meta.language` 并绑定原图指纹。工具只校验和打包，不自动翻译。缺失的子代理能力或翻译版本必须如实报告，详见[语言版本规范](references/11-language-variants.md)。

## 更新与卸载

在实际安装路径执行 `git pull --ff-only`；有本地改动先保存，不强制覆盖。卸载时将对应的 `noemorph` 文件夹移出客户端发现路径即可，可先移到备份目录保留回滚；确定不再需要时只删除该 Skill 文件夹。本项目没有安装全局配置、常驻服务、钩子或凭据。按宿主需要刷新发现列表。

## 验证与发布

```sh
python3 scripts/validate_skill.py
python3 scripts/check_upstream.py
python3 -m unittest discover -s scripts -p 'test_run_state.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/graph-core.test.cjs tests/languages.test.cjs
python3 scripts/release_scan.py
python3 scripts/build_demo.py
python3 scripts/package_skill.py --output dist/noemorph.zip
```

本地规范检查针对本仓库使用的扁平 YAML 子集，依据 [Agent Skills 规范](https://agentskills.io/specification)实现等效约束及引用检查，不冒称官方验证器。安装官方 `skills-ref` 后也可从父目录执行 `skills-ref validate ./noemorph`。

完整架构、差异和输出格式在 `references/`；验收报告列出实际测试、失败项和未验证能力。脚本能验证结构计数，不能证明概念新颖性、论文支持关系或真实 Agent 调用。项目尚无证明优于 Deep Research、苏格拉底提问或递归任务分解的对照实验。

采用 [Apache-2.0](LICENSE)，原项目权利人已确认授权，来源说明见 [NOTICE](NOTICE)。外部文献、用户私有研究和第三方服务不在授权范围内，也未打包。`.github/repository.json` 保存拟用描述与 Topics；`publish.py --dry-run` 查看发布计划，`publish.py` 使用已有且已登录的 GitHub CLI，经扫描和干净提交检查后发布，不强推、不改无关远程仓库。
