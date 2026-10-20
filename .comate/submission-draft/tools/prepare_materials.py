"""Evidence-only submission preparation. Never writes application files or source Git index."""
import argparse
import collections
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
STORE = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'
PENDING = '【待补充】'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, text):
    path = OUT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def dump(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def run(args, cwd=ROOT, data=None):
    result = subprocess.run(args, cwd=cwd, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError(f'{args}: {result.returncode}: {result.stderr.decode("utf-8", "replace")[:2000]}')
    return result.stdout


def yaml_values(path):
    # Input forms contain plain scalar double-quoted values; do not infer blanks.
    result = {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        m = re.match(r'^([a-z_]+):\s*"([^"]*)"', line)
        if m:
            result[m[1]] = m[2] or PENDING
    return result


def matches(term):
    p = subprocess.run(['rg', '-l', '-F', '--glob', '*.jsonl', term, str(STORE)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode not in (0, 1):
        raise RuntimeError(p.stderr.decode('utf-8', 'replace'))
    return set(p.stdout.decode('utf-8').splitlines())


def load_rows(path):
    rows, incomplete = [], 0
    for line in path.read_bytes().splitlines():
        try:
            rows.append(json.loads(line))
        except (ValueError, UnicodeError):
            incomplete += 1
    return rows, incomplete


def collect():
    state = read(ROOT / 'workflow/state.json')
    wanted = {x['session_id'] for x in state['sessions'] if x.get('session_id')} - {OVERVIEW}
    # Search both separators as JSON native records escape Windows backslashes.
    by_path = matches(str(ROOT).replace('\\', '\\\\')) | matches(str(ROOT).replace('\\', '/'))
    by_id = matches('vg-spec13')
    selected, unrelated, overview, missing = {}, 0, 0, []
    for item in sorted(by_path | by_id):
        path = Path(item)
        if OVERVIEW in path.name:
            overview += 1
            continue
        with path.open('rb') as f:
            first = json.loads(f.readline())
        meta = first.get('payload', {})
        # Codex subagent records inherit the root session_id; id identifies this thread.
        sid = meta.get('id', meta.get('session_id'))
        cwd = meta.get('cwd', '').replace('\\', '/').rstrip('/').lower()
        if sid in wanted or cwd == ROOT.as_posix().lower():
            selected[sid] = path
        else:
            unrelated += 1
    # Registered IDs also searched by filename, so a session without task text is not lost.
    for sid in wanted - set(selected):
        files = list(STORE.rglob(f'*{sid}.jsonl'))
        if len(files) == 1:
            selected[sid] = files[0]
        else:
            missing.append(sid)
    identities = set()
    loaded = {}
    for sid, path in selected.items():
        rows, incomplete = load_rows(path)
        loaded[sid] = (path, rows, incomplete)
        for row in rows:
            if row.get('type') == 'session_meta':
                for key in ('creator_user_id', 'creator_account_id'):
                    if row['payload'].get(key):
                        identities.add(row['payload'][key])
    dump('traces/redaction-policy.json', {
        'created_at': now(), 'scope': ['creator_user_id', 'creator_account_id', 'same literal IDs in nested tool output'],
        'replacement': '【账号标识已脱敏】', 'count_of_distinct_identifiers': len(identities),
        'not_removed': 'session IDs, prompts, model/config fields, source citations, code, tool calls/results, failures/retries, local paths, timestamps',
        'overview_session_excluded': OVERVIEW,
    })
    records, tool_counts, urls = [], collections.Counter(), set()
    index_lines = []
    for sid, (path, rows, incomplete) in sorted(loaded.items()):
        raw = path.read_bytes()
        rows = []
        incomplete = 0
        for line in raw.splitlines():
            try:
                rows.append(json.loads(line))
            except (ValueError, UnicodeError):
                incomplete += 1
        exported = raw.decode('utf-8', 'replace')
        for identity in identities:
            exported = exported.replace(identity, '【账号标识已脱敏】')
        # An active session may end mid-record; retain only fully parseable native records.
        lines = []
        for line in exported.splitlines():
            try:
                json.loads(line)
                lines.append(line)
            except ValueError:
                pass
        text = '\n'.join(lines) + '\n'
        dest = f'traces/native/{sid}.jsonl'
        write(dest, text)
        md = ['# Codex 原生轨迹的 Markdown 副本', '', f'会话：`{sid}`。这是原生 JSONL 的逐记录包裹副本，由本脚本生成；不是 IDE“导出本地”文件。', '',
              '账号标识已按 redaction-policy.json 脱敏；其它完整记录见下列 JSON。', '']
        for line in lines:
            item = json.loads(line)
            md.extend([f'## {item.get("timestamp", "")} · {item.get("type", "")}', '', '``````json', line, '``````', ''])
            if item.get('type') == 'session_meta':
                index_lines.append({'timestamp': item.get('timestamp'), 'type': 'session_meta', 'payload': {
                    k: v for k, v in item.get('payload', {}).items()
                    if k in ('id', 'session_id', 'timestamp', 'cwd', 'originator', 'cli_version', 'source', 'thread_source', 'model_provider', 'source_info', 'forked_from_id', 'agent_nickname', 'agent_role')
                }})
        write(f'traces/markdown/{sid}.md', '\n'.join(md))
        meta = next((x['payload'] for x in rows if x.get('type') == 'session_meta'), {})
        contexts = [x['payload'] for x in rows if x.get('type') == 'turn_context']
        models = sorted({x.get('model') for x in contexts if x.get('model')})
        efforts = sorted({x.get('effort') for x in contexts if x.get('effort')})
        token_rows = [x for x in rows if x.get('type') == 'event_msg' and x.get('payload', {}).get('type') == 'token_count' and x.get('payload', {}).get('info')]
        last_token = token_rows[-1] if token_rows else None
        tools = collections.Counter()
        for row in rows:
            payload = row.get('payload', {})
            if row.get('type') == 'response_item' and payload.get('type') in ('function_call', 'custom_tool_call'):
                tools[payload.get('name', 'unnamed')] += 1
                # Only URLs actually occurring in tool input are auto-extracted; never assert all were used as sources.
                for url in re.findall(r'https?://[^\s\"<>\\)]+', str(payload.get('arguments', payload.get('input', '')))):
                    urls.add(url.rstrip('.,;'))
        tool_counts.update(tools)
        roles = sorted({x['role'] for x in state['sessions'] if x.get('session_id') == sid})
        records.append({
            'sessionUuid': PENDING, 'sessionUuid_reason': 'Comate engine not used / store absent; Codex IDs below are not relabelled as Comate IDs',
            'codex_thread_id': sid, 'ide_sidebar_session_id': sid,
            'codex_engine_session_id': meta.get('session_id'),
            'id_mapping': 'session_meta.id == this CODEX_THREAD_ID / Codex chat UUID; session_meta.session_id can be inherited from root by subagents. Neither field is relabelled as a Comate sessionUuid.',
            'roles': roles, 'cwd': meta.get('cwd'), 'originator': meta.get('originator'),
            'cli_version': meta.get('cli_version'), 'source': meta.get('source'), 'source_info': meta.get('source_info'),
            'models': models, 'efforts': efforts,
            'token_usage_latest_observed': last_token['payload']['info']['total_token_usage'] if last_token else None,
            'token_usage_timestamp': last_token.get('timestamp') if last_token else None,
            'tools': dict(tools), 'source_file': str(path), 'source_sha256': sha(raw),
            'export_path': dest, 'export_sha256': sha(text.encode()), 'bytes': len(text.encode()),
            'native_record_count': len(lines), 'incomplete_lines_omitted': incomplete,
            'snapshot_captured_at': now(), 'last_record_timestamp': rows[-1].get('timestamp') if rows else None,
            'active_snapshot_notice': 'Capture is a finite snapshot; it cannot contain later records.',
            'appliedRuleNames': PENDING, 'appliedRuleNames_reason': 'No Comate field; actual instructions are in native session_meta/turn_context and repository snapshots.',
        })
    write('traces/session-index.filtered.jsonl', ''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in index_lines))
    dump('traces/session-inventory.json', records)
    dump('traces/tools-used.json', dict(tool_counts.most_common()))
    dump('traces/tool-input-urls.json', {'notice': 'Candidate URLs extracted from actual tool inputs, not proof every URL was read or reused.', 'urls': sorted(urls)})
    dump('traces/discovery.json', {
        'captured_at': now(), 'store': str(STORE), 'search_dimensions': ['absolute project path (both separators)', 'task ID vg-spec13', 'registered session filename fallback'],
        'path_match_files': len(by_path), 'task_id_match_files': len(by_id),
        'selected_sessions': sorted(selected), 'unrelated_candidates_not_exported': unrelated,
        'overview_candidates_excluded': overview, 'overview_id': OVERVIEW,
        'registered_sessions_missing': missing,
        'comate_store_exists': (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
        'macos_comate_product_exists': Path('/Applications/Comate.app/Contents/Resources/app/product.json').exists(),
    })
    # Capture instructions actually supplied with this task, not a new team-level configuration.
    common = ROOT.parent / 'common/spec-harness'
    version = {'method': 'four task-book SHA-256 values; common/spec-harness has no own .git, enclosing Git commit is recorded separately',
               'enclosing_repository_head': run(['git', '-C', str(common), 'rev-parse', 'HEAD']).decode().strip(), 'files': {}}
    for name in ('0-analyze.md', '1-do.md', '2-submit.md', '3-package.md'):
        src = common / name
        version['files'][name] = {'common_sha256': sha(src.read_bytes()), 'project_sha256': sha((ROOT / 'spec-harness' / name).read_bytes())}
    dump('traces/taskbook-version.json', version)
    dump('traces/history-taskbooks.json', [{'path': p.relative_to(ROOT).as_posix(), 'sha256': sha(p.read_bytes())} for p in sorted((ROOT / 'spec/history').rglob('*')) if p.is_file()] if (ROOT / 'spec/history').exists() else [])
    for src in (ROOT.parent / 'common/test-harness').rglob('*'):
        if src.is_file() and '__pycache__' not in src.parts and src.suffix != '.pyc' and '.git' not in src.parts:
            dst = OUT / 'repro-support/test-harness' / src.relative_to(ROOT.parent / 'common/test-harness')
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    # All original build/test logs, including failures, are copied without editing.
    log_records = []
    for src in sorted((ROOT / 'logs').rglob('*')):
        if src.is_file():
            rel = src.relative_to(ROOT)
            dst = OUT / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            log_records.append({'path': rel.as_posix(), 'bytes': src.stat().st_size, 'sha256': sha(src.read_bytes())})
    dump('logs/copy-manifest.json', log_records)
    print(json.dumps({'sessions': len(records), 'logs': len(log_records), 'missing': missing}))


def seal():
    base = read(ROOT / 'spec/metadata.json')['base_commit']
    # Freeze all Git-visible source/process files; never rely on current Git index contents.
    names = run(['git', '-c', 'core.quotepath=false', 'ls-files', '-c', '-o', '--exclude-standard', '-z']).decode('utf-8').split('\0')
    snapshot = OUT / 'traces/code-snapshot/project'
    if snapshot.exists() and not args.retry:
        raise RuntimeError('Snapshot exists: do not silently replace a frozen version.')
    snapshot.mkdir(parents=True, exist_ok=args.retry)
    ids = set()
    for path in (OUT / 'traces/native').glob('*.jsonl'):
        # Personal account values are taken only from the matching original session metadata.
        inventory = read(OUT / 'traces/session-inventory.json')
        rec = next((x for x in inventory if x['codex_thread_id'] == path.stem), None)
        if rec:
            with Path(rec['source_file']).open('rb') as f:
                meta = json.loads(f.readline())['payload']
            ids.update(meta[k] for k in ('creator_user_id', 'creator_account_id') if meta.get(k))
    files, excluded, generated = [], [], []
    for rel in sorted(set(names)):
        if not rel:
            continue
        src = ROOT / rel
        if rel.startswith('.comate/submission-draft/'):
            continue
        if '__pycache__' in Path(rel).parts or Path(rel).suffix.lower() in ('.pyc', '.pyo'):
            generated.append({'path': rel, 'reason': 'Generated Python bytecode cache, not source or execution evidence.'})
            # Only remove an earlier draft copy, never the original working-tree cache.
            stale = snapshot / rel
            if stale.is_file():
                if not stale.resolve().is_relative_to(snapshot.resolve()):
                    raise RuntimeError('Refusing to remove a cache copy outside the submission snapshot.')
                stale.unlink()
            continue
        if OVERVIEW in Path(rel).name and rel.endswith('.jsonl'):
            excluded.append({'path': rel, 'reason': 'Mixed-task initialization overview; never feature-development evidence and unrelated raw conversation must not be submitted.'})
            continue
        if not src.is_file():
            continue
        data = src.read_bytes()
        original = sha(data)
        redacted = False
        if rel.startswith('traces/native/') and rel.endswith('.jsonl'):
            for identity in ids:
                if identity.encode() in data:
                    data = data.replace(identity.encode(), '【账号标识已脱敏】'.encode())
                    redacted = True
        dest = snapshot / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        files.append({'path': rel, 'bytes': len(data), 'sha256': sha(data), 'workspace_sha256': original, 'account_ids_redacted': redacted})
    tracked = run(['git', 'ls-tree', '-r', '-z', base]).split(b'\0')
    modes = {}
    base_blobs = {}
    for row in tracked:
        if row:
            head, path = row.split(b'\t', 1)
            mode, kind, oid = head.decode().split()
            modes[path.decode()] = mode
            base_blobs[path.decode()] = oid
    temporary_root = OUT / '.work'
    temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='patch-', dir=temporary_root) as tmp:
        tmp = Path(tmp)
        branch = run(['git', 'branch', '--show-current']).decode().strip()
        commands = []
        def git(args, cwd, data=None):
            # Explicit process flags override inherited runtime Git config as well as global defaults.
            argv = ['git', '-c', 'core.autocrlf=false', '-c', 'core.eol=lf'] + args
            commands.append({'argv': argv, 'cwd_role': 'temporary baseline clone' if cwd != ROOT else 'source project', 'exit_code': 0})
            return run(argv, cwd, data)
        repo = tmp / 'objects'
        git(['clone', '--shared', '--no-checkout', '--single-branch', '--branch', branch, str(ROOT), str(repo)], ROOT)
        git(['config', 'core.autocrlf', 'false'], repo)
        git(['checkout', '--detach', base], repo)
        git(['read-tree', '--empty'], repo)
        hashes = git(['hash-object', '-w', '--no-filters', '--stdin-paths'], repo, ('\n'.join(str(snapshot / x['path']) for x in files) + '\n').encode()).decode().splitlines()
        index = ''.join(f'{modes.get(f["path"], "100644")} {oid}\t{f["path"]}\n' for f, oid in zip(files, hashes))
        git(['update-index', '--index-info'], repo, index.encode())
        tree = git(['write-tree'], repo).decode().strip()
        patch = git(['diff', '--binary', '--full-index', '--no-ext-diff', '--no-textconv', base, tree, '--'], repo)
        (OUT / 'changes/final.diff').parent.mkdir(exist_ok=True)
        (OUT / 'changes/final.diff').write_bytes(patch)
        checked = tmp / 'apply-check'
        git(['clone', '--shared', '--no-checkout', '--single-branch', '--branch', branch, str(ROOT), str(checked)], ROOT)
        git(['config', 'core.autocrlf', 'false'], checked)
        git(['checkout', '--detach', base], checked)
        git(['apply', '--check', '--binary', str(OUT / 'changes/final.diff')], checked)
        git(['apply', '--binary', str(OUT / 'changes/final.diff')], checked)
        actual = {p.relative_to(checked).as_posix(): sha(p.read_bytes()) for p in checked.rglob('*') if p.is_file() and '.git' not in p.relative_to(checked).parts}
        expected = {f['path']: f['sha256'] for f in files}
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        mismatches = sorted(k for k in expected.keys() & actual.keys() if actual[k] != expected[k])
        if missing or extra or mismatches:
            details = []
            for name in mismatches:
                a, b = (snapshot / name).read_bytes(), (checked / name).read_bytes()
                details.append({'path': name, 'expected_sha256': sha(a), 'actual_sha256': sha(b), 'expected_bytes': len(a), 'actual_bytes': len(b),
                                'expected_crlf': a.count(b'\r\n'), 'actual_crlf': b.count(b'\r\n'), 'expected_lf': a.count(b'\n'), 'actual_lf': b.count(b'\n')})
            dump('audits/patch-roundtrip-failed-v1.json', {'captured_at': now(), 'missing': missing, 'extra': extra, 'mismatches': details, 'diff_sha256': sha(patch)})
            raise RuntimeError(f'Patch round-trip differs: {missing[:5]} {extra[:5]} {mismatches[:5]}')
        binaries = []
        for f in files:
            data = (snapshot / f['path']).read_bytes()
            if b'\0' in data or Path(f['path']).suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp', '.gif', '.ttf', '.mp3', '.wav', '.har', '.zip', '.hap'):
                oid = base_blobs.get(f['path'])
                same = False
                if oid:
                    same = sha(run(['git', 'cat-file', 'blob', oid])) == f['sha256']
                binaries.append({**{k: f[k] for k in ('path', 'bytes', 'sha256')}, 'same_as_official_baseline_at_same_path': same,
                                 'origin': 'Official bundled baseline, unchanged' if same else ('Local UI/test evidence, see original run logs' if f['path'].startswith('logs/') else 'Additional binary; origin requires review')})
        dump('changes/binary-files.json', binaries)
        dump('changes/patch-validation.json', {'validated_at': now(), 'base_commit': base, 'submitted_git_tree': tree,
             'diff_bytes': len(patch), 'diff_sha256': sha(patch), 'git_apply_check_exit': 0, 'git_apply_exit': 0,
             'files_compared': len(expected), 'missing': missing, 'extra': extra, 'hash_mismatches': mismatches,
             'method': 'Two temporary local single-branch clones; detached official base; git apply --check --binary, then actual apply and SHA-256 comparison of every file, including process files.', 'commands': commands})
    temporary_root.rmdir()
    aggregate = sha(''.join(f'{f["path"]}\0{f["sha256"]}\n' for f in files).encode())
    dump('traces/code-snapshot/manifest.json', {'captured_at': now(), 'base_commit': base, 'git_tree': tree,
         'aggregate_sha256': aggregate, 'files': files, 'excluded_unrelated_records': excluded, 'excluded_generated_files': generated,
         'scope': 'Exact future tasks/vg-spec13/project contents. Git-visible source and process files, excluding this submission-draft material staging directory itself, unrelated initialization overview raw records and generated Python bytecode/cache files. Ignored build/dependency/cache paths are not project deliverables.',
         'packaging_instruction': 'Copy this sealed project directory as tasks/vg-spec13/project. Copy draft materials as task siblings. Do not copy the live workspace recursively or include submission-draft within project.',
         'source_workspace_mutated': False})
    hap = ROOT / 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    dump('changes/verified-hap.json', {'path': hap.relative_to(ROOT).as_posix(), 'bytes': hap.stat().st_size, 'sha256': sha(hap.read_bytes()), 'note': 'Build artifact is not a source/project file and not required in this material draft; final package must contain complete source.'})
    print(json.dumps({'files': len(files), 'git_tree': tree, 'diff_bytes': len(patch), 'binaries': len(binaries), 'excluded_overview_copies': len(excluded), 'round_trip': 'pass'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['collect', 'seal'])
    parser.add_argument('--retry', action='store_true', help='Explicitly regenerate an unsuccessful draft seal; original workspace is never changed.')
    args = parser.parse_args()
    (collect if args.command == 'collect' else seal)()
