# Eval-1 Window Dossier: 纳瓦尔宝典

This page is the reviewer-facing drill-down for one Eval-1 Retry1 window. It is interpretation support, not a formal benchmark promotion or product-quality claim.

## Window Verdict

- Segment: `nawaer_baodian_private_zh__segment_1`
- Lane A selective note recall: `0.4348` over `23` note cases.
- Lane A labels: exact `8`, focused `2`, incidental `2`, miss `11`.
- Lane B Memory Quality: average `3.65` over `5` probes.
- Callback/FVI audit: visible `40`, grounded `6`, weak `4`, FVI `1`, local-only `29`.
- Interpretation boundary: Lane A recall, MQ score, and callback audit are separate evidence channels; do not collapse them into one product-quality score.

## Evidence Map

| Surface | Path |
| --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/summary/aggregate.json` |
| Lane A report | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/summary/report.md` |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases` |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/aggregate.json` |
| Lane B MQ results | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` |
| Lane B reaction audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/reaction_audit_results.jsonl` |
| Lane B output bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2` |

## Lane A: Selective Legibility

| Metric | Value |
| --- | ---: |
| note cases | 23 |
| exact match | 8 |
| focused hit | 2 |
| incidental cover | 2 |
| miss | 11 |
| unlocatable reactions | 1 |
| note recall | 0.4348 |

### Representative Note Cases

| Label | Case | Note / source target | Reaction evidence | Judge / reviewer reading |
| --- | --- | --- | --- | --- |
| `exact_match` | `e0004` | 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。 | `rx:Full_Content:src:c1:p14@0-p15@41:highlight:7`: 把工资劳动称为"出租时间"是很犀利的表述——它把这种交易模式的本质暴露出来了：你在出卖生命时间，换来一次性报酬，但没有积累任何生产资料。这种命名方式本身就带有一股揭示感。 | Visible reaction source span exactly matched the aligned note span. |
| `exact_match` | `e0010` | 专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。 | `rx:Full_Content:src:c1:p32@0-p35@30:highlight:10`: 这个"如果……那么"的反事实结构很犀利——它把专长的反面说成是"可替代性"，等于给专长下了一个功能性定义：不是"你会什么"，而是"别人不会什么，而且学不来"。 | Visible reaction source span exactly matched the aligned note span. |
| `focused_hit` | `e0019` | 这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。 | `rx:Full_Content:src:c1:p85@0-p88@72:highlight:32`: 这个"交叉重叠"的结构很有意思："专长"既是"产品化"的门槛，也是"自己"本来就有的东西。作者用这个词的双重归属，把整个分散的理念体系——责任感、判断力、独特性、杠杆——全部锚定在这两个词的交叉点上。 | The reaction's quoted source span covers the core substantive content of the note—the examples tying "自己" to uniqueness, responsibility, and expertise, and "产品化" to leverage and expertise. The reaction's analysis direct… |
| `focused_hit` | `e0023` | 社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。 | `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`: "轻松自然"这个条件与前面"专长累积像玩耍"形成精确呼应——两个标准合并成一个更完整的检验：如果你做的事既像玩耍，又是轻松自然的，那它大概率就是你真正的专长所在，也可能是财富的入口。 | The reaction specifically targets the "轻松自然" portion of the overlapped source span and develops a substantive analysis by connecting it to another principle ("专长累积像玩耍") to form a combined test for identifying one's true… |
| `incidental_cover` | `e0002` | 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。 | `rx:Full_Content:src:c1:p1@0-p3@215:highlight:2`: 财富三要素：做什么（内容选择）、和谁（合作伙伴/团队）、什么时候（时机判断）。不是埋头苦干，而是这三个维度的决策质量决定结果。 | The reaction's quoted span (136-165) covers only the first sentence about the three wealth elements, which is indeed a core part of the note. However, the note also contains important content about 'understanding and th… |
| `miss` | `e0001` | 赚钱跟工作的努力程度没什么必然联系。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0003` | 追求财富，而不是金钱或地位。财富是指在你睡觉时仍能为你赚钱的资产。金钱是我们转换时间和财富的方式。地位是你在社会等级体系中所处的位置。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0005` | 获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |

### Miss-Mode Reading

- `no_source_overlap_candidate`: 11 cases. Example: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0001`. No visible reaction was admitted by strict `segment_source_v1` source-span overlap, so the note could not be credited even if the broader theme appeared nearby.

### Unlocatable Diagnostics

- `rx:Chapter_1:src:c1:p99@193-p99@193:retrospect:1`

These reactions were diagnostic only. They were not counted as matches, candidates, or recall credit.

## Lane B: Memory Quality

| Probe | Position | Score | Probe focus | What memory retained | Gap / judge concern |
| ---: | --- | ---: | --- | --- | --- |
| 1 | near 20% | 3.25 | wealth vs money vs status; renting time vs owning equity/assets | The snapshot retains several key concepts including equity ownership as the wealth path and the leverage-points observation skill, and correctly captures the ignore… | the foundational structural signal of wealth vs. money vs. status as a three-way distinction is absent—no concept in the digest explicitly captures this trinity. Furthermore,… |
| 2 | near 40% | 3.50 | specific knowledge definition; sales/build pairing | The snapshot retains strong individual items (复利回报, 股权致富, 销售构建双技傍身, 合伙人正直诚信优先) and correctly marks the transition at responsibility/leverage. | the "specific knowledge" cluster's defining structure is only partially retained: the definition '专长指的是无法通过培训获得的知识' is NOT captured as a standalone definition (only the play-… |
| 3 | near 55% | 3.25 | capital, labor, code, and media as leverage; permissioned vs permissionless leverage | The snapshot retains individual leverage concepts (capital as money requiring financing, labor as oldest leverage, code/media as permissionless) and includes two re… | three significant gaps exist: (1) The explicit "robots, code, media, and data centers" formulation is absent—the nearby passage '有一大批机器人可供我们免费使用...这些机器人就集中放在数据中心' is not capt… |
| 4 | near 80% | 5.00 | productize yourself; uniqueness, responsibility, and leverage | The snapshot captures the chapter's culminating synthesis '把自己产品化' with full fidelity, including the two-pillar structure that maps '自己' (uniqueness + responsibilit… | This reads as strong chapter-level memory at the synthesis point. |
| 5 | window end | 3.25 | wealth-building body chapter frame; assets, technology, unmet needs, and scale | The snapshot retains 6 active items and 3 concepts from the chapter's wealth-building body, all accurately sourced. | it misses the chapter's central organizing frame: '把自己产品化' (productize yourself) — the self(unique+accountability) + productize(leverage+expertise) synthesis that unifies all… |

## Lane B: Callback / FVI Audit

Definitions for this page: grounded callback means a visible reaction correctly reconnects to earlier visible material; weak callback means it gestures at prior material but is loose or underspecified; FVI means the reaction visibly integrates earlier material in a way judged false or unsupported; local-only means no callback claim is made.

### Grounded Callback Examples

- `rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13`: 这句话和前面那句「专长指的是无法通过培训获得的知识」形成了完整的逻辑闭环：前一句给出了定义层面的约束（不可培训性），这一句给出了实践层面的约束（不可学校化）。两个「无法」指向同一个方向——专长的获得和传授都绕不开个人化的、近身的接触。 Judge reason: Prior link to reaction 10 is explicit and correctly identified. The logical closure between '不可培训性' (definition layer) and '不可学校化' (practice layer) is a precise, well-supported co…
- `rx:Full_Content:src:c1:p44@0-p47@51:retrospect:16`: 这里把商业杠杆落实为三个可识别的类别，"复制边际成本为零"这个经济学措辞精确地刻画了代码和媒体的特性——一次创造、无限分发、没有边际成本。这也呼应了前文对专长积累的描述：高杠杆的领域，往往就是那些无法被标准化、外包或自动化的个人化领域。 Judge reason: Prior link to reaction 14 is explicit and substantively supported. The claim that high-leverage fields align with non-standardizable personal expertise is a concrete, correct exte…
- `rx:Full_Content:src:c1:p64@0-p67@31:discern:26`: 这份清单与前文"判断力是杠杆的倍增器"构成直接呼应：微观经济学理解激励结构，博弈论处理策略互动，心理学和说服术指向人与人的影响，伦理学提供价值框架，数学与计算机则是建模和执行的工具——这不是随机的课程列表，而是支撑高质量判断的完整认知工具箱。 Judge reason: Explicitly maps the discipline list to earlier material ('判断力是杠杆的倍增器') and provides thematic connection to reaction 24's definition of judgment as cognitive capability.

### Weak Callback Examples

- `rx:Full_Content:src:c1:p40@0-p43@43:highlight:14`: 这句话和前文建立的专长概念形成同方向延伸：不可培训、不可学校化、不可外包自动化——三个"不能"从不同维度指向同一个结论：专长是个人化的、不可标准化的。 Judge reason: The content gestures at '前文' with vague self-reference but provides no explicit prior link in metadata. The claim of three 'cannots' summarizing earlier material lacks specificity…
- `rx:Full_Content:src:c1:p89@0-p93@57:highlight:35`: 这个定义直接呼应了"把自己产品化"的最终目标：你不是在销售时间，而是在部署一套能在你缺席时继续运转的系统。睡眠测试是一个非常直觉化的检验标准——如果一个资产停止运作你就停止收入，那它就不是真正的财富。 Judge reason: 声称'直接呼应把自己产品化的最终目标'，但'把自己产品化'的表述未在前文可见段落中以该措辞出现，回调方向正确但措辞缺乏可见文本支撑。
- `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`: "轻松自然"这个条件与前面"专长累积像玩耍"形成精确呼应——两个标准合并成一个更完整的检验：如果你做的事既像玩耍，又是轻松自然的，那它大概率就是你真正的专长所在，也可能是财富的入口。 Judge reason: 声称与前面'专长累积像玩耍'形成精确呼应，但'专长累积像玩耍'并非前文可见段落中的已有表述，其所依据的reaction 12内容为问句形式，与此处断言存在落差。

### False Visible Integration Examples

- `rx:Full_Content:src:c1:p85@0-p88@72:retrospect:33`: 这与前面"当你终于变得富有时，你会意识到，这并不是你最初的追求"形成呼应——财富不是起点，"我能提供什么独特的价值"才是真正需要花几十年去回答的问题。 Why FVI: 声称呼应前文具体引文'当你终于变得富有时，你会意识到，这并不是你最初的追求'，但该引文未出现在当前阅读窗口内的可见材料中。prior_link所引的thread标签属于主题类投射，非文本级可见回调，为过拟合类集成。

## Reviewer Takeaway

- Lane A shows comparatively stronger selective legibility in this window, but the miss count still prevents a product-quality claim.
- Lane B memory state is relatively coherent for this diagnostic suite, with omissions concentrated around specific structural signals rather than wholesale loss.
- Callback counts are audit evidence, not proof that visible reactions are product-quality callbacks.
