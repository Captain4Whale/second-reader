from copy import deepcopy
import json
from pathlib import Path
import shutil

import pytest

from scripts.q1_comparison import digest
from scripts.q1_private_snapshot import fingerprint
from scripts.q1_scoring import (
    append,
    calculate,
    counts,
    read_lines,
    resolve_path,
    validate_all,
)

BACKEND = Path(__file__).resolve().parents[1]


@pytest.fixture
def scoring(tmp_path):
    root = tmp_path
    for name in ["rubric", "src/attentional_v2/prompts/versions"]:
        shutil.copytree(BACKEND / name, root / name)
    (root / "experiments/annotations").mkdir(parents=True)
    (root / "state").mkdir()
    (root / "experiments/log.jsonl").write_text('{"experiment_id":"E"}\n')
    (root / "experiments/scorings.jsonl").touch()
    mark = dict(
        marginalia_id="m1", type="N", original_source_range={"start": 1, "end": 2}
    )
    batch = dict(
        schema="q1-batch/1",
        run_id="run",
        product_sha256="a" * 64,
        units=[dict(unit_id="u", marginalia=[mark])],
    )
    batch["batch_id"] = digest(batch)
    rows = [
        dict(
            revision=1,
            batch_id=batch["batch_id"],
            run_id="run",
            product_sha256="a" * 64,
            unit_id="u",
            record_type="marginalia",
            record_id="m1",
            judgment="pass",
            timestamp="2026-11-10T00:00:00Z",
            annotator_version="q1-annotator/1.8",
            **mark,
        )
    ]
    (root / "state/batch.json").write_text(json.dumps(batch))
    (root / "state/judgments.jsonl").write_text(json.dumps(rows[0]) + "\n")
    (root / "experiments/units.json").write_text(
        json.dumps({"units": [{"run_id": "run", "unit_id": "u"}]})
    )
    journal_hash = fingerprint(root / "state/judgments.jsonl")
    overlay = dict(
        batch_id=batch["batch_id"],
        annotator_id="weijiang",
        revision_end=1,
        journal_prefix_sha256=journal_hash,
    )
    (root / "experiments/annotations/legacy-context.jsonl").write_text(
        json.dumps(overlay) + "\n"
    )
    releases = json.loads(
        (root / "src/attentional_v2/prompts/versions/published.json").read_text()
    )["releases"]
    version = "attentional_v2.digest.v24"
    row = dict(
        schema="q1-scoring/1",
        scoring_id="S1",
        series_id="S",
        supersedes=None,
        registered_at="2026-11-10T00:00:00+00:00",
        date="2026-11-10",
        experiment_id="E",
        title="测试",
        status="completed",
        products=[
            dict(
                experiment_id="E",
                run_id="run",
                model="test-model",
                reasoning_effort="medium",
                product_sha256="a" * 64,
                prompts=[
                    dict(
                        version=version,
                        release_sha256=releases[version]["release_sha256"],
                    )
                ],
                hash_evidence="reconstructed_after_run",
            )
        ],
        unit_set=dict(
            path="experiments/units.json",
            sha256=fingerprint(root / "experiments/units.json"),
            count=1,
        ),
        rubric=dict(
            version="open_coding", sha256=None, form_version=None, form_sha256=None
        ),
        scorer=dict(kind="human", id="weijiang"),
        snapshots=[
            dict(
                path="state/judgments.jsonl",
                sha256=journal_hash,
                revision=1,
                annotator_versions=["q1-annotator/1.8"],
                judgment_time_range=["2026-11-10T00:00:00Z"] * 2,
            )
        ],
        blinding=dict(was_blind=False),
        inputs=dict(kind="legacy", batches=["state/batch.json"]),
        evidence_files={
            p: fingerprint(root / p)
            for p in ["state/batch.json", "state/judgments.jsonl"]
        },
        comparable_to=[],
        calculation={},
        review_session_id=None,
    )
    row["results"] = calculate(row, root)
    return root, row


def test_append_recompute_and_duplicate_guard(scoring):
    root, row = scoring
    append(row, root)
    assert (
        read_lines(root / "experiments/scorings.jsonl")[0]["results"][0]["counts"][
            "Note"
        ]["pass_rate"]
        == 1
    )
    before = (root / "experiments/scorings.jsonl").read_bytes()
    with pytest.raises(ValueError, match="Duplicate"):
        append(row, root)
    assert (root / "experiments/scorings.jsonl").read_bytes() == before
    (root / "state/judgments.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_all([row], root, True)


def test_latest_snapshot_chain_preserves_history(scoring):
    root, row = scoring
    new = {**deepcopy(row), "scoring_id": "S2", "supersedes": "S1"}
    assert validate_all([row, new], root)["S"]["scoring_id"] == "S2"
    new["supersedes"] = None
    with pytest.raises(ValueError, match="chain"):
        validate_all([row, new], root)


def test_incompatible_rejudgment_cannot_claim_same_outputs(scoring):
    root, row = scoring
    new = {**deepcopy(row), "scoring_id": "T1", "series_id": "T"}
    new["products"][0]["product_sha256"] = "b" * 64
    new["comparable_to"] = [
        dict(
            scoring_id="S1",
            mode="same_outputs_different_rubric",
            limitations="different ruler",
        )
    ]
    with pytest.raises(ValueError, match="identical outputs"):
        validate_all([row, new], root)


def test_rates_and_missing_are_not_zero_or_pass(scoring):
    root, row = scoring
    row["results"][0]["counts"]["Note"]["pass_rate"] = 0
    with pytest.raises(ValueError, match="denominator"):
        validate_all([row], root)
    c = counts([dict(type="N", marginalia_id="x")], {})["Note"]
    assert (
        c["pass_rate"] is None and c["unjudged"] == 1 and c["failed_criteria"] is None
    )


def test_criteria_overlap_and_exposure():
    marks = [dict(type="N", marginalia_id="x")]
    form = {
        "mark_types": {
            "N": {
                "criteria": [{"id": "N1", "label": "一"}, {"id": "N2", "label": "二"}]
            },
            "H": {"criteria": []},
        }
    }
    c = counts(
        marks,
        {
            "x": dict(
                judgment="fail",
                failed_criteria=["N1", "N2"],
                prior_judgment_seen=True,
                rubric_uncovered=True,
            )
        },
        form,
    )["Note"]
    assert (
        c["failed"] == 1
        and sum(x["failed"] for x in c["failed_criteria"].values()) == 2
    )
    assert c["prior_judgment_seen"] == 1 and c["rubric_uncovered"] == 1


def test_path_mapping_longest_prefix_and_no_old_edits(tmp_path):
    (tmp_path / "experiments").mkdir()
    rows = [
        {
            "path_mappings": [
                {"from": "/old", "to": "state/copy"},
                {"from": "/old/deep", "to": "state/specific"},
            ]
        }
    ]
    (tmp_path / "experiments/log.jsonl").write_text(json.dumps(rows[0]) + "\n")
    assert resolve_path("/old/deep/x", tmp_path) == tmp_path / "state/specific/x"
    assert resolve_path("/older/x", tmp_path) == Path("/older/x")


def test_partial_jsonl_refuses_read(tmp_path):
    path = tmp_path / "journal.jsonl"
    path.write_text('{"revision":1}')
    with pytest.raises(ValueError, match="Incomplete"):
        read_lines(path)
