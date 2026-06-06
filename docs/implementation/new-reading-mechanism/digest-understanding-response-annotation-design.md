# Digest Understanding / Response / Annotation Design

Purpose: define the implemented Digest action semantics and prompt/output contract shift from memory-shaped output to reading-action-shaped output.
Use when: reviewing the Digest `Understanding / Response / Annotation` prompt contract after `DEC-108` and `DEC-109`.
Not for: stable runtime authority, evaluation claims, or evidence-catalog updates.
Update when: Digest action names, output fields, XML prompt structure, or runtime mapping from Digest output to stored memory changes.

## Status

- Date: `2026-06-01`
- Status: implemented in live Digest prompt / LLM output normalization.
- Evaluation status: no eval run, no evidence-catalog update.
- Supersession note:
  - This document remains the authority for Digest's three peer model-facing outputs: `understanding`, `response`, and `annotations`.
  - Its early `ReadingState` context examples were superseded by `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md`.
  - The current live Digest prompt uses top-level `ReadingMemory`, not `ReadingState`, `RecentMemory`, or `RetrievedUnitMemory`.
- Subject-continuity note:
  - `docs/implementation/new-reading-mechanism/ingest-recall-and-digest-memory-context-design.md` defines the subject-continuity rule now implemented in Digest prompt `attentional_v2.digest.v7`.
  - The implementation carries narrator / speaker / actor / concept continuity through prior Understanding in `ReadingMemory`; it is not a mechanical ban on every pronoun and does not add a new raw-source backfill path.
- Current basis:
  - `DEC-108` makes `Digest` the concrete per-unit interpretation LLM call.
  - `DEC-109` removes content-typed structured long-memory stores from the current live surface.
  - Current Digest stores one model-produced `understanding` object through runtime `recent_reading_memory`, but the model-facing task no longer phrases this as "maintain memory."

## Implementation Status

- Implemented prompt version: `attentional_v2.digest.v9`
- Implemented XML assembly spec: `attentional_v2.digest.xml.v9`
- Implemented promptset: `attentional_v2-phase6-v55`
- Implemented output contract: `digest_understanding_response_annotation_json_v3`
- Runtime mapping:
  - `understanding` string -> zero or one internal `memory_uptake_ops[].payload.memory_text` targeting `recent_reading_memory`
  - `response` -> internal `DigestResult.reading_impression`
  - `annotations[]` -> internal `DigestResult.surfaced_reactions`
- Subject-continuity mapping:
  - `ReadingMemory` is the only prompt-facing carrier of prior Understanding for subject continuity.
  - Digest should establish new subjects, continue known subjects from `ReadingMemory` when supported, and preserve genuine ambiguity instead of guessing.
  - Pronouns are allowed only when the referent is clear inside the same `understanding`.
- Source-established-content calibration:
  - Digest should write `understanding` as content established by the source text, not as commentary on what the passage does as a passage.
  - Readerly effects such as suspense, revelation, atmosphere, or aftertaste belong in `response` unless the source text itself states them as content.
- Old model-facing fields `reading_impression`, `surfaced_reactions`, and `recent_reading_memory` are not accepted as current Digest LLM contract fields; internal runtime/audit names remain stable in this slice.

## Design Claim

Digest should be described as one coherent reading action with three peer outputs:

- `Understanding`: read the source text in; state what is understood from the text itself in concise, source-faithful content-level prose.
- `Response`: read the source unit out; express the reader's integrated feeling, thought, pressure, question, or aftertaste after understanding it.
- `Annotation`: produce visible margin-note-style output anchored to exact source text.

This replaces the current uneven semantic split:

- `reading_impression` and `surfaced_reactions` are described as reading behavior.
- `recent_reading_memory` is described under memory maintenance.

The new model-facing semantics should not ask Digest to remember for memory's sake. Digest should understand the present unit. The runtime may store that understanding as recent reading memory afterward, but storage is a post-processing consequence rather than the LLM's primary self-description.

## Is Instruction-Only Enough?

No. The main semantic work belongs in `Instruction`, but the refactor should also update the LLM-facing output contract and runtime normalization.

Minimum implementation scope:

- `Instruction`
  - Make `Understanding`, `Response`, and `Annotation` direct child blocks under top-level `Instruction`.
  - Remove `MemoryInstruction` as a top-level action category.
  - Keep non-action support blocks such as `CurrentStep` / `TaskOverview`, `ContextUseGuide`, `SourceGrounding`, and `ResponseDiscipline`.
- `OutputContract`
  - Rename LLM-facing output fields from `recent_reading_memory`, `reading_impression`, and `surfaced_reactions` to `understanding`, `response`, and `annotations`.
  - Update field contracts so the three outputs are peers.
- Runtime adapter
  - Convert the single `understanding` object into zero or one internal `memory_uptake_ops[]` with `target_store="recent_reading_memory"`.
  - Normalize `annotations[]` using the existing surfaced-reaction grounding rules.
  - Map `response` into the current internal `reading_impression` field unless a later cleanup renames audit/runtime artifacts too.
- Tests / docs
  - Update prompt manifest tests, Digest output-normalizer tests, read-audit tests, and stable docs that describe the current Digest output contract.

Storage can remain unchanged in the first implementation slice:

- `recent_reading_memory` remains the runtime store.
- `read_audit.jsonl` may continue to record internal `reading_impression`, `surfaced_reactions`, and normalized memory ops.
- A later cleanup can decide whether audit keys should become `digest_understanding`, `digest_response`, and `digest_annotations`.

## Pre-Implementation Prompt Structure

Before this implementation, the top-level user prompt shape was:

```xml
<ReaderRole>...</ReaderRole>
<Instruction>...</Instruction>
<BookInfo>...</BookInfo>
<ReadingState>...</ReadingState>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

Pre-implementation `Instruction` shape:

```xml
<Instruction>
  <TaskOverview>...</TaskOverview>
  <ContextUseGuide>...</ContextUseGuide>
  <ReadingBehavior>
    <ReadingImpression>...</ReadingImpression>
    <SurfacedReaction>
      <ReactionSelection>...</ReactionSelection>
      <ReactionGroundingAndCallback>...</ReactionGroundingAndCallback>
    </SurfacedReaction>
  </ReadingBehavior>
  <MemoryInstruction>
    <MemoryBoundary>...</MemoryBoundary>
    <RecentReadingMemory>...</RecentReadingMemory>
  </MemoryInstruction>
  <SourceGrounding>...</SourceGrounding>
  <ResponseDiscipline>...</ResponseDiscipline>
</Instruction>
```

Pre-implementation LLM-facing output contract:

```json
{
  "reading_impression": "...",
  "surfaced_reactions": [],
  "recent_reading_memory": []
}
```

Before this implementation, runtime converted:

- `recent_reading_memory[]` -> `memory_uptake_ops[]` targeting `recent_reading_memory`
- `reading_impression` -> internal `DigestResult.reading_impression`
- `surfaced_reactions[]` -> internal `DigestResult.surfaced_reactions`

## Current Live Prompt Structure

The current live Digest prompt shape is:

```xml
<ReaderRole>...</ReaderRole>
<Instruction>...</Instruction>
<BookInfo>...</BookInfo>
<ReadingMemory>...</ReadingMemory>
<CurrentFocus>...</CurrentFocus>
<OutputContract>...</OutputContract>
```

Current prompt-facing memory is one `ReadingMemory` text block. Runtime merges hot current-chapter Understanding from `recent_reading_memory` with selected long-distance Unit Memory Understanding lines before rendering it. Digest does not receive separate `ReadingState`, `RecentMemory`, `RetrievedUnitMemory`, raw prior source text, prior Response, or prior Annotation blocks.

## Old Prompt Text Moved Or Rewritten

### Old Task Overview

Old fragment:

```text
Your job is to read the exact current unit with a small carried-forward memory packet, then return a structured record of the reading experience.

Rules:
- First read the provided unit as the current reading present, not as a field-filling task.
```

Assessment:

- Keep the "current reading present" idea.
- Replace "structured record of the reading experience" with the three peer outputs.

### Old Reading Impression Policy

Old fragment:

```text
- Let `reading_impression` be the brief natural impression that remains after reading: what you now understand, notice, or feel from this passage.
- Use the carried-forward memory naturally when it genuinely matters, but do not collapse the unit into a chapter summary or evaluator voice.
- Do not invent earlier text that is not present in the carried memory or selective carry.
```

Assessment:

- Keep most of this, but rename and narrow it to `Response`.
- Remove "what you now understand" from this field because `Understanding` will own source-faithful content.
- Keep "notice or feel" only if it is framed as a reader response after understanding.

### Old Surfaced Reaction Policy

Old fragment is already mostly aligned with `Annotation`. It says surfaced reactions should:

- stay proportionate around thin structural units
- only surface naturally worth-marking material
- stay anchored to the current unit
- use exact `source_quote`
- default to `0-2`
- avoid swallowing earlier independently meaningful lines
- use a wide-entry, narrow-expression stance

Assessment:

- Keep the policy substance.
- Rename `surfaced_reactions` to `annotations` in prompt-facing text.
- Rename `SurfacedReaction` instruction block to `Annotation`.
- Keep callback/link hygiene under `AnnotationGroundingAndCallback`.

### Old Recent Reading Memory Policy

Old fragment begins:

```text
- First maintain Recent Reading Memory: after reading this unit, write one Recent Reading Memory entry for your future self unless the unit is empty or purely structural.
- Assume the exact source text of this unit may not be shown again in the next Digest step. Record what you now understand from this unit that should remain available for coherent continued reading.
- Write Recent Reading Memory as source-established content first, not essay-like analysis.
- First record what the source directly establishes for future reading: who or what appears, what happened, what the author claims, what distinction / stage / example is introduced, what condition or consequence is stated, or what writing position / evidence boundary / reader-orientation is declared.
```

Assessment:

- This is the largest semantic rewrite.
- The core content rules are useful, but the "maintain memory" framing should be removed.
- The output should be `Understanding`: what the current unit itself establishes, not "what should be remembered."
- Future-use language can remain lightly as "for continued reading," but should not dominate the task.
- References to stable concept/thread context should be removed because `DEC-109` retired those model-facing stores.

## Target Instruction Shape

`Understanding`, `Response`, and `Annotation` should be direct child tags under `Instruction`.

Target shape:

```xml
<Instruction>
  <CurrentStep>...</CurrentStep>
  <ContextUseGuide>...</ContextUseGuide>
  <Understanding>...</Understanding>
  <Response>...</Response>
  <Annotation>...</Annotation>
  <SourceGrounding>...</SourceGrounding>
  <ResponseDiscipline>...</ResponseDiscipline>
</Instruction>
```

Why direct children:

- They are the three main work products of Digest.
- Keeping them direct makes the prompt easy to inspect and avoids hiding one output under "memory."
- `CurrentStep`, `ContextUseGuide`, `SourceGrounding`, and `ResponseDiscipline` remain support blocks rather than peer outputs.

## Target Prompt Text

Tone rule:

- The beginning of `Instruction` should invite a readerly stance before it introduces output governance.
- Mechanical language is acceptable in `OutputContract`, but `CurrentStep`, `Understanding`, and `Response` should not sound like schema-filling instructions.
- Boundary rules should appear after the positive reading posture is established.

### CurrentStep

```text
You are now reading the next source unit in an ongoing deep reading of this book.

Stay with this unit as the present moment of reading. Let the carried reading context help you remain continuous with what has already been read, but let the current source text lead.

After reading, express the result in three connected ways: what you understand from the text, how you respond to it as a reader, and which exact lines, if any, are worth annotating.
```

### ContextUseGuide

```text
- Let BookInfo orient you to the stable identity of the book; it is not source text.
- Let ReadingMemory hold prior understanding that the reading has already carried forward. Use it for continuity, contrast, callback, and unresolved pressure when it genuinely clarifies the current source unit.
- Do not treat ReadingMemory as current source text, prior reader response to imitate, or a reason to force a connection.
- Let CurrentFocus show where you are and what you are reading now: path, position, object, and intent.
- Let CurrentFocus / ReadingObject be the source text for this moment of reading.
- Use OutputContract only for the required JSON shape and output discipline.
```

This is the current `digest.context_use_guide` posture after the `ReadingMemory` follow-through slice.

### Understanding

```text
# Read
Read the current source text and state what you understand from it.

# Keep key information
Keep the minimum content needed to understand what this source text has added.

For narrative or scene text, keep the main actors, actions, situation, and any important change in relation, emotion, knowledge, or condition.

For claim, concept, or argument text, keep the central claim, definition, distinction, necessary condition, or step. Keep examples only when they are needed to understand the claim; otherwise compress them into the meaning they support.

For list, taxonomy, or step text, preserve the structure with compact bullets or numbering when that is clearer than prose.

# Writing stance
Let the grammatical subject normally be a person, event, concept, claim, relationship, scene, method, or condition from the text, rather than the source container itself.

# Source-established content
Write Understanding as the content established by the source text, not as commentary on what the passage does as a passage.

Prefer statements of who appears, what happens, what is claimed, what relationship, condition, change, or situation becomes clear.

Do not describe readerly effects such as suspense, revelation, atmosphere, or aftertaste unless the source text itself states that content.

# Concision
Compress meaning, not wording. Be brief, but do not drop the main event, claim, condition, or relationship change. Do not copy the whole source or turn the understanding into a reaction, evaluation, or annotation. The understanding should be shorter than the source text and normally no more than a few compact sentences.

# Empty-content exception
If the source text is only a divider, empty heading, or other non-content structure, `content` may be empty; otherwise give a substantive understanding.

# Examples
## Example 1 - Source
"哪里？"我追问了一句。他随手指向几百码外的烟囱，烟囱里冒出的一串串火苗映照着波兰灰暗的天空，又慢慢融入幽暗的烟云。

"你的朋友正慢慢地飘向天空。"他答道。起初我不太理解，直到后来有人用通俗的语言做了解释，我才明白他那句话的真正含义。

我不想就此多说一句。从心理学角度讲，从拂晓时分到达车站一直到在营地度过第一夜，在我们心中，这是一个漫长的过程。

在荷枪实弹的党卫军护送下，我们跑步从火车站出发，经过带电的铁丝网，穿过集中营，到达清洁站。在那里，我们这些初次被筛选出来能活着的人，真正地洗了个澡。被缓期执行的幻觉也得到了证实。奇怪的是，那些党卫军看起来极具友好的魅力，其中的原因不久就被我们找到了。他们在看中我们的腕表并婉言说服我们交出来时，显得极其友好。难道我们不该向这些友好人士上交那些财产吗？难道这样的好人不该拥有这块手表吗？也许有一天他们会报答我们。

当我们在貌似消毒室的屋子里等待时，党卫军来了。他们在地上铺开一块毯子，让我们把所有的财物包括手表和珠宝都扔到上面。一些天真的人还问他们能否保留一枚戒指、一块奖牌或一件幸运物，这惹得那些老道的囚徒发出阵阵笑声，他们在嘲笑这些天真的人尚未意识到自己的财产都要被剥夺的事实。

## Example 1 - Understanding
- 在前往集中营的路程中，作者的朋友提醒他看到了远方烟囱冒出的火苗与烟云，并解释道这是焚烧犯人产生的。从到达车站一直到在营地度过第一夜，在作者他们的心中是一个漫长的过程。
- 在到达集中营后，党卫军奇怪地看起来非常友好，要求这些经筛选出来的"被缓期执行"的人把所有财产上交。有些天真的刚来的人试图请求保留某些物件，引起老道的囚徒的嘲笑。

## Example 2 - Source
无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。

有一次，有人向哈佛大学的校长德里克·博克（Derek Bok）提出了同样的问题。那时候，哈佛大学的捐赠基金规模最大，哈佛大学的学术声誉和社会影响力都处于巅峰时期。有人问博克教授，如果政府持续削减投向高校的教育经费，哈佛大学会受到怎样的影响。博克沉吟了片刻，回答道："我们不会是第一个倒下去的大学。"

我们发放贷款的时候就谨小慎微，留足了安全边际。我们发放的贷款占资产评估价值的比例较低。我们发放贷款的信用标准设置得很高。我们持有的长期贷款，99.999%都是安全的。在我们持有的贷款中，很多属于房产价值高、贷款金额低的情况，例如，房产价值40万美元、贷款金额两万美元。

虽然我们已经很保守了，但还是会零星出现违约的情况，可能是借款人得了老年痴呆，或者到了酗酒晚期。几百笔贷款，做到了足够保守，有可能实现整体零亏损，但很难避免个别违约。有些借款人总是不能按时还款，这一部分贷款在我们的贷款总量中占0.5%左右，但是我们有足够的抵押物价值做担保。

## Example 2 - Understanding
芒格公司的业务都留了足够的安全边际，很难陷入困境。

## Example 3 - Source
要想在社会上赚到钱，就要为社会提供其有需求但无从获得的东西。如果社会已经创造出需要的产品和服务，你也就不被需要了。

你家里、工作场所和大街上的几乎所有东西都曾是科技产品。曾几何时，石油这种科技产品让洛克菲勒变得富有，汽车这种科技产品让亨利·福特积累起财富。

因此，正如艾伦·凯所说，科技就是一套尚未完全发挥作用的东西（更正，是丹尼尔·希利斯所说）。某种东西一旦得到广泛应用，它就不再是科技了。社会总是需要新事物。如果想变得富有，你就要弄清楚你能为社会提供哪些其有需求但无从获得的东西，而提供这些东西对你来说又是轻松自然的事情，在你的技术和能力范围内。

下一步是思考如何规模化，因为只提供一个产品或一项服务是远远不够的，必须提供成千上万个，甚至几十万、几百万、几十亿个，最好人手一个。史蒂夫·乔布斯（当然还有他的团队）发现社会需要智能手机。他们设想的是一台可以装在口袋里随身携带的小型计算机，拥有电话的所有功能，甚至比电话的功能还强大100倍，使用起来也非常简单。然后，他们研究出了如何制造这样一部智能手机，以及如何实现规模化生产。[78]

## Example 3 - Understanding
如果想变得富有：
1. 弄清楚自己能为社会提供哪些其有需求但无从获得的东西。
2. 这些东西对自己来说是轻松自然的事情，并且在自己的技术和能力范围内。
3. 将其规模化。

## Example 4 - Source
Across cultures and throughout history, people have devised three general approaches to the problem of others.⁠1 Some choose to move against others. This involves taking what they want from other people using force, skill, or guile in conquest or competition. Others choose to move away from others. This involves eliminating the inner desire for things or the interpersonal dependence that makes it necessary to deal with people. Both of these approaches are essentially antisocial – albeit for different reasons.

## Example 4 - Understanding
People have developed several ways to deal with dependence on others. This source defines two of them: moving against others by taking what one wants through force, skill, or guile, and moving away from others by trying to eliminate desire or interpersonal dependence. Both are antisocial, though in different ways.

## Example 5 - Source
可伤口依然灼痛。悉达多苦苦思念着儿子。他耽于爱和柔情，任凭痛苦吞噬，体验一切爱的痴愚。这火焰无法自行熄灭。

这天，伤口又灼痛得厉害。悉达多被渴望折磨。他毅然渡河登岸，进城寻子。正值旱季的河水轻柔涌动，水声却有些奇特：它在笑！它的确在笑。它清脆响亮地嘲笑着老船夫。悉达多停下脚步，俯身贴近水面倾听。他看见平静的水面上倒映出他的脸，这张脸似乎让他记起遗忘的往事。他沉思片刻，继而发觉这张脸跟一张他熟悉、热爱又敬畏的脸十分相似。那是他父亲的脸，那个婆罗门的脸。

他记起年轻时曾如何迫使父亲答应他出门苦修，如何同父亲告别，如何离家，之后又再未回去。难道父亲不是为他受苦，如同他现在为儿子受苦？难道父亲不是再没见到儿子，早已孤零零地死去？这难道不是一幕奇异又荒谬的谐剧？不是一场宿命的轮回？

河水笑着。是的，正是如此。一切未受尽的苦，未获得的救赎都会重来。苦难从未改变。悉达多重新登船，返回茅舍。他想着父亲、儿子，内心挣扎着，几近绝望。他被河水嘲笑，也想跟随河水大声嘲笑自己和整个世界。啊，这伤口尚未风化，他的心仍在抗拒命运，他的苦难仍未绽放喜悦和胜利的光华。可他却感受到希望。回到茅舍后，他迫切要向瓦稣迪瓦倾诉，向这位倾听大师敞开心扉。

## Example 5 - Understanding
悉达多苦苦思念儿子，毅然渡河登岸，进城寻子。但他听到河水在嘲笑他，俯身在水面中自己的倒影中看到了父亲的脸，想到自己年轻时迫使父亲答应他出门苦修，让父亲再没见到儿子，早已孤零零地死去。现在发生他身上的是一场宿命的轮回，他感受到希望，迫切要向瓦稣迪瓦倾诉。
```

Implementation notes:

- This wording intentionally avoids asking the model to describe what the unit "does" in the reading, because that led to commentary-like `本单元/This unit` outputs.
- It adds type-aware compression rules for narrative/scene text, claim/argument text, and list/taxonomy/step text so the model compresses meaning rather than reproducing source wording.
- The grammatical-subject guidance steers the model toward content from the text: people, events, concepts, claims, relationships, scenes, methods, or conditions.
- The source-established-content calibration keeps reading effects such as suspense, revelation, atmosphere, or aftertaste out of `Understanding` unless the source itself states them as content.
- The five examples are approved from real five-window diagnostic units and show content-level, memory-ready Understanding without naming the source container.
- The single-string rule for `understanding` lives in `OutputContract`, not in the reader-facing `Understanding` instruction.

### Implemented Subject-Continuity Understanding Rule

Prompt version `attentional_v2.digest.v9` makes `understanding` self-contained by using the current source text and `ReadingMemory` to continue known subjects, establish new subjects, or preserve meaningful ambiguity.

This rule does not add raw prior-source context to Digest and does not make Ingest responsible for reference resolution.

Implemented rule:

```text
# Subject continuity
Use ReadingMemory to understand whether the current source text continues an already established narrator, speaker, actor, concept, relationship, or point of view.

When the current unit establishes a new subject, write that subject explicitly in Understanding. If the identity is not yet fully known, use the clearest source-supported description, such as the first-person narrator, a quoted speaker, a prisoner, Siddhartha's son, a company, a claim, or a relationship.

When a pronoun or demonstrative clearly refers to a known subject from ReadingMemory or from the current unit, write the referent explicitly at its first important mention.

When the referent is genuinely ambiguous, do not guess. Record the ambiguity as part of the Understanding when it matters for continued reading.

Pronouns are acceptable after the referent is clear inside the same Understanding. Avoid floating pronouns that cannot be understood after this Understanding is stored as memory.
```

This is a subject-continuity rule, not a no-pronoun rule.

Known subject continued:

```text
ReadingMemory:
P12 U4: The first-person narrator Frankl has arrived at the concentration camp and is describing the first night from his own experience.

Current source:
I did not want to say more about it.

Understanding:
Frankl avoids dwelling on the friend's death and turns toward the psychological experience of arriving at the camp.
```

New subject established:

```text
Current source:
I had never seen the city before.

Understanding:
A first-person narrator begins from an unfamiliar arrival in the city; the narrator's exact identity is not yet established.
```

Ambiguity preserved:

```text
Current source:
He returned before anyone could explain why.

Understanding:
A male figure returns before the cause of his earlier absence is explained; the current memory does not yet make clear which person "he" refers to.
```

Clear local pronoun allowed:

```text
Siddhartha recognizes that father-son suffering is recurring in his own life. This recognition gives Siddhartha hope and makes him want to speak with Vasudeva.
```

Here `This recognition` is acceptable because the referent is explicit in the preceding sentence.

Bad stored Understanding:

```text
He realizes that this is happening again and wants to tell him about it.
```

That output is not acceptable as stored Understanding because the later reader cannot recover `he`, `this`, `him`, or `it` from memory.

The same rule is reflected in `OutputContract / UnderstandingField`, because `understanding` is converted into runtime memory text and later rendered inside `ReadingMemory`.

### Response

```text
After understanding the unit, let yourself respond as a reader.

Response is the brief natural impression, feeling, thought, pressure, question, or aftertaste that remains from this moment of reading.

Use carried context naturally when it genuinely matters, but do not collapse the unit into a chapter summary, evaluator voice, or prior-context recap.

Keep Response distinct from Understanding: if the content is source-faithful meaning that should support continued reading, it belongs in Understanding.

Keep Response distinct from Annotation: if the expression is tied to a specific source span and worth showing as a visible margin-note-style output, it belongs in Annotation.
```

Mapping from old prompt:

- Reuses `reading_impression` policy.
- Removes "what you now understand" from the definition.
- Keeps the anti-summary and anti-invention rules.

### Annotation

```text
When a line or small span genuinely asks to be marked, annotate it.

An Annotation is a visible margin-note-style response anchored to exact source text from the current unit.

It may be a line that lands with force, a margin-note thought or question, a natural connection, a distinction or turn that suddenly clarifies something, or a local trigger that feels worth marking.

Do not create an Annotation just to fill the field. It is acceptable to emit zero annotations. Default to 0-2.

Each Annotation must stay anchored to the current unit. Each `source_quote` must be an exact quote from this unit.

Choose each `source_quote` as the smallest self-sufficient span that can honestly stand as the annotation's footing.

If the unit contains multiple independently valuable local triggers, you may annotate them separately. Do not let one sharper later sentence erase an earlier framing line, premise line, or hinge line that also stands on its own.

Keep V1's wide-entry, narrow-expression stance: be willing to notice and surface a real local trigger, but do not manufacture commentary just to fill space.

If you callback to earlier material in visible content, speak naturally to the reader. Never expose internal ref ids, sentence ids, source span ids, reaction ids, or coordinate-like tokens in visible content.
```

Mapping from old prompt:

- Reuses `digest.surfaced_reaction_policy`.
- Reuses `digest.reaction_anchor_and_callback_policy`.
- Renames the output and instruction from reaction to annotation.
- Keeps exact-quote grounding.

### SourceGrounding

```text
- `annotations[].source_quote` must be a short exact contiguous span copied from the current unit: no ellipses, no stitched fragments, no paraphrase, no translation.
- Never invent source coordinates. The runner resolves source quotes to paragraph + char-offset `SourceRef` objects after Digest returns.
- Understanding is grounded in the current source unit as a whole; it does not need exact source quotes.
```

Mapping from old prompt:

- Rename `surfaced_reactions[].source_quote` to `annotations[].source_quote`.
- Rename Recent Reading Memory grounding to Understanding grounding.

### ResponseDiscipline

```text
- Do not output broad chapter summary.
- Do not explain whether you "used prior material".
- Do not decide or name the next route. After this read, the runner will settle the unit and advance normally.
- Return JSON only.
```

This can reuse the current response-discipline text.

## Target Output Contract

Recommended LLM-facing contract:

```json
{
  "understanding": "...",
  "response": "...",
  "annotations": [
    {
      "source_quote": "...",
      "content": "...",
      "prior_link": null,
      "outside_link": null,
      "search_intent": null
    }
  ]
}
```

Notes:

- `understanding` replaces `recent_reading_memory[].memory_text` at the model-facing level.
- `response` replaces `reading_impression`.
- `annotations` replaces `surfaced_reactions`.
- Digest no longer emits a content-type `kind`; Understanding remains content-neutral and retrieval should work from the text itself.
- `understanding` may be empty only for empty or purely structural units; runtime does not append an empty recent-memory entry.

Runtime mapping:

```text
understanding -> zero or one memory_uptake_ops[] entry -> recent_reading_memory store
response -> DigestResult.reading_impression
annotations[] -> DigestResult.surfaced_reactions
```

This keeps runtime state stable while making the LLM call semantically cleaner.

## Implementation Checklist

- Rename or add prompt fragments:
  - `digest.current_step`
  - `digest.understanding_policy`
  - `digest.response_policy`
  - `digest.annotation_policy`
  - `digest.annotation_grounding_and_callback_policy`
- Reshape `DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE`:
  - remove `ReadingBehavior`
  - remove `MemoryInstruction`
  - add direct children `Understanding`, `Response`, and `Annotation`
- Update source-grounding text:
  - `surfaced_reactions[].source_quote` -> `annotations[].source_quote`
  - `Recent Reading Memory entries` -> one holistic `Understanding`
- Update `OutputContract`:
  - `ReturnFormat`
  - field contracts
  - output contract name: `digest_understanding_response_annotation_json_v3`
- Update `llm_calls.digest(...)` normalizer:
  - parse `payload["understanding"]`
  - parse `payload["response"]`
  - parse `payload["annotations"]`
  - optionally ignore legacy fields rather than supporting them, depending on whether this is a hard cutover
- Update tests:
  - prompt XML structure contains direct `Understanding`, `Response`, `Annotation`
  - prompt XML no longer has `MemoryInstruction` or model-facing `RecentReadingMemory`
  - output contract no longer asks for `reading_impression`, `surfaced_reactions`, or `recent_reading_memory`
  - runtime still stores Understanding through `recent_reading_memory` append ops
- Update stable docs after implementation:
  - `docs/backend-reading-mechanisms/attentional_v2.md`
  - `docs/current-state.md`
  - `docs/tasks/registry.md`
  - `docs/tasks/registry.json`

## Open Questions

- Should the implementation be a hard LLM-facing field rename, or should it temporarily accept both old and new fields?
  - Default recommendation: hard rename for prompt/LLM-facing fields; keep only internal runtime mapping stable.
- Should `response` remain a single string?
  - Default recommendation: yes. It should stay compact and not compete with Understanding.
- Should `annotations` remain 0-2 by default?
  - Default recommendation: yes. The current density rule is working conceptually and should not be loosened in this semantic refactor.
- Should `understanding` be a list, object, or string?
  - Resolved implementation: one string. `understanding` may contain one sentence or several compact paragraphs when needed, but the model-facing field is not a list or object.
