# Source Normalization Design

Purpose: define the import-time source-normalization direction for separating
mainline reading text from auxiliary/support/noise text before reader mechanisms
run.
Use when: designing or implementing parser/source-substrate cleanup that affects
which original book blocks reach `Ingest` / `Digest`.
Not for: live Ingest prompt wording, Digest output schema, Unit Memory retrieval
policy, or frontend highlight rendering details.
Update when: source-normalization roles, confidence policy, metadata shape, or
mainline/auxiliary routing changes.

Status: implemented-live v1.2 for newly created parsed-book documents.
Current live behavior classifies new canonical paragraph records with
Source Normalization before `Ingest` / `Digest` run, then keeps the existing
runtime gate: paragraphs whose `text_role` is `auxiliary` are excluded from the
mainline reader stream. The live default is deterministic-only: it does not call
a whole-book LLM classifier during product parse.

## Problem

The live Ingest selector behaved correctly given the source stream it received,
but the stream sometimes contains text that is not part of the book's mainline
reading flow.

Concrete evidence:

- The Siddhartha window-partition report showed Units 014-21 selecting one
  translator/endnote item at a time, such as `[1]Brahmanen...`, `[2]Om...`,
  `[3]Atman...`. Those blocks were parsed as `body`, so Ingest treated each
  note as a complete next semantic unit.
- The same source region also showed repeated heading-like fragments such as
  `沙门`, where source layout noise or duplicate titles can appear between
  notes and resumed body text.
- Earlier review of Naval-style source artifacts exposed isolated layout
  symbols / special characters that can enter the reading stream even though
  they are not meaningful body text.
- Unit Memory retrieval reviews found that auxiliary surfaces can pull broad
  terminology / note-cluster units into later memory selection unless the main
  source stream and retrieval surfaces are kept clean.

This is not primarily an Ingest prompt problem. Ingest should not be asked to
decide whether to skip arbitrary source spans. It should choose the next unit
inside a source stream that has already been normalized for reading.

## Principle

Raw source remains canonical.

Source normalization should classify original book paragraph/block records into
reading-flow roles while preserving their original coordinates:

- chapter id / chapter reference
- original `paragraph_index`
- paragraph-local `char_offset`
- EPUB locators such as `href`, `start_cfi`, and `end_cfi` when available

The first implementation should not introduce a persistent `reading_blocks[]`
model. It should attach richer normalization metadata to existing paragraph
records. The current mainline reading stream is the ordered subset of original
paragraphs that remain visible to reader mechanisms after normalization.

Highlights and notes produced by the agent still map back through the original
paragraph coordinates. Auxiliary material is not deleted; it is excluded from
mainline Ingest visibility and retained for support/audit uses.

## Role Taxonomy

`mainline_body`
: Narrative, dialogue, argument, poem text, letter text, or any other content a
reader should encounter in order as part of the book.

`heading`
: Chapter or section title text that should remain visible as structure context.
Headings are weak cues, not automatic standalone reading units.

`auxiliary_note`
: Footnotes, endnotes, translator notes, terminology definitions, source
explanations, and note clusters. These should not become Ingest/Digest units but
may be supplied later as support context when the mainline text refers to them.

`reference_like`
: Bibliography, citation lists, indexes, source-attribution lists, and formal
references. These are usually outside the mainline flow.

`front_back_matter`
: Copyright, contents, publication metadata, index, acknowledgments, and similar
apparatus. Some front/back matter can be product-useful, but it should not enter
the default mainline fiction/nonfiction reading stream by accident.

`layout_noise`
: Page numbers, repeated running headers, duplicated book/chapter titles,
isolated OCR leftovers, stray symbols, and formatting artifacts such as a lone
`v` or repeated ornamental residue.

`caption_or_table_support`
: Captions, table labels, image credits, and table/figure support text. For
nonfiction this may sometimes be mainline-relevant; the first design should
classify it explicitly rather than flattening it into body text.

`uncertain_keep_mainline`
: Any ambiguous block that might be author-intended content. This is the default
safe class for low-confidence cases.

## Metadata Contract

Existing `text_role` remains the coarse runtime gate:

- `body`, `chapter_heading`, and `section_heading` remain eligible for mainline
  reading unless a later implementation adds finer handling.
- `auxiliary` is excluded by current `attentional_v2` preview construction and
  sentence derivation.

Richer source-normalization detail should live under a nested field, for
example:

```json
{
  "paragraph_index": 58,
  "text": "[1]Brahmanen, ...",
  "text_role": "auxiliary",
  "source_normalization": {
    "normalized_role": "auxiliary_note",
    "kind": "translator_note",
    "confidence": 0.96,
    "method": "deterministic_markup",
    "reason_code": "html_auxiliary_marker",
    "linked_markers": ["[1]"],
    "evidence": {
      "cluster_start_paragraph_index": 58,
      "cluster_end_paragraph_index": 68,
      "position": "chapter_tail_before_next_section"
    }
  }
}
```

For v1, source normalization should not rewrite paragraph text. If future source
artifacts require paragraph-internal splitting, represent that as a later
`source_normalization.spans[]` extension with original char offsets. Do not add
that complexity until real examples require it.

## Pipeline

1. Parse original EPUB / HTML blocks as today.
2. Preserve block metadata that can help classification:
   - tag name
   - class/id attributes
   - `epub:type`, `role`, `aria-*` attributes when available
   - ancestor tags/classes/ids/roles/types for source containers such as
     footnote wrappers or blockquotes
   - bounded inline anchor ids/hrefs/texts for note-definition links
   - `href` / CFI locator data
   - chapter title and chapter position
   - pure parent containers with textual child blocks should not also become
     paragraph records; for example `blockquote > p` keeps the child paragraph
     records and avoids a duplicated parent aggregate
3. Run deterministic evidence collection:
   - explicit footnote/endnote/reference HTML markers
   - inline note-definition anchors and body-marker links
   - chapter titles such as `Notes`, `Footnotes`, `Endnotes`, `注释`, `译注`
   - consecutive note-definition patterns like `[1]`, `[2]`, `[3]`
   - local clusters of short definition/citation blocks
   - repeated running headers or duplicate headings
   - URL / publication / bibliography patterns
   - literary containers such as `blockquote`, poem, verse, stanza, or letter
     wrappers that protect unusual mainline forms from false exclusion
   - mainline markers that link body text to later notes
4. Apply deterministic exclusion only when the original source structure proves
   the block is apparatus:
   - explicit footnote/endnote/translator-note containers
   - note-definition anchors such as `f1 -> #s1` with leading `[1]`
   - explicit reference/bibliography containers
   - baseline parser `text_role == "auxiliary"` records
5. Validate conservatively:
   - inline note references such as `s1 -> #f1` or `noteref-1 -> #note-1`
     remain mainline body text
   - malformed orphan note-like text without structural proof is audit-only
   - ambiguous blocks remain mainline
   - every exclusion records a method, confidence, and reason code
6. Materialize normalized paragraph records while preserving raw coordinates.
7. Let Ingest read only the normalized mainline stream. Let Digest retrieve
   auxiliary notes only when mainline source markers or runtime policy asks for
   them.
8. Optional offline classifier hooks may be used in tests or audit tools, but
   they are not the live default parse gate.

## Optional Offline Classifier Prompt Sketch

This prompt is retained as an offline/audit sketch only. It is not the live
default Source Normalization path. If reused later, classifier output must not
hide正文 without independent deterministic structure evidence.

```text
You are classifying original book blocks before reading begins.

Your task is not to judge importance, summarize content, or rewrite the book.
Your task is to classify each original paragraph/block by its role in the
book's source flow.

Mainline text is what a reader should encounter in order while reading the book.
Auxiliary text explains, cites, indexes, attributes, or repairs the source, but
is not itself the next narrative/argument unit.

Be conservative:
- If unsure, choose uncertain_keep_mainline.
- Do not mark unusual literary form as auxiliary merely because it is short,
  numbered, poetic, quoted, foreign-language, or formatted oddly.
- Do not mark letters, poems, dialogue, fictional documents, or author-intended
  note-like prose as auxiliary unless source-flow evidence clearly supports it.
- Treat source markup as evidence: footnote/endnote/reference containers are
  exclusion evidence, while blockquote/poem/verse containers usually protect
  mainline literary text.
- Never mark blockquote, poem, verse, letter, dialogue, or fictional-document
  text as layout_noise merely because it is line-broken, repeated nearby, or
  stylistically unusual.
- Footnote/endnote/translator-note clusters may be auxiliary even if each note
  is meaningful.
- Layout artifacts and repeated running headers should not enter mainline
  reading.
```

Input should include block ids and evidence, not only raw text:

```json
{
  "book_type_hint": "novel",
  "chapter_title": "婆罗门之子",
  "blocks": [
    {
      "paragraph_index": 58,
      "text": "[1]Brahmanen，婆罗门...",
      "current_text_role": "body",
      "block_tag": "p",
      "ancestor_html_classes": ["fnote"],
      "inline_anchor_ids": ["f1"],
      "inline_anchor_hrefs": ["part0005.xhtml#s1"],
      "inline_anchor_texts": ["[1]"],
      "position_hint": "after_main_scene_before_next_section",
      "nearby_markers_seen_in_body": ["[1]"]
    }
  ]
}
```

Output should be structured labels:

```json
{
  "classifications": [
    {
      "paragraph_index": 58,
      "normalized_role": "auxiliary_note",
      "text_role": "auxiliary",
      "kind": "translator_note",
      "confidence": 0.96,
      "reason_code": "numbered_endnote_cluster",
      "linked_markers": ["[1]"]
    }
  ]
}
```

## Example: Siddhartha Note Cluster

The desired normalization for the reviewed Siddhartha region is:

- P55-P57: `mainline_body`
- P58-P68: `auxiliary_note`, likely `translator_note` / `endnote`, because the
  raw XHTML places them under `div.fnote` and each note definition uses an
  anchor such as `f1 -> #s1`
- any duplicate or heading-like fragments without strong structure evidence:
  preserve mainline or heading visibility rather than guessing
- P71 onward: `mainline_body`

After normalization, Ingest should move from the P55-P57 departure unit to the
next mainline body region. It should not read P58-P68 as separate units. Those
notes remain available as support context for Digest when matching body markers
such as `[1]` or terms such as `Brahmanen`.

The v1.1/v1.2 repair adds concrete guardrails from the real Siddhartha parse:

- `div.fnote > p > a` note definitions preserve their ancestor class/type/role
  and inline anchor metadata, so single notes such as `[1]Magadha...` can be
  excluded as `auxiliary_note` without a classifier.
- body note references such as `sup > a id="s1" href="#f1"` are evidence of a
  mainline reference, not evidence that the body paragraph is auxiliary.
- `blockquote > p` literary lines keep only the child paragraph records and
  carry `ancestor_tags=["blockquote"]`; the parent aggregate is not emitted.
- malformed orphan-note candidates such as `1《爱经》...` are retained as body
  unless a later, narrower rule gains enough structure evidence to exclude them.

## False-Positive Guardrails

The normalizer must avoid removing author-intended content. Keep mainline when:

- the block is a poem, letter, diary entry, fictional document, or numbered
  aphorism that participates in the work
- the block is a chapter heading or title card that cues the next body section
- a single numbered block has no nearby note cluster or structural evidence
- a short or foreign-language block appears in dialogue, poetry, or stylized
  fiction
- confidence is low or evidence conflicts

The safe default is `uncertain_keep_mainline`.

## Implemented Live V1.2

The implementation is live for newly parsed books:

- `reading-companion-backend/src/reading_runtime/source_normalization.py`
  contains deterministic evidence collection, metadata merge, sentence-layer
  rebuild, and diagnostics writer. Product parse defaults to
  `method=deterministic_only` and does not call the LLM classifier.
- `reading-companion-backend/src/iterator_reader/parse.py` invokes Source
  Normalization only when creating a new `public/book_document.json`.
- Existing parsed books are not migrated or rewashed automatically; they retain
  their stored paragraph roles except for the existing sentence-layer backfill.
- EPUB/HTML extraction retains lightweight evidence fields such as `html_id`,
  `html_class`, `epub_type`, and `role` on paragraph records.
- v1.1 also retains compact source-structure context on paragraph records:
  `ancestor_tags`, `ancestor_html_ids`, `ancestor_html_classes`,
  `ancestor_epub_types`, `ancestor_roles`, `inline_anchor_ids`,
  `inline_anchor_hrefs`, and `inline_anchor_texts`.
- v1.1 skips pure parent containers that only aggregate textual child blocks,
  avoiding duplicated blockquote/poem正文 while preserving child paragraph
  coordinates.
- v1.2 separates inline note references from note definitions: `noteref` and
  `sN -> fN` stay mainline, while `fN -> sN` plus leading marker and/or explicit
  note containers can become auxiliary.
- v1.2 excludes explicit footnote/endnote/translator-note/reference containers
  but treats note-like damaged text without structure as audit metadata only.
- v1.2 preserves literary containers such as blockquote/poem/verse/letter unless
  explicit auxiliary/reference structure is also present.
- Runtime `Ingest` and `Digest` remain unchanged. They still rely on the
  shared paragraph stream and the coarse `text_role == "auxiliary"` gate.
- Parse diagnostics write Source Normalization status/counts under
  `_mechanisms/iterator_v1/internal/diagnostics/parse.json`.

## Non-Goals For V1

- Do not introduce persistent `reading_blocks[]`.
- Do not rewrite or summarize source text.
- Do not let Ingest emit skip operations.
- Do not change frontend highlight coordinates.
- Do not require a formal A/B rerun before documenting this design.
- Do not use a live whole-book LLM classifier as the default parse gate.
- Do not implement paragraph-internal splitting until real mixed-block examples
  require it.

## Follow-Ups

- Add richer audit reports that show removed mainline blocks and their original
  coordinates in a reviewer-friendly table.
- Add paragraph-internal `source_normalization.spans[]` only if real mixed
  body/auxiliary paragraphs require it.
- Decide later whether auxiliary notes should become explicit support-context
  retrieval material for Digest when mainline markers refer to them.
- Design a review-only report for orphan-note candidates and other suspicious
  blocks that deterministic-only v1.2 deliberately keeps in mainline.
