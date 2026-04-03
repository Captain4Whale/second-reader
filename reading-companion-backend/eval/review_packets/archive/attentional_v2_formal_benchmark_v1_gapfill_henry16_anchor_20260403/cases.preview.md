# Revision/Replacement Packet `attentional_v2_formal_benchmark_v1_gapfill_henry16_anchor_20260403`

This packet was generated automatically from cases whose current `benchmark_status` requires another hardening round.

## Dataset
- dataset_id: `attentional_v2_private_library_excerpt_en_question_aligned_v1__scratch__closed_loop_full_smoke_en_henry_whitespacefix_20260331`
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

## 1. `education_of_henry_adams_public_en__16__anchored_reaction_selectivity__seed_v1`

- benchmark_status: `reviewed_active`
- review_status: `llm_reviewed`
- book: `The Education of Henry Adams`
- author: `Henry Adams`
- chapter: `XI: The Battle of the Rams (1863)` (`16`)
- question_ids: `EQ-CM-002|EQ-AV2-005`
- phenomena: `reaction_anchor|selective_legibility|visible_thought`
- selection_reason: Selected because the passage contains a line that seems reaction-worthy but still demands selective, anchored reading. Anchor line: “I weakly supposed … I really, though most strangely, believed that it was an act of friendliness.”
- judge_focus: Is the visible reaction anchored to the actual line and genuinely worth preserving?
- latest_review_action: `keep`
- latest_problem_types: `other`
- latest_revised_bucket: ``
- latest_notes: The excerpt is clean with a well-defined anchor line in quotes that generates a visible, preserved reaction about believing an act of friendliness. The bucket 'anchored_reaction_selectivity' fits correctly since the passage demonstrates both anchoring (clear quoted line) and selective legibility (the irony of the mistaken belief). No adversarial risks flagged, all bands are strong, and the factual audit is clean.

```text
Gladstone’s offence, “singular and palpable,” was not the speech alone, but its cause—the policy that inspired the speech.
“I weakly supposed … I really, though most strangely, believed that it was an act of friendliness.”
Whatever absurdity Gladstone supposed, Russell supposed nothing of the sort.
```
