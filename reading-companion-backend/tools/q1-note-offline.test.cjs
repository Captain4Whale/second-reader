const { test } = require("node:test"),
  assert = require("node:assert/strict"),
  fs = require("node:fs");
const P = require("./q1-note-protocol.js");
require("./q1-journal.js");
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
    { choice: P.difficulty[0] },
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
  await act(restored, "save", { choice: P.difficulty[2] });
  assert.equal(x.files["progress.jsonl"], prefix);
});
test('invalid transition is validation feedback, persistence failure is not', async () => {
  const f=await fixture(); await act(f.s,'open');
  await assert.rejects(act(f.s,'complete',{}),e=>e.code==='FORM_VALIDATION');
  assert.equal(f.s.state.drafts.r.stage,0);
  f.dbFail=true;
  await assert.rejects(act(f.s,'complete',{judgment:'pass'}),e=>e.code!=='FORM_VALIDATION');
});
