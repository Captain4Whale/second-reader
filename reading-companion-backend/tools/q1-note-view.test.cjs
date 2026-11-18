const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const src = fs.readFileSync(__dirname+'/q1-note-annotator.js','utf8');
function extract(start,end) {
  const from=src.indexOf(start),to=src.indexOf(end,from);
  assert.ok(from>=0 && to>from,`source boundary missing: ${start} / ${end}`);
  return src.slice(from,to);
}
function keyboardHarness(step=1) {
  const calls=[],errors=[],listeners={},nodes=new Map();
  const get=id=>{
    if(!nodes.has(id)) nodes.set(id,{id,open:false,hidden:false,disabled:false,
      click(){calls.push(id);},close(){this.open=false;calls.push('close');}});
    return nodes.get(id);
  };
  const options={firstPass:[0,1],rewriteChoice:[2,3],tag:[0,1,2,3,4]};
  const host={addEventListener:(name,fn)=>listeners[name]=fn,
    querySelector:selector=>selector==='[name="tag"]'&&options.tag?.length?{name:'tag'}:null,
    querySelectorAll:selector=> (selector.includes('firstPass')?options.firstPass:selector.includes('rewriteChoice')?options.rewriteChoice:selector.includes('tag')?options.tag:[])
      .map(i=>({click(){calls.push(i);}}))};
  const c=vm.createContext({composing:false,busy:false,tagMode:false,pendingGroupFocus:null,executing:false,dirty:false,
    boot:{record_ids:['r1','r2']},index:0,commandTail:Promise.resolve(),pendingContinuation:null,
    data:{state:{stage:step,viewStep:step,record:{first_impression:{}}}},
    $:get,host,innerWidth:1200,document:{getElementById:get},
    currentStep:()=>c.data.state.viewStep ?? c.data.state.stage,
    isReadOnly:()=>c.data.state.stage===7 || !!c.data.state.discussionRequired,
    currentId:()=>c.boot.record_ids[c.index],
    focusGroup:name=>calls.push(name),focusField:id=>calls.push(id),
    focusDecision:()=>calls.push('decision'),shownError:error=>errors.push(error),
    save:async()=>{calls.push('save');c.dirty=false;},
    inspect:async i=>{calls.push(['navigate',i]);c.data.state.viewStep=i;},
    completeCurrent:async advance=>calls.push(['complete',advance]),
    openCase:async i=>{calls.push(['case',i]);c.index=i;},
  });
  vm.runInContext(extract('  function enqueue(', '  async function persistUI(')+
    extract('  function queueContinue(', '  async function completeCurrent(')+
    extract('  function queuedGroupKey(', '  document.addEventListener("keydown", keydown'),c);
  return {c,calls,errors,listeners,get,options,host,
    key(key,props={},target={matches:()=>false,closest:()=>null}) {
      const event={key,preventDefault(){this.prevented=true;},composedPath:()=>[target],...props};
      c.event=event;vm.runInContext('keydown(event)',c);return event;
    },
    async drain(){await c.commandTail;if(c.pendingContinuation)await c.pendingContinuation;await Promise.resolve();assert.deepEqual(errors,[]);}
  };
}
function postHarness() {
 const calls=[],fields=new Map(),get=id=>{
  if(!fields.has(id))fields.set(id,{value:'',hidden:false,textContent:''});
  return fields.get(id);
 };
 const c=vm.createContext({$:get,active:0,busy:false,dirty:false,composing:false,editEpoch:0,timer:null,
  clearTimeout,host:{querySelectorAll:()=>[]},
  data:{state:{version:1,viewStep:2,record:{first_impression:{}}},unit_note:''},
  currentId:()=> 'r',currentStep:()=>c.data.state.viewStep,elapsed:()=>0,captureUI:()=>({}),
  collect:()=>c.values,values:{n1:{writing_style:'补充'}},
  render:()=>calls.push(['render',c.data.state.version]),rememberFocus:()=>null,restoreFocus:()=>{},
  updateStatus:()=>{},updateNavigation:()=>{},persistUI:async()=>calls.push('ui'),
  api:async(path,body)=>{calls.push(body.action);return {...c.data,state:{...c.data.state,version:c.data.state.version+1}};}});
 vm.runInContext(extract('  function lockEditing(', '  function updateStatus(')+
  extract('  async function save(', '  async function openCase('),c);
 return {c,calls,get,run:code=>vm.runInContext(code,c)};
}
function groupHarness() {
 const h=keyboardHarness(2),groups={};
 for(const [name,values] of Object.entries({n1:['pass','fail'],style:['补充','联想','解读'],followingUse:['没用到','紧接着几段','挂早了'],failure:['没新东西','下文马上讲了']})) {
  groups[name]=values.map(value=>({name,value,type:name==='failure'?'checkbox':'radio',checked:false,disabled:false,
   focus(){h.host.activeElement=this;},scrollIntoView(){},
   click(){
    if(this.type==='radio')groups[name].forEach(el=>el.checked=false);
    this.checked=this.type==='radio'||!this.checked;h.c.dirty=true;h.calls.push([name,value]);
   }}));
 }
 h.host.querySelectorAll=selector=>groups[selector.match(/name="([^"]+)"/)?.[1]]||[];
 h.host.querySelector=selector=>{
  const group=groups[selector.match(/name="([^"]+)"/)?.[1]]||[];
  const value=selector.match(/value="([^"]+)"/)?.[1];
  return value?group.find(el=>el.value===value):group[0];
 };
 vm.runInContext(extract('  function focusGroup(', '  function focusMissing('),h.c);
 return {...h,groups};
}
function harness(width=1200) {
  const nodes=new Map();
  const get=id=> {
    if(!nodes.has(id)) nodes.set(id,{hidden:false,textContent:'',scrollTop:80,clientHeight:400,
      getBoundingClientRect:()=>({top:100}),querySelector:()=>null,
      scrollIntoView(opts){this.scrolled=opts;},focus(opts){this.focused=opts;}});
    return nodes.get(id);
  };
  const c=vm.createContext({$:get,innerWidth:width,host:{querySelectorAll:()=>[]}});
  vm.runInContext(extract('  const outcomeLabel','  function node('),c);
  return {get,c,run:code=>vm.runInContext(code,c)};
}
test('anchor positioning scrolls only reading pane, leaves following text untouched',()=>{
  const h=harness(), mark={getBoundingClientRect:()=>({top:500})};
  h.get('sourceText').querySelector=()=>mark;
  h.get('following').hidden=true;
  h.run('locateAnchor()');
  assert.equal(h.get('readerScroll').scrollTop,300);
  assert.equal(h.get('anchorStatus').hidden,true);
  assert.equal(h.get('following').hidden,true);
});
test('missing anchor has visible fallback; narrow layout reveals actual anchor',()=>{
  const h=harness(600); h.run('locateAnchor()');
  assert.equal(h.get('anchorStatus').hidden,false);
  assert.match(h.get('anchorStatus').textContent,/未找到/);
  const mark=h.get('mark'); h.get('sourceText').querySelector=()=>mark;
  h.run('locateAnchor()'); assert.equal(mark.scrolled.block,'center');
});
test('decision jump focuses heading without an intermediate scroll jump',()=>{
  const h=harness(),title=h.get('title'); h.get('workflow').querySelector=()=>title;
  h.run('focusDecision()');assert.equal(title.tabIndex,-1);
  assert.equal(title.focused.preventScroll,true);assert.equal(title.scrolled.block,'nearest');
});
test('read-only outcomes are Chinese including unjudged fallback',()=>{
  const h=harness(); assert.equal(h.run("outcomeLabel('pass')"),'过');
  assert.equal(h.run("outcomeLabel('fail')"),'不过');assert.equal(h.run('outcomeLabel(null)'),'未判定');
});
test('help preferences default closed, restore, and tolerate unavailable storage',()=>{
  const snippet=extract('  const preferenceKey','  const outcomeLabel');
  for(const [value,expected] of [[null,{}],['{"n1":true}',{n1:true}],['broken',{}]]) {
    const c=vm.createContext({localStorage:{getItem:()=>value}});
    vm.runInContext(snippet,c);
    assert.deepEqual(JSON.parse(vm.runInContext('JSON.stringify(helpPreferences)',c)),expected);
  }
  const c=vm.createContext({localStorage:{getItem(){throw Error('blocked');}}});
  assert.doesNotThrow(()=>vm.runInContext(snippet,c));
});
test('first-impression selection survives redraw using protocol values, not display labels',()=>{
  const radiosCall=src.slice(src.indexOf('    if (s === 0)\n      radios('),src.indexOf('    if (s === 1) {',src.indexOf('    if (s === 0)\n      radios(')));
  function element(tag){return {tag,children:[],append(...children){this.children.push(...children);}};}
  for(const judgment of [null,'pass','fail']) {
    const w=element('section');
    const c=vm.createContext({s:0,r:{first_impression:{judgment}},w,
      node:element,document:{createElement:element}});
    vm.runInContext(extract('  function radios(', '  function get(')+radiosCall,c);
    const inputs=w.children[0].children.slice(1).map(label=>label.children[0]);
    assert.deepEqual(inputs.filter(i=>i.checked).map(i=>i.value),judgment?[judgment]:[]);
  }
});
test('validation feedback hides retry while storage errors retain recovery',()=>{
  const h=harness();
  vm.runInContext(extract('  function shownError(', '  function tick('),h.c);
  h.run('shownError({code:"FORM_VALIDATION",message:"请选择第一印象"})');
  assert.equal(h.get('status').textContent,'请检查判定内容');
  assert.equal(h.get('retryVisible').hidden,true);
  assert.equal(h.get('error').textContent,'请选择第一印象');
  h.run('shownError(new Error("disk failed"))');
  assert.equal(h.get('retryVisible').hidden,false);
  assert.match(h.get('status').textContent,/保存失败/);
});
test('status separates unsaved browser drafts from submitted file synchronization',()=>{
 const h=harness();h.c.dirty=false;h.c.session={};
 h.c.data={state:{record:{review_completed:false}},receipt:{browser_saved:false,journal_revision:0,file_revision:0,pending_file:false}};
 vm.runInContext(extract('  function updateStatus(', '  async function save('),h.c);
 h.run('updateStatus()');assert.doesNotMatch(h.get('status').textContent,/草稿已保存在此浏览器/);
 assert.match(h.get('status').textContent,/尚未保存|保存失败/);
 h.c.data.receipt={browser_saved:true,journal_revision:2,file_revision:1,pending_file:true,submitted_revision:2};
 h.run('updateStatus()');assert.match(h.get('status').textContent,/草稿已保存在此浏览器/);
 assert.match(h.get('status').textContent,/已提交记录待同步文件/);
 assert.match(h.get('status').textContent,/本条有待提交修改/);
 h.c.data.receipt.pending_file=false;h.c.data.receipt.file_revision=2;h.c.data.state.record.review_completed=true;
 h.run('updateStatus()');assert.match(h.get('status').textContent,/修订 2/);
 assert.doesNotMatch(h.get('status').textContent,/本条有待提交修改|待同步文件/);
});
test('conclusion hint explains decision instead of displaying markdown table header',()=>{
  const h=harness();
  const hint=h.run('stepHint({id:"conclusion",help:"| 项 | 类型 | 问题 |"})');
  assert.match(hint,/N1 过/);assert.match(hint,/未覆盖/);assert.doesNotMatch(hint,/\|/);
  assert.equal(h.run('stepHint({id:"n1",help:"**原说明**"})'),'原说明');
});
test('redraw restores option focus without stealing a newer focus',()=>{
 const h=harness();
 const old={name:'difficulty',value:'一遍能复述'},fresh={...old,focus(){this.focused=true;}},newer={id:'reason'};
 h.c.host={activeElement:old,querySelectorAll:()=>[fresh]};
 const f=h.run('rememberFocus()');h.c.f=f;
 h.c.host.activeElement=newer;h.run('restoreFocus(f)');assert.equal(fresh.focused,undefined);
 h.c.host.activeElement=null;h.run('restoreFocus(f)');assert.equal(fresh.focused,true);
});
test('keyboard uses native arrows in controls, preserves IME and traps help dialog',async()=>{
 const h=keyboardHarness(),input={matches:()=>true,closest:()=>null};
 assert.equal(h.key('ArrowRight',{},input).prevented,undefined);
 assert.equal(h.key('d',{isComposing:true}).prevented,undefined);
 assert.equal(h.key('d',{keyCode:229}).prevented,undefined);
 h.c.composing=true;h.key('g');h.c.composing=false;
 h.get('shortcutHelp').open=true;h.key('p');
 await h.drain();assert.deepEqual(h.calls,[]);
 assert.equal(h.key('Escape').prevented,true);assert.deepEqual(h.calls,['close']);
});
test('independent difficulty answers and text shortcuts work outside text entry only',async()=>{
 const h=keyboardHarness();
 for(const key of ['q','g','w','z','y','i','m']) h.key(key);
 await h.drain();assert.deepEqual(h.calls,[0,1,2,3,'paraphrase','rewrite','reason']);
 h.key('g',{}, {closest:()=>({tagName:'TEXTAREA'})});
 await h.drain();assert.equal(h.calls.length,7);
});
test('rewrite labels explain rubric while radio values keep independent answer identities',()=>{
 const values=['能改写得更直白','改写不出'];
 function node(tag,text){return {tag,text,children:[],append(...xs){this.children.push(...xs);}};}
 const w=node('div'),c=vm.createContext({node,document:{createElement:node},w,values});
 vm.runInContext(extract('  const difficultyLabel','  function stepHint(')+extract('  function radios(', '  function get('),c);
 vm.runInContext('radios(w,"rewriteChoice","能否改写",values,"改写不出")',c);
 const labels=w.children[0].children.slice(1);
 assert.deepEqual(labels.map(l=>l.children[0].value),values);
 assert.equal(labels[1].children[0].checked,true);
 assert.match(labels[1].children[1].text,/想法本身复杂.*表达已尽量清楚.*不否决.*拿不准.*Z/);
 assert.match(labels[0].children[1].text,/不丢内容.*W/);
});

test('difficulty form has two independent unanswered groups and locks only first-pass evidence',()=>{
 const start=src.indexOf('    if (s === 1) {',src.indexOf('    const spec = boot.form.steps[s];'));
 const call=src.slice(start,src.indexOf('    if (s === 2) {',start));
 function node(tag,text){return {tag,text,children:[],append(...xs){this.children.push(...xs);},
  querySelectorAll(selector){return this.children.flatMap(el=>[...(el.name==='firstPass'?[el]:[]),...(el.querySelectorAll?.(selector)||[])]);}};}
 for(const d of [{first_pass:null,rewrite:null},{first_pass:'复述得出',rewrite:null,rewrite_text:'保留的改写'},{first_pass:'复述不出或说偏',rewrite:null},{first_pass:'复述不出或说偏',rewrite:'改写不出',locked_at:'locked'}]) {
  const w=node('div'),fields={},ctx=vm.createContext({s:1,node,document:{createElement:node},w,r:{reading_difficulty:d},
   textArea:(parent,id,label,value)=>{const field={id,label,value};fields[id]=field;parent.append(field);return field;}});
  vm.runInContext(extract('  const difficultyLabel','  function stepHint(')+extract('  function radios(', '  function get(')+call,ctx);
  const groups=w.children.filter(el=>el.tag==='fieldset');
  const inputs=group=>group.children.slice(1).map(l=>l.children[0]);
  assert.deepEqual(inputs(groups[0]).filter(i=>i.checked).map(i=>i.value),d.first_pass?[d.first_pass]:[]);
  if(d.first_pass==='复述不出或说偏')assert.deepEqual(inputs(groups[1]).filter(i=>i.checked).map(i=>i.value),d.rewrite?[d.rewrite]:[]);
  else assert.equal(groups.length,1);
  assert.equal(!!fields.paraphrase.readOnly,!!d.locked_at);
  assert.ok(fields.rewrite);assert.equal(fields.rewrite.value,d.rewrite_text);
  assert.equal(inputs(groups[0]).every(i=>i.disabled===true),!!d.locked_at);
  if(groups[1])assert.ok(inputs(groups[1]).every(i=>!i.disabled));
 }
});

test('reopening an N1 other branch restores hidden explanation without overriding an intentional clear',()=>{
 const branches={otherWriting:'保留的其他写法说明',otherFailure:'保留的其他失败说明'};
 for(const [judgment,id,key] of [['pass','otherWriting','other_writing_explanation'],['fail','otherFailure','other_failure_explanation']]) {
  const fields={n1Paraphrase:{value:'复述'},n1Reason:{value:'理由'}};
  const c=vm.createContext({currentStep:()=>2,uiState:()=>({branches}),
   data:{state:{record:{uncovered_reason:'',reason:''},ui:{branches}}},
   $:id=>fields[id],checked:()=>false,
   get:name=>({n1:judgment,followingUse:'没用到',style:'其他写法'}[name]),
   host:{querySelector:()=>null,querySelectorAll:()=>[{value:'其他'}]}});
  vm.runInContext(extract('  function collect(', '  const currentStep'),c);
  assert.equal(vm.runInContext('collect()',c).n1[key],branches[id]);
  fields[id]={value:''};
  assert.equal(vm.runInContext('collect()',c).n1[key],'');
 }
});

test('returning to completed steps navigates without reopening or clearing subsequent answers',async()=>{
  const P=require('./q1-note-protocol.js');
  const record={first_impression:{judgment:'pass',locked_at:'locked'},review_completed:true,
    reading_difficulty:{choice:'一遍能复述',original_choice:'一遍能复述'},
    n1:{judgment:'pass',writing_style:'补充'},tags:['冗余'],revision:4,
    steps:{first_impression:{completed_at:'first'},reading_difficulty:{completed_at:'difficulty'},n1:{completed_at:'n1'}}};
  const data={state:{stage:7,viewStep:7,maxUnlockedStage:6,dirtySteps:[],version:5,record}};
  const snapshot=JSON.stringify(record),calls=[];
  const c=vm.createContext({data,tagMode:true,flush:async()=>calls.push('flush'),
    currentStep:()=>c.data.state.viewStep,
    post:async(a,v)=>{calls.push([a,v.step]);c.data.state=P.transition(c.data.state,a,v,0,{}, {}, []);},
    focusDecision:()=>calls.push('focus')});
  vm.runInContext(extract('  async function inspect(', '  host.addEventListener("compositionstart"'),c);
  for(const step of [1,2,3,4,5,6,0]) {
    calls.length=0;await vm.runInContext(`inspect(${step})`,c);
    assert.deepEqual(calls,['flush',['navigate',step],'focus']);
    assert.equal(c.data.state.viewStep,step);
    assert.equal(c.data.state.stage,7);assert.equal(c.data.state.maxUnlockedStage,6);
    assert.equal(JSON.stringify(c.data.state.record),snapshot);
  }
  assert.equal(c.tagMode,false);
  assert.doesNotMatch(src,/editCompletedStep|amendControls|保存费劲修正/);
});
test('navigation enforces first-pass frontier and revisiting current step does not post',async()=>{
  const calls=[],c=vm.createContext({data:{state:{stage:2,viewStep:1,maxUnlockedStage:2}},
    currentStep:()=>c.data.state.viewStep,flush:async()=>calls.push('flush'),
    post:async(a,v)=>calls.push([a,v.step]),focusDecision:()=>calls.push('focus')});
  vm.runInContext(extract('  async function inspect(', '  host.addEventListener("compositionstart"'),c);
  await vm.runInContext('inspect(3)',c);await vm.runInContext('inspect(-1)',c);
  assert.deepEqual(calls,[]);
  await vm.runInContext('inspect(1)',c);assert.deepEqual(calls,['flush','focus']);
  calls.length=0;await vm.runInContext('inspect(2)',c);
  assert.deepEqual(calls,['flush',['navigate',2],'focus']);
});
test('number keys navigate normally; T explicitly enables tag numbers and Escape exits',async()=>{
  const h=keyboardHarness(6);
  h.key('5');await h.drain();assert.deepEqual(h.calls,[['navigate',4]]);
  h.key('7');await h.drain();assert.equal(h.c.tagMode,false);
  h.calls.length=0;h.key('t');await h.drain();assert.equal(h.c.tagMode,true);
  for(const key of ['5','6','7','8','9']) h.key(key);
  await h.drain();assert.deepEqual(h.calls,['tag',0,1,2,3,4]);
  h.key('Escape');assert.equal(h.c.tagMode,false);
  h.key('6');await h.drain();assert.deepEqual(h.calls.slice(-2),['decision',['navigate',5]]);
});
test('tag mode exits when focus leaves tags, and missing tags cannot enable it',async()=>{
  const h=keyboardHarness(6);h.key('t');await h.drain();
  h.listeners.focusin({target:{matches:selector=>selector==='[name="tag"]'}});
  assert.equal(h.c.tagMode,true);
  h.listeners.focusin({target:{matches:()=>false}});assert.equal(h.c.tagMode,false);
  h.options.tag=[];h.key('t');await h.drain();assert.equal(h.c.tagMode,false);
});
test('T then a tag number retain their meaning while an earlier command is still saving',async()=>{
  const h=keyboardHarness(6);let release;
  h.c.blocked=()=>new Promise(resolve=>release=resolve);
  vm.runInContext('enqueue(blocked)',h.c);await Promise.resolve();await Promise.resolve();
  h.key('t');h.key('5');release();await h.drain();
  assert.deepEqual(h.calls,['tag',0]);
  assert.equal(h.c.data.state.viewStep,6);
});
test('shift shortcuts focus conditional fields without triggering ordinary groups',async()=>{
  const h=keyboardHarness(2);
  h.key('W',{shiftKey:true,code:'KeyW'});h.key('X',{shiftKey:true,code:'KeyX'});
  h.key(')',{shiftKey:true,code:'Digit0'});
  await h.drain();assert.deepEqual(h.calls,['otherWriting','otherFailure','uncoveredReason']);
  h.calls.length=0;h.key('w');h.key('x');h.key('y');h.key('r');h.key('m');
  await h.drain();assert.deepEqual(h.calls,['style','failure','n1Paraphrase','n1Reason','reason']);
});
test('file shortcuts retain trusted activation; Ctrl Enter saves unit note while typing',async()=>{
  const h=keyboardHarness();
  for(const key of ['O','S','V']) h.key(key,{shiftKey:true});
  assert.deepEqual(h.calls,['openFolder','exportNote','retry']);
  const target={id:'unitNote',closest:()=>({tagName:'TEXTAREA'})};
  assert.equal(h.key('Enter',{ctrlKey:true},target).prevented,true);
  assert.deepEqual(h.calls,['openFolder','exportNote','retry','saveUnit']);
  await h.drain();
});
test('rapid choices are serialized through slow saves instead of discarded while busy',async()=>{
  const h=keyboardHarness();let release;
  h.host.querySelectorAll=()=>[0,1,2].map(i=>({click(){h.calls.push(i);h.c.dirty=true;}}));
  let saves=0;
  h.c.save=async()=>{h.calls.push('save-start');if(++saves===1)await new Promise(resolve=>release=resolve);h.c.dirty=false;h.calls.push('save-end');};
  h.c.busy=true;
  h.key('q');await Promise.resolve();await Promise.resolve();
  assert.deepEqual(h.calls,[0,'save-start']);
  h.key('g');h.key('Enter');assert.deepEqual(h.calls,[0,'save-start']);
  release();await h.drain();
  assert.deepEqual(h.calls,[0,'save-start','save-end',1,'save-start','save-end',['complete',undefined]]);
});
test('queued repeated continuation runs once and stale case choices cannot edit the next item',async()=>{
  const h=keyboardHarness();
  h.c.completeCurrent=async()=>{h.calls.push('complete');h.c.data.state.viewStep++;};
  h.key('Enter');h.key('Enter');await h.drain();assert.deepEqual(h.calls,['complete']);
  h.calls.length=0;h.c.data.state.viewStep=1;
  h.key('ArrowDown');h.key('g');await h.drain();
  assert.deepEqual(h.calls,[['case',1]]);
});
test('step navigation followed by difficulty choice judges editable destinations but preserves submitted records',async()=>{
 for(const step of [2,7,0]) {
  const h=keyboardHarness(step);
  if(step===0)h.c.data.state.record.first_impression.locked_at='already locked';
  h.key('2');h.key('g');await h.drain();
  assert.deepEqual(h.calls,step===7?[['navigate',1]]:[['navigate',1],1]);
 }
});
test('blocked navigation then choice and repeated Enter judges and continues the destination once',async()=>{
 const h=keyboardHarness(2);let release;
 h.c.blocked=()=>new Promise(resolve=>release=resolve);
 vm.runInContext('enqueue(blocked)',h.c);await Promise.resolve();await Promise.resolve();
 h.c.completeCurrent=async()=>{h.calls.push(['complete',h.c.data.state.viewStep]);h.c.data.state.viewStep++;};
 h.key('2');h.key('g');h.key('Enter');h.key('Enter');
 release();await h.drain();
 assert.deepEqual(h.calls,[['navigate',1],1,['complete',1]]);
 assert.equal(h.c.data.state.viewStep,2);assert.equal(h.c.pendingContinuation,null);
 h.key('Enter');await h.drain();assert.deepEqual(h.calls.at(-1),['complete',2]);
});
test('a failed command reports the error and does not poison later queued commands',async()=>{
  const h=keyboardHarness(),failure=new Error('validation');
  h.c.completeCurrent=async()=>{throw failure;};h.key('Enter');h.key('g');
  await h.c.commandTail;await Promise.resolve();
  assert.deepEqual(h.errors,[failure]);assert.deepEqual(h.calls,[1]);
});
test('flush renders the latest same-step edit after a slow save preserves newer input',async()=>{
 const h=postHarness();let release,requests=0;
 h.c.api=async(path,body)=>{
  h.calls.push(['save',body.values.n1.writing_style]);
  if(++requests===1)await new Promise(resolve=>release=resolve);
  return {...h.c.data,state:{...h.c.data.state,version:h.c.data.state.version+1}};
 };
 h.c.dirty=true;const pending=h.run('save(true)');
 h.c.editEpoch++;h.c.values={n1:{writing_style:'其他写法',other_writing_explanation:''}};
 release();await pending;
 assert.equal(h.c.dirty,true);assert.deepEqual(h.calls,[['save','补充']]);
 await h.run('flush()');
 assert.equal(h.c.dirty,false);
 assert.deepEqual(h.calls,[['save','补充'],['save','其他写法'],['render',3],'ui']);
});
test('same-step validation redraws saved conditional controls before reporting the missing field',async()=>{
 const h=postHarness(),error=Object.assign(new Error('其他写法必须说明'),{code:'FORM_VALIDATION',step:2});
 h.c.api=async()=>{throw error;};
 await assert.rejects(h.run('post("complete", {})'),e=>e===error);
 assert.deepEqual(h.calls,[['render',1]]);assert.equal(h.c.busy,false);
});
test('queued native changes collect the latest DOM and drain edits arriving during a save',async()=>{
 const h=postHarness(),handlers={};
 Object.assign(h.c,{boot:{record_ids:['r']},index:0,commandTail:Promise.resolve(),executing:false,
  editEpoch:0,autoGrow:()=>{},setTimeout:()=>1,shownError:error=>{throw error;}});
 h.get('workflow').addEventListener=(event,handler)=>handlers[event]=handler;
 vm.runInContext(extract('  function enqueue(', '  async function persistUI(')+
  extract('  $("workflow").addEventListener("input"', '  $("prev").onclick'),h.c);
 const nativeChange=value=>{
  h.c.values={n1:{writing_style:value}};
  handlers.input();handlers.change({target:{matches:()=>true}});
 };
 let release,requests=0;
 h.c.api=async(path,body)=>{
  h.calls.push(['save',body.values.n1.writing_style]);
  if(++requests===1)await new Promise(resolve=>release=resolve);
  return {...h.c.data,state:{...h.c.data.state,version:h.c.data.state.version+1}};
 };
 nativeChange('补充');nativeChange('联想');
 await Promise.resolve();await Promise.resolve();
 assert.deepEqual(h.calls,[['save','联想']]);
 assert.equal(h.c.executing,true);
 nativeChange('其他写法');release();await h.c.commandTail;
 assert.deepEqual(h.calls,[['save','联想'],['save','其他写法'],['render',3]]);
 assert.equal(h.c.dirty,false);assert.equal(h.c.executing,false);
});
test('P then W and Space waits for the pass save before selecting the writing style',async()=>{
 const h=groupHarness();let release,saves=0;
 h.c.save=async()=>{if(++saves===1)await new Promise(resolve=>release=resolve);h.c.dirty=false;};
 h.key('p');await Promise.resolve();await Promise.resolve();
 h.key('w');assert.equal(h.key(' ').prevented,true);
 assert.deepEqual(h.calls,[['n1','pass']]);
 release();await h.drain();
 assert.deepEqual(h.calls,[['n1','pass'],['style','补充']]);
 assert.equal(h.groups.style[0].checked,true);assert.equal(h.c.pendingGroupFocus,null);
});
test('rapid B Space F Enter applies following choice and N1 failure before attempting completion',async()=>{
 const h=groupHarness();let release;
 h.c.blocked=()=>new Promise(resolve=>release=resolve);
 vm.runInContext('enqueue(blocked)',h.c);await Promise.resolve();await Promise.resolve();
 h.c.save=async()=>{h.c.dirty=false;};
 h.c.completeCurrent=async()=>h.calls.push(['complete',h.groups.followingUse.find(el=>el.checked)?.value,h.groups.n1.find(el=>el.checked)?.value]);
 h.key('b');h.key(' ');h.key('f');h.key('Enter');release();await h.drain();
 assert.deepEqual(h.calls,[['followingUse','没用到'],['n1','fail'],['complete','没用到','fail']]);
});
test('queued group arrows select radio options but move checkbox focus without toggling',async()=>{
 const radio=groupHarness();radio.key('w');radio.key('ArrowRight');await radio.drain();
 assert.deepEqual(radio.calls.filter(c=>Array.isArray(c)),[['style','联想']]);
 const multi=groupHarness();multi.key('x');multi.key('ArrowRight');multi.key(' ');await multi.drain();
 assert.deepEqual(multi.calls.filter(c=>Array.isArray(c)),[['failure','下文马上讲了']]);
 assert.equal(multi.groups.failure[0].checked,false);assert.equal(multi.groups.failure[1].checked,true);
 for(const key of ['ArrowRight',' '])
  assert.equal(multi.key(key,{}, {matches:()=>true,closest:()=>null}).prevented,undefined);
});
test('switching cases clears stale pending group focus before the next item handles keys',async()=>{
 const h=postHarness();
 Object.assign(h.c,{boot:{record_ids:['r','next']},index:0,pendingGroupFocus:'style',tagMode:true,
  clock:0,performance:{now:()=>1},flush:async()=>{},render:()=>{},focusDecision:()=>{},
  requestAnimationFrame:()=>{},api:async()=>({state:{version:1,viewStep:0,ui:{readerScroll:0}},unit_note:''})});
 vm.runInContext(extract('  async function openCase(', '  function render('),h.c);
 await h.run('openCase(1)');
 assert.equal(h.c.pendingGroupFocus,null);assert.equal(h.c.tagMode,false);assert.equal(h.c.index,1);
});
test('first-pass evidence is omitted after locking while rewrite answer and text remain separate',()=>{
 const fields={paraphrase:{value:'不应回写的第一遍复述'},rewrite:{value:'这是一句改写'}};
 const c=vm.createContext({currentStep:()=>1,uiState:()=>({}),$:id=>fields[id],checked:()=>false,
  get:name=>({firstPass:'复述得出',rewriteChoice:'能改写得更直白'}[name]),
  data:{state:{record:{reading_difficulty:{first_pass:'复述不出或说偏',locked_at:'locked'},reason:'',uncovered_reason:''}}},
  host:{querySelector:()=>null}});
 vm.runInContext(extract('  function collect(', '  const currentStep'),c);
 const values=vm.runInContext('collect()',c);
 assert.equal('first_pass' in values,false);assert.equal('paraphrase' in values,false);
 assert.equal(values.rewrite,'能改写得更直白');assert.equal(values.rewrite_text,'这是一句改写');
});
test('unanswered veto checks stay unanswered instead of becoming false on save',()=>{
 for(const step of [3,4])for(const selected of [undefined,'false','true']) {
  const c=vm.createContext({currentStep:()=>step,$:()=>undefined,checked:()=>false,get:()=>selected,
   data:{state:{record:{reason:'',uncovered_reason:''}}},host:{querySelector:()=>null}});
  vm.runInContext(extract('  function collect(', '  const currentStep'),c);
  const values=vm.runInContext('collect()',c),key=step===3?'spoiler':'incorrect_information';
  assert.equal(key in values,selected!==undefined);
  if(selected!==undefined)assert.equal(values[key],selected==='true');
 }
});
test('P and F select explicit no and yes radio answers for each veto check',async()=>{
 for(const step of [3,4]) {
  const h=keyboardHarness(step);h.host.querySelector=selector=>({click:()=>h.calls.push(selector)});
  h.key('p');h.key('f');await h.drain();
  const name=step===3?'spoiler':'incorrect';
  assert.deepEqual(h.calls,[`[name="${name}"][value="false"]`,`[name="${name}"][value="true"]`]);
 }
});
test('submitted and legacy pending revisions require explicit discussion entry before edits',async()=>{
 for(const state of [{stage:7},{stage:6,discussionRequired:true}]) {
  const calls=[],notes={open:true},following=[{hidden:false},{hidden:false}],c=vm.createContext({data:{state},flush:async()=>calls.push('flush'),
   $:id=>id==='notes'?notes:null,host:{querySelectorAll:()=>following},
   post:async action=>calls.push(action),focusDecision:()=>calls.push('focus')});
  vm.runInContext(extract('  const isReadOnly', '  const currentId')+
   extract('  async function beginDiscussion(', '  async function completeCurrent('),c);
  assert.equal(vm.runInContext('isReadOnly()',c),true);
  await vm.runInContext('beginDiscussion()',c);
  assert.deepEqual(calls,['flush','begin_discussion','focus']);
  assert.equal(notes.open,false);assert.ok(following.every(el=>el.hidden));
 }
});
test('far-following confirmation follows successful protocol validation and only retries with acknowledgement',async()=>{
 const flag='far_following_without_spoiler';
 for(const [confirmed,acknowledged] of [[false,false],[true,false],[false,true]]) {
  const calls=[],c=vm.createContext({data:{state:{stage:6,record:{n1:{following_text_use:'更远后文，转第四步判剧透'},checks:{spoiler:false},acknowledged_warnings:acknowledged?[flag]:[]}}},
   currentStep:()=>6,isReadOnly:()=>false,interactionEpoch:0,index:0,collect:()=>({}),
   flush:async()=>{},post:async(action,values)=>{
    calls.push({action,...values});
    if(!acknowledged&&!values.acknowledge_far_following)throw Object.assign(new Error('确认组合'),{code:'FORM_VALIDATION',warning:flag});
   },focusDecision:()=>{},updateStatus:()=>{},
   window:{confirm:message=>{calls.push(message);return confirmed;}}});
  vm.runInContext(extract('  async function completeCurrent(', '  async function init('),c);
  await vm.runInContext('completeCurrent(false)',c);
  if(acknowledged)assert.deepEqual(calls,[{action:'submit'}]);
  else {
   assert.deepEqual(calls[0],{action:'submit'});
   assert.equal(calls[1],'N1 记了用到更远后文，但剧透判了没有，确认吗？');
   assert.equal(calls.length,confirmed?3:2);
   if(confirmed)assert.deepEqual(calls[2],{action:'submit',acknowledge_far_following:true});
  }
 }
});
test('missing discussion or conditional reasons fail before any far-following confirmation',async()=>{
 for(const message of ['讨论后改判必须写原因','其他写法必须说明写法及增量']) {
  const error=Object.assign(new Error(message),{code:'FORM_VALIDATION',step:6}),calls=[];
  const c=vm.createContext({data:{state:{record:{}}},currentStep:()=>6,isReadOnly:()=>false,interactionEpoch:0,index:0,
   collect:()=>({}),flush:async()=>{},post:async()=>{calls.push('submit');throw error;},
   window:{confirm:()=>{calls.push('unexpected confirm');return true;}},focusDecision:()=>calls.push('unexpected focus')});
  vm.runInContext(extract('  async function completeCurrent(', '  async function init('),c);
  await assert.rejects(vm.runInContext('completeCurrent(false)',c),e=>e===error);
  assert.deepEqual(calls,['submit']);
 }
});
test('cancelled warning keeps the draft available for retry and disk failure never advances',async()=>{
 const calls=[],warning=Object.assign(new Error('confirm'),{warning:'far_following_without_spoiler',code:'FORM_VALIDATION'}),diskError=new Error('disk failure');
 let accept=false;
 const c=vm.createContext({data:{state:{record:{}}},currentStep:()=>6,isReadOnly:()=>false,interactionEpoch:0,index:0,
  collect:()=>({amendment_reason:'说明'}),flush:async()=>{},updateStatus:()=>calls.push('status'),focusDecision:()=>calls.push('focus'),
  openCase:async()=>calls.push('unexpected navigation'),window:{confirm:()=>{calls.push('confirm');return accept;}},
  post:async(action,values)=>{calls.push(values.acknowledge_far_following?'retry':'submit');throw values.acknowledge_far_following?diskError:warning;}});
 vm.runInContext(extract('  async function completeCurrent(', '  async function init('),c);
 await vm.runInContext('completeCurrent(true)',c);
 assert.deepEqual(calls,['submit','confirm','status','focus']);
 calls.length=0;accept=true;
 await assert.rejects(vm.runInContext('completeCurrent(true)',c),e=>e===diskError);
 assert.deepEqual(calls,['submit','confirm','retry']);
});
test('warning rejection retains elapsed time for the single acknowledged submission',async()=>{
 const h=postHarness(),durations=[];
 Object.assign(h.c,{active:50,isReadOnly:()=>false,interactionEpoch:0,index:0,
  flush:async()=>{},focusDecision:()=>{},window:{confirm:()=>true}});
 h.c.data.state.viewStep=h.c.data.state.stage=6;
 h.c.elapsed=()=>{const duration=h.c.active;h.c.active=0;return duration;};
 h.c.api=async(path,body)=>{
  durations.push(body.active_ms);
  if(!body.values.acknowledge_far_following)throw Object.assign(new Error('确认组合'),{code:'FORM_VALIDATION',warning:'far_following_without_spoiler',actionApplied:false});
  return {...h.c.data,state:{...h.c.data.state,viewStep:7,stage:7,version:2}};
 };
 vm.runInContext(extract('  async function completeCurrent(', '  async function init('),h.c);
 await h.run('completeCurrent(false)');
 assert.deepEqual(durations,[50,50]);assert.equal(h.c.active,0);
});
test('Enter browsing a submitted step navigates without completing or revising it',async()=>{
 const calls=[],c=vm.createContext({data:{state:{stage:7,record:{}}},currentStep:()=>2,isReadOnly:()=>true,
  interactionEpoch:0,index:0,flush:async()=>{},inspect:async step=>calls.push(['navigate',step]),
  post:async()=>calls.push('unexpected write')});
 vm.runInContext(extract('  async function completeCurrent(', '  async function init('),c);
 await vm.runInContext('completeCurrent(false)',c);assert.deepEqual(calls,[['navigate',3]]);
});
test('legacy difficulty display distinguishes initial evidence from later cross-category changes',()=>{
 const h=harness();
 for(const [initial,final,firstPass] of [['一遍能复述','能改写得更直白','复述得出'],['改写不出','一遍能复述','复述不出或说偏']]) {
  const legacy={original_choice:initial,choice:final,paraphrase:'旧文本',rewrite:'旧改写'};
  h.c.legacy=legacy;
  const result=h.run('difficultyView(legacy)'),text=h.run('difficultySummary(legacy)');
  assert.equal(result.first_pass,firstPass);assert.equal(result.rewrite_text,'旧改写');
  assert.match(text,/旧版最初：.*最终：.*第一遍未独立记录/);
  assert.equal(result.rewrite,final==='一遍能复述'?null:final);
  assert.deepEqual(legacy,{original_choice:initial,choice:final,paraphrase:'旧文本',rewrite:'旧改写'});
 }
 h.c.legacy={choice:'能改写得更直白'};
 assert.equal(h.run('difficultyView(legacy).first_pass'),null);
});
test('readonly tags do not enter a mode that intercepts numeric step navigation',async()=>{
 const h=keyboardHarness(7);h.c.data.state.viewStep=6;
 h.key('t');h.key('5');await h.drain();
 assert.equal(h.c.tagMode,false);assert.deepEqual(h.calls,[['navigate',4]]);
});
test('changing the unlocked first answer to understood explicitly clears a stale rewrite answer',()=>{
 const fields={paraphrase:{value:'复述'},rewrite:{value:'旧改写'}};
 const c=vm.createContext({currentStep:()=>1,$:id=>fields[id],checked:()=>false,
  get:name=>({firstPass:'复述得出',rewriteChoice:'能改写得更直白'}[name]),
  data:{state:{record:{reading_difficulty:{first_pass:'复述不出或说偏'},reason:'',uncovered_reason:''}}},host:{querySelector:()=>null}});
 vm.runInContext(extract('  function collect(', '  const currentStep'),c);
 const values=vm.runInContext('collect()',c);
 assert.equal(values.first_pass,'复述得出');assert.equal(values.rewrite,null);
});
test('legacy readonly difficulty renders old answers and text without inventing two independent observations',()=>{
 const start=src.indexOf('    if (s === 1) {',src.indexOf('    const spec = boot.form.steps[s];'));
 const call=src.slice(start,src.indexOf('    if (s === 2) {',start)),calls=[];
 const c=vm.createContext({s:1,r:{reading_difficulty:{original_choice:'改写不出',choice:'一遍能复述',paraphrase:'旧复述',rewrite:'旧改写'}},
  w:{append:value=>calls.push(value)},node:(tag,text)=>({tag,text}),
  textArea:(w,id,label,value)=>calls.push({id,label,value}),radios:()=>{throw Error('legacy must not render v2 observations');}});
 vm.runInContext(extract('  const difficultyLabel','  function stepHint(')+call,c);
 assert.match(calls[0].text,/旧版最初.*最终.*第一遍未独立记录/);
 assert.deepEqual(calls.slice(1).map(x=>x.value),['旧复述','旧改写']);
});
