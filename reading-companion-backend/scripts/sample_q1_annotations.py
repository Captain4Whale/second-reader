#!/usr/bin/env python3
"""Build blinded unit samples from a finished Reading Product or a finished chapter pilot."""

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import tempfile

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from build_q1_chapter_review import build_packet
from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_core.source_ranges import (
    source_range_from_wire,
    validate_book_document_source_range,
)
from src.reading_product.serialization import load_document_bytes
from src.reading_product.validation import validate_document

PRESETS = {"bovary": (100, 120, 150, 3), "sapiens": (60, 70, 80, 1)}


def encode(data):
    return json.dumps(
        data, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()


def load_source(args):
    pilot = args.pilot_product is not None
    original_dir = args.pilot_original if pilot else args.output
    if pilot:
        path = args.pilot_product
    else:
        folder = args.output / "public/reading-products"
        pointer = json.loads((folder / "current.json").read_bytes())
        path = folder / "revisions" / pointer["revision_id"] / "reading-product.json"
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError("Invalid revision path")
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    product = load_document_bytes(raw)
    original = json.loads((original_dir / "public/book_document.json").read_bytes())
    packet = {}
    if pilot:
        verified = build_packet(path, args.output, original_dir)
        packet = {u["unit_id"]: u for u in verified["units"]}
        original_sha = verified["original_epub_sha256"]
    else:
        if (
            product.status != "complete"
            or product.reading_id != pointer["reading_id"]
            or digest != pointer["reading_product_sha256"]
            or digest != pointer["revision_id"]
        ):
            raise ValueError("Expected a matching published, complete revision")
        validate_document(product, book_document=original)
        original_sha = sha256(
            (original_dir / "_assets/source.epub").read_bytes()
        ).hexdigest()
        if original_sha != product.source.epub_sha256:
            raise ValueError("Original EPUB differs from published product")
    meta = dict(
        book=original["metadata"]["book"],
        author=original["metadata"].get("author"),
        run_id=args.run_id,
        reading_id=product.reading_id,
        product_sha256=digest,
        product_source=asdict(product.source),
        original_epub_sha256=original_sha,
        original_substrate_sha256=book_document_substrate_digest(original),
    )
    return product, original, packet, meta


def unit_data(unit, doc, pilot_packet):
    span = unit.source_range
    pilot = pilot_packet.get(unit.unit_id)
    original_span = (
        source_range_from_wire(pilot["original_source_range"]) if pilot else span
    )
    resolved = validate_book_document_source_range(
        doc, original_span, require_single_resource=False
    )
    first, last = original_span.start, original_span.end
    paragraphs, before, after = [], [], []
    for para in resolved.chapter["paragraphs"]:
        i, text = para["paragraph_index"], para["text"]
        if not text or para.get("text_role") == "auxiliary":
            continue
        if i < first.paragraph_index:
            before.append(text)
        elif i > last.paragraph_index:
            after.append(text)
        else:
            lo = first.char_offset if i == first.paragraph_index else 0
            hi = last.char_offset if i == last.paragraph_index else len(text)
            if text[:lo]:
                before.append(text[:lo])
            if text[hi:]:
                after.append(text[hi:])
            if lo < hi:
                paragraphs.append(
                    dict(index=i, offset=lo, text=text[lo:hi], href=para["href"])
                )
    pilot_marks = {m["marginalia_id"]: m for m in pilot["marginalia"]} if pilot else {}
    marks = []
    for item in unit.marginalia:
        original = pilot_marks.get(item.marginalia_id)
        marks.append(
            dict(
                marginalia_id=item.marginalia_id,
                type="H" if item.kind == "highlight" else "N",
                source_range=asdict(item.source_range),
                source_quote=item.source_quote,
                body_text=item.body_text,
                original_source_range=(
                    original["original_source_range"]
                    if original
                    else asdict(item.source_range)
                ),
            )
        )
    marks.sort(
        key=lambda m: (
            m["source_range"]["start"]["paragraph_index"],
            m["source_range"]["start"]["char_offset"],
            m["marginalia_id"],
        )
    )
    return dict(
        unit_id=unit.unit_id,
        chapter_title=resolved.chapter.get("title"),
        source_range=asdict(span),
        original_source_range=asdict(original_span),
        paragraphs=paragraphs,
        before=before[-4:],
        after=after[:4],
        marginalia=marks,
    )


def sample(units, limits, seed, all_units=False):
    low, target, high, batches = limits
    rng = random.Random(seed)
    lengths = [sum(len(p["text"]) for p in u["paragraphs"]) for u in units]
    total = sum(lengths)
    pools = [[], [], []]
    pos = 0
    for u, length in zip(units, lengths):
        layer = min(2, (2 * pos + length) * 3 // (2 * total))
        pos += length
        pools[layer].append(dict(u, stratum=layer + 1))
    strata_sizes = list(map(len, pools))
    for pool in pools:
        rng.shuffle(pool)
    order = []
    while any(pools):
        for pool in pools:
            if pool:
                order.append(pool.pop())
    if not all_units:
        count, choices = 0, []
        for n, u in enumerate(order, 1):
            count += len(u["marginalia"])
            if low <= count <= high and n >= batches:
                choices.append((abs(count - target), n))
        if not choices:
            raise ValueError(
                "No whole-unit prefix within the requested mark budget; use --pilot-all for a pilot"
            )
        order = order[: min(choices)[1]]
    groups = [[] for _ in range(batches)]
    counts = [0] * batches
    per_layer = [[0] * batches for _ in pools]
    for u in order:
        load = per_layer[u["stratum"] - 1]
        b = min(range(batches), key=lambda i: (load[i], counts[i], len(groups[i]), i))
        load[b] += 1
        groups[b].append(u)
        counts[b] += len(u["marginalia"])
    for group in groups:
        rng.shuffle(group)
    return groups, strata_sizes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output", type=Path, help="book output containing public/ and _assets/"
    )
    parser.add_argument(
        "--run-id", required=True, help="exact evaluation ledger run ID"
    )
    parser.add_argument("--preset", choices=PRESETS, required=True)
    parser.add_argument("--seed", type=int, default=20261103)
    parser.add_argument(
        "--pilot-product", type=Path, help="finished chapter pilot partial product"
    )
    parser.add_argument(
        "--pilot-original", type=Path, help="matching original book output for pilot"
    )
    parser.add_argument(
        "--pilot-all", action="store_true", help="one small batch of all pilot units"
    )
    args = parser.parse_args()
    if bool(args.pilot_original) != bool(args.pilot_product) or (
        args.pilot_all and not args.pilot_product
    ):
        parser.error("A pilot requires both --pilot-product and --pilot-original")
    product, doc, packet, meta = load_source(args)
    units = [unit_data(u, doc, packet) for u in product.units]
    # Measure against the original whole book, including for single-chapter pilots.
    paragraph_starts = {}
    total_chars = 0
    for chapter in doc["chapters"]:
        for para in chapter["paragraphs"]:
            if para["text"] and para.get("text_role") != "auxiliary":
                paragraph_starts[chapter["id"], para["paragraph_index"]] = total_chars
                total_chars += len(para["text"])

    for u in units:
        span = u["original_source_range"]
        endpoints = [
            paragraph_starts[pos["chapter_id"], pos["paragraph_index"]]
            + pos["char_offset"]
            for pos in (span["start"], span["end"])
        ]
        u["book_position_percent"] = round(sum(endpoints) * 50 / total_chars)

    # Deferred chapters can settle after later chapters. Stratify by book position.
    chapter_order = {c["id"]: i for i, c in enumerate(doc["chapters"])}

    def book_position(unit):
        start = unit["original_source_range"]["start"]
        return (
            chapter_order[start["chapter_id"]],
            start["paragraph_index"],
            start["char_offset"],
        )

    units.sort(key=book_position)
    if not units or not args.run_id.strip():
        parser.error("Nonempty run ID and accepted units required")
    limits = (0, 0, 0, 1) if args.pilot_all else PRESETS[args.preset]
    groups, sizes = sample(units, limits, args.seed, args.pilot_all)
    rules = dict(
        version=1,
        seed=args.seed,
        preset=args.preset,
        scope="completed chapter pilot" if packet else "complete reading",
        pilot_all=args.pilot_all,
        available_units=len(units),
        stratum_units=sizes,
        mark_budget=None if args.pilot_all else list(limits[:3]),
        rule="All accepted units in source order; strata by midpoint in cumulative accepted "
        "paragraph code points (excluding separators). Seed-shuffle within thirds, draw "
        "round-robin without replacement. Choose earliest prefix nearest target within bounds. "
        "Balance each stratum across batches, then mark and unit counts; shuffle each batch. "
        "Marks ordered by source start, then ID.",
    )
    for number, group in enumerate(groups, 1):
        batch = dict(
            schema="q1-batch/1",
            **meta,
            sampling=rules,
            batch_number=number,
            batch_count=len(groups),
            units=group,
        )
        batch["batch_id"] = sha256(encode(batch)).hexdigest()
        folder = BACKEND / "state/q1_annotation" / batch["batch_id"]
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / "batch.json"
        data = encode(batch) + b"\n"
        with tempfile.NamedTemporaryFile(dir=folder) as temp:
            temp.write(data)
            temp.flush()
            try:
                dest.hardlink_to(temp.name)
            except FileExistsError:
                if dest.read_bytes() != data:
                    raise ValueError(f"Conflicting existing batch at {dest}")
        # Create the selectable journal once, preserving every previous review.
        with (folder / "judgments.jsonl").open("ab"):
            pass
        print(
            f"{dest}  ({len(group)} units, {sum(len(u['marginalia']) for u in group)} marks)"
        )


if __name__ == "__main__":
    main()
