from copy import deepcopy
import pytest

from scripts.q1_rubric_form import load_form
from scripts.q1_note_form import validate_form, STEPS, FORM_V1, FORM_V2, FIRST_PASS, REWRITE


def test_new_form_is_registered_and_note_only():
    form, digest = load_form("q1-v3.4.form.v1")
    assert len(digest) == 64
    assert form["mark_types"] == ["N"]
    assert [s["id"] for s in form["steps"]] == list(STEPS)
    assert form["choices"]["failure_types"][-1] == "其他"


@pytest.mark.parametrize("change", ["order", "highlight", "choice", "policy"])
def test_protocol_changes_require_new_implementation(change):
    form = deepcopy(load_form("q1-v3.4.form.v1")[0])
    if change == "order":
        form["steps"][2:4] = reversed(form["steps"][2:4])
    elif change == "highlight":
        form["mark_types"].append("H")
    elif change == "choice":
        form["choices"]["following_text_use"].pop()
    else:
        form["policy"]["uncovered_fails"] = False
    with pytest.raises(ValueError):
        validate_form(form)


def test_v2_is_a_new_frozen_form_and_v1_identity_is_unchanged():
    from hashlib import sha256
    from pathlib import Path
    import json
    backend = Path(__file__).resolve().parents[1]
    old, old_hash = load_form(FORM_V1)
    new, digest = load_form(FORM_V2)
    assert old_hash == "4943a37bf0065d05248535e572e3842e2c5c69f996d7d3c6d8ce2cbbb4d07b84"
    assert new["rubric_sha256"] == old["rubric_sha256"]
    assert new["annotation_guide_sha256"] == old["annotation_guide_sha256"]
    assert new["choices"]["first_pass"] == list(FIRST_PASS)
    assert new["choices"]["rewrite"] == list(REWRITE)
    assert "reading_difficulty" not in new["choices"]
    assert digest == sha256((backend / f"rubric/{FORM_V2}.json").read_bytes()).hexdigest()
    assert json.loads((backend / "experiments/frozen.json").read_text())[f"rubric/{FORM_V2}.json"] == digest


@pytest.mark.parametrize("field", ["first_pass", "rewrite"])
def test_v2_rejects_missing_branch_choices(field):
    form = deepcopy(load_form(FORM_V2)[0])
    form["choices"][field].pop()
    with pytest.raises(ValueError, match="选项"):
        validate_form(form)
