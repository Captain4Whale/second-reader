# Digest Annotation Quality Sourcebook

Purpose: collect high-quality historical Agent reading annotations for future Digest / annotation prompt optimization.
Use when: revising annotation prompts, building judge rubrics for reader-visible notes, or selecting examples for qualitative review.
Not for: current runtime behavior, formal evidence promotion, active benchmark pointers, or proving current `attentional_v2` capability.
Update when: a reviewed run produces reusable annotation examples, a prompt revision needs stronger examples / counterexamples, or source artifacts are recataloged.

Created: `2026-06-18`

## Scope

This sourcebook is a prompt-design reference. It does not change prompts, backend/frontend runtime, active task state, or evaluation ledgers.

The main examples below favor reader-visible `reaction` / `annotation` outputs. They use short source-anchor quotes for review orientation rather than reproducing long book passages. `iterator_v1` examples are included only as `reference_only`; they are useful behaviors to study, not evidence for the current default mechanism.

## Source Priority

Primary extraction surfaces:

- `reaction_records.json` under `_mechanisms/attentional_v2/runtime/`
- `_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`
- `_runtime/activity.jsonl` rows with `reaction_emitted`
- `summary/reaction_audit_results.jsonl` and `summary/reaction_window_summaries.jsonl`
- user-level `note_cases/*.json` only through Agent `best_reaction`, not the human note itself
- report appendices such as `*_score_impact_reaction_appendix.md` and `highlight_comparison_ch1-3.md`, mainly for candidate discovery and reviewer weighting

Local inventory checked during this pass:

- `reaction_audit_results.jsonl`: `40` files
- `reaction_records.json`: `294` files
- `normalized_eval_bundle.json`: `280` files

Explicitly skipped:

- `ingest_*` probes that only test boundary / preview / Ingest behavior
- provider, model, capacity, and transport smokes
- `subsegment` runs
- human `note_cases` as if they were Agent output
- Memory Quality internal memory snapshots as primary annotation examples

## Selection Rubric

Strong annotation examples usually do at least one of these things:

- make a precise claim from a small textual anchor instead of summarizing the surrounding paragraph
- define or distinguish a concept in the author's own local terms
- notice a structural turn, reversal, or tension without inventing one
- connect to earlier material with a concrete prior anchor rather than a theme-only callback
- stay useful to a human reader beside the source text: short enough to read, specific enough to change attention
- avoid unsupported external facts, invented numbers, and generic "this echoes earlier" language

Deduplication key for future refreshes:

`source_id + mechanism + source_span/section_ref + normalized(anchor_quote) + normalized(note_content)`

## Curated Examples

### 1. Reality Replaces Fantasy

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `真正的水从浴室的喷头里流出来`
- Agent note: `「真正的水」——这三个字的形容词指向了前文s158「缓期执行的幻觉」中那个被心理期待替代的「淋浴」。在那里，水是幻觉性补偿的对象；在这里，水是感官现实的具体确认。叙述者用「真正」这个词，精确区分了心理投射与感官现实之间的距离。能够在淋浴时「深感庆幸」，说明心理适应已从想象层面收缩到最原始的感官满足——不需要多，只需要真实。`
- Why selected: turns one adjective into a grounded distinction between fantasy, sensory reality, and camp adaptation.
- Quality signal: judged as a grounded prior callback in the reaction-evidence rejudge.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 2. The Smallest Administrative Sentence

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `“是的。”`
- Agent note: `两个字终结了一个人的命运。没有解释，没有哀悼，只是一个方向被确认。在90%的死亡率之后，第二个具体的名字也走向了同一边。`
- Why selected: respects the tiny quote and reads its bureaucratic finality without padding.
- Quality signal: explicit prior-link evidence in the judge window.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 3. Inner Laughter As Psychological Evidence

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `发自内心的笑`
- Agent note: `"发自内心的笑"——不是麻木的、机械的笑，而是真实的内心反应。这与前文朋友评价"不是那种会在恐怖环境中抑郁不堪的人"构成双重锚点：一个是事后他者的确认，一个是当时自身的体验。两者共同指向同一种心理质地。`
- Why selected: connects self-experience and later external description without overclaiming.
- Quality signal: strong callback with two concrete anchors.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 4. Freedom Under Constraint

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_huochu`
- Sample role: `current_mechanism_positive`
- Quote: `选择自己的态度和行为方式的自由`
- Agent note: `这句话是全书中核心论点的最直接表述。从之前关于「爱」和「精神自由」的铺垫，到此处明确说出「选择的自由」，作者为整个集中营叙事赋予了哲学基础。需要注意的是，这与前文「帮助他人等于违规」的生存逻辑表面上看似矛盾，但作者在167段已经区分了「物质和社会条件」与「内心决定」的不同层面——外部处境限制行为选项，但不剥夺内心选择的权利。`
- Why selected: names a real local tension and resolves it through the book's own distinction.
- Quality signal: runtime `reaction_records.json` example with source-span anchored note.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_huochu/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json`

### 5. Home Rewritten By Captivity

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5`
- Sample role: `current_mechanism_positive`
- Quote: `经过我出生的街道`
- Agent note: `「回家」的悖论在此达到最深的冲击——经过出生地和旧居时，感受到的归属感竟指向集中营而非自由世界。这揭示了精神异化的终极程度：熟悉感被集中营经历重写，曾经的家已成为无法回归的异乡。`
- Why selected: extracts a sharp experiential reversal from a brief biographical detail.
- Quality signal: post-Ingest/Digest diagnostic runtime output.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/outputs/huochu_shengming_de_yiyi_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json`

### 6. Responsibility As Reversal

- Book: `活出生命的意义`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407`
- Sample role: `current_mechanism_positive`
- Quote: `生活向他提出的问题`
- Agent note: `这个翻转是全章最锐利的一刀：不是人向生活追问意义，而是生活向人发问。意义不再是被发现的抽象答案，而是被承担的具体责任。`
- Why selected: good model for compact philosophical reframing that remains tied to the sentence.
- Quality signal: surfaced in score-impact reaction appendix as a high-value candidate.
- Source path: `reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_score_impact_reaction_appendix.md`

### 7. Respecting The Teacher, Rejecting The Doctrine

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_xidaduo`
- Sample role: `current_mechanism_positive`
- Quote: `他对法义全无好奇`
- Agent note: `这是悉达多第一次明确宣告对法义本身的拒绝——不是对某个法义的某个部分，而是整个方向。他已经在沙门之道中宣告失败，现在面对佛陀，他宣告法义本身不能给他新知。但他仍然跟随，仍然敬重这个人。这种"认同人但不认同道"的姿态，将他与乔文达彻底分开。`
- Why selected: captures a central character distinction without flattening it into rebellion.
- Quality signal: runtime `reaction_records.json` with exact source anchor.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_xidaduo/outputs/xidaduo_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json`

### 8. Waiting Without Instrumental Purpose

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `我会站着等待`
- Agent note: `这句话的每个词都在减法：没有"直到"任何终点，没有"为了"任何目的，没有"除非"任何条件。等待在这里不是策略，而是存在方式。时间对我不是武器，是见证。`
- Why selected: close reading of grammatical absence; highly useful as an annotation exemplar.
- Quality signal: judged window candidate with strong local-text fit.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 9. Exterior Grace, Interior Lack

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `可他心中却并无喜悦`
- Agent note: `这一句的并列结构力道极强：外表让人愉悦，内在却空无一物。叙述没有否认他的优雅，而是把优雅和空虚同时放在同一幅肖像里。`
- Why selected: clean example of structural tension found in syntax rather than invented after the fact.
- Quality signal: strong local close-reading candidate.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 10. Arrow Image Reused As Insight

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `迅捷如箭般看穿乔文达的心思`
- Agent note: `弓箭隐喻在乔文达身上的第三次回收：从最初的向往与跟随，到此刻被看穿的恐惧和默许，"箭"不再只是朝向目标的意志，也成为洞察他人内心的速度。`
- Why selected: good motif callback with concrete earlier-image discipline.
- Quality signal: grounded callback in reaction window review.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 11. The Hidden Cost Of Listening To A King

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_f4a_quality_audit_20260419`
- Sample role: `current_mechanism_positive`
- Quote: `以王者之姿坐着`
- Agent note: `前面父亲以"王者"姿态坐着，儿子以顺从姿态站着；现在父亲说出"你会听见"，其实是在承认这场沉默已经改变了权力关系。听见不再是父亲命令儿子，而是父亲终于被迫听见儿子的意志。`
- Why selected: identifies a power shift through posture and speech role.
- Quality signal: F4A focused quality-audit candidate; useful for reading-time style.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_f4a_quality_audit_20260419/summary/report.md`

### 12. Disclosure Structure As Financial Reading

- Book: `芒格之道`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `1985年和1986年的合并净收益分解如下`
- Agent note: `从这里开始从叙述体转向表格呈现。c1-s5刚刚建立了1986年'不计投资收益'与'合并净收益'双口径的披露惯例，此处宣布将两年度并置分解——有理由预期表格将延续双口径对比的结构，甚至可能对应地拆分出1985年的投资收益项，形成完整的两年对照框架。`
- Why selected: annotation reads a table-introduction as argument structure, not just data.
- Quality signal: grounded callback in judged reaction window.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 13. Market Constraint, Not Personal Preference

- Book: `芒格之道`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `放眼望去，只能持有市政债券`
- Agent note: `"放眼望去"将约束视野从西科/伯克希尔的个别处境扩展至整个市场环境——这不是战略失误的结果，而是时代性的无选择。"真不愿意"与前文"不愿"是同一态度，但语气逐次加重，暗示这种被迫接受的处境已经持续并加深。`
- Why selected: distinguishes individual reluctance from system-level constraint.
- Quality signal: judged as a grounded local/prior reading.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 14. Weak Institution Plus Social Silence

- Book: `芒格之道`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `如此孱弱，却没人呼吁增强`
- Agent note: `"如此孱弱，却没人呼吁增强"——这个句式揭示的不是FSLIC的无力，而是政治层面的集体沉默。c1-s148说的是FSLIC自己"没能力"，这里说的是外部世界根本"不呼吁"增强它。两句话组合起来才完整：不仅弱小，而且无人正视。这比单纯的无力更致命——它意味着修复路径被彻底封死，不是没有出口，而是没人去找出口。`
- Why selected: exemplary non-fiction callback: it combines two nearby claims into a fuller institutional diagnosis.
- Quality signal: high-quality grounded callback candidate.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 15. Smart People Can Still Be Trapped

- Book: `芒格之道`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_user_level_selective_v1_active_rerun_20260419`
- Sample role: `current_mechanism_positive`
- Quote: `如果比你聪明很多的人要骗你`
- Agent note: `这是本段落的释义核心句。叙述者不是转述格雷厄姆的话，而是给出了一个主动判断——「我觉得」三个字清晰标注了这是 narrator 的解释而非格雷厄姆的原话。这一区分在文本层面制造了一个微妙的权威悬置：格雷厄姆本人在场却始终未明确说出结论，叙述者代替他完成了这个工作。欺骗与智商的不对称关系（聪明人反而更易被骗）是一个反直觉命题，它预设了「判断力」与「智慧」之间存在某种断裂。`
- Why selected: exact-match user-level case; shows narrator/source-voice discrimination.
- Quality signal: `exact_match` through Agent `best_reaction`, not human note target.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/shards/mangge_zhi_dao_private_zh__attentional_v2/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0019.json`

### 16. Industrial Leverage Versus Zero-Marginal-Cost Leverage

- Book: `纳瓦尔宝典`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_user_level_selective_v1_active_rerun_20260419`
- Sample role: `current_mechanism_positive`
- Quote: `资本、劳动力和复制边际成本为零的产品`
- Agent note: `这个分类在本地语境内并非中性罗列。资本和劳动力是工业时代的经典杠杆形式，而「代码和媒体」以括号加注形式被优先标出——括号内是当下普通人最易触及的杠杆类型。这不是平列，而是隐含的价值排序：代码和媒体是杠杆效应最强、门槛最低的形式。`
- Why selected: concrete concept distinction from list structure and parenthesis.
- Quality signal: `exact_match` through Agent `best_reaction`.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/shards/nawaer_baodian_private_zh__attentional_v2/note_cases/nawaer_baodian_private_zh__nawaer_baodian_private_zh_personal_notes__e0014.json`

### 17. Interest As The Root Of Specialization

- Book: `纳瓦尔宝典`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `真正的兴趣和热爱`
- Agent note: `这句话将专长的获得条件从能力层（无法培训）推进到动机层（真正的兴趣和热爱）。『盲目追逐热点』被直接否定——热点意味着高竞争、高可替代性，与专长的不可复制性相悖。这与前文『可培训性等于可替换性』形成镜像对称：外部追逐热点 = 外部可培训 = 内部可替换；内在真实热爱 = 不可培训 = 不可替换。热点是专长的反面。`
- Why selected: maps a local sentence into the book's concept lattice.
- Quality signal: strong grounded callback candidate.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 18. Effort Is Not The First Variable

- Book: `纳瓦尔宝典`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `比努力程度更重要`
- Agent note: `这句话把「努力」的赛道悄悄换掉了——不是在努力里面比谁更拼命，而是先决定努力的方向和同行者。「比努力程度更重要」不是否定努力，而是把它降格为次优变量。在前文时薪决策机制之后，这里又提供了一层主动筛选：你的时间和注意力应该优先流向正确的人和事，其次才轮到拼尽全力。`
- Why selected: good explanatory annotation that prevents a common misreading.
- Quality signal: grounded local/prior relation.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 19. No Shortcut To Compound Returns

- Book: `纳瓦尔宝典`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `没有快速致富的教程`
- Agent note: `这是一个不需要论证的断言，直接作为边界条件钉在那里。与前文刚建立的「迭代积累」框架形成咬合：复利的前提恰好是放弃对速度的幻想。`
- Why selected: concise and anchored; turns a slogan-like sentence into a structural constraint.
- Quality signal: judged high-value local annotation.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 20. Value Calculation As Necessity

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `tireless calculation of value`
- Agent note: `Ranking value calculation as the third most important brain function elevates it from process to necessity. This is the payoff of the earlier "principles of valuation are like principles of logic" framing: value is not treated as a preference overlay, but as a survival-adjacent cognitive function.`
- Why selected: strong definition-building move in English nonfiction.
- Quality signal: grounded callback in judged reaction window.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 21. Problem And Solution As A Two-Way Relation

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `bi-directional relationship between problem and solution`
- Agent note: `"Bi-directional" signals a structural property of the problem-solution relationship, not just a one-way inference tool. The author is saying problems reveal solutions, but possible solutions also determine which problems become visible as problems in the first place.`
- Why selected: turns abstract methodology into a clear conceptual distinction.
- Quality signal: judged local reading candidate.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 22. Marketplace Logic Becomes Socially Total

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `current_mechanism_positive`
- Quote: `sexual marketplace is functionally everywhere`
- Agent note: `The "sexual marketplace" reentry here carries the earlier economic-exchange framing into the mating domain, while the triad "hurtful, shameful, and desperate" explicitly invokes the register of antisocial taxonomy. The sentence does not merely name a market; it explains why value-seeking behavior leaks into ethically ugly forms.`
- Why selected: connects a returning term to a changed argumentative domain.
- Quality signal: grounded callback / terminology tracking.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 23. No Objective Marketplace Value

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `highlight_comparison_ch3`
- Sample role: `current_mechanism_positive`
- Quote: `There is no such thing as "objective" sexual marketplace value`
- Agent note: `This is the conceptual foundation of pSMV. The author is essentially saying attractiveness is constructed in the receiver, not the signal. This connects to semiotic theory and encoding/decoding problems - your value is only as real as someone else's perception of it. It's a useful corrective to essentialist views of beauty, though the author doesn't fully develop the implications.`
- Why selected: useful prompt example for handling quotation marks and concept boundaries.
- Quality signal: surfaced in chapter highlight comparison report.
- Source path: `reading-companion-backend/docs/evaluation/highlight_comparison_ch3.md`

### 24. Trade-Offs Against Solution Fantasy

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `highlight_comparison_ch1`
- Sample role: `current_mechanism_positive`
- Quote: `there aren't any solutions, only trade-offs`
- Agent note: `This is the honest center of the segment. The model doesn't offer optimization - it offers understanding of why optimization is impossible. The trade-offs fluctuate not just in importance but differentially (as the earlier segment on exemplars suggested, what you want from someone changes over time). This is what makes relationships feel unstable even when they're functional.`
- Why selected: compact example of reading a sentence as a methodological guardrail.
- Quality signal: surfaced in chapter highlight comparison report.
- Source path: `reading-companion-backend/docs/evaluation/highlight_comparison_ch1.md`

### 25. From Autonomous Unit To Political Weapon

- Book: `Supremacy`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407`
- Sample role: `current_mechanism_positive`
- Quote: `Instead of being an autonomous unit`
- Agent note: `The pivot 'Instead of being…could become' is the hinge: 'autonomous unit' was a research designation with soft autonomy, while 'Alphabet company' is a corporate subsidiary with hard accountability.`
- Why selected: very clear structural-turn annotation for narrative nonfiction.
- Quality signal: high-value candidate in score-impact reaction appendix.
- Source path: `reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_score_impact_reaction_appendix.md`

### 26. Design Language As Strategy

- Book: `Steve Jobs`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407`
- Sample role: `current_mechanism_positive`
- Quote: `It was the breakthrough`
- Agent note: `'Cheerful but affordable'—not cold, not luxury. Jobs names the exact aesthetic tension: warmth without exclusivity, democratized modernism for the home computer.`
- Why selected: good example of extracting product strategy from a design adjective.
- Quality signal: high-value candidate in score-impact reaction appendix.
- Source path: `reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_score_impact_reaction_appendix.md`

### 27. A Definition Becomes A Control System

- Book: `The Value of Others`
- Mechanism: `iterator_v1`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `reference_only`
- Quote: `A relationship is the medium`
- Agent note: `The opening "People want things from other people" set up a transactional frame. This passage upgrades that frame from descriptive to definitional: a relationship is not merely where exchange happens, it is the medium that makes value transfer possible.`
- Why selected: old mechanism reference for concept-definition sharpening.
- Quality signal: iterator reference example from judged reaction window; do not treat as current capability evidence.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 28. Good Business, Bad People

- Book: `芒格之道`
- Mechanism: `iterator_v1`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `reference_only`
- Quote: `生意怎么能不是好生意呢`
- Agent note: `联系前文悼词中对迪克「坚守原则、痛恨不良资产」的描述，这里的反问把问题从商业模式转向人的品格。生意本身是好的，但生意里的人出了问题。`
- Why selected: reference-only example for moving from surface question to implied diagnosis.
- Quality signal: iterator reference example; mechanism label must remain explicit.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 29. What Survives The Father's World

- Book: `悉达多`
- Mechanism: `iterator_v1`
- Run id: `attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425`
- Sample role: `reference_only`
- Quote: `还剩下什么`
- Agent note: `呼应前文关于父亲的观察——父亲"博学却仍是渴望者、探索者"。悉达多此刻不是否认父亲，而是在追问父亲所代表的整套知识世界究竟留下了什么可经受考验的东西。`
- Why selected: reference-only example for grounded prior callback in fiction.
- Quality signal: iterator reference example; useful behavior, not current evidence.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`

### 30. Wealth Is Not A Social Marker

- Book: `纳瓦尔宝典`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_long_span_vnext_phase1_20260423`
- Sample role: `current_mechanism_transition`
- Quote: `财富不是金钱，也不是地位`
- Agent note: `本章从「赚钱是技巧而非努力」的认识论起点出发，最终收束于「把自己产品化」这一极简行动公式。这个压缩过程本身值得注意：作者并未从任何经济学或金融学框架出发，而是从个人能力（专长）与杠杆工具（代码/媒体）的交叉点建构了一套完整的财富观。这与传统理财建议的「储蓄-投资-复利」路径形成鲜明对比。章节末尾关于「财富和金钱区别」的讨论（s139起）则从概念辨析角度为前文的行动框架提供了理论基础——财富不是金钱的多寡，而是系统化运转的能力。乔布斯案例（s165-168）是全章唯一的应用演示，完整展示了「识别需求缺口→构思产品形态→破解规模化」的创业逻辑闭环，与前文「缺口识别+供给+规模化」的公式（s35）形成呼应。`
- Why selected: historical `attentional_v2` example for chapter-level synthesis that still preserves specific conceptual anchors.
- Quality signal: older long-span runtime `reaction_records.json`; retain only as design inspiration.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_20260423/outputs/nawaer_baodian_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json`

### 31. Internal Emptiness Behind A Perfect Surface

- Book: `悉达多`
- Mechanism: `attentional_v2`
- Run id: `attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606`
- Sample role: `current_mechanism_positive`
- Quote: `如此渊博的父亲`
- Agent note: `这句话点出了悉达多困境的核心：知识渊博、举止完美、德高望重，却仍然无法获得内心的平静。他每日洗涤罪孽、每日更新——这暗示了一种永恒的空虚和循环的焦虑，而非真正的解脱。`
- Why selected: good example of turning a character comparison into a precise spiritual-diagnosis note.
- Quality signal: `activity.jsonl` reader-visible `reaction_emitted` event.
- Source path: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_unit_memory_text_only_smoke_xidaduo_post_ingest_v6_contract_20260606/outputs/xidaduo_private_zh__segment_1/attentional_v2/_runtime/activity.jsonl`

### 32. Cruel Reality Of Shifting Value

- Book: `The Value of Others`
- Mechanism: `attentional_v2`
- Run id: `highlight_comparison_ch1`
- Sample role: `current_mechanism_positive`
- Quote: `she will have become less valuable to him`
- Agent note: `This is the brutal crystallization of the 'plumber' analogy from 7.11. The husband doesn't consciously think 'her utility has dropped'—he just feels less attracted. And the guilt comes from sensing this discrepancy: she gave him what he wanted, and now he wants her less. The author calls this 'cruel reality.' It's not that the husband is evil—it's that the value calculus shifted, and the emotion followed.`
- Why selected: strong example of following an analogy across sections without losing the local sentence.
- Quality signal: surfaced in chapter highlight comparison report.
- Source path: `reading-companion-backend/docs/evaluation/highlight_comparison_ch1.md`

## Appendix A: Broader Candidate Map

High-yield artifact families for future refreshes:

- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_long_span_vnext_phase1_reaction_evidence_fix_rejudge_20260425/summary/reaction_window_summaries.jsonl`
  - best single source for judged grounded / weak / false visible integrations across `attentional_v2` and `iterator_v1`
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_ingest_digest_unit_memory_full_diagnostic_20260603_parallel5/**/reaction_records.json`
  - best source for current Ingest/Digest-era runtime examples
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_*/**/reaction_records.json`
  - useful transitional XML Digest / read-prompt examples
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_user_level_selective_v1_active_rerun_20260419/shards/*/note_cases/*.json`
  - use only Agent `best_reaction`; `exact_match` and `focused_hit` are strong quality signals
- `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_f4a_quality_audit_20260419/summary/report.md`
  - useful for short-window, reading-time style
- `reading-companion-backend/docs/evaluation/long_span/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407_score_impact_reaction_appendix.md`
  - useful historical high-score candidates, especially when raw runtime artifacts are hard to locate
- `reading-companion-backend/docs/evaluation/highlight_comparison_ch1.md`
- `reading-companion-backend/docs/evaluation/highlight_comparison_ch2.md`
- `reading-companion-backend/docs/evaluation/highlight_comparison_ch3.md`
  - useful for highlight/value examples, but should be backfilled to raw artifacts when used as formal prompt examples

## Appendix B: Candidate Roles

- `current_mechanism_positive`: usable as a positive pattern for future Digest / annotation prompts, though still historical unless rerun on current prompts.
- `current_mechanism_transition`: useful but tied to an older `attentional_v2` prompt surface; prefer as secondary evidence.
- `reference_only`: useful behavior from `iterator_v1` or other old surfaces; do not cite as current default behavior.
- `anti_pattern`: explicitly weak or false behavior that should shape negative instructions or judge rubrics.

## Appendix C: Weak / False Anti-Patterns

Use these as prompt-avoidance targets:

- Generic callback language: says "呼应前文" or "forms a contrast" without naming the earlier quote, event, reaction, or source coordinate.
- Theme-only similarity: connects two passages because both feel like "freedom", "value", "desire", or "humility", but cannot show a shared local object.
- Unsupported fact injection: adds external numbers, causal claims, or background facts that are not in source or prompt-visible memory.
- Manufactured tension: invents a contradiction such as "learned lesson versus not humble" when the passage does not actually place those ideas in tension.
- Over-broad continuity: treats a whole past scene as relevant when the current note only needs one concrete prior term or image.
- Source-backed note replaced by target note: user-level human note text must not be used as if the Agent produced it; only the Agent `best_reaction` counts.
- Internal-memory leakage: Memory Quality snapshots can inspire mechanism analysis, but are not reader-visible annotations.

## Appendix D: Validation Checklist

Every curated entry should have:

- Book
- Mechanism
- Run id
- Sample role
- Quote
- Agent note
- Why selected
- Quality signal
- Source path

All `iterator_v1` rows must have `Sample role: reference_only`.

When promoting an item from this sourcebook into an actual prompt:

- recheck the raw artifact if the current entry came from a report layer
- keep the quote short and source-anchored
- do not mix old-mechanism behavior into current-mechanism capability claims
- pair positive examples with at least one anti-pattern from Appendix C
