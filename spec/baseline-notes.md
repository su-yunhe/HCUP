# vg-spec14 基线现状记录

测试日期：2026-10-16，主机时区 Asia/Shanghai。以下请求时间统一使用 UTC；设备命令原始记录保留 `+08:00`。本轮仅执行 `spec-harness/0-analyze.md` 的分析基线验证，不改生产源码、构建配置、既有测试或 Spec。

证据分类：`SPEC_EXPLICIT` 仅指 `spec/requirement.md` 明文；`CODE_FACT` 指下述带文件/行号的源码事实；`RUNTIME_FACT` 指本轮日志、UI 树或截图观测；`INFERENCE` 为源码推断；`UNVERIFIED` 为尚未实测。原始角色报告保留在 `workflow/design/baseline-map-v1.md`、`workflow/verification/baseline-run-v1.md`，本文件在构建、安装和实际操作完成后汇合。验收编号和假设决策见 `spec/acceptance.md`，不把基线表现直接升级为 Spec 要求。

结论：**基线构建、安装、真实入口导航及真实 WebDAV 请求可运行；Spec 所要求的 ArkUI `LoadingProgress` 缺失，基线不满足两个场景的完整要求。** 该结论来自本次重新构建和实际操作，不以初始化构建、静态阅读或官方演示替代运行证据。没有官方成绩或隐藏测试结果。

## 1. 基线快照与证据有效性

- HEAD：`88db8789e28333c7b7dcc8db078f394a262b73c3`，与 `spec/metadata.json` 一致；未打新 tag。
- Spec SHA256：`22ca2ecd1c5749dd8abc972854eee167a3aa3fa0e3cf17ab2a16f424643ae3d4`。
- 构建前后对全部 295 个已跟踪文件逐一 SHA256（排除已有指导变更 `AGENTS.md`）相同。两份清单 SHA256 均为 `38a68b171673c7d55ec3b3af6b445762536f85ad5128606dd5f059dcad01262d`。
- 原始清单：[source-before.json](../logs/analysis-baseline/source-before.json)、[source-after.json](../logs/analysis-baseline/source-after.json)；比较结果：[integrity-result.json](../logs/analysis-baseline/integrity-result.json)。没有源码指纹变化导致的证据失效。
- `git diff --name-only` 仅有既存 `AGENTS.md`。本 Agent 新写入内容限本报告与 `logs/analysis-baseline/`；其他 Agent 的文档改动保留。
- 运行器 `CODEX_THREAD_ID=01a142ac-5fc9-7dc3-b649-dc3ce4910ab8`。`CODEX_SESSION_ID=01a142a8-0cc3-7ba2-8729-a773fd70d69b` 与主会话相同，不能当作独立子会话 ID。

`AGENTS.md` 的既存追加指导在本轮前已存在，未改动；与初始化指纹比较全部跟踪文件相同，见 `workflow/analysis-code-fingerprint-before.json`。基线 HEAD 作为快照标识已满足本阶段要求，无需改变分支或添加 tag。日志、支撑 fixture 和分析文档是过程材料，不参与生产构建。

## 2. 构建、安装状态及全部告警

使用 `hmos-arkts-syntax-checker/SKILL.md` 的工具链检查、编译诊断、构建与产物核对步骤；遵守本阶段授权，不执行技能中的修复循环。

工具链：DevEco Studio `6.1.0.860`，Node `18.20.1`，ohpm `6.1.1.830`，hdc `3.2.0d`，`DEVECO_SDK_HOME=D:\HarmonyDev\sdk\api23`。项目目标/兼容 SDK 保持 `6.0.2(22)`（`build-profile.json5:8-9`），运行设备 API 23。新 PowerShell 构建/设备进程均先加载环境脚本；构建前加载了 `D:/hongmengcup/Enter-HarmonyEnv.ps1` 与 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。

本次干净构建命令（在题根目录）：

```powershell
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
hvigorw.bat --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon
```

退出码 **0**，`BUILD SUCCESSFUL in 16 s 124 ms`。完整原始日志 [build.log](../logs/analysis-baseline/build.log)，SHA256 `cbb4bc42791f5c4a1d77446425c7a0dd61c2804fd4a116413f5b2ba91f866994`；命令与退出码分别在 [build-command.txt](../logs/analysis-baseline/build-command.txt)、[build-exit-code.txt](../logs/analysis-baseline/build-exit-code.txt)。

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`，8,937,956 bytes，SHA256 `5b7d8aa36ddb5253a7b0a78063a5f25dce4518ffc69e119eaa90527ea7346dfc`。`signingConfigs` 保持空数组。模拟器接受该 unsigned HAP，未修改签名配置、未绕过设备校验、未使用其他题的签名产物。

| 告警分类 | 数量 | 处理 |
| --- | ---: | --- |
| P1 废弃 API | 249 | 基线记录，不修复 |
| P2 可能抛异常而需特殊处理 | 505 | 基线记录，不修复 |
| P2 ArkTS 限制 | 3 | `DesignTokens.ets:411:3` 的 ESObject；`UserStateManager.ets:372:56`、`:439:49` 的 classes-as-objects |
| P2 可选 `@Prop` | 2 | `ui/LoadingAnimations.ets:225:9`、`:226:9` |
| P2 构建环境签名配置为空 | 1 | `No signingConfig found for product default`，对应 `build-profile.json5:3` |

共 **759 条源码告警（759 个唯一位置+消息）及 1 条签名配置告警**。全部源码告警的文件、行、列、分类、完整消息逐条保存在 [warnings.csv](../logs/analysis-baseline/warnings.csv)，无省略；汇总见 [build-summary.json](../logs/analysis-baseline/build-summary.json)、[warning-summary.json](../logs/analysis-baseline/warning-summary.json)。本报告的 P1/P2 是自测归类，不是编译器官方评分。

构建生成文件单独登记：[generated-artifacts.csv](../logs/analysis-baseline/generated-artifacts.csv)，列出 `.hvigor/`、`entry/build/`、`build/` 中 519 个当前产物/缓存的路径、大小、UTC 修改时间；该清单表示构建后快照，未声称所有缓存均本次新建。没有跟踪的业务或构建配置文件变动。

设备起初 `hdc list targets` 为 `[Empty]`，详细列表仅有 Offline TCP 和未连接 UART。主 Agent 授予本题唯一设备操作权。检查时无运行中的模拟器；启动后 `aa dump -a` / WindowManager 显示系统桌面，无其他题前台应用。已有 `HarmonyCup_API23`，Pura 90 Pro Max，x86_64，1308×2880，API 23，设备参数 `OpenHarmony-6.1.0.115`，连接 `127.0.0.1:5555`。

首次启动停于软件服务/隐私协议。主 Agent 转达本轮用户原话 **“同意并继续启动模拟器”** 后执行 `Emulator.exe -license accept`（退出码 0），再启动已有实例。授权来源和原始日志保存于 [emulator-license-authorization.json](../logs/analysis-baseline/emulator-license-authorization.json)、`emulator-license-accept.log`、`emulator-start-stdout.txt`、`emulator-start-stderr.txt`、`emulator-boot-stdout.txt`。未自行替用户作出许可决定。

实际安装/启动：

```powershell
hdc -t 127.0.0.1:5555 install -r 'D:\HCUP\vg-spec14\entry\build\default\outputs\default\entry-default-unsigned.hap'
hdc -t 127.0.0.1:5555 shell aa force-stop io.qzz.weiyu
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu
```

安装、force-stop、start 均退出码 0，且输出分别确认 `install bundle successfully`、`force stop process successfully`、`start ability successfully`。安装日志 [install-retry.log](../logs/analysis-baseline/install-retry.log)，启动日志 [relaunch.log](../logs/analysis-baseline/relaunch.log)。第一次误用正斜线 Windows 路径导致 hdc 将其拼接到 cwd，未安装成功；原始失败在 `install.log`，随即使用上面的绝对反斜线路径重新成功安装。未把初次失败后的旧应用启动结果当作本次基线证据。

## 3. Spec 入口实测位置

真实操作链：启动 `pages/Index` → 首页右上角齿轮 → `pages/SettingsPage` 设置列表 → 点击 **“WebDAV 配置”** → WebDAV 配置区。没有使用深链参数跳过列表。

- 首页跳转：`entry/src/main/ets/pages/Index.ets:325`，`router.pushUrl({ url: 'pages/SettingsPage' })`；注册路由 `entry/src/main/resources/base/profile/main_pages.json:7`。
- 设置列表文案/标识：`SettingsPage.ets:41` 的 `id: 'sync'`、`title: 'WebDAV 配置'`。
- 点击列表改变 `activeSectionId`：`SettingsPage.ets:507`、`:527-528`；`:447-448` 渲染 `SettingsSyncSection`，不是另一个独立页面路由。
- 首页齿轮组件在 `entry/src/main/ets/pages/index/components/TopNavigation.ets:70`，`:79` 触发父回调；启动页由 `entry/src/main/ets/entryability/EntryAbility.ets:35` 加载 `pages/Index`。页头返回调用 `SettingsPage.ets:487` → `:172-179`：从分区先回设置列表，再从列表保存通用设置并 `router.back()`。
- 实测 UI 树：`ui-initial.json`、`ui-settings-list.json`、`ui-webdav-empty.json`。这些初次文件记录真实导航，但 `empty` 是采集名，并不代表表单为空。
- 有效 JPEG 截图补采：[首页](../logs/analysis-baseline/screen-homepage-confirmed.jpeg)、[设置列表](../logs/analysis-baseline/screen-settings-list-confirmed.jpeg)、[本轮配置返回后重进](../logs/analysis-baseline/screen-webdav-reentered.jpeg)，各有同名 `ui-*.json` 树。

安装采用覆盖安装 `-r`，会保留该 bundle 的既存本地数据。最初看到的保留 fixture 配置**不作为本题功能实现或本轮请求证据**，未分析其来源。正式采集前经 UI 全部替换成本轮虚构配置：端点 `http://127.0.0.1:18164`、账号 `vg14-fixture`、密码 `vg14-password`、同步密码 `vg14-sync-pass`、远端目录 `/vg14-fixture`。自动同步开关实测已为 `checked=false`，保持关闭，正式请求计数从零开始。输入命令、键盘全选替换及值见 `device-commands.jsonl`；未使用真实凭据。

`CODE_FACT/UNVERIFIED`：另有跳转携带 `params:{section:'sync'}`（`entry/src/main/ets/pages/settings/FSRSOptimizationSection.ets:159-162`、`SettingsBackupSection.ets:195-198`），但 `SettingsPage.ets:132` 初值为空且未发现参数消费；因此未把这些调用当作已验证直达入口。首次全新安装的应用隐私/引导分支见 `Index.ets:115-136`、`:287-300`，本轮覆盖安装未重新验证该分支。

## 4. 页面、状态、网络与存储现状

以下源码结论为代码实证，动态结论另以日志/树/截图支撑。

- UI：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets`。`:25-37` 用 `@Link` 接收字段；`:41-43` 管理结果和 `webdavBusy`；`:348-391` 为文本/密码输入；`:439-443` 为基础配置字段。目标按钮 `:578-587`，以 `webdavBusy` 变换文字、颜色和 `.enabled()`。
- 手动同步：`:289-317` 先置忙碌与“正在同步数据...”，等待 100 ms，保存设置，再等待 50 ms，调用 `webdavManager.syncIncremental()`；`finally` 恢复忙碌。`:100-111` 的保存方法把结果文案改成“✅ WebDAV 设置已保存”，本次 busy 截图也确实显示此文案。**该文案不等于同步已完成。**
- 管理器：`entry/src/main/ets/sync/WebDavSyncManager.ets:672-698` 校验配置、防重复执行、置 SYNCING、创建客户端与远端目录预检；`:299` 发出目录 HEAD；`:892` 成功返回“同步完成”；`:901-903` 最终重置状态。
- 数据模型：`entry/src/main/ets/sync/webdav/WebDavCommon.ets:49-97` 的 `WebDavSettings`，包含 endpoint、username、password、syncPassword、remoteRoot、enabled。
- 网络客户端：`entry/src/main/ets/sync/webdav/WebDavClient.ets:22-38` 建立 Basic Auth、提供 GET/HEAD；`:88-95` 拼端点和路径；`:132-164` 通过 `@ohos.net.http` 发出真实请求，连接超时 15 s、读超时 20 s。
- 本地存储：`entry/src/main/ets/utils/WebDavStateStore.ets:63` 使用 Preferences 名 `webdav_state_store`，`:128` 打开，`:146-152` 读写设置 JSON；`WebDavSyncManager.ets:115-126` 调用存储保存。返回列表再进配置，显示本轮新端点、账号、目录和关闭的自动同步，见 `ui-webdav-reentered.json`。未直接读取设备数据库或旧配置文件。

`CODE_FACT` 的进一步调用链（不是额外运行覆盖）：

| 环节 | 文件与行号 | 现状 |
| --- | --- | --- |
| 配置保存/重载 | `SettingsSyncSection.ets:100-111`；`WebDavSyncManager.ets:115-125,132-160`；`SettingsPage.ets:149-168,190-196` | 当前输入保存后再同步；地址/账号 trim、空目录回退；父页持有 `@State`、子组件用 `@Link`。 |
| Preferences 主副本 | `WebDavStateStore.ets:66-69,261-301`；`WebDavCommon.ets:73-97` | 设置 JSON 有主副本及时间戳，写后 flush。JSON 包含 password/syncPassword；这仅描述存储调用链，未查看设备文件或扩展本题安全改造。 |
| 真实增量步骤 | `WebDavSyncManager.ets:710-719,733-739,751-775,793-802,830-873` | 下载单词、导入、导出/加密上传、下载/合并事件、按需上传；无本地变更也不能仅凭代码存在认定全部运行分支已测。 |
| TaskPool/HTTP | `WebDavSyncManager.ets:1087-1104`；`WebDavSyncTask.ets:209-242,309-334`；`WebDavClient.ets:149` | 下载/加密上传调用后台任务，每个任务创建真实客户端；fallback 只针对不支持能力错误。未对设备线程执行位置作独立性能测量。 |
| 远端路径 | `WebDavCommon.ets:221-236,251,254`；`WebDavSyncManager.ets:205-231,284-343`；`WebDavClient.ets:27-30,88-95` | endpoint 去尾斜杠后拼 remoteRoot/文件名；预检 HEAD，GET/PUT 增量文件；方法和请求次数是基线事实，Spec 未冻结这些细节。 |
| 页面超时 | `SettingsSyncSection.ets:114-122,289-308,315-316` | Promise.race 只包装 manager 同步等待，不包含前面的 100ms 等待及保存配置；超时会解除页面等待，未见取消底层 operation。`INFERENCE`：存在 UI 空闲而请求仍在途的风险；`UNVERIFIED`：本轮未运行 120 秒超时场景。 |
| 页面重建/自动同步 | `SettingsSyncSection.ets:43`；`SettingsPage.ets:447-462`；`EntryAbility.ets:53-54`；`AutoWebDavSyncManager.ets:48-65` | busy 属于条件创建的子组件，前台还可能自动同步。`INFERENCE`：忙碌时离页重进可能丢本地状态，自动请求可能干扰动作归因；本轮未验证这些风险。 |

## 5. 可复用实现与本次网络/UI 对应证据

可复用现有 `SettingsPage` 路由/分区、`@Link` 配置字段、`@State webdavBusy`、既有 `syncIncremental()` 和 Preferences 存储；已有真实 WebDAV 请求链。本轮没有为测试建立新的业务入口。

| 可复用的基线模式（仅盘点，不选择实现方案） | 源码证据 | 适用边界 |
| --- | --- | --- |
| 原生 LoadingProgress 遮罩 | `entry/src/main/ets/pages/TaskLoadingOverlay.ets:6-10,18-41`；`entry/src/main/ets/pages/ReadPage.ets:344-345,962-967,2174-2177` | 调用侧持有忙碌状态，组件用 `@Prop` 接收提示；遮罩与本题当前忙碌无绑定，也没有专用 id。 |
| 内联加载行 | `entry/src/main/ets/pages/index/WordBookTabContent.ets:21,45-68,134-143` | `@State isLoading` 配合 try/finally 和原生 LoadingProgress；可参考既有状态模式。 |
| 页面加载与文字 | `entry/src/main/ets/pages/WordListPage.ets:501-515` | 按 isLoading 显示 LoadingProgress/loadingMessage；证明本题基线内已有原生组件用法，不需访问上游实现。 |

测试支撑脚本：[webdav-fixture.cjs](../logs/analysis-baseline/webdav-fixture.cjs)，仅 Node 标准库；内存保存 PUT 数据，支持本轮 GET/HEAD/PUT 等请求，首次响应延迟 12,000 ms，记录 UTC、方法、路径、正文长度、响应码及是否存在认证头，不记录认证头内容。该服务只用于验证真实请求/状态，不等同完整生产 WebDAV 服务或同步数据正确性测试。

服务启动命令：

```powershell
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
& 'D:/HarmonyDev/DevEcoStudio-6.1.0/tools/node/node.exe' 'D:/HCUP/vg-spec14/logs/analysis-baseline/webdav-fixture.cjs'
hdc -t 127.0.0.1:5555 rport tcp:18164 tcp:18164
```

真实服务日志 [webdav-requests.jsonl](../logs/analysis-baseline/webdav-requests.jsonl) 证明 rport 方向有效。首次服务启动 `03:17:49.204Z`；[preclick-state.json](../logs/analysis-baseline/preclick-state.json) 在 `03:19:38.1916504Z` 记录请求数 **0**、自动同步关闭。`03:19:38.2155172Z` 点立即同步，`03:19:38.663Z` 收到 `HEAD /vg14-fixture`；首次响应 `03:19:50.681Z` 返回 200。

在请求等待期间，`03:19:38.4605860Z` 发起 `dumpLayout`，`03:19:39.4880902Z` 解析统计：**0 个 LoadingProgress，5 个“处理中...”禁用 Button**（[busy-state.json](../logs/analysis-baseline/busy-state.json)、[ui-sync-busy.json](../logs/analysis-baseline/ui-sync-busy.json)）。之后服务收到 GET/HEAD/PUT/GET，最后响应 `03:19:54.252Z`；`03:20:08Z` 后采集 `ui-after-first-request.json` 已见“✅ 同步完成”和按钮恢复。

初次截图尝试使用 `.png`，本设备 `snapshot_display` 要求 `.jpeg`，命令虽然退出 0，但输出明确报错；相应 PNG 文件没有生成，**不能作为截图证据**。已保留失败记录并修正支撑脚本。`ui-sync-complete.json` 的名字过早，实际在 `03:19:52Z` 仍是 busy，**不作为最终完成证据**。有效最终树为 `ui-after-first-request.json`、`ui-first-final.json` 及下述重复运行最终树。

为补忙碌 JPEG 截图，仅重复一次相同操作；重启临时服务并使用 `screenshot-rerun` 运行标识，保持同一基线和同一 UI 配置：

| UTC | 观测 |
| --- | --- |
| 03:20:52 | 点击立即同步，记录在 `device-commands.jsonl` |
| 03:20:52.549 | 收到 HEAD `/vg14-fixture`，进入 12 s 延迟 |
| 03:20:52–53 | UI 树、JPEG 均显示五个禁用“处理中...”，无 LoadingProgress |
| 03:21:04.562 | 首个 HEAD 响应 200 |
| 03:21:04.566 | GET `/vg14-fixture/words_delta.json.enc`，404 |
| 03:21:08.017 | HEAD `/vg14-fixture`，200 |
| 03:21:08.031 | PUT `/vg14-fixture/words_delta.json.enc`，549 bytes，201 |
| 03:21:08.048 | GET `/vg14-fixture/events_all.jsonl.enc`，404；03:21:08.057 响应结束 |
| 03:21:16–17 | 最终 UI 显示“✅ 同步完成”，5 个按钮均 enabled=true |

有效证据：[busy JPEG](../logs/analysis-baseline/screen-repeat-busy.jpeg)、[busy UI 树](../logs/analysis-baseline/ui-repeat-busy.json)、[busy 统计](../logs/analysis-baseline/repeat-busy-state.json)、[final JPEG](../logs/analysis-baseline/screen-repeat-final.jpeg)、[final UI 树](../logs/analysis-baseline/ui-repeat-final.json)、[final 统计](../logs/analysis-baseline/final-state.json)。JPEG 已实际打开目视核对。

## 6. 缺失项、逐需求判定与最小复现

下列编号只为本次独立自测引用，不代表官方 F-point 数量/分值；请由主 Agent 映射到批准验收矩阵。

| 项 | 来源 | 状态 | 证据与限制 |
| --- | --- | --- | --- |
| V1 沿既有入口进入配置页 | 场景一第 1 步 | pass | 首页→齿轮→设置列表→WebDAV 配置，实际 UI 树/截图 |
| V2 填写可访问 WebDAV 配置 | 场景一第 1 步 | pass | 本轮虚构配置；本地服务实际收到带认证头的请求 |
| V3 点击“立即同步”进入忙碌 | 场景一第 2、3 步 | pass | 两次真实点击，busy 树中 5 按钮禁用 |
| V4 同步运行期间渲染 ArkUI `LoadingProgress` | 场景一第 4 步 | **fail** | 两次延迟请求窗口 UI 树均 0 个 LoadingProgress；busy JPEG 无指示器；源码也无对应构建 |
| V5 手动同步向配置端点发送真实请求 | 场景二第 1、3 步的网络原子行为 | pass | 点击前 0 请求，点击后 HEAD/GET/PUT；服务与 UI 时间重叠 |
| V6 加载指示器显示时绑定真实请求 | 场景二第 2–4 步及概述完整行为 | **fail** | 后端请求真实存在，但加载指示器未显示，完整联动不满足 |
| V7 请求链正常结束后恢复闲置 | 合理推导 | pass | 最终“✅ 同步完成”、5 按钮恢复；只证明本轮本地成功路径 |
| V8 正常返回后重进保留新配置 | 合理推导 | pass | 本轮端点、账号、目录、自动同步关闭保留；未测应用重启后持久化 |
| V9 空/空格/错误配置、鉴权失败、断网、请求失败、快速连点、忙碌返回/关闭、重启 | 边界评审范围 | not_run | 本轮分析基线任务未逐一运行这些边界；不能从正常路径推定通过 |
| V10 UI 120 s 超时与底层请求取消关系 | 静态风险 | not_run | `SettingsSyncSection.ets:116-122` 使用 Promise.race；未实测超时，不声称请求取消/恢复正确 |

与正式验收矩阵的映射：A01/A02/A03/A04、B01 的入口/动作/忙碌原子行为有实测证据；B03/B04 的本轮配置端点请求原子行为有实测证据，尚未执行两个端点 A/B 切换样本；A05/A06/B02/B05 因没有 LoadingProgress 而失败。B06 是拒绝“只有加载没有请求”的判据，本轮无该反例，未单独运行负向控制。D01 仅“忙碌解除/再次发起”部分已测，不能因基线始终没有 spinner 就宣称“正确移除 spinner”通过；D02 未测；D03 未证明干净空库/完全无变更，不能用覆盖安装的数据推定通过；D04 的点击前后请求归因已测。E01～E15 是后续覆盖清单：除 E09/E10 的本轮多请求/12 秒延迟及 E11 的正常结束后重进片段外，其余未运行或仅作静态评审，均不记为通过。

最小失败复现：安装本报告哈希的基线 HAP → 从首页齿轮进入设置列表，再点“WebDAV 配置” → 填本轮虚构配置并保持自动同步关闭 → 启动上述本地 fixture 与 rport → 点击“立即同步” → 在首 HEAD 12 s 延迟窗口采 UI 树和 JPEG。

期望：同步运行期间显示 ArkUI `LoadingProgress`，同时服务收到请求。实际：服务收到真实请求，界面仅出现禁用“处理中...”按钮，`LoadingProgress` 计数为 0。错误日志：本项没有崩溃或网络错误；失败来自需求期望与 UI 树/截图不一致。归因假设：`SettingsSyncSection.ets:578-587` 只改变按钮状态，没有相应 LoadingProgress 渲染；**强证据**（代码、UI 树、截图、延迟服务日志交叉一致）。建议主 Agent 在后续获准实施阶段交回方案/编码，复用现有忙碌状态和真实请求链补指示器，本分析阶段不修复。

## 7. 前置环境与清理

本轮不需用户登录、真实账号、外部 WebDAV 或真实凭据。仅本机 Node fixture、模拟器、hdc rport，即可建立可观察请求链。fixture 对不存在的加密文件返回 404，上传保存在内存；因此验证范围不含生产服务器互操作性、加密内容正确性、复杂学习数据冲突或端到端数据一致性。

`CODE_FACT`：业务登录不是该入口的显式门槛；manager 要求 WebDAV 地址、账号/密码非空及 trim 后至少 4 位同步密码（`WebDavSyncManager.ets:164-174`）。存在旧加密远端数据时需匹配同步口令（`WebDavSyncTask.ets:242-255`）；网络权限已声明（`entry/src/main/module.json5:15`）。本轮 fixture 只记录认证头是否存在，不验证服务商鉴权、证书或密码正确性；生产服务账号/权限/网络兼容性仍为 `UNVERIFIED`。本地条件足以检验本题请求与 UI 绑定的基本缺口，不能替代所有 WebDAV 服务的集成验证。

服务端只需支持所选真实路径实际经过的请求。本轮经过 HEAD/GET/PUT；源码的写探测分支还可能 DELETE（`WebDavSyncManager.ets:245-269`），不能把开放 DELETE 当成所有基本路径的前置要求。请求方法、次数和目录策略均不是本题 Spec 明文，相关候选处理保留在验收矩阵 U01/U02。

曾发生的阻断均留证：无在线设备→在用户许可授权后启动；空签名配置→模拟器实际接受 unsigned 包；hdc Windows 路径格式→更正命令；PNG 截图→改 JPEG 并复测。最终本轮有效路径没有 remaining blocked 项。普通 `hdc` 的退出码可能为 0 而输出含错误，报告同时检查输出，不将其误判成功。

结束时通过 exec 会话 Ctrl+C 停止本 Agent 两次临时 Node 服务（初次会话 35795、截图重复会话 60496，停止返回 1 反映主动中断），没有残留 18164 监听。仅移除本 Agent 创建的转发：`hdc -t 127.0.0.1:5555 fport rm tcp:18164 tcp:18164` 输出成功，随后 `fport ls` 为 `[Empty]`。保留全部证据文件。模拟器保留运行于本题 WebDAV 配置页，自动同步关闭，设备操作权交回主 Agent；未停止共享环境的其他服务。

## 8. 测试可观测性风险与证据索引

- 关键齿轮、列表入口、输入框、5 个操作按钮均缺少稳定业务 `.id()`；只有页面外层存在随主题令牌变化的 `settings_...`（`SettingsPage.ets:565`），不适合作为按钮稳定选择器。当前树中目标 Button 的 `id` 为空。
- 忙碌时 5 个不同动作全部同名“处理中...”，单凭文本无法定位“立即同步”原按钮；应由主 Agent 在后续实现阶段评估稳定 id。该风险有实际 UI 树支撑。
- 操作结果“✅ WebDAV 设置已保存”会覆盖“正在同步数据...”，单看状态文字可能误判完成；本轮以按钮 busy/服务等待区间判断运行中。
- UI 树采集与服务器同为本机 UTC 可关联；仅取有限时刻，不能证明每一帧、每个失败分支。结合源代码未渲染该组件，足以证明本次缺失，不能扩展成未来修复后的全覆盖结论。
- 入口操作本次使用观察到的坐标（1308×2880），非跨设备稳定测试脚本。未运行 Hypium 测试或任何未公开官方测试。

主要原始材料都在 `logs/analysis-baseline/`：`environment.txt`、`device-preinstall.log`、`device-commands.jsonl`（每条命令、时间、退出码、原始输出）、`device-hilog.txt`、`build.log`、`warnings.csv`、源指纹 JSON、各阶段完整 UI 树/JPEG、`webdav-requests.jsonl`。支撑代码 `device-helpers.ps1`、`webdav-fixture.cjs` 与本报告均未参与生产构建。
