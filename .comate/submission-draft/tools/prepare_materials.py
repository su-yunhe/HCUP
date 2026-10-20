"""Snapshot project bytes, generate full binary diff and verify against a local baseline clone."""
import collections
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.comate/submission-draft'
BASE=json.loads((ROOT/'spec/metadata.json').read_text())['base_commit']
EXCLUDED_PARTS={'build','oh_modules','node_modules','.hvigor','__pycache__','.git','.venv','.venv-selftest','.idea','.cxx','.clangd','.appanalyzer'}

def sha(raw): return hashlib.sha256(raw).hexdigest()
def jwrite(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args,cwd=ROOT,env=None,input=None):
    p=subprocess.run(['git',*args],cwd=cwd,env=env,input=input,capture_output=True)
    if p.returncode: raise RuntimeError(f'git {args}: {p.returncode}: {p.stderr.decode("utf-8",errors="replace")}')
    return p.stdout
def excluded(name):
    p=Path(name)
    return name.startswith('.comate/submission-draft/') or any(x in EXCLUDED_PARTS for x in p.parts) or p.name=='local.properties' or p.suffix in {'.pyc','.pyo'}

def main():
    stamp=dt.datetime.now(dt.timezone.utc).isoformat()
    (OUT/'changes').mkdir(parents=True,exist_ok=True)
    status=git('status','--porcelain=v1','-z','--untracked-files=all')
    (OUT/'changes/git-status-before.z').write_bytes(status)
    tracked=git('ls-files','-z').split(b'\0')
    names=git('ls-files','--cached','--others','--exclude-standard','-z').split(b'\0')
    decoded=sorted({x.decode('utf-8') for x in names if x})
    exclusions=[n for n in decoded if excluded(n)]
    included=[n for n in decoded if not excluded(n) and (ROOT/n).is_file()]
    manifest=[{'path':n,'bytes':(ROOT/n).stat().st_size,'sha256':sha((ROOT/n).read_bytes())} for n in included]
    aggregate=sha(json.dumps(manifest,ensure_ascii=False,separators=(',',':'),sort_keys=True).encode('utf-8'))
    jwrite(OUT/'changes/project-manifest.json',{'base_commit':BASE,'created_at':stamp,'aggregate_sha256':aggregate,
      'aggregate_method':'SHA256 of UTF8 compact sorted-key JSON files array, including raw bytes SHA256 per path',
      'files':manifest,'excluded_paths':exclusions,
      'exclude_policy':'Git ignored build/dependency/local-machine files; explicit build/oh_modules/node_modules/.hvigor/__pycache__/.git/.venv/.idea/local.properties caches; .comate/submission-draft is exported separately and MUST NOT be copied under project. Other .comate files remain included.'})
    command_log=[]
    with tempfile.TemporaryDirectory(prefix='baseline-verify-',dir=OUT) as temporary:
        temp=Path(temporary).resolve(); assert temp.is_relative_to(OUT.resolve())
        clone=temp/'baseline'
        branch=git('symbolic-ref','--short','HEAD').decode().strip()
        git('clone','--no-local','--single-branch','--no-tags','--branch',branch,'--no-checkout',str(ROOT),str(clone))
        git('-c','core.autocrlf=true','checkout','--detach',BASE,cwd=clone)
        command_log += ['git clone --no-local --single-branch --no-tags --branch '+branch+' --no-checkout <this-project> <temporary-baseline>', f'git -c core.autocrlf=true checkout --detach {BASE}']
        tree_entries={}
        for line in git('ls-tree','-r','-z',BASE,cwd=clone).split(b'\0'):
            if not line: continue
            meta,name=line.split(b'\t',1); mode,kind,oid=meta.decode().split()
            tree_entries[name.decode()]={'mode':mode,'oid':oid}
        changed=[n for n in included if not (clone/n).is_file() or (clone/n).read_bytes()!=(ROOT/n).read_bytes()]
        deleted=sorted(set(tree_entries)-set(included))
        # Hash the raw bytes, bypassing CRLF normalization for the changed/new files.
        # Unchanged baseline files stay as their original Git blobs; checkout uses the source workspace's CRLF policy.
        paths=''.join(json.dumps(str(ROOT/n),ensure_ascii=False)+'\n' for n in changed).encode('utf-8')
        oids=git('hash-object','-w','--no-filters','--stdin-paths',cwd=clone,input=paths).decode().splitlines() if changed else []
        env=os.environ.copy(); env['GIT_INDEX_FILE']=str(temp/'snapshot.index')
        git('read-tree',BASE,cwd=clone,env=env)
        index_records=b''.join((tree_entries.get(n,{}).get('mode','100644')+' '+oid+'\t'+n).encode()+b'\0' for n,oid in zip(changed,oids))
        index_records+=b''.join(('0 '+'0'*40+'\t'+n).encode()+b'\0' for n in deleted)
        if index_records: git('update-index','-z','--index-info',cwd=clone,env=env,input=index_records)
        patch=git('diff','--cached','--binary','--full-index','--no-ext-diff','--no-textconv',BASE,cwd=clone,env=env)
        diffpath=OUT/'changes/final.diff'; diffpath.write_bytes(patch)
        change_rows=[]
        for n in changed:
            change_rows.append({'path':n,'status':'M' if n in tree_entries else 'A','bytes':(ROOT/n).stat().st_size,'sha256':sha((ROOT/n).read_bytes())})
        change_rows += [{'path':n,'status':'D'} for n in deleted]
        jwrite(OUT/'changes/change-list.json',change_rows)
        git('-c','core.autocrlf=input','apply','--check','--binary',str(diffpath),cwd=clone)
        git('-c','core.autocrlf=input','apply','--binary',str(diffpath),cwd=clone)
        command_log += ['git -c core.autocrlf=input apply --check --binary <changes/final.diff>', 'git -c core.autocrlf=input apply --binary <changes/final.diff>']
        mismatches=[n for n in included if not (clone/n).is_file() or sha((clone/n).read_bytes())!=sha((ROOT/n).read_bytes())]
        expected=set(included)
        actual={p.relative_to(clone).as_posix() for p in clone.rglob('*') if p.is_file() and '.git' not in p.relative_to(clone).parts}
        extra=sorted(actual-expected);missing=sorted(expected-actual)
        binaries=[]
        for n in included:
            raw=(ROOT/n).read_bytes()
            # Match Git's binary heuristic, supplemented by undecodable UTF8 resources.
            is_binary=b'\0' in raw[:8000]
            if not is_binary:
                try: raw.decode('utf-8-sig')
                except UnicodeDecodeError: is_binary=True
            if is_binary:
                origin='new task evidence/test fixture; not production external artwork'
                baseline_oid=tree_entries.get(n,{}).get('oid')
                if baseline_oid:
                    origin='same baseline resource, unchanged' if git('show',BASE+':'+n,cwd=clone)==raw else 'baseline resource, changed bytes'
                binaries.append({'path':n,'bytes':len(raw),'sha256':sha(raw),'status':'unchanged' if n not in changed else ('modified' if baseline_oid else 'added'),'provenance':origin,'baseline_blob':baseline_oid})
        jwrite(OUT/'changes/binaries.json',binaries)
        report={'created_at':stamp,'verified_at':dt.datetime.now(dt.timezone.utc).isoformat(),'base_commit':BASE,'project_snapshot_sha256':aggregate,
          'diff_bytes':len(patch),'diff_sha256':sha(patch),'baseline_clone':'local clone of this task Git repository, then detached checkout to metadata.base_commit; no protected bundle or upstream repair read',
          'commands':command_log,'apply_check_exit_code':0,'apply_exit_code':0,
          'raw_byte_comparison_files':len(included),'raw_byte_mismatches':mismatches,'missing':missing,'extra':extra,
          'added':sum(x['status']=='A' for x in change_rows),'modified':sum(x['status']=='M' for x in change_rows),'deleted':len(deleted),
          'binary_files':len(binaries),'pass':not(mismatches or missing or extra),
          'line_endings':'Baseline checkout uses core.autocrlf=true, matching original Windows checkout; changed/new blobs are hashed with --no-filters. Apply uses core.autocrlf=input to preserve both original CRLF and LF raw bytes. SHA256 comparison is byte-for-byte, not normalized text.',
          'snapshot_excludes_draft':True}
        jwrite(OUT/'changes/validation.json',report)
        if not report['pass']: raise RuntimeError(json.dumps(report,ensure_ascii=False))
    # Preserve every source log, including failed attempts and unrelated-to-success diagnostics.
    log_manifest=[]
    for source in sorted((ROOT/'logs').rglob('*')):
        if not source.is_file(): continue
        rel=source.relative_to(ROOT/'logs'); target=OUT/'logs'/rel
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
        log_manifest.append({'path':rel.as_posix(),'bytes':source.stat().st_size,'sha256':sha(source.read_bytes())})
    jwrite(OUT/'logs-manifest.json',log_manifest)
    production=json.loads((ROOT/'workflow/implementation/source-round-02.json').read_text())['production_scope_sha256']
    for n,expected_hash in production.items():
        assert sha((ROOT/n).read_bytes())==expected_hash,n
        target=OUT/'traces/code-snapshot'/n; target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,target)
    jwrite(OUT/'traces/code-snapshot/manifest.json',{'path_base':'package_root','source':'tasks/vg-spec15/project/workflow/implementation/source-round-02.json','snapshot_files_base':'traces/vg-spec15/code-snapshot/','files':production,'complete_project':'tasks/vg-spec15/changes/project-manifest.json','full_diff':'tasks/vg-spec15/changes/final.diff'})
    common=ROOT.parent/'common'
    version_files={}
    for n in ['0-analyze.md','1-do.md','2-submit.md','3-package.md']:
        version_files[n]={'common_sha256':sha((common/'spec-harness'/n).read_bytes()),'task_copy_sha256':sha((ROOT/'spec-harness'/n).read_bytes())}
    try:
        common_head=git('-C',str(common),'rev-parse','HEAD').decode().strip()
        common_git_root=git('-C',str(common),'rev-parse','--show-toplevel').decode().strip()
    except RuntimeError: common_head=None;common_git_root=None
    jwrite(OUT/'taskbook-version.json',{'queried_at':stamp,'current_common_repository_head':common_head,'repository_root':common_git_root,'files':version_files,
      'history_present':(ROOT/'spec/history').exists(),'history_files':[p.relative_to(ROOT).as_posix() for p in (ROOT/'spec/history').rglob('*') if p.is_file()],
      'interpretation':'Current parent HCUP Git HEAD, not a proven historical run commit. Exact taskbook bytes are identified by SHA256; per-task copies retained. No spec/history directory when history_present=false.'})
    print(json.dumps({'project_files':len(manifest),'snapshot_sha256':aggregate,'diff_bytes':len(patch),'diff_sha256':sha(patch),'logs':len(log_manifest),'verification':report['pass']},ensure_ascii=False))

if __name__=='__main__': main()
