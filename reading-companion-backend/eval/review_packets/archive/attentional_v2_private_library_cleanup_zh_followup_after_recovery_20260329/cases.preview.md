# Revision/Replacement Packet `attentional_v2_private_library_cleanup_zh_followup_after_recovery_20260329`

This packet was generated automatically from cases whose current `benchmark_status` requires another hardening round.

## Dataset
- dataset_id: `attentional_v2_private_library_excerpt_zh_v2`
- family: `excerpt_cases`
- language_track: `zh`
- version: `2`
- targeted_statuses: `needs_revision|needs_replacement|needs_revision|needs_replacement`

## Review Actions
- `keep`
- `revise`
- `drop`
- `unclear`

## Confidence
- `high`
- `medium`
- `low`

## 1. `zouchu_weiyi_zhenliguan_private_zh__8__seed_1`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `走出唯一真理观`
- author: `陈嘉映`
- chapter: `思想增益元气` (`8`)
- question_ids: ``
- phenomena: ``
- selection_reason: The excerpt discusses when to read philosophy versus protecting one's 元气 (vital energy), using Bernard Williams' critique of over-reflection as context. The core advice centers on reading philosophy based on whether it strengthens or depletes one's energy.
- judge_focus: Does the excerpt clearly convey the relationship between philosophical reading and personal energy management? Is the Bernard Williams reference on over-reflection explicitly connected to the advice about protecting 元气, or does it appear as a separate question?
- latest_review_action: `revise`
- latest_problem_types: `weak_excerpt|ambiguous_focus`
- latest_revised_bucket: `philosophy_energy_management`
- latest_notes: The excerpt combines two distinct elements—advice about reading philosophy based on 元气 and a Bernard Williams quote on over-reflection—that are only implicitly, not explicitly, connected. The Williams reference is embedded in a questioner's quoted question rather than serving as the author's direct support for the energy advice. To strengthen the excerpt, either remove the Williams reference entirely or add a bridging sentence that explicitly links over-reflection to 元气 depletion. Alternatively, restructure the excerpt to show the author's own connection between excessive philosophical reflection and energy loss.

```text
要是快扛不住了，就别读哲学了，去看娱乐节目什么的。
不说变得强大吧，说保护、增益元气。
你觉得读哲学增益了整个人的元气，就读，觉得气短了，就放下。
谢玉问：2015年您在和周濂老师访谈里说：“伯纳德·威廉斯认为，这种无所不在的反思会威胁和摧毁很多东西，因为它会把原本厚实的东西变得薄瘠。
我们是否能够以及在什么程度上以何种方式不陷入过度反思，这是当代生活面临的一个很重要的问题。”
```

## 2. `kangxi_hongpiao_private_zh__12__seed_2`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `康熙的红票：全球化中的清朝`
- author: `孙立天`
- chapter: `消除奴籍` (`12`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `ambiguous_focus|text_noise`
- latest_revised_bucket: ``
- latest_notes: This case must be dropped after two review cycles with identical findings. Critical metadata fields remain entirely empty (case_title, question_ids, phenomena, selection_reason, judge_focus), making the case impossible to evaluate as a benchmark unit. The [97] reference artifact also requires removal. While the historical excerpt about Catholic priests entering Qing service as enslaved war captives is coherent, no analytical question or bucket rationale has been defined, leaving bucket assignment arbitrary. Without defined scope, this case cannot test any specific reading mechanism.

```text
[97]
二位神父在战场上捡回性命后，被归入奴籍，挂入了清朝八旗中。
他们归顺清朝统治的轨迹和汤若望神父完全不一样。
汤若望跟许多降清的汉臣轨迹相似，改朝换代后又直接成了新朝廷的大臣。
而二位神父是以战俘奴隶身份进入到满人世界中的。
```

## 3. `kangxi_hongpiao_private_zh__27__seed_1`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `康熙的红票：全球化中的清朝`
- author: `孙立天`
- chapter: `功不可没的南怀仁` (`27`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `weak_excerpt|ambiguous_focus|too_easy`
- latest_revised_bucket: ``
- latest_notes: Despite the primary reviewer's attempt to salvage this case with a proposed 'historical_reliability' framing, the excerpt remains fundamentally weak. The critical analytical point—that Tong Guoqi was easily accepted after claiming only minor involvement—does not appear in the excerpt itself, creating a disconnect between the suggested interpretation and the actual source text. Multiple review layers consistently identify this as descriptive background rather than a benchmark-quality case with an embedded question or analytical task. The proposed revised metadata (selection_reason, judge_focus) cannot compensate for an excerpt that lacks the evidentiary substance to support the intended reasoning chain.

```text
佟国器是佟氏家族经营江南的代表人物，历任江南各省督抚。
而他受1665年历狱影响，被迫回京，接受关于他和传教士关系的审讯。
现存历狱档案中，还有对他的审讯记录。
佟国器在江南和传教士交好，当时是天下共知的事。
他为传教士修教堂，给他们的书写序言，都是公开进行的。
```
