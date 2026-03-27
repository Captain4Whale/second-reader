# Mechanism Pattern Ledger

Purpose: preserve portable strengths, adoption candidates, failure modes, and anti-patterns discovered during evaluation and repair work.
Use when: interpreting evaluation runs, planning mechanism repairs, deciding what to carry forward from competing mechanisms, or avoiding repeated mistakes.
Not for: stable methodology authority, public API decisions, or one-off benchmark scores without interpretation.
Update when: a meaningful evaluation pass, repair pass, or cross-mechanism comparison reveals a reusable strength or a repeatable failure pattern.

This file is a living working ledger. Stable rules still belong in `docs/backend-reader-evaluation.md`. Decision-bearing adoptions or rejections should later be promoted into stable mechanism docs or `docs/history/decision-log.md`.

## Entry Format
- `Pattern kind`
  - `strength`
  - `adoption_candidate`
  - `failure_mode`
  - `anti_pattern`
- `Source mechanism`
  - where the behavior was observed first
- `Potential destination`
  - where we may adopt it, if anywhere
- `Why it matters`
  - what reader-quality dimension it improves or harms
- `Evidence`
  - reports, bundles, excerpts, or code links
- `Status`
  - `observed`
  - `candidate_for_adoption`
  - `partially_adopted`
  - `adopted`
  - `avoid`

## Current High-Value Patterns

### 1. Iterator V1 local micro-selectivity
- Pattern kind: `adoption_candidate`
- Source mechanism: `iterator_v1`
- Potential destination: `attentional_v2` local-reading loop and future merged mechanism
- Why it matters:
  - It notices and reacts to small but decisive local expressions instead of jumping too quickly to chapter-level summary.
  - This improves `local_impact`, especially on close-reading passages with compact but meaningful wording.
- Contributing causes:
  - the express prompt explicitly permits a free list of repeated local reactions instead of one compressed meaning-unit reaction
  - the runtime can keep multiple `highlight` / `curious` / `discern` reactions from one segment rather than forcing one surfaced output
  - curiosity/search is allowed to extend local investigation when a phrase genuinely opens a line of inquiry
- Evidence:
  - `attentional_v2_vs_iterator_v1_chapter_core_zh_round1_20260326`
  - `ouyou_zaji_public_zh__4`
  - Example local expressions and reactions:
    - original excerpt:
      - `大運河穿過威尼斯像反寫的S；這就是大街。`
      - `好像我們戲裡大將出場，後面一杆旗子總是偏著取勢；這方場中的建築，節奏其實是和諧不過的。`
    - iterator-style reactions:
      - `「反写的S」这个比喻是否当时旅欧文学中的常见套语？还是作者的原创观察？`
      - `作者用中国传统看戏经验来理解威尼斯建筑布局的视角——不对称本身就可以是美。`
- Status: `candidate_for_adoption`

### 2. Attentional V2 chapter-scale thematic threading
- Pattern kind: `strength`
- Source mechanism: `attentional_v2`
- Potential destination: preserve and deepen in future merged mechanism
- Why it matters:
  - It can turn repeated local signals into a chapter-level thematic thread instead of leaving them as isolated reactions.
  - This improves `system_regression`, especially `coherent_accumulation` and `chapter_arc_clarity`.
- Contributing causes:
  - the loop is organized around meaning-unit closure and then chapter-level accumulation rather than around a flat list of local reactions
  - callback / distinction / durable-pattern cues are explicitly surfaced to the local cycle
  - retrospect reactions can compress repeated local signals into one chapter-level theme instead of keeping them episodic
- Evidence:
  - `attentional_v2_vs_iterator_v1_chapter_core_zh_round1_20260326`
  - `jinghua_yuan_25377_zh__34`
  - Example original signals:
    - `屢次要尋自盡，無奈眾人日夜提防，真是求生不能，求死不得。`
  - Attentional V2 repeatedly lifted the same phrase across multiple chapter moments and then closed with:
    - `此八字在本章四度標記極端困境……形成情感共振，凝結為本章最核心的主題訊號。`
- Status: `observed`

### 3. Attentional V2 callback-cue and durable-pattern repair
- Pattern kind: `partially_adopted`
- Source mechanism: `attentional_v2`
- Potential destination: retain as baseline in future merged mechanism
- Why it matters:
  - The second repair pass showed that explicit cue packets can materially improve weak local cases instead of only changing wording.
  - This is one of the strongest examples of a repair changing benchmark outcomes in a trustworthy way.
- Contributing causes:
  - deterministic local cue packets keep the model centered on the exact textual pressure
  - merged bridge candidates now reach controller choice instead of being dropped before decision time
  - the repaired prompts now ask for exact callback / distinction / pattern naming instead of generic scene paraphrase
- Evidence:
  - targeted repair reports:
    - `attentional_v2_integrity_repair_pass1_targeted_20260326`
    - `attentional_v2_integrity_repair_pass2_targeted_20260326`
  - code:
    - `reading-companion-backend/src/attentional_v2/nodes.py`
    - `reading-companion-backend/src/attentional_v2/prompts.py`
    - `reading-companion-backend/src/attentional_v2/runner.py`
  - observed repair targets:
    - `callback_cue`
    - `distinction_cue`
    - `recognition_gap`
    - `durable_pattern`
- Status: `partially_adopted`

## Current High-Value Failure Memory

### 4. Sparse but globally correct reading is not enough for strong `local_impact`
- Pattern kind: `anti_pattern`
- Source mechanism: `attentional_v2`
- Potential destination: avoid in future merged mechanism
- Why it matters:
  - A mechanism can be globally coherent yet still lose passage-level comparison if it reacts too sparsely and skips the tiny local expressions that make the reading feel earned.
- Contributing causes:
  - `reaction_emission` is intentionally gated and often withholds visible output
  - closure pressure encourages one distilled meaning-unit reading rather than multiple local observations
  - this can produce correct chapter sense while still missing the small local expression that the judge rewards in `local_impact`
- Evidence:
  - `attentional_v2_vs_iterator_v1_chapter_core_en_round1_20260326`
  - `women_and_economics_public_en__9`
  - `on_liberty_public_en__10`
  - pattern seen in judge reasons:
    - V2 often read correctly but felt like retrospective summary rather than live local investigation.
- Status: `avoid`

### 5. Wrong-chapter or wrong-target traversal corrupts chapter-scale evaluation even if local reactions look rich
- Pattern kind: `anti_pattern`
- Source mechanism: `iterator_v1`
- Potential destination: avoid in future merged mechanism
- Why it matters:
  - Rich local reactions are not a product win if they happen on the wrong chapter or never accumulate on the assigned target text.
- Contributing causes:
  - section-first traversal can still fail catastrophically at chapter targeting
  - once the mechanism is misaligned with the target chapter, local reaction richness becomes misleading rather than helpful
- Evidence:
  - `attentional_v2_vs_iterator_v1_chapter_core_en_round1_20260326`
  - `women_and_economics_public_en__9`
  - `ouyou_zaji_public_zh__4`
  - judge reason examples:
    - `Iterator V1 ... never accesses Chapter IV at all`
    - `Iterator V1 ... only processed Chapter 1 (封面), completely missing the target chapter`
- Status: `avoid`

### 6. Callback cue without honest anchor resolution still causes false confidence
- Pattern kind: `failure_mode`
- Source mechanism: `attentional_v2`
- Potential destination: future bridge-resolution refinement
- Why it matters:
  - The mechanism may notice an explicit callback cue but still bridge to the wrong earlier material instead of saying the anchor is not honestly available.
  - This creates misleading fluency in bridge cases.
- Contributing causes:
  - cue detection can succeed before source-anchor resolution is actually honest
  - the current bridge path is better than before, but still sometimes prefers a weak earlier echo over an explicit "anchor not available" outcome
- Evidence:
  - repaired reviewed-slice work on:
    - `jinghua_yuan_25377_zh__15__callback_bridge__v2`
    - `nahan_27166_zh__2__callback_bridge__v2`
  - post-repair interpretation in:
    - `attentional_v2_integrity_repair_pass2_targeted_20260326`
    - `attentional_v2_integrity_reviewed_slice_round3_repair_pass2_20260326`
- Status: `observed`

### 7. Benchmark winner/loser language alone is insufficient memory
- Pattern kind: `anti_pattern`
- Source mechanism: evaluation process itself
- Potential destination: all future comparison passes
- Why it matters:
  - If we preserve only who won, we lose the transferable strengths and the repeated mistakes that should shape the next mechanism.
  - This was the direct motivation for this ledger.
- Evidence:
  - first broader chapter-core comparison:
    - `attentional_v2_vs_iterator_v1_chapter_core_en_round1_20260326`
    - `attentional_v2_vs_iterator_v1_chapter_core_zh_round1_20260326`
- Status: `avoid`
