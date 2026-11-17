const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const src = fs.readFileSync(__dirname+'/q1-note-annotator.js','utf8');
function extract(start,end) {return src.slice(src.indexOf(start),src.indexOf(end));}
function harness(width=1200) {
  const nodes=new Map();
  const get=id=> {
    if(!nodes.has(id)) nodes.set(id,{hidden:false,textContent:'',scrollTop:80,clientHeight:400,
      getBoundingClientRect:()=>({top:100}),querySelector:()=>null,
      scrollIntoView(opts){this.scrolled=opts;},focus(opts){this.focused=opts;}});
    return nodes.get(id);
  };
  const c=vm.createContext({$:get,innerWidth:width});
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
