"""Merge actual per-case results; never rewrite original run reports."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
base = root / 'logs/implementation-verification'
reference = json.loads((root/'workflow/implementation/source-fingerprint-v2.json').read_text(encoding='utf-8-sig'))
actual = {p:hashlib.sha256((root/p).read_bytes()).hexdigest()
          for p in reference['tracked_plus_authorized_new_files_sha256']}
changed = [p for p,h in actual.items() if h != reference['tracked_plus_authorized_new_files_sha256'][p]]
comparison = {'reference_aggregate':reference['aggregate_sha256'],'file_count':len(actual),
              'mismatches':changed,'matched':not changed,'actual_files_sha256':actual}
(base/'final-source-fingerprint-comparison.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
if changed:
    raise RuntimeError('Frozen source changed: evidence requires revalidation')

reports = {run:json.loads((base/run/'selftest.json').read_text(encoding='utf-8-sig')) for run in ('run02','run04')}
latest = {}
for run,report in reports.items():
    for case in report['cases']:
        method = case['name'].split(' ')[0]
        latest[method] = dict(case,source_run=run,original_report=f'logs/implementation-verification/{run}/selftest.json')
assert len(latest)==17, f'Expected 17 distinct real cases, got {len(latest)}'
counts={key:sum(case['outcome']==key for case in latest.values()) for key in ('pass','fail','error','skip')}
history=[]
for run in ('run01','run02','run03','run04'):
    record=json.loads((base/run/'run-result.json').read_text(encoding='utf-8-sig'))
    raw_report = base/run/'selftest.json'
    record['run_report']=f'logs/implementation-verification/{run}/selftest.json' if raw_report.exists() else None
    record['run_result']=f'logs/implementation-verification/{run}/run-result.json'
    record['cleanup_log']=f'logs/implementation-verification/{run}/' + ('cleanup-corrected.log' if run=='run01' else 'commands.log')
    if raw_report.exists():
        raw_cases=json.loads(raw_report.read_text(encoding='utf-8-sig'))['cases']
        record['raw_counts']={key:sum(case['outcome']==key for case in raw_cases) for key in ('pass','fail','error','skip')}
    record['disposition']='interrupted/not_run' if run in ('run01','run03') else 'actual_results_retained'
    history.append(record)
result={'project':str(root),'device_sn':'127.0.0.1:5555','env_warnings':reports['run04']['env_warnings'],
        'combined_runs':['run02','run04'],'aggregation':'latest_actual_result_per_case_same_frozen_v2_source',
        'not_a_single_full_suite_run':True,'source_aggregate_reference':reference['aggregate_sha256'],
        'source_fingerprint_matched':True,'generated_utc':datetime.now(timezone.utc).isoformat(),
        'counts':counts,'cases':[latest[name] for name in sorted(latest)],'run_history':history,
        'oracle_review':'workflow/requirements/test14-oracle-review-v1.md',
        'note':'Original run02 remains 14 pass / 1 fail; run04 independently reruns corrected test14 and adds test15/test16. run01/run03 remain interrupted.'}
(root/'logs/selftest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
short=['# vg-spec13 验证结果摘要','',
       f"同一 v2 冻结源码按每用例最新实际结果合并：{counts}；17 个独立用例。不是单次17/17全套。",'',
       '- 原始 run02：14 pass / 1 fail（test14 判据过度）；原报告保留。',
       '- run04：test14 精准修正复测及 test15/test16 补充；实际结果见下表。',
       '- run01/run03：interrupted/not_run，均不计通过。',
       f"- 全指纹匹配：{reference['aggregate_sha256']}，逐文件核对 {len(actual)} 项，无差异。",'',
       '| 用例 | 最新结果 | 原始运行 |','| --- | --- | --- |']
short.extend(f"| {name} | {case['outcome']} | {case['source_run']} |" for name,case in sorted(latest.items()))
short.extend(['','A01–A16 明文项均由 run02 核心真实备份取得证据；R01–R10 的已批准可执行分支已覆盖。',
              '未安全注入的本地导出/加密/TaskPool异常仍为 not_run；详细逐项矩阵、原始证据与限制见 final-report.md。'])
(root/'workflow/verification/summary.md').write_text('\n'.join(short)+'\n',encoding='utf-8')
print(json.dumps({'counts':counts,'canonical':'logs/selftest.json','fingerprint_matched':not changed}))
