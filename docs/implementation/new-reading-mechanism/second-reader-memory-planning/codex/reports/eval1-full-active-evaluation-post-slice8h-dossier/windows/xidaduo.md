# Eval-1 Window Audit Dossier: 悉达多

This page is a reviewer audit dossier for one Eval-1 Retry1 window. It is evidence interpretation only: no eval was run to produce this page, no catalog entry is created here, and no product-quality or formal-authority claim is made.

## Window Verdict

悉达多 shows partial Lane A selective legibility: exact/focused evidence is real, but misses remain the dominant outcome. Lane B memory is weak at MQ 3.00; reviewer should inspect whether the mechanism is over-producing local reactions without durable organization. Callback audit records 47 grounded and 25 weak callbacks, with 0 FVI; these are callback-quality diagnostics, not proof of product-level reading quality.

| Channel | Result | Reviewer boundary |
| --- | --- | --- |
| Lane A selective legibility | recall `0.4000` over `20` note cases | exact/focused count toward recall; incidental and miss do not |
| Lane B Memory Quality | average `3.00` over `5` probes | evaluates state retention/organization, not visible reaction quality |
| Callback/FVI | grounded `47`, weak `25`, FVI `0` | visible callback correctness is separate from memory quality |

## Window-Specific Reading

- Lane A pattern: `8` of `20` note cases received recall credit, while `12` remained misses. The dominant miss mode below should be read as a candidate-admission / visible-reaction coverage issue, not as proof that the mechanism understood nothing about those notes.
- Lane B strongest probe: probe `2` at `near 30%` scored `4` because The snapshot strongly retains the three departure structures (from father, from Samanas, from Gotama) and the central declaration '我要拜自己为师' (I will take myself as teacher). The teacher-refusal dialogue with Gotama is preserved with Siddhartha's argument that …
- Lane B weakest probe: probe `4` at `near 85%` scored `2.25`; main reviewer concern: the structural_signals_to_check for this probe point—river and Vasudeva listening, Kamala's death, and son emergence/fatherhood transition—are only captured as isolated reaction highlights, not as organized thematic or narrative knowledge. The active_attentio…
- Callback/FVI pattern: no FVI was recorded in this window, but weak callbacks still need inspection because they show where the model gestures at continuity without tight visible grounding.

## Evidence Map

| Evidence | Path | What to inspect |
| --- | --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/summary/aggregate.json` (`present`) | label counts, recall, unlocatable diagnostics |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases` (`present`) | per-note source targets, candidates, judge labels |
| Lane A rebuilt bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/rebuilt_bundles/xidaduo_private_zh__segment_1/attentional_v2/normalized_eval_bundle.json` (`present`) | normalized visible reactions used for matching |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/aggregate.json` (`present`) | MQ and callback totals |
| Lane B MQ rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` (`present`) | probe scores and judge reasons |
| Lane B reaction audit rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/reaction_audit_results.jsonl` (`present`) | grounded/weak/FVI/local-only labels |
| Probe snapshots | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` (`present`) | probe-time state evidence; primary MQ audit source |
| Normalized eval bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json` (`present`) | visible reactions and memory summaries |
| Runtime state | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime` (`present`) | final run state; useful for diagnosis, not a substitute for probe-time snapshots |

## Lane A Selective Legibility Audit

Lane A asks whether visible reactions recover user-selected note spans under strict `segment_source_v1` source-span overlap. Text similarity and semantic similarity are not candidate-admission paths.

| Label | Count | Reviewer interpretation |
| --- | ---: | --- |
| `exact_match` | 1 | exact: the reaction span is identical to the aligned note span, so it is credited without semantic judging. |
| `focused_hit` | 7 | focused: the admitted span overlaps the note target and judge says the reaction captures the note-level meaning closely enough for recall credit. |
| `incidental_cover` | 0 | incidental: the reaction touches the note span but its attention is elsewhere; useful as support, not recall credit. |
| `miss` | 12 | miss: no credit; either no strict source-overlap candidate existed or admitted candidates did not satisfy focused recall. |
| `unlocatable diagnostic` | 0 | recorded as locator evidence only; never credited as candidate/match/recall |

### Case-Level Evidence

#### `e0001` — `exact_match`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001`
- source target: p143@0-55: 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！”
- matched reaction: `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`
- reaction text: "你并未理会我的祝愿"——这句话表面上是责备，实则是最后一次清晰的告白：我的祝愿已经说尽，我的路不在佛陀那里。两次"愿你"合在一起，既是友情的终点，也是道路的分野。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0001.json`

#### `e0002` — `focused_hit`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002`
- source target: p165@1-95: 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。
- matched reaction: `rx:Full_Content:src:c1:p164@68-p165@95:highlight:60`
- reaction text: 乔文达的角色在这里被精确地镜像化：他"曾经是我的影子"，现在"是乔达摩的影子"。这个"影子"的替换说明他从未真正追随法义本身，而是追随一个人。悉达多把这句"劫掠"说出来，意味着他完全理解并接受了这个损失。
- source-span relation: `note_contains_candidate; coverage=0.50`
- judge / runner reason: The reaction's quoted span (the '影子' passage about Govinda) is a central component of the note, and the reaction's analysis of the shadow metaphor and Siddhartha's acceptance directly addresses key content in the note. However, the note also emphasizes the reciprocal exchange ('他劫掠了我，但他馈赠得更多' and '他所馈赠的，则是悉达多，是我的自我')—…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0002.json`

#### `e0004` — `focused_hit`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004`
- source target: p274@42-120: 恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。
- matched reaction: `rx:Full_Content:src:c1:p270@0-p274@232:highlight:101`
- reaction text: 石子比喻的微妙之处在于"不必费力"——不是放弃努力，而是把努力消解在引力（目标）之中。但这和沙门修行的"无欲"并不完全相同：这里恰恰是因为有强烈目标，才产生了类似重力的向心力。他把宗教修行的被动接受，转化成了主动聚焦。
- source-span relation: `candidate_contains_note; coverage=1.00`
- judge / runner reason: The reaction's quoted source span (char 14-120) contains the note's entire source span (char 42-120) and the reaction's commentary directly engages with the core philosophical content: the stone metaphor and its key phrases '不必费力' and '无需挣扎'. The reaction's focus on explaining how the stone analogy represents active f…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0004.json`

#### `e0003` — `miss`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0003`
- source target: p181@93-131: 可我哪，我这个有意研读世界之书、自我存在之书的人，却预先爱上一个臆想的意义。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0003.json`

#### `e0005` — `miss`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0005`
- source target: p311@140-170: 而迦摩罗则教会他，不付出情欲就难收获情欲这一《爱经》的根本。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0005.json`

#### `e0007` — `miss`

- note case id: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0007`
- source target: p320@240-303: 他给出建议，表示同情，慷慨解囊，他甚至故意被欺骗。就像当年他热衷于侍奉诸神和做沙门时一样，他全神贯注，激情饱满地和众人游戏着。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases/xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0007.json`

### Miss-Mode Aggregation

- `no_source_overlap_candidate`: 12. No visible reaction entered the candidate set under strict source-span overlap. Do not infer a hidden semantic hit from thematic proximity.

### Unlocatable Source-Locator Diagnostics

- None recorded for this shard.

## Lane B Memory Quality Audit

Lane B asks whether probe-time memory state retains salient, source-faithful, organized understanding at five semantic-probe checkpoints. Final runtime dumps can help diagnose, but probe-time snapshots remain the scoring evidence.

| Probe | Position | Overall | Salience | Mainline | Organization | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | near 20% | 3.5 | 4 | 3 | 3 | 4 |
| 2 | near 30% | 4 | 4 | 4 | 4 | 4 |
| 3 | near 60% | 2.75 | 3 | 2 | 2 | 4 |
| 4 | near 85% | 2.25 | 2 | 2 | 2 | 3 |
| 5 | window end | 2.5 | 2 | 2 | 3 | 3 |

### Probe 1 — near 20%

#### Probe Position And Question

- target / captured: `c1-s436` -> `c1-s442`
- boundary kind: `chapter close`
- why this probe point: Ends the 沙门 chapter before 乔达摩, closing Siddhartha's ascetic self-denial phase and its limits.
- structural signals to check:
  - initial dissatisfaction
  - ascetic self-denial and Samana path
  - failure of escape-through-self-erasure before Buddha encounter

#### Source Orientation

- capture-neighborhood excerpt: 乔达摩最爱栖身城外的祗树给孤独园[2]。 / 该园由一位富庶的商人，也是世尊忠诚的追随者，给孤独[3]敬献。 / 两位朝拜乔达摩的青年沙门，一路探询到达此地。
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
- `govinda_shadow_devotion`: 乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在 Source: `src:c1:p7@230-p7@258`: 他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子
- `devotion_structure_this_unit`: 崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望 Source: `src:c1:p7@0-p7@10`: 而最爱他的人是乔文达
- `atman_becomes_own`: 内在"我"之源泉，必须拥有自己的阿特曼 Source: `src:c1:p11@0-p11@481`: 内在"我"之源泉，必须拥有自己的阿特曼
- `atman_not_learnable_obstacle_is_practice`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。 Source: `src:c1:p90@0-p93@122`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。
- `desire_as_fuel_of_samsara`: 他好似猎人，在新的渴望中瞄准摆脱轮回的出口 Source: `src:c1:p76@193-p76@214`: 他好似猎人，在新的渴望中瞄准摆脱轮回的出口
- `govinda_siddhartha_diverge_path`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友…… Source: `src:c1:p78@0-p81@77`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……

#### What The Mechanism Retained

- The snapshot strongly retains the three structural signals: (1) initial dissatisfaction with Brahman teachings is captured through 'inner_void_despite_outer_perfection' and 'spiritual_container_never_full' (his inability to find joy despite perfect external conditions); (2) ascetic self-denial and the Samana path is evidenced by the 'desire_as_fuel_of_samsa…

#### What It Missed Or Distorted

- the mainline fidelity is slightly weak—the detailed narrative arc of the three years with the Samanas and the specific departure moment are not deeply traced; the memory captures the philosophical conclusion but not the experiential journey that produced it. Organization is solid with active_attention, concept_digest, and thread_digest all functional, thoug…

#### Score Rationale

- scores: salience `4`, mainline `3`, organization `3`, fidelity `4`, overall `3.5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot strongly retains the three structural signals: (1) initial dissatisfaction with Brahman teachings is captured through 'inner_void_despite_outer_perfection' and 'spiritual_container_never_full' (his inability to find joy despite perfect external conditions); (2) ascetic self-denial and the Samana path is evidenced by the 'desire_as_fuel_of_samsara' thread and concepts about practicing physical austeritie…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` filtered by `probe_index=1`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[0]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 2 — near 30%

#### Probe Position And Question

- target / captured: `c1-s752` -> `c1-s752`
- boundary kind: `part-one close`
- why this probe point: Ends the first major movement through 乔达摩 and 觉醒, where Siddhartha refuses borrowed doctrine and turns toward self-experience.
- structural signals to check:
  - teacher refusal
  - self-experience over doctrine
  - leaving inherited teachings

#### Source Orientation

- capture-neighborhood excerpt: [3]Maja，幻。 / 虚妄不实。 / 第二部
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
- `govinda_shadow_devotion`: 乔文达的追随方式：不做朋友而做影子；追随的不是同路而是依附式的侍奉；即便在神的世界里仍是附属性存在 Source: `src:c1:p7@230-p7@258`: 他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子
- `devotion_structure_this_unit`: 崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望 Source: `src:c1:p7@0-p7@10`: 而最爱他的人是乔文达
- `atman_becomes_own`: 内在"我"之源泉，必须拥有自己的阿特曼 Source: `src:c1:p11@0-p11@481`: 内在"我"之源泉，必须拥有自己的阿特曼
- `atman_not_learnable_obstacle_is_practice`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。 Source: `src:c1:p90@0-p93@122`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。
- `govinda_siddhartha_diverge_path`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友…… / 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！” Source: `src:c1:p78@0-p81@77`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……
- `desire_as_fuel_of_samsara`: 他好似猎人，在新的渴望中瞄准摆脱轮回的出口 Source: `src:c1:p76@193-p76@214`: 他好似猎人，在新的渴望中瞄准摆脱轮回的出口

#### What The Mechanism Retained

- The snapshot strongly retains the three departure structures (from father, from Samanas, from Gotama) and the central declaration '我要拜自己为师' (I will take myself as teacher). The teacher-refusal dialogue with Gotama is preserved with Siddhartha's argument that Gotama's doctrine cannot transmit the Buddha's own experience ('没人能通过法义得到解脱'). The structural signal…

#### What It Missed Or Distorted

- the reading window metadata indicates coverage through chapters 3-14 (including 迦摩罗, 尘世间, 轮回, etc.), yet the captured memory content appears to end near the '觉醒' chapter conclusion, not reaching Part Two material. This creates a gap between declared coverage and actual retained content for this probe point.

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `4`, fidelity `4`, overall `4`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot strongly retains the three departure structures (from father, from Samanas, from Gotama) and the central declaration '我要拜自己为师' (I will take myself as teacher). The teacher-refusal dialogue with Gotama is preserved with Siddhartha's argument that Gotama's doctrine cannot transmit the Buddha's own experience ('没人能通过法义得到解脱'). The structural signal of 'self-experience over doctrine' is well-represented in t…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` filtered by `probe_index=2`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[1]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 3 — near 60%

#### Probe Position And Question

- target / captured: `c1-s1532` -> `c1-s1532`
- boundary kind: `worldly-life collapse`
- why this probe point: Ends 轮回 before 在河边, closing Kamala/Kamaswami/worldly life and the crisis that prepares river rebirth.
- structural signals to check:
  - Kamala and Kamaswami worldly life
  - disgust, despair, and collapse of worldly pursuit
  - transition toward river rebirth

#### Source Orientation

- capture-neighborhood excerpt: 从这天起，她关闭宅邸，不再见客。 / 不久后，她发现同悉达多最后的交欢令她怀了身孕。 / 在河边
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
- `govinda_shadow_devotion`: 乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。 Source: `src:c1:p7@230-p7@258`: 他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子
- `devotion_structure_this_unit`: 崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望 Source: `src:c1:p7@0-p7@10`: 而最爱他的人是乔文达
- `atman_becomes_own`: 内在"我"之源泉，必须拥有自己的阿特曼 Source: `src:c1:p11@0-p11@481`: 内在"我"之源泉，必须拥有自己的阿特曼
- `atman_not_learnable_obstacle_is_practice`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。 Source: `src:c1:p90@0-p93@122`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。
- `govinda_siddhartha_diverge_path`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友…… / 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！” Source: `src:c1:p78@0-p81@77`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……
- `atman_self_ungraspable_by_thought`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。 Source: `src:c1:p195@201-p195@233`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。

#### What The Mechanism Retained

- The snapshot retains strong fidelity to Part One early material (devotion structure, inner void, atman concepts)

#### What It Missed Or Distorted

- its active_attention and thread_digest are dominated by chapters 3–5 content. The three structural signals for this probe point — (1) Kamala and Kamaswami worldly life, (2) disgust/despair/collapse of worldly pursuit, (3) transition toward river rebirth — are largely absent from the snapshot's organized threads. The recent_reactions do capture Kamala's fina…

#### Score Rationale

- scores: salience `3`, mainline `2`, organization `2`, fidelity `4`, overall `2.75`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains strong fidelity to Part One early material (devotion structure, inner void, atman concepts) but its active_attention and thread_digest are dominated by chapters 3–5 content. The three structural signals for this probe point — (1) Kamala and Kamaswami worldly life, (2) disgust/despair/collapse of worldly pursuit, (3) transition toward river rebirth — are largely absent from the snapshot's organiz…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` filtered by `probe_index=3`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[2]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 4 — near 85%

#### Probe Position And Question

- target / captured: `c1-s2067` -> `c1-s2067`
- boundary kind: `chapter close`
- why this probe point: Ends 船夫 before 儿子, after the river/Vasudeva listening frame and Kamala's death introduce fatherhood.
- structural signals to check:
  - river and Vasudeva listening
  - Kamala death
  - son emergence and fatherhood transition

#### Source Orientation

- capture-neighborhood excerpt: 孩子仍在熟睡。 / 他们架起了柴堆。 / 儿子
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
- `govinda_shadow_devotion`: 乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。 Source: `src:c1:p7@230-p7@258`: 他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子
- `devotion_structure_this_unit`: 崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望 Source: `src:c1:p7@0-p7@10`: 而最爱他的人是乔文达
- `atman_becomes_own`: 内在"我"之源泉，必须拥有自己的阿特曼 Source: `src:c1:p11@0-p11@481`: 内在"我"之源泉，必须拥有自己的阿特曼
- `atman_not_learnable_obstacle_is_practice`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。 Source: `src:c1:p90@0-p93@122`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。
- `govinda_siddhartha_diverge_path`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友…… / 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！” Source: `src:c1:p78@0-p81@77`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……
- `atman_self_ungraspable_by_thought`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。 Source: `src:c1:p195@201-p195@233`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。

#### What The Mechanism Retained

- The snapshot retains three recent_reactions correctly sourced from the probe window (Kamala's silence '不语', Siddhartha listening to the river '被一生的时光触摸', the child sleeping vs. the pyre being built),

#### What It Missed Or Distorted

- the structural_signals_to_check for this probe point—river and Vasudeva listening, Kamala's death, and son emergence/fatherhood transition—are only captured as isolated reaction highlights, not as organized thematic or narrative knowledge. The active_attention_digest and concept_digest are dominated entirely by Part 1 material (devotion_structure, inner_voi…

#### Score Rationale

- scores: salience `2`, mainline `2`, organization `2`, fidelity `3`, overall `2.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains three recent_reactions correctly sourced from the probe window (Kamala's silence '不语', Siddhartha listening to the river '被一生的时光触摸', the child sleeping vs. the pyre being built), but the structural_signals_to_check for this probe point—river and Vasudeva listening, Kamala's death, and son emergence/fatherhood transition—are only captured as isolated reaction highlights, not as organized thematic…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` filtered by `probe_index=4`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[3]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 5 — window end

#### Probe Position And Question

- target / captured: `c1-s2417` -> `c1-s2417`
- boundary kind: `window end`
- why this probe point: Ends the full active window at the final integration, where the river voices, unity, reconciliation, and final transmission come together.
- structural signals to check:
  - 唵 and final integration
  - river voices and unity
  - reconciliation and final transmission

#### Source Orientation

- capture-neighborhood excerpt: 悉达多怀着深深的喜悦与诚挚目送他远去。 / 他步伐平和，浑身满是华彩，满是光明。
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
- `govinda_shadow_devotion`: 乔文达皈依佛陀、加入僧团，走的是集体依附之路；悉达多此刻用宗教故事换取理发伙计的信任、用刮胡理发敷油沐浴完成自我改造，走的是主动个体化之路。两条路的对照正在成形。 Source: `src:c1:p7@230-p7@258`: 他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子
- `devotion_structure_this_unit`: 崇拜结构：父亲（期待）、母亲（幸福）、女儿们（爱情涟漪）、乔文达（影子式追随）——四个方向完成对悉达多的仰望 Source: `src:c1:p7@0-p7@10`: 而最爱他的人是乔文达
- `atman_becomes_own`: 内在"我"之源泉，必须拥有自己的阿特曼 Source: `src:c1:p11@0-p11@481`: 内在"我"之源泉，必须拥有自己的阿特曼
- `atman_not_learnable_obstacle_is_practice`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。 Source: `src:c1:p90@0-p93@122`: 只有一种知识，它无处不在，它就是阿特曼……这种知识最恼人的敌人莫过于求知欲和修习。
- `govinda_siddhartha_diverge_path`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友…… / 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！” Source: `src:c1:p78@0-p81@77`: “你将成为伟大的沙门，悉达多。沙门长老常常赞叹，你学什么都快。你将成为圣人，哦，悉达多。”悉达多道：“我并不这么看，我的朋友……
- `atman_self_ungraspable_by_thought`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。 Source: `src:c1:p195@201-p195@233`: 然而因他始终试图以思想之网去捕捉自我，而使得自我从未被真正发现。

#### What The Mechanism Retained

- The snapshot retains the beginning-of-book material (devotion structure, inner void, spiritual container hunger) with good fidelity, and the recent_reactions section does capture the three probe structural signals—'唵' condensing from the river's symphony, Vasudeva's departure after his 'long career as ferryman,' and '我要去林中，去融入统一' with radiance.

#### What It Missed Or Distorted

- the active_focus_digest, concept_digest, and thread_digest are almost entirely anchored to the first chapter's opening scenes, leaving the book's mainline arc (Kamalila, city life, gambling and decadence, near-suicide by the river, Vasudeva as teacher, the son's arrival and departure, the final communion) severely underrepresented or absent. The structural …

#### Score Rationale

- scores: salience `2`, mainline `2`, organization `3`, fidelity `3`, overall `2.5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains the beginning-of-book material (devotion structure, inner void, spiritual container hunger) with good fidelity, and the recent_reactions section does capture the three probe structural signals—'唵' condensing from the river's symphony, Vasudeva's departure after his 'long career as ferryman,' and '我要去林中，去融入统一' with radiance. However, the active_focus_digest, concept_digest, and thread_digest are …

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` filtered by `probe_index=5`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[4]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

## Callback / FVI Audit

Callback audit reads visible reactions, not memory state. A grounded callback correctly reconnects to earlier visible material; weak callback gestures at prior material but with loose or underspecified anchoring; FVI is a false visible integration; local-only makes no callback claim.

| Label | Count | What it means |
| --- | ---: | --- |
| grounded callback | 47 | credited visible continuity |
| weak callback | 25 | attempted continuity with loose or incomplete grounding |
| false visible integration | 0 | visible continuity claim judged unsupported or wrong |
| local-only reaction | 139 | visible reaction without callback claim |

### Grounded Callback Examples

#### `rx:Full_Content:src:c1:p36@0-p40@9:retrospect:14`

- reaction: 这六个字完成了物理距离向心理距离的最终跃迁。不是"长大了"，是"陌生了"——父亲在破晓的光线里第一次真正失去了他认识的那个孩子。
- prior-link evidence: ref_ids=['reaction:rx:Full_Content:src:c1:p34@0-p35@81:highlight:13']
- judge reason: Explicitly links to reaction_index 13 (highlight:13) using prior_link field; '陌生了' builds on the montage observation where the father watches the son's unchanging vigil.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:22`

- reaction: 这里Brahman被明确标注为"宇宙自我"，与前文反复出现的"阿特曼（Atman）"构成对位——Atman指向内在的、个别的自我，Brahman指向宇宙的、至高的自我。两者同源而层次不同，解释了为何婆罗门知识无法填满那个容器：那是个人灵魂与宇宙本体之间的结构性距离，而非认知不足。
- prior-link evidence: ref_ids=['concept:atman_becomes_own']
- judge reason: Uses prior_link to 'concept:atman_becomes_own' - a concept thread that has been developed across visible earlier reading; correctly grounds the Brahman-Atman distinction in established conceptual framework.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:23`

- reaction: 这段引文是整部小说背后哲学框架的直接出处。自我=不死+无畏+梵+真实——悉达多离开婆罗门并非因为经典有误，而是因为知道"真实"与"抵达真实"之间隔着一条无法通过知识跨越的鸿沟。奥义书本身给出了答案，却无法保证学生能成为那个答案。
- prior-link evidence: ref_ids=['thread:knowing_without_arriving_thread']
- judge reason: Links to 'thread:knowing_without_arriving_thread' via prior_link; this conceptual thread has been built across earlier visible reactions discussing why knowledge alone cannot achieve enlightenment.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

### Weak Callback Examples

#### `rx:Full_Content:src:c1:p130@0-p131@191:discern:45`

- reaction: "无欲满足，无所模仿"——这句话把佛陀的本质点出来了。不是通过克制达到平静，不是通过修炼获得力量，而是根本上没有向外寻求、没有要模仿的对象。这与前面悉达多嗤笑沙门的"把戏"、否定一切知识传授构成微妙对照：也许真正的完美不是更高超的技艺，而是彻底放下对完美的追求？三个"在……中"的平行结构制造了一种庄严而不可动摇的完整感，与婴儿般的自然状态结合在一起——既是神性也是童真。
- prior-link evidence: no structured prior_link present
- judge reason: Mentions '与前面悉达多嗤笑沙门的把戏构成微妙对照' as thematic contrast, but this is general/partial without specific anchoring to earlier visible text.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p140@0-p144@25:highlight:51`

- reaction: 这里的转折极其重要："你一直是我的朋友，一直紧随我"，然后是"你现在成了男子汉，选择了自己的路"——这句话同时是祝福和放手。乔文达的追随从来不是"选择"，而是附属性质的跟随；此刻悉达多正是在说：你终于有了自己的步子，你不再是我的影子了。这与前文"影子"主题形成完整的呼应和收束。
- prior-link evidence: no structured prior_link present
- judge reason: Mentions '前文影子主题形成完整的呼应和收束' but without explicit prior_link reference. Theme-only connection, partial and unsupported by specific anchor.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`

- reaction: "你并未理会我的祝愿"——这句话表面上是责备，实则是最后一次清晰的告白：我的祝愿已经说尽，我的路不在佛陀那里。两次"愿你"合在一起，既是友情的终点，也是道路的分野。
- prior-link evidence: no structured prior_link present
- judge reason: Again references '影子' theme and '前文' without explicit prior_link. Theme-level connection without grounded anchor.
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
