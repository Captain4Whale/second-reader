# Attentional_v2 Phase F4A Focused Quality Audit

Date: `2026-04-19`

Run:

- job id: `bgjob_attentional_v2_f4a_quality_audit_20260419`
- run id: `attentional_v2_f4a_quality_audit_20260419`
- summary:
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_f4a_quality_audit_20260419/summary/aggregate.json`
  - `reading-companion-backend/eval/runs/attentional_v2/attentional_v2_f4a_quality_audit_20260419/summary/report.md`

## Scope

This audit was the first post-`Phase F3` focused quality check for the new `Read`-owned `attentional_v2` live path.

It used the fixed six-case short-window pack:

- `supremacy_private_en__chapter_13`
- `value_of_others_private_en__8_10`
- `huochu_shengming_de_yiyi_private_zh__segment_1`
- `xidaduo_private_zh__segment_1`
- `nawaer_baodian_private_zh__segment_1`
- `mangge_zhi_dao_private_zh__segment_1`

Each shard ran in parallel, but each case still read serially and stopped after `8` formal units.

## Top-Line Findings

### 1. Visible reaction density recovered

The old "almost never speaks" regression did not reproduce.

- `supremacy_private_en__chapter_13`: `7` reactions over `8` units, `2` silent units
- `value_of_others_private_en__8_10`: `6` reactions over `8` units, `3` silent units
- `huochu_shengming_de_yiyi_private_zh__segment_1`: `8` reactions over `8` units, `3` silent units
- `xidaduo_private_zh__segment_1`: `7` reactions over `8` units, `3` silent units
- `nawaer_baodian_private_zh__segment_1`: `8` reactions over `8` units, `2` silent units
- `mangge_zhi_dao_private_zh__segment_1`: `4` reactions over `8` units, `5` silent units

Interpretation:

- removing the live `Express` node and returning visible-reaction ownership to `Read` fixed the main density collapse
- `supremacy_private_en__chapter_13` in particular no longer shows the old long silent stretch problem

### 2. Reaction wording is mostly back in "reading-time" territory

The sampled reactions are now usually:

- anchored to a concrete quote inside the current unit
- phrased as an immediate notice, local tension, or textual hinge
- much less like broad chapter summary or post-hoc book review

Strong examples:

- `supremacy_private_en__chapter_13`
  - `"extricate themselves from the grip"` -> immediate attention to diction and local power dynamics
- `huochu_shengming_de_yiyi_private_zh__segment_1`
  - `"亲口讲述"` / `"小的磨难"` -> short, local, close-reading style reactions
- `nawaer_baodian_private_zh__segment_1`
  - `"能学会。"` / `"做什么、和谁一起做、什么时候做"` -> short, text-near, non-summary reactions

Caution:

- some `xidaduo_private_zh` and `value_of_others_private_en` reactions still lean toward literary-analysis or argumentative mini-essay wording
- this is much better than the old summary voice, but it is not yet uniformly "just-read, just-reacted"

### 3. Anchor honesty looked healthy in the sampled pass

In the sampled reactions:

- `anchor_quote` stayed inside the current unit
- the body of the reaction generally answered the quoted local phrase rather than drifting to unrelated chapter material

No obvious case surfaced where compat projection was driving the wording itself.

### 4. Detour was not validated

This is the main failing outcome of the audit.

Across all six cases:

- `detour_trace_count = 0`
- `backward_pull = 0` in every shard
- `detour_need.status=open|resolved|abandoned = 0`

Implication:

- the new detour machinery is landed in code, but this audit did not actually exercise it
- we therefore cannot claim `land_region`, `narrow_scope -> land_region`, or `defer_detour` quality from this pack
- `xidaduo_private_zh__segment_1` and `mangge_zhi_dao_private_zh__segment_1` were intended as detour-risk samples, but they still stayed on plain mainline reading inside the short audit window

### 5. Surfaced semantics were too quiet

Across all six cases:

- `prior_link_count = 0`
- `outside_link_count = 0`
- `search_intent_count = 0`

Interpretation:

- the mechanism is now speaking again, but it is still under-surfacing the optional structured semantics we explicitly wanted to keep honest
- this does not mean the model never used prior material or internal knowledge; it means those relations did not become explicit surfaced outputs in this pack

### 6. Compat outputs are still intact

For all six shards:

- chapter-result compatibility projection exists
- normalized eval bundle exists

So the surfaced-native truth is not breaking the existing compat exports.

## Operational Notes

### Summary/report harness gap

The first generated F4A summary left `compat_projection_available` and `normalized_eval_available` as `null` even though the files existed.

This was a harness aggregation bug, not a mechanism failure.

It was fixed in-place by:

- teaching the F4A aggregator to compute artifact availability explicitly
- regenerating the per-shard `result.json` plus `summary/aggregate.json` and `summary/report.md` from the finished outputs

### Read-audit visibility gap

The first F4A run confirmed that `read_audit.jsonl` still persisted only `surfaced_reaction_count`, not the full `surfaced_reactions` payload.

That made per-unit quality review less transparent than it should be.

The audit persistence code is now patched so future runs keep:

- `surfaced_reaction_count`
- full `surfaced_reactions`

This visibility fix was landed after the run completed, so the April 19 F4A run itself still reflects the old count-only read-audit shape.

## Case-Level Verdict

### Pass / encouraging

- `supremacy_private_en__chapter_13`
  - clear density recovery
  - local English reactions feel immediate and text-near
- `nawaer_baodian_private_zh__segment_1`
  - strong local anchoring
  - short-form reaction style works well
- `mangge_zhi_dao_private_zh__segment_1`
  - restraint looked honest
  - did not over-expand into outside commentary

### Mixed

- `huochu_shengming_de_yiyi_private_zh__segment_1`
  - local and anchored, but still fairly talkative for a "restrained" sample
- `value_of_others_private_en__8_10`
  - local and critical, but still somewhat essay-like
  - no surfaced cross-chapter carryover signal
- `xidaduo_private_zh__segment_1`
  - anchored and readable, but several reactions still read like polished literary commentary
  - no detour despite being chosen as a detour-risk sample

## Decision

`Phase F4A` is only a partial pass.

What passed:

- visible reaction density
- local anchoring
- compat export survival

What did not pass:

- detour validation
- surfaced `prior_link / outside_link / search_intent` behavior

Recommended next move:

1. make one small repair pass focused on:
   - detour trigger willingness
   - explicit surfaced semantic honesty
   - any remaining over-literary reaction voice in the English / `悉达多` samples
2. rerun the same six-case F4A pack
3. only move to `Phase F4B` after at least one real detour path is observed and the structured surfaced semantics appear when genuinely warranted
