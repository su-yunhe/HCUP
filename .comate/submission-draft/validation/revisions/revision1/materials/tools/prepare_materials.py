"""Prepare task-local materials. Does not modify production files or submit anything."""
from __future__ import annotations

import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[3]
DRAFT = ROOT / '.comate/submission-draft'
COMMON = ROOT.parent / 'common'
TEMPLATES = ROOT.parents[1] / 'SWE-OpenHarmony/templates'
OVERVIEW = '01a13fc4-2611-7761-a580-1283e0c70541'
NOW = datetime.now(timezone.utc)
CAPTURE = 'local-snapshot-' + NOW.strftime('%Y%m%dT%H%M%SZ')

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path: str, value):
    dest = DRAFT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def md(path: str, text: str):
    dest = DRAFT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text.strip() + '\n', encoding='utf-8')

def main():
    state = load(ROOT / 'workflow/state.json')
    frozen = load(ROOT / 'workflow/production-freeze-01.json')
    assert all(sha((ROOT / f['path']).read_bytes()) == f['sha256'] for f in frozen)
    write('validation/production-before.json', frozen)
    base = load(ROOT / 'spec/metadata.json')['base_commit']
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == base
    session_rows = {}
    for entry in state['sessions']:
        if entry.get('session_id') and entry['session_id'] != OVERVIEW:
            session_rows[entry['session_id']] = entry
    native_root = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'sessions'
    raw_sessions = []
    private_values = set()
    for sid, entry in sorted(session_rows.items()):
        paths = list(native_root.rglob('*-' + sid + '.jsonl'))
        assert len(paths) == 1, (sid, paths)
        data = paths[0].read_bytes()
        # An active JSONL tail is not a completed record. Preserve only complete lines.
        data = data[:data.rfind(b'\n') + 1]
        records = [json.loads(line) for line in data.decode('utf-8').splitlines()]
        meta = records[0]['payload']
        assert meta['id'] == sid
        assert meta['cwd'].replace('\\', '/').lower().rstrip('/') == ROOT.as_posix().lower()
        for key in ['creator_user_id', 'creator_account_id']:
            if meta.get(key):
                private_values.add(meta[key])
        # Two independent retrieval dimensions, confined to these registered files.
        path_hits = [i for i, line in enumerate(data.decode('utf-8').splitlines(), 1)
                     if str(ROOT).lower() in line.lower() or ROOT.as_posix().lower() in line.lower()
                     or str(ROOT).replace('\\', '\\\\').lower() in line.lower()]
        task_hits = [i for i, line in enumerate(data.decode('utf-8').splitlines(), 1) if 'vg-spec8' in line.lower()]
        assert path_hits and task_hits, sid
        raw_sessions.append((sid, entry, paths[0], data, records, path_hits, task_hits))

    def sanitize(data: bytes):
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            return data, []
        changes = []
        for value in sorted(private_values):
            count = text.count(value)
            if count:
                text = text.replace(value, '[REDACTED_ACCOUNT_IDENTIFIER]')
                changes.append({'kind': 'account_identifier', 'occurrences': count})
        # Replace only the observed environment value prefix, never JSON delimiters
        # or the remainder of a serialized tool-output record.
        text, count = re.subn(r'MCowBQYDK2VwAyEA[A-Za-z0-9+/=]+',
                              '[REDACTED_EPHEMERAL_VERIFICATION_VALUE]', text)
        if count:
            changes.append({'kind': 'ephemeral_workspace_verification_value', 'occurrences': count})
        return text.encode('utf-8'), changes

    write('validation/redaction-rules.json', {
        'account_identifiers': 'creator_user_id / creator_account_id values from the selected task session headers, including exact repeats in text',
        'ephemeral_environment': 'observed MCowBQYDK2VwAyEA-prefixed verification environment values only',
        'source_paths_code_tools_results': 'retained; no masking of source URLs, modification basis or failure evidence',
        'test_credentials': 'task-local sentinel values retained; no real server account used in tests',
    })
    # This local helper data is used only by the snapshotter; no credential values stored.
    write('validation/context.json', {
        'capture_id': CAPTURE, 'captured_at_utc': NOW.isoformat(),
        'captured_at_beijing': NOW.astimezone(timezone(timedelta(hours=8))).isoformat(),
        'base_commit': base, 'overview_excluded': OVERVIEW,
        'comate_index_exists': (Path.home() / '.comate-engine/store/comate_chat_sessions.jsonl').exists(),
        'official_prepare_log_exists': (ROOT.parents[1] / 'SWE-OpenHarmony/reports/build-baselines/vg-spec8.log').exists(),
        'codex_desktop_version': '26.1007.2314.0',
        'desktop_version_evidence': 'Get-AppxPackage -Name OpenAI.Codex in this task native trace',
    })
    trace_index = []
    tool_index = []
    redactions = []
    for sid, entry, path, original, records, path_hits, task_hits in raw_sessions:
        clean, edits = sanitize(original)
        dest = DRAFT / 'traces/native' / (sid + '.jsonl')
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(clean)
        clean_records = [json.loads(line) for line in clean.decode('utf-8').splitlines()]
        meta = clean_records[0]['payload']
        models = []
        token = None
        calls = collections.Counter()
        out = [f'# 原生记录可读副本 {sid}', '',
               '由本题 JSONL 机械转换，不是 IDE 人工导出；原始提示、调用及返回以 native 文件为准。', '']
        for line_no, record in enumerate(clean_records, 1):
            payload = record.get('payload', {})
            kind = record.get('type')
            if kind == 'turn_context':
                item = {'model': payload.get('model'), 'effort': payload.get('effort')}
                if item not in models:
                    models.append(item)
            if kind == 'event_msg' and payload.get('type') == 'token_count' and payload.get('info'):
                token = payload['info'].get('total_token_usage')
            if kind == 'response_item' and payload.get('type') in ['function_call', 'custom_tool_call']:
                calls[payload.get('name', '')] += 1
                tool_index.append({'thread_id': sid, 'line': line_no, 'timestamp': record.get('timestamp'),
                                   'tool': payload.get('name'), 'call_id': payload.get('call_id')})
            # Reasoning/compaction records remain in native JSONL; the readable copy
            # mechanically includes all records, including call arguments and results.
            out.extend([f'## JSONL line {line_no} / {kind} / {record.get("timestamp", "")}', '',
                        '```json', json.dumps(record, ensure_ascii=False, indent=2), '```', ''])
        md('traces/markdown/' + sid + '.md', '\n'.join(out))
        item = {'thread_id': sid, 'native_session_id': meta.get('session_id'),
                'parent_thread_id': meta.get('parent_thread_id'), 'role': entry['role'],
                'agent_path': meta.get('agent_path'), 'cli_version': meta.get('cli_version'),
                'originator': meta.get('originator'), 'started_at': meta.get('timestamp'),
                'native_file': 'traces/native/' + sid + '.jsonl',
                'markdown_file': 'traces/markdown/' + sid + '.md',
                'source_path': str(path), 'source_complete_prefix_bytes': len(original),
                'source_prefix_sha256': sha(original), 'export_sha256': sha(clean),
                'records': len(clean_records), 'models': models, 'last_cumulative_token_usage': token,
                'token_scope_note': 'native total_token_usage snapshot; cache is a subset of input; do not infer billing or sum repeated cumulative events',
                'tools': dict(calls), 'source_path_match_lines': path_hits,
                'task_id_match_lines': task_hits, 'active_prefix_snapshot': sid in {
                    '01a14501-8f22-73b2-b107-150ed01e18bb', '01a14549-2c5d-70c0-ab26-64feca32bde8'}}
        trace_index.append(item)
        if edits:
            redactions.append({'file': item['native_file'], 'source_sha256': sha(original),
                               'export_sha256': sha(clean), 'changes': edits})
    write('traces/session-index.json', trace_index)
    md('traces/session-index.filtered.jsonl', '\n'.join(json.dumps(x, ensure_ascii=False) for x in trace_index))
    md('traces/tool-index.jsonl', '\n'.join(json.dumps(x, ensure_ascii=False) for x in tool_index))
    write('traces/redaction-ledger.json', redactions)
    write('traces/retrieval.json', {
        'method': 'Only registered vg-spec8 session UUID filename matches; then independently verify cwd and task-id hits within each selected native JSONL',
        'searched_dimensions': ['absolute project cwd/path', 'task_id vg-spec8'],
        'unrelated_session_contents_read': False, 'whole_client_database_exported': False,
        'comate_index': 'not present; no Comate sessionUuid or Comate IDE id invented',
        'overview_exclusion': {'id': OVERVIEW, 'reason': 'shared initialization overview includes other tasks; no full overview content exported'},
        'limitations': ['Does not establish absence of undiscovered sessions outside registered task UUIDs',
                       'Live parent/material-review sessions are complete-prefix snapshots, not future or final post-export turns',
                       'IDE Markdown export directory was not supplied; readable copies are generated conversions'],
    })
    # Copy task logs. Exclude only known unrelated pre-install UI, and caches.
    copied = []; excluded = []
    for src in sorted((ROOT / 'logs').rglob('*')):
        if not src.is_file():
            continue
        rel = src.relative_to(ROOT / 'logs')
        reason = None
        if src.name in {'00-before-install.png', '00-before-install.json'} and rel.parts[0] == 'analysis-baseline':
            reason = 'Pre-install screenshot/tree belongs to prior unrelated device screen, per baseline-notes; not this task evidence'
        if '__pycache__' in rel.parts or src.suffix.lower() in {'.pyc', '.pyo'}:
            reason = 'generated Python cache, not original interaction evidence'
        if reason:
            excluded.append({'path': 'logs/' + rel.as_posix(), 'bytes': src.stat().st_size,
                             'sha256': sha(src.read_bytes()), 'reason': reason})
            continue
        data = src.read_bytes(); clean, edits = sanitize(data)
        dest = DRAFT / 'logs' / rel
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(clean)
        copied.append({'path': 'logs/' + rel.as_posix(), 'source_sha256': sha(data),
                       'export_sha256': sha(clean), 'bytes': len(clean), 'redactions': edits})
    write('logs/copy-manifest.json', {'files': copied, 'excluded': excluded})
    artifacts = DRAFT / 'artifacts'; artifacts.mkdir(exist_ok=True)
    hap = ROOT / 'entry/build/default/outputs/default/entry-default-unsigned.hap'
    shutil.copy2(hap, artifacts / hap.name)
    write('changes/build-artifact.json', {'path': 'artifacts/' + hap.name, 'bytes': hap.stat().st_size,
                                         'sha256': sha(hap.read_bytes()), 'kind': 'tested generated HAP, not new application resource'})
    taskbooks = []
    for name in ['0-analyze.md', '1-do.md', '2-submit.md', '3-package.md']:
        p = COMMON / 'spec-harness' / name
        row = {'common_path': 'common/spec-harness/' + name, 'sha256': sha(p.read_bytes())}
        local = ROOT / 'spec-harness' / name
        if local.exists():
            row['task_copy_sha256'] = sha(local.read_bytes()); row['same_as_common'] = row['sha256'] == row['task_copy_sha256']
        taskbooks.append(row)
    write('provenance/taskbook-version.json', {'common_is_own_git_checkout': (COMMON / '.git').exists(),
                                               'files': taskbooks, 'spec_history_exists': (ROOT / 'spec/history').exists()})
    for name in ['submission-checklist.md', 'trace-index.md', 'submission.json']:
        data = (TEMPLATES / name).read_bytes(); dest = DRAFT / 'provenance/templates' / name
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
    write('provenance/template-hashes.json', [{'path': n, 'sha256': sha((TEMPLATES / n).read_bytes())}
                                            for n in ['submission-checklist.md', 'trace-index.md', 'submission.json']])
    write('provenance/client.json', {'client': 'Codex Desktop', 'desktop_appx_version': '26.1007.2314.0',
                                    'native_cli_version': '0.162.0-alpha.17.2',
                                    'model_and_effort_observed': 'gpt-6.1-sol / xhigh',
                                    'independent_model_build_version': '【待补充】',
                                    'comate_engine_sessionUuid': 'not applicable: Comate not used/index not present',
                                    'comate_ide_sidebar_id': 'not applicable: Comate not used',
                                    'codex_sidebar_thread_id': '01a14501-8f22-73b2-b107-150ed01e18bb',
                                    'sidebar_evidence': 'Codex read_thread returned thread.id and cwd in current native trace'})
    # No inferred user declarations. These remain pending even when observed facts exist.
    pending = [
        ('team.version', 'common/spec-harness/team.yaml', '成果包版本'),
        ('team.contact', 'common/spec-harness/team.yaml', '联系人姓名及邮箱/电话'),
        ('team.freeze_time', 'common/spec-harness/team.yaml', '团队成果冻结时间，北京时间；本地快照时间不能代填'),
        ('team.members[].name / work', 'common/spec-harness/team.yaml', '人员及实际分工'),
        ('team.source_guard', 'common/spec-harness/team.yaml', '团队来源保护措施声明；本题实际配置另列'),
        ('task.human_edits', 'spec/submit-input.yaml', '人工直接改代码声明或逐批证据'),
        ('task.known_issues', 'spec/submit-input.yaml', '用户补充的已知问题；本地客观限制另列'),
        ('task.extra_sources', 'spec/submit-input.yaml', '额外来源声明；已观察来源另列'),
        ('task.md_export_dir', 'spec/submit-input.yaml', 'IDE侧边栏人工Markdown导出目录；已生成JSONL可读转换副本'),
        ('team.submitted_tasks / attempted_not_submitted / zip_out', 'common/spec-harness/team.yaml', '仅3-package使用，不推断团队其他题或输出路径'),
    ]
    md('pending-fields.md', '# 仍需补充的字段\n\n| 字段 | 当前值 | 原始输入 | 需要补充 |\n| --- | --- | --- | --- |\n' +
       '\n'.join(f'| `{key}` | 【待补充】 | `{source}` | {why} |' for key, source, why in pending) +
       '\n\n其他缺失/不适用：Comate双ID本次不存在，不能补造；官方指定基线准备日志路径不存在，仅有本题实际准备记录；未取得独立模型构建版本和Comate扩展版本。活跃会话只导出到明确截点，3-package冻结时需保存之后的新记录。\n\n自动测试保留固定开发机ROOT与安装清单门槛，本阶段未改；若需任意目录自动重跑，须另行适配测试脚本。当前手工场景及App构建命令可按build.md复现。')
    md('build.md', '''# vg-spec8 构建与运行

本题项目目录为成果包内 `tasks/vg-spec8/project/`；在该目录执行以下命令。构建App不依赖参赛电脑的私有环境脚本。工具由使用者安装并加入 PATH。

## 环境与依赖

实测工具：DevEco Studio 6.1.0.860，SDK 6.1.0.105 / API 23；工程 targetSdkVersion、compatibleSdkVersion 为 `6.0.2(22)`。Node 18.20.1、JBR/OpenJDK 21.0.8、Hvigor 6.23.7、HDC 3.2.0c。设备为 API 23、系统6.1.0.115、1308×2880模拟器。OHPM与Python的历史精确版本尚未核实，记【待补充】，不得猜测。

根 `oh-package.json5` 与 `oh-package-lock.json5` 固定 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`，锁版本3。entry模块没有新增外部依赖。安装依赖、构建：

```powershell
ohpm install
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
```

若系统使用 `hvigorw` 命令，去掉 `.bat` 后缀即可；需先配置SDK、JDK、Node与OHPM工具环境。原始构建记录见 `logs/implementation-validation/round-01/build-clean-assembleHap.log`，exit0；764条既有ArkTS告警，新增0。生产源码未在材料阶段重建或修改。

## 安装和启动

应用 `io.qzz.weiyu`，模块 `entry`，入口 `EntryAbility`，版本1.0.0。调试产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。原项目签名配置为空，实测模拟器允许此unsigned HAP；其他设备如需签名，须使用其合法配置，包内没有私钥。

```powershell
hdc list targets
$device = '127.0.0.1:5555' # 改为实际列出的目标序列号
hdc -t $device install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $device shell bm dump -n io.qzz.weiyu
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
```

安装需同时检查成功文本和bm updateTime，不能只信退出码；实测某些HDC文件路径失败时仍返回0。被测HAP SHA256 为 `c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229`，材料 `artifacts/` 保留该产物。

## 初始化与手工复现

首次安装如出现隐私/引导，按实际页面完成；本题功能不要求应用账号登录。首页齿轮→设置→「WebDAV 配置」，滚动到手动操作区。可先使用空配置验证确认与取消；证明网络门槛时应保存有效、可达的独立测试端点，并持久关闭自动同步，确保没有在途请求。

点击「从云端恢复」，观察第一层「取消／继续」。点击「取消」后弹层关闭、仍回到WebDAV操作区，恢复按钮原文且可用；再次打开、反复取消，未明确点本轮「继续」前所有HTTP方法累计请求应为0。系统返回/遮罩关闭亦不授权。不要点击测试连接、同步或备份污染计数。独立点「继续」后才允许现有下载/预览流程，云端无备份时可返回原有失败结果；后续覆盖确认保持原行为。

## 自测证据和复现边界

本地Python Hypium为6.1.0.210，测试类继承公共HarnessTestCase。工程保留 `test-harness/` 框架副本、`hypium_tests/`、逐轮原始日志、测试脚本快照和源码/安装清单。完整轮4pass/2skip，补测4pass/0skip，合并6个唯一方法均有真实pass。20个空/空格保存与未保存边界、重复点击、返回/重启、空数据、非空哨兵及真实请求正控均有记录。

**自动脚本移植限制**：`hypium_tests/run_validation.ps1` 含开发机工具/工程路径，`verification_support.py` 另有固定ROOT检查和本轮manifest/HAP/源码指纹门槛。它们原样保留以对应历史证据，不能仅换成相对runner命令就声称任意目录可自动重跑。本阶段禁止修改脚本；后续适配须单独完成并重测。App本身可使用上述PATH命令构建、安装、手工复现。

未测：官方隐藏用例、D2预览取消/完整成功恢复、自动同步并发。自动同步关闭是本地测量隔离前置，不是全局并发零请求的证明。
''')
    md('human-changes.md', '''# 人工操作及修改声明

用户输入 `spec/submit-input.yaml` 的 `human_edits` 为空：**【待补充】**。不能把未观察到人工编辑等同于“无人工直接修改代码”。如有人工修改，请补操作人、目的、文件、修改前后版本和当时留存证据；不创建伪造的历史差异。

可核实观察：本题原生编码会话 `01a1450b-f62c-7710-8bcd-0c24be8870be` 的工具调用证明AI执行了五文件实现；需求、方案、验证由相应原生子会话完成。初始化前已有AGENTS调度规则增补，见setup记录及初始指纹；不能只凭总体diff推断所有修改作者。分析阶段有用户允许使用空闲共享设备的提示，原文在分析主会话。当前材料阶段没有人工改代码操作由本Agent执行，也没有业务文件修改。

这些客观事实不能替代待补充的团队声明。完整差异在 `changes/final.diff`；原始会话见 `traces/session-index.json`。
''')
    md('sources.fragment.md', '''# vg-spec8 来源片段

随包基线：本题 `spec/metadata.json` 指定 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，bundle标识 `repo_bundles/vignette-9cbcf7292c-base.bundle`。原有代码、资源、依赖与文档来自该基线，不声明为本次原创；没有从来源应用上游当前实现或相关修复历史获取本功能代码。基线来源与文件摘要见project中的 `workflow/baseline-provenance.json`。

用户的 `extra_sources` 声明为空：**【待补充】**。以下是本题记录已直接证实的额外技术资料，不代填用户声明：

| 来源 | 实际用途与记录 |
| --- | --- |
| OpenHarmony docs master原始CustomDialog文档：https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 方案会话原生JSONL第84行open、第87行返回；实际打开过，予以披露 |
| OpenHarmony 6.0 Release文档：https://raw.githubusercontent.com/openharmony/docs/OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 同会话100/104行open与返回，108/112行查成员；官方通用API资料 |
| 6.0文档GitHub页面：https://github.com/openharmony/docs/blob/OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 设计报告引用同一文档页面，未取应用来源实现 |
| 本地SDK CustomDialog声明、ArkTS enum/初始化/迁移指南、linter CLI声明、公共Harness | 见project/workflow/design/implementation-plan-01.md第10节、原生调用；用于语法/API/测试框架 |
| harmony-task-flow 与四角色、ArkTS相关Skills | project/system-config既有快照；本阶段未改团队配置 |

以上方案会话为 `01a14503-4b1d-7e70-943e-a0d57c675547`，原生文件位于本材料traces/native同名JSONL。搜索回包中还包含通用文档Issue等命中；命中回包完整保留，不把未点击的全部命中当实际引用。检索工具缺索引失败、后续直接读取文档的过程均保留。依赖版本和registry URL见project/oh-package-lock.json5。

新二进制材料是本题测试截图、只读数据库哨兵快照和生成HAP；未新增App二进制素材。`changes/binary-manifest.json`逐项列路径、大小、SHA及基线同源判断。混合初始化总览与非本题安装前UI不交付，范围见trace-index和排除清单。
''')
    md('solution.fragment.md', f'''# vg-spec8 完成情况片段

团队HC2026-111 / Ghost_London，阶段online。团队成果版本、联系人、人员分工及正式冻结时间：**【待补充】**。本地技术快照标识 `{CAPTURE}` 只用于对应文件清单，不代替团队正式版本或冻结时间。

本题完成WebDAV恢复的第一层确认：取消关闭并可重开；仅明确继续且关闭完成后进入原恢复流程。沿用既有路由、管理器、存储与下载后的D2。新增确认组件和配置拆分，入口补稳定id。

AI实际参与：分析主会话与需求/方案/只读编码审计/基线验证；实施主会话与需求复审、方案、唯一编码、独立验证；本轮四角色只做材料审查。原始ID、模型和工具见traces/session-index.json。实际模型记录gpt-6.1-sol，effort=xhigh；未取得独立模型构建号。无需推算代码贡献比例。用户human_edits、known_issues、extra_sources仍【待补充】，客观事实单列。

本地A1—A19全部pass，其中A1—A14明文、A15—A19合理推导。完整轮4pass/2skip，受影响补测4pass/0skip消除哨兵前置跳过，六方法均有真实pass；不是单轮六项全过。138个未授权计数点增量0；明确继续后各3条HEAD；非空哨兵实体一致。构建exit0，764旧告警、新增0，258输入测试前后一致。

客观限制：官方隐藏测试、D2预览取消/完整成功恢复、自动同步并发未测；非空数据只覆盖1条测试词书，其余学习表为空；既有SettingsPage超过500行、旧告警与超时未取消底层任务未扩改。自动自测固定开发机ROOT和manifest门槛，不可宣称任意目录一键复现；本阶段不改脚本。

团队级来源保护声明source_guard【待补充】；本题实际限定目录、禁止其他题与上游修复等规则在project/AGENTS.md、system-config已有快照及原生派工中。没有对外上传、发邮件或提交赛事成果；根solution/sources/README、团队配置和ZIP由3-package处理。
''')
    write('submission.json.fragment', {'task_id': 'vg-spec8', 'status': 'submitted',
          'project_path': 'tasks/vg-spec8/project', 'build_instructions': 'tasks/vg-spec8/build.md',
          'trace_index': 'tasks/vg-spec8/trace-index.md'})
    facts = [
        ('团队/阶段/题号', 'HC2026-111 / Ghost_London / online / vg-spec8', 'common/spec-harness/team.yaml；spec/submit-input.yaml'),
        ('官方基线', base, 'spec/metadata.json；本地base/vg-spec8解析'),
        ('应用与入口', 'io.qzz.weiyu / entry / EntryAbility', 'AppScope/app.json5；entry/src/main/module.json5'),
        ('依赖锁/SDK', 'Hypium1.0.24、hamock1.0.0；锁3；target/compatible22', 'oh-package*.json5；build-profile.json5'),
        ('构建及告警', 'exit0；764条旧告警，新增0', 'logs/implementation-validation/round-01/build-result.json、warning-comparison.json'),
        ('自测', 'A1—A19本地pass；6方法分轮真实pass；138点零请求', 'logs/selftest.json；workflow/final-evidence-check.json；两轮原始报告'),
        ('生成HAP', 'SHA256 c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229', '实际产物重新hash；changes/build-artifact.json'),
        ('实际准备记录', 'harmony-cup-build-v1；dry_run=false；changes=[]；官方规定路径不存在', 'logs/prepare-baseline.log；workflow/setup-result.json；本轮文件存在性检查'),
        ('客户端/CLI/模型', 'Codex Desktop26.1007.2314.0 / CLI0.162.0-alpha.17.2 / gpt-6.1-sol xhigh', 'Get-AppxPackage输出；原生session_meta与turn_context'),
        ('会话映射/用量', '逐会话id、session_id、parent、tokenUsage记录', 'traces/session-index.json；原生JSONL逐字段'),
        ('公共任务书版本', '四文件SHA256；本题副本同异另列；无spec/history', 'provenance/taskbook-version.json'),
        ('来源/人工客观边界', 'AI写入证据与实际API文档访问；不代填人工声明', 'sources.fragment.md；human-changes.md；原生工具调用'),
        ('完整差异/二进制/对应', '全冻结project文件；仅派生容器/缓存/跨题内容排除', 'changes/project-manifest.json、binary-manifest.json、patch-manifest.json；validation/apply-check.json'),
    ]
    md('auto-facts.md', '# 已自动填入的事实及出处\n\n| 事实 | 已填写内容 | 出处 |\n| --- | --- | --- |\n' +
       '\n'.join(f'| {name} | {value} | `{source}` |' for name, value, source in facts) +
       '\n\n正式团队冻结时间、版本和人工声明仍未提供；没有用本地技术快照时间代填。')
    labels = [line[2:].split('：', 1)[0] for line in (TEMPLATES / 'trace-index.md').read_text(encoding='utf-8-sig').splitlines() if line.startswith('- ')]
    assert len(labels) == 24
    values = [
        'vg-spec8',
        '需求分析、基线观察、方案、实现、独立自测、提交材料；逐线程/工具事件见traces/session-index.json、tool-index.jsonl和原生JSONL；AI实际参与不以摘要代替原始记录。',
        '实际日志project/logs/prepare-baseline.log：profile=harmony-cup-build-v1、dry_run=false、changes=[]；project/workflow/setup-result.json记录pass。官方reports/build-baselines/vg-spec8.log不存在；脚本精确执行时刻【待补充】，prepared_at仅汇总时间。',
        'Codex Desktop 26.1007.2314.0，CLI0.162.0-alpha.17.2；四原生角色名称/版本配置见project/system-config与session_meta。Comate未使用，扩展版本不适用。',
        '原生turn_context记录gpt-6.1-sol、effort=xhigh；独立模型构建版本【待补充】；累计tokenUsage原字段与口径见traces/session-index.json，不把缓存输入与总输入重复相加。',
        '既有project/system-config/initial-*及implementation-*；native session_meta/turn_context保留实际提示规则；traces/tool-index.jsonl列实际工具调用；本阶段不生成团队system-config。',
        '历史配置及分析/实现阶段变更见project/workflow/state.json与既有system-config；材料阶段未改生产规则/资源/构建配置，仅加本地材料与调度记录。',
        'Codex主线程：分析01a144eb-32eb-7cb3-b4d6-daea0ae599b7，实施/材料01a14501-8f22-73b2-b107-150ed01e18bb。Comate引擎sessionUuid【待补充：本次未使用Comate，无法提供】；Comate IDE侧边栏ID【待补充：不适用】。Codex原生session_meta.session_id与id分别列在session-index；read_thread核实当前侧边栏thread.id等于后者。子会话session_id可继承主会话，不冒充Comate双ID。',
        '全部本题登记子会话见traces/session-index.json（含四角色分析、实现及材料复审）；跨题初始化总览01a13fc4-2611-7761-a580-1283e0c70541不整体提交。',
        'traces/native/*.jsonl，UTF-8逐行JSON；traces/markdown/*.md为机械可读副本；traces/session-index.filtered.jsonl为本题过滤索引；代码快照见traces/code-changes/及冻结project。未提交整个客户端DB。',
        '原生调用与返回、project/workflow/events.jsonl、各阶段报告及logs/的所有本题失败/重试；包含提前联网基线失败、hdc假成功、Ability/滚动适配、哨兵前置skip及补测。',
        'traces/native、tool-index.jsonl；project/workflow/design/implementation-plan-01.md；project/logs/analysis-baseline与implementation-validation；changes/final.diff及代码快照。',
        f'本地技术导出截点 {NOW.isoformat()}；tools/prepare_materials.py按登记UUID取原生完整行前缀，分别核对工程路径与题号；账户标识/临时环境验证值脱敏后原生JSON格式保留。活跃会话之后产生的尾部不在该截点内。',
        '【待补充】（team.freeze_time为空；不得用本地技术快照或导出时间代填团队成果冻结时间）',
        f'官方基线{base}；当前Git HEAD仍为该基线并有未提交变更，未伪造最终commit。最终技术版本标识{CAPTURE}，以changes/project-manifest.json全文件摘要定义。团队version【待补充】。',
        'changes/final.diff（--binary、完整新增修改删除）；changes/binary-manifest.json逐项路径/字节/SHA及基线同源判断，真实文件保留在冻结project。补丁与其派生manifest位于project之外，避免自引用。',
        '3-package必须复制本目录project/为tasks/vg-spec8/project，不能重新扫描活动工程。冻结时的普通.comate材料也纳入；仅project/changes/validation派生容器、缓存和明确跨题原文排除，见changes/exclusions.json。验证基线check+真实apply并逐文件比对，见validation/apply-check.json。业务258指纹与1-do冻结一致。',
        'human-changes.md；用户提示和共享设备允许记录在分析主会话；本Agent本轮只整理材料，不进行业务写入。实际人工操作人声明【待补充】。',
        'human-changes.md；spec/submit-input.yaml的human_edits为空，仍【待补充】，不擅自写“无人工直接修改代码”。',
        '【待补充】操作人/目的/文件/前后版本/当时证据。可观察AI工具修改记录另见编码native，不据此否定未知人工编辑。',
        'sources.fragment.md（供根sources.md汇总）；设计原生线程包含通用OpenHarmony master和6.0 CustomDialog文档读取，SDK/ArkTS资料及公共框架。extra_sources用户声明【待补充】。',
        '实际工作目录D:/HCUP/vg-spec8；本题AGENTS/原生派工/既有system-config记录只读common、禁止其他题及上游相关修复。团队source_guard声明【待补充】，不以机器观察代填。',
        'traces/redaction-ledger.json及validation/redaction-rules.json：只处理选中会话header账户标识及精确重复、临时环境验证输出；源URL/代码/失败/依据不遮蔽。跨题总览和安装前非本题UI直接排除并记录hash/理由；原机文件不改。',
        'Comate双ID/数据库未使用；IDE人工Markdown未提供（已生成原生转换）；官方指定prepare日志缺失（本题实际日志存在）；共享总览未整体导出，未证明可覆盖其所有本题初始化原始事件；活跃材料会话截点后的尾部待3-package再冻结。独立模型构建版本/用户空字段【待补充】。检索只限登记UUID，不能证明不存在未登记会话。',
    ]
    assert len(values) == 24
    md('trace-index.md', '# 运行记录索引\n\n' + '\n'.join('- ' + label + '：' + value for label, value in zip(labels, values)))
    md('PACKAGING-HANDOFF.md', f'''# 单题材料交接与边界

本目录是本地提交草稿，尚未上传、发邮件、创建ZIP或提交Git。团队级文件与最终打包由3-package处理。

技术快照标识：`{CAPTURE}`；技术捕获时间 `{NOW.astimezone(timezone(timedelta(hours=8))).isoformat()}`。团队正式version/freeze_time等仍【待补充】。

| 本目录内容 | 3-package目标 |
| --- | --- |
| project/ | tasks/vg-spec8/project/（只复制该冻结副本） |
| build.md、trace-index.md、human-changes.md | tasks/vg-spec8/下同名文件 |
| changes/ | tasks/vg-spec8/changes/ |
| traces/、logs/、artifacts/ | tasks/vg-spec8/下同名目录，可保留一份并使用相对引用 |
| sources.fragment.md、solution.fragment.md、submission.json.fragment | 汇入团队根文件，不替代25题完整清单 |
| pending-fields.md、auto-facts.md、validation/的最终JSON/MD | 供人工补全与校验审阅；不复制临时clone/.git/缓存 |

**差异完整性口径**：冻结副本包含本工程所有真实文件、spec、hypium_tests、日志、轨迹、既有system-config以及冻结时的普通.comate材料；不是五文件补丁。仅排除本材料的递归输出子树project/、changes/、validation/，以及.git、已登记缓存/私有环境、明确跨题内容。补丁无法包含自身字节；这些派生输出独立放在project外，排除清单逐项公开。禁止后来把整个submission-draft再塞回project。

工程清单与最终diff/二进制摘要见changes/；validation/apply-check.json记录从本地官方基线clone、checkout、check、真实apply及全文件哈希比较。临时clone禁用文本/过滤器归一化，保留工程物理字节，因而补丁可能包含既有CRLF相对Git blob的字节差异；不代表材料阶段修改业务文件。

共享初始化总览含其他题，原文不提交；本题所有失败/重试保留。根输入中的人工声明与extra_sources未填，不据工具观察擅自作有利认定。构建说明仅使用PATH和包内相对路径；自动化脚本的固定ROOT限制如实披露。

冻结后产生的主会话/独立材料审核记录可能未包含在project快照中；3-package重新收尾导出并新增外置材料记录即可。若变更工程文件集、源码或项目内过程文件，须重做完整diff与apply比较，不得沿用旧校验。当前不是可直接对外提交的最终团队ZIP。
''')
    # Exports contain no input field values that were blank and guessed.
    write('validation/material-preparation.json', {'capture_id': CAPTURE, 'sessions': len(trace_index),
          'copied_log_files': len(copied), 'excluded_log_files': len(excluded), 'native_redacted_files': len(redactions),
          'trace_index_fields': len(labels), 'business_input_count_unchanged': len(frozen)})
    print(json.dumps({'capture_id': CAPTURE, 'sessions': len(trace_index), 'copied_logs': len(copied),
                      'trace_fields': len(labels), 'business_files_unchanged': len(frozen)}, ensure_ascii=True))

if __name__ == '__main__':
    main()
