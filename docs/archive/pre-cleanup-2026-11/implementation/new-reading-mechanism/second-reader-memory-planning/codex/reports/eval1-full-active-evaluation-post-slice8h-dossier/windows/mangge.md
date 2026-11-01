# Eval-1 Window Audit Dossier: 芒格之道

This page is a reviewer audit dossier for one Eval-1 Retry1 window. It is evidence interpretation only: no eval was run to produce this page, no catalog entry is created here, and no product-quality or formal-authority claim is made.

## Window Verdict

芒格之道 shows partial Lane A selective legibility: exact/focused evidence is real, but misses remain the dominant outcome. Lane B memory is weak at MQ 3.10; reviewer should inspect whether the mechanism is over-producing local reactions without durable organization. Callback audit records 43 grounded and 13 weak callbacks, with 0 FVI; these are callback-quality diagnostics, not proof of product-level reading quality.

| Channel | Result | Reviewer boundary |
| --- | --- | --- |
| Lane A selective legibility | recall `0.3600` over `25` note cases | exact/focused count toward recall; incidental and miss do not |
| Lane B Memory Quality | average `3.10` over `5` probes | evaluates state retention/organization, not visible reaction quality |
| Callback/FVI | grounded `43`, weak `13`, FVI `0` | visible callback correctness is separate from memory quality |

## Window-Specific Reading

- Lane A pattern: `9` of `25` note cases received recall credit, while `16` remained misses. The dominant miss mode below should be read as a candidate-admission / visible-reaction coverage issue, not as proof that the mechanism understood nothing about those notes.
- Lane B strongest probe: probe `1` at `near 20%` scored `4` because The snapshot retains strong, important material across multiple dimensions. Key retained items include: Wesco's three-branch structure (互助储蓄, 精密钢材, 西科保险), the annual-one-deal acquisition discipline, the defensive posture when both acquisition and equity marke…
- Lane B weakest probe: probe `3` at `near 60%` scored `2.25`; main reviewer concern: critically omits the detailed causal mechanism that should anchor this probe point. The causal chain from '制度的死穴' through deregulated incentives to moral hazard gambling with taxpayer money is present in the source text's appendix but absent from active focus…
- Callback/FVI pattern: no FVI was recorded in this window, but weak callbacks still need inspection because they show where the model gestures at continuity without tight visible grounding.

## Evidence Map

| Evidence | Path | What to inspect |
| --- | --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/summary/aggregate.json` (`present`) | label counts, recall, unlocatable diagnostics |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases` (`present`) | per-note source targets, candidates, judge labels |
| Lane A rebuilt bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/rebuilt_bundles/mangge_zhi_dao_private_zh__segment_1/attentional_v2/normalized_eval_bundle.json` (`present`) | normalized visible reactions used for matching |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/aggregate.json` (`present`) | MQ and callback totals |
| Lane B MQ rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` (`present`) | probe scores and judge reasons |
| Lane B reaction audit rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/reaction_audit_results.jsonl` (`present`) | grounded/weak/FVI/local-only labels |
| Probe snapshots | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` (`present`) | probe-time state evidence; primary MQ audit source |
| Normalized eval bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json` (`present`) | visible reactions and memory summaries |
| Runtime state | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime` (`present`) | final run state; useful for diagnosis, not a substitute for probe-time snapshots |

## Lane A Selective Legibility Audit

Lane A asks whether visible reactions recover user-selected note spans under strict `segment_source_v1` source-span overlap. Text similarity and semantic similarity are not candidate-admission paths.

| Label | Count | Reviewer interpretation |
| --- | ---: | --- |
| `exact_match` | 2 | exact: the reaction span is identical to the aligned note span, so it is credited without semantic judging. |
| `focused_hit` | 7 | focused: the admitted span overlaps the note target and judge says the reaction captures the note-level meaning closely enough for recall credit. |
| `incidental_cover` | 0 | incidental: the reaction touches the note span but its attention is elsewhere; useful as support, not recall credit. |
| `miss` | 16 | miss: no credit; either no strict source-overlap candidate existed or admitted candidates did not satisfy focused recall. |
| `unlocatable diagnostic` | 0 | recorded as locator evidence only; never credited as candidate/match/recall |

### Case-Level Evidence

#### `e0002` — `exact_match`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002`
- source target: p81@0-23: 有时候，只有经过失败的历练，我们才能懂得谦卑。
- matched reaction: `rx:Full_Content:src:c1:p77@0-p81@23:discern:37`
- reaction text: 前面已经用墨菲的故事铺陈了，这里是一句直接的结论性陈述。但它加了一个"只有"——意味着没有失败这个历练，谦卑是学不到的，前面的成功再多也学不会。这和前文"没有一个人说我谦卑"形成呼应：芒格自己身边这些强人都没学会谦卑，因为他们还没有经足够失败的历练。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002.json`

#### `e0015` — `exact_match`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015`
- source target: p310@100-112: 打得过就打，打不过就跑。
- matched reaction: `rx:Full_Content:src:c1:p307@0-p310@112:highlight:134`
- reaction text: 结论干脆，没有道德色彩。这和前文"攥在手里，不意味着永远"的立场一致：不是不能动，是形势不好时不硬撑。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015.json`

#### `e0006` — `focused_hit`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006`
- source target: p99@0-81: 多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？” 他回答道：“查理，我这鱼钩又不是卖给鱼的。”
- matched reaction: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:42`
- reaction text: 这句话的力度来自它直接的逻辑：买家才是目标，鱼不是。整个段落的讽刺力量都在这句短回应里——不需要解释，笑完就懂了。
- source-span relation: `note_contains_candidate; coverage=0.15`
- judge / runner reason: The reaction's quoted span precisely captures the punchline ('查理，我这鱼钩又不是卖给鱼的。'), which is the core insight of the entire note. The reaction's analysis focuses directly on this specific quote, explaining its satirical logic about targeting buyers rather than fish. Although the note includes the story setup, the reactio…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006.json`

#### `e0007` — `focused_hit`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007`
- source target: p101@16-62: 所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
- matched reaction: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:41`
- reaction text: 这个"所有人"把前面的所有铺垫（销售员、顾问、律师）都收进去了。芒格不是在骂某个职业，他是在指出一件每个人都干的事。没有控诉感，只有冷静的描述，这是最难以反驳的批评方式。
- source-span relation: `candidate_contains_note; coverage=1.00`
- judge / runner reason: The reaction directly engages with the note's core idea about '所有人' (everyone) having this subconscious bias. It analyzes why Munger's use of '所有人' is rhetorically powerful—encompassing all previously mentioned professions (salespeople, consultants, lawyers) without accusation. The reaction is specifically focused on …
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007.json`

#### `e0001` — `miss`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0001`
- source target: p70@0-30: 这证明，一家公司建立了好的文化之后，就能走上良性循环的轨道。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0001.json`

#### `e0003` — `miss`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0003`
- source target: p82@0-102: 用“谦卑”这个词也许不太恰当，可能用“务实”这个词更合适。我们能取得今时今日的成就，不是因为我们的能力比别人高出多少，而是我们比别人更清楚自己能力的大小。清楚自己能力的大小，这个品质应该不能说是“谦卑”。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0003.json`

#### `e0004` — `miss`

- note case id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0004`
- source target: p83@62-99: 一件事，他没彻底弄明白之前，是绝对不会做的。一笔交易，等上五年，他都能等。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0004.json`

### Miss-Mode Aggregation

- `no_source_overlap_candidate`: 16. No visible reaction entered the candidate set under strict source-span overlap. Do not infer a hidden semantic hit from thematic proximity.

### Unlocatable Source-Locator Diagnostics

- None recorded for this shard.

## Lane B Memory Quality Audit

Lane B asks whether probe-time memory state retains salient, source-faithful, organized understanding at five semantic-probe checkpoints. Final runtime dumps can help diagnose, but probe-time snapshots remain the scoring evidence.

| Probe | Position | Overall | Salience | Mainline | Organization | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | near 20% | 4 | 4 | 4 | 4 | 4 |
| 2 | near 40% | 3.25 | 3 | 3 | 3 | 4 |
| 3 | near 60% | 2.25 | 2 | 2 | 2 | 3 |
| 4 | near 80% | 2.75 | 3 | 2 | 3 | 3 |
| 5 | window end | 3.25 | 3 | 3 | 3 | 4 |

### Probe 1 — near 20%

#### Probe Position And Question

- target / captured: `c1-s411` -> `c1-s411`
- boundary kind: `annual chapter close`
- why this probe point: Closes the 1988 discussion before the 1989 turn, giving a semantically complete checkpoint for the early management-trust and valuation discipline material.
- structural signals to check:
  - 1988 annual discussion closure
  - management trust and reputation
  - valuation discipline before the 1989 shift

#### Source Orientation

- capture-neighborhood excerpt: 在今年的伯克希尔年报中，沃伦写道，回顾过去，他感到后悔，有些公司生意非常好，但是他因为不看好公司的管理层，而没有大量买入。 / 与之形成对照的是，西科不是好生意，但我们的股东因为信任管理层而买入。 / [3] 1987年，伯克希尔以七亿美元买进所罗门兄弟公司20%的优先股，其中的一亿美元由西科及其子公司投资。
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
- `wesco_1987_structure`: 1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险） Source: `src:c1:p4@0-p4@172`: 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属…
- `wesco_board_composition`: 西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量 Source: `src:c1:p23@0-p23@57`: 好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。
- `adverse_selection_as_design`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。 Source: `src:c1:p142@18-p142@75`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
- `agency_cost_commoditization`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。 Source: `src:c1:p73@56-p73@100`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
- `humility_through_success_tension`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。 / 清楚自己能力的大小，这个品质应该不能说是'谦卑'。 Source: `src:c1:p76@0-p76@140`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人…
- `liquidation_value_ethical_constraint`: 有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。 Source: `src:c1:p174@0-p174@33`: 有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。

#### What The Mechanism Retained

- The snapshot retains strong, important material across multiple dimensions. Key retained items include: Wesco's three-branch structure (互助储蓄, 精密钢材, 西科保险), the annual-one-deal acquisition discipline, the defensive posture when both acquisition and equity markets close, the management quality criteria (Munger's 'thrown off train' test), and the Solomon invest…

#### What It Missed Or Distorted

- no significant drift or false material. Organization is solid with clear conceptual clusters and thematic threading. Rating 4.

#### Score Rationale

- scores: salience `4`, mainline `4`, organization `4`, fidelity `4`, overall `4`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains strong, important material across multiple dimensions. Key retained items include: Wesco's three-branch structure (互助储蓄, 精密钢材, 西科保险), the annual-one-deal acquisition discipline, the defensive posture when both acquisition and equity markets close, the management quality criteria (Munger's 'thrown off train' test), and the Solomon investment with AA rating and John Gutfreund's credit-risk vigilan…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` filtered by `probe_index=1`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[0]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 2 — near 40%

#### Probe Position And Question

- target / captured: `c1-s710` -> `c1-s710`
- boundary kind: `major argument turn`
- why this probe point: Ends the anti-forecasting and cash-optionality argument before the Mutual Savings topic expands the 1989 material.
- structural signals to check:
  - anti-forecasting investment posture
  - cash optionality
  - disclosure boundary and Mutual Savings transition

#### Source Orientation

- capture-neighborhood excerpt: 我们不发表评论，既不代表我们正在大量买入可口可乐（Coca-Cola），也不代表我们已经停止买入。 / 不发表评论就是不发表评论，没什么隐藏含义，不必揣摩猜测。 / 互助储蓄前途坎坷、忧患重重
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
- `wesco_1987_structure`: 1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险） Source: `src:c1:p4@0-p4@172`: 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属…
- `wesco_board_composition`: 西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量 Source: `src:c1:p23@0-p23@57`: 好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。
- `adverse_selection_as_design`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。 Source: `src:c1:p142@18-p142@75`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
- `agency_cost_commoditization`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。 Source: `src:c1:p73@56-p73@100`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
- `humility_through_success_tension`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。 / 清楚自己能力的大小，这个品质应该不能说是'谦卑'。 Source: `src:c1:p76@0-p76@140`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人…
- `munger_market_timing_record`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇"黑色星期一"，道指狂泻508点，单日跌幅超过20%。 / 所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们… Source: `src:c1:p6@0-p10@64`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股…

#### What The Mechanism Retained

- The snapshot retains solid material on Wesco's asset posture (攥在手里不意味着永远, 两条路都关闭的守势), the disclosure boundary rule (recent_reactions: '不谈论' as cognitive boundary, '不发表评论就是不发表评论'), and company structure.

#### What It Missed Or Distorted

- the 'anti-forecasting investment posture' as a coherent framework is fragmented—the Osler/Carlyle '与其为朦胧的未来而烦恼忧虑，不如脚踏实地' quote (which anchors the entire anti-forecast argument) and the 'no long-term planning' principle are in the source but absent from active digest items or concept_digest, weakening salience. More critically for this probe point, the 'boun…

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains solid material on Wesco's asset posture (攥在手里不意味着永远, 两条路都关闭的守势), the disclosure boundary rule (recent_reactions: '不谈论' as cognitive boundary, '不发表评论就是不发表评论'), and company structure. However, the 'anti-forecasting investment posture' as a coherent framework is fragmented—the Osler/Carlyle '与其为朦胧的未来而烦恼忧虑，不如脚踏实地' quote (which anchors the entire anti-forecast argument) and the 'no long-term planning…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` filtered by `probe_index=2`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[1]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 3 — near 60%

#### Probe Position And Question

- target / captured: `c1-s1052` -> `c1-s1053`
- boundary kind: `crisis appendix argument turn`
- why this probe point: Completes the causal explanation of policy changes in the S&L crisis before the text moves into broader judgment.
- structural signals to check:
  - S&L crisis mechanics
  - regulatory incentives and unintended consequences
  - causal explanation before normative judgment

#### Source Orientation

- capture-neighborhood excerpt: 或许是生物学家加勒特·哈丁（Garrett Hardin）说过，或许是经济学家乔治·斯蒂格勒（George Stigler）说过：“这是必然的结果！” / 这不是自由市场经济制度，而是毁灭价值的经济制度 / 总之，事情发展到现在，所有经营稳健、业务清晰、管理良好的储贷机构，它们谨慎地防范利率变化风险和信用损失风险，结果却根本无法实现盈利。
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
- `wesco_1987_structure`: 1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险） Source: `src:c1:p4@0-p4@172`: 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属…
- `wesco_board_composition`: 西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量 Source: `src:c1:p23@0-p23@57`: 好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。
- `adverse_selection_as_design`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。 Source: `src:c1:p142@18-p142@75`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
- `agency_cost_commoditization`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。 Source: `src:c1:p73@56-p73@100`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
- `humility_through_success_tension`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。 / 清楚自己能力的大小，这个品质应该不能说是'谦卑'。 Source: `src:c1:p76@0-p76@140`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人…
- `munger_market_timing_record`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇"黑色星期一"，道指狂泻508点，单日跌幅超过20%。 / 所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们… Source: `src:c1:p6@0-p10@64`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股…

#### What The Mechanism Retained

- The snapshot retains important S&L crisis insights in recent_reactions (policy combinations as locked system, '九龙治水' fragmentation diagnosis, complexity theory observation),

#### What It Missed Or Distorted

- critically omits the detailed causal mechanism that should anchor this probe point. The causal chain from '制度的死穴' through deregulated incentives to moral hazard gambling with taxpayer money is present in the source text's appendix but absent from active focus items, concept digest, and thread digest. Instead, active focus items center on Wesco's operational…

#### Score Rationale

- scores: salience `2`, mainline `2`, organization `2`, fidelity `3`, overall `2.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains important S&L crisis insights in recent_reactions (policy combinations as locked system, '九龙治水' fragmentation diagnosis, complexity theory observation), but critically omits the detailed causal mechanism that should anchor this probe point. The causal chain from '制度的死穴' through deregulated incentives to moral hazard gambling with taxpayer money is present in the source text's appendix but absent…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` filtered by `probe_index=3`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[2]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 4 — near 80%

#### Probe Position And Question

- target / captured: `c1-s1418` -> `c1-s1418`
- boundary kind: `section close`
- why this probe point: Closes the 1990 S&L crisis section before the text shifts toward Graham and risk-arbitrage lessons.
- structural signals to check:
  - 1990 crisis recap
  - regulator exhaustion
  - transition from crisis diagnosis to investing doctrine

#### Source Orientation

- capture-neighborhood excerpt: 审计恶劣的储贷机构，如同打一场艰苦的持久战。 / 谁都不可能在残酷的战场上坚持很长时间。 / 本·格雷厄姆教我们的重要一课
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
- `wesco_1987_structure`: 1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险） Source: `src:c1:p4@0-p4@172`: 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属…
- `wesco_board_composition`: 西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量 Source: `src:c1:p23@0-p23@57`: 好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。
- `adverse_selection_as_design`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。 Source: `src:c1:p142@18-p142@75`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
- `agency_cost_commoditization`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。 Source: `src:c1:p73@56-p73@100`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
- `humility_through_success_tension`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。 / 清楚自己能力的大小，这个品质应该不能说是'谦卑'。 Source: `src:c1:p76@0-p76@140`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人…
- `munger_market_timing_record`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇"黑色星期一"，道指狂泻508点，单日跌幅超过20%。 / 所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们… Source: `src:c1:p6@0-p10@64`: 芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股…

#### What The Mechanism Retained

- The snapshot retains the 1990 S&L crisis recap with reasonable fidelity—the industry's self-inflicted wounds, the shame of lobbying, the system design failures (government backstop + no rate limits = gambling), and critically, the regulator exhaustion material (six weeks for a small company audit, nine months for a large one, the '持久战' metaphor).

#### What It Missed Or Distorted

- the probe's explicit structural signal 'transition from crisis diagnosis to investing doctrine' is entirely absent. The source text explicitly signals that after closing the 1990 S&L crisis section, the text will shift toward Graham and risk-arbitrage lessons; the snapshot shows no forward-looking conceptual bridge toward this next doctrinal phase. The reta…

#### Score Rationale

- scores: salience `3`, mainline `2`, organization `3`, fidelity `3`, overall `2.75`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains the 1990 S&L crisis recap with reasonable fidelity—the industry's self-inflicted wounds, the shame of lobbying, the system design failures (government backstop + no rate limits = gambling), and critically, the regulator exhaustion material (six weeks for a small company audit, nine months for a large one, the '持久战' metaphor). However, the probe's explicit structural signal 'transition from crisi…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` filtered by `probe_index=4`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[3]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 5 — window end

#### Probe Position And Question

- target / captured: `c1-s1755` -> `c1-s1755`
- boundary kind: `window end`
- why this probe point: Ends the active window, allowing the final snapshot to cover the full selected annual-letter span.
- structural signals to check:
  - full-window investment doctrine continuity
  - crisis-to-risk-arbitrage arc
  - Munger/Buffett operating principles across the window

#### Source Orientation

- capture-neighborhood excerpt: （3）冠军国际（Champion International）1989年12月6日，西科和它的一些子公司投资2300万美元买入冠军国际新发行的可转换优先股。 / 该股票每年派发9.25%的股息，冠军国际必须在10年内赎回，并可按每股38美元转换为冠军国际的普通股。”
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
- `wesco_1987_structure`: 1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险） Source: `src:c1:p4@0-p4@172`: 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属…
- `wesco_board_composition`: 西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量 Source: `src:c1:p23@0-p23@57`: 好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。
- `adverse_selection_as_design`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。 Source: `src:c1:p142@18-p142@75`: 我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
- `agency_cost_commoditization`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。 Source: `src:c1:p73@56-p73@100`: 参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
- `ben_graham_trap_story`: 答对最多的那个人，真会做的只有三道，其他都是蒙的。连蒙带猜，才勉强答对了一半多点。 / 也许大多数储贷机构的高管定力很强，能不为所动。反正格雷厄姆设置陷阱，让我和沃伦·巴菲特上当，我们是没逃过去。好在本·格雷厄姆是个天才，在我们遇到的人中，很少有像他那么聪明的。另外，我们很清楚自己的不足，很清楚有很多事我们做不到，所以我们谨小慎微地留在… Source: `src:c1:p560@43-p560@84`: 答对最多的那个人，真会做的只有三道，其他都是蒙的。连蒙带猜，才勉强答对了一半多点。
- `humility_through_success_tension`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。 / 清楚自己能力的大小，这个品质应该不能说是'谦卑'。 Source: `src:c1:p76@0-p76@140`: 我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人…

#### What The Mechanism Retained

- The snapshot retains several well-sourced concrete items (Wesco's three subsidiaries, asset deployability stance, Ben Graham trap story, humility/competence tension) with accurate quotes and source citations.

#### What It Missed Or Distorted

- it misses significant structural material from the source: the '形势比人强' (form overpowers people) thesis, which is explicitly identified as the organizing theme of the 1989 meeting and appears again in 1990, receives only peripheral mention. The detailed S&L crisis analysis presented in two major appendices (covering regulatory failures, junk bond risks, and …

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains several well-sourced concrete items (Wesco's three subsidiaries, asset deployability stance, Ben Graham trap story, humility/competence tension) with accurate quotes and source citations. However, it misses significant structural material from the source: the '形势比人强' (form overpowers people) thesis, which is explicitly identified as the organizing theme of the 1989 meeting and appears again in 1…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl` filtered by `probe_index=5`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[4]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

## Callback / FVI Audit

Callback audit reads visible reactions, not memory state. A grounded callback correctly reconnects to earlier visible material; weak callback gestures at prior material but with loose or underspecified anchoring; FVI is a false visible integration; local-only makes no callback claim.

| Label | Count | What it means |
| --- | ---: | --- |
| grounded callback | 43 | credited visible continuity |
| weak callback | 13 | attempted continuity with loose or incomplete grounding |
| false visible integration | 0 | visible continuity claim judged unsupported or wrong |
| local-only reaction | 214 | visible reaction without callback claim |

### Grounded Callback Examples

#### `rx:Full_Content:src:c1:p34@0-p38@97:highlight:16`

- reaction: 这里"现在没一个"和前文那句"这是现在，不意味着永远"形成呼应——不是手里没钱，而是没有值得出手的好标的。持有资本等待是主动姿态，不是被动困局。
- prior-link evidence: no structured prior_link present
- judge reason: 明确声称与前文'这是现在，不意味着永远'形成呼应，两个文本位置相近，关联具体且可查。
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:18`

- reaction: 这句话把收购的难度从偶然性提升为规律性——"好事多磨"不是概率问题，而是本质特征。任何试图绕开这一规律的做法，"很难有好结果"。前文那句"一年也只能做成一笔"在这里获得了逻辑支撑：不是慢，是本来就应该慢。
- prior-link evidence: ref_ids=['concept:annual_one_deal_discipline']
- judge reason: prior_link指向'concept:annual_one_deal_discipline'，将'好事多磨'与'一年只能做成一笔'做了明确的逻辑关联，具体可查。
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:19`

- reaction: 这里的"守势"值得关注：不是手里没钱，而是两条主动路都暂时关闭后的主动选择。结合前文"攥在手里，这是现在，不意味着永远"的立场，守势是等待机会的姿态，和被迫收缩是两回事。
- prior-link evidence: ref_ids=['active_attention:wesco_asset_deployability']
- judge reason: prior_link指向'active_attention:wesco_asset_deployability'，将守势姿态锚定到前文关于资产可部署性的讨论上，关联具体。
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

### Weak Callback Examples

#### `rx:Full_Content:src:c1:p18@0-p19@88:discern:5`

- reaction: "应该"这个词在这里出现了两次，语气是自我确认式的，但并非言之凿凿。这和芒格在前面说"实在没有预测未来的能力"形成了一个有趣的对照——在储蓄银行的具体投资上，叙述者反而用"应该"来建立信心。这不是矛盾，而是层次区分：对宏观市场无法预测，对具体纾困标的的退出路径（整体出售）则有一定的把握。
- prior-link evidence: no structured prior_link present
- judge reason: 声称与前文'实在没有预测未来的能力'形成对照，但未提供具体文本位置或引用，依赖印象式关联而非锚定型引证。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p51@0-p55@64:highlight:27`

- reaction: 又一个"不凑热闹"的时刻——和前面投资的守势逻辑一脉相承。在开发商贷款业务上别人越踊跃，西科就越主动退出，说明他们不是在所有业务上都守势，而是在高风险的拥挤赛道上保持距离。
- prior-link evidence: no structured prior_link present
- judge reason: 声称与前文投资的守势逻辑一脉相承，但未提供具体锚定文本，属于印象式关联而非锚定型引用。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p61@0-p62@104:discern:28`

- reaction: 这句话是整个段落的基调锚点。把"没有预知未来的能力"放在"如履薄冰"之前，等于把不确定性设定为行动的前提条件，而不是行动的障碍——意味着你不是因为谨慎才不动，而是因为认清了现实的不可预测，才坦然接受"动也是如履薄冰"。和前面"我们出手的时候很少"的自律逻辑是一脉相承的。
- prior-link evidence: no structured prior_link present
- judge reason: 声称与前面'我们出手的时候很少'的自律逻辑一脉相承，但未提供具体文本锚定，关联依赖推断而非引用。
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
