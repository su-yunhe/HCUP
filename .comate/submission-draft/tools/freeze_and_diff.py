"""Freeze all task files, create a binary patch, and reconstruct it from local base.

Output containers are explicit and finite. No production edits, network access,
commits, or external submissions. Temporary Git repositories stay in validation/.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / '.comate/submission-draft'
PROJECT = DRAFT / 'project'
VALID = DRAFT / 'validation'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

COMMANDS = []

def run(args, cwd=ROOT, stdin=None):
    p = subprocess.run([str(x) for x in args], cwd=cwd, input=stdin, capture_output=True)
    COMMANDS.append({'command': [str(x) for x in args], 'cwd': str(cwd), 'exit_code': p.returncode,
                     'stdout': p.stdout.decode('utf-8', 'replace'), 'stderr': p.stderr.decode('utf-8', 'replace')})
    write(VALID / 'commands.json', COMMANDS)
    if p.returncode:
        raise RuntimeError(f'Failed command {args}: {p.stderr[:500]!r}')
    return p.stdout

def private_values():
    values = set()
    for row in load(DRAFT / 'traces/session-index.json'):
        p = Path(row['source_path'])
        meta = json.loads(p.open(encoding='utf-8').readline())['payload']
        for key in ['creator_user_id', 'creator_account_id']:
            if meta.get(key):
                values.add(meta[key])
    return values

def cleaner(values):
    def clean(data):
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            return data, []
        edits = []
        for value in sorted(values):
            count = text.count(value)
            if count:
                text = text.replace(value, '[REDACTED_ACCOUNT_IDENTIFIER]')
                edits.append({'kind': 'account_identifier', 'occurrences': count})
        text, count = re.subn(r'MCowBQYDK2VwAyEA[A-Za-z0-9+/=]+', '[REDACTED_EPHEMERAL_VERIFICATION_VALUE]', text)
        if count:
            edits.append({'kind': 'ephemeral_verification_value', 'occurrences': count})
        return (text.encode('utf-8') if edits else data), edits
    return clean

def manifest(root):
    result = []
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != '.git')
        for name in sorted(files):
            p = Path(directory) / name
            data = p.read_bytes()
            result.append({'path': p.relative_to(root).as_posix(), 'bytes': len(data), 'sha256': sha(data)})
    return sorted(result, key=lambda item: item['path'])

def clone_base(name, base):
    path = VALID / name
    assert not path.exists(), f'Will not overwrite evidence directory {path}'
    assert path.resolve().is_relative_to(VALID.resolve())
    run(['git', 'clone', '--no-local', '--no-checkout', '--single-branch', '--branch',
         'base/vg-spec8', '--no-tags', '--depth', '1', str(ROOT), str(path)])
    run(['git', 'config', 'core.autocrlf', 'false'], path)
    run(['git', 'config', 'core.eol', 'lf'], path)
    run(['git', 'config', 'core.safecrlf', 'false'], path)
    attrs = path / '.git/info/attributes'
    attrs.parent.mkdir(parents=True, exist_ok=True)
    attrs.write_text('* -text -filter -ident -working-tree-encoding\n', encoding='utf-8')
    run(['git', 'checkout', '--detach', base], path)
    assert run(['git', 'rev-parse', 'HEAD'], path).decode().strip() == base
    return path

def main():
    assert ROOT == Path('D:/HCUP/vg-spec8')
    assert not PROJECT.exists(), 'Freeze is immutable; do not overwrite it'
    context = load(VALID / 'context.json')
    base = context['base_commit']
    before = load(ROOT / 'workflow/production-freeze-01.json')
    assert all(sha((ROOT / r['path']).read_bytes()) == r['sha256'] for r in before)
    clean = cleaner(private_values())
    # Native-derived code snapshots are explicitly copies, never new historical events.
    files = ['entry/src/main/ets/pages/settings/SettingsSyncSection.ets',
             'entry/src/main/ets/pages/settings/SettingsWebDavConfigPanel.ets',
             'entry/src/main/ets/pages/settings/WebDavRestoreConfirmDialog.ets',
             'entry/src/main/ets/pages/SettingsPage.ets',
             'entry/src/main/ets/pages/index/components/TopNavigation.ets']
    code_rows = []
    for rel in files:
        source = ROOT / rel
        target = DRAFT / 'traces/code-changes/final' / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        p = subprocess.run(['git', 'show', base + ':' + rel], cwd=ROOT, capture_output=True)
        if p.returncode == 0:
            old = DRAFT / 'traces/code-changes/base' / rel
            old.parent.mkdir(parents=True, exist_ok=True); old.write_bytes(p.stdout)
        code_rows.append({'path': rel, 'final_sha256': sha(source.read_bytes()),
                          'base_present': p.returncode == 0,
                          'base_blob_sha256': sha(p.stdout) if p.returncode == 0 else None})
    write(DRAFT / 'traces/code-changes/index.json', {'kind': 'retrospective copies of actual base and validated source, not fabricated edit history', 'files': code_rows})
    team = ROOT.parent / 'common/spec-harness/team.yaml'
    dest = DRAFT / 'provenance/inputs/team.yaml'; dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(team, dest)
    shutil.copy2(ROOT / 'spec/submit-input.yaml', dest.parent / 'submit-input.yaml')

    excludes = []; candidates = []
    skip_dirs = {'.git', 'oh_modules', 'node_modules', '.hvigor', 'build', '.idea', '.preview', '.test',
                 '.cxx', '.clangd', '.appanalyzer', '__pycache__'}
    outputs = {'.comate/submission-draft/project', '.comate/submission-draft/changes', '.comate/submission-draft/validation'}
    for directory, dirs, files_here in os.walk(ROOT, followlinks=False):
        kept = []
        for name in sorted(dirs):
            p = Path(directory) / name; rel = p.relative_to(ROOT).as_posix()
            junction = getattr(p, 'is_junction', lambda: False)()
            if rel in outputs:
                reason = 'derived output container: immutable project, patch/manifest, or validation repositories; self-reference excluded'
            elif name in skip_dirs or rel == '.trae/documents':
                reason = 'Git metadata or generated dependency/build/IDE/Python cache; not task source evidence'
            elif p.is_symlink() or junction:
                reason = 'linked tool/runtime directory; not a physical independent project file tree'
            else:
                kept.append(name); continue
            excludes.append({'path': rel + '/', 'kind': 'directory', 'reason': reason})
        dirs[:] = kept
        for name in sorted(files_here):
            p = Path(directory) / name; rel = p.relative_to(ROOT).as_posix()
            reason = None
            if name == '.git':
                reason = 'Git worktree metadata pointer; never a submitted project file'
            elif name == 'local.properties':
                reason = 'private local SDK location; regenerate using configured SDK tools'
            elif name in {'.DS_Store', 'Thumbs.db'} or p.suffix.lower() in {'.pyc', '.pyo'}:
                reason = 'generated OS/Python cache'
            elif OVERVIEW in name and rel.startswith('traces/native/'):
                reason = 'mixed initialization overview includes other tasks; full raw overview is not a vg-spec8-only record'
            elif name in {'00-before-install.png', '00-before-install.json'} and rel.startswith('logs/analysis-baseline/'):
                reason = 'known unrelated pre-install device UI; baseline-notes explicitly disclaims task evidence'
            elif p.is_symlink():
                reason = 'linked external file; not a physical source artifact'
            if reason:
                excludes.append({'path': rel, 'kind': 'file', 'bytes': p.stat().st_size,
                                 'sha256': sha(p.read_bytes()), 'reason': reason})
            else:
                assert p.resolve().is_relative_to(ROOT.resolve()), p
                candidates.append((rel, p))
    # Enumeration completes before output tree is created: no recursive traversal.
    PROJECT.mkdir()
    rows = []; redactions = []
    for rel, source in sorted(candidates):
        original = source.read_bytes(); data, edits = clean(original)
        target = PROJECT / rel; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        rows.append({'path': rel, 'bytes': len(data), 'sha256': sha(data), 'source_sha256': sha(original)})
        if edits:
            redactions.append({'path': rel, 'source_sha256': sha(original), 'export_sha256': sha(data), 'changes': edits})
    write(DRAFT / 'changes/exclusions.json', {'output_boundary': sorted(outputs), 'excluded': excludes,
          'scope': 'only named recursive artifacts, caches/private environment, and evidenced unrelated original records excluded',
          'original_files_deleted_or_modified': False})
    write(DRAFT / 'changes/project-redactions.json', redactions)
    write(DRAFT / 'changes/project-manifest.json', {'capture_id': context['capture_id'],
          'technical_capture_time': context['captured_at_utc'], 'official_team_freeze_time': '【待补充】',
          'base_commit': base, 'project_directory': 'project', 'files': rows, 'file_count': len(rows),
          'total_bytes': sum(x['bytes'] for x in rows)})
    expected = manifest(PROJECT)
    expected_by_path = {x['path']: x for x in expected}
    assert all(expected_by_path[r['path']]['sha256'] == r['sha256'] for r in before)
    generator = clone_base('patch-generator', base)
    base_tree = {}
    tree = run(['git', 'ls-tree', '-r', '-z', base], generator)
    for item in tree.split(b'\0'):
        if not item:continue
        header, rawpath = item.split(b'\t', 1)
        mode, typ, oid = header.decode().split()
        assert typ == 'blob', 'Submodules need explicit handling'
        base_tree[os.fsdecode(rawpath)] = {'mode': mode, 'oid': oid}
    # Remove only baseline tracked files absent from this frozen project, within clone.
    for rel in base_tree:
        path = generator / rel
        if rel not in expected_by_path and path.exists():
            assert path.resolve().is_relative_to(generator.resolve())
            assert '.git' not in Path(rel).parts
            path.unlink()
    for row in expected:
        source = PROJECT / row['path']; target = generator / row['path']
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
    run(['git', 'add', '-A', '-f', '--', '.'], generator)
    patch = DRAFT / 'changes/final.diff'
    run(['git', 'diff', '--cached', '--binary', '--full-index', '--no-ext-diff', '--no-textconv',
         '--no-renames', '--output=' + str(patch), base, '--'], generator)
    changed = run(['git', 'diff', '--cached', '--name-status', '--no-renames', base], generator).decode('utf-8')
    (DRAFT / 'changes/name-status.txt').write_text(changed, encoding='utf-8')
    binaries = []
    for row in expected:
        data = (PROJECT / row['path']).read_bytes()
        binary = b'\0' in data[:8000] or Path(row['path']).suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.db', '.hap'}
        if not binary:continue
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        original = base_tree.get(row['path'])
        same = original is not None and original['oid'] == blob
        binaries.append({**row, 'same_as_baseline_resource': same,
                         'origin': 'same bytes as official bundled baseline' if same else 'task evidence/test snapshot/generated HAP; not a new App visual asset' if any(x in row['path'].split('/') for x in ['logs', 'traces', 'artifacts']) else 'see task source/provenance disclosure',
                         'actual_file_in_project': True})
    write(DRAFT / 'changes/binary-manifest.json', binaries)
    receiver = clone_base('apply-reconstruction', base)
    run(['git', 'apply', '--check', '--binary', str(patch)], receiver)
    run(['git', 'apply', '--binary', '--whitespace=nowarn', str(patch)], receiver)
    actual = manifest(receiver)
    exp = {r['path']: r for r in expected}; got = {r['path']: r for r in actual}
    missing = sorted(set(exp) - set(got)); extra = sorted(set(got) - set(exp))
    different = [p for p in sorted(set(exp) & set(got)) if exp[p] != got[p]]
    assert not missing and not extra and not different, (missing[:5], extra[:5], different[:5])
    live_changed = [r['path'] for r in before if sha((ROOT / r['path']).read_bytes()) != r['sha256']]
    assert not live_changed
    write(VALID / 'apply-check.json', {'check_exit_code': 0, 'apply_exit_code': 0,
          'base_commit': base, 'capture_id': context['capture_id'], 'expected_files': len(expected),
          'reconstructed_files': len(actual), 'missing': missing, 'extra': extra, 'different': different,
          'all_files_equal': True, 'production_inputs_unchanged': len(before),
          'private_line_endings_note': 'temporary .git/info/attributes disables filters; project bytes not normalized',
          'patch_bytes': patch.stat().st_size, 'patch_sha256': sha(patch.read_bytes()),
          'project_manifest_sha256': sha((DRAFT / 'changes/project-manifest.json').read_bytes()),
          'validated_at': datetime.now(timezone.utc).isoformat()})
    write(DRAFT / 'changes/patch-manifest.json', {'path': 'changes/final.diff', 'bytes': patch.stat().st_size,
          'sha256': sha(patch.read_bytes()), 'base_commit': base, 'capture_id': context['capture_id'],
          'project_manifest': 'changes/project-manifest.json', 'validation': 'validation/apply-check.json',
          'change_entries': len(changed.splitlines()), 'binary_files': len(binaries)})
    print(json.dumps({'project_files': len(expected), 'patch_bytes': patch.stat().st_size,
                      'patch_sha256': sha(patch.read_bytes()), 'apply_check': 'pass',
                      'all_files_equal': True, 'business_inputs_unchanged': len(before)}))

if __name__ == '__main__':
    main()
