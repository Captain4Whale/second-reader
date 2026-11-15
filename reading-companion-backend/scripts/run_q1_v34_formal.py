#!/usr/bin/env python3
"""Isolated high diagnostic and serial, frozen 26-unit v3.4 validation run.

No annotation judgments are read. Raw text and stability identities stay in state/.
Existing output directories refuse regeneration; failure requires operator review.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import re
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
from eval.attentional_v2.fixed_history_digest import HistoricalRun, canonical, read, render_packet, run_digest, sha, write
from scripts.run_fixed_history_a1 import validate_marks
from scripts.run_q1_v34_pilot import MODEL, PROMPT, SAMPLING, stability_sample
from src.attentional_v2.llm_output_tools import validate_digest_result

ROOT = BACKEND / 'state/experiments/Q1-RUBRIC-V34-VALIDATION-001'
FORMAL = ROOT / 'formal'
DIAGNOSTIC = ROOT / 'diagnostic-high'
SERIES = 'Q1-RUBRIC-V34-VALIDATION-001'


def now():
    return datetime.now(timezone.utc).isoformat()


def status(root, phase, **kw):
    (root / 'status.json').write_text(json.dumps({'phase': phase, 'updated_at': now(), **kw}, ensure_ascii=False, indent=2) + '\n')


def registered_manifest():
    rows = [json.loads(l) for l in (BACKEND / 'experiments/log.jsonl').read_text().splitlines()]
    prereg = next(r for r in rows if r['experiment_id'] == SERIES + '-PREREG-001')
    for field in ['unit_set', 'acceptance_unit_set', 'sampling_manifest']:
        ref = prereg[field]
        if sha((BACKEND / ref['path']).read_bytes()) != ref['sha256']:
            raise ValueError('Registered manifest changed: ' + field)
    manifest = read(BACKEND / prereg['unit_set']['path'])
    if Counter(u['book'] for u in manifest['units']) != {'bovary': 13, 'sapiens': 13}:
        raise ValueError('Formal scope must be exactly 13 + 13')
    return manifest


def normalization_difference(raw, normalized, field):
    """Record exact differences privately; accept only existing whitespace rules."""
    if raw == normalized:
        return None
    if raw is None and normalized == '' and field.endswith('.content'):
        return {'field': field, 'rule': 'highlight_null_to_empty', 'raw': None, 'normalized': ''}
    if not isinstance(raw, str) or re.sub(r'\s+', ' ', raw).strip() != normalized:
        raise ValueError('Unexpected non-whitespace normalization: ' + field)
    edits = []
    for op, a, b, c, d in difflib.SequenceMatcher(None, raw, normalized, autojunk=False).get_opcodes():
        if op != 'equal':
            removed, added = raw[a:b], normalized[c:d]
            if any(not ch.isspace() for ch in removed + added):
                raise ValueError('Non-whitespace edit: ' + field)
            edits.append({'operation': op, 'raw_range': [a, b], 'normalized_range': [c, d],
                          'removed_codepoints': [f'U+{ord(ch):04X}' for ch in removed],
                          'added_codepoints': [f'U+{ord(ch):04X}' for ch in added]})
    return {'field': field, 'rule': 'existing_clean_text_whitespace', 'raw': raw, 'normalized': normalized,
            'raw_characters': len(raw), 'normalized_characters': len(normalized),
            'raw_utf8_bytes': len(raw.encode()), 'normalized_utf8_bytes': len(normalized.encode()), 'edits': edits}


def audit(directory, history, packet, result, effort):
    expected_sampling = {**SAMPLING, 'reasoning_effort': effort}
    if result['sampling'] != expected_sampling or result['model'] != MODEL or result['prompt_version'] != PROMPT:
        raise ValueError('Configuration differs from authorization')
    history.verify_memory_selection(packet)
    if read(directory / 'input.json') != packet:
        raise ValueError('Stored input changed')
    system, user = render_packet(packet, PROMPT)
    if read(directory / 'rendered.json') != {'system_prompt': system, 'user_prompt': user, 'reconstructed': True}:
        raise ValueError('Frozen prompt differs')
    requests = sorted((directory / 'actual').glob('request-*.json'))
    responses = sorted((directory / 'actual').glob('response-*.json'))
    if len(requests) != len(responses):
        raise ValueError('Incomplete response capture')
    calls = result['calls']
    if {sha(canonical(read(p))) for p in requests} != {c['request_sha256'] for c in calls}:
        raise ValueError('Logical request hashes differ')
    first = read(requests[0])
    if first['messages'][:2] != [{'role': 'system', 'content': system}, {'role': 'human', 'content': user}]:
        raise ValueError('Actual prompt differs from frozen rendering')
    attempts = []
    for p in responses:
        response = read(p)
        usage = response.get('usage_metadata') or {}
        if response.get('model_name') != MODEL:
            raise ValueError('Unexpected returned model')
        if usage.get('input_tokens') is None or usage.get('output_tokens') is None:
            raise ValueError('Missing usage')
        attempts.append({'attempt': int(p.stem.split('-')[-1]), 'returned_model': response['model_name'],
                         'finish_reason': response.get('finish_reason'), 'input_tokens': usage['input_tokens'],
                         'output_tokens': usage['output_tokens'],
                         'reasoning_tokens': (usage.get('output_token_details') or {}).get('reasoning')})
    payload = read(responses[-1])['tool_calls'][-1]['args']
    errors = validate_digest_result(payload, current_unit_texts=[packet['current_unit_source']['source_text']])
    if errors:
        raise ValueError('Raw payload failed existing validator')
    raw_marks, marks = payload['marginalia'], result['result']['marginalia']
    if len(raw_marks) != len(marks):
        raise ValueError('Marks removed during normalization')
    differences = []
    for index, (raw, normalized) in enumerate(zip(raw_marks, marks), 1):
        if raw['kind'] != normalized['kind']:
            raise ValueError('Marginalia kind changed')
        for field in ['content', 'source_quote']:
            diff = normalization_difference(raw.get(field), normalized.get(field), f'marginalia[{index - 1}].{field}')
            if diff:
                diff.update(marginalia_index=index, marginalia_id=f"{packet['unit_id']}-replay-m{index:03d}", kind=normalized['kind'])
                differences.append(diff)
    for raw_key, normalized_key in [('understanding', 'understanding'), ('response', 'reading_impression')]:
        diff = normalization_difference(payload[raw_key], result['result'][normalized_key], raw_key)
        if diff:
            differences.append(diff)
    anchors = validate_marks(history, packet, result)
    counts = Counter(m['kind'] for m in marks)
    receipt = {'unit_id': packet['unit_id'], 'parsed': True, 'exact_anchors': len(anchors),
               'Note': counts['note'], 'Highlight': counts['highlight'], 'attempts': attempts,
               'physical_attempt_count': sum(c['physical_attempt_count'] for c in calls),
               'quota_retries': sum(c['quota_retry_attempt_count'] for c in calls),
               'logical_repairs': max(0, len(requests) - 1),
               'failover': any(c['fallback']['used_failover'] for c in calls),
               'truncated': any(a['finish_reason'] == 'length' for a in attempts),
               'normalizations': differences, 'result_sha256': sha((directory / 'result.json').read_bytes()),
               'request_sha256': [sha(p.read_bytes()) for p in requests],
               'response_sha256': [sha(p.read_bytes()) for p in responses]}
    write(directory / 'validation.json', receipt)
    if receipt['truncated']:
        raise ValueError('Truncated response; stop for review')
    return receipt


def prepare(source):
    manifest = registered_manifest()
    (FORMAL / 'preflight').mkdir(parents=True, exist_ok=False)
    histories = {u['book']: HistoricalRun(source, u['run_id']) for u in manifest['units']}
    write(FORMAL / 'preflight/manifest-checks.json', [h.check_manifest() for h in histories.values()])
    fingerprints = {str(p): sha(p.read_bytes()) for h in histories.values() for p in h.output.rglob('*') if p.is_file()}
    write(FORMAL / 'preflight/source-files-before.json', fingerprints)
    reviews = read(BACKEND / 'experiments/unit-sets/q1-v34-sampling-001.json')['source_review_receipts']
    review_map = {(r['book'], r['unit_id']): r for r in reviews if r['status'] == 'retained'}
    for u in manifest['units']:
        packet = histories[u['book']].reconstruct(u['unit_id'])
        if packet['accepted_call']['sampling'] != SAMPLING or packet['accepted_call']['prompt_version'] != PROMPT:
            raise ValueError('Original sampling differs')
        if packet['original_source_range'] != u['original_source_range']:
            raise ValueError('Registered source range differs')
        if sha(packet['current_unit_source']['source_text'].encode()) != review_map[(u['book'], u['unit_id'])]['source_text_sha256']:
            raise ValueError('Previously reviewed source changed')
        write(FORMAL / 'preflight' / f"{u['book']}-{u['unit_id']}.json", packet)
    status(FORMAL, 'prepared', units=26, model_calls=0)


def diagnostic(source):
    DIAGNOSTIC.mkdir(exist_ok=False)
    packet = read(ROOT / 'pilot/preflight/sapiens-u000019.json')
    history = HistoricalRun(source, packet['original_run_id'])
    if packet != history.reconstruct('u000019'):
        raise ValueError('Pilot historical packet changed')
    directory = DIAGNOSTIC / 'sapiens/u000019'
    status(DIAGNOSTIC, 'running', excluded_from_all_statistics=True)
    result = run_digest(packet, directory, model=MODEL, effort='high', prompt_version=PROMPT, operator_backend=source)
    receipt = audit(directory, history, packet, result, 'high')
    receipt['excluded_from_all_statistics'] = True
    receipt['only_change_relative_to_pilot'] = 'reasoning_effort: medium -> high'
    pilot_request = ROOT / 'pilot/outputs/sapiens/u000019/actual/request-001.json'
    receipt['logical_payload_identical_to_pilot'] = read(pilot_request) == read(directory / 'actual/request-001.json')
    if not receipt['logical_payload_identical_to_pilot']:
        raise ValueError('Diagnostic differs from pilot beyond effort')
    write(DIAGNOSTIC / 'summary.json', receipt)
    status(DIAGNOSTIC, 'completed', formal_effort='medium')
    print(json.dumps({'diagnostic': receipt['attempts'], 'excluded_from_all_statistics': True}), flush=True)


def run(source):
    manifest = registered_manifest()
    (FORMAL / 'outputs').mkdir(exist_ok=False)
    status(FORMAL, 'running', units_completed=0)
    receipts = []
    try:
        for u in manifest['units']:
            packet = read(FORMAL / 'preflight' / f"{u['book']}-{u['unit_id']}.json")
            history = HistoricalRun(source, u['run_id'])
            if packet != history.reconstruct(u['unit_id']):
                raise ValueError('Historical packet changed since preflight')
            directory = FORMAL / 'outputs' / u['book'] / u['unit_id']
            result = run_digest(packet, directory, model=MODEL, effort='medium', prompt_version=PROMPT, operator_backend=source)
            receipt = audit(directory, history, packet, result, 'medium')
            receipt['book'] = u['book']
            receipts.append(receipt)
            status(FORMAL, 'running', units_completed=len(receipts))
            print(json.dumps({k: receipt[k] for k in ['book', 'unit_id', 'Note', 'Highlight', 'parsed']}), flush=True)
        finish(manifest, receipts)
    except Exception as exc:
        write(FORMAL / 'failure.json', {'error_type': type(exc).__name__, 'message': str(exc), 'units_completed': len(receipts)})
        status(FORMAL, 'failed', units_completed=len(receipts), error_type=type(exc).__name__)
        raise


def finish(manifest, receipts):
    fingerprints = read(FORMAL / 'preflight/source-files-before.json')
    if not all(sha(Path(p).read_bytes()) == digest for p, digest in fingerprints.items()):
        raise ValueError('Historical file changed during formal run')
    attempts = [{**a, 'book': r['book'], 'unit_id': r['unit_id']} for r in receipts for a in r['attempts']]
    totals = {k: sum(r[k] for r in receipts) for k in ['Note', 'Highlight']}
    totals.update({k: sum(a[k] or 0 for a in attempts) for k in ['input_tokens', 'output_tokens', 'reasoning_tokens']})
    totals['total_tokens'] = totals['input_tokens'] + totals['output_tokens']
    summary = {'schema': 'q1-v34-formal-result/1', 'completed_at': now(), 'model': MODEL, 'sampling': SAMPLING,
               'units': [{k: v for k, v in r.items() if k != 'normalizations'} for r in receipts],
               'attempts': attempts, 'totals': totals,
               'by_book': {b: {k: sum(r[k] for r in receipts if r['book'] == b) for k in ['Note', 'Highlight']} for b in ['bovary', 'sapiens']},
               'cost_at_requested_rates_usd': (totals['input_tokens'] + 5 * totals['output_tokens']) / 1_000_000,
               'actual_billed_cost_usd': None, 'source_file_count': len(fingerprints), 'source_files_unchanged': True,
               'note_gate_passed': 30 <= totals['Note'] <= 80, 'human_annotation_started': False}
    write(FORMAL / 'summary.json', summary)
    write(FORMAL / 'normalizations.json', [{'book': r['book'], 'unit_id': r['unit_id'], **d} for r in receipts for d in r['normalizations']])
    text = ['# 正式批次批注正文', '', '包含原文，仅保存于忽略的 state/；不在盲标前汇报中展示。', '']
    population, result_hashes = [], {}
    for u in manifest['units']:
        path = FORMAL / 'outputs' / u['book'] / u['unit_id'] / 'result.json'
        result_hashes[str(path.relative_to(BACKEND))] = sha(path.read_bytes())
        marks = read(path)['result']['marginalia']
        text += [f"## {u['book']}/{u['unit_id']}", '']
        for i, m in enumerate(marks, 1):
            mid = f"{u['unit_id']}-replay-m{i:03d}"
            text += [f"### {mid} · {m['kind']}", '', m['source_quote'], '', m['content'], '']
            if m['kind'] == 'note':
                population.append({'book': u['book'], 'unit_id': u['unit_id'], 'marginalia_id': mid})
    with (FORMAL / 'annotations.md').open('x') as f:
        f.write('\n'.join(text) + '\n')
    if not summary['note_gate_passed']:
        status(FORMAL, 'note_count_gate_stop', Note=totals['Note'], add_units=False)
        print(json.dumps({'note_count_gate_stop': totals['Note']}), flush=True)
        return
    private = FORMAL / 'stability-private'
    private.mkdir(exist_ok=False, mode=0o700)
    write(private / 'population.json', population)
    selection = stability_sample(population)
    selection.update(protocol_id=SERIES + '-PROTOCOL-001', frozen_at=now(), input_sha256=sha((private / 'population.json').read_bytes()), result_sha256=result_hashes)
    write(private / 'selection.json', selection)
    for p in private.iterdir():
        p.chmod(0o600)
    write(FORMAL / 'stability-receipt.json', {'protocol_id': SERIES + '-PROTOCOL-001', 'seed': 20261122, 'count': 15,
          'frozen_at': selection['frozen_at'], 'population_sha256': sha((private / 'population.json').read_bytes()),
          'selection_sha256': sha((private / 'selection.json').read_bytes()), 'result_sha256': result_hashes,
          'identities_not_disclosed_to_annotator': True})
    status(FORMAL, 'completed', human_review='pending', units_completed=26, stability_selection_saved=True)
    print(json.dumps({'formal_totals': totals, 'stability_selection_saved': True}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['diagnostic', 'prepare', 'run'])
    p.add_argument('--source-backend', type=Path, required=True)
    args = p.parse_args()
    {'diagnostic': diagnostic, 'prepare': prepare, 'run': run}[args.action](args.source_backend.resolve())


if __name__ == '__main__':
    main()
