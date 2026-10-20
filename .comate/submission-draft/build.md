# cml-spec7 构建与运行草案

本题当前为本地部分完成：41项明文验收中38项通过，B9/B10/B11真实微信、QQ、支付宝授权流程受外部条件阻断。不可用提示与恢复不计三项通过。构建、安装、冷启动及已实现范围适用回归已通过；本地计数不等于官方 F-point 或成绩。本阶段整理现有证据，未重跑构建或设备测试，未正式打包提交。

以下命令均从成果包 `tasks/cml-spec7/project/` 执行。工具链须由使用者安装并配置到 PATH，不能依赖参赛机环境脚本；工程内已有 `test-harness/`，无需另一个公共目录。构建目标、依赖和原始日志见工程内的配置及本文引用。

## 环境与依赖

- 工程 `build-profile.json5`：HarmonyOS，target/compatible SDK 均为 `6.0.1(21)`；产品 `default`，模块 `entry`，构建模式 `debug`。实际历史运行使用 API 23 SDK/模拟器，见原始 `logs/verification-navigation-smoke-03/environment.json` 和 `logs/analysis-baseline/env-check-final.json`。
- 历史工具实测：Node.js `18.20.1`、Python `3.12.3`、Hvigor `6.23.7`、hdc `3.2.0c`、Python Hypium `6.1.0.210`，依据 `logs/analysis-baseline/tool-versions.txt`。工程 modelVersion 为 `6.0.1`；modelVersion 不是 Hvigor 运行时版本。
- 本机需准备兼容的 DevEco Studio/HarmonyOS SDK、JDK、Node.js、OHPM，并保证 `hvigorw`、`ohpm`、`hdc` 可从 PATH 调用。签名配置为空，产物为 unsigned HAP；历史可调试模拟器安装成功不证明任意真实设备可接受未签名包。真实设备需使用合法本地签名配置，私钥不随成果包提交。
- 依赖版本以根及模块 `oh-package-lock.json5` 为准。本题没有新增三方登录 SDK 依赖；研究下载的 HAR 不代表已集成。Python 测试依赖由 `test-harness/requirements.txt` 锁定为 `hypium==6.1.0.210`。

| 已锁定外部依赖 | 版本 | 锁文件（工程相对路径） |
| --- | --- | --- |
| @hview/dayjs | 1.11.11 | `entry/oh-package-lock.json5`、`core/ui/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |
| @ibestservices/area-data | 0.0.6 | `entry/oh-package-lock.json5`、`core/ui/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |
| @ibestservices/ibest-orm | 2.0.2 | `entry/oh-package-lock.json5`、`core/data/oh-package-lock.json5`、`core/database/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |
| @ibestservices/ibest-ui-v2 | 1.0.7 | `entry/oh-package-lock.json5`、`core/ui/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |
| @jjr/lottie_component_v2 | 1.0.1 | `entry/oh-package-lock.json5`、`feature/main/oh-package-lock.json5` |
| @ohos/axios | 2.2.6 | `entry/oh-package-lock.json5`、`core/data/oh-package-lock.json5`、`core/network/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |
| @ohos/hamock | 1.0.0 | `oh-package-lock.json5` |
| @ohos/hypium | 1.0.24 | `oh-package-lock.json5` |
| @ohos/lottie | 2.0.25 | `entry/oh-package-lock.json5`、`feature/main/oh-package-lock.json5` |
| lunar | 1.0.0 | `entry/oh-package-lock.json5`、`core/ui/oh-package-lock.json5`、`feature/auth/oh-package-lock.json5`、`feature/common/oh-package-lock.json5`、`feature/cs/oh-package-lock.json5`、`feature/feedback/oh-package-lock.json5`、`feature/goods/oh-package-lock.json5`、`feature/launch/oh-package-lock.json5`、`feature/main/oh-package-lock.json5`、`feature/market/oh-package-lock.json5`、`feature/order/oh-package-lock.json5`、`feature/user/oh-package-lock.json5` |

在工程根执行（PowerShell）：

```powershell
ohpm install
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

保留锁文件；不要用升级依赖代替安装。原始准备安装结果见 `logs/ohpm-install.log`，最终独立全量构建及退出码见 `logs/verification-navigation-smoke-03/build.json`、`build.stdout.txt`、`build.stderr.txt`。这些是历史执行记录，上述便携命令未在本材料阶段重新执行。

## 安装、启动与人工入口

应用标识来自 `AppScope/app.json5`：`com.joker.coolmall`；entry 模块 `mainElement` 与 Ability 名均为 `EntryAbility`。产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。

```powershell
hdc list targets
$taskDevice = Read-Host '输入 hdc 列出的目标设备序列号'
hdc -t $taskDevice install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $taskDevice shell aa start -b com.joker.coolmall -a EntryAbility
```

先确认安装输出成功，再启动。首次启动按实际系统提示处理权限；正常进入“我的”，点击未登录入口/头像进入登录页。手机号登录、账号密码登录分别进入既有目标页；两份本地协议可离线查看并滚动至末尾。目标页导航不代表短信发送、密码认证或第三方登录已验证成功。没有为本页新增初始化账号、数据库导入、网络服务或硬编码凭据。

最终历史 HAP 的 bytes/SHA-256 见同级 `facts.json` 的 `hap` 和 `project/workflow/verification/root-delivery-check-03.json`；源码指纹与HAP对应见原始 `install-manifest.json`。HAP 是构建产物，不替代完整源码；当前工程快照的缓存排除以同级 `project-exclusions.json` 为准，解包后需要重新构建。

## 使用随包框架复现本地检查

原 `workflow/verification/run-verified-round.ps1` 写死了参赛机驱动器、工程目录、公共虚拟环境及 PYTHONPATH，保留它是为了原始证据；换机器时使用下面的相对路径入口。`cml_evidence.py` 从自身位置推导工程根，`fingerprint` 的 `--out` 必须是工程内的**JSON文件路径**。`run_verified_round.py` 从同一工程根定位源码和HAP，调用 PATH 中的 Hvigor/hdc，归档源码/测试首尾哈希、重新安装HAP及命令原始输出；其 `--round` 必须是全新的简单目录名。

```powershell
python -m venv .submission-venv
& ./.submission-venv/Scripts/python.exe -m pip install -r test-harness/requirements.txt
$taskProject = (Get-Location).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Join-Path $taskProject 'test-harness') + [IO.Path]::PathSeparator + $taskProject
$env:HDC_DEVICE = $taskDevice
& ./.submission-venv/Scripts/python.exe workflow/verification/cml_evidence.py fingerprint --out logs/reproduce-source.json
$taskSource = Get-Content -LiteralPath logs/reproduce-source.json -Raw | ConvertFrom-Json
$taskRound = 'reproduce-smoke-' + (Get-Date -Format 'yyyyMMddHHmmss')
& ./.submission-venv/Scripts/python.exe workflow/verification/run_verified_round.py --round $taskRound --expected-source-sha256 $taskSource.sha256 --device $taskDevice --mode suite --suite-kind smoke
```

该入口默认真实重构建和安装，不使用含旧绝对路径的 `--built-manifest`。不要在该轮运行期间改源码或测试。若要跑手机完整用例，换一个新 `$taskRound` 并使用 `--suite-kind full`。视觉条目需要对**当前源码/HAP及当前设备截图**独立复核；未提供匹配的 `--visual-review` 会跳过相应条目，跳过不计通过，不应把旧轮视觉JSON当作新轮结果。大屏/平板、旋转和文档终点另有 `layout`、`large-geometry`、`rotation`、`documents` 分组；只有真实改变设备窗口后才有对应尺寸证据，目录名称不构成尺寸证据。

三方真实授权仍需合法平台应用身份、签名/回调登记和服务端凭据交换契约，详见 `workflow/implementation/third-party-setup.md`。当前缺少这些条件，B9–B11保持blocked。历史最终验收矩阵和限制见 `workflow/verification/final-verification-03.md`、`logs/verification-final-03.json`。本材料阶段未执行上述复现命令，不能把指南当新增通过证据。
