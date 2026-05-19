# Eval-1 Window Dossier: 芒格之道

This page is the reviewer-facing drill-down for one Eval-1 Retry1 window. It is interpretation support, not a formal benchmark promotion or product-quality claim.

## Window Verdict

- Segment: `mangge_zhi_dao_private_zh__segment_1`
- Lane A selective note recall: `0.3600` over `25` note cases.
- Lane A labels: exact `2`, focused `7`, incidental `0`, miss `16`.
- Lane B Memory Quality: average `3.10` over `5` probes.
- Callback/FVI audit: visible `270`, grounded `43`, weak `13`, FVI `0`, local-only `214`.
- Interpretation boundary: Lane A recall, MQ score, and callback audit are separate evidence channels; do not collapse them into one product-quality score.

## Evidence Map

| Surface | Path |
| --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/summary/aggregate.json` |
| Lane A report | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/summary/report.md` |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases` |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/aggregate.json` |
| Lane B MQ results | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` |
| Lane B reaction audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/reaction_audit_results.jsonl` |
| Lane B output bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2` |

## Lane A: Selective Legibility

| Metric | Value |
| --- | ---: |
| note cases | 25 |
| exact match | 2 |
| focused hit | 7 |
| incidental cover | 0 |
| miss | 16 |
| unlocatable reactions | 0 |
| note recall | 0.3600 |

### Representative Note Cases

| Label | Case | Note / source target | Reaction evidence | Judge / reviewer reading |
| --- | --- | --- | --- | --- |
| `exact_match` | `e0002` | 有时候，只有经过失败的历练，我们才能懂得谦卑。 | `rx:Full_Content:src:c1:p77@0-p81@23:discern:37`: 前面已经用墨菲的故事铺陈了，这里是一句直接的结论性陈述。但它加了一个"只有"——意味着没有失败这个历练，谦卑是学不到的，前面的成功再多也学不会。这和前文"没有一个人说我谦卑"形成呼应：芒格自己身边这些强人都没学会谦卑，因为他们还没有经足够失败的历练。 | Visible reaction source span exactly matched the aligned note span. |
| `exact_match` | `e0015` | 打得过就打，打不过就跑。 | `rx:Full_Content:src:c1:p307@0-p310@112:highlight:134`: 结论干脆，没有道德色彩。这和前文"攥在手里，不意味着永远"的立场一致：不是不能动，是形势不好时不硬撑。 | Visible reaction source span exactly matched the aligned note span. |
| `focused_hit` | `e0006` | 多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？”他回答道：“查理，我这鱼钩又不是卖给鱼的。” | `rx:Full_Content:src:c1:p97@0-p101@62:highlight:42`: 这句话的力度来自它直接的逻辑：买家才是目标，鱼不是。整个段落的讽刺力量都在这句短回应里——不需要解释，笑完就懂了。 | The reaction's quoted span precisely captures the punchline ('查理，我这鱼钩又不是卖给鱼的。'), which is the core insight of the entire note. The reaction's analysis focuses directly on this specific quote, explaining its satirical lo… |
| `focused_hit` | `e0007` | 所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。 | `rx:Full_Content:src:c1:p97@0-p101@62:highlight:41`: 这个"所有人"把前面的所有铺垫（销售员、顾问、律师）都收进去了。芒格不是在骂某个职业，他是在指出一件每个人都干的事。没有控诉感，只有冷静的描述，这是最难以反驳的批评方式。 | The reaction directly engages with the note's core idea about '所有人' (everyone) having this subconscious bias. It analyzes why Munger's use of '所有人' is rhetorically powerful—encompassing all previously mentioned professi… |
| `miss` | `e0001` | 这证明，一家公司建立了好的文化之后，就能走上良性循环的轨道。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0003` | 用“谦卑”这个词也许不太恰当，可能用“务实”这个词更合适。我们能取得今时今日的成就，不是因为我们的能力比别人高出多少，而是我们比别人更清楚自己能力的大小。清楚自己能力的大小，这个品质应该不能说是“谦卑”。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |
| `miss` | `e0004` | 一件事，他没彻底弄明白之前，是绝对不会做的。一笔交易，等上五年，他都能等。 | `(no matched reaction)` | No visible reaction was admitted by strict source-span overlap; no recall credit was assigned. |

### Miss-Mode Reading

- `no_source_overlap_candidate`: 16 cases. Example: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0001`. No visible reaction was admitted by strict `segment_source_v1` source-span overlap, so the note could not be credited even if the broader theme appeared nearby.

### Unlocatable Diagnostics

- None recorded for this shard.

## Lane B: Memory Quality

| Probe | Position | Score | Probe focus | What memory retained | Gap / judge concern |
| ---: | --- | ---: | --- | --- | --- |
| 1 | near 20% | 4.00 | 1988 annual discussion closure; management trust and reputation | The snapshot retains strong, important material across multiple dimensions. Key retained items include: Wesco's three-branch structure (互助储蓄, 精密钢材, 西科保险), the annua… | no significant drift or false material. Organization is solid with clear conceptual clusters and thematic threading. Rating 4. |
| 2 | near 40% | 3.25 | anti-forecasting investment posture; cash optionality | The snapshot retains solid material on Wesco's asset posture (攥在手里不意味着永远, 两条路都关闭的守势), the disclosure boundary rule (recent_reactions: '不谈论' as cognitive boundary, '… | the 'anti-forecasting investment posture' as a coherent framework is fragmented—the Osler/Carlyle '与其为朦胧的未来而烦恼忧虑，不如脚踏实地' quote (which anchors the entire anti-forecast argumen… |
| 3 | near 60% | 2.25 | S&L crisis mechanics; regulatory incentives and unintended consequences | The snapshot retains important S&L crisis insights in recent_reactions (policy combinations as locked system, '九龙治水' fragmentation diagnosis, complexity theory obse… | critically omits the detailed causal mechanism that should anchor this probe point. The causal chain from '制度的死穴' through deregulated incentives to moral hazard gambling with… |
| 4 | near 80% | 2.75 | 1990 crisis recap; regulator exhaustion | The snapshot retains the 1990 S&L crisis recap with reasonable fidelity—the industry's self-inflicted wounds, the shame of lobbying, the system design failures (gov… | the probe's explicit structural signal 'transition from crisis diagnosis to investing doctrine' is entirely absent. The source text explicitly signals that after closing the … |
| 5 | window end | 3.25 | full-window investment doctrine continuity; crisis-to-risk-arbitrage arc | The snapshot retains several well-sourced concrete items (Wesco's three subsidiaries, asset deployability stance, Ben Graham trap story, humility/competence tension… | it misses significant structural material from the source: the '形势比人强' (form overpowers people) thesis, which is explicitly identified as the organizing theme of the 1989 mee… |

## Lane B: Callback / FVI Audit

Definitions for this page: grounded callback means a visible reaction correctly reconnects to earlier visible material; weak callback means it gestures at prior material but is loose or underspecified; FVI means the reaction visibly integrates earlier material in a way judged false or unsupported; local-only means no callback claim is made.

### Grounded Callback Examples

- `rx:Full_Content:src:c1:p34@0-p38@97:highlight:16`: 这里"现在没一个"和前文那句"这是现在，不意味着永远"形成呼应——不是手里没钱，而是没有值得出手的好标的。持有资本等待是主动姿态，不是被动困局。 Judge reason: 明确声称与前文'这是现在，不意味着永远'形成呼应，两个文本位置相近，关联具体且可查。
- `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:18`: 这句话把收购的难度从偶然性提升为规律性——"好事多磨"不是概率问题，而是本质特征。任何试图绕开这一规律的做法，"很难有好结果"。前文那句"一年也只能做成一笔"在这里获得了逻辑支撑：不是慢，是本来就应该慢。 Judge reason: prior_link指向'concept:annual_one_deal_discipline'，将'好事多磨'与'一年只能做成一笔'做了明确的逻辑关联，具体可查。
- `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:19`: 这里的"守势"值得关注：不是手里没钱，而是两条主动路都暂时关闭后的主动选择。结合前文"攥在手里，这是现在，不意味着永远"的立场，守势是等待机会的姿态，和被迫收缩是两回事。 Judge reason: prior_link指向'active_attention:wesco_asset_deployability'，将守势姿态锚定到前文关于资产可部署性的讨论上，关联具体。

### Weak Callback Examples

- `rx:Full_Content:src:c1:p18@0-p19@88:discern:5`: "应该"这个词在这里出现了两次，语气是自我确认式的，但并非言之凿凿。这和芒格在前面说"实在没有预测未来的能力"形成了一个有趣的对照——在储蓄银行的具体投资上，叙述者反而用"应该"来建立信心。这不是矛盾，而是层次区分：对宏观市场无法预测，对具体纾困标的的退出路径（整体出售）则有一定的把握。 Judge reason: 声称与前文'实在没有预测未来的能力'形成对照，但未提供具体文本位置或引用，依赖印象式关联而非锚定型引证。
- `rx:Full_Content:src:c1:p51@0-p55@64:highlight:27`: 又一个"不凑热闹"的时刻——和前面投资的守势逻辑一脉相承。在开发商贷款业务上别人越踊跃，西科就越主动退出，说明他们不是在所有业务上都守势，而是在高风险的拥挤赛道上保持距离。 Judge reason: 声称与前文投资的守势逻辑一脉相承，但未提供具体锚定文本，属于印象式关联而非锚定型引用。
- `rx:Full_Content:src:c1:p61@0-p62@104:discern:28`: 这句话是整个段落的基调锚点。把"没有预知未来的能力"放在"如履薄冰"之前，等于把不确定性设定为行动的前提条件，而不是行动的障碍——意味着你不是因为谨慎才不动，而是因为认清了现实的不可预测，才坦然接受"动也是如履薄冰"。和前面"我们出手的时候很少"的自律逻辑是一脉相承的。 Judge reason: 声称与前面'我们出手的时候很少'的自律逻辑一脉相承，但未提供具体文本锚定，关联依赖推断而非引用。

### False Visible Integration Examples

- None in this window.

## Reviewer Takeaway

- Lane A shows partial selective legibility: meaningful hits exist, but misses remain the dominant outcome.
- Lane B memory state is weak for this diagnostic suite, especially on organization and structural retention.
- Callback counts are audit evidence, not proof that visible reactions are product-quality callbacks.
