# vg-spec1 基线笔记

执行范围为 `spec-harness/0-analyze.md`，仅记录未修改基线。本文件在本轮重新构建、安装、启动及实际操作完成后，由主 Agent 汇总独立验证报告与静态代码审查。详细原始报告为 `workflow/verification/baseline-round-01.md`，结构化结果为同名 JSON；需求标准见 `spec/acceptance.md`。结论：基线可构建、安装、启动并进入恢复入口；**第一层确认缺失**。已配置隔离探针时，未收到任何用户确认即发起 HEAD/GET，GET 返回 403，未取得备份正文。此报告不表示实现完成、官方测试通过或得到官方成绩。

2026-10-17 自动同步状态更正：原报告将开启的开关误写为关闭，属于验证者判读错误。原稿已保留，详见 `workflow/verification/correction-autosync-01.md`。实际开关开启；手动请求归因由调用链、命令时间线和日志交叉支持，不能再称自动同步已关闭隔离。

## 快照与隔离

- 根目录：`D:/HCUP/vg-spec1`；HEAD：`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。
- 验证会话：`01a148ab-4616-7133-b3ee-22512ca72dd7`；2026-10-17 15:03 开始，UTC+08；结束时间见同名 JSON 的 finishedAt。
- Spec SHA256：`cb03466bca1943ed5d0e5d191f14607fb2e9b7d6195540275be8c9205477ec48`；metadata SHA256：`92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。
- 开始时 `hdc list targets` 为 `[Empty]`，未发现模拟器/DevEco 占用。主 Agent 授予本轮设备独占权，本轮没有其他角色操作设备；其他角色仅写分析文档。
- `source-before.json`/`source-after.json` 覆盖 298 个 tracked 文件，排除原已修改的 `AGENTS.md`；前后差异 0。生产路径 `git diff` 为空，未改生产代码、Spec、业务配置或全局 workflow state/events。
- 构建生成物在 `entry/build/`、`.hvigor/`，完整列表为 `generated-artifact-inventory.csv`；没有新增 tracked 生产改动。原有 `AGENTS.md` 修改未触碰。
- 所有 PowerShell 进程首先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。没有读取其他题、上游历史、题包或初始化总览 trace。

## 环境、构建与告警

PowerShell 7.6.5；DevEco Studio 6.1.0.860；`DEVECO_SDK_HOME=D:/HarmonyDev/sdk/api23`；JBR 位于 `D:/HarmonyDev/DevEcoStudio-6.1.0/jbr`。工具精确位置见 `environment.json`。已加载 `hmos-arkts-syntax-checker` 技能用于编译诊断，本阶段禁止自动修源码，实际没有执行修复。

实际构建命令（当前工作目录为工程根）：

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
& hvigorw --mode module -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon 2>&1 | Tee-Object -FilePath traces/baseline-round-01/build.log
$buildCode=$LASTEXITCODE
$buildCode | Set-Content -LiteralPath traces/baseline-round-01/build.exit.txt
```

退出码 0，`BUILD SUCCESSFUL in 46 s 306 ms`。使用现有 API 22 product 配置（`build-profile.json5:7-8`）、当前 API 23 工具链，没有降级或更改配置。构建输出 `entry/build/default/outputs/default/entry-default-unsigned.hap`，9,065,537 字节，SHA256 `E8467AC516C1B4C90A21586C08F99DBF4EA35CAFA6742BC132753BC547021451`。产品签名配置为空（`build-profile.json5:3`），未在产物副本上另行签名；本模拟器直接安装未签名 HAP 成功。

**告警基线：764 条带路径/行列的唯一 ArkTS 诊断，另加 1 条无签名配置告警，共 765 条实际诊断。** FAQ 提示行单列为说明，不计诊断。完整原始日志为 `build.log`；逐项清单为 `build-warnings.csv`/`build-warnings.json`，分类为 `build-warning-summary.json`，生成脚本为 `summarize_build.py`。

| 类别 | 数量 |
| --- | ---: |
| Function may throw exceptions | 498 |
| 弃用 API | 260 |
| ESObject/globalThis/classes-as-object 规范 | 4 |
| 可选 @Prop | 2 |
| No signingConfig found for product default | 1 |

弃用 API 明细：showToast 132、back 32、pushUrl 27、getContext 25、showDialog 11、SetOrCreate 6、getParams 6、decode 5、createAudioPlayer/src/play 各 3、animateTo/release 各 2、encode/setPasteData/getLength 各 1。没有修复或忽略这些既有告警。

## 设备与安装启动

创建了本题专用空白实例 `VgSpec1Baseline`，位置 `traces/baseline-round-01/emulator-instances`，未使用现有共享实例，也未连接真实用户云端。实例镜像是已安装的 HarmonyOS 6.1.0(23)，设备返回 `OpenHarmony-6.1.0.115`，x86_64，Pura 90 Pro，1256×2760，density=3.5（560 dpi），60 Hz。系统参数与原始配置分别见 `device-version-connected.log`、`device-screen.log`、`device-display-manager.log`、`emulator-instance-config.txt`。

本地通用测试框架记录的目标为 Pura 90 Pro Max 1308×2880/560 dpi、API 23（`test-harness/harness/env_check.py:17-23`）；本轮设备尺寸不同，因此本轮不能作为该目标机型的布局适配通过证据。项目目标/兼容 API 22，本轮运行 API 23；没有在 API 22 或实体手机上运行。

关键命令：

```powershell
& D:/HarmonyDev/DevEcoStudio-6.1.0/tools/emulator/Emulator.exe -create VgSpec1Baseline -deviceType phone -osVersion 'HarmonyOS 6.1.0(23)' -instancePath D:/HCUP/vg-spec1/traces/baseline-round-01/emulator-instances -imageRoot D:/HarmonyDev/emulator/images
# Start-Process -WindowStyle Hidden 启动，完整参数见 emulator-running-processes.json
hdc tconn 127.0.0.1:11235
hdc -t 127.0.0.1:11235 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:11235 shell aa start -a EntryAbility -b io.qzz.weiyu
```

连接、安装、启动均成功；安装/启动单项退出码均 0，日志分别为 `hdc-connect.log`、`install-unsigned.log`、`start-app.log`。应用 `io.qzz.weiyu`，versionName=1.0.0，versionCode=1000000，appSignType=none；详见 `app-installed.log`。PID 3555，末次 mission 为 FOREGROUND（`foreground-after.log`）。

初次使用先显示隐私政策，同意后显示使用引导，点击“跳过”进入首页。配置输入首次唤起系统小艺输入法的首次同意和键盘布局引导，本轮在空白模拟器完成引导后输入伪凭据。相关系统弹层见截图 09-11，不属于恢复确认框。

## 实际入口与交互证据

所有证据路径以下均相对 `traces/baseline-round-01/`，每个编号都有 PNG 和 JSON UI 树。后续设备命令的时间、参数、返回值和退出码保存在 `device-commands.log`，调用帮助脚本为 `device-helpers.ps1`。HDC 在部分失败输出时仍返回 0，本报告同时检查文本和退出码。

1. `01-start`：首次隐私政策；`02-after-privacy`：使用引导。
2. `03-home`：首页右上角 `⚙`。点击该图标进入 `04-settings`。
3. `04-settings`：列表项 **WebDAV 配置**，并非相邻的“备份与恢复”；点击进入 `05-webdav-top`。
4. `05-webdav-top`：空地址/账号/密码/同步密码，默认远端目录 `/weiyu_vignette`。**自动同步开关实际开启**：截图为蓝色右侧，原始 UI 树为 `checked=true`；`selected=false` 不能当作关闭状态。`WebDavStateStore.ets:172` 的未设置默认值也是 true。原报告的“未开启”错误已更正。
5. 上滑后 `06-webdav-actions`：保存设置、测试连接、立即同步、立即备份、**从云端恢复**。恢复按钮 enabled=true、clickable=true、id 为空。
6. 点击恢复，`07-unconfigured-restore`：直接显示 `⚠️ 未配置 WebDAV 地址：WebDAV endpoint is empty` 和 toast。没有 `⚠️ 从云端恢复`、`取消`、`继续`。五个操作按钮均恢复 enabled=true。该按钮恢复是**配置错误后的状态**，不能记为取消路径通过。
7. 使用伪账号 `baseline_user`、伪密码与测试同步密码，地址 `http://127.0.0.1:28761`；`13-probe-filled` 为字段证据。配置仅写入本题空白模拟器。`15-probe-saved` 显示保存成功。
8. 点击恢复，`16-configured-restore` 显示 `⚠️ 下载失败：GET 403: `，没有第一层。全部操作按钮恢复可用。用户没有点击任何“继续”或“确认恢复”。

独立 HTTP 探针 `readonly_webdav_probe.py` 仅绑定主机 127.0.0.1:28761，通过 `hdc rport tcp:28761 tcp:28761` 暴露给本题模拟器；HEAD 返回 200，所有其他方法返回 403，不保存任何备份正文、写入或删除数据。服务器保存请求方法/路径/正文长度/返回码，不保存 Authorization 值。首次恢复前请求日志为空；未点击测试连接/同步/备份，也未主动切换自动同步。**开关保持默认开启，没有通过关闭自动同步隔离**。下述归因不能以“未主动打开”替代“实际关闭”。

请求归因依据：`AutoWebDavSyncManager.tryRun` 的唯一工程调用在 `EntryAbility.ets:53-54` 的 onForeground；`AutoWebDavSyncManager.ets:44` 在未配置时直接返回；保存 WebDAV 配置只更新/持久化设置（`WebDavSyncManager.ets:111-121`），不触发 tryRun。命令时间线在主机 15:10:04.124 保存配置，之后只有截图/UI 树/只读文件查询，再于 15:10:13.661 手动点击恢复；期间无后台/前台动作。该观察窗口 PID 3555 的 hilog 没有 `autosync start` 或 Ability onForeground，只记录与探针相符的三次请求。`SettingsSyncSection.ets:164-165`、`:199-200` 的手动恢复链直接调用下载方法。调用链与完整交互时间线、实际服务端请求相互支持，足以将本轮三次请求归于手动恢复；日志“未出现”只作支持证据，不能单独证明自动同步被禁用。未为此次更正重跑设备。

2026-10-17 15:10:14 UTC+08 一次恢复点击产生：

| 顺序 | UTC 时间 | 方法与路径 | 状态 |
| --- | --- | --- | --- |
| 1 | 07:10:14.407075 | HEAD `/weiyu_vignette` | 200 |
| 2 | 07:10:14.435431 | HEAD `/weiyu_vignette/backup.json.enc` | 200 |
| 3 | 07:10:14.472328 | GET `/weiyu_vignette/backup.json.enc` | 403，0 字节正文 |

原始记录为 `webdav-requests.jsonl`。这是**发起下载请求的证据**，不是成功下载、解密、预览或覆盖的证据。未构造成功的加密备份，没有实际走到原有第二层确认或导入。本轮没有观察到 PUT/DELETE，不能据此否定其他预检分支可能发起这些请求。

已保留两次 hilog 原始快照。`hilog-app-3555.log` 是第二次环形日志快照中 PID 3555 的 254 行，包含 4 条 W、10 条 E、0 条 F；计数不代表完整应用生命周期。出现 RdbService、NETSTACK handover/tcp info、NAPI worker 等系统级诊断，详见原文；实际 HEAD/GET 已到达探针，不能将这些诊断推断成此次入口缺失的根因。没有额外修改系统来消除日志。

## 逐需求状态

按已发布 `spec/acceptance.md` 的 R01-R28 记录基线。`blocked` 表示必要第一层或数据观测前置不存在；`not_run` 表示本轮基线范围未运行。任何 blocked/not_run 都不是通过。

| ID | 状态 | 基线证据及限制 |
| --- | --- | --- |
| R01 | pass | 03-06 实际沿设置进入并点击目标按钮。 |
| R02 | fail | 07 无配置直接报错；16 已配置直接发起请求并失败。 |
| R03 | fail | 第一层及规定标题不存在，07/16 UI 树。 |
| R04 | fail | 风险文字只在背景使用说明；没有第一层正文。 |
| R05 | fail | 没有第一层取消入口。 |
| R06 | fail | 没有第一层继续入口。 |
| R07 | fail | 没有等待选择阶段，已配置路径自行发起请求。 |
| R08 | fail | 未选择任何确认即产生 GET；403 未获得正文。 |
| R09 | blocked | 第一层不存在；未做用户学习数据哨兵/语义摘要比对。 |
| R10 | blocked | 没有第一层，无法点击其取消。 |
| R11 | blocked | 没有第一层，无法直接关闭该层。 |
| R12 | blocked | 没有第一层，系统返回手势取消路径不可执行。 |
| R13 | blocked | 没有第一层，蒙层外部关闭路径不可执行。 |
| R14 | blocked | 三种取消等价性没有可操作前置。 |
| R15 | blocked | 第一层取消后终止不可验证。 |
| R16 | blocked | 取消路径不可执行；不能用 GET403 代替零请求通过。 |
| R17 | blocked | 取消路径缺失，且没有本地哨兵数据语义比对。 |
| R18 | blocked | 取消路径缺失；错误结果后的状态不等同取消不变。 |
| R19 | blocked | 错误返回后按钮可用，但没有测试取消后的按钮状态。 |
| R20 | fail | 未选择前实测 HEAD×2、GET×1。 |
| R21 | blocked | 第一层取消/loading 清理路径不可执行。 |
| R22 | not_run | 没有进一步运行重复/快速点击测试。 |
| R23 | blocked | 无取消前置，不把错误后可点击记为本项通过。 |
| R24 | not_run | 本轮未运行取消后返回重进。 |
| R25 | not_run | 本轮未运行未确认/取消后强停重启。 |
| R26 | fail | 空配置子项实测未先确认；纯空白/无云端数据子项未运行。 |
| R27 | fail | GET403 服务端失败路径仍无第一层；离线/延迟子项未运行。 |
| R28 | blocked | 没有第一层继续，无法验证单次交接。 |

汇总仅是本地基线状态：1 pass、10 fail、14 blocked、3 not_run，不是官方 F-point 计数或成绩。

## 源码现状与可复用入口（静态证据）

除显式给出的工程根路径外，下面 `pages/`、`sync/`、`utils/`、`database/`、`model/` 开头的源码引用均相对 `entry/src/main/ets/`。所有代码结论为静态实证；运行事实以上述命令、UI 树和服务端日志为准。

- 启动 `entry/src/main/ets/entryability/EntryAbility.ets:35` loadContent `pages/Index`；路由声明 `entry/src/main/resources/base/profile/main_pages.json:7`。
- 首页 `pages/index/components/TopNavigation.ets:69` 的齿轮 Column；`pages/Index.ets:323` 的 onSettingsClick 调用 router.pushUrl `pages/SettingsPage`。首次隐私与引导在 `Index.ets:285`、`:116`。
- 设置项 `pages/SettingsPage.ets:40` 的 sync 数据，`:511` 改 activeSectionId，`:427` 渲染 SettingsSyncSection；这是同页区域切换，不是额外 WebDAV 路由。页面状态/配置字段在 `:114`，`:190` 从 manager 载入。
- `pages/settings/SettingsSyncSection.ets:41` 的结果/忙状态、`:140` 的 backup action 包装、`:164` 恢复动作、`:199` 下载/预览/原有确认、`:507` 恢复按钮可复用。现有弹框标题 `⚠️ 恢复确认`，按钮 `取消`/`确认恢复`（`:215`），属于下载后的第二层，未在本轮实际触达。
- 配置模型 `sync/webdav/WebDavCommon.ets:49`；结果模型 `:185`、`:207`；服务 `sync/WebDavSyncManager.ets:471` 下载与 `:502` 导入。
- 持久化 `utils/WebDavStateStore.ets:63` 的 Preferences 名称 `webdav_state_store`；`:166` 存本地快照。`sync/webdav/WebDavBackupManager.ets:96` 至 `:98` 在 GET 之前导出并保存快照；这是源码调用链证据，**本轮没有提取设备 Preferences 证实落盘**。
- `sync/DataSyncManager.ets:351` 为 previewImport，`:207` 为 importData。它们可用于保留原有后续流程，但当前第一层缺失。
- 主 Agent 的额外静态副作用分析见 `workflow/requirements/coordinator-code-audit-01.md`，包括其他预检分支的 PUT/DELETE 可能性和超时未取消底层 Promise 风险；其静态结论不冒充本轮实测。

## 数据模型、网络服务与本地存储补充（静态证据）

| 领域 | 基线位置与写法 | 对后续实现/验证的影响 |
| --- | --- | --- |
| WebDAV 配置、结果与状态 | `sync/webdav/WebDavCommon.ets:3` 的 IDLE/RESTORING 等状态；`:49` 的 WebDavSettings 包含地址、凭据、同步密码和远端目录；`:185`、`:207` 的同步/明文结果模型。`SettingsSyncSection.ets:25-43` 通过 @Link 链接父配置，@State 保存两个结果区与 busy。 | 复用既有模型与父子数据流；等待用户确认不能等同正在执行网络恢复。无需为此另建配置或恢复系统。 |
| 备份数据 | `sync/DataExportImport.ets:15-31` 的 ExportedWord 包含 status、fsrsState、history、dueDate 等具体字段；`:144-152` 的 ExportData 包含 words、definitions、userBooks、versionControl、fsrsParamsJson。 | 数据不变要比对本地独有记录和冲突字段，不仅比总条数。导出 timestamp 可能变化，不能把非语义时间字段误算成学习记录覆盖。 |
| 预览与导入 | `sync/DataSyncManager.ets:64-69` 是 ImportPreview 计数/错误/样例模型；`:351` 的 previewImport 读取对照；`:207-255` 的 importData 修改 FSRS 设置与词条记录。 | 原有继续后链路可复用；预览和导入不是同一个副作用阶段。本轮未成功运行二者，不能宣称数据完整性通过。 |
| 数据库 | `database/DBManager.ets:83-85` 配置 `vignette.db`；`:166-182` 通过 relationalStore.getRdbStore 初始化各 Repository 和 SchemaManager；`:258-271` 委派词条插入/更新。`database/DBConstants.ets:9-20` 列出 words、definitions、review_events、user_word_books 等表，`:28-38` 定义词状态、FSRS、history 等列。 | 数据验证的对象有明确位置；这些是结构证据，本轮没有直接读取沙箱数据库或验证取消后的字段相等。不能因表存在就推断所有表都在备份中。 |
| WebDAV 持久化 | `utils/WebDavStateStore.ets:63` 命名 Preferences；`:128` 打开；`:146-167` 分别通过 get/saveJsonWithBackup 读写 settings、manifest、snapshot。`WebDavSyncManager.ets:138-156` 初始化时读回。 | 页面局部状态和落盘数据要分开观测；第一层不得为了确认就调用会导出/保存快照的下载链路。快照实际落盘未验证。 |
| HTTP 服务 | `sync/webdav/WebDavClient.ets:6` 使用 @ohos.net.http；`:27-38` 构造 Basic Auth 并暴露 GET/HEAD，`:41` PUT、`:74` DELETE；`:123-140` 创建请求并设置请求参数。`WebDavSyncManager.ets:280-339` 做远端目录预检。 | 以服务端记录核验实际请求；已实测 HEAD×2/GET×1。其他预检分支可能写探针或创建目录是静态事实，不是本轮实际发生的请求。 |

## 可复用的既有模式与缺失项

- **入口/路由复用**：首页齿轮沿 `pages/Index.ets:323` 跳到 `pages/SettingsPage`；WebDAV 为 `SettingsPage.ets:427-442` 的子区域。官方流程可沿此入口进入，不需要另建 WebDAV 页面或绕开设置列表。
- **确认模式复用**：本地 JSON 导入 `pages/settings/SettingsBackupSection.ets:152-190` 采用 previewImport → showDialog → 检查取消 index → importData，并在 catch 退出；这是可参考的取消/继续模式。它先预览本地 JSON，不代表本题可以先下载云端再做第一层确认。原有 WebDAV 预览层也可在用户继续之后保留作回归。
- **业务服务复用**：保留 WebDavSyncManager、DataSyncManager、WebDavStateStore 既有职责（上述行号）；将新确认门禁与既有后续流程的交接列入方案，具体实现方式本阶段不决定。

| 缺失或风险 | 证据 | 后续验收关联 |
| --- | --- | --- |
| 下载前的第一层风险确认及精确标题/取消/继续 | 实测 07/16 的 UI 树无该层；`SettingsSyncSection.ets:164-165` 直接进入动作包装，`:199-220` 在下载后才确认。 | R02-R07。 |
| 等待确认时阻止恢复链路启动 | 实测 `webdav-requests.jsonl` 未确认就 HEAD/GET；静态 `WebDavBackupManager.ets:96-101` 还有导出/存快照。 | R08-R09、R20；不能只阻止最终 import。 |
| 第一层取消、手势关闭、外部关闭及等价终态 | 第一层不存在，无法实际执行这三个分支。已有第二层 `SettingsSyncSection.ets:224-230` 的取消/catch 不弥补前置下载。 | R10-R19、R21、R23；本轮为 blocked，非通过。 |
| 第一层取消后保留原 UI/结果并可再次操作的行为 | `SettingsSyncSection.ets:140-156` 先写 busy/处理中，结果包装会写操作结果；没有第一层对应的退出路径。 | 后续需以 UI0、enabled、重进/重启及真实数据观测补证；本轮只记录。 |
| 目标组件缺固定 id | `SettingsSyncSection.ets:270-277`、`:446-465`、`:481-526`；`SettingsPage.ets:549` 仅动态根 id。 | 属于可观测性风险，建议实现时补可用 id；不是强制更换原生弹框技术。 |

## 选择器、前置环境与未验证项

- 目标入口、WebDAV 配置项、五个输入框、恢复按钮、结果区均无固定 id。UI 树可按精确按钮文本进入，但 busy 文案统一改为“处理中...”，多个“显示”、多处风险说明文本会导致全局文本选择歧义；页面根只有 `settings_<theme token>`。后续测试需使用已确认稳定 id 或弹框独立窗口作用域。
- 本轮坐标来自当次 UI 树，只适用于本轮 1256×2760 设备，不是稳定的官方机型定位方案。
- 无云端账号要求即可进入设置；触发实际恢复服务需要已保存地址、账号/密码、至少四字符同步密码。本轮只用了隔离地址/伪凭据；成功恢复仍需合法加密备份与差异数据。
- 学习记录、词状态、词书等语义不变**未验证**。尝试通过 HDC debug bundle `find .`/`ls /data/storage/el2/base` 获取沙箱只得到 Permission denied/No such file；原始输出为 `device-files-before-restore.txt`、`device-files-after-restore.txt`、`device-sandbox-access.log`。没有用 root/删除/重置绕过，也没有把这些阻断算通过。
- 未验证真实云端、成功下载、解密、原有第二层取消、最终导入、各取消方式的零请求零写入、数据持久性、连点、重启、多设备适配或隐藏测试。

## 最小复现与建议交接

**F01：第一层确认缺失。** 期望：空白本题实例进入首页齿轮 → WebDAV 配置 → 上滑 → 从云端恢复，先显示标题 `⚠️ 从云端恢复`、风险正文、`取消`、`继续`，未选择前不进入恢复流程。实际：未配置直接显示配置错误；已配置到隔离探针时未经选择就 HEAD/GET，随后 GET403 下载失败。关联 R02-R08、R20、R26-R27。证据强度高：两条 UI 树/截图、设备命令与本地服务端请求原始日志相互印证；没有毫秒性能或成功覆盖结论。

归因假设：恢复按钮直接进入 busy 包装和下载/预览方法，第一层门禁不存在（`SettingsSyncSection.ets:164`、`:199`）。建议主 Agent 把此项交给方案/编码阶段处理，并在后续验证时分别实测取消按钮、系统手势与外部关闭；本轮不修代码。

**环境插曲均已有限处理并留证：** 第一次使用 `Phone` 与带连字符名称创建时，CLI 退出 0 却未生成实例；第二次使用实际镜像列表中的 `phone` 与 `VgSpec1Baseline` 创建成功，未单独隔离两参数，不能断言唯一根因。HDC 需显式 `tconn`；使用带 `/` 的 Windows 绝对接收路径被工具拼接出错误路径，改用工作目录下反斜杠相对路径后成功。`rport rm` 被工具拒绝，最终使用 `fport rm tcp:28761 tcp:28761` 成功清除本轮反向规则，原始失败及最终成功均在 device-commands.log。

临时 HTTP 探针 PID 32412 已校验命令行并停止（`probe-cleanup.json`）；转发最终 `[Empty]`（`forwarding-final.log`）。独立模拟器 PID 19336 保留供主 Agent 复查，应用停在已配置探针失败后的 WebDAV 操作区，**自动同步开关保持开启**；本轮更正仅检查已有证据，没有操作设备改变它。保存的 endpoint 仅为已停止的本地测试地址，后续重新前台可能尝试自动同步；下一轮探针应先关闭开关并核对截图/checked 属性，再建立请求计数窗口。重跑探针需先启动脚本并重新建立 rport。没有异常探针后台进程残留。

生产代码保持不变；最终复核 `source-final-comparison.json` 仍为 298 文件、0 变化。`evidence-manifest.json` 为本轮直接证据文件的 SHA256 索引，保留中的模拟器 stdout/stderr 属于仍可变化的打开文件，已明确排除冻结哈希；虚拟磁盘/实例目录也未纳入哈希索引。本轮分析产物已汇总到本文件与 `spec/acceptance.md`；后续只有进入开发阶段后才推进方案、编码与功能验证。当前不能标记整题 local_validation_complete。
