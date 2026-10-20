"""Coordinator-only checkpoints for the authorized 1-do stage."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
state_path = root / 'workflow/state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
action = sys.argv[1]

if action == 'start':
    state['current_scope'] = {
        'request': '1-do', 'business_code_frozen': False,
        'full_feature_implementation_requested': True,
        'source': 'spec-harness/1-do.md',
        'dedicated_session': os.environ.get('CODEX_THREAD_ID'),
        'deliverables': ['production implementation', 'hypium_tests', 'verification evidence']
    }
    snapshot = root / 'system-config' / ('implementation-' + stamp)
    flow = Path('D:/HarmonyDev/codex/skills/harmony-task-flow')
    shutil.copytree(flow, snapshot / 'skills/harmony-task-flow',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (snapshot / 'agents').mkdir()
    for role in ('requirements', 'design', 'implementation', 'verification'):
        name = 'harmony_' + role + '.toml'
        shutil.copy2(flow.parent.parent / 'agents' / name, snapshot / 'agents' / name)
    state['implementation_config_snapshot'] = snapshot.relative_to(root).as_posix()
elif action == 'approve':
    paths = sys.argv[3:]
    state['approved_artifacts'][sys.argv[2]] = [
        {'path': p, 'sha256': hashlib.sha256((root / p).read_bytes()).hexdigest(),
         'bytes': (root / p).stat().st_size} for p in paths]
elif action == 'fingerprint':
    paths = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0'))
    paths.discard('')
    for folder in ('AppScope', 'entry', 'core', 'feature', 'hvigor', 'hypium_tests'):
        for directory, subdirs, files in os.walk(root / folder):
            subdirs[:] = [x for x in subdirs if x not in {'build', 'oh_modules', '.hvigor', '.preview', '__pycache__'}]
            for filename in files:
                paths.add((Path(directory) / filename).relative_to(root).as_posix())
    for path in (root / 'workflow/verification').iterdir():
        if path.is_file() and path.suffix in {'.py', '.ps1', '.json'}:
            paths.add(path.relative_to(root).as_posix())
    inputs = [{'path': p, 'sha256': hashlib.sha256((root / p).read_bytes()).hexdigest() if (root / p).is_file() else None}
              for p in sorted(paths)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root).decode().strip()
    payload = {'timestamp_utc': stamp, 'head': head, 'inputs': inputs,
               'git_status': subprocess.check_output(['git', 'status', '--short'], cwd=root).decode()}
    path = root / 'workflow' / (sys.argv[2] + '-fingerprint.json')
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    state['code_fingerprint'] = {'head': head, 'base_commit': state['base_commit'],
        'manifest': path.relative_to(root).as_posix(), 'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
elif action == 'failure':
    item = json.loads((root / sys.argv[2]).read_text(encoding='utf-8-sig'))
    state['failures'].append(item)
elif action == 'resolve':
    for item in state['failures']:
        if item['fingerprint'] == sys.argv[2]:
            item['status'] = 'resolved'
            item['resolution_evidence'] = sys.argv[3:]
else:
    raise ValueError(action)
state['updated_at'] = datetime.now(timezone.utc).isoformat()
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(action + ': checkpoint saved')
