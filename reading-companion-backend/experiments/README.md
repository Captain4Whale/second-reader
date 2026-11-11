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
drafts. Publish a new version for later rule changes, with version, date, change and
rationale at the top. Drafts cannot be selected for scoring. The owner-approved
`q1-v0` is now published; the original unreferenced draft is preserved byte-for-byte
as `q1-v0-draft`, with its original registration and the explicit migration receipt
retained in `rubric/releases.json` and bound by `experiments/frozen.json`.
This one-time authorized migration does not relax the existing draft-freezing rule.

`q1-v1` and `q1-v1.form.v1` were published on 2026-11-11 as new files and registry
entries; all v0 bytes/identities remain unchanged. See [v1 verification](../rubric/q1-v1.verification.md)
and [separate review sessions](rubric-review.md#published-v1-and-separate-sessions-2026-11-11).
Its 38-example exclusion list has exactly the same identities as v0; the two former
N2 counterexamples now belong to N1. Use the list matching the chosen rubric version.
The stopped v0 review and the fresh v1 review must not share criterion judgments.
The INDEX shows the owner correction from
`Q1-DIGEST-DIAG-001-HIGHLIGHT-RECONCILIATION-001` above the table and the three case
findings in the experiment details. Original closure text is explicitly folded as
historical text when owner verification addenda are present. Conclusions are read
from the append-only log, not hardcoded in the generator; the frozen v0 pending
score and all historical records remain unchanged.

Model-generated Note bodies and human reasons without separately copied book passages
may be tracked in a rubric, as explicitly authorized for q1-v0. Book passages, anchors,
rendered prompt examples and raw source-bearing data remain in ignored state directories.
`rubric/q1-v0.examples.json` freezes all 38 referenced annotations (including ID-only
references); [the verification report](../rubric/q1-v0.verification.md) lists body and
reason differences without editing the supplied rubric. Judge-human agreement must
exclude those examples; see [comparison.md](comparison.md#rubric-example-exclusion).
The existing immutable check covers rubric text, registered entries and frozen example
lists, including simultaneous file/hash edits. Use a trusted pre-change `--base-ref`.
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
baseline registration, not a model experiment. The historical `Q1-BASELINE-001` retains `results.pass_rate: null` byte-for-byte.
Its computed scores now live in `scorings.jsonl`; do not manually fill or edit old
experiment rows. Both logs are append-only. New experiment IDs are added with the
checked append command; scoring snapshots use the scoring append command below.

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

For rubric scoring, use a published version such as `q1-v0` instead of
`open_coding`; `q1-v0-draft` is rejected. No existing batch context was changed by
publication. To change an existing context, prepare the new
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

## Independent DIAG-001 artifact copy

The former main-workspace DIAG path is still a symlink into the replay worktree.
The independent copy is `state/experiments/Q1-DIGEST-DIAG-001/files`, with an adjacent
`manifest.json`. `Q1-DIGEST-DIAG-001-LOCATION-001` appends old-to-new path mappings
and the manifest hash; historical paths/records remain unchanged. Verify with
`python scripts/q1_private_snapshot.py state/experiments/Q1-DIGEST-DIAG-001`.
This copy is not a backup; the source worktree must still be preserved.

## Scoring receipts (q1-scoring/1)

`experiments/scorings.jsonl` is append-only: one row per frozen scoring snapshot,
not per generation run. `series_id` identifies one scoring scope; `scoring_id`
identifies its snapshot. A later row names the immediately preceding snapshot in
`supersedes`; it never edits a pending or completed row. Changing products, unit set,
rubric/form, scorer or review session requires a new series. `comparable_to` records
explicit comparison scope and limitations, not just a list of unrelated IDs.

Each row binds product/run/group/model/reasoning/prompt identities; a frozen unit
manifest; rubric/form hashes; human or versioned judge identity; per-journal SHA-256,
cutoff revision, original timestamp range and annotator versions; exposure context;
and the statistics implementation and input evidence hashes. Historical prompt release
hashes remain reconstructed, with unavailable actual request hashes null. Human
open_coding has no form or criterion counts; those fields are null, never inferred
from free-text reasons. Published form criteria may overlap on one failed annotation.

Note and Highlight counts stay separate per product group. `total` counts eligible
outputs, `judged = passed + failed`, and `pass_rate = passed / judged` (null when
unjudged). Completion and missing counts are explicit. New rubric rows count only
completed judgments. A pending receipt binds an empty snapshot, not a live journal.
`registered_at` is the real backfill time; judgment dates remain historical.

Private snapshots/reports live under ignored `state/scorings/`. To validate, recompute,
or append a fully prepared receipt without changing any annotations:

```sh
.venv/bin/python scripts/q1_scoring.py --base-ref TRUSTED_PRE_CHANGE_COMMIT
.venv/bin/python scripts/q1_scoring.py --evidence --base-ref TRUSTED_PRE_CHANGE_COMMIT
.venv/bin/python scripts/q1_scoring.py --append state/scorings/new-receipt.json
```

Validation rejects rewritten log prefixes, duplicate IDs, broken snapshot chains,
unknown releases, mismatched scope/counts and partial JSONL tails. `--evidence` also
checks all bound bytes and recalculates results from frozen inputs. A plain public
checkout can validate metadata without private source files; evidence validation
requires provisioned private data. Path resolution uses the most specific matching
prefix in append-only `path_mappings`; a later mapping of that same prefix wins.

## 中文总表与本机备份

[INDEX.md](INDEX.md) 的主表按 `series_id` 只显示最新评分快照，原始快照在下方
折叠；每次评分的小节包含分组分母、逐条款不过数、哈希、标注时间和可比性。
同一实验的 continuation/addendum 日志合并展示；历史结论不覆盖最新收尾决策。

```sh
.venv/bin/python scripts/q1_experiment_index.py
.venv/bin/python scripts/q1_experiment_index.py --check
```

`make agent-check` 包含评分元数据、日志追加约束及 INDEX 一致性检查；私有证据
复算使用 `q1_scoring.py --evidence`，不会写标注。补登记程序
`register_q1_scorings.py` 仅记录初始三次评分，目标目录已存在则拒绝再次运行。

备份采用显式本机快照，不安装定时任务，不访问外部服务，不覆盖或删除旧备份。
命令只收集 Q1 相关的实验实体副本、两本原始整书产物、第一批及保留批次目录、
评分快照、当前 q1-v0 会话、私有 rubric 例子和 few-shot；另存复算所需的受版本
管理脚本、单元清单、prompt 发布登记、rubric/form。不会遍历整个 state、读取
环境凭据或隐式跟随工作树内的软链接。保留批次只做字节备份与 JSON 语法校验，
不参与评分或内容审阅。

```sh
.venv/bin/python scripts/q1_backup.py \
  --annotation-root /Users/baiweijiang/Documents/Projects/reading-companion-q1-annotation/reading-companion-backend/state/q1_annotation
```

默认写 `~/Backups/second-reader/<UTC时间戳>/`。`files/` 是真实文件副本，
`manifest.json` 记录逐文件大小及 SHA-256；`verification.json` 记录恢复结果。
独立恢复副本保留在 `state/backup_verification/<UTC时间戳>/restore/files/`。
恢复后的评分脚本直接读取恢复目录内的证据重新计算三个评分，再验证 INDEX；
不回退读取原工作树。原路径仅作为历史来源信息保留。

源文件在复制期间变化、JSONL 尾行不完整或哈希不符时明确失败，不称为成功备份。
失败目录保留以供诊断，重试必须使用新时间戳。完成标记是通过恢复验证后才写入的
`verification.json`。未来可考虑工作期间每小时快照、每轮评分后再补一次；
是否安装定时任务由用户另行确认。不自动清理旧备份。本机同盘备份防误操作，
不能防整机或磁盘损坏；本任务未进行任何云端上传。
