import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('D:/HCUP/vg-spec8')
DRAFT = ROOT / '.comate/submission-draft'
PROJECT = DRAFT / 'project'
OUT = DRAFT / 'validation/independent-rebuild'
CLONE = OUT / 'round02/baseline'
BASE = '9cbcf7292c8cc46955dc3b522ddbda41c66a61d9'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'
THREAD = '01a14549-2c5d-70c0-ab26-64feca32bde8'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()

def read_json(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def text(p):
    return p.read_text(encoding='utf-8-sig')

def allfiles(p):
    return {x.relative_to(p).as_posix(): x for x in p.rglob('*') if x.is_file()}

def status(passed, **facts):
    return {'status': 'pass' if passed else 'fail', **facts}

result = {'thread_id': THREAD, 'started_at': datetime.now(timezone.utc).isoformat(),
          'scope': 'submission material checks; no build, device, network, unrelated session, or production mutation'}
check = {}
manifest = read_json(DRAFT / 'changes/project-manifest.json')
manifest_before = digest(DRAFT / 'changes/project-manifest.json')
expected = {x['path']: x for x in manifest['files']}
freeze = read_json(ROOT / 'workflow/production-freeze-01.json')
production_before = {x['path']: digest(ROOT / x['path']) for x in freeze}

# Official field names, same order, populated, with honest pending markers allowed.
template = text(Path('D:/SWE-OpenHarmony/templates/trace-index.md'))
trace = text(DRAFT / 'trace-index.md')
field_pattern = re.compile(r'^- (.*?)\uff1a(.*)$', re.M)
official_fields = field_pattern.findall(template)
actual_fields = field_pattern.findall(trace)
check['trace_index_24_fields'] = status(len(official_fields) == 24 and
    [x[0] for x in official_fields] == [x[0] for x in actual_fields] and
    all(x[1].strip() for x in actual_fields),
    official_count=len(official_fields), actual_count=len(actual_fields),
    fields=[{'field': a, 'populated': bool(b.strip()), 'contains_pending': '\u3010\u5f85\u8865\u5145' in b}
            for a, b in actual_fields])

# The single-task fragment maps into a future package, without fabricating team-wide entries.
fragment = read_json(DRAFT / 'submission.json.fragment')
path_checks = []
for key in ['project_path', 'build_instructions', 'trace_index']:
    value = fragment[key]
    pure = PurePosixPath(value)
    relative = (not pure.is_absolute() and '\\' not in value and ':' not in value
                and '..' not in pure.parts and value.startswith('tasks/vg-spec8/'))
    local = DRAFT / value.removeprefix('tasks/vg-spec8/')
    exists_as_kind = local.is_dir() if key == 'project_path' else local.is_file()
    path_checks.append({'field': key, 'path': value, 'package_relative': relative,
                        'exists_as_required_kind': exists_as_kind})
check['submission_paths'] = status(fragment['task_id'] == 'vg-spec8' and
    fragment['status'] == 'submitted' and all(x['package_relative'] and x['exists_as_required_kind'] for x in path_checks),
    checks=path_checks)

build = text(DRAFT / 'build.md')
private_paths = re.findall(r'(?:[A-Za-z]:[/\\][^\s`]*|/(?:Users|home|Applications)/[^\s`]*)', build)
required_build_tokens = ['ohpm install', 'assembleHap', 'install -r', 'aa start', 'io.qzz.weiyu',
                         'EntryAbility', 'entry-default-unsigned.hap', '\u521d\u59cb\u5316',
                         'verification_support.py', '\u3010\u5f85\u8865\u5145\u3011']
check['portable_build_document'] = status(not private_paths and all(x in build for x in required_build_tokens),
    private_absolute_path_matches=private_paths,
    required_tokens={x: x in build for x in required_build_tokens},
    test_script_portability_limit_disclosed='ROOT' in build and '\u81ea\u52a8\u811a\u672c\u79fb\u690d\u9650\u5236' in build)

# User blanks remain pending; observable facts do not become human declarations.
team = text(Path('D:/HCUP/common/spec-harness/team.yaml'))
task = text(ROOT / 'spec/submit-input.yaml')
pending = text(DRAFT / 'pending-fields.md')
blanks = ['team.version', 'team.contact', 'team.freeze_time', 'team.members[].name / work',
          'team.source_guard', 'task.human_edits', 'task.known_issues', 'task.extra_sources', 'task.md_export_dir']
check['pending_inputs'] = status(all(x in pending for x in blanks) and
    '\u3010\u5f85\u8865\u5145\u3011' in pending and all(f'{x}: ""' in task for x in
    ['human_edits', 'known_issues', 'extra_sources', 'md_export_dir']) and
    all(f'{x}: ""' in team for x in ['version', 'contact', 'freeze_time', 'source_guard']),
    pending_input_fields=blanks, team_only_package_fields_also_disclosed='team.submitted_tasks' in pending)
check['codex_comate_disclosure'] = status(all(x in trace for x in
    ['Comate', 'sessionUuid', 'session_meta.session_id', '\u4fa7\u8fb9\u680f', '\u672c\u6b21\u672a\u4f7f\u7528Comate',
     '\u6d3b\u8dc3\u6750\u6599\u4f1a\u8bdd\u622a\u70b9\u540e', '\u672a\u767b\u8bb0\u4f1a\u8bdd']),
    note='Codex thread and inherited native session ID are disclosed; Comate dual IDs are pending/not applicable, not fabricated')

sources = text(DRAFT / 'sources.fragment.md')
check['source_scope_disclosure'] = status(
    '\u6ca1\u6709\u4ece\u6765\u6e90\u5e94\u7528\u4e0a\u6e38\u5f53\u524d\u5b9e\u73b0\u6216\u76f8\u5173\u4fee\u590d\u5386\u53f2\u83b7\u53d6\u672c\u529f\u80fd\u4ee3\u7801' not in sources and
    '\u5df2\u6838\u9a8c' in sources and 'AI' in sources and 'extra_sources' in sources and
    '\u3010\u5f85\u8865\u5145\u3011' in sources and '\u4eba\u5de5' in sources,
    note='Source statement must stay within observed AI records and retain the unknown human/extra source declaration')

# All native exports parse, match their independent index hash/header, and belong to known task threads.
index = read_json(DRAFT / 'traces/session-index.json')
state = read_json(PROJECT / 'workflow/state.json')
expected_ids = {x['session_id'] for x in state['sessions'] if x.get('session_id') and x['session_id'] != OVERVIEW}
actual_ids = {x['thread_id'] for x in index}
native_findings = []
native_failures = []
for row in index:
    p = DRAFT / row['native_file']
    count = 0
    kinds = {}
    first = None
    with p.open(encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            item = json.loads(line)
            if first is None: first = item
            count += 1
            key = item.get('type', '')
            kinds[key] = kinds.get(key, 0) + 1
    meta = first['payload']
    valid = (count == row['records'] and digest(p) == row['export_sha256'] and
             meta['id'] == row['thread_id'] and meta['session_id'] == row['native_session_id'] and
             meta['cwd'].replace('\\', '/').lower() == str(ROOT).replace('\\', '/').lower() and
             bool(row['source_path_match_lines']) and bool(row['task_id_match_lines']) and
             (DRAFT / row['markdown_file']).is_file())
    native_findings.append({'thread_id': row['thread_id'], 'native_session_id': meta['session_id'],
                            'records': count, 'types': kinds, 'valid': valid,
                            'active_prefix_snapshot': row['active_prefix_snapshot']})
    if not valid: native_failures.append(row['thread_id'])
native_paths = sorted(p.name for p in (DRAFT / 'traces/native').glob('*'))
snapshot_native_paths = [p for p in expected if p.startswith('traces/native/') and p.endswith('.jsonl')]
unknown_snapshot_names = [p for p in snapshot_native_paths if not any(t in p for t in actual_ids)]
filtered = [json.loads(s) for s in text(DRAFT / 'traces/session-index.filtered.jsonl').splitlines() if s.strip()]
check['native_traces'] = status(not native_failures and actual_ids == expected_ids and
    len(native_paths) == len(index) and not unknown_snapshot_names,
    expected_threads=len(expected_ids), indexed_threads=len(index), native_files=len(native_paths),
    missing_ids=sorted(expected_ids - actual_ids), extra_ids=sorted(actual_ids - expected_ids),
    unknown_old_native_filenames=unknown_snapshot_names,
    mixed_overview_raw_absent=not any(OVERVIEW in p for p in expected if p.endswith('.jsonl')),
    filtered_index_rows=len(filtered), sessions=native_findings,
    external_source_sessions_scanned=False)

# Logs were copied, including original failed attempts, without silently substituting only final reports.
excluded = read_json(DRAFT / 'changes/exclusions.json')
excluded_log_paths = {x['path'].removeprefix('logs/') for x in excluded['excluded'] if x['path'].startswith('logs/')}
original_logs = {k: p for k, p in allfiles(ROOT / 'logs').items() if k not in excluded_log_paths}
draft_logs = allfiles(DRAFT / 'logs')
project_logs = allfiles(PROJECT / 'logs')
copy_manifest = read_json(DRAFT / 'logs/copy-manifest.json')
copy_rows = {x['path'].removeprefix('logs/'): x for x in copy_manifest['files']}
copy_manifest_failures = []
for name, row in copy_rows.items():
    if (name not in original_logs or name not in draft_logs or
        row['source_sha256'] != digest(original_logs[name]) or
        row['export_sha256'] != digest(draft_logs[name]) or
        row['bytes'] != draft_logs[name].stat().st_size):
        copy_manifest_failures.append(name)
log_different = [k for k in sorted(set(draft_logs) & set(original_logs)) if
                 digest(draft_logs[k]) != digest(original_logs[k]) or
                 k not in project_logs or digest(draft_logs[k]) != digest(project_logs[k])]
failure_examples = [
    'analysis-baseline/mock-requests.jsonl',
    'implementation-validation/round-01/install-attempt01-raw-exit.json',
    'implementation-validation/round-01/install-attempt01-path-failure.log',
    'implementation-validation/round-01/harness-attempt01.log',
    'implementation-validation/round-01/harness-report-attempt01.json',
    'implementation-validation/round-01/attempt02/harness-report.json',
    'implementation-validation/round-01/attempt04-full/harness-report.json',
    'implementation-validation/round-01/attempt05-sentinel/harness-report.json']
check['logs_and_failures'] = status(set(original_logs) == set(copy_rows) and
    set(original_logs) | {'copy-manifest.json'} == set(draft_logs) and
    set(original_logs) == set(project_logs) and
    digest(DRAFT / 'logs/copy-manifest.json') == digest(PROJECT / '.comate/submission-draft/logs/copy-manifest.json') and
    not log_different and not copy_manifest_failures and all(x in draft_logs for x in failure_examples),
    original_task_log_files=len(original_logs), copied_log_files=len(draft_logs),
    original_location_project_log_files=len(project_logs),
    missing=sorted(set(original_logs)-set(draft_logs)), extra=sorted(set(draft_logs)-set(original_logs)),
    different=log_different, generated_copy_manifest='copy-manifest.json',
    copy_manifest_entries=len(copy_rows), copy_manifest_failures=copy_manifest_failures,
    failed_and_retry_examples_present={x: x in draft_logs for x in failure_examples},
    excluded_unrelated_preinstall_ui=sorted(excluded_log_paths))

discovery = read_json(DRAFT / 'validation/session-discovery.json')
path_ids = {x['id'] for x in discovery['path_query_matches']}
task_query_ids = {x['id'] for x in discovery['task_id_query_matches_current_project']}
check['recorded_session_discovery'] = status(path_ids == actual_ids and task_query_ids <= actual_ids and
    not discovery['unexported_dedicated_project_ids'] and not discovery['nonproject_metadata_matches_not_opened'],
    cwd_query_ids=len(path_ids), task_query_ids=len(task_query_ids),
    unexported_dedicated_ids=discovery['unexported_dedicated_project_ids'],
    evidence='validation/session-discovery.json',
    evidence_strength='Reviewed parent-recorded read-only metadata query; verifier did not open client database or other session originals')

# Binary bytes and baseline origin claims are checked against only the specified baseline tree.
env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
cp = subprocess.run(['git', 'ls-tree', '-r', '-z', BASE], cwd=CLONE, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(OUT / 'material-baseline-tree.raw').write_bytes(cp.stdout)
(OUT / 'material-baseline-tree-stderr.log').write_bytes(cp.stderr)
base_blobs = {}
for item in cp.stdout.split(b'\0'):
    if not item: continue
    metadata, name = item.split(b'\t', 1)
    base_blobs[name.decode('utf-8')] = metadata.split()[2].decode('ascii')
binary = read_json(DRAFT / 'changes/binary-manifest.json')
binary_failures = []
origin_failures = []
baseline_binary_count = 0
for row in binary:
    p = PROJECT / row['path']
    if not p.is_file() or p.stat().st_size != row['bytes'] or digest(p) != row['sha256']:
        binary_failures.append(row['path'])
    same = False
    if row['path'] in base_blobs:
        blob = subprocess.run(['git', 'cat-file', 'blob', base_blobs[row['path']]], cwd=CLONE,
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if blob.returncode: origin_failures.append(row['path'] + ':cat-file-failed')
        same = hashlib.sha256(blob.stdout).hexdigest() == row['sha256']
    if same: baseline_binary_count += 1
    if same != row['same_as_baseline_resource']: origin_failures.append(row['path'])
binary_paths = {x['path'] for x in binary}
null_sample_paths = set()
for name in expected:
    with (PROJECT / name).open('rb') as f:
        if b'\0' in f.read(8192): null_sample_paths.add(name)
check['binary_manifest'] = status(cp.returncode == 0 and not binary_failures and not origin_failures and
    null_sample_paths <= binary_paths and len(binary_paths) == len(binary),
    files=len(binary), baseline_same_bytes=baseline_binary_count, failed_bytes_or_hash=binary_failures,
    failed_baseline_origin=origin_failures, unlisted_nul_sample_files=sorted(null_sample_paths-binary_paths),
    duplicate_paths=len(binary)-len(binary_paths), baseline_tree_exit_code=cp.returncode)

# Recorded taskbook versions and copied official templates are reproducible from permitted read-only inputs.
taskbooks = read_json(DRAFT / 'provenance/taskbook-version.json')
taskbook_failures = []
for row in taskbooks['files']:
    name = Path(row['common_path']).name
    common = Path('D:/HCUP/common/spec-harness') / name
    local = ROOT / 'spec-harness' / name
    if digest(common) != row['sha256'] or digest(local) != row['task_copy_sha256']:
        taskbook_failures.append(name)
check['taskbook_version'] = status(not taskbook_failures and
    bool((ROOT / 'spec/history').exists()) == taskbooks['spec_history_exists'],
    files=len(taskbooks['files']), failures=taskbook_failures,
    common_own_git_checkout_declared=taskbooks['common_is_own_git_checkout'],
    task_history_exists=taskbooks['spec_history_exists'])

production_failures = []
for row in freeze:
    name, expected_sha = row['path'], row['sha256']
    if production_before[name] != expected_sha or digest(ROOT / name) != expected_sha or digest(PROJECT / name) != expected_sha:
        production_failures.append(name)
parent_before = read_json(DRAFT / 'validation/production-before.json')
check['production_258_unchanged'] = status(len(freeze) == 258 and not production_failures and parent_before == freeze,
    files=len(freeze), different=production_failures,
    freeze_manifest_sha256=digest(ROOT / 'workflow/production-freeze-01.json'),
    parent_before_matches_implementation_freeze=parent_before == freeze)

boundary = excluded['output_boundary']
forbidden_nested = [x for x in expected if any(x == b or x.startswith(b + '/') for b in boundary)]
check['artifact_boundaries'] = status(not forbidden_nested and '.git' not in expected and
    not (PROJECT / '.git').exists() and (ROOT / '.git').is_file() and
    any(x['path'] == '.git' for x in excluded['excluded']),
    recursive_output_boundaries=boundary, nested_derived_files=forbidden_nested,
    repository_metadata_absent_from_snapshot=not (PROJECT / '.git').exists(),
    original_worktree_pointer_preserved=(ROOT / '.git').is_file(),
    original_pointer_sha256=digest(ROOT / '.git'),
    overview_jsonl_absent=not any(OVERVIEW in p for p in expected if p.endswith('.jsonl')))

hap = DRAFT / 'artifacts/entry-default-unsigned.hap'
hap_record = read_json(DRAFT / 'changes/build-artifact.json')
check['hap_artifact'] = status(hap.is_file() and digest(hap) ==
    'c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229',
    path='artifacts/entry-default-unsigned.hap', bytes=hap.stat().st_size,
    sha256=digest(hap), manifest=hap_record)

recovery = read_json(DRAFT / 'validation/metadata-boundary-fix.json')
check['freeze_time_disclosure'] = status('\u3010\u5f85\u8865\u5145\u3011' in manifest['official_team_freeze_time']
    and recovery['snapshot_identifier_created_at'] != recovery['project_enumeration_manifest_written_at_before_correction']
    and '\u3010\u5f85\u8865\u5145\u3011' in trace and 'team.freeze_time' in trace,
    official_team_freeze_time=manifest['official_team_freeze_time'],
    technical_identifier_created_at=recovery['snapshot_identifier_created_at'],
    later_manifest_written_at=recovery['project_enumeration_manifest_written_at_before_correction'],
    note='Technical identifier/export start time is not material freeze completion or the official team freeze time')
result['checks'] = check
result['manifest_sha256_before'] = manifest_before
result['manifest_sha256_after'] = digest(DRAFT / 'changes/project-manifest.json')
result['frozen_manifest_unchanged_during_checks'] = result['manifest_sha256_before'] == result['manifest_sha256_after']
result['passed'] = all(x['status'] == 'pass' for x in check.values()) and result['frozen_manifest_unchanged_during_checks']
result['ended_at'] = datetime.now(timezone.utc).isoformat()
(OUT / 'material-check-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'passed': result['passed'], 'checks': {k:v['status'] for k,v in check.items()}}, ensure_ascii=True))
sys.exit(0 if result['passed'] else 1)
