"""Task-scoped, read-only native extraction; writes only this traces directory.

Exact source paths come from this task's existing manifests and UUIDs from state.
No whole-client database discovery. JSONL originals are copied byte-for-byte;
Markdown is a complete derived rendering, never an IDE export.
"""
import collections
import datetime as dt
import hashlib
import json
import os
import pathlib
import re

ROOT = pathlib.Path('D:/HCUP/cml-spec28')
OUT = ROOT / '.comate/submission-draft/traces'
EXCLUDED = '01a13fc4-2611-7761-a580-1283e0c70541'
CURRENT_ROOT = '01a14f53-1fa0-72d2-b947-fa27e7fb37c7'
utc = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
sha = lambda b: hashlib.sha256(b).hexdigest()
started = utc()
state_bytes = (ROOT/'workflow/state.json').read_bytes()
state = json.loads(state_bytes.decode('utf-8-sig'))
registry = collections.OrderedDict()
for item in state['sessions']:
    sid = item.get('session_id')
    if sid and sid != EXCLUDED:
        registry.setdefault(sid, []).append(item)
source_map = {}
manifest_sources = []
for mp in sorted((ROOT/'traces/native').glob('*/manifest.json')):
    data = json.loads(mp.read_text(encoding='utf-8-sig'))
    manifest_sources.append({'path':mp.relative_to(ROOT).as_posix(), 'sha256':sha(mp.read_bytes())})
    for entry in data.get('files', data.get('records', [])):
        sid = entry.get('session_id')
        if sid in registry and entry.get('source'):
            source_map[sid] = entry['source']

run = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run_dir = OUT/run
run_dir.mkdir(parents=True, exist_ok=False)
(run_dir/'native').mkdir()
(run_dir/'markdown').mkdir()
records, gaps, potential_sensitive = [], [], []

def strings(obj, path='$'):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from strings(value, path+'.'+str(key))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from strings(value, path+'['+str(i)+']')
    elif isinstance(obj, str):
        yield path, obj

def fence(text, language=''):
    ticks = '`' * max(3, max((len(x) for x in re.findall(r'`+', text)), default=0)+1)
    return ticks+language+'\n'+text+'\n'+ticks+'\n'

for sid, registrations in registry.items():
    source_string = source_map.get(sid)
    if not source_string:
        gaps.append({'session_id':sid,'reason':'No exact source path in task manifests; no global discovery attempted'})
        continue
    source = pathlib.Path(source_string)
    if sid not in source.name or source.suffix != '.jsonl':
        raise RuntimeError('Source UUID/name mismatch')
    capture_started = utc()
    with source.open('rb') as stream:
        before = os.fstat(stream.fileno())
        data = stream.read(before.st_size)
        after = os.fstat(stream.fileno())
    captured_at = utc()
    lines = data.splitlines()
    parsed, invalid = [], []
    for no, line in enumerate(lines, 1):
        try:
            parsed.append((no, json.loads(line)))
        except Exception as exc:
            invalid.append({'line':no,'error':type(exc).__name__})
    metas = [(no,o['payload']) for no,o in parsed if o.get('type')=='session_meta']
    if len(metas)!=1 or metas[0][1].get('id') != sid:
        raise RuntimeError('session_meta ID not verified: '+sid)
    meta_line, meta = metas[0]
    cwd = str(meta.get('cwd','')).replace('\\','/').rstrip('/').casefold()
    if cwd != ROOT.as_posix().casefold():
        raise RuntimeError('session_meta cwd not task root: '+sid)
    raw = run_dir/'native'/source.name
    raw.write_bytes(data)
    markdown = run_dir/'markdown'/(sid+'.md')
    event_types = collections.Counter()
    tools = collections.Counter()
    models, efforts, policies = set(), set(), set()
    contexts, token_records, token_counts, skill_refs, tool_refs = [], [], [], [], []
    with markdown.open('w', encoding='utf-8', newline='\n') as output:
        output.write('# Native 会话完整可读派生副本\n\n')
        output.write('这是逐条 JSONL 事件的 Markdown 派生呈现，非 IDE 侧栏导出。原始字节、失败及工具事件未筛除。原始数据已有的截断/压缩保持原状；不声称恢复客户端未保存内容。\n\n')
        output.write(f'- UUID: `{sid}`\n- Source: `{source}`\n- Capture start: `{capture_started}`\n- Capture end: `{captured_at}`\n- SHA256: `{sha(data)}`\n- Snapshot only: true; includes_future_events: false\n- Raw: [JSONL](../native/{source.name})\n\n')
        for no, obj in parsed:
            kind = obj.get('type','unknown')
            payload = obj.get('payload', {})
            event_types[kind]+=1
            tag = payload.get('type', '') if isinstance(payload, dict) else ''
            name = payload.get('name', '') if isinstance(payload, dict) else ''
            output.write(f'## Event {no} · {obj.get("timestamp", "no timestamp")} · {kind} {tag} {name}\n\n')
            if isinstance(payload,dict):
                if kind=='turn_context':
                    model=payload.get('model'); effort=payload.get('effort')
                    if model: models.add(model)
                    if effort: efforts.add(effort)
                    if payload.get('approval_policy'): policies.add(payload['approval_policy'])
                    contexts.append({'line':no,'timestamp':obj.get('timestamp'),'payload':payload})
                if kind=='token_usage_record': token_records.append({'line':no,'timestamp':obj.get('timestamp'),'payload':payload})
                if kind=='event_msg' and tag=='token_count': token_counts.append({'line':no,'timestamp':obj.get('timestamp'),'payload':payload})
                if kind=='response_item' and tag in ('function_call','custom_tool_call'):
                    tools[name]+=1
                    text=json.dumps(payload,ensure_ascii=False)
                    tool_refs.append({'line':no,'name':name,'call_id':payload.get('call_id')})
                    if 'SKILL.md' in text or '-SKILL.md' in text:
                        skill_refs.append({'line':no,'name':name,'note':'Tool input mentions SKILL.md; inspect this event to distinguish read from discovery or quoted text'})
            readable = []
            for key,value in strings(payload):
                leaf=key.rsplit('.',1)[-1]
                if leaf in ('text','output','input','arguments','cmd','message','summary') and value:
                    if leaf=='arguments':
                        try:
                            decoded=json.loads(value)
                            for inner, content in strings(decoded):
                                if '\n' in content or inner.endswith(('.cmd','.code','.input','.prompt','.message')):
                                    readable.append((key+inner[1:], content))
                        except (ValueError,TypeError):
                            readable.append((key,value))
                    else: readable.append((key,value))
                # High-specificity candidates only, locations only. Public fixture value is excluded.
                for label,pattern in (
                    ('private-key-block',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
                    ('OpenAI-key-shape',r'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{25,}'),
                    ('bearer-token-shape',r'(?i)Bearer\s+(?!fixture28-public-identity\b)[A-Za-z0-9._~+/-]{24,}')):
                    if re.search(pattern,value):
                        potential_sensitive.append({'session_id':sid,'native_line':no,'field':key,'kind':label,'status':'candidate; values intentionally omitted'})
            for key,value in readable:
                output.write('### Readable '+key+'\n\n'+fence(value)+'\n')
            output.write('### Complete event JSON\n\n'+fence(json.dumps(obj,ensure_ascii=False,indent=2),'json')+'\n')
        for item in invalid:
            output.write('## Unparsed native line '+str(item['line'])+'\n\n'+fence(lines[item['line']-1].decode('utf-8',errors='replace'))+'\n')
    summary = {
        'session_id':sid,'registrations':registrations,'source':str(source),
        'session_meta':meta,'session_meta_line':meta_line,'session_meta_cwd_checked':True,
        'capture_started_at_utc':capture_started,'captured_at_utc':captured_at,
        'source_size_at_start':before.st_size,'source_size_at_end':after.st_size,
        'source_mtime_ns_at_start':before.st_mtime_ns,'source_mtime_ns_at_end':after.st_mtime_ns,
        'bytes':len(data),'sha256':sha(data),'line_count':len(lines),'ends_with_newline':data.endswith(b'\n'),
        'raw':raw.relative_to(ROOT).as_posix(),'markdown':markdown.relative_to(ROOT).as_posix(),
        'markdown_sha256':sha(markdown.read_bytes()),'markdown_bytes':markdown.stat().st_size,
        'parse_errors':invalid,'event_types':dict(event_types),'first_timestamp':parsed[0][1].get('timestamp') if parsed else None,
        'last_timestamp':parsed[-1][1].get('timestamp') if parsed else None,
        'models':sorted(models),'efforts':sorted(efforts),'approval_policies':sorted(policies),
        'tool_calls_by_name':dict(tools),'tool_call_locations':tool_refs,'skill_tool_input_references':skill_refs,
        'turn_contexts':contexts,'token_usage_records':token_records,
        'token_count_event_count':len(token_counts),'last_token_count_event':token_counts[-1] if token_counts else None,
        'token_accounting_note':'Per-session native reported counters/records, not billing or a deduplicated sum; inherited context and cached tokens may repeat.',
        'ide_sidebar_thread_id':sid if sid==CURRENT_ROOT else '【待补充】',
        'ide_mapping_evidence':'workflow/submit-app-thread-proof.json' if sid==CURRENT_ROOT else None,
        'snapshot_only':True,'includes_future_events':False}
    records.append(summary)
    if invalid: gaps.append({'session_id':sid,'reason':'Native JSONL parse errors retained','details':invalid})

comate_source = pathlib.Path('C:/Users/22580/.comate-engine/store/comate_chat_sessions.jsonl')
comate = {'source':str(comate_source),'exists':comate_source.is_file(),'lookup_dimensions':['D:/HCUP/cml-spec28','cml-spec28'],'matched_only':True,'whole_database_copied':False}
if comate_source.is_file():
    hits=[]; matched=[]; dimensions=collections.Counter()
    with comate_source.open('rb') as stream:
        for no,line in enumerate(stream,1):
            text=line.decode('utf-8',errors='replace')
            normalized=text.replace('\\\\','/').replace('\\','/').casefold()
            path_match=ROOT.as_posix().casefold() in normalized
            id_match='cml-spec28' in normalized
            if path_match or id_match:
                matched.append(line)
                hits.append({'index_line':no,'project_path_match':path_match,'task_id_match':id_match})
            dimensions['project_path']+=path_match;dimensions['task_id']+=id_match
    cp=run_dir/'comate-matching-index.jsonl';cp.write_bytes(b''.join(matched))
    comate.update({'hits':hits,'counts_by_dimension':dict(dimensions),'copy':cp.relative_to(ROOT).as_posix(),'sha256':sha(cp.read_bytes())})
else:
    comate.update({'result':'missing index; both project-path and task-ID lookup unavailable, no Comate native/IDE export claimed'})
    gaps.append({'kind':'Comate-index-missing','path':str(comate_source)})

config_inventory=[]
for path in sorted((ROOT/'system-config').rglob('*')):
    if path.is_file():config_inventory.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size})
references=[]
for path in [ROOT/'AGENTS.md', ROOT/'spec/metadata.json', ROOT/'spec/requirement.md', ROOT/'spec/acceptance.md',ROOT/'workflow/submit-app-thread-proof.json',ROOT/'workflow/baseline-provenance.json', ROOT/'logs/prepare-baseline.log', *[ROOT.parent/'common/spec-harness'/n for n in ('0-analyze.md','1-do.md','2-submit.md','3-package.md')], *[pathlib.Path('D:/SWE-OpenHarmony/templates')/n for n in ('trace-index.md','submission-checklist.md','submission.json')]]:
    references.append({'path':str(path),'exists':path.is_file(),**({'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size} if path.is_file() else {})})
manifest={
    'schema_version':1,'task_id':'cml-spec28','created_by_CODEX_THREAD_ID':os.environ.get('CODEX_THREAD_ID'),
    'started_at_utc':started,'finished_at_utc':utc(),'export_run':run,'root':str(ROOT),
    'method':'Exact UUID paths from task manifests; verify native session_meta.id and cwd; capture bounded original file bytes once; derive all-event Markdown without filtering failures/tools. Not IDE sidebar export.',
    'snapshot_only':True,'includes_future_events':False,'formal_freeze_time':None,
    'state_registry_source':'workflow/state.json','state_registry_sha256':sha(state_bytes),
    'registered_unique_session_count':len(registry),'exported_session_count':len(records),
    'excluded_sessions':[{'session_id':EXCLUDED,'reason':'Initialization overview; body not read, not exported'}],
    'null_registry_entries':[s for s in state['sessions'] if not s.get('session_id')],
    'source_task_manifests':manifest_sources,'sessions':records,'comate_index':comate,
    'system_config_inventory':config_inventory,'reference_hashes':references,
    'spec_history_exists':(ROOT/'spec/history').exists(),'common_git_metadata_present':(ROOT.parent/'common/.git').exists(),
    'desktop_client_version':'【待补充】; native session_meta.cli_version is runtime/CLI metadata, not an independently verified desktop UI version',
    'sensitive_scan':{'method':'High-specificity private-key, OpenAI-key, Bearer candidate regex over parsed native string fields; not exhaustive; values never printed','public_fixture_identity_excluded':True,'candidates':potential_sensitive,'redactions_applied':False,'upload_performed':False},
    'gaps':gaps+[
      {'kind':'old-sidebar-ID','reason':'Only current root mapping independently evidenced; other engine UUIDs have no separately saved IDE sidebar mapping'},
      {'kind':'desktop-version','reason':'Native runtime/CLI version available; desktop client product version independently unproven'},
      {'kind':'formal-freeze','reason':'Ongoing materials preparation; exports are snapshots, future messages/events excluded'},
      {'kind':'AUTH','reason':'Production original tests 1pass5AUTHskip; full 1-do acceptance not complete; fixture boundary successes do not prove real-auth acceptance'},
      {'kind':'old-failed-build-source','reason':'First failed development build has logs but no exact full pre-build source fingerprint; historical gap retained'},
      {'kind':'historical-script-drift','reason':'Registered fixture-matrix.py hash differs from later file; audited restored exact old SHA/2 note strings; old manifest not rewritten; old result full byte copy unavailable'}]}
manifest_path=OUT/'manifest.json'
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(run_dir/'manifest.json').write_bytes(manifest_path.read_bytes())
print(json.dumps({'manifest':str(manifest_path),'sha256':sha(manifest_path.read_bytes()),'export_run':run,'registered':len(registry),'exported':len(records),'raw_bytes':sum(s['bytes'] for s in records),'markdown_bytes':sum(s['markdown_bytes'] for s in records),'parse_errors':sum(len(s['parse_errors']) for s in records),'sensitive_candidate_count':len(potential_sensitive),'desktop_version':manifest['desktop_client_version'],'comate_exists':comate['exists'],'models':sorted(set(x for s in records for x in s['models'])),'efforts':sorted(set(x for s in records for x in s['efforts']))},ensure_ascii=False,indent=2))
