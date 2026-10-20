# vg-spec15 构建与运行

以下路径以成果包为准。正式工程为 `tasks/vg-spec15/project/`。先按团队根 README 配置 DevEco、SDK、JBR、Node、OHPM、Hvigor 与 hdc，使命令可从 PowerShell 调用；团队公共环境说明由 3-package 汇总。不要直接运行工程历史环境脚本，它们保留了原机器路径，仅作证据。

## 环境与依赖

- 工程 `modelVersion=6.0.2`，target/compatible 声明均为 `6.0.2(22)`；实测构建日志使用 API 23 SDK，设备 API 为 23。
- 实测 Node `v18.20.1`，hdc `3.2.0c`；模拟器系统 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`。
- 保存的环境配置标注 DevEco `6.1.0.860` 和 SDK `6.1.0.105`，但这两个完整版本没有本轮独立版本命令输出。OHPM、Hvigor、JBR 的独立工具版本：【待补充】。工程模型版本不代替工具版本。
- 根 `oh-package.json5` 声明 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`；根及 entry 的 `oh-package-lock.json5` 均保留，根锁文件版本为 3，含 integrity 和获取地址。
- `build-profile.json5` 的 `signingConfigs=[]`，实测产物为 unsigned HAP。原测试模拟器接受该包。需要签名的目标设备应由使用者在 DevEco 配置自己的签名，个人签名私钥不随包提交。

证据：工程上述配置；`logs/implementation-validation/environment.json`、`build-round-02/build-result.json`；工程 `system-config/initial-20261015T140117Z/` 的环境记录。这里的 `logs/` 指本题随包日志。

## 安装依赖与构建

在工程根执行：

```powershell
ohpm install
if ($LASTEXITCODE -ne 0) { throw 'OHPM install failed' }

hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'HAP build failed' }
```

OHPM 命令是依据依赖清单整理的复用指令，历史安装日志只保留安装结果。Hvigor 完整命令有原始记录，exit 0；原有 759 条定位编译诊断与基线相同，没有新增诊断。本材料阶段没有重新构建。

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。已测历史产物大小 `8978553` 字节，SHA-256 `481c6f4609aee0370e12331e5200f1a1021886f9b8f9dd4e45289944ee6b56fa`。构建输出不放入完整工程；重建产物摘要未必相同。

证据：`logs/ohpm-install.log`、`logs/implementation-validation/build-round-02/{build-result.json,build.raw.log,artifacts.json}`。

## 安装与启动

应用标识：bundle `io.qzz.weiyu`，模块 `entry`，入口 `EntryAbility`，设备类型 `phone`，来自 `AppScope/app.json5` 和 `entry/src/main/module.json5`。

```powershell
hdc list targets
$device = '127.0.0.1:5555'
hdc -t $device install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $device shell aa start -b io.qzz.weiyu -a EntryAbility
```

安装有 `logs/implementation-validation/install-09.json` 和对应 raw 日志实证。历史启动由 Hypium `start_app` 完成，上述 `aa start` 是根据应用标识整理的等效启动指令，未冒称为历史原命令。

首次运行按页面处理隐私引导。进入“设置 → 同步”，填写可访问的 WebDAV 配置和与备份一致的同步密码，再操作“从云端恢复”。构建不需要 WebDAV 账户。自动测试使用本地受控服务及虚构凭据，不需要外部账户。

## 自测复用

历史最终命令是 `powershell -File hypium_tests/run.ps1 -Run 09`，结果为 9 通过、0 失败、0 跳过，exit 0。历史脚本含原机器路径，应作为证据保留；下述相对路径流程供解包复用，材料阶段未执行此新流程。

3-package 须提供团队公共 `system-config/test-harness/` 及其 requirements。实测 Python 为 `3.12.3`，Python 依赖 `hypium==6.1.0.210`、`cryptography==50.0.2`。后者没有列入现有公共 requirements，必须另行安装。Python Hypium 与 OHPM 的 Hypium 是独立依赖。

先安装刚构建的 HAP，再于工程根执行：

```powershell
$projectRoot = (Get-Location).Path
$packageRoot = (Resolve-Path '../../..').Path
$harnessRoot = Join-Path $packageRoot 'system-config/test-harness'
python -m venv .venv-selftest
$testPython = Join-Path $projectRoot '.venv-selftest/Scripts/python.exe'
& $testPython -m pip install -r (Join-Path $harnessRoot 'requirements.txt')
& $testPython -m pip install cryptography==50.0.2
$env:PYTHONPATH = $harnessRoot
$env:PYTHONIOENCODING = 'utf-8'
$env:VG15_RUN = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$env:VG15_CASES = ''
New-Item -ItemType Directory -Force logs | Out-Null
hdc -t 127.0.0.1:5555 rport tcp:18165 tcp:18165
Push-Location logs
try {
    & $testPython -m harness.runner --project $projectRoot --device 127.0.0.1:5555 --json selftest-reproduce.json
    if ($LASTEXITCODE -ne 0) { throw 'Selftest failed; inspect logs' }
} finally {
    Pop-Location
    hdc -t 127.0.0.1:5555 fport rm tcp:18165 tcp:18165
}
```

现有 `restore_support.py` 辅助调用将设备固定为 `127.0.0.1:5555`，仅修改 runner 的设备参数不能切换整套测试。`VG15_RUN` 每次必须唯一，不能复用历史 `09`，因为用例要求本轮测试词此前不存在。测试会写入虚构配置与夹具词，并关闭自动同步。

覆盖限制：云端“未更新”分支未设备执行；预览长时 pending/reject、导入失败/reject 主要通过当前实现的受控依赖探针验证；活动恢复生命周期变体、同一挂载视图主题重渲染等未逐项设备验证。9 项本地通过不代表官方 F-point 分数。详见 `solution.fragment.md` 及工程 `workflow/verification/implementation-round-02.md`。
