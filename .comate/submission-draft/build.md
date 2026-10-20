# vg-spec7 构建与运行

以下命令均从本题 `project/` 根目录执行。源码、资源、根及 entry 的包清单／锁文件随工程交付。无需本机私有目录；本说明是可移植复现步骤，历史原始命令仍保留在日志中。本次材料阶段没有重新构建或运行应用。

## 环境与依赖

实测 DevEco Studio 6.1.0.860、SDK 编译工具 6.1.0.105（API 23）、Node 18.20.1、JBR OpenJDK 21.0.8。工程 targetSdkVersion 和 compatibleSdkVersion 均保持 `6.0.2(22)`，没有修改为 API 23。实测 PowerShell 7.6.5。依据自己的安装位置配置 `DEVECO_SDK_HOME`、`JAVA_HOME` 和 PATH，确保 DevEco 随附 `node`、`java`、`ohpm`、`hvigorw`、`hdc` 可调用；工程本身不附 hvigorw wrapper。

根及 entry 运行 dependencies 为空；开发依赖锁定 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`，lockfileVersion=3。工具 CLI 的历史精确版本（ohpm、Hvigor、hdc）【待补充】，不能把 modelVersion 当 CLI 版本。

```powershell
ohpm install
hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

`ohpm install` 是依据清单的复现步骤；历史安装日志只有成功输出，没有完整 argv／起止时间。独立 clean 构建实际退出 0；`project/traces/do-verification-build-v1/invocation.json` 保存起止时间与命令，build.log 保存完整输出。764 条基线诊断与 763 条当前诊断相比新增 0、减少 1，不是零告警。

## 产物、安装与启动

- 产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。
- 历史最终验证产物：9,101,851 字节，SHA-256 `604fe92b34c70df74cf6907a363ac4571721fb4078ed7107d854baaab42b6e0d`。构建输出不随源码工程拷贝；新构建不承诺安装包字节恒定。
- bundleName：`io.qzz.weiyu`；entry 模块；入口 `EntryAbility`，源文件 `entry/src/main/ets/entryability/EntryAbility.ets`；版本 1.0.0（1000000）。
- `signingConfigs=[]`；上述 unsigned HAP 已在实际模拟器安装、启动。真机签名和真机安装未验证，相关配置【待补充】。

```powershell
hdc list targets
$deviceId = Read-Host '输入列表中的目标设备标识'
$hapPath = (Resolve-Path -LiteralPath './entry/build/default/outputs/default/entry-default-unsigned.hap').Path
hdc -t $deviceId install -r $hapPath
hdc -t $deviceId shell aa start -a EntryAbility -b io.qzz.weiyu
```

Windows 安装使用 Resolve-Path 返回的原生路径，并同时检查退出码和 `install bundle successfully` 输出。历史 core-v1 曾因正斜杠路径解析失败却退出 0，整轮无效记录保留。实际设备 `127.0.0.1:5555`，安装与 bundle 元数据见同级 `logs/do-regression-v3/`。

## 必要初始化与本题行为

首页 → 设置 → WebDAV 配置；输入可访问的地址、账号、密码、同步密码并显式保存。验证确认门禁时关闭自动同步并等待旧任务排空。点击「从云端恢复」先出现本地「继续／取消」；尚未点击「继续」不应产生本次恢复网络流量。有效当前弹窗点击「继续」后才进入既有发现／下载／解密／统计预览，原第二次「确认恢复」仍保留。使用自己的受控 WebDAV 端点；日志中的账号与口令是测试夹具值，不是应用默认配置。

首次全新安装的引导未独立覆盖；不能把保留数据安装等同于全新安装验证。完整实际导入与非空覆盖未测，继续前门禁的本地证据不代表这些分支通过。

## 可移植自测命令

工程保留 `test-harness/` 与 `hypium_tests/`；Python 侧 `hypium==6.1.0.210` 与 ohpm 的同名开发依赖是不同工具。以可访问应用沙箱的模拟器、竖屏及受控端点运行。以下是利用随包框架的复现命令；历史日志中的绝对路径运行脚本只作记录，无需执行。

```powershell
python -m venv .testenv
& ./.testenv/Scripts/python.exe -m pip install -r ./test-harness/requirements.txt
$projectRoot = (Get-Location).Path
$testPython = Join-Path $projectRoot '.testenv/Scripts/python.exe'
$env:PYTHONPATH = Join-Path $projectRoot 'test-harness'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:VG7_EVIDENCE_DIR = Join-Path $projectRoot 'traces/reproduction'
$env:VG7_CASES = ''
$env:VG7_DATABASE_DIR = Read-Host '输入本次设备上本应用实际可访问的数据库目录，用于 D0 只读对比'
New-Item -ItemType Directory -Path ./logs -Force | Out-Null
Push-Location ./logs
try {
  & $testPython -m harness.runner --project $projectRoot --device $deviceId --json ./reproduction-selftest.json
} finally {
  Pop-Location
}
```

按执行顺序同轮运行时 T02 生成 T06 的单次发现链参考。单跑 T06 须通过 `VG7_SINGLE_FLOW_REFERENCE` 指向对应单次链 JSON。未提供可访问数据库目录时，测试会记录 D0 阻断，不能把这当作 D0 已验证。测试会经既有「立即备份」生成夹具并隔离其流量，因此只在允许测试数据操作的环境运行。

历史接受结果是 core-v2 的 T01/T02/T03/T05/T07 加 regression-v3 的 T04/T06/T08/T09，共 9 项最终有效通过；core-v2 原始退出 1、regression-v3 退出 0。没有一次历史执行全部 9 项成功的记录。参见 `project/workflow/verification/do-result-v1.json`。本材料阶段未执行上述复现命令，未取得新的功能测试结论。
