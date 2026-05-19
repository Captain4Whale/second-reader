# Eval-1 Window Dossier: 悉达多

This page is the reviewer-facing drill-down for one Eval-1 Retry1 window. It is interpretation support, not a formal benchmark promotion or product-quality claim.

## Window Verdict

- Segment: `xidaduo_private_zh__segment_1`
- Lane A selective note recall: `0.4000` over `20` note cases.
- Lane A labels: exact `1`, focused `7`, incidental `0`, miss `12`.
- Lane B Memory Quality: average `3.00` over `5` probes.
- Callback/FVI audit: visible `211`, grounded `47`, weak `25`, FVI `0`, local-only `139`.
- Interpretation boundary: Lane A recall, MQ score, and callback audit are separate evidence channels; do not collapse them into one product-quality score.

## Evidence Map

| Surface | Path |
| --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/summary/aggregate.json` |
| Lane A report | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/summary/report.md` |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_xidaduo/note_cases` |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/aggregate.json` |
| Lane B MQ results | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/memory_quality_results.jsonl` |
| Lane B reaction audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/summary/reaction_audit_results.jsonl` |
| Lane B output bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2` |

## Lane A: Selective Legibility

| Metric | Value |
| --- | ---: |
| note cases | 20 |
| exact match | 1 |
| focused hit | 7 |
| incidental cover | 0 |
| miss | 12 |
| unlocatable reactions | 0 |
| note recall | 0.4000 |

### Representative Note Cases

| Label | Case | Note / source target | Reaction evidence | Judge / reviewer reading |
| --- | --- | --- | --- | --- |
| `exact_match` | `e0001` | 悉达多将手放在乔文达的肩头：“你并未理会我的祝愿。哦，乔文达。我再说一次：愿你将这条路走到底，愿你寻得解脱！” | `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`: "你并未理会我的祝愿"——这句话表面上是责备，实则是最后一次清晰的告白：我的祝愿已经说尽，我的路不在佛陀那里。两次"愿你"合在一起，既是友情的终点，也是道路的分野。 | Visible reaction source span exactly matched the aligned note span. |
| `focused_hit` | `e0002` | 佛陀劫掠了我。”悉达多想，“他劫掠了我，但他馈赠得更多。他夺走了我的朋友，那曾经信奉我，如今信奉他的朋友；那曾经是我的影子，如今是乔达摩的影子的朋友。而他所馈赠的，则是悉达多，是我的自我。 | `rx:Full_Content:src:c1:p164@68-p165@95:highlight:60`: 乔文达的角色在这里被精确地镜像化：他"曾经是我的影子"，现在"是乔达摩的影子"。这个"影子"的替换说明他从未真正追随法义本身，而是追随一个人。悉达多把这句"劫掠"说出来，意味着他完全理解并接受了这个损失。 | The reaction's quoted span (the '影子' passage about Govinda) is a central component of the note, and the reaction's analysis of the shadow metaphor and Siddhartha's acceptance directly addresses key content in the note. … |
| `focused_hit` | `e0004` | 恰如悉达多有了目标并下定决心。悉达多什么都不做，他等待、思考、斋戒。他穿行于尘世万物间正如石子飞入水底——不必费力，无需挣扎；他自会被指引，他任凭自己沉落。 | `rx:Full_Content:src:c1:p270@0-p274@232:highlight:101`: 石子比喻的微妙之处在于"不必费力"——不是放弃努力，而是把努力消解在引力（目标）之中。但这和沙门修行的"无欲"并不完全相同：这里恰恰是因为有强烈目标，才产生了类似重力的向心力。他把宗教修行的被动接受，转化成了主动聚焦。 | The reaction's quoted source span (char 14-120) contains the note's entire source span (char 42-120) and the reaction's commentary directly engages with the core philosophical content: the stone metaphor and its key phr… |
| `miss` | `e0003` | 可我哪，我这个有意研读世界之书、自我存在之书的人，却预先爱上一个臆想的意义。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0005` | 而迦摩罗则教会他，不付出情欲就难收获情欲这一《爱经》的根本。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0007` | 他给出建议，表示同情，慷慨解囊，他甚至故意被欺骗。就像当年他热衷于侍奉诸神和做沙门时一样，他全神贯注，激情饱满地和众人游戏着。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |

### Miss-Mode Reading

- `no_source_overlap_candidate`: 12 cases. Example: `xidaduo_private_zh__xidaduo_private_zh_personal_notes__e0003`. No visible reaction was admitted by strict `segment_source_v1` source-span overlap, so the note could not be credited even if the broader theme appeared nearby.

### Unlocatable Diagnostics

- None recorded for this shard.

## Lane B: Memory Quality

| Probe | Position | Score | Probe focus | What memory retained | Gap / judge concern |
| ---: | --- | ---: | --- | --- | --- |
| 1 | near 20% | 3.50 | initial dissatisfaction; ascetic self-denial and Samana path | The snapshot strongly retains the three structural signals: (1) initial dissatisfaction with Brahman teachings is captured through 'inner_void_despite_outer_perfect… | the mainline fidelity is slightly weak—the detailed narrative arc of the three years with the Samanas and the specific departure moment are not deeply traced; the memory capt… |
| 2 | near 30% | 4.00 | teacher refusal; self-experience over doctrine | The snapshot strongly retains the three departure structures (from father, from Samanas, from Gotama) and the central declaration '我要拜自己为师' (I will take myself as t… | the reading window metadata indicates coverage through chapters 3-14 (including 迦摩罗, 尘世间, 轮回, etc.), yet the captured memory content appears to end near the '觉醒' chapter conc… |
| 3 | near 60% | 2.75 | Kamala and Kamaswami worldly life; disgust, despair, and collapse of worldly pursuit | The snapshot retains strong fidelity to Part One early material (devotion structure, inner void, atman concepts) | its active_attention and thread_digest are dominated by chapters 3–5 content. The three structural signals for this probe point — (1) Kamala and Kamaswami worldly life, (2) d… |
| 4 | near 85% | 2.25 | river and Vasudeva listening; Kamala death | The snapshot retains three recent_reactions correctly sourced from the probe window (Kamala's silence '不语', Siddhartha listening to the river '被一生的时光触摸', the child … | the structural_signals_to_check for this probe point—river and Vasudeva listening, Kamala's death, and son emergence/fatherhood transition—are only captured as isolated react… |
| 5 | window end | 2.50 | 唵 and final integration; river voices and unity | The snapshot retains the beginning-of-book material (devotion structure, inner void, spiritual container hunger) with good fidelity, and the recent_reactions sectio… | the active_focus_digest, concept_digest, and thread_digest are almost entirely anchored to the first chapter's opening scenes, leaving the book's mainline arc (Kamalila, city… |

## Lane B: Callback / FVI Audit

Definitions for this page: grounded callback means a visible reaction correctly reconnects to earlier visible material; weak callback means it gestures at prior material but is loose or underspecified; FVI means the reaction visibly integrates earlier material in a way judged false or unsupported; local-only means no callback claim is made.

### Grounded Callback Examples

- `rx:Full_Content:src:c1:p36@0-p40@9:retrospect:14`: 这六个字完成了物理距离向心理距离的最终跃迁。不是"长大了"，是"陌生了"——父亲在破晓的光线里第一次真正失去了他认识的那个孩子。 Judge reason: Explicitly links to reaction_index 13 (highlight:13) using prior_link field; '陌生了' builds on the montage observation where the father watches the son's unchanging vigil.
- `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:22`: 这里Brahman被明确标注为"宇宙自我"，与前文反复出现的"阿特曼（Atman）"构成对位——Atman指向内在的、个别的自我，Brahman指向宇宙的、至高的自我。两者同源而层次不同，解释了为何婆罗门知识无法填满那个容器：那是个人灵魂与宇宙本体之间的结构性距离，而非认知不足。 Judge reason: Uses prior_link to 'concept:atman_becomes_own' - a concept thread that has been developed across visible earlier reading; correctly grounds the Brahman-Atman distinction in establ…
- `rx:Full_Content:src:c1:p63@0-p67@111:retrospect:23`: 这段引文是整部小说背后哲学框架的直接出处。自我=不死+无畏+梵+真实——悉达多离开婆罗门并非因为经典有误，而是因为知道"真实"与"抵达真实"之间隔着一条无法通过知识跨越的鸿沟。奥义书本身给出了答案，却无法保证学生能成为那个答案。 Judge reason: Links to 'thread:knowing_without_arriving_thread' via prior_link; this conceptual thread has been built across earlier visible reactions discussing why knowledge alone cannot achi…

### Weak Callback Examples

- `rx:Full_Content:src:c1:p130@0-p131@191:discern:45`: "无欲满足，无所模仿"——这句话把佛陀的本质点出来了。不是通过克制达到平静，不是通过修炼获得力量，而是根本上没有向外寻求、没有要模仿的对象。这与前面悉达多嗤笑沙门的"把戏"、否定一切知识传授构成微妙对照：也许真正的完美不是更高超的技艺，而是彻底放下对完美的追求？三个"在……中"的平行结构制造了一种庄严而不可动摇的完整感，与婴儿般的自然状态结合在一起——既是神性也是童真。 Judge reason: Mentions '与前面悉达多嗤笑沙门的把戏构成微妙对照' as thematic contrast, but this is general/partial without specific anchoring to earlier visible text.
- `rx:Full_Content:src:c1:p140@0-p144@25:highlight:51`: 这里的转折极其重要："你一直是我的朋友，一直紧随我"，然后是"你现在成了男子汉，选择了自己的路"——这句话同时是祝福和放手。乔文达的追随从来不是"选择"，而是附属性质的跟随；此刻悉达多正是在说：你终于有了自己的步子，你不再是我的影子了。这与前文"影子"主题形成完整的呼应和收束。 Judge reason: Mentions '前文影子主题形成完整的呼应和收束' but without explicit prior_link reference. Theme-only connection, partial and unsupported by specific anchor.
- `rx:Full_Content:src:c1:p140@0-p144@25:highlight:52`: "你并未理会我的祝愿"——这句话表面上是责备，实则是最后一次清晰的告白：我的祝愿已经说尽，我的路不在佛陀那里。两次"愿你"合在一起，既是友情的终点，也是道路的分野。 Judge reason: Again references '影子' theme and '前文' without explicit prior_link. Theme-level connection without grounded anchor.

### False Visible Integration Examples

- None in this window.

## Reviewer Takeaway

- Lane A shows comparatively stronger selective legibility in this window, but the miss count still prevents a product-quality claim.
- Lane B memory state is weak for this diagnostic suite, especially on organization and structural retention.
- Callback counts are audit evidence, not proof that visible reactions are product-quality callbacks.
