"""Reconcile derived tool counts without altering frozen project or native bytes."""
import collections
import json
from pathlib import Path

draft = Path(__file__).resolve().parent.parent
path = draft / 'traces/manifest.json'
manifest = json.loads(path.read_text(encoding='utf-8'))
for item in manifest['files']:
    counts = {}
    for line in (draft / item['native_path']).read_text(encoding='utf-8').splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            continue  # The original manifest identifies any incomplete final line.
        payload = record.get('payload', {})
        kind = payload.get('type')
        if kind in ('function_call', 'custom_tool_call'):
            counts.setdefault(kind, collections.Counter())[payload.get('name', '(unnamed)')] += 1
    combined = collections.Counter()
    for counter in counts.values():
        combined.update(counter)
    item['tools_by_call_type'] = {kind: dict(counter) for kind, counter in counts.items()}
    item['tools'] = dict(combined)
    item['tools_scope'] = 'top-level native function_call + custom_tool_call records; nested tools inside exec source are preserved in raw calls, not recursively counted'
manifest['tool_count_reconciliation'] = 'audit/reconcile-native-metadata.py; derived metadata only, native bytes and frozen project unchanged'
path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
