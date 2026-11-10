"""Offline form identity and completed rubric-assessment validation."""
import json
import re

from scripts.check_iteration_provenance import BACKEND, rubric_identity, sha

IDENTITY_FIELDS = {'rubric_form_version', 'rubric_form_sha256', 'review_session_id'}
ASSESSMENT_FIELDS = {'failed_criteria', 'tags', 'criterion_flags', 'rubric_uncovered',
                     'review_completed', 'prior_judgment_seen'}
STEP_FIELDS = {'criterion_assessments', 'uncovered_reason'}
REVIEW_SCHEMAS = {'q1-mixed-judgment/2', 'q1-mixed-judgment/3'}
REVIEW_FIELDS = IDENTITY_FIELDS | ASSESSMENT_FIELDS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_form(form):
    require(set(form) == {'schema', 'form_version', 'rubric_version', 'rubric_sha256',
                         'title', 'protocol_notes', 'policy', 'mark_types'}, 'Invalid form fields')
    require(form['schema'] == 'q1-rubric-form/1', 'Unsupported form schema')
    for key in ('form_version', 'rubric_version', 'title'):
        require(isinstance(form[key], str) and bool(form[key].strip()), 'Invalid form identity')
    require(bool(re.fullmatch(r'[a-f0-9]{64}', form['rubric_sha256'])), 'Invalid rubric hash')
    require(isinstance(form['protocol_notes'], list) and all(isinstance(x, str) for x in form['protocol_notes']), 'Invalid protocol notes')
    policy = form['policy']
    require(set(policy) == {'reason_required_on_fail', 'omissions_enabled', 'star_requires_pass', 'uncovered_fails', 'explicit_completion'}
            and all(type(x) is bool for x in policy.values()), 'Invalid form policy')
    require(not policy['omissions_enabled'] and policy['explicit_completion'] and policy['uncovered_fails'], 'Unsupported review policy')
    require(set(form['mark_types']) == {'N', 'H'}, 'Invalid mark types')
    for spec in form['mark_types'].values():
        require(set(spec) == {'label', 'criteria', 'tags'} and isinstance(spec['label'], str), 'Invalid type specification')
        require(isinstance(spec['criteria'], list) and spec['criteria'] and isinstance(spec['tags'], list), 'Missing criteria/tags')
        ids = []
        for c in spec['criteria']:
            require(set(c) == {'id', 'label', 'help', 'flags'} and all(isinstance(c[k], str) and c[k].strip() for k in ('id','label','help')) and isinstance(c['flags'], list), 'Invalid criterion')
            ids.append(c['id'])
            flags = []
            for flag in c['flags']:
                require(set(flag) == {'id','label','compatibility_field'} and isinstance(flag['id'], str) and flag['id'] and isinstance(flag['label'], str) and flag['label'] and flag['compatibility_field'] == 'needs_verification', 'Invalid criterion flag')
                flags.append(flag['id'])
            require(len(flags) == len(set(flags)), 'Duplicate criterion flag')
        for tag in spec['tags']:
            require(set(tag) == {'id','label'} and all(isinstance(v, str) and v.strip() for v in tag.values()), 'Invalid tag')
            ids.append(tag['id'])
        require(len(ids) == len(set(ids)), 'Duplicate criterion/tag ID')
    return form


def load_form(version, root=BACKEND):
    release = json.loads((root / 'rubric/form-releases.json').read_text())[version]
    path = (root / release['path']).resolve()
    require(path.is_relative_to((root / 'rubric').resolve()), 'Form path outside rubric')
    require(sha(path) == release['sha256'], 'Form fingerprint changed')
    form = validate_form(json.loads(path.read_text()))
    identity = rubric_identity(form['rubric_version'], root)
    require(form['form_version'] == version and form['rubric_version'] == release['rubric_version']
            and form['rubric_sha256'] == release['rubric_sha256'] == identity['rubric_sha256'], 'Form/rubric identity mismatch')
    return form, release['sha256']


def validate_assessment(row, form):
    """Validate derived outcome, allowed choices, and all optional flag mirrors."""
    stepwise = row.get('schema') == 'q1-mixed-judgment/3'
    fields = ASSESSMENT_FIELDS | (STEP_FIELDS if stepwise else set())
    require(IDENTITY_FIELDS | fields <= row.keys(), 'Missing review fields')
    require(isinstance(row['review_session_id'], str) and bool(re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', row['review_session_id'])), 'Invalid review session')
    if row['record_type'] != 'marginalia':
        require(row['record_type'] == 'unit_note' and all(row[k] is None for k in fields), 'Rubric review does not record omissions')
        return
    spec = form['mark_types'][row['type']]
    for field, allowed in [('failed_criteria', {c['id'] for c in spec['criteria']}), ('tags', {t['id'] for t in spec['tags']})]:
        values = row[field]
        require(isinstance(values, list) and all(isinstance(v, str) for v in values)
                and len(values) == len(set(values)) and set(values) <= allowed, 'Invalid rubric choices')
    if stepwise:
        assessments = row['criterion_assessments']
        require(isinstance(assessments, dict) and set(assessments) == {c['id'] for c in spec['criteria']}, 'Missing/unknown criterion assessment')
        require(all(isinstance(a, dict) and set(a) == {'judgment', 'reason'} and a['judgment'] in ('pass', 'fail') and isinstance(a['reason'], str) for a in assessments.values()), 'Invalid/unjudged criterion assessment')
        require(isinstance(row['uncovered_reason'], str), 'Invalid uncovered reason')
        require(set(row['failed_criteria']) == {cid for cid, a in assessments.items() if a['judgment'] == 'fail'}, 'Failed criteria mismatch')
    flags = row['criterion_flags']
    require(isinstance(flags, dict), 'Invalid criterion flags')
    verified = False
    for cid, values in flags.items():
        criterion = next((c for c in spec['criteria'] if c['id'] == cid), None)
        require(criterion is not None and isinstance(values, dict), 'Unknown flagged criterion')
        allowed = {f['id'] for f in criterion['flags']}
        require(set(values) <= allowed and all(type(v) is bool for v in values.values()), 'Unknown/nonboolean flag')
        verified |= any(values.values())
    require(all(type(row[k]) is bool for k in ('rubric_uncovered','review_completed','prior_judgment_seen','star','needs_verification')), 'Invalid review booleans')
    require(row['review_completed'], 'Unconfirmed draft cannot enter journal')
    expected = 'fail' if row['failed_criteria'] or row['rubric_uncovered'] else 'pass'
    require(row['judgment'] == expected, 'Derived judgment mismatch')
    require(row['needs_verification'] == verified, 'Verification mirror mismatch')
    require(not row['star'] or not form['policy']['star_requires_pass'] or expected == 'pass', 'A failing annotation cannot be starred')
    require(isinstance(row['reason'], str) and isinstance(row['remarks'], str), 'Invalid review text')
    reasons_present = (all(row['criterion_assessments'][cid]['reason'].strip() for cid in row['failed_criteria']) and (not row['rubric_uncovered'] or row['uncovered_reason'].strip())) if stepwise else row['reason'].strip()
    require(expected != 'fail' or not form['policy']['reason_required_on_fail'] or reasons_present, 'Failure reason required')


def check_forms(root=BACKEND):
    registry = root / 'rubric/form-releases.json'
    if registry.exists():
        for version in json.loads(registry.read_text()):
            load_form(version, root)
