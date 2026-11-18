"""Q1 v3.4 Note protocol. No legacy coercion, source I/O or statistics."""

from datetime import datetime
import re

STEPS = (
    "first_impression",
    "reading_difficulty",
    "n1",
    "spoiler",
    "incorrect_information",
    "conclusion",
    "tags",
)
LABELS = ("第一印象", "读着费劲", "N1", "有剧透", "有错误信息", "结论", "标签")
DIFFICULTY = ("一遍能复述", "能改写得更直白", "改写不出")
FOLLOWING = ("没用到", "紧接着几段", "挂早了", "更远后文，转第四步判剧透")
STYLES = ("补充", "联想", "解读", "其他写法")
FAILURES = ("没新东西", "下文马上讲了", "只提问不回答", "有东西没送到", "其他")
TAGS = ("有空话", "冗余", "老师口吻", "太简练", "锚点问题")
SCHEMA = "q1-note-judgment/1"
FORM_V1 = "q1-v3.4.form.v1"
FORM_V2 = "q1-v3.4.form.v2"
FIRST_PASS = ("复述得出", "复述不出或说偏")
REWRITE = DIFFICULTY[1:]
WARNINGS = ("far_following_without_spoiler",)
V2_EVENT_VERSION_MIN = 2 ** 32


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp(value):
    require(isinstance(value, str), "缺少步骤时间")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "时间必须含时区")
    return result


def choices(values, allowed, name):
    require(
        isinstance(values, list)
        and all(isinstance(v, str) for v in values)
        and len(set(values)) == len(values)
        and set(values) <= set(allowed),
        f"{name}选项无效",
    )


def validate_form(form):
    require(
        set(form)
        == {
            "schema",
            "form_version",
            "rubric_version",
            "rubric_sha256",
            "annotation_guide_sha256",
            "title",
            "mark_types",
            "steps",
            "choices",
            "policy",
            "flags_help",
        },
        "Note 表单字段无效",
    )
    require(
        form["schema"] == "q1-note-rubric-form/1" and form["mark_types"] == ["N"],
        "只支持 Note 表单",
    )
    require(
        all(
            text(form[k])
            for k in ("form_version", "rubric_version", "title", "flags_help")
        ),
        "缺少表单身份",
    )
    require(
        all(
            re.fullmatch("[a-f0-9]{64}", form[k])
            for k in ("rubric_sha256", "annotation_guide_sha256")
        ),
        "版本哈希无效",
    )
    require([s["id"] for s in form["steps"]] == list(STEPS), "步骤顺序不符合标注说明")
    require(
        all(
            set(s) == {"id", "label", "section", "help"}
            and text(s["label"])
            and text(s["help"])
            for s in form["steps"]
        ),
        "步骤说明无效",
    )
    require(form["form_version"] in (FORM_V1, FORM_V2), "未知 Note 表单版本")
    v2 = form["form_version"] == FORM_V2
    expected = dict(
        reading_difficulty=list(DIFFICULTY),
        following_text_use=list(FOLLOWING),
        writing_style=list(STYLES),
        failure_types=list(FAILURES),
        tags=list(TAGS),
    )
    if v2:
        expected.pop("reading_difficulty")
        expected.update(first_pass=list(FIRST_PASS), rewrite=list(REWRITE))
    require(form["choices"] == expected, "选项与 v3.4 协议不符")
    require(
        form["policy"]
        == dict.fromkeys(
            (
                "first_impression_immutable",
                "difficulty_amendments_append_only",
                "following_chapter_only",
                "uncovered_fails",
                "star_requires_pass",
                "tags_only_on_pass",
                "explicit_completion",
            ) + (("first_pass_immutable", "first_pass_paraphrase_immutable",
                   "post_discussion_amendments_only", "explicit_veto_checks",
                   "acknowledge_far_following_without_spoiler") if v2 else ()),
            True,
        ),
        "表单策略无效",
    )
    return form


def outcome(row):
    return (
        "pass"
        if (
            row.get("n1", {}).get("judgment") == "pass"
            and not any(row.get("vetoes", {}).values())
            and not row.get("rubric_uncovered")
        )
        else "fail"
    )


def derive(row):
    """Update dependent values, preserving only currently applicable fields."""
    difficulty = row["reading_difficulty"]
    v2 = row.get("event_schema_version") == 2
    value = difficulty["rewrite"] if v2 else difficulty["choice"]
    row["vetoes"]["reading_difficulty"] = value == DIFFICULTY[1]
    if v2:
        for key in ("spoiler", "incorrect_information"):
            row["vetoes"][key] = row.get("checks", {}).get(key) is True
    difficulty["veto"] = row["vetoes"]["reading_difficulty"]
    sources = row["unsure_sources"]
    manual = "manual" in sources.get("读着费劲", [])
    sources.pop("读着费劲", None)
    values = (["automatic"] if value == DIFFICULTY[2] else []) + (
        ["manual"] if manual else []
    )
    if values:
        sources["读着费劲"] = values
    row["unsure"] = [label for label in LABELS if sources.get(label)]
    row["judgment"] = outcome(row)
    if row["judgment"] != "pass":
        row.pop("tags", None)
        row["star"] = False
    else:
        row.setdefault("tags", [])
        if (
            row["n1"].get("following_text_use") == "挂早了"
            and "锚点问题" not in row["tags"]
        ):
            row["tags"].append("锚点问题")


def validate_n1(n, event_schema_version=1):
    require(n.get("following_text_use") in FOLLOWING, "请选择用到后文的分支")
    require(n.get("judgment") in ("pass", "fail"), "请判断 N1 过或不过")
    if n["judgment"] == "pass":
        require(
            not ({"failure_types", "other_failure_explanation"} & n.keys()),
            "写法和失败类型不能同时出现",
        )
        require(n.get("writing_style") in STYLES, "请选择写法")
        require(
            n["writing_style"] != "其他写法"
            or text(n.get("other_writing_explanation")),
            "其他写法必须说明写法及增量",
        )
        require(n["following_text_use"] != "紧接着几段", "下文马上讲了，N1 应判不过")
    else:
        require(
            not ({"writing_style", "other_writing_explanation"} & n.keys()),
            "写法和失败类型不能同时出现",
        )
        choices(n.get("failure_types"), FAILURES, "失败类型")
        require(bool(n["failure_types"]), "N1 不过至少选一个失败类型")
        require(
            "其他" not in n["failure_types"]
            or text(n.get("other_failure_explanation")),
            "失败类型其他必须写说明",
        )
        require(
            n["following_text_use"] != "紧接着几段"
            or "下文马上讲了" in n["failure_types"],
            "缺少下文马上讲了失败类型",
        )

    if event_schema_version == 2:
        require(
            "下文马上讲了" not in n.get("failure_types", [])
            or n["following_text_use"] in ("紧接着几段", "挂早了"),
            "下文马上讲了只适用于紧接着几段或挂早了",
        )


def _validate_v2_difficulty(d):
    require(
        isinstance(d, dict) and set(d) == {
            "first_pass", "locked_at", "paraphrase", "rewrite", "rewrite_text",
            "veto", "amendments",
        },
        "新版费劲字段无效",
    )
    require(d["first_pass"] in FIRST_PASS, "缺少第一遍复述判断")
    timestamp(d["locked_at"])
    require(all(isinstance(d[k], str) for k in ("paraphrase", "rewrite_text")), "费劲文字无效")
    require(isinstance(d["amendments"], list) and all(isinstance(a, dict) for a in d["amendments"]), "费劲修改历史无效")
    require(
        d["rewrite"] is None if d["first_pass"] == FIRST_PASS[0] else d["rewrite"] in REWRITE,
        "第一遍复述结果与改写分支不符",
    )
    require(type(d["veto"]) is bool and d["veto"] == (d["rewrite"] == REWRITE[0]), "费劲否决值无效")
    cursor = d["amendments"][0].get("from") if d["amendments"] else d["rewrite"]
    for a in d["amendments"]:
        require(
            isinstance(a, dict) and a.get("from") == cursor
            and a.get("from") in REWRITE and a.get("to") in REWRITE
            and a.get("from") != a.get("to"),
            "费劲修改历史不连续",
        )
        timestamp(a.get("at"))
        require(isinstance(a.get("reason"), str), "修正理由必须是文字")
        require(type(a.get("active_ms")) is int and a["active_ms"] >= 0, "修正计时无效")
        cursor = a["to"]
    require(cursor == d["rewrite"], "费劲最终值与历史不符")
    require(d["first_pass"] != FIRST_PASS[0] or not d["amendments"], "复述得出不能改写判断")


def validate_assessment(row, previous=None, first_submitted=None):
    """Validate one complete record; previous enforces immutable evidence on amendments."""
    require(
        row.get("schema") == SCHEMA
        and row.get("type") == "N"
        and row.get("record_type") == "marginalia",
        "不是新版 Note 判定",
    )
    require(row.get("review_completed") is True, "未完成的草稿不能写入 judgments")
    v2 = row.get("event_schema_version") == 2
    require(not v2 or row.get("rubric_form_version") == FORM_V2, "新版事件必须绑定 v2 表单")
    require(row.get("rubric_form_version") != FORM_V2 or v2, "v2 表单必须写新版事件")
    required = set(
        "schema annotator_id annotator_version review_session_id session_purpose batch_id session_manifest_sha256 rubric_version rubric_sha256 annotation_guide_sha256 rubric_form_version rubric_form_sha256 record_type record_id marginalia_id window_id unit_key book_key revision supersedes_revision timestamp type source_quote body_text original_source_range randomization context first_impression reading_difficulty n1 vetoes unsure unsure_sources needs_verification rubric_uncovered uncovered_reason judgment star reason steps review_completed event_version".split()
    )
    optional = {"tags"}
    if v2:
        required |= {"event_schema_version", "checks", "legacy_inferences", "acknowledged_warnings"}
        optional |= {"amendment_kind", "amendment_reason", "legacy_reading_difficulty"}
    require(
        required <= row.keys() and set(row) <= required | optional,
        "判定字段缺失或包含未知字段",
    )
    require(row["first_impression"]["judgment"] in ("pass", "fail"), "缺少第一印象")
    timestamp(row["first_impression"]["locked_at"])
    d = row["reading_difficulty"]
    if v2:
        require(type(row["event_schema_version"]) is int, "事件协议版本无效")
        _validate_v2_difficulty(d)
        require(type(row["event_version"]) is int and row["event_version"] >= V2_EVENT_VERSION_MIN, "事件序号无效")
        if previous:
            require(row["event_version"] > previous["event_version"], "事件序号必须继续增长")
        require(
            isinstance(row["checks"], dict)
            and set(row["checks"]) == {"spoiler", "incorrect_information"}
            and all(type(v) is bool for v in row["checks"].values()),
            "剧透和错误信息必须明确判断",
        )
        require(
            all(row["checks"][k] == row["vetoes"].get(k) for k in row["checks"]),
            "明确判断与否决值不一致",
        )
        require(
            isinstance(row["legacy_inferences"], list)
            and all(text(x) for x in row["legacy_inferences"]),
            "旧记录推断说明无效",
        )
        choices(row["acknowledged_warnings"], WARNINGS, "已确认提醒")
        require(
            row["n1"].get("following_text_use") != FOLLOWING[3]
            or row["checks"]["spoiler"]
            or WARNINGS[0] in row["acknowledged_warnings"],
            "更远后文但无剧透需要确认提醒",
        )
        if previous or row.get("supersedes_revision") is not None:
            require(row.get("amendment_kind") == "post_discussion" and text(row.get("amendment_reason")), "提交后只能填写原因追加讨论后修订")
        else:
            require(not ({"amendment_kind", "amendment_reason"} & row.keys()), "首次提交不是讨论后修订")
    else:
        require(
            all(isinstance(d.get(k), str) for k in ("paraphrase", "rewrite"))
            and isinstance(d.get("amendments"), list),
            "费劲文字或修改历史无效",
        )
        require(
            d.get("original_choice") in DIFFICULTY and d.get("choice") in DIFFICULTY,
            "缺少读着费劲判断",
        )
        cursor = d["original_choice"]
        for a in d["amendments"]:
            require(
                a["from"] == cursor and a["to"] in DIFFICULTY and a["from"] != a["to"],
                "费劲修改历史不连续",
            )
            timestamp(a["at"])
            require(isinstance(a.get("reason"), str), "修正理由必须是文字")
            cursor = a["to"]
        require(cursor == d["choice"], "费劲最终值与历史不符")
    validate_n1(row["n1"], 2 if v2 else 1)
    require(
        set(row["vetoes"]) == {"reading_difficulty", "spoiler", "incorrect_information"}
        and all(type(v) is bool for v in row["vetoes"].values()),
        "否决项必须分别判断",
    )
    require(
        d["veto"]
        == row["vetoes"]["reading_difficulty"]
        == ((d["rewrite"] == REWRITE[0]) if v2 else (d["choice"] == DIFFICULTY[1])),
        "费劲结论必须使用最终值",
    )
    require(
        all(
            type(row[k]) is bool
            for k in ("rubric_uncovered", "needs_verification", "star")
        ),
        "标记字段无效",
    )
    require(
        not row["rubric_uncovered"] or text(row.get("uncovered_reason")),
        "rubric 未覆盖必须写原因",
    )
    require(row["judgment"] == outcome(row), "自动结论不一致")
    if row["judgment"] == "fail":
        require("tags" not in row and not row["star"], "不过的记录不能有标签或星")
    else:
        choices(row.get("tags"), TAGS, "标签")
        require(
            row["n1"]["following_text_use"] != "挂早了" or "锚点问题" in row["tags"],
            "挂早了必须带锚点问题",
        )
    choices(row["unsure"], LABELS, "拿不准")
    require(set(row["unsure_sources"]) == set(row["unsure"]), "拿不准来源不一致")
    for label, sources in row["unsure_sources"].items():
        choices(sources, ("manual", "automatic"), "拿不准来源")
        require(
            sources and ("automatic" not in sources or label == "读着费劲"),
            "拿不准来源无效",
        )
    require(
        ("automatic" in row["unsure_sources"].get("读着费劲", []))
        == ((d["rewrite"] == REWRITE[1]) if v2 else (d["choice"] == DIFFICULTY[2])),
        "改写不出必须自动拿不准",
    )
    for name in STEPS:
        s = row["steps"].get(name, {})
        if name == "tags" and row["judgment"] == "fail":
            require(s.get("status") == "skipped_due_to_fail", "不过应跳过标签")
            continue
        require(
            timestamp(s["started_at"]) <= timestamp(s["completed_at"]), "步骤时间倒序"
        )
        require(type(s["active_ms"]) is int and s["active_ms"] >= 0, "步骤计时无效")
    for name in ("n1", "spoiler"):
        s = row["steps"][name]
        require(
            type(s["viewed_following_text"]) is bool
            and s["viewed_following_text"] == bool(s["following_text_views"]),
            "后文展开记录不一致",
        )
        for view in s["following_text_views"]:
            timestamp(view["opened_at"])
            require(view["scope"] in ("within_unit", "after_unit"), "后文展开范围无效")
            r = view["range"]
            require(
                r["start"]["chapter_id"]
                == r["end"]["chapter_id"]
                == row["original_source_range"]["end"]["chapter_id"],
                "后文不能超过本章",
            )
    if previous:
        require(
            row["first_impression"] == previous["first_impression"], "第一印象已经锁定"
        )
        old = previous["reading_difficulty"]
        if v2 and previous.get("event_schema_version") == 2:
            require(
                all(d[k] == old[k] for k in ("first_pass", "locked_at", "paraphrase"))
                and d["amendments"][:len(old["amendments"])] == old["amendments"],
                "不能覆盖第一遍结果、复述或修改历史",
            )
            added = d["amendments"][len(old["amendments"]):]
            require(
                (added[0]["from"] == old["rewrite"]) if added else d["rewrite"] == old["rewrite"],
                "费劲修改历史必须接续上次提交",
            )
            require(
                row["legacy_inferences"][:len(previous["legacy_inferences"])] == previous["legacy_inferences"]
                and row.get("legacy_reading_difficulty") == previous.get("legacy_reading_difficulty"),
                "不能覆盖旧记录推断与原始证据",
            )
        elif v2:
            source = first_submitted or previous
            original = source["reading_difficulty"]
            legacy = row.get("legacy_reading_difficulty")
            require(
                isinstance(legacy, dict) and row["legacy_inferences"]
                and legacy.get("original_choice") == old["original_choice"]
                and isinstance(legacy.get("amendments"), list)
                and legacy["amendments"][:len(old["amendments"])] == old["amendments"],
                "旧费劲证据及推断说明必须保留",
            )
            require(
                d["first_pass"] == (FIRST_PASS[0] if original["original_choice"] == DIFFICULTY[0] else FIRST_PASS[1])
                and d["paraphrase"] == original["paraphrase"]
                and (not source["steps"]["reading_difficulty"].get("completed_at")
                     or d["locked_at"] == source["steps"]["reading_difficulty"]["completed_at"]),
                "不能覆盖首条判定的第一遍结果或复述",
            )
        elif not v2:
            require(previous.get("event_schema_version") != 2, "新版记录不能退回旧事件")
            require(
                d["original_choice"] == old["original_choice"]
                and d["amendments"][:len(old["amendments"])] == old["amendments"],
                "不能覆盖费劲原值或修改历史",
            )
        for name in ("n1", "spoiler"):
            old_views = previous["steps"][name]["following_text_views"]
            require(
                row["steps"][name]["following_text_views"][: len(old_views)]
                == old_views,
                "不能撤销后文暴露",
            )
    return row
