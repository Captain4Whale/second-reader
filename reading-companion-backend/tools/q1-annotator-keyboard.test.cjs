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
      id, open:false, disabled:false, hidden:false, clientHeight:500,
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
test('rubric numbers, flags, prior and Shift+digits dispatch only to configured controls',()=>{
  const h=harness();
  h.node('rubricEditor').querySelector=s=>s.includes('"1"') ? h.node('criterion') : null;
  h.node('criteria').querySelector=s=>s.includes('"V"') ? h.node('flag') : s.includes('"1"') ? h.node('explanation') : null;
  h.node('explanation').querySelector=()=>h.node('summary');
  h.key('1');h.key('4');h.key('0');h.key('v');h.key('b');
  assert.deepEqual(h.clicks,['criterion','uncovered','flag','showPrior']);
  h.key('!',{shiftKey:true,code:'Digit1'});assert.equal(h.node('explanation').open,true);
  h.key('!',{shiftKey:true,code:'Digit1'});assert.equal(h.node('explanation').open,false);
  h.node('criteria').querySelector=()=>null;h.key('v');assert.equal(h.clicks.length,4);
  for(const k of ['p','f','o']) assert.equal(h.key(k).prevented,true);
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
  h.key('r');assert.equal(h.c.document.activeElement.id,'reason');
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
