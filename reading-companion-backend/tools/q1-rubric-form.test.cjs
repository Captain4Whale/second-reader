const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const rules = require('./q1-rubric-form.js');
const form = JSON.parse(fs.readFileSync(__dirname+'/../rubric/q1-v0.form.json','utf8'));
function row() { return {...rules.empty(),record_type:'marginalia',type:'N',rubric_form_version:form.form_version,rubric_form_sha256:'a'.repeat(64),review_session_id:'test',review_completed:true,judgment:'pass',needs_verification:false,star:false,reason:'',remarks:''}; }
test('form-driven outcomes, tags, optional reason and uncovered',()=>{
  rules.validateForm(form);
  let r = row(); r.tags=['redundancy']; rules.validateAssessment(r,form);
  r.failed_criteria=['N1','N4'];r.judgment=rules.outcome(r);rules.validateAssessment(r,form);
  r.failed_criteria=[];r.rubric_uncovered=true;rules.validateAssessment(r,form);
  r.rubric_uncovered=false;r.judgment='pass';r.criterion_flags={N2:{needs_verification:true}};r.needs_verification=rules.verification(r);rules.validateAssessment(r,form);
});
test('wrong type, duplicates, unconfirmed, mirror and star contradictions reject',()=>{
  for (const patch of [{failed_criteria:['H1']},{tags:['redundancy','redundancy']},{review_completed:false},{needs_verification:true},{failed_criteria:['N1'],judgment:'fail',star:true}]) assert.throws(()=>rules.validateAssessment({...row(),...patch},form));
});
test('review cache scope cannot collide with legacy, another user, form or session',()=>{
  const c={annotator_id:'weijiang',rubric_version:'q1-v0',rubric_sha256:'r',rubric_form_version:'v',rubric_form_sha256:'f',review_session_id:'one'};
  const keys=[rules.scopeKey('batch',null),rules.scopeKey('batch',c),...Object.keys(c).map(k=>rules.scopeKey('batch',{...c,[k]:'other'}))];
  assert.equal(new Set(keys).size,keys.length);
});

function stepRow(kind='N') {
  const r = {...row(),schema:'q1-mixed-judgment/3',type:kind,uncovered_reason:''};
  r.criterion_assessments=Object.fromEntries(form.mark_types[kind].criteria.map(c=>[c.id,{judgment:'pass',reason:''}]));
  return r;
}
test('explicit all-pass, multifail and independent reasons validate; legacy reason stays independent',()=>{
  for(const kind of ['N','H']) {
    const r=stepRow(kind);rules.validateAssessment(r,form);
    const id=form.mark_types[kind].criteria[0].id;
    r.criterion_assessments[id]={judgment:'fail',reason:'  independent\n理由  '};
    r.failed_criteria=rules.failed(r);r.judgment=rules.outcome(r);r.reason='legacy whole-case reason';
    rules.validateAssessment(r,form);assert.equal(r.criterion_assessments[id].reason,'  independent\n理由  ');
  }
});
test('unjudged/missing/extra/wrong-type assessments and mismatched derived failures reject',()=>{
  for(const mutate of [r=>r.criterion_assessments.N1.judgment=null,r=>delete r.criterion_assessments.N2,
    r=>r.criterion_assessments.H1={judgment:'pass',reason:''},r=>r.criterion_assessments.N1.reason=2,
    r=>r.failed_criteria=['N1'],r=>r.uncovered_reason=null,r=>r.criterion_assessments.N1.extra=true]) {
    const r=stepRow();mutate(r);assert.throws(()=>rules.validateAssessment(r,form));
  }
});
test('legacy draft retains explicit failures, reasons and flags without inventing passes',()=>{
  const old={...row(),failed_criteria:['N2'],reason:'overall',review_completed:false,criterion_flags:{N2:{needs_verification:true}}};
  const d=rules.stepDraft(old,form.mark_types.N);
  assert.equal(d.criterion_assessments.N2.judgment,'fail');assert.equal(d.criterion_assessments.N1.judgment,null);
  assert.equal(d.reason,'overall');assert.equal(d.criterion_assessments.N2.reason,'');assert.equal(rules.complete(d,form.mark_types.N),false);
  const restarted=rules.stepDraft({...old,review_completed:true},form.mark_types.N,true);
  assert.ok(Object.values(restarted.criterion_assessments).every(a=>a.judgment===null));
  assert.equal(old.criterion_assessments,undefined);
  assert.equal(rules.stepDraft({...old,star:true},form.mark_types.N).star,false);
});
