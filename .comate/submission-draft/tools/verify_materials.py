"""Verify material correspondence; does not build, install, run tests or edit source."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    issues = []
    required = ['changes/final.diff', 'build.md', 'trace-index.md', 'sources.fragment.md', 'solution.fragment.md',
                'submission.json.fragment', 'traces/manifest.json', 'traces/session-map.md', 'traces/token-usage.md',
                'logs/build.log', 'logs/install.log', 'logs/selftest.log', 'logs/selftest.json',
                'changes/project-manifest.json', 'changes/binary-files.json', 'delivery-notes.md', 'pending-fields.md', 'facts-and-sources.md']
    for item in required:
        if not (OUT / item).is_file():
            issues.append('Required file missing: ' + item)
    template = Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
    labels = [line[2:].strip().rstrip('：:') for line in template.splitlines() if line.startswith('- ')]
    actual = (OUT / 'trace-index.md').read_text(encoding='utf-8')
    for label in labels:
        if '- ' + label + '：' not in actual:
            issues.append('Official trace field missing: ' + label)
    build = (OUT / 'build.md').read_text(encoding='utf-8')
    if re.search(r'\b[A-Za-z]:[/\\]', build):
        issues.append('build.md contains private absolute Windows path')
    fragment = load(OUT / 'submission.json.fragment')
    official = load(Path('D:/SWE-OpenHarmony/templates/submission.json'))
    expected = next(t for t in official['tasks'] if t['task_id'] == 'vg-spec9')
    if set(fragment) != set(expected):
        issues.append('Submission fragment fields differ from official task schema')
    for key in ('project_path', 'build_instructions', 'trace_index'):
        value = fragment[key]
        if '\\' in value or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts:
            issues.append('Invalid package path: ' + key)
    if not fragment['build_instructions'].endswith('/build.md') or not fragment['trace_index'].endswith('/trace-index.md'):
        issues.append('Instruction and trace paths must refer to files')
    m = load(OUT / 'changes/project-manifest.json')
    canonical = ''.join(item['path'] + '\0' + item['sha256'] + '\n'
                        for item in sorted(m['files'], key=lambda item: item['path'])).encode('utf-8')
    recomputed_snapshot_id = hashlib.sha256(canonical).hexdigest()
    if recomputed_snapshot_id != m['snapshot_id']:
        issues.append('Snapshot identifier does not match declared path-string sorting algorithm')
    snapshot = OUT / m['snapshot_path']
    source_mismatches = []
    for item in m['files']:
        for label, path in [('snapshot', snapshot / item['path']), ('worktree', ROOT / item['path'])]:
            if not path.is_file() or path.stat().st_size != item['bytes'] or sha(path) != item['sha256']:
                source_mismatches.append(label + ':' + item['path'])
    issues.extend(source_mismatches)
    patch = load(OUT / 'checks/diff-validation.json')
    if sha(OUT / 'changes/final.diff') != patch['patch_sha256'] or not patch['all_files_reconstructed_byte_identically']:
        issues.append('Patch proof/hash mismatch')
    changes = load(OUT / 'changes/changed-files.json')
    for entry in changes:
        parts = PurePosixPath(entry['path']).parts
        if '.git' in parts or '__pycache__' in parts or 'build' in parts or entry['path'].endswith('.pyc') or entry['path'].startswith('.comate/submission-draft/'):
            issues.append('Noise or recursive output in final.diff: ' + entry['path'])
    logs = load(OUT / 'checks/copied-log-manifest.json')
    for item in logs:
        if sha(OUT / item['path']) != item['sha256'] or sha(ROOT / item['path']) != item['sha256']:
            issues.append('Copied log differs: ' + item['path'])
    trace = load(OUT / 'traces/manifest.json')
    sessions = {s['session_id']: s for s in trace['sessions']}
    if trace['registered_missing']:
        issues.append('Missing registered native sessions: ' + repr(trace['registered_missing']))
    native_records = 0
    for s in sessions.values():
        path = OUT / s['native_path']
        if not path.is_file() or sha(path) != s['sha256']:
            issues.append('Native export/hash mismatch: ' + s['session_id'])
            continue
        records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        native_records += len(records)
        if records[0]['payload']['id'] != s['session_id']:
            issues.append('Native header ID mismatch: ' + s['session_id'])
        if not (OUT / s['markdown_path']).is_file():
            issues.append('Native Markdown copy missing: ' + s['session_id'])
    index = [json.loads(line) for line in (OUT / 'traces/filtered-session-index.jsonl').read_text(encoding='utf-8').splitlines() if line]
    for row in index:
        if row['id'] not in sessions:
            issues.append('Unrelated sidebar row in filtered index')
    for s in sessions.values():
        if s['ide_sidebar_session_id'] not in {row['id'] for row in index}:
            issues.append('Sidebar mapping lacks matched row: ' + s['session_id'])
    binary = load(OUT / 'changes/binary-files.json')
    for item in binary['files']:
        if sha(snapshot / item['path']) != item['sha256']:
            issues.append('Binary content missing: ' + item['path'])
    # Local links in newly authored materials, not historical docs or mechanical native copies.
    link_files = ['README.md', 'trace-index.md', 'build.md', 'solution.fragment.md', 'sources.fragment.md',
                  'delivery-notes.md', 'human-changes.md', 'pending-fields.md', 'facts-and-sources.md', 'taskbook-version.md']
    for name in link_files:
        text = (OUT / name).read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if re.match(r'^[a-z]+:', target) or target.startswith('#'):
                continue
            target = target.split('#', 1)[0].strip('<>')
            if not ((OUT / name).parent / target).exists():
                issues.append('Broken local material link: ' + name + ' -> ' + target)
    # All input fields that were empty must remain explicit, including human/source assertions.
    if '【待补充】' not in (OUT / 'human-changes.md').read_text(encoding='utf-8'):
        issues.append('Missing human-edits unknown declaration')
    keys = ['human_edits', 'known_issues', 'extra_sources', 'md_export_dir']
    inputs = load(OUT / 'checks/verified-input-fields.json')
    if any(inputs['task'].get(key) != '【待补充】' for key in keys):
        issues.append('Blank task input was inferred')
    git_status = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no'], cwd=ROOT).decode('utf-8').splitlines()
    result = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'Material integrity only; no build or runtime test rerun.',
        'status': 'pass' if not issues else 'fail', 'issues': issues, 'official_trace_fields': len(labels),
        'project_files': len(m['files']), 'source_mismatches': source_mismatches,
        'copied_logs': len(logs), 'native_sessions': len(sessions), 'native_records': native_records,
        'filtered_sidebar_rows': len(index), 'binary_files': len(binary['files']),
        'patch_apply_check_exit_code': patch['apply_check_exit_code'], 'patch_actual_apply_exit_code': patch['apply_exit_code'],
        'all_snapshot_files_reconstructed_byte_identically': patch['all_files_reconstructed_byte_identically'],
        'snapshot_id': m['snapshot_id'], 'tracked_status': git_status,
        'recomputed_snapshot_id': recomputed_snapshot_id,
        'limits': ['User-provided pending fields remain open; passing technical material integrity is not official submission approval.',
                   'No team-wide package or ZIP created. Native material-session capture is a point-in-time snapshot.'],
    }
    (OUT / 'checks/material-integrity.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    # A precise stage-3 copy map keeps temporary Git clones and superseded scratch
    # snapshots out of the package. The map cannot recursively hash itself.
    mapping = []
    excluded_counts = {'temporary_clone_files': 0, 'superseded_snapshot_files': 0}
    current_snapshot_prefix = m['snapshot_path'].removesuffix('/project') + '/'
    for path in sorted(OUT.rglob('*'), key=lambda path: path.relative_to(OUT).as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(OUT).as_posix()
        if relative.startswith('checks/work/'):
            excluded_counts['temporary_clone_files'] += 1
            continue
        if relative.startswith('traces/code-snapshots/') and not relative.startswith(current_snapshot_prefix):
            excluded_counts['superseded_snapshot_files'] += 1
            continue
        if relative == 'delivery-manifest.json':
            continue
        mapping.append({'source': relative, 'destination': 'tasks/vg-spec9/' + relative,
                        'bytes': path.stat().st_size, 'sha256': sha(path)})
    delivery = {'created_at_utc': result['checked_at_utc'], 'task_id': 'vg-spec9', 'snapshot_id': m['snapshot_id'],
                'project_copy': {'source': m['snapshot_path'], 'destination': fragment['project_path'], 'manifest': 'changes/project-manifest.json'},
                'material_files': mapping, 'excluded_local_scratch_counts': excluded_counts,
                'notes': ['Copy delivery-manifest.json itself as an index, without inventing a recursive self-hash.',
                          'The listed final code snapshot is preserved as trace evidence and also supplies the complete project/.',
                          'Only the submitted task object is a fragment; team/root files and ZIP remain stage 3 work.']}
    (OUT / 'delivery-manifest.json').write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=True))
    if issues:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
