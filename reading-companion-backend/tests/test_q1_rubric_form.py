from copy import deepcopy

import pytest

from scripts.q1_rubric_form import load_form, validate_form, validate_assessment
from scripts.q1_comparison import build_bundle
from scripts.q1_comparison_fixture import synthetic_inputs
from scripts.q1_comparison_stats import validate_rows
from tests.test_q1_comparison_stats import record


def review_row(kind='N'):
    _, mixed, _ = build_bundle(*synthetic_inputs())
    w, m = next((w, m) for w in mixed['windows'] for m in w['marginalia'] if m['type'] == kind)
    form, digest = load_form('q1-v0.form.v1')
    row = record(mixed, w, m, schema='q1-mixed-judgment/2', annotator_version='q1-annotator/2.3',
                 rubric_version=form['rubric_version'], rubric_sha256=form['rubric_sha256'],
                 rubric_form_version=form['form_version'], rubric_form_sha256=digest,
                 review_session_id='synthetic-review', failed_criteria=[], tags=[], criterion_flags={},
                 rubric_uncovered=False, review_completed=True, prior_judgment_seen=False)
    return mixed, row, form


@pytest.mark.parametrize('version', ['q1-annotator/2.3', 'q1-annotator/2.4', 'q1-annotator/2.5'])
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


def test_future_form_ids_work_without_code_change():
    _, row, form = review_row('H')
    form = deepcopy(form)
    form['mark_types']['H']['criteria'][0]['id'] = 'future-criterion'
    validate_form(form)
    row.update(failed_criteria=['future-criterion'], judgment='fail')
    validate_assessment(row, form)
