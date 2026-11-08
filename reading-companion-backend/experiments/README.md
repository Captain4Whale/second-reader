# Q1 iteration provenance

For comparison batches, mixed blind annotation and the fixed-history Digest rerun
output contract, see [comparison.md](comparison.md). Side-by-side and reveal are deferred.

## Published prompts

Runtime prompt text is loaded from `src/attentional_v2/prompts/versions/<family>/<version>.md`.
The exact text is between `<!-- prompt:key -->` and `<!-- /prompt -->`; the surrounding
newline is a delimiter, not prompt content. Python retains rendering logic, not a second
copy of these texts. Shared reader role and language rules are versioned dependencies.
`versions/published.json` binds each release to its dependency files and resolved text.
Never edit a published file or its lock entry. Copy to a new version and add a release.
When checking a branch, pass the trusted pre-change base commit to the checker so a
simultaneous edit to an old file and its lock cannot masquerade as a new release.

```sh
cd reading-companion-backend
.venv/bin/python scripts/check_prompt_releases.py --base-ref HEAD
.venv/bin/python -m pytest -q tests/test_prompt_releases.py
```

The migration fixture contains only nine complete prompt-pair SHA-256 values captured
before extraction. Acceptance compared the complete system/user strings byte for byte
across chapter classification, Digest languages/source shapes, and Ingest source shapes;
no model was called. Existing prompt/call contract tests remain applicable.

### Private few-shot assets

The original Digest examples (including quoted book passages) live only in ignored
`state/prompt_assets/<sha256>.txt`. Version files contain their SHA-256 references.
Restore exact assets from the operator's private copy/backup of that directory. No
external download or public distribution is configured. For this initial release only,
an existing local historical Git object also permits explicit offline recovery:

```sh
.venv/bin/python scripts/restore_private_prompt_assets.py --legacy-ref d414030c149bc56590bed890421eb59aad22aa05
.venv/bin/python scripts/check_prompt_releases.py
```

The recovery command verifies the expected content address before writing. It requires
that object to exist locally; a shallow clone without it needs the private backup.
It never fetches anything. Missing or mismatched assets raise a clear error while loading
the prompt module; a fresh checkout must provision these files before starting the API
or importing the reader in tests. There is no silent removal of examples or substitute
prompt. Existing Git history is retained; this task does not rewrite it. The original
few-shot file must be backed up privately alongside runtime artifacts.

Raw migration captures are ignored under `state/prompt_migration/`; tracked fixtures and
release records contain hashes only. Never commit rendered prompts or example bodies.

## Runtime receipts and dirty workspaces

Each parse/read invocation (including resumes) keeps an immutable directory at
`<output>/_runtime/provenance/<invocation_id>/`. It contains `invocation.json`, an
append-only `requests.jsonl` and the first complete logical request for each node.
Full messages, fixed examples, template values, tool schemas/choice, tool history and
repair instructions enter `request_sha256` before the provider call; this identifies
the provider-neutral input, not provider-specific HTTP encoding. Generation settings
remain in the existing allowlisted model/sampling receipt. No provider configuration,
headers, API keys or environment variables are included in the sample.

Standard success/error traces and run configuration link request hashes and invocation
IDs, without requiring debug mode. `prompt_releases` records the separate stable
`release_sha256` (version files, resolved fixed text including few-shot, dependencies).
Actual request hashes vary with book/source/context; a release hash does not.
`request_sha256` hashes canonical UTF-8 JSON without the sample file's final newline;
system/user text hashes retain the gateway's plain UTF-8 text convention.

At every invocation start, a dirty workspace saves `git diff --binary HEAD` as
`workspace.patch`, including staged and unstaged tracked changes across the repository.
The receipt binds the patch hash and base commit. Untracked nonignored files are listed
with hashes, not copied; `reproduction_complete=false` explicitly marks that limitation.
Ignored private assets are covered separately by release hashes. Patches and raw model
inputs are always ignored and must be retained privately with the run. The event stream
and invocation directories preserve earlier resume receipts after the current
`run_configuration.json` advances. No historical patch is fabricated for Q1.
Outside a Git checkout, source identity is explicitly `unavailable` and reproduction
is incomplete; existing product reading is not broken by inventing a Git identity.

## Rubrics and human judgments

`rubric/<version>.md` is immutable once registered in `rubric/releases.json`, including
the initial `q1-v0` draft. Publish a new version for later rule changes, with version,
date, change and rationale at the top. Drafts cannot be selected for scoring. Only IDs
belong in example references; bodies go in ignored `state/rubric_examples/<version>/`.
`open_coding` is the explicit no-rubric sentinel, not an alias for q1-v0.

Annotator 1.9 adds `annotator_id`, `rubric_version` and `rubric_sha256` to every new
record type. Defaults are `weijiang` and `open_coding`. Existing 1.0–1.8 records remain
byte-identical and are attributed by `experiments/annotations/legacy-context.jsonl`:
batch ID + revision range + SHA-256 of that exact journal prefix. The original record
timestamp is the judgment time; the overlay date is attribution time. Later appends
cannot change the old prefix. Rejudging with a rubric appends a new revision; it never
changes old records. Do not confuse tool `annotator_version` with human `annotator_id`.

Opening a batch folder optionally reads `annotation-context.json` from that ignored
folder. It supplies batch ID, annotator ID, rubric version, rubric file SHA-256 and
`rubric_status: published`. The context is saved with that browser batch. The tool
rejects draft contexts and context switches with pending drafts; finish saving all
units first. Plain JSON opening uses the stored context or the open-coding default.
No rubric is inferred from the content of an old judgment. Existing file-prefix,
revision and conflicting-history checks still apply. New metadata does not rewrite
`batch.json`, its identity or any prior `judgments.jsonl` row.

## Fixed units and trials

`experiments/unit-sets/dev-v1.json` freezes Bovary batch 1 and Sapiens batch 1
(67 units, 110 generated marks). `holdout-v1.json` freezes Bovary batches 2/3
(75 units, 80 marks). Manifests contain original source coordinates, product/source
hashes, batch/run/reading/unit IDs and mark IDs; no source or judgment bodies.
Do not redraw samples. `experiments/frozen.json` locks these identities; the checker
also rejects edits to existing lock entries against the trusted pre-change commit.
Holdout is excluded from iteration and can only be referenced by a trial whose phase
is `final_validation`. The checker never opens holdout judgment files.

The experiment table is `experiments/log.jsonl`: one experiment per JSON object/line.
JSONL preserves lists of runs and prompt identities plus structured metrics without
embedding JSON in CSV cells. Required fields cover experiment/date/hypothesis/change,
at most one changed variable, version + release hash, fixed unit-set path + hash, run
IDs, rubric, results, conclusion and notes. Reusing historical outputs is explicitly a
baseline registration, not a model experiment. The initial `Q1-BASELINE-001` has
`results.pass_rate: null` for the owner to fill; this task calculates no pass rate.
Results may be filled in that row; unit manifests, rubric files and annotation
journals do not change. New experiment IDs are added with the checked append command.

For a byte-preserving protocol addendum, append a complete validated row with a
unique log-row ID and `amends_experiment_id` naming the original experiment. Keep
its `record_type`, actual `registered_at`, scope and pre-annotation evidence explicit;
the addendum is not a new generation experiment. Read the target and linked addenda
together. Existing rows are never overwritten or duplicated under the same ID.
This convention does not automatically alter annotator behavior or publish a rubric.


```sh
.venv/bin/python scripts/check_iteration_provenance.py
# Verify the two historical dev journal prefixes in their actual current worktree:
.venv/bin/python scripts/check_iteration_provenance.py --annotation-root /Users/baiweijiang/Documents/Projects/reading-companion-q1-annotation/reading-companion-backend/state/q1_annotation
# Prepare a new JSON trial with one changed variable, then append it:
.venv/bin/python scripts/check_iteration_provenance.py --append-trial /private/tmp/new-trial.json
# Generate context for a new review (refuses to overwrite an existing file):
.venv/bin/python scripts/check_iteration_provenance.py --write-context /path/to/batch/annotation-context.json --batch-id FULL_BATCH_ID --rubric-version open_coding --annotator-id weijiang
```

For rubric scoring, register a new published rubric and use its version instead of
`open_coding`; draft `q1-v0` is rejected. To change an existing context, prepare the new
file separately and deliberately replace it after saving drafts; this helper never
overwrites one. Retain earlier contexts with their experiment. Opening this branch's
`tools/q1-annotator.html` against the existing batch folder is sufficient; the separate
older worktree's HTML has not been changed. Avoid running both versions against the
same live journal. Validation of old metadata uses the two immutable journal-prefix
overlays; new 1.9 rows carry identity directly. Legacy judgment timestamps remain UTC.

`experiments/baselines/q1-workspace-evidence.json` records contemporaneous status
snapshots before/after the original launches and after completion. They name only
the two run-ledger files as dirty. No original patch exists, so exact historical diff
contents and inter-snapshot changes remain unknown. Historical release hashes are
marked `reconstructed_after_run`, and actual request hashes remain null. Do not
substitute today's patch or a saved pre-gateway manifest for an observed old request.
The one-time `register_q1_baseline.py` preserves the construction procedure and refuses
to overwrite existing registration; it is not a command to resample or regenerate.
