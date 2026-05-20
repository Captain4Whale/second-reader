# Eval-1 Playback Dossier: 悉达多

This playback page is a product-facing reading trace for human review. It replays the Eval-1 window in reading order, then explains how the four evaluation channels score that trace. It is not a new eval run, not a catalog update, not product-quality proof, and not Long Span formal authority.

## Window Verdict

- Lane A selective-legibility recall: `0.4000` over `20` note cases (`1` exact, `7` focused, `0` incidental, `12` miss).
- Lane B Memory Quality: `3.00` average over `5` semantic probes.
- Visible reaction audit: `211` reactions (`47` grounded callback, `25` weak callback, `0` FVI, `139` local-only).
- Reviewer stance: read the timeline first, then the scoring interpretation. The score is justified by the trace, not by the aggregate table alone.

## Evidence Map

- Dataset source window: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/xidaduo_private_zh__segment_1.md`
- Raw segment text: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/xidaduo_private_zh__segment_1.txt`
- Lane A run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo`
- Lane B run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo`
- Lane A note cases: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases`
- Lane B MQ rows: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl`
- Lane B reaction audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/reaction_audit_results.jsonl`
- Probe snapshots: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`
- Normalized eval bundle: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`

## Source Window And Chapter Coverage

- Covered chapters: `婆罗门之子, 沙门, 乔达摩, 觉醒, 第二部, 迦摩罗, 尘世间, 轮回, 在河边, 船夫, 儿子, 唵`
- Full reviewer-readable source window lives beside the dataset: `source_windows_readable/xidaduo_private_zh__segment_1.md`.
- Each reaction below includes its own source-span excerpt so the reviewer can stay in reading flow, then jump to the full source window when needed.

## Selective Legibility Note-Case Ledger

This ledger lists every dataset note target in the window. Matched note cases point to the reaction that appears later in the reading timeline; misses remain visible here so reviewer analysis is not biased toward successful reactions only.

### Note `e0001` — `exact_match`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001`
- target note:
```text
悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
```
- target source span(s):
  - `p143@0-55`: 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
- matched reaction in timeline: `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001.json`

### Note `e0002` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002`
- target note:
```text
佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
```
- target source span(s):
  - `p165@1-95`: 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
- matched reaction in timeline: `rx:Full_Content:src:c1:p164@68-p165@95:highlight:60`
- source-span relation: `note_contains_candidate`; coverage `0.5`
- judge/runner reason: The reaction's quoted span (the '影子' passage about Govinda) is a central component of the note, and the reaction's analysis of the shadow metaphor and Siddhartha's acceptance directly addresses key content in the note. However, the note also emphasizes the reciprocal exchange ('他劫掠了我，但他馈赠得更多' and '他所馈赠的，则是悉达多，是我的自我')—the gift side of the exchange—which the reaction does not engage with.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002.json`

### Note `e0003` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0003`
- target note:
```text
可我哪，我这个有意研读世界之书、自我存在之书的人，却预先爱上一个臆想的意义。
```
- target source span(s):
  - `p181@93-131`: 可我哪，我这个有意研读世界之书、自我存在之书的人，却预先爱上一个臆想的意义。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0003.json`

### Note `e0004` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004`
- target note:
```text
恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
```
- target source span(s):
  - `p274@42-120`: 恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
- matched reaction in timeline: `rx:Full_Content:src:c1:p270@0-p274@232:highlight:101`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction's quoted source span (char 14-120) contains the note's entire source span (char 42-120) and the reaction's commentary directly engages with the core philosophical content: the stone metaphor and its key phrases '不必费力' and '无需挣扎'. The reaction's focus on explaining how the stone analogy represents active focus (主动聚焦) rather than passive acceptance clearly centers on the note's essential meaning. This is not incidental coverage—the reaction genuinely interprets and expands upon the note's central concept.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004.json`

### Note `e0005` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0005`
- target note:
```text
而迦摩罗则教会他，不付出情欲就难收获情欲这一《爱经》的根本。
```
- target source span(s):
  - `p311@140-170`: 而迦摩罗则教会他，不付出情欲就难收获情欲这一《爱经》的根本。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0005.json`

### Note `e0006` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0006`
- target note:
```text
可事实上，时间和金钱已经蒙受损失。而我享受了几天美妙时光，学到了知识，心情愉快，我和他人均未因我的气恼和草率而受到伤害。
```
- target source span(s):
  - `p317@89-149`: 可事实上，时间和金钱已经蒙受损失。而我享受了几天美妙时光，学到了知识，心情愉快，我和他人均未因我的气恼和草率而受到伤害。
- matched reaction in timeline: `rx:Full_Content:src:c1:p315@217-p317@281:highlight:117`
- source-span relation: `note_contains_candidate`; coverage `0.7`
- judge/runner reason: The reaction's source span covers the core of the note (the gains: wonderful time, knowledge, good mood, no harm). Its analytical content directly engages with the note's central insight about a 'new value accounting' system contrasting quantifiable losses with unquantifiable gains. Though the quote misses the opening clause about losses, the reaction's interpretation of the note's essential argument is precise and focused.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0006.json`

### Note `e0007` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0007`
- target note:
```text
他给出建议，表示同情，慷慨解囊，他甚至故意被欺骗。就像当年他热衷于侍奉诸神和做沙门时一样，他全神贯注，激情饱满地和众人游戏着。
```
- target source span(s):
  - `p320@240-303`: 他给出建议，表示同情，慷慨解囊，他甚至故意被欺骗。就像当年他热衷于侍奉诸神和做沙门时一样，他全神贯注，激情饱满地和众人游戏着。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0007.json`

### Note `e0008` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008`
- target note:
```text
或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
```
- target source span(s):
  - `p330@1-74`: 或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
- matched reaction in timeline: `rx:Full_Content:src:c1:p326@0-p330@74:discern:123`
- source-span relation: `note_contains_candidate`; coverage `0.5479`
- judge/runner reason: 反应的引用范围（"我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。"）精准对应高亮文本的核心哲学判断，且反应对"将爱当作艺术经营"与爱的本质之间张力的分析直接服务于对这段对话的理解。虽然高亮文本末尾的"如孩童般的世人才会爱"未被引用，但反应抓住了这句话的核心矛盾，评价"技艺的完美可能恰恰是内在缺失的证明"是真正聚焦于该文本的重要思想内涵。
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008.json`

### Note `e0009` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0009`
- target note:
```text
为重新成为孩子，为从头再来，我必须变蠢、习恶、犯错。必须经历厌恶、失望、痛苦。
```
- target source span(s):
  - `p392@272-311`: 为重新成为孩子，为从头再来，我必须变蠢、习恶、犯错。必须经历厌恶、失望、痛苦。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0009.json`

### Note `e0010` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0010`
- target note:
```text
没有过去，没有未来。一切都是本质和当下。”
```
- target source span(s):
  - `p436@89-110`: 没有过去，没有未来。一切都是本质和当下。”
- matched reaction in timeline: `rx:Full_Content:src:c1:p432@0-p436@109:highlight:172`
- source-span relation: `partial_overlap`; coverage `0.9524`
- judge/runner reason: The reaction's quoted source span (char 65-109) contains the note's entire source span (char 89-110) and the reaction's interpretive content is directly focused on the note's core insight: the dissolution of linear time into '当下' (the present) and '本质' (essence). The extra context included in the quote ('悉达多的前世并非过去，死亡和重归梵天亦并非未来') serves to ground the interpretation in the broader philosophical context but does not dilute the reaction's focus on the note's central message. The 0.9524 coverage confirms the note is fully embedded within and central to the reaction's quoted span.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0010.json`

### Note `e0011` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0011`
- target note:
```text
心硬又傲慢的人会受很多苦，会迷路，会做错事，会担许多罪孽。
```
- target source span(s):
  - `p484@74-103`: 心硬又傲慢的人会受很多苦，会迷路，会做错事，会担许多罪孽。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0011.json`

### Note `e0012` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0012`
- target note:
```text
人独自行过生命，蒙受玷污，承担罪过，痛饮苦酒，寻觅出路。
```
- target source span(s):
  - `p490@161-189`: 人独自行过生命，蒙受玷污，承担罪过，痛饮苦酒，寻觅出路。
- matched reaction in timeline: `rx:Full_Content:src:c1:p488@0-p492@92:highlight:194`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction's source span contains the exact note text and extends slightly beyond it. The reaction's content is focused on interpreting '独自行过生命' as a structural concept rather than mere loneliness, and explicitly connects it to the book's themes of education, love, and good. The commentary directly engages with and elaborates on the note's philosophical content rather than merely quoting or tangentially referencing it.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0012.json`

### Note `e0013` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0013`
- target note:
```text
他从未忘形地热恋一个人。从未全然忘我地去为了爱做蠢事。
```
- target source span(s):
  - `p493@93-120`: 他从未忘形地热恋一个人。从未全然忘我地去为了爱做蠢事。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0013.json`

### Note `e0014` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0014`
- target note:
```text
可是自从儿子出现，他悉达多却成了完全的世人。苦恋着，在爱中迷失；因为爱，而成为愚人。
```
- target source span(s):
  - `p493@145-187`: 可是自从儿子出现，他悉达多却成了完全的世人。苦恋着，在爱中迷失；因为爱，而成为愚人。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0014.json`

### Note `e0015` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0015`
- target note:
```text
他忧伤地席地坐下，感到内心的一些东西正在死去。他感到虚无，看不到快乐，也没有目标。
```
- target source span(s):
  - `p509@49-90`: 他忧伤地席地坐下，感到内心的一些东西正在死去。他感到虚无，看不到快乐，也没有目标。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0015.json`

### Note `e0016` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0016`
- target note:
```text
他在他们的每种激情、每种作为中看到生命、生机，看到坚不可摧之物和梵天。他在他们盲目的忠诚、盲目的强悍和坚韧中看到可爱和可敬之处。
```
- target source span(s):
  - `p514@287-351`: 他在他们的每种激情、每种作为中看到生命、生机，看到坚不可摧之物和梵天。他在他们盲目的忠诚、盲目的强悍和坚韧中看到可爱和可敬之处。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0016.json`

### Note `e0017` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0017`
- target note:
```text
悉达多甚至怀疑自觉的价值被高估，或许它只是思想者的天真。思想者只是思想的孩童般的世人而已。
```
- target source span(s):
  - `p514@396-441`: 悉达多甚至怀疑自觉的价值被高估，或许它只是思想者的天真。思想者只是思想的孩童般的世人而已。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0017.json`

### Note `e0018` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0018`
- target note:
```text
就如同动物在必要时强劲决绝的作为，往往胜于人类。
```
- target source span(s):
  - `p514@469-493`: 就如同动物在必要时强劲决绝的作为，往往胜于人类。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0018.json`

### Note `e0019` — `miss`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0019`
- target note:
```text
他坦白最狼狈的事，无所顾忌地暴露伤口。他说他今天如何被灼痛击败，孩子气地逃过河，非进城不可，河水又如何嘲笑他。
```
- target source span(s):
  - `p521@71-126`: 他坦白最狼狈的事，无所顾忌地暴露伤口。他说他今天如何被灼痛击败，孩子气地逃过河，非进城不可，河水又如何嘲笑他。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0019.json`

### Note `e0020` — `focused_hit`

- note_case_id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0020`
- target note:
```text
每个人都奔向目标，被折磨，受苦难。
```
- target source span(s):
  - `p525@92-109`: 每个人都奔向目标，被折磨，受苦难。
- matched reaction in timeline: `rx:Full_Content:src:c1:p523@0-p525@139:discern:208`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction's source span contains the note's full text, and the reaction's analysis is specifically focused on the phrase '奔向目标' from the note, interpreting it as a structural pattern that unifies three generations, directly addressing the note's core idea that 'desire is torment and the goal is the prison itself.' The additional river imagery in the source span serves as supporting context, but the reaction's primary focus remains on the note's central content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0020.json`

## Reading Timeline: All Visible Reactions

Every visible reaction in this Eval-1 window is listed in reading order. Fields are conditional: callback/FVI details appear only when the audit found a callback claim; Selective Legibility details appear only when the reaction overlapped a dataset note target.

### Reaction 001 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p1@0-p3@277:highlight:1`
- source span: `src:c1:p3@16-p3@21`
- source span excerpt:
```text
年轻的鹰隼
```
- visible reaction:
```text
这个比喻出现在人物描写的起始处，鹰隼的形象隐含了即将振翅的冲动，与后文他必然的离去形成隐约呼应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 002 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p4@0-p7@259:highlight:2`
- source span: `src:c1:p7@206-p7@259`
- source span excerpt:
```text
他要追随他，当悉达多成了神，抵达无量光明的世界，他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子。
```
- visible reaction:
```text
这段话里的层层递进——从朋友到随从、仆人、侍卫，最后落到"影子"——将一种亲密关系逐步稀释成单向的依附。乔文达追求的不是同行，而是不离不弃的侍奉。这为后文悉达多的离去埋下了某种悲剧性的预设：他要去的地方，不是任何忠诚的影子能够跟进的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 003 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p4@0-p7@259:highlight:3`
- source span: `src:c1:p7@84-p7@152`
- source span excerpt:
```text
乔文达知道：悉达多不会成为卑劣的婆罗门，腐败的祭司，贪婪施咒的商贩，虚荣空洞的辩术士；他也不会成为邪恶奸诈的僧侣，信众中善良愚蠢的羔羊。
```
- visible reaction:
```text
这句话用否定句式列举了一整套堕落的类型——腐败的祭司、贪婪的商贩、虚荣的辩士、邪恶的僧侣、愚蠢的羔羊。乔文达对婆罗门世界的负面判断如此清晰，却仍然选择以"影子"的身份留在其中，而不是与悉达多一同离开。这种选择本身透着一种自甘边缘的味道。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 004 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p8@0-p9@194:discern:4`
- source span: `src:c1:p9@0-p9@27`
- source span excerpt:
```text
可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致。
```
- visible reaction:
```text
这一转折句用否定句式两次强调"无法"，把外部的圆满（所有人热爱他、对他兴致勃勃）与内部的空洞（他无法让自己喜悦）并置。三层递进的"热爱""喜悦""兴致勃勃"在先，但全部指向一个核心：他对自己无能为力。这种反差不是普通的"富而不乐"——它暗示着一种根本的错位：他拥有的东西不能触及他真正需要的东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 005 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p10@0-p10@583:discern:5`
- source span: `src:c1:p10@107-p10@156`
- source span excerpt:
```text
他充满渴望的精神容器仍未盛满。洗礼虽善，但那只是水，不能洗涤罪孽，满足焦渴的灵魂，抚慰畏惧的心灵。
```
- visible reaction:
```text
"不能洗涤罪孽，满足焦渴的灵魂"——这句把宗教仪式（水）的局限性彻底点明了。不是否定洗礼，而是指出它功能上的边界：它处理得了外在的仪式，但触及不了内在的焦渴和畏惧。这为悉达多后来离开婆罗门教义埋下了认识论上的伏笔：他不是因为怀疑而离开，而是因为发现仪式有其无法抵达的领域。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 006 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p12@0-p12@22:discern:6`
- source span: `src:c1:p12@0-p12@22`
- source span excerpt:
```text
这就是悉达多的想法，也是他的渴望，他的痛苦。
```
- visible reaction:
```text
三个平行名词构成一种存在状态的三位一体——不是递进，不是因果，而是并置：他的思想就是他的渴望，他的渴望就是他的痛苦。这种结构本身就在说：这不是阶段性情绪，而是他整个存在方式被定义的方式。这与前文"精神容器仍未盛满"构成因果链接——正因为容器永不盛满，想法才持续燃烧为渴望，渴望才结晶为痛苦。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 007 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p13@0-p13@125:discern:7`
- source span: `src:c1:p13@86-p13@125`
- source span excerpt:
```text
在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。
```
- visible reaction:
```text
这句话把焦渴从个人困境升格为存在性的普遍命运。"所有"——这个词把范围推到最大；"没有一人"——把可能性彻底否定。它在说：这不是悉达多的资质问题，而是这条道路本身的极限。圣贤和智者都失败了，说明问题不在于修行者的造诣，而在于知识与天国之间存在不可逾越的鸿沟。这与前文"经典本身无误"但"知识积累不能等于内在拥有"形成完整的逻辑闭合——既然所有智者都失败，知识本身就不是答案。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 008 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p13@0-p13@125:discern:8`
- source span: `src:c1:p13@54-p13@75`
- source span excerpt:
```text
时常，他感到天国近在咫尺，又无法完全够及。
```
- visible reaction:
```text
"近在咫尺，又无法完全够及"——这个悖论在此获得了结构性意义。它不再只是心理上的距离，而是知识与体验之间不可通约性的精确表达：经典告诉他天国在哪里，修行让他感到近，但文字和修行的合力始终差了最后一步。这与前文"知识积累不能等于内在拥有"形成直接呼应——即便把知识积累到极致，那种"够及"仍然是无法完成的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 009 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p16@0-p20@106:discern:9`
- source span: `src:c1:p20@48-p20@106`
- source span excerpt:
```text
他仍沉浸在冥想中，眼睛凝视着遥远的目标，舌尖轻抵齿间，似乎静止了呼吸。他坐着，潜神冥思着“唵”字，灵魂之剑直指大梵。
```
- visible reaction:
```text
"灵魂之剑"这个意象是这一段最强的视觉锚点。它把抽象的灵修目标（梵、大梵）落实为身体性的武器——冥想中的悉达多不是平和的，而是武装的。他的舌头、呼吸、目光全部被这个入定姿态所冻结和导向。这与乔文达完成沐浴、呼唤朋友"起身"的日常节奏形成尖锐的对比：一个人在仪式中过完这一天，另一个人已不在同一时间。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 010 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p16@0-p20@106:highlight:10`
- source span: `src:c1:p20@0-p20@48`
- source span excerpt:
```text
惯常打坐时间结束后，乔文达起身。夜幕降临，晚间沐浴的时辰到了。乔文达呼唤悉达多，悉达多并未应答。
```
- visible reaction:
```text
三件日常事件（打坐结束、夜幕降临、沐浴时辰）密集排列，构成强烈的常规感——而"悉达多并未应答"五个字，就把悉达多从这套常规中完全抽离。他已不在同一套时间里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 011 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p21@0-p25@45:highlight:11`
- source span: `src:c1:p21@72-p21@143`
- source span excerpt:
```text
他们是人类王国的异乡人，骨瘦如柴的胡狼。孤独、绝尘，与世界为敌。一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。
```
- visible reaction:
```text
这串密集的意象——胡狼、灼热、献身、肉体灭绝——不是旁观者的描写，而是悉达多灵魂的镜像。沙门的形象不是风景，是投射。他从这些异乡人身上看到了自己内心早已存在却始终找不到出口的东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 012 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p35@81:highlight:12`
- source span: `src:c1:p35@65-p35@81`
- source span excerpt:
```text
心中充满恼怒和不安，恐惧和痛苦。
```
- visible reaction:
```text
这四个词不是随意堆叠的——它们构成一个心理坠落序列：恼怒（对不理解之事的愤怒），不安（无法掌控的焦灼），恐惧（某种失去正在发生），痛苦（最终的承受）。父亲从窗口望出去，每一小时都在这个序列里下坠一层。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 013 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p35@81:highlight:13`
- source span: `src:c1:p35@16-p35@40`
- source span excerpt:
```text
透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。
```
- visible reaction:
```text
三个时间/光线状态——月光、星光、黑暗——叠合在同一个持续的画面上，构成一种蒙太奇效果：不管光线如何变化，悉达多始终在那里，姿态不变。父亲的世界在轮转，儿子的世界已经停止了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 014 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p36@0-p40@9:retrospect:14`
- source span: `src:c1:p36@10-p36@32`
- source span excerpt:
```text
他走出房间，看见伫立于眼前的少年高大而陌生。
```
- visible reaction:
```text
这六个字完成了物理距离向心理距离的最终跃迁。不是"长大了"，是"陌生了"——父亲在破晓的光线里第一次真正失去了他认识的那个孩子。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p34@0-p35@81:highlight:13"]}`
  - judge reason: Explicitly links to reaction_index 13 (highlight:13) using prior_link field; '陌生了' builds on the montage observation where the father watches the son's unchanging vigil.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 015 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p36@0-p40@9:highlight:15`
- source span: `src:c1:p38@0-p38@6`
- source span excerpt:
```text
“您知道。”
```
- visible reaction:
```text
两个字封死所有斡旋空间。不是防御性回避，而是拒绝参与这场对话——父亲需要谈判，悉达多已经不需要。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 016 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p41@0-p45@12:highlight:16`
- source span: `src:c1:p42@0-p42@7`
- source span excerpt:
```text
“我会疲惫。”
```
- visible reaction:
```text
五组对话中唯一主动承认脆弱的一句，与"我不会睡着"构成鲜明反差——他接受身体的局限，却拒绝精神的停歇。疲惫是肉体的，但睡着意味着交出清醒。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 017 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p41@0-p45@12:highlight:17`
- source span: `src:c1:p45@0-p45@12`
- source span excerpt:
```text
“你会死去的，悉达多。”
```
- visible reaction:
```text
最后一句没有回应，悬在空气里。这是所有测试中最重的一句，也是唯一一句被故意留白的。悉达多没有说"我会死去"，也没有说"我不会"——面对死亡，他选择让这句话自己落下来。父亲的话说到这里，对话已经没有必要再继续。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 018 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p46@0-p50@16:highlight:18`
- source span: `src:c1:p47@0-p47@19`
- source span excerpt:
```text
“你宁愿死去，也不愿服从你的父亲吗？”
```
- visible reaction:
```text
这个问题预设了一个框架：服从父亲是默认选项，死亡只是威胁砝码。但悉达多从第一句就打破了这种预设——"我会死去"是陈述事实，不是筹码。他从未在"死亡"和"服从"之间做选择，因为两者对他而言根本不在同一逻辑层面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 019 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p46@0-p50@16:highlight:19`
- source span: `src:c1:p50@0-p50@16`
- source span excerpt:
```text
“悉达多会做他父亲要求的事情。”
```
- visible reaction:
```text
最后一句是整场对话中最干净的收尾。它听起来像顺从，却没有一句真正承诺留下。"父亲要求的事情"是空白的——父亲从未明确说出他到底要求什么，而悉达多也没有替他说出来。对话到此终止，父亲已经没有问题可问了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 020 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p51@0-p52@11:highlight:20`
- source span: `src:c1:p51@45-p51@72`
- source span excerpt:
```text
父亲意识到，悉达多已不在他身边。他已离开家乡，离开他。
```
- visible reaction:
```text
时态是关键：不是"将要离开"，而是"已不在"——父亲在这一刻才真正完成认知，悉达多的离开在意识层面已经发生，虽然身体还停留在屋内。这是父亲对儿子离去的最精确记录。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 021 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p53@0-p57@11:highlight:21`
- source span: `src:c1:p55@0-p55@40`
- source span excerpt:
```text
破晓时分，当悉达多拖着僵硬的双腿离开尚在沉睡的城邑，一个蹲伏的身影从房舍间跃出。
```
- visible reaction:
```text
「蹲伏」二字把乔文达写成了一种夜间潜伏的动物式存在——他不是在门口等候，而是在房舍间的暗处等待破晓。这个词呼应了之前「影子」的定位，但没有用那个词，而是让身体姿态本身说话。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 022 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:22`
- source span: `src:c1:p66@3-p66@34`
- source span excerpt:
```text
Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。
```
- visible reaction:
```text
这里Brahman被明确标注为"宇宙自我"，与前文反复出现的"阿特曼（Atman）"构成对位——Atman指向内在的、个别的自我，Brahman指向宇宙的、至高的自我。两者同源而层次不同，解释了为何婆罗门知识无法填满那个容器：那是个人灵魂与宇宙本体之间的结构性距离，而非认知不足。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:atman_becomes_own"]}`
  - judge reason: Uses prior_link to 'concept:atman_becomes_own' - a concept thread that has been developed across visible earlier reading; correctly grounds the Brahman-Atman distinction in established conceptual framework.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 023 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:23`
- source span: `src:c1:p67@56-p67@111`
- source span excerpt:
```text
……这是自我。它不死，无畏，它是梵(Brahman)。这个梵，名为真实。……知道这样，他就能天天前往天国世界。
```
- visible reaction:
```text
这段引文是整部小说背后哲学框架的直接出处。自我=不死+无畏+梵+真实——悉达多离开婆罗门并非因为经典有误，而是因为知道"真实"与"抵达真实"之间隔着一条无法通过知识跨越的鸿沟。奥义书本身给出了答案，却无法保证学生能成为那个答案。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["thread:knowing_without_arriving_thread"]}`
  - judge reason: Links to 'thread:knowing_without_arriving_thread' via prior_link; this conceptual thread has been built across earlier visible reactions discussing why knowledge alone cannot achieve enlightenment.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 024 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p67@111-p71@37:highlight:24`
- source span: `src:c1:p71@0-p71@37`
- source span excerpt:
```text
当晚，他们追上苦行者，向三位枯瘦的沙门请求同行，并承诺顺从。他们被接纳了。
```
- visible reaction:
```text
从婆罗门之子到沙门，顺从作为准入条件——身份转换的句法极为简洁，两句话完成了一整个世界的跨越。前文"影子"式的乔文达此刻跟随着悉达多一起去顺从另一位导师，这条线索在悄悄收紧。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 025 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p72@0-p72@281:highlight:25`
- source span: `src:c1:p72@225-p72@281`
- source span excerpt:
```text
一切都是欺骗，都散发着恶臭，谎言的恶臭。一切欲望、幸福和优美皆为虚幻。一切都在腐朽。世界是苦涩的。生活即是折磨。
```
- visible reaction:
```text
这段六字排比是整段的精神顶点。从"欺骗"到"苦涩"到"折磨"，三层递进完成了一次彻底的世界否定。但这个否定恰恰是从婆罗门圆满跌落后的反向极端——焦渴越深，否定的力道越彻底。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 026 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p74@0-p77@228:highlight:26`
- source span: `src:c1:p76@193-p76@214`
- source span excerpt:
```text
他好似猎人，在新的渴望中瞄准摆脱轮回的出口
```
- visible reaction:
```text
这个比喻在讽刺的精确度上几乎刺眼：瞄准"摆脱轮回"这一动作本身即是一种新的渴望，而新的渴望正是轮回的燃料。猎人与猎物的关系在隐喻层发生了倒置。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 027 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p78@0-p81@77:highlight:27`
- source span: `src:c1:p81@6-p81@77`
- source span excerpt:
```text
我并不这么看，我的朋友。至今我在沙门处学到的东西，乔文达，我本可以更快更便捷地学到。在花街柳巷的酒馆里，我的朋友，在脚夫和赌徒处，我都能学到。
```
- visible reaction:
```text
"更快更便捷"这几个字不是反讽，而是认真声明——悉达多在用世俗的效率逻辑质疑苦行的神圣必要性。乔文达描绘的"圣人"前景，他没有接住，反而拆解了苦行本身的价值。这不是叛逆，是认识的转向。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 028 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p78@0-p81@77:highlight:28`
- source span: `src:c1:p80@0-p80@64`
- source span excerpt:
```text
乔文达答：“我们学了不少。我们依然在学。你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”
```
- visible reaction:
```text
乔文达的回答完整地停留在"累积成就"的逻辑里——学得多、学得快、将成为圣人。但悉达多接下来的质疑，恰恰针对的是这种累积本身的价值。两个人看似在讨论同一段经历，实际上已经不在同一个问题场域里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 029 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p81@77-p85@83:highlight:29`
- source span: `src:c1:p85@44-p85@83`
- source span excerpt:
```text
我仍似一个在子宫内的婴孩，距离开悟、解脱十分遥远。这我知道。乔文达，这我知道。
```
- visible reaction:
```text
"子宫内的婴孩"这个意象在前面已经出现过一次——那是对婆罗门圆满生活的绝望隐喻。现在悉达多把它用在修习之后：沙门之道也未能让他出生。这是双重否定：既否定世俗圆满，又否定出世苦行。他承认自己仍在原处。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 030 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p85@83-p89@14:highlight:30`
- source span: `src:c1:p87@6-p87@55`
- source span excerpt:
```text
我们学了很多，悉达多。许多还需修习。我们没有打转，我们在攀登，打转如同陀螺，我们却已升了几级台阶。
```
- visible reaction:
```text
乔文达的"攀登"与"打转如同陀螺"构成完整意象：轮回是打转，解脱是攀登。但悉达多紧接着问的是师父的年纪——这个问题直接指向：如果师父攀登了六十年还在这里，攀登和打转的区别在哪里？这个追问本身说明他并不接受乔文达给出的安慰。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 031 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p85@83-p89@14:highlight:31`
- source span: `src:c1:p88@0-p88@29`
- source span excerpt:
```text
悉达多问：“你认为我们景仰的师父，那位沙门长老多大年纪？”
```
- visible reaction:
```text
这个问题看似随意，实则锋利。它接续了前面"我仍似一个在子宫内的婴孩"的自我判断：用师父的年龄来间接质疑修习时间的投入产出比。六十年的攀登，尚未抵达——这与悉达多自认仍在子宫内的感受形成无声呼应。不是直接反驳，而是用一个数字让乔文达自己去想。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 032 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p90@0-p93@122:highlight:32`
- source span: `src:c1:p92@139-p92@176`
- source span excerpt:
```text
或许，乔文达，或许我去求教犀鸟或黑猩猩也同样受益，同样获得才智，同样奏效。
```
- visible reaction:
```text
这个类比不是戏谑，而是严肃的自我判断：沙门的教导与动物本能一样无效。悉达多用这种极端的等价来宣告他与这条道路的彻底决裂。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 033 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p93@122-p94@18:highlight:33`
- source span: `src:c1:p94@0-p94@18`
- source span excerpt:
```text
说罢，乔文达喃喃诵念奥义书中的诗行：
```
- visible reaction:
```text
从论证切换到诵念，乔文达用神圣文本回应理性挑战——这不是回应，而是转渡。当悉达多的问题无法在逻辑层面被回答时，乔文达诉诸经典的权威来维持对话的延续。"说罢"二字标明了这一转向的决然。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 034 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p95@0-p99@31:retrospect:34`
- source span: `src:c1:p99@0-p99@31`
- source span excerpt:
```text
悉达多沉默不语。他久久思索着乔文达的话，一字一句地思索他的话。
```
- visible reaction:
```text
这个"久久思索"与前文那句犀鸟黑猩猩的决绝嘲讽形成鲜明对照。沙门的修习他毫不犹豫地否定了，但乔文达引述奥义书时，他选择了沉默而非反驳——这沉默本身就是一种敬重，也是内心仍在寻找入口的信号。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p90@0-p93@122:highlight:32"], "note": "前一个反应记录了悉达多用犀鸟黑猩猩彻底否定沙门修习；这里他对经典文本却选择了沉默中的久久思索，而非嘲讽式拒绝——两种态度形成对比，暗示经典尚未被他划入\"无效\"之列。"}`
  - judge reason: Explicitly references reaction_index 32 (highlight:32) via prior_link with note explaining the contrast between Siddhartha's mockery of Sramana practice versus his silence contemplating sacred texts.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 035 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p100@0-p101@149:highlight:35`
- source span: `src:c1:p100@0-p100@49`
- source span excerpt:
```text
悉达多垂首伫立。是的，他想，还剩下什么？什么能彰显神圣？什么能留下来？什么能经受考验？他摇了摇头。
```
- visible reaction:
```text
三个"什么"构成的是一种存在性真空，而非修辞性排比——它在说：所有已知的路径（婆罗门仪式、沙门苦修、经典诵念）此刻都被悬置了，答案不在任何已有的框架内。这个真空是结构性的，不是情绪性的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 036 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p100@0-p101@149:retrospect:36`
- source span: `src:c1:p101@40-p101@75`
- source span excerpt:
```text
一个叫乔达摩的人现世了，他是世尊佛陀。他已战胜尘世疾苦，止息转生之轮。
```
- visible reaction:
```text
这正好是前文那句"在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国"的正面回应。乔达摩完成了所有先贤未能完成之事——不是从经典或修习中，而是从"现世"这一事件本身进入叙述。这使得追随他成为逻辑上最自然的下一步，但也因此成为悉达多必须面对的陷阱：他是要寻找自己的答案，还是接受一个现成的？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["thread:knowing_without_arriving_thread"]}`
  - judge reason: Links to 'thread:knowing_without_arriving_thread' via prior_link; directly connects Gotama's arrival to the earlier established thread about why all sages failed to reach the kingdom.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 037 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p102@0-p106@178:highlight:37`
- source span: `src:c1:p104@15-p104@70`
- source span excerpt:
```text
世界病入膏肓，生命不堪重负——可是看！这里涌出一眼清泉，此处回响天人召唤。满是抚慰，令人振奋，满是高贵的承诺！
```
- visible reaction:
```text
这个意象用瘟疫隐喻将佛陀的传闻置于绝望与希望的交叉点上。世界有病——这正好呼应前文悉达多发现所有已知道路都无效时的内在焦渴。但"涌出一眼清泉"也暗含危险：急于寻找出口的人，可能会不加分辨地拥抱第一个看起来像答案的东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 038 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p102@0-p106@178:highlight:38`
- source span: `src:c1:p106@89-p106@151`
- source span excerpt:
```text
真的，我胸中的痛苦让我不得透气，我暗自想：难道我，难道我们俩，悉达多和我，不该去亲身经历、亲耳听闻这位修得圆满的世尊宣法吗！
```
- visible reaction:
```text
乔文达用"痛苦"而非"渴望"来描述自己的动机——这与前文"每滴都带着巨大的希望"形成对照。痛苦是更急迫的驱力。它也将两人绑在一起：不是"我想"，而是"我们俩"。这推进了乔文达作为影子追随者的设定——他需要将悉达多拉进同一轨道，才能安全地追随。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 039 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p107@0-p111@87:discern:39`
- source span: `src:c1:p109@120-p109@142`
- source span excerpt:
```text
尽管我坚信，我们已品尝过这法义中最好的果实。
```
- visible reaction:
```text
这句话是整段的枢纽。悉达多说"我打算去聆听"，但紧接着就说"我已品尝过最好的果实"——这意味着他们不需要真正的教导，只需要确认。这是一种冷峻的了然：焦渴本身就是答案，而不是需要被教导才能解除的东西。这也暗示了悉达多将如何看待乔达摩：他不会接受一个现成的答案，但会参与这场对话。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 040 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p107@0-p111@87:highlight:40`
- source span: `src:c1:p109@13-p109@30`
- source span excerpt:
```text
他的笑声里一半是悲痛，一半是嘲讽。
```
- visible reaction:
```text
这个笑与前文"所有圣贤都没有抵达天国"形成呼应——当所有人都在寻求答案时，悉达多已经知道答案不在任何人的教导里。但这种知道不是解脱，而是带着悲伤和嘲讽的处境。他同情那些仍然相信答案存在的人，也嘲讽包括自己在内的这个追逐。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 041 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p115@0-p116@41:highlight:41`
- source span: `src:c1:p116@1-p116@14`
- source span excerpt:
```text
在水面行走并不是我的追求。
```
- visible reaction:
```text
这句话干脆到近乎冷酷。"并不"是否定，但比"不是"更主动——它暗示他曾被邀请，但他选择了拒绝。它将"能力"和"追求"分开：你能做到，但你不必以此为目的。这也是对乔文达那句"很快就能学会"的冷处理——学会又怎样？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 042 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p115@0-p116@41:discern:42`
- source span: `src:c1:p116@21-p116@41`
- source span excerpt:
```text
还是让那些沙门老朽为这些把戏沾沾自喜吧！
```
- visible reaction:
```text
"老朽"这个词暴露了悉达多的位置：他用这个词时，已经不在沙门之中了。他在外面看他们，带着一种超越之后的距离感。而"把戏"这个词又把沙门的技艺彻底贬低——不是法门，不是修炼，是把戏。这进一步推进了前面那句"并不是我的追求"：他不只是不追求，他根本就是蔑视。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 043 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p125@63-p129@24:discern:43`
- source span: `src:c1:p128@7-p128@46`
- source span excerpt:
```text
仿似神灵指点，他即刻认出他。他看见那位质朴无华的着僧衣者，手持钵盂，静默前行。
```
- visible reaction:
```text
"即刻认出"这个瞬间很重——前文悉达多一直在质疑所有导师、否定一切知识传授，说没有人真正抵达过天国。而现在，一个如此确定、几乎本能的"认出"发生了。"神灵指点"这个词把它推向一个无法用理性解释的维度。是悉达多终于找到了对的老师，还是他依然在投射自己的渴望？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 044 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p125@63-p129@24:highlight:44`
- source span: `src:c1:p128@21-p128@46`
- source span excerpt:
```text
他看见那位质朴无华的着僧衣者，手持钵盂，静默前行。
```
- visible reaction:
```text
"质朴无华"——这是佛陀在满园繁华中呈现的样子，与前文婆罗门世界的仪式辉煌、沙门世界的技艺把戏都不同。静默前行，是最低的姿态。但周围所有的人都在追随这个最低的姿态。这本身就构成一个问题：为什么最质朴的人吸引了最多的仰望？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 045 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p130@0-p131@191:discern:45`
- source span: `src:c1:p131@142-p131@191`
- source span excerpt:
```text
他无欲满足，无所模仿。在恒久不变的平静中，在永不凋零的光芒中，在不容进犯的和平中，他柔和地呼吸着。
```
- visible reaction:
```text
"无欲满足，无所模仿"——这句话把佛陀的本质点出来了。不是通过克制达到平静，不是通过修炼获得力量，而是根本上没有向外寻求、没有要模仿的对象。这与前面悉达多嗤笑沙门的"把戏"、否定一切知识传授构成微妙对照：也许真正的完美不是更高超的技艺，而是彻底放下对完美的追求？三个"在……中"的平行结构制造了一种庄严而不可动摇的完整感，与婴儿般的自然状态结合在一起——既是神性也是童真。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '与前面悉达多嗤笑沙门的把戏构成微妙对照' as thematic contrast, but this is general/partial without specific anchoring to earlier visible text.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 046 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p130@0-p131@191:highlight:46`
- source span: `src:c1:p131@65-p131@142`
- source span excerpt:
```text
他严格依照规范，同他的徒众着一致的僧衣，迈同样的步履。只是他的面庞，他的步态，他安然低垂的眼帘，宁和垂下的手臂，乃至他手上的每根指头都流露和平，彰显完善。
```
- visible reaction:
```text
形式上完全同侪，内在上完全超越——这个张力本身就是对"佛陀是谁"的回答：他的完美不在于他做了什么不同的事，而在于他做同一件事时的"如何"。这恰好解释了为何周围的人都在追随这个"最低的姿态"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 047 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p132@0-p134@178:highlight:47`
- source span: `src:c1:p134@8-p134@30`
- source span excerpt:
```text
他对法义全无好奇。他不相信法义能带给他新知。
```
- visible reaction:
```text
这个"不感兴趣"本身就是一个强烈的反应——它不是说"法义是错的"，而是说"我已经知道了，没意思"。但恰恰是这种对内容的不在乎，把注意力完全挤压到形式上：佛陀这个人本身成了唯一值得观察的东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 048 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p132@0-p134@178:retrospect:48`
- source span: `src:c1:p134@89-p134@125`
- source span excerpt:
```text
他看上去仿佛每个指关节处都写满法义，都在言说，在吐纳，在散发真理的光辉。
```
- visible reaction:
```text
身体变成经文。这是整部小说最集中的一个意象翻转：之前的精神容器无法盛满、知识与抵达之间有结构性断裂，现在"法"直接刻在肉身之上，而且是手指——最小、最具体、最物质性的身体部位。这个反转暗示：真正的法义或许不是一套可以转述的命题，而是活人身上的存在方式本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:atman_not_learnable_obstacle_is_practice", "thread:knowing_without_arriving_thread"]}`
  - judge reason: Prior_link to 'thread:knowing_without_arriving_thread' and 'concept:atman_not_learnable_obstacle_is_practice' with explicit contrast: body becoming scripture reverses the earlier 'spirit container never fills' metaphor. Clear and grounded.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 049 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p135@0-p139@42:retrospect:49`
- source span: `src:c1:p139@0-p139@42`
- source span excerpt:
```text
看哪，腼腆的乔文达也上前一步道：“我也愿皈依您及您的法义。”他祈求加入僧众并被接纳。
```
- visible reaction:
```text
这个"被接纳"和前文乔文达反复作为"影子"追随的结构形成呼应。他一直在看、在跟随，但从未正式进入。现在他不是作为朋友的随从，而是作为皈依者——这是从"影子"变成"弟子"的关键一步。前文说"他对法义全无好奇"，但皈依法义本身——这个矛盾或许暗示：他的皈依仍然首先是追随这个人，而非认同那些命题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p132@0-p134@178:highlight:47", "active_attention:govinda_shadow_devotion"]}`
  - judge reason: Prior_link explicitly references reaction:47 (highlight:47) and 'active_attention:govinda_shadow_devotion'. Links Govinda's acceptance to the 'shadow' theme with explicit textual grounding.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 050 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p135@0-p139@42:retrospect:50`
- source span: `src:c1:p137@45-p137@71`
- source span excerpt:
```text
他的声音明亮而安静地盘旋在听者上空，如光影，如星辰。
```
- visible reaction:
```text
"光影"与"星辰"——不是实在的物质，而是飘浮的、不可把握的、超越性的存在。这与前文"手指关节写满法义"构成另一个对比：法义既是具体到可见的，又同时是飘浮不可及的。这种双重性或许是全书对"法义本质"的持续追问。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p132@0-p134@178:retrospect:48"]}`
  - judge reason: Prior_link to reaction:48 (retrospect:48) with explicit comparison: '光影/星辰' versus '手指关节写满法义'. Clearly links current passage to earlier specific visible material.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 051 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p140@0-p144@25:highlight:51`
- source span: `src:c1:p141@39-p141@159`
- source span excerpt:
```text
“乔文达，我的朋友，你已迈出步子，你选择了这条路。哦，乔文达，你一直是我的朋友，一直紧随我。我时常问：会有那么一天，乔文达听凭自己的心声，独自迈步前行吗？你看，你现在成了男子汉，选择了自己的路。愿你始终跟随他，哦，我的朋友！愿你寻得解脱！”
```
- visible reaction:
```text
这里的转折极其重要："你一直是我的朋友，一直紧随我"，然后是"你现在成了男子汉，选择了自己的路"——这句话同时是祝福和放手。乔文达的追随从来不是"选择"，而是附属性质的跟随；此刻悉达多正是在说：你终于有了自己的步子，你不再是我的影子了。这与前文"影子"主题形成完整的呼应和收束。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '前文影子主题形成完整的呼应和收束' but without explicit prior_link reference. Theme-only connection, partial and unsupported by specific anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 052 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`
- source span: `src:c1:p143@0-p143@55`
- source span excerpt:
```text
悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
```
- visible reaction:
```text
"你并未理会我的祝愿"——这句话表面上是责备，实则是最后一次清晰的告白：我的祝愿已经说尽，我的路不在佛陀那里。两次"愿你"合在一起，既是友情的终点，也是道路的分野。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001` / note `xidaduo_private_zh_personal_notes__e0001` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p143@0-55` 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
    - target note: 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: Again references '影子' theme and '前文' without explicit prior_link. Theme-level connection without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 053 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p145@0-p148@87:discern:53`
- source span: `src:c1:p147@82-p147@114`
- source span excerpt:
```text
“不要再问了，乔文达！佛陀的法义非常之好，我怎么可能发现瑕疵？”
```
- visible reaction:
```text
这句话的核心不是否认法义，而是拒绝把自己离开的原因归结为"法义有问题"。悉达多否认瑕疵，不是为佛陀辩护，而是彻底切断乔文达的逻辑起点：你问我在法义里发现了什么——我什么都没发现，我只是没有在那里找到我的路。这是悉达多第一次如此清晰地将"法义的完美"与"自己的无法容身"并列说出，两件事不矛盾，但它们之间的距离正是悉达多的困境所在。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 054 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p145@0-p148@87:discern:54`
- source span: `src:c1:p148@48-p148@87`
- source span excerpt:
```text
这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。
```
- visible reaction:
```text
这个动作序列值得关注：出离→拥抱→加入。不是跟随悉达多，而是加入了佛陀的行列。乔文达在两人最终分别的时刻，选择了留在佛陀的道路上。这与前文"影子"主题形成新的对照：乔文达不再是悉达多的影子，他有了自己的光源——佛陀的法义和僧团。这或许是乔文达真正"成年"的时刻：不再是追随者，而是一个有了自己道路的人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '前文影子主题形成新的对照' without explicit prior_link. Theme-level observation without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 055 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p149@0-p152@15:discern:55`
- source span: `src:c1:p152@0-p152@15`
- source span excerpt:
```text
“随你的心意。”世尊谦逊地说。
```
- visible reaction:
```text
佛陀用"谦逊"而非"宽宏"或"慈悲"来形容自己——这个词在此语境中意味深长。佛陀不以权威挽留悉达多，不以法义的完美性来驳回他的疑虑，这种不占有、不执取听众的姿态本身便是一种无声的回应。悉达多正在离开，而佛陀连挽留的姿态都不摆，这或许正是他能给予的最深的尊重。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 056 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p153@0-p154@7:highlight:56`
- source span: `src:c1:p153@21-p153@45`
- source span excerpt:
```text
如若我不坦率地将我的思想奉告世尊，我便无法离去。
```
- visible reaction:
```text
这句话将即将说出的话从"可选"升格为"必要"。不是"我想说"而是"我必须说，否则走不了"——这为悉达多接下来对佛陀法义的核心质疑或请求设置了结构性强度。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 057 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p153@0-p154@7:retrospect:57`
- source span: `src:c1:p154@0-p154@7`
- source span excerpt:
```text
佛陀默默首肯。
```
- visible reaction:
```text
与前文"世尊谦逊地说"形成呼应：佛陀既不争辩法义，也不挽留人，只是接受。这与乔文达的影子式追随形成对照——佛陀自己的姿态恰恰是"不留"的姿态，悉达多正是在这种不占有的接受中得以说清自己的思想。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p149@0-p152@15:discern:55"]}`
  - judge reason: Prior_link to reaction:55 (discern:55) with explicit contrast: Buddha's '不挽留'姿态 enables Siddhartha to speak. Clear link to earlier visible material.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 058 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p155@0-p159@20:highlight:58`
- source span: `src:c1:p157@174-p157@258`
- source span excerpt:
```text
哦，世尊佛陀，您从未以言辞或法义宣讲您在证觉成道之际所发生的事！世尊佛陀的法义多教人诸善奉行，诸恶莫作。在明晰又可敬的法义中不包含世尊的历程，那个您独自超越众生的秘密。
```
- visible reaction:
```text
这里悉达多说出了他真正在意的东西：法义告诉人"做什么"，但佛陀证道那一刻究竟发生了什么，那个独自超越的秘密——法义没有说，也不可能说。这既是批评，也是对"亲身经验不可传递"这一命题的确认。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 059 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p160@0-p164@68:highlight:59`
- source span: `src:c1:p162@0-p162@39`
- source span excerpt:
```text
“你很聪明，哦，沙门。”世尊道，“你能言善道，我的朋友。要提防不要太过聪明！”
```
- visible reaction:
```text
佛陀面对悉达多那番关于"我会将法义当作我"的拒绝，没有辩驳、没有挽留，只回以一句警告。这句话的力量在于它的反身结构：恰恰是你用来证明自己立场的聪明，可能正是你需要警惕的东西——这不是攻击，而是某种洞察。佛陀在"不占有"的姿态上做到了彻底。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 060 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p164@68-p165@95:highlight:60`
- source span: `src:c1:p165@29-p165@76`
- source span excerpt:
```text
他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。
```
- visible reaction:
```text
乔文达的角色在这里被精确地镜像化：他"曾经是我的影子"，现在"是乔达摩的影子"。这个"影子"的替换说明他从未真正追随法义本身，而是追随一个人。悉达多把这句"劫掠"说出来，意味着他完全理解并接受了这个损失。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002` / note `xidaduo_private_zh_personal_notes__e0002` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p165@1-95` 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
    - target note: 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
    - source-span relation: `note_contains_candidate`; coverage `0.50`
    - judge/runner reason: The reaction's quoted span (the '影子' passage about Govinda) is a central component of the note, and the reaction's analysis of the shadow metaphor and Siddhartha's acceptance directly addresses key content in the note. However, the note also emphasizes the reciprocal exchange ('他劫掠了我，但他馈赠得更多' and '他所馈赠的，则是悉达多，是我的自我')—the gift side of the exchange—which the reaction does not engage with.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '影子' thematic replacement without explicit prior_link. Theme-level observation.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 061 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p164@68-p165@95:discern:61`
- source span: `src:c1:p165@76-p165@95`
- source span excerpt:
```text
而他所馈赠的，则是悉达多，是我的自我。
```
- visible reaction:
```text
这是整个段落的核心转折。"馈赠自我"——佛陀通过带走乔文达，通过那番关于"亲身经验不可传递"的辩论，通过不挽留的姿态，最终逼出了悉达多必须独自面对自我的命运。这与前文"精神容器的结构性饥饿"形成深层呼应：正是这个"被劫掠"的时刻，终于打破了那个永远无法被知识填满的循环——因为没有什么可以再向外求了。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002` / note `xidaduo_private_zh_personal_notes__e0002` / label `miss` / best `false` / recall-credit `false`
    - target span(s): `p165@1-95` 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
    - target note: 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
    - source-span relation: `note_contains_candidate`; coverage `0.20`
    - judge/runner reason: The reaction's quoted span covers only the final clause (20% overlap) of the highlighted note, capturing '馈赠自我' but missing the note's core grievance about losing his friend and being compared to Gautama's shadow. The reaction interprets the ending as a 'core turning point' but does not address the note's primary emphasis on the loss and the deeper thematic stakes of the shadow/robbery metaphor.
    - reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: References '前文精神容器的结构性饥饿' but no explicit prior_link. Theme-level connection without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 062 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p172@0-p174@146:retrospect:62`
- source span: `src:c1:p174@103-p174@146`
- source span excerpt:
```text
认识缘由乃是一种深思。通过这样的深思，情感升华为认知，变得牢靠；它盘踞内心，熠熠生辉。
```
- visible reaction:
```text
「深思」在这里不是积累，而是转化——情感通过深思被深探至底部，成为认知。与前文「精神容器无法填满」构成对照：知识是外部积累，此路不通；而深思是内部转化，让情感本身成为认识之源。这是方法论的彻底转向：从向外求转向向内潜。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:atman_not_learnable_obstacle_is_practice"]}`
  - judge reason: Prior_link to 'concept:atman_not_learnable_obstacle_is_practice' with explicit contrast: 深思 (internal transformation) versus 精神容器无法填满 (external accumulation). Clearly grounded.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 063 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p175@0-p179@141:retrospect:63`
- source span: `src:c1:p176@58-p176@126`
- source span excerpt:
```text
答案是‘我’。我要学的即是‘我’的意义及本质。‘我’，是我要摆脱、要制胜的东西。‘我’，却是我无法制胜，只能欺罔、逃遁，只能隐藏的东西。
```
- visible reaction:
```text
这里的悖论结构精确极了——"我"既是目标（要认识），又是障碍（要摆脱）。前文反复出现的精神容器饥饿，在"我"这个问题上达到了最深的层面：不是知识不够，不是法义不够，而是连那个被追问的主体本身都是陌生的。这不是认知问题，而是存在性的撕裂——他与自己的距离，比他与任何圣典的距离都要远。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:atman_not_learnable_obstacle_is_practice", "active_attention:spiritual_container_never_full"]}`
  - judge reason: Prior_link to 'concept:atman_not_learnable_obstacle_is_practice' and 'active_attention:spiritual_container_never_full' with explicit contrast: 知识是外部积累 vs 深思是内部转化. Clearly grounded.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 064 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p175@0-p179@141:discern:64`
- source span: `src:c1:p179@117-p179@141`
- source span excerpt:
```text
我要拜自己为师。我要认识自己，认识神秘的悉达多。
```
- visible reaction:
```text
这句话是整个单元的最终落脚点。从拜父亲为师、拜圣典为师、拜佛陀为师，到"拜自己为师"——这是一条彻底转向的路径。但"神秘的悉达多"这个说法同时承认了自我认知的不可能：他仍不知道自己是什么，仍在寻找的路上。这个宣言不是答案，而是新一轮寻找的开始。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 065 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p184@0-p184@311:highlight:65`
- source span: `src:c1:p184@115-p184@137`
- source span excerpt:
```text
如今，他只是苏醒的悉达多，再不是别的什么人。
```
- visible reaction:
```text
这句话道出了觉醒的代价——不是获得了什么，而是剥去了所有旧有身份之后赤裸的存在。不是否定，是清空。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 066 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p184@0-p184@311:highlight:66`
- source span: `src:c1:p184@285-p184@311`
- source span excerpt:
```text
可是他，悉达多，他属于哪里？和谁分享生活？说谁的话？
```
- visible reaction:
```text
三个问题构成孤独的精确诊断：从"我在哪里"到"我与谁同在"，最后到"我用什么语言"——归属感被逐层剥去，最后落到语言和存在的根底。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 067 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p185@0-p185@111:highlight:67`
- source span: `src:c1:p185@90-p185@111`
- source span excerpt:
```text
他再也不回家，再也不回父亲那里，再不回去。
```
- visible reaction:
```text
三个"再也不"构成一种不可逆的结构——不是"也许不"，不是"暂时不"，是结构性的永不回头。与前面那个"拜自己为师"的宣言合在一起，才完整：向内的认知转向，必须以向外的决绝出走为行动锚点。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 068 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p185@0-p185@111:highlight:68`
- source span: `src:c1:p185@25-p185@42`
- source span excerpt:
```text
此刻，悉达多比从前更自我，更坚实。
```
- visible reaction:
```text
这个"更自我"的悖论在此刻落定——不是拥有了什么而更完整，而是剥去了所有支撑才更"坚实"。这与前面"精神容器的结构性饥饿"形成一种反向呼应：当初是外在圆满而内在空洞，如今是外在丧失而内在充盈。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 069 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p189@0-p193@599:highlight:69`
- source span: `src:c1:p193@317-p193@346`
- source span excerpt:
```text
如若人能毫无希求，质朴而天真无邪地看待世界，世界何其隽美！
```
- visible reaction:
```text
这句话是整个翻转的凝缩——"毫无希求"四字点出了从求索到放手的转化，而"质朴而天真无邪"则不是幼稚，而是最深的觉醒后才能抵达的境界。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 070 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p189@0-p193@599:highlight:70`
- source span: `src:c1:p193@295-p193@317`
- source span excerpt:
```text
他不再问询本质，瞄准彼岸，他在世间寻找故乡。
```
- visible reaction:
```text
"寻找故乡"这个表达在此处格外有力——故乡不在彼岸，不在超越处，而在"世间"本身。这与前面"本质位于可见世界的彼岸"形成对位：曾经的彼岸成了此刻的此地。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: States '与前面本质位于可见世界的彼岸形成对位' but no explicit prior_link. Theme-level contrast without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 071 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p194@0-p194@59:highlight:71`
- source span: `src:c1:p194@21-p194@37`
- source span excerpt:
```text
他从不在场。而现在，他归属其中。
```
- visible reaction:
```text
这个"从不在场"是前面所有追寻阶段的总诊断——婆罗门的知识和仪式、沙门的苦行、佛陀的教义，他都在使用却从未真正"在此"。而"归属其中"与"在世间寻找故乡"（p193）形成完整闭合：故乡不是彼岸的某个地方，而是此刻的归属。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '精神容器的结构性饥饿' but no explicit prior_link reference. Theme-level connection without anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 072 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p194@0-p194@59:discern:72`
- source span: `src:c1:p194@37-p194@59`
- source span excerpt:
```text
流光魅影在他眼中闪耀，星辰月亮在他心中运行。
```
- visible reaction:
```text
这句话是内化的完成——世界不再是外在的幻象威胁，而是进入他的眼睛和心脏。这与早期"精神容器的结构性饥饿"形成彻底的反转：那个永远无法盛满的容器，此刻已与世界同频运行。流光魅影（光与影的游戏）这个表达在此处有双重含义——既是世界的本来面貌，也是他不再视之为幻象后的自在观照。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 073 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p195@0-p195@625:retrospect:73`
- source span: `src:c1:p195@124-p195@173`
- source span excerpt:
```text
佛陀的彻悟纪事才是无法言说、不可传授的珍宝——这恰恰是他现在要去经验的，他现在才刚刚开始去经验的。
```
- visible reaction:
```text
这解释了前面他对佛陀说的那句话的含义。当时他无法体会，现在他亲身去经验了——这不仅是回忆，更是一种确认：教义是路标，不是目的地。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p189@0-p193@599:highlight:70"]}`
  - judge reason: Prior_link to reaction:70 (highlight:70) with explicit connection: '教义是路标，不是目的地'. Clearly grounded to earlier visible material.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 074 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p195@0-p195@625:retrospect:74`
- source span: `src:c1:p195@534-p195@601`
- source span excerpt:
```text
他并非凭苦行、献祭、洗礼和祈祷悟道，也不是凭斋戒悟道，不是在睡梦中悟道。他听凭了这个声音。如此听凭内心的召唤而非听凭外在的命令是善的。
```
- visible reaction:
```text
这里完成了对所有修行方法的消解——不是它们无用，而是它们都不是根本。根本是那个声音，而这个声音在菩提树下响起时，乔达摩只是“听凭”了。这是行动哲学的核心：顺从内在而非服从外在权威或技术。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p194@0-p194@59:discern:72"]}`
  - judge reason: Prior_link to reaction:72 (discern:72) with explicit connection: '听凭' as following the inner voice. Clearly grounded to earlier visible material.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 075 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p196@0-p196@258:highlight:75`
- source span: `src:c1:p196@94-p196@143`
- source span excerpt:
```text
乔文达不见了，取而代之的是一个女人。一对丰满的乳房从女人的衣襟中袒露出来。悉达多在她怀里吸吮乳汁。
```
- visible reaction:
```text
这个变形是关键——乔文达消失，取而代之的是女人和乳汁。之前乔文达代表的是影子式的追随和依附的渴望；现在这个渴望没有消失，而是变形为对世界之乳的吸吮。不是背弃乔文达，而是将那种渴望转了向。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: References earlier '影子' theme and '甘愿做他的影子' but no explicit prior_link. Theme-level connection without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 076 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p196@0-p196@258:discern:76`
- source span: `src:c1:p196@155-p196@211`
- source span excerpt:
```text
它是男人和女人的味道，阳光和森林的味道，动物和花朵的味道；它是每种果实，每种欲望的味道；它让人销魂，让人陶醉昏厥
```
- visible reaction:
```text
这个枚举不是色情描写，是存在论宣言：这奶汁不是某一类事物，而是全部事物——所有的对立（男女、阳光森林、动物花朵）都在其中。"每种欲望"直接点出了这不是禁欲之路，而是全欲望的吸收和参与。"销魂、陶醉昏厥"是这条路的感官词汇，不是清明的超越，而是沉浸在滋味中。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Claims this is '不是色情描写' and links to earlier '每种欲望' but no explicit prior_link. Partial/under-supported connection.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 077 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p202@0-p204@110:discern:77`
- source span: `src:c1:p204@43-p204@109`
- source span excerpt:
```text
我在路上遇到的人都像乔文达。他们都心怀感激，尽管他们都有资格获得他人的感激。他们都谦卑、善意、恭顺，思虑甚少。他们都有一颗赤子之心。
```
- visible reaction:
```text
这个归纳有反转的力量：不是"追随我的人都像乔文达"，而是"我遇到的人都像乔文达"。悉达多不再是众人仰望的中心，而是行走中不断遇见自己的某个侧影。这与早期段落中乔文达"甘愿做他的影子"形成对位——现在悉达多把这条线推了出去：我所遇见的每一个人，都是乔文达式的存在，带着同样的渴望和赤子之心。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: References earlier '影子式的追随' but no explicit prior_link. Theme-level connection to Govinda imagery without grounded anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 078 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p205@0-p205@335:discern:78`
- source span: `src:c1:p205@275-p205@335`
- source span excerpt:
```text
此刻，梦境再次袭来，他朝妇人俯下身去，亲吻她乳房上褐色的乳头。抬起头时，他看见妇人焦渴地微笑着，满是企盼的双眼细若游丝。
```
- visible reaction:
```text
"梦境再次袭来"——这个"再次"将此刻与p196那个"乔文达变形为女人和乳汁"的梦境直接链接。但方向发生了决定性的翻转：之前是乔文达变成女人供他吸吮；现在是他向现实中的妇人俯下身去。梦不再是逃避现实的避风港，而是变成了现实的内在延伸——他不是"梦见"了女人，而是"通过"女人进入了梦。妇人的焦渴与他的焦渴在"细若游丝"中相互缠绕，前文的"永恒焦渴"在这里找到了具体的、身体的面孔。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Claims explicit link to p196 '乔文达变形为女人和乳汁的梦境' but no prior_link reference provided. Assertion without grounded support.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 079 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p206@0-p206@138:highlight:79`
- source span: `src:c1:p206@45-p206@105`
- source span excerpt:
```text
就在这一刻，他听见内心颤抖的声音说“不”。顿时，年轻妇人微笑的脸失去了全部魅力。她在他眼中不过是一只目光迷离的发情母兽。
```
- visible reaction:
```text
这个"不"字的效应极其迅速——不是延迟判断，是瞬间转化。渴望和厌恶之间没有过渡。但"发情母兽"这个措辞相当刺耳：是拒绝中的降格，还是内心状态的真实映照？此处与p196"每种欲望"的全接纳立场形成张力——那个说"不"的声音是从哪里来的？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions '与p196每种欲望的全接纳立场形成张力' but no explicit prior_link. Partial connection without anchor.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 080 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p207@0-p209@98:highlight:80`
- source span: `src:c1:p209@0-p209@72`
- source span excerpt:
```text
悉达多见她如此美丽，心中欢喜。轿子临近时，他深鞠一躬，接着抬头注视那张靓丽妩媚的脸。他凝视她高挑眉毛下聪慧的双眼，并嗅到一缕从未闻过的沁人香气。
```
- visible reaction:
```text
与p206"不"字的瞬间拒绝形成对照——这里没有厌恶，没有降格，只有欢喜、鞠躬和凝视。这是另一种面对美的方式：不是对抗，也不是沦陷，而是尊重地、完整地纳入眼中。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 081 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p207@0-p209@98:highlight:81`
- source span: `src:c1:p208@208-p208@248`
- source span excerpt:
```text
艳绿和金黄搭配的上衣中露出光洁修长的颈项。娴雅的手指纤纤柔荑，手腕上戴着宽金镯。
```
- visible reaction:
```text
这段描写带有强烈的中国传统仕女画质感——发髻、细眉、红唇、金镯、颈项。将佛陀故事中的场景用这种美学方式呈现，暗示悉达多此刻所接触的世界已是一个完全世俗化、审美化的世界。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 082 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p210@0-p214@189:highlight:82`
- source span: `src:c1:p214@153-p214@189`
- source span excerpt:
```text
他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。之后，他去河里沐浴。
```
- visible reaction:
```text
从讲述毗湿奴和拉克什米的故事（宗教知识成为社交工具），到刮胡理发敷油沐浴（身体被系统性地世俗化）——这一系列动作构成了一种净身式的转化仪式。沙门的标记正在被一一剥去。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 083 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p215@0-p215@147:highlight:83`
- source span: `src:c1:p215@60-p215@87`
- source span excerpt:
```text
请求仆从向林苑女主人禀告，有位青年婆罗门渴望与她交谈。
```
- visible reaction:
```text
他已离开婆罗门、已刮须理发完成世俗化改造，却在此刻以"青年婆罗门"自称叩门。这个身份宣称是策略性的——借助一个仍被世俗世界认可的头衔来敲门——还是内在残存的自我认知？值得观察。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 084 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p216@0-p220@44:highlight:84`
- source span: `src:c1:p219@105-p219@151`
- source span excerpt:
```text
你是让悉达多并未低垂眼帘而与之交谈的第一个女人。今后，如若我遇见漂亮女人，也不会再垂下眼帘。
```
- visible reaction:
```text
这句话同时完成了三层宣告：宣告身份（沙门之路已告别）、宣告态度转变（不再回避女人）、宣告未来立场（从此直视不垂眼）。沙门僧侣不能直视女人的戒律在这里被公开打破——不是悄悄逾越，而是在面对面时宣告给对方听。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 085 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p216@0-p220@44:highlight:85`
- source span: `src:c1:p220@0-p220@25`
- source span excerpt:
```text
迦摩罗微笑着。她一边玩弄手中的孔雀翎摇扇，一边问道
```
- visible reaction:
```text
这个"微笑着"的迦摩罗与上一段"艳绿和金黄"的仕女画意象形成连贯的感官在场。摇扇是又一个审美细节，暗示她以从容的姿态掌控着这场对话的节奏——是她在问"为什么来"，不是他在主导。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确回调reaction 81中'艳绿和金黄'的仕女画意象，建立连续性。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 086 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p220@44-p223@110:highlight:86`
- source span: `src:c1:p223@1-p223@110`
- source span excerpt:
```text
从来没有林中沙门来拜我为师！朋友。也从来没有围着破旧遮羞布、留着长发的沙门来过我这里！许多青年来拜访我，其中不乏婆罗门之子。他们可是个个穿华丽的衣裳、考究的鞋子，头发飘香，腰缠万贯。沙门，那些青年都是置备停当才来见我。
```
- visible reaction:
```text
两组"置备停当"的人：那些婆罗门之子带着华丽的衣裳、飘香的头发而来，是为了感官享受；而悉达多穿着同样的精心装扮而来，却是为了求学——两组人用了完全相同的"置备"，目的是镜像式的对立。他请求学习她"所熟稔的艺术"，这个措辞本身已经是一场优雅的反讽。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 087 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p223@110-p227@48:highlight:87`
- source span: `src:c1:p226@37-p226@81`
- source span excerpt:
```text
你的嘴唇仿似新鲜开裂的无花果，迦摩罗。而我的嘴唇也同样又红又嫩。你将验证，它们是多么般配
```
- visible reaction:
```text
嘴唇对嘴唇，"般配"这个词从求道者口中说出来有种奇怪的郑重感——他在把她拉入一个对等的框架里，仿佛这不仅仅是买卖，而是两个嘴唇之间的对等相遇。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 088 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p223@110-p227@48:discern:88`
- source span: `src:c1:p227@1-p227@48`
- source span excerpt:
```text
我为何要畏惧一个沙门，一个林中来的愚笨的沙门，一个从胡狼群中来，又根本不知女人为何物的沙门呢？
```
- visible reaction:
```text
"根本不知女人为何物"——这句话的杀伤力在于：不是说"你不懂女人"，而是说"你连女人的概念都没有"，直接否定了悉达多自称"更复杂学问"的那个自我定位，把他的全部姿态打回门外汉的原形。前文他说要向伽摩罗学习'所熟稔的艺术'，这里伽摩罗还以颜色：你不配说'学习'，因为你连学习的门槛都没摸到。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 089 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p227@48-p229@236:highlight:89`
- source span: `src:c1:p229@161-p229@206`
- source span excerpt:
```text
情爱可以乞得，可以购买，可以受馈，也可在陋巷觅得，却唯独不能强夺。你想出了一个错误的主意。
```
- visible reaction:
```text
"唯独"二字在这里有很强的收束力——前面四种获得方式（乞、买、受、觅）逐一列举，最后用"唯独不能"划出边界。这种句式把"强夺"从所有可能中彻底剔除，不是说它困难，而是说它从根本上被排除在爱的法则之外。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 090 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p229@236-p231@40:discern:90`
- source span: `src:c1:p231@12-p231@40`
- source span excerpt:
```text
谁会不愿给一个从荒林狼群中来，又贫穷无知的沙门一些指示？
```
- visible reaction:
```text
"荒林狼群"这个词从迦摩罗口中说出来有一种微妙的回声感——前面她说的是"胡狼群"，现在换成了"狼群"，语气相近但更重。更有意思的是"贫穷无知"：他刚才还在说"学习更复杂的学问"，她现在用"无知"二字轻轻还回去，既是调侃也是接纳。"谁会不愿"这个反问修辞在这里不是傲慢，而是一种俏皮的应允。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确回调reaction 11中出现的'胡狼'意象（狼群vs胡狼），建立跨段落的回声。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 091 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p231@40-p234@17:highlight:91`
- source span: `src:c1:p234@1-p234@16`
- source span excerpt:
```text
我会思考。我会等待。我会斋戒。
```
- visible reaction:
```text
三个"我会"在这里产生了奇特的并置效果——前文"你会什么哪"问的是谋生技能，悉达多的回答却是修习之道。沙门最珍贵的三种能力，在这个场景里恰好等于"无一技之长"的坦白；但他没有丝毫窘迫，仿佛这三者的分量并不在金钱逻辑之下。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 092 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p240@0-p243@9:discern:92`
- source span: `src:c1:p243@0-p243@9`
- source span excerpt:
```text
不禁俯身扪心示敬，
```
- visible reaction:
```text
"扪心示敬"是身体对神圣意象的本能反应，和前文"你会什么哪"时他坦白三样沙门能力（思考、等待、斋戒）构成一种无声的回声——他已经不再是沙门了，但那套训练留下的身体记忆仍在。迦摩罗用宗教故事换来一个沙门的理发师位置，而沙门在她面前用"扪心"回应莲花：两边都在某种默契中进行着身份转换的仪式。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 回调reaction 91和109中提到的'三样沙门能力'（思考、等待、斋戒），建立与分析91的呼应。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 093 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p244@0-p247@10:discern:93`
- source span: `src:c1:p247@0-p247@10`
- source span excerpt:
```text
献祭诸神固情深义重，
```
- visible reaction:
```text
这句判断有一个微妙的内在张力：它不是在说献祭有效，而是在说献祭的动机"情深义重"。这种措辞暗示青年对宗教行为的评价标准已经从"是否灵验"转向"是否真诚"——他在从一个实用性的沙门逻辑，转向某种更深层的内心尺度。前文他已经完成了用宗教故事换身份的操作，现在他独自思量时，关注的焦点从功能层面回到了情感层面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 094 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p250@0-p252@178:highlight:94`
- source span: `src:c1:p252@60-p252@95`
- source span excerpt:
```text
让他深深惊叹的是她在如何引导他；她在怎样聪慧地降服他，推却他，魅惑他。
```
- visible reaction:
```text
四个动词——引导、降服、推却、魅惑——形成一套完整的情爱战术。其中"降服"一词尤为刺目：它本是宗教修习中自我克制的用语，却在此刻被迦摩罗反向施之于曾经的沙门。悉达多曾以沙门身份追求对欲望的克服，如今他体验到的却是被欲望的化身所"降服"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 095 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p253@0-p257@24:highlight:95`
- source span: `src:c1:p256@0-p256@43`
- source span excerpt:
```text
“我会唱圣歌，”悉达多道，“但我不再吟唱。我会念咒语，但我不再念诵。我也学过写字——”
```
- visible reaction:
```text
三个"不再"和一个"学过"：宗教性技能是主动放弃的过去时，识字则是更早学会但从未在此语境动用的备用资源。迦摩罗感兴趣的不是他的灵魂修炼，而是他在人间流通的实际本事。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 096 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p253@0-p257@24:highlight:96`
- source span: `src:c1:p257@0-p257@24`
- source span excerpt:
```text
“等一下。”迦摩罗打断他，“你识字？也会写字？”
```
- visible reaction:
```text
打断本身即是认可：她突然意识到这个曾经的沙门掌握了一种可以转化为城中生存资本的技能。这与前文"需要很多钱财"形成直接的逻辑连接——识字和写字，在她的世界里，是可以换来金币的实际能力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 097 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p258@0-p261@45:retrospect:97`
- source span: `src:c1:p261@0-p261@45`
- source span excerpt:
```text
“我有客人。”迦摩罗道，“赶快离开，悉达多。记住，不要让任何人看见你在这里！明天我再见你。
```
- visible reaction:
```text
"不要让任何人看见你在这里"——这句话把悉达多此刻的身份钉死了。他不是客人，不是朋友，甚至不是情人候选人；他是一个需要被藏起来的、可用的资源。明天"再见"承诺了延续，却不承诺任何位置上的改变。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p250@0-p252@178:highlight:94"]}`
  - judge reason: prior_link明确指向reaction 94，承接'引导、降服、推却、魅惑'的分析，将身份钉死与四动词战术进行链接。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 098 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p261@45-p265@96:highlight:98`
- source span: `src:c1:p264@0-p264@44`
- source span excerpt:
```text
一股自豪感油然而生。他已不再是沙门，无需再去乞食。他将手中饭团扔给一条狗，自己并未进食。
```
- visible reaction:
```text
扔饭团给狗而不吃——这个动作比放弃沙门身份本身更有意味。他不是"没有食物可吃"，而是"不需要吃"。一种主动的拒绝，暗示他连最原始的饥饿感都要压制或超越，仿佛吃了这口饭就还是那个乞食的沙门。他需要证明自己已经彻底翻篇。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 099 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p261@45-p265@96:highlight:99`
- source span: `src:c1:p265@0-p265@96`
- source span excerpt:
```text
“尘世生活其实简单。”悉达多想，“没什么难的。难的是做辛劳的沙门，到头来只收获绝望。现在一切易如反掌，就像迦摩罗的接吻课。我需要衣裳和金钱，别无其他。实现这些又小又近的目标，不会让人寝食难安。
```
- visible reaction:
```text
"到头来只收获绝望"——这句话把沙门生涯总结为彻底的失败。这是事后诸葛亮式的重新叙事：把离开宗教道路合理化为"因为我发现它走不通"，而不是"因为我厌倦了"或"因为我想要别的东西"。前者显得更有洞察力，后者则显得更轻率。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 100 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p268@0-p269@39:discern:100`
- source span: `src:c1:p269@0-p269@39`
- source span excerpt:
```text
“你真幸运。”告别时她道，“一扇扇门为你打开。这是怎么回事？难道你施了法术？”
```
- visible reaction:
```text
"一扇扇门为你打开"——这是迦摩罗在解读悉达多此刻的处境：没钱、没身份、没住处，但一切都在为他让路。而"难道你施了法术"这句追问，实际上是在问他到底凭什么。她不知道的是，悉达多的"法术"就是他自己——他的平静、他的不慌、他敢于向任何人开口的自信。两天不吃东西也笑着感谢她，这份从容本身就成了他最大的资本。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 101 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p270@0-p274@232:highlight:101`
- source span: `src:c1:p274@14-p274@120`
- source span excerpt:
```text
如果你将一粒石子投入水中，石子会沿着最短的路径沉入水底。恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
```
- visible reaction:
```text
石子比喻的微妙之处在于"不必费力"——不是放弃努力，而是把努力消解在引力（目标）之中。但这和沙门修行的"无欲"并不完全相同：这里恰恰是因为有强烈目标，才产生了类似重力的向心力。他把宗教修行的被动接受，转化成了主动聚焦。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004` / note `xidaduo_private_zh_personal_notes__e0004` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p274@42-120` 恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
    - target note: 恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction's quoted source span (char 14-120) contains the note's entire source span (char 42-120) and the reaction's commentary directly engages with the core philosophical content: the stone metaphor and its key phrases '不必费力' and '无需挣扎'. The reaction's focus on explaining how the stone analogy represents active focus (主动聚焦) rather than passive acceptance clearly centers on the note's essential meaning. This is not incidental coverage—the reaction genuinely interprets and expands upon the note's central concept.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 102 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p270@0-p274@232:highlight:102`
- source span: `src:c1:p274@161-p274@231`
- source span excerpt:
```text
愚人们称其为魔法。愚人以为此乃魔鬼所为。其实，魔鬼无所作为，魔鬼并不存在。每个人都能施展法术。每个人都能实现目标，如果他会思考、等待、斋戒。
```
- visible reaction:
```text
这段话的双重性很突出：对"魔法"的祛魅同时也是对这种能力的肯定——不是魔鬼所为，因为魔鬼不存在；也不是少数人的特权，因为"每个人都能"。他用否定句式建立了一种平等主义的可能性宣言。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 103 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p275@0-p277@44:discern:103`
- source span: `src:c1:p276@21-p276@54`
- source span excerpt:
```text
也或许因为悉达多是个俊美的男子，女人们喜爱他的目光，他才好运连连。
```
- visible reaction:
```text
迦摩罗用"帅哥理论"轻轻解构了悉达多刚才那套沉水石子和"法术"的宏大叙事——你运气好，是因为你长得好看。这是一种亲昵的打趣，也是一种智识上的不服：她不打算完全接受他的精神框架。但注意她说的是"女人们"而不是"我"，把自己放在了"例外"的位置。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 104 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p281@0-p285@49:highlight:104`
- source span: `src:c1:p284@0-p284@38`
- source span excerpt:
```text
迦摩施瓦弥步入室内。他敏捷矫健，华发萧萧。一双眼睛精明谨慎，嘴唇流露出贪欲。
```
- visible reaction:
```text
商人的外貌肖像几乎是一个性格速写：精明、贪欲。这是文本中第一次如此不加修饰地使用"贪欲"这个词——之前描述人物时更多是内省的、精神的，这里突然转向了一种直接的、物质性的词汇。它为整个商业世界段落定了一个基调：这是一个以欲望为驱动的领域。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 105 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p281@0-p285@49:highlight:105`
- source span: `src:c1:p285@36-p285@49`
- source span excerpt:
```text
你这位婆罗门可是陷入困境？
```
- visible reaction:
```text
商人这个问题表面上是在探底，实际上预设了一个判断：婆罗门给商人做工，本身就是反常的。而"困境"这个词会回响在后续的阅读中——悉达多离开婆罗门教义的深层焦渴，是否正是他此刻踏入的这个"困境"的开端？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 106 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p285@49-p289@17:highlight:106`
- source span: `src:c1:p288@0-p288@50`
- source span excerpt:
```text
“我没有财产。”悉达多道，“如果你指这一点，我的确一无所有。但我志愿成为沙门，所以我并未陷入困境。”
```
- visible reaction:
```text
悉达多对"困境"的回应是一种精准的概念手术：商人预设了"一无所有必然是困境"，但他把"没有财产"和"陷入困境"切分开了——前者是事实陈述，后者是价值判断，而他的判断取决于他进入沙门是志愿而非被迫。这个区分很干净，也很沙门式。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 107 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p285@49-p289@17:highlight:107`
- source span: `src:c1:p289@0-p289@17`
- source span excerpt:
```text
“既然你一无所有，你靠什么生活？”
```
- visible reaction:
```text
这个问题比"困境"更锋利。困境可以是精神状态，但"靠什么生活"是铁打的物质问题。沙门式的回答会是什么？靠施舍、靠乞食？这是当时的社会结构，但商人显然在问的是一个更根本的问题：你这个"无"怎么在有"有"的世界里存活？这是一个尚未被回答的刀锋。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 108 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p290@0-p294@23:highlight:108`
- source span: `src:c1:p292@0-p292@17`
- source span excerpt:
```text
“看来是。商人也靠他人钱财为生。”
```
- visible reaction:
```text
这句回答是整段对话最干净的刀。商人设问的核心是：你凭什么生存？悉达多没有正面回答，而是把商人的处境和自己的生活叠放在同一个句式里——「看来是」，承认了指控；「商人也」把它普遍化，把商人的审判变成了对自己立场的支持。这个转移很利落。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 109 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p294@23-p298@17:discern:109`
- source span: `src:c1:p298@0-p298@17`
- source span excerpt:
```text
“我会思考。我会等待。我会斋戒。”
```
- visible reaction:
```text
这三个词没有一个属于商人的词汇系统。「武士力气、商人货物、教师学问」——这套分类本身就是一套交换经济的语言。而「思考、等待、斋戒」指向的是一种不需要交换对象的内在实践。这里藏着悉达多对商人问题的根本绕开：他不需要证明自己能付出什么，因为他的生存本身不以交换为前提。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 110 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p294@23-p298@17:highlight:110`
- source span: `src:c1:p297@0-p297@28`
- source span excerpt:
```text
“非常对。只是，你付出什么？你究竟学过什么？又会什么？”
```
- visible reaction:
```text
商人在这里把问题从「困境」推进到「价值」。前两次追问（困境和生存）已经被悉达多用「志愿」和「反射」化解，但这一句切到了更深的预设：每个人都必须「拥有」什么才能在这个世界里有价值。悉达多接下来给出的回答，正是对这个预设的结构性取消。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 111 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p299@0-p303@15:retrospect:111`
- source span: `src:c1:p302@9-p302@25`
- source span excerpt:
```text
对于没有食物的人，斋戒最为明智。
```
- visible reaction:
```text
这句话用斋戒的前提来解释斋戒的价值——放弃食物才是面对食物匮乏时最明智的策略。这是一个完整的悖论结构：正是"没有"才使得这种"放弃"成为可能，正是饥饿才使得藐视饥饿成为可能。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p294@23-p298@17:discern:109"]}`
  - judge reason: prior_link明确指向reaction 109，将斋戒价值的自解释与109对三样沙门能力的分析进行链接。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 112 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p299@0-p303@15:highlight:112`
- source span: `src:c1:p302@95-p302@114`
- source span excerpt:
```text
即便长时间被饥饿围困，他仍能藐视饥饿。
```
- visible reaction:
```text
"藐视"这个词的选择很精确——不是"战胜"，不是"忍耐"，是一种内在的轻蔑。精神修行的力量感在这里不是苦行的悲壮，而是一种对最根本生存压力也不屑一顾的高傲。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 113 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p308@0-p310@219:highlight:113`
- source span: `src:c1:p310@151-p310@172`
- source span excerpt:
```text
这迫使商人与他平起平坐，甚至对他高看一眼。
```
- visible reaction:
```text
不奴颜婢膝的静默迫使商人重新定价——这个反向逻辑在悉达多身上一再出现：他放弃争取什么，反而获得了什么。这是他策略性疏离的社会力学。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 114 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p308@0-p310@219:highlight:114`
- source span: `src:c1:p310@190-p310@219`
- source span excerpt:
```text
悉达多则视一切如游戏。他努力学习规则，内容他并不记挂于心。
```
- visible reaction:
```text
这是悉达多此刻人生状态的精准定义——他在学规则，但不对内容动心。学习本身成为目的，内容的空洞正是他的保护机制。这与前文知识积累不能等于内在拥有的逻辑一脉相承，只是场景从经典换成了生意。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 115 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p311@0-p315@217:highlight:115`
- source span: `src:c1:p315@0-p315@92`
- source span excerpt:
```text
他显然对生意心不在焉。一次，他去村落收购大批稻谷。当他抵达时，稻谷已全部卖给其他商人。尽管如此，悉达多仍在村落逗留数日。他宴请农民，送给农民的孩子铜币，参加一次结婚庆典，随后满意而归。
```
- visible reaction:
```text
这段让"视一切如游戏"落实为具体行动——出发时目标明确：收购稻谷；抵达时目标落空；但他没有切换回目标轨道，而是把整趟旅程改写成另一场收获。宴请、给铜币、参加婚礼——这些行为不是意外的填充，而是对"满意而归"的主动建构。他把失败的商业任务悄悄替换成了人的相遇。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 116 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p311@0-p315@217:discern:116`
- source span: `src:c1:p315@172-p315@217`
- source span excerpt:
```text
一位婆罗门成了我的朋友，孩子们在我膝上玩耍，农民带我参观他们的田地。没人把我当作一位商人。
```
- visible reaction:
```text
这最后一句把整个段落翻到了一个新的层次。"没人把我当作一位商人"——这不是被动的误解，而是他主动造成的结果。他来是为了做生意，但他的行为方式让"商人"这个身份从未成立。他全程在玩的是另一场游戏，一场以人的相遇而非利润为目的的游戏。迦摩施瓦弥说他"似乎总在生意上游戏"，没有说错，但那个"似乎"低估了真相——他不是在生意中游戏，他是用生意来掩护另一场游戏。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 117 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p315@217-p317@281:highlight:117`
- source span: `src:c1:p317@107-p317@149`
- source span excerpt:
```text
我享受了几天美妙时光，学到了知识，心情愉快，我和他人均未因我的气恼和草率而受到伤害。
```
- visible reaction:
```text
这不只是自我安慰，而是一套完整的新价值核算：损失的是可量化的（时间和金钱），获得的是不可量化的（美好、知识、好心情、不伤人）。他在用迦摩施瓦弥的语言为一种迦摩施瓦弥无法接受的账目做辩护。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0006` / note `xidaduo_private_zh_personal_notes__e0006` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p317@89-149` 可事实上，时间和金钱已经蒙受损失。而我享受了几天美妙时光，学到了知识，心情愉快，我和他人均未因我的气恼和草率而受到伤害。
    - target note: 可事实上，时间和金钱已经蒙受损失。而我享受了几天美妙时光，学到了知识，心情愉快，我和他人均未因我的气恼和草率而受到伤害。
    - source-span relation: `note_contains_candidate`; coverage `0.70`
    - judge/runner reason: The reaction's source span covers the core of the note (the gains: wonderful time, knowledge, good mood, no harm). Its analytical content directly engages with the note's central insight about a 'new value accounting' system contrasting quantifiable losses with unquantifiable gains. Though the quote misses the opening clause about losses, the reaction's interpretation of the note's essential argument is precise and focused.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0006.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 118 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p315@217-p317@281:highlight:118`
- source span: `src:c1:p317@149-p317@212`
- source span excerpt:
```text
如果今后我再去那里，或许去收购下季收成，或许因为其他生意，那里友好的人们必将由于我这次没有表现得急躁和闷闷不乐而热情地款待我。
```
- visible reaction:
```text
这句话把"没有急躁和闷闷不乐"这个态度本身变成了生产性资产——它在未来会产生商业回报。这是悉达多对迦摩施瓦弥最精准的一击：他用利润逻辑来证明"不追求利润"的合理性。这既是策略上的妥协，也是立场上最深的坚持。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 119 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p317@281-p321@257:highlight:119`
- source span: `src:c1:p321@108-p321@184`
- source span excerpt:
```text
如同一个人在玩球，他同他的生意以及周围的人玩耍。他冷眼旁观，寻得开心。而他的心，他存在的源泉却不在。那眼泉十分遥远，渐渐消失在视线之外，与他的生活无关。
```
- visible reaction:
```text
这与早期"以思想之网捕捉自我"的结构形成呼应——沙门时期他试图用思想捕捉，现在他用游戏捕捉，两种方式都让他心不在场。但这一次他有了自我意识，开始感到惊恐。内在之泉不在场，是他始终无法真正参与任何事物的根本原因。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确回调早期沙门时期'以思想之网捕捉自我'的意象，建立与修行阶段的跨章节连接。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 120 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p317@281-p321@257:highlight:120`
- source span: `src:c1:p321@202-p321@257`
- source span excerpt:
```text
他希望自己也能满腔热情，全心全意地参与到孩子气的日常行为中。真正地去生活、去劳作、去享乐，而不只是一位旁观者。
```
- visible reaction:
```text
"孩子气的日常行为"这个词值得注意：他用沙门的眼光鄙视世人的孩子气，却又渴望加入其中。这里的讽刺在于，他想要参与的，恰恰是他同时在蔑视的东西——但没有这层参与，就永远无法触及那眼遥远的泉。这是一个无法靠观望来解决的悖论。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 121 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p324@0-p325@240:highlight:121`
- source span: `src:c1:p325@10-p325@42`
- source span excerpt:
```text
聪明并非关键。迦摩施瓦弥聪明如我，但他心中没有这安静庇护的一隅。
```
- visible reaction:
```text
"安静庇护的一隅"——这个措辞很值得注意：它不是宏大的精神境界，而是心里的一个角落，一个不会被风动摇的所在。聪明可以到达任何地方，却不一定能在内心找到这个庇护。这把精神生活的关键从"认知高度"拉回到"存在质地"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 122 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p324@0-p325@240:highlight:122`
- source span: `src:c1:p325@58-p325@137`
- source span excerpt:
```text
大多数人，迦摩罗，仿佛一片落叶，在空中翻滚、飘摇，最后踉跄着归于尘土。有的人，极少数，如同天际之星，沿着固定的轨迹运行。没有风能动摇他，他内心自有律法和轨道。
```
- visible reaction:
```text
落叶与星辰的对置在这里落定。但悉达多紧接着指向乔达摩时抛出了一个悖论：乔达摩是完美典范，而他最忠实的追随者在他看来仍是落叶。拥有最高明的导师，并不等于拥有自己的内在律法——这与前文"知识拥有不能等于阿特曼拥有"构成深层呼应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 123 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p326@0-p330@74:discern:123`
- source span: `src:c1:p330@15-p330@55`
- source span excerpt:
```text
我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。
```
- visible reaction:
```text
这个"我就像你"的回应构成镜像确认——他不是在辩解"我并非不爱"，而是在说"你我同类"。这对迦摩罗是一个意外，因为她期待的是否认，而不是联盟。将爱当作艺术经营意味着爱是刻意为之的、有技术的、可教授的——但正是这种性质本身否定了爱的本质。这与前文"聪明并非关键"形成深层呼应：技艺的完美可能恰恰是内在缺失的证明。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008` / note `xidaduo_private_zh_personal_notes__e0008` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p330@1-74` 或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
    - target note: 或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
    - source-span relation: `note_contains_candidate`; coverage `0.55`
    - judge/runner reason: 反应的引用范围（"我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。"）精准对应高亮文本的核心哲学判断，且反应对"将爱当作艺术经营"与爱的本质之间张力的分析直接服务于对这段对话的理解。虽然高亮文本末尾的"如孩童般的世人才会爱"未被引用，但反应抓住了这句话的核心矛盾，评价"技艺的完美可能恰恰是内在缺失的证明"是真正聚焦于该文本的重要思想内涵。
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 124 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p326@0-p330@74:retrospect:124`
- source span: `src:c1:p330@55-p330@74`
- source span excerpt:
```text
如孩童般的世人才会爱。这是他们的秘密。
```
- visible reaction:
```text
"这是他们的秘密"这个说法值得注意：世人像孩童般地爱，而这是秘密——意味着无法被这类人（沙门、艺术经营者）理解和进入的状态。但同时"孩童般"也是前面"孩子气的日常行为"的进一步深化：世人的爱在悉达多看来既是羡慕的对象（想要参与孩子气的日常），也是需要超越的低层次状态。这种复杂的双重态度指向悉达多此时仍未完成的整合。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008` / note `xidaduo_private_zh_personal_notes__e0008` / label `focused_hit` / best `false` / recall-credit `false`
    - target span(s): `p330@1-74` 或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
    - target note: 或许是。”悉达多疲惫地说，“我就像你。你也谁都不爱——否则你怎会将爱当作艺术经营？像你我这类人大概都不会爱。如孩童般的世人才会爱。这是他们的秘密。
    - source-span relation: `note_contains_candidate`; coverage `0.26`
    - judge/runner reason: The reaction's source span (char 55-74) covers the key interpretive core of the note—"如孩童般的世人才会爱。这是他们的秘密"—and the reaction's analysis directly engages with this passage's significance: the notion of "secret," the double attitude toward children's love, and what this reveals about Siddhartha's incomplete integration. The interpretation builds specifically from this covered text rather than using it as incidental context.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0008.json`
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p317@281-p321@257:highlight:120"]}`
  - judge reason: Content contains ref_ids pointing to reaction:rx:Full_Content:src:c1:p317@281-p321@257:highlight:120 ('孩子气的日常行为'), but native_surfaced_evidence shows prior_link: null—the surface evidence does not support this linkage.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 125 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p330@74-p333@120:retrospect:125`
- source span: `src:c1:p333@104-p333@120`
- source span excerpt:
```text
他和孩童般的世人间彼此依旧陌生。
```
- visible reaction:
```text
这句话将前面迦摩罗所说的"如孩童般的世人才会爱"落定为一个结构性的隔阂状态——不是因为他排斥世人，而是因为他无法进入那种孩童般的爱。陌生是双向的：他不属于尘世，尘世也不属于他。这是一个没有归属的中间状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p326@0-p330@74:retrospect:124"]}`
  - judge reason: Content explicitly chains to p326@0-p330@74:retrospect:124 via ref_ids, but native_surfaced_evidence shows prior_link: null—the surface evidence layer does not carry this forward.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 126 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p330@74-p333@120:highlight:126`
- source span: `src:c1:p333@83-p333@104`
- source span excerpt:
```text
指引他生活的一直是思考、等待和斋戒的技艺。
```
- visible reaction:
```text
这是沙门三学的完整表述在尘世经历后的再次确认。经历了财富淫乐权力之后，真正指引他的仍是这些技艺——感官苏醒不等于灵魂转向，尘世的色欲之娱是外在流过，内在的修行秩序丝毫未动。迦摩罗看穿这一点，说明这个判断是准确的结构观察而非批评。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 127 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p334@0-p337@179:highlight:127`
- source span: `src:c1:p335@277-p335@327`
- source span excerpt:
```text
如同濒死的树干因潮气侵袭、注满而腐朽，世俗和惰性侵入并充满悉达多的灵魂。它不再轻盈，反而疲惫、麻痹。
```
- visible reaction:
```text
这个意象反转了沙门修行的方向：不是通过苦行耗尽世俗，而是世俗反过来"注满"了灵魂——如同水浸透枯木。这是一个危险的倒置：原本用来排空的东西，现在被反向填满了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 128 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p334@0-p337@179:retrospect:128`
- source span: `src:c1:p336@266-p336@402`
- source span excerpt:
```text
他羡慕他们拥有，他却欠缺的对个人生活的重视，羡慕他们强烈的快乐和恐惧，羡慕他们为不安又甜蜜的幸福感而不断坠入爱河，羡慕他们不懈地爱自己、爱女人、爱他们的孩子、爱名望金钱，羡慕他们热衷于诸多盘算和祈盼。他无法效仿这孩童般的快乐和愚蠢。他学会的，恰是他最难接受、最蔑视的东西。
```
- visible reaction:
```text
这段"羡慕"清单是悉达多内心真实的全景式暴露：他真正欠缺的不是知识或修行能力，而是"对个人生活的重视"和"孩童般的愚蠢"——这是他早期作为沙门和婆罗门时所蔑视的东西，现在成了他无法企及的彼岸。前文迦摩罗说他"羡慕"世人，这里给出了羡慕的具体内容。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p326@0-p330@74:retrospect:124", "reaction:rx:Full_Content:src:c1:p330@74-p333@120:retrospect:125"]}`
  - judge reason: Content references two earlier reactions (124 and 125) to construct the envy list, but native_surfaced_evidence prior_link is null—the surface evidence does not validate this chain.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 129 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p334@0-p337@179:highlight:129`
- source span: `src:c1:p337@145-p337@179`
- source span excerpt:
```text
他只意识到内心曾觉醒的清悦笃定之音，曾不断指引他的声音，已悄然缄默。
```
- visible reaction:
```text
"缄默"一词比"微弱"更彻底。前面段落说那声音"遥远而微弱地低语着"，现在连低语都停止了。这是一个结构性的断裂点：悉达多失去了最后的声音锚点，没有任何东西在内指引他了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 130 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p339@0-p343@82:highlight:130`
- source span: `src:c1:p340@60-p340@79`
- source span excerpt:
```text
悉达多从未如此明白，性和死是如此相近。
```
- visible reaction:
```text
这个"如此明白"不是推理出来的结论，而是性爱场景中身体性的觉察——"流着泪亲他、咬他，仿佛要从虚幻短促的快感中榨取最后一滴甘露"，在这种绝望的缠绵中，死的最近邻不是敌人，而是高潮。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 131 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p339@0-p343@82:highlight:131`
- source span: `src:c1:p343@63-p343@82`
- source span excerpt:
```text
他孤单伫立，空洞得如同岸边遇难的破船。
```
- visible reaction:
```text
"遇难"而非"搁浅"——破船不是停在岸上，而是被灾难打到岸边的，暗示暴力、无力、被遗弃的综合意象，比单薄的"空洞"更有重量。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 132 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p344@0-p345@51:retrospect:132`
- source span: `src:c1:p344@288-p344@373`
- source span excerpt:
```text
“继续！继续！这是你的使命！”这声音召唤他，在他离开家乡，成为沙门时；在他离开沙门，走向世尊佛陀时；在他离开世尊佛陀，踏入无常时。他已多久没听见这声音？已有多久毫无精进？
```
- visible reaction:
```text
这个"已有多久毫无精进"与前文"内心声音已悄然缄默"构成递进：缄默是状态，无精进是后果。两条路——离开婆罗门、离开佛陀——都曾被这声音召唤，现在声音彻底消失了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p334@0-p337@179:highlight:129"]}`
  - judge reason: Content explicitly references reaction:rx:Full_Content:src:c1:p334@0-p337@179:highlight:129 ('内心声音已悄然缄默'), but native_surfaced_evidence prior_link is null—the surface does not carry this linkage.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 133 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p344@0-p345@51:highlight:133`
- source span: `src:c1:p344@595-p344@641`
- source span excerpt:
```text
这游戏叫做轮回，一种孩童游戏，一种或许可爱的游戏。一次，两次，十次——难道要不停地游戏下去？
```
- visible reaction:
```text
"或许可爱的"这个限定词在此刻产生了奇异的消解力量——他用"可爱"而非"恐怖"来形容轮回，恰恰因为他已经看穿它，不需要恐惧了。后面"游戏业已终结"就是这个"看穿"的结果。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 134 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p346@0-p347@87:highlight:134`
- source span: `src:c1:p347@0-p347@19`
- source span excerpt:
```text
他与这些做了了断。它们已在他心中死去。
```
- visible reaction:
```text
"在心中死去"——不是等到起身离开才算告别，内在的断裂已经完成，身体的起身只是确认这个业已存在的事实。这与前面那个"我竟拥有一棵芒果树"构成了完整的精神弧线：先是清醒地看见拥有的荒诞，然后内在先行死去，最后起身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 135 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p346@0-p347@87:highlight:135`
- source span: `src:c1:p346@106-p346@130`
- source span excerpt:
```text
这是真实的，必要的吗？难道这不是一场愚蠢的游戏？
```
- visible reaction:
```text
连接前文"这游戏叫做轮回"的"游戏"——这里他用来质问自己拥有芒果树和花园这件事，同样是游戏。而且是更基础的、在他走入红尘之前的那层游戏：把世界当真，把拥有当真。轮回是一个游戏，这个"拥有"是嵌套在轮回里的更小的游戏。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 136 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p348@0-p349@93:retrospect:136`
- source span: `src:c1:p348@112-p348@146`
- source span excerpt:
```text
她在失却的痛苦中欣喜，她能最后一次把他紧贴胸口，再一次彻底被他征服。
```
- visible reaction:
```text
"失却的痛苦中欣喜"——这里不是矛盾，而是清醒。她知道那是最后一次，所以每一个动作同时是告别和彻底。痛苦和欣喜并行，因为两个都是真的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p344@0-p345@51:highlight:133"]}`
  - judge reason: Content references reaction:rx:Full_Content:src:c1:p344@0-p345@51:highlight:133 ('游戏叫做轮回') to frame Kamaladevi's choice to keep playing, but native_surfaced_evidence prior_link is null.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 137 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p348@0-p349@93:retrospect:137`
- source span: `src:c1:p349@70-p349@93`
- source span excerpt:
```text
不久后，她发现同悉达多最后的交欢令她怀了身孕。
```
- visible reaction:
```text
前文"这游戏叫做轮回"的"游戏"在此处发生了回响：迦摩罗继续这场游戏——她选择留下这个孩子，承担代价，而非切断联系。这与悉达多"游戏业已终结"的离去形成对照的弧线：他走了，她选择继续留在这个游戏里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p344@0-p345@51:highlight:133"]}`
  - judge reason: Again references the '游戏' from reaction 133 to contrast Siddhartha's departure with Kamaladevi's continuation—surface evidence does not support this link.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 138 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p350@0-p352@142:highlight:138`
- source span: `src:c1:p352@54-p352@73`
- source span excerpt:
```text
他梦中的知更鸟死了。他心中的鸟也死了。
```
- visible reaction:
```text
两只鸟的死去对应着前文离开婆罗门时的"内在焦渴"和离开沙门时的"知更鸟"意象——但这一次不是转移，而是彻底熄灭。这个"鸟"在他历尽一切之后，现在彻底死了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 139 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p350@0-p352@142:highlight:139`
- source span: `src:c1:p352@123-p352@142`
- source span excerpt:
```text
世上再没什么能诱惑他，愉悦他，安抚他。
```
- visible reaction:
```text
这不是超脱，是清空。两个"彻底"（腻烦、痛苦）之后，这个否定句完成了对悉达多所有可能性的关闭——只有在这之后，某些新的东西才可能有入口。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 140 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p353@0-p353@142:highlight:140`
- source span: `src:c1:p353@129-p353@142`
- source span excerpt:
```text
这轮回不是耗尽和桎梏了他？
```
- visible reaction:
```text
"耗尽和桎梏"这两个词的并置形成了一对互补的锁链——耗尽是被榨干了，桎梏是被捆住了。他不仅空了，而且无路可逃。这与前文"知更鸟死了"的意象形成闭合：不是某一种欲望没被满足，而是所有的路都已走尽，鸟彻底死了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 141 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p353@0-p353@142:discern:141`
- source span: `src:c1:p353@83-p353@100`
- source span excerpt:
```text
还有哪一隅灵魂的荒蛮之地他没驻足？
```
- visible reaction:
```text
"荒蛮之地"这个词很重——不是说他去过好的地方或坏的地方，而是说他已经走到了灵魂中那些未被触及过的、最偏僻的角落。这意味着他已经不只是堕落，而是将堕落本身推进到了极致。前文迦摩罗怀孕的细节在这里得到了回应：连生命本身的延续（孩子）都被卷入了这场轮回。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 142 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p359@0-p360@48:highlight:142`
- source span: `src:c1:p360@0-p360@24`
- source span excerpt:
```text
可这只是刹那，是一道闪电。悉达多跌落在椰子树下。
```
- visible reaction:
```text
"只是刹那"——这个"只是"把刚才那一瞬的灵性瞥见彻底按灭了。它不是失败的觉醒，而是连觉醒的力气都不够的一次短路。这与前文那个"耗尽和桎梏"构成直接的时间顺序：耗尽之后，连闪电都是透支的结果，不是救赎。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 143 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p359@0-p360@48:discern:143`
- source span: `src:c1:p360@24-p360@48`
- source span excerpt:
```text
他疲倦地仰面朝天，念着“唵”，头枕树根沉沉睡去。
```
- visible reaction:
```text
"念着'唵'"和前文他不断自语"唵"形成呼应——这次不是狂喜中的发现，而是疲惫中勉力维持的姿势。他用诵念替代了清醒，用睡去替代了彻悟。"头枕树根"这个细节非常具体、非常身体性：不是倒在床上，而是倒在树根旁。这与他在婆罗门时期"充满渴望的精神容器"构成反向镜像——此刻，容器已经空了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 144 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p361@0-p361@267:highlight:144`
- source span: `src:c1:p361@177-p361@201`
- source span excerpt:
```text
在神圣的“唵”字脱口而出时复活、苏醒，环顾世界。
```
- visible reaction:
```text
"复活"这个词把前面的赴死和此刻的苏醒直接缝在一起——那个让他宁愿赴死的'唵'，也是把他重新唤醒的声音。这不是偶然而是递归：同样的触发器，既是坠落的原因，也是回升的机制。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 145 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p361@0-p361@267:discern:145`
- source span: `src:c1:p361@213-p361@267`
- source span excerpt:
```text
睡眠于他不过是一声深意又专注的“唵”，一次“唵”的思考，一次隐匿又全然抵达的“唵”——那无名之地，圆满之地。
```
- visible reaction:
```text
"思考"这个词用得很重：睡眠不是意识的空白，而是某种形式的思维活动，是'唵'在其中的运作。"隐匿又全然抵达"是一个悖论式表述——既遮蔽又完全敞开，既沉睡又抵达。这与前面'头枕树根沉沉睡去'构成递进：那次睡着是被动的、耗竭的；这次定义中，睡眠已经被重新赋予了结构和意义。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 146 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p362@0-p366@39:retrospect:146`
- source span: `src:c1:p362@98-p362@127`
- source span excerpt:
```text
这悉达多已变形，脱胎换骨。他奇异地睡去又清醒，愉快又好奇。
```
- visible reaction:
```text
"变形，脱胎换骨"与"他认得自己"同时成立——不是变成别人，而是成为更完整的自己。这和乔文达加入僧团形成对照：乔文达是在一个集体中消融自我，悉达多是在一条孤独的路上找到自我。"愉快又好奇"这个状态很新鲜：前面没有用过"好奇"来描述悉达多，这不是修行者的凝重，而是某种重新出生的眼光。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["thread:govinda_siddhartha_diverge_path"]}`
  - judge reason: Content explicitly references thread:govinda_siddhartha_diverge_path in prior_link ref_ids, but this is a thread reference, not a reaction reference to earlier visible material in the same list—the surface evidence does not ground to specific visible content.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 147 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p362@0-p366@39:highlight:147`
- source span: `src:c1:p363@120-p363@155`
- source span excerpt:
```text
他见悉达多已醒，十分高兴，他仿佛一直在等他醒来，尽管他并未认出悉达多。
```
- visible reaction:
```text
"一直在等他醒来"却"并未认出"——乔文达守候的是一个陌生人。这句话把"守护"与"辨认"之间的距离拉到最大：他的善意是真实的，只是他已经完全不认得悉达多了。这与"这悉达多已变形"形成互文——不仅是外在的变形，连最亲近的朋友都认不出。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 148 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p367@0-p371@5:highlight:148`
- source span: `src:c1:p368@0-p368@10`
- source span excerpt:
```text
“我感谢你，沙门。”
```
- visible reaction:
```text
称呼变了：悉达多称乔文达为"沙门"，而不是"朋友"。在婆罗门的仪式性告别用语中，这个称呼已经足够正式和友善——但对于曾经发誓做彼此影子的人，这层距离本身就是答案。两人已经走上了不同的路，这条路他们没有一起走过。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 149 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p367@0-p371@5:discern:149`
- source span: `src:c1:p371@0-p371@5`
- source span excerpt:
```text
僧人驻足。
```
- visible reaction:
```text
"驻足"——乔文达在说出"再会"并转身离开之后停住了。这个停顿没有解释。它可能是对某种说不清的东西的回应：一种熟悉感，一种在陌生面孔背后隐约感知到的什么。或者只是单纯的犹豫，不知道还有什么该说的话。这三字把告别的余韵悬在了半空，比任何解释都更有力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 150 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p372@0-p376@44:highlight:150`
- source span: `src:c1:p374@0-p374@58`
- source span excerpt:
```text
“我认得你，乔文达。在你父亲的屋舍，在婆罗门学园，在祭祀中，在我们追随沙门的路上，在祗树给孤独园你皈依世尊的时刻。”
```
- visible reaction:
```text
悉达多不是在回忆，他是在证明一条路的连续性。这五个地点串起的不只是地理轨迹，而是一个人如何从父亲屋舍里的婆罗门少年，一步步走向在祗树给孤独园皈依佛陀的僧人。他记得每一段，不是作为旁观者，而是作为同路人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 151 — `weak_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p377@0-p381@35:retrospect:151`
- source span: `src:c1:p379@39-p379@70`
- source span excerpt:
```text
你穿着富人的衣裳和鞋子，你头发飘香。这不像求道者，也不是沙门。
```
- visible reaction:
```text
乔文达的观察本身就是对"求道者该是什么样子"的一种判定——他朝圣多年，从未见过这种打扮。这句话背后隐含的逻辑是：外表与内在是一致的，有那样的外表，内在必定不同。这与前文记住的"主动个体化之路"形成张力：乔文达用集体标准来判断，悉达多已经脱离了这个标准。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - prior_link: `{"ref_ids": ["active_attention:govinda_shadow_devotion"]}`
  - judge reason: Content references active_attention:govinda_shadow_devotion in prior_link, but this is an active_attention reference (a theme), not a direct link to a specific earlier visible reaction—the surface does not ground to concrete earlier material.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 152 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p382@0-p386@79:highlight:152`
- source span: `src:c1:p386@1-p386@21`
- source span excerpt:
```text
我失去了财富，或财富失去了我。它已不在。
```
- visible reaction:
```text
"或财富失去了我"——这个"或"字把主客体完全抹平了。不是他主动放弃，不是财富被动消失，而是两者之间关系本身的瓦解。在前文"主动个体化"的框架下看，这一刻恰好是主动性的反向完成：连"我主动失去"这个叙事都不成立了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 153 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p386@79-p390@33:discern:153`
- source span: `src:c1:p389@152-p389@202`
- source span excerpt:
```text
为了肉体、享乐和财富这些无常之物、卑劣之物，他交付了它们！他陷入古怪的现实。看来，他已真正成为世人。
```
- visible reaction:
```text
"交付"这个词把整个交易说得格外清晰——不是被动失去，而是主动递交。不是"遗弃"了那些艺术去换取财富，而是把斋戒、等待、思考当作筹码，递交给了肉体、享乐和财富这个阵营。而"看来，他已真正成为世人"作为结论，语调平缓，却字字见骨：成为世人不是获得了什么，而是那些使他区别于世人的东西已经全部交出去了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 154 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p386@79-p390@33:highlight:154`
- source span: `src:c1:p389@70-p389@152`
- source span excerpt:
```text
他懂三种高贵又制胜的艺术：斋戒、等待、思考。这是他的宝，他的力，他不变的支撑。他用他勤奋艰辛的全部青年岁月修习这三门艺术，如今他却遗弃了它们，不再斋戒、等待、思考。
```
- visible reaction:
```text
这句话完整地呈现了一个结构的坍塌："他的宝、他的力、他不变的支撑"——三种艺术曾是他的全部根基。三个"不再"对应三个"高贵"，而最后一句"尽管他全无思考的兴致，却依旧强行思考"完成了反讽——连最后一种也在变质中运行。这三门艺术的命运构成了一条值得单独追踪的线索。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 155 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p391@0-p393@11:discern:155`
- source span: `src:c1:p392@382-p392@415`
- source span excerpt:
```text
为了重新找到内在的阿特曼，我必须先成为愚人。为了再活，我必须犯罪。
```
- visible reaction:
```text
这个双重悖论句是全段的逻辑锚点。"愚人"对应前文"变蠢"，"犯罪"呼应"走投无路，堕入深渊"——他把所有世俗意义上最坏的可能性全部接纳为路径本身，而不是路径的终点或偏差。这与婆罗门知识积累的旧路径形成直接对照：旧路径的障碍是"知识不够"，新路径的障碍恰恰相反，是"知识太多而需要清空"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 156 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p391@0-p393@11:highlight:156`
- source span: `src:c1:p391@168-p391@192`
- source span excerpt:
```text
他愉快亲切地望着河水，这不是那条他想溺亡的河吗？
```
- visible reaction:
```text
这条河在悉达多的生命史上完成了最完整的角色转换：先是想要逃离的痛苦终点，此刻成了接纳的平静对象。河水欢歌着"不断下行"，正是悉达多此刻自况的客观对应。"我愿随它走"作为全段最后一句，不是顺从，而是彻底的了悟之后的自愿同行。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 157 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p394@0-p398@391:discern:157`
- source span: `src:c1:p398@311-p398@329`
- source span excerpt:
```text
他死了。一个新的悉达多从睡眠中苏醒。
```
- visible reaction:
```text
"睡眠"在此处不是隐喻性词汇——它对应着他此前在河边的昏厥/沉沉睡去。一个死去的悉达多从睡眠中醒来，这个"醒来"才是真正的觉醒，而此前婆罗门的一切"醒着"实际上都是昏睡。这是"睡眠"与"觉醒"的第三次语义翻转（入睡前→河边昏迷→此刻的精神苏醒），语义在一路叠加。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 158 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p404@0-p408@31:highlight:158`
- source span: `src:c1:p406@6-p406@50`
- source span excerpt:
```text
当年的那条船依旧泊在原处，曾摆渡年轻沙门的船夫站在船旁。他已苍老，但悉达多立刻认出了他。
```
- visible reaction:
```text
"曾摆渡年轻沙门的船夫"——这个定语从句不只是时间标记，它将此刻的悉达多与当年离开沙门身份的自己连接起来。船不变，船夫老了，悉达多的身份换了，但渡河这件事本身没变。这是循环结构的又一次现身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 159 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p404@0-p408@31:highlight:159`
- source span: `src:c1:p408@0-p408@31`
- source span excerpt:
```text
船夫惊讶地望着这位独自踱步的华贵之人，继而扶他上船，撑船离岸。
```
- visible reaction:
```text
"华贵之人"这个措辞在此处有双重的陌生感：不仅船夫感到陌生，连读者也在此前很久没有见过如此描述悉达多的词。"独自踱步"与"华贵"的并置，标记了悉达多从沙门苦行者到世俗贵族的完整弧线，而这条弧线的终点，他回到了渡口。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 160 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p409@0-p413@49:highlight:160`
- source span: `src:c1:p410@0-p410@41`
- source span excerpt:
```text
船夫摇橹微笑道：“的确美好，先生，如你所云。难道不是每种生活、每种劳作都很美好？”
```
- visible reaction:
```text
这个反问不只是船夫的谦逊，而是一种平等主义的生活哲学——万物皆有其美好，正是这种态度让他能安然做一个船夫而不觉卑微。这与前文"精神容器永不盛满"的焦虑形成对照：船夫之所以满足，不是因为他的容器大，而是因为他根本不需要用外在之物去填满它。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 161 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p409@0-p413@49:highlight:161`
- source span: `src:c1:p412@0-p412@27`
- source span excerpt:
```text
“啊，你很快会失去兴趣。这种生活不适合穿着体面之人。”
```
- visible reaction:
```text
船夫这句话精准地击中了悉达多此前的身份。"穿着体面之人"与前文船夫眼中"独自踱步的华贵之人"形成精确回扣，而"你很快会失去兴趣"则暗示了悉达多在世俗富贵中也曾有过的倦怠。船夫无意中说出了悉达多自己的处境。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Directly links 'dressed presentably' from this passage to the ferryman's earlier description of '独自踱步的华贵之人' and connects 'lose interest' to Siddhartha's documented world-weariness.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 162 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p413@49-p417@54:discern:162`
- source span: `src:c1:p417@0-p417@54`
- source span excerpt:
```text
“啊，我倒希望最好不再赶路。船夫，你要是给我条旧围裙，收我做你的帮手就好了。最好做你的学徒，我要先学会撑船。
```
- visible reaction:
```text
这个"希望不再赶路"与前文所有情节形成根本断裂：婆罗门时期他在求道，沙门时期他在赶路离开轮回，佛陀出现后他在赶路赴约，世俗时期他在赶路积累。现在连目的地都不要了。"学撑船"这个具体而微小的愿望，替代了此前所有的宏大追求——这不是过渡阶段，而是一种全新的存在姿态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly contrasts 'hope no longer to travel' against all prior narrative phases: Brahmin seeking, Shramana fleeing, Buddha rushing, and merchant accumulating.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 163 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p417@54-p421@57:highlight:163`
- source span: `src:c1:p419@0-p419@54`
- source span excerpt:
```text
“我认出你了。”终于，他开口道，“很久以前，二十多年前，我曾渡你过河，你在我的茅舍过夜，我们曾像好友般道别。
```
- visible reaction:
```text
这个"终于"字很重要——不是脱口而出，而是经历了长久凝视之后的开口。二十多年前那个渡河之夜，两人曾像好友般道别，而今悉达多重返这条河、这间茅舍，完成了某种隐秘的循环。船夫的记忆成为悉达多身份最朴素也最可靠的锚点。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Cites '二十多年前那个渡河之夜' - directly references the earlier crossing episode, marking return to a specific prior location in the narrative.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 164 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p417@54-p421@57:highlight:164`
- source span: `src:c1:p421@0-p421@57`
- source span excerpt:
```text
“悉达多，欢迎你。我叫瓦稣迪瓦。我希望你今天仍是我的客人，住在我的茅舍。跟我讲讲你从哪里来，为何你的华服成了累赘。
```
- visible reaction:
```text
"为何你的华服成了累赘"这个问法精准地击中了悉达多此刻状态的核心：不是华服本身沉重，而是它们作为身份符号已经失效。这个问题船夫问得自然，却恰好触及悉达多整个世俗时期的核心矛盾。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Links '累赘' to the precise situation of Siddhartha discarding his fine clothes, connecting to the passage being analyzed and earlier wealth/luxury context.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 165 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p421@57-p423@53:retrospect:165`
- source span: `src:c1:p422@106-p422@130`
- source span excerpt:
```text
船夫端来面包和水，悉达多欢快地吃着，也吃了芒果。
```
- visible reaction:
```text
"欢快地"三个字在这个位置极为关键。婆罗门时期"无法让自己喜悦"，世俗时期欲望越盛内在越空，而此刻几片面包和水、一颗芒果，竟能欢快地吃——最简单的食物正在修复那个结构性饥饿的精神容器。这是比任何法义都更根本的转变信号。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:inner_void_despite_outer_perfection"]}`
  - judge reason: Uses prior_link to 'inner_void_despite_outer_perfection'; contrasts '欢快地' eating simple food against the documented '无法让自己喜悦' in Brahmin period.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 166 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p421@57-p423@53:retrospect:166`
- source span: `src:c1:p423@16-p423@53`
- source span excerpt:
```text
悉达多向船夫述说起自己的来历和生活，述说那些历历在目的绝望时刻，直至夜深。
```
- visible reaction:
```text
"历历在目"这个措辞精准：绝望不是模糊的往事，而是清晰可触的记忆。他在向一个寡言的船夫敞开这段最黑暗的历程——不是向圣哲求教，而是向一个"不思想、不评判"的人倾诉。这种反向的信任选择，恰好印证了船夫角色作为"无言的容器"的功能。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["thread:atman_self_ungraspable_by_thought"]}`
  - judge reason: Uses prior_link to thread 'atman_self_ungraspable_by_thought'; explicitly connects sharing darkest memories with the ferryman to earlier struggles with self-knowledge.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 167 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p424@0-p428@130:discern:167`
- source span: `src:c1:p424@32-p424@99`
- source span excerpt:
```text
船夫最大的美德是倾听：他乃少数擅长倾听之人。即便默不作声，讲述者也能感知他在安静、坦诚、满怀期待地倾听。他既不褒扬亦不挑剔，只是倾听。
```
- visible reaction:
```text
船夫美德的定义是倾听而非言说——这与婆罗门时期教义权威和佛陀的言说形成鲜明对照。船夫通过"无言"完成了导师的职能，却又不将自己置于导师位置。这种"否定性导师"的结构，恰好呼应了前文所述"阿特曼不可通过求知欲和修习获得"的核心悖论——越是试图教导，越是将学习者推离。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Contrasts ferryman's listening against Brahmin doctrinal authority and Buddha's speaking, explicitly referencing all three prior teaching traditions.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 168 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p424@0-p428@130:highlight:168`
- source span: `src:c1:p428@0-p428@55`
- source span excerpt:
```text
“你自会学到。”瓦稣迪瓦道，“却不是跟我。我跟河水学会倾听，你也该跟它学。河水无所不知，求教河水你可学会一切。
```
- visible reaction:
```text
"却不是跟我"——这个否定性指向极为关键。船夫通过转向河流来完成教导，将自己定位为河流与悉达多之间的中介而非源头。这与所有其他导师（婆罗门、沙门、佛陀）直接言说的方式根本不同，指向一种"无言之道"的哲学。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Contrasts ferryman pointing to river against all other teachers (Brahmin, Shramana, Buddha) who speak directly - explicit structural comparison.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 169 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p428@130-p430@251:highlight:169`
- source span: `src:c1:p430@192-p430@239`
- source span excerpt:
```text
对于这些人中为数不多的四五人来说，河水却并非障碍，他们凝神听水。同我一样，河水在他们心中圣化。
```
- visible reaction:
```text
"四五人"这个具体数字与前文"千万人"构成强烈对照。船夫一辈子渡了千万人，但真正听懂河水的只有四五人。这个比例揭示了一种稀有性——不是普遍启示，而是极少数人的道路。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 170 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p431@0-p431@138:retrospect:170`
- source span: `src:c1:p431@71-p431@138`
- source span excerpt:
```text
他跟河水比跟瓦稣迪瓦学到的更多，他永不停歇地向河水求教，首要的是学会抛弃激情和期盼，不论断、无成见地以寂静的心、侍奉和敞开的灵去倾听。
```
- visible reaction:
```text
"侍奉和敞开的灵"这个并列很有张力——不是被动消极的接受，而是带着侍奉姿态的敞开。抛弃激情与期盼不是为了空无，而是为了以一种全然不同的方式在场。这也呼应了前文阿特曼"不可通过求知欲和修习获得"的悖论：越是主动求取，越是远离；越是以被动的侍奉姿态倾听，反而越能触及。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p424@0-p428@130:highlight:168"]}`
  - judge reason: Uses prior_link to reaction:highlight:168; builds on ferryman pointing to river, connecting '侍奉姿态' to the '否定性导师' framework established in that linked passage.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 171 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p432@0-p436@109:highlight:171`
- source span: `src:c1:p436@33-p436@65`
- source span excerpt:
```text
这条河用幻象，而非现实，隔开少年悉达多、成年悉达多和老年悉达多。
```
- visible reaction:
```text
"幻象"与"现实"的区分是关键——分离不同时刻的不是时间本身，而是人心给时间加上的虚假的网。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 172 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p432@0-p436@109:highlight:172`
- source span: `src:c1:p436@65-p436@109`
- source span excerpt:
```text
悉达多的前世并非过去，死亡和重归梵天亦并非未来。没有过去，没有未来。一切都是本质和当下。
```
- visible reaction:
```text
这是对印度教轮回时间观的根本消解——前世、死亡、梵天回归，这些本应是线性的过去和未来，现在全部压缩为"当下"。"本质"这个词暗示：一切存在的核心不是时间的延伸，而是永恒的在场。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0010` / note `xidaduo_private_zh_personal_notes__e0010` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p436@89-110` 没有过去，没有未来。一切都是本质和当下。”
    - target note: 没有过去，没有未来。一切都是本质和当下。”
    - source-span relation: `partial_overlap`; coverage `0.95`
    - judge/runner reason: The reaction's quoted source span (char 65-109) contains the note's entire source span (char 89-110) and the reaction's interpretive content is directly focused on the note's core insight: the dissolution of linear time into '当下' (the present) and '本质' (essence). The extra context included in the quote ('悉达多的前世并非过去，死亡和重归梵天亦并非未来') serves to ground the interpretation in the broader philosophical context but does not dilute the reaction's focus on the note's central message. The 0.9524 coverage confirms the note is fully embedded within and central to the reaction's quoted span.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0010.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 173 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p436@109-p438@81:discern:173`
- source span: `src:c1:p437@48-p437@82`
- source span excerpt:
```text
人一旦战胜时间，放逐时间，一切世上的苦难与仇恨不就被战胜，被放逐了？
```
- visible reaction:
```text
这个表述从"时间制造幻象"推进到"战胜时间=战胜苦难"，逻辑上更进了一步，但也更危险——它暗示救赎是可获得的、是通过某种修行可以达到的状态。这与前文阿特曼"不可通过求知欲和修习获得"构成反向张力：如果战胜时间本身成为新的目标，那又回到了求取之路。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 174 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p438@81-p442@198:highlight:174`
- source span: `src:c1:p441@0-p441@43`
- source span excerpt:
```text
瓦稣迪瓦幸福地微笑着，俯身靠近悉达多，在他耳畔说出神圣的“唵”。这也正是悉达多听到的。
```
- visible reaction:
```text
这个"也正是"是关键——不是瓦粟迪瓦传授了答案，而是两人的聆听同时抵达了同一个地方。真正的悟不是一方给予另一方，而是两方同时听到同一件事。这是婆罗门教义、佛教、沙门修行都无法抵达的通道，因为那种抵达需要的是倾听而非求知。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Implicitly contrasts with Govinda (Brahmin friend, '影子') who followed Buddha - reader knowledge of character arc provides grounding.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 175 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p438@81-p442@198:highlight:175`
- source span: `src:c1:p442@55-p442@74`
- source span excerpt:
```text
许多旅人见到这对船夫，以为他们是兄弟。
```
- visible reaction:
```text
这与乔文达构成深层对照：乔文达曾经是悉达多最亲近的人，被称为"影子"和"最爱他的人"，却在信仰道路上走向佛陀。而此刻被陌生人误认为兄弟的，是渡船的瓦粟迪瓦——一个以倾听河水为修行的人。真正的同道，不是童年的情感纽带，而是当下的精神共振。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Mentions Govinda as '影子' and '最爱他的人' - these labels exist in earlier visible reactions (2, 51) but no explicit prior_link is cited; reliance on theme rather than anchored citation.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 176 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p443@0-p443@171:discern:176`
- source span: `src:c1:p443@116-p443@171`
- source span excerpt:
```text
他们没有见到法师和智者，只是见到两位缄默迟钝、有些特别的老人，于是他们嘲笑那些轻信的愚蠢之人，散布荒谬的谣言。
```
- visible reaction:
```text
这个转折最刺目：来求智慧的人，因为没得到答案而成为嘲笑者。"轻信的愚蠢之人"——他们用这个词称呼的恰恰是自己刚才还认同的那个慕道者的自己。这是一个求索者自我否定的结构：追求真理而不得，便转而否定真理的存在。这与乔文达式的皈依形成对照——后者是将自我交付给一个答案体系，而这里的人则是将失望直接转化为虚无。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Structurally contrasts these seekers' rejection with Govinda's acceptance/皈依, which was explicitly documented in reactions 49-50 and 54.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 177 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p444@0-p447@214:highlight:177`
- source span: `src:c1:p446@124-p446@196`
- source span excerpt:
```text
一位真正的求道者，真正渴求正觉成悟之人不会接受任何法义。但得道之人却认可任何法义、道路和目标。没有什么能将他和其他万千驻永恒、通神冥的圣贤隔绝。
```
- visible reaction:
```text
这与前文"知识积累不能等于内在拥有"形成完整闭合：求道者的拒绝法义不是因为法义有错，而是因为接受任何单一法义都意味着在终点之前画地为牢。而得道者之所以能认可一切，正因为终点不在任何一条路上——终点是超越路本身的存在状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly links to '知识积累不能等于内在拥有' - a concept established in reactions 5, 7, 8, 23 about the gap between knowing and arriving.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 178 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p444@0-p447@214:highlight:178`
- source span: `src:c1:p447@161-p447@214`
- source span excerpt:
```text
孩子不理解母亲为何带他踏上辛苦忧伤的朝拜之路，去往陌生地，见一位陌生而垂死的圣人。他死了和小孩有什么关系？
```
- visible reaction:
```text
这个问题在文本内部构成对神圣叙事的最质朴解构：佛陀的涅槃是宇宙事件还是个人执念？小悉达多的冷漠与四方如蚁涌来的人群形成结构性反讽——伟大与渺小、永恒与当下，赶往同一终点的两极心态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 179 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p448@0-p452@119:highlight:179`
- source span: `src:c1:p449@123-p449@221`
- source span excerpt:
```text
他抬起头，先见到孩子的脸，这张脸让他惊讶地记起已经淡忘的往事。接着，他看见迦摩罗，尽管她晕厥地躺在船夫的臂弯中，悉达多还是马上认出她。他立即明白，这个有着和他相同面孔的孩子是他的儿子。他心潮起伏。
```
- visible reaction:
```text
"他心潮起伏"——四个字压住了所有可能的抒情。但恰恰是这种克制，让这个瞬间变得无比沉重：他不需要任何解释，不需要任何确认，看到孩子的脸，看到她，就明白了。所有的往事不是被"想起"，而是被"认出"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 180 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p453@0-p455@146:highlight:180`
- source span: `src:c1:p455@39-p455@83`
- source span excerpt:
```text
他望着孩子的脸，想起自己儿时学过的婆罗门祷文，开始慢声吟唱起来，祷词从往昔和童年涌向他。
```
- visible reaction:
```text
"从往昔和童年涌来"——这个"涌"字很关键。不是回忆，不是检索，而是源头本身向他涌动。他给儿子的不是教义，是源头。这种传承的方式与悉达多此前拒绝一切法义的立场完全一致：不给任何结论，只给源头。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: The '涌' echoes narrative structure from earlier '那声音向你涌来' reactions; implicitly connects to flowing/receiving imagery established in river passages.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 181 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p453@0-p455@146:highlight:181`
- source span: `src:c1:p455@106-p455@146`
- source span excerpt:
```text
悉达多把他放在瓦稣迪瓦的床上。瓦稣迪瓦正在炉边烧饭，悉达多瞥向他，他以微笑作答。
```
- visible reaction:
```text
瓦稣迪瓦的"微笑作答"——他不问，不说，甚至不回头看，只是烧着饭，微笑。这个沉默比任何言语都更完整地接纳了眼前的一切。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Connects Vasudeva's '微笑作答' to Siddhartha's own '不语' response - both characters using silence as communication, callback to Siddhartha's earlier wordless acknowledgment.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 182 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p456@0-p460@17:highlight:182`
- source span: `src:c1:p459@0-p459@48`
- source span excerpt:
```text
她看见他，说道：“我看到，你的眼睛变了，不同于从前。可我是怎么认出你的？你是悉达多，却又不是。”
```
- visible reaction:
```text
这个"却又不是"与开篇的自我追寻形成完整的回环。迦摩罗不是在辨认一张脸，而是在辨认一个人——而那个人已经变了。认出"是"，同时认出"不是"，这两种判断竟然可以同时成立，这本身就是悉达多一路走来的证明。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly states '与开篇的自我追寻形成完整的回环' - directly anchors to the opening chapter's self-quest narrative arc.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 183 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p456@0-p460@17:highlight:183`
- source span: `src:c1:p460@0-p460@17`
- source span excerpt:
```text
悉达多不语，他安静地望着她的眼睛。
```
- visible reaction:
```text
"不语"在这里是完整的回应。面对"你是悉达多却又不是"这句话，任何言语都是多余的解释，而沉默本身就是最好的承认——他接受了这种矛盾，不辩解，不纠正，只是望着她，如同望着他自己已经走过的路。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Connects Siddhartha's '不语' from recognition moment to Kamala's matching '不语' now - direct verbal/action callback within visible text.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 184 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p461@0-p465@143:highlight:184`
- source span: `src:c1:p465@9-p465@63`
- source span excerpt:
```text
她想起自己本是去朝觐乔达摩，去亲眼目睹佛陀的圣容，吸纳他的平和，却和悉达多重逢。这样也好。和见到佛陀同样好。
```
- visible reaction:
```text
这个"同样好"是全章最轻、最重的句子。它不是在比较两条路的高下，而是在说：遇见悉达多与亲眼见到佛陀，在精神上等价。这将悉达多放到了与佛陀同级的位置——他不是佛陀的门徒，他自己就是目的地。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 185 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p461@0-p465@143:highlight:185`
- source span: `src:c1:p465@63-p465@87`
- source span excerpt:
```text
她想把这告诉他，可舌头却不听使唤。她默默望着他。
```
- visible reaction:
```text
这里的"不语"与悉达多之前的"不语"形成完整的呼应——他在认出"是悉达多却又不是"时选择沉默，她也在这最想说话的时刻失去了言语。两个人用同样的方式完成了最后的交流：不说。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly links Kamala's '不语' to Siddhartha's earlier '不语' in section 1.456 - consecutive silence patterns forming complete exchange.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 186 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p467@0-p467@110:highlight:186`
- source span: `src:c1:p467@60-p467@87`
- source span excerpt:
```text
他倾听河水奔涌，沉浸在往事中，被一生的时光触摸，簇拥。
```
- visible reaction:
```text
时间拟人化：不是他在回忆时间，而是时间在触摸他、簇拥他——一种被动的、被命运浸润的感受。这与前面"不语"和"同样好"的情感重量形成反差，这里是更宽广、更沉默的承接。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 187 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p472@38-p474@15:highlight:187`
- source span: `src:c1:p474@0-p474@15`
- source span excerpt:
```text
孩子仍在熟睡。他们架起了柴堆。
```
- visible reaction:
```text
全章最轻与最重的句子并置。熟睡——生命；柴堆——死亡。它们之间没有任何过渡词，只有句号。这不是对比，是同在。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 188 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p475@0-p479@123:highlight:188`
- source span: `src:c1:p478@121-p478@160`
- source span excerpt:
```text
他不强迫他，而是为他做事，把最好的留给他。他希望善意的忍耐能慢慢赢得孩子的心。
```
- visible reaction:
```text
这与前文悉达多离开父亲时的"不回头"形成鲜明对照。当年父亲想用期待留住他；现在他选择用善意而非权力留住儿子。这是他真正学到的一课——控制是假的，忍耐才是真的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly contrasts with '离开父亲时的'不回头'' from section 1.36-40, which was documented in reactions 15, 19-20.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 189 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p475@0-p479@123:highlight:189`
- source span: `src:c1:p479@90-p479@123`
- source span excerpt:
```text
可是他爱他，宁愿忍受爱的痛苦和忧虑，也不愿接受没有他的幸福和快乐。
```
- visible reaction:
```text
全章最简洁也最重的句子。爱在这里被定义为一种主动选择承担的痛苦，而非任何形式的交换或安慰。这与前面所有关于"容器"、"焦渴"、"空洞"的描写形成隐秘呼应——他在给予爱中承受的匮乏，恰恰是他灵魂的满盈。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Implicitly connects to earlier '容器'/'焦渴'/'空洞' imagery from reactions 4, 6, 8, 72 - the hunger framework now redefined through giving love.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 190 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p480@0-p484@136:highlight:190`
- source span: `src:c1:p482@55-p482@113`
- source span excerpt:
```text
这只小鸟在另一个巢穴过惯了另一种生活。他不像你，出于憎恶和厌倦逃离城邑和富裕的生活。他是违背意愿，不得不放弃那一切。
```
- visible reaction:
```text
同样是离开，动机却完全相反。悉达多主动逃离，儿子被迫放弃——这种不对称将"爱"的难题推到极致：父亲的经验无法直接移植给儿子。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Implicitly contrasts active逃离 (Siddhartha leaving Brahmin/Shramana/Buddha) with被动放弃 - reader recall of documented departure patterns provides grounding.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 191 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p480@0-p484@136:highlight:191`
- source span: `src:c1:p484@33-p484@66`
- source span excerpt:
```text
可是你和我，我们知道他为何奉召而来？走什么路？做什么事？受什么苦？
```
- visible reaction:
```text
三个问号不只是瓦酥迪瓦的追问，也是全书最核心的悬念——没有人知道另一个灵魂的命运。河水不回答，只嘲笑人类的自大。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Implicitly invokes river's voice/speech theme from section 1.436-438 (reactions 171-174) where the river's answers were discussed.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 192 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p484@136-p487@24:highlight:192`
- source span: `src:c1:p486@48-p486@96`
- source span excerpt:
```text
可你不强迫不责罚的主张，难道不是一种过失？难道你没有用爱束缚他？没有每天用善和忍，令他羞愧为难？
```
- visible reaction:
```text
这一问把全书"柔与刚"的对立推向了第三层：善本身可以是暴力，爱本身可以是束缚。不是软比硬好，而是所有施加都值得质疑——包括"好的"施加。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Claims full chapter arc for '柔与刚' - reader recalls earlier structural contrasts documented throughout; implicitly grounded in visible progression.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 193 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p484@136-p487@24:highlight:193`
- source span: `src:c1:p487@0-p487@24`
- source span excerpt:
```text
悉达多错愕地垂下头，轻声问：“你说我该怎么办？”
```
- visible reaction:
```text
这是悉达多全书唯一一次主动向他人请教"怎么办"。此前他每一次转向都是主动的——逃离婆罗门、离开沙门、告别佛陀。这一刻，他被问住了，身体语言从"垂下头"三个字里透出此前从未有过的茫然。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly contrasts with all documented active departures: '逃离婆罗门、离开沙门、告别佛陀' - all three documented in visible reactions.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 194 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p488@0-p492@92:highlight:194`
- source span: `src:c1:p490@161-p490@205`
- source span excerpt:
```text
人独自行过生命，蒙受玷污，承担罪过，痛饮苦酒，寻觅出路。难道有人曾被父亲或老师一路庇护？
```
- visible reaction:
```text
这是全书最接近直接陈述"哲学"的地方。"独自行过生命"——不是孤独感，而是结构性的：任何人的替代或保护都是幻觉。这把前面所有关于教育、爱、善的讨论全部收拢到一个不可动摇的底线上。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0012` / note `xidaduo_private_zh_personal_notes__e0012` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p490@161-189` 人独自行过生命，蒙受玷污，承担罪过，痛饮苦酒，寻觅出路。
    - target note: 人独自行过生命，蒙受玷污，承担罪过，痛饮苦酒，寻觅出路。
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction's source span contains the exact note text and extends slightly beyond it. The reaction's content is focused on interpreting '独自行过生命' as a structural concept rather than mere loneliness, and explicitly connects it to the book's themes of education, love, and good. The commentary directly engages with and elaborates on the note's philosophical content rather than merely quoting or tangentially referencing it.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0012.json`
- Callback/FVI audit: `grounded_callback`
  - judge reason: Claims '全书最接近直接陈述' - reader recall of visible arc; implicitly connects to earlier '独自' themes documented throughout.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 195 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p488@0-p492@92:highlight:195`
- source span: `src:c1:p491@54-p491@99`
- source span excerpt:
```text
但那只是认知，他无法行动。因为比认知更强烈的是他对孩子的爱，他的柔情，他对失去孩子的恐惧。
```
- visible reaction:
```text
这句话捅破了一个最脆弱的地方：悉达多一辈子求索阿特曼，到头来却发现有一种力量比最高的认知更强——爱本身。认知可以在思想上抵达一切，却无法在行动上穿透这道温柔的墙。这和前文他离开沙门、告别佛陀时那种主动决断形成了鲜明对比：他现在完全被动。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Contrasts with documented '主动决断' of leaving Brahmin/Shramana/Buddha - all three visible departures provide grounding for this passive contrast.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 196 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p493@0-p497@140:highlight:196`
- source span: `src:c1:p493@40-p493@45`
- source span excerpt:
```text
你不会爱。
```
- visible reaction:
```text
迦摩罗二十年前说的这句话，现在变成了悉达多对自己最准确的诊断——不是判断，是诊断。他从未爱过，这不是他的失败，而是他整个求道生涯的结构性前提。儿子出现，他才第一次被这句话钉住。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly references '迦摩罗二十年前说的这句话' - direct verbal echo to earlier Kamala dialogue documented in reactions 79-90.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 197 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p493@0-p497@140:highlight:197`
- source span: `src:c1:p497@62-p497@115`
- source span excerpt:
```text
你希望我像你一样虔敬、温顺、明智！可是我，你听着，我要让你痛苦。我宁愿做扒手、杀人犯、下地狱，也不愿做你！
```
- visible reaction:
```text
这是全书最残忍的孩子的话。不是因为它粗俗，而是因为它精准地刺中了每一个悉达多式的美德与婆罗门体系之间的暧昧关系：虔诚、温顺、明智——在孩子的逻辑里，这些不是境界，是锁链。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 198 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p497@140-p498@31:discern:198`
- source span: `src:c1:p498@0-p498@18`
- source span excerpt:
```text
他愤怒又悲伤，粗野又恶毒地咒骂父亲。
```
- visible reaction:
```text
四个词并置：愤怒/悲伤，粗野/恶毒。前两个是情感维度，后两个是表达方式——但两者之间并不对应。愤怒通常是粗野的出口，悲伤通常是痛苦的沉默。这里"愤怒又悲伤"同时与"粗野又恶毒"搭配，暴露的是悉达多此刻已经没有任何内在空间来调节自己——他完全被情绪淹没，完全失去了一向引以为傲的精神自制力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 199 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p499@0-p499@63:highlight:199`
- source span: `src:c1:p499@45-p499@63`
- source span excerpt:
```text
悉达多发现小船泊在对岸，孩子已逃走。
```
- visible reaction:
```text
"泊在对岸"——船安全地停在对岸，说明孩子水性好、撑船技术没问题，这个细节反过来揭示孩子并非冲动出逃，而是有计划地掌握了自己的命运。"已逃走"的"已"字比"逃走了"更有完成时态的判决感：这是既成事实，无法更改。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: The child's plan and skill implicitly echo Siddhartha leaving father in section 1.36-40 (reactions 15, 17-20) - both involve deliberate, competent departure.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 200 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p500@0-p504@141:discern:200`
- source span: `src:c1:p501@39-p501@86`
- source span excerpt:
```text
朋友，他不再是孩子了，他会保护自己。他要回城里，他做得对。别忘了这点，他做的，正是你耽搁的事。
```
- visible reaction:
```text
这句话是整段的核心。"他做的，正是你耽搁的事"——孩子走的是独立之路，而悉达多自己也曾如此离开父亲。瓦乌斯迪瓦实际上在说：你在恨你的孩子走你走过的路，但你有没有意识到你自己当年对你的父亲做了什么？这种递归式的对称揭示了悉达多此刻的双重标准：他可以离开父亲去求道，却不允许儿子离开他去求生。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly invokes recursive symmetry: '你当年对你的父亲做了什么' - directly recalls section 1.34-40 father's waiting scene documented in reactions 12-20.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 201 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p505@0-p507@201:discern:201`
- source span: `src:c1:p505@104-p505@134`
- source span excerpt:
```text
可他却不能停下脚步，不是为救孩子，只为盼着或许还能见上一面。
```
- visible reaction:
```text
这句话把悉达多从"焦虑的父亲"重新定义为"有情感需要的人"。他并不真的担心孩子的安危（他知道孩子水性好、会保护自己），他停不下来仅仅是因为想看孩子一面。这种承认情感需要而非行动必要的话语，实际上标志着他与儿子的关系从权力博弈进入了一个更人性的层面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Thematically connects to earlier material on Siddhartha's emotional architecture—the 'spiritual container never fills' motif (reactions 4-6) and his fundamental inability to love (reactions 123-125). The claim that this moment marks his transition from 'power game' to 'human level' implicitly grounds in earlier established pattern, but no specific prior reaction is cited.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 202 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p508@0-p510@213:discern:202`
- source span: `src:c1:p510@170-p510@178`
- source span excerpt:
```text
谁也不触碰伤口。
```
- visible reaction:
```text
这一句把整段的沉默主题收得极准。不是“没有人谈论此事”，而是“谁也不触碰伤口”——伤口是活的、有边界的存在，触碰即意味着重新撕开。不触碰，是一种共同的克制，也是一种共同的保护。瓦乌斯迪瓦的善意不需要语言来传达，他只是用手唤醒他递上芭蕉，然后陪他沉默着穿过森林回来。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 203 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p508@0-p510@213:highlight:203`
- source span: `src:c1:p509@100-p509@116`
- source span excerpt:
```text
他跟河水学会了等待、忍耐、倾听。
```
- visible reaction:
```text
这是从行动者到倾听者的关键翻转。年轻时悉达多总是入城、下河、做生意——现在他所有的练习都指向退让：不是去做什么，而是待在原地，听自己心跳的声音，等某种声音从内心升起。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: Implicitly references Siddhartha's historical pattern of active engagement with the world—prior reactions documented his city visits, business transactions, and sensory immersion in chapters 6-8. The 'from actor to listener' framing echoes those behavioral records but cites no specific earlier reaction.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 204 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p511@0-p513@103:highlight:204`
- source span: `src:c1:p513@95-p513@103`
- source span excerpt:
```text
和世人一模一样。
```
- visible reaction:
```text
这是悉达多身份的根本滑落。不是稍有动摇，而是彻底：他终于和所有普通人一样了。前文他跟河水学会了等待、忍耐、倾听——那些修行的品质，在这句哀怨面前全部失效。他不需要智慧，他只需要一个孩子。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 205 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p514@0-p518@112:highlight:205`
- source span: `src:c1:p515@19-p515@87`
- source span excerpt:
```text
究竟什么是智慧？什么是他的目标？不过是在生命中的每个瞬间，能圆融统一地思考，能感受并融入这种统一的灵魂的准备，一种能力，一种秘密的艺术。
```
- visible reaction:
```text
这里对智慧的终极定义：不是关于什么的知识，而是每一个瞬间都能统一思考的感受力——一种随时在场的准备状态，而非某种达成后的静止状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 206 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p514@0-p518@112:highlight:206`
- source span: `src:c1:p518@42-p518@112`
- source span excerpt:
```text
难道父亲不是为他受苦，如同他现在为儿子受苦？难道父亲不是再没见到儿子，早已孤零零地死去？这难道不是一幕奇异又荒谬的谐剧？不是一场宿命的轮回？
```
- visible reaction:
```text
这一段是全段的情感锚点。河水笑完以后，他在倒影里看见父亲的脸——这张脸让他直接面对自己当年离家时父亲的处境。"荒谬的谐剧"和"宿命的轮回"两个词并置，前者带着自嘲的苦涩，后者指向超越个人意志的结构性力量。悉达多修习了一切，最终发现自己仍在轮回之中。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: The father's face in the river echo connects to the established recursive pattern documented in reaction 200 ('the child does what you delayed') and earlier departure scenes. The 'absurd comedy' and 'fateful reincarnation' framing implicitly builds on earlier visible material about father-son departure symmetry, but no specific prior reaction is cited.
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 207 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p519@0-p522@304:highlight:207`
- source span: `src:c1:p522@64-p522@94`
- source span excerpt:
```text
向这位倾听者袒露伤口，如同在河中沐浴，伤口冷却后与河水合一。
```
- visible reaction:
```text
这句是全段的情感核心。伤口在河中冷却，然后与河水合一——不是伤口被治愈，而是伤口本身变成了河水的一部分。悉达多的痛苦没有消失，而是被升华进了河流的永恒之中。这与他从河水学到的'统一'完美呼应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 208 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p523@0-p525@139:discern:208`
- source span: `src:c1:p525@92-p525@139`
- source span excerpt:
```text
每个人都奔向目标，被折磨，受苦难。河水痛苦地歌唱着，充满渴望地歌唱着，不断涌向目标，如泣如诉。
```
- visible reaction:
```text
「奔向目标」这个表达将三幅画面——父亲、自己、儿子——统一在同一个运动里。它不是个别的悲伤，而是一个结构性的模式：渴望即折磨，目标是囚禁本身。河水最后那句「如泣如诉」把前面所有的倒影画面收束成一种持续的悲鸣，使「轮回」这个词获得了一个音乐性的身体。
```
- Selective Legibility dataset relation:
  - note-case `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0020` / note `xidaduo_private_zh_personal_notes__e0020` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p525@92-109` 每个人都奔向目标，被折磨，受苦难。
    - target note: 每个人都奔向目标，被折磨，受苦难。
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction's source span contains the note's full text, and the reaction's analysis is specifically focused on the phrase '奔向目标' from the note, interpreting it as a structural pattern that unifies three generations, directly addressing the note's core idea that 'desire is torment and the goal is the prison itself.' The additional river imagery in the source span serves as supporting context, but the reaction's primary focus remains on the note's central content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0020.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 209 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p529@0-p533@115:highlight:209`
- source span: `src:c1:p529@172-p529@263`
- source span excerpt:
```text
当他专注于河水咆哮的交响，当他不再听到哀，听到笑，当他的灵魂不再执念于一种声音，自我不再被占据，而是倾听一切，倾听整体和统一时，这伟大的交响，凝成了一个字，这个字是“唵”，意为圆满。
```
- visible reaction:
```text
「不再听到哀，听到笑」——这个并列句揭示了修行的核心：不是学会了某种高级的听法，而是彻底停止了选择。所有的哀与笑同时涌来，而灵魂不再被任何一种占据。统一不是综合，而是不再区分。这个「唵」是取消区别的结果，不是添加进来的东西。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 210 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p529@0-p533@115:highlight:210`
- source span: `src:c1:p533@48-p533@97`
- source span excerpt:
```text
我在等候这一时刻，亲爱的，现在它终于来临。让我走吧，我已等候良久，我已做了太久的船夫。现在已结束。
```
- visible reaction:
```text
瓦酥迪瓦的离开与悉达多的觉醒同时完成。他不是被动的旁观者，而是引导者——引导到无需再引导的那一刻。「做了太久的船夫」呼应了前文船夫作为过渡性角色的定位：河流是通道，不是居所。当悉达多已能在河中听见「唵」，船夫的历史使命便完结了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 211 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p533@115-p536@23:highlight:211`
- source span: `src:c1:p536@0-p536@23`
- source span excerpt:
```text
“我要去林中，去融入统一。”瓦稣迪瓦光芒四射。
```
- visible reaction:
```text
"光芒四射"这个词骤然明亮——它不仅是告别，更是一种显化。船夫在离开的瞬间成为光本身，与佛陀的圆满、与"唵"的圆满形成结构性的共鸣。融入统一不是削弱，而是显发。这与前文"统一不是综合而是不再区分"形成深层回响：区分停止之时，光芒才得以透出。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

## Probe Memory Checkpoints

Memory Quality is scored at probe time. The state below is a structured re-layout of the recorded probe snapshot, not a fresh summary and not the final runtime dump.

### Probe 1 — MQ `3.50` — near 20%

#### Probe Position And Question
- target sentence: `c1-s442`
- boundary kind: `chapter close`
- why this point: Ends the 沙门 chapter before 乔达摩, closing Siddhartha's ascetic self-denial phase and its limits.
- structural signals to check:
  - initial dissatisfaction
  - ascetic self-denial and Samana path
  - failure of escape-through-self-erasure before Buddha encounter

#### Source Orientation
```text
   s440 / p108: 你尽管嘲讽我，悉达多！
   s441 / p108: 难道你心中没有萌生去聆听这位觉者宣法的渴望和欲念吗？
>> s442 / p108: 你不是曾和我说过，你不会在沙门之路上久留吗？
   s443 / p108: ”
   s444 / p109: 悉达多以他特有的方式笑了。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:knowledge_insufficient_but_not_wrong",
      "item_id": "knowledge_insufficient_but_not_wrong",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "婆罗门知识的结构性局限：经典本身无误，诗句蕴含智慧，但知识积累不能等同于内在阿特曼的拥有——两者之间存在不可通约的断裂",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p11@462-p11@480",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 462
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 480
            }
          },
          "quote": "其他一切都只是寻觅、走弯路和误入歧途",
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
      "ref_id": "active_attention:knowledge_vs_arrival_structural_gap",
      "item_id": "knowledge_vs_arrival_structural_gap",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "知识与抵达的结构性断裂：即便所有圣贤和智者都曾指向天国，也没有一人真正抵达——焦渴是所有人的共同命运，而非悉达多个人的失败。这与前文'知识积累不能等于内在拥有'构成完整的逻辑闭合，指向婆罗门道路的终极局限。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@86-p13@125",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 86
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 125
            }
          },
          "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p107@0-p111@87:highlight:40",
      "reaction_id": "rx:Full_Content:src:c1:p107@0-p111@87:highlight:40",
      "type": "highlight",
      "thought": "这个笑与前文\"所有圣贤都没有抵达天国\"形成呼应——当所有人都在寻求答案时，悉达多已经知道答案不在任何人的教导里。但这种知道不是解脱，而是带着悲伤和嘲讽的处境。他同情那些仍然相信答案存在的人，也嘲讽包括自己在内的这个追逐。",
      "emitted_at_source_span_id": "src:c1:p107@0-p111@87",
      "primary_source_ref": {
        "source_span_id": "src:c1:p109@13-p109@30",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 109,
            "char_offset": 13
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 109,
            "char_offset": 30
          }
        },
        "quote": "他的笑声里一半是悲痛，一半是嘲讽。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "他的笑声里一半是悲痛，一半是嘲讽。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p115@0-p116@41:highlight:41",
      "reaction_id": "rx:Full_Content:src:c1:p115@0-p116@41:highlight:41",
      "type": "highlight",
      "thought": "这句话干脆到近乎冷酷。\"并不\"是否定，但比\"不是\"更主动——它暗示他曾被邀请，但他选择了拒绝。它将\"能力\"和\"追求\"分开：你能做到，但你不必以此为目的。这也是对乔文达那句\"很快就能学会\"的冷处理——学会又怎样？",
      "emitted_at_source_span_id": "src:c1:p115@0-p116@41",
      "primary_source_ref": {
        "source_span_id": "src:c1:p116@1-p116@14",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 116,
            "char_offset": 1
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 116,
            "char_offset": 14
          }
        },
        "quote": "在水面行走并不是我的追求。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "在水面行走并不是我的追求。",
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
    "ref_id": "concept:atman_becomes_own",
    "concept_key": "atman_becomes_own",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@481",
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
            "char_offset": 481
          }
        },
        "quote": "内在\"我\"之源泉，必须拥有自己的阿特曼",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "内在\"我\"之源泉，必须拥有自己的阿特曼"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:atman_not_learnable_obstacle_is_practice",
    "concept_key": "atman_not_learnable_obstacle_is_practice",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p90@0-p93@122",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 90,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 93,
            "char_offset": 122
          }
        },
        "quote": "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:brahman_cosmic_self",
    "concept_key": "brahman_cosmic_self",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p66@3-p66@34",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 3
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 34
          }
        },
        "quote": "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。",
        "role": "definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。"
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
    "ref_id": "thread:desire_as_fuel_of_samsara",
    "thread_key": "desire_as_fuel_of_samsara",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@193-p76@214",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 193
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 214
          }
        },
        "quote": "他好似猎人，在新的渴望中瞄准摆脱轮回的出口",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "他好似猎人，在新的渴望中瞄准摆脱轮回的出口"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:govinda_siddhartha_diverge_path",
    "thread_key": "govinda_siddhartha_diverge_path",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p78@0-p81@77",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 78,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 81,
            "char_offset": 77
          }
        },
        "quote": "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
        "role": "milestone",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:knowing_without_arriving_thread",
    "thread_key": "knowing_without_arriving_thread",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p13@86-p13@125",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 13,
            "char_offset": 86
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 13,
            "char_offset": 125
          }
        },
        "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。"
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
    "source_span_id": "src:c1:p7@230-p7@258",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 230
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 258
      }
    },
    "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p7@0-p7@10",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 10
      }
    },
    "quote": "而最爱他的人是乔文达",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p9@0-p9@26",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 26
      }
    },
    "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@107-p10@121",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 107
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 121
      }
    },
    "quote": "他充满渴望的精神容器仍未盛满",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@462-p11@480",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 462
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 480
      }
    },
    "quote": "其他一切都只是寻觅、走弯路和误入歧途",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@86-p13@125",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 86
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 125
      }
    },
    "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p21@104-p21@143",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 104
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 143
      }
    },
    "quote": "一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p34@0-p35@81",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 34,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 35,
        "char_offset": 81
      }
    },
    "quote": "心中充满恼怒和不安，恐惧和痛苦。透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  }
]
```
#### Score Rationale
- salience: `4`
- mainline_fidelity: `3`
- organization: `3`
- fidelity: `4`
- judge-provided overall: `4`
- final overall MQ: `3.5`
- judge reason: The snapshot strongly retains the three structural signals: (1) initial dissatisfaction with Brahman teachings is captured through 'inner_void_despite_outer_perfection' and 'spiritual_container_never_full' (his inability to find joy despite perfect external conditions); (2) ascetic self-denial and the Samana path is evidenced by the 'desire_as_fuel_of_samsara' thread and concepts about practicing physical austerities; (3) the failure of escape-through-self-erasure is retained in the key concept 'atman_not_learnable_obstacle_is_practice' (the most striking knowledge is that learning and practice are its greatest enemies) and the observation that no sage has ever fully arrived at heaven. However, the mainline fidelity is slightly weak—the detailed narrative arc of the three years with the Samanas and the specific departure moment are not deeply traced; the memory captures the philosophical conclusion but not the experiential journey that produced it. Organization is solid with active_attention, concept_digest, and thread_digest all functional, though reflective_digest remains empty, suggesting limited higher-order synthesis. The probe_review_focus on 'failure of escape-through-self-erasure before Buddha encounter' is materially retained via the Samana-to-Gautama transition that is being set up at this boundary point.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[0]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/xidaduo_private_zh__segment_1.md`.

### Probe 2 — MQ `4.00` — near 30%

#### Probe Position And Question
- target sentence: `c1-s752`
- boundary kind: `part-one close`
- why this point: Ends the first major movement through 乔达摩 and 觉醒, where Siddhartha refuses borrowed doctrine and turns toward self-experience.
- structural signals to check:
  - teacher refusal
  - self-experience over doctrine
  - leaving inherited teachings

#### Source Orientation
```text
   s750 / p178: 悉达多睁大双眼，望向四周，一抹微笑不禁在他脸上荡溢开来。
   s751 / p178: 一种从大梦中彻底苏醒的感觉贯穿他的周身直至脚趾。
>> s752 / p178: 他迈开双腿，如同一个完全清楚去向和使命的男人般疾步前行。
   s753 / p179: “哦，”他深吸了口气，释然道，“我不会再让悉达多溜走！
   s754 / p179: 不会再让阿特曼和尘世疾苦成为我思想和生命的中心。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:knowledge_insufficient_but_not_wrong",
      "item_id": "knowledge_insufficient_but_not_wrong",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "婆罗门知识的结构性局限：经典本身无误，诗句蕴含智慧，但知识积累不能等同于内在阿特曼的拥有——两者之间存在不可通约的断裂",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p11@462-p11@480",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 462
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 480
            }
          },
          "quote": "其他一切都只是寻觅、走弯路和误入歧途",
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
      "ref_id": "active_attention:knowledge_vs_arrival_structural_gap",
      "item_id": "knowledge_vs_arrival_structural_gap",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "知识与抵达的结构性断裂：即便所有圣贤和智者都曾指向天国，也没有一人真正抵达——焦渴是所有人的共同命运，而非悉达多个人的失败。这与前文'知识积累不能等于内在拥有'构成完整的逻辑闭合，指向婆罗门道路的终极局限。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@86-p13@125",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 86
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 125
            }
          },
          "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p184@0-p184@311:highlight:66",
      "reaction_id": "rx:Full_Content:src:c1:p184@0-p184@311:highlight:66",
      "type": "highlight",
      "thought": "三个问题构成孤独的精确诊断：从\"我在哪里\"到\"我与谁同在\"，最后到\"我用什么语言\"——归属感被逐层剥去，最后落到语言和存在的根底。",
      "emitted_at_source_span_id": "src:c1:p184@0-p184@311",
      "primary_source_ref": {
        "source_span_id": "src:c1:p184@285-p184@311",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 285
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 311
          }
        },
        "quote": "可是他，悉达多，他属于哪里？和谁分享生活？说谁的话？",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "可是他，悉达多，他属于哪里？和谁分享生活？说谁的话？",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p185@0-p185@111:highlight:67",
      "reaction_id": "rx:Full_Content:src:c1:p185@0-p185@111:highlight:67",
      "type": "highlight",
      "thought": "三个\"再也不\"构成一种不可逆的结构——不是\"也许不\"，不是\"暂时不\"，是结构性的永不回头。与前面那个\"拜自己为师\"的宣言合在一起，才完整：向内的认知转向，必须以向外的决绝出走为行动锚点。",
      "emitted_at_source_span_id": "src:c1:p185@0-p185@111",
      "primary_source_ref": {
        "source_span_id": "src:c1:p185@90-p185@111",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 185,
            "char_offset": 90
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 185,
            "char_offset": 111
          }
        },
        "quote": "他再也不回家，再也不回父亲那里，再不回去。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "他再也不回家，再也不回父亲那里，再不回去。",
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
    "ref_id": "concept:atman_becomes_own",
    "concept_key": "atman_becomes_own",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@481",
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
            "char_offset": 481
          }
        },
        "quote": "内在\"我\"之源泉，必须拥有自己的阿特曼",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "内在\"我\"之源泉，必须拥有自己的阿特曼"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:atman_not_learnable_obstacle_is_practice",
    "concept_key": "atman_not_learnable_obstacle_is_practice",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p90@0-p93@122",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 90,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 93,
            "char_offset": 122
          }
        },
        "quote": "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:brahman_cosmic_self",
    "concept_key": "brahman_cosmic_self",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p66@3-p66@34",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 3
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 34
          }
        },
        "quote": "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。",
        "role": "definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。"
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
    "ref_id": "thread:govinda_siddhartha_diverge_path",
    "thread_key": "govinda_siddhartha_diverge_path",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p78@0-p81@77",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 78,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 81,
            "char_offset": 77
          }
        },
        "quote": "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
        "role": "milestone",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p143@0-p143@55",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 55
          }
        },
        "quote": "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
        "role": "milestone",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p148@48-p148@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 48
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 87
          }
        },
        "quote": "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p184@244-p184@285",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 244
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 285
          }
        },
        "quote": "乔文达已皈依佛门，万千僧人是他的弟兄，他们着同样的僧服，信共同的信仰，说相同的话。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
      "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
      "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:desire_as_fuel_of_samsara",
    "thread_key": "desire_as_fuel_of_samsara",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@193-p76@214",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 193
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 214
          }
        },
        "quote": "他好似猎人，在新的渴望中瞄准摆脱轮回的出口",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "他好似猎人，在新的渴望中瞄准摆脱轮回的出口"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:govinda_ordained",
    "thread_key": "govinda_ordained",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p139@0-p139@42",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 139,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 139,
            "char_offset": 42
          }
        },
        "quote": "看哪，腼腆的乔文达也上前一步道：“我也愿皈依您及您的法义。”他祈求加入僧众并被接纳。",
        "role": "milestone",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "看哪，腼腆的乔文达也上前一步道：“我也愿皈依您及您的法义。”他祈求加入僧众并被接纳。"
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
    "source_span_id": "src:c1:p7@230-p7@258",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 230
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 258
      }
    },
    "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p7@0-p7@10",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 10
      }
    },
    "quote": "而最爱他的人是乔文达",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p9@0-p9@26",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 26
      }
    },
    "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@107-p10@121",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 107
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 121
      }
    },
    "quote": "他充满渴望的精神容器仍未盛满",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@462-p11@480",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 462
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 480
      }
    },
    "quote": "其他一切都只是寻觅、走弯路和误入歧途",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@86-p13@125",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 86
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 125
      }
    },
    "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p21@104-p21@143",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 104
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 143
      }
    },
    "quote": "一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p34@0-p35@81",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 34,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 35,
        "char_offset": 81
      }
    },
    "quote": "心中充满恼怒和不安，恐惧和痛苦。透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
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
- judge reason: The snapshot strongly retains the three departure structures (from father, from Samanas, from Gotama) and the central declaration '我要拜自己为师' (I will take myself as teacher). The teacher-refusal dialogue with Gotama is preserved with Siddhartha's argument that Gotama's doctrine cannot transmit the Buddha's own experience ('没人能通过法义得到解脱'). The structural signal of 'self-experience over doctrine' is well-represented in the active_items (inner_void_despite_outer_perfection, spiritual_container_never_full, atman_not_learnable_obstacle_is_practice). The Govinda-thread is captured across multiple milestones showing their divergence. However, the reading window metadata indicates coverage through chapters 3-14 (including 迦摩罗, 尘世间, 轮回, etc.), yet the captured memory content appears to end near the '觉醒' chapter conclusion, not reaching Part Two material. This creates a gap between declared coverage and actual retained content for this probe point.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[1]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/xidaduo_private_zh__segment_1.md`.

### Probe 3 — MQ `2.75` — near 60%

#### Probe Position And Question
- target sentence: `c1-s1532`
- boundary kind: `worldly-life collapse`
- why this point: Ends 轮回 before 在河边, closing Kamala/Kamaswami/worldly life and the crisis that prepares river rebirth.
- structural signals to check:
  - Kamala and Kamaswami worldly life
  - disgust, despair, and collapse of worldly pursuit
  - transition toward river rebirth

#### Source Orientation
```text
   s1530 / p335: 悉达多灵魂的苦修之轮、思想之轮、分辨之轮长久旋转着，依旧旋转着，但它已渐缓，松动乃至接近静止。
   s1531 / p335: 如同濒死的树干因潮气侵袭、注满而腐朽，世俗和惰性侵入并充满悉达多的灵魂。
>> s1532 / p335: 它不再轻盈，反而疲惫、麻痹。
   s1533 / p335: 同时，他的感官却活跃起来，它学到许多，体验许多。
   s1534 / p336: 悉达多学会做生意，发号施令，寻欢作乐。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:knowledge_insufficient_but_not_wrong",
      "item_id": "knowledge_insufficient_but_not_wrong",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "婆罗门知识的结构性局限：经典本身无误，诗句蕴含智慧，但知识积累不能等同于内在阿特曼的拥有——两者之间存在不可通约的断裂",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p11@462-p11@480",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 462
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 480
            }
          },
          "quote": "其他一切都只是寻觅、走弯路和误入歧途",
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
      "ref_id": "active_attention:knowledge_vs_arrival_structural_gap",
      "item_id": "knowledge_vs_arrival_structural_gap",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "知识与抵达的结构性断裂：即便所有圣贤和智者都曾指向天国，也没有一人真正抵达——焦渴是所有人的共同命运，而非悉达多个人的失败。这与前文'知识积累不能等于内在拥有'构成完整的逻辑闭合，指向婆罗门道路的终极局限。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@86-p13@125",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 86
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 125
            }
          },
          "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p346@0-p347@87:highlight:135",
      "reaction_id": "rx:Full_Content:src:c1:p346@0-p347@87:highlight:135",
      "type": "highlight",
      "thought": "连接前文\"这游戏叫做轮回\"的\"游戏\"——这里他用来质问自己拥有芒果树和花园这件事，同样是游戏。而且是更基础的、在他走入红尘之前的那层游戏：把世界当真，把拥有当真。轮回是一个游戏，这个\"拥有\"是嵌套在轮回里的更小的游戏。",
      "emitted_at_source_span_id": "src:c1:p346@0-p347@87",
      "primary_source_ref": {
        "source_span_id": "src:c1:p346@106-p346@130",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 346,
            "char_offset": 106
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 346,
            "char_offset": 130
          }
        },
        "quote": "这是真实的，必要的吗？难道这不是一场愚蠢的游戏？",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "这是真实的，必要的吗？难道这不是一场愚蠢的游戏？",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p348@0-p349@93:retrospect:136",
      "reaction_id": "rx:Full_Content:src:c1:p348@0-p349@93:retrospect:136",
      "type": "retrospect",
      "thought": "\"失却的痛苦中欣喜\"——这里不是矛盾，而是清醒。她知道那是最后一次，所以每一个动作同时是告别和彻底。痛苦和欣喜并行，因为两个都是真的。",
      "emitted_at_source_span_id": "src:c1:p348@0-p349@93",
      "primary_source_ref": {
        "source_span_id": "src:c1:p348@112-p348@146",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 348,
            "char_offset": 112
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 348,
            "char_offset": 146
          }
        },
        "quote": "她在失却的痛苦中欣喜，她能最后一次把他紧贴胸口，再一次彻底被他征服。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "她在失却的痛苦中欣喜，她能最后一次把他紧贴胸口，再一次彻底被他征服。",
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
    "ref_id": "concept:atman_becomes_own",
    "concept_key": "atman_becomes_own",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@481",
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
            "char_offset": 481
          }
        },
        "quote": "内在\"我\"之源泉，必须拥有自己的阿特曼",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "内在\"我\"之源泉，必须拥有自己的阿特曼"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:atman_not_learnable_obstacle_is_practice",
    "concept_key": "atman_not_learnable_obstacle_is_practice",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p90@0-p93@122",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 90,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 93,
            "char_offset": 122
          }
        },
        "quote": "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:brahman_cosmic_self",
    "concept_key": "brahman_cosmic_self",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p66@3-p66@34",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 3
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 34
          }
        },
        "quote": "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。",
        "role": "definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。"
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
    "ref_id": "thread:govinda_siddhartha_diverge_path",
    "thread_key": "govinda_siddhartha_diverge_path",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p78@0-p81@77",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 78,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 81,
            "char_offset": 77
          }
        },
        "quote": "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
        "role": "milestone",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p143@0-p143@55",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 55
          }
        },
        "quote": "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
        "role": "milestone",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p148@48-p148@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 48
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 87
          }
        },
        "quote": "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p184@244-p184@285",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 244
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 285
          }
        },
        "quote": "乔文达已皈依佛门，万千僧人是他的弟兄，他们着同样的僧服，信共同的信仰，说相同的话。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
      "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
      "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:atman_self_ungraspable_by_thought",
    "thread_key": "atman_self_ungraspable_by_thought",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p195@201-p195@233",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 201
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 233
          }
        },
        "quote": "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:desire_as_fuel_of_samsara",
    "thread_key": "desire_as_fuel_of_samsara",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@193-p76@214",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 193
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 214
          }
        },
        "quote": "他好似猎人，在新的渴望中瞄准摆脱轮回的出口",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "他好似猎人，在新的渴望中瞄准摆脱轮回的出口"
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
    "source_span_id": "src:c1:p7@230-p7@258",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 230
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 258
      }
    },
    "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p7@0-p7@10",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 10
      }
    },
    "quote": "而最爱他的人是乔文达",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p9@0-p9@26",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 26
      }
    },
    "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@107-p10@121",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 107
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 121
      }
    },
    "quote": "他充满渴望的精神容器仍未盛满",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@462-p11@480",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 462
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 480
      }
    },
    "quote": "其他一切都只是寻觅、走弯路和误入歧途",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@86-p13@125",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 86
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 125
      }
    },
    "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p21@104-p21@143",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 104
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 143
      }
    },
    "quote": "一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p34@0-p35@81",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 34,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 35,
        "char_offset": 81
      }
    },
    "quote": "心中充满恼怒和不安，恐惧和痛苦。透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  }
]
```
#### Score Rationale
- salience: `3`
- mainline_fidelity: `2`
- organization: `2`
- fidelity: `4`
- judge-provided overall: `1`
- final overall MQ: `2.75`
- judge reason: The snapshot retains strong fidelity to Part One early material (devotion structure, inner void, atman concepts) but its active_attention and thread_digest are dominated by chapters 3–5 content. The three structural signals for this probe point — (1) Kamala and Kamaswami worldly life, (2) disgust/despair/collapse of worldly pursuit, (3) transition toward river rebirth — are largely absent from the snapshot's organized threads. The recent_reactions do capture Kamala's final encounter, the robin dream, and the pregnancy reveal, but these are logged as isolated reactions rather than being integrated into a thread or concept that represents Siddhartha's own collapse. The snapshot does not meaningfully retain the robin's death dream, Siddhartha sitting at the mango tree questioning his possessions, the gambling addiction, or the decisive nightly departure — the very material that closes 轮回 and initiates the river rebirth. The reader cannot tell from this snapshot that Siddhartha has just experienced a spiritual/psychological collapse requiring river renewal.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[2]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/xidaduo_private_zh__segment_1.md`.

### Probe 4 — MQ `2.25` — near 85%

#### Probe Position And Question
- target sentence: `c1-s2067`
- boundary kind: `chapter close`
- why this point: Ends 船夫 before 儿子, after the river/Vasudeva listening frame and Kamala's death introduce fatherhood.
- structural signals to check:
  - river and Vasudeva listening
  - Kamala death
  - son emergence and fatherhood transition

#### Source Orientation
```text
   s2065 / p428: 河水无所不知，求教河水你可学会一切。
   s2066 / p428: 你瞧，你已学会足履实地，学会沉寂并向深处探寻。
>> s2067 / p428: 富有而高贵的悉达多要成为摆渡人。
   s2068 / p428: 博学的婆罗门悉达多要成为船夫。
   s2069 / p428: 这也是河水所示。
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:knowledge_insufficient_but_not_wrong",
      "item_id": "knowledge_insufficient_but_not_wrong",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "婆罗门知识的结构性局限：经典本身无误，诗句蕴含智慧，但知识积累不能等同于内在阿特曼的拥有——两者之间存在不可通约的断裂",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p11@462-p11@480",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 462
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 480
            }
          },
          "quote": "其他一切都只是寻觅、走弯路和误入歧途",
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
      "ref_id": "active_attention:knowledge_vs_arrival_structural_gap",
      "item_id": "knowledge_vs_arrival_structural_gap",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "知识与抵达的结构性断裂：即便所有圣贤和智者都曾指向天国，也没有一人真正抵达——焦渴是所有人的共同命运，而非悉达多个人的失败。这与前文'知识积累不能等于内在拥有'构成完整的逻辑闭合，指向婆罗门道路的终极局限。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@86-p13@125",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 86
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 125
            }
          },
          "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p461@0-p465@143:highlight:185",
      "reaction_id": "rx:Full_Content:src:c1:p461@0-p465@143:highlight:185",
      "type": "highlight",
      "thought": "这里的\"不语\"与悉达多之前的\"不语\"形成完整的呼应——他在认出\"是悉达多却又不是\"时选择沉默，她也在这最想说话的时刻失去了言语。两个人用同样的方式完成了最后的交流：不说。",
      "emitted_at_source_span_id": "src:c1:p461@0-p465@143",
      "primary_source_ref": {
        "source_span_id": "src:c1:p465@63-p465@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 465,
            "char_offset": 63
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 465,
            "char_offset": 87
          }
        },
        "quote": "她想把这告诉他，可舌头却不听使唤。她默默望着他。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "她想把这告诉他，可舌头却不听使唤。她默默望着他。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p467@0-p467@110:highlight:186",
      "reaction_id": "rx:Full_Content:src:c1:p467@0-p467@110:highlight:186",
      "type": "highlight",
      "thought": "时间拟人化：不是他在回忆时间，而是时间在触摸他、簇拥他——一种被动的、被命运浸润的感受。这与前面\"不语\"和\"同样好\"的情感重量形成反差，这里是更宽广、更沉默的承接。",
      "emitted_at_source_span_id": "src:c1:p467@0-p467@110",
      "primary_source_ref": {
        "source_span_id": "src:c1:p467@60-p467@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 467,
            "char_offset": 60
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 467,
            "char_offset": 87
          }
        },
        "quote": "他倾听河水奔涌，沉浸在往事中，被一生的时光触摸，簇拥。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "他倾听河水奔涌，沉浸在往事中，被一生的时光触摸，簇拥。",
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
    "ref_id": "concept:atman_becomes_own",
    "concept_key": "atman_becomes_own",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@481",
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
            "char_offset": 481
          }
        },
        "quote": "内在\"我\"之源泉，必须拥有自己的阿特曼",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "内在\"我\"之源泉，必须拥有自己的阿特曼"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:atman_not_learnable_obstacle_is_practice",
    "concept_key": "atman_not_learnable_obstacle_is_practice",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p90@0-p93@122",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 90,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 93,
            "char_offset": 122
          }
        },
        "quote": "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:brahman_cosmic_self",
    "concept_key": "brahman_cosmic_self",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p66@3-p66@34",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 3
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 34
          }
        },
        "quote": "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。",
        "role": "definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。"
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
    "ref_id": "thread:govinda_siddhartha_diverge_path",
    "thread_key": "govinda_siddhartha_diverge_path",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p78@0-p81@77",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 78,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 81,
            "char_offset": 77
          }
        },
        "quote": "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
        "role": "milestone",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p143@0-p143@55",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 55
          }
        },
        "quote": "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
        "role": "milestone",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p148@48-p148@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 48
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 87
          }
        },
        "quote": "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p184@244-p184@285",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 244
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 285
          }
        },
        "quote": "乔文达已皈依佛门，万千僧人是他的弟兄，他们着同样的僧服，信共同的信仰，说相同的话。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
      "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
      "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:atman_self_ungraspable_by_thought",
    "thread_key": "atman_self_ungraspable_by_thought",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p195@201-p195@233",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 201
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 233
          }
        },
        "quote": "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:child_vs_eternity_contrast",
    "thread_key": "child_vs_eternity_contrast",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p447@202-p447@214",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 447,
            "char_offset": 202
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 447,
            "char_offset": 214
          }
        },
        "quote": "他死了和小孩有什么关系？",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "他死了和小孩有什么关系？"
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
    "source_span_id": "src:c1:p7@230-p7@258",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 230
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 258
      }
    },
    "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p7@0-p7@10",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 10
      }
    },
    "quote": "而最爱他的人是乔文达",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p9@0-p9@26",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 26
      }
    },
    "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@107-p10@121",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 107
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 121
      }
    },
    "quote": "他充满渴望的精神容器仍未盛满",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@462-p11@480",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 462
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 480
      }
    },
    "quote": "其他一切都只是寻觅、走弯路和误入歧途",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@86-p13@125",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 86
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 125
      }
    },
    "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p21@104-p21@143",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 104
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 143
      }
    },
    "quote": "一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p34@0-p35@81",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 34,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 35,
        "char_offset": 81
      }
    },
    "quote": "心中充满恼怒和不安，恐惧和痛苦。透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  }
]
```
#### Score Rationale
- salience: `2`
- mainline_fidelity: `2`
- organization: `2`
- fidelity: `3`
- judge-provided overall: `1`
- final overall MQ: `2.25`
- judge reason: The snapshot retains three recent_reactions correctly sourced from the probe window (Kamala's silence '不语', Siddhartha listening to the river '被一生的时光触摸', the child sleeping vs. the pyre being built), but the structural_signals_to_check for this probe point—river and Vasudeva listening, Kamala's death, and son emergence/fatherhood transition—are only captured as isolated reaction highlights, not as organized thematic or narrative knowledge. The active_attention_digest and concept_digest are dominated entirely by Part 1 material (devotion_structure, inner_void, spiritual_container, etc.) that predates the probe point by 85% of the book. The reader's active focus has not been updated to reflect that this is the 船夫 chapter ending, that Kamala has died, that the son has appeared, and that Siddhartha is now facing fatherhood—these central events are present as raw reaction anchors but are not consolidated into coherent structural memory about what this part of the book means.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[3]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/xidaduo_private_zh__segment_1.md`.

### Probe 5 — MQ `2.50` — window end

#### Probe Position And Question
- target sentence: `c1-s2417`
- boundary kind: `window end`
- why this point: Ends the full active window at the final integration, where the river voices, unity, reconciliation, and final transmission come together.
- structural signals to check:
  - 唵 and final integration
  - river voices and unity
  - reconciliation and final transmission

#### Source Orientation
```text
   s2415 / p497: 你希望我像你一样虔敬、温顺、明智！
   s2416 / p497: 可是我，你听着，我要让你痛苦。
>> s2417 / p497: 我宁愿做扒手、杀人犯、下地狱，也不愿做你！
   s2418 / p497: 我恨你。
   s2419 / p497: 你不是我父亲，哪怕你做过我母亲十次的姘夫！
```

#### Active Attention

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:knowledge_insufficient_but_not_wrong",
      "item_id": "knowledge_insufficient_but_not_wrong",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "婆罗门知识的结构性局限：经典本身无误，诗句蕴含智慧，但知识积累不能等同于内在阿特曼的拥有——两者之间存在不可通约的断裂",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p11@462-p11@480",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 462
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 11,
              "char_offset": 480
            }
          },
          "quote": "其他一切都只是寻觅、走弯路和误入歧途",
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
      "ref_id": "active_attention:knowledge_vs_arrival_structural_gap",
      "item_id": "knowledge_vs_arrival_structural_gap",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "知识与抵达的结构性断裂：即便所有圣贤和智者都曾指向天国，也没有一人真正抵达——焦渴是所有人的共同命运，而非悉达多个人的失败。这与前文'知识积累不能等于内在拥有'构成完整的逻辑闭合，指向婆罗门道路的终极局限。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p13@86-p13@125",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 86
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 13,
              "char_offset": 125
            }
          },
          "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "active_attention:govinda_shadow_devotion",
      "item_id": "govinda_shadow_devotion",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@230-p7@258",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 230
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 258
            }
          },
          "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
          "role": "support",
          "resolution": {
            "status": "matched",
            "method": "exact_text",
            "match_count": 1
          }
        },
        {
          "source_span_id": "src:c1:p210@0-p214@189",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 210,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 214,
              "char_offset": 189
            }
          },
          "quote": "为了这个目标，悉达多踏遍城邑，走街串巷……他让那位伙计为他刮了胡须，剪了头发并敷了上好的头油。",
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
      "ref_id": "active_attention:devotion_structure_this_unit",
      "item_id": "devotion_structure_this_unit",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p7@0-p7@10",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 7,
              "char_offset": 10
            }
          },
          "quote": "而最爱他的人是乔文达",
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
      "ref_id": "active_attention:inner_void_despite_outer_perfection",
      "item_id": "inner_void_despite_outer_perfection",
      "attention_tags": [
        "focus",
        "motif"
      ],
      "statement": "外部圆满/内部空洞的对照：所有人都爱他、仪式完美执行，但\"无法让自己喜悦\"——这种空虚不是匮乏而是过载：婆罗门教义越多，灵魂越不安",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p9@0-p9@26",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 9,
              "char_offset": 26
            }
          },
          "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
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
      "ref_id": "active_attention:spiritual_container_never_full",
      "item_id": "spiritual_container_never_full",
      "attention_tags": [
        "focus",
        "interpretation"
      ],
      "statement": "精神容器的结构性饥饿：婆罗门教义越渊博，灵魂越不安；爱、仪式、知识全部无法盛满这个容器；这是存在性的、结构性的焦渴，而非匮乏性的",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p10@107-p10@121",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 107
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 10,
              "char_offset": 121
            }
          },
          "quote": "他充满渴望的精神容器仍未盛满",
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
      "ref_id": "reaction:rx:Full_Content:src:c1:p529@0-p533@115:highlight:209",
      "reaction_id": "rx:Full_Content:src:c1:p529@0-p533@115:highlight:209",
      "type": "highlight",
      "thought": "「不再听到哀，听到笑」——这个并列句揭示了修行的核心：不是学会了某种高级的听法，而是彻底停止了选择。所有的哀与笑同时涌来，而灵魂不再被任何一种占据。统一不是综合，而是不再区分。这个「唵」是取消区别的结果，不是添加进来的东西。",
      "emitted_at_source_span_id": "src:c1:p529@0-p533@115",
      "primary_source_ref": {
        "source_span_id": "src:c1:p529@172-p529@263",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 529,
            "char_offset": 172
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 529,
            "char_offset": 263
          }
        },
        "quote": "当他专注于河水咆哮的交响，当他不再听到哀，听到笑，当他的灵魂不再执念于一种声音，自我不再被占据，而是倾听一切，倾听整体和统一时，这伟大的交响，凝成了一个字，这个字是“唵”，意为圆满。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "当他专注于河水咆哮的交响，当他不再听到哀，听到笑，当他的灵魂不再执念于一种声音，自我不再被占据，而是倾听一切，倾听整体和统一时，这伟大的交响，凝成了一个字，这个字是“唵”，意为圆满。",
      "projection_role": "visible_trace",
      "support_status": "visible_trace",
      "visible_trace_support": true,
      "current_support": false,
      "projection_warning": "visible_trace_not_semantic_memory"
    },
    {
      "ref_id": "reaction:rx:Full_Content:src:c1:p529@0-p533@115:highlight:210",
      "reaction_id": "rx:Full_Content:src:c1:p529@0-p533@115:highlight:210",
      "type": "highlight",
      "thought": "瓦酥迪瓦的离开与悉达多的觉醒同时完成。他不是被动的旁观者，而是引导者——引导到无需再引导的那一刻。「做了太久的船夫」呼应了前文船夫作为过渡性角色的定位：河流是通道，不是居所。当悉达多已能在河中听见「唵」，船夫的历史使命便完结了。",
      "emitted_at_source_span_id": "src:c1:p529@0-p533@115",
      "primary_source_ref": {
        "source_span_id": "src:c1:p533@48-p533@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 533,
            "char_offset": 48
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 533,
            "char_offset": 97
          }
        },
        "quote": "我在等候这一时刻，亲爱的，现在它终于来临。让我走吧，我已等候良久，我已做了太久的船夫。现在已结束。",
        "role": "reaction_anchor",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      "source_quote": "我在等候这一时刻，亲爱的，现在它终于来临。让我走吧，我已等候良久，我已做了太久的船夫。现在已结束。",
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
    "ref_id": "concept:atman_becomes_own",
    "concept_key": "atman_becomes_own",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p11@0-p11@481",
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
            "char_offset": 481
          }
        },
        "quote": "内在\"我\"之源泉，必须拥有自己的阿特曼",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "内在\"我\"之源泉，必须拥有自己的阿特曼"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:atman_not_learnable_obstacle_is_practice",
    "concept_key": "atman_not_learnable_obstacle_is_practice",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p90@0-p93@122",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 90,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 93,
            "char_offset": 122
          }
        },
        "quote": "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:brahman_cosmic_self",
    "concept_key": "brahman_cosmic_self",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p66@3-p66@34",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 3
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 66,
            "char_offset": 34
          }
        },
        "quote": "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。",
        "role": "definition",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "Brahman，在奥义书中指称至高存在或至高自我，即宇宙自我。"
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
    "ref_id": "thread:govinda_siddhartha_diverge_path",
    "thread_key": "govinda_siddhartha_diverge_path",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p78@0-p81@77",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 78,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 81,
            "char_offset": 77
          }
        },
        "quote": "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
        "role": "milestone",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p143@0-p143@55",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 143,
            "char_offset": 55
          }
        },
        "quote": "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
        "role": "milestone",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p148@48-p148@87",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 48
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 148,
            "char_offset": 87
          }
        },
        "quote": "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p184@244-p184@285",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 244
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 184,
            "char_offset": 285
          }
        },
        "quote": "乔文达已皈依佛门，万千僧人是他的弟兄，他们着同样的僧服，信共同的信仰，说相同的话。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "“你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……",
      "悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”",
      "这时，乔文达出离僧团，再次拥抱了他青年时代的朋友，之后便加入了新皈依者的行列。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:atman_self_ungraspable_by_thought",
    "thread_key": "atman_self_ungraspable_by_thought",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p195@201-p195@233",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 201
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 195,
            "char_offset": 233
          }
        },
        "quote": "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:child_vs_eternity_contrast",
    "thread_key": "child_vs_eternity_contrast",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p447@202-p447@214",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 447,
            "char_offset": 202
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 447,
            "char_offset": 214
          }
        },
        "quote": "他死了和小孩有什么关系？",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "他死了和小孩有什么关系？"
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
    "source_span_id": "src:c1:p7@230-p7@258",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 230
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 258
      }
    },
    "quote": "他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p7@0-p7@10",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 7,
        "char_offset": 10
      }
    },
    "quote": "而最爱他的人是乔文达",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p9@0-p9@26",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 9,
        "char_offset": 26
      }
    },
    "quote": "可是他，悉达多，却无法让自己喜悦，无法让自己略有兴致",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p10@107-p10@121",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 107
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 10,
        "char_offset": 121
      }
    },
    "quote": "他充满渴望的精神容器仍未盛满",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p11@462-p11@480",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 462
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 11,
        "char_offset": 480
      }
    },
    "quote": "其他一切都只是寻觅、走弯路和误入歧途",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p13@86-p13@125",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 86
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 13,
        "char_offset": 125
      }
    },
    "quote": "在所有教诲过他的圣贤和智者中，也没有一人完全抵达过天国，完全消除过永恒的焦渴。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p21@104-p21@143",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 104
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 21,
        "char_offset": 143
      }
    },
    "quote": "一种由无声的激情、不惜一切去献身、无情的肉体灭绝构成的灼热气息回旋在他们周身。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p34@0-p35@81",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 34,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 35,
        "char_offset": 81
      }
    },
    "quote": "心中充满恼怒和不安，恐惧和痛苦。透过窗子，他瞭望月光中，星光中，黑暗中的悉达多。",
    "role": "support",
    "resolution": {
      "status": "fallback_unit_span",
      "method": "quote_not_found",
      "match_count": 0
    }
  }
]
```
#### Score Rationale
- salience: `2`
- mainline_fidelity: `2`
- organization: `3`
- fidelity: `3`
- judge-provided overall: `2`
- final overall MQ: `2.5`
- judge reason: The snapshot retains the beginning-of-book material (devotion structure, inner void, spiritual container hunger) with good fidelity, and the recent_reactions section does capture the three probe structural signals—'唵' condensing from the river's symphony, Vasudeva's departure after his 'long career as ferryman,' and '我要去林中，去融入统一' with radiance. However, the active_focus_digest, concept_digest, and thread_digest are almost entirely anchored to the first chapter's opening scenes, leaving the book's mainline arc (Kamalila, city life, gambling and decadence, near-suicide by the river, Vasudeva as teacher, the son's arrival and departure, the final communion) severely underrepresented or absent. The structural signals from the probe_review_focus are present only as isolated reactions rather than as organizing principles in the digest, which is a notable organizational drift toward the opening material.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[4]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/xidaduo_private_zh__segment_1.md`.

## Scoring Interpretation

This section explains how the trace above becomes the Eval-1 scores for this window.

### Selective Legibility

- Formula used by the run report: `(exact_match + focused_hit) / note_case_count = (1 + 7) / 20 = 0.4000`.
- Incidental cover count `0` is visible support, not recall credit.
- Miss count `12` means the reaction timeline either did not produce a strict source-overlap candidate for the note target or the judge rejected the admitted candidate.
- Unlocatable reaction count `0` is diagnostic only and never becomes a match.

### Memory Quality

- Window MQ is the average of the five probe-time overall scores: 3.5, 4, 2.75, 2.25, 2.5 -> `3.00`.
- The probe state sections above show what the mechanism had available at scoring time; final runtime state is not substituted for probe-time evidence.

### Callback / FVI

- Reaction audit reviewed `211` visible reactions: `47` grounded, `25` weak, `0` FVI, `139` local-only.
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
