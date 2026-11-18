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
  function deriveLegacy(r) {
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
  function n1validLegacy(n, f) {
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
  function validateLegacy(r, f, old) {
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
    n1validLegacy(r.n1, f);
    need(
      !r.rubric_uncovered || r.uncovered_reason?.trim(),
      "rubric 未覆盖必须写原因",
    );
    const derived = copy(r);
    deriveLegacy(derived);
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
  const firstPass = ["复述得出", "复述不出或说偏"];
  const rewriteChoices = ["能改写得更直白", "改写不出"];
  const farWarning = "far_following_without_spoiler";
  const eventVersionBase = 2 ** 32;
  const isV2 = (r) => r.event_schema_version === 2;
  const readOnly = (s) => s.stage === 7 || !!s.discussionRequired;
  function invalid(message, step, code) {
    const error = Error(message);
    if (step !== undefined) error.step = step;
    if (code) error.code = code;
    throw error;
  }
  function dangerousFollowing(r) {
    return (
      r.n1.following_text_use === "更远后文，转第四步判剧透" &&
      r.checks?.spoiler === false
    );
  }
  function derive(r) {
    if (!isV2(r)) return deriveLegacy(r);
    const d = r.reading_difficulty;
    d.veto = r.vetoes.reading_difficulty =
      d.first_pass === firstPass[1] && d.rewrite_judgment === rewriteChoices[0];
    r.vetoes.spoiler = r.checks.spoiler === true;
    r.vetoes.incorrect_information = r.checks.incorrect_information === true;
    const manual = (r.unsure_sources[labels[1]] || []).includes("manual");
    delete r.unsure_sources[labels[1]];
    const sources = [
      ...(d.first_pass === firstPass[1] && d.rewrite_judgment === rewriteChoices[1]
        ? ["automatic"]
        : []),
      ...(manual ? ["manual"] : []),
    ];
    if (sources.length) r.unsure_sources[labels[1]] = sources;
    r.unsure = labels.filter((k) => r.unsure_sources[k]?.length);
    const veto =
      r.n1.judgment === "fail" ||
      Object.values(r.vetoes).some(Boolean) ||
      r.rubric_uncovered;
    const complete =
      firstPass.includes(d.first_pass) &&
      (d.first_pass === firstPass[0] || rewriteChoices.includes(d.rewrite_judgment)) &&
      r.n1.judgment === "pass" &&
      Object.values(r.checks).every((v) => typeof v === "boolean");
    r.judgment = veto ? "fail" : complete ? "pass" : null;
    if (r.judgment !== "pass") {
      delete r.tags;
      r.star = false;
    } else {
      r.tags ??= [];
      if (r.n1.following_text_use === "挂早了" && !r.tags.includes("锚点问题"))
        r.tags.push("锚点问题");
    }
    r.acknowledged_warnings ??= [];
    if (!dangerousFollowing(r))
      r.acknowledged_warnings = r.acknowledged_warnings.filter(
        (x) => x !== farWarning,
      );
  }
  function n1valid(n, f) {
    n1validLegacy(n, f);
    need(
      !n.failure_types?.includes("下文马上讲了") ||
        ["紧接着几段", "挂早了"].includes(n.following_text_use),
      "选择下文马上讲了时，用到后文应选紧接着几段或挂早了",
    );
  }
  function validateDifficulty(d, complete = true) {
    need(
      Object.keys(d).sort().join() ===
        "amendments,first_pass,locked_at,paraphrase,rewrite_judgment,rewrite_text,veto",
      "费劲字段无效",
    );
    need(firstPass.includes(d.first_pass), "请选择第一遍能否准确复述");
    need(
      typeof d.paraphrase === "string" && typeof d.rewrite_text === "string",
      "费劲文字无效",
    );
    need(
      d.first_pass === firstPass[0]
        ? d.rewrite_judgment === null
        : rewriteChoices.includes(d.rewrite_judgment),
      "请判断能否改写得更直白且不丢内容",
    );
    if (complete)
      need(Number.isFinite(Date.parse(d.locked_at)), "第一遍复述尚未锁定");
    need(Array.isArray(d.amendments), "改写修改历史无效");
    let cursor = d.amendments[0]?.from ?? d.rewrite_judgment;
    for (const a of d.amendments) {
      need(
        rewriteChoices.includes(a.from) &&
          rewriteChoices.includes(a.to) &&
          a.from === cursor &&
          a.to !== cursor &&
          Number.isFinite(Date.parse(a.at)) &&
          typeof a.reason === "string" &&
          Number.isInteger(a.active_ms) &&
          a.active_ms >= 0,
        "改写修改历史不连续",
      );
      cursor = a.to;
    }
    need(
      cursor === d.rewrite_judgment &&
        (d.first_pass !== firstPass[0] || !d.amendments.length),
      "改写最终值与历史不符",
    );
  }
  function validateStep(r, i, f) {
    try {
      if (i === 0)
        need(
          ["pass", "fail"].includes(r.first_impression.judgment),
          "请选择第一印象",
        );
      if (i === 1) validateDifficulty(r.reading_difficulty, false);
      if (i === 2) n1valid(r.n1, f);
      if (i === 3)
        need(typeof r.checks.spoiler === "boolean", "请选择有剧透或无剧透");
      if (i === 4)
        need(
          typeof r.checks.incorrect_information === "boolean" &&
            typeof r.needs_verification === "boolean",
          "请选择有错误信息或无错误信息",
        );
      if (i === 6)
        need(
          r.judgment === "fail" ||
            (r.judgment === "pass" &&
              Array.isArray(r.tags) &&
              r.tags.every((t) => f.choices.tags.includes(t))),
          "标签选项或最终结论无效",
        );
    } catch (error) {
      error.step = i;
      throw error;
    }
  }
  // Early v2 builds stored the radio answer in rewrite. Keep journal rows intact
  // for append-only comparison; normalize only the consumer's view.
  function normalizeRecord(row) {
    const d = row?.reading_difficulty;
    if (row?.event_schema_version !== 2 || !d || !Object.hasOwn(d, "rewrite")) return row;
    need(!Object.hasOwn(d, "rewrite_judgment"), "改写判断字段重复");
    const {rewrite, ...fields} = d;
    return {...row, reading_difficulty: {...fields, rewrite_judgment: rewrite}};
  }

  function validate(r, f, old, firstSubmitted) {
    r = normalizeRecord(r);
    old = normalizeRecord(old);
    need(
      r.event_schema_version === undefined || r.event_schema_version === 2,
      "事件协议版本无效",
    );
    if (!isV2(r)) {
      need(
        r.rubric_form_version !== "q1-v3.4.form.v2",
        "v2 表单必须写新版事件",
      );
      return validateLegacy(r, f, old && !isV2(old) ? old : undefined);
    }
    need(
      r.rubric_form_version === "q1-v3.4.form.v2",
      "新版事件必须绑定 v2 表单",
    );
    const required =
      "schema annotator_id annotator_version review_session_id session_purpose batch_id session_manifest_sha256 rubric_version rubric_sha256 annotation_guide_sha256 rubric_form_version rubric_form_sha256 record_type record_id marginalia_id window_id unit_key book_key revision supersedes_revision timestamp type source_quote body_text original_source_range randomization context first_impression reading_difficulty n1 vetoes unsure unsure_sources needs_verification rubric_uncovered uncovered_reason judgment star reason steps review_completed event_version event_schema_version checks legacy_inferences acknowledged_warnings".split(
        " ",
      );
    const allowed = new Set([
      ...required,
      "tags",
      "amendment_kind",
      "amendment_reason",
      "legacy_reading_difficulty",
    ]);
    need(
      required.every((key) => Object.hasOwn(r, key)) &&
        Object.keys(r).every((key) => allowed.has(key)),
      "判定字段缺失或包含未知字段",
    );
    need(
      r.review_completed && r.schema === "q1-note-judgment/1" && r.type === "N",
      "不是完整 Note 判定",
    );
    need(
      Number.isSafeInteger(r.event_version) &&
        r.event_version >= eventVersionBase,
      "新版事件序号无效",
    );
    need(
      ["pass", "fail"].includes(r.first_impression.judgment) &&
        r.first_impression.locked_at,
      "缺少第一印象",
    );
    validateDifficulty(r.reading_difficulty);
    need(
      Object.keys(r.checks).sort().join() === "incorrect_information,spoiler" &&
        Object.values(r.checks).every((v) => typeof v === "boolean"),
      "否决项必须分别判断",
    );
    need(
      Object.keys(r.vetoes).sort().join() ===
        "incorrect_information,reading_difficulty,spoiler" &&
        Object.values(r.vetoes).every((v) => typeof v === "boolean"),
      "否决项无效",
    );
    need(
      ["rubric_uncovered", "needs_verification", "star"].every(
        (k) => typeof r[k] === "boolean",
      ),
      "标记字段无效",
    );
    need(
      ["reason", "uncovered_reason"].every((k) => typeof r[k] === "string"),
      "理由无效",
    );
    need(
      !r.rubric_uncovered || r.uncovered_reason.trim(),
      "rubric 未覆盖必须写原因",
    );
    n1valid(r.n1, f);
    for (const [label, sources] of Object.entries(r.unsure_sources))
      need(
        labels.includes(label) &&
          Array.isArray(sources) &&
          sources.length &&
          new Set(sources).size === sources.length &&
          sources.every(
            (x) => x === "manual" || (x === "automatic" && label === labels[1]),
          ),
        "拿不准来源无效",
      );
    const derived = copy(r);
    derive(derived);
    for (const key of [
      "judgment",
      "vetoes",
      "unsure",
      "unsure_sources",
      "tags",
      "star",
      "acknowledged_warnings",
    ])
      need(
        canonical(r[key]) === canonical(derived[key]),
        "自动结论、标签或标记不一致",
      );
    need(
      r.reading_difficulty.veto === r.vetoes.reading_difficulty,
      "费劲结论不一致",
    );
    need(r.judgment === "pass" || !("tags" in r), "不过不能有标签");
    need(
      !r.tags || r.tags.every((t) => f.choices.tags.includes(t)),
      "标签选项无效",
    );
    need(
      Array.isArray(r.acknowledged_warnings) &&
        new Set(r.acknowledged_warnings).size ===
          r.acknowledged_warnings.length &&
        r.acknowledged_warnings.every((x) => x === farWarning),
      "确认警告无效",
    );
    need(
      !dangerousFollowing(r) || r.acknowledged_warnings.includes(farWarning),
      "请确认更远后文与无剧透的组合",
    );
    need(
      Array.isArray(r.legacy_inferences) &&
        r.legacy_inferences.every((x) => typeof x === "string" && x.trim()),
      "历史推断依据无效",
    );
    if ("legacy_reading_difficulty" in r)
      need(
        r.legacy_reading_difficulty &&
          typeof r.legacy_reading_difficulty === "object" &&
          !Array.isArray(r.legacy_reading_difficulty),
        "历史费劲判断无效",
      );
    for (const key of steps) {
      const step = r.steps[key];
      if (key === "tags" && r.judgment === "fail") {
        need(step?.status === "skipped_due_to_fail", "不过应跳过标签");
        continue;
      }
      need(
        step &&
          Number.isFinite(Date.parse(step.started_at)) &&
          Date.parse(step.completed_at) >= Date.parse(step.started_at) &&
          Number.isInteger(step.active_ms) &&
          step.active_ms >= 0,
        "步骤尚未完成",
      );
    }
    for (const key of ["n1", "spoiler"]) {
      const step = r.steps[key];
      need(
        step.viewed_following_text === !!step.following_text_views.length,
        "后文记录不一致",
      );
      for (const view of step.following_text_views)
        need(
          ["within_unit", "after_unit"].includes(view.scope) &&
            view.range.start.chapter_id === view.range.end.chapter_id &&
            view.range.end.chapter_id ===
              r.original_source_range.end.chapter_id,
          "后文不能超过本章",
        );
    }
    if (old || r.supersedes_revision != null)
      need(
        r.amendment_kind === "post_discussion" &&
          typeof r.amendment_reason === "string" &&
          r.amendment_reason.trim(),
        "讨论后改判必须写原因",
      );
    else
      need(
        !("amendment_kind" in r) && !("amendment_reason" in r),
        "首次提交不能伪装为讨论后修订",
      );
    if (old) {
      need(r.event_version > old.event_version, "后继事件序号必须递增");
      need(
        canonical(r.first_impression) === canonical(old.first_impression),
        "第一印象已经锁定",
      );
      if (isV2(old)) {
        for (const key of ["first_pass", "paraphrase", "locked_at"])
          need(
            r.reading_difficulty[key] === old.reading_difficulty[key],
            "第一遍复述已经锁定",
          );
        need(
          canonical(
            r.reading_difficulty.amendments.slice(
              0,
              old.reading_difficulty.amendments.length,
            ),
          ) === canonical(old.reading_difficulty.amendments),
          "不能覆盖改写修改历史",
        );
        const next =
          r.reading_difficulty.amendments[
            old.reading_difficulty.amendments.length
          ];
        if (next)
          need(
            next.from === old.reading_difficulty.rewrite_judgment,
            "改写修改历史起点不符",
          );
        else
          need(
            r.reading_difficulty.rewrite_judgment === old.reading_difficulty.rewrite_judgment,
            "改写变化缺少修改历史",
          );
      } else {
        const baseline = firstSubmitted || old,
          d = baseline.reading_difficulty;
        const expectedFirst =
          d.original_choice === difficulty[0] ? firstPass[0] : firstPass[1];
        need(
          r.reading_difficulty.first_pass === expectedFirst &&
            r.reading_difficulty.paraphrase === (d.paraphrase ?? ""),
          "历史第一遍复述映射不符",
        );
        if (baseline.steps.reading_difficulty.completed_at)
          need(
            r.reading_difficulty.locked_at ===
              baseline.steps.reading_difficulty.completed_at,
            "历史第一遍锁定时间不符",
          );
        const legacy = r.legacy_reading_difficulty;
        need(
          legacy?.original_choice === old.reading_difficulty.original_choice &&
            canonical(
              legacy.amendments.slice(
                0,
                old.reading_difficulty.amendments.length,
              ),
            ) === canonical(old.reading_difficulty.amendments),
          "不能覆盖历史费劲判断",
        );
      }
      need(
        canonical(
          (r.legacy_inferences || []).slice(
            0,
            (old.legacy_inferences || []).length,
          ),
        ) === canonical(old.legacy_inferences || []),
        "不能覆盖历史推断依据",
      );
      if (old.legacy_reading_difficulty)
        need(
          canonical(r.legacy_reading_difficulty) ===
            canonical(old.legacy_reading_difficulty),
          "不能覆盖历史费劲判断",
        );
      for (const key of ["n1", "spoiler"])
        need(
          canonical(
            r.steps[key].following_text_views.slice(
              0,
              old.steps[key].following_text_views.length,
            ),
          ) === canonical(old.steps[key].following_text_views),
          "不能撤销后文暴露",
        );
    }
  }
  function migrateRecord(record, options = {}) {
    const r = copy(record),
      baseline = options.firstSubmitted || options.submitted;
    if (!isV2(r)) {
      const old = copy(r.reading_difficulty),
        source = baseline?.reading_difficulty || old;
      const original = source.original_choice || old.original_choice,
        first = original || old.choice;
      const inferred = difficulty.includes(first)
        ? first === difficulty[0]
          ? firstPass[0]
          : firstPass[1]
        : null;
      const finalRewrite =
        old.choice === difficulty[0]
          ? null
          : rewriteChoices.includes(old.choice)
            ? old.choice
            : null;
      r.event_schema_version = 2;
      r.legacy_reading_difficulty = old;
      r.legacy_inferences = [
        ...(r.legacy_inferences || []),
        "第一遍复述由历史首次确认值推断；原记录和历史修改保留",
      ];
      r.reading_difficulty = {
        first_pass: inferred,
        locked_at: original
          ? baseline?.steps?.reading_difficulty?.completed_at ||
            r.steps.reading_difficulty?.completed_at ||
            now()
          : null,
        paraphrase: source.paraphrase ?? "",
        rewrite_judgment: inferred === firstPass[0] ? null : finalRewrite,
        rewrite_text: old.rewrite ?? "",
        veto: false,
        amendments: [],
      };
      if (
        original &&
        !baseline?.steps?.reading_difficulty?.completed_at &&
        !r.steps.reading_difficulty?.completed_at
      )
        r.legacy_inferences.push(
          "历史第一遍确认时间缺失；锁定时间记录本次转换时间",
        );
      if (typeof source.paraphrase !== "string")
        r.legacy_inferences.push("历史第一遍复述文本缺失，保留空白");
      if (
        original &&
        old.choice &&
        (original === difficulty[0]) !== (old.choice === difficulty[0])
      )
        r.legacy_inferences.push(
          "历史首次与最终值跨越第一遍类别；第一遍按首次确认映射，旧最终值不伪装为新的改写判断",
        );
      r.checks = {};
      for (const key of ["spoiler", "incorrect_information"]) {
        const completed = !!r.steps[key]?.completed_at;
        r.checks[key] =
          completed || r.vetoes[key] === true ? !!r.vetoes[key] : null;
        r.legacy_inferences.push(
          completed
            ? `${key} 由历史已完成步骤推断为${r.checks[key]}`
            : r.checks[key] === true
              ? `${key} 历史步骤未完成，保留已主动勾选的true`
              : `${key} 历史步骤未完成，旧默认值转为未判`,
        );
      }
      r.acknowledged_warnings = [];
    }
    if (baseline) {
      r.first_impression = copy(baseline.first_impression);
      if (isV2(baseline))
        for (const key of ["first_pass", "paraphrase", "locked_at"])
          r.reading_difficulty[key] = baseline.reading_difficulty[key];
    }
    if (options.identity)
      for (const key of ["rubric_form_version", "rubric_form_sha256"])
        if (options.identity[key] !== undefined) r[key] = options.identity[key];
    r.annotator_version = "q1-annotator/3.6";
    derive(r);
    return r;
  }
  function normalizeDraft(state, options = {}) {
    const s = copy(state);
    s.record = normalizeRecord(s.record);
    need(
      Number.isInteger(s.stage) && s.stage >= 0 && s.stage <= 7,
      "草稿步骤无效",
    );
    if (s.record.review_completed) s.stage = 7;
    s.discussion = !!s.discussion && !s.record.review_completed;
    s.discussionRequired =
      !s.discussion &&
      !s.record.review_completed &&
      !!(options.submitted || s.record.revision);
    if (!readOnly(s)) {
      s.record = migrateRecord(s.record, options);
      s.version = Math.max(s.version, eventVersionBase);
    }
    const r = s.record;
    const reached = steps.reduce(
      (max, key, index) =>
        r.steps[key]?.started_at || r.steps[key]?.completed_at
          ? Math.max(max, index)
          : max,
      Math.min(s.stage, 6),
    );
    s.maxUnlockedStage = Math.min(
      6,
      Math.max(
        reached,
        Number.isInteger(s.maxUnlockedStage) ? s.maxUnlockedStage : 0,
      ),
    );
    if (!r.first_impression.locked_at) s.maxUnlockedStage = 0;
    else if (
      !(isV2(r)
        ? r.reading_difficulty.locked_at
        : r.reading_difficulty.original_choice)
    )
      s.maxUnlockedStage = Math.min(1, s.maxUnlockedStage);
    if (
      !Number.isInteger(s.viewStep) ||
      s.viewStep < 0 ||
      (s.viewStep > s.maxUnlockedStage && !(s.stage === 7 && s.viewStep === 7))
    )
      s.viewStep = s.stage === 7 ? 7 : Math.min(s.stage, s.maxUnlockedStage);
    s.dirtySteps = [
      ...new Set(
        (s.dirtySteps || []).filter(
          (i) => Number.isInteger(i) && i >= 0 && i <= 6,
        ),
      ),
    ].sort();
    s.pendingActiveMs ??= {};
    if (!Array.isArray(s.anchorTagSources))
      s.anchorTagSources = r.tags?.includes("锚点问题") ? ["legacy"] : [];
    return s;
  }
  function deriveDraft(s) {
    const r = s.record,
      sources = new Set(s.anchorTagSources.filter((x) => x !== "automatic"));
    if (r.n1.following_text_use === "挂早了") sources.add("automatic");
    if (r.tags?.includes("锚点问题") && !sources.size)
      r.tags = r.tags.filter((t) => t !== "锚点问题");
    derive(r);
    if (r.judgment !== "pass") s.anchorTagSources = [];
    else {
      s.anchorTagSources = [...sources];
      if (sources.size && !r.tags.includes("锚点问题")) r.tags.push("锚点问题");
    }
  }
  function semantic(r) {
    return canonical(
      Object.fromEntries(
        [
          "first_impression",
          "reading_difficulty",
          "n1",
          "checks",
          "vetoes",
          "unsure_sources",
          "needs_verification",
          "rubric_uncovered",
          "uncovered_reason",
          "reason",
          "tags",
          "star",
          "amendment_reason",
        ].map((k) => [k, r[k]]),
      ),
    );
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
      annotator_version: "q1-annotator/3.6",
      event_schema_version: 2,
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
        first_pass: null,
        locked_at: null,
        paraphrase: "",
        rewrite_judgment: null,
        rewrite_text: "",
        veto: false,
        amendments: [],
      },
      checks: { spoiler: null, incorrect_information: null },
      acknowledged_warnings: [],
      legacy_inferences: [],
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
    return {
      version: eventVersionBase,
      stage: 0,
      viewStep: 0,
      maxUnlockedStage: 0,
      dirtySteps: [],
      pendingActiveMs: {},
      anchorTagSources: [],
      discussion: false,
      discussionRequired: false,
      record: r,
    };
  }
  function transition(
    state,
    action,
    v = {},
    ms = 0,
    f,
    c,
    rows = [],
    options = {},
  ) {
    const submitted =
      options.submitted ||
      rows.findLast(
        (x) =>
          x.record_type === "marginalia" &&
          x.record_id === state.record.record_id,
      );
    const firstSubmitted =
      options.firstSubmitted ||
      rows.find(
        (x) =>
          x.record_type === "marginalia" &&
          x.record_id === state.record.record_id,
      );
    const migration = { ...options, submitted, firstSubmitted },
      s = normalizeDraft(state, migration);
    let r = s.record;
    const i = s.viewStep;
    need(Number.isInteger(ms) && ms >= 0 && ms <= 86400000, "计时无效");
    if (i < 7) s.pendingActiveMs[i] = (s.pendingActiveMs[i] || 0) + ms;
    const accountTime = (step) => {
      start(r, step);
      r.steps[steps[step]].active_ms += s.pendingActiveMs[step] || 0;
      delete s.pendingActiveMs[step];
    };
    const markDirty = (step) => {
      s.dirtySteps = [...new Set([...s.dirtySteps, step])].sort();
      r.review_completed = false;
    };
    if (action === "navigate") {
      need(
        Number.isInteger(v.step) && v.step >= 0 && v.step <= s.maxUnlockedStage,
        "只能查看已开放步骤",
      );
      s.viewStep = v.step;
    } else if (action === "open") {
      // Read-only visits never migrate journal rows.
    } else if (action === "begin_discussion") {
      need(
        readOnly(s) && (submitted || r.revision || r.review_completed),
        "提交后才能进入讨论后改判",
      );
      r = migrateRecord(r, migration);
      s.record = r;
      s.version = Math.max(
        s.version,
        eventVersionBase,
        submitted?.event_version || 0,
      );
      s.stage = 6;
      s.viewStep = 6;
      s.maxUnlockedStage = 6;
      s.discussion = true;
      s.discussionRequired = false;
      r.review_completed = false;
      r.amendment_kind = "post_discussion";
      r.amendment_reason = "";
      markDirty(6);
    } else if (readOnly(s)) {
      if (!["following", "notes"].includes(action))
        invalid("已提交判定为只读；请先进入讨论后改判", undefined, "READ_ONLY");
      if (action === "following") {
        need([2, 3].includes(i), "只有 N1 和有剧透两步可以展开后文");
        need(
          ["within_unit", "after_unit"].includes(v.scope) &&
            c.context[v.scope]?.length,
          "本章此范围没有后文",
        );
      }
    } else if (action === "reopen") {
      const target = v.step ?? 2;
      need(
        Number.isInteger(target) && target >= 1 && target <= s.maxUnlockedStage,
        "只能返回已经开放的第二步及后续步骤",
      );
      s.viewStep = target;
    } else if (action === "amend") {
      need(s.maxUnlockedStage >= 2, "完成读着费劲后才能修正");
      const judgment = v.rewrite_judgment ?? v.choice,
        d = r.reading_difficulty;
      need(
        d.first_pass === firstPass[1] &&
          rewriteChoices.includes(judgment) &&
          judgment !== d.rewrite_judgment,
        "请选择不同的改写判断",
      );
      if (rewriteChoices.includes(d.rewrite_judgment)) {
        d.amendments.push({
          from: d.rewrite_judgment,
          to: judgment,
          at: now(),
          reason: v.reason || "",
          active_ms: ms,
        });
      }
      d.rewrite_judgment = judgment;
      if (v.rewrite_text !== undefined) d.rewrite_text = v.rewrite_text;
      accountTime(1);
      markDirty(1);
      deriveDraft(s);
    } else if (action === "following") {
      need([2, 3].includes(i), "只有 N1 和有剧透两步可以展开后文");
      need(["within_unit", "after_unit"].includes(v.scope), "后文范围无效");
      const parts = c.context[v.scope];
      need(parts.length, "本章此范围没有后文");
      accountTime(i);
      r.steps[steps[i]].viewed_following_text = true;
      r.steps[steps[i]].following_text_views.push({
        opened_at: now(),
        scope: v.scope,
        range: { start: parts[0].range.start, end: parts.at(-1).range.end },
      });
      markDirty(i);
    } else if (action === "notes") {
      if (!r.context.viewed_original_notes) {
        r.context.viewed_original_notes = true;
        markDirty(i);
      }
    } else {
      need(["save", "complete", "submit"].includes(action), "未知操作");
      const before = semantic(r),
        previousResult = canonical([r.judgment, r.tags, r.star]);
      const per = [
        ["judgment"],
        ["first_pass", "paraphrase", "rewrite_judgment", "rewrite_text"],
        ["n1"],
        ["spoiler"],
        ["incorrect_information", "needs_verification"],
        [],
        ["tags", "acknowledge_far_following"],
      ];
      need(
        Object.keys(v).every((k) =>
          [
            "manual_unsure",
            "rubric_uncovered",
            "uncovered_reason",
            "reason",
            "star",
            "amendment_reason",
            ...per[i],
          ].includes(k),
        ),
        "不能修改锁定项或其他步骤的字段",
      );
      for (const key of [
        "rubric_uncovered",
        "star",
        "uncovered_reason",
        "reason",
      ]) {
        if (key in v) r[key] = v[key];
      }
      if ("amendment_reason" in v) {
        need(s.discussion, "只有讨论后改判可填写修订原因");
        r.amendment_reason = v.amendment_reason;
      }
      if ("manual_unsure" in v) {
        const a = (r.unsure_sources[labels[i]] || []).filter(
          (x) => x !== "manual",
        );
        if (v.manual_unsure) a.push("manual");
        if (a.length) r.unsure_sources[labels[i]] = a;
        else delete r.unsure_sources[labels[i]];
      }
      if (i === 0 && "judgment" in v) {
        need(
          !r.first_impression.locked_at ||
            v.judgment === r.first_impression.judgment,
          "第一印象已经锁定",
        );
        r.first_impression.judgment = v.judgment;
      }
      if (i === 1) {
        const d = r.reading_difficulty;
        if (d.locked_at) {
          for (const key of ["first_pass", "paraphrase"]) {
            need(!(key in v) || v[key] === d[key], "第一遍复述已经锁定");
          }
        }
        if ("first_pass" in v) {
          need(firstPass.includes(v.first_pass), "请选择第一遍能否准确复述");
          d.first_pass = v.first_pass;
        }
        if ("paraphrase" in v) d.paraphrase = v.paraphrase;
        if ("rewrite_judgment" in v) {
          need(
            v.rewrite_judgment === null || rewriteChoices.includes(v.rewrite_judgment),
            "改写选项无效",
          );
          need(
            d.first_pass !== firstPass[0] || v.rewrite_judgment === null,
            "一遍能复述不需要改写判断",
          );
          need(
            !d.locked_at ||
              d.first_pass !== firstPass[1] ||
              d.rewrite_judgment === null ||
              v.rewrite_judgment !== null,
            "已确认的改写判断不能清空",
          );
          if (
            d.locked_at &&
            rewriteChoices.includes(d.rewrite_judgment) &&
            rewriteChoices.includes(v.rewrite_judgment) &&
            v.rewrite_judgment !== d.rewrite_judgment
          ) {
            d.amendments.push({
              from: d.rewrite_judgment,
              to: v.rewrite_judgment,
              at: now(),
              reason: v.reason || "",
              active_ms: ms,
            });
          }
          d.rewrite_judgment = v.rewrite_judgment;
        }
        if (d.first_pass === firstPass[0]) d.rewrite_judgment = null;
        if ("rewrite_text" in v) d.rewrite_text = v.rewrite_text;
      }
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
      if (i === 3 && "spoiler" in v) r.checks.spoiler = v.spoiler;
      if (i === 4) {
        if ("incorrect_information" in v)
          r.checks.incorrect_information = v.incorrect_information;
        if ("needs_verification" in v)
          r.needs_verification = v.needs_verification;
      }
      if (i === 6 && "tags" in v) {
        need(r.judgment === "pass" || !v.tags.length, "不过不能标标签");
        const had = r.tags?.includes("锚点问题"),
          has = v.tags.includes("锚点问题");
        if (has && !had) s.anchorTagSources = ["manual"];
        else if (!has) s.anchorTagSources = [];
        r.tags = copy(v.tags);
      }
      if (semantic(r) !== before) deriveDraft(s);
      if (semantic(r) !== before) {
        need(i !== 0 || !r.first_impression.locked_at, "第一印象已经锁定");
        accountTime(i);
        markDirty(i);
        if (previousResult !== canonical([r.judgment, r.tags, r.star])) {
          for (const step of [5, 6]) {
            if (
              r.steps[steps[step]]?.completed_at ||
              r.steps[steps[step]]?.status
            ) {
              markDirty(step);
            }
          }
        }
      }
      if (action === "complete") {
        need(i < 6, "标签之后请提交");
        if (i === s.stage) {
          validateStep(r, i, f);
          need(
            !r.rubric_uncovered || r.uncovered_reason.trim(),
            "rubric 未覆盖必须写原因",
          );
          accountTime(i);
          if (i === 0) r.first_impression.locked_at = now();
          if (i === 1) r.reading_difficulty.locked_at ??= now();
          r.steps[steps[i]].completed_at = now();
          s.dirtySteps = s.dirtySteps.filter((step) => step !== i);
          s.stage++;
          s.maxUnlockedStage = Math.max(
            s.maxUnlockedStage,
            Math.min(s.stage, 6),
          );
          if (s.stage === 6 && r.judgment === "fail")
            r.steps.tags = { status: "skipped_due_to_fail" };
          else start(r, s.stage);
        }
        s.viewStep = Math.min(i + 1, s.maxUnlockedStage);
      } else if (action === "submit") {
        need(i === 6 && s.maxUnlockedStage === 6, "请按顺序完成所有步骤后提交");
        for (let step = 0; step <= 6; step++) validateStep(r, step, f);
        if (r.rubric_uncovered && !r.uncovered_reason.trim())
          invalid("rubric 未覆盖必须写原因", 6);
        if (s.discussion && !r.amendment_reason?.trim())
          invalid("讨论后改判必须写原因", 6);
        if (
          dangerousFollowing(r) &&
          !r.acknowledged_warnings.includes(farWarning)
        ) {
          if (v.acknowledge_far_following !== true) {
            const e = Error("更远后文与无剧透的组合需要确认");
            e.code = "ACKNOWLEDGEMENT_REQUIRED";
            e.warning = farWarning;
            e.step = 6;
            throw e;
          }
          r.acknowledged_warnings.push(farWarning);
        }
        accountTime(6);
        const confirm = new Set([
          ...s.dirtySteps,
          ...steps.flatMap((key, step) =>
            !r.steps[key]?.completed_at ? [step] : [],
          ),
        ]);
        for (const step of confirm) {
          if (step === 0 || (step === 6 && r.judgment === "fail")) continue;
          accountTime(step);
          r.steps[steps[step]].completed_at = now();
        }
        if (r.judgment === "fail")
          r.steps.tags = { status: "skipped_due_to_fail" };
        else r.steps.tags.completed_at = now();
        r.review_completed = true;
        Object.assign(r, {
          revision: rows.length + 1,
          supersedes_revision: submitted?.revision ?? null,
          timestamp: now(),
          event_version: s.version + 1,
          annotator_version: "q1-annotator/3.6",
          event_schema_version: 2,
        });
        validate(r, f, submitted, firstSubmitted);
        s.stage = 7;
        s.viewStep = 7;
        s.maxUnlockedStage = 6;
        s.dirtySteps = [];
        s.discussion = false;
        s.discussionRequired = false;
      }
    }
    s.version++;
    return s;
  }
  const api = {
    steps,
    labels,
    difficulty,
    firstPass,
    rewriteChoices,
    farWarning,
    eventVersionBase,
    dangerousFollowing,
    readOnly,
    normalizeRecord,
    migrateRecord,
    copy,
    need,
    stable,
    canonical,
    hash,
    derive,
    validate,
    n1valid,
    initial,
    normalizeDraft,
    transition,
  };
  root.Q1NoteProtocol = api;
  if (typeof module !== "undefined") module.exports = api;
})(globalThis);
