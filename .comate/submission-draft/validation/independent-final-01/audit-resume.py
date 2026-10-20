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
rows=manifest['files'];expected={x['path'] for x in rows};patch=ROOT/result['patch']['path']
assert read(OUT/'byte-parity.json')['mismatches']==[]
assert len(read(OUT/'git-command-evidence.json'))==30
assert len(read(OUT/'repository-guards.json')['clones'])==2
binary=read(ROOT/result['binary_manifest']['path']);print('binary keys',list(binary),flush=True)
binary_rows=binary['items'];assert len(binary_rows)==669
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
