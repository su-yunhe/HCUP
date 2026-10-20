"""Snapshot only this implementation run's explicitly registered native sessions."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4


root = Path(__file__).resolve().parent.parent
state_path = root / 'workflow/state.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
current_root_id = '01a1448f-dc21-7c42-a6c5-731bc0a5c14e'
current_agents = {
    '/root/requirements_resume', '/root/design', '/root/implementation',
    '/root/verification',
}
selected = {}
for entry in state['sessions']:
    session_id = entry.get('session_id')
    if session_id and (session_id == current_root_id or entry['agent_id'] in current_agents):
        selected[session_id] = entry

native = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8]
destination = root / 'traces/native' / ('implementation-' + stamp)
destination.mkdir(parents=True)
copied = []
gaps = []
for session_id, entry in selected.items():
    candidates = list(native.rglob('*-' + session_id + '.jsonl'))
    if not candidates:
        gaps.append('Current native session file unavailable: ' + session_id)
    for source in candidates:
        if source.is_symlink() or not source.resolve().is_relative_to(native.resolve()):
            gaps.append('Current native session path outside store: ' + session_id)
            continue
        raw = source.read_bytes()
        header = json.loads(raw.split(b'\n', 1)[0])
        if header.get('type') != 'session_meta' or header.get('payload', {}).get('id') != session_id:
            gaps.append('Current native session header mismatch: ' + session_id)
            continue
        target = destination / source.relative_to(native)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        copied.append({
            'role': entry['role'], 'agent_id': entry['agent_id'],
            'session_id': session_id, 'source': str(source),
            'snapshot': target.relative_to(root).as_posix(), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'ends_with_newline': raw.endswith(b'\n'),
        })

manifest = {
    'created_at': datetime.now(timezone.utc).isoformat(),
    'scope': 'Current implementation chat and its four actual role sessions only.',
    'excluded': 'Initialization overview and unrelated sessions are not read or copied.',
    'snapshot_only': True, 'includes_future_events': False,
    'files': copied, 'gaps': gaps,
}
manifest_path = destination / 'manifest.json'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
state['implementation_trace_snapshot'] = manifest_path.relative_to(root).as_posix()
state['implementation_record_gaps'] = gaps
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'copied': len(copied), 'gaps': gaps, 'manifest': state['implementation_trace_snapshot']}))
