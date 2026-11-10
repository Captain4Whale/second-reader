/* Pure rubric rules shared by the browser and offline UI tests. No I/O or provenance. */
(function (root) {
  "use strict";
  const identityFields = ["rubric_form_version", "rubric_form_sha256", "review_session_id"];
  const assessmentFields = ["failed_criteria", "tags", "criterion_flags", "rubric_uncovered", "review_completed", "prior_judgment_seen"];
  const stepFields = ["criterion_assessments", "uncovered_reason"];
  const isReviewSchema = schema => ["q1-mixed-judgment/2", "q1-mixed-judgment/3"].includes(schema);
  const fieldsFor = schema => schema === "q1-mixed-judgment/3" ? [...assessmentFields,...stepFields] : assessmentFields;
  const explicit = v => object(v.criterion_assessments);
  const failed = v => Object.entries(v.criterion_assessments).filter(([,a])=>a.judgment === "fail").map(([id])=>id);
  const complete = (v, spec) => explicit(v) && spec.criteria.every(c=>["pass","fail"].includes(v.criterion_assessments[c.id]?.judgment));
  function stepDraft(v, spec, restart = false) {
    return {...v, criterion_assessments: Object.fromEntries(spec.criteria.map(c=>[c.id,
      !restart && explicit(v) && v.criterion_assessments[c.id]
        ? {...v.criterion_assessments[c.id]}
        : {judgment:!restart && v.failed_criteria?.includes(c.id) ? "fail" : null, reason:""}])),
      uncovered_reason:v.uncovered_reason ?? "", review_completed:false,
      star:!restart && complete(v,spec) ? v.star : false};
  }
  const require = (ok, message) => { if (!ok) throw Error(message); };
  const object = v => !!v && typeof v === "object" && !Array.isArray(v);
  const exact = (v, keys) => object(v) && Object.keys(v).sort().join("|") === [...keys].sort().join("|");
  const text = v => typeof v === "string" && !!v.trim();
  const hash = v => typeof v === "string" && /^[a-f0-9]{64}$/.test(v);
  function validateForm(f) {
    require(exact(f, ["schema","form_version","rubric_version","rubric_sha256","title","protocol_notes","policy","mark_types"]) && f.schema === "q1-rubric-form/1", "表单格式不支持。");
    require([f.form_version,f.rubric_version,f.title].every(text) && hash(f.rubric_sha256), "表单身份无效。");
    require(Array.isArray(f.protocol_notes) && f.protocol_notes.every(v => typeof v === "string"), "表单协议说明无效。");
    require(exact(f.policy, ["reason_required_on_fail","omissions_enabled","star_requires_pass","uncovered_fails","explicit_completion"]) && Object.values(f.policy).every(v => typeof v === "boolean"), "表单规则无效。");
    require(!f.policy.omissions_enabled && f.policy.explicit_completion && f.policy.uncovered_fails, "本重判模式不支持此表单规则。");
    require(exact(f.mark_types, ["N","H"]), "表单缺少批注类型。");
    for (const spec of Object.values(f.mark_types)) {
      require(exact(spec,["label","criteria","tags"]) && text(spec.label) && Array.isArray(spec.criteria) && spec.criteria.length && Array.isArray(spec.tags), "表单条目无效。");
      const ids = [];
      for (const c of spec.criteria) {
        require(exact(c,["id","label","help","flags"]) && [c.id,c.label,c.help].every(text) && Array.isArray(c.flags), "判定条目无效。");
        ids.push(c.id);
        const flags = [];
        for (const flag of c.flags) {
          require(exact(flag,["id","label","compatibility_field"]) && [flag.id,flag.label].every(text) && flag.compatibility_field === "needs_verification", "条目标记无效。");
          flags.push(flag.id);
        }
        require(new Set(flags).size === flags.length, "条目标记重复。");
      }
      for (const tag of spec.tags) {
        require(exact(tag,["id","label"]) && [tag.id,tag.label].every(text), "标签无效。");
        ids.push(tag.id);
      }
      require(new Set(ids).size === ids.length, "表单条目或标签 ID 重复。");
    }
    return f;
  }
  const outcome = v => (explicit(v) ? failed(v).length : v.failed_criteria.length) || v.rubric_uncovered ? "fail" : "pass";
  const verification = v => Object.values(v.criterion_flags).some(flags => Object.values(flags).some(Boolean));
  const empty = () => ({ failed_criteria:[], tags:[], criterion_flags:{}, rubric_uncovered:false, review_completed:false, prior_judgment_seen:false });
  function validateAssessment(r, f) {
    const fields = fieldsFor(r.schema);
    require([...identityFields,...fields].every(k => Object.hasOwn(r,k)), "缺少重判字段。");
    require(typeof r.review_session_id === "string" && /^[a-zA-Z0-9_-]{1,100}$/.test(r.review_session_id), "重判会话无效。");
    if (r.record_type !== "marginalia") {
      require(r.record_type === "unit_note" && fields.every(k => r[k] === null), "本次重判不记录漏标。");
      return;
    }
    const spec = f.mark_types[r.type];
    require(!!spec, "批注类型无效。");
    for (const [field, allowed] of [["failed_criteria",spec.criteria.map(c=>c.id)],["tags",spec.tags.map(t=>t.id)]]) {
      const values = r[field];
      require(Array.isArray(values) && values.every(v => typeof v === "string" && allowed.includes(v)) && new Set(values).size === values.length, "勾选项不属于本批注类型或存在重复。");
    }
    if (r.schema === "q1-mixed-judgment/3") {
      require(exact(r.criterion_assessments, spec.criteria.map(c=>c.id)), "逐项判定必须覆盖全部条件。");
      require(Object.values(r.criterion_assessments).every(a=>exact(a,["judgment","reason"]) && ["pass","fail"].includes(a.judgment) && typeof a.reason === "string"), "逐项判定或理由无效。");
      require(typeof r.uncovered_reason === "string", "未覆盖说明无效。");
      require(JSON.stringify([...failed(r)].sort()) === JSON.stringify([...r.failed_criteria].sort()), "失败条件与逐项判定不一致。");
    }
    require(object(r.criterion_flags), "条目标记无效。");
    for (const [cid, values] of Object.entries(r.criterion_flags)) {
      const c = spec.criteria.find(c => c.id === cid);
      require(c && object(values) && Object.entries(values).every(([k,v]) => c.flags.some(f=>f.id===k) && typeof v === "boolean"), "存在未知条目标记。");
    }
    require(["rubric_uncovered","review_completed","prior_judgment_seen","star","needs_verification"].every(k=>typeof r[k]==="boolean") && r.review_completed, "未确认的草稿不能写入重判日志。");
    require(r.judgment === outcome(r) && r.needs_verification === verification(r), "自动判定或待核实字段不一致。");
    require(!r.star || !f.policy.star_requires_pass || r.judgment === "pass", "不过的批注不能标星。");
    require(typeof r.reason === "string" && typeof r.remarks === "string" && (r.judgment !== "fail" || !f.policy.reason_required_on_fail || (r.schema === "q1-mixed-judgment/3" ? failed(r).every(id=>r.criterion_assessments[id].reason.trim()) && (!r.rubric_uncovered || r.uncovered_reason.trim()) : r.reason.trim())), "理由或备注无效。");
  }
  function scopeKey(batchId, context) {
    return context?.review_session_id
      ? "review:" + JSON.stringify([batchId,context.annotator_id,context.rubric_version,context.rubric_sha256,context.rubric_form_version,context.rubric_form_sha256,context.review_session_id])
      : batchId;
  }
  const api = {stepFields, isReviewSchema, fieldsFor, explicit, failed, complete, stepDraft, identityFields, assessmentFields, reviewFields:[...identityFields,...assessmentFields], validateForm, validateAssessment, outcome, verification, empty, scopeKey};
  root.Q1Rubric = api;
  if (typeof module !== "undefined") module.exports = api;
})(globalThis);
