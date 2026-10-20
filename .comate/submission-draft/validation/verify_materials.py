"""Independent, read-only cml-spec7 materials audit. Writes only beside this script."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parents[1]
RESULTS, COMMANDS, INPUTS = [], [], {}

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read(rel):
    p = OUT / rel
    INPUTS[rel] = sha(p)
    return json.loads(p.read_text(encoding='utf-8'))

def text(rel):
    p = OUT / rel
    INPUTS[rel] = sha(p)
    return p.read_text(encoding='utf-8')

def emit(name, status, evidence, **details):
    RESULTS.append(dict(check=name, status=status, evidence=evidence, **details))

def check(name, ok, evidence, **details):
    emit(name, 'pass' if ok else 'fail', evidence, **details)

def group(name, fn):
    try:
        fn()
    except FileNotFoundError as err:
        emit(name, 'not_run', 'Pending material file', missing=str(err.filename))
    except Exception as err:
        emit(name, 'fail', 'Audit exception; inspect raw exception', error=repr(err))

def run(args, cwd=ROOT):
    p = subprocess.run(args, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace')
    row = dict(command=args, cwd=str(cwd), exit_code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    COMMANDS.append(row)
    return p

def same_files(base, rows):
    return [x['path'] for x in rows if not (base / x['path']).is_file()
            or sha(base / x['path']) != x['sha256']
            or ('bytes' in x and (base / x['path']).stat().st_size != x['bytes'])]

def production():
    before = read('production-before.json')
    drift = same_files(ROOT, before['files'])
    check('production_and_tests_unchanged', not drift, 'production-before.json', checked=len(before['files']), mismatches=drift)
    fp = json.loads((ROOT/'workflow/verification/final-evidence-fingerprint-03.json').read_text(encoding='utf-8'))
    rows = [dict(path=k, sha256=v) for k,v in fp['production']['files'].items()]
    rows += [dict(path=k, sha256=v) for k,v in fp['final_runtime_test_files'].items()]
    mismatch = same_files(ROOT, rows)
    actual_production=set()
    for prefix in ['AppScope','entry','core','feature','hvigor']:
        for current,dirs,names in os.walk(ROOT/prefix):
            dirs[:]=[d for d in dirs if d not in {'build','oh_modules','.hvigor','.preview','.git'}]
            actual_production.update((Path(current)/name).relative_to(ROOT).as_posix() for name in names)
    actual_production.update(p.name for p in ROOT.iterdir() if p.is_file() and p.suffix in {'.json','.json5','.ts','.properties','.bat'})
    extra=sorted(actual_production-set(fp['production']['files']))
    aggregate=hashlib.sha256(json.dumps(fp['production']['files'],sort_keys=True).encode()).hexdigest()
    check('final_verification_source_identity', not mismatch, 'workflow/verification/final-evidence-fingerprint-03.json', checked=len(rows), mismatches=mismatch, source_sha256=fp['production']['sha256'])
    check('production_file_set_and_aggregate',not extra and actual_production==set(fp['production']['files']) and aggregate==fp['production']['sha256'],
          'independent directory enumeration and recorded path/hash JSON aggregation',extra_production_files=extra,
          missing_production_files=sorted(set(fp['production']['files'])-actual_production),computed_aggregate=aggregate)
    facts = read('facts.json')
    hap = ROOT/facts['hap']['path']
    matrix = json.loads((ROOT/'logs/verification-final-03.json').read_text(encoding='utf-8'))
    counts = dict(Counter(x['status'] for x in matrix['requirements']))
    blocked = sorted(x['requirement'] for x in matrix['requirements'] if x['status']=='blocked')
    check('hap_and_matrix_identity', sha(hap)==facts['hap']['sha256']==fp['hap_sha256']==matrix['hap_sha256']
          and matrix['source_sha256']==fp['production']['sha256'] and counts=={'pass':38,'blocked':3}
          and blocked==['B10','B11','B9'] and not facts['validation']['full_feature_validation_complete'],
          'facts.json; logs/verification-final-03.json', counts=counts, blocked=blocked, hap_sha256=sha(hap))
    missing_evidence=[]
    for row in matrix['requirements']:
        for ev in row.get('evidence',[]):
            if ev.get('observation') and not (ROOT/ev['observation']).is_file():
                missing_evidence.append(ev['observation'])
    check('matrix_observation_paths', not missing_evidence, 'logs/verification-final-03.json', missing=missing_evidence)
    build=json.loads((ROOT/'logs/verification-navigation-smoke-03/build.json').read_text(encoding='utf-8'))
    check('final_build_raw_result',build['exit_code']==0 and not build['timed_out'] and 'BUILD SUCCESSFUL' in build['stdout'],
          'logs/verification-navigation-smoke-03/build.json',exit_code=build['exit_code'],command=build['command'])
    errors=[]; summaries=[]
    for row in matrix['rounds']:
        folder=ROOT/row['round']
        def j(name): return json.loads((folder/name).read_text(encoding='utf-8'))
        install,manifest,cases=j('install.json'),j('install-manifest.json'),j('selftest.json')
        first,last=j('fingerprint-before.json'),j('fingerprint-after.json')
        codefirst,codelast=j('test-code-fingerprint-before.json'),j('test-code-fingerprint-after.json')
        badcode=same_files(folder/'test-code',[dict(path=k,sha256=v) for k,v in codefirst.items()])
        checks={'hap':manifest['hap_sha256']==fp['hap_sha256'],
                'source':manifest['source_sha256']==first['sha256']==last['sha256']==fp['production']['sha256'],
                'source_files':first['files']==last['files']==fp['production']['files'],
                'install':install['exit_code']==manifest['install_exit_code']==0 and 'successfully' in install['stdout'],
                'cases':cases['cases']==row['raw_cases'], 'case_counts':dict(Counter(x['outcome'] for x in cases['cases']))==row['case_counts'],
                'test_archive':codefirst==codelast==row['test_code_sha256'] and not badcode}
        if not all(checks.values()): errors.append({'round':row['round'],'failed':[k for k,v in checks.items() if not v], 'archive_mismatches':badcode})
        summaries.append({'round':row['round'],'device':manifest['device'],'hap_sha256':manifest['hap_sha256'],
                          'source_sha256':manifest['source_sha256'],'case_counts':row['case_counts'], 'test_archive_files':len(codefirst)})
    check('existing_install_selftest_source_hap_archives_correspond',not errors,'logs/verification-final-03.json; per-round install/fingerprint/selftest/test-code',errors=errors,rounds=summaries)

def logs():
    m = read('logs-copy-manifest.json')
    source_drift = same_files(ROOT,m['copied'])
    copy_drift = same_files(OUT,m['copied'])
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT/'logs').rglob('*') if p.is_file()}
    represented={x['path'] for x in m['copied']+m['excluded_reproducible_cache']}
    check('logs_copy_complete_and_exact', not source_drift and not copy_drift and actual==represented,
          'logs-copy-manifest.json', copied=len(m['copied']), exclusions=len(m['excluded_reproducible_cache']),
          source_mismatches=source_drift, copy_mismatches=copy_drift, unrepresented=sorted(actual-represented), stale=sorted(represented-actual))
    check('logs_exclusions_are_declared_runtime_disks', all(x.get('reason') and x['path'].startswith('logs/verification-emulator/instances/')
          and x['path'].endswith(('.img','.qcow2','.lock','.pid')) for x in m['excluded_reproducible_cache']), 'logs-copy-manifest.json')
    required=['logs/verification-closeout-03/temporary-disk-cleanup-rejected.json', 'logs/verification-final-03.json',
              'logs/verification-phone-suite-02/hypium-runner.stderr.txt']
    check('failed_round_and_rejection_preserved', all((OUT/x).is_file() for x in required), required)

def inputs():
    pairs=[('evidence-inputs/team.yaml',ROOT.parent/'common/spec-harness/team.yaml'),
           ('evidence-inputs/submit-input.yaml',ROOT/'spec/submit-input.yaml')]
    mismatch=[a for a,b in pairs if sha(OUT/a)!=sha(b)]
    versions=read('taskbook-versions.json')
    for row in versions['task_books']:
        if sha(ROOT/row['common_path'])!=row['sha256'] or sha(ROOT/row['local_path'])!=row['local_sha256']:
            mismatch.append(row['local_path'])
    for row in versions['official_templates']:
        p=Path(row['path'])
        if sha(p)!=row['sha256'] or sha(OUT/'evidence-inputs/templates'/p.name)!=row['sha256']:
            mismatch.append(p.name)
    check('real_inputs_templates_taskbook_versions',not mismatch,'evidence-inputs/; taskbook-versions.json',mismatches=mismatch,
          baseline_log_exists=versions['official_baseline_report']['exists'],history=versions['history'])

def native():
    m=read('traces/session-metadata.json')
    discovery=read('traces/discovery.json')
    searches=read('traces/native-discovery-search.json')
    excluded=set(discovery['excluded_overview_session_ids'])
    state=json.loads((ROOT/'workflow/state.json').read_text(encoding='utf-8'))
    registered={x['session_id'] for x in state['sessions'] if x.get('session_id') and not x.get('excluded_from_task_evidence')}
    selected={x['session_id'] for x in m['sessions']}
    missing=sorted(registered-selected)
    ok=set(searches['queries'])=={'project_path','task_id'} and all(x['exit_code'] in (0,1) for x in searches['queries'].values())
    emit('native_two_dimension_discovery', 'fail' if not ok else 'not_run' if missing else 'pass',
         'traces/native-discovery-search.json; traces/discovery.json', missing_registered=missing, selected_count=len(selected),
         note='Pending refreshed export when missing_registered is nonempty. Discovery command/results cross-checked locally; no global session store reread by verifier.')
    errors=[]; summaries=[]
    for row in m['sessions']:
        p=OUT/row['native_path']
        objects=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()]
        h=objects[0]['payload']; sid=h['id']; ctx=[]; models=[]; token=None; usage=None
        for n,obj in enumerate(objects,1):
            t,v=obj.get('type'),obj.get('payload',{})
            if t=='turn_context':
                c={k:v[k] for k in ['model','effort','cwd','approval_policy','sandbox_policy'] if k in v}
                if c not in ctx: ctx.append(c)
                if v.get('model') and v['model'] not in models: models.append(v['model'])
            if t=='event_msg' and v.get('type')=='token_count': token=v.get('info')
            if t=='token_usage_record': usage={'source_line':n,**v}
        relation=h.get('source',{}).get('subagent',{}).get('thread_spawn') if isinstance(h.get('source'),dict) else None
        tests={'native_hash':sha(p)==row['sha256'], 'bytes':p.stat().st_size==row['bytes'],
               'own_id':sid==row['session_id']==row['Codex_native_session_id'],
               'parent_id':relation==row['parent_thread_relation'], 'header_session_id':h.get('session_id')==row['source_header_session_id'],
               'contexts':ctx==row['turn_contexts'], 'models':models==row['models'],
               'latest_token_info':token==row['latest_token_info'], 'latest_usage_record':usage==row['latest_token_usage_record'],
               'line_count':len(objects)==sum(row['event_counts'].values()),
               'excluded':sid not in excluded, 'snapshot_declaration':row['snapshot_only'] and not row['includes_future_events'],
               'markdown_exists':(OUT/row['markdown_path']).is_file()}
        if tests['markdown_exists']:
            md=text(row['markdown_path'])
            blocks=re.findall(r'```json\n(.*?)\n```',md,re.S)
            tests['markdown_complete_native_equivalence']=[json.loads(b) for b in blocks]==objects
        if row['sidebar_index_rows']:
            tests['sidebar_id']=row['IDE_sidebar_id']==sid and all(x['id']==sid for x in row['sidebar_index_rows'])
        else: tests['sidebar_missing_declared']='待补充' in row['IDE_sidebar_id']
        if not all(tests.values()): errors.append({'id':sid,'failed':[k for k,v in tests.items() if not v]})
        summaries.append({'session_id':sid,'source_header_session_id':h.get('session_id'),'parent':relation,
                          'line_count':len(objects),'last_event_type':objects[-1].get('type'),
                          'models':models,'latest_usage_line':usage.get('source_line') if usage else None})
    native_ids=[]
    for p in (OUT/'traces/native').glob('*.jsonl'):
        with p.open(encoding='utf-8') as f: native_ids.append(json.loads(f.readline())['payload']['id'])
    check('native_metadata_latest_cumulative_and_identity', not errors and not (set(native_ids)&excluded)
          and set(native_ids)==selected and not m['gaps'], 'traces/session-metadata.json; traces/native/*.jsonl',
          errors=errors, session_summaries=summaries, excluded_ids=sorted(excluded), gaps=m['gaps'])

def project():
    m=read('project-manifest.json'); rows=m['files']; paths=[x['path'] for x in rows]
    valid_paths=all(not Path(p).is_absolute() and '..' not in Path(p).parts and '\\' not in p for p in paths)
    snapshot=OUT/m['snapshot']; mismatches=same_files(snapshot,rows); live=same_files(ROOT,rows)
    actual={p.relative_to(snapshot).as_posix() for p in snapshot.rglob('*') if p.is_file()}
    version='sha256:'+hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    check('project_snapshot_all_file_hashes', valid_paths and len(paths)==len(set(paths)) and actual==set(paths)
          and not mismatches and not live and version==m['final_version'] and m['not_team_freeze_time'] is True, 'project-manifest.json; traces/code-snapshot/project/',
          files=len(rows), snapshot_mismatches=mismatches, live_mismatches=live, extra=sorted(actual-set(paths)), computed_version=version)
    excluded_ids={'01a13fc4-2611-7761-a580-1283e0c70541'}
    copied_native=[]
    for path in paths:
        if path.startswith('traces/native/') and path.endswith('.jsonl'):
            with (snapshot/path).open(encoding='utf-8') as f: first=json.loads(f.readline())
            if first.get('type')=='session_meta': copied_native.append({'path':path,'id':first['payload']['id']})
    check('project_native_snapshots_exclude_overview',not any(x['id'] in excluded_ids for x in copied_native),
          'snapshot traces/native/ JSONL headers',native_files=len(copied_native),distinct_task_thread_ids=sorted({x['id'] for x in copied_native}))
    ex=read('project-exclusions.json')
    candidates=set(run(['git','ls-files','-z']).stdout.strip('\0').split('\0'))
    candidates.update(run(['git','ls-files','--others','--exclude-standard','-z']).stdout.strip('\0').split('\0'))
    candidates.add('AGENTS.md'); candidates.discard('')
    omitted={x['path'] for x in ex['excluded_files']}
    unexplained=sorted(p for p in candidates-set(paths)-omitted if not p.startswith(ex['excluded_derivative_prefix']) and (ROOT/p).is_file())
    check('project_scope_and_exclusions', not unexplained and all(any(p.startswith(q) for p in paths) for q in ['spec/','hypium_tests/','workflow/','logs/','traces/'])
          and not any(p.startswith('.comate/submission-draft/') for p in paths) and ex['original_files_deleted'] is False,
          'project-exclusions.json; git ls-files', unexplained=unexplained, excluded_files=len(omitted), declared_rules=ex['git_ignored_runtime_exclusions'])
    binaries=read('changes/binary-files.json'); index={x['path']:x for x in binaries}
    required=[]
    for row in rows:
        p=snapshot/row['path']
        with p.open('rb') as f: prefix=f.read(8192)
        if b'\0' in prefix or p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.webp','.ico','.hap','.db','.sqlite'}: required.append(row['path'])
    bad=[x['path'] for x in binaries if not x.get('baseline_lineage') or not x['binary'] or x['sha256']!=sha(snapshot/x['path']) or x['bytes']!=(snapshot/x['path']).stat().st_size]
    check('binary_inventory_complete',set(required)==set(index) and not bad, 'changes/binary-files.json', expected=len(required), listed=len(binaries), invalid=bad)
    p=read('patch-validation.json')
    check('root_patch_proof_consistent',p['passed'] and p['file_count']==len(rows) and p['all_files_compared']==len(rows)
          and p['final_version']==m['final_version'] and p['snapshot_git_tree']==m['snapshot_git_tree']
          and p['patch_sha256']==sha(OUT/'changes/final.diff') and p['apply_check_exit_code']==p['apply_exit_code']==0
          and all(c['exit_code']==0 for c in p['commands']), 'patch-validation.json', commands=len(p['commands']), patch_sha256=p['patch_sha256'])
    diffcheck=run(['git','diff','--check'])
    check('live_git_diff_check',diffcheck.returncode==0,'git diff --check',exit_code=diffcheck.returncode)
    signatures=[]; private_files=[]
    for row in rows:
        path=snapshot/row['path']
        if path.suffix.lower() in {'.p12','.pfx','.jks','.keystore'}: private_files.append(row['path'])
        if path.suffix.lower() in {'.pem','.key'}:
            data=path.read_bytes()
            if re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',data): signatures.append(row['path'])
    check('bounded_sensitive_artifact_scan',not signatures and not private_files,'project-manifest.json; snapshot extensions/private-key header scan',
          private_key_header_paths=signatures,private_artifact_paths=private_files,
          limitation='Bounded artifact/header check, not a guarantee that arbitrary prose/JSON contains no sensitive value. Original records retain local usernames/paths; human final-package review remains pending.')

def docs():
    trace=text('trace-index.md')
    template=Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8')
    fields=[line.strip()[2:].split('：')[0] for line in template.splitlines() if line.startswith('- ')]
    missing=[x for x in fields if x not in trace]
    check('official_trace_index_all_fields',not missing,'trace-index.md; official template',fields=len(fields),missing=missing)
    build=text('build.md')
    absolute=re.findall(r'(?i)(?:[A-Z]:[\\/]|/Users/|/home/|/Applications/)[^\s`]*',build)
    app=(ROOT/'AppScope/app.json5').read_text(encoding='utf-8')
    bundle=re.search(r'"bundleName"\s*:\s*"([^"]+)"',app).group(1)
    required=['ohpm','hvigor','install','aa start','EntryAbility',bundle,'B9','B10','B11']
    check('build_portable_and_complete_review',not absolute and all(s in build for s in required), 'build.md', absolute_paths=absolute,missing_tokens=[x for x in required if x not in build],
          scope='Static portability/instruction audit only; existing build evidence checked separately; no new build/device execution.')
    frag=read('submission.json.fragment')
    tasks=frag['tasks'] if isinstance(frag,dict) and 'tasks' in frag else [frag]
    row=tasks[0]
    mapping={'project_path':'tasks/cml-spec7/project/','build_instructions':'tasks/cml-spec7/build.md','trace_index':'tasks/cml-spec7/trace-index.md'}
    source_mapping={'project_path':OUT/'traces/code-snapshot/project','build_instructions':OUT/'build.md','trace_index':OUT/'trace-index.md'}
    check('json_single_task_relative_paths',len(tasks)==1 and row['task_id']=='cml-spec7' and row['status']=='not_completed'
          and all(row[k].rstrip('/')==v.rstrip('/') for k,v in mapping.items()) and source_mapping['project_path'].is_dir()
          and source_mapping['build_instructions'].is_file() and source_mapping['trace_index'].is_file(),
          'submission.json.fragment',actual=row,expected_mapping=mapping,source_mapping={k:p.relative_to(OUT).as_posix() for k,p in source_mapping.items()},
          note='Stage 3 mapping contract resolves to an existing snapshot directory and two existing files; trailing slash optional for directory; no final ZIP claimed.')
    solution=text('solution.fragment.md'); sources=text('sources.fragment.md'); human=text('human-changes.md'); missing=text('missing-fields.md'); auto=text('auto-filled-facts.md')
    check('partial_completion_and_human_gaps_disclosed',all(x in solution for x in ['38','B9','B10','B11'])
          and '待补充' in human and '待补充' in sources and all(x in missing for x in ['human_edits','known_issues','extra_sources','freeze_time','contact']),
          'solution.fragment.md; sources.fragment.md; human-changes.md; missing-fields.md')
    check('two_handoff_lists_and_original_gaps',bool(auto.strip()) and bool(missing.strip()) and '待补充' in trace
          and any(x in trace for x in ['stdout','标准输出']) and any(x in trace for x in ['不存在','缺失']),
          'auto-filled-facts.md; missing-fields.md; trace-index.md')
    metadata=read('traces/session-metadata.json'); table_errors=[]
    token_section=trace.split('## 模型参数与累计token口径',1)[1].split('## ',1)[0]
    for session in metadata['sessions']:
        sid=session['session_id']; lines=[x for x in token_section.splitlines() if x.startswith('| '+sid+' |')]
        total=(session.get('latest_token_info') or {}).get('total_token_usage') or {}
        vals=[str(total.get(x,'【待补充】')) for x in ['input_tokens','cached_input_tokens','output_tokens','total_tokens']]
        if not lines or [x.strip() for x in lines[0].split('|')[3:7]]!=vals:
            table_errors.append({'id':sid,'field':'token table','expected':vals,'actual':lines})
        if session['sha256'] not in trace: table_errors.append({'id':sid,'field':'native hash'})
        count=sum(session['event_counts'].values())
        if f'1–{count}（ordinal 0–{count-1}）' not in trace: table_errors.append({'id':sid,'field':'line range','expected':count})
    check('trace_tables_match_latest_export',not table_errors,'trace-index.md; traces/session-metadata.json',errors=table_errors)
    review_path=HERE/'manual-document-review.json'
    if not review_path.exists():
        emit('manual_document_semantics','not_run','Await verifier manual reading of final document bytes')
    else:
        review=json.loads(review_path.read_text(encoding='utf-8'))
        stale=[x['path'] for x in review['files'] if sha(OUT/x['path'])!=x['sha256']]
        check('manual_document_semantics',review['passed'] and not stale,'validation/manual-document-review.json',stale=stale,reviewed_fields=review['reviewed_fields'])

def requirement_matrix():
    mapping={
      'S01':['hap_and_matrix_identity','partial_completion_and_human_gaps_disclosed'],
      'S02':['production_and_tests_unchanged'],
      'S03':['real_inputs_templates_taskbook_versions','json_single_task_relative_paths'],
      'S04':['project_scope_and_exclusions','project_snapshot_all_file_hashes','root_patch_proof_consistent'],
      'S05':['independent_baseline_real_apply_all_files'],
      'S06':['project_scope_and_exclusions','independent_change_and_eol_classification'],
      'S07':['binary_inventory_complete','independent_binary_baseline_lineage'],
      'S08':['build_portable_and_complete_review'],
      'S09':['official_trace_index_all_fields','trace_tables_match_latest_export','manual_document_semantics'],
      'S10':['native_two_dimension_discovery','native_metadata_latest_cumulative_and_identity'],
      'S11':['native_metadata_latest_cumulative_and_identity'],
      'S12':['native_metadata_latest_cumulative_and_identity','manual_document_semantics'],
      'S13':['failed_round_and_rejection_preserved','logs_copy_complete_and_exact','manual_document_semantics'],
      'S14':['native_metadata_latest_cumulative_and_identity','real_inputs_templates_taskbook_versions','manual_document_semantics'],
      'S15':['partial_completion_and_human_gaps_disclosed','manual_document_semantics'],
      'S16':['hap_and_matrix_identity','partial_completion_and_human_gaps_disclosed','manual_document_semantics'],
      'S17':['json_single_task_relative_paths'],
      'S18':['logs_copy_complete_and_exact','existing_install_selftest_source_hap_archives_correspond'],
      'S19':['partial_completion_and_human_gaps_disclosed','manual_document_semantics'],
      'S20':['two_handoff_lists_and_original_gaps','manual_document_semantics','bounded_sensitive_artifact_scan'],
      'S21':['two_handoff_lists_and_original_gaps','manual_document_semantics'],
      'S22':['project_snapshot_all_file_hashes','audit_inputs_stable','manual_document_semantics']}
    statuses={x['check']:x['status'] for x in RESULTS}
    output=[]
    for rid,names in mapping.items():
        values=[statuses.get(x,'not_run') for x in names]
        status='fail' if 'fail' in values else 'blocked' if 'blocked' in values else 'not_run' if 'not_run' in values else 'pass'
        output.append({'requirement':rid,'status':status,'checks':names})
    return output

def independent_apply(resume=False):
    m=read('project-manifest.json'); temp=HERE/'independent-baseline'
    if resume:
        prior_path=HERE/'independent-apply-proof-01.json'
        prior=json.loads(prior_path.read_text(encoding='utf-8'))
        if prior['patch_sha256']!=sha(OUT/'changes/final.diff') or any(sha(OUT/k)!=v for k,v in prior['input_sha256'].items()):
            raise RuntimeError('Prior actual apply proof inputs changed')
        original=[c for c in prior['commands'] if c['command'][:2] in [['git','clone'],['git','config'],['git','checkout'],['git','apply'],['git','branch']]]
        applied=[c for c in original if c['command'][:2]==['git','apply']]
        if len(applied)!=2 or any(c['exit_code'] for c in original): raise RuntimeError('Original real apply commands are not successful')
        COMMANDS.extend(original)
        head=run(['git','rev-parse','HEAD'],temp)
        if head.returncode or head.stdout.strip()!=m['base_commit']: raise RuntimeError('Retained applied clone base changed')
        emit('independent_original_apply_proof_reused','pass','validation/independent-apply-proof-01.json; checker-correction-01.json',
             original_proof_sha256=sha(prior_path),reason='Correct verifier dict-shape bug; original clone/check/apply already succeeded, no patch reapplication or deletion.')
    else:
        if temp.exists(): raise RuntimeError('Existing independent-baseline is retained; do not overwrite')
        branch=run(['git','branch','--show-current']).stdout.strip()
        steps=[(['git','clone','--no-checkout','--no-tags','--single-branch','--branch',branch,'--no-local',str(ROOT),str(temp)],ROOT),
               (['git','config','core.autocrlf','false'],temp),
               (['git','checkout','--detach',m['base_commit']],temp),
               (['git','apply','--check','--binary',str(OUT/'changes/final.diff')],temp),
               (['git','apply','--binary',str(OUT/'changes/final.diff')],temp)]
        for args,cwd in steps:
            if run(args,cwd).returncode: raise RuntimeError('Independent clone/apply failed; clone retained')
    mismatch=same_files(temp,m['files'])
    actual={p.relative_to(temp).as_posix() for p in temp.rglob('*') if p.is_file() and '.git' not in p.relative_to(temp).parts}
    expected={x['path'] for x in m['files']}
    check('independent_baseline_real_apply_all_files',not mismatch and actual==expected,'validation command log; project-manifest.json',
          checked=len(expected),mismatches=mismatch,extras=sorted(actual-expected),missing=sorted(expected-actual))
    if mismatch or actual!=expected: return
    # Compare a fresh staged Git tree as well as bytes: this checks path modes and every A/M/D.
    run(['git','-c','core.autocrlf=false','add','--all','--force','.'],temp)
    tree=run(['git','write-tree'],temp)
    raw=run(['git','diff','--cached','--name-status','-z','--no-renames',m['base_commit'],'--'],temp)
    fields=raw.stdout.strip('\0').split('\0')
    changes=[{'status':fields[i],'path':fields[i+1]} for i in range(0,len(fields),2)]
    declared=read('changes/changed-files.json')
    tree_output=run(['git','ls-tree','-r','-z',m['base_commit']],temp)
    baseline={}
    for item in tree_output.stdout.strip('\0').split('\0'):
        left,path=item.split('\t',1); mode,kind,oid=left.split(' ')
        baseline[path]={'mode':mode,'kind':kind,'oid':oid}
    binary_rows=read('changes/binary-files.json')
    requested=sorted({x['path'] for x in changes if x['status']=='M'}|{x['path'] for x in binary_rows if x['path'] in baseline})
    payload=''.join(baseline[p]['oid']+'\n' for p in requested).encode('ascii')
    process=subprocess.run(['git','cat-file','--batch'],cwd=temp,input=payload,capture_output=True)
    output_path=HERE/'baseline-modified-blobs.raw'; output_path.write_bytes(process.stdout)
    COMMANDS.append({'command':['git','cat-file','--batch'],'cwd':str(temp),'exit_code':process.returncode,
                     'stdin_blob_ids':[baseline[p]['oid'] for p in requested],
                     'stdout_file':output_path.relative_to(HERE).as_posix(),'stdout_bytes':len(process.stdout),
                     'stdout_sha256':sha(output_path),'stderr':process.stderr.decode('utf-8',errors='replace')})
    if process.returncode: raise RuntimeError('Independent baseline blob inspection failed')
    data=process.stdout; offset=0; blobs={}
    for path in requested:
        end=data.index(b'\n',offset); head=data[offset:end].decode('ascii').split(' '); size=int(head[2]); offset=end+1
        blobs[path]=data[offset:offset+size]; offset+=size+1
    eol=[]; meaningful=[]
    for row in changes:
        if row['status']=='M':
            old=blobs[row['path']]; new=(temp/row['path']).read_bytes()
            if old!=new and old.replace(b'\r\n',b'\n')==new.replace(b'\r\n',b'\n'):
                eol.append(row['path']); continue
        meaningful.append(row)
    published=read('changes/line-ending-only.json')
    published_rows=published if isinstance(published,list) else published.get('files',published.get('paths',[]))
    published_paths=sorted(x if isinstance(x,str) else x['path'] for x in published_rows)
    noise=[x['path'] for x in meaningful if Path(x['path']).name=='BuildProfile.ets' and not x['path'].startswith(('logs/','traces/'))]
    declared_pairs=[{'status':x['status'],'path':x['path']} for x in declared]
    flags_match=all(x['line_endings_only']==(x['path'] in eol) for x in declared)
    check('independent_change_and_eol_classification',changes==declared_pairs and flags_match and tree.returncode==0 and tree.stdout.strip()==m['snapshot_git_tree']
          and published_paths==sorted(eol) and not noise,'fresh applied clone staged tree/name-status; changes/line-ending-only.json',
          same_tree=tree.stdout.strip(),baseline_modes=dict(Counter(x['mode'] for x in baseline.values())),
          eol_only_count=len(eol),eol_paths=eol,meaningful_changes=len(meaningful),tracked_build_noise=noise,
          eol_inventory_matches=published_paths==sorted(eol),change_inventory_matches=changes==declared_pairs,line_ending_flags_match=flags_match,
          corrected_verifier_check='Projection of status/path plus independent line_endings_only flags; original whole-dict failure preserved in checker-correction-01.json')
    lineage_errors=[]
    for row in binary_rows:
        is_same=row['path'] in blobs and hashlib.sha256(blobs[row['path']]).hexdigest()==row['sha256']
        claims_same=row['baseline_lineage'].startswith('same path and identical bytes')
        if is_same!=claims_same: lineage_errors.append(row['path'])
    resource_rows=read('changes/resource-files.json')
    svg=[]
    for row in resource_rows:
        if Path(row['path']).name.startswith('ic_login_'):
            origin=row.get('baseline_source_path')
            if not origin or origin not in baseline:
                lineage_errors.append(row['path']); continue
            p=subprocess.run(['git','show',m['base_commit']+':'+origin],cwd=temp,capture_output=True)
            equal=p.returncode==0 and hashlib.sha256(p.stdout).hexdigest()==row['sha256']
            COMMANDS.append({'command':['git','show',m['base_commit']+':'+origin],'cwd':str(temp),'exit_code':p.returncode,
                             'stdout_bytes':len(p.stdout),'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),
                             'stderr':p.stderr.decode('utf-8',errors='replace')})
            svg.append({'path':row['path'],'baseline_source_path':origin,'same_bytes':equal})
            if not equal: lineage_errors.append(row['path'])
    check('independent_binary_baseline_lineage',not lineage_errors and len(svg)==3,'baseline blob bytes; binary/resource inventories',
          compared_binary_files=len(binary_rows),errors=lineage_errors,svg_reuse=svg)
    target=temp.resolve(); boundary=HERE.resolve()
    if target.parent!=boundary or target.name!='independent-baseline': raise RuntimeError('Temporary clone boundary check failed')
    # Parent explicitly instructed retention after its own clone cleanup was rejected.
    exclusion={'excluded_material_prefix':'validation/independent-baseline/', 'reason':'Generated local clone for independent patch proof; exclude its complete checkout and .git from Stage 3 materials.',
               'resolved_path':str(target),'exists_after':target.exists(),'cleanup_attempted_by_verifier':False,
               'parent_cleanup_constraint':'Root draft/.validation-work cleanup rejected by automatic approval policy; no alternate deletion mechanism attempted.'}
    (HERE/'temporary-material-exclusions.json').write_text(json.dumps(exclusion,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    emit('independent_clone_retained_and_excluded','pass','validation/temporary-material-exclusions.json',**exclusion)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--apply',action='store_true'); parser.add_argument('--resume-applied',action='store_true'); args=parser.parse_args()
    for name,fn in [('production',production),('inputs',inputs),('logs',logs),('native',native),('project',project),('documents',docs)]: group(name,fn)
    if args.apply or args.resume_applied:
        first_assertion,first_command=len(RESULTS),len(COMMANDS)
        group('independent_apply',lambda:independent_apply(args.resume_applied))
        proof={'assertions':RESULTS[first_assertion:],'commands':COMMANDS[first_command:],
               'input_sha256':{k:v for k,v in INPUTS.items() if k in ['project-manifest.json','changes/final.diff','changes/changed-files.json','changes/line-ending-only.json','changes/binary-files.json','changes/resource-files.json']}}
        proof['patch_sha256']=sha(OUT/'changes/final.diff')
        (HERE/'independent-apply-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    elif (HERE/'independent-apply-proof.json').exists():
        proof=json.loads((HERE/'independent-apply-proof.json').read_text(encoding='utf-8'))
        stale=[k for k,v in proof['input_sha256'].items() if sha(OUT/k)!=v]
        if sha(OUT/'changes/final.diff')!=proof['patch_sha256']: stale.append('changes/final.diff')
        if stale:
            emit('independent_apply_cached_proof','not_run','Prior independent proof invalidated by changed inputs',stale=stale)
        else:
            RESULTS.extend(proof['assertions']); COMMANDS.extend(proof['commands'])
            emit('independent_apply_cached_proof','pass','validation/independent-apply-proof.json; exact input and patch hashes remain unchanged')
    changed=[k for k,v in INPUTS.items() if not (OUT/k).is_file() or sha(OUT/k)!=v]
    check('audit_inputs_stable',not changed,'SHA-256 at first read and final report',changed_during_audit=changed)
    result={'schema_version':1,'task_id':'cml-spec7','role':'harmony_verification','thread_id':os.environ.get('CODEX_THREAD_ID'),
            'checked_at_utc':datetime.now(timezone.utc).isoformat(),'purpose':'Independent materials audit; no build/device/feature rerun',
            'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'argv':sys.argv},
            'counts':dict(Counter(x['status'] for x in RESULTS)),'assertions':RESULTS,'requirements':requirement_matrix(),'input_sha256':INPUTS,'commands':COMMANDS,
            'known_unresolved':['B9/B10/B11 remain blocked; 38 pass is local requirement evidence, not official score',
                               'Blank human/team declarations and official freeze/submission selection remain unprovided',
                               'Original baseline log, initial stdout gap, unavailable independent IDE/Comate identifiers remain disclosed gaps',
                               'Root temporary-clone cleanup rejected by automatic approval policy (blocked by policy); generated clones retained and excluded, no alternate deletion attempted']}
    result['result']='fail' if result['counts'].get('fail') else 'pending' if result['counts'].get('not_run') else 'pass_with_declared_gaps'
    (HERE/'materials-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# cml-spec7 独立材料验证','',f"结果：{result['result']}；真实 CODEX_THREAD_ID={result['thread_id']}。",'',
           '本报告只校验材料及既有功能证据对应关系；未重跑构建、设备或功能测试。生产文件与测试按字节核对。', '',
           '| 检查 | 状态 | 证据 |','| --- | --- | --- |']
    lines += [f"| {x['check']} | {x['status']} | {str(x['evidence']).replace('|','/')} |" for x in RESULTS]
    lines += ['', '| 批准需求 | 状态 | 对应检查 |', '| --- | --- | --- |']
    lines += [f"| {x['requirement']} | {x['status']} | {', '.join(x['checks'])} |" for x in result['requirements']]
    lines += ['', '全部命令、退出码、stdout/stderr、各会话ID/父ID、原始行数、输入SHA-256及失败详情见同名JSON。', '',
              '待解决：B9/B10/B11外部接入条件、空白人工/团队声明、正式冻结时间/提交选择、已声明的原始日志及ID缺口。当前草案不代表整题完成或正式提交。']
    (HERE/'materials-verification.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for ext in ['json','md']:
        (HERE/('audit-run-'+stamp+'.'+ext)).write_bytes((HERE/('materials-verification.'+ext)).read_bytes())
    print(json.dumps({'result':result['result'],'counts':result['counts'],'issues':[x for x in RESULTS if x['status']!='pass']},ensure_ascii=False))
    return 1 if result['counts'].get('fail') else 0

if __name__=='__main__': sys.exit(main())
