from copy import deepcopy
from hashlib import sha256
import json

import pytest

from scripts import q1_rubric_review as review
from scripts.q1_comparison import build_bundle, encode
from scripts.q1_comparison_fixture import synthetic_inputs
from scripts.q1_rubric_form import load_form
from tests.test_q1_comparison_stats import record, write_rows


@pytest.fixture(params=["q1-v0.form.v1", "q1-v1.form.v1"])
def prepared(tmp_path, monkeypatch, request):
    source = tmp_path / "source"
    source.mkdir()
    b, mixed, key = build_bundle(*synthetic_inputs())
    for name, data in [
        ("batch.json", b),
        ("mixed.json", mixed),
        ("blind-key.json", key),
    ]:
        (source / name).write_bytes(encode(data) + b"\n")
    marks = [(w, m) for w in mixed["windows"] for m in w["marginalia"]]
    rows = [
        record(
            mixed,
            w,
            m,
            judgment="fail" if i == 1 else "pass",
            reason="synthetic old reason",
        )
        for i, (w, m) in enumerate(marks)
    ]
    # Latest revision wins; omissions must not affect report denominators.
    rows += [
        record(mixed, marks[0][0], marks[0][1], judgment="pass", reason="latest old"),
        record(mixed, mixed["windows"][1]),
    ]
    write_rows(source, rows)
    original = {p.name: p.read_bytes() for p in source.iterdir()}
    real_backend = review.BACKEND
    monkeypatch.setattr(review, "BACKEND", tmp_path)
    (tmp_path / "rubric").symlink_to(real_backend / "rubric", target_is_directory=True)
    output = tmp_path / "state/review"
    context = review.prepare(source, output, form_version=request.param)
    return source, output, mixed, context, original


def new_row(mixed, w, m, context, **changes):
    return record(
        mixed,
        w,
        m,
        schema="q1-mixed-judgment/2",
        annotator_version="q1-annotator/2.3",
        **{
            k: context[k]
            for k in (
                "rubric_version",
                "rubric_sha256",
                "rubric_form_version",
                "rubric_form_sha256",
                "review_session_id",
            )
        },
        failed_criteria=[],
        tags=[],
        criterion_flags={},
        rubric_uncovered=False,
        review_completed=True,
        prior_judgment_seen=False,
        **changes,
    )


def test_preparation_exact_copies_no_keys_no_original_writes_and_no_overwrite(prepared):
    source, output, _, context, original = prepared
    assert {p.name: p.read_bytes() for p in source.iterdir()} == original
    assert (output / "mixed.json").read_bytes() == original["mixed.json"]
    assert (output / "open_coding.snapshot.jsonl").read_bytes() == original[
        "judgments.jsonl"
    ]
    assert context["baseline_sha256"] == sha256(original["judgments.jsonl"]).hexdigest()
    assert (output / "judgments.jsonl").read_bytes() == b""
    assert (
        not (output / "blind-key.json").exists()
        and not (output / "batch.json").exists()
    )
    with pytest.raises(ValueError, match="overwrite"):
        review.prepare(source, output)
    with pytest.raises(ValueError, match="state"):
        review.prepare(source, source.parent / "outside")


def test_latest_comparison_groups_uncovered_incomplete_and_exposure(prepared):
    source, output, mixed, context, original = prepared
    marks = [(w, m) for w in mixed["windows"] for m in w["marginalia"]]
    rows = [new_row(mixed, w, m, context) for w, m in marks[:4]]
    form, _ = load_form(context["rubric_form_version"])
    rows[0].update(
        judgment="fail",
        failed_criteria=[form["mark_types"][rows[0]["type"]]["criteria"][0]["id"]],
        reason="",
    )
    rows[2].update(judgment="fail", rubric_uncovered=True)
    seen = deepcopy(rows[0])
    seen.update(prior_judgment_seen=True, remarks="amended after exposure")
    rows.append(seen)
    write_rows(output, rows)
    report = review.comparison(output)
    assert report["counts"] == dict(
        annotations=5,
        completed=4,
        unchanged=1,
        incomplete=1,
        unpaired=0,
        old_pass_new_fail=2,
        old_fail_new_pass=1,
        rubric_uncovered=1,
    )
    changed = report["old_pass_new_fail"][0]
    assert changed["old_reason"] == "latest old"
    assert (
        changed["prior_judgment_seen"]
        and changed["new_revision"] == 5
        and changed["first_completed_revision"] == 1
    )
    assert changed["body_text"] == marks[0][1]["body_text"]
    destination = output.parent / "report"
    assert review.write_report(output, destination) == report["counts"]
    assert "旧过新不过" in (destination / "report.md").read_text()
    assert {p.name: p.read_bytes() for p in source.iterdir()} == original


@pytest.mark.parametrize(
    "name", ["rubric-form.json", "mixed.json", "open_coding.snapshot.jsonl"]
)
def test_tampered_snapshot_rejects_before_report(prepared, name):
    _, output, _, _, _ = prepared
    with (output / name).open("ab") as stream:
        stream.write(b" ")
    with pytest.raises(ValueError, match="mismatch"):
        review.write_report(output, output.parent / "report")
    assert not (output.parent / "report").exists()


def test_cross_session_or_partial_journal_rejected(prepared):
    _, output, mixed, context, _ = prepared
    w = mixed["windows"][0]
    m = w["marginalia"][0]
    row = new_row(mixed, w, m, context)
    row["review_session_id"] = "other"
    write_rows(output, [row])
    with pytest.raises(ValueError, match="scope"):
        review.comparison(output)
    (output / "judgments.jsonl").write_text(json.dumps(row))
    with pytest.raises(ValueError, match="Incomplete"):
        review.comparison(output)


def test_stepwise_report_preserves_independent_reasons_and_prior_legacy_rows(prepared):
    source, output, mixed, context, original = prepared
    w, m = next((w, m) for w in mixed['windows'] for m in w['marginalia'] if m['type'] == 'N')
    old = new_row(mixed, w, m, context, reason='legacy overall')
    form, _ = load_form(context['rubric_form_version'])
    new = deepcopy(old)
    new.update(schema='q1-mixed-judgment/3', annotator_version='q1-annotator/3.0',
               criterion_assessments={c['id']: {'judgment': 'pass', 'reason': c['id'] + ' individual'} for c in form['mark_types']['N']['criteria']},
               uncovered_reason='uncovered text', rubric_uncovered=True, judgment='fail')
    write_rows(output, [old, new])
    report = review.comparison(output)
    item = report['rubric_uncovered'][0]
    assert len(report['assessments']) == 1
    assert report['assessments'][0]['marginalia_id'] == item['marginalia_id']
    assert item['assessment_mode'] == 'stepwise'
    assert item['criterion_assessments']['N1']['reason'] == 'N1 individual'
    assert item['new_reason'] == 'legacy overall'
    assert item['uncovered_reason'] == 'uncovered text'
    target = output.parent / 'step-report'
    review.write_report(output, target)
    text = (target / 'report.md').read_text()
    assert 'N1 individual' in text and 'uncovered text' in text
    assert {p.name: p.read_bytes() for p in source.iterdir()} == original
