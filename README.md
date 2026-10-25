# Noemorph

**Go beyond the question you asked. Discover the questions you didn't know existed.**

[简体中文](README.zh-CN.md) · [Skill instructions](SKILL.md) · [Architecture](references/ARCHITECTURE.md) · [QA report](QA_REPORT.md)

Noemorph expands the concepts behind a research question and recursively investigates promising connections. It maintains the existing Socrates Skill's five logical roles: interpretation, predicate expansion, subject substitution, predicate abstraction and subject abstraction.

The method is **concept transformation → breadth-first discovery → explicit branch selection → evidence-linked depth → a revised frontier**. It supports Concept Expansion, Recursive Exploration, Cross-disciplinary Knowledge Discovery and Deep Research. It is an instruction-driven Agent Skill with optional local tools; it is not an autonomous Python research service.

> Release status: research acceptance was stopped by the user. Publication proceeds at the user’s request with incomplete acceptance disclosed in [QA_REPORT.md](QA_REPORT.md). CI checks are manual only; publishing does not restart tests.

[Download v0.1.0-alpha.1](https://github.com/21sjhhs/noemorph/releases/tag/v0.1.0-alpha.1) — installable ZIP and SHA256 checksum.

## What a run does

1. Preserve the original question, whole concept, subject, process, conditions, ambiguity and user scope.
2. Let the interpretation role establish a working explanation before the other roles explore.
3. Give four transformation roles the same anchor. Each investigates five distinct directions, producing 20 candidates per round.
4. Have the main agent compare novelty, depth, bridge, evidence, overlap and risk, then select the user's `n` branches.
5. Make at least three successive evidence-seeking attempts per selected branch, retaining blocked and contradicted paths honestly.
6. Reinterpret the updated frontier and repeat exactly the user's `N` rounds. Retain useful findings from unselected branches in the final catalogue and graph.

The source materials disagree about five breadth agents versus one interpretation plus four breadth agents. This release preserves the specialized source entrypoint's **five roles / four breadth submitters / 20 directions**. It does **not** claim to implement five agents each generating five directions. The discrepancy and all migration decisions are recorded in the architecture.

## Install

Requires a compatible agent client. Verified source-backed research additionally needs that client's retrieval tools; independent workers need its actual delegation support. Local utilities require **Python 3.10+ standard library**. The HTML viewer needs a modern browser. Node.js 18+ is only needed for development tests. No API keys or model SDK are bundled.

The public repository is [21sjhhs/noemorph](https://github.com/21sjhhs/noemorph). This early release discloses incomplete acceptance in the QA report. Choose one installation destination, leaving the folder named `noemorph`:

```sh
# Codex: personal local skill
mkdir -p ~/.agents/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.agents/skills/noemorph

# Claude Code: personal local skill
mkdir -p ~/.claude/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.claude/skills/noemorph

# Cursor: personal local skill
mkdir -p ~/.cursor/skills
git clone https://github.com/21sjhhs/noemorph.git ~/.cursor/skills/noemorph
```

Run **one** relevant pair of commands. `git clone` refuses an existing destination instead of overwriting it. For a project installation, use the corresponding `.agents/skills/noemorph`, `.claude/skills/noemorph` or `.cursor/skills/noemorph` directory inside that project. Keep the entire skill directory, including the HTML assets. For other clients, place this directory in the client's documented skill location or explicitly ask the agent to read its `SKILL.md`.

Paths and discovery behavior are documented by [OpenAI](https://learn.chatgpt.com/docs/build-skills), [Claude Code](https://code.claude.com/docs/en/skills), and [Cursor](https://cursor.com/docs/skills). These are installation instructions, not a claim that native activation was tested in all clients. Restart/refresh discovery when the client requires it. Do not install duplicate copies with the same name into several discovery paths.

For an offline installation, unpack the locally built `noemorph.zip` into one of those skill roots, producing `<skill-root>/noemorph/SKILL.md`. Validate the extracted directory with `python3 <skill-root>/noemorph/scripts/validate_skill.py`.

## Invoke and configure

The commands below assume you changed into the installed skill directory, for example `cd ~/.agents/skills/noemorph` for that Codex installation. Use your actual chosen location for another client.

Use a natural-language request such as:

> Use Noemorph to discover overlooked interdisciplinary research directions from my hypothesis. Run two rounds, select four deep paths per round, and preserve all unselected findings. Ask for the hypothesis and scope if I have not supplied them.

In clients exposing explicit skill invocation, select Noemorph from the skill menu; Claude Code also supports `/noemorph`. Automatic discovery/activation depends on the host and competing skills. The description targets recursive knowledge exploration, not ordinary factual answers, simple summaries or literature retrieval alone.

The [parameter card](examples/run-card.html) collects rounds, scope/exclusions, concurrency ceiling, deep paths, minimum attempts and final content languages. A host can use its native question UI, a portable HTML card, JSON or text choices:

```sh
python3 scripts/run_card.py serve \
  --question 'Your research question' --directory runs/current --port 0
```

The agent sends the printed `card_url` to the user. After actual submission, the utility writes `runs/current/run-config.json`, returns the configuration and exits. It does not start research. Use `run_card.py prompt` for portable field metadata or `run_card.py render --question 'Your question' --output runs/current/run-card.html` for an offline card.

Five logical roles remain fixed. The subagent setting is a **concurrency ceiling**, not a switch to remove roles. When real workers cannot run simultaneously, batch them. When no delegation exists, disclose `role_sequential`, keep separate role records and the same anchor, and do not claim independent models. A single-context fallback cannot guarantee independent cognition. If the user requires genuine isolation, the run remains blocked until that capability is available.

![Noemorph interactive knowledge map — synthetic demonstration](docs/preview.png)

## Read and share the map

Open [the static viewer](index.html) or [the standalone example](examples/knowledge-map.html). The example is synthetic UI data, not scientific evidence or a demonstration of completed research. For local HTTP preview:

```sh
python3 scripts/serve.py --port 8765
```

The map supports node/background dragging, wheel/pinch zoom, progressive branch expansion, search across collapsed nodes, role/round/status filters, a minimap, source/file jump buttons, light/dark themes and HTML/JSON/SVG export. Node importance represents reading priority; evidence is labeled separately.

```sh
python3 scripts/knowledge_map.py \
  --input runs/current/state.json --output runs/current/knowledge-map.html
```

If details live in Markdown ledgers, pass `--breadth-ledger`, `--depth-ledger` and `--report`. The exporter accepts the preserved v4 state, a supported historical ledger format or a standard [graph JSON](docs/graph-format.md). It reads existing output and does not conduct research. Local attachments remain separate relative files: keep them beside the shared output as linked, or re-export after moving the package.

## Two independent language settings

“中 / EN” changes interface controls. The graph-language selector switches existing content versions or follows the interface. Content switching retains node IDs, layout, zoom, expanded branches and selection.

Final content language does **not** constrain the language used for research or retrieval. After freezing the source graph, a real translation worker generates a full copy per requested language, preserving structure, IDs, sources, logic and evidence qualifiers. Declare `meta.language`, bind it with `graph_languages.py`, then pack it with repeatable `knowledge_map.py --translation`. The utility validates/binds; it does not translate or spawn workers. Missing delegation or translations must be reported. See [language variants](references/11-language-variants.md).

## Inspect, update and uninstall

Inspect `SKILL.md` and the scripts before installation. To update a clean clone:

```sh
git -C ~/.agents/skills/noemorph pull --ff-only
```

Use the path you installed into. Preserve local changes before updating. To uninstall reversibly, move that `noemorph` directory out of all client discovery roots, for example to a backup directory. If you no longer need it, delete only that skill directory; no global client settings or credentials were installed. Restart/refresh the client as needed. The project does not install a daemon, hook, model runtime or third-party marketplace plugin.

## Validate and package

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

`validate_skill.py` implements the applicable [Agent Skills specification](https://agentskills.io/specification) constraints for this repository's flat YAML subset and checks entrypoint paths. It is not the official validator or a general YAML parser. If installed, `skills-ref validate ./noemorph` is the official alternative from the parent directory. Tests do not prove research novelty or citation truth; see `QA_REPORT.md` for exact performed checks and limits.

## Repository layout

```text
SKILL.md / AGENTS.md          Portable entrypoints
README.md / README.zh-CN.md   Installation and use
references/                  Architecture, operators, workflow, output and preserved sources
scripts/                     State audit, cards, graph tools, validation, packaging, publication
plugins/knowledge-map/        Offline HTML/SVG viewer and card
examples/                    Synthetic UI and input/output-format examples
tests/                       Executable regression tests
audit/                       Sanitized source manifest and performed evaluations
.github/                     Manual checks and publication metadata
LICENSE / NOTICE             Apache-2.0 and provenance
QA_REPORT.md                  Release acceptance and unverified capabilities
```

## Differentiation and limits

Compared with a conventional research synthesis, Noemorph explicitly transforms subjects, predicates and abstraction levels before selecting paths. Compared with Socratic questioning, the emphasis is generating researchable conceptual neighborhoods with evidence-linked exploration. Compared with recursive task decomposition, recursion revises a knowledge frontier rather than only splitting a task into subtasks. These are mechanism descriptions, not controlled evidence of superior performance. Neither independent execution nor scientific discovery is guaranteed by a prompt file.

## License and publication

[Apache-2.0](LICENSE), with original-project attribution in [NOTICE](NOTICE). The rights holder confirmed licensing of the original code and instructions. External papers, linked material, private research, and third-party services retain their own rights and are not bundled. GitHub settings live in `.github/repository.json`; `python3 scripts/publish.py --dry-run` shows the plan, and `python3 scripts/publish.py` uses an installed/authenticated GitHub CLI after scans and a clean local commit. It refuses unrelated origins and never force-pushes.
