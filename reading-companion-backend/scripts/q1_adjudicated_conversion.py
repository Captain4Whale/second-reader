"""Deterministic v1 + owner adjudication conversion; never a new annotation."""

from hashlib import sha256
import json
from pathlib import Path
import re

from scripts.q1_comparison import require
from scripts.q1_rubric_review import read_review

BASIS = "N1/H1 取自 q1-v1 文字下的人工判定及所有者裁决，再换算为 v2 结构；不是按 q1-v2 逐条标注。"
VETO_LABELS = {
    "incorrect_information": "有错误信息",
    "spoiler": "有剧透",
    "incomplete_range": "范围不完整",
    "unintelligible_without_context": "离开上下文看不懂",
}
TAG_LABELS = {
    "redundancy": "冗余",
    "teacher_tone": "老师口吻",
    "too_terse": "太简练",
    "empty_talk": "有空话",
    "anchor_issue": "锚点问题",
}
RULES = {
    "N1": "Copy v1; owner adjudication overrides the listed 15 N1 decisions.",
    "N2_fail": "incorrect_information veto",
    "N3_fail": "spoiler veto",
    "N4_fail": "anchor_issue tag (not a veto)",
    "uncovered_尾巴：阅读理解": "empty_talk tag (not a veto)",
    "existing_tags_and_needs_verification": "copy unchanged",
    "H1": "copy v1",
    "H2_fail": "incomplete_range veto",
    "H3_fail": "unintelligible_without_context veto",
    "overall": "core pass and no vetoes",
    "clean_note_pass": "overall pass and neither empty_talk nor redundancy",
    "uncertain": "not collected in v1; null, never inferred",
}


def normalize_quotes(text):
    return text.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))


def adjudication_sections(raw):
    parts = re.split(r"^\*\*([ABCD]\d)\*\*", raw.decode("utf-8"), flags=re.M)[1:]
    require(len(parts) == 30, "Expected 15 owner evidence sections")
    result = {}
    for label, text in zip(parts[::2], parts[1::2], strict=True):
        require(label not in result, "Duplicate adjudication section")
        verdict = re.search(r"^最终：(.*)$", text, re.M)
        require(verdict is not None, "Missing owner final text")
        result[label] = {
            "body_text": "\n".join(re.findall(r"^> (.*)$", text, re.M)),
            "final_text": verdict.group(1),
        }
    return result


def convert_records(mixed, rows, adjudications):
    """One derived record per latest completed mark, with field-level provenance."""
    marks = {
        m["marginalia_id"]: (w, m) for w in mixed["windows"] for m in w["marginalia"]
    }
    latest = {r["record_id"]: r for r in rows if r["record_type"] == "marginalia"}
    require(set(latest) == set(marks), "Conversion requires complete paired judgments")
    overrides = {a["marginalia_id"]: a for a in adjudications}
    require(
        len(overrides) == len(adjudications) and set(overrides) <= set(marks),
        "Duplicate/unknown adjudication ID",
    )
    for mid, a in overrides.items():
        require(
            marks[mid][1]["type"] == "N" and a["final_n1"] in ("pass", "fail"),
            "Invalid Note adjudication",
        )
        require(
            normalize_quotes(a["body_text"])
            == normalize_quotes(marks[mid][1]["body_text"]),
            "Adjudication body mismatch",
        )
    converted = []
    for mid, (window, mark) in marks.items():
        row = latest[mid]
        require(
            row["review_completed"] and row["schema"] == "q1-mixed-judgment/3",
            "Expected completed stepwise v1 judgment",
        )
        note = mark["type"] == "N"
        assessments = row["criterion_assessments"]
        cid = "N1" if note else "H1"
        override = overrides.get(mid)
        core = override["final_n1"] if override else assessments[cid]["judgment"]
        mapping = (
            {"N2": "incorrect_information", "N3": "spoiler"}
            if note
            else {"H2": "incomplete_range", "H3": "unintelligible_without_context"}
        )
        vetoes = [v for c, v in mapping.items() if assessments[c]["judgment"] == "fail"]
        tags = list(row["tags"])
        require(
            set(tags) <= {"redundancy", "teacher_tone", "too_terse"},
            "Unknown source tag",
        )
        if note and assessments["N4"]["judgment"] == "fail":
            tags.append("anchor_issue")
        if row["rubric_uncovered"]:
            require(
                note and row["uncovered_reason"] == "尾巴：阅读理解",
                "Unmapped rubric-uncovered reason; stop",
            )
            tags.append("empty_talk")
        judgment = "pass" if core == "pass" and not vetoes else "fail"
        converted.append(
            {
                "marginalia_id": mid,
                "window_id": window["window_id"],
                "book": window["book"],
                "type": mark["type"],
                "source_quote": mark["source_quote"],
                "body_text": mark["body_text"],
                "judgment": judgment,
                "core": {"id": cid, "judgment": core},
                "vetoes": vetoes,
                "tags": tags,
                "clean_pass": judgment == "pass"
                and not ({"empty_talk", "redundancy"} & set(tags))
                if note
                else None,
                "needs_verification": row["needs_verification"],
                "uncertain": None,
                "failure_type": None,
                "provenance": {
                    "basis": BASIS,
                    "source_revision": row["revision"],
                    "source_review_session_id": row["review_session_id"],
                    "source_rubric_version": row["rubric_version"],
                    "core_source": "owner_adjudication"
                    if override
                    else "q1-v1_completed_revision",
                    "adjudication_item": override["evidence_item"]
                    if override
                    else None,
                    "adjudication_final_text": override["final_text"]
                    if override
                    else None,
                    "source_core_judgment": assessments[cid]["judgment"],
                    "source_criterion_reason": assessments[cid]["reason"],
                    "other_fields_source": "q1-v1 completed revision via fixed conversion rules",
                },
            }
        )
    return converted


def load_conversion(review, specification, rubric_identity):
    spec_path = Path(specification)
    spec = json.loads(spec_path.read_bytes())
    context, _, mixed, _, rows, raw = read_review(review)
    require(context["rubric_version"] == "q1-v1", "Conversion source must be q1-v1")
    require(
        sha256(raw).hexdigest() == spec["source_review_sha256"],
        "Source review snapshot mismatch",
    )
    evidence = spec_path.parent / spec["adjudication_file"]
    require(
        sha256(evidence.read_bytes()).hexdigest() == spec["adjudication_sha256"],
        "Adjudication evidence mismatch",
    )
    sections = adjudication_sections(evidence.read_bytes())
    require(
        len(spec["adjudications"]) == 15
        and {a["evidence_item"] for a in spec["adjudications"]} == set(sections),
        "Adjudication coverage mismatch",
    )
    for a in spec["adjudications"]:
        require(
            all(
                a[k] == sections[a["evidence_item"]][k]
                for k in ("body_text", "final_text")
            ),
            "Adjudication source text mismatch",
        )
        # D1's N1 pass is explicit in the owner request, not in its anchor-only final text.
        if a["evidence_item"] != "D1":
            # Read the first final verdict, not later discussion of an earlier failure.
            verdict = re.search(r"不过|过", a["final_text"])
            require(verdict is not None, "Missing explicit owner verdict")
            expected = "fail" if verdict.group() == "不过" else "pass"
            require(a["final_n1"] == expected, "Owner verdict mismatch")
        else:
            require(a["final_n1"] == "pass", "D1 owner instruction requires N1 pass")
    require(
        spec["target_rubric"] == rubric_identity
        and rubric_identity["version"] == "q1-v2",
        "Target rubric mismatch",
    )
    return {
        "schema": "q1-adjudicated-conversion/1",
        "conversion_id": spec["conversion_id"],
        "basis": BASIS,
        "rules": RULES,
        "target_rubric": rubric_identity,
        "source_review_sha256": spec["source_review_sha256"],
        "adjudication_sha256": spec["adjudication_sha256"],
        "records": convert_records(mixed, rows, spec["adjudications"]),
    }


def conversion_counts(records):
    result = {}
    for kind, name in (("N", "Note"), ("H", "Highlight")):
        selected = [r for r in records if r["type"] == kind]
        total = len(selected)
        passed = sum(r["judgment"] == "pass" for r in selected)
        core = "N1" if kind == "N" else "H1"
        veto_ids = (
            ("incorrect_information", "spoiler")
            if kind == "N"
            else ("incomplete_range", "unintelligible_without_context")
        )
        clean = sum(r["clean_pass"] for r in selected) if kind == "N" else None
        result[name] = {
            "total": total,
            "judged": total,
            "passed": passed,
            "failed": total - passed,
            "unjudged": 0,
            "pass_rate": passed / total if total else None,
            "failed_criteria": {
                core: {
                    "label": "增量" if kind == "N" else "值得停下来",
                    "failed": sum(r["core"]["judgment"] == "fail" for r in selected),
                }
            },
            "rubric_uncovered": 0,
            "prior_judgment_seen": None,
            "clean_passed": clean,
            "clean_pass_rate": clean / total if total and clean is not None else None,
            "vetoes": {
                v: {
                    "label": VETO_LABELS[v],
                    "count": sum(v in r["vetoes"] for r in selected),
                }
                for v in veto_ids
            },
            "tags": {
                t: {"label": label, "count": sum(t in r["tags"] for r in selected)}
                for t, label in TAG_LABELS.items()
            }
            if kind == "N"
            else {},
            "needs_verification": sum(r["needs_verification"] for r in selected),
            "uncertain": None,
        }
    return result
