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
