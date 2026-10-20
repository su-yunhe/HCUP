# cml-spec24 构建、运行与自测

本说明中的相对路径均以完整工程根目录为起点。工程根包含 `AppScope/`、`entry/`、`core/`、`feature/`，不需要再套一层 `project/`。以下命令由已保存的真实命令和当前配置归纳；本次材料整理未重新安装依赖、构建或操作设备，也未验证在另一台机器上的重放。

## 环境与初始化

- 使用支持本工程 `modelVersion: 6.0.1` 的 DevEco Studio/Hvigor、OHPM、Node.js、Java 与 HarmonyOS SDK。根 `build-profile.json5` 的 target/compatible SDK 均为 `6.0.1(21)`，runtimeOS 为 `HarmonyOS`。
- 历史设备验证使用 x86_64、API 23、HarmonyOS 6.1.0.115、1308×2880@560dpi 的独立模拟器。自测脚本及 receipt 校验固定设备序列号 `127.0.0.1:11241`；先启动本题独立实例并确认该端口对应它。
- 每个新的 PowerShell 构建或设备进程须先配置已安装的公共工具环境，使 `hvigorw.bat`、`ohpm`、`hdc`、`node`、`python` 在 PATH 中。可选的 `HARMONY_ENV_SCRIPT` 指向接收机器实际环境脚本；也可直接使用 DevEco 配置好的 PATH，不要求未随包提供的脚本。公共工具安装要求及 common 测试框架应随成果包公共材料提供。

```powershell
# 先进入完整工程根，使用接收机器已安装工具的 PATH；可选加载本机环境脚本。
if ($env:HARMONY_ENV_SCRIPT) { . $env:HARMONY_ENV_SCRIPT }
$TaskRoot = (Get-Location).Path
$Device = '127.0.0.1:11241'
$Bundle = 'com.joker.coolmall'
$env:PYTHONDONTWRITEBYTECODE = '1'
Get-Command hvigorw.bat, ohpm, hdc, node, python
```

本题浏览、搜索、筛选和排序使用基线配置的 `https://mall.dusksnow.top/app/` 真实服务；商品页读取 `goods/info/page`、分类读取 `goods/type/list`，需要联网。已有取证为无鉴权只读请求；本题被测浏览流程没有额外账号、种子数据或后端初始化步骤。商品和销量随服务变化，不能固定历史商品顺序作为答案。

## 依赖安装

在工程根执行，保留各模块清单和锁文件：

```powershell
ohpm install
if ($LASTEXITCODE -ne 0) { throw 'OHPM installation failed' }
```

原安装记录 `logs/ohpm-install.log`、`logs/ohpm-install-exit-code.txt` 为成功、退出 0。当前根开发依赖为 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`；模块锁文件还记录 axios 2.2.6、IBest UI v2 1.1.1、IBest ORM 2.0.2、Lottie component v2 1.0.1 / Lottie 2.0.25、cashiersdk 15.8.42、crypto-js 2.0.5 等依赖，以随工程提交的 `oh-package*.json5` 为准。

## 三个构建目标

在工程根、已加载环境的 PowerShell 中依次执行：

```powershell
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'default build failed' }
hvigorw.bat --mode module -p module=entry@emulator -p product=default -p buildMode=debug assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'emulator build failed' }
hvigorw.bat --mode module -p module=entry@ohosTest -p product=default -p buildMode=debug assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'ohosTest build failed' }
```

| 目标 | 输出（相对工程根） | 范围 |
| --- | --- | --- |
| default | `entry/build/default/outputs/default/entry-default-unsigned.hap` | 正常应用，保留基线两个 arm64 原生库；没有 arm64 真机运行结论 |
| emulator | `entry/build/default/outputs/emulator/entry-emulator-unsigned.hap` | 正常应用，目标配置排除 arm64 库；用于 x86_64 模拟器 |
| ohosTest | `entry/build/default/outputs/ohosTest/entry-ohosTest-unsigned.hap` | 独立受控测试 feature，需与正常 emulator main 配套安装 |

根配置 `signingConfigs` 为空，保存的是 unsigned HAP，原日志保留 `No signingConfig` 告警。本题独立模拟器安装成功不能外推到要求签名的其他设备；这些设备须按其实际签名环境准备安装包。

最终 default/emulator 的成功命令在 `logs/development/verification-build-v4/{default,emulator}.command.json`，均为增量构建退出 0，含 UP-TO-DATE 任务；ohosTest 的实际成功命令在 `logs/development/verification-build-v3/ohosTest.command.json`，该同一测试产物随后安装并用于 v4 受控验证。材料阶段没有重跑 clean build。

| 最终已验证归档 | 字节 | SHA-256 |
| --- | ---: | --- |
| default | 19,923,862 | `febb328774368ad115670b8518836c5f71d8f302a8878a7922f3a331b9857954` |
| emulator | 15,075,281 | `74d10ad1219d5ef36697b248657d9c557aff5978c6ddc19a3eec96dc8ec8acf3` |
| ohosTest | 9,519,398 | `70c5db809b865584b561ace940c3b3f2c472f446e431e89c57f5b2afe11b6a3d` |

归档位于 `logs/development/verification-build-v4/artifacts/`，包隔离审计为该目录上一级的 `independent-hap-manifest.json`。在不同环境重建时保留新摘要，不把不同产物冒充上述历史产物。

## 安装、启动与应用标识

正常应用 bundle 为 `com.joker.coolmall`、module 为 `entry`、入口为 `EntryAbility`；受控 feature 的 module 为 `entry_test`、入口为 `FixtureAbility`。依据 `AppScope/app.json5`、`entry/src/main/module.json5` 和 `entry/src/ohosTest/module.json5`。

```powershell
$MainHap = (Resolve-Path -LiteralPath 'entry/build/default/outputs/emulator/entry-emulator-unsigned.hap').Path
hdc -t $Device install -r $MainHap
hdc -t $Device shell bm dump -n $Bundle
hdc -t $Device shell aa start -a EntryAbility -b $Bundle
```

检查安装输出含 `install bundle successfully`，并检查 dump 的 bundle/module/Ability；仅退出码 0 不足以认定安装成功。Windows HAP 参数先经 `Resolve-Path` 转为本机绝对原生路径。启动后从首页入口、分类 Tab 子分类或搜索进入商品分类页。

受控测试另外安装 test feature，并可启动其宿主：

```powershell
$TestHap = (Resolve-Path -LiteralPath 'entry/build/default/outputs/ohosTest/entry-ohosTest-unsigned.hap').Path
hdc -t $Device install -r $MainHap
hdc -t $Device install -r $TestHap
hdc -t $Device shell bm dump -n $Bundle
hdc -t $Device shell aa start -a FixtureAbility -b $Bundle -m entry_test
```

正常真实服务测试前须卸除该 bundle 的测试 feature，再只装 main；这会清除该独立测试应用的数据。核对 dump 只有正常 `entry` / `EntryAbility`，不含 `entry_test` / `FixtureAbility`。

## 自测依赖与证据初始化

本地设备套件使用公共 `test-harness/`。将 `COMMON_TEST_HARNESS` 设为成果包中该公共目录的实际路径（目录内应有 `harness/`、`requirements.txt`），然后：

```powershell
if (-not $env:COMMON_TEST_HARNESS) { throw 'Set COMMON_TEST_HARNESS to the packaged common test-harness directory' }
$HarnessRoot = (Resolve-Path -LiteralPath $env:COMMON_TEST_HARNESS).Path
python -m pip install -r (Join-Path $HarnessRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Hypium dependency installation failed' }
$env:PYTHONPATH = $HarnessRoot + [IO.Path]::PathSeparator + $TaskRoot
$Freeze = Join-Path $TaskRoot 'workflow/verification-freeze-v4.json'
$RoundRoot = Join-Path $TaskRoot ('logs/development/reproduce-' + (Get-Date -Format 'yyyyMMddTHHmmssfff'))
New-Item -ItemType Directory -Path $RoundRoot -ErrorAction Stop | Out-Null
python workflow/verification/verify_freeze_v1.py --freeze $Freeze --out (Join-Path $RoundRoot 'source-before.json')
if ($LASTEXITCODE -ne 0) { throw 'Source differs from the tested v4 freeze' }
```

公共 requirements 固定 Python `hypium==6.1.0.210`，它与根 OHPM 的 `@ohos/hypium` 是两套依赖。测试期间保持生产源码冻结，每轮重新安装精确 HAP、生成新 receipt 并使用唯一新日志目录。`workflow/verification/DEVICE_TESTS.md` 保留原环境说明及历史整轮脚本；原 PowerShell 包装中包含开发机路径，迁移机器时采用下面的底层命令，不直接依赖原包装的绝对路径。

为给现有 receipt 脚本提供真实安装命令与原始输出，可在当前进程定义以下记录函数；它只记录实际调用，不生成通过结论：

```powershell
function Invoke-RecordedHdc {
  param([string]$Label, [string[]]$HdcArgs)
  $stdout = Join-Path $RoundRoot ($Label + '.stdout.log')
  $stderr = Join-Path $RoundRoot ($Label + '.stderr.log')
  $commandFile = Join-Path $RoundRoot ($Label + '.command.json')
  $started = [DateTime]::UtcNow.ToString('o')
  & hdc -t $Device @HdcArgs 1> $stdout 2> $stderr
  $code = $LASTEXITCODE
  [ordered]@{command=@('hdc','-t',$Device)+$HdcArgs; started_utc=$started;
    ended_utc=[DateTime]::UtcNow.ToString('o'); exit_code=$code;
    stdout=$stdout; stderr=$stderr} | ConvertTo-Json -Depth 6 |
    Set-Content -LiteralPath $commandFile -Encoding utf8
  if ($code -ne 0) { throw ('hdc failed: ' + $Label) }
}
```

### device_real：正常 HAP、真实服务、自动发现 12 例

```powershell
Invoke-RecordedHdc -Label 'normal-uninstall' -HdcArgs @('shell','bm','uninstall','-n',$Bundle)
$uninstall = Get-Content -LiteralPath (Join-Path $RoundRoot 'normal-uninstall.stdout.log') -Raw
if ($uninstall -notmatch 'uninstall bundle successfully') { throw 'Native normal-only uninstall was not confirmed' }
Invoke-RecordedHdc -Label 'normal-main' -HdcArgs @('install','-r',$MainHap)
Invoke-RecordedHdc -Label 'normal-bundle' -HdcArgs @('shell','bm','dump','-n',$Bundle)
$dump = Get-Content -LiteralPath (Join-Path $RoundRoot 'normal-bundle.stdout.log') -Raw
if ($dump -match 'FixtureAbility|entry_test' -or $dump -notmatch 'EntryAbility') { throw 'Normal-only bundle check failed' }
$env:CMLSPEC24_INSTALL_RECEIPT = Join-Path $RoundRoot 'normal-install-receipt.json'
python workflow/verification/prepare_install_receipt_v2.py --hap $MainHap --install-command (Join-Path $RoundRoot 'normal-main.command.json') --bundle-dump (Join-Path $RoundRoot 'normal-bundle.stdout.log') --freeze $Freeze --out $env:CMLSPEC24_INSTALL_RECEIPT
if ($LASTEXITCODE -ne 0) { throw 'Normal install receipt failed' }
Push-Location -LiteralPath $RoundRoot
try {
  python -m harness.runner --project $TaskRoot --device $Device --json (Join-Path $RoundRoot 'selftest.json') *> (Join-Path $RoundRoot 'selftest.raw.log')
  $normalExit = $LASTEXITCODE
} finally { Pop-Location }
if ($normalExit -ne 0) { throw 'Normal suite failed; preserve raw evidence' }
```

最新历史结果为 `logs/development/normal-final-v1/selftest.json`：12 pass / 0 fail / 0 skip，exit 0。App 截断响应仍保留不完整标记，单独的实时只读 oracle 不得替换 App 原响应。

### device_controlled：main + 独立 feature、显式 9 例

继续在工程根运行，使用该轮真实双包安装记录生成另一份 receipt：

```powershell
$TestHap = (Resolve-Path -LiteralPath 'entry/build/default/outputs/ohosTest/entry-ohosTest-unsigned.hap').Path
Invoke-RecordedHdc -Label 'controlled-main' -HdcArgs @('install','-r',$MainHap)
Invoke-RecordedHdc -Label 'controlled-test' -HdcArgs @('install','-r',$TestHap)
Invoke-RecordedHdc -Label 'controlled-bundle' -HdcArgs @('shell','bm','dump','-n',$Bundle)
$env:CMLSPEC24_FIXTURE_INSTALL_RECEIPT = Join-Path $RoundRoot 'controlled-install-receipt.json'
python workflow/verification/prepare_fixture_receipt_v1.py --main-hap $MainHap --test-hap $TestHap --default-hap entry/build/default/outputs/default/entry-default-unsigned.hap --main-install (Join-Path $RoundRoot 'controlled-main.command.json') --test-install (Join-Path $RoundRoot 'controlled-test.command.json') --bundle-dump (Join-Path $RoundRoot 'controlled-bundle.stdout.log') --freeze $Freeze --out $env:CMLSPEC24_FIXTURE_INSTALL_RECEIPT
if ($LASTEXITCODE -ne 0) { throw 'Controlled install receipt failed' }
python workflow/verification/test_controlled_ui_v1.py --json (Join-Path $RoundRoot 'controlled-result.json') *> (Join-Path $RoundRoot 'controlled.raw.log')
if ($LASTEXITCODE -ne 0) { throw 'Controlled suite failed; preserve raw evidence' }
```

不传 `--method` 时选择全部 9 例；可重复 `--method` 显式选择重测方法，但未选或未执行的用例不记通过。该套件继承公共 HarnessTestCase，使用原 Page/VM/Repository/RequestHelper 与可控外部 Promise，覆盖错误、延迟、分页门禁、旧响应隔离和真实导航，不代表物理网络故障实测。

已有 9 例有效记录来自同源码同双包两轮组合：`controlled-run-v1` 的 C01–C06 通过、C07 宿主输入前置失败且 exit 1；`controlled-run-v2` 重测 C07–C09 为 3 pass、exit 0。不能写作历史单轮九例全部退出 0。

### host 补充状态验证

将 `CMLSPEC24_TYPESCRIPT` 指向接收机器 DevEco/Hvigor 随附 TypeScript 的 `lib/typescript.js`，用于覆盖脚本中的开发机默认路径：

```powershell
if (-not $env:CMLSPEC24_TYPESCRIPT) { throw 'Set CMLSPEC24_TYPESCRIPT to the local TypeScript lib/typescript.js' }
node workflow/verification/test_goods_category_state.cjs --freeze workflow/verification-freeze-v4.json --out (Join-Path $RoundRoot 'state')
if ($LASTEXITCODE -ne 0) { throw 'Host supplemental suite failed' }
python workflow/verification/verify_freeze_v1.py --freeze $Freeze --out (Join-Path $RoundRoot 'source-after.json')
if ($LASTEXITCODE -ne 0) { throw 'Source changed during validation' }
```

历史 host 结果为 `logs/development/state-v4/state-results.json`：14 pass。它使用原代码转译及外部 datasource / 装饰器 / Toast 替身，只证明宿主行为，不替代 ArkTS 构建、原生 UI 或真实 HTTP 验证。

## 收尾及真实覆盖边界

受控测试后卸除本题 bundle，再只安装正常 main，检查 dump 不含测试 feature。历史运行曾临时调整 app 日志 buffer 和 flow control，最终恢复 app buffer 256K、pid/domain flow control on；新重放若变更这些设置，也须按运行前值恢复并保留命令。历史恢复证据在 `logs/development/device-v4/final-*`。

正常包与测试包的隔离、失败重试及限制详见 `workflow/verification/development-verification-v5.md`、`workflow/verification/DEVICE_TESTS.md` 和 `spec/acceptance-implementation.md`。arm64 真机及相关原生支付能力、物理网络中断/超时/服务器乱序、CDN 全量下载与所有图像像素对比、官方隐藏测试均无已完成运行结论。本地 A01–A76 的 76 pass 是本地验收拆解结果，不是官方 F-point 或成绩。
