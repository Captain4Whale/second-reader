/* v3.4 browser protocol; Python validates the same journal for future consumers. */
(function (root) {
  "use strict";
  const steps = [
    "first_impression",
    "reading_difficulty",
    "n1",
    "spoiler",
    "incorrect_information",
    "conclusion",
    "tags",
  ];
  const labels = [
    "第一印象",
    "读着费劲",
    "N1",
    "有剧透",
    "有错误信息",
    "结论",
    "标签",
  ];
  const difficulty = ["一遍能复述", "能改写得更直白", "改写不出"];
  const copy = (x) => structuredClone(x),
    now = () => new Date().toISOString();
  const need = (v, m) => {
    if (!v) throw Error(m);
  };
  const stable = (x) =>
    Array.isArray(x)
      ? x.map(stable)
      : x && typeof x === "object"
        ? Object.fromEntries(
            Object.keys(x)
              .sort()
              .map((k) => [k, stable(x[k])]),
          )
        : x;
  // Match the compact sorted UTF-8 fingerprints in q1_note_context.py.
  const canonical = (x) => JSON.stringify(stable(x));
  const hash = async (s) =>
    Array.from(
      new Uint8Array(
        await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)),
      ),
      (x) => x.toString(16).padStart(2, "0"),
    ).join("");
  function derive(r) {
    const d = r.reading_difficulty;
    d.veto = r.vetoes.reading_difficulty = d.choice === difficulty[1];
    const src = r.unsure_sources,
      manual = (src[labels[1]] || []).includes("manual");
    delete src[labels[1]];
    const a = [
      ...(d.choice === difficulty[2] ? ["automatic"] : []),
      ...(manual ? ["manual"] : []),
    ];
    if (a.length) src[labels[1]] = a;
    r.unsure = labels.filter((k) => src[k]?.length);
    r.judgment =
      r.n1.judgment === "pass" &&
      !Object.values(r.vetoes).some(Boolean) &&
      !r.rubric_uncovered
        ? "pass"
        : "fail";
    if (r.judgment === "fail") {
      delete r.tags;
      r.star = false;
    } else {
      r.tags ??= [];
      if (r.n1.following_text_use === "挂早了" && !r.tags.includes("锚点问题"))
        r.tags.push("锚点问题");
    }
  }
  function n1valid(n, f) {
    need(
      f.choices.following_text_use.includes(n.following_text_use),
      "请选择用到后文的分支",
    );
    need(["pass", "fail"].includes(n.judgment), "请判断 N1 过或不过");
    if (n.judgment === "pass") {
      need(
        !("failure_types" in n) && !("other_failure_explanation" in n),
        "写法和失败类型不能同时出现",
      );
      need(f.choices.writing_style.includes(n.writing_style), "请选择写法");
      need(
        n.writing_style !== "其他写法" || n.other_writing_explanation?.trim(),
        "其他写法必须说明写法及增量",
      );
      need(n.following_text_use !== "紧接着几段", "下文马上讲了，N1 应判不过");
    } else {
      need(
        !("writing_style" in n) && !("other_writing_explanation" in n),
        "写法和失败类型不能同时出现",
      );
      need(
        n.failure_types?.length &&
          n.failure_types.every((x) => f.choices.failure_types.includes(x)),
        "N1 不过至少选一个失败类型",
      );
      need(
        !n.failure_types.includes("其他") ||
          n.other_failure_explanation?.trim(),
        "失败类型其他必须写说明",
      );
      need(
        n.following_text_use !== "紧接着几段" ||
          n.failure_types.includes("下文马上讲了"),
        "缺少下文马上讲了失败类型",
      );
    }
  }
  function validate(r, f, old) {
    need(["rubric_uncovered","needs_verification","star"].every(k=>typeof r[k]==="boolean"),"标记字段无效");
    need(Object.keys(r.vetoes).sort().join() === "incorrect_information,reading_difficulty,spoiler" && Object.values(r.vetoes).every(x=>typeof x==="boolean"),"否决项无效");
    need(["reason","uncovered_reason"].every(k=>typeof r[k]==="string"),"理由无效");
    need(r.reading_difficulty.veto===r.vetoes.reading_difficulty,"费劲结论不一致");
    for(const [label,values] of Object.entries(r.unsure_sources))need(labels.includes(label)&&Array.isArray(values)&&values.length&&new Set(values).size===values.length&&values.every(x=>x==="manual"||(x==="automatic"&&label===labels[1])),"拿不准来源无效");

    need(
      r.review_completed && r.schema === "q1-note-judgment/1" && r.type === "N",
      "不是完整 Note 判定",
    );
    need(
      ["pass", "fail"].includes(r.first_impression.judgment) &&
        r.first_impression.locked_at,
      "缺少第一印象",
    );
    const d = r.reading_difficulty;
    let cursor = d.original_choice;
    need(difficulty.includes(cursor), "缺少读着费劲判断");
    for (const a of d.amendments) {
      need(
        a.from === cursor &&
          difficulty.includes(a.to) &&
          a.to !== cursor &&
          a.at,
        "费劲修改历史不连续",
      );
      cursor = a.to;
    }
    need(cursor === d.choice, "费劲最终值与历史不符");
    n1valid(r.n1, f);
    need(
      !r.rubric_uncovered || r.uncovered_reason?.trim(),
      "rubric 未覆盖必须写原因",
    );
    const derived = copy(r);
    derive(derived);
    for (const k of [
      "judgment",
      "vetoes",
      "unsure",
      "unsure_sources",
      "tags",
      "star",
    ])
      need(
        JSON.stringify(stable(r[k])) === JSON.stringify(stable(derived[k])),
        "自动结论、标签或标记不一致",
      );
    need(r.judgment === "pass" || !("tags" in r), "不过不能有标签");
    need(
      !r.tags || r.tags.every((x) => f.choices.tags.includes(x)),
      "标签选项无效",
    );
    for (const k of steps) {
      const s = r.steps[k];
      if (k === "tags" && r.judgment === "fail") {
        need(s?.status === "skipped_due_to_fail", "不过应跳过标签");
        continue;
      }
      need(
        s &&
          Number.isFinite(Date.parse(s.started_at)) &&
          Date.parse(s.completed_at) >= Date.parse(s.started_at) &&
          Number.isInteger(s.active_ms) &&
          s.active_ms >= 0,
        "步骤尚未完成",
      );
    }
    for (const k of ["n1", "spoiler"]) {
      const s = r.steps[k];
      need(
        s.viewed_following_text === !!s.following_text_views.length,
        "后文记录不一致",
      );
      for (const v of s.following_text_views)
        need(
          ["within_unit", "after_unit"].includes(v.scope) &&
            v.range.start.chapter_id === v.range.end.chapter_id &&
            v.range.end.chapter_id === r.original_source_range.end.chapter_id,
          "后文不能超过本章",
        );
    }
    if (old) {
      need(
        JSON.stringify(r.first_impression) ===
          JSON.stringify(old.first_impression),
        "第一印象已经锁定",
      );
      need(
        d.original_choice === old.reading_difficulty.original_choice &&
          JSON.stringify(
            d.amendments.slice(0, old.reading_difficulty.amendments.length),
          ) === JSON.stringify(old.reading_difficulty.amendments),
        "不能覆盖费劲修改历史",
      );
      for (const k of ["n1", "spoiler"])
        need(
          JSON.stringify(
            r.steps[k].following_text_views.slice(
              0,
              old.steps[k].following_text_views.length,
            ),
          ) === JSON.stringify(old.steps[k].following_text_views),
          "不能撤销后文暴露",
        );
    }
  }
  function start(r, i) {
    const s = (r.steps[steps[i]] ??= {});
    delete s.status;
    s.started_at ??= now();
    s.active_ms ??= 0;
    if ([2, 3].includes(i)) {
      s.viewed_following_text ??= false;
      s.following_text_views ??= [];
    }
  }
  function initial(c, m, manifestHash) {
    const identity = Object.fromEntries(
      [
        "review_session_id",
        "session_purpose",
        "batch_id",
        "annotator_id",
        "rubric_version",
        "rubric_sha256",
        "annotation_guide_sha256",
        "rubric_form_version",
        "rubric_form_sha256",
      ].map((k) => [k, m[k]]),
    );
    const r = {
      schema: "q1-note-judgment/1",
      ...identity,
      session_manifest_sha256: manifestHash,
      annotator_version: "q1-annotator/3.4",
      record_type: "marginalia",
      record_id: c.record_id,
      marginalia_id: c.record_id,
      type: "N",
      ...Object.fromEntries(
        [
          "window_id",
          "unit_key",
          "book_key",
          "body_text",
          "source_quote",
          "original_source_range",
        ].map((k) => [k, copy(c[k])]),
      ),
      randomization: {
        ...m.randomization,
        position: m.record_ids.indexOf(c.record_id) + 1,
      },
      context: {
        snapshot_sha256: m.context_sha256,
        observer_cutoff: c.context.observer_cutoff,
        original_notes_status: c.context.original_notes.status,
        original_note_ids: c.context.original_notes.items.map((n) => n.id),
        viewed_original_notes: false,
      },
      first_impression: {},
      reading_difficulty: {
        original_choice: null,
        choice: null,
        veto: false,
        paraphrase: "",
        rewrite: "",
        amendments: [],
      },
      n1: {},
      vetoes: {
        reading_difficulty: false,
        spoiler: false,
        incorrect_information: false,
      },
      unsure: [],
      unsure_sources: {},
      needs_verification: false,
      rubric_uncovered: false,
      uncovered_reason: "",
      judgment: null,
      star: false,
      reason: "",
      steps: {},
      review_completed: false,
    };
    start(r, 0);
    return { version: 0, stage: 0, record: r };
  }
  function transition(state, action, v = {}, ms = 0, f, c, rows = []) {
    const s = copy(state),
      r = s.record,
      i = s.stage;
    need(Number.isInteger(ms) && ms >= 0 && ms <= 86400000, "计时无效");
    if (i < 7) {
      start(r, i);
      r.steps[steps[i]].active_ms += ms;
    }
    if (action === "open") {
    } else if (action === "amend") {
      need(i >= 5, "完成核心判断后才能修正读着费劲");
      const d = r.reading_difficulty;
      need(
        difficulty.includes(v.choice) && v.choice !== d.choice,
        "请选择不同的费劲选项",
      );
      d.amendments.push({
        from: d.choice,
        to: v.choice,
        at: now(),
        reason: v.reason || "",
        active_ms: ms,
      });
      d.choice = v.choice;
      d.rewrite = v.rewrite ?? d.rewrite;
      derive(r);
      if (i === 7) {
        s.stage = 5;
        r.review_completed = false;
        delete r.steps.conclusion.completed_at;
      }
    } else if (action === "reopen") {
      const target = v.step ?? 2;
      need(Number.isInteger(target) && target >= 2 && target <= 6 && target < i, "只能修改已经完成的 N1 及后续步骤");
      s.stage = target;
      r.review_completed = false;
      steps.slice(target).forEach((k) => {
        r.steps[k] ??= {};
        delete r.steps[k].completed_at;
      });
    } else if (action === "following") {
      need([2, 3].includes(i), "只有 N1 和有剧透两步可以展开后文");
      need(["within_unit", "after_unit"].includes(v.scope), "后文范围无效");
      const parts = c.context[v.scope];
      need(parts.length, "本章此范围没有后文");
      const p = r.steps[steps[i]];
      p.viewed_following_text = true;
      p.following_text_views.push({
        opened_at: now(),
        scope: v.scope,
        range: { start: parts[0].range.start, end: parts.at(-1).range.end },
      });
    } else if (action === "notes") r.context.viewed_original_notes = true;
    else {
      need(
        ["save", "complete", "submit"].includes(action) && i < 7,
        "记录已提交，先重新检查",
      );
      const per = [
        ["judgment"],
        ["choice", "paraphrase", "rewrite"],
        ["n1"],
        ["spoiler"],
        ["incorrect_information", "needs_verification"],
        [],
        ["tags"],
      ];
      need(
        Object.keys(v).every((k) =>
          [
            "manual_unsure",
            "rubric_uncovered",
            "uncovered_reason",
            "reason",
            "star",
            ...per[i],
          ].includes(k),
        ),
        "不能修改锁定项或其他步骤的字段",
      );
      for (const k of [
        "rubric_uncovered",
        "star",
        "uncovered_reason",
        "reason",
      ])
        if (k in v) r[k] = v[k];
      if ("manual_unsure" in v) {
        const a = (r.unsure_sources[labels[i]] || []).filter(
          (x) => x !== "manual",
        );
        if (v.manual_unsure) a.push("manual");
        if (a.length) r.unsure_sources[labels[i]] = a;
        else delete r.unsure_sources[labels[i]];
      }
      if (i === 0 && v.judgment) {
        need(!r.first_impression.locked_at, "第一印象已经锁定");
        r.first_impression.judgment = v.judgment;
      }
      if (i === 1)
        for (const k of per[i]) if (k in v) r.reading_difficulty[k] = v[k];
      if (i === 2 && v.n1) {
        r.n1 = copy(v.n1);
        if (r.n1.following_text_use === "紧接着几段") {
          r.n1.judgment = "fail";
          delete r.n1.writing_style;
          delete r.n1.other_writing_explanation;
          r.n1.failure_types = [
            ...new Set([...(r.n1.failure_types || []), "下文马上讲了"]),
          ];
        }
      }
      if (i === 3 && "spoiler" in v) r.vetoes.spoiler = v.spoiler;
      if (i === 4) {
        if ("incorrect_information" in v)
          r.vetoes.incorrect_information = v.incorrect_information;
        if ("needs_verification" in v)
          r.needs_verification = v.needs_verification;
      }
      if (i === 6 && "tags" in v) {
        need(r.judgment === "pass" || !v.tags.length, "不过不能标标签");
        r.tags = v.tags;
      }
      derive(r);
      if (action !== "save") {
        need(
          !r.rubric_uncovered || r.uncovered_reason.trim(),
          "rubric 未覆盖必须写原因",
        );
        if (i === 0) {
          need(
            ["pass", "fail"].includes(r.first_impression.judgment),
            "请选择第一印象",
          );
          r.first_impression.locked_at = now();
        }
        if (i === 1) {
          need(
            difficulty.includes(r.reading_difficulty.choice),
            "请选择读着费劲的判断",
          );
          r.reading_difficulty.original_choice = r.reading_difficulty.choice;
        }
        if (i === 2) n1valid(r.n1, f);
        r.steps[steps[i]].completed_at = now();
        if (action === "complete") {
          need(i < 6, "标签之后请提交");
          s.stage++;
          if (s.stage === 6 && r.judgment === "fail")
            r.steps.tags = { status: "skipped_due_to_fail" };
          else start(r, s.stage);
        } else {
          need(i === 6, "请按顺序完成所有步骤");
          if (r.judgment === "fail")
            r.steps.tags = { status: "skipped_due_to_fail" };
          r.review_completed = true;
          const old = rows.findLast(
            (x) =>
              x.record_type === "marginalia" && x.record_id === r.record_id,
          );
          Object.assign(r, {
            revision: rows.length + 1,
            supersedes_revision: old?.revision ?? null,
            timestamp: now(),
            event_version: s.version + 1,
            annotator_version: "q1-annotator/3.4",
          });
          validate(r, f, old);
          s.stage = 7;
        }
      }
    }
    s.version++;
    return s;
  }
  const api = {
    steps,
    labels,
    difficulty,
    copy,
    need,
    stable,
    canonical,
    hash,
    derive,
    validate,
    n1valid,
    initial,
    transition,
  };
  root.Q1NoteProtocol = api;
  if (typeof module !== "undefined") module.exports = api;
})(globalThis);
