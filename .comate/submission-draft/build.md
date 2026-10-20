# vg-spec14 构建、运行与本地自测

本说明只针对 vg-spec14。证据路径以单题交付目录为基准，`project/` 表示完整工程；命令中的路径以该工程根目录为基准。成果包中工程目录拟为 `tasks/vg-spec14/project/`，本说明供后续打包时放到该题的 `build.md`。不需要克隆来源项目或获取其修复记录。工程实体按冻结manifest定义的有限投影交付，排除交付封套自身、两个混合总览原件及Python缓存；不声称复制本地所有目录。

## 已记录的环境与应用标识

| 项目 | 事实及依据 |
| --- | --- |
| 主机 | Windows 11；Python 3.12.3 64 位。`project/logs/do-validation/preparation-manifest.json` |
| IDE / 工具链 | DevEco Studio 6.1.0.860，实际编译SDK `6.1.0.105 / API 23`；Node v18.20.1，ohpm 6.1.1.830，hdc 3.2.0d。`project/logs/do-implementation/environment.log`、`project/logs/analysis-baseline/environment.txt`、`project/logs/do-validation/bundle-installed-run-11.txt`；版本归属核对见 `project/workflow/design/submit-facts-v1.md`。 |
| Java / Hvigor | 实际使用DevEco随附jbr与hvigorw；JDK精确版本【待补充】，Hvigor独立版本【待补充】，不以工程modelVersion代替。 |
| 工程 SDK 声明 | `targetSdkVersion` 与 `compatibleSdkVersion` 均为 `6.0.2(22)`，runtimeOS 为 HarmonyOS；本次没有为适配模拟器而修改这些声明。`project/build-profile.json5` |
| 构建配置 | product `default`，module `entry`，target `default`，mode `debug`；根清单与 Hvigor 的 modelVersion 均为 `6.0.2`。`project/build-profile.json5`、`project/oh-package.json5`、`project/hvigor/hvigor-config.json5` |
| 模拟器实测 | HarmonyOS/OpenHarmony 6.1 / API 23，1308×2880，560 dpi；当次设备序列号 `127.0.0.1:5555`。`project/workflow/verification/do-validation-v1.md` |
| 应用 | bundleName `io.qzz.weiyu`；module `entry`；入口 `EntryAbility`；versionName `1.0.0` / versionCode `1000000`。`project/AppScope/app.json5`、`project/entry/src/main/module.json5` |
| 工程依赖 | 业务 dependencies 为空；devDependencies 为 `@ohos/hypium` `1.0.24`、`@ohos/hamock` `1.0.0`，锁文件版本3，下载地址与完整性摘要见 `project/oh-package-lock.json5`。Python 设备自测使用另一套 `hypium==6.1.0.210`，见 `project/test-harness/requirements.txt`。 |

安装上述 DevEco 工具链与 SDK，设置读者本机的 `DEVECO_STUDIO_HOME`（DevEco安装根目录）与 `DEVECO_SDK_HOME`（含 `default/sdk-pkg.json` 的SDK根目录），再在当前PowerShell终端配置：

```powershell
$taskStudio = $env:DEVECO_STUDIO_HOME
$taskSdk = $env:DEVECO_SDK_HOME
if (-not $taskStudio -or -not $taskSdk) { throw '请先设置本机的DEVECO_STUDIO_HOME与DEVECO_SDK_HOME' }
$env:JAVA_HOME = Join-Path $taskStudio 'jbr'
$env:NODE_HOME = Join-Path $taskStudio 'tools/node'
$taskToolPaths = @(
  (Join-Path $env:JAVA_HOME 'bin'),
  $env:NODE_HOME,
  (Join-Path $taskStudio 'tools/ohpm/bin'),
  (Join-Path $taskStudio 'tools/hvigor/bin'),
  (Join-Path $taskSdk 'default/openharmony/toolchains')
)
$env:PATH = ($taskToolPaths -join [IO.Path]::PathSeparator) + [IO.Path]::PathSeparator + $env:PATH
```

历史执行进程加载过两层环境脚本；上述配置不依赖参赛电脑上的脚本路径。SDK 声明与实际工具链版本应分别保留，不能把工程 API 22 声明写成 API 23。安装工具的原始下载记录、安装包摘要及完整Python传递依赖锁未核实，均为【待补充】。

## 基线准备、依赖与构建

官方基线为 `88db8789e28333c7b7dcc8db078f394a262b73c3`，题包提交为 `4ea7779175fc185ed70e8dc515249ec77cd55563`。本题保留的准备日志 `project/logs/prepare-baseline.log` 记录 profile `harmony-cup-build-v1`、`dry_run=false`、`changes=[]`；`project/workflow/setup-result.json` 记录准备与依赖安装通过。题包约定位置的 `reports/build-baselines/vg-spec14.log` 缺失，不能将本题日志冒充为该文件。基线准备脚本的独立版本标识及精确执行时间仍为【待补充】；setup-result 的记录时间为 `2026-10-16T02:59:40.696733+00:00`，不能当成脚本精确起止时间。

工程已经包含必要源码、资源、依赖清单与锁文件。首次在新机器复现时安装依赖，再执行已实测的干净构建命令：

```powershell
ohpm install
hvigorw.bat --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon
```

历史依赖安装成功记录为 `project/logs/ohpm-install.log`。独立干净构建退出0，见 `project/logs/do-validation/build-command.txt`、`project/logs/do-validation/build.log`、`project/logs/do-validation/build-exit-code.txt`。源码告警由基线759降到756，32条随抽取迁移、减少3条、0新增；另有既有空签名配置告警1条，见 `project/logs/do-validation/warning-comparison.json`。这些告警未被隐藏。

HAP 产物：`project/entry/build/default/outputs/default/entry-default-unsigned.hap`。独立验证实测文件 SHA-256 为 `a8c2b0cd7f00f13cdded0bbbb51e17b183e7236c949f14ea97ca15fbd4634b17`，见 `project/logs/do-validation/hap-sha256.json`；重新构建的包摘要不保证相同，应另行保存本轮摘要。生产源码聚合 SHA-256 为 `8d882180894e3689b4dc0930b59034f3d46627fb454496b0e3ac32a141f2b285`，算法及逐文件记录见 `project/workflow/implementation/do-source-after-v1.json`。

## 安装、启动与必要初始化

在 DevEco 启动 API 23 手机模拟器，确认 `hdc list targets` 中设备在线。以下序列号来自本次实测；新机器应使用自己的在线设备序列号。

```powershell
hdc list targets
$taskDevice = '127.0.0.1:5555'
$taskHap = (Resolve-Path -LiteralPath 'entry/build/default/outputs/default/entry-default-unsigned.hap').Path
hdc -t $taskDevice install -r $taskHap
hdc -t $taskDevice shell aa start -b io.qzz.weiyu -a EntryAbility
hdc -t $taskDevice shell bm dump -n io.qzz.weiyu
```

逐批安装输出、应用更新时间与摘要在 `project/logs/do-validation/device-commands.jsonl`、`project/logs/do-validation/install-integrity-summary.json` 和 `project/logs/do-validation/install-run-*.log` 中。本次 API 23 模拟器实际接受 unsigned 包；真机或其他签名策略下须由复现者按目标设备配置合法签名，未验证 unsigned 包在其他设备上的可安装性。hdc某些错误会以exit0返回，应同时核对原始输出与bm信息。

首次启动如出现隐私页，阅读并同意后进入；使用引导可点「跳过」。本地验证保留了首次弹窗/引导阻挡入口的失败记录与后续处理。沿首页齿轮 → 设置总览 →「WebDAV 配置」进入，填写服务器地址、账号、密码、同步口令和远端目录。手动点击「立即同步」会保存本次配置并执行真实同步，无需预先点击「测试连接」。本题验证关闭自动同步，以区分本次手动请求；本地夹具使用虚构凭据，不需要真实账号或 AI 服务 Key。运行中固定页头显示原生 `LoadingProgress`，真实操作成功或失败结束后恢复；同进程离页重进会恢复仍在运行的状态。

## 可移植的自测复现

本题 `hypium_tests/` 是本地测试，并非官方隐藏用例或评分器。历史执行使用只读公共 runner；工程内 `test-harness/` 的 README、requirements 和8个 Python 模块已逐文件与该公共副本核对，SHA-256 相同。可使用这个工程自带副本建立独立测试环境，无需本机私有路径。以下为将历史命令参数化后的复现步骤，本次材料整理阶段未重新执行构建或设备测试。

先在工程根目录创建 Python 3.12 环境并安装已固定版本的依赖：

```powershell
python -m venv .venv-submit
& ./.venv-submit/Scripts/python.exe -m pip install -r test-harness/requirements.txt --index-url https://repo.huaweicloud.com/repository/pypi/simple
```

测试通过 `git ls-files` 和文件散列检查运行前后源码一致性。若完整工程解压后没有 `.git`，先在本地创建校验索引：`git init`，再执行 `git add -- entry/src AppScope '*.json5' hvigorfile.ts`；不需远程仓库。测试期间暂停源码编辑。先安装刚构建的本题 HAP，再建立模拟器到主机18164端口的反向转发；测试自身启动/停止内存 WebDAV 夹具，勿另启占用该端口的服务器。

```powershell
$taskRoot = (Get-Location).Path
$taskPython = (Resolve-Path -LiteralPath '.venv-submit/Scripts/python.exe').Path
$env:PYTHONPATH = Join-Path $taskRoot 'test-harness'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:VG14_TEST_AUTHORIZED = '1'
$env:HDC_DEVICE = $taskDevice
$env:VG14_EVIDENCE = Join-Path $taskRoot 'logs/submission-repro/device-run'
New-Item -ItemType Directory -Force -Path $env:VG14_EVIDENCE | Out-Null
hdc -t $taskDevice rport tcp:18164 tcp:18164
Push-Location (Join-Path $taskRoot 'logs')
try {
  & $taskPython -m harness.env_check
  & $taskPython -m harness.runner --project $taskRoot --device $taskDevice --json (Join-Path $taskRoot 'logs/submission-repro/runner.json')
  $taskRunnerExit = $LASTEXITCODE
} finally {
  Pop-Location
  hdc -t $taskDevice fport rm tcp:18164 tcp:18164
}
$taskRunnerExit
```

保留本轮 runner 原始输出与 JSON，检查 fail/error/skip 和 UI/服务证据，不只检查进程退出码。该命令运行最终脚本的完整11个方法；历史通过证据是分批结果，不能用此复现说明倒推历史曾有一轮11/11。若要按单方法定位，可沿 `project/logs/do-validation/run-selected.py` 的显式过滤方式设置 `VG14_CASE_FILTER`，每批重装本轮 HAP，输出到新证据目录，避免覆盖原始记录。

## 历史有效批次、范围与限制

| 批次 | 有效通过方法 | 退出及证据说明 |
| --- | --- | --- |
| v7 | 01–03 | 完整方法结束后主动中断，04片段不计；`project/logs/do-validation/batch-v7-completed.json`、`project/logs/do-validation/runner-v7.log` |
| v8 | 04–08 | 完整方法结束后主动中断，09片段不计；`project/logs/do-validation/batch-v8-completed.json`、`project/logs/do-validation/runner-v8.log` |
| v10 | 10、11 | 整批exit1来自09的测试键盘前置失败；独立10/11有效通过，见 `project/logs/do-validation/runner-v10.json` |
| v11 | 完整09 | 从头运行11组空/纯空格输入，一项通过、exit0，见 `project/logs/do-validation/runner-v11.json` |

上述运行日志也会在单题封套同级 `logs/` 保留副本。独立报告 `project/workflow/verification/do-validation-v1.md`、逐项矩阵 `project/workflow/verification/do-results-v1.json` 与审计 `project/workflow/do-final-validation-audit.json` 汇总 **11个唯一方法分批通过、无skip，29项适用条目pass**；E03显式取消、E13分页有依据不适用。`project/logs/do-validation/assertion-preservation.json` 对照有效批次与最终脚本的方法体AST。v1–v11的设施失败、定位/键盘调整、主动中断与成功记录均保留。

已覆盖首次/空数据/无变更、真实UI与请求联动、多阶段及后续失败、401/403/500、断连、连点、运行中返回重进、前后台、正常重启/在途强停、更换端点、空/纯空格、快响应及真实HTTP超时重试。快路径原始采样21份、同次真实请求5次；实际超时约20.109秒后客户端关闭无响应连接，真实流程结束后恢复并重试。

可选累计超过120秒压力样本未运行；全部系统返回手势/section组合、生产WebDAV认证及证书互操作性、复杂业务数据冲突和官方隐藏用例未全面测试。本地结果不代表官方成绩。独立报告未发现未解决的本题产品失败；参赛者的 `known_issues` 输入仍为【待补充】，不能据此替其声明「无已知问题」。
