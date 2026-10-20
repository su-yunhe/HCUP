"""Snapshot only this task's active native sessions; preserve historical registration.

Task-scoped variant of harmony-task-flow/scripts/snapshot_traces.py. The initializer
overview registration is explicitly excluded because it contains other-task work.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

ROOT = Path(__file__).resolve().parent.parent
state_path = ROOT / 'workflow/state.json'
state = json.loads(state_path.read_text('utf-8'))
source = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
selected: dict[tuple[str, str], dict] = {}
excluded = []
for entry in state['sessions']:
    if 'initialization only' in entry.get('purpose', '').lower():
        excluded.append({'session_id': entry.get('session_id'),
                         'reason': 'Initialization overview includes other tasks; outside feature-analysis evidence scope.'})
        continue
    selected[(entry['role'], entry['agent_id'])] = entry

stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8]
destination = ROOT / 'traces/native' / stamp
destination.mkdir(parents=True)
copied, gaps = [], []
for entry in selected.values():
    session_id = entry.get('session_id')
    if not session_id:
        gaps.append('Native session ID unavailable: ' + entry['role'] + '/' + entry['agent_id'])
        continue
    session_id = str(UUID(session_id))
    candidates = list(source.rglob('*-' + session_id + '.jsonl'))
    if not candidates:
        gaps.append('Native session file not found: ' + session_id)
    for path in candidates:
        if path.is_symlink() or not path.resolve().is_relative_to(source.resolve()):
            gaps.append('Skipped native path outside session store: ' + str(path))
            continue
        raw = path.read_bytes()
        meta = json.loads(raw.split(b'\n', 1)[0])
        payload = meta.get('payload', {})
        if meta.get('type') != 'session_meta' or payload.get('id') != session_id:
            gaps.append('Native header identity mismatch: ' + str(path))
            continue
        if Path(payload.get('cwd', '')).resolve() != ROOT:
            gaps.append('Native cwd mismatch: ' + session_id)
            continue
        if entry['role'] != 'orchestrator' and payload.get('agent_path') != entry['agent_id']:
            gaps.append('Native agent path mismatch: ' + session_id)
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        copied.append({'role': entry['role'], 'agent_id': entry['agent_id'],
                       'session_id': session_id, 'source': str(path),
                       'snapshot': target.relative_to(ROOT).as_posix(),
                       'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                       'ends_with_newline': raw.endswith(b'\n')})

result = {'created_at': datetime.now(timezone.utc).isoformat(), 'files': copied,
          'excluded_sessions': excluded, 'gaps': gaps, 'snapshot_only': True,
          'includes_future_events': False,
          'scope': 'Latest registered root and four specialist sessions for cml-spec1 only.'}
manifest = destination / 'manifest.json'
manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf-8')
old_native = set(state.get('native_snapshot_gaps', []))
state['record_gaps'] = [g for g in state.get('record_gaps', []) if g not in old_native
                        and g != 'Native session snapshots have not yet been collected.'] + gaps
state['native_snapshot_gaps'] = gaps
state['last_trace_snapshot'] = manifest.relative_to(ROOT).as_posix()
state['trace_scope_exclusions'] = excluded
state['updated_at'] = result['created_at']
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', 'utf-8')
print(json.dumps({'copied': len(copied), 'gaps': gaps, 'excluded': excluded,
                  'manifest': str(manifest), 'snapshot_only': True}, ensure_ascii=False))
raise SystemExit(2 if gaps else 0)
