# Revision/Replacement Packet `attentional_v2_formal_benchmark_v1_gapfill_en_local_20260403`

This packet was generated automatically from cases whose current `benchmark_status` requires another hardening round.

## Dataset
- dataset_id: `attentional_v2_private_library_excerpt_en_v2`
- family: `excerpt_cases`
- language_track: `en`
- version: `2`
- targeted_statuses: `needs_revision|needs_replacement|reviewed_active`

## Review Actions
- `keep`
- `revise`
- `drop`
- `unclear`

## Confidence
- `high`
- `medium`
- `low`

## 1. `evicted_private_en__29__seed_1`

- benchmark_status: `reviewed_active`
- review_status: `llm_reviewed`
- book: `Evicted`
- author: `Matthew Desmond`
- chapter: `Chapter 18: Lobster on Food Stamps` (`29`)
- question_ids: ``
- phenomena: ``
- selection_reason: This excerpt illustrates how individuals facing chronic poverty and housing instability maintain dignity and aspirational identity through material desires—wanting new furniture, perfume, and brand-new items as a form of self-respect despite financial constraints.
- judge_focus: Assess whether the model correctly identifies Larraine's economic desperation ('rent-strapped forever') while recognizing her refusal to sacrifice personal possessions as dignity preservation rather than pure fiscal irrationality. The model should distinguish between surface-level 'poor person making irrational choices' and the deeper psychological need to maintain aspirational self-concept.
- latest_review_action: `keep`
- latest_problem_types: `other`
- latest_revised_bucket: `housing_instability`
- latest_notes: The case is now properly populated with metadata. The excerpt is coherent, demonstrates clear phenomena (dignity preservation through aspirational identity under chronic poverty), and the judge_focus appropriately challenges models to make nuanced interpretations rather than surface-level judgments. Minor footnote marker '4' is negligible text noise that doesn't impact comprehension. The case is ready for benchmark inclusion.

```text
It wasn’t like she had just stumbled into a pit and would soon climb out.
Larraine imagined she would be poor and rent-strapped forever.
And if that was to be her lot in life, she might as well have a little jewelry to show for it.
She wanted a new television, not some worn and boxy thing inherited from Lane and Susan.
She wanted a bed no one else had slept in.
She loved perfume and could tell you what a woman was wearing after passing her on the sidewalk.
“Even people like myself,” Larraine said, “we deserve, too, something brand-new.”4
```

## 2. `steve_jobs_private_en__43__seed_1`

- benchmark_status: `reviewed_active`
- review_status: `llm_reviewed`
- book: `Steve Jobs`
- author: `Walter Isaacson`
- chapter: `Chapter Thirty-Four: Twenty-first-century Macs: Setting Apple Apart` (`43`)
- question_ids: ``
- phenomena: ``
- selection_reason: Excerpt captures Jobs criticizing a design for lacking 'purity' and advocating that 'each element be true to itself' - exemplifies his perfectionist approach to product design and aesthetic philosophy.
- judge_focus: Evaluate whether the model can identify Jobs' design philosophy emphasizing purity and holistic integrity in product engineering.
- latest_review_action: `keep`
- latest_problem_types: `other`
- latest_revised_bucket: ``
- latest_notes: The excerpt clearly demonstrates Jobs' design philosophy through his criticism of lack of 'purity' and directive to 'let each element be true to itself.' The primary review correctly identifies this as a strong case with bucket_fit=1 and focus_clarity=1. The 'too_easy' flag from adversarial review is a minor difficulty concern but not a validity issue - the case appropriately illustrates the concept. The original 'revise' decision was overly conservative; metadata now exists and the excerpt is coherent.

```text
Jobs didn’t like it.
As he often did, both at Pixar and at Apple, he slammed on the brakes to rethink things.
There was something about the design that lacked purity, he felt.
“Why have this flat display if you’re going to glom all this stuff on its back?”
he asked Ive.
“We should let each element be true to itself.”
Jobs went home early that day to mull over the problem, then called Ive to come by.
```
