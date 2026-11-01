# Eval-1 Window Audit Dossier: 活出生命的意义

This page is a reviewer audit dossier for one Eval-1 Retry1 window. It is evidence interpretation only: no eval was run to produce this page, no catalog entry is created here, and no product-quality or formal-authority claim is made.

## Window Verdict

活出生命的意义 shows partial Lane A selective legibility: exact/focused evidence is real, but misses remain the dominant outcome. Lane B memory is comparatively healthy at MQ 3.70, with the main review work concentrated on structural omissions rather than total loss. Callback audit records 19 grounded and 9 weak callbacks, with 0 FVI; these are callback-quality diagnostics, not proof of product-level reading quality.

| Channel | Result | Reviewer boundary |
| --- | --- | --- |
| Lane A selective legibility | recall `0.3750` over `40` note cases | exact/focused count toward recall; incidental and miss do not |
| Lane B Memory Quality | average `3.70` over `5` probes | evaluates state retention/organization, not visible reaction quality |
| Callback/FVI | grounded `19`, weak `9`, FVI `0` | visible callback correctness is separate from memory quality |

## Window-Specific Reading

- Lane A pattern: `15` of `40` note cases received recall credit, while `23` remained misses. The dominant miss mode below should be read as a candidate-admission / visible-reaction coverage issue, not as proof that the mechanism understood nothing about those notes.
- Lane B strongest probe: probe `2` at `near 40%` scored `4.25` because The snapshot retains the central love/wife spiritual resource clearly via three key reactions: the '不论真实与否' anchor quote about wife's brightness, the discern on love transcending physical presence, and the bird-as-witness moment at the very end. The '爱是人类终身追求…
- Lane B weakest probe: probe `3` at `near 60%` scored `3.25`; main reviewer concern: the structural signal of '被囚禁处境中的主动选择' is treated as a surface plot event rather than as the paradigmatic moral reversal it represents — the snapshot does not capture that Frankl's most 'active' choice under captivity was precisely the choice NOT to act. The …
- Callback/FVI pattern: no FVI was recorded in this window, but weak callbacks still need inspection because they show where the model gestures at continuity without tight visible grounding.

## Evidence Map

| Evidence | Path | What to inspect |
| --- | --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/summary/aggregate.json` (`present`) | label counts, recall, unlocatable diagnostics |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases` (`present`) | per-note source targets, candidates, judge labels |
| Lane A rebuilt bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/rebuilt_bundles/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/normalized_eval_bundle.json` (`present`) | normalized visible reactions used for matching |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/aggregate.json` (`present`) | MQ and callback totals |
| Lane B MQ rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` (`present`) | probe scores and judge reasons |
| Lane B reaction audit rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/reaction_audit_results.jsonl` (`present`) | grounded/weak/FVI/local-only labels |
| Probe snapshots | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` (`present`) | probe-time state evidence; primary MQ audit source |
| Normalized eval bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json` (`present`) | visible reactions and memory summaries |
| Runtime state | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime` (`present`) | final run state; useful for diagnosis, not a substitute for probe-time snapshots |

## Lane A Selective Legibility Audit

Lane A asks whether visible reactions recover user-selected note spans under strict `segment_source_v1` source-span overlap. Text similarity and semantic similarity are not candidate-admission paths.

| Label | Count | Reviewer interpretation |
| --- | ---: | --- |
| `exact_match` | 7 | exact: the reaction span is identical to the aligned note span, so it is credited without semantic judging. |
| `focused_hit` | 8 | focused: the admitted span overlaps the note target and judge says the reaction captures the note-level meaning closely enough for recall credit. |
| `incidental_cover` | 2 | incidental: the reaction touches the note span but its attention is elsewhere; useful as support, not recall credit. |
| `miss` | 23 | miss: no credit; either no strict source-overlap candidate existed or admitted candidates did not satisfy focused recall. |
| `unlocatable diagnostic` | 1 | recorded as locator evidence only; never credited as candidate/match/recall |

### Case-Level Evidence

#### `e0002` — `exact_match`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002`
- source target: p14@110-155: 每当看到狱友吸烟时，我们就知道他已失去了生活下去的勇气。勇气一旦失去，几乎就不可能再挽回。
- matched reaction: `rx:Full_Content:src:c1:p10@265-p14@155:discern:14`
- reaction text: 前文已经揭示了生存的三重斗争：面包、生活、朋友。这里的"勇气"是第四重——也是最内在、最不可逆的一重。前三重是外向的争夺，而勇气是内在的熄灭。并且"几乎就不可能再挽回"与前文"为了生存，他们可以使用一切手段"构成反向呼应：能活下来的人已经耗尽了几乎所有的勇气筹码。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0002.json`

#### `e0015` — `exact_match`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015`
- source target: p137@186-215: 犯人们觉得自己的生死取决于看守的情绪，这使得他们更不像人。
- matched reaction: `rx:Full_Content:src:c1:p137@0-p137@215:highlight:89`
- reaction text: 这与前文"犯人成了名副其实的号码"形成不同层面的剥除：号码是制度的抽象化，这里是权力的任意化。两种剥除叠加——制度把你变成数字，狱卒的情绪让你觉得连数字都不如。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0015.json`

#### `e0003` — `focused_hit`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003`
- source target: p46@51-78: “是的，人可以习惯任何事物，但请不要问我们是如何习惯的
- matched reaction: `rx:Full_Content:src:c1:p43@0-p46@138:retrospect:25`
- reaction text: 「不要问我们如何习惯的」这句话值得细读。它不是在否认适应本身，而是拒绝说出适应的机制——那个过程一旦被言说，就会暴露某种让人无法直视的东西。同时「仍处于心理反应的第一阶段」这句话暗示后面还有更深的阶段，这些更深的阶段里会发生什么，叙述者没有说，但这本身就是一个悬置的威胁。
- source-span relation: `candidate_contains_note; coverage=1.00`
- judge / runner reason: The reaction precisely centers on the core phrase from the note ('不要问我们如何习惯的') and provides a substantive interpretation of its meaning: the refusal to articulate the adaptation mechanism because doing so would reveal something unbearable. The analysis genuinely engages with the note's central idea rather than merely …
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0003.json`

#### `e0004` — `focused_hit`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004`
- source target: p61@0-87: 冷漠、迟钝、对任何事情都漠不关心是囚徒第二阶段心理反应的表现，这些症状最终会使他们对每天每时频繁发生的酷刑折磨无动于衷。正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。
- matched reaction: `rx:Full_Content:src:c1:p58@0-p61@87:highlight:34`
- reaction text: 这里把心理死亡从损耗的副作用重新框架为生存的适应性策略。"冷漠外壳"这个词暗示的不是情感的丧失，而是一层保护层的形成——叙述者不再把麻木当作问题，而是当作在酷刑频繁发生之地唯一可靠的防线。
- source-span relation: `note_contains_candidate; coverage=0.31`
- judge / runner reason: The reaction directly interprets and elaborates on the overlapped source span ("正是由于这种冷漠外壳的包裹，囚徒们才能真正地保护自己。"), reframing it as a protective strategy, which captures the essential content of that span.
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0004.json`

#### `e0014` — `incidental_cover`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014`
- source target: p132@0-99: 如同绵羊胆怯地缩到羊群当中一样，我们每个人也都尽量挤到队列中间去。这样做可以少挨看守揍，他们就在队伍的前后左右看着我们。中间的位置还有一个好处，就是不易被寒风吹到。因此，为了保全自己就不得不融入人群
- matched reaction: `rx:Full_Content:src:c1:p132@0-p132@173:retrospect:83`
- reaction text: "如同绵羊"——前面p131已经用过"这群羊"，这里再次出现同一个意象，但这次有了身体行为的填充：不只是被动地被定义为羊，而是主动地执行羊的动作。羊的隐喻在积累。
- source-span relation: `note_contains_candidate; coverage=0.33`
- judge / runner reason: The reaction's quoted span (char 0-33) is contained within the note and does overlap, but the reaction only analyzes the sheep metaphor as a literary device accumulating across pages. It ignores the note's core content about the practical survival logic (avoiding guard beatings, staying warm) and the explicit conclusi…
- Reviewer reading: this is not recall success. The mechanism touched nearby or overlapping text but did not make the human-note idea its main object.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0014.json`

#### `e0005` — `miss`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0005`
- source target: p62@148-195: 这时，最痛的不是肉体 （这样的惩罚对成人和儿童都一样），而是不公正和不可理喻对心理造成的伤害。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0005.json`

#### `e0007` — `miss`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0007`
- source target: p100@42-133: 爱是人类终身追求的最高目标。我理解了诗歌、思想和信仰所传达的伟大秘密的真正含义：拯救人类要通过爱与被爱。我知道世界上一无所有的人只要有片刻的时间思念爱人，那么他就可以领悟幸福的真谛。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0007.json`

#### `e0008` — `miss`

- note case id: `huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0008`
- source target: p100@217-232: 天使存在于无比美丽的永恒思念中
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_huochu/note_cases/huochu_shengming_de_yiyi_private_zh__huochu_shengming_de_yiyi_private_zh_personal_notes__e0008.json`

### Miss-Mode Aggregation

- `no_source_overlap_candidate`: 23. No visible reaction entered the candidate set under strict source-span overlap. Do not infer a hidden semantic hit from thematic proximity.

### Unlocatable Source-Locator Diagnostics

- `rx:Chapter_1:src:c1:p239@287-p239@287:retrospect:1`

These diagnostics are intentionally not counted as matches. They identify reactions whose source location could not be turned into a usable `segment_source_v1` candidate for Lane A matching.

## Lane B Memory Quality Audit

Lane B asks whether probe-time memory state retains salient, source-faithful, organized understanding at five semantic-probe checkpoints. Final runtime dumps can help diagnose, but probe-time snapshots remain the scoring evidence.

| Probe | Position | Overall | Salience | Mainline | Organization | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | near 20% | 3.5 | 3 | 4 | 3 | 4 |
| 2 | near 40% | 4.25 | 4 | 4 | 4 | 5 |
| 3 | near 60% | 3.25 | 3 | 3 | 3 | 4 |
| 4 | near 80% | 3.75 | 4 | 4 | 3 | 4 |
| 5 | window end | 3.75 | 4 | 4 | 3 | 4 |

### Probe 1 — near 20%

#### Probe Position And Question

- target / captured: `c1-s261` -> `c1-s269`
- boundary kind: `phase transition`
- why this probe point: Ends the first-stage camp-arrival arc and crosses into the second stage, so the snapshot can be checked after the book has introduced the explicit three-stage prisoner-response structure and completed the first transition.
- explicit review focus: **囚徒精神反应三阶段** — Does the memory snapshot retain that the author is organizing camp-life psychology through this three-stage structure, even if it does not use the exact same wording?
- structural signals to check:
  - 囚徒精神反应三阶段：收容阶段、适应阶段、释放与解放阶段
  - 第一阶段向第二阶段过渡
  - 恐惧、休克、情感麻木作为集中营心理反应框架

#### Source Orientation

- capture-neighborhood excerpt: 在道路蜿蜒曲折的运输途中，粪便经常飞溅到囚徒的脸上，他们一旦表现出厌恶，或者用手擦去粪便，就会招致一顿毒打。 / 人的正常反应受到强烈的抑制。 / 在心理反应的第一阶段，某个囚徒往往不忍目睹别人被罚示众，也不忍目睹泥潭里一排排的囚徒在皮鞭的威慑下来回走几个钟头。
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 3 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `focus-ordinary-prisoners`: 书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。 Source: `src:c1:p4@126-p4@174`: 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。
- `adaptation-to-terror`: "适应"与"习以为常"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。 Source: `src:c1:p18@146-p18@178`: 从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
- `concept-communication-impossibility-paradox`: 对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。 Source: `src:c1:p10@199-p10@265`: 对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。
- `concept-depersonalization-through-stripping`: 现在，眼镜和皮带就是我的全部财产。 Source: `src:c1:p39@52-p39@69`: 现在，眼镜和皮带就是我的全部财产。
- `thread-threefold-struggle`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。 / 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争… Source: `src:c1:p5@63-p5@88`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- `thread-courage-irrecoverability`: 勇气一旦失去，几乎就不可能再挽回。 Source: `src:c1:p14@138-p14@155`: 勇气一旦失去，几乎就不可能再挽回。

#### What The Mechanism Retained

- The snapshot retains the three-stage concept in fragments through 'psychological-first-stage' (引用'仍处于心理反应的第一阶段') and 'concept-emotional-death-in-survival' (引用'从心理反应的第一阶段进入第二阶段'), but the explicit three-stage framework names—收容阶段、适应阶段、释放与解放阶段—are absent as an organizing structure. The second-stage entry (冷漠/情感死亡状态) is retained, but the third-stage label (释放与…

#### What It Missed Or Distorted

- the source's explicit framework statement is not surfaced as a structural digest item, which reduces salience and organization scores for a probe specifically checking this signal.

#### Score Rationale

- scores: salience `3`, mainline `4`, organization `3`, fidelity `4`, overall `3.5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains the three-stage concept in fragments through 'psychological-first-stage' (引用'仍处于心理反应的第一阶段') and 'concept-emotional-death-in-survival' (引用'从心理反应的第一阶段进入第二阶段'), but the explicit three-stage framework names—收容阶段、适应阶段、释放与解放阶段—are absent as an organizing structure. The second-stage entry (冷漠/情感死亡状态) is retained, but the third-stage label (释放与解放阶段) is missing. The snapshot captures the arc from terror→…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` filtered by `probe_index=1`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[0]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 2 — near 40%

#### Probe Position And Question

- target / captured: `c1-s528` -> `c1-s528`
- boundary kind: `inner-life episode closure`
- why this probe point: Closes the wife/nature/beauty inner-life sequence before the text turns again, so it can test whether the reader retains spiritual survival rather than only external camp events.
- structural signals to check:
  - 爱与妻子的形象作为精神生存资源
  - 自然与美感在极端处境中的支撑作用
  - 从外部苦难转向内在自由的主线

#### Source Orientation

- capture-neighborhood excerpt: 我强烈感觉到她的存在，她陪伴在我身旁，我甚至有伸手触摸她或抓住她的冲动，她就在身边的感觉越来越强烈。 / 就在那一刻，一只鸟飞下来，刚好落在我面前，在我挖壕沟的土堆上直直地盯着我。 / 前面我曾经提到过艺术。
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 3 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `focus-ordinary-prisoners`: 书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。 Source: `src:c1:p4@126-p4@174`: 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。
- `adaptation-to-terror`: "适应"与"习以为常"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。 Source: `src:c1:p18@146-p18@178`: 从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
- `concept-collective-emotional-economy`: 一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。 Source: `src:c1:p91@123-p91@156`: 一些人彻底绝望了，但这也是因为那些不可救药的乐观派实在令同伴气愤。
- `concept-communication-impossibility-paradox`: 对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。 Source: `src:c1:p10@199-p10@265`: 对于经历过这场噩梦的人来说，所有的解释都是多余的，而对于没有这种经历的人来说，他们不会理解我们过去的感受，也不会理解我们现在的感觉。
- `thread-threefold-struggle`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。 / 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争… Source: `src:c1:p5@63-p5@88`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- `thread-courage-irrecoverability`: 勇气一旦失去，几乎就不可能再挽回。 Source: `src:c1:p14@138-p14@155`: 勇气一旦失去，几乎就不可能再挽回。

#### What The Mechanism Retained

- The snapshot retains the central love/wife spiritual resource clearly via three key reactions: the '不论真实与否' anchor quote about wife's brightness, the discern on love transcending physical presence, and the bird-as-witness moment at the very end. The '爱是人类终身追求的最高目标' formulation is present in active attention. The broad mainline from external camp suffering t…

#### What It Missed Or Distorted

- the natural-beauty closing scene—specifically the sunset with changing colors over Bavarian forest, the mud reflecting the sky, and the remark '世界多美呀'—is absent from the digest. This is a significant omission because it is the precise structural moment this probe is designed to test: beauty in extremity as spiritual survival. The wife sequence trails off in…

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `4`, fidelity `5`, overall `4.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains the central love/wife spiritual resource clearly via three key reactions: the '不论真实与否' anchor quote about wife's brightness, the discern on love transcending physical presence, and the bird-as-witness moment at the very end. The '爱是人类终身追求的最高目标' formulation is present in active attention. The broad mainline from external camp suffering toward inner freedom is present (psychological stages, select…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` filtered by `probe_index=2`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[1]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 3 — near 60%

#### Probe Position And Question

- target / captured: `c1-s794` -> `c1-s794`
- boundary kind: `moral-decision episode closure`
- why this probe point: Closes the decision-not-to-escape episode, giving a clean semantic checkpoint for active choice, responsibility, and care under captivity.
- structural signals to check:
  - 被囚禁处境中的主动选择
  - 照顾病友与责任感
  - 命运、选择和平静之间的关系

#### Source Orientation

- capture-neighborhood excerpt: 我不知道接下来会发生什么事，但我内心得到了前所未有的平静。 / 我返回监狱，坐在同胞的床板边，试图安慰他，然后跟其他病号聊了一会，想让他们也安静下来。 / 我们在集中营的最后一天到来了。
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 3 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `focus-ordinary-prisoners`: 书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。 Source: `src:c1:p4@126-p4@174`: 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。
- `adaptation-to-terror`: "适应"与"习以为常"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。 Source: `src:c1:p18@146-p18@178`: 从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
- `concept-art-as-forgetfulness`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。 Source: `src:c1:p110@192-p110@217`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。
- `concept-art-ghostly-contrast`: 真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。 Source: `src:c1:p113@28-p113@73`: 真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。
- `thread-threefold-struggle`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。 / 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争… Source: `src:c1:p5@63-p5@88`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- `thread-art-memory-versus-forgetfulness`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。 Source: `src:c1:p113@213-p113@247`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。

#### What The Mechanism Retained

- The snapshot retains concrete material from the escape-refusal episode (the friend's offer, Frankl's momentary hesitation before the dying comrade, his whispered message to Otto about his wife, and the key line '一说出这句话，那种不安的感觉就顿时消失了'), and it correctly anchors the three-stage psychological framework from earlier.

#### What It Missed Or Distorted

- the structural signal of '被囚禁处境中的主动选择' is treated as a surface plot event rather than as the paradigmatic moral reversal it represents — the snapshot does not capture that Frankl's most 'active' choice under captivity was precisely the choice NOT to act. The second signal '照顾病友与责任感' appears only as context for why he hesitated, not as a thematic anchor. The…

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains concrete material from the escape-refusal episode (the friend's offer, Frankl's momentary hesitation before the dying comrade, his whispered message to Otto about his wife, and the key line '一说出这句话，那种不安的感觉就顿时消失了'), and it correctly anchors the three-stage psychological framework from earlier. However, the structural signal of '被囚禁处境中的主动选择' is treated as a surface plot event rather than as the pa…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` filtered by `probe_index=3`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[2]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 4 — near 80%

#### Probe Position And Question

- target / captured: `c1-s1059` -> `c1-s1083`
- boundary kind: `argument turn`
- why this probe point: Captures the argument that loss of future orientation weakens the body, just before the text deepens the life-purpose frame.
- structural signals to check:
  - 未来感、希望和生命力的关系
  - 精神状态影响身体抵抗力
  - 尼采命题和意义治疗主线的准备

#### Source Orientation

- capture-neighborhood excerpt: 没有人能够解除你的磨难，替代你的痛苦。 / 你独特的机会就依存于自己承受重负的方式之中。 / 作为犯人，我们这样的想法绝非脱离实际的臆想，这也是唯一能帮助我们解脱的想法。
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 3 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `focus-ordinary-prisoners`: 书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。 Source: `src:c1:p4@126-p4@174`: 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。
- `adaptation-to-terror`: "适应"与"习以为常"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。 Source: `src:c1:p18@146-p18@178`: 从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
- `concept-art-as-forgetfulness`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。 Source: `src:c1:p110@192-p110@217`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。
- `concept-art-ghostly-contrast`: 真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。 Source: `src:c1:p113@28-p113@73`: 真正让人难以忘怀且与艺术沾点边的，正是节目表演与凄惨的集中营生活背景所形成的幽灵般的反差。
- `thread-threefold-struggle`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。 / 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争… Source: `src:c1:p5@63-p5@88`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- `thread-art-memory-versus-forgetfulness`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。 Source: `src:c1:p113@213-p113@247`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。

#### What The Mechanism Retained

- The snapshot clearly retains the three probe structural signals. (1) 未来感/希望与生命力的关系: the F case (concept-collapse-inversion) shows hope's departure caused physical death—'身体也就成为疾病的牺牲品'—and the director's observation that Christmas-expectation deaths were due to abandoned hope weakening immunity. (2) 精神状态影响身体抵抗力: captured via the F case, the Nietzsche quote '…

#### What It Missed Or Distorted

- organization is modest—the active_attention_digest is heavily front-loaded with s1–s55 entries (focus-ordinary-prisoners, adaptation-to-terror, selection-mechanism, etc.) while the late-text meaning is represented only by the three concept-digest items and recent_reactions, leaving the life-purpose frame somewhat undersystematized compared to the early mate…

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `3`, fidelity `4`, overall `3.75`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot clearly retains the three probe structural signals. (1) 未来感/希望与生命力的关系: the F case (concept-collapse-inversion) shows hope's departure caused physical death—'身体也就成为疾病的牺牲品'—and the director's observation that Christmas-expectation deaths were due to abandoned hope weakening immunity. (2) 精神状态影响身体抵抗力: captured via the F case, the Nietzsche quote '知道为什么而活的人便能生存' framed as a psychotherapist motto, and the Sp…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` filtered by `probe_index=4`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[3]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 5 — window end

#### Probe Position And Question

- target / captured: `c1-s1292` -> `c1-s1292`
- boundary kind: `main-text ending`
- why this probe point: Ends the meaningful main-text window before citation-only tail material, so the final snapshot reflects the whole selected chapter rather than footnote residue.
- structural signals to check:
  - 释放与解放阶段
  - 人格恢复、苦涩和幻灭
  - 最终自由与不再畏惧的结尾框架

#### Source Orientation

- capture-neighborhood excerpt: 因此，当他们觉得集中营的全部经历仅仅是一场噩梦而已时，他们最后的解放也就到来了。 / 对于回家的犯人来说，最重要的体验是在他经受了那么多苦难之后，除了上帝，他不再畏惧任何东西，那种体验有着无与伦比的美妙感觉。 / [1] 提起这位党卫军司令，曾经有过一件趣事，与那些犹太犯人对他的态度有关。
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 3 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `focus-ordinary-prisoners`: 书中关注的是普通囚徒——没有袖箍、没有特权、姓名不为人知——而非英雄或囚头。死亡多发生在小集中营而非奥斯维辛式的大集中营。 Source: `src:c1:p4@126-p4@174`: 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。
- `adaptation-to-terror`: "适应"与"习以为常"不是麻木，而是心理防线的战略性重塑——为了在极端环境中存活，大脑必须将极度恐慌改写为可接受的日常状态。 Source: `src:c1:p18@146-p18@178`: 从那一刻起，我们不得不逐渐适应这种极度恐慌的状态，直至习以为常。
- `concept-action-speaks-louder-than-words-in-emptiness`: 拒绝跟监狱当局同流合污的号长以其正直和勇敢拥有成千上百次机会对所辖犯人施加道德影响。行为的直接影响总是比言辞更有说服力。 Source: `src:c1:p203@39-p203@99`: 拒绝跟监狱当局同流合污的号长以其正直和勇敢拥有成千上百次机会对所辖犯人施加道德影响。行为的直接影响总是比言辞更有说服力。
- `concept-art-as-forgetfulness`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。 Source: `src:c1:p110@192-p110@217`: 所有这一切都是为了帮助我们忘却，当然这也的确管用。
- `thread-threefold-struggle`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。 / 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争… Source: `src:c1:p5@63-p5@88`: 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- `thread-art-memory-versus-forgetfulness`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。 Source: `src:c1:p113@213-p113@247`: 提琴在哭泣，我身体的一部分也在哭泣，因为那天正好是某人的24岁生日。

#### What The Mechanism Retained

- The snapshot retains solid material on the main psychological themes: ordinary prisoners vs. Kapos/famous figures, the selection mechanism (left/right SS gesture), adaptation as strategic psychological rewiring, cold humor and suspended curiosity as coping strategies, and the three-stage psychological framework (with first and second stages well-defined). T…

#### What It Missed Or Distorted

- the three structural signals that define this probe point are incompletely organized: the '释放与解放阶段' (Third Phase) lacks systematic treatment beyond individual reactions; '人格恢复、苦涩和幻灭' (personality recovery, bitterness, disillusionment) is present only in fragmented reactions rather than as a named analytic category; and '最终自由与不再畏惧' (final freedom/fearlessnes…

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `3`, fidelity `4`, overall `3.75`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains solid material on the main psychological themes: ordinary prisoners vs. Kapos/famous figures, the selection mechanism (left/right SS gesture), adaptation as strategic psychological rewiring, cold humor and suspended curiosity as coping strategies, and the three-stage psychological framework (with first and second stages well-defined). Three recent reactions near the segment end correctly capture…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/summary/memory_quality_results.jsonl` filtered by `probe_index=5`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[4]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

## Callback / FVI Audit

Callback audit reads visible reactions, not memory state. A grounded callback correctly reconnects to earlier visible material; weak callback gestures at prior material but with loose or underspecified anchoring; FVI is a false visible integration; local-only makes no callback claim.

| Label | Count | What it means |
| --- | ---: | --- |
| grounded callback | 19 | credited visible continuity |
| weak callback | 9 | attempted continuity with loose or incomplete grounding |
| false visible integration | 0 | visible continuity claim judged unsupported or wrong |
| local-only reaction | 122 | visible reaction without callback claim |

### Grounded Callback Examples

#### `rx:Full_Content:src:c1:p9@0-p9@206:retrospect:10`

- reaction: 这里补全了前文"自己或朋友的胜出就意味着另一个的死亡"的操作层面："出卖朋友"是真实的生存手段，不是修辞。而"人格"也可以被"使用"这个措辞，揭示了残酷选择机制下人性的工具化。
- prior-link evidence: ref_ids=['reaction:rx:Full_Content:src:c1:p8@0-p8@110:discern:8']
- judge reason: Prior_link to reaction 8; correctly references the earlier visible reaction's analysis of '另一个号码' and connects it to betrayal and instrumentalization of personality.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p10@0-p10@265:highlight:11`

- reaction: 这是全书的方法论锚点：不是宏观历史叙事，而是具体的、有人格重量的个人经验。呼应了前文"书中关注的是普通囚徒"的承诺。
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly references earlier visible material about '普通囚徒' and its promise, correctly grounding the callback.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p10@265-p14@155:discern:14`

- reaction: 前文已经揭示了生存的三重斗争：面包、生活、朋友。这里的"勇气"是第四重——也是最内在、最不可逆的一重。前三重是外向的争夺，而勇气是内在的熄灭。并且"几乎就不可能再挽回"与前文"为了生存，他们可以使用一切手段"构成反向呼应：能活下来的人已经耗尽了几乎所有的勇气筹码。
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly references '前文已经揭示了生存的三重斗争：面包、生活、朋友'—directly connecting to reactions 1 and 3/4's content about the three survival layers.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

### Weak Callback Examples

#### `rx:Full_Content:src:c1:p71@0-p75@102:discern:42`

- reaction: 这里的「十分高兴」与之前「能被选中干活也是让他十分高兴的事」形成同一个倒错模式：不是为活着高兴，而是为在淘汰机制中仍被标记为「有用」而高兴。叙述者用一种黑色幽默式的清醒标注自己的高兴，这本身就是一种心理防御——他知道自己处境的可悲，但选择用「十分高兴」来消解它。
- prior-link evidence: no structured prior_link present
- judge reason: 提及'十分高兴'与前文某处形成相同倒错模式，但仅是主题层面的重复指出，缺乏精确锚定。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p89@0-p89@197:highlight:53`

- reaction: 「阴间人的眼光」——这个措辞精确而有力。「俯瞰」故乡这个动作，将前文所说的「悬置式好奇」推进到了极限：不是麻木，不是习惯，而是彻底的精神位移。从旁观者的距离看自己的来处，故乡变成了景观，变成了「毛骨悚然的城市」。
- prior-link evidence: no structured prior_link present
- judge reason: 提到'悬置式好奇'的推进，但与reaction 24的链接未经确认，属于暗示性关联。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p119@0-p119@149:highlight:69`

- reaction: 这是庆幸逻辑的终点——「烟囱」意味着毒气室，「奥斯维辛够远」意味着暂时安全。他们的快乐不在于任何正面事物，而在于最坏的选项被暂时排除在外。这与前文提到的「乐观派令同伴气愤」形成暗线：这里的「开心」是被剥夺到极限之后的最低阈值满足。
- prior-link evidence: no structured prior_link present
- judge reason: 提到'乐观派令同伴气愤'的暗线，但仅主题层面关联，缺乏精确锚定。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

### False Visible Integration Examples

- None recorded for this window.

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
