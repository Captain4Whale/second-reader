# Eval-1: Full Active Evaluation Post-Slice8H - Interpretation Report v0

## Reviewer Summary

Eval-1 Retry1 completed the full active post-Slice8H `attentional_v2` evaluation scope: Lane A ran all 5 active Local/User-level Selective Legibility windows with 202 note cases, and Lane B ran all 5 active Long Span semantic-probe windows with 25 Memory Quality probes plus fresh Callback/FVI audit.

What it supports: `attentional_v2` is evaluation-operational on the current active dataset boundary. The run produced health-checked reading outputs, strict user-level source-span matching, fresh Memory Quality judging, and fresh visible-reaction audit evidence across all active windows.

What it does not support: this is not product-quality proof, not a cross-mechanism conclusion, not an evidence-catalog update, and not a Long Span vNext formal-authority promotion. Treat it as completed evaluation evidence awaiting human review.

Recommendation: accept Eval-1 as completed evaluation evidence after review; consider a separate catalog-entry brief only after reviewers agree the interpretation and caveats are adequate. Keep Long Span vNext diagnostic unless a later formal-authority brief explicitly promotes it.

## Run Evidence Map

Primary post-run report:

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/Eval1-Full-Active-Evaluation-Post-Slice8H-Retry1-High-Parallel-Post-run-Report v0.md`

Detailed reviewer dossier:

- `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/eval1-full-active-evaluation-post-slice8h-dossier/README.md`
- Window pages: `docs/implementation/new-reading-mechanism/second-reader-memory-planning/codex/reports/eval1-full-active-evaluation-post-slice8h-dossier/windows/*.md`
- The dossier is the probe/case-level audit layer for human review; this main report intentionally stays at aggregate interpretation and navigation level.

Operational index:

- Parent ledger entry: `eval1_full_active_post_slice8h_retry1_20260519`
- Run-ledger status: `review_pending`
- Catalog status: `review_pending` / not cataloged
- Aggregation note: all totals below are report-level aggregation across 10 completed shard runs, not a runner-emitted merged root summary.

Scope boundaries:

| Boundary | Eval-1 value |
| --- | --- |
| Mechanism | `attentional_v2` only |
| Lane A dataset | `state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422` |
| Lane A manifest | `eval/manifests/splits/attentional_v2_user_level_selective_v1_draft.json` |
| Lane B probe plan | `eval/manifests/probes/memory_quality_semantic_probe_plan_20260504.json` |
| Probe selection | `semantic_boundary_with_distance_reference` |
| Historical surfaces | not run |
| `iterator_v1` | not run |
| Evidence catalog | not updated |

Run/job map:

| Lane | Slug | Run id | Job id | Status |
| --- | --- | --- | --- | --- |
| B | `huochu` | `attentional_v2_eval1_long_span_post_slice8h_20260519_huochu` | `bgjob_eval1_long_span_post_slice8h_20260519_huochu` | completed |
| B | `mangge` | `attentional_v2_eval1_long_span_post_slice8h_20260519_mangge` | `bgjob_eval1_long_span_post_slice8h_20260519_mangge` | completed |
| B | `nawaer` | `attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer` | `bgjob_eval1_long_span_post_slice8h_20260519_nawaer` | completed |
| B | `value_of_others` | `attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others` | `bgjob_eval1_long_span_post_slice8h_20260519_value_of_others` | completed |
| B | `xidaduo` | `attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo` | `bgjob_eval1_long_span_post_slice8h_20260519_xidaduo` | completed |
| A | `huochu` | `attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_huochu` | completed |
| A | `mangge` | `attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_mangge` | completed |
| A | `nawaer` | `attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_nawaer` | completed |
| A | `value_of_others` | `attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_value_of_others` | completed |
| A | `xidaduo` | `attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo` | `bgjob_eval1_user_level_post_slice8h_20260519_reuse_xidaduo` | completed |

Raw artifact pattern:

- Lane A shard dirs: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_<slug>`
- Lane B shard dirs: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_<slug>`
- Each shard contains `summary/aggregate.json`, `summary/report.md`, and `summary/llm_usage.json`; Lane B also contains `summary/memory_quality_results.jsonl`, `summary/reaction_audit_results.jsonl`, `summary/reaction_window_summaries.jsonl`, and sourcing metadata.

## Lane A: Local/User-Level Selective Legibility

Lane A asks a strict question: did a visible `attentional_v2` reaction recover a user-selected note span under `segment_source_v1` source-span overlap? Exact matches and focused hits count toward recall. Incidental cover is useful supporting evidence but does not count. Unlocatable reactions are diagnostics only.

### Aggregate Result

| Window | Note cases | Exact | Focused hit | Incidental | Miss | Recall | Unlocatable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `huochu` | 40 | 7 | 8 | 2 | 23 | 0.3750 | 1 |
| `mangge` | 25 | 2 | 7 | 0 | 16 | 0.3600 | 0 |
| `nawaer` | 23 | 8 | 2 | 2 | 11 | 0.4348 | 1 |
| `value_of_others` | 94 | 10 | 18 | 4 | 62 | 0.2979 | 1 |
| `xidaduo` | 20 | 1 | 7 | 0 | 12 | 0.4000 | 0 |
| **Total** | **202** | **28** | **42** | **8** | **124** | **0.3465** | **3** |

Prior comparison caveat: the April 19 formal run used the `20260416` repaired package and reported `attentional_v2 note_recall=0.3498`. Eval-1 uses the active `20260422` package and reports `0.3465`. That is continuity under a newer dataset boundary, not a direct regression/improvement claim.

### Window Interpretation

| Window | Reviewer interpretation |
| --- | --- |
| `huochu` | Strong examples show the mechanism can recover psychologically central notes when the visible reaction lands on the same span. Misses still cluster around compact meaning-therapy aphorisms and survival-art observations where no candidate reaction overlapped the note span. |
| `mangge` | Exact matches are sparse, but focused hits show useful alignment on investment discipline, salesmanship, and decision logic. The dominant issue is visible reaction placement, not judge leniency. |
| `nawaer` | Best recall in Lane A. The mechanism cleanly recovered several wealth-building principles such as equity, specific knowledge, and productizing yourself, but incidental cases show partial coverage of multi-clause notes. |
| `value_of_others` | Lowest recall and largest sample. Many user notes are short conceptual claims; visible reactions often captured nearby framework logic but did not land on enough note spans to satisfy strict recall. |
| `xidaduo` | Recall is mostly focused hits rather than exact matches, suggesting interpretive legibility is present but canonical span precision is uneven. |

### Representative Exact / Focused Hits

| Artifact | Label | Evidence chain | Interpretation |
| --- | --- | --- | --- |
| `huochu...e0002` | exact | Note target: courage lost when prisoners smoke. Best reaction: `rx:Full_Content:src:c1:p10@265-p14@155:discern:14`. Judge reason: exact aligned span. | This is the cleanest selective-legibility path: the visible reaction lands on the identical canonical span and interprets the note's core claim. |
| `huochu...e0004` | focused | Note target: second-stage numbness as a protective shell. Best reaction: `rx:Full_Content:src:c1:p58@0-p61@87:highlight:34`. Judge reason: focused interpretation of the protective-shell clause. | The candidate covers a narrower subspan, but it captures the essential concept, so the judge counts it toward recall. |
| `mangge...e0002` | exact | Note target: learning humility through failure. Best reaction: `rx:Full_Content:src:c1:p77@0-p81@23:discern:37`. Judge reason: exact aligned span. | The mechanism can recover short conclusion-like notes when the reaction locator is precise. |
| `nawaer...e0004` | exact | Note target: renting time cannot create wealth; equity is required. Best reaction: `rx:Full_Content:src:c1:p14@0-p15@41:highlight:7`. Judge reason: exact aligned span. | This is a high-value exact match on a central user-note principle, not merely a thematic overlap. |
| `xidaduo...e0004` | focused | Note target: Siddhartha waiting/thinking/fasting and sinking like a stone. Best reaction: `rx:Full_Content:src:c1:p270@0-p274@232:highlight:101`. Judge reason: reaction contains the note and directly interprets the stone metaphor. | The label is focused rather than exact because the reaction span is broader, but the analysis addresses the note's core. |

### Representative Misses

| Artifact | Label | Evidence chain | Interpretation |
| --- | --- | --- | --- |
| `huochu...e0012` | miss | Note target: humor as a survival art. Judge reason: `no_candidate_source_span_overlap`. | The failure is coverage: no visible reaction entered the strict source-overlap candidate set. |
| `huochu...e0028` | miss | Note target: Spinoza quote about understanding painful passion. Judge reason: `no_candidate_source_span_overlap`. | A strong meaning-therapy line can still be missed if no visible reaction anchors the selected span. |
| `mangge...e0004` | miss | Note target: waiting five years until a transaction is understood. Judge reason: `no_candidate_source_span_overlap`. | The mechanism may understand investment patience broadly, but this note span did not receive candidate coverage. |
| `nawaer...e0003` | miss | Note target: wealth vs. money vs. status. Judge reason: `no_candidate_source_span_overlap`. | This is important because Lane B also found the wealth/money/status structure missing in Memory Quality probe 1. |
| `xidaduo...e0007` | miss | Note target: Siddhartha's worldly play and deliberate gullibility. Judge reason: `no_candidate_source_span_overlap`. | This aligns with Lane B's later weakness on integrating the worldly-life collapse arc. |

### Incidental Cover Examples

| Artifact | Label | Evidence chain | Why it did not count |
| --- | --- | --- | --- |
| `huochu...e0014` | incidental | Reaction `rx:Full_Content:src:c1:p132@0-p132@173:retrospect:83` analyzed the sheep metaphor. | The note's main point was practical survival through crowd-positioning; the reaction covered only the literary image. |
| `nawaer...e0002` | incidental | Reaction `rx:Full_Content:src:c1:p1@0-p3@215:highlight:2` covered the "what / who / when" wealth elements. | The note also emphasized understanding over hard work and choosing the right method; the reaction covered only part of that structure. |
| `value_of_others...e0463` | incidental | Reaction `rx:Full_Content:src:c1:p27@0-p28@512:discern:25` covered non-recoverability of expended resources. | The note's resource taxonomy was broader than the final non-refund clause the reaction interpreted. |

### Miss Modes

| Miss mode | Evidence | Reviewer interpretation |
| --- | --- | --- |
| No visible reaction near note span | Many misses report `no_candidate_source_span_overlap`. | This is the dominant Lane A pressure: the reader often does not emit a visible reaction on the user-selected span. |
| Candidate covers only a subclaim | Incidental examples in `huochu`, `nawaer`, and `value_of_others`. | The mechanism can notice something real while failing to recover the user's note-level proposition. |
| Reaction broader than note but useful | Focused hits such as `xidaduo...e0004`. | Broader spans can count only when the judge finds the note's core content directly addressed. |
| Important concept missed locally and in memory | `nawaer...e0003` and Lane B `nawaer` probe 1 both flag wealth/money/status weakness. | Cross-lane agreement strengthens this as a concrete follow-up area. |
| Source locator unusable | 3 unlocatable diagnostics. | Slice 8D prevented locator gaps from aborting the run, but unlocatable reactions still cannot become matches. |

Unlocatable diagnostics, not counted as matches:

| Window | Reaction id |
| --- | --- |
| `huochu` | `rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1` |
| `nawaer` | `rx:Chapter_1:src:c1:p99@193-p99@193:retrospect:1` |
| `value_of_others` | `rx:Chapter_1:src:c1:p78@176-p78@176:retrospect:1` |

## Lane B: Long Span MQ / Callback / FVI

Lane B asks two different questions. Memory Quality asks whether the probe-time memory snapshot retained important structure at semantic-probe boundaries. Callback/FVI asks whether visible reactions correctly integrate earlier visible material. These are related, but they are not interchangeable.

### Aggregate Result

| Window | MQ avg | Probes | Visible reactions | Grounded callbacks | Weak callbacks | FVI | Local only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `huochu` | 3.70 | 5 | 150 | 19 | 9 | 0 | 122 |
| `mangge` | 3.10 | 5 | 270 | 43 | 13 | 0 | 214 |
| `nawaer` | 3.65 | 5 | 40 | 6 | 4 | 1 | 29 |
| `value_of_others` | 3.65 | 5 | 58 | 11 | 9 | 1 | 37 |
| `xidaduo` | 3.00 | 5 | 211 | 47 | 25 | 0 | 139 |
| **Total** | **3.42** | **25** | **729** | **126** | **60** | **2** | **541** |

Source policy:

- Memory Quality source: `fresh_judge`
- Reaction audit source: `fresh_judge`
- Reading jobs: 5 fresh Lane B producer tasks
- Fresh reaction-audit judging: yes
- LLM health: all producer traces had `error_count=0` and `fallback_count=0`

### Per-Window Interpretation

| Window | Interpretation |
| --- | --- |
| `huochu` | Strongest Memory Quality after `nawaer`/`value_of_others` tie, with good retention of suffering-to-inner-freedom structures. Weakness: final release/liberation architecture remains fragmented rather than fully organized. |
| `mangge` | Starts strong on Wesco structure and management trust, then weakens around S&L causal mechanics and the shift from crisis diagnosis to investing doctrine. The mechanism retains many facts but under-organizes the cross-year thesis. |
| `nawaer` | Very strong around the "productize yourself" synthesis, including a perfect probe 4. Weakness: foundational wealth/money/status and specific-knowledge structures are not always preserved as standalone concepts. |
| `value_of_others` | Good conceptual retention of relationship-as-transaction, value coefficient, and emotion-as-valuation. Weaknesses concentrate around goal conflation, exemplar selection, and some organizing frames introduced early or late. |
| `xidaduo` | The main long-span pressure point. Early spiritual-dissatisfaction material is retained, but later worldly collapse, river rebirth, fatherhood, and final unity are often isolated in recent reactions rather than integrated into active memory. |

### Per-Probe Memory Quality Summary

| Window | Probe | Score | What memory did well | What memory missed |
| --- | ---: | ---: | --- | --- |
| `huochu` | 1 | 3.50 | Retained first/second-stage prisoner-response concepts and emotional death. | Did not preserve all three stages as an explicit organizing framework. |
| `huochu` | 2 | 4.25 | Strongly retained the wife/love spiritual-resource sequence. | Under-retained the natural-beauty/sunset sequence as part of the same inner-life movement. |
| `huochu` | 3 | 3.25 | Retained the escape-refusal episode and responsibility to the dying comrade. | Treated the active choice not to flee more as plot than moral reversal. |
| `huochu` | 4 | 3.75 | Captured hope, bodily resistance, Nietzsche, and Spinoza signals. | Organization was useful but still modest. |
| `huochu` | 5 | 3.75 | Retained main psychological themes and end reactions. | Did not organize terminal liberation/disillusionment into a full ending framework. |
| `mangge` | 1 | 4.00 | Retained Wesco structure, acquisition discipline, management trust, and valuation discipline. | Minor flattening of contextual details. |
| `mangge` | 2 | 3.25 | Preserved asset posture and disclosure boundaries. | Anti-forecasting and cash-optionality argument remained fragmented. |
| `mangge` | 3 | 2.25 | Retained some S&L crisis observations. | Missed the detailed causal chain from deregulated incentives to moral-hazard gambling. |
| `mangge` | 4 | 2.75 | Retained 1990 S&L recap and regulator exhaustion. | Missed the transition from crisis diagnosis to investing doctrine. |
| `mangge` | 5 | 3.25 | Preserved concrete investment items and citations. | Under-represented the larger "conditions overpower people" thesis and S&L appendix structure. |
| `nawaer` | 1 | 3.25 | Retained equity ownership and leverage-point observation. | Missed wealth / money / status as a clear three-way foundation. |
| `nawaer` | 2 | 3.50 | Retained compounding, equity wealth, sales/build pairing, and partner integrity. | Did not preserve specific knowledge as a standalone organized definition. |
| `nawaer` | 3 | 3.25 | Retained individual leverage concepts and permissioned/permissionless contrast. | Did not unify capital/labor/code/media into one leverage taxonomy. |
| `nawaer` | 4 | 5.00 | Captured "productize yourself" with full fidelity and clean organization. | Minimal limitations in the judge rationale. |
| `nawaer` | 5 | 3.25 | Retained several accurately sourced wealth-building items. | Missed the chapter-level organizing synthesis. |
| `value_of_others` | 1 | 4.00 | Retained relationships as value transactions and valuation opacity. | Missed the three approaches to other people as the opening frame. |
| `value_of_others` | 2 | 3.75 | Retained sexual relationship definition, game frame, and perceived best options. | Economic model synthesis was siloed rather than integrated. |
| `value_of_others` | 3 | 4.00 | Strongly retained covert calculator, subjective value, and emotion as valuation output. | Minor gap on comparative ranking function. |
| `value_of_others` | 4 | 3.50 | Retained transactional relationship thesis and goal-relative value. | Missed exemplar-based selection and the "problem of living" inference as named structures. |
| `value_of_others` | 5 | 3.00 | Retained foundational framework and some late desire/disgust/conflict material. | Missed goal conflation and red-flag material as major structures. |
| `xidaduo` | 1 | 3.50 | Retained dissatisfaction, ascetic self-denial, and failure of self-erasure. | Captured conclusion better than experiential journey. |
| `xidaduo` | 2 | 4.00 | Retained the three departure structures and self-experience over doctrine. | Declared coverage reached later material, but retained content still skewed early. |
| `xidaduo` | 3 | 2.75 | Retained early Part One material and isolated recent reactions. | Failed to integrate worldly-life collapse and river rebirth. |
| `xidaduo` | 4 | 2.25 | Retained some recent reactions around Kamala, river, and child. | Did not consolidate fatherhood, Kamala's death, or Vasudeva/river listening. |
| `xidaduo` | 5 | 2.50 | Captured final river/unity material in recent reactions. | Active memory remained anchored to the opening and missed the final integration arc. |

### Callback / FVI Category Meanings

| Category | Meaning |
| --- | --- |
| Grounded callback | The visible reaction connects to earlier visible material with enough textual or explicit prior-link support. |
| Weak callback | The reaction gestures at earlier material, but the link is loose, theme-level, or insufficiently anchored. |
| False visible integration | The reaction claims a prior integration that the visible evidence surface does not support. |
| Local-only visible reaction | The reaction may be useful locally but does not claim or require a callback. |

### Callback / FVI Examples

| Category | Artifact | Evidence chain | Reviewer interpretation |
| --- | --- | --- | --- |
| Grounded | `huochu` reaction `rx:Full_Content:src:c1:p9@0-p9@206:retrospect:10` | Prior link to reaction 8; reason says it correctly connects earlier "another number" analysis to betrayal/personality instrumentalization. | A clear visible callback: the reaction names a prior visible idea and advances it with textual support. |
| Grounded | `nawaer` reaction `rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13` | Prior link to reaction 10; reason accepts the closure between untrainability and unschoolability of specific knowledge. | Good example of structural callback across a conceptual sequence. |
| Grounded | `xidaduo` reaction `rx:Full_Content:src:c1:p36@0-p40@9:retrospect:14` | Prior link to reaction 13; reason accepts that "estranged" builds on the father watching the son's vigil. | Good narrative callback: it links a later emotional state to an earlier visible scene. |
| Weak | `huochu` reaction `rx:Full_Content:src:c1:p71@0-p75@102:discern:42` | Reason says the repeated "happy to be useful" inversion is only theme-level and lacks precise anchoring. | Plausible but under-specified; useful for interpretation, not strong callback evidence. |
| Weak | `mangge` reaction `rx:Full_Content:src:c1:p18@0-p19@88:discern:5` | Reason says it contrasts with an earlier anti-forecasting claim but lacks a concrete text location. | This is the classic weak-callback shape: thematically plausible, evidentially thin. |
| Weak | `value_of_others` reaction `rx:Full_Content:src:c1:p13@0-p13@543:discern:11` | Reason says "unequal-subjective premise" does not map clearly to a specific earlier visible reaction. | A concept label cannot substitute for a traceable prior visible anchor. |
| FVI | `nawaer` reaction `rx:Full_Content:src:c1:p85@0-p88@72:retrospect:33` | Reason says the claimed earlier quote about becoming wealthy and realizing it was not the original pursuit was not visible in the window. | The reaction overfits a thematic thread into a visible callback claim. |
| FVI | `value_of_others` reaction `rx:Full_Content:src:c1:p19@0-p19@794:retrospect:18` | Reason says the `active_attention:nested-game-structure` prior link points outside the visible evidence surface. | The reaction may be thematically meaningful, but the audit correctly rejects it as visible integration evidence. |

## Cross-Lane Synthesis

Eval-1 suggests that `attentional_v2` is more evaluation-ready and operationally stable after Slice 8H, especially after the LLM-health repair and source-locator compatibility work. The mechanism can now be examined across both active lanes without fallback-backed outputs or aborted locator failures.

The result is mixed but useful. Lane B shows moderate long-span memory quality, with strong pockets where the text has a clear conceptual synthesis (`nawaer` probe 4, `value_of_others` probe 3, `huochu` probe 2). Lane A remains stricter and lower because it asks a different question: whether the reader emits a visible reaction on the user's chosen source span. A mechanism can remember a theme and still miss a user note.

The most actionable cross-lane signals:

- `nawaer` wealth/money/status appears as both a Lane A miss and a Lane B early structural omission.
- `xidaduo` later-book integration is weak in Lane B and also has Lane A misses around worldly-life scenes.
- `value_of_others` has many visible reactions but the lowest Lane A recall, suggesting reaction presence does not guarantee selective user-note legibility.
- `mangge` shows many callbacks but lower MQ around causal S&L structures, suggesting callback frequency and memory organization diverge.

Do not conflate:

- selective note recall with Memory Quality
- visible reaction presence with callback correctness
- SourceRef / anchor counts with fidelity
- audit existence with product quality
- diagnostic evidence with formal authority

## Known Limitations

- `attentional_v2` only; no `iterator_v1` comparison.
- No historical/discontinued benchmark surfaces ran.
- No Reader Reaction Value / Insight and Clarification addendum ran.
- No evidence catalog update has been made for Eval-1.
- Report-level aggregation across shards, not a runner-emitted merged root summary.
- Dataset-boundary difference vs. prior formal local/user-level evidence.
- Long Span vNext remains diagnostic pending a separate formal-authority decision.
- This report intentionally includes representative examples, not exhaustive case-by-case commentary for all 202 Lane A note cases and 729 Lane B visible reactions.

## Recommendations

1. Accept Eval-1 Retry1 as completed evaluation evidence after human review.
2. Create a separate evidence-catalog update brief if reviewers agree the evidence should be cataloged.
3. Keep Long Span vNext diagnostic unless a formal-authority brief defines the promotion criteria.
4. Consider a Reader Reaction Value / Insight and Clarification addendum later; do not retrofit it into Eval-1.
5. No immediate runtime patch is indicated by this interpretation alone.
6. No immediate eval-runner patch is indicated by this interpretation alone.
7. If the next mechanism-improvement slice is opened, prioritize cross-lane confirmed weak spots: source-span reaction coverage for short user notes, `nawaer` wealth taxonomy retention, `xidaduo` late-arc integration, and `mangge` S&L causal-chain organization.

## Evidence Appendix

### Lane A Artifact Pattern

For each Lane A shard:

- `summary/aggregate.json`: window label counts and recall
- `summary/report.md`: runner summary
- `summary/llm_usage.json`: judge usage
- `note_cases/*.json`: individual case evidence, including note span, best reaction, judge label/reason, and locator diagnostics

Example path:

- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002.json`

### Lane B Artifact Pattern

For each Lane B shard:

- `summary/aggregate.json`: MQ and reaction-audit aggregate
- `summary/memory_quality_results.jsonl`: per-probe MQ scores and judge reasons
- `summary/reaction_audit_results.jsonl`: per-reaction callback/FVI labels and reasons
- `summary/reaction_window_summaries.jsonl`: per-window reaction totals
- `meta/output_sourcing.json`: fresh/reused output policy
- `summary/llm_usage.json`: judge usage

Example path:

- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl`

### Guardrails

- No eval was run to create this interpretation report.
- No background jobs were launched.
- No runtime mechanism code was changed.
- No eval runners or judge prompts were changed.
- `reading-companion-backend/docs/evaluation/evidence_catalog.md` and `reading-companion-backend/docs/evaluation/evidence_catalog.json` were not updated.
- Long Span vNext was not promoted to formal benchmark authority.
- This report makes no product-quality claim.
