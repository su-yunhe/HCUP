"""Report only: consume retained evidence without importing tests or operating device."""
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('D:/HCUP/vg-spec15')
LOG = ROOT / 'logs/implementation-validation'
OUT = ROOT / 'workflow/verification'

def read(name):
    return json.loads((LOG / name).read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

results = read('selftest-09.json')
command = read('selftest-09-command.json')
build = read('build-round-02/build-result.json')
warnings = read('build-round-02/warning-comparison.json')
source_before = read('source-before-run-09.json')
source_after = read('source-after-run-09.json')
tests_before = read('tests-before-run-09.json')
tests_after = read('tests-after-run-09.json')
audit = read('run-09/offline-audit.json')
cleanup = read('cleanup-final.json')
cache = read('test-cache-cleanup.json')
cache.update(exists_after=(ROOT / 'hypium_tests/__pycache__').exists(),
             method='Explicit verified .pyc LiteralPath files, then empty directory; nonrecursive',
             cleanup_command_exit_code=0)
write(LOG / 'test-cache-cleanup.json', cache)
outcomes = dict(collections.Counter(case['outcome'] for case in results['cases']))
assert outcomes == {'pass': 9} and command['exit_code'] == 0 and command['cases'] == ''
assert source_before == source_after
assert tests_before['files'] == tests_after['files']
assert all(hashlib.sha256((ROOT / 'hypium_tests' / name).read_bytes()).hexdigest() == sha
           for name, sha in tests_before['files'].items())
assert build['exit_code'] == 0 and warnings['baseline_diagnostics'] == warnings['current_diagnostics'] == 759
assert not warnings['added'] and not warnings['removed']
assert all(cleanup[k] for k in ('preexisting_preserved', 'own_mappings_absent', 'loopback_service_stopped'))
assert not cache['exists_after']

# Each status is restricted to the stated scope; unexercised subcases remain explicit.
matrix = []
def row(number, status, scope, evidence, limitations=''):
    matrix.append(dict(id=f'A{number:02}', status=status, scope=scope,
                       evidence=evidence, limitations=limitations))

core = 'run-09/offline-audit.json; run-09/timeline.jsonl; selftest-09.json; run-09 UI JSON/PNG'
row(1, 'pass', 'Actual navigation to WebDAV configuration', 'test_01; test_07')
row(2, 'pass', 'Fill/readback current fields; real authentication and decryption including spaced passwords', 'test_00; test_00a; test_01; test_04')
row(3, 'pass', 'First native confirmation opens before authorization', 'test_01; test_02; test_03')
row(4, 'pass', 'First Continue starts genuine restoration', 'test_01; test_02; ' + core)
row(5, 'pass', 'Visible ArkUI LoadingProgress during genuine pending request and authorized import', core,
    'Preview pending UI separately covered only by extracted-method controlled dependencies, not device sampling')
row(6, 'pass', 'Restore-specific first Continue action timestamped', core)
row(7, 'pass', 'Actual pending work owns busy UI', core)
row(8, 'pass', 'Visible restoration status has ongoing-operation meaning', core)
row(9, 'pass', 'Repeated status/loading samples while genuine request pending; actual import status visible', core,
    '15 samples prove observed points; full asynchronous branch lifetime additionally has source/dependency evidence')
row(10, 'pass', 'First Continue correlated with this run, excluding old requests', core)
row(11, 'pass', 'Loading and actual request occur in the same restoration', core)
row(12, 'pass', 'Current configured endpoint receives original restore-chain request; decrypt/preview/import chain exercised', core)
row(13, 'pass', 'Controlled service preserves request begin/end/action records', core)
row(14, 'pass', 'Each required field empty and all empty; directory default; terminal without false success/network fallback', 'test_06')
row(15, 'pass', 'Each required field whitespace and all whitespace; directory default; legitimate spaced passwords retained', 'test_06; test_04')
row(16, 'pass', 'First Cancel: no restore request, saved A survives restart, draft B preserved while mounted', 'test_02; test_00a')
row(17, 'pass', 'Actual system Back dismisses first dialog; no restore and saved A retained', 'test_02',
    'No unsupported outside-mask dismissal contract')
row(18, 'pass', 'Pending repeated actions cannot create competing restoration; later genuine retries work', 'test_03; test_05')
row(19, 'pass', 'Rapid entry/Continue: at most one dialog and no unauthorized request; eventual single flow', 'test_03; workflow/requirements/test-contract-review-02.md',
    'Rapid outside taps may leave zero or one dialog; zero requires stable single reopen before authorized flow')
row(20, 'not_run', 'Partial: missing backup404, empty decrypted plaintext, legal empty business fixture pass', 'test_05',
    'Cloud backup not-updated branch not device-exercised; whole four-subcase item is not a blanket pass')
row(21, 'pass', 'Reasoned non-applicability: this restoration has no pagination/last-page model', 'spec/acceptance.md A21; approved requirements review',
    'No fabricated device pagination test')
row(22, 'pass', 'No first authorization means no restore; second Cancel leaves business word set identical', 'test_02; test_04; run-09/export-01.json; run-09/export-02.json',
    'Second-confirm system-close variant not separately exercised; second Cancel is the device authorization negative case')
row(23, 'pass', 'Real401/403/503, disconnect/read-timeout, malformed cipher/wrong key, preview failure; terminal/retry', 'test_05; dependency-results.json',
    'Direct connection-refused not separately exercised; settings-save and import rejection only source-level controlled dependencies')
row(24, 'pass', 'Exploratory terminal/idle section and route return/reentry observed', 'test_07; run-09 section/route snapshots',
    'Active download/preview/second-confirm/import reentry not_run; no continuation or persistence guarantee asserted')
row(25, 'pass', 'Exploratory process restart observed; explicit saved configuration readback tested', 'test_07; test_00; test_02',
    'Restart during active download/second-confirm/import not_run; no resume, retry, or result persistence guarantee asserted')
row(26, 'pass', 'True held request owns activity until release, real network timeout terminates, authorized import completes', 'run-09/offline-audit.json; dependency-results.json; frozen Section',
    'Preview pending/reject and settings/import failure branches source-level Node controlled dependencies only; not ArkTS VM/UI proof')
row(27, 'pass', 'R01 current form direct use with invalid saved state and saved A to unsaved B; R02 cancel/close no save', 'test_00; test_00a; test_01; test_02')
row(28, 'pass', 'R03 second wait has no spinner and retains exclusivity; Cancel unchanged data; Continue actual import UI/data', 'test_04; test_05; run-09/offline-audit.json')
row(29, 'pass', 'Actual ongoing restore text checked in its region; exact example wording not imposed', 'test_01; test_04; frozen tests')
row(30, 'pass', 'Actual restore endpoint/chain checked; HTTP method/path/total-count not promoted to Spec contract', 'test_01; test_03; test_05; controlled service log')
row(31, 'pass', 'Exploratory terminal/idle background/foreground and page/application lifecycle observed', 'test_07',
    'Closing during real pending work not_run; no background continuation/cancellation/persistence guarantee asserted')
assert len(matrix) == 31

report = dict(
    task='vg-spec15', phase='independent implementation verification', round='02',
    native_thread_id='01a14010-40f0-7aa2-b3d6-dd38f83d64f4',
    completed_utc=datetime.now(timezone.utc).isoformat(),
    conclusion='Final full run09: 9 pass, 0 fail, 0 error, 0 skip; core A01-A13 pass. Coverage limits retained.',
    source_manifest='workflow/implementation/source-round-02.json',
    source_sha256=source_before['sha256'], source_file_count=len(source_before['files']),
    source_unchanged=True, tests_sha256=tests_before['sha256'], test_file_count=len(tests_before['files']),
    tests_before_after_actual_equal=True, hap_sha256=command['hap_sha256'],
    build=dict(exit_code=0, command=build['command'], baseline_diagnostics=759, current_diagnostics=759,
               added=[], removed=[], evidence='logs/implementation-validation/build-round-02/'),
    final_run=dict(run='09', command=command['command'], exit_code=0, selected_cases='',
                   pass_count=9, fail_count=0, error_count=0, skip_count=0, duration_seconds=964.786,
                   fresh_install='logs/implementation-validation/install-09.json',
                   raw_log='logs/implementation-validation/selftest-09.raw.log',
                   harness='logs/implementation-validation/selftest-09.json'),
    offline_audit=dict(exit_code=0, pending_samples=15, all_samples_in_live_request_intervals=True,
                       before_words=1000, after_cancel_words=1000, after_import_words=2000,
                       verified_new_words=1000, cancel_wordset_unchanged=True,
                       evidence='logs/implementation-validation/run-09/offline-audit.json'),
    environment=dict(device='127.0.0.1:5555', model_reported='emulator', api=23,
                     software='emulator 6.1.0.115(SP11DEVC00E115R4P11)', display='1308x2880@60, density3.5',
                     hypium='6.1.0.210', python='3.12.3', hdc='3.2.0c',
                     evidence='logs/implementation-validation/environment.json',
                     limitation='Model identifier does not independently verify exact Pura model; dpi param failed1002, DisplayManager fallback used'),
    matrix=matrix,
    source_dependency_probe=dict(pass_groups=7, source_sha256='e0e4f0804e3403c263f6e09b0d4efb204e90ee7acdbd00b77f3580f35bcf0508',
                                 evidence='logs/implementation-validation/dependency-results.json',
                                 limitation='Extracted actual frozen Section method transpiled in Node with controlled dependencies; not ArkTS VM/UI/network/business storage'),
    retained_failures=[
        dict(runs='01-03', classification='product', fingerprint='VG15_CURRENT_FORM_RESET_ON_FIRST_CONFIRM',
             resolution='Approved View live-getter repair, production round02; final09 regression pass',
             evidence='workflow/verification/implementation-round-01.md'),
        dict(runs='04', classification='test navigation', resolution='Avoid Back after already-empty no-op input; run05 core pass; final09 all pass'),
        dict(runs='06-07', classification='test timing/contract', resolution='Wait actual dialog disappearance and stable enabled bounds; rapid outside taps 0/1 allowed by requirements review; run08 affected pass then final09 all pass',
             traceability='Run06 lacked contemporaneous test archive; labelled reconstruction retained. Runs07-09 exact before/after test archives. No historical failures overwritten.')],
    additional_not_run=['same-mounted-view theme rerender', 'cloud backup not-updated branch',
                        'active restoration lifecycle variants', 'second-confirm system-close variant',
                        'direct connection-refused variant'],
    cleanup=dict(device_lease='RELEASED to Root; no further device commands', own_loopback_service_stopped=True,
                 own_mappings_absent=True, own_hypium_mappings_removed=9, preexisting_mappings_preserved=3,
                 generated_test_cache_removed=True, evidence='logs/implementation-validation/cleanup-final.json',
                 cache_evidence='logs/implementation-validation/test-cache-cleanup.json',
                 device_contents='Installed current HAP, fictional loopback WebDAV settings and test words remain in simulator. Fixtures live only in test support/logs; no fixture data embedded in production source.',
                 tracked_build_noise='None found; existing AGENTS and approved production changes preserved'),
    evidence_root='logs/implementation-validation',
    official_score='not_run; no hidden tests or official grading claim')
write(OUT / 'implementation-round-02.json', report)

lines = [
    '# vg-spec15 独立自测 round02', '',
    '最终完整 run09：**9 pass / 0 fail / 0 error / 0 skip**，964.786s，退出码0。A01–A13 核心均通过。未覆盖项见下表，未推断官方成绩。', '',
    f"会话 `{report['native_thread_id']}`。仅写自测脚本与证据；生产代码由 Root 冻结，测试前后源码及测试字节一致。", '',
    '## 构建、命令与指纹', '',
    '- 独立 clean build：`' + build['command'] + '`，退出码0；759条规范化诊断与基线完全一致，无新增/删除。见 `logs/implementation-validation/build-round-02/`。',
    '- 完整执行：`powershell -File hypium_tests/run.ps1 -Run 09`（Cases为空）；每次执行前安装当前HAP，安装退出码0且成功文本已核对。实际 harness 命令与退出码见 `selftest-09-command.json`；完整原始日志 `selftest-09.raw.log`。',
    '- 离线证据复核：`python hypium_tests/summarize.py 09`，退出码0，结果 `run-09/offline-audit.json`。',
    f"- 250文件源码 SHA256：`{report['source_sha256']}`。四个批准文件另与 `workflow/implementation/source-round-02.json` 核对。",
    f"- HAP SHA256：`{report['hap_sha256']}`。",
    f"- 9个测试/脚本文件 SHA256：`{report['tests_sha256']}`。`tests-before-run-09.json`、`tests-after-run-09.json`及两份逐文件归档均一致，当前字节亦一致。", '',
    '上述短证据路径均在 `logs/implementation-validation/` 下。', '',
    '## 实测结论', '',
    '15个 LoadingProgress/进行中文案采样全部严格位于对应真实请求 begin/end 内；包含无有效旧配置直接恢复、已存A草稿B、连点、第二取消及实际导入。组件节点类型为 ArkUI LoadingProgress。第二确认人工等待不显示活动组件，并保持恢复排他。', '',
    '通过应用原有实际备份导出并解密回读：1000词 → 第二取消后1000词（词集合完全一致）→ 授权导入后2000词，1000个本轮新测试词全部存在。真实下载、解密、预览、授权导入均已执行。第一确认草稿/密码显隐、自动同步开关保存与禁用后恢复亦通过。', '',
    '环境：设备127.0.0.1:5555，emulator 6.1.0.115(SP11DEVC00E115R4P11)/API23；1308×2880@60、density3.5；Hypium6.1.0.210/Python3.12.3/hdc3.2.0c。设备仅报告model=emulator，未独立确认具体Pura型号。dpi参数读取1002失败，实际密度使用DisplayManager原始输出核对。', '',
    '## 逐需求矩阵', '',
    'pass仅指记录范围；A24/A25/A31按批准复审E/T07作探索观察，活动中生命周期子项明确not_run。', '',
    '| 条目 | 状态 | 范围及证据限制 |',
    '| --- | --- | --- |',
]
for item in matrix:
    text = item['scope'] + ('；限制：' + item['limitations'] if item['limitations'] else '')
    lines.append(f"| {item['id']} | {item['status']} | {text} |")
lines.extend([
    '', '机器矩阵的逐项证据索引见 `implementation-round-02.json`。A20整体记not_run，三个无数据子例通过，但“备份未更新”未设备实测。', '',
    '预览pending、保存失败/拒绝、导入失败/拒绝等难触发分支另有7组实际提取Section方法的受控依赖检查通过；这属于Node源码级证据，不能代替ArkTS VM/UI/网络/存储实测。Section在round02未改，原始源指纹仍一致。未做同一挂载视图的主题重渲染。', '',
    '## 失败留存、清理与交接', '',
    'run01–03确认产品缺陷VG15_CURRENT_FORM_RESET_ON_FIRST_CONFIRM；批准View实时getter修复后，run09保留草稿回归通过。run04输入辅助Back误退、run06/07原生弹窗时序及快速外部点按合同问题均保留原始失败；经需求复审修正测试合同和稳定等待，run08受影响项通过，再执行最终完整09。未覆盖或覆盖失败均未删除断言冒充通过。run06导入后测试文件曾修改，缺少同期归档，只有明确标注的重建版本；最终09前后完整归档无此歧义。', '',
    '自身127.0.0.1:18165服务已停止；自身9个Hypium转发及服务映射均清理，原有3个转发保留。仅在核对绝对路径后逐项非递归删除生成的5个.pyc及空缓存目录，所有原始失败、截图、日志、测试归档保留。`cleanup-final.json`、`test-cache-cleanup.json`及原始命令日志可复核。无tracked构建噪声；未回退其他角色文件。', '',
    '**设备租约已释放给Root**，不再执行设备命令。模拟器保留当前HAP、虚构loopback配置及测试词；测试夹具只在自测支持/日志中，生产源码未嵌入夹具数据。', '',
    'Root另行完成最终输入/297文件审计；本报告不冒称独立官方验收或隐藏测试结果。', ''
])
(OUT / 'implementation-round-02.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps(dict(report=str(OUT / 'implementation-round-02.md'), machine=str(OUT / 'implementation-round-02.json'),
                      source_equal=True, tests_equal=True, test_cases=outcomes, matrix_items=len(matrix),
                      device_lease='RELEASED', cache_exists=cache['exists_after']), ensure_ascii=False))
