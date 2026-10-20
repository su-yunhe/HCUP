# cml-spec7 独立基线验证第 1 轮

## 结论与范围

2026-10-20，本轮独立构建、安装并实际操作了未修改业务源码的基线。构建和安装启动成功；从首页的“我的”→“点击登录账号”能够进入登录页。该页实际只有标题“登录”和正文“登录页面内容视图”，缺少 Logo、两个登录按钮、其他登录方式、第三方图标/标签和协议页脚。返回重进及冷启动后重新导航，结果相同。本轮不能判本题功能完成。

派工为 [dispatch-baseline-01.md](dispatch-baseline-01.md)。未实现业务、未更改 Spec、签名配置或依赖，未访问其他题工程/修复历史，未派生子 Agent。主 Agent 已确认测试期间业务源码冻结。

原生子会话 `CODEX_THREAD_ID=01a158b7-cf4a-7b83-8b86-51f14fe4c556`；`CODEX_SESSION_ID=01a158b5-95c1-7843-be11-cfb16aaa2e74` 是继承的主会话值，不作为子会话 UUID。

## 输入指纹与环境

| 项目 | 本轮实际值 |
| --- | --- |
| HEAD | `75fd0066a7fc0c1e8cedb6218df081f86d307f45` |
| Spec SHA256 | `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9` |
| 验收草稿 | `workflow/requirements/acceptance-draft.md`，SHA256 `f97a642a0e3b3ef0c15b5305a7aa72405dd56da7a0efa3370420359b65595f51`；只用于映射，仍为主 Agent 待审草稿 |
| 源码稳定性 | 开始、完整构建后、测试结束均为 794 个生产输入；差异均 `[]`；tracked/staged diff 均为空 |
| Windows / Python / Node | Windows 11 build 26200 / Python 3.12.3 / Node 18.20.1 |
| 工具链 | DevEco Studio 6.1.0.860；SDK API 23；Hvigor 6.23.7；hdc 3.2.0c；Hypium 6.1.0.210 |
| 工程配置 | target/compatible SDK `6.0.1(21)`；`signingConfigs=[]` |
| 设备 | `127.0.0.1:5555`，已有 `HarmonyCup_API23` 手机模拟器，Pura 90 Pro Max / PHEMU-FD00 |
| 运行镜像 / API | `emulator 6.1.0.115(SP11DEVC00E115R4P11)` / 实际查询 API `23` |
| 屏幕 | 实际 `1308 × 2880`；运行 density / virtualPixelRatio 均 3.5（逻辑密度相当于 560dpi）；配置 `hw.lcd.density=560`。DMS 另报物理 DPI X/Y 461.433/468.923，不将它混为逻辑 dpi |

证据：[closeout.json](../../logs/analysis-baseline/closeout.json)、[before](../../logs/analysis-baseline/fingerprint-before.json)、[after-build](../../logs/analysis-baseline/fingerprint-after-build.json)、[final](../../logs/analysis-baseline/fingerprint-final.json)、[工具版本](../../logs/analysis-baseline/tool-versions.txt)、[设备配置](../../logs/analysis-baseline/emulator-config.ini)、[运行屏幕](../../logs/analysis-baseline/runtime-display.json)、[API](../../logs/analysis-baseline/runtime-api.json)、[最终环境检查](../../logs/analysis-baseline/env-check-final.json)。harness 环境检查只核对镜像和分辨率；本报告另补运行 API 和密度证据。

初始 `hdc list targets` 返回 `[Empty]`，环境检查 exit=1。经主 Agent 授权，使用已安装 Emulator 启动已配置的 `HarmonyCup_API23`，没有创建/修改模拟器。安装前 AMS mission list 为空，前台为系统锁屏/桌面，无其他题正在运行的应用窗口；证据为 [AMS](../../logs/analysis-baseline/foreground-before-install.json)、[WMS](../../logs/analysis-baseline/windows-before-install.json)。设备启动后环境检查 exit=0。

## 构建、产物和告警

每个构建/设备命令所在 PowerShell 进程均先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1` 和 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。构建脚本：[baseline-build.ps1](baseline-build.ps1)。最终构建命令为：

```powershell
hvigorw --mode project -p product=default clean --no-daemon
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

两条退出码均为 0。最终 assembleHap 为 `BUILD SUCCESSFUL in 32 s 790 ms`；日志中实际执行 `CompileArkTS`，不是仅凭缓存成功。完整原始合并输出保存在 [build-full-raw.txt](../../logs/analysis-baseline/build-full-raw.txt)（116,754 字节，SHA256 `26c29957df10e5a86943c3325654f44e7aaa4dfd50abe397cae733244e3b3697`），命令、退出码和 HAP 哈希保存在 [build-full-transcript.txt](../../logs/analysis-baseline/build-full-transcript.txt)。

最终产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`：17,026,818 字节，SHA256 `792dc2809f4376f4d4c94a796d9c959305d300298870a00b1ee673bafc20f109`。此前第一轮 HAP 的 SHA256 为 `efa0976eca9c2f70ceb92c23698b0a60e71715fa79fd7d554494d8d58120c4a8`；最终 HAP 已重新安装，以下 `final-*` 和 `cold-*` 功能证据对应最终产物。

没有修改/隐藏警告。[warning-summary.json](../../logs/analysis-baseline/warning-summary.json) 包含所有 ArkTS 文件位置、原文、来源和统计；[分类脚本](baseline-warning-summary.py) 可复算。统计的是诊断出现次数，不声称是官方评分：

| 类别 | 次数 | 处理/归因 |
| --- | ---: | --- |
| ArkTS 文件诊断总数 | 207 | 207 个不同的“位置+消息”；依赖 153、工程 54 |
| strict typing 注释关闭检查 | 140 | 依赖声明；保留 |
| `this` 类型标注 | 1 | 依赖声明；保留 |
| 返回类型推断受限 | 8 | 依赖声明；保留 |
| 类型上下文 `typeof` | 2 | 依赖声明；保留 |
| API 可能抛异常，需特殊处理 | 34 | 原文逐条见 JSON；未以构建成功抵消风险 |
| `@BuilderParam content` 初始化方式 | 22 | designsystem Column/Row；保留 |
| 资源名重复 | 170 | 工程/依赖合并时出现；名称及两端路径见原始日志 |
| 重复 dayjs 文件名 | 1 | `dayjs.min.js` 与 `?commonjs-entry` |
| 缺少 sourceMapsPath | 1 | ibest-ui-v2 |
| 无 signingConfig | 1 | 当前配置事实；该模拟器实际接受本轮 unsigned HAP |

构建工具自动生成/更新 `.hvigor/`、模块 `build/` 与 BuildProfile 等输出。按构建起始时间登记了 1,247 个生成文件路径和大小，见 `closeout.json.generated_files`；生产输入内容仍无变化。未撤销他人的文件。

## 安装与实际操作

最终安装命令：

```powershell
hdc -t 127.0.0.1:5555 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell aa force-stop com.joker.coolmall
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b com.joker.coolmall
```

三个命令均 exit=0，且输出分别明确为 `install bundle successfully`、`force stop process successfully`、`start ability successfully`。没有更改签名配置或关闭校验。原始命令、退出码、stdout/stderr：[install-final.json](../../logs/analysis-baseline/install-final.json)、[stop-before-final-launch.json](../../logs/analysis-baseline/stop-before-final-launch.json)、[start-final.json](../../logs/analysis-baseline/start-final.json)；同名 `.stdout.txt`/`.stderr.txt` 保留原始字节。

首次启动出现麦克风权限对话框。本轮选择“不允许”；应用随后打开自身系统权限详情。保留默认不允许，返回系统详情再返回应用，可继续本题导航；未输入任何账号或第三方凭据。后续冷启动也会打开同样的权限详情，本轮通过返回恢复首页。此行为不改变登录页缺失控件的结论。

| 实际步骤 | 结果与证据 |
| --- | --- |
| 回到首页 | 可见“主页/分类/购物车/我的”；[截图](../../traces/analysis-baseline/final-home-visible.jpeg)、[树](../../traces/analysis-baseline/final-home-visible.ui.json) |
| 点击“我的” | 可见“未登录”“点击登录账号”；[截图](../../traces/analysis-baseline/final-me.jpeg)、[树](../../traces/analysis-baseline/final-me.ui.json)、[动作](../../logs/analysis-baseline/final-me-action.json) |
| 点击“点击登录账号” | 标题“登录”、正文“登录页面内容视图”；[截图](../../traces/analysis-baseline/final-login.jpeg)、[树](../../traces/analysis-baseline/final-login.ui.json)、[动作](../../logs/analysis-baseline/final-login-action.json) |
| 返回再进入 | 返回“我的”，再次进入仍为占位页；[返回树](../../traces/analysis-baseline/final-return-me.ui.json)、[重进截图](../../traces/analysis-baseline/final-reenter-login.jpeg)、[重进树](../../traces/analysis-baseline/final-reenter-login.ui.json) |
| 强停/冷启动后再进入 | 显式 aa force-stop/start 后，返回权限详情，再经“我的”→登录，结果相同；[冷启动命令](../../logs/analysis-baseline/cold-start.json)、[冷启动重进截图](../../traces/analysis-baseline/cold-login.jpeg)、[树](../../traces/analysis-baseline/cold-login.ui.json)、[退出码](../../logs/analysis-baseline/cold-reentry-exit.txt) |

[baseline-ui.py](baseline-ui.py) 用 Hypium 点击实际发现的文字，按步骤保存 UI 树、截图、组件边界、命令及 stdout/stderr，每次动作成功退出 0。没有以测试 id 代替真实页面内容。

[baseline-login-assertions.py](baseline-login-assertions.py) 在重进后的真实页面独立查找 9 项文字：标题“登录”1 项可见，`手机号登录/账号密码登录/其他登录方式/微信/QQ/支付宝/用户协议/隐私政策` 8 项失败，脚本 exit=1。证据为 [断言 JSON](../../logs/analysis-baseline/login-assertions.json)、[原始控制台](../../logs/analysis-baseline/login-assertions-console.txt)、[退出码](../../logs/analysis-baseline/login-assertions-exit.txt)。A1 的导航 pass 另有真实进入前后证据，不只凭标题断言。Logo/图标缺失还经过截图和完整 UI 树核对。

## 逐需求基线状态

映射冻结草稿的 41 个明文项：`pass=1 / fail=11 / blocked=25 / not_run=4`。`blocked` 表示缺少真实前置控件，不能执行点击或量测；不算通过。手机截图已实测，平板和更宽设备均未实测。没有伪称点击过缺失控件。

| 编号 | 状态 | 实际结论/阻断 |
| --- | --- | --- |
| A1 | pass | 从“我的”真实入口进入登录页；返回及冷启动后可重复 |
| A2 | fail | 登录页无应用 Logo |
| A3 | blocked | 无 Logo，无法判断顶部位置 |
| A4 | blocked | 无 Logo，无法量测居中 |
| A5 | blocked | 无 Logo，无法量测 120 尺寸 |
| A6 | fail | 无“手机号登录”按钮 |
| A7 | blocked | 无 Logo/手机号按钮，无法量测相对位置 |
| A8 | blocked | 无手机号按钮，无法核对实心样式 |
| A9 | blocked | 无手机号按钮，无法核对圆角 |
| A10 | fail | 无“账号密码登录”按钮 |
| A11 | blocked | 无 Logo/账号按钮，无法量测相对位置 |
| A12 | blocked | 无账号按钮，无法核对空心样式 |
| A13 | blocked | 无账号按钮，无法核对圆角 |
| A14 | blocked | 无手机号按钮，未执行短信页跳转 |
| A15 | blocked | 无账号按钮，未执行密码页跳转 |
| B1 | fail | 无“其他登录方式”文字 |
| B2 | blocked | 无提示/按钮，无法量测上下位置 |
| B3 | fail | 无微信、QQ、支付宝图标 |
| B4 | blocked | 无图标/提示，无法量测上下位置 |
| B5 | blocked | 无三图标，无法量测间距 |
| B6 | fail | 无微信文字说明 |
| B7 | fail | 无 QQ 文字说明 |
| B8 | fail | 无支付宝文字说明 |
| B9 | blocked | 无微信入口，未启动第三方流程 |
| B10 | blocked | 无 QQ 入口，未选择快速登录 |
| B11 | blocked | 无支付宝入口，未选择快速登录 |
| B12 | fail | 无用户协议文字入口 |
| B13 | fail | 无隐私政策文字入口 |
| B14 | blocked | 无用户协议入口，未打开详情 |
| B15 | blocked | 无隐私政策入口，未打开详情 |
| B16 | fail | 无完整登录同意文案 |
| B17 | blocked | 无同意文案，无法确认最底部位置 |
| B18 | blocked | 无用户协议链接，无法核对主题色 |
| B19 | blocked | 无隐私政策链接，无法核对主题色 |
| C1 | blocked | 已实测手机，但无按钮区可量测全宽 |
| C2 | not_run | 未运行平板设备/窗口，未量测 70% |
| C3 | not_run | 未运行平板设备/窗口，未量测居中 |
| C4 | not_run | 未运行更宽设备/窗口，未量测 60% |
| C5 | not_run | 未运行更宽设备/窗口，未量测居中 |
| C6 | blocked | 手机无图标；其他尺寸未运行，无法核对均匀间隔 |
| C7 | blocked | 手机无图标/按钮区；其他尺寸未运行，无法核对区域归属 |

## 最小复现、归因与下一步

最小复现：加载本题环境→运行最终构建命令→安装本轮 HAP→启动 EntryAbility→若麦克风权限详情出现，保持不允许并返回应用→首页“我的”→“点击登录账号”。期望为 Spec 的 Logo、主/次登录按钮、三方区域和底部协议；实际仅“登录页面内容视图”。返回重进和强停重进相同，实时文字断言 exit=1。

关联 A2/A6/A10、B1/B3/B6–B8/B12/B13/B16；其余布局/点击项缺前置。证据强度高：最终产物安装、真实操作、截图、UI 树、独立实时查询和稳定源码指纹相互吻合。只读源码 `feature/auth/src/main/ets/view/LoginPage.ets` 的 LoginContent 也仅包含该占位 Text，LoginViewModel 为空；这是归因补充，未拿静态阅读代替设备验证。推测为基线尚未实现本题登录主页，建议主 Agent 进入方案/编码角色，而非通过调整测试或环境把功能记为通过。

微信/QQ/支付宝真实授权、认证请求、取消/失败恢复、协议正文、平板/大屏适配、横屏及窄窗口等均没有通过证据。本轮未抓取登录网络请求，不对是否发请求、凭据有效性或官方成绩作断言。首页曾出现网络异常/重试，不影响已本地复现的登录占位页缺失结论。

## 证据缺口与工具故障（保留，不伪造）

1. 初轮 `Start-Transcript` 没有保留原生程序 stdout：`build.txt` 仅 1,218 字节，初始 preflight 也缺 hdc 原始输出。最终构建已用 `Tee-Object` 禁用增量重新取证；后续设备命令改为 subprocess 原始字节捕获。初始 `[Empty]` 仅有工具返回记录及 [明确标注的转录](../../logs/analysis-baseline/initial-device-observation-transcription.json)，不冒充初始原始 stdout 文件。初始原始文件缺口不可追补，后续成功设备证据完整。
2. 初次 `snapshot_display -f *.png` 实际报 suffix must be `.jpeg`，hdc 仍 exit=0；对应 [错误原始输出](../../logs/analysis-baseline/initial-screenshot.stdout.txt)、[接收失败](../../logs/analysis-baseline/initial-screenshot-recv.stdout.txt) 保留。后续全部使用 JPEG，实际成功并接收，未把该失败记成截图成功。
3. Hypium `start_app(bundle)` 未传 page_name 时实际失败：`Fail to get main ability ... please specify one`，脚本 exit=1；[错误控制台](../../logs/analysis-baseline/final-cold-restart-console.txt)、[动作错误](../../logs/analysis-baseline/final-cold-restart-action.json) 保留。随后使用实际 module 中的 EntryAbility，通过显式 hdc aa 命令完成冷启动/重进，未将工具故障归为业务失败。辅助脚本现提供显式 page_name，最终冷启动证明使用的仍是已记录的 hdc 命令。

本轮结束时模拟器保持运行、前台为本题登录占位页；没有停止/卸载其他应用。主 Agent 可以据本报告更新 `spec/baseline-notes.md` 并决定下一阶段；本子 Agent 未改全局 workflow 状态。
