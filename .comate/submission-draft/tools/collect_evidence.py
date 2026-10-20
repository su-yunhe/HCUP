"""Task-only evidence export. No production edits and no external network access."""
from pathlib import Path
from datetime import datetime, timezone
import collections, hashlib, json, os, re, shutil, subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
STORE = Path(os.environ.get('CODEX_HOME') or Path.home()/'.codex')
EXCLUDED_ID = '01a13fc4-2611-7761-a580-1283e0c70541'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):h.update(b)
    return h.hexdigest()

def write(p, obj):
    p=OUT/p;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def collect():
    started=datetime.now(timezone.utc).isoformat()
    sidebar_ids=set()
    for line in (STORE/'session_index.jsonl').read_text('utf-8').splitlines():
        try:sidebar_ids.add(json.loads(line).get('id'))
        except ValueError:continue
    selected=[];headers={};allfiles=sorted((STORE/'sessions').rglob('*.jsonl'))
    for p in allfiles:
        if EXCLUDED_ID in p.name:continue
        with p.open('rb') as f: line=f.readline()
        try: d=json.loads(line);m=d.get('payload',{})
        except (ValueError,AttributeError):continue
        headers[str(p)]=m
        cwd=str(m.get('cwd','')).replace('\\','/').lower().rstrip('/')
        if cwd==ROOT.as_posix().lower() and m.get('id')!=EXCLUDED_ID:selected.append(p)
    # Discover task-id candidates in the lightweight index, without searching unrelated bodies.
    index_task_hits=[];index_candidates=[]
    for line in (STORE/'session_index.jsonl').read_text('utf-8').splitlines():
        try:item=json.loads(line)
        except ValueError:continue
        if 'cml-spec1' in line.lower():
            index_task_hits.append(item.get('id'))
            index_candidates.append({'id':item.get('id'),'decision':'included' if any(headers[str(p)].get('id')==item.get('id') for p in selected) else 'excluded',
              'reason':'Task cwd approved' if any(headers[str(p)].get('id')==item.get('id') for p in selected) else 'Not task-cwd approved or mixed initialization; content not opened for this lookup'})
    # Content search is limited to cwd-approved task records, with overview excluded first.
    query=subprocess.run(['rg','-l','--fixed-strings','cml-spec1',*[str(p) for p in selected]],capture_output=True,text=True)
    hits=[str(Path(x)) for x in query.stdout.splitlines()]
    outside=[x for x in hits if Path(x) not in selected]
    rows=[];calls=[];index_ids=set();exported=OUT/'traces/native';exported.mkdir(parents=True,exist_ok=True)
    for p in selected:
        raw=p.read_bytes();target=exported/p.name;target.write_bytes(raw)
        meta=headers[str(p)];sid=meta['id'];index_ids.add(sid)
        contexts=set();tools=collections.Counter();nested=collections.Counter();tokens=None;invalid=[];md=[]
        for n,line in enumerate(raw.splitlines(),1):
            try:d=json.loads(line)
            except ValueError:invalid.append(n);continue
            q=d.get('payload',{});typ=d.get('type');timestamp=d.get('timestamp','')
            if typ=='turn_context':contexts.add((str(q.get('model')),str(q.get('effort'))))
            if q.get('type')=='token_count':tokens=q.get('info',{}).get('total_token_usage')
            if q.get('type') in ('function_call','custom_tool_call'):
                tools[q.get('name')]+=1
                args=q.get('arguments',q.get('input',''))
                if isinstance(args,str):
                    for tool in re.findall(r'tools\.([a-zA-Z0-9_]+)\s*\(',args):nested[tool]+=1
                calls.append({'native_file':target.name,'line':n,'timestamp':timestamp,'session_id':sid,'tool':q.get('name'),'call_id':q.get('call_id')})
            # A readable, lossless JSON representation of every native record, not an IDE export.
            md.append(f'### Native line {n} | {timestamp} | {typ}\n\n````json\n'+json.dumps(d,ensure_ascii=False,indent=2)+'\n````\n')
        mpath=OUT/'traces/markdown'/ (p.stem+'.md');mpath.parent.mkdir(parents=True,exist_ok=True)
        mpath.write_text('# Native JSONL Markdown rendering\n\n自动逐行转换，非 IDE 侧边栏导出；未省略工具结果和失败记录。原生 JSONL 是权威副本。\n\n'+'\n'.join(md),encoding='utf-8')
        rows.append({'session_id':sid,'engine_sessionUuid':'【待补充】（Codex 原生格式没有该 Comate 字段）',
          'codex_thread_id':sid,'sidebar_thread_id':sid if sid in sidebar_ids else '【待补充】（未在侧边栏索引中找到，保留实际原生子线程ID）',
          'mapping_evidence':'session_meta.payload.id/session_id; sidebar mapping asserted only for actual matching session_index.jsonl entries',
          'agent_path':meta.get('agent_path','root'),'originator':meta.get('originator'),'cli_version':meta.get('cli_version'),
          'native_source':str(p),'native_export':'traces/native/'+p.name,'sha256':sha(target),'bytes':len(raw),
          'markdown':'traces/markdown/'+mpath.name,'models_efforts':sorted(contexts),'last_total_token_usage':tokens,
          'token_scope':'Last native token_count per segment; do not sum segments as an audited billing total.',
          'tools':dict(tools),'nested_tools':dict(nested),'parse_error_lines':invalid,'ends_with_newline':raw.endswith(b'\n'),
          'first_timestamp':json.loads(raw.splitlines()[0]).get('timestamp'),'last_timestamp':json.loads(raw.splitlines()[-1]).get('timestamp'),
          'snapshot_only':True,'includes_future_events':False})
    filtered=[]
    for line in (STORE/'session_index.jsonl').read_bytes().splitlines(keepends=True):
        try:d=json.loads(line)
        except ValueError:continue
        if d.get('id') in index_ids:filtered.append(line)
    (OUT/'traces/session_index.filtered.jsonl').write_bytes(b''.join(filtered))
    with (OUT/'traces/tool-call-index.jsonl').open('w',encoding='utf-8') as f:
        for row in calls:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    write('traces/native-manifest.json',{'export_started_utc':started,'export_finished_utc':datetime.now(timezone.utc).isoformat(),
       'selection':'Task cwd metadata + task-id lookup in lightweight session index + rg restricted to cwd-approved task native files; non-task workspaces never copied.',
       'cwd_matches_files':len(selected),'task_id_search_hit_count':len(hits),'excluded_non_task_or_overview_hits_count':len(outside),
       'task_id_index_hit_count':len(index_task_hits),'task_id_index_hits_not_cwd_approved_count':len(set(index_task_hits)-index_ids),
       'task_id_index_candidates':index_candidates,
       'excluded_overview_id':EXCLUDED_ID,'files':rows,'filtered_index_rows':len(filtered),
       'audit_scope_disclosure':['The initial task-id filename-only rg query searched the whole native store, including mixed initialization records; it emitted filenames only, and no non-task raw file was copied. It was replaced by metadata/index-first selection. This is material collection, not feature-development evidence.',
          'The implementation audit initially read 8000-byte prefixes of git-visible process files before excluding the mixed initialization snapshot; its report discloses the scope mistake.'],
       'gaps':['Comate database and sessionUuid fields absent; Codex native JSONL supplied instead.',
               'IDE sidebar Markdown export directory not supplied; Markdown is generated from native JSONL.',
               'Current preparation chat is an as-of export, not a final export of future events.']})
    # Preserve build/test logs byte-for-byte, without rerunning or creating replacement evidence.
    logrows=[]
    for p in sorted((ROOT/'logs').rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(ROOT/'logs');dest=OUT/'logs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        logrows.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    write('logs-manifest.json',logrows)
    common=ROOT.parent/'common'
    top=subprocess.run(['git','-C',str(common),'rev-parse','--show-toplevel'],capture_output=True,text=True)
    commit=subprocess.run(['git','-C',str(common),'rev-parse','HEAD'],capture_output=True,text=True)
    docs=[]
    for name in ('0-analyze.md','1-do.md','2-submit.md','3-package.md'):
        p=common/'spec-harness'/name;dest=OUT/'traces/taskbooks/common'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        local=ROOT/'spec-harness'/name
        docs.append({'file':name,'common_sha256':sha(p),'task_local_sha256':sha(local),'equal':sha(p)==sha(local)})
    write('traces/taskbooks/version.json',{'git_toplevel':top.stdout.strip(),'common_own_git_root':top.stdout.strip().replace('\\','/').lower()==common.as_posix().lower(),
       'containing_git_head':commit.stdout.strip(),'version_policy':'common is a tracked subdirectory of the HCUP repository, not an independent repository. Both containing HEAD and four file hashes recorded.',
       'files':docs,'task_history_exists':(ROOT/'spec/history').exists(),'used_historical_hash_evidence':'Original prompts/native records and system-config snapshots; current hashes do not by themselves establish historical use.'})
    for name in ('submission-checklist.md','trace-index.md','submission.json'):
        src=Path('D:/SWE-OpenHarmony/templates')/name;dest=OUT/'traces/official-templates'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    frozen=json.loads((ROOT/'traces/do-implementation/source-frozen-r2.json').read_text('utf-8'))
    differences=[k for k,v in frozen['files_sha256'].items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
    hap=ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap'
    write('production-preservation.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'files':len(frozen['files_sha256']),
       'source_manifest':'traces/do-implementation/source-frozen-r2.json','source_aggregate':frozen['source_aggregate_sha256'],
       'changed_paths':differences,'hap_bytes':hap.stat().st_size,'hap_sha256':sha(hap),'pass':not differences})
    print(json.dumps({'native_segments':len(rows),'unique_session_ids':len(index_ids),'logs':len(logrows),'production_changed':differences},ensure_ascii=False))

if __name__=='__main__':collect()
