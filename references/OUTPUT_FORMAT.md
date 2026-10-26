# Output contract

Deliver the source records as well as a readable synthesis. Data from examples is demonstration-only and must never become evidence or a cold-start anchor.

## Run directory

```text
run-config.json        User choices and scope; no credentials
decomposition.json     Whole question, typed concepts, relations and ambiguity
execution.json         Actual host mode, role/task identities and retrieval capability
state.json             Optional v4 structural ledger, maintained by main agent
breadth.jsonl          All original directions, including failed/unselected ones
selection.jsonl        Reasons, criteria, duplicates, exclusions and shortfalls
depth.jsonl            Every selected branch and each successive attempt
report.md              Synthesis answering the original question with qualifications
catalogue.md           All directions, findings, evidence, unresolved questions and IDs
coverage.json          Direction ID → report/catalogue/map locations or exclusion reason
graph.json             Frozen source graph; independent from view and translation
graph.<language>.json  Full translated copies with meta.language and source binding
knowledge-map.html     Standalone interactive map; attachments remain separate files
knowledge-map.bundle.json  All language versions and optional saved view
```

These filenames are a convention; the original engine has no automatic `execution` or `coverage` generator. The host agent writes those records from actual tool results, not invented logs. The viewer can consume the v4 state directly or a graph conforming to `docs/graph-format.md`.

## Required research records

Each breadth direction has a stable ID, round, originating role/executor, original question, anchors, fixed/changed variables, logical operation, discovery target, search route, bridge test, novelty reason, finding, evidence and unknowns. A complete round preserves 4 × 5 directions. Interpretation is separately recorded.

Selection records retain all candidates and distinguish duplicates, invalid questions, unselected useful findings and rejected claims. Record Boundary, Depth, Bridge, Evidence, Nonredundancy, Risk and set-level diversity; heuristic scores are not objective measurements.

Each depth path records executor, direction ID, at least the configured number of successive attempts, question, finding, `why_next`, typed relation, evidence references/status, new concepts, boundary change, limits and unresolved gaps. A failed attempt counts as an attempt, not as a discovery.

Use evidence states `verified_direct`, `supported_with_limits`, `inferred`, `unresolved`, `contradicted`. Supporting references must identify what they support. Record source-access failures separately. No software check proves a cited source supports a claim.

## Final synthesis and map

Follow preserved `references/07-report.md`: synthesis, complete map, full catalogue. Account for every breadth ID, including unselected valuable findings; maintain an ID-to-output coverage map. “Selected” allocates further research, not permission to retain knowledge.

Keep typed bridge relations and limits. Separate established findings from inferred links and open questions. State actual completed rounds, execution mode and missing capabilities. Show all branches in the complete graph, prioritize major nodes initially, and keep per-node source/file jump buttons.

The UI's Chinese/English controls change interface text. Content language selects an existing graph version or follows the interface. Translation happens only after the source graph is frozen and uses actual independent translation workers when possible. Language tags, fingerprint checks and structure protection prevent attaching a translation to the wrong source; they do not prove translation accuracy. See `references/11-language-variants.md` for the executable binding/export commands.

English is mandatory for every final graph delivery, together with the other requested content languages. Before claiming completion, apply the final language-delivery gate in `references/11-language-variants.md`; an incomplete-language preview is not a completed delivery.
