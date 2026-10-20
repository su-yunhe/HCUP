"""Independent content/structure checks for the frozen single-task draft."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
VERIFY = OUT / 'verification'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.ico', '.hap', '.har', '.hsp', '.zip', '.gz', '.ttf', '.woff', '.woff2', '.mp3', '.wav', '.mp4', '.pdf', '.so', '.dll', '.exe'}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def text(path):
    return path.read_text(encoding='utf-8-sig')


def git_blob_sha(path):
    h = hashlib.sha1()
    h.update(b'blob ' + str(path.stat().st_size).encode() + b'\0')
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
              'script_sha256': sha(Path(__file__)), 'checks': {}, 'commands': []}
    tracked_inputs = [OUT / name for name in ('build.md', 'trace-index.md', 'sources.fragment.md',
        'solution.fragment.md', 'submission.json.fragment', 'human-changes.md', 'missing-fields.md',
        'auto-filled-facts.md', 'evidence-facts.json', 'package-layout.json', 'changes/project-files.json',
        'changes/final.diff', 'changes/binary-files.json', 'changes/excluded-files.json',
        'changes/ignore-boundary-audit.json', 'README.md', 'handoff.md')]
    before = {p.relative_to(OUT).as_posix(): sha(p) for p in tracked_inputs}
    result['input_sha256_before'] = before
    manifest = read_json(OUT / 'changes/project-files.json')
    facts = read_json(OUT / 'evidence-facts.json')
    binaries = read_json(OUT / 'changes/binary-files.json')
    indexed = {x['path']: x for x in manifest['files']}
    index_text = text(OUT / 'trace-index.md')
    build = text(OUT / 'build.md')
    solution = text(OUT / 'solution.fragment.md')
    missing = text(OUT / 'missing-fields.md')
    checks = result['checks']

    def command(argv):
        proc = subprocess.run(argv, cwd=ROOT, capture_output=True)
        number = len(result['commands']) + 1
        out = VERIFY / f'content-command-{number:02d}.stdout'
        err = VERIFY / f'content-command-{number:02d}.stderr'
        out.write_bytes(proc.stdout)
        err.write_bytes(proc.stderr)
        result['commands'].append({'argv': argv, 'exit_code': proc.returncode,
            'stdout': out.relative_to(OUT).as_posix(), 'stdout_sha256': sha(out),
            'stderr': err.relative_to(OUT).as_posix(), 'stderr_sha256': sha(err)})
        if proc.returncode:
            raise RuntimeError('Content command failed: ' + str(argv))
        return proc.stdout

    checks['required_materials'] = all((OUT / p).is_file() and (OUT / p).stat().st_size > 0 for p in (
        'changes/final.diff', 'build.md', 'trace-index.md', 'sources.fragment.md', 'solution.fragment.md',
        'submission.json.fragment')) and any((OUT / 'traces/native').glob('*.jsonl')) and any((OUT / 'logs').rglob('*'))
    template = text(Path('D:/SWE-OpenHarmony/templates/trace-index.md'))
    labels = [line[2:].strip().rstrip('：:') for line in template.splitlines() if line.startswith('- ')]
    result['trace_fields'] = [{'field': label, 'present': label in index_text} for label in labels]
    checks['all_24_official_trace_fields'] = len(labels) == 24 and all(x['present'] for x in result['trace_fields'])
    result['build_private_path_matches'] = re.findall(r'(?<![A-Za-z])[A-Za-z]:[\\/][^\s`]*|/Users/[^\s`]+|/home/[^\s`]+', build)
    checks['build_has_no_machine_private_absolute_path'] = not result['build_private_path_matches']
    result['build_delivered_dependencies'] = {p: p in indexed for p in (
        'workflow/do-entry/README.md', 'workflow/do-entry/prepare.py', 'workflow/do-entry/build.ps1',
        'workflow/do-entry/run.ps1', 'workflow/do-entry/production_probe.py', 'test-harness/requirements.txt',
        'AppScope/app.json5', 'entry/src/main/module.json5', 'oh-package.json5', 'oh-package-lock.json5', 'build-profile.json5')}
    checks['build_named_dependencies_delivered'] = all(result['build_delivered_dependencies'].values())
    checks['build_scope_and_portability_disclosed'] = all(x in build for x in (
        'ohpm install --all', 'assembleHap', 'install -r', 'aa start', 'com.joker.coolmall', 'EntryAbility',
        'DEVECO_STUDIO_HOME', 'DEVECO_SDK_HOME', '未验证无修改跨机运行', '普通', '认证'))
    fragment = read_json(OUT / 'submission.json.fragment')
    targets = {'project_path': 'tasks/cml-spec17/project', 'build_instructions': 'tasks/cml-spec17/build.md',
               'trace_index': 'tasks/cml-spec17/trace-index.md'}
    result['fragment'] = fragment
    checks['fragment_paths_and_scope'] = (fragment.get('task_id') == 'cml-spec17' and fragment.get('status') == 'submitted' and
        set(fragment) == {'task_id', 'status', *targets} and all(fragment.get(k) == v for k, v in targets.items()) and
        all(not PurePosixPath(fragment[k]).is_absolute() and '\\' not in fragment[k] and '..' not in PurePosixPath(fragment[k]).parts for k in targets))
    user_fields = ['version', 'contact', 'freeze_time', 'members[].name', 'members[].work', 'source_guard',
                   'human_edits', 'known_issues', 'extra_sources', 'md_export_dir']
    result['missing_user_fields'] = [{'field': x, 'placeholder_line': any(x in line and '【待补充】' in line for line in missing.splitlines())} for x in user_fields]
    checks['user_empty_fields_not_guessed'] = all(x['placeholder_line'] for x in result['missing_user_fields'])
    stage = read_json(ROOT / 'workflow/do-stage-result-03.json')
    result['known_boundaries'] = [{'id': x['id'], 'disclosed': x['id'] in solution and x['status'] in solution}
                                  for x in stage['additional_boundary_not_run'] + stage['external_blocked']]
    checks['all_existing_unrun_and_blocked_boundaries_disclosed'] = all(x['disclosed'] for x in result['known_boundaries'])
    checks['bounded_completion_and_no_official_score'] = all(x in solution for x in (
        '正常23', '故障3', '26', '42', '2项普通', '不代表认证线上', 'official hidden tests', 'unknown',
        'adopted_bounded_strategy_not_spec_explicit', '没有上传', '团队ZIP'))
    result['token_table'] = []
    for session in facts['native_sessions']:
        sid = session['session_id']
        match = re.search(r'^\| `' + re.escape(sid) + r'` \| ([^|]+) \| (\d+) / (\d+) / (\d+) \|$', index_text, re.M)
        info = session.get('last_reported_token_info') or {}
        use = info.get('total_token_usage') or {}
        expected = [use.get('input_tokens'), use.get('output_tokens'), use.get('total_tokens')]
        actual = [int(match.group(n)) for n in (2, 3, 4)] if match else None
        result['token_table'].append({'id': sid, 'actual': actual, 'expected': expected, 'match': actual == expected,
                                       'native_link_present': Path(session['native']).name in index_text})
    checks['all_native_ids_links_and_token_snapshots_current'] = all(x['match'] and x['native_link_present'] for x in result['token_table'])

    stats = command(['git', 'apply', '--numstat', '-z', str(OUT / 'changes/final.diff')])
    expected_binaries = set()
    for line in stats.split(b'\0'):
        if not line:
            continue
        a, b, name = line.split(b'\t', 2)
        path = name.decode()
        if path in indexed and ((a == b'-' and b == b'-') or Path(path).suffix.lower() in EXTENSIONS):
            expected_binaries.add(path)
    declared_binaries = {x['path'] for x in binaries}
    result['binary_inventory'] = {'expected_count': len(expected_binaries), 'declared_count': len(binaries),
        'missing': sorted(expected_binaries - declared_binaries), 'extra': sorted(declared_binaries - expected_binaries),
        'duplicates': [p for p, n in Counter(x['path'] for x in binaries).items() if n != 1], 'mismatches': [], 'same_source_mismatches': []}
    base_blobs = {}
    for line in command(['git', 'ls-tree', '-rz', manifest['base_commit']]).split(b'\0'):
        if line:
            meta, name = line.split(b'\t', 1)
            base_blobs[name.decode()] = meta.split()[2].decode()
    for item in binaries:
        f = ROOT / item['path']
        if not f.is_file() or f.stat().st_size != item['bytes'] or sha(f) != item['sha256']:
            result['binary_inventory']['mismatches'].append(item['path'])
            continue
        own_oid = git_blob_sha(f)
        actual_matches = {name for name, oid in base_blobs.items() if oid == own_oid}
        if actual_matches != set(item.get('baseline_same_content_paths', [])):
            result['binary_inventory']['same_source_mismatches'].append(item['path'])
    zero = next((x for x in binaries if x['path'] == 'traces/local-entry-02/27-roundtrip-remark-visible.png'), {})
    result['zero_byte_failure_screenshot'] = zero
    checks['binary_inventory_and_same_source_verified'] = not any(result['binary_inventory'][x] for x in (
        'missing', 'extra', 'duplicates', 'mismatches', 'same_source_mismatches')) and zero.get('bytes') == 0 and zero.get('invalid_as_screenshot') and zero.get('retained_failure')
    result['project_categories'] = {prefix: sum(name.startswith(prefix) for name in indexed) for prefix in (
        'spec/', 'spec-harness/', 'inputs/', 'hypium_tests/', 'test-harness/', 'workflow/', 'traces/', 'logs/', 'system-config/', '.comate/')}
    checks['all_process_categories_delivered'] = all(result['project_categories'][x] > 0 for x in result['project_categories'] if x != '.comate/')
    checkpoint_path = ROOT / 'workflow/submit-stage-result-01.json'
    if checkpoint_path.is_file():
        checkpoint = read_json(checkpoint_path)
        closure = []
        for item in checkpoint['pre_close_checks']:
            path = ROOT / item['path']
            closure.append({'source_path': item['path'], 'hash_matches': path.is_file() and sha(path) == item['sha256'],
                            'actual_result': read_json(path).get('result') if path.is_file() else None})
        result['immutable_pre_close_checks'] = closure
        checks['workflow_closure_uses_real_immutable_bounded_evidence'] = (all(x['hash_matches'] and x['actual_result'] == 'pass' for x in closure)
            and len(closure) == 3 and checkpoint.get('formal_submission_ready') is False
            and checkpoint.get('pre_close_validated_tree') != manifest['git_tree_oid']
            and 'workflow/submit-stage-result-01.json' in indexed)
    else:
        result['immutable_pre_close_checks'] = []
        checks['workflow_closure_uses_real_immutable_bounded_evidence'] = False
    result['unexpected_noise_paths'] = [name for name in indexed if '.git' in PurePosixPath(name).parts or
        any(x in PurePosixPath(name).parts for x in ('build', 'oh_modules', 'node_modules', '.hvigor', '__pycache__')) or
        name.endswith('/BuildProfile.ets') or name.startswith('.comate/submission-draft/') or OVERVIEW in name]
    checks['noise_overview_and_recursive_output_excluded'] = not result['unexpected_noise_paths']
    ignored = read_json(OUT / 'changes/ignore-boundary-audit.json')
    result['ignore_audit_keys'] = list(ignored)

    # Validate top-level authored Markdown links in their future package locations.
    package_files = {'tasks/cml-spec17/project/' + name for name in indexed}
    layout = read_json(OUT / 'package-layout.json')
    mapping = {x['source']: x['package_destination'] for x in layout['mappings']}
    result['layout_mapped_material_count'] = len(mapping)
    result['layout_unsafe_destinations'] = [x for x in layout['mappings'] if
        PurePosixPath(x['package_destination']).is_absolute() or '\\' in x['package_destination'] or
        '..' in PurePosixPath(x['package_destination']).parts or ':' in x['package_destination']]
    result['layout_duplicate_destinations'] = [p for p, n in Counter(x['package_destination'] for x in layout['mappings']).items() if n > 1]
    result['unmapped_material_files'] = []
    for base, dirs, files in os.walk(OUT):
        relbase = Path(base).relative_to(OUT)
        dirs[:] = [d for d in dirs if d not in ('.work', '.git', '__pycache__') and not (relbase.as_posix() == 'verification' and d.startswith('replay-'))]
        for name in files:
            rel = (relbase / name).as_posix()
            if rel not in mapping:
                result['unmapped_material_files'].append(rel)
            else:
                package_files.add(mapping[rel])
    # Names are stable even when the currently running final audit rewrites them.
    checks['package_layout_complete_and_safe'] = not (result['unmapped_material_files'] or
        result['layout_unsafe_destinations'] or result['layout_duplicate_destinations']) and all(
        x['package_destination'] == ('traces/cml-spec17/' + x['source'][len('traces/'):] if x['source'].startswith('traces/') else 'tasks/cml-spec17/' + x['source'])
        for x in layout['mappings'])
    links = []
    for name in ('build.md', 'trace-index.md', 'sources.fragment.md', 'solution.fragment.md',
                 'human-changes.md', 'missing-fields.md', 'auto-filled-facts.md', 'README.md', 'handoff.md'):
        path = OUT / name
        if not path.is_file():
            continue
        package_path = 'sources.md' if name == 'sources.fragment.md' else 'solution.md' if name == 'solution.fragment.md' else 'tasks/cml-spec17/' + name
        body = re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$', '', text(path))
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            target = target.strip('<>')
            if re.match(r'^[a-z]+://', target) or target.startswith('#'):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(package_path), target.split('#')[0]))
            links.append({'source': name, 'target': target, 'package_target': resolved, 'exists': resolved in package_files})
    result['authored_markdown_links'] = links
    checks['all_authored_markdown_package_links_exist'] = all(x['exists'] for x in links)
    result['sensitive_filename_candidates'] = [name for name in package_files if Path(name).suffix.lower() in {'.p12', '.pfx', '.pem', '.key', '.jks', '.keystore'}]
    checks['no_private_key_files_declared'] = not result['sensitive_filename_candidates']
    patterns = {
        'private_key_header': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'),
        'openai_token_shape': re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
        'aws_access_key_shape': re.compile(rb'\bAKIA[0-9A-Z]{16}\b'),
        'jwt_shape': re.compile(rb'\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b')}
    candidates = []
    scanned = 0
    scan_files = [(ROOT / name, 'project/' + name) for name in indexed if Path(name).suffix.lower() not in EXTENSIONS]
    scan_files += [(OUT / x['native'], x['native']) for x in facts['native_sessions']]
    for path, label in scan_files:
        body = path.read_bytes()
        scanned += 1
        for pattern_name, pattern in patterns.items():
            matches = list(pattern.finditer(body))
            if matches:
                candidates.append({'path': label, 'pattern': pattern_name, 'match_count': len(matches),
                                   'first_byte_offset': matches[0].start()})
    result['sensitive_content_scan'] = {'method': 'Pattern scan only; candidate metadata records no matched credential value',
        'patterns': list(patterns), 'files_scanned': scanned, 'candidates': candidates,
        'limit': 'Zero detections is limited to the declared patterns, not proof that arbitrary secrets cannot exist.'}
    checks['no_configured_sensitive_pattern_candidates'] = not candidates
    result['input_sha256_after'] = {p.relative_to(OUT).as_posix(): sha(p) for p in tracked_inputs}
    checks['content_inputs_unchanged_during_audit'] = result['input_sha256_before'] == result['input_sha256_after']
    result['result'] = 'pass' if all(checks.values()) else 'fail'
    result['failed_checks'] = [key for key, value in checks.items() if not value]
    target = VERIFY / 'content-audit.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': target.relative_to(ROOT).as_posix(), 'result': result['result'],
                      'failed_checks': result['failed_checks'], 'checks': len(checks),
                      'binary_count': len(binaries), 'markdown_links': len(links)}, ensure_ascii=False))
    if result['result'] != 'pass':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
