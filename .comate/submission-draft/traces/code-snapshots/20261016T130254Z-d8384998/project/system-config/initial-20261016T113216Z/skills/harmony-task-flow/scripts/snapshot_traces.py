"""Copy only explicitly registered native JSONL session files; never synthesize traces."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from workflow import load_state, write_json


def snapshot(root, source):
    state = load_state(root)
    ids, gaps = set(), []
    for entry in state['sessions']:
        if not entry.get('session_id'):
            gaps.append('Native session ID unavailable: ' + entry['role'] + '/' + entry['agent_id'])
        else:
            ids.add(str(UUID(entry['session_id'])))
    if not ids:
        gaps.append('No native UUID sessions registered.')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid4().hex[:8]
    destination = root / 'traces/native' / stamp
    destination.mkdir(parents=True)
    copied = []
    for session_id in sorted(ids):
        # Native rollout names end in the UUID. Only explicit IDs are matched.
        candidates = list(source.rglob('*-' + session_id + '.jsonl')) if source.exists() else []
        if not candidates:
            gaps.append('Native session file not found: ' + session_id)
        for path in candidates:
            if path.is_symlink() or not path.resolve().is_relative_to(source):
                gaps.append('Skipped path outside native session store: ' + str(path))
                continue
            raw = path.read_bytes()
            first = raw.split(b'\n', 1)[0]
            try:
                meta = json.loads(first)
                if meta.get('type') != 'session_meta' or meta.get('payload', {}).get('id') != session_id:
                    raise ValueError('session metadata mismatch')
            except (ValueError, UnicodeError):
                gaps.append('Unrecognized native session header: ' + str(path))
                continue
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            copied.append({'session_id': session_id, 'source': str(path),
                           'snapshot': target.relative_to(root).as_posix(), 'bytes': len(raw),
                           'sha256': hashlib.sha256(raw).hexdigest(),
                           'ends_with_newline': raw.endswith(b'\n')})
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'files': copied, 'gaps': gaps,
              'snapshot_only': True, 'includes_future_events': False}
    write_json(destination / 'manifest.json', result)
    # Preserve unrelated recording gaps; replace only gaps produced by this helper.
    old_native = set(state.get('native_snapshot_gaps', []))
    state['record_gaps'] = [gap for gap in state.get('record_gaps', [])
                            if gap not in old_native and gap != 'Native session snapshots have not yet been collected.'] + gaps
    state['native_snapshot_gaps'] = gaps
    state['last_trace_snapshot'] = str((destination / 'manifest.json').relative_to(root))
    state['updated_at'] = result['created_at']
    write_json(root / 'workflow/state.json', state)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--sessions-root', default=str(Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'))
    args = parser.parse_args()
    root, source = Path(args.root).resolve(), Path(args.sessions_root).resolve()
    if source == root or source.is_relative_to(root) or root.is_relative_to(source):
        parser.error('Task directory and native session store must be disjoint.')
    try:
        result = snapshot(root, source)
        print(json.dumps({'copied': len(result['files']), 'gaps': result['gaps'], 'snapshot_only': True}, ensure_ascii=False))
        raise SystemExit(2 if result['gaps'] else 0)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
