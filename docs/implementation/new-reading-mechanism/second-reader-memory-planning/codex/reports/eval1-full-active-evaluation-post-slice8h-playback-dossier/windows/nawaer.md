# Eval-1 Playback Dossier: 纳瓦尔宝典

This playback page is a product-facing reading trace for human review. It replays the Eval-1 window in reading order, then explains how the four evaluation channels score that trace. It is not a new eval run, not a catalog update, not product-quality proof, and not Long Span formal authority.

## Window Verdict

- Lane A selective-legibility recall: `0.4348` over `23` note cases (`8` exact, `2` focused, `2` incidental, `11` miss).
- Lane B Memory Quality: `3.65` average over `5` semantic probes.
- Visible reaction audit: `40` reactions (`6` grounded callback, `4` weak callback, `1` FVI, `29` local-only).
- Reviewer stance: read the timeline first, then the scoring interpretation. The score is justified by the trace, not by the aggregate table alone.

## Evidence Map

- Dataset source window: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/nawaer_baodian_private_zh__segment_1.md`
- Raw segment text: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/nawaer_baodian_private_zh__segment_1.txt`
- Lane A run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer`
- Lane B run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer`
- Lane A note cases: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases`
- Lane B MQ rows: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl`
- Lane B reaction audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/reaction_audit_results.jsonl`
- Probe snapshots: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`
- Normalized eval bundle: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`

## Source Window And Chapter Coverage

- Covered chapters: `认识财富创造的原理`
- Full reviewer-readable source window lives beside the dataset: `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.
- Each reaction below includes its own source-span excerpt so the reviewer can stay in reading flow, then jump to the full source window when needed.

## Selective Legibility Note-Case Ledger

This ledger lists every dataset note target in the window. Matched note cases point to the reaction that appears later in the reading timeline; misses remain visible here so reviewer analysis is not biased toward successful reactions only.

### Note `e0001` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0001`
- target note:
```text
赚钱跟工作的努力程度没什么必然联系。
```
- target source span(s):
  - `p3@94-112`: 赚钱跟工作的努力程度没什么必然联系。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0001.json`

### Note `e0002` — `incidental_cover`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002`
- target note:
```text
要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
```
- target source span(s):
  - `p3@136-215`: 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
- matched reaction in timeline: `rx:Full_Content:src:c1:p1@0-p3@215:highlight:2`
- source-span relation: `note_contains_candidate`; coverage `0.3671`
- judge/runner reason: The reaction's quoted span (136-165) covers only the first sentence about the three wealth elements, which is indeed a core part of the note. However, the note also contains important content about 'understanding and thinking being more important than hard work' and 'choosing the correct approach,' which are not covered by the reaction's quote or its derived content. The reaction captures a fraction of the note's key points, making the note's emphasis on understanding vs. hard work incidental to the narrower three-element focus.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002.json`

### Note `e0003` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0003`
- target note:
```text
追求财富，而不是金钱或地位。财富是指在你睡觉时仍能为你赚钱的资产。金钱是我们转换时间和财富的方式。地位是你在社会等级体系中所处的位置。
```
- target source span(s):
  - `p9@0-67`: 追求财富，而不是金钱或地位。财富是指在你睡觉时仍能为你赚钱的资产。金钱是我们转换时间和财富的方式。地位是你在社会等级体系中所处的位置。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0003.json`

### Note `e0004` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004`
- target note:
```text
依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
```
- target source span(s):
  - `p15@0-41`: 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
- matched reaction in timeline: `rx:Full_Content:src:c1:p14@0-p15@41:highlight:7`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004.json`

### Note `e0005` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0005`
- target note:
```text
获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。
```
- target source span(s):
  - `p17@0-37`: 获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0005.json`

### Note `e0006` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0006`
- target note:
```text
选择一个有长期发展前景的行业，找到可以长期合作的人。
```
- target source span(s):
  - `p19@0-26`: 选择一个有长期发展前景的行业，找到可以长期合作的人。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0006.json`

### Note `e0007` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0007`
- target note:
```text
不要跟愤世嫉俗和消极悲观的人合作。他们的预言会自我实现。
```
- target source span(s):
  - `p27@0-28`: 不要跟愤世嫉俗和消极悲观的人合作。他们的预言会自我实现。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0007.json`

### Note `e0008` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0008`
- target note:
```text
学会销售，学会构建，两技傍身，势不可当。
```
- target source span(s):
  - `p29@0-20`: 学会销售，学会构建，两技傍身，势不可当。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0008.json`

### Note `e0009` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0009`
- target note:
```text
用专长、责任感和杠杆效应武装自己。
```
- target source span(s):
  - `p31@0-17`: 用专长、责任感和杠杆效应武装自己。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0009.json`

### Note `e0010` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010`
- target note:
```text
专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
```
- target source span(s):
  - `p33@0-43`: 专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
- matched reaction in timeline: `rx:Full_Content:src:c1:p32@0-p35@30:highlight:10`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010.json`

### Note `e0011` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0011`
- target note:
```text
要想有所专长，就要追求真正的兴趣和热爱，而不是盲目追逐热点。
```
- target source span(s):
  - `p35@0-30`: 要想有所专长，就要追求真正的兴趣和热爱，而不是盲目追逐热点。
- matched reaction in timeline: `rx:Full_Content:src:c1:p32@0-p35@30:highlight:11`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0011.json`

### Note `e0012` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0012`
- target note:
```text
累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。
```
- target source span(s):
  - `p37@0-27`: 累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。
- matched reaction in timeline: `rx:Full_Content:src:c1:p36@0-p37@27:highlight:12`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0012.json`

### Note `e0013` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0013`
- target note:
```text
专长往往具有高度的技术性或创造性，不能被外包或自动化。
```
- target source span(s):
  - `p41@0-27`: 专长往往具有高度的技术性或创造性，不能被外包或自动化。
- matched reaction in timeline: `rx:Full_Content:src:c1:p40@0-p43@43:highlight:14`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0013.json`

### Note `e0014` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0014`
- target note:
```text
商业杠杆来自资本、劳动力和复制边际成本为零的产品（代码和媒体）。
```
- target source span(s):
  - `p47@19-51`: 商业杠杆来自资本、劳动力和复制边际成本为零的产品（代码和媒体）。
- matched reaction in timeline: `rx:Full_Content:src:c1:p44@0-p47@51:retrospect:16`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0014.json`

### Note `e0015` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0015`
- target note:
```text
劳动力杠杆就是让别人为你工作。这是最古老、争夺最激烈的一种杠杆。拥有劳动力杠杆会让你的父母觉得你很了不起，但不要过度追逐劳动力杠杆。
```
- target source span(s):
  - `p51@0-66`: 劳动力杠杆就是让别人为你工作。这是最古老、争夺最激烈的一种杠杆。拥有劳动力杠杆会让你的父母觉得你很了不起，但不要过度追逐劳动力杠杆。
- matched reaction in timeline: `rx:Full_Content:src:c1:p50@0-p51@66:highlight:18`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0015.json`

### Note `e0016` — `incidental_cover`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016`
- target note:
```text
代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
```
- target source span(s):
  - `p55@0-59`: 代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
- matched reaction in timeline: `rx:Full_Content:src:c1:p54@0-p55@59:highlight:21`
- source-span relation: `note_contains_candidate`; coverage `0.322`
- judge/runner reason: The reaction's quoted span covers only the first sentence of the note ('代码和媒体是不需要许可就能使用的杠杆'), which addresses permission-free leverage but not the note's distinctive content about code/media being the leverage of the new wealthy class and enabling work while sleeping. The reaction merely explains the permission aspect and the three-part categorization rather than genuinely engaging with the note's core insight about wealth creation mechanics.
- reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016.json`

### Note `e0017` — `exact_match`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0017`
- target note:
```text
学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。
```
- target source span(s):
  - `p67@0-31`: 学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。
- matched reaction in timeline: `rx:Full_Content:src:c1:p64@0-p67@31:discern:26`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0017.json`

### Note `e0018` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0018`
- target note:
```text
读比听快，做比看快。
```
- target source span(s):
  - `p69@0-10`: 读比听快，做比看快。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0018.json`

### Note `e0019` — `focused_hit`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019`
- target note:
```text
这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。
```
- target source span(s):
  - `p86@0-81`: 这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。
- matched reaction in timeline: `rx:Full_Content:src:c1:p85@0-p88@72:highlight:32`
- source-span relation: `partial_overlap`; coverage `0.679`
- judge/runner reason: The reaction's quoted source span covers the core substantive content of the note—the examples tying "自己" to uniqueness, responsibility, and expertise, and "产品化" to leverage and expertise. The reaction's analysis directly interprets this structural overlap, explaining how "专长" serves as a double-anchor that connects the two concepts and unifies the conceptual system. The overlap is substantial (0.679) and genuinely addresses the note's central insight about the "交叉重叠" structure.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019.json`

### Note `e0020` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0020`
- target note:
```text
金钱是社会的信用符号，具有调用别人时间的能力。
```
- target source span(s):
  - `p90@13-36`: 金钱是社会的信用符号，具有调用别人时间的能力。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0020.json`

### Note `e0021` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0021`
- target note:
```text
所以，我对财富的定义是在睡觉时也能带来收入的企业和资产。
```
- target source span(s):
  - `p94@0-28`: 所以，我对财富的定义是在睡觉时也能带来收入的企业和资产。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0021.json`

### Note `e0022` — `miss`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0022`
- target note:
```text
要想在社会上赚到钱，就要为社会提供其有需求但无从获得的东西。如果社会已经创造出需要的产品和服务，你也就不被需要了。
```
- target source span(s):
  - `p96@0-57`: 要想在社会上赚到钱，就要为社会提供其有需求但无从获得的东西。如果社会已经创造出需要的产品和服务，你也就不被需要了。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0022.json`

### Note `e0023` — `focused_hit`

- note_case_id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023`
- target note:
```text
社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
```
- target source span(s):
  - `p98@67-146`: 社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
- matched reaction in timeline: `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`
- source-span relation: `note_contains_candidate`; coverage `0.4051`
- judge/runner reason: The reaction specifically targets the "轻松自然" portion of the overlapped source span and develops a substantive analysis by connecting it to another principle ("专长累积像玩耍") to form a combined test for identifying one's true expertise. While the note covers a broader theme (wealth creation through providing what society needs), the reaction's focus on a key component within the shared span and its analytical development of that component's meaning justifies a focused_hit label.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023.json`

## Reading Timeline: All Visible Reactions

Every visible reaction in this Eval-1 window is listed in reading order. Fields are conditional: callback/FVI details appear only when the audit found a callback claim; Selective Legibility details appear only when the reaction overlapped a dataset note target.

### Reaction 001 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p3@215:highlight:1`
- source span: `src:c1:p3@0-p3@8`
- source span excerpt:
```text
能学会。[78]
```
- visible reaction:
```text
以断言代替论证，直接把财富创造定性为可掌握的技能。这个"能学会"预设了方法论的存在，是整章的基点。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 002 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p3@215:highlight:2`
- source span: `src:c1:p3@136-p3@165`
- source span excerpt:
```text
要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。
```
- visible reaction:
```text
财富三要素：做什么（内容选择）、和谁（合作伙伴/团队）、什么时候（时机判断）。不是埋头苦干，而是这三个维度的决策质量决定结果。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002` / note `nawaer_baodian_private_zh_personal_notes__e0002` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p3@136-215` 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
    - target note: 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
    - source-span relation: `note_contains_candidate`; coverage `0.37`
    - judge/runner reason: The reaction's quoted span (136-165) covers only the first sentence about the three wealth elements, which is indeed a core part of the note. However, the note also contains important content about 'understanding and thinking being more important than hard work' and 'choosing the correct approach,' which are not covered by the reaction's quote or its derived content. The reaction captures a fraction of the note's key points, making the note's emphasis on understanding vs. hard work incidental to the narrower three-element focus.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 003 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p4@0-p6@136:highlight:3`
- source span: `src:c1:p4@0-p4@39`
- source span excerpt:
```text
如果还不知道自己应该做什么，那么你先要弄清楚这个问题。在这之前，不要盲目发力。
```
- visible reaction:
```text
这是对前面"能学会"的直接补充：学会之前还有一个前提性问题——学什么、做什么。不能跳过这个自我澄清的阶段直接进入方法论。这个顺序本身是有信息的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 004 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p4@0-p6@136:highlight:4`
- source span: `src:c1:p5@98-p5@124`
- source span excerpt:
```text
然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
```
- visible reaction:
```text
这个"可悲还是幸运"的自问很有意思——它不是谦辞，而是真实的不确定：擅长找到杠杆支点并攫取财富，这件事本身是值得庆幸的能力，还是某种让人停不下来的诅咒？这种模糊性让作者显得比一般的财富导师更诚实。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 005 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p11@39:highlight:5`
- source span: `src:c1:p11@18-p11@39`
- source span excerpt:
```text
如果你内心鄙视财富，财富就会对你避而远之。
```
- visible reaction:
```text
这句话把道德兼容性的反面说透了：不是"不能"拥有财富，而是内心对财富的排斥会直接导致财富的疏离。是一种自我应验的预言。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 006 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p12@0-p13@33:highlight:6`
- source span: `src:c1:p13@0-p13@33`
- source span excerpt:
```text
无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
```
- visible reaction:
```text
这句话揭示了一种经典的权力逻辑：地位是一个零和博弈的坐标，它的增长只能通过贬低他人来实现。而攻击的靶点往往选得精准——恰好是那些真正在做有价值之事的人。这种「攻击创造者」的行为模式，本质上是一种嫉妒的投射，比单纯的贪婪更难对付。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 007 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p14@0-p15@41:highlight:7`
- source span: `src:c1:p15@0-p15@41`
- source span excerpt:
```text
依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
```
- visible reaction:
```text
把工资劳动称为"出租时间"是很犀利的表述——它把这种交易模式的本质暴露出来了：你在出卖生命时间，换来一次性报酬，但没有积累任何生产资料。这种命名方式本身就带有一股揭示感。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004` / note `nawaer_baodian_private_zh_personal_notes__e0004` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p15@0-41` 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
    - target note: 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 008 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p22@0-p23@38:highlight:8`
- source span: `src:c1:p23@7-p23@38`
- source span excerpt:
```text
生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。
```
- visible reaction:
```text
这个"都来自复利"的断言很宽——把关系和知识也纳入复利框架，隐含了一个前提：所有这些领域的回报都需要时间积累和正向反馈循环才能产生质变。它不只是在说道理，而是在给"迭代思维"提供一个底层逻辑。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 009 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p24@0-p25@32:highlight:9`
- source span: `src:c1:p25@0-p25@32`
- source span excerpt:
```text
选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。
```
- visible reaction:
```text
这这句话把「正直诚信」放在了比「聪明」和「精力充沛」更高的优先级上，形成了一种筛选逻辑：技术能力可以被替代，但品格的缺陷无法弥补。这种排序在商业建议中不常见——通常人们会把能力放在前面，这里却明确说"更重要的是"品性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 010 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p32@0-p35@30:highlight:10`
- source span: `src:c1:p33@0-p33@43`
- source span excerpt:
```text
专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
```
- visible reaction:
```text
这个"如果……那么"的反事实结构很犀利——它把专长的反面说成是"可替代性"，等于给专长下了一个功能性定义：不是"你会什么"，而是"别人不会什么，而且学不来"。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010` / note `nawaer_baodian_private_zh_personal_notes__e0010` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p33@0-43` 专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
    - target note: 专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 011 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p32@0-p35@30:highlight:11`
- source span: `src:c1:p35@0-p35@30`
- source span excerpt:
```text
要想有所专长，就要追求真正的兴趣和热爱，而不是盲目追逐热点。
```
- visible reaction:
```text
前一句在用可替代性这把尺子量人，这一句却把尺子换成了内在动机——两句话的底层逻辑不同，一个是外部竞争视角，一个是内部价值视角。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0011` / note `nawaer_baodian_private_zh_personal_notes__e0011` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p35@0-30` 要想有所专长，就要追求真正的兴趣和热爱，而不是盲目追逐热点。
    - target note: 要想有所专长，就要追求真正的兴趣和热爱，而不是盲目追逐热点。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0011.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 012 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p36@0-p37@27:highlight:12`
- source span: `src:c1:p37@0-p37@27`
- source span excerpt:
```text
累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。
```
- visible reaction:
```text
这句话和前文形成了一个检验标准：如果你正在做的事情让你觉得吃力而不是好玩，那可能说明你不是真的在追求真正的兴趣和热爱，而是在追逐外部热点。这个标准不是"你能坚持多久"，而是"这个过程本身对你来说是什么质地"。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0012` / note `nawaer_baodian_private_zh_personal_notes__e0012` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p37@0-27` 累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。
    - target note: 累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0012.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 013 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13`
- source span: `src:c1:p39@0-p39@32`
- source span excerpt:
```text
专长的传授需要通过师傅带徒弟的方式完成，而无法通过学校教育完成。
```
- visible reaction:
```text
这句话和前面那句「专长指的是无法通过培训获得的知识」形成了完整的逻辑闭环：前一句给出了定义层面的约束（不可培训性），这一句给出了实践层面的约束（不可学校化）。两个「无法」指向同一个方向——专长的获得和传授都绕不开个人化的、近身的接触。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p32@0-p35@30:highlight:10"]}`
  - judge reason: Prior link to reaction 10 is explicit and correctly identified. The logical closure between '不可培训性' (definition layer) and '不可学校化' (practice layer) is a precise, well-supported connection back to the earlier expertise definition.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 014 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p40@0-p43@43:highlight:14`
- source span: `src:c1:p41@0-p41@27`
- source span excerpt:
```text
专长往往具有高度的技术性或创造性，不能被外包或自动化。
```
- visible reaction:
```text
这句话和前文建立的专长概念形成同方向延伸：不可培训、不可学校化、不可外包自动化——三个"不能"从不同维度指向同一个结论：专长是个人化的、不可标准化的。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0013` / note `nawaer_baodian_private_zh_personal_notes__e0013` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p41@0-27` 专长往往具有高度的技术性或创造性，不能被外包或自动化。
    - target note: 专长往往具有高度的技术性或创造性，不能被外包或自动化。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0013.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: The content gestures at '前文' with vague self-reference but provides no explicit prior link in metadata. The claim of three 'cannots' summarizing earlier material lacks specificity about which earlier reaction is being extended.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 015 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p40@0-p43@43:highlight:15`
- source span: `src:c1:p43@0-p43@43`
- source span excerpt:
```text
培养责任感，勇于以个人名义承担商业风险。社会将根据责任大小、股权多少和杠杆效应回报你。
```
- visible reaction:
```text
这里出现了一个视角切换：从"专长的内在属性"（技术性、创造性、热爱驱动）转向"获取财富所需的个人行动"（承担责任、持股、使用杠杆）。专长是入场券，愿意用个人名义承担风险才是真正的分界线。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 016 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p44@0-p47@51:retrospect:16`
- source span: `src:c1:p47@19-p47@51`
- source span excerpt:
```text
商业杠杆来自资本、劳动力和复制边际成本为零的产品（代码和媒体）。
```
- visible reaction:
```text
这里把商业杠杆落实为三个可识别的类别，"复制边际成本为零"这个经济学措辞精确地刻画了代码和媒体的特性——一次创造、无限分发、没有边际成本。这也呼应了前文对专长积累的描述：高杠杆的领域，往往就是那些无法被标准化、外包或自动化的个人化领域。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0014` / note `nawaer_baodian_private_zh_personal_notes__e0014` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p47@19-51` 商业杠杆来自资本、劳动力和复制边际成本为零的产品（代码和媒体）。
    - target note: 商业杠杆来自资本、劳动力和复制边际成本为零的产品（代码和媒体）。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0014.json`
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p40@0-p43@43:highlight:14", "active_attention:expertise_play_vs_effort"]}`
  - judge reason: Prior link to reaction 14 is explicit and substantively supported. The claim that high-leverage fields align with non-standardizable personal expertise is a concrete, correct extension of reaction 14's '三个不能' framing.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 017 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p48@0-p49@39:highlight:17`
- source span: `src:c1:p49@0-p49@39`
- source span excerpt:
```text
资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。
```
- visible reaction:
```text
这句话把"资本"与"专长"、"责任感"、"判断力"放在了同一个行动链条里。前面已经建立了专长和责任感的个人积累维度，这里把它们兑现为获取资本的手段——要获得融资光有钱不够，必须以专长和信誉作为背书。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 018 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p50@0-p51@66:highlight:18`
- source span: `src:c1:p51@0-p51@66`
- source span excerpt:
```text
劳动力杠杆就是让别人为你工作。这是最古老、争夺最激烈的一种杠杆。拥有劳动力杠杆会让你的父母觉得你很了不起，但不要过度追逐劳动力杠杆。
```
- visible reaction:
```text
"争夺最激烈"这个判断很有分量。结合前文，资本杠杆需要专长和信誉作为背书，代码/媒体杠杆依赖个人技能积累，而劳动力杠杆的门槛相对最低——任何有钱的人都可以雇佣他人，这意味着它早已是一片红海。作者在三种杠杆的排序中隐含了价值递减的梯度。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0015` / note `nawaer_baodian_private_zh_personal_notes__e0015` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p51@0-66` 劳动力杠杆就是让别人为你工作。这是最古老、争夺最激烈的一种杠杆。拥有劳动力杠杆会让你的父母觉得你很了不起，但不要过度追逐劳动力杠杆。
    - target note: 劳动力杠杆就是让别人为你工作。这是最古老、争夺最激烈的一种杠杆。拥有劳动力杠杆会让你的父母觉得你很了不起，但不要过度追逐劳动力杠杆。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0015.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 019 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p52@0-p53@57:highlight:19`
- source span: `src:c1:p53@0-p53@21`
- source span excerpt:
```text
资本和劳动力是需要获得许可才能使用的杠杆。
```
- visible reaction:
```text
这句话与前文三类杠杆的框架形成内部分类：资本/劳动力的许可依赖性，区别于代码/媒体的自主扩展性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 020 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p52@0-p53@57:highlight:20`
- source span: `src:c1:p53@21-p53@57`
- source span excerpt:
```text
人人都在追逐资本，但得有人愿意出资。人人都想领导他人，但得有人愿意追随。
```
- visible reaction:
```text
两句并置，道出了追逐与获得之间那道必须由他人来填补的鸿沟——需求是单向的，但实现是双向依赖的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 021 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p54@0-p55@59:highlight:21`
- source span: `src:c1:p55@0-p55@19`
- source span excerpt:
```text
代码和媒体是不需要许可就能使用的杠杆。
```
- visible reaction:
```text
这与前文"资本和劳动力是需要获得许可才能使用的杠杆"形成直接对照。三种杠杆由此完成了许可依赖性的光谱排列：劳动力需要雇佣协议，资本需要融资同意，而代码/媒体只依赖个人技能积累，无需第三方授权。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016` / note `nawaer_baodian_private_zh_personal_notes__e0016` / label `incidental_cover` / best `true` / recall-credit `false`
    - target span(s): `p55@0-59` 代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
    - target note: 代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
    - source-span relation: `note_contains_candidate`; coverage `0.32`
    - judge/runner reason: The reaction's quoted span covers only the first sentence of the note ('代码和媒体是不需要许可就能使用的杠杆'), which addresses permission-free leverage but not the note's distinctive content about code/media being the leverage of the new wealthy class and enabling work while sleeping. The reaction merely explains the permission aspect and the three-part categorization rather than genuinely engaging with the note's core insight about wealth creation mechanics.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 022 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p54@0-p55@59:highlight:22`
- source span: `src:c1:p55@19-p55@35`
- source span excerpt:
```text
这两个杠杆是新富阶层背后的杠杆。
```
- visible reaction:
```text
"新富阶层"这个定性在价值排序上有分量——它暗示代码/媒体杠杆不只是"更好的选择"，而是当代财富迁移的结构性标志。结合前文劳动力杠杆的"争夺最激烈"，三种杠杆的价值梯度已完整呈现。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016` / note `nawaer_baodian_private_zh_personal_notes__e0016` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p55@0-59` 代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
    - target note: 代码和媒体是不需要许可就能使用的杠杆。这两个杠杆是新富阶层背后的杠杆。你可以创建软件和媒体，让它们在你睡觉时为你工作。
    - source-span relation: `note_contains_candidate`; coverage `0.27`
    - judge/runner reason: The reaction's quoted span (the sentence about '新富阶层') is indeed contained in the note, but the reaction focuses narrowly on the significance of the '新富阶层' characterization within a value hierarchy. It does not engage with the note's central themes about code/media being 'permissionless levers' or the concept of creating assets that 'work while you sleep.' The note's most important substantive points are peripheral to what the reaction addresses.
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0016.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 023 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p58@0-p59@25:highlight:23`
- source span: `src:c1:p59@0-p59@25`
- source span excerpt:
```text
如果不会写代码，那就出书、写博客、做视频、录播客。
```
- visible reaction:
```text
这句话把"代码和媒体是不需要许可的杠杆"落地成具体路径——四种形态，覆盖了从深度内容到即时传播的完整媒体光谱。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 024 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p60@0-p63@27:highlight:24`
- source span: `src:c1:p61@0-p61@11`
- source span excerpt:
```text
杠杆是判断力的倍增器。
```
- visible reaction:
```text
这个定义把杠杆从技术工具层面拉升到认知能力层面——杠杆的效力取决于使用者的判断力质量，而不是工具本身的属性。这为前文"代码和媒体是不需要许可的杠杆"提供了内在逻辑：许可门槛低，但判断力门槛仍然存在。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 025 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p60@0-p63@27:highlight:25`
- source span: `src:c1:p63@0-p63@27`
- source span excerpt:
```text
判断力从经验中来，但可以通过学习基本技能快速建立起来。
```
- visible reaction:
```text
这句话把"判断力"从纯粹的经验主义框架中解放出来——虽然它起源于经验，但基本技能的学习可以绕过漫长的摸索期。这是一个相当乐观的认识论主张，直接回应了"普通人如何获取杠杆"的隐含问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 026 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p64@0-p67@31:discern:26`
- source span: `src:c1:p67@0-p67@31`
- source span excerpt:
```text
学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。
```
- visible reaction:
```text
这份清单与前文"判断力是杠杆的倍增器"构成直接呼应：微观经济学理解激励结构，博弈论处理策略互动，心理学和说服术指向人与人的影响，伦理学提供价值框架，数学与计算机则是建模和执行的工具——这不是随机的课程列表，而是支撑高质量判断的完整认知工具箱。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0017` / note `nawaer_baodian_private_zh_personal_notes__e0017` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p67@0-31` 学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。
    - target note: 学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0017.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly maps the discipline list to earlier material ('判断力是杠杆的倍增器') and provides thematic connection to reaction 24's definition of judgment as cognitive capability.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 027 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p72@0-p73@66:highlight:27`
- source span: `src:c1:p73@0-p73@18`
- source span excerpt:
```text
设定一个大胆的个人时薪，并严格执行。
```
- visible reaction:
```text
"大胆"这个词很关键——它暗示要高于自己感觉舒适的水平，实际上是在对抗人们普遍低估自己时间价值的倾向。这里隐含着一种自我尊重的姿态：你的时间是有真实成本的，不是可以随便挥霍的廉价品。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 028 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p74@0-p75@36:highlight:28`
- source span: `src:c1:p75@0-p75@36`
- source span excerpt:
```text
工作时要拼尽全力，毫无保留。不过，共事的人和工作的内容比努力程度更重要。
```
- visible reaction:
```text
这个"不过"是全文最简洁的战略声明之一：它把努力从首要位置拉下来，把选择（和谁一起、做什么事）放到了前面。这与前文"正直诚信才是决定性要素"形成跨段落共振——都在说：决策质量决定结果质量，努力只是执行层的事。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly invokes cross-paragraph resonance with reaction 9 ('正直诚信才是决定性要素'), correctly linking the prioritization of choices over effort to the earlier prioritization of integrity over competence.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 029 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p78@0-p79@35:highlight:29`
- source span: `src:c1:p79@0-p79@35`
- source span excerpt:
```text
世界上没有快速致富的教程。即使有，那也只是提供教程的人想从你身上赚钱。
```
- visible reaction:
```text
两句话完成了一次动机溯源：断定了"教程不存在"之后，紧接着指出"如果存在，制作者就是在利用你"——这已经把判断规则内嵌进去了：所有快速致富教程的盈利结构本身，就是最好的鉴定信号。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 030 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p80@0-p84@10:highlight:30`
- source span: `src:c1:p83@0-p83@40`
- source span excerpt:
```text
当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。
```
- visible reaction:
```text
"后话，暂且不提"——这句话本身就是叙事节奏的操控。它故意在财富这个"显而易见的目标"背后撕开了一个口子，暗示追求的起点另有所在。这种写法让结尾带上了未完成感，而不是一个干净的自洽结论。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 031 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p80@0-p84@10:highlight:31`
- source span: `src:c1:p84@0-p84@10`
- source span excerpt:
```text
总结：把自己产品化。
```
- visible reaction:
```text
五个字完成了整个章节的压缩。所有分散的原则——专长、杠杆、判断力、责任、时薪框架——都在这个公式里找到了聚合点。它既是命令句，也是诊断工具：你现在做的，是不是在"产品化自己"？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly connects back to the chapter's core concepts (专长, 杠杆, 判断力, 责任感, 时薪框架) introduced in earlier reactions, identifying the '产品化自己' formula as their聚合点.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 032 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p85@0-p88@72:highlight:32`
- source span: `src:c1:p86@26-p86@102`
- source span excerpt:
```text
“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。因此，这两个重点就可以概括上述所有的理念。
```
- visible reaction:
```text
这个"交叉重叠"的结构很有意思："专长"既是"产品化"的门槛，也是"自己"本来就有的东西。作者用这个词的双重归属，把整个分散的理念体系——责任感、判断力、独特性、杠杆——全部锚定在这两个词的交叉点上。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019` / note `nawaer_baodian_private_zh_personal_notes__e0019` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p86@0-81` 这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。
    - target note: 这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。
    - source-span relation: `partial_overlap`; coverage `0.68`
    - judge/runner reason: The reaction's quoted source span covers the core substantive content of the note—the examples tying "自己" to uniqueness, responsibility, and expertise, and "产品化" to leverage and expertise. The reaction's analysis directly interprets this structural overlap, explaining how "专长" serves as a double-anchor that connects the two concepts and unifies the conceptual system. The overlap is substantial (0.679) and genuinely addresses the note's central insight about the "交叉重叠" structure.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Uses '专长' as an anchor term, which was extensively discussed in reactions 10, 13, 14, and 16, and correctly identifies how the '产品化' and '自己' framework absorbs multiple earlier principles.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 033 — `false_visible_integration` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p85@0-p88@72:retrospect:33`
- source span: `src:c1:p88@31-p88@68`
- source span excerpt:
```text
并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？
```
- visible reaction:
```text
这与前面"当你终于变得富有时，你会意识到，这并不是你最初的追求"形成呼应——财富不是起点，"我能提供什么独特的价值"才是真正需要花几十年去回答的问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `false_visible_integration`
  - prior_link: `{"ref_ids": ["thread:original_pursuit_vs_wealth"]}`
  - judge reason: 声称呼应前文具体引文'当你终于变得富有时，你会意识到，这并不是你最初的追求'，但该引文未出现在当前阅读窗口内的可见材料中。prior_link所引的thread标签属于主题类投射，非文本级可见回调，为过拟合类集成。
  - reviewer interpretation: rejected visible integration; the reaction claims a connection the visible evidence surface does not support.

### Reaction 034 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p89@0-p93@57:highlight:34`
- source span: `src:c1:p91@57-p91@75`
- source span excerpt:
```text
这是一张欠条，我们可以把这个叫作钱。
```
- visible reaction:
```text
把货币直接定义为"欠条"，这比任何教科书定义都更直接地暴露了金钱的本质——它不是财富本身，而是一张等待兑现的社会凭证。这意味着追逐金钱本质上是在追逐对他人的索取权，而不是在创造真实的价值承载物。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 035 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p89@0-p93@57:highlight:35`
- source span: `src:c1:p92@12-p92@32`
- source span excerpt:
```text
财富就是在你睡觉时也可以帮你赚钱的资产。
```
- visible reaction:
```text
这个定义直接呼应了"把自己产品化"的最终目标：你不是在销售时间，而是在部署一套能在你缺席时继续运转的系统。睡眠测试是一个非常直觉化的检验标准——如果一个资产停止运作你就停止收入，那它就不是真正的财富。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称'直接呼应把自己产品化的最终目标'，但'把自己产品化'的表述未在前文可见段落中以该措辞出现，回调方向正确但措辞缺乏可见文本支撑。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 036 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`
- source span: `src:c1:p98@114-p98@146`
- source span excerpt:
```text
提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
```
- visible reaction:
```text
"轻松自然"这个条件与前面"专长累积像玩耍"形成精确呼应——两个标准合并成一个更完整的检验：如果你做的事既像玩耍，又是轻松自然的，那它大概率就是你真正的专长所在，也可能是财富的入口。
```
- Selective Legibility dataset relation:
  - note-case `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023` / note `nawaer_baodian_private_zh_personal_notes__e0023` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p98@67-146` 社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
    - target note: 社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
    - source-span relation: `note_contains_candidate`; coverage `0.41`
    - judge/runner reason: The reaction specifically targets the "轻松自然" portion of the overlapped source span and develops a substantive analysis by connecting it to another principle ("专长累积像玩耍") to form a combined test for identifying one's true expertise. While the note covers a broader theme (wealth creation through providing what society needs), the reaction's focus on a key component within the shared span and its analytical development of that component's meaning justifies a focused_hit label.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前面'专长累积像玩耍'形成精确呼应，但'专长累积像玩耍'并非前文可见段落中的已有表述，其所依据的reaction 12内容为问句形式，与此处断言存在落差。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 037 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p94@0-p98@146:highlight:37`
- source span: `src:c1:p98@45-p98@67`
- source span excerpt:
```text
某种东西一旦得到广泛应用，它就不再是科技了。
```
- visible reaction:
```text
这提供了一个关于技术价值的锐利时间窗口视角：科技在被广泛采用前才有超额回报，之后就变成基础设施。这个定义把"科技投资"从玄学变成一个可辨识的生命周期问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 038 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p99@0-p99@193:highlight:38`
- source span: `src:c1:p99@0-p99@65`
- source span excerpt:
```text
下一步是思考如何规模化，因为只提供一个产品或一项服务是远远不够的，必须提供成千上万个，甚至几十万、几百万、几十亿个，最好人手一个。
```
- visible reaction:
```text
这个表述把「规模化」从商业术语变成了一种思维姿态——不是「如果成功了再考虑规模」，而是把规模本身作为设计目标。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 039 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p99@0-p99@193:highlight:39`
- source span: `src:c1:p99@93-p99@189`
- source span excerpt:
```text
他们设想的是一台可以装在口袋里随身携带的小型计算机，拥有电话的所有功能，甚至比电话的功能还强大100倍，使用起来也非常简单。然后，他们研究出了如何制造这样一部智能手机，以及如何实现规模化生产。
```
- visible reaction:
```text
从「设想」到「规模化生产」之间有一个隐含的关键步骤：制造工艺的突破。这暗示了一个财富创造的结构性要求——不仅要想得好，还要能让别人也能生产。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 040 — `weak_callback` — `retrospect`

- reaction_id: `rx:Chapter_1:src:c1:p99@193-p99@193:retrospect:1`
- source span: `src:c1:p99@193-p99@193`
- source span excerpt:
```text
下一步是思考如何规模化，因为只提供一个产品或一项服务是远远不够的，必须提供成千上万个，甚至几十万、几百万、几十亿个，最好人手一个。史蒂夫·乔布斯（当然还有他的团队）发现社会需要智能手机。他们设想的是一台可以装在口袋里随身携带的小型计算机，拥有电话的所有功能，甚至比电话的功能还强大100倍，使用起来也非常简单。然后，他们研究出了如何制造这样一部智能手机，以及如何实现规模化生产。[78]
```
- visible reaction:
```text
这一章的独特之处在于它把财富叙事从「努力」转向「结构」——不是教人更拼命，而是教人选对系统、站在对的位置、用对的方式放大。这个框架为整本书定下了基调：财富是一种可习得、可设计、可迭代的系统能力，而非少数人的神秘天赋。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 反应以「基调」声明对整章进行总结性定性，虽然内部概念（从努力到结构、可习得性、系统能力）与前文具体内容存在语义关联，但「prior_link」为空且无具体锚点文本，"基调"级别的主张缺少直接、可追溯的文本支撑，属于泛化性总结而非有据可查的回溯链接。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

## Probe Memory Checkpoints

Memory Quality is scored at probe time. The state below is a structured re-layout of the recorded probe snapshot, not a fresh summary and not the final runtime dump.

### Probe 1 — MQ `3.25` — near 20%

#### Probe Position And Question
- target sentence: `c1-s35`
- boundary kind: `foundational thesis cluster close`
- why this point: Closes the opening wealth thesis cluster, where the text distinguishes wealth from money/status and introduces scale.
- structural signals to check:
  - wealth vs money vs status
  - renting time vs owning equity/assets
  - unmet demand and scale

#### Source Orientation
```text
   s33 / p15: 你必须拥有股权（企业的部分所有权），才能实现财务自由。
   s34 / p16: ∨
>> s35 / p17: 获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。
   s36 / p18: ∨
   s37 / p19: 选择一个有长期发展前景的行业，找到可以长期合作的人。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p10@0-p11@39:highlight:5",
      "reaction_id": "rx:Full_Content:src:c1:p10@0-p11@39:highlight:5",
      "type": "highlight",
      "thought": "这句话把道德兼容性的反面说透了：不是\"不能\"拥有财富，而是内心对财富的排斥会直接导致财富的疏离。是一种自我应验的预言。",
      "emitted_at_source_span_id": "src:c1:p10@0-p11@39",
      "primary_source_ref": {
        "source_span_id": "src:c1:p11@18-p11@39",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 11,
            "char_offset": 39
          }
        },
        "quote": "如果你内心鄙视财富，财富就会对你避而远之。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "如果你内心鄙视财富，财富就会对你避而远之。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p12@0-p13@33:highlight:6",
      "reaction_id": "rx:Full_Content:src:c1:p12@0-p13@33:highlight:6",
      "type": "highlight",
      "thought": "这句话揭示了一种经典的权力逻辑：地位是一个零和博弈的坐标，它的增长只能通过贬低他人来实现。而攻击的靶点往往选得精准——恰好是那些真正在做有价值之事的人。这种「攻击创造者」的行为模式，本质上是一种嫉妒的投射，比单纯的贪婪更难对付。",
      "emitted_at_source_span_id": "src:c1:p12@0-p13@33",
      "primary_source_ref": {
        "source_span_id": "src:c1:p13@0-p13@33",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 13,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 13,
            "char_offset": 33
          }
        },
        "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
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
    "ref_id": "concept:equity_ownership_wealth_path",
    "concept_key": "equity_ownership_wealth_path",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p15@0-p15@41",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 15,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 15,
            "char_offset": 41
          }
        },
        "quote": "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:wealth_creation_frame",
    "concept_key": "wealth_creation_frame",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p3@136-p3@184",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 3,
            "char_offset": 136
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 3,
            "char_offset": 184
          }
        },
        "quote": "要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。"
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
[]
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
    "source_span_id": "src:c1:p5@67-p5@124",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 67
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 124
      }
    },
    "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p15@0-p15@41",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 41
      }
    },
    "quote": "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p3@136-p3@184",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 136
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 3,
        "char_offset": 184
      }
    },
    "quote": "要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@18-p11@39",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 18
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 39
      }
    },
    "quote": "如果你内心鄙视财富，财富就会对你避而远之。",
    "role": "reaction_anchor",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "reaction_anchor",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p15@0-p15@41",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 41
      }
    },
    "quote": "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。",
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
- salience: `3`
- mainline_fidelity: `3`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.25`
- judge reason: The snapshot retains several key concepts including equity ownership as the wealth path and the leverage-points observation skill, and correctly captures the ignore-status-seekers principle. However, the foundational structural signal of wealth vs. money vs. status as a three-way distinction is absent—no concept in the digest explicitly captures this trinity. Furthermore, the source's wealth creation formula '提供其有需求但无从获得的东西，并实现规模化' is missing the scale component entirely; only the unmet demand phrase appears implicitly via one highlight. The moral compatibility principle appears only in recent_reactions as a visible trace rather than as a durable concept. Organization is decent but the missing structural signals significantly weaken how well the snapshot would help a reader reconstruct the chapter's core argument.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[0]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.

### Probe 2 — MQ `3.50` — near 40%

#### Probe Position And Question
- target sentence: `c1-s65`
- boundary kind: `specific-knowledge cluster close`
- why this point: Closes the specific-knowledge discussion before leverage becomes the dominant frame.
- structural signals to check:
  - specific knowledge definition
  - sales/build pairing
  - interest, apprenticeship, and non-outsourcable skill

#### Source Orientation
```text
   s63 / p42: ∨
   s64 / p43: 培养责任感，勇于以个人名义承担商业风险。
>> s65 / p43: 社会将根据责任大小、股权多少和杠杆效应回报你。
   s66 / p44: ∨
   s67 / p45: “给我一根足够长的杠杆和一个支点，我就能撬动地球。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
  "hot_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13",
      "reaction_id": "rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13",
      "type": "retrospect",
      "thought": "这句话和前面那句「专长指的是无法通过培训获得的知识」形成了完整的逻辑闭环：前一句给出了定义层面的约束（不可培训性），这一句给出了实践层面的约束（不可学校化）。两个「无法」指向同一个方向——专长的获得和传授都绕不开个人化的、近身的接触。",
      "emitted_at_source_span_id": "src:c1:p38@0-p39@32",
      "primary_source_ref": {
        "source_span_id": "src:c1:p39@0-p39@32",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 39,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 39,
            "char_offset": 32
          }
        },
        "quote": "专长的传授需要通过师傅带徒弟的方式完成，而无法通过学校教育完成。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "专长的传授需要通过师傅带徒弟的方式完成，而无法通过学校教育完成。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p40@0-p43@43:highlight:14",
      "reaction_id": "rx:Full_Content:src:c1:p40@0-p43@43:highlight:14",
      "type": "highlight",
      "thought": "这句话和前文建立的专长概念形成同方向延伸：不可培训、不可学校化、不可外包自动化——三个\"不能\"从不同维度指向同一个结论：专长是个人化的、不可标准化的。",
      "emitted_at_source_span_id": "src:c1:p40@0-p43@43",
      "primary_source_ref": {
        "source_span_id": "src:c1:p41@0-p41@27",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 41,
            "char_offset": 27
          }
        },
        "quote": "专长往往具有高度的技术性或创造性，不能被外包或自动化。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "专长往往具有高度的技术性或创造性，不能被外包或自动化。",
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
    "ref_id": "concept:compound_returns_life",
    "concept_key": "compound_returns_life",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@7-p23@38",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 7
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 38
          }
        },
        "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:dual_core_competencies",
    "concept_key": "dual_core_competencies",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p29@0-p29@20",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 20
          }
        },
        "quote": "学会销售，学会构建，两技傍身，势不可当。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "学会销售，学会构建，两技傍身，势不可当。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:equity_ownership_wealth_path",
    "concept_key": "equity_ownership_wealth_path",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p15@0-p15@41",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 15,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 15,
            "char_offset": 41
          }
        },
        "quote": "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。"
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
[]
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
    "source_span_id": "src:c1:p5@67-p5@124",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 67
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 124
      }
    },
    "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p25@0-p25@32",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 32
      }
    },
    "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p37@0-p37@27",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 27
      }
    },
    "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@7-p23@38",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 7
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 38
      }
    },
    "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p29@0-p29@20",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 29,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 29,
        "char_offset": 20
      }
    },
    "quote": "学会销售，学会构建，两技傍身，势不可当。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p15@0-p15@41",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 15,
        "char_offset": 41
      }
    },
    "quote": "依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p39@0-p39@32",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 39,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 39,
        "char_offset": 32
      }
    },
    "quote": "专长的传授需要通过师傅带徒弟的方式完成，而无法通过学校教育完成。",
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
- salience: `3`
- mainline_fidelity: `4`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.5`
- judge reason: The snapshot retains strong individual items (复利回报, 股权致富, 销售构建双技傍身, 合伙人正直诚信优先) and correctly marks the transition at responsibility/leverage. However, the "specific knowledge" cluster's defining structure is only partially retained: the definition '专长指的是无法通过培训获得的知识' is NOT captured as a standalone definition (only the play-vs-effort downstream implication is retained), and the source's explicit three-part structure (兴趣热爱 → 师徒制传授 → 不可外包自动化) appears only as scattered visible traces (reactions) rather than as an organized concept cluster. The sales/build pairing IS captured as concept:dual_core_competencies, satisfying one structural signal. But two of three structural signals (specific knowledge definition, interest/apprenticeship/non-outsourcable triad) are thin or absent, making the salience and organization scores moderate rather than strong.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[1]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.

### Probe 3 — MQ `3.25` — near 55%

#### Probe Position And Question
- target sentence: `c1-s92`
- boundary kind: `leverage taxonomy close`
- why this point: Closes the leverage taxonomy, including permissioned and permissionless leverage.
- structural signals to check:
  - capital, labor, code, and media as leverage
  - permissioned vs permissionless leverage
  - robots, code, media, and data centers

#### Source Orientation
```text
   s90 / p57: 用起来吧。
   s91 / p58: ∨
>> s92 / p59: 如果不会写代码，那就出书、写博客、做视频、录播客。
   s93 / p60: ∨
   s94 / p61: 杠杆是判断力的倍增器。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
  "hot_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p54@0-p55@59:highlight:21",
      "reaction_id": "rx:Full_Content:src:c1:p54@0-p55@59:highlight:21",
      "type": "highlight",
      "thought": "这与前文\"资本和劳动力是需要获得许可才能使用的杠杆\"形成直接对照。三种杠杆由此完成了许可依赖性的光谱排列：劳动力需要雇佣协议，资本需要融资同意，而代码/媒体只依赖个人技能积累，无需第三方授权。",
      "emitted_at_source_span_id": "src:c1:p54@0-p55@59",
      "primary_source_ref": {
        "source_span_id": "src:c1:p55@0-p55@19",
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
            "char_offset": 19
          }
        },
        "quote": "代码和媒体是不需要许可就能使用的杠杆。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "代码和媒体是不需要许可就能使用的杠杆。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p54@0-p55@59:highlight:22",
      "reaction_id": "rx:Full_Content:src:c1:p54@0-p55@59:highlight:22",
      "type": "highlight",
      "thought": "\"新富阶层\"这个定性在价值排序上有分量——它暗示代码/媒体杠杆不只是\"更好的选择\"，而是当代财富迁移的结构性标志。结合前文劳动力杠杆的\"争夺最激烈\"，三种杠杆的价值梯度已完整呈现。",
      "emitted_at_source_span_id": "src:c1:p54@0-p55@59",
      "primary_source_ref": {
        "source_span_id": "src:c1:p55@19-p55@35",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 55,
            "char_offset": 19
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 55,
            "char_offset": 35
          }
        },
        "quote": "这两个杠杆是新富阶层背后的杠杆。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "这两个杠杆是新富阶层背后的杠杆。",
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
    "ref_id": "concept:capital_financing_prerequisites",
    "concept_key": "capital_financing_prerequisites",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p49@0-p49@39",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 39
          }
        },
        "quote": "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:compound_returns_life",
    "concept_key": "compound_returns_life",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@7-p23@38",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 7
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 38
          }
        },
        "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:dual_core_competencies",
    "concept_key": "dual_core_competencies",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p29@0-p29@20",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 20
          }
        },
        "quote": "学会销售，学会构建，两技傍身，势不可当。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "学会销售，学会构建，两技傍身，势不可当。"
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
[]
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
    "source_span_id": "src:c1:p5@67-p5@124",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 67
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 124
      }
    },
    "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p25@0-p25@32",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 32
      }
    },
    "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p37@0-p37@27",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 27
      }
    },
    "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p49@0-p49@39",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 49,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 49,
        "char_offset": 39
      }
    },
    "quote": "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@7-p23@38",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 7
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 38
      }
    },
    "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p29@0-p29@20",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 29,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 29,
        "char_offset": 20
      }
    },
    "quote": "学会销售，学会构建，两技傍身，势不可当。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p55@0-p55@19",
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
        "char_offset": 19
      }
    },
    "quote": "代码和媒体是不需要许可就能使用的杠杆。",
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
- salience: `3`
- mainline_fidelity: `3`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.25`
- judge reason: The snapshot retains individual leverage concepts (capital as money requiring financing, labor as oldest leverage, code/media as permissionless) and includes two reactions about the permissioned/permissionless distinction (labor needs hiring agreements, capital needs financing consent vs. code/media needing only personal skill accumulation). However, three significant gaps exist: (1) The explicit "robots, code, media, and data centers" formulation is absent—the nearby passage '有一大批机器人可供我们免费使用...这些机器人就集中放在数据中心' is not captured in any concept; (2) The core taxonomy organizing structure—capital/labor/code/media as the three-part leverage classification—exists scattered across concept_digest items but is not presented as a unified framework in thread_digest or otherwise; (3) The active_attention items focus on unrelated concepts (status-seekers, partner selection, expertise as play) rather than the leverage taxonomy that is the structural focus of this probe point. The memory captures the individual concepts faithfully but fails to organize them into the salient leverage taxonomy that anchors this segment's mainline argument.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[2]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.

### Probe 4 — MQ `5.00` — near 80%

#### Probe Position And Question
- target sentence: `c1-s139`
- boundary kind: `synthesis close`
- why this point: Closes the self-productization synthesis that combines uniqueness, responsibility, and leverage.
- structural signals to check:
  - productize yourself
  - uniqueness, responsibility, and leverage
  - long-term self-inquiry

#### Source Orientation
```text
   s137 / p88: “把自己产品化”很难。
   s138 / p88: 所以我才说“把自己产品化”要花几十年——并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？
>> s139 / p88: [10]
   s140 / p89: 财富和金钱的区别是什么？
   s141 / p90: 金钱是我们转移财富的方式。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:foundational_disciplines_list",
      "item_id": "foundational_disciplines_list",
      "attention_tags": [
        "model",
        "focus"
      ],
      "statement": "判断力的知识基底：微观经济学（激励与价格机制）、博弈论（策略互动）、心理学（行为动机）、说服术（影响技术）、伦理学（价值判断）、数学（建模与逻辑）、计算机（执行与规模化）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p67@0-p67@31",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 67,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 67,
              "char_offset": 31
            }
          },
          "quote": "学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。",
          "role": "core_definition",
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
      "ref_id": "active_attention:personal_hourly_rate_framework",
      "item_id": "personal_hourly_rate_framework",
      "attention_tags": [
        "model",
        "focus"
      ],
      "statement": "个人时薪决策框架：设定一个足够高的时薪作为决策基准——解决问题节省的成本低于时薪就忽略，外包成本低于时薪就外包。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p73@0-p73@66",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 73,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 73,
              "char_offset": 66
            }
          },
          "quote": "设定一个大胆的个人时薪，并严格执行。如果解决一个问题节省的成本低于时薪，那就忽略问题；如果外包一项任务的成本低于时薪，那就选择外包。",
          "role": "core_definition",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p80@0-p84@10:highlight:31",
      "reaction_id": "rx:Full_Content:src:c1:p80@0-p84@10:highlight:31",
      "type": "highlight",
      "thought": "五个字完成了整个章节的压缩。所有分散的原则——专长、杠杆、判断力、责任、时薪框架——都在这个公式里找到了聚合点。它既是命令句，也是诊断工具：你现在做的，是不是在\"产品化自己\"？",
      "emitted_at_source_span_id": "src:c1:p80@0-p84@10",
      "primary_source_ref": {
        "source_span_id": "src:c1:p84@0-p84@10",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 84,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 84,
            "char_offset": 10
          }
        },
        "quote": "总结：把自己产品化。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "总结：把自己产品化。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p85@0-p88@72:highlight:32",
      "reaction_id": "rx:Full_Content:src:c1:p85@0-p88@72:highlight:32",
      "type": "highlight",
      "thought": "这个\"交叉重叠\"的结构很有意思：\"专长\"既是\"产品化\"的门槛，也是\"自己\"本来就有的东西。作者用这个词的双重归属，把整个分散的理念体系——责任感、判断力、独特性、杠杆——全部锚定在这两个词的交叉点上。",
      "emitted_at_source_span_id": "src:c1:p85@0-p88@72",
      "primary_source_ref": {
        "source_span_id": "src:c1:p86@26-p86@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 86,
            "char_offset": 26
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 86,
            "char_offset": 102
          }
        },
        "quote": "“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。因此，这两个重点就可以概括上述所有的理念。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。因此，这两个重点就可以概括上述所有的理念。",
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
    "ref_id": "concept:capital_financing_prerequisites",
    "concept_key": "capital_financing_prerequisites",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p49@0-p49@39",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 39
          }
        },
        "quote": "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:compound_returns_life",
    "concept_key": "compound_returns_life",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@7-p23@38",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 7
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 38
          }
        },
        "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:dual_core_competencies",
    "concept_key": "dual_core_competencies",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p29@0-p29@20",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 20
          }
        },
        "quote": "学会销售，学会构建，两技傍身，势不可当。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "学会销售，学会构建，两技傍身，势不可当。"
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
    "ref_id": "thread:original_pursuit_vs_wealth",
    "thread_key": "original_pursuit_vs_wealth",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p83@0-p83@40",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 83,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 83,
            "char_offset": 40
          }
        },
        "quote": "当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:wealth_as_derivative_question",
    "thread_key": "wealth_as_derivative_question",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p88@31-p88@68",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 88,
            "char_offset": 31
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 88,
            "char_offset": 68
          }
        },
        "quote": "并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？"
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
    "source_span_id": "src:c1:p5@67-p5@124",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 67
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 124
      }
    },
    "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p25@0-p25@32",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 32
      }
    },
    "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p37@0-p37@27",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 27
      }
    },
    "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p67@0-p67@31",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 67,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 67,
        "char_offset": 31
      }
    },
    "quote": "学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p73@0-p73@66",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 73,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 73,
        "char_offset": 66
      }
    },
    "quote": "设定一个大胆的个人时薪，并严格执行。如果解决一个问题节省的成本低于时薪，那就忽略问题；如果外包一项任务的成本低于时薪，那就选择外包。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p75@0-p75@36",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 75,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 75,
        "char_offset": 36
      }
    },
    "quote": "工作时要拼尽全力，毫无保留。不过，共事的人和工作的内容比努力程度更重要。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p86@26-p86@102",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 86,
        "char_offset": 26
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 86,
        "char_offset": 102
      }
    },
    "quote": "“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。因此，这两个重点就可以概括上述所有的理念。",
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
- salience: `5`
- mainline_fidelity: `5`
- organization: `5`
- fidelity: `5`
- judge-provided overall: `5`
- final overall MQ: `5`
- judge reason: The snapshot captures the chapter's culminating synthesis '把自己产品化' with full fidelity, including the two-pillar structure that maps '自己' (uniqueness + responsibility + expertise) to '产品化' (leverage + expertise). All three structural signals are strongly retained: (1) the 'productize yourself' formula with its two-word elaboration, (2) the uniqueness/responsibility/leverage triad appearing in the active items and reactions, and (3) the long-term self-inquiry thread preserved in the thread_digest as 'wealth_as_derivative_question' and the retrospection connecting it to the 'original pursuit vs wealth' thread. The active_attention items capture high-value principles (foundational disciplines list, hourly rate framework, expertise play-vs-effort test, partner integrity-first) that are salient and non-obvious. Organization is excellent: active items, concept_digest, and thread_digest are cleanly separated, and reactions capture the cross-references between the synthesis and earlier material. This reads as strong chapter-level memory at the synthesis point.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[3]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.

### Probe 5 — MQ `3.25` — window end

#### Probe Position And Question
- target sentence: `c1-s169`
- boundary kind: `meaningful window end`
- why this point: Ends the meaningful body window before citation-only tail material.
- structural signals to check:
  - wealth-building body chapter frame
  - assets, technology, unmet needs, and scale
  - chapter-level synthesis without citation tail

#### Source Orientation
```text
   s167 / p99: 他们设想的是一台可以装在口袋里随身携带的小型计算机，拥有电话的所有功能，甚至比电话的功能还强大100倍，使用起来也非常简单。
   s168 / p99: 然后，他们研究出了如何制造这样一部智能手机，以及如何实现规模化生产。
>> s169 / p99: [78]
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:foundational_disciplines_list",
      "item_id": "foundational_disciplines_list",
      "attention_tags": [
        "model",
        "focus"
      ],
      "statement": "判断力的知识基底：微观经济学（激励与价格机制）、博弈论（策略互动）、心理学（行为动机）、说服术（影响技术）、伦理学（价值判断）、数学（建模与逻辑）、计算机（执行与规模化）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p67@0-p67@31",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 67,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 67,
              "char_offset": 31
            }
          },
          "quote": "学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。",
          "role": "core_definition",
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
      "ref_id": "active_attention:personal_hourly_rate_framework",
      "item_id": "personal_hourly_rate_framework",
      "attention_tags": [
        "model",
        "focus"
      ],
      "statement": "个人时薪决策框架：设定一个足够高的时薪作为决策基准——解决问题节省的成本低于时薪就忽略，外包成本低于时薪就外包。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p73@0-p73@66",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 73,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 73,
              "char_offset": 66
            }
          },
          "quote": "设定一个大胆的个人时薪，并严格执行。如果解决一个问题节省的成本低于时薪，那就忽略问题；如果外包一项任务的成本低于时薪，那就选择外包。",
          "role": "core_definition",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "active_attention:find_leverage_points",
      "item_id": "find_leverage_points",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p5@67-p5@124",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 67
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 5,
              "char_offset": 124
            }
          },
          "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
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
      "ref_id": "active_attention:ignore_status_seekers",
      "item_id": "ignore_status_seekers",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@0-p13@33",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 33
            }
          },
          "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
          "role": "core_definition",
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
      "ref_id": "active_attention:partner_selection_integrity_first",
      "item_id": "partner_selection_integrity_first",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "商业伙伴选择的价值排序：聪明+精力充沛是基本门槛，正直诚信才是决定性要素",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p25@0-p25@32",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 25,
              "char_offset": 32
            }
          },
          "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
          "role": "core_definition",
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
      "ref_id": "active_attention:expertise_play_vs_effort",
      "item_id": "expertise_play_vs_effort",
      "attention_tags": [
        "focus",
        "model"
      ],
      "statement": "专长累积的检验标准：过程对你像玩耍，对他人吃力——这个主观感受可以作为判断是否在追求真正兴趣的信号。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p37@0-p37@27",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 37,
              "char_offset": 27
            }
          },
          "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p94@0-p98@146:highlight:37",
      "reaction_id": "rx:Full_Content:src:c1:p94@0-p98@146:highlight:37",
      "type": "highlight",
      "thought": "这提供了一个关于技术价值的锐利时间窗口视角：科技在被广泛采用前才有超额回报，之后就变成基础设施。这个定义把\"科技投资\"从玄学变成一个可辨识的生命周期问题。",
      "emitted_at_source_span_id": "src:c1:p94@0-p98@146",
      "primary_source_ref": {
        "source_span_id": "src:c1:p98@45-p98@67",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 98,
            "char_offset": 45
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 98,
            "char_offset": 67
          }
        },
        "quote": "某种东西一旦得到广泛应用，它就不再是科技了。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "某种东西一旦得到广泛应用，它就不再是科技了。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p99@0-p99@193:highlight:38",
      "reaction_id": "rx:Full_Content:src:c1:p99@0-p99@193:highlight:38",
      "type": "highlight",
      "thought": "这个表述把「规模化」从商业术语变成了一种思维姿态——不是「如果成功了再考虑规模」，而是把规模本身作为设计目标。",
      "emitted_at_source_span_id": "src:c1:p99@0-p99@193",
      "primary_source_ref": {
        "source_span_id": "src:c1:p99@0-p99@65",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 99,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 99,
            "char_offset": 65
          }
        },
        "quote": "下一步是思考如何规模化，因为只提供一个产品或一项服务是远远不够的，必须提供成千上万个，甚至几十万、几百万、几十亿个，最好人手一个。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "下一步是思考如何规模化，因为只提供一个产品或一项服务是远远不够的，必须提供成千上万个，甚至几十万、几百万、几十亿个，最好人手一个。",
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
    "ref_id": "concept:capital_financing_prerequisites",
    "concept_key": "capital_financing_prerequisites",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p49@0-p49@39",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 49,
            "char_offset": 39
          }
        },
        "quote": "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:compound_returns_life",
    "concept_key": "compound_returns_life",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p23@7-p23@38",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 7
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 23,
            "char_offset": 38
          }
        },
        "quote": "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:dual_core_competencies",
    "concept_key": "dual_core_competencies",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p29@0-p29@20",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 29,
            "char_offset": 20
          }
        },
        "quote": "学会销售，学会构建，两技傍身，势不可当。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "学会销售，学会构建，两技傍身，势不可当。"
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
    "ref_id": "thread:original_pursuit_vs_wealth",
    "thread_key": "original_pursuit_vs_wealth",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p83@0-p83@40",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 83,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 83,
            "char_offset": 40
          }
        },
        "quote": "当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。",
        "role": "core_definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:wealth_as_derivative_question",
    "thread_key": "wealth_as_derivative_question",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p88@31-p88@68",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 88,
            "char_offset": 31
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 88,
            "char_offset": 68
          }
        },
        "quote": "并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？"
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
    "source_span_id": "src:c1:p5@67-p5@124",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 67
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 5,
        "char_offset": 124
      }
    },
    "quote": "我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@0-p13@33",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 33
      }
    },
    "quote": "无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p25@0-p25@32",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 25,
        "char_offset": 32
      }
    },
    "quote": "选择聪明过人、精力充沛的商业伙伴，但更重要的是，他们要正直诚信。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p37@0-p37@27",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 37,
        "char_offset": 27
      }
    },
    "quote": "累积专长的过程，对你而言就像玩耍，对他人来说则很吃力。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p67@0-p67@31",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 67,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 67,
        "char_offset": 31
      }
    },
    "quote": "学习微观经济学、博弈论、心理学、说服术、伦理学、数学和计算机。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p73@0-p73@66",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 73,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 73,
        "char_offset": 66
      }
    },
    "quote": "设定一个大胆的个人时薪，并严格执行。如果解决一个问题节省的成本低于时薪，那就忽略问题；如果外包一项任务的成本低于时薪，那就选择外包。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p75@0-p75@36",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 75,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 75,
        "char_offset": 36
      }
    },
    "quote": "工作时要拼尽全力，毫无保留。不过，共事的人和工作的内容比努力程度更重要。",
    "role": "core_definition",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p86@26-p86@102",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 86,
        "char_offset": 26
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 86,
        "char_offset": 102
      }
    },
    "quote": "“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。因此，这两个重点就可以概括上述所有的理念。",
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
- mainline_fidelity: `3`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `3`
- final overall MQ: `3.25`
- judge reason: The snapshot retains 6 active items and 3 concepts from the chapter's wealth-building body, all accurately sourced. However, it misses the chapter's central organizing frame: '把自己产品化' (productize yourself) — the self(unique+accountability) + productize(leverage+expertise) synthesis that unifies all principles. The wealth definition ('在你睡觉时仍能为你赚钱的资产') appears only in source_ref_digest as a passive reference, not as working memory. The three-part chapter structure (what wealth is, how to create it, how to scale) is not reflected in active organization. The snapshot shows good fidelity on individual items but the mainline structural signal — the chapter-level synthesis — is weakly retained in working memory.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[4]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/nawaer_baodian_private_zh__segment_1.md`.

## Scoring Interpretation

This section explains how the trace above becomes the Eval-1 scores for this window.

### Selective Legibility

- Formula used by the run report: `(exact_match + focused_hit) / note_case_count = (8 + 2) / 23 = 0.4348`.
- Incidental cover count `2` is visible support, not recall credit.
- Miss count `11` means the reaction timeline either did not produce a strict source-overlap candidate for the note target or the judge rejected the admitted candidate.
- Unlocatable reaction count `1` is diagnostic only and never becomes a match.

### Memory Quality

- Window MQ is the average of the five probe-time overall scores: 3.25, 3.5, 3.25, 5, 3.25 -> `3.65`.
- The probe state sections above show what the mechanism had available at scoring time; final runtime state is not substituted for probe-time evidence.

### Callback / FVI

- Reaction audit reviewed `40` visible reactions: `6` grounded, `4` weak, `1` FVI, `29` local-only.
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
