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
