/* Dedicated v3.4 UI. All durable transitions and validation are server-owned. */
"use strict";
const $ = (id) => document.getElementById(id);
let boot,
  data,
  index = 0,
  dirty = false,
  timer,
  active = 0,
  clock = performance.now(),
  busy = false,
  editEpoch = 0;
const labels = [
  "第一印象",
  "读着费劲",
  "N1",
  "有剧透",
  "有错误信息",
  "结论",
  "标签",
];
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
  $("error").hidden = false;
  $("error").textContent = error.message;
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
document.addEventListener("visibilitychange", () => {
  const t = performance.now();
  if (document.hidden) active += t - clock;
  clock = t;
  if (dirty && !busy) save().catch(shownError);
});
async function api(path, body) {
  const res = await fetch(
    path,
    body
      ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      : {},
  );
  const result = await res.json();
  if (!res.ok) throw Error(result.error);
  return result;
}
function textArea(parent, id, label, value = "") {
  parent.append(node("label", label, "text"));
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
  f.append(node("legend", title));
  for (const v of values) {
    const l = node("label", undefined, "option"),
      i = node("input");
    i.type = "radio";
    i.name = name;
    i.value = v;
    i.checked = value === v;
    l.append(i, node("span", v === "pass" ? "过" : v === "fail" ? "不过" : v));
    f.append(l);
  }
  parent.append(f);
}
function get(name) {
  return document.querySelector(`#workflow input[name="${name}"]:checked`)
    ?.value;
}
function checked(name) {
  return !!document.querySelector(`#workflow input[name="${name}"]`)?.checked;
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
  if (document.querySelector("[name=star]")) v.star = checked("star");
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
        ...document.querySelectorAll("[name=failure]:checked"),
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
    v.tags = [...document.querySelectorAll("[name=tag]:checked")].map(
      (x) => x.value,
    );
  return v;
}
async function post(action, values = {}, renderAfter = true) {
  if (busy) throw Error("正在保存，请稍候");
  const epoch = editEpoch;
  const duration = elapsed();
  let succeeded = false;
  const controls = action === "save" ? [] : [...document.querySelectorAll("input,textarea,select")].map(e => [e,e.disabled]);
  controls.forEach(([e]) => e.disabled = true);
  busy = true;
  $("status").textContent = "正在保存…";
  document.querySelectorAll("button").forEach((b) => (b.disabled = true));
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
    if (renderAfter && !dirty) render();
    else updateStatus();
    return result;
  } catch (e) {
    active += duration;
    $("status").textContent = "保存失败 · 请重试";
    throw e;
  } finally {
    busy = false;
    controls.forEach(([e,disabled]) => { if(e.isConnected) e.disabled=disabled; });
    document.querySelectorAll("button").forEach((b) => (b.disabled = false));
    $("prev").disabled = index === 0;
    $("next").disabled = index === boot.record_ids.length - 1;
    if (dirty && succeeded) {
      clearTimeout(timer);
      timer = setTimeout(() => save(true).catch(shownError), 700);
    }
  }
}
function updateStatus() {
  $("status").textContent = dirty ? "尚未保存" : "已保存到本机会话";
}
async function save(renderAfter = false) {
  clearTimeout(timer);
  if (!dirty) return;
  if (busy) return;
  await post("save", collect(), renderAfter);
}
async function flush() {
  clearTimeout(timer);
  if (busy) throw Error("正在保存，请稍候再操作");
  if (dirty) await save();
}
async function openCase(i) {
  if (i < 0 || i >= boot.record_ids.length) return;
  await flush();
  index = i;
  data = await api("/action", { id: boot.record_ids[index], action: "open" });
  active = 0;
  clock = performance.now();
  render();
  $("prev").disabled = index === 0;
  $("next").disabled = index === boot.record_ids.length - 1;
  window.scrollTo(0, 0);
}
function render() {
  const s = data.state.stage,
    r = data.state.record,
    c = boot.form.choices;
  $("position").textContent = `${index + 1} / ${boot.record_ids.length} 条`;
  $("purpose").textContent = boot.purpose === "test" ? "测试会话" : "正式会话";
  $("book").textContent = data.case.book;
  $("chapter").textContent = data.case.chapter_title;
  $("body").textContent = data.case.body_text;
  segments($("sourceText"), data.prefix);
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
        `读着费劲：${r.reading_difficulty.choice}；修改 ${r.reading_difficulty.amendments.length} 次。`,
        "muted",
      ),
    );
    if (r.tags) w.append(node("p", `标签：${r.tags.join("、") || "无"}`));
    if (r.star) w.append(node("p", "★ 范例级批注"));
    if (r.unsure.length) w.append(node("p", `拿不准：${r.unsure.map(k=>`${k}（${r.unsure_sources[k].map(s=>s==='automatic'?'自动':'手动').join('、')}）`).join('；')}`, "muted"));
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
    help.append(
      node("summary", `判定提示 · rubric ${spec.section}`),
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
        "“改写不出”：想法本身就绕，已经说得尽量清楚。不勾否决，自动勾拿不准。",
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
      w.append(node("p", "失败类型（至少一个，可多选）"));
      for (const label of c.failure_types) {
        const i = check(w, "failure", label, n.failure_types?.includes(label));
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
    "这一项拿不准（手动）",
    r.unsure_sources[labels[s]]?.includes("manual"),
  );
  if (r.unsure_sources[labels[s]]?.includes("automatic"))
    flags.append(
      node("p", "已自动勾选拿不准：读着费劲选择了“改写不出”。", "muted"),
    );
  check(flags, "uncovered", "rubric 未覆盖", r.rubric_uncovered);
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
  const complete = node(
    "button",
    s === 6
      ? "确认并提交本条"
      : s === 0
        ? "锁定第一印象，继续"
        : "完成此步，继续",
    "primary",
  );
  complete.onclick = async () => {
    try {
      await flush();
      await post(s === 6 ? "submit" : "complete", collect());
    } catch (e) {
      shownError(e);
    }
  };
  w.append(complete);
  updateStatus();
  autoGrow();
}
function amendControls(w, r) {
  const d = node("details");
  d.append(
    node("summary", `修正读着费劲 · 当前：${r.reading_difficulty.choice}`),
  );
  d.append(
    node(
      "p",
      `首次：${r.reading_difficulty.original_choice}。修正不覆盖原值，结论使用最终值。`,
      "muted",
    ),
  );
  const sel = node("select");
  sel.setAttribute("aria-label", "修正后的费劲选项");
  for (const v of boot.form.choices.reading_difficulty) {
    const o = node("option", v);
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
  document.querySelectorAll("textarea").forEach((t) => {
    t.style.height = "auto";
    t.style.height = Math.max(72, t.scrollHeight + 2) + "px";
  });
}
$("workflow").addEventListener("input", (e) => {
  if (e.target.id.startsWith("amend") || e.target.tagName === "SELECT") return;
  editEpoch++;
  dirty = true;
  updateStatus();
  autoGrow();
  clearTimeout(timer);
  timer = setTimeout(() => save().catch(shownError), 700);
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
$("anchorGo").onclick = () =>
  $("sourceText").querySelector("mark")?.scrollIntoView({ block: "center" });
$("decisionGo").onclick = () =>
  $("workflow").scrollIntoView({ block: "start" });
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
window.addEventListener("beforeunload", (e) => {
  if (dirty || busy) {
    e.preventDefault();
    e.returnValue = "";
  }
});
(async () => {
  boot = await api("/bootstrap");
  await openCase(Math.max(0, boot.record_ids.indexOf(boot.last_id)));
})().catch(shownError);
