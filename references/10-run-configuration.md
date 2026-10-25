# 研究启动前：跨宿主参数选择卡

只在用户要求运行一次新的 Noemorph 研究时使用。维护项目、调整界面、查看旧报告或翻译现有图谱不属于新研究，不应询问研究轮数。

## 一次收集参数

在步骤 0 之前收集并保存 `run-config.json`。用户已经明确提供的本次参数直接沿用，不要求再次批准，也不把默认值当成用户已经提交的答案。

卡片包含：研究问题、`macro_rounds`、`max_parallel_agents`、`top_n`、`depth_hops`、`presentation_languages`。界面语言 `ui_language` 独立于最终内容语言。

宿主有原生选择卡 / 问答控件时，优先使用该控件。可先执行以下命令获取与软件无关的字段描述，再映射到该宿主实际支持的工具参数：

```sh
python3 <skill-dir>/scripts/run_card.py prompt --question '<本次问题>'
```

不要假设其他软件存在某个特定厂商的工具名。原生控件不能容纳全部字段时，可分组呈现，或直接提供配套 HTML 卡片。没有原生控件但有本地 shell / 文件能力时，推荐：

```sh
python3 <skill-dir>/scripts/run_card.py serve \
  --question '<本次问题>' --directory <new-run-dir> --port 0
```

将输出的 `card_url` 作为可点击链接交给用户。用户提交后，程序将配置原子写入 `<new-run-dir>/run-config.json`，退出并向调用 Agent 返回配置。服务仅在本机运行，不会自行开展研究。等待真实提交；轮询或等待必须采用宿主允许的非阻塞方式，不能把超时当成选择。

不能启动本地服务时，使用离线卡：

```sh
python3 <skill-dir>/scripts/run_card.py render \
  --question '<本次问题>' --output <new-run-dir>/run-card.html
```

用户可下载 / 复制 JSON。由用户提供本次保存的文件路径；不得通过扫描旧配置来猜测选择。连 HTML 也无法展示时，给出编号文字选择卡，明确询问同样的参数。**不存在所有软件共用的原生选择卡 API；HTML、JSON 和文字卡是跨宿主降级协议。**

## 参数与原研究骨架的映射

| 参数 | 如何执行 |
| --- | --- |
| `macro_rounds` | 原流程恰好执行 N 个大轮；必填，不擅自增加或缩短 |
| `max_parallel_agents` | 同时活跃的工作子代理上限，1–5，或 `null` 表示自动适配；不包括主 Agent |
| `top_n` | 原选题阶段每轮深入的独立方向数；`null` 表示沿用原流程的默认目标与选择判断 |
| `depth_hops` | 每条深入路径的最低尝试次数，至少 3；更高值是用户对纵深的要求，证据不足仍要如实标记 |
| `presentation_languages` | 研究结束后的内容语言版本列表，例如 `['zh-CN','en']`；不约束研究语言 |
| `ui_language` | 网页操作界面的初始语言，`zh-CN` 或 `en`；不改变内容语言选择 |

五个逻辑角色及其隔离顺序不变：一个表层释义角色 + 四个广度探索角色。并发上限不是删除角色的开关。实际同时活跃的子代理数取用户上限、宿主能力和当前阶段需要的最小值；不足时分批调度。没有真实委派能力时遵循原 skill 的能力边界，不伪称已运行。

`scripts/run_state.py init` 的 `--agents` 是**广度提交者数量**，应为 4，不能把 `max_parallel_agents` 直接传给它。轮数和显式 `top_n` 可以映射到已有相应参数。脚本不执行研究，也无法替代实际委派记录；主 Agent 要在最终报告中说明实际调度能力与采用的批次策略。

原生卡答案转换为配置后可执行 `run_card.py validate --input <config.json>`。配置契约见 `docs/run-config.schema.json`。只使用本次研究的配置，保留原有冷启动与盲测隔离。

## 语言边界

`research_language_policy` 固定为 `unconstrained`。不要把最终内容语言写入研究 Agent 的检索语言限制或推理语言要求。研究完成、原始图谱冻结后，才按 `references/11-language-variants.md` 调度独立翻译子 Agent。
