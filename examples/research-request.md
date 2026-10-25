# Example input and process record

This is an input/output-format example, not a completed research result. The synthetic HTML graph is a separate UI demonstration. Neither belongs in a fresh research worker's context.

## Input

> Use Noemorph to explore my hypothesis. Run two rounds, choose one deep path each round, and keep the other findings. Ask me for the actual hypothesis and any excluded scope before beginning.

The agent first collects the actual hypothesis, scope, rounds, concurrency/depth preferences and content languages. It does not replace the missing hypothesis with a favorite scientific example.

## Expected process

Interpret the supplied question; freeze a neutral anchor. Four transformation roles independently investigate five questions each. Main agent compares all 20, records duplicate or invalid candidates, selects one and preserves the other 19. Investigate successive questions for at least three attempts; update the frontier from actual findings and repeat once. Stop after round two. With no external retrieval, mark this as a prompt-only plan and do not claim evidence or finished research.

## Minimal direction shape

```json
{
  "id": "R1-A3-1",
  "question": "Does a different subject class satisfy the same operational predicate under the same conditions?",
  "anchor_ids": ["S", "P", "C"],
  "logical_move": "subject_substitution",
  "fixed": ["predicate definition", "conditions"],
  "changed": ["subject class"],
  "discovery_target": "An alternative class, not a predetermined answer",
  "search_route": "Search the operational properties and necessary conditions",
  "bridge_test": "Compare predicate measurements and applicability conditions",
  "novelty_reason": "Changes the subject class rather than its name",
  "finding": "Pending actual investigation",
  "evidence_refs": [],
  "status": "unresolved",
  "unknowns": ["Whether a candidate class exists and is comparable"]
}
```

This record is a placeholder example, never a verified finding. See `references/OUTPUT_FORMAT.md` for synthesis, catalogue, coverage and graph requirements. The optional state engine accepts the direction's required structural fields but does not prove its logical move was executed.
