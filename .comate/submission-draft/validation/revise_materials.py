"""Reopen failed material freeze only; preserve revision 1 and revalidate revision 2."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from datetime import datetime, timezone

R = Path(__file__).resolve().parents[3]
D = R / '.comate/submission-draft'
V = D / 'validation'
P = D / 'project'
HISTORY = V / 'revisions/revision1'
HISTORY.mkdir(parents=True, exist_ok=True)

def hs(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def rd(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def wr(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

commands = []
def run(args, cwd):
    p = subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True)
    commands.append({'command': [str(x) for x in args], 'cwd': str(cwd), 'exit_code': p.returncode,
                     'stdout': p.stdout.decode('utf-8', 'replace'), 'stderr': p.stderr.decode('utf-8', 'replace')})
    wr(V / 'revision2-commands.json', commands)
    if p.returncode:
        raise RuntimeError(str(args) + '\n' + p.stderr.decode('utf-8', 'replace'))
    return p.stdout

def main():
    assert R == Path('D:/HCUP/vg-spec8')
    assert not (HISTORY / 'final.diff').exists()
    for relative in ['changes/final.diff', 'changes/project-manifest.json', 'changes/patch-manifest.json',
                     'changes/name-status.txt', 'validation/apply-check.json']:
        shutil.copy2(D / relative, HISTORY / Path(relative).name)
    updates = []
    old = '没有从来源应用上游当前实现或相关修复历史获取本功能代码。'
    new = '在已核验的AI原生记录范围内，未见从来源应用上游当前实现或相关修复历史获取本功能代码的证据；这不代表对未知人工操作或团队额外来源的保证，相关声明仍【待补充】。'
    for rel in ['sources.fragment.md', 'tools/prepare_materials.py']:
        live = D / rel
        content = live.read_text(encoding='utf-8')
        assert content.count(old) == 1, rel
        save = HISTORY / 'materials' / rel; save.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live, save)
        content = content.replace(old, new)
        live.write_text(content, encoding='utf-8')
        target = P / '.comate/submission-draft' / rel
        target.write_bytes(live.read_bytes())
        updates.append('.comate/submission-draft/' + rel)
    rel = 'tools/freeze_and_diff.py'
    live = D / rel; content = live.read_text(encoding='utf-8')
    old_code = "            if name == 'local.properties':\n"
    new_code = "            if name == '.git':\n                reason = 'Git worktree metadata pointer; never a submitted project file'\n            elif name == 'local.properties':\n"
    assert content.count(old_code) == 1
    save = HISTORY / 'materials' / rel; save.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(live, save)
    live.write_text(content.replace(old_code, new_code), encoding='utf-8')
    (P / '.comate/submission-draft' / rel).write_bytes(live.read_bytes())
    updates.append('.comate/submission-draft/' + rel)
    manifest = rd(D / 'changes/project-manifest.json')
    for row in manifest['files']:
        if row['path'] in updates:
            path = P / row['path']; row.update({'bytes': path.stat().st_size, 'sha256': hs(path), 'source_sha256': hs(R / row['path'])})
    manifest['material_revision'] = 2
    manifest['material_revision_frozen_at_utc'] = datetime.now(timezone.utc).isoformat()
    manifest['technical_capture_time_note'] = 'original capture_id timestamp is trace export/identifier creation, not this later material freeze; official team freeze remains pending'
    manifest['total_bytes'] = sum(x['bytes'] for x in manifest['files'])
    wr(D / 'changes/project-manifest.json', manifest)
    generator = V / 'patch-generator'
    for rel in updates:
        shutil.copy2(P / rel, generator / rel)
    run(['git', 'add', '-A', '-f', '--', '.'], generator)
    patch = D / 'changes/final.diff'; temp = patch.with_suffix('.diff.next')
    run(['git', 'diff', '--cached', '--binary', '--full-index', '--no-ext-diff', '--no-textconv',
         '--no-renames', '--output=' + str(temp), manifest['base_commit'], '--'], generator)
    os.replace(temp, patch)
    changed = run(['git', 'diff', '--cached', '--name-status', '--no-renames', manifest['base_commit']], generator)
    (D / 'changes/name-status.txt').write_bytes(changed)
    receiver = V / 'apply-reconstruction-r2'
    assert not receiver.exists()
    assert receiver.resolve().is_relative_to(V.resolve())
    run(['git', 'clone', '--no-local', '--no-checkout', '--single-branch', '--branch', 'base/vg-spec8',
         '--no-tags', '--depth', '1', str(R), str(receiver)], R)
    for key, value in [('core.autocrlf', 'false'), ('core.eol', 'lf'), ('core.safecrlf', 'false')]:
        run(['git', 'config', key, value], receiver)
    (receiver / '.git/info/attributes').write_text('* -text -filter -ident -working-tree-encoding\n', encoding='utf-8')
    run(['git', 'checkout', '--detach', manifest['base_commit']], receiver)
    run(['git', 'apply', '--check', '--binary', str(patch)], receiver)
    run(['git', 'apply', '--binary', '--whitespace=nowarn', str(patch)], receiver)
    actual = {p.relative_to(receiver).as_posix(): p for p in receiver.rglob('*')
              if p.is_file() and '.git' not in p.relative_to(receiver).parts}
    expected = {x['path']: x for x in manifest['files']}
    missing = sorted(set(expected) - set(actual)); extra = sorted(set(actual) - set(expected))
    different = [x for x in sorted(set(actual) & set(expected))
                 if actual[x].stat().st_size != expected[x]['bytes'] or hs(actual[x]) != expected[x]['sha256']]
    assert not missing and not extra and not different
    prod = rd(R / 'workflow/production-freeze-01.json')
    assert all(hs(R / x['path']) == x['sha256'] and hs(P / x['path']) == x['sha256'] for x in prod)
    result = {'material_revision': 2, 'check_exit_code': 0, 'apply_exit_code': 0,
              'base_commit': manifest['base_commit'], 'capture_id': manifest['capture_id'],
              'expected_files': len(expected), 'reconstructed_files': len(actual), 'missing': missing,
              'extra': extra, 'different': different, 'all_files_equal': True,
              'production_inputs_unchanged': len(prod), 'manifest_count_checked': len(expected),
              'project_manifest_sha256': hs(D / 'changes/project-manifest.json'),
              'patch_bytes': patch.stat().st_size, 'patch_sha256': hs(patch),
              'validated_at': datetime.now(timezone.utc).isoformat()}
    wr(V / 'apply-check.json', result)
    wr(D / 'changes/patch-manifest.json', {**result, 'path': 'changes/final.diff',
        'project_manifest': 'changes/project-manifest.json', 'validation': 'validation/apply-check.json',
        'change_entries': len(changed.splitlines()), 'binary_files': len(rd(D / 'changes/binary-manifest.json'))})
    wr(V / 'revision2-resolution.json', {'reason': 'Independent audit rejected unsupported whole-task source assurance; narrowed to observed AI record scope, user declarations remain pending',
        'material_files_changed': updates, 'business_files_changed': [],
        'prior_patch_evidence_preserved': 'validation/revisions/revision1/',
        'worktree_git_metadata_enumerator_also_fixed': True, 'result': result})
    print(json.dumps(result, ensure_ascii=True), flush=True)

if __name__ == '__main__':
    main()
