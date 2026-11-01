# Read XML Prompt Full Active Diagnostic Post-run Report v0

## Answer First

The full active diagnostic completed successfully at the machine-run level. Five registered pipeline jobs ran one LongSpan producer each with `ATTENTIONAL_V2_READ_PROMPT_ASSEMBLY_MODE=xml`, then launched the corresponding Lane A user-level selective reuse shard. All five jobs finished with exit code `0`; all ten run dirs emitted `summary/aggregate.json`, `summary/report.md`, and `summary/llm_usage.json`; strict LLM health passed for all ten run dirs with `0` fallback-backed evidence.

This report supports one narrow conclusion: the opt-in XML Read prompt assembly path can run the full active diagnostic surface end to end, and the new `recent_reading_memory` store is being populated in fresh full-window reading. It does not prove product quality, does not update the evidence catalog, and does not promote Long Span vNext to formal benchmark authority.

## Run Evidence Map

Parent ledger run: `attentional_v2_read_prompt_xml_full_active_diagnostic_20260526`

Task: `TASK-SECOND-READER-READ-PROMPT-XML-FULL-ACTIVE-DIAGNOSTIC-20260526`

Mode: diagnostic only, `attentional_v2` only, no `iterator_v1`, no evidence catalog update.

| Window | Lane B LongSpan producer | Lane A reuse shard | Job id |
|---|---|---|---|
| `huochu` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_huochu` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_user_level_reuse_diagnostic_20260526_huochu` | `bgjob_read_prompt_xml_full_diagnostic_20260526_huochu` |
| `mangge` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_mangge` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_user_level_reuse_diagnostic_20260526_mangge` | `bgjob_read_prompt_xml_full_diagnostic_20260526_mangge` |
| `nawaer` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_nawaer` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_user_level_reuse_diagnostic_20260526_nawaer` | `bgjob_read_prompt_xml_full_diagnostic_20260526_nawaer` |
| `value_of_others` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_value_of_others` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_user_level_reuse_diagnostic_20260526_value_of_others` | `bgjob_read_prompt_xml_full_diagnostic_20260526_value_of_others` |
| `xidaduo` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_long_span_diagnostic_20260526_xidaduo` | `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_read_prompt_xml_user_level_reuse_diagnostic_20260526_xidaduo` | `bgjob_read_prompt_xml_full_diagnostic_20260526_xidaduo` |

The run ledger has been updated to `review_pending` for the parent and all ten child runs.

## Completion And Health

Job registry result: each of the five pipeline job records reports `status=completed` and `exit_code=0`.

LLM health result: `scripts/check_eval_llm_health.py` returned `status=ok` for all ten run dirs. Across the five LongSpan producers and five Lane A reuse shards, `summary/llm_usage.json` reports `1256` requests, `1256` successes, `0` errors, and `46` retries. The strict health checker found `0` fallback-backed evidence.

| Window | Read units | Recent Memory entries | RM ops | ops with reason | MQ avg | Reactions audited | Lane A notes |
|---|---:|---:|---:|---:|---:|---:|---:|
| `huochu` | 97 | 133 | 133 | 0 | 4.05 | 116 | 40 |
| `mangge` | 199 | 239 | 239 | 0 | 3.50 | 221 | 25 |
| `nawaer` | 32 | 35 | 35 | 0 | 3.70 | 44 | 23 |
| `value_of_others` | 45 | 70 | 70 | 0 | 3.90 | 53 | 94 |
| `xidaduo` | 164 | 205 | 205 | 0 | 3.85 | 193 | 20 |

Aggregate diagnostic totals: `537` Read units, `682` Recent Reading Memory entries, `25` MQ probes, `627` audited visible reactions, and `202` Lane A note cases.

## XML Assembly Verification

The diagnostic did not merely set an environment variable; the fresh artifacts show the XML Read path was actually active. Each LongSpan producer wrote `_mechanisms/attentional_v2/internal/prompt_manifests/read_unit.json` with:

```json
{
  "prompt_version": "attentional_v2.read.xml.v1",
  "prompt_assembly": {
    "mode": "xml",
    "spec_id": "attentional_v2.read_unit.xml.v1",
    "output_contract": "read_unit_xml_json_v1"
  }
}
```

That confirms the new XML assembly path was exercised in fresh reading outputs. This report does not yet claim the XML context structure is optimal; it only records that the opt-in path is executable and produced complete artifacts.

## Recent Reading Memory Snapshot

Recent Reading Memory formation is clearly active in full-window reading. Every accepted Recent Memory write was an append to `recent_reading_memory`; none used an operation-level `reason`, matching the current design that `memory_text` itself is the retained content.

Examples from final runtime stores:

- `huochu`: `本书定位为个人见证而非历史陈述，聚焦于小集中营中普通囚徒（无特权、无袖箍标记）的日常磨难与死亡，而非名人或烈士的故事。囚头（享有特权的囚徒职能人员）有时比纳粹看守更为残忍，书中将以这些普通囚徒的经历为核心。`
- `mangge`: `芒格在1987年股东会上表达了对市场环境的谨慎判断：好投资和收购机会缺乏，市场环境不妙。他同时承认自己无法预测未来，对累积起来的风险感到不安。这与前文具体财务数据形成对照，呈现出一种防御性的投资态度。`
- `nawaer`: `作者通过推特风暴引出核心理念体系，明确三个核心定义的区分：财富是"在你睡觉时仍能为你赚钱的资产"，金钱是"转换时间和财富的方式"，地位是"社会等级体系中的位置"。这三个定义共同构成了后续所有原则的认知基础。`
- `value_of_others`: `People devise three general approaches to the problem of others: (1) move against—taking by force, skill, or guile; (2) move away—eliminating desire or dependence; (3) move toward—joining into larger units by giving or promising what others want. The third is the most common and is called prosocial.`
- `xidaduo`: `开篇人物：悉达多，俊美的婆罗门之子，年轻的鹰隼，与同是婆罗门之子的乔文达为友。在河岸、树荫、屋舍阴凉中成长。已习得辩论、参禅、冥想，无声念诵'唵'，体认内在不朽的阿特曼，与宇宙合一。父亲对其期望极高，盼其成为伟大的贤士和僧侣，婆罗门中的王。`

Initial interpretation: the store is not empty, not decorative, and not just a prompt artifact. It is being written to runtime state as source-facing near-term semantic memory. The examples also show that entries are often useful for future reading, but a deeper reviewer pass is still needed to judge coverage, continuity, and whether the memory remains too summary-like or too abstract in some windows.

## Lane B Memory / Callback Diagnostic Snapshot

LongSpan ran 5 semantic probes per window, all using `memory_snapshot_basis=full_probe_time_memory_state` in `memory_quality_results.jsonl`.

| Window | MQ scores | MQ average |
|---|---|---:|
| `huochu` | `3.75, 4.75, 3.75, 3.75, 4.25` | 4.05 |
| `mangge` | `3.25, 4.00, 4.00, 2.75, 3.50` | 3.50 |
| `nawaer` | `3.75, 3.75, 2.75, 4.50, 3.75` | 3.70 |
| `value_of_others` | `4.75, 3.00, 4.00, 4.00, 3.75` | 3.90 |
| `xidaduo` | `3.50, 4.00, 3.75, 3.25, 4.75` | 3.85 |

Reaction audit labels:

| Window | local_only | grounded_callback | weak_callback | FVI |
|---|---:|---:|---:|---:|
| `huochu` | 96 | 4 | 16 | 0 |
| `mangge` | 158 | 39 | 24 | 0 |
| `nawaer` | 29 | 10 | 4 | 1 |
| `value_of_others` | 46 | 6 | 1 | 0 |
| `xidaduo` | 114 | 47 | 32 | 0 |

Aggregate reaction audit labels: `443` local-only, `106` grounded callbacks, `77` weak callbacks, and `1` false visible integration.

This suggests the XML prompt path did not break callback auditing or MQ scoring. It also suggests the new Recent Memory state is being seen by the MQ judge: for example, the `huochu` probe-1 judge reason explicitly cites `recent:c1:u0006:m1` and `recent:c1:u0023:m1` as retaining the three-stage prisoner-response framework and first-to-second-stage transition. However, the same reason notes an organization weakness: the framework is recorded as entries rather than woven into a durable concept/thread structure. That is consistent with the current architecture: Recent Memory formation is implemented, but Recent Memory-to-durable-memory consolidation is still deferred.

## Lane A Selective Legibility Snapshot

Lane A reuse shards completed over all 202 active note cases.

| Window | notes | exact | focused | incidental | miss | recall | unlocatable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `huochu` | 40 | 6 | 4 | 1 | 29 | 0.2500 | 0 |
| `mangge` | 25 | 5 | 10 | 2 | 8 | 0.6000 | 0 |
| `nawaer` | 23 | 9 | 2 | 3 | 9 | 0.4783 | 1 |
| `value_of_others` | 94 | 4 | 15 | 5 | 70 | 0.2021 | 0 |
| `xidaduo` | 20 | 1 | 4 | 0 | 15 | 0.2500 | 0 |

Totals: `202` note cases, `25` exact, `35` focused, `11` incidental, `131` miss, recall `0.3465`, and `1` unlocatable reaction diagnostic.

This should be treated as a diagnostic continuity check, not a formal comparison claim. The total recall matches the earlier Eval-1 aggregate at the rounded level, but label composition differs; dataset and run conditions are diagnostic, and this report does not claim improvement or regression.

## What This Supports

- The opt-in XML Read prompt assembly path can run the full active diagnostic scope end to end.
- Fresh reading artifacts confirm `prompt_assembly.mode=xml` and `prompt_version=attentional_v2.read.xml.v1`.
- Recent Reading Memory is being written as real runtime state, not just as a report-only projection.
- Read behavior remains executable enough to produce LongSpan MQ, reaction audit, and Lane A selective-legibility outputs across all five active windows.
- LLM health guardrails worked for this run: no fallback-backed evidence was admitted.

## What This Does Not Support

- It does not prove the XML prompt structure is better than the legacy prompt assembly.
- It does not prove product quality.
- It does not make Long Span vNext formal benchmark authority.
- It does not validate Recent Memory-to-durable-memory consolidation, because that node/design is not implemented yet.
- It does not authorize evidence catalog update.
- It does not show that `concept_registry` / `thread_trace` are now well-structured; in fact, MQ judge comments still point toward the need for a separate durable-memory consolidation design.

## Recommended Next Steps

1. Keep the diagnostic in `review_pending` until a human reviews the post-run report and selected raw artifacts.
2. Do a focused Recent Memory review on 2-3 windows before changing prompt assembly defaults. The high-level stats are healthy, but quality still depends on whether entries are faithful, continuous, and usable by the next Read step.
3. Continue the current design thread for durable memory, starting with `concept_registry`, because this run reinforces that Recent Memory can record rich near-term content but does not itself solve concept/thread organization.
4. Do not update `evidence_catalog.*` from this diagnostic unless explicitly approved after review.
5. Do not switch XML prompt assembly to default solely from this report; treat this as an executable-path validation plus raw evidence package.

## Validation Performed

Before this report:

- `scripts/check_background_jobs.py` showed no active jobs.
- All five pipeline job records showed `status=completed` and `exit_code=0`.
- All ten run dirs contained `summary/aggregate.json`, `summary/report.md`, and `summary/llm_usage.json`.
- `scripts/check_eval_llm_health.py` returned `status=ok` for all ten run dirs.
- `scripts/update_evaluation_run_ledger.py --check` passed after the run ledger was updated to `review_pending`.
- `node -e "JSON.parse(require('fs').readFileSync('docs/tasks/registry.json','utf8'))"` passed.
- `git diff --check` passed.
- Forbidden diff check for frontend and evidence catalog paths was empty.
