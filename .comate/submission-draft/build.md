# cml-spec17 构建与运行说明

本文件计划放在 `tasks/cml-spec17/build.md`，完整工程位于同级 `project/`。以下生产命令在 `project/` 根目录执行。原始构建与测试证据见同级 `logs/`、`trace-index.md` 和工程内 `workflow/verification/do-results-03.md`。本次材料整理没有重新构建或运行设备测试。

## 工具、依赖与环境

已有环境记录使用 DevEco Studio 6.1.0.860、API 23 工具链；工程 `build-profile.json5` 保留原 `targetSdkVersion` / `compatibleSdkVersion` 为 `6.0.1(21)`，没有为材料整理升级项目配置。独立自测设备为 HarmonyOS 6.1.0.115/API 23，1308×2880、560dpi；Python 3.12.3、Python Hypium 6.1.0.210、hdc 3.2.0c。Python 依赖只供本地自测，生产构建不需要运行 Hypium。

安装对应 DevEco Studio、HarmonyOS SDK，并将 `DEVECO_STUDIO_HOME` 指向本机安装目录、`DEVECO_SDK_HOME` 指向已安装 SDK 根目录。每个新的 PowerShell 构建或设备进程都先初始化环境。原开发环境使用工作区环境入口；迁移环境可使用下列等价配置，无需原机环境脚本：

```powershell
$ErrorActionPreference = 'Stop'
if (-not $env:DEVECO_STUDIO_HOME -or -not $env:DEVECO_SDK_HOME) {
  throw '请先设置 DEVECO_STUDIO_HOME 与 DEVECO_SDK_HOME'
}
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
$env:Path = ($toolPaths -join ';') + ';' + $env:Path
Get-Command node, ohpm, hvigorw.bat, hdc | Select-Object Name, Source
```

根 `oh-package.json5` / `oh-package-lock.json5` 固定 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`；网络模块声明 `@ohos/axios=2.2.6`。其余模块依赖和锁文件随工程交付，`entry/oh-package.json5` 使用 `core/`、`feature/` 的相对本地依赖。根及 Hvigor 的 `modelVersion` 为 `6.0.1`。使用锁文件安装，不改写版本以避开构建问题。

## 安装依赖与构建生产 HAP

```powershell
# 当前目录为 tasks/cml-spec17/project；先执行上节环境初始化。
$taskRoot = (Get-Location).Path
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
$outDir = Join-Path $taskRoot "logs/material-reproduce-$stamp"
New-Item -ItemType Directory -Path $outDir | Out-Null
& ohpm install --all *> (Join-Path $outDir 'ohpm.log')
if ($LASTEXITCODE -ne 0) { throw '依赖安装失败，请保留日志' }
& hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon *> (Join-Path $outDir 'build.log')
if ($LASTEXITCODE -ne 0) { throw '构建失败，请保留日志' }
$hap = Join-Path $taskRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
Get-Item -LiteralPath $hap | Select-Object Length
Get-FileHash -LiteralPath $hap -Algorithm SHA256
```

原修复后生产构建成功日志为 `logs/implementation-fix-02-build-01.log`。该轮 HAP 为 9,489,353 字节，SHA-256 为 `5b835ea1f7b436e6b03234b86d88b48b5812a223d1052e08cb54b08dd6d4e8d3`。新的构建须保留自己的日志及摘要，不以旧 HAP 摘要替代新构建结果。原构建含依赖/SDK告警及无签名配置提示；“新增观察诊断0”来自有缓存限制的增量比较，不代表全量零告警。

## 安装、启动与初始化

生产应用标识为 `com.joker.coolmall`，模块 `entry`，主 Ability 为 `EntryAbility`，入口源码为 `entry/src/main/ets/entryability/EntryAbility.ets`。`build-profile.json5` 的 `signingConfigs` 为空，输出为 unsigned HAP；既有记录是在支持该安装方式的开发模拟器上成功安装。实际设备如要求签名，需由运行者自行提供合法签名配置和凭据，私钥不随成果包交付。

```powershell
# 新进程先执行环境初始化；当前目录仍为工程根。
& hdc list targets
# 将 HCUP_DEVICE 设置为本次实际占用的设备序列号后执行。
if (-not $env:HCUP_DEVICE) { throw '请设置本次实际设备 HCUP_DEVICE' }
$hap = Join-Path (Get-Location).Path 'entry/build/default/outputs/default/entry-default-unsigned.hap'
& hdc -t $env:HCUP_DEVICE install -r $hap
if ($LASTEXITCODE -ne 0) { throw '安装失败' }
& hdc -t $env:HCUP_DEVICE shell aa start -a EntryAbility -b com.joker.coolmall
if ($LASTEXITCODE -ne 0) { throw '启动失败' }
```

首次启动沿用原应用初始化和本地数据库。普通包访问原网络客户端配置的 `https://mall.dusksnow.top/app/`，进入受保护的下单流程需要合法登录及可用业务数据。本题没有取得合法测试账号或认证线上数据；原购物车结算仍经原 guard 进入登录，未验证真实线上订单或支付交易。不得用写入 token、播种生产数据库或移除普通 guard 代替认证初始化。

## 受控本地验证与原记录

独立验证使用包名 `com.hcup.cmlspec17.localdo`，只有显式测试 Want 才启用合成商品/地址/券、受控本地 HTTP 与测试路由例外；无 Want 保持普通认证行为。正常变体保留原 datasource，故障变体只在获批 IO 前加入有界延迟/单项异常。它们不是生产包或真实后端服务。

工程内 `workflow/do-entry/README.md`、`prepare.py`、`build.ps1`、`run.ps1`、`production_probe.py`、`hypium_tests/`、`test-harness/` 和 `test-harness/requirements.txt` 保存真实测试入口。脚本与测试支持代码包含原工作区根、设备及环境入口的固定配置；它们是历史原入口，未在本阶段改写，也未验证无修改跨机运行。迁移复测需在独立副本适配工作区根、设备选择、环境初始化、Python `PYTHONPATH` / 虚拟环境和唯一新轮次输出，保持业务及断言不变，并重新取证；不得直接复用旧轮目录覆盖原记录。

原设备使用 host loopback 18173 的受控服务和对应反向端口；fixture 服务未知路径返回404，无上游回落，不写 token。最新实际轮次为 `do-04` / `do-04-fault`：正常23、故障3个唯一方法通过；42项受控需求样本和2项普通 guard 回归另列。完整证据、原命令、测试变体差异及9项未运行边界见 `project/workflow/verification/do-results-03.md`（从本文件所在材料目录定位）。此前编译失败、do-01重试及do-03的E03/D02失败均保留。上述结果不代表官方隐藏测试或线上 F-point 成绩。

指定官方 baseline 日志未取得；工程内 `logs/prepare-baseline.log`、`logs/baseline-build.log` 和 `workflow/setup-result.json` 是单独的本地准备证据，记录 profile=`harmony-cup-build-v1`、准备时间与基线构建结果。不能将 profile 代称为未取证的脚本源码版本。
