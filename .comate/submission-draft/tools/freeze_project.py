"""Freeze a complete explicit project tree using an isolated index, then replay it."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
BASE = json.loads((ROOT / 'spec/metadata.json').read_text())['base_commit']
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def run(args, cwd=ROOT, env=None, stdout=None):
    r = subprocess.run(args, cwd=cwd, env=env, stdout=stdout or subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode: raise RuntimeError(f'Command exit {r.returncode}: {args}\n' + r.stderr.decode(errors='replace')[-6000:])
    return r.stdout

def git(*args, **kw): return run(['git', *args], **kw)

def aggregate(files):
    return hashlib.sha256(''.join(f"{x['path']}\0{x['sha256']}\n" for x in files).encode()).hexdigest()

def freeze():
    changes = OUT / 'changes'; changes.mkdir(parents=True, exist_ok=True)
    work = OUT / '.work'; work.mkdir(parents=True, exist_ok=True)
    tracked = set(filter(None, git('ls-files', '-z').decode().split('\0')))
    others = set(filter(None, git('ls-files', '--others', '--exclude-standard', '-z').decode().split('\0')))
    # A globally ignored .comate process file must not silently disappear.
    extra_process = set()
    for directory, dirs, names in os.walk(ROOT / '.comate', followlinks=False):
        dirs[:] = [n for n in dirs if n != 'submission-draft' and not (Path(directory) / n).is_symlink() and not os.path.isjunction(Path(directory) / n)]
        for name in names:
            p = Path(directory) / name
            if not p.is_symlink(): extra_process.add(p.relative_to(ROOT).as_posix())
    paths, excluded = [], []
    for p in sorted(tracked | others | extra_process | {'AGENTS.md'}):
        reason = None
        if p.startswith('.comate/submission-draft/'):
            continue
        if p.startswith('traces/baseline-01/emulator-instances/'):
            reason = 'Task emulator runtime image/config/system rolling-log directory; cache, not project or selected functional evidence.'
        if p not in tracked and ('__pycache__' in Path(p).parts or Path(p).suffix.lower() in {'.pyc', '.pyo'}):
            reason = 'Generated Python bytecode cache; source test harness is retained.'
        if OVERVIEW in p and p.endswith('.jsonl'):
            reason = 'Unrelated cross-task setup overview raw conversation; excluded without reading contents.'
        f = ROOT / p
        if reason:
            excluded.append({'path': p, 'bytes': f.stat().st_size if f.exists() else None, 'reason': reason})
        else: paths.append(p)
    env = dict(os.environ, GIT_INDEX_FILE=str(work / 'freeze.index'))
    git('read-tree', BASE, env=env)
    nul = work / 'paths.nul'; nul.write_bytes(('\0'.join(paths) + '\0').encode())
    git('-c', 'core.autocrlf=false', '-c', 'core.safecrlf=false', 'add', '-f', '-A', '--pathspec-from-file=' + str(nul), '--pathspec-file-nul', env=env)
    tree = git('write-tree', env=env).decode().strip()
    # Git blobs preserve CRLF bytes because this isolated add disables autocrlf.
    with (changes / 'final.diff').open('wb') as f:
        git('diff', '--cached', '--binary', '--full-index', '--no-ext-diff', '--no-textconv', BASE, '--', env=env, stdout=f)
    files = []
    for p in paths:
        f = ROOT / p
        if f.is_file(): files.append({'path': p, 'bytes': f.stat().st_size, 'sha256': sha(f)})
    numstat = git('diff', '--cached', '--numstat', '-z', BASE, env=env).split(b'\0')
    binaries = []
    base_blobs = {x.split(b'\t', 1)[1].decode(): x.split()[2].decode() for x in git('ls-tree', '-rz', BASE).split(b'\0') if x}
    for item in numstat:
        if not item: continue
        a, b, rawpath = item.split(b'\t', 2)
        p = rawpath.decode(); f = ROOT / p
        binary_ext = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.hap', '.har', '.hsp', '.zip', '.gz', '.ttf', '.woff', '.woff2', '.mp3', '.wav', '.mp4', '.pdf', '.so', '.dll', '.exe'}
        git_binary = a == b'-' and b == b'-'
        if not git_binary and f.suffix.lower() not in binary_ext: continue
        if not f.is_file(): continue
        blob = git('hash-object', '--no-filters', str(f)).decode().strip()
        match = [name for name, value in base_blobs.items() if value == blob]
        binaries.append({'path': p, 'bytes': f.stat().st_size, 'sha256': sha(f), 'baseline_same_content_paths': match,
                         'origin': 'Same bytes as bundled baseline resource' if match else 'Task-generated local evidence/artifact; source context remains in task records',
                         'git_binary_patch': git_binary, 'zero_bytes': f.stat().st_size == 0,
                         'invalid_as_screenshot': f.stat().st_size == 0 and f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp'},
                         'retained_failure': f.stat().st_size == 0 and f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp'}})
    write(changes / 'binary-files.json', binaries)
    with (changes / 'binary-files.csv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['path', 'bytes', 'sha256', 'origin', 'baseline_same_content_paths'])
        for x in binaries: w.writerow([x['path'], x['bytes'], x['sha256'], x['origin'], ';'.join(x['baseline_same_content_paths'])])
    write(changes / 'excluded-files.json', {'excluded_actual_files': excluded, 'generated_output_namespace': '.comate/submission-draft/',
          'generated_output_reason': 'Material artifacts copied outside project in stage 3; excluding their own output namespace prevents final.diff recursion. All other .comate process files are included.',
          'git_ignored_policy': 'Dependency caches, build outputs, local settings are excluded by the unchanged baseline .gitignore. Ignored AGENTS.md is explicitly included for workflow evidence. No production tracked file is excluded.',
          'ignore_boundary_audit': 'changes/ignore-boundary-audit.json; pruned directory paths and every ignored nonpruned file/rule are enumerated. Generated BuildProfile.ets is ignored and not a tracked production change.',
          'stage3_contract': 'Copy exactly project-files.json paths as project/, fail on any current-byte drift, copy draft material files to task material destinations, never recursively copy draft into project/.'})
    manifest = {'task_id': 'cml-spec17', 'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': BASE,
                'head': git('rev-parse', 'HEAD').decode().strip(), 'git_tree_oid': tree, 'files': files, 'file_count': len(files),
                'aggregate_sha256': aggregate(files), 'deleted': [p for p in paths if not (ROOT / p).exists()],
                'patch': 'changes/final.diff', 'patch_bytes': (changes / 'final.diff').stat().st_size, 'patch_sha256': sha(changes / 'final.diff'),
                'excluded_actual_count': len(excluded), 'binary_change_count': len(binaries),
                'version_identifier': 'git-tree:' + tree, 'official_freeze_time': '【待补充】',
                'note': 'This local material snapshot time is not a user-supplied official freeze time.'}
    write(changes / 'project-files.json', manifest)
    (changes / 'name-status.txt').write_bytes(git('diff', '--cached', '--name-status', BASE, env=env))
    print(json.dumps({k: manifest[k] for k in ('file_count', 'git_tree_oid', 'aggregate_sha256', 'patch_bytes', 'binary_change_count', 'excluded_actual_count')}, ensure_ascii=False))

def verify():
    changes = OUT / 'changes'
    manifest = json.loads((changes / 'project-files.json').read_text(encoding='utf-8'))
    patch = changes / 'final.diff'
    if sha(patch) != manifest['patch_sha256']: raise ValueError('Patch hash mismatch')
    tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    replay = OUT / '.work' / ('replay-' + tag)
    if replay.exists(): raise ValueError('Refuse to overwrite replay directory')
    transcript = []
    def command(args, cwd=ROOT):
        r = subprocess.run(args, cwd=cwd, capture_output=True)
        transcript.append({'argv': args, 'cwd': str(cwd), 'exit_code': r.returncode, 'stdout': r.stdout.decode(errors='replace')[-3000:], 'stderr': r.stderr.decode(errors='replace')[-3000:]})
        write(changes / ('replay-commands-' + tag + '.json'), transcript)
        if r.returncode:
            failure = {'result': 'fail', 'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'commands': transcript, 'failed_command': transcript[-1]}
            write(changes / ('validation-' + tag + '.json'), failure)
            write(changes / 'validation.json', failure)
            raise RuntimeError(str(transcript[-1]))
    branch = git('symbolic-ref', '--short', 'HEAD').decode().strip()
    # The worktree shares a repository: transfer only this task branch's reachable
    # baseline, rather than copying other task refs or the common object store.
    command(['git', 'clone', '--no-local', '--single-branch', '--no-tags', '--no-checkout', '--branch', branch, str(ROOT), str(replay)])
    command(['git', '-c', 'core.autocrlf=false', 'checkout', '--detach', BASE], replay)
    command(['git', '-c', 'core.autocrlf=false', 'apply', '--check', '--binary', str(patch)], replay)
    command(['git', '-c', 'core.autocrlf=false', 'apply', '--binary', str(patch)], replay)
    mismatches = []
    for x in manifest['files']:
        for label, f in [('replayed', replay / x['path']), ('current_project', ROOT / x['path'])]:
            if not f.is_file() or sha(f) != x['sha256']:
                mismatches.append({'path': x['path'], 'where': label})
    for p in manifest['deleted']:
        if (replay / p).exists(): mismatches.append({'path': p, 'where': 'deleted path still present'})
    expected = {x['path'] for x in manifest['files']}
    actual = {p.relative_to(replay).as_posix() for p in replay.rglob('*') if p.is_file() and '.git' not in p.relative_to(replay).parts}
    extra = sorted(actual - expected); missing = sorted(expected - actual)
    current_names = set(filter(None, git('ls-files', '--cached', '--others', '--exclude-standard', '-z').decode().split('\0'))) | {'AGENTS.md'}
    for directory, dirs, names in os.walk(ROOT / '.comate', followlinks=False):
        dirs[:] = [n for n in dirs if n != 'submission-draft' and not (Path(directory) / n).is_symlink() and not os.path.isjunction(Path(directory) / n)]
        current_names.update((Path(directory) / n).relative_to(ROOT).as_posix() for n in names)
    current_names = {p for p in current_names if (ROOT / p).is_file() and not p.startswith('.comate/submission-draft/') and not p.startswith('traces/baseline-01/emulator-instances/') and not (OVERVIEW in p and p.endswith('.jsonl')) and '__pycache__' not in Path(p).parts and Path(p).suffix.lower() not in {'.pyc', '.pyo'}}
    current_extra = sorted(current_names - expected)
    current_missing = sorted(expected - current_names)
    production = json.loads((ROOT / 'workflow/do-final-fingerprint-02.json').read_text())
    production_drift = [x['path'] for x in production['files'] if sha(ROOT / x['path']) != x['sha256']]
    result = {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': BASE,
              'git_tree_oid': manifest['git_tree_oid'], 'patch_sha256': sha(patch), 'patch_bytes': patch.stat().st_size,
              'commands': transcript, 'checked_files': len(manifest['files']), 'mismatches': mismatches, 'extra': extra, 'missing': missing,
              'current_extra': current_extra, 'current_missing': current_missing,
              'production_drift_from_1do': production_drift, 'result': 'pass' if not (mismatches or extra or missing or production_drift or current_extra or current_missing) else 'fail',
              'replay_directory': str(replay), 'replay_is_scratch_not_deliverable': True}
    write(changes / ('validation-' + tag + '.json'), result)
    write(changes / 'validation.json', result)
    print(json.dumps({k: result[k] for k in ('result', 'checked_files', 'patch_bytes', 'mismatches', 'extra', 'missing', 'production_drift_from_1do')}, ensure_ascii=False))
    if result['result'] != 'pass': raise SystemExit(1)

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ('freeze', 'verify'): raise SystemExit('freeze_project.py freeze|verify')
    {'freeze': freeze, 'verify': verify}[sys.argv[1]]()
