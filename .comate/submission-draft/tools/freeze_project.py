"""Freeze a complete portable task project and verify a binary-capable patch.

Only submission materials are written. Source worktree, real Git index and HEAD
are never changed. The copy is the exact project input for stage 3.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
BASE = json.loads((ROOT / 'spec/metadata.json').read_text(encoding='utf-8-sig'))['base_commit']
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args, cwd=ROOT):
    result = subprocess.run(['git', *args], cwd=cwd, capture_output=True)
    if result.returncode:
        failure = OUT / 'checks' / ('freeze-command-failure-' + uuid.uuid4().hex[:8] + '.json')
        save(failure, {'command': ['git', *args], 'cwd': str(cwd), 'exit_code': result.returncode,
                       'stdout': result.stdout.decode('utf-8', 'replace'), 'stderr': result.stderr.decode('utf-8', 'replace')})
        raise RuntimeError(str(args) + ': see ' + str(failure))
    return result.stdout


def manifest(directory, exclude_git=False):
    result = []
    for path in sorted(directory.rglob('*')):
        relative = path.relative_to(directory).as_posix()
        if exclude_git and (relative == '.git' or relative.startswith('.git/')):
            continue
        if path.is_file():
            if path.is_symlink():
                raise RuntimeError('Unexpected symlink: ' + relative)
            raw = path.read_bytes()
            result.append({'path': relative, 'bytes': len(raw), 'sha256': sha(raw)})
    # Pure strings, not WindowsPath ordering: the identifier must be cross-platform.
    return sorted(result, key=lambda item: item['path'])


def is_binary(raw, path):
    if Path(path).suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bin', '.hap', '.zip', '.har', '.ico', '.ttf', '.woff', '.woff2', '.pdf'}:
        return True
    if b'\x00' in raw:
        return True
    try:
        raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return True
    return False


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    snapshot = OUT / 'traces/code-snapshots' / stamp / 'project'
    snapshot.mkdir(parents=True)
    entries = git('ls-files', '-c', '-o', '--exclude-standard', '-z').decode('utf-8').split('\0')
    exclusions = []
    selected = []
    for relative in sorted(set(p for p in entries if p)):
        if relative.startswith('.comate/submission-draft/'):
            continue
        source = ROOT / relative
        if not source.is_file():
            continue  # Tracked deletions are represented by absence and git add -A below.
        if source.is_symlink():
            raise RuntimeError('Unexpected source symlink: ' + relative)
        if OVERVIEW in source.name and relative.startswith('traces/native/'):
            exclusions.append({'path': relative, 'bytes': source.stat().st_size,
                               'sha256': sha(source.read_bytes()),
                               'reason': 'Initialization overview contains other tasks; excluded from submitted project and native evidence. Original retained locally, not read as feature evidence.'})
            continue
        target = snapshot / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        selected.append(relative)
    files = manifest(snapshot)
    canonical = ''.join(item['path'] + '\0' + item['sha256'] + '\n' for item in files).encode('utf-8')
    snapshot_hash = sha(canonical)
    work = OUT / 'checks/work' / stamp
    generator = work / 'patch-generator'
    verifier = work / 'baseline-apply-check'
    work.mkdir(parents=True)
    # Clone only the already available local task Git repository. No upstream access.
    branch = git('symbolic-ref', '--short', 'HEAD').decode('utf-8').strip()
    # Force local transport to fetch only this task branch; do not clone sibling refs.
    clone_args = ('clone', '--no-local', '--single-branch', '--no-tags', '--branch', branch,
                  '--no-checkout', '--quiet', str(ROOT))
    git(*clone_args, str(generator))
    git('config', 'core.autocrlf', 'false', cwd=generator)
    git('config', 'core.eol', 'lf', cwd=generator)
    git('checkout', '--detach', '--quiet', BASE, cwd=generator)
    # Preserve recorded CRLF bytes (notably raw logs) instead of silently normalizing them.
    (generator / '.git/info/attributes').write_text('* -text\n', encoding='utf-8')
    baseline_files = git('ls-files', '-z', cwd=generator).decode('utf-8').split('\0')
    selected_set = set(selected)
    for relative in baseline_files:
        if relative and relative not in selected_set:
            target = generator / relative
            if target.is_file():
                # Only individual files in the verified task-local temporary clone.
                if not target.resolve().is_relative_to(generator.resolve()):
                    raise RuntimeError('Deletion escaped temporary clone')
                target.unlink()
    shutil.copytree(snapshot, generator, dirs_exist_ok=True)
    git('-c', 'core.autocrlf=false', 'add', '-A', '-f', '--', '.', cwd=generator)
    diff = git('-c', 'core.quotepath=false', 'diff', '--cached', '--binary', '--full-index', '--no-ext-diff', '--no-renames', BASE, '--', '.', cwd=generator)
    diff_path = OUT / 'changes/final.diff'
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    diff_path.write_bytes(diff)
    diff_paths_raw = git('-c', 'core.quotepath=false', 'diff', '--cached', '--name-status', '-z', '--no-renames', BASE, cwd=generator).decode('utf-8').split('\0')
    changes = [{'status': diff_paths_raw[i], 'path': diff_paths_raw[i + 1]} for i in range(0, len(diff_paths_raw) - 1, 2)]
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check', BASE], cwd=generator, capture_output=True)
    # Historic logs/Markdown may contain original whitespace; report, never rewrite evidence.
    (OUT / 'checks/patch-whitespace.log').write_bytes(whitespace.stdout + whitespace.stderr)
    git(*clone_args, str(verifier))
    git('config', 'core.autocrlf', 'false', cwd=verifier)
    git('config', 'core.eol', 'lf', cwd=verifier)
    git('checkout', '--detach', '--quiet', BASE, cwd=verifier)
    (verifier / '.git/info/attributes').write_text('* -text\n', encoding='utf-8')
    precheck = git('apply', '--check', '--binary', '--whitespace=nowarn', str(diff_path), cwd=verifier)
    apply_output = git('-c', 'core.autocrlf=false', 'apply', '--binary', '--whitespace=nowarn', str(diff_path), cwd=verifier)
    reproduced = manifest(verifier, exclude_git=True)
    if files != reproduced:
        a = {x['path']: x for x in files}
        b = {x['path']: x for x in reproduced}
        errors = [p for p in sorted(set(a) | set(b)) if a.get(p) != b.get(p)]
        save(OUT / 'checks/reproduction-errors.json', errors)
        raise RuntimeError('Patch reconstruction differs: ' + repr(errors[:10]))
    # Compare ALL submitted files against original project, beyond just the key source files.
    original_mismatches = [item['path'] for item in files if sha((ROOT / item['path']).read_bytes()) != item['sha256']]
    if original_mismatches:
        raise RuntimeError('Project changed during freeze: ' + repr(original_mismatches))
    changed_set = {x['path'] for x in changes}
    eol_preservation = []
    for item in changes:
        if item['status'] != 'M':
            continue
        before = git('show', BASE + ':' + item['path'])
        after = (snapshot / item['path']).read_bytes()
        if before != after and before.replace(b'\r\n', b'\n') == after.replace(b'\r\n', b'\n'):
            eol_preservation.append(item['path'])
    save(OUT / 'changes/baseline-checkout-eol-preservation.json', {
        'reason': 'These files have no content change after CRLF/LF normalization. Patch retains actual original Windows checkout bytes so raw snapshot hashes match exactly; this is not a feature edit or generated build change.',
        'files': eol_preservation})
    binaries = []
    base_tree = set(p for p in git('ls-tree', '-r', '--name-only', BASE).decode('utf-8').splitlines())
    for item in files:
        raw = (snapshot / item['path']).read_bytes()
        if not is_binary(raw, item['path']):
            continue
        base_data = git('show', BASE + ':' + item['path']) if item['path'] in base_tree else None
        same = base_data is not None and sha(base_data) == item['sha256']
        binaries.append({**item, 'changed_from_base': item['path'] in changed_set,
                         'same_path_same_bytes_as_official_base': same,
                         'provenance': ('Official bundled baseline; identical bytes at same path.' if same else
                                        'Locally generated runtime screenshot/test upload evidence.' if item['path'].startswith('traces/') else
                                        'Additional binary; origin needs confirmation.')})
    hap_path = ROOT / 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    hap = {'path': hap_path.relative_to(ROOT).as_posix(), 'bytes': hap_path.stat().st_size,
           'sha256': sha(hap_path.read_bytes()), 'included_in_project': False, 'reason': 'Ignored build product; reproducible from source, not a source-resource change.'}
    audit = {
        'created_at_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': BASE,
        'snapshot_id': snapshot_hash, 'snapshot_path': snapshot.relative_to(OUT).as_posix(),
        'manifest_algorithm': 'SHA256(UTF8(concat(sorted(path + NUL + sha256 + LF))))',
        'file_count': len(files), 'total_bytes': sum(x['bytes'] for x in files), 'files': files,
        'exclusions': exclusions,
        'non_project_container': '.comate/submission-draft/** is the separate submission-material container and never recursively nested into project/. All other tracked and non-ignored project files are included.',
        'git_ignored_build_and_private_files': 'Existing .gitignore excludes .git, caches, oh_modules/node_modules, build/, .hvigor/, local.properties and IDE local data; dependencies are represented by manifests and locks.',
    }
    save(OUT / 'changes/project-manifest.json', audit)
    save(OUT / 'changes/changed-files.json', changes)
    save(OUT / 'changes/binary-files.json', {'base_commit': BASE, 'files': binaries, 'build_artifact': hap})
    validation = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'base_commit': BASE,
        'clone_source': str(ROOT), 'clone_destination': str(verifier), 'checkout': BASE,
        'commands': ['git clone --no-local --single-branch --no-tags --branch ' + branch + ' --no-checkout <local-task-repository> <temporary-clone>',
                     'git config core.autocrlf false', 'git config core.eol lf', 'git checkout --detach ' + BASE,
                     'git apply --check --binary --whitespace=nowarn <final.diff>', 'git -c core.autocrlf=false apply --binary --whitespace=nowarn <final.diff>'],
        'apply_check_exit_code': 0, 'apply_exit_code': 0,
        'all_files_reconstructed_byte_identically': files == reproduced,
        'all_snapshot_files_match_original_worktree': not original_mismatches,
        'reconstructed_files': len(reproduced), 'patch_bytes': len(diff), 'patch_sha256': sha(diff),
        'snapshot_id': snapshot_hash, 'changed_files': len(changes),
        'historic_whitespace_check_exit_code': whitespace.returncode,
        'historic_whitespace_log': 'checks/patch-whitespace.log',
        'real_git_index_and_head_untouched': True,
        'baseline_checkout_eol_only_entries': len(eol_preservation),
        'stage3_project_source': snapshot.relative_to(OUT).as_posix(),
        'limits': ['No claim that the raw workspace including unrelated initialization traces is package-ready.',
                   'Use the complete snapshot as project/, without adding the submission-material container recursively.',
                   'Submission metadata completion does not change the frozen project; regenerate patch if project contents change.'],
    }
    save(OUT / 'checks/diff-validation.json', validation)
    lines = ['# Binary resources and generated binary evidence', '', '| Path | Bytes | SHA-256 | Origin |', '| --- | ---: | --- | --- |']
    for item in binaries:
        lines.append('| `' + item['path'] + '` | ' + str(item['bytes']) + ' | `' + item['sha256'] + '` | ' + item['provenance'] + ' |')
    lines += ['', 'Unsigned build artifact (not part of project source): `' + hap['path'] + '`; ' + str(hap['bytes']) + ' bytes; SHA-256 `' + hap['sha256'] + '`.',
              '', 'Actual binary bytes are retained in the complete code snapshot. final.diff uses Git binary patches. No new product binary asset was introduced by the five production file edits.']
    (OUT / 'changes/binary-files.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({k: validation[k] for k in ('snapshot_id', 'changed_files', 'reconstructed_files', 'patch_bytes', 'patch_sha256', 'apply_check_exit_code', 'all_files_reconstructed_byte_identically')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
