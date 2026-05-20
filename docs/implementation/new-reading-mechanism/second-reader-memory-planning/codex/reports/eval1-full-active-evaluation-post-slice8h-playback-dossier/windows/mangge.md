# Eval-1 Playback Dossier: 芒格之道

This playback page is a product-facing reading trace for human review. It replays the Eval-1 window in reading order, then explains how the four evaluation channels score that trace. It is not a new eval run, not a catalog update, not product-quality proof, and not Long Span formal authority.

## Window Verdict

- Lane A selective-legibility recall: `0.3600` over `25` note cases (`2` exact, `7` focused, `0` incidental, `16` miss).
- Lane B Memory Quality: `3.10` average over `5` semantic probes.
- Visible reaction audit: `270` reactions (`43` grounded callback, `13` weak callback, `0` FVI, `214` local-only).
- Reviewer stance: read the timeline first, then the scoring interpretation. The score is justified by the trace, not by the aggregate table alone.

## Evidence Map

- Dataset source window: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`
- Raw segment text: `reading-companion-backend/state/eval_local_datasets/user_level_benchmarks/attentional_v2_user_level_selective_v1_repaired_20260422/segment_sources/mangge_zhi_dao_private_zh__segment_1.txt`
- Lane A run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge`
- Lane B run dir: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge`
- Lane A note cases: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases`
- Lane B MQ rows: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/memory_quality_results.jsonl`
- Lane B reaction audit: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/summary/reaction_audit_results.jsonl`
- Probe snapshots: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`
- Normalized eval bundle: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/normalized_eval_bundle.json`

## Source Window And Chapter Coverage

- Covered chapters: `1987年 西科金融股东会讲话, 1988年 西科金融股东会讲话, 1989年 西科金融股东会讲话, 1990年 西科金融股东会讲话`
- Full reviewer-readable source window lives beside the dataset: `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.
- Each reaction below includes its own source-span excerpt so the reviewer can stay in reading flow, then jump to the full source window when needed.

## Selective Legibility Note-Case Ledger

This ledger lists every dataset note target in the window. Matched note cases point to the reaction that appears later in the reading timeline; misses remain visible here so reviewer analysis is not biased toward successful reactions only.

### Note `e0001` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0001`
- target note:
```text
这证明，一家公司建立了好的文化之后，就能走上良性循环的轨道。
```
- target source span(s):
  - `p70@0-30`: 这证明，一家公司建立了好的文化之后，就能走上良性循环的轨道。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0001.json`

### Note `e0002` — `exact_match`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002`
- target note:
```text
有时候，只有经过失败的历练，我们才能懂得谦卑。
```
- target source span(s):
  - `p81@0-23`: 有时候，只有经过失败的历练，我们才能懂得谦卑。
- matched reaction in timeline: `rx:Full_Content:src:c1:p77@0-p81@23:discern:37`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002.json`

### Note `e0003` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0003`
- target note:
```text
用“谦卑”这个词也许不太恰当，可能用“务实”这个词更合适。我们能取得今时今日的成就，不是因为我们的能力比别人高出多少，而是我们比别人更清楚自己能力的大小。清楚自己能力的大小，这个品质应该不能说是“谦卑”。
```
- target source span(s):
  - `p82@0-102`: 用“谦卑”这个词也许不太恰当，可能用“务实”这个词更合适。我们能取得今时今日的成就，不是因为我们的能力比别人高出多少，而是我们比别人更清楚自己能力的大小。清楚自己能力的大小，这个品质应该不能说是“谦卑”。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0003.json`

### Note `e0004` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0004`
- target note:
```text
一件事，他没彻底弄明白之前，是绝对不会做的。一笔交易，等上五年，他都能等。
```
- target source span(s):
  - `p83@62-99`: 一件事，他没彻底弄明白之前，是绝对不会做的。一笔交易，等上五年，他都能等。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0004.json`

### Note `e0005` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0005`
- target note:
```text
充分认清客观条件的限制，充分认识自身能力的限制，谨小慎微地在限制范围内活动，这是赚钱的诀窍。这个诀窍，与其说是“谦卑”，不如说是“有克制的贪婪”。
```
- target source span(s):
  - `p85@0-73`: 充分认清客观条件的限制，充分认识自身能力的限制，谨小慎微地在限制范围内活动，这是赚钱的诀窍。这个诀窍，与其说是“谦卑”，不如说是“有克制的贪婪”。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0005.json`

### Note `e0006` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006`
- target note:
```text
多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？”他回答道：“查理，我这鱼钩又不是卖给鱼的。”
```
- target source span(s):
  - `p99@0-81`: 多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？”
  - `p100@0-22`: 他回答道：“查理，我这鱼钩又不是卖给鱼的。”
- matched reaction in timeline: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:42`
- source-span relation: `note_contains_candidate`; coverage `0.1456`
- judge/runner reason: The reaction's quoted span precisely captures the punchline ('查理，我这鱼钩又不是卖给鱼的。'), which is the core insight of the entire note. The reaction's analysis focuses directly on this specific quote, explaining its satirical logic about targeting buyers rather than fish. Although the note includes the story setup, the reaction correctly identifies that the humorous and rhetorical power lies entirely in this short response, and it targets that essence without being distracted by peripheral context.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006.json`

### Note `e0007` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007`
- target note:
```text
所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
```
- target source span(s):
  - `p101@16-62`: 所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
- matched reaction in timeline: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:41`
- source-span relation: `candidate_contains_note`; coverage `1.0`
- judge/runner reason: The reaction directly engages with the note's core idea about '所有人' (everyone) having this subconscious bias. It analyzes why Munger's use of '所有人' is rhetorically powerful—encompassing all previously mentioned professions (salespeople, consultants, lawyers) without accusation. The reaction is specifically focused on the note's main insight rather than tangential content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007.json`

### Note `e0008` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0008`
- target note:
```text
我们始终把眼前所有的投资机会进行比较，力求找到当下最合理的投资逻辑，这才是重中之重。找到了最合理的投资逻辑之后，无论周期波动如何剧烈，是顺境还是逆境，我们都泰然自若。这就是我们的投资之道。
```
- target source span(s):
  - `p255@122-216`: 我们始终把眼前所有的投资机会进行比较，力求找到当下最合理的投资逻辑，这才是重中之重。找到了最合理的投资逻辑之后，无论周期波动如何剧烈，是顺境还是逆境，我们都泰然自若。这就是我们的投资之道。
- matched reaction in timeline: `rx:Full_Content:src:c1:p254@0-p257@94:highlight:106`
- source-span relation: `note_contains_candidate`; coverage `0.883`
- judge/runner reason: The visible reaction's source span covers the core content of the note's source span (comparing opportunities, finding the most reasonable logic, maintaining calm through cycles), with only the concluding sentence '这就是我们的投资之道' excluded. The commentary directly engages with the key concepts: the two-step methodology of comparing opportunities and maintaining composure, and emphasizes the significance of '重中之重' (top priority). This represents genuine focused coverage of the note's important content.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0008.json`

### Note `e0009` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0009`
- target note:
```text
威廉·奥斯勒爵士信奉托马斯·卡莱尔(Thomas Carlyle)的一句名言：“与其为朦胧的未来而烦恼忧虑，不如脚踏实地，做好眼前的事。”这同样是伯克希尔的经营哲学。
```
- target source span(s):
  - `p258@104-187`: 威廉·奥斯勒爵士信奉托马斯·卡莱尔（Thomas Carlyle）的一句名言：“与其为朦胧的未来而烦恼忧虑，不如脚踏实地，做好眼前的事。”这同样是伯克希尔的经营哲学。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0009.json`

### Note `e0010` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010`
- target note:
```text
谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
```
- target source span(s):
  - `p259@90-157`: 谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
- matched reaction in timeline: `rx:Full_Content:src:c1:p258@0-p259@190:highlight:110`
- source-span relation: `note_contains_candidate`; coverage `0.6269`
- judge/runner reason: The reaction's quoted source span (the latter half of the note) captures the core message: that good results emerge from focusing on immediate actions rather than long-term planning. The interpretation ('好公司是副产品') and the connection to the '从来不制定长期规划' theme directly address the note's essential point about practical action leading to good outcomes. The overlap is not incidental—the reaction intentionally engages with the note's central idea, even though it doesn't quote the opening rhetorical question.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010.json`

### Note `e0011` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0011`
- target note:
```text
。在我们的世界观中，我们不相信预言。我们不是纯粹的机会主义者，但我们确实信奉见机行事。我们也做长期预测，但做得很少。也许正是因为我们努力做好眼前的事，很少做长期预测，我们的长期预测才更加准确。
```
- target source span(s):
  - `p260@127-223`: 。在我们的世界观中，我们不相信预言。我们不是纯粹的机会主义者，但我们确实信奉见机行事。我们也做长期预测，但做得很少。也许正是因为我们努力做好眼前的事，很少做长期预测，我们的长期预测才更加准确。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0011.json`

### Note `e0012` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0012`
- target note:
```text
最后，还有一类人，愚蠢而又勤奋。按照陆军操典所说，此类人必须遣散。我们深有同感。一类是品行不端的人，一类是愚蠢而又勤奋的人，这两类人都是祸害。
```
- target source span(s):
  - `p268@0-33`: 最后，还有一类人，愚蠢而又勤奋。按照陆军操典所说，此类人必须遣散。
  - `p269@0-38`: 我们深有同感。一类是品行不端的人，一类是愚蠢而又勤奋的人，这两类人都是祸害。
- matched reaction in timeline: `rx:Full_Content:src:c1:p267@0-p271@59:highlight:115`
- source-span relation: `note_contains_candidate`; coverage `0.4366`
- judge/runner reason: The reaction's quoted source span captures the core claim—'品行不端' and '愚蠢而勤奋' both being hazards—from paragraph 269. While the note's source includes a preceding paragraph (268) with '必须遣散' context, the reaction's commentary explicitly discusses this military terminology and covers the note's central thesis that both categories are destructive. The coverage (43.66%) is modest but sufficient to address the note's main point.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0012.json`

### Note `e0013` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0013`
- target note:
```text
这个经历让我懂得了一个深刻的道理。决定结果的主要有两个因素：一个是形势，另一个是人。形势太强，任凭你有多大能力，都无济于事。
```
- target source span(s):
  - `p307@0-62`: 这个经历让我懂得了一个深刻的道理。决定结果的主要有两个因素：一个是形势，另一个是人。形势太强，任凭你有多大能力，都无济于事。
- matched reaction in timeline: `rx:Full_Content:src:c1:p307@0-p310@112:highlight:133`
- source-span relation: `note_contains_candidate`; coverage `0.7258`
- judge/runner reason: The reaction's quoted span (char 17-62) covers the core substantive content of the note—the two-factor framework of situation vs. person and the insight about circumstances overriding individual ability. The reaction goes beyond mere overlap to genuinely interpret and elaborate on this central message, framing it as a 'more底层' version of a related concept. The note's opening framing sentence is omitted from the quote but the important analytical content is fully captured.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0013.json`

### Note `e0014` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0014`
- target note:
```text
每当年轻人建议他冒险的时候，他总是说：“河里淹死的都是会水的。”
```
- target source span(s):
  - `p308@48-80`: 每当年轻人建议他冒险的时候，他总是说：“河里淹死的都是会水的。”
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0014.json`

### Note `e0015` — `exact_match`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015`
- target note:
```text
打得过就打，打不过就跑。
```
- target source span(s):
  - `p310@100-112`: 打得过就打，打不过就跑。
- matched reaction in timeline: `rx:Full_Content:src:c1:p307@0-p310@112:highlight:134`
- source-span relation: `exact_same_span`; coverage `1.0`
- judge/runner reason: Visible reaction source span exactly matched the aligned note span.
- reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015.json`

### Note `e0016` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0016`
- target note:
```text
所有持有联邦牌照的储贷机构和绝大部分持有州政府牌照的储贷机构都是“互助”机构。此类机构由储户所有，不以追求股东利益为目的
```
- target source span(s):
  - `p361@92-152`: 所有持有联邦牌照的储贷机构和绝大部分持有州政府牌照的储贷机构都是“互助”机构。此类机构由储户所有，不以追求股东利益为目的
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0016.json`

### Note `e0017` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0017`
- target note:
```text
“变化总在发生，你不去迎接进步的变化，就会等到退步的变化”。
```
- target source span(s):
  - `p478@57-87`: “变化总在发生，你不去迎接进步的变化，就会等到退步的变化”。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0017.json`

### Note `e0018` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0018`
- target note:
```text
。重压之下，它们很容易铤而走险，追求不切实际的高收益投资。最终的结局，必然是整个行业分崩离析。
```
- target source span(s):
  - `p524@96-143`: 。重压之下，它们很容易铤而走险，追求不切实际的高收益投资。最终的结局，必然是整个行业分崩离析。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0018.json`

### Note `e0019` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0019`
- target note:
```text
我觉得，他是想让我们知道：如果比你聪明很多的人要骗你，你再怎么判断和分析，也很难不受骗。
```
- target source span(s):
  - `p561@33-77`: 我觉得，他是想让我们知道：如果比你聪明很多的人要骗你，你再怎么判断和分析，也很难不受骗。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0019.json`

### Note `e0020` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0020`
- target note:
```text
另外，我们很清楚自己的不足，很清楚有很多事我们做不到，所以我们谨小慎微地留在我们的“能力圈”之中。“能力圈”是沃伦提出的概念。沃伦和我都认为，我们的“能力圈”是一个非常小的圆圈。
```
- target source span(s):
  - `p564@33-122`: 另外，我们很清楚自己的不足，很清楚有很多事我们做不到，所以我们谨小慎微地留在我们的“能力圈”之中。“能力圈”是沃伦提出的概念。沃伦和我都认为，我们的“能力圈”是一个非常小的圆圈。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0020.json`

### Note `e0021` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0021`
- target note:
```text
本·富兰克林说过：“结婚之前，擦亮双眼。结婚之后，睁一只眼闭一只眼。”商学院就是这么做的。它们已经嫁给了大公司，有些事情，只能睁一只眼闭一只眼。
```
- target source span(s):
  - `p578@0-72`: 本·富兰克林说过：“结婚之前，擦亮双眼。结婚之后，睁一只眼闭一只眼。”商学院就是这么做的。它们已经嫁给了大公司，有些事情，只能睁一只眼闭一只眼。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0021.json`

### Note `e0022` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0022`
- target note:
```text
本·格雷厄姆讲过，高等级公司债往往不值得投资。高等级公司债的收益率只比国债收益率略高一些，向上的潜力丝毫没有，向下的风险却特别大。
```
- target source span(s):
  - `p581@0-65`: 本·格雷厄姆讲过，高等级公司债往往不值得投资。高等级公司债的收益率只比国债收益率略高一些，向上的潜力丝毫没有，向下的风险却特别大。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0022.json`

### Note `e0023` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0023`
- note comment: 尽力而为了
- target note:
```text
无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。
```
- target source span(s):
  - `p595@0-87`: 无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0023.json`

### Note `e0024` — `miss`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0024`
- target note:
```text
无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。
```
- target source span(s):
  - `p595@0-87`: 无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。
- matched reaction in timeline: `(none)`
- judge/runner reason: no_candidate_source_span_overlap
- reviewer interpretation: No recall credit: either no strict source-overlap candidate existed or the admitted candidate did not satisfy the judge.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0024.json`

### Note `e0025` — `focused_hit`

- note_case_id: `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0025`
- target note:
```text
我们始终牢记凯恩斯(Keynes)勋爵的箴言，这也是沃伦经常引用的一句话：“宁要模糊的正确，也不要精确的错误。”对于至关重要的信息，没有准确数字，我们会尽力估算，绝对不会只靠准确的部分信息做决定。
```
- target source span(s):
  - `p607@36-134`: 我们始终牢记凯恩斯（Keynes）勋爵的箴言，这也是沃伦经常引用的一句话：“宁要模糊的正确，也不要精确的错误。”对于至关重要的信息，没有准确数字，我们会尽力估算，绝对不会只靠准确的部分信息做决定。
- matched reaction in timeline: `rx:Full_Content:src:c1:p606@0-p608@211:highlight:249`
- source-span relation: `note_contains_candidate`; coverage `0.4286`
- judge/runner reason: The reaction's quoted source span covers the core operational principle from the note (estimation when numbers are missing, not bypassing crucial information). The reaction correctly identifies the key insight as '芒格式的诚实' (Munger's honesty) and captures the essential message: the transition from the motto '模糊的正确' to concrete operational stance. The overlap, while not including the famous Keynes quote itself, contains the most practically important content of the note.
- reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
- raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0025.json`

## Reading Timeline: All Visible Reactions

Every visible reaction in this Eval-1 window is listed in reading order. Fields are conditional: callback/FVI details appear only when the audit found a callback claim; Selective Legibility details appear only when the reaction overlapped a dataset note target.

### Reaction 001 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p5@0-p5@105:highlight:1`
- source span: `src:c1:p5@45-p5@104`
- source span excerpt:
```text
合并净运营收益（不计投资收益）为1193.4万美元，每股1.68美元；合并净收益为1652.4万美元，每股2.32美元
```
- visible reaction:
```text
这里明确区分了两种收益口径——净运营收益（排除投资收益）和合并净收益（含全部收益）。两者之差约459万美元来自投资或非运营业务。这个"不计投资收益"的明确标注，是芒格财务语言中常见的精确区分，提醒读者不要把运营利润和投资收益混为一谈。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 002 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p6@0-p10@64:highlight:2`
- source span: `src:c1:p9@17-p9@82`
- source span excerpt:
```text
芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。
```
- visible reaction:
```text
"实在没有预测未来的能力"——这句话和"黑色星期一"的后见之明之间形成了有趣的落差：芒格承认无法预测，但又确实感到了不安。这不是先知的姿态，而是一种诚实的、对风险的直觉性警觉。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 003 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p13@0-p17@79:highlight:3`
- source span: `src:c1:p16@11-p16@81`
- source span excerpt:
```text
储蓄银行发放贷款的利率上限为8%，因此，储蓄银行持有的都是利率为8%的长期抵押贷款。后来，随着利率上升到15%、20%，储蓄银行陷入了困境。
```
- visible reaction:
```text
监管创造的利率锁定期望值，和市场利率的真实走向之间存在不可调和的结构性断裂。一旦这种断裂被打破，储蓄银行的整个资产端逻辑就失效了——这是被动持有劣质资产的根源，也是整个叙述的一个隐性前提。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 004 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p13@0-p17@79:highlight:4`
- source span: `src:c1:p17@0-p17@79`
- source span excerpt:
```text
为了摆脱困境，储蓄银行开始相信风险越高、收益越高的理论。它们听信证券行业和房地产行业掮客的花言巧语，买入了大量充满风险的资产，结果它们越陷越深，甚至濒临破产。
```
- visible reaction:
```text
"越陷越深"这个表述不是偶然的——它精确地描述了当错误认知遭遇现实惩罚时，系统性行为如何从失调走向崩溃。掮客的"花言巧语"恰好利用了绝望，而不是创造了贪婪。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 005 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p18@0-p19@88:discern:5`
- source span: `src:c1:p19@45-p19@63`
- source span excerpt:
```text
这笔投资还是不错的，将来应该可以的。
```
- visible reaction:
```text
"应该"这个词在这里出现了两次，语气是自我确认式的，但并非言之凿凿。这和芒格在前面说"实在没有预测未来的能力"形成了一个有趣的对照——在储蓄银行的具体投资上，叙述者反而用"应该"来建立信心。这不是矛盾，而是层次区分：对宏观市场无法预测，对具体纾困标的的退出路径（整体出售）则有一定的把握。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前文'实在没有预测未来的能力'形成对照，但未提供具体文本位置或引用，依赖印象式关联而非锚定型引证。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 006 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p20@0-p20@147:highlight:6`
- source span: `src:c1:p20@87-p20@111`
- source span excerpt:
```text
除非是受虐狂，这么枯燥烦琐的东西，谁能读得下去？
```
- visible reaction:
```text
「受虐狂」这个类比用得很随意，但透露了叙述者对复杂合同的态度：复杂性不是用来被理解的，是用来被承认然后绕过的。它和前面那种对储蓄银行困境的细致分析形成了某种张力——那里有认知，这里只有委托。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 007 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p21@0-p21@140:highlight:7`
- source span: `src:c1:p21@89-p21@127`
- source span excerpt:
```text
迪克是个坚守原则的投资者。他痛恨人类的愚蠢，痛恨不良资产。他有恒心、有韧劲。
```
- visible reaction:
```text
通过否定性描述来勾勒人物——不是说他追求什么，而是说他反对什么。这种"痛恨X、痛恨Y"的句式本身就有一种鲜明的立场感，比正面罗列美德更有个性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 008 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p22@0-p23@74:highlight:8`
- source span: `src:c1:p23@0-p23@74`
- source span excerpt:
```text
好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。各位可以放心，有我们给大家守着呢。
```
- visible reaction:
```text
"好在我们还有"这句话的结构本身就很有意思——它用"好在我们还有"来回应"迪克去世"，而不是用"我们感到悲痛"来回应。悲伤被迅速转化为"替代方案已就位"的安心陈述。两个句子的接口不是情感，而是结构性的续接。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 009 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p24@0-p26@188:highlight:9`
- source span: `src:c1:p24@0-p24@76`
- source span excerpt:
```text
从表面上看，包厘街储蓄银行与储贷机构非常类似。实际上，它不是储贷机构，而是一家银行。包厘街储蓄银行不是储蓄和贷款机构体系中的一员，而是银行体系中的一员。
```
- visible reaction:
```text
这段澄清用了双重否定来建构身份：不是A，而是B；不是X体系的一员，而是Y体系的一员。这种句式不是为了强调相似性，反而是为了划清边界——越像，越需要说清楚不是什么。叙述者的立场很鲜明：分类错误比分类模糊更不可接受。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 010 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p24@0-p26@188:highlight:10`
- source span: `src:c1:p26@56-p26@188`
- source span excerpt:
```text
现在，保险生意进入了周期的新阶段，这个阶段不是该投资的时候。从本质上说，保险生意销售的只是普通商品。和所有销售普通商品的公司相比，保险公司的定价特点没什么两样。处于景气周期时，各家保险公司竞相增发股票，扩充资金规模，不遗余力地争抢业务。保险生意现在就处于景气周期。
```
- visible reaction:
```text
这里用"普通商品"这个定性来解释为什么景气周期反而危险：保险没有定价护城河，大家只能在规模上竞争，繁荣本身制造了风险敞口。"不是该投资的时候"这句话干脆利落，和芒格之前对市场整体的谨慎完全一致——不是在预测危机，而是在周期位置上做出方向性判断。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 011 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p27@0-p27@98:highlight:11`
- source span: `src:c1:p27@84-p27@98`
- source span excerpt:
```text
保费太低，我们就往后退一步。
```
- visible reaction:
```text
这句几乎可以作为伯克希尔保险业务的行动准则。在一个保费下跌50%的市场里，选择收缩而非扛规模，是知行合一的味道——"景气周期不投资"不只是一句判断，而是真实发生的选择。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 012 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p28@0-p32@53:highlight:12`
- source span: `src:c1:p30@0-p30@71`
- source span excerpt:
```text
一天，银行的客户经理请他吃饭，席间对他说：“您整天酗酒、寻欢作乐，我们很担心。”这人听了，回答道：“你放心吧，我喝酒，但我的市政债券不喝酒。”
```
- visible reaction:
```text
这个回答的妙处在于：行为主体可能失序，但工具性资产保持中立。一个字都没提风险管理，却完美示范了资产隔离的逻辑——人在喝酒，债券不喝，两者不相关。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 013 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p28@0-p32@53:highlight:13`
- source span: `src:c1:p31@20-p31@75`
- source span excerpt:
```text
即使保险业务停了，资产还在我们手里，资产的盈利能力还在我们手里。有这些资产，有这个盈利能力，我们可以游刃有余。
```
- visible reaction:
```text
这里用"停"而非"亏"来描述风险，语气就不一样了。不是在说会发生损失，而是说即使业务中断，资产本身还在发挥功能。这是用资产质量说话，而不是用承诺或预测说话。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 014 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p33@0-p33@62:highlight:14`
- source span: `src:c1:p33@12-p33@24`
- source span excerpt:
```text
这是现在，不意味着永远。
```
- visible reaction:
```text
这句话把静态的资产持有状态，转成了一个有时间刻度的阶段性选择。不是"我们被套住了"，而是"我们选择等，但等不等于永远等"。语气里有耐心，也有清醒。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 015 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p33@0-p33@62:highlight:15`
- source span: `src:c1:p33@24-p33@62`
- source span excerpt:
```text
真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。
```
- visible reaction:
```text
用极端假设来证明资产的流动性——即使到最被迫的境地，钱也不是死钱。这和"找不到好机会，没地方配置"形成呼应：现在不动，是因为没有值得动的好机会，不是因为动不了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 016 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p38@97:highlight:16`
- source span: `src:c1:p37@0-p37@31`
- source span excerpt:
```text
真有我们看好的公司，我们会尽全力追求，但现在没一个我们看好的。
```
- visible reaction:
```text
这里"现在没一个"和前文那句"这是现在，不意味着永远"形成呼应——不是手里没钱，而是没有值得出手的好标的。持有资本等待是主动姿态，不是被动困局。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确声称与前文'这是现在，不意味着永远'形成呼应，两个文本位置相近，关联具体且可查。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 017 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p34@0-p38@97:highlight:17`
- source span: `src:c1:p38@0-p38@97`
- source span excerpt:
```text
有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。
```
- visible reaction:
```text
最后这句"一年也只能做成一笔"是全文最实诚的一句话。不是能力问题，是纪律问题——机会再多，也不滥投。把"耐心"从美德降格为操作原则：不是不想做更多，而是本来就应该只做一笔好的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 018 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:18`
- source span: `src:c1:p40@40-p40@68`
- source span excerpt:
```text
真正做收购是好事多磨，要熬过辛苦的等待，经历反复的波折。
```
- visible reaction:
```text
这句话把收购的难度从偶然性提升为规律性——"好事多磨"不是概率问题，而是本质特征。任何试图绕开这一规律的做法，"很难有好结果"。前文那句"一年也只能做成一笔"在这里获得了逻辑支撑：不是慢，是本来就应该慢。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["concept:annual_one_deal_discipline"]}`
  - judge reason: prior_link指向'concept:annual_one_deal_discipline'，将'好事多磨'与'一年只能做成一笔'做了明确的逻辑关联，具体可查。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 019 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p39@0-p41@181:retrospect:19`
- source span: `src:c1:p41@142-p41@181`
- source span excerpt:
```text
现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。
```
- visible reaction:
```text
这里的"守势"值得关注：不是手里没钱，而是两条主动路都暂时关闭后的主动选择。结合前文"攥在手里，这是现在，不意味着永远"的立场，守势是等待机会的姿态，和被迫收缩是两回事。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:wesco_asset_deployability"]}`
  - judge reason: prior_link指向'active_attention:wesco_asset_deployability'，将守势姿态锚定到前文关于资产可部署性的讨论上，关联具体。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 020 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p42@0-p43@107:highlight:20`
- source span: `src:c1:p43@69-p43@107`
- source span excerpt:
```text
优秀的管理层是资产中的一部分，沃伦并不因为管理层优秀，而支付高出价值的价格。
```
- visible reaction:
```text
这里有个隐含前提：管理层的价值已经体现在"资产价值"里了。如果买入价低于资产价值，管理层那部分已经白送；再为"管理层优秀"加钱，就成了重复支付。这个逻辑把对管理层的偏好和定价纪律彻底解耦——可以看好，但不用为此多付。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 021 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p44@0-p45@88:highlight:21`
- source span: `src:c1:p45@0-p45@54`
- source span excerpt:
```text
有哪个经理人是如此优秀，能让我们愿意以高于资产价值的价格买入一家公司吗？即使是在全美国范围内，也一个都没有。
```
- visible reaction:
```text
这个"全美国范围内"的绝对化有很强的经验背书感——不是在理论上否定，而是在实践层面声称没有先例。把抽象的定价纪律落实为具体的经验边界。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 022 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p44@0-p45@88:highlight:22`
- source span: `src:c1:p45@54-p45@88`
- source span excerpt:
```text
也许有人愿意为管理层支付溢价，而且还做得很成功，但那不是我们的风格。
```
- visible reaction:
```text
这句收尾很干净："也许有人做得很成功"承认了别的路可行，但"不是我们的风格"明确划清界限而不做价值判断。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 023 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p46@0-p46@106:retrospect:23`
- source span: `src:c1:p46@58-p46@106`
- source span excerpt:
```text
巴菲特原来是一块钱的东西，五角钱买。现在，他愿意出更高的价格，一块钱的东西，大概是八角五分钱买。
```
- visible reaction:
```text
这个"更高的价格"其实还是在价值以内的折扣。巴菲特的底线没破——只是从五角放宽到八角五，还是便宜，只是没那么极端便宜。这和前面"不支付高于价值的价格"并不矛盾，因为八角五分仍低于一块钱的价值。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p42@0-p43@107:highlight:20", "reaction:rx:Full_Content:src:c1:p44@0-p45@88:highlight:21"]}`
  - judge reason: prior_link明确指向reaction 20和reaction 21，将'更高的价格'锚定到前文的定价纪律讨论，关联具体。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 024 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p47@0-p50@81:highlight:24`
- source span: `src:c1:p49@18-p49@74`
- source span excerpt:
```text
你把他从火车上扔下去，扔到一个偏僻的小镇，不给他钱，他在这个小镇上诚实本分地经营，用不了多长时间，又发家致富了。
```
- visible reaction:
```text
这个场景测试的厉害之处在于：它把"优秀"从静态的资质描述变成了动态的能力验证——不是看他有什么学历、懂什么理论，而是看他被剥夺一切之后能做什么。能凭空发家致富的人，学历和理论都是多余的了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 025 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p47@0-p50@81:highlight:25`
- source span: `src:c1:p50@38-p50@81`
- source span excerpt:
```text
如果这种聘请人才的思路行得通，所有美国公司都蒸蒸日上了，哪至于像现在这样存在诸多弊病。
```
- visible reaction:
```text
这是一个反事实论证——不是从理论层面反驳，而是用结果反过来否定前提。用全美国公司层面的普遍失败来为这个具体的招聘哲学背书，力量感很强。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 026 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p51@0-p55@64:highlight:26`
- source span: `src:c1:p54@0-p54@61`
- source span excerpt:
```text
许多储贷机构在发放贷款时，都尽可能让客户开始的时候多交钱。把年度业绩做得漂亮，管理层能得到大笔的期权。我们的文化截然相反。
```
- visible reaction:
```text
这段把行业惯用做法和西科的文化直接对撞：别人靠前期收费美化年报拿期权，西科则反其道而行——前期收入少，但最终利润合理且无坏账风险。"截然相反"四个字掷地有声，把整个行业的问题点了出来。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 027 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p51@0-p55@64:highlight:27`
- source span: `src:c1:p55@24-p55@64`
- source span excerpt:
```text
别的储贷机构都积极地向开发商提供贷款，既然别人那么踊跃，我们就不去凑那个热闹了。
```
- visible reaction:
```text
又一个"不凑热闹"的时刻——和前面投资的守势逻辑一脉相承。在开发商贷款业务上别人越踊跃，西科就越主动退出，说明他们不是在所有业务上都守势，而是在高风险的拥挤赛道上保持距离。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前文投资的守势逻辑一脉相承，但未提供具体锚定文本，属于印象式关联而非锚定型引用。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 028 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p61@0-p62@104:discern:28`
- source span: `src:c1:p61@0-p61@24`
- source span excerpt:
```text
我们根本没有预知未来的能力，即使出手也是如履薄冰
```
- visible reaction:
```text
这句话是整个段落的基调锚点。把"没有预知未来的能力"放在"如履薄冰"之前，等于把不确定性设定为行动的前提条件，而不是行动的障碍——意味着你不是因为谨慎才不动，而是因为认清了现实的不可预测，才坦然接受"动也是如履薄冰"。和前面"我们出手的时候很少"的自律逻辑是一脉相承的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前面'我们出手的时候很少'的自律逻辑一脉相承，但未提供具体文本锚定，关联依赖推断而非引用。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 029 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p61@0-p62@104:highlight:29`
- source span: `src:c1:p62@79-p62@104`
- source span excerpt:
```text
以前的投资机会让我们感到踏实，现在我们觉得不踏实。
```
- visible reaction:
```text
这是一个清晰的时间节点对比。"以前"和"现在"的区别不是性格变了，而是环境变了。用主观感受的变化来映射客观机会质量的变化，比直接说"现在机会少"更有温度。这种"不踏实"的感知，和前面反复出现的"感到不安"形成了一个贯穿性的情绪主题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前文反复出现的'感到不安'形成贯穿性情绪主题，但未锚定具体文本位置，关联模糊。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 030 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p63@0-p66@76:highlight:30`
- source span: `src:c1:p65@85-p65@177`
- source span excerpt:
```text
有一幅梵高的作品，拍出了天价，被有史以来最蠢的一个买家买走了。这幅画作从100美元涨到3900万美元。尽管拍出了天价，可经过了从1888年到现在这么长的时间，计算下来，复利只有13%。
```
- visible reaction:
```text
这个"最蠢买家"的玩笑背后藏着一个清醒的计算：3900万听起来疯狂，但跨越将近一个世纪，年化复利只有13%。它用一种戏剧化的方式把"时间对复利的腐蚀"说得比任何公式都清楚。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 031 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p63@0-p66@76:highlight:31`
- source span: `src:c1:p64@33-p64@73`
- source span excerpt:
```text
到底是他们聪明呢，还是走运呢？反正只拿我们过去三年的业绩和他们的比，是他们聪明。
```
- visible reaction:
```text
"只拿过去三年和他们的比"——这个限定条件很诚实。短期业绩比较根本无法区分运气和skill，但作者选择坦承这一点，而不是装作能分辨清楚。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 032 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p71@0-p75@26:retrospect:32`
- source span: `src:c1:p73@56-p73@100`
- source span excerpt:
```text
参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。
```
- visible reaction:
```text
这个类比比之前的数字玩笑更进一步：它不是说"这宗收购的回报率和那幅画一样"，而是说"这些基金经理的行为模式和那个日本人一样"——钱不是自己的，所以不在意价格。激励机制变了，行为就跟着疯了。前文讲梵高那幅画是拿13%的年化复利说"长期来看收益没那么惊人"，这里把那个类比转成了"买家行为模式"的解释工具。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p63@0-p66@76:highlight:30"], "note": "前文用梵高画作说复利的时间代价，这里转用其描述行为模式"}`
  - judge reason: prior_link明确指向reaction 30，将梵高画作类比从复利逻辑转用为行为模式解释，关联具体且有note说明转换路径。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 033 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p71@0-p75@26:highlight:33`
- source span: `src:c1:p75@0-p75@26`
- source span excerpt:
```text
汤姆·墨菲的故事告诉我们，只有经过失败，才能懂得谦卑
```
- visible reaction:
```text
把"找不到好机会"这件事装进了一个更大的谦卑叙事里。这不是"市场现在不好"的短期判断，而是一个贯穿性的原则：成功让人自大，失败让人清醒。整个1986年的叙事——找不到收购对象、股市没机会、只能守势——现在都归到这个落点上。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称将1986年的整个叙事归到谦卑叙事这一落点，但未提供具体锚定文本，关联依赖整体印象。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 034 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p76@0-p76@140:highlight:34`
- source span: `src:c1:p76@0-p76@41`
- source span excerpt:
```text
我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。
```
- visible reaction:
```text
"非常欣赏"和"算不上"连在一起，这种承认很彻底——不是谦逊式的自我贬低，而是诚实地把自己的局限摆出来。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 035 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p76@0-p76@140:highlight:35`
- source span: `src:c1:p76@106-p76@140`
- source span excerpt:
```text
她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。
```
- visible reaction:
```text
在这里"但是"不是转折，而是并列：能力强和不谦卑同时成立。芒格在用身边的具体人物建立一个观察——厉害的人可以同时不谦卑，不谦卑不等于失败。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 036 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p77@0-p81@23:highlight:36`
- source span: `src:c1:p80@27-p80@64`
- source span excerpt:
```text
上帝回应了我的祷告。我祈求懂得谦卑，上帝让我去威尔克斯—巴里市学会了谦卑。
```
- visible reaction:
```text
这里"让"字很关键——不是"上帝允许我失败"，而是"上帝派我去学"。失败是神意设计的一门课，不是偶然的运气差。墨菲把整个灾难叙事重新框定为神圣的教学安排，亏损几百万反而成了"谦卑课"的学费。这比"失败使人谦卑"的普通说法要强有力得多。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 037 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p77@0-p81@23:discern:37`
- source span: `src:c1:p81@0-p81@23`
- source span excerpt:
```text
有时候，只有经过失败的历练，我们才能懂得谦卑。
```
- visible reaction:
```text
前面已经用墨菲的故事铺陈了，这里是一句直接的结论性陈述。但它加了一个"只有"——意味着没有失败这个历练，谦卑是学不到的，前面的成功再多也学不会。这和前文"没有一个人说我谦卑"形成呼应：芒格自己身边这些强人都没学会谦卑，因为他们还没有经足够失败的历练。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002` / note `mangge_zhi_dao_private_zh_personal_notes__e0002` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p81@0-23` 有时候，只有经过失败的历练，我们才能懂得谦卑。
    - target note: 有时候，只有经过失败的历练，我们才能懂得谦卑。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0002.json`
- Callback/FVI audit: `weak_callback`
  - judge reason: 声称与前文'没有一个人说我谦卑'形成呼应，但未提供具体锚定文本，关联模糊。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 038 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p83@0-p83@127:discern:38`
- source span: `src:c1:p83@108-p83@127`
- source span excerpt:
```text
谁能想到这么笨的一个人，竟然那么富有？
```
- visible reaction:
```text
这个"笨"字被精心设计过——前面的铺垫让"笨"字指向的是"需要讲很多遍才懂"，而不是"不耐心"或"乱花钱"。所以最后反转的力量不是来自意外，而是来自重新定义：芒格在说，你以为的聪明（反应快、理解力强）根本不是真正的优势；你以为的笨（慢、重复）反而是真正的壁垒。"富有"是对这套逻辑的最终盖章。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 039 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p93@0-p96@48:retrospect:39`
- source span: `src:c1:p94@78-p94@146`
- source span excerpt:
```text
但是他们在1987年10月——就在股灾前夕，买入了所罗门兄弟公司的可转换优先股，与整个市场一起遭遇暴跌。这也成为股东会上的一个关注焦点。
```
- visible reaction:
```text
这个细节值得注意：西科和巴菲特从3月就开始抛售，说明他们已经嗅到了危险。但10月又买所罗门的优先股，说明他们认为这笔投资值得冒险，即便市场已经摇摇欲坠。"关注焦点"说明股东要追问：你们预见到了风险，为什么又在这里下注？这是一个需要在股东会上解释的决策。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["thread:munger_market_timing_record"]}`
  - judge reason: prior_link指向'thread:munger_market_timing_record'，将3月抛售与10月买所罗门的行为锚定到市场择时记录这一贯穿线索。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 040 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p93@0-p96@48:retrospect:40`
- source span: `src:c1:p96@0-p96@48`
- source span excerpt:
```text
目前的西科，持有大量流动资产，但找不到什么好的投资机会。如果你能找到好的投资机会，那你比我们强。
```
- visible reaction:
```text
这句话是芒格的典型风格——把自己的困境直接说出来，反而显得诚实。它和前文"手握大量资产"的立场一致，但加了一层自嘲式的退让：不是我们不想投资，是真的找不到值得投的机会。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:wesco_asset_solidity", "active_attention:wesco_asset_deployability"]}`
  - judge reason: prior_link明确指向'active_attention:wesco_asset_solidity'和'active_attention:wesco_asset_deployability'，将'手握大量资产'锚定到前文两次出现的资产质量讨论。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 041 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:41`
- source span: `src:c1:p101@6-p101@62`
- source span excerpt:
```text
所有人都有这个倾向。所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
```
- visible reaction:
```text
这个"所有人"把前面的所有铺垫（销售员、顾问、律师）都收进去了。芒格不是在骂某个职业，他是在指出一件每个人都干的事。没有控诉感，只有冷静的描述，这是最难以反驳的批评方式。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007` / note `mangge_zhi_dao_private_zh_personal_notes__e0007` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p101@16-62` 所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
    - target note: 所有人的潜意识里都有这样的偏见：给别人提建议时，以为是在为别人考虑，其实是从自己的利益出发。
    - source-span relation: `candidate_contains_note`; coverage `1.00`
    - judge/runner reason: The reaction directly engages with the note's core idea about '所有人' (everyone) having this subconscious bias. It analyzes why Munger's use of '所有人' is rhetorically powerful—encompassing all previously mentioned professions (salespeople, consultants, lawyers) without accusation. The reaction is specifically focused on the note's main insight rather than tangential content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0007.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 042 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p97@0-p101@62:highlight:42`
- source span: `src:c1:p100@6-p100@21`
- source span excerpt:
```text
查理，我这鱼钩又不是卖给鱼的。
```
- visible reaction:
```text
这句话的力度来自它直接的逻辑：买家才是目标，鱼不是。整个段落的讽刺力量都在这句短回应里——不需要解释，笑完就懂了。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006` / note `mangge_zhi_dao_private_zh_personal_notes__e0006` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p99@0-81` 多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？”; `p100@0-22` 他回答道：“查理，我这鱼钩又不是卖给鱼的。”
    - target note: 多年以前，我在帕萨迪纳市有个朋友，是做渔具生意的。他出售的鱼钩五颜六色的。我以前从没见过色彩这么丰富的鱼钩。我问他：“你这鱼钩五颜六色的，鱼是不是更容易上钩啊？”他回答道：“查理，我这鱼钩又不是卖给鱼的。”
    - source-span relation: `note_contains_candidate`; coverage `0.15`
    - judge/runner reason: The reaction's quoted span precisely captures the punchline ('查理，我这鱼钩又不是卖给鱼的。'), which is the core insight of the entire note. The reaction's analysis focuses directly on this specific quote, explaining its satirical logic about targeting buyers rather than fish. Although the note includes the story setup, the reaction correctly identifies that the humorous and rhetorical power lies entirely in this short response, and it targets that essence without being distracted by peripheral context.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0006.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 043 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p102@0-p103@20:highlight:43`
- source span: `src:c1:p102@0-p102@30`
- source span excerpt:
```text
自己用不用理发，别问理发师。从自己利益出发的，不仅仅是券商。
```
- visible reaction:
```text
理发师的比喻极其朴素，却精准地把"利益偏见"从专业术语拉回日常经验。后面那句"不仅仅是券商"是个关键——它把这个毛病从职业标签（券商）上升到了人性层面。前文的"所有人"在这里得到了具体演绎。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: '前文的"所有人"在这里得到了具体演绎'——明确回调reaction 41，将理发师比喻定位为'所有人'论述的具体落点。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 044 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p102@0-p103@20:highlight:44`
- source span: `src:c1:p103@0-p103@20`
- source span excerpt:
```text
所罗门兄弟公司的生意怎么能不是好生意呢？
```
- visible reaction:
```text
修辞性反问，语气里带着冷笑。它不是在说所罗门兄弟真的认为自己的生意不好，而是在说：他们当然会说自己的生意好——因为他们从自己的生意里获利。"怎么能不是"暗示的是：如果你是所罗门，你会说不是吗？
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 045 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p104@0-p108@95:highlight:45`
- source span: `src:c1:p107@39-p107@94`
- source span excerpt:
```text
古弗兰对人性持有怀疑态度。所罗门是一家授出信用的公司，古弗兰对人性的怀疑态度，可以帮他做好监控信用风险的工作。
```
- visible reaction:
```text
这里把"怀疑人性"明确定性为一种职业能力——对授信公司来说，不信任交易对手是风险管控的基础，而非人际关系的缺陷。这和前文"理发师不给自己理发"的逻辑一脉相承：利益偏见需要外部机制来对冲，古弗兰的怀疑态度就是这个机制。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: '和前文"理发师不给自己理发"的逻辑一脉相承'——提到前文但未给出具体ref_ids，且'怀疑人性'作为职业能力与'利益偏见'的关联较松散。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 046 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p104@0-p108@95:highlight:46`
- source span: `src:c1:p108@53-p108@95`
- source span excerpt:
```text
1987年10月的股市大跌导致许多券商破产，因为它们向很多不够资格的客户授出了信用。
```
- visible reaction:
```text
这是为前文"信用质量至关重要"提供的历史注脚。它既是对古弗兰信用纪律路线的隐性肯定，也暗示了巴菲特/芒格对1987年股灾早有警觉——当时他们判断市场"没有好机会"、采取守势，并非悲观预测，而是看到了信用过度扩张积累的系统性风险。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提及'前文"信用质量至关重要"'但缺少具体ref_ids；将1987年守势与信用风险挂钩是延伸性解读，支撑较弱。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 047 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p109@0-p113@89:highlight:47`
- source span: `src:c1:p110@88-p110@98`
- source span excerpt:
```text
怎么能说是垃圾债呢？
```
- visible reaction:
```text
这是为那笔所罗门优先股投资正名。语气与前文"所罗门兄弟公司的生意怎么能不是好生意呢"形成对称——但那里是反讽（暗示他们会自利性地说好），这里是正面澄清（说明这债实际上是AA级）。两句话看似相近，实际功能相反。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 提到'前文"所罗门兄弟公司……"形成对称'，但未提供具体ref_ids；两处功能对比的论证依赖读者自行连接。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 048 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p109@0-p113@89:highlight:48`
- source span: `src:c1:p113@60-p113@89`
- source span excerpt:
```text
结果，在很多年份里，我们的估算还是与实际数字有很大的出入。
```
- visible reaction:
```text
这是结尾的自省。"尽可能偏保守地估算"之后，仍然"有很大的出入"——芒格在这里坦承，即使是刻意保守的估计框架，也系统性偏离实际。这不是策略失败的自我批评，而是对预测本质的诚实承认：为不确定性预留缓冲，缓冲本身仍然可能不够。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 049 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p114@0-p116@37:highlight:49`
- source span: `src:c1:p116@14-p116@37`
- source span excerpt:
```text
进行审计的会计和我们没什么两样，也是全靠估算。
```
- visible reaction:
```text
这是本段最锐的一句话。它把外部审计的权威性轻轻拆掉了——审计不是独立于估算的第二层真相，而是和被审计方站在同一个估计地基上。这对保险行业的信用结构而言是一个颇为激进的坦白。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 050 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p117@0-p119@39:highlight:50`
- source span: `src:c1:p119@0-p119@39`
- source span excerpt:
```text
提议是好提议，但储贷行业中充斥着政治博弈，这个提议能否变成现实，还是未知之数。
```
- visible reaction:
```text
这一句把整段的赞成基调轻轻收窄。"好提议"和"未知之数"之间的落差，不是否定政策逻辑，而是对执行链条中政治阻力的诚实承认。这种"方向对但路径不确定"的并置，在芒格讨论制度问题时反复出现。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 051 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p123@0-p127@63:highlight:51`
- source span: `src:c1:p125@73-p125@142`
- source span excerpt:
```text
再不改革，会有更多优秀的储贷机构离开，最后留给联邦储蓄贷款保险公司的只能是质量差、实力弱的储贷机构，到那时，整个储贷行业将面临崩盘的风险。
```
- visible reaction:
```text
这是整个段落最锐的一句话。它把一个逆向选择机制清晰地说出来了：不是FSLIC本身坏了，而是它被好机构抛弃了，留下的都是差的，系统性恶化。这是一种结构性崩塌，不是单点故障。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 052 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p123@0-p127@63:highlight:52`
- source span: `src:c1:p127@0-p127@63`
- source span excerpt:
```text
发展到这一步，都是因为政府当初缺乏预见性，颁布了错误的政策。很多问题都如此，提前预见到了，可以避免，事到临头的时候，悔之晚矣。
```
- visible reaction:
```text
这是一个相当普遍的政治判断，也是芒格反复出现的一个底层思路：预见性是治理能力的核心，政策错误的影响是累积的，等后果显现再补救已太晚。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 053 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p128@0-p131@16:highlight:53`
- source span: `src:c1:p130@0-p130@58`
- source span excerpt:
```text
向一个主权国家发放的贷款，根本没办法强行收回。你让还款，人家说：“你看，我们国家多少穷人还流落街头呢，拿什么还钱？”
```
- visible reaction:
```text
这段对话把主权债务的悖论说得很形象：债务人用"穷人"作为道德盾牌，而债权人除了反问"难道把海军开过去"之外毫无办法。这不是幽默，是结构性无力的真实写照。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 054 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p132@0-p135@41:retrospect:54`
- source span: `src:c1:p135@0-p135@41`
- source span excerpt:
```text
西科没有大量分支机构。很早以前，我们就比同行更早地意识到，多开分支机构无益。[4]
```
- visible reaction:
```text
"很早以前就比同行更早地意识到"这个句式值得注意。芒格在这里用了双重比较级，强调的不是西科做了什么，而是西科比行业早多久看清了这件事。这和他一贯的"预见性"主张完全一致：不是事后补救，而是更早地看见了结构。这和前文"政府当初缺乏预见性"构成一个贯穿性主题——预见能力是区分好机构和坏机构的核心品质，不只在金融业，在政策层面也是如此。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p123@0-p127@63:highlight:52"], "note": "前文说\"政府当初缺乏预见性\"。这里\"很早以前就比同行更早地意识到\"是同一个框架在机构层面的正面版本——预见性是好机构的核心竞争力。这两个节点加在一起，构成芒格对\"预见性\"的多层次论证。"}`
  - judge reason: 明确以reaction 52为锚——'政府当初缺乏预见性'为负面版本，西科'比同行更早意识到'为正面版本，构成'预见性'的多层次论证。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 055 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p136@0-p140@32:highlight:55`
- source span: `src:c1:p139@36-p139@54`
- source span excerpt:
```text
从表面上看，我们的利差低于平均水平。
```
- visible reaction:
```text
这个"表面"用得很有意思。芒格紧接着解释原因：西科把所有不良贷款都算进去，而其他机构未必这么严格。所以"低于平均"不是表现差，而是算法更诚实。这是一个关于披露质量的暗示——表面的数字低，可能恰恰是因为你看得更全。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 056 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p136@0-p140@32:highlight:56`
- source span: `src:c1:p140@0-p140@32`
- source span excerpt:
```text
对于利率风险，我们考虑得很细致、很全面，我们有能力抵御利率风险。
```
- visible reaction:
```text
这是本单元唯一一句不带任何限定语和比较级的直接断言。前面全是"估计""从表面上看""比过去高了很多"这样的软性表述，最后突然变成"我们有能力"——语气切换本身就在传递信息。配合前文对1987年市场环境的隐隐不安，这是一种主动的掌控感表达。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 057 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p141@0-p143@41:highlight:57`
- source span: `src:c1:p141@20-p141@35`
- source span excerpt:
```text
这种贷款方式似乎没什么吸引力。
```
- visible reaction:
```text
芒格直接承认产品不吸引人，和前文"从表面上看利差低于平均水平"是同一种诚实披露策略。承认"看起来不好"，再解释为什么"实际不差"——这已经成为西科沟通风格的一部分。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: '和前文"从表面上看利差低于平均水平"是同一种诚实披露策略'——明确回调reaction 55，建立一致的披露风格。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 058 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p141@0-p143@41:highlight:58`
- source span: `src:c1:p142@18-p142@75`
- source span excerpt:
```text
我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。
```
- visible reaction:
```text
这是对客户品质的描述，更是产品设计逻辑的镜像反射：产品不花哨，所以花哨的客户不会来；来的人看重简单清晰——这本身就是在说风控前置，筛选机制已经嵌入产品本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 059 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p144@0-p147@28:highlight:59`
- source span: `src:c1:p145@0-p145@27`
- source span excerpt:
```text
我们有一片因无法收回贷款而没收的土地，目前正在开发中。
```
- visible reaction:
```text
"没收的"——这个词在这里不带任何负面情绪，只是陈述一个事实：银行收回了抵押的土地，西科在用它开发。这和前文"手握大量资产"的立场一致：被动得来的资产也在被主动经营。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: '和前文"手握大量资产"的立场一致'——明确回调reaction 39关于资产的论述。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 060 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p144@0-p147@28:highlight:60`
- source span: `src:c1:p146@63-p146@95`
- source span excerpt:
```text
隐花狼尾草是非常难根除的一种草，我们想尽了各种办法，都难以除尽。
```
- visible reaction:
```text
前面是利率风险、收购市场、竞争格局，这里突然变成了一种草的烦恼。芒格在描述具体经营管理中真实遇到的小麻烦——这种并置本身就是一种风格：大事小事都是事，都值得直接说。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 061 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p148@0-p149@60:highlight:61`
- source span: `src:c1:p149@34-p149@60`
- source span excerpt:
```text
就因为草的品种，当局让我们废了好多口舌、花了很多钱。
```
- visible reaction:
```text
"就因为"——这三个字轻描淡写地把当局的审美要求落地成了实际的成本摩擦。没有抱怨的语气，但代价已经说清楚了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 062 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p155@0-p158@61:highlight:62`
- source span: `src:c1:p156@47-p156@57`
- source span excerpt:
```text
标准有，但公式没有。
```
- visible reaction:
```text
这句话有一种反教条的明确性。强调有标准不等于有公式——承认投资决策的复杂性，但不为复杂性找借口。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 063 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p155@0-p158@61:highlight:63`
- source span: `src:c1:p157@50-p157@89`
- source span excerpt:
```text
一家赚钱的杂志，一年创造了100万美元的利润，但创造的现金可能是120万美元。
```
- visible reaction:
```text
这个具体例子让"现金高于净利润"这个抽象标准变得可触摸。杂志公司的轻资产属性使其天然具备这种优势——这和西科金融"手握大量资产却找不到好机会"形成了对比：不是所有资产都能转化为这种理想状态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: '联系前文'但未给出具体ref_ids；杂志公司轻资产与西科困境的对比是延伸性类比，支撑较弱。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 064 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p159@0-p159@15:retrospect:64`
- source span: `src:c1:p159@0-p159@15`
- source span excerpt:
```text
西科的收益率不可能超过伯克希尔
```
- visible reaction:
```text
这句话给收益率画了一条硬边界。不是谦虚，是事实陈述。联系前文西科"找不到好机会"的处境，这个天花板是结构性限制，不是能力问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:wesco_defensive_posture", "active_attention:wesco_asset_deployability"]}`
  - judge reason: 以active_attention标签明确回调'wesco_defensive_posture'和'wesco_asset_deployability'，指出收益率上限是结构性限制而非能力问题，与前文西科守势逻辑一致。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 065 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p160@0-p160@109:highlight:65`
- source span: `src:c1:p160@93-p160@109`
- source span excerpt:
```text
我明确地告诉各位，这种想法不对。
```
- visible reaction:
```text
"明确地告诉各位"——不是温和纠正，是直接定性。配合"不对"而非"不一定"或"可能有问题"，措辞的硬度表明这不是一个需要讨论的前提，而是一个已被确认的错误。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 066 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p160@0-p160@109:highlight:66`
- source span: `src:c1:p160@10-p160@93`
- source span excerpt:
```text
控股西科的巴菲特和芒格用了二三十年时间把伯克希尔发展壮大了，现在伯克希尔的规模已经大了，但西科还小呢，西科的复合收益率将远远超过伯克希尔，因此西科具有极高的投资价值。
```
- visible reaction:
```text
这个推理链条值得解剖：规模小→复制路径→复合收益率更高→投资价值极高。伯克希尔的成功被简单理解为"从小到大"的规模扩张，忽略了时间、环境、能力边界等多重约束条件。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 067 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p161@0-p165@27:highlight:67`
- source span: `src:c1:p162@23-p162@47`
- source span excerpt:
```text
我是有可能找到适合西科的好机会，但我可不敢肯定。
```
- visible reaction:
```text
"有可能"和"不敢肯定"之间的张力，是芒格式的诚实：承认存在路径，但拒绝高估自己把握路径的概率。这不是谦虚，是精确的自我评估。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 068 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p161@0-p165@27:highlight:68`
- source span: `src:c1:p165@0-p165@27`
- source span excerpt:
```text
我们尽量把财报做得简单干净，这样我们自己看起来也清楚。
```
- visible reaction:
```text
"我们自己看起来也清楚"——干净财报的首要受益人是管理层自己。这个顺序透露了真实的财务报告哲学：不是为了取悦外部，而是为了管好自己的认知。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 069 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p166@0-p169@106:highlight:69`
- source span: `src:c1:p168@32-p168@80`
- source span excerpt:
```text
问题在于，很多历史记录看不清楚。99%的管理层都把水搅得很浑，让你看不清留存收益的投资效率如何。
```
- visible reaction:
```text
"99%的管理层都把水搅得很浑"——这是一个重量级的经验性断言，不是笼统的批评，而是直接指出这个领域的系统性信息不透明。留存收益分析的最大障碍不是分析方法本身，而是管理层普遍性的信息披露不配合。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 070 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p170@0-p172@68:highlight:70`
- source span: `src:c1:p171@21-p171@38`
- source span excerpt:
```text
有什么问题，来问我，我让你更困惑。
```
- visible reaction:
```text
一个哈佛教授用"让你更困惑"来描述自己的教学——这不是反讽，而是承认理解的边界本身就是教学内容。把"不确定"当作认知的正常状态，而不是需要消除的故障。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 071 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p173@0-p177@20:highlight:71`
- source span: `src:c1:p174@0-p174@33`
- source span excerpt:
```text
有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。
```
- visible reaction:
```text
"不想"而非"不能"——是主动的道德选择，不是能力约束。清算价值在这里不是被放弃的技术选项，而是被主动拒绝的价值路径。这个措辞让芒格的态度从"做不到"切换到"不做"，立场清晰。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 072 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p173@0-p177@20:highlight:72`
- source span: `src:c1:p175@0-p175@65`
- source span excerpt:
```text
老张是个老员工，勤勤恳恳地为公司工作了40年，我们不忍心把他辞掉。既然我们不愿做辞掉老张这样的事，估算公司的清算价值也没什么意义。
```
- visible reaction:
```text
"40年"这个数字具体而有力。一个人工作四十年的分量，让"不忍心"变得具体可感，也让"清算价值没什么意义"不再是抽象表态，而是一个有情感依托的结论。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 073 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p173@0-p177@20:highlight:73`
- source span: `src:c1:p177@0-p177@20`
- source span excerpt:
```text
西科的清算价值是多少？我不能向你们剧透。
```
- visible reaction:
```text
"剧透"这个词精确地捕捉了信息披露的本质：不是不知道，而是说出来会破坏某些东西。这个词与前面的校长笑话形成闭环，幽默中带着真实的边界感。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: '这个词与前面的校长笑话形成闭环'——明确回调前文的校长笑话比喻，建立'剧透'概念的叙事闭环。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 074 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p178@0-p182@34:highlight:74`
- source span: `src:c1:p180@0-p180@53`
- source span excerpt:
```text
他们最早买入的时候，西科很有价值。现在，西科已经没那么有价值了，他们还是愿意买。因为他们看好西科的管理者。
```
- visible reaction:
```text
"已经没那么有价值了"——这句话说得很平，却很重要。股东不是因为低估而买，而是越过价值问题去信任管理层。这让信任这件事变得非常纯粹，也非常脆弱。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 075 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p178@0-p182@34:discern:75`
- source span: `src:c1:p182@0-p182@34`
- source span excerpt:
```text
与之形成对照的是，西科不是好生意，但我们的股东因为信任管理层而买入。
```
- visible reaction:
```text
"不是好生意"和"信任管理层"用"但是"连接，是全文的逻辑落点。芒格不是在批评，而是在展示一种选择：有些投资决策的核心变量不是生意本身，而是管理层的可信度。这与前面"不想"而非"不能"清算的道德立场形成深层呼应——对人的信任可以独立于对生意的评估而成立。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 076 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p190@0-p190@338:highlight:76`
- source span: `src:c1:p190@263-p190@338`
- source span excerpt:
```text
芒格表示伯克希尔·哈撒韦越来越多地采用这种收购模式：他们因为欣赏和信任一家公司的管理层而收购；而管理层持有其余20%的股份，并不受干预地继续经营业务。
```
- visible reaction:
```text
这是对"不是好生意，但信任管理层"那句话的收购结构版本。信任不是抽象的判断，而是用20%股权和一张10年期票据具体落地的。管理层既是被信任的对象，也是利益绑定的一方——"不受干预"四个字是信任的核心承诺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: '这是对"不是好生意，但信任管理层"那句话的收购结构版本'——明确回调reaction 75，将信任从抽象判断落实为具体的股权和票据安排。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 077 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p204@0-p206@139:highlight:77`
- source span: `src:c1:p206@107-p206@139`
- source span excerpt:
```text
蒙特西托地区还有四五百块空置的土地，这些土地的所有者可成苦主了。
```
- visible reaction:
```text
"可成苦主了"——从被羡慕的地主变成受害者，这个转折用得很口语，却把管制后果说得极为直接。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 078 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p207@0-p207@87:retrospect:78`
- source span: `src:c1:p207@39-p207@62`
- source span excerpt:
```text
我们向圣巴巴拉市让渡了大量利益，才换来开发许可
```
- visible reaction:
```text
"让渡了大量利益"这几个字点出了开发许可是政治交易的产物，而非纯粹的市场行为。这和前面土地所有者"可成苦主了"构成同一张图景的两面：管制收紧之后，谁都觉得自己是受害者——已经开发的要援引既得权利，还没开发的要面对"可成苦主"的命运。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p204@0-p206@139:highlight:77"]}`
  - judge reason: 明确以reaction 77为锚——将'让渡了大量利益'定位为政治交易，与土地所有者的'苦主'处境构成同一张图景的两面。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 079 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p208@0-p210@119:highlight:79`
- source span: `src:c1:p208@0-p208@23`
- source span excerpt:
```text
我们对当地政府和居民简直是俯首帖耳、言听计从。
```
- visible reaction:
```text
"俯首帖耳、言听计从"——四个字把姿态说到头了。不是客气，不是配合，是彻底的低姿态。后面答应给邻居翻新大门又不设先例，字里行间已经是在给自己留退路。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 080 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p208@0-p210@119:retrospect:80`
- source span: `src:c1:p210@56-p210@78`
- source span excerpt:
```text
在圣巴巴拉市开发房地产，想赚钱，实在太难了。
```
- visible reaction:
```text
这八个字是整段的落点。前面的让步、管道、"尽到最大努力"都是铺垫，这句话才是实际结论：新法规只是压死骆驼的最后一根稻草，"太难了"是从一开始就在积累的底色。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p207@0-p207@87:retrospect:78"]}`
  - judge reason: 明确以reaction 78为锚——'太难了'是从reaction 78的'让渡大量利益'到开发许可困境的叙事落点，前面所有让步都是铺垫。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 081 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p211@0-p213@106:retrospect:81`
- source span: `src:c1:p213@0-p213@34`
- source span excerpt:
```text
这好比把你家左右各扣减六米，分给两边的邻居，因为邻居的投票数比你多。
```
- visible reaction:
```text
财产边界被投票数重新划定——这个比喻把抽象的权力博弈变成了物理空间的直接侵占，一下就穿透了法律与民主之间的那道裂缝。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p207@0-p207@87:retrospect:78"]}`
  - judge reason: 明确连接到reaction 78关于'让渡了大量利益'的政治土地博弈讨论，将财产边界被投票重新划定的比喻与前文政治干预主题直接衔接，逻辑清晰。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 082 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p214@0-p214@138:highlight:82`
- source span: `src:c1:p214@69-p214@89`
- source span excerpt:
```text
他们完全符合我们互助储蓄招聘员工的条件。
```
- visible reaction:
```text
这句话的讽刺在于：连自己的招聘标准都找不到比他们更合适的人——但这毫无用处，因为下一句直接点出了转折：受政治团体压力左右。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 083 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p214@0-p214@138:highlight:83`
- source span: `src:c1:p214@109-p214@138`
- source span excerpt:
```text
只是受政治团体的压力左右，他们遵循的是一套不同的价值体系。
```
- visible reaction:
```text
"不同"二字在此轻描淡写，实际上说的是：这些聪明正直的好人，在具体事务中做出了与道德判断相反的决定。政治压力将人格与行为切割开来。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 084 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p216@0-p216@40:highlight:84`
- source span: `src:c1:p216@0-p216@40`
- source span excerpt:
```text
我想提醒各位股东，别高兴地盘算我们的地产项目能大赚多少，这个项目离完工还早着呢。
```
- visible reaction:
```text
"别高兴地盘算"——在股东会上主动压制乐观情绪，这种预期管理本身就是一种权力动作：把讨论框架拉回到"还没到能算账的时候"，而不是跟着股东的乐观预期走。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 085 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p217@0-p219@83:highlight:85`
- source span: `src:c1:p218@41-p218@84`
- source span excerpt:
```text
一方面，不是富人，买不起我们的房子；另一方面，不是乐善好施的人，我们也不把房子卖给他。
```
- visible reaction:
```text
"另一方面"这个转折把筛选条件从财富推进到品格——有钱只是门槛，卖不卖还要看你是否"乐善好施"。这种双重过滤实际上是把慈善意愿也纳入了商业交易的隐性条款里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 086 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p217@0-p219@83:highlight:86`
- source span: `src:c1:p219@15-p219@38`
- source span excerpt:
```text
他们在哪居住，都会为当地贡献良多，而索取极少。
```
- visible reaction:
```text
"贡献良多，索取极少"——这句话用极简的对偶结构，把目标客户塑造成近乎纯粹的利他存在。这种修辞不是描述事实，而是一种说服策略：把商业开发的目标客群包装成公共福利的净贡献者。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 087 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p220@0-p220@98:highlight:87`
- source span: `src:c1:p220@59-p220@98`
- source span excerpt:
```text
举例来说，帕萨迪纳市最近也颁布了一项抑制增长的法规，给房地产开发商带来了打击。
```
- visible reaction:
```text
帕萨迪纳——西科互助储蓄的所在地。芒格在此处不动声色地告知股东，总部所在地的监管环境正在收紧。这不是泛泛的趋势讨论，而是直接关系到西科旗下机构的经营基础。把地方性法规作为"趋势"的佐证来引出，实际上是在给股东打预防针：压力已经在眼前了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 088 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p221@0-p221@61:highlight:88`
- source span: `src:c1:p221@27-p221@61`
- source span excerpt:
```text
从法规的严厉程度来说，帕萨迪纳市与圣巴巴拉市相比，那是小巫见大巫了。
```
- visible reaction:
```text
"小巫见大巫"这个成语把圣巴巴拉设为参照锚点，暗示帕萨迪纳的监管压力虽然真实存在，但尚在可承受范围内。这与前一段的"抑制增长法规"形成组合叙事：压力已来，但比较而言，还未触及极限。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 089 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p222@0-p224@160:highlight:89`
- source span: `src:c1:p224@117-p224@160`
- source span excerpt:
```text
我与这位主管只有一面之缘，我因为欣赏她，而持有乐观态度，但这不足以作为判断未来的依据。
```
- visible reaction:
```text
"不足以作为判断未来的依据"——这句话是芒格向股东的明确免责声明：他把个人印象摆上台面，但拒绝让这种印象混入确定性判断。对比前文他在其他话题上的自信语气，这里反而显出一种刻意的降调：他不是不能乐观，而是要确保听众知道乐观的真正分量。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 090 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p225@0-p229@85:discern:90`
- source span: `src:c1:p228@0-p228@54`
- source span excerpt:
```text
他们的这种文化有很多可取之处。他们的文化之中有智慧，有对自然的尊重。我代表的这种文化之中倒很可能有许多弊端。
```
- visible reaction:
```text
这里芒格把自己所属的文化类型直接置于审判席上——不是谦虚的套话，而是一种真实的自我对照。"我代表的这种文化"这个措辞不是泛指，而是有具体所指的：他习惯的那种高效、目标导向、不拖泥带水的商业文化。在他一贯的自信叙述中，这种主动的自我限定相当罕见。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 091 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p230@0-p234@183:highlight:91`
- source span: `src:c1:p232@137-p232@170`
- source span excerpt:
```text
连续两年，每年保费都降低一半，正常的保险公司怎么可能接这样的单子？
```
- visible reaction:
```text
这个反问把行业的非理性定价直接摆上台面。保费已经低到无法用正常风险模型解释，却仍有人接单——这不是市场失灵，而是竞争压力下的囚徒困境。"畏惧"这个词既是情绪，也是芒格对这种结构性扭曲的诚实反应。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 092 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p230@0-p234@183:highlight:92`
- source span: `src:c1:p234@65-p234@152`
- source span excerpt:
```text
业绩规模是用了近百年时间才积累起来的，负责核保、理赔的众多员工和你共事多年，都是非常熟悉的老同事了，怎么可能轻而易举地说：“算了，保费低到没法做了，我们要把规模削减80%。”
```
- visible reaction:
```text
这段话揭示了机构规模与理性决策之间的根本矛盾：知道应该收缩，却说不出口、做不动。不是判断失误，而是组织惯性和人际关系形成了真实的执行壁垒。这与前文西科"采取守势"的策略形成对照——守势是主动选择，但收缩到极致也需要条件，而有些机构连这个条件都不具备。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 093 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p239@0-p239@106:retrospect:93`
- source span: `src:c1:p239@52-p239@83`
- source span excerpt:
```text
降低保费20%的要求太过分了，不符合传统法律文化，应该被驳回。
```
- visible reaction:
```text
这里芒格明确站到了"传统法律文化"一边——不是从经济学效率角度，而是从宪法精神角度判断监管干预的边界。结合前文他主动说"我代表的这种文化之中倒很可能有许多弊端"，这个法律立场的选择就有了微妙的自我对照意味：他批评的那种文化（高效率、目标导向），在保险行业的语境下，恰恰可能是抵制价格管制、维护市场定价权的文化。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p225@0-p229@85:discern:90"]}`
  - judge reason: 明确连接到reaction 90（discern关于'我代表的这种文化'），将法律文化立场选择与芒格自批评形成有意义的对照。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 094 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p239@0-p239@106:retrospect:94`
- source span: `src:c1:p239@83-p239@103`
- source span excerpt:
```text
无论如何，人身保险公司的苦日子也要来了。
```
- visible reaction:
```text
这是预测的收尾，但也是最诚实的一句。法律上阻止了20%的强制降幅，但行业的基本困境——保费已经低到无法维持正常运营——并不因此消失。苦日子要来的"无论"两字说明：司法胜利救不了行业基本面。这与前文描述的公司无法自我收缩到80%的结构性痼疾形成呼应：既不能靠市场自我调节，也很难靠法律救济，整个行业的困境是系统性的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p230@0-p234@183:highlight:91", "reaction:rx:Full_Content:src:c1:p230@0-p234@183:highlight:92"]}`
  - judge reason: 连接到reactions 91和92，将司法胜利救不了行业基本面的结论与结构性无法收缩的痼疾直接衔接。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 095 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p240@0-p241@98:highlight:95`
- source span: `src:c1:p240@136-p240@162`
- source span excerpt:
```text
人身保险行业将承受越来越大的政治压力，尤其是在加州。
```
- visible reaction:
```text
这里把政治压力明确锁定加州，和前文加州103号提案的法律争议形成呼应——法律诉讼失败了，但政治压力会持续。结构性矛盾没有因为一次司法胜利而消解。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 096 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p240@0-p241@98:highlight:96`
- source span: `src:c1:p241@56-p241@98`
- source span excerpt:
```text
未来四年，消防员基金保险公司将如何？能否像过去四年一样平稳发展？这是一个很大的问号。
```
- visible reaction:
```text
从宏观行业困境转到一个具体公司的未来不确定性。"很大的问号"和前文"无论如何苦日子也要来"形成逻辑衔接：苦日子不是抽象的，是对每个具体公司实实在在的考验。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 097 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p242@0-p243@138:highlight:97`
- source span: `src:c1:p243@77-p243@138`
- source span excerpt:
```text
如果不是沃伦同意为消防员基金保险公司担任顾问，我们做不成这笔交易。我们沾了母公司的光，我们的这份合同是伯克希尔送给我们的。
```
- visible reaction:
```text
诚实得少见——把子公司的成功直接挂在母公司名下，不抢功，也不掩饰"靠山"的价值。这和前文反复强调的西科独立性形成了一个张力：在经营上强调自主判断，在资源上又坦承依赖伯克希尔的关系网络。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 098 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p244@0-p246@97:highlight:98`
- source span: `src:c1:p246@0-p246@36`
- source span excerpt:
```text
伯克希尔有个原则，如果不能换来同等的内在价值，伯克希尔绝对不会发行股票。
```
- visible reaction:
```text
这个"同等内在价值"的表述把前文芒格反复提到的"公平"标准进一步明确化了——不是账面价值、不是市场报价，而是内在价值。而且语气斩钉截铁："绝对不会"。这和他在其他地方表述"宁可不动，也不占别人便宜"的原则是一以贯之的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 099 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p247@0-p248@129:highlight:99`
- source span: `src:c1:p248@0-p248@26`
- source span excerpt:
```text
从所罗门这笔投资中可以看出来，我们有多擅长捕捉时机。
```
- visible reaction:
```text
这个开头是反语，"擅长捕捉时机"在此处是一句自我调侃的笑谈，紧接着就说明这笔交易做完一周就撞上了黑色星期一。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 100 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p247@0-p248@129:highlight:100`
- source span: `src:c1:p248@98-p248@129`
- source span excerpt:
```text
我们刚达成交易，市场就出现了百年一遇的暴跌。这点踩的，太背了。
```
- visible reaction:
```text
"太背了"把芒格一贯的自我诚实推向一个轻快的收尾——不是解释、不是辩护，只是把运气不好的事实摊开来讲，语气和前面"我们有多擅长捕捉时机"形成完整的自嘲弧线。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 101 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p249@0-p250@90:highlight:101`
- source span: `src:c1:p250@67-p250@90`
- source span excerpt:
```text
我们没有未卜先知的能力，这笔交易没赶上好时机。
```
- visible reaction:
```text
这个收尾把"时机运气"和"决策质量"明确区分开了。交易本身的逻辑是成立的，环境不利纯粹是运气问题——不是判断失误。这种把运气和决策分开来讲的做法，和前面"擅长捕捉时机"的反语形成完整的自嘲弧线。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 102 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p251@0-p252@69:highlight:102`
- source span: `src:c1:p252@0-p252@69`
- source span excerpt:
```text
投资银行的生意波动很大，所罗门的生意肯定会起起伏伏，有年景不好的时候，也有年景好的时候。所罗门人才济济，他们应该有能力克服将来遇到的困难。
```
- visible reaction:
```text
这里出现了芒格对所罗门人才储备的直接信任——不是承诺，而是对能力的基本判断。和前面的自嘲形成对照：运气不好是运气，班底够硬是班底够硬，两件事分开说。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 103 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p253@0-p253@247:highlight:103`
- source span: `src:c1:p253@144-p253@163`
- source span excerpt:
```text
他们干得很漂亮，一般的公司没这个本事。
```
- visible reaction:
```text
这句话把所罗门的能力和"一般公司"做了明确区隔，语气直接，不是泛泛的客套——是在为已经完成的240万股交易作证。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 104 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p253@0-p253@247:highlight:104`
- source span: `src:c1:p253@184-p253@233`
- source span excerpt:
```text
所罗门在芝加哥有一位合伙人，名叫布莱恩（Bryan），他为我们做了很多工作，是一个特别有能力的人。
```
- visible reaction:
```text
"特别有能力"这个措辞从前面"人才济济"的集体描述落实到了个人。和西科对蒂施家族的信任表达方式一致——先是肯定群体，然后点出具体的人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 105 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p254@0-p257@94:highlight:105`
- source span: `src:c1:p255@0-p255@31`
- source span excerpt:
```text
我们走到今天，靠的不是预测未来的利率高低，预测经济周期的变化。
```
- visible reaction:
```text
这是整个段落的起点——把"不预测"作为已经验证过的方法论，而不是防御性托词。结合近期记忆里多次提到市场风险和机会缺乏，这句话有一种笃定感：不是不能预测，而是主动选择不预测。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 106 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p254@0-p257@94:highlight:106`
- source span: `src:c1:p255@122-p255@205`
- source span excerpt:
```text
我们始终把眼前所有的投资机会进行比较，力求找到当下最合理的投资逻辑，这才是重中之重。找到了最合理的投资逻辑之后，无论周期波动如何剧烈，是顺境还是逆境，我们都泰然自若。
```
- visible reaction:
```text
这里把方法论展开为两步：比较机会找最合理的逻辑，然后在任何周期条件下都保持泰然。"重中之重"突出了这个习惯动作的优先级——比预测、规划都重要。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0008` / note `mangge_zhi_dao_private_zh_personal_notes__e0008` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p255@122-216` 我们始终把眼前所有的投资机会进行比较，力求找到当下最合理的投资逻辑，这才是重中之重。找到了最合理的投资逻辑之后，无论周期波动如何剧烈，是顺境还是逆境，我们都泰然自若。这就是我们的投资之道。
    - target note: 我们始终把眼前所有的投资机会进行比较，力求找到当下最合理的投资逻辑，这才是重中之重。找到了最合理的投资逻辑之后，无论周期波动如何剧烈，是顺境还是逆境，我们都泰然自若。这就是我们的投资之道。
    - source-span relation: `note_contains_candidate`; coverage `0.88`
    - judge/runner reason: The visible reaction's source span covers the core content of the note's source span (comparing opportunities, finding the most reasonable logic, maintaining calm through cycles), with only the concluding sentence '这就是我们的投资之道' excluded. The commentary directly engages with the key concepts: the two-step methodology of comparing opportunities and maintaining composure, and emphasizes the significance of '重中之重' (top priority). This represents genuine focused coverage of the note's important content.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0008.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 107 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p254@0-p257@94:highlight:107`
- source span: `src:c1:p256@0-p256@68`
- source span excerpt:
```text
我完全不知道，明年的道指将是涨是跌，利率是14%，还是6%。我不知道，投行的生意将迎来一波繁荣潮，还是将进入衰退的寒冬期。我们真不知道。
```
- visible reaction:
```text
三个"不知道"的并列，语气平静但坚定。值得注意的是：不知道自己不知道什么和知道自己不知道什么，在这里都呈现为一种坦诚的能力边界声明，不是谦虚表演。和前面提到的所罗门人才判断放在一起看：对人的判断自信，对宏观的不可知同样自信。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 108 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p254@0-p257@94:highlight:108`
- source span: `src:c1:p257@65-p257@94`
- source span excerpt:
```text
除非是监管部门要求的，伯克希尔·哈撒韦从来不制定长期规划。
```
- visible reaction:
```text
这是整个段落的语气终点，掷地有声。"除非是监管部门要求的"是一个精准的边界条件，说明他们不是意识形态性地反对规划，而是拒绝一切没有外部约束的规划。配合前面"我们真不知道"的自述，这条原则很自然：既然不知道未来，就不为不知道的事做计划。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 109 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p258@0-p259@190:highlight:109`
- source span: `src:c1:p259@90-p259@115`
- source span excerpt:
```text
谁不想看得远一些？问题是，想看得远，也看不了多远。
```
- visible reaction:
```text
这句话把"认知有限"从自我怀疑翻转成行动前提。不是因为看不清而焦虑，而是因为看不远，所以干脆不看——把注意力收回到眼前能做的事上。语气平静，但逻辑很彻底。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010` / note `mangge_zhi_dao_private_zh_personal_notes__e0010` / label `incidental_cover` / best `false` / recall-credit `false`
    - target span(s): `p259@90-157` 谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
    - target note: 谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
    - source-span relation: `note_contains_candidate`; coverage `0.37`
    - judge/runner reason: 反应引用的源文本'谁不想看得远一些？问题是，想看得远，也看不了多远。'确实与笔记开头重叠，并抓住了作者将'认知有限'转化为行动前提的核心逻辑。但用户标注的后半部分——关于具体行动（开动脑筋、埋头苦干、处理眼前每件事）和结果预期（打造优秀公司）——在反应中完全未触及。反应只涵盖了笔记约37%的内容，遗漏了这条建议的重要组成部分。
    - reviewer interpretation: Supporting only: the reaction touched the note span but did not make the note-level idea central enough for recall credit.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 110 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p258@0-p259@190:highlight:110`
- source span: `src:c1:p259@115-p259@157`
- source span excerpt:
```text
只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
```
- visible reaction:
```text
"好公司是副产品"——这里的措辞很有意思：不是规划出来的，不是愿景驱动的，而是做好眼前每件事的结果。这和前面"从来不制定长期规划"完全一致：好的结果不是目标，眼前的行动才是。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010` / note `mangge_zhi_dao_private_zh_personal_notes__e0010` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p259@90-157` 谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
    - target note: 谁不想看得远一些？问题是，想看得远，也看不了多远。只要开动脑筋、埋头苦干，把眼前的每件事处理好了，你最后很可能会打造出一家优秀的公司。
    - source-span relation: `note_contains_candidate`; coverage `0.63`
    - judge/runner reason: The reaction's quoted source span (the latter half of the note) captures the core message: that good results emerge from focusing on immediate actions rather than long-term planning. The interpretation ('好公司是副产品') and the connection to the '从来不制定长期规划' theme directly address the note's essential point about practical action leading to good outcomes. The overlap is not incidental—the reaction intentionally engages with the note's central idea, even though it doesn't quote the opening rhetorical question.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0010.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 111 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p260@0-p261@68:discern:111`
- source span: `src:c1:p261@0-p261@48`
- source span excerpt:
```text
我们也做长期的准备，主要是尽可能地保守，防范大灾难的冲击。我们为可能出现的最恶劣的环境做好准备。
```
- visible reaction:
```text
"最恶劣的环境"——这个措辞很有意思。不是"最可能的不利情况"，而是"最恶劣"。这意味着他们准备的不是概率加权后的预期损失，而是极端尾部风险。配合前面的"不见机行事"，这里的"见机行事"是双向的：既不在没有机会时硬投，也不在有机会时忘乎所以。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 112 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p260@0-p261@68:highlight:112`
- source span: `src:c1:p261@48-p261@68`
- source span excerpt:
```text
长期以来，我们的资产负债表始终非常保守。
```
- visible reaction:
```text
这句话把"保守"从哲学立场落地成了财务事实。不是因为没能力激进，而是主动选择了保守作为防御大灾难的代价。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 113 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p262@0-p266@84:highlight:113`
- source span: `src:c1:p266@0-p266@84`
- source span excerpt:
```text
有一类人，聪明而又懒惰，这类人是指挥官的绝佳人选。总参谋部提出的大量作战方案中，有很多根本不可行。只有聪明而又懒惰的指挥官，才能去粗取精，从中挑选出一两个最合理的方案。
```
- visible reaction:
```text
这个"聪明而懒惰"的定义落地得很实在：不是无为，而是"在大量不可行方案中只挑一两个合理的"。这是主动筛选能力的赞美，不是躺平。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 114 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p267@0-p271@59:highlight:114`
- source span: `src:c1:p267@0-p267@68`
- source span excerpt:
```text
有一类人，聪明而又勤奋。这类人适合进总参谋部。他们能不停地出谋划策，制定出大量方案。有了足够多的方案，才便于从中挑选出最合适的用于实战。
```
- visible reaction:
```text
聪明而懒惰做指挥官，聪明而勤奋做参谋——这两类人构成了"大量方案"和"只挑一两个"的分工。整个链条是：勤奋参谋生产选项，懒惰指挥官做减法。这和前面"大量现金找不到好机会"形成了平行的资源配置逻辑：选项多不是问题，不会筛选才是。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 115 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p267@0-p271@59:highlight:115`
- source span: `src:c1:p269@7-p269@38`
- source span excerpt:
```text
一类是品行不端的人，一类是愚蠢而又勤奋的人，这两类人都是祸害。
```
- visible reaction:
```text
"品行不端"和"愚蠢而勤奋"并列为祸害——前者是道德失败，后者是执行失败。这个并置很直接：勤勉如果没有判断力护航，就是把错误放大十倍的加速器。配合"必须遣散"的军事表述，愚蠢的勤奋在这里不是中性缺点，而是有破坏力的危险因素。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0012` / note `mangge_zhi_dao_private_zh_personal_notes__e0012` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p268@0-33` 最后，还有一类人，愚蠢而又勤奋。按照陆军操典所说，此类人必须遣散。; `p269@0-38` 我们深有同感。一类是品行不端的人，一类是愚蠢而又勤奋的人，这两类人都是祸害。
    - target note: 最后，还有一类人，愚蠢而又勤奋。按照陆军操典所说，此类人必须遣散。我们深有同感。一类是品行不端的人，一类是愚蠢而又勤奋的人，这两类人都是祸害。
    - source-span relation: `note_contains_candidate`; coverage `0.44`
    - judge/runner reason: The reaction's quoted source span captures the core claim—'品行不端' and '愚蠢而勤奋' both being hazards—from paragraph 269. While the note's source includes a preceding paragraph (268) with '必须遣散' context, the reaction's commentary explicitly discusses this military terminology and covers the note's central thesis that both categories are destructive. The coverage (43.66%) is modest but sufficient to address the note's main point.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0012.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 116 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p272@0-p274@84:retrospect:116`
- source span: `src:c1:p274@0-p274@84`
- source span excerpt:
```text
我们有个规矩，除非是法律要求披露，我们不谈论我们的有价证券投资活动。我们一般也不会公开谈论我们的投资逻辑，房地美算是个特例，因为我们已经达到了买入上限，不能买入更多了。
```
- visible reaction:
```text
"不谈论"是一种主动的认知边界，而非信息披露义务的被动应对。这个规矩的实质是：保护决策空间，不向市场解释逻辑。只有当客观约束（买入上限）出现时，才例外开口——这和"攥在手里，不意味着永远"的立场一致：行动由内部判断驱动，而非外部解释需求。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:wesco_asset_deployability"]}`
  - judge reason: prior_link连接到active_attention:wesco_asset_deployability，与前文'攥在手里，不意味着永远'的立场一致，逻辑清晰。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 117 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p272@0-p274@84:retrospect:117`
- source span: `src:c1:p272@29-p272@56`
- source span excerpt:
```text
占比如此之高的流动资产，该如何配置？管理层还一无所知。
```
- visible reaction:
```text
"一无所知"在这里是坦诚的自我描述，不是能力失败的托辞——他们诚实面对的是"有资产、无机会"的结构性状态，而不是掩盖找不到好标的的事实。这个措辞和前文"找不到好机会，没地方配置"完全一致，但"管理层还一无所知"多了一层主动承认无知的味道。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["active_attention:wesco_asset_deployability", "active_attention:wesco_defensive_posture"]}`
  - judge reason: prior_link连接到wesco_asset_deployability和wesco_defensive_posture，与'找不到好机会'的结构性状态讨论直接衔接。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 118 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p275@0-p275@77:retrospect:118`
- source span: `src:c1:p275@49-p275@77`
- source span excerpt:
```text
不发表评论就是不发表评论，没什么隐藏含义，不必揣摩猜测。
```
- visible reaction:
```text
这个反身句式（"不X就是不X"）干脆堵死了揣测的入口。语气近乎防御性——仿佛预见到有人会在沉默里找信号，于是提前把门焊死。这和前文"保护决策空间，不向市场解释逻辑"一脉相承：沉默是空白，不是谜面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p272@0-p274@84:retrospect:116"]}`
  - judge reason: prior_link连接到reaction 116，直接承接'沉默是空白，不是谜面'的论述。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 119 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p278@0-p282@44:highlight:119`
- source span: `src:c1:p280@0-p280@106`
- source span excerpt:
```text
无论做什么行业，对手不如你，却能得到补贴，那还怎么竞争？你在一条街上开了一家干洗店，这条街上还有其他家干洗店，它们能得到政府的补助，你的生意还怎么做？人家的价格会低到你根本经营不下去。储贷行业的现有体系是病态的。
```
- visible reaction:
```text
干洗店比喻非常直觉，直接把补贴竞争的扭曲效果拉到日常经验里。"病态的"这个词用在体系上，不是针对竞争对手，而是针对整个游戏规则——这是结构性批判，不是策略性抱怨。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 120 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p278@0-p282@44:highlight:120`
- source span: `src:c1:p282@0-p282@44`
- source span excerpt:
```text
混乱局面出现了，你拥有雄厚的财力，可能会有好机会。别人都把子弹打没了，你可能会有好机会。
```
- visible reaction:
```text
这句话是整段的落脚点，也是芒格式的冷机会主义：混乱是机会，但前提是你有弹药。和前文"攥在手里，不意味着永远"以及"找不到好机会，没地方配置"形成呼应——现在守着大量资产不动，关键时刻可能是优势。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 121 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p283@0-p284@41:highlight:121`
- source span: `src:c1:p284@23-p284@41`
- source span excerpt:
```text
我们的贷款政策在储贷行业中比较另类。
```
- visible reaction:
```text
"另类"这个词在"病态的"行业背景下不是自嘲，而是自我定位——不随行业潜规则走，才可能避开那些结构性风险。和前文干洗店的比喻形成明确分野：行业补贴游戏是扭曲的，西科的应对方式是在规则内保持独立判断，不去玩那个游戏。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 反应121明确引用了前文'干洗店'比喻和'病态的'行业定性（反应119-120），并将西科'另类'定位与之形成清晰分野，构成正确的往前回指。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 122 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p285@0-p286@124:highlight:122`
- source span: `src:c1:p286@55-p286@124`
- source span excerpt:
```text
就算我们能做到利率上限设在25%，而且能保证100%完全收回贷款，但是最终要没收房产，让一些勤劳本分的人痛苦万分，我还是不愿做这样的贷款。
```
- visible reaction:
```text
"就算能做到"这个条件句是关键：不是说自己做不到，而是在能做到的情况下仍然拒绝。这是超越商业理性的原则宣示——不是能力问题，是意愿问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 123 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p287@0-p287@125:discern:123`
- source span: `src:c1:p287@35-p287@96`
- source span excerpt:
```text
棕榈泉（Palm Springs）是个沙漠小镇。当地人顶着40多摄氏度的高温在沙漠之中用水泵打水。要住酒店，只能乘船前往。
```
- visible reaction:
```text
这三个细节不是装饰——"40多摄氏度"量化了生存条件的恶劣，"用水泵打水"点出了生态不可持续，"只能乘船前往"则把地理隔绝推向荒诞。这个组合本身就是对"为什么不能在这里放贷"的无声论证：不是市场风险，而是那里的生活方式本身就建立在一种脆弱的依赖之上，放贷介入只会把脆弱变成灾难。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 124 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p287@0-p287@125:highlight:124`
- source span: `src:c1:p287@112-p287@125`
- source span excerpt:
```text
这确实是很奇怪的限制条件。
```
- visible reaction:
```text
作者两次自我标记"奇怪"：先"你可能觉得我的想法很怪"，结尾又"这确实是很奇怪的限制条件"。承认但不撤回，这是前文"就算能做到……我还是不愿"的姿态在地理维度上的再次呈现。伦理判断不需要说服别人，只需要自己清楚。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 反应124直接引用'就算能做到……我还是不愿'（反应122）和两处'奇怪'自我标注，将'承认但不撤回'的姿态从道德维度延伸到地理维度，构成精确且正确的回指。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 125 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p288@0-p288@88:highlight:125`
- source span: `src:c1:p288@39-p288@88`
- source span excerpt:
```text
我设置了这么多条条框框，我们负责贷款业务的鲍勃·阿斯顿（Bob Aston）很难把业务规模做上去。
```
- visible reaction:
```text
「条条框框」这个说法轻描淡写，和前面两次自我标注「奇怪」是同一个姿态——承认代价，但不收回立场。没有辩解，没有解释为什么这对Bob Aston不公平。伦理约束的成本被平实地陈述出来，像在说天气。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 反应125引用'前面两次自我标注奇怪'，即反应124中'你可能觉得我的想法很怪'和'这确实是很奇怪的限制条件'两处原文，实现正确的向前回指。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 126 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p291@0-p295@15:discern:126`
- source span: `src:c1:p293@26-p293@79`
- source span excerpt:
```text
在通过派息的方式，将大部分资金从子公司互助储蓄中抽离之后，互助储蓄中仅保留计提的坏账准备金4700万美元。
```
- visible reaction:
```text
「大部分资金」通过派息抽离，只剩4700万坏账准备金——这不是贷款业务的衰退，而是整个子公司的结构性清空。原本是主营业务载体，现在只剩下一个坏账壳。这和前文「主要资金已经不在储蓄和贷款子公司」形成精确对应：钱走了，壳留下，专门处理遗留的坏账准备。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 反应126明确引用前文'主要资金已经不在储蓄和贷款子公司'表述，将子公司从业务载体转变为坏账壳的演变过程与之精确对应，构成文本层面的正确回指。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 127 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p291@0-p295@15:highlight:127`
- source span: `src:c1:p295@0-p295@15`
- source span excerpt:
```text
消防员基金保险公司的前景很难说
```
- visible reaction:
```text
这是一个悬空的句子，没有主句，没有结论。在整段关于贷款业务和互助储蓄的叙述之后，突然抛出这一句，像是某段被截断的文字留在那里。「前景很难说」是评价还是悬置？没有答案，只有这一句话孤零零地立着。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 128 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p296@0-p300@9:highlight:128`
- source span: `src:c1:p299@9-p299@88`
- source span excerpt:
```text
一方面，他们两个都是非常有可能取得成功的人。任何一家公司，只要有他们两个人之中的一个掌管，我都不会看空；另一方面，形势确实非常不利，更何况，还有那么高的杠杆。
```
- visible reaction:
```text
这里把「人」和「势」拆开评判：个人能力足以支撑任何公司，但行业周期加高杠杆的组合又足以压垮任何个人。人才强不强的问题和行业环境好不好是两个独立变量，不能直接抵消。前一句是真实判断，后一句也是真实判断，但两者之间留了空白——读者自己去想什么时候人压过势，什么时候势压过人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 129 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p296@0-p300@9:highlight:129`
- source span: `src:c1:p300@0-p300@9`
- source span excerpt:
```text
精密钢材将保持优秀
```
- visible reaction:
```text
又一个孤立的标题式句子，与段落296开篇的「这也不全是坏事」形成同一种处理方式：不展开，不解释，结论式地抛出来。不同之处在于，前者是对已发生事件的价值重塑，后者是对未来状态的断言。两者都没有主语叙述，只有判断。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 130 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p301@0-p303@66:highlight:130`
- source span: `src:c1:p302@11-p302@62`
- source span excerpt:
```text
精密钢材已经在钢铁服务业中做到了极致。它的管理已经做到了无可挑剔。这意味着，精密钢材没什么上升潜力了。
```
- visible reaction:
```text
「做到了极致」和「没什么上升潜力」之间没有转折词，直接等同——这是结构性讽刺：做到了最好，反而触到了天花板。管理无可挑剔本来是优点，在这里变成了没有增长空间的另一种说法。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 131 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p301@0-p303@66:retrospect:131`
- source span: `src:c1:p303@23-p303@66`
- source span excerpt:
```text
精密钢材在整个西科中所占比重很低，我们的钢铁服务业务做得再好，对西科的贡献也十分有限。
```
- visible reaction:
```text
质量判断和权重判断在此分叉：做得好和贡献大是两回事。这与前文「人」和「势」的独立判断逻辑一致——每个维度都可以是真的，但合在一起决定了是否值得期待。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p296@0-p300@9:highlight:128"]}`
  - judge reason: Prior_link correctly references reaction 128 ('人'与'势'的独立判断), and this reaction builds on that framework—extending it to '质量判断与权重判断的分叉' with proper elaboration.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 132 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p304@0-p304@83:highlight:132`
- source span: `src:c1:p304@41-p304@83`
- source span excerpt:
```text
虽然不如我们的精密钢材，但这家公司也还可以，只是近两倍净资产的价格，我们觉得太贵了。
```
- visible reaction:
```text
「也还可以」和「太贵了」之间没有犹豫，语气近乎轻松——买得起但不买，因为不值得。这是估值纪律的具体执行，不是在评估质量时犹豫不决。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 133 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p307@0-p310@112:highlight:133`
- source span: `src:c1:p307@17-p307@62`
- source span excerpt:
```text
决定结果的主要有两个因素：一个是形势，另一个是人。形势太强，任凭你有多大能力，都无济于事。
```
- visible reaction:
```text
这个"形势与人"的二分法是前面"质量判断与权重判断分叉"的更底层版本——不是一件事做得好不好，而是外部环境是否允许做得好这件事产生效果。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0013` / note `mangge_zhi_dao_private_zh_personal_notes__e0013` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p307@0-62` 这个经历让我懂得了一个深刻的道理。决定结果的主要有两个因素：一个是形势，另一个是人。形势太强，任凭你有多大能力，都无济于事。
    - target note: 这个经历让我懂得了一个深刻的道理。决定结果的主要有两个因素：一个是形势，另一个是人。形势太强，任凭你有多大能力，都无济于事。
    - source-span relation: `note_contains_candidate`; coverage `0.73`
    - judge/runner reason: The reaction's quoted span (char 17-62) covers the core substantive content of the note—the two-factor framework of situation vs. person and the insight about circumstances overriding individual ability. The reaction goes beyond mere overlap to genuinely interpret and elaborate on this central message, framing it as a 'more底层' version of a related concept. The note's opening framing sentence is omitted from the quote but the important analytical content is fully captured.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0013.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 134 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p307@0-p310@112:highlight:134`
- source span: `src:c1:p310@100-p310@112`
- source span excerpt:
```text
打得过就打，打不过就跑。
```
- visible reaction:
```text
结论干脆，没有道德色彩。这和前文"攥在手里，不意味着永远"的立场一致：不是不能动，是形势不好时不硬撑。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015` / note `mangge_zhi_dao_private_zh_personal_notes__e0015` / label `exact_match` / best `true` / recall-credit `true`
    - target span(s): `p310@100-112` 打得过就打，打不过就跑。
    - target note: 打得过就打，打不过就跑。
    - source-span relation: `exact_same_span`; coverage `1.00`
    - judge/runner reason: Visible reaction source span exactly matched the aligned note span.
    - reviewer interpretation: Exact credit: the reaction span exactly matches the dataset note target span.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0015.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 135 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p311@0-p315@47:highlight:135`
- source span: `src:c1:p312@93-p312@116`
- source span excerpt:
```text
他们没等山姆·沃尔顿的新店开张，就宣布关店了。
```
- visible reaction:
```text
这个细节很有力：他们甚至没有等对手真的开业就决定关门。不是被打败，而是主动选择了不参战。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 136 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p311@0-p315@47:retrospect:136`
- source span: `src:c1:p314@24-p314@48`
- source span excerpt:
```text
谁爱去谁去，反正我不去。你的提议不错，但我不干。
```
- visible reaction:
```text
这句话在"形势与人"的框架上叠加了礼貌的拒绝。"提议不错"和"但我不干"之间没有犹豫——不是因为提议坏，是因为形势判断已经做完。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p307@0-p310@112:highlight:133"]}`
  - judge reason: Prior_link correctly references reaction 133's '形势与人' framework; reaction builds on it by adding '礼貌的拒绝' dimension—'提议不错' + '但我不干'—directly extending the earlier analysis with the same logical structure.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 137 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p324@0-p325@37:highlight:137`
- source span: `src:c1:p324@0-p324@12`
- source span excerpt:
```text
附录一 投资房地美的逻辑
```
- visible reaction:
```text
附录不是补充，而是专题。标题直接点出核心案例：投资房地美。放在正文末尾作为附录，暗示这部分可能包含某种后来才显出价值的判断逻辑，值得留意。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 138 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p326@0-p328@171:highlight:138`
- source span: `src:c1:p327@87-p327@117`
- source span excerpt:
```text
我们的持股数量占总流通股的4%，达到了单一股东持股比例上限。
```
- visible reaction:
```text
连续增持到法规允许的上限——这不是偶发的投资，而是有意识的建仓行为，对这只股票下了重注。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 139 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p329@0-p330@194:highlight:139`
- source span: `src:c1:p330@0-p330@52`
- source span excerpt:
```text
房地美是一个混合体，它仍然接受联邦住房贷款银行委员会的监管，但已经完全由私人出资，股东主要是机构投资者。
```
- visible reaction:
```text
"混合体"这个词在这里不是模糊的妥协，而是一个精确的结构描述：政府背书加私人效率。这种中间态恰好是它的护城河所在——能享受监管红利，却不必像纯国有企业那样承担政策任务。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 140 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p331@0-p332@79:retrospect:140`
- source span: `src:c1:p332@48-p332@79`
- source span excerpt:
```text
我们的税前股息率只有5.35%，税后股息率更低，只有4.4%。
```
- visible reaction:
```text
"只有"两字在这里很关键。它表明这些数字是谦逊的，不是亮眼的理由。那么"亮眼的财务数字"这个标题，究竟亮眼在哪里？暗示随后的叙述会给出答案——也许不是股息，而是资本利得或结构性价值。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p329@0-p330@194:highlight:139"]}`
  - judge reason: 通过'亮眼的财务数字'这个标签词，精准回调至前文反应139对'混合体'双重身份的描述——从身份结构导出数字谦逊的逻辑，链路清晰。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 141 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p335@0-p336@85:highlight:141`
- source span: `src:c1:p336@44-p336@85`
- source span excerpt:
```text
投资者担心房地美的监管部门可能失职，或者迫于国会的压力，给予私人资本不公平的待遇。
```
- visible reaction:
```text
第二个原因才是核心——"混合体"的双重身份既是护城河，也是市场疑虑的来源。享受监管红利，却同时担心监管本身会偏向私人资本，这种矛盾立场是市场定价偏低的关键。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 142 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p337@0-p338@207:highlight:142`
- source span: `src:c1:p338@0-p338@38`
- source span excerpt:
```text
投资者之所以有上述担心，主要是联邦储蓄贷款保险公司的前车之鉴让他们心有余悸。
```
- visible reaction:
```text
这个因果链很关键：投资者的疑虑不是针对房地美本身，而是对整个监管体系的反射性不信任。"前车之鉴"说明这是从历史创伤中学到的行为模式，而不是对当前风险的结构性分析。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 143 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p337@0-p338@207:highlight:143`
- source span: `src:c1:p338@137-p338@182`
- source span excerpt:
```text
监管部门未能及早出手干预，把问题扼杀在萌芽之中，结果风险迅速膨胀，最终到了无法收拾的地步。
```
- visible reaction:
```text
"扼杀在萌芽之中"这个说法在这里是双关：它既是批评监管失职的理由，也是为房地美辩护的隐含框架——房地美的问题还没到"萌芽"阶段，不存在需要"扼杀"的风险。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 144 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p339@0-p340@78:highlight:144`
- source span: `src:c1:p340@21-p340@37`
- source span excerpt:
```text
监管部门不可能让房地美步其后尘。
```
- visible reaction:
```text
这是明确的辩护性断言。但"不可能"在这里不是凭空的乐观承诺，而是紧接着用"历史和现实情况截然不同"来支撑——是一种有条件保证，而非无条件保证。巴菲特在这里区分了两个层面：监管意愿（不可能任其倒下）和机构现实（两家本质上不同）。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 145 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p339@0-p340@78:retrospect:145`
- source span: `src:c1:p340@60-p340@78`
- source span excerpt:
```text
两家公司的历史和现实情况也截然不同。
```
- visible reaction:
```text
这句是差异化论证的核心。"历史"对应前文提及的FSLIC创伤（历史包袱不同），"现实情况"指向房地美的结构特征（混合体身份等）。这个对照与前文的"前车之鉴"形成呼应——不是说监管不会失职，而是说这个机构本身与那个"前车"根本不同，因此不适用同一个历史教训。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p337@0-p338@207:highlight:142"]}`
  - judge reason: 明确引用前文highlight:142的'前车之鉴'概念，并将其与p340的'历史和现实情况截然不同'对照衔接，说明房地美不适用同一历史教训的论证逻辑。引用关系具体可查。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 146 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p341@0-p345@145:discern:146`
- source span: `src:c1:p345@44-p345@93`
- source span excerpt:
```text
见证了20世纪80年代住房抵押贷款的大规模损失，在今后的很长时间里，房地美也将保持严格的信贷标准。
```
- visible reaction:
```text
这里出现了一个微妙的论证结构。前文（p340）说"两家公司的历史和现实情况也截然不同"，把房地美与FSLIC的教训隔离；现在这里又说"见证了……损失，房地美也将保持严格标准"——把80年代的教训吸收进来。两次引用的教训指向不同，但房地美都被定位为能够正确应对教训的那一方。这种把外部冲击转化为自我约束力量的论证方式，逻辑上需要区分"为什么房地美不会重蹈FSLIC覆辙"和"房地美如何自我管理防止任何问题"——前者是防御性的机构对比，后者是主动性的风险规避。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 147 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p346@0-p347@122:highlight:147`
- source span: `src:c1:p347@0-p347@36`
- source span excerpt:
```text
我们公开了我们投资房地美的逻辑，这不符合伯克希尔·哈撒韦这个团体的惯例。
```
- visible reaction:
```text
这句话平静地宣告了一个反常举动。"不符合惯例"意味着这是一个经过考虑的破例，而非无心之举。语气越平实，背后的决策分量越重——不是随便说说，是专门为此写了这一段。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 148 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p346@0-p347@122:highlight:148`
- source span: `src:c1:p347@51-p347@79`
- source span excerpt:
```text
公开投资逻辑之后，我们后续的买入或卖出活动可能遭遇阻力。
```
- visible reaction:
```text
这是最直接的代价陈述。"可能遭遇阻力"——市场知道你的逻辑，就会据此反向行动。这句话同时也是一种防御性预告：如果之后房地美的操作不顺利，这个"阻力"可以作为解释。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 149 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p348@0-p349@60:highlight:149`
- source span: `src:c1:p349@30-p349@60`
- source span excerpt:
```text
我们从来不鼓励西科的股东模仿西科的投资行为，照抄西科的投资。
```
- visible reaction:
```text
这句话放在一封详细阐述投资逻辑的信里，有一种微妙的自我消解感。前面花大量篇幅讲为什么投房地美，后面立刻说"别抄"——既是一种防御性的法律语言，也是在说：我们的逻辑你们听听就好，投资是另一回事。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 150 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p354@0-p358@194:highlight:150`
- source span: `src:c1:p357@0-p357@21`
- source span excerpt:
```text
政府为储贷行业制定的这套制度本身存在死穴。
```
- visible reaction:
```text
这个判断很重要——不是市场出了错，而是制度本身的设计埋下了导火索。20年代行业危机的教训促成了这套监管框架，而这框架本身又孕育了新的危机。这种"为了防止旧问题而产生新问题"的结构，是制度设计失败的经典形态。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 151 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p354@0-p358@194:highlight:151`
- source span: `src:c1:p357@106-p357@128`
- source span excerpt:
```text
如此一来，储贷机构将腹背受敌，出现严重亏损。
```
- visible reaction:
```text
"腹背受敌"这个词把结构性矛盾说得很形象：存款利率被迫提升是前方的压力，原有固定利率贷款是后方的锁定，两头夹击，利润空间瞬间归零。这不只是经营问题，而是整个商业模式的底层假设在利率环境改变时瞬间失效。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 152 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p359@0-p362@112:highlight:152`
- source span: `src:c1:p362@13-p362@39`
- source span excerpt:
```text
这套胡萝卜加大棒的制度成为美国历史上最成功的制度之一
```
- visible reaction:
```text
这个"最成功"的定性读来有一种事后回看的反讽意味。作者显然知道结局，所以用一种看似称赞实则铺垫的语调讲述——越是赞美初期的成功，就越凸显后来崩溃的讽刺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 153 — `grounded_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p365@0-p368@132:highlight:153`
- source span: `src:c1:p367@0-p367@36`
- source span excerpt:
```text
储贷机构一心想着顺风顺水的时候怎么赚钱，毫不考虑逆水行舟的时候如何应对。
```
- visible reaction:
```text
这个"顺风/逆水"的对比把问题定性为结构性短视，不是风险管理不到位，而是对极端情形完全缺乏预案。这也呼应前文关于西科"手握大量资产"和"不意味着永远"的立场——芒格这边的选择恰好是这套逻辑的反面：备荒，而非逐利。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 明确引用前文西科'手握大量资产'和'不意味着永远'的立场，将储贷机构短视的对比锚定在已确立的芒格策略框架上，回调精准且具体。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 154 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p365@0-p368@132:highlight:154`
- source span: `src:c1:p368@71-p368@132`
- source span excerpt:
```text
货币市场基金的利率更高，还有开支票的便利，而购买国债的渠道更便捷了。储贷机构的存款非但没法增加，反而遭到了外部竞争的分流。
```
- visible reaction:
```text
储贷机构的困境不仅是内部资产质量问题，还有来自外部竞争的结构性分流。这个"腹背受敌"在利率冲击之后进一步加剧，存款端被蚕食，利润空间彻底消失。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: '腹背受敌'一词虽与reaction 151的用法相关，但此处应用较为表面，缺乏对前文具体论述的深层钩联，只是主题词重复而非论证链条的延伸。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 155 — `weak_callback` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p369@0-p372@157:highlight:155`
- source span: `src:c1:p372@70-p372@157`
- source span excerpt:
```text
于是，监管部门修改了对储贷机构投资的限制，允许它们尝试风险更高、难度更大的投资，允许它们追求更高的收益率，允许它们想方设法扩大利差。与此同时，存款保险制度却按原样保留了下来。
```
- visible reaction:
```text
"允许追求更高收益"和"存款保险原样保留"放在一起，就是道德风险的完整定义。前文说储贷机构"一心想着顺风顺水怎么赚钱"，现在政策给了它们合法的通道——但保险还挂在外面兜着底。这个组合比单纯的监管失职更危险：它是有意识的制度设计，却在结构上奖励了错误的行为。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 引用'一心想着顺风顺水怎么赚钱'是对同段落前文的表面呼应，但整体分析属于独立展开的道德风险机制论证，与更早的西科立场对照较弱。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 156 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p376@0-p379@86:highlight:156`
- source span: `src:c1:p378@52-p378@83`
- source span excerpt:
```text
房地产开发商里有很多充满野心的自大狂，也有很多信口开河的骗子。
```
- visible reaction:
```text
这个分类把开发商的道德光谱直接端出来，不是笼统说"高风险合作伙伴"，而是具体点名"自大狂"和"骗子"两种类型——前者是认知问题，后者是意图问题，两者都指向同一个结构性后果：它们许下的承诺根本不可信，但储贷机构仍然选择合作。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 157 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p376@0-p379@86:discern:157`
- source span: `src:c1:p379@65-p379@86`
- source span excerpt:
```text
无论是信用风险，还是利率风险，都同样致命。
```
- visible reaction:
```text
这句话把两种风险拉到同一平面，消除了"信用没问题就安全"的幻想。结合前文"固定利率发放长期贷款"的做法——表面合规、短期业绩好看，但结构性地把利率风险埋进了资产端。和前文西科"手握大量资产，不意味着永远不动"的逻辑完全相反：储贷机构不是没有资产，而是主动把未来的致命风险装进了资产里。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 同时回调'手握大量资产，不意味着永远不动'和'固定利率发放长期贷款'两个前文论点，将储贷机构的结构性失误与西科的主动守势策略形成清晰对比，论证逻辑连贯。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 158 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p381@0-p384@143:retrospect:158`
- source span: `src:c1:p382@41-p382@104`
- source span excerpt:
```text
在新制度之下，品行不端的人会做出不良行为。受新制度的影响，有些原本奉公守法的储贷机构，因为陷入了经营困境，现在也会钻法律漏洞。
```
- visible reaction:
```text
这句话用了一个"受新制度影响"的结构，暗示问题出在制度而非个人。它把从"品行不端"到"奉公守法也会钻漏洞"串成一条连续谱——不是坏人在捣乱，是制度改变了博弈的收益结构，把原本守规矩的人也拉进了这个游戏。这种"制度污染好人"的逻辑，比单纯的"坏人利用漏洞"更难以归咎：没有人觉得自己是坏人，但每个人都在理性地回应新激励。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p369@0-p372@157:highlight:155"]}`
  - judge reason: 通过prior_link明确回调reaction 155的道德风险论述，并将其延伸为从'品行不端'到'奉公守法也钻漏洞'的连续谱，论证层次递进有据。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 159 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p381@0-p384@143:discern:159`
- source span: `src:c1:p382@104-p382@198`
- source span excerpt:
```text
对于濒临破产的储贷机构而言，新制度给了它们一个翻身的机会。自己的钱已经赔光了，没关系，可以拿国家的钱豪赌一把，赌利率、赌将来能赚钱。赢了，还有机会活下来。第一次输了，没关系，输后加倍下注。
```
- visible reaction:
```text
这段描述把"破产边缘的机构用国家资金豪赌"的机制拆得很细：不是铤而走险的意外选择，而是新制度提供的合法选项。"赌赢了活，赌输了反正不是自己的钱"——这种损失不对称结构，正是道德风险的核心特征。从西科的立场看，这种结构性激励是外部的、不可控的，和它"主动持有现金等待好机会"的策略正好相反：西科选择不动，是因为没有足够确定性的标的；而储贷机构疯狂下注，是因为新制度把不确定性变成了对自己有利的选项——赢了是我的，输了是你的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: 回调'赌赢了活，赌输了反正不是自己的钱'这一前文提炼的道德风险核心特征，并将其与西科'主动持有现金等待好机会'的策略形成结构性对置，论证支撑充分。
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 160 — `weak_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p385@0-p387@95:discern:160`
- source span: `src:c1:p387@40-p387@95`
- source span excerpt:
```text
具体而言，只要高管买入垃圾债，公司就会授予他特权，允许他以储贷机构享有的优惠价，购买垃圾债发行机构的其他产品。
```
- visible reaction:
```text
这条激励机制的设计逻辑很清晰：绕过年薪上限，用垃圾债购买特权来补足高管的补偿。它的实质是把冒险行为本身变成高管的个人收益来源——买得越多，福利越好。这和前面"赌赢了活，赌输了反正不是自己的钱"是一脉相承的激励结构，只是这里展示了更具体的兑现方式。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `weak_callback`
  - judge reason: 虽引用'赌赢了活，赌输了反正不是自己的钱'，但此处分析重点落在高管激励兑现机制的细节（垃圾债购买特权），与前文西科立场对照较远，属于自成体系的延伸解读而非清晰的论点回调。
  - reviewer interpretation: callback-like but weak; useful diagnostic signal, not strong callback evidence.

### Reaction 161 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p388@0-p389@95:highlight:161`
- source span: `src:c1:p389@17-p389@44`
- source span excerpt:
```text
银行的监管体系非常严格，对银行购买垃圾债的态度很严厉。
```
- visible reaction:
```text
这句话解释了为什么风险最终落在监管更松的主体上——银行被管住了，储贷机构就成了承接垃圾债的出口。这和前文储贷机构"拿国家的钱豪赌"的激励结构是同一个故事的两个侧面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 162 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p388@0-p389@95:highlight:162`
- source span: `src:c1:p389@44-p389@95`
- source span excerpt:
```text
近年来，发行垃圾债主要有两种情况：一种是筹集资金进行杠杆收购；另一种是筹集资金进行重组，抵制恶意收购。
```
- visible reaction:
```text
两种场景恰好对应两种资本逻辑：进攻性的杠杆收购和防御性的反收购重组。两者都是大资金博弈的工具，区别在于谁在用、用来对付谁。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 163 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p390@0-p390@135:highlight:163`
- source span: `src:c1:p390@26-p390@68`
- source span excerpt:
```text
银行的存款由监管机构提供保险，因此银行购买公司债必须保证安全，不触犯监管机构的红线。
```
- visible reaction:
```text
监管机构的保险本意是保护储户，但在公司债市场上，它实际上变成了一个准入过滤器——把最安全的资产划给银行，把剩下的逼向监管更松的主体。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 164 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p390@0-p390@135:highlight:164`
- source span: `src:c1:p390@90-p390@135`
- source span excerpt:
```text
优先级债券已经被银行买走了，留给储贷机构的只有偿还顺序靠后的垃圾债。垃圾债是最劣质的贷款。
```
- visible reaction:
```text
最后这句定义"垃圾债是最劣质的贷款"，不是闲笔，而是一个结构性结论：经过监管筛选之后，储贷机构最终承接的，正好是风险最高、信用最差的那一层。前文的高管激励结构和这条监管路径，在"垃圾债"这个节点上完成了合流。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 165 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p391@0-p392@131:highlight:165`
- source span: `src:c1:p392@0-p392@29`
- source span excerpt:
```text
储贷机构监管失灵，一个很重要的原因在于，监管部门各自为政。
```
- visible reaction:
```text
"各自为政"——不是能力问题，而是结构问题。这里说的不是监管人员失职，而是制度设计本身造成的责任真空。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 166 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p396@0-p397@46:highlight:166`
- source span: `src:c1:p396@111-p396@144`
- source span excerpt:
```text
结果经营保守的储贷机构，被迫向它们看齐，不得不承受更高的存款成本。
```
- visible reaction:
```text
"被迫"这个词用得准确——不是主动冒进，而是竞争压力下的别无选择。这和前文高管激励的主动冒险形成对比：这里的好机构是被动的受害者。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 167 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p396@0-p397@46:highlight:167`
- source span: `src:c1:p397@0-p397@46`
- source span excerpt:
```text
存款成本上升了，为了覆盖成本，原本保守的储贷机构别无选择，只能考虑风险更高、收益更高的资产。
```
- visible reaction:
```text
这条是本单元的核心结论：成本压力→被迫风险偏好上升。逻辑链完整，且和前文"各自为政"的监管真空形成宏观-微观的闭合。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 168 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p398@0-p400@103:highlight:168`
- source span: `src:c1:p400@25-p400@103`
- source span excerpt:
```text
监管部门为储贷行业提供存款保险、为困难企业提供很长的缓冲期、储贷机构的利率不受限制、资产配置不受限制，这些是既定政策，难以改变。储贷行业的问题也许根本无解。
```
- visible reaction:
```text
"既定政策，难以改变"——和前文"各自为政"的诊断形成结构层面的呼应：监管失灵是制度碎片化导致的，而行业困境是政策组合锁死的。问题不是某个人做错了什么，而是系统本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 169 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p398@0-p400@103:highlight:169`
- source span: `src:c1:p400@89-p400@103`
- source span excerpt:
```text
储贷行业的问题也许根本无解。
```
- visible reaction:
```text
"也许根本无解"——这个措辞值得注意。不是"无法解决"，而是"也许""根本"——带着一种对系统复杂性的诚实承认，同时暗示这些政策本身是权衡的产物。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 170 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p401@0-p403@23:retrospect:170`
- source span: `src:c1:p401@17-p401@72`
- source span excerpt:
```text
在复杂的体系中，牵一发而动全身，本来只想提高一个变量的作用，却往往导致其他变量的作用降低，产生意料之外的后果。
```
- visible reaction:
```text
这是本单元新增的元层面：复杂性理论本身作为诊断工具。前文说的是"既定政策难以改变"和"成本压力迫不得已"，这里转向的是政策干预行为的内在复杂性——即使政策目标单一、出发点合理，系统响应也可能反噬。这个框架比"政策错了"更深一层。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p398@0-p400@103:highlight:169"]}`
  - judge reason: Explicitly references reaction 169 (highlight:169) via prior_link, extending its '也许根本无解' into a complexity-theory framing about policy intervention dynamics.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 171 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p404@0-p404@125:highlight:171`
- source span: `src:c1:p404@11-p404@66`
- source span excerpt:
```text
所有经营稳健、业务清晰、管理良好的储贷机构，它们谨慎地防范利率变化风险和信用损失风险，结果却根本无法实现盈利。
```
- visible reaction:
```text
"结果却根本无法实现盈利"——这句话把悖论说尽了。不是"很难"，不是"暂时"，而是"根本"。稳健经营在这个结构里不是优势，而是亏损的来源。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 172 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p409@0-p411@42:highlight:172`
- source span: `src:c1:p409@0-p409@17`
- source span excerpt:
```text
我们认为，上述逻辑同样适用于银行。
```
- visible reaction:
```text
"同样适用"四个字把前文整个储贷危机的分析框架升格为一般性理论——存款保险与利率管制解除的组合在金融系统中具有普遍性，不只是储贷行业特例。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 173 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p409@0-p411@42:highlight:173`
- source span: `src:c1:p411@0-p411@42`
- source span excerpt:
```text
第二，银行业的监管机构实施了更严格的监管措施，银行的国内资产质量受到了更严格的控制。
```
- visible reaction:
```text
这条补充理由值得细想——"更严格的监管"是相对于储贷行业的对比，还是绝对意义上的严格？如果是前者，那么储贷监管的宽松程度就更是制度性失职，而非简单的技术性疏漏。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 174 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p412@0-p412@136:highlight:174`
- source span: `src:c1:p412@51-p412@101`
- source span excerpt:
```text
效仿证券交易所和商品交易所的清算机制，只要银行的亏损触及资本金，不等它出现大量损失，就立即暂时关闭。
```
- visible reaction:
```text
这个类比把监管问题从"事后处置"拉回到"事前威慑"。交易所清算的逻辑是触底即平，不拖；转移到银行监管上就是触线即关，不等。威慑力来自不可拖延，而非仅仅是惩罚的严厉程度。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 175 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p412@0-p412@136:highlight:175`
- source span: `src:c1:p412@101-p412@116`
- source span excerpt:
```text
如此一来，看哪家银行还敢冒险？
```
- visible reaction:
```text
这是整段的收尾句，用反问语气强化"立即关闭"机制的威慑逻辑，语气口语但论证精准。威慑的有效性在于预期被改变，而不仅仅是结果被惩罚。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 176 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p413@0-p413@98:highlight:176`
- source span: `src:c1:p413@27-p413@46`
- source span excerpt:
```text
这种风险是所有银行同时触犯了一种风险。
```
- visible reaction:
```text
这里精确地区分了一种特殊的系统性风险类别——不是某一家银行单独冒险，而是整个行业步调一致地越界。这种"同步越界"让监管从"管个体"变成了"管集体"，而集体行为天然抗拒个体问责。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 177 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p413@0-p413@98:highlight:177`
- source span: `src:c1:p413@77-p413@98`
- source span excerpt:
```text
法不责众，难不成监管机构把所有银行都关了？
```
- visible reaction:
```text
这句反问把"法不责众"的俗语翻译成了监管逻辑的死穴。"立即关闭"机制的必要性在这里再次被印证：正因为知道集体违规时任何事后惩罚都会不了了之，所以威慑必须设计成触线即发、不可拖延的自动机制，让"大家都犯"这件事本身变成不可能。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 178 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p414@0-p414@131:retrospect:178`
- source span: `src:c1:p414@83-p414@131`
- source span excerpt:
```text
国内贷款质量出了问题，银行监管机构很严格。国外贷款质量出了更大的问题，银行监管机构却没那么严格。
```
- visible reaction:
```text
这个"更大问题反而更宽松"的悖论不是监管失职，而是结构性制约：执法的边界受限于执法对象的存在本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p413@0-p413@98:highlight:177"]}`
  - judge reason: Prior_link explicitly references reaction 177 (highlight:177), building on its '法不责众'/enforcement paradox to explain the 'larger problem gets looser regulation' structural constraint.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 179 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p415@0-p416@88:retrospect:179`
- source span: `src:c1:p416@0-p416@88`
- source span excerpt:
```text
当储贷行业的监管机构放松管制之时，恰逢全国范围内投机钻营、坑蒙拐骗之风盛行。在这样的大环境之中，监管机构的新制度为投机倒把的人提供了土壤，让储贷机构成为他们牟取不义之财的工具。
```
- visible reaction:
```text
"放松管制"与"投机盛行"在时间上的巧合被说成因果关联——不是监管失职单方面导致灾难，而是制度改变恰好撞上了最需要被制度约束的那股力量。"提供了土壤"这个表述很关键：不是投机分子自己挖好了坑，而是新制度整出来的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p413@0-p413@98:highlight:176", "reaction:rx:Full_Content:src:c1:p413@0-p413@98:highlight:177", "reaction:rx:Full_Content:src:c1:p414@0-p414@131:retrospect:178"]}`
  - judge reason: Prior_link references reactions 176, 177, and 178, connecting deregulation timing to the structural soil that enabled speculation—directly grounded in the synchronized-transgression analysis.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 180 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p417@0-p419@142:highlight:180`
- source span: `src:c1:p419@40-p419@61`
- source span excerpt:
```text
陷入了20世纪30年代以来最严重的经济衰退
```
- visible reaction:
```text
这个"30年代以来最严重"的定调很关键。它不是泛泛地说"严重"，而是用大萧条作为历史坐标，把读者锚定在"系统性地量级"上——说明这不是周期性的波动，而是结构性塌陷。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 181 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p417@0-p419@142:highlight:181`
- source span: `src:c1:p419@90-p419@142`
- source span excerpt:
```text
通货膨胀、存在漏洞的行业制度已经让联邦储蓄贷款保险公司叫苦不迭，油价大跌导致的逾期潮又带来了巨大的损失。
```
- visible reaction:
```text
"已经……又"这个句式标记的是叠加逻辑：前两个压力（通胀+制度漏洞）已经是既有负担，逾期潮作为第三重再压上来——不是替代，是累加。这和前面"新制度起了助纣为虐的作用"形成递进：制度漏洞本身就在制造损失，再叠加外部冲击，损失被放大。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 182 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p420@0-p421@142:highlight:182`
- source span: `src:c1:p421@53-p421@118`
- source span excerpt:
```text
会计师是储贷机构聘请的。在遵守职业准则的同时，他们也要效忠于客户。自然而然地，从客户的利益出发，他们要让联邦储蓄贷款保险公司活着。
```
- visible reaction:
```text
"自然而然地"这个词标记的是一种结构必然，而非偶然过失。支付链条决定了忠诚方向，职业准则与客户利益之间的张力最终以"客户利益优先"收场——不是因为会计师不讲道德，而是制度设计让他们没有别的选择。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 183 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p420@0-p421@142:highlight:183`
- source span: `src:c1:p421@118-p421@142`
- source span excerpt:
```text
非等到它病入膏肓、无可救药的地步，才肯宣判死刑。
```
- visible reaction:
```text
这句话与前面关于"监管人员和会计师如果能早一些采取行动"形成呼应——延误诊断不是能力问题，而是立场问题。诊断本身就被利益关系污染了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 184 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p422@0-p426@152:highlight:184`
- source span: `src:c1:p425@0-p425@21`
- source span excerpt:
```text
幕后真凶——法律制定者和自私自利的行业高管
```
- visible reaction:
```text
标题本身就是一种定论宣判。不是市场失灵，不是监管人员失职，而是法律制定者与行业高管联手制造的困境。这个"幕后"与"真凶"的措辞，在行文上是明确的道德判断。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 185 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p422@0-p426@152:highlight:185`
- source span: `src:c1:p426@107-p426@152`
- source span excerpt:
```text
他们的工作环境像野战医院一样艰难，还没有新鲜血浆可以输送给伤员，我们不能对他们有太多苛求。
```
- visible reaction:
```text
结尾这句"不能有太多苛求"是一个明确的免责声明，同时把责任方向彻底翻转——不是因为他们做不好，而是因为条件不允许。对比前文对国会"逃避"的直接批评，这个结尾是整段的逻辑落点：失败是可以预见的，但责任不在执行层。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 186 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p427@0-p430@79:highlight:186`
- source span: `src:c1:p430@53-p430@79`
- source span excerpt:
```text
如果联盟仍然坚持不负责任的行为，互助储蓄将退出联盟。
```
- visible reaction:
```text
在悔过之后加了一个明确的行为底线：有条件地退出。这个威胁既是诚意的证明，也是一个结构性声明——这个联盟已经不值得信任。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 187 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p442@0-p444@82:highlight:187`
- source span: `src:c1:p444@45-p444@82`
- source span excerpt:
```text
要成功救助联邦储蓄贷款保险公司，1989年的新法律中必须至少包含这些内容。
```
- visible reaction:
```text
"至少包含"这个措辞把一份政策清单直接升级为最低门槛声明——不是建议，不是选项，而是必要条件。在行文上，这句话关闭了谈判空间，同时强化了前文所有条目的紧迫性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 188 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p445@0-p446@146:highlight:188`
- source span: `src:c1:p445@0-p445@7`
- source span excerpt:
```text
难以把握的分寸
```
- visible reaction:
```text
这个标题本身就是一个判断：不是"错误的政策"，不是"不可能的任务"，而是"分寸难以把握"——暗示正确答案存在，只是很难找到。这比直接批评更耐人寻味。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 189 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p445@0-p446@146:highlight:189`
- source span: `src:c1:p446@88-p446@119`
- source span excerpt:
```text
新政策执行后，联邦储蓄贷款保险公司能得到多少资金，这是未知之数
```
- visible reaction:
```text
"未知之数"四个字比"不确定"更彻底——不是概率分布未知，而是连量级都无法预估。这个承认在枚举结构中插入了一个断裂，提醒读者所有推演都建立在不稳固的地基上。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 190 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p452@0-p456@81:retrospect:190`
- source span: `src:c1:p453@0-p453@66`
- source span excerpt:
```text
目前的政治决策，大多数是拍脑门，很少经过深思熟虑。对于1989年的新法律，我们没什么信心，联邦储蓄贷款保险公司将来还是可能陷入危机。
```
- visible reaction:
```text
从"未知之数"推进到"拍脑门"——不确定性从概率问题变成了过程问题。不是结果看不清，而是决策方式本身令人失去信任。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p445@0-p446@146:highlight:189"]}`
  - judge reason: Prior_link explicitly references reaction 189 (highlight:189), connecting '未知之数' epistemic unknowability to the more damning 'decision process by gut feeling' critique.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 191 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p452@0-p456@81:highlight:191`
- source span: `src:c1:p454@0-p454@16`
- source span excerpt:
```text
法律制定者一错再错，让人难以信任
```
- visible reaction:
```text
标题本身就是判断。"一错再错"把多个历史错误串联成一条轨迹，暗示这不是偶发失误，而是系统性的失信。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 192 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p452@0-p456@81:highlight:192`
- source span: `src:c1:p456@22-p456@81`
- source span excerpt:
```text
当年的制度设计者深知，在经营无差别普通商品的行业中，竞争极其激烈。储贷行业经营的是货币，而货币完全是一种无差别的商品。
```
- visible reaction:
```text
悖论所在：设计者明知货币是无差别商品，却用保护性制度来规避无差别竞争的后果。这个内在矛盾是整个储贷危机更深层的制度根源。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 193 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p457@0-p458@207:highlight:193`
- source span: `src:c1:p458@169-p458@207`
- source span excerpt:
```text
负债端的利率已经放开了很长时间，他们仍然不允许资产端的住房贷款采用浮动利率。
```
- visible reaction:
```text
这才是真正的基础设施断裂：一边已经利率市场化了，一边还卡着浮动利率。负债成本可以随市场波动，资产收益却锁定——这个错位本身就是一颗定时炸弹。立法者持续无视它，这才是"失职"的核心。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 194 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p459@0-p460@91:highlight:194`
- source span: `src:c1:p460@17-p460@53`
- source span excerpt:
```text
立法机构一拖再拖、遮遮掩掩，最终导致问题愈演愈烈，损失高达100亿美元。
```
- visible reaction:
```text
「一拖再拖、遮遮掩掩」把立法机构的失职具体化了——不是没有行动，而是行动迟缓且不透明，任由问题发酵。100亿美元的数字让这个「愈演愈烈」的轨迹有了重量。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 195 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p459@0-p460@91:highlight:195`
- source span: `src:c1:p460@53-p460@91`
- source span excerpt:
```text
现在，危机爆发之后，我们听到的却是不绝于耳的口水战，争抢着把责任推卸给别人。
```
- visible reaction:
```text
从「一拖再拖」到「争抢着推卸」：行为模式完全一致——始终不是面对，而是回避。这一句把「一错再错」的题旨从制度层面延伸到了政治文化层面，危机后第一反应不是补救而是甩锅。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 196 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p461@0-p464@27:highlight:196`
- source span: `src:c1:p463@3-p463@43`
- source span excerpt:
```text
私人养老金体系是一个巨大的存款池，这部分资金享受税收优惠，承受利率变化的能力强。
```
- visible reaction:
```text
「巨大的存款池」这个定位很关键——它不是在讨论个人储蓄，而是在识别一个具有系统性规模的长钱池。这个池子的存在本身就是一种结构性资源，问题在于它流向了高风险资产而不是它本来应该服务的长期稳定投资。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 197 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p461@0-p464@27:highlight:197`
- source span: `src:c1:p463@79-p463@113`
- source span excerpt:
```text
可以考虑从私人养老金体系中拿出一定比例的资金，用于投资住房贷款市场。
```
- visible reaction:
```text
这里给出了具体机制：不是新增资金，而是重新定向。把原本流向高换手股票的资金改道进入住房贷款——一端是稳定的长期资产，另一端是稳定的长期资本。这个逻辑和芒格一贯的「用好资产匹配好去处」思路一致，而不是靠金融工程弥补错配。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 198 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p465@0-p465@99:highlight:198`
- source span: `src:c1:p465@50-p465@72`
- source span excerpt:
```text
这样的措施毫无力度，最终只能付出更大的代价。
```
- visible reaction:
```text
「毫无力度」的评价很直接，但关键是后半句——它不只是说无效，而是说这种无力的应对会让未来的代价更大。这比单纯的批评更重：不仅是现在输了，而且是主动选择了在将来输更多。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 199 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p466@0-p468@173:highlight:199`
- source span: `src:c1:p468@119-p468@173`
- source span excerpt:
```text
在各种因素的交织中，希望建立一套长期稳定运行的储贷制度，并为储贷机构提供存款保险，这几乎是不可能完成的任务。
```
- visible reaction:
```text
这里的关键不在于"危机难解决"，而在于"稳定储贷制度"和"存款保险"这两个目标的内在矛盾——存款保险本身会激励风险行为，从而破坏储贷制度的稳定。芒格把这个问题说成是结构性不可能，而不是技术性不足。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 200 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p466@0-p468@173:highlight:200`
- source span: `src:c1:p467@20-p467@81`
- source span excerpt:
```text
在合奏效应（lollapa looza）的影响下，储贷行业陷入的危机错综复杂，我们现有的法律制定者没有化解这个危机的能力。
```
- visible reaction:
```text
"合奏效应"这个词点出了多因素同时共振的复杂性——不是单因单果，而是多个机制同时放大彼此。这和芒格在别处用"lollapalooza effect"解释连锁反应的逻辑一致。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 201 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p469@0-p470@186:highlight:201`
- source span: `src:c1:p470@24-p470@76`
- source span excerpt:
```text
所有人类的大脑天生存在缺陷。在面对复杂问题的时候，我们的大脑总是难以破旧立新，难以从过去的老路中走出来。
```
- visible reaction:
```text
这个陈述不是比喻，而是事实性判断。芒格用它的目的是把储贷危机的立法困境从'人的问题'升格为'物种问题'——不是这届议员不行，而是任何时代的立法者面对这种多因素共振的复杂局面都注定受限。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 202 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p469@0-p470@186:highlight:202`
- source span: `src:c1:p470@149-p470@186`
- source span excerpt:
```text
只有老一代退出历史舞台，新一代不受旧观念的束缚，正确的新理念才会得到普及。
```
- visible reaction:
```text
普朗克这段话的适用范围远超储贷危机。它是芒格式的'代际认知更替'模型：正确的理念不是靠说服老人来普及，而是靠时间窗口的自然替换。这与前文关于'合奏效应'使危机超出当下解决能力的判断形成逻辑闭环——问题的答案在时间，而非法案。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 203 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p471@0-p471@114:highlight:203`
- source span: `src:c1:p471@30-p471@51`
- source span excerpt:
```text
我们说它是个难题，也许是我们在为自己辩护。
```
- visible reaction:
```text
这句话把"难题"定性本身变成了反思对象。不是讨论危机本身难不难，而是追溯"我们称它为难"这个命名行为背后的动机——自我开脱。这比单纯承认困难要更深一层。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 204 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p471@0-p471@114:highlight:204`
- source span: `src:c1:p471@87-p471@114`
- source span excerpt:
```text
如果不是难题，如果破旧立新很容易，我们的亏损如何解释？
```
- visible reaction:
```text
这个反问把逻辑逼到死角：要么承认危机确实难以克服，要么承认我们本该避免损失却没能做到。没有中间地带。这个张力恰好是"难题框架作为自我辩护"的核心证据。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 205 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p472@0-p473@107:highlight:205`
- source span: `src:c1:p473@43-p473@107`
- source span excerpt:
```text
导致其他储贷机构破产的种种行为，互助储蓄一种都没有沾边，然而互助储蓄同样需要缴纳更高的存款保险费，同样会在投资方面受到诸多限制。
```
- visible reaction:
```text
这个"然而"是一个精确的逻辑陷阱：无辜本身不是豁免的理由。芒格没有愤怒，只是平静地陈述事实，但这恰恰让这个结构性不公更加刺眼。它说明危机管理机制对"行业身份"的惩罚超越了对"个体行为"的甄别。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 206 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p474@0-p477@36:discern:206`
- source span: `src:c1:p477@0-p477@36`
- source span excerpt:
```text
（3）立法机构因危机爆发而对储贷行业采取惩罚措施，制定了有害无益的法律。
```
- visible reaction:
```text
"因危机爆发而采取惩罚措施"——这个表述把动机本身暴露了：不是因为查清了谁有罪，而是因为恐慌，所以打击整个行业。这比"制定有害法律"更进一步，不仅揭示结果有害，还揭示了驱动这种有害结果的情感机制。这与前文"互助储蓄一种行为都没沾边，却同样承担后果"的逻辑直接呼应：结构性的无辜，并不能换来结构性的豁免。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 207 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p478@0-p481@72:discern:207`
- source span: `src:c1:p479@0-p479@26`
- source span excerpt:
```text
总之，除了对房地美的投资，互助储蓄没什么光明的前景。
```
- visible reaction:
```text
这个「总之」语气很平，但结论很冷。没有愤怒，没有哀叹，只有判断。它将整个互助储蓄的存续处境压缩为一句话：唯一的光亮来自房地美——那是一笔外部投资，不是自身业务的复兴。这个判断与之前段落建立的结构性困境完全一致：无辜不能换来豁免，守正不能换来出路。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 208 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p490@0-p490@70:retrospect:208`
- source span: `src:c1:p490@26-p490@70`
- source span excerpt:
```text
我们认为，联盟目前的游说行为存在严重错误，让我们深感羞愧，因此我们不愿继续留在联盟之中。
```
- visible reaction:
```text
"羞愧"这个词用得很重。不是为自己的处境哀叹，而是因为联盟的行为让自己感到羞耻——这说明他们仍在以行业标准衡量自身，即使这个"行业身份"本身正在给他们带来灾难。这种在逆境中仍然保持道德判断的姿态，与前文"守正却无出路"的困境形成了一种安静的对抗：即使结构压死了他们，他们也不愿与导致这种结构的东西同流。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p472@0-p473@107:highlight:205", "reaction:rx:Full_Content:src:c1:p478@0-p481@72:discern:207"]}`
  - judge reason: Has explicit prior_link ref_ids pointing to reactions 205 and 207. Content about '羞愧' directly addresses the alliance's behavior discussed in those earlier reactions, connecting moral stance to the '守正却无出路' situation with specific grounding.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 209 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p491@0-p491@187:discern:209`
- source span: `src:c1:p491@85-p491@127`
- source span excerpt:
```text
联盟一直通过政治游说，庇护一小撮坑蒙拐骗、经营不善的储贷机构，阻挠监管机构的正常执法
```
- visible reaction:
```text
这个句子的结构很有意思："庇护"+"阻挠"。庇护的是一小撮坏机构，阻挠的是监管执法。这说明联盟的功能不是代表行业，而是代表行业中不该被保护的那部分。这与前文"守正却无出路"的逻辑形成了一种结构性呼应——联盟庇护坏分子，正当机构却要跟着承担后果。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 210 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p491@0-p491@187:highlight:210`
- source span: `src:c1:p491@150-p491@186`
- source span excerpt:
```text
让储贷机构有空子可钻，实际资本充足率根本不达标，无法为储户的存款提供保障
```
- visible reaction:
```text
三句话形成了一条完整的因果链：宽松会计→空子可钻→资本不达标→无法保障存款。这是把联盟的第二条罪状解释得非常清晰的一组递进。它不仅仅是"政策有问题"，而是"这个政策问题导致了实质性的风险暴露"。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 211 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p492@0-p496@402:highlight:211`
- source span: `src:c1:p496@200-p496@245`
- source span excerpt:
```text
如果行业协会只顾一己之私利，那么它们的影响力是国家的心腹大患。储贷行业的危机就是前车之鉴。
```
- visible reaction:
```text
这里说出了行业协会影响力问题的核心：不是影响力本身有错，而是"只顾一己之私"这个前提让影响力变成了结构性威胁。把联盟定性为"心腹大患"，语气很重，但落脚点在前车之鉴——强调的是这种模式会重复。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 212 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p497@0-p501@314:highlight:212`
- source span: `src:c1:p501@225-p501@313`
- source span excerpt:
```text
皇天不负有心人，我们终于实现了水通、电通、路通和场地平整，正式的建筑工作已经展开。我们将建造32栋房屋。无论是开阔气派的空间，还是别具一格的景观，整个项目在方方面面都堪称一流。
```
- visible reaction:
```text
这段股东信的语气很有意思——不是业绩汇报，而是"皇天不负有心人"。芒格用这种私人化的感慨来描述一笔被迫接收的抵押资产慢慢变成优质项目的过程，13年的等待最后落在"堪称一流"四个字上。这和他"攥在手里，不意味着永远"的说法形成了一种性格上的呼应：真正有价值的资产，时间是朋友。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 213 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p512@0-p512@253:highlight:213`
- source span: `src:c1:p512@193-p512@253`
- source span excerpt:
```text
由于巴芒在风险套利方面乃是师从本·格雷厄姆（Benjamin Graham），芒格于是也分享了格雷厄姆教他们的重要几课。
```
- visible reaction:
```text
这条师承线把垃圾债危机和风险套利方法从投资工具层面拉到了方法论层面——不是说"1989年发生了什么"，而是说"我们从格雷厄姆那里学到了什么框架，能让我们理解这类事件"。这和前文反复出现的"前车之鉴"思路是同一个逻辑层次。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 214 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p513@0-p515@126:highlight:214`
- source span: `src:c1:p515@13-p515@51`
- source span excerpt:
```text
有的储贷机构首席执行官动用100万美元的公款购买名画，挂在自己的客厅里欣赏。
```
- visible reaction:
```text
"挂在自己的客厅里欣赏"这个细节把挪用公款的行为从财务数字落实成了生活场景——不是"有违规行为"，而是"我买画，挂我家"。这种叙事把管理层的自我中心和短视推到了读者可以直接感受的层面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 215 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p513@0-p515@126:highlight:215`
- source span: `src:c1:p515@78-p515@126`
- source span excerpt:
```text
有的储贷机构，前段时间还在电视上播放宣传片，突然之间就破产了。储贷行业的公众形象怎能不一落千丈？
```
- visible reaction:
```text
从电视宣传片到破产的反差速度，配合反问句的确认语气，构成了一种辛辣的讽刺。这种叙事节奏和"前车之鉴"的前文呼应：错的不是复杂的金融工具，而是做出决策的人。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 216 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p516@0-p520@82:highlight:216`
- source span: `src:c1:p519@0-p519@52`
- source span excerpt:
```text
资本主义不是万能的。资本主义制度是一套理想的制度，但它也有解决不了的问题，有时候需要采用少许的社会主义。
```
- visible reaction:
```text
这个"少许的社会主义"的说法在这里语境里指的其实是互助结构——不是税收或福利政策层面的社会主义，而是所有权结构层面的。State Farm作为"行业翘楚"的事实让这个论点有了实证支点，而不只是哲学主张。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 217 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p521@0-p525@90:highlight:217`
- source span: `src:c1:p524@0-p524@21`
- source span excerpt:
```text
发放贷款时只考虑短期业绩，无异于饮鸩止渴。
```
- visible reaction:
```text
"饮鸩止渴"这个比喻把短视行为的后果推到了极致：明知是毒酒，还是一口一口地喝——不是因为蠢，而是因为短期业绩压力下，不喝马上就死，喝了将来死。这是整个储贷危机的行为逻辑的核心隐喻。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 218 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p521@0-p525@90:discern:218`
- source span: `src:c1:p522@5-p522@61`
- source span excerpt:
```text
不可能一方面由政府提供信用背书，另一方面又不限制存款利率。这样的制度难以长久，因为它会驱使银行和储贷机构去冒险。
```
- visible reaction:
```text
这里把"政府背书 + 利率自由"的结构性矛盾直接点出来了：不是 отдельные机构"做错了"，而是制度设计本身在激励冒险。与前文提到的"少许的社会主义"（互助结构）形成明确对立——芒格认为互助结构才能从根本上解决这个问题，但在里根—撒切尔时代这种主张没有政治可行性。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 219 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p529@0-p529@160:retrospect:219`
- source span: `src:c1:p529@127-p529@160`
- source span excerpt:
```text
储贷机构像染上了毒瘾一样，只能不断地继续吸食，根本顾不上考虑成本。
```
- visible reaction:
```text
这里把"饮鸩止渴"（前文的比喻）彻底落实为成瘾行为——不是喝一次毒酒就死，而是必须一口接一口地吸，明知有害、无法停下。前文点出了结构性矛盾，这里则揭示了它的行为后果。"顾不上考虑成本"是关键：不是不知道有风险，而是激励机制把风险评估彻底屏蔽了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p521@0-p525@90:highlight:217"], "note": "推进了饮鸩止渴的机制：从隐喻落实为成瘾循环"}`
  - judge reason: Has explicit prior_link ref_id to reaction 217, with note stating it '推进了饮鸩止渴的机制：从隐喻落实为成瘾循环'. The content explicitly advances the earlier metaphor into addiction behavior with specific grounding.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 220 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p529@0-p529@160:highlight:220`
- source span: `src:c1:p529@73-p529@124`
- source span excerpt:
```text
到了第二年，为了让利润继续增长，为了让总裁和董事长的薪酬继续提高，就要继续冒险，把更多的收入提前入账。
```
- visible reaction:
```text
escalation（升级）机制在这里变得清晰：第二年要超越第一年，就必须比第一年更冒险、吃更多的未来收入。不是原地踏步，而是必须加码。利润增长和高管薪酬挂钩形成双重压力，两个目标叠加让冒险的幅度只能越来越大，弹性空间越来越小，直到崩溃。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 221 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p530@0-p530@57:highlight:221`
- source span: `src:c1:p530@30-p530@57`
- source span excerpt:
```text
然而，在我看来，我们做得还远远不够，制度还是不够严格。
```
- visible reaction:
```text
这个"然而"从承认改善转向坚持批判，把评价从"有进步"拉向"进步不够"。语气很直接，没有留缓冲余地——说明芒格对制度改革力度的判断是相当坚定的，不因为危机已经过去就放松批评。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 222 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p532@0-p535@133:highlight:222`
- source span: `src:c1:p534@0-p534@65`
- source span excerpt:
```text
银行买入了隐藏在复杂策略之下的高风险产品，在期货市场对冲分成多个层级的住房抵押贷款证券，还振振有词地宣称自己在谨慎地防范利率风险。
```
- visible reaction:
```text
"隐藏"这个词点出了整个机制的核心——复杂性不是为了降低风险，而是为了掩盖风险。投行提供的那种"看不懂才安全"的逻辑，本质上是一种信用转移：把风险包装成你无力识别的形式，然后让你的无能为力变成他们的免责证据。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 223 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p532@0-p535@133:highlight:223`
- source span: `src:c1:p535@124-p535@133`
- source span excerpt:
```text
我们怎么就不信呢？
```
- visible reaction:
```text
这句反问不是真正的疑问，而是芒格式的判断姿态——"我们不信"已经是一个立场声明，不需要进一步论证。它暗示的是：恰恰因为我们无法确证这东西是假的，所以我们不碰。这和"清楚自己能力的大小"是一脉相承的认知纪律。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 224 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p538@0-p538@80:discern:224`
- source span: `src:c1:p538@19-p538@80`
- source span excerpt:
```text
请你们发表一下高见。如果一家银行买入了第四层级的住房抵押贷款证券并通过期货市场进行了所谓的对冲，你们能判断出其中的风险吗？
```
- visible reaction:
```text
两句之间形成一个内在的反讽：邀请监管者发表意见，紧接着抛出一个他们很可能无法回答的问题。这个结构本身就是芒格式的质疑方式——不是否定监管者，而是通过"请你们说两句"这个动作本身，暴露出"你们其实说不清楚"的事实。高见变成了一个反讽的前提，而非真正的请求。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 225 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p539@0-p543@106:highlight:225`
- source span: `src:c1:p539@24-p539@69`
- source span excerpt:
```text
在检查时，我们看到的信息都是投行提供的，而投行是证券化产品的卖方，它们在里面有自己的利益。
```
- visible reaction:
```text
这句话点出了监管的结构性悖论：监管依赖的信息来源本身带有利益立场，而这种利益立场恰恰是监管对象想要隐藏的东西。信息提供者是卖方，卖方想成交——这个链条本身就是风险所在。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 226 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p539@0-p543@106:highlight:226`
- source span: `src:c1:p543@84-p543@106`
- source span excerpt:
```text
这么多文件，连律师都看不过来，更别提外行了。
```
- visible reaction:
```text
这个细节和前面"隐藏"的逻辑形成共振：复杂性不只是"外行看不懂"的问题，而是连专业法律人员都无法应对的系统性过载。复杂性成了所有人的困境，不分内行外行。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 227 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p546@0-p550@41:highlight:227`
- source span: `src:c1:p550@0-p550@41`
- source span excerpt:
```text
审计我们这样一家小公司尚且需要这么长时间，如果要审计一家问题重重的大型储贷机构呢？
```
- visible reaction:
```text
这个反问把"六周"这个具体数字变成了一个结构性困境的锚点。审计一家小公司尚且如此，当规模放大、问题变多时，时间和能力的缺口就成为不可弥补的结构性漏洞。六周这个数字本身不重要，重要的是它与"大型储贷机构"之间那道无法跨越的鸿沟。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 228 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p551@0-p555@52:highlight:228`
- source span: `src:c1:p553@51-p553@125`
- source span excerpt:
```text
看到了太多的丑恶，很容易对周围的世界充满敌意。让我去审计一家声名狼藉的储贷机构，看高管睁着眼睛说瞎话，我肯定受不了。每天都要面对人渣，怎么能不崩溃？
```
- visible reaction:
```text
这段话把"敌意"从道德问题还原为心理机制——不是性格问题，是暴露量的函数。和"投行是卖方"的信息困境形成平行：认知被污染，不只是监管人员自身的原因。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 229 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p551@0-p555@52:highlight:229`
- source span: `src:c1:p555@0-p555@52`
- source span excerpt:
```text
我不是要批评监管人员。审计恶劣的储贷机构，如同打一场艰苦的持久战。谁都不可能在残酷的战场上坚持很长时间。
```
- visible reaction:
```text
"我不是要批评"是一个关键姿态——芒格在这里选择理解而非批判，把监管失败从个人道德问题收回了结构性描述。持久战的比喻完成了最后的升格：这不是个体撑不住，是战场设计的结构性问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 230 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p556@0-p560@84:highlight:230`
- source span: `src:c1:p560@43-p560@84`
- source span excerpt:
```text
答对最多的那个人，真会做的只有三道，其他都是蒙的。连蒙带猜，才勉强答对了一半多点。
```
- visible reaction:
```text
这个"三道"和"勉强一半多点"的细节才是真正刺痛的。不是笨，是被设计；不是不懂，是根本没机会懂。这和前文"审计大型储贷机构需要多久"那个结构性困境形成了暗合：不是能力问题，是陷阱设置的问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 231 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p566@0-p570@121:highlight:231`
- source span: `src:c1:p568@14-p568@60`
- source span excerpt:
```text
发放贷款要判断信用风险，做这种风险套利要判断交易达成的可能性。风险套利本质上和发放贷款类似。
```
- visible reaction:
```text
这个类比把风险套利从"炒消息"的印象里拉出来，给它一个清晰的认知框架：不是赌股价波动，而是评估交易概率，本质上是给并购事件放一笔短期贷款。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 232 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p571@0-p573@69:highlight:232`
- source span: `src:c1:p572@0-p572@12`
- source span excerpt:
```text
最重要的知识，商学院没教
```
- visible reaction:
```text
这个标题本身就是一个完整的芒格式命题——不是课程缺失，是最关键的那一块没覆盖到。紧接着就给出了一个具体的锚点。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 233 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p571@0-p573@69:highlight:233`
- source span: `src:c1:p573@44-p573@69`
- source span excerpt:
```text
商学院没教学生如何分辨好生意、一般的生意和烂生意。
```
- visible reaction:
```text
这才是"最重要的知识"的具体内容。三分法在这里不是随口说说，而是芒格判断一切投资机会的核心过滤器：先分出好坏，再决定是否行动。和前文"一年只能做成一笔收购"以及"留在能力圈之中"是同一个决策框架的不同侧面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 234 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p575@0-p578@72:highlight:234`
- source span: `src:c1:p577@0-p577@91`
- source span excerpt:
```text
商学院需要大公司的捐赠，商学院的毕业生需要到大公司就业。所以说，从自己的利益出发，商学院不可能谴责大公司的不良行为，除非一家大公司已经遭到全社会的谴责，那商学院倒是可以跟着进行批判。
```
- visible reaction:
```text
这里说清楚了"不教"的真正原因——不是不知道，是结构性利益使其不可能客观。跟在全社会谴责后面批判是安全的，但这已经是事后了。这和"好生意烂生意三分法"的前文形成完整的因果链：商学院教不了，所以巴菲特只能从格雷厄姆那里学投资技艺，区分好坏的本事是自己悟出来的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 235 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p579@0-p579@11:highlight:235`
- source span: `src:c1:p579@0-p579@11`
- source span excerpt:
```text
低级垃圾债，如镜花水月
```
- visible reaction:
```text
这个比喻直接点出了垃圾债券的本质：表面光鲜，实质上不可靠。芒格在这里没有展开论述，只用八个字就给出了一个定性——与前文"商学院没教"的批判形成内在一致：那些看似诱人、实则危险的东西，往往是被系统性忽视或刻意回避的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 236 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p580@0-p583@45:highlight:236`
- source span: `src:c1:p582@66-p582@142`
- source span excerpt:
```text
现在这个债券值得买了：一方面，向上的潜力很大；另一方面，有大量资产价值做缓冲，向下的保护很充足。加权计算上涨和下跌的概率，得出的净期望值很高，值得投资。
```
- visible reaction:
```text
格雷厄姆的分析公式在这里变得非常透明：先判断向上的弹性，再确认向下的资产安全垫，两者加权后的净期望值为正才值得投。这和前文"好生意烂生意三分法"是一体两面——不是"垃圾债能不能买"的问题，而是先做质地判断，再算期望值。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 237 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p580@0-p583@45:discern:237`
- source span: `src:c1:p580@118-p580@148`
- source span excerpt:
```text
在别人避之唯恐不及的地方发掘投资机会，是一种很好的投资方式。
```
- visible reaction:
```text
这句话在格雷厄姆框架之外又叠加了一层反直觉逻辑：不是"别人贪婪我恐惧"，而是主动去别人恐惧的地方找机会——前提是已经做过了质地和期望值的功课。这和"留在能力圈"的纪律并不冲突，但芒格把它说成"很好的投资方式"，有一种把风险嗅觉内化为本能的味道。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 238 — `local_only` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p585@0-p587@130:discern:238`
- source span: `src:c1:p587@62-p587@118`
- source span excerpt:
```text
如果公司发行的债券只有一个层级，那倒有可能。但像现在这样一层叠一层，只要稍微有个风吹草动，最底层的人就被横扫了。
```
- visible reaction:
```text
这里划出了米尔肯理论与格雷厄姆框架的本质差异：格雷厄姆的期望值计算预设了质地可判断和资产缓冲真实存在；米尔肯的"平均化"却跳过了质地判断，直接用数学把多层级的风险暴露抹平。问题是底层持有者的脆弱性不是概率均值，而是结构性的——任何下跌都会被放大并截留到底层。这不是投资分析，是风险重新分配的障眼法。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 239 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p588@0-p592@197:highlight:239`
- source span: `src:c1:p590@0-p590@45`
- source span excerpt:
```text
被收买的专家学者们，好比是在通过分析一堆橘子的数据，来预测长颈鹿的预期寿命，纯属胡说八道。
```
- visible reaction:
```text
橘子和长颈鹿这个类比本身就是一个笑话结构——直接点出了数据误用的荒谬程度。用错数据的类比来批判用错公式的教授，既精准又带点刻薄。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 240 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p588@0-p592@197:retrospect:240`
- source span: `src:c1:p592@156-p592@197`
- source span excerpt:
```text
如果把第六级垃圾债比作车贷，可以说，在第六级垃圾债中，存在所有车辆都被没收的风险。
```
- visible reaction:
```text
这个"所有车辆同时没收"的表述，把结构性风险和概率性风险的区别说透了。不是"黑天鹅"式的极端事件，而是结构本身决定了全损是常态而非例外。这和前文"只要稍微有个风吹草动，最底层的人就被横扫了"形成数值化的量化支撑。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p585@0-p587@130:discern:238"]}`
  - judge reason: Has explicit prior_link ref_id to reaction 238. Content about 'all vehicles simultaneously confiscated' explicitly references structural risk discussion from 238, providing quantitative support for the earlier claim about底层持有者 vulnerability.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 241 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p593@0-p597@134:highlight:241`
- source span: `src:c1:p596@133-p596@148`
- source span excerpt:
```text
我们不会是第一个倒下去的大学。
```
- visible reaction:
```text
博克这句话把防御逻辑说得很干净。不是"我们最优秀"，而是"我们最后一个倒下"。这句话和段首"老派而保守"形成完整的自我定位：防御不是劣势，而是战略。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 242 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p593@0-p597@134:highlight:242`
- source span: `src:c1:p597@60-p597@134`
- source span excerpt:
```text
我们持有的长期贷款，99.999%都是安全的。在我们持有的贷款中，很多属于房产价值高、贷款金额低的情况，例如，房产价值40万美元、贷款金额两万美元。
```
- visible reaction:
```text
99.999%这个数字本身就是一种声明——不是99%，不是99.9%，而是几乎绝对的确定性。配合那个"40万房产、2万贷款"的极端LTV例子，把"安全边际"从原则落实成了可量化的杠杆比例控制。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 243 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p598@0-p598@136:highlight:243`
- source span: `src:c1:p598@119-p598@136`
- source span excerpt:
```text
但是我们有足够的抵押物价值做担保。
```
- visible reaction:
```text
这句话才是收尾的重心。前面铺垫"很难避免个别违约"，最后用"足够的抵押物"把风险吸收掉。保守不是不亏损，而是不被亏损击穿。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 244 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p599@0-p603@123:highlight:244`
- source span: `src:c1:p601@51-p601@84`
- source span excerpt:
```text
棕榈泉位于炎热的沙漠之中，严重缺水，去酒店只能乘船，还有很多火山。
```
- visible reaction:
```text
这几个细节的组合——沙漠、缺水、船、火山——构成了一幅过于具体的画面。这不是"环境恶劣"的抽象描述，而是用一连串极端特征把一个地方钉死在记忆里。教训用这种方式传递，比"要谨慎"有力得多。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 245 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p599@0-p603@123:highlight:245`
- source span: `src:c1:p603@56-p603@83`
- source span excerpt:
```text
不设贷款任务指标，没有繁多的管理层级和复杂的官僚主义。
```
- visible reaction:
```text
"不设任务指标"这一条，直接切断了以规模扩张为导向的激励链条。在很多金融机构里，贷款任务指标本身就是系统性风险的传导机制。这里把它列为需要主动避免的事项。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 246 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p604@0-p605@139:highlight:246`
- source span: `src:c1:p605@56-p605@92`
- source span excerpt:
```text
短期的记录很详尽，长期的记录没那么详尽，所以做设计的人只考虑了短期记录。
```
- visible reaction:
```text
这句话点出了一个认知陷阱的内部机制：不是因为数据缺乏而犯错，而是因为某类数据"过于详尽"，反而系统性地排除了另一类数据。详尽本身制造了注意力锚定。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 247 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p604@0-p605@139:highlight:247`
- source span: `src:c1:p605@92-p605@139`
- source span excerpt:
```text
如果把几百年前的情况都考虑在内，他们就会发现，他们设计的供水系统有缺陷，没办法应对严重的旱灾。
```
- visible reaction:
```text
"几百年前的情况"——极端事件的时间尺度远超记录覆盖范围。这个比喻的力度在于：它不是用数字说话的，而是用"如果时间拉得足够长，当时设计的依据本身就是残缺的"这个事实来击中盲点。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 248 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p606@0-p608@211:highlight:248`
- source span: `src:c1:p606@75-p606@124`
- source span excerpt:
```text
更重要的那部分信息，虽然对得出正确认知结论很重要，但因为比较模糊，没有准确数字，直接被扔到了一边。
```
- visible reaction:
```text
这里说清楚了认知陷阱的内部机制：不是因为缺少信息而犯错，而是因为某类信息"有数字"，反而把更重要的那部分系统性地排除了。详尽本身制造了注意力锚定。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 249 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p606@0-p608@211:highlight:249`
- source span: `src:c1:p607@92-p607@134`
- source span excerpt:
```text
对于至关重要的信息，没有准确数字，我们会尽力估算，绝对不会只靠准确的部分信息做决定。
```
- visible reaction:
```text
这句把"模糊的正确"从格言落实为操作立场：估算，而不是因为数字缺失就放弃。这是芒格式的诚实——承认自己的估计不精确，但承认缺失数字的那部分更重要，不能因此绕过它。
```
- Selective Legibility dataset relation:
  - note-case `mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0025` / note `mangge_zhi_dao_private_zh_personal_notes__e0025` / label `focused_hit` / best `true` / recall-credit `true`
    - target span(s): `p607@36-134` 我们始终牢记凯恩斯（Keynes）勋爵的箴言，这也是沃伦经常引用的一句话：“宁要模糊的正确，也不要精确的错误。”对于至关重要的信息，没有准确数字，我们会尽力估算，绝对不会只靠准确的部分信息做决定。
    - target note: 我们始终牢记凯恩斯(Keynes)勋爵的箴言，这也是沃伦经常引用的一句话：“宁要模糊的正确，也不要精确的错误。”对于至关重要的信息，没有准确数字，我们会尽力估算，绝对不会只靠准确的部分信息做决定。
    - source-span relation: `note_contains_candidate`; coverage `0.43`
    - judge/runner reason: The reaction's quoted source span covers the core operational principle from the note (estimation when numbers are missing, not bypassing crucial information). The reaction correctly identifies the key insight as '芒格式的诚实' (Munger's honesty) and captures the essential message: the transition from the motto '模糊的正确' to concrete operational stance. The overlap, while not including the famous Keynes quote itself, contains the most practically important content of the note.
    - reviewer interpretation: Focused credit: source overlap admitted the candidate and the judge accepted that the reaction centers the target note idea.
    - raw note-case artifact: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_user_level_post_slice8h_20260519_reuse_mangge/note_cases/mangge_zhi_dao_private_zh__mangge_zhi_dao_private_zh_personal_notes__e0025.json`
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 250 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p609@0-p611@101:highlight:250`
- source span: `src:c1:p611@30-p611@80`
- source span excerpt:
```text
没有大批监管人员对它进行审计，它用不着支付这项合规成本。它没有上一级的监管部门，不必缴纳存款保险金。
```
- visible reaction:
```text
把监管成本拆解成三个具体项：审计人员、合规成本、存款保险金。不是笼统说"监管负担重"，而是让读者看见每一项都对应着一家正常金融机构必须承担的刚性费用。这种拆解方式本身就是芒格式的——把一个模糊的概念变成可以核算的结构。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 251 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p612@0-p616@122:highlight:251`
- source span: `src:c1:p614@121-p614@186`
- source span excerpt:
```text
房地美不是对所有开发商都采取排斥的态度，而是具有严格的把关标准。房地美一开始就很清楚，市场中可能存在大量不良行为。它这么做是对的。
```
- visible reaction:
```text
这里的「对」不是含糊的肯定，而是有内在逻辑的——清楚市场中存在大量不良行为，所以把不信任写进程序。这种「不信任」不是悲观，是基于概率认知的防御性设计。把这个立场明确表达出来，而不是用「谨慎」之类的软词带过，是芒格式的分析诚实。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 252 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p612@0-p616@122:highlight:252`
- source span: `src:c1:p615@0-p615@35`
- source span excerpt:
```text
我们有很多老股东，之所以长期持有西科，不也是因为认同我们的行事风格吗？
```
- visible reaction:
```text
这句话把股东选择从结果变成了价值观的认同——不是「买了西科的股票」，而是「认同行事风格所以持有」。这是把股东关系从市场行为重新定义为理念共同体，同时为后面关于互助储蓄开发商筛选的经验做铺垫：他们之所以这样做，是因为这就是他们的行事风格。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 253 — `grounded_callback` — `discern`

- reaction_id: `rx:Full_Content:src:c1:p621@0-p623@84:discern:253`
- source span: `src:c1:p623@38-p623@84`
- source span excerpt:
```text
赚尽最后一个铜板，这是银行和储贷机构犯过的错误。如今，货币市场基金重蹈覆辙，也想赚钱赚到尽。
```
- visible reaction:
```text
「赚尽最后一个铜板」在这里不是修辞，而是被当作一个可以被重复引用的历史案例模式。第一句确认这个错误曾经发生，第二句直接宣告货币市场基金正在重演。「重蹈覆辙」这个词把时间跨度很大的两类机构并置，暗示这不是偶然，而是某种可识别的行为模式——当机构从"赚钱"转向"赚尽"时，崩溃就是时间问题。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - judge reason: Explicitly identifies '赚尽最后一个铜板' as a historical pattern and connects '货币市场基金' as current repetition using '重蹈覆辙' - clearly links present phenomenon to established pattern from earlier visible analysis.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 254 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p621@0-p623@84:highlight:254`
- source span: `src:c1:p621@0-p621@67`
- source span excerpt:
```text
在现有住房市场，没出现信用紧缩的现象。一些房贷出现违约，或是因为之前房价炒得太高，或是因为部分地区的经济出现了大滑坡，与监管部门无关。
```
- visible reaction:
```text
这里把房贷违约的归因明确划归市场因素而非监管因素——不是在为监管辩护，而是在说监管的缺位并没有导致紧缩。这种精确的因果切割在芒格的分析中很典型：不介入政治判断，只说明客观机制。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 255 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p624@0-p624@157:highlight:255`
- source span: `src:c1:p624@28-p624@102`
- source span excerpt:
```text
为了防范风险，我们制定的规矩，恰恰是不赚最后一个铜板。例如，我们会规定：参照高信用等级的标准收益率，如果某品种的收益率高出0.125%，则禁止投资。
```
- visible reaction:
```text
「不赚最后一个铜板」在这里不是修辞或道德劝诫，而是一套可以编号、写进手册、用数字执行的操作规程。0.125%这个具体阈值让模糊的风险意识变成了清晰的投资边界。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 256 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p624@0-p624@157:highlight:256`
- source span: `src:c1:p624@102-p624@157`
- source span excerpt:
```text
一笔投资，利率超出了正常水平，我们绝对不碰。另外，对于发行人，我们也有限制条件，只投资符合条件的发行人的品种。
```
- visible reaction:
```text
「正常水平」和「符合条件的发行人」是两个维度——一个约束价格，一个约束交易对手。两道闸门同时存在，说明风险控制不是单点而是结构性的。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 257 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p625@0-p629@29:highlight:257`
- source span: `src:c1:p626@0-p626@68`
- source span excerpt:
```text
货币市场基金这个生意还是很赚钱的。在今年的伯克希尔股东会上，有股东问我，为什么不把互助储蓄变成一家货币市场基金。我都不知道怎么回答好了。
```
- visible reaction:
```text
"不知道怎么回答"在这里不是谦虚，是芒格式的沉默式拒绝——不正面辩论，但沉默本身就是立场。面对一个短期很赚钱的业务，他没有解释逻辑，而是直接退出了对话。这比直接说"我不看好"更有力。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 258 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p625@0-p629@29:highlight:258`
- source span: `src:c1:p627@0-p627@16`
- source span excerpt:
```text
天生丽质的公司，经得起时间的考验
```
- visible reaction:
```text
这个标题是个定义性声明。结合本段西科"资金已用在别处"、芒格"人在欧洲"而伯克希尔接手PS集团的叙事，天生丽质的含义很清楚：不是某个时点做对了什么，而是无论是谁掌舵、有没有我在场，结构上始终有可用资产待命。好的公司不依赖天才在场。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 259 — `grounded_callback` — `retrospect`

- reaction_id: `rx:Full_Content:src:c1:p630@0-p634@115:retrospect:259`
- source span: `src:c1:p632@0-p632@30`
- source span excerpt:
```text
这几家公司都经营管理得很好。它们天生丽质，谁来经营都差不了。
```
- visible reaction:
```text
前文把"天生丽质"作为标题概念抛出，这里用一句话给出了完整的操作化定义：好公司的股份，牢牢抓在手里——不是时点判断，是结构立场。"谁来经营都差不了"是关键——好公司不依赖天才在场。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: `grounded_callback`
  - prior_link: `{"ref_ids": ["reaction:rx:Full_Content:src:c1:p625@0-p629@29:highlight:258"]}`
  - judge reason: Explicitly references earlier reaction rx:Full_Content:src:c1:p625@0-p629@29:highlight:258 via prior_link field, correctly developing the '天生丽质' concept by explaining its operational meaning.
  - reviewer interpretation: accepted as a visible callback because the audit found enough prior visible evidence or an explicit prior link.

### Reaction 260 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p630@0-p634@115:highlight:260`
- source span: `src:c1:p634@97-p634@115`
- source span excerpt:
```text
买西科、不买伯克希尔，是脑子糊涂了。
```
- visible reaction:
```text
一句话结论，没有修饰，没有任何退路。这是芒格式的直接。前提是第633段已经铺垫了"西科底子很薄"——两句话之间逻辑清晰：底子薄，所以买小不买大是糊涂。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 261 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p635@0-p636@82:highlight:261`
- source span: `src:c1:p636@41-p636@82`
- source span excerpt:
```text
20世纪70年代早期，出现了很多机会，我们感觉就像“桶里射鱼”一样。现在可不行了。
```
- visible reaction:
```text
这个时间对照很清晰——70年代初是结构性easy money，遍地便宜货；现在是机会稀少但管理层收购热情依旧。同一批人在做判断，但机会结构已经完全不同了。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 262 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p637@0-p639@94:highlight:262`
- source span: `src:c1:p639@28-p639@94`
- source span excerpt:
```text
如果自己公司的股票是高估的，用自己公司的股票收购同行，倒也不吃亏。至于像我们这样用现金收购的，那就难了。特别是最近一段时间，非常难。
```
- visible reaction:
```text
这里点出了一个结构性不对称：用高估的股票收购是隐性的杠杆，等于用别人的钱买自己的东西；现金收购没有这个缓冲层，是纯粹的价值支付。三个"非常难"的递进，不是修辞，是芒格对现实的直接陈述——不是悲观预期，而是对机会结构正在收紧的判断。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 263 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p640@0-p644@19:highlight:263`
- source span: `src:c1:p643@0-p643@87`
- source span excerpt:
```text
作者说，有两家公司用它们的实际行动表明了，经理人以公司所有者利益为重，才能造福股东。这两家公司一个是伯克希尔·哈撒韦，另一个是汉森工业（Hanson Industries）。
```
- visible reaction:
```text
这里终于点出了具体公司。伯克希尔在文中出现多次，但"伯克希尔·哈撒韦"这个完整名称出现在这里，是作为正面案例被外部权威引用——不是芒格自夸，而是《经济学人》通过外部视角确认了同一点。这与前文"买西科、不买伯克希尔是脑子糊涂了"形成互证，只是论证来源不同。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 264 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p640@0-p644@19:highlight:264`
- source span: `src:c1:p644@0-p644@19`
- source span excerpt:
```text
快进快出、唯利是图，不是我们的行事风格
```
- visible reaction:
```text
这是整段的落点。用否定句式而非肯定句式划界限，是芒格的一贯风格——不说"我们是怎样"，而说"我们不是怎样"。这句话直接回应段落开头"现在人们热衷于收购"的背景，把主流文化当作反面教材留在那里，然后转身离开。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 265 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p645@0-p649@59:highlight:265`
- source span: `src:c1:p645@141-p645@159`
- source span excerpt:
```text
我们不会像打牌一样，抓一张、扔一张。
```
- visible reaction:
```text
"打牌"这个比喻为整个段落定了调——把主流收购文化的轻率比作赌桌行为，而西科/伯克希尔的立场是不换手、不放弃。与前文"快进快出、唯利是图"形成同一个意思的两个侧面。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 266 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p645@0-p649@59:highlight:266`
- source span: `src:c1:p648@38-p648@60`
- source span excerpt:
```text
我们也不绝对保证，永远不出售任何一家子公司。
```
- visible reaction:
```text
在做了坚定的原则性陈述之后，补这一句是典型的芒格式表达：划定界限的同时保留一点弹性，不把自己锁死在绝对承诺里。这和"攥在手里，不意味着永远"是同一个逻辑结构——主动选择而非被迫承诺。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 267 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p650@0-p654@79:highlight:267`
- source span: `src:c1:p654@0-p654@79`
- source span excerpt:
```text
在进行这笔收购时，本来有更好的投资机会，但我们被西科便宜的价格吸引住了，只看到它的价格比清算价值还低，于是做了一笔不划算的投资，买了一家内在价值并不高的公司。
```
- visible reaction:
```text
"只看到它的价格比清算价值还低"——这是芒格式的精准表述。不是看错了公司，而是看问题的维度错了：把"便宜"当成买入理由，而没有问"便宜的东西到底值不值"。价值投资的陷阱，有时候恰恰在于低价本身。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 268 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p650@0-p654@79:highlight:268`
- source span: `src:c1:p653@0-p653@11`
- source span excerpt:
```text
西科的底子薄是天生的。
```
- visible reaction:
```text
"天生的"三个字把问题定调了：这不是管理失误或市场变化造成的，而是结构性的起点问题。这解释了为什么西科此后的多年一直在"守势"——底子薄决定了它的选择空间受限。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 269 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p655@0-p657@56:highlight:269`
- source span: `src:c1:p657@0-p657@29`
- source span excerpt:
```text
好生意内在价值高，如同兔子。普通生意内在价值低，如同乌龟。
```
- visible reaction:
```text
兔子/乌龟的类比在这里不只是修辞，而是把价值投资的竞争结构说清楚了：好生意天然跑得快，普通生意天然跑得慢，这不是努力能弥补的起点差异。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

### Reaction 270 — `local_only` — `highlight`

- reaction_id: `rx:Full_Content:src:c1:p655@0-p657@56:highlight:270`
- source span: `src:c1:p657@29-p657@55`
- source span excerpt:
```text
西科是一只与兔子赛跑的乌龟，而且是一只不好动的乌龟。
```
- visible reaction:
```text
"不好动"三个字把芒格的自我定位说到了最诚实的地方——不是不能动，是主动选择不动。这和前面"攥在手里，不意味着永远"是同一个底色：好机会没出现之前，不作为是美德而非懒惰。
```
- Selective Legibility dataset relation: not in selective-legibility target set for this run.
- Callback/FVI audit: local-only visible reaction; no callback claim credited or rejected.

## Probe Memory Checkpoints

Memory Quality in this historical Eval-1 Retry1 dossier was scored from legacy probe-time digest snapshots. These scores should be read as `memory_snapshot_basis=legacy_digest_snapshot`, not as full-state Memory Quality. The state blocks below are exact Markdown re-layouts of recorded digest fields, not fresh summaries and not final runtime dumps.

### Memory State Evidence Boundary

- Legacy probe-time digest evidence: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json`. The per-probe blocks below come from snapshot fields such as `active_attention_digest`, `concept_digest`, `thread_digest`, `reflective_digest`, and `source_ref_digest`.
- Final full runtime state references: files under `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime`. These are useful for diagnosis, but they are window-end state references rather than the exact state used at each Memory Quality probe.
- Window boundary checkpoint: `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/checkpoints/chapter-001.json`. This is the chapter/window boundary checkpoint, not five independent probe-time checkpoints.
- Historical artifact boundary: current Eval-1 artifacts do not contain `scoring_memory_state`, so these MQ scores remain legacy digest-based. Post-repair runs should score full probe-time memory stores from `scoring_memory_state`.

### Full Runtime State Links

| State artifact | Path | Boundary note |
| --- | --- | --- |
| Active Attention | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/active_attention.json` | Final window-end active attention store; not the probe-time full store. |
| Concept Registry | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/concept_registry.json` | Final window-end concept store; use for diagnosis only. |
| Thread Trace | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/thread_trace.json` | Final window-end thread store; use for diagnosis only. |
| Reflective Frames | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reflective_frames.json` | Final window-end reflective store; use for diagnosis only. |
| Reaction Records | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/reaction_records.json` | Final window reaction record store; timeline above is the reviewer-readable projection. |
| Read Audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/read_audit.jsonl` | Runtime operation/audit stream for diagnosis. |
| Settlement Audit | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/settlement_audit.jsonl` | Runtime settlement/audit stream for diagnosis. |
| Chapter checkpoint | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/runtime/checkpoints/chapter-001.json` | Full window boundary checkpoint, not a per-probe checkpoint. |

### Probe 1 — MQ `4.00` — near 20%

#### Probe Position And Question
- target sentence: `c1-s411`
- boundary kind: `annual chapter close`
- why this point: Closes the 1988 discussion before the 1989 turn, giving a semantically complete checkpoint for the early management-trust and valuation discipline material.
- structural signals to check:
  - 1988 annual discussion closure
  - management trust and reputation
  - valuation discipline before the 1989 shift

#### Source Orientation
```text
   s409 / p177: 我不能向你们剧透。
   s410 / p178: 西科的股东因为信任管理层而买入
>> s411 / p179: 西科的股东是一群特立独行的价值投资者。
   s412 / p180: 他们最早买入的时候，西科很有价值。
   s413 / p180: 现在，西科已经没那么有价值了，他们还是愿意买。
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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
      "ref_id": "active_attention:wesco_defensive_posture",
      "item_id": "wesco_defensive_posture",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科的守势逻辑：收购难做，股市也没好机会——两条主动路径同时关闭。但守势是主动选择，不是被迫撤退。和\"攥在手里，不意味着永远\"的立场一致：现在不动，因为没好标的，不是动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p41@142-p41@181",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 142
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 181
            }
          },
          "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
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
      "ref_id": "active_attention:wesco_1987_financial_data",
      "item_id": "wesco_1987_financial_data",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融财务数据（编者按）：合并净运营收益（不计投资收益）1661.2万美元，每股2.33美元；合并净收益1521.3万美元，每股2.14美元。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p91@40-p91@105",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 40
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 105
            }
          },
          "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
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
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:adverse_selection_as_design",
    "concept_key": "adverse_selection_as_design",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p142@18-p142@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 75
          }
        },
        "quote": "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:agency_cost_commoditization",
    "concept_key": "agency_cost_commoditization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p73@56-p73@100",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 56
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 100
          }
        },
        "quote": "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:annual_one_deal_discipline",
    "concept_key": "annual_one_deal_discipline",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p38@0-p38@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 97
          }
        },
        "quote": "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。"
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

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:humility_through_success_tension",
    "thread_key": "humility_through_success_tension",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@0-p76@140",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 140
          }
        },
        "quote": "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p82@0-p82@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 102
          }
        },
        "quote": "清楚自己能力的大小，这个品质应该不能说是'谦卑'。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
      "清楚自己能力的大小，这个品质应该不能说是'谦卑'。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:liquidation_value_ethical_constraint",
    "thread_key": "liquidation_value_ethical_constraint",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p174@0-p174@33",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 174,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 174,
            "char_offset": 33
          }
        },
        "quote": "有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:munger_market_timing_record",
    "thread_key": "munger_market_timing_record",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@0-p10@64",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 64
          }
        },
        "quote": "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。"
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

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@0-p4@172",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 172
      }
    },
    "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@0-p23@57",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 57
      }
    },
    "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p32@0-p32@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 53
      }
    },
    "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@0-p33@62",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 62
      }
    },
    "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p41@142-p41@181",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 142
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 181
      }
    },
    "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p91@40-p91@105",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 40
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 105
      }
    },
    "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p112@0-p112@61",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 61
      }
    },
    "quote": "你问我，西科的保险业务这几年的综合成本率如何？我估计，从我们签署合作协议起的四年里，我们的综合成本率大概是104、105。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p139@36-p139@85",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 36
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 85
      }
    },
    "quote": "从表面上看，我们的利差低于平均水平。从目前的情况看，与我们自身相比，我们的利差已经比过去高了很多。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
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
- judge reason: The snapshot retains strong, important material across multiple dimensions. Key retained items include: Wesco's three-branch structure (互助储蓄, 精密钢材, 西科保险), the annual-one-deal acquisition discipline, the defensive posture when both acquisition and equity markets close, the management quality criteria (Munger's 'thrown off train' test), and the Solomon investment with AA rating and John Gutfreund's credit-risk vigilance. The closing reactions capture the trust-centered investment thesis ('西科不是好生意，但我们的股东因为信任管理层而买入') as a thematic landing point. The three structural signals are all addressed: the 1988 chapter closure is reflected in the captured sentences near 411; management trust and reputation is central to the active focus and the closing reactions; valuation discipline (ideal company, cash generation, rational deployment) is present in the concept_digest. The snapshot shows minor flattening of contextual details (e.g., the precision steel 1979 acquisition date is a detail rather than a salient frame), but no significant drift or false material. Organization is solid with clear conceptual clusters and thematic threading. Rating 4.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[0]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.

### Probe 2 — MQ `3.25` — near 40%

#### Probe Position And Question
- target sentence: `c1-s710`
- boundary kind: `major argument turn`
- why this point: Ends the anti-forecasting and cash-optionality argument before the Mutual Savings topic expands the 1989 material.
- structural signals to check:
  - anti-forecasting investment posture
  - cash optionality
  - disclosure boundary and Mutual Savings transition

#### Source Orientation
```text
   s708 / p271: 手握大量现金，我们向威廉·奥斯勒爵士学习。
   s709 / p271: 脚踏实地，做好眼前的事，让公司顺其自然地长期发展。
>> s710 / p271: 我们是一家特立独行的公司。
   s711 / p272: 在西科的资产负债表中，绝大部分资产是高流动性的类现金资产。
   s712 / p272: 占比如此之高的流动资产，该如何配置？
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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
      "ref_id": "active_attention:wesco_defensive_posture",
      "item_id": "wesco_defensive_posture",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科的守势逻辑：收购难做，股市也没好机会——两条主动路径同时关闭。但守势是主动选择，不是被迫撤退。和\"攥在手里，不意味着永远\"的立场一致：现在不动，因为没好标的，不是动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p41@142-p41@181",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 142
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 181
            }
          },
          "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
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
      "ref_id": "active_attention:wesco_1987_financial_data",
      "item_id": "wesco_1987_financial_data",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融财务数据（编者按）：合并净运营收益（不计投资收益）1661.2万美元，每股2.33美元；合并净收益1521.3万美元，每股2.14美元。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p91@40-p91@105",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 40
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 105
            }
          },
          "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
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
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:adverse_selection_as_design",
    "concept_key": "adverse_selection_as_design",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p142@18-p142@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 75
          }
        },
        "quote": "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:agency_cost_commoditization",
    "concept_key": "agency_cost_commoditization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p73@56-p73@100",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 56
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 100
          }
        },
        "quote": "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:annual_one_deal_discipline",
    "concept_key": "annual_one_deal_discipline",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p38@0-p38@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 97
          }
        },
        "quote": "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。"
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

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:humility_through_success_tension",
    "thread_key": "humility_through_success_tension",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@0-p76@140",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 140
          }
        },
        "quote": "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p82@0-p82@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 102
          }
        },
        "quote": "清楚自己能力的大小，这个品质应该不能说是'谦卑'。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
      "清楚自己能力的大小，这个品质应该不能说是'谦卑'。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:munger_market_timing_record",
    "thread_key": "munger_market_timing_record",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@0-p10@64",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 64
          }
        },
        "quote": "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p249@43-p249@153",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 43
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 153
          }
        },
        "quote": "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
      "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:liquidation_value_ethical_constraint",
    "thread_key": "liquidation_value_ethical_constraint",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p174@0-p174@33",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 174,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 174,
            "char_offset": 33
          }
        },
        "quote": "有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有时候，清算价值是有办法实现的，但我们不会那么做，我们不想那么做。"
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

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@0-p4@172",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 172
      }
    },
    "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@0-p23@57",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 57
      }
    },
    "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p32@0-p32@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 53
      }
    },
    "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@0-p33@62",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 62
      }
    },
    "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p41@142-p41@181",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 142
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 181
      }
    },
    "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p91@40-p91@105",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 40
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 105
      }
    },
    "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p112@0-p112@61",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 61
      }
    },
    "quote": "你问我，西科的保险业务这几年的综合成本率如何？我估计，从我们签署合作协议起的四年里，我们的综合成本率大概是104、105。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p139@36-p139@85",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 36
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 85
      }
    },
    "quote": "从表面上看，我们的利差低于平均水平。从目前的情况看，与我们自身相比，我们的利差已经比过去高了很多。",
    "role": "support",
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
- judge reason: The snapshot retains solid material on Wesco's asset posture (攥在手里不意味着永远, 两条路都关闭的守势), the disclosure boundary rule (recent_reactions: '不谈论' as cognitive boundary, '不发表评论就是不发表评论'), and company structure. However, the 'anti-forecasting investment posture' as a coherent framework is fragmented—the Osler/Carlyle '与其为朦胧的未来而烦恼忧虑，不如脚踏实地' quote (which anchors the entire anti-forecast argument) and the 'no long-term planning' principle are in the source but absent from active digest items or concept_digest, weakening salience. More critically for this probe point, the 'boundary_kind: major argument turn' marking an ending is not reflected in the snapshot—it preserves active items on Mutual Savings structure but gives no signal that this is a closing point before Mutual Savings 'expands the 1989 material,' nor does it encode the upcoming 1989 shift in Mutual Savings' prominence.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[1]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.

### Probe 3 — MQ `2.25` — near 60%

#### Probe Position And Question
- target sentence: `c1-s1053`
- boundary kind: `crisis appendix argument turn`
- why this point: Completes the causal explanation of policy changes in the S&L crisis before the text moves into broader judgment.
- structural signals to check:
  - S&L crisis mechanics
  - regulatory incentives and unintended consequences
  - causal explanation before normative judgment

#### Source Orientation
```text
   s1051 / p396: 受这些害群之马的影响，稳健经营的储贷机构也被拉下了水。
   s1052 / p396: 或是为了摆脱困境，或是为了一夜暴富，有些储贷机构承诺非常高的利率，拼命做大规模。
>> s1053 / p396: 结果经营保守的储贷机构，被迫向它们看齐，不得不承受更高的存款成本。
   s1054 / p397: 存款成本上升了，为了覆盖成本，原本保守的储贷机构别无选择，只能考虑风险更高、收益更高的资产。
   s1055 / p398: 于是，因为存款有保险、利率不受限制，储贷行业上演了“劣币驱逐良币”的一幕。
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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
      "ref_id": "active_attention:wesco_defensive_posture",
      "item_id": "wesco_defensive_posture",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科的守势逻辑：收购难做，股市也没好机会——两条主动路径同时关闭。但守势是主动选择，不是被迫撤退。和\"攥在手里，不意味着永远\"的立场一致：现在不动，因为没好标的，不是动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p41@142-p41@181",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 142
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 181
            }
          },
          "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
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
      "ref_id": "active_attention:wesco_1987_financial_data",
      "item_id": "wesco_1987_financial_data",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融财务数据（编者按）：合并净运营收益（不计投资收益）1661.2万美元，每股2.33美元；合并净收益1521.3万美元，每股2.14美元。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p91@40-p91@105",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 40
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 105
            }
          },
          "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
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
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:adverse_selection_as_design",
    "concept_key": "adverse_selection_as_design",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p142@18-p142@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 75
          }
        },
        "quote": "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:agency_cost_commoditization",
    "concept_key": "agency_cost_commoditization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p73@56-p73@100",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 56
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 100
          }
        },
        "quote": "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:annual_one_deal_discipline",
    "concept_key": "annual_one_deal_discipline",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p38@0-p38@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 97
          }
        },
        "quote": "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。"
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

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:humility_through_success_tension",
    "thread_key": "humility_through_success_tension",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@0-p76@140",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 140
          }
        },
        "quote": "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p82@0-p82@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 102
          }
        },
        "quote": "清楚自己能力的大小，这个品质应该不能说是'谦卑'。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
      "清楚自己能力的大小，这个品质应该不能说是'谦卑'。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:munger_market_timing_record",
    "thread_key": "munger_market_timing_record",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@0-p10@64",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 64
          }
        },
        "quote": "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p249@43-p249@153",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 43
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 153
          }
        },
        "quote": "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
      "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:chaos_opportunity_structural_advantage",
    "thread_key": "chaos_opportunity_structural_advantage",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p282@0-p282@44",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 282,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 282,
            "char_offset": 44
          }
        },
        "quote": "混乱局面出现了，你拥有雄厚的财力，可能会有好机会。别人都把子弹打没了，你可能会有好机会。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "混乱局面出现了，你拥有雄厚的财力，可能会有好机会。别人都把子弹打没了，你可能会有好机会。"
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

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@0-p4@172",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 172
      }
    },
    "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@0-p23@57",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 57
      }
    },
    "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p32@0-p32@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 53
      }
    },
    "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@0-p33@62",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 62
      }
    },
    "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p41@142-p41@181",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 142
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 181
      }
    },
    "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p91@40-p91@105",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 40
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 105
      }
    },
    "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p112@0-p112@61",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 61
      }
    },
    "quote": "你问我，西科的保险业务这几年的综合成本率如何？我估计，从我们签署合作协议起的四年里，我们的综合成本率大概是104、105。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p139@36-p139@85",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 36
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 85
      }
    },
    "quote": "从表面上看，我们的利差低于平均水平。从目前的情况看，与我们自身相比，我们的利差已经比过去高了很多。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  }
]
```
#### Score Rationale
- salience: `2`
- mainline_fidelity: `2`
- organization: `2`
- fidelity: `3`
- judge-provided overall: `2`
- final overall MQ: `2.25`
- judge reason: The snapshot retains important S&L crisis insights in recent_reactions (policy combinations as locked system, '九龙治水' fragmentation diagnosis, complexity theory observation), but critically omits the detailed causal mechanism that should anchor this probe point. The causal chain from '制度的死穴' through deregulated incentives to moral hazard gambling with taxpayer money is present in the source text's appendix but absent from active focus items, concept digest, and thread digest. Instead, active focus items center on Wesco's operational structure (three subsidiaries, asset solidity, defensive posture), which is contextually relevant but secondary to the stated probe purpose. The thread_digest includes general investment principles ('chaos_opportunity_structural_advantage') and unrelated material ('humility_through_success_tension') but no thread specifically tracing the S&L crisis mechanics. The probe_review_focus explicitly states 'completes the causal explanation' — this causal chain is not structurally retained in any core memory field, only as recent_reaction highlights.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[2]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.

### Probe 4 — MQ `2.75` — near 80%

#### Probe Position And Question
- target sentence: `c1-s1418`
- boundary kind: `section close`
- why this point: Closes the 1990 S&L crisis section before the text shifts toward Graham and risk-arbitrage lessons.
- structural signals to check:
  - 1990 crisis recap
  - regulator exhaustion
  - transition from crisis diagnosis to investing doctrine

#### Source Orientation
```text
   s1416 / p549: 监管人员：有六个星期了。
   s1417 / p550: 审计我们这样一家小公司尚且需要这么长时间，如果要审计一家问题重重的大型储贷机构呢？
>> s1418 / p551: 监管人员：最近我们审计了一家濒临破产的储贷机构，用了九个月的时间。
   s1419 / p552: 感觉快崩溃了吧？
   s1420 / p552: 我想起了很久以前遇到的一位国税局审计员。
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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
      "ref_id": "active_attention:wesco_defensive_posture",
      "item_id": "wesco_defensive_posture",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科的守势逻辑：收购难做，股市也没好机会——两条主动路径同时关闭。但守势是主动选择，不是被迫撤退。和\"攥在手里，不意味着永远\"的立场一致：现在不动，因为没好标的，不是动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p41@142-p41@181",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 142
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 181
            }
          },
          "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
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
      "ref_id": "active_attention:wesco_1987_financial_data",
      "item_id": "wesco_1987_financial_data",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融财务数据（编者按）：合并净运营收益（不计投资收益）1661.2万美元，每股2.33美元；合并净收益1521.3万美元，每股2.14美元。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p91@40-p91@105",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 40
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 105
            }
          },
          "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
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
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:adverse_selection_as_design",
    "concept_key": "adverse_selection_as_design",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p142@18-p142@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 75
          }
        },
        "quote": "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:agency_cost_commoditization",
    "concept_key": "agency_cost_commoditization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p73@56-p73@100",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 56
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 100
          }
        },
        "quote": "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:annual_one_deal_discipline",
    "concept_key": "annual_one_deal_discipline",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p38@0-p38@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 97
          }
        },
        "quote": "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。"
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

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:humility_through_success_tension",
    "thread_key": "humility_through_success_tension",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@0-p76@140",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 140
          }
        },
        "quote": "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p82@0-p82@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 102
          }
        },
        "quote": "清楚自己能力的大小，这个品质应该不能说是'谦卑'。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
      "清楚自己能力的大小，这个品质应该不能说是'谦卑'。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:munger_market_timing_record",
    "thread_key": "munger_market_timing_record",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@0-p10@64",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 64
          }
        },
        "quote": "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p249@43-p249@153",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 43
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 153
          }
        },
        "quote": "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
      "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:chaos_opportunity_structural_advantage",
    "thread_key": "chaos_opportunity_structural_advantage",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p282@0-p282@44",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 282,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 282,
            "char_offset": 44
          }
        },
        "quote": "混乱局面出现了，你拥有雄厚的财力，可能会有好机会。别人都把子弹打没了，你可能会有好机会。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "混乱局面出现了，你拥有雄厚的财力，可能会有好机会。别人都把子弹打没了，你可能会有好机会。"
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

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@0-p4@172",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 172
      }
    },
    "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@0-p23@57",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 57
      }
    },
    "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p32@0-p32@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 53
      }
    },
    "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@0-p33@62",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 62
      }
    },
    "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p41@142-p41@181",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 142
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 181
      }
    },
    "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p91@40-p91@105",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 40
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 105
      }
    },
    "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p112@0-p112@61",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 61
      }
    },
    "quote": "你问我，西科的保险业务这几年的综合成本率如何？我估计，从我们签署合作协议起的四年里，我们的综合成本率大概是104、105。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p139@36-p139@85",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 36
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 85
      }
    },
    "quote": "从表面上看，我们的利差低于平均水平。从目前的情况看，与我们自身相比，我们的利差已经比过去高了很多。",
    "role": "support",
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
- mainline_fidelity: `2`
- organization: `3`
- fidelity: `3`
- judge-provided overall: `1`
- final overall MQ: `2.75`
- judge reason: The snapshot retains the 1990 S&L crisis recap with reasonable fidelity—the industry's self-inflicted wounds, the shame of lobbying, the system design failures (government backstop + no rate limits = gambling), and critically, the regulator exhaustion material (six weeks for a small company audit, nine months for a large one, the '持久战' metaphor). However, the probe's explicit structural signal 'transition from crisis diagnosis to investing doctrine' is entirely absent. The source text explicitly signals that after closing the 1990 S&L crisis section, the text will shift toward Graham and risk-arbitrage lessons; the snapshot shows no forward-looking conceptual bridge toward this next doctrinal phase. The retained material is accurate and sourced, but the snapshot reads as a retrospective locked into the crisis diagnosis without retaining the signal that investing doctrine lessons follow.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[3]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.

### Probe 5 — MQ `3.25` — window end

#### Probe Position And Question
- target sentence: `c1-s1755`
- boundary kind: `window end`
- why this point: Ends the active window, allowing the final snapshot to cover the full selected annual-letter span.
- structural signals to check:
  - full-window investment doctrine continuity
  - crisis-to-risk-arbitrage arc
  - Munger/Buffett operating principles across the window

#### Source Orientation
```text
   s1753 / p652: “在西科的全部内在价值中，只有很小的一部分具有商业优势，能保证长期实现较高的资本收益率。
   s1754 / p652: 西科的母公司伯克希尔·哈撒韦则完全不同。
>> s1755 / p652: 在伯克希尔的全部内在价值中，大部分是好生意，能长期获得较高的资本收益率。
   s1756 / p653: 西科的底子薄是天生的。
   s1757 / p653: 当年，西科的母公司收购西科时，西科就非常孱弱。
```

#### Probe-time snapshot field: active_attention_digest

`active_attention_digest`:

```json
{
  "active_items": [
    {
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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
      "ref_id": "active_attention:wesco_defensive_posture",
      "item_id": "wesco_defensive_posture",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科的守势逻辑：收购难做，股市也没好机会——两条主动路径同时关闭。但守势是主动选择，不是被迫撤退。和\"攥在手里，不意味着永远\"的立场一致：现在不动，因为没好标的，不是动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p41@142-p41@181",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 142
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 41,
              "char_offset": 181
            }
          },
          "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
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
      "ref_id": "active_attention:wesco_1987_financial_data",
      "item_id": "wesco_1987_financial_data",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融财务数据（编者按）：合并净运营收益（不计投资收益）1661.2万美元，每股2.33美元；合并净收益1521.3万美元，每股2.14美元。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p91@40-p91@105",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 40
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 91,
              "char_offset": 105
            }
          },
          "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
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
      "ref_id": "active_attention:wesco_1987_structure",
      "item_id": "wesco_1987_structure",
      "attention_tags": [
        "focus"
      ],
      "statement": "1987年西科金融三个主要分支机构：互助储蓄（加州帕萨迪纳）、精密钢材Precision Steel（芝加哥，1979年收购）、西科—金融保险公司（奥马哈，再保险）",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p4@0-p4@172",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 4,
              "char_offset": 172
            }
          },
          "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
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
      "ref_id": "active_attention:wesco_board_composition",
      "item_id": "wesco_board_composition",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科董事会成员：迪克·罗森塔尔（已故，飞机事故）之后，蒂施家族成员（Tisch family）接续作为董事会保障力量",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p23@0-p23@57",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 23,
              "char_offset": 57
            }
          },
          "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
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
      "ref_id": "active_attention:wesco_asset_solidity",
      "item_id": "wesco_asset_solidity",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融资产状况：质量可靠，手握大量富余资产，目前缺乏好机会配置。保险业务可能因周期不利而收缩，但资产和盈利能力不受业务中断影响。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p32@0-p32@53",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 32,
              "char_offset": 53
            }
          },
          "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
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
      "ref_id": "active_attention:wesco_asset_deployability",
      "item_id": "wesco_asset_deployability",
      "attention_tags": [
        "focus"
      ],
      "statement": "西科金融的资产立场：手握大量资产是主动选择，持有状态有弹性，即使极端情况下也能部署。\"这是现在，不意味着永远\"——不动是因为没好机会，不是因为动不了。",
      "status": "active",
      "source_refs": [
        {
          "source_span_id": "src:c1:p33@0-p33@62",
          "source_span": {
            "start_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 0
            },
            "end_cursor": {
              "chapter_id": 1,
              "chapter_ref": "Full Content",
              "paragraph_index": 33,
              "char_offset": 62
            }
          },
          "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
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

#### Probe-time snapshot field: concept_digest

`concept_digest`:

```json
[
  {
    "ref_id": "concept:adverse_selection_as_design",
    "concept_key": "adverse_selection_as_design",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p142@18-p142@75",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 18
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 142,
            "char_offset": 75
          }
        },
        "quote": "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "我很欣赏选择我们的客户，他们头脑很清楚，也非常有责任感。他们非常懂我们的产品，他们看中的是我们的还款条件清晰简单。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:agency_cost_commoditization",
    "concept_key": "agency_cost_commoditization",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p73@56-p73@100",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 56
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 73,
            "char_offset": 100
          }
        },
        "quote": "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "参与竞拍的是给别人管理资金的基金经理，他们出手很阔绰，就像那个买了梵高画作的日本人一样。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "concept:annual_one_deal_discipline",
    "concept_key": "annual_one_deal_discipline",
    "concept_type": "concept",
    "source_refs": [
      {
        "source_span_id": "src:c1:p38@0-p38@97",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 38,
            "char_offset": 97
          }
        },
        "quote": "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "有的人做收购，请来一群投行员工，以为听他们的建议，就能做成一笔又一笔完美的收购。对于这种做法，我实在不敢苟同。即使是投资机会很多的时候，我们辛辛苦苦地研究和跟踪各个机会，一年也只能做成一笔收购。"
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

#### Probe-time snapshot field: thread_digest

`thread_digest`:

```json
[
  {
    "ref_id": "thread:ben_graham_trap_story",
    "thread_key": "ben_graham_trap_story",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p560@43-p560@84",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 560,
            "char_offset": 43
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 560,
            "char_offset": 84
          }
        },
        "quote": "答对最多的那个人，真会做的只有三道，其他都是蒙的。连蒙带猜，才勉强答对了一半多点。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p561@0-p565@79",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 561,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 565,
            "char_offset": 79
          }
        },
        "quote": "也许大多数储贷机构的高管定力很强，能不为所动。反正格雷厄姆设置陷阱，让我和沃伦·巴菲特上当，我们是没逃过去。好在本·格雷厄姆是个天才，在我们遇到的人中，很少有像他那么聪明的。另外，我们很清楚自己的不足，很清楚有很多事我们做不到，所以我们谨小慎微地留在我们的\"能力圈\"之中。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "答对最多的那个人，真会做的只有三道，其他都是蒙的。连蒙带猜，才勉强答对了一半多点。",
      "也许大多数储贷机构的高管定力很强，能不为所动。反正格雷厄姆设置陷阱，让我和沃伦·巴菲特上当，我们是没逃过去。好在本·格雷厄姆是个天才，在我们遇到的人中，很少有像他那么聪明的。另外，我们很清楚自己的不足，很清楚有很多事我们做不到，所以我们谨小慎微地留在我们的\"能力圈\"之中。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:humility_through_success_tension",
    "thread_key": "humility_through_success_tension",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p76@0-p76@140",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 76,
            "char_offset": 140
          }
        },
        "quote": "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      },
      {
        "source_span_id": "src:c1:p82@0-p82@102",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 82,
            "char_offset": 102
          }
        },
        "quote": "清楚自己能力的大小，这个品质应该不能说是'谦卑'。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      }
    ],
    "sample_quotes": [
      "我这一辈子，没遇到一个人说我谦卑。我非常欣赏谦卑这种品格，但我算不上一个谦卑的人。我周围有些人和我一样，他们也不谦卑。创建了内布拉斯加家具城（Nebraska Furniture Mart）的B夫人，她可不谦卑。她是个商业头脑特别强的人，但是她不谦卑。汤姆·墨菲也不是个谦卑的人。",
      "清楚自己能力的大小，这个品质应该不能说是'谦卑'。"
    ],
    "rationale": "",
    "projection_role": "current_support",
    "support_status": "source_backed",
    "current_support": true,
    "lineage_only": false,
    "projection_warning": ""
  },
  {
    "ref_id": "thread:munger_market_timing_record",
    "thread_key": "munger_market_timing_record",
    "thread_type": "thread",
    "source_refs": [
      {
        "source_span_id": "src:c1:p6@0-p10@64",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 6,
            "char_offset": 0
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 10,
            "char_offset": 64
          }
        },
        "quote": "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
        "role": "support",
        "resolution": {
          "status": "fallback_unit_span",
          "method": "quote_not_found",
          "match_count": 0
        }
      },
      {
        "source_span_id": "src:c1:p249@43-p249@153",
        "source_span": {
          "start_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 43
          },
          "end_cursor": {
            "chapter_id": 1,
            "chapter_ref": "Full Content",
            "paragraph_index": 249,
            "char_offset": 153
          }
        },
        "quote": "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。",
        "role": "support",
        "resolution": {
          "status": "matched",
          "method": "exact_text",
          "match_count": 1
        }
      }
    ],
    "sample_quotes": [
      "芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。从后视镜角度我们知道，就在大约半年后的1987年10月19日，美国股市遭遇\"黑色星期一\"，道指狂泻508点，单日跌幅超过20%。",
      "所罗门兄弟公司的信用评级是A。我们的本金有保证，所罗门将在规定日期赎回我们购买的优先股。我们相当于向一家信用评级为A的公司发放了一笔贷款，还获得了分享股价上升收益的额外好处。我们很欣赏所罗门的管理层，特别是约翰·古弗兰。"
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

#### Probe-time snapshot field: reflective_digest

`reflective_digest`:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

#### Probe-time snapshot field: source_ref_digest

`source_ref_digest`:

```json
[
  {
    "source_span_id": "src:c1:p4@0-p4@172",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 4,
        "char_offset": 172
      }
    },
    "quote": "1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p23@0-p23@57",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 23,
        "char_offset": 57
      }
    },
    "quote": "好在我们还有和迪克·罗森塔尔一样的人才，我们的董事会中还有蒂施家族的成员。蒂施家族人才济济，都是脚踏实地的投资者。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p32@0-p32@53",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 32,
        "char_offset": 53
      }
    },
    "quote": "西科金融的资产质量非常让人放心。目前，我们手中掌握着大量富余的资产，只是找不到好机会，没地方配置这些资产。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p33@0-p33@62",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 33,
        "char_offset": 62
      }
    },
    "quote": "我们把大量资产攥在手里，这是现在，不意味着永远。真有人拿枪顶着我的脑袋，逼我把这些钱投出去，迫不得已，我也能把这些钱投出去。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p41@142-p41@181",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 142
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 41,
        "char_offset": 181
      }
    },
    "quote": "现在股市里好的投资机会没了，收购也很难做，两条路都不好走了，我们只能采取守势。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p91@40-p91@105",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 40
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 91,
        "char_offset": 105
      }
    },
    "quote": "1987年合并净运营收益（不计投资收益）为1661.2万美元，每股2.33美元；合并净收益为1521.3万美元，每股2.14美元。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p112@0-p112@61",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 0
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 112,
        "char_offset": 61
      }
    },
    "quote": "你问我，西科的保险业务这几年的综合成本率如何？我估计，从我们签署合作协议起的四年里，我们的综合成本率大概是104、105。",
    "role": "support",
    "resolution": {
      "status": "matched",
      "method": "exact_text",
      "match_count": 1
    }
  },
  {
    "source_span_id": "src:c1:p139@36-p139@85",
    "source_span": {
      "start_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 36
      },
      "end_cursor": {
        "chapter_id": 1,
        "chapter_ref": "Full Content",
        "paragraph_index": 139,
        "char_offset": 85
      }
    },
    "quote": "从表面上看，我们的利差低于平均水平。从目前的情况看，与我们自身相比，我们的利差已经比过去高了很多。",
    "role": "support",
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
- judge reason: The snapshot retains several well-sourced concrete items (Wesco's three subsidiaries, asset deployability stance, Ben Graham trap story, humility/competence tension) with accurate quotes and source citations. However, it misses significant structural material from the source: the '形势比人强' (form overpowers people) thesis, which is explicitly identified as the organizing theme of the 1989 meeting and appears again in 1990, receives only peripheral mention. The detailed S&L crisis analysis presented in two major appendices (covering regulatory failures, junk bond risks, and policy recommendations) is barely represented in the digest, yet this is central content spanning both 1989 and 1990. The risk-arbitrage discussion from 1990, which explicitly connects back to Graham's methodology, is thin. The snapshot preserves individual years well but does not clearly maintain the cross-year doctrinal continuity—Munger's consistent emphasis on conservative capital allocation, the circle of competence, and the '宁要模糊的正确，不要精确的错误' philosophy—across all four annual letters.

#### Manual Check
- Open probe snapshot `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_eval1_long_span_post_slice8h_20260519_mangge/outputs/mangge_zhi_dao_private_zh__segment_1/attentional_v2/_mechanisms/attentional_v2/exports/memory_quality_probe_snapshots.json` and inspect `snapshots[4]`.
- Compare against source window paragraph/sentence orientation in `source_windows_readable/mangge_zhi_dao_private_zh__segment_1.md`.

## Scoring Interpretation

This section explains how the trace above becomes the Eval-1 scores for this window.

### Selective Legibility

- Formula used by the run report: `(exact_match + focused_hit) / note_case_count = (2 + 7) / 25 = 0.3600`.
- Incidental cover count `0` is visible support, not recall credit.
- Miss count `16` means the reaction timeline either did not produce a strict source-overlap candidate for the note target or the judge rejected the admitted candidate.
- Unlocatable reaction count `0` is diagnostic only and never becomes a match.

### Memory Quality

- Window MQ is the average of the five probe-time overall scores: 4, 3.25, 2.25, 2.75, 3.25 -> `3.10`.
- The probe state sections above show what the mechanism had available at scoring time; final runtime state is not substituted for probe-time evidence.

### Callback / FVI

- Reaction audit reviewed `270` visible reactions: `43` grounded, `13` weak, `0` FVI, `214` local-only.
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
