# Go beyond the question you asked. Discover the questions you didn't know existed.

**Noemorph** turns a research question into new directions to investigate, connections across disciplines, and an interactive knowledge map you can keep exploring.

An open-source **AI research skill** for **research question generation, hypothesis exploration, and cross-disciplinary knowledge discovery**. Bring a question to your AI agent. Find out where it can lead.

[Get started](#quick-start) · [See what you get](#a-map-you-can-keep-exploring) · [简体中文](README.zh-CN.md)

![Noemorph interactive knowledge map showing new questions, connected research paths, and evidence details](docs/preview.png)

*Interactive map preview with illustrative demo data.*

## When you have a question—but need a new direction

You know the topic. You have read the obvious papers. Yet the next useful question is still hard to see.

Noemorph helps you look beyond your starting frame: explore other explanations, look for the same process in different systems, and ask which ideas from another field might transfer. Promising directions become deeper investigations, with sources and uncertainties kept alongside the findings.

Use it when you want to:

- **Find your next research question.** Explore open directions around a topic or an early hypothesis.
- **Connect ideas across fields.** Look for shared mechanisms, useful analogies, and the conditions under which they hold.
- **Challenge a familiar explanation.** Investigate alternative objects, processes, and levels of analysis.
- **Build a research agenda.** Keep the paths worth pursuing, the evidence behind them, and the questions still open.

## Start with something you are curious about

After installing the skill, give your agent a request like this:

> Use Noemorph to explore this question: Why do some online communities retain useful knowledge while others repeatedly lose it? Look for connections across disciplines and turn promising ideas into researchable questions. Run two rounds, investigate four paths per round, and deliver an English report with an interactive knowledge map. Keep sources, uncertainty, and unselected findings.

An exploration might ask whether the answer changes with community size, what other systems preserve information under turnover, or which findings about memory can usefully transfer to a community. These are illustrative starting directions, not research results.

**Bring your own question, hypothesis, or puzzling observation.** You choose the scope and how far to explore.

## A map you can keep exploring

The output is a connected record of the investigation:

| You receive | What you can do with it |
| --- | --- |
| **New research directions** | See questions that extend your original framing, including paths not selected for deeper study. |
| **Evidence-linked research paths** | Follow how one finding leads to the next question, with sources, assumptions, and unresolved gaps. |
| **An interactive knowledge map** | Expand branches, search across hidden nodes, filter findings, and jump to source links. |
| **A synthesis and research catalogue** | Review the main findings and return to the full set of discoveries later. |
| **Shareable files** | Export HTML, JSON, or SVG; keep linked local attachments beside the shared output. |

The map viewer works locally in a browser. It includes light/dark themes and separate controls for interface language and available content translations.

To explore the bundled demo, clone the repository, then run from its parent directory:

```sh
cd noemorph
python3 scripts/serve.py --port 8765
```

Open <http://127.0.0.1:8765>. The [standalone example](examples/knowledge-map.html) can also be downloaded and opened locally. The demo shows the interface using synthetic data.

## Quick start

Noemorph runs inside your AI agent client. Choose **one** installation below, then ask your agent to use Noemorph with your question.

<details open>
<summary><strong>Codex</strong></summary>

```sh
mkdir -p ~/.agents/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.agents/skills/noemorph
```

</details>

<details>
<summary><strong>Claude Code</strong></summary>

```sh
mkdir -p ~/.claude/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.claude/skills/noemorph
```

</details>

<details>
<summary><strong>Cursor</strong></summary>

```sh
mkdir -p ~/.cursor/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.cursor/skills/noemorph
```

</details>

Refresh skill discovery or restart the client if needed. Ask: **“Use Noemorph to explore [your question].”** In Claude Code, you can also invoke `/noemorph`. Discovery and activation depend on the client; native activation has not been tested in every client.

For another client, keep the complete `noemorph` folder in its supported skill directory, or ask the agent to read its `SKILL.md`. Source-backed research needs the client's retrieval tools; independent research workers need delegation support. Local utilities use Python 3.10+ with the standard library. No API key or model runtime is bundled.

The agent collects your question, scope, number of rounds, paths to investigate, and output languages before starting. See the [example research request](examples/research-request.md) for a fuller prompt.

## How the exploration grows

**Your question → new directions → selected investigations → connected findings → new questions.**

Each round first clarifies the question, then explores it from four complementary perspectives. The agent compares the resulting directions, investigates selected paths, and uses what it learns to shape the next round. You control the scope and stopping point; unselected findings remain available.

Noemorph combines concept expansion, recursive deep research, and knowledge graph exploration. The [workflow](references/WORKFLOW.md) and [architecture](references/ARCHITECTURE.md) explain the method in detail.

## Questions before you start

**Does this run research by itself?** It is an Agent Skill: your client supplies the model, retrieval, and execution. The bundled scripts collect settings, check records, and build maps.

**What if my client cannot run independent agents?** The workflow supports separately recorded roles executed in sequence, with that limitation disclosed. Independent contexts require actual delegation support.

**Can I trust every connection?** Findings must distinguish evidence, hypotheses, analogies, and unresolved questions. Treat a promising connection as a lead to examine. This is an early alpha; end-to-end research acceptance remains incomplete. See the [QA report](QA_REPORT.md) for performed checks and limitations.

**Can I update or remove it?** Run `git -C <your-skill-directory>/noemorph pull --ff-only` to update a clean clone. To uninstall, move the folder out of the client's skill directory and refresh discovery. Preserve any local changes first.

## Explore the project

[Skill instructions](SKILL.md) · [Research workflow](references/WORKFLOW.md) · [Graph format](docs/graph-format.md) · [Development and checks](docs/development.md) · [Agent-readable overview](llms.txt)

Contributions to documentation, research workflows, and the map viewer are welcome. See the development guide for validation and packaging commands.

Licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) for attribution and third-party material boundaries.
