const { test } = require("node:test"),
  assert = require("node:assert/strict"),
  fs = require("node:fs");
const P = require("./q1-note-protocol.js");
require("./q1-journal.js");
require("./q1-note-form-v2.js");
require("./q1-note-offline.js");
async function fixture() {
  const formText = fs.readFileSync(
      __dirname + "/../rubric/q1-v3.4.form.v1.json",
      "utf8",
    ),
    f = JSON.parse(formText);
  const p = { chapter_id: 1, paragraph_index: 1, char_offset: 0 },
    range = { start: p, end: { ...p, char_offset: 1 } };
  const cases = [
    {
      record_id: "r",
      window_id: "w",
      unit_key: "w",
      book_key: "b",
      body_text: "批注",
      source_quote: "文",
      original_source_range: range,
      context: {
        prefix: [],
        earlier: [],
        within_unit: [],
        after_unit: [],
        observer_cutoff: range.end,
        original_notes: { status: "unresolved", items: [] },
      },
    },
  ];
  const m = {
    schema: "q1-note-session/1",
    rubric_version: f.rubric_version,
    rubric_sha256: f.rubric_sha256,
    annotation_guide_sha256: f.annotation_guide_sha256,
    rubric_form_version: f.form_version,
    rubric_form_sha256: await P.hash(formText),
    context_sha256: await P.hash(P.canonical(cases)),
    record_ids: ["r"],
    randomization: { seed: 7, order_sha256: await P.hash(P.canonical(["r"])) },
    session_purpose: "test",
    review_session_id: "test",
    batch_id: "batch",
    annotator_id: "test",
  };
  const files = {
      "manifest.json": JSON.stringify(m),
      "context.json": JSON.stringify(cases),
      "rubric-form.json": formText,
      "judgments.jsonl": "",
      "progress.jsonl": "",
    },
    db = new Map();
  let diskFail = false,
    dbFail = false;
  const dir = {
    name: "test",
    getFileHandle: async (name) => ({
      queryPermission: async () => "granted",
      getFile: async () => ({
        text: async () => files[name],
        size: Buffer.byteLength(files[name]),
      }),
      createWritable: async () => {
        if (diskFail) throw Error("disk failed");
        let text = "";
        return {
          seek: async () => {},
          write: async (s) => {
            text = s;
          },
          close: async () => {
            files[name] += text;
          },
          abort: async () => {},
        };
      },
    }),
  };
  const host = {
    get: async (k) => structuredClone(db.get(k)),
    put: async (k, v) => {
      if (dbFail) throw Error("browser failed");
      if (k.startsWith("directory:")) return;
      db.set(k, structuredClone(v));
    },
  };
  const s = await Q1NoteOffline.Session.load(dir, host);
  return {
    s,
    dir,
    host,
    files,
    db,
    set diskFail(v) {
      diskFail = v;
    },
    set dbFail(v) {
      dbFail = v;
    },
  };
}
async function act(s, action, values) {
  return s.api("/action", {
    id: "r",
    action,
    values,
    version: s.state.drafts.r?.version,
    active_ms: 1,
  });
}
async function ready(s) {
  await act(s, "open");
  for (const v of [
    { judgment: "pass" },
    { first_pass:"复述不出或说偏", rewrite:"改写不出" },
    {
      n1: {
        following_text_use: "没用到",
        judgment: "pass",
        writing_style: "补充",
      },
    },
    { spoiler: false },
    { incorrect_information: false },
    {},
  ])
    await act(s, "complete", v);
}
test("offline reload restores first lock/drafts, completed journal parsed by browser", async () => {
  const x = await fixture();
  await ready(x.s);
  await act(x.s, "submit");
  const prefix = x.files["judgments.jsonl"];
  const restored = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.equal(restored.state.drafts.r.stage, 7);
  assert.equal(restored.state.rows.length, 1);
  await restored.sync();
  assert.equal(x.files["judgments.jsonl"], prefix);
  assert.equal(x.files["progress.jsonl"], "");
});
test("failed disk keeps completed row in browser; retry appends exactly once", async () => {
  const x = await fixture();
  await ready(x.s);
  x.diskFail = true;
  await assert.rejects(act(x.s, "submit"), /disk failed/);
  assert.equal(x.s.state.rows.length, 1);
  assert.equal(x.files["judgments.jsonl"], "");
  x.diskFail = false;
  await x.s.sync();
  await x.s.sync();
  assert.equal(x.files["judgments.jsonl"].trim().split("\n").length, 1);
});
test("failed browser save prevents disk advancement and allows retry", async () => {
  const x = await fixture();
  await ready(x.s);
  x.dbFail = true;
  await assert.rejects(act(x.s, "submit"), /browser failed/);
  assert.equal(x.files["judgments.jsonl"], "");
  x.dbFail = false;
  await x.s.sync();
  await act(x.s, "open");
  assert.equal(x.s.state.rows.length, 0);
  await act(x.s, "submit");
  assert.equal(x.s.state.rows.length, 1);
});
test("fork or partial disk stops without overwrite", async () => {
  const x = await fixture();
  await ready(x.s);
  await act(x.s, "submit");
  x.files["judgments.jsonl"] = x.files["judgments.jsonl"].replace(
    "批注",
    "改动",
  );
  const before = x.files["judgments.jsonl"];
  await assert.rejects(x.s.sync());
  assert.equal(x.files["judgments.jsonl"], before);
  x.files["judgments.jsonl"] = before.slice(0, -1);
  await assert.rejects(x.s.sync(), /末尾不完整/);
});
test("unit upstream exclusion appends revisions and reopens latest state", async () => {
  const x = await fixture();
  for (const remarks of ["上游：混入注释", ""])
    await x.s.api("/action", {
      id: "r",
      action: "unit_note",
      values: { remarks },
    });
  assert.equal(x.s.state.rows.length, 2);
  assert.equal(x.s.state.rows[1].upstream_excluded, false);
  assert.equal(
    (await Q1NoteOffline.Session.load(x.dir, x.host)).state.rows.length,
    2,
  );
});

test("service-era progress imports read-only and keeps first lock", async () => {
  const x = await fixture();
  await act(x.s, "open");
  await act(x.s, "complete", { judgment: "fail" });
  const event = { record_id: "r", state: structuredClone(x.s.state.drafts.r) };
  x.files["progress.jsonl"] = JSON.stringify(event) + "\n";
  const prefix = x.files["progress.jsonl"];
  const db = new Map();
  const host = {
    get: async (k) => db.get(k),
    put: async (k, v) => {
      if (!k.startsWith("directory:")) db.set(k, structuredClone(v));
    },
  };
  const restored = await Q1NoteOffline.Session.load(x.dir, host);
  assert.equal(restored.state.drafts.r.stage, 1);
  assert.deepEqual(
    restored.state.drafts.r.record.first_impression,
    event.state.record.first_impression,
  );
  await act(restored, "save", { first_pass:"复述不出或说偏", rewrite:"改写不出" });
  assert.equal(x.files["progress.jsonl"], prefix);
});
test('invalid transition is validation feedback, persistence failure is not', async () => {
  const f=await fixture(); await act(f.s,'open');
  await assert.rejects(act(f.s,'complete',{}),e=>e.code==='FORM_VALIDATION');
  assert.equal(f.s.state.drafts.r.stage,0);
  f.dbFail=true;
  await assert.rejects(act(f.s,'complete',{judgment:'pass'}),e=>e.code!=='FORM_VALIDATION');
});


test("legacy browser drafts recover previously opened steps without rewriting logs", async () => {
  const x = await fixture();
  await ready(x.s);
  const old = structuredClone(x.s.state);
  const d = old.drafts.r;
  d.stage = 1;
  delete d.viewStep;
  delete d.maxUnlockedStage;
  delete d.dirtySteps;
  for (const key of P.steps.slice(1)) delete d.record.steps[key]?.completed_at;
  x.db.set("state:" + x.s.key, old);
  const restored = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.equal(restored.state.drafts.r.stage, 1);
  assert.equal(restored.state.drafts.r.viewStep, 1);
  assert.equal(restored.state.drafts.r.maxUnlockedStage, 6);
  assert.equal(x.files["judgments.jsonl"], "");
  assert.equal(x.files["progress.jsonl"], "");
  assert.deepEqual(restored.state.drafts.r.record.first_impression, d.record.first_impression);
});

test("browsing a submitted record preserves its completion and file receipt", async () => {
  const x = await fixture();
  await ready(x.s);
  await act(x.s, "submit");
  const original = structuredClone(x.s.state.rows[0]);
  const prefix = x.files["judgments.jsonl"];
  const viewed = await act(x.s, "navigate", { step: 1 });
  assert.equal(viewed.state.viewStep, 1);
  assert.equal(viewed.state.stage, 7);
  assert.equal(viewed.state.maxUnlockedStage, 6);
  assert.deepEqual(viewed.state.record, original);
  assert.equal(viewed.receipt.submitted_revision, 1);
  assert.equal(viewed.receipt.has_unsubmitted_changes, false);
  assert.equal(viewed.receipt.file_revision, 1);
  await act(x.s, "navigate", { step: 2 });
  assert.equal(x.files["judgments.jsonl"], prefix);
  const boot = await x.s.api("/bootstrap");
  assert.deepEqual(boot.completed, ["r"]);
  assert.equal(boot.session_id, "test");
  assert.equal(boot.directory_name, "test");
  assert.equal(boot.tool_version, "q1-annotator/3.6");
});

test("browser-only UI metadata survives reload without changing the judgment version", async () => {
  const x = await fixture();
  await ready(x.s);
  const original = structuredClone(x.s.state.drafts.r);
  await act(x.s, "ui_meta", { ui: { branches: { otherWriting: "keep explanation" }, reader: { scrollTop: 130, earlier: true } } });
  await act(x.s, "ui_meta", { ui: { reader: { scrollTop: 240, earlier: true } } });
  assert.equal(x.s.state.drafts.r.version, original.version);
  assert.deepEqual(x.s.state.drafts.r.record, original.record);
  const restored = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.deepEqual(restored.state.drafts.r.ui, {
    branches: { otherWriting: "keep explanation" }, reader: { scrollTop: 240, earlier: true },
  });
  assert.equal(x.files["judgments.jsonl"], "");
  assert.equal(x.files["progress.jsonl"], "");
});

test("action UI metadata is persisted with the judgment but excluded from exported rows", async () => {
  const x = await fixture();
  await ready(x.s);
  await x.s.api("/action", {
    id: "r", action: "submit", version: x.s.state.drafts.r.version,
    values: {}, ui: { branches: { otherFailure: "inactive explanation" } }, active_ms: 1,
  });
  const restored = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.equal(restored.state.drafts.r.ui.branches.otherFailure, "inactive explanation");
  const row = JSON.parse(x.files["judgments.jsonl"]);
  assert.equal(Object.hasOwn(row, "ui"), false);
  assert.equal(Object.hasOwn(row, "viewStep"), false);
  assert.equal(Object.hasOwn(row, "dirtySteps"), false);
});

test("draft and pending-file receipts stay distinct across edits and a failed revision", async () => {
  const x = await fixture();
  await ready(x.s);
  assert.equal(x.s.receipt("r").has_unsubmitted_changes, true);
  assert.equal(x.s.receipt("r").file_revision, 0);
  await act(x.s, "submit");
  const prefix = x.files["judgments.jsonl"];
  const untouched = x.s.state.rows[0].steps.n1.completed_at;
  await act(x.s, "navigate", { step: 1 });
  await act(x.s, "begin_discussion");
  await act(x.s, "navigate", { step: 1 });
  await act(x.s, "save", { rewrite:"能改写得更直白", amendment_reason:"测试理由" });
  assert.deepEqual(x.s.receipt("r"), {
    browser_saved: true, journal_revision: 1, file_revision: 1,
    pending_file: false, submitted_revision: 1, has_unsubmitted_changes: true,
  });
  await act(x.s, "navigate", { step: 6 });
  x.diskFail = true;
  await assert.rejects(act(x.s, "submit"), /disk failed/);
  assert.equal(x.s.receipt("r").browser_saved, true);
  assert.equal(x.s.receipt("r").file_revision, 1);
  assert.equal(x.s.receipt("r").journal_revision, 2);
  assert.equal(x.s.receipt("r").pending_file, true);
  assert.equal(x.files["judgments.jsonl"], prefix);
  x.diskFail = false;
  const receipt = await x.s.sync();
  assert.equal(receipt.file_revision, 2);
  assert.equal(receipt.pending_file, false);
  await x.s.sync();
  assert.equal(x.files["judgments.jsonl"].trim().split("\n").length, 2);
  assert.equal(x.s.state.rows[1].steps.n1.completed_at, untouched);
  assert.equal(x.s.state.rows[1].reading_difficulty.amendments.length, 1);
  assert.equal(x.files["judgments.jsonl"].startsWith(prefix), true);
});


test("saving an untouched empty unit note does not append a judgment row", async () => {
  const x = await fixture();
  await act(x.s, "unit_note", { remarks: "" });
  await act(x.s, "unit_note", { remarks: "" });
  assert.equal(x.s.state.rows.length, 0);
  assert.equal(x.files["judgments.jsonl"], "");
  await act(x.s, "unit_note", { remarks: "QA note" });
  await act(x.s, "unit_note", { remarks: "QA note" });
  assert.equal(x.s.state.rows.length, 1);
});

test("reading UI metadata can be cached while a submitted row awaits disk retry", async () => {
  const x = await fixture();
  await ready(x.s);
  x.diskFail = true;
  await assert.rejects(act(x.s, "submit"), /disk failed/);
  const original = structuredClone(x.s.state.drafts.r);
  const result = await act(x.s, "ui_meta", { ui: { reader: { scrollTop: 80 } } });
  assert.equal(result.state.version, original.version);
  assert.deepEqual(result.state.record, original.record);
  assert.equal(result.receipt.pending_file, true);
  assert.equal(result.receipt.browser_saved, true);
  assert.equal(x.files["judgments.jsonl"], "");
  x.diskFail = false;
  const restored = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.equal(restored.state.drafts.r.ui.reader.scrollTop, 80);
  assert.equal(restored.state.rows.length, 1);
  assert.equal(restored.receipt("r").pending_file, false);
});

test("file failure returns the applied draft version and retry does not duplicate a submission", async () => {
  const x = await fixture(); await ready(x.s);
  const before = x.s.state.drafts.r.version;
  x.diskFail = true;
  let failure;
  await assert.rejects(act(x.s, "submit"), error => {
    failure = error;
    return /disk failed/.test(error.message);
  });
  assert.equal(failure.actionApplied, true);
  assert.equal(failure.currentState.version, before + 1);
  assert.equal(failure.currentState.stage, 7);
  assert.equal(failure.receipt.browser_saved, true);
  assert.equal(failure.receipt.pending_file, true);
  assert.equal(failure.receipt.submitted_revision, 1);
  failure.currentState.record.reason = "caller copy";
  assert.equal(x.s.state.drafts.r.record.reason, "");
  x.diskFail = false;
  await x.s.sync();
  const revisited = await x.s.api("/action", {
    id:"r", action:"navigate", values:{step:1}, version:failure.currentState.version,
  });
  assert.equal(revisited.state.viewStep, 1);
  assert.equal(x.files["judgments.jsonl"].trim().split("\n").length, 1);
  assert.equal(x.s.state.rows.length, 1);
});

test("post-transition browser failure distinguishes in-memory progress from persisted recovery", async () => {
  const x = await fixture(); await ready(x.s);
  const before = x.s.state.drafts.r.version, originalPut = x.host.put;
  let calls = 0;
  x.host.put = async (...args) => {
    if (++calls === 2) throw Error("late browser failed");
    return originalPut(...args);
  };
  let failure;
  await assert.rejects(act(x.s, "submit"), error => {
    failure = error;
    return /late browser failed/.test(error.message);
  });
  assert.equal(failure.actionApplied, true);
  assert.equal(failure.currentState.version, before + 1);
  assert.equal(failure.receipt.browser_saved, false);
  assert.equal(failure.receipt.pending_file, true);
  assert.equal(x.files["judgments.jsonl"], "");
  x.host.put = originalPut;
  await x.s.sync();
  await x.s.api("/action", {id:"r", action:"navigate", values:{step:2}, version:failure.currentState.version});
  assert.equal(x.s.state.rows.length, 1);
  assert.equal(x.files["judgments.jsonl"].trim().split("\n").length, 1);
});

test("validation and pre-transition persistence failure report that the action was not applied", async () => {
  const x = await fixture(); await act(x.s, "open");
  const before = x.s.state.drafts.r.version;
  await assert.rejects(act(x.s, "complete"), error =>
    error.code === "FORM_VALIDATION" && !error.actionApplied && error.currentState.version === before);
  x.dbFail = true;
  await assert.rejects(act(x.s, "complete", {judgment:"pass"}), error =>
    !error.actionApplied && error.currentState.version === before && error.receipt.browser_saved === false);
});

test("offline release is identical to published v2, and original-only export excludes amendments and unit notes", async () => {
  const form = fs.readFileSync(__dirname + "/../rubric/q1-v3.4.form.v2.json", "utf8");
  assert.equal(JSON.stringify(Q1NoteFormV2, null, 2) + "\n", form);
  const x = await fixture();
  await ready(x.s);
  await act(x.s, "submit");
  const first = structuredClone(x.s.state.rows[0]);
  assert.equal(first.rubric_form_version, "q1-v3.4.form.v2");
  await act(x.s, "unit_note", {remarks:"合成备注"});
  await act(x.s, "begin_discussion");
  await act(x.s, "navigate", {step:6});
  await act(x.s, "submit", {reason:"合成修改", amendment_reason:"合成讨论"});
  const reopened = await Q1NoteOffline.Session.load(x.dir, x.host);
  assert.equal(reopened.state.rows.length, 3);
  assert.deepEqual(Q1NoteOffline.firstJudgments(reopened.state.rows), [first]);
});
