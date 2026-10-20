"""Independent, read-only material audit. Writes only its named verification report."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import re
from collections import Counter
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
V = OUT / 'verification'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def aggregate(items):
    return hashlib.sha256(''.join(f"{x['path']}\0{x['sha256']}\n" for x in items).encode()).hexdigest()


def check_fingerprint():
    p = ROOT / 'workflow/do-final-fingerprint-02.json'
    fp = load(p)
    actual = []
    bad = []
    for x in fp['files']:
        f = ROOT / x['path']
        if not f.is_file():
            bad.append({'path': x['path'], 'reason': 'missing'})
            continue
        digest = sha(f)
        actual.append({'path': x['path'], 'sha256': digest})
        if digest != x['sha256']:
            bad.append({'path': x['path'], 'reason': 'hash', 'actual': digest})
    result = {'manifest_sha256': sha(p), 'files': len(fp['files']),
              'expected_aggregate_sha256': fp['aggregate_sha256'],
              'actual_aggregate_sha256': aggregate(actual), 'mismatches': bad}
    result['pass'] = not bad and result['actual_aggregate_sha256'] == fp['aggregate_sha256']
    return result


def main():
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'argv': sys.argv, 'python': sys.version, 'platform': platform.platform(),
              'device_access': False, 'build_rerun': False,
              'script_sha256': sha(Path(__file__)), 'production_before': check_fingerprint()}
    facts_path = OUT / 'evidence-facts.json'
    facts = load(facts_path)
    result['evidence_facts_sha256_before'] = sha(facts_path)
    state = load(ROOT / 'workflow/state.json')
    registered = {x['session_id'] for x in state['sessions'] if x.get('session_id')} - {OVERVIEW}
    index = [json.loads(line) for line in (OUT / 'traces/session-index.filtered.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    index_ids = {x['id'] for x in index}
    sessions = []
    for x in facts['native_sessions']:
        f = OUT / x['native']
        raw = f.read_bytes()
        errors = []
        rows = []
        for no, line in enumerate(raw.splitlines(), 1):
            try:
                rows.append(json.loads(line))
            except (ValueError, UnicodeDecodeError):
                errors.append(no)
        meta = rows[0].get('payload', {}) if rows else {}
        digest = sha(f)
        md = OUT / x['markdown']
        md_rows = []
        inside_json = False
        for line in md.read_text(encoding='utf-8').splitlines():
            if line == '````json':
                inside_json = True
            elif line == '````':
                inside_json = False
            elif inside_json:
                md_rows.append(json.loads(line))
        sessions.append({'id': x['session_id'], 'native': x['native'],
                         'bytes': len(raw), 'sha256': digest, 'lines': len(rows),
                         'json_errors': errors, 'ends_with_newline': raw.endswith(b'\n'),
                         'native_id': meta.get('id'), 'cwd': meta.get('cwd'),
                         'native_secondary_session_id_matches': meta.get('session_id', meta.get('id')) == meta.get('id'),
                         'native_parent_thread_id': meta.get('parent_thread_id'),
                         'parent_id_matches_fact': meta.get('parent_thread_id') == x.get('parent_thread_id'),
                         'sidebar_rows': sum(y['id'] == x['session_id'] for y in index),
                         'claimed_sidebar_id': x.get('sidebar_id'),
                         'sidebar_id_matches_independent_row': (x.get('sidebar_id') == x['session_id']) == (x['session_id'] in index_ids),
                         'native_hash_match': digest == x['sha256'],
                         'native_size_match': len(raw) == x['bytes'],
                         'native_id_match': meta.get('id') == x['session_id'] == x.get('native_id'),
                         'markdown_hash_match': md.is_file() and sha(md) == x['markdown_sha256'],
                         'markdown_all_native_rows_equal': md_rows == rows,
                         'source_bytes_accounted': (x.get('source_bytes_at_read', len(raw)) ==
                              len(raw) + x.get('incomplete_tail_bytes_excluded', 0)),
                         'source_hash_match_when_no_excluded_tail': (x.get('incomplete_tail_bytes_excluded', 0) != 0 or
                              x.get('source_sha256_at_read', digest) == digest),
                         'last_event_timestamp': rows[-1].get('timestamp') if rows else None,
                         'fact_last_timestamp_match': bool(rows) and rows[-1].get('timestamp') == x['last_native_timestamp'],
                         'cli_version': meta.get('cli_version'), 'agent_role': meta.get('agent_role')})
    selected = {x['id'] for x in sessions}
    export_manifest = load(OUT / 'traces/export-manifest.json')
    excluded_ids = set(re.findall(r'[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',
                                 json.dumps(facts.get('excluded_search_hits'), ensure_ascii=False)))
    result['native'] = {'sessions': sessions, 'count': len(sessions), 'registered_not_exported': sorted(registered - selected),
                        'exported_unregistered': sorted(selected - registered),
                        'extra_index_ids': sorted(index_ids - selected),
                        'overview_native_exported': any(OVERVIEW in p.name for p in (OUT / 'traces/native').glob('*')),
                        'facts_gaps': facts.get('gaps'), 'search': facts.get('search'),
                        'export_manifest_matches_facts': export_manifest.get('native_sessions') == facts['native_sessions'],
                        'unrelated_uuid_metadata_count': len(excluded_ids - selected - {OVERVIEW}),
                        'source_store_read_by_this_audit': False}
    logs = []
    for x in facts['copied_logs']:
        source, target = ROOT / x['source'], OUT / x['copy']
        s, t = sha(source), sha(target)
        logs.append({'source': x['source'], 'copy': x['copy'],
                     'source_sha256': s, 'copy_sha256': t,
                     'match': s == t == x['sha256'] and source.stat().st_size == target.stat().st_size == x['bytes']})
    sources = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'logs').rglob('*') if p.is_file()}
    result['logs'] = {'count': len(logs), 'mismatches': [x for x in logs if not x['match']],
                      'unlisted_source_files': sorted(sources - {x['source'] for x in logs}), 'files': logs}
    stage = load(ROOT / 'workflow/do-stage-result-03.json')
    evidence = []
    for x in stage['artifacts'] + [stage['native_trace_snapshot']]:
        f = ROOT / x['path']
        evidence.append({'path': x['path'], 'exists': f.is_file(), 'match': f.is_file() and sha(f) == x['sha256']})
    hap = ROOT / stage['production_hap']['path']
    result['do_stage'] = {'status': stage['status'], 'scope': stage['scope'], 'artifacts': evidence,
                           'hap': {'exists': hap.is_file(), 'hash_match': hap.is_file() and sha(hap) == stage['production_hap']['sha256'],
                                   'size_match': hap.is_file() and hap.stat().st_size == stage['production_hap']['length']},
                           'verification': stage['verification'], 'hidden_tests': stage['official_hidden_test_result']}
    rawtests = []
    identities = set()
    for name in ('logs/do-04/selftest-20261019-213555.json',
                 'logs/do-04-fault/selftest-20261019-214313.json',
                 'logs/do-03/selftest-20261019-212521.json'):
        path = ROOT / name
        data = load(path)
        outcomes = dict(Counter(x['outcome'] for x in data['cases']))
        passed = []
        for case in data['cases']:
            if case['outcome'] == 'pass':
                match = re.search(r'\(([^()]*)\)$', case['name'])
                if match:
                    passed.append(match.group(1))
                    if '/do-04' in name:
                        identities.add(match.group(1))
        rawtests.append({'path': name, 'sha256': sha(path), 'outcomes': outcomes,
                         'passed_full_method_ids': passed,
                         'failures': [x for x in data['cases'] if x['outcome'] in ('fail', 'error')]})
    result['raw_selftests'] = {'reports': rawtests, 'unique_passed_method_count': len(identities),
                              'unique_passed_method_ids': sorted(identities),
                              'raw_failure_history_preserved': bool(rawtests[-1]['failures'])}
    harness = {}
    for kind, directory in [('taskbooks', ROOT.parent / 'common/spec-harness'), ('local_taskbooks', ROOT / 'spec-harness')]:
        actual = {p.name: sha(p) for p in directory.glob('[0-3]-*.md')}
        harness[kind] = {'files': actual, 'facts_match': actual == facts['harness'][kind]}
    result['harness'] = harness
    result['production_after'] = check_fingerprint()
    result['evidence_facts_sha256_after'] = sha(facts_path)
    result['audit_inputs_stable'] = result['evidence_facts_sha256_before'] == result['evidence_facts_sha256_after']
    # This evidence-only pass deliberately does not mean draft contents or patch replay passed.
    result['evidence_checks_pass'] = (result['production_before']['pass'] and result['production_after']['pass'] and
        result['audit_inputs_stable'] and not result['logs']['mismatches'] and not result['logs']['unlisted_source_files'] and
        not result['native']['overview_native_exported'] and all(not x['json_errors'] and x['ends_with_newline'] and
            x['native_hash_match'] and x['native_size_match'] and x['native_id_match'] and x['markdown_hash_match'] and
            x['native_secondary_session_id_matches'] and x['parent_id_matches_fact'] and
            x['markdown_all_native_rows_equal'] and x['source_bytes_accounted'] and
            x['source_hash_match_when_no_excluded_tail'] and
            x['sidebar_id_matches_independent_row'] and x['fact_last_timestamp_match'] for x in sessions) and
        result['native']['export_manifest_matches_facts'] and
        not result['native']['unrelated_uuid_metadata_count'] and
        all(x['match'] for x in evidence) and all(x['facts_match'] for x in harness.values()))
    result['evidence_checks_pass'] = (result['evidence_checks_pass'] and
        all(result['do_stage']['hap'].values()) and len(identities) == 26 and
        rawtests[0]['outcomes'].get('pass') == 23 and rawtests[1]['outcomes'].get('pass') == 3 and
        result['raw_selftests']['raw_failure_history_preserved'])
    name = sys.argv[1] if len(sys.argv) > 1 else 'evidence-audit-01.json'
    if Path(name).name != name:
        raise ValueError('Output must be one verification filename')
    output = V / name
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': output.relative_to(ROOT).as_posix(), 'evidence_checks_pass': result['evidence_checks_pass'],
                      'production_files': result['production_after']['files'], 'native_sessions': len(sessions),
                      'registered_not_exported': result['native']['registered_not_exported'], 'logs': len(logs),
                      'log_mismatches': len(result['logs']['mismatches']), 'native_json_errors': sum(len(x['json_errors']) for x in sessions)}, ensure_ascii=False))
    if not result['evidence_checks_pass']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
