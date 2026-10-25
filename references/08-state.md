# 可选结构审计脚本

脚本 `scripts/run_state.py` 仅用于管理**明确的大轮边界与结构计数**。它不会调用模型、不会检索文献、不会替代 Agent；状态文件存放在每次运行独立目录。

主 Agent 应将广度和深度子 Agent 返回内容转成 JSON 后由脚本合并，脚本保证：

- 初始概念拆解先于广度。
- 一个大轮需收到指定数量 Agent 各 5 个有效方向后才能筛选。
- 只有筛选出的 n 个方向全部提交深度结果后才能关闭该大轮。
- 每条深度路径至少记录 3 次逐级深入的**尝试**，不能把程序验证等同于事实验证。
- 每个大轮结束自动进入下一大轮，直到用户规定的大轮数结束。

## 命令

命令只需传入研究问题与参数；脚本不会注入任何研究领域示例。

- `python scripts/run_state.py init --state <state-path> --question <text> --rounds <integer> --agents <integer> [--top-n <integer>]`
- `python scripts/run_state.py decomp --state <state-path> --input <decomposition-json>`
- `python scripts/run_state.py breadth --state <state-path> --input <one-agent-json>`
- `python scripts/run_state.py select --state <state-path> --ids <comma-separated-ids>`
- `python scripts/run_state.py depth --state <state-path> --input <one-depth-json>`
- `python scripts/run_state.py close --state <state-path>`
- `python scripts/run_state.py status --state <state-path>`

`--state` 指向本次运行的独立 JSON 文件，不得复用旧状态文件。

## 初始拆解文件结构

需要：

- `concepts`：非空数组，每项至少有唯一 `id`、非空 `label` 与 `kind`。
- `relations`：数组，每项可有 `source`、`target`、`predicate`、`certainty`。
- `open_questions`：数组，保留拆解引出的开放问题。

所有内容由本次用户问题动态生成。不得读取预置概念库。

## 单 Agent 广度结果结构

需要：

- `round`：当前大轮编号。
- `agent_id`：本轮的实际子 Agent 标识。
- `directions`：**恰好 5 项**。每项至少包含唯一 `id`、`question`、非空 `anchor_ids`、`logical_move`、`discovery_target`、`search_route`、`bridge_test`、`novelty_reason`、`unknowns`。

`agent_id` 仅标记真实执行过该委托的子 Agent，不得捏造。子 Agent 调用轨迹由编排环境证明，脚本只能核对名称和计数。

## 单选中方向的深度结果结构

需要：

- `round`：当前大轮编号。
- `agent_id`：实际深度研究执行者标识。
- `direction_id`：已入选方向标识。
- `hops`：至少 3 项，每项至少包含 `question`、`finding`、`relation`、`evidence_refs`（数组）、`status`。
- `new_concepts`、`bridges`、`boundary_change`、`limits`、`unresolved`。

`status` 为 `verified_direct`、`supported_with_limits`、`inferred`、`unresolved` 或 `contradicted` 之一。出现证据断裂时允许使用 `unresolved`，不得人为凑出新的知识。

## 审计范围

脚本可查重、检查工作流顺序、字段和计数；无法检查搜索是否真的执行，也无法保证概念深度、研究原创性、来源有效性。主 Agent 必须自行审计真实工具调用和实际科学证据。
