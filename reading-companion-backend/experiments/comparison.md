# Q1 mixed comparison and Digest output contract

Authority for the offline comparison importer, blind projection and mixed statistics.
This task implements data preparation, mixed annotation and statistics only. Side-by-side
columns, preference records, per-window group aliases and reveal operations are deferred
until the A/B diagnostic has been annotated. No model, prompt or mechanism changes.

## Fixed-history Digest rerun output contract (v1)

The separate rerun task MUST emit `q1-digest-comparison-output/1` JSON. One file is one
group/run. The comparison task consumes this file; it does not reconstruct inputs or run
Digest. Put the file and its source documents in ignored backend `state/` directories.

```json
{
  "schema": "q1-digest-comparison-output/1",
  "experiment_id": "REGISTERED-EXPERIMENT-ID",
  "run_id": "REGISTERED-RUN-ID",
  "model": "ACTUAL-MODEL",
  "prompt": {"version": "attentional_v2.digest.v24", "release_sha256": "64-lowercase-hex"},
  "reconstructed": true,
  "synthetic": false,
  "sources": [{
    "source_id": "local-source-identity",
    "epub_sha256": "64-lowercase-hex",
    "substrate_sha256": "64-lowercase-hex",
    "book_document_path": "relative/path/to/book_document.json"
  }],
  "coverage": [{
    "source_id": "local-source-identity",
    "original_source_range": {
      "start": {"chapter_id": 1, "paragraph_index": 1, "char_offset": 0},
      "end": {"chapter_id": 1, "paragraph_index": 2, "char_offset": 20}
    },
    "status": "complete"
  }],
  "marginalia": [{
    "source_id": "local-source-identity",
    "marginalia_id": "original-output-id",
    "unit_id": "optional-provenance-only",
    "type": "N",
    "body_text": "Note body; empty string for H",
    "source_quote": "Exact canonical quote",
    "original_source_range": {
      "start": {"chapter_id": 1, "paragraph_index": 1, "char_offset": 0},
      "end": {"chapter_id": 1, "paragraph_index": 1, "char_offset": 10}
    },
    "request_sha256": null
  }]
}
```

Rules:

- Production `experiment_id`, `run_id`, prompt version/release hash must match
  `experiments/log.jsonl`. Register the trial in the separate generation task. No new
  experiment is invented merely to package comparisons.
- `reconstructed` describes historical input reconstruction, not whether output
  coordinates were reconstructed. `release_sha256` identifies fixed prompt content;
  `request_sha256` identifies the actual complete request producing this mark. A missing
  historical request hash is null, never replaced with a release hash. Future reruns
  should supply the observed request hash and may add call/attempt metadata.
- Source identity is the pair of original EPUB SHA-256 and canonical BookDocument
  substrate digest (`book_document_substrate_digest`), not title, unit ID or file name.
  The importer validates the referenced document's substrate and each exact quote/range.
  The EPUB identity must match the frozen dev manifest; no EPUB parsing or model call occurs.
- Coordinates are one-based chapter/paragraph IDs and zero-based Unicode code-point
  offsets into **original** BookDocument paragraphs, half-open `[start,end)`. Each range
  is nonempty and in one chapter. Adjacent ranges touching at an endpoint do not overlap.
  Quotes join readable paragraph slices with `\n\n`, following existing source-range rules.
- IDs must be unique within `(source_id, marginalia_id)` per group. Cross-group and
  cross-book duplicate IDs are expected and remapped privately.
- `coverage` must explicitly certify complete generation over every comparison window.
  In v1 each window must be contained in one complete coverage range. This distinguishes
  zero generated marks from a missing/failed attempt. Partial or failed generation is
  not accepted as an empty group. Preserve its diagnostic artifacts separately.
- H means Highlight and requires empty `body_text`; N means Note and requires a body.
  No matching by `unit_id`. No fuzzy quote search or guessed coordinates. Malformed,
  unlocated or ambiguous anchors reject the import with an error; fix their provenance
  in the producer, without silently removing marks.
- Synthetic fixtures use `synthetic: true`, `SYNTHETIC-...` experiment IDs and may have
  null release hashes. They are labelled in the UI and statistics and never registered
  as actual experiments. All production comparisons must have `synthetic: false`.

## Windows, membership and blind files

`dev-v1` fixes boundaries; source text/context comes from the hash-verified original
`q1-batch/1` files. The frozen manifest and historical journals are never rewritten.
Overlapping fixed windows are rejected because they would have ambiguous start owners.
Multiple books are supported; coordinate comparisons always include source identity.

For each mark, preserve all intersecting windows for the future side-by-side view.
For **mixed**, assign it only to the window containing the anchor start. Set
`crosses_boundary` when its full anchor extends outside that window. Retain the full
quote; clip highlighting to the visible window. A mark whose start is outside every
window is never silently reassigned: record `anchor_start_outside_windows` (if it
intersects a window) or `no_window_overlap` in `unassigned_items`. These counts must be
reported beside statistics. No ID deduplication of repeated judgments across windows
is needed: the projection contains each eligible mark exactly once.

The immutable bundle under `state/q1_comparison/<batch-id>/` contains:

- `batch.json`: `q1-comparison-batch/1`, original sources, window text/ranges, N group
  metadata, experiment IDs, manifest hash, full anchors, all overlaps and unassigned report.
- `mixed.json`: `q1-mixed/1`, content-addressed `batch_id`, synthetic flag and `windows`.
  Windows expose only random window IDs, source text/context, book/author/chapter and
  randomly shuffled anonymous marks. Each mark exposes random `marginalia_id`, H/N,
  quote/body, original range and crossing flag. No group, model, run, version, original
  IDs, input paths, seed, membership lists or per-group counts enter this file.
- `blind-key.json`: `q1-blind-key/1`, batch binding and anonymous mark -> private group,
  original source/mark/unit/run/request identity. Used by the offline statistics only.
- `judgments.jsonl`: appended by the annotator; new comparisons start empty. Optional
  `annotation-context.json` uses the existing published-rubric context contract.

Random UUIDs and a system-random within-window shuffle are persisted in the immutable
projection; reopening never reshuffles. Rebuilding creates a different batch, so retain
the original files. IDs are not shown to annotators. The UI reads **only mixed.json**
for comparisons, never the canonical batch or key. Do not expose metadata through tooltips,
DOM datasets, error messages or export fields. Original author text remains unchanged;
blindness removes interface/provenance clues, not stylistic differences in the output.

## Preparation

Run from the backend (all commands offline):

```sh
.venv/bin/python scripts/build_q1_comparison.py --synthetic
.venv/bin/python scripts/build_q1_comparison.py \
  --batch-root /private/path/to/state/q1_annotation --legacy-baseline
.venv/bin/python scripts/build_q1_comparison.py \
  --batch-root /private/path/to/state/q1_annotation \
  --group /private/path/to/group-a.json --group /private/path/to/group-b.json
```

`--legacy-baseline` makes one group across the two dev books, linked to Q1-BASELINE-001.
It copies outputs only, not old judgments. The legacy loader remains available for
reading and appending to original single-group journals; those labels are historical,
not retroactively treated as mixed blind judgments. Holdout is not an iteration input.
The baseline is original historical output (`reconstructed: false`), not a replay of
reconstructed inputs. Its prompt `hash_evidence: reconstructed_after_run` separately
records that the release hash was reconstructed later; request hashes remain null.

Output paths are restricted to backend `state/`, already ignored by Git. Back up full
batch, mixed projection, key, input outputs and journals privately. The mapping is not
encryption; an operator who reads private files can reveal sources outside the tool.
There is no reveal UI or preference support in this delivery.

## Annotator 2.2

Mixed navigation retains the visible mark types (`1 · 高亮`, `2 · 旁注`). H/N is
annotation content, not group provenance; hiding it is not part of blinding. Version
2.1 restores these labels without changing the persisted order, IDs, batches or old
judgments. Both annotator and statistics accept 2.0, 2.1 and 2.2 records.

Version 2.2 reserves a stable area for save feedback and updates navigation only when
its displayed state changes, preventing toolbar flicker while typing. Browser/file
receipts, composition handling and append-only autosave semantics remain unchanged.

Open `tools/q1-annotator.html`, then the comparison folder. The tool prefers `mixed.json`;
only when that file is absent does it try legacy `batch.json`. A malformed mixed file
does not fall back to canonical data. Single-file import accepts `mixed.json` or a legacy
batch, never a full comparison manifest. JSON import saves to the browser until a journal
is connected. Folder import connects the same folder's `judgments.jsonl`.

Existing P/F, reason, star, verification, remarks, arrows, window navigation, source
selection and append-only autosave remain. Mixed shows only the current mark's anchor,
with the full quote in the judgment panel; cross-window marks have an explicit notice.
Density and its shortcuts are disabled, and completion counts judged marks only (empty
windows therefore need no mark judgments). Completion is not proof of exhaustive omission
review. Mixed omissions are window-owned, can be edited/removed by appending revisions,
and do not inherit the old two-omission cap. Legacy mode retains its original behavior.

New mixed rows use `schema: q1-mixed-judgment/1`, `annotator_version: q1-annotator/2.2`,
`batch_id` and `comparison_batch_id` bound to the mixed fingerprint, `window_id`,
`view: mixed`, human/rubric identity, monotonic `revision` and UTC `timestamp`.
`record_type` is `marginalia`, `omission` or the compatible name `unit_note` for a window
note. Marginalia rows use the anonymous ID as both `record_id` and `marginalia_id`; no
group/run/model/original ID enters the journal. Other records have null mark judgment
fields. Omission rows carry `action: save/remove`, exact source quote/range and reason.
The parser rejects unexpected fields, wrong ownership, changed anchors and conflicting
journal prefixes. Existing 1.0–1.9 rows are still readable in legacy mode and remain
byte-identical. Default attribution is `weijiang / open_coding`; published rubric
selection still uses `annotation-context.json`.

## Independent statistics and snapshots

```sh
.venv/bin/python scripts/q1_comparison_stats.py state/q1_comparison/BATCH_ID \
  --annotator weijiang --rubric open_coding \
  --output state/q1_comparison/report.json
# Optional historical journal prefix, ending at an exact revision:
.venv/bin/python scripts/q1_comparison_stats.py state/q1_comparison/BATCH_ID --revision 25
```

The script never loads the annotator. It verifies manifest/projection/key fingerprints,
single ownership, append order, mark identities, exact anchors and published rubric
identity. Missing journals, partial lines, unknown records, mismatched mappings and
reveal/preference rows fail explicitly. `--journal` can select an exported JSONL. A report
file is created exclusively under ignored backend state and is never overwritten.

It reads one byte snapshot, then optionally selects a prefix. The report records prefix
SHA-256 and revision, whole-file SHA-256 and row count, manifest/projection/key hashes,
unit-set hash, synthetic status and experiment IDs. Keep the bundle and exact journal
prefix alongside the report. A later append does not invalidate the earlier snapshot.

Latest revisions are resolved independently within `(annotator_id, rubric_version,
rubric_sha256)` scopes. Defaults select `weijiang`; omitting `--rubric` reports separate
rubric scopes. Earlier rubric judgments are retained in their own scope, not silently
replaced by judgments made under another rubric. Empty snapshots have null rates.

For each group, report separate Note/Highlight totals, pass/fail/judged/unjudged counts,
`pass_rate = passed / (passed + failed)`, stars and needs-verification counts. Flag counts
include flagged items that have not yet received pass/fail judgments. Only marks assigned
to mixed windows enter this denominator; excluded/unassigned counts and reasons are
reported explicitly. No extra deduplication is applied beyond resolving append revisions.

For each active (latest `save`) omission in that scope, check each group's **full** anchors
against its source identity and range, even if a crossing mark is judged in another window
or has its start outside the selected windows. Count one hit per omission/group. Report
`hit_count / active_omission_count`, or null when no active omissions exist. Removed
omissions are excluded. This is anchor-overlap coverage, not a semantic recall estimate.
Preference wins/ties/losses and post-reveal reporting will be implemented with the deferred
views; this version rejects those records instead of producing misleading zero counts.

Validation commands (no model):

```sh
.venv/bin/python -m pytest -q tests/test_q1_comparison.py tests/test_q1_comparison_stats.py
node --test tools/q1-annotator-storage.test.cjs
```
