import json
import shutil

import pytest

from scripts.check_iteration_provenance import (
    BACKEND,
    append_trial,
    check,
    rubric_identity,
    rows,
    sha,
    validate_trial,
)


@pytest.fixture
def snapshot(tmp_path):
    for name in ("experiments", "rubric", "src/attentional_v2/prompts/versions"):
        shutil.copytree(BACKEND / name, tmp_path / name)
    return tmp_path


def baseline(root):
    return next(
        row
        for row in rows(root / "experiments/log.jsonl")
        if row["experiment_id"] == "Q1-BASELINE-001"
    )


def test_baseline_has_frozen_units_open_coding_and_honest_missing_history(snapshot):
    result = check(snapshot, base_ref=None)
    assert result == {
        "experiments": len(rows(snapshot / "experiments/log.jsonl")),
        "dev_units": 67,
        "holdout_units": 75,
        "legacy_contexts": 2,
    }
    row = baseline(snapshot)
    assert row["results"]["pass_rate"] is None
    assert row["rubric_version"] == "open_coding"
    assert row["actual_request_hashes"] is None
    assert {p["hash_evidence"] for p in row["prompts"]} == {"reconstructed_after_run"}
    text = (snapshot / "experiments/unit-sets/dev-v1.json").read_text()
    assert all(
        '"' + key + '"' not in text
        for key in (
            "text",
            "source_quote",
            "body_text",
            "before",
            "after",
            "reason",
            "remarks",
        )
    )


def test_trial_rejects_holdout_multiple_variables_and_draft_rubric(snapshot):
    row = baseline(snapshot)
    row["phase"] = "iteration"
    row["unit_set"] = {
        "path": "experiments/unit-sets/holdout-v1.json",
        "sha256": sha(snapshot / "experiments/unit-sets/holdout-v1.json"),
    }
    with pytest.raises(ValueError, match="Holdout"):
        validate_trial(row, snapshot)
    row["phase"] = "final_validation"
    validate_trial(row, snapshot)
    row["changed_variables"] = ["prompt", "model"]
    with pytest.raises(ValueError, match="one variable"):
        validate_trial(row, snapshot)
    with pytest.raises(ValueError, match="draft"):
        rubric_identity("q1-v0", snapshot)


def test_duplicate_trial_and_manifest_edits_are_rejected(snapshot):
    row = baseline(snapshot)
    old = (snapshot / "experiments/log.jsonl").read_bytes()
    with pytest.raises(ValueError, match="Duplicate"):
        append_trial(row, snapshot)
    assert (snapshot / "experiments/log.jsonl").read_bytes() == old
    path = snapshot / "experiments/unit-sets/dev-v1.json"
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="Frozen"):
        check(snapshot, base_ref=None)


def test_new_trial_preserves_every_existing_log_byte(snapshot):
    path = snapshot / "experiments/log.jsonl"
    before = path.read_bytes()
    row = baseline(snapshot)
    row["experiment_id"] = "TEST-APPEND-ONLY"
    append_trial(row, snapshot)
    assert path.read_bytes().startswith(before)
    assert rows(path)[-1] == row
    assert len(rows(path)) == len(before.splitlines()) + 1
    check(snapshot, base_ref=None)


def test_legacy_prefix_digest_detects_rewrite_even_with_valid_json(snapshot, tmp_path):
    journal_root = tmp_path / "journals"
    for overlay in (
        json.loads(line)
        for line in (snapshot / "experiments/annotations/legacy-context.jsonl")
        .read_text()
        .splitlines()
    ):
        path = journal_root / overlay["batch_id"] / "judgments.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("{}\n")
    with pytest.raises(ValueError, match="prefix changed"):
        check(snapshot, base_ref=None, annotation_root=journal_root)
