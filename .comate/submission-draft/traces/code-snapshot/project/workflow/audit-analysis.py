"""Capture this task's source fingerprint without reading other tasks or history."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def git(*args: str) -> bytes:
    return subprocess.check_output(['git', *args], cwd=ROOT)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

tracked = [p.decode('utf-8') for p in git('ls-files', '-z').split(b'\0') if p]
baseline = json.loads((ROOT / 'workflow/setup-code-fingerprint.json').read_text('utf-8'))
manifest = {name: sha((ROOT / name).read_bytes()) for name in tracked if (ROOT / name).is_file()}
expected = baseline['tracked_files_sha256']
changed = sorted(name for name in set(manifest) | set(expected) if manifest.get(name) != expected.get(name))
new_build_inputs = [name.decode('utf-8') for name in git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')
                    if name and name.decode('utf-8').split('/')[0] in {'AppScope', 'core', 'entry', 'feature', 'hvigor'}]
result = {
    'captured_at': datetime.now(timezone.utc).isoformat(),
    'head': git('rev-parse', 'HEAD').decode().strip(),
    'base_commit': baseline['base_commit'],
    'tracked_diff': git('diff', '--stat').decode(),
    'staged_diff': git('diff', '--cached', '--stat').decode(),
    'tracked_files_sha256': manifest,
    'changes_since_setup': changed,
    'new_build_input_sha256': {name: sha((ROOT / name).read_bytes()) for name in new_build_inputs},
    'spec_sha256': sha((ROOT / 'spec/requirement.md').read_bytes()),
    'metadata_sha256': sha((ROOT / 'spec/metadata.json').read_bytes()),
}
path = ROOT / 'workflow/analysis-code-fingerprint.json'
path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'path': str(path), 'head': result['head'], 'changed': changed,
                  'tracked_count': len(manifest), 'new_build_inputs': new_build_inputs}, ensure_ascii=False))
