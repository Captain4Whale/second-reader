import json
import subprocess
import sys
from copy import deepcopy

import pytest

from tests.test_q1_scoring import scoring  # noqa: F401
from scripts.q1_experiment_index import BACKEND, families, render


def test_latest_only_table_history_folded_and_drift_check(scoring):  # noqa: F811
    root, row = scoring
    new = {**deepcopy(row), "scoring_id": "S2", "supersedes": "S1"}
    (root / "experiments/scorings.jsonl").write_text(
        "".join(json.dumps(x) + "\n" for x in [row, new])
    )
    output = render(root)
    top = output.split("以下小节")[0]
    assert "#s2" in top and "#s1" not in top
    assert "历史评分快照（1 条）" in output and "<summary>测试 · S1</summary>" in output
    path = root / "experiments/INDEX.md"
    path.write_text(output)
    command = [
        sys.executable,
        str(BACKEND / "scripts/q1_experiment_index.py"),
        "--root",
        str(root),
        "--check",
    ]
    assert subprocess.run(command, capture_output=True).returncode == 0
    path.write_text(output + "drift\n")
    assert subprocess.run(command, capture_output=True).returncode != 0


def test_experiment_addenda_merge_and_bad_links_reject():
    rows = [
        {"experiment_id": "E"},
        {"experiment_id": "E2", "continuation_of": "E"},
        {"experiment_id": "E3", "amends_experiment_id": "E2"},
    ]
    assert len(families(rows)["E"]) == 3
    with pytest.raises(ValueError, match="linkage"):
        families([{"experiment_id": "E", "amends_experiment_id": "missing"}])


def test_owner_correction_is_visible_and_original_closure_is_historical(scoring):  # noqa: F811
    root, score = scoring
    (root / "experiments/scorings.jsonl").write_text(json.dumps(score) + "\n")
    closing = {
        "experiment_id": "C",
        "amends_experiment_id": "E",
        "record_type": "experiment_closure",
        "conclusion": "旧结论：标准漂移。",
    }
    addendum = {
        "experiment_id": "A",
        "amends_experiment_id": "C",
        "record_type": "owner_verification_addendum",
        "date": "2026-11-11",
        "conclusion": "不是标准漂移，是规则未写明加一次误操作。",
        "results": {
            "cases": [
                {"book": "测试书", "unit_id": "u1", "finding": "旧判定是误操作。"}
            ]
        },
    }
    log = root / "experiments/log.jsonl"
    with log.open("a") as stream:
        for row in (closing, addendum):
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    protected = {p: p.read_bytes() for p in (log, root / "experiments/scorings.jsonl")}
    output = render(root)
    top = output.split("| 评分／单元 |")[0]
    assert addendum["conclusion"] in top and "`A`" in top
    assert closing["conclusion"] not in top
    assert "测试书 `u1`：旧判定是误操作。" in output
    assert output.index(addendum["conclusion"]) < output.index(closing["conclusion"])
    assert "<summary>原收尾记录（历史原文；后续核对见上文）</summary>" in output
    assert all(p.read_bytes() == raw for p, raw in protected.items())


def test_without_owner_addendum_does_not_invent_a_correction(scoring):  # noqa: F811
    root, score = scoring
    (root / "experiments/scorings.jsonl").write_text(json.dumps(score) + "\n")
    with (root / "experiments/log.jsonl").open("a") as stream:
        stream.write(
            json.dumps(
                {
                    "experiment_id": "C",
                    "amends_experiment_id": "E",
                    "record_type": "experiment_closure",
                    "conclusion": "原始收尾结论",
                }
            )
            + "\n"
        )
    output = render(root)
    assert "原始收尾结论" in output
    assert "所有者补充核对" not in output
    assert "标准有漂移" not in output


def test_converted_human_results_without_a_form_are_labeled_and_rendered(scoring):  # noqa: F811
    from scripts.q1_adjudicated_conversion import BASIS, conversion_counts

    root, row = scoring
    releases = json.loads((root / "rubric/releases.json").read_text())
    row["rubric"] = {
        "version": "q1-v2",
        "sha256": releases["q1-v2"]["sha256"],
        "form_version": None,
        "form_sha256": None,
    }
    row["inputs"]["kind"] = "adjudicated_conversion"
    row["calculation"].update(method="q1-v1_plus_owner_adjudication_to_v2", basis=BASIS)
    row["results"][0]["counts"] = conversion_counts(
        [
            {
                "type": "N",
                "judgment": "pass",
                "core": {"judgment": "pass"},
                "vetoes": [],
                "tags": ["empty_talk"],
                "clean_pass": False,
                "needs_verification": False,
            }
        ]
    )
    (root / "experiments/scorings.jsonl").write_text(json.dumps(row) + "\n")
    output = render(root)
    assert "q1-v2 结构换算<br>无表单" in output
    assert BASIS in output and "Note 干净通过率：0/1（0.00%）" in output
    assert "有空话 1" in output
