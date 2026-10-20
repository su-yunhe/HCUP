# vg-spec1 构建与运行说明

本说明供成果包中的 `tasks/vg-spec1/build.md` 使用。以下命令均在相邻的 `project/` 工程根目录执行；说明中的链接以本说明所在目录为基准。公共工具安装、工具版本、环境变量与完整自测框架由 `3-package.md` 阶段归档到包根 `README.md` 和 `system-config/`。先按公共环境说明配置当前终端，使 `ohpm`、`hvigorw`、`hdc` 可从 `PATH` 调用。

## 工程与实测环境

| 项目 | 值与出处 |
| --- | --- |
| 题目 | `vg-spec1`，官方基线 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`；见 [metadata.json](project/spec/metadata.json) |
| 工程 SDK 声明 | `targetSdkVersion`、`compatibleSdkVersion` 均为 `6.0.2(22)`，`runtimeOS=HarmonyOS`；见 [build-profile.json5](project/build-profile.json5) |
| 构建模型 | `modelVersion=6.0.2`；见 [oh-package.json5](project/oh-package.json5) 和 [hvigor-config.json5](project/hvigor/hvigor-config.json5) |
| 已使用的工具环境 | DevEco Studio `6.1.0.860`、API 23 SDK 工具链、PowerShell `7.6.5`；见 [基线验证记录](project/workflow/verification/baseline-round-01.md) 和 [环境记录](project/traces/baseline-round-01/environment.json) |
| 当前完整自测设备 | 专用模拟器 `127.0.0.1:11237`，API `23`，`OpenHarmony-6.1.0.115`，实测渲染分辨率 `1308×2880`；系统参数与 RenderService 读回见 [commands.jsonl](logs/development-round-02/manual-instance/commands.jsonl) |

API 23 是本次构建工具链和模拟器的实测环境，工程 SDK 声明仍为 API 22；没有把配置改成 API 23，也没有 API 22 设备或实体机运行结论。Node、OHPM、Hvigor、Java 等公共依赖的精确版本以成果包根公共环境记录为准。

## 依赖安装

保留随工程提交的根及 `entry/` 下依赖清单和锁文件。在工程根执行：

```powershell
ohpm install
```

根 [oh-package-lock.json5](project/oh-package-lock.json5) 锁定 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`，解析源为 `ohpm.openharmony.cn`；`entry` 无额外依赖。这里的 `@ohos/hypium` 是工程侧开发依赖，与设备自动验证所用 Python Hypium 是两个依赖。

现有 [ohpm-install.log](logs/ohpm-install.log) 记录 `install completed in 0s 165ms`，[setup-result.json](project/workflow/setup-result.json) 记为 `pass`。该安装日志未保存原始命令行参数；上面给出基础安装命令，不声称恢复了当时额外参数。

## clean 构建

```powershell
hvigorw --mode module -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon
```

该命令取自实际验证入口 [run_verification.ps1](project/hypium_tests/run_verification.ps1)，不需要运行这个脚本即可构建。当前完整轮次的 [build.log](logs/development-round-02/manual-full-round-02/build.log) 包含 `entry:clean` 与 `BUILD SUCCESSFUL in 17 s 695 ms`，[build.exit.txt](logs/development-round-02/manual-full-round-02/build.exit.txt) 为 `0`。复现时须确认命令退出码为 `0` 后再安装。

产物相对工程根路径为：

```text
entry/build/default/outputs/default/entry-default-unsigned.hap
```

留存的当前产物大小为 `9,121,443` 字节，SHA-256 为 `a3574072f81f37e14c0f0c1b335673d44e7aa1691c83488a065d4b7c91278a36`，见 [hap-file.json](logs/development-round-02/manual-full-round-02/hap-file.json)、[hap-sha256.json](logs/development-round-02/manual-full-round-02/hap-sha256.json)。该摘要标识留存产物；重新构建后应记录本次实际产物的大小和摘要。

构建保留了既有告警：`764` 条 ArkTS 诊断，以及 `No signingConfig found for product default`。按路径、消息与出现次数规范化比较，新增和缺失诊断均为 `0`；见 [warning-comparison.json](logs/development-round-02/manual-full-round-02/warning-comparison.json)。

## 安装、启动与应用标识

| 标识 | 值 |
| --- | --- |
| bundleName | `io.qzz.weiyu` |
| 入口模块 / target | `entry` / `default` |
| 主 Ability | `EntryAbility` |
| 主 Ability 源文件 | `entry/src/main/ets/entryability/EntryAbility.ets` |
| versionName / versionCode | `1.0.0` / `1000000` |
| 模型与设备类型 | Stage，`phone` |

标识来自 [AppScope/app.json5](project/AppScope/app.json5) 与 [module.json5](project/entry/src/main/module.json5)。

先通过已配置的设备管理器启动模拟器，并使用下列已记录命令查看设备：

```powershell
hdc list targets
```

以下使用完整自测实际设备序列号；在另一设备上复现时，将 `127.0.0.1:11237` 替换为 `hdc list targets` 显示的目标。安装和启动均在工程根执行：

```powershell
hdc -t 127.0.0.1:11237 install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:11237 shell aa start -a EntryAbility -b io.qzz.weiyu
```

安装参数取自 [run_verification.ps1](project/hypium_tests/run_verification.ps1)。[install.log](logs/development-round-02/manual-full-round-02/install.log) 记录 `install bundle successfully`，[install.exit.txt](logs/development-round-02/manual-full-round-02/install.exit.txt) 为 `0`；[installed-hap-manifest.json](logs/development-round-02/manual-full-round-02/installed-hap-manifest.json) 关联设备、安装时间、源码指纹与 HAP 摘要。启动参数与成功输出见 [基线验证记录](project/workflow/verification/baseline-round-01.md)、[start-app.log](project/traces/baseline-round-01/start-app.log)、[start-app.exit.txt](project/traces/baseline-round-01/start-app.exit.txt)；该次启动使用基线专用设备 `11235`，当前自动验证也显式使用相同 bundle 和 Ability。

基线及当前工程的 `signingConfigs` 为空，产出的是 unsigned HAP。本题基线模拟器直接安装 unsigned HAP 成功，见 [install-unsigned.log](project/traces/baseline-round-01/install-unsigned.log)、[install-unsigned.exit.txt](project/traces/baseline-round-01/install-unsigned.exit.txt)；当前完整轮次也有上述安装成功证据。正式实体机运行需评审者按其正常开发环境配置有效签名并安装对应签名产物；本次材料整理未修改签名配置，模拟器 unsigned 安装成功不代表实体机免签可安装。

## 首次初始化与手动检查

首次启动后，在隐私页选择“同意并进入”，引导页可选择“跳过”，随后进入首页。该真实入口由 [bootstrap_device.py](project/hypium_tests/bootstrap_device.py) 与 [首次使用测试](project/hypium_tests/test_restore_confirmation.py) 记录。普通启动无需导入测试数据、配置合成 WebDAV 服务或执行自动测试。

可按本题 [需求](project/spec/requirement.md) 做基本手动检查：

1. 首页齿轮进入设置，打开“WebDAV 配置”。为单独观察手动恢复行为，先关闭“启用自动同步”。
2. 点击“从云端恢复”，应立即出现标题“⚠️ 从云端恢复”的第一层确认，包含丢失本地未同步学习记录的提示及“取消”“继续”按钮。
3. 等待而不确认，随后点击“取消”；重新打开后分别用系统返回手势、点击弹窗外部关闭。三种取消都应回到可操作的同步页面，不进入下载或导入。
4. 若要检查“继续”路径，使用专门的测试账号与备份配置；第一层继续后仍须保留既有导入预览及第二层明确确认。纯 UI 手查不能替代无请求、数据库和 Preferences 不变的自动证据。

## 已有自动自测与移植边界

完整核心自测结果见 [selftest.json](logs/development-round-02/manual-full-round-02/selftest.json)、[hypium.log](logs/development-round-02/manual-full-round-02/hypium.log)、[hypium.exit.txt](logs/development-round-02/manual-full-round-02/hypium.exit.txt)：`13 pass / 0 fail / 0 skip`。补充继续分支、温后台及真实出站隔离的证据与范围见 [独立自测最终汇总](project/workflow/verification/round-01.md)；这些是本地验证结果，不是官方隐藏测试或成绩。

自动 13 项需要专用的合成数据模拟器、关闭并核实持久化自动同步、Python Hypium 与公共 `test-harness`、受控 WebDAV 服务、HDC 转发，以及从本轮冻结源码 clean 构建并新安装生成的 manifest。首项会清除本题应用数据后重装并恢复合成 fixture。这些条件仅用于独立自动验证，不是普通运行的必要初始化。

现有 [hypium_tests/README.md](project/hypium_tests/README.md) 与 PowerShell 验证脚本保存了原环境入口，含原机器的环境加载路径、工程根检查和 `PYTHONPATH`，因此不能声称复制成果包后原样直接可运行。本说明中的依赖、构建、安装和启动命令均独立于这些脚本。公共环境、Python 依赖和完整验证框架由 `3-package.md` 统一归档；重放自动验证前须按成果包实际目录适配设施路径，保留冻结、指纹、新安装及全部断言。不得把缺失 manifest、跳过或仅能发现测试当作通过。历史失败与重试由 `trace-index.md` 关联的原始日志保留。
