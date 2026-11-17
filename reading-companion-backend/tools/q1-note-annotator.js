/* Field renderer shared by the offline v3.4 adapter. */
globalThis.Q1NoteView = async function (host, session) {
  const abort = new AbortController();
  /* v3.4 field renderer hosted by the original offline annotator. */
  ("use strict");
  const $ = (id) => host.querySelector("#" + id);
  let boot,
    data,
    index = 0,
    dirty = false,
    timer,
    active = 0,
    clock = performance.now(),
    busy = false,
    editEpoch = 0,
    interactionEpoch = 0,
    composing = false,
    inspecting = null;
  const labels = [
    "第一印象",
    "读着费劲",
    "N1",
    "有剧透",
    "有错误信息",
    "结论",
    "标签",
  ];
  const preferenceKey = "q1-note-ui-help/1";
  let helpPreferences = {};
  try {
    helpPreferences = JSON.parse(localStorage.getItem(preferenceKey) || "{}") || {};
    if (typeof helpPreferences !== "object" || Array.isArray(helpPreferences))
      helpPreferences = {};
  } catch {}
  const outcomeLabel = (value) => ({ pass: "过", fail: "不过" }[value] || "未判定");
  const difficultyLabel = (value) => ({
    "一遍能复述": "读一遍能准确复述意思（不否决）",
    "能改写得更直白": "读一遍说不出或说偏了，但能改写得更直白且不丢内容（否决）",
    "改写不出": "读一遍说不出或说偏了；想法本身复杂，表达已尽量清楚，无法更直白且不丢内容（不否决，标拿不准）",
  }[value] || value || "未判定");
  function stepHint(spec) {
    if (spec.id === "conclusion")
      return "N1 过，且读着费劲、有剧透、有错误信息均未勾选，结论才是过。rubric 未覆盖会强制不过；待核实不影响结论。";
    return spec.help.split("\n").find(line => line.trim())?.replaceAll("**", "") || "";
  }
  function rememberFocus() {
    const el = host.activeElement;
    if (!el) return null;
    return {el, id:el.id, name:el.name, value:el.value,
      start:el.selectionStart, end:el.selectionEnd};
  }
  function restoreFocus(f) {
    if (!f || (host.activeElement && host.activeElement !== f.el)) return;
    const target = f.id ? $(f.id) : [...host.querySelectorAll("input")]
      .find(e => e.name === f.name && e.value === f.value);
    if (!target) { focusDecision(); return; }
    target.focus({preventScroll:true});
    if (typeof f.start === "number" && target.setSelectionRange)
      target.setSelectionRange(f.start, f.end);
  }
  function focusGroup(name) {
    const all = [...host.querySelectorAll(`#workflow [name="${name}"]`)].filter(e=>!e.disabled);
    const el = all.find(e=>e.checked) || all[0];
    if (el) { el.focus(); el.scrollIntoView({block:"nearest"}); }
  }
  function focusMissing() {
    const missing = [...host.querySelectorAll('textarea')]
      .find(e => e.labels?.[0]?.textContent.includes('必填') && !e.value.trim());
    if (missing) return focusField(missing.id);
    for (const name of ['first','difficulty','followingUse','n1','style','failure']) {
      const group = [...host.querySelectorAll(`#workflow [name="${name}"]`)];
      if (group.length && !group.some(e=>e.checked)) return focusGroup(name);
    }
    focusDecision();
  }
  function focusDecision() {
    const title = $("workflow").querySelector("h2");
    if (title) {
      title.tabIndex = -1;
      title.focus({ preventScroll: true });
      title.scrollIntoView({ block: "nearest" });
    }
  }
  function locateAnchor() {
    const anchor = $("sourceText").querySelector("mark");
    $("anchorStatus").hidden = !!anchor;
    $("anchorStatus").textContent = anchor ? "" : "未找到可定位锚点，请查看原文。";
    if (anchor) {
      const reader = $("readerScroll");
      if (innerWidth >= 960)
        reader.scrollTop += anchor.getBoundingClientRect().top
          - reader.getBoundingClientRect().top - reader.clientHeight * 0.45;
      else anchor.scrollIntoView({ block: "center" });
    }
  }
  function node(tag, text, cls) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }
  function helpContent(text) {
    const host = node("div", undefined, "helpContent");
    for (const line of text.split("\n").filter((x) => x.trim())) {
      const p = node("p");
      for (const [i, part] of line.split(/\*\*(.*?)\*\*/g).entries()) {
        p.append(i % 2 ? node("strong", part) : document.createTextNode(part));
      }
      host.append(p);
    }
    return host;
  }
  function shownError(error) {
    const validation = error.code === "FORM_VALIDATION";
    $("status").textContent = validation ? "请检查判定内容" : "保存失败 · 请重试";
    $("retryVisible").hidden = validation;
    $("saveError").hidden = false;
    $("error").hidden = false;
    $("error").textContent = error.message;
    if (validation) focusMissing();
  }
  function tick() {
    const t = performance.now();
    if (!document.hidden) active += t - clock;
    clock = t;
  }
  function elapsed() {
    tick();
    const n = Math.round(active);
    active = 0;
    return n;
  }
  document.addEventListener(
    "visibilitychange",
    () => {
      const t = performance.now();
      if (document.hidden) active += t - clock;
      clock = t;
      if (dirty && !busy && !composing) save().catch(shownError);
    },
    { signal: abort.signal },
  );
  const api = (path, body) => session.api(path, body);
  function textArea(parent, id, label, value = "") {
    const shortcut = {paraphrase:"Y",n1Paraphrase:"Y",rewrite:"I",reason:"M",n1Reason:"R"}[id];
    parent.append(node("label", label + (shortcut ? ` · ${shortcut}` : ""), "text"));
    parent.lastChild.htmlFor = id;
    const t = node("textarea");
    t.id = id;
    t.value = value;
    t.rows = 2;
    parent.append(t);
    return t;
  }
  function check(parent, name, label, checked = false) {
    const l = node("label", undefined, "option"),
      i = node("input");
    i.type = "checkbox";
    i.name = name;
    i.checked = checked;
    l.append(i, node("span", label));
    parent.append(l);
    return i;
  }
  function radios(parent, name, title, values, value) {
    const f = node("fieldset");
    const keys = {difficulty:"D",followingUse:"B",style:"W"};
    f.append(node("legend", title + (keys[name] ? ` · ${keys[name]}` : "")));
    for (const v of values) {
      const l = node("label", undefined, "option"),
        i = node("input");
      i.type = "radio";
      i.name = name;
      i.value = v;
      i.checked = value === v;
      l.append(
        i,
        node("span", v === "pass" ? "过 · P" : v === "fail" ? "不过 · F" : name === "difficulty" ? `${difficultyLabel(v)} · ${["Q", "G", "Z"][values.indexOf(v)]}` : v),
      );
      f.append(l);
    }
    parent.append(f);
  }
  function get(name) {
    return host.querySelector(`#workflow input[name="${name}"]:checked`)?.value;
  }
  function checked(name) {
    return !!host.querySelector(`#workflow input[name="${name}"]`)?.checked;
  }
  function segments(host, parts) {
    host.replaceChildren();
    let para, last;
    for (const p of parts) {
      const key = `${p.range.start.chapter_id}:${p.range.start.paragraph_index}`;
      if (key !== last) {
        para = node("p");
        host.append(para);
        last = key;
      }
      para.append(
        p.anchor ? node("mark", p.text) : document.createTextNode(p.text),
      );
    }
  }
  function collect() {
    const s = data.state.stage,
      r = data.state.record;
    if (s === 7) return {};
    const v = {
      manual_unsure: checked("manualUnsure"),
      rubric_uncovered: checked("uncovered"),
      uncovered_reason: $("uncoveredReason")?.value ?? r.uncovered_reason,
      reason: $("reason")?.value ?? r.reason,
    };
    if (host.querySelector("[name=star]")) v.star = checked("star");
    if (s === 0 && get("first")) v.judgment = get("first");
    if (s === 1) {
      if (get("difficulty")) v.choice = get("difficulty");
      v.paraphrase = $("paraphrase").value;
      v.rewrite = $("rewrite").value;
    }
    if (s === 2) {
      const n = {
        following_text_use: get("followingUse") ?? null,
        judgment: get("n1") ?? null,
        paraphrase: $("n1Paraphrase").value,
        reason: $("n1Reason").value,
      };
      if (n.judgment === "pass") {
        n.writing_style = get("style") ?? null;
        if (n.writing_style === "其他写法")
          n.other_writing_explanation = $("otherWriting")?.value ?? "";
      }
      if (n.judgment === "fail") {
        n.failure_types = [
          ...host.querySelectorAll("[name=failure]:checked"),
        ].map((x) => x.value);
        if (n.failure_types.includes("其他"))
          n.other_failure_explanation = $("otherFailure")?.value ?? "";
      }
      v.n1 = n;
    }
    if (s === 3) v.spoiler = checked("spoiler");
    if (s === 4) {
      v.incorrect_information = checked("incorrect");
      v.needs_verification = checked("verification");
    }
    if (s === 6 && r.judgment === "pass")
      v.tags = [...host.querySelectorAll("[name=tag]:checked")].map(
        (x) => x.value,
      );
    return v;
  }
  async function post(action, values = {}, renderAfter = true) {
    if (busy) throw Error("正在保存，请稍候");
    const epoch = editEpoch;
    const duration = elapsed();
    let succeeded = false;
    const controls =
      action === "save"
        ? []
        : [...host.querySelectorAll("input,textarea,select")].map((e) => [
            e,
            e.disabled,
          ]);
    controls.forEach(([e]) => (e.disabled = true));
    busy = true;
    $("status").textContent = "正在保存…";
    host.querySelectorAll("button").forEach((b) => (b.disabled = true));
    try {
      const result = await api("/action", {
        id: boot.record_ids[index],
        action,
        values,
        version: data?.state.version,
        active_ms: duration,
      });
      data = result;
      succeeded = true;
      dirty = editEpoch !== epoch;
      $("error").hidden = true;
      $("saveError").hidden = true;
      if (renderAfter && !dirty) {
        const focus = rememberFocus();
        render();
        if (action === "save") restoreFocus(focus);
      }
      else updateStatus();
      return result;
    } catch (e) {
      active += duration;
      $("status").textContent = e.code === "FORM_VALIDATION"
        ? "请检查判定内容" : "保存失败 · 请重试";
      throw e;
    } finally {
      busy = false;
      controls.forEach(([e, disabled]) => {
        if (e.isConnected) e.disabled = disabled;
      });
      host.querySelectorAll("button").forEach((b) => (b.disabled = false));
      updateNavigation();
      $("prev").disabled = index === 0;
      $("next").disabled = index === boot.record_ids.length - 1;
      if (dirty && succeeded) {
        clearTimeout(timer);
        timer = setTimeout(() => save(true).catch(shownError), 700);
      }
    }
  }
  function updateStatus() {
    $("status").textContent = dirty ? "草稿尚未保存" : "浏览器和文件已同步";
  }
  async function save(renderAfter = false) {
    clearTimeout(timer);
    if (!dirty) return;
    if (busy || composing) return;
    await post("save", collect(), renderAfter);
  }
  async function flush() {
    clearTimeout(timer);
    if (busy) throw Error("正在保存，请稍候再操作");
    if (dirty) await save();
    if (data && $("unitNote").value !== data.unit_note) {
      await api("/action", {
        id: boot.record_ids[index],
        action: "unit_note",
        values: { remarks: $("unitNote").value },
      });
      data.unit_note = $("unitNote").value;
    }
  }
  async function openCase(i) {
    if (i < 0 || i >= boot.record_ids.length) return;
    await flush();
    busy = true;
    try {
      const result = await api("/action", {
        id: boot.record_ids[i],
        action: "open",
      });
      index = i;
      data = result;
    } finally {
      busy = false;
    }
    active = 0;
    clock = performance.now();
    render();
    $("prev").disabled = index === 0;
    $("next").disabled = index === boot.record_ids.length - 1;
    $("notePreview").open = false;
    $("caseTitle").scrollIntoView({ block: "nearest" });
    requestAnimationFrame(locateAnchor);
  }
  function render() {
    const sourceScroll = $("readerScroll").scrollTop;
    requestAnimationFrame(() => { $("readerScroll").scrollTop = sourceScroll; });
    inspecting = null;
    updateNavigation();
    requestAnimationFrame(updateLayout);
    const s = data.state.stage,
      r = data.state.record,
      c = boot.form.choices;
    $("position").textContent = `${index + 1} / ${boot.record_ids.length} 条`;
    $("purpose").textContent =
      boot.purpose === "test" ? "测试会话" : "正式会话";
    $("book").textContent = data.case.book;
    $("chapter").textContent = data.case.chapter_title;
    $("body").textContent = data.case.body_text;
    $("previewBody").textContent = data.case.body_text;
    $("decisionGo").textContent = "定位当前判定";
    segments($("sourceText"), data.prefix);
    $("chapter").hidden = $("sourceText").firstElementChild?.textContent.trim() === data.case.chapter_title?.trim();
    segments($("recentText"), data.recent);
    $("olderText").replaceChildren();
    $("earlier").open = false;
    $("moreEarlier").hidden = !data.earlier_count;
    $("notes").open = false;
    $("notesText").replaceChildren();
    $("noteStatus").textContent =
      data.notes_status === "resolved" ? "可查看" : "未解析或部分未解析";
    $("unitNote").value = data.unit_note;
    const f = $("following");
    f.replaceChildren();
    if (s === 2 || s === 3) {
      f.append(
        node(
          "p",
          "后文最多展开到本章结束。更远的后文靠你对这本书的了解。",
          "muted",
        ),
      );
      for (const scope of ["within_unit", "after_unit"]) {
        const button = node(
          "button",
          scope === "within_unit" ? "展开单元内后文" : "展开单元外后文",
          "followingControl",
        );
        button.type = "button";
        button.id = "following-" + scope;
        button.hidden = !data.has_following[scope];
        const content = node("div", undefined, "followingText");
        content.hidden = true;
        button.onclick = async () => {
          try {
            if (!content.hidden) {
              content.hidden = true;
              button.textContent = button.textContent.replace("收起", "展开");
              return;
            }
            await flush();
            const result = await post("following", { scope }, false);
            segments(content, result.following);
            content.hidden = false;
            button.textContent = button.textContent.replace("展开", "收起");
          } catch (e) {
            shownError(e);
          }
        };
        f.append(button, content);
      }
    } else if (s < 2)
      f.append(
        node(
          "p",
          "锚点之后的原文已折叠。完成“读着费劲”后，在 N1 或有剧透步骤按需查看。",
          "muted",
        ),
      );
    const w = $("workflow");
    w.replaceChildren();
    if (s > 0)
      w.append(
        node(
          "p",
          `第一印象：${r.first_impression.judgment === "pass" ? "过" : "不过"} · 已锁定`,
          "locked",
        ),
      );
    $("reviewActions").replaceChildren();
    if (s === 7) {
      w.append(
        node("h2", "本条已提交"),
        node(
          "p",
          r.judgment === "pass" ? "结论：过" : "结论：不过",
          `result ${r.judgment}`,
        ),
      );
      w.append(
        node(
          "p",
          `读着费劲：${difficultyLabel(r.reading_difficulty.choice)}；修改 ${r.reading_difficulty.amendments.length} 次。`,
          "muted",
        ),
      );
      if (r.tags) w.append(node("p", `标签：${r.tags.join("、") || "无"}`));
      if (r.star) w.append(node("p", "★ 范例级批注"));
      if (r.unsure.length)
        w.append(
          node(
            "p",
            `拿不准：${r.unsure.map((k) => `${k}（${r.unsure_sources[k].map((s) => (s === "automatic" ? "自动" : "手动")).join("、")}）`).join("；")}`,
            "muted",
          ),
        );
      const b = node("button", "重新检查 N1 及后续项");
      b.onclick = () => post("reopen").catch(shownError);
      w.append(b);
      amendControls(w, r);
      updateStatus();
      return;
    }
    const spec = boot.form.steps[s];
    w.append(
      node("div", `第 ${s + 1} / 7 步`, "eyebrow"),
      node("h2", s === 6 && r.judgment === "fail" ? "提交检查" : spec.label),
    );
    if (s === 0) w.append(node("p", spec.help));
    else {
      const help = node("details", undefined, "help");
      help.open = helpPreferences[spec.id] === true;
      help.addEventListener("toggle", () => {
        if (!help.isConnected) return;
        helpPreferences[spec.id] = help.open;
        try { localStorage.setItem(preferenceKey, JSON.stringify(helpPreferences)); } catch {}
      });
      w.append(node("p", stepHint(spec), "stepHint"));
      help.append(
        node("summary", `完整判定说明 · rubric ${spec.section}`),
        helpContent(spec.help),
      );
      w.append(help);
    }
    if (s === 0)
      radios(
        w,
        "first",
        "第一遍读完，直觉是？",
        ["pass", "fail"],
        r.first_impression.judgment,
      );
    if (s === 1) {
      radios(
        w,
        "difficulty",
        "就用刚才那一遍，马上判断",
        c.reading_difficulty,
        r.reading_difficulty.choice,
      );
      w.append(
        node(
          "p",
          "第三项指想法本身就绕、表达已尽量清楚，不是仅仅自己暂时不会改写；不勾否决，自动勾拿不准。",
          "muted",
        ),
      );
      textArea(
        w,
        "paraphrase",
        "一遍之后的复述（选填）",
        r.reading_difficulty.paraphrase,
      );
      textArea(
        w,
        "rewrite",
        "更直白的改写（选填）",
        r.reading_difficulty.rewrite,
      );
    }
    if (s === 2) {
      const n = r.n1;
      radios(
        w,
        "followingUse",
        "用到后文",
        c.following_text_use,
        n.following_text_use,
      );
      w.append(
        node(
          "p",
          "挂早了：按挪到合适位置后的内容判；更远后文透露的部分不算增量，其余照常判。",
          "muted",
        ),
      );
      radios(w, "n1", "N1 有增量吗？", ["pass", "fail"], n.judgment);
      if (n.judgment === "pass") {
        radios(w, "style", "写法（单选）", c.writing_style, n.writing_style);
        if (n.writing_style === "其他写法")
          textArea(
            w,
            "otherWriting",
            "这是什么写法、增量在哪（必填）",
            n.other_writing_explanation,
          );
      }
      if (n.judgment === "fail") {
        w.append(node("p", "失败类型（至少一个，可多选）· X"));
        for (const label of c.failure_types) {
          const i = check(
            w,
            "failure",
            label,
            n.failure_types?.includes(label),
          );
          i.value = label;
        }
        if (n.failure_types?.includes("其他")) {
          textArea(
            w,
            "otherFailure",
            "其他失败类型说明（必填）",
            n.other_failure_explanation,
          );
          w.append(
            node(
              "p",
              "其他：N1 不成立，但现有类型不贴切。rubric 未覆盖：现有判定标准没有涵盖这个问题。",
              "muted",
            ),
          );
        }
      }
      textArea(w, "n1Paraphrase", "读懂后的复述（选填）", n.paraphrase);
      textArea(w, "n1Reason", "N1 理由（选填）", n.reason);
    }
    if (s === 3) check(w, "spoiler", "有剧透", r.vetoes.spoiler);
    if (s === 4) {
      check(w, "incorrect", "有错误信息", r.vetoes.incorrect_information);
      check(w, "verification", "待核实（不影响结论）", r.needs_verification);
      w.append(
        node(
          "p",
          "同一个拿不准的事实只标待核实；若另有已确认错误，可以同时勾。",
          "muted",
        ),
      );
    }
    if (s >= 5) {
      w.append(
        node(
          "p",
          r.judgment === "pass" ? "自动结论：过" : "自动结论：不过",
          `result ${r.judgment}`,
        ),
      );
      const failures = [];
      if (r.n1.judgment === "fail") failures.push("N1 不过");
      for (const [k, label] of [
        ["reading_difficulty", "读着费劲"],
        ["spoiler", "有剧透"],
        ["incorrect_information", "有错误信息"],
      ])
        if (r.vetoes[k]) failures.push(label);
      if (r.rubric_uncovered) failures.push("rubric 未覆盖");
      if (failures.length) w.append(node("p", failures.join("、")));
      amendControls(w, r);
    }
    if (s === 6 && r.judgment === "pass") {
      for (const label of c.tags) {
        const i = check(w, "tag", label, r.tags?.includes(label));
        i.value = label;
        if (label === "锚点问题" && r.n1.following_text_use === "挂早了")
          i.disabled = true;
      }
    }
    const flags = node("div", undefined, "flags");
    check(
      flags,
      "manualUnsure",
      "这一项拿不准（手动）· N",
      r.unsure_sources[labels[s]]?.includes("manual"),
    );
    if (r.unsure_sources[labels[s]]?.includes("automatic"))
      flags.append(
        node("p", "已自动勾选拿不准：选择了“想法本身复杂，表达已尽量清楚”。", "muted"),
      );
    check(flags, "uncovered", "rubric 未覆盖 · 0", r.rubric_uncovered);
    if (r.rubric_uncovered)
      textArea(
        flags,
        "uncoveredReason",
        "未覆盖的原因（必填）",
        r.uncovered_reason,
      );
    if (s >= 5 && r.judgment === "pass")
      check(flags, "star", "星 · 范例级批注", r.star);
    textArea(flags, "reason", "整条理由（选填）", r.reason);
    w.append(flags);
    const helpPanel = w.querySelector("details.help");
    if (helpPanel) w.append(helpPanel);
    const complete = node(
      "button",
      s === 6
        ? "确认并提交本条"
        : s === 0
          ? "锁定第一印象，继续"
          : "完成此步，继续",
      "primary",
    );
    complete.onclick = () => completeCurrent(false).catch(shownError);
    complete.id = "noteComplete";
    $("reviewActions").replaceChildren(complete);
    updateStatus();
    autoGrow();
  }
  function amendControls(w, r) {
    const d = node("details");
    d.append(
      node("summary", `修正读着费劲 · 当前：${difficultyLabel(r.reading_difficulty.choice)}`),
    );
    d.append(
      node(
        "p",
        `首次：${difficultyLabel(r.reading_difficulty.original_choice)}。修正不覆盖原值，结论使用最终值。`,
        "muted",
      ),
    );
    const sel = node("select");
    sel.setAttribute("aria-label", "修正后的费劲选项");
    for (const v of boot.form.choices.reading_difficulty) {
      const o = node("option", difficultyLabel(v));
      o.value = v;
      sel.append(o);
    }
    sel.value = r.reading_difficulty.choice;
    d.append(sel);
    const reason = textArea(d, "amendReason", "修正理由（选填）", "");
    const rewrite = textArea(
      d,
      "amendRewrite",
      "修正后的改写文本（选填）",
      r.reading_difficulty.rewrite,
    );
    const b = node("button", "保存费劲修正");
    b.type = "button";
    b.onclick = async () => {
      try {
        await flush();
        await post("amend", {
          choice: sel.value,
          reason: reason.value,
          rewrite: rewrite.value,
        });
      } catch (e) {
        shownError(e);
      }
    };
    d.append(b);
    w.append(d);
  }
  function autoGrow() {
    host.querySelectorAll("textarea").forEach((t) => {
      t.style.height = "auto";
      t.style.height = Math.max(72, t.scrollHeight + 2) + "px";
    });
  }
  $("workflow").addEventListener("input", (e) => {
    if (e.target.id.startsWith("amend") || e.target.tagName === "SELECT")
      return;
    editEpoch++;
    dirty = true;
    updateStatus();
    autoGrow();
    clearTimeout(timer);
    if (!composing) timer = setTimeout(() => save().catch(shownError), 500);
  });
  $("workflow").addEventListener("change", async (e) => {
    if (!e.target.matches("input")) return;
    dirty = true;
    clearTimeout(timer);
    try {
      await save(true);
    } catch (err) {
      shownError(err);
    }
  });
  $("prev").onclick = () => openCase(index - 1).catch(shownError);
  $("anchorGo").onclick = locateAnchor;
  $("decisionGo").onclick = () => { if (inspecting !== null) render(); focusDecision(); };
  $("next").onclick = () => openCase(index + 1).catch(shownError);
  $("moreEarlier").onclick = async () => {
    try {
      segments(
        $("olderText"),
        await api("/earlier?id=" + encodeURIComponent(boot.record_ids[index])),
      );
      $("moreEarlier").hidden = true;
    } catch (e) {
      shownError(e);
    }
  };
  $("notes").addEventListener("toggle", async () => {
    if (!$("notes").open) return;
    try {
      await flush();
      const result = await post("notes", {}, false);
      const host = $("notesText");
      host.replaceChildren();
      if (!result.notes.items.length)
        host.append(
          node("p", "未解析：未找到可核实的注释链接，可继续标注。", "muted"),
        );
      for (const n of result.notes.items)
        host.append(
          node(
            "p",
            n.status === "resolved"
              ? `${n.marker} ${n.text}`
              : `${n.marker} 未解析，可继续标注。`,
          ),
        );
    } catch (e) {
      shownError(e);
    }
  });
  $("saveUnit").onclick = async () => {
    try {
      await flush();
      await api("/action", {
        id: boot.record_ids[index],
        action: "unit_note",
        values: { remarks: $("unitNote").value },
      });
      data.unit_note = $("unitNote").value;
      $("status").textContent = "单元备注已保存";
    } catch (e) {
      shownError(e);
    }
  };
  window.addEventListener(
    "beforeunload",
    (e) => {
      if (dirty || busy) {
        e.preventDefault();
        e.returnValue = "";
      }
    },
    { signal: abort.signal },
  );

  function updateLayout() {
    const panel = $("casePanel"),
      top =
        document.getElementById("toolbar").getBoundingClientRect().height + 12;
    panel.classList.toggle(
      "fits-viewport",
      panel.offsetHeight < innerHeight - top - 24,
    );
    $("readerScroll").style.maxHeight =
      innerWidth >= 960
        ? Math.max(180, innerHeight - top - 160) + "px"
        : "none";
  }
  window.addEventListener("resize", updateLayout, { signal: abort.signal });
  for (const event of ["focusin", "pointerdown"])
    document.addEventListener(event, () => interactionEpoch++, {
      signal: abort.signal,
    });
  async function completeCurrent(advance) {
    if (busy || inspecting !== null) return;
    const stage = data.state.stage;
    if (stage === 7 || (advance && stage !== 6)) return;
    const epoch = interactionEpoch;
    await flush();
    await post(stage === 6 ? "submit" : "complete", collect());
    if (advance && epoch === interactionEpoch) await openCase(index + 1);
    else if (epoch === interactionEpoch) {
      focusDecision();
      const first = host.querySelector("#workflow input:not(:disabled)");
      first?.focus({preventScroll:true});
    }
  }
  async function init() {
    boot = await api("/bootstrap");
    await openCase(Math.max(0, boot.record_ids.indexOf(boot.last_id)));
  }
  function updateNavigation() {
    const grid = $("unitGrid");
    grid.replaceChildren();
    boot.record_ids.forEach((rid, i) => {
      const st = session.state.drafts[rid];
      const b = node(
        "button",
        String(i + 1),
        "unit-cell" + (st?.stage === 7 ? " done" : st ? " started" : ""),
      );
      b.title = `第 ${i + 1} 条 · ${st?.stage === 7 ? "已完成" : st ? "进行中" : "未开始"}`;
      b.setAttribute("aria-label", b.title);
      b.setAttribute("aria-current", String(i === index));
      b.onclick = () => openCase(i).catch(shownError);
      grid.append(b);
    });
    const nav = $("rubricSteps");
    nav.replaceChildren();
    labels.forEach((label, i) => {
      const done =
        !!data.state.record.steps[session.form.steps[i].id]?.completed_at;
      const b = node("button", `${i + 1} ${label}${done ? " ✓" : ""}`);
      b.disabled = i > Math.min(6, data.state.stage);
      b.onclick = () => inspect(i).catch(shownError);
      nav.append(b);
    });
    $("batchCounts").textContent =
      `已完成 ${boot.record_ids.filter((id) => session.state.drafts[id]?.stage === 7).length} / ${boot.record_ids.length}`;
  }
  async function inspect(i) {
    if (i < 0 || i > 6 || i > data.state.stage) return;
    await flush();
    if (i === data.state.stage) {
      render();
      return;
    }
    inspecting = i;
    const w = $("workflow");
    w.replaceChildren(node("h2", labels[i] + (i < 2 ? " · 已完成，只读" : " · 已完成")));
    if (i >= 2) {
      const edit = node("button", "修改此步 · Shift+R");
      edit.id = "editCompletedStep";
      edit.onclick = async () => {
        try { await post("reopen", {step:i}); focusDecision(); }
        catch (error) { shownError(error); }
      };
      w.append(edit, node("p", "保留已填内容；修改后需重新确认本步及后续步骤。第一印象保持锁定。", "muted"));
    }
    const r = data.state.record,
      values = [
        outcomeLabel(r.first_impression.judgment),
        difficultyLabel(r.reading_difficulty.choice),
        [
          r.n1.following_text_use,
          r.n1.judgment === "pass" ? "过" : "不过",
          r.n1.writing_style,
          ...(r.n1.failure_types || []),
          r.n1.reason,
        ]
          .filter(Boolean)
          .join(" · "),
        r.vetoes.spoiler ? "勾选" : "未勾选",
        r.vetoes.incorrect_information ? "勾选" : "未勾选",
        outcomeLabel(r.judgment),
        (r.tags || []).join("、"),
      ];
    w.append(node("p", values[i]));
    if (i > 0) w.append(helpContent(boot.form.steps[i].help));
    const returnLabel = data.state.stage === 7 ? "返回已完成结果" : `返回第 ${data.state.stage + 1} 步：${labels[data.state.stage]}`;
    const b = node("button", returnLabel);
    b.onclick = () => { render(); focusDecision(); };
    $("decisionGo").textContent = returnLabel;
    w.append(b);
    $("reviewActions").replaceChildren();
  }
  $("workflow").addEventListener("compositionstart", () => {
    composing = true;
    clearTimeout(timer);
  });
  $("workflow").addEventListener("compositionend", () => {
    composing = false;
    timer = setTimeout(() => save().catch(shownError), 500);
  });
  $("unitNote").addEventListener("input", () => {
    session.state.unitDrafts[data.case.unit_key] = $("unitNote").value;
    session.persist().catch(shownError);
    autoGrow();
  });
  $("unitNote").addEventListener("blur", () => {
    $("saveUnit").click();
  });
  $("retry").onclick = async () => {
    try {
      if (
        (await session.directory.requestPermission({ mode: "readwrite" })) !==
        "granted"
      )
        throw Error("需要文件夹授权");
      await session.sync();
      dirty = false;
      await openCase(index);
      $("error").hidden = true;
      $("saveError").hidden = true;
    } catch (e) {
      shownError(e);
    }
  };
  $("retryVisible").onclick = () => $("retry").click();
  $("exportNote").onclick = () => {
    const a = document.createElement("a"),
      url = URL.createObjectURL(
        new Blob(
          session.state.rows.map((r) => JSON.stringify(r) + "\n"),
          { type: "application/x-ndjson" },
        ),
      );
    a.href = url;
    a.download = "q1-" + session.m.review_session_id + ".jsonl";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  };
  let helpReturn;
  $("shortcutHelp").addEventListener("close", () => {
    if (helpReturn?.isConnected) helpReturn.focus();
    else focusDecision();
  });
  $("noteHelp").onclick = () => {
    const d = $("shortcutHelp");
    if (!d.open) helpReturn = host.activeElement;
    if (d.open) d.close();
    else d.showModal();
  };
  $("closeNoteHelp").onclick = () => $("shortcutHelp").close();
  function focusField(id) {
    const el = $(id);
    if (!el) return;
    for (let p = el.parentElement; p; p = p.parentElement)
      if (p.tagName === "DETAILS") p.open = true;
    el.focus();
    el.scrollIntoView({ block: "nearest" });
  }
  function keydown(e) {
    if (
      e.isComposing ||
      composing ||
      e.keyCode === 229 ||
      e.metaKey ||
      e.ctrlKey ||
      e.altKey
    )
      return;
    const t = e.composedPath()[0],
      key = e.key.toLowerCase();
    if ($("shortcutHelp").open) {
      if (key === "escape") { e.preventDefault(); $("shortcutHelp").close(); }
      return;
    }
    if (key === "escape") {
      e.preventDefault(); focusDecision(); return;
    }
    if (t.closest?.('textarea,select,input:not([type=radio]):not([type=checkbox]),[contenteditable=true]')) return;
    if (t.matches?.('input') && ['arrowup','arrowdown','arrowleft','arrowright',' '].includes(key)) return;
    if (
      key === "enter" &&
      t.id !== "noteComplete" &&
      t.closest?.("button,a,summary")
    )
      return;
    if (e.repeat && !["j", "k"].includes(key)) return;
    if (busy) return;
    const run = (f) => {
      e.preventDefault();
      Promise.resolve().then(f).catch(shownError);
    };
    if (key === "?") return run(() => $("noteHelp").click());
    if (["j", "k"].includes(key)) {
      e.preventDefault();
      (e.shiftKey || innerWidth < 960 ? window : $("readerScroll")).scrollBy({
        top: key === "j" ? 180 : -180,
      });
      return;
    }
    if (key === "arrowdown" || key === "arrowup")
      return run(() => openCase(index + (key === "arrowdown" ? 1 : -1)));
    if (key === "arrowleft" || key === "arrowright")
      return run(() => openCase(index + (key === "arrowright" ? 1 : -1)));
    if (key === "[" || key === "]")
      return run(() =>
        inspect(
          (inspecting ?? Math.min(data.state.stage, 6)) +
            (key === "[" ? -1 : 1),
        ),
      );
    if (data.state.stage === 6 && /^[5-9]$/.test(key))
      return run(() =>
        host.querySelectorAll("[name=tag]")[Number(key) - 5]?.click(),
      );
    if (/^[1-7]$/.test(key) && !e.shiftKey)
      return run(() => inspect(Number(key) - 1));
    if (e.shiftKey && /^Digit[1-7]$/.test(e.code))
      return run(() => {
        const help = host.querySelector("#workflow details.help");
        if (help) help.open = !help.open;
      });
    if (key === "c") return run(() => $("decisionGo").click());
    if (key === "a") return run(locateAnchor);
    if (["e","o","h"].includes(key)) return run(() => {
      const el = key === "e" ? $("earlier") : key === "o" ? $("notes") : host.querySelector("#workflow details.help");
      if (el) { el.open = !el.open; el.querySelector("summary")?.focus(); }
    });
    if (key === "l" && inspecting === null) return run(() => {
      const el = $("following-" + (e.shiftKey ? "after_unit" : "within_unit"));
      if (el && !el.hidden && !el.disabled) el.click();
    });
    if (key === "r" && e.shiftKey && inspecting !== null)
      return run(() => $("editCompletedStep")?.click());
    if (inspecting !== null) return;
    if (key === "y") return run(() => focusField(data.state.stage === 2 ? "n1Paraphrase" : "paraphrase"));
    if (key === "i") return run(() => focusField("rewrite"));
    if (data.state.stage === 1 && ["q","g","z"].includes(key))
      return run(() => host.querySelectorAll('[name="difficulty"]')[["q","g","z"].indexOf(key)]?.click());
    const groups = {d:"difficulty",b:"followingUse",w:"style",x:"failure",t:"tag"};
    if (groups[key]) return run(() => focusGroup(groups[key]));
    if (key === "enter") return run(() => completeCurrent(e.shiftKey));
    if (key === "r")
      return run(() =>
        focusField(data.state.stage === 2 ? "n1Reason" : "reason"),
      );
    if (key === "m") return run(() => focusField("reason"));
    if (key === "u") return run(() => focusField("unitNote"));
    const toggle = (name) => {
      const el = host.querySelector(`#workflow [name="${name}"]`);
      el?.click();
    };
    if (key === "n") return run(() => toggle("manualUnsure"));
    if (key === "0") return run(() => toggle("uncovered"));
    if (key === "s") return run(() => toggle("star"));
    if (key === "v") return run(() => toggle("verification"));
    if (["p", "f"].includes(key))
      return run(() => {
        const stage = data.state.stage;
        if ([0, 2].includes(stage))
          host
            .querySelector(
              `[name="${stage === 0 ? "first" : "n1"}"][value="${key === "p" ? "pass" : "fail"}"]`,
            )
            ?.click();
        else if ([3, 4].includes(stage)) {
          const el = host.querySelector(
            `[name="${stage === 3 ? "spoiler" : "incorrect"}"]`,
          );
          if (el && el.checked !== (key === "f")) el.click();
        }
      });
  }
  document.addEventListener("keydown", keydown, { signal: abort.signal });

  await init();
  return {
    flush,
    dispose: () => {
      clearTimeout(timer);
      abort.abort();
    },
    session,
  };
};
