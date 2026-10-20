"""Freeze exactly the declared project tree and prove its complete binary patch."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_evidence import ROOT, OUT, cache_reason, digest, write

def run(args, cwd=ROOT, output=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    record = {'command': args, 'cwd': str(cwd), 'exit_code': result.returncode,
              'stdout': result.stdout.decode('utf-8', errors='replace') if output is None else 'Written to ' + str(output.relative_to(OUT)),
              'stderr': result.stderr.decode('utf-8', errors='replace')}
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(result.stdout)
    COMMANDS.append(record)
    if result.returncode:
        write(OUT / 'patch-validation-failure.json', COMMANDS)
        raise RuntimeError(record)
    return result.stdout

COMMANDS = []

def main():
    base = json.loads((ROOT/'spec/metadata.json').read_text(encoding='utf-8'))['base_commit']
    branch = run(['git', 'branch', '--show-current']).decode().strip()
    head = run(['git', 'rev-parse', 'HEAD']).decode().strip()
    if head != base:
        raise RuntimeError('This snapshot helper expects the verified task branch at its official base; review newer history first.')
    selected = set(run(['git','ls-files','-z']).decode().strip('\0').split('\0'))
    selected.update(run(['git','ls-files','--others','--exclude-standard','-z']).decode().strip('\0').split('\0'))
    # AGENTS.md is intentionally ignored in Git, but is task process evidence.
    selected.add('AGENTS.md')
    selected.discard('')
    omitted = []
    for name in sorted(selected.copy()):
        p = ROOT / name
        reason = cache_reason(name)
        if name.startswith('.comate/submission-draft/'):
            reason = 'submission material derivative, excluded from project to prevent self-referential diff'
        if 'tmp_hypium/' in name or '/__pycache__/' in name:
            reason = 'temporary test runtime or Python bytecode cache'
        if reason:
            selected.remove(name)
            # Large generated draft files are enumerated without hashing to avoid quadratic self-digests.
            if not name.startswith('.comate/submission-draft/'):
                omitted.append({'path': name, 'reason': reason, 'bytes': p.stat().st_size if p.is_file() else None})
    work = OUT / '.validation-work'
    if work.exists():
        raise RuntimeError('Validation work exists; preserve or explicitly clear the previous generated-only directory before a new freeze.')
    work.mkdir()
    stage = work / 'stage'
    run(['git','clone','--no-checkout','--single-branch','--no-tags','--branch',branch,'--no-local',str(ROOT),str(stage)])
    run(['git','config','core.autocrlf','false'], cwd=stage)
    run(['git','config','core.safecrlf','false'], cwd=stage)
    run(['git','checkout','--detach',base], cwd=stage)
    # New clone only; no original index, branch, source or Git config is changed.
    base_names = set(run(['git','ls-files','-z'],cwd=stage).decode().strip('\0').split('\0'))
    source_rows = []
    snapshot = OUT / 'traces/code-snapshot/project'
    if snapshot.exists():
        raise RuntimeError('Snapshot already exists; do not overlay a prior freeze.')
    snapshot.mkdir(parents=True)
    for name in sorted(selected):
        p = ROOT / name
        if not p.is_file():
            # A tracked deletion is represented by removal from the baseline clone.
            if (stage/name).is_file():
                (stage/name).unlink()
            continue
        if p.is_symlink():
            raise RuntimeError('Review symlink before packaging: ' + name)
        for target in [stage/name, snapshot/name]:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(p,target)
        source_rows.append({'path':name,'bytes':p.stat().st_size,'sha256':digest(p)})
    # All tracked deleted files, including directories absent from the final source selection.
    current_paths = {x['path'] for x in source_rows}
    for name in base_names - current_paths:
        if (stage/name).is_file():
            (stage/name).unlink()
    run(['git','-c','core.autocrlf=false','add','--all','--force','.'],cwd=stage)
    diff = OUT / 'changes/final.diff'
    run(['git','-c','core.autocrlf=false','diff','--cached','--binary','--full-index','--no-renames',base,'--'],cwd=stage,output=diff)
    change_raw = run(['git','diff','--cached','--name-status','-z','--no-renames',base,'--'],cwd=stage).decode().strip('\0').split('\0')
    changes = [{'status':change_raw[i], 'path':change_raw[i+1]} for i in range(0,len(change_raw),2)]
    # Original Windows checkout used CRLF; preserve bytes without changing business files.
    # Classify those mechanical differences exactly, rather than calling them business edits.
    existing = [x['path'] for x in changes if x['status']=='M' and x['path'] in base_names]
    batch = subprocess.run(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(base+':'+name+'\n' for name in existing).encode('utf-8'),capture_output=True,check=True).stdout
    offset=0
    eol_only=[]
    for name in existing:
        end=batch.index(b'\n',offset)
        header=batch[offset:end].decode('ascii').split()
        length=int(header[2]); offset=end+1
        old=batch[offset:offset+length]; offset+=length+1
        new=(snapshot/name).read_bytes()
        if old!=new and old.replace(b'\r\n',b'\n')==new.replace(b'\r\n',b'\n'):
            eol_only.append({'path':name,'base_crlf_count':old.count(b'\r\n'),'snapshot_crlf_count':new.count(b'\r\n'),
                             'normalized_sha256':hashlib.sha256(new.replace(b'\r\n',b'\n')).hexdigest()})
    eol_paths={x['path'] for x in eol_only}
    for row in changes:
        row['line_endings_only']=row['path'] in eol_paths
    write(OUT/'changes/line-ending-only.json',{'files':eol_only,'reason':'Byte-preserving export of existing CRLF Windows checkout against LF Git baseline. Application files were not normalized or edited by the materials stage.'})
    tree_id = run(['git','write-tree'],cwd=stage).decode().strip()
    manifest_bytes = json.dumps(source_rows,sort_keys=True,separators=(',',':')).encode('utf-8')
    version = 'sha256:' + hashlib.sha256(manifest_bytes).hexdigest()
    write(OUT/'project-manifest.json',{'base_commit':base,'current_git_head':head,'final_version':version,
          'snapshot_git_tree':tree_id,'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
          'files':source_rows,'scope':'All tracked plus nonignored task files and AGENTS.md, minus listed runtime caches and .comate/submission-draft/ derivatives.',
          'snapshot':'traces/code-snapshot/project','not_team_freeze_time':True})
    write(OUT/'changes/changed-files.json',changes)
    write(OUT/'project-exclusions.json',{'excluded_files':omitted,
          'excluded_derivative_prefix':'.comate/submission-draft/',
          'git_ignored_runtime_exclusions':['**/build/','**/oh_modules/','**/.hvigor/','tmp_hypium/','**/__pycache__/'],
          'packaging_contract':'Stage3 must copy traces/code-snapshot/project/ as tasks/cml-spec7/project/, not recursively copy the live task root. Put the draft artifacts beside project/. Refresh freeze/patch if expanding project scope.',
          'original_files_deleted':False})
    binaries = []
    assets = []
    changed_paths = {x['path'] for x in changes}
    for row in source_rows:
        p = snapshot/row['path']
        with p.open('rb') as f:
            prefix=f.read(8192)
        binary = b'\0' in prefix or p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.webp','.ico','.hap','.db','.sqlite'}
        is_asset = '/resources/' in row['path'] or row['path'].startswith('docs/img/')
        if not binary and not (is_asset and row['path'] in changed_paths):
            continue
        old = subprocess.run(['git','show',base+':'+row['path']],cwd=ROOT,capture_output=True)
        lineage = 'same path and identical bytes in official supplied baseline' if old.returncode==0 and hashlib.sha256(old.stdout).hexdigest()==row['sha256'] else 'new or changed; see sources.fragment.md and original AI/tool traces'
        item = {**row,'binary':binary,'changed':row['path'] in changed_paths,'baseline_lineage':lineage}
        if p.name in {'ic_login_wechat.svg','ic_login_qq.svg','ic_login_alipay.svg'}:
            origin='core/ui/src/main/resources/base/media/'+p.name.replace('ic_login_','ic_')
            origin_bytes=subprocess.run(['git','show',base+':'+origin],cwd=ROOT,capture_output=True)
            current=p.read_bytes()
            if origin_bytes.returncode==0 and origin_bytes.stdout.replace(b'\r\n',b'\n')==current.replace(b'\r\n',b'\n'):
                item.update(baseline_lineage='copied from supplied baseline resource; content identical after CRLF/LF normalization',
                            baseline_source_path=origin,baseline_source_sha256=hashlib.sha256(origin_bytes.stdout).hexdigest(),
                            normalized_sha256=hashlib.sha256(current.replace(b'\r\n',b'\n')).hexdigest())
            else:
                raise RuntimeError('Claimed baseline resource copy does not match: '+row['path'])
        if binary:
            binaries.append(item)
        if is_asset:
            assets.append(item)
    write(OUT/'changes/binary-files.json',binaries)
    write(OUT/'changes/resource-files.json',assets)
    # An independent baseline clone receives only the complete generated patch.
    check = work/'apply-check'
    run(['git','clone','--no-checkout','--single-branch','--no-tags','--branch',branch,'--no-local',str(ROOT),str(check)])
    run(['git','config','core.autocrlf','false'],cwd=check)
    run(['git','checkout','--detach',base],cwd=check)
    run(['git','apply','--check','--binary',str(diff)],cwd=check)
    run(['git','apply','--binary',str(diff)],cwd=check)
    mismatches=[]
    for row in source_rows:
        p=check/row['path']
        if not p.is_file() or digest(p)!=row['sha256']:
            mismatches.append(row['path'])
    applied={p.relative_to(check).as_posix() for p in check.rglob('*') if p.is_file() and '.git' not in p.relative_to(check).parts}
    extras=sorted(applied-current_paths)
    production=json.loads((OUT/'production-before.json').read_text(encoding='utf-8'))
    drift=[x['path'] for x in production['files'] if (digest(ROOT/x['path']) if (ROOT/x['path']).is_file() else None)!=x['sha256']]
    tracked_noise=[x for x in changes if Path(x['path']).name=='BuildProfile.ets' and not x['path'].startswith(('logs/','traces/'))]
    result={'passed':not mismatches and not extras and not drift and not tracked_noise,
            'base_commit':base,'final_version':version,'snapshot_git_tree':tree_id,
            'patch_bytes':diff.stat().st_size,'patch_sha256':digest(diff),
            'file_count':len(source_rows),'change_count':len(changes),'binary_files':len(binaries),
            'apply_check_exit_code':0,'apply_exit_code':0,'all_files_compared':len(source_rows),
            'mismatches':mismatches,'unexpected_files':extras,'production_drift':drift,
            'tracked_build_noise':tracked_noise,'commands':COMMANDS,
            'comparison_note':'Every selected file compared by SHA-256 after independent baseline clone + git apply. Original working tree untouched.'}
    write(OUT/'patch-validation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='commands'},ensure_ascii=False))
    if not result['passed']:
        raise SystemExit(2)

if __name__=='__main__':
    main()
