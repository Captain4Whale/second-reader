# Eval-1 Playback Dossier: 活出生命的意义

This playback page is a product-facing reading trace for human review. It replays the Eval-1 window in reading order, then explains how the four evaluation channels score that trace. It is not a new eval run, not a catalog update, not product-quality proof, and not Long Span formal authority.

## Window Verdict

- Lane A selective-legibility recall: `0.3750` over `40` note cases (`7` exact, `8` focused, `2` incidental, `23` miss).
- Lane B Memory Quality: `3.70` average over `5` semantic probes.
- Visible reaction audit: `150` reactions (`19` grounded callback, `9` weak callback, `0` FVI, `122` local-only).
- Reviewer stance: read the timeline first, then the scoring interpretation. The score is justified by the trace, not by the aggregate table alone.

## Evidence Map

- Dataset source window: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`
- Raw segment text: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/huochu_shengming_de_yiyi_private_zh__segment_1.txt`
- Lane A run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu`
- Lane B run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu`
- Lane A note cases: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases`
- Lane B MQ rows: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl`
- Lane B reaction audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/reaction_audit_results.jsonl`
- Probe snapshots: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`
- Normalized eval bundle: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`

## Source Window And Chapter Coverage

- Covered chapters: `第一部分　在集中营的经历`
- Full reviewer-readable source window lives beside the dataset: `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.
- Each reaction below includes its own source-span excerpt so the reviewer can stay in reading flow, then jump to the full source window when needed.

## Selective Legibility Note-Case Ledger

This ledger lists every dataset note target in the window. Matched note cases point to the reaction that appears later in the reading timeline; misses remain visible here so reviewer analysis is not biased toward successful reactions only.

### Note `e0002` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002`
- target note:
```text
每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
```
- target source span(s):
  - `p14@110-155`: 每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
- matched reaction in timeline: `rx:Full_Content:src:c1:p10@265-p14@155:discern:14`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002.json`

### Note `e0003` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003`
- target note:
```text
“是的，人可以习惯任何事物，但请不要问我们是如何习惯的
```
- target source span(s):
  - `p46@51-78`: “是的，人可以习惯任何事物，但请不要问我们是如何习惯的
- matched reaction in timeline: `rx:Full_Content:src:c1:p43@0-p46@138:retrospect:25`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction precisely centers on the core phrase from the note ('不要问我们如何习惯的') and provides a substantive interpretation of its meaning: the refusal to articulate the adaptation mechanism because doing so would reveal something unbearable. The analysis genuinely engages with the note's central idea rather than merely citing it peripherally.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003.json`

### Note `e0004` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004`
- note comment: 职场类似
- target note:
```text
冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
```
- target source span(s):
  - `p61@0-87`: 冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
- matched reaction in timeline: `rx:Full_Content:src:c1:p58@0-p61@87:highlight:34`
- source-span relation: `note_contains_candidate`; coverage `0.3103`
- judge/runner reason: The reaction directly interprets and elaborates on the overlapped source span ("正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。"), reframing it as a protective strategy, which captures the essential content of that span.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004.json`

### Note `e0005` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0005`
- target note:
```text
这时，最痛的不是肉体（这样的惩罚对成人和儿童都一样），而是不公正和不可理喻对心理造成的伤害。
```
- target source span(s):
  - `p62@148-195`: 这时，最痛的不是肉体 （这样的惩罚对成人和儿童都一样），而是不公正和不可理喻对心理造成的伤害。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0005.json`

### Note `e0006` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0006`
- target note:
```text
有丰富的精神生活且比较敏感的人在这里会承受更多痛苦（他们身体也会更弱），但对内心的伤害相应也会少许多。他们能把恶劣的外部环境转化成内心丰富自由的精神生活，只有这样才能解释集中营中身体羸弱的一些人比看似强壮的人生存能力更强。
```
- target source span(s):
  - `p96@42-154`: 有丰富的精神生活且比较敏感的人在这里会承受更多痛苦 （他们身体也会更弱），但对内心的伤害相应也会少许多。他们能把恶劣的外部环境转化成内心丰富自由的精神生活，只有这样才能解释集中营中身体羸弱的一些人比看似强壮的人生存能力更强。
- matched reaction in timeline: `rx:Full_Content:src:c1:p95@0-p99@176:highlight:60`
- source-span relation: `note_contains_candidate`; coverage `0.4643`
- judge/runner reason: The reaction's source span overlaps the note's opening proposition about sensitive people suffering more physically but less mentally. More importantly, the reaction's content directly interprets and amplifies the core thesis: that sensitivity becomes a "护心之术" (heart-protection mechanism) in extreme conditions by converting external pain into internal meaning. This captures the essential paradox the note intends to highlight, making the narrower overlap (46%) an accurate, focused hit rather than incidental coverage.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0006.json`

### Note `e0007` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0007`
- target note:
```text
爱是人类终身追求的最高目标。我理解了诗歌、思想和信仰所传达的伟大秘密的真正含义：拯救人类要通过爱与被爱。我知道世界上一无所有的人只要有片刻的时间思念爱人，那么他就可以领悟幸福的真谛。
```
- target source span(s):
  - `p100@42-133`: 爱是人类终身追求的最高目标。我理解了诗歌、思想和信仰所传达的伟大秘密的真正含义：拯救人类要通过爱与被爱。我知道世界上一无所有的人只要有片刻的时间思念爱人，那么他就可以领悟幸福的真谛。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0007.json`

### Note `e0008` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0008`
- target note:
```text
天使存在于无比美丽的永恒思念中
```
- target source span(s):
  - `p100@217-232`: 天使存在于无比美丽的永恒思念中
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0008.json`

### Note `e0009` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0009`
- target note:
```text
那就是爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。
```
- target source span(s):
  - `p104@68-134`: 那就是爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。
- matched reaction in timeline: `rx:Full_Content:src:c1:p100@0-p104@134:discern:62`
- source-span relation: `note_contains_candidate`; coverage `0.9545`
- judge/runner reason: The reaction's source span covers 95.45% of the note's text, and the content directly engages with and elaborates on the note's core insight about love transcending physical presence and existence. The reaction explicitly extracts and explains the key distinction (爱一个人≠爱她的肉体) and connects it to the contextual meaning, making this a focused analysis rather than an incidental overlap.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0009.json`

### Note `e0010` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0010`
- target note:
```text
几分钟的寂静后，一名囚犯对另一名感叹道：“世界多美呀！”
```
- target source span(s):
  - `p108@212-240`: 几分钟的寂静后，一名囚犯对另一名感叹道：“世界多美呀！”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0010.json`

### Note `e0011` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0011`
- target note:
```text
幽默是灵魂保存自我的另一件武器。大家都知道，幽默比人性中的其他任何成分更能够使人漠视困苦，从任何境遇中超脱出来，哪怕只是几秒种。
```
- target source span(s):
  - `p114@83-147`: 幽默是灵魂保存自我的另一件武器。大家都知道，幽默比人性中的其他任何成分更能够使人漠视困苦，从任何境遇中超脱出来，哪怕只是几秒种。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0011.json`

### Note `e0012` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0012`
- target note:
```text
培养幽默感并以一种幽默的态度看待事情，是人在掌握生存艺术时学到的技巧。
```
- target source span(s):
  - `p116@0-35`: 培养幽默感并以一种幽默的态度看待事情，是人在掌握生存艺术时学到的技巧。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0012.json`

### Note `e0013` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0013`
- target note:
```text
集中营生活中快乐的匮乏为我们提供了一种消极的幸福——即叔本华所谓 “免于痛苦的自由”
```
- target source span(s):
  - `p124@0-42`: 集中营生活中快乐的匮乏为我们提供了一种消极的幸福——即叔本华所谓 “免于痛苦的自由”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0013.json`

### Note `e0014` — `incidental_cover`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014`
- target note:
```text
如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。这样做可以少挨看守揍，他们就在队伍的前后左右看着我们。中间的位置还有一个好处，就是不易被寒风吹到。因此，为了保全自己就不得不融入人群
```
- target source span(s):
  - `p132@0-99`: 如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。这样做可以少挨看守揍，他们就在队伍的前后左右看着我们。中间的位置还有一个好处，就是不易被寒风吹到。因此，为了保全自己就不得不融入人群
- matched reaction in timeline: `rx:Full_Content:src:c1:p132@0-p132@173:retrospect:83`
- source-span relation: `note_contains_candidate`; coverage `0.3333`
- judge/runner reason: The reaction's quoted span (char 0-33) is contained within the note and does overlap, but the reaction only analyzes the sheep metaphor as a literary device accumulating across pages. It ignores the note's core content about the practical survival logic (avoiding guard beatings, staying warm) and the explicit conclusion about self-preservation through crowd integration. The analysis is tangential to the note's main point.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014.json`

### Note `e0015` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015`
- target note:
```text
犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
```
- target source span(s):
  - `p137@186-215`: 犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
- matched reaction in timeline: `rx:Full_Content:src:c1:p137@0-p137@215:highlight:89`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015.json`

### Note `e0016` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0016`
- target note:
```text
犯人最终成为什么样的人，仍然取决于他自己内心的决定，而不单单取决于集中营生活的影响。
```
- target source span(s):
  - `p167@95-137`: 犯人最终成为什么样的人，仍然取决于他自己内心的决定，而不单单取决于集中营生活的影响。
- matched reaction in timeline: `rx:Full_Content:src:c1:p164@0-p167@349:discern:104`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0016.json`

### Note `e0017` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0017`
- target note:
```text
陀思妥耶夫斯基说过：“我只害怕一样——那就是配不上我所受的痛苦。”
```
- target source span(s):
  - `p167@192-226`: 陀思妥耶夫斯基说过： “我只害怕一样——那就是配不上我所受的痛苦。”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0017.json`

### Note `e0018` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018`
- target note:
```text
如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
```
- target source span(s):
  - `p168@156-214`: 如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
- matched reaction in timeline: `rx:Full_Content:src:c1:p168@0-p168@214:highlight:106`
- source-span relation: `note_contains_candidate`; coverage `0.6552`
- judge/runner reason: The reaction's quoted span (176-214) overlaps a significant portion of the note, and the reaction's commentary directly engages with the note's core argument about '不可剥离' (inseparable) and '不完整' (incomplete) — the claim that suffering is not an obstacle to overcome but a constitutive condition of a complete life. This captures the note's essential philosophical contribution.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018.json`

### Note `e0019` — `incidental_cover`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0019`
- target note:
```text
在这样的情况下，这种困苦环境所提供的能使人道德完善的机会，有的人会充分运用它，有的人会放弃它。这也决定了他是否配得上自己所遭受的苦难。
```
- target source span(s):
  - `p169@101-168`: 在这样的情况下，这种困苦环境所提供的能使人道德完善的机会，有的人会充分运用它，有的人会放弃它。这也决定了他是否配得上自己所遭受的苦难。
- matched reaction in timeline: `rx:Full_Content:src:c1:p169@0-p173@125:highlight:107`
- source-span relation: `note_contains_candidate`; coverage `0.2985`
- judge/runner reason: The reaction's quoted span overlaps only the final consequence clause of the note ('这也决定了他是否配得上自己所遭受的苦难'), covering 29.85% of the note's text. While the reaction correctly interprets the significance of '配得上' as treating suffering as a character test, it isolates this conclusion from the note's main point about the moral opportunity in hardship and the active choice to use or abandon it. The reaction addresses the end result without engaging the note's central reasoning about how different responses to the opportunity determine one's worthiness of suffering.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0019.json`

### Note `e0020` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0020`
- target note:
```text
看不到 “临时的存在”何时结束的人，也不可能去追求生活的终极目标。他不再像正常人那样为了将来而生存。因此，他内在生命的这个结构就改变了，我们从生活其他领域所知道的堕落迹象就开始了。
```
- target source span(s):
  - `p178@32-122`: 看不到 “临时的存在”何时结束的人，也不可能去追求生活的终极目标。他不再像正常人那样为了将来而生存。因此，他内在生命的这个结构就改变了，我们从生活其他领域所知道的堕落迹象就开始了。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0020.json`

### Note `e0021` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0021`
- target note:
```text
在集中营里，一天过得比一个星期慢。
```
- target source span(s):
  - `p178@311-328`: 在集中营里，一天过得比一个星期慢。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0021.json`

### Note `e0022` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0022`
- target note:
```text
看不到未来的人之所以自甘沉沦，是因为他发现自己老在回忆。
```
- target source span(s):
  - `p180@0-28`: 看不到未来的人之所以自甘沉沦，是因为他发现自己老在回忆。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0022.json`

### Note `e0023` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0023`
- target note:
```text
但剥去当下的现实性就会蕴涵着一个危险，那就是容易忽视积极度过集中营生活的机会，而的确存在这样的机会。
```
- target source span(s):
  - `p180@53-103`: 但剥去当下的现实性就会蕴涵着一个危险，那就是容易忽视积极度过集中营生活的机会，而的确存在这样的机会。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0023.json`

### Note `e0024` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0024`
- target note:
```text
正是在极端困苦的环境下，人才有实现精神升华的机会。
```
- target source span(s):
  - `p180@160-185`: 正是在极端困苦的环境下，人才有实现精神升华的机会。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0024.json`

### Note `e0025` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0025`
- target note:
```text
他们不是把集中营的苦难看做对自身内在力量的考验，而是很不严肃地对待自己的生命，把生命轻易抛弃。
```
- target source span(s):
  - `p180@185-232`: 他们不是把集中营的苦难看做对自身内在力量的考验，而是很不严肃地对待自己的生命，把生命轻易抛弃。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0025.json`

### Note `e0026` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0026`
- target note:
```text
他们更愿意闭上眼睛，生活在过去之中。对这些人来说，生命是无意义的。
```
- target source span(s):
  - `p180@232-265`: 他们更愿意闭上眼睛，生活在过去之中。对这些人来说，生命是无意义的。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0026.json`

### Note `e0027` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0027`
- target note:
```text
人的独特之处在于只有人才能着眼于未来。在极端困难的时刻，这就是他的救赎之道，不过他得迫使自己将精神专注于此。
```
- target source span(s):
  - `p182@83-137`: 人的独特之处在于只有人才能着眼于未来。在极端困难的时刻，这就是他的救赎之道，不过他得迫使自己将精神专注于此。
- matched reaction in timeline: `rx:Full_Content:src:c1:p180@0-p184@214:discern:113`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0027.json`

### Note `e0028` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0028`
- target note:
```text
斯宾诺莎在《伦理学》中谈到 “作为痛苦的激情，一旦我们对它有了清晰而明确的认识，就不再感到痛苦了”。
```
- target source span(s):
  - `p184@163-214`: 斯宾诺莎在 《伦理学》中谈到 “作为痛苦的激情，一旦我们对它有了清晰而明确的认识，就不再感到痛苦了”。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0028.json`

### Note `e0029` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0029`
- target note:
```text
尼采说过：“知道为什么而活的人，便能生存。”
```
- target source span(s):
  - `p194@35-57`: 尼采说过：“知道为什么而活的人，便能生存。”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0029.json`

### Note `e0030` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0030`
- target note:
```text
我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。
```
- target source span(s):
  - `p195@45-75`: 我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。
- matched reaction in timeline: `rx:Full_Content:src:c1:p193@0-p197@106:discern:121`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0030.json`

### Note `e0031` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0031`
- target note:
```text
生命最终意味着承担与接受所有的挑战，完成自己应该完成的任务这一巨大责任。
```
- target source span(s):
  - `p195@138-174`: 生命最终意味着承担与接受所有的挑战，完成自己应该完成的任务这一巨大责任。
- matched reaction in timeline: `rx:Full_Content:src:c1:p193@0-p197@106:highlight:122`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0031.json`

### Note `e0032` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0032`
- target note:
```text
“生命”的意义不是某种含糊的东西，而是非常实在和具体的。
```
- target source span(s):
  - `p196@68-96`: “生命”的意义不是某种含糊的东西，而是非常实在和具体的。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0032.json`

### Note `e0033` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0033`
- target note:
```text
没有人能够解除你的磨难，替代你的痛苦。你独特的机会就依存于自己承受重负的方式之中。
```
- target source span(s):
  - `p197@65-106`: 没有人能够解除你的磨难，替代你的痛苦。你独特的机会就依存于自己承受重负的方式之中。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0033.json`

### Note `e0034` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0034`
- target note:
```text
一旦我们明白了磨难的意义，我们就不再通过无视折磨或心存幻想、虚假乐观等方式去减少或平复在集中营遭受的苦难。经受苦难成了一项我们不能逃避的任务。
```
- target source span(s):
  - `p199@0-71`: 一旦我们明白了磨难的意义，我们就不再通过无视折磨或心存幻想、虚假乐观等方式去减少或平复在集中营遭受的苦难。经受苦难成了一项我们不能逃避的任务。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0034.json`

### Note `e0035` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0035`
- target note:
```text
我们意识到了苦难中暗藏着的成功机会，诗人称这种机会为“要经受多少磨难啊
```
- target source span(s):
  - `p199@71-106`: 我们意识到了苦难中暗藏着的成功机会，诗人称这种机会为“要经受多少磨难啊
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0035.json`

### Note `e0036` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0036`
- target note:
```text
我们有太多的苦难要经受，因此，必须直面所有的苦难，不能软弱，眼泪是无用的，但也不必讳言流泪，因为眼泪见证了人们承受痛苦的巨大勇气。
```
- target source span(s):
  - `p199@138-203`: 我们有太多的苦难要经受，因此，必须直面所有的苦难，不能软弱，眼泪是无用的，但也不必讳言流泪，因为眼泪见证了人们承受痛苦的巨大勇气。
- matched reaction in timeline: `rx:Full_Content:src:c1:p199@0-p199@272:highlight:125`
- source-span relation: `note_contains_candidate`; coverage `0.5385`
- judge/runner reason: The reaction's quoted span (168-203) is a central, substantive portion of the note that captures the philosophical core about tears being simultaneously useless yet witnessing courage. The commentary directly engages with this '双重裁定' and builds a meaningful interpretation around it. The reaction's analysis is specifically focused on this central claim rather than tangentially related to it.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0036.json`

### Note `e0037` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0037`
- target note:
```text
一旦他意识到自己是不可替代的，那他就会充分意识到自己的责任。认识到自己对所爱的人或者未竟的事业的责任，也就永远不会抛弃自己的生命。他知道自己存在是 “为了什么”，也就知道 “如何”继续活下去。
```
- target source span(s):
  - `p202@57-153`: 一旦他意识到自己是不可替代的，那他就会充分意识到自己的责任。认识到自己对所爱的人或者未竟的事业的责任，也就永远不会抛弃自己的生命。他知道自己存在是 “为了什么”，也就知道 “如何”继续活下去。
- matched reaction in timeline: `rx:Full_Content:src:c1:p202@0-p203@189:highlight:129`
- source-span relation: `note_contains_candidate`; coverage `0.6771`
- judge/runner reason: The reaction's quoted span (the first two sentences about irreplaceability leading to responsibility and never abandoning life) overlaps substantively with the note's core argument. The reaction's analysis—interpreting the source text as ontological logic where irreplaceability is a structural fact that transforms meaning from value judgment to responsibility attribution—directly engages with and illuminates the note's key claims, not tangential content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0037.json`

### Note `e0038` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0038`
- target note:
```text
尼采的话：“那没能杀死我的，会让我更强壮。”
```
- target source span(s):
  - `p207@205-227`: 尼采的话：“那没能杀死我的，会让我更强壮。”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0038.json`

### Note `e0039` — `miss`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0039`
- target note:
```text
在任何情况下，人的生命都不会没有意义，而且生命的无限意义就包含着苦难、剥夺和死亡。
```
- target source span(s):
  - `p210@45-86`: 在任何情况下，人的生命都不会没有意义，而且生命的无限意义就包含着苦难、剥夺和死亡。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0039.json`

### Note `e0040` — `focused_hit`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0040`
- target note:
```text
当时我感动得热泪盈眶，不只是因为一块面包，他所给我的还有一份人性，跟礼物相伴的是他温暖的话语和仁慈的表情。
```
- target source span(s):
  - `p218@255-308`: 当时我感动得热泪盈眶，不只是因为一块面包，他所给我的还有一份人性，跟礼物相伴的是他温暖的话语和仁慈的表情。
- matched reaction in timeline: `rx:Full_Content:src:c1:p214@0-p218@308:highlight:139`
- source-span relation: `note_contains_candidate`; coverage `0.6038`
- judge/runner reason: The reaction's quoted span covers the note's core content about receiving '一份人性' with warm words and benevolent expression. The reaction's analysis directly engages with this theme—interpreting the bread as a vehicle for '人性' rather than mere sustenance, and connecting it to the broader context of camp dehumanization. This demonstrates genuine focused engagement with the note's important content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0040.json`

### Note `e0041` — `exact_match`

- note_case_id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0041`
- target note:
```text
对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。
```
- target source span(s):
  - `p238@0-61`: 对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。
- matched reaction in timeline: `rx:Full_Content:src:c1:p237@0-p238@61:highlight:148`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0041.json`

## Reading Timeline: All Visible Reactions

Every visible reaction in this Eval-1 window is listed in reading order. Fields are conditional: callback/FVI details appear only when the audit found a callback claim; Selective Legibility details appear only when the reaction overlapped a dataset note target.

### Reaction 001 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p5@88:highlight:1`
- source span: `src:c1:p5@63-p5@88`
- source span excerpt:
```text
这是一场为了每天的面包、为了生活、为了朋友的斗争。
```
- visible reaction:
```text
三句话把生存的层次说尽了。不是抽象的苦难，而是一个人最具体的匮乏——面包；最迫切的冲动——活下去；还有那个在极端处境中仍然被保留下来的人际维度。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 002 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p5@88:highlight:2`
- source span: `src:c1:p4@267-p4@292`
- source span excerpt:
```text
与看守相比，这些人更为凶狠，在鞭打囚徒时更为残忍。
```
- visible reaction:
```text
一个令人不安的洞见：暴力不来自外部命令时，反而可能更彻底。囚头为了保住自己的位置，必须表现得比看守更配得上这份工作。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 003 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p6@0-p6@207:highlight:3`
- source span: `src:c1:p6@105-p6@151`
- source span excerpt:
```text
谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。
```
- visible reaction:
```text
选择权变成了凶器。不是刽子手在动手，而是系统把刀递给了每一个想活下去的人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 004 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p6@0-p6@207:highlight:4`
- source span: `src:c1:p6@177-p6@207`
- source span excerpt:
```text
尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。
```
- visible reaction:
```text
这句话把零和逻辑说透了——没有任何生存是干净的，没有任何友情能在这套机制里全身而退。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 005 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p7@0-p7@239:highlight:5`
- source span: `src:c1:p7@207-p7@223`
- source span excerpt:
```text
可以想象我们是如此害怕这一瞟吧！
```
- visible reaction:
```text
括号里这一句是全段唯一的主观出口。作者突然用"我们"介入叙述，语气近乎恳求——这不是修辞，是真实的恐惧。一个号码瞟一眼就能定罪，这种恐惧背后是一套无需语言就能运作的识别与惩罚系统。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 006 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p7@0-p7@239:highlight:6`
- source span: `src:c1:p7@225-p7@239`
- source span excerpt:
```text
他们从不会去问囚犯姓甚名谁。
```
- visible reaction:
```text
这是全段最强的一锤。所有前面的铺垫——没收文件、刺青、缝在衣服上——都在指向这句话。它不只是事实陈述，而是一个系统性的宣告：在这个世界里，人没有名字，只有编号。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 007 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p8@0-p8@110:highlight:7`
- source span: `src:c1:p8@12-p8@33`
- source span excerpt:
```text
人们没有时间也没欲望去考虑道德和伦理问题。
```
- visible reaction:
```text
这句话直接回应了可能的道德追问——不是"道德崩溃"，而是"没时间没欲望"。道德不是被否定了，而是被生存压力彻底挤出视野。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 008 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p8@0-p8@110:discern:8`
- source span: `src:c1:p8@80-p8@110`
- source span excerpt:
```text
他会尽量设法使另一个囚徒、另一个号码来取代他在名单中的位置。
```
- visible reaction:
```text
这是paragraph 6那句"自己或朋友的胜出就意味着另一个的死亡"的具体化操作：不是抽象的零和逻辑，而是"设法让另一个号码替我上名单"这个真实的、可执行的念头。"另一个号码"的措辞呼应了前文"从不问囚犯姓甚名谁"——连推上死亡线的都只是编号。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 009 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p9@0-p9@206:discern:9`
- source span: `src:c1:p9@155-p9@206`
- source span excerpt:
```text
我们这种人之所以能够存活，纯属幸运和上天的庇佑——不管你怎么说——我们当中最优秀的却没有我们这么幸运。
```
- visible reaction:
```text
这是全章迄今最重的一句。不是自谦，而是对生存机制最冷的诊断：活下来的不是最配活的人，只是最幸运的人。那些在道德上更值得活下去的人，反而没有这份运气。这种"幸运"与"优秀"之间的倒置，构成了集中营幸存者最深的心结——活着本身就是一场道德审判未竟的债务。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 010 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p9@0-p9@206:retrospect:10`
- source span: `src:c1:p9@60-p9@155`
- source span excerpt:
```text
囚犯当中还有一种自主选择囚头的过程。一般来说，只有那些经历过集中营的数次转移、在生存斗争中已经无所顾忌的人才能活下来。为了生存，他们可以使用一切手段，诸如人格，甚至还有暴力、偷窃和出卖朋友。
```
- visible reaction:
```text
这里补全了前文"自己或朋友的胜出就意味着另一个的死亡"的操作层面："出卖朋友"是真实的生存手段，不是修辞。而"人格"也可以被"使用"这个措辞，揭示了残酷选择机制下人性的工具化。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p8@0-p8@110:discern:8"]}`
  - judge reason: Prior_link to reaction 8; correctly references the earlier visible reaction's analysis of '另一个号码' and connects it to betrayal and instrumentalization of personality.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 011 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p10@265:highlight:11`
- source span: `src:c1:p10@24-p10@54`
- source span excerpt:
```text
在这本书中，这种真实情况只是与某个人有直接关系时才具有意义。
```
- visible reaction:
```text
这是全书的方法论锚点：不是宏观历史叙事，而是具体的、有人格重量的个人经验。呼应了前文"书中关注的是普通囚徒"的承诺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly references earlier visible material about '普通囚徒' and its promise, correctly grounding the callback.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 012 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p10@265:highlight:12`
- source span: `src:c1:p10@199-p10@265`
- source span excerpt:
```text
对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。
```
- visible reaction:
```text
这句话构成了一个表达悖论：幸存者声称"不理解"，却仍然在"说"这句话。他们试图沟通的恰恰是那种不可沟通性。这不只是心理创伤的表达，而是对集中营经验之本质的一个哲学判断——它将亲历者与非亲历者永久地分隔在两个不可通约的认知世界。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 013 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p10@265-p14@155:highlight:13`
- source span: `src:c1:p13@277-p13@371`
- source span excerpt:
```text
每张奖券实际相当于50芬尼，通常在几周后，一张奖券可换取六支香烟，尽管有时会失效。手头有12支香烟，我的自豪感便油然而生。但更重要的是，这些香烟还可以换取12份汤，这些汤足以暂时抵挡饥饿。
```
- visible reaction:
```text
奖赏券经济的细节令人震动：12支香烟=12份汤，这是"自豪感"的底层计量单位。这个等式本身就是集中营逻辑的精确缩影——自豪不是成就带来的，而是多换了一份汤。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 014 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p10@265-p14@155:discern:14`
- source span: `src:c1:p14@110-p14@155`
- source span excerpt:
```text
每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
```
- visible reaction:
```text
前文已经揭示了生存的三重斗争：面包、生活、朋友。这里的"勇气"是第四重——也是最内在、最不可逆的一重。前三重是外向的争夺，而勇气是内在的熄灭。并且"几乎就不可能再挽回"与前文"为了生存，他们可以使用一切手段"构成反向呼应：能活下来的人已经耗尽了几乎所有的勇气筹码。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0002` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p14@110-155` 每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
    - target note: 每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly references '前文已经揭示了生存的三重斗争：面包、生活、朋友'—directly connecting to reactions 1 and 3/4's content about the three survival layers.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 015 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p15@0-p16@56:highlight:15`
- source span: `src:c1:p16@0-p16@35`
- source span excerpt:
```text
第一阶段显露的症状是惊恐，有时，这种恐惧在进入集中营之前就已经产生了。
```
- visible reaction:
```text
进入集中营之前的恐惧——这一句值得标记。它暗示收容阶段的惊恐并非始于铁门之内，而是从党卫队的筛选、上车前的命令、甚至得知自己编号的那一刻就已经启动了。三阶段模型的第一阶段实际上前置于物理意义上的"进入"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 016 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p17@0-p17@327:highlight:16`
- source span: `src:c1:p17@155-p17@193`
- source span excerpt:
```text
火车不断地发出怪诞的嘶鸣，像是因怜悯这些注定走向地狱的人们而发出的求助呼喊。
```
- visible reaction:
```text
火车被赋予了同情心——这不是拟人，这是将火车变成了目击者，一个被迫参与却又无力反抗的存在。它的"嘶鸣"和"犹豫"与乘客的心理完全同步，共同承担这份恐惧。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 017 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p17@0-p17@327:highlight:17`
- source span: `src:c1:p17@281-p17@316`
- source span excerpt:
```text
火车慢慢地，犹豫地继续行驶，似乎也在尽可能地拖延乘客意识到恐惧的时间，
```
- visible reaction:
```text
"似乎也在尽可能地拖延"——这个比喻将火车人格化为一个有意识的存在，试图延缓乘客面对现实的时刻。这里火车与人的心理节奏彻底融合：缓慢、挣扎、无法逃避。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 018 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p18@0-p18@178:highlight:18`
- source span: `src:c1:p18@131-p18@146`
- source span excerpt:
```text
除了极度惊恐，我没有其他感觉。
```
- visible reaction:
```text
抵达的那一刻，情感被压缩到最简——不是愤怒、不是屈辱、不是困惑，只有惊恐。这句话的力量在于它的排他性结构：不是"感到惊恐"，而是"除了惊恐没有其他"，仿佛在抵达集中营的瞬间，人的全部心理内容被清空了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 019 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p18@0-p18@178:discern:19`
- source span: `src:c1:p18@146-p18@178`
- source span excerpt:
```text
从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
```
- visible reaction:
```text
这是本段的核心句。"适应"和"习以为常"两个词不是描述麻木，而是描述一种主动的心理重塑——为了存活，大脑必须将极端状态改写为可接受的日常。这与前面关于勇气的不可挽回性构成呼应：恐惧的"习以为常"也是一种一旦形成就难以逆转的状态，只是方向相反。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 020 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p21@0-p25@52:highlight:20`
- source span: `src:c1:p21@291-p21@311`
- source span excerpt:
```text
那时，他们不再是行刑者，而是成了受刑者。
```
- visible reaction:
```text
这个句式——「不再是……而是成了……」——以最简短的逻辑道出了集中营最残酷的时间结构：施害者与受害者的身份不是对立的，而是前后相继的同一批人。毒气室的工人得到无限量杜松子酒，不是因为特权，而是因为他们知道自己也在倒计时。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 021 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p36@171-p40@177:highlight:21`
- source span: `src:c1:p39@0-p39@69`
- source span excerpt:
```text
等待淋浴时，赤条条的身体使我们意识到：除了赤裸的身体，如今我们真的是一无所有。前半生挣下的财富还剩什么？现在，眼镜和皮带就是我的全部财产。
```
- visible reaction:
```text
「一无所有」和「全部财产」放在同一个句子结构里，构成一种极致的反差。「眼镜」和「皮带」——一个关乎残存的尊严（看不清一切就无法确认自己是谁），一个关乎最后一点流通能力——这两个物品被并列说出来的时候，人的存在已经被压缩到了最低限度。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 022 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p36@171-p40@177:highlight:22`
- source span: `src:c1:p40@54-p40@144`
- source span excerpt:
```text
一些囚徒则陷入了真正的麻烦，他们听取了接待室里那些高级囚徒的善意建议，剪去长筒靴的上部使其变短，并在剪口处抹上肥皂加以掩饰。党卫军似乎早有预料，所有剪过靴子的同谋被关进隔壁的房间。
```
- visible reaction:
```text
「善意建议」这四个字在此处读来令人窒息。高级囚徒不是施害者，他们也曾是被剥夺的人，他们的建议出于真实的好意。但这种好意被系统性地利用为陷阱——党卫军的「早有预料」说明这根本就是预设的抓捕链条。同谋一起受刑，这个「同谋」用法精准得可怕：你以为你们在互相帮助，其实在共同入套。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 023 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p41@0-p42@100:discern:23`
- source span: `src:c1:p41@16-p41@39`
- source span excerpt:
```text
出乎意料的是，大多数人开始被冷酷的幽默感战胜。
```
- visible reaction:
```text
「被战胜」这个措辞很精准——幽默不是主动释放的，而是某种力量把人大面积地接管了。更值得留意的是「冷酷」二字：幽默里有寒意，有解冻之后反而更冷的东西。不是温暖的互助式玩笑，而是赤条条的身体之间的自嘲，喷头里流出的水成为庆幸的理由——这种幽默的距离感，恰好是心理防线重塑的证据。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 024 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p41@0-p42@100:highlight:24`
- source span: `src:c1:p42@43-p42@100`
- source span excerpt:
```text
在登山遇险的关键时刻，人们只会有一种感觉，即好奇。人们会好奇自己能否脱险，好奇自己将会粉身碎骨还是仅仅受点儿轻伤。
```
- visible reaction:
```text
这个类比值得记住：登山遇险时的心理状态被拿来等价于集中营里的人的状态。好奇不是求知欲，而是一种悬置恐惧之后的观察——人在极端处境里把自身当作一个陌生事件来打量。恐惧被好奇替代，或者说好奇是恐惧的解离形式：不是「我害怕」，而是「我会怎样」。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 025 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p43@0-p46@138:retrospect:25`
- source span: `src:c1:p46@0-p46@138`
- source span excerpt:
```text
如果现在有人问我们陀思妥耶夫斯基 “把人定义为可以习惯任何事物的种群”的观点是否正确，我们肯定会回答：“是的，人可以习惯任何事物，但请不要问我们是如何习惯的。”我们的心理调查还没到达那么深入的程度，囚徒的心理也没有达到能够习惯的程度。到目前为止，我们仍处于心理反应的第一阶段。
```
- visible reaction:
```text
「不要问我们如何习惯的」这句话值得细读。它不是在否认适应本身，而是拒绝说出适应的机制——那个过程一旦被言说，就会暴露某种让人无法直视的东西。同时「仍处于心理反应的第一阶段」这句话暗示后面还有更深的阶段，这些更深的阶段里会发生什么，叙述者没有说，但这本身就是一个悬置的威胁。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0003` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p46@51-78` “是的，人可以习惯任何事物，但请不要问我们是如何习惯的
    - target note: “是的，人可以习惯任何事物，但请不要问我们是如何习惯的
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction precisely centers on the core phrase from the note ('不要问我们如何习惯的') and provides a substantive interpretation of its meaning: the refusal to articulate the adaptation mechanism because doing so would reveal something unbearable. The analysis genuinely engages with the note's central idea rather than merely citing it peripherally.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003.json`
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p41@0-p42@100:highlight:24"]}`
  - judge reason: Prior_link to reaction 24; correctly references the earlier visible reaction about mountain trekper analogy to support the 'don't ask how we adapted' reading.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 026 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p43@0-p46@138:highlight:26`
- source span: `src:c1:p44@24-p44@112`
- source span excerpt:
```text
一名医生甚至惊呼：“教科书在撒谎！”教科书上说，当睡眠时间不足规定的小时数时，人就不能生存，错！我也一直确信有些事情我做不到：没有这个我不能入睡，没有那个或别的什么我不能生存。
```
- visible reaction:
```text
「教科书在撒谎」这个惊呼里有一种朴素的反讽：不是对知识本身的质疑，而是因为现实比教科书更残酷，残酷到连睡眠规律都失效了。随之而来的「我也一直确信有些事情我做不到」——这些信念在进入集中营后全部崩塌。这个细节很具体：信念不是被思想击破的，而是被极端环境直接碾过的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 027 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p47@0-p47@276:discern:27`
- source span: `src:c1:p47@0-p47@54`
- source span excerpt:
```text
几乎每个人都动过自杀的念头，这种念头源于绝望的处境，源于时时刻刻笼罩着的死亡危险和不断接近他人的死亡的事实。
```
- visible reaction:
```text
「几乎每个人」这个词在这里不是修辞，而是一个精确的集体诊断。叙述者不是在说自己有自杀念头，而是在说整个群体都经历了这个状态——它不是个体的软弱，而是极端处境的系统性产物。这为整个叙述奠定了一个心理基线：站在这个起点上，之后任何的心理反应（好奇、冷漠、对毒气室的接受）都是在已经有了这个念头的基础上展开的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly references '前面积累的那个' psychological baseline, establishing connection to earlier visible material about psychological stages; no prior_link field but native surfaced evidence shows thematic grounding in accumulated earlier content.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 028 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p47@0-p47@276:discern:28`
- source span: `src:c1:p47@253-p47@276`
- source span excerpt:
```text
不要忘了，毒气室至少可以使他们免除自杀的麻烦。
```
- visible reaction:
```text
「免除麻烦」这个说法冷酷到了极点，却因此具有一种奇怪的诚实。它不是在美化毒气室，而是揭示了一种极端处境下的功利逻辑：死亡已经被安排好了，你不需要亲自动手。这个逻辑隐含的前提是——自杀念头确实存在，而且确实需要某种出口，只是这个出口已经被外部力量接管了。它同时暗示：真正让人恐惧的不是死亡本身，而是死亡之前的那个等待——毒气室至少结束这个等待。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 029 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p48@0-p48@323:highlight:29`
- source span: `src:c1:p48@241-p48@322`
- source span excerpt:
```text
他关于这个M的判断是错误的，他的善言具有误导性。因为一位约60岁的棚屋街区医生犯人曾告诉过我他是如何祈求M博士放过他将被送进毒气室的儿子，可M博士却冷冷地拒绝了。
```
- visible reaction:
```text
"善言具有误导性"——这个判断本身值得注意。在集中营中，善意与误导并不矛盾。传递安慰的人自己没有可靠的判断依据，他的信息来自已被现实否定的预期。这和前文那些"我一直确信"的信念崩解是同一种结构：人在极端环境中失去了辨别真假的能力，连安慰都可能是建立在错误之上的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 030 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p49@0-p53@154:retrospect:30`
- source span: `src:c1:p53@140-p53@154`
- source span excerpt:
```text
人的正常反应受到强烈的抑制。
```
- visible reaction:
```text
这句话是整个粪便段落的重心，却轻描淡写。"强烈抑制"的不只是厌恶感，而是"正常人"这个概念本身在身体层面的被取消。这个抑制不是隐喻，而是字面意义的：你的情感反应系统必须死机才能让你活下来。这与第二阶段"情感进入一种死亡状态"构成因果链——先是被环境强制压制，随后情感自己学会了死。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:psychological-first-stage"]}`
  - judge reason: Prior_link to active_attention:psychological-first-stage; correctly grounds the analysis of emotional suppression in the earlier visible framework about first-stage psychological response.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 031 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p54@0-p55@272:highlight:31`
- source span: `src:c1:p55@96-p55@223`
- source span excerpt:
```text
他看到一个12岁的男孩被带进医务室，这个男孩因为集中营没有他穿着合适的鞋子，被迫在雪地里执勤或在户外干活站了几个小时之后，脚趾被严重冻伤。值班医生用镊子一点点地拽去变黑坏死的部分，而我们这位旁观者的感情却已经麻木，无法真切地感受到厌恶、恐惧或怜悯等情感。
```
- visible reaction:
```text
这个场景的具体性让它超越了"情感麻木"的标签。一个12岁的孩子，只因为没有合适的鞋子，就被冻伤了脚趾。而"合适的鞋子"这个细节——这本是集中营最基本的配给——让这个男孩的处境显得既具体又绝望。医生用镊子拽去坏死组织的动作描写，与旁观者的无动于衷之间的对比，比任何关于麻木的抽象陈述都更有力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 032 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p56@0-p57@191:highlight:32`
- source span: `src:c1:p56@134-p56@151`
- source span excerpt:
```text
连只拿到细绳的人都会因此沾沾自喜。
```
- visible reaction:
```text
这个细节把剥夺推到了最小单位——连一根绳子都成了值得高兴的战利品。这是「情感死亡」概念在生存最底层逻辑里的具体化：当最基本的东西都成了奢望，任何微小所得都值得庆祝，无论它来自何处。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 033 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p56@0-p57@191:highlight:33`
- source span: `src:c1:p57@150-p57@191`
- source span excerpt:
```text
在几个月的集中营生活里，如果不用手抓住门框，我们几乎无法登上那些约6英寸高的台阶。
```
- visible reaction:
```text
这个细节暗示了心理死亡与身体衰竭之间的互文——心理上的麻木不只是精神状态，也是长期饥饿在身体上留下的痕迹。叙述者把它作为背景一笔带过，但它同时支撑了前面积累的那个「情感进入死亡状态」的概念，说明这种心理状态是有物质基础的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 034 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p58@0-p61@87:highlight:34`
- source span: `src:c1:p61@60-p61@87`
- source span excerpt:
```text
正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
```
- visible reaction:
```text
这里把心理死亡从损耗的副作用重新框架为生存的适应性策略。"冷漠外壳"这个词暗示的不是情感的丧失，而是一层保护层的形成——叙述者不再把麻木当作问题，而是当作在酷刑频繁发生之地唯一可靠的防线。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0004` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p61@0-87` 冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
    - target note: 冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
    - source-span relation: `note_contains_candidate`; coverage `0.31`
    - judge/runner reason: The reaction directly interprets and elaborates on the overlapped source span ("正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。"), reframing it as a protective strategy, which captures the essential content of that span.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 035 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p58@0-p61@87:highlight:35`
- source span: `src:c1:p59@78-p59@116`
- source span excerpt:
```text
两个小时前，我们还在交谈，现在却阴阳两隔。这个念头一闪而过，我继续低头喝汤。
```
- visible reaction:
```text
这个"一闪而过"和"继续低头喝汤"的动作，把刚才积累的情感反应推向了更深处——不是麻木，而是连悲伤的间隙都不再存在。这与前面积累的「情感进入死亡状态」直接呼应，但程度更深。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 036 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p62@0-p63@257:discern:36`
- source span: `src:c1:p63@191-p63@257`
- source span excerpt:
```text
他只是戏谑地捡起一块石头向我扔来。在我眼里，这样的举动更像是吸引野兽的注意或者吆喝家禽和畜生时，人们因为没必要惩罚它们而使出的伎俩。
```
- visible reaction:
```text
「犯不上」这个词精准地揭示了最深的伤害——不是愤怒的暴力，而是连惩罚都嫌浪费精力的冷漠。被视为不值得言语交流的对象，比被殴打更摧毁人作为人的根基。这与前面积累的「去人格化」概念形成递进：不仅是失去财产和姓名，而是连被当作有尊严的主体来对待的资格都被否认。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 037 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p62@0-p63@257:discern:37`
- source span: `src:c1:p63@0-p63@31`
- source span excerpt:
```text
很奇怪，在一些情况下，不留痕迹的鞭打比留下痕迹的鞭打更伤人心。
```
- visible reaction:
```text
这句话建立了一个关键的心理伤害层级：物理伤痕可见证、可承受，但当伤害不留痕迹地刻在心理深处——那种不被当人看的经历——反而更难以被承认、也无人见证，因而更加难以愈合。这推进了「冷漠外壳」的概念：囚徒学会的不仅是忍受疼痛，而是抵御那种将自身非人化的凝视。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 038 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p64@0-p64@282:highlight:38`
- source span: `src:c1:p64@97-p64@145`
- source span excerpt:
```text
能被选中干活也是让他十分高兴的事，因为一般来说，身体残疾的人在面临第一次选择时肯定要被送上死路。
```
- visible reaction:
```text
「能被选中干活」这件事本身就被定义为一种幸运——因为残疾意味着直接送死。这个老朋友「十分高兴」的原因是倒错的：不是因为活着，而是因为被判定为还有劳动力可用。这里「第一次选择」的残酷含义终于落实为具体的生存博弈。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 039 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p65@0-p69@71:highlight:39`
- source span: `src:c1:p69@1-p69@35`
- source span excerpt:
```text
老实说，我是为穷人开诊所的，大多数情况下我分文不取。”我说的太多了。
```
- visible reaction:
```text
这句话揭示了一种反直觉的生存法则：在极端环境中，暴露真实的价值取向比隐藏身份更危险。监工无法处理"不收钱的医生"这种存在，因为这颠覆了他关于医生的一切预设。当诚实变成挑衅，善意成为获罪的理由。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 040 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p70@0-p70@166:retrospect:40`
- source span: `src:c1:p70@32-p70@64`
- source span excerpt:
```text
他的愤怒不是由于自己所承受的残忍或疼痛，而是出自与之相关的侮辱。
```
- visible reaction:
```text
这里建立了愤怒的不同层次：身体痛苦是可被"适应"的（之前的心理防御机制），但侮辱——被迫接受一个无知者的审判——却突破了这种适应框架，成为无法被消化的心理创伤。这与前文"不留痕迹的鞭打比留下痕迹的鞭打更伤人心"形成另一个层级：可见的伤痕可以被承受和见证，但被贬低为非人的判断却无人见证、无从诉诸。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p62@0-p63@257:discern:37"]}`
  - judge reason: Prior_link to reaction 37; correctly references the earlier visible reaction's analysis of invisible psychological wounds and connects it to the layers of humiliation and unworthiness.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 041 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p71@0-p75@102:discern:41`
- source span: `src:c1:p75@0-p75@28`
- source span excerpt:
```text
第二阶段的主要症状是冷漠，这也是必不可少的自我保护机制。
```
- visible reaction:
```text
这个定义比第一阶段的所有描述都更彻底。好奇可以悬置，幽默可以反身，但冷漠意味着主动关闭——对他人命运的冷漠、对自身痛苦之外一切的冷漠。这不是麻木，而是策略性的情感切除术。这直接回应了前面追踪的「第一阶段」悬置，它不是更深的适应，而是适应之后真正来临的心理状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确引用前文'第一阶段'概念，并直接回应其悬置状态，指出冷漠不是麻木而是适应之后的真正心理状态。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 042 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p71@0-p75@102:discern:42`
- source span: `src:c1:p72@327-p72@369`
- source span excerpt:
```text
作为私下公认的大囚头儿御用医生，我稳稳当当地走在队伍第一排，同时也为此感到十分高兴。
```
- visible reaction:
```text
这里的「十分高兴」与之前「能被选中干活也是让他十分高兴的事」形成同一个倒错模式：不是为活着高兴，而是为在淘汰机制中仍被标记为「有用」而高兴。叙述者用一种黑色幽默式的清醒标注自己的高兴，这本身就是一种心理防御——他知道自己处境的可悲，但选择用「十分高兴」来消解它。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提及'十分高兴'与前文某处形成相同倒错模式，但仅是主题层面的重复指出，缺乏精确锚定。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 043 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p76@0-p76@107:discern:43`
- source span: `src:c1:p76@89-p76@107`
- source span excerpt:
```text
囚徒们的希望和梦想只能在梦中被表现。
```
- visible reaction:
```text
这句话与前文「冷酷的幽默」形成对照。幽默是意识层面的主动防御（可以把玩自己的处境），但「希望和梦想只能在梦中被表现」意味着意识层面已经无法容纳这些东西——它们被排挤到无意识的梦境中。这不是幽默的反面，而是更深层的退化：即便在梦里，囚徒仍然只能看到被剥夺了一切的状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确指向'冷酷的幽默'这一前文标记，将幽默（意识防御）与梦中的希望（无意识退缩）作对比。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 044 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p77@0-p78@178:retrospect:44`
- source span: `src:c1:p78@113-p78@146`
- source span excerpt:
```text
那一刻，我强烈意识到，不管梦有多恐怖也比集中营的现实状况要好得多。
```
- visible reaction:
```text
这句话将集中营的现实定性为「比噩梦更恐怖」——不是隐喻，而是字面意义上的比较。叙述者在此做出了一种冷硬的优先排序：噩梦是可接受的，因为它有尽头；集中营的现实是无尽头的，因此更糟。这不是绝望，而是极端环境下的清醒成本计算。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p71@0-p75@102:discern:41"]}`
  - judge reason: 通过prior_link明确引用reaction 41，将集中营现实与噩梦的比较框架建立在之前对冷漠的定义之上。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 045 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p77@0-p78@178:highlight:45`
- source span: `src:c1:p78@85-p78@113`
- source span excerpt:
```text
我还是猛地把手抽了回来，一想到会叫醒他，我突然有点后怕。
```
- visible reaction:
```text
「后怕」这个词用得准确——不是怕打扰对方的睡眠，而是怕让他面对清醒后的现实。这是叙述者对自身处境最具体的一次顿悟时刻：通过阻止一个同情举动，他发现了现实的真正重量。那个「猛地把手抽回来」的动作，是整段最有力的身体叙事。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 046 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p79@0-p79@146:highlight:46`
- source span: `src:c1:p79@10-p79@36`
- source span excerpt:
```text
精神生活的重点重新回到对食物的渴望这样的原始本能上。
```
- visible reaction:
```text
「重新回到」这个表述值得注意——它暗示了一个退化的方向。囚徒的精神生活不是往前发展出什么新的能力，而是向后撤退到最原始的层级。「原始本能」这个词也再次呼应了前文对囚徒心理状态的整体刻画。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 047 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p79@0-p79@146:highlight:47`
- source span: `src:c1:p79@115-p79@146`
- source span excerpt:
```text
计划他们与家人重逢那天，也就是遥远的未来获释回家后那天的菜谱。
```
- visible reaction:
```text
「遥远的未来」这个表述在这里具有双重含义：一是实际的遥远（不知何时能获释），二是逻辑上的遥远（这个未来可能永远不会到来）。但囚徒们仍然在认真「计划菜谱」——这种认真的计划行为本身，就已经是他们抵御完全崩溃的一种方式。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 048 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p79@146-p83@134:highlight:48`
- source span: `src:c1:p82@197-p82@250`
- source span excerpt:
```text
每天夜间抓虱子时，看到赤裸裸的身体，我们就会有同一个想法：这样的躯干——我们的身体——实际上已经是僵尸了。
```
- visible reaction:
```text
「抓虱子」这个细节把日常行为变成了认识论时刻——当囚徒在夜间裸露身体互相清除虱子时，他们同时在进行一种集体性的自我确认。这个行为让「僵尸」不再是一个比喻，而成为经过赤裸身体验证的事实。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 049 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p79@146-p83@134:highlight:49`
- source span: `src:c1:p83@100-p83@134`
- source span excerpt:
```text
像现在这样除了美味佳肴不会再想到其他任何东西的次等生存状态终将结束。
```
- visible reaction:
```text
「次等生存状态」这个命名有结构意义：它将当前的生存明确定义为一种降格的、低于正常人类的状态。这种命名本身暗示了一个隐含的正常标准——而渴望那个标准，正是维持精神存续的方式。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 050 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p84@0-p88@163:highlight:50`
- source span: `src:c1:p88@64-p88@163`
- source span excerpt:
```text
当我从奥斯维辛转往达豪集中营下属的一个集中营时，居然产生了回家的感受。半夜，运载我们约2000名囚徒的火车经过维也纳的一个火车站，沿着火车的轨道依次经过我出生的街道，经过我做囚徒前居住多年的老宅子。
```
- visible reaction:
```text
「居然」这个词值得注意——它表明连叙述者自己都对这种感受感到意外。这不是自我欺骗，而是极端处境对「家」这一概念的彻底倒置：家变成了一个无法触及的抽象，而可预测的囚禁反而成为某种可依附的东西。火车经过出生街道而不停——这本身就是一种极致的流离。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 051 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p84@0-p88@163:highlight:51`
- source span: `src:c1:p86@210-p86@251`
- source span excerpt:
```text
看到这可怕的一幕，我只好自己找点安慰。我从口袋里摸出那份小面包，美滋滋地大吃起来。
```
- visible reaction:
```text
「看到」别人的崩溃，然后「自己找点安慰」——这个转折没有自我谴责，也没有内疚，只是冷静地执行了一种生存逻辑。看到同伴的惨状不是激起同情，而是触发自我保护式的进食。这种心理反应本身就说明了一件事：他已经没有多余的情感带宽去承受他人的痛苦。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 052 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p89@0-p89@197:highlight:52`
- source span: `src:c1:p89@94-p89@150`
- source span excerpt:
```text
我们都感觉到与其说自己活着不如说已经死了，因为一直认为这次旅途的终点是毛特豪森，所以估计自己最多也就再活一两周。
```
- visible reaction:
```text
「与其说自己活着不如说已经死了」——这不是绝望，而是一种主动的心理重新定位。放弃对「活着」的期待，意味着同时也放弃了希望破灭时的反复撕裂。把自己当作已死之人，反而获得了一种奇异的平静。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 053 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p89@0-p89@197:highlight:53`
- source span: `src:c1:p89@150-p89@197`
- source span excerpt:
```text
我明显感觉自己是在用阴间人的眼光看我童年生活的街道、广场和房屋，俯瞰着这个令人毛骨悚然的城市。
```
- visible reaction:
```text
「阴间人的眼光」——这个措辞精确而有力。「俯瞰」故乡这个动作，将前文所说的「悬置式好奇」推进到了极限：不是麻木，不是习惯，而是彻底的精神位移。从旁观者的距离看自己的来处，故乡变成了景观，变成了「毛骨悚然的城市」。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提到'悬置式好奇'的推进，但与reaction 24的链接未经确认，属于暗示性关联。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 054 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p90@0-p90@149:highlight:54`
- source span: `src:c1:p90@57-p90@91`
- source span excerpt:
```text
他们专心致志地通过窥孔向外凝视，我乞求甚至哀求他们让我站在前面片刻。
```
- visible reaction:
```text
「专心致志」和「乞求甚至哀求」之间的对比很有力量。那些第一次看到街道的年轻人保持着完整的好奇心，而叙述者——那个真正有故事、有资格说「我的街道」的人——反而被推开了。创伤最深的人反而最没有资格看。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 055 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p90@149-p91@156:highlight:55`
- source span: `src:c1:p91@9-p91@13`
- source span excerpt:
```text
文化冬眠
```
- visible reaction:
```text
政治和宗教"除外"这一点值得注意。几乎一切文化生活都冬眠了，但政治和宗教没有——因为它们直接关涉囚犯的命运：政治决定生死，宗教提供意义框架。这两个领域的"幸存"并非活跃，而是因为它们不能冬眠，否则就等于放弃最后的生命线。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 056 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p90@149-p91@156:discern:56`
- source span: `src:c1:p91@123-p91@156`
- source span excerpt:
```text
一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。
```
- visible reaction:
```text
"彻底绝望"的原因被追溯到"不可救药的乐观派"——这是关键的社会性因果。绝望不是因为坏消息本身，而是因为反复被好消息欺骗；乐观派的危害在于：他们让同伴经历了不必要的希望-幻灭循环，每一次幻灭都在消耗残存的活下去的理由。这种绝望是二手的，是被乐观派"传染"和"透支"后的结果。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 057 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p92@0-p93@246:highlight:57`
- source span: `src:c1:p93@118-p93@164`
- source span excerpt:
```text
我的一位朋友严重昏迷，他认为自己快要死了，想做祈祷，但由于神智昏迷，他竟然不知道该祈祷什么。
```
- visible reaction:
```text
这句话揭示了一个关键的不对称：信仰的意志仍然存在（他想祈祷），但信仰的执行能力已经被摧毁（不知道该祈祷什么）。这比单纯失去信念更可怕——他知道自己在失去什么，却无能为力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 058 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p92@0-p93@246:highlight:58`
- source span: `src:c1:p93@164-p93@246`
- source span excerpt:
```text
为了避免昏迷，我也和其他人一样尽量在夜里保持清醒。我需要在脑海里用几个钟头组织语言，重新构思我在奥斯维辛传染病房里丢失的手稿，或者干脆用速记法在小纸片上记下关键词。
```
- visible reaction:
```text
「保持清醒」在这里不是被动的状态，而是一种主动的心理劳作——用组织语言和记录关键词来对抗神志不清。这与前文「心理反应的第一阶段」形成呼应，提示叙述者仍在使用有意识的心理策略来维持自己的认知完整性，而不是进入被动接受状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 059 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p94@0-p94@124:highlight:59`
- source span: `src:c1:p94@105-p94@124`
- source span excerpt:
```text
参加者围成一圈，还来了一名党卫军军官。
```
- visible reaction:
```text
这个细节有一种难以言说的诡异：犯人与加害者围坐同一圈，参与同一场秘密的精神活动。这不是简单的「人性尚存」，而是一种更复杂的场景——在这间私人小病房里，日常世界的等级秩序似乎短暂悬置，但它的在场本身就构成了悬置得以可能的条件。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 060 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p95@0-p99@176:highlight:60`
- source span: `src:c1:p96@42-p96@94`
- source span excerpt:
```text
有丰富的精神生活且比较敏感的人在这里会承受更多痛苦 （他们身体也会更弱），但对内心的伤害相应也会少许多。
```
- visible reaction:
```text
这是本书的核心生存悖论之一：敏感不是弱点，在极端环境中反而是护心之术——因为它能将外部痛苦转化为内部意义，从而在外在意义上损失最少。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0006` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0006` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p96@42-154` 有丰富的精神生活且比较敏感的人在这里会承受更多痛苦 （他们身体也会更弱），但对内心的伤害相应也会少许多。他们能把恶劣的外部环境转化成内心丰富自由的精神生活，只有这样才能解释集中营中身体羸弱的一些人比看似强壮的人生存能力更强。
    - target note: 有丰富的精神生活且比较敏感的人在这里会承受更多痛苦（他们身体也会更弱），但对内心的伤害相应也会少许多。他们能把恶劣的外部环境转化成内心丰富自由的精神生活，只有这样才能解释集中营中身体羸弱的一些人比看似强壮的人生存能力更强。
    - source-span relation: `note_contains_candidate`; coverage `0.46`
    - judge/runner reason: The reaction's source span overlaps the note's opening proposition about sensitive people suffering more physically but less mentally. More importantly, the reaction's content directly interprets and amplifies the core thesis: that sensitivity becomes a "护心之术" (heart-protection mechanism) in extreme conditions by converting external pain into internal meaning. This captures the essential paradox the note intends to highlight, making the narrower overlap (46%) an accurate, focused hit rather than incidental coverage.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0006.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 061 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p95@0-p99@176:highlight:61`
- source span: `src:c1:p99@148-p99@176`
- source span excerpt:
```text
不论真实与否，我都坚信她的外貌比冉冉升起的太阳还要明亮。
```
- visible reaction:
```text
"不论真实与否"这几个字至关重要——它坦承了这种明亮的理想化性质，却也正因为坦承而更具力量。不是因为她真的比太阳亮，所以值得坚守；而是无论真假，这种确信本身就是集中营中最后的自由领地。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 062 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p100@0-p104@134:discern:62`
- source span: `src:c1:p104@71-p104@134`
- source span excerpt:
```text
爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。
```
- visible reaction:
```text
这里有一个隐含的深刻区分：爱一个人≠爱她的肉体。在极端环境中，「不知妻子是否还活着」这个念头非但没有摧毁他的爱，反而促成了对爱的更本质理解——所爱之人的在场与否、存亡与否，都不是爱的边界；真正重要的是爱以何种方式终止。这意味着爱是一种独立于被爱对象的价值。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0009` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0009` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p104@68-134` 那就是爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。
    - target note: 那就是爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。
    - source-span relation: `note_contains_candidate`; coverage `0.95`
    - judge/runner reason: The reaction's source span covers 95.45% of the note's text, and the content directly engages with and elaborates on the note's core insight about love transcending physical presence and existence. The reaction explicitly extracts and explains the key distinction (爱一个人≠爱她的肉体) and connects it to the contextual meaning, making this a focused analysis rather than an incidental overlap.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0009.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 063 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p105@0-p109@374:highlight:63`
- source span: `src:c1:p109@287-p109@374`
- source span excerpt:
```text
我强烈感觉到她的存在，她陪伴在我身旁，我甚至有伸手触摸她或抓住她的冲动，她就在身边的感觉越来越强烈。就在那一刻，一只鸟飞下来，刚好落在我面前，在我挖壕沟的土堆上直直地盯着我。
```
- visible reaction:
```text
鸟的降临不是偶然的文学点缀。"直直地盯着我"——这个"直直"暗示了一种有意识的、带有见证性质的注视。它同时完成了三件事：将内在的精神体验外在化，将"她在身边"这个不可见的确信可见化，并在"看守侮辱我"的同一时刻，引入了一个完全不同的观察者。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 064 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p110@0-p110@259:highlight:64`
- source span: `src:c1:p110@192-p110@217`
- source span excerpt:
```text
所有这一切都是为了帮助我们忘却，当然这也的确管用。
```
- visible reaction:
```text
「忘却」二字直接说出来了。与前文关于爱和记忆的讨论形成反向镜像——不是守住什么，而是在集体中一起忘掉。这是一种功能性的、解脱式的精神出口，与持守式精神力量分属不同层次。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 065 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p110@0-p110@259:highlight:65`
- source span: `src:c1:p110@226-p110@259`
- source span excerpt:
```text
有的普通犯人不顾疲惫与饥饿来看卡巴莱表演，甚至误了领取当天的份饭。
```
- visible reaction:
```text
在食物就是生死筹码的环境里，用一顿饭去换一场演出——这说明了集体性忘却的需求有多迫切。也呼应了前文对普通犯人处境的关注：他们不是英雄，他们也需要relief，哪怕代价高昂。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 066 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p111@0-p111@156:highlight:66`
- source span: `src:c1:p111@74-p111@107`
- source span excerpt:
```text
在大家贪婪地吸溜稀汤的时候，一名犯人爬到桶上，唱起了意大利咏叹调。
```
- visible reaction:
```text
在生存本能的「贪婪」和文化的「咏叹调」之间，这个犯人的一跃完成了从动物性进食到人性的跳跃。动作本身——爬到桶上——既是卑微的，又是勇敢的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 067 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p112@0-p113@307:retrospect:67`
- source span: `src:c1:p113@213-p113@307`
- source span excerpt:
```text
提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。那个人正躺在奥斯维辛集中营的另一个地方，也许近到仅几百米的距离，也许远至几千米之遥，却与我全然隔绝。那个人就是我的妻子。
```
- visible reaction:
```text
不是「忘却」，而是「记得」——用音乐记住。用「流畅」和「美」来承受绝望，用生日日期来锚定记忆。这与前文关于艺术用于忘却的论述形成反向镜像。提琴的哭泣与叙述者身体的哭泣同步，是身体对音乐的情感反应，无法伪装，也无法压抑。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p110@0-p110@259:highlight:64"]}`
  - judge reason: 通过prior_link明确引用reaction 64，形成'忘却'与'记得'的精确反转，音乐记忆与艺术忘却形成对照。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 068 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p114@0-p117@198:highlight:68`
- source span: `src:c1:p117@160-p117@198`
- source span excerpt:
```text
囚犯们为此在车厢里跳起了欢乐的舞蹈，不是亲身经历的话，那个场面简直难以想象。
```
- visible reaction:
```text
从极度紧张（害怕被送往毛特豪斯）到在车厢里跳舞，只因为列车没有跨过那座桥。这不是理性的快乐计算——而是"苦难的量已经被占满"之后，任何微小的转向都成了纯粹的盈余。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 069 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p119@0-p119@149:highlight:69`
- source span: `src:c1:p119@125-p119@149`
- source span excerpt:
```text
起码这个集中营里没有烟囱，奥斯维辛又离得那么远。
```
- visible reaction:
```text
这是庆幸逻辑的终点——「烟囱」意味着毒气室，「奥斯维辛够远」意味着暂时安全。他们的快乐不在于任何正面事物，而在于最坏的选项被暂时排除在外。这与前文提到的「乐观派令同伴气愤」形成暗线：这里的「开心」是被剥夺到极限之后的最低阈值满足。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提到'乐观派令同伴气愤'的暗线，但仅主题层面关联，缺乏精确锚定。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 070 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p120@0-p120@147:highlight:70`
- source span: `src:c1:p120@21-p120@66`
- source span excerpt:
```text
当时我们觉得，苦难的相对性是多么明显呀！我们嫉妒那些管理相对好、相对安全、相对幸福的犯人。
```
- visible reaction:
```text
「相对幸福」这个词本身就是一种扭曲——在集中营内部，洗澡和牙膏竟然成了「幸福」的尺度。但叙述者用这个词是准确的，因为对极度剥夺之下的人来说，这确实是幸福。它不是与外界的比较，而是营内各部分之间的残酷分层。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 071 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p120@0-p120@147:highlight:71`
- source span: `src:c1:p120@85-p120@147`
- source span excerpt:
```text
他们肯定有牙膏、衣服刷子和褥子——每人一套——每月还能收到亲人的来信，至少知道他们是否还活着。而我们很久以前就失去这一切了。
```
- visible reaction:
```text
「至少知道他们是否还活着」——这句话的重量在于：失去家人来信，不只是失去联系，而是一种持续的死亡焦虑。与前文（某人的24岁生日、提琴与妻子的记忆）形成暗线：叙述者自己的妻子就躺在几百米外却全然隔绝。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提及'24岁生日''提琴与妻子的记忆''叙述者妻子'等暗线，但属于theme-level连接，缺乏具体可见文本锚定。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 072 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p121@0-p123@110:discern:72`
- source span: `src:c1:p122@182-p122@245`
- source span excerpt:
```text
没人能够想象出类似情况下空袭警报带给你的解脱，哪怕是那些因比赛结束铃声响起而得以避免在最后一分钟被击倒的拳击手也会难以理解吧。
```
- visible reaction:
```text
空袭警报在这个语境里完全反转了意义——它不是灾难的信号，而是暴行的中断器。拳击手的类比很精确：真正让人解脱的不是胜利，而是在被彻底击垮之前，比赛被叫停了。叙述者在两小时的折磨之后，距离被装上「运送已死或垂死之人的雪橇」只差一步。这个细节让人看到，营内不仅有人杀人，还有系统性地让人「出事故」的设计——而空袭警报打断了这个设计一次。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 073 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p121@0-p123@110:discern:73`
- source span: `src:c1:p123@0-p123@21`
- source span excerpt:
```text
在这里，我们对最微不足道的仁慈也心存感激。
```
- visible reaction:
```text
这句话是整段的结穴。「仁慈」这个词已经被压缩到最小尺度——不是给予什么，而是不做什么：灯没关、空袭没响。而「感激」的对象是一个赤裸站在挂着冰柱的屋里的人，他没法捉完虱子，只希望不被咬一整夜。这是「相对幸福」逻辑的最终落地：在极端剥夺中，快乐不是某种正面事物的存在，而是某种负面事物的缺席。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 074 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p124@0-p124@265:highlight:74`
- source span: `src:c1:p124@192-p124@231`
- source span excerpt:
```text
他是唯一一个不看人下菜碟、能做到均等分汤的厨子，他也从不照顾自己的朋友或同胞。
```
- visible reaction:
```text
「不看人下菜碟」——这句话在集中营语境里的重量完全翻转了。在正常世界里，这是对服务行业的基本要求；在奥斯维辛，它是快乐的理由。这个词选得精准，因为它暗示的不是伟大的善行，而仅仅是不做坏事本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 075 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p124@0-p124@265:highlight:75`
- source span: `src:c1:p124@231-p124@265`
- source span excerpt:
```text
其他厨子不是这样，他们给朋友或同胞捞土豆，只给其他犯人从上面舀清汤。
```
- visible reaction:
```text
「从上面舀清汤」这个细节值得标记：它说明清汤是浮在表面的，而土豆沉在锅底。「从上面舀」是一个主动的选择性动作，不是无意的。这一句揭示了歧视的结构：不是忽略公平，而是有意地、系统性地亏待非己者。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 076 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p125@0-p128@71:highlight:76`
- source span: `src:c1:p127@312-p127@383`
- source span excerpt:
```text
我当时觉得，那个兄弟是多么可怜，而我自己有多么幸运，居然生了病，并因此可以躺在病号房里打盹！在那里待上两天，也许还能再多待几天，真是救命的呀！
```
- visible reaction:
```text
这句是整个段落的张力中心。「那个兄弟」与「我自己」的对比在这里不是冷漠，而是系统在剥夺了一切之后的最后一道防线——幸运不是拥有什么，而是没有轮到自己承受更多。这个句式在集中营叙事中反复出现，但每一次仍然有效，因为它把「庆幸」和「同情」压缩进了同一个呼吸里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 077 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p125@0-p128@71:discern:77`
- source span: `src:c1:p128@22-p128@71`
- source span excerpt:
```text
经过我这样的解释，那人明白了我为什么不觉得那张照片有多可怕，照片上的人也不见得像他想象得那么倒霉。
```
- visible reaction:
```text
「不见得像他想象得那么倒霉」——这句话没有否认照片中的处境是悲惨的，而是精确地指向了观察者与经历者之间那道无法弥合的裂缝：外部判断的标准建立在一套不同的参照系上，而这个参照系在集中营里早已失效。这呼应了前面「任何人都没有资格去评判别人」的道德立场，但把它从断言推进成了可演示的案例。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 078 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p129@0-p130@98:highlight:78`
- source span: `src:c1:p130@0-p130@19`
- source span excerpt:
```text
对我来说，这仅仅是权衡，不能说是牺牲。
```
- visible reaction:
```text
「权衡」而非「牺牲」——这个措辞是全文最冷静的一笔。叙述者拒绝了英雄主义的自我叙事，把自己定格在一套没有情感附加值的成本核算里。这不是谦逊，而是极端环境下将意义降到最低可计算单位之后的语言特征。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 079 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p129@0-p130@98:highlight:79`
- source span: `src:c1:p130@64-p130@98`
- source span excerpt:
```text
我们看起来是那么虚弱，他担心手上会多出两具尸体，而不是多出两个医生。
```
- visible reaction:
```text
这句话的力量在于它从外部戳破了第一段的全部前提：叙述者自认为在做一个主动的、有意义的选择，而医官眼中看到的是两个即将成为尸体的人。这个落差——自选的意义与客观的濒危——在同一段文本里并存，构成了一种叙事者自己尚未意识到的讽刺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 080 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p131@0-p131@394:highlight:80`
- source span: `src:c1:p131@171-p131@229`
- source span excerpt:
```text
如果集中营的犯人不竭力抵挡住这种影响以保存自尊，他就会失去人的感情，没有了精神，没有了内在的自由，没有了个人的价值。
```
- visible reaction:
```text
这是一个条件句，但它揭示的不是可能性，而是几乎必然的进程：不去抵抗，就失去一切。而"保存自尊"在这里成了抵抗的唯一锚点——不是希望，不是信念，而是自尊。这个门槛低到几乎可以执行，又高到意味着全部。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 081 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p131@0-p131@394:highlight:81`
- source span: `src:c1:p131@362-p131@394`
- source span excerpt:
```text
而我们，这群羊，只想着两件事情——如何躲开恶狗或找到一小块吃的。
```
- visible reaction:
```text
"恶狗"与"吃的"——守卫与面包，两个最原始的关切，被并置在同一句话里，将人降低到条件反射的层次。这句话的残忍在于它的平淡语气：叙述者不是在控诉，只是在报告自己已经变成了什么。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 082 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p132@0-p132@173:retrospect:82`
- source span: `src:c1:p132@126-p132@155`
- source span excerpt:
```text
这是遵守集中营里自我保全的一条最要紧的法则，即不要太显眼。
```
- visible reaction:
```text
"法则"这个词在这里有一种令人不安的分量：它不是建议，不是习惯，而是规律性的、被普遍执行的生存条令。"不要太显眼"——五个字，概括了一种持续监控的自我状态：永远在意识自己的位置、姿势、可见度。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p131@0-p131@394:highlight:81"], "note": "前一段中\"恶狗\"与\"吃的\"并置，将人降低到条件反射层次；这里\"法则\"这个词将同样的行为提升到了规律的高度——两句话共同构成了生存逻辑的完整表达：最低层的本能反应 + 最高层的规律确认"}`
  - judge reason: Explicitly links to reaction:81, correctly extending the previous 'conditioned reflex' observation to '法则' as systematic pattern elevation.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 083 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p132@0-p132@173:retrospect:83`
- source span: `src:c1:p132@0-p132@33`
- source span excerpt:
```text
如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。
```
- visible reaction:
```text
"如同绵羊"——前面p131已经用过"这群羊"，这里再次出现同一个意象，但这次有了身体行为的填充：不只是被动地被定义为羊，而是主动地执行羊的动作。羊的隐喻在积累。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0014` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p132@0-99` 如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。这样做可以少挨看守揍，他们就在队伍的前后左右看着我们。中间的位置还有一个好处，就是不易被寒风吹到。因此，为了保全自己就不得不融入人群
    - target note: 如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。这样做可以少挨看守揍，他们就在队伍的前后左右看着我们。中间的位置还有一个好处，就是不易被寒风吹到。因此，为了保全自己就不得不融入人群
    - source-span relation: `note_contains_candidate`; coverage `0.33`
    - judge/runner reason: The reaction's quoted span (char 0-33) is contained within the note and does overlap, but the reaction only analyzes the sheep metaphor as a literary device accumulating across pages. It ignores the note's core content about the practical survival logic (avoiding guard beatings, staying warm) and the explicit conclusion about self-preservation through crowd integration. The analysis is tangential to the note's main point.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014.json`
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p131@0-p131@394:highlight:81"], "note": "前一段\"这群羊，只想着两件事情\"，这里的\"如同绵羊\"是同一隐喻的再次激活，但增加了具体行为描写"}`
  - judge reason: Explicitly links to reaction:81, accurately identifying the recurring sheep metaphor with added behavioral detail.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 084 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p133@0-p133@348:retrospect:84`
- source span: `src:c1:p133@0-p133@84`
- source span excerpt:
```text
当然，有时不仅有可能，而且有必要躲开人群。大家都知道，在强制性的集体生活中，每个人的一举一动都在众目睽睽之下，这就让你有一种不可抗拒的逃离人群的冲动，哪怕只是一小会儿。
```
- visible reaction:
```text
"不可抗拒的逃离人群的冲动"——这是集中营生存机制中一种反向需求的提出。前面（p131-p132）已经在讲"不要太显眼"的法则，讲人群中的自我压缩；这里进一步揭示：被强制置于集体之中的人，反而产生了对独处的深刻需要。这种需要在"休息营"里仅得到五分钟的满足，而这五分钟还被置于尸体旁边。这不是隐喻性的孤独，而是字面意义上的：独处只有在死人堆里才成为可能。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p132@0-p132@173:retrospect:82", "reaction:rx:Full_Content:src:c1:p132@0-p132@173:retrospect:83"]}`
  - judge reason: Links to reactions 82 and 83, correctly tracing progression from '不要太显眼' self-compression to the new '逃离人群的冲动' need for solitude.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 085 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p133@0-p133@348:highlight:85`
- source span: `src:c1:p133@263-p133@348`
- source span excerpt:
```text
我就那么坐着，透过乱七八糟的铁丝网，望着外面长满野花的山坡和远处巴伐利亚地区蓝色的山岗。我梦想着，思绪忽而飘向北边，忽而飘向东北边，飘向我家乡的方向，可我看到的只有白云。
```
- visible reaction:
```text
"可我看到的只有白云"——整段最重的一句。思绪向家乡飞行，但视野被铁丝网切割，最终只有白云。家乡在方向里，不在视线里；梦可以到达，视觉无法到达。这种双重阻隔——铁丝网的物理切割和"只有白云"的意义空洞——比直接表达思乡之痛更有力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 086 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p134@0-p134@255:discern:86`
- source span: `src:c1:p134@131-p134@174`
- source span excerpt:
```text
病情极重的病号不给药，因为吃药也不管用了，这么点药还是留给那些还有希望好转的病人好了。
```
- visible reaction:
```text
这是集中营版的" triage"——战场或灾难中的医疗分诊原则。极度稀缺下，"不值得救"与"还能救"之间划出一条生死线。"还有希望好转"成了分配标准：谁的康复概率高，谁先用。叙述者执行这套逻辑时没有犹豫，也没有道德负罪感——恰恰是这种平静，让它读来比哭诉更令人不安。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 087 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p136@0-p136@354:highlight:87`
- source span: `src:c1:p136@145-p136@201`
- source span excerpt:
```text
一个犯人的意义就在于他有号码，因此囚号才是最要紧的。犯人成了名副其实的号码，不管你是活着还是死了，死活倒不重要。
```
- visible reaction:
```text
「名副其实」四个字是点睛之笔——它暗示这个转化并非隐喻，而是字面意义上的身份替换：一个人不再是人，只是一串数字的容器。生死之间的差异在这里被彻底抹平。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 088 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p136@0-p136@354:highlight:88`
- source span: `src:c1:p136@266-p136@354`
- source span excerpt:
```text
有个年轻的犯人，因为他的兄弟不在名单上，所以他就得留下来。经他苦苦哀求，号长决定来个调换：他顶替了另外一个愿意留下来的人。但是名单不能对不上！他的兄弟只得跟被顶替的人换了号码。
```
- visible reaction:
```text
整个段落最有力的地方在于：兄弟之间的交换不是为了救人，而是为了凑数。最终被顶替的人成了数字缺口的填补物——他的命运完全取决于数字逻辑是否需要他。这种偶然性揭示了系统的本质：活着的理由不是人的价值，而是数字的匹配。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 089 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p137@0-p137@215:highlight:89`
- source span: `src:c1:p137@186-p137@215`
- source span excerpt:
```text
犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
```
- visible reaction:
```text
这与前文"犯人成了名副其实的号码"形成不同层面的剥除：号码是制度的抽象化，这里是权力的任意化。两种剥除叠加——制度把你变成数字，狱卒的情绪让你觉得连数字都不如。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0015` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p137@186-215` 犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
    - target note: 犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly links to '犯人成了名副其实的号码' from earlier visible material, correctly extending it to '权力的任意化' as a distinct second layer of dehumanization.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 090 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p138@0-p139@190:discern:90`
- source span: `src:c1:p138@39-p138@113`
- source span excerpt:
```text
这条规矩就是要如实回答所有问题，但是对没有明确问及的一切都保持沉默。如果问我的年龄，我会告诉他们。问我的职业，我也会如实回答 “医生”，但不作解释。
```
- visible reaction:
```text
「如实回答」与「沉默」的组合构成了一种精准的信息边界——只交付被索取的，不给予任何多余的联想空间。在一个以剥除身份为手段的系统里，这套策略本质上是对信息泄漏的主动封堵。但真正值得注意的并非策略本身，而是它被叙述为「规矩」而非「本能」——这意味着叙述者在进入集中营时就已经启动了某种系统化的自我管理，而非被环境推着走。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 091 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p138@0-p139@190:discern:91`
- source span: `src:c1:p139@123-p139@190`
- source span excerpt:
```text
82名犯人马上报了名。25分钟后，运输任务取消了，但82名犯人还在值夜班的名单上。对他们大多数人来说，那意味着在以后的几个礼拜中死亡。
```
- visible reaction:
```text
这个结构有完整的内部逻辑：行动基于预期→预期落空→行动的后果逆转成死亡。「82名犯人马上报了名」说明他们是清醒的、主动的，并非绝望中的胡乱一搏；但正是这份清醒使悲剧更具分量——他们不是在赌，而是以为自己算清了，而算清的结果恰好与现实完全相反。这与前文反复出现的「筛选」不同：筛选是外部强加的，这里是内部决策的失效，两者共同构成生存的不可能性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 092 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p145@0-p149@181:highlight:92`
- source span: `src:c1:p148@0-p148@202`
- source span excerpt:
```text
集中营的犯人害怕做决定，也不敢采取任何主动行为。这是因为他们强烈地感觉到一切皆有定数，不要试图去影响命运，而应该听从命运的安排。此外，犯人们对一切都漠然处之，这也在很大程度上影响了他们的情绪。有时，你得在瞬间做出意味着生死的决断。犯人则更愿意让命运替他做这个决断。在决定是否逃跑的时候，犯人这种逃避责任的心理表现得最明显。在那样需要几分钟内拿定主意的时刻，他遭受着地狱般的折磨。是试着逃跑，还是放弃冒险？
```
- visible reaction:
```text
"逃避责任的心理"这个措辞值得注意：它不是"无力"，不是"恐惧"，而是"逃避责任"——这暗示了一种主动的心理让渡：不是不能做决定，而是不愿意承担决定的后果，因此把决定权外包给命运。这与"适应"机制（早期段落）属于同类心理结构的不同侧面：适应是把痛苦外包给日常感，逃避责任是把选择权外包给命运。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 093 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p150@0-p150@280:discern:93`
- source span: `src:c1:p150@255-p150@280`
- source span excerpt:
```text
我进去找到了一个背包和一把牙刷，还发现了一具女尸。
```
- visible reaction:
```text
三个宾语并列：「背包」「牙刷」「女尸」。没有过渡、没有停顿、没有情绪词。搜刮生存物资与发现死亡并列，这意味着在集中营里，发现尸体已经内化为日常搜索行为的一部分，而非需要单独标记的事件。这种平静本身就是一种精神状态的体现——不是麻木，而是已经将「身边有尸体」整合进了正常活动的框架。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 094 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p151@0-p151@366:highlight:94`
- source span: `src:c1:p151@242-p151@294`
- source span excerpt:
```text
突然，我决定自己拿一次主意。我跑出去告诉那个朋友我不跟他跑了。一说出这句话，那种不安的感觉就顿时消失了。
```
- visible reaction:
```text
「自己拿一次主意」——这个表述直接呼应了前文关于犯人「逃避责任」「不敢采取主动行为」的描述。叙说者打破了这个模式，而他打破它的方式是：拒绝行动。这里存在一个悖论结构——在集中营语境下，最大胆的决定往往恰恰是「不做某事」，而非「做某事」。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly links to earlier material about犯人'逃避责任' and '不敢采取主动行为', correctly identifying '自己拿一次主意' as breaking that pattern.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 095 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p151@0-p151@366:discern:95`
- source span: `src:c1:p151@294-p151@323`
- source span excerpt:
```text
我不知道接下来会发生什么事，但我内心得到了前所未有的平静。
```
- visible reaction:
```text
「前所未有的平静」与前文的不安形成对照——前者是拒绝逃跑后即刻获得的，而不是等到结果出现之后。这个平静不是建立在确定性之上的，它是真正的内在状态，而非外部结果的折射。这与「82名犯人」段落中那种建立在错误预期上的行动形成镜像式对比：这里是平静源于决定本身，那里是死亡源于预期落空。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Claims contrast with '前文的不安' but does not cite a specific prior reaction; self-referential contrast without verifiable earlier anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 096 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p152@0-p152@205:discern:96`
- source span: `src:c1:p152@192-p152@205`
- source span excerpt:
```text
我和我的朋友再次决定逃跑。
```
- visible reaction:
```text
与前一段「我决定自己拿一次主意……不跟他跑了」形成直接逆转。那个决定带来的是平静，这一次「再次逃跑」说明处境已经完全不同——前一次是拒绝参与一次冒险，这一次是面对被活活烧死的威胁。两次决定方向相反，但本质相同：都是自主选择，而非屈从指令。这可能是全书最后一个自主选择的时刻。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly links to prior section '拒绝参与一次冒险', correctly identifying this as a direct reversal of that earlier decision pattern.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 097 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p153@0-p154@177:highlight:97`
- source span: `src:c1:p153@212-p153@256`
- source span excerpt:
```text
经过三年的监禁，我想象着自由的快乐，想象着奔向战线该是多么奇妙，但我们最终没能走那么远。
```
- visible reaction:
```text
这一句将三年的监禁与"自由的快乐"并置，同时又以"没能走那么远"做了反讽式收尾。叙述者的想象力在这里成为唯一的逃亡工具，而他恰恰在最需要行动的时候发现自己只能想象。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 098 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p153@0-p154@177:highlight:98`
- source span: `src:c1:p154@117-p154@177`
- source span excerpt:
```text
这样，谁还再想逃跑的事？车上卸下来不少药箱，每人都分到了香烟，拍了照，大家感到无比欢快，我们也用不着冒险往战线那边跑了。
```
- visible reaction:
```text
这个反问句是全段的枢纽：它将外部保护降临的瞬间定义为逃跑计划的终结点。"用不着冒险"与前文"我们制定了计划"的主动冒险形成鲜明落差——叙述者曾经需要自己拿主意，如今连这个需要也被外部力量取消了。香烟、拍照、欢快，都在这取消之后发生。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 099 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p155@0-p159@141:discern:99`
- source span: `src:c1:p158@36-p158@61`
- source span excerpt:
```text
我们发现人的决定是多么无常，尤其是事关生死的决定。
```
- visible reaction:
```text
这句话在叙述完那13个朋友的惨死后说出来，显得格外沉痛。"无常"——不是残忍的系统性决策，而是偶然和疏忽。叙述者活下来，不是因为正确或勇敢，而仅仅是因为被漏点了。这个"决定的无常"与之前那句"勇气一旦失去，几乎就不可能再挽回"形成对照：勇气是可贵的、不可挽回的；而剥夺人生命的那只手，却是懈怠的、随机的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 100 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p155@0-p159@141:discern:100`
- source span: `src:c1:p156@172-p156@189`
- source span excerpt:
```text
还说我们的运气真好，应当感激他们。
```
- visible reaction:
```text
这句话在极度反讽中成立：党卫军一边在清空集中营送人去死，一边宣称这是"运气好"。叙述者用了"不敢认"这个词——他认不出这些人就是之前那些凶残的党卫军。但他们的"友好"恰恰说明，之前的凶残不是性格，而是功能——当需要清空集中营时，他们又可以表现得友善。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 101 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p160@0-p160@373:discern:101`
- source span: `src:c1:p160@77-p160@148`
- source span excerpt:
```text
人们对于自身内在价值的认识寄托于更高、更精神性的事物上，这种精神性的事物不会被集中营生活摧垮，但又有多少自由的人拥有这样的自觉，更不用说囚犯？
```
- visible reaction:
```text
这个括号里的反问将囚犯的困境升华为对所有人的普遍追问。叙述者在这里暗示了一种逃离路径——将自身价值寄托于精神性事物，使其不受集中营生活摧垮——随即又用反问将这条路堵死：即便自由人也很少拥有这种自觉，囚犯就更不用说了。这句话不是悲观的断言，而是一种诚实的观察：极端环境暴露了平常状态下被遮蔽的精神脆弱性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 102 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p160@0-p160@373:discern:102`
- source span: `src:c1:p160@149-p160@178`
- source span excerpt:
```text
一般犯人尽管没有明确地意识到，但都觉得自己被极大地贬低了。
```
- visible reaction:
```text
「没有明确地意识到」与「都觉得」之间的张力值得注意：自卑情结不是被明确认识的判断，而是弥散的、被感受到的贬低感。这种「觉得」是一种身体性、情感性的感知，而非认知性的认识。这与前文提到的「悬置式好奇」（不问「我害怕」而问「我会怎样」）形成呼应——极端环境下，知觉本身被重塑，既是防御也是适应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 103 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p161@0-p163@254:highlight:103`
- source span: `src:c1:p162@54-p162@149`
- source span excerpt:
```text
当局经常借检查卫生之名虐待犯人。虽然犯人们更需要多一点食物、多一点药品，但当局只关心走廊里是否落下一根稻草，破破烂烂而爬满臭虫的布片是否整齐地裹在病人的脚上。至于犯人的命运，他们根本不在意。
```
- visible reaction:
```text
稻草与脚上的布片 vs. 食物和药品——这个对比用具体的荒谬替代了抽象的控诉。"卫生"这个词加了引号，本身就是一种讽刺。系统性地把人的命运替换为表面的整洁，这种"检查"的本质不是卫生，而是对人格的最后一层剥夺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 104 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p164@0-p167@349:discern:104`
- source span: `src:c1:p167@95-p167@137`
- source span excerpt:
```text
犯人最终成为什么样的人，仍然取决于他自己内心的决定，而不单单取决于集中营生活的影响。
```
- visible reaction:
```text
这句话是全文迄今最直接的核心论点。「不单单取决于」是一种精确的保守表述——外部条件确实限定了可能性，但充分条件落在内心决定这一侧。这与前文关于「习以为常」的适应机制并不矛盾，因为那是低层的生存策略，而这里说的是高层的人格性决定。两者属于不同层级。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0016` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0016` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p167@95-137` 犯人最终成为什么样的人，仍然取决于他自己内心的决定，而不单单取决于集中营生活的影响。
    - target note: 犯人最终成为什么样的人，仍然取决于他自己内心的决定，而不单单取决于集中营生活的影响。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0016.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 105 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p168@0-p168@214:highlight:105`
- source span: `src:c1:p168@156-p168@176`
- source span excerpt:
```text
如果说生命有意义，那么遭受苦难也有意义。
```
- visible reaction:
```text
条件命题的等式：生命有意义 → 苦难有意义。这不是比喻或安慰，而是一种逻辑上的绑定——意义不是可以切割的，不能说「生活有意义但苦难没有意义」，因为苦难是生活的组成部分。这个命题为后续的绝对判断埋下伏笔。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0018` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p168@156-214` 如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
    - target note: 如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
    - source-span relation: `note_contains_candidate`; coverage `0.34`
    - judge/runner reason: The reaction anchors on only the first sentence of the note, analyzing it as a logical conditional. However, the note presents a three-sentence cumulative argument about suffering, misfortune, and death being integral to life. The reaction's 34.48% coverage captures only the conditional premise without addressing the note's other two sentences about suffering厄运和death being indispensable parts of life and life being incomplete without them. The reaction misses the broader philosophical claim that gives the conditional its full significance.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 106 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p168@0-p168@214:highlight:106`
- source span: `src:c1:p168@176-p168@214`
- source span excerpt:
```text
苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
```
- visible reaction:
```text
「不可剥离」和「不完整」是强措辞。苦难不是需要被克服才能获得完整的东西，而是完整本身的构成条件。这与前文将苦难视为代价或障碍的常见理解形成根本性的逆转。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0018` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p168@156-214` 如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
    - target note: 如果说生命有意义，那么遭受苦难也有意义。苦难、厄运和死亡是生活不可剥离的组成部分。没有苦难和死亡，人的生命就不完整。
    - source-span relation: `note_contains_candidate`; coverage `0.66`
    - judge/runner reason: The reaction's quoted span (176-214) overlaps a significant portion of the note, and the reaction's commentary directly engages with the note's core argument about '不可剥离' (inseparable) and '不完整' (incomplete) — the claim that suffering is not an obstacle to overcome but a constitutive condition of a complete life. This captures the note's essential philosophical contribution.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0018.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 107 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p169@0-p173@125:highlight:107`
- source span: `src:c1:p169@148-p169@168`
- source span excerpt:
```text
这也决定了他是否配得上自己所遭受的苦难。
```
- visible reaction:
```text
「配得上」是一种强措辞。不是「从苦难中获得意义」，而是苦难本身成为考验——你是否能以值得其重量的方式来承担它。这将苦难从需要被合理化的障碍变成了人格性试金石。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0019` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0019` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p169@101-168` 在这样的情况下，这种困苦环境所提供的能使人道德完善的机会，有的人会充分运用它，有的人会放弃它。这也决定了他是否配得上自己所遭受的苦难。
    - target note: 在这样的情况下，这种困苦环境所提供的能使人道德完善的机会，有的人会充分运用它，有的人会放弃它。这也决定了他是否配得上自己所遭受的苦难。
    - source-span relation: `note_contains_candidate`; coverage `0.30`
    - judge/runner reason: The reaction's quoted span overlaps only the final consequence clause of the note ('这也决定了他是否配得上自己所遭受的苦难'), covering 29.85% of the note's text. While the reaction correctly interprets the significance of '配得上' as treating suffering as a character test, it isolates this conclusion from the note's main point about the moral opportunity in hardship and the active choice to use or abandon it. The reaction addresses the end result without engaging the note's central reasoning about how different responses to the opportunity determine one's worthiness of suffering.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0019.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 108 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p169@0-p173@125:highlight:108`
- source span: `src:c1:p172@128-p172@187`
- source span excerpt:
```text
但当我们自己遭遇到厄运、需要决定是否以同样伟大的精神面对厄运时，我们早已忘记了好多年前年轻时候的决心，因此我们失败了。
```
- visible reaction:
```text
这是失败的一种精确描述：不是因为不知道该怎么做，而是因为无法在需要时召回当初的决定。道德决心如果只是审美性地看过、点头认同，就无法在关键时刻被激活——它在咖啡和汉堡中消散了。这个失败模式解释了为什么「知道」不等于「能活出来」。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 109 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p169@0-p173@125:highlight:109`
- source span: `src:c1:p173@110-p173@125`
- source span excerpt:
```text
对我来说，那个场面就像一首诗。
```
- visible reaction:
```text
在证词语境中说「就像一首诗」是一种奇怪的说法——他甚至预见到读者会怀疑他在编造。诗歌与见证之间存在张力：诗是语言美化，而见证要求诚实。但在这里，诗不是修辞，而是说这个场面本身就具有那种完满的形态——在极端中实现了某种不可言说的完整。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 110 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p174@0-p174@224:discern:110`
- source span: `src:c1:p174@37-p174@81`
- source span excerpt:
```text
我感谢命运给了我这么沉重的打击……以前的生命让我糟践了，我从没有认真考虑过精神完美的事。
```
- visible reaction:
```text
「感谢命运给了我这么沉重的打击」——这里的措辞不是「接受」或「承受」，而是「感谢」。这不是斯多亚式的冷漠忍耐，而是一种主动的重新框架：苦难被重新定义为唤醒的媒介。她把自己此前的生命定性为「糟践」，这是一种毫不留情的清醒，而这种清醒恰好是在打击之后才成为可能的。苦难在此不是需要被合理化的障碍，而是使精神觉醒成为必要的条件。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 111 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p174@0-p174@224:discern:111`
- source span: `src:c1:p174@197-p174@224`
- source span excerpt:
```text
它对我说，我在这里，我在这里，我就是生命，永恒的生命。
```
- visible reaction:
```text
「永恒的生命」——这是整段的核心意象。树说的不是「我会活着」而是「我就是生命」，并且是「永恒的」。在一个只能看到一枝两朵花的极其受限的窗口视野里，临终者与自然的这段对话，在弗兰克尔的框架中不是幻觉，而是意义本身的显现——意义不依赖视野的宽阔，而依赖主体是否有能力去回应。这与前文「配得上自己所遭受的苦难」形成内在共振：她不仅承受了苦难，而且从中生出了精神性的理解。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 112 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p175@0-p179@206:highlight:112`
- source span: `src:c1:p179@63-p179@83`
- source span excerpt:
```text
他觉得自己的生命已经终结，好像已经死去。
```
- visible reaction:
```text
这里的"已经"是时态上的关键：不是将要死去，不是濒临死亡，而是心理上已经抵达了死亡——这是意义系统彻底关闭之后的精神状态，而不是生理上的死亡。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 113 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p180@0-p184@214:discern:113`
- source span: `src:c1:p182@83-p182@137`
- source span excerpt:
```text
人的独特之处在于只有人才能着眼于未来。在极端困难的时刻，这就是他的救赎之道，不过他得迫使自己将精神专注于此。
```
- visible reaction:
```text
「迫使自己将精神专注于此」——这里的「迫使」很重要。不是自发的乐观，而是意志的主动介入。在极端剥夺中，注意力不是自然流向未来的，它需要被强行拽过去。这解释了为什么单纯拥有「未来目标」还不够——必须持续、刻意地保持专注，而这种专注本身就已经是一种胜利。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0027` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0027` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p182@83-137` 人的独特之处在于只有人才能着眼于未来。在极端困难的时刻，这就是他的救赎之道，不过他得迫使自己将精神专注于此。
    - target note: 人的独特之处在于只有人才能着眼于未来。在极端困难的时刻，这就是他的救赎之道，不过他得迫使自己将精神专注于此。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0027.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 114 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p185@0-p185@256:highlight:114`
- source span: `src:c1:p185@0-p185@47`
- source span excerpt:
```text
对自己的未来丧失信心的犯人，注定要走向毁灭。由于他对未来失去了信念，他也就丧失了对精神的把握。
```
- visible reaction:
```text
「丧失信心→丧失精神把握→毁灭」——这是一个精确的因果链，直接构成第182段救赎机制的镜像：那里是「迫使自己专注于未来=救赎之道」，这里是失去未来信念=注定毁灭。两者相加，才是完整的心理动力学图景。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 115 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p185@0-p185@256:highlight:115`
- source span: `src:c1:p185@100-p185@128`
- source span excerpt:
```text
我们都害怕这一刻，不是担心我们自己，而是担心我们的朋友。
```
- visible reaction:
```text
恐惧的他者化：不是「我害怕自己崩溃」，而是「我害怕看到朋友崩溃」。这不只是利他，而是一种心理防御——将最深的恐惧投向他人，使它成为可旁观的对象，从而维持自己的清醒。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 116 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p186@0-p186@167:retrospect:116`
- source span: `src:c1:p186@127-p186@166`
- source span excerpt:
```text
我问他战争什么时候结束？你明白我的意思，医生。我就想知道什么时候能够得到解放。
```
- visible reaction:
```text
一个作曲家和词作家，在最梦幻的场景里、在拥有「问任何问题都能得到答案」的最高权限时，选择问的只有一件事：什么时候能解脱。这个选择比任何论证都更直接地表明——在最深层的需求面前，想象力和创造力调动的方向仍然是未来、是解放。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p180@0-p184@214:discern:113"]}`
  - judge reason: Links to reaction:113 but the connection (composer asking about liberation) is inferred rather than explicitly demonstrated in the text evidence.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 117 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p187@0-p191@141:retrospect:117`
- source span: `src:c1:p191@84-p191@124`
- source span excerpt:
```text
3月30日，就是梦中声音告诉他战争将结束的那一天，他陷入了昏迷。第二天，他死了。
```
- visible reaction:
```text
希望之锚的残忍反噬：那个声音指定的日期，本来是F活下去的支点，却最终成为他倒下的日子。不是因为预言「实现」——战争那天没有结束——而是因为预言落空这件事本身杀死了他。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["concept:concept-collapse-inversion"], "note": "直接印证「丧失未来信念→毁灭」的核心机制：F的毁灭不是死于战败或疾病，而是死于「特定日期的希望落空」这一事实本身——希望的锚越精确，落空时毁灭性越大。"}`
  - judge reason: Prior_link references concept:concept-collapse-inversion which is a projection concept tag, not visible surface content from the earlier reaction list.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 118 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p187@0-p191@141:highlight:118`
- source span: `src:c1:p191@0-p191@68`
- source span excerpt:
```text
当F告诉我这个梦时，他充满了希望，确信梦里那个声音所说的是正确的。但随着日子的临近，我们根据得到的消息判断，战争极不可能在那个日子结束。
```
- visible reaction:
```text
对称的时间结构：2月充满希望地讲述→3月初（F视角：还有三周）→3月30日（F身体已无法等待答案）。叙述者在此留下了一个沉默的注脚：他当时判断「战争极不可能」在那日结束，而F却还活着等待。这是两种时间意识之间的错位——清醒的现实判断与被预言锁定的心理时间。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 119 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p192@0-p192@160:retrospect:119`
- source span: `src:c1:p192@47-p192@62`
- source span excerpt:
```text
突然失去希望和勇气会导致死亡。
```
- visible reaction:
```text
这是全书最直接的因果声明。不是比喻，不是精神层面的「毁灭」，而是字面意义上的生理死亡——通过免疫系统介导的因果链。叙述者把这个机制当作已知常识来陈述，语气平静得像在说一个医学事实。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["concept:concept-collapse-inversion"]}`
  - judge reason: Prior_link references concept:concept-collapse-inversion, a projection concept rather than verifiable visible surface material from the earlier list.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 120 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p192@0-p192@160:retrospect:120`
- source span: `src:c1:p192@143-p192@160`
- source span excerpt:
```text
虽然他梦里声音所说的最终都应验了。
```
- visible reaction:
```text
这句话是全段最锋利的反讽。声音是对的——战争在某一天结束了；但F没能活到那一天。预言在事实层面成立，在F的生命时间线上彻底失效。这比「预言错了」更残忍，因为它证明F的死亡不是来自预言的欺骗，而是来自时间的不等人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p187@0-p191@141:retrospect:117"]}`
  - judge reason: Explicitly links to reaction:117 (F's hope anchor), correctly identifying the ironic gap between prophecy being factually correct and F not living to witness it.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 121 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p193@0-p197@106:discern:121`
- source span: `src:c1:p195@45-p195@75`
- source span excerpt:
```text
我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。
```
- visible reaction:
```text
这句话翻转了主客体关系。通常人问「我活着有什么意义」时，是把生活当作一个有待回应自己的客体。但这里的逻辑是反过来的：生活是主体，它在向你提问，你要回答的不是「我想从生活得到什么」，而是「生活要我做什么」。这个翻转意味着意义的发现不是内省的，而是行动性的。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0030` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0030` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p195@45-75` 我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。
    - target note: 我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0030.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 122 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p193@0-p197@106:highlight:122`
- source span: `src:c1:p195@138-p195@174`
- source span excerpt:
```text
生命最终意味着承担与接受所有的挑战，完成自己应该完成的任务这一巨大责任。
```
- visible reaction:
```text
这里用「责任」来定义生命本身——不是「活着是美好的」，而是「活着是一种被赋予的任务」。这种表述和加缪的荒谬哲学有相近处，但方向不同：加缪强调荒谬与反抗的并列，这里强调的是「应该完成的任务」这一结构性词汇，意味着某种超越个人偏好的秩序感。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0031` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0031` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p195@138-174` 生命最终意味着承担与接受所有的挑战，完成自己应该完成的任务这一巨大责任。
    - target note: 生命最终意味着承担与接受所有的挑战，完成自己应该完成的任务这一巨大责任。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0031.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 123 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p198@0-p198@142:retrospect:123`
- source span: `src:c1:p198@61-p198@111`
- source span excerpt:
```text
我们早就过了质问生命意义的阶段，已经不是天真地想通过积极地创造某种有价值的东西实现某个目标的年龄了。
```
- visible reaction:
```text
「过了」这个动词精准地标记了一种被迫的成熟——不是因为理解了什么，而是因为继续追问是一种无法承受的奢侈。这也意味着意义感的获得不是通过新增什么，而是通过放下某些东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p193@0-p197@106:discern:121", "reaction:rx:Full_Content:src:c1:p193@0-p197@106:highlight:122"]}`
  - judge reason: Correctly links to prior_link IDs 121 and 122, extending their discussion of responsibility/tasks by showing meaning emerges from letting go rather than gaining.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 124 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p198@0-p198@142:highlight:124`
- source span: `src:c1:p198@111-p198@142`
- source span excerpt:
```text
对我们来说，生命的意义包含着从生到死受苦受难这一更广阔的循环。
```
- visible reaction:
```text
「更广阔的循环」这个表述把个人苦难纳入了一个不可逃避的宇宙框架。苦难不是需要被克服的障碍，而是意义本身的组成部分——这是集中营处境逼出来的、无法在正常生活中产生的哲学。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 125 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p199@0-p199@272:highlight:125`
- source span: `src:c1:p199@168-p199@203`
- source span excerpt:
```text
眼泪是无用的，但也不必讳言流泪，因为眼泪见证了人们承受痛苦的巨大勇气。
```
- visible reaction:
```text
这个关于眼泪的双重裁定——无用于实际，但见证勇气——拒绝了两个极端：虚假的坚强和感伤的自我放纵。它既不是「忍住不哭」的道德化，也不是「哭出来就好了」的心理化，而是一种更难达到的坦然。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0036` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0036` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p199@138-203` 我们有太多的苦难要经受，因此，必须直面所有的苦难，不能软弱，眼泪是无用的，但也不必讳言流泪，因为眼泪见证了人们承受痛苦的巨大勇气。
    - target note: 我们有太多的苦难要经受，因此，必须直面所有的苦难，不能软弱，眼泪是无用的，但也不必讳言流泪，因为眼泪见证了人们承受痛苦的巨大勇气。
    - source-span relation: `note_contains_candidate`; coverage `0.54`
    - judge/runner reason: The reaction's quoted span (168-203) is a central, substantive portion of the note that captures the philosophical core about tears being simultaneously useless yet witnessing courage. The commentary directly engages with this '双重裁定' and builds a meaningful interpretation around it. The reaction's analysis is specifically focused on this central claim rather than tangentially related to it.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0036.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 126 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p199@0-p199@272:highlight:126`
- source span: `src:c1:p199@217-p199@272`
- source span excerpt:
```text
有时人们不好意思地承认自己曾经痛哭过，在被问及他是如何度过难关时，我的一个狱友就羞答答地说：“我眼泪都哭干了。
```
- visible reaction:
```text
「羞答答」和「哭干了」放在一起有一种奇特的诗意：眼泪流尽不是软弱，而是一种完成。这个细节把前文关于苦难作为任务的哲学，落实到了一个具体的人的窘迫状态里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 127 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p199@272-p201@190:highlight:127`
- source span: `src:c1:p200@38-p200@72`
- source span excerpt:
```text
个体的心理治疗措施常常是 “救命程序”，这些措施一般与预防自杀有关。
```
- visible reaction:
```text
「救命程序」这个说法比「心理治疗」更朴素、更准确。它直接承认了在集中营的处境中，心理学工作首先不是在处理神经症或心理创伤，而是在处理一个原始问题：活下去。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 128 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p199@272-p201@190:highlight:128`
- source span: `src:c1:p201@154-p201@190`
- source span excerpt:
```text
他的著作不可能由别人代写，就好比第一个人作为孩子的父亲无人能够替代一样。
```
- visible reaction:
```text
这是两个锚点同时成立的时刻：一件事（科学家的工作）和一个人（父亲与孩子）。两者都指向同一个结构——不可替代性。这种并列不是修辞，而是对「还有什么能留住一个人」的平行追问。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 129 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p202@0-p203@189:highlight:129`
- source span: `src:c1:p202@57-p202@122`
- source span excerpt:
```text
一旦他意识到自己是不可替代的，那他就会充分意识到自己的责任。认识到自己对所爱的人或者未竟的事业的责任，也就永远不会抛弃自己的生命。
```
- visible reaction:
```text
这里的逻辑是存在论层面的，不是比喻：不可替代性不是一种感觉，而是一种结构性事实——我做的事确实只有我能做，我对所爱的人的责任确实只有我能负。这个推导直接驳斥了「活着有什么意义」的回答路径，因为它把意义从价值判断变成了责任归属。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0037` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0037` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p202@57-153` 一旦他意识到自己是不可替代的，那他就会充分意识到自己的责任。认识到自己对所爱的人或者未竟的事业的责任，也就永远不会抛弃自己的生命。他知道自己存在是 “为了什么”，也就知道 “如何”继续活下去。
    - target note: 一旦他意识到自己是不可替代的，那他就会充分意识到自己的责任。认识到自己对所爱的人或者未竟的事业的责任，也就永远不会抛弃自己的生命。他知道自己存在是 “为了什么”，也就知道 “如何”继续活下去。
    - source-span relation: `note_contains_candidate`; coverage `0.68`
    - judge/runner reason: The reaction's quoted span (the first two sentences about irreplaceability leading to responsibility and never abandoning life) overlaps substantively with the note's core argument. The reaction's analysis—interpreting the source text as ontological logic where irreplaceability is a structural fact that transforms meaning from value judgment to responsibility attribution—directly engages with and illuminates the note's key claims, not tangential content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0037.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 130 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p202@0-p203@189:highlight:130`
- source span: `src:c1:p203@81-p203@99`
- source span excerpt:
```text
行为的直接影响总是比言辞更有说服力。
```
- visible reaction:
```text
这是一个来自极端处境的经验命题，不是道德说教。当一切制度性的治疗框架都被摧毁，剩下唯一可信的传导介质就是具体的人的行为。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 131 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p204@0-p205@158:highlight:131`
- source span: `src:c1:p204@147-p204@165`
- source span excerpt:
```text
自然，2500个犯人更愿意斋戒一天。
```
- visible reaction:
```text
这个"自然"用得很平——不是英雄式的反抗，而是两千五百人在压力下做出的具体选择：宁可全体挨饿，也不交出一个人。这与"筛选机制"里每个人都清楚自己或朋友的胜出意味着另一个的死亡形成了一个持续的背景对位。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 132 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p204@0-p205@158:highlight:132`
- source span: `src:c1:p205@140-p205@158`
- source span excerpt:
```text
在我看来，号长是有意提出这个忠告的。
```
- visible reaction:
```text
叙述者明确点出了号长的意图性——这不是随机谈话，而是在大家情绪糟糕到极点时的刻意干预。结合前文"行为的直接影响总是比言辞更有说服力"，这里的"有意"与号长的具体行为构成了直接对应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 133 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p206@0-p206@101:highlight:133`
- source span: `src:c1:p206@47-p206@73`
- source span excerpt:
```text
我又冷又饿，暴躁而疲惫，但我必须利用这个难得的机会。
```
- visible reaction:
```text
"必须"在这里是绝对性的，不是选择，而是由处境的紧迫性直接发出的命令。这与号长在厨房里的"有意"形成了同一逻辑的两个切面：都是个人在极端状态下主动抓住行动窗口。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 134 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p206@0-p206@101:highlight:134`
- source span: `src:c1:p206@82-p206@101`
- source span excerpt:
```text
站起来鼓励大家的需要比任何时候都迫切。
```
- visible reaction:
```text
"站起来"的身体性动作与"鼓励大家"的社会功能叠合在一起。和号长的"行为的直接影响"那条线形成了明确的承接——这里也是用行动本身来承担功能，而非用言辞。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 135 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p207@0-p207@227:highlight:135`
- source span: `src:c1:p207@51-p207@106`
- source span excerpt:
```text
我说每个人都应该问自己一个问题：我们所遭受的难以挽回的损失是什么？我推测说，对绝大多数人而言，这样的损失很少。
```
- visible reaction:
```text
这个反问框架本身就是一种干预技术——不是告诉人们"你要乐观"，而是引导他们自己去做一次损失盘点，结果指向"其实没那么多"。这与号长的"有意忠告"和叙述者自己的"必须利用机会"构成了同一个逻辑链条上的三个节点：引导→时机把握→具体行动。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 136 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p208@0-p212@142:highlight:136`
- source span: `src:c1:p210@150-p210@230`
- source span excerpt:
```text
我说有人在看着我们在艰难环境中的表现，这个人可能是朋友、妻子或者活着和死去的他人，甚至是上帝，他希望我们骄傲地而不是悲惨地面对苦难，并且清醒地知道如何对待死亡。
```
- visible reaction:
```text
"有人在看着"这个框架把处境从无人在场的绝望感中拉出来——不是自我表演给监控者看的那种屈辱性观看，而是一种被承认、被在乎的存在感。它提前预演了后来"意义疗法"中"负责地存在"的核心结构：人不是为自己活着，而是为某种意义的承担而活着。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 137 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p213@0-p213@198:highlight:137`
- source span: `src:c1:p213@97-p213@131`
- source span excerpt:
```text
同样也是血肉之躯的看守，怎么能够像许多犯人说的那样去对待他的同类呢？
```
- visible reaction:
```text
这个措辞值得注意：它用「同类」而非「人类/非人」来界定看守与囚徒的关系，预先封堵了一种解释（怪物论），把答案指向情境与人格瓦解的机制，而非本质性的邪恶。后文对「心理学角度看怎么会发生」的追问，进一步确认了这里的理论意图。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 138 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p214@0-p218@308:highlight:138`
- source span: `src:c1:p218@0-p218@58`
- source span excerpt:
```text
显然，一个人是集中营司令还是犯人，不能说明任何问题。在任何团体里，都能发现人的仁慈，哪怕这个团体整体上应该受到谴责。
```
- visible reaction:
```text
这个结论是全段的道德锚点。「不能说明任何问题」——角色位置不是道德预测器，它预先封堵了「看守必然邪恶、囚徒必然无辜」的两极叙事，与前文对囚头儿（同样是囚徒）的残酷描述形成直接呼应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 139 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p214@0-p218@308:highlight:139`
- source span: `src:c1:p218@276-p218@308`
- source span excerpt:
```text
他所给我的还有一份人性，跟礼物相伴的是他温暖的话语和仁慈的表情。
```
- visible reaction:
```text
一片面包之所以值得热泪盈眶，不在于热量，而在于它携带了「人性」这个不可量化的东西。这与集中营整体的非人化构成了反向运动——在最彻底的剥夺环境中，一个微小举动反而成为人性的凭证。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0040` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0040` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p218@255-308` 当时我感动得热泪盈眶，不只是因为一块面包，他所给我的还有一份人性，跟礼物相伴的是他温暖的话语和仁慈的表情。
    - target note: 当时我感动得热泪盈眶，不只是因为一块面包，他所给我的还有一份人性，跟礼物相伴的是他温暖的话语和仁慈的表情。
    - source-span relation: `note_contains_candidate`; coverage `0.60`
    - judge/runner reason: The reaction's quoted span covers the note's core content about receiving '一份人性' with warm words and benevolent expression. The reaction's analysis directly engages with this theme—interpreting the bread as a vehicle for '人性' rather than mere sustenance, and connecting it to the broader context of camp dehumanization. This demonstrates genuine focused engagement with the note's important content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0040.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 140 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p219@0-p220@232:highlight:140`
- source span: `src:c1:p220@22-p220@84`
- source span excerpt:
```text
在人性的深处，如果你发现人类在本性上就善恶交织，你还会觉得奇怪吗？所有人的心里都有一道划分善恶的分水岭，它一直延伸到人性深处
```
- visible reaction:
```text
「善恶交织」这个说法不只是描述，它是一个结构性断言：善恶不是对立的两个人群，而是一条存在于每个人内心的分界线。这与前文反复出现的"两类人"说法形成对位——表面上是二分的，实质上每个人都横跨两边。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 141 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p221@0-p225@215:highlight:141`
- source span: `src:c1:p225@0-p225@61`
- source span excerpt:
```text
从心理学的角度讲，得到解放的犯人最初的感觉叫“人格解体”。一切都显得不真实、不可能，像是在梦中一样。我们不能相信这是真的。
```
- visible reaction:
```text
「人格解体」——这是当前单元给出的核心诊断。它不是冷漠，而是一种心理上的不能相信：现实的质感消失了，真实的解放与曾经反复出现的梦境无法区分。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 142 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p221@0-p225@215:highlight:142`
- source span: `src:c1:p221@99-p221@127`
- source span excerpt:
```text
一开始我们几乎不敢认他们，他们这么快就换上了文明的外衣。
```
- visible reaction:
```text
「文明的外衣」这个说法有惊人的速度感——看守在几小时内就完成了从施害者到普通人的切换，而囚徒们却发现自己在自由世界里失去了归属感。这种不对等本身就构成了一种延迟的暴力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 143 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p226@0-p229@209:discern:143`
- source span: `src:c1:p227@156-p227@178`
- source span excerpt:
```text
我从心底呼唤着上帝，他在自由的空间回答了我。
```
- visible reaction:
```text
「自由的空间」这个表述把答案的所在从某个神迹事件转到了空间本身——不是特定的奇迹，而是开放和无阻碍本身即是回应。这与段落开头「身体所受的束缚要少一些」形成呼应：身体的解放先发生，然后精神在自由的空间里找到回应。恢复不是被给予什么，而是阻隔消失了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 144 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p230@0-p231@171:highlight:144`
- source span: `src:c1:p230@118-p230@153`
- source span excerpt:
```text
他们痛苦的经历成了为所欲为的借口，这种情况在小事中就能很清楚地看出来。
```
- visible reaction:
```text
这段话揭示了一个几乎机械性的逻辑：受害本身成了施害的许可证。经历变成了通行证，而非界限。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 145 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p230@0-p231@171:highlight:145`
- source span: `src:c1:p231@140-p231@171`
- source span excerpt:
```text
说这话的人并不坏，在集中营和后来的日子里，他都是我最好的朋友。
```
- visible reaction:
```text
"并不坏"三个字在这里不是宽慰，而是一种道德诊断：施害行为来自迷失而非本质。这为随后的"引导回常识性真理"提供了前提——如果已经坏了，引导就不成立。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 146 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p232@0-p236@159:highlight:146`
- source span: `src:c1:p235@0-p235@85`
- source span excerpt:
```text
我们在说到给予集中营犯人精神力量的时候，曾经讲过应该给他一个未来生活中值得期待的目标。要提醒他，生活在等着他，亲人在等着他回家。但被解放以后呢？一些犯人发现没有人在等他。
```
- visible reaction:
```text
这里构成了一个尖锐的翻转：拯救手段在解放后成为伤害来源——因为那个被植入的期待（有人在等你回家）可能从一开始就是假的。心理支持系统的失效不是技术问题，而是它的前提在归来时塌陷了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 147 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p237@0-p238@61:highlight:147`
- source span: `src:c1:p237@72-p237@109`
- source span excerpt:
```text
当他们觉得集中营的全部经历仅仅是一场噩梦而已时，他们最后的解放也就到来了。
```
- visible reaction:
```text
「最后的解放」被定义为能够把经历当作噩梦来观看的那一刻——即与那段经验拉开心理距离。这与前面讨论的「适应」和「悬置式好奇」构成呼应：生存需要将现实改写为可承受状态，而解放需要将那段改写本身再拉开一层距离，变成可回顾的对象。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 148 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p237@0-p238@61:highlight:148`
- source span: `src:c1:p238@0-p238@61`
- source span excerpt:
```text
对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。
```
- visible reaction:
```text
「除了上帝」这个限定在这里不是普通的宗教表达——它精确地划出了无惧的边界：苦难的尽头不是虚无，而是对某种不可测之物的敬畏保留。这意味着自由的反面不是恐惧，而是冒犯神圣。
```
- Selective Legibility dataset relation:
  - note-case `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0041` / note `huochu_shengming_de_yiyi_private_zh_personal_notes__e0041` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p238@0-61` 对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。
    - target note: 对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0041.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 149 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p239@0-p239@287:highlight:149`
- source span: `src:c1:p239@193-p239@287`
- source span excerpt:
```text
美军指挥官不仅信守了诺言，而且那个党卫军司令实际上被官复原职，负责监督从附近村子里收集衣物并向我们发放，而我们当时仍然穿着从奥斯维辛那些没我们幸运、被送到毒气室杀害的犯人身上扒下来的衣服。
```
- visible reaction:
```text
这句话包含三个层次的叠加讽刺：美军信守诺言（道德信誉的胜利）、司令官复原职（制度性荒谬）、而囚徒仍穿着死者的衣服。这三段式并置揭示了「解放」的有限性——政治层面的解放与心理层面、人际层面的持续压迫共存。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 150 — `weak_callback` — `retrospect`

- reaction_id: `rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1`
- source span: `src:c1:p239@287-p239@287`
- source span excerpt:
```text
犹太犯人将那位司令掩藏在了巴伐利亚的丛林中，然后他们找到美军的指挥官 （他正组织抓捕集中营司令），说他们可以帮他找到司令，但有一些条件：美军指挥官必须保证绝不允许任何人伤害司令。过了一会，美军指挥官答应三个犹太人，抓到党卫军司令后保证不许任何人伤害他。美军指挥官不仅信守了诺言，而且那个党卫军司令实际上被官复原职，负责监督从附近村子里收集衣物并向我们发放，而我们当时仍然穿着从奥斯维辛那些没我们幸运、被送到毒气室杀害的犯人身上扒下来的衣服。
```
- visible reaction:
```text
第一章结尾的道德人类学总结，实际上是对全章叙述的一种元伦理学注脚：善与恶不是阵营的属性，而是每个人内部都在持续进行的内部选择。弗兰克尔没有在这里停步——他紧接着预告第二章将揭示这一发现的哲学后果：正是这种'人可以选择'的洞见，构成了意义治疗法最根本的人类学前提。党卫军司令的善与囚徒的恶之间不存在矛盾，只存在一个共同的结构——每个人都在极端处境中被召唤做出选择，而选择的后果完全由个人承担。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: The reaction claims to be retrospective but has no prior_link populated with specific earlier reaction IDs. While the content about '善恶不是阵营的属性，而是每个人内部都在持续进行的内部选择' clearly echoes earlier reactions (particularly reaction 140's '善恶交织' concept and reaction 138's moral complexity discussion), it references book content ('第一章结尾的道德人类学总结') rather than grounding itself in specific visible reactions from the window. Without actual prior_link citations, the retrospective claim is unsupported — the mechanism cannot verify that this reaction is genuinely anchoring to earlier surfaced material rather than independently re-deriving the same thematic connections.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

## Probe Memory Checkpoints

Memory Quality is scored at probe time. The state below is a structured re-layout of the recorded probe snapshot, not a fresh summary and not the final runtime dump.

### Probe 1 — MQ `3.50` — near 20%

#### Probe Position And Question
- target sentence: `c1-s269`
- boundary kind: `phase transition`
- why this point: Ends the first-stage camp-arrival arc and crosses into the second stage, so the snapshot can be checked after the book has introduced the explicit three-stage prisoner-response structure and completed the first transition.
- focus: `huochu_probe1_prisoner_response_three_stages` / 囚徒精神反应三阶段
- audit question: Does the memory snapshot retain that the author is organizing camp-life psychology through this three-stage structure, even if it does not use the exact same wording?
- structural signals to check:
  - 囚徒精神反应三阶段：收容阶段、适应阶段、释放与解放阶段
  - 第一阶段向第二阶段过渡
  - 恐惧、休克、情感麻木作为集中营心理反应框架

#### Source Orientation
```text
   s267 / p51: 囚徒开始从心理反应的第一阶段进入第二阶段，即一个表现相当冷漠的阶段。
   s268 / p51: 在这期间，他的情感进入一种死亡状态。
>> s269 / p52: 除了以上描述的反应之外，新囚徒还经常遭受痛苦的感情折磨，他还要抑制这些情感。
   s270 / p52: 这种情感首先指他对家乡和家庭的无限思念，有时强烈到足以将其吞噬。
   s271 / p52: 其次指对周围一切丑恶行为的厌恶，甚至仅仅是丑陋的外貌都让他感觉厌恶。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
      "ref_id": "active_attention:psychological-first-stage",
      "item_id": "psychological-first-stage",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "「心理反应的第一阶段」：叙述者明确界定当前状态仍处于第一阶段。这意味着存在后续阶段，且第一阶段的特点（好奇、冷酷幽默、身体适应）与更深的阶段（真正「习惯」之后）之间存在关键分野。这个悬置的「后面阶段」是一个值得追踪的概念。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p46@117-p46@138",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 117
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 138
            }
          },
          "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
          "role": "core definition",
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
      "ref_id": "active_attention:misguided-comfort",
      "item_id": "misguided-comfort",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "误导性安慰的结构：传递安慰的人已经消瘦得认不出来，他自己也不具备可靠的判断力，他的\"漫不经心的幽默\"和\"别害怕\"建立在已被证伪的预期之上。在极端剥夺中，善意与误导可以并存——因为信息来源本身就不可靠。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p48@241-p48@265",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 241
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 265
            }
          },
          "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
          "role": "core observation",
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
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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

#### Active Focus

`active_focus_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
  "recent_reactions": [
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p47@0-p47@276:discern:28",
      "reaction_id": "rx:Full_Content:src:c1:p47@0-p47@276:discern:28",
      "type": "discern",
      "thought": "「免除麻烦」这个说法冷酷到了极点，却因此具有一种奇怪的诚实。它不是在美化毒气室，而是揭示了一种极端处境下的功利逻辑：死亡已经被安排好了，你不需要亲自动手。这个逻辑隐含的前提是——自杀念头确实存在，而且确实需要某种出口，只是这个出口已经被外部力量接管了。它同时暗示：真正让人恐惧的不是死亡本身，而是死亡之前的那个等待——毒气室至少结束这个等待。",
      "emitted_at_source_span_id": "src:c1:p47@0-p47@276",
      "primary_source_ref": {
        "source_span_id": "src:c1:p47@253-p47@276",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 47,
            "char_offset": 253
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 47,
            "char_offset": 276
          }
        },
        "quote": "不要忘了，毒气室至少可以使他们免除自杀的麻烦。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "不要忘了，毒气室至少可以使他们免除自杀的麻烦。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p48@0-p48@323:highlight:29",
      "reaction_id": "rx:Full_Content:src:c1:p48@0-p48@323:highlight:29",
      "type": "highlight",
      "thought": "\"善言具有误导性\"——这个判断本身值得注意。在集中营中，善意与误导并不矛盾。传递安慰的人自己没有可靠的判断依据，他的信息来自已被现实否定的预期。这和前文那些\"我一直确信\"的信念崩解是同一种结构：人在极端环境中失去了辨别真假的能力，连安慰都可能是建立在错误之上的。",
      "emitted_at_source_span_id": "src:c1:p48@0-p48@323",
      "primary_source_ref": {
        "source_span_id": "src:c1:p48@241-p48@322",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 48,
            "char_offset": 241
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 48,
            "char_offset": 322
          }
        },
        "quote": "他关于这个M的判断是错误的，他的善言具有误导性。因为一位约60岁的棚屋街区医生犯人曾告诉过我他是如何祈求M博士放过他将被送进毒气室的儿子，可M博士却冷冷地拒绝了。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "他关于这个M的判断是错误的，他的善言具有误导性。因为一位约60岁的棚屋街区医生犯人曾告诉过我他是如何祈求M博士放过他将被送进毒气室的儿子，可M博士却冷冷地拒绝了。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    }
  ]
}
```

#### Concept Digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:concept-communication-impossibility-paradox",
    "concept_key": "concept-communication-impossibility-paradox",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p10@199-p10@265",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 199
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 265
          }
        },
        "quote": "对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-depersonalization-through-stripping",
    "concept_key": "concept-depersonalization-through-stripping",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p39@52-p39@69",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 39,
            "char_offset": 52
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 39,
            "char_offset": 69
          }
        },
        "quote": "现在，眼镜和皮带就是我的全部财产。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "现在，眼镜和皮带就是我的全部财产。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-emotional-death-in-survival",
    "concept_key": "concept-emotional-death-in-survival",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p51@208-p51@260",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 51,
            "char_offset": 208
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 51,
            "char_offset": 260
          }
        },
        "quote": "囚徒开始从心理反应的第一阶段进入第二阶段，即一个表现相当冷漠的阶段。在这期间，他的情感进入一种死亡状态。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "囚徒开始从心理反应的第一阶段进入第二阶段，即一个表现相当冷漠的阶段。在这期间，他的情感进入一种死亡状态。"
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

#### Thread Digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:thread-threefold-struggle",
    "thread_key": "thread-threefold-struggle",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p5@63-p5@88",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 88
          }
        },
        "quote": "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
        "role": "frame",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p6@0-p6@207",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 207
          }
        },
        "quote": "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。",
        "role": "structural extension",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "missing_quote"
        }
      }
    ],
    "sample_quotes": [
      "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
      "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-courage-irrecoverability",
    "thread_key": "thread-courage-irrecoverability",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p14@138-p14@155",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 138
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 155
          }
        },
        "quote": "勇气一旦失去，几乎就不可能再挽回。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "勇气一旦失去，几乎就不可能再挽回。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-friend-P",
    "thread_key": "thread-friend-P",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p25@22-p25@52",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 25,
            "char_offset": 22
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 25,
            "char_offset": 52
          }
        },
        "quote": "我向待在那里时间较长的囚徒询问我的同事和朋友P被送到哪里了。",
        "role": "thread anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我向待在那里时间较长的囚徒询问我的同事和朋友P被送到哪里了。"
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

#### Reflective Digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### SourceRef Digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@126-p4@174",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 126
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 174
      }
    },
    "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
    "role": "core thesis",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@146-p18@178",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 146
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 178
      }
    },
    "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
    "role": "core mechanism",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@18-p23@59",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 59
      }
    },
    "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p42@43-p42@68",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 43
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 68
      }
    },
    "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p46@117-p46@138",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 117
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 138
      }
    },
    "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p48@241-p48@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 241
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 265
      }
    },
    "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
    "role": "core observation",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@199-p10@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 199
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 265
      }
    },
    "quote": "对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p39@52-p39@69",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 39,
        "char_offset": 52
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 39,
        "char_offset": 69
      }
    },
    "quote": "现在，眼镜和皮带就是我的全部财产。",
    "role": "core_definition",
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
- judge-provided overall: `4`
- final overall MQ: `3.5`
- judge reason: The snapshot retains the three-stage concept in fragments through 'psychological-first-stage' (引用'仍处于心理反应的第一阶段') and 'concept-emotional-death-in-survival' (引用'从心理反应的第一阶段进入第二阶段'), but the explicit three-stage framework names—收容阶段、适应阶段、释放与解放阶段—are absent as an organizing structure. The second-stage entry (冷漠/情感死亡状态) is retained, but the third-stage label (释放与解放阶段) is missing. The snapshot captures the arc from terror→curiosity/humor→emotional numbness well, and accurately preserves key items like the selection mechanism, the ordinary-prisoners thesis, and specific quotations. However, the source's explicit framework statement is not surfaced as a structural digest item, which reduces salience and organization scores for a probe specifically checking this signal.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[0]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.

### Probe 2 — MQ `4.25` — near 40%

#### Probe Position And Question
- target sentence: `c1-s528`
- boundary kind: `inner-life episode closure`
- why this point: Closes the wife/nature/beauty inner-life sequence before the text turns again, so it can test whether the reader retains spiritual survival rather than only external camp events.
- structural signals to check:
  - 爱与妻子的形象作为精神生存资源
  - 自然与美感在极端处境中的支撑作用
  - 从外部苦难转向内在自由的主线

#### Source Orientation
```text
   s526 / p107: 在从奥斯维辛集中营到巴伐利亚集中营的路上，如果有人看见我们透过囚车铁窗远眺扎耳茨伯格山脉的山峰在落日中闪闪发光时的一张张面孔，他们决不会相信这是放弃了生活的希望和自由的人的面孔，尽管这也可能是由于我们渴望借由许久没见的大自然的美而转移目前的痛苦。
   s527 / p108: 在集中营中，一个人也能转移旁边干活者的注意力，使其注意力被引向落日照耀的巴伐利亚森林 （其情景就像丢勒的一幅著名水彩画）。
>> s528 / p108: 在这片树林中，我们已经建好一个巨大的、秘密的兵工厂。
   s529 / p108: 一天晚上，我们端着汤碗，精疲力竭地躺在棚屋的地板上休息，一名狱友冲进来让我们跑到集合地看日落。
   s530 / p108: 站在外面，我们欣赏着晚霞，看着不断变换形状和色彩的云朵笼罩着整个天空，云彩一会儿铁红色，一会儿艳红色，与我们荒凉的棚屋形成鲜明对比，泥潭也映照出灿烂的天空。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
      "ref_id": "active_attention:psychological-first-stage",
      "item_id": "psychological-first-stage",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "「心理反应的第一阶段」：叙述者明确界定当前状态仍处于第一阶段。这意味着存在后续阶段，且第一阶段的特点（好奇、冷酷幽默、身体适应）与更深的阶段（真正「习惯」之后）之间存在关键分野。这个悬置的「后面阶段」是一个值得追踪的概念。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p46@117-p46@138",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 117
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 138
            }
          },
          "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
          "role": "core definition",
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
      "ref_id": "active_attention:misguided-comfort",
      "item_id": "misguided-comfort",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "误导性安慰的结构：传递安慰的人已经消瘦得认不出来，他自己也不具备可靠的判断力，他的\"漫不经心的幽默\"和\"别害怕\"建立在已被证伪的预期之上。在极端剥夺中，善意与误导可以并存——因为信息来源本身就不可靠。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p48@241-p48@265",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 241
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 265
            }
          },
          "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
          "role": "core observation",
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
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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

#### Active Focus

`active_focus_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
  "recent_reactions": [
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p95@0-p99@176:highlight:61",
      "reaction_id": "rx:Full_Content:src:c1:p95@0-p99@176:highlight:61",
      "type": "highlight",
      "thought": "\"不论真实与否\"这几个字至关重要——它坦承了这种明亮的理想化性质，却也正因为坦承而更具力量。不是因为她真的比太阳亮，所以值得坚守；而是无论真假，这种确信本身就是集中营中最后的自由领地。",
      "emitted_at_source_span_id": "src:c1:p95@0-p99@176",
      "primary_source_ref": {
        "source_span_id": "src:c1:p99@148-p99@176",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 99,
            "char_offset": 148
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 99,
            "char_offset": 176
          }
        },
        "quote": "不论真实与否，我都坚信她的外貌比冉冉升起的太阳还要明亮。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "不论真实与否，我都坚信她的外貌比冉冉升起的太阳还要明亮。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p100@0-p104@134:discern:62",
      "reaction_id": "rx:Full_Content:src:c1:p100@0-p104@134:discern:62",
      "type": "discern",
      "thought": "这里有一个隐含的深刻区分：爱一个人≠爱她的肉体。在极端环境中，「不知妻子是否还活着」这个念头非但没有摧毁他的爱，反而促成了对爱的更本质理解——所爱之人的在场与否、存亡与否，都不是爱的边界；真正重要的是爱以何种方式终止。这意味着爱是一种独立于被爱对象的价值。",
      "emitted_at_source_span_id": "src:c1:p100@0-p104@134",
      "primary_source_ref": {
        "source_span_id": "src:c1:p104@71-p104@134",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 104,
            "char_offset": 71
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 104,
            "char_offset": 134
          }
        },
        "quote": "爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "爱一个人可以远远超过爱她的肉体本身。爱在精神和内心方面具有深刻的含义，无论伴侣是否在场，是否健在，爱以什么方式终止是很重要的。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    }
  ]
}
```

#### Concept Digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:concept-collective-emotional-economy",
    "concept_key": "concept-collective-emotional-economy",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p91@123-p91@156",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 91,
            "char_offset": 123
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 91,
            "char_offset": 156
          }
        },
        "quote": "一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-communication-impossibility-paradox",
    "concept_key": "concept-communication-impossibility-paradox",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p10@199-p10@265",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 199
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 265
          }
        },
        "quote": "对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-corpse-looting-normalization",
    "concept_key": "concept-corpse-looting-normalization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p56@134-p56@151",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 56,
            "char_offset": 134
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 56,
            "char_offset": 151
          }
        },
        "quote": "连只拿到细绳的人都会因此沾沾自喜。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "连只拿到细绳的人都会因此沾沾自喜。"
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

#### Thread Digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:thread-threefold-struggle",
    "thread_key": "thread-threefold-struggle",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p5@63-p5@88",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 88
          }
        },
        "quote": "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
        "role": "frame",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p6@0-p6@207",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 207
          }
        },
        "quote": "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。",
        "role": "structural extension",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "missing_quote"
        }
      }
    ],
    "sample_quotes": [
      "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
      "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-courage-irrecoverability",
    "thread_key": "thread-courage-irrecoverability",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p14@138-p14@155",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 138
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 155
          }
        },
        "quote": "勇气一旦失去，几乎就不可能再挽回。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "勇气一旦失去，几乎就不可能再挽回。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-friend-P",
    "thread_key": "thread-friend-P",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p25@22-p25@52",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 25,
            "char_offset": 22
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 25,
            "char_offset": 52
          }
        },
        "quote": "我向待在那里时间较长的囚徒询问我的同事和朋友P被送到哪里了。",
        "role": "thread anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我向待在那里时间较长的囚徒询问我的同事和朋友P被送到哪里了。"
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

#### Reflective Digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### SourceRef Digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@126-p4@174",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 126
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 174
      }
    },
    "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
    "role": "core thesis",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@146-p18@178",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 146
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 178
      }
    },
    "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
    "role": "core mechanism",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@18-p23@59",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 59
      }
    },
    "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p42@43-p42@68",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 43
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 68
      }
    },
    "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p46@117-p46@138",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 117
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 138
      }
    },
    "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p48@241-p48@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 241
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 265
      }
    },
    "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
    "role": "core observation",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p55@0-p55@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 53
      }
    },
    "quote": "进入心理反应的第二阶段，这个囚徒的眼睛将不再躲避这一切。由于情感已经麻木，他看到什么都只会呆呆地站着不动。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p61@0-p61@87",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 87
      }
    },
    "quote": "冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。",
    "role": "core definition",
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
- fidelity: `5`
- judge-provided overall: `4`
- final overall MQ: `4.25`
- judge reason: The snapshot retains the central love/wife spiritual resource clearly via three key reactions: the '不论真实与否' anchor quote about wife's brightness, the discern on love transcending physical presence, and the bird-as-witness moment at the very end. The '爱是人类终身追求的最高目标' formulation is present in active attention. The broad mainline from external camp suffering toward inner freedom is present (psychological stages, selection, beatings, hunger, then love revelation). However, the natural-beauty closing scene—specifically the sunset with changing colors over Bavarian forest, the mud reflecting the sky, and the remark '世界多美呀'—is absent from the digest. This is a significant omission because it is the precise structural moment this probe is designed to test: beauty in extremity as spiritual survival. The wife sequence trails off in the reactions but the complementary natural-aesthetic sequence is missing entirely from the snapshot, meaning the '从外部苦难转向内在自由' mainline is only partially completed at this boundary.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[1]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.

### Probe 3 — MQ `3.25` — near 60%

#### Probe Position And Question
- target sentence: `c1-s794`
- boundary kind: `moral-decision episode closure`
- why this point: Closes the decision-not-to-escape episode, giving a clean semantic checkpoint for active choice, responsibility, and care under captivity.
- structural signals to check:
  - 被囚禁处境中的主动选择
  - 照顾病友与责任感
  - 命运、选择和平静之间的关系

#### Source Orientation
```text
   s792 / p149: 随着战线的日益推近，我曾有机会逃脱。
   s793 / p149: 我的一个同事在执行医疗任务的时候曾经到过狱外，他想带我一起跑出去。
>> s794 / p149: 他借口一个病人的病情复杂，需要专家会诊，把我带了出去。
   s795 / p149: 到了外面，一个外国抵抗组织的成员要给我们制服和证件。
   s796 / p149: 在最后关头，出了点技术上的问题，我们不得不再回到集中营。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
      "ref_id": "active_attention:psychological-first-stage",
      "item_id": "psychological-first-stage",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "「心理反应的第一阶段」：叙述者明确界定当前状态仍处于第一阶段。这意味着存在后续阶段，且第一阶段的特点（好奇、冷酷幽默、身体适应）与更深的阶段（真正「习惯」之后）之间存在关键分野。这个悬置的「后面阶段」是一个值得追踪的概念。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p46@117-p46@138",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 117
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 138
            }
          },
          "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
          "role": "core definition",
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
      "ref_id": "active_attention:misguided-comfort",
      "item_id": "misguided-comfort",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "误导性安慰的结构：传递安慰的人已经消瘦得认不出来，他自己也不具备可靠的判断力，他的\"漫不经心的幽默\"和\"别害怕\"建立在已被证伪的预期之上。在极端剥夺中，善意与误导可以并存——因为信息来源本身就不可靠。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p48@241-p48@265",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 241
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 265
            }
          },
          "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
          "role": "core observation",
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
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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

#### Active Focus

`active_focus_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
  "recent_reactions": [
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p150@0-p150@280:discern:93",
      "reaction_id": "rx:Full_Content:src:c1:p150@0-p150@280:discern:93",
      "type": "discern",
      "thought": "三个宾语并列：「背包」「牙刷」「女尸」。没有过渡、没有停顿、没有情绪词。搜刮生存物资与发现死亡并列，这意味着在集中营里，发现尸体已经内化为日常搜索行为的一部分，而非需要单独标记的事件。这种平静本身就是一种精神状态的体现——不是麻木，而是已经将「身边有尸体」整合进了正常活动的框架。",
      "emitted_at_source_span_id": "src:c1:p150@0-p150@280",
      "primary_source_ref": {
        "source_span_id": "src:c1:p150@255-p150@280",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 150,
            "char_offset": 255
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 150,
            "char_offset": 280
          }
        },
        "quote": "我进去找到了一个背包和一把牙刷，还发现了一具女尸。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "我进去找到了一个背包和一把牙刷，还发现了一具女尸。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p151@0-p151@366:highlight:94",
      "reaction_id": "rx:Full_Content:src:c1:p151@0-p151@366:highlight:94",
      "type": "highlight",
      "thought": "「自己拿一次主意」——这个表述直接呼应了前文关于犯人「逃避责任」「不敢采取主动行为」的描述。叙说者打破了这个模式，而他打破它的方式是：拒绝行动。这里存在一个悖论结构——在集中营语境下，最大胆的决定往往恰恰是「不做某事」，而非「做某事」。",
      "emitted_at_source_span_id": "src:c1:p151@0-p151@366",
      "primary_source_ref": {
        "source_span_id": "src:c1:p151@242-p151@294",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 151,
            "char_offset": 242
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 151,
            "char_offset": 294
          }
        },
        "quote": "突然，我决定自己拿一次主意。我跑出去告诉那个朋友我不跟他跑了。一说出这句话，那种不安的感觉就顿时消失了。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "突然，我决定自己拿一次主意。我跑出去告诉那个朋友我不跟他跑了。一说出这句话，那种不安的感觉就顿时消失了。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    }
  ]
}
```

#### Concept Digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:concept-art-as-forgetfulness",
    "concept_key": "concept-art-as-forgetfulness",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p110@192-p110@217",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 192
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 217
          }
        },
        "quote": "所有这一切都是为了帮助我们忘却，当然这也的确管用。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "所有这一切都是为了帮助我们忘却，当然这也的确管用。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-art-ghostly-contrast",
    "concept_key": "concept-art-ghostly-contrast",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@28-p113@73",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 28
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 73
          }
        },
        "quote": "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-collective-emotional-economy",
    "concept_key": "concept-collective-emotional-economy",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p91@123-p91@156",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 91,
            "char_offset": 123
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 91,
            "char_offset": 156
          }
        },
        "quote": "一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。"
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

#### Thread Digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:thread-threefold-struggle",
    "thread_key": "thread-threefold-struggle",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p5@63-p5@88",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 88
          }
        },
        "quote": "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
        "role": "frame",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p6@0-p6@207",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 207
          }
        },
        "quote": "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。",
        "role": "structural extension",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "missing_quote"
        }
      }
    ],
    "sample_quotes": [
      "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
      "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-art-memory-versus-forgetfulness",
    "thread_key": "thread-art-memory-versus-forgetfulness",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@213-p113@247",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 213
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 247
          }
        },
        "quote": "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。",
        "role": "thread anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-courage-irrecoverability",
    "thread_key": "thread-courage-irrecoverability",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p14@138-p14@155",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 138
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 155
          }
        },
        "quote": "勇气一旦失去，几乎就不可能再挽回。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "勇气一旦失去，几乎就不可能再挽回。"
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

#### Reflective Digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### SourceRef Digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@126-p4@174",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 126
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 174
      }
    },
    "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
    "role": "core thesis",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@146-p18@178",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 146
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 178
      }
    },
    "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
    "role": "core mechanism",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@18-p23@59",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 59
      }
    },
    "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p42@43-p42@68",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 43
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 68
      }
    },
    "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p46@117-p46@138",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 117
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 138
      }
    },
    "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p48@241-p48@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 241
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 265
      }
    },
    "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
    "role": "core observation",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p55@0-p55@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 53
      }
    },
    "quote": "进入心理反应的第二阶段，这个囚徒的眼睛将不再躲避这一切。由于情感已经麻木，他看到什么都只会呆呆地站着不动。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p61@0-p61@87",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 87
      }
    },
    "quote": "冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。",
    "role": "core definition",
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
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.25`
- judge reason: The snapshot retains concrete material from the escape-refusal episode (the friend's offer, Frankl's momentary hesitation before the dying comrade, his whispered message to Otto about his wife, and the key line '一说出这句话，那种不安的感觉就顿时消失了'), and it correctly anchors the three-stage psychological framework from earlier. However, the structural signal of '被囚禁处境中的主动选择' is treated as a surface plot event rather than as the paradigmatic moral reversal it represents — the snapshot does not capture that Frankl's most 'active' choice under captivity was precisely the choice NOT to act. The second signal '照顾病友与责任感' appears only as context for why he hesitated, not as a thematic anchor. The third signal '命运、选择和平静之间的关系' is present in the recent_reactions (the '前所未有的平静' reaction and its contrast with the 82 prisoners who wrongly chose to volunteer), but the digest and hot_items do not foreground this philosophical thread. The philosophical climax — that choosing responsibility to a dying comrade produced inner peace regardless of outcome — is insufficiently elevated in the snapshot's organization despite being the most salient feature at this boundary.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[2]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.

### Probe 4 — MQ `3.75` — near 80%

#### Probe Position And Question
- target sentence: `c1-s1083`
- boundary kind: `argument turn`
- why this point: Captures the argument that loss of future orientation weakens the body, just before the text deepens the life-purpose frame.
- structural signals to check:
  - 未来感、希望和生命力的关系
  - 精神状态影响身体抵抗力
  - 尼采命题和意义治疗主线的准备

#### Source Orientation
```text
   s1081 / p192: 他对未来的希望和活下去的意志都没有了，身体也就成为疾病的牺牲品——虽然他梦里声音所说的最终都应验了。
   s1082 / p193: 对这个病例的观察与从中得出的结论，跟我们集中营主任医生所注意到的情况是一致的。
>> s1083 / p193: 集中营在1944年圣诞节至1945年圣诞间的死亡率是最高的。
   s1084 / p193: 他认为，原因不在于劳动强度增大，也不在于食物短缺或气候寒冷，甚至不是因为出现了新的流行病，而是由于多数犯人都天真地以为能在圣诞节前回家，而随着时间的推移，这种可能性越来越小，犯人失去了勇气，变得沮丧起来。
   s1085 / p193: 这严重减弱了他们身体的抵抗力，导致许多人死亡。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
      "ref_id": "active_attention:psychological-first-stage",
      "item_id": "psychological-first-stage",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "「心理反应的第一阶段」：叙述者明确界定当前状态仍处于第一阶段。这意味着存在后续阶段，且第一阶段的特点（好奇、冷酷幽默、身体适应）与更深的阶段（真正「习惯」之后）之间存在关键分野。这个悬置的「后面阶段」是一个值得追踪的概念。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p46@117-p46@138",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 117
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 138
            }
          },
          "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
          "role": "core definition",
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
      "ref_id": "active_attention:misguided-comfort",
      "item_id": "misguided-comfort",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "误导性安慰的结构：传递安慰的人已经消瘦得认不出来，他自己也不具备可靠的判断力，他的\"漫不经心的幽默\"和\"别害怕\"建立在已被证伪的预期之上。在极端剥夺中，善意与误导可以并存——因为信息来源本身就不可靠。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p48@241-p48@265",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 241
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 265
            }
          },
          "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
          "role": "core observation",
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
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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

#### Active Focus

`active_focus_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
  "recent_reactions": [
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p192@0-p192@160:retrospect:120",
      "reaction_id": "rx:Full_Content:src:c1:p192@0-p192@160:retrospect:120",
      "type": "retrospect",
      "thought": "这句话是全段最锋利的反讽。声音是对的——战争在某一天结束了；但F没能活到那一天。预言在事实层面成立，在F的生命时间线上彻底失效。这比「预言错了」更残忍，因为它证明F的死亡不是来自预言的欺骗，而是来自时间的不等人。",
      "emitted_at_source_span_id": "src:c1:p192@0-p192@160",
      "primary_source_ref": {
        "source_span_id": "src:c1:p192@143-p192@160",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 192,
            "char_offset": 143
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 192,
            "char_offset": 160
          }
        },
        "quote": "虽然他梦里声音所说的最终都应验了。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "虽然他梦里声音所说的最终都应验了。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p193@0-p197@106:discern:121",
      "reaction_id": "rx:Full_Content:src:c1:p193@0-p197@106:discern:121",
      "type": "discern",
      "thought": "这句话翻转了主客体关系。通常人问「我活着有什么意义」时，是把生活当作一个有待回应自己的客体。但这里的逻辑是反过来的：生活是主体，它在向你提问，你要回答的不是「我想从生活得到什么」，而是「生活要我做什么」。这个翻转意味着意义的发现不是内省的，而是行动性的。",
      "emitted_at_source_span_id": "src:c1:p193@0-p197@106",
      "primary_source_ref": {
        "source_span_id": "src:c1:p195@45-p195@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 45
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 75
          }
        },
        "quote": "我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "我们期望生活给予什么并不重要，重要的是生活对我们有什么期望。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    }
  ]
}
```

#### Concept Digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:concept-art-as-forgetfulness",
    "concept_key": "concept-art-as-forgetfulness",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p110@192-p110@217",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 192
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 217
          }
        },
        "quote": "所有这一切都是为了帮助我们忘却，当然这也的确管用。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "所有这一切都是为了帮助我们忘却，当然这也的确管用。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-art-ghostly-contrast",
    "concept_key": "concept-art-ghostly-contrast",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@28-p113@73",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 28
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 73
          }
        },
        "quote": "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-collapse-inversion",
    "concept_key": "concept-collapse-inversion",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p185@0-p185@47",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 185,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 185,
            "char_offset": 47
          }
        },
        "quote": "对自己的未来丧失信心的犯人，注定要走向毁灭。由于他对未来失去了信念，他也就丧失了对精神的把握。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "对自己的未来丧失信心的犯人，注定要走向毁灭。由于他对未来失去了信念，他也就丧失了对精神的把握。"
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

#### Thread Digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:thread-threefold-struggle",
    "thread_key": "thread-threefold-struggle",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p5@63-p5@88",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 88
          }
        },
        "quote": "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
        "role": "frame",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p6@0-p6@207",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 207
          }
        },
        "quote": "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。",
        "role": "structural extension",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "missing_quote"
        }
      }
    ],
    "sample_quotes": [
      "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
      "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-art-memory-versus-forgetfulness",
    "thread_key": "thread-art-memory-versus-forgetfulness",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@213-p113@247",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 213
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 247
          }
        },
        "quote": "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。",
        "role": "thread anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-courage-irrecoverability",
    "thread_key": "thread-courage-irrecoverability",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p14@138-p14@155",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 138
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 155
          }
        },
        "quote": "勇气一旦失去，几乎就不可能再挽回。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "勇气一旦失去，几乎就不可能再挽回。"
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

#### Reflective Digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### SourceRef Digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@126-p4@174",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 126
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 174
      }
    },
    "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
    "role": "core thesis",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@146-p18@178",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 146
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 178
      }
    },
    "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
    "role": "core mechanism",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@18-p23@59",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 59
      }
    },
    "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p42@43-p42@68",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 43
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 68
      }
    },
    "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p46@117-p46@138",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 117
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 138
      }
    },
    "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p48@241-p48@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 241
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 265
      }
    },
    "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
    "role": "core observation",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p55@0-p55@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 53
      }
    },
    "quote": "进入心理反应的第二阶段，这个囚徒的眼睛将不再躲避这一切。由于情感已经麻木，他看到什么都只会呆呆地站着不动。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p61@0-p61@87",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 87
      }
    },
    "quote": "冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。",
    "role": "core definition",
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
- judge reason: The snapshot clearly retains the three probe structural signals. (1) 未来感/希望与生命力的关系: the F case (concept-collapse-inversion) shows hope's departure caused physical death—'身体也就成为疾病的牺牲品'—and the director's observation that Christmas-expectation deaths were due to abandoned hope weakening immunity. (2) 精神状态影响身体抵抗力: captured via the F case, the Nietzsche quote '知道为什么而活的人便能生存' framed as a psychotherapist motto, and the Spinoza reference on turning suffering into object of study. (3) 尼采命题的准备: the Nietzsche quote surfaces explicitly near the probe point. However, organization is modest—the active_attention_digest is heavily front-loaded with s1–s55 entries (focus-ordinary-prisoners, adaptation-to-terror, selection-mechanism, etc.) while the late-text meaning is represented only by the three concept-digest items and recent_reactions, leaving the life-purpose frame somewhat undersystematized compared to the early material. The fidelity is high: no distorted paraphrasing, all sampled quotes resolve to exact matches, and the F case captures the source's exact ironies (the voice was right in fact, wrong for F's timeline).

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[3]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.

### Probe 5 — MQ `3.75` — window end

#### Probe Position And Question
- target sentence: `c1-s1292`
- boundary kind: `main-text ending`
- why this point: Ends the meaningful main-text window before citation-only tail material, so the final snapshot reflects the whole selected chapter rather than footnote residue.
- structural signals to check:
  - 释放与解放阶段
  - 人格恢复、苦涩和幻灭
  - 最终自由与不再畏惧的结尾框架

#### Source Orientation
```text
   s1290 / p230: 他们痛苦的经历成了为所欲为的借口，这种情况在小事中就能很清楚地看出来。
   s1291 / p230: 有一回，我跟一个朋友穿过农田正朝集中营方向走，突然到了一块长着绿油油庄稼的田地。
>> s1292 / p230: 我本能地想绕道走，但他拽着我的胳膊，径直从地里穿了过去。
   s1293 / p230: 我嘀咕了几句，大概是说不该践踏青苗。
   s1294 / p230: 他生气了，恼怒地瞪了我一眼，吼道：“你甭说啦！
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
      "ref_id": "active_attention:psychological-first-stage",
      "item_id": "psychological-first-stage",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "「心理反应的第一阶段」：叙述者明确界定当前状态仍处于第一阶段。这意味着存在后续阶段，且第一阶段的特点（好奇、冷酷幽默、身体适应）与更深的阶段（真正「习惯」之后）之间存在关键分野。这个悬置的「后面阶段」是一个值得追踪的概念。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p46@117-p46@138",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 117
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 46,
              "char_offset": 138
            }
          },
          "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
          "role": "core definition",
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
      "ref_id": "active_attention:misguided-comfort",
      "item_id": "misguided-comfort",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "误导性安慰的结构：传递安慰的人已经消瘦得认不出来，他自己也不具备可靠的判断力，他的\"漫不经心的幽默\"和\"别害怕\"建立在已被证伪的预期之上。在极端剥夺中，善意与误导可以并存——因为信息来源本身就不可靠。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p48@241-p48@265",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 241
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 48,
              "char_offset": 265
            }
          },
          "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
          "role": "core observation",
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
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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

#### Active Focus

`active_focus_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:focus-ordinary-prisoners",
      "item_id": "focus-ordinary-prisoners",
      "attention_tags": [
        "focus"
      ],
      "statement": "书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@126-p4@174",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 126
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 174
            }
          },
          "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
          "role": "core thesis",
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
      "ref_id": "active_attention:adaptation-to-terror",
      "item_id": "adaptation-to-terror",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "\"适应\"与\"习以为常\"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p18@146-p18@178",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 146
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 18,
              "char_offset": 178
            }
          },
          "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
          "role": "core mechanism",
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
      "ref_id": "active_attention:selection-mechanism",
      "item_id": "selection-mechanism",
      "attention_tags": [
        "focus",
        "mechanism"
      ],
      "statement": "「筛选」机制：党卫军军官通过一个简单的手势（左=老弱病残→毒气室，右=劳动力→劳役）在一分钟内做出生死判决。叙述者因背包略微左倾、用力挺直身体、军官犹豫后转向其双肩而幸存在右侧。这一过程后来「反复出现」。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@18-p23@59",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 18
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 59
            }
          },
          "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
          "role": "core definition",
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
      "ref_id": "active_attention:psychological-adaptations-under-extremity",
      "item_id": "psychological-adaptations-under-extremity",
      "attention_tags": [
        "focus",
        "psychological-mechanism"
      ],
      "statement": "极端剥夺后的两种心理适应态：①冷酷的幽默感（反身性自嘲，最低限度的庆幸）——「幽默」是被接管而非主动选择；②悬置式好奇（把自己当作陌生事件打量，不问「我害怕」而问「我会怎样」）。两者都是将极度恐惧改写为可承受状态的心理策略的具体显现。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p42@43-p42@68",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 43
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 42,
              "char_offset": 68
            }
          },
          "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
          "role": "support",
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
  "recent_reactions": [
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p232@0-p236@159:highlight:146",
      "reaction_id": "rx:Full_Content:src:c1:p232@0-p236@159:highlight:146",
      "type": "highlight",
      "thought": "这里构成了一个尖锐的翻转：拯救手段在解放后成为伤害来源——因为那个被植入的期待（有人在等你回家）可能从一开始就是假的。心理支持系统的失效不是技术问题，而是它的前提在归来时塌陷了。",
      "emitted_at_source_span_id": "src:c1:p232@0-p236@159",
      "primary_source_ref": {
        "source_span_id": "src:c1:p235@0-p235@85",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 235,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 235,
            "char_offset": 85
          }
        },
        "quote": "我们在说到给予集中营犯人精神力量的时候，曾经讲过应该给他一个未来生活中值得期待的目标。要提醒他，生活在等着他，亲人在等着他回家。但被解放以后呢？一些犯人发现没有人在等他。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "我们在说到给予集中营犯人精神力量的时候，曾经讲过应该给他一个未来生活中值得期待的目标。要提醒他，生活在等着他，亲人在等着他回家。但被解放以后呢？一些犯人发现没有人在等他。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p237@0-p238@61:highlight:147",
      "reaction_id": "rx:Full_Content:src:c1:p237@0-p238@61:highlight:147",
      "type": "highlight",
      "thought": "「最后的解放」被定义为能够把经历当作噩梦来观看的那一刻——即与那段经验拉开心理距离。这与前面讨论的「适应」和「悬置式好奇」构成呼应：生存需要将现实改写为可承受状态，而解放需要将那段改写本身再拉开一层距离，变成可回顾的对象。",
      "emitted_at_source_span_id": "src:c1:p237@0-p238@61",
      "primary_source_ref": {
        "source_span_id": "src:c1:p237@72-p237@109",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 237,
            "char_offset": 72
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 237,
            "char_offset": 109
          }
        },
        "quote": "当他们觉得集中营的全部经历仅仅是一场噩梦而已时，他们最后的解放也就到来了。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "当他们觉得集中营的全部经历仅仅是一场噩梦而已时，他们最后的解放也就到来了。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    }
  ]
}
```

#### Concept Digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:concept-action-speaks-louder-than-words-in-emptiness",
    "concept_key": "concept-action-speaks-louder-than-words-in-emptiness",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p203@39-p203@99",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 203,
            "char_offset": 39
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 203,
            "char_offset": 99
          }
        },
        "quote": "拒绝跟监狱当局同流合污的号长以其正直和勇敢拥有成千上百次机会对所辖犯人施加道德影响。行为的直接影响总是比言辞更有说服力。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "拒绝跟监狱当局同流合污的号长以其正直和勇敢拥有成千上百次机会对所辖犯人施加道德影响。行为的直接影响总是比言辞更有说服力。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-art-as-forgetfulness",
    "concept_key": "concept-art-as-forgetfulness",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p110@192-p110@217",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 192
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 110,
            "char_offset": 217
          }
        },
        "quote": "所有这一切都是为了帮助我们忘却，当然这也的确管用。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "所有这一切都是为了帮助我们忘却，当然这也的确管用。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:concept-art-ghostly-contrast",
    "concept_key": "concept-art-ghostly-contrast",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@28-p113@73",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 28
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 73
          }
        },
        "quote": "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。",
        "role": "core definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。"
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

#### Thread Digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:thread-threefold-struggle",
    "thread_key": "thread-threefold-struggle",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p5@63-p5@88",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 5,
            "char_offset": 88
          }
        },
        "quote": "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
        "role": "frame",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p6@0-p6@207",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 207
          }
        },
        "quote": "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。",
        "role": "structural extension",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "missing_quote"
        }
      }
    ],
    "sample_quotes": [
      "这是一场为了每天的面包、为了生活、为了朋友的斗争。",
      "首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-art-memory-versus-forgetfulness",
    "thread_key": "thread-art-memory-versus-forgetfulness",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p113@213-p113@247",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 213
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 113,
            "char_offset": 247
          }
        },
        "quote": "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。",
        "role": "thread anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:thread-courage-irrecoverability",
    "thread_key": "thread-courage-irrecoverability",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p14@138-p14@155",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 138
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 14,
            "char_offset": 155
          }
        },
        "quote": "勇气一旦失去，几乎就不可能再挽回。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "勇气一旦失去，几乎就不可能再挽回。"
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

#### Reflective Digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### SourceRef Digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@126-p4@174",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 126
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 174
      }
    },
    "quote": "本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。",
    "role": "core thesis",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p18@146-p18@178",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 146
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 18,
        "char_offset": 178
      }
    },
    "quote": "从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。",
    "role": "core mechanism",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@18-p23@59",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 59
      }
    },
    "quote": "分到右边的是干活的人，分到左边的是老弱病残、不能干活的人，这些人要被送到特殊营地。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p42@43-p42@68",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 43
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 42,
        "char_offset": 68
      }
    },
    "quote": "在登山遇险的关键时刻，人们只会有一种感觉，即好奇。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p46@117-p46@138",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 117
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 46,
        "char_offset": 138
      }
    },
    "quote": "到目前为止，我们仍处于心理反应的第一阶段。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p48@241-p48@265",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 241
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 48,
        "char_offset": 265
      }
    },
    "quote": "他关于这个M的判断是错误的，他的善言具有误导性。",
    "role": "core observation",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p55@0-p55@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 55,
        "char_offset": 53
      }
    },
    "quote": "进入心理反应的第二阶段，这个囚徒的眼睛将不再躲避这一切。由于情感已经麻木，他看到什么都只会呆呆地站着不动。",
    "role": "core definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p61@0-p61@87",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 61,
        "char_offset": 87
      }
    },
    "quote": "冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。",
    "role": "core definition",
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
- judge reason: The snapshot retains solid material on the main psychological themes: ordinary prisoners vs. Kapos/famous figures, the selection mechanism (left/right SS gesture), adaptation as strategic psychological rewiring, cold humor and suspended curiosity as coping strategies, and the three-stage psychological framework (with first and second stages well-defined). Three recent reactions near the segment end correctly capture the disillusionment paradox ('no one waiting at home'), the 'final liberation' as nightmare-distancing, and 'besides God, fearing nothing.' However, the three structural signals that define this probe point are incompletely organized: the '释放与解放阶段' (Third Phase) lacks systematic treatment beyond individual reactions; '人格恢复、苦涩和幻灭' (personality recovery, bitterness, disillusionment) is present only in fragmented reactions rather than as a named analytic category; and '最终自由与不再畏惧' (final freedom/fearlessness) survives only in the final sentence reaction, not as an integrated ending framework. The snapshot covers the chapter's substance but does not organize its terminal psychological architecture into a usable structural whole.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[4]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/huochu_shengming_de_yiyi_private_zh__segment_1.md`.

## Scoring Interpretation

This section explains how the trace above becomes the Eval-1 scores for this window.

### Selective Legibility

- Formula used by the run report: `(exact_match + focused_hit) / note_case_count = (7 + 8) / 40 = 0.3750`.
- Incidental cover count `2` is visible support, not recall credit.
- Miss count `23` means the reaction timeline either did not produce a strict source-overlap candidate for the note target or the judge rejected the admitted candidate.
- Unlocatable reaction count `1` is diagnostic only and never becomes a match.

### Memory Quality

- Window MQ is the average of the five probe-time overall scores: 3.5, 4.25, 3.25, 3.75, 3.75 -> `3.70`.
- The probe state sections above show what the mechanism had available at scoring time; final runtime state is not substituted for probe-time evidence.

### Callback / FVI

- Reaction audit reviewed `150` visible reactions: `19` grounded, `9` weak, `0` FVI, `122` local-only.
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
