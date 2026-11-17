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
test("correction cannot unlock first impression, future or current steps", () => {
  const h = setup(); core(h);
  for (const step of [0,5,6,7,-1,2.5,"2",true])
    assert.throws(() => h.act("reopen", {step}), /只能返回/);
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

test('original difficulty form records every changed saved value, never replaces the initial judgment', () => {
  const h=setup();core(h);done(h);
  const original=JSON.stringify(h.rows[0]);
  const first=structuredClone(h.s.record.first_impression);
  h.act('reopen',{step:1});
  h.act('save',{choice:P.difficulty[1],paraphrase:'重新复述',rewrite:'更直接'});
  assert.equal(h.s.record.judgment,'fail');
  h.act('save',{choice:P.difficulty[1]}); // Repeated autosave is not another amendment.
  h.act('save',{choice:P.difficulty[2],manual_unsure:true});
  assert.deepEqual([...h.s.record.unsure_sources['读着费劲']].sort(),['automatic','manual']);
  h.act('complete',{choice:P.difficulty[0],manual_unsure:true});
  assert.equal(h.s.stage,2);
  assert.equal(h.s.record.reading_difficulty.original_choice,P.difficulty[0]);
  assert.equal(h.s.record.reading_difficulty.amendments.length,3);
  assert.deepEqual(h.s.record.reading_difficulty.amendments.map(a=>[a.from,a.to]),[
    [P.difficulty[0],P.difficulty[1]],[P.difficulty[1],P.difficulty[2]],[P.difficulty[2],P.difficulty[0]]]);
  h.act('complete',{});h.act('complete',{});h.act('complete',{});done(h);
  assert.equal(JSON.stringify(h.rows[0]),original);
  assert.equal(h.rows[1].supersedes_revision,1);
  assert.deepEqual(h.s.record.first_impression,first);
  assert.deepEqual(h.s.record.unsure_sources['读着费劲'],['manual']);
  assert.equal(h.s.record.judgment,'pass');
});
test('revisiting difficulty without changing the choice does not invent an amendment',()=>{
  const h=setup();core(h);h.act('reopen',{step:1});h.act('complete',{});
  assert.equal(h.s.record.reading_difficulty.amendments.length,0);
  assert.equal(h.s.record.reading_difficulty.original_choice,P.difficulty[0]);
});

test("navigation preserves progress, completed record and first-pass access gates", () => {
  const h = setup();
  assert.throws(() => h.act("navigate", {step:1}), /已开放/);
  assert.throws(() => h.act("submit"), /顺序/);
  h.act("complete", {judgment:"pass"});
  h.act("complete", {choice:P.difficulty[0]});
  const before = structuredClone(h.s.record);
  h.act("navigate", {step:1});
  assert.equal(h.s.stage, 2);
  assert.equal(h.s.viewStep, 1);
  assert.equal(h.s.maxUnlockedStage, 2);
  h.act("save", {choice:P.difficulty[0], paraphrase:"", rewrite:"", manual_unsure:false});
  h.act("navigate", {step:2});
  assert.deepEqual(h.s.record, before);
  assert.deepEqual(h.s.dirtySteps, []);
  assert.throws(() => h.act("navigate", {step:3}), /已开放/);
  h.act("navigate", {step:0});
  assert.throws(() => h.act("save", {judgment:"fail"}), /锁定/);
  assert.throws(() => h.act("save", {manual_unsure:true}), /锁定/);
});

test("submitted browsing and unchanged saves do not create another revision", () => {
  const h = setup(); core(h); done(h);
  const before = structuredClone(h.s.record);
  assert.equal(h.s.viewStep, 7);
  assert.throws(() => h.act("submit"), /已提交/);
  h.act("navigate", {step:1});
  h.act("save", {choice:P.difficulty[0]});
  h.act("complete", {choice:P.difficulty[0]});
  assert.equal(h.s.viewStep, 2);
  assert.equal(h.s.stage, 7);
  assert.deepEqual(h.s.record, before);
  assert.deepEqual(h.s.dirtySteps, []);
  h.act("navigate", {step:6});
  assert.throws(() => h.act("submit"), /顺序/);
  assert.equal(h.rows.length, 1);
});

test("completed steps can be edited then reviewed once without replaying unchanged later steps", () => {
  const h = setup(); core(h); done(h);
  const original = structuredClone(h.rows[0]);
  h.act("navigate", {step:1});
  h.act("save", {choice:P.difficulty[1]});
  assert.equal(h.s.stage, 6);
  assert.equal(h.s.viewStep, 1);
  assert.equal(h.s.maxUnlockedStage, 6);
  assert.deepEqual(h.s.dirtySteps, [1,5,6]);
  assert.equal(h.s.record.review_completed, false);
  assert.deepEqual(h.s.record.steps.n1, original.steps.n1);
  h.act("navigate", {step:4});
  h.act("save", {needs_verification:false});
  h.act("navigate", {step:6});
  const r = h.act("submit").record;
  assert.equal(r.judgment, "fail");
  assert.ok(!("tags" in r));
  assert.equal(r.supersedes_revision, 1);
  assert.deepEqual(r.first_impression, original.first_impression);
  assert.deepEqual(r.steps.n1, original.steps.n1);
  assert.deepEqual(r.steps.spoiler, original.steps.spoiler);
  assert.equal(r.steps.reading_difficulty.started_at, original.steps.reading_difficulty.started_at);
  assert.ok(r.steps.reading_difficulty.active_ms > original.steps.reading_difficulty.active_ms);
  assert.deepEqual(h.rows[0], original);
  assert.deepEqual(h.s.dirtySteps, []);
  assert.equal(h.s.viewStep, 7);
});

test("final review validates unfinished conditional edits and identifies the failing step", () => {
  const h = setup(); core(h); done(h);
  h.act("navigate", {step:2});
  h.act("save", {n1:{following_text_use:"没用到", judgment:"pass", writing_style:"其他写法"}});
  h.act("complete"); // Already-open steps remain navigable with an incomplete draft.
  assert.equal(h.s.viewStep, 3);
  h.act("navigate", {step:6});
  assert.throws(() => h.act("submit"), error => error.step === 2 && /说明/.test(error.message));
  assert.equal(h.rows.length, 1);
  h.act("navigate", {step:2});
  h.act("save", {n1:{following_text_use:"没用到", judgment:"pass", writing_style:"其他写法", other_writing_explanation:"写法及增量"}});
  h.act("navigate", {step:6});
  assert.equal(h.act("submit").record.revision, 2);
});

test("final review requires uncovered reason after edits and clears pass-only fields", () => {
  const h = setup(); core(h); h.act("complete");
  h.act("submit", {tags:["冗余"], star:true});
  h.act("navigate", {step:3});
  h.act("save", {rubric_uncovered:true});
  assert.equal(h.s.record.star, false);
  assert.ok(!("tags" in h.s.record));
  h.act("navigate", {step:6});
  assert.throws(() => h.act("submit"), error => error.step === 6 && /原因/.test(error.message));
  h.act("save", {uncovered_reason:"未覆盖的情况"});
  const r = h.act("submit").record;
  assert.equal(r.judgment, "fail");
  assert.ok(!("tags" in r));
  assert.equal(r.star, false);
});

test("difficulty edits retain the original and continuous transitions with separate uncertainty sources", () => {
  const h = setup(); core(h); done(h);
  h.act("navigate", {step:1});
  h.act("save", {choice:P.difficulty[1]});
  h.act("save", {choice:P.difficulty[2], manual_unsure:true});
  assert.deepEqual(h.s.record.unsure_sources.读着费劲, ["automatic","manual"]);
  h.act("save", {choice:P.difficulty[0]});
  h.act("navigate", {step:6});
  const r = h.act("submit").record;
  assert.equal(r.reading_difficulty.original_choice, P.difficulty[0]);
  assert.deepEqual(r.reading_difficulty.amendments.map(a => [a.from,a.to]), [
    [P.difficulty[0],P.difficulty[1]], [P.difficulty[1],P.difficulty[2]], [P.difficulty[2],P.difficulty[0]],
  ]);
  assert.equal(r.judgment, "pass");
  assert.deepEqual(r.unsure_sources.读着费劲, ["manual"]);
});

test("automatic anchor tag clears with its cause while manual and unknown legacy tags survive", () => {
  const early = {following_text_use:"挂早了", judgment:"pass", writing_style:"补充"};
  const plain = {...early, following_text_use:"没用到"};
  const h = setup(); core(h, P.difficulty[0], early); done(h);
  assert.deepEqual(h.s.anchorTagSources, ["automatic"]);
  h.act("navigate", {step:2}); h.act("save", {n1:plain});
  assert.deepEqual(h.s.record.tags, []);
  h.act("navigate", {step:6}); h.act("save", {tags:["锚点问题"]});
  assert.deepEqual(h.s.anchorTagSources, ["manual"]);
  h.act("navigate", {step:2}); h.act("save", {n1:early});
  h.act("save", {n1:plain});
  assert.deepEqual(h.s.record.tags, ["锚点问题"]);
  h.act("navigate", {step:6}); h.act("submit");
  const legacy = {version:1, stage:7, record:structuredClone(h.s.record)};
  let migrated = P.normalizeDraft(legacy);
  assert.deepEqual(migrated.anchorTagSources, ["legacy"]);
  migrated = P.transition(migrated, "navigate", {step:2}, 1, form, c);
  migrated = P.transition(migrated, "save", {n1:early}, 1, form, c);
  migrated = P.transition(migrated, "save", {n1:plain}, 1, form, c);
  assert.deepEqual(migrated.record.tags, ["锚点问题"]);
  assert.ok(!("anchorTagSources" in h.s.record));
});

test("normalization migrates old drafts without mutating rows or draft-only UI data", () => {
  const h = setup(); core(h); done(h);
  const legacy = {version:12, stage:7, record:structuredClone(h.s.record), ui:{branchDrafts:{n1:{note:"draft"}}}};
  const before = structuredClone(legacy);
  const migrated = P.normalizeDraft(legacy);
  assert.equal(migrated.viewStep, 7);
  assert.equal(migrated.maxUnlockedStage, 6);
  assert.deepEqual(migrated.dirtySteps, []);
  assert.deepEqual(migrated.ui, legacy.ui);
  assert.deepEqual(legacy, before);
  const opened = P.transition({...migrated, viewStep:1}, "open", {}, 2, form, c);
  assert.equal(opened.viewStep, 1);
  assert.deepEqual(opened.record, before.record);
  assert.deepEqual(opened.ui, legacy.ui);
  const reopened = structuredClone(legacy);
  reopened.stage = 1;
  for (const key of P.steps.slice(1)) delete reopened.record.steps[key].completed_at;
  assert.equal(P.normalizeDraft(reopened).maxUnlockedStage, 6);
});

test("new revisions change tool version without changing the journal schema or legacy validity", () => {
  const h = setup(); core(h); done(h);
  const old = structuredClone(h.s.record);
  old.annotator_version = "q1-annotator/3.4";
  P.validate(old, form);
  h.act("navigate", {step:5}); h.act("save", {reason:"补充理由"});
  h.act("navigate", {step:6});
  const r = h.act("submit").record;
  assert.equal(r.annotator_version, "q1-annotator/3.5");
  assert.equal(r.schema, old.schema);
  for (const key of ["viewStep","maxUnlockedStage","dirtySteps","pendingActiveMs","anchorTagSources","ui"])
    assert.ok(!(key in r));
});

test("viewing following text after submission appends exposure in the next confirmed revision", () => {
  const h = setup(); core(h); done(h);
  const original = structuredClone(h.rows[0]);
  h.act("navigate", {step:2}); h.act("following", {scope:"within_unit"});
  assert.equal(h.s.stage, 6);
  assert.deepEqual(h.s.dirtySteps, [2]);
  h.act("navigate", {step:6});
  const r = h.act("submit").record;
  assert.equal(r.steps.n1.viewed_following_text, true);
  assert.equal(r.steps.n1.following_text_views.length, 1);
  assert.deepEqual(r.steps.spoiler, original.steps.spoiler);
  assert.deepEqual(h.rows[0], original);
});

test("legacy reopened drafts can confirm the missing suffix at final review only after all steps were opened", () => {
  const h = setup(); core(h); done(h);
  const original = structuredClone(h.rows[0]);
  h.act("reopen", {step:1});
  assert.equal(h.s.stage, 1);
  assert.equal(h.s.maxUnlockedStage, 6);
  assert.equal(h.s.record.steps.n1.completed_at, undefined);
  h.act("navigate", {step:6});
  const r = h.act("submit").record;
  assert.equal(r.revision, 2);
  for (const key of P.steps.slice(1)) {
    assert.ok(r.steps[key].completed_at);
    assert.equal(r.steps[key].started_at, original.steps[key].started_at);
  }
  assert.deepEqual(r.steps.first_impression, original.steps.first_impression);
  const early = setup(); core(early);
  early.act("reopen", {step:1});
  assert.equal(early.s.maxUnlockedStage, 5);
  assert.throws(() => early.act("navigate", {step:6}), /已开放/);
  early.act("navigate", {step:5});
  assert.throws(() => early.act("submit"), /顺序/);
});

test("first original-note exposure from the submitted summary returns to final confirmation", () => {
  for (const difficulty of [P.difficulty[0], P.difficulty[1]]) {
    const h = setup(); core(h, difficulty); done(h);
    const original = structuredClone(h.rows[0]);
    assert.equal(h.s.viewStep, 7);
    h.act("notes");
    assert.equal(h.s.stage, 6);
    assert.equal(h.s.viewStep, 6);
    assert.deepEqual(h.s.dirtySteps, [6]);
    assert.equal(h.s.record.review_completed, false);
    assert.equal(h.s.record.context.viewed_original_notes, true);
    assert.equal(h.rows.length, 1);
    const r = h.act("submit").record;
    assert.equal(r.supersedes_revision, 1);
    assert.equal(r.context.viewed_original_notes, true);
    assert.deepEqual(h.rows[0], original);
    const submitted = structuredClone(h.s.record);
    h.act("notes");
    assert.equal(h.s.viewStep, 7);
    assert.deepEqual(h.s.dirtySteps, []);
    assert.deepEqual(h.s.record, submitted);
  }
});
