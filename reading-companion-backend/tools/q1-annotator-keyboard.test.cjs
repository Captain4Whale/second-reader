// Exercise the actual browser dispatcher and completion coordinator with controlled I/O.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const {readFileSync} = require('node:fs');
const html = readFileSync(__dirname+'/q1-annotator.html','utf8');
const source = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const extract = (start, end) => source.slice(source.indexOf(start),source.indexOf(end));
function harness() {
  const nodes = new Map(), clicks = [], moves = [];
  function node(id) {
    if (!nodes.has(id)) nodes.set(id, {
      id, open:false, disabled:false, hidden:false, clientHeight:500, scrollHeight:500,
      click(){if (!this.disabled) clicks.push(id);},
      closest(){return null;}, querySelector(){return null;}, scrollBy(v){moves.push([id,v.top]);},
    });
    return nodes.get(id);
  }
  const c = vm.createContext({document:{activeElement:node('progress')}, $:node, Promise,
    matchMedia:()=>({matches:true}), window:node('window')});
  vm.runInContext(`
    let review=true, hasItem=true, busy=false, composing=false, navigationEpoch=0, reviewCompletion=null;
    let session={state:{mi:0,rows:[],drafts:{},missDrafts:{}},writes:Promise.resolve(),browserWrites:Promise.resolve()};
    let acknowledged=true, completed=false, saves=0, focusCount=0, syncs=0, message='', lastAdvance=null;
    const marks=[{marginalia_id:'a'},{marginalia_id:'b'}];
    const item=()=>hasItem ? marks[session.state.mi] : null;
    const unit=()=>({marginalia:marks}), uid=()=> 'u';
    const reviewMode=()=>review, mixed=()=>review;
    let step=4, ready=true, legacy=false, decisions=[];
    const reviewSpec=()=>({criteria:[{id:'N1'},{id:'N2'},{id:'N3'},{id:'N4'}]});
    const summaryStep=()=>step===4, reviewStep=()=>step, legacyReview=()=>legacy;
    const markValue=()=>({rubric_uncovered:true});
    const Q1Rubric={complete:()=>ready};
    const setReviewStep=i=>{if(i>=0&&i<=4){step=i;navigationEpoch++;}};
    const nextReviewStep=()=>{step++;};
    const setCriterion=v=>{decisions.push(v);};
    const markStatus=()=>completed ? '已完成' : '未标注';
    const latest=()=>({revision:saves});
    const draftReview=()=>{};
    const saveMark=()=>{saves++;completed=true;return true;};
    const syncReviewControls=()=>{syncs++;};
    const canRevealPrior=()=>acknowledged;
    const neutralFocus=()=>{focusCount++;document.activeElement=$('progress');};
    const focusField=n=>{document.activeElement=n;};
    const say=text=>{message=text;};
    const chooseMark=i=>{session.state.mi=i;navigationEpoch++;};
    const moveUnit=i=>{navigationEpoch++;lastAdvance=i;};
    const finishMiss=()=>{}, showHelp=()=>{$('help').open=!$('help').open;};
    const selectedRange=null, activeMisses=()=>[];
  `, c);
  vm.runInContext(extract('    async function completeReview(', '    $("completeReview").onclick'),c);
  vm.runInContext(extract('    function handleKeydown(', '    document.addEventListener("keydown", handleKeydown);'),c);
  const run = code=>vm.runInContext(code,c);
  function key(key, options={}) {
    const e={key,code:'',target:node('progress'),preventDefault(){this.prevented=true;},...options};
    c.handleKeydown(e);return e;
  }
  return {c,node,run,key,clicks,moves};
}
test('stepwise keys select criteria, judge, browse and scope summary controls',()=>{
  const h=harness();h.node('criterionFlags').querySelector=()=>h.node('flag');
  h.node('rubricTags').querySelector=()=>h.node('tag');
  h.key('1');assert.equal(h.run('step'),0);h.key('p');h.key('f');
  assert.equal(h.run('decisions.join(",")'),'pass,fail');assert.equal(h.run('step'),0);
  h.key('r');assert.equal(h.c.document.activeElement.id,'criterionReason');
  h.key('Enter');assert.equal(h.run('step'),1);
  h.key('v');h.key('5');h.key('b');assert.deepEqual(h.clicks,['flag']);
  h.key('4');assert.equal(h.run('step'),3);
  h.key('!',{shiftKey:true,code:'Digit1'});assert.equal(h.run('step'),0);
  h.key('!',{shiftKey:true,code:'Digit1'});assert.equal(h.node('criterionHelp').open,true);
  h.key(']');assert.equal(h.run('step'),1);h.key('[');assert.equal(h.run('step'),0);
  h.key('m');assert.equal(h.run('step'),4);assert.equal(h.c.document.activeElement.id,'memo');
  for(const k of ['5','0','s','b','v'])h.key(k);
  assert.deepEqual(h.clicks,['flag','tag','uncovered','star','showPrior']);
  assert.equal(h.key('o').prevented,true);
});
test('an incomplete case cannot complete even on summary',async()=>{
  const h=harness();h.run('ready=false');await h.c.completeReview(true);
  assert.equal(h.run('saves'),0);assert.equal(h.run('session.state.mi'),0);
  assert.match(h.run('message'),/所有条件/);
});
test('composition, modifiers, editable ancestors, repeat and native controls are respected',()=>{
  const h=harness();
  h.node('criteria').querySelector=()=>h.node('flag');
  for(const opts of [{repeat:true},{isComposing:true},{keyCode:229},{metaKey:true},{ctrlKey:true},{altKey:true}]) h.key('v',opts);
  const editable={closest:s=>s.startsWith('textarea') ? {} : null};
  for(const key of ['v','1','Enter','ArrowDown']) h.key(key,{target:editable});
  const native={closest:s=>s.startsWith('button') ? {} : null};
  assert.equal(h.key('Enter',{target:native}).prevented,undefined);
  h.key(' ',{target:h.node('checkbox')});
  assert.equal(h.clicks.length,0);assert.equal(h.run('saves'),0);
  h.key('j',{repeat:true});h.key('k',{repeat:true,shiftKey:true});
  assert.deepEqual(h.moves.map(v=>v[0]),['readerScroll','window']);
  h.run('step=0');h.key('r');assert.equal(h.c.document.activeElement.id,'criterionReason');
  h.key('Escape',{target:editable});assert.equal(h.c.document.activeElement.id,'progress');
});
test('Open Coding retains P/F/S/V, density, arrows and text fields',()=>{
  const h=harness();h.run('review=false');
  h.node('density').querySelector=s=>h.node('density'+s.match(/[123]/)[0]);
  for(const k of ['p','f','s','v','1','2','3']) h.key(k);
  assert.deepEqual(h.clicks,['pass','fail','star','verify','density1','density2','density3']);
  h.key('Enter');assert.equal(h.run('saves'),0);
  h.key('ArrowDown');assert.equal(h.run('session.state.mi'),1);
  h.key('ArrowDown');assert.equal(h.run('session.state.mi'),1);
  h.key('ArrowRight');assert.equal(h.run('lastAdvance'),1);
  h.key('m');assert.equal(h.c.document.activeElement.id,'memo');
  h.key('u');assert.equal(h.c.document.activeElement.id,'unitNote');
});
test('scroll keys follow the visible review surface and preserve narrow/Open Coding page scrolling',()=>{
  const h=harness();h.run('step=0');h.node('criterionHelp').open=true;
  h.key('j',{shiftKey:true});h.key('k');
  h.node('criterionHelp').open=false;h.key('j',{shiftKey:true});
  h.c.matchMedia=()=>({matches:false});h.key('j',{shiftKey:true});
  h.c.matchMedia=()=>({matches:true});h.run('review=false');h.key('k',{shiftKey:true});
  assert.deepEqual(h.moves.map(v=>v[0]),['window','readerScroll','window','window','window']);
  h.run('review=true');h.node('criterionHelp').open=true;
  h.node('decisionScroll').scrollHeight=700;h.key('j',{shiftKey:true});
  h.run('hasItem=false');h.key('j',{shiftKey:true});
  assert.deepEqual(h.moves.slice(-2).map(v=>v[0]),['window','window']);
});
test('U opens window notes and reveals the field in the page',()=>{
  const h=harness(), seen=[];
  const field=h.node('unitNote');
  field.focus=options=>seen.push(['focus',options.preventScroll]);
  h.c.revealReviewElement=field=>seen.push(['reveal',field.id]);
  h.c.resizeTextareas=()=>{};
  const focusField=vm.runInContext('('+extract('    function focusField(', '    function neutralFocus(')+')',h.c);
  focusField(field);
  assert.equal(h.node('windowNotes').open,true);
  assert.deepEqual(seen,[['focus',true],['reveal','unitNote']]);
  assert.equal(h.moves.length,0);
});
test('completion stays or advances within window, without duplicate revisions',async()=>{
  const h=harness();await h.c.completeReview();
  assert.equal(h.run('saves'),1);assert.equal(h.run('session.state.mi'),0);
  await h.c.completeReview(true);assert.equal(h.run('saves'),1);assert.equal(h.run('session.state.mi'),1);
  await h.c.completeReview(true);assert.equal(h.run('session.state.mi'),1);assert.match(h.run('message'),/最后一条/);
});
test('completion waits for disk AND browser receipts and suppresses duplicate attempts',async()=>{
  const h=harness();let disk,browser;
  h.c.disk=new Promise(r=>disk=r);h.c.browser=new Promise(r=>browser=r);
  h.run('session.writes=disk;session.browserWrites=browser');
  const pending=h.c.completeReview(true);await h.c.completeReview(true);
  assert.equal(h.run('saves'),1);assert.equal(h.run('session.state.mi'),0);
  disk();await Promise.resolve();assert.equal(h.run('session.state.mi'),0);
  browser();await pending;assert.equal(h.run('session.state.mi'),1);
});
test('failed or absent save acknowledgement keeps the current annotation',async()=>{
  const h=harness();h.run('acknowledged=false');await h.c.completeReview(true);
  assert.equal(h.run('session.state.mi'),0);assert.match(h.run('message'),/两端保存/);
  assert.equal(h.run('focusCount'),0);assert.equal(h.run('reviewCompletion'),null);
});
for(const change of [
  'chooseMark(1);chooseMark(0)',
  'setReviewStep(0);setReviewStep(4)',
  "document.activeElement=$('reason')",
  "session.state.drafts.a={reason:'new edit'}",
  'saves++',
  "session={...session,state:{...session.state}}",
  "$('help').open=true",
]) test('pending completion cannot steal focus or navigate after '+change,async()=>{
  const h=harness();let release;h.c.gate=new Promise(r=>release=r);h.run('session.writes=gate');
  const pending=h.c.completeReview(true);h.run(change);release();await pending;
  assert.equal(h.run('session.state.mi'),0);assert.equal(h.run('focusCount'),0);assert.equal(h.run('reviewCompletion'),null);
});

test('Shift+Enter on the completion button survives disabling the focused control',async()=>{
  const h=harness();h.c.document.activeElement=h.node('completeReview');
  await h.c.completeReview(true);
  assert.equal(h.run('session.state.mi'),1);assert.equal(h.c.document.activeElement.id,'progress');
});


test('page reveal leaves visible headings in place and clears toolbar/footer for fields',()=>{
  const h=harness();h.c.window.innerHeight=800;
  h.node('toolbar').getBoundingClientRect=()=>({bottom:140});
  h.node('reviewActions').offsetHeight=60;
  const reveal=vm.runInContext('('+extract('    function revealReviewElement(', '    function focusField(')+')',h.c);
  reveal({getBoundingClientRect:()=>({top:200,bottom:240,height:40})});
  assert.equal(h.moves.length,0);
  reveal({getBoundingClientRect:()=>({top:700,bottom:764,height:64})});
  assert.equal(h.moves.at(-1)[1],48);
  reveal({getBoundingClientRect:()=>({top:100,bottom:140,height:40})});
  assert.equal(h.moves.at(-1)[1],-52);
});
