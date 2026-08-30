# LLM Structured Output Protocol Note

Purpose: record the current CPA / Luna structured-output calling policy, contract-failure audit policy, and historical provider transport compatibility notes for `attentional_v2`.
Use when: configuring LLM targets, changing `src/reading_runtime/llm_gateway.py`, or testing provider reasoning / structured-output behavior.
Not for: mechanism prompt wording, Unit Memory retrieval semantics, or product-facing evaluation criteria.
Update when: a provider contract is re-tested, the default transport policy changes, or structured-output failure auditing changes.

Status: current implementation note after the 2026-08-30 provider switch; active local operation uses CPA Manager Plus and `gpt-5.6-luna`.

## Summary

Current project-owned prompts and tools stay protocol-neutral. The selected profile decides the transport:

- Runtime, dataset review, and eval judge profiles route to the CPA OpenAI-compatible target `cpa_codex_local`.
- That target uses `gpt-5.6-luna` with explicit `reasoning_effort: medium`.
- Ingest/Digest final structured results use OpenAI function tools plus the existing project validator / repair boundary.
- OpenCode Go / DeepSeek and MiniMax transports remain historical compatibility evidence only. They are not present in current active target/profile configuration.
- `retrieve_unit_memory` remains an action tool. It is never forced merely to transport final structured output.
- For Ingest, `retrieve_unit_memory` action-tool args are the only model-authored Unit Memory recall-intent surface; final structured output must not echo `memory_recalls[]`.
- Standard runtime traces do not store raw reasoning content. Debug/probe code must opt in explicitly before preserving it.
- A provider-valid function call is not automatically a valid project result. Local validators remain the final business contract for Ingest/Digest outputs, and contract failures preserve bounded final-response evidence for diagnosis.

## Verified Matrix

| Provider path | Model / endpoint | Reasoning request | Final structured output | Status |
| --- | --- | --- | --- | --- |
| CPA Manager Plus OpenAI-compatible | `gpt-5.6-luna` at `http://127.0.0.1:8317/v1` | `reasoning_effort="medium"` | forced final-output OpenAI function tool plus local validator / repair | Current active path; bounded Digest smoke verified |
| OpenCode Go / DeepSeek OpenAI-compatible | `deepseek-v4-flash` at `https://opencode.ai/zen/go/v1` | historical `thinking` option | historical JSON-object output plus local validator / repair | Inactive; removed from current target/profile configuration |
| MiniMax Anthropic-compatible | `MiniMax-M2.7` at `https://api.minimaxi.com/anthropic` | historical thinking budget | forced final-output tool | Historical compatibility evidence only |

The official Luna model reference documents Chat Completions, function calling, structured outputs, and the supported reasoning-effort values: <https://developers.openai.com/api/docs/models/gpt-5.6-luna>.

## Default Calling Policy

### Current CPA / Luna

Configure the target with:

```json
{
  "target_id": "cpa_codex_local",
  "contract": "openai_compatible",
  "base_url": "http://127.0.0.1:8317/v1",
  "model": "gpt-5.6-luna",
  "provider_options": {
    "reasoning_effort": "medium"
  }
}
```

- Keep `reasoning_effort` at target level so runtime, review, and eval profiles inherit one explicit setting.
- Use the shared gateway's OpenAI-compatible function-tool translation.
- When a structured final result is required, call the mechanism-private final-output tool exactly once:
  - `submit_ingest_result`
  - `submit_digest_result`
  - `submit_bridge_resolution_result`
  - `submit_reflective_promotion_result`
  - `submit_reconsolidation_result`
  - `submit_chapter_consolidation_result`
  - `submit_survey_chapter_zone_result`
- Keep project validators and one bounded repair attempt as the final business contract.
- If final tool args fail the expected result shape, or if repair still fails, surface `problem_code="llm_contract"` and preserve the bounded final-response body plus parsed payload in contract-failure audit metadata.
- Keep CPA provider/profile concurrency at `1` until a separately authorized capacity test supports a higher value.

### Action Tools With CPA OpenAI-Compatible Profiles

- If `retrieve_unit_memory` is available, expose it as an auto action tool before final submission.
- After valid action-tool results are returned to the model, force only the mechanism-private final-output tool.
- Ingest final output is limited to the boundary / preview-partition result; runtime derives private/audit `memory_recalls[]` from valid non-empty action-tool args.
- Invalid optional `retrieve_unit_memory` recall args remain non-fatal `invalid_tool_noop` / `invalid_skipped` retrieval degradation. Empty optional calls remain no-op / not-requested events.
- Legacy final `memory_recalls[]` echoes are ignored rather than treated as a second authority.

### Historical OpenCode / DeepSeek JSON Object

- The former active target used `response_format={"type":"json_object"}` and provider-specific thinking options.
- It did not force a final-output tool while that thinking mode was enabled.
- Those settings are retained only in historical reports, traces, and pricing records. Reintroducing the provider requires a new explicit target/profile change and a fresh live health check.

### Historical MiniMax / Anthropic-Compatible

- The prior Anthropic-compatible path used forced final-output tools and provider thinking options.
- MiniMax official-key profiles are no longer current local operation. Reintroducing one requires an explicit new target/profile and a fresh live health check.

## Trace And Artifact Policy

- Standard LLM traces may record provider id, contract, status, usage, compact errors, and final normal content metadata.
- Standard traces must not persist raw reasoning or thinking blocks.
- Structured-output contract failures write bounded diagnostic rows to `contract_failures.jsonl` next to the standard trace sink when a trace context exists. Each row records transport path, output tool name, attempt index, validation errors, final response text hash/excerpt, parsed payload excerpt, and trace stage/node metadata; `ReaderLLMError.details.structured_output_contract` carries the compact pointer used by diagnostic runners.
- Contract-failure audit rows are for final normal response content only, not raw provider reasoning.
- Historical run artifacts may contain older transport evidence; they do not define current routing.

## Code Ownership

- Shared transport selection lives in `reading-companion-backend/src/reading_runtime/llm_gateway.py`.
- Provider/target/profile configuration lives in:
  - `reading-companion-backend/config/llm_targets.local.example.json`
  - `reading-companion-backend/config/llm_profile_bindings.local.example.json`
  - untracked local `llm_targets.local.json` / `llm_profile_bindings.local.json`
- Current local secrets are carried by `CPA_PROXY_API_KEY`; OpenCode Go and MiniMax credentials are not part of active local configuration.
- `attentional_v2` schemas and final-output tool definitions remain mechanism-private, while the shared gateway translates tool shape at the provider boundary.
