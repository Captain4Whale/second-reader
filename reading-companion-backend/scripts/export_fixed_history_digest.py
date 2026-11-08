#!/usr/bin/env python3
"""Export verified fixed-history results for the offline Q1 importer; no model calls."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

BACKEND = next(
    p for p in Path(__file__).resolve().parents if (p / "src/reading_core").is_dir()
)
sys.path.insert(0, str(BACKEND))
from src.attentional_v2.source_spans import source_ref_from_unit  # noqa: E402
from src.reading_core.book_document_identity import book_document_substrate_digest  # noqa: E402
from src.reading_core.source_ranges import (  # noqa: E402
    source_range_from_wire,
    validate_book_document_source_range,
)


def read(path):
    return json.loads(Path(path).read_bytes())


def encode(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def export(group_root, unit_set, source_backend, experiment_id, run_id, output):
    output = output.resolve()
    if not output.is_relative_to((BACKEND / "state").resolve()):
        raise ValueError("Output must be inside ignored backend/state")
    manifest = read(unit_set)
    if manifest["purpose"] != "dev":
        raise ValueError("Only dev units may be exported for this diagnostic")
    selected = {(u["run_id"], u["unit_id"]): u for u in manifest["units"]}
    if len(selected) != len(manifest["units"]):
        raise ValueError("Duplicate selected unit")
    ledger = {
        r["run_id"]: r
        for r in read(source_backend / "docs/evaluation/run_ledger.json")["entries"]
    }
    packets = {}
    for path in group_root.glob("*/*/input.json"):
        packet = read(path)
        key = packet["original_run_id"], packet["unit_id"]
        if key in packets:
            raise ValueError("Duplicate replay unit")
        packets[key] = (path.parent, packet)
    if packets.keys() != selected.keys():
        raise ValueError("Replay units differ from fixed manifest")
    sources, documents, coverage, marks, identities = {}, {}, [], [], set()
    for key, row in selected.items():
        directory, packet = packets[key]
        result = read(directory / "result.json")
        if (result["original_run_id"], result["unit_id"]) != key or not result[
            "reconstructed"
        ]:
            raise ValueError("Replay identity mismatch")
        if result["input_sha256"] != hashlib.sha256(encode(packet)).hexdigest():
            raise ValueError("Replay input hash mismatch")
        if packet["original_source_range"] != row["original_source_range"]:
            raise ValueError("Replay coverage differs from fixed window")
        if (
            result["calls"][-1]["status"] != "ok"
            or result["request_sha256"] != result["calls"][-1]["request_sha256"]
        ):
            raise ValueError("Missing accepted request receipt")
        identity = (row["original_epub_sha256"], row["original_substrate_sha256"])
        sid = hashlib.sha256(encode(identity)).hexdigest()
        if sid not in sources:
            path = (
                source_backend.parent
                / ledger[key[0]]["run_dir"]
                / "output/public/book_document.json"
            )
            raw = path.read_bytes()
            doc = json.loads(raw)
            if (
                book_document_substrate_digest(doc) != identity[1]
                or packet["substrate_sha256"] != identity[1]
            ):
                raise ValueError("Source substrate mismatch")
            sources[sid] = dict(
                source_id=sid,
                epub_sha256=identity[0],
                substrate_sha256=identity[1],
                book_document_path=f"sources/{sid}.json",
            )
            documents[sid] = raw
        doc = json.loads(documents[sid])
        coverage.append(
            dict(
                source_id=sid,
                original_source_range=packet["original_source_range"],
                status="complete",
            )
        )
        identities.add(
            (
                result["model"],
                result["prompt_version"],
                result["prompt"]["release_sha256"],
            )
        )
        for i, mark in enumerate(result["result"]["marginalia"], 1):
            ref = source_ref_from_unit(
                packet["current_unit_source"],
                quote=mark["source_quote"],
                role="reaction_anchor",
            )
            if ref["resolution"]["status"] != "matched":
                raise ValueError("Nonexact or ambiguous replay anchor")
            r = {
                end: {
                    k: ref["source_span"][cursor][k]
                    for k in ("chapter_id", "paragraph_index", "char_offset")
                }
                for end, cursor in (("start", "start_cursor"), ("end", "end_cursor"))
            }
            validate_book_document_source_range(
                doc,
                source_range_from_wire(r),
                expected_quote=mark["source_quote"],
                require_single_resource=False,
            )
            if mark["kind"] not in ("highlight", "note"):
                raise ValueError("Unknown marginalia kind")
            marks.append(
                dict(
                    source_id=sid,
                    marginalia_id=f"{key[1]}-replay-m{i:03d}",
                    unit_id=key[1],
                    type="H" if mark["kind"] == "highlight" else "N",
                    body_text="" if mark["kind"] == "highlight" else mark["content"],
                    source_quote=mark["source_quote"],
                    original_source_range=r,
                    request_sha256=result["request_sha256"],
                )
            )
    if len(identities) != 1:
        raise ValueError("Group has mixed model/prompt identities")
    model, version, release_sha256 = identities.pop()
    data = dict(
        schema="q1-digest-comparison-output/1",
        experiment_id=experiment_id,
        run_id=run_id,
        model=model,
        prompt=dict(version=version, release_sha256=release_sha256),
        reconstructed=True,
        synthetic=False,
        sources=list(sources.values()),
        coverage=coverage,
        marginalia=marks,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    for sid, raw in documents.items():
        p = output.parent / sources[sid]["book_document_path"]
        p.parent.mkdir(exist_ok=True)
        if p.exists():
            if p.read_bytes() != raw:
                raise ValueError("Existing source copy differs")
        else:
            with p.open("xb") as f:
                f.write(raw)
    with output.open("xb") as f:
        f.write(encode(data) + b"\n")
    return output


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("group-root", "unit-set", "source-backend", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    for name in ("experiment-id", "run-id"):
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    print(
        export(
            a.group_root,
            a.unit_set,
            a.source_backend,
            a.experiment_id,
            a.run_id,
            a.output,
        )
    )
