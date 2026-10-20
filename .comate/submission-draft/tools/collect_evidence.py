"""Read this task's evidence only; never export an entire client store."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
STORE = Path.home() / '.codex'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    if result.returncode:
        raise RuntimeError(str(args) + ': ' + result.stderr.decode('utf-8', 'replace'))
    return result.stdout


def redact_unrelated_index_rows(value, allowed):
    """Remove only unrelated sidebar metadata accidentally returned during inventory.

    This does not redact task messages, tools, failures, source or code decisions.
    Native tool outputs can contain nested JSON-encoded strings.
    """
    if isinstance(value, dict):
        if 'thread_name' in value and 'id' in value and value['id'] not in allowed:
            return {'redacted_unrelated_sidebar_index_row': True}, 1
        result, count = {}, 0
        for key, item in value.items():
            result[key], changed = redact_unrelated_index_rows(item, allowed)
            count += changed
        return result, count
    if isinstance(value, list):
        result, count = [], 0
        for item in value:
            clean, changed = redact_unrelated_index_rows(item, allowed)
            result.append(clean)
            count += changed
        return result, count
    if isinstance(value, str) and 'thread_name' in value:
        try:
            parsed = json.loads(value)
        except ValueError:
            parsed = None
        if isinstance(parsed, (dict, list)):
            clean, count = redact_unrelated_index_rows(parsed, allowed)
            if count:
                return json.dumps(clean, ensure_ascii=False), count
        lines, count = [], 0
        for line in value.splitlines(keepends=True):
            try:
                parsed = json.loads(line)
            except ValueError:
                parsed = None
            if isinstance(parsed, dict) and 'thread_name' in parsed and parsed.get('id') not in allowed:
                lines.append('[REDACTED: unrelated sidebar metadata row]\n')
                count += 1
            else:
                lines.append(line)
        if count:
            return ''.join(lines), count
    return value, 0


def main():
    state = json.loads((ROOT / 'workflow/state.json').read_text(encoding='utf-8'))
    roles = {item['session_id']: item for item in state['sessions'] if item.get('session_id')}
    # Two independent searches return filenames only. Unrelated matching bodies are not loaded.
    searches = {}
    for name, patterns in [('absolute_path', ['D:/HCUP/vg-spec9', 'D:\\HCUP\\vg-spec9', 'D:\\\\HCUP\\\\vg-spec9']),
                           ('task_id', ['vg-spec9'])]:
        args = ['rg', '-l', '-F', '--glob', '*.jsonl']
        for pattern in patterns:
            args.extend(['-e', pattern])
        result = subprocess.run(args + [str(STORE / 'sessions')], capture_output=True)
        if result.returncode not in (0, 1):
            raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
        searches[name] = {Path(p) for p in result.stdout.decode('utf-8').splitlines()}
    candidates = set.union(*searches.values())
    for sid in roles:
        if sid != OVERVIEW:
            candidates.update((STORE / 'sessions').rglob('*-' + sid + '.jsonl'))
    accepted = []
    excluded = Counter()
    for path in sorted(candidates):
        # Header metadata is used to select task-local sessions. Never inspect overview content.
        with path.open('rb') as handle:
            first = handle.readline()
        try:
            header = json.loads(first)['payload']
        except (ValueError, KeyError):
            excluded['invalid_header'] += 1
            continue
        sid = header.get('id')
        if sid == OVERVIEW:
            excluded['initialization_overview_non_task_specific'] += 1
            continue
        cwd = str(header.get('cwd', '')).replace('\\', '/').lower().rstrip('/')
        # Unknown candidates outside this exact workspace need user adjudication; no raw export.
        if sid not in roles and cwd != ROOT.as_posix().lower():
            excluded['other_workspace_candidate_not_exported'] += 1
            continue
        original_raw = path.read_bytes()
        records = []
        parse_errors = []
        redactions = []
        exported_lines = []
        for line_no, line in enumerate(original_raw.splitlines(keepends=True), 1):
            try:
                record = json.loads(line)
                clean, changed = redact_unrelated_index_rows(record, set(roles) - {OVERVIEW})
                if changed:
                    redactions.append({'native_line': line_no, 'unrelated_index_rows_replaced': changed})
                    exported_lines.append(json.dumps(clean, ensure_ascii=False).encode('utf-8') + b'\n')
                else:
                    exported_lines.append(line)
                records.append((line_no, clean))
            except ValueError:
                parse_errors.append(line_no)
                exported_lines.append(line)
        raw = b''.join(exported_lines)
        contexts = []
        tools = Counter()
        last_tokens = None
        response_models = Counter()
        skill_mentions = set()
        source_urls = set()
        tool_evidence = []
        for line_no, record in records:
            payload = record.get('payload', {})
            if record.get('type') == 'turn_context':
                item = {key: payload.get(key) for key in ('model', 'effort', 'reasoning_effort', 'approval_policy', 'sandbox_policy', 'collaboration_mode') if key in payload}
                if item not in contexts:
                    contexts.append(item)
            if record.get('type') == 'event_msg' and payload.get('type') == 'token_count':
                if payload.get('info'):
                    last_tokens = {'line': line_no, 'info': payload['info']}
            if record.get('type') == 'response_item' and payload.get('type') in ('function_call', 'custom_tool_call'):
                name = payload.get('name', '<unnamed>')
                tools[name] += 1
                arguments = payload.get('arguments', payload.get('input', ''))
                # Preserve references to real usage, not a fabricated inventory of capabilities.
                if 'SKILL.md' in str(arguments) or 'web__run' in str(arguments) or 'web.run' in str(arguments):
                    tool_evidence.append({'line': line_no, 'name': name, 'arguments': arguments})
                skill_mentions.update(re.findall(r'[^\s\"\'<>;,]*SKILL\.md', str(arguments)))
            if record.get('type') == 'response_item' and payload.get('model'):
                response_models[payload['model']] += 1
            text = json.dumps(payload, ensure_ascii=False)
            if 'web__run' in text or 'web.run' in text:
                source_urls.update(re.findall(r'https?://[^\s\"\\)<>]+', text))
        dest = OUT / 'traces/native' / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        md = OUT / 'traces/markdown' / (sid + '.md')
        md.parent.mkdir(parents=True, exist_ok=True)
        with md.open('w', encoding='utf-8', newline='\n') as handle:
            handle.write('# Native JSONL readable copy\n\nDerived mechanically; not an IDE sidebar export. All complete native records, including failed calls and retries, are retained.\n\n')
            for line_no, record in records:
                handle.write(f'## Native line {line_no}: {record.get("type")}\n\n')
                handle.write('````json\n' + json.dumps(record, ensure_ascii=False, indent=2) + '\n````\n\n')
        accepted.append({
            'session_id': sid, 'role': roles.get(sid, {}).get('role', 'task_local_unregistered'),
            'agent_id': roles.get(sid, {}).get('agent_id', '【待补充】'),
            'source': str(path), 'native_path': dest.relative_to(OUT).as_posix(),
            'markdown_path': md.relative_to(OUT).as_posix(), 'sha256': sha(raw), 'bytes': len(raw),
            'source_sha256': sha(original_raw), 'source_bytes': len(original_raw),
            'privacy_redactions': redactions,
            'records': len(records), 'parse_error_lines': parse_errors,
            'ends_with_newline': raw.endswith(b'\n'),
            'header': {key: value for key, value in header.items() if key not in ('base_instructions', 'dynamic_tools')},
            'contexts': contexts, 'tool_call_counts': dict(tools),
            'last_token_usage': last_tokens, 'response_models': dict(response_models),
            'skill_reference_strings': sorted(skill_mentions), 'web_source_urls': sorted(source_urls),
            'tool_evidence': tool_evidence,
            'found_by_absolute_path': path in searches['absolute_path'],
            'found_by_task_id': path in searches['task_id'],
        })
    ids = {item['session_id'] for item in accepted}
    # Only matching index lines leave the client store. Do not copy unrelated titles or sessions.
    index_lines = []
    index_path = STORE / 'session_index.jsonl'
    if index_path.exists():
        for line in index_path.read_text(encoding='utf-8').splitlines():
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if value.get('id') in ids:
                index_lines.append(line)
    (OUT / 'traces/filtered-session-index.jsonl').write_text('\n'.join(index_lines) + '\n', encoding='utf-8')
    index_ids = {json.loads(line)['id'] for line in index_lines}
    for item in accepted:
        sid = item['session_id']
        parent_sidebar = item['header'].get('session_id')
        item['ide_sidebar_session_id'] = sid if sid in index_ids else (parent_sidebar if parent_sidebar in index_ids else '【待补充】')
        item['id_relationship'] = ('Native session_meta.payload.id equals the matched sidebar session_index.id.' if sid in index_ids
                                   else ('Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row.' if parent_sidebar in index_ids
                                         else 'No sidebar row found; child native ID and parent spawn record are retained.'))
    common = ROOT.parent / 'common/spec-harness'
    taskbooks = {}
    for name in ('0-analyze.md', '1-do.md', '2-submit.md', '3-package.md'):
        source = common / name
        local = ROOT / 'spec-harness' / name
        taskbooks[name] = {'common_sha256': sha(source.read_bytes()), 'local_sha256': sha(local.read_bytes()),
                           'identical': source.read_bytes() == local.read_bytes()}
    git_files = run(['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z']).decode('utf-8').split('\0')
    scoped_files = sorted({p for p in git_files if p and not p.startswith('.comate/submission-draft/')})
    by_folder = Counter()
    for relative in scoped_files:
        path = ROOT / relative
        if path.is_file():
            by_folder[relative.split('/')[0]] += path.stat().st_size
    result = {
        'collected_at_utc': datetime.now(timezone.utc).isoformat(), 'task_id': 'vg-spec9',
        'current_session': os.environ.get('CODEX_THREAD_ID'),
        'searches': {key: {'matched_candidate_files': len(value), 'query_scope': str(STORE / 'sessions')} for key, value in searches.items()},
        'excluded_candidate_counts': dict(excluded), 'sessions': accepted,
        'registered_missing': sorted(set(roles) - ids - {OVERVIEW}),
        'common_git_commit': run(['git', '-C', str(common), 'rev-parse', 'HEAD']).decode().strip(),
        'taskbook_hashes': taskbooks,
        'history_files': [p.relative_to(ROOT).as_posix() for p in (ROOT / 'spec/history').rglob('*') if p.is_file()] if (ROOT / 'spec/history').exists() else [],
        'comate_index_exists': (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
        'specified_baseline_report_exists': Path('D:/SWE-OpenHarmony/reports/build-baselines/vg-spec9.log').exists(),
        'file_bytes_by_top_folder': dict(by_folder),
    }
    save(OUT / 'checks/evidence-inventory.json', result)
    save(OUT / 'checks/trace-redactions.json', {'method': 'Only unrelated sidebar id/title index rows in material-session tool outputs replaced; original client files unchanged. No task code, source, failure, retry, model or token fields concealed.',
         'sessions': [{'session_id': s['session_id'], 'source_sha256': s['source_sha256'], 'exported_sha256': s['sha256'], 'records': s['privacy_redactions']} for s in accepted if s['privacy_redactions']]})
    print(json.dumps({'sessions': [{k: x[k] for k in ('session_id', 'role', 'bytes', 'ide_sidebar_session_id')} for x in accepted],
                      'excluded': dict(excluded), 'common_commit': result['common_git_commit'],
                      'taskbooks': taskbooks, 'file_bytes_by_top_folder': dict(by_folder)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
