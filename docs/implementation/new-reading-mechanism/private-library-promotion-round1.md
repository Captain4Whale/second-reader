# Private-Library Promotion Round 1

Purpose: propose the first balanced promotion-preparation round from the combined `attentional_v2_private_library_v2` local-only supplement into later formal benchmark growth work.
Use when: selecting which private-library books to curate first, deciding how many chapter/excerpt candidates to lift into the next benchmark-growth pass, or explaining why some private books should be deferred.
Not for: final benchmark promotion decisions, reviewed-case results, or stable corpus policy.
Update when: the prioritized source set changes, the round-1 target counts change, or the local-only supplement inventory changes materially.

## Inputs Analyzed
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/manifests/source_books/attentional_v2_private_library_screen_v2.json`
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/eval/manifests/corpora/attentional_v2_private_library_bilingual_v2.json`
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/eval_local_datasets/chapter_corpora/attentional_v2_private_library_chapters_en_v2/chapters.jsonl`
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/eval_local_datasets/chapter_corpora/attentional_v2_private_library_chapters_zh_v2/chapters.jsonl`
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_private_library_excerpt_en_v2/cases.jsonl`
- `/Users/baiweijiang/Documents/Projects/reading-companion/reading-companion-backend/state/eval_local_datasets/excerpt_cases/attentional_v2_private_library_excerpt_zh_v2/cases.jsonl`
- `/Users/baiweijiang/Documents/Projects/reading-companion/docs/implementation/new-reading-mechanism/modern-nonfiction-expansion-booklist.md`
- `/Users/baiweijiang/Documents/Projects/reading-companion/docs/implementation/new-reading-mechanism/evaluation-dataset-layout.md`

## Current Supplement Snapshot
The combined private-library `v2` supplement is large enough to support a real promotion-preparation pass:

- books: `29`
  - English: `22`
  - Chinese: `7`
- corpus lane:
  - `28` `chapter_corpus_eligible`
  - `1` `excerpt_only`
- chapter candidates:
  - English: `85`
  - Chinese: `28`
- excerpt seed candidates:
  - English: `170`
  - Chinese: `56`

Role distribution in the local-only candidate pool:

- English chapters:
  - `24` argumentative
  - `41` expository
  - `20` narrative_reflective
- Chinese chapters:
  - `8` argumentative
  - `12` expository
  - `8` narrative_reflective
- English excerpts:
  - `48` argumentative
  - `82` expository
  - `40` narrative_reflective
- Chinese excerpts:
  - `16` argumentative
  - `24` expository
  - `16` narrative_reflective

Important implication:
- the supplement is broad enough for a balanced first round
- but the Chinese pool is much thinner and should not be exhausted in one pass
- the first formal promotion-preparation round should therefore stay balanced in promoted counts, while being conservative about how many Chinese source books it burns through

## Promotion Objective For Round 1
Round 1 should not try to absorb the whole supplement into the benchmark.

It should do three things well:

1. move the benchmark mix away from literature-only pressure
2. add modern nonfiction failure surfaces without overloading curation/review
3. preserve enough Chinese reserve material for a later round

This means round 1 should prioritize:
- management / economics argument structure
- business / principle extraction
- biography / timeline / causality
- one stronger institutional-history or social-reportage line per language

It should explicitly avoid spending the first round on:
- duplicate or near-duplicate source families
- narrow tactical interview-prep material
- extra literature controls before nonfiction coverage is stabilized

## Recommended Balanced Shape
Use a symmetric promotion-preparation shape even though the source pool is asymmetric.

Recommended round-1 shape:
- prioritized source books:
  - English: `6`
  - Chinese: `6`
- chapter candidates to lift into the next curation pass:
  - English: `8`
  - Chinese: `8`
- excerpt seed candidates to lift into the next curation pass:
  - English: `16`
  - Chinese: `16`

Why this size is reasonable:
- it is large enough to matter against the current tracked benchmark sizes
- it stays small enough to review seriously
- it does not consume the entire Chinese pool in one step
- it gives enough room for later rejection during curation or LLM review without collapsing the round

Recommended role mix per language:
- chapter candidates:
  - `3` expository
  - `3` argumentative
  - `2` narrative_reflective
- excerpt candidates:
  - roughly `6` expository
  - roughly `5` argumentative
  - roughly `5` narrative_reflective

Recommended sourcing rule:
- every prioritized book contributes at least `1` chapter and `2` excerpts
- the strongest `2` books per language contribute a second chapter
- the strongest `4` books per language contribute a third excerpt

That yields:
- `8` chapter candidates per language
- `16` excerpt candidates per language

## Priority Source Books
### English Priority Set (`6`)
1. `good_strategy_bad_strategy_private_en` — `Good Strategy/Bad Strategy`
- Why:
  - strongest management-argument source in the pool
  - directly useful for `argument_evidence_linkage`
  - directly useful for `principle_boundary_control`
- Recommended contribution:
  - `2` chapter candidates
  - `3` excerpt candidates

2. `poor_charlies_almanack_private_en` — `Poor Charlie's Almanack`
- Why:
  - strong example-to-principle mapping
  - exposes over-generalization and weak warranting
  - complements strategy prose with denser principle prose
- Recommended contribution:
  - `2` chapter candidates
  - `3` excerpt candidates

3. `steve_jobs_private_en` — `Steve Jobs`
- Why:
  - strong long-range biography and causal reinterpretation
  - useful for character-pattern establishment in nonfiction
  - adds science/technology-adjacent biography instead of pure management prose
- Recommended contribution:
  - `1` chapter candidate
  - `3` excerpt candidates

4. `evicted_private_en` — `Evicted`
- Why:
  - best English social-reportage / institution-individual source in the pool
  - useful for evidence-heavy explanation without generic moral summary
  - improves nonfiction grounding beyond executive / entrepreneur material
- Recommended contribution:
  - `1` chapter candidate
  - `3` excerpt candidates

5. `fooled_by_randomness_private_en` — `Fooled by Randomness`
- Why:
  - strongest available English probability / luck-versus-skill source
  - useful for conceptual distinction and anti-intuitive explanatory turns
  - broadens the benchmark beyond business memoir voice
- Recommended contribution:
  - `1` chapter candidate
  - `2` excerpt candidates

6. `supremacy_private_en` — `Supremacy`
- Why:
  - modern multi-actor AI/business rivalry
  - useful for institutional incentives, timeline pressure, and technology-business causality
  - keeps the modern supplement visibly current rather than purely canonical
- Recommended contribution:
  - `1` chapter candidate
  - `2` excerpt candidates

### Chinese Priority Set (`6`)
1. `kangxi_hongpiao_private_zh` — `康熙的红票：全球化中的清朝`
- Why:
  - strongest Chinese history / institutional-causality source in the pool
  - useful for diplomacy, state, religion, and policy interaction
  - balances the English side’s social/institutional nonfiction with a Chinese history lane
- Recommended contribution:
  - `2` chapter candidates
  - `3` excerpt candidates

2. `zhangzhongmou_zizhuan_private_zh` — `张忠谋自传(1931-1964)`
- Why:
  - strongest Chinese biography/business source
  - useful for timeline, decision pressure, and early-pattern establishment
  - gives the Chinese track a real biography counterpart instead of only abstract exposition
- Recommended contribution:
  - `2` chapter candidates
  - `3` excerpt candidates

3. `meiguoren_de_xingge_private_zh` — `美国人的性格`
- Why:
  - best Chinese social-observation / culture-history line in the pool
  - useful for evidence-to-claim discipline in cross-society explanation
  - broadens the Chinese track beyond business-only growth material
- Recommended contribution:
  - `1` chapter candidate
  - `3` excerpt candidates

4. `fooled_by_randomness_private_zh` — `随机漫步的傻瓜`
- Why:
  - useful for conceptual distinction and probability language in Chinese
  - gives the Chinese side a direct decision/uncertainty pressure source
  - helpful for cross-language comparison against the English Taleb lane without requiring the same exact chapter pairings
- Recommended contribution:
  - `1` chapter candidate
  - `3` excerpt candidates

5. `biji_de_fangfa_private_zh` — `笔记的方法`
- Why:
  - strongest Chinese expository method/management source
  - useful for claim-to-application structure and concrete advice restraint
  - broadens the Chinese expository lane beyond philosophy or history
- Recommended contribution:
  - `1` chapter candidate
  - `2` excerpt candidates

6. `zouchu_weiyi_zhenliguan_private_zh` — `走出唯一真理观`
- Why:
  - strongest Chinese philosophical / decision-distinction source
  - useful for concept definition, contrast, and anti-dogmatic reasoning
  - adds a precision-demanding argumentative voice not otherwise present in the Chinese pool
- Recommended contribution:
  - `1` chapter candidate
  - `2` excerpt candidates

## Reserve / Defer List
These books should stay in reserve for later rounds rather than round 1.

### English reserves
- `antifragile_private_en`
- `skin_in_the_game_private_en`
- `black_swan_private_en`
- `principles_private_en`
- `shoe_dog_private_en`
- `snowball_private_en`
- `naval_almanack_private_en`
- `making_of_a_manager_private_en`
- `inspired_private_en`

Why reserve them for now:
- Taleb-family overlap is high; `Fooled by Randomness` is enough for round 1
- principle / management overlap is already covered by `Good Strategy/Bad Strategy` and `Poor Charlie's Almanack`
- memoir overlap is already covered by `Steve Jobs`
- some books are strong but better as second-wave expansions after the first nonfiction pass lands

### English defer / low-priority for formal promotion
- `book_of_elon_private_en`
- `elon_musk_private_en`
- `cracking_pm_career_private_en`
- `cracking_pm_interview_private_en`
- `decode_and_conquer_private_en`
- `chance_private_en`

Why defer:
- `The Book of Elon` overlaps with stronger biography choices
- `Elon Musk` is valuable, but round 1 already has biography coverage and should avoid over-weighting one public figure cluster
- PM interview / PM career books are more tactical and narrower than the first-round benchmark needs
- `Chance` is literature control material, but the public-first benchmark is already literature-heavy

### Chinese reserve
- `canglang_zhishui_private_zh`

Why reserve:
- it is useful as a later Chinese literature control
- but round 1 should spend its narrow Chinese bandwidth on nonfiction diversification first

## Recommended Round-1 Promotion Targets
### Chapters
Promote `8` chapter candidates per language into the next curation/review step.

English chapter targets:
- `good_strategy_bad_strategy_private_en`: `2`
- `poor_charlies_almanack_private_en`: `2`
- `steve_jobs_private_en`: `1`
- `evicted_private_en`: `1`
- `fooled_by_randomness_private_en`: `1`
- `supremacy_private_en`: `1`

Chinese chapter targets:
- `kangxi_hongpiao_private_zh`: `2`
- `zhangzhongmou_zizhuan_private_zh`: `2`
- `meiguoren_de_xingge_private_zh`: `1`
- `fooled_by_randomness_private_zh`: `1`
- `biji_de_fangfa_private_zh`: `1`
- `zouchu_weiyi_zhenliguan_private_zh`: `1`

### Excerpts
Promote `16` excerpt candidates per language into the next curation/review step.

English excerpt targets:
- `good_strategy_bad_strategy_private_en`: `3`
- `poor_charlies_almanack_private_en`: `3`
- `steve_jobs_private_en`: `3`
- `evicted_private_en`: `3`
- `fooled_by_randomness_private_en`: `2`
- `supremacy_private_en`: `2`

Chinese excerpt targets:
- `kangxi_hongpiao_private_zh`: `3`
- `zhangzhongmou_zizhuan_private_zh`: `3`
- `meiguoren_de_xingge_private_zh`: `3`
- `fooled_by_randomness_private_zh`: `3`
- `biji_de_fangfa_private_zh`: `2`
- `zouchu_weiyi_zhenliguan_private_zh`: `2`

## Why This Round Is Balanced Enough
It is balanced in the ways that matter most for benchmark growth:

- same promoted counts per language
- same number of prioritized source books per language
- same target role shape per language
- nonfiction-heavy in both languages
- still varied enough to avoid becoming a pure business-only supplement

It is not perfectly symmetric by category, and that is acceptable for round 1.

Important nuance:
- the Chinese pool does not yet have the same science/technology depth as the English pool
- forcing exact category symmetry now would either weaken the round or waste better English material
- role balance and count balance matter more than one-to-one category mirroring in this first pass

## Key Gaps And Risks
1. Chinese source-pool thinness
- only `7` Chinese books exist in the supplement
- round 1 should therefore leave at least one Chinese reserve book untouched

2. English pool overlap
- Taleb and business-memoir clusters are dense
- without restraint, the benchmark could become “different books saying similar things”

3. Tactical-product-management contamination
- PM interview / career books are useful operationally
- but they are too narrow to anchor the first formal promotion round

4. Literature-control temptation
- both languages have literature candidates
- but the formal tracked benchmark already leans literary
- round 1 should correct that imbalance before adding more literature pressure

5. Review-load realism
- `16` excerpts per language and `8` chapters per language is already a meaningful curation load
- round 1 should stop there and inspect quality before a second supplement-promotion round

## Execution Recommendation
When this round is executed later, the clean sequence should be:

1. create a promotion-candidate packet from the exact source ids listed above
2. preserve the recommended per-book chapter/excerpt counts as soft caps
3. curate and LLM-review that packet
4. promote only the strongest reviewed units into tracked benchmark growth
5. inspect whether the benchmark’s exposed failure surfaces now broaden beyond literary callback and tension cases

## Bottom Line
The first balanced promotion-preparation round should be:
- `6` English books + `6` Chinese books
- `8` chapter candidates per language
- `16` excerpt candidates per language
- nonfiction-first
- role-balanced
- conservative about Chinese pool exhaustion

That is the best first step from the combined private-library `v2` supplement into formal benchmark growth.
