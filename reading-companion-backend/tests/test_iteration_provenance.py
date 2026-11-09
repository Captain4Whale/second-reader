import json
import shutil
import subprocess

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
        draft = next(
            version
            for version, release in json.loads(
                (snapshot / "rubric/releases.json").read_text()
            ).items()
            if release["status"] == "draft"
        )
        rubric_identity(draft, snapshot)


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


@pytest.mark.parametrize("target", ["rubric", "examples", "registry", "removal"])
def test_published_rubric_cannot_be_rewritten_by_refreshing_hashes(snapshot, tmp_path, target):
    """A trusted Git base must catch changes even when current hashes agree."""
    repo = tmp_path / "repo"
    root = repo / "backend"
    root.mkdir(parents=True)
    for name in ("experiments", "rubric", "src"):
        shutil.copytree(snapshot / name, root / name)
    rubric = root / "rubric/test-published.md"
    examples = root / "rubric/test-published.examples.json"
    rubric.write_text("Published synthetic criterion\n")
    examples.write_text('{"entries": []}\n')
    registry = root / "rubric/releases.json"
    releases = json.loads(registry.read_text())
    releases["test-published"] = {
        "status": "published", "path": "rubric/test-published.md",
        "sha256": sha(rubric), "date": "2026-11-09",
    }
    registry.write_text(json.dumps(releases))
    frozen = root / "experiments/frozen.json"
    locks = json.loads(frozen.read_text())
    for p in (rubric, examples):
        locks[str(p.relative_to(root))] = sha(p)
    frozen.write_text(json.dumps(locks))
    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True,
        )
    git("init")
    git("add", "backend")
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
        "-c", "core.hooksPath=/dev/null", "commit", "-m", "Trusted publication")
    check(root, base_ref="HEAD")
    if target in {"rubric", "examples"}:
        path = rubric if target == "rubric" else examples
        path.write_bytes(path.read_bytes() + b" ")
        locks[str(path.relative_to(root))] = sha(path)
        frozen.write_text(json.dumps(locks))
        if target == "rubric":
            releases["test-published"]["sha256"] = sha(path)
            registry.write_text(json.dumps(releases))
    elif target == "registry":
        releases["test-published"]["status"] = "draft"
        registry.write_text(json.dumps(releases))
    else:
        releases.pop("test-published")
        registry.write_text(json.dumps(releases))
    with pytest.raises(ValueError, match="Frozen lock entry changed|Rubric publication entry changed"):
        check(root, base_ref="HEAD")
