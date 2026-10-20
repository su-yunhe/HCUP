"""Prepare a byte-exact local project projection; never changes the source repo."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
BASE = json.loads((ROOT/'spec/metadata.json').read_text(encoding='utf-8-sig'))['base_commit']
MIXED = '01a13fc4-2611-7761-a580-1283e0c70541'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024), b''): h.update(b)
    return h.hexdigest()

def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def git(args, cwd=ROOT, **kw):
    return subprocess.run(['git',*args], cwd=cwd, check=True, **kw)

def exclusions(name):
    p = Path(name)
    if name.startswith('.comate/submission-draft/'): return '本次派生材料与临时校验区，置于工程外的任务材料位置，避免diff自包含递归'
    if MIXED in p.name: return '初始化总览混合会话，包含其他题；AGENTS明确不得作为本题研发证据'
    if '__pycache__' in p.parts or p.suffix in ('.pyc','.pyo'): return 'Python缓存'
    if '/emulator-instances/' in '/'+name or '/manual-instance/instances/' in '/'+name: return '模拟器运行镜像、磁盘、锁与运行缓存；命令及验证日志仍保留'
    return None

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = set(subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')) - {''}
    selected=[]; excluded=[]
    for n in sorted(names):
        p=ROOT/n
        if n.startswith('.comate/submission-draft/'): continue
        why=exclusions(n)
        if not p.is_file(): continue
        info={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
        if why: excluded.append({**info,'reason':why})
        else: selected.append(info)
    encoded=''.join(f"{x['path']}\0{x['sha256']}\n" for x in selected).encode()
    manifest={'captured_at':datetime.now(timezone.utc).isoformat(),'base_commit':BASE,
      'version':'sha256:'+hashlib.sha256(encoded).hexdigest(), 'files':selected,
      'exclusions':excluded,'excluded_generated_prefix':'.comate/submission-draft/',
      'selection':'git cached + untracked --exclude-standard; excludes only derived draft, Python cache, emulator runtime, mixed initialization native logs',
      'package_rule':'3-package must copy exactly files in this manifest into tasks/vg-spec1/project; never recursively copy submission-draft. Other .comate files, if present, are included.',
      'formal_freeze_time':'【待补充】'}
    write(OUT/'changes/project-manifest.json',manifest)
    write(OUT/'audit/excluded-files.json',{'files':excluded,'generated_prefix':'.comate/submission-draft/'})
    git(['status','--porcelain=v1','--untracked-files=all'],stdout=(OUT/'audit/git-status-before.txt').open('wb'))
    (OUT/'audit').mkdir(exist_ok=True)
    tmp=OUT/'validation/project'
    if tmp.exists(): raise RuntimeError('Validation checkout already exists; preserve prior evidence and use a new output directory')
    git(['clone','--no-hardlinks','--no-checkout',str(ROOT),str(tmp)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    git(['config','core.autocrlf','false'],cwd=tmp)
    (tmp/'.git/info/attributes').write_text('* -text\n',encoding='utf-8')
    git(['checkout','--detach',BASE],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    base_names=set(subprocess.check_output(['git','ls-files','-z'],cwd=tmp).decode().split('\0'))-{''}
    chosen={x['path'] for x in selected}
    for n in base_names-chosen:
        p=tmp/n
        if p.is_file(): p.unlink()
    for x in selected:
        src=ROOT/x['path']; dst=tmp/x['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    git(['add','--all','--force'],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    patch=OUT/'changes/final.diff'
    with patch.open('wb') as f:
        git(['-c','core.quotePath=false','diff','--cached','--binary','--full-index',BASE,'--'],cwd=tmp,stdout=f,stderr=subprocess.PIPE)
    # Binary detection is based on content, not extension. Also include unchanged baseline assets.
    binary=[]
    for x in selected:
        p=ROOT/x['path']
        with p.open('rb') as f: first=f.read(8192)
        if b'\0' not in first: continue
        obj=subprocess.run(['git','rev-parse',BASE+':'+x['path']],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        same=False
        if obj.returncode==0:
            raw=subprocess.check_output(['git','cat-file','blob',obj.stdout.decode().strip()],cwd=ROOT)
            same=hashlib.sha256(raw).hexdigest()==x['sha256']
        binary.append({**x,'baseline_same':same,'provenance':'随包基线同源，字节一致' if same else '本题新增测试/记录二进制；用途及人工额外来源声明见sources.fragment.md'})
    write(OUT/'changes/binary-files.json',{'files':binary})
    lines=['# 二进制文件清单','', '| 工程内路径 | 字节 | SHA-256 | 基线同源 |','| --- | ---: | --- | --- |']
    lines += [f"| `{x['path']}` | {x['bytes']} | `{x['sha256']}` | {'是，字节一致' if x['baseline_same'] else '否，新增记录/测试产物'} |" for x in binary]
    (OUT/'changes/binary-files.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    # Return the disposable clone to the exact baseline, then apply the delivered patch.
    git(['reset','--hard',BASE],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    git(['clean','-fdx'],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    checks=[]
    for args in [['apply','--check','--binary',str(patch)],['apply','--binary',str(patch)]]:
        p=subprocess.run(['git',*args],cwd=tmp,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        checks.append({'command':['git',*args[:-1],'changes/final.diff'],'exit_code':p.returncode,'stdout':p.stdout.decode(errors='replace'),'stderr':p.stderr.decode(errors='replace')})
        if p.returncode: write(OUT/'audit/diff-validation.json',{'checks':checks,'pass':False}); raise RuntimeError('Patch failed')
    mismatch=[]
    for x in selected:
        p=tmp/x['path']
        if not p.is_file() or sha(p)!=x['sha256']: mismatch.append(x['path'])
    extra=[p.relative_to(tmp).as_posix() for p in tmp.rglob('*') if p.is_file() and '.git' not in p.relative_to(tmp).parts and p.relative_to(tmp).as_posix() not in chosen]
    changed_source=[x['path'] for x in selected if sha(ROOT/x['path'])!=x['sha256']]
    report={'base_commit':BASE,'snapshot_version':manifest['version'],'clone_method':'git clone --no-hardlinks --no-checkout 本题工程 临时副本; git checkout --detach base_commit',
       'byte_preservation':'temporary clone .git/info/attributes * -text; core.autocrlf=false; source repository/index untouched',
       'checks':checks,'compared_files':len(selected),'mismatches':mismatch,'extra_files':extra,'source_changed_during_collection':changed_source,
       'patch_bytes':patch.stat().st_size,'patch_sha256':sha(patch),'pass':not(mismatch or extra or changed_source),
       'scope_note':'完整性针对project-manifest.json中的交付工程投影；不是未经筛选的本地全目录。3-package必须使用同一清单。'}
    write(OUT/'audit/diff-validation.json',report)
    # Logs are copied byte-exactly except the runtime exclusions above.
    copied=[]
    for x in selected:
        if not x['path'].startswith('logs/'): continue
        dst=OUT/x['path'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/x['path'],dst)
        copied.append({'path':x['path'],'sha256':sha(dst),'bytes':dst.stat().st_size})
    write(OUT/'audit/log-copy-manifest.json',{'files':copied,'all_match':all(x['sha256']==next(y['sha256'] for y in selected if y['path']==x['path']) for x in copied),'excluded_runtime': [x for x in excluded if x['path'].startswith('logs/')]})
    print(json.dumps({k:report[k] for k in ['pass','compared_files','patch_bytes','patch_sha256','mismatches','extra_files']},ensure_ascii=False))

if __name__=='__main__':main()
