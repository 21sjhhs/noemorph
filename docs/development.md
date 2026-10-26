# Development and preservation

Read `references/ARCHITECTURE.md` before changing research semantics. `upstream.lock.json` records the research baseline, including `references/01–08`, the structural state utility, its six tests, and `references/NOEMORPH_SKILL.baseline.md`. Branding maintenance on 2026-10-26 updated the archive name/text and the state utility's temporary-file prefix, with prior hashes retained in the lock. `scripts/check_upstream.py` checks that recorded baseline; it does not assert that these two files are unchanged from their earlier versions.

The source tree remains outside this publication directory, with a separate local rollback snapshot. No private run, personal filesystem path, user report, credential or screenshot of private research belongs in this repository.

## Modules

- Research behavior: `SKILL.md`, `references/ARCHITECTURE.md`, `EXPLORATION_OPERATORS.md`, `WORKFLOW.md`, `OUTPUT_FORMAT.md` and the directly referenced original logic/selection/depth/evidence/report files.
- `run_state.py`: original structural engine; explicitly use four breadth submitters. `audit_run.py` adds read-only checks without modifying its behavior.
- `graph-core.js`: pure graph validation, visibility, search and layout. `app.js`: SVG, pan/zoom, inspection and export.
- `i18n.js`: UI strings only. `languages.js` / `graph_languages.py`: structure protection, declared language variants and source fingerprint. Browser APIs use the `Noemorph` namespace.
- `settings.js` / `run_card.py`: matching JS/Python configuration contract, optional scope, independent UI/content languages, portable cards and loopback return. Configurations use `noemorph-run-config/1.0`. Retired schema/header aliases and browser preference fallbacks were removed; update older configuration identifiers before reuse.
- `knowledge_map.py`: read-only adapters and standalone export. It never invents a missing hop or upgrades evidence because a branch was selected.
- `serve.py`: loopback static preview; rejects symlinks escaping its directory. `run_card.py serve` is a separate one-shot configuration receiver.
- `validate_skill.py`, `release_scan.py`, `package_skill.py`, `publish.py`: bounded validation/scanning, reproducible archive, and explicit GitHub CLI publication. No global installation or key extraction.

## Checks

Run these checks from the repository root:

```sh
python3 scripts/validate_skill.py
python3 scripts/check_upstream.py
python3 -m unittest discover -s scripts -p 'test_run_state.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/graph-core.test.cjs tests/languages.test.cjs
node --check plugins/knowledge-map/app.js
node --check plugins/knowledge-map/settings.js
python3 scripts/release_scan.py
```

Run `python3 scripts/build_demo.py` after changing UI assets so standalone HTML and the bundled example remain current. If demo research text changes, update the complete translated copy before binding it; never call a stale copy a translated new source. Demo data is not an end-to-end research benchmark.

Build a local installable archive with `python3 scripts/package_skill.py --output dist/noemorph.zip`. Development tests also require Node.js 18+. See `scripts/publish.py --help` for the optional GitHub CLI publication helper.

The equivalent specification checker is deliberately limited to the flat plain-string YAML used here; the official `skills-ref` validator or a full YAML parser is needed to validate other frontmatter forms. Common secret patterns are scanned with redacted output. That scan cannot prove arbitrary secrets or copyrighted text are absent; review new assets and data as well.

Native client discovery, independent model behavior, online source support and performance require separate integration/behavioral tests. A two-round synthetic ledger run proves stage/round handling, not recursive scientific discovery. Report only completed checks in `QA_REPORT.md`.


Viewer browser regression is optional and requires Playwright plus local Chrome: `node tests/viewer.browser.cjs [standalone.html] [screenshot.png]`. It exercises wheel batching, zoom boundaries, overlays, resize, content-language switching and the mandatory English setting. Private fixtures/screenshots belong outside the release tree.
