"""Offline Q1 window alignment and blind projections. Never imports the reader/LLM."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import re
import uuid

from src.reading_core.book_document_identity import book_document_substrate_digest
from src.reading_core.source_ranges import (
    source_range_from_wire,
    validate_book_document_source_range,
)

BACKEND = Path(__file__).resolve().parents[1]


def encode(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()


def digest(value):
    return sha256(encode(value)).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def hash_value(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def point(value):
    require(
        set(value) == {"chapter_id", "paragraph_index", "char_offset"},
        "Invalid coordinate fields",
    )
    require(all(type(v) is int for v in value.values()), "Coordinates must be integers")
    require(
        value["chapter_id"] > 0
        and value["paragraph_index"] > 0
        and value["char_offset"] >= 0,
        "Invalid coordinate bounds",
    )
    return value["chapter_id"], value["paragraph_index"], value["char_offset"]


def span(value):
    require(set(value) == {"start", "end"}, "Invalid range fields")
    a, z = point(value["start"]), point(value["end"])
    require(a[0] == z[0] and a < z, "Range must be nonempty and within one chapter")
    return a, z


def overlaps(a, b):
    x, y = span(a), span(b)
    return x[0][0] == y[0][0] and max(x[0], y[0]) < min(x[1], y[1])


def contains(a, b):
    x, y = span(a), span(b)
    return x[0] <= y[0] < y[1] <= x[1] and x[0][0] == y[0][0]


def source_identity(source):
    return source["epub_sha256"], source["substrate_sha256"]


def legacy_batch(path):
    b = read_json(path)
    require(b.get("schema") == "q1-batch/1", "Expected q1-batch/1")
    require(
        b["batch_id"] == digest({k: v for k, v in b.items() if k != "batch_id"}),
        "Legacy batch fingerprint mismatch",
    )
    return b


def load_dev_windows(unit_set_path, batch_root):
    """Only opens referenced dev batches, never walks or opens holdout folders."""
    manifest = read_json(unit_set_path)
    require(
        manifest.get("schema") == "fixed-unit-set/1"
        and manifest.get("purpose") == "dev",
        "This iteration tool only accepts dev manifests",
    )
    relative = (
        Path(unit_set_path).resolve().relative_to(BACKEND)
        if Path(unit_set_path).resolve().is_relative_to(BACKEND)
        else None
    )
    frozen = read_json(BACKEND / "experiments/frozen.json")
    if relative and str(relative) in frozen:
        require(
            sha256(Path(unit_set_path).read_bytes()).hexdigest()
            == frozen[str(relative)],
            "Frozen dev manifest changed",
        )
    batches, sources, windows = {}, {}, []
    for row in manifest["units"]:
        bid = row["batch_id"]
        require(hash_value(bid), "Invalid legacy batch ID")
        if bid not in batches:
            batches[bid] = legacy_batch(Path(batch_root) / bid / "batch.json")
        b = batches[bid]
        for field in (
            "run_id",
            "reading_id",
            "product_sha256",
            "original_epub_sha256",
            "original_substrate_sha256",
        ):
            require(
                row[field] == b[field], "Manifest/batch identity mismatch: " + field
            )
        matched = [u for u in b["units"] if u["unit_id"] == row["unit_id"]]
        require(len(matched) == 1, "Missing/duplicate fixed unit")
        u = matched[0]
        require(
            u["original_source_range"] == row["original_source_range"]
            and u["source_range"] == row["source_range"]
            and [m["marginalia_id"] for m in u["marginalia"]] == row["marginalia_ids"],
            "Frozen unit differs from batch",
        )
        identity = (b["original_epub_sha256"], b["original_substrate_sha256"])
        sid = digest(identity)
        sources[sid] = dict(
            source_id=sid, epub_sha256=identity[0], substrate_sha256=identity[1]
        )
        windows.append(
            dict(
                source_id=sid,
                original_source_range=u["original_source_range"],
                book=b["book"],
                author=b.get("author"),
                chapter_title=u.get("chapter_title"),
                paragraphs=u["paragraphs"],
                before=u["before"],
                after=u["after"],
                legacy_ref=dict(batch_id=bid, unit_id=u["unit_id"]),
            )
        )
    return (
        list(sources.values()),
        windows,
        batches,
        dict(
            id=manifest["unit_set_id"],
            sha256=sha256(Path(unit_set_path).read_bytes()).hexdigest(),
        ),
    )


def load_output(path, experiment_log):
    """The documented fixed-history Digest rerun output contract; fail closed."""
    path = Path(path)
    data = read_json(path)
    require(
        data.get("schema") == "q1-digest-comparison-output/1",
        "Unsupported Digest output contract",
    )
    for key in ("experiment_id", "run_id", "model"):
        require(nonempty(data.get(key)), "Missing output metadata: " + key)
    require(
        type(data.get("reconstructed")) is bool and type(data.get("synthetic")) is bool,
        "Explicit reconstructed/synthetic booleans required",
    )
    p = data["prompt"]
    require(
        nonempty(p.get("version"))
        and (
            hash_value(p.get("release_sha256"))
            or (data["synthetic"] and p.get("release_sha256") is None)
        ),
        "Invalid prompt identity",
    )
    if not data["synthetic"]:
        rows = [
            json.loads(s)
            for s in Path(experiment_log).read_text().splitlines()
            if s.strip()
        ]
        trials = [r for r in rows if r["experiment_id"] == data["experiment_id"]]
        require(
            len(trials) == 1 and data["run_id"] in trials[0]["run_ids"],
            "Output experiment/run is not registered",
        )
        require(
            any(
                x["version"] == p["version"]
                and x["release_sha256"] == p["release_sha256"]
                for x in trials[0]["prompts"]
            ),
            "Output prompt differs from registered trial",
        )
    else:
        require(
            data["experiment_id"].startswith("SYNTHETIC-"),
            "Synthetic IDs must start SYNTHETIC-",
        )
    sources, docs = {}, {}
    for s in data["sources"]:
        require(
            nonempty(s["source_id"]) and s["source_id"] not in sources,
            "Duplicate source ID",
        )
        require(
            hash_value(s["epub_sha256"]) and hash_value(s["substrate_sha256"]),
            "Invalid source hashes",
        )
        doc = read_json(path.parent / s["book_document_path"])
        require(
            book_document_substrate_digest(doc) == s["substrate_sha256"],
            "Source substrate hash mismatch",
        )
        sources[s["source_id"]] = s
        docs[s["source_id"]] = doc
    require(bool(sources), "Sources are required")

    def validate_range(sid, value, quote=None):
        require(sid in sources, "Unknown source ID")
        span(value)
        validate_book_document_source_range(
            docs[sid],
            source_range_from_wire(value),
            expected_quote=quote,
            require_single_resource=False,
        )

    for c in data["coverage"]:
        require(
            c.get("status") == "complete",
            "Only terminal complete coverage can be compared",
        )
        validate_range(c["source_id"], c["original_source_range"])
    ids = set()
    for m in data["marginalia"]:
        key = m["source_id"], m["marginalia_id"]
        require(
            nonempty(m["marginalia_id"]) and key not in ids,
            "Duplicate source/mark identity within a group",
        )
        ids.add(key)
        require(
            m["type"] in ("H", "N") and isinstance(m["body_text"], str),
            "Invalid mark type/body",
        )
        require(
            (m["type"] == "N" and bool(m["body_text"].strip()))
            or (m["type"] == "H" and not m["body_text"]),
            "H has no body; N requires a body",
        )
        require(nonempty(m["source_quote"]), "Missing quote")
        require(
            m.get("request_sha256") is None or hash_value(m["request_sha256"]),
            "Invalid request hash",
        )
        validate_range(m["source_id"], m["original_source_range"], m["source_quote"])
    data["output_sha256"] = sha256(path.read_bytes()).hexdigest()
    return data


def legacy_output(batches, trial):
    """No judgments are copied or relabelled as blind. This is one baseline group."""
    prompt = next(p for p in trial["prompts"] if ".digest." in p["version"])
    sources, coverage, marks, models = {}, [], [], set()
    ledger = {
        r["run_id"]: r
        for r in read_json(BACKEND / "docs/evaluation/run_ledger.json")["entries"]
    }
    for b in batches.values():
        require(b["run_id"] in trial["run_ids"], "Legacy run missing from baseline")
        metadata = BACKEND.parent / ledger[b["run_id"]]["summary_paths"]["metadata"]
        models.add(read_json(metadata)["config"]["profile"]["model"])
        sid = digest((b["original_epub_sha256"], b["original_substrate_sha256"]))
        sources[sid] = dict(
            source_id=sid,
            epub_sha256=b["original_epub_sha256"],
            substrate_sha256=b["original_substrate_sha256"],
        )
        for u in b["units"]:
            coverage.append(
                dict(
                    source_id=sid,
                    original_source_range=u["original_source_range"],
                    status="complete",
                )
            )
            for m in u["marginalia"]:
                marks.append(
                    {
                        **deepcopy(m),
                        "body_text": m.get("body_text") or "",
                        "source_id": sid,
                        "run_id": b["run_id"],
                        "unit_id": u["unit_id"],
                        "request_sha256": None,
                    }
                )
    require(
        len(models) == 1,
        "Legacy baseline runs have different models; import separately",
    )
    return dict(
        schema="q1-digest-comparison-output/1",
        experiment_id=trial["experiment_id"],
        run_id=None,
        run_ids=sorted({b["run_id"] for b in batches.values()}),
        model=models.pop(),
        prompt={k: prompt[k] for k in ("version", "release_sha256")},
        reconstructed=True,
        synthetic=False,
        sources=list(sources.values()),
        coverage=coverage,
        marginalia=marks,
        output_sha256=digest(batches),
    )


def build_bundle(sources, windows, outputs, unit_set):
    require(bool(windows) and bool(outputs), "Need windows and at least one group")
    sources = deepcopy(sources)
    source_ids = {source_identity(s): s["source_id"] for s in sources}
    require(len(source_ids) == len(sources), "Duplicate source identity")
    windows = deepcopy(windows)
    for w in windows:
        span(w["original_source_range"])
        require(w["source_id"] in source_ids.values(), "Window source missing")
        w["window_id"] = str(uuid.uuid4())
    # Multiple owners would make mixed assignment ambiguous; reject overlapping windows.
    for i, w in enumerate(windows):
        require(
            not any(
                w["source_id"] == v["source_id"]
                and overlaps(w["original_source_range"], v["original_source_range"])
                for v in windows[:i]
            ),
            "Fixed windows overlap; choose unambiguous windows",
        )
    rng = random.SystemRandom()
    groups, marks, mappings, unmatched = [], [], {}, []
    for output in outputs:
        gid = str(uuid.uuid4())
        group = {
            k: deepcopy(output[k])
            for k in (
                "experiment_id",
                "run_id",
                "model",
                "prompt",
                "reconstructed",
                "synthetic",
                "output_sha256",
            )
        }
        group.update(opaque_group_id=gid)
        if "run_ids" in output:
            group["run_ids"] = output["run_ids"]
        groups.append(group)
        remap = {
            s["source_id"]: source_ids.get(source_identity(s))
            for s in output["sources"]
        }
        require(all(remap.values()), "Group source does not match fixed window sources")
        for w in windows:
            require(
                any(
                    remap[c["source_id"]] == w["source_id"]
                    and c["status"] == "complete"
                    and contains(c["original_source_range"], w["original_source_range"])
                    for c in output["coverage"]
                ),
                "Group has no complete coverage for a window (not an empty output)",
            )
        for original in output["marginalia"]:
            mid = str(uuid.uuid4())
            sid, r = remap[original["source_id"]], original["original_source_range"]
            start, end = span(r)
            related = [
                w
                for w in windows
                if w["source_id"] == sid and overlaps(r, w["original_source_range"])
            ]
            owners = [
                w
                for w in related
                if span(w["original_source_range"])[0]
                <= start
                < span(w["original_source_range"])[1]
            ]
            owner = owners[0] if owners else None
            m = {
                k: deepcopy(original[k])
                for k in ("type", "body_text", "source_quote", "original_source_range")
            }
            m.update(
                marginalia_id=mid,
                source_id=sid,
                mixed_window_id=owner["window_id"] if owner else None,
                overlapping_window_ids=[w["window_id"] for w in related],
                crosses_boundary=bool(
                    owner and not contains(owner["original_source_range"], r)
                ),
            )
            marks.append(m)
            mappings[mid] = dict(
                opaque_group_id=gid,
                original_marginalia_id=original["marginalia_id"],
                original_source_id=original["source_id"],
                run_id=original.get("run_id", output["run_id"]),
                unit_id=original.get("unit_id"),
                request_sha256=original.get("request_sha256"),
            )
            if owner is None:
                unmatched.append(
                    dict(
                        marginalia_id=mid,
                        reason="anchor_start_outside_windows"
                        if related
                        else "no_window_overlap",
                    )
                )
    mixed_windows = []
    for w in windows:
        visible = {
            k: deepcopy(w[k])
            for k in (
                "window_id",
                "original_source_range",
                "book",
                "author",
                "chapter_title",
                "paragraphs",
                "before",
                "after",
            )
        }
        visible["marginalia"] = [
            {
                k: deepcopy(m[k])
                for k in (
                    "marginalia_id",
                    "type",
                    "body_text",
                    "source_quote",
                    "original_source_range",
                    "crosses_boundary",
                )
            }
            for m in marks
            if m["mixed_window_id"] == w["window_id"]
        ]
        rng.shuffle(visible["marginalia"])
        mixed_windows.append(visible)
    # Opaque source/group IDs, ordering seeds, membership and provenance never enter this projection.
    mixed = dict(
        schema="q1-mixed/1",
        synthetic=any(g["synthetic"] for g in groups),
        windows=mixed_windows,
    )
    mixed["batch_id"] = digest(mixed)
    key = dict(
        schema="q1-blind-key/1",
        comparison_batch_id=mixed["batch_id"],
        marginalia=mappings,
    )
    canonical = dict(
        schema="q1-comparison-batch/1",
        comparison_batch_id=mixed["batch_id"],
        unit_set=unit_set,
        experiment_ids=sorted({g["experiment_id"] for g in groups}),
        groups=groups,
        sources=sources,
        windows=windows,
        marginalia=marks,
        unassigned_items=unmatched,
        mixed_sha256=digest(mixed),
        blind_key_sha256=digest(key),
    )
    canonical["manifest_sha256"] = digest(canonical)
    return canonical, mixed, key


def write_bundle(root, bundle):
    """Restrict generated copyrighted/private artifacts to ignored backend state."""
    root = Path(root).resolve()
    require(
        root.is_relative_to((BACKEND / "state").resolve()),
        "Batch output must be inside backend/state",
    )
    canonical, mixed, key = bundle
    dest = root / mixed["batch_id"]
    dest.mkdir(parents=True, exist_ok=False)
    for name, data in (
        ("batch.json", canonical),
        ("mixed.json", mixed),
        ("blind-key.json", key),
    ):
        (dest / name).write_bytes(encode(data) + b"\n")
    return dest
