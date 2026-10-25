# Development and preservation

Read `references/ARCHITECTURE.md` before changing research semantics. The migration preserves original `references/01–08`, `scripts/run_state.py`, its six tests, and the original entrypoint snapshot. `upstream.lock.json` points its entrypoint record to `references/SOCRATES_SKILL.original.md`. `scripts/check_upstream.py` verifies preserved bytes; it does not assert that the renamed entrypoint is unchanged.

The source tree remains outside this publication directory, with a separate local rollback snapshot. No private run, personal filesystem path, user report, credential or screenshot of private research belongs in this repository.

## Modules

- Research behavior: `SKILL.md`, `references/ARCHITECTURE.md`, `EXPLORATION_OPERATORS.md`, `WORKFLOW.md`, `OUTPUT_FORMAT.md` and the directly referenced original logic/selection/depth/evidence/report files.
- `run_state.py`: original structural engine; explicitly use four breadth submitters. `audit_run.py` adds read-only checks without modifying its behavior.
- `graph-core.js`: pure graph validation, visibility, search and layout. `app.js`: SVG, pan/zoom, inspection and export.
- `i18n.js`: UI strings only. `languages.js` / `graph_languages.py`: structure protection, declared language variants and source fingerprint. Namespaced JavaScript APIs retain legacy names for compatibility.
- `settings.js` / `run_card.py`: matching JS/Python configuration contract, optional scope, independent UI/content languages, portable cards and loopback return. New configurations use `noemorph-run-config/1.0`; legacy Socrates configurations normalize on input.
- `knowledge_map.py`: read-only adapters and standalone export. It never invents a missing hop or upgrades evidence because a branch was selected.
- `serve.py`: loopback static preview; rejects symlinks escaping its directory. `run_card.py serve` is a separate one-shot configuration receiver.
- `validate_skill.py`, `release_scan.py`, `package_skill.py`, `publish.py`: bounded validation/scanning, reproducible archive, and explicit GitHub CLI publication. No global installation or key extraction.

## Checks

Run the Python/Node commands from the README. Run `python3 scripts/build_demo.py` after changing UI assets so standalone HTML and the bundled example remain current. If demo research text changes, update the complete translated copy before binding it; never call a stale copy a translated new source. Demo data is not an end-to-end research benchmark.

The equivalent specification checker is deliberately limited to the flat plain-string YAML used here; the official `skills-ref` validator or a full YAML parser is needed to validate other frontmatter forms. Common secret patterns are scanned with redacted output. That scan cannot prove arbitrary secrets or copyrighted text are absent; review new assets and data as well.

Native client discovery, independent model behavior, online source support and performance require separate integration/behavioral tests. A two-round synthetic ledger run proves stage/round handling, not recursive scientific discovery. Report only completed checks in `QA_REPORT.md`.
