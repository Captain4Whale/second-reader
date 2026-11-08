"""Read-only historical input reconstruction and isolated Digest invocation.

No Ingest, retrieval, Reading Runner, settlement or Product Store is imported.
Inputs are reconstructed evidence, not an observed historical request receipt.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

from src.prompts.integrity import canonical
from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_core.source_ranges import source_range_from_wire, validate_book_document_source_range
from src.attentional_v2.prompts.selection import render_selected_digest_prompt

BACKEND = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(Path(path).read_text())


def rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(canonical(value) + b"\n")


def wire_span(span):
    return {key: {k: int(span[name][k]) for k in ("chapter_id", "paragraph_index", "char_offset")}
            for key, name in (("start", "start_cursor"), ("end", "end_cursor"))}


def stamp(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


class HistoricalRun:
    def __init__(self, source_backend, run_id):
        self.run_id = run_id
        ledger = read(Path(source_backend) / "docs/evaluation/run_ledger.json")
        matches = [x for x in ledger["entries"] if x["run_id"] == run_id]
        if len(matches) != 1:
            raise ValueError(f"Missing/duplicate historical run: {run_id}")
        self.output = (Path(source_backend).parent / matches[0]["run_dir"] / "output").resolve()
        self.runtime = self.output / "_mechanisms/attentional_v2/runtime"
        self.spans = rows(self.runtime / "unit_span_ledger.jsonl")
        self.calls = rows(self.output / "_runtime/llm_standard.jsonl")
        self.selections = [x for x in rows(self.runtime / "unit_memory_retrieval_trace.jsonl")
                           if x.get("event_type") == "unit_memory_reading_memory_selection"]
        with sqlite3.connect((self.runtime / "unit_memory.sqlite").as_uri() + "?mode=ro&immutable=1", uri=True) as db:
            self.units = {uid: json.loads(value) for uid, value in db.execute(
                "SELECT unit_id, entry_json FROM unit_memory_entries")}
        self.by_span = {x["source_span_id"]: x for x in self.units.values()}
        if len(self.by_span) != len(self.units):
            raise ValueError("Ambiguous historical Unit Memory spans")
        self.audit = {x["source_span_id"]: x for x in rows(self.runtime / "read_audit.jsonl")}
        self.recent = {x["entry_id"]: x for x in read(self.runtime / "recent_reading_memory.json")["entries"]}
        self.document_path = self.output / "public/book_document.json"
        self.document = read(self.document_path)
        self.manifest = read(self.output / "_mechanisms/attentional_v2/internal/prompt_manifests/digest.json")
        xml = ET.fromstring("<root>" + self.manifest["user_prompt"] + "</root>")
        self.identity = json.loads("".join(xml.find("BookInfo").itertext()).strip())

    def reconstruct(self, unit_id):
        spans = [x for x in self.spans if x["unit_id"] == unit_id]
        if len(spans) != 1 or unit_id not in self.units:
            raise ValueError(f"Missing/ambiguous accepted unit: {self.run_id}/{unit_id}")
        span = spans[0]
        entry = self.units[unit_id]
        source = deepcopy(entry["accepted_source_unit"])
        source_coordinates = wire_span(source["source_span"])
        ledger_coordinates = wire_span(span)
        start, end = source_coordinates["start"], source_coordinates["end"]
        expected_span_id = (f"src:c{start['chapter_id']}:p{start['paragraph_index']}@{start['char_offset']}"
                            f"-p{end['paragraph_index']}@{end['char_offset']}")
        if (source["source_span_id"] != span["source_span_id"]
                or source["source_span_id"] != expected_span_id
                or source_coordinates != ledger_coordinates
                or start["chapter_id"] != end["chapter_id"]):
            raise ValueError(f"Unit source mismatch: {unit_id}")
        validate_book_document_source_range(self.document, source_range_from_wire(wire_span(source["source_span"])),
                                           expected_quote=source["source_text"], require_single_resource=False)
        accepted_calls = [x for x in self.calls if x["node"] == "digest" and x["status"] == "ok"
                          and x["correlation"].get("unit_id") == unit_id
                          and stamp(x["completed_at"]) <= stamp(span["created_at"])]
        if not accepted_calls:
            raise ValueError(f"Accepted Digest call not found: {unit_id}")
        call = max(accepted_calls, key=lambda x: stamp(x["completed_at"]))
        selections = [x for x in self.selections if x["source_span_id"] == span["source_span_id"]
                      and stamp(x["recorded_at"]) <= stamp(call["started_at"])]
        if not selections:
            raise ValueError(f"ReadingMemory selection missing: {unit_id}")
        selection = max(selections, key=lambda x: stamp(x["recorded_at"]))
        records = [*selection["rendered_hot_units"], *selection["rendered_retrieved_units"]]
        records.sort(key=lambda x: int(x["unit_index"]), reverse=True)
        lines, evidence = [], []
        for record in records:
            previous = self.by_span[record["source_span_id"]]
            text = previous["digest"]["understanding"]["content"].strip()
            if not text or previous["unit_index"] >= span["sequence_index"]:
                raise ValueError(f"Empty/future historical memory: {unit_id}")
            if record["origin"] == "retrieved" and previous["unit_id"] != record["unit_id"]:
                raise ValueError("Retrieved memory identity mismatch")
            if int(previous["unit_index"]) != int(record["unit_index"]):
                raise ValueError("Historical memory order mismatch")
            if self.audit[record["source_span_id"]]["understanding"].strip() != text:
                raise ValueError("Historical memory/audit text mismatch")
            if record["origin"] == "hot" and record["unit_id"] in self.recent:
                if self.recent[record["unit_id"]]["memory_text"].strip() != text:
                    raise ValueError("Historical recent-memory text mismatch")
            paragraph = int(re.search(r":p(\d+)@", record["source_span_id"])[1])
            lines.append(f"P{paragraph} U{record['unit_index']}: {text}")
            evidence.append({**record, "text_sha256": sha(text.encode())})
        if len(lines) != selection["line_count"]:
            raise ValueError("Historical ReadingMemory line count mismatch")
        chapter = next(x for x in self.document["chapters"] if x["id"] == span["chapter_id"])
        packet = {
            "schema": "fixed-history-digest-input/1", "reconstructed": True,
            "original_run_id": self.run_id, "unit_id": unit_id,
            "source_span_id": span["source_span_id"], "current_unit_source": source,
            "book_title": self.identity["book_title"], "author": self.identity["author"],
            "chapter_title": chapter["title"], "output_language": "zh",
            "label_provenance": {
                "unit_memory_chapter_ref": entry.get("chapter_ref"),
                "unit_memory_cursor_refs": {k: source["source_span"][k].get("chapter_ref")
                                            for k in ("start_cursor", "end_cursor")},
                "ledger_chapter_ref": span.get("chapter_ref"),
                "ledger_cursor_refs": {k: span[k].get("chapter_ref") for k in ("start_cursor", "end_cursor")},
                "prompt_chapter_title": chapter["title"],
                "chapter_ref_is_prompt_input": False,
                "prompt_title_basis": "Historical runner passes chapter.title; Digest renderer never reads cursor.chapter_ref.",
                "historical_code_commit": call["code_commit"],
            },
            "reading_memory_lines": lines, "memory_evidence": evidence,
            "selection_recorded_at": selection["recorded_at"],
            "accepted_call": {k: call[k] for k in ("call_id", "started_at", "completed_at", "model", "sampling", "prompt_version", "code_commit", "code_dirty")},
            "original_source_range": wire_span(source["source_span"]),
            "substrate_sha256": book_document_substrate_digest(self.document),
            "historical_result": self.audit[span["source_span_id"]]["digest_result"],
            "limitations": ["No observed historical request hash or complete retry/repair body.",
                            "Memory text reconstructed from retained historical Understanding by selected span."],
        }
        packet["memory_selection_check"] = self.verify_memory_selection(packet)
        return packet

    def verify_memory_selection(self, packet):
        """Check a serialized packet independently against the historical trace/audit.

        Trace arrays retain their per-origin order. The historical runner merges
        hot + retrieved records by descending unit_index (stable sort), without
        adding chapter labels. Check actual line text as well as every ID/order.
        """
        selections = [x for x in self.selections
                      if x["source_span_id"] == packet["source_span_id"]
                      and stamp(x["recorded_at"]) <= stamp(packet["accepted_call"]["started_at"])]
        if not selections:
            raise ValueError("Memory selection verification: missing original trace")
        trace = max(selections, key=lambda x: stamp(x["recorded_at"]))
        actual = packet["memory_evidence"]
        identities = lambda records: [(x["origin"], x["unit_id"], x["source_span_id"], int(x["unit_index"])) for x in records]
        original = []
        for origin, field in (("hot", "rendered_hot_units"), ("retrieved", "rendered_retrieved_units")):
            expected = trace[field]
            if any(x["origin"] != origin for x in expected):
                raise ValueError("Memory selection verification: trace origin mismatch")
            if identities([x for x in actual if x["origin"] == origin]) != identities(expected):
                raise ValueError(f"Memory selection verification: {origin} IDs/order mismatch")
            original.extend(expected)
        original.sort(key=lambda x: int(x["unit_index"]), reverse=True)
        if identities(actual) != identities(original) or len(actual) != trace["line_count"]:
            raise ValueError("Memory selection verification: merged IDs/order mismatch")
        if packet["selection_recorded_at"] != trace["recorded_at"]:
            raise ValueError("Memory selection verification: attempt/trace mismatch")
        expected_lines, label_findings = [], []
        label_pattern = re.compile(r"\bChapter\s+(?:\d+|[IVXLCDM]+)\b|第[零〇一二三四五六七八九十百千万两0-9]+[章节卷部篇]", re.I)
        for record in original:
            # Audit is the original settled model Understanding, not a freshly
            # rendered or renamed value from the later reconciled memory DB.
            body = self.audit[record["source_span_id"]]["understanding"].strip()
            paragraph = int(re.search(r":p(\d+)@", record["source_span_id"])[1])
            expected_lines.append(f"P{paragraph} U{record['unit_index']}: {body}")
            labels = label_pattern.findall(body)
            if labels:
                label_findings.append({"unit_id": record["unit_id"], "labels": labels,
                                       "body_sha256": sha(body.encode()), "matches_original_audit": True})
        if packet["reading_memory_lines"] != expected_lines:
            raise ValueError("Memory selection verification: body/label text mismatch")
        return {"status": "matched", "trace_recorded_at": trace["recorded_at"],
                "ordered_ids": [x["unit_id"] for x in original],
                "hot_ids": [x["unit_id"] for x in trace["rendered_hot_units"]],
                "retrieved_ids": [x["unit_id"] for x in trace["rendered_retrieved_units"]],
                "id_and_order_equal": True, "complete_line_text_equal": True,
                "body_labels": label_findings,
                "label_scan": "Chapter N/Roman or 第…章/节/卷/部/篇; all body text is checked verbatim regardless of matches",
                "render_order_basis": "historical runner hot+retrieved stable descending unit_index"}

    def check_manifest(self):
        packet = self.reconstruct(self.spans[-1]["unit_id"])
        system, user = render_packet(packet, self.manifest["prompt_version"])
        if system != self.manifest["system_prompt"] or user != self.manifest["user_prompt"]:
            raise ValueError(f"Historical manifest byte mismatch: {self.run_id}")
        return {"run_id": self.run_id, "unit_id": packet["unit_id"], "system_equal": True,
                "user_equal": True, "user_sha256": sha(user.encode())}


def render_packet(packet, version):
    from src.iterator_reader.language import language_name
    system, assembly = render_selected_digest_prompt(version,
        book_title=packet["book_title"], author=packet["author"], chapter_title=packet["chapter_title"],
        output_language_name=language_name(packet["output_language"]),
        reading_memory_lines=packet["reading_memory_lines"], current_unit_source=packet["current_unit_source"])
    return system, assembly.rendered_text


def configure_model(operator_backend, model, effort, sampling, target_id="cpa_codex_local"):
    """Isolated in-process config; credentials remain environment references."""
    from dotenv import load_dotenv
    load_dotenv(Path(operator_backend) / ".env")
    # Provider quota/dispatch state belongs to this checkout, never to linked inputs.
    os.environ["BACKEND_RUNTIME_ROOT"] = str(BACKEND)
    targets = read(Path(operator_backend) / "config/llm_targets.local.json")
    bindings = read(Path(operator_backend) / "config/llm_profile_bindings.local.json")
    target = next(x for x in targets["targets"] if x["target_id"] == target_id)
    for credential in target.get("credentials", []):
        if credential.get("api_key") or not credential.get("api_key_env"):
            raise ValueError("Only environment-backed credentials are supported")
    target.update(model=model, provider_options={**target.get("provider_options", {}), "reasoning_effort": effort})
    profile = next(x for x in bindings["profiles"] if x["profile_id"] == "runtime_reader_default")
    profile.update(temperature=sampling["temperature"], max_output_tokens=sampling["max_output_tokens"],
                   target_tiers=[{"tier_id": "primary", "target_ids": [target_id], "min_required_stable_concurrency": 1}],
                   max_concurrency=1, default_burst_concurrency=1)
    os.environ["LLM_TARGETS_JSON"] = json.dumps({"targets": [target]})
    os.environ["LLM_PROFILE_BINDINGS_JSON"] = json.dumps({"profiles": [
        {**profile, "profile_id": name} for name in ("runtime_reader_default", "dataset_review_high_trust", "eval_judge_high_trust")]})
    from src.reading_runtime.llm_registry import clear_llm_registry_cache
    clear_llm_registry_cache()


class CaptureAdapter:
    def __init__(self, delegate, directory):
        self.delegate, self.directory = delegate, directory
        self.hashes, self.payloads, self.response_usages = [], [], []

    def invoke(self, messages, **kwargs):
        # The diagnostic preserves the historical forced-tool transport.
        if not kwargs.get("tools"):
            raise ValueError("Fixed-history diagnostic requires the historical tool transport")
        normalized = []
        for m in messages:
            item = {"role": m.type, "content": m.content}
            for k in ("tool_calls", "tool_call_id", "name"):
                if getattr(m, k, None):
                    item[k] = getattr(m, k)
            for k in ("tool_calls", "function_call"):
                if k in m.additional_kwargs and k not in item:
                    item[k] = m.additional_kwargs[k]
            normalized.append(item)
        request = {"schema": "logical-model-request/1", "messages": normalized,
                   "tools": kwargs["tools"], "tool_choice": kwargs.get("tool_choice"), "expect_json": False}
        self.hashes.append(sha(canonical(request)))
        number = len(self.hashes)
        write(self.directory / f"request-{number:03d}.json", request)
        response = self.delegate.invoke(messages, **kwargs)
        from src.reading_runtime.llm_usage import normalize_provider_usage

        self.response_usages.append(normalize_provider_usage(response).to_dict())
        write(self.directory / f"response-{number:03d}.json", {
            "content": response.content, "tool_calls": response.tool_calls,
            "invalid_tool_calls": response.invalid_tool_calls, "usage_metadata": response.usage_metadata,
            "finish_reason": response.response_metadata.get("finish_reason"),
            "model_name": response.response_metadata.get("model_name"),
        })
        self.payloads.append(response.tool_calls[-1]["args"] if response.tool_calls else None)
        return response


def run_digest(packet, directory, *, model, effort, prompt_version, operator_backend):
    """Run only Digest; never apply its returned memory operations."""
    from src.attentional_v2.llm_calls import digest
    from src.reading_runtime.llm_gateway import CONTRACT_ADAPTERS, llm_invocation_scope, runtime_trace_context
    from src.reading_runtime.run_provenance import provenance_scope
    from src.reading_runtime.observation_context import run_observation_scope
    from src.prompts.integrity import LOCK, release_receipt
    directory = Path(directory).resolve()
    if not directory.is_relative_to((BACKEND / "state").resolve()):
        raise ValueError("Replay outputs must be inside this worktree's ignored backend/state")
    directory.mkdir(parents=True, exist_ok=False)
    write(directory / "input.json", packet)
    system, user = render_packet(packet, prompt_version)
    write(directory / "rendered.json", {"system_prompt": system, "user_prompt": user, "reconstructed": True})
    configure_model(operator_backend, model, effort, packet["accepted_call"]["sampling"])
    originals = dict(CONTRACT_ADAPTERS)
    captures = {k: CaptureAdapter(v, directory / "actual") for k, v in originals.items()}
    CONTRACT_ADAPTERS.update(captures)
    try:
        with run_observation_scope(
            directory, f"fixed-history-digest-{packet['unit_id']}",
            run_id=f"fixed-history-{directory.parent.name}-{packet['unit_id']}",
            mechanism_key="attentional_v2", job_kind="offline_digest_replay",
        ), provenance_scope(directory, stage="fixed_history_digest") as provenance:
            context = runtime_trace_context(directory, mechanism_key="attentional_v2", node="digest", extra={
                "original_run_id": packet["original_run_id"], "unit_id": packet["unit_id"], "reconstructed": True})
            with llm_invocation_scope(profile_id="runtime_reader_default", trace_context=context):
                result = digest(carry_forward_context={}, output_language=packet["output_language"],
                    current_unit_source=packet["current_unit_source"], reading_memory_lines=packet["reading_memory_lines"],
                    book_title=packet["book_title"], author=packet["author"], chapter_title=packet["chapter_title"],
                    prompt_version=prompt_version, output_dir=directory)
            trace = rows(directory / "_runtime/llm_standard.jsonl")
            capture = next(x for x in captures.values() if x.hashes)
            logical_hashes = [x["request_sha256"] for x in trace]
            if set(logical_hashes) != set(capture.hashes) or logical_hashes[-1] != capture.hashes[-1]:
                raise ValueError("Captured requests differ from gateway request receipts")
            raw_marks = capture.payloads[-1].get("marginalia", [])
            if len(raw_marks) != len(result["marginalia"]):
                raise ValueError("Digest normalization removed marks; refusing partial output")
            for raw, normalized in zip(raw_marks, result["marginalia"]):
                if raw["source_quote"].strip() != normalized["source_quote"]:
                    raise ValueError("Digest normalization changed a source anchor")
            discarded = len(result.pop("memory_uptake_ops", []))
            result.pop("memory_uptake_admission_events", None)
            output = {"schema": "fixed-history-digest-result/1", "reconstructed": True,
                      "original_run_id": packet["original_run_id"], "unit_id": packet["unit_id"],
                      "model": model, "reasoning_effort": effort, "prompt_version": prompt_version,
                      "prompt": release_receipt(read(LOCK)["releases"][prompt_version]),
                      "input_sha256": sha(canonical(packet)), "request_sha256": trace[-1]["request_sha256"],
                      "sampling": trace[-1]["sampling"], "code_commit": trace[-1]["code_commit"],
                      "code_dirty": trace[-1]["code_dirty"], "calls": trace, "result": result,
                      "response_usages": capture.response_usages,
                      "physical_request_count": len(capture.hashes),
                      "discarded_memory_operation_count": discarded,
                      "provenance_invocation_id": provenance["invocation_id"]}
            write(directory / "result.json", output)
            return output
    except Exception as exc:
        write(directory / "failed.json", {"reconstructed": True, "error_type": type(exc).__name__, "message": str(exc)})
        raise
    finally:
        CONTRACT_ADAPTERS.update(originals)
