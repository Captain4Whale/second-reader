const { test } = require("node:test"),
  assert = require("node:assert/strict"),
  fs = require("node:fs");
const P = require("./q1-note-protocol.js"),
  form = JSON.parse(
    fs.readFileSync(__dirname + "/../rubric/q1-v3.4.form.v1.json"),
  );
const pos = { chapter_id: 1, paragraph_index: 1, char_offset: 0 },
  range = { start: pos, end: { ...pos, char_offset: 1 } };
const c = {
  record_id: "r",
  window_id: "w",
  unit_key: "w",
  book_key: "b",
  body_text: "批注",
  source_quote: "文",
  original_source_range: range,
  context: {
    observer_cutoff: range.end,
    original_notes: { status: "unresolved", items: [] },
    within_unit: [{ range, text: "后文" }],
    after_unit: [],
  },
};
const m = {
  record_ids: ["r"],
  randomization: { seed: 7 },
  context_sha256: "x",
};
function setup() {
  let s = P.initial(c, m, "h"),
    rows = [];
  return {
    get s() {
      return s;
    },
    rows,
    act(a, v) {
      s = P.transition(s, a, v, 1, form, c, rows);
      if (a === "submit") rows.push(structuredClone(s.record));
      return s;
    },
  };
}
function core(
  h,
  d = P.difficulty[0],
  n = { following_text_use: "没用到", judgment: "pass", writing_style: "补充" },
) {
  h.act("complete", { judgment: "pass" });
  h.act("complete", { choice: d });
  h.act("complete", { n1: n });
  h.act("complete", { spoiler: false });
  h.act("complete", { incorrect_information: false, needs_verification: true });
}
function done(h) {
  h.act("complete");
  return h.act("submit").record;
}
test("required first impression, difficulty and immutable locks", () => {
  const h = setup();
  assert.throws(() => h.act("complete"), /第一印象/);
  h.act("complete", { judgment: "pass" });
  assert.throws(() => h.act("save", { judgment: "fail" }), /锁定/);
  assert.throws(() => h.act("following", { scope: "within_unit" }), /只有/);
  assert.throws(() => h.act("complete"), /读着费劲/);
});
test("final difficulty controls outcome; original and all transitions retained", () => {
  const h = setup();
  core(h);
  h.act("amend", { choice: P.difficulty[1] });
  assert.equal(h.s.record.judgment, "fail");
  h.act("amend", { choice: P.difficulty[2] });
  assert.deepEqual(h.s.record.unsure_sources, { 读着费劲: ["automatic"] });
  h.act("amend", { choice: P.difficulty[0] });
  const r = done(h);
  assert.equal(r.judgment, "pass");
  assert.equal(r.reading_difficulty.amendments.length, 3);
  assert.deepEqual(r.unsure, []);
});
test("manual uncertainty survives automatic trigger removal", () => {
  const h = setup();
  h.act("complete", { judgment: "pass" });
  h.act("complete", { choice: P.difficulty[2], manual_unsure: true });
  h.act("complete", {
    n1: {
      following_text_use: "没用到",
      judgment: "pass",
      writing_style: "补充",
    },
  });
  h.act("complete", { spoiler: false });
  h.act("complete", { incorrect_information: false });
  h.act("amend", { choice: P.difficulty[0] });
  assert.deepEqual(h.s.record.unsure_sources, { 读着费劲: ["manual"] });
});
test("uncovered forces fail, clears tags/star and requires reason", () => {
  const h = setup();
  core(h);
  h.act("save", { star: true });
  h.act("save", { rubric_uncovered: true });
  assert.equal(h.s.record.star, false);
  assert.ok(!("tags" in h.s.record));
  assert.throws(() => done(h), /原因/);
  h.act("save", { uncovered_reason: "缺口" });
  assert.equal(done(h).judgment, "fail");
});
test("N1 failure still requires spoiler and incorrect information", () => {
  const h = setup();
  core(h, P.difficulty[0], {
    following_text_use: "紧接着几段",
    judgment: "fail",
    failure_types: ["下文马上讲了"],
  });
  const r = done(h);
  assert.equal(r.judgment, "fail");
  assert.ok(!("tags" in r));
  assert.ok(
    r.steps.spoiler.completed_at && r.steps.incorrect_information.completed_at,
  );
});
test("following exposure per step and early anchor tag survive reopen", () => {
  const h = setup();
  h.act("complete", { judgment: "pass" });
  h.act("complete", { choice: P.difficulty[0] });
  h.act("following", { scope: "within_unit" });
  h.act("complete", {
    n1: {
      following_text_use: "挂早了",
      judgment: "pass",
      writing_style: "解读",
    },
  });
  h.act("following", { scope: "within_unit" });
  h.act("complete", { spoiler: false });
  h.act("complete", { incorrect_information: false });
  const r = done(h);
  assert.deepEqual(r.tags, ["锚点问题"]);
  h.act("reopen");
  assert.equal(h.s.record.steps.n1.following_text_views.length, 1);
  assert.equal(h.s.record.steps.spoiler.following_text_views.length, 1);
});
for (const n of [
  { following_text_use: "没用到", judgment: "pass", writing_style: "其他写法" },
  { following_text_use: "没用到", judgment: "fail", failure_types: [] },
  { following_text_use: "没用到", judgment: "fail", failure_types: ["其他"] },
  {
    following_text_use: "没用到",
    judgment: "pass",
    writing_style: "补充",
    failure_types: ["其他"],
  },
])
  test("reject invalid N1 " + JSON.stringify(n), () =>
    assert.throws(() => P.n1valid(n, form)),
  );
test("reader rejects labels on fail and mutated outcome", () => {
  const h = setup();
  core(h, P.difficulty[1]);
  const r = done(h);
  assert.throws(() => P.validate({ ...r, tags: [] }, form));
  assert.throws(() => P.validate({ ...r, judgment: "pass" }, form));
});
test("fingerprint compact unicode", () =>
  assert.equal(
    P.canonical({ z: ["文", true], a: { b: 1 } }),
    '{"a":{"b":1},"z":["文",true]}',
  ));

for (const target of [2, 3, 4]) test(`correct completed step ${target} before submission`, () => {
  const h = setup(); core(h);
  const before = structuredClone(h.s.record);
  h.act("reopen", {step: target});
  assert.equal(h.s.stage, target);
  assert.deepEqual(h.s.record.first_impression, before.first_impression);
  assert.deepEqual(h.s.record.reading_difficulty, before.reading_difficulty);
  assert.deepEqual(h.s.record.n1, before.n1);
  for (const k of P.steps.slice(target)) assert.equal(h.s.record.steps[k].completed_at, undefined);
  assert.throws(() => h.act("submit"), /顺序/);
  assert.equal(h.rows.length, 0);
});
test("N1 correction preserves exposure and appends a new confirmed revision", () => {
  const h = setup();
  h.act("complete", {judgment:"pass"}); h.act("complete", {choice:P.difficulty[0]});
  h.act("following", {scope:"within_unit"});
  h.act("complete", {n1:{following_text_use:"没用到",judgment:"fail",failure_types:["下文马上讲了"]}});
  const exposure = structuredClone(h.s.record.steps.n1.following_text_views);
  h.act("reopen", {step:2});
  assert.deepEqual(h.s.record.steps.n1.following_text_views, exposure);
  h.act("complete", {n1:{following_text_use:"没用到",judgment:"pass",writing_style:"补充"}});
  h.act("complete", {spoiler:false}); h.act("complete", {incorrect_information:false});
  done(h); const original = JSON.stringify(h.rows[0]);
  h.act("reopen", {step:3}); h.act("complete", {spoiler:true});
  h.act("complete", {incorrect_information:false}); done(h);
  assert.equal(JSON.stringify(h.rows[0]), original);
  assert.equal(h.rows[1].supersedes_revision, 1);
  assert.equal(h.rows[1].judgment, "fail");
  assert.deepEqual(h.rows[1].steps.n1.following_text_views, exposure);
});
test("correction cannot unlock first impression, difficulty, future or current steps", () => {
  const h = setup(); core(h);
  for (const step of [0,1,5,6,7,-1,2.5,"2",true])
    assert.throws(() => h.act("reopen", {step}), /只能修改/);
});

test('difficulty can be corrected immediately after leaving step two with audit trail', () => {
  const h=setup();
  assert.throws(()=>h.act('amend',{choice:P.difficulty[1]}),/完成读着费劲/);
  h.act('complete',{judgment:'pass'});
  h.act('complete',{choice:P.difficulty[0]});
  h.act('amend',{choice:P.difficulty[1]});
  assert.equal(h.s.stage,2);
  assert.equal(h.s.record.reading_difficulty.original_choice,P.difficulty[0]);
  assert.equal(h.s.record.vetoes.reading_difficulty,true);
  h.act('amend',{choice:P.difficulty[2]});
  assert.equal(h.s.record.vetoes.reading_difficulty,false);
  assert.equal(h.s.record.reading_difficulty.amendments[1].from,P.difficulty[1]);
  assert.equal(h.s.record.reading_difficulty.amendments[1].to,P.difficulty[2]);
});
