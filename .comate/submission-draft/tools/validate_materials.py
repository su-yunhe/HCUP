"""Check actual submission files and their evidence without building or using a device."""
import ast
from pathlib import Path
import re
from prepare_materials import ROOT, OUT, OVERVIEW, read, sha, dump


def validate():
    checks = []
    def check(name, ok, detail):
        checks.append({'check': name, 'pass': bool(ok), 'detail': detail})
    required = ['changes/final.diff', 'changes/binary-files.json', 'changes/patch-validation.json',
                'build.md', 'trace-index.md', 'sources.fragment.md', 'solution.fragment.md',
                'submission.json.fragment', 'human-changes.md', 'NEEDS-INPUT.md', 'AUTO-FACTS.md', 'DELIVERY.md',
                'traces/session-inventory.json', 'traces/session-index.filtered.jsonl', 'traces/code-snapshot/manifest.json',
                'logs/copy-manifest.json', 'repro-support/run-selftest.ps1']
    check('required outputs', all((OUT / p).is_file() for p in required), required)
    snapshot = read(OUT / 'traces/code-snapshot/manifest.json')
    project = OUT / 'traces/code-snapshot/project'
    expected = {f['path']: f['sha256'] for f in snapshot['files']}
    actual = {p.relative_to(project).as_posix(): sha(p.read_bytes()) for p in project.rglob('*') if p.is_file()}
    check('sealed project file set and hashes', expected == actual, {'files': len(actual)})
    check('no recursive staging or .git in project', not any('.git' in Path(p).parts or p.startswith('.comate/submission-draft/') for p in actual), '')
    overview_files = [p.relative_to(OUT).as_posix() for p in OUT.rglob('*.jsonl') if OVERVIEW in p.name]
    check('mixed-task initialization raw files excluded', not overview_files, overview_files)
    patch = read(OUT / 'changes/patch-validation.json')
    check('patch independently applies and compares all files', patch['git_apply_check_exit'] == 0 and patch['git_apply_exit'] == 0 and not patch['missing'] and not patch['extra'] and not patch['hash_mismatches'] and patch['files_compared'] == len(expected), patch['files_compared'])
    check('patch checksum and final tree', sha((OUT / 'changes/final.diff').read_bytes()) == patch['diff_sha256'] and patch['submitted_git_tree'] == snapshot['git_tree'], patch['submitted_git_tree'])
    ref = read(ROOT / 'workflow/implementation/source-fingerprint-v2.json')['tracked_plus_authorized_new_files_sha256']
    mismatches = [p for p, h in ref.items() if not (ROOT / p).is_file() or sha((ROOT / p).read_bytes()).lower() != h.lower()]
    check('frozen application and configuration remain unchanged', not mismatches, {'reference_files': len(ref), 'mismatches': mismatches})
    logs = read(OUT / 'logs/copy-manifest.json')
    bad_logs = [x['path'] for x in logs if sha((OUT / x['path']).read_bytes()) != x['sha256'] or sha((ROOT / x['path']).read_bytes()) != x['sha256']]
    check('all original logs copied byte for byte', not bad_logs, {'logs': len(logs), 'mismatches': bad_logs})
    sessions = read(OUT / 'traces/session-inventory.json')
    bad_traces = [x['codex_thread_id'] for x in sessions if sha((OUT / x['export_path']).read_bytes()) != x['export_sha256'] or not (OUT / 'traces/markdown' / (x['codex_thread_id'] + '.md')).exists()]
    check('scoped native and Markdown traces exist with matching checksums', not bad_traces, {'sessions': len(sessions), 'mismatches': bad_traces})
    bad_ids = []
    for x in sessions:
        with (OUT / x['export_path']).open(encoding='utf-8') as f:
            meta = __import__('json').loads(f.readline())['payload']
        if meta.get('id') != x['codex_thread_id'] or meta.get('session_id') != x['codex_engine_session_id']:
            bad_ids.append(x['codex_thread_id'])
    check('each exported thread ID matches its own native metadata id', not bad_ids, bad_ids)
    discovery = read(OUT / 'traces/discovery.json')
    check('registered dedicated sessions present', not discovery['registered_sessions_missing'], discovery['registered_sessions_missing'])
    template = Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
    fields = [s[2:].split('：')[0] for s in template.splitlines() if s.startswith('- ')]
    trace = (OUT / 'trace-index.md').read_text(encoding='utf-8')
    absent = [s for s in fields if ('- ' + s + '：') not in trace]
    check('every official trace-index field filled or explicitly pending', not absent, {'fields': len(fields), 'absent': absent})
    build = (OUT / 'build.md').read_text(encoding='utf-8')
    private_paths = re.findall(r'(?<![A-Za-z])(?:[A-Za-z]:[\\/]|/Users/|/Applications/|/home/)', build)
    check('build instructions contain no private absolute path', not private_paths, private_paths)
    frag = read(OUT / 'submission.json.fragment')
    mapping = {'project_path': project, 'build_instructions': OUT / 'build.md', 'trace_index': OUT / 'trace-index.md'}
    check('three package paths relative slash format with file targets', all(not re.match(r'^(?:[A-Za-z]:|/)', frag[k]) and '\\' not in frag[k] and '..' not in Path(frag[k]).parts and p.exists() for k, p in mapping.items()) and mapping['project_path'].is_dir() and mapping['build_instructions'].is_file() and mapping['trace_index'].is_file(), {k: frag[k] for k in mapping})
    python_files = list((OUT / 'tools').glob('*.py')) + list((OUT / 'repro-support/test-harness').rglob('*.py'))
    for p in python_files:
        ast.parse(p.read_text(encoding='utf-8-sig'), filename=str(p))
    check('material tools and copied Harness Python parse', True, {'files': len(python_files)})
    # Automated screening is intentionally narrow and does not attest no undisclosed human secrets.
    secret_patterns = [rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', rb'(?<![A-Za-z0-9])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}']
    hits = []
    for p in project.rglob('*'):
        if p.is_file() and p.suffix.lower() in ('.json', '.jsonl', '.json5', '.md', '.log', '.ps1', '.py', '.ets', '.ts', '.yaml'):
            data = p.read_bytes()
            if any(re.search(pattern, data) for pattern in secret_patterns):
                hits.append(p.relative_to(project).as_posix())
    check('private-key and common API-key signature scan', not hits, {'matching_paths_only': hits, 'scope': 'heuristic scan; not proof that no undisclosed secret exists'})
    dump('validation-report.json', {'result': 'pass' if all(x['pass'] for x in checks) else 'fail', 'checks': checks})
    print(__import__('json').dumps({'checks': len(checks), 'failed': [x['check'] for x in checks if not x['pass']], 'project_files': len(actual), 'sessions': len(sessions), 'logs': len(logs)}))
    if not all(x['pass'] for x in checks):
        raise SystemExit(1)


if __name__ == '__main__':
    validate()
