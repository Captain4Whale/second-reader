# LLM Structured Output Protocol Note

Purpose: record the current OpenCode / DeepSeek structured-output calling policy and historical MiniMax transport compatibility notes for `attentional_v2`.
Use when: configuring LLM targets, changing `src/reading_runtime/llm_gateway.py`, or testing provider thinking / structured-output behavior.
Not for: mechanism prompt wording, Unit Memory retrieval semantics, or product-facing evaluation criteria.
Update when: a provider contract is re-tested and the default transport policy changes.

Status: current implementation note after `DEC-115`; local active operation now uses OpenCode Go only.

## Summary

Current project-owned prompts and tools stay protocol-neutral. The active profile decides the transport:

- Current local profiles use OpenCode Go OpenAI-compatible targets with DeepSeek / OpenCode models, thinking, JSON-object final output, and project validator / repair.
- Anthropic-compatible MiniMax transport remains a historical compatibility note, but MiniMax official-key targets are no longer an active local routing path.
- `retrieve_unit_memory` remains an action tool. It is never forced merely to transport final structured output.
- For Ingest, `retrieve_unit_memory` action-tool args are the only model-authored Unit Memory recall-intent surface; final structured output must not echo `memory_recalls[]`.
- Standard runtime traces do not store raw thinking or reasoning content. Debug/probe code must opt in explicitly before preserving raw reasoning.

## Verified Matrix

| Provider path | Verified model / endpoint | Thinking request | Final structured output | Reasoning location | Notes |
| --- | --- | --- | --- | --- | --- |
| OpenCode Go / DeepSeek OpenAI-compatible | `deepseek-v4-flash` at `https://opencode.ai/zen/go/v1` | `extra_body={"thinking":{"type":"enabled"}}` | `response_format={"type":"json_object"}` plus local validator / repair | `message.reasoning_content` | Current local active path. Auto action tools can be used with thinking; do not force final-output `tool_choice` while thinking is enabled. |
| MiniMax Anthropic-compatible | `MiniMax-M2.7` at `https://api.minimaxi.com/anthropic` | `thinking={"type":"enabled","budget_tokens":N}` | forced final-output tool, such as `submit_ingest_result` | `response.content[]` block with `type == "thinking"` | Historical compatibility evidence only; do not route active local profiles to MiniMax official-key targets. |

OpenCode Go requires a normal OpenAI-like `User-Agent`; the shared OpenAI-compatible adapter sends `User-Agent: OpenAI/Python 1.0` by default.

## Default Calling Policy

### Historical MiniMax / Anthropic-Compatible

- Use the shared gateway Anthropic contract.
- Preserve provider thinking options from target/profile configuration when present.
- When a structured final result is required, call the mechanism-private final-output tool exactly once:
  - `submit_ingest_result`
  - `submit_digest_result`
  - `submit_bridge_resolution_result`
  - `submit_reflective_promotion_result`
  - `submit_reconsolidation_result`
  - `submit_chapter_consolidation_result`
  - `submit_survey_chapter_zone_result`
- Let action tools run separately before final submission. For current `attentional_v2`, the live action tool is `retrieve_unit_memory`.
- MiniMax official-key profiles are no longer current local operation. Reintroducing one requires an explicit new target/profile and a fresh live health check.

### Current OpenCode / DeepSeek JSON Object

- Configure the selected target or profile with:

```json
{
  "provider_options": {
    "response_format": {"type": "json_object"},
    "thinking": {"type": "enabled"}
  }
}
```

- The gateway treats `response_format={"type":"json_object"}` on an `openai_compatible` profile as the final structured-output transport.
- Do not force a final-output tool for that JSON-object profile.
- Keep project validators and one repair attempt as the final business contract.
- Instructor is part of the OpenAI-compatible dependency surface and may be used by direct OpenAI SDK probes or future parser refinements, but it does not replace project validators.
- For thinking-enabled profiles, use a larger output budget. If a selected profile omits `max_output_tokens` and either target/profile options enable thinking, the registry default is `8192`; explicit profile settings still win. `8192` is also the default engineering target for Ingest boundary probes so final JSON is not squeezed out by reasoning tokens.

### Action Tools With OpenAI-Compatible Profiles

- If `retrieve_unit_memory` is available, expose it as an auto action tool.
- The first action-tool turn may use `tool_choice="auto"` with provider thinking enabled; the June 9 Ingest reasoning probe confirmed that DeepSeek returns both `reasoning_content` and an auto `retrieve_unit_memory` tool call.
- After action tool results, request final JSON object output with no final-output `tool_choice`.
- Ingest final JSON is limited to the boundary / preview-partition result; runtime derives private/audit `memory_recalls[]` from the action-tool args. Legacy final `memory_recalls[]` echoes are ignored, not matched as a second authority.
- The restriction is on forced final-output tool choice under thinking, not on auto action-tool use.

## Trace And Artifact Policy

- Standard LLM traces may record provider id, contract, status, usage, compact errors, and final normal content metadata.
- Standard traces must not persist raw `thinking` blocks or `reasoning_content`.
- Debug/probe scripts may print or persist raw reasoning only when explicitly designed for that purpose.
- Historical run artifacts may contain older transport evidence; current stable docs and code should point to this note and `DEC-115`.

## Code Ownership

- Shared transport selection lives in `reading-companion-backend/src/reading_runtime/llm_gateway.py`.
- Provider/target/profile configuration lives in:
  - `reading-companion-backend/config/llm_targets.local.example.json`
  - `reading-companion-backend/config/llm_profile_bindings.local.example.json`
  - untracked local `llm_targets.local.json` / `llm_profile_bindings.local.json`
- Current local secrets are carried by `OPENCODE_GO_API_KEY`; MiniMax official keys are not part of the active local config.
- `attentional_v2` schemas and final-output tool definitions remain mechanism-private, while the shared gateway translates tool shape at the provider boundary.
