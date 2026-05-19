# Eval-1 Window Audit Dossier: The Value of Others

This page is a reviewer audit dossier for one Eval-1 Retry1 window. It is evidence interpretation only: no eval was run to produce this page, no catalog entry is created here, and no product-quality or formal-authority claim is made.

## Window Verdict

The Value of Others is weak on Lane A selective legibility: most human note cases were not recovered by strict visible-reaction overlap. Lane B memory is comparatively healthy at MQ 3.65, with the main review work concentrated on structural omissions rather than total loss. Callback audit records 11 grounded and 9 weak callbacks, with 1 FVI; these are callback-quality diagnostics, not proof of product-level reading quality.

| Channel | Result | Reviewer boundary |
| --- | --- | --- |
| Lane A selective legibility | recall `0.2979` over `94` note cases | exact/focused count toward recall; incidental and miss do not |
| Lane B Memory Quality | average `3.65` over `5` probes | evaluates state retention/organization, not visible reaction quality |
| Callback/FVI | grounded `11`, weak `9`, FVI `1` | visible callback correctness is separate from memory quality |

## Window-Specific Reading

- Lane A pattern: `28` of `94` note cases received recall credit, while `62` remained misses. The dominant miss mode below should be read as a candidate-admission / visible-reaction coverage issue, not as proof that the mechanism understood nothing about those notes.
- Lane B strongest probe: probe `1` at `near 20%` scored `4` because The snapshot retains strong material including the governing thesis ('relationships are media in which value is transacted'), the refined definition of unequal goods of comparable value, the epistemic opacity of valuation, the covert transaction norm, and the…
- Lane B weakest probe: probe `5` at `window end` scored `3`; main reviewer concern: 'goal conflation' — explicitly named as one of the two major complicators in the source — has no dedicated active_item or concept entry, despite being a significant structural pivot. The 'red flags' material is present only in the probe metadata, not as a ret…
- Callback/FVI pattern: this window has `1` FVI, so reviewer should inspect the FVI section before treating callback counts as encouraging.

## Evidence Map

| Evidence | Path | What to inspect |
| --- | --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/summary/aggregate.json` (`present`) | label counts, recall, unlocatable diagnostics |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases` (`present`) | per-note source targets, candidates, judge labels |
| Lane A rebuilt bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/rebuilt_bundles/value_of_others_private_en__segment_1/attentional_v2/normalized_eval_bundle.json` (`present`) | normalized visible reactions used for matching |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/aggregate.json` (`present`) | MQ and callback totals |
| Lane B MQ rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` (`present`) | probe scores and judge reasons |
| Lane B reaction audit rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/reaction_audit_results.jsonl` (`present`) | grounded/weak/FVI/local-only labels |
| Probe snapshots | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` (`present`) | probe-time state evidence; primary MQ audit source |
| Normalized eval bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json` (`present`) | visible reactions and memory summaries |
| Runtime state | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime` (`present`) | final run state; useful for diagnosis, not a substitute for probe-time snapshots |

## Lane A Selective Legibility Audit

Lane A asks whether visible reactions recover user-selected note spans under strict `segment_source_v1` source-span overlap. Text similarity and semantic similarity are not candidate-admission paths.

| Label | Count | Reviewer interpretation |
| --- | ---: | --- |
| `exact_match` | 10 | exact: the reaction span is identical to the aligned note span, so it is credited without semantic judging. |
| `focused_hit` | 18 | focused: the admitted span overlaps the note target and judge says the reaction captures the note-level meaning closely enough for recall credit. |
| `incidental_cover` | 4 | incidental: the reaction touches the note span but its attention is elsewhere; useful as support, not recall credit. |
| `miss` | 62 | miss: no credit; either no strict source-overlap candidate existed or admitted candidates did not satisfy focused recall. |
| `unlocatable diagnostic` | 1 | recorded as locator evidence only; never credited as candidate/match/recall |

### Case-Level Evidence

#### `e0126` — `exact_match`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0126`
- source target: p4@0-37: People want things from other people.
- matched reaction: `rx:Full_Content:src:c1:p1@0-p4@516:discern:1`
- reaction text: The opening line is deliberately blunt. No softening, no qualification. It establishes the transactional premise as self-evident.
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0126.json`

#### `e0129` — `exact_match`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0129`
- source target: p7@639-754: This is why people who want the same things are generally useless to each other: each lacks what the other desires.
- matched reaction: `rx:Full_Content:src:c1:p5@0-p7@754:discern:3`
- reaction text: This tightens the transactional logic from the previous unit. Exchange works not despite divergence but because of it. The double meaning of 'want' makes this feel almost definitional rather than empirical — a structural necessity, not a contingent social fact.
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0129.json`

#### `e0001` — `focused_hit`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0001`
- source target: p4@0-516: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to gi…
- matched reaction: `rx:Full_Content:src:c1:p1@0-p4@516:discern:2`
- reaction text: The closing sentence lands harder than the symmetry that precedes it. This inverts the social norm of assumed goodwill and replaces it with a skeptical default. Worth tracking whether this framing holds or gets complicated as the book develops.
- source-span relation: `note_contains_candidate; coverage=0.12`
- judge / runner reason: The reaction's quoted span (the closing sentence about other people being a problem until they prove otherwise) captures the note's key insight and thesis. The reaction directly engages with this content, interpreting it as an 'inversion of social norm of assumed goodwill' and considering its broader implications for …
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0001.json`

#### `e0132` — `focused_hit`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0132`
- source target: p8@505-717: why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things fr…
- matched reaction: `rx:Full_Content:src:c1:p8@0-p9@894:discern:5`
- reaction text: This is the most explicit moral inversion in the text so far. The author directly names and dismisses the intuitive moral reading — that goodness, love, or virtue would be the attractive qualities — and replaces it with pure functional desire. The sentence structure (neither...nor...nor...but) perf…
- source-span relation: `note_contains_candidate; coverage=0.63`
- judge / runner reason: The reaction's quoted span captures the central claim of the note—the moral inversion where neither goodness, love, nor virtue but functional desire drives relationships—and the reaction's analysis of the 'neither...nor...nor...but' structural rejection directly engages with the note's core argument. While the reactio…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0132.json`

#### `e0151` — `incidental_cover`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0151`
- source target: p29@325-565: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarc…
- matched reaction: `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`
- reaction text: This is the direct answer to the value-examination promised at paragraph 26. Not a metaphor or analogy — the definition of value itself is scarcity-derived. It connects back to the irreversibility claim in paragraph 28: since resources cannot be refunded, scarcity is structural, not incidental.
- source-span relation: `note_contains_candidate; coverage=0.51`
- judge / runner reason: The reaction's quoted span captures only the first sentence about scarcity creating value while omitting the Greek mythology example that serves as the note's key illustrative support. Although the reaction's commentary is focused on the scarcity-value connection, the intentional exclusion of the mythological elaborat…
- Reviewer reading: this is not recall success. The mechanism touched nearby or overlapping text but did not make the human-note idea its main object.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0151.json`

#### `e0127` — `miss`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0127`
- source target: p7@367-438: People typically don’t join together because they want the same things.
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0127.json`

#### `e0128` — `miss`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0128`
- source target: p7@551-638: Keep in mind that to want has a double meaning: it can mean both to desire and to lack.
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0128.json`

#### `e0130` — `miss`

- note case id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0130`
- source target: p8@0-71: In most cases, people come together because they want different things.
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0130.json`

### Miss-Mode Aggregation

- `no_source_overlap_candidate`: 62. No visible reaction entered the candidate set under strict source-span overlap. Do not infer a hidden semantic hit from thematic proximity.

### Unlocatable Source-Locator Diagnostics

- `rx:Chapter_1:src:c1:p78@176-p78@176:retrospect:1`

These diagnostics are intentionally not counted as matches. They identify reactions whose source location could not be turned into a usable `segment_source_v1` candidate for Lane A matching.

## Lane B Memory Quality Audit

Lane B asks whether probe-time memory state retains salient, source-faithful, organized understanding at five semantic-probe checkpoints. Final runtime dumps can help diagnose, but probe-time snapshots remain the scoring evidence.

| Probe | Position | Overall | Salience | Mainline | Organization | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | near 20% | 4 | 4 | 4 | 4 | 4 |
| 2 | near 35% | 3.75 | 4 | 4 | 3 | 4 |
| 3 | near 60% | 4 | 4 | 4 | 4 | 4 |
| 4 | near 75% | 3.5 | 3 | 4 | 3 | 4 |
| 5 | window end | 3 | 3 | 3 | 3 | 3 |

### Probe 1 — near 20%

#### Probe Position And Question

- target / captured: `c1-s90` -> `c1-s90`
- boundary kind: `early argument-block closure`
- why this probe point: Closes the opening relationship-as-value-transaction frame before the argument turns more explicitly toward mating and dating.
- structural signals to check:
  - three approaches to other people
  - prosocial vs antisocial framing
  - relationships as games and value transactions

#### Source Orientation

- capture-neighborhood excerpt: And they have to go about doing this without violating – or, more realistically, selectively violating – various inter-… / If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidental… / Every type of relationship constitutes a different game – as does every s…
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 4 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 0 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `transactional-relationships-framing`: Relationships as value-transaction media: this is the governing frame introduced at the outset. Source: `src:c1:p3@0-p3@56`: RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED
- `default-skepticism-default`: Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions. Source: `src:c1:p4@452-p4@516`: other people are typically a problem until they prove otherwise.
- `comparable-value-exchange`: the media in which unequal goods of comparable value are exchanged Source: `src:c1:p12@464-p12@530`: the media in which unequal goods of comparable value are exchanged
- `epistemic-opacity-of-valuation`: this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exis… Source: `src:c1:p11@0-p11@916`: this valuation typically occurs beneath the threshold of awareness. This means that neither party c…

#### What The Mechanism Retained

- The snapshot retains strong material including the governing thesis ('relationships are media in which value is transacted'), the refined definition of unequal goods of comparable value, the epistemic opacity of valuation, the covert transaction norm, and the game-theoretic exit condition (stop playing when payoff is insufficient).

#### What It Missed Or Distorted

- the structural signal 'three approaches to other people' (move against, move away, move toward) is absent from all digest fields—this is the organizing framework the source explicitly introduces at the outset to structure the prosocial/antisocial distinction. The 'prosocial vs antisocial framing' is only partially captured (the prosocial concept is stored b…

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `4`, fidelity `4`, overall `4`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains strong material including the governing thesis ('relationships are media in which value is transacted'), the refined definition of unequal goods of comparable value, the epistemic opacity of valuation, the covert transaction norm, and the game-theoretic exit condition (stop playing when payoff is insufficient). However, the structural signal 'three approaches to other people' (move against, move…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` filtered by `probe_index=1`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[0]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 2 — near 35%

#### Probe Position And Question

- target / captured: `c1-s136` -> `c1-s136`
- boundary kind: `section pivot`
- why this probe point: Captures the pivot into sexual relationships and the economic model of mating/dating before the calculator model expands.
- structural signals to check:
  - sexual relationship definition
  - mating and dating as a game
  - perceived best options and economic modeling

#### Source Orientation

- capture-neighborhood excerpt: And since the model can explain emotions (but emotions cannot explain the model), this means that the model is more fun… / To understand why this is the case, we need to take a closer look at the concept of value: what it is and how it operat… / The covert calculator⁠4
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 1 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `transactional-relationships-framing`: Relationships as value-transaction media: this is the governing frame introduced at the outset. Source: `src:c1:p3@0-p3@56`: RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED
- `default-skepticism-default`: Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions. Source: `src:c1:p4@452-p4@516`: other people are typically a problem until they prove otherwise.
- `comparable-value-exchange`: the media in which unequal goods of comparable value are exchanged Source: `src:c1:p12@464-p12@530`: the media in which unequal goods of comparable value are exchanged
- `epistemic-opacity-of-valuation`: this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exis… Source: `src:c1:p11@0-p11@916`: this valuation typically occurs beneath the threshold of awareness. This means that neither party c…
- `perception-vs-actuality-mechanism`: then the perception of value must be the mechanism that lies at the heart of sexual relationships. Source: `src:c1:p23@565-p23@663`: then the perception of value must be the mechanism that lies at the heart of sexual relationships.

#### What The Mechanism Retained

- The snapshot retains all three probe-targeted structural signals in substantial form: (1) the sexual relationship definition ('necessary and sufficient element of a sexual relationship is the presence of sex'), (2) mating and dating as a game with rules/laws, and (3) perceived best options as the governing law plus the economic/behavioral economics framing.…

#### What It Missed Or Distorted

- the economic model synthesis is present only as concept entries ('epistemic-opacity-of-valuation') without a coherent thread connecting all three signals together, and the behavioral economics label/framework is present in the source but not prominently surfaced in the digest threads. The nested game structure from paragraph 18 is retained but shows a fallb…

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `3`, fidelity `4`, overall `3.75`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains all three probe-targeted structural signals in substantial form: (1) the sexual relationship definition ('necessary and sufficient element of a sexual relationship is the presence of sex'), (2) mating and dating as a game with rules/laws, and (3) perceived best options as the governing law plus the economic/behavioral economics framing. The 'perceived best options' thread is correctly captured a…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` filtered by `probe_index=2`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[1]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 3 — near 60%

#### Probe Position And Question

- target / captured: `c1-s243` -> `c1-s247`
- boundary kind: `section closure`
- why this probe point: Closes the covert-calculator section, giving a strong checkpoint for subjective value and emotion-as-valuation.
- structural signals to check:
  - covert calculator model
  - subjective and fluctuating value
  - emotion as valuation output

#### Source Orientation

- capture-neighborhood excerpt: It’s unsettling because we would prefer not to think that some people are more valuable than others, and it’s contentio… / However, we can largely avoid both issues by remembering that value is always assessed in relation to a personally rele… / For instance, a plumber is neither inherently more nor less valuable than…
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 1 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `transactional-relationships-framing`: Relationships as value-transaction media: this is the governing frame introduced at the outset. Source: `src:c1:p3@0-p3@56`: RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED
- `default-skepticism-default`: Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions. Source: `src:c1:p4@452-p4@516`: other people are typically a problem until they prove otherwise.
- `comparable-value-exchange`: the media in which unequal goods of comparable value are exchanged Source: `src:c1:p12@464-p12@530`: the media in which unequal goods of comparable value are exchanged
- `emotion-as-translator`: the calculated value coefficient is transformed into an emotion Source: `src:c1:p41@379-p41@442`: the calculated value coefficient is transformed into an emotion
- `perception-vs-actuality-mechanism`: then the perception of value must be the mechanism that lies at the heart of sexual relationships. Source: `src:c1:p23@565-p23@663`: then the perception of value must be the mechanism that lies at the heart of sexual relationships.

#### What The Mechanism Retained

- The snapshot strongly retains the three probe-targeted structural signals: the covert calculator model (value coefficient concept with provisional values/weights/aggregation), subjective and fluctuating value (driven by goal-relevance and information), and emotion as valuation output (conceptually captured via 'emotion-as-translator' with quote 'the calcula…

#### What It Missed Or Distorted

- this is a sub-component rather than a central structural feature.

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `4`, fidelity `4`, overall `4`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot strongly retains the three probe-targeted structural signals: the covert calculator model (value coefficient concept with provisional values/weights/aggregation), subjective and fluctuating value (driven by goal-relevance and information), and emotion as valuation output (conceptually captured via 'emotion-as-translator' with quote 'the calculated value coefficient is transformed into an emotion'). Rece…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` filtered by `probe_index=3`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[2]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 4 — near 75%

#### Probe Position And Question

- target / captured: `c1-s293` -> `c1-s297`
- boundary kind: `late hinge before complication`
- why this probe point: Captures the goal-relative human value frame before the text complicates the model with revealed preferences and red flags.
- structural signals to check:
  - goal-relative human value
  - problem-of-living inference
  - selection thresholds and mating/dating as genetic-survival game

#### Source Orientation

- capture-neighborhood excerpt: We can call this goal conflation, which occurs when a single means (i.e., a specific relationship) is used to pursue mu… / Goal conflation makes every aspect of a relationship more challenging because completely satisfying options will be bot… / As a result, most people will not be able to get everything they want fro…
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 1 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `transactional-relationships-framing`: Relationships as value-transaction media: this is the governing frame introduced at the outset. Source: `src:c1:p3@0-p3@56`: RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED
- `default-skepticism-default`: Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions. Source: `src:c1:p4@452-p4@516`: other people are typically a problem until they prove otherwise.
- `comparable-value-exchange`: the media in which unequal goods of comparable value are exchanged Source: `src:c1:p12@464-p12@530`: the media in which unequal goods of comparable value are exchanged
- `emotion-as-translator`: the calculated value coefficient is transformed into an emotion Source: `src:c1:p41@379-p41@442`: the calculated value coefficient is transformed into an emotion
- `perception-vs-actuality-mechanism`: then the perception of value must be the mechanism that lies at the heart of sexual relationships. Source: `src:c1:p23@565-p23@663`: then the perception of value must be the mechanism that lies at the heart of sexual relationships.

#### What The Mechanism Retained

- The snapshot retains core material including the transactional relationships thesis, the goal-relative value frame (plumber/cardiology analogy, value coefficient, goal-relevance drivers), and the genetic-survival framing of mating/dating as 'the game of games.'

#### What It Missed Or Distorted

- the 'problem-of-living inference' framing ('What problem of living are they attempting to solve?') is not explicitly retained as a named inferential structure, though its content appears indirectly. More significantly, the exemplar-based selection mechanism is absent despite being a central structural device introduced around the probe point—the source disc…

#### Score Rationale

- scores: salience `3`, mainline `4`, organization `3`, fidelity `4`, overall `3.5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains core material including the transactional relationships thesis, the goal-relative value frame (plumber/cardiology analogy, value coefficient, goal-relevance drivers), and the genetic-survival framing of mating/dating as 'the game of games.' However, the 'problem-of-living inference' framing ('What problem of living are they attempting to solve?') is not explicitly retained as a named inferential…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` filtered by `probe_index=4`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[3]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 5 — window end

#### Probe Position And Question

- target / captured: `c1-s391` -> `c1-s391`
- boundary kind: `window end`
- why this probe point: Ends the active window after the model has expanded into desire, disgust, red flags, and revealed preferences.
- structural signals to check:
  - goal conflation
  - desire, disgust, conflict, and red flags
  - revealed preferences, culture, and valuation algorithm

#### Source Orientation

- capture-neighborhood excerpt: Penguins, ostriches, and condors are fully just as avian as sparrows, but an algorithm trained exclusively on sparrows … / We could call this the law of small numbers as applied to relationships, and it skews our valuations irrespective of th…
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 1 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `transactional-relationships-framing`: Relationships as value-transaction media: this is the governing frame introduced at the outset. Source: `src:c1:p3@0-p3@56`: RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED
- `default-skepticism-default`: Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions. Source: `src:c1:p4@452-p4@516`: other people are typically a problem until they prove otherwise.
- `approach-avoidance-conflict-taxonomy`: high-value individual is desire. low-value individual is disgust. mid-value individual — if a lot of what we really want AND a lot of what we really don't — we feel conf… Source: `src:c1:p63@0-p65@1416`: high-value individual is desire. low-value individual is disgust. mid-value individual — if a lot o…
- `comparable-value-exchange`: the media in which unequal goods of comparable value are exchanged Source: `src:c1:p12@464-p12@530`: the media in which unequal goods of comparable value are exchanged
- `perception-vs-actuality-mechanism`: then the perception of value must be the mechanism that lies at the heart of sexual relationships. Source: `src:c1:p23@565-p23@663`: then the perception of value must be the mechanism that lies at the heart of sexual relationships.

#### What The Mechanism Retained

- The snapshot retains strong coverage of the book's foundational framework (relationships as value-transaction media, comparable-value exchange, the covert calculator, emotion-as-translator) and captures key later additions including the approach-avoidance conflict taxonomy (desire/disgust/conflict) and the law of small numbers from parental relationship tra…

#### What It Missed Or Distorted

- 'goal conflation' — explicitly named as one of the two major complicators in the source — has no dedicated active_item or concept entry, despite being a significant structural pivot. The 'red flags' material is present only in the probe metadata, not as a retained semantic item. The revealed-preferences insight (people's choices reveal their values; direct …

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `3`, overall `3`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains strong coverage of the book's foundational framework (relationships as value-transaction media, comparable-value exchange, the covert calculator, emotion-as-translator) and captures key later additions including the approach-avoidance conflict taxonomy (desire/disgust/conflict) and the law of small numbers from parental relationship training. However, 'goal conflation' — explicitly named as one …

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl` filtered by `probe_index=5`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[4]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

## Callback / FVI Audit

Callback audit reads visible reactions, not memory state. A grounded callback correctly reconnects to earlier visible material; weak callback gestures at prior material but with loose or underspecified anchoring; FVI is a false visible integration; local-only makes no callback claim.

| Label | Count | What it means |
| --- | ---: | --- |
| grounded callback | 11 | credited visible continuity |
| weak callback | 9 | attempted continuity with loose or incomplete grounding |
| false visible integration | 1 | visible continuity claim judged unsupported or wrong |
| local-only reaction | 37 | visible reaction without callback claim |

### Grounded Callback Examples

#### `rx:Full_Content:src:c1:p11@0-p11@916:discern:9`

- reaction: The unconscious-valuation point extends the earlier exclusion of non-transactable gifts. If people don't fully know their own valuations, even 'spontaneous' generosity or liking may be driven by processes below awareness. This feels like a foundational claim for the book's model.
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly references 'earlier exclusion of non-transactable gifts' from reaction 7, extending that concept to the unconscious-valuation point.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p14@0-p15@559:discern:12`

- reaction: This adds a crucial layer to the transactional model — not just that value is exchanged, but that the exchange must be hidden. Relationships work partly because the negotiation itself stays invisible. This extends beyond the 'beneath awareness' point from earlier: it's not only that valuations are unconscious, it's that the whole transac…
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly extends from the 'beneath awareness' point (referencing reaction 9's unconscious-valuation discussion) and adds the concept of socially forbidden explicit negotiation.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p16@0-p16@1015:discern:13`

- reaction: This is a clean two-boundary theorem for relationship formation. Too symmetric (identical goods) → no transaction. Too asymmetric (disparate values) → relationship probability decreases. Only the narrow middle band — unequal goods, comparable value — sustains the exchange. This extends the earlier 'unequal goods of comparable value' defi…
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly extends the 'unequal goods of comparable value' definition from reaction 10, applying it as a generative condition with named failure modes.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

### Weak Callback Examples

#### `rx:Full_Content:src:c1:p13@0-p13@543:discern:11`

- reaction: This closes the paragraph as a clean structural rule, completing the thought that began with the unequal-subjective premise. It extends the transactional model from mechanism (what is exchanged) into form (how it is acknowledged), but doesn't add a new concept — it maps existing relationship types onto the framework.
- prior-link evidence: no structured prior_link present
- judge reason: Uses vague phrase 'unequal-subjective premise' that doesn't clearly map to any specific earlier visible reaction, making the linkage partial and unsupported.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`

- reaction: This is the direct answer to the value-examination promised at paragraph 26. Not a metaphor or analogy — the definition of value itself is scarcity-derived. It connects back to the irreversibility claim in paragraph 28: since resources cannot be refunded, scarcity is structural, not incidental.
- prior-link evidence: no structured prior_link present
- judge reason: References the internal text structure ('promised at paragraph 26,' 'irreversibility claim in paragraph 28') and a general connection to the 'reversibility test' in reaction 22, but these are structural cross-references within the segment rather than grounded callbacks to previously surfaced visible content.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p34@0-p35@1132:discern:30`

- reaction: The scale claim is striking — not that valuation is complex, but that it is continuous and parallel. This reframes value determination from a discrete decision event to a constant computational flood. It makes the "opaque" quality mentioned earlier even more structurally inevitable: if this process is running beneath awareness across unc…
- prior-link evidence: no structured prior_link present
- judge reason: Vaguely references 'opaque' and 'beneath awareness' concepts that appear to derive from earlier visible material (reaction 12's 'hidden negotiation,' reaction 24's 'beneath the surface'), but the linkage is implied rather than explicit and lacks specific grounding.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

### False Visible Integration Examples

#### `rx:Full_Content:src:c1:p19@0-p19@794:retrospect:18`

- reaction: This is the core concession of the book so far — a direct acknowledgment that the framework's rigor comes at the cost of practical specificity. Principles that survive contact with individual variation become too thin to act on.
- prior-link evidence: ref_ids=['active_attention:nested-game-structure']
- judge reason: The compat_type is 'retrospect' and prior_link points to 'active_attention:nested-game-structure', but no earlier visible reaction in this window contains that specific ref_id or explicitly surfaces the concession being referenced. The link connects to something outside the visible evidence surface.
- Reviewer reading: this is harmful callback evidence: the reaction presents an integration as visible continuity, but the judge could not ground that prior claim in earlier visible material.

## Reviewer Manual Check

To manually verify this page, inspect these fields in order:

1. Lane A: open selected `note_cases/*.json`; compare `note_case.source_span_slices`, `candidate_reactions`, `best_reaction.source_span_slices`, `judgment.label`, and `judgment.reason`.
2. Lane B MQ: open `memory_quality_probe_snapshots.json`; for each probe, inspect `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, and `source_ref_digest` before reading final runtime state.
3. Callback/FVI: open `reaction_audit_results.jsonl`; compare `label`, `prior_link`, `content`, and judge `reason`.
4. Runtime diagnosis: use files under `_mechanisms/attentional_v2/runtime/` only to explain why state ended up this way; do not use final runtime state to overwrite probe-time scoring evidence.

## Claims Not Authorized

- This window page is not product-quality proof.
- This window page does not update `evidence_catalog.md` or `evidence_catalog.json`.
- This window page does not promote Long Span vNext to formal benchmark authority.
- Callback counts, SourceRef counts, audit existence, and trace existence are diagnostic evidence only, not standalone quality scores.
