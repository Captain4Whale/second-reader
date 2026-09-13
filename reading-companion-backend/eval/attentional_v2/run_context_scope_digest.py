"""Frozen A/B/C Xidaduo diagnostic: three serial requests, stop on any failure."""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from . import run_whole_book_digest as single
from .whole_book_digest_artifacts import (
    review_payload,
    render_review,
    render_historical_reference,
)

RUN_ID = "xidaduo_context_scope_digest_20260913"
JOB_ID = f"bgjob_{RUN_ID}"
DEFAULT_RUN_DIR = single.BACKEND_ROOT / "state/experiments" / RUN_ID
BASELINE_RUN = single.DEFAULT_RUN_DIR
CHAPTER_ID = 8
CHAPTER_HASH = "73d55d4e1f94503f90ec4abc661996cf79f906609dfdfced003a88511b75a93d"
CONDITIONS = ("A", "B", "C")
FIXED_TAGS = ("ReaderRole", "Instruction", "BookInfo", "OutputContract")
BACKGROUND_TAGS = ("SourceContextBefore", "SourceContextAfter")
SCOPE_INSTRUCTION = (
    "For this request, 'this unit' means only the text inside SourceUnit: the chapter 迦摩罗. "
    "Understanding, Response, and Marginalia must all concern this target chapter. "
    "SourceContextBefore and SourceContextAfter, when present, contain original book text "
    "provided only as optional background for understanding the target chapter. "
    "Do not annotate the background. Every Marginalia source_quote must be an exact "
    "contiguous span inside SourceUnit. Apply the existing reading and annotation criteria."
)


def xml_text(root: ET.Element) -> str:
    return (root.text or "") + "".join(
        ET.tostring(child, encoding="unicode") for child in root
    )


def paragraph_text(root: ET.Element) -> str:
    return "\n\n".join((p.text or "").strip() for p in root.findall(".//Paragraph"))


def chapter_source(full: dict, chapter_id: int = CHAPTER_ID) -> dict:
    paragraphs = []
    offset = 0
    for item in full["paragraphs"]:
        if item["chapter_id"] != chapter_id:
            continue
        paragraph = {**item, "start": offset, "end": offset + len(item["text"])}
        paragraphs.append(paragraph)
        offset = paragraph["end"] + 2
    if not paragraphs:
        raise ValueError("Target chapter is absent")
    return {
        "source_text": "\n\n".join(p["text"] for p in paragraphs),
        "paragraphs": paragraphs,
        "paragraph_slices": [
            {"paragraph_index": p["global_paragraph_index"], "text": p["text"]}
            for p in paragraphs
        ],
    }


def build_chapter_packet(
    baseline_packet: dict, full: dict, target: dict, background: bool
) -> dict:
    old = single.xml_root(baseline_packet["user_prompt"])
    identity = json.loads("".join(old.find("BookInfo").itertext()).strip())
    assembly = single.render_digest_prompt_xml(
        book_title=identity["book_title"],
        author=identity["author"],
        chapter_title="迦摩罗",
        output_language_name="Chinese",
        reading_memory_lines=[],
        current_unit_source=target,
    )
    root = single.xml_root(assembly.rendered_text)
    obj = root.find("./CurrentFocus/ReadingObject")
    before = ET.Element(BACKGROUND_TAGS[0])
    after = ET.Element(BACKGROUND_TAGS[1])
    first = target["paragraphs"][0]["global_paragraph_index"]
    last = target["paragraphs"][-1]["global_paragraph_index"]
    if background:
        for p in full["paragraphs"]:
            index = p["global_paragraph_index"]
            container = before if index < first else after if index > last else None
            if container is not None:
                ET.SubElement(container, "Paragraph", {"n": str(index)}).text = p[
                    "text"
                ]
    obj.insert(0, before)
    obj.append(after)
    intent = root.find("./CurrentFocus/ReadingIntent")
    intent.text = json.dumps(
        {
            "intent": "read_current_source_unit_in_sequence",
            "scope_instruction": SCOPE_INSTRUCTION,
        },
        ensure_ascii=False,
    )
    # Retain the exact established instruction/identity/output blocks even though
    # the experimental CurrentFocus adds optional source background containers.
    for tag in FIXED_TAGS:
        index = list(root).index(root.find(tag))
        root.remove(root.find(tag))
        root.insert(index, copy.deepcopy(old.find(tag)))
    return {**copy.deepcopy(baseline_packet), "user_prompt": xml_text(root)}


def verify_pair(b: dict, c: dict, full: dict, target: dict) -> None:
    br, cr = (single.xml_root(p["user_prompt"]) for p in (b, c))
    if (
        paragraph_text(br) != full["source_text"]
        or paragraph_text(cr) != target["source_text"]
    ):
        raise ValueError("Source text truncated, duplicated, or reordered")
    for root in (br, cr):
        if (
            paragraph_text(root.find("./CurrentFocus/ReadingObject/SourceUnit"))
            != target["source_text"]
        ):
            raise ValueError("Target unit drift")
        if (root.findtext("ReadingMemory") or "").strip():
            raise ValueError("ReadingMemory must be empty")
        for tag in BACKGROUND_TAGS:
            root.find(f"./CurrentFocus/ReadingObject/{tag}").clear()
    if xml_text(br) != xml_text(cr):
        raise ValueError("B/C differ outside the extra source background")
    if b["system_prompt"] != c["system_prompt"] or b["output_tool"] != c["output_tool"]:
        raise ValueError("B/C instruction or output tool drift")


def prepare(run_dir: Path) -> dict:
    single.verify_prepared(BASELINE_RUN)
    full = single.read_json(BASELINE_RUN / "source.json")
    target = chapter_source(full)
    if (
        len(target["paragraphs"]) != 86
        or len(target["source_text"]) != 7044
        or single.digest_bytes(target["source_text"].encode()) != CHAPTER_HASH
    ):
        raise ValueError("Target chapter differs from approved coordinates")
    packet = single.read_json(BASELINE_RUN / "prompt.json")
    previous_request = single.read_json(BASELINE_RUN / "request.json")
    if previous_request["messages"] != [
        {"role": "system", "content": packet["system_prompt"]},
        {"role": "human", "content": packet["user_prompt"]},
    ] or previous_request["tools"] != [packet["output_tool"]]:
        raise ValueError("Baseline prompt does not reproduce its actual request")
    packets = {
        "A": packet,
        "B": build_chapter_packet(packet, full, target, True),
        "C": build_chapter_packet(packet, full, target, False),
    }
    verify_pair(packets["B"], packets["C"], full, target)
    original = single.xml_root(packet["user_prompt"])
    for condition, candidate in packets.items():
        root = single.xml_root(candidate["user_prompt"])
        if any(
            ET.tostring(root.find(tag)) != ET.tostring(original.find(tag))
            for tag in FIXED_TAGS
        ):
            raise ValueError(f"Fixed instruction drift: {condition}")
    run_dir.mkdir(parents=True, exist_ok=False)
    single.write_json(run_dir / "full-source.json", full)
    single.write_json(run_dir / "target-source.json", target)
    (run_dir / "target-source.md").write_text(
        "# 《迦摩罗》原文\n\n"
        + "\n\n".join(
            f"〔段落 {p['paragraph_index']}〕\n\n{p['text']}"
            for p in target["paragraphs"]
        )
        + "\n"
    )
    historical = copy.deepcopy(full)
    historical["historical_product"]["units"] = [
        u
        for u in historical["historical_product"]["units"]
        if any(
            m["source_range"]["start"]["chapter_id"] == CHAPTER_ID
            for m in u["marginalia"]
        )
    ]
    for unit in historical["historical_product"]["units"]:
        unit["marginalia"] = [
            m
            for m in unit["marginalia"]
            if m["source_range"]["start"]["chapter_id"] == CHAPTER_ID
        ]
    if (
        sum(len(u["marginalia"]) for u in historical["historical_product"]["units"])
        != 25
    ):
        raise ValueError("Historical chapter reference drift")
    (run_dir / "historical-reference.md").write_text(
        render_historical_reference(historical)
    )
    single.write_json(run_dir / "historical-chapter.json", historical)
    old_manifest = single.read_json(BASELINE_RUN / "manifest.json")
    for condition in CONDITIONS:
        path = run_dir / condition
        path.mkdir()
        source = full if condition == "A" else target
        for name, value in {
            "source.json": source,
            "prompt.json": packets[condition],
        }.items():
            single.write_json(path / name, value)
        (path / "prompt.xml").write_text(packets[condition]["user_prompt"])
        for name in ("targets.local.json", "bindings.local.json"):
            (path / name).write_bytes((BASELINE_RUN / name).read_bytes())
        hashes = {
            name: single.digest_bytes((path / name).read_bytes())
            for name in (
                "source.json",
                "prompt.json",
                "prompt.xml",
                "targets.local.json",
                "bindings.local.json",
            )
        }
        manifest = {
            k: v
            for k, v in old_manifest.items()
            if k
            not in {
                "artifact_hashes",
                "source_metrics",
                "runner_sha256",
                "baseline_prompt_manifest_sha256",
            }
        }
        manifest.update(
            run_id=f"{RUN_ID}_{condition.lower()}",
            job_id=JOB_ID,
            condition=condition,
            status="prepared",
            prepared_at=single.now(),
            source_sha256=single.digest_bytes(source["source_text"].encode()),
            paragraph_count=len(source["paragraphs"]),
            source_characters=len(source["source_text"]),
            input_source_sha256=(
                single.SOURCE_HASH if condition != "C" else CHAPTER_HASH
            ),
            target_chapter_sha256=CHAPTER_HASH,
            artifact_hashes=hashes,
        )
        single.write_json(path / "manifest.json", manifest)
    manifest = {
        "run_id": RUN_ID,
        "job_id": JOB_ID,
        "status": "prepared",
        "prepared_at": single.now(),
        "application_request_limit": 3,
        "order": list(CONDITIONS),
        "baseline_run": str(BASELINE_RUN),
        "full_source_sha256": single.SOURCE_HASH,
        "target_source_sha256": CHAPTER_HASH,
        "checks": {
            "A_replays_original_messages_and_tool": True,
            "B_C_only_background_differs": True,
            "source_once_in_original_order": True,
            "fixed_prompt_blocks_identical": True,
        },
        "artifact_hashes": {
            str(p.relative_to(run_dir)): single.digest_bytes(p.read_bytes())
            for p in [
                run_dir / "full-source.json",
                run_dir / "target-source.json",
                run_dir / "historical-chapter.json",
                *[run_dir / x / "manifest.json" for x in CONDITIONS],
            ]
        },
        "code_hashes": {
            str(p): single.digest_bytes(p.read_bytes())
            for p in (Path(__file__), Path(single.__file__))
        },
    }
    single.write_json(run_dir / "manifest.json", manifest)
    single.write_json(run_dir / "status.json", {"status": "prepared"})
    return manifest


def verify_condition(path: Path) -> dict:
    manifest = single.read_json(path / "manifest.json")
    expected_hash = single.SOURCE_HASH if manifest["condition"] == "A" else CHAPTER_HASH
    if (
        manifest["condition"] not in CONDITIONS
        or manifest["application_request_limit"] != 1
        or manifest["source_sha256"] != expected_hash
    ):
        raise ValueError("Condition outside approved scope")
    for name, expected in manifest["artifact_hashes"].items():
        if single.digest_bytes((path / name).read_bytes()) != expected:
            raise ValueError(f"Frozen condition artifact changed: {name}")
    return manifest


def verify_batch(run_dir: Path) -> dict:
    manifest = single.read_json(run_dir / "manifest.json")
    if (
        manifest["order"] != list(CONDITIONS)
        or manifest["application_request_limit"] != 3
    ):
        raise ValueError("Batch outside approved scope")
    for name, expected in manifest["artifact_hashes"].items():
        if single.digest_bytes((run_dir / name).read_bytes()) != expected:
            raise ValueError(f"Frozen batch artifact changed: {name}")
    for name, expected in manifest["code_hashes"].items():
        if single.digest_bytes(Path(name).read_bytes()) != expected:
            raise ValueError(f"Runner changed after preparation: {name}")
    for condition in CONDITIONS:
        verify_condition(run_dir / condition)
        if (run_dir / condition / "request.started.json").exists():
            raise ValueError("Batch already reserved a request; use --render")
    return manifest


def chapter_review(payload: object, full: dict, target: dict) -> dict:
    review = review_payload(payload, target)
    full_review = review_payload(payload, full)
    by_index = {item["original_index"]: item for item in full_review["items"]}
    for item in review["items"]:
        candidates = by_index[item["original_index"]]["candidates"]
        item["full_book_candidates"] = candidates
        item["target_scope"] = (
            "inside" if item["candidates"] else "outside" if candidates else "unlocated"
        )
        if item["target_scope"] == "outside":
            item["validation_errors"].append(
                "source_quote is outside the target chapter"
            )
    review["counts"]["outside_target"] = sum(
        item["target_scope"] == "outside" for item in review["items"]
    )
    return review


def render_condition(path: Path) -> dict:
    source = single.read_json(path / "source.json")
    full = single.read_json(path.parent / "full-source.json")
    target = single.read_json(path.parent / "target-source.json")
    raw = single.read_json(path / "raw-response.json")
    payload, errors = single.interpret_response(raw, source)
    review = (
        review_payload(payload, source)
        if path.name == "A"
        else chapter_review(payload, full, target)
    )
    review["contract_errors"] = errors
    target_review = chapter_review(payload, full, target)
    single.write_json(path / "parsed-result.json", payload)
    single.write_json(path / "quote-validation.json", review)
    single.write_json(path / "target-quote-validation.json", target_review)
    title = f"《悉达多》条件 {path.name}：完整原始产出"
    markdown = render_review(payload, review, title)
    if errors:
        markdown = "终止/结构检查失败；仅供诊断，已停止本轮。\n\n" + markdown
    (path / "review.md").write_text(markdown)
    # Confirm the effective request captured immediately above the provider call.
    request = single.read_json(path / "request.json")
    packet = single.read_json(path / "prompt.json")
    if request["messages"] != [
        {"role": "system", "content": packet["system_prompt"]},
        {"role": "human", "content": packet["user_prompt"]},
    ] or request["tools"] != [packet["output_tool"]]:
        raise ValueError("Actual request differs from the frozen packet")
    return {
        "contract_errors": errors,
        "counts": review["counts"],
        "target_counts": target_review["counts"],
        "actual_request_verified": True,
    }


def update_ledger(run_dir: Path, status: str, results: dict) -> None:
    from scripts import update_evaluation_run_ledger as ledger

    def relative(path: Path) -> str:
        return str(path.relative_to(single.BACKEND_ROOT.parent))

    entry = {
        "run_id": RUN_ID,
        "date": "2026-09-13",
        "surface": "context_scope_digest",
        "lane": "mechanism_eval",
        "status": status,
        "mechanisms": ["attentional_v2"],
        "dataset_or_manifest": [relative(run_dir / "manifest.json")],
        "run_dir": relative(run_dir),
        "job_ids": [JOB_ID],
        "catalog_status": "not_cataloged",
        "summary_paths": {"manifest": relative(run_dir / "manifest.json")},
        "report_paths": [relative(run_dir / "historical-reference.md")],
        "notes": "Authorized A/B/C diagnostic, one request per condition, serial A→B→C, fail-stop. A replays the prior whole-book request; B/C share chapter SourceUnit and differ only in optional surrounding source. Manual review only; no judge or product change. One selected failure chapter and one sample per condition do not establish a general causal effect. CPA internal attempts and actual billed cost remain unobservable.",
        "metadata": {
            "conditions": results,
            "request_limit": 3,
            "target_chapter": CHAPTER_ID,
        },
    }
    for name in ("summary.json", "review-key.json", "review-items.json"):
        if (run_dir / name).exists():
            entry["summary_paths"][name.removesuffix(".json")] = relative(
                run_dir / name
            )
    for name in ("review.md", "execution-summary.md"):
        if (run_dir / name).exists():
            entry["report_paths"].append(relative(run_dir / name))
    for condition in CONDITIONS:
        for name in (
            "summary.json",
            "request.json",
            "raw-response.json",
            "quote-validation.json",
            "llm-standard.jsonl",
        ):
            if (run_dir / condition / name).exists():
                entry["summary_paths"][f"{condition}_{name}"] = relative(
                    run_dir / condition / name
                )
    data = ledger.upsert_ledger_entry(entry)
    ledger.write_markdown_ledger(data)
    subprocess.run(
        [sys.executable, str(Path(ledger.__file__)), "--check"],
        check=True,
        capture_output=True,
        text=True,
    )


def execute_batch(run_dir: Path) -> dict:
    verify_batch(run_dir)
    single.reserve_request(run_dir, RUN_ID)
    started = time.monotonic()
    results = {}
    update_ledger(run_dir, "running", results)
    try:
        for condition in CONDITIONS:
            single.write_json(
                run_dir / "status.json",
                {
                    "status": "running",
                    "condition": condition,
                    "updated_at": single.now(),
                },
            )
            print(f"Starting condition {condition}", flush=True)
            summary = single.run(
                run_dir / condition,
                prepared_verifier=verify_condition,
                result_renderer=render_condition,
            )
            results[condition] = {
                k: summary[k]
                for k in (
                    "status",
                    "application_request_count",
                    "counts",
                    "target_counts",
                    "usage",
                    "elapsed_seconds",
                    "response_metadata",
                    "error",
                )
                if k in summary
            }
            print(
                json.dumps(
                    {"condition": condition, **results[condition]}, ensure_ascii=False
                ),
                flush=True,
            )
            single.write_json(
                run_dir / "summary.json",
                {"run_id": RUN_ID, "status": "running", "conditions": results},
            )
            update_ledger(run_dir, "running", results)
            if summary["status"] != "review_pending":
                break
    except Exception as exc:
        # Avoid provider exception strings, which may contain credentials.
        results["batch_error"] = {"type": type(exc).__name__}
    status = (
        "review_pending"
        if all(results.get(c, {}).get("status") == "review_pending" for c in CONDITIONS)
        else "failed"
    )
    summary = {
        "run_id": RUN_ID,
        "status": status,
        "conditions": results,
        "unattempted_conditions": [
            c for c in CONDITIONS if not (run_dir / c / "request.started.json").exists()
        ],
        "application_request_count": sum(
            single.read_json(run_dir / c / "request.json")["application_request_number"]
            for c in CONDITIONS
            if (run_dir / c / "request.json").exists()
        ),
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "completed_at": single.now(),
    }
    single.write_json(run_dir / "summary.json", summary)
    single.write_json(
        run_dir / "status.json",
        {
            "status": "completed" if status == "review_pending" else "failed",
            "review_status": status,
            "updated_at": single.now(),
        },
    )
    from .context_scope_review import render_packet

    render_packet(run_dir)
    update_ledger(run_dir, status, results)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--run", action="store_true")
    action.add_argument("--render", action="store_true")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    args = parser.parse_args()
    path = args.run_dir.resolve()
    if args.prepare:
        result = prepare(path)
        update_ledger(path, "planned", {})
    elif args.run:
        result = execute_batch(path)
    else:
        from .context_scope_review import render_packet

        render_packet(path)
        result = {"status": "rendered", "model_calls": 0}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
