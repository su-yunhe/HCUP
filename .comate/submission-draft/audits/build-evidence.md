# 构建与复现材料审查 v1

审查角色实际 `CODEX_THREAD_ID`：`01a143f6-357c-70a1-afbd-efd13c14d146`（本轮进程环境读取）。本轮仅静态读取本题工程、只读公共 Harness 和允许的提交模板；没有执行依赖安装、构建或设备命令，没有修改业务、测试、配置或 workflow 状态。本文件是材料审查，不是新增运行证明。

## 1. 材料要求与结论

`spec-harness/2-submit.md` 和 `D:/SWE-OpenHarmony/templates/submission-checklist.md` 要求 `build.md` 说明依赖安装、构建、安装、启动、应用标识和必要初始化，不能依赖未提交文件或参赛电脑私有路径。建议按下文事实编写，原始日志仍原样保留、通过相对路径引用。

必须区分以下三件事：

- 本机实际执行记录：包含原环境路径、设备序列号、退出码和历史失败，属于证据。
- 可移植命令：由已执行命令去除机器路径、改用复现者的安装目录变量；本材料阶段未重新执行，不得写成一次新的成功运行。
- 尚待包内落实的公共依赖：公共 Harness 及其 `requirements.txt` 必须具有明确的成果包内位置，不能仅指向原机器的公共目录或 `.venv`。

## 2. 配置与依赖事实

| 项目 | 核实结果 | 证据 |
| --- | --- | --- |
| bundleName / version | `io.qzz.weiyu`；`1.0.0` / versionCode `1000000` | `AppScope/app.json5` |
| 模块 / Ability | entry 模块，stageMode，`EntryAbility`，phone；首页 `pages/Index` | `entry/src/main/module.json5`、`entry/build-profile.json5`、`entry/src/main/ets/entryability/EntryAbility.ets` |
| 构建产品与目标 | product `default`，module `entry@default`，debug | `build-profile.json5`、run02 runner |
| 工程 SDK 声明 | target 与 compatible 均为 `6.0.2(22)`；runtimeOS `HarmonyOS` | `build-profile.json5` |
| 构建模型 | `6.0.2`；Hvigor 使用内置 `@ohos/hvigor-ohos-plugin` 的 appTasks/hapTasks | `oh-package.json5`、`hvigor/hvigor-config.json5`、两个 `hvigorfile.ts` |
| ArkTS 包依赖 | 根 runtime dependencies 为空；devDependencies 为 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`；entry dependencies 为空 | 根和 entry 的 `oh-package.json5` / `oh-package-lock.json5`；根锁文件保留版本、registry 和 integrity |
| 已记录工具链 | DevEco Studio `6.1.0.860`，环境记录 SDK `6.1.0.105` / API23；与工程声明 API22 分开列出 | 本题 `system-config/initial-20261016T070659Z/environment/toolchain-Enter-HarmonyEnv.ps1`；同快照 `skills/harmony-task-flow/references/local-setup.md`；`spec/baseline-notes.md` |
| 测试 Python | 公共 venv 配置为 Python `3.12.3`；最终报告为 Python3.12。公共 README 的“3.13”不应照抄为本轮事实 | 只读 `common/.venv/pyvenv.cfg`、`workflow/verification/final-report.md` |
| Python 测试依赖 | `hypium==6.1.0.210`；这是 Python Hypium，与 ArkTS `@ohos/hypium` 分别列出 | 只读 `common/test-harness/requirements.txt`、run04 `commands.log` |
| 实测设备 | `127.0.0.1:5555`；`emulator 6.1.0.115(SP11DEVC00E115R4P11)`，API23，1308×2880 | run04 `device-version.log`、`device-api.log`；独立最终报告 |
| 签名与产物 | `signingConfigs=[]`；输出 `entry/build/default/outputs/default/entry-default-unsigned.hap`；构建存在“No signingConfig found”告警 | 根 build-profile、run02/run03 `build-raw.log` |
| 最终安装 HAP 指纹 | `40971677431e7da2238dcff28e814dbe0ed81b889c093ee249be638fb34fd341` | run04 `hap-sha256.json`、最终报告；本轮没有重新计算实物摘要 |

本题根没有 `hvigorw` / `hvigorw.bat` 文件（本轮仅检查存在性），实际命令通过环境 PATH 找到 DevEco 随附工具。不得写成工程自带 `./hvigorw.bat`。JDK、Node、ohpm、Hvigor 的独立版本号未从本次读取的证据中核实，不能自行补写；目前可准确写“采用上述 DevEco 随附 JBR、Node、ohpm、Hvigor”。

## 3. 本机实际执行命令与结果

下列路径用于解释历史证据。公开 `build.md` 的复现命令应改用第4节的变量，不能要求存在这些原机器路径。

实际初始化（run02 归档 runner，run04 当前 runner 和报告一致）：

```powershell
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location -LiteralPath D:/HCUP/vg-spec13
```

工具链快照设置 JAVA_HOME、NODE_HOME、DEVECO_SDK_HOME，并把 DevEco 的 Node、ohpm/bin、hvigor/bin 和 SDK toolchains 放入当前进程 PATH；工作区快照还设置 Python UTF-8 和公共 Harness 路径。快照只能作为本机环境说明，不能直接作为可移植初始化入口。

| 阶段 | 已运行命令 / 结果 | 原始证据 |
| --- | --- | --- |
| 安装工程依赖 | `ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true`，退出0 | `workflow/implementation/build.ps1`；`logs/implementation-build/20261016-162656-{ohpm.log,result.json}` |
| 实现构建 | `hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon`，退出0 | 同轮 result 与 build.log |
| 独立 clean 构建 | `hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon`，run02/run03 均退出0 | run02 `runner-executed.ps1`、`build-raw.log`、`run-result.json`；run03 对应日志 |
| 安装 | `hdc -t 127.0.0.1:5555 install -r <本题HAP完整路径>`，run02/run03/run04 均退出0；run04 输出 install bundle successfully | runner；各轮 `install.log` / `run-result.json` |
| 启动 | `hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu`，run02 实际退出0、start ability successfully | `hypium_tests/test_webdav_backup.py:navigate`；run02 `observations.jsonl` 首个 hdc 事件，UTC `2026-10-16T08:30:12.405685+00:00` |
| 测试端口 | `hdc -t 127.0.0.1:5555 rport tcp:18173 tcp:18173`，18174 同理；退出0 | 各轮 `rport-add-*.log` |
| 完整发现运行 | 从该轮 logs 目录调用 `D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project D:/HCUP/vg-spec13 --device 127.0.0.1:5555 --json <该轮目录>/selftest.json` | run02 归档 runner、commands.log 与 selftest.json；同时设置 PYTHONPATH、VG13_EVIDENCE_DIR、VG13_RUN_TAG |
| 定向复测 | `./workflow/verification/run-verification.ps1 -RunId run04 -ExclusiveLease vg-spec13-01a143b8-verification-v2 -SelectedTests test_14_other_testing_task_survives_page_reentry,test_15_other_actions_then_backup_and_failed_reentry,test_16_fast_double_click_single_task -ReuseBuildFromRun run03` | run04 `commands.log`；实际调用 `workflow/verification/run-selected.py`，使用同一 Harness 结果模型 |
| 端口收尾 | `hdc -t 127.0.0.1:5555 fport rm tcp:18173 tcp:18173`，18174 同理 | 各轮 `rport-remove-*.log`；用 `fport rm` 删除实际 reverse 规则，不应照抄 run01 已纠正的错误清理命令 |

最新结果的准确表述：run02 原始15例为14 pass / 1 fail，测试退出1；run03构建安装成功，测试被中断，不记通过；run04 核对源码与HAP一致后复用 run03 构建、重新 install -r，3例为3 pass，测试退出0。`logs/selftest.json` 合并 run02 的00–13与run04的14–16得到17 pass / 0 fail / 0 error / 0 skip，并有 `not_a_single_full_suite_run=true`。不得写成“单次完整17/17通过”，也不得删掉 run02 原失败。详细失败归因、批准 oracle 修正和未执行项由 `workflow/verification/final-report.md` 说明。

## 4. 可移植复现写法（本轮未执行）

以下保留已实际运行参数，通过复现者配置的安装目录变量消除本机私有路径。需要在 `build.md` 明示：Windows PowerShell，安装上述 DevEco 和 SDK，将 `DEVECO_STUDIO_HOME`、`DEVECO_SDK_HOME` 设置为复现者的真实安装目录；当前目录为成果包中的本题工程。不要改低工程 SDK 声明来适应环境。

```powershell
$ErrorActionPreference = 'Stop'
if (!$env:DEVECO_STUDIO_HOME -or !$env:DEVECO_SDK_HOME) {
  throw '请先配置 DevEco Studio 和 SDK 安装目录环境变量'
}
$projectRoot = (Get-Location).Path
$env:JAVA_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'jbr'
$env:NODE_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'tools/node'
$toolPaths = @(
  (Join-Path $env:JAVA_HOME 'bin'),
  $env:NODE_HOME,
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/ohpm/bin'),
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/hvigor/bin'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/openharmony/toolchains'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/hms/toolchains')
)
$env:Path = ($toolPaths -join [IO.Path]::PathSeparator) + [IO.Path]::PathSeparator + $env:Path
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true
if ($LASTEXITCODE -ne 0) { throw 'ohpm install failed' }
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'HAP build failed' }
hdc list targets
$device = Read-Host '输入本轮在线设备序列号'
$hap = Join-Path $projectRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
hdc -t $device install -r $hap
if ($LASTEXITCODE -ne 0) { throw 'HAP install failed' }
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
if ($LASTEXITCODE -ne 0) { throw 'Ability start failed' }
```

上述 unsigned 包的安装成功范围是本轮 API23 模拟器；现有证据不证明所有真机允许安装 unsigned 包。用于限制的说明即可，不应据此擅改签名配置或加入签名私钥。

自测应在公共 Harness **明确的包内位置落实后**再填写完整命令。可使用 Python3.12 新建 venv，然后执行 `python -m pip install -r <包内test-harness>/requirements.txt --index-url https://repo.huaweicloud.com/repository/pypi/simple`；这是公共 README 提供的复现安装方法，**不是本次材料阶段已执行的 pip 记录**。不要随包复制本机 `.venv`，也不要把旧 `pyvenv.cfg` 的机器目录当作入口。

测试命令须包含的实际要素（下列 `$harnessRoot`、`$python` 必须指向成果包内 Harness 与复现者新建 venv 的解释器，具体相对位置由主 Agent/后续打包落实）：

```powershell
$runTag = 'reproduction-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$evidenceDir = Join-Path $projectRoot ('logs/' + $runTag)
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
$env:PYTHONPATH = $harnessRoot + [IO.Path]::PathSeparator + $projectRoot
$env:VG13_EVIDENCE_DIR = $evidenceDir
$env:VG13_RUN_TAG = $runTag
hdc -t $device rport tcp:18173 tcp:18173
hdc -t $device rport tcp:18174 tcp:18174
try {
  Set-Location -LiteralPath $evidenceDir
  & $python -m harness.runner --project $projectRoot --device $device --json (Join-Path $evidenceDir 'selftest.json')
} finally {
  Set-Location -LiteralPath $projectRoot
  hdc -t $device fport rm tcp:18173 tcp:18173
  hdc -t $device fport rm tcp:18174 tcp:18174
}
```

该代码只展示参数和数据流；最终 `build.md` 应先检查18173/18174/18175无现有监听和冲突映射，并检查两条 rport 退出码，只清理由本轮成功新增的映射（现有 runner 已有这些检查，不得移除既有所有者的规则）。测试源码自行创建18173/18174服务，无需另外启动 `webdav_fixture.py`；18175须保持无人监听以验证连接拒绝。完整发现当前17例是新的复现写法，未在材料阶段执行，不能将旧合并报告当成该命令的新输出。

当前 `workflow/verification/run-verification.ps1` 仍含本机私有路径，run02 归档 runner 更是历史原件；两者应保留作为证据，不能仅给出“运行该脚本”充当可移植说明。

## 5. 必要应用初始化与复测前置

- 启动后应用在 `pages/Index` 内初始化数据库、Preferences、词典等。未发现本功能要求另执行数据库导入或种子命令；空本地词库真实备份已由独立报告覆盖。
- 首次全新安装可能先出现隐私政策与使用引导：源码按钮为“同意并进入”，引导有“跳过”或“下一步/完成”。这是源码核对的初始化说明；本轮安装保留原 Preferences，没有进行卸载后干净安装，不能写成该首次流程已实际验收。自动测试期望已能到达首页 `⚙`。
- 功能入口：首页右上角 `⚙` → 设置 → `WebDAV 配置` → 滚动到手动操作“立即备份”。填入可访问的 WebDAV 地址、账号、密码、至少4位非空白同步密码及远程目录（空目录使用 `/weiyu_sync`）。支持当前未保存表单直接备份，不要把点击“保存设置”“测试连接”写成手动备份必需前置。
- 独立测试关闭自动同步、逐轮使用隔离目录。fixture 使用合成账号 `vg13-fixture`、密码 `fixture-pass`、同步密码 `fixture-sync-pass`，地址为 `http://127.0.0.1:18173` 或18174；只有建立上述 reverse 映射后才指向主机 fixture。它们不是外部真实服务凭据，不可用于真实服务商测试。
- 每轮须安装刚构建的本题 HAP、独占目标设备、保持源码冻结；不要并行执行多个 Harness/uitest 进程。现有测试会保存源码前后摘要并拒绝期间变更。
- HTTP fixture 证明本题所需网络请求与UI状态时序，不能扩展为外网/TLS/所有 WebDAV 服务商兼容、解密恢复或大库性能证明。D03/B18/B19本地异常未注入等限制继续引用独立最终报告，不得全部改为pass。

## 6. 证据缺失与交付前需要落实的材料项

1. 允许的官方基线日志 `D:/SWE-OpenHarmony/reports/build-baselines/vg-spec13.log` 本轮读取失败：文件不存在。仅保存本题 `logs/prepare-baseline.log`（changes为空）、`workflow/setup-result.json`、`logs/baseline-build.log` 等现存本地记录；不能伪称已读取官方基线报告。这些初始化记录只用于环境/准备说明，不作功能开发证据。
2. 主 Agent应落实公共 Harness 和 requirements 的成果包内位置，并在 `build.md` 绑定 `$harnessRoot` 与新 venv 的 `$python`。若本阶段不随单题材料复制公共依赖，应明确交给3-package处理并保持该项未完成，不能声称已脱离未提交文件独立复现。
3. Node/JDK/ohpm/Hvigor独立版本号目前未核实；保留“DevEco随附版本”及真实快照依据，若需要细化，由获准角色补充只读版本记录。本审查不运行工具版本命令。
4. 新的可移植命令、本次完整17例单轮执行、首次干净安装均未执行；这是材料准确性限制，不要求材料角色重跑或改业务。

审查完成范围：配置、依赖、构建/安装/启动命令与原始结果、自测命令和端口前置、首次初始化、路径与证据限制均已覆盖。未访问其他题工程、来源项目修复历史或题包禁止目录。
