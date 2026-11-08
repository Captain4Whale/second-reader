from copy import deepcopy
from hashlib import sha256

import pytest

from scripts.q1_comparison import build_bundle, encode
from scripts.q1_comparison_fixture import synthetic_inputs, source_range
from scripts.q1_comparison_stats import quote_in_window, summarize


@pytest.fixture
def packet(tmp_path):
    b, mixed, key = build_bundle(*synthetic_inputs())
    for name, value in [
        ("batch.json", b),
        ("mixed.json", mixed),
        ("blind-key.json", key),
    ]:
        (tmp_path / name).write_bytes(encode(value) + b"\n")
    return tmp_path, b, mixed, key


def record(mixed, window, mark=None, **changes):
    r = dict(
        schema="q1-mixed-judgment/1",
        annotator_version="q1-annotator/2.0",
        annotator_id="weijiang",
        rubric_version="open_coding",
        rubric_sha256=None,
        batch_id=mixed["batch_id"],
        comparison_batch_id=mixed["batch_id"],
        view="mixed",
        window_id=window["window_id"],
        record_type="marginalia" if mark else "omission",
        record_id=mark["marginalia_id"] if mark else "omission-id",
        revision=1,
        timestamp="2026-11-08T01:00:00.000Z",
        marginalia_id=mark["marginalia_id"] if mark else None,
        type=mark["type"] if mark else None,
        judgment="pass" if mark else None,
        reason="" if mark else "synthetic omission",
        star=False if mark else None,
        needs_verification=False if mark else None,
        remarks="" if mark else None,
        original_source_range=deepcopy(
            mark["original_source_range"] if mark else source_range(14, 17)
        ),
    )
    if mark:
        r.update(source_quote=mark["source_quote"], body_text=mark["body_text"])
    else:
        r.update(action="save", source_quote="天地玄")
    r.update(changes)
    return r


def write_rows(folder, rows):
    for i, row in enumerate(rows, 1):
        row["revision"] = i
    raw = b"".join(encode(r) + b"\n" for r in rows)
    (folder / "judgments.jsonl").write_bytes(raw)
    return raw


@pytest.mark.parametrize("version", ["q1-annotator/2.0", "q1-annotator/2.1"])
def test_counts_revision_snapshot_and_cross_window_omission_hit(packet, version):
    folder, b, mixed, key = packet
    rows = [record(mixed, w, m) for w in mixed["windows"] for m in w["marginalia"]]
    crossing = next(
        r for r in rows if r["original_source_range"] == source_range(12, 18)
    )
    revised = {
        **crossing,
        "judgment": "fail",
        "reason": "synthetic failure",
        "star": True,
        "needs_verification": True,
    }
    revised["annotator_version"] = version
    rows += [revised, record(mixed, mixed["windows"][1])]
    raw = write_rows(folder, rows)
    result = summarize(folder)
    assert result["synthetic"] is True
    assert result["annotation_snapshot"]["sha256"] == sha256(raw).hexdigest()
    assert result["annotation_snapshot"]["revision"] == 7
    groups = {g["experiment_id"]: g for g in result["scopes"][0]["groups"]}
    assert groups["SYNTHETIC-1"]["counts"]["Note"] == dict(
        total=1,
        passed=0,
        failed=1,
        judged=1,
        unjudged=0,
        pass_rate=0.0,
        starred=1,
        needs_verification=1,
    )
    assert groups["SYNTHETIC-2"]["counts"]["Note"]["passed"] == 1
    # Omission is in window 2; group 1's crossing note is judged only in window 1.
    assert all(
        g["omission_anchor_coverage"] == dict(hit_count=1, total=1, hit_rate=1.0)
        for g in groups.values()
    )
    earlier = summarize(folder, revision=5)
    assert earlier["scopes"][0]["groups"][0]["counts"]["Note"]["passed"] == 1
    assert (
        earlier["annotation_snapshot"]["sha256"]
        == sha256(b"".join(raw.splitlines(keepends=True)[:5])).hexdigest()
    )
    assert (
        earlier["scopes"][0]["groups"][0]["omission_anchor_coverage"]["hit_rate"]
        is None
    )


def test_unjudged_flags_empty_snapshot_and_removed_omission(packet):
    folder, b, mixed, key = packet
    w = mixed["windows"][0]
    mark = w["marginalia"][0]
    rows = [
        record(mixed, w, mark, judgment=None, star=True),
        record(mixed, mixed["windows"][1]),
        record(mixed, mixed["windows"][1], action="remove"),
    ]
    write_rows(folder, rows)
    result = summarize(folder)
    gid = key["marginalia"][mark["marginalia_id"]]["opaque_group_id"]
    g = next(g for g in result["scopes"][0]["groups"] if g["opaque_group_id"] == gid)
    count = g["counts"]["Highlight" if mark["type"] == "H" else "Note"]
    assert count["starred"] == 1 and count["judged"] == 0 and count["pass_rate"] is None
    assert g["omission_anchor_coverage"]["total"] == 0
    zero = summarize(folder, revision=0)
    assert all(
        c["judged"] == 0
        for g in zero["scopes"][0]["groups"]
        for c in g["counts"].values()
    )


def test_annotators_and_rubrics_not_pooled(packet, monkeypatch):
    import scripts.q1_comparison_stats as stats

    monkeypatch.setattr(
        stats,
        "rubric_identity",
        lambda version: dict(
            rubric_version=version,
            rubric_sha256=None if version == "open_coding" else "b" * 64,
        ),
    )
    folder, _, mixed, _ = packet
    w = mixed["windows"][0]
    m = w["marginalia"][0]
    rows = [
        record(mixed, w, m),
        record(mixed, w, m, annotator_id="other", judgment="fail", reason="other"),
        record(
            mixed,
            w,
            m,
            rubric_version="test-published",
            rubric_sha256="b" * 64,
            judgment="fail",
            reason="new rubric",
        ),
    ]
    write_rows(folder, rows)
    assert len(summarize(folder)["scopes"]) == 2
    assert len(summarize(folder, annotator=None)["scopes"]) == 3
    assert len(summarize(folder, rubric="open_coding")["scopes"]) == 1


def test_missing_paragraph_omission_endpoint_is_rejected():
    r = source_range(0, 1)
    r["end"]["paragraph_index"] = 3
    w = dict(
        original_source_range=r,
        paragraphs=[
            dict(index=1, offset=0, text="甲"),
            dict(index=3, offset=0, text="乙"),
        ],
    )
    missing = deepcopy(r)
    missing["start"]["paragraph_index"] = 2
    with pytest.raises(ValueError, match="endpoint"):
        quote_in_window(w, missing)


@pytest.mark.parametrize(
    "damage", ["key", "partial", "revision", "leak", "anchor", "revealed", "rubric"]
)
def test_bad_inputs_fail_closed(packet, damage):
    folder, _, mixed, key = packet
    w = mixed["windows"][0]
    rows = [record(mixed, w, w["marginalia"][0])]
    raw = write_rows(folder, rows)
    if damage == "key":
        key["marginalia"] = {}
        (folder / "blind-key.json").write_bytes(encode(key))
    elif damage == "partial":
        (folder / "judgments.jsonl").write_bytes(raw.rstrip(b"\n"))
    else:
        if damage == "revision":
            rows[0]["revision"] = 2
        if damage == "leak":
            rows[0]["run_id"] = "leak"
        if damage == "anchor":
            rows[0]["original_source_range"] = source_range(0, 1)
        if damage == "revealed":
            rows[0]["record_type"] = "reveal"
        if damage == "rubric":
            rows[0]["rubric_sha256"] = "a" * 64
        (folder / "judgments.jsonl").write_bytes(encode(rows[0]) + b"\n")
    with pytest.raises(ValueError):
        summarize(folder)
