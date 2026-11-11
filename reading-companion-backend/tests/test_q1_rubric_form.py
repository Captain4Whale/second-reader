from copy import deepcopy

import pytest

from scripts.q1_rubric_form import load_form, validate_form, validate_assessment
from scripts.q1_comparison import build_bundle
from scripts.q1_comparison_fixture import synthetic_inputs
from scripts.q1_comparison_stats import validate_rows
from tests.test_q1_comparison_stats import record


def review_row(kind='N', form_version='q1-v0.form.v1'):
    _, mixed, _ = build_bundle(*synthetic_inputs())
    w, m = next((w, m) for w in mixed['windows'] for m in w['marginalia'] if m['type'] == kind)
    form, digest = load_form(form_version)
    row = record(mixed, w, m, schema='q1-mixed-judgment/2', annotator_version='q1-annotator/2.3',
                 rubric_version=form['rubric_version'], rubric_sha256=form['rubric_sha256'],
                 rubric_form_version=form['form_version'], rubric_form_sha256=digest,
                 review_session_id='synthetic-review', failed_criteria=[], tags=[], criterion_flags={},
                 rubric_uncovered=False, review_completed=True, prior_judgment_seen=False)
    return mixed, row, form


@pytest.mark.parametrize('version', ['q1-annotator/2.3', 'q1-annotator/2.4', 'q1-annotator/2.5', 'q1-annotator/2.6', 'q1-annotator/3.0', 'q1-annotator/3.1', 'q1-annotator/3.2'])
def test_failure_reason_optional_tags_and_verification_do_not_fail(version):
    mixed, row, form = review_row()
    row['annotator_version'] = version
    row.update(tags=['redundancy'], criterion_flags={'N2':{'needs_verification':True}}, needs_verification=True)
    validate_rows([row], mixed)
    row.update(failed_criteria=['N1','N4'], judgment='fail', reason='')
    validate_rows([row], mixed)
    row.update(failed_criteria=[], rubric_uncovered=True)
    validate_rows([row], mixed)


@pytest.mark.parametrize('changes', [
    {'failed_criteria':['H1']}, {'failed_criteria':['N1','N1']}, {'tags':['unknown']},
    {'criterion_flags':{'N1':{'needs_verification':True}}}, {'needs_verification':True},
    {'rubric_uncovered':True}, {'review_completed':False},
    {'failed_criteria':['N1'],'judgment':'fail','star':True},
    {'prior_judgment_seen':True}, {'rubric_form_sha256':'f'*64},
    {'record_type':'omission'}, {'review_session_id':'../other'},
])
def test_invalid_or_unconfirmed_review_rejected(changes):
    mixed, row, _ = review_row()
    row.update(changes)
    with pytest.raises((ValueError, KeyError)):
        validate_rows([row], mixed)


def test_exposure_monotonic_and_journals_isolated():
    mixed, row, _ = review_row()
    seen = {**row, 'revision':2, 'prior_judgment_seen':True}
    validate_rows([row, seen], mixed)
    with pytest.raises(ValueError, match='exposure'):
        validate_rows([row, seen, {**row,'revision':3}], mixed)
    with pytest.raises(ValueError, match='isolated'):
        validate_rows([row, {**row,'revision':2,'review_session_id':'other'}], mixed)


def test_published_v1_is_a_separate_scope_despite_shared_criterion_ids():
    mixed, old, old_form = review_row()
    form, digest = load_form('q1-v1.form.v1')
    new = {**old, 'rubric_version': form['rubric_version'],
           'rubric_sha256': form['rubric_sha256'],
           'rubric_form_version': form['form_version'], 'rubric_form_sha256': digest}
    validate_rows([new], mixed)
    assert form['policy'] == old_form['policy']
    assert form['mark_types']['N']['criteria'][1]['label'] == '准确'
    assert form['mark_types']['N']['criteria'][1]['flags'] == old_form['mark_types']['N']['criteria'][1]['flags']
    for kind in ('N', 'H'):
        assert form['mark_types'][kind]['tags'] == old_form['mark_types'][kind]['tags']
        assert [c['id'] for c in form['mark_types'][kind]['criteria']] == [c['id'] for c in old_form['mark_types'][kind]['criteria']]
    with pytest.raises(ValueError, match='isolated'):
        validate_rows([old, {**new, 'revision': 2}], mixed)


def test_future_form_ids_work_without_code_change():
    _, row, form = review_row('H')
    form = deepcopy(form)
    form['mark_types']['H']['criteria'][0]['id'] = 'future-criterion'
    validate_form(form)
    row.update(failed_criteria=['future-criterion'], judgment='fail')
    validate_assessment(row, form)


def step_row(kind='N'):
    mixed, row, form = review_row(kind)
    row.update(schema='q1-mixed-judgment/3', annotator_version='q1-annotator/3.0',
               criterion_assessments={c['id']: {'judgment': 'pass', 'reason': ''} for c in form['mark_types'][kind]['criteria']},
               uncovered_reason='')
    return mixed, row, form


@pytest.mark.parametrize('kind', ['N', 'H'])
@pytest.mark.parametrize('version', ['q1-annotator/3.0', 'q1-annotator/3.1', 'q1-annotator/3.2'])
def test_explicit_complete_assessments_and_legacy_prefix(kind, version):
    mixed, row, form = step_row(kind)
    row['annotator_version'] = version
    validate_rows([row], mixed)
    first = next(iter(row['criterion_assessments']))
    row['criterion_assessments'][first] = {'judgment': 'fail', 'reason': '  本项\n理由  '}
    row.update(failed_criteria=[first], judgment='fail', reason='旧版整体理由', uncovered_reason='独立说明')
    validate_rows([row], mixed)
    old = {k: deepcopy(v) for k, v in row.items() if k not in ('criterion_assessments', 'uncovered_reason')}
    old.update(schema='q1-mixed-judgment/2', annotator_version='q1-annotator/2.5')
    row['revision'] = 2
    validate_rows([old, row], mixed)
    assert row['criterion_assessments'][first]['reason'] == '  本项\n理由  '


@pytest.mark.parametrize('change', [
    'missing', 'unknown', 'unjudged', 'reason_type', 'extra_field', 'mismatch',
    'uncovered_type', 'wrong_version', 'star_fail',
])
def test_stepwise_bad_shapes_rejected(change):
    mixed, row, _ = step_row()
    a = row['criterion_assessments']
    if change == 'missing':
        del a['N1']
    elif change == 'unknown':
        a['H1'] = a.pop('N1')
    elif change == 'unjudged':
        a['N1']['judgment'] = None
    elif change == 'reason_type':
        a['N1']['reason'] = 123
    elif change == 'extra_field':
        a['N1']['model'] = 'not allowed'
    elif change == 'mismatch':
        row['failed_criteria'] = ['N1']
    elif change == 'uncovered_type':
        row['uncovered_reason'] = None
    elif change == 'wrong_version':
        row['annotator_version'] = 'q1-annotator/2.5'
    elif change == 'star_fail':
        row.update(star=True, rubric_uncovered=True, judgment='fail')
    with pytest.raises(ValueError):
        validate_rows([row], mixed)
