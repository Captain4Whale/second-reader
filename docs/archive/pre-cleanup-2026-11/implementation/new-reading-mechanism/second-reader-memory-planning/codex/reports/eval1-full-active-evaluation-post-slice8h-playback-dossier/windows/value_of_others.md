# Eval-1 Playback Dossier: The Value of Others

This playback page is a product-facing reading trace for human review. It replays the Eval-1 window in reading order, then explains how the four evaluation channels score that trace. It is not a new eval run, not a catalog update, not product-quality proof, and not Long Span formal authority.

## Window Verdict

- Lane A selective-legibility recall: `0.2979` over `94` note cases (`10` exact, `18` focused, `4` incidental, `62` miss).
- Lane B Memory Quality: `3.65` average over `5` semantic probes.
- Visible reaction audit: `58` reactions (`11` grounded callback, `9` weak callback, `1` FVI, `37` local-only).
- Reviewer stance: read the timeline first, then the scoring interpretation. The score is justified by the trace, not by the aggregate table alone.

## Evidence Map

- Dataset source window: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/value_of_others_private_en__segment_1.md`
- Raw segment text: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/value_of_others_private_en__segment_1.txt`
- Lane A run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others`
- Lane B run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others`
- Lane A note cases: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases`
- Lane B MQ rows: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/memory_quality_results.jsonl`
- Lane B reaction audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/summary/reaction_audit_results.jsonl`
- Probe snapshots: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`
- Normalized eval bundle: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`

## Source Window And Chapter Coverage

- Covered chapters: `Chapter 1`
- Full reviewer-readable source window lives beside the dataset: `source_windows_readable/value_of_others_private_en__segment_1.md`.
- Each reaction below includes its own source-span excerpt so the reviewer can stay in reading flow, then jump to the full source window when needed.

## Selective Legibility Note-Case Ledger

This ledger lists every dataset note target in the window. Matched note cases point to the reaction that appears later in the reading timeline; misses remain visible here so reviewer analysis is not biased toward successful reactions only.

### Note `e0001` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0001`
- target note:
```text
People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which people are which – which is why other people are typically a problem until they prove otherwise.
```
- target source span(s):
  - `p4@0-516`: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which people are which – which is why other people are typically a problem until they prove otherwise.
- matched reaction in timeline: `rx:Full_Content:src:c1:p1@0-p4@516:discern:2`
- source-span relation: `note_contains_candidate`; coverage `0.124`
- judge/runner reason: The reaction's quoted span (the closing sentence about other people being a problem until they prove otherwise) captures the note's key insight and thesis. The reaction directly engages with this content, interpreting it as an 'inversion of social norm of assumed goodwill' and considering its broader implications for the book's development, indicating substantive engagement with the note's core argument rather than incidental coverage.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0001.json`

### Note `e0126` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0126`
- target note:
```text
People want things from other people.
```
- target source span(s):
  - `p4@0-37`: People want things from other people.
- matched reaction in timeline: `rx:Full_Content:src:c1:p1@0-p4@516:discern:1`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0126.json`

### Note `e0127` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0127`
- target note:
```text
People typically don’t join together because they want the same things.
```
- target source span(s):
  - `p7@367-438`: People typically don’t join together because they want the same things.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0127.json`

### Note `e0128` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0128`
- target note:
```text
Keep in mind that to want has a double meaning: it can mean both to desire and to lack.
```
- target source span(s):
  - `p7@551-638`: Keep in mind that to want has a double meaning: it can mean both to desire and to lack.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0128.json`

### Note `e0129` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0129`
- target note:
```text
This is why people who want the same things are generally useless to each other: each lacks what the other desires .
```
- target source span(s):
  - `p7@639-754`: This is why people who want the same things are generally useless to each other: each lacks what the other desires.
- matched reaction in timeline: `rx:Full_Content:src:c1:p5@0-p7@754:discern:3`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0129.json`

### Note `e0130` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0130`
- target note:
```text
In most cases, people come together because they want different things.
```
- target source span(s):
  - `p8@0-71`: In most cases, people come together because they want different things.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0130.json`

### Note `e0131` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0131`
- target note:
```text
And if we exchange the things we respectively want, then we enter into a relationship.
```
- target source span(s):
  - `p8@382-468`: And if we exchange the things we respectively want, then we enter into a relationship.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0131.json`

### Note `e0132` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0132`
- target note:
```text
why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
```
- target source span(s):
  - `p8@505-717`: why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
- matched reaction in timeline: `rx:Full_Content:src:c1:p8@0-p9@894:discern:5`
- source-span relation: `note_contains_candidate`; coverage `0.6321`
- judge/runner reason: The reaction's quoted span captures the central claim of the note—the moral inversion where neither goodness, love, nor virtue but functional desire drives relationships—and the reaction's analysis of the 'neither...nor...nor...but' structural rejection directly engages with the note's core argument. While the reaction omits the introductory question about why some people are rich in relationship opportunities, the substantive philosophical claim it addresses is the most important content of the note.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0132.json`

### Note `e0133` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0133`
- target note:
```text
A relationship is the medium in which value is transacted.
```
- target source span(s):
  - `p9@0-58`: A relationship is the medium in which value is transacted.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0133.json`

### Note `e0134` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0134`
- target note:
```text
Most individuals do not walk around with either desire and admiration or fear and animosity toward other human beings: instead, they feel indifferent.
```
- target source span(s):
  - `p9@476-626`: Most individuals do not walk around with either desire and admiration or fear and animosity toward other human beings: instead, they feel indifferent.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0134.json`

### Note `e0135` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0135`
- target note:
```text
On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
```
- target source span(s):
  - `p10@132-377`: On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
- matched reaction in timeline: `rx:Full_Content:src:c1:p10@0-p10@661:discern:7`
- source-span relation: `note_contains_candidate`; coverage `0.9184`
- judge/runner reason: The reaction's quoted span overlaps almost entirely with the note's text (0.9184 coverage), capturing the core claim about gifts without transactability being excluded from relationship foundations. The reaction directly engages with this specific argument—identifying it as a 'hardest-line exclusion,' acknowledging the internal logic, and raising a substantive philosophical challenge about whether unconditional generosity can exist within this framework. The focus is tightly on the note's essential content, not tangential.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0135.json`

### Note `e0136` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0136`
- target note:
```text
relationships require exchange, and unilateral transactions don’t meet the criteria.
```
- target source span(s):
  - `p10@394-478`: relationships require exchange, and unilateral transactions don’t meet the criteria.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0136.json`

### Note `e0137` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0137`
- target note:
```text
Relationships must go both ways.
```
- target source span(s):
  - `p10@629-661`: Relationships must go both ways.
- matched reaction in timeline: `rx:Full_Content:src:c1:p10@0-p10@661:discern:8`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0137.json`

### Note `e0138` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0138`
- target note:
```text
value is neither static nor objective. As we’ll see, it exists solely in the mind of the valuer, and it is subject to constant fluctuation as new information emerges and circumstances evolve.
```
- target source span(s):
  - `p11@151-342`: value is neither static nor objective. As we’ll see, it exists solely in the mind of the valuer, and it is subject to constant fluctuation as new information emerges and circumstances evolve.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0138.json`

### Note `e0139` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0139`
- target note:
```text
these valuations must be comparable. People do not willingly exchange something they value highly for something they do not.
```
- target source span(s):
  - `p12@11-135`: these valuations must be comparable. People do not willingly exchange something they value highly for something they do not.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0139.json`

### Note `e0140` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0140`
- target note:
```text
As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
```
- target source span(s):
  - `p12@386-531`: As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
- matched reaction in timeline: `rx:Full_Content:src:c1:p12@0-p12@531:discern:10`
- source-span relation: `note_contains_candidate`; coverage `0.9103`
- judge/runner reason: The reaction's quoted span nearly matches the note (91% overlap), and the reaction's explanatory content is tightly focused on interpreting the key terms 'unequal goods' and 'comparable value' within the source span. The reaction genuinely engages with the refined definition rather than treating it as incidental context.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0140.json`

### Note `e0141` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0141`
- target note:
```text
Since these values are both unequal and subjective, relationships must be negotiated – not just at their inception but through their entire duration, as well.
```
- target source span(s):
  - `p13@0-158`: Since these values are both unequal and subjective, relationships must be negotiated – not just at their inception but through their entire duration, as well.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0141.json`

### Note `e0142` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0142`
- target note:
```text
A game is anything with rules and a goal. And under this definition, human relationships are games.
```
- target source span(s):
  - `p17@457-556`: A game is anything with rules and a goal. And under this definition, human relationships are games.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0142.json`

### Note `e0143` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0143`
- target note:
```text
In relationships, people try to get what they want from others: this is the goal. And they have to go about doing this without violating – or, more realistically, selectively violating – various inter- and intrapersonal guidelines: these are the rules.
```
- target source span(s):
  - `p17@557-809`: In relationships, people try to get what they want from others: this is the goal. And they have to go about doing this without violating – or, more realistically, selectively violating – various inter- and intrapersonal guidelines: these are the rules.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0143.json`

### Note `e0144` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0144`
- target note:
```text
If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
```
- target source span(s):
  - `p17@810-961`: If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
- matched reaction in timeline: `rx:Full_Content:src:c1:p17@0-p17@961:discern:15`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0144.json`

### Note `e0145` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0145`
- target note:
```text
Every type of relationship constitutes a different game – as does every specific relationship of the same type.
```
- target source span(s):
  - `p18@0-111`: Every type of relationship constitutes a different game – as does every specific relationship of the same type.
- matched reaction in timeline: `rx:Full_Content:src:c1:p18@0-p18@875:discern:16`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0145.json`

### Note `e0146` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0146`
- target note:
```text
On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the highest wisdom can often sound so vague and idiotic, while detailed advice can be so contentious and inapplicable.
```
- target source span(s):
  - `p20@31-561`: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the highest wisdom can often sound so vague and idiotic, while detailed advice can be so contentious and in…
- matched reaction in timeline: `rx:Full_Content:src:c1:p20@0-p20@737:highlight:19`
- source-span relation: `note_contains_candidate`; coverage `0.7528`
- judge/runner reason: The reaction's quoted span captures the core two-horn structure (specificity→validity loss and generality→utility loss) which is the essential analytical content of the note. The reaction's commentary focuses specifically on this structural symmetry rather than tangential content, making it a focused engagement with the overlapped source span.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0146.json`

### Note `e0147` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0147`
- target note:
```text
people enter into (and remain in) sexual relationships with their perceived best options.
```
- target source span(s):
  - `p23@177-266`: people enter into (and remain in) sexual relationships with their perceived best options.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0147.json`

### Note `e0148` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0148`
- target note:
```text
Value is easy to define but difficult to pin down. Our everyday use of the word suggests a serviceable enough definition: value is something that people are willing to pay for. And payment, in turn, is the expenditure of resources.
```
- target source span(s):
  - `p28@0-231`: Value is easy to define but difficult to pin down. Our everyday use of the word suggests a serviceable enough definition: value is something that people are willing to pay for. And payment, in turn, is the expenditure of resources.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0148.json`

### Note `e0149` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0149`
- target note:
```text
Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
```
- target source span(s):
  - `p28@296-510`: Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
- matched reaction in timeline: `rx:Full_Content:src:c1:p27@0-p28@512:discern:25`
- source-span relation: `note_contains_candidate`; coverage `0.2196`
- judge/runner reason: The reaction explicitly quotes and builds upon the core claim about resource non-recoverability ('resources – once expended – cannot be refunded'), extending it to a theoretical point about valuation being 'structurally locked in.' The reaction is tightly focused on this specific claim rather than the broader paragraph, making it a purposeful engagement with the note's key content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0149.json`

### Note `e0150` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0150`
- target note:
```text
This means that people have to make decisions about how they allocate their limited resources most effectively. They can’t have everything, and pursuing some paths will close off others.
```
- target source span(s):
  - `p29@138-324`: This means that people have to make decisions about how they allocate their limited resources most effectively. They can’t have everything, and pursuing some paths will close off others.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0150.json`

### Note `e0151` — `incidental_cover`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0151`
- target note:
```text
At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
```
- target source span(s):
  - `p29@325-565`: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
- matched reaction in timeline: `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`
- source-span relation: `note_contains_candidate`; coverage `0.5083`
- judge/runner reason: The reaction's quoted span captures only the first sentence about scarcity creating value while omitting the Greek mythology example that serves as the note's key illustrative support. Although the reaction's commentary is focused on the scarcity-value connection, the intentional exclusion of the mythological elaboration suggests the note's full important content is not being addressed.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0151.json`

### Note `e0152` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0152`
- target note:
```text
it’s important to appreciate that value is never static.
```
- target source span(s):
  - `p30@268-324`: it’s important to appreciate that value is never static.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0152.json`

### Note `e0153` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0153`
- target note:
```text
What’s more, value is never objective. As we’ll see, it only exists in the minds of the valuers.
```
- target source span(s):
  - `p30@399-495`: What’s more, value is never objective. As we’ll see, it only exists in the minds of the valuers.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0153.json`

### Note `e0154` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0154`
- target note:
```text
There are two primary drivers of value fluctuation at the individual level: goal-relevance and information.
```
- target source span(s):
  - `p31@0-107`: There are two primary drivers of value fluctuation at the individual level: goal-relevance and information.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0154.json`

### Note `e0155` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0155`
- target note:
```text
In fact, the human experience means being embedded in a complex and interrelated set of nested games.
```
- target source span(s):
  - `p31@299-400`: In fact, the human experience means being embedded in a complex and interrelated set of nested games.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0155.json`

### Note `e0156` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0156`
- target note:
```text
the covert calculator that exists within all of us doesn’t require our understanding to operate. It goes about its calculations intuitively and unconsciously – whether we want it to or not.
```
- target source span(s):
  - `p37@860-1049`: the covert calculator that exists within all of us doesn’t require our understanding to operate. It goes about its calculations intuitively and unconsciously – whether we want it to or not.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0156.json`

### Note `e0157` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0157`
- target note:
```text
the calculated value coefficient is transformed into an emotion.
```
- target source span(s):
  - `p41@379-443`: the calculated value coefficient is transformed into an emotion.
- matched reaction in timeline: `rx:Full_Content:src:c1:p40@0-p41@710:highlight:34`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction directly engages with the note's core concept—the transformation of the value coefficient into emotion—interpreting and expanding on it as the book's central mechanism. The quoted source span begins with the exact note text and extends naturally to explain the significance and function of this transformation.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0157.json`

### Note `e0158` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0158`
- target note:
```text
All’s fair in love and war.
```
- target source span(s):
  - `p52@304-331`: All’s fair in love and war.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0158.json`

### Note `e0159` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0159`
- target note:
```text
While the “game of war” is associated with the survival of the individual organism, the “game of love” is associated with the survival of the individual’s genes.
```
- target source span(s):
  - `p53@0-161`: While the “game of war” is associated with the survival of the individual organism, the “game of love” is associated with the survival of the individual’s genes.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0159.json`

### Note `e0160` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0160`
- target note:
```text
As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
```
- target source span(s):
  - `p54@0-251`: As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
- matched reaction in timeline: `rx:Full_Content:src:c1:p54@0-p55@595:discern:44`
- source-span relation: `note_contains_candidate`; coverage `0.255`
- judge/runner reason: The reaction's quoted span covers the 'game of games' phrase, which is the note's core conceptual contribution—the distinctive framing that elevates mating/dating from merely dominant to constitutive. Although the note includes the surrounding context about 'nested hierarchy' and ranking, the reaction demonstrates genuine engagement with the note's most substantive idea: the double framing that allows the text to derive behavioral consequences as logical deductions. The analysis is focused and adds interpretive value to the specific span selected.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0160.json`

### Note `e0161` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0161`
- target note:
```text
After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
```
- target source span(s):
  - `p55@399-595`: After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
- matched reaction in timeline: `rx:Full_Content:src:c1:p54@0-p55@595:discern:45`
- source-span relation: `note_contains_candidate`; coverage `0.4745`
- judge/runner reason: The reaction's quoted span (about balking and post-job payment) intersects with an important part of the note's argument about transactional logic, and the analysis directly addresses the rhetorical strategy within that quoted portion. The commentary engages substantively with the 'balk' language and reframing mechanism present in the overlap, making this focused rather than incidental.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0161.json`

### Note `e0162` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0162`
- target note:
```text
Though potentially challenging (and frustrating), the changing priority of our goals – and, therefore, the fluctuating value of any given person for a particular relationship over time – might be navigable were it not for two additional variables that significantly complicate the matter further, namely: goal conflation and lack of awareness.
```
- target source span(s):
  - `p56@0-343`: Though potentially challenging (and frustrating), the changing priority of our goals – and, therefore, the fluctuating value of any given person for a particular relationship over time – might be navigable were it not for two additional variables that significantly complicate the matter further, namely: goal conflation and lack of awareness.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0162.json`

### Note `e0163` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0163`
- target note:
```text
As a result, most people will not be able to get everything they want from a single person. And this means – when it comes to relationships – there aren’t any solutions, only trade-offs.
```
- target source span(s):
  - `p58@0-186`: As a result, most people will not be able to get everything they want from a single person. And this means – when it comes to relationships – there aren’t any solutions, only trade-offs.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0163.json`

### Note `e0164` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0164`
- target note:
```text
Remember: no one continues to pay the plumber.
```
- target source span(s):
  - `p59@874-920`: Remember: no one continues to pay the plumber.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0164.json`

### Note `e0165` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0165`
- target note:
```text
What’s more, the individual is generally only made aware of the outcome of this process when the value coefficient is transmuted into an emotion. And with respect to sexual relationships, the emotion into which this value coefficient is transmuted is desire.
```
- target source span(s):
  - `p60@292-550`: What’s more, the individual is generally only made aware of the outcome of this process when the value coefficient is transmuted into an emotion. And with respect to sexual relationships, the emotion into which this value coefficient is transmuted is desire.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0165.json`

### Note `e0166` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0166`
- target note:
```text
This is the true (though, perhaps, unsatisfying) definition of a high-value man (or woman): it is a person we perceive as being able to give us more of what is most important to us, given the current prioritization of our goals. What’s more, this person’s ability to give us more of what is most important to us should not be compromised by any significant liabilities that would negate the benefits we hope to accrue in a relationship with him (or her). That is, a high-value person also gives us less of what we don’t want.
```
- target source span(s):
  - `p61@0-525`: This is the true (though, perhaps, unsatisfying) definition of a high-value man (or woman): it is a person we perceive as being able to give us more of what is most important to us, given the current prioritization of our goals. What’s more, this person’s ability to give us more of what is most important to us should not be compromised by any significant liabilities that would negate the benefits we hope to accrue in a relationship with him (or her). That is, a high-value person also gives us less of what we don’t…
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0166.json`

### Note `e0167` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0167`
- target note:
```text
because value and desire are the same thing experienced in different ways.
```
- target source span(s):
  - `p62@802-876`: because value and desire are the same thing experienced in different ways.
- matched reaction in timeline: `rx:Full_Content:src:c1:p60@0-p62@876:retrospect:47`
- source-span relation: `note_contains_candidate`; coverage `0.8919`
- judge/runner reason: The reaction's quoted span (810-876) falls within the note's source span (802-876), and the reaction directly engages with the note's core claim that value and desire are the same thing experienced differently. The reaction builds on this idea by explaining it as 'two registers of a single process,' connecting valuation and desire as simultaneous registers rather than sequential stages.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0167.json`

### Note `e0168` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0168`
- target note:
```text
If we perceive that a person might be capable of giving us a few things we kinda want (and a few things we kinda don’t), we typically feel indifferent.
```
- target source span(s):
  - `p65@761-912`: If we perceive that a person might be capable of giving us a few things we kinda want (and a few things we kinda don’t), we typically feel indifferent.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0168.json`

### Note `e0169` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0169`
- target note:
```text
it is generally useless to directly ask people what they want in a sexual partner. Even if they could tell you the whole story (and they can’t), they wouldn’t. This is due to the fact that sharing some parts of that story would result in social censure and other parts might compromise the attainment of their goals.
```
- target source span(s):
  - `p72@333-649`: it is generally useless to directly ask people what they want in a sexual partner. Even if they could tell you the whole story (and they can’t), they wouldn’t. This is due to the fact that sharing some parts of that story would result in social censure and other parts might compromise the attainment of their goals.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0169.json`

### Note `e0170` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0170`
- target note:
```text
In many respects, the brain is like a machine learning algorithm. It is hardwired with certain computational pathways, but it must be trained on data to function properly. And how accurately and efficiently such an algorithm performs its intended purpose is directly related to the data on which it is trained. These data not only constitute the inputs of the algorithm, they are also capable of altering the structure and process of the algorithm itself.
```
- target source span(s):
  - `p75@349-804`: In many respects, the brain is like a machine learning algorithm. It is hardwired with certain computational pathways, but it must be trained on data to function properly. And how accurately and efficiently such an algorithm performs its intended purpose is directly related to the data on which it is trained. These data not only constitute the inputs of the algorithm, they are also capable of altering the structure and process of the algorithm itself.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0170.json`

### Note `e0171` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0171`
- target note:
```text
The first reason is related to the quantity of our training data. If each of our valuation algorithms for sexual relationships is principally trained on data collected from just one relationship, then our algorithms will be unduly biased by the idiosyncratic features of that relationship.
```
- target source span(s):
  - `p77@0-289`: The first reason is related to the quantity of our training data. If each of our valuation algorithms for sexual relationships is principally trained on data collected from just one relationship, then our algorithms will be unduly biased by the idiosyncratic features of that relationship.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0171.json`

### Note `e0439` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0439`
- target note:
```text
People want things from other people.
```
- target source span(s):
  - `p4@0-37`: People want things from other people.
- matched reaction in timeline: `rx:Full_Content:src:c1:p1@0-p4@516:discern:1`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0439.json`

### Note `e0440` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0440`
- target note:
```text
People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which people are which – which is why other people are typically a problem until they prove otherwise.
```
- target source span(s):
  - `p4@0-516`: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which people are which – which is why other people are typically a problem until they prove otherwise.
- matched reaction in timeline: `rx:Full_Content:src:c1:p1@0-p4@516:discern:2`
- source-span relation: `note_contains_candidate`; coverage `0.124`
- judge/runner reason: The reaction explicitly anchors on the closing sentence of the source span and engages substantively with its meaning—specifically how it 'inverts the social norm of assumed goodwill' into a skeptical default. While the note covers broader themes (others as both solution and problem), the reaction genuinely engages with the core claim captured in the overlapped source text and offers interpretive analysis about its rhetorical effect and significance for reading forward.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0440.json`

### Note `e0441` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0441`
- target note:
```text
People typically don’t join together because they want the same things.
```
- target source span(s):
  - `p7@367-438`: People typically don’t join together because they want the same things.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0441.json`

### Note `e0442` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0442`
- target note:
```text
Keep in mind that to want has a double meaning: it can mean both to desire and to lack.
```
- target source span(s):
  - `p7@551-638`: Keep in mind that to want has a double meaning: it can mean both to desire and to lack.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0442.json`

### Note `e0443` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0443`
- target note:
```text
This is why people who want the same things are generally useless to each other: each lacks what the other desires .
```
- target source span(s):
  - `p7@639-754`: This is why people who want the same things are generally useless to each other: each lacks what the other desires.
- matched reaction in timeline: `rx:Full_Content:src:c1:p5@0-p7@754:discern:3`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0443.json`

### Note `e0444` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0444`
- target note:
```text
In most cases, people come together because they want different things.
```
- target source span(s):
  - `p8@0-71`: In most cases, people come together because they want different things.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0444.json`

### Note `e0445` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0445`
- target note:
```text
And if we exchange the things we respectively want, then we enter into a relationship.
```
- target source span(s):
  - `p8@382-468`: And if we exchange the things we respectively want, then we enter into a relationship.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0445.json`

### Note `e0446` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0446`
- target note:
```text
why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
```
- target source span(s):
  - `p8@505-717`: why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
- matched reaction in timeline: `rx:Full_Content:src:c1:p8@0-p9@894:discern:5`
- source-span relation: `note_contains_candidate`; coverage `0.6321`
- judge/runner reason: The reaction's quoted span (the 'neither...nor...but' sentence about functional desire) captures the core insight of the note—that moral virtues are replaced by utility as the basis for relationship desirability. Though it covers only the second half of the note's span (char 583-717 vs. the note's 505-717), the reaction's analytical focus on the moral inversion and structural dismissal of virtue aligns with the note's central thesis.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0446.json`

### Note `e0447` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0447`
- target note:
```text
A relationship is the medium in which value is transacted.
```
- target source span(s):
  - `p9@0-58`: A relationship is the medium in which value is transacted.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0447.json`

### Note `e0448` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0448`
- target note:
```text
Most individuals do not walk around with either desire and admiration or fear and animosity toward other human beings: instead, they feel indifferent.
```
- target source span(s):
  - `p9@476-626`: Most individuals do not walk around with either desire and admiration or fear and animosity toward other human beings: instead, they feel indifferent.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0448.json`

### Note `e0449` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0449`
- target note:
```text
On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
```
- target source span(s):
  - `p10@132-377`: On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
- matched reaction in timeline: `rx:Full_Content:src:c1:p10@0-p10@661:discern:7`
- source-span relation: `note_contains_candidate`; coverage `0.9184`
- judge/runner reason: The reaction directly engages with the core claim of the note—that gifts with no transactability cannot form relationships—and substantively engages with the logic ('no transactability, no relationship') while raising probing questions about its implications for generosity and kindness. The quoted span covers the essential content of the note and the reaction is clearly focused on analyzing this specific exclusion rather than merely referencing it.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0449.json`

### Note `e0450` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0450`
- target note:
```text
relationships require exchange, and unilateral transactions don’t meet the criteria.
```
- target source span(s):
  - `p10@394-478`: relationships require exchange, and unilateral transactions don’t meet the criteria.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0450.json`

### Note `e0451` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0451`
- target note:
```text
Relationships must go both ways.
```
- target source span(s):
  - `p10@629-661`: Relationships must go both ways.
- matched reaction in timeline: `rx:Full_Content:src:c1:p10@0-p10@661:discern:8`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0451.json`

### Note `e0452` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0452`
- target note:
```text
value is neither static nor objective. As we’ll see, it exists solely in the mind of the valuer, and it is subject to constant fluctuation as new information emerges and circumstances evolve.
```
- target source span(s):
  - `p11@151-342`: value is neither static nor objective. As we’ll see, it exists solely in the mind of the valuer, and it is subject to constant fluctuation as new information emerges and circumstances evolve.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0452.json`

### Note `e0453` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0453`
- target note:
```text
these valuations must be comparable. People do not willingly exchange something they value highly for something they do not.
```
- target source span(s):
  - `p12@11-135`: these valuations must be comparable. People do not willingly exchange something they value highly for something they do not.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0453.json`

### Note `e0454` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0454`
- target note:
```text
As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
```
- target source span(s):
  - `p12@386-531`: As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
- matched reaction in timeline: `rx:Full_Content:src:c1:p12@0-p12@531:discern:10`
- source-span relation: `note_contains_candidate`; coverage `0.9103`
- judge/runner reason: The reaction's source span covers 91% of the note's text, and the content directly unpacks the core concepts ('unequal goods' and 'comparable value') and explains the mechanism the definition describes. The reaction is tightly focused on explaining the specific phrase 'unequal goods of comparable value are exchanged' rather than being tangential to it.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0454.json`

### Note `e0455` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0455`
- target note:
```text
Since these values are both unequal and subjective, relationships must be negotiated – not just at their inception but through their entire duration, as well.
```
- target source span(s):
  - `p13@0-158`: Since these values are both unequal and subjective, relationships must be negotiated – not just at their inception but through their entire duration, as well.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0455.json`

### Note `e0456` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0456`
- target note:
```text
A game is anything with rules and a goal. And under this definition, human relationships are games.
```
- target source span(s):
  - `p17@457-556`: A game is anything with rules and a goal. And under this definition, human relationships are games.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0456.json`

### Note `e0457` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0457`
- target note:
```text
In relationships, people try to get what they want from others: this is the goal. And they have to go about doing this without violating – or, more realistically, selectively violating – various inter- and intrapersonal guidelines: these are the rules.
```
- target source span(s):
  - `p17@557-809`: In relationships, people try to get what they want from others: this is the goal. And they have to go about doing this without violating – or, more realistically, selectively violating – various inter- and intrapersonal guidelines: these are the rules.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0457.json`

### Note `e0458` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0458`
- target note:
```text
If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
```
- target source span(s):
  - `p17@810-961`: If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
- matched reaction in timeline: `rx:Full_Content:src:c1:p17@0-p17@961:discern:15`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0458.json`

### Note `e0459` — `exact_match`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0459`
- target note:
```text
Every type of relationship constitutes a different game – as does every specific relationship of the same type.
```
- target source span(s):
  - `p18@0-111`: Every type of relationship constitutes a different game – as does every specific relationship of the same type.
- matched reaction in timeline: `rx:Full_Content:src:c1:p18@0-p18@875:discern:16`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0459.json`

### Note `e0460` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0460`
- target note:
```text
On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the highest wisdom can often sound so vague and idiotic, while detailed advice can be so contentious and inapplicable.
```
- target source span(s):
  - `p20@31-561`: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the highest wisdom can often sound so vague and idiotic, while detailed advice can be so contentious and in…
- matched reaction in timeline: `rx:Full_Content:src:c1:p20@0-p20@737:highlight:19`
- source-span relation: `note_contains_candidate`; coverage `0.7528`
- judge/runner reason: The reaction's source span covers the core two-horned dilemma (specificity→validity loss and generality→utility loss) that is the central argument of the note. The reaction explicitly analyzes this structural framing, identifying the 'two-horned structure' as the 'structural heart' and explaining how the symmetrical presentation makes the trade-off 'feel like a genuine constraint.' This directly engages with the note's substantive content rather than incidental coverage.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0460.json`

### Note `e0461` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0461`
- target note:
```text
people enter into (and remain in) sexual relationships with their perceived best options.
```
- target source span(s):
  - `p23@177-266`: people enter into (and remain in) sexual relationships with their perceived best options.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0461.json`

### Note `e0462` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0462`
- target note:
```text
Value is easy to define but difficult to pin down. Our everyday use of the word suggests a serviceable enough definition: value is something that people are willing to pay for. And payment, in turn, is the expenditure of resources.
```
- target source span(s):
  - `p28@0-231`: Value is easy to define but difficult to pin down. Our everyday use of the word suggests a serviceable enough definition: value is something that people are willing to pay for. And payment, in turn, is the expenditure of resources.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0462.json`

### Note `e0463` — `incidental_cover`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0463`
- target note:
```text
Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
```
- target source span(s):
  - `p28@296-510`: Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
- matched reaction in timeline: `rx:Full_Content:src:c1:p27@0-p28@512:discern:25`
- source-span relation: `note_contains_candidate`; coverage `0.2196`
- judge/runner reason: The reaction's source span (47 characters) covers only the final clause of the note about non-recoverability of expended resources, while the note's opening claim—that time, effort, attention, and opportunity are forms of resources—goes entirely uncovered. The reaction interprets and extends the non-recoverability concept into valuation locking and psychological pain, which is thoughtful but the quote itself is narrow relative to the note's full scope.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0463.json`

### Note `e0464` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0464`
- target note:
```text
This means that people have to make decisions about how they allocate their limited resources most effectively. They can’t have everything, and pursuing some paths will close off others.
```
- target source span(s):
  - `p29@138-324`: This means that people have to make decisions about how they allocate their limited resources most effectively. They can’t have everything, and pursuing some paths will close off others.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0464.json`

### Note `e0465` — `incidental_cover`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0465`
- target note:
```text
At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
```
- target source span(s):
  - `p29@325-565`: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
- matched reaction in timeline: `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`
- source-span relation: `note_contains_candidate`; coverage `0.5083`
- judge/runner reason: The reaction's quoted span covers only the first sentence of the note (scarcity creates value), and its content correctly identifies this as a core definition. However, the note's important content includes the mythological example about gods envying mortal mortality—this second part is completely unaddressed by the reaction. The reaction treats the passage as a standalone definition without engaging the illustrative reasoning that completes the note's argument. The 50.83% coverage, while substantial, leaves out a meaningful portion of the note's key content.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0465.json`

### Note `e0466` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0466`
- target note:
```text
it’s important to appreciate that value is never static.
```
- target source span(s):
  - `p30@268-324`: it’s important to appreciate that value is never static.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0466.json`

### Note `e0467` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0467`
- target note:
```text
What’s more, value is never objective. As we’ll see, it only exists in the minds of the valuers.
```
- target source span(s):
  - `p30@399-495`: What’s more, value is never objective. As we’ll see, it only exists in the minds of the valuers.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0467.json`

### Note `e0468` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0468`
- target note:
```text
There are two primary drivers of value fluctuation at the individual level: goal-relevance and information.
```
- target source span(s):
  - `p31@0-107`: There are two primary drivers of value fluctuation at the individual level: goal-relevance and information.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0468.json`

### Note `e0469` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0469`
- target note:
```text
In fact, the human experience means being embedded in a complex and interrelated set of nested games.
```
- target source span(s):
  - `p31@299-400`: In fact, the human experience means being embedded in a complex and interrelated set of nested games.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0469.json`

### Note `e0470` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0470`
- target note:
```text
the covert calculator that exists within all of us doesn’t require our understanding to operate. It goes about its calculations intuitively and unconsciously – whether we want it to or not.
```
- target source span(s):
  - `p37@860-1049`: the covert calculator that exists within all of us doesn’t require our understanding to operate. It goes about its calculations intuitively and unconsciously – whether we want it to or not.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0470.json`

### Note `e0471` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0471`
- target note:
```text
the calculated value coefficient is transformed into an emotion.
```
- target source span(s):
  - `p41@379-443`: the calculated value coefficient is transformed into an emotion.
- matched reaction in timeline: `rx:Full_Content:src:c1:p40@0-p41@710:highlight:34`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction's quoted source span contains the entire note text, and the reaction content directly engages with and elaborates the note's core claim: that a calculated value coefficient is transformed into an emotion, explaining it as the book's central mechanism where unconscious value calculations become conscious emotional readouts.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0471.json`

### Note `e0472` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0472`
- target note:
```text
All’s fair in love and war.
```
- target source span(s):
  - `p52@304-331`: All’s fair in love and war.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0472.json`

### Note `e0473` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0473`
- target note:
```text
While the “game of war” is associated with the survival of the individual organism, the “game of love” is associated with the survival of the individual’s genes.
```
- target source span(s):
  - `p53@0-161`: While the “game of war” is associated with the survival of the individual organism, the “game of love” is associated with the survival of the individual’s genes.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0473.json`

### Note `e0474` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0474`
- target note:
```text
As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
```
- target source span(s):
  - `p54@0-251`: As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
- matched reaction in timeline: `rx:Full_Content:src:c1:p54@0-p55@595:discern:44`
- source-span relation: `note_contains_candidate`; coverage `0.255`
- judge/runner reason: The reaction's quoted span ('the game of games: the game that makes all other games possible') is contained within the note, and the reaction's analysis directly addresses the core claim of the note—that mating/dating is not just dominant but constitutive of all other games. The reaction explains the rhetorical mechanism ('double framing') that makes this logical move work, which is the substantive insight in the note. While the note's opening clause about 'ranking very highly' and 'above individual survival' isn't quoted, the reaction engages with the most important conceptual content: the game-of-games framing and its implications.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0474.json`

### Note `e0475` — `incidental_cover`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0475`
- target note:
```text
After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
```
- target source span(s):
  - `p55@399-595`: After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
- matched reaction in timeline: `rx:Full_Content:src:c1:p54@0-p55@595:discern:45`
- source-span relation: `note_contains_candidate`; coverage `0.4745`
- judge/runner reason: The reaction's quoted span covers the second half of the note's source text (starting at 'People might balk...'), missing the first half which contains the core claim about the plumber being more valuable before the job is done. While the reaction analyzes the 'balk' and reframing logic, it does not genuinely engage with the note's primary point about relative value before versus after work is performed. The overlap covers only 47% of the note's source span, and the missing portion contains the note's most distinctive claim.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0475.json`

### Note `e0476` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0476`
- target note:
```text
Though potentially challenging (and frustrating), the changing priority of our goals – and, therefore, the fluctuating value of any given person for a particular relationship over time – might be navigable were it not for two additional variables that significantly complicate the matter further, namely: goal conflation and lack of awareness.
```
- target source span(s):
  - `p56@0-343`: Though potentially challenging (and frustrating), the changing priority of our goals – and, therefore, the fluctuating value of any given person for a particular relationship over time – might be navigable were it not for two additional variables that significantly complicate the matter further, namely: goal conflation and lack of awareness.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0476.json`

### Note `e0477` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0477`
- target note:
```text
As a result, most people will not be able to get everything they want from a single person. And this means – when it comes to relationships – there aren’t any solutions, only trade-offs.
```
- target source span(s):
  - `p58@0-186`: As a result, most people will not be able to get everything they want from a single person. And this means – when it comes to relationships – there aren’t any solutions, only trade-offs.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0477.json`

### Note `e0478` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0478`
- target note:
```text
Remember: no one continues to pay the plumber.
```
- target source span(s):
  - `p59@874-920`: Remember: no one continues to pay the plumber.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0478.json`

### Note `e0479` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0479`
- target note:
```text
What’s more, the individual is generally only made aware of the outcome of this process when the value coefficient is transmuted into an emotion. And with respect to sexual relationships, the emotion into which this value coefficient is transmuted is desire.
```
- target source span(s):
  - `p60@292-550`: What’s more, the individual is generally only made aware of the outcome of this process when the value coefficient is transmuted into an emotion. And with respect to sexual relationships, the emotion into which this value coefficient is transmuted is desire.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0479.json`

### Note `e0480` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0480`
- target note:
```text
This is the true (though, perhaps, unsatisfying) definition of a high-value man (or woman): it is a person we perceive as being able to give us more of what is most important to us, given the current prioritization of our goals. What’s more, this person’s ability to give us more of what is most important to us should not be compromised by any significant liabilities that would negate the benefits we hope to accrue in a relationship with him (or her). That is, a high-value person also gives us less of what we don’t want.
```
- target source span(s):
  - `p61@0-525`: This is the true (though, perhaps, unsatisfying) definition of a high-value man (or woman): it is a person we perceive as being able to give us more of what is most important to us, given the current prioritization of our goals. What’s more, this person’s ability to give us more of what is most important to us should not be compromised by any significant liabilities that would negate the benefits we hope to accrue in a relationship with him (or her). That is, a high-value person also gives us less of what we don’t…
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0480.json`

### Note `e0481` — `focused_hit`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0481`
- target note:
```text
because value and desire are the same thing experienced in different ways.
```
- target source span(s):
  - `p62@802-876`: because value and desire are the same thing experienced in different ways.
- matched reaction in timeline: `rx:Full_Content:src:c1:p60@0-p62@876:retrospect:47`
- source-span relation: `note_contains_candidate`; coverage `0.8919`
- judge/runner reason: The reaction's source span (810-876) overlaps with the note's source span (802-876), and the reaction's commentary directly engages with and elaborates the note's central claim. The content explains the mechanism ('Valuation below awareness produces desire above awareness') and clarifies the relationship ('two registers of a single process'), demonstrating genuine coverage of the note's important content rather than incidental reference.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0481.json`

### Note `e0482` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0482`
- target note:
```text
If we perceive that a person might be capable of giving us a few things we kinda want (and a few things we kinda don’t), we typically feel indifferent.
```
- target source span(s):
  - `p65@761-912`: If we perceive that a person might be capable of giving us a few things we kinda want (and a few things we kinda don’t), we typically feel indifferent.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0482.json`

### Note `e0483` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0483`
- target note:
```text
it is generally useless to directly ask people what they want in a sexual partner. Even if they could tell you the whole story (and they can’t), they wouldn’t. This is due to the fact that sharing some parts of that story would result in social censure and other parts might compromise the attainment of their goals.
```
- target source span(s):
  - `p72@333-649`: it is generally useless to directly ask people what they want in a sexual partner. Even if they could tell you the whole story (and they can’t), they wouldn’t. This is due to the fact that sharing some parts of that story would result in social censure and other parts might compromise the attainment of their goals.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0483.json`

### Note `e0484` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0484`
- target note:
```text
In many respects, the brain is like a machine learning algorithm. It is hardwired with certain computational pathways, but it must be trained on data to function properly. And how accurately and efficiently such an algorithm performs its intended purpose is directly related to the data on which it is trained. These data not only constitute the inputs of the algorithm, they are also capable of altering the structure and process of the algorithm itself.
```
- target source span(s):
  - `p75@349-804`: In many respects, the brain is like a machine learning algorithm. It is hardwired with certain computational pathways, but it must be trained on data to function properly. And how accurately and efficiently such an algorithm performs its intended purpose is directly related to the data on which it is trained. These data not only constitute the inputs of the algorithm, they are also capable of altering the structure and process of the algorithm itself.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0484.json`

### Note `e0485` — `miss`

- note_case_id: `value_of_others_private_en__value_of_others_private_en_personal_notes__e0485`
- target note:
```text
The first reason is related to the quantity of our training data. If each of our valuation algorithms for sexual relationships is principally trained on data collected from just one relationship, then our algorithms will be unduly biased by the idiosyncratic features of that relationship.
```
- target source span(s):
  - `p77@0-289`: The first reason is related to the quantity of our training data. If each of our valuation algorithms for sexual relationships is principally trained on data collected from just one relationship, then our algorithms will be unduly biased by the idiosyncratic features of that relationship.
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0485.json`

## Reading Timeline: All Visible Reactions

Every visible reaction in this Eval-1 window is listed in reading order. Fields are conditional: callback/FVI details appear only when the audit found a callback claim; Selective Legibility details appear only when the reaction overlapped a dataset note target.

### Reaction 001 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p4@516:discern:1`
- source span: `src:c1:p4@0-p4@37`
- source span excerpt:
```text
People want things from other people.
```
- visible reaction:
```text
The opening line is deliberately blunt. No softening, no qualification. It establishes the transactional premise as self-evident.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0001` / note `value_of_others_private_en_personal_notes__e0001` / label `miss` / best `false` / recall-credit `false`
    - target span(s): `p4@0-516` People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a poten…
    - target note: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which…
    - source-span relation: `note_contains_candidate`; coverage `0.07`
    - judge/runner reason: The reaction's quoted span (the opening sentence only) represents only 7.17% of the note's source span and captures none of the note's substantive content. The reaction observes that the opening line is 'blunt' and establishes a 'transactional premise,' but the note's meaningful content lies in its exploration of other people as both solutions AND problems based on whether they have and will share what we want. The reaction engages with the note's style rather than its substance, making the coverage incidental rather than genuine.
    - reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0001.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0126` / note `value_of_others_private_en_personal_notes__e0126` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p4@0-37` People want things from other people.
    - target note: People want things from other people.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0126.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0439` / note `value_of_others_private_en_personal_notes__e0439` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p4@0-37` People want things from other people.
    - target note: People want things from other people.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0439.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0440` / note `value_of_others_private_en_personal_notes__e0440` / label `miss` / best `false` / recall-credit `false`
    - target span(s): `p4@0-516` People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a poten…
    - target note: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which…
    - source-span relation: `note_contains_candidate`; coverage `0.07`
    - judge/runner reason: The reaction quotes only the first sentence (37 chars) of the note's 516-character span. While it characterizes the opening as 'deliberately blunt' and establishing a 'transactional premise,' it does not engage with the note's substantive argument about the dual nature of others as both potential solutions and problems. The reaction captures only a fragment of the note without covering its core content.
    - reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0440.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 002 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p4@516:discern:2`
- source span: `src:c1:p4@452-p4@516`
- source span excerpt:
```text
other people are typically a problem until they prove otherwise.
```
- visible reaction:
```text
The closing sentence lands harder than the symmetry that precedes it. This inverts the social norm of assumed goodwill and replaces it with a skeptical default. Worth tracking whether this framing holds or gets complicated as the book develops.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0001` / note `value_of_others_private_en_personal_notes__e0001` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p4@0-516` People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a poten…
    - target note: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which…
    - source-span relation: `note_contains_candidate`; coverage `0.12`
    - judge/runner reason: The reaction's quoted span (the closing sentence about other people being a problem until they prove otherwise) captures the note's key insight and thesis. The reaction directly engages with this content, interpreting it as an 'inversion of social norm of assumed goodwill' and considering its broader implications for the book's development, indicating substantive engagement with the note's core argument rather than incidental coverage.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0001.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0440` / note `value_of_others_private_en_personal_notes__e0440` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p4@0-516` People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a poten…
    - target note: People want things from other people. This is why other people represent both a potential solution and a potential problem. They are a potential solution when they have the things we want and are willing to give them to us. On the other hand, they are a potential problem when they don’t have the things we want – or when they do have them but won’t give them to us. And it’s far from straightforward to determine which…
    - source-span relation: `note_contains_candidate`; coverage `0.12`
    - judge/runner reason: The reaction explicitly anchors on the closing sentence of the source span and engages substantively with its meaning—specifically how it 'inverts the social norm of assumed goodwill' into a skeptical default. While the note covers broader themes (others as both solution and problem), the reaction genuinely engages with the core claim captured in the overlapped source text and offers interpretive analysis about its rhetorical effect and significance for reading forward.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0440.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 003 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p5@0-p7@754:discern:3`
- source span: `src:c1:p7@639-p7@754`
- source span excerpt:
```text
This is why people who want the same things are generally useless to each other: each lacks what the other desires.
```
- visible reaction:
```text
This tightens the transactional logic from the previous unit. Exchange works not despite divergence but because of it. The double meaning of 'want' makes this feel almost definitional rather than empirical — a structural necessity, not a contingent social fact.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0129` / note `value_of_others_private_en_personal_notes__e0129` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p7@639-754` This is why people who want the same things are generally useless to each other: each lacks what the other desires.
    - target note: This is why people who want the same things are generally useless to each other: each lacks what the other desires .
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0129.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0443` / note `value_of_others_private_en_personal_notes__e0443` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p7@639-754` This is why people who want the same things are generally useless to each other: each lacks what the other desires.
    - target note: This is why people who want the same things are generally useless to each other: each lacks what the other desires .
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0443.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 004 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p5@0-p7@754:highlight:4`
- source span: `src:c1:p7@0-p7@158`
- source span excerpt:
```text
Now, these terms can trip people up. Because of the language involved, many believe that anything prosocial must be good, and anything antisocial must be bad.
```
- visible reaction:
```text
This is the explicit defusing move. The author preemptively blocks the moral reading. Worth tracking whether the text ever partially rehabilitates 'prosocial' or keeps it purely instrumental throughout.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 005 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p8@0-p9@894:discern:5`
- source span: `src:c1:p8@583-p8@717`
- source span excerpt:
```text
It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
```
- visible reaction:
```text
This is the most explicit moral inversion in the text so far. The author directly names and dismisses the intuitive moral reading — that goodness, love, or virtue would be the attractive qualities — and replaces it with pure functional desire. The sentence structure (neither...nor...nor...but) performs the rejection structurally, not just logically.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0132` / note `value_of_others_private_en_personal_notes__e0132` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p8@505-717` why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
    - target note: why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
    - source-span relation: `note_contains_candidate`; coverage `0.63`
    - judge/runner reason: The reaction's quoted span captures the central claim of the note—the moral inversion where neither goodness, love, nor virtue but functional desire drives relationships—and the reaction's analysis of the 'neither...nor...nor...but' structural rejection directly engages with the note's core argument. While the reaction omits the introductory question about why some people are rich in relationship opportunities, the substantive philosophical claim it addresses is the most important content of the note.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0132.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0446` / note `value_of_others_private_en_personal_notes__e0446` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p8@505-717` why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
    - target note: why certain people are rich in relationship opportunities and others are not. It is neither the good nor the loving nor the virtuous who are desired for relationships, but the people whom others want things from.
    - source-span relation: `note_contains_candidate`; coverage `0.63`
    - judge/runner reason: The reaction's quoted span (the 'neither...nor...but' sentence about functional desire) captures the core insight of the note—that moral virtues are replaced by utility as the basis for relationship desirability. Though it covers only the second half of the note's span (char 583-717 vs. the note's 505-717), the reaction's analytical focus on the moral inversion and structural dismissal of virtue aligns with the note's central thesis.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0446.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 006 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p8@0-p9@894:discern:6`
- source span: `src:c1:p9@757-p9@894`
- source span excerpt:
```text
In general, people feel relatively disinterested until they perceive that someone has something they want: either to acquire or to avoid.
```
- visible reaction:
```text
The 'acquire or avoid' binary is reductive but consistent with the book's structural approach. It frames all motivation in transactional terms — nothing beyond wanting to gain or wanting to escape. Worth tracking whether this binary ever gets complicated or if depth, meaning, or non-instrumental connection can exist within this framework.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 007 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p10@661:discern:7`
- source span: `src:c1:p10@151-p10@376`
- source span excerpt:
```text
anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships
```
- visible reaction:
```text
This is the hardest-line exclusion in the book so far. Freely given gifts with no expectation of return are ruled out as relationship grounds. The logic is consistent — no transactability, no relationship — but it feels like a provocative claim about generosity. Does this mean genuine kindness, unconditional support, or grace cannot build relationships within this framework?
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0135` / note `value_of_others_private_en_personal_notes__e0135` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p10@132-377` On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
    - target note: On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
    - source-span relation: `note_contains_candidate`; coverage `0.92`
    - judge/runner reason: The reaction's quoted span overlaps almost entirely with the note's text (0.9184 coverage), capturing the core claim about gifts without transactability being excluded from relationship foundations. The reaction directly engages with this specific argument—identifying it as a 'hardest-line exclusion,' acknowledging the internal logic, and raising a substantive philosophical challenge about whether unconditional generosity can exist within this framework. The focus is tightly on the note's essential content, not tangential.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0135.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0449` / note `value_of_others_private_en_personal_notes__e0449` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p10@132-377` On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
    - target note: On the other hand, anything that can neither be bought nor earned – gifts that are given solely at the pleasure of the giver (and for which no reciprocity is expected) – cannot be transacted, and therefore do not form the basis of relationships.
    - source-span relation: `note_contains_candidate`; coverage `0.92`
    - judge/runner reason: The reaction directly engages with the core claim of the note—that gifts with no transactability cannot form relationships—and substantively engages with the logic ('no transactability, no relationship') while raising probing questions about its implications for generosity and kindness. The quoted span covers the essential content of the note and the reaction is clearly focused on analyzing this specific exclusion rather than merely referencing it.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0449.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 008 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p10@661:discern:8`
- source span: `src:c1:p10@629-p10@661`
- source span excerpt:
```text
Relationships must go both ways.
```
- visible reaction:
```text
The closing line is the thesis compressed. It follows directly from the examples and lands as a clean structural rule — not a normative statement about what relationships ought to be, but a definitional claim about what counts.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0137` / note `value_of_others_private_en_personal_notes__e0137` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p10@629-661` Relationships must go both ways.
    - target note: Relationships must go both ways.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0137.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0451` / note `value_of_others_private_en_personal_notes__e0451` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p10@629-661` Relationships must go both ways.
    - target note: Relationships must go both ways.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0451.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 009 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p11@0-p11@916:discern:9`
- source span: `src:c1:p11@356-p11@423`
- source span excerpt:
```text
this valuation typically occurs beneath the threshold of awareness.
```
- visible reaction:
```text
The unconscious-valuation point extends the earlier exclusion of non-transactable gifts. If people don't fully know their own valuations, even 'spontaneous' generosity or liking may be driven by processes below awareness. This feels like a foundational claim for the book's model.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly references 'earlier exclusion of non-transactable gifts' from reaction 7, extending that concept to the unconscious-valuation point.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 010 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p12@0-p12@531:discern:10`
- source span: `src:c1:p12@399-p12@531`
- source span excerpt:
```text
we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
```
- visible reaction:
```text
This is the book's most refined definition so far. 'Unequal goods' means the items differ (not a barter of identical objects), while 'comparable value' means both parties perceive similar worth. The asymmetry is in the goods; the symmetry is in the value. This is the mechanism that allows exchange to benefit both parties even when what they receive is fundamentally different.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0140` / note `value_of_others_private_en_personal_notes__e0140` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p12@386-531` As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
    - target note: As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
    - source-span relation: `note_contains_candidate`; coverage `0.91`
    - judge/runner reason: The reaction's quoted span nearly matches the note (91% overlap), and the reaction's explanatory content is tightly focused on interpreting the key terms 'unequal goods' and 'comparable value' within the source span. The reaction genuinely engages with the refined definition rather than treating it as incidental context.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0140.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0454` / note `value_of_others_private_en_personal_notes__e0454` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p12@386-531` As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
    - target note: As a result, we can refine our definition of relationships even further to be the media in which unequal goods of comparable value are exchanged.
    - source-span relation: `note_contains_candidate`; coverage `0.91`
    - judge/runner reason: The reaction's source span covers 91% of the note's text, and the content directly unpacks the core concepts ('unequal goods' and 'comparable value') and explains the mechanism the definition describes. The reaction is tightly focused on explaining the specific phrase 'unequal goods of comparable value are exchanged' rather than being tangential to it.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0454.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 011 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p13@0-p13@543:discern:11`
- source span: `src:c1:p13@479-p13@543`
- source span excerpt:
```text
Different types of relationships must be negotiated differently.
```
- visible reaction:
```text
This closes the paragraph as a clean structural rule, completing the thought that began with the unequal-subjective premise. It extends the transactional model from mechanism (what is exchanged) into form (how it is acknowledged), but doesn't add a new concept — it maps existing relationship types onto the framework.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Uses vague phrase 'unequal-subjective premise' that doesn't clearly map to any specific earlier visible reaction, making the linkage partial and unsupported.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 012 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p14@0-p15@559:discern:12`
- source span: `src:c1:p14@475-p14@616`
- source span excerpt:
```text
the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.
```
- visible reaction:
```text
This adds a crucial layer to the transactional model — not just that value is exchanged, but that the exchange must be hidden. Relationships work partly because the negotiation itself stays invisible. This extends beyond the 'beneath awareness' point from earlier: it's not only that valuations are unconscious, it's that the whole transaction is socially forbidden from being explicit.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly extends from the 'beneath awareness' point (referencing reaction 9's unconscious-valuation discussion) and adds the concept of socially forbidden explicit negotiation.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 013 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p16@0-p16@1015:discern:13`
- source span: `src:c1:p16@260-p16@574`
- source span excerpt:
```text
If the goods are the same, then exchange is either unnecessary or impossible (so no relationship is formed). And if their values are too disparate, then the relationship becomes likely in inverse proportion to the size of the perceived mismatch in value: the greater the mismatch, the less likely the relationship.
```
- visible reaction:
```text
This is a clean two-boundary theorem for relationship formation. Too symmetric (identical goods) → no transaction. Too asymmetric (disparate values) → relationship probability decreases. Only the narrow middle band — unequal goods, comparable value — sustains the exchange. This extends the earlier 'unequal goods of comparable value' definition into a generative condition with failure modes.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly extends the 'unequal goods of comparable value' definition from reaction 10, applying it as a generative condition with named failure modes.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 014 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p16@0-p16@1015:discern:14`
- source span: `src:c1:p16@791-p16@896`
- source span excerpt:
```text
awareness of this violation can lead to a great deal of pain and distress for the under-compensated party
```
- visible reaction:
```text
This is the key consequence clause. The pain isn't automatic — it requires awareness. Someone operating with a stale mismatch perception feels fine until the other party's shifted valuation becomes visible. The distress is a function of the recognition, not the mismatch itself.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 015 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p17@0-p17@961:discern:15`
- source span: `src:c1:p17@810-p17@961`
- source span excerpt:
```text
If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
```
- visible reaction:
```text
The exit condition is now formalized as a law: insufficient payoff (or reverse payoff) triggers withdrawal. This completes the game-theoretic frame — not just the structure of play, but the conditions under which play ends.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0144` / note `value_of_others_private_en_personal_notes__e0144` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p17@810-961` If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
    - target note: If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0144.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0458` / note `value_of_others_private_en_personal_notes__e0458` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p17@810-961` If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
    - target note: If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0458.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 016 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p18@0-p18@875:discern:16`
- source span: `src:c1:p18@0-p18@111`
- source span excerpt:
```text
Every type of relationship constitutes a different game – as does every specific relationship of the same type.
```
- visible reaction:
```text
This opens the nesting cleanly: two layers of differentiation — by type and by individual instance within the type. The dash construction makes both claims land in one breath.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0145` / note `value_of_others_private_en_personal_notes__e0145` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p18@0-111` Every type of relationship constitutes a different game – as does every specific relationship of the same type.
    - target note: Every type of relationship constitutes a different game – as does every specific relationship of the same type.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0145.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0459` / note `value_of_others_private_en_personal_notes__e0459` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p18@0-111` Every type of relationship constitutes a different game – as does every specific relationship of the same type.
    - target note: Every type of relationship constitutes a different game – as does every specific relationship of the same type.
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0459.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 017 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p18@0-p18@875:discern:17`
- source span: `src:c1:p18@698-p18@875`
- source span excerpt:
```text
And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.
```
- visible reaction:
```text
The nesting concept is the structural payoff here. An "overarching category" that contains enormous variation — this is the fractal property of the framework. It also quietly explains why category-level generalizations about relationship behavior are always unstable.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 018 — `false_visible_integration` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p19@0-p19@794:retrospect:18`
- source span: `src:c1:p19@502-p19@591`
- source span excerpt:
```text
the truer these principles are, the more abstract and unsatisfying they are likely to be.
```
- visible reaction:
```text
This is the core concession of the book so far — a direct acknowledgment that the framework's rigor comes at the cost of practical specificity. Principles that survive contact with individual variation become too thin to act on.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `false_visible_integration`
  - prior_link: `{"ref_ids": ["active_attention:nested-game-structure"]}`
  - judge reason: The compat_type is 'retrospect' and prior_link points to 'active_attention:nested-game-structure', but no earlier visible reaction in this window contains that specific ref_id or explicitly surfaces the concession being referenced. The link connects to something outside the visible evidence surface.
  - reviewer interpretation: rejected visible integration; the reaction claims a connection the visible evidence surface does not support.

### Reaction 019 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p20@0-p20@737:highlight:19`
- source span: `src:c1:p20@31-p20@430`
- source span excerpt:
```text
On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level.
```
- visible reaction:
```text
The two-horned structure is the structural heart here. The first horn (specificity → validity loss) and the second horn (generality → utility loss) are presented as true mirrors, not as uneven trade-offs. This framing makes the dilemma feel like a genuine constraint rather than a rhetorical concession.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0146` / note `value_of_others_private_en_personal_notes__e0146` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p20@31-561` On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make…
    - target note: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the hig…
    - source-span relation: `note_contains_candidate`; coverage `0.75`
    - judge/runner reason: The reaction's quoted span captures the core two-horn structure (specificity→validity loss and generality→utility loss) which is the essential analytical content of the note. The reaction's commentary focuses specifically on this structural symmetry rather than tangential content, making it a focused engagement with the overlapped source span.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0146.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0460` / note `value_of_others_private_en_personal_notes__e0460` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p20@31-561` On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make…
    - target note: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the hig…
    - source-span relation: `note_contains_candidate`; coverage `0.75`
    - judge/runner reason: The reaction's source span covers the core two-horned dilemma (specificity→validity loss and generality→utility loss) that is the central argument of the note. The reaction explicitly analyzes this structural framing, identifying the 'two-horned structure' as the 'structural heart' and explaining how the symmetrical presentation makes the trade-off 'feel like a genuine constraint.' This directly engages with the note's substantive content rather than incidental coverage.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0460.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 020 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p20@0-p20@737:discern:20`
- source span: `src:c1:p20@431-p20@561`
- source span excerpt:
```text
This is why the highest wisdom can often sound so vague and idiotic, while detailed advice can be so contentious and inapplicable.
```
- visible reaction:
```text
The word 'idiotic' lands hard — it doesn't soften the failure mode but names it unflinchingly. The symmetry of 'vague and idiotic' against 'contentious and inapplicable' treats both failure modes as equally real and equally embarrassing, which is unusual honesty for a book that is itself trying to navigate this terrain.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0146` / note `value_of_others_private_en_personal_notes__e0146` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p20@31-561` On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make…
    - target note: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the hig…
    - source-span relation: `note_contains_candidate`; coverage `0.25`
    - judge/runner reason: The reaction quotes and analyzes the last sentence of the note, discussing the rhetorical force of 'idiotic' and the symmetry of the failure modes. However, the note's important content is the substantive trade-off argument about specificity at category vs individual level—the reaction focuses narrowly on the concluding sentence's stylistic impact rather than engaging with the core argument about validity/reliability versus practicality/actionability.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0146.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0460` / note `value_of_others_private_en_personal_notes__e0460` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p20@31-561` On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make…
    - target note: On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level. This is why the hig…
    - source-span relation: `note_contains_candidate`; coverage `0.25`
    - judge/runner reason: The reaction's quoted span (the final sentence about wisdom sounding vague/idiotic and advice being contentious/inapplicable) is contained within the note, but the note's core intellectual contribution is the full trade-off argument about specificity versus validity/reliability versus practicality. The reaction only comments on the rhetorical finish—the word choice and symmetry of the failure modes—rather than engaging with the substantive trade-off mechanism that the note establishes and then illustrates. The overlapping portion is incidental to the note's main thrust.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0460.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 021 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p22@0-p23@663:discern:21`
- source span: `src:c1:p23@468-p23@663`
- source span excerpt:
```text
And if people enter into (and remain in) sexual relationships with their perceived best options, then the perception of value must be the mechanism that lies at the heart of sexual relationships.
```
- visible reaction:
```text
The pivot from "perceived" to "perception of value" is the book's key move in this unit — not what is actually valuable, but what is perceived as valuable. This is where the framework becomes distinctively about subjective evaluation rather than objective exchange.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 022 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p24@0-p26@122:discern:22`
- source span: `src:c1:p25@500-p25@662`
- source span excerpt:
```text
And since the model can explain emotions (but emotions cannot explain the model), this means that the model is more fundamentally true and should take precedence.
```
- visible reaction:
```text
The reversibility test as epistemic arbiter: the model's ability to explain its own inputs makes it more fundamental than those inputs. This subordinates emotion to the economic framework rather than placing them in parallel — a strong asymmetric move that runs counter to most popular relationship writing.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 023 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p24@0-p26@122:discern:23`
- source span: `src:c1:p26@0-p26@122`
- source span excerpt:
```text
To understand why this is the case, we need to take a closer look at the concept of value: what it is and how it operates.
```
- visible reaction:
```text
The pivot is the book's own explicit roadmap for what comes next. The 'why this is the case' directly references the priority claim just made, signaling that the value-examination is not a digression but the infrastructure supporting it.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 024 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p27@0-p28@512:discern:24`
- source span: `src:c1:p27@0-p27@21`
- source span excerpt:
```text
The covert calculator
```
- visible reaction:
```text
The section heading earns its weight through the 'covert' qualifier — it reaches back to the earlier 'covert transaction' framing and recasts the individual as an internal calculator operating beneath the surface of social interaction. This is not a metaphor; it is the mechanism's name.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: The 'covert' qualifier explicitly reaches back to the 'covert transaction' framing from reactions 12 and 13, grounding the current section heading's mechanism in earlier visible material. The callback is specific and correctly cross-referenced.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 025 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p27@0-p28@512:discern:25`
- source span: `src:c1:p28@463-p28@510`
- source span excerpt:
```text
resources – once expended – cannot be refunded.
```
- visible reaction:
```text
This ties directly to the irreversibility thread. Since resources cannot be recovered, the valuation at the point of transaction is structurally locked in — which means pain from perceived under-compensation follows necessarily from this non-recoverability.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0149` / note `value_of_others_private_en_personal_notes__e0149` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p28@296-510` Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
    - target note: Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
    - source-span relation: `note_contains_candidate`; coverage `0.22`
    - judge/runner reason: The reaction explicitly quotes and builds upon the core claim about resource non-recoverability ('resources – once expended – cannot be refunded'), extending it to a theoretical point about valuation being 'structurally locked in.' The reaction is tightly focused on this specific claim rather than the broader paragraph, making it a purposeful engagement with the note's key content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0149.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0463` / note `value_of_others_private_en_personal_notes__e0463` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p28@296-510` Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
    - target note: Time, effort, attention, and opportunity (among others) are all forms of resources. These resources must be expended both to acquire and to retain valuable goods, and resources – once expended – cannot be refunded.
    - source-span relation: `note_contains_candidate`; coverage `0.22`
    - judge/runner reason: The reaction's source span (47 characters) covers only the final clause of the note about non-recoverability of expended resources, while the note's opening claim—that time, effort, attention, and opportunity are forms of resources—goes entirely uncovered. The reaction interprets and extends the non-recoverability concept into valuation locking and psychological pain, which is thoughtful but the quote itself is narrow relative to the note's full scope.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0463.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 026 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p29@0-p29@565:discern:26`
- source span: `src:c1:p29@325-p29@447`
- source span excerpt:
```text
At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved.
```
- visible reaction:
```text
This is the direct answer to the value-examination promised at paragraph 26. Not a metaphor or analogy — the definition of value itself is scarcity-derived. It connects back to the irreversibility claim in paragraph 28: since resources cannot be refunded, scarcity is structural, not incidental.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0151` / note `value_of_others_private_en_personal_notes__e0151` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p29@325-565` At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - target note: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - source-span relation: `note_contains_candidate`; coverage `0.51`
    - judge/runner reason: The reaction's quoted span captures only the first sentence about scarcity creating value while omitting the Greek mythology example that serves as the note's key illustrative support. Although the reaction's commentary is focused on the scarcity-value connection, the intentional exclusion of the mythological elaboration suggests the note's full important content is not being addressed.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0151.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0465` / note `value_of_others_private_en_personal_notes__e0465` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p29@325-565` At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - target note: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - source-span relation: `note_contains_candidate`; coverage `0.51`
    - judge/runner reason: The reaction's quoted span covers only the first sentence of the note (scarcity creates value), and its content correctly identifies this as a core definition. However, the note's important content includes the mythological example about gods envying mortal mortality—this second part is completely unaddressed by the reaction. The reaction treats the passage as a standalone definition without engaging the illustrative reasoning that completes the note's argument. The 50.83% coverage, while substantial, leaves out a meaningful portion of the note's key content.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0465.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: References the internal text structure ('promised at paragraph 26,' 'irreversibility claim in paragraph 28') and a general connection to the 'reversibility test' in reaction 22, but these are structural cross-references within the segment rather than grounded callbacks to previously surfaced visible content.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 027 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p29@0-p29@565:discern:27`
- source span: `src:c1:p29@448-p29@565`
- source span excerpt:
```text
This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
```
- visible reaction:
```text
The rhetorical inversion here is striking — mortality framed as the source of envy rather than deprivation. It restates the scarcity-value thesis in mythological dress and provides the paragraph's emotional anchor.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0151` / note `value_of_others_private_en_personal_notes__e0151` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p29@325-565` At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - target note: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - source-span relation: `note_contains_candidate`; coverage `0.49`
    - judge/runner reason: The reaction's quoted span (the mythological sentence) covers about half of the note's span, but the note's important content includes the foundational scarcity-value thesis in the first sentence. The reaction focuses primarily on the rhetorical effect ('rhetorical inversion,' 'emotional anchor') of the mythological framing rather than engaging substantively with the core economic concept that scarcity produces value. While the reaction briefly mentions 'the scarcity-value thesis,' its analysis treats the Greek mythology example as a literary device rather than as evidence for the central argument about scarcity creating value through limited resources.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0151.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0465` / note `value_of_others_private_en_personal_notes__e0465` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p29@325-565` At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - target note: At the most basic level, the scarcity produced by our limited resources is what creates value to the individuals involved. This is essentially why the gods in Greek mythology envied man: mortality (i.e., scarce time) made his life valuable.
    - source-span relation: `note_contains_candidate`; coverage `0.49`
    - judge/runner reason: The reaction's quoted span covers only the second half of the note (the Greek mythology example about gods envying mortal man's scarce time), which represents roughly half of the note's content. While the reaction mentions the 'scarcity-value thesis,' it treats it as merely 'restated' in mythological dress rather than engaging with the note's primary claim that scarcity produces value at a basic level. The note's fundamental argument about scarcity creating value is referenced but not genuinely addressed; only the illustrative example is analyzed.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0465.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 028 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p31@0-p33@1131:retrospect:28`
- source span: `src:c1:p33@19-p33@195`
- source span excerpt:
```text
nesting games will always take precedence over nested games whenever we become aware of new information that affects the acquisition (or maintenance) of the superordinate game.
```
- visible reaction:
```text
This is the sharpest rule-formulation yet. It restates the nested-game structure from paragraph 18 with a specific operative principle attached: not just that games nest, but that they compete for precedence based on information-driven relevance. The asymmetry is directional — nesting always wins.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:nested-game-structure"]}`
  - judge reason: Explicitly and correctly references the 'nested-game structure' from reaction 18 by prior_link ref_id, and correctly identifies it as being restated with a new operative principle here. The callback is specific and substantively grounded.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 029 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p31@0-p33@1131:highlight:29`
- source span: `src:c1:p33@584-p33@897`
- source span excerpt:
```text
People might scoff at paying ten dollars for a bottle of water – but a man dying of thirst would be willing to pay a great deal more. But he will likely not be willing to pay as much for a second bottle, as the new information provided by his body will tell him that his need is now not quite so great and urgent.
```
- visible reaction:
```text
The second-bottle clause is doing real work here — it shows that the mechanism is not just about different people valuing the same good differently, but about the same person updating their valuation in real time as information arrives. This directly answers the question of how value becomes dynamic rather than static.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 030 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p35@1132:discern:30`
- source span: `src:c1:p34@600-p34@717`
- source span excerpt:
```text
This output is also calculated anew hundreds of times every second for an uncountable number of goods simultaneously.
```
- visible reaction:
```text
The scale claim is striking — not that valuation is complex, but that it is continuous and parallel. This reframes value determination from a discrete decision event to a constant computational flood. It makes the "opaque" quality mentioned earlier even more structurally inevitable: if this process is running beneath awareness across uncountable goods at hundreds of times per second, neither party can realistically track what the other is doing.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Vaguely references 'opaque' and 'beneath awareness' concepts that appear to derive from earlier visible material (reaction 12's 'hidden negotiation,' reaction 24's 'beneath the surface'), but the linkage is implied rather than explicit and lacks specific grounding.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 031 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p35@1132:discern:31`
- source span: `src:c1:p35@746-p35@976`
- source span excerpt:
```text
We execute these evaluations using many different cognitive processes that utilize information from the present and the subjective past (e.g., perception, memory) to predict an outcome in the subjective future (e.g., imagination).
```
- visible reaction:
```text
This temporal triad — present + subjective past → subjective future — is the operational core of how valuation actually works. It extends the earlier epistemic-opacity concept: if the future is always subjectively constructed via imagination, then the gap between actual and perceived value is not incidental but structural.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: References 'epistemic-opacity concept' which appears to connect to earlier discussion of unconscious valuation and hidden transactions, but the linkage is general rather than specific and the connection to visible earlier content is implied, not confirmed.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 032 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p36@0-p36@1007:discern:32`
- source span: `src:c1:p36@350-p36@576`
- source span excerpt:
```text
the principles of valuation are like the principles of logic: they do not change from place to place or moment to moment. What’s more, neither can be empirically proven: we just somehow perceive them to be self-evidently true.
```
- visible reaction:
```text
This analogy is the passage's strongest structural move. By placing valuation on the same footing as logic—universal, not empirically demonstrable, yet self-evidently true—the author is claiming something foundational about human cognition, not merely something about economic behavior. The double 'neither can be empirically proven' / 'self-evidently true' pair is doing the heavy lifting.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 033 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p37@0-p38@1156:discern:33`
- source span: `src:c1:p38@366-p38@680`
- source span excerpt:
```text
We can call this output the value coefficient of a particular good. It represents how valuable an individual perceives a specific good to be at a distinct moment in time. The higher the value of a coefficient associated with a specific good, the more valuable a particular individual will perceive that good to be.
```
- visible reaction:
```text
This is the book's first explicit named variable. The value coefficient is not a metaphor but a functional label for the covert calculator's output — a single numerical representation of perceived value at a given moment, subject to continuous recalculation. The structural force: it makes the earlier 'unconscious' and 'hundreds of times per second' claims concrete and measurable.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: The reaction references 'unconscious' (supported by earlier 'covert' and 'beneath awareness' language in reactions 24-25) and links to computational frequency claims from reaction 30, but the specific phrase 'hundreds of times per second' does not appear in visible prior material. The callback is partial and relies on thematic rather than explicit structural grounding.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 034 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p40@0-p41@710:highlight:34`
- source span: `src:c1:p41@379-p41@710`
- source span excerpt:
```text
the calculated value coefficient is transformed into an emotion. This emotion contains the personally relevant significance of the value coefficient, and it transmits this significance in a manner that (typically) prevents individuals from being overwhelmed with unnecessary information and can motivate them into immediate action.
```
- visible reaction:
```text
This is the book's central mechanism: emotion is not raw feeling but a translated readout of unconscious value calculation. The value coefficient (from earlier) is the input; the felt emotion is the output. This directly answers how a process that must stay hidden produces a usable conscious signal.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0157` / note `value_of_others_private_en_personal_notes__e0157` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p41@379-443` the calculated value coefficient is transformed into an emotion.
    - target note: the calculated value coefficient is transformed into an emotion.
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction directly engages with the note's core concept—the transformation of the value coefficient into emotion—interpreting and expanding on it as the book's central mechanism. The quoted source span begins with the exact note text and extends naturally to explain the significance and function of this transformation.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0157.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0471` / note `value_of_others_private_en_personal_notes__e0471` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p41@379-443` the calculated value coefficient is transformed into an emotion.
    - target note: the calculated value coefficient is transformed into an emotion.
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction's quoted source span contains the entire note text, and the reaction content directly engages with and elaborates the note's core claim: that a calculated value coefficient is transformed into an emotion, explaining it as the book's central mechanism where unconscious value calculations become conscious emotional readouts.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0471.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Directly references the value coefficient from reaction 33 (the immediately preceding reaction in this batch) and explicitly maps the mechanism: value coefficient → emotional readout. This is the first clear intra-batch callback showing how the named variable functions operationally.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 035 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p40@0-p41@710:discern:35`
- source span: `src:c1:p41@193-p41@310`
- source span excerpt:
```text
How can people be meaningfully made aware of the output of a process of which they must remain functionally ignorant?
```
- visible reaction:
```text
This framing question captures the whole problem the book is solving. It sets up the emotion-as-translator answer with precision, and it connects back to the earlier epistemic-opacity concept — we are functionally ignorant of the process AND we are functionally ignorant that we are performing calculations at all.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly names 'epistemic-opacity' which appears verbatim in reaction 30. The framing question directly connects to the problem statement established in reaction 34 (emotion as translator) and to the earlier functional-ignorance framing in reaction 35. Clean callback chain.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 036 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p42@0-p42@987:discern:36`
- source span: `src:c1:p42@550-p42@677`
- source span excerpt:
```text
The feelings behind these statements accomplish the same goal more elegantly than awareness of the valuation process ever could
```
- visible reaction:
```text
The 'more elegantly' qualifier does real work here. Earlier material established that emotion transforms the value coefficient as a functional necessity. This unit goes further—it claims the emotional channel is not just a workaround for unconscious opacity but a superior method. Conscious awareness of the full valuation calculus would be epistemically accurate but behaviorally clumsy; emotion is elegant precisely because it condenses the signal down to what drives action. This upgrades the emotion-as-translator concept from necessity to optimization.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Correctly identifies that this passage upgrades the 'emotion-as-translator' concept from necessity (reaction 35) to optimization ('more elegantly'). The claim that the emotional channel is 'not just a workaround but a superior method' has visible grounding in the prior reactions on the mechanism, making the upgrade claim traceable.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 037 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p42@0-p42@987:discern:37`
- source span: `src:c1:p42@795-p42@987`
- source span excerpt:
```text
this communication is extremely useful because it is constituted by behavioral impulses that motivate action in alignment with this valuation: to approach, to acquire, to protect, to maintain.
```
- visible reaction:
```text
The word 'constituted' is precise: feelings are not merely accompanied by impulses but made of them. This tightens the mechanism—valuation flows into emotion, and emotion is already structured as action-readiness. The four verbs (approach, acquire, protect, maintain) map onto the behavioral register the value coefficient needs to express.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 038 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p44@0-p46@455:discern:38`
- source span: `src:c1:p46@388-p46@454`
- source span excerpt:
```text
value is always assessed in relation to a personally relevant goal
```
- visible reaction:
```text
This is the clean resolution to the unsettled/contention tension — reframing value from an absolute property to a goal-relative one. It defuses the moral discomfort by shifting the question from 'are some people more valuable?' to 'valuable for what purpose?' Worth remembering as a key conceptual hinge the book has been building toward.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 039 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p48@0-p49@568:discern:39`
- source span: `src:c1:p49@285-p49@460`
- source span excerpt:
```text
one of our most common decision-making heuristics is to (often unconsciously) determine the perceived goodness of fit between any specific candidate and its relevant exemplar.
```
- visible reaction:
```text
The goodness-of-fit heuristic operationalizes the exemplar concept—this is how the template actually works in practice. 'Often unconsciously' keeps the epistemic-opacity theme alive. The heuristic is framed as practical necessity (thorough examination is time-consuming and prohibitively expensive), which suggests the template shortcut isn't just cognitive convenience but a structural adaptation.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 'Exemplar concept' and 'template shortcut' are named without prior grounding in the visible reactions. The epistemic-opacity theme (reaction 30) provides partial support, but the specific 'goodness-of-fit heuristic' terminology and the 'practical necessity' / 'structural adaptation' characterization lack visible anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 040 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p50@0-p50@576:discern:40`
- source span: `src:c1:p50@523-p50@574`
- source span excerpt:
```text
provided we weren’t under an urgent time constraint
```
- visible reaction:
```text
This qualifier is the model's pressure point: when urgency overrides importance, the threshold logic inverts. The book has been building a clean, rational model of value-based selection — this parenthetical quietly acknowledges that real conditions often sabotage it.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Thematic continuity exists with the book's broader modeling approach, but 'urgency overrides importance' and 'threshold logic' are not named in earlier visible reactions. The claim that the parenthetical 'quietly acknowledges' a sabotage of the model lacks explicit visible grounding.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 041 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p51@0-p52@626:discern:41`
- source span: `src:c1:p52@561-p52@626`
- source span excerpt:
```text
losing that game typically makes it impossible to win the others.
```
- visible reaction:
```text
The 'typically' here does quiet work — the claim isn't absolute. There are edge cases where losing the survival game doesn't preclude other wins, but the qualifier keeps the model tractable. It frames survival priority as a reliable tendency rather than a hard law.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 042 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p53@0-p53@803:discern:42`
- source span: `src:c1:p53@195-p53@289`
- source span excerpt:
```text
an organism that lives to a ripe, old age without reproducing not only dies – it goes extinct.
```
- visible reaction:
```text
The 'goes extinct' formulation is the sharpest reframe in this passage. It collapses the distance between individual death and genealogical erasure, making non-reproduction feel categorically different from ordinary mortality—not just a lesser outcome but a different kind of failure entirely.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 043 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p53@0-p53@803:discern:43`
- source span: `src:c1:p53@538-p53@611`
- source span excerpt:
```text
A mother who dies so her children might live exemplifies this phenomenon.
```
- visible reaction:
```text
The example performs quiet work: it shows that the genetic-survival priority isn't just about unconscious biological imperative but can manifest as conscious sacrifice. This sets up potential tension with the earlier framing of relationship dynamics as transaction-based.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Reaction 43 vaguely mentions 'earlier framing of relationship dynamics as transaction-based' but offers no specific prior citation—only a general thematic reference.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 044 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p54@0-p55@595:discern:44`
- source span: `src:c1:p54@187-p54@251`
- source span excerpt:
```text
the game of games: the game that makes all other games possible.
```
- visible reaction:
```text
The double framing here does quiet work. 'Game of games' elevates the category, then 'the game that makes all other games possible' makes it constitutive rather than merely dominant. This is what allows the text to derive behavioral consequences as logical deductions rather than empirical claims.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0160` / note `value_of_others_private_en_personal_notes__e0160` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p54@0-251` As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
    - target note: As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
    - source-span relation: `note_contains_candidate`; coverage `0.26`
    - judge/runner reason: The reaction's quoted span covers the 'game of games' phrase, which is the note's core conceptual contribution—the distinctive framing that elevates mating/dating from merely dominant to constitutive. Although the note includes the surrounding context about 'nested hierarchy' and ranking, the reaction demonstrates genuine engagement with the note's most substantive idea: the double framing that allows the text to derive behavioral consequences as logical deductions. The analysis is focused and adds interpretive value to the specific span selected.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0160.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0474` / note `value_of_others_private_en_personal_notes__e0474` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p54@0-251` As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
    - target note: As a consequence, the game of mating and dating ranks very highly in most people’s nested hierarchy of games – in many cases, above their own individual survival. In many respects, it is the game of games: the game that makes all other games possible.
    - source-span relation: `note_contains_candidate`; coverage `0.26`
    - judge/runner reason: The reaction's quoted span ('the game of games: the game that makes all other games possible') is contained within the note, and the reaction's analysis directly addresses the core claim of the note—that mating/dating is not just dominant but constitutive of all other games. The reaction explains the rhetorical mechanism ('double framing') that makes this logical move work, which is the substantive insight in the note. While the note's opening clause about 'ranking very highly' and 'above individual survival' isn't quoted, the reaction engages with the most important conceptual content: the game-of-games framing and its implications.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0474.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 045 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p54@0-p55@595:discern:45`
- source span: `src:c1:p55@502-p55@595`
- source span excerpt:
```text
People might balk at this, but no one continues to pay the plumber after the job is finished.
```
- visible reaction:
```text
The 'balk' acknowledges reader resistance upfront, then the plumber line sidesteps the objection by reframing the logic in neutral transactional terms. The analogy applies the framework unflinchingly to sexual relationships—the discomfort is the point.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0161` / note `value_of_others_private_en_personal_notes__e0161` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p55@399-595` After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
    - target note: After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
    - source-span relation: `note_contains_candidate`; coverage `0.47`
    - judge/runner reason: The reaction's quoted span (about balking and post-job payment) intersects with an important part of the note's argument about transactional logic, and the analysis directly addresses the rhetorical strategy within that quoted portion. The commentary engages substantively with the 'balk' language and reframing mechanism present in the overlap, making this focused rather than incidental.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0161.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0475` / note `value_of_others_private_en_personal_notes__e0475` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p55@399-595` After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
    - target note: After all, a plumber is much more valuable to us before he fixes our clog than he is after he does so. People might balk at this, but no one continues to pay the plumber after the job is finished.
    - source-span relation: `note_contains_candidate`; coverage `0.47`
    - judge/runner reason: The reaction's quoted span covers the second half of the note's source text (starting at 'People might balk...'), missing the first half which contains the core claim about the plumber being more valuable before the job is done. While the reaction analyzes the 'balk' and reframing logic, it does not genuinely engage with the note's primary point about relative value before versus after work is performed. The overlap covers only 47% of the note's source span, and the missing portion contains the note's most distinctive claim.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0475.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 046 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p60@0-p62@876:discern:46`
- source span: `src:c1:p62@583-p62@720`
- source span excerpt:
```text
saying people desire a high-value individual is a tautology, as desire is the natural emotional response to the perception of high value.
```
- visible reaction:
```text
The tautology move performs quiet defusing work: it reduces the culturally mystified question 'what makes someone desirable?' to a definitional truth. Nothing to decode or pursue—just the logical structure of the claim itself.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 047 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p60@0-p62@876:retrospect:47`
- source span: `src:c1:p62@810-p62@876`
- source span excerpt:
```text
value and desire are the same thing experienced in different ways.
```
- visible reaction:
```text
This closes the loop opened earlier with 'emotion-as-translator.' Valuation below awareness produces desire above awareness—they are not sequential stages but two registers of a single process.
```
- Selective Legibility dataset relation:
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0167` / note `value_of_others_private_en_personal_notes__e0167` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p62@802-876` because value and desire are the same thing experienced in different ways.
    - target note: because value and desire are the same thing experienced in different ways.
    - source-span relation: `note_contains_candidate`; coverage `0.89`
    - judge/runner reason: The reaction's quoted span (810-876) falls within the note's source span (802-876), and the reaction directly engages with the note's core claim that value and desire are the same thing experienced differently. The reaction builds on this idea by explaining it as 'two registers of a single process,' connecting valuation and desire as simultaneous registers rather than sequential stages.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0167.json`
  - note-case `value_of_others_private_en__value_of_others_private_en_personal_notes__e0481` / note `value_of_others_private_en_personal_notes__e0481` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p62@802-876` because value and desire are the same thing experienced in different ways.
    - target note: because value and desire are the same thing experienced in different ways.
    - source-span relation: `note_contains_candidate`; coverage `0.89`
    - judge/runner reason: The reaction's source span (810-876) overlaps with the note's source span (802-876), and the reaction's commentary directly engages with and elaborates the note's central claim. The content explains the mechanism ('Valuation below awareness produces desire above awareness') and clarifies the relationship ('two registers of a single process'), demonstrating genuine coverage of the note's important content rather than incidental reference.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_value_of_others/note_cases/value_of_others_private_en__value_of_others_private_en_personal_notes__e0481.json`
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:emotion-as-translator"]}`
  - judge reason: Reaction 47 explicitly cites 'concept:emotion-as-translator' via prior_link, correctly linking back to the earlier emotion-as-translator framing from reactions 34-37.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 048 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p66@0-p67@898:discern:48`
- source span: `src:c1:p66@393-p66@473`
- source span excerpt:
```text
the same liability is always less detrimental in the future than in the present.
```
- visible reaction:
```text
The symmetry with benefits (more valuable in the present) makes this precise: it's not that people are irrationally optimistic, it's that future liabilities are genuinely less costly by probability — and that rational discount alone tilts the field.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 049 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p66@0-p67@898:highlight:49`
- source span: `src:c1:p67@283-p67@522`
- source span excerpt:
```text
this positive emotion will reciprocally influence their valuation process in predictable ways, namely: by weighting values associated with current benefits more heavily, and weighting values associated with future liabilities more lightly.
```
- visible reaction:
```text
The feedback loop is the key move: desire doesn't just follow from perception of high value — it then reshapes the valuation itself, making the initial perception self-confirming.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 050 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p68@0-p71@460:retrospect:50`
- source span: `src:c1:p70@256-p70@679`
- source span excerpt:
```text
if the process of determining value is comprised of a countless number of individual evaluations, each associated with a specific weight that attempts to predict the importance of that evaluation to the achievement of a particular goal, and if the valuation process is almost entirely unconscious, then (to a large extent) people will be unaware of precisely what they value and the extent to which they value those things.
```
- visible reaction:
```text
This is the meta-move: not just that desire distorts perception (as established earlier), but that the valuation engine itself runs below the threshold. The person is not merely biased — they are genuinely uninformed about their own architecture.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p60@0-p62@876:retrospect:47"], "note": "extends the earlier 'emotion-as-translator' framing — here the mechanism is not just unconscious but also opaque to introspection"}`
  - judge reason: Reaction 50 explicitly cites reaction 47 via prior_link and extends the emotion-as-translator framing, correctly grounding the callback to the specific earlier visible claim.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 051 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p68@0-p71@460:discern:51`
- source span: `src:c1:p69@0-p69@16`
- source span excerpt:
```text
When models fail
```
- visible reaction:
```text
The section heading signals that the entire preceding framework — the smooth valuation machinery, the reciprocal desire-value loop — has a built-in failure condition. The heading is the announcement, not the content of failure itself.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 052 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p72@0-p72@1002:discern:52`
- source span: `src:c1:p72@883-p72@1002`
- source span excerpt:
```text
people are generally forced into some measure of dissimulation when trying to get what they want from the opposite sex.
```
- visible reaction:
```text
This pushes beyond the earlier 'covert transaction' framing (p14) — which described indirect negotiation as a norm. Now dissimulation is positioned as structurally forced by the game itself, not merely culturally preferred.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Reaction 52 explicitly references 'earlier covert transaction framing (p14)' and correctly grounds the claim that dissimulation is now repositioned as structurally forced rather than merely culturally preferred.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 053 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p73@0-p73@494:discern:53`
- source span: `src:c1:p73@230-p73@363`
- source span excerpt:
```text
what people are attracted to is not always rationally aligned with their best interests (or even their consciously explicated goals).
```
- visible reaction:
```text
This restates the irrationality problem but now from within the unconscious-process frame: it's not just that people make bad choices, it's that the choice machinery generates attractions that bypass the rational faculty entirely.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 054 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p73@0-p73@494:discern:54`
- source span: `src:c1:p73@395-p73@494`
- source span excerpt:
```text
while the valuation process is inherent – the weights and evaluations used in that process are not.
```
- visible reaction:
```text
This is the technical hinge. The process runs on autopilot (inherent), but the evaluation criteria that feed it are not native — they are acquired, cultural, or experiential. That distinction explains why self-knowledge is structurally limited even about one's own desires.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 055 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p74@0-p74@544:discern:55`
- source span: `src:c1:p74@137-p74@273`
- source span excerpt:
```text
This tendency is baked into our neurobiology and might only be surmountable through enlightenment-level self-awareness and self-control.
```
- visible reaction:
```text
The 'enlightenment-level' qualifier lands as a deliberate deflation. Rather than offering a practical path, it sets the bar so high that for normal purposes the unconscious process might as well be treated as fixed.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 056 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p74@0-p74@544:discern:56`
- source span: `src:c1:p74@293-p74@544`
- source span excerpt:
```text
what people value – and how much they value those things – is not entirely biologically determined. It is both mediated by perception (which is not always reliable) and informed by culture (which creates significant variability across time and place).
```
- visible reaction:
```text
This second half runs against the deterministic tenor of the first. The 'not entirely' is doing real work — it preserves the biological substrate while asserting that cultural and perceptual inputs reshape the weighting. Together with the earlier 'weights and evaluations used in that process are not' (p73), this frames culture and perception as the levers worth examining, even if direct self-override isn't on the table.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Reaction 56 references 'the first' (earlier section) and 'earlier...weights and evaluations used in that process are not' but provides no specific prior citation—only a vague structural reference.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 057 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p76@0-p78@176:discern:57`
- source span: `src:c1:p78@0-p78@176`
- source span excerpt:
```text
We could call this the law of small numbers as applied to relationships, and it skews our valuations irrespective of the nature of the relationships on which they were trained.
```
- visible reaction:
```text
The naming here is the operative move — not just the analogy. 'Law of small numbers' borrows from statistics to describe a structural sampling problem: n=1 yields overfitted pattern recognition that fails to categorize genuinely similar cases. The phrase 'irrespective of the nature of the relationships on which they were trained' is doing real work — it means the distortion isn't determined by whether the parental relationship was good or bad, but by its singularity alone. The second reason (announced as 'both' alongside this one) hasn't arrived yet.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 058 — `local_only` — `retrospect`

- reaction_id: `rx:Chapter_1:src:c1:p78@176-p78@176:retrospect:1`
- source span: `src:c1:p78@176-p78@176`
- source span excerpt:
```text
We could call this the law of small numbers as applied to relationships, and it skews our valuations irrespective of the nature of the relationships on which they were trained.
```
- visible reaction:
```text
The chapter closes on a structural promissory note: two universal difficulties named, one specified. The transition to section 2 ('The Game of Games') signals a shift to application after the dense theoretical foundation. The valuation algorithm is now fully operationalized — innate architecture with trained weights — and the dual-barrier failure mode (unconscious + strategic) is established as the irreducible epistemic constraint on every subsequent claim. What the chapter does not yet resolve: how accurate relationship assessment becomes possible given these barriers, and what the second universal difficulty is.
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

## Probe Memory Checkpoints

Memory Quality in this historical Eval-1 Retry1 dossier was scored from legacy probe-time digest snapshots. These scores should be read as `memory_snapshot_basis=legacy_digest_snapshot`, not as full-state Memory Quality. The state blocks below are exact Markdown re-layouts of recorded digest fields, not fresh summaries and not final runtime dumps.

### Memory State Evidence Boundary

- Legacy probe-time digest evidence: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`. The per-probe blocks below come from snapshot fields such as `active_attention_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, and `source_ref_digest`.
- Final full runtime state references: files under `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime`. These are useful for diagnosis, but they are window-end state references rather than the exact state used at each Memory Quality probe.
- Window boundary checkpoint: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/checkpoints/chapter-001.json`. This is the chapter/window boundary checkpoint, not five independent probe-time checkpoints.
- Historical artifact boundary: current Eval-1 artifacts do not contain `scoring_memory_state`, so these MQ scores remain legacy digest-based. Post-repair runs should score full probe-time memory stores from `scoring_memory_state`.

### Full Runtime State Links

| State artifact | Path | Boundary note |
| --- | --- | --- |
| Active Attention | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/active_attention.json` | Final window-end active attention store; not the probe-time full store. |
| Concept Registry | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/concept_registry.json` | Final window-end concept store; use for diagnosis only. |
| Thread Trace | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/thread_trace.json` | Final window-end thread store; use for diagnosis only. |
| Reflective Frames | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reflective_frames.json` | Final window-end reflective store; use for diagnosis only. |
| Reaction Records | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json` | Final window reaction record store; timeline above is the reviewer-readable projection. |
| Read Audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/read_audit.jsonl` | Runtime operation/audit stream for diagnosis. |
| Settlement Audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/settlement_audit.jsonl` | Runtime settlement/audit stream for diagnosis. |
| Chapter checkpoint | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/checkpoints/chapter-001.json` | Full window boundary checkpoint, not a per-probe checkpoint. |

### Probe 1 — MQ `4.00` — near 20%

#### Probe Position And Question
- target sentence: `c1-s90`
- boundary kind: `early argument-block closure`
- why this point: Closes the opening relationship-as-value-transaction frame before the argument turns more explicitly toward mating and dating.
- structural signals to check:
  - three approaches to other people
  - prosocial vs antisocial framing
  - relationships as games and value transactions

#### Source Orientation
```text
   s88 / p17: In relationships, people try to get what they want from others: this is the goal.
   s89 / p17: And they have to go about doing this without violating – or, more realistically, selectively violating – various inter- and intrapersonal guidelines: these are the rules.
>> s90 / p17: If people get too little of what they want (or too much of what they don’t want), they stop playing – which, incidentally, is another relationship law.
   s91 / p18: Every type of relationship constitutes a different game – as does every specific relationship of the same type.
   s92 / p18: For instance, the game of friendship is different from the game of business, both in their rules and goals.
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ],
  "hot_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ]
}
```

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:comparable-value-exchange",
    "concept_key": "comparable-value-exchange",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p12@464-p12@530",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 464
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 530
          }
        },
        "quote": "the media in which unequal goods of comparable value are exchanged",
        "role": "refined_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the media in which unequal goods of comparable value are exchanged"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:epistemic-opacity-of-valuation",
    "concept_key": "epistemic-opacity-of-valuation",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@916",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 916
          }
        },
        "quote": "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question.",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:prosocial-neutral-instrumental",
    "concept_key": "prosocial-neutral-instrumental",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@472-p6@553",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 472
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 553
          }
        },
        "quote": "This is, by definition, a prosocial solution, as it creates the basis of society.",
        "role": "key_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "This is, by definition, a prosocial solution, as it creates the basis of society."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[]
```

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p3@0-p3@56",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 56
      }
    },
    "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
    "role": "thesis_statement",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p4@452-p4@516",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 452
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 516
      }
    },
    "quote": "other people are typically a problem until they prove otherwise.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p14@475-p14@616",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 475
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 616
      }
    },
    "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@791-p16@896",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 791
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 896
      }
    },
    "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p12@464-p12@530",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 12,
        "char_offset": 464
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 12,
        "char_offset": 530
      }
    },
    "quote": "the media in which unequal goods of comparable value are exchanged",
    "role": "refined_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@0-p11@916",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 916
      }
    },
    "quote": "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question.",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  },
  {
    "source_span_id": "src:c1:p6@472-p6@553",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 6,
        "char_offset": 472
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 6,
        "char_offset": 553
      }
    },
    "quote": "This is, by definition, a prosocial solution, as it creates the basis of society.",
    "role": "key_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@260-p16@574",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 260
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 574
      }
    },
    "quote": "If the goods are the same, then exchange is either unnecessary or impossible (so no relationship is formed). And if their values are too disparate, then the relationship becomes likely in inverse proportion to the size of the perceived mismatch in value: the greater the mismatch, the less likely the relationship.",
    "role": "reaction_anchor",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `4`
- mainline_fidelity: `4`
- organization: `4`
- fidelity: `4`
- judge-provided overall: `4`
- final overall MQ: `4`
- judge reason: The snapshot retains strong material including the governing thesis ('relationships are media in which value is transacted'), the refined definition of unequal goods of comparable value, the epistemic opacity of valuation, the covert transaction norm, and the game-theoretic exit condition (stop playing when payoff is insufficient). However, the structural signal 'three approaches to other people' (move against, move away, move toward) is absent from all digest fields—this is the organizing framework the source explicitly introduces at the outset to structure the prosocial/antisocial distinction. The 'prosocial vs antisocial framing' is only partially captured (the prosocial concept is stored but not the three-part contrast with move-against and move-away). The 'relationships as games' structure is implied through the exit condition but not explicitly stated as a game definition (rules + goal). These omissions are notable given the probe explicitly flagged these structural signals as worth checking at this early-argument-block boundary.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[0]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/value_of_others_private_en__segment_1.md`.

### Probe 2 — MQ `3.75` — near 35%

#### Probe Position And Question
- target sentence: `c1-s136`
- boundary kind: `section pivot`
- why this point: Captures the pivot into sexual relationships and the economic model of mating/dating before the calculator model expands.
- structural signals to check:
  - sexual relationship definition
  - mating and dating as a game
  - perceived best options and economic modeling

#### Source Orientation
```text
   s134 / p25: In fact, the economic model clarifies the reasons behind the emotions that motivate people to form relationships.
   s135 / p25: And since the model can explain emotions (but emotions cannot explain the model), this means that the model is more fundamentally true and should take precedence.
>> s136 / p26: To understand why this is the case, we need to take a closer look at the concept of value: what it is and how it operates.
   s137 / p27: The covert calculator⁠4
   s138 / p28: Value is easy to define but difficult to pin down.
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:nested-game-structure",
      "item_id": "nested-game-structure",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Nested game structure: each specific relationship is its own sub-game within a meta-game category. Rules and goals vary not only by relationship type but by individual instance.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@0-p18@875",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 875
            }
          },
          "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
          "role": "support",
          "resolution": {
            "status": "fallback_unit_span",
            "method": "quote_not_found",
            "match_count": 0
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:abstraction-utility-inverse",
      "item_id": "abstraction-utility-inverse",
      "attention_tags": [
        "focus",
        "tension"
      ],
      "statement": "Truth and utility are inversely related in relationship principles: the more accurate a category-level principle is, the more abstract and unsatisfying it becomes.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p19@502-p19@591",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 502
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 591
            }
          },
          "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ],
  "hot_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ]
}
```

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:comparable-value-exchange",
    "concept_key": "comparable-value-exchange",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p12@464-p12@530",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 464
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 530
          }
        },
        "quote": "the media in which unequal goods of comparable value are exchanged",
        "role": "refined_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the media in which unequal goods of comparable value are exchanged"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:epistemic-opacity-of-valuation",
    "concept_key": "epistemic-opacity-of-valuation",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@916",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 916
          }
        },
        "quote": "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question.",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:prosocial-neutral-instrumental",
    "concept_key": "prosocial-neutral-instrumental",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@472-p6@553",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 472
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 553
          }
        },
        "quote": "This is, by definition, a prosocial solution, as it creates the basis of society.",
        "role": "key_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "This is, by definition, a prosocial solution, as it creates the basis of society."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:perception-vs-actuality-mechanism",
    "thread_key": "perception-vs-actuality-mechanism",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@565-p23@663",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 565
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 663
          }
        },
        "quote": "then the perception of value must be the mechanism that lies at the heart of sexual relationships.",
        "role": "key_claim",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "then the perception of value must be the mechanism that lies at the heart of sexual relationships."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p3@0-p3@56",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 56
      }
    },
    "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
    "role": "thesis_statement",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p4@452-p4@516",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 452
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 516
      }
    },
    "quote": "other people are typically a problem until they prove otherwise.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p14@475-p14@616",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 475
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 616
      }
    },
    "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@791-p16@896",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 791
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 896
      }
    },
    "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@0-p18@875",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 875
      }
    },
    "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  },
  {
    "source_span_id": "src:c1:p19@502-p19@591",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 502
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 591
      }
    },
    "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p20@31-p20@430",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 31
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 430
      }
    },
    "quote": "On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level.",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p12@464-p12@530",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 12,
        "char_offset": 464
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 12,
        "char_offset": 530
      }
    },
    "quote": "the media in which unequal goods of comparable value are exchanged",
    "role": "refined_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `4`
- mainline_fidelity: `4`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `4`
- final overall MQ: `3.75`
- judge reason: The snapshot retains all three probe-targeted structural signals in substantial form: (1) the sexual relationship definition ('necessary and sufficient element of a sexual relationship is the presence of sex'), (2) mating and dating as a game with rules/laws, and (3) perceived best options as the governing law plus the economic/behavioral economics framing. The 'perceived best options' thread is correctly captured as the 'fundamental law of the game.' However, the economic model synthesis is present only as concept entries ('epistemic-opacity-of-valuation') without a coherent thread connecting all three signals together, and the behavioral economics label/framework is present in the source but not prominently surfaced in the digest threads. The nested game structure from paragraph 18 is retained but shows a fallback resolution, suggesting partial coverage. Overall the snapshot is accurate and substantive but the three structural signals are somewhat siloed rather than integrated into a unified economic model thread.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[1]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/value_of_others_private_en__segment_1.md`.

### Probe 3 — MQ `4.00` — near 60%

#### Probe Position And Question
- target sentence: `c1-s247`
- boundary kind: `section closure`
- why this point: Closes the covert-calculator section, giving a strong checkpoint for subjective value and emotion-as-valuation.
- structural signals to check:
  - covert calculator model
  - subjective and fluctuating value
  - emotion as valuation output

#### Source Orientation
```text
   s245 / p46: It’s unsettling because we would prefer not to think that some people are more valuable than others, and it’s contentious because we tend to disagree about what might contribute to those differences in value.
   s246 / p46: However, we can largely avoid both issues by remembering that value is always assessed in relation to a personally relevant goal.
>> s247 / p47: For instance, a plumber is neither inherently more nor less valuable than a cardiologist.
   s248 / p47: However, if your toilet backs up, you’ll be calling one and not the other.
   s249 / p47: This decision is not unsettling – it’s common sense.
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:nested-game-structure",
      "item_id": "nested-game-structure",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Nested game structure: each specific relationship is its own sub-game within a meta-game category. Rules and goals vary not only by relationship type but by individual instance.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@0-p18@875",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 875
            }
          },
          "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
          "role": "support",
          "resolution": {
            "status": "fallback_unit_span",
            "method": "quote_not_found",
            "match_count": 0
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:abstraction-utility-inverse",
      "item_id": "abstraction-utility-inverse",
      "attention_tags": [
        "focus",
        "tension"
      ],
      "statement": "Truth and utility are inversely related in relationship principles: the more accurate a category-level principle is, the more abstract and unsatisfying it becomes.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p19@502-p19@591",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 502
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 591
            }
          },
          "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ],
  "hot_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ]
}
```

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:comparable-value-exchange",
    "concept_key": "comparable-value-exchange",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p12@464-p12@530",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 464
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 530
          }
        },
        "quote": "the media in which unequal goods of comparable value are exchanged",
        "role": "refined_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the media in which unequal goods of comparable value are exchanged"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:emotion-as-translator",
    "concept_key": "emotion-as-translator",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p41@379-p41@442",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 379
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 442
          }
        },
        "quote": "the calculated value coefficient is transformed into an emotion",
        "role": "key_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the calculated value coefficient is transformed into an emotion"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:epistemic-opacity-of-valuation",
    "concept_key": "epistemic-opacity-of-valuation",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@916",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 916
          }
        },
        "quote": "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question.",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:perception-vs-actuality-mechanism",
    "thread_key": "perception-vs-actuality-mechanism",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@565-p23@663",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 565
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 663
          }
        },
        "quote": "then the perception of value must be the mechanism that lies at the heart of sexual relationships.",
        "role": "key_claim",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "then the perception of value must be the mechanism that lies at the heart of sexual relationships."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p3@0-p3@56",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 56
      }
    },
    "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
    "role": "thesis_statement",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p4@452-p4@516",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 452
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 516
      }
    },
    "quote": "other people are typically a problem until they prove otherwise.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p14@475-p14@616",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 475
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 616
      }
    },
    "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@791-p16@896",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 791
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 896
      }
    },
    "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@0-p18@875",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 875
      }
    },
    "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  },
  {
    "source_span_id": "src:c1:p19@502-p19@591",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 502
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 591
      }
    },
    "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p20@31-p20@430",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 31
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 430
      }
    },
    "quote": "On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level.",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@19-p33@195",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 19
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 195
      }
    },
    "quote": "nesting games will always take precedence over nested games whenever we become aware of new information that affects the acquisition (or maintenance) of the superordinate game.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `4`
- mainline_fidelity: `4`
- organization: `4`
- fidelity: `4`
- judge-provided overall: `4`
- final overall MQ: `4`
- judge reason: The snapshot strongly retains the three probe-targeted structural signals: the covert calculator model (value coefficient concept with provisional values/weights/aggregation), subjective and fluctuating value (driven by goal-relevance and information), and emotion as valuation output (conceptually captured via 'emotion-as-translator' with quote 'the calculated value coefficient is transformed into an emotion'). Recent reactions demonstrate good engagement depth, noting that emotion is 'constituted by behavioral impulses' (approach, acquire, protect, maintain) and that it communicates 'more elegantly' than conscious awareness. The governing thesis (relationships as value-transaction media), key terms like 'value coefficient,' and the consciousness-bandwidth justification are all retained. Minor gap: the snapshot doesn't explicitly capture the value coefficient's comparative function (being ranked against other goods' coefficients to determine action), but this is a sub-component rather than a central structural feature.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[2]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/value_of_others_private_en__segment_1.md`.

### Probe 4 — MQ `3.50` — near 75%

#### Probe Position And Question
- target sentence: `c1-s297`
- boundary kind: `late hinge before complication`
- why this point: Captures the goal-relative human value frame before the text complicates the model with revealed preferences and red flags.
- structural signals to check:
  - goal-relative human value
  - problem-of-living inference
  - selection thresholds and mating/dating as genetic-survival game

#### Source Orientation
```text
   s295 / p58: As a result, most people will not be able to get everything they want from a single person.
   s296 / p58: And this means – when it comes to relationships – there aren’t any solutions, only trade-offs.
>> s297 / p58: And this system of trade-offs becomes increasingly more complicated in direct proportion to the number of things we want from any given person.
   s298 / p58: Not only will the things we want fluctuate in importance over time, but they will fluctuate differentially, as well.
   s299 / p58: This will alter the relative priority of what we want from any particular person, and this, in turn, will affect how much we value that person by influencing our perception of the trade-offs involved.
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:nested-game-structure",
      "item_id": "nested-game-structure",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Nested game structure: each specific relationship is its own sub-game within a meta-game category. Rules and goals vary not only by relationship type but by individual instance.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@0-p18@875",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 875
            }
          },
          "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
          "role": "support",
          "resolution": {
            "status": "fallback_unit_span",
            "method": "quote_not_found",
            "match_count": 0
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:abstraction-utility-inverse",
      "item_id": "abstraction-utility-inverse",
      "attention_tags": [
        "focus",
        "tension"
      ],
      "statement": "Truth and utility are inversely related in relationship principles: the more accurate a category-level principle is, the more abstract and unsatisfying it becomes.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p19@502-p19@591",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 502
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 591
            }
          },
          "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ],
  "hot_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ]
}
```

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:comparable-value-exchange",
    "concept_key": "comparable-value-exchange",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p12@464-p12@530",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 464
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 530
          }
        },
        "quote": "the media in which unequal goods of comparable value are exchanged",
        "role": "refined_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the media in which unequal goods of comparable value are exchanged"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:emotion-as-translator",
    "concept_key": "emotion-as-translator",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p41@379-p41@442",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 379
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 442
          }
        },
        "quote": "the calculated value coefficient is transformed into an emotion",
        "role": "key_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the calculated value coefficient is transformed into an emotion"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:epistemic-opacity-of-valuation",
    "concept_key": "epistemic-opacity-of-valuation",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@916",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 916
          }
        },
        "quote": "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question.",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "this valuation typically occurs beneath the threshold of awareness. This means that neither party can ever know the other's true valuation of a specific good (which exists in the inaccessible privacy of the other's mind), and also that each party typically doesn't entirely know his or her own valuation of the good in question."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:perception-vs-actuality-mechanism",
    "thread_key": "perception-vs-actuality-mechanism",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@565-p23@663",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 565
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 663
          }
        },
        "quote": "then the perception of value must be the mechanism that lies at the heart of sexual relationships.",
        "role": "key_claim",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "then the perception of value must be the mechanism that lies at the heart of sexual relationships."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p3@0-p3@56",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 56
      }
    },
    "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
    "role": "thesis_statement",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p4@452-p4@516",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 452
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 516
      }
    },
    "quote": "other people are typically a problem until they prove otherwise.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p14@475-p14@616",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 475
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 616
      }
    },
    "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@791-p16@896",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 791
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 896
      }
    },
    "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@0-p18@875",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 875
      }
    },
    "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  },
  {
    "source_span_id": "src:c1:p19@502-p19@591",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 502
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 591
      }
    },
    "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p20@31-p20@430",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 31
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 430
      }
    },
    "quote": "On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level.",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@19-p33@195",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 19
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 195
      }
    },
    "quote": "nesting games will always take precedence over nested games whenever we become aware of new information that affects the acquisition (or maintenance) of the superordinate game.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `3`
- mainline_fidelity: `4`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.5`
- judge reason: The snapshot retains core material including the transactional relationships thesis, the goal-relative value frame (plumber/cardiology analogy, value coefficient, goal-relevance drivers), and the genetic-survival framing of mating/dating as 'the game of games.' However, the 'problem-of-living inference' framing ('What problem of living are they attempting to solve?') is not explicitly retained as a named inferential structure, though its content appears indirectly. More significantly, the exemplar-based selection mechanism is absent despite being a central structural device introduced around the probe point—the source discusses idealized constructs, goodness-of-fit heuristics, and selection thresholds varying by goal importance, but the snapshot does not capture this thread. This represents a meaningful gap in the goal-relative value apparatus.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[3]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/value_of_others_private_en__segment_1.md`.

### Probe 5 — MQ `3.00` — window end

#### Probe Position And Question
- target sentence: `c1-s391`
- boundary kind: `window end`
- why this point: Ends the active window after the model has expanded into desire, disgust, red flags, and revealed preferences.
- structural signals to check:
  - goal conflation
  - desire, disgust, conflict, and red flags
  - revealed preferences, culture, and valuation algorithm

#### Source Orientation
```text
   s386 / p77: This is comparable to using one specific sparrow not only as the exemplar for all other sparrows but also for all other birds.
   s387 / p77: Penguins, ostriches, and condors are fully just as avian as sparrows, but an algorithm trained exclusively on sparrows (let alone one specific sparrow) probably wouldn’t even recognize them as birds.
   s388 / p78: We could call this the law of small numbers as applied to relationships, and it skews our valuations irrespective of the nature of the relationships on which they were trained.
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:nested-game-structure",
      "item_id": "nested-game-structure",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Nested game structure: each specific relationship is its own sub-game within a meta-game category. Rules and goals vary not only by relationship type but by individual instance.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@0-p18@875",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 875
            }
          },
          "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
          "role": "support",
          "resolution": {
            "status": "fallback_unit_span",
            "method": "quote_not_found",
            "match_count": 0
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:abstraction-utility-inverse",
      "item_id": "abstraction-utility-inverse",
      "attention_tags": [
        "focus",
        "tension"
      ],
      "statement": "Truth and utility are inversely related in relationship principles: the more accurate a category-level principle is, the more abstract and unsatisfying it becomes.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p19@502-p19@591",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 502
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 19,
              "char_offset": 591
            }
          },
          "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ],
  "hot_items": [
    {
      "ref_id": "active_attention:transactional-relationships-framing",
      "item_id": "transactional-relationships-framing",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Relationships as value-transaction media: this is the governing frame introduced at the outset.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p3@0-p3@56",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 3,
              "char_offset": 56
            }
          },
          "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
          "role": "thesis_statement",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:default-skepticism-default",
      "item_id": "default-skepticism-default",
      "attention_tags": [
        "tension",
        "interpretation"
      ],
      "statement": "Default skepticism toward others: 'problem until they prove otherwise' — inverts normal social assumptions.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@452-p4@516",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 452
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 516
            }
          },
          "quote": "other people are typically a problem until they prove otherwise.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:covert-transaction-norm",
      "item_id": "covert-transaction-norm",
      "attention_tags": [
        "focus",
        "framework"
      ],
      "statement": "Value transactions in relationships are covert by necessity — negotiated with subtlety, tact, and indirectness. The exchange is structurally hidden, not just unconsciously operated.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p14@475-p14@616",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 475
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 14,
              "char_offset": 616
            }
          },
          "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    },
    {
      "ref_id": "active_attention:value-mismatch-pain-awareness-conditional",
      "item_id": "value-mismatch-pain-awareness-conditional",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "Relationship pain from value mismatch is awareness-conditional: distress emerges when the under-compensated party recognizes that the other party's perception has shifted since the point of transaction.",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p16@791-p16@896",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 791
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 16,
              "char_offset": 896
            }
          },
          "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
          "role": "key_claim",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        }
      ],
      "linked_concept_keys": [],
      "linked_thread_keys": [],
      "projection_role": "current_support",
      "support_status": "source_backed",
      "current_support": true,
      "lineage_only": false,
      "projection_warning": ""
    }
  ]
}
```

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:approach-avoidance-conflict-taxonomy",
    "concept_key": "approach-avoidance-conflict-taxonomy",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p63@0-p65@1416",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 63,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 65,
            "char_offset": 1416
          }
        },
        "quote": "high-value individual is desire. low-value individual is disgust. mid-value individual — if a lot of what we really want AND a lot of what we really don't — we feel conflicted. this is called an approach-avoidance conflict, and it can trap people in agonizing indecision for years.",
        "role": "key_claim",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "high-value individual is desire. low-value individual is disgust. mid-value individual — if a lot of what we really want AND a lot of what we really don't — we feel conflicted. this is called an approach-avoidance conflict, and it can trap people in agonizing indecision for years."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:comparable-value-exchange",
    "concept_key": "comparable-value-exchange",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p12@464-p12@530",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 464
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 12,
            "char_offset": 530
          }
        },
        "quote": "the media in which unequal goods of comparable value are exchanged",
        "role": "refined_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the media in which unequal goods of comparable value are exchanged"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:emotion-as-translator",
    "concept_key": "emotion-as-translator",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p41@379-p41@442",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 379
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 442
          }
        },
        "quote": "the calculated value coefficient is transformed into an emotion",
        "role": "key_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "the calculated value coefficient is transformed into an emotion"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:perception-vs-actuality-mechanism",
    "thread_key": "perception-vs-actuality-mechanism",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@565-p23@663",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 565
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 663
          }
        },
        "quote": "then the perception of value must be the mechanism that lies at the heart of sexual relationships.",
        "role": "key_claim",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "then the perception of value must be the mechanism that lies at the heart of sexual relationships."
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  }
]
```

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p3@0-p3@56",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 56
      }
    },
    "quote": "RELATIONSHIPS ARE THE MEDIA IN WHICH VALUE IS TRANSACTED",
    "role": "thesis_statement",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p4@452-p4@516",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 452
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 516
      }
    },
    "quote": "other people are typically a problem until they prove otherwise.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p14@475-p14@616",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 475
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 14,
        "char_offset": 616
      }
    },
    "quote": "the transaction of value in such relationships is typically negotiated covertly: it must be approached with subtlety, tact, and indirectness.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p16@791-p16@896",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 791
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 16,
        "char_offset": 896
      }
    },
    "quote": "awareness of this violation can lead to a great deal of pain and distress for the under-compensated party",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@0-p18@875",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 875
      }
    },
    "quote": "Every type of relationship constitutes a different game – as does every specific relationship of the same type. And since each specific friendship is nested in the larger game of general friendship, we find that the overarching category contains enormous variation at the individual level.",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  },
  {
    "source_span_id": "src:c1:p19@502-p19@591",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 502
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 19,
        "char_offset": 591
      }
    },
    "quote": "the truer these principles are, the more abstract and unsatisfying they are likely to be.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p20@31-p20@430",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 31
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 20,
        "char_offset": 430
      }
    },
    "quote": "On the one hand, greater specificity at the category level will make any claim less valid and reliable because it will increase the likelihood that it is contradicted at the individual level. On the other hand, less specificity at the category level will make any claim less practical and actionable because it will decrease the likelihood that it can be effectively applied at the individual level.",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@19-p33@195",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 19
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 195
      }
    },
    "quote": "nesting games will always take precedence over nested games whenever we become aware of new information that affects the acquisition (or maintenance) of the superordinate game.",
    "role": "key_claim",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `3`
- mainline_fidelity: `3`
- organization: `3`
- fidelity: `3`
- judge-provided overall: `3`
- final overall MQ: `3`
- judge reason: The snapshot retains strong coverage of the book's foundational framework (relationships as value-transaction media, comparable-value exchange, the covert calculator, emotion-as-translator) and captures key later additions including the approach-avoidance conflict taxonomy (desire/disgust/conflict) and the law of small numbers from parental relationship training. However, 'goal conflation' — explicitly named as one of the two major complicators in the source — has no dedicated active_item or concept entry, despite being a significant structural pivot. The 'red flags' material is present only in the probe metadata, not as a retained semantic item. The revealed-preferences insight (people's choices reveal their values; direct questioning is useless) is implied by the valuation algorithm section but not named or foregrounded. The snapshot is organized into coherent concepts and threads with good source-backing, but the recent_reactions feel somewhat detached from the main digest structure, and the three structural signals are unevenly represented rather than uniformly surfaced.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_value_of_others/outputs/value_of_others_private_en__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[4]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/value_of_others_private_en__segment_1.md`.

## Scoring Interpretation

This section explains how the trace above becomes the Eval-1 scores for this window.

### Selective Legibility

- Formula used by the run report: `(exact_match + focused_hit) / note_case_count = (10 + 18) / 94 = 0.2979`.
- Incidental cover count `4` is visible support, not recall credit.
- Miss count `62` means the reaction timeline either did not produce a strict source-overlap candidate for the note target or the judge rejected the admitted candidate.
- Unlocatable reaction count `1` is diagnostic only and never becomes a match.

### Memory Quality

- Window MQ is the average of the five probe-time overall scores: 4, 3.75, 4, 3.5, 3 -> `3.65`.
- The probe state sections above show what the mechanism had available at scoring time; final runtime state is not substituted for probe-time evidence.

### Callback / FVI

- Reaction audit reviewed `58` visible reactions: `11` grounded, `9` weak, `1` FVI, `37` local-only.
- Grounded callback means the visible reaction had enough prior visible evidence; weak callback means the link was plausible but under-anchored; FVI means the integration claim was rejected as unsupported.

### Product-Experience Reading

The playback is the closest artifact to the reader experience: it shows the source span, visible reaction, note coverage, callback/FVI decision, and probe memory state in one path. It still does not prove product quality; it gives reviewers concrete evidence to inspect before making that judgment.

## Manual Review Guide

1. Start with the dataset source window for chapter/paragraph context.
2. Read the reaction timeline in order and mark reactions that feel productively useful or visibly wrong.
3. For every important user note, check whether the matching reaction actually centers the target note, not just nearby text.
4. At each probe point, compare the source orientation with the structured memory state before reading the MQ judge reason.
5. Treat weak callback and FVI rows as debugging leads, not product-quality conclusions.

## Claims Not Authorized

- No evidence catalog update is made by this playback dossier.
- No Long Span vNext formal benchmark authority is promoted here.
- No product-quality claim is made from these artifacts alone.
- No Reader Reaction Value / Insight and Clarification metric is introduced.
- No runtime, eval-runner, judge-prompt, frontend, public API, or durable-state behavior changed to create this document.
