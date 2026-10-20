import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('D:/HCUP/vg-spec8').resolve()
DRAFT = ROOT / '.comate/submission-draft'
OUT = DRAFT / 'validation/independent-rebuild'
CLONE = OUT / 'baseline'
PATCH = DRAFT / 'changes/final.diff'
MANIFEST = DRAFT / 'changes/project-manifest.json'
BASE = '9cbcf7292c8cc46955dc3b522ddbda41c66a61d9'
OUT.mkdir(parents=True, exist_ok=True)

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

commands = []
env = dict(os.environ)
env['GIT_CONFIG_NOSYSTEM'] = '1'
env['GIT_CONFIG_GLOBAL'] = os.devnull
env['GIT_TERMINAL_PROMPT'] = '0'

def run(args, cwd=ROOT):
    start = now()
    cp = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    index = len(commands) + 1
    stdout = OUT / f'{index:02d}-stdout.log'
    stderr = OUT / f'{index:02d}-stderr.log'
    stdout.write_bytes(cp.stdout)
    stderr.write_bytes(cp.stderr)
    record = {'command': args, 'cwd': str(cwd), 'started_at': start, 'ended_at': now(),
              'exit_code': cp.returncode, 'stdout': stdout.name, 'stderr': stderr.name}
    commands.append(record)
    (OUT / 'commands.json').write_text(json.dumps(commands, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=True), flush=True)
    if cp.returncode:
        raise RuntimeError(f'Command {index} failed: {cp.returncode}')
    return cp.stdout.decode('utf-8', 'replace').strip()

def files(root):
    return {p.relative_to(root).as_posix(): p for p in root.rglob('*')
            if p.is_file() and '.git' not in p.relative_to(root).parts}

def compare(expected, actual):
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    different = []
    checked = 0
    for path in sorted(set(expected) & set(actual)):
        record = expected[path]
        actual_path = actual[path]
        size = actual_path.stat().st_size
        sha = digest(actual_path)
        checked += 1
        if size != record['bytes'] or sha != record['sha256']:
            different.append({'path': path, 'expected_bytes': record['bytes'], 'actual_bytes': size,
                              'expected_sha256': record['sha256'], 'actual_sha256': sha})
    return {'expected_files': len(expected), 'actual_files': len(actual), 'compared_files': checked,
            'missing': missing, 'extra': extra, 'different': different,
            'all_files_equal': not (missing or extra or different)}

result = {'thread_id': '01a14549-2c5d-70c0-ab26-64feca32bde8', 'started_at': now(),
          'base_commit': BASE, 'environment_entry': 'D:/hongmengcup/Enter-HarmonyEnv.ps1',
          'scope': 'local baseline only; no remote or unrelated refs, no build/device commands'}
try:
    result['manifest_sha256_before'] = digest(MANIFEST)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
    expected = {item['path']: item for item in manifest['files']}
    result['capture_id'] = manifest['capture_id']
    result['manifest_declared_file_count'] = manifest['file_count']
    result['manifest_unique_file_count'] = len(expected)
    result['patch_bytes_before'] = PATCH.stat().st_size
    result['patch_sha256_before'] = digest(PATCH)
    result['project_comparison_before'] = compare(expected, files(DRAFT / 'project'))
    if CLONE.exists():
        raise RuntimeError('Dedicated reconstruction directory already exists; refusing reuse')
    run(['git', 'clone', '--no-local', '--no-checkout', '--single-branch', '--branch',
         'base/vg-spec8', '--no-tags', '--depth', '1', str(ROOT), str(CLONE)])
    for key, value in [('core.autocrlf', 'false'), ('core.eol', 'lf'), ('core.safecrlf', 'false')]:
        run(['git', 'config', key, value], CLONE)
    attributes = CLONE / '.git/info/attributes'
    attributes.write_text('* -text -eol -ident -filter -working-tree-encoding\n', encoding='utf-8')
    result['git_attribute_override'] = attributes.read_text(encoding='utf-8')
    run(['git', 'checkout', '--detach', BASE], CLONE)
    result['checked_out_head'] = run(['git', 'rev-parse', 'HEAD'], CLONE)
    run(['git', 'apply', '--check', '--binary', str(PATCH)], CLONE)
    result['check_exit_code'] = commands[-1]['exit_code']
    run(['git', 'apply', '--binary', '--whitespace=nowarn', str(PATCH)], CLONE)
    result['apply_exit_code'] = commands[-1]['exit_code']
    result['reconstructed_comparison'] = compare(expected, files(CLONE))
    result['project_comparison_after'] = compare(expected, files(DRAFT / 'project'))
    result['manifest_sha256_after'] = digest(MANIFEST)
    result['patch_bytes_after'] = PATCH.stat().st_size
    result['patch_sha256_after'] = digest(PATCH)
    result['frozen_inputs_unchanged'] = (result['manifest_sha256_before'] == result['manifest_sha256_after']
                                          and result['patch_sha256_before'] == result['patch_sha256_after'])
    result['passed'] = (result['checked_out_head'] == BASE and result['frozen_inputs_unchanged']
                        and result['project_comparison_before']['all_files_equal']
                        and result['project_comparison_after']['all_files_equal']
                        and result['reconstructed_comparison']['all_files_equal'])
except Exception as exc:
    result['error'] = repr(exc)
    result['passed'] = False
finally:
    result['ended_at'] = now()
    (OUT / 'reconstruction-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True), flush=True)
sys.exit(0 if result['passed'] else 1)
