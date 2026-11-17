"""Isolated Note sessions: deterministic preparation and append-only durable transitions."""

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
from uuid import uuid4

from scripts.q1_comparison_stats import load_bundle
from scripts.q1_note_context import BookSource, contexts, fingerprint
from scripts.q1_note_form import (
    SCHEMA,
    STEPS,
    LABELS,
    DIFFICULTY,
    TAGS,
    require,
    derive,
    validate_assessment,
    validate_n1,
    choices,
    text,
)
from scripts.q1_rubric_form import load_form

BACKEND = Path(__file__).resolve().parents[1]
FORM = "q1-v3.4.form.v1"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n").encode()


def rows(path):
    raw = path.read_bytes()
    require(not raw or raw.endswith(b"\n"), "日志末尾不完整，保留原文件并停止写入")
    return [json.loads(line) for line in raw.splitlines()]


def append(path, value):
    with path.open("ab") as stream:
        stream.write(encoded(value))
        stream.flush()
        os.fsync(stream.fileno())


def prepare(source, output, book_roots, seed=20261115, purpose="formal", mark_ids=None):
    output = Path(output).resolve()
    require(
        output.is_relative_to((BACKEND / "state").resolve()),
        "会话必须放在 backend/state/",
    )
    require(not output.exists(), "会话目录已存在，拒绝覆盖")
    require(purpose in ("formal", "test"), "会话用途无效")
    require(not mark_ids or purpose == "test", "选取测试条目只能写入 test 会话")
    canonical, mixed, _ = load_bundle(Path(source))
    books = [BookSource(p) for p in book_roots]
    by_identity = {(b.epub_sha256, b.substrate_sha256): b for b in books}
    source_map = {
        s["source_id"]: by_identity.get((s["epub_sha256"], s["substrate_sha256"]))
        for s in canonical["sources"]
    }
    require(all(source_map.values()), "源书 EPUB / BookDocument 身份与批次不符")
    windows = {w["window_id"]: w for w in canonical["windows"]}
    cases = []
    for w in mixed["windows"]:
        book = source_map[windows[w["window_id"]]["source_id"]]
        for m in w["marginalia"]:
            if m["type"] != "N" or (mark_ids and m["marginalia_id"] not in mark_ids):
                continue
            cases.append(
                dict(
                    record_id=m["marginalia_id"],
                    window_id=w["window_id"],
                    unit_key=w["window_id"],
                    book_key=book.epub_sha256,
                    book=w["book"],
                    chapter_title=w["chapter_title"],
                    body_text=m["body_text"],
                    source_quote=m["source_quote"],
                    original_source_range=m["original_source_range"],
                    context=contexts(book, w, m),
                )
            )
    require(
        cases and (not mark_ids or len(cases) == len(set(mark_ids))),
        "没有匹配的 Note 或测试 ID 无效",
    )
    cases.sort(
        key=lambda c: (
            sha256(f"{seed}\0{c['record_id']}".encode()).hexdigest(),
            c["record_id"],
        )
    )
    form, form_hash = load_form(FORM)
    manifest = dict(
        schema="q1-note-session/1",
        review_session_id=str(uuid4()),
        session_purpose=purpose,
        batch_id=mixed["batch_id"],
        annotator_id="weijiang",
        rubric_version=form["rubric_version"],
        rubric_sha256=form["rubric_sha256"],
        annotation_guide_sha256=form["annotation_guide_sha256"],
        rubric_form_version=FORM,
        rubric_form_sha256=form_hash,
        randomization=dict(
            seed=seed,
            algorithm="sha256-sort-v1",
            order_sha256=fingerprint([c["record_id"] for c in cases]),
        ),
        context_sha256=fingerprint(cases),
        created_at=now(),
        source_mixed_sha256=sha256(
            (Path(source) / "mixed.json").read_bytes()
        ).hexdigest(),
        source_identities=[
            dict(
                epub_sha256=b.epub_sha256,
                substrate_sha256=b.substrate_sha256,
                document_sha256=b.document_sha256,
            )
            for b in books
        ],
        record_ids=[c["record_id"] for c in cases],
        total_notes=len(cases),
        exposure="historical_reannotation" if mark_ids else "not_assumed_unseen",
    )
    # Preserve only explicit upstream notes, never import old mark outcomes into a new judgment.
    upstream = {}
    journal = Path(source) / "judgments.jsonl"
    if journal.exists():
        for r in rows(journal):
            if r.get("record_type") == "unit_note":
                upstream[r["window_id"]] = r.get("remarks", "")
    manifest["initial_unit_notes"] = {
        k: v for k, v in upstream.items() if v.lstrip().startswith("上游：")
    }
    output.mkdir(parents=True)
    for name, data in [
        ("manifest.json", encoded(manifest)),
        ("context.json", encoded(cases)),
        ("rubric-form.json", (BACKEND / "rubric/q1-v3.4.form.v1.json").read_bytes()),
        ("judgments.jsonl", b""),
        ("progress.jsonl", b""),
    ]:
        with (output / name).open("xb") as stream:
            stream.write(data)
    store = Store(output)
    for key, note in manifest["initial_unit_notes"].items():
        if any(c["unit_key"] == key for c in cases):
            store.unit_note(key, note)
    return manifest


class Store:
    def __init__(self, folder):
        self.folder = Path(folder).resolve()
        require(
            self.folder.is_relative_to((BACKEND / "state").resolve()),
            "会话必须在 state/",
        )
        self.manifest = json.loads((self.folder / "manifest.json").read_bytes())
        self.form, h = load_form(self.manifest["rubric_form_version"])
        require(
            all(
                self.manifest[k] == self.form[k]
                for k in ("rubric_version", "rubric_sha256", "annotation_guide_sha256")
            ),
            "会话 rubric 身份不符",
        )
        require(
            h
            == self.manifest["rubric_form_sha256"]
            == sha256((self.folder / "rubric-form.json").read_bytes()).hexdigest(),
            "表单快照被修改",
        )
        self.cases = json.loads((self.folder / "context.json").read_bytes())
        require(
            fingerprint(self.cases) == self.manifest["context_sha256"],
            "上下文快照被修改",
        )
        require(
            [c["record_id"] for c in self.cases] == self.manifest["record_ids"]
            and fingerprint(self.manifest["record_ids"])
            == self.manifest["randomization"]["order_sha256"],
            "条目顺序被修改",
        )
        self.case_map = {c["record_id"]: c for c in self.cases}
        self.identity = {
            k: self.manifest[k]
            for k in (
                "review_session_id",
                "session_purpose",
                "batch_id",
                "annotator_id",
                "rubric_version",
                "rubric_sha256",
                "annotation_guide_sha256",
                "rubric_form_version",
                "rubric_form_sha256",
            )
        }
        self.identity["session_manifest_sha256"] = fingerprint(self.manifest)
        self.read_judgments()

    @contextmanager
    def lock(self):
        with (self.folder / ".session.lock").open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)

    def read_judgments(self):
        journal, latest = rows(self.folder / "judgments.jsonl"), {}
        for index, r in enumerate(journal, 1):
            require(
                r["revision"] == index
                and all(r.get(k) == v for k, v in self.identity.items()),
                "日志修订或会话身份不符",
            )
            if r["record_type"] == "unit_note":
                require(
                    r["schema"] == SCHEMA
                    and any(c["unit_key"] == r["unit_key"] for c in self.cases),
                    "单元备注身份无效",
                )
                require(
                    type(r["upstream_excluded"]) is bool
                    and r["upstream_excluded"]
                    == r["remarks"].lstrip().startswith("上游："),
                    "上游排除与备注不符",
                )
                continue
            c = self.case_map.get(r["record_id"])
            require(
                c is not None
                and all(
                    r[k] == c[k]
                    for k in (
                        "window_id",
                        "unit_key",
                        "book_key",
                        "body_text",
                        "source_quote",
                        "original_source_range",
                    )
                ),
                "批注内容或身份被修改",
            )
            old = latest.get(r["record_id"])
            expected = self.new_state(r["record_id"])["record"]
            require(
                r["randomization"] == expected["randomization"]
                and all(
                    r["context"][k] == expected["context"][k]
                    for k in (
                        "snapshot_sha256",
                        "observer_cutoff",
                        "original_notes_status",
                        "original_note_ids",
                    )
                ),
                "随机顺序或上下文身份不符",
            )
            require(
                r["supersedes_revision"] == (old["revision"] if old else None),
                "修订前驱不符",
            )
            validate_assessment(r, old)
            latest[r["record_id"]] = r
        return journal

    def state(self, rid):
        require(rid in self.case_map, "未知批注")
        found = [
            e for e in rows(self.folder / "progress.jsonl") if e["record_id"] == rid
        ]
        state = deepcopy(found[-1]["state"]) if found else None
        completed = [
            r
            for r in self.read_judgments()
            if r["record_type"] == "marginalia" and r["record_id"] == rid
        ]
        if completed and (
            state is None or completed[-1]["event_version"] > state["version"]
        ):
            r = deepcopy(completed[-1])
            state = dict(version=r["event_version"], stage=7, record=r)
        return state

    def new_state(self, rid):
        c = self.case_map[rid]
        r = dict(
            schema=SCHEMA,
            **self.identity,
            annotator_version="q1-note-annotator/1.0",
            record_type="marginalia",
            record_id=rid,
            marginalia_id=rid,
            type="N",
            **{
                k: deepcopy(c[k])
                for k in (
                    "window_id",
                    "unit_key",
                    "book_key",
                    "body_text",
                    "source_quote",
                    "original_source_range",
                )
            },
            randomization={
                **self.manifest["randomization"],
                "position": self.manifest["record_ids"].index(rid) + 1,
            },
            context=dict(
                snapshot_sha256=self.manifest["context_sha256"],
                observer_cutoff=c["context"]["observer_cutoff"],
                original_notes_status=c["context"]["original_notes"]["status"],
                original_note_ids=[
                    n["id"] for n in c["context"]["original_notes"]["items"]
                ],
                viewed_original_notes=False,
            ),
            first_impression={},
            reading_difficulty=dict(
                original_choice=None,
                choice=None,
                veto=False,
                paraphrase="",
                rewrite="",
                amendments=[],
            ),
            n1={},
            vetoes=dict(
                reading_difficulty=False, spoiler=False, incorrect_information=False
            ),
            unsure=[],
            unsure_sources={},
            needs_verification=False,
            rubric_uncovered=False,
            uncovered_reason="",
            judgment=None,
            star=False,
            reason="",
            steps={},
            review_completed=False,
        )
        r["steps"]["first_impression"] = dict(started_at=now(), active_ms=0)
        return dict(version=0, stage=0, record=r)

    def unit_note(self, key, remark):
        require(
            isinstance(remark, str) and any(c["unit_key"] == key for c in self.cases),
            "单元备注无效",
        )
        with self.lock():
            journal = self.read_judgments()
            previous = next(
                (
                    r
                    for r in reversed(journal)
                    if r["record_type"] == "unit_note" and r["unit_key"] == key
                ),
                None,
            )
            if previous and previous["remarks"] == remark:
                return
            append(
                self.folder / "judgments.jsonl",
                dict(
                    schema=SCHEMA,
                    **self.identity,
                    record_type="unit_note",
                    record_id=key,
                    unit_key=key,
                    remarks=remark,
                    upstream_excluded=remark.lstrip().startswith("上游："),
                    revision=len(journal) + 1,
                    timestamp=now(),
                    supersedes_revision=previous["revision"] if previous else None,
                ),
            )

    def action(self, rid, action, values=None, version=None, active_ms=0):
        with self.lock():
            state = self.state(rid) or self.new_state(rid)
            if action != "open":
                require(
                    version == state["version"],
                    "页面状态已过期，请重新载入；已保存的锁定与记录不变",
                )
            require(type(active_ms) is int and 0 <= active_ms <= 86400000, "计时无效")
            values = values or {}
            r, stage = state["record"], state["stage"]
            if stage < 7:
                step = STEPS[stage]
                r["steps"][step]["active_ms"] = (
                    r["steps"][step].get("active_ms", 0) + active_ms
                )
            if action == "open":
                pass
            elif action == "amend":
                require(stage >= 2, "完成读着费劲后才能修正")
                choice = values.get("choice")
                require(
                    choice in DIFFICULTY
                    and choice != r["reading_difficulty"]["choice"],
                    "请选择不同的费劲选项",
                )
                d = r["reading_difficulty"]
                d["amendments"].append(
                    dict(
                        from_=d["choice"],
                        to=choice,
                        at=now(),
                        reason=values.get("reason", ""),
                        active_ms=active_ms,
                    )
                )
                d["amendments"][-1]["from"] = d["amendments"][-1].pop("from_")
                d["choice"] = choice
                d["rewrite"] = values.get("rewrite", d["rewrite"])
                derive(r)
                if stage == 7:
                    state["stage"] = 5
                    r["review_completed"] = False
                    r["steps"]["conclusion"].pop("completed_at", None)
            elif action == "reopen":
                target = values.get("step", 2)
                require(type(target) is int and 2 <= target <= 6 and target < stage, "只能修改已经完成的 N1 及后续步骤")
                state["stage"] = target
                r["review_completed"] = False
                for k in STEPS[target:]:
                    r["steps"].setdefault(k, {}).pop("completed_at", None)
            elif action == "following":
                require(stage in (2, 3), "只有 N1 和有剧透两步可以展开后文")
                scope = values.get("scope")
                require(scope in ("within_unit", "after_unit"), "后文范围无效")
                parts = self.case_map[rid]["context"][scope]
                require(parts, "本章此范围没有后文")
                s = r["steps"][STEPS[stage]]
                s["viewed_following_text"] = True
                s["following_text_views"].append(
                    dict(
                        opened_at=now(),
                        scope=scope,
                        range=dict(
                            start=parts[0]["range"]["start"],
                            end=parts[-1]["range"]["end"],
                        ),
                    )
                )
            elif action == "notes":
                r["context"]["viewed_original_notes"] = True
            elif action in ("save", "complete", "submit"):
                require(stage < 7, "记录已提交，先点击重新检查")
                self.apply_values(r, stage, values)
                if action == "complete":
                    require(stage < 6, "标签之后请提交")
                    self.complete_step(r, stage)
                    state["stage"] = stage + 1
                    if state["stage"] == 6 and r["judgment"] != "pass":
                        r["steps"]["tags"] = dict(status="skipped_due_to_fail")
                    else:
                        self.start_step(r, STEPS[state["stage"]])
                if action == "submit":
                    require(stage == 6, "请按顺序完成所有步骤")
                    if r["judgment"] == "pass":
                        self.complete_step(r, 6)
                    else:
                        r["steps"]["tags"] = dict(status="skipped_due_to_fail")
                    r["review_completed"] = True
                    journal = self.read_judgments()
                    previous = next(
                        (
                            x
                            for x in reversed(journal)
                            if x["record_type"] == "marginalia"
                            and x["record_id"] == rid
                        ),
                        None,
                    )
                    r.update(
                        revision=len(journal) + 1,
                        supersedes_revision=previous["revision"] if previous else None,
                        timestamp=now(),
                        event_version=state["version"] + 1,
                    )
                    validate_assessment(r, previous)
                    append(self.folder / "judgments.jsonl", r)
                    state["stage"] = 7
            else:
                raise ValueError("未知操作")
            state["version"] += 1
            append(
                self.folder / "progress.jsonl",
                dict(record_id=rid, action=action, timestamp=now(), state=state),
            )
            return state

    def start_step(self, r, step):
        s = r["steps"].setdefault(step, {})
        s.pop("status", None)
        s.setdefault("started_at", now())
        s.setdefault("active_ms", 0)
        if step in ("n1", "spoiler"):
            s.setdefault("viewed_following_text", False)
            s.setdefault("following_text_views", [])

    def apply_values(self, r, stage, v):
        # Only editable fields for the current stage are accepted, never identity or locked evidence.
        allowed = {
            "manual_unsure",
            "rubric_uncovered",
            "uncovered_reason",
            "reason",
            "star",
        }
        per_step = (
            {"judgment"},
            {"choice", "paraphrase", "rewrite"},
            {"n1"},
            {"spoiler"},
            {"incorrect_information", "needs_verification"},
            set(),
            {"tags"},
        )
        require(set(v) <= allowed | per_step[stage], "不能修改锁定项或其他步骤的字段")
        for k in ("rubric_uncovered", "star"):
            if k in v:
                require(type(v[k]) is bool, "勾选值无效")
                r[k] = v[k]
        for k in ("uncovered_reason", "reason"):
            if k in v:
                require(isinstance(v[k], str), "说明必须是文字")
                r[k] = v[k]
        if "manual_unsure" in v:
            require(type(v["manual_unsure"]) is bool, "拿不准值无效")
            label = LABELS[stage]
            sources = [x for x in r["unsure_sources"].get(label, []) if x != "manual"]
            if v["manual_unsure"]:
                sources.append("manual")
            if sources:
                r["unsure_sources"][label] = sources
            else:
                r["unsure_sources"].pop(label, None)
        if stage == 0 and "judgment" in v:
            require(v["judgment"] in ("pass", "fail"), "请选择第一印象")
            require(not r["first_impression"].get("locked_at"), "第一印象已经锁定")
            r["first_impression"]["judgment"] = v["judgment"]
        elif stage == 1:
            for k in ("choice", "paraphrase", "rewrite"):
                if k in v:
                    require(isinstance(v[k], str), "费劲字段无效")
                    r["reading_difficulty"][k] = v[k]
        elif stage == 2 and "n1" in v:
            n = v["n1"]
            require(
                isinstance(n, dict)
                and set(n)
                <= {
                    "following_text_use",
                    "judgment",
                    "writing_style",
                    "other_writing_explanation",
                    "failure_types",
                    "other_failure_explanation",
                    "paraphrase",
                    "reason",
                },
                "N1 字段无效",
            )
            if n.get("following_text_use") == "紧接着几段":
                n["judgment"] = "fail"
                n.pop("writing_style", None)
                n.pop("other_writing_explanation", None)
                n["failure_types"] = list(
                    dict.fromkeys(n.get("failure_types", []) + ["下文马上讲了"])
                )
            r["n1"] = deepcopy(n)
        elif stage in (3, 4):
            key = "spoiler" if stage == 3 else "incorrect_information"
            if key in v:
                require(type(v[key]) is bool, "否决值无效")
                r["vetoes"][key] = v[key]
            if "needs_verification" in v:
                require(type(v["needs_verification"]) is bool, "待核实值无效")
                r["needs_verification"] = v["needs_verification"]
        elif stage == 6 and "tags" in v:
            choices(v["tags"], TAGS, "标签")
            require(r["judgment"] == "pass" or not v["tags"], "不过不能标标签")
            r["tags"] = v["tags"]
        derive(r)
        if stage == 6 and r["judgment"] == "pass":
            self.start_step(r, "tags")

    def complete_step(self, r, stage):
        if stage == 0:
            require(
                r["first_impression"].get("judgment") in ("pass", "fail"),
                "请选择第一印象",
            )
            r["first_impression"]["locked_at"] = now()
        if stage == 1:
            d = r["reading_difficulty"]
            require(d["choice"] in DIFFICULTY, "请选择读着费劲的判断")
            d["original_choice"] = d["choice"]
        if stage == 2:
            validate_n1(r["n1"])
        require(
            not r["rubric_uncovered"] or text(r["uncovered_reason"]),
            "rubric 未覆盖必须写原因",
        )
        r["steps"][STEPS[stage]]["completed_at"] = now()


def read_note_review(folder):
    """Future scoring adapters can call this without loading UI code or old adapters."""
    store = Store(folder)
    return store.manifest, store.read_judgments()
