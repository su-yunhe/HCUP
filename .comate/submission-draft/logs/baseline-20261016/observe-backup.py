from datetime import datetime, timezone
from pathlib import Path
import subprocess, shutil, json, time
ROOT = Path(__file__).resolve().parent
hdc = shutil.which('hdc')
def shell(*args):
    begin = datetime.now(timezone.utc).isoformat()
    p = subprocess.run([hdc, '-t', '127.0.0.1:5555', *args], text=True, capture_output=True, encoding='utf8', timeout=30)
    print(begin, datetime.now(timezone.utc).isoformat(), args, 'exit=', p.returncode, p.stdout, p.stderr, flush=True)
    if p.returncode: raise RuntimeError(args)
def snapshot(name):
    remote = '/data/local/tmp/vg13-' + name
    begin = datetime.now(timezone.utc).isoformat()
    shell('shell','uitest','dumpLayout','-p',remote+'.json')
    shell('file','recv',remote+'.json',str(ROOT/(name+'.json')))
    shell('shell','uitest','screenCap','-p',remote+'.png')
    shell('file','recv',remote+'.png',str(ROOT/(name+'.png')))
    tree = json.loads((ROOT/(name+'.json')).read_text(encoding='utf8'))
    nodes=[]
    def walk(n):
        nodes.append(n.get('attributes',{}))
        for c in n.get('children',[]): walk(c)
    walk(tree)
    summary={'name':name,'dump_started_utc':begin,'capture_finished_utc':datetime.now(timezone.utc).isoformat(),'loading_progress_count':sum(n.get('type')=='LoadingProgress' for n in nodes),'buttons':[{'text':n.get('text'), 'enabled':n.get('enabled'), 'id':n.get('id')} for n in nodes if n.get('type')=='Button'],'busy_texts':[n.get('text') for n in nodes if any(x in n.get('text','') for x in ['正在','处理中','备份已上传','失败'])]}
    with (ROOT/'backup-observations.jsonl').open('a',encoding='utf8') as f: f.write(json.dumps(summary,ensure_ascii=False)+'\n')
    print(summary,flush=True)
print('BACKUP_CLICK_UTC', datetime.now(timezone.utc).isoformat(),flush=True)
shell('shell','uitest','uiInput','click','400','1940')
snapshot('07-busy-early')
time.sleep(2)
snapshot('08-busy-mid')
time.sleep(2)
snapshot('09-busy-late')
time.sleep(5)
snapshot('10-completed')
