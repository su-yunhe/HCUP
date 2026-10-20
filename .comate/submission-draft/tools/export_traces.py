"""Export only this task's native sessions and observable transcript."""
from pathlib import Path
from datetime import datetime,timezone
import collections,hashlib,json,os,re,shutil,subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.comate/submission-draft'
HOME=Path.home()/'.codex'
INIT='01a13fc4-2611-7761-a580-1283e0c70541'

def digest(b):return hashlib.sha256(b).hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def normalized(s):return str(s).replace('\\','/').lower().rstrip('/')
def main():
    t=OUT/'traces';t.mkdir(parents=True,exist_ok=True)
    # Run two independent exact-boundary searches. Reject foreign CWDs using metadata only.
    patterns={'project_path':r'D:[/\\]HCUP[/\\]vg-spec1([/\\"\s]|$)',
              'task_id':r'(^|[^A-Za-z0-9_-])vg-spec1([^A-Za-z0-9_-]|$)'}
    hits={};candidates=set()
    for mode,pat in patterns.items():
        p=subprocess.run(['rg','-l','-e',pat,str(HOME/'sessions'),'--glob','*.jsonl'],stdout=subprocess.PIPE,check=False)
        found=set(p.stdout.decode().splitlines());candidates|=found;hits[mode]=found
    sidebar={}
    idx=HOME/'session_index.jsonl'
    if idx.exists():
        for line in idx.read_text(encoding='utf-8').splitlines():
            try:o=json.loads(line)
            except ValueError:continue
            sidebar[o['id']]=o
    records=[];edits=[];selected_index=[];excluded_count=0
    for fn in sorted(candidates):
        src=Path(fn)
        with src.open(encoding='utf-8') as f:
            try:meta=json.loads(f.readline()).get('payload',{})
            except ValueError:continue
        sid=meta.get('id') or meta.get('session_id')
        if sid==INIT or normalized(meta.get('cwd',''))!=normalized(ROOT):
            excluded_count+=1;continue
        data=src.read_bytes();lines=data.splitlines(keepends=True)
        model=set();effort=set();tools=collections.Counter();tokens=None;turns=0
        markdown=[f'# Codex会话 {sid}', '', '自动转写的可见消息与工具记录，不是IDE侧边栏原生Markdown导出。原生JSONL为主证据。', '']
        export=[];redactions=[];kinds=collections.Counter()
        for i,line in enumerate(lines,1):
            try:o=json.loads(line)
            except ValueError:
                redactions.append({'line':i,'reason':'snapshot trailing partial JSON record omitted','sha256':digest(line)});continue
            typ=o.get('type');p=o.get('payload',{});kinds[typ]+=1
            if typ=='turn_context':
                turns+=1
                if p.get('model'):model.add(p['model'])
                if p.get('effort'):effort.add(p['effort'])
            if typ=='event_msg' and p.get('type')=='token_count': tokens=(p.get('info') or {}).get('total_token_usage',tokens)
            if typ=='response_item' and p.get('type') in ('function_call','custom_tool_call'):
                tools[p.get('name','')]+=1
                arg=p.get('arguments',p.get('input',''))
                for n in re.findall(r'tools\.([A-Za-z0-9_]+)\s*\(',str(arg)):tools['nested:'+n]+=1
                if p.get('name')=='apply_patch' or 'apply_patch(' in str(arg):edits.append({'session_id':sid,'source_line':i,'call_id':p.get('call_id'),'native':f'native/{sid}.jsonl'})
            # Keep protocol fields; omit internal model reasoning from the deliverable copy.
            if (typ=='response_item' and (p.get('type')=='reasoning' or p.get('channel')=='analysis')) or (typ=='event_msg' and p.get('type') in ('agent_reasoning','agent_reasoning_raw_content')):
                redactions.append({'line':i,'reason':'non-user-visible internal model reasoning omitted','sha256':digest(line)});continue
            # This collection turn briefly printed global search-hit headers. Do not export foreign session metadata.
            if typ=='response_item' and p.get('type') in ('function_call_output','custom_tool_call_output'):
                val=str(p.get('output',''))
                if 'excluded_nonlocal_metadata_count' not in val and re.search(r'"cwd"\s*:\s*"D:\\\\HCUP\\\\vg-spec(?:[0-9]{2,}|[2-9])"', val):
                    p=dict(p);p['output']='[跨工作区检索命中元数据已排除；仅为会话标识/CWD/大小，未导出无关会话正文。原字段SHA256: '+digest(val.encode())+']';o=dict(o);o['payload']=p
                    line=(json.dumps(o,ensure_ascii=False)+'\n').encode()
                    redactions.append({'line':i,'reason':'foreign search-hit metadata omitted','sha256':digest(val.encode())})
            export.append(line)
            if typ!='response_item':continue
            if p.get('type')=='message':
                role=p.get('role','message');parts=[]
                for c in p.get('content',[]):
                    if isinstance(c,dict) and c.get('text'):parts.append(c['text'])
                if parts:markdown.extend([f'## {role} · 原生行 {i}', '', '\n\n'.join(parts),''])
            elif p.get('type') in ('function_call','custom_tool_call'):
                markdown.extend([f"## 工具 {p.get('name')} · 原生行 {i}",'',str(p.get('arguments',p.get('input',''))),''])
            elif p.get('type') in ('function_call_output','custom_tool_call_output'):
                markdown.extend([f'## 工具返回 · 原生行 {i}','',str(p.get('output','')),''])
        dest=t/'native'/f'{sid}.jsonl';dest.parent.mkdir(exist_ok=True);dest.write_bytes(b''.join(export))
        md=t/'markdown'/f'{sid}.md';md.parent.mkdir(exist_ok=True);md.write_text('\n'.join(markdown),encoding='utf-8')
        source=meta.get('source');spawn=source.get('subagent',{}).get('thread_spawn',{}) if isinstance(source,dict) else {}
        rec={'codex_native_session_id':sid,'codex_sidebar_id':sid if sid in sidebar else '【待补充：子会话无独立侧边栏索引行】',
          'sidebar_evidence':'filtered-session-index.jsonl' if sid in sidebar else None,
          'comate_sessionUuid':'【待补充：本机未找到Comate store，本次证据为Codex】','comate_ide_sidebar_id':'【待补充：无Comate双ID映射证据】',
          'agent':spawn.get('agent_role','orchestrator'),'agent_path':spawn.get('agent_path','/root'),'parent_thread_id':spawn.get('parent_thread_id'),
          'cli_version':meta.get('cli_version'),'originator':meta.get('originator'),'models':sorted(model),'efforts':sorted(effort),'turn_context_count':turns,
          'token_usage_last_total':tokens,'token_note':'最后一条token_count.info.total_token_usage；快照截点值，不对重复快照累加，不推断客户端账单或隐藏内部token',
          'native_file':f'native/{sid}.jsonl','markdown_file':f'markdown/{sid}.md','source_path':str(src),'source_bytes':len(data),'source_sha256':digest(data),
          'export_sha256':digest(dest.read_bytes()),'markdown_sha256':digest(md.read_bytes()),'source_lines':len(lines),'export_lines':len(export),'ends_with_newline':data.endswith(b'\n'),
          'timestamp':meta.get('timestamp'),'snapshot_at':datetime.now(timezone.utc).isoformat(),'snapshot_only':True,
          'search_matches':[k for k,v in hits.items() if fn in v],'tools':dict(tools),'redactions':redactions,'appliedRuleNames':'【待补充：Codex原生记录未提供该Comate字段】'}
        records.append(rec)
        if sid in sidebar:selected_index.append(sidebar[sid])
    (t/'filtered-session-index.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in selected_index),encoding='utf-8')
    save(t/'sessions.json',{'exported_at':datetime.now(timezone.utc).isoformat(),'sessions':records,'search':{'dimensions':list(patterns),'excluded_nonlocal_or_mixed_count':excluded_count,'excluded_mixed_initialization_id':INIT,'rule':'search hits do not establish task relevance; require exact local cwd. Shared setup overview excluded, never feature evidence.'},'gaps':['Comate store及双ID、Mac product.json/扩展版本不适用于当前Windows Codex；未编造映射','IDE原生Markdown导出目录未提供，现Markdown为可见原生事件的脚本转写','当前材料主会话和活跃子会话仅为导出时快照，不含其后事件','原生记录中内部推理字段不纳入可见材料；删行位置与摘要在逐会话redactions登记']})
    save(t/'code-edit-index.json',{'events':edits,'note':'原生工具调用行索引；最终代码由changes/project-manifest.json和final.diff界定，旧源码patch仍在project/logs、project/traces。'})
    # Make changed production files convenient to inspect without copying the whole tree again.
    baseline=json.loads((ROOT/'spec/metadata.json').read_text())['base_commit']
    changed=subprocess.check_output(['git','diff','--name-only',baseline,'--','entry'],cwd=ROOT).decode().splitlines()
    added=subprocess.check_output(['git','ls-files','--others','--exclude-standard','--','entry'],cwd=ROOT).decode().splitlines()
    code=[]
    for n in sorted(set(changed+added)):
        p=ROOT/n
        if not p.is_file():continue
        dst=t/'code-snapshot'/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst);code.append({'path':n,'sha256':digest(p.read_bytes()),'bytes':p.stat().st_size})
    save(t/'code-snapshot/manifest.json',{'files':code,'scope':'6 changed production .ets files; full project is described by changes/project-manifest.json'})
    print(json.dumps({'sessions':len(records),'native_bytes':sum((t/x['native_file']).stat().st_size for x in records),'codex_ids':[x['codex_native_session_id'] for x in records],'excluded_count':excluded_count},ensure_ascii=False))

if __name__=='__main__':main()
