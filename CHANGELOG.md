# Changelog

## Unreleased

- Coalesce wheel zoom updates per animation frame, normalize wheel units, support map overlays, and retain zoom when the viewport resizes.
- Require English in final graph deliveries, validate complete requested language versions, and distinguish incomplete source previews from completed output.
- Extend translation checks to node/edge prose, protect reference URLs and evidence codes, preserve saved graph views, and add explicit Skill language-delivery review requirements.

- Lead both READMEs with the project promise, use cases, example request, map preview, and quick start.
- Add `llms.txt` and clearer project metadata for readers and retrieval tools.
- Use Noemorph names throughout documentation, browser APIs, configuration, and generated examples.
- Remove retired configuration/header aliases and browser preference fallbacks. Older configurations must use `noemorph-run-config/1.0`; earlier browser preferences reset to current defaults.
- Rename the archived entrypoint to `references/NOEMORPH_SKILL.baseline.md` and explicitly record branding-only baseline updates without changing research operators or state transitions.

## Initial public source release

- Rename the maintained Noemorph project to Noemorph with bilingual installation and usage documentation.
- Preserve the original five logical roles, typed transformations, breadth selection, recursive frontier and research state engine.
- Document the original 20-versus-25-direction discrepancy rather than changing research semantics silently.
- Include the offline HTML graph viewer, multilingual graph contract and portable parameter card.
- Add explicit execution boundaries, read-only audit, source provenance, package and publication helpers.
- License original project code and instructions under Apache-2.0 with the rights holder’s confirmation.

Acceptance remains incomplete: the user stopped the live research pilot and subsequent testing, then explicitly requested packaging and publication using the existing results. Historical passing checks are documented in QA_REPORT.md. No new regression or research test was run after the stop. GitHub checks are manual only.
