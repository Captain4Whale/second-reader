from copy import deepcopy
from hashlib import sha256
import json

import pytest

from scripts import q1_adjudicated_conversion as conversion


def sample(kind="N"):
    mark = {
        "marginalia_id": "m1",
        "type": kind,
        "source_quote": "anchor",
        "body_text": "body",
    }
    mixed = {"windows": [{"window_id": "w", "book": "book", "marginalia": [mark]}]}
    row = {
        "record_id": "m1",
        "record_type": "marginalia",
        "schema": "q1-mixed-judgment/3",
        "review_completed": True,
        "revision": 1,
        "review_session_id": "s",
        "rubric_version": "q1-v1",
        "criterion_assessments": {
            c: {"judgment": "pass", "reason": ""}
            for c in (["N1", "N2", "N3", "N4"] if kind == "N" else ["H1", "H2", "H3"])
        },
        "tags": [],
        "needs_verification": False,
        "rubric_uncovered": False,
        "uncovered_reason": "",
    }
    return mixed, row


@pytest.mark.parametrize(
    "kind,criterion,veto,passed",
    [
        ("N", "N1", None, False),
        ("N", "N2", "incorrect_information", False),
        ("N", "N3", "spoiler", False),
        ("N", "N4", None, True),
        ("H", "H1", None, False),
        ("H", "H2", "incomplete_range", False),
        ("H", "H3", "unintelligible_without_context", False),
    ],
)
def test_exact_criterion_mapping(kind, criterion, veto, passed):
    mixed, row = sample(kind)
    row["criterion_assessments"][criterion]["judgment"] = "fail"
    original = deepcopy(row)
    result = conversion.convert_records(mixed, [row], [])[0]
    assert (result["judgment"] == "pass") == passed
    assert result["vetoes"] == ([veto] if veto else [])
    assert result["tags"] == (["anchor_issue"] if criterion == "N4" else [])
    assert row == original
    assert "annotator_version" not in result and "timestamp" not in result
    assert result["provenance"]["source_revision"] == 1


def test_friction_and_verification_do_not_veto_but_clean_pass_excludes_only_two_tags():
    mixed, row = sample()
    row.update(tags=["teacher_tone", "too_terse"], needs_verification=True)
    result = conversion.convert_records(mixed, [row], [])[0]
    assert result["judgment"] == "pass" and result["clean_pass"]
    assert result["needs_verification"] and result["uncertain"] is None
    for change in (
        {"tags": ["redundancy"]},
        {"rubric_uncovered": True, "uncovered_reason": "尾巴：阅读理解"},
    ):
        r = {**row, **change}
        result = conversion.convert_records(mixed, [r], [])[0]
        assert result["judgment"] == "pass" and not result["clean_pass"]
    with pytest.raises(ValueError, match="Unmapped"):
        conversion.convert_records(
            mixed,
            [{**row, "rubric_uncovered": True, "uncovered_reason": "unknown"}],
            [],
        )


def test_adjudication_only_overrides_core_and_keeps_veto_and_revision():
    mixed, row = sample()
    row["criterion_assessments"]["N1"]["judgment"] = "fail"
    row["criterion_assessments"]["N3"]["judgment"] = "fail"
    a = {
        "marginalia_id": "m1",
        "final_n1": "pass",
        "body_text": "body",
        "evidence_item": "A1",
        "final_text": "过。",
    }
    result = conversion.convert_records(mixed, [row], [a])[0]
    assert result["core"]["judgment"] == "pass" and result["judgment"] == "fail"
    assert result["provenance"]["core_source"] == "owner_adjudication"
    with pytest.raises(ValueError, match="body mismatch"):
        conversion.convert_records(mixed, [row], [{**a, "body_text": "other"}])
    with pytest.raises(ValueError, match="Duplicate/unknown"):
        conversion.convert_records(mixed, [row], [a, a])


def test_latest_revision_and_clean_denominator():
    mixed, row = sample()
    later = {**deepcopy(row), "revision": 2, "tags": ["redundancy"]}
    records = conversion.convert_records(mixed, [row, later], [])
    c = conversion.conversion_counts(records)
    assert records[0]["provenance"]["source_revision"] == 2
    assert c["Note"]["passed"] == 1 and c["Note"]["clean_pass_rate"] == 0
    assert c["Highlight"]["pass_rate"] is None


def test_evidence_binding_and_final_verdict_before_historical_reason(
    tmp_path, monkeypatch
):
    mixed, row = sample()
    labels = (
        [f"A{i}" for i in range(1, 8)]
        + ["B1", "B2"]
        + [f"C{i}" for i in range(1, 6)]
        + ["D1"]
    )
    marks, rows, text = [], [], []
    for i, label in enumerate(labels):
        marks.append({**mixed["windows"][0]["marginalia"][0], "marginalia_id": label})
        rows.append({**deepcopy(row), "record_id": label, "revision": i + 1})
        final = (
            "这些原则指什么？"
            if label == "D1"
            else "过。之前不过主要是因为原书有注解。"
        )
        text.append(f"**{label}** 锚点\n> body\n\n最终：{final}\n")
    mixed["windows"][0]["marginalia"] = marks
    raw = "\n".join(text).encode()
    (tmp_path / "owner.md").write_bytes(raw)
    sections = conversion.adjudication_sections(raw)
    target = {"version": "q1-v2", "sha256": "a" * 64}
    spec = {
        "source_review_sha256": sha256(b"journal").hexdigest(),
        "adjudication_file": "owner.md",
        "adjudication_sha256": sha256(raw).hexdigest(),
        "target_rubric": target,
        "conversion_id": "test",
        "adjudications": [
            {
                "marginalia_id": label,
                "evidence_item": label,
                "final_n1": "pass",
                **sections[label],
            }
            for label in labels
        ],
    }
    path = tmp_path / "binding.json"
    path.write_text(json.dumps(spec))
    monkeypatch.setattr(
        conversion,
        "read_review",
        lambda _: ({"rubric_version": "q1-v1"}, None, mixed, [], rows, b"journal"),
    )
    result = conversion.load_conversion(tmp_path, path, target)
    assert len(result["records"]) == 15 and all(
        r["judgment"] == "pass" for r in result["records"]
    )
    (tmp_path / "owner.md").write_bytes(raw + b" ")
    with pytest.raises(ValueError, match="evidence mismatch"):
        conversion.load_conversion(tmp_path, path, target)
