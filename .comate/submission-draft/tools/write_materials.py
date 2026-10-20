"""Render submission fragments from verified local evidence, leaving unknowns explicit."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'
PENDING = '【待补充】'


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(name, text):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8')


def save(name, value):
    write(name, json.dumps(value, ensure_ascii=False, indent=2))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inv = load(OUT / 'checks/evidence-inventory.json')
    frozen = load(OUT / 'changes/project-manifest.json')
    validation = load(OUT / 'checks/diff-validation.json')
    binaries = load(OUT / 'changes/binary-files.json')
    base = frozen['base_commit']
    snapshot = frozen['snapshot_path']
    prefix = snapshot + '/'
    task = load(ROOT / 'spec/metadata.json')
    # The input files intentionally use a very small scalar YAML subset.
    def input_scalars(path):
        values = {}
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            match = re.match(r'^([a-z_]+):\s*"([^\"]*)"', line)
            if match:
                values[match.group(1)] = match.group(2) or PENDING
        return values
    team = input_scalars(ROOT.parent / 'common/spec-harness/team.yaml')
    user = input_scalars(ROOT / 'spec/submit-input.yaml')
    # Copy every existing log, byte for byte; original failure records remain in project/traces too.
    copied_logs = []
    for source in sorted((ROOT / 'logs').rglob('*')):
        if source.is_file():
            relative = source.relative_to(ROOT / 'logs')
            target = OUT / 'logs' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied_logs.append({'path': 'logs/' + relative.as_posix(), 'bytes': source.stat().st_size,
                                'sha256': sha(source), 'source': 'project/logs/' + relative.as_posix()})
    save('checks/copied-log-manifest.json', copied_logs)
    save('checks/verified-input-fields.json', {'team': team, 'task': user, 'members': PENDING})

    write('build.md', r'''
# vg-spec9 构建、安装与自测

以下命令从成果包内 `tasks/vg-spec9/project/` 执行。此文件使用工程相对路径和评测机的环境变量，不依赖参赛机环境脚本。历史日志中的绝对路径属于原始记录，不能照搬执行。

## 环境与依赖

本题实际验证环境为 Windows 11、DevEco Studio 6.1.0.860、API 23 SDK、Python 3.12.3、Python Hypium 6.1.0.210；模拟器系统 `6.1.0.115(SP11DEVC00E115R4P11)`，API23，实读 model 为 emulator，UI 1308×2880。未独立确认 Pura 90 Pro Max 型号或 560 DPI。环境值的原始工具输出可在验证会话 JSONL 与 `checks/prior-evidence-review.md` 定位。框架日志存在 `tracker dependency is not ok` 提示；不宣称环境完全无告警。

`build-profile.json5` 保留随包产品 targetSdkVersion / compatibleSdkVersion `6.0.2(22)`，product=`default`，module=`entry`；使用 API23 工具链验证时没有修改这两个声明。`signingConfigs=[]`。`hvigor/hvigor-config.json5` modelVersion 为 `6.0.2`。

评测机应先安装相应 DevEco、SDK，并将 `DEVECO_STUDIO_HOME` 和 `DEVECO_SDK_HOME` 设置为本机真实安装目录。然后在 PowerShell 初始化当前终端：

```powershell
$ErrorActionPreference = 'Stop'
$studio = $env:DEVECO_STUDIO_HOME
$sdk = $env:DEVECO_SDK_HOME
if (-not $studio -or -not $sdk) { throw '请设置 DEVECO_STUDIO_HOME 和 DEVECO_SDK_HOME' }
$env:JAVA_HOME = Join-Path $studio 'jbr'
$env:NODE_HOME = Join-Path $studio 'tools/node'
$paths = @('jbr/bin', 'tools/node', 'tools/ohpm/bin', 'tools/hvigor/bin') |
  ForEach-Object { Join-Path $studio $_ }
$paths += Join-Path $sdk 'default/openharmony/toolchains'
$paths += Join-Path $sdk 'default/hms/toolchains'
$env:Path = ($paths -join ';') + ';' + $env:Path
$root = (Get-Location).Path
```

根 `oh-package.json5` 的开发依赖为 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`；entry 无新增依赖。保留根 `oh-package-lock.json5` 的版本和 integrity，未新增第三方业务依赖。安装与构建：

```powershell
ohpm install
if ($LASTEXITCODE -ne 0) { throw 'ohpm install failed' }
hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'assembleHap failed' }
```

产物为 `entry/build/default/outputs/default/entry-default-unsigned.hap`。本地独立 clean 构建退出0，见本材料 `logs/build.log`；依赖安装见 `logs/ohpm-install.log`。既有编译告警比较结论为基线759、本轮756，按源文件和消息多重集无净新增；保留签名配置提示，详见工程 `workflow/verification/round-02-final-report.md`。

## 安装、启动与初始化

应用 bundleName=`io.qzz.weiyu`，module=`entry`，入口=`EntryAbility`，srcEntry=`./ets/entryability/EntryAbility.ets`，versionName=`1.0.0`，versionCode=`1000000`。来源分别是 `AppScope/app.json5` 和 `entry/src/main/module.json5`。

```powershell
hdc list targets
$device = '127.0.0.1:5555' # 改为上一条命令实际显示的设备序列号
hdc -t $device install -r './entry/build/default/outputs/default/entry-default-unsigned.hap'
if ($LASTEXITCODE -ne 0) { throw 'install failed' }
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
if ($LASTEXITCODE -ne 0) { throw 'launch failed' }
```

该 unsigned HAP 仅在本机 API23 模拟器实证安装；其他签名策略和实体设备未验证。工程没有提交签名私钥。自测保留原应用数据，首次清数据安装引导未运行，因此不能声称全新安装路径已验收。如首次启动有引导，先正常完成至首页；人工步骤应另行记录。

手动验证：从首页 `⚙` → `WebDAV 配置`，填写可访问端点、账号、密码和目录，点击 `立即同步`。同轮服务端请求未结束时应可见 ArkUI `LoadingProgress`；真实成功或失败结束后收束。只点测试连接不算手动同步证据。

## 可移植 Hypium 复现命令

工程自带 `test-harness/`、`hypium_tests/`，无需原公共目录。先暂停改源码，取得设备独占，并确认宿主18769端口空闲。建立测试环境：

```powershell
python -m venv './build/test-venv'
$python = Join-Path $root 'build/test-venv/Scripts/python.exe'
& $python -m pip install -r './test-harness/requirements.txt'
if ($LASTEXITCODE -ne 0) { throw 'Hypium install failed' }
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = (Join-Path $root 'test-harness') + ';' + $root
$env:HDC_DEVICE = $device
$env:VGSPEC9_PORT = '18769'
$env:VGSPEC9_SOURCE_FROZEN = '1'
$env:VGSPEC9_TESTS = ''
$env:VGSPEC9_EVIDENCE = Join-Path $root 'traces/replay-all'
New-Item -ItemType Directory -Path $env:VGSPEC9_EVIDENCE -Force | Out-Null
hdc -t $device fport ls
# 若尚无18769反向映射，执行下一行；已有匹配映射则跳过。
hdc -t $device fport rport tcp:18769 tcp:18769
```

每次 runner 前重新安装刚构建 HAP，然后从 `logs/` 启动：

```powershell
hdc -t $device install -r (Join-Path $root 'entry/build/default/outputs/default/entry-default-unsigned.hap')
if ($LASTEXITCODE -ne 0) { throw 'install failed' }
Set-Location -LiteralPath (Join-Path $root 'logs')
& $python -m harness.runner --project $root --device $device --json (Join-Path $env:VGSPEC9_EVIDENCE 'selftest.json')
$testExit = $LASTEXITCODE
Set-Location -LiteralPath $root
if ($testExit -ne 0) { throw 'selftest failed; preserve the generated evidence' }
```

默认无筛选发现12项；全套包含真实约264秒请求链，整轮较长。夹具绑定宿主 loopback、自动生成合成测试凭据，逐项关闭自动同步，保存 UI 树、截图、认证匹配、请求/响应时间及上传原字节。必须由设备实际连到宿主夹具，不能用仅切 UI 的假流程替代。测试结束关闭夹具；测试会保存合成配置并保留既有业务数据。

这些可移植命令是对历史运行命令的路径参数化整理，本材料阶段没有再次运行构建或设备测试。历史 `workflow/verification/run_frozen_validation.ps1` 和 `REPRODUCE.md` 仍原样留档，其中参赛机路径不能作为跨机运行入口。

本地12项通过不代表官方隐藏评测成绩；未执行范围见 `solution.fragment.md`。原始失败、自检修正和重试均保留在工程 `traces/implementation-validation/`。
''')

    table = ['| 阶段／角色 | Codex 原生线程 ID（引擎等效标识） | IDE 侧边栏 ID | 对应关系 |', '| --- | --- | --- | --- |']
    token_rows = ['| 原生线程 ID | input_tokens | cached_input_tokens | output_tokens | reasoning_output_tokens | total_tokens | 原生日志行 |', '| --- | ---: | ---: | ---: | ---: | ---: | --- |']
    tool_rows = ['| 原生线程 ID | 实际顶层工具调用名及次数 |', '| --- | --- |']
    for s in inv['sessions']:
        table.append('| ' + s['role'] + ' | `' + s['session_id'] + '` | `' + s['ide_sidebar_session_id'] + '` | ' + s['id_relationship'] + ' |')
        usage = s['last_token_usage']
        tokens = usage['info'].get('total_token_usage', {}) if usage else {}
        token_rows.append('| `' + s['session_id'] + '` | ' + ' | '.join(str(tokens.get(k, PENDING)) for k in ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'total_tokens')) + ' | ' + (str(usage['line']) if usage else PENDING) + ' |')
        tool_rows.append('| `' + s['session_id'] + '` | ' + ', '.join(k + '=' + str(v) for k, v in s['tool_call_counts'].items()) + ' |')
    write('traces/session-map.md', '# 本题会话 ID 对照\n\n本机实际客户端为 Codex Desktop；不存在指定 Comate 库，故没有可核实的 Comate `sessionUuid`，该字段为【待补充／本运行器未产生】。下表保留真实 Codex 原生线程标识及其 IDE 侧边栏关联，不能把它们改称 Comate 字段。主会话 `payload.id` 与过滤索引 `id` 相等；子会话 `payload.id` 是自身 ID，`payload.session_id` 是有侧边栏索引的父会话，`parent_thread_id` 与父调用共同补证。\n\n' + '\n'.join(table) + '\n\n原生字段、父子路径、来源文件和哈希见 `manifest.json`；只有本题匹配索引行被复制到 `filtered-session-index.jsonl`。总览初始化会话未导出。')
    write('traces/token-usage.md', '# 原生 token 计数\n\n以下逐会话取本次快照中最后一条 `event_msg/token_count.info.total_token_usage`，原样保留字段语义。缓存输入是输入的一部分；reasoning 也不额外加到 output。父会话与子会话不相加，不估算计费 token。材料阶段为活动会话截点，后续内容尚未计入。\n\n' + '\n'.join(token_rows))
    write('traces/tool-inventory.md', '# 实际工具和 Skill 证据\n\n' + '\n'.join(tool_rows) + '\n\n顶层 `exec` 包含组合调用，具体 `exec_command`、`apply_patch`、`clock` 等及其参数/返回应按原生日志读取，不能将顶层计数当各嵌套工具次数。原生 `custom_tool_call_output` 也完整保留。失败和重试不会因计数方式而省略。\n\n实际读取过的 Skill：`harmony-task-flow`、`hmos-arkts-knowledge-retriever`、`hmos-arkts-syntax-checker`、`arkts-syntax-assistant`；逐会话路径和实际调用行在 `manifest.json` 的 `tool_evidence` 与 `skill_reference_strings`。其中工具目录检索曾缺 `references/doc_index.json`，随后直接读安装包内 ArkTS 语法文档，见编码交接及原始工具返回。初始 `system-config/` 只保留当时已复制的配置，不声称包含每个 Skill 独立目录的完整历史快照；其他实际读取内容仍在原始会话中。\n\n开发各会话与本材料会话的 `turn_context` 均记录模型 `gpt-6.1-sol`、effort=`xhigh`、approval_policy=`never`、sandbox_policy=`danger-full-access`；更细模型修订号未输出。Skill/角色配置实际内容可由工程 `system-config/initial-20261016T113216Z/` 及会话读文件返回交叉定位。')
    save('traces/manifest.json', {'exported_at_utc': inv['collected_at_utc'], 'snapshot_only': True,
                                  'no_future_events_included': True, 'searches': inv['searches'],
                                  'excluded_candidate_counts': inv['excluded_candidate_counts'], 'sessions': inv['sessions'],
                                  'registered_missing': inv['registered_missing']})

    history = '本工程 `spec/history/` 不存在，未发现历史任务书副本。' if not inv['history_files'] else '历史任务书：' + ', '.join(inv['history_files'])
    taskbook_lines = ['| 文件 | 本题副本与 common 的 SHA-256（当前逐文件相同） |', '| --- | --- |']
    for name, item in inv['taskbook_hashes'].items():
        taskbook_lines.append('| `' + name + '` | `' + item['local_sha256'] + '` |')
    write('taskbook-version.md', '# 实际任务书版本\n\ncommon 所属 Git 仓库当前 HEAD=`' + inv['common_git_commit'] + '`。它是本次整理时读到的版本，不能单凭当前 HEAD 推断历史执行时 Git 状态；四份本题实际留存任务书与 common 当前对应文件逐字节一致，以下摘要同时固定内容。历史会话中读取过的任务书仍以原生调用为准。\n\n' + '\n'.join(taskbook_lines) + '\n\n' + history)

    write('human-changes.md', '# 人工操作与修改记录\n\n人工直接修改代码声明：' + user.get('human_edits', PENDING) + '。`spec/submit-input.yaml` 的 `human_edits` 为空，不能根据 AI 写入痕迹推断“无人工直接修改代码”。操作人、目的、文件、修改前后版本、差异与当时证据均待用户补充或明确声明无。\n\n现有原生主会话包含人类提示及阶段推进请求；独立报告记录测试前已有应用数据、本地合成配置和设备状态，但没有提供可核实的人工登录、引导或逐次设备操作人清单，不能填造姓名或分工。AI 工具执行的构建、安装、点击和配置见原生会话与项目 traces；这些工具动作不自动归为人工操作。\n\n团队成员姓名及分工未提供。缺失字段清单见 `pending-fields.md`。')

    write('sources.fragment.md', '# vg-spec9 来源片段\n\n'
          'S-vg9-1：官方随包基线 `metadata.base_commit=' + base + '`；bundle 标识 `' + task['baseline_bundle'] + '`。仅从本工程 `spec/metadata.json`、`workflow/baseline-provenance.json` 和本地 Git 取证，没有在材料阶段访问题包受限目录或下载来源项目历史。基线资源的路径/字节摘要及同源判断见 `changes/binary-files.json`；原样保留的官方基线二进制不当作额外自制素材。\n\n'
          'S-vg9-2：本题 `spec/requirement.md` 与 `inputs/Spec.md`，SHA-256=`c6236994e253c6de9f6decd99d7c0637620027ac16ce3699154796cba7a5edbf`。本题元数据 SHA-256=`496950d171e032fe6f10cf76fd485341f4f293b6f162857d60a46bd98756f660`。\n\n'
          'S-vg9-3：只读公共任务书和测试框架；本题保留 `spec-harness/`、`test-harness/`、`system-config/initial-20261016T113216Z/`，任务书版本见 `taskbook-version.md`。Python `hypium==6.1.0.210`、ArkTS `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`，由需求/锁文件与实际环境记录支持。没有新增业务第三方依赖。\n\n'
          'S-vg9-4：已安装的 ArkTS 技能及其本地参考文档。实际读取路径和原始返回在本题需求/方案/编码/验证会话中；编码交接明确记录检索索引缺失，改读 Basic-Syntax/functions.md 的 Function Types、classes.md 的 Static Members、error-handling.md 的 finally/async 说明。不能把安装包中的整理文档自动声明为逐条核验过的当前华为官方网页。本次原生工具检索未发现 `web.run` / `web__run` 调用；这只是工具记录观察，不替代用户的完整来源声明。\n\n'
          '用户额外来源声明：' + user.get('extra_sources', PENDING) + '。输入为空，不能写“无额外来源”或断言历史从未访问受保护修复内容。团队实际来源保护措施声明：' + team.get('source_guard', PENDING) + '；已观察到的本题 AGENTS/Skill 约束可列为配置证据，不能替代用户对实际措施的确认。\n\n'
          '本阶段只提供本题片段，不写根 `sources.md`。')

    limits = ('官方隐藏评测与成绩不可见；unsigned HAP 仅本机 API23 模拟器验证；Pura 型号与560 DPI未独立确认；首次清数据引导、实体设备、其他 WebDAV 产品、在途 force-stop/跨进程恢复、自动同步竞争、物理断网/DNS等全部错误、无关旧 ohosTest 均未验收。T10旧首闸风险已以补测替换最终依据，旧结果仍留档。设备合成配置保留、自动同步关闭；夹具关闭，原有 hdc 映射未声称全清。')
    write('solution.fragment.md', '# vg-spec9 完成情况与 AI 参与片段\n\n'
          '团队：' + team.get('team_id', PENDING) + ' / ' + team.get('team_name', PENDING) + '；阶段：' + team.get('stage', PENDING) + '。成果包版本、联系人、冻结时间、成员分工及实际来源保护措施尚待填写，见 `pending-fields.md`。\n\n'
          '本题已完成 1-do 的功能开发和本地验收：手动立即同步渲染实际 ArkUI LoadingProgress，进程内控制器持有本轮运行状态并直接等待真实 WebDAV 同步链；页面重入恢复绑定、重复触发/配置交错受控，真实终态后结束加载。五份生产文件的改动及需求映射见工程 `workflow/implementation/round-01-handoff.md`。\n\n'
          '独立 clean 构建、安装/启动均有成功原始日志；12个唯一有效本地用例为12 pass、0 fail/error/skip，由1项重试、9项回归与3项补测按名称取最终证据，T10只计一次。成功链有真实 HEAD/GET/PUT，请求未结束区间与实际 LoadingProgress 可见重叠；长链264.469秒仍保持加载。不得将12个本地方法直接换算为官方 F-point 数或成绩。\n\n'
          'AI 实际参与需求分析与复审、方案、五文件实现、测试夹具/用例、独立构建/设备自测、失败诊断与本次材料整理。历史四角色及本阶段验证角色均有原生线程；具体 ID、父子关系、参数和工具返回见 `traces/session-map.md`、`traces/manifest.json`，不是由主 Agent 自称兼任角色。人工代码修改情况：' + user.get('human_edits', PENDING) + '；团队成员工作：' + PENDING + '。\n\n'
          '用户未完成项/已知问题声明：' + user.get('known_issues', PENDING) + '。已记录技术限制：' + limits + '\n\n'
          '失败和重试保留：基线缺加载、夹具父目录自检失败后修正、Hypium swipe小写参数失败后重试、旧T10门闸+延时风险后补测、ArkTS检索索引缺失后直读本地文档、先前清理被拒及保留内容的处理。证据在工程 workflow/verification 报告、traces/implementation-validation/ 与本题原始会话；不得只取成功记录。\n\n'
          '本阶段工程快照标识为 `' + frozen['snapshot_id'] + '`，完整补丁应用与逐文件验证通过。阶段3必须采用 `delivery-notes.md` 指定快照作为 project/；原工作区仍保留含其他题内容的初始化总览，不能直接全目录打包。本阶段没有修改业务代码、资源或配置，没有生成成果 ZIP、提交或发布。\n\n'
          '正式成果冻结时间（北京时间，与团队 solution.md 一致）：' + team.get('freeze_time', PENDING) + '。材料导出截点见 trace-index，不作为正式冻结时间。')

    fragment = {'task_id': 'vg-spec9', 'status': 'submitted', 'project_path': 'tasks/vg-spec9/project',
                'build_instructions': 'tasks/vg-spec9/build.md', 'trace_index': 'tasks/vg-spec9/trace-index.md'}
    save('submission.json.fragment', fragment)

    field_values = [
        ('题目 ID', 'vg-spec9'),
        ('AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围（每道作答的赛题均须填写）', '需求/方案/编码/独立验证与材料整理；角色、实际提示及调用范围见 [session-map](traces/session-map.md)、[native manifest](traces/manifest.json)。0-analyze/1-do 以各原生线程全记录为范围，材料阶段单列，初始化总览不作为功能证据。'),
        ('基线构建准备：脚本配置版本、执行时间及输出记录路径（见 tools/prepare_baseline.py）', '本地日志 profile=`harmony-cup-build-v1`、task_id=`vg-spec9`、base_commit匹配、changes=[]；[prepare log](logs/prepare-baseline.log)、工程 workflow/setup-result.json 的 prepared_at=`2026-10-16T11:33:24.509135+00:00`（北京时间19:33:24，setup-result记录时间，不冒称脚本起止时间）。包版本记录见 workflow/baseline-provenance.json。指定题包 reports/build-baselines/vg-spec9.log 不存在；精确 prepare_baseline.py 脚本摘要和独立执行时间【待补充】，不访问题包禁区补取。'),
        ('Agent 名称及版本', '原生 header originator=`Codex Desktop`、cli_version=`0.162.0-alpha.17.2`；自定义角色见工程 system-config/initial-20261016T113216Z/agents/。这是 CLI/引擎版本，不是桌面客户端/扩展版本。Comate 客户端、桌面版本和 IDE 扩展 package 版本【待补充】；指定 /Applications 路径不适用于本机，exe版本字段为空，不能编造。'),
        ('模型名称、版本及运行参数', '本题已选会话 turn_context.model=`gpt-6.1-sol`、effort=`xhigh`；更细模型修订号【待补充／运行器未输出】。approval_policy=`never`、sandbox_policy=`danger-full-access` 是记录中的实际运行参数。逐线程 token 原始累计值见 [token-usage](traces/token-usage.md)，不推算计费或父子合计。'),
        ('本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置', '实际Skill/工具见 [tool-inventory](traces/tool-inventory.md)，初始配置在工程 system-config/initial-20261016T113216Z/，原生 session_meta.base_instructions、用户/开发提示与工具读文件返回补充实际规则。Comate appliedRuleNames/agentInfo 字段未产生；按原生配置记录，不发明同名字段。任务书版本见 [taskbook-version](taskbook-version.md)，common当前Git HEAD=`' + inv['common_git_commit'] + '`；四文件内容摘要固定本题实际副本；' + history),
        ('运行期间配置变更及原因（无则填“无”）', '已有初始快照及运行期间的角色派工、测试参数/夹具修正、同题会话恢复见 workflow/events.jsonl 和原生调用。生产产品签名/SDK声明/依赖未在本轮修改；不能把初始快照存在直接解释为整个运行期间“无配置变更”。其他未记录人工配置变更【待补充】。'),
        ('主会话 ID', '分析=`01a1447d-ff45-7802-986d-1bc93f60db1c`；实现验收=`01a1448f-dc21-7c42-a6c5-731bc0a5c14e`；材料=`' + str(inv['current_session']) + '`。各主线程原生 payload.id 与侧边栏索引 id 对应，详见 session-map。Comate sessionUuid【待补充／本机未产生】。'),
        ('关联会话及子会话 ID', '完整 [session-map](traces/session-map.md) 列10个本题线程，含本阶段独立验证。子线程自身 payload.id、父 sidebar id 与 parent_thread_id 区分记录，不把父ID误写为子ID。'),
        ('解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式', 'traces/native/*.jsonl（UTF-8，每行独立JSON）、filtered-session-index.jsonl（仅匹配本题的索引行）、traces/markdown/*.md（逐行机械转录，非侧边栏导出）、本题工程快照内 traces/baseline-analysis/、traces/implementation-validation/、workflow/ 与 logs/。原生清单见 manifest；不打包客户端数据库。'),
        ('失败、重试、未采用的候选方案及选择过程的记录位置', '工程 workflow/requirements/round-02-implementation-review.md、workflow/design/round-01-plan.md、workflow/implementation/orchestrator-decisions.md；workflow/verification/round-01-baseline-evidence.md、round-02-final-report.md；原生调用及 traces/implementation-validation/preparation/、round02-t1/、round02-t1-retry/、round02-regression/、round02-supplement/。包含失败而非仅成功日志。'),
        ('实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置', '本题原生JSONL及可读副本；完整源代码快照见 `' + snapshot + '`；changes/final.diff与changed-files.json；logs/build.log、install.log、selftest.log、selftest.json。可移植命令见 build.md；本材料阶段只静态复核，没有以新测试替换既有证据。'),
        ('导出时间、方法与读取方式', '本次本题原生快照截点（UTC）`' + inv['collected_at_utc'] + '`；[tools/collect_evidence.py](tools/collect_evidence.py) 分别按绝对工程路径与题号检索，再按精确cwd/登记ID筛选。只复制本题JSONL与匹配索引行；解题线程原样，材料线程中一次过宽索引读取返回的非本题侧边栏元数据行作隐私替换，逐行说明与原始/导出摘要见checks/trace-redactions.json；Markdown为对应机械副本。历史阶段快照与哈希亦保留。当前活动主会话只包含截点前记录，不声称含后续结束消息。'),
        ('成果冻结时间（北京时间，与 `solution.md` 一致）', team.get('freeze_time', PENDING) + '（team.yaml为空；本地工程快照/导出时间不能替代团队正式冻结时间）。'),
        ('官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识', '`' + base + '`；无新增Git提交，最终工程内容标识使用 [project-manifest](changes/project-manifest.json) 的 snapshot_id=`' + frozen['snapshot_id'] + '`。真实HEAD仍为基线，不把HEAD当最终内容版本。'),
        ('基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）', '[final.diff](changes/final.diff)，`--binary --full-index`，覆盖完整工程快照（含spec、tests、workflow、system-config、logs、traces及所有非递归材料容器外的.comate文件）。二进制逐项大小/摘要/同源见 [binary-files](changes/binary-files.md)；输出容器及初始化总览排除项见 delivery-notes。'),
        ('与提交源码的对应关系', '临时clone本地仓库→checkout基线→git apply --check --binary→实际apply，均退出0；还原全部' + str(frozen['file_count']) + '文件与快照逐字节相同，且快照每份文件与原工作区字节相同。详见 [diff-validation](checks/diff-validation.json)。历史251项运行指纹、五文件冻结摘要及HAP由独立材料审查复核；阶段3采用同一快照。'),
        ('人工操作及相关记录位置', '[human-changes](human-changes.md)；原生用户提示与工具执行分开记录。没有可核实的操作人完整清单，待用户补充。'),
        ('人工修改索引位置（可使用 `human-changes.md`；无则注明“无人工直接修改代码”）', '[human-changes.md](human-changes.md)：' + user.get('human_edits', PENDING) + '；输入为空，不推断为无。'),
        ('人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置', PENDING + '；如确无人工直接改代码，请由用户明确声明；如有，需真实当时记录，不能事后伪造。'),
        ('公开资料检索与代码复用记录位置，以及 `sources.md` 中的对应来源条目', '[sources.fragment.md](sources.fragment.md) S-vg9-1—S-vg9-4；本地ArkTS资料读取在原生会话；用户 extra_sources为空，完整额外来源声明【待补充】。不写团队根sources.md。'),
        ('本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 `solution.md`）', '实际工作目录 `D:/HCUP/vg-spec9`；成果包工作目录 `tasks/vg-spec9/project/`。工程AGENTS.md、初始Skill/四角色配置及原生派工含来源限制；team.yaml的实际source_guard为空，用户声明【待补充】，不能把提示约束等同于已实施的全部保护措施。'),
        ('脱敏范围（无则填“无”）', '本题解题JSONL/日志/截图未改写正文，保留本机路径、运行账号标识和合成测试配置。材料线程工具返回中非本题侧边栏索引元数据行已按checks/trace-redactions.json替换；没有遮蔽本题来源、代码、失败或重试。另排除整个初始化总览两份原始快照及其他工作区候选会话。Git仓库内部、依赖缓存、构建缓存及本机local.properties不随工程提交。没有导出auth、整个客户端库或签名私钥。具体项目排除项见 project-manifest，来源于同题内容的引用不被遮蔽。'),
        ('记录缺失及原因（无则填“无”）', 'Comate库/原生sessionUuid及Comate客户端与扩展版本未产生；Codex桌面/扩展精确版本未核实；用户侧边栏Markdown导出目录为空（已另产机械Markdown）；指定题包基线报告不存在；prepare脚本精确版本/起止时间未核实；正式冻结/人工修改/额外来源/实际保护声明留空。本题已登记8份解题线程原生JSONL均找到，另有2份材料线程；快照是截点导出，后续活动会话待阶段3最终导出。其他工作区候选不展开，不能据此声称不存在跨工作区本题历史；如用户另有此类记录需补索引。')
    ]
    # Keep every official template field verbatim and in its original order.
    template = Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
    labels = [line[2:].strip().rstrip('：:') for line in template.splitlines() if line.startswith('- ')]
    assert labels == [key for key, _ in field_values], (labels, [key for key, _ in field_values])
    write('trace-index.md', '# 运行记录索引\n\n' + '\n\n'.join('- ' + key + '：' + value for key, value in field_values))

    excluded_lines = '\n'.join('- `' + item['path'] + '`：' + item['reason'] for item in frozen['exclusions'])
    write('delivery-notes.md', '# vg-spec9 材料交付说明\n\n'
          '本轮仅完成2-submit单题材料；本地材料可审阅，用户未提供项保持【待补充】。没有改业务代码、资源和配置，也没有运行设备/重建HAP。workflow/state与events仅登记本轮会话和材料阶段事件。正式团队文档和ZIP由3-package处理。\n\n'
          '工程快照：`' + snapshot + '`；snapshot_id=`' + frozen['snapshot_id'] + '`，' + str(frozen['file_count']) + '份文件。阶段3必须将这个目录的全部内容复制为 `tasks/vg-spec9/project/`，不能直接递归复制原工作区。完整补丁基于该同一版本。材料会话一次索引读取返回了无关侧边栏元数据行，导出副本只替换这些行，原件不改；checks/trace-redactions.json保留逐行脱敏说明及前后摘要。\n\n'
          '补丁验证：仅通过本地传输clone本题分支、不拉取其他分支/标签，并detach到 `' + base + '`，git apply --check --binary 退出0；实际apply退出0；全文件路径、大小、SHA-256均与快照相同，快照与原工程所纳入文件逐字节相同。验证记录 `checks/diff-validation.json`，逐文件 `changes/project-manifest.json`。快照ID以相对路径字符串排序计算，最终完整性检查独立重算；材料阶段的换行与排序问题、修复和重试保留于 `checks/material-retries.md` 及材料原始会话。用临时仓库的 `core.autocrlf=false`、`core.eol=lf`，并通过临时info/attributes禁用写入时归一化，保留原始日志CRLF。部分基线文件的Windows checkout CRLF与Git基线blob LF不同，补丁为字节复原保留这部分差异；它们不属于功能修改，清单见 `changes/baseline-checkout-eol-preservation.json`。原始历史文本的空白诊断单独保留，不改写证据。\n\n'
          '纳入边界：基线全部保留文件，以及本工程所有tracked和非ignored新增文件，包括spec、hypium_tests、流程资料、原生本题记录、日志、配置快照。没有把diff限定在业务目录。已有.gitignore排除构建产物/依赖缓存/本机local.properties；新增输出目录 `.comate/submission-draft/**` 是外层材料容器，不再放进project/，避免补丁、快照和自身递归。若日后该容器外出现其他.comate过程文件，必须纳入工程并重生成补丁。\n\n'
          '隐私和跨题隔离仅排除以下本机原始初始化总览快照，原件留在原工作区，相关初始化摘要/版本/准备日志仍在本题工程；不读取或用其内容证明本题研发：\n\n' + excluded_lines + '\n\n'
          '历史manifest仍保留其原始路径/摘要，未伪造新哈希；其中指向被排除总览的条目须结合本说明读取。阶段3不能为了补齐这些路径而把总览原文放回工程。没有删除本题失败和重试。\n\n'
          '二进制实际字节保存在上述工程快照；基线同源、截图、夹具上传字节全部单列在 changes/binary-files.*。HAP摘要在同文件，仅作构建证据，不以HAP代替完整工程。\n\n'
          '路径汇总约定：以 `delivery-manifest.json` 的逐文件复制表为准，它同时指定完整project的来源和目的地，并排除checks/work临时仓库与旧的scratch快照。本材料目录的build.md、trace-index.md、taskbook-version.md、human-changes.md、sources.fragment.md、solution.fragment.md、delivery-notes.md、pending-fields.md、facts-and-sources.md、traces/、changes/、logs/、tools/及checks中的非work文件，按相同相对位置置于tasks/vg-spec9/；最终traces/code-snapshots中的完整project另外复制为任务project。复制表保留最终快照作为代码证据，确保索引路径有效。`checks/work/**`仅为本地补丁验证临时clone，含.git，不是交付材料；不要打包这些临时仓库。\n\n'
          '`submission.json.fragment`是官方tasks数组内本题候选对象；三个路径字段均用/，后两项为文件。它不是根任务清单或正式提交指令。team.yaml的submitted_tasks为空，阶段3应按用户选择合并，不据此自动决定全部题目状态。\n\n'
          '仍需补充项见 pending-fields.md；自动事实及出处见 facts-and-sources.md。本地输出和导出时间均不能代替用户未提供的正式冻结时间。')

    missing = [
        ('团队成果包版本', 'common/spec-harness/team.yaml: version', '空'),
        ('联系人姓名及联系方式', 'common/spec-harness/team.yaml: contact', '空'),
        ('正式成果冻结时间（北京时间精确到分）', 'common/spec-harness/team.yaml: freeze_time', '空；不可用快照时间代填'),
        ('成员姓名及实际分工', 'common/spec-harness/team.yaml: members[].name/work', '空'),
        ('实际来源保护措施', 'common/spec-harness/team.yaml: source_guard', '空；若确未配置需用户明确声明'),
        ('人工直接改代码声明／真实修改证据', 'spec/submit-input.yaml: human_edits', '空；如有请给操作人/目的/文件/前后标识/当时证据，如无请明确声明'),
        ('未完成项与已知问题声明', 'spec/submit-input.yaml: known_issues', '空；已观察到的技术限制已另列，不替用户填无'),
        ('完整额外来源使用声明', 'spec/submit-input.yaml: extra_sources', '空；不能推断为无'),
        ('IDE侧边栏Markdown导出目录', 'spec/submit-input.yaml: md_export_dir', '空；已提供标注来源的机械Markdown，可由用户判断是否另需侧边栏导出'),
        ('Comate会话sessionUuid、客户端/扩展版本的适用说明', '指定Comate库不存在，Windows上指定macOS product.json路径不适用', '本机未产生；已给Codex原生线程与真实父侧边栏关联，请按实际运行器说明'),
        ('Codex桌面客户端/IDE扩展精确版本及更细模型修订', '原生只有CLI 0.162.0-alpha.17.2和模型ID；exe版本字段为空', '未核实／运行器未输出；不填造'),
        ('基线prepare脚本精确版本/起止时间或指定原报告', '指定reports/build-baselines/vg-spec9.log不存在', '本题prepare日志及setup结果已保留；不越界补取其他题包目录'),
        ('未记录的人工配置/设备操作及可能的跨工作区本题会话', '当前受限取证只能精确关联本题cwd/登记ID；其他工作区候选不展开', '请用户仅在实际存在时给本题记录；不要求编造不存在的记录'),
    ]
    write('pending-fields.md', '# 仍需用户补充或确认适用性的字段\n\n所有未提供项保持【待补充】，本轮不以猜测填充。\n\n| 字段 | 来源 | 当前缺口 |\n| --- | --- | --- |\n' + '\n'.join('| ' + ' | '.join(row) + ' |' for row in missing) + '\n\n仅阶段3使用的 submitted_tasks、attempted_not_submitted、zip_out 也为空，留给团队打包阶段决定；本轮没有读取其他题。正式冻结前需导出活动材料会话的最终截点，不能用新记录替换原始解题证据。')
    write('facts-and-sources.md', '# 已自动填入的事实及出处\n\n'
          '| 事实 | 核实来源 |\n| --- | --- |\n'
          '| 团队 `' + team.get('team_id', PENDING) + '`、队名 `' + team.get('team_name', PENDING) + '`、阶段 `' + team.get('stage', PENDING) + '` | 只读 common/spec-harness/team.yaml |\n'
          '| 题号 vg-spec9，基线 `' + base + '`，bundle `' + task['baseline_bundle'] + '` | spec/submit-input.yaml、spec/metadata.json、Git基线对象 |\n'
          '| bundleName io.qzz.weiyu，EntryAbility，versionName 1.0.0 / code1000000 | AppScope/app.json5、entry/src/main/module.json5 |\n'
          '| product default，module entry，buildMode debug，SDK声明6.0.2(22)，未签名 | build-profile.json5、hvigor配置、独立Build-command.log |\n'
          '| ArkTS开发依赖Hypium1.0.24、Hamock1.0.0，Python Hypium6.1.0.210 | oh-package.json5/锁文件、test-harness/requirements.txt、原生验证工具输出 |\n'
          '| 独立构建/安装成功，12唯一最终有效用例通过；失败与重试仍保留 | logs/四入口、分轮raw_report、workflow/verification/round-02-final-report.md、checks/prior-evidence-review.md |\n'
          '| 当前251项运行指纹和5份生产冻结文件一致，真实LoadingProgress与请求重叠 | 既有原始指纹、checks/prior-evidence-review.md的本轮静态复核 |\n'
          '| HAP ' + str(binaries['build_artifact']['bytes']) + '字节、SHA256 `' + binaries['build_artifact']['sha256'] + '` | 当前HAP文件、先前构建/安装哈希、changes/binary-files.json |\n'
          '| 10个本题原生线程：8解题+2材料；主ID与侧边栏对应，子ID关联父sidebar | 两维文件名检索、session_meta、过滤session_index、本题workflow登记；traces/session-map.md |\n'
          '| Codex CLI 0.162.0-alpha.17.2，模型gpt-6.1-sol，effort xhigh；逐线程原生token | 原生header、turn_context、最后token_count；traces/token-usage.md |\n'
          '| common当前Git HEAD `' + inv['common_git_commit'] + '`、四任务书内容摘要、本题history不存在 | 只读common Git与四文件、spec/history存在性；taskbook-version.md |\n'
          '| 全工程快照 `' + frozen['snapshot_id'] + '`，' + str(frozen['file_count']) + '文件，补丁可应用且全字节还原 | changes/project-manifest.json、checks/diff-validation.json |\n'
          '| 二进制路径/大小/SHA256及与同路径官方基线是否同源 | 逐文件字节与本地Git基线blob比较；changes/binary-files.* |\n'
          '| 复制全部现有logs且摘要一致 | checks/copied-log-manifest.json |\n'
          '| Comate库和指定基线报告缺失；初始化总览不作本题研发证据；字段空值 | 文件存在性、本题state的初始化purpose、真实输入YAML；未用推测补齐 |')
    write('README.md', '# vg-spec9 提交材料草稿\n\n'
          '入口：[交付说明](delivery-notes.md)、[官方字段记录索引](trace-index.md)、[构建运行说明](build.md)。\n\n'
          '本题工程快照与完整补丁已验证可对应还原；未改业务代码、资源和配置。用户未提供字段仍待补充，不能据材料文件存在就认定可正式提交。\n\n'
          '- [仍需补充的字段](pending-fields.md)\n'
          '- [已自动填入的事实与出处](facts-and-sources.md)\n'
          '- [独立材料复核](checks/prior-evidence-review.md)\n'
          '- [完整补丁验证](checks/diff-validation.json)\n'
          '- [终审发现与修复闭环](checks/review-findings-resolution.md)\n'
          '- [二进制资源清单](changes/binary-files.md)\n\n'
          '团队级solution.md、sources.md、README.md、system-config汇总及ZIP均留给3-package；没有向外发送材料。')
    recomputed = hashlib.sha256(''.join(item['path'] + '\0' + item['sha256'] + '\n'
                                       for item in sorted(frozen['files'], key=lambda item: item['path'])).encode('utf-8')).hexdigest()
    assert recomputed == frozen['snapshot_id'], 'Cannot resolve review M1 without a matching independent recomputation'
    write('checks/review-findings-resolution.md', '# 材料终审发现与修复闭环\n\n'
          '独立验证报告保留其当时的结论，不改写历史失败。该报告审核的是先前e68d截点；随后仅workflow/state.json和events.jsonl登记了本材料阶段与下一步，生产代码、资源和产品配置没有变动。\n\n'
          'M1（已修复）：先前清单宣称按相对路径字符串排序生成ID，脚本却使用WindowsPath大小写排序，独立重算不一致。freeze_project.py已明确使用字符串path排序，verify_materials.py独立按声明算法重算。当前 snapshot_id=`' + frozen['snapshot_id'] + '`，独立重算=`' + recomputed + '`，两者相同。最终完整性报告 checks/material-integrity.json 还会再次核对。逐文件和补丁内容的旧审查结论未被当作新ID通过证明。\n\n'
          'R1（已修复）：首轮临时clone的Windows native换行导致apply-check失败。临时clone显式core.autocrlf=false、core.eol=lf后，重新checkout基线并生成补丁；当前apply-check与实际apply均退出0，' + str(frozen['file_count']) + '份文件全字节还原，见diff-validation.json。277项基线checkout换行保留条目不是功能改动；原始文本空白警告仍在patch-whitespace.log，不用改日志来消除警告。\n\n'
          '隐私处理：材料会话工具输出中的无关侧边栏索引行局部替换，实际替换行及前后摘要见trace-redactions.json。8份解题线程、源码依据和失败/重试没有被裁掉。\n\n'
          '尚未关闭的是用户输入和可核实记录缺口，见pending-fields.md；它们不被技术校验pass覆盖。没有补跑设备或构建；正式打包未执行。')
    print(json.dumps({'project_files': frozen['file_count'], 'logs_copied': len(copied_logs), 'template_fields': len(field_values),
                      'snapshot': frozen['snapshot_id'], 'formal_freeze_time': team.get('freeze_time', PENDING)}, ensure_ascii=True))


if __name__ == '__main__':
    main()
