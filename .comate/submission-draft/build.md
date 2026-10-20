# cml-spec1 构建与运行

下列命令从包内 `tasks/cml-spec1/project/` 执行。工程、锁文件及自测工具均随包提供。命令使用复现方的本地工具环境，本说明不依赖参赛电脑的私有目录或环境脚本。

## 环境与依赖

原实测环境：DevEco Studio 6.1.0.860、SDK API23、Node 18.20.1、JBR 21.0.8、hdc 3.2.0c。工程 `build-profile.json5` 保留 target/compatible `6.0.1(21)`，product `default`；工程 API21 配置与使用 API23 SDK 的事实分别记录。

安装上述工具，将 DevEco 的 Node、JBR、ohpm、hvigor 和 SDK hdc 工具加入当前终端 PATH，并使 JAVA_HOME、DEVECO_SDK_HOME 指向复现方安装目录。仓库不含独立 hvigorw 包装器，命令由 DevEco 提供。保留所有模块的 `oh-package.json5` 与 `oh-package-lock.json5`；模块间 `file:` 依赖均为工程内相对路径。新增运行依赖为 `@ohos/lottie=2.0.33`，锁文件同时保留 registry 地址及 integrity。根开发依赖有 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`。

```powershell
ohpm install --all
hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

最终产物相对路径：`entry/build/default/outputs/default/entry-default-unsigned.hap`。原实测大小 20,739,960 bytes，SHA-256 `d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615`。重建产物可能因工具时间戳不同而摘要不同，源码绑定以随包快照清单为准。

## 安装、启动与初始化

应用 bundleName `com.joker.coolmall`，模块 `entry`，入口 `EntryAbility`；应用版本 `1.0.0` / `1000000`。原验证模拟器为 Pura 90 Pro Max，系统镜像 6.1.0.115 / API23，分辨率 1308×2880、560dpi。

```powershell
hdc list targets
$taskDevice = Read-Host '输入 hdc 实际列出的目标序列号'
hdc -t $taskDevice install -r ./entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $taskDevice shell bm dump -n com.joker.coolmall
hdc -t $taskDevice shell aa start -a EntryAbility -b com.joker.coolmall
```

`signingConfigs` 为空，当前 HAP 未签名。上述 unsigned HAP 在原模拟器安装成功有日志；其他设备若要求签名，应由复现方使用自己的合法签名配置，不随包提供参赛者签名私钥。原首启包含麦克风权限请求，拒绝权限后的系统设置窗口与返回路径在基线日志保留；此权限不是四标签本地导航的授权前提。保留启动路由和数据库自动初始化，无需预置账号、人工改库或启动私有服务。购物车为空、我的页未登录属于已测状态。

## 本题自测

以下复现环境安装方式使用随包 `test-harness/`。原执行使用其公共只读副本，实际 argv 与退出码见日志；本次材料整理没有重新执行构建或设备测试。

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r ./test-harness/requirements.txt numpy==2.5.4 opencv-python==5.0.0.93
$env:PYTHONPATH = (Resolve-Path ./test-harness).Path
./.venv/Scripts/python.exe -m harness.runner --project (Get-Location).Path --device $taskDevice --json ./logs/selftest-reproduction.json
```

Python 原实测为 3.12.3，Hypium 为6.1.0.210；NumPy/OpenCV 版本是材料整理时从同一公共虚拟环境只读查询得到，不冒称保存了历史运行时的独立依赖锁。不要启用 skip-env-check。测试会写新的日志和轨迹，复跑结果应另存，不替换原 run-r4。

## 原始验证与限制

原最终独立构建 `assembleHap` exit0（增量任务含 UP-TO-DATE），其日志 `logs/verification-do-build-run-r2-commands.json` 与同前缀 assembleHap.log；首次 clean 全量构建为修复前 r1，不能混写。基线182条文件诊断无新增，比较见 `project/traces/verification-do-r1/independent-warning-compare-r1.json`（相对本说明所在目录）。run-r4 安装与 runner 均exit0，8/8 pass，A1–A44本地验收通过，记录在 `logs/selftest-run-r4.json`、`logs/verification-do-run-run-r4-commands.json`，详细矩阵见 `project/workflow/verification/do-matrix-r4.md`。

历史一次 LIFECYCLE_TIMEOUT 的根因尚未完全排除，最终 run-r4 未复现；截图工具的有界重试原文保留。未运行官方隐藏测试，不声明官方得分。文本输入、空白输入、强制网络请求失败分支不属于本题可达验收内容。现有构建和自测日志完整复制到本题 `logs/`，本阶段无需补跑替代历史证据。
