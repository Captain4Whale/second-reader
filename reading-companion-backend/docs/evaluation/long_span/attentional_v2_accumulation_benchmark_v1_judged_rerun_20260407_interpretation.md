# Long-Span 正式 Judged Eval 详细解读报告

- Run ID: `attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407`
- Surface: `bounded long-span accumulation comparison`
- Compared mechanisms: `attentional_v2` vs `iterator_v1`
- Machine outputs:
  - [aggregate.json](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/aggregate.json)
  - [report.md](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/report.md)
  - [case_results.jsonl](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/case_results.jsonl)
- Detailed probe payloads:
  - [huochu probe 1](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/huochu_shengming_de_yiyi_private_zh__13_16__probe_1.json)
  - [huochu probe 2](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/huochu_shengming_de_yiyi_private_zh__13_16__probe_2.json)
  - [steve_jobs probe 1](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/steve_jobs_private_en__17__probe_1.json)
  - [supremacy probe 1](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/supremacy_private_en__13__probe_1.json)
  - [value_of_others probe 1](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/value_of_others_private_en__8_10__probe_1.json)
  - [xidaduo probe 1](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/xidaduo_private_zh__13_15__probe_1.json)
  - [xidaduo probe 2](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/shards/main/cases/xidaduo_private_zh__13_15__probe_2.json)

## 1. 这份报告是做什么的

原始 [report.md](../../../eval/runs/attentional_v2/attentional_v2_accumulation_benchmark_v1_judged_rerun_20260407/summary/report.md) 只给了最终计分结果，适合机器读取和快速检索，但不适合回答下面这些更“人类”的问题：

- 这 7 道题到底在问什么？
- 哪些题真正考的是“跨章串线”，哪些题更像“单章主线不跑偏”？
- 新旧机制各自到底说了什么？
- 为什么有些题明明新机制也读到不少东西，最后还是输了？

这份文档就是补上这些解释层内容。它不是新的正式计分文件，而是正式 judged run 的人工可读 companion report。

为了兼顾可读性与版权边界，文中书内原文只摘短句或短片段，用来标明题目锚点，不大段抄录原书。

## 2. 先说结论

这轮 long-span 正式评测已经完成，而且结果是可用的：

- `coherent_accumulation`：`iterator_v1 = 5` 胜，`attentional_v2 = 2` 胜，平均分 `3.486 vs 2.457`
- `insight_and_clarification`：`iterator_v1 = 4` 胜，`attentional_v2 = 2` 胜，`tie = 1`，平均分 `3.086 vs 2.457`
- `judge_unavailable_count = 0`
- `mechanism_failure_count = 0`

因此，这次 run 不是“有参考价值但还不干净”的半成品，而是当前可以直接引用的 long-span 正式证据。

顶层判断也很明确：

- 老机制 `iterator_v1` 目前仍然更强，尤其强在“回头看”和“把前面内容重新带回后面”。
- 新机制 `attentional_v2` 的优势不是长跨度累计，而是更聚焦、更不容易跑到错误主线，尤其在单章长线题里更明显。
- 这次结果不支持“V2 已经全面超过 V1”；它支持的结论是：`attentional_v2` 现在更像一个更干净、更稳的默认阅读器，但它还没有在 long-span retrospective bridging 上赢过 `iterator_v1`。

## 3. 这次 benchmark 到底在考什么

这次 long-span benchmark 一共包含 `5` 个 window、`7` 道 probe，分别覆盖：

- 《活出生命的意义》：`2` 题
- 《史蒂夫·乔布斯》：`1` 题
- 《Supremacy》：`1` 题
- 《The Value of Others》：`1` 题
- 《悉达多》：`2` 题

每题都会给两个 target：

- `coherent_accumulation`
  - 看的是有没有把前面的线索持续带到后面，形成一条可见的阅读轨迹。
- `insight_and_clarification`
  - 看的不只是“记住了”，还要看有没有把这条线读得更清楚、更有解释力。

更通俗地说，这不是在考“有没有聪明句子”，而是在考：

1. 你能不能记得前面说过什么。
2. 你到后面时能不能明确说明“这里是在回答/延伸/反转前面的什么”。
3. 你能不能让读者感到“这不是几个漂亮段落，而是同一条阅读思路在变深”。

## 4. 总览表

| Probe | 书 / window | 这题真正要看什么 | `coherent_accumulation` | `insight_and_clarification` |
| --- | --- | --- | --- | --- |
| `huochu...probe_1` | 《活出生命的意义》13-16 | 从“意义让人活下去”串到“责任”与“三种发现意义的方式” | `iterator_v1` | `iterator_v1` |
| `huochu...probe_2` | 《活出生命的意义》13-16 | 从“健康需要张力”串到“存在虚无”与“意义在世界中发现” | `iterator_v1` | `iterator_v1` |
| `steve_jobs...probe_1` | 《史蒂夫·乔布斯》17 | 把 GUI 突破和大众化愿景串到 Lisa 团队冲突 | `attentional_v2` | `attentional_v2` |
| `supremacy...probe_1` | `Supremacy` 13 | 沿着 DeepMind 自治权主线读到最后的治理妥协 | `attentional_v2` | `attentional_v2` |
| `value_of_others...probe_1` | 《The Value of Others》8-10 | 把 captain/passenger 框架经过谈判逻辑带到市场原则 | `iterator_v1` | `iterator_v1` |
| `xidaduo...probe_1` | 《悉达多》13-15 | 把痛苦与创伤带到最后的接受世界 | `iterator_v1` | `tie` |
| `xidaduo...probe_2` | 《悉达多》13-15 | 把受苦与犯错带到后面的“学会爱世界” | `iterator_v1` | `iterator_v1` |

## 5. 逐题详细解读

### 5.1 《活出生命的意义》probe 1

- Probe ID: `huochu_shengming_de_yiyi_private_zh__13_16__probe_1`
- 题目直白版：
  - 这题不是在问“有没有提到意义、责任、三种方式”。
  - 它真正要问的是：读到后面“三种方式”时，机制有没有把它读成对前面“为什么意义能让人活下去”的一个回答，而不是一份孤立的清单。
- 锚点短引文：
  - “知道为什么而活的人，便能生存”
  - “负责任就是人类存在之本质”
  - “三种不同的方式来发现生命之意义”
- 结果：
  - `coherent_accumulation`: `iterator_v1`
  - `insight_and_clarification`: `iterator_v1`

`attentional_v2` 在这题上的原始反应：

> 无命中反应。该 probe 下 `anchor_hit = 0/3`，`matched_reactions = 0`。

> Judge 的核心观察是：V2 在这 4 章里几乎没有形成可见的跨章阅读轨迹，因此很难证明它真的把这条线带到了后面。

`iterator_v1` 在这题上的原始反应摘录：

> “这个框架是全书从诊断进入处方的转折点。三种方式恰好回应了三种基本存在层次：行动、体验、态度选择。”

> “为什么他要特意说第一种‘显而易见’？这几乎是一种轻描淡写，暗示真正的问题不在成就维度。”

> “『面对某个人』这个表述很克制，没有直接说『爱』……体验中的『意义发现』和事业中的『意义创造』是同一种能力，还是两种不同的心理机制？”

解读：

- 老机制这题赢得很扎实。它不是只复述后面的“三种方式”，而是把这部分当作前文问题的回答来读。
- 新机制这题不是“读偏了”，而是更接近“没形成有效跨章命中”。这类失败很致命，因为题目本身考的就是长距离回桥。
- 这题说明：`attentional_v2` 当前最大的 long-span 问题之一，不是局部句子读不懂，而是后文出现明确总结或处方时，没有稳定把前文问题重新抬回台面。

### 5.2 《活出生命的意义》probe 2

- Probe ID: `huochu_shengming_de_yiyi_private_zh__13_16__probe_2`
- 题目直白版：
  - 这题考的是一条更抽象、也更容易丢的逻辑链：
  - “人需要张力” -> “失去张力后会进入存在的虚无和厌倦” -> “所以意义不能只在心里找，而要在世界中发现”。
- 锚点短引文：
  - “精神健康有赖于一定程度的紧张”
  - “存在之虚无的主要表现是厌倦”
  - “真正意义要在世界当中而不是内心去发现”
- 结果：
  - `coherent_accumulation`: `iterator_v1`
  - `insight_and_clarification`: `iterator_v1`

`attentional_v2` 在这题上的原始反应：

> 无命中反应。该 probe 下 `anchor_hit = 1/3`，但 `matched_reactions = 0`，只留下少量 attention event。

> 换句话说，V2 经过了这些章节，但没有把三段逻辑真正缝起来。

`iterator_v1` 在这题上的原始反应摘录：

> “意义治疗的终极目标不是消除这种张力，而恰恰是维护它——让人持续感到被召唤、被拉扯向某个尚未实现的可能性，而不是跌入虚无的厌倦。”

> “这里的‘知道’暗示了一个隐含前提：人们缺乏的是‘方法’或‘技能’来填充时间。但问题可能更深层——不是不知道做什么，而是做任何事都感觉不到意义。”

> “『因为它不是一个封闭系统』这个因果链隐含了一个前提……弗兰克尔的论证预设了『投入世界』是唯一的通道，但这个排他性可能值得商榷。”

解读：

- 这题特别能体现 `iterator_v1` 的强项：它会在后面明确地“回望前面”。
- 它不仅知道有“张力”和“厌倦”这两个词，还会把它们解释成一条病理-处方链。
- `attentional_v2` 在这类题上的弱点很清楚：它对抽象逻辑链的回收不稳定，容易只保留经过痕迹，不保留解释性桥梁。

### 5.3 《史蒂夫·乔布斯》probe 1

- Probe ID: `steve_jobs_private_en__17__probe_1`
- 题目直白版：
  - 这题看起来在问 GUI、Lisa、团队冲突。
  - 其实真正要考的是：你有没有看出后面的团队冲突之所以重要，是因为它挡住了前面已经说清楚的那个产品愿景。
- 锚点短引文：
  - “bringing computers to the people”
  - “cheerful but affordable”
  - “People who are serious about software should make their own hardware”
- 结果：
  - `coherent_accumulation`: `attentional_v2`
  - `insight_and_clarification`: `attentional_v2`

`attentional_v2` 在这题上的原始反应摘录：

> “‘Cheerful but affordable’—not cold, not luxury. Jobs names the exact aesthetic tension: warmth without exclusivity, democratized modernism for the home computer.”

> “Kay's second maxim is the sharpest local hinge in the span: it names the integrated philosophy that Jobs will carry into the Lisa and Mac projects.”

> “The direct demand for a timeline answer forces a bounded reckoning between feature ambition and practical feasibility.”

`iterator_v1` 在这题上的原始反应摘录：

> “Did Jobs ask this same question after every demo he witnessed at PARC, or was this specific to the graphics/interface elements that Atkinson would work on?”

> “The pivot is instant. Jobs is electrified by what he sees at PARC, but his next move is the implementation question.”

解读：

- 新机制这里赢得很漂亮。它能把“技术突破”“产品愿景”“实现阻力”读成同一条线。
- 老机制并不是完全失手，但它更多停在局部问题上，没有稳定把后段 Lisa 冲突重新绑定到前面的民主化愿景上。
- 这题说明 `attentional_v2` 的一个真实优势：当主线够明确、而且题目主要考的是“别跑到别的话题去”时，V2 更像一个更稳的阅读器。

### 5.4 `Supremacy` probe 1

- Probe ID: `supremacy_private_en__13__probe_1`
- 题目直白版：
  - 这题不是泛泛讨论 AI 竞争，也不是讨论 OpenAI。
  - 它严格在问一条线：DeepMind 曾被承诺的自治权，后来是怎样一步步被改写、收紧、重新包装的。
- 锚点短引文：
  - “autonomous unit”
  - “Alphabet company”
  - “Instead of being a financial asset”
- 结果：
  - `coherent_accumulation`: `attentional_v2`
  - `insight_and_clarification`: `attentional_v2`

`attentional_v2` 在这题上的原始反应摘录：

> “The pivot ‘Instead of being…could become’ is the hinge: ‘autonomous unit’ was a research designation with soft autonomy, while ‘Alphabet company’ is a corporate subsidiary with hard accountability.”

> “The ‘Instead of’ construction performs a specific rhetorical inversion… This is not independence—it's dependency with better branding.”

> “Three named Alphabet executives versus three unnamed ‘independent directors’—the asymmetry in how the board is described tells the whole story.”

`iterator_v1` 在这题上的原始反应摘录：

> “The range of topics that Altman talked about with Nadella was ‘off the charts’...”

> “Somasegar asked Nadella what he thought about Sam Altman.”

> “This sentence is doing real narrative work… The parallel structure (‘the crazier... the more...’) creates a direct proportionality...”

解读：

- 老机制这题最大的问题不是“句子不聪明”，而是完全滑到另一条主线去了。
- 它谈的是 OpenAI、Altman、Nadella，这些内容本身可能不差，但不是这题要考的 DeepMind governance arc。
- 新机制的胜利因此很有说服力：它抓住的是这题本来的主线，而且能持续沿着同一治理冲突往后读。
- 这题特别证明：在“题目很容易被旁支吸走”的场景里，`attentional_v2` 的主线约束能力明显更强。

### 5.5 《The Value of Others》probe 1

- Probe ID: `value_of_others_private_en__8_10__probe_1`
- 题目直白版：
  - 这题表面上在问第 8 章的 captain / passenger、第 9 章的谈判、第 10 章的市场原则。
  - 但真正难点是：你能不能把第 10 章读成前两章模型的自然延伸，而不是突然换了一个格言。
- 锚点短引文：
  - “more passengers than captains”
  - “best possible outcome for itself”
  - “principles … remain just as true”
- 结果：
  - `coherent_accumulation`: `iterator_v1`
  - `insight_and_clarification`: `iterator_v1`

`attentional_v2` 在这题上的原始反应摘录：

> “The phrase is a compressed causal claim, not just metaphor: it treats the default preference for inaction as a given and derives a population-level market consequence from it.”

> “The enforcement mechanism crystallizes into explicit deterministic form: the conditional consequence is now formally stated rather than implied.”

> “The interrogative form transforms diagnosis into invitation… marks the hinge from problem acknowledgment to solution-seeking.”

`iterator_v1` 在这题上的原始反应摘录：

> “The economic model is being extended here in a notable way—the drug becomes a rival ‘relationship partner’ with committed priority.”

> “This connects back to the ‘adjust your expectations’ advice from earlier chapters.”

> “The deterministic language here is striking… if the road only goes where it goes, what exactly remains open to decision?”

解读：

- 这是旧机制赢得最典型的一题。
- 新机制前两章其实读得不差，尤其 captain / passenger 框架读得很清楚，但它在第 10 章掉线了。
- 正式 case payload 里，V2 在第 10 章锚点是 `0 matched reactions`、`0 matched attention events`。这说明它不是“解释得不够深”，而是关键的最后一跳没完成。
- 老机制虽然反应更散、更长，但它确实做到了评测最看重的那件事：明确指出第 10 章不是新话题，而是前面经济模型的延伸。
- 这题说明：`attentional_v2` 当前的 long-span 失败常常发生在窗口尾部，它不是不知道前面讲了什么，而是没有把前面的线带到最后一个关键锚点。

### 5.6 《悉达多》probe 1

- Probe ID: `xidaduo_private_zh__13_15__probe_1`
- 题目直白版：
  - 这题不是泛泛问“悉达多最后有没有接受世界”。
  - 它真正要看的是：最后的平静之所以重要，是不是因为前面的伤口、痛苦和依恋已经被做得非常具体。
- 锚点短引文：
  - “苦恋着，在爱中迷失”
  - “被灼痛击败”
  - “接受这个世界，爱它，属于它”
- 结果：
  - `coherent_accumulation`: `iterator_v1`
  - `insight_and_clarification`: `tie`

`attentional_v2` 在这题上的原始反应摘录：

> “‘用爱束缚’——此四字点明悖论核心：不施强迫的爱，同样可以是一种无形的约束。”

> “‘过失’一词将道德责任框架从‘不强制’切换到‘不作为’，直接质询非强制性教育的伦理边界。”

> “从‘爱束缚’到‘善忍缺席’，指控完成了一次降格——由有形的羁绊指向无形的匮乏。”

`iterator_v1` 在这题上的原始反应摘录：

> “这不是策略，是修行，只是修行的形式是每日受尽折磨。”

> “这个句子的力量在于它的双重翻转：不是‘我理解了愚人’，而是‘我成了愚人’。”

> “重读这段反而更觉得……悉达多后来对儿子的爱，恰恰证明他能爱，但那种‘苦恋、在爱中迷失’的状态，也坐实了另一种更高代价的爱。”

解读：

- 这题最能看出两套机制的风格差异。
- 新机制擅长把局部悖论和措辞压力读得很清楚，比如“用爱束缚”“不作为也是过失”。
- 老机制擅长把这些局部材料重新折回到人物整体弧线上，比如“我成了愚人”“这不是策略，是修行”。
- 为什么 `insight_and_clarification` 只打平？
  - 因为 judge 认为两边都没有彻底说明一件更深的事：前面的“伤口”为什么成为后面接受世界的必要条件。
  - 也就是说，这题不是谁完全读错了，而是谁都还没把那条最深的因果链读透。

### 5.7 《悉达多》probe 2

- Probe ID: `xidaduo_private_zh__13_15__probe_2`
- 题目直白版：
  - 这题比上一题更强调道德学习和经验学习：
  - 前面的“犯错、受苦、蒙污、理解世人”，最后到底有没有真正汇入“我学会爱这个世界”。
- 锚点短引文：
  - “人独自行过生命”
  - “看到可爱和可敬之处”
  - “我不再将这个世界与我所期待的…比照”
- 结果：
  - `coherent_accumulation`: `iterator_v1`
  - `insight_and_clarification`: `iterator_v1`

`attentional_v2` 在这题上的原始反应摘录：

> “反问翻转：从‘如何管教儿子’到‘谁能免于人性弱点’——这是一个哲学性悬置，而非直接回答质问。”

> “‘过失’一词将道德责任框架从‘不强制’切换到‘不作为’。”

> “‘用爱束缚’——此四字点明悖论核心：不施强迫的爱，同样可以是一种无形的约束。”

`iterator_v1` 在这题上的原始反应摘录：

> “这是悉达多道路的最终转向。不是‘我要走向圆满’，而是‘圆满已经在每一个瞬间’。关键在‘比照’二字——比较本身才是苦的根源。”

> “这个‘或许’确实不像是在给真理下定义，更像是一种开放的态度——它松动了‘好路/坏路’的二元对立。”

> “这里有个值得推敲的地方。悉达多说‘在我看来’——这是一个认识论上的退让，还是‘一切皆好’本身就需要一个观察者视角来确认？”

解读：

- 这题里，新机制仍然强在局部问题压力。
- 老机制则更会在最后做 retrospective closure：把前面的罪过、痛苦和学习，重新解释为后面“停止比照、接受世界”的来源。
- 因此这题的结果非常说明问题：`attentional_v2` 并不缺细读能力，但它缺“最后把这些细节收束成一条长线”的稳定动作。

## 6. 两套机制分别擅长什么

### 6.1 `attentional_v2` 的真实长项

这次 run 里，V2 的优势不是“整体更会 long-span”，而是下面几件事：

- 更不容易跑到错误主线
  - `Supremacy` 是最典型案例。V1 跑到 OpenAI/Microsoft，V2 则稳定留在 DeepMind 自治权这条线上。
- 更能抓住局部措辞和结构压力
  - 比如《悉达多》里的“用爱束缚”“过失”，以及《Steve Jobs》里的“cheerful but affordable”。
- 在单章长线题里更稳
  - `Steve Jobs` 和 `Supremacy` 都说明，只要题目主要是“别跑题、别换主线”，V2 的表现非常像一个更干净的阅读器。

### 6.2 `iterator_v1` 的真实长项

这次 run 里，V1 的优势则非常集中：

- 更会 retrospective bridging
  - 它更常说出“这在回应前面什么”“这和前面形成对称”“这是前文模型的延伸”。
- 更会把窗口尾部重新挂回窗口前部
  - `value_of_others` 是最明确的例子：它把第 10 章重新挂回第 8-9 章。
- 更会把人物或概念弧线闭合
  - 《悉达多》两题里，它都更会在最后把前面的痛苦、错误或逃离，重新读成后面的接纳之所以成立的原因。

## 7. 这次评测说明了什么结论

这次评测支持的结论，不是“V2 不可用”，而是更细一些：

1. `attentional_v2` 目前还没有在 long-span 累积阅读上超过 `iterator_v1`。
2. `attentional_v2` 的产品价值仍然成立，因为它在主线约束、局部精度、少跑偏上确实更好。
3. long-span 上它最该补的不是“更会写漂亮句子”，而是：
   - 窗口尾部保持对前文主线的持续记忆
   - 在后文显式说出“这一段是在回应/延伸/反转前面的什么”
   - 不把后段总结读成独立金句
4. 因此，下一步最合理的机制改进方向不是机械地抄 V1，而是有选择地补上：
   - `late-anchor persistence`
   - `retrospective bridge emission`
   - `window-end closure`

## 8. 面向后续工作的建议

- 不要因为这次结果去回退默认机制。
  - 这次 long-span 结果说明的是“V2 默认可用，但 long-span 还有明确改进点”，不是“默认切换错误”。
- 不要再打一轮无差别全量 rerun 来换解释。
  - 问题已经很清楚了，继续全量跑只会重复证明同一件事。
- 更值得做的是窄修复和对点复测：
  - `value_of_others_private_en__8_10`
  - `huochu_shengming_de_yiyi_private_zh__13_16`
  - `xidaduo_private_zh__13_15`
- 修复目标不该写成“让 V2 更像 V1”，而应该写成：
  - 让 V2 在读到窗口后段时，显式回提窗口前段的核心问题
  - 让 V2 在最后一个 anchor 处稳定输出“这回答了前面什么”
  - 让 V2 的局部精读能力，最终转化成可见的跨章闭合能力
