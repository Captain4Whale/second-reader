# Eval-1 Window Dossier: The Value of Others

This page is the reviewer-facing drill-down for one Eval-1 Retry1 window. It is interpretation support, not a formal benchmark promotion or product-quality claim.

## Window Verdict

- Segment: `value_of_others_private_en__segment_1`
- Lane A selective note recall: `0.2979` over `94` note cases.
- Lane A labels: exact `10`, focused `18`, incidental `4`, miss `62`.
- Lane B Memory Quality: average `3.65` over `5` probes.
- Callback/FVI audit: visible `58`, grounded `11`, weak `9`, FVI `1`, local-only `37`.
- Interpretation boundary: Lane A recall, MQ score, and callback audit are separate evidence channels; do not collapse them into one product-quality score.

## Evidence Map

| Surface | Path |
| --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/summary/aggregate.json` |
| Lane A report | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/summary/report.md` |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases` |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/aggregate.json` |
| Lane B MQ results | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` |
| Lane B reaction audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/reaction_audit_results.jsonl` |
| Lane B output bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2` |

## Lane A: Selective Legibility

| Metric | Value |
| --- | ---: |
| note cases | 94 |
| exact match | 10 |
| focused hit | 18 |
| incidental cover | 4 |
| miss | 62 |
| unlocatable reactions | 1 |
| note recall | 0.2979 |

### Representative Note Cases

| Label | Case | Note / source target | Reaction evidence | Judge / reviewer reading |
| --- | --- | --- | --- | --- |
| `exact_match` | `e0126` | People want things from other people. | `rx:Full_Content:src:c1:p1@0-p4@516:discern:1`: The opening line is deliberately blunt. No softening, no qualification. It establishes the transactional premise as self-evident. | Visible reaction source span exactly matched the aligned note span. |
| `exact_match` | `e0129` | This is why people who want the same things are generally useless to each other: each lacks what the other desires . | `rx:Full_Content:src:c1:p5@0-p7@754:discern:3`: This tightens the transactional logic from the previous unit. Exchange works not despite divergence but because of it. The double meaning of 'want' makes this feel almost definitional rathe… | Visible reaction source span exactly matched the aligned note span. |
| `focused_hit` | `e0001` | People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have … | `rx:Full_Content:src:c1:p1@0-p4@516:discern:2`: The closing sentence lands harder than the symmetry that precedes it. This inverts the social norm of assumed goodwill and replaces it with a skeptical default. Worth tracking whether this … | The reaction's quoted span (the closing sentence about other people being a problem until they prove otherwise) captures the note's key insight and thesis. The reaction directly engages with this content, interpreting i… |
| `focused_hit` | `e0132` | why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, b… | `rx:Full_Content:src:c1:p8@0-p9@894:discern:5`: This is the most explicit moral inversion in the text so far. The author directly names and dismisses the intuitive moral reading — that goodness, love, or virtue would be the attractive qu… | The reaction's quoted span captures the central claim of the note—the moral inversion where neither goodness, love, nor virtue but functional desire drives relationships—and the reaction's analysis of the 'neither...nor… |
| `incidental_cover` | `e0151` | At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek myth… | `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`: This is the direct answer to the value-examination promised at paragraph 26. Not a metaphor or analogy — the definition of value itself is scarcity-derived. It connects back to the irrevers… | The reaction's quoted span captures only the first sentence about scarcity creating value while omitting the Greek mythology example that serves as the note's key illustrative support. Although the reaction's commentary… |
| `miss` | `e0127` | People typically don’t join together because they want the same things. | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0128` | Keep in mind that to want has a double meaning: it can mean both to desire and to lack. | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0130` | In most cases, people come together because they want different things. | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |

### Miss-Mode Reading

- `no_source_overlap_candidate`: 62 cases. Example: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0127`. No visible reaction was admitted by strict `segment_source_v1` source-span overlap, so the note could not be credited even if the broader theme appeared nearby.

### Unlocatable Diagnostics

- `rx:Chapter_1:src:c1:p78@176-p78@176:retrospect:1`

These reactions were diagnostic only. They were not counted as matches, candidates, or recall credit.

## Lane B: Memory Quality

| Probe | Position | Score | Probe focus | What memory retained | Gap / judge concern |
| ---: | --- | ---: | --- | --- | --- |
| 1 | near 20% | 4.00 | three approaches to other people; prosocial vs antisocial framing | The snapshot retains strong material including the governing thesis ('relationships are media in which value is transacted'), the refined definition of unequal good… | the structural signal 'three approaches to other people' (move against, move away, move toward) is absent from all digest fields—this is the organizing framework the source e… |
| 2 | near 35% | 3.75 | sexual relationship definition; mating and dating as a game | The snapshot retains all three probe-targeted structural signals in substantial form: (1) the sexual relationship definition ('necessary and sufficient element of a… | the economic model synthesis is present only as concept entries ('epistemic-opacity-of-valuation') without a coherent thread connecting all three signals together, and the be… |
| 3 | near 60% | 4.00 | covert calculator model; subjective and fluctuating value | The snapshot strongly retains the three probe-targeted structural signals: the covert calculator model (value coefficient concept with provisional values/weights/ag… | this is a sub-component rather than a central structural feature. |
| 4 | near 75% | 3.50 | goal-relative human value; problem-of-living inference | The snapshot retains core material including the transactional relationships thesis, the goal-relative value frame (plumber/cardiology analogy, value coefficient, g… | the 'problem-of-living inference' framing ('What problem of living are they attempting to solve?') is not explicitly retained as a named inferential structure, though its con… |
| 5 | window end | 3.00 | goal conflation; desire, disgust, conflict, and red flags | The snapshot retains strong coverage of the book's foundational framework (relationships as value-transaction media, comparable-value exchange, the covert calculato… | 'goal conflation' — explicitly named as one of the two major complicators in the source — has no dedicated active_item or concept entry, despite being a significant structura… |

## Lane B: Callback / FVI Audit

Definitions for this page: grounded callback means a visible reaction correctly reconnects to earlier visible material; weak callback means it gestures at prior material but is loose or underspecified; FVI means the reaction visibly integrates earlier material in a way judged false or unsupported; local-only means no callback claim is made.

### Grounded Callback Examples

- `rx:Full_Content:src:c1:p11@0-p11@916:discern:9`: The unconscious-valuation point extends the earlier exclusion of non-transactable gifts. If people don't fully know their own valuations, even 'spontaneous' generosity or liking may be driven by processes belo… Judge reason: Explicitly references 'earlier exclusion of non-transactable gifts' from reaction 7, extending that concept to the unconscious-valuation point.
- `rx:Full_Content:src:c1:p14@0-p15@559:discern:12`: This adds a crucial layer to the transactional model — not just that value is exchanged, but that the exchange must be hidden. Relationships work partly because the negotiation itself stays invisible. This ext… Judge reason: Explicitly extends from the 'beneath awareness' point (referencing reaction 9's unconscious-valuation discussion) and adds the concept of socially forbidden explicit negotiation.
- `rx:Full_Content:src:c1:p16@0-p16@1015:discern:13`: This is a clean two-boundary theorem for relationship formation. Too symmetric (identical goods) → no transaction. Too asymmetric (disparate values) → relationship probability decreases. Only the narrow middle… Judge reason: Explicitly extends the 'unequal goods of comparable value' definition from reaction 10, applying it as a generative condition with named failure modes.

### Weak Callback Examples

- `rx:Full_Content:src:c1:p13@0-p13@543:discern:11`: This closes the paragraph as a clean structural rule, completing the thought that began with the unequal-subjective premise. It extends the transactional model from mechanism (what is exchanged) into form (how… Judge reason: Uses vague phrase 'unequal-subjective premise' that doesn't clearly map to any specific earlier visible reaction, making the linkage partial and unsupported.
- `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`: This is the direct answer to the value-examination promised at paragraph 26. Not a metaphor or analogy — the definition of value itself is scarcity-derived. It connects back to the irreversibility claim in par… Judge reason: References the internal text structure ('promised at paragraph 26,' 'irreversibility claim in paragraph 28') and a general connection to the 'reversibility test' in reaction 22, b…
- `rx:Full_Content:src:c1:p34@0-p35@1132:discern:30`: The scale claim is striking — not that valuation is complex, but that it is continuous and parallel. This reframes value determination from a discrete decision event to a constant computational flood. It makes… Judge reason: Vaguely references 'opaque' and 'beneath awareness' concepts that appear to derive from earlier visible material (reaction 12's 'hidden negotiation,' reaction 24's 'beneath the su…

### False Visible Integration Examples

- `rx:Full_Content:src:c1:p19@0-p19@794:retrospect:18`: This is the core concession of the book so far — a direct acknowledgment that the framework's rigor comes at the cost of practical specificity. Principles that survive contact with individual variation become too thin t… Why FVI: The compat_type is 'retrospect' and prior_link points to 'active_attention:nested-game-structure', but no earlier visible reaction in this window contains that specific ref_id or explicitly surfaces …

## Reviewer Takeaway

- Lane A is weak in this window: misses dominate despite some exact/focused evidence.
- Lane B memory state is relatively coherent for this diagnostic suite, with omissions concentrated around specific structural signals rather than wholesale loss.
- Callback counts are audit evidence, not proof that visible reactions are product-quality callbacks.
