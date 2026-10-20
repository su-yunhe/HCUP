# vg-spec13 构建与运行

本文件按成果包内 `tasks/vg-spec13/` 编写，完整工程为同级 `project/`；命令中的位置由当前包路径计算，不依赖参赛电脑上的目录。历史原始命令和输出另见 `logs/`。

## 环境与声明

本地实测 DevEco Studio 6.1.0.860、SDK 6.1.0.105/API 23，HarmonyOS 模拟器 6.1.0.115(SP11DEVC00E115R4P11)、API 23、1308×2880、VirtualPixelRatio 3.5。机型没有独立确认，不能据此宣称满足全部官方屏幕/机型规格。Python 环境为 3.12.3，Hypium 6.1.0.210，uitest 6.0.2.3（见原运行证据及 `audits/build-evidence.md`）。

工程本身声明 `targetSdkVersion` / `compatibleSdkVersion` 为 `6.0.2(22)`，`modelVersion` 为 `6.0.2`，没有为本次材料改写。`signingConfigs=[]`。工具链版本与工程兼容声明是不同字段。Node、Java、OHPM、Hvigor 的独立精确版本未从现有日志核实，标记【待补充】，使用该 DevEco 配套工具。

在 Windows PowerShell 中由复现者把环境变量 `DEVECO_STUDIO_HOME` 设为已安装 Studio 的目录，把 `DEVECO_SDK_HOME` 设为 API 23 SDK 根目录，然后执行：

```powershell
$ErrorActionPreference = 'Stop'
if (-not $env:DEVECO_STUDIO_HOME -or -not $env:DEVECO_SDK_HOME) { throw 'Set Studio and API 23 SDK environment variables first.' }
$taskDir = (Get-Location).Path # 当前为 tasks/vg-spec13
$projectDir = Join-Path $taskDir 'project'
$env:JAVA_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'jbr'
$env:NODE_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'tools/node'
$toolPaths = @(
  (Join-Path $env:JAVA_HOME 'bin'), $env:NODE_HOME,
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/ohpm/bin'),
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/hvigor/bin'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/openharmony/toolchains'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/hms/toolchains')
)
$env:Path = ($toolPaths -join ';') + ';' + $env:Path
Set-Location -LiteralPath $projectDir
```

工程没有自带 hvigor wrapper；`hvigorw.bat` 来自 Studio 配套工具。不要执行工程旧 `workflow/verification` runner 来替代以上初始化，它们属于历史证据，含原运行机路径。

## 依赖、构建与产物

根 `oh-package.json5` 的开发依赖为 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`，entry 模块无额外包依赖；提交完整 `oh-package-lock.json5`，不得只交安装包。

```powershell
ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true
if ($LASTEXITCODE -ne 0) { throw 'ohpm install failed' }
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'assembleHap failed' }
$hap = Join-Path $projectDir 'entry/build/default/outputs/default/entry-default-unsigned.hap'
Get-FileHash -LiteralPath $hap -Algorithm SHA256
```

依赖安装与实现构建均退出 0（`logs/implementation-build/20261016-162656-result.json`）；独立 run02、run03 的 clean 构建退出 0。历史最终安装产物 SHA-256：`40971677431e7da2238dcff28e814dbe0ed81b889c093ee249be638fb34fd341`，大小见 `changes/verified-hap.json`。重新构建的容器时间/工具环境可能导致包字节不同，此摘要标识历史实际测试产物。

## 安装与启动

```powershell
hdc list targets
$device = '127.0.0.1:5555' # 本地实测设备；复现时替换为 discovery 返回的目标
hdc -t $device install -r $hap
if ($LASTEXITCODE -ne 0) { throw 'install failed' }
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
```

应用 `bundleName=io.qzz.weiyu`，入口 `EntryAbility`，模块 `entry`，版本 `1.0.0` / `1000000`。来源：工程 `AppScope/app.json5` 与 `entry/src/main/module.json5`。上述 unsigned HAP 曾在所记录模拟器安装成功；对要求签名的物理设备，需要复现者按该设备配置自己的合法签名，本阶段不提供或复制私钥。

首次进入按界面完成必要引导。首页⚙→设置→WebDAV 同步，输入合法地址、账号、密码、至少四位同步密码及远程目录，点击“立即备份”。填入的当前配置用于本轮备份；自动同步应关闭以隔离手动测试。真实服务必须具备所需网络/目录权限。原运行的临时端点与凭据只用于本地 fixture，不是可连接的线上服务。无额外数据库初始化，历史本地数据为空库，不声明非空大库覆盖。

## 可移植自测入口

`repro-support/test-harness/` 是只读公共 Harness 的随材料副本，`requirements.txt` 固定 Hypium 版本。打包时连同 `repro-support/run-selftest.ps1` 复制到本题材料目录。建立本题独立虚拟环境不会改工程或公共框架：

```powershell
Set-Location -LiteralPath $taskDir
python -m venv .repro-venv
& ./.repro-venv/Scripts/python.exe -m pip install -r ./repro-support/test-harness/requirements.txt --index-url https://repo.huaweicloud.com/repository/pypi/simple
& ./repro-support/run-selftest.ps1 -Device $device -Python ./.repro-venv/Scripts/python.exe
```

先安装本轮刚构建的 HAP，再独占设备运行；脚本拒绝主机18173/18174/18175或设备18173/18174已有映射。测试创建本机18173/18174的合成WebDAV服务并经hdc反向映射；脚本只移除本轮创建的映射。自测会操作应用设置并保存合成配置，适用于独立测试模拟器。它使用提交工程原有 `hypium_tests`，从新日志目录运行，不覆盖历史失败记录。此入口是本次材料整理写出的可移植等价脚本，本阶段没有重新运行设备测试。

历史结果：同一 v2 源码 `run02` test00–13 与 `run04` test14–16 合并 17 pass；run02 原始15例为14 pass/1 fail，run04定向3例通过。run01/run03 中断保留。不是单次全套17/17，也不是官方评测。D03、B09、B16、B18、B19为 not_run；非预期本地异常、真实服务商/TLS、解密恢复、非空大库等限制见 `solution.fragment.md` 与工程 `workflow/verification/final-report.md`。原始日志齐备，不需要为补日志重跑业务。
