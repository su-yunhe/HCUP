from pathlib import Path,PurePosixPath
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
import datetime,hashlib,json,os,shutil,sqlite3,subprocess

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while data:=f.read(2**20):h.update(data)
    return h.hexdigest()
def save(name,v):(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
result=read(ROOT/'.comate/submission-draft/validation/patch-01/result.json')
run=ROOT/result['run_directory'];canonical=ROOT/result['reconstructed_project']
manifest_path=ROOT/result['project_manifest']['path'];manifest=read(manifest_path)
rows=manifest['files'];assert len(rows)==10029 and len({row['path'] for row in rows})==10029
for row in rows:
    p=PurePosixPath(row['path'])
    assert not p.is_absolute() and '..' not in p.parts and '\\' not in row['path']
    assert not row['path'].startswith('.comate/submission-draft/validation/')
    assert '01a13fc4-2611-7761-a580-1283e0c70541' not in row['path']
aggregate=hashlib.sha256(''.join(row['path']+'\0'+row['sha256']+'\n' for row in sorted(rows,key=lambda r:r['path'])).encode()).hexdigest()
assert aggregate==manifest['aggregate_sha256']
assert sha(manifest_path)==result['project_manifest']['sha256']=='5ae3a07bf9a438352996379e8e84ff0375bad7186673059d1daa6d08f85d7405'
assert sha(run/'project-files.frozen.json')==sha(manifest_path)
patch=ROOT/result['patch']['path']
assert patch.stat().st_size==767891670 and sha(patch)==result['patch']['sha256']=='37e5b0a0bdf8e4885cd93f5ddeffd89ea220ab2f911b34057273d5bd1be0955f'
assert sha(run/'final.diff')==sha(patch)
print('manifest and two patch copies hash match',flush=True)
def check(row):
    output={'path':row['path'],'expected_sha256':row['sha256'],'expected_bytes':row['bytes']}
    for label,base in [('original',ROOT),('canonical',canonical)]:
        p=base/row['path'];assert p.resolve().is_relative_to(base.resolve()) and p.is_file() and not p.is_symlink()
        output[label]={'bytes':p.stat().st_size,'sha256':sha(p)}
    output['pass']=all(v['bytes']==row['bytes'] and v['sha256']==row['sha256'] for v in [output['original'],output['canonical']])
    return output
with ThreadPoolExecutor(max_workers=6) as pool:comparison=list(pool.map(check,rows))
actual=[]
for base,dirs,files in os.walk(canonical,followlinks=False):
    dirs[:]=[d for d in dirs if d!='.git']
    actual.extend((Path(base)/name).relative_to(canonical).as_posix() for name in files)
expected={row['path'] for row in rows}
parity={'expected_count':len(rows),'actual_count':len(actual),'missing':sorted(expected-set(actual)),'extra':sorted(set(actual)-expected),'mismatches':[x for x in comparison if not x['pass']],'per_file':comparison}
assert not parity['missing'] and not parity['extra'] and not parity['mismatches']
save('byte-parity.json',parity)
print('all10029 source+canonical files independently hash/size match; no extras',flush=True)
commands=[]
for command in result['commands']:
    assert command['exit_code']==0
    for stream in ['stdout','stderr']:
        p=ROOT/command[stream]
        assert sha(p)==command[stream+'_sha256'] and p.stat().st_size==command[stream+'_bytes']
    commands.append({'sequence':command['sequence'],'phase':command['phase'],'argv':command['argv'],'exit_code':0,'raw_outputs_hash_match':True})
assert len(commands)==30
assert any('apply' in c['argv'] and '--check' in c['argv'] and '--binary' in c['argv'] for c in commands)
assert any('apply' in c['argv'] and '--check' not in c['argv'] and '--binary' in c['argv'] for c in commands)
assert any('diff' in c['argv'] and '--binary' in c['argv'] and '--full-index' in c['argv'] for c in commands)
save('git-command-evidence.json',commands)
env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}
def git(cwd,args):
    argv=['git','-c','core.fsmonitor=false','-c','core.hooksPath='+str(run/'empty-hooks'),*args]
    p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=60)
    assert p.returncode==0
    return p.stdout
clones=[];known={'9a1d608dc89acfc301657c33ce5dd6089cbf9572','b75aa21fdb29af1d3d00aa313360da85c6e05e4f'}
for clone in [run/'generator-project',canonical]:
    commits=set(git(clone,['rev-list','--all']).decode().splitlines())
    refs=git(clone,['for-each-ref','--format=%(refname)%00%(objectname)']).decode().splitlines()
    assert commits==known and all(line.split('\0')[1] in known for line in refs)
    assert git(clone,['rev-parse','HEAD']).decode().strip()=='9a1d608dc89acfc301657c33ce5dd6089cbf9572'
    clones.append({'path':clone.relative_to(ROOT).as_posix(),'reachable_commits':sorted(commits),'refs':refs,'HEAD':next(c for c in known if c.startswith('9a1d'))})
original={'HEAD':git(ROOT,['rev-parse','HEAD']).decode().strip(),'branch':git(ROOT,['symbolic-ref','--short','HEAD']).decode().strip(),'staged_logical_sha256':hashlib.sha256(git(ROOT,['ls-files','--stage','-z'])).hexdigest()}
assert original['HEAD']==result['original_repository_before']['HEAD']==result['original_repository_after']['HEAD']
assert original['staged_logical_sha256']==result['original_repository_before']['staged_logical_content_sha256']==result['original_repository_after']['staged_logical_content_sha256']
save('repository-guards.json',{'clones':clones,'original':original,'index_scope':'logical staged ls-files output only, not physical index bytes'})
binary=read(ROOT/result['binary_manifest']['path']);print('binary keys',list(binary),flush=True)
binary_rows=binary.get('files',binary.get('entries',[]));assert len(binary_rows)==669
for row in binary_rows:
    expected_row=next(x for x in rows if x['path']==row['path'])
    assert row['sha256']==expected_row['sha256'] and row.get('bytes',row.get('size'))==expected_row['bytes']
save('binary-summary.json',{'count':669,'all_in_manifest_and_byte_checked':True,'sha256':sha(ROOT/result['binary_manifest']['path'])})
assert sha(ROOT/result['binary_manifest']['path'])==result['binary_manifest']['sha256']
audits=result['sqlite_audits'];assert len(audits)==91
dbresults=[];rowmap={x['path']:x for x in rows};nonempty=[]
for index,audit in enumerate(audits,1):
    assert audit['integrity_ok'] and audit['integrity_check_rows']==[['ok']]
    copied=audit['copied_files'];assert all(x['stable_and_equal'] and x['expected_sha256']==x['copy_sha256']==x['original_postcopy_sha256'] and x['original_mtime_ns_before']==x['original_mtime_ns_after'] for x in copied)
    files=[audit['source_db']]+([audit['source_wal']] if audit['source_wal'] else [])
    target=OUT/'sqlite-audit'/f'{index:03d}';target.mkdir(parents=True)
    before=[]
    for rel in files:
        src=canonical/rel;original=ROOT/rel;expected_row=rowmap[rel]
        assert sha(src)==expected_row['sha256']==sha(original)
        before.append((rel,sha(src),src.stat().st_mtime_ns,original.stat().st_mtime_ns))
        shutil.copy2(src,target/src.name)
    connection=sqlite3.connect(target/Path(audit['source_db']).name)
    try:
        mode=connection.execute('PRAGMA journal_mode').fetchall();integrity=connection.execute('PRAGMA integrity_check').fetchall()
        tables=connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
        counts={name:connection.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0] for (name,) in tables}
    finally:connection.close()
    assert integrity==[('ok',)]
    for rel,h,mtime,original_mtime in before:
        assert sha(canonical/rel)==h==sha(ROOT/rel)
        assert (canonical/rel).stat().st_mtime_ns==mtime and (ROOT/rel).stat().st_mtime_ns==original_mtime
    if audit['source_wal']:nonempty.append(audit['source_wal'])
    dbresults.append({'source_db':audit['source_db'],'source_wal':audit['source_wal'],'audit_copy':target.relative_to(ROOT).as_posix(),'integrity':integrity,'journal_mode':mode,'table_counts':counts,'source_canonical_hash_mtime_unchanged':True,'sqlite_version':sqlite3.sqlite_version})
assert len(nonempty)==5
save('sqlite-independent.json',{'count':91,'all_integrity_ok':True,'nonempty_wal_count':5,'nonempty_wal_paths':nonempty,'audits':dbresults,'method':'Opened only independently copied validation audit DB/WAL pairs; originals and canonical never connected'})
formal=read(ROOT/'workflow/implementation/development-frozen-fingerprint-10.json')
assert len(formal['files'])==827 and all(sha(ROOT/x['path'])==x['sha256'] for x in formal['files'])
assert sha(ROOT/'entry/build/default/outputs/default/entry-default-unsigned.hap')=='51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229'
assert sha(ROOT/'hypium_tests/test_address_workflow.py')=='7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f'
excluded=read(ROOT/result['excluded_manifest']['path']);init=[x for x in excluded['candidate_exclusions'] if 'filename-only' in x['reason']]
assert len(init)==2 and all(x['path'] not in expected and not (canonical/x['path']).exists() for x in init)
assert all(x in expected and x[:-4] in expected for x in nonempty)
summary={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'thread_id':'01a14f55-5f14-7860-976f-10407965f444','manifest_count':10029,'manifest_sha256':sha(manifest_path),'patch_sha256':sha(patch),'patch_bytes':patch.stat().st_size,'all_source_canonical_hashes_match':True,'command_logs_verified':30,'clones_only_approved_two_commits':True,'binary_count':669,'SQLite_independent_integrity_ok':91,'stable_nonempty_WAL_pairs':5,'filename_only_init_raw_excluded':2,'business827_HAP_original_test_protected':True,'HEAD_staged_logical_unchanged':True,'remaining':'Final prose/pending-fields/links/native exports check plus Root post-review5 session export still pending.'}
save('technical-summary.json',summary);print(json.dumps(summary),flush=True)
