# Revision/Replacement Packet `attentional_v2_private_library_backlog_rescue_en_round1`

This packet was generated automatically from cases whose current `benchmark_status` requires another hardening round.

## Dataset
- dataset_id: `attentional_v2_private_library_excerpt_en_v2`
- family: `excerpt_cases`
- language_track: `en`
- version: `2`
- targeted_statuses: `needs_revision|needs_replacement`

## Review Actions
- `keep`
- `revise`
- `drop`
- `unclear`

## Confidence
- `high`
- `medium`
- `low`

## 1. `steve_jobs_private_en__17__seed_2`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `Steve Jobs`
- author: `Walter Isaacson`
- chapter: `Chapter Eight: Xerox and Lisa: Graphical User Interfaces` (`17`)
- question_ids: ``
- phenomena: ``
- selection_reason: Tests understanding of why Xerox failed commercially despite pioneering GUI technology at PARC - illustrating that good ideas alone aren't enough without effective execution, pricing, and market fit.
- judge_focus: Evaluate whether the model correctly identifies that Xerox failed due to poor execution (clunky performance, excessive $16,595 cost, misaligned target market) rather than lack of innovation, and recognizes the business lesson about execution quality being as important as idea quality.
- latest_review_action: `revise`
- latest_problem_types: `wrong_bucket`
- latest_revised_bucket: `business_strategy`
- latest_notes: The bucket 'narrative_reflective' is clearly wrong - this excerpt is fundamentally about business strategy and causal analysis (why execution matters as much as innovation). The 'too_easy' concern from adversarial review is noted but not disqualifying; the case still requires causal reasoning to connect the specific failure details ($16,595 cost, 30k units sold, clunky performance) to the broader execution-vs-innovation lesson. Once re-bucketed to business_strategy, the case is strong enough for benchmark entry.

```text
It’s not as if Xerox executives ignored what their scientists had created at PARC.
In fact they did try to capitalize on it, and in the process they showed why good execution is as important as good ideas.
In 1981, well before the Apple Lisa or Macintosh, they introduced the Xerox Star, a machine that featured their graphical user interface, mouse, bitmapped display, windows, and desktop metaphor.
But it was clunky (it could take minutes to save a large file), costly ($16,595 at retail stores), and aimed mainly at the networked office market.
It flopped; only thirty thousand were ever sold.
Jobs and his team went to a Xerox dealer to look at the Star as soon as it was released.
But he deemed it so worthless that he told his colleagues they couldn’t spend the money to buy one.
```
