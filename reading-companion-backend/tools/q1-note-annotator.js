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
    uiTimer,
    active = 0,
    clock = performance.now(),
    busy = false,
    editEpoch = 0,
    interactionEpoch = 0,
    composing = false,
    tagMode = false,
    pendingGroupFocus = null,
    executing = false,
    pendingContinuation = null,
    commandTail = Promise.resolve(),
    renderedCase = null,
    renderedStep = null;
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
  function difficultyView(value) {
    if ("first_pass" in value) return value;
    return {...value,
      first_pass:value.original_choice === "一遍能复述" ? "复述得出" : value.original_choice ? "复述不出或说偏" : null,
      rewrite:["能改写得更直白","改写不出"].includes(value.choice) ? value.choice : null,
      rewrite_text:value.rewrite || "", legacy:true};
  }
  function difficultySummary(value) {
    const d = difficultyView(value);
    if (d.legacy) return `旧版最初：${difficultyLabel(value.original_choice)}；最终：${difficultyLabel(value.choice)}（第一遍未独立记录）`;
    return [d.first_pass || "未判定", d.first_pass === "复述不出或说偏" ? d.rewrite || "改写尚未判定" : ""].filter(Boolean).join("；");
  }
  function checkValue(record, key) {
    if (record.checks) return record.checks[key];
    return record.review_completed ? record.vetoes[key] : null;
  }
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
    for (const name of ['first','firstPass','rewriteChoice','followingUse','n1','style','failure','spoiler','incorrect']) {
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
      if (dirty && !composing) enqueue(() => save()).catch(shownError);
    },
    { signal: abort.signal },
  );
  const api = (path, body) => session.api(path, body);
  function textArea(parent, id, label, value = "") {
    const shortcut = {paraphrase:"Y",n1Paraphrase:"Y",rewrite:"I",reason:"M",n1Reason:"R",otherWriting:"Shift+W",otherFailure:"Shift+X",uncoveredReason:"Shift+0",amendmentReason:"Shift+M"}[id];
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
    const keys = {rewriteChoice:"D",followingUse:"B",style:"W"};
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
        node("span", v === "pass" ? "过 · P" : v === "fail" ? "不过 · F" :
          name === "firstPass" ? `${v} · ${["Q", "G"][values.indexOf(v)]}` :
          name === "rewriteChoice" ? `${v === "改写不出" ? "改写不出：想法本身复杂，表达已尽量清楚（不否决，标拿不准）" : "能改写得更直白且不丢内容（否决）"} · ${["W", "Z"][values.indexOf(v)]}` :
          ["spoiler","incorrect"].includes(name) ? `${v === "true" ? "有 · F" : "没有 · P"}` : v),
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
    const s = currentStep(),
      r = data.state.record;
    if (s === 7) return {};
    const v = {
      manual_unsure: checked("manualUnsure"),
      rubric_uncovered: checked("uncovered"),
      uncovered_reason: $("uncoveredReason")?.value ?? r.uncovered_reason,
      reason: $("reason")?.value ?? r.reason,
    };
    if (host.querySelector("[name=star]")) v.star = checked("star");
    if ($("amendmentReason")) v.amendment_reason = $("amendmentReason").value;
    if (s === 0 && get("first")) v.judgment = get("first");
    if (s === 1) {
      if (!r.reading_difficulty.locked_at) {
        if (get("firstPass")) v.first_pass = get("firstPass");
        v.paraphrase = $("paraphrase").value;
      }
      const firstPass = v.first_pass ?? r.reading_difficulty.first_pass;
      if (firstPass === "复述不出或说偏" && get("rewriteChoice")) v.rewrite = get("rewriteChoice");
      else if (firstPass === "复述得出") v.rewrite = null;
      v.rewrite_text = $("rewrite")?.value ?? r.reading_difficulty.rewrite_text ?? "";
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
          n.other_writing_explanation = $("otherWriting")?.value ?? uiState().branches?.otherWriting ?? "";
      }
      if (n.judgment === "fail") {
        n.failure_types = [
          ...host.querySelectorAll("[name=failure]:checked"),
        ].map((x) => x.value);
        if (n.failure_types.includes("其他"))
          n.other_failure_explanation = $("otherFailure")?.value ?? uiState().branches?.otherFailure ?? "";
      }
      v.n1 = n;
    }
    if (s === 3 && get("spoiler") !== undefined) v.spoiler = get("spoiler") === "true";
    if (s === 4) {
      if (get("incorrect") !== undefined) v.incorrect_information = get("incorrect") === "true";
      v.needs_verification = checked("verification");
    }
    if (s === 6 && r.judgment === "pass")
      v.tags = [...host.querySelectorAll("[name=tag]:checked")].map(
        (x) => x.value,
      );
    return v;
  }
  const currentStep = () => data.state.viewStep ?? data.state.stage;
  const isReadOnly = () => data.state.stage === 7 || !!data.state.discussionRequired;
  const currentId = () => boot.record_ids[index];
  const uiState = () => data.state.ui ??= {};
  function captureUI() {
    const ui = uiState();
    const branches = {...ui.branches};
    for (const [id, key] of [["otherWriting","otherWriting"],["otherFailure","otherFailure"]])
      if ($(id)) branches[key] = $(id).value;
    const following = {};
    host.querySelectorAll(".followingText").forEach(el => {
      if (!el.hidden) following[el.dataset.scope] = true;
    });
    return {...ui, branches, readerScroll:$("readerScroll").scrollTop,
      earlierOpen:$("earlier").open, notesOpen:$("notes").open,
      olderOpen:$("moreEarlier").hidden && !!data.earlier_count,
      previewOpen:$("notePreview").open, unitOpen:$("unitDetails").open,
      followingStep:currentStep(), following};
  }
  function enqueue(work, {stepBound = false, saveAfter = true} = {}) {
    const id = boot && currentId(), step = data && currentStep();
    const task = commandTail.then(async () => {
      if (id && (id !== currentId() || (stepBound && step !== currentStep()))) return;
      executing = true;
      try {
        const result = await work();
        while (saveAfter && dirty && !composing) await save(true);
        return result;
      } finally { executing = false; }
    });
    commandTail = task.catch(() => {});
    return task;
  }
  async function persistUI() {
    if (!data || renderedCase !== currentId()) return;
    const ui = captureUI();
    data.state.ui = ui;
    await api("/action", {id:currentId(), action:"ui_meta", values:{ui}});
  }
  function lockEditing() {
    const controls = [...host.querySelectorAll("#workflow input,#workflow textarea")];
    const previous = controls.map(el => [el, el.disabled]);
    controls.forEach(el => { el.disabled = true; });
    return () => previous.forEach(([el, disabled]) => { el.disabled = disabled; });
  }
  async function post(action, values = {}, renderAfter = true, epoch = editEpoch) {
    const id = currentId(), duration = elapsed(), ui = captureUI();
    let succeeded = false;
    const unlock = ["navigate","complete","submit"].includes(action) ? lockEditing() : () => {};
    busy = true;
    $("status").textContent = "正在保存草稿…";
    try {
      const result = await api("/action", {
        id, action, values, ui, version:data.state.version, active_ms:duration,
      });
      if (id !== currentId()) return result;
      data = result;
      succeeded = true;
      dirty = editEpoch !== epoch;
      $("error").hidden = true;
      $("saveError").hidden = true;
      if (renderAfter && !dirty) {
        const focus = rememberFocus();
        render();
        if (action === "save") restoreFocus(focus);
      } else updateStatus();
      return result;
    } catch (e) {
      active += duration;
      if (e.currentState && e.currentState.version !== data.state.version) {
        const oldStep = currentStep(), hasNewInput = editEpoch !== epoch;
        data.state = e.currentState;
        data.receipt = e.receipt;
        dirty = hasNewInput;
        if (oldStep !== currentStep() || !hasNewInput) {
          const focus = rememberFocus(); render(); restoreFocus(focus);
        }
      }
      if (e.code === "FORM_VALIDATION" && !dirty) render();
      if (Number.isInteger(e.step) && e.step !== currentStep()) {
        data = await api("/action", {id,action:"navigate",values:{step:e.step},version:data.state.version});
        render();
      }
      throw e;
    } finally {
      unlock();
      busy = false;
      updateNavigation();
      if (succeeded) updateStatus();
    }
  }
  function updateStatus() {
    const receipt = data.receipt ?? session.receipt?.(currentId());
    const parts = [dirty || receipt?.browser_saved === false ? "草稿尚未保存" : "草稿已保存在此浏览器"];
    if (receipt?.pending_file) parts.push("已提交记录待同步文件");
    else if (receipt?.file_revision) parts.push(`已提交记录已同步文件（修订 ${receipt.file_revision}）`);
    else parts.push("尚无已提交记录");
    if (receipt?.submitted_revision && !data.state.record.review_completed)
      parts.push("本条有待提交修改");
    $("status").textContent = parts.join(" · ");
  }
  async function save(renderAfter = true) {
    clearTimeout(timer);
    if (!dirty || composing || (currentStep() === 0 && data.state.record.first_impression.locked_at)) return;
    await post("save", collect(), renderAfter);
  }
  async function flush() {
    clearTimeout(timer);
    if (dirty) await save(true);
    if (data && $("unitNote").value !== data.unit_note) {
      const value = $("unitNote").value;
      const result = await api("/action", {id:currentId(),action:"unit_note",values:{remarks:value}});
      data.unit_note = value;
      data.receipt = result.receipt;
    }
    await persistUI();
  }
  async function openCase(i) {
    if (i < 0 || i >= boot.record_ids.length) return;
    if (data) await flush();
    const unlock = data ? lockEditing() : () => {};
    let result;
    try { result = await api("/action", {id:boot.record_ids[i],action:"open"}); }
    finally { unlock(); }
    index = i;
    data = result;
    active = 0;
    clock = performance.now();
    tagMode = false;
    pendingGroupFocus = null;
    render();
    $("prev").disabled = index === 0;
    $("next").disabled = index === boot.record_ids.length - 1;
    if (data.state.ui?.readerScroll === undefined) requestAnimationFrame(locateAnchor);
    focusDecision();
  }
  function render() {
    const sameCase = renderedCase === currentId(), sameStep = sameCase && renderedStep === currentStep();
    const sourceScroll = sameCase ? $("readerScroll").scrollTop : (uiState().readerScroll ?? 0);
    const ui = uiState();
    if (!sameStep) tagMode = false;
    renderedCase = currentId(); renderedStep = currentStep();
    requestAnimationFrame(() => { $("readerScroll").scrollTop = sourceScroll; });

    updateNavigation();
    requestAnimationFrame(updateLayout);
    const s = currentStep(),
      r = data.state.record,
      c = boot.form.choices;
    $("position").textContent = `${index + 1} / ${boot.record_ids.length} 条`;
    $("purpose").textContent =
      boot.purpose === "test" ? "测试会话" : "正式会话";
    $("book").textContent = data.case.book;
    $("chapter").textContent = data.case.chapter_title;
    $("body").textContent = data.case.body_text;
    $("previewBody").textContent = data.case.body_text;
    $("decisionGo").textContent = "定位当前判定 · C";
    $("sessionIdentity").textContent = `${boot.session_id} · 文件夹 ${boot.directory_name} · 工具 3.6`;
    segments($("sourceText"), data.prefix);
    $("chapter").hidden = $("sourceText").firstElementChild?.textContent.trim() === data.case.chapter_title?.trim();
    segments($("recentText"), data.recent);
    $("olderText").replaceChildren();
    $("earlier").open = !!ui.earlierOpen;
    $("moreEarlier").hidden = !data.earlier_count;
    $("notes").open = !!ui.notesOpen;
    $("notesText").replaceChildren();
    $("noteStatus").textContent =
      data.notes_status === "resolved" ? "可查看" : "未解析或部分未解析";
    $("unitNote").value = data.unit_note;
    $("unitDetails").open = !!ui.unitOpen;
    $("notePreview").open = !!ui.previewOpen;
    if (ui.olderOpen) { segments($("olderText"), data.case.context.earlier.slice(0,-4)); $("moreEarlier").hidden=true; }
    if (ui.notesOpen) renderNotes(data.case.context.original_notes);
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
          scope === "within_unit" ? "展开单元内后文 · L" : "展开单元外后文 · Shift+L",
          "followingControl",
        );
        button.type = "button";
        button.id = "following-" + scope;
        button.hidden = !data.has_following[scope];
        const content = node("div", undefined, "followingText");
        content.dataset.scope = scope;
        content.hidden = !(ui.followingStep === s && ui.following?.[scope]);
        if (!content.hidden) { segments(content,data.case.context[scope]); button.textContent=button.textContent.replace("展开","收起"); }
        button.activate = async () => {
          try {
            if (!content.hidden) {
              content.hidden = true;
              button.textContent = button.textContent.replace("收起", "展开");
              await persistUI(); return;
            }
            await flush();
            const result = await post("following", { scope }, false);
            segments(content, result.following);
            content.hidden = false;
            button.textContent = button.textContent.replace("展开", "收起");
            await persistUI();
          } catch (e) {
            shownError(e);
          }
        };
        button.onclick = () => enqueue(button.activate, {stepBound:true}).catch(shownError);
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
          `读着费劲：${difficultySummary(r.reading_difficulty)}；修改 ${r.reading_difficulty.amendments.length} 次。`,
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
      w.append(node("p", "本条已提交，判定只读。可以切换步骤查看，或在讨论后改判。", "muted"));
      $("reviewActions").replaceChildren(discussionButton());
      updateStatus();
      return;
    }
    if (s === 0 && r.first_impression.locked_at) {
      w.replaceChildren(node("h2", "第一印象 · 已锁定"), node("p", outcomeLabel(r.first_impression.judgment)),
        node("p", "第一印象确认后不能修改。已开放步骤可直接切换。", "muted"));
      const b = node("button", "返回第 2 步 · 2 / Enter");
      b.onclick = () => enqueue(() => inspect(1)).catch(shownError);
      $("reviewActions").replaceChildren(b); updateStatus(); return;
    }
    const spec = boot.form.steps[s];
    w.append(
      node("div", `第 ${s + 1} / 7 步 · Enter ${s === 6 ? "提交" : "继续"} · 1–7 切换已开放步骤`, "eyebrow"),
      node("h2", s === 6 && r.judgment !== "pass" ? "提交检查" : spec.label),
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
        node("summary", `完整判定说明 · H · rubric ${spec.section}`),
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
      const d = difficultyView(r.reading_difficulty);
      if (d.legacy) {
        w.append(node("p", difficultySummary(r.reading_difficulty) + "。保留旧版选项和文本，不把后来改判当作第一遍。", "muted"));
        textArea(w, "paraphrase", "旧版复述文本（非独立第一遍记录）", d.paraphrase);
        textArea(w, "rewrite", "旧版改写文本", d.rewrite_text);
      } else {
        radios(
          w,
          "firstPass",
          "第一遍能准确复述意思吗？（必选）",
          ["复述得出", "复述不出或说偏"],
          d.first_pass,
        );
        const firstText = textArea(
          w,
          "paraphrase",
          "第一遍复述 / 卡在哪（选填）",
          d.paraphrase,
        );
        if (d.locked_at) {
          w.querySelectorAll('[name="firstPass"]').forEach(el => { el.disabled=true; });
          firstText.readOnly = true;
          w.append(node("p", "第一遍判断和复述已锁定。" + (d.first_pass === "复述不出或说偏" ? "下面的改写判断仍可修改。" : ""), "muted"));
        }
        if (d.first_pass === "复述不出或说偏") {
          radios(w, "rewriteChoice", "能否写得更直白，又不丢内容？（必选）",
            ["能改写得更直白", "改写不出"], d.rewrite);
          w.append(node("p", "改写不出：想法本身复杂，表达已尽量清楚，无法更直白且不丢内容；不否决，自动标拿不准。", "muted"));
        }
        textArea(w, "rewrite", "更直白的改写（选填）", d.rewrite_text);
      }
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
            n.other_writing_explanation ?? ui.branches?.otherWriting,
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
          if (label === "下文马上讲了" && n.following_text_use === "紧接着几段") i.disabled = true;
        }
        if (n.failure_types?.includes("其他")) {
          textArea(
            w,
            "otherFailure",
            "其他失败类型说明（必填）",
            n.other_failure_explanation ?? ui.branches?.otherFailure,
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
    if (s === 3) radios(w, "spoiler", "有剧透吗？（必选）", ["true","false"], checkValue(r,"spoiler") == null ? null : String(checkValue(r,"spoiler")));
    if (s === 4) {
      radios(w, "incorrect", "有错误信息吗？（必选）", ["true","false"], checkValue(r,"incorrect_information") == null ? null : String(checkValue(r,"incorrect_information")));
      check(w, "verification", "待核实（不影响结论）· V", r.needs_verification);
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
          `自动结论：${outcomeLabel(r.judgment)}`,
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
    }
    if (s === 6 && r.judgment === "pass") {
      w.append(node("p", tagMode ? "标签快捷键已启用：5–9 选择，Esc 退出" : "按 T 进入标签组；普通状态 1–7 切换步骤", "tagModeHint"));
      for (const [tagIndex, label] of c.tags.entries()) {
        const i = check(w, "tag", `${label} · T 后 ${tagIndex+5}`, r.tags?.includes(label));
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
      check(flags, "star", "星 · 范例级批注 · S", r.star);
    textArea(flags, "reason", "整条理由（选填）", r.reason);
    if (data.state.discussion)
      textArea(flags, "amendmentReason", "讨论后改判的原因（必填）", r.amendment_reason);
    w.append(flags);
    const helpPanel = w.querySelector("details.help");
    if (helpPanel) w.append(helpPanel);
    if (isReadOnly()) {
      w.querySelectorAll("input,textarea").forEach(el => { el.disabled=true; });
      w.append(node("p", "本条判定只读；需要改动时，请先进入讨论后改判。", "muted"));
      $("reviewActions").replaceChildren(discussionButton());
      updateStatus(); autoGrow(); return;
    }
    const complete = node(
      "button",
      s === 6
        ? "确认并提交本条 · Enter"
        : s === 0
          ? "锁定第一印象，继续 · Enter"
          : "继续下一步 · Enter",
      "primary",
    );
    complete.onclick = () => queueContinue(false);
    complete.id = "noteComplete";
    $("reviewActions").replaceChildren(complete);
    if (s === 6) $("reviewActions").append(node("span", "提交后下一条 · Shift+Enter", "muted"));
    updateStatus();
    autoGrow();
  }
  function autoGrow() {
    host.querySelectorAll("textarea").forEach((t) => {
      t.style.height = "auto";
      t.style.height = Math.max(72, t.scrollHeight + 2) + "px";
    });
  }
  $("workflow").addEventListener("input", () => {
    editEpoch++;
    dirty = true;
    updateStatus();
    autoGrow();
    clearTimeout(timer);
    if (!composing) timer = setTimeout(() => enqueue(() => save()).catch(shownError), 500);
  });
  $("workflow").addEventListener("change", (e) => {
    if (!e.target.matches("input")) return;
    dirty = true;
    clearTimeout(timer);
    enqueue(() => save(true), {stepBound:true}).catch(shownError);
  });
  $("prev").onclick = () => enqueue(() => openCase(index - 1)).catch(shownError);
  $("anchorGo").onclick = locateAnchor;
  $("decisionGo").onclick = focusDecision;
  $("next").onclick = () => enqueue(() => openCase(index + 1)).catch(shownError);
  async function showEarlier() {
    segments($("olderText"), await api("/earlier?id=" + encodeURIComponent(currentId())));
    $("moreEarlier").hidden = true;
    await persistUI();
  }
  $("moreEarlier").onclick = () => enqueue(showEarlier).catch(shownError);
  function renderNotes(notes) {
    const target = $("notesText"); target.replaceChildren();
    if (!notes.items.length)
      target.append(node("p", "未解析：未找到可核实的注释链接，可继续标注。", "muted"));
    for (const n of notes.items)
      target.append(node("p", n.status === "resolved" ? `${n.marker} ${n.text}` : `${n.marker} 未解析，可继续标注。`));
  }
  $("notes").addEventListener("toggle", () => {
    if (!data || !$("notes").open) return;
    renderNotes(data.case.context.original_notes);
    if (data.state.record.context.viewed_original_notes) return;
    enqueue(async () => {
      await flush();
      const step = currentStep();
      const result = await post("notes", {}, false);
      if (currentStep() !== step) render();
      renderNotes(result.notes);
      await persistUI();
    }).catch(shownError);
  });
  $("saveUnit").onclick = () => enqueue(async () => {
    await flush();
    updateStatus();
  }).catch(shownError);
  for (const id of ["earlier","notes","notePreview","unitDetails"])
    $(id).addEventListener("toggle", () => {
      if (data && renderedCase === currentId()) enqueue(persistUI, {saveAfter:false}).catch(shownError);
    });
  $("readerScroll").addEventListener("scroll", () => {
    if (data) {
      uiState().readerScroll = $("readerScroll").scrollTop;
      clearTimeout(uiTimer);
      uiTimer = setTimeout(() => enqueue(persistUI, {saveAfter:false}).catch(shownError), 200);
    }
  }, {passive:true});
  window.addEventListener(
    "beforeunload",
    (e) => {
      if (dirty || busy || session.browserSaved === false) {
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
  function queueContinue(advance) {
    if (pendingContinuation) return;
    pendingContinuation = enqueue(() => completeCurrent(advance))
      .catch(shownError).finally(() => { pendingContinuation = null; });
  }
  function discussionButton() {
    const button = node("button", "讨论后改判 · Shift+D");
    button.onclick = () => enqueue(beginDiscussion).catch(shownError);
    return button;
  }
  async function beginDiscussion() {
    if (!isReadOnly()) return;
    await flush();
    $("notes").open = false;
    host.querySelectorAll(".followingText").forEach(el => { el.hidden = true; });
    await post("begin_discussion");
    focusDecision();
  }
  async function completeCurrent(advance) {
    const step = currentStep();
    if (step === 7 || (advance && step !== 6)) return;
    if (step === 0 && data.state.record.first_impression.locked_at) return inspect(1);
    const epoch = interactionEpoch;
    await flush();
    if (isReadOnly()) {
      if (advance) await openCase(index + 1);
      else if (step < 6) await inspect(step + 1);
      return;
    }
    const values = collect();
    try {
      await post(step === 6 ? "submit" : "complete", values);
    } catch (error) {
      if (step !== 6 || error.warning !== "far_following_without_spoiler") throw error;
      if (!window.confirm("N1 记了用到更远后文，但剧透判了没有，确认吗？")) {
        updateStatus();
        if (epoch === interactionEpoch) focusDecision();
        return;
      }
      await post("submit", {...values, acknowledge_far_following:true});
    }
    if (advance && epoch === interactionEpoch) await openCase(index + 1);
    else if (epoch === interactionEpoch) focusDecision();
  }
  async function init() {
    boot = await api("/bootstrap");
    await openCase(Math.max(0, boot.record_ids.indexOf(boot.last_id)));
  }
  function updateNavigation() {
    const submitted = new Set(session.state.rows.filter(r => r.record_type === "marginalia").map(r => r.record_id));
    const grid = $("unitGrid"); grid.replaceChildren();
    let pending = 0;
    boot.record_ids.forEach((rid, i) => {
      const st = session.state.drafts[rid], done = submitted.has(rid), changed = done && st && !st.record.review_completed;
      if (changed) pending++;
      const status = changed ? "有待提交修改" : done ? "已提交" : st?.record.first_impression.judgment ? "进行中" : "未开始";
      const b = node("button", String(i+1), "unit-cell" + (done ? " done" : status === "进行中" ? " started" : "") + (changed ? " changed" : ""));
      b.title = `第 ${i+1} 条 · ${status}`;
      b.setAttribute("aria-label", b.title);
      b.setAttribute("aria-current", String(i===index));
      b.onclick = () => enqueue(() => openCase(i)).catch(shownError);
      grid.append(b);
    });
    const nav = $("rubricSteps"); nav.replaceChildren();
    labels.forEach((label,i) => {
      const changed = data.state.dirtySteps?.includes(i);
      const done = !!data.state.record.steps[session.form.steps[i].id]?.completed_at;
      const b = node("button", `${i+1} ${label}${changed ? " · 已修改" : done ? " ✓" : ""}`);
      b.disabled = i > (data.state.maxUnlockedStage ?? Math.min(6,data.state.stage));
      b.setAttribute("aria-current", String(i === currentStep()));
      b.onclick = () => enqueue(() => inspect(i)).catch(shownError);
      nav.append(b);
    });
    $("batchCounts").textContent = `已提交 ${submitted.size} / ${boot.record_ids.length}${pending ? ` · ${pending} 条待提交修改` : ""}`;
  }
  async function inspect(i) {
    if (i < 0 || i > 6 || i > (data.state.maxUnlockedStage ?? Math.min(6,data.state.stage))) return;
    await flush();
    if (i === currentStep()) { focusDecision(); return; }
    tagMode = false;
    await post("navigate", {step:i});
    focusDecision();
  }
  host.addEventListener("compositionstart", () => {
    composing = true;
    clearTimeout(timer);
  });
  host.addEventListener("compositionend", () => {
    composing = false;
    timer = setTimeout(() => enqueue(() => save()).catch(shownError), 500);
  });
  $("unitNote").addEventListener("input", () => {
    session.state.unitDrafts[data.case.unit_key] = $("unitNote").value;
    session.persist().catch(shownError);
    autoGrow();
  });
  $("unitNote").addEventListener("blur", () => {
    $("saveUnit").click();
  });
  $("retry").onclick = () => enqueue(async () => {
    if ((await session.directory.requestPermission({mode:"readwrite"})) !== "granted")
      throw Error("需要文件夹授权");
    await session.sync();
    await flush();
    await openCase(index);
    $("error").hidden = true; $("saveError").hidden = true;
  }).catch(shownError);
  $("retryVisible").onclick = () => $("retry").click();
  function downloadRows(rows, suffix = "") {
    const a = document.createElement("a"),
      url = URL.createObjectURL(
        new Blob(
          rows.map((r) => JSON.stringify(r) + "\n"),
          { type: "application/x-ndjson" },
        ),
      );
    a.href = url;
    a.download = "q1-" + session.m.review_session_id + suffix + ".jsonl";
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
  $("exportNote").onclick = () => downloadRows(session.state.rows);
  $("exportFirst").onclick = () => downloadRows(Q1NoteOffline.firstJudgments(session.state.rows), "-first");
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
  function queuedGroupKey(name, key) {
    const all = [...host.querySelectorAll(`#workflow [name="${name}"]`)].filter(el => !el.disabled);
    if (!all.length) return;
    const focused = all.includes(host.activeElement) ? host.activeElement : all.find(el => el.checked) || all[0];
    const offset = ["arrowright","arrowdown"].includes(key) ? 1 : -1;
    const target = key === " " ? focused : all[(all.indexOf(focused) + offset + all.length) % all.length];
    target.focus();
    if (key === " " || target.type === "radio") target.click();
  }
  function keydown(e) {
    if (e.isComposing || composing || e.keyCode === 229) return;
    const t = e.composedPath()[0], key = e.key.toLowerCase();
    if (t.id === "unitNote" && e.ctrlKey && !e.metaKey && !e.altKey && key === "enter") {
      e.preventDefault(); $("saveUnit").click(); return;
    }
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    if ($("shortcutHelp").open) {
      if (key === "escape") { e.preventDefault(); $("shortcutHelp").close(); }
      return;
    }
    if (key === "escape") {
      e.preventDefault(); tagMode = false; updateTagMode(); focusDecision(); return;
    }
    if (t.closest?.('textarea,select,input:not([type=radio]):not([type=checkbox]),[contenteditable=true]')) return;
    if (pendingGroupFocus && ['arrowup','arrowdown','arrowleft','arrowright',' '].includes(key)) {
      e.preventDefault();
      const group = pendingGroupFocus;
      enqueue(() => queuedGroupKey(group,key)).catch(shownError); return;
    }
    if (t.matches?.('input') && ['arrowup','arrowdown','arrowleft','arrowright',' '].includes(key)) return;
    if (key === "enter" && t.id !== "noteComplete" && t.closest?.("button,a,summary")) return;
    if (e.repeat && !["j","k"].includes(key)) return;
    const run = (f,stepBound=false) => {
      e.preventDefault();
      enqueue(f,{stepBound}).catch(shownError);
    };
    // Native browser pickers need the original trusted user activation.
    if (e.shiftKey && key === "o") { e.preventDefault(); document.getElementById("openFolder").click(); return; }
    if (e.shiftKey && key === "s") { e.preventDefault(); $("exportNote").click(); return; }
    if (e.shiftKey && key === "v") { e.preventDefault(); $("retry").click(); return; }
    if (key === "?" || (e.shiftKey && e.code === "Slash")) return run(() => $("noteHelp").click(),false);
    if (["j","k"].includes(key)) {
      e.preventDefault();
      (e.shiftKey || innerWidth < 960 ? window : $("readerScroll")).scrollBy({top:key === "j" ? 180 : -180}); return;
    }
    if (["arrowdown","arrowup","arrowleft","arrowright"].includes(key))
      return run(() => openCase(index + (["arrowdown","arrowright"].includes(key) ? 1 : -1)),false);
    if (key === "[" || key === "]" || ["BracketLeft","BracketRight"].includes(e.code))
      return run(() => inspect(Math.min(currentStep(),6) + (key === "[" || e.code === "BracketLeft" ? -1 : 1)),false);
    if (/^[1-9]$/.test(key) && !e.shiftKey) return run(() => {
      if (tagMode && currentStep() === 6 && /^[5-9]$/.test(key))
        host.querySelectorAll('[name="tag"]')[Number(key)-5]?.click();
      else if (Number(key) <= 7) return inspect(Number(key)-1);
    },false);
    if (e.shiftKey && e.code === "Digit0") return run(() => focusField("uncoveredReason"));
    if (e.shiftKey && /^Digit[1-7]$/.test(e.code)) return run(() => toggleDetails(host.querySelector("#workflow details.help")));
    if (e.shiftKey && key === "w") return run(() => focusField("otherWriting"));
    if (e.shiftKey && key === "x") return run(() => focusField("otherFailure"));
    if (e.shiftKey && key === "m") return run(() => focusField("amendmentReason"));
    if (e.shiftKey && key === "d") return run(beginDiscussion);
    if (e.shiftKey && key === "e") return run(async () => { $("earlier").open=true; await showEarlier(); });
    if (e.shiftKey && key === "c") return run(() => toggleDetails($("notePreview")));
    if (key === "c") return run(focusDecision);
    if (key === "a") return run(locateAnchor);
    if (["e","o","h"].includes(key)) return run(() => toggleDetails(key === "e" ? $("earlier") : key === "o" ? $("notes") : host.querySelector("#workflow details.help")));
    if (key === "l") return run(() => {
      const el = $("following-"+(e.shiftKey ? "after_unit" : "within_unit"));
      if (el && !el.hidden && !el.disabled) return el.activate();
    });
    if (key === "u") return run(() => focusField("unitNote"));
    if (key === "y") return run(() => focusField(currentStep() === 2 ? "n1Paraphrase" : "paraphrase"));
    if (key === "i") return run(() => focusField("rewrite"));
    if (["q","g","z"].includes(key))
      return run(() => {
        if (currentStep() !== 1 || isReadOnly()) return;
        const name = ["q","g"].includes(key) ? "firstPass" : "rewriteChoice";
        const index = ["q","w"].includes(key) ? 0 : 1;
        host.querySelectorAll(`[name="${name}"]`)[index]?.click();
      });
    const groups = {d:"rewriteChoice",b:"followingUse",w:"style",x:"failure",t:"tag"};
    if (groups[key]) {
      const group = groups[key]; pendingGroupFocus = group;
      return run(() => {
        try {
          if (key === "t" && isReadOnly()) return;
          if (key === "w" && currentStep() === 1) {
            if (!isReadOnly()) host.querySelectorAll('[name="rewriteChoice"]')[0]?.click();
            return;
          }
          if (key === "t" && host.querySelector('[name="tag"]')) { tagMode=true; updateTagMode(); }
          focusGroup(group);
        } finally { if (pendingGroupFocus === group) pendingGroupFocus=null; }
      });
    }
    if (key === "enter") { e.preventDefault(); queueContinue(e.shiftKey); return; }
    if (key === "r") return run(() => focusField(currentStep() === 2 ? "n1Reason" : "reason"));
    if (key === "m") return run(() => focusField("reason"));
    const toggle = name => host.querySelector(`#workflow [name="${name}"]`)?.click();
    if (key === "n") return run(() => toggle("manualUnsure"));
    if (key === "0") return run(() => toggle("uncovered"));
    if (key === "s") return run(() => toggle("star"));
    if (key === "v") return run(() => toggle("verification"));
    if (["p","f"].includes(key)) return run(() => {
      const step = currentStep();
      if ([0,2].includes(step)) host.querySelector(`[name="${step===0 ? "first" : "n1"}"][value="${key==='p' ? 'pass' : 'fail'}"]`)?.click();
      else if ([3,4].includes(step)) {
        host.querySelector(`[name="${step===3 ? 'spoiler' : 'incorrect'}"][value="${key === "f"}"]`)?.click();
      }
    });
  }
  function toggleDetails(el) {
    if (el) { el.open=!el.open; el.querySelector("summary")?.focus(); }
  }
  function updateTagMode() {
    const hint = host.querySelector(".tagModeHint");
    if (hint) hint.textContent = tagMode ? "标签快捷键已启用：5–9 选择，Esc 退出" : "按 T 进入标签组；普通状态 1–7 切换步骤";
  }
  host.addEventListener("focusin", (e) => {
    if (tagMode && !e.target.matches('[name="tag"]')) { tagMode=false; updateTagMode(); }
  });
  document.addEventListener("keydown", keydown, { signal: abort.signal });

  await init();
  return {
    flush: () => enqueue(flush),
    dispose: () => {
      clearTimeout(timer);
      clearTimeout(uiTimer);
      abort.abort();
    },
    session,
  };
};
