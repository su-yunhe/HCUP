"""Read/click the baseline UI; every device command and exit is recorded."""
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'traces/baseline-analysis'
def run(*args):
    t = datetime.datetime.now().astimezone().isoformat()
    p = subprocess.run(['hdc', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    with (OUT / 'ui-commands.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({'time':t, 'argv':['hdc', *args], 'exit':p.returncode, 'stdout':p.stdout, 'stderr':p.stderr}, ensure_ascii=False)+'\n')
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
def nodes(d):
    yield d.get('attributes', {})
    for c in d.get('children', []): yield from nodes(c)
def dump(name, screenshot=False):
    remote=f'/data/local/tmp/vg-spec9-{name}.json'
    run('shell','uitest','dumpLayout','-p',remote)
    run('file','recv',remote,f'traces/baseline-analysis/{name}.json')
    d=json.loads((OUT/f'{name}.json').read_text(encoding='utf-8'))
    rows=[a for a in nodes(d) if a.get('text') or a.get('type') in ['LoadingProgress','TextInput','Button','Toggle']]
    (OUT/f'{name}-summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:a.get(k) for k in ['text','hint','type','bounds','id','enabled','visible']} for a in rows],ensure_ascii=False,indent=2))
    if screenshot:
        run('shell','uitest','screenCap','-p',f'/data/local/tmp/vg-spec9-{name}.png')
        run('file','recv',f'/data/local/tmp/vg-spec9-{name}.png',f'traces/baseline-analysis/{name}.png')
    return d
def click(text):
    d=dump('last-action')
    matches=[a for a in nodes(d) if a.get('text')==text and a.get('visible')=='true']
    if len(matches)!=1: raise AssertionError(f'Expected unique visible text {text!r}, got {len(matches)}')
    b=list(map(int,re.findall(r'\d+',matches[0]['bounds'])))
    print(run('shell','uitest','uiInput','click',str((b[0]+b[2])//2),str((b[1]+b[3])//2)))
if __name__=='__main__':
    if sys.argv[1]=='dump': dump(sys.argv[2], True)
    elif sys.argv[1]=='click': click(sys.argv[2])
    elif sys.argv[1]=='hdc': print(run(*sys.argv[2:]))
