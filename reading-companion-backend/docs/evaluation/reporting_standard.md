# Evaluation Reporting Standard

Purpose: define the reviewer-facing writing standard for important evaluation reports and evidence audits.
Use when: writing, reviewing, or regenerating human-readable evaluation interpretation reports.
Not for: changing metrics, judge prompts, runtime behavior, evidence-catalog status, or raw eval artifacts.
Update when: the expected report shape, evidence chain, or reviewer workflow changes.

## Why This Standard Exists

Important eval reports should let a human reviewer move through one clear path:

`answer -> metrics -> window/case evidence -> raw artifacts`

A good report is not just a score dump. It is a navigable reviewer dossier: it starts with the answer, keeps caveats visible, names what the evidence supports, and then gives enough concrete examples that the reviewer can independently inspect the underlying artifacts.

This standard generalizes the best parts of the April 25 Long Span Phase-1 evidence pack, especially the later `memory_quality_probe_audit_20260503_source_map` layout. That pack was valuable because it connected aggregate results to per-window and per-probe evidence; it was hard to use because entrypoints and appendices accumulated organically. New reports should keep the evidence depth while making the navigation cleaner.

## Required Four-Layer Shape

### 1. Reviewer Summary

Start with the answer.

Include:

- what ran and what completed
- what the result supports
- what the result does not support
- catalog/readiness recommendation
- no product-quality or formal-authority claim unless separately approved

### 2. Run Evidence Map

Give the reviewer a map before analysis.

Include:

- run ids, job ids, dates, and status
- dataset / manifest / probe-plan boundaries
- raw run directories
- required summary paths
- related post-run / interpretation reports
- run-ledger and evidence-catalog status
- explicit note if aggregation is report-level across shards rather than a runner-emitted merged root summary

### 3. Lane / Window Analysis

Explain the result at the level where behavior actually differs.

Include:

- per-lane aggregate tables
- per-window tables and short narrative interpretation
- representative examples for each important label or score bucket
- recurring strengths and failure modes
- where judge decisions were strict rather than automatic
- how the findings should and should not be compared to prior evidence

### 4. Evidence Appendix

End with raw-evidence pointers and concrete examples.

Include:

- artifact paths for each lane/window
- note-case, probe, or reaction ids for examples
- source span or note text snippets when useful
- visible reaction / memory-state evidence
- judge label and short reason
- runtime context links when relevant

## Book-Window Playback Dossier

Important evals should also provide a reviewer-facing playback dossier when the run is meant to expose product behavior, not only metric outcomes.

The playback dossier answers: what did the reader visibly do while reading this exact source window?

Required shape:

- `Source Window`: link to the dataset-stable source window, including covered chapters, paragraph ids, note-target markers, and probe markers.
- `Reading Timeline`: list every visible reaction in reading order, with source-span excerpt, reaction text, SourceRef / paragraph-char coordinate, and only the relevant eval annotations.
- `Probe Memory Checkpoints`: for each Memory Quality probe, show source orientation, capture point, probe-time scoring evidence fields, judge scores, and judge reason.
- `Scoring Interpretation`: explain how the reaction timeline and probe checkpoints produce the lane scores.
- `Manual Review Guide`: tell reviewers which raw artifacts to open and which fields to inspect when they disagree with a label or score.

Storage rules:

- Dataset-stable source windows should live near the dataset package, not in a run-specific report directory.
- Run-specific playback dossiers should live with the human-readable eval report for that run.
- The playback dossier is not a new metric, not evidence-catalog promotion, and not product-quality proof.

Field display rules:

- Keep reaction entries conditional rather than template-heavy. If a reaction has no Selective Legibility target, say so once; do not emit an empty note block.
- If a reaction is local-only, say it is local-only; do not emit empty callback/FVI fields.
- If a reaction overlaps a Selective Legibility note target, include the note-case id, target note text, target source span, label, source-span relation, judge reason, and whether it counted toward recall.
- If a reaction is a grounded callback, weak callback, or FVI, include prior-link evidence when present, judge reason, and a short reviewer interpretation.
- Memory state should use the artifact's real field names and values. Preserve the recorded probe-time fields such as `active_attention_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, and `source_ref_digest`; show empty arrays, empty objects, and `null` values explicitly rather than silently omitting them.
- Do not present derived projection fields such as `active_focus_digest` as peer memory stores. If a report needs them for prompt/context-packaging diagnosis, put them in a clearly labeled projection appendix rather than the main Memory Quality state evidence.
- Distinguish probe-time scoring evidence from final runtime state references. A probe snapshot digest is the evidence the judge saw; final `runtime/*.json` files are useful diagnostic references, but they cannot be used as substitutes for complete probe-time stores.
- If the run does not contain per-probe full-store snapshots, state that boundary explicitly. Future reports that need complete probe-time stores should require exporter artifacts such as `exports/probe_state_snapshots/probe_###/active_attention.json` rather than inferring backward from final runtime state.
- Do not default-display `continuity_context`, `recent_reading_orientation`, `recent_sentence_ids`, `recent_meaning_units`, or `recent_reactions` as Memory Quality state. These are continuity/projection artifacts, not durable memory stores; include them only in a clearly labeled continuity-diagnostics section when that is the review target.
- Recent visible reactions should appear in the reading timeline or callback/FVI evidence when relevant, not inside a synthetic memory-state wrapper.
- Do not present `target_sentence_id`, `target sentence`, or `cN-sM` handles by themselves as canonical source coordinates. Label them as orientation-only or legacy/eval locator metadata, and pair them with paragraph-char `SourceRef` / source-span coordinates whenever those are available.
- Do not use `rough_position_target`, `distribution_reference_label`, or labels such as `near 20%` as the primary Memory Quality probe heading. Headings should foreground the semantic boundary and source coordinate; distance labels are secondary distribution-reference metadata.

## Cross-Surface Rules

- Every score or label used as evidence should have at least one explanation path back to a concrete case, probe, or reaction.
- Representative examples should identify the artifact, the source/note/reaction evidence, the judge label, and the reviewer interpretation.
- Keep caveats near the claim they qualify; do not bury them in the final section.
- Separate metric results from mechanism quality. A metric can be valid evidence without proving product quality.
- Separate visible reaction presence from callback correctness.
- Separate SourceRef or anchor counts from fidelity.
- Separate audit existence from product quality.
- Separate diagnostic evidence from formal benchmark authority.

## Long Span / Memory Quality Reports

Long Span Memory Quality evidence should follow the source-map model.

Required:

- one full source document per window
- inline probe markers in that source document
- probe sections with short deterministic orientation excerpts, not repeated full source-so-far dumps
- raw probe snapshot links
- final runtime state links, clearly labeled as final references rather than probe-time scoring evidence
- judge score dimensions and judge reason
- a clear statement that probe-time snapshot is scoring evidence
- a clear statement that final runtime dump is for learning/debugging and cannot replace probe-time evidence
- a clear statement when complete per-probe memory-store dumps are unavailable

The narrower Long Span Memory Quality contract lives in [long_span/memory_quality_report_contract.md](./long_span/memory_quality_report_contract.md).

## Local / User-Level Reports

Local/User-level Selective Legibility reports should provide a comparable evidence chain.

Required:

- per-window note-case counts and label counts
- exact / focused / incidental / miss examples
- all unlocatable diagnostics, with explicit note that they are not matches
- miss-mode analysis grounded in note-case artifacts
- confirmation that strict source-span overlap remains the candidate gate
- confirmation that text similarity and semantic similarity are not candidate-admission paths unless a future accepted method changes that contract

## Report Quality Bar

A report meets the bar when a reviewer can answer these questions without archaeology:

- What did we run?
- Where are the raw artifacts?
- What are the headline results?
- Which concrete examples justify those results?
- What failed or remained weak?
- Which claims are explicitly not authorized?
- What is the next human decision?
