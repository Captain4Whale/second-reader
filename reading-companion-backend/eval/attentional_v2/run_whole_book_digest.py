"""One approved whole-book Digest request, with offline preparation and rendering.

This intentionally bypasses the Digest wrapper's automatic repair/normalization,
while retaining its prompt, final-output tool, validator, and shared gateway.
It neither commits a Product Unit nor changes the normal reading pipeline.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import xml.etree.ElementTree as ET
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.attentional_v2.llm_output_tools import (
    DIGEST_RESULT_TOOL,
    validate_digest_result,
)
from src.attentional_v2.prompts.digest import (
    DIGEST_PROMPT_VERSION,
    DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
    render_digest_prompt_xml,
)
from src.reading_runtime import llm_gateway as gateway
from src.reading_runtime.llm_registry import (
    DEFAULT_DATASET_REVIEW_PROFILE_ID,
    DEFAULT_EVAL_JUDGE_PROFILE_ID,
    clear_llm_registry_cache,
    get_llm_registry,
)
from src.reading_runtime.observation_context import run_observation_scope

from .whole_book_digest_artifacts import (
    prepare_source,
    render_historical_reference,
    render_review,
    review_payload,
)

BACKEND_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "xidaduo_fullbook_single_digest_20260913"
JOB_ID = f"bgjob_{RUN_ID}"
DEFAULT_RUN_DIR = BACKEND_ROOT / "state" / "experiments" / RUN_ID
BASELINE = (
    BACKEND_ROOT
    / "state/reading_product_live_acceptance/cpa_luna_xidaduo_full_book_20260903/book-output"
)
SOURCE_HASH = "6d75c4bdd06668ccfc03c2a96ea4b484a31898fda05f8dfe793b852efcdb3be9"
TARGET_ID = "cpa_codex_local"
PROFILE_ID = "runtime_reader_default"
MODEL = "gpt-5.6-luna"
OUTPUT_TOKENS = 65536
TIMEOUT_SECONDS = 1800


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, data: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def xml_root(text: str) -> ET.Element:
    return ET.fromstring(f"<root>{text}</root>")


def build_prompt(source: dict, historical_manifest: dict) -> dict:
    old = xml_root(historical_manifest["user_prompt"])
    identity = json.loads("".join(old.find("BookInfo").itertext()).strip())
    assembly = render_digest_prompt_xml(
        book_title=identity["book_title"],
        author=identity["author"],
        chapter_title="全书",
        output_language_name="Chinese",
        reading_memory_lines=[],
        current_unit_source={
            "source_text": source["source_text"],
            "paragraph_slices": source["paragraph_slices"],
        },
    )
    current = xml_root(assembly.rendered_text)
    fixed_checks = {
        tag: ET.tostring(old.find(tag)) == ET.tostring(current.find(tag))
        for tag in ("ReaderRole", "Instruction", "BookInfo", "OutputContract")
    }
    fixed_checks["system_prompt"] = (
        historical_manifest["system_prompt"] == DIGEST_XML_TRANSPORT_SYSTEM_PROMPT
    )
    if historical_manifest["prompt_version"] != DIGEST_PROMPT_VERSION or not all(
        fixed_checks.values()
    ):
        raise ValueError(f"Historical Digest prompt drift: {fixed_checks}")
    rendered_paragraphs = current.findall(
        "./CurrentFocus/ReadingObject/SourceUnit/Paragraph"
    )
    if (
        "\n\n".join((p.text or "").strip() for p in rendered_paragraphs)
        != source["source_text"]
    ):
        raise ValueError("Prompt source differs from frozen full text")
    if "".join(current.find("ReadingMemory").itertext()).strip():
        raise ValueError("ReadingMemory must be empty")
    return {
        "system_prompt": DIGEST_XML_TRANSPORT_SYSTEM_PROMPT,
        "user_prompt": assembly.rendered_text,
        "output_tool": DIGEST_RESULT_TOOL,
        "fixed_block_checks": fixed_checks,
        "prompt_version": DIGEST_PROMPT_VERSION,
    }


def isolated_config(targets: dict, bindings: dict) -> tuple[dict, dict]:
    target = next(dict(t) for t in targets["targets"] if t["target_id"] == TARGET_ID)
    profile = next(
        dict(p) for p in bindings["profiles"] if p["profile_id"] == PROFILE_ID
    )
    # Only an environment reference is allowed in persisted experiment config.
    for credential in target.get("credentials", []):
        if credential.get("api_key") or not credential.get("api_key_env"):
            raise ValueError("Experiment requires environment-backed credentials")
    if (
        target["model"] != MODEL
        or target.get("provider_options", {}).get("reasoning_effort") != "medium"
    ):
        raise ValueError("Model or reasoning effort differs from the approved baseline")
    target.update(
        timeout_seconds=TIMEOUT_SECONDS,
        retry_attempts=1,
        max_concurrency=1,
        initial_max_concurrency=1,
        probe_max_concurrency=1,
        min_stable_concurrency=1,
    )
    profile.update(
        target_tiers=[
            {
                "tier_id": "primary",
                "target_ids": [TARGET_ID],
                "min_required_stable_concurrency": 1,
            }
        ],
        temperature=0.2,
        max_output_tokens=OUTPUT_TOKENS,
        timeout_seconds=TIMEOUT_SECONDS,
        retry_attempts=1,
        quota_retry_attempts=0,
        quota_wait_budget_seconds=0,
        max_concurrency=1,
        default_burst_concurrency=1,
    )
    # Registry requires these names even though this runner only uses the reader.
    profiles = [
        {**profile, "profile_id": name}
        for name in (
            PROFILE_ID,
            DEFAULT_DATASET_REVIEW_PROFILE_ID,
            DEFAULT_EVAL_JUDGE_PROFILE_ID,
        )
    ]
    return {"targets": [target]}, {"profiles": profiles}


def prepare(run_dir: Path, baseline: Path) -> dict:
    if (run_dir / "request.started.json").exists():
        raise ValueError(
            "This experiment has already reserved its only request; use --render"
        )
    source = prepare_source(baseline)
    text = source["source_text"]
    if (
        len(source["paragraph_slices"]) != 552
        or len(text) != 55185
        or digest_bytes(text.encode()) != SOURCE_HASH
        or source["metrics"]["unit_count"] != 89
        or source["metrics"]["historical_marginalia_count"] != 207
    ):
        raise ValueError(
            "Source differs from the approved 552-paragraph Xidaduo baseline"
        )
    historical_manifest = read_json(
        baseline / "_mechanisms/attentional_v2/internal/prompt_manifests/digest.json"
    )
    packet = build_prompt(source, historical_manifest)
    targets, bindings = isolated_config(
        read_json(BACKEND_ROOT / "config/llm_targets.local.json"),
        read_json(BACKEND_ROOT / "config/llm_profile_bindings.local.json"),
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "source.json", source)
    (run_dir / "source.txt").write_text(text)
    write_json(run_dir / "prompt.json", packet)
    (run_dir / "prompt.xml").write_text(packet["user_prompt"])
    write_json(run_dir / "targets.local.json", targets)
    write_json(run_dir / "bindings.local.json", bindings)
    (run_dir / "historical-reference.md").write_text(
        render_historical_reference(source)
    )
    hashes = {
        name: digest_bytes((run_dir / name).read_bytes())
        for name in (
            "source.json",
            "source.txt",
            "prompt.json",
            "prompt.xml",
            "targets.local.json",
            "bindings.local.json",
        )
    }
    manifest = {
        "run_id": RUN_ID,
        "job_id": JOB_ID,
        "status": "prepared",
        "prepared_at": now(),
        "baseline_output": str(baseline),
        "source_sha256": SOURCE_HASH,
        "paragraph_count": 552,
        "source_characters": 55185,
        "source_metrics": source["metrics"],
        "model": MODEL,
        "target_id": TARGET_ID,
        "profile_id": PROFILE_ID,
        "reasoning_effort": "medium",
        "temperature": 0.2,
        "max_output_tokens": OUTPUT_TOKENS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "application_request_limit": 1,
        "repair_attempts": 0,
        "proxy_internal_attempts": "not_observable",
        "artifact_hashes": hashes,
        "fixed_block_checks": packet["fixed_block_checks"],
        "baseline_prompt_manifest_sha256": digest_bytes(
            json.dumps(historical_manifest, sort_keys=True).encode()
        ),
        "runner_sha256": digest_bytes(Path(__file__).read_bytes()),
    }
    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "status.json", {"status": "prepared", "updated_at": now()})
    return manifest


def verify_prepared(run_dir: Path) -> dict:
    manifest = read_json(run_dir / "manifest.json")
    for name, expected in manifest["artifact_hashes"].items():
        if digest_bytes((run_dir / name).read_bytes()) != expected:
            raise ValueError(f"Frozen artifact changed: {name}")
    if (
        manifest["source_sha256"] != SOURCE_HASH
        or manifest["application_request_limit"] != 1
    ):
        raise ValueError("Experiment manifest does not match approved scope")
    return manifest


def reserve_request(run_dir: Path) -> None:
    # Exclusive creation survives process crashes and prevents a second attempt.
    with (run_dir / "request.started.json").open("x") as handle:
        json.dump({"started_at": now(), "pid": os.getpid(), "run_id": RUN_ID}, handle)


class SingleRequestAdapter:
    """Enforce the physical application-call limit below all gateway retry paths."""

    def __init__(self, delegate: Any, run_dir: Path):
        self.delegate = delegate
        self.run_dir = run_dir
        self.count = 0

    def invoke(self, messages: list, **kwargs: Any) -> Any:
        if self.count:
            raise RuntimeError("Second application request refused")
        profile = kwargs["profile"]
        options = kwargs.get("invocation_options") or {}
        if (
            profile.model,
            profile.max_output_tokens,
            profile.temperature,
            options.get("reasoning_effort"),
        ) != (
            MODEL,
            OUTPUT_TOKENS,
            0.2,
            "medium",
        ):
            raise ValueError("Effective request differs from approved model/budget")
        if profile.retry_attempts != 1 or profile.quota_retry_attempts != 0:
            raise ValueError("Automatic retries must be disabled")
        if (
            kwargs["timeout_seconds"] != TIMEOUT_SECONDS
            or kwargs["provider"].provider_id != TARGET_ID
        ):
            raise ValueError(
                "Effective timeout or target differs from approved request"
            )
        request = {
            "started_at": now(),
            "application_request_number": 1,
            "model": profile.model,
            "temperature": profile.temperature,
            "max_output_tokens": profile.max_output_tokens,
            "timeout_seconds": kwargs["timeout_seconds"],
            "target_id": kwargs["provider"].provider_id,
            "messages": [{"role": m.type, "content": m.content} for m in messages],
            "tools": kwargs.get("tools"),
            "tool_choice": kwargs.get("tool_choice"),
            "invocation_options": options,
        }
        write_json(self.run_dir / "request.json", request)
        self.count += 1
        return self.delegate.invoke(messages, **kwargs)


def normal_response(response: Any) -> dict:
    """Keep normal visible content/tool arguments/usage, never private reasoning."""
    content = response.content
    if isinstance(content, list):
        content = [
            b
            for b in content
            if isinstance(b, str)
            or (
                isinstance(b, dict)
                and b.get("type")
                in {"text", "output_text", "tool_use", "function_call"}
            )
        ]
    metadata = response.response_metadata or {}
    extra = response.additional_kwargs or {}
    return {
        "content": content,
        "tool_calls": response.tool_calls,
        "invalid_tool_calls": response.invalid_tool_calls,
        "raw_tool_calls": extra.get("tool_calls", []),
        "refusal": extra.get("refusal"),
        "response_metadata": {
            k: metadata[k]
            for k in (
                "finish_reason",
                "model_name",
                "model_provider",
                "token_usage",
                "system_fingerprint",
                "id",
            )
            if k in metadata
        },
        "usage_metadata": response.usage_metadata,
    }


def interpret_response(raw: dict, source: dict) -> tuple[Any, list[str]]:
    errors = []
    if raw.get("response_metadata", {}).get("finish_reason") not in {
        "tool_calls",
        "stop",
    }:
        errors.append(
            f"Non-complete finish reason: {raw.get('response_metadata', {}).get('finish_reason')}"
        )
    calls = raw.get("tool_calls") or []
    expected = DIGEST_RESULT_TOOL["name"]
    matching = [c for c in calls if c.get("name") == expected]
    payload = matching[0].get("args") if matching else None
    if len(calls) != 1 or len(matching) != 1:
        errors.append("Expected exactly one submit_digest_result tool call")
    if raw.get("invalid_tool_calls"):
        errors.append(
            "Response contains unparseable tool arguments; retained in raw-response.json"
        )
    if isinstance(payload, dict):
        errors.extend(
            validate_digest_result(payload, current_unit_texts=[source["source_text"]])
        )
        from jsonschema import Draft202012Validator

        errors.extend(
            e.message
            for e in Draft202012Validator(
                DIGEST_RESULT_TOOL["input_schema"]
            ).iter_errors(payload)
        )
    else:
        errors.append("Digest payload is not an object")
    return payload, errors


def render(run_dir: Path) -> dict:
    source = read_json(run_dir / "source.json")
    raw = read_json(run_dir / "raw-response.json")
    payload, contract_errors = interpret_response(raw, source)
    review = review_payload(payload, source)
    review["contract_errors"] = contract_errors
    write_json(run_dir / "parsed-result.json", payload)
    write_json(run_dir / "quote-validation.json", review)
    markdown = render_review(payload, review, "《悉达多》单次整书 Digest：人工审阅")
    if contract_errors:
        markdown = (
            "运行未完整通过结构/终止检查；以下内容仅供诊断，不是合格完成结果。\n\n"
            + markdown
        )
    (run_dir / "review.md").write_text(markdown)
    return {"contract_errors": contract_errors, "counts": review["counts"]}


def run(run_dir: Path) -> dict:
    manifest = verify_prepared(run_dir)
    if (run_dir / "request.started.json").exists():
        raise ValueError(
            "This experiment already used/reserved its one request; use --render"
        )
    os.environ["LLM_TARGETS_PATH"] = str(run_dir / "targets.local.json")
    os.environ["LLM_PROFILE_BINDINGS_PATH"] = str(run_dir / "bindings.local.json")
    clear_llm_registry_cache()
    registry = get_llm_registry()
    # The production parser floors quota retries at one. This dedicated process
    # uses its own frozen config/cache; remove that floor only for this experiment.
    for profile_id, profile in registry.profiles.items():
        registry.profiles[profile_id] = replace(profile, quota_retry_attempts=0)
    if not registry.get_provider(TARGET_ID).resolved_key_pool():
        raise ValueError("Existing CPA credential is unavailable")
    packet = read_json(run_dir / "prompt.json")
    reserve_request(run_dir)
    write_json(run_dir / "status.json", {"status": "running", "updated_at": now()})
    started = time.monotonic()
    adapter = SingleRequestAdapter(
        gateway.CONTRACT_ADAPTERS["openai_compatible"], run_dir
    )
    gateway.CONTRACT_ADAPTERS["openai_compatible"] = adapter
    summary = {**manifest, "status": "failed", "application_request_count": 0}
    try:
        with run_observation_scope(
            run_dir,
            JOB_ID,
            run_id=RUN_ID,
            mechanism_key="attentional_v2",
            job_kind="whole_book_digest_experiment",
            stage="digest",
            node="digest",
        ):
            with gateway.llm_invocation_scope(
                profile_id=PROFILE_ID,
                pinned_target_id=TARGET_ID,
                trace_context=gateway.LLMTraceContext(
                    standard_sink=gateway.JsonlTraceSink(
                        run_dir / "llm-standard.jsonl"
                    ),
                    mechanism_key="attentional_v2",
                    stage="digest",
                    node="digest",
                ),
            ):
                # One low-level shared-gateway request; validation is local only.
                response = gateway._invoke_response(
                    packet["system_prompt"],
                    packet["user_prompt"],
                    explicit_profile_id=PROFILE_ID,
                    tools=[packet["output_tool"]],
                    tool_choice={"type": "tool", "name": DIGEST_RESULT_TOOL["name"]},
                )
                raw = normal_response(response)
                write_json(run_dir / "raw-response.json", raw)
        summary.update(render(run_dir))
        summary.update(
            usage=raw["usage_metadata"], response_metadata=raw["response_metadata"]
        )
        summary["status"] = "failed" if summary["contract_errors"] else "review_pending"
    except Exception as exc:
        # Do not serialize provider repr/traceback: it can contain credentials.
        summary["error"] = {
            "type": type(exc).__name__,
            "problem_code": getattr(exc, "problem_code", None),
        }
        if not (run_dir / "review.md").exists():
            (run_dir / "review.md").write_text(
                "# 《悉达多》单次整书 Digest\n\n本次请求未生成完整可审阅结果，已停止，未自动重试。\n"
                "请查看 summary.json、llm-standard.jsonl 及已保存的原始响应（若有）。\n"
            )
    finally:
        gateway.CONTRACT_ADAPTERS["openai_compatible"] = adapter.delegate
        summary.update(
            application_request_count=adapter.count,
            elapsed_seconds=round(time.monotonic() - started, 3),
            completed_at=now(),
        )
        write_json(run_dir / "summary.json", summary)
        write_json(
            run_dir / "status.json",
            {
                "status": "completed"
                if summary["status"] == "review_pending"
                else "failed",
                "review_status": summary["status"],
                "updated_at": now(),
            },
        )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run", action="store_true")
    action.add_argument("--render", action="store_true")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--baseline-output", type=Path, default=BASELINE)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if args.prepare:
        result = prepare(run_dir, args.baseline_output.resolve())
    elif args.run:
        result = run(run_dir)
    else:
        result = render(run_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
