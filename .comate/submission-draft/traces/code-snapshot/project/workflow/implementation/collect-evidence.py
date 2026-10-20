from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess

root = Path('D:/HCUP/vg-spec13')
out = root / 'workflow/implementation'
logroot = root / 'logs/implementation-build'
production_paths = [
    'entry/src/main/ets/pages/SettingsPage.ets',
    'entry/src/main/ets/pages/settings/SettingsSyncSection.ets',
    'entry/src/main/ets/pages/settings/SettingsWebDavBuilders.ets',
    'entry/src/main/ets/pages/settings/SettingsNavigationBuilders.ets',
    'entry/src/main/ets/sync/ManualWebDavBackupController.ets',
    'entry/src/main/ets/sync/WebDavSyncManager.ets',
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def read_text(path):
    raw = path.read_bytes()
    encoding = 'utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
    return raw.decode(encoding)

def warnings(path):
    lines = read_text(path).splitlines()
    result = []
    for index, line in enumerate(lines):
        match = re.search(r'ArkTS:WARN File: (.*?):(\d+):(\d+)', line)
        if match:
            message_index = index + 1
            while message_index < len(lines) and not lines[message_index].strip():
                message_index += 1
            result.append({
                'file': match[1].replace('D:/HCUP/vg-spec13/', ''),
                'line': int(match[2]), 'column': int(match[3]),
                'message': lines[message_index].strip(), 'raw_log_line': index + 1,
            })
    return result

build_results = sorted(logroot.glob('*-result.json'))
latest_path = build_results[-1]
latest = json.loads(read_text(latest_path))
assert latest['build_exit_code'] == 0
baseline_log = root / 'logs/baseline-20261016/build-raw.log'
current_log = Path(latest['build_log'])
baseline_warnings = warnings(baseline_log)
current_warnings = warnings(current_log)
key = lambda item: (item['file'], item['message'])
baseline_counts = Counter(map(key, baseline_warnings))
current_counts = Counter(map(key, current_warnings))
added = current_counts - baseline_counts
removed = baseline_counts - current_counts
warning_delta = {
    'comparison': 'file + message multiset; line numbers ignored because code moved',
    'baseline_log': str(baseline_log), 'build_log': str(current_log),
    'baseline_count': len(baseline_warnings), 'current_count': len(current_warnings),
    'added': [{'file': path, 'message': message, 'count': count} for (path, message), count in added.items()],
    'removed': [{'file': path, 'message': message, 'count': count} for (path, message), count in removed.items()],
    'new_file_diagnostics': [item for item in current_warnings if item['file'] in production_paths[2:5]],
}
save(logroot / 'warnings-full.json', current_warnings)
save(logroot / 'warnings-comparison.json', warning_delta)

baseline = json.loads((root / 'workflow/implementation-start-code-fingerprint.json').read_text(encoding='utf-8-sig'))
fingerprint_paths = sorted(set(baseline['tracked_files_sha256']) | set(production_paths))
fingerprints = {path: sha(root / path) for path in fingerprint_paths}
aggregate = hashlib.sha256(json.dumps(fingerprints, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
changed = [path for path, digest in baseline['tracked_files_sha256'].items() if fingerprints[path] != digest]
source_fingerprint = {
    'created_at': datetime.now(timezone.utc).isoformat(),
    'CODEX_THREAD_ID': '01a143bf-40f7-7d62-b34c-af46d1698de6',
    'base_commit': baseline['head'],
    'aggregate_sha256': aggregate,
    'tracked_plus_authorized_new_files_sha256': fingerprints,
    'changed_tracked_files_since_implementation_start': changed,
    'authorized_production_files_sha256': {path: fingerprints[path] for path in production_paths},
}
save(out / 'source-fingerprint-v1.json', source_fingerprint)
hap = root / 'entry/build/default/outputs/default/entry-default-unsigned.hap'
design_sha = sha(root / 'workflow/design/implementation-plan-v1.md')
assert design_sha == '52c1ecbd06bfc1f55453c961ace20ec7e6a9d8cdce34632be6cb62faaf47162a'
texts = {path: (root / path).read_text(encoding='utf-8') for path in production_paths}
diff_check = subprocess.run(['git', 'diff', '--check'], cwd=root, text=True, capture_output=True)
report = {
    'design_sha256': design_sha,
    'build_result': str(latest_path), 'build_exit_code': latest['build_exit_code'],
    'hap': str(hap), 'hap_bytes': hap.stat().st_size, 'hap_sha256': sha(hap),
    'line_counts': {path: len(text.splitlines()) for path, text in texts.items()},
    'new_any_unknown_tokens': {path: re.findall(r'\b(?:any|unknown)\b', text) for path, text in texts.items()},
    'diff_check_exit_code': diff_check.returncode, 'diff_check_output': diff_check.stdout + diff_check.stderr,
    'warning_comparison': warning_delta,
    'source_aggregate_sha256': aggregate,
    'changed_tracked_files_since_implementation_start': changed,
    'device_commands_performed': False,
}
save(out / 'implementation-checks-v1.json', report)
print(json.dumps({
    'build_exit_code': report['build_exit_code'], 'hap_sha256': report['hap_sha256'],
    'warning_counts': [len(baseline_warnings), len(current_warnings)], 'new_warning_groups': len(added),
    'source_aggregate_sha256': aggregate, 'line_counts': report['line_counts'],
    'changed_tracked': changed,
}, ensure_ascii=False, indent=2))
