# 实验与评分总表

主表每个评分范围只显示最新快照；通过率 = 通过数 / 已判数。含原文的证据仅存本机忽略目录。
DIAG-001 的 Highlight 数字保留用于追溯；现有决策仍只依据 Note。

**所有者补充核对 · 2026-11-11**（`Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`）

所有者核对上述 3 条 Highlight 后确认：不是标准漂移，是规则未写明加一次误操作。

| 评分／单元 | 产物配置 | 尺子／评分者 | Note 通过率 | Highlight 通过率 | 状态 |
|---|---|---|---|---|---|
| [第一批开放编码](#q1-score-baseline-open-s001)<br>67 单元 | GPT-6 Luna / medium | 开放编码<br>weijiang | 包法利：3/37（8.11%）<br>人类简史：5/47（10.64%） | 包法利：1/3（33.33%）<br>人类简史：15/23（65.22%） | 已完成 |
| [DIAG-001 混合盲标](#q1-score-diag-open-s001)<br>16 单元 | GPT-6 Luna / medium<br>GPT-6 Sol / high | 开放编码<br>weijiang | A1：4/21（19.05%）<br>B：21/30（70.00%） | A1：9/10（90.00%）<br>B：15/20（75.00%） | 已完成 |
| [DIAG-001 q1-v0 重判](#q1-score-diag-q1v0-s001)<br>16 单元 | GPT-6 Luna / medium<br>GPT-6 Sol / high | q1-v0<br>q1-v0.form.v1<br>weijiang | A1：待标（共 21）<br>B：待标（共 30） | A1：待标（共 10）<br>B：待标（共 20） | 待标 |

以下小节包含哈希、标注时间、分母、可比范围及合并后的实验日志。

<a id="q1-score-baseline-open-s001"></a>
<details>
<summary>第一批开放编码 · Q1-SCORE-BASELINE-OPEN-S001</summary>

- 实验：`Q1-BASELINE-001`；范围：67 单元，[dev-v1.json](unit-sets/dev-v1.json)，SHA-256 `c25a0396c99dc9db4bb25f9e7958b975142cfd11d79834f13cbe92e1afb7a680`。
- 评分者：human / weijiang；尺子：open_coding，表单：无。
- rubric SHA-256：`None`；表单 SHA-256：`None`。
- 登记：2026-11-10T12:09:47.326104+00:00；评分快照状态：completed；会话：`None`。
- 盲化：原运行第一批开放编码，未采用混合盲标。

- 包法利：**gpt-6-luna / medium**，run `q1_full_bovary_d414030_20261103`；产物 SHA-256 `5e80fafa3ad30afa88fbf4c883b75cf34732324c90e954803c590411d58c9b17`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：reconstructed_after_run。
  - prompt `attentional_v2.ingest.v19` / `c44b671f55ee34e24c849418d9bc720921108999d4a9a40e3b0d45223355fa16`；证据：reconstructed_after_run。
  - prompt `attentional_v2.chapter_zone.v2` / `ee0879bdd8025d4b4b969179dd0c14b751e5cdc67d9f880debd8f6212df67a51`；证据：reconstructed_after_run。
  - 实际请求哈希：0 条；历史请求哈希不可用。
- 人类简史：**gpt-6-luna / medium**，run `q1_full_sapiens_d414030_20261103`；产物 SHA-256 `198e72038ecbf318d555a28bfe3540c41548cc7c994ac7acad1aacc78edb4dd5`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：reconstructed_after_run。
  - prompt `attentional_v2.ingest.v19` / `c44b671f55ee34e24c849418d9bc720921108999d4a9a40e3b0d45223355fa16`；证据：reconstructed_after_run。
  - prompt `attentional_v2.chapter_zone.v2` / `ee0879bdd8025d4b4b969179dd0c14b751e5cdc67d9f880debd8f6212df67a51`；证据：reconstructed_after_run。
  - 实际请求哈希：0 条；历史请求哈希不可用。

| 产物 | 类型 | 通过/已判 | 产物总数 | 不过 | 未判 |
|---|---|---|---:|---:|---:|
| 包法利 | Highlight | 1/3（33.33%） | 3 | 2 | 0 |
| 包法利 | Note | 3/37（8.11%） | 37 | 34 | 0 |
| 人类简史 | Highlight | 15/23（65.22%） | 23 | 8 | 0 |
| 人类简史 | Note | 5/47（10.64%） | 47 | 42 | 0 |

逐条款不过数：开放编码不适用；待标条目不计入条款统计。多个条款可重叠。

标注快照：
- [judgments.snapshot.jsonl](../state/scorings/q1-initial-20261110/baseline/eb022649ceece1a1829d6d61f4a4d4535cdad4e4713050bab1db78afc5925ed6/judgments.snapshot.jsonl)；截止 revision **303**；SHA-256 `c4ab59d2e246bb9f7bfa97c0d571688762d5626e7b95a5b1bd93c0bf8c7b94f3`；原标注时间 ['2026-11-04T13:09:35.706Z', '2026-11-07T03:22:05.096Z']；工具版本 q1-annotator/1.1, q1-annotator/1.2, q1-annotator/1.4, q1-annotator/1.5, q1-annotator/1.7。
- [judgments.snapshot.jsonl](../state/scorings/q1-initial-20261110/baseline/3015bb621409111746f8c2074f15981dc2a539e4354bfee2c3c5b0a8caafbb90/judgments.snapshot.jsonl)；截止 revision **302**；SHA-256 `d6e8bb2819389e0223be8cab48e04706e9977dda03e7b29d2ae20af876a88fc2`；原标注时间 ['2026-11-07T05:53:57.128Z', '2026-11-07T14:09:00.418Z']；工具版本 q1-annotator/1.7。

可比性：
- 无前序评分。

复算：`python scripts/q1_scoring.py --evidence`；代码提交 `534870911cce55f59c62d4c9db0fcb0664b15532`；[私有统计报告](../state/scorings/q1-initial-20261110/Q1-SCORE-BASELINE-OPEN-S001.report.json)。

本实验日志合并：`Q1-BASELINE-001`。

</details>

<a id="q1-score-diag-open-s001"></a>
<details>
<summary>DIAG-001 混合盲标 · Q1-SCORE-DIAG-OPEN-S001</summary>

- 实验：`Q1-DIGEST-DIAG-001`；范围：16 单元，[diag-001.json](unit-sets/diag-001.json)，SHA-256 `a991dbcfeb9bf9fe09282d04de86b14ab86da97fa86ba6d04bb7e1875c357db4`。
- 评分者：human / weijiang；尺子：open_coding，表单：无。
- rubric SHA-256：`None`；表单 SHA-256：`None`。
- 登记：2026-11-10T12:09:47.351586+00:00；评分快照状态：completed；会话：`None`。
- 盲化：评分截点在揭晓之前；既往看过原运行产物，且期间恢复了类型提示。Highlight 标准有漂移，决策仅使用 Note。

- A1：**gpt-6-luna / medium**，run `q1_digest_fixed_history_20261108_A1`；产物 SHA-256 `f4a864630f41d6385244bd81332afaa07e7013cdd5f404553a99c96a100aa81a`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：runtime_recorded。
  - 实际请求哈希：16 条；逐请求对应关系见评分账。
- B：**gpt-6-sol / high**，run `q1_digest_fixed_history_20261108_B`；产物 SHA-256 `3b57de54a2c0735cd32942a80df16a7109660363f1e062f35c764a538c4f7262`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：runtime_recorded。
  - 实际请求哈希：16 条；逐请求对应关系见评分账。

| 产物 | 类型 | 通过/已判 | 产物总数 | 不过 | 未判 |
|---|---|---|---:|---:|---:|
| A1 | Highlight | 9/10（90.00%） | 10 | 1 | 0 |
| A1 | Note | 4/21（19.05%） | 21 | 17 | 0 |
| B | Highlight | 15/20（75.00%） | 20 | 5 | 0 |
| B | Note | 21/30（70.00%） | 30 | 9 | 0 |

逐条款不过数：开放编码不适用；待标条目不计入条款统计。多个条款可重叠。

标注快照：
- [judgments.snapshot.jsonl](../state/scorings/q1-initial-20261110/diag-open/judgments.snapshot.jsonl)；截止 revision **313**；SHA-256 `28fff5eb3b0269d69c46d46b66f67f654dcc1ac6703e07edd4cbec4f627235b5`；原标注时间 ['2026-11-08T07:12:42.585Z', '2026-11-08T09:23:29.444Z']；工具版本 q1-annotator/2.0, q1-annotator/2.1, q1-annotator/2.2。

可比性：
- `Q1-SCORE-BASELINE-OPEN-S001`：descriptive_only；67 单元与其 16 单元子集；生成产物不同，不能直接把通过率差归因于判定标准或模型。

复算：`python scripts/q1_scoring.py --evidence`；代码提交 `534870911cce55f59c62d4c9db0fcb0664b15532`；[私有统计报告](../state/scorings/q1-initial-20261110/Q1-SCORE-DIAG-OPEN-S001.report.json)。

本实验日志合并：`Q1-DIGEST-DIAG-001` → `Q1-DIGEST-DIAG-001-CONTINUATION` → `Q1-DIGEST-DIAG-001-PREREG-001` → `Q1-DIGEST-DIAG-001-REVEAL-001` → `Q1-DIGEST-DIAG-001-LOCATION-001` → `Q1-DIGEST-DIAG-001-CLOSE-001` → `Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`。

**所有者补充核对 · 2026-11-11**（`Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`）

所有者核对上述 3 条 Highlight 后确认：不是标准漂移，是规则未写明加一次误操作。

- 包法利 `u000031`：第一批的理由评价的是附带的 Note。
- 人类简史 `u000237`：第一批因遗漏相邻句子判不过，按 q1-v0 起应判过并记漏标。
- 人类简史 `u000144`：第一批判不过是误操作。

<details>
<summary>原收尾记录（历史原文；后续核对见上文）</summary>

DIAG-001 的 A1/B 混合盲标已完成，结果引用关联评分账。PREREG-001 登记的通过标准为：Highlight 选中本段值得停下来的文字且范围完整；Note 提供原文未直接说出的东西，不是语文阅读理解，且准确、与锚点相关。登记的决策指标是 B 相对 A1 的 Note 通过率差：高 25 个百分点以上为明显好，10 个点以内为无差别，介于两者之间则盲标 A2 测噪声后再判。

本次 A1 为 4/21（19.05%），B 为 21/30（70%），B 高 50.95 个百分点，落入“明显好”一侧，触发该预登记判断，不触发中间区间的 A2 盲标测噪声步骤。

在同一 prompt、固定历史上下文的这批诊断中，B 明显更好。这不支持“质量问题主要来自 prompt”，说明模型配置是重要杠杆；但 B 同时更换了模型与推理强度，两者未拆分，prompt 的作用本实验没有检验。该判断限于这批 dev 样本，并保留既往产物暴露及标注展示变化的局限。Highlight 的判定标准在本轮标注中有过漂移，本次 Highlight 通过率不用于任何结论，只有 Note 通过率作为决策依据。

本轮模型对比暂停，后续使用 GPT-6 Luna medium 迭代；B 的现有产物作为参照上限，这是工作参考定位，不是已证明的能力上限。B 实际使用 GPT-6 Sol high，而非 GPT-6.1。DIAG-001 诊断阶段收尾，q1-v0 重判作为独立评分继续登记。

</details>

</details>

<a id="q1-score-diag-q1v0-s001"></a>
<details>
<summary>DIAG-001 q1-v0 重判 · Q1-SCORE-DIAG-Q1V0-S001</summary>

- 实验：`Q1-DIGEST-DIAG-001`；范围：16 单元，[diag-001.json](unit-sets/diag-001.json)，SHA-256 `a991dbcfeb9bf9fe09282d04de86b14ab86da97fa86ba6d04bb7e1875c357db4`。
- 评分者：human / weijiang；尺子：q1-v0，表单：q1-v0.form.v1。
- rubric SHA-256：`3ed0c44ab82b1a95802eb669717570a282169200b45faec1a090706ab1bd12fa`；表单 SHA-256：`40a97086fd03f48fc2df997c6ce7bbdb58e2333fc3a741ad082434ac196b1586`。
- 登记：2026-11-10T12:09:47.370476+00:00；评分快照状态：pending；会话：`1319f550-aa0a-4081-bbc1-376340958b1b`。
- 盲化：已揭晓后的匿名重判；先完成并保存才允许查看旧判断，后续修订记录暴露状态。

- A1：**gpt-6-luna / medium**，run `q1_digest_fixed_history_20261108_A1`；产物 SHA-256 `f4a864630f41d6385244bd81332afaa07e7013cdd5f404553a99c96a100aa81a`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：runtime_recorded。
  - 实际请求哈希：16 条；逐请求对应关系见评分账。
- B：**gpt-6-sol / high**，run `q1_digest_fixed_history_20261108_B`；产物 SHA-256 `3b57de54a2c0735cd32942a80df16a7109660363f1e062f35c764a538c4f7262`。
  - prompt `attentional_v2.digest.v24` / `b20654a196efd6d83e6e8411f580c9bb119054878e6de74b8575ccfc3a33571e`；证据：runtime_recorded。
  - 实际请求哈希：16 条；逐请求对应关系见评分账。

| 产物 | 类型 | 通过/已判 | 产物总数 | 不过 | 未判 |
|---|---|---|---:|---:|---:|
| A1 | Highlight | 待标（共 10） | 10 | 0 | 10 |
| A1 | Note | 待标（共 21） | 21 | 0 | 21 |
| B | Highlight | 待标（共 20） | 20 | 0 | 20 |
| B | Note | 待标（共 30） | 30 | 0 | 30 |

逐条款不过数：开放编码不适用；待标条目不计入条款统计。多个条款可重叠。
- A1 Highlight：待标
- A1 Note：待标
- B Highlight：待标
- B Note：待标

标注快照：
- [judgments.jsonl](../state/scorings/q1-initial-20261110/diag-q1v0/judgments.jsonl)；截止 revision **0**；SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；原标注时间 [None, None]；工具版本 尚无标注。

可比性：
- `Q1-SCORE-DIAG-OPEN-S001`：same_outputs_different_rubric；相同 81 条产物，尺子和表单不同；已知揭晓结果，不能当作独立盲标。

复算：`python scripts/q1_scoring.py --evidence`；代码提交 `534870911cce55f59c62d4c9db0fcb0664b15532`；[私有统计报告](../state/scorings/q1-initial-20261110/Q1-SCORE-DIAG-Q1V0-S001.report.json)。

本实验日志合并：`Q1-DIGEST-DIAG-001` → `Q1-DIGEST-DIAG-001-CONTINUATION` → `Q1-DIGEST-DIAG-001-PREREG-001` → `Q1-DIGEST-DIAG-001-REVEAL-001` → `Q1-DIGEST-DIAG-001-LOCATION-001` → `Q1-DIGEST-DIAG-001-CLOSE-001` → `Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`。

**所有者补充核对 · 2026-11-11**（`Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001`）

所有者核对上述 3 条 Highlight 后确认：不是标准漂移，是规则未写明加一次误操作。

- 包法利 `u000031`：第一批的理由评价的是附带的 Note。
- 人类简史 `u000237`：第一批因遗漏相邻句子判不过，按 q1-v0 起应判过并记漏标。
- 人类简史 `u000144`：第一批判不过是误操作。

<details>
<summary>原收尾记录（历史原文；后续核对见上文）</summary>

DIAG-001 的 A1/B 混合盲标已完成，结果引用关联评分账。PREREG-001 登记的通过标准为：Highlight 选中本段值得停下来的文字且范围完整；Note 提供原文未直接说出的东西，不是语文阅读理解，且准确、与锚点相关。登记的决策指标是 B 相对 A1 的 Note 通过率差：高 25 个百分点以上为明显好，10 个点以内为无差别，介于两者之间则盲标 A2 测噪声后再判。

本次 A1 为 4/21（19.05%），B 为 21/30（70%），B 高 50.95 个百分点，落入“明显好”一侧，触发该预登记判断，不触发中间区间的 A2 盲标测噪声步骤。

在同一 prompt、固定历史上下文的这批诊断中，B 明显更好。这不支持“质量问题主要来自 prompt”，说明模型配置是重要杠杆；但 B 同时更换了模型与推理强度，两者未拆分，prompt 的作用本实验没有检验。该判断限于这批 dev 样本，并保留既往产物暴露及标注展示变化的局限。Highlight 的判定标准在本轮标注中有过漂移，本次 Highlight 通过率不用于任何结论，只有 Note 通过率作为决策依据。

本轮模型对比暂停，后续使用 GPT-6 Luna medium 迭代；B 的现有产物作为参照上限，这是工作参考定位，不是已证明的能力上限。B 实际使用 GPT-6 Sol high，而非 GPT-6.1。DIAG-001 诊断阶段收尾，q1-v0 重判作为独立评分继续登记。

</details>

</details>

<details>
<summary>历史评分快照（0 条）</summary>

暂无被后续快照替代的评分。

</details>

由 `scripts/q1_experiment_index.py` 生成，请勿手工编辑。
