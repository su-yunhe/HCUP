"""Audit final native/doc slice, retaining the completed exact-patch proof unchanged."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('materials',HERE/'verify_materials.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
OUT=v.OUT
expected='94a96a73b3e2f54cf657631a0c56b8a919e6baeee36ee2c20ae57a17abdaf496'
full_path=HERE/'full-apply-03.json'
full=json.loads(full_path.read_text(encoding='utf-8'))
v.check('immutable_full_apply_proof_anchor',v.sha(full_path)==expected and full['result']=='pass_with_declared_gaps'
        and full['counts']=={'pass':33},'validation/full-apply-03.json',sha256=v.sha(full_path),expected_sha256=expected)
anchor_keys=['project-manifest.json','project-exclusions.json','changes/changed-files.json','changes/line-ending-only.json',
             'changes/binary-files.json','changes/resource-files.json','patch-validation.json','production-before.json']
changed=[p for p in anchor_keys if v.sha(OUT/p)!=full['input_sha256'][p]]
patch=next(x for x in full['assertions'] if x['check']=='root_patch_proof_consistent')['patch_sha256']
v.check('same_project_and_patch_version',not changed and v.sha(OUT/'changes/final.diff')==patch,
        'Identical manifest/inventory/proof bytes and actual patch SHA-256; agreed immutable source window',
        changed=changed,patch_sha256=v.sha(OUT/'changes/final.diff'),
        note='Full source/snapshot/apply checks are reused from the anchored report; not rerun in this final targeted audit.')
for p in anchor_keys:v.INPUTS[p]=v.sha(OUT/p)
v.INPUTS['changes/final.diff']=v.sha(OUT/'changes/final.diff')

review_path=HERE/'manual-document-review.json'
old=json.loads(review_path.read_text(encoding='utf-8'))
old_copy=HERE/'manual-document-review-full-apply-03.json'
if not old_copy.exists():old_copy.write_bytes(review_path.read_bytes())
original=json.loads(old_copy.read_text(encoding='utf-8'))
changes=[x['path'] for x in original['files'] if v.sha(OUT/x['path'])!=x['sha256']]
v.check('final_nine_document_delta_scope',changes==['trace-index.md'] and v.sha(OUT/'trace-index.md')=='54e05cadf31a4a2820cfbeb14ea67eebd20e67973ddeea1f9f0228d7c292d695',
        'Nine document hashes versus original manual review',changed=changes,trace_sha256=v.sha(OUT/'trace-index.md'))
old['reviewed_at_utc']=datetime.now(timezone.utc).isoformat()
old['method']='Final official field prose reread; only trace-index changed. All native/Markdown events, latest metadata/token tables and final trace hashes/line ranges checked mechanically. Other eight documents unchanged from full manual review.'
old['files']=[{'path':x['path'],'sha256':v.sha(OUT/x['path'])} for x in original['files']]
review_path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

v.group('final_native',v.native)
v.group('final_documents',v.docs)

markers=[]
for sid in ['01a15914-c10a-7f52-8c6b-5180f42bb365','01a1590b-c9f9-7f32-9607-2b3f4c8c38e7']:
    objs=[json.loads(s) for s in (OUT/'traces/native'/f'{sid}.jsonl').read_text(encoding='utf-8').splitlines()]
    for n,obj in enumerate(objs,1):
        p=obj.get('payload',{})
        if obj.get('type')=='response_item' and p.get('type') in ['function_call_output','custom_tool_call_output']:
            val=str(p.get('output',''))
            if 'pass_with_declared_gaps' in val or 'blocked by policy' in val:
                markers.append({'session_id':sid,'line':n,'call_id':p.get('call_id'),
                                'successful_audit_marker':'pass_with_declared_gaps' in val,'cleanup_rejection_marker':'blocked by policy' in val})
v.check('final_native_contains_substantive_verification_and_rejection',
        any(x['successful_audit_marker'] and x['session_id']=='01a15914-c10a-7f52-8c6b-5180f42bb365' for x in markers)
        and any(x['cleanup_rejection_marker'] and x['session_id']=='01a1590b-c9f9-7f32-9607-2b3f4c8c38e7' for x in markers),
        'Actual native tool-output events (not only prompts/summary prose)',matching_events=markers)
assembly=v.read('assembly-plan.json'); rejection=v.read('temporary-clone-cleanup-rejected.json')
v.check('retained_clones_excluded_without_cleanup_retry',set(['.validation-work/','validation/independent-baseline/']).issubset(assembly['exclude_prefixes'])
        and rejection['executed'] is False and rejection['alternative_deletion_attempted'] is False,
        'assembly-plan.json; temporary-clone-cleanup-rejected.json',reason=rejection['tool_reason'])
drift=[k for k,h in v.INPUTS.items() if v.sha(OUT/k)!=h]
v.check('final_slice_inputs_stable',not drift,'First-read/final SHA-256 over this targeted audit',changed_during_audit=drift)

counts=dict(Counter(x['status'] for x in v.RESULTS))
report={'schema_version':1,'task_id':'cml-spec7','thread_id':os.environ.get('CODEX_THREAD_ID'),
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Final native/doc slice audit; no clone/apply/build/device/feature rerun',
        'result':'fail' if counts.get('fail') else 'pending' if counts.get('not_run') else 'pass_with_declared_gaps',
        'counts':counts,'assertions':v.RESULTS,'requirements':full['requirements'],
        'inherited_full_apply':{'path':'validation/full-apply-03.json','sha256':expected,'assertions':33,'requirements':22,
                                'source_sha256':'26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e',
                                'patch_sha256':patch,'same_immutable_version':not changed,
                                'original_apply_commands_results':'validation/independent-apply-proof-01.json',
                                'checker_failure_and_correction':'validation/checker-correction-01.json'},
        'input_sha256':v.INPUTS,'known_unresolved':full['known_unresolved'],
        'cutoff_note':'Final exported records include substantive patch validation and cleanup refusal. This targeted audit and later closeout are after that declared slice; future events are not claimed exported.',
        'verification_script_sha256':v.sha(Path(__file__))}
(HERE/'materials-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# cml-spec7 最终材料独立验证','',f"结果：{report['result']}；本轮{counts}。",'',
       '最后15会话的原生JSONL/Markdown、模型/effort/最新累计token、ID/父ID、索引hash与事件范围一致，官方24字段及人工待补声明保持原义。',
       '完整补丁证据锚定 full-apply-03.json（SHA-256 '+expected+'）；同一工程/补丁版本保持有效：4554文件、4460差异、667纯行尾项、173二进制和3SVG同源已通过。此次不重跑clone/apply/构建/设备。','',
       '| 本轮检查 | 状态 |','| --- | --- |']
lines += [f"| {x['check']} | {x['status']} |" for x in v.RESULTS]
lines += ['', 'S01–S22草案核验22pass沿用完整报告，并经本轮最新文档/会话复核。历史预检、验证器字段比较失败及修正证据均保留。',
          '', '剩余：B9–B11真实授权阻断、人工/团队声明、正式版本和冻结/提交选择及已披露原始日志/ID缺口。不得将草案核验通过解释为功能全完成或正式提交。',
          '', '自动审批曾以 blocked by policy 拒绝主调度临时克隆清理；未执行、未换机制删除。克隆保留，并在assembly排除。',
          '', '当前定向审查及其后收尾晚于所声明原生切片，不声称已覆盖未来事件。真实 CODEX_THREAD_ID='+str(report['thread_id'])+'。']
(HERE/'materials-verification.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for suffix in ['json','md']:(HERE/('final-slice-04.'+suffix)).write_bytes((HERE/('materials-verification.'+suffix)).read_bytes())
print(json.dumps({'result':report['result'],'counts':counts,'issues':[x for x in v.RESULTS if x['status']!='pass']},ensure_ascii=False))
sys.exit(1 if counts.get('fail') else 0)
