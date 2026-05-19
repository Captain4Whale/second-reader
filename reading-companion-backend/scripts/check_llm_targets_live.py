#!/usr/bin/env python3
"""Run a short live LLM health check for configured targets.

The output intentionally redacts credentials and response text. This is a
preflight gate for eval launches, not an eval runner.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.reading_runtime.llm_registry import get_llm_registry  # noqa: E402


def _anthropic_messages_url(base_url: str | None) -> str:
    base = str(base_url or "").rstrip("/")
    if not base:
        raise ValueError("missing base_url")
    if base.endswith("/v1/messages"):
        return base
    if base.endswith("/v1"):
        return f"{base}/messages"
    return f"{base}/v1/messages"


def _check_target(provider: Any, *, timeout_seconds: int) -> dict[str, Any]:
    started = time.perf_counter()
    result: dict[str, Any] = {
        "target_id": provider.provider_id,
        "contract": provider.contract,
        "model": provider.supported_models[0] if provider.supported_models else "",
        "status": "failed",
    }
    if provider.contract != "anthropic":
        result["status"] = "skipped"
        result["reason"] = "unsupported_contract_for_live_preflight"
        return result
    key_pool = provider.resolved_key_pool()
    if not key_pool:
        result["error_type"] = "missing_credentials"
        return result

    body = {
        "model": result["model"],
        "max_tokens": 16,
        "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
    }
    request = urllib.request.Request(
        _anthropic_messages_url(provider.base_url),
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "accept": "application/json",
            "x-api-key": key_pool[0]["api_key"],
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            response.read(4096)
            result["status"] = "ok"
            result["http_status"] = response.status
    except urllib.error.HTTPError as exc:
        result["http_status"] = exc.code
        result["error_type"] = "http_error"
        result["error"] = str(exc)
    except TimeoutError as exc:
        result["error_type"] = "timeout"
        result["error"] = str(exc)
    except OSError as exc:
        result["error_type"] = exc.__class__.__name__
        result["error"] = str(exc)
    finally:
        result["elapsed_ms"] = int((time.perf_counter() - started) * 1000)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-id", action="append", default=None, help="Limit to one target id. Repeatable.")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    wanted = set(args.target_id or [])
    registry = get_llm_registry()
    providers = [
        provider
        for provider_id, provider in sorted(registry.providers.items())
        if not wanted or provider_id in wanted
    ]
    target_results = [
        _check_target(provider, timeout_seconds=max(1, int(args.timeout_seconds)))
        for provider in providers
    ]
    failed = [item for item in target_results if item.get("status") == "failed"]
    payload = {
        "status": "failed" if failed else "ok",
        "target_count": len(target_results),
        "failed_count": len(failed),
        "target_results": target_results,
    }
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
