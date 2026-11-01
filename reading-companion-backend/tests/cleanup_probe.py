"""Offline before/after evidence for the approved lightweight cleanup.

Run with ``python -m tests.cleanup_probe --output PATH`` from the backend.
Only the provider transport is substituted in the product probe. The normal
gateway writes its real accounting ledger. No socket may connect externally.
"""

from __future__ import annotations

import argparse
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

import pytest

from eval.attentional_v2 import run_user_level_selective_comparison as matching
from src.attentional_v2 import llm_calls, product_output, runner
from src.reading_core.runtime_contracts import ParseRequest, ReadRequest
from src.reading_mechanisms.attentional_v2 import AttentionalV2Mechanism
from src.reading_product import store
from src.reading_product.serialization import document_to_wire
from src.reading_runtime.llm_gateway import CONTRACT_ADAPTERS, clear_llm_gateway_runtime_state
from src.reading_runtime.llm_registry import clear_llm_registry_cache
from tests.reading_product.test_offline_whole_book_lifecycle import (
    TINY_READER_EPUB,
    _deterministic_digest_factory,
    _deterministic_ingest,
    _export_pack,
    _load_complete_product,
)
from tests.test_run_user_level_selective_comparison import _mechanism_payload, _note_case, _slice
from tests.test_runtime_observability_e2e import _UsageResponse, _configure_priced_runtime_target


FIXED_TIME = datetime(2026, 11, 1, tzinfo=timezone.utc)


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_TIME


def forbid_connection(*args, **kwargs):
    raise AssertionError("cleanup probe forbids network connections")


class ReadingAdapter:
    def __init__(self):
        self.pending_ingest = {}
        self.pending_digest = {}
        self.prompts = []

    def invoke(self, messages, *, provider, profile, api_key, timeout_seconds,
               tools=None, tool_choice=None, invocation_options=None):
        name = next(t["name"] for t in tools if t["name"].startswith("submit_"))
        if name == "submit_ingest_result":
            payload = self.pending_ingest
            node = "ingest"
        elif name == "submit_digest_result":
            payload = self.pending_digest
            node = "digest"
        elif name == "submit_survey_chapter_zone_result":
            payload = {"zone": "main_body", "confidence": "high", "reason": "Offline fixture body."}
            node = "survey"
        elif name == "submit_chapter_consolidation_result":
            payload = {"chapter_ref": "fixture", "promotion_candidates": [], "cross_chapter_carry_forward": []}
            node = "chapter_consolidation"
        else:
            raise AssertionError(f"unexpected model node: {name}")
        if node in {"ingest", "digest"}:
            self.prompts.append({"node": node, "messages": [str(m.content) for m in messages]})
        return _UsageResponse(
            content="", usage_metadata={"input_tokens": 100, "output_tokens": 20, "total_tokens": 120},
            response_metadata={"model_provider": "openai", "finish_reason": "tool_calls"},
            tool_calls=[{"id": "fixture-submit", "name": name, "args": payload}],
        )


def matching_probe(root, patch):
    patch.setattr(matching, "llm_invocation_scope", lambda **kw: __import__("contextlib").nullcontext())
    judgments = []

    def fixed_judge(system, prompt, default, **kwargs):
        judgments.append(prompt)
        return {"label": "focused_hit", "confidence": "high", "reason": "fixed judge response"}

    patch.setattr(matching, "invoke_json", fixed_judge)
    rows = []
    for end in (17, 25, 8):
        note = _note_case(source_span_text="Alpha hinge line.", span=_slice(end=end))
        rows.append(matching.evaluate_note_case_for_mechanism(
            note_case=note, mechanism_payload=_mechanism_payload("Alpha hinge line."),
            mechanism_key="attentional_v2", run_root=root,
            judge_mode="llm",
        ))
    assert judgments, "probe must exercise the fixed judge, not only exact matches"
    return {"rows": rows, "judge_prompts": judgments}


def product_probe(root, patch):
    patch.chdir(root)
    _configure_priced_runtime_target(patch)
    patch.setenv("BACKEND_RUNTIME_ROOT", str(root))
    patch.setattr(store, "uuid4", lambda: UUID("11111111-1111-4111-8111-111111111111"))
    real_utc = store.utc_seconds
    patch.setattr(store, "utc_seconds", lambda value=None: real_utc(FIXED_TIME if value is None else value))
    patch.setattr(product_output, "datetime", FixedDateTime)
    adapter = ReadingAdapter()
    patch.setitem(CONTRACT_ADAPTERS, "openai_compatible", adapter)
    real_ingest, real_digest = llm_calls.ingest, llm_calls.digest
    fixed_digest = _deterministic_digest_factory([])

    def ingest(**kwargs):
        adapter.pending_ingest = _deterministic_ingest(**kwargs)
        return real_ingest(**kwargs)

    def digest(**kwargs):
        result = fixed_digest(**kwargs)
        for item in result["marginalia"]:
            if item["kind"] == "highlight":
                item["selection_reason"] = "A self-contained durable phrase in this fixture."
        # The malformed-source candidate is covered by the separate admission test.
        result["marginalia"] = [m for m in result["marginalia"] if m["source_quote"] != "text absent from the EPUB"]
        adapter.pending_digest = {"understanding": result["understanding"],
                                  "response": result["reading_impression"],
                                  "marginalia": result["marginalia"]}
        return real_digest(**kwargs)

    patch.setattr(runner, "_call_ingest", ingest)
    patch.setattr(runner, "_call_digest", digest)
    mechanism = AttentionalV2Mechanism()
    mechanism.parse_book(ParseRequest(book_path=TINY_READER_EPUB, mechanism_key="attentional_v2"))
    result = mechanism.read_book(ReadRequest(book_path=TINY_READER_EPUB, mechanism_key="attentional_v2",
                                            mechanism_config={"memory_retrieval_mode": "text_only"}))
    output_dir = result.output_dir.resolve()
    product = _load_complete_product(output_dir)
    assert product.status == "complete" and any(u.marginalia for u in product.units)
    pack = _export_pack(output_dir, output_dir.parent, root)
    assert pack.validation.publishable
    ledger = [json.loads(l) for l in (output_dir / "_runtime/llm_standard.jsonl").read_text().splitlines()]
    assert ledger and all(row["status"] == "ok" for row in ledger)
    return {"prompts": adapter.prompts, "product": document_to_wire(product),
            "pack": json.loads(pack.annotations_json.read_text()),
            "ledger_nodes": [row["node"] for row in ledger]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--without-slow-cycle", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    baseline = json.loads(args.baseline.read_text()) if args.baseline else None
    with TemporaryDirectory(prefix="cleanup-probe-") as temp, pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket.socket, "connect", forbid_connection)
        root = Path(temp)
        evidence = {"matching": matching_probe(root, patch), "product": product_probe(root, patch)}
    clear_llm_gateway_runtime_state()
    clear_llm_registry_cache()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    if baseline:
        assert evidence["matching"] == baseline["matching"], "STOP: matching changed"
        for key in ("prompts", "product", "pack"):
            assert evidence["product"][key] == baseline["product"][key], f"STOP: {key} changed"
    if args.without_slow_cycle:
        assert not {"chapter_consolidation", "reflective_promotion"}.intersection(evidence["product"]["ledger_nodes"])
    print("offline cleanup probe passed; matching, core prompts, Product and Pack captured")


if __name__ == "__main__":
    main()
