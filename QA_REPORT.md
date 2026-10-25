# Noemorph — QA report

Status: **Interrupted by the user; release acceptance is incomplete.**

This report records work completed before the stop instruction on 2026-10-25. The user explicitly terminated the current test. No new retrieval, research-worker task, regression run or acceptance test was performed after that instruction. Existing artifacts were retained. This does not cancel the Noemorph project.

## 1. Result and release recommendation

Do not describe this revision as having passed final release acceptance. The live pilot has research-worker outputs and a main-agent selection, but final parent review, normalized ledger submission, round closure and the acceptance decision were not completed. See [the interruption record](audit/live-pilot/run-status.json).

The latest code changes have not all received a final regression run. This repository is an early release with incomplete acceptance, not an accepted stable release. After stopping tests, the user explicitly authorized completing the release package, sensitive-data/rights review and public GitHub publication without resuming verification. Packaging and publication therefore proceed independently of acceptance, with this incomplete status disclosed. CI is manual-only so publication does not restart tests. Publication progress is recorded below.

Apache-2.0 was selected by the user, who confirmed the right to license the original instructions and code. The official license text and a NOTICE are present. This confirmation does not license external publications, linked research data or third-party services.

## 2. Scope and original-version preservation

The existing project was inspected rather than replaced with a new research design. A 49-file snapshot of public source material was retained outside the candidate release. Its inventory is recorded in [audit/source-manifest.json](audit/source-manifest.json). Private earlier LLPS reports were excluded from the release candidate and the new research pilot.

Eleven protected source files have a hash lock. The original full skill is retained at [references/SOCRATES_SKILL.original.md](references/SOCRATES_SKILL.original.md); original references 01–08 and the research state engine are retained. The last completed upstream check passed for all 11 protected files. A final whole-tree comparison was not performed after the stop.

The original specialized entrypoint has five logical roles, but only roles 2–5 each submit five directions: **20 directions per round**. Historical generic references and the state engine's default instead describe five breadth submitters, yielding 25 directions. This discrepancy is documented in [the architecture](references/ARCHITECTURE.md). The maintained workflow explicitly uses four breadth submitters and preserves the specialized 20-direction behavior. The requested interpretation of five agents each supplying five directions has **not** been implemented; it requires a deliberate research-design decision.

## 3. Specification and executable checks completed before interruption

The [Agent Skills specification](https://agentskills.io/specification) was read. The release entrypoint uses `name: noemorph`, an English description of 509 characters, and `license: Apache-2.0`. The containing directory is `noemorph`. Long technical instructions were moved into linked references. Optional compatibility information was moved to the body because the bundled older Codex validator rejected that otherwise permitted metadata field.

| Command or actual operation | Recorded result | Boundary |
| --- | --- | --- |
| `python3 scripts/validate_skill.py` | Passed; 16 linked references resolved | Equivalent checker for this repository's plain scalar frontmatter subset; not a general YAML parser or the official `skills-ref` tool |
| Bundled skill-creator `scripts/quick_validate.py .` | `Skill is valid!` | Local bundled validator; not the official Agent Skills CLI |
| `python3 scripts/check_upstream.py` | Passed, 11 protected original files | Hash preservation, not semantic verification |
| `python3 -m unittest discover -s scripts -p test_run_state.py -v` | 6 tests passed | Original engine tests |
| `python3 -m unittest discover -s tests -p 'test_*.py' -v` | 35 tests passed in the last completed suite | A later card-handler regression test was added and has not been run in the final suite |
| `node --test tests/graph-core.test.cjs tests/languages.test.cjs` | 13 tests passed | Pure graph and language-bundle logic |
| `node --check plugins/knowledge-map/app.js` and `node --check plugins/knowledge-map/settings.js` | Passed at the recorded revision | Later small UI changes have no final syntax/regression run |
| `python3 scripts/build_demo.py` | Completed | Generates demo HTML and assets; not a research executor |
| `python3 scripts/release_scan.py` | Passed at the scanned revision | Pattern-based check only; final candidate has not been rescanned after every later change |
| `python3 scripts/publish.py --dry-run` | Completed with `executed: false` | No remote mutation or publication |

The last fully executed suites total **54 tests: 6 + 35 + 13**. This is a historical result, not a claim that the final working tree passed all tests. Test output from the original session remains in ignored local working artifacts. No official `skills-ref` validation, package reproducibility test or final clean-install acceptance was completed after interruption. Subsequent packaging guards are not a resumption of the stopped test suite.

The test suite actually exercises a two-round structural fixture: 40 breadth directions, two selected branches, six depth attempts, preservation of 38 unselected directions, and refusal to continue after the requested round limit. The fixture explicitly contains no researched evidence. It must not be represented as a successful two-round online research experiment.

Installation checks in the completed suite packaged a temporary skill, extracted it into a new directory, validated its entrypoint, checked protected sources, invoked the portable configuration prompt and moved that installation out of the discovery location as a reversible uninstall. Native discovery in Claude Code, Codex and Cursor was not exercised.

## 4. Functional acceptance

| Requirement | Evidence actually obtained | Assessment |
| --- | --- | --- |
| Understand the original question | Typed subject/predicate/condition/whole-question anchor, explicit ambiguity and scope records in the live pilot | Demonstrated on one question; not a general accuracy benchmark |
| Execute five roles | Five actual role-worker tasks; role 1 interpretation followed by four isolated breadth tasks, scheduled in batches | Role outputs exist; end-to-end acceptance was interrupted |
| Genuine concept transformations | Operator forward test and live outputs record what stays fixed, what changes, proposed class inclusion and bridge conditions | Transformations were attempted; several universal abstractions were rejected or remained conditional, so five established class inclusions per abstraction role were not demonstrated |
| Breadth before selection | Four live submissions with five directions each; main selection records receipt of all 20 first | Observed for one round; preserved source behavior is 20 rather than requested 25 |
| Main-agent selection | [selection.json](audit/live-pilot/selection.json) records scores, reasons, overlaps, rejected universal claims and one selected path | Explicit human-readable heuristic, not proof of optimal selection |
| Multiple deep rounds | Executable two-round structural fixture and offline recursive planning | Continuous multi-round **online** research remains unverified |
| Detect repetition, invalidity and weak evidence | Same-round literal duplicate rejection; cross-round repeat warnings in the read-only auditor; live records flag unjustified universal learning/group-agency claims and scope/transfer gaps | Exact/normalized duplicates are automated; semantic novelty, evidence entailment and scope still need agent review |
| Preserve user control | Round/path/depth configuration, optional scope, explicit-submit requirement, independent UI/content languages; a real card submission was saved correctly | Structural controls demonstrated; not every client has native cards or independent subagents |

### Offline prompt-following evaluation

[operator-forward-test.md](audit/operator-forward-test.md) records an isolated prompt evaluation with retrieval intentionally disabled. It produced 20 candidate questions, one provisional path, three conditional stages and a next-frontier plan. It performed **zero searches and completed zero research rounds**. Planning output is not completed research. This test exposed the single-path/diversity conflict, unsupported abstraction pressure, dependent blocked-hop handling and the need to distinguish attempts from discoveries. New maintained instructions address these issues; a fresh post-fix evaluation was not completed.

### Interrupted live research pilot

The fixture asks: “How do decentralized teams recover coordination after disruption?” Scope excludes employee surveillance and military command and requires non-coercive organizational coordination. It requests one round, one selected path and at least three depth attempts, with two workers at most concurrently.

Actual worker outputs include an interpretation, a frozen neutral anchor, 20 breadth directions, a recorded main-agent selection and one worker's three-step depth submission. The selected path examines whether a polycentric institutional representation is justified. Records preserve primary-source retrieval attempts, access failures, abstract-only evidence and unresolved transfer conditions. The final depth output does not establish complete recovery, non-coercive participation or a causal benefit of decentralization.

All listed research workers had completed when the stop instruction arrived. No research worker remained active. The parent had **not** finished reviewing the last depth output, submitting normalized records to the preserved state engine, closing the round or deciding end-to-end acceptance. The local preview server used for current testing was stopped. Consequently, the pilot is marked `stopped_by_user`, with `completed_run: false`.

Raw artifacts are retained under [audit/live-pilot](audit/live-pilot/run-status.json). They are evidence of partial execution, not a fully validated research report. No subsequent source-opening or fact-checking was performed after the stop.

## 5. Automatic activation simulation

An isolated evaluator read the skill metadata and classified 20 prompts. See [routing-evaluation.json](audit/routing-evaluation.json). Results: seven route to Noemorph, one needs clarification, twelve are ordinary questions or another workflow.

All five requested positive scenarios were identified: hidden scientific connections, going beyond the original question, overlooked interdisciplinary directions, generating questions from a hypothesis, and recursive knowledge exploration rather than a conventional review.

Negative scenarios included definitions, arithmetic, translation, summarization, finding a specific paper, Socratic teaching, ordinary software decomposition, causal appraisal, displaying an existing report, price comparison, fixing the viewer and asking what recursive research means. A bare “perform deep research” request was treated as ambiguous rather than automatically matching.

This is one metadata-routing simulation. It does not establish native client activation behavior, population-level precision/recall, or consistency across models. No such claims are made.

## 6. Competitive distinction

These are mechanism descriptions, not measured comparisons against a particular implementation.

| Method | Typical organizing operation | Noemorph's documented distinction |
| --- | --- | --- |
| Ordinary deep research | Retrieve and synthesize evidence around a question | Explicitly vary or abstract typed subject/predicate concepts before choosing branches; deep retrieval remains necessary |
| Socratic questioning | Clarify assumptions, definitions and reasoning through questions | Retains an interpretation role and adds four prescribed transformation roles plus breadth selection and evidence-linked recursion |
| Recursive problem decomposition | Split a problem into subproblems | Allows changes to the original framing and investigation of related objects/process classes rather than only constituent tasks |

The fixed/changed constraints, class-membership tests, source qualifiers, main-agent branch selection and traceable recursion are the intended distinctive mechanism. They do not ensure novelty, correct abstraction, interdisciplinary transfer or superiority. No controlled comparison, speed benchmark, external user evaluation or performance advantage was established.

## 7. Issues and safe repairs

Severity: P1 blocks the corresponding release claim; P2 limits reliability or portability; P3 concerns documentation or presentation.

| Issue | Severity | Action/status |
| --- | --- | --- |
| Specialized source produces 20 directions while other source material/request suggests 25 | P1 | Documented; actual 20-direction mechanism preserved. A claim of implemented 25-direction behavior fails acceptance |
| Final pilot review and final regression interrupted by user | P1 | Preserved artifacts, explicit stop status; final release acceptance remains incomplete |
| Initially no usable authenticated publishing route | P1 | CLI unavailable; later browser showed the authenticated 21sjhhs creation form. Publication progress is recorded in section 8 |
| Broken original entrypoint reference paths | P2 | Maintained entrypoint now links existing reference files; original archived source retained |
| Generic state-engine default conflicts with specialized roles | P2 | New workflow explicitly passes `--agents 4`; original engine untouched |
| Engine accepts supported labels without sources and does not enforce higher configured depth | P2 | Added read-only auditor and negative/positive tests; no claim of automatic semantic or source validation |
| Scope/control and sequential fallback insufficiently explicit | P2 | Added scope to portable card/config, explicit submission, batch/sequential disclosure and user-boundary instructions |
| New frontend token header differed from backend | P2 | Backend accepts Noemorph and legacy headers; actual browser roundtrip succeeded; added regression awaits final suite |
| One selected path conflicts with historical multi-anchor diversity rule | P2 | New instructions qualify diversity when the selected set can contain multiple branches |
| Abstract operators can generate unsupported universal membership claims | P2 | Require genuine inclusion/bridge tests and honest shortfalls; live evaluation still found rejected/conditional candidates |
| Single-language export lost independent interface preference | P2 | Config/UI preference retained in export; regression passed in completed suite |
| Native card/subagent APIs differ by client | P2 | Portable JSON/HTML/text fallbacks documented; single-context fallback is not advertised as cognitively independent |
| Camera animation could continue during content switch; badge pointerdown could begin pan | P3 | Small UI-only repairs made; final interaction regression not completed |
| Existing project lacked a confirmed license | P1, resolved | User chose Apache-2.0 and confirmed original-content rights; LICENSE and NOTICE added |
| Branding, install/use/uninstall and actual execution boundaries unclear | P3 | English/Chinese docs, architecture, operators, output contract and packaging/publishing helpers added |

No fixed scientific examples were added to the core operator prompts. No original research engine was replaced by a purported executable research automation. Helpers are described as ledger, validation, packaging and visualization tools.

## 8. Privacy, licensing and publication

Private earlier reports were not included. The explicitly authorized pre-publication pattern scans inspected 78 files, then 79 after adding the changelog; both found no credential or personal-path match. An additional literal password/API-key/client-secret/access-token assignment review returned no locations. The included PNG was visually reviewed: it contains the synthetic Noemorph demo, without private reports or account data. The package helper also applied the same scan to the 79-file candidate before archive creation; it passed. These are the authorized release guards, not resumed research or regression tests. This is not proof that arbitrary secrets or every copyright issue are absent. No real leaked credential was identified, so no rotation was performed. External papers are referenced rather than bundled or relicensed.

The GitHub connector reported identity `21sjhhs`; its lookup of `21sjhhs/noemorph` returned 404. The connector did not expose repository creation. GitHub CLI was not installed, relevant token environment variables were absent, the noninteractive credential helper did not provide usable credentials, and the browser reached the GitHub sign-in page. These observations do not mean the connector was logged out; they mean no usable creation-and-push route was established.

Public repository: [21sjhhs/noemorph](https://github.com/21sjhhs/noemorph). The authenticated browser created this new public repository under the user’s existing account. GitHub returned repository ID 1433158271 and admin/push permissions; a connector blob write succeeded. All 79 reviewed source/assets files were published to main in [commit e2eb808](https://github.com/21sjhhs/noemorph/commit/e2eb8083b921d44a748c5bb8615ce0f19643fae1). Description and nine Topics were saved. A local ZIP was built with 79 files using the package helper and its structural/sensitive-data guards; final archive delivery is separate from acceptance. No research or regression test was resumed. No unrelated remote was overwritten and no force push occurred. The local candidate now has its own Git repository on main, with origin set to this new repository. Its published history was fetched and synchronized without changing source files; the local pre-publication commit is retained under the local-pre-publication tag. Author identity uses the public GitHub noreply address rather than a private email. The original workspace remains separate and the pre-migration snapshot is retained. The CLI-only helper was not used for the actual publication because gh is unavailable. Actual publication used the logged-in browser for repository creation/metadata and the authenticated GitHub connector for blobs, tree, commit and a non-forced, expected-parent-checked main update. The reviewed helper is `scripts/publish.py`.

## 9. Unverified capabilities and pending work

- Final regression of the current working tree, archive reproducibility testing and fresh final installation acceptance. Sensitive-data review and packaging are separately authorized and do not imply test acceptance.
- Completed online pilot closure and online research across two or more rounds.
- Native automatic activation and card/delegation behavior in Codex, Claude Code, Cursor and other clients.
- Scientific novelty, broad semantic duplicate detection, citation entailment and transfer validity beyond the inspected examples.
- Five established new abstractions for every arbitrary input and the requested five-times-five breadth variant.
- Empirical competitive advantage or multi-model evaluation.
- Direct `file://` browser behavior: the test browser disallowed that navigation; HTTP preview and structural offline checks are distinct evidence.
- Final mouse/drag/zoom and language-switch interaction acceptance after the last small UI repairs. Browser automation coordinate limitations are not treated as proof of a product defect.
- Native client installation from the public remote remains untested. Publication progress is recorded in section 8.

Research and acceptance tests resume only when the user requests it. The later authorization covers packaging, sensitive-data/rights review and publication; it does not resume tests.
