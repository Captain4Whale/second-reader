# Attentional_v2 Phase F4A Full Reaction Appendix

Run: `attentional_v2_f4a_quality_audit_20260419`

Purpose: expand the six-case F4A audit into a human-readable appendix that shows every audited unit, every surfaced reaction, the unit original text being read at that moment, and the exact anchor quote stored on the persisted reaction record.

Text-surface note: for segment-style and cross-chapter generated cases, the "unit original text" below is reconstructed from the run's `public/book_document.json`, which is the exact text surface the mechanism actually read during F4A. For `supremacy_private_en__chapter_13`, the source is the parsed full-book chapter output. The anchor quote is the persisted `primary_anchor.quote` from `reaction_records.json`.

Detour-review note: the final subsection of each case records a post-run reassessment of whether this case was actually a good detour sample under an 8-unit short-window audit.

## supremacy_private_en__chapter_13

- Book: `Supremacy`
- Goal in F4A: Reaction-density regression against the old low-expression problem.
- Formal units read: `8`
- Visible reactions: `7`
- Silent units: `2`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c13-s1 -> c13-s4` | reactions `0` | pressure `none` | preview: CHAPTER 7 Playing Games A short walk from London’s King Cross Station, where tourists flocked to see the magical train platform that Harry …
- Unit `2` | `c13-s5 -> c13-s7` | reactions `1` | pressure `none` | preview: For all the perks that DeepMind got from being part of Google, including the nap pods, massage rooms, and indoor gym, its founders were sti…
- Unit `3` | `c13-s8 -> c13-s13` | reactions `1` | pressure `none` | preview: Being in England and far removed from the relentless growth ethos that drove Silicon Valley, the founders took Google’s suggestion in good …
- Unit `4` | `c13-s14 -> c13-s21` | reactions `0` | pressure `frame_shift_pressure` | preview: That left hundreds of other researchers at DeepMind free to continue researching ways to build AGI. Once every few weeks, the founders woul…
- Unit `5` | `c13-s22 -> c13-s25` | reactions `1` | pressure `none` | preview: Hassabis’s brain would grapple for solutions, but they sometimes sounded a little off the wall. For instance, he’d suggest that as their AI…
- Unit `6` | `c13-s26 -> c13-s31` | reactions `2` | pressure `continuation_pressure` | preview: Tao had said in interviews that AI was largely clever mathematics and that the world would probably never have true AI. He saw the technolo…
- Unit `7` | `c13-s32 -> c13-s33` | reactions `1` | pressure `none` | preview: Hassabis imagined that as he got close to AGI, he’d stop pushing the performance of his AI models and then invite some of the world’s great…
- Unit `8` | `c13-s34 -> c13-s38` | reactions `1` | pressure `none` | preview: Suleyman disagreed with his cofounder’s approach, believing it far too focused on numbers and theory. He believed AI needed to be managed b…

### Detailed Units

#### Unit 1 — `c13-s1 -> c13-s4`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
CHAPTER 7 Playing Games
A short walk from London’s King Cross Station, where tourists flocked to see the magical train platform that Harry Potter took to Hogwarts, a different kind of magic was being created inside a gleaming collection of high-rise buildings jutting into the gray sky, their facades a blend of glass and metal cladding. Between them was a pretty promenade bustling with pedestrians. Some of them were the engineers and artificial intelligence scientists of DeepMind, fishing badges out of their pockets as they walked through the glass doors of an office building that officially belonged to Google but that had two floors devoted to their secretive AI lab.
```
- Surfaced reactions: none

#### Unit 2 — `c13-s5 -> c13-s7`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
For all the perks that DeepMind got from being part of Google, including the nap pods, massage rooms, and indoor gym, its founders were still trying to extricate themselves from the grip of their parent company, Alphabet. It had been more than two years since the acquisition, and the tech giant’s executives were dangling a new prospect in front of Demis Hassabis, Mustafa Suleyman, and Shane Legg. Instead of being an “autonomous unit,” DeepMind could become an “Alphabet company” with its own profit-and-loss statements.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s7:discern:1` | compat family: `discern`
Original reaction text: 'Extricate' is a notably strong verb for a supposed acquisition success story. Nap pods, massage rooms, indoor gym—yet the founders' posture toward Alphabet remains one of entrapment. The word 'grip' reinforces this. Two years in, and the desire to pull away hasn't softened.
Anchor quote from source text:
```text
its founders were still trying to extricate themselves from the grip of their parent company, Alphabet.
```
Anchor sentence ids: `c13-s5 -> c13-s5`
Anchor locator: `paragraph_index=3, char=0-221, href=xhtml/chapter7.xhtml`


#### Unit 3 — `c13-s8 -> c13-s13`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
Being in England and far removed from the relentless growth ethos that drove Silicon Valley, the founders took Google’s suggestion in good faith. Suleyman wanted to show that DeepMind could stand on its own two feet as a business, so he dove into proving out the value of its AI systems in the real world. He put renewed focus on a division he’d started called Applied, whose researchers used reinforcement learning techniques to tackle problems in healthcare, energy, and robotics to potentially turn into businesses. Another team of about twenty researchers, who called themselves DeepMind for Google, worked on projects that directly helped Google’s business, making YouTube’s recommendations more efficient, for instance, or improving Google’s ad targeting algorithms. Google agreed to give DeepMind 50 percent of the proceeds of the value that it added to those features, according to someone with knowledge of those agreements. About two-thirds of the projects ended up being useful to Google, another former staffer says.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s13:discern:2` | compat family: `discern`
Original reaction text: A 50/50 revenue split is not the language of a parent company nourishing a subsidiary. It reads more like a contract between equals. That the 'value added' is measured and then split introduces a mercenary precision into what was previously described as a philosophically fraught relationship.
Anchor quote from source text:
```text
Google agreed to give DeepMind 50 percent of the proceeds of the value that it added to those features
```
Anchor sentence ids: `c13-s12 -> c13-s12`
Anchor locator: `paragraph_index=4, char=773-933, href=xhtml/chapter7.xhtml`


#### Unit 4 — `c13-s14 -> c13-s21`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
That left hundreds of other researchers at DeepMind free to continue researching ways to build AGI. Once every few weeks, the founders would meet at a London pub to talk shop, and their discussions would arrive at familiar points of tension. Suleyman wanted to solve real-world problems but also worried they could inadvertently build a superintelligent system that would go awry. What if the AI got out of its box and manipulated people? he asked. In the office he warned other staff and managers that AGI’s impact on the economy could lead to a sudden displacement of millions of jobs and plummeting incomes. What if that led to an uprising? “People will be walking up to Kings Cross with pitchforks if we don’t think about equality,” he’d say, according to a former staff member.
```
- Surfaced reactions: none

#### Unit 5 — `c13-s22 -> c13-s25`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
Hassabis’s brain would grapple for solutions, but they sometimes sounded a little off the wall. For instance, he’d suggest that as their AI got more powerful and potentially dangerous, DeepMind could hire Terence Tao, a professor at University of California, Los Angeles, who was widely regarded as one of the world’s greatest living mathematicians. A former child prodigy who went to college at the age of nine, Tao had become known as a Mr. Fix-It for frustrated researchers, according to New Scientist magazine.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s25:discern:3` | compat family: `discern`
Original reaction text: The word 'off' carries a slight dismissiveness—a distance between Hassabis's brainstorming and the reader's expected logic. Yet the suggestion to hire a world-class mathematician to address AI danger is not absurd on its face; it's the pairing with the qualifier that makes it curious. Why preemptively hire Tao, specifically? The answer would require knowing what problem Hassabis was trying to solve, which the unit withholds.
Anchor quote from source text:
```text
they sometimes sounded a little off the wall
```
Anchor sentence ids: `c13-s22 -> c13-s22`
Anchor locator: `paragraph_index=6, char=0-95, href=xhtml/chapter7.xhtml`


#### Unit 6 — `c13-s26 -> c13-s31`

- Boundary: `paragraph_end`
- Pressure signals: `continuation_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
Tao had said in interviews that AI was largely clever mathematics and that the world would probably never have true AI. He saw the technology in the same mechanistic and almost black-and-white way that Hassabis did. If AI got out of control, math could contain it. Hassabis wasn’t alone in believing that. On Yudkowsky’s LessWrong forum, members had engaged in a lengthy project to brainstorm how they might convince someone like Tao and other top mathematicians to work on AI alignment, the practice of making AI more “aligned” to human values to prevent it going rogue. They tossed out figures of between $5 million and $10 million for how much these math luminaries would need to be paid.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s31:discern:4` | compat family: `discern`
Original reaction text: Tao is being recruited to work on AI alignment problems by people who believe AI poses an existential risk—but Tao himself apparently doesn't believe true AI will ever exist. The recruitment logic is circular: the problem you're being hired to solve is, by your own stated view, probably not a real problem. Yet the unit treats this as a viable recruiting target, which sharpens the gap between the earnestness of the alignment community and the skepticism of its most-cited mathematician.
Anchor quote from source text:
```text
Tao had said in interviews that AI was largely clever mathematics and that the world would probably never have true AI.
```
Anchor sentence ids: `c13-s26 -> c13-s26`
Anchor locator: `paragraph_index=7, char=0-119, href=xhtml/chapter7.xhtml`

2. Reaction id: `rx:Chapter_7:c13-s31:discern:5` | compat family: `discern`
Original reaction text: The casualness of 'tossed out' contrasts with the specificity of the numbers. These forum members aren't speculating loosely—they're doing the arithmetic of influence, as if math talent has a market price and the fee will unlock the alignment problem. The figure itself is noteworthy: $5–10M is a generous salary for a mathematician, but a rounding error against the compute investments being discussed elsewhere in the book.
Anchor quote from source text:
```text
They tossed out figures of between $5 million and $10 million for how much these math luminaries would need to be paid.
```
Anchor sentence ids: `c13-s31 -> c13-s31`
Anchor locator: `paragraph_index=7, char=572-691, href=xhtml/chapter7.xhtml`


#### Unit 7 — `c13-s32 -> c13-s33`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
Hassabis imagined that as he got close to AGI, he’d stop pushing the performance of his AI models and then invite some of the world’s greatest minds to come and analyze them down to the minutest detail so that they could help figure out the best calculations to contain them. “Maybe we should start putting out the call, an almost ‘Avengers Assemble’ of mathematicians and scientists,” Hassabis still says today.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s33:discern:6` | compat family: `discern`
Original reaction text: The word "contain" is the local hinge. Previous units discussed recruiting mathematicians for alignment work, but this unit makes containment explicit: the goal is not just analysis but restraint. Hassabis imagines AGI as a system requiring calculations to keep it bounded—mechanistic control through math, echoing Tao's worldview but applied to the containment problem rather than the creation problem.
Anchor quote from source text:
```text
they could help figure out the best calculations to contain them
```
Anchor sentence ids: `c13-s32 -> c13-s32`
Anchor locator: `paragraph_index=8, char=0-275, href=xhtml/chapter7.xhtml`


#### Unit 8 — `c13-s34 -> c13-s38`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
Suleyman disagreed with his cofounder’s approach, believing it far too focused on numbers and theory. He believed AI needed to be managed by people, not just clever math, to make it safe. As he and Hassabis debated the best strategy for containing AI, they got another update from Google’s leadership about the plan to become an “Alphabet company.” That idea wasn’t going to work after all, the executives told them. Spinning out wasn’t straightforward because as AI had become increasingly valuable to Google’s business, the larger company needed DeepMind even more.
```
- Surfaced reactions:

1. Reaction id: `rx:Chapter_7:c13-s38:discern:7` | compat family: `discern`
Original reaction text: This is a local hinge worth tracking. The unit has been building a picture of Hassabis as someone who believes containment is a mathematical problem. Suleyman now explicitly rejects that framing—he wants human management, not just theory. This introduces a philosophical fault line between the two founders that the previous units hadn't surfaced directly: one wants to solve safety through math, the other through people and governance. The word "managed" is doing real work here—it positions AI as requiring ongoing human oversight, not a one-time containment calculation.
Anchor quote from source text:
```text
He believed AI needed to be managed by people, not just clever math, to make it safe.
```
Anchor sentence ids: `c13-s35 -> c13-s35`
Anchor locator: `paragraph_index=9, char=102-187, href=xhtml/chapter7.xhtml`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low`
- Why: These eight units mostly form a self-contained chapter opening about DeepMind, Alphabet, and the Hassabis/Suleyman disagreement. The local text keeps reintroducing its own context, so a backward hop was not naturally required.
- Verdict on case choice for detour validation: Not a strong detour-validation case under an 8-unit cap.

## value_of_others_private_en__8_10

- Book: `The Value of Others`
- Goal in F4A: English cross-chapter carryover style and prior-link audit.
- Formal units read: `8`
- Visible reactions: `6`
- Silent units: `3`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c1-s1 -> c1-s1` | reactions `0` | pressure `none` | preview: Chapter 2
- Unit `2` | `c1-s2 -> c1-s2` | reactions `0` | pressure `none` | preview: CHAPTER 2
- Unit `3` | `c1-s3 -> c1-s6` | reactions `0` | pressure `none` | preview: SEXUAL RELATIONSHIPS ARE TRANSACTED IN THE SEXUAL MARKETPLACE That seems straightforward enough. However, despite the ubiquity of the sexua…
- Unit `4` | `c1-s7 -> c1-s12` | reactions `2` | pressure `frame_shift_pressure` | preview: In the first place, it’s important to understand that the sexual marketplace is not relegated to online dating sites or local meat markets.…
- Unit `5` | `c1-s13 -> c1-s14` | reactions `1` | pressure `none` | preview: This makes people uncomfortable because the possibility represented by the marketplace is a potential chaos that is always threatening to d…
- Unit `6` | `c1-s15 -> c1-s17` | reactions `1` | pressure `frame_shift_pressure` | preview: It is the Wild West that lurks at the heart of even the most repressive civilizations. It is a lawless free-for-all that will never be comp…
- Unit `7` | `c1-s18 -> c1-s21` | reactions `1` | pressure `none` | preview: In any case, the sexual marketplace is everywhere, and the interaction between any two adults could potentially lead to a sexual encounter.…
- Unit `8` | `c1-s22 -> c1-s26` | reactions `1` | pressure `none` | preview: If the sexual marketplace is coincident with the social world, then – on some level – we can’t avoid locating ourselves within that marketp…

### Detailed Units

#### Unit 1 — `c1-s1 -> c1-s1`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
Chapter 2
```
- Surfaced reactions: none

#### Unit 2 — `c1-s2 -> c1-s2`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
CHAPTER 2
```
- Surfaced reactions: none

#### Unit 3 — `c1-s3 -> c1-s6`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
SEXUAL RELATIONSHIPS ARE TRANSACTED IN THE SEXUAL MARKETPLACE
That seems straightforward enough. However, despite the ubiquity of the sexual marketplace, how it tends to operate is not entirely obvious. So let’s take a closer look, shall we?
```
- Surfaced reactions: none

#### Unit 4 — `c1-s7 -> c1-s12`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
In the first place, it’s important to understand that the sexual marketplace is not relegated to online dating sites or local meat markets. Quite the contrary: the sexual marketplace is everywhere. Though we may not like to admit it, the sexual marketplace is functionally coincident with the social world. This is because any two adults can initiate a sexual relationship at any time, irrespective of the differences in their age, wealth, attractiveness, or relationship status. Every day, new sexual relationships are initiated despite the ethical, moral, and – in some cases – legal prohibitions against doing so. That certain sexual relationships remain present even in contexts in which they are punishable by death is a testament to the irrepressible omnipresence of the sexual marketplace.
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s12:discern:1` | compat family: `discern`
Original reaction text: This 'irrespective of' clause is doing significant framing work. It asserts that formal or practical obstacles to sexual initiation are irrelevant to the underlying logic—which positions the marketplace not as something people navigate or negotiate, but as a background condition that simply exists wherever adults are. This framing has consequences: it makes resistance to the framework look like denial rather than critique.
Anchor quote from source text:
```text
any two adults can initiate a sexual relationship at any time, irrespective of the differences in their age, wealth, attractiveness, or relationship status.
```
Anchor sentence ids: `c1-s10 -> c1-s10`
Anchor locator: `paragraph_index=5, char=307-479`

2. Reaction id: `rx:Full_Content:c1-s12:discern:2` | compat family: `discern`
Original reaction text: 'A testament to' is rhetorical testimony rather than evidence. The claim that sexual relationships exist under death penalty does not establish a 'marketplace' in any economic or exchange-theoretic sense—it establishes that desire persists under extreme threat. The inferential leap from 'sex happens even when forbidden' to 'a marketplace is omnipresent' is not yet argued.
Anchor quote from source text:
```text
That certain sexual relationships remain present even in contexts in which they are punishable by death is a testament to the irrepressible omnipresence of the sexual marketplace.
```
Anchor sentence ids: `c1-s12 -> c1-s12`
Anchor locator: `paragraph_index=5, char=617-796`


#### Unit 5 — `c1-s13 -> c1-s14`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
This makes people uncomfortable because the possibility represented by the marketplace is a potential chaos that is always threatening to disrupt the stability of their everyday lives. Sex – because of its connection to the propagation of life – remains an untamed (and untamable) force of nature.
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s14:discern:3` | compat family: `discern`
Original reaction text: The parenthetical '(and untamable)' is doing rhetorical work beyond the surface claim. It anticipates and preempts the counterargument before anyone makes it. By saying 'untamed (and untamable),' the text forestalls the obvious objection: that human societies have always attempted to regulate, channel, or suppress sexual behavior. The self-correction closes the door on this line of thinking. This is a different move than the earlier 'irrespective of' clause—that one neutralized obstacles. This one neutralizes the very possibility of resistance to the framing.
Anchor quote from source text:
```text
Sex – because of its connection to the propagation of life – remains an untamed (and untamable) force of nature.
```
Anchor sentence ids: `c1-s14 -> c1-s14`
Anchor locator: `paragraph_index=6, char=185-297`


#### Unit 6 — `c1-s15 -> c1-s17`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
It is the Wild West that lurks at the heart of even the most repressive civilizations. It is a lawless free-for-all that will never be completely subjugated to order, and this is how it has always been. That contemporary sexual behavior is judged by some as increasingly shameless or permissive is less the result of a shift in sexual predilection than it is a change in the social reinforcement contingencies surrounding the acceptability of sexuality in the public sphere.
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s17:discern:4` | compat family: `discern`
Original reaction text: This phrase brings a more analytical register into the text. The author is now offering a specific explanatory framework—judgments of permissiveness are attributed not to actual behavioral change but to changed social contingencies governing public acceptability. This is more worked than the earlier declarative peaks. Worth tracking whether this framework becomes a sustained analytical tool or just a single concession before the rhetoric resumes.
Anchor quote from source text:
```text
social reinforcement contingencies surrounding the acceptability of sexuality in the public sphere
```
Anchor sentence ids: `c1-s17 -> c1-s17`
Anchor locator: `paragraph_index=6, char=501-772`


#### Unit 7 — `c1-s18 -> c1-s21`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
In any case, the sexual marketplace is everywhere, and the interaction between any two adults could potentially lead to a sexual encounter. The fact that most interactions do not lead to a sexual encounter does not necessarily mean that they couldn’t in the future or that the interaction occurred outside of the marketplace. It simply means that at least one of the parties involved did not consider the projected benefits of such an encounter to sufficiently exceed the possible costs, risks, and liabilities. This contributes to a net neutral (or net negative) valuation, which is transmuted into indifference (or disgust).
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s21:discern:5` | compat family: `discern`
Original reaction text: The language of 'costs, risks, and liabilities' is strikingly legalistic and transactional. It treats the decision not to pursue a sexual encounter as an active cost-benefit calculation that came up negative. The text has moved from declaring the marketplace omnipresent to now supplying an internal mechanism—yet the mechanism itself is asserted, not demonstrated. The underlying claim that people mentally weight 'liabilities' against projected benefits before declining a sexual opportunity is doing significant work without independent support.
Anchor quote from source text:
```text
It simply means that at least one of the parties involved did not consider the projected benefits of such an encounter to sufficiently exceed the possible costs, risks, and liabilities.
```
Anchor sentence ids: `c1-s20 -> c1-s20`
Anchor locator: `paragraph_index=7, char=326-511`


#### Unit 8 — `c1-s22 -> c1-s26`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
If the sexual marketplace is coincident with the social world, then – on some level – we can’t avoid locating ourselves within that marketplace. We don’t have to opt in, and we can’t really opt out. This can be distressing to a lot of people because it is generally uncomfortable to be sexualized against one’s will. The best we can do is communicate on as many levels as possible that we are “closed for business.” Just keep in mind that most shops are willing to transact after hours for the right price.
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s26:discern:6` | compat family: `discern`
Original reaction text: The final sentence reverses the pragmatic consolation of s25 without signaling the reversal. 'Closed for business' is presented as the best available response—and then immediately qualified with a scenario that renders it conditional on insufficient inducement. The economic logic from the prior unit (net valuation of costs vs. benefits) resurfaces here as a mechanism for overriding stated refusal. The effect is that the coping strategy becomes part of the problem: the transactional frame treats even explicit closure as a provisional price point, not a boundary.
Anchor quote from source text:
```text
Just keep in mind that most shops are willing to transact after hours for the right price.
```
Anchor sentence ids: `c1-s26 -> c1-s26`
Anchor locator: `paragraph_index=8, char=416-506`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low-to-medium`
- Why: Although this case was constructed from chapters 8-10, the first eight units stayed inside one contiguous argumentative block. The reader could critique the claims locally without needing to re-open earlier source material. If we want detour here, we need a later or more cross-referential slice.
- Verdict on case choice for detour validation: Weak detour sample for this short-window audit.

## huochu_shengming_de_yiyi_private_zh__segment_1

- Book: `活出生命的意义`
- Goal in F4A: Chinese restrained mainline sample.
- Formal units read: `8`
- Visible reactions: `8`
- Silent units: `3`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c1-s1 -> c1-s1` | reactions `0` | pressure `none` | preview: 第一部分 在集中营的经历
- Unit `2` | `c1-s2 -> c1-s2` | reactions `0` | pressure `frame_shift_pressure` | preview: 第一部分 在集中营的经历
- Unit `3` | `c1-s3 -> c1-s4` | reactions `2` | pressure `frame_shift_pressure` | preview: 首先申明，这并不是对某些事实的陈述，而是有关我个人经历的记录，同时也是对数以百万的囚徒经历过的事件的记录。 这是由一名集中营的幸存者亲口讲述的故事。
- Unit `4` | `c1-s5 -> c1-s6` | reactions `2` | pressure `none` | preview: 故事的焦点不是大家常听到的有关集中营的恐怖遭遇，而是一些小的磨难。 换句话说，就是想要回答一个问题：集中营的日常生活是如何反映在普通囚徒的思想中的？
- Unit `5` | `c1-s7 -> c1-s16` | reactions `0` | pressure `none` | preview: 文中所描述的多数事件并不发生在诸如奥斯维辛这样著名的大集中营，而是一些小的集中营，事实上死亡大多发生在这些小集中营。 本书的主人公不是平日里受人景仰的大英雄、烈士，也不是那些有名的囚头——就是狱中充当临时财产托管人并享有特权的囚犯——或者一些有名的囚徒。 本书不是名人的受难记，…
- Unit `6` | `c1-s17 -> c1-s19` | reactions `1` | pressure `none` | preview: 对于没有经历过集中营生活的人来说，很容易对有过这种经历的人抱有一种错误的同情心态。 外人对于囚徒之间为了生存的残酷斗争一无所知。 这是一场为了每天的面包、为了生活、为了朋友的斗争。
- Unit `7` | `c1-s20 -> c1-s24` | reactions `2` | pressure `none` | preview: 首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。 但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。 转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。 谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间…
- Unit `8` | `c1-s25 -> c1-s25` | reactions `1` | pressure `none` | preview: 每次转移都会转走一定数量的囚徒。

### Detailed Units

#### Unit 1 — `c1-s1 -> c1-s1`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
第一部分　在集中营的经历
```
- Surfaced reactions: none

#### Unit 2 — `c1-s2 -> c1-s2`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
第一部分 在集中营的经历
```
- Surfaced reactions: none

#### Unit 3 — `c1-s3 -> c1-s4`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
首先申明，这并不是对某些事实的陈述，而是有关我个人经历的记录，同时也是对数以百万的囚徒经历过的事件的记录。 这是由一名集中营的幸存者亲口讲述的故事。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s4:highlight:1` | compat family: `highlight`
Original reaction text: '亲口讲述'——这个表述强调了声音的直接性，区分于转述或编写的历史记录。将见证者身份与叙事行为直接绑定，承诺了一种第一人称的、不可替代的视角。
Anchor quote from source text:
```text
这是由一名集中营的幸存者亲口讲述的故事。
```
Anchor sentence ids: `c1-s4 -> c1-s4`
Anchor locator: `paragraph_index=3, char=53-73`

2. Reaction id: `rx:Full_Content:c1-s4:highlight:2` | compat family: `highlight`
Original reaction text: '个人经历的记录'与'事实陈述'的区分——这是一个认识论声明：这里呈现的是体验的真实，而非客观事实的复现。同时，'数以百万'的量词将个人叙事锚定在集体规模上。
Anchor quote from source text:
```text
首先申明，这并不是对某些事实的陈述，而是有关我个人经历的记录，同时也是对数以百万的囚徒经历过的事件的记录。
```
Anchor sentence ids: `c1-s3 -> c1-s3`
Anchor locator: `paragraph_index=3, char=0-53`


#### Unit 4 — `c1-s5 -> c1-s6`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
故事的焦点不是大家常听到的有关集中营的恐怖遭遇，而是一些小的磨难。 换句话说，就是想要回答一个问题：集中营的日常生活是如何反映在普通囚徒的思想中的？
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s6:highlight:3` | compat family: `highlight`
Original reaction text: "小的磨难"——这个表述与集中营叙事的常见期待形成反张力。通常的集中营书写指向大屠杀、死亡、毒气室等极端恐怖，而这里承诺的是一种微观聚焦。"小"既可能指规模，也可能指事件本身的日常性。这个词的选择预告了一种去戏剧化的叙事策略。
Anchor quote from source text:
```text
故事的焦点不是大家常听到的有关集中营的恐怖遭遇，而是一些小的磨难。
```
Anchor sentence ids: `c1-s5 -> c1-s5`
Anchor locator: `paragraph_index=3, char=73-106`

2. Reaction id: `rx:Full_Content:c1-s6:highlight:4` | compat family: `highlight`
Original reaction text: "反映在……思想中的"——这个措辞将心理过程本身视为叙事对象。不是问"发生了什么"，而是问"如何被体验和加工"。这与之前的"个人经历的记录"而非"事实陈述"形成呼应：见证者的任务不是还原事件，而是呈现经验的心理折射。
Anchor quote from source text:
```text
集中营的日常生活是如何反映在普通囚徒的思想中的？
```
Anchor sentence ids: `c1-s6 -> c1-s6`
Anchor locator: `paragraph_index=3, char=106-146`


#### Unit 5 — `c1-s7 -> c1-s16`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
文中所描述的多数事件并不发生在诸如奥斯维辛这样著名的大集中营，而是一些小的集中营，事实上死亡大多发生在这些小集中营。 本书的主人公不是平日里受人景仰的大英雄、烈士，也不是那些有名的囚头——就是狱中充当临时财产托管人并享有特权的囚犯——或者一些有名的囚徒。 本书不是名人的受难记，而是将注意力集中在那些不为人所知、没有记录在案的遇难者所遭受的磨难和死亡。 书中讲述的正是这些普通的囚徒，他们没有戴着表明身份和特权的袖箍，却时常遭到囚头的轻视。 当普通囚徒饥寒交迫时，囚头们却衣食无忧。 不夸张地说，许多囚头在集中营的日子甚至要比以前任何时候都好。 与看守相比，这些人更为凶狠，在鞭打囚徒时更为残忍。 当然，集中营挑选这一类人也有自己的标准，那就是性格要适合这份工作，而且，一旦这些人没有遵照指令完成任务，那么他们的职位也会不保。 不久，他们就会变得与纳粹的看守一样。 人们可以以纳粹看守的心理来判断这些人的心理状态。
```
- Surfaced reactions: none

#### Unit 6 — `c1-s17 -> c1-s19`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
对于没有经历过集中营生活的人来说，很容易对有过这种经历的人抱有一种错误的同情心态。 外人对于囚徒之间为了生存的残酷斗争一无所知。 这是一场为了每天的面包、为了生活、为了朋友的斗争。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s19:highlight:5` | compat family: `highlight`
Original reaction text: "面包、生活、朋友"这三个具体对象将生存竞争落实为日常伦理困境。为了自己的面包是否意味着夺取他人的面包？为了生活是否意味着牺牲他人的生活？为了朋友是否意味着背叛朋友？这三个"为了"之间可能存在不可调和的冲突。
Anchor quote from source text:
```text
这是一场为了每天的面包、为了生活、为了朋友的斗争。
```
Anchor sentence ids: `c1-s19 -> c1-s19`
Anchor locator: `paragraph_index=5, char=63-88`


#### Unit 7 — `c1-s20 -> c1-s24`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
首先让我以一次转移为例：有时集中营会将某囚犯转移到另一集中营。 但通常情况下，这种迁徙就是一次死亡之旅，终点站是毒气室。 转移的囚犯多半是那些基本丧失劳动力的体弱多病者，他们会被送往设有毒气室和焚烧炉的中心集中营。 谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。 其中，最重要的是将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s24:highlight:6` | compat family: `highlight`
Original reaction text: 「争取自由和生存」——这里将转移名单的争夺定性为「争取自由」，而非单纯的避死。这种表述揭示了囚徒内部竞争的认知框架：被选中留下被视为一种积极成就，而非仅仅免于被选中送走。这个价值框架本身就构成了囚徒思想的一部分。
Anchor quote from source text:
```text
谁将成为死亡之旅成员的选择过程，意味着囚徒个人之间或者群体之间将会为了争取自由和生存而斗争。
```
Anchor sentence ids: `c1-s23 -> c1-s23`
Anchor locator: `paragraph_index=6, char=105-151`

2. Reaction id: `rx:Full_Content:c1-s24:highlight:7` | compat family: `highlight`
Original reaction text: 「旅客」这一称呼的讽刺性：被送往毒气室的人被称为「旅客」，他们的旅程被称为「死亡之旅」。这种语言本身就构成了制度对囚徒的再定义——将灭绝包装为正常的旅行与转运。划去名字的行为则是一种代理决策：不是你亲手杀人，而是你选择让谁的名字留在名单上。
Anchor quote from source text:
```text
将自己或朋友的名字从旅客名单中划去，尽管每个人心里都明白，自己或朋友的胜出就意味着另一个的死亡。
```
Anchor sentence ids: `c1-s24 -> c1-s24`
Anchor locator: `paragraph_index=6, char=151-207`


#### Unit 8 — `c1-s25 -> c1-s25`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
每次转移都会转走一定数量的囚徒。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s25:highlight:8` | compat family: `highlight`
Original reaction text: 「一定数量」这个词表面中性，实则预设了规模前提——不是全部人，而是固定名额。这个数字的存在本身就定义了囚徒必须争夺的「槽位」数量。它为后续名单操作提供了可量化的结构性压力。
Anchor quote from source text:
```text
每次转移都会转走一定数量的囚徒。
```
Anchor sentence ids: `c1-s25 -> c1-s25`
Anchor locator: `paragraph_index=7, char=0-16`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low`
- Why: This opening is mostly authorial framing and setup. The questions it raises are interpretive, but they are answered by continuing forward inside the same passage rather than by recovering a missing earlier anchor.
- Verdict on case choice for detour validation: Reasonable non-detour sample; no obvious missed backward read.

## xidaduo_private_zh__segment_1

- Book: `悉达多`
- Goal in F4A: Detour narrow-scope to land-region sample.
- Formal units read: `8`
- Visible reactions: `7`
- Silent units: `3`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c1-s1 -> c1-s1` | reactions `0` | pressure `none` | preview: 婆罗门之子
- Unit `2` | `c1-s2 -> c1-s3` | reactions `0` | pressure `none` | preview: 婆罗门之子 悉达多，俊美的婆罗门[1]之子，年轻的鹰隼，在屋舍阴凉处，在河岸船旁的阳光中，在婆罗双林和无花果树的浓荫下，与他的好友，同为婆罗门之子的乔文达一道长大。
- Unit `3` | `c1-s4 -> c1-s10` | reactions `0` | pressure `none` | preview: 他浅亮的臂膀，在河边沐浴时，在神圣的洗礼和祭祀中，被阳光晒黑。 芒果林的树影，在孩童嬉戏间，在母亲的歌声里，在智慧父亲的教诲中，在至高无上的牲礼上，潜入他的黑眸。 悉达多早已加入智者的交谈。 他和乔文达一道修习辩论，修习参禅的艺术及冥想的功夫。 他已学会无声地念诵“唵”[2]这…
- Unit `4` | `c1-s11 -> c1-s12` | reactions `1` | pressure `none` | preview: 欢喜涌上他父亲的心头。 这个善悟而渴慕知识的儿子将成长为伟大的贤士和僧侣，成长为婆罗门中的王。
- Unit `5` | `c1-s13 -> c1-s13` | reactions `1` | pressure `none` | preview: 母亲看见儿子落座，起身；看见悉达多，她强壮英俊、四肢修长的儿子，以完美的礼仪向她问安，幸福便在胸中跃动。
- Unit `6` | `c1-s14 -> c1-s14` | reactions `1` | pressure `none` | preview: 年轻的婆罗门女儿们看见悉达多以王者之姿走过城中街巷，额头清朗，背影颀长，心中不免泛起爱情的涟漪。
- Unit `7` | `c1-s15 -> c1-s22` | reactions `2` | pressure `none` | preview: 而最爱他的人是乔文达。 他爱悉达多的目光和仁慈的嗓音；他爱他的步态，他行动时的优雅完美。 他爱悉达多的一切言行，但更爱他的精神，他崇高激昂的思想、强大的意志和高贵的使命感。 乔文达知道：悉达多不会成为卑劣的婆罗门，腐败的祭司，贪婪施咒的商贩，虚荣空洞的辩术士；他也不会成为邪恶奸…
- Unit `8` | `c1-s23 -> c1-s25` | reactions `2` | pressure `none` | preview: 所有人都热爱悉达多。 悉达多令所有人喜悦。 所有人都对他兴致勃勃。

### Detailed Units

#### Unit 1 — `c1-s1 -> c1-s1`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
婆罗门之子
```
- Surfaced reactions: none

#### Unit 2 — `c1-s2 -> c1-s3`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
婆罗门之子
悉达多，俊美的婆罗门[1]之子，年轻的鹰隼，在屋舍阴凉处，在河岸船旁的阳光中，在婆罗双林和无花果树的浓荫下，与他的好友，同为婆罗门之子的乔文达一道长大。
```
- Surfaced reactions: none

#### Unit 3 — `c1-s4 -> c1-s10`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
他浅亮的臂膀，在河边沐浴时，在神圣的洗礼和祭祀中，被阳光晒黑。 芒果林的树影，在孩童嬉戏间，在母亲的歌声里，在智慧父亲的教诲中，在至高无上的牲礼上，潜入他的黑眸。 悉达多早已加入智者的交谈。 他和乔文达一道修习辩论，修习参禅的艺术及冥想的功夫。 他已学会无声地念诵“唵”[2]这一辞中之辞，无声地、聚精会神地在呼吸间吐纳这辞。 这时，清明的心灵之光闪耀在他的前额。 他已学会体认内在不朽的阿特曼[3]，同宇宙合一。
```
- Surfaced reactions: none

#### Unit 4 — `c1-s11 -> c1-s12`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
欢喜涌上他父亲的心头。 这个善悟而渴慕知识的儿子将成长为伟大的贤士和僧侣，成长为婆罗门中的王。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s12:discern:1` | compat family: `discern`
Original reaction text: "婆罗门中的王"——这一表述叠加在"贤士和僧侣"之上，引入宗教权威的维度。父亲此刻的欢喜既是对儿子灵性禀赋的确认，也是外部世界对悉达多未来的投射性期待。这两个句子里，父亲的视角与悉达多此前的内在修习形成对照：张力不在于冲突，而在于方向——一个是已完成的内在境界，一个是尚未发生的外部命运。
Anchor quote from source text:
```text
成长为婆罗门中的王
```
Anchor sentence ids: `c1-s12 -> c1-s12`
Anchor locator: `paragraph_index=4, char=11-46`


#### Unit 5 — `c1-s13 -> c1-s13`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
母亲看见儿子落座，起身；看见悉达多，她强壮英俊、四肢修长的儿子，以完美的礼仪向她问安，幸福便在胸中跃动。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s13:highlight:2` | compat family: `highlight`
Original reaction text: 母亲的情感反应是即时而身体化的——幸福在胸中"跃动"。这与前句父亲复杂的权威期许形成温度对比。父亲的欢喜是投射向未来的，母亲的欢喜是此刻当下的。这种差异在同一个家庭、同一个"完美的儿子"身上，却呈现出截然不同的质地。
Anchor quote from source text:
```text
幸福便在胸中跃动
```
Anchor sentence ids: `c1-s13 -> c1-s13`
Anchor locator: `paragraph_index=5, char=0-52`


#### Unit 6 — `c1-s14 -> c1-s14`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
年轻的婆罗门女儿们看见悉达多以王者之姿走过城中街巷，额头清朗，背影颀长，心中不免泛起爱情的涟漪。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s14:highlight:3` | compat family: `highlight`
Original reaction text: "以王者之姿"——父亲口中的"婆罗门中的王"，此刻经由年轻女子们的目光折射出来。这个意象在家庭内部的精神期许与外部的社会目光之间发生了传递。它不再是父亲的语言，而是这些年轻女儿们眼中所见。父亲的投射已经扩散为一种公共形象。
Anchor quote from source text:
```text
以王者之姿
```
Anchor sentence ids: `c1-s14 -> c1-s14`
Anchor locator: `paragraph_index=6, char=0-48`


#### Unit 7 — `c1-s15 -> c1-s22`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
而最爱他的人是乔文达。 他爱悉达多的目光和仁慈的嗓音；他爱他的步态，他行动时的优雅完美。 他爱悉达多的一切言行，但更爱他的精神，他崇高激昂的思想、强大的意志和高贵的使命感。 乔文达知道：悉达多不会成为卑劣的婆罗门，腐败的祭司，贪婪施咒的商贩，虚荣空洞的辩术士；他也不会成为邪恶奸诈的僧侣，信众中善良愚蠢的羔羊。 不，即便是他乔文达也不愿成为那样的人。 他不想做千万庸碌的婆罗门中的一员。 他要追随他，为人拥戴而神圣的悉达多。 他要追随他，当悉达多成了神，抵达无量光明的世界，他仍要做他的朋友，他的随从，他的仆人，他的侍卫，他的影子。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s22:discern:4` | compat family: `discern`
Original reaction text: "成了神"——乔文达在此刻使用的是一个完成时的确信，而非假设性的期待。他看见的不是一个可能的未来，而是一个必然的终点。这种宗教确信与父亲"婆罗门中的王"构成同一话语方向的不同层级：父亲叠加的是权威，乔文达叠加的是神性。但这个确信本身埋下了张力——后文中的悉达多将踏上完全不同的道路，而乔文达将以追随者的身份经历漫长的困惑。
Anchor quote from source text:
```text
当悉达多成了神，抵达无量光明的世界
```
Anchor sentence ids: `c1-s22 -> c1-s22`
Anchor locator: `paragraph_index=7, char=206-259`

2. Reaction id: `rx:Full_Content:c1-s22:discern:5` | compat family: `discern`
Original reaction text: 乔文达对"精神"的辨识精确而内行——"崇高激昂的思想"、"强大的意志"、"高贵的使命感"。这不是旁观者的赞叹，而是一个同样在修习之路上的人对另一个人的辨认。乔文达在悉达多身上看见的是一种可以被追随的东西：他自己的意志、使命感、对平庸的拒绝。这里隐含着一种对称——乔文达也是那个不满足于"千万庸碌婆罗门"的人，他只是尚未找到自己的路，而是将悉达多的道路视为自己的道路。
Anchor quote from source text:
```text
他爱悉达多的一切言行，但更爱他的精神，他崇高激昂的思想、强大的意志和高贵的使命感
```
Anchor sentence ids: `c1-s17 -> c1-s17`
Anchor locator: `paragraph_index=7, char=43-84`


#### Unit 8 — `c1-s23 -> c1-s25`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
所有人都热爱悉达多。 悉达多令所有人喜悦。 所有人都对他兴致勃勃。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s25:discern:6` | compat family: `discern`
Original reaction text: 全称陈述"所有人"是一个修辞收束点。此前三段视角各具特异性——父亲的权威期许、母亲的身体性欢喜、年轻女子的情爱涟漪、乔文达的宗教确信——而此刻它们被统一为"所有人"。这种全称化本身就是一种叙事节奏的标记：它为不可阻挡的外部热爱定型，也就在为"热爱所指向的人走向相反方向"预备张力。
Anchor quote from source text:
```text
所有人都热爱悉达多。
```
Anchor sentence ids: `c1-s23 -> c1-s23`
Anchor locator: `paragraph_index=8, char=0-10`

2. Reaction id: `rx:Full_Content:c1-s25:highlight:7` | compat family: `highlight`
Original reaction text: "令"字指向一种被动性的情感结构：所有人作为被愉悦的对象，悉达多作为愉悦的施予者。这种主客关系在后文悉达多自身的精神旅程中将发生根本性翻转——他将不再是施予者，而是追寻者；将不再令人喜悦，而是令人困惑。
Anchor quote from source text:
```text
悉达多令所有人喜悦。
```
Anchor sentence ids: `c1-s24 -> c1-s24`
Anchor locator: `paragraph_index=8, char=10-20`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low-to-medium`
- Why: The opening of 《悉达多》 is rich in projection and foreshadowing, but it does not yet create a concrete unresolved backward-reference problem. True detour pressure is more likely later in the book, once earlier spiritual claims need to be reopened against later experience.
- Verdict on case choice for detour validation: Poor detour-validation case in this exact early-window form.

## nawaer_baodian_private_zh__segment_1

- Book: `纳瓦尔宝典（硅谷投资人纳瓦尔十年人生智慧，教你如何获得财富与幸福。新时代创业者的《穷查理宝典》）`
- Goal in F4A: Short local anchored reactions and prior-link sample.
- Formal units read: `8`
- Visible reactions: `8`
- Silent units: `2`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c1-s1 -> c1-s1` | reactions `0` | pressure `none` | preview: 认识财富创造的原理
- Unit `2` | `c1-s2 -> c1-s3` | reactions `1` | pressure `none` | preview: 认识财富创造的原理 能学会。
- Unit `3` | `c1-s4 -> c1-s8` | reactions `2` | pressure `none` | preview: [78]假设有一天，我创业失败，身无分文，这时把我随意丢到任何一个说英语的国家的街道上，我相信自己会在5年或10年内重新变得富有，因为我已经掌握了“赚钱”这门技巧，而这门技巧人人都赚钱跟工作的努力程度没什么必然联系。 即使每周在餐厅拼命工作80个小时，也不可能发财。 要想获得财…
- Unit `4` | `c1-s9 -> c1-s10` | reactions `1` | pressure `none` | preview: 如果还不知道自己应该做什么，那么你先要弄清楚这个问题。 在这之前，不要盲目发力。
- Unit `5` | `c1-s11 -> c1-s13` | reactions `1` | pressure `frame_shift_pressure` | preview: 十三四岁时，我就给自己列出一系列原则，详见下面的推特风暴。 30年来，我一直谨记这些原则，也在生活和工作中践行这些原则。 随着时间的推移，我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
- Unit `6` | `c1-s14 -> c1-s17` | reactions `0` | pressure `continuation_pressure` | preview: 下面推特风暴的内容，其中的推文广为流传，当然，每条都可以衍生出一个小时的谈话内容。 这条推特风暴是一个很好的起点。 我在其中写下了我所有的理念和原则，力求信息密集、简洁有力、影响广泛、历久弥新。 如果你能吸收这些理念和原则，以此为指引，奋斗10年，你就一定能够得偿所愿。
- Unit `7` | `c1-s18 -> c1-s19` | reactions `1` | pressure `none` | preview: [77] 如何致富（不靠运气）：
- Unit `8` | `c1-s20 -> c1-s24` | reactions `2` | pressure `continuation_pressure` | preview: ∨ 追求财富，而不是金钱或地位。 财富是指在你睡觉时仍能为你赚钱的资产。 金钱是我们转换时间和财富的方式。 地位是你在社会等级体系中所处的位置。

### Detailed Units

#### Unit 1 — `c1-s1 -> c1-s1`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
认识财富创造的原理
```
- Surfaced reactions: none

#### Unit 2 — `c1-s2 -> c1-s3`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
认识财富创造的原理
能学会。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s3:highlight:1` | compat family: `highlight`
Original reaction text: 三字断言的重量。「能学会。」置于章节标题之后，既非论证亦非解释，而是一个纯宣告——将「财富创造」从不可控的外部条件重新框架为可习得技能。这是一种认知重置，而非内容传递。
Anchor quote from source text:
```text
能学会。
```
Anchor sentence ids: `c1-s3 -> c1-s3`
Anchor locator: `paragraph_index=3, char=0-4`


#### Unit 3 — `c1-s4 -> c1-s8`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
[78]假设有一天，我创业失败，身无分文，这时把我随意丢到任何一个说英语的国家的街道上，我相信自己会在5年或10年内重新变得富有，因为我已经掌握了“赚钱”这门技巧，而这门技巧人人都赚钱跟工作的努力程度没什么必然联系。 即使每周在餐厅拼命工作80个小时，也不可能发财。 要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。 与埋头苦干相比，更重要的是理解和思考。 当然，努力非常重要，不能吝啬自己的努力，但必须选择正确的方式。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s8:highlight:2` | compat family: `highlight`
Original reaction text: 极端场景本身即宣告：不是在讲故事，是在立旗。「5年或10年」不是模糊乐观，而是一个有结构的时间承诺，隐含对系统可迁移性的笃信——技能属于人本身，不依附于原始资源或特定市场。
Anchor quote from source text:
```text
假设有一天，我创业失败，身无分文，这时把我随意丢到任何一个说英语的国家的街道上，我相信自己会在5年或10年内重新变得富有，因为我已经掌握了“赚钱”这门技巧，而这门技巧人人都赚钱跟工作的努力程度没什么必然联系。
```
Anchor sentence ids: `c1-s4 -> c1-s4`
Anchor locator: `paragraph_index=3, char=4-112`

2. Reaction id: `rx:Full_Content:c1-s8:highlight:3` | compat family: `highlight`
Original reaction text: 「做什么、和谁一起做、什么时候做」——三个维度恰好对应决策、协作、时机。构成一个简洁的三元框架，而这三个维度恰好都不是「努力」本身。这是在为整章的底层逻辑结构预埋桩子。
Anchor quote from source text:
```text
要想获得财富，你就必须知道做什么、和谁一起做、什么时候做。
```
Anchor sentence ids: `c1-s6 -> c1-s6`
Anchor locator: `paragraph_index=3, char=136-165`


#### Unit 4 — `c1-s9 -> c1-s10`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
如果还不知道自己应该做什么，那么你先要弄清楚这个问题。 在这之前，不要盲目发力。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s10:highlight:4` | compat family: `highlight`
Original reaction text: "盲目"这个词精准地锁定了前文所否定的路径——不是努力本身有问题，而是无方向的使劲儿。该句在三元框架刚铺完之后就立刻加了一道"先别动手"的门卫，把"做什么"从框架元素升级为第一优先级的前提条件。
Anchor quote from source text:
```text
在这之前，不要盲目发力。
```
Anchor sentence ids: `c1-s10 -> c1-s10`
Anchor locator: `paragraph_index=4, char=27-39`


#### Unit 5 — `c1-s11 -> c1-s13`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
十三四岁时，我就给自己列出一系列原则，详见下面的推特风暴。 30年来，我一直谨记这些原则，也在生活和工作中践行这些原则。 随着时间的推移，我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s13:highlight:5` | compat family: `highlight`
Original reaction text: 括号内的自我设问是一个值得注意的裂口。前文一直以客观语气讲述可迁移技巧的机制，这里突然出现第一人称的价值判断犹豫——"抓住财富"这个动作本身，在作者眼中并非全然正面的。它可能是本书为数不多的道德留白，暗示财富获取存在某种作者不愿直接辩护的灰色质地。
Anchor quote from source text:
```text
随着时间的推移，我发现自己愈加擅长观察企业，并从中找到最能创造财富的杠杆支点，然后抓住这部分财富（这种特长说不上是可悲还是幸运）。
```
Anchor sentence ids: `c1-s13 -> c1-s13`
Anchor locator: `paragraph_index=5, char=59-124`


#### Unit 6 — `c1-s14 -> c1-s17`

- Boundary: `paragraph_end`
- Pressure signals: `continuation_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
下面推特风暴的内容，其中的推文广为流传，当然，每条都可以衍生出一个小时的谈话内容。 这条推特风暴是一个很好的起点。 我在其中写下了我所有的理念和原则，力求信息密集、简洁有力、影响广泛、历久弥新。 如果你能吸收这些理念和原则，以此为指引，奋斗10年，你就一定能够得偿所愿。
```
- Surfaced reactions: none

#### Unit 7 — `c1-s18 -> c1-s19`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
[77]
如何致富（不靠运气）：
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s19:discern:6` | compat family: `discern`
Original reaction text: 标题中"不靠运气"四字是一个精确的结构锚点。它不是修饰性补充，而是对全章核心论断的第二次显性锁定——第一次在c1-s6的"要想获得财富，你就必须知道做什么、和谁一起做、什么时候做"，本次以标题形式再次宣示。两次锁定之间夹着作者的个人实践史，现在方法论的正式输出即将展开。
Anchor quote from source text:
```text
如何致富（不靠运气）：
```
Anchor sentence ids: `c1-s19 -> c1-s19`
Anchor locator: `paragraph_index=7, char=0-11`


#### Unit 8 — `c1-s20 -> c1-s24`

- Boundary: `paragraph_end`
- Pressure signals: `continuation_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
∨
追求财富，而不是金钱或地位。 财富是指在你睡觉时仍能为你赚钱的资产。 金钱是我们转换时间和财富的方式。 地位是你在社会等级体系中所处的位置。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s24:highlight:7` | compat family: `highlight`
Original reaction text: 这一定义精确地将「财富」与「劳动收入」切割开来——不是你在场时赚的钱，而是你缺席时依然运转的机制。副词「仍然」与「睡觉时」的搭配是一个严格的时间限定，它规定了财富的不可替代特性：被动性与持续性。
Anchor quote from source text:
```text
财富是指在你睡觉时仍能为你赚钱的资产。
```
Anchor sentence ids: `c1-s22 -> c1-s22`
Anchor locator: `paragraph_index=9, char=14-33`

2. Reaction id: `rx:Full_Content:c1-s24:highlight:8` | compat family: `highlight`
Original reaction text: 这一排除句将三种目标置于同一评价轴上，但只肯定财富。金钱被降格为转换工具，地位被归入社会博弈——两者均非「睡觉时仍能为你赚钱」的资产类别。这句作为开篇定义组的第一句话，同时也是整组定义的方向宣言。
Anchor quote from source text:
```text
追求财富，而不是金钱或地位。
```
Anchor sentence ids: `c1-s21 -> c1-s21`
Anchor locator: `paragraph_index=9, char=0-14`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low`
- Why: The units are manifesto-like and heavily self-defining. They build a method and vocabulary locally, so the reader can stay on the page and still react richly. No strong reason to jump backward appeared in the first eight units.
- Verdict on case choice for detour validation: Good density/style sample, but not a detour sample.

## mangge_zhi_dao_private_zh__segment_1

- Book: `芒格之道：查理·芒格股东会讲话 1987—2022`
- Goal in F4A: Defer-detour and outside-link/search-intent risk sample.
- Formal units read: `8`
- Visible reactions: `4`
- Silent units: `5`
- Detour trace count: `0`

### Unit Overview

- Unit `1` | `c1-s1 -> c1-s1` | reactions `0` | pressure `frame_shift_pressure` | preview: 1987年 西科金融股东会讲话
- Unit `2` | `c1-s2 -> c1-s2` | reactions `0` | pressure `none` | preview: 1987年 西科金融股东会讲话
- Unit `3` | `c1-s3 -> c1-s4` | reactions `2` | pressure `frame_shift_pressure` | preview: 编者按 1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial …
- Unit `4` | `c1-s5 -> c1-s5` | reactions `0` | pressure `none` | preview: 在1987年2月致西科金融股东的信中，查理·芒格披露了公司1986年的营收数据：1986年合并净运营收益（不计投资收益）为1193.4万美元，每股1.68美元；合并净收益为1652.4万美元，每股2.32美元。
- Unit `5` | `c1-s6 -> c1-s6` | reactions `1` | pressure `none` | preview: 1985年和1986年的合并净收益分解如下（收益单位为千美元，每股单位为美元）：
- Unit `6` | `c1-s7 -> c1-s7` | reactions `0` | pressure `none` | preview: 注1：美国政府国民抵押贷款协会。
- Unit `7` | `c1-s8 -> c1-s10` | reactions `0` | pressure `none` | preview: 1987年4月28日，西科在洛杉矶召开了股东会。 芒格在会上介绍了储贷、保险和精密钢材各板块近期的业务状况，展望了一些发展趋势。 他也分享了对好的管理者的看法、所坚持的收购风格，以及对“谦卑”这种品质的洞见。
- Unit `8` | `c1-s11 -> c1-s11` | reactions `1` | pressure `none` | preview: 在当时那个时点上，我们还要注意到，芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。

### Detailed Units

#### Unit 1 — `c1-s1 -> c1-s1`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
1987年 西科金融股东会讲话
```
- Surfaced reactions: none

#### Unit 2 — `c1-s2 -> c1-s2`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
1987年 西科金融股东会讲话
```
- Surfaced reactions: none

#### Unit 3 — `c1-s3 -> c1-s4`

- Boundary: `paragraph_end`
- Pressure signals: `frame_shift_pressure`
- Detour need emitted: `none`
- Unit original text:
```text
编者按
1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s4:highlight:1` | compat family: `highlight`
Original reaction text: 标记为'编者按'意味着此段为编者添加的说明性文字，而非西科金融或讲话原文本身。这暗示后续可能直接切入巴菲特/芒格的正式讲话内容。
Anchor quote from source text:
```text
编者按
```
Anchor sentence ids: `c1-s3 -> c1-s3`
Anchor locator: `paragraph_index=3, char=0-3`

2. Reaction id: `rx:Full_Content:c1-s4:highlight:2` | compat family: `highlight`
Original reaction text: 三机构地理分布跨度大（加州、芝加哥、奥马哈），业务性质差异明显（储蓄、钢铁制造、再保险），1979年收购精密钢材的时间节点值得关注。
Anchor quote from source text:
```text
1987年时，西科金融有三个主要的分支机构：（1）位于加州帕萨迪纳的互助储蓄；（2）精密钢材（Precision Steel），由西科金融于1979年收购，总部位于芝加哥，从事钢铁制品批发和贴牌金属专用产品生产；（3）西科—金融保险公司（Wesco-Financial Insurance Company），总部位于奥马哈，主要从事再保险业务。
```
Anchor sentence ids: `c1-s4 -> c1-s4`
Anchor locator: `paragraph_index=4, char=0-172`


#### Unit 4 — `c1-s5 -> c1-s5`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
在1987年2月致西科金融股东的信中，查理·芒格披露了公司1986年的营收数据：1986年合并净运营收益（不计投资收益）为1193.4万美元，每股1.68美元；合并净收益为1652.4万美元，每股2.32美元。
```
- Surfaced reactions: none

#### Unit 5 — `c1-s6 -> c1-s6`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
1985年和1986年的合并净收益分解如下（收益单位为千美元，每股单位为美元）：
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s6:highlight:3` | compat family: `highlight`
Original reaction text: 关键结构信号：此句引入的表覆盖"1985年和1986年"两年对比，而c1-s5仅呈现1986年汇总数字。这个两年对比的维度意味着编者有意让读者看到收益的年度变化趋势，不只是静止快照。
Anchor quote from source text:
```text
1985年和1986年的合并净收益分解如下（收益单位为千美元，每股单位为美元）：
```
Anchor sentence ids: `c1-s6 -> c1-s6`
Anchor locator: `paragraph_index=6, char=0-40`


#### Unit 6 — `c1-s7 -> c1-s7`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
注1：美国政府国民抵押贷款协会。
```
- Surfaced reactions: none

#### Unit 7 — `c1-s8 -> c1-s10`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
1987年4月28日，西科在洛杉矶召开了股东会。 芒格在会上介绍了储贷、保险和精密钢材各板块近期的业务状况，展望了一些发展趋势。 他也分享了对好的管理者的看法、所坚持的收购风格，以及对“谦卑”这种品质的洞见。
```
- Surfaced reactions: none

#### Unit 8 — `c1-s11 -> c1-s11`

- Boundary: `paragraph_end`
- Pressure signals: `none`
- Detour need emitted: `none`
- Unit original text:
```text
在当时那个时点上，我们还要注意到，芒格反复指出，目前好的投资和收购机会均缺乏，明显感觉到市场环境不妙，但又表示实在没有预测未来的能力，只是对累积起来的风险感到不安。
```
- Surfaced reactions:

1. Reaction id: `rx:Full_Content:c1-s11:highlight:4` | compat family: `highlight`
Original reaction text: 这句揭示了一种值得注意的认知张力：承认"无法预测"的同时仍表达"对风险不安"。这并非自我矛盾——它区分了概率预判与风险感知的差异。对读者而言，这提示后续芒格分享的实际内容可能带有防御性保守倾向，而非自信的市场择时建议。
Anchor quote from source text:
```text
实在没有预测未来的能力，只是对累积起来的风险感到不安。
```
Anchor sentence ids: `c1-s11 -> c1-s11`
Anchor locator: `paragraph_index=9, char=0-82`


### Detour Reassessment

- Detour pressure judgment after rereading the audited window: `low`
- Why: This slice is mostly editorial framing, company background, and table setup. It encourages restraint more than backward recovery. The right failure mode to watch here is over-explaining or over-expanding, not missing a detour.
- Verdict on case choice for detour validation: Not a realistic detour sample in the audited window.
