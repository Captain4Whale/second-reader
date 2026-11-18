const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const {spawnSync} = require('node:child_process');
const P = require('./q1-note-protocol.js');
const form = JSON.parse(fs.readFileSync(__dirname+'/../rubric/q1-v3.4.form.v2.json'));
const legacyForm = JSON.parse(fs.readFileSync(__dirname+'/../rubric/q1-v3.4.form.v1.json'));
const pos={chapter_id:1,paragraph_index:1,char_offset:0};
const range={start:pos,end:{...pos,char_offset:1}};
const c={record_id:'r',window_id:'w',unit_key:'w',book_key:'b',body_text:'批注',source_quote:'文',original_source_range:range,
  context:{observer_cutoff:range.end,original_notes:{status:'unresolved',items:[]},within_unit:[{range,text:'后文'}],after_unit:[]}};
const m={record_ids:['r'],randomization:{seed:7},context_sha256:'x',rubric_form_version:form.form_version,rubric_form_sha256:'v2hash',
 review_session_id:'synthetic-protocol-test',session_purpose:'test',batch_id:'synthetic',annotator_id:'test',rubric_version:form.rubric_version,
 rubric_sha256:form.rubric_sha256,annotation_guide_sha256:form.annotation_guide_sha256};
const plain={following_text_use:'没用到',judgment:'pass',writing_style:'补充'};
const first={first_pass:P.firstPass[0],paraphrase:'第一次复述',rewrite_judgment:null,rewrite_text:''};
const difficult={first_pass:P.firstPass[1],paraphrase:'第一遍没说对',rewrite_judgment:P.rewriteChoices[0],rewrite_text:'更直白'};
function setup(state,rows=[],options={}){
 let s=state||P.initial(c,m,'h');
 options={identity:{rubric_form_version:form.form_version,rubric_form_sha256:'v2hash'},...options};
 return {get s(){return s;},rows,act(action,values={},ms=1){
   s=P.transition(s,action,values,ms,form,c,rows,options);
   if(action==='submit') rows.push(structuredClone(s.record));
   return s;
 }};
}
function core(h,d=first,n1=plain){
 h.act('complete',{judgment:'pass'});h.act('complete',d);h.act('complete',{n1});
 h.act('complete',{spoiler:false});h.act('complete',{incorrect_information:false,needs_verification:true});
}
function done(h,values={}){h.act('complete');return h.act('submit',values).record;}
function legacy(choice=P.difficulty[0],original=choice){
 const h=setup();core(h);const r=done(h);
 for(const key of ['event_schema_version','checks','acknowledged_warnings','legacy_inferences'])delete r[key];
 r.annotator_version='q1-annotator/3.5';r.event_version=100;r.rubric_form_version=legacyForm.form_version;r.rubric_form_sha256='v1hash';
 r.reading_difficulty={original_choice:original,choice,veto:choice===P.difficulty[1],paraphrase:'历史第一遍',rewrite:'历史改写文本',amendments:original===choice?[]:[{from:original,to:choice,at:r.timestamp,reason:'历史修改',active_ms:1}]};
 P.derive(r);if(r.judgment==='fail')r.steps.tags={status:'skipped_due_to_fail'};
 P.validate(r,legacyForm);
 return r;
}
function fromRow(row){return {version:row.event_version,stage:7,record:structuredClone(row)};}

test('new records use explicit observations, null checks and the version-two event range',()=>{
 const h=setup();assert.equal(h.s.version,P.eventVersionBase);assert.equal(h.s.record.event_schema_version,2);
 assert.equal(h.s.record.annotator_version,'q1-annotator/3.6');assert.deepEqual(h.s.record.checks,{spoiler:null,incorrect_information:null});
 assert.equal(h.s.record.reading_difficulty.first_pass,null);assert.equal(h.s.record.reading_difficulty.rewrite_judgment,null);
 assert.equal(h.s.record.judgment,null);assert.deepEqual(h.s.record.legacy_inferences,[]);
});
test('first pass and paraphrase lock on continue; rewrite and its text remain editable',()=>{
 const h=setup();h.act('complete',{judgment:'pass'});
 assert.throws(()=>h.act('complete'),/第一遍/);
 h.act('save',{first_pass:P.firstPass[1],paraphrase:'初次'});
 assert.throws(()=>h.act('complete'),/改写/);
 h.act('complete',{rewrite_judgment:P.rewriteChoices[0],rewrite_text:'改写'});
 const locked=h.s.record.reading_difficulty.locked_at;h.act('navigate',{step:1});
 assert.throws(()=>h.act('save',{first_pass:P.firstPass[0]}),/锁定/);
 assert.throws(()=>h.act('save',{paraphrase:'重写第一次'}),/锁定/);
 h.act('save',{rewrite_judgment:P.rewriteChoices[1],rewrite_text:'新的改写'});
 assert.equal(h.s.record.reading_difficulty.locked_at,locked);
 assert.equal(h.s.record.reading_difficulty.paraphrase,'初次');assert.equal(h.s.record.reading_difficulty.rewrite_text,'新的改写');
 assert.deepEqual(h.s.record.reading_difficulty.amendments.map(a=>[a.from,a.to]),[[P.rewriteChoices[0],P.rewriteChoices[1]]]);
});
test('can paraphrase forbids a contradictory rewrite and has no default rewrite choice',()=>{
 const h=setup();h.act('complete',{judgment:'pass'});
 assert.throws(()=>h.act('save',{first_pass:P.firstPass[0],rewrite_judgment:P.rewriteChoices[0]}),/不需要/);
 h.act('complete',first);assert.equal(h.s.record.reading_difficulty.rewrite_judgment,null);
 h.act('navigate',{step:1});assert.throws(()=>h.act('save',{rewrite_judgment:P.rewriteChoices[0]}),/不需要/);
});
test('final rewrite drives veto and automatic uncertainty with a continuous change history',()=>{
 const h=setup();core(h,difficult);h.act('navigate',{step:1});
 assert.equal(h.s.record.judgment,'fail');
 h.act('save',{rewrite_judgment:P.rewriteChoices[1],manual_unsure:true});
 assert.deepEqual(h.s.record.unsure_sources.读着费劲,['automatic','manual']);assert.equal(h.s.record.judgment,'pass');
 h.act('save',{rewrite_judgment:P.rewriteChoices[0]});assert.deepEqual(h.s.record.unsure_sources.读着费劲,['manual']);
 h.act('save',{rewrite_judgment:P.rewriteChoices[1]});h.act('save',{rewrite_judgment:P.rewriteChoices[1]});
 assert.equal(h.s.record.reading_difficulty.amendments.length,3);
 h.act('navigate',{step:5});const r=done(h);assert.equal(r.judgment,'pass');assert.equal(r.reading_difficulty.veto,false);
});
test('first impression remains immutable before and during discussion',()=>{
 const h=setup();core(h);h.act('navigate',{step:0});assert.throws(()=>h.act('save',{judgment:'fail'}),/锁定/);
 h.act('navigate',{step:5});done(h);h.act('begin_discussion');h.act('navigate',{step:0});assert.throws(()=>h.act('save',{judgment:'fail'}),/锁定/);
});
test('both veto checks require explicit yes or no even when N1 failed',()=>{
 const h=setup();h.act('complete',{judgment:'pass'});h.act('complete',first);
 h.act('complete',{n1:{following_text_use:'没用到',judgment:'fail',failure_types:['没新东西']}});
 assert.throws(()=>h.act('complete'),/剧透/);assert.equal(h.s.record.checks.spoiler,null);
 h.act('complete',{spoiler:false});assert.throws(()=>h.act('complete'),/错误信息/);
 h.act('complete',{incorrect_information:false});const r=done(h);
 assert.equal(r.judgment,'fail');assert.deepEqual(r.checks,{spoiler:false,incorrect_information:false});assert.ok(!('tags'in r));
});
test('unanswered checks do not display an automatic pass',()=>{
 const h=setup();h.act('complete',{judgment:'pass'});h.act('complete',first);h.act('complete',{n1:plain});
 assert.equal(h.s.record.judgment,null);h.act('complete',{spoiler:false});assert.equal(h.s.record.judgment,null);
 h.act('complete',{incorrect_information:false});assert.equal(h.s.record.judgment,'pass');
});
test('navigation and unchanged saves preserve prior completion times',()=>{
 const h=setup();core(h);const r=structuredClone(h.s.record);
 h.act('navigate',{step:1});h.act('save',{rewrite_text:'',first_pass:first.first_pass,paraphrase:first.paraphrase,rewrite_judgment:null});
 h.act('navigate',{step:4});assert.deepEqual(h.s.record,r);assert.equal(h.s.stage,5);
 assert.throws(()=>h.act('navigate',{step:6}),/已开放/);
 h.act('navigate',{step:2});h.act('save',{n1:{...plain,writing_style:'联想'}});h.act('navigate',{step:5});done(h);
 assert.deepEqual(h.s.record.steps.spoiler,r.steps.spoiler);assert.deepEqual(h.s.record.steps.incorrect_information,r.steps.incorrect_information);
});
test('submitted rows are wholly read-only and contextual browsing creates no amendment or exposure',()=>{
 const h=setup();core(h);done(h);const original=structuredClone(h.s.record);
 h.act('notes');h.act('navigate',{step:2});h.act('following',{scope:'within_unit'});
 for(const action of ['save','complete','submit','reopen','amend'])assert.throws(()=>h.act(action),/只读/);
 h.act('navigate',{step:4});h.act('open');assert.deepEqual(h.s.record,original);assert.equal(h.rows.length,1);assert.deepEqual(h.s.dirtySteps,[]);
});
test('only explicit discussion with a nonempty reason can append a revision',()=>{
 const h=setup();assert.throws(()=>h.act('begin_discussion'),/提交后/);core(h);done(h);
 const original=structuredClone(h.rows[0]);h.act('begin_discussion');assert.equal(h.s.discussion,true);assert.equal(h.s.viewStep,6);
 assert.throws(()=>h.act('submit'),/原因/);h.act('save',{amendment_reason:'  '});assert.throws(()=>h.act('submit'),/原因/);
 h.act('navigate',{step:3});h.act('save',{spoiler:true});h.act('navigate',{step:6});
 const r=h.act('submit',{amendment_reason:'讨论后发现剧透'}).record;
 assert.equal(r.amendment_kind,'post_discussion');assert.equal(r.supersedes_revision,1);assert.ok(r.event_version>original.event_version);
 assert.equal(r.judgment,'fail');assert.equal(h.s.discussion,false);assert.deepEqual(h.rows[0],original);
});
test('discussion preserves first-pass fields and rewrite amendments across later revisions',()=>{
 const h=setup();core(h,{...difficult,rewrite_judgment:P.rewriteChoices[1]});done(h);const initial=structuredClone(h.s.record.reading_difficulty);
 h.act('begin_discussion');h.act('navigate',{step:1});
 assert.throws(()=>h.act('save',{paraphrase:'重新作第一遍'}),/锁定/);
 h.act('save',{rewrite_judgment:P.rewriteChoices[0]});h.act('navigate',{step:6});h.act('submit',{amendment_reason:'讨论'});
 for(const key of ['first_pass','paraphrase','locked_at'])assert.equal(h.s.record.reading_difficulty[key],initial[key]);
 assert.equal(h.s.record.reading_difficulty.amendments.length,1);
});
for(const following of ['没用到','更远后文，转第四步判剧透'])test('N1 immediate-following failure cannot contradict branch '+following,()=>{
 assert.throws(()=>P.n1valid({following_text_use:following,judgment:'fail',failure_types:['下文马上讲了']},form),/紧接着几段或挂早了/);
});
for(const following of ['紧接着几段','挂早了'])test('N1 immediate-following failure accepts appropriate branch '+following,()=>{
 P.n1valid({following_text_use:following,judgment:'fail',failure_types:['下文马上讲了']},form);
});
test('far following without spoilers requires one acknowledgement and persists it',()=>{
 const h=setup();core(h,first,{...plain,following_text_use:'更远后文，转第四步判剧透'});h.act('complete');
 assert.throws(()=>h.act('submit'),e=>e.code==='ACKNOWLEDGEMENT_REQUIRED'&&e.step===6&&e.warning===P.farWarning);
 assert.equal(h.rows.length,0);const r=h.act('submit',{acknowledge_far_following:true}).record;
 assert.deepEqual(r.acknowledged_warnings,[P.farWarning]);
 h.act('begin_discussion');h.act('submit',{amendment_reason:'确认保留'});assert.equal(h.rows.length,2);
});
test('acknowledgement expires when its combination changes and must be confirmed again',()=>{
 const h=setup();core(h,first,{...plain,following_text_use:'更远后文，转第四步判剧透'});done(h,{acknowledge_far_following:true});
 h.act('begin_discussion');h.act('navigate',{step:3});h.act('save',{spoiler:true});assert.deepEqual(h.s.record.acknowledged_warnings,[]);
 h.act('save',{spoiler:false});h.act('navigate',{step:6});h.act('save',{amendment_reason:'重新判断'});
 assert.throws(()=>h.act('submit'),/需要确认/);
});
test('conditional N1 explanations and uncovered explanations are validated at final review',()=>{
 for(const n1 of [{...plain,writing_style:'其他写法'},{following_text_use:'没用到',judgment:'fail',failure_types:['其他']}]){
  const h=setup();core(h);h.act('navigate',{step:2});h.act('save',{n1});h.act('navigate',{step:5});h.act('complete');
  assert.throws(()=>h.act('submit'),e=>e.step===2&&/说明/.test(e.message));
 }
 const h=setup();core(h);h.act('complete');h.act('save',{rubric_uncovered:true});assert.ok(!('tags'in h.s.record));
 assert.throws(()=>h.act('submit'),/原因/);h.act('submit',{uncovered_reason:'缺口'});
 assert.equal(h.s.record.judgment,'fail');assert.equal(h.s.record.star,false);
});
test('known automatic anchors clear with their cause while manual anchors survive',()=>{
 const h=setup();core(h,first,{...plain,following_text_use:'挂早了'});assert.deepEqual(h.s.record.tags,['锚点问题']);
 h.act('navigate',{step:2});h.act('save',{n1:plain});assert.deepEqual(h.s.record.tags,[]);
 h.act('navigate',{step:5});h.act('complete');h.act('save',{tags:['锚点问题']});
 h.act('navigate',{step:2});h.act('save',{n1:{...plain,following_text_use:'挂早了'}});h.act('save',{n1:plain});assert.deepEqual(h.s.record.tags,['锚点问题']);
});
test('legacy submitted rows validate and remain byte-identical during read-only browsing',()=>{
 const row=legacy();const h=setup(fromRow(row),[row]);const before=JSON.stringify(row);
 h.act('open');h.act('navigate',{step:2});h.act('following',{scope:'within_unit'});h.act('notes');
 assert.equal(JSON.stringify(h.s.record),before);assert.equal(h.s.record.event_schema_version,undefined);assert.equal(h.s.record.event_version,100);
 assert.throws(()=>h.act('save',{n1:plain}),/只读/);
});
test('legacy unsubmitted drafts infer completed checks, preserve unknown checks, and upgrade identity',()=>{
 const row=legacy(P.difficulty[1]);delete row.revision;delete row.supersedes_revision;row.review_completed=false;
 delete row.steps.incorrect_information.completed_at;row.steps.tags={};
 const state={version:19,stage:4,record:row};const before=structuredClone(state);
 const d=P.normalizeDraft(state,{identity:{rubric_form_version:form.form_version,rubric_form_sha256:'v2hash'}});
 assert.deepEqual(state,before);assert.equal(d.version,P.eventVersionBase);assert.equal(d.record.event_schema_version,2);
 assert.deepEqual(d.record.checks,{spoiler:false,incorrect_information:null});assert.equal(d.record.rubric_form_sha256,'v2hash');
 assert.deepEqual(d.record.legacy_reading_difficulty,row.reading_difficulty);assert.ok(d.record.legacy_inferences.some(x=>x.includes('未判')));
 assert.equal(d.record.reading_difficulty.first_pass,P.firstPass[1]);assert.equal(d.record.reading_difficulty.rewrite_judgment,P.rewriteChoices[0]);
});
test('legacy unfinished positive checks retain the annotators explicit selection',()=>{
 const row=legacy();delete row.revision;row.review_completed=false;
 for(const key of ['spoiler','incorrect_information']) {delete row.steps[key].completed_at;row.vetoes[key]=true;}
 const migrated=P.normalizeDraft({version:18,stage:3,record:row});
 assert.deepEqual(migrated.record.checks,{spoiler:true,incorrect_information:true});
 assert.equal(migrated.record.legacy_inferences.filter(x=>x.includes('主动勾选')).length,2);
});
test('legacy drafts with a submitted predecessor are protected until explicit discussion',()=>{
 const row=legacy();const draft=fromRow(row);draft.stage=2;draft.record.review_completed=false;delete draft.record.revision;
 draft.record.reason='尚未提交的文字';draft.record.first_impression.judgment='fail';draft.record.reading_difficulty.paraphrase='不应替换第一遍';
 const identity={rubric_form_version:form.form_version,rubric_form_sha256:'v2hash'};
 const normalized=P.normalizeDraft(draft,{submitted:row,firstSubmitted:row,identity});assert.equal(normalized.discussionRequired,true);
 assert.equal(normalized.record.event_schema_version,undefined);
 const h=setup(normalized,[structuredClone(row)],{identity});assert.throws(()=>h.act('submit'),/只读/);
 h.act('begin_discussion');assert.equal(h.s.record.reason,'尚未提交的文字');assert.equal(h.s.record.first_impression.judgment,'pass');
 assert.equal(h.s.record.reading_difficulty.paraphrase,'历史第一遍');assert.equal(h.s.record.rubric_form_version,form.form_version);
 h.act('submit',{amendment_reason:'确认旧草稿中的改动'});assert.equal(h.rows.length,2);assert.deepEqual(h.rows[0],row);
});
for(const [original,choice,firstPass,rewrite] of [[P.difficulty[0],P.difficulty[1],P.firstPass[0],null],[P.difficulty[1],P.difficulty[0],P.firstPass[1],null]])test('cross-category legacy changes preserve first observation without inventing a rewrite '+original,()=>{
 const row=legacy(choice,original);const h=setup(fromRow(row),[structuredClone(row)]);h.act('begin_discussion');
 assert.equal(h.s.record.reading_difficulty.first_pass,firstPass);assert.equal(h.s.record.reading_difficulty.rewrite_judgment,rewrite);
 assert.deepEqual(h.s.record.legacy_reading_difficulty,row.reading_difficulty);assert.ok(h.s.record.legacy_inferences.some(x=>x.includes('跨越')));
 if(firstPass===P.firstPass[1])assert.throws(()=>h.act('submit',{amendment_reason:'讨论'}),e=>e.step===1);
});
test('first submitted record is the authoritative source for migrated locked fields',()=>{
 const initial=legacy(P.difficulty[1]);const latest=structuredClone(initial);latest.revision=2;latest.event_version=120;latest.supersedes_revision=1;
 latest.reading_difficulty.paraphrase='后来改过的复述';latest.steps.reading_difficulty.completed_at=new Date(Date.parse(initial.timestamp)+500).toISOString();
 const h=setup(fromRow(latest),[initial,latest]);h.act('begin_discussion');
 assert.equal(h.s.record.reading_difficulty.paraphrase,initial.reading_difficulty.paraphrase);
 assert.equal(h.s.record.reading_difficulty.locked_at,initial.steps.reading_difficulty.completed_at);
 h.act('submit',{amendment_reason:'讨论后确认'});assert.equal(h.rows.length,3);
});
test('v2 revisions reject forged locked values, missing discussion provenance and invalid event ordering',()=>{
 const h=setup();core(h);done(h);h.act('begin_discussion');const r=h.act('submit',{amendment_reason:'讨论'}).record;
 for(const mutate of [x=>x.reading_difficulty.paraphrase='另一次复述',x=>delete x.amendment_reason,x=>x.event_version=h.rows[0].event_version,x=>x.event_version=1]){
  const wrong=structuredClone(r);mutate(wrong);assert.throws(()=>P.validate(wrong,form,h.rows[0]));
 }
 const firstBad=structuredClone(h.rows[0]);firstBad.amendment_kind='post_discussion';firstBad.amendment_reason='伪装';assert.throws(()=>P.validate(firstBad,form));
});
test('rewrite changes cannot bypass their amendment history by clearing or forging it',()=>{
 const h=setup();core(h,{...difficult,rewrite_judgment:P.rewriteChoices[1]});done(h);h.act('begin_discussion');h.act('navigate',{step:1});
 assert.throws(()=>h.act('save',{rewrite_judgment:null}),/不能清空/);
 h.act('save',{rewrite_judgment:P.rewriteChoices[0]});h.act('navigate',{step:6});const r=h.act('submit',{amendment_reason:'讨论'}).record;
 const forged=structuredClone(r);forged.reading_difficulty.amendments=[];
 assert.throws(()=>P.validate(forged,form,h.rows[0]),/缺少修改历史/);
 const wrongStart=structuredClone(r);wrongStart.reading_difficulty.amendments[0].from=P.rewriteChoices[0];
 assert.throws(()=>P.validate(wrongStart,form,h.rows[0]),/历史/);
});
test('schema metadata remains outside historical rows and draft UI metadata survives',()=>{
 const row=legacy();const state={...fromRow(row),ui:{branches:{otherWriting:'草稿'},readerScroll:90}};
 const h=setup(state,[row]);h.act('begin_discussion');const record=h.act('submit',{amendment_reason:'讨论'}).record;
 assert.equal(record.schema,'q1-note-judgment/1');assert.equal(record.event_schema_version,2);assert.ok(record.event_version>=P.eventVersionBase);
 assert.deepEqual(h.s.ui,state.ui);for(const key of ['viewStep','dirtySteps','discussion','ui'])assert.ok(!(key in record));
 assert.equal(row.event_schema_version,undefined);assert.equal(row.event_version,100);
});
test('compact unicode fingerprints retain their historical encoding',()=>assert.equal(P.canonical({z:['文',true],a:{b:1}}),'{"a":{"b":1},"z":["文",true]}'));

test('Python accepts JavaScript-produced new revisions and legacy discussion conversions',()=>{
 const h=setup();core(h,difficult);done(h);h.act('begin_discussion');h.act('navigate',{step:1});h.act('save',{rewrite_judgment:P.rewriteChoices[1]});h.act('navigate',{step:6});h.act('submit',{amendment_reason:'synthetic discussion'});
 const original=legacy(P.difficulty[1]);const upgraded=setup(fromRow(original),[structuredClone(original)]);upgraded.act('begin_discussion');upgraded.act('submit',{amendment_reason:'synthetic migration'});
 const result=spawnSync(__dirname+'/../.venv/bin/python',['-c',
  'import json,sys; sys.path.insert(0,"scripts"); from q1_note_form import validate_assessment\nfor rows in json.load(sys.stdin):\n for i,row in enumerate(rows): validate_assessment(row, rows[i-1] if i else None, rows[0])\nprint("validated")'],
  {cwd:__dirname+'/..',input:JSON.stringify([h.rows,upgraded.rows]),encoding:'utf8'});
 assert.equal(result.status,0,result.stderr);assert.equal(result.stdout.trim(),'validated');
});

test('resume early v2 drafts and retain v1 rewrite text without conflating it with the radio answer', () => {
  const h = setup();
  core(h, difficult);
  const earlyDraft = structuredClone(h.s);
  const old = earlyDraft.record.reading_difficulty;
  old.rewrite = old.rewrite_judgment;
  delete old.rewrite_judgment;
  const restored = P.normalizeDraft(earlyDraft);
  assert.deepEqual(restored.record.reading_difficulty, h.s.record.reading_difficulty);
  assert.ok(!Object.hasOwn(old, 'rewrite_judgment'));
  assert.throws(() => P.normalizeRecord({...earlyDraft.record, reading_difficulty: {...old, rewrite_judgment: null}}), /重复/);

  const legacy = {reading_difficulty: {rewrite: '改写不出'}};
  assert.equal(P.normalizeRecord(legacy), legacy);
});
