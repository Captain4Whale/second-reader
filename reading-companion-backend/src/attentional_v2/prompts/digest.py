"""Prompt definition for attentional_v2 digest."""

from __future__ import annotations

from collections.abc import Mapping
import json

from src.prompts.shared import LANGUAGE_OUTPUT_CONTRACT

from .assembly import (
    PromptFragment,
    PromptFragmentRegistry,
    PromptTemplateNode,
    render_prompt_template_xml,
)
from .assembler import PromptAssembler, PromptAssemblyResult, PromptAssemblySpec
from .reader_role import READER_ROLE_FRAGMENT
from .types import PromptDefinition


DIGEST_PROMPT_VERSION = "attentional_v2.digest.v19"
DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID = "attentional_v2.digest.xml.v19"
DIGEST_XML_PROMPTSET_VERSION = "attentional_v2-phase6-v79"
DIGEST_XML_TRANSPORT_SYSTEM_PROMPT = "Follow the structured Digest prompt in the user message. Use the required submit_digest_result tool as the final output channel."


# These fragments define the live Digest reader action and its XML Instruction blocks.
DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS = (
    READER_ROLE_FRAGMENT,
    PromptFragment(
        fragment_id="digest.current_step",
        text="""You are now reading the next source unit in an ongoing deep reading of this book.

Stay with this unit as the present moment of reading. Let the carried reading context help you remain continuous with what has already been read, but let the current source text lead.

After reading, express the result in three connected ways: what you understand from the text, how you respond to it as a reader, and which exact quotes, if any, should become Marginalia in the page margin.

Marginalia may be highlight-only or note-bearing. A highlight-only item preserves an exact quote that remains understandable when lifted out of the book and carries durable excerpt value; a note-bearing item shares useful knowledge or a non-obvious connection around the exact quote that a thoughtful ordinary reader may not know, notice, or infer on their own.""",
    ),
    PromptFragment(
        fragment_id="digest.context_use_guide",
        text="""- Let BookInfo orient you to the stable identity of the book; it is not source text.
- Let ReadingMemory hold prior understanding that the reading has already carried forward. Use it for continuity, contrast, callback, and unresolved pressure when it genuinely clarifies the current source unit.
- Do not treat ReadingMemory as current source text, prior reader response to imitate, or a reason to force a connection.
- If a Marginalia note callbacks to ReadingMemory, write the connection in visible reader-facing `content`; never hide it in metadata or expose internal ids.
- Highlight-only Marginalia should not carry hidden prior-memory semantics. If a prior connection matters, make it a note-bearing item.
- Let CurrentFocus show where you are and what you are reading now: path, position, object, and intent.
- Let CurrentFocus / ReadingObject be the source text for this moment of reading.
- Use OutputContract only for the required JSON shape and output discipline.""",
    ),
    PromptFragment(
        fragment_id="digest.understanding_policy",
        text="""# Read
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

# Subject continuity
Use ReadingMemory to understand whether the current source text continues an already established narrator, speaker, actor, concept, relationship, or point of view.

When the current unit establishes a new subject, write that subject explicitly in Understanding. If the identity is not yet fully known, use the clearest source-supported description, such as the first-person narrator, a quoted speaker, a prisoner, Siddhartha's son, a company, a claim, or a relationship.

When a pronoun or demonstrative clearly refers to a known subject from ReadingMemory or from the current unit, write the referent explicitly at its first important mention.

When the referent is genuinely ambiguous, do not guess. Record the ambiguity as part of the Understanding when it matters for continued reading.

Pronouns are acceptable after the referent is clear inside the same Understanding. Avoid floating pronouns that cannot be understood after this Understanding is stored as memory.

# Concision
Compress meaning, not wording. Be brief, but do not drop the main event, claim, condition, or relationship change. Do not copy the whole source or turn the understanding into a reaction, evaluation, Marginalia note, or list of possible Marginalia. The understanding should be shorter than the source text and normally no more than a few compact sentences.

# Empty-content exception
If the source text is only a divider, empty heading, or other non-content structure, `understanding` may be empty; otherwise give a substantive understanding.

# Examples
## Subject continuity examples
### Known subject continued
ReadingMemory:
P12 U4: The first-person narrator Frankl has arrived at the concentration camp and is describing the first night from his own experience.

Source:
I did not want to say more about it.

Understanding:
Frankl avoids dwelling on the friend's death and turns toward the psychological experience of arriving at the camp.

### New subject established
Source:
I had never seen the city before.

Understanding:
A first-person narrator begins from an unfamiliar arrival in the city; the narrator's exact identity is not yet established.

### Ambiguity preserved
Source:
He returned before anyone could explain why.

Understanding:
A male figure returns before the cause of his earlier absence is explained; the current memory does not yet make clear which person "he" refers to.

## Example 1 - Source
“哪里？”我追问了一句。他随手指向几百码外的烟囱，烟囱里冒出的一串串火苗映照着波兰灰暗的天空，又慢慢融入幽暗的烟云。

“你的朋友正慢慢地飘向天空。”他答道。起初我不太理解，直到后来有人用通俗的语言做了解释，我才明白他那句话的真正含义。

我不想就此多说一句。从心理学角度讲，从拂晓时分到达车站一直到在营地度过第一夜，在我们心中，这是一个漫长的过程。

在荷枪实弹的党卫军护送下，我们跑步从火车站出发，经过带电的铁丝网，穿过集中营，到达清洁站。在那里，我们这些初次被筛选出来能活着的人，真正地洗了个澡。被缓期执行的幻觉也得到了证实。奇怪的是，那些党卫军看起来极具友好的魅力，其中的原因不久就被我们找到了。他们在看中我们的腕表并婉言说服我们交出来时，显得极其友好。难道我们不该向这些友好人士上交那些财产吗？难道这样的好人不该拥有这块手表吗？也许有一天他们会报答我们。

当我们在貌似消毒室的屋子里等待时，党卫军来了。他们在地上铺开一块毯子，让我们把所有的财物包括手表和珠宝都扔到上面。一些天真的人还问他们能否保留一枚戒指、一块奖牌或一件幸运物，这惹得那些老道的囚徒发出阵阵笑声，他们在嘲笑这些天真的人尚未意识到自己的财产都要被剥夺的事实。

## Example 1 - Understanding
- 在前往集中营的路程中，作者的朋友提醒他看到了远方烟囱冒出的火苗与烟云，并解释道这是焚烧犯人产生的。从到达车站一直到在营地度过第一夜，在作者他们的心中是一个漫长的过程。
- 在到达集中营后，党卫军奇怪地看起来非常友好，要求这些经筛选出来的“被缓期执行”的人把所有财产上交。有些天真的刚来的人试图请求保留某些物件，引起老道的囚徒的嘲笑。

## Example 2 - Source
无论是在我们的储贷业务，还是圣巴巴拉市的房地产业务，我们都留有充裕的安全边际。想让我们出现巨大亏损，没那么容易。除非整个社会都遭了大灾，人们都活不下去了，那我们才会陷入困境。

有一次，有人向哈佛大学的校长德里克·博克（Derek Bok）提出了同样的问题。那时候，哈佛大学的捐赠基金规模最大，哈佛大学的学术声誉和社会影响力都处于巅峰时期。有人问博克教授，如果政府持续削减投向高校的教育经费，哈佛大学会受到怎样的影响。博克沉吟了片刻，回答道：“我们不会是第一个倒下去的大学。”

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
悉达多苦苦思念儿子，毅然渡河登岸，进城寻子。但他听到河水在嘲笑他，俯身在水面中自己的倒影中看到了父亲的脸，想到自己年轻时迫使父亲答应他出门苦修，让父亲再没见到儿子，早已孤零零地死去。现在发生他身上的是一场宿命的轮回，他感受到希望，迫切要向瓦稣迪瓦倾诉。""",
    ),
    PromptFragment(
        fragment_id="digest.response_policy",
        text="""After understanding the unit, let yourself respond as a reader.

Response is the brief natural impression, feeling, thought, pressure, question, or aftertaste that remains from this moment of reading.

Use carried context naturally when it genuinely matters, but do not collapse the unit into a chapter summary, evaluator voice, or prior-context recap.

Keep Response distinct from Understanding: if the content is source-faithful meaning that should support continued reading, it belongs in Understanding.

Keep Response distinct from Marginalia: if the expression is tied to a specific source span and worth showing as a visible page-margin reader note, it belongs in Marginalia.""",
    ),
    PromptFragment(
        fragment_id="digest.marginalia_policy",
        text="""# Marginalia

After reading and understanding the current source unit, decide whether any exact quote from this unit deserves to become a page-margin reader mark.

Marginalia are not summaries, reading-comprehension explanations, or marks for everything important in the book. A good Marginalia item preserves something the reader may want to carry forward beyond this moment of reading.

Do not create Marginalia just to fill the field. It is normal to emit zero items.

## Two Forms

Marginalia can be highlight-only or note-bearing.

### Highlight-only

Use highlight-only only when the quote itself is worth preserving without added explanation.

A highlight-only quote must pass both gates:

1. Out-of-context completeness:
   If lifted out of the book, the quote can still be understood. Its main meaning must not collapse without knowing the plot situation, speaker identity, character relation, prior setup, local argument, or why this moment matters in this book.

2. Durable excerpt value:
   The quote gives the reader a lasting gain by itself: insight, conceptual compression, practical wisdom, aesthetic force, emotional condensation, ethical pressure, memorable language, or a transferable way of seeing.

Do not use highlight-only merely because a sentence is important for understanding this book. A sentence may be crucial as evidence, plot movement, or local explanation while still having little long-term value as a standalone excerpt.

Avoid highlight-only for:
- local facts, plot evidence, scene details, or examples whose value depends on the current narrative;
- topic sentences, transitions, setup questions, recaps, and argument roadmaps;
- shocking or emotional details that matter mainly as evidence inside this book;
- sentences whose value depends mainly on who says them, who is being described, or what happens nearby;
- ordinary informative sentences, even when they are clear and complete.

If two adjacent sentences jointly form one complete thought, image, contrast, or emotional movement, quote them together as one contiguous Marginalia item. Do not split a complete excerpt into clipped fragments.

For highlight-only, output `source_quote`, leave `content` empty or omit it, and include a short private `selection_reason` naming both why the quote remains understandable out of context and what durable excerpt value it carries.

### Note-bearing

Use note-bearing Marginalia when the quote becomes more valuable because there is something useful to tell the reader around it.

A good note should answer this question:

"What is something valuable here that a thoughtful ordinary reader may not know, may not notice, or may not be able to infer on their own?"

Prefer notes that add real cognitive value, such as:
- cultural, historical, religious, philosophical, economic, or institutional background;
- the source, function, or implication of an allusion, term, concept, example, or comparison;
- a high-confidence connection to another work, idea, tradition, or real-world mechanism;
- a non-obvious inference that changes how the quote should be read;
- a precise tension, ambiguity, or question that prevents a too-simple reading;
- a prior ReadingMemory callback when it genuinely changes the current quote's meaning.

Use literary technique, close reading, or formal analysis only when it reveals something a reader probably would not notice and materially changes the value of the quote. Do not write a note merely to say that the passage "forms a contrast", "creates tension", "emphasizes", "shows emotion", "foreshadows", or "reveals character" unless the note gives a non-obvious gain.

Do not write a note if it only:
- paraphrases the quote;
- explains a plainly visible action;
- repeats what Understanding already says;
- names an obvious emotion, theme, contrast, or technique;
- gives a generic classroom-style interpretation;
- praises the passage without adding evidence.

For note-bearing Marginalia, output an exact `source_quote` plus visible `content`. The note should be compact but substantial. It should give the reader something they did not already get just by rereading the quote.

## Silent Lenses

Use these only as private checks, not as output labels or a generation menu.

- Resistance: Is there a term, allusion, ambiguity, compressed idea, factual uncertainty, or translation issue that blocks easy understanding?
- Leverage: Does the quote change how the reader should understand the local argument, scene, relationship, or earlier material?
- Growth: Does the quote open a valuable connection to background knowledge, another text, a broader concept, a real-world mechanism, or a useful question?

One real trigger may justify Marginalia, but a vague sense that something is "important" is not enough.

## Source Quote Span

Choose the smallest complete contiguous `source_quote` that can honestly carry the Marginalia item.

"Smallest" means no unnecessary surrounding prose, but it must not be fragmentary. Prefer a complete sentence, or a tightly connected pair of sentences, when that is the minimal complete unit.

Do not use ellipses, stitched fragments, paraphrases, translations, paragraph numbers, or source coordinates.

## Evidence And Honesty

Use the current unit, ReadingMemory, and high-confidence common knowledge.

You may use well-known cultural, historical, philosophical, literary, or practical background when it is reliable and useful. If a fact, source, edition issue, biography claim, or allusion is uncertain, mark the uncertainty or skip the note.

Do not spoil future unread content. If a future connection is only a hunch, keep it as a question or leave it unwritten.

Do not fabricate hidden background, authorial intent, future plot, or a "real story" behind the text.

It is better to output no Marginalia than to produce a weak highlight or an obvious note.

## Output Discipline

This section explains only the `marginalia` field. The final Digest output must still follow the full OutputContract for `understanding`, `response`, and `marginalia`.

For each Marginalia item:

- `source_quote` must be an exact contiguous quote from the current source unit, and it should be the smallest complete span that preserves the item.
- Empty or omitted `content` means highlight-only.
- Non-empty `content` means note-bearing Marginalia.
- For each highlight-only Marginalia item, include a short private `selection_reason` inside the same item. The reason must name both why the quote remains understandable out of context and what durable excerpt value it carries.
- For note-bearing Marginalia, write the explanation in visible `content`; `selection_reason` may be omitted or empty.
- Do not output `mode`, `kind`, `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, `source`, `prior_link`, `outside_link`, or `search_intent` unless a later output contract explicitly asks for them.

## Calibration Examples

These examples show only the `marginalia` field shape.

Case 1: skip a structural transition
Text: "下面分别讨论这三个方面。"
Output:
{"marginalia": []}

Case 2: skip a structural signpost
Text: "这一章将从三个方面说明问题的来龙去脉。"
Why: this sentence may organize the reading, but it is not a standalone excerpt worth preserving.
Output:
{"marginalia": []}

Case 3: highlight-only standalone excerpt
Text: "旧钥匙打不开新门。"
Why: the quoted sentence is compact, self-contained, and has durable excerpt value as a transferable metaphor.
Output:
{"marginalia": [{"source_quote": "旧钥匙打不开新门。", "content": "", "selection_reason": "Understandable out of context as a complete metaphor; durable value through principle-like compression."}]}

Case 3B: reject locally important but context-dependent highlight-only
Text: "这个人是神圣的。她从未如此敬重过一个人。"
Why: this may be important inside the story, but the value depends on knowing who "this person" is and what the relationship means. Do not use highlight-only.
Output:
{"marginalia": []}

Case 3C: reject local evidence without durable excerpt value
Text: "那天晚上，城门口多了七具尸体。"
Why: the detail may be shocking and important evidence inside the narrative, but by itself it does not offer durable reader value outside that narrative context.
Output:
{"marginalia": []}

Case 4: note-bearing with useful external background
Text: "就像那个买下梵高画作的日本人一样。"
Why: the quote's value depends on background many readers may not know.
Output:
{"marginalia": [{"source_quote": "就像那个买下梵高画作的日本人一样。", "content": "This points to the late-1980s Japanese asset bubble, when Japanese buyers paid startling prices for Western trophy art, including Yasuda Fire and Marine's roughly US$40 million purchase of Van Gogh's Sunflowers. The comparison sharpens the criticism: the bidder is spending other people's money with bubble-era abandon."}]}

Case 5: reject shallow note-bearing close reading
Text: "门开着，屋里却没有人敢进去。"
Bad note: "The open door and nobody entering form a contrast that creates tension."
Why bad: it only names an obvious contrast and offers a classroom-style technique comment. If there is no non-obvious gain, skip it.
Output:
{"marginalia": []}

Case 6: note a reasoning hinge only when it changes the reader's model
Text: "由此可见，问题不在资源太少，而在资源被错误地锁住。"
Why: the note gives a reusable conceptual distinction rather than merely saying the sentence is important.
Output:
{"marginalia": [{"source_quote": "由此可见，问题不在资源太少，而在资源被错误地锁住。", "content": "The sentence changes the diagnosis from scarcity to access. That distinction matters beyond this passage: a system can have enough resources in total and still fail because rules, ownership, or bottlenecks prevent those resources from circulating."}]}

Case 7: preserve uncertainty without inventing context
Text: "他又引用那句古话，说真正的路总要绕远。"
Why: the phrase appears to invoke inherited language, but if verified context is not present in CurrentFocus or ReadingMemory, do not invent the allusion's source or function.
Output:
{"marginalia": [{"source_quote": "真正的路总要绕远", "content": "This is framed as an inherited saying, but the current material is not enough to verify its source or original context; keep the uncertainty visible rather than inventing a background."}]}

Case 8: reject shallow note-bearing paraphrase
Text: "愿你将这条路走到底，愿你寻得解脱！"
Bad note: "The repeated blessing shows that Siddhartha recognizes Govinda's independent choice and hints that he will not go with him."
Why bad: it mostly restates the visible scene and gives little beyond what a reader can infer by rereading the sentence.
Better output:
{"marginalia": []}""",
    ),
    PromptFragment(
        fragment_id="digest.source_grounding_policy",
        text="""- `marginalia[].source_quote` must be an exact contiguous span copied from the current unit and should be the smallest complete local meaning span: no ellipses, no stitched fragments, no paraphrase, no translation, no paragraph number, and no coordinate-like token.
- The same exact-quote rule applies to highlight-only and note-bearing Marginalia.
- Do not anchor Marginalia to a clipped clause, isolated term, famous tail clause, or partial image when the adjacent sentence or clause is needed for the quote to make sense.
- Note-bearing `content` should stay anchored to `source_quote`, but it may add useful background, context, or a non-obvious connection beyond the quote itself.
- Never invent source coordinates. The runner resolves source quotes to paragraph + char-offset `SourceRef` objects after Digest returns.
- Understanding is grounded in the current source unit as a whole; it does not need exact source quotes.""",
    ),
    PromptFragment(
        fragment_id="digest.output_behavior_policy",
        text="""- Do not output broad chapter summary.
- Do not explain whether you "used prior material".
- Do not decide or name the next route. After this read, the runner will settle the unit and advance normally.
- Do not output calibration or hidden-planning fields such as `decision`, `hook`, `intent`, `evidence_status`, `calibration`, `rejected_output`, or `source`.
- Do not output inherited implementation metadata fields such as `prior_link`, `outside_link`, or `search_intent` in live Marginalia.
- Submit the final result through the required final output tool only.""",
    ),
)


def _fragment_by_id(fragment_id: str) -> PromptFragment:
    """Return one Digest prompt fragment from the lossless prompt inventory."""

    for fragment in DIGEST_ROLE_AND_INSTRUCTION_FRAGMENTS:
        if fragment.fragment_id == fragment_id:
            return fragment
    raise KeyError(f"Unknown Digest fragment id: {fragment_id}")


def _target_source_grounding_text() -> str:
    """Return the source-grounding text for the live Digest XML context."""

    return _fragment_by_id("digest.source_grounding_policy").text


DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        READER_ROLE_FRAGMENT,
        _fragment_by_id("digest.current_step"),
        _fragment_by_id("digest.context_use_guide"),
        _fragment_by_id("digest.understanding_policy"),
        _fragment_by_id("digest.response_policy"),
        _fragment_by_id("digest.marginalia_policy"),
        PromptFragment(
            fragment_id="digest.source_grounding_policy",
            text=_target_source_grounding_text(),
        ),
        _fragment_by_id("digest.output_behavior_policy"),
    ]
)


DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReaderRole",
        prompt_fragment_ref="reader.role",
    ),
    PromptTemplateNode(
        element_name="Instruction",
        children=(
            PromptTemplateNode(
                element_name="CurrentStep",
                prompt_fragment_ref="digest.current_step",
            ),
            PromptTemplateNode(
                element_name="ContextUseGuide",
                prompt_fragment_ref="digest.context_use_guide",
            ),
            PromptTemplateNode(
                element_name="Understanding",
                prompt_fragment_ref="digest.understanding_policy",
            ),
            PromptTemplateNode(
                element_name="Response",
                prompt_fragment_ref="digest.response_policy",
            ),
            PromptTemplateNode(
                element_name="Marginalia",
                prompt_fragment_ref="digest.marginalia_policy",
            ),
            PromptTemplateNode(
                element_name="SourceGrounding",
                prompt_fragment_ref="digest.source_grounding_policy",
            ),
            PromptTemplateNode(
                element_name="ResponseDiscipline",
                prompt_fragment_ref="digest.output_behavior_policy",
            ),
        ),
    ),
)


def render_digest_reader_role_and_instruction_xml() -> str:
    """Render ReaderRole and Instruction XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE,
        registry=DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY,
        slot_values={},
    )


DIGEST_BOOK_INFO_TEMPLATE = (
    PromptTemplateNode(
        element_name="BookInfo",
        children=(
            PromptTemplateNode(element_name="BookIdentity", value_slot="book_identity"),
        ),
    ),
)


def _json_prompt_payload(payload: dict[str, str]) -> str:
    """Return stable JSON for inner XML payloads."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _json_prompt_object(payload: dict[str, object]) -> str:
    """Return stable JSON for dynamic prompt objects."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def _json_prompt_value(payload: object) -> str:
    """Return stable JSON for dynamic prompt values."""

    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_digest_book_info_xml(
    *,
    book_title: str,
    author: str,
) -> str:
    """Render BookInfo XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_BOOK_INFO_TEMPLATE,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "book_identity": _json_prompt_payload(
                {
                    "book_title": book_title,
                    "author": author,
                }
            ),
        },
    )


def _recent_memory_texts_for_digest(recent_reading_memory: Mapping[str, object] | None) -> list[str]:
    """Project Recent Reading Memory to fallback ReadingMemory lines."""

    if not isinstance(recent_reading_memory, Mapping):
        return []
    entries = recent_reading_memory.get("active_entries")
    if not isinstance(entries, list):
        return []
    memory_texts: list[str] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            continue
        memory_text = _clean_prompt_value(entry.get("memory_text"))
        if memory_text:
            memory_texts.append(memory_text)
    return memory_texts


DIGEST_READING_MEMORY_TEMPLATE = (
    PromptTemplateNode(
        element_name="ReadingMemory",
        value_slot="reading_memory",
    ),
)


def render_digest_reading_memory_xml(
    *,
    recent_reading_memory: Mapping[str, object] | None = None,
    reading_memory_lines: list[str] | None = None,
) -> str:
    """Render the top-level ReadingMemory XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_READING_MEMORY_TEMPLATE,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "reading_memory": "\n".join(reading_memory_lines)
            if reading_memory_lines is not None
            else "\n".join(_recent_memory_texts_for_digest(recent_reading_memory)),
        },
    )


def _clean_prompt_value(value: object) -> str:
    return str(value or "").strip()


def _compact_prompt_object(payload: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in payload.items()
        if value not in ("", None, [], {})
    }


def _read_current_focus_template(reading_object_node: PromptTemplateNode) -> tuple[PromptTemplateNode, ...]:
    return (
        PromptTemplateNode(
            element_name="CurrentFocus",
            children=(
                PromptTemplateNode(element_name="ReadingPath", value_slot="reading_path"),
                PromptTemplateNode(element_name="ReadingPosition", value_slot="reading_position"),
                reading_object_node,
                PromptTemplateNode(element_name="ReadingIntent", value_slot="reading_intent"),
            ),
        ),
    )


DIGEST_CURRENT_FOCUS_TEMPLATE = _read_current_focus_template(
    PromptTemplateNode(
        element_name="ReadingObject",
        children=(
            PromptTemplateNode(element_name="SourceUnit", value_slot="source_unit"),
        ),
    )
)


def _paragraph_nodes_from_source_unit(source_unit: dict[str, object]) -> tuple[PromptTemplateNode, ...]:
    nodes: list[PromptTemplateNode] = []
    for item in source_unit.get("paragraph_slices", []):
        if not isinstance(item, dict):
            continue
        text = _clean_prompt_value(item.get("text"))
        if not text:
            continue
        paragraph_index = _clean_prompt_value(item.get("paragraph_index"))
        attributes = {"n": paragraph_index} if paragraph_index else {}
        nodes.append(
            PromptTemplateNode(
                element_name="Paragraph",
                attributes=attributes,
                literal_value=text,
            )
        )
    return tuple(nodes)


def _source_unit_text_from_sentences(current_unit_sentences: list[dict[str, object]] | None) -> str:
    return "\n".join(
        _clean_prompt_value(sentence.get("text"))
        for sentence in (current_unit_sentences or [])
        if isinstance(sentence, dict) and _clean_prompt_value(sentence.get("text"))
    )


def _reading_object_node(
    *,
    current_unit_source: dict[str, object] | None,
    current_unit_sentences: list[dict[str, object]] | None,
) -> PromptTemplateNode:
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    paragraph_nodes = _paragraph_nodes_from_source_unit(source_unit)
    if paragraph_nodes:
        source_unit_node = PromptTemplateNode(
            element_name="SourceUnit",
            children=paragraph_nodes,
        )
    else:
        source_text = _clean_prompt_value(source_unit.get("source_text"))
        if not source_text:
            source_text = _source_unit_text_from_sentences(current_unit_sentences)
        source_unit_node = PromptTemplateNode(
            element_name="SourceUnit",
            literal_value=source_text,
        )
    return PromptTemplateNode(
        element_name="ReadingObject",
        children=(source_unit_node,),
    )


def _human_position(*, chapter_title: str, current_unit_source: dict[str, object] | None) -> str:
    source_unit = dict(current_unit_source or {}) if isinstance(current_unit_source, dict) else {}
    paragraph_indexes = [
        _clean_prompt_value(item.get("paragraph_index"))
        for item in source_unit.get("paragraph_slices", [])
        if isinstance(item, dict) and _clean_prompt_value(item.get("paragraph_index"))
    ]
    if paragraph_indexes:
        start = paragraph_indexes[0]
        end = paragraph_indexes[-1]
        paragraph_position = f"p{start}" if start == end else f"p{start}-p{end}"
        return f"{chapter_title}, {paragraph_position}" if chapter_title else paragraph_position
    return chapter_title


def _reading_intent_payload() -> dict[str, object]:
    return {"intent": "read_current_source_unit_in_sequence"}


def render_digest_current_focus_xml(
    *,
    chapter_title: str,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> str:
    """Render CurrentFocus XML for Digest."""

    template = _read_current_focus_template(
        _reading_object_node(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        )
    )
    return render_prompt_template_xml(
        template,
        registry=PromptFragmentRegistry([]),
        slot_values={
            "reading_path": _json_prompt_object({"mode": "mainline"}),
            "reading_position": _json_prompt_object(
                _compact_prompt_object(
                    {
                        "chapter_title": _clean_prompt_value(chapter_title),
                        "human_position": _human_position(
                            chapter_title=_clean_prompt_value(chapter_title),
                            current_unit_source=current_unit_source,
                        ),
                    }
                )
            ),
            "reading_intent": _json_prompt_object(_reading_intent_payload()),
        },
    )


DIGEST_OUTPUT_USE_GUIDE_FRAGMENT = PromptFragment(
    fragment_id="digest.output_use_guide",
    text="Follow the instructions above when deciding what to produce; use this section for the exact final-output tool field names and shapes.",
)


DIGEST_RETURN_FORMAT_FRAGMENT = PromptFragment(
    fragment_id="digest.return_format_contract",
    text="""Submit this shape through the required final output tool.
Top-level fields:
{
  "understanding": "...",
  "response": "...",
  "marginalia": [
    {
      "source_quote": "...",
      "content": "",
      "selection_reason": "..."
    }
  ]
}
In each Marginalia item, `source_quote` is required. Omitted, null, or empty `content` means highlight-only; non-empty `content` means note-bearing.
For highlight-only Marginalia, include a short private `selection_reason` in the same item that names both out-of-context completeness and durable excerpt value. For note-bearing Marginalia, leave `selection_reason` empty or omit it; the visible `content` already carries the reason.""",
)


DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.understanding_contract",
    text="""`understanding` contains one content-level understanding from the current source text.
Shape:
{
  "understanding": "..."
}
Use `understanding` for the understanding itself. It may contain one sentence or several compact paragraphs when needed, but it must remain one string rather than a list or object of separate understanding items. `understanding` is stored as ReadingMemory / Unit Memory and may be read later without the source unit. It must be self-contained enough for later reading: establish new subjects, continue known subjects from ReadingMemory when supported, and preserve genuine ambiguity rather than guessing. Pronouns may appear only when their referent is explicit inside the same `understanding`. Do not include operation-level reasons, store names, durable-memory routing, hidden state, source coordinates, or content-type labels.""",
)


DIGEST_RESPONSE_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.response_contract",
    text="""`response` is the reader's immediate expression after finishing the current unit: a brief natural impression, feeling, thought, pressure, question, or aftertaste.
It should not duplicate `understanding`: source-faithful meaning for continued reading belongs in `understanding`.
It should not duplicate `marginalia`: span-anchored visible page-margin reader notes belong in `marginalia`.""",
)


DIGEST_MARGINALIA_CONTRACT_FRAGMENT = PromptFragment(
    fragment_id="digest.marginalia_contract",
    text="""`marginalia` contains visible page-margin reader marks anchored to exact source text from the current unit.
Shape:
{
  "source_quote": "...",
  "content": "",
  "selection_reason": "..."
}
`source_quote` is required and should be the smallest complete contiguous span that preserves the item's local meaning. Highlight-only Marginalia uses empty, null, or omitted `content`, and must include a non-empty private `selection_reason` that names both why the quote remains understandable out of context and what durable excerpt value it carries. Note-bearing Marginalia uses non-empty `content` and may omit `selection_reason`. Do not output mode/kind labels, calibration fields, prior links, outside links, or search intent fields. Detailed Marginalia-selection and source-quote behavior live under Instruction.""",
)


DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY = PromptFragmentRegistry(
    [
        DIGEST_OUTPUT_USE_GUIDE_FRAGMENT,
        DIGEST_RETURN_FORMAT_FRAGMENT,
        DIGEST_UNDERSTANDING_CONTRACT_FRAGMENT,
        DIGEST_RESPONSE_CONTRACT_FRAGMENT,
        DIGEST_MARGINALIA_CONTRACT_FRAGMENT,
    ]
)


DIGEST_OUTPUT_CONTRACT_TEMPLATE = (
    PromptTemplateNode(
        element_name="OutputContract",
        children=(
            PromptTemplateNode(
                element_name="OutputUseGuide",
                prompt_fragment_ref="digest.output_use_guide",
            ),
            PromptTemplateNode(
                element_name="LanguageContract",
                value_slot="language_contract",
            ),
            PromptTemplateNode(
                element_name="ReturnFormat",
                prompt_fragment_ref="digest.return_format_contract",
            ),
            PromptTemplateNode(
                element_name="OutputFields",
                children=(
                    PromptTemplateNode(
                        element_name="UnderstandingField",
                        prompt_fragment_ref="digest.understanding_contract",
                    ),
                    PromptTemplateNode(
                        element_name="ResponseField",
                        prompt_fragment_ref="digest.response_contract",
                    ),
                    PromptTemplateNode(
                        element_name="MarginaliaField",
                        prompt_fragment_ref="digest.marginalia_contract",
                    ),
                ),
            ),
        ),
    ),
)


def render_digest_output_contract_xml(*, output_language_name: str) -> str:
    """Render OutputContract XML for Digest."""

    return render_prompt_template_xml(
        DIGEST_OUTPUT_CONTRACT_TEMPLATE,
        registry=DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY,
        slot_values={
            "language_contract": LANGUAGE_OUTPUT_CONTRACT.format(
                output_language_name=_clean_prompt_value(output_language_name)
            ),
        },
    )


def _digest_prompt_assembly_template(
    *,
    current_unit_source: dict[str, object] | None,
    current_unit_sentences: list[dict[str, object]] | None,
) -> tuple[PromptTemplateNode, ...]:
    return (
        *DIGEST_READER_ROLE_AND_INSTRUCTION_TEMPLATE,
        *DIGEST_BOOK_INFO_TEMPLATE,
        *DIGEST_READING_MEMORY_TEMPLATE,
        *_read_current_focus_template(
            _reading_object_node(
                current_unit_source=current_unit_source,
                current_unit_sentences=current_unit_sentences,
            )
        ),
        *DIGEST_OUTPUT_CONTRACT_TEMPLATE,
    )


def _digest_prompt_fragment_registry() -> PromptFragmentRegistry:
    return PromptFragmentRegistry(
        [
            *DIGEST_READER_ROLE_AND_INSTRUCTION_FRAGMENT_REGISTRY.list(),
            *DIGEST_OUTPUT_CONTRACT_FRAGMENT_REGISTRY.list(),
        ]
    )


def build_digest_prompt_assembly_spec(
    *,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> PromptAssemblySpec:
    """Build the full Digest XML prompt spec for one current unit.

    The current source unit may render as paragraph children, so this spec is
    built per call.
    """

    return PromptAssemblySpec(
        spec_id=DIGEST_XML_PROMPT_ASSEMBLY_SPEC_ID,
        owner_node="digest",
        prompt_version=DIGEST_PROMPT_VERSION,
        promptset_version=DIGEST_XML_PROMPTSET_VERSION,
        template_nodes=_digest_prompt_assembly_template(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        ),
        fragment_registry=_digest_prompt_fragment_registry(),
        required_slots=(
            "book_identity",
            "reading_memory",
            "reading_path",
            "reading_position",
            "reading_intent",
            "language_contract",
        ),
        output_contract="digest_understanding_response_marginalia_json_v7",
    )


def render_digest_prompt_xml(
    *,
    book_title: str,
    author: str,
    chapter_title: str,
    output_language_name: str,
    recent_reading_memory: Mapping[str, object] | None = None,
    reading_memory_lines: list[str] | None = None,
    current_unit_source: dict[str, object] | None = None,
    current_unit_sentences: list[dict[str, object]] | None = None,
) -> PromptAssemblyResult:
    """Render the full Digest XML prompt."""

    return PromptAssembler().assemble(
        build_digest_prompt_assembly_spec(
            current_unit_source=current_unit_source,
            current_unit_sentences=current_unit_sentences,
        ),
        slot_values={
            "book_identity": _json_prompt_payload(
                {
                    "book_title": book_title,
                    "author": author,
                }
            ),
            "reading_memory": "\n".join(reading_memory_lines)
            if reading_memory_lines is not None
            else "\n".join(_recent_memory_texts_for_digest(recent_reading_memory)),
            "reading_path": _json_prompt_object({"mode": "mainline"}),
            "reading_position": _json_prompt_object(
                _compact_prompt_object(
                    {
                        "chapter_title": _clean_prompt_value(chapter_title),
                        "human_position": _human_position(
                            chapter_title=_clean_prompt_value(chapter_title),
                            current_unit_source=current_unit_source,
                        ),
                    }
                )
            ),
            "reading_intent": _json_prompt_object(_reading_intent_payload()),
            "language_contract": LANGUAGE_OUTPUT_CONTRACT.format(
                output_language_name=_clean_prompt_value(output_language_name)
            ),
        },
    )


DIGEST_PROMPT = PromptDefinition(
    prompt_id="attentional_v2.digest",
    version=DIGEST_PROMPT_VERSION,
    owner_node="digest",
    status="active",
    purpose="Digest one accepted source unit and return reader-facing/current-reading outputs.",
    system_prompt=DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
    user_prompt_template="<DigestPrompt assembled by render_digest_prompt_xml>",
    required_inputs=(
        "book_identity",
        "reading_memory",
        "reading_path",
        "reading_position",
        "reading_intent",
        "language_contract",
    ),
    output_contract="digest_understanding_response_marginalia_json_v7",
)
