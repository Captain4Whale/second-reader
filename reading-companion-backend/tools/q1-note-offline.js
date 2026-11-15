/* v3.4 adapter inside the existing offline annotator; no HTTP or new database. */
(function (root) {
  const P = Q1NoteProtocol;
  class Session {
    static async load(directory, host) {
      const read = async (name) => {
        try {
          return await (
            await (await directory.getFileHandle(name)).getFile()
          ).text();
        } catch (e) {
          throw Error(
            "无法读取 " + directory.name + " / " + name + "：" + e.message,
          );
        }
      };
      const [mt, ct, ft, jt, pt] = await Promise.all(
        [
          "manifest.json",
          "context.json",
          "rubric-form.json",
          "judgments.jsonl",
          "progress.jsonl",
        ].map(read),
      );
      const m = JSON.parse(mt),
        cases = JSON.parse(ct),
        form = JSON.parse(ft);
      P.need(
        m.schema === "q1-note-session/1" &&
          form.schema === "q1-note-rubric-form/1",
        "不是 v3.4 会话",
      );
      P.need(
        (await P.hash(ft)) === m.rubric_form_sha256 &&
          (await P.hash(P.canonical(cases))) === m.context_sha256,
        "表单或上下文指纹不符",
      );
      for (const k of [
        "rubric_version",
        "rubric_sha256",
        "annotation_guide_sha256",
      ])
        P.need(form[k] === m[k], "表单身份不符");
      P.need(
        form.form_version === m.rubric_form_version &&
          JSON.stringify(cases.map((c) => c.record_id)) ===
            JSON.stringify(m.record_ids) &&
          (await P.hash(P.canonical(m.record_ids))) ===
            m.randomization.order_sha256,
        "表单版本或顺序不符",
      );
      const s = new Session();
      Object.assign(s, {
        host,
        directory,
        m,
        cases,
        form,
        manifestHash: await P.hash(P.canonical(m)),
        handle: await directory.getFileHandle("judgments.jsonl"),
      });
      s.key =
        "note:" +
        m.batch_id +
        ":" +
        m.annotator_id +
        ":" +
        m.rubric_version +
        ":" +
        m.rubric_form_version +
        ":" +
        m.review_session_id;
      const cached = await host.get("state:" + s.key),
        remote = s.parse(jt);
      s.state = cached || { rows: [], drafts: {}, index: 0, unitDrafts: {} };
      P.need(
        !cached || cached.manifestHash === s.manifestHash,
        "缓存会话身份不符",
      );
      s.parse(s.state.rows.map((x) => JSON.stringify(x) + "\n").join(""));
      if (Q1Journal.compare(s.state.rows, remote) > 0) s.state.rows = remote;
      // Import service-era progress read-only, never rewrite it. Browser drafts take over.
      P.need(!pt || pt.endsWith("\n"), "旧进度日志不完整");
      for (const e of pt.split("\n").filter(Boolean).map(JSON.parse))
        if (
          !s.state.drafts[e.record_id] ||
          s.state.drafts[e.record_id].version < e.state.version
        )
          s.state.drafts[e.record_id] = e.state;
      if (!cached && pt.trim()) {
        const last = JSON.parse(pt.trim().split("\n").at(-1));
        s.state.index = Math.max(0, m.record_ids.indexOf(last.record_id));
      }
      for (const r of s.state.rows)
        if (
          r.record_type === "marginalia" &&
          (!s.state.drafts[r.record_id] ||
            s.state.drafts[r.record_id].version < r.event_version)
        )
          s.state.drafts[r.record_id] = {
            version: r.event_version,
            stage: 7,
            record: P.copy(r),
          };
      s.state.manifestHash = s.manifestHash;
      await s.persist();
      await host.put("directory:" + s.key, directory);
      await host.put("note:last", s.key);
      await s.sync();
      return s;
    }
    parse(raw) {
      P.need(!raw || raw.endsWith("\n"), "日志末尾不完整，已停止同步");
      const rows = raw.split("\n").filter(Boolean).map(JSON.parse),
        latest = {};
      rows.forEach((r, i) => {
        P.need(
          r.revision === i + 1 &&
            r.review_session_id === this.m.review_session_id &&
            r.session_manifest_sha256 === this.manifestHash,
          "日志修订或会话身份不符",
        );
        for (const k of [
          "batch_id",
          "annotator_id",
          "rubric_version",
          "rubric_sha256",
          "rubric_form_version",
          "rubric_form_sha256",
          "annotation_guide_sha256",
          "session_purpose",
        ])
          P.need(r[k] === this.m[k], "日志身份不符");
        if (r.record_type === "unit_note") {
          P.need(
            this.cases.some((c) => c.unit_key === r.unit_key) &&
              r.upstream_excluded ===
                r.remarks.trimStart().startsWith("上游："),
            "单元备注无效",
          );
          return;
        }
        const c = this.cases.find((c) => c.record_id === r.record_id);
        P.need(c, "未知批注");
        const expected = P.initial(c, this.m, this.manifestHash).record;
        for (const k of [
          "window_id",
          "unit_key",
          "book_key",
          "body_text",
          "source_quote",
          "original_source_range",
          "randomization",
        ])
          P.need(
            JSON.stringify(P.stable(r[k])) ===
              JSON.stringify(P.stable(expected[k])),
            "批注或随机顺序不符",
          );
        for (const k of [
          "snapshot_sha256",
          "observer_cutoff",
          "original_notes_status",
          "original_note_ids",
        ])
          P.need(
            JSON.stringify(P.stable(r.context[k])) ===
              JSON.stringify(P.stable(expected.context[k])),
            "上下文身份不符",
          );
        P.need(
          r.supersedes_revision === (latest[r.record_id]?.revision ?? null),
          "修订前驱不符",
        );
        P.validate(r, this.form, latest[r.record_id]);
        latest[r.record_id] = r;
      });
      return rows;
    }
    async persist() {
      await this.host.put("state:" + this.key, this.state);
    }
    async sync() {
      await this.persist();
      if (
        (await this.handle.queryPermission({ mode: "readwrite" })) !== "granted"
      )
        throw Error("需要重新授权文件夹；草稿已保存在浏览器。");
      await Q1Journal.append(this.handle, this.state.rows, (x) =>
        this.parse(x),
      );
    }
    api(path, b) {
      const pending = (this.operations || Promise.resolve()).then(() => this.perform(path, b));
      this.operations = pending.catch(() => {});
      return pending;
    }
    async perform(path, b) {
      if (path === "/bootstrap")
        return {
          form: this.form,
          purpose: this.m.session_purpose,
          record_ids: this.m.record_ids,
          last_id: this.m.record_ids[this.state.index],
          completed: this.state.rows
            .filter((r) => r.record_type === "marginalia")
            .map((r) => r.record_id),
        };
      if (path.startsWith("/earlier"))
        return this.cases
          .find((c) => c.record_id === decodeURIComponent(path.split("=")[1]))
          .context.earlier.slice(0, -4);
      const c = this.cases.find((c) => c.record_id === b.id);
      P.need(c, "未知条目");
      if (b.action === "unit_note") {
        const old = this.state.rows.findLast(
          (r) => r.record_type === "unit_note" && r.unit_key === c.unit_key,
        );
        if (old?.remarks !== b.values.remarks) {
          const r = P.initial(c, this.m, this.manifestHash).record;
          this.state.rows.push({
            ...Object.fromEntries(
              [
                "schema",
                "review_session_id",
                "session_purpose",
                "batch_id",
                "annotator_id",
                "rubric_version",
                "rubric_sha256",
                "annotation_guide_sha256",
                "rubric_form_version",
                "rubric_form_sha256",
                "session_manifest_sha256",
              ].map((k) => [k, r[k]]),
            ),
            record_type: "unit_note",
            record_id: c.unit_key,
            unit_key: c.unit_key,
            remarks: b.values.remarks,
            upstream_excluded: b.values.remarks
              .trimStart()
              .startsWith("上游："),
            revision: this.state.rows.length + 1,
            timestamp: new Date().toISOString(),
            supersedes_revision: old?.revision ?? null,
          });
        }
        delete this.state.unitDrafts[c.unit_key];
        await this.sync();
        return { saved: true };
      }
      await this.sync(); // Retry an unacknowledged completion before another transition.
      const state =
        this.state.drafts[b.id] || P.initial(c, this.m, this.manifestHash);
      if (b.action !== "open")
        P.need(b.version === state.version, "状态已改变，请重试恢复后继续");
      const next = P.transition(
        state,
        b.action,
        b.values,
        b.active_ms || 0,
        this.form,
        c,
        this.state.rows,
      );
      this.state.drafts[b.id] = next;
      this.state.index = this.m.record_ids.indexOf(b.id);
      if (b.action === "submit") this.state.rows.push(P.copy(next.record));
      await this.sync();
      return {
        case: c,
        prefix: c.context.prefix,
        recent: c.context.earlier.slice(-4),
        earlier_count: Math.max(0, c.context.earlier.length - 4),
        has_following: Object.fromEntries(
          ["within_unit", "after_unit"].map((k) => [k, !!c.context[k].length]),
        ),
        notes_status: c.context.original_notes.status,
        state: next,
        unit_note:
          this.state.unitDrafts[c.unit_key] ??
          this.state.rows.findLast(
            (r) => r.record_type === "unit_note" && r.unit_key === c.unit_key,
          )?.remarks ??
          "",
        ...(b.action === "following"
          ? { following: c.context[b.values.scope] }
          : {}),
        ...(b.action === "notes" ? { notes: c.context.original_notes } : {}),
      };
    }
  }
  root.Q1NoteOffline = { Session };
})(globalThis);

Q1NoteOffline.mount = async function (session) {
  const container = document.createElement("div");
  container.id = "noteOffline";
  document.querySelector("main").append(container);
  const host = container.attachShadow({ mode: "open" });
  const style = document.createElement("style");
  style.textContent =
    document.querySelector("style").textContent +
    `
 :host{display:block} button,h2,textarea,input,summary,#workflow{scroll-margin-top:calc(var(--reader-top,64px) + 16px);scroll-margin-bottom:100px}.layout{margin-top:16px} #workflow fieldset{border:0;padding:0;margin:14px 0} #workflow legend{font-weight:600} .option{display:flex;gap:8px;align-items:baseline;margin:8px 0} .text{display:block;margin-top:12px} .muted,.eyebrow{color:#667269;font-size:13px} .helpContent p{line-height:1.7} #workflow h2{font-size:18px} .note{white-space:pre-wrap} #sourceText p,#recentText p,#olderText p,.followingText p{white-space:pre-wrap;line-height:1.85} #unitGrid{display:flex;flex-wrap:wrap;gap:4px} #unitGrid button[aria-current=true]{outline:2px solid #367456} #unitGrid button{color:#24352b} #unitGrid .done{background:#cfe4d4} #unitGrid .started{background:#eee2bf} #error{color:#a12828} .helpContent{overflow:visible} #reviewActions{padding:12px 0} textarea{width:100%;box-sizing:border-box} #casePanel{display:block} @media(min-width:1440px){#casePanel.fits-viewport{position:sticky;top:var(--reader-top)}} #caseScroll{height:auto;max-height:none} #workflow{overflow:visible} #readerScroll{max-height:calc(100vh - 220px)} #noteBar{padding:10px 0} #rubricSteps{display:flex;flex-wrap:wrap;gap:4px} @media(max-width:959px){#readerScroll{max-height:none}}`;
  host.append(style);
  const wrap = document.createElement("div");
  wrap.innerHTML = `
 <div id="noteBar"><div class="row"><strong>q1-v3.4 · Note</strong><span id="purpose"></span><span id="position"></span><span id="batchCounts"></span><button id="noteHelp">? 快捷键</button><button id="exportNote">导出 JSONL</button><button id="retry">重试保存 / 恢复授权</button></div><p id="status" role="status"></p><div id="error" role="alert" hidden></div><div id="unitGrid" aria-label="随机顺序条目进度"></div></div>
 <div class="layout rubric-layout">
 <article><h2 id="book"></h2><p id="chapter"></p><div class="row"><span>原文 · 到锚点为止</span><button id="anchorGo">定位锚点</button></div><div id="readerScroll" tabindex="0"><details id="earlier"><summary>查看前文</summary><button id="moreEarlier">展开更早前文</button><div id="olderText"></div><div id="recentText"></div></details><div id="sourceText"></div><div id="following"></div><details id="notes"><summary>原书注释 <span id="noteStatus"></span></summary><div id="notesText"></div></details></div></article>
 <aside id="casePanel" class="panel"><h2 id="caseTitle" tabindex="-1">当前批注</h2><div id="caseScroll"><p id="body" class="note"></p></div><details><summary>单元备注 U</summary><p class="hint">上游问题以“上游：”开头，之后统计排除整个单元。</p><textarea id="unitNote" rows="2"></textarea><button id="saveUnit">保存单元备注</button></details></aside>
 <div class="judgments"><aside class="panel review-panel"><nav id="rubricSteps"></nav><div id="decisionScroll"><section id="workflow"></section></div><div id="reviewActions"></div><div class="row"><button id="prev">上一条 ↑</button><button id="decisionGo">返回判定</button><button id="next">下一条 ↓</button><span id="saveHint"></span></div></aside></div></div>
 <dialog id="shortcutHelp"><h2>快捷键 · v3.4</h2><p>P / F：当前二选一判定；Enter：确认当前步骤；Shift+Enter：末步提交后下一条。</p><p>1–7 或 [ / ]：回看已开放步骤；Shift+数字：提示展开 / 收起。第一印象与费劲的锁定不受回看影响。</p><p>↑ / ↓、← / →：按随机顺序上一条 / 下一条。J / K：原文滚动；Shift+J / K：页面滚动。</p><p>R：本项理由；M：整条理由；U：单元备注；V：待核实；S：星；0：未覆盖；?：帮助；Esc：退出输入。</p><p>标签步骤 5–9 切换标签。三选一、多选及写法请用 Tab、方向键和空格操作。输入法和文本框不拦截快捷键。</p><button id="closeNoteHelp">关闭 Esc</button></dialog>`;
  host.append(wrap);
  try {
    const view = await Q1NoteView(host, session);
    return {
      ...view,
      dispose() {
        view.dispose();
        container.remove();
      },
    };
  } catch (e) {
    container.remove();
    throw e;
  }
};
