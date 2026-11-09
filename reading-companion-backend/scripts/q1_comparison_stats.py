#!/usr/bin/env python3
"""Independent, offline statistics for immutable Q1 mixed annotation snapshots."""

import argparse
from collections import Counter
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.q1_comparison import (  # noqa: E402
    contains,
    digest,
    encode,
    nonempty,
    overlaps,
    read_json,
    require,
    span,
)
from scripts.check_iteration_provenance import rubric_identity  # noqa: E402
from scripts.q1_rubric_form import REVIEW_FIELDS, load_form, validate_assessment  # noqa: E402


def load_bundle(folder):
    folder = Path(folder)
    b, mixed, key = (
        read_json(folder / f) for f in ("batch.json", "mixed.json", "blind-key.json")
    )
    require(
        b["schema"] == "q1-comparison-batch/1"
        and mixed["schema"] == "q1-mixed/1"
        and key["schema"] == "q1-blind-key/1",
        "Unsupported comparison bundle",
    )
    require(
        b["manifest_sha256"]
        == digest({k: v for k, v in b.items() if k != "manifest_sha256"}),
        "Manifest hash mismatch",
    )
    require(
        b["mixed_sha256"] == digest(mixed) and b["blind_key_sha256"] == digest(key),
        "Projection/key hash mismatch",
    )
    require(
        b["comparison_batch_id"]
        == mixed["batch_id"]
        == key["comparison_batch_id"]
        == digest({k: v for k, v in mixed.items() if k != "batch_id"}),
        "Batch identity mismatch",
    )
    marks = {m["marginalia_id"]: m for m in b["marginalia"]}
    require(
        len(marks) == len(b["marginalia"]) and set(marks) == set(key["marginalia"]),
        "Incomplete/duplicate mark mapping",
    )
    groups = {g["opaque_group_id"] for g in b["groups"]}
    require(
        all(v["opaque_group_id"] in groups for v in key["marginalia"].values()),
        "Unknown mapped group",
    )
    projected = [m["marginalia_id"] for w in mixed["windows"] for m in w["marginalia"]]
    eligible = {mid for mid, m in marks.items() if m["mixed_window_id"] is not None}
    require(
        len(projected) == len(set(projected)) and set(projected) == eligible,
        "Mixed projection must assign each eligible mark once",
    )
    require(
        {w["window_id"] for w in mixed["windows"]}
        == {w["window_id"] for w in b["windows"]},
        "Window mapping mismatch",
    )
    for w in mixed["windows"]:
        original_window = next(
            v for v in b["windows"] if v["window_id"] == w["window_id"]
        )
        require(
            all(original_window[k] == v for k, v in w.items() if k != "marginalia"),
            "Mixed window differs from original",
        )
        for m in w["marginalia"]:
            origin = marks[m["marginalia_id"]]
            require(
                origin["mixed_window_id"] == w["window_id"]
                and all(origin[k] == v for k, v in m.items()),
                "Mixed mark differs from original",
            )
    return b, mixed, key


def quote_in_window(w, r):
    require(contains(w["original_source_range"], r), "Omission is outside its window")
    for endpoint in (r["start"], r["end"]):
        p = next(
            (p for p in w["paragraphs"] if p["index"] == endpoint["paragraph_index"]),
            None,
        )
        require(
            p is not None
            and p["offset"] <= endpoint["char_offset"] <= p["offset"] + len(p["text"]),
            "Omission endpoint is absent from window text",
        )
    pieces = []
    for p in w["paragraphs"]:
        i = p["index"]
        if r["start"]["paragraph_index"] <= i <= r["end"]["paragraph_index"]:
            lo = (
                r["start"]["char_offset"] - p["offset"]
                if i == r["start"]["paragraph_index"]
                else 0
            )
            hi = (
                r["end"]["char_offset"] - p["offset"]
                if i == r["end"]["paragraph_index"]
                else len(p["text"])
            )
            require(
                0 <= lo <= hi <= len(p["text"]),
                "Omission character offsets out of bounds",
            )
            pieces.append(p["text"][lo:hi])
    return "\n\n".join(p for p in pieces if p)


def validate_rows(rows, mixed):
    windows = {w["window_id"]: w for w in mixed["windows"]}
    bindings, rubrics, forms, seen = {}, {}, {}, {}
    review_scopes = set()
    base = set(
        "schema annotator_version annotator_id rubric_version rubric_sha256 batch_id comparison_batch_id view window_id record_type record_id revision timestamp marginalia_id type judgment reason star needs_verification remarks original_source_range".split()
    )
    for i, r in enumerate(rows, 1):
        require(isinstance(r, dict), "Journal rows must be objects")
        rt = r.get("record_type")
        review = r.get("schema") == "q1-mixed-judgment/2"
        extra = (
            {"source_quote", "body_text"}
            if rt == "marginalia"
            else {"action", "source_quote"}
            if rt == "omission"
            else set()
        )
        require(
            rt in ("marginalia", "omission", "unit_note") and set(r) == base | extra | (REVIEW_FIELDS if review else set()),
            "Unsupported/extra record fields (reveal, preference and legacy records are not mixed judgments)",
        )
        require(
            r["schema"] in ("q1-mixed-judgment/1", "q1-mixed-judgment/2")
            and r["annotator_version"] in (("q1-annotator/2.3",) if review else ("q1-annotator/2.0", "q1-annotator/2.1", "q1-annotator/2.2", "q1-annotator/2.3"))
            and r["view"] == "mixed"
            and r["batch_id"] == r["comparison_batch_id"] == mixed["batch_id"]
            and type(r["revision"]) is int
            and r["revision"] == i,
            "Journal batch/version/revision mismatch",
        )
        require(
            nonempty(r["annotator_id"]) and nonempty(r["record_id"]),
            "Missing human/record identity",
        )
        require(
            nonempty(r["timestamp"])
            and datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).tzinfo
            is not None,
            "Timestamp requires an offset",
        )
        version = r["rubric_version"]
        require(nonempty(version), "Missing rubric version")
        if version not in rubrics:
            rubrics[version] = rubric_identity(version)
        require(
            r["rubric_sha256"] == rubrics[version]["rubric_sha256"],
            "Unknown/draft/changed rubric",
        )
        if review:
            fv = r['rubric_form_version']
            if fv not in forms:
                forms[fv] = load_form(fv)
            form, form_hash = forms[fv]
            require(r['rubric_form_sha256'] == form_hash and version == form['rubric_version'], 'Form identity mismatch')
            validate_assessment(r, form)
            review_scopes.add((r['annotator_id'], version, fv, form_hash, r['review_session_id']))
            if rt == 'marginalia':
                prior = seen.get(r['record_id'])
                require(not r['prior_judgment_seen'] or prior is not None, 'Old judgment viewed before first completion')
                require(not prior or not prior['prior_judgment_seen'] or r['prior_judgment_seen'], 'Prior exposure cannot be undone')
                seen[r['record_id']] = r
        require(r["window_id"] in windows, "Unknown window")
        w = windows[r["window_id"]]
        identity = rt, r["record_id"]
        require(
            identity not in bindings or bindings[identity] == r["window_id"],
            "A record changed its owning window",
        )
        bindings[identity] = r["window_id"]
        span(r["original_source_range"])
        if rt == "marginalia":
            m = next(
                (m for m in w["marginalia"] if m["marginalia_id"] == r["record_id"]),
                None,
            )
            require(
                m is not None and r["marginalia_id"] == r["record_id"],
                "Unknown marginalia judgment",
            )
            require(
                all(
                    r[k] == m[k]
                    for k in (
                        "type",
                        "body_text",
                        "source_quote",
                        "original_source_range",
                    )
                ),
                "Judgment does not match mark",
            )
            require(
                r["judgment"] in (None, "pass", "fail")
                and isinstance(r["reason"], str)
                and isinstance(r["remarks"], str)
                and type(r["star"]) is bool
                and type(r["needs_verification"]) is bool
                and (review or r["judgment"] != "fail" or nonempty(r["reason"])),
                "Invalid judgment fields",
            )
        else:
            require(
                all(
                    r[k] is None
                    for k in (
                        "marginalia_id",
                        "type",
                        "judgment",
                        "star",
                        "needs_verification",
                    )
                ),
                "Non-mark row has judgment fields",
            )
            if rt == "omission":
                require(
                    r["action"] in ("save", "remove")
                    and nonempty(r["reason"])
                    and nonempty(r["source_quote"])
                    and r["remarks"] is None
                    and quote_in_window(w, r["original_source_range"])
                    == r["source_quote"],
                    "Invalid omission",
                )
            else:
                require(
                    r["record_id"] == w["window_id"]
                    and r["original_source_range"] == w["original_source_range"]
                    and isinstance(r["remarks"], str)
                    and r["reason"] is None,
                    "Invalid window note",
                )


    if review_scopes:
        require(len(review_scopes) == 1 and all(r['schema'] == 'q1-mixed-judgment/2' for r in rows),
                'Review journal must contain one isolated session/form scope')


def summarize(
    folder, journal_path=None, revision=None, annotator="weijiang", rubric=None
):
    b, mixed, key = load_bundle(folder)
    path = Path(journal_path) if journal_path else Path(folder) / "judgments.jsonl"
    raw = (
        path.read_bytes()
    )  # one immutable in-memory snapshot, even if writer later appends
    require(not raw or raw.endswith(b"\n"), "Journal has an incomplete final line")
    lines = raw.splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    validate_rows(rows, mixed)
    limit = len(rows) if revision is None else revision
    require(type(limit) is int and 0 <= limit <= len(rows), "Invalid snapshot revision")
    prefix = b"".join(lines[:limit])
    rows = rows[:limit]
    selected = [
        r
        for r in rows
        if (annotator is None or r["annotator_id"] == annotator)
        and (rubric is None or r["rubric_version"] == rubric)
    ]
    scopes = sorted(
        {(r["annotator_id"], r["rubric_version"], r["rubric_sha256"]) for r in selected}
    )
    # An explicitly selected empty scope still reports zero judged, not zero generated.
    if not scopes and annotator:
        identity = rubric_identity(rubric or "open_coding")
        scopes = [(annotator, identity["rubric_version"], identity["rubric_sha256"])]
    windows = {w["window_id"]: w for w in b["windows"]}
    results = []
    for human, rv, rh in scopes:
        latest = {}
        for r in selected:
            if (r["annotator_id"], r["rubric_version"], r["rubric_sha256"]) == (
                human,
                rv,
                rh,
            ):
                latest[(r["record_type"], r["record_id"])] = r
        omissions = [
            r
            for (t, _), r in latest.items()
            if t == "omission" and r["action"] == "save"
        ]
        by_group = []
        for g in b["groups"]:
            all_marks = [
                m
                for m in b["marginalia"]
                if key["marginalia"][m["marginalia_id"]]["opaque_group_id"]
                == g["opaque_group_id"]
            ]
            eligible = [m for m in all_marks if m["mixed_window_id"] is not None]
            counts = {}
            for kind, label in (("H", "Highlight"), ("N", "Note")):
                marks = [m for m in eligible if m["type"] == kind]
                judgments = [
                    latest.get(("marginalia", m["marginalia_id"])) for m in marks
                ]
                passed = sum(
                    r is not None and r["judgment"] == "pass" for r in judgments
                )
                failed = sum(
                    r is not None and r["judgment"] == "fail" for r in judgments
                )
                judged = passed + failed
                counts[label] = dict(
                    total=len(marks),
                    passed=passed,
                    failed=failed,
                    judged=judged,
                    unjudged=len(marks) - judged,
                    pass_rate=passed / judged if judged else None,
                    starred=sum(bool(r and r["star"]) for r in judgments),
                    needs_verification=sum(
                        bool(r and r["needs_verification"]) for r in judgments
                    ),
                )
            hits = []
            for omission in omissions:
                w = windows[omission["window_id"]]
                # Full anchors, including those owned by other windows or reported unassigned.
                hits.append(
                    any(
                        m["source_id"] == w["source_id"]
                        and overlaps(
                            m["original_source_range"],
                            omission["original_source_range"],
                        )
                        for m in all_marks
                    )
                )
            by_group.append(
                dict(
                    **g,
                    counts=counts,
                    unassigned_count=len(all_marks) - len(eligible),
                    omission_anchor_coverage=dict(
                        hit_count=sum(hits),
                        total=len(hits),
                        hit_rate=sum(hits) / len(hits) if hits else None,
                    ),
                )
            )
        results.append(
            dict(
                annotator_id=human, rubric_version=rv, rubric_sha256=rh, groups=by_group
            )
        )
    return dict(
        schema="q1-mixed-statistics/1",
        comparison_batch_id=mixed["batch_id"],
        synthetic=mixed["synthetic"],
        experiment_ids=b["experiment_ids"],
        unit_set=b["unit_set"],
        manifest_sha256=b["manifest_sha256"],
        mixed_sha256=b["mixed_sha256"],
        blind_key_sha256=b["blind_key_sha256"],
        annotation_snapshot=dict(
            sha256=sha256(prefix).hexdigest(),
            revision=limit,
            whole_file_sha256=sha256(raw).hexdigest(),
            whole_file_revisions=len(lines),
        ),
        unassigned_reasons=dict(Counter(x["reason"] for x in b["unassigned_items"])),
        notes=[
            "Latest revision per record within each annotator/rubric scope; scopes never pooled.",
            "Pass rate denominator is pass + fail; star/verification include unjudged marks.",
            "Omission metric is anchor-overlap coverage, not semantic recall.",
            "Mixed marks have one start-owner; no duplicate-window judgments.",
            "Side-by-side, preference and reveal are deferred; their records are rejected.",
        ],
        scopes=results,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("batch", type=Path)
    p.add_argument("--journal", type=Path)
    p.add_argument("--revision", type=int)
    p.add_argument("--annotator", default="weijiang")
    p.add_argument("--rubric")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = summarize(
        args.batch, args.journal, args.revision, args.annotator, args.rubric
    )
    raw = encode(report) + b"\n"
    if args.output:
        require(
            args.output.resolve().is_relative_to((BACKEND / "state").resolve()),
            "Statistics output must be in backend/state",
        )
        with args.output.open("xb") as f:
            f.write(raw)
        print(args.output)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
