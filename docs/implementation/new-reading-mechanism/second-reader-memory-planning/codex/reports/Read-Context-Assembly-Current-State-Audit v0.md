# Read Context Assembly Current-State Audit v0

Status note: this audit records the pre-`read.v31` baseline that motivated `C设计11-Read Context Layer Contract v0.md`. The current implemented Read prompt now uses XML-style outer context layers; use `C设计11` and `docs/backend-reading-mechanisms/attentional_v2.md` for the current contract.

Short answer at audit time: the Read node received a structured prompt made from five visible blocks: `Structural frame`, `Current unit`, `Read context packet`, `Selective carry`, and `Policy snapshot`. The most important distinction was that the runtime first built a wider internal `carry_forward_context`, then narrowed it through `build_read_prompt_packet(...)` before rendering the actual Read prompt. `recent_reading_memory` was already included in that narrowed Read packet, but it was carried as all `active` entries with no consolidation-based pruning yet.

This document is a current-code fact audit. It does not change runtime behavior, run eval, update evidence catalog entries, or claim product quality.

## Code Path

The active mainline path is:

1. `runner._run_read_with_context_loop(...)`
   - receives the chosen unit and the current persisted mechanism state.
   - calls `build_carry_forward_context(...)`.
2. `state_projection.build_carry_forward_context(...)`
   - builds the wider internal continuity packet from persisted state.
   - this packet contains more material than the Read prompt should see directly.
3. `nodes.read_unit(...)`
   - receives the internal `carry_forward_context`.
   - calls `build_read_prompt_packet(...)`.
4. `state_projection.build_read_prompt_packet(...)`
   - projects the internal packet into the narrower Read-facing packet.
5. `nodes.read_unit(...)`
   - renders `ATTENTIONAL_V2_PROMPTS.read_unit_prompt`.
   - passes the rendered prompt to `invoke_json(...)`.
6. `runner._run_read_with_context_loop(...)`
   - normalizes `memory_uptake_ops`.
   - records private read audit through `record_read(...)`.

Primary source files:

- `reading-companion-backend/src/attentional_v2/runner.py`
- `reading-companion-backend/src/attentional_v2/state_projection.py`
- `reading-companion-backend/src/attentional_v2/nodes.py`
- `reading-companion-backend/src/attentional_v2/prompts.py`
- `reading-companion-backend/src/attentional_v2/observability.py`
- `reading-companion-backend/src/attentional_v2/schemas.py`

## Baseline Read Prompt Shape Before `read.v31`

At audit time, the Read user prompt was rendered as:

```text
Structural frame:
{structural_frame}

Current unit:
{current_unit}

Read context packet:
{carry_forward_context}

Selective carry:
{supplemental_context}

Policy snapshot:
{policy_snapshot}

Output language contract:
...
```

Important naming note: in the rendered prompt, `{carry_forward_context}` is not the raw internal `CarryForwardContext`. It is the output of `build_read_prompt_packet(...)`.

## Structural Frame

`_structural_frame(...)` provides simple book/chapter metadata:

| Field | Meaning |
| --- | --- |
| `book_title` | Current book title. |
| `author` | Current author value. |
| `chapter_title` | Current chapter title. |
| `output_language` | Runtime output language code. |

This is prompt-visible framing. It can legitimately influence Read interpretation and Recent Memory formation, but it is not source text.

## Current Unit

When source-native unit data is available, `current_unit` is rendered as:

| Field | Meaning |
| --- | --- |
| `source_span` | Paragraph + character source span for the current unit. |
| `source_text` | Full text of the current unit. |
| `paragraph_slices[]` | Paragraph-local slices with `paragraph_index`, `text_role`, `start_char`, `end_char`, and `text`. |

There is still a sentence-list fallback path for older shapes:

| Field | Meaning |
| --- | --- |
| `sentence_id` | Legacy / compatibility sentence id. |
| `text` | Sentence text. |
| `text_role` | Source text role. |

Current mechanism direction is source-span-native. Sentence ids in fallback or local continuity are compatibility / orientation metadata, not authoritative source coordinates.

## Internal Carry-Forward Context

`build_carry_forward_context(...)` builds a wider packet with these main fields:

| Field | Source | Purpose |
| --- | --- | --- |
| `packet_version` | constant `attentional_v2.state_packet.v1` | Packet schema marker. |
| `continuation_capsule` | current state or newly built capsule | Persisted continuity seed for resume / rehydration. |
| `session_continuity_capsule` | `local_buffer` + recent reactions | Cheap near-continuity view. |
| `active_attention_digest` | `active_attention` | Deprecated ActiveTension digest while store remains. |
| `recent_reading_memory` | `recent_reading_memory` | Active Recent Memory entries. |
| `chapter_reflective_frame` | `reflective_frames` | Bounded chapter/book reflective frames. |
| `active_focus_digest` | active attention + recent reactions | Derived projection, not a memory store. |
| `concept_digest` | `concept_registry` | Bounded concept digest. |
| `thread_digest` | `thread_trace` | Bounded thread digest. |
| `reflective_digest` | flattened reflective frame copies | Internal / eval convenience view. |
| `source_ref_digest` | refs from carried records | Internal / eval source-ref digest. |
| `continuity_digest` | alias of session continuity | Compatibility / audit convenience. |
| `refs` | generated carry-forward refs | Internal handle set for selective retrieval and audit. |

The internal packet is also used for navigation and observability paths. It should not be confused with the narrower Read-facing packet.

## Read-Facing Packet

`build_read_prompt_packet(...)` narrows the internal packet to:

```json
{
  "packet_version": "...",
  "local_continuity": {},
  "active_attention": {},
  "recent_reading_memory": {},
  "concept_digest": [],
  "thread_digest": [],
  "reflective_digest": {},
  "selective_carry": {}
}
```

`selective_carry` is omitted when empty.

### `local_continuity`

Built from `session_continuity_capsule`.

| Field | Current behavior |
| --- | --- |
| `recent_sentence_ids` | Last 6 recent sentence ids from `local_buffer.recent_sentences`, excluding current-unit sentence ids. Compatibility / orientation metadata. |
| `recent_meaning_units` | Last 2 recent meaning-unit sentence-id lists, excluding current-unit sentence ids. Compatibility / orientation metadata. |
| `recent_reactions` | Last 3 reaction records, marked as visible traces rather than semantic memory. |

Current caveat: this is short-term continuity glue, not durable memory. It can help local orientation, but it should not be treated as the main memory layer.

### `active_attention`

Current status: deprecated store, still prompt-carried until cleanup.

Read-facing shape:

```json
{
  "active_tensions": [
    {
      "item_id": "...",
      "tension_from": "...",
      "tension_focus": "...",
      "working_interpretation": "..."
    }
  ],
  "open_tension_count": 0,
  "projection_warning": ""
}
```

Rules:

- Only open items enter the prompt.
- Terminal items such as `answered`, `resolved`, and `closed` do not enter the prompt.
- Source refs, development refs, linked keys, statuses, coordinates, and terminal reasons are not prompt-visible.
- The prompt packet includes all open ActiveTension items it finds; if the count exceeds the soft limit, it emits `projection_warning="open_active_tension_count_exceeds_soft_limit"` instead of silently truncating.

Current caveat: this layer is no longer the target near-term memory architecture. It remains only until `recent_reading_memory` consolidation and Active Attention cleanup are implemented.

### `recent_reading_memory`

Current status: active near-term semantic memory layer.

Read-facing shape:

```json
{
  "active_entries": [
    {
      "entry_id": "...",
      "kind": "...",
      "memory_text": "...",
      "source_unit_span_id": "...",
      "created_at_unit_index": 0
    }
  ],
  "active_entry_count": 0
}
```

Projection rules:

- Includes entries where `status == "active"`.
- Skips entries without `entry_id` or `memory_text`.
- Carries `entry_id`, `kind`, `memory_text`, `source_unit_span_id`, and `created_at_unit_index`.
- Does not carry operation-level reasons.
- Does not carry fine-grained `source_refs`.
- Does not carry archived entries.

Current caveat: there is no limit or summarization in this projection yet. Until consolidation / archival exists, the active set can grow linearly with each read unit.

### `concept_digest`

Read-facing shape is a list of up to 3 concept items.

Each item can include:

| Field | Meaning |
| --- | --- |
| `ref_id` | Internal prompt/audit handle. |
| `concept_key` | Stable concept key. |
| `concept_type` | Concept type. |
| `source_refs` | Up to 4 inline SourceRefs. |
| `sample_quotes` | Up to 2 quotes sampled from SourceRefs. |
| `rationale` | Canonical `summary` from the concept entry. |
| projection markers | `projection_role`, `support_status`, warnings, etc. |

Selection behavior:

- Source code first sorts entries by number of source refs, then open-status preference, then key.
- The digest builder emits up to `_CONCEPT_DIGEST_LIMIT = 3`.
- `build_read_prompt_packet(...)` slices to 3 again.

### `thread_digest`

Read-facing shape is a list of up to 3 thread items.

Each item can include:

| Field | Meaning |
| --- | --- |
| `ref_id` | Internal prompt/audit handle. |
| `thread_key` | Stable thread key. |
| `thread_type` | Thread type. |
| `source_refs` | Up to 4 inline SourceRefs. |
| `sample_quotes` | Up to 2 quotes sampled from SourceRefs. |
| `rationale` | Canonical `summary` from the thread entry. |
| projection markers | `projection_role`, `support_status`, warnings, etc. |

Selection behavior mirrors `concept_digest`: bounded to 3.

### `reflective_digest`

Read-facing `reflective_digest` is actually the bounded `chapter_reflective_frame` dict, not the flattened internal `reflective_digest` list.

Shape:

```json
{
  "chapter_frames": [],
  "book_frames": [],
  "durable_definitions": []
}
```

Current bounds:

- `chapter_frames`: up to 2 matching current chapter, with fallback to earliest items.
- `book_frames`: up to 1.
- `durable_definitions`: up to 1.

Current caveat: the prompt-facing name `reflective_digest` hides that the value is a structured frame dict. This is not currently broken, but it is a naming clarity issue for report and code readers.

### `selective_carry`

This is optional and only appears when supplemental context or detour context exists.

From `supplemental_context`:

| Field | Bound | Meaning |
| --- | --- | --- |
| `earlier_excerpts` | 4 | Bounded look-back excerpts. |
| `source_ref_details` | 4 | Specific source refs requested/resolved. |
| `supporting_refs` | 6 | Compact supporting handles. |
| `retrieval_context` | present only if built | Sparse retrieval contract details. |

From `detour_context`:

| Field | Bound | Meaning |
| --- | --- | --- |
| `active_detour_need` | one dict | Current detour need. |
| `mainline_background` | one dict | Mainline background for detour reading. |
| `detour_trace_summary` | 4 | Compact trace summary. |

Current mainline note: normal Read calls pass `supplemental_context=None`; detour context appears only when the Navigate / detour path has provided it.

## Policy Snapshot

`reader_policy` is rendered as `Policy snapshot`.

It is not a memory store. It carries runtime policy / budget / density controls that the Read node should obey while interpreting the unit and emitting reactions / memory ops.

## What Is Deliberately Not Prompt-Carried

The Read prompt does not directly receive:

- Full `refs`.
- Full `reaction_records`.
- Full `read_audit`.
- Full source-ref history.
- Full `concept_registry`.
- Full `thread_trace`.
- Full `reflective_frames`.
- Internal `source_ref_digest`.
- Internal `active_focus_digest`.
- Full `continuation_capsule`.
- Archived `recent_reading_memory` entries.
- Terminal ActiveTension details such as answered / closed reasons.

This matches the current design principle: persisted state is not the same thing as prompt-visible state.

## After Read Returns

The Read node returns a JSON payload that can include:

- `reading_impression`
- `surfaced_reactions[]`
- `memory_uptake_ops[]`
- `detour_need`

Then the runner:

1. normalizes source refs for state operations;
2. strips source-ref payload fields from `recent_reading_memory` operations because Recent Memory is grounded by the unit span as a whole;
3. records read audit rows with `carry_forward_ref_ids`, source unit info, reactions, memory ops, admission events, detour evidence, and fallback diagnostics;
4. applies state updates in settlement.

For Recent Reading Memory specifically:

- LLM proposes an append op with `kind` and `memory_text`.
- Runner/state code owns `entry_id`, `source_unit_span_id`, `created_at_unit_index`, `status`, and archival fields.
- Recent Memory append ops do not use an operation-level `reason`.

## Current Review Targets

The current assembly is functional, but the following points deserve review before consolidation design:

1. `recent_reading_memory` is currently unbounded in prompt projection. This is acceptable for micro windows but not for full-book reading without consolidation / archival.
2. `active_attention` is still prompt-visible even though it is deprecated. This should be removed after Recent Memory consolidation and cleanup are approved.
3. `local_continuity` still exposes sentence-id-shaped orientation fields. They are compatibility metadata, not canonical source coordinates.
4. `reflective_digest` is a slightly misleading prompt key because it contains `chapter_reflective_frame` structure.
5. Concept and thread digests are bounded to 3 each. This keeps context small, but selection quality may matter once Recent Memory consolidation begins producing more long-distance memory.
6. There is not yet a priority policy across Recent Memory vs concept/thread/reflective context. The current design relies on all active Recent Memory being carried and long-distance stores being compact digests.

## Suggested Next Audit

Use the retry4 prompt manifests / read audit to inspect several actual Read prompts:

- confirm each Read after unit 2 receives prior `recent_reading_memory.active_entries`;
- check whether the context is readable and not overbearing;
- compare entries that later Read generated against the prior context it received;
- decide whether consolidation is enough to control growth, or whether a temporary projection soft-limit is needed before consolidation lands.

This should be read-only first. Any projection change should be a separate accepted implementation step.
