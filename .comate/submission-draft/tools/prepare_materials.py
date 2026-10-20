"""Single-task material collection and exact-byte diff validation (Python stdlib)."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / '.comate/submission-draft'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'
SCRATCH = DRAFT / '.scratch'
DERIVED = {'.comate/submission-draft/changes/final.diff',
           '.comate/submission-draft/changes/project-snapshot.json',
           '.comate/submission-draft/changes/binary-files.json',
           '.comate/submission-draft/changes/binary-files.md'}
PRUNE = {'.git', 'build', 'oh_modules', 'node_modules', '.hvigor', '__pycache__',
         '.venv', '.testenv', '.idea', '.test', '.cxx', '.clangd', '.appanalyzer'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(args, *, cwd=ROOT, env=None, data=None):
    result = subprocess.run(args, cwd=cwd, env=env, input=data, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'{args}: {result.returncode}\n{result.stderr.decode("utf-8", "replace")}')
    return result.stdout


def collect():
    state = json.loads((ROOT / 'workflow/state.json').read_text(encoding='utf-8'))
    known = {x['session_id'] for x in state['sessions'] if x.get('session_id')} - {OVERVIEW}
    native_store = Path(os.environ.get('CODEX_HOME', Path.home() / '.codex'))
    index_path = native_store / 'session_index.jsonl'
    index_rows, by_task_id = [], set()
    if index_path.exists():
        for line in index_path.read_text(encoding='utf-8').splitlines():
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get('id') == OVERVIEW:
                continue
            if re.search(r'(?<![\w-])vg-spec7(?![\w-])', row.get('thread_name', '')):
                by_task_id.add(row['id'])
            if row.get('id') in known or row.get('id') in by_task_id:
                index_rows.append(line)
    selected, by_workspace = {}, set()
    for path in (native_store / 'sessions').rglob('*.jsonl'):
        try:
            with path.open(encoding='utf-8') as f:
                first = json.loads(next(f))
            meta = first.get('payload', {})
        except (ValueError, StopIteration, OSError):
            continue
        sid = meta.get('id')
        if sid == OVERVIEW:
            continue
        cwd = meta.get('cwd', '').replace('\\', '/').lower().rstrip('/')
        if cwd == ROOT.as_posix().lower():
            by_workspace.add(sid)
        if sid in known or sid in by_task_id or cwd == ROOT.as_posix().lower():
            selected[sid] = (path, meta)
    index_out = DRAFT / 'traces/session-index.filtered.jsonl'
    index_out.parent.mkdir(parents=True, exist_ok=True)
    index_out.write_text('\n'.join(index_rows) + '\n', encoding='utf-8')
    rows = []
    for sid, (path, meta) in sorted(selected.items()):
        original = path.read_bytes()
        # Native event strings can contain a terminal's global-index excerpt.
        # Remove only unrelated sidebar-index rows; retain all task events.
        redactions = []
        def scrub(value):
            if isinstance(value, str):
                def replace(match):
                    try:
                        item = json.loads(match.group(0))
                    except ValueError:
                        return match.group(0)
                    if item.get('id') not in selected and 'thread_name' in item:
                        redactions.append('unrelated sidebar index row')
                        return '[REDACTED: unrelated sidebar index row]'
                    return match.group(0)
                return re.sub(r'\{"id"\s*:\s*"[^"\n]+"[^\n]*?"updated_at"\s*:\s*"[^"\n]+"\}', replace, value)
            if isinstance(value, list):
                return [scrub(x) for x in value]
            if isinstance(value, dict):
                return {k: scrub(v) for k, v in value.items()}
            return value
        events, invalid_lines = [], []
        for number, line in enumerate(original.splitlines(), 1):
            try:
                events.append(scrub(json.loads(line)))
            except (ValueError, UnicodeError):
                invalid_lines.append(number)
        exported = (''.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) + '\n' for x in events).encode('utf-8')
                    if redactions or invalid_lines else original)
        target = DRAFT / 'traces/native' / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(exported)
        md = DRAFT / 'traces/markdown' / (sid + '.md')
        md.parent.mkdir(parents=True, exist_ok=True)
        with md.open('w', encoding='utf-8') as f:
            f.write(f'# {sid}\n\nNative JSONL reading copy generated during material collection. '
                    'Not an IDE Markdown export; no new development evidence is asserted.\n\n')
            for event in events:
                f.write(f'## {event.get("timestamp", "")} {event.get("type", "")}\n\n')
                f.write('````json\n' + json.dumps(event, ensure_ascii=False, indent=2) + '\n````\n\n')
        models, efforts, tools, last_usage = set(), set(), Counter(), None
        for event in events:
            payload = event.get('payload', {})
            if event.get('type') == 'turn_context':
                if payload.get('model'): models.add(payload['model'])
                for key in ('effort', 'reasoning_effort'):
                    if payload.get(key): efforts.add(str(payload[key]))
            if event.get('type') == 'response_item' and payload.get('type') in ('function_call', 'custom_tool_call'):
                tools[payload.get('name', '?')] += 1
            if payload.get('type') == 'token_count' and (payload.get('info') or {}).get('total_token_usage'):
                last_usage = payload['info']['total_token_usage']
        source = meta.get('source', {})
        spawn = source.get('subagent', {}).get('thread_spawn', {}) if isinstance(source, dict) else {}
        rows.append({'native_id': sid, 'payload_session_id': meta.get('session_id'),
                     'parent_thread_id': spawn.get('parent_thread_id'),
                     'role': spawn.get('agent_role', 'orchestrator'), 'agent_path': spawn.get('agent_path', 'root'),
                     'started_at': meta.get('timestamp'), 'cwd': meta.get('cwd'),
                     'source_file': str(path), 'native_file': target.relative_to(DRAFT).as_posix(),
                     'markdown_file': md.relative_to(DRAFT).as_posix(),
                     'original_bytes': len(original), 'original_sha256': sha(original),
                     'export_bytes': len(exported), 'export_sha256': sha(exported),
                     'original_ends_with_newline': original.endswith(b'\n'), 'unparseable_lines': invalid_lines,
                     'redactions': dict(Counter(redactions)), 'cli_version': meta.get('cli_version'),
                     'models': sorted(models), 'efforts': sorted(efforts), 'tool_calls': dict(tools),
                     'last_recorded_total_token_usage': last_usage,
                     'snapshot_only': sid == os.environ.get('CODEX_THREAD_ID')})
    write_json(DRAFT / 'traces/native-manifest.json', {
        'exported_at_utc': datetime.now(timezone.utc).isoformat(),
        'method': 'Read native session_meta headers; project-path match plus task-ID sidebar-index match; copy only selected sessions.',
        'project_path_match_ids': sorted(by_workspace), 'task_id_index_match_ids': sorted(by_task_id),
        'registered_missing': sorted(known - selected.keys()),
        'excluded_overview_session': OVERVIEW,
        'overview_reason': 'Known multi-task initialization overview; neither read nor exported as task development evidence.',
        'index_rows_are_original_filtered_lines': True,
        'comate_store_exists': (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
        'records': rows})
    shutil.copytree(ROOT / 'logs', DRAFT / 'logs', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('SettingsSyncSection.ets', 'SettingsSyncCards.ets'):
        src = ROOT / 'entry/src/main/ets/pages/settings' / name
        dst = DRAFT / 'traces/code-snapshots' / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    instructions = []
    for name in ('0-analyze.md', '1-do.md', '2-submit.md', '3-package.md'):
        common = ROOT.parent / 'common/spec-harness' / name
        local = ROOT / 'spec-harness' / name
        dst = DRAFT / 'traces/task-books' / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local, dst)
        instructions.append({'name': name, 'common_sha256': sha(common.read_bytes()),
                             'used_local_sha256': sha(local.read_bytes()),
                             'same_bytes': common.read_bytes() == local.read_bytes()})
    write_json(DRAFT / 'traces/task-books/version.json', {
        'common_git_toplevel': run(['git','-C',str(ROOT.parent/'common'),'rev-parse','--show-toplevel']).decode().strip(),
        'common_git_head': run(['git','-C',str(ROOT.parent/'common'),'rev-parse','HEAD']).decode().strip(),
        'common_scope_status': run(['git','-C',str(ROOT.parent/'common'),'status','--porcelain','--','spec-harness']).decode(),
        'files': instructions, 'spec_history_exists': (ROOT / 'spec/history').exists()})
    print(json.dumps({'sessions': len(rows), 'project_matches': len(by_workspace), 'task_index_matches': len(by_task_id),
                      'missing': sorted(known - selected.keys()), 'redacted_rows': sum(sum(x['redactions'].values()) for x in rows)}, ensure_ascii=False))


def excluded(path):
    parts = Path(path).parts
    if set(parts) & PRUNE or '.scratch' in parts:
        return True
    if path == 'local.properties' or path.startswith('.trae/documents/'):
        return True
    if path in DERIVED or path.startswith('.comate/submission-draft/validation/'):
        return True
    if OVERVIEW in path and path.endswith('.jsonl'):
        return True
    return path.endswith(('.pyc', '.p12', '.pfx', '.keystore', '.key'))


def snapshot():
    metadata = json.loads((ROOT / 'spec/metadata.json').read_text(encoding='utf-8'))
    base = metadata['base_commit']
    SCRATCH.mkdir(parents=True, exist_ok=True)
    index = SCRATCH / ('index-' + next(tempfile._get_candidate_names()))
    env = os.environ.copy(); env['GIT_INDEX_FILE'] = str(index)
    run(['git','read-tree',base], env=env)
    baseline = {}
    for line in run(['git','ls-tree','-rz','--full-tree',base]).split(b'\0'):
        if not line: continue
        info, name = line.split(b'\t',1)
        mode, typ, oid = info.split()
        if typ != b'blob': raise RuntimeError('Unsupported baseline object: ' + str(line))
        baseline[name.decode('utf-8')] = {'mode': mode.decode(), 'oid': oid.decode()}
    candidates = set(baseline)
    candidates.update(x.decode('utf-8') for x in run(['git','ls-files','-z']).split(b'\0') if x)
    candidates.update(x.decode('utf-8') for x in run(['git','ls-files','--others','--exclude-standard','-z']).split(b'\0') if x)
    final, binary, index_records = [], [], []
    for name in sorted(candidates):
        p = ROOT / name
        if excluded(name) or not p.is_file():
            if name in baseline:
                index_records.append(b'0 ' + b'0'*40 + b'\t' + name.encode() + b'\0')
            continue
        raw = p.read_bytes()
        mode = baseline.get(name,{}).get('mode','100644')
        if p.is_symlink(): raise RuntimeError('Symlink requires explicit review: ' + name)
        oid = run(['git','hash-object','-w','--no-filters','--stdin'],data=raw).decode().strip()
        index_records.append(f'{mode} {oid}\t{name}'.encode('utf-8') + b'\0')
        unchanged = baseline.get(name,{}).get('oid') == oid
        normalized = raw.replace(b'\r\n', b'\n')
        normalized_oid = hashlib.sha1(b'blob ' + str(len(normalized)).encode() + b'\0' + normalized).hexdigest()
        is_binary = b'\0' in raw[:8000]
        entry = {'path':name,'bytes':len(raw),'sha256':sha(raw),'git_blob':oid,'mode':mode,
                 'change':'unchanged' if unchanged else ('modified' if name in baseline else 'added'),
                 'baseline_windows_checkout_eol_only': not unchanged and baseline.get(name,{}).get('oid')==normalized_oid}
        final.append(entry)
        if is_binary:
            binary.append({**entry, 'same_as_baseline': unchanged,
                           'source': 'official bundled baseline, identical blob' if unchanged else 'task-local artifact; inspect associated trace'})
    run(['git','update-index','-z','--index-info'],env=env,data=b''.join(index_records))
    diff = run(['git','-c','core.quotePath=false','diff','--cached','--binary','--full-index','--no-ext-diff','--no-textconv',base,'--'],env=env)
    target = DRAFT / 'changes/final.diff'; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(diff)
    tree = run(['git','write-tree'],env=env).decode().strip()
    manifest = {'created_at_utc':datetime.now(timezone.utc).isoformat(), 'base_commit':base,
                'git_tree':tree,'file_count':len(final),'total_bytes':sum(x['bytes'] for x in final),
                'snapshot_digest_sha256':sha(json.dumps(final,sort_keys=True,separators=(',',':')).encode()),
                'diff_bytes':len(diff),'diff_sha256':sha(diff),
                'exact_excluded_derived':sorted(DERIVED),
                'excluded_prefixes':['.comate/submission-draft/.scratch/', '.comate/submission-draft/validation/'],
                'excluded_overview_session':OVERVIEW,
                'exclusion_rule':'See tools/prepare_materials.py:excluded. Build/cache/private-local files excluded. All remaining tracked and unignored files included, including spec, inputs, hypium_tests, logs, traces, workflow, system-config and stable .comate materials.',
                'deleted':[name for name in baseline if not excluded(name) and not (ROOT/name).is_file()],
                'files':final}
    write_json(DRAFT / 'changes/project-snapshot.json',manifest)
    write_json(DRAFT / 'changes/binary-files.json',binary)
    md = ['# Binary file inventory','', 'Includes retained baseline binaries and new task artifacts. Actual bytes remain in the project scope; final.diff uses --binary.', '', '| Path | Bytes | SHA-256 | Baseline identity |', '| --- | ---: | --- | --- |']
    md += [f'| `{x["path"]}` | {x["bytes"]} | `{x["sha256"]}` | {"same bundled blob" if x["same_as_baseline"] else "new/modified task artifact"} |' for x in binary]
    (DRAFT/'changes/binary-files.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps({'file_count':len(final),'diff_bytes':len(diff),'diff_sha256':sha(diff),'git_tree':tree,'binary_count':len(binary)},ensure_ascii=False))


def verify():
    manifest = json.loads((DRAFT/'changes/project-snapshot.json').read_text(encoding='utf-8'))
    patch = (DRAFT/'changes/final.diff').read_bytes()
    assert sha(patch)==manifest['diff_sha256']
    temp = Path(tempfile.mkdtemp(prefix='baseline-',dir=SCRATCH))
    clone = temp / 'project'
    branch = run(['git','symbolic-ref','--short','HEAD']).decode().strip()
    commands = []
    def call(args, cwd=ROOT):
        p=subprocess.run(args,cwd=cwd,capture_output=True)
        commands.append({'argv':args,'cwd':str(cwd),'exit_code':p.returncode,
                         'stdout':p.stdout.decode('utf-8','replace'),'stderr':p.stderr.decode('utf-8','replace')})
        if p.returncode: raise RuntimeError(commands[-1])
        return p.stdout
    call(['git','clone','--no-local','--no-hardlinks','--no-checkout','--single-branch','--branch',branch,str(ROOT),str(clone)])
    # Highest-precedence clone-local attributes override the baseline's text=auto.
    # core.autocrlf=false alone still permits explicit text attributes to choose CRLF.
    attributes = clone / '.git/info/attributes'
    attributes.parent.mkdir(parents=True, exist_ok=True)
    attributes.write_text('* -text -filter -working-tree-encoding\n', encoding='utf-8')
    options = ['git','-c','core.autocrlf=false','-c','core.eol=lf']
    call(options + ['checkout','--detach',manifest['base_commit']],cwd=clone)
    call(options + ['apply','--check','--binary',str(DRAFT/'changes/final.diff')],cwd=clone)
    call(options + ['apply','--binary',str(DRAFT/'changes/final.diff')],cwd=clone)
    mismatches=[]
    expected={x['path']:x for x in manifest['files']}
    actual={p.relative_to(clone).as_posix() for p in clone.rglob('*') if p.is_file() and '.git' not in p.relative_to(clone).parts}
    for name,row in expected.items():
        p=clone/name
        if not p.is_file() or sha(p.read_bytes())!=row['sha256']:
            mismatches.append(name)
        if not (ROOT/name).is_file() or sha((ROOT/name).read_bytes())!=row['sha256']:
            mismatches.append('live:'+name)
    extra=sorted(actual-expected.keys()); missing=sorted(expected.keys()-actual)
    protected=json.loads((ROOT/'workflow/do-final-integrity.json').read_text(encoding='utf-8'))['production_hashes']
    production={name:sha((ROOT/name).read_bytes())==digest for name,digest in protected.items()}
    result={'validated_at_utc':datetime.now(timezone.utc).isoformat(),'status':'pass' if not(mismatches or extra or missing) and all(production.values()) else 'fail',
            'base_commit':manifest['base_commit'],'diff_sha256':sha(patch),'snapshot_digest_sha256':manifest['snapshot_digest_sha256'],
            'checked_file_count':len(expected),'missing':missing,'extra':extra,'hash_mismatches':mismatches,
            'production_matches_do_acceptance':production,
            'temporary_clone':str(clone),'clone_source':'This task local Git repository; no upstream source or other task visited.',
            'clone_local_info_attributes':'* -text -filter -working-tree-encoding',
            'commands':commands,'all_files_compared':True}
    write_json(DRAFT/'validation/diff-validation.json',result)
    print(json.dumps({k:result[k] for k in ('status','checked_file_count','missing','extra','hash_mismatches','production_matches_do_acceptance')},ensure_ascii=False))
    if result['status']!='pass': raise SystemExit(1)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['collect','snapshot','verify'])
    args=parser.parse_args()
    {'collect':collect,'snapshot':snapshot,'verify':verify}[args.command]()
