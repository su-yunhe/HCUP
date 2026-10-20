"""Replay the submitted binary patch without invoking the producer's freeze code."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
VERIFY = OUT / 'verification'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def inventory(directory):
    rows = []
    for base, directories, files in os.walk(directory):
        directories[:] = [x for x in directories if x != '.git']
        for name in files:
            path = Path(base) / name
            rows.append({'path': path.relative_to(directory).as_posix(),
                         'bytes': path.stat().st_size, 'sha256': sha(path)})
    return sorted(rows, key=lambda x: x['path'])


def main():
    tag = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    scratch = VERIFY / ('replay-' + tag)
    report = {'started_at_utc': datetime.now(timezone.utc).isoformat(),
              'script_sha256': sha(Path(__file__)), 'python': sys.version,
              'platform': platform.platform(), 'commands': [],
              'scratch': scratch.relative_to(ROOT).as_posix(),
              'build_rerun': False, 'device_access': False, 'result': 'fail'}

    def command(argv, cwd=ROOT):
        started = datetime.now(timezone.utc).isoformat()
        proc = subprocess.run(argv, cwd=cwd, capture_output=True)
        number = len(report['commands']) + 1
        stdout_path = VERIFY / f'replay-command-{tag}-{number:02d}.stdout'
        stderr_path = VERIFY / f'replay-command-{tag}-{number:02d}.stderr'
        stdout_path.write_bytes(proc.stdout)
        stderr_path.write_bytes(proc.stderr)
        report['commands'].append({'argv': argv, 'cwd': str(cwd), 'started_at_utc': started,
            'completed_at_utc': datetime.now(timezone.utc).isoformat(), 'exit_code': proc.returncode,
            'stdout': stdout_path.relative_to(OUT).as_posix(), 'stdout_sha256': sha(stdout_path),
            'stderr': stderr_path.relative_to(OUT).as_posix(), 'stderr_sha256': sha(stderr_path)})
        if proc.returncode:
            raise RuntimeError(f'Command {number} exited {proc.returncode}')
        return proc.stdout

    try:
        manifest_path = OUT / 'changes/project-files.json'
        patch_path = OUT / 'changes/final.diff'
        manifest = read_json(manifest_path)
        report['manifest_sha256_before'] = sha(manifest_path)
        report['patch_sha256_before'] = sha(patch_path)
        report['patch_bytes'] = patch_path.stat().st_size
        metadata = read_json(ROOT / 'spec/metadata.json')
        base = metadata['base_commit']
        report['base_commit'] = base
        if manifest['base_commit'] != base or manifest['patch_sha256'] != report['patch_sha256_before']:
            raise ValueError('Declared baseline or patch hash does not match actual inputs')
        declared = manifest['files']
        expected = {}
        for item in declared:
            name = item['path']
            parts = PurePosixPath(name).parts
            if '\\' in name or PurePosixPath(name).is_absolute() or '..' in parts or ':' in name:
                raise ValueError('Unsafe project path: ' + name)
            if name in expected:
                raise ValueError('Duplicate project path: ' + name)
            expected[name] = item
        report['manifest_file_count'] = len(declared)
        report['pre_replay_workspace_mismatches'] = [name for name, x in expected.items()
            if not (ROOT / name).is_file() or (ROOT / name).stat().st_size != x['bytes'] or sha(ROOT / name) != x['sha256']]
        if report['pre_replay_workspace_mismatches']:
            raise ValueError('Workspace changed before independent replay')
        # The workspace is a worktree with a shared object database. Transfer only
        # the actual current task branch rather than copying all shared objects.
        branch = command(['git', 'symbolic-ref', '--quiet', '--short', 'HEAD']).decode().strip()
        if not branch:
            raise ValueError('Task branch is unavailable; refusing a broad clone')
        report['source_branch'] = branch
        command(['git', 'clone', '--no-local', '--single-branch', '--no-tags',
                 '--no-checkout', '--branch', branch, str(ROOT), str(scratch)])
        command(['git', '-c', 'core.autocrlf=false', 'checkout', '--detach', base], scratch)
        command(['git', '-c', 'core.autocrlf=false', 'apply', '--check', '--binary', str(patch_path)], scratch)
        command(['git', '-c', 'core.autocrlf=false', 'apply', '--binary', str(patch_path)], scratch)
        actual_rows = inventory(scratch)
        actual = {x['path']: x for x in actual_rows}
        report['missing'] = sorted(set(expected) - set(actual))
        report['extra'] = sorted(set(actual) - set(expected))
        report['mismatches'] = [{'path': name, 'expected': expected[name], 'actual': actual[name]}
            for name in sorted(set(expected) & set(actual)) if expected[name] != actual[name]]
        report['post_replay_workspace_mismatches'] = [name for name, x in expected.items()
            if not (ROOT / name).is_file() or (ROOT / name).stat().st_size != x['bytes'] or sha(ROOT / name) != x['sha256']]
        report['manifest_sha256_after'] = sha(manifest_path)
        report['patch_sha256_after'] = sha(patch_path)
        report['stable_inputs'] = (report['manifest_sha256_before'] == report['manifest_sha256_after'] and
                                   report['patch_sha256_before'] == report['patch_sha256_after'])
        report['actual_file_count'] = len(actual_rows)
        inventory_path = VERIFY / 'independent-replay-files.json'
        inventory_path.write_text(json.dumps(actual_rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        report['actual_inventory_sha256'] = sha(inventory_path)
        report['actual_aggregate_sha256'] = hashlib.sha256(''.join(
            x['path'] + '\0' + x['sha256'] + '\n' for x in actual_rows).encode()).hexdigest()
        report['declared_aggregate_sha256'] = manifest['aggregate_sha256']
        report['aggregate_match'] = report['actual_aggregate_sha256'] == manifest['aggregate_sha256']
        production = read_json(ROOT / 'workflow/do-final-fingerprint-02.json')
        report['production_mismatches'] = [x['path'] for x in production['files']
            if not (scratch / x['path']).is_file() or sha(scratch / x['path']) != x['sha256']]
        report['excluded_namespaces_in_replay'] = [name for name in actual
            if name.startswith('.comate/submission-draft/') or '01a13fc4-2611-7761-a580-1283e0c70541' in name]
        if not (report['missing'] or report['extra'] or report['mismatches'] or
                report['post_replay_workspace_mismatches'] or report['production_mismatches'] or
                report['excluded_namespaces_in_replay']) and report['stable_inputs'] and report['aggregate_match']:
            report['result'] = 'pass'
    except Exception:
        report['error'] = traceback.format_exc()
    finally:
        report['completed_at_utc'] = datetime.now(timezone.utc).isoformat()
        target = VERIFY / 'independent-replay.json'
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'report': target.relative_to(ROOT).as_posix(), 'result': report['result'],
                          'commands': len(report['commands']), 'files': report.get('actual_file_count'),
                          'missing': len(report.get('missing', [])), 'extra': len(report.get('extra', [])),
                          'mismatches': len(report.get('mismatches', [])), 'error': report.get('error')}, ensure_ascii=False))
    if report['result'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
