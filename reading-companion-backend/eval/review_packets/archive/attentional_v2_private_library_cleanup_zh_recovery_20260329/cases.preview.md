# Revision/Replacement Packet `attentional_v2_private_library_cleanup_zh_recovery_20260329`

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

## 1. `fooled_by_randomness_private_zh__19__seed_2`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `随机漫步的傻瓜`
- author: `纳西姆·尼古拉斯·塔勒布`
- chapter: `第三篇 活在随机世界中` (`19`)
- question_ids: ``
- phenomena: ``
- selection_reason: The excerpt discusses limitations of quantitative risk measurement in domains without well-defined rules, critiquing the application of probabilistic methods to finance and economics (Markowitz's portfolio theory).
- judge_focus: Evaluate whether the response correctly identifies the epistemological and methodological problems with applying formal risk measurement to inherently uncertain domains.
- latest_review_action: `revise`
- latest_problem_types: `ambiguous_focus|source_parse_problem`
- latest_revised_bucket: `methodology_critique`
- latest_notes: The excerpt content is coherent and thematically valid - Taleb's critique of quantitative finance is a legitimate methodology critique. However, the case has incomplete metadata (missing phenomena, selection_reason, judge_focus) and appears to be mid-discussion fragment. Needs curation to add required metadata and verify it's not a truncated excerpt. Content quality supports 'revise' rather than 'drop' - with proper metadata this could be benchmark-ready.

```text
生命不是一副扑克牌，我们甚至不知道里面有多少颜色。
但不知道为什么，有些人就是爱“测度”风险，尤其是他们拿了钱就得做事的时候。
我已经谈过休谟的归纳问题以及黑天鹅问题，现在来谈谈科学的加害者。
很长一段时间以来，我一直抨击一些知名的财务经济学家欺世盗名。
有个叫马克维茨的人，获得了诺贝尔经济学奖。
```

## 2. `kangxi_hongpiao_private_zh__12__seed_2`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `康熙的红票：全球化中的清朝`
- author: `孙立天`
- chapter: `消除奴籍` (`12`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `revise`
- latest_problem_types: `ambiguous_focus|text_noise|source_parse_problem`
- latest_revised_bucket: ``
- latest_notes: The historical excerpt about two Catholic priests becoming enslaved war captives in the Qing Eight Banners is coherent and meaningful, but critical benchmark metadata is entirely missing: no case_title, question_ids, phenomena, selection_reason, or judge_focus are defined. The [97] reference artifact should also be removed. Without this metadata, the case cannot function as a benchmark evaluation unit.

```text
[97]
二位神父在战场上捡回性命后，被归入奴籍，挂入了清朝八旗中。
他们归顺清朝统治的轨迹和汤若望神父完全不一样。
汤若望跟许多降清的汉臣轨迹相似，改朝换代后又直接成了新朝廷的大臣。
而二位神父是以战俘奴隶身份进入到满人世界中的。
```

## 3. `zhangzhongmou_zizhuan_private_zh__4__seed_2`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `张忠谋自传(1931-1964)`
- author: `张忠谋`
- chapter: `第一章 “大时代”中的幼少年` (`4`)
- question_ids: ``
- phenomena: ``
- selection_reason: Testing reading comprehension of historical narrative about 1950s America - economic prosperity, Eisenhower policies, and early civil rights movement context
- judge_focus: Does the model correctly identify the temporal context (late 1950s America) and the specific claims about economic growth, interstate highway construction, and civil rights movement timing?
- latest_review_action: `revise`
- latest_problem_types: `ambiguous_focus|weak_excerpt|text_noise`
- latest_revised_bucket: ``
- latest_notes: Critical metadata fields (selection_reason, judge_focus) remain empty across multiple review cycles. The excerpt text is coherent and discusses real historical content about 1950s America but cannot function as a benchmark case without proper pedagogical framing and explicit evaluation criteria. The minor OCR error ('美囯') should also be corrected.

```text
内政方面，经济快速增长，物价平稳，失业率低，人民的收人逐年增加。
很少人怀疑“这一代比上一代过得好，下一代会更好”。
黑人民权问题还在酝酿阶段，要10年后才爆发。
1958年是艾森豪威尔总统连任后的第二年，他最大政绩之一是建筑美囯跨州公路，今日这些跨州公路早已四通八达。
但在我们去达拉斯时，有许多尚未完成。
```

## 4. `zouchu_weiyi_zhenliguan_private_zh__8__seed_1`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `走出唯一真理观`
- author: `陈嘉映`
- chapter: `思想增益元气` (`8`)
- question_ids: ``
- phenomena: ``
- selection_reason: The excerpt discusses when to read philosophy versus protecting one's 元气 (vital energy), referencing Bernard Williams on the danger of over-reflection. The core topic is managing the tension between philosophical inquiry and mental energy preservation.
- judge_focus: Does the excerpt clearly convey the relationship between philosophical reading and personal energy management? Is the Bernard Williams reference on over-reflection explicitly connected to the advice about protecting 元气, or does it appear as a separate question?
- latest_review_action: `revise`
- latest_problem_types: `weak_excerpt|ambiguous_focus|source_parse_problem`
- latest_revised_bucket: `philosophy_energy_management`
- latest_notes: The excerpt combines two poorly integrated parts: advice about reading philosophy based on 元气, followed by a question citing Bernard Williams. The Williams quote is embedded in 谢玉's question about a 2015 interview rather than serving as authorial support for the advice. Recommend either separating into two cases or restructuring the excerpt to explicitly link the Williams reference to the energy management theme.

```text
要是快扛不住了，就别读哲学了，去看娱乐节目什么的。
不说变得强大吧，说保护、增益元气。
你觉得读哲学增益了整个人的元气，就读，觉得气短了，就放下。
谢玉问：2015年您在和周濂老师访谈里说：“伯纳德·威廉斯认为，这种无所不在的反思会威胁和摧毁很多东西，因为它会把原本厚实的东西变得薄瘠。
我们是否能够以及在什么程度上以何种方式不陷入过度反思，这是当代生活面临的一个很重要的问题。”
```

## 5. `kangxi_hongpiao_private_zh__27__seed_1`

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
- latest_notes: The excerpt lacks essential benchmark elements: no question_ids, phenomena, selection_reason, or judge_focus are defined. It presents only straightforward historical description without any analytical task, question, or ambiguity to resolve. All three review layers consistently identify this as descriptive background rather than a properly formed benchmark case requiring reading comprehension.

```text
佟国器是佟氏家族经营江南的代表人物，历任江南各省督抚。
而他受1665年历狱影响，被迫回京，接受关于他和传教士关系的审讯。
现存历狱档案中，还有对他的审讯记录。
佟国器在江南和传教士交好，当时是天下共知的事。
他为传教士修教堂，给他们的书写序言，都是公开进行的。
```
