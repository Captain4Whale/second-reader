#!/usr/bin/env python3
"""Check local readiness for attentional_v2 Unit Memory hybrid retrieval."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.attentional_v2.unit_memory import DEFAULT_RETRIEVAL_CONFIG  # noqa: E402


def _json_dumps(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def _load_sqlite_vec() -> dict[str, object]:
    result: dict[str, object] = {
        "import_ok": False,
        "load_ok": False,
        "vec0_table_ok": False,
        "version": "",
        "error": "",
    }
    try:
        import sqlite_vec  # type: ignore[import-not-found]

        result["import_ok"] = True
        result["version"] = str(getattr(sqlite_vec, "__version__", "") or "")
        connection = sqlite3.connect(":memory:")
        try:
            connection.enable_load_extension(True)
            sqlite_vec.load(connection)
            connection.enable_load_extension(False)
            result["load_ok"] = True
            connection.execute("CREATE VIRTUAL TABLE vec_probe USING vec0(embedding float[3] distance_metric=cosine)")
            result["vec0_table_ok"] = True
        finally:
            connection.close()
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def _fetch_json(url: str, *, timeout_seconds: float, payload: dict[str, object] | None = None) -> dict[str, object]:
    data = None
    method = "GET"
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        method = "POST"
        headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        value = json.loads(response.read().decode("utf-8"))
    return value if isinstance(value, dict) else {"value": value}


def _model_names(tags_payload: dict[str, object]) -> list[str]:
    names: list[str] = []
    models = tags_payload.get("models")
    if not isinstance(models, list):
        return names
    for item in models:
        if not isinstance(item, dict):
            continue
        for key in ("name", "model"):
            value = str(item.get(key) or "").strip()
            if value and value not in names:
                names.append(value)
    return names


def _embedding_from_payload(payload: dict[str, object]) -> list[float]:
    embeddings = payload.get("embeddings")
    if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
        return [float(item) for item in embeddings[0]]
    embedding = payload.get("embedding")
    if isinstance(embedding, list):
        return [float(item) for item in embedding]
    return []


def probe_hybrid_readiness(
    *,
    base_url: str,
    model_id: str,
    expected_dimension: int,
    timeout_ms: int,
    sample_text: str = "Unit Memory hybrid readiness probe.",
) -> dict[str, object]:
    """Return a machine-readable readiness summary without starting services."""

    timeout_seconds = max(0.05, timeout_ms / 1000)
    sqlite_vec = _load_sqlite_vec()
    ollama: dict[str, object] = {
        "base_url": base_url.rstrip("/"),
        "reachable": False,
        "model_id": model_id,
        "model_available": False,
        "models": [],
        "error": "",
    }
    embedding: dict[str, object] = {
        "checked": False,
        "ok": False,
        "dimension": 0,
        "expected_dimension": expected_dimension,
        "error": "",
    }

    try:
        tags = _fetch_json(f"{base_url.rstrip('/')}/api/tags", timeout_seconds=timeout_seconds)
        ollama["reachable"] = True
        names = _model_names(tags)
        ollama["models"] = names
        ollama["model_available"] = model_id in names
    except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError) as exc:
        ollama["error"] = f"{type(exc).__name__}: {exc}"

    if ollama["reachable"] and ollama["model_available"]:
        embedding["checked"] = True
        try:
            payload = _fetch_json(
                f"{base_url.rstrip('/')}/api/embed",
                timeout_seconds=timeout_seconds,
                payload={"model": model_id, "input": sample_text},
            )
            vector = _embedding_from_payload(payload)
            embedding["dimension"] = len(vector)
            embedding["ok"] = len(vector) == expected_dimension
            if not embedding["ok"]:
                embedding["error"] = f"embedding_dimension_mismatch:{len(vector)}"
        except (OSError, TimeoutError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
            embedding["error"] = f"{type(exc).__name__}: {exc}"

    blocking_reasons: list[str] = []
    if not sqlite_vec["vec0_table_ok"]:
        blocking_reasons.append("sqlite_vec_unavailable")
    if not ollama["reachable"]:
        blocking_reasons.append("ollama_unreachable")
    elif not ollama["model_available"]:
        blocking_reasons.append("ollama_model_missing")
    elif not embedding["ok"]:
        blocking_reasons.append(str(embedding["error"] or "embedding_probe_failed"))

    return {
        "status": "ok" if not blocking_reasons else "blocked",
        "mode": "hybrid",
        "sqlite_vec": sqlite_vec,
        "ollama": ollama,
        "embedding": embedding,
        "blocking_reasons": blocking_reasons,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model-id", default=str(DEFAULT_RETRIEVAL_CONFIG["ollama_model_id"]))
    parser.add_argument("--expected-dimension", type=int, default=int(DEFAULT_RETRIEVAL_CONFIG["embedding_dimension"]))
    parser.add_argument("--timeout-ms", type=int, default=int(DEFAULT_RETRIEVAL_CONFIG["query_embedding_timeout_ms"]))
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when hybrid readiness is blocked.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = probe_hybrid_readiness(
        base_url=str(args.base_url),
        model_id=str(args.model_id),
        expected_dimension=int(args.expected_dimension),
        timeout_ms=int(args.timeout_ms),
    )
    print(_json_dumps(summary))
    return 1 if args.strict and summary["status"] != "ok" else 0


if __name__ == "__main__":
    raise SystemExit(main())
