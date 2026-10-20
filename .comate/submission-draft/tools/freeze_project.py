"""Freeze the exact packaging project and prove its full binary patch reconstructs it."""
from pathlib import Path
from datetime import datetime, timezone
import collections, hashlib, json, os, shutil, subprocess, sys
from collect_evidence import ROOT, OUT, sha, write

SKIP_DIRS={'.git','build','oh_modules','node_modules','.hvigor','__pycache__','.idea','.cxx','.test','.appanalyzer'}
SKIP_FILES={'local.properties','BuildProfile.ets'}
MIXED='traces/native/20261020T031347Z-6162c371'
RUNTIME_LOGS='traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/Log/'
SNAP=OUT/'traces/code-snapshot/project'
WORK=OUT/'.validation'
COMMANDS=[]
RUN_STAMP=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def run(args,cwd=ROOT,output=None):
    start=datetime.now(timezone.utc).isoformat()
    if output:
        with Path(output).open('wb') as f:p=subprocess.run(args,cwd=cwd,stdout=f,stderr=subprocess.PIPE)
        stdout='[written to '+Path(output).relative_to(OUT).as_posix()+']'
    else:
        p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE);stdout=p.stdout.decode('utf-8',errors='replace')
    row={'argv':args,'cwd':str(cwd),'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),
         'exit_code':p.returncode,'stdout':stdout,'stderr':p.stderr.decode('utf-8',errors='replace')}
    COMMANDS.append(row)
    write('validation/patch-commands.json',COMMANDS)
    write('validation/patch-command-history/'+RUN_STAMP+'.json',COMMANDS)
    if p.returncode:raise RuntimeError(str(row))
    return stdout

def scan():
    files={};excluded=[]
    for parent,dirs,names in os.walk(ROOT):
        current=Path(parent);rel=current.relative_to(ROOT).as_posix()
        for name in list(dirs):
            p=current/name;rp=p.relative_to(ROOT).as_posix()
            reason=None
            if name in SKIP_DIRS:reason='Git internals, generated output, dependency or local tool cache'
            if rp=='.comate/submission-draft':reason='Submission staging and patch itself; prevents self inclusion; packaged separately'
            if rp==MIXED:reason='Initialization overview contains other-task context; forbidden task evidence'
            if p.is_symlink():reason='Symlink not followed'
            if reason:dirs.remove(name);excluded.append({'path':rp+'/','reason':reason})
        for name in names:
            p=current/name;rp=p.relative_to(ROOT).as_posix()
            reason=None
            if name=='.git':reason='Git worktree pointer'
            elif name in SKIP_FILES:reason='Machine-local configuration or generated BuildProfile'
            elif name.endswith(('.pyc','.pyo','.img','.qcow2')):reason='Compiled Python or emulator disk cache, not development log'
            elif p.is_symlink():reason='Symlink not followed'
            if reason:excluded.append({'path':rp,'reason':reason});continue
            files[rp]={'bytes':p.stat().st_size,'sha256':sha(p)}
    return files,excluded

def main():
    base=json.loads((ROOT/'spec/metadata.json').read_text('utf-8'))['base_commit']
    files,excluded=scan();SNAP.mkdir(parents=True,exist_ok=True)
    old={p.relative_to(SNAP).as_posix():p for p in SNAP.rglob('*') if p.is_file()}
    for rel,p in old.items():
        if rel not in files:p.unlink()
    runtime_captures=[]
    for rel,v in files.items():
        p=SNAP/rel
        capture_started=datetime.now(timezone.utc).isoformat() if rel.startswith(RUNTIME_LOGS) else None
        if rel.startswith(RUNTIME_LOGS) or not p.exists() or sha(p)!=v['sha256']:
            p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,p)
        if rel.startswith(RUNTIME_LOGS):
            # A running emulator can append/rotate logs; the copied bytes are the captured evidence.
            files[rel]={'bytes':p.stat().st_size,'sha256':sha(p)}
            source=ROOT/rel
            runtime_captures.append({'path':rel,'capture_started_utc':capture_started,'capture_finished_utc':datetime.now(timezone.utc).isoformat(),
                'source_scan_before':v,'captured':files[rel],
                'source_after_copy':{'bytes':source.stat().st_size,'sha256':sha(source)} if source.exists() else None})
    aggregate=hashlib.sha256(json.dumps({k:v['sha256'] for k,v in files.items()},ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    manifest={'task_id':'cml-spec1','captured_at_utc':datetime.now(timezone.utc).isoformat(),'base_commit':base,
      'head':run(['git','rev-parse','HEAD']).strip(),'snapshot':'traces/code-snapshot/project',
      'snapshot_aggregate_sha256':aggregate,'aggregate_algorithm':'SHA256(JSON sorted path to SHA256 map, ensure_ascii=False, compact separators)',
      'file_count':len(files),'bytes':sum(v['bytes'] for v in files.values()),'files':files,'excluded':excluded,
      'runtime_capture_policy':'Emulator Log/ files are copied as-of this capture. Their copied hashes are authoritative; subsequent live writes/rotation are reported separately, not treated as changes to frozen evidence.',
      'runtime_log_captures':runtime_captures,
      'packaging_contract':'3-package must copy this exact project snapshot to tasks/cml-spec1/project, not recursively copy the live worktree or staging directory.'}
    write('traces/code-snapshot/manifest.json',manifest)
    WORK.mkdir(parents=True,exist_ok=True)
    clone=WORK/'patch-source-scoped'
    if not (clone/'.git').exists():
        run(['git','clone','--no-local','--no-hardlinks','--no-checkout','--single-branch','--branch','cml-spec1',str(ROOT),str(clone)])
    run(['git','config','core.autocrlf','false'],clone)
    run(['git','config','core.safecrlf','false'],clone)
    run(['git','-c','core.autocrlf=false','checkout','--detach',base],clone)
    # This is our isolated disposable clone only. The shared source worktree is never reset.
    for parent,dirs,names in os.walk(clone):
        if '.git' in dirs:dirs.remove('.git')
        for name in names:
            p=Path(parent)/name
            if p.relative_to(clone).as_posix() not in files:p.unlink()
    for rel,v in files.items():
        p=clone/rel
        if not p.exists() or sha(p)!=v['sha256']:
            p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SNAP/rel,p)
    run(['git','-c','core.autocrlf=false','-c','core.safecrlf=false','add','--force','--all','.'],clone)
    (OUT/'changes').mkdir(exist_ok=True)
    run(['git','-c','core.autocrlf=false','diff','--cached','--binary','--full-index','--no-ext-diff','--no-renames',base,'--'],clone,OUT/'changes/final.diff')
    tree=run(['git','write-tree'],clone).strip()
    # A separate pristine local clone checks AND applies the patch, then every byte is compared.
    check=WORK/'patch-apply-scoped'
    if not (check/'.git').exists():run(['git','clone','--no-local','--no-hardlinks','--no-checkout','--single-branch','--branch','cml-spec1',str(ROOT),str(check)])
    run(['git','config','core.autocrlf','false'],check)
    run(['git','config','core.safecrlf','false'],check)
    run(['git','-c','core.autocrlf=false','checkout','--force','--detach',base],check)
    # Clear only files from a previous successful application, verified inside this named clone.
    if not check.resolve().is_relative_to(WORK.resolve()) or check.name!='patch-apply-scoped':raise RuntimeError('unsafe disposable clone path')
    run(['git','clean','-fdx'],check)
    patch=str(OUT/'changes/final.diff')
    run(['git','-c','core.autocrlf=false','apply','--check','--binary',patch],check)
    run(['git','-c','core.autocrlf=false','apply','--binary',patch],check)
    actual={}
    for parent,dirs,names in os.walk(check):
        if '.git' in dirs:dirs.remove('.git')
        for name in names:
            p=Path(parent)/name;actual[p.relative_to(check).as_posix()]=sha(p)
    expected={k:v['sha256'] for k,v in files.items()}
    mismatches=sorted(k for k in actual.keys()|expected.keys() if actual.get(k)!=expected.get(k))
    live_files,_=scan()
    live_changes=sorted(k for k in live_files.keys()|files.keys() if live_files.get(k)!=files.get(k))
    runtime_changes=[k for k in live_changes if k.startswith(RUNTIME_LOGS)]
    original_mismatches=[k for k in live_changes if not k.startswith(RUNTIME_LOGS)]
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'base_commit':base,'snapshot_aggregate_sha256':aggregate,
       'final_git_tree':tree,'patch_bytes':(OUT/'changes/final.diff').stat().st_size,'patch_sha256':sha(OUT/'changes/final.diff'),
       'git_apply_check_exit_code':0,'git_apply_exit_code':0,'files_compared':len(expected),'reconstruction_mismatches':mismatches,
       'live_project_mismatches':original_mismatches,'pass':not mismatches and not original_mismatches}
    result['live_runtime_log_changes_after_capture']=runtime_changes
    result['live_runtime_log_change_details']=[{'path':k,'captured':files.get(k),'live_after_validation':live_files.get(k)} for k in runtime_changes]
    result['runtime_log_capture_policy']=manifest['runtime_capture_policy']
    write('validation/patch-validation.json',result)
    # Binary inventory includes all delivered non-text evidence/resources, not only business assets.
    inventory=[]
    with (OUT/'changes/binary-files.csv').open('w',encoding='utf-8-sig',newline='') as f:
        import csv
        writer=csv.writer(f);writer.writerow(['path','bytes','sha256','scope','baseline_same_path_same_bytes'])
        for rel,v in files.items():
            import codecs
            decoder=codecs.getincrementaldecoder('utf-8')();binary=False
            with (SNAP/rel).open('rb') as src:
                try:
                    for b in iter(lambda:src.read(65536),b''):
                        if b'\x00' in b:binary=True;break
                        decoder.decode(b)
                    if not binary:decoder.decode(b'',final=True)
                except UnicodeDecodeError:binary=True
            if not binary:continue
            production=rel.startswith(('AppScope/','core/','feature/','entry/'))
            same='not_a_baseline_production_resource'
            if production:
                blob=subprocess.run(['git','show',base+':'+rel],cwd=ROOT,capture_output=True)
                same=str(blob.returncode==0 and hashlib.sha256(blob.stdout).hexdigest()==v['sha256']).lower()
            writer.writerow([rel,v['bytes'],v['sha256'],'production_resource' if production else 'task_evidence',same])
    print(json.dumps(result,ensure_ascii=False),flush=True)
    if not result['pass']:raise SystemExit(2)

if __name__=='__main__':main()
