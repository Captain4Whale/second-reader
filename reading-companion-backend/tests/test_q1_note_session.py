from copy import deepcopy
import json
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from scripts import q1_note_session as mod
from scripts.q1_note_form import validate_assessment, DIFFICULTY
from scripts.q1_note_context import fingerprint, contexts, point
from scripts.q1_note_review import server
from scripts.q1_rubric_form import load_form


@pytest.fixture
def store(tmp_path, monkeypatch):
    form, form_hash = load_form(mod.FORM)
    form_bytes = (mod.BACKEND / "rubric/q1-v3.4.form.v1.json").read_bytes()
    monkeypatch.setattr(mod, "BACKEND", tmp_path)
    folder = tmp_path / "state/session"
    folder.mkdir(parents=True)
    span = dict(start=point(1, 1, 0), end=point(1, 1, 4))
    case = dict(
        record_id="anonymous-note",
        window_id="window",
        unit_key="window",
        book_key="book",
        book="测试书",
        chapter_title="一",
        body_text="测试批注",
        source_quote="虚构原文",
        original_source_range=span,
        context=dict(
            prefix=[dict(text="虚构原文", anchor=True, range=span)],
            earlier=[],
            within_unit=[
                dict(
                    text="后文",
                    anchor=False,
                    range=dict(start=point(1, 1, 4), end=point(1, 1, 6)),
                )
            ],
            after_unit=[],
            original_notes=dict(status="unresolved", items=[]),
            observer_cutoff=span["end"],
        ),
    )
    manifest = dict(
        schema="q1-note-session/1",
        review_session_id="test-session",
        session_purpose="test",
        batch_id="test-batch",
        annotator_id="test-human",
        rubric_version=form["rubric_version"],
        rubric_sha256=form["rubric_sha256"],
        annotation_guide_sha256=form["annotation_guide_sha256"],
        rubric_form_version=mod.FORM,
        rubric_form_sha256=form_hash,
        randomization=dict(
            seed=7,
            algorithm="sha256-sort-v1",
            order_sha256=fingerprint([case["record_id"]]),
        ),
        context_sha256=fingerprint([case]),
        record_ids=[case["record_id"]],
        total_notes=1,
    )
    for name, value in [("manifest.json", manifest), ("context.json", [case])]:
        (folder / name).write_bytes(mod.encoded(value))
    (folder / "rubric-form.json").write_bytes(form_bytes)
    for name in ("judgments.jsonl", "progress.jsonl"):
        (folder / name).touch()
    return mod.Store(folder)


def act(store, action, values=None):
    state = store.state("anonymous-note")
    return store.action(
        "anonymous-note",
        action,
        values,
        version=state["version"] if state else None,
        active_ms=20,
    )


def to_n1(store, difficulty=DIFFICULTY[0]):
    act(store, "open")
    act(store, "complete", {"judgment": "pass"})
    act(store, "complete", {"choice": difficulty})


def to_conclusion(store, n1=None, difficulty=DIFFICULTY[0]):
    to_n1(store, difficulty)
    act(
        store,
        "complete",
        {
            "n1": n1
            or dict(following_text_use="没用到", judgment="pass", writing_style="补充")
        },
    )
    act(store, "complete", {"spoiler": False})
    act(store, "complete", {"incorrect_information": False, "needs_verification": True})


def finish(store):
    act(store, "complete")
    return act(store, "submit")["record"]


@pytest.mark.parametrize("field", ["seed", "snapshot_sha256", "observer_cutoff"])
def test_reader_rejects_altered_context_or_randomization(store, field):
    to_conclusion(store)
    finish(store)
    journal = store.read_judgments()
    if field == "seed":
        journal[-1]["randomization"][field] = 99
    else:
        journal[-1]["context"][field] = "altered"
    (store.folder / "judgments.jsonl").write_bytes(
        b"".join(mod.encoded(row) for row in journal)
    )
    with pytest.raises(ValueError, match="随机顺序或上下文身份"):
        mod.Store(store.folder)


def test_session_rejects_mismatched_rubric_identity(store):
    manifest = deepcopy(store.manifest)
    manifest["rubric_version"] = "q1-v0"
    (store.folder / "manifest.json").write_bytes(mod.encoded(manifest))
    with pytest.raises(ValueError, match="rubric 身份"):
        mod.Store(store.folder)


def test_first_impression_lock_survives_reload_and_rejects_skips(store):
    act(store, "open")
    with pytest.raises(ValueError, match="请选择第一印象"):
        act(store, "complete")
    act(store, "complete", {"judgment": "pass"})
    store = mod.Store(store.folder)
    with pytest.raises(ValueError, match="锁定项"):
        act(store, "save", {"judgment": "fail"})
    with pytest.raises(ValueError, match="只有 N1"):
        act(store, "following", {"scope": "within_unit"})
    with pytest.raises(ValueError, match="按顺序"):
        act(store, "submit")
    assert not store.read_judgments()


def test_difficulty_amendment_final_value_and_all_transitions(store):
    to_conclusion(store)
    first = deepcopy(
        store.state("anonymous-note")["record"]["steps"]["reading_difficulty"]
    )
    act(store, "amend", {"choice": DIFFICULTY[1]})
    assert store.state("anonymous-note")["record"]["judgment"] == "fail"
    act(store, "amend", {"choice": DIFFICULTY[2]})
    r = store.state("anonymous-note")["record"]
    assert r["judgment"] == "pass" and r["unsure_sources"] == {
        "读着费劲": ["automatic"]
    }
    act(store, "amend", {"choice": DIFFICULTY[0]})
    r = finish(store)
    assert r["reading_difficulty"]["original_choice"] == DIFFICULTY[0]
    assert [a["to"] for a in r["reading_difficulty"]["amendments"]] == [
        DIFFICULTY[1],
        DIFFICULTY[2],
        DIFFICULTY[0],
    ]
    assert r["steps"]["reading_difficulty"] == first
    assert r["unsure"] == [] and r["needs_verification"] and r["judgment"] == "pass"


def test_manual_and_automatic_uncertainty_are_separate(store):
    to_n1(store, DIFFICULTY[2])
    r = act(store, "save", {"manual_unsure": True})["record"]
    assert r["unsure_sources"] == {"读着费劲": ["automatic"], "N1": ["manual"]}


def test_following_exposure_is_per_step_and_survives_reopen(store):
    to_n1(store)
    act(store, "following", {"scope": "within_unit"})
    act(
        store,
        "complete",
        {
            "n1": dict(
                following_text_use="挂早了", judgment="pass", writing_style="解读"
            )
        },
    )
    assert not store.state("anonymous-note")["record"]["steps"]["spoiler"][
        "viewed_following_text"
    ]
    act(store, "following", {"scope": "within_unit"})
    act(store, "complete", {"spoiler": False})
    act(store, "complete", {"incorrect_information": False})
    r = finish(store)
    assert r["tags"] == ["锚点问题"]
    act(store, "reopen")
    assert store.state("anonymous-note")["record"]["steps"]["n1"][
        "viewed_following_text"
    ]


def test_uncovered_clears_tags_star_and_requires_reason(store):
    to_conclusion(store)
    act(store, "complete")
    act(store, "save", {"tags": ["有空话"], "star": True})
    r = act(store, "save", {"rubric_uncovered": True})["record"]
    assert r["judgment"] == "fail" and "tags" not in r and not r["star"]
    with pytest.raises(ValueError, match="未覆盖必须"):
        act(store, "submit")
    r = act(store, "submit", {"uncovered_reason": "新问题"})["record"]
    assert "tags" not in r


def test_n1_failure_still_requires_both_veto_steps(store):
    to_n1(store)
    r = act(
        store,
        "complete",
        {
            "n1": dict(
                following_text_use="紧接着几段", judgment="fail", failure_types=[]
            )
        },
    )
    assert r["stage"] == 3 and r["record"]["n1"]["failure_types"] == ["下文马上讲了"]
    with pytest.raises(ValueError, match="按顺序"):
        act(store, "submit")
    act(store, "complete", {"spoiler": True})
    act(store, "complete", {"incorrect_information": True})
    r = finish(store)
    assert (
        r["vetoes"]["spoiler"]
        and r["vetoes"]["incorrect_information"]
        and "tags" not in r
    )


@pytest.mark.parametrize(
    "n,match",
    [
        ({}, "后文"),
        (dict(following_text_use="没用到", judgment="pass"), "写法"),
        (
            dict(
                following_text_use="没用到", judgment="pass", writing_style="其他写法"
            ),
            "增量",
        ),
        (dict(following_text_use="没用到", judgment="fail", failure_types=[]), "至少"),
        (
            dict(following_text_use="没用到", judgment="fail", failure_types=["其他"]),
            "说明",
        ),
        (
            dict(
                following_text_use="没用到",
                judgment="pass",
                writing_style="补充",
                failure_types=["没新东西"],
            ),
            "同时",
        ),
    ],
)
def test_required_and_mutually_exclusive_n1_fields(store, n, match):
    to_n1(store)
    with pytest.raises(ValueError, match=match):
        act(store, "complete", {"n1": n})


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(judgment="fail"),
        lambda r: r["vetoes"].update(reading_difficulty=True),
        lambda r: r["steps"].pop("spoiler"),
        lambda r: r.update(rubric_uncovered=True, uncovered_reason=""),
        lambda r: r["reading_difficulty"].update(original_choice=DIFFICULTY[1]),
    ],
)
def test_reader_rejects_invalid_records(store, mutate):
    to_conclusion(store)
    r = finish(store)
    mutate(r)
    with pytest.raises((ValueError, KeyError)):
        validate_assessment(r)


def test_append_only_revision_recovery_and_stale_browser(store):
    to_conclusion(store)
    first = finish(store)
    prefix = (store.folder / "judgments.jsonl").read_bytes()
    act(store, "amend", {"choice": DIFFICULTY[1]})
    second = finish(store)
    assert (
        second["judgment"] == "fail"
        and second["supersedes_revision"] == first["revision"]
    )
    assert (store.folder / "judgments.jsonl").read_bytes().startswith(prefix)
    with pytest.raises(ValueError, match="过期"):
        store.action("anonymous-note", "reopen", version=0)
    # Simulate crash after journal fsync but before its progress event was appended.
    progress = mod.rows(store.folder / "progress.jsonl")
    (store.folder / "progress.jsonl").write_bytes(
        b"".join(mod.encoded(x) for x in progress[:-1])
    )
    recovered = mod.Store(store.folder).state("anonymous-note")
    assert recovered["stage"] == 7 and recovered["record"] == second


def test_upstream_unit_note_updates_do_not_rewrite_mark_records(store):
    to_conclusion(store)
    finish(store)
    prefix = (store.folder / "judgments.jsonl").read_bytes()
    store.unit_note("window", "上游：混入注释")
    store.unit_note("window", "已核查，不排除")
    journal = store.read_judgments()
    assert journal[-2]["upstream_excluded"] and not journal[-1]["upstream_excluded"]
    assert journal[-1]["supersedes_revision"] == journal[-2]["revision"]
    assert (store.folder / "judgments.jsonl").read_bytes().startswith(prefix)


def test_http_does_not_send_following_before_allowed_step_and_checks_origin(store):
    srv = server(store, 0)
    thread = Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    root = f"http://127.0.0.1:{srv.server_port}"
    try:
        req = Request(
            root + "/action",
            data=json.dumps(dict(id="anonymous-note", action="open")).encode(),
            headers={"Content-Type": "application/json", "Origin": root},
        )
        response = json.load(urlopen(req))
        assert "following" not in response and "context" not in response["case"]
        req = Request(
            root + "/action",
            data=b"{}",
            headers={
                "Content-Type": "application/json",
                "Origin": "https://example.org",
            },
        )
        with pytest.raises(HTTPError):
            urlopen(req)
        with pytest.raises(HTTPError):
            urlopen(root + "/context.json")
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join()


def test_anchor_splits_same_paragraph_and_following_stops_at_chapter():
    class Source:
        doc = {
            "chapters": [
                {"id": 1, "paragraphs": [{"paragraph_index": 1, "text": "此前"}]},
                {
                    "id": 2,
                    "paragraphs": [
                        {"paragraph_index": 1, "text": "前😀锚后文"},
                        {"paragraph_index": 2, "text": "章末"},
                    ],
                },
                {"id": 3, "paragraphs": [{"paragraph_index": 1, "text": "不得提供"}]},
            ]
        }

        def notes(self, parts):
            return {"status": "unresolved", "items": []}

    window = {"original_source_range": dict(start=point(2, 1, 0), end=point(2, 1, 5))}
    mark = {
        "original_source_range": dict(start=point(2, 1, 1), end=point(2, 1, 3)),
        "source_quote": "😀锚",
    }
    ctx = contexts(Source(), window, mark)
    assert "".join(p["text"] for p in ctx["prefix"]) == "前😀锚"
    assert "".join(p["text"] for p in ctx["within_unit"]) == "后文"
    assert "".join(p["text"] for p in ctx["after_unit"]) == "章末"
    assert "".join(p["text"] for p in ctx["earlier"]) == "此前"


def test_notes_use_actual_links_not_independently_deduplicated_metadata():
    from xml.etree import ElementTree as ET
    from scripts.q1_note_context import BookSource

    source = object.__new__(BookSource)
    source.xml = {
        "text/chapter.html": ET.fromstring("""<html><body>
      <p>正文<a href="chapter.html#note1" id="ref1">[1]</a></p>
      <p><a href="chapter.html#ref1" id="note1">[1]</a>原书注释</p>
      </body></html>""")
    }
    p = dict(
        href="text/chapter.html",
        text="正文[1]",
        inline_anchor_hrefs=["wrong#wrong"],
        inline_anchor_texts=["[9]"],
    )
    result = source.notes([(p, "正文[1]")])
    assert (
        result["status"] == "resolved" and result["items"][0]["text"] == "[1]原书注释"
    )
    assert source.notes([(p, "正文")])["items"] == []  # Later marker stays hidden.
    source.xml = {}
    assert source.notes([(p, "正文[1]")]) == {"status": "unresolved", "items": []}


def test_conflicting_original_note_targets_stop_instead_of_guessing():
    from xml.etree import ElementTree as ET
    from scripts.q1_note_context import BookSource, UnreliableNotesError

    source = object.__new__(BookSource)
    source.xml = {
        "text/c.html": ET.fromstring(
            '<html><p>正文<a id="r" href="#n">[1]</a></p><p id="n">一</p><p id="n">二</p></html>'
        )
    }
    with pytest.raises(UnreliableNotesError):
        source.notes([(dict(href="text/c.html", text="正文[1]"), "正文[1]")])


def test_unresolved_note_target_does_not_block():
    from xml.etree import ElementTree as ET
    from scripts.q1_note_context import BookSource

    source = object.__new__(BookSource)
    source.xml = {
        "text/c.html": ET.fromstring(
            '<html><p>正文<a id="r" href="#missing">[1]</a></p></html>'
        )
    }
    result = source.notes([(dict(href="text/c.html", text="正文[1]"), "正文[1]")])
    assert result["status"] == "unresolved" and result["items"][0]["text"] == ""


def test_failed_record_cannot_carry_even_empty_tags_or_star(store):
    to_conclusion(store, difficulty=DIFFICULTY[1])
    r = finish(store)
    for changes in ({"tags": []}, {"star": True}):
        with pytest.raises(ValueError, match="标签或星"):
            validate_assessment({**r, **changes})


def test_first_impression_and_exposure_cannot_be_changed_in_later_record(store):
    to_n1(store)
    act(store, "following", {"scope": "within_unit"})
    act(
        store,
        "complete",
        {
            "n1": dict(
                following_text_use="没用到", judgment="pass", writing_style="补充"
            )
        },
    )
    act(store, "complete")
    act(store, "complete")
    r = finish(store)
    altered = deepcopy(r)
    altered["first_impression"]["judgment"] = "fail"
    with pytest.raises(ValueError, match="第一印象已经锁定"):
        validate_assessment(altered, r)
    altered = deepcopy(r)
    altered["steps"]["n1"].update(viewed_following_text=False, following_text_views=[])
    with pytest.raises(ValueError, match="撤销后文暴露"):
        validate_assessment(altered, r)


def test_other_style_valid_and_clean_nonclean_tags_remain_explicit(store):
    to_conclusion(
        store,
        n1=dict(
            following_text_use="更远后文，转第四步判剧透",
            judgment="pass",
            writing_style="其他写法",
            other_writing_explanation="明确的语言增量",
        ),
    )
    act(store, "complete")
    r = act(store, "submit", {"tags": ["老师口吻", "锚点问题"]})["record"]
    assert r["judgment"] == "pass" and r["n1"]["writing_style"] == "其他写法"
    assert r["tags"] == ["老师口吻", "锚点问题"]


def test_partial_jsonl_tail_stops_without_rewriting(store):
    to_n1(store)
    path = store.folder / "progress.jsonl"
    with path.open("ab") as f:
        f.write(b"{")
    original = path.read_bytes()
    with pytest.raises(ValueError, match="日志末尾不完整"):
        act(store, "save")
    assert path.read_bytes() == original


@pytest.mark.parametrize("form_version", [mod.FORM_V1, mod.FORM_V2])
def test_prepare_filters_notes_without_mutating_source_and_reproduces_order(
    tmp_path, monkeypatch, form_version
):
    real_backend = mod.BACKEND
    monkeypatch.setattr(mod, "BACKEND", tmp_path)
    (tmp_path / "rubric").mkdir()
    (tmp_path / f"rubric/{form_version}.json").write_bytes(
        (real_backend / f"rubric/{form_version}.json").read_bytes()
    )
    source = tmp_path / "source"
    source.mkdir()
    (source / "mixed.json").write_text("{}\n")
    (source / "judgments.jsonl").write_text("")
    c = dict(
        window_id="w",
        book="虚构书",
        chapter_title="第一章",
        marginalia=[
            dict(
                marginalia_id=f"item-{i}",
                type="H" if i == 0 else "N",
                body_text="批注",
                source_quote="原文",
                original_source_range=dict(start=point(1, 1, 0), end=point(1, 1, 2)),
            )
            for i in range(5)
        ],
    )
    canonical = dict(
        sources=[dict(source_id="s", epub_sha256="epub", substrate_sha256="substrate")],
        windows=[dict(window_id="w", source_id="s")],
    )
    mixed = dict(batch_id="batch", windows=[c])
    monkeypatch.setattr(mod, "load_bundle", lambda _: (canonical, mixed, {}))

    class Book:
        epub_sha256 = "epub"
        substrate_sha256 = "substrate"
        document_sha256 = "document"

        def __init__(self, _):
            pass

    monkeypatch.setattr(mod, "BookSource", Book)
    monkeypatch.setattr(mod, "contexts", lambda *args: {})
    before = deepcopy(mixed)
    options = {"form_version": form_version} if form_version == mod.FORM_V1 else {}
    a = mod.prepare(source, tmp_path / "state/a", ["book"], seed=31, **options)
    b = mod.prepare(source, tmp_path / "state/b", ["book"], seed=31, **options)
    assert a["rubric_form_version"] == form_version
    assert (tmp_path / "state/a/rubric-form.json").read_bytes() == (real_backend / f"rubric/{form_version}.json").read_bytes()
    if form_version == mod.FORM_V2:
        with pytest.raises(ValueError, match="离线 HTML"):
            mod.Store(tmp_path / "state/a").action(a["record_ids"][0], "open")
        assert (tmp_path / "state/a/progress.jsonl").read_bytes() == b""
    assert a["record_ids"] == b["record_ids"] and a["total_notes"] == 4
    assert "item-0" not in a["record_ids"] and mixed == before
    assert (source / "judgments.jsonl").read_bytes() == b""
    with pytest.raises(ValueError, match="目录已存在"):
        mod.prepare(source, tmp_path / "state/a", ["book"])
    with pytest.raises(ValueError, match="只能写入 test"):
        mod.prepare(source, tmp_path / "state/c", ["book"], mark_ids=["item-1"])


@pytest.mark.parametrize("target", [2, 3, 4])
def test_correct_completed_step_before_submission(store, target):
    to_conclusion(store)
    before = deepcopy(store.state("anonymous-note")["record"])
    state = act(store, "reopen", {"step": target})
    assert state["stage"] == target
    assert state["record"]["first_impression"] == before["first_impression"]
    assert state["record"]["reading_difficulty"] == before["reading_difficulty"]
    assert state["record"]["n1"] == before["n1"]
    for key in mod.STEPS[target:]:
        assert "completed_at" not in state["record"]["steps"][key]
    with pytest.raises(ValueError, match="顺序"):
        act(store, "submit")
    assert store.read_judgments() == []


def test_midflow_n1_correction_preserves_exposure_and_append_history(store):
    to_n1(store)
    act(store, "following", {"scope": "within_unit"})
    act(store, "complete", {"n1": dict(following_text_use="没用到", judgment="fail", failure_types=["下文马上讲了"])})
    exposure = deepcopy(store.state("anonymous-note")["record"]["steps"]["n1"]["following_text_views"])
    state = act(store, "reopen", {"step": 2})
    assert state["record"]["steps"]["n1"]["following_text_views"] == exposure
    act(store, "complete", {"n1": dict(following_text_use="没用到", judgment="pass", writing_style="补充")})
    act(store, "complete", {"spoiler": False})
    act(store, "complete", {"incorrect_information": False})
    finish(store)
    prefix = (store.folder / "judgments.jsonl").read_bytes()
    act(store, "reopen", {"step": 3})
    act(store, "complete", {"spoiler": True})
    act(store, "complete", {"incorrect_information": False})
    result = finish(store)
    assert result["judgment"] == "fail"
    assert result["supersedes_revision"] == 1
    assert (store.folder / "judgments.jsonl").read_bytes().startswith(prefix)
    assert result["steps"]["n1"]["following_text_views"] == exposure


@pytest.mark.parametrize("target", [0, 5, 6, 7, -1, 2.5, "2", True])
def test_correction_cannot_unlock_protected_or_future_steps(store, target):
    to_conclusion(store)
    with pytest.raises(ValueError, match="只能返回"):
        act(store, "reopen", {"step": target})


def test_difficulty_correction_immediately_after_step_two(store):
    to_n1(store)
    original = store.state("anonymous-note")["record"]["reading_difficulty"]["choice"]
    state = act(store, "amend", {"choice": DIFFICULTY[1]})
    assert state["stage"] == 2
    assert state["record"]["reading_difficulty"]["original_choice"] == original
    assert state["record"]["vetoes"]["reading_difficulty"] is True
    state = act(store, "amend", {"choice": DIFFICULTY[2]})
    assert state["record"]["vetoes"]["reading_difficulty"] is False
    assert state["record"]["reading_difficulty"]["amendments"][-1]["from"] == DIFFICULTY[1]


def test_return_to_original_difficulty_form_preserves_history_and_old_submission(store):
    to_conclusion(store)
    finish(store)
    prefix = (store.folder / "judgments.jsonl").read_bytes()
    first = deepcopy(store.state("anonymous-note")["record"]["first_impression"])
    act(store, "reopen", {"step": 1})
    act(store, "save", {"choice": DIFFICULTY[1], "paraphrase": "复述", "rewrite": "改写"})
    act(store, "save", {"choice": DIFFICULTY[1]})
    act(store, "save", {"choice": DIFFICULTY[2], "manual_unsure": True})
    state = act(store, "complete", {"choice": DIFFICULTY[0], "manual_unsure": True})
    assert state["stage"] == 2
    d = state["record"]["reading_difficulty"]
    assert d["original_choice"] == DIFFICULTY[0]
    assert [(a["from"], a["to"]) for a in d["amendments"]] == [
        (DIFFICULTY[0], DIFFICULTY[1]), (DIFFICULTY[1], DIFFICULTY[2]), (DIFFICULTY[2], DIFFICULTY[0])]
    for _ in range(3):
        act(store, "complete")
    result = finish(store)
    assert result["judgment"] == "pass"
    assert result["first_impression"] == first
    assert result["unsure_sources"]["读着费劲"] == ["manual"]
    assert result["supersedes_revision"] == 1
    assert (store.folder / "judgments.jsonl").read_bytes().startswith(prefix)


def v2_record(store, *, previous=False):
    to_conclusion(store)
    old = deepcopy(finish(store))
    row = deepcopy(old)
    row.update(rubric_form_version=mod.FORM_V2, rubric_form_sha256=load_form(mod.FORM_V2)[1],
               annotator_version="q1-annotator/3.6", event_schema_version=2, event_version=2 ** 32,
               checks={"spoiler": False, "incorrect_information": False},
               legacy_inferences=[], acknowledged_warnings=[])
    row["reading_difficulty"] = dict(first_pass="复述得出",
        locked_at=old["steps"]["reading_difficulty"]["completed_at"],
        paraphrase=old["reading_difficulty"]["paraphrase"], rewrite_judgment=None, rewrite_text="",
        veto=False, amendments=[])
    if previous:
        row.update(revision=2, supersedes_revision=1, event_version=2 ** 32,
                   amendment_kind="post_discussion", amendment_reason="讨论后确认说明",
                   legacy_reading_difficulty=deepcopy(old["reading_difficulty"]),
                   legacy_inferences=["第一遍判断来自首条旧记录，不是新观察"])
    return row, old


def test_reader_accepts_real_v2_append_under_unchanged_v1_manifest(store):
    row, old = v2_record(store, previous=True)
    journal = store.folder / "judgments.jsonl"
    before = journal.read_bytes()
    manifest = (store.folder / "manifest.json").read_bytes()
    mod.append(journal, row)
    _, result = mod.read_note_review(store.folder)
    assert result == [old, row]
    assert journal.read_bytes().startswith(before)
    assert (store.folder / "manifest.json").read_bytes() == manifest
    with pytest.raises(ValueError, match="离线 HTML"):
        act(store, "open")


@pytest.mark.parametrize("field,value", [
    ("rubric_form_sha256", "0" * 64), ("rubric_form_version", "q1-v3.4.form.v99"),
    ("session_manifest_sha256", "0" * 64), ("rubric_sha256", "0" * 64),
    ("annotation_guide_sha256", "0" * 64),
])
def test_reader_rejects_v2_identity_shortcuts(store, field, value):
    row, _ = v2_record(store, previous=True)
    row[field] = value
    mod.append(store.folder / "judgments.jsonl", row)
    with pytest.raises(ValueError, match="身份"):
        store.read_judgments()


@pytest.mark.parametrize("field", ["first_pass", "locked_at", "paraphrase"])
def test_v2_first_pass_evidence_is_immutable(store, field):
    row, _ = v2_record(store)
    previous = deepcopy(row)
    row.update(amendment_kind="post_discussion", amendment_reason="讨论后修正", supersedes_revision=1,
               revision=2, event_version=previous["event_version"] + 1)
    if field == "first_pass":
        row["reading_difficulty"][field] = "复述不出或说偏"
        row["reading_difficulty"]["rewrite_judgment"] = "改写不出"
        from scripts.q1_note_form import derive
        derive(row)
    elif field == "locked_at":
        row["reading_difficulty"][field] = "2099-01-01T00:00:00Z"
    else:
        row["reading_difficulty"][field] = "事后改写复述"
    with pytest.raises(ValueError, match="第一遍"):
        validate_assessment(row, previous)


@pytest.mark.parametrize("field", ["spoiler", "incorrect_information"])
@pytest.mark.parametrize("value", [None, "false", 0])
def test_v2_requires_explicit_boolean_checks(store, field, value):
    row, _ = v2_record(store)
    row["checks"][field] = value
    with pytest.raises(ValueError, match="明确判断"):
        validate_assessment(row)


def test_v2_rewrite_amendments_and_auto_manual_uncertainty(store):
    from scripts.q1_note_form import derive
    row, _ = v2_record(store)
    d = row["reading_difficulty"]
    d.update(first_pass="复述不出或说偏", rewrite_judgment="能改写得更直白")
    derive(row)
    row["steps"]["tags"] = {"status": "skipped_due_to_fail"}
    assert validate_assessment(row)["judgment"] == "fail"
    previous = deepcopy(row)
    row.update(amendment_kind="post_discussion", amendment_reason="讨论后确认表达已清楚",
               supersedes_revision=1, revision=2, event_version=row["event_version"] + 1)
    d["rewrite_judgment"] = "改写不出"
    d["amendments"].append({"from": "能改写得更直白", "to": "改写不出", "at": mod.now(), "reason": "讨论后确认", "active_ms": 4})
    row["unsure_sources"]["读着费劲"] = ["manual"]
    derive(row)
    row["steps"]["tags"] = deepcopy(row["steps"]["conclusion"])
    assert validate_assessment(row, previous)["judgment"] == "pass"
    assert row["unsure_sources"]["读着费劲"] == ["automatic", "manual"]
    d["amendments"][0]["from"] = None
    with pytest.raises(ValueError, match="不连续"):
        validate_assessment(row, previous)


@pytest.mark.parametrize("branch,valid", [("没用到", False), ("紧接着几段", True), ("挂早了", True), ("更远后文，转第四步判剧透", False)])
def test_v2_immediate_following_failure_is_branch_limited(store, branch, valid):
    from scripts.q1_note_form import derive
    row, _ = v2_record(store)
    row["n1"] = {"following_text_use": branch, "judgment": "fail", "failure_types": ["下文马上讲了"]}
    row["acknowledged_warnings"] = ["far_following_without_spoiler"]
    derive(row)
    row["steps"]["tags"] = {"status": "skipped_due_to_fail"}
    if valid:
        validate_assessment(row)
    else:
        with pytest.raises(ValueError, match="只适用于"):
            validate_assessment(row)


def test_v2_far_following_without_spoiler_requires_acknowledgement(store):
    row, _ = v2_record(store)
    row["n1"]["following_text_use"] = "更远后文，转第四步判剧透"
    with pytest.raises(ValueError, match="确认提醒"):
        validate_assessment(row)
    row["acknowledged_warnings"] = ["far_following_without_spoiler"]
    validate_assessment(row)


@pytest.mark.parametrize("field,value", [("amendment_kind", "correction"), ("amendment_reason", " ")])
def test_v2_submitted_revision_requires_discussion_marker_and_reason(store, field, value):
    row, old = v2_record(store, previous=True)
    row[field] = value
    with pytest.raises(ValueError, match="讨论后修订"):
        validate_assessment(row, old)


def test_v2_initial_record_does_not_claim_discussion_revision(store):
    row, _ = v2_record(store)
    row.update(amendment_kind="post_discussion", amendment_reason="错误地声明修订")
    with pytest.raises(ValueError, match="首次提交"):
        validate_assessment(row)


@pytest.mark.parametrize("field", ["first_pass", "paraphrase", "locked_at"])
def test_v2_upgrade_must_keep_first_submitted_reading_observation(store, field):
    row, first = v2_record(store, previous=True)
    if field == "first_pass":
        row["reading_difficulty"].update(first_pass="复述不出或说偏", rewrite_judgment="改写不出")
        from scripts.q1_note_form import derive
        derive(row)
    else:
        row["reading_difficulty"][field] = "2099-01-01T00:00:00Z" if field == "locked_at" else "新复述"
    with pytest.raises(ValueError, match="第一遍"):
        validate_assessment(row, first, first)


def test_v2_record_event_counter_cannot_reset_on_schema_upgrade(store):
    row, old = v2_record(store, previous=True)
    row["event_version"] = 2
    with pytest.raises(ValueError, match="序号"):
        validate_assessment(row, old)


def test_reader_accepts_native_v2_manifest_without_changing_its_bytes(store):
    row, _ = v2_record(store)
    form, digest = load_form(mod.FORM_V2)
    manifest = deepcopy(store.manifest)
    manifest.update(rubric_form_version=mod.FORM_V2, rubric_form_sha256=digest)
    manifest_bytes = mod.encoded(manifest)
    (store.folder / "manifest.json").write_bytes(manifest_bytes)
    from pathlib import Path
    backend = Path(__file__).resolve().parents[1]
    (store.folder / "rubric-form.json").write_bytes((backend / f"rubric/{mod.FORM_V2}.json").read_bytes())
    row["session_manifest_sha256"] = fingerprint(manifest)
    (store.folder / "judgments.jsonl").write_bytes(mod.encoded(row))
    assert mod.read_note_review(store.folder)[1] == [row]
    assert (store.folder / "manifest.json").read_bytes() == manifest_bytes


@pytest.mark.parametrize("form_version", [None, mod.FORM_V1])
def test_prepare_cli_defaults_to_v2_but_can_prepare_legacy_form(monkeypatch, form_version):
    import sys
    from scripts import q1_note_review
    calls = []
    monkeypatch.setattr(q1_note_review, "prepare", lambda *args, **kwargs: calls.append((args, kwargs)))
    argv = ["q1_note_review", "prepare", "--source", "/unused/source", "--session", "/unused/state/test", "--book-root", "/unused/book"]
    if form_version:
        argv += ["--form", form_version]
    monkeypatch.setattr(sys, "argv", argv)
    q1_note_review.main()
    assert calls[0][1]["form_version"] == (form_version or mod.FORM_V2)


def test_v2_rewrite_revision_requires_history_from_previous_value(store):
    from scripts.q1_note_form import derive
    row, _ = v2_record(store)
    d = row["reading_difficulty"]
    d.update(first_pass="复述不出或说偏", rewrite_judgment="改写不出")
    derive(row)
    previous = deepcopy(row)
    d["rewrite_judgment"] = "能改写得更直白"
    derive(row)
    row.update(amendment_kind="post_discussion", amendment_reason="讨论", supersedes_revision=1,
               revision=2, event_version=row["event_version"] + 1)
    row["steps"]["tags"] = {"status": "skipped_due_to_fail"}
    with pytest.raises(ValueError, match="接续"):
        validate_assessment(row, previous)
    d["amendments"] = [{"from": "能改写得更直白", "to": "改写不出", "at": mod.now(), "reason": "", "active_ms": 0},
                       {"from": "改写不出", "to": "能改写得更直白", "at": mod.now(), "reason": "", "active_ms": 0}]
    with pytest.raises(ValueError, match="接续"):
        validate_assessment(row, previous)


@pytest.mark.parametrize("form_version", [mod.FORM_V1, mod.FORM_V2])
def test_unit_note_reopens_under_original_manifest_identity_without_event_schema(store, form_version):
    from pathlib import Path
    backend = Path(__file__).resolve().parents[1]
    if form_version == mod.FORM_V2:
        manifest = deepcopy(store.manifest)
        manifest.update(rubric_form_version=form_version,
                        rubric_form_sha256=load_form(form_version)[1])
        (store.folder / "manifest.json").write_bytes(mod.encoded(manifest))
        (store.folder / "rubric-form.json").write_bytes((backend / f"rubric/{form_version}.json").read_bytes())
        store = mod.Store(store.folder)
    manifest_before = (store.folder / "manifest.json").read_bytes()
    store.unit_note("window", "测试单元备注")
    first = store.read_judgments()
    assert len(first) == 1
    assert first[0]["rubric_form_version"] == form_version
    assert "event_schema_version" not in first[0]
    assert all(first[0][key] == value for key, value in store.identity.items())
    prefix = (store.folder / "judgments.jsonl").read_bytes()
    reopened = mod.Store(store.folder)
    reopened.unit_note("window", "更新测试单元备注")
    result = mod.read_note_review(store.folder)[1]
    assert len(result) == 2 and result[1]["supersedes_revision"] == 1
    assert (store.folder / "judgments.jsonl").read_bytes().startswith(prefix)
    assert (store.folder / "manifest.json").read_bytes() == manifest_before
    # Unlike marginalia, unit notes cannot opt into another form within the session.
    other_form = mod.FORM_V1 if form_version == mod.FORM_V2 else mod.FORM_V2
    result[1].update(rubric_form_version=other_form,
                     rubric_form_sha256=load_form(other_form)[1], event_schema_version=2)
    (store.folder / "judgments.jsonl").write_bytes(b"".join(mod.encoded(row) for row in result))
    with pytest.raises(ValueError, match="身份"):
        mod.Store(store.folder)


def test_reader_normalizes_only_premerge_v2_rewrite_without_rewriting_journal(store):
    current, legacy = v2_record(store, previous=True)
    d = current["reading_difficulty"]
    d["rewrite_text"] = "独立的改写文本"
    early = deepcopy(current)
    fields = early["reading_difficulty"]
    fields["rewrite"] = fields.pop("rewrite_judgment")
    journal = store.folder / "judgments.jsonl"
    mod.append(journal, early)
    before = journal.read_bytes()
    assert mod.read_note_review(store.folder)[1] == [legacy, current]
    assert journal.read_bytes() == before
    fields["rewrite_judgment"] = None
    with pytest.raises(ValueError, match="重复"):
        validate_assessment(early, legacy)
