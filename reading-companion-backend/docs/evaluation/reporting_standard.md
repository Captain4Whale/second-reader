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
- judge score dimensions and judge reason
- a clear statement that probe-time snapshot is scoring evidence
- a clear statement that final runtime dump is for learning/debugging and cannot replace probe-time evidence

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
