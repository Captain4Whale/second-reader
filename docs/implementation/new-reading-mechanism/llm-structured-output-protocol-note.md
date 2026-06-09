# LLM Structured Output Protocol Note

Purpose: record the verified MiniMax / DeepSeek transport matrix and the default backend calling policy for current `attentional_v2` structured outputs.
Use when: configuring LLM targets, changing `src/reading_runtime/llm_gateway.py`, or testing provider thinking / structured-output behavior.
Not for: mechanism prompt wording, Unit Memory retrieval semantics, or product-facing evaluation criteria.
Update when: a provider contract is re-tested and the default transport policy changes.

Status: current implementation note after `DEC-115`.

## Summary

Current project-owned prompts and tools stay protocol-neutral. The active profile decides the transport:

- Anthropic-compatible MiniMax uses thinking plus forced final-output tools.
- OpenAI-compatible DeepSeek / OpenCode JSON-object profiles use thinking plus JSON-object final output and project validator / repair.
- `retrieve_unit_memory` remains an action tool. It is never forced merely to transport final structured output.
- Standard runtime traces do not store raw thinking or reasoning content. Debug/probe code must opt in explicitly before preserving raw reasoning.

## Verified Matrix

| Provider path | Verified model / endpoint | Thinking request | Final structured output | Reasoning location | Notes |
| --- | --- | --- | --- | --- | --- |
| MiniMax Anthropic-compatible | `MiniMax-M2.7` at `https://api.minimaxi.com/anthropic` | `thinking={"type":"enabled","budget_tokens":N}` | forced final-output tool, such as `submit_ingest_result` | `response.content[]` block with `type == "thinking"` | Keep final-output tools as the default Anthropic transport. |
| DeepSeek OpenAI-compatible | `deepseek-v4-flash` at `https://opencode.ai/zen/go/v1` | `extra_body={"thinking":{"type":"enabled"}}` | `response_format={"type":"json_object"}` plus local validator / repair | `message.reasoning_content` | Do not force final-output `tool_choice` while thinking is enabled. |

OpenCode Go requires a normal OpenAI-like `User-Agent`; the shared OpenAI-compatible adapter sends `User-Agent: OpenAI/Python 1.0` by default.

## Default Calling Policy

### MiniMax / Anthropic-Compatible

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

### DeepSeek / OpenAI-Compatible JSON Object

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
- The first action-tool turn may use tools; provider `thinking` is omitted in tool-present OpenAI-compatible calls because forced/tool mixed thinking has provider limitations.
- After action tool results, request final JSON object output with no final-output `tool_choice`.

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
- `attentional_v2` schemas and final-output tool definitions remain mechanism-private, while the shared gateway translates tool shape at the provider boundary.
