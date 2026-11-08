// Run the actual single-file annotator storage code with controllable I/O receipts.
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const vm = require("node:vm");
const html = readFileSync(__dirname + "/q1-annotator.html", "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const storage = script.slice(0, script.indexOf("    function record("));
function harness() {
  const nodes = new Map();
  const get = (id) => {
    if (!nodes.has(id))
      nodes.set(id, {
        textContent: "",
        hidden: false,
        classList: { toggle() {} },
        replaceChildren() {},
      });
    return nodes.get(id);
  };
  const c = vm.createContext({
    document: { getElementById: get },
    window: { showOpenFilePicker() {} },
    structuredClone,
    TextEncoder,
    crypto: require("node:crypto").webcrypto,
    setTimeout,
    clearTimeout,
    queueMicrotask,
    console,
  });
  vm.runInContext(
    storage +
      "\nfunction editStatus() {}\nfunction render() {}\nfunction flushEdits() {}\nfunction recoverDrafts() {}\nlet editTimer; function queueEdits() {}",
    c,
  );
  vm.runInContext(
    `
    var batch = {batch_id:'b', units:[{unit_id:'u',marginalia:[{marginalia_id:'m'}]}]};
    var state = {ui:0,mi:0,rows:[],drafts:{},missDrafts:{},unitNoteDrafts:{}};
    var disk = '', permission = 'granted', writes = 0, failWrite = false, afterLock;
    var handle = { name:'judgments.jsonl', queryPermission:async()=>permission, requestPermission:async()=>permission,
      getFile:async()=>({text:async()=>disk,size:BufferSize(disk)}),
      createWritable:async()=>{ writes++; if(failWrite) throw Error('disk failure');
        if(afterLock) afterLock(); let suffix=''; return {seek:async()=>{},write:async data=>{suffix=data},
          close:async()=>{if(gate) await gate; disk+=suffix},abort:async()=>{}}; }};
    var gate = null;
    dbPut = async()=>{};
    session = makeSession(batch,state,handle);
  `,
    c,
  );
  c.BufferSize = (s) => Buffer.byteLength(s);
  const run = (code) => vm.runInContext(code, c);
  const row = (i, reason = "  original\n text  ") => ({
    batch_id: "b",
    unit_id: "u",
    record_type: "marginalia",
    record_id: "m",
    revision: i,
    annotator_version: "q1-annotator/1.0",
    source_range: {
      start: { chapter_id: 1, paragraph_index: 1, char_offset: 0 },
      end: { chapter_id: 1, paragraph_index: 1, char_offset: 1 },
    },
    original_source_range: {
      start: { chapter_id: 1, paragraph_index: 1, char_offset: 0 },
      end: { chapter_id: 1, paragraph_index: 1, char_offset: 1 },
    },
    judgment: "pass",
    remarks: "",
    star: false,
    needs_verification: false,
    reason,
  });
  return { c, run, row, get };
}
test("new judgments carry rubric and human identity without rewriting legacy rows", async () => {
  const h = harness();
  const recordCode = script.slice(script.indexOf("    function record("), script.indexOf("    function activeMisses("));
  h.run(recordCode);
  h.c.old = h.row(1);
  h.run("state.rows.push(old)");
  h.c.span = h.row(1).source_range;
  h.run('record("marginalia", "m", {judgment:"pass", reason:"", remarks:"", star:false, needs_verification:false}, span, span)');
  await h.run("session.writes");
  assert.equal(h.run("state.rows[1].rubric_version"), "open_coding");
  assert.equal(h.run("state.rows[1].annotator_id"), "weijiang");
  assert.equal(h.run("state.rows[0].rubric_version"), undefined);
  assert.equal(h.run('parseJournal(state.rows.map(r=>JSON.stringify(r)+"\\n").join(""),batch).length'), 2);
});
test("published rubric context requires a content hash; draft context is rejected", () => {
  const h = harness();
  assert.throws(() => h.run('annotationContext({batch_id:"b",annotator_id:"weijiang",rubric_version:"q1-v0",rubric_status:"draft"},"b")'));
  assert.equal(h.run('annotationContext({batch_id:"b",annotator_id:"weijiang",rubric_version:"q1-v1",rubric_status:"published",rubric_sha256:"a".repeat(64)},"b").rubric_version'), "q1-v1");
  h.c.bad = { ...h.row(1), annotator_version:"q1-annotator/1.9" };
  assert.throws(() => h.run('parseJournal(JSON.stringify(bad)+"\\n",batch)'));
});
test("prefix reconcile: newer file imported, newer browser appended, duplicate sync is a no-op", async () => {
  const h = harness();
  h.c.row1 = h.row(1);
  h.c.row2 = h.row(2, "next");
  h.run('disk=JSON.stringify(row1)+"\\n";');
  await h.run("reconcile(session)");
  assert.equal(h.run("state.rows.length"), 1);
  h.run("state.rows.push(row2)");
  await h.run("scheduleDisk()");
  await h.run("scheduleDisk()");
  assert.equal(h.run("writes"), 1);
  assert.equal(h.run("disk"), JSON.stringify(h.row(1)) + "\n" + JSON.stringify(h.row(2, "next")) + "\n");
  assert.equal(h.get("saveState").textContent, "浏览器与文件均已保存");
});
test("fork, wrong batch, malformed and partial journals preserve both sides and block writes", async () => {
  for (const mode of ["fork", "batch", "json", "partial", "revision"]) {
    const h = harness();
    h.c.row1 = h.row(1);
    h.c.other = { ...h.row(1), reason: "different" };
    h.run("state.rows=[row1]");
    if (mode === "fork") h.run('disk=JSON.stringify(other)+"\\n"');
    if (mode === "batch") h.run('other.batch_id="other"; disk=JSON.stringify(other)+"\\n"');
    if (mode === "json") h.run('disk="{broken}\\n"');
    if (mode === "partial") h.run("disk=JSON.stringify(row1)");
    if (mode === "revision") h.run('other.revision=2;disk=JSON.stringify(other)+"\\n"');
    const before = h.run("disk");
    await h.run("scheduleDisk()");
    assert.equal(h.run("disk"), before);
    assert.equal(h.run("state.rows[0].reason"), h.row(1).reason);
    assert.equal(h.run("writes"), 0);
    assert.equal(h.run("session.blocked"), true);
    assert.match(h.get("saveState").textContent, /文件待同步/);
  }
});
test("writer lock recheck detects external replacement without appending", async () => {
  const h = harness();
  h.c.row1 = h.row(1);
  h.run('state.rows=[row1]; afterLock=()=>{disk="changed\\n"}');
  await h.run("scheduleDisk()");
  assert.equal(h.run("disk"), "changed\n");
  assert.equal(h.run("session.blocked"), true);
});
test("permission loss and write failure retain browser records; retry reconciles without duplicate rows", async () => {
  for (const mode of ["permission", "write"]) {
    const h = harness();
    h.c.row1 = h.row(1);
    h.run("state.rows=[row1]");
    h.run(mode === "permission" ? 'permission="prompt"' : "failWrite=true");
    await h.run("scheduleDisk()");
    assert.equal(h.run("disk"), "");
    assert.match(h.get("saveState").textContent, /文件待同步/);
    h.run('permission="granted";failWrite=false');
    await h.run("reconcile(session)");
    await h.run("scheduleDisk()");
    assert.equal(h.run("disk"), JSON.stringify(h.row(1)) + "\n");
  }
});
test("slow write receipt cannot acknowledge a newer revision or pending valid draft", async () => {
  const h = harness();
  h.c.row1 = h.row(1);
  h.c.row2 = h.row(2);
  h.run("var release;gate=new Promise(r=>release=r);state.rows=[row1]");
  const p = h.run("scheduleDisk()");
  await new Promise((r) => setImmediate(r));
  h.run("state.rows.push(row2)");
  const q = h.run("scheduleDisk()");
  h.run("release()");
  await p;
  assert.notEqual(h.get("saveState").textContent, "浏览器与文件均已保存");
  await q;
  assert.equal(h.get("saveState").textContent, "浏览器与文件均已保存");
  h.run('state.drafts.m={judgment:"pass",reason:"new"};updateSaveStatus()');
  assert.match(h.get("saveState").textContent, /同步中/);
  h.run('state.drafts.m={judgment:"fail",reason:"  "};updateSaveStatus()');
  assert.equal(h.get("saveState").textContent, "浏览器与文件均已保存");
});
test("browser receipts: pending, failure, retry, and stale receipt cannot claim success", async () => {
  const h = harness();
  h.run("session.diskAck=0;var receipts=[];dbPut=()=>new Promise((ok,no)=>receipts.push({ok,no}))");
  const p = h.run("persist()");
  const q = h.run("persist()");
  h.run("receipts[0].ok()");
  await p;
  assert.equal(h.get("saveState").textContent, "浏览器保存中");
  h.run('receipts[1].no(Error("quota"))');
  await q;
  assert.match(h.get("saveState").textContent, /浏览器保存失败/);
  assert.equal(h.get("retryBrowser").hidden, false);
  const r = h.run("persist()");
  h.run("receipts[2].ok()");
  await r;
  assert.equal(h.get("saveState").textContent, "浏览器与文件均已保存");
});
test("folder cancellation, denial and invalid batch leave current session and last selection untouched", async () => {
  for (const mode of ["cancel", "denied", "invalid"]) {
    const h = harness();
    h.run(
      "var before=session;var created=false;var committed=false;dbSaveSession=async()=>{committed=true}",
    );
    h.c.showDirectoryPicker = async () => {
      if (mode === "cancel") throw Object.assign(Error("cancel"), { name: "AbortError" });
      return {
        requestPermission: async () => (mode === "denied" ? "denied" : "granted"),
        getFileHandle: async (name) => {
          if (name === "judgments.jsonl") {
            h.c.created = true;
            return h.c.handle;
          }
          return { getFile: async () => ({ text: async () => JSON.stringify({ schema: "bad" }) }) };
        },
      };
    };
    await h.run("openFolder()");
    assert.equal(h.run("session===before"), true);
    assert.equal(h.run("created"), false);
    assert.equal(h.run("committed"), false);
  }
});

test("valid JSON with damaged fields or coordinates is rejected without modifying history", async () => {
  for (const change of [
    (r) => {
      r.reason = {};
    },
    (r) => {
      r.source_range.start.char_offset = -1;
    },
    (r) => {
      r.judgment = "fail";
      r.reason = "  ";
    },
    (r) => {
      r.needs_verification = null;
    },
  ]) {
    const h = harness();
    const damaged = h.row(1);
    change(damaged);
    h.c.damaged = damaged;
    h.run('disk=JSON.stringify(damaged)+"\\n"');
    const before = h.run("disk");
    await h.run("scheduleDisk()");
    assert.equal(h.run("disk"), before);
    assert.equal(h.run("state.rows.length"), 0);
    assert.equal(h.run("session.blocked"), true);
  }
});

function mixedFixture() {
  const range = (lo, hi) => ({start:{chapter_id:1,paragraph_index:1,char_offset:lo},end:{chapter_id:1,paragraph_index:1,char_offset:hi}});
  const batch = {schema:"q1-mixed/1",synthetic:true,windows:[{
    window_id:"11111111-1111-4111-8111-111111111111",book:"合成",author:null,chapter_title:null,
    original_source_range:range(0,4),paragraphs:[{index:1,offset:0,text:"甲乙丙丁",href:"s.xhtml"}],before:[],after:["戊己"],
    marginalia:[{marginalia_id:"22222222-2222-4222-8222-222222222222",type:"N",body_text:"合成旁注",source_quote:"丙丁戊",original_source_range:range(2,5),crosses_boundary:true}],
  }]};
  const sort = v => Array.isArray(v) ? v.map(sort) : v && typeof v === "object" ? Object.fromEntries(Object.keys(v).sort().map(k=>[k,sort(v[k])])) : v;
  batch.batch_id = require("node:crypto").createHash("sha256").update(JSON.stringify(sort(batch))).digest("hex");
  return batch;
}

test("blind projection rejects hidden provenance, duplicate IDs and wrong start-owner assignments", async () => {
  const h = harness();
  h.c.blind = mixedFixture();
  await h.run("checkBatch(blind)");
  for (const mutate of [
    b=>b.model="secret", b=>b.windows[0].marginalia[0].group="secret",
    b=>b.windows[0].marginalia.push({...b.windows[0].marginalia[0]}),
    b=>b.windows[0].marginalia[0].original_source_range.start.char_offset=4,
    b=>b.windows[0].marginalia[0].crosses_boundary=false,
  ]) {
    const b=mixedFixture(); mutate(b); h.c.blind=b;
    await assert.rejects(h.run("checkBatch(blind)"));
  }
});

test("mixed records append no group identity and reject reveal/density/provenance rows", async () => {
  const h=harness(); h.c.blind=mixedFixture();
  h.run("session=makeSession(blind,state,handle);batch=blind;");
  h.run(script.slice(script.indexOf("    function record("),script.indexOf("    function activeMisses(")));
  h.run('var mark=blind.windows[0].marginalia[0];record("marginalia",mark.marginalia_id,{marginalia_id:mark.marginalia_id,type:mark.type,source_quote:mark.source_quote,body_text:mark.body_text,judgment:"pass",reason:"",remarks:"",star:false,needs_verification:false},mark.original_source_range,mark.original_source_range)');
  await h.run("session.writes");
  const r=JSON.parse(h.run("JSON.stringify(state.rows[0])"));
  assert.equal(r.annotator_version,"q1-annotator/2.1");
  h.c.older={...r,annotator_version:"q1-annotator/2.0"};
  assert.equal(h.run('parseJournal(JSON.stringify(older)+"\\n",batch).length'),1);
  assert.equal(r.view,"mixed"); assert.equal(r.comparison_batch_id,h.c.blind.batch_id);
  for(const k of ["run_id","reading_id","unit_id","group","model","source_range"]) assert.equal(r[k],undefined);
  assert.equal(h.run('parseJournal(disk,batch).length'),1);
  for(const changes of [{run_id:"leak"},{record_type:"reveal"},{record_type:"density"},{window_id:"wrong"}]) {
    h.c.bad={...r,...changes};
    assert.throws(()=>h.run('parseJournal(JSON.stringify(bad)+"\\n",batch)'));
  }
});

test("mixed completion needs judgments, not density; browser restores windows and order", async () => {
  const h=harness();h.c.blind=mixedFixture();h.run('session=makeSession(blind,state,handle)');
  h.run(script.slice(script.indexOf("    function activeMisses("),script.indexOf("    function progress(")));
  assert.deepEqual(Array.from(h.run('unitStatus(unit()).missing')),["剩 1 条未完成"]);
  h.run('state.drafts[unit().marginalia[0].marginalia_id]={judgment:"pass",reason:""}');
  assert.equal(h.run('unitStatus(unit()).state'),"done");
});

test("folder import reads mixed projection without opening private batch or mapping", async () => {
  const h=harness();h.c.blind=mixedFixture();h.run('var reads=[];dbGet=async()=>undefined;settleCurrent=async()=>{};dbSaveSession=async()=>{};installSession=async s=>{session=s}');
  h.c.showDirectoryPicker=async()=>({requestPermission:async()=>"granted",getFileHandle:async name=>{
    h.c.reads.push(name);
    if(name==="mixed.json") return {getFile:async()=>({text:async()=>JSON.stringify(h.c.blind)})};
    if(name==="judgments.jsonl") return h.c.handle;
    if(name==="annotation-context.json") throw Object.assign(Error("missing"),{name:"NotFoundError"});
    throw Error("private file was accessed");
  }});
  await h.run("openFolder()");
  assert.equal(h.run('session.batch.schema'),"q1-mixed/1");
  assert.deepEqual(Array.from(h.c.reads),["mixed.json","judgments.jsonl","annotation-context.json"]);
});
