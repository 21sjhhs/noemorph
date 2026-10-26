# Exploration operators and delegation

This document preserves the five specialized Noemorph roles. Use abstract structures inferred from the current user question. Do not seed a scientific example, discipline list, named theory, expected conclusion or an earlier demo into core prompts.

## Shared input

The immutable breadth input contains the user's exact question, whole concept `X`, typed subject `S`, predicate/process `P`, relations `R`, conditions `C`, ambiguities, scope/exclusions, neutral anchor IDs and previous-round frontier. The main agent may revise the anchor after evidence review, not selectively for one sibling role. No same-round sibling discoveries are supplied before breadth closes.

| Role | Fixed / changed | What counts as a real transformation | Failure to reject |
| --- | --- | --- | --- |
| 1. Interpretation | Preserve whole question and explicit qualifiers | Distinguish object/process, observation/explanation, definition/evidence, candidate meanings and hidden arguments | Inventing the user's desired answer or collapsing ambiguity |
| 2. Predicate expansion | Hold `S` and declared `C` fixed; vary `P → P′` | Another phenomenon, relation, outcome or neighboring process of the same subject, with a new search path | Renaming `P`; silently replacing the subject |
| 3. Subject substitution | Hold `P`, its operational definition and conditions fixed; vary `S → S′` | A different subject class that could participate in the same process; compare necessary conditions and exclusions | Renaming the same subject; changing both subject and process without disclosure |
| 4. Predicate abstraction | Lift `P → G_P` through a stated inclusion relation | A superordinate process/relation with sibling subtypes, explicit invariants and applicability limits | An elegant synonym or unsupported universal mechanism |
| 5. Subject abstraction | Lift `S → G_S` through a stated type/class relation | A broader class/theoretical object structure whose properties can be examined and mapped back | Replacing an instance by a vague label with no new consequences |

Formal patterns are open queries, not facts: `P(S,C)?`; `P′(S,C)?`; `P(S′,C)?`; `SubtypeOf(P,G_P)?`; `InstanceOf(S,G_S)?`. Type-lifts require justification. Shared mathematical form does not establish shared physical cause.

## Role prompts

Interpretation: “Clarify the original question using only the supplied neutral decomposition. Preserve the whole concept and qualifiers. Give a revisable working explanation, definitions, ambiguity and boundaries. Do not enumerate the later transformation roles' answers.”

Breadth template: “You are the {operator} role. Read only the immutable shared anchor, prior-round frontier and your operator definition. Independently propose and investigate exactly five semantically different directions. For each, record what stays fixed, what changes, `logical_move`, anchors, discovery target, repeatable search route, bridge test, novelty reason, finding, sources and unknowns. Use the current question rather than a fixed domain example. Do not read sibling submissions. A synonym is not a new direction. Report failed retrieval; never invent sources.”

Depth template: “Investigate selected direction {id} with its explicit bridge and initial evidence. Perform at least {depth_hops} consecutive research attempts: locate a concept, trace its conditions/theory/structure, then remap or extend from the previous finding. Explain each next question, relation, source support and limit. Record unresolved or contradicted attempts honestly. Do not manufacture a complete chain.”

Each delegated output includes its actual executor identity and execution mode. These templates are instructions for the host agent, not executable Python behavior.

A type-lift is a hypothesis until justified. If five valid directions cannot be found within the available scope and resources, report the shortfall and keep the stage incomplete; do not invent five classifications to meet a count. The main agent may request correction or another actual worker. Completing a planning exercise is never completing a research round.

## Novelty and validity review

Before selection, compare question meaning, fixed variables, changed variables, anchor coverage, search route and bridge test. Link equivalent directions by IDs; preserve both original records. Exact-text deduplication is only a lower bound. Reject or return circular questions, synonyms, unsupported type-lifts, impossible scopes and disguised preselected answers for correction. A candidate without verified evidence can remain an open direction, but cannot be promoted to an established result.
