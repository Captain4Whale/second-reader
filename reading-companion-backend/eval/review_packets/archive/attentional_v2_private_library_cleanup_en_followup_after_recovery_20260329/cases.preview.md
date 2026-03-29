# Revision/Replacement Packet `attentional_v2_private_library_cleanup_en_followup_after_recovery_20260329`

This packet was generated automatically from cases whose current `benchmark_status` requires another hardening round.

## Dataset
- dataset_id: `attentional_v2_private_library_excerpt_en_v2`
- family: `excerpt_cases`
- language_track: `en`
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

## 1. `poor_charlies_almanack_private_en__10__seed_1`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `Poor Charlie's Almanack`
- author: `Charles T. Munger`
- chapter: `The Munger Approach to Life, Learning, and Decision Making` (`10`)
- question_ids: ``
- phenomena: ``
- selection_reason: Illustrates that accounting provides only approximations and requires judgment about limitations, such as depreciation estimates and the Carl Braun example
- judge_focus: Does the response correctly identify that accounting is a starting point with inherent limitations, not precise knowledge?
- latest_review_action: `revise`
- latest_problem_types: `text_noise|ambiguous_focus`
- latest_revised_bucket: `accounting_knowledge`
- latest_notes: The excerpt content is substantively valid—coherent discussion of accounting limitations with concrete examples. However, critical metadata fields (case_title, question_ids, phenomena, selection_reason, judge_focus) remain entirely empty, preventing proper benchmark evaluation. The 'C.E. Braun' line break should be corrected to restore proper readability. The excerpt also trails off mid-thought with the Carl Braun anecdote, losing potential context. Revise with complete metadata population before re-evaluation—not a drop since the underlying content is sound.

```text
But you have to know enough about it to understand its limitations-because although accounting is the starting place, it's only a crude approximation.
And it's not very hard to understand its limitations.
For example, everyone can see that you have to more or less just guess at the useful life of a jet airplane or anything like that.
Just because you express the depreciation rate in neat numbers doesn't make it anything you really know.
In terms of the limitations of accounting, one of my favorite stories involves a very great businessman named Carl Braun who created the C.
E Braun Engineering Company.
It designed and built oil refineries-which is very hard to do.
```

## 2. `steve_jobs_private_en__17__seed_1`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `Steve Jobs`
- author: `Walter Isaacson`
- chapter: `Chapter Eight: Xerox and Lisa: Graphical User Interfaces` (`17`)
- question_ids: ``
- phenomena: ``
- selection_reason: Illustrates Apple's parallel development strategy in 1979 through three simultaneous projects (Apple III, Lisa, and Raskin's low-cost machine) that would eventually compete for the company's future direction.
- judge_focus: Evaluate whether the model correctly identifies all three Apple projects mentioned in the excerpt and understands they were presented as parallel simultaneous efforts rather than sequential ones. Assess whether the model recognizes the skunkworks project (Raskin's machine) as representing an alternative vision for affordable personal computing.
- latest_review_action: `revise`
- latest_problem_types: `too_easy`
- latest_revised_bucket: `technology_history`
- latest_notes: Four consecutive review rounds flagged this case as too_easy, and the adversarial reviewer confirms the excerpt aligns almost verbatim with the judge focus through explicit markers ('three ponies,' 'parallel,' 'alternative vision'). While the primary reviewer rated it a 'keep,' the consistent too_easy feedback across multiple independent reviews outweighs this single positive assessment. The case requires redesign—either a narrower focus that probes less explicit aspects (e.g., inferring why the skunkworks was 'off Jobs's radar'), an expanded excerpt showing project outcomes, or selection of a different passage from the same source that demands actual inference.

```text
Jobs had resisted, thinking that BASIC was all the Apple II needed, but he told Atkinson, “Since you’re so passionate about it, I’ll give you six days to prove me wrong.”
He did, and Jobs respected him ever after.
By the fall of 1979 Apple was breeding three ponies to be potential successors to the Apple II workhorse.
There was the ill-fated Apple III.
There was the Lisa project, which was beginning to disappoint Jobs.
And somewhere off Jobs’s radar screen, at least for the moment, there was a small skunkworks project for a low-cost machine that was being developed by a colorful employee named Jef Raskin, a former professor who had taught Bill Atkinson.
Raskin’s goal was to make an inexpensive “computer for the masses” that would be like an appliance—a self-contained unit with computer, keyboard, monitor, and software all together—and have a graphical interface.
```

## 3. `steve_jobs_private_en__24__seed_1`

- benchmark_status: `needs_revision`
- review_status: `llm_reviewed`
- book: `Steve Jobs`
- author: `Walter Isaacson`
- chapter: `Chapter Fifteen: The Launch: A Dent in the Universe` (`24`)
- question_ids: ``
- phenomena: ``
- selection_reason: Illustrates Jobs' approach to marketing and product launches during the Macintosh era, including his demand for a revolutionary commercial.
- judge_focus: Identify the purpose of the '1984' commercial and Jobs' stated goals for it.
- latest_review_action: `revise`
- latest_problem_types: `ambiguous_focus|other`
- latest_revised_bucket: `business_history/innovation`
- latest_notes: This seed excerpt (status: private_library_seed_v2) contains solid biographical content about the '1984' Apple commercial, but lacks all evaluation metadata required for benchmark promotion—case_title, question_ids, phenomena, selection_reason, and judge_focus are null or empty. The excerpt is historically engaging and accurate, but cannot function as a benchmark case without explicit evaluation criteria. Primary and adversarial reviews correctly note this gap. Return to curation pipeline to add required metadata rather than dropping, as the source material has genuine potential. The suggested revised_bucket (business_history/innovation) and judge_focus provide a reasonable template for the missing metadata.

```text
A short while later Apple’s Fremont factory began to roll out boxes emblazoned with the colorful line drawings of the Macintosh.
Real artists ship, Jobs had declared, and now the Macintosh team had.
The “1984” Ad
In the spring of 1983, when Jobs had begun to plan for the Macintosh launch, he asked for a commercial that was as revolutionary and astonishing as the product they had created.
“I want something that will stop people in their tracks,” he said.
“I want a thunderclap.”
The task fell to the Chiat/Day advertising agency, which had acquired the Apple account when it bought the advertising side of Regis McKenna’s business.
```

## 4. `evicted_private_en__10__seed_1`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Evicted`
- author: `Matthew Desmond`
- chapter: `Chapter 1: The Business of Owning the City` (`10`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `wrong_bucket|weak_excerpt|ambiguous_focus`
- latest_revised_bucket: ``
- latest_notes: This case is correctly flagged for removal. The excerpt describes Sherrena and Quentin's courtship and Sherrena's teaching mannerisms, but contains zero content about eviction, housing instability, or poverty—the core phenomena the 'Evicted' source bucket addresses. It functions as literary character backstory with no evaluative tension or reading-mechanism challenge. All three prior reviews and both primary/adversarial assessments converge on drop, citing wrong bucket, weak excerpt, and missing critical metadata. No viable alternative bucket or metadata addition would salvage this passage as a benchmark case.

```text
Sherrena thought he looked like a dope dealer but gave him her real number anyway.
Quentin called Sherrena for three months before she agreed to let him take her out for ice cream.
It took him another six years to marry her.
When Quentin pulled Sherrena over, she was a fourth-grade teacher.
She talked like a teacher, calling strangers “honey” and offering motherly advice or chiding.
“You know I’m fixing to fuss at you,” she would say.
If she sensed your attention starting to drift, she would touch your elbow or thigh to pull you back in.
```

## 5. `evicted_private_en__17__seed_2`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Evicted`
- author: `Matthew Desmond`
- chapter: `Chapter 8: Christmas in Room 400` (`17`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `ambiguous_focus|weak_excerpt`
- latest_revised_bucket: ``
- latest_notes: This case has been reviewed four times across multiple rounds and consistently identified with the same core problems: ambiguous focus from concatenating two structurally unrelated passages (Rent Recovery Service's systemic debt critique + Arleen's courtroom scene) and weak excerpt cohesion. The narrative journalism excerpt lacks a coherent analytical thread and would require external interpretive work to unify. The primary review's metadata gaps (empty case_title, question_ids, phenomena, selection_reason, judge_focus) confirm the case cannot function as a valid benchmark. No evidence suggests these issues can be resolved through further revision given the source material's inherent disconnect.

```text
Like landlords docketing judgments, the company took the long view, waiting for tenants to “get back on their financial feet and begin to earn a living” before collection could begin.
Rent Recovery Service “never closed an unpaid file.”15 Some of those files contained debt amounts calculated in a reasonable and well-documented way; others contained bloated second and third causes and unreasonably high interest rates.
But since both had the court’s approval, Rent Recovery Service did not distinguish between them.
—
When her turn came, Arleen decided to sit right next to Sherrena at the commissioner’s table.
The two women looked for a moment like old friends or even sisters, with one reflecting life’s favor.
Sherrena was still stewing over being denied her $5,000 claim when the commissioner, without lifting her eyes from Arleen’s file, said, “Your landlady is seeking to evict you for unpaid rent.
```

## 6. `fooled_by_randomness_private_en__14__seed_2`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Fooled by Randomness`
- author: `Nassim Nicholas Taleb`
- chapter: `Chapter Seven` (`14`)
- question_ids: ``
- phenomena: ``
- selection_reason: Tests ability to resolve anaphoric references and understand philosophical argumentation about verification vs falsification, where 'These people' explicitly refers to logical positivists.
- judge_focus: Can the reader correctly resolve 'These people' to logical positivists/Vienna Circle and understand Popper's falsification approach as opposing verificationism?
- latest_review_action: `drop`
- latest_problem_types: `too_easy|text_noise|source_parse_problem`
- latest_revised_bucket: ``
- latest_notes: The case cannot be salvaged through relabeling. The anaphoric resolution task is trivial because 'These people' is explicitly defined in the same sentence ('These people were sometimes called the logical positivists'), leaving no ambiguity to resolve. The lookback_sentences contain unrelated text noise that contradicts the excerpt content. Additionally, the chapter_id (14) mismatches chapter_title ('Chapter Seven'), indicating unresolved source parsing issues. The philosophical content is well-presented but the excerpt fails as a reading mechanism test due to its explicit nature.

```text
Popper intellectually came to the world with the dramatic shifts in philosophy as attempts were made to shift it from the verbal and rhetorical to the scientific and rigorous, as we saw with the presentation of the Vienna Circle in Chapter 4 .
These people were sometimes called the logical positivists, after the movement called positivism pioneered in France in the nineteenth century by Auguste Comte, where positivism meant scientification of things (literally everything under the sun).
It was the equivalent of bringing the industrial revolution into the soft sciences.
Without dwelling on positivism, I have to note that Popper is the antidote to positivism.
To him, verification is not possible.
Verificationism is more dangerous than anything else.
Taken to the extreme, Popper’s ideas appear naive and primitive—but they work.
```

## 7. `poor_charlies_almanack_private_en__10__seed_2`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Poor Charlie's Almanack`
- author: `Charles T. Munger`
- chapter: `The Munger Approach to Life, Learning, and Decision Making` (`10`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `weak_excerpt|ambiguous_focus|source_parse_problem`
- latest_revised_bucket: ``
- latest_notes: This excerpt is meta-commentary criticizing academic psychology textbooks rather than an illustration of a specific dangerous idea or cognitive bias. The Samuel Johnson anecdote about 'pure ignorance' is tangential and decorative rather than central. The excerpt starts mid-sentence, contains truncated content at both boundaries, and lacks the clear evaluation criteria needed for benchmark testing. Three independent reviews have consistently recommended drop due to missing critical metadata (selection_reason, judge_focus) combined with vague philosophical content that requires outside knowledge to interpret. Not worth further curation investment.

```text
And, possibly, the cause of their
inadequacy was the one given by Samuel Johnson in response to a woman who inquired as to what accounted for his dictionary's misdefinition of the word "pastern."
"Pure ignorance," Johnson replied.
And, finally, the text writers showed little
interest in describing standard antidotes to standard
psychology-driven folly, and they thus avoided most
discussion of exactly what most interested me.
```

## 8. `steve_jobs_private_en__24__seed_2`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Steve Jobs`
- author: `Walter Isaacson`
- chapter: `Chapter Fifteen: The Launch: A Dent in the Universe` (`24`)
- question_ids: ``
- phenomena: ``
- selection_reason: 
- judge_focus: 
- latest_review_action: `drop`
- latest_problem_types: `ambiguous_focus|other`
- latest_revised_bucket: ``
- latest_notes: The excerpt content is coherent and depicts a clear example of strategic manipulation through flattery (Jobs manipulating Sculley), but critical evaluation metadata (question_ids, phenomena, selection_reason, judge_focus, case_title) remains entirely absent despite four review rounds. Without defined evaluation criteria, this case cannot serve a meaningful benchmark function regardless of excerpt quality. The case should be dropped from active benchmark consideration until proper metadata configuration is completed.

```text
Most of all, Jobs fretted about his presentation.
Sculley fancied himself a good writer, so he suggested changes in Jobs’s script.
Jobs recalled being slightly annoyed, but their relationship was still in the phase when he was lathering on flattery and stroking Sculley’s ego.
“I think of you just like Woz and Markkula,” he told Sculley.
“You’re like one of the founders of the company.
They founded the company, but you and I are founding the future.”
Sculley lapped it up.
```

## 9. `supremacy_private_en__13__seed_1`

- benchmark_status: `needs_replacement`
- review_status: `llm_reviewed`
- book: `Supremacy`
- author: `Parmy Olson`
- chapter: `Chapter 7. Playing Games` (`13`)
- question_ids: ``
- phenomena: ``
- selection_reason: Examines DeepMind's independent governance structure post-2015 spinout, focusing on ethics board composition and transparency mechanisms around high-profile director appointments (Obama, former VP, former CIA director)
- judge_focus: Evaluate the effectiveness and credibility of independent oversight structures in AI labs, particularly whether high-profile external directors provide meaningful governance or primarily serve as legitimacy proxies
- latest_review_action: `drop`
- latest_problem_types: `weak_excerpt`
- latest_revised_bucket: ``
- latest_notes: The excerpt describes governance intentions rather than outcomes—the entire passage uses future tense ('would be made,' 'would also be') with only vague confirmation that 'several agreed to take part.' The judge's focus asks to evaluate effectiveness and credibility of oversight structures, but the content offers only planning-phase intentions with no evidence of whether these directors served, made decisions, or if the structure functioned. This is fundamentally insufficient to assess whether high-profile appointments provided meaningful governance or merely served as legitimacy signaling. The excerpt presents aspirational PR messaging as potential governance evidence, which is misleading given the stated evaluation goals.

```text
Decisions would be made by majority vote.
Crucially, there would also be a fully independent board of trustees made up of six directors who would oversee DeepMind’s compliance with its social and ethical mission.
The names of those directors, as well as their decisions, would be made transparent to the public.
Since those six directors would be steering some of the most powerful and potentially dangerous technology in the world, they needed to be high-caliber, trustworthy people.
So DeepMind reached for the stratosphere, asking former president Barack Obama to become one of those directors, along with a former US vice president and a former CIA director.
Several of these people agreed to take part, according to someone who was close to that work.
After consulting with legal experts, DeepMind decided it would not go down the same route that Sam Altman initially had by becoming a nonprofit organization.
```
