# Run workflow and portability

## Configuration and scope

Use `run_card.py prompt` to map fields to the host's actual question UI, or `run_card.py serve --question '<question>' --directory <new-run-dir> --port 0`. The HTML card saves `run-config.json` and returns only after user submission. Offline `render` supports JSON download/copy. If neither cards nor HTML are supported, ask the same numbered text choices. Do not fabricate a universal native-card API.

Keep the original question, explicit scope/exclusions, `macro_rounds`, `top_n`, `depth_hops`, `max_parallel_agents`, UI language and final content languages with this run. Already supplied choices need no second confirmation. Do not read a different run's old settings. `scope` is a user-supplied boundary, not a preset discipline. Stop or ask if a necessary expansion would violate it.

## Five roles under different hosts

| Mode | Scheduling | Claim allowed |
| --- | --- | --- |
| `independent_agents` | Interpretation first, then four isolated breadth workers; actual tools identify workers | Real independent agent calls, subject to host context isolation |
| `batched_agents` | Same roles and immutable anchor, batches bounded by user ceiling and host capacity | Real agent calls in batches; not five concurrent workers |
| `role_sequential` | No delegation: disclose this mode, complete interpretation then each transformation in separate output records; keep the same anchor and do not feed earlier-role findings into later prompts | Five separated method roles; not five independent models or truly isolated cognition |

Prefer fresh contexts for sequential role execution when the host supports them. A single conversation cannot erase what the model already saw; disclose this limitation rather than claiming equivalence. If the user requires independent agents and none are available, stop that run and provide a pending task package. No private SDK, API key, shell command name or hidden provider tool is assumed.

Real retrieval is required for research claims. When unavailable, continue only as an explicitly labeled prompt-only exploration plan with `unresolved` evidence, or stop if the user requires verified research. Never count a generated citation as a completed search.

## Each macro round

1. Main agent decomposes the question; Role 1 establishes/recalibrates a working interpretation.
2. Freeze the anchor. Roles 2–5 independently investigate five distinct questions each. Correct invalid submissions with the actual worker when available.
3. Review all 20 directions, their overlap and uncertain evidence. Main agent selects `n` with explicit criteria and set-level diversity; keep the unselected records.
4. Depth workers make successive attempts from selected questions. No unverified intermediate finding becomes a proved premise.
5. Review bridge types, contradiction and scope. Preserve all findings and unresolved paths, update the frontier, and re-anchor the next round to the original question.
6. Close exactly `N` rounds, or report a partial run if resources/tools prevent completion. Do not silently extend or prematurely declare success.

For `n = 1`, select the best justified single branch; the legacy multi-anchor constraint cannot require more branches than the user requested. Use diversity as a comparison criterion, not an impossible quota. A blocked first attempt can be followed by alternative retrieval or boundary-checking attempts at that unresolved point, but not by treating the missing premise as established. Record their dependence and stop the factual chain at the evidence gap.

Before a resource-intensive run, agree any requested time/search budget or use the host's available limits and report them. No arbitrary universal per-search budget is built into the original method. If a limit prevents five valid directions or the selected depth attempts, save a partial stage; do not silently shrink the contract or count a plan as completed research.

## Optional structural ledger

```sh
python3 scripts/run_state.py init --state runs/current/state.json \
  --question '<question>' --rounds 2 --agents 4 --top-n 4
python3 scripts/run_state.py decomp --state runs/current/state.json --input runs/current/decomposition.json
python3 scripts/run_state.py breadth --state runs/current/state.json --input runs/current/role2.json
# Submit roles 3–5 before selecting; IDs come from their actual outputs.
python3 scripts/run_state.py select --state runs/current/state.json --ids '<selected IDs>'
python3 scripts/run_state.py depth --state runs/current/state.json --input runs/current/depth-result.json
python3 scripts/run_state.py close --state runs/current/state.json
python3 scripts/audit_run.py --state runs/current/state.json --config runs/current/run-config.json
```

Commands do not invoke agents. Only the main agent writes state. The original engine requires three depth attempts and checks literal duplicates; it does not enforce role semantics, selection quality, genuine retrieval, re-interpretation or higher configured depth. The read-only audit detects some structural/evidence inconsistencies; it cannot validate scientific truth. Record selection rationales and execution evidence outside the engine's narrow schema as described in `OUTPUT_FORMAT.md`.
