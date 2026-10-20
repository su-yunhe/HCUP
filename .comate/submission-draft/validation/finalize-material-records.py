"""Derived material audit and bounded final snapshots; no application/build/device mutations."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import re
from collections import Counter

ROOT = Path('D:/HCUP/cml-spec28').resolve()
DRAFT = ROOT / '.comate/submission-draft'
IDS = {
    '01a14f53-1fa0-72d2-b947-fa27e7fb37c7',
    '01a14f55-3f56-7841-af11-d4ab55b3ba1a',
    '01a14f55-1969-7703-8fb7-ef6f5619d6da',
    '01a14f55-5f14-7860-976f-10407965f444',
    '01a14f58-dd63-7fb1-8463-04c83e0cf7e4',
}


def utc():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def rel(path):
    return path.relative_to(ROOT).as_posix()


def audit():
    formal = load(ROOT/'workflow/implementation/development-frozen-fingerprint-10.json')
    bad = [e['path'] for e in formal['files'] if sha(ROOT/e['path']) != e['sha256']]
    hap = ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap'
    original = ROOT/'hypium_tests/test_address_workflow.py'
    protection = {
        'captured_at': utc(), 'source_manifest': 'workflow/implementation/development-frozen-fingerprint-10.json',
        'source_count': formal['count'], 'source_aggregate': formal['aggregate'], 'source_mismatches': bad,
        'hap_sha256': sha(hap), 'hap_bytes': hap.stat().st_size,
        'original_test_sha256': sha(original), 'AUTH_status': 'blocked', 'one_do_complete': False,
        'no_build_or_device_execution_in_materials_phase': True,
    }
    assert not bad and protection['hap_sha256'] == '51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229'
    assert protection['original_test_sha256'] == '7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f'
    dump(DRAFT/'validation/business-frozen-after.json', protection)
    logs = load(DRAFT/'logs/manifest.json')['files']
    log_bad = [e['source'] for e in logs if sha(ROOT/e['source']) != e['sha256'] or sha(DRAFT/e['snapshot']) != e['sha256']]
    initial = load(DRAFT/'traces/manifest.json')
    trace_bad = []
    for e in initial['sessions']:
        for key, hash_key in [('raw', 'sha256'), ('markdown', 'markdown_sha256')]:
            if sha(ROOT/e[key]) != e[hash_key]:
                trace_bad.append(e[key])
    links = re.findall(r'\]\(([^)]+)\)', (DRAFT/'trace-index.md').read_text(encoding='utf-8'))
    missing = []
    for link in links:
        if link.startswith('project/'):
            target = ROOT/link[len('project/'):]
        elif link.startswith('../../traces/cml-spec28/'):
            target = DRAFT/'traces'/link[len('../../traces/cml-spec28/'):]
        elif re.match(r'https?://', link):
            continue
        else:
            target = DRAFT/link
        if not target.exists():
            missing.append(link)
    private_build_paths = re.findall(r'(?:[A-Za-z]:[\\/]|/Users/|/home/|/Applications/)', (DRAFT/'build.md').read_text(encoding='utf-8'))
    patch_result = load(DRAFT/'validation/patch-01/result.json')
    assert patch_result['status'] == 'pass'
    patch = ROOT/patch_result['patch']['path']
    assert sha(patch) == patch_result['patch']['sha256']
    report = {
        'captured_at_utc': utc(), 'status': 'pass' if not any([log_bad, trace_bad, missing, private_build_paths]) else 'failed',
        'business_protection': 'business-frozen-after.json', 'logs_checked': len(logs), 'log_mismatches': log_bad,
        'initial_unique_native_sessions_checked': len(initial['sessions']), 'initial_raw_and_markdown_hash_mismatches': trace_bad,
        'trace_index_package_layout_links_checked': len(links), 'missing_trace_links': missing,
        'build_private_absolute_paths': private_build_paths, 'patch_bytes': patch.stat().st_size, 'patch_sha256': sha(patch),
        'patch_validation_result': rel(DRAFT/'validation/patch-01/result.json'),
        'canonical_project': patch_result['reconstructed_project'],
        'scope_limit': 'Material audit only; AUTH stays blocked; no new clean build or device test',
        'snapshot_is_not_team_freeze_time': True,
    }
    dump(DRAFT/'validation/root-materials-integrity.json', report)
    assert report['status'] == 'pass', report
    print(json.dumps(report, ensure_ascii=False, indent=2))


def export():
    initial_path = DRAFT/'traces/manifest.json'
    initial = load(initial_path)
    selected = [x for x in initial['sessions'] if x['session_id'] in IDS]
    assert {x['session_id'] for x in selected} == IDS and len(selected) == 5
    state = load(ROOT/'workflow/state.json')
    assert IDS <= {s.get('session_id') for s in state['sessions']}
    destination = DRAFT/'traces/materials-final'
    destination.mkdir(exist_ok=False)
    (destination/'native').mkdir()
    (destination/'markdown').mkdir()
    results = []
    for old in selected:
        session_id = old['session_id']
        source = Path(old['source'])
        assert session_id in source.name and source.suffix == '.jsonl'
        started = utc()
        with source.open('rb') as stream:
            before = os.fstat(stream.fileno())
            bounded = stream.read(before.st_size)
            after = os.fstat(stream.fileno())
        # A concurrently written partial record is excluded as an explicitly recorded suffix.
        cut = bounded.rfind(b'\n') + 1
        raw = bounded[:cut]
        records = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
        meta = [e['payload'] for e in records if e.get('type') == 'session_meta']
        assert len(meta) == 1 and meta[0]['id'] == session_id
        assert Path(meta[0]['cwd']).resolve() == ROOT
        raw_path = destination/'native'/source.name
        with raw_path.open('xb') as stream:
            stream.write(raw)
        md_path = destination/'markdown'/(session_id+'.md')
        with md_path.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(f'# Native session {session_id}\n\n')
            stream.write('Full per-event JSON rendered as Markdown. Derived from the bounded native snapshot; no tool, failure, retry or opaque field is omitted. This is not an IDE sidebar plaintext export.\n\n')
            for number, event in enumerate(records, 1):
                encoded = json.dumps(event, ensure_ascii=False, indent=2)
                fence = '`' * max(3, max((len(x) for x in re.findall(r'`+', encoded)), default=0)+1)
                stream.write(f'## Native line {number}: {event.get("type", "unknown")}\n\n{fence}json\n{encoded}\n{fence}\n\n')
        contexts = [e['payload'] for e in records if e.get('type') == 'turn_context']
        token_events = [e['payload'] for e in records if e.get('type') == 'event_msg' and e.get('payload', {}).get('type') == 'token_count']
        results.append({
            'session_id': session_id, 'source': str(source), 'registrations': old['registrations'],
            'source_meta_id': meta[0]['id'], 'source_meta_cwd': meta[0]['cwd'],
            'parent_thread_id': meta[0].get('parent_thread_id'), 'originator': meta[0].get('originator'),
            'cli_version': meta[0].get('cli_version'), 'capture_started_at_utc': started, 'captured_at_utc': utc(),
            'source_size_at_start': before.st_size, 'source_size_after_read': after.st_size,
            'bounded_bytes_read': len(bounded), 'trailing_unfinished_record_bytes_excluded': len(bounded)-cut,
            'raw': rel(raw_path), 'bytes': len(raw), 'sha256': sha(raw_path),
            'markdown': rel(md_path), 'markdown_bytes': md_path.stat().st_size, 'markdown_sha256': sha(md_path),
            'line_count': len(records), 'parse_errors': [], 'event_types': dict(Counter(e.get('type') for e in records)),
            'first_timestamp': records[0].get('timestamp'), 'last_timestamp': records[-1].get('timestamp'),
            'models': sorted({c['model'] for c in contexts if isinstance(c.get('model'), str)}),
            'efforts': sorted({c['effort'] for c in contexts if isinstance(c.get('effort'), str)}),
            'token_count_event_count': len(token_events),
            'last_native_token_info': token_events[-1].get('info') if token_events else None,
            'token_accounting_note': 'Native cumulative/context metrics; not billed usage; do not sum repeated events or duplicate snapshots.',
            'snapshot_only': True, 'includes_future_events': False,
            'redaction': 'None; opaque encrypted fields preserved without decryption. Account identifiers/local paths remain; packaging confidentiality review still required.',
        })
    manifest = {
        'schema_version': 1, 'task_id': 'cml-spec28', 'captured_at_utc': utc(),
        'method': 'Only five exact registered material-session UUIDs from initial task manifest; full bounded native file prefix, all-event Markdown derivative.',
        'initial_16_session_manifest': rel(initial_path), 'initial_manifest_sha256': sha(initial_path),
        'supersedes_current_session_snapshots_only': True, 'unique_total_task_sessions_remains': 16,
        'excluded_initialization_session_id': '01a13fc4-2611-7761-a580-1283e0c70541',
        'excluded_initialization_body_read': False, 'session_count': len(results), 'sessions': results,
        'snapshot_only': True, 'includes_future_events': False, 'formal_team_freeze_time': None,
        'project_exclusion': 'Declared before project freeze; these late material events are separately copied to package traces/cml-spec28/materials-final, outside frozen canonical project.',
        'ide_export': False, 'comate_export': False, 'failure_events_filtered': False,
        'records_after_capture_not_included': True,
    }
    dump(destination/'manifest.json', manifest)
    print(json.dumps({'manifest': rel(destination/'manifest.json'), 'sha256': sha(destination/'manifest.json'), 'session_count': len(results), 'raw_bytes': sum(e['bytes'] for e in results), 'markdown_bytes': sum(e['markdown_bytes'] for e in results), 'trailing_partial_bytes': sum(e['trailing_unfinished_record_bytes_excluded'] for e in results)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['audit', 'export'])
    args = parser.parse_args()
    {'audit': audit, 'export': export}[args.action]()
