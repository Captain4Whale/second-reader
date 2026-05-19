# Eval-1 Window Audit Dossier: 纳瓦尔宝典

This page is a reviewer audit dossier for one Eval-1 Retry1 window. It is evidence interpretation only: no eval was run to produce this page, no catalog entry is created here, and no product-quality or formal-authority claim is made.

## Window Verdict

纳瓦尔宝典 is the strongest Lane A selective-legibility shard in this run, but still leaves 11 missed note cases. Lane B memory is comparatively healthy at MQ 3.65, with the main review work concentrated on structural omissions rather than total loss. Callback audit records 6 grounded and 4 weak callbacks, with 1 FVI; these are callback-quality diagnostics, not proof of product-level reading quality.

| Channel | Result | Reviewer boundary |
| --- | --- | --- |
| Lane A selective legibility | recall `0.4348` over `23` note cases | exact/focused count toward recall; incidental and miss do not |
| Lane B Memory Quality | average `3.65` over `5` probes | evaluates state retention/organization, not visible reaction quality |
| Callback/FVI | grounded `6`, weak `4`, FVI `1` | visible callback correctness is separate from memory quality |

## Window-Specific Reading

- Lane A pattern: `10` of `23` note cases received recall credit, while `11` remained misses. The dominant miss mode below should be read as a candidate-admission / visible-reaction coverage issue, not as proof that the mechanism understood nothing about those notes.
- Lane B strongest probe: probe `4` at `near 80%` scored `5` because The snapshot captures the chapter's culminating synthesis '把自己产品化' with full fidelity, including the two-pillar structure that maps '自己' (uniqueness + responsibility + expertise) to '产品化' (leverage + expertise). All three structural signals are strongly retai…
- Lane B weakest probe: probe `1` at `near 20%` scored `3.25`; main reviewer concern: the foundational structural signal of wealth vs. money vs. status as a three-way distinction is absent—no concept in the digest explicitly captures this trinity. Furthermore, the source's wealth creation formula '提供其有需求但无从获得的东西，并实现规模化' is missing the scale co…
- Callback/FVI pattern: this window has `1` FVI, so reviewer should inspect the FVI section before treating callback counts as encouraging.

## Evidence Map

| Evidence | Path | What to inspect |
| --- | --- | --- |
| Lane A aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/summary/aggregate.json` (`present`) | label counts, recall, unlocatable diagnostics |
| Lane A note cases | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases` (`present`) | per-note source targets, candidates, judge labels |
| Lane A rebuilt bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/rebuilt_bundles/nawaer_baodian_private_zh__segment_1/attentional_v2/normalized_eval_bundle.json` (`present`) | normalized visible reactions used for matching |
| Lane B aggregate | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/aggregate.json` (`present`) | MQ and callback totals |
| Lane B MQ rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` (`present`) | probe scores and judge reasons |
| Lane B reaction audit rows | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/reaction_audit_results.jsonl` (`present`) | grounded/weak/FVI/local-only labels |
| Probe snapshots | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` (`present`) | probe-time state evidence; primary MQ audit source |
| Normalized eval bundle | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json` (`present`) | visible reactions and memory summaries |
| Runtime state | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime` (`present`) | final run state; useful for diagnosis, not a substitute for probe-time snapshots |

## Lane A Selective Legibility Audit

Lane A asks whether visible reactions recover user-selected note spans under strict `segment_source_v1` source-span overlap. Text similarity and semantic similarity are not candidate-admission paths.

| Label | Count | Reviewer interpretation |
| --- | ---: | --- |
| `exact_match` | 8 | exact: the reaction span is identical to the aligned note span, so it is credited without semantic judging. |
| `focused_hit` | 2 | focused: the admitted span overlaps the note target and judge says the reaction captures the note-level meaning closely enough for recall credit. |
| `incidental_cover` | 2 | incidental: the reaction touches the note span but its attention is elsewhere; useful as support, not recall credit. |
| `miss` | 11 | miss: no credit; either no strict source-overlap candidate existed or admitted candidates did not satisfy focused recall. |
| `unlocatable diagnostic` | 1 | recorded as locator evidence only; never credited as candidate/match/recall |

### Case-Level Evidence

#### `e0004` — `exact_match`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004`
- source target: p15@0-41: 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
- matched reaction: `rx:Full_Content:src:c1:p14@0-p15@41:highlight:7`
- reaction text: 把工资劳动称为"出租时间"是很犀利的表述——它把这种交易模式的本质暴露出来了：你在出卖生命时间，换来一次性报酬，但没有积累任何生产资料。这种命名方式本身就带有一股揭示感。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0004.json`

#### `e0010` — `exact_match`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010`
- source target: p33@0-43: 专长指的是无法通过培训获得的知识。如果社会可以培训你，那么社会也可以培训他人来取代你。
- matched reaction: `rx:Full_Content:src:c1:p32@0-p35@30:highlight:10`
- reaction text: 这个"如果……那么"的反事实结构很犀利——它把专长的反面说成是"可替代性"，等于给专长下了一个功能性定义：不是"你会什么"，而是"别人不会什么，而且学不来"。
- source-span relation: `exact_same_span; coverage=1.00`
- judge / runner reason: Visible reaction source span exactly matched the aligned note span.
- Reviewer reading: this is strong selective legibility evidence because the visible reaction landed on the exact human-note span; the semantic quality can still be debated, but recall credit is mechanically justified.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0010.json`

#### `e0019` — `focused_hit`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019`
- source target: p86@0-81: 这句话有两个重点，一个是“自己”，一个是“产品化”。“自己”具有独特性，“产品化”是发挥杠杆效应；“自己”具有责任感，“产品化”需要专长。“自己”其实也具有专长。
- matched reaction: `rx:Full_Content:src:c1:p85@0-p88@72:highlight:32`
- reaction text: 这个"交叉重叠"的结构很有意思："专长"既是"产品化"的门槛，也是"自己"本来就有的东西。作者用这个词的双重归属，把整个分散的理念体系——责任感、判断力、独特性、杠杆——全部锚定在这两个词的交叉点上。
- source-span relation: `partial_overlap; coverage=0.68`
- judge / runner reason: The reaction's quoted source span covers the core substantive content of the note—the examples tying "自己" to uniqueness, responsibility, and expertise, and "产品化" to leverage and expertise. The reaction's analysis directly interprets this structural overlap, explaining how "专长" serves as a double-anchor that connects t…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0019.json`

#### `e0023` — `focused_hit`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023`
- source target: p98@67-146: 社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。
- matched reaction: `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`
- reaction text: "轻松自然"这个条件与前面"专长累积像玩耍"形成精确呼应——两个标准合并成一个更完整的检验：如果你做的事既像玩耍，又是轻松自然的，那它大概率就是你真正的专长所在，也可能是财富的入口。
- source-span relation: `note_contains_candidate; coverage=0.41`
- judge / runner reason: The reaction specifically targets the "轻松自然" portion of the overlapped source span and develops a substantive analysis by connecting it to another principle ("专长累积像玩耍") to form a combined test for identifying one's true expertise. While the note covers a broader theme (wealth creation through providing what society ne…
- Reviewer reading: this is meaningful but judge-mediated evidence; the source overlap alone is insufficient, so the important question is whether the visible reaction actually centers the note-level idea.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0023.json`

#### `e0002` — `incidental_cover`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002`
- source target: p3@136-215: 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
- matched reaction: `rx:Full_Content:src:c1:p1@0-p3@215:highlight:2`
- reaction text: 财富三要素：做什么（内容选择）、和谁（合作伙伴/团队）、什么时候（时机判断）。不是埋头苦干，而是这三个维度的决策质量决定结果。
- source-span relation: `note_contains_candidate; coverage=0.37`
- judge / runner reason: The reaction's quoted span (136-165) covers only the first sentence about the three wealth elements, which is indeed a core part of the note. However, the note also contains important content about 'understanding and thinking being more important than hard work' and 'choosing the correct approach,' which are not cover…
- Reviewer reading: this is not recall success. The mechanism touched nearby or overlapping text but did not make the human-note idea its main object.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0002.json`

#### `e0001` — `miss`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0001`
- source target: p3@94-112: 赚钱跟工作的努力程度没什么必然联系。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0001.json`

#### `e0003` — `miss`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0003`
- source target: p9@0-67: 追求财富，而不是金钱或地位。财富是指在你睡觉时仍能为你赚钱的资产。金钱是我们转换时间和财富的方式。地位是你在社会等级体系中所处的位置。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0003.json`

#### `e0005` — `miss`

- note case id: `nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0005`
- source target: p17@0-37: 获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。
- matched reaction: `(no matched reaction)`
- source-span relation: no admitted matched reaction
- judge / runner reason: no_candidate_source_span_overlap
- Reviewer reading: this remains a miss under strict admission. Mode `no_source_overlap_candidate` means the report should not infer invisible understanding from broader thematic similarity.
- raw artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_nawaer/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0005.json`

### Miss-Mode Aggregation

- `no_source_overlap_candidate`: 11. No visible reaction entered the candidate set under strict source-span overlap. Do not infer a hidden semantic hit from thematic proximity.

### Unlocatable Source-Locator Diagnostics

- `rx:Chapter_1:src:c1:p99@193-p99@193:retrospect:1`

These diagnostics are intentionally not counted as matches. They identify reactions whose source location could not be turned into a usable `segment_source_v1` candidate for Lane A matching.

## Lane B Memory Quality Audit

Lane B asks whether probe-time memory state retains salient, source-faithful, organized understanding at five semantic-probe checkpoints. Final runtime dumps can help diagnose, but probe-time snapshots remain the scoring evidence.

| Probe | Position | Overall | Salience | Mainline | Organization | Fidelity |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | near 20% | 3.25 | 3 | 3 | 3 | 4 |
| 2 | near 40% | 3.5 | 3 | 4 | 3 | 4 |
| 3 | near 55% | 3.25 | 3 | 3 | 3 | 4 |
| 4 | near 80% | 5 | 5 | 5 | 5 | 5 |
| 5 | window end | 3.25 | 3 | 3 | 3 | 4 |

### Probe 1 — near 20%

#### Probe Position And Question

- target / captured: `c1-s35` -> `c1-s35`
- boundary kind: `foundational thesis cluster close`
- why this probe point: Closes the opening wealth thesis cluster, where the text distinguishes wealth from money/status and introduces scale.
- structural signals to check:
  - wealth vs money vs status
  - renting time vs owning equity/assets
  - unmet demand and scale

#### Source Orientation

- capture-neighborhood excerpt: ∨ / 获得财富的一个途径，就是为社会提供其有需求但无从获得的东西，并实现规模化。 / ∨
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 2 | current semantic items still available to the reader |
| active focus items | 2 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 2 | abstraction / reusable concept evidence |
| thread digest | 0 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 7 | grounding support, not a fidelity score by itself |

Key state evidence:
- `find_leverage_points`: 观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富 Source: `src:c1:p5@67-p5@124`: 我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- `ignore_status_seekers`: 追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。 Source: `src:c1:p13@0-p13@33`: 无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
- `equity_ownership_wealth_path`: 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。 Source: `src:c1:p15@0-p15@41`: 依靠出租时间是不可能致富的。你必须拥有股权（企业的部分所有权），才能实现财务自由。
- `wealth_creation_frame`: 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。 Source: `src:c1:p3@136-p3@184`: 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。与埋头苦干相比，更重要的是理解和思考。

#### What The Mechanism Retained

- The snapshot retains several key concepts including equity ownership as the wealth path and the leverage-points observation skill, and correctly captures the ignore-status-seekers principle.

#### What It Missed Or Distorted

- the foundational structural signal of wealth vs. money vs. status as a three-way distinction is absent—no concept in the digest explicitly captures this trinity. Furthermore, the source's wealth creation formula '提供其有需求但无从获得的东西，并实现规模化' is missing the scale component entirely; only the unmet demand phrase appears implicitly via one highlight. The moral compa…

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains several key concepts including equity ownership as the wealth path and the leverage-points observation skill, and correctly captures the ignore-status-seekers principle. However, the foundational structural signal of wealth vs. money vs. status as a three-way distinction is absent—no concept in the digest explicitly captures this trinity. Furthermore, the source's wealth creation formula '提供其有需求…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` filtered by `probe_index=1`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[0]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 2 — near 40%

#### Probe Position And Question

- target / captured: `c1-s62` -> `c1-s65`
- boundary kind: `specific-knowledge cluster close`
- why this probe point: Closes the specific-knowledge discussion before leverage becomes the dominant frame.
- structural signals to check:
  - specific knowledge definition
  - sales/build pairing
  - interest, apprenticeship, and non-outsourcable skill

#### Source Orientation

- capture-neighborhood excerpt: 培养责任感，勇于以个人名义承担商业风险。 / 社会将根据责任大小、股权多少和杠杆效应回报你。 / ∨
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 4 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 0 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `find_leverage_points`: 观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富 Source: `src:c1:p5@67-p5@124`: 我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- `ignore_status_seekers`: 追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。 Source: `src:c1:p13@0-p13@33`: 无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
- `compound_returns_life`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。 Source: `src:c1:p23@7-p23@38`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。
- `dual_core_competencies`: 学会销售，学会构建，两技傍身，势不可当。 Source: `src:c1:p29@0-p29@20`: 学会销售，学会构建，两技傍身，势不可当。

#### What The Mechanism Retained

- The snapshot retains strong individual items (复利回报, 股权致富, 销售构建双技傍身, 合伙人正直诚信优先) and correctly marks the transition at responsibility/leverage.

#### What It Missed Or Distorted

- the "specific knowledge" cluster's defining structure is only partially retained: the definition '专长指的是无法通过培训获得的知识' is NOT captured as a standalone definition (only the play-vs-effort downstream implication is retained), and the source's explicit three-part structure (兴趣热爱 → 师徒制传授 → 不可外包自动化) appears only as scattered visible traces (reactions) rather than a…

#### Score Rationale

- scores: salience `3`, mainline `4`, organization `3`, fidelity `4`, overall `3.5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains strong individual items (复利回报, 股权致富, 销售构建双技傍身, 合伙人正直诚信优先) and correctly marks the transition at responsibility/leverage. However, the "specific knowledge" cluster's defining structure is only partially retained: the definition '专长指的是无法通过培训获得的知识' is NOT captured as a standalone definition (only the play-vs-effort downstream implication is retained), and the source's explicit three-part structure …

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` filtered by `probe_index=2`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[1]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 3 — near 55%

#### Probe Position And Question

- target / captured: `c1-s92` -> `c1-s92`
- boundary kind: `leverage taxonomy close`
- why this probe point: Closes the leverage taxonomy, including permissioned and permissionless leverage.
- structural signals to check:
  - capital, labor, code, and media as leverage
  - permissioned vs permissionless leverage
  - robots, code, media, and data centers

#### Source Orientation

- capture-neighborhood excerpt: ∨ / 如果不会写代码，那就出书、写博客、做视频、录播客。 / ∨
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 4 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 0 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `find_leverage_points`: 观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富 Source: `src:c1:p5@67-p5@124`: 我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- `ignore_status_seekers`: 追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。 Source: `src:c1:p13@0-p13@33`: 无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
- `capital_financing_prerequisites`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。 Source: `src:c1:p49@0-p49@39`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。
- `compound_returns_life`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。 Source: `src:c1:p23@7-p23@38`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。

#### What The Mechanism Retained

- The snapshot retains individual leverage concepts (capital as money requiring financing, labor as oldest leverage, code/media as permissionless) and includes two reactions about the permissioned/permissionless distinction (labor needs hiring agreements, capital needs financing consent vs. code/media needing only personal skill accumulation).

#### What It Missed Or Distorted

- three significant gaps exist: (1) The explicit "robots, code, media, and data centers" formulation is absent—the nearby passage '有一大批机器人可供我们免费使用...这些机器人就集中放在数据中心' is not captured in any concept; (2) The core taxonomy organizing structure—capital/labor/code/media as the three-part leverage classification—exists scattered across concept_digest items but is no…

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains individual leverage concepts (capital as money requiring financing, labor as oldest leverage, code/media as permissionless) and includes two reactions about the permissioned/permissionless distinction (labor needs hiring agreements, capital needs financing consent vs. code/media needing only personal skill accumulation). However, three significant gaps exist: (1) The explicit "robots, code, medi…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` filtered by `probe_index=3`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[2]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 4 — near 80%

#### Probe Position And Question

- target / captured: `c1-s138` -> `c1-s139`
- boundary kind: `synthesis close`
- why this probe point: Closes the self-productization synthesis that combines uniqueness, responsibility, and leverage.
- structural signals to check:
  - productize yourself
  - uniqueness, responsibility, and leverage
  - long-term self-inquiry

#### Source Orientation

- capture-neighborhood excerpt: 所以我才说“把自己产品化”要花几十年——并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？ / [10] / 财富和金钱的区别是什么？
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 2 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `find_leverage_points`: 观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富 Source: `src:c1:p5@67-p5@124`: 我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- `ignore_status_seekers`: 追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。 Source: `src:c1:p13@0-p13@33`: 无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
- `capital_financing_prerequisites`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。 Source: `src:c1:p49@0-p49@39`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。
- `compound_returns_life`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。 Source: `src:c1:p23@7-p23@38`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。
- `original_pursuit_vs_wealth`: 当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。 Source: `src:c1:p83@0-p83@40`: 当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。
- `wealth_as_derivative_question`: 并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？ Source: `src:c1:p88@31-p88@68`: 并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？

#### What The Mechanism Retained

- The snapshot captures the chapter's culminating synthesis '把自己产品化' with full fidelity, including the two-pillar structure that maps '自己' (uniqueness + responsibility + expertise) to '产品化' (leverage + expertise). All three structural signals are strongly retained: (1) the 'productize yourself' formula with its two-word elaboration, (2) the uniqueness/respons…

#### What It Missed Or Distorted

- This reads as strong chapter-level memory at the synthesis point.

#### Score Rationale

- scores: salience `5`, mainline `5`, organization `5`, fidelity `5`, overall `5`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot captures the chapter's culminating synthesis '把自己产品化' with full fidelity, including the two-pillar structure that maps '自己' (uniqueness + responsibility + expertise) to '产品化' (leverage + expertise). All three structural signals are strongly retained: (1) the 'productize yourself' formula with its two-word elaboration, (2) the uniqueness/responsibility/leverage triad appearing in the active items and rea…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` filtered by `probe_index=4`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[3]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

### Probe 5 — window end

#### Probe Position And Question

- target / captured: `c1-s168` -> `c1-s169`
- boundary kind: `meaningful window end`
- why this probe point: Ends the meaningful body window before citation-only tail material.
- structural signals to check:
  - wealth-building body chapter frame
  - assets, technology, unmet needs, and scale
  - chapter-level synthesis without citation tail

#### Source Orientation

- capture-neighborhood excerpt: 然后，他们研究出了如何制造这样一部智能手机，以及如何实现规模化生产。 / [78]
- note: this is a short orientation excerpt only; use `public/book_document.json` and the snapshot coverage fields for full context.

#### Snapshot Evidence

| Layer | Count | Reviewer use |
| --- | ---: | --- |
| active attention | 6 | current semantic items still available to the reader |
| active focus items | 4 | prompt-facing focus carried into the next read |
| recent reactions | 2 | visible traces nearby in time, not durable memory by themselves |
| concept digest | 3 | abstraction / reusable concept evidence |
| thread digest | 2 | cross-local continuity evidence |
| reflective frames | 0 | slow-cycle durable framing evidence |
| source refs | 8 | grounding support, not a fidelity score by itself |

Key state evidence:
- `find_leverage_points`: 观察企业，找到最能创造财富的杠杆支点，然后抓住这部分财富 Source: `src:c1:p5@67-p5@124`: 我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- `ignore_status_seekers`: 追求地位者：以攻击创造者而非创造价值为手段获取地位。对这种人应主动无视，不将其作为竞争或说服的对象。 Source: `src:c1:p13@0-p13@33`: 无视一味追求社会地位的人。他们获得地位的手段就是攻击创造财富的人。
- `capital_financing_prerequisites`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。 Source: `src:c1:p49@0-p49@39`: 资本是指金钱。要想获得融资，需要运用自己的专长和责任感，并表现出良好的判断力。
- `compound_returns_life`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。 Source: `src:c1:p23@7-p23@38`: 生活中所有的回报，无论是财富、人际关系，还是知识，都来自复利。
- `original_pursuit_vs_wealth`: 当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。 Source: `src:c1:p83@0-p83@40`: 当你终于变得富有时，你会意识到，这并不是你最初的追求。但这是后话，此处暂且不提。
- `wealth_as_derivative_question`: 并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？ Source: `src:c1:p88@31-p88@68`: 并不是要花几十年执行，而是要把大部分时间用于思考：我能提供什么独特的价值？

#### What The Mechanism Retained

- The snapshot retains 6 active items and 3 concepts from the chapter's wealth-building body, all accurately sourced.

#### What It Missed Or Distorted

- it misses the chapter's central organizing frame: '把自己产品化' (productize yourself) — the self(unique+accountability) + productize(leverage+expertise) synthesis that unifies all principles. The wealth definition ('在你睡觉时仍能为你赚钱的资产') appears only in source_ref_digest as a passive reference, not as working memory. The three-part chapter structure (what wealth is, …

#### Score Rationale

- scores: salience `3`, mainline `3`, organization `3`, fidelity `4`, overall `3.25`
- reviewer interpretation: the score is justified only insofar as the retained state above answers the probe question; gaps above are the main reasons this is not a stronger score. Full judge reason: The snapshot retains 6 active items and 3 concepts from the chapter's wealth-building body, all accurately sourced. However, it misses the chapter's central organizing frame: '把自己产品化' (productize yourself) — the self(unique+accountability) + productize(leverage+expertise) synthesis that unifies all principles. The wealth definition ('在你睡觉时仍能为你赚钱的资产') appears only in source_ref_digest as a passive reference, not as w…

#### Manual Check

- MQ result row source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/summary/memory_quality_results.jsonl` filtered by `probe_index=5`
- probe snapshot source: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_nawaer/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` -> `snapshots[4]`
- check fields: `active_attention_digest`, `active_focus_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, `source_ref_digest`, and `coverage`.

## Callback / FVI Audit

Callback audit reads visible reactions, not memory state. A grounded callback correctly reconnects to earlier visible material; weak callback gestures at prior material but with loose or underspecified anchoring; FVI is a false visible integration; local-only makes no callback claim.

| Label | Count | What it means |
| --- | ---: | --- |
| grounded callback | 6 | credited visible continuity |
| weak callback | 4 | attempted continuity with loose or incomplete grounding |
| false visible integration | 1 | visible continuity claim judged unsupported or wrong |
| local-only reaction | 29 | visible reaction without callback claim |

### Grounded Callback Examples

#### `rx:Full_Content:src:c1:p38@0-p39@32:retrospect:13`

- reaction: 这句话和前面那句「专长指的是无法通过培训获得的知识」形成了完整的逻辑闭环：前一句给出了定义层面的约束（不可培训性），这一句给出了实践层面的约束（不可学校化）。两个「无法」指向同一个方向——专长的获得和传授都绕不开个人化的、近身的接触。
- prior-link evidence: ref_ids=['reaction:rx:Full_Content:src:c1:p32@0-p35@30:highlight:10']
- judge reason: Prior link to reaction 10 is explicit and correctly identified. The logical closure between '不可培训性' (definition layer) and '不可学校化' (practice layer) is a precise, well-supported connection back to the earlier expertise definition.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p44@0-p47@51:retrospect:16`

- reaction: 这里把商业杠杆落实为三个可识别的类别，"复制边际成本为零"这个经济学措辞精确地刻画了代码和媒体的特性——一次创造、无限分发、没有边际成本。这也呼应了前文对专长积累的描述：高杠杆的领域，往往就是那些无法被标准化、外包或自动化的个人化领域。
- prior-link evidence: ref_ids=['reaction:rx:Full_Content:src:c1:p40@0-p43@43:highlight:14', 'active_attention…
- judge reason: Prior link to reaction 14 is explicit and substantively supported. The claim that high-leverage fields align with non-standardizable personal expertise is a concrete, correct extension of reaction 14's '三个不能' framing.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

#### `rx:Full_Content:src:c1:p64@0-p67@31:discern:26`

- reaction: 这份清单与前文"判断力是杠杆的倍增器"构成直接呼应：微观经济学理解激励结构，博弈论处理策略互动，心理学和说服术指向人与人的影响，伦理学提供价值框架，数学与计算机则是建模和执行的工具——这不是随机的课程列表，而是支撑高质量判断的完整认知工具箱。
- prior-link evidence: no structured prior_link present
- judge reason: Explicitly maps the discipline list to earlier material ('判断力是杠杆的倍增器') and provides thematic connection to reaction 24's definition of judgment as cognitive capability.
- Reviewer reading: the callback is credited because the reaction names or uses earlier visible material in a way the judge found textually grounded.

### Weak Callback Examples

#### `rx:Full_Content:src:c1:p40@0-p43@43:highlight:14`

- reaction: 这句话和前文建立的专长概念形成同方向延伸：不可培训、不可学校化、不可外包自动化——三个"不能"从不同维度指向同一个结论：专长是个人化的、不可标准化的。
- prior-link evidence: no structured prior_link present
- judge reason: The content gestures at '前文' with vague self-reference but provides no explicit prior link in metadata. The claim of three 'cannots' summarizing earlier material lacks specificity about which earlier reaction is being extended.
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p89@0-p93@57:highlight:35`

- reaction: 这个定义直接呼应了"把自己产品化"的最终目标：你不是在销售时间，而是在部署一套能在你缺席时继续运转的系统。睡眠测试是一个非常直觉化的检验标准——如果一个资产停止运作你就停止收入，那它就不是真正的财富。
- prior-link evidence: no structured prior_link present
- judge reason: 声称'直接呼应把自己产品化的最终目标'，但'把自己产品化'的表述未在前文可见段落中以该措辞出现，回调方向正确但措辞缺乏可见文本支撑。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

#### `rx:Full_Content:src:c1:p94@0-p98@146:highlight:36`

- reaction: "轻松自然"这个条件与前面"专长累积像玩耍"形成精确呼应——两个标准合并成一个更完整的检验：如果你做的事既像玩耍，又是轻松自然的，那它大概率就是你真正的专长所在，也可能是财富的入口。
- prior-link evidence: no structured prior_link present
- judge reason: 声称与前面'专长累积像玩耍'形成精确呼应，但'专长累积像玩耍'并非前文可见段落中的已有表述，其所依据的reaction 12内容为问句形式，与此处断言存在落差。
- Reviewer reading: this is a real callback attempt but weak because the prior anchor is thematic, underspecified, or not textually tight enough.

### False Visible Integration Examples

#### `rx:Full_Content:src:c1:p85@0-p88@72:retrospect:33`

- reaction: 这与前面"当你终于变得富有时，你会意识到，这并不是你最初的追求"形成呼应——财富不是起点，"我能提供什么独特的价值"才是真正需要花几十年去回答的问题。
- prior-link evidence: ref_ids=['thread:original_pursuit_vs_wealth']
- judge reason: 声称呼应前文具体引文'当你终于变得富有时，你会意识到，这并不是你最初的追求'，但该引文未出现在当前阅读窗口内的可见材料中。prior_link所引的thread标签属于主题类投射，非文本级可见回调，为过拟合类集成。
- Reviewer reading: this is harmful callback evidence: the reaction presents an integration as visible continuity, but the judge could not ground that prior claim in earlier visible material.

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
