# Subsegment Benchmark Report: subsegment_benchmark_v1

## Comparison Target

- `heuristic_only` vs `llm_primary` on curated subsegment benchmark cases

## Rubric

- Plan-level: self-containedness, minimal sufficiency, one primary reading move.
- Downstream: reaction focus, source-anchor quality, coverage of meaningful turns/definitions/callbacks, coherence after merge.

## Aggregate Findings

- Cases evaluated: 3
- Core cases: 3
- Audit cases: 0
- `llm_primary` fallback rate: 33.33%
- `llm_primary` invalid-plan rate: 33.33%
- `llm_primary` timeout/failure rate: 100.00%
- `heuristic_only` timeout/failure rate: 100.00%
- Average unit count (`heuristic_only`): 1.67
- Average unit count (`llm_primary`): 3.00

### Plan-Level Pairwise Winners

- `llm_primary`: 1
- `tie`: 2

### Downstream Pairwise Winners

- `heuristic_only`: 1
- `llm_primary`: 1
- `tie`: 1

## Representative LLM Wins

- `core_c1_02` 7.4: B (llm_primary) 更全面地覆盖了段落的关键要点：它捕捉了'整个持续时间'的谈判、关系类型导致的公开程度差异、以及规则与法律的核心区分。A (heuristic_only) 虽然聚焦于隐蔽性悖论这一有价值的切入点，但遗漏了规则/法律区别这一贯穿段落后半部分的核心内容，且其reason codes显示低归属置信度和弱关联性，表明其分析深度不足。

## Representative Heuristic Wins

- `core_c1_01` 7.3: 候选A覆盖了更多有意义的核心点：双向性要求、不可交易物品的张力、fan-idol例子引出的不对称关系讨论、冷漠作为默认假设、以及与Mauss《礼物》的理论对话。相比之下B虽然也有质量不错的反应，但遗漏了关键的反面案例（victim-mugger）和对'不可交易物品'的系统性质疑。A的反应轨迹更能体现阅读过程中的思维张力与多维思考。

## Known Caveats

- This benchmark is intentionally small and curated for attribution, not broad corpus coverage.
- This run covered 3 of 24 tracked benchmark cases.
- The v1 dataset is dominated by repo-tracked sections from one book plus one fixture sanity case.
- Search is disabled during downstream section runs so the comparison stays focused on subsegment slicing rather than curiosity expansion.
