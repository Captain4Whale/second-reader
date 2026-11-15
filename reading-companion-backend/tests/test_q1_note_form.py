from copy import deepcopy
import pytest

from scripts.q1_rubric_form import load_form
from scripts.q1_note_form import validate_form, STEPS


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
