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
