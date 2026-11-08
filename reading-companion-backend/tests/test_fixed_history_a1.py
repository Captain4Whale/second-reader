import json
from pathlib import Path

import pytest

from scripts import run_fixed_history_a1 as a1


def test_note_average_excludes_anchors_highlights_and_counts_unicode_codepoints():
    marks = [{"kind": "note", "content": "  甲乙。  ", "source_quote": "a long source quote"},
             {"kind": "note", "content": "🌱?", "source_quote": "another long quote"},
             {"kind": "highlight", "content": "", "source_quote": "very long highlight"}]
    stats = a1.mark_statistics(marks)
    assert (stats["total"], stats["H"], stats["N"]) == (3, 1, 2)
    assert stats["note_characters"] == 5
    assert stats["mean_note_length"] == 2.5
    assert stats["question_marks"] == 1
    assert a1.mark_statistics(marks[-1:])["mean_note_length"] is None


def test_failed_memory_check_stops_before_model_invocation(tmp_path, monkeypatch):
    class History:
        def verify_memory_selection(self, packet):
            raise ValueError("memory order mismatch")

    work = tmp_path / "A1-full"
    (work / "preflight/bovary").mkdir(parents=True)
    (work / "source-files-before.json").write_text("{}")
    (work / "preflight/bovary/u000006.json").write_text("{}")
    monkeypatch.setattr(a1, "load_histories", lambda _: {"bovary": History()})
    monkeypatch.setattr(a1, "fingerprint", lambda _: {})
    monkeypatch.setattr(a1, "selected_units", lambda: [("bovary", "synthetic-run", "u000006")])
    called = []
    monkeypatch.setattr(a1, "run_digest", lambda *a, **kw: called.append(1))
    with pytest.raises(ValueError, match="memory order"):
        a1.execute(Path("unused"), tmp_path)
    assert not called
    assert json.loads((work / "status.json").read_text())["phase"] == "stopped"
