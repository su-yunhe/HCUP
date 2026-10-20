"""Index actual SKILL.md read commands in task-only exported native records."""
import json
import re
from prepare_materials import OUT, dump

pattern = re.compile(r"Get-Content(?:\s+-[A-Za-z]+)*\s+(?:['\"]([^'\"\r\n]*SKILL\.md)['\"]|([^\s;'\"]*SKILL\.md))")
reads = []
for file in sorted((OUT / 'traces/native').glob('*.jsonl')):
    for index, line in enumerate(file.read_text(encoding='utf-8').splitlines(), 1):
        row = json.loads(line)
        payload = row.get('payload', {})
        if row.get('type') != 'response_item' or payload.get('type') not in ('function_call', 'custom_tool_call'):
            continue
        text = str(payload.get('arguments', payload.get('input', '')))
        # Decode JSON tool arguments when possible, but do not execute them.
        try:
            decoded = json.loads(text)
            if isinstance(decoded, dict):
                text = '\n'.join(str(x) for x in decoded.values())
        except ValueError:
            pass
        for match in pattern.finditer(text):
            path = (match.group(1) or match.group(2)).replace('\\\\', '\\')
            # A bare filename in generated prose is ambiguous and is not evidence of a read.
            if '/' not in path and '\\' not in path:
                continue
            reads.append({'skill_path_in_actual_tool_input': path,
                          'thread_id': file.stem, 'native_line': index, 'timestamp': row.get('timestamp'),
                          'call_id': payload.get('call_id'), 'tool': payload.get('name')})
dump('traces/skill-read-index.json', {'method': 'Observed Get-Content SKILL.md read commands in native tool inputs, with exact record pointers. Native injected role/base instructions are separate and remain in session_meta/turn_context.',
     'reads': reads, 'unique_paths': sorted({x['skill_path_in_actual_tool_input'] for x in reads})})
print(json.dumps({'skill_reads': len(reads), 'unique_paths': len({x['skill_path_in_actual_tool_input'] for x in reads})}))
