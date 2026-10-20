"""Export only task-matched Codex records; generated Markdown is a reading aid."""
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
STORE = Path.home() / '.codex/sessions'
INDEX = Path.home() / '.codex/session_index.jsonl'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    state = json.loads((ROOT / 'workflow/state.json').read_text(encoding='utf-8-sig'))
    registered = {x['session_id'] for x in state['sessions'] if x.get('session_id')}
    paths = list(STORE.rglob('*.jsonl'))
    # Search twice independently, printing filenames only; do not export other chats.
    searches = {}
    for label, needles in [('project_path', [str(ROOT), ROOT.as_posix(), str(ROOT).replace('\\', '\\\\')]), ('task_id', ['vg-spec15'])]:
        cmd = ['rg', '-l', '-F', '--glob', '*.jsonl']
        for needle in needles:
            cmd += ['-e', needle]
        cmd += [str(STORE)]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        if res.returncode not in (0, 1):
            raise RuntimeError(res.stderr)
        searches[label] = set(res.stdout.splitlines())
    candidates, selected = [], []
    for path in paths:
        if str(path) not in searches['project_path'] | searches['task_id']:
            continue
        with path.open('r', encoding='utf-8') as stream:
            header = json.loads(stream.readline())
        p = header.get('payload', {})
        sid = p.get('id') or p.get('session_id')
        cwd = p.get('cwd', '').replace('\\', '/').rstrip('/').casefold()
        included = sid in registered or cwd == ROOT.as_posix().casefold()
        row = {'session_id': sid, 'source': str(path), 'cwd': p.get('cwd'),
               'project_path_match': str(path) in searches['project_path'],
               'task_id_match': str(path) in searches['task_id'],
               'registered': sid in registered, 'included': included,
               'reason': 'registered task session or exact task cwd' if included else 'different workspace; not copied; requires task-specific review if relevant'}
        candidates.append(row)
        if included:
            selected.append((sid, path, header))
    write_json(OUT / 'traces/discovery.json', {'created_at': dt.datetime.now(dt.timezone.utc).isoformat(),
               'searches': {k: {'matches': len(v), 'method': 'rg -l -F native JSONL; filenames only'} for k,v in searches.items()},
               'comate_store_exists': (Path.home()/'.comate-engine/store/comate_chat_sessions.jsonl').exists(),
               'candidates': candidates})
    index_lines = []
    if INDEX.exists():
        ids = {x[0] for x in selected}
        for line in INDEX.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            if row.get('id') in ids or row.get('thread_id') in ids:
                index_lines.append(line)
    (OUT / 'traces').mkdir(parents=True, exist_ok=True)
    (OUT / 'traces/session-index.filtered.jsonl').write_text('\n'.join(index_lines)+'\n', encoding='utf-8')
    sidebar_ids={json.loads(x).get('id') for x in index_lines}
    inventory=[]
    skill_calls=[]
    for sid, source, header in selected:
        raw=source.read_bytes()
        target=OUT/'traces/native'/f'{sid}.jsonl'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        models=collections.Counter(); efforts=collections.Counter(); tools=collections.Counter()
        tokens=[]; parse_errors=[]; red_flags=[]; contexts=[]
        md=['# Codex 原生记录阅读副本', '', f'会话：`{sid}`', '',
            '本文件由原生 JSONL 机械转换，不是 IDE 的“导出本地”。完整工具返回和失败均保留；JSONL 是权威记录。', '']
        for number,line in enumerate(raw.splitlines(),1):
            try:
                row=json.loads(line)
            except (ValueError, UnicodeError) as exc:
                parse_errors.append({'line':number, 'error':str(exc)})
                continue
            typ=row.get('type'); p=row.get('payload',{})
            if typ=='turn_context':
                if p.get('model'): models[p['model']]+=1
                effort=p.get('effort') or p.get('reasoning_effort')
                if effort: efforts[str(effort)]+=1
                contexts.append({'line':number,'model':p.get('model'),'effort':effort})
            if typ=='event_msg' and p.get('type')=='token_count':
                info=p.get('info') or {}
                if info.get('total_token_usage'):
                    tokens.append({'line':number, **info['total_token_usage']})
            if typ=='response_item' and p.get('type') in ('function_call','custom_tool_call'):
                tools[p.get('name','unavailable')]+=1
                args=p.get('arguments') or p.get('input') or ''
                if isinstance(args,str):
                    for nested in re.findall(r'tools\.([A-Za-z0-9_]+)\s*\(',args):
                        tools['nested:'+nested]+=1
                    if re.search(r'SKILL\.md|snapshot_traces\.py|workflow\.py|doc_index\.json',args,re.I):
                        skill_calls.append({'session_id':sid,'line':number,'tool':p.get('name'),
                                            'arguments':args,'interpretation':'actual tool input, not proof that every command succeeded; inspect following native outputs'})
            # Keep every native record in the Markdown copy, including tool errors and retries.
            md += [f'## 行 {number} · {row.get("timestamp", "")} · {typ}', '', '```json', json.dumps(row,ensure_ascii=False), '```', '']
        md_target=OUT/'traces/markdown'/f'{sid}.md'
        md_target.parent.mkdir(parents=True, exist_ok=True)
        md_target.write_text('\n'.join(md),encoding='utf-8')
        p=header['payload']
        inventory.append({'native_session_id':sid, 'sidebar_thread_id':sid if sid in sidebar_ids else None,
           'id_relationship':'Main chats: session_meta.payload.id/session_id equals local session index id. Subagents: native thread id preserved; no independent sidebar entry found. Comate sessionUuid is not available in this runtime.',
           'source':str(source),'export':target.relative_to(OUT).as_posix(),'bytes':len(raw),'sha256':digest(raw),
           'package_path':'traces/vg-spec15/native/'+sid+'.jsonl',
           'exported_at':dt.datetime.now(dt.timezone.utc).isoformat(),
           'markdown':md_target.relative_to(OUT).as_posix(),
           'markdown_package_path':'traces/vg-spec15/markdown/'+sid+'.md', 'snapshot_only':True,'parse_errors':parse_errors,
           'timestamp':p.get('timestamp'),'cwd':p.get('cwd'),'originator':p.get('originator'),
           'cli_version':p.get('cli_version'),'thread_source':p.get('thread_source'),'agent':p.get('agent_role') or p.get('agent_nickname') or p.get('source'),
           'model_ids':dict(models),'effort_values':dict(efforts), 'turn_contexts':contexts,
           'last_cumulative_token_usage':tokens[-1] if tokens else None,
           'token_accounting':'Last native cumulative total only, not the sum of cumulative samples. This is session usage, not API billing.',
           'tool_invocations':dict(tools), 'setup_only':sid=='01a13fc4-2611-7761-a580-1283e0c70541'})
    write_json(OUT/'traces/session-inventory.json',inventory)
    write_json(OUT/'traces/tool-skill-index.json',{'method':'Index actual skill/workflow-related tool inputs with native line numbers. Failures remain in original following tool outputs. No inference of successful invocation from a filename alone.', 'calls':skill_calls})
    print(json.dumps({'included':len(inventory), 'discovery_candidates':len(candidates),
                     'other_workspace_candidates':sum(not x['included'] for x in candidates),
                     'raw_bytes':sum(x['bytes'] for x in inventory),
                     'ids':[x['native_session_id'] for x in inventory]},ensure_ascii=False))

if __name__=='__main__': main()
