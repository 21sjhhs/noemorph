# Architecture and audited migration

Noemorph is an Agent Skill for **Multi-Agent Knowledge Exploration**. The client executes the research instructions using its actual model, delegation and retrieval tools. Python utilities validate/persist records and render output; none of them executes a language model or a search.

## Components

| Component | Responsibility | Execution boundary |
| --- | --- | --- |
| Main agent | Interpret, construct anchor, delegate, select branches, connect findings, maintain state and synthesize | Client-provided agent |
| Interpretation role | Clarify the user's whole question, definitions, conditions and ambiguity; recalibrate each round | A real subagent when available |
| Four transformation roles | Predicate expansion, subject substitution, predicate abstraction, subject abstraction | Independently supplied the same anchor; batch if needed |
| Depth workers | Evidence-linked successive questions on selected branches | May reuse workers, with explicit stage identity |
| `run_state.py` | Phase ordering, per-submitter five-direction count, exact-ID / normalized-text duplicates, selected paths, minimum three attempts, round termination | Deterministic structural audit only |
| `audit_run.py` | Read-only checks against the maintained four-submitter protocol and optional run configuration | Does not establish scientific truth or semantic novelty |
| `run_card.py` | Portable fields, offline HTML and loopback save/return | Requires a real user submission; no research execution |
| `knowledge_map.py` | Read existing records; preserve all branches; export standalone graph / HTML | Does not reassess citations |
| Graph languages | Full display-text translations, source binding, language declarations | Translation uses an actual delegated agent or is reported unavailable |

## Preserved algorithm

`user question → neutral typed decomposition → interpretation → shared anchor → four independent transformations × five directions → main-agent selection → selected multi-hop research → evidence audit → new frontier → next round → complete output`

Breadth comes before depth. The semantic operations are substitutions and justified type-lifts, not a to-do list or five rephrasings. The original question remains a reference point across rounds. An unselected finding remains part of the knowledge catalogue.

## Source discrepancies and decisions

The audit read the source entrypoint, all eight original research references, state implementation and its tests, rather than deriving the workflow from the README.

| Source difference | Actual implementation | Migration decision |
| --- | --- | --- |
| Source `SKILL.md`: five logical roles, Role 1 interpretation only, Roles 2–5 five directions | 20 breadth directions per round | Preserve this specialized entrypoint as the maintained protocol |
| Legacy `02-breadth.md`: Ontology / Transformation / Relation / Representation / Outsider, each five directions | A different method-role description; no dispatcher selects it | Preserve as historical source; do not mix it with the five specialized roles |
| State CLI defaults `--agents 5` | Accepts generic submitter counts; no role identity check | Preserve engine behavior; maintained instructions explicitly pass `--agents 4` |
| Requested five agents each producing at least five directions | Not implemented by the specialized entrypoint | Explicitly record the gap; a 25-direction mode would require a separately reviewed algorithm change |
| Legacy selection reference suggests 3–8 paths; source entrypoint targets four | State accepts explicit `top_n`, does not score candidates | Use source entrypoint's target four; user setting takes precedence |
| Legacy multi-anchor selection constraint conflicts with user `n = 1` | Engine accepts one selected path | Clarify that set diversity cannot require extra branches beyond user `n` |
| Source entrypoint refers to absent role/breadth/report/state files | Several references do not resolve | Maintained entrypoint links actual files; the baseline records the historical instructions |
| State phase goes straight to breadth after round close | Reinterpretation is a prompt instruction, not a state phase | Preserve and disclose; do not claim code enforces anchor recalibration |
| Depth minimum in state code is three | A higher card setting is not enforced by the original engine | Preserve engine; prompt and optional read-only `audit_run.py --config` check the higher minimum |
| State frontier aggregates depth `new_concepts` | Unselected directions remain in `history`, not the frontier list | Main agent must reconsider unresolved historical directions; map export includes all breadth records |

The maintained `SKILL.md`, this architecture, `WORKFLOW.md` and `EXPLORATION_OPERATORS.md` govern new runs. The archived `NOEMORPH_SKILL.baseline.md` and contradictory legacy method-role passages are baseline records, not alternate runtime instructions. On 2026-10-26, branding maintenance renamed and normalized the archived entrypoint and changed the state utility's temporary-file prefix. Those two lock records were explicitly updated, retaining their prior hashes; they are not byte-identical to the earlier baseline. `references/01–08` and the state tests retain their original hashes. `scripts/check_upstream.py` checks the recorded baseline in `upstream.lock.json`. The maintenance does not change research operators, role counts, or state transitions.

## Implemented versus specified

Executable and tested: structural state transitions, input/output preservation, graph rendering, language binding, run cards, export and validation. Prompt-specified: operator fidelity, interpretation quality, search strategy, selection reasoning, semantic deduplication, cross-round novelty and source verification. Host-dependent: real delegation, independent contexts, retrieval, model compliance and automatic skill activation. No benchmark establishes superiority over Deep Research, Question-led questioning or recursive decomposition.

The optional viewer exposes `NoemorphGraph`, `NoemorphLanguages`, `NoemorphI18n`, and `NoemorphSettings` JavaScript namespaces. Historical state v4 remains supported. Run cards accept `noemorph-run-config/1.0` and the `X-Noemorph-Token` header; retired branding aliases and preference-key fallbacks were removed. Older run configurations must use the current schema identifier; earlier browser preferences reset to the current defaults. The repository is a standard skill folder; `plugins/knowledge-map/plugin.json` is a static-viewer manifest, not a marketplace installation claim.
