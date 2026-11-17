#!/usr/bin/env python3
"""Run the preregistered three-unit pilot, never the formal validation batch."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
PILOT_SET = BACKEND / "experiments/unit-sets/q1-v34-pilot-001.json"
PROTOCOL_ID = "Q1-RUBRIC-V34-VALIDATION-001-PROTOCOL-001"
OUTPUT = BACKEND / "state/experiments/Q1-RUBRIC-V34-VALIDATION-001/pilot"
MODEL = "gpt-6.1-terra"
PROMPT = "attentional_v2.digest.v24"
SAMPLING = {"temperature": 0.2, "max_output_tokens": 4096, "reasoning_effort": "medium"}


def read(path):
    return json.loads(Path(path).read_text())


def stability_sample(notes, seed=20261122):
    """Sample 15 immutable formal Note identities before inspecting judgments.

    Each item has book, unit_id and marginalia_id. Input order is irrelevant.
    When both books have enough Notes, randomly assign the odd slot (8 vs 7).
    A shortage transfers to the other book; fewer than 15 in total is an error.
    """
    identity = lambda n: (n["book"], n["unit_id"], n["marginalia_id"])
    if len({identity(n) for n in notes}) != len(notes):
        raise ValueError("Duplicate formal Note identity")
    if any(n["book"] not in {"bovary", "sapiens"} for n in notes):
        raise ValueError("Unknown book")
    if len(notes) < 15:
        raise ValueError("Fewer than 15 formal Notes; stop, do not silently reduce sample")
    rng = random.Random(seed)
    books = ["bovary", "sapiens"]
    extra = rng.choice(books)
    pools = {b: sorted([dict(n) for n in notes if n["book"] == b], key=identity) for b in books}
    for b in books:
        rng.shuffle(pools[b])
    allocations = {b: min(len(pools[b]), 8 if b == extra else 7) for b in books}
    for b in books:
        allocations[b] += min(15 - sum(allocations.values()), len(pools[b]) - allocations[b])
    result = [n for b in books for n in pools[b][:allocations[b]]]
    rng.shuffle(result)
    return {"seed": seed, "extra_slot_book": extra, "allocations": allocations, "notes": result}


def status(phase, **values):
    (OUTPUT / "status.json").write_text(json.dumps({
        "phase": phase, "updated_at": datetime.now(timezone.utc).isoformat(), **values,
    }, ensure_ascii=False, indent=2) + "\n")


def protocol():
    from eval.attentional_v2.fixed_history_digest import sha
    rows = [json.loads(line) for line in (BACKEND / "experiments/log.jsonl").read_text().splitlines()]
    row = next(r for r in rows if r["experiment_id"] == PROTOCOL_ID)
    if sha(PILOT_SET.read_bytes()) != row["pilot_unit_set"]["sha256"]:
        raise ValueError("Pilot manifest changed after registration")
    manifest = read(PILOT_SET)
    if Counter(u["book"] for u in manifest["units"]) != {"bovary": 1, "sapiens": 2}:
        raise ValueError("Pilot must contain exactly one Bovary and two Sapiens units")
    if manifest["source_review"]["status"] != "passed":
        raise ValueError("Pilot source review not passed")
    return manifest


def prepare(source):
    from eval.attentional_v2.fixed_history_digest import HistoricalRun, write, sha
    manifest = protocol()
    directory = OUTPUT / "preflight"
    directory.mkdir(parents=True, exist_ok=False)
    histories = {u["book"]: HistoricalRun(source, u["run_id"]) for u in manifest["units"]}
    write(directory / "manifest-checks.json", [h.check_manifest() for h in histories.values()])
    fingerprints = {}
    for book, h in histories.items():
        fingerprints[book] = {str(p): sha(p.read_bytes()) for p in h.output.rglob("*") if p.is_file()}
    write(directory / "source-files-before.json", fingerprints)
    for u in manifest["units"]:
        h = histories[u["book"]]
        packet = h.reconstruct(u["unit_id"])
        if packet["accepted_call"]["sampling"] != SAMPLING or packet["accepted_call"]["prompt_version"] != PROMPT:
            raise ValueError("Original sampling/prompt differs from approved formal configuration")
        if packet["original_source_range"] != u["original_source_range"]:
            raise ValueError("Pilot source range differs from preregistered selection")
        if sha(packet["current_unit_source"]["source_text"].encode()) != manifest["source_review"]["source_text_sha256"][u["book"] + "/" + u["unit_id"]]:
            raise ValueError("Reviewed source differs from reconstructed input")
        write(directory / f"{u['book']}-{u['unit_id']}.json", packet)
    status("prepared", model_calls=0)


def report():
    from eval.attentional_v2.fixed_history_digest import write, sha
    manifest = protocol()
    summary = {"schema": "q1-v34-pilot-report/1", "model": MODEL, "sampling": SAMPLING,
               "excluded_from_formal_statistics": True, "units": [], "attempts": []}
    text = ["# Terra medium 试跑全部批注", "", "试跑排除正式统计。以下包含原书引用，仅保存在忽略的 state 中。", ""]
    for u in manifest["units"]:
        directory = OUTPUT / "outputs" / u["book"] / u["unit_id"]
        if not directory.exists():
            continue
        result = read(directory / "result.json") if (directory / "result.json").exists() else None
        requests = sorted((directory / "actual").glob("request-*.json"))
        responses = sorted((directory / "actual").glob("response-*.json"))
        counts = Counter(m["kind"] for m in result["result"]["marginalia"]) if result else Counter()
        summary["units"].append({"book": u["book"], "unit_id": u["unit_id"], "Note": counts["note"],
            "Highlight": counts["highlight"], "parsed": result is not None, "physical_attempts": len(requests),
            "retry_or_repair": len(requests) > 1, "responses_captured": len(responses)})
        for request in requests:
            response_path = request.with_name(request.name.replace("request-", "response-"))
            response = read(response_path) if response_path.exists() else {}
            usage = response.get("usage_metadata") or {}
            reasoning = (usage.get("output_token_details") or {}).get("reasoning")
            summary["attempts"].append({"book": u["book"], "unit_id": u["unit_id"],
                "attempt": int(request.stem.split("-")[-1]), "returned_model": response.get("model_name"),
                "finish_reason": response.get("finish_reason"), "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"), "reasoning_tokens": reasoning,
                "reasoning_share_of_4096_limit": reasoning / 4096 if reasoning is not None else None,
                "reasoning_exceeds_half_limit": reasoning > 2048 if reasoning is not None else None,
                "request_path": str(request), "response_path": str(response_path) if response else None})
        text += [f"## {u['book']} / {u['unit_id']} · {u['chapter_title']}", ""]
        if result:
            for i, mark in enumerate(result["result"]["marginalia"], 1):
                text += [f"### {i}. {mark['kind']}", "", "引用：", mark["source_quote"], ""]
                if mark["kind"] == "note":
                    text += ["批注：", mark["content"], ""]
        else:
            text += ["未生成可接受结果；失败证据保留。", ""]
    summary["usage_complete"] = all(a["input_tokens"] is not None and a["output_tokens"] is not None for a in summary["attempts"])
    summary["totals"] = {k: sum(a[k] or 0 for a in summary["attempts"]) for k in ["input_tokens", "output_tokens", "reasoning_tokens"]}
    summary["totals"].update({k: sum(u[k] for u in summary["units"]) for k in ["Note", "Highlight"]})
    totals = summary["totals"]
    summary["cost_at_requested_rates_usd"] = (totals["input_tokens"] + totals["output_tokens"] * 5) / 1_000_000
    summary["actual_billed_cost_usd"] = None
    before = read(OUTPUT / "preflight/source-files-before.json")
    summary["source_files_unchanged"] = all(sha(Path(p).read_bytes()) == digest for files in before.values() for p, digest in files.items())
    write(OUTPUT / "summary.json", summary)
    with (OUTPUT / "annotations.md").open("x") as f:
        f.write("\n".join(text) + "\n")
    return summary


def run(source):
    from eval.attentional_v2.fixed_history_digest import HistoricalRun, run_digest, sha
    from scripts.run_fixed_history_a1 import validate_marks
    manifest = protocol()
    if (OUTPUT / "outputs").exists():
        raise ValueError("Pilot already attempted; no automatic resume or regeneration")
    (OUTPUT / "outputs").mkdir()
    status("running")
    try:
        for u in manifest["units"]:
            packet = read(OUTPUT / "preflight" / f"{u['book']}-{u['unit_id']}.json")
            history = HistoricalRun(source, u["run_id"])
            if packet != history.reconstruct(u["unit_id"]):
                raise ValueError("Historical input changed since preflight")
            directory = OUTPUT / "outputs" / u["book"] / u["unit_id"]
            result = run_digest(packet, directory, model=MODEL, effort="medium", prompt_version=PROMPT, operator_backend=source)
            validate_marks(history, packet, result)
            if result["sampling"] != SAMPLING:
                raise ValueError("Effective sampling differs from approved configuration")
            for p in sorted((directory / "actual").glob("response-*.json")):
                returned_model = read(p).get("model_name")
                if not returned_model or not returned_model.startswith(MODEL):
                    raise ValueError("Returned model identifier differs from requested Terra; stop")
            print(json.dumps({"book": u["book"], "unit_id": u["unit_id"], "status": "complete"}), flush=True)
        summary = report()
        if not summary["source_files_unchanged"]:
            raise ValueError("Historical source files changed during pilot")
        status("completed", human_review="pending", formal_run="not_started")
    except Exception as exc:
        if not (OUTPUT / "summary.json").exists():
            report()
        status("failed", error_type=type(exc).__name__, message=str(exc), formal_run="not_started")
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["prepare", "run", "stability-sample"])
    p.add_argument("--source-backend", type=Path)
    p.add_argument("--notes", type=Path, help="Formal Note identity JSON list; no judgment data")
    p.add_argument("--output", type=Path, help="New private stability-selection receipt")
    args = p.parse_args()
    if args.action == "stability-sample":
        if not args.notes or not args.output or not args.output.resolve().is_relative_to((BACKEND / "state").resolve()):
            p.error("--notes and a new --output under backend/state required")
        notes = read(args.notes)
        if any(set(n) != {"book", "unit_id", "marginalia_id"} for n in notes):
            p.error("Input must contain identities only; no judgments or content")
        result = stability_sample(notes)
        from eval.attentional_v2.fixed_history_digest import write, sha
        result["input_sha256"] = sha(args.notes.read_bytes())
        write(args.output, result)
    else:
        if not args.source_backend:
            p.error("--source-backend required")
        (prepare if args.action == "prepare" else run)(args.source_backend.resolve())


if __name__ == "__main__":
    main()
