# vg-spec15 基线调查

本阶段范围：`spec-harness/0-analyze.md`。仅分析、构建、安装与操作未修改基线，未实现功能。本文区分 **Spec 明文**、**代码实证**、**设备实测**与**推断/未验证**；验收项见 `spec/acceptance.md`。本轮已完成未修改基线的清理构建、重装、启动、入口实操、取消对照及受控延迟无备份恢复调查。实测发现：忙碌文字和真实请求已存在，恢复期间缺少 ArkUI `LoadingProgress`；成功导入及其他未测分支不计通过，详见第7节。

## 1. 快照与来源

- 基线 HEAD / `spec/metadata.json:2`：`88db8789e28333c7b7dcc8db078f394a262b73c3`。采用记录 HEAD 的方式，未额外打 tag。
- Spec SHA-256：`65bb001ac7d97ac9a66685430b559fb42977b615ceea32554ddd738ad1c03acc`。
- metadata SHA-256：`6ace3344962c66300a23b017d435e18bc9d340d8b77eaec478a3f6a96006f920`。
- 本轮起始指纹：`workflow/analyze-code-fingerprint.json`；`changes_since_setup=[]`。构建角色再次逐文件核对，见 `logs/analyze-baseline/preflight.json` 的 `fingerprint_mismatches=[]`。
- 初始 Git 已有 `AGENTS.md` 指导追加和题目资料/记录目录，未清理或覆盖。未访问上游功能实现、修复历史、其他赛题目录或题包目录。初始化会话及官方示例验证不作为本题功能证据。

## 2. 本轮清理构建、安装与启动

每个构建、设备 PowerShell 进程先执行：

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/vg-spec15
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
```

**设备实测/命令结果**：2026-10-15 22:14:58–22:15:15（Asia/Shanghai）本轮清理构建退出码 0。完整命令及时间见 `logs/analyze-baseline/build-result.json:2`；原始输出见 `logs/analyze-baseline/build.raw.log`，可复执行脚本为 `logs/analyze-baseline/build-baseline.ps1`。

- 工具：DevEco 附带 Node `v18.20.1`、SDK `D:/HarmonyDev/sdk/api23`、HDC `3.2.0c`；实际路径和版本见 `logs/analyze-baseline/preflight.json`。
- 本轮 HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，8,937,956 字节；SHA-256 `e212ec6bcc965a69af5f2fa6b5f886fb5153f89ef8fefa09ea7889c5f276a08a`，见 `logs/analyze-baseline/artifacts.json:3`。
- 安装：`hdc -t 127.0.0.1:5555 install entry\build\default\outputs\default\entry-default-unsigned.hap`，返回 `install bundle successfully`，见 `logs/analyze-baseline/install-retry.log:1`。
- 启动：`hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu`，返回 `start ability successfully`，见 `logs/analyze-baseline/launch.log:1`。
- 首次安装传入正斜杠绝对路径被 HDC 错误拼接后失败，重试改本地相对路径成功。失败原始输出保留在 `logs/analyze-baseline/install.log:1`，未更改应用代码。`01-launch` 捕获的是安装失败后的旧前台，明确排除，不作本题证据。
- 本次启动确实出现本应用隐私政策弹窗，`02-launch-baseline.png` / `.json`；用户在本聊天明确选择同意并授权代点击后才继续。未以修改偏好项等方式绕过首启。

### 本轮已有告警清单

构建成功不等于零告警。原始日志共2,313行，759条带源文件位置的编译告警，另有2条通用/签名告警标题。完整逐条清单见 `logs/analyze-baseline/warning-index.md`（含原始日志行号、源文件行列、原文），机器可读索引为同目录 `warning-index.json`，计数来源为 `warning-summary.json:2`。后续应对比这些原始条目，不只比较总数。

| 类别 | 数量 | 原始证据 |
| --- | ---: | --- |
| 可能抛异常，要求专门处理 | 505 | `warning-summary.json` 的 `compiler_warning_messages`；每条位置见索引 |
| `showToast` 已弃用 | 128 | 同上，保留基线原样 |
| 其他已弃用 API | 121 | 涵盖 `encode/decode`、`SetOrCreate`、`animateTo`、`getContext`、`pushUrl`、`showDialog`、`back`、`release`、`getParams`、`createAudioPlayer`、`src`、`play`、`setPasteData`、`getLength`，各项精确计数见 JSON |
| ArkTS 类型限制 | 3 | 1条 `arkts-limited-esobj`，2条 `arkts-no-classes-as-obj`，原始日志27–34行 |
| 可选 `@Prop` 参数 | 2 | `LoadingAnimations.ets:225`、226，对应原始日志2299–2302行 |
| 通用 FAQ 提示及缺少 signingConfig | 2 | 原始日志36行、2309行；后者解释本轮为 unsigned HAP，不影响本模拟器的实际安装成功记录 |

本阶段未修复、删除或压制任何告警；后续若要认定未引入新告警，必须使用修改后构建与本清单逐项对比。

## 3. 入口与路由：代码定位

| 节点 | 代码实证与位置 | 验证方式 |
| --- | --- | --- |
| bundle / Ability | `AppScope/app.json5:3` 为 `io.qzz.weiyu`；`entry/src/main/module.json5:6` 主入口 `EntryAbility` | 本轮重装、启动结果见上 |
| 首页 | `entry/src/main/ets/entryability/EntryAbility.ets:35` 调用 `loadContent('pages/Index')` | 启动后的 UI 树、截图 |
| 设置按钮 | `entry/src/main/ets/pages/index/components/TopNavigation.ets:69` 齿轮区域，79 行调用 `onSettingsClick()` | 从首页按既有入口点击 |
| 设置路由 | `entry/src/main/ets/pages/Index.ets:325` 调用 `router.pushUrl({ url: 'pages/SettingsPage' })`；路由注册于 `entry/src/main/resources/base/profile/main_pages.json:7` | 不新增直达测试页或独立入口 |
| WebDAV 配置 | `entry/src/main/ets/pages/SettingsPage.ets:41` 设置项 `id='sync'`；527–529 行点击后赋值 `activeSectionId`；447–462 行渲染 `SettingsSyncSection` | 它是设置内的子区块，没有独立 WebDAV 路由 |
| 从云端恢复 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:604` 恢复按钮，613 行调用 `webdavRestore()` | 既有按钮进入确认弹窗 |
| 返回 | `entry/src/main/ets/pages/SettingsPage.ets:172` 的头部返回先清空当前区块，再执行保存通用设置与 `router.back()`（177–179 行） | 这是代码行为；硬件返回和运行中返回另作边界验证 |

## 4. 相关组件、状态、数据与服务

以下均为**代码实证**，未列为动态恢复成功证据。

| 范围 | 基线现状与证据 |
| --- | --- |
| 配置输入 | `SettingsSyncSection.ets:439` 起提供地址、账号、密码、同步密码、远端目录；普通输入 Builder 在347–367行，密码 Builder 在369–402行。显示/隐藏密码是既有 UI。 |
| 父子状态 | `SettingsPage.ets:114` 起保存页面配置 `@State`；`SettingsSyncSection.ets:25` 起用 `@Link` 同步字段。子组件自己的 `webdavBusy`、`webdavBackupResult`、`restoreDialogShowing` 分别在41–44行定义。 |
| 配置保存与读取 | `SettingsSyncSection.ets:100` 构造 `WebDavSettings`，trim 地址/账号/目录，109行调用 `setSettings()`；`SettingsPage.ets:163` 初始化 manager 和 state store，190–196行把 manager 配置载入输入。 |
| 恢复第一确认 | `SettingsSyncSection.ets:179` 弹窗标题“从云端恢复”，183–184行是“取消”“继续”；188–192行取消/关闭直接返回。 |
| 下载及忙碌 | `SettingsSyncSection.ets:196` 设置 busy，198行设“正在下载云端备份...”，201行让出 UI，207行实际 await `downloadBackupPlain(false)`；226–229行解析预览。 |
| 第二确认与导入 | `SettingsSyncSection.ets:238` 暂停 busy 等待第二个“⚠️ 恢复确认”弹窗；253行为“确认恢复”；271–275行再次置 busy 并 await `importPlainBackup()`；283–285行 finally 释放状态。该第二弹窗不是 Spec 明文中的“继续”。 |
| 忙碌呈现 | `SettingsSyncSection.ets:543`、553、578、594、604行有五个按钮同时变为“处理中...”；619行渲染恢复状态 Text。整个目标文件没有 `LoadingProgress` 调用，也没有 `.id()`。 |
| 数据模型 | `entry/src/main/ets/sync/webdav/WebDavCommon.ets:49` 定义 `WebDavSettings`；3–8行为 `WebDavSyncStatus` 枚举，11–34行为设置/manifest 序列化接口。manager 状态位于 `WebDavSyncManager.ets:74`，与 UI busy 不是同一状态变量。 |
| 真实服务入口 | `entry/src/main/ets/sync/WebDavSyncManager.ets:475` 校验配置、置 RESTORING、创建原有客户端，482行执行远端预检，再调用 `backupManager.downloadBackupPlain()`；506–510行为本地导入入口。 |
| 请求与备份 | `entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:81` HEAD 检查备份（404可尝试旧路径），103行 GET，118行 TaskPool 解密，129行返回明文；196–207行为真正导入。当前方法/路径来自基线，不是 Spec 固定请求格式。 |
| HTTP 客户端 | `entry/src/main/ets/sync/webdav/WebDavClient.ets:27` 用地址和 Basic 认证初始化；126行 `http.createHttp()`，149行 await 请求，167/179行销毁请求；143–144行连接15秒、读取20秒超时。 |
| 远端预检 | `WebDavSyncManager.ets:284` 检查缓存/远端目录，298行 HEAD；目录不可达时可能进行创建或写入探测。不能把唯一 GET 或固定请求数量当验收前提。 |
| 持久化 | `entry/src/main/ets/utils/WebDavStateStore.ets:63` 用 Preferences `webdav_state_store`；66–82行是设置/manifest/本地快照及备份键；128行加载，284–299行保存主副本并 flush。`WebDavSettings.toJSON()` 包含密码（`WebDavCommon.ets:73`），这里仅记录基线写法。 |
| 数据预览与落地 | `entry/src/main/ets/sync/DataSyncManager.ets:379` 预览，390–403行统计新增/更新；209行导入，221行异步解析，后续写入本地数据。下载前可导出本地快照（`WebDavBackupManager.ets:98`），不可笼统断言“下载期间本地无任何写入”。 |

本节中未带目录的 `SettingsSyncSection.ets` 指 `entry/src/main/ets/pages/settings/SettingsSyncSection.ets`；`SettingsPage.ets` 指 `entry/src/main/ets/pages/SettingsPage.ets`；`WebDavSyncManager.ets` 指 `entry/src/main/ets/sync/WebDavSyncManager.ets`。

## 5. 可复用实现与已知缺口

**可复用的代码实证**：已有设置入口、`WebDavSettings`、manager / backup manager / HTTP client、Preferences 持久化、两阶段恢复确认、真实下载/解密/预览/导入流程。相近 UI 在 `entry/src/main/ets/pages/ImportPage.ets:731` 的 `buildImporting()` 同时呈现 `LoadingProgress()`（734行）和“正在导入...”文字（739行）；这只是本题基线的相近实现，不表示应把新流程搬到导入页。

**Spec 要求但目标页面完全缺失的能力**：恢复流程内的 ArkUI `LoadingProgress` 渲染分支；代码证据为目标组件完整 build/Builder（`SettingsSyncSection.ets:429` 至文件尾）只渲染文字和按钮。忙碌文案及真实请求链已经存在，不能归类为“完全缺失”。设备对应观察见第7节。

**推断风险，非本阶段修复事项**：

1. 填写配置不等于 manager 已采用配置：`webdavRestore()`（165–287行）不调用100行的 `saveWebDavSettings()`，而 manager 在475–482行读取已存的 `this.settings`。“只填写不保存是否应直接生效”须按验收矩阵中的待确认项决定，不能暗加保存为 Spec 步骤。
2. 第一弹窗打开前只检查 `restoreDialogShowing`（172行），直到用户“继续”后的197行才置 true。快速连点第一恢复入口的防重窗口存在风险，尚不能由代码阅读断言设备一定重复弹窗。
3. `SettingsSyncSection.ets:116` 的 `Promise.race` 只对包装等待计时，120行定时器没有在成功后清除，超时也不取消底层请求/导入。不能把 busy=false 等同所有网络/本地任务均已终止。
4. `SettingsPage.ets:447` 的条件渲染会重建子区块；`SettingsSyncSection` 未实现销毁时请求协调。运行中返回重进可能产生新 UI 状态与旧任务不同步；必须实测，不能把风险写成已经发生。
5. `entry/src/main/ets/entryability/EntryAbility.ets:49` 的前台回调调用自动同步（53–54行）；`entry/src/main/ets/sync/AutoWebDavSyncManager.ets:65` 会发起增量同步。网络证据必须排除自动同步、测试连接、保存前旧请求的干扰。

## 6. 前置环境与测试可观测性

| 条件 | 事实、限制与准备方式 |
| --- | --- |
| 设备与安装对象 | 使用本题新构建 HAP 安装 `127.0.0.1:5555`；不是沿用模拟器预装的同包程序。设备版本/规格以本轮设备记录为准。 |
| 登录与凭证 | 本轮未登录账号即可进入设置和 WebDAV 配置，见 `logs/analyze-baseline/nodes/05-settings.jsonl:43`、`nodes/06-webdav-initial.jsonl:7`。网络操作需要 WebDAV 地址、账号/密码、至少4位同步密码；基线校验见 `WebDavSyncManager.ets:164`。可用仅本机端点与虚构凭证验证请求发出，无需用户提供真实云端账号；本轮输入法门槛已在用户明确选择后解除，详情见第7节。 |
| 云端成功数据 | 要验证完整成功恢复，需兼容基线加密格式的备份、对应同步密码、可读取的远端路径；代码见 `WebDavBackupManager.ets:70` 和118行。单有可达 HTTP 端点只能证明请求与错误生命周期，不能证明成功解密、预览、导入。 |
| 空云端/失败 | 可用本地受控404/错误/延迟响应覆盖；请求日志需包含用户动作时间、端点、接收/结束时间，UI 树在等待期间采样。 |
| 稳定 id | 首页齿轮、设置列表项、全部 WebDAV 输入/按钮/状态 Text 均缺少固定 id，定位见前述来源；`SettingsPage.ets:565` 唯一容器 id 为 `'settings_' + themeRefreshToken`，会变，不适合作为固定契约。具体建议见验收矩阵选择器表。 |
| 同名歧义 | 忙碌时五个按钮都是“处理中...”；两个密码字段各有“显示/隐藏”；“从云端恢复”同时是按钮和第一弹窗标题。仅按文字定位可能选错目标，应按类型/父容器缩小范围，后续实现再补 `.id()`。 |
| 滚动与时序 | 配置、自动同步和操作区在设置 Scroll 内（`SettingsPage.ets:503`），需要滚动；无稳定 id 时按坐标只能用于本轮人工式探索，不能作为可靠的后续回归契约。 |

## 7. 本轮设备与网络结果

本节未单独注明目录的证据文件均位于 `logs/analyze-baseline/`。完整命令、用户选择时间与动作时间线为 `device-timeline.jsonl`；逐节点索引在 `nodes/`，每行保留原始 JSON 文件名和原始行号，便于复核。独立角色完整报告为 `workflow/verification/baseline-round-01.md`。

### 入口、配置与用户前置选择

**设备实测**：从本题新安装应用的首页右上齿轮，进入设置，再选“WebDAV 配置”。设置入口见 `nodes/05-settings.jsonl:43`，配置页标题见 `nodes/06-webdav-initial.jsonl:7`。五个输入框依次见该文件16、19、23、30、36行，均无业务 id。实际初始远端目录为 `/weiyu_vignette`（36行），与 manager 默认值一致（`entry/src/main/ets/sync/webdav/WebDavCommon.ets:62`）；不能只凭父页字段初始值 `/weiyu_sync` 推断最终设备值。

本应用首次隐私政策出现后，由用户在本聊天明确选择“同意并进入”并授权代操作，才继续进入设置。填写地址又出现独立小艺输入法协议，普通输入及 Hypium 组件 `input_text(..., InputTextMode().paste(True))` 均触发它，证据为 `nodes/11-hypium-endpoint.jsonl:27`、33、40、42行以及 `hypium-endpoint-retry.raw.log`。该协议暂时阻断了输入；后来用户明确选择“同意全量模式，请代我操作并继续验证”，自测才执行该选项并完成初始26键设置，见 `device-timeline.jsonl:100` 起及 `12-ime-before-approved-mode` 至 `16-after-ime-settle` 系列证据。前置协议已解除，不是最终阻断，也不是本题业务缺陷。没有修改偏好项或业务数据绕过这些页面。

自动同步初始为开（`nodes/06-webdav-initial.jsonl:45`），实验前已通过 UI 关闭（`nodes/17-auto-sync-off.jsonl:45` 为 `checked=false`）。之后填写本机端点与虚构凭据，点击“保存设置”；`nodes/21-configuration-saved.jsonl:30` 明示“✅ WebDAV 设置已保存”，24行仍为自动同步关闭。本轮没有点击“测试连接”“立即同步”或“立即备份”，不会用它们的请求充数。**直接填写但不保存的路径仍未验证**，保存是否为必需步骤保留 U03 歧义，不能暗加成 Spec 明文。

### 受控端点与动作时间线

只在宿主回环地址 `127.0.0.1:18085` 建立临时服务，脚本 `webdav-probe.py:65`；使用本次专用 `hdc rport tcp:18085 tcp:18085` 映射。地址配置为 `http://127.0.0.1:18085`，虚构账号为 `spec15-user`，远端目录为 `/baseline-spec15`，密码/同步密码均为本次测试专用值。未连接外部 WebDAV、未索取真实凭证、未覆盖业务数据。服务校验虚构 Basic 认证，对目录 HEAD 返回200，对备份文件返回404，并将每条请求延迟12秒（`webdav-probe.py:23–52`、`server-state.json`）。该服务可以验证请求、忙碌和无备份终态，不能证明完整成功导入。

下表时间均为2026-10-15 Asia/Shanghai；原始 JSONL 使用 UTC，表内已加8小时。

| 事件 | 实测及证据 |
| --- | --- |
| 第一次取消 | 22:35:25 以两次稳定 UI 树定位“取消”后点击（`device-timeline.jsonl:201–202`），`25-after-stable-cancel.json` 显示弹窗已消失，恢复按钮仍可用。22:35:26至22:35:48下一次“继续”前没有 `request_begin`；见 `server-requests.jsonl:3–4` 与动作时间线203–223行。第一次按坐标尝试的23号快照仍有弹窗，**该次不计取消成功**，保留工具失败。 |
| 下一次第一次“继续” | 22:35:48.386 按稳定的“继续”文本位置点击（`device-timeline.jsonl:223`）；恢复工作随即运行，无需先点击第二次“确认恢复”。 |
| 真实请求1 | 22:35:48.702收到 `HEAD /baseline-spec15`，虚构鉴权匹配；22:36:00.703返回200（`server-requests.jsonl:4–5`）。它属于原有恢复预检链，参 `WebDavSyncManager.ets:475–488`，不是 UI 演示另发的无关请求。 |
| 请求 pending 时界面 | `27-restore-pending-early`、`28-restore-pending-second`、`29-restore-pending-later` 三组有效截图和 UI 树。各自 `nodes/*.jsonl:38` 均为可见 Text“正在下载云端备份...”；28、29、33、36、37行是五个 disabled“处理中...”按钮。三棵树 `LoadingProgress` 数量均为0，截图也无加载指示器，与目标源码完全缺该组件相互印证。 |
| 后续真实请求 | 22:36:00.756收到 `HEAD /baseline-spec15/backup.json.enc`，22:36:12.757返回404；22:36:12.828收到旧路径 `HEAD /baseline-spec15/data/backup.json.enc`，22:36:24.830返回404（`server-requests.jsonl:6–9`）。这只是本轮观测序列，不是固定验收合同。 |
| 无备份终态 | `nodes/30-restore-404-terminal.jsonl:38` 明示“⚠️ 云端暂无备份：云端不存在备份文件，请先在其他设备上创建备份”；28、29、33、36、37行按钮恢复原文且 enabled=true，不再显示进行中文字。有效截图为 `30-restore-404-terminal.png`。未伪报导入成功，未进入第二覆盖导入确认。 |

**核心结论（设备实测）**：A05 所要求的 ArkUI `LoadingProgress` 在真实恢复请求 pending 时缺失；A08 的忙碌文案与 A12/A13 的真实、可观察请求已存在。A11 仅要求一般“恢复加载状态”，需求复审认为本路径文字及忙碌按钮可以满足该步，不能把 A05 的组件缺失重复扩大成 A11 的新组件合同。整体需求仍未全部满足。

取证后的离线断言命令为 `python -X utf8 logs/analyze-baseline/assert-baseline-observations.py`，退出码1（`assertion-run-result.json:3`），因为A05组件断言失败；逐项实际值保留在 `assertion-results.json` 与 `assertions.raw.log`。这不是构建失败，也没有将基线功能缺口改成跳过或通过；该脚本只检查已保存证据，不能代替尚未运行的场景。

### 本轮执行范围与限制

`pass` 仅指注明的本轮路径，不表示该编号在所有数据、所有阶段下均已满足；采样不能单独证明每一时刻均可见。

| 验收项／检查 | 本轮状态 | 范围与证据 |
| --- | --- | --- |
| 清理构建、重装、启动 | 已完成 | `build-result.json:5`、`build.raw.log:2313`、`install-retry.log:1`、`launch.log:1` |
| A01 配置入口 | pass | `nodes/05-settings.jsonl:43`、`nodes/06-webdav-initial.jsonl:7` |
| A02 有效表单 | pass，限显式保存路径 | 虚构配置输入、保存反馈及服务端鉴权匹配；不保存路径未测 |
| A03–A04、A06、A10 确认及触发 | pass，限本轮路径 | 第一弹窗22/26组及22:35:48点击“继续”后请求时间线 |
| A05 ArkUI LoadingProgress | **fail** | 27/28/29组截图与树均无组件，目标源码也未声明 |
| A07–A08 忙碌状态及提示 | pass，限本轮无备份请求路径 | 三组 pending UI 有进行中文字与禁用按钮 |
| A09 期间持续文案 | 采样满足；全阶段仍未验证 | 三个 pending 采样点相同；未覆盖成功解密、预览与导入，不能宣称全部区间通过 |
| A11 一般恢复加载状态 | pass，限本轮观察窗口 | 按场景三原句粒度有文字及忙碌 UI；不替代 A05 |
| A12–A13 真实且可观察请求 | pass，限本轮路径 | `server-requests.jsonl:4–9` 与同轮 UI、原有调用链对齐 |
| A16 第一次取消 | pass，限稳定定位后的操作 | 25号树/截图、点击时间与下一继续前零请求窗口；不采用失败的23号尝试 |
| A20、A23、A26 无备份及状态恢复 | 部分已观察 | 当前/旧文件HEAD404后退出busy且给真实错误；未覆盖其他空数据、断连、鉴权失败、异常、超时和成功导入 |
| A14–A15、A17–A19、A22 | not_run（或仅部分流程观察） | 未穷跑空/空白输入、弹窗关闭、重复/快速点击和全部部分操作；保持验收计划 |
| A21 最后一页 | 不适用，静态判断 | 无分页恢复入口或模型，不计运行通过 |
| A24–A25、A27–A28、A31 | not_run / 待确认 | 未保存配置、第二等待、返回/关闭/重启语义未擅自确定 |
| A29–A30 固定文案/网络序列假设 | 不作为硬验收合同 | 依 Spec 排除无依据限制，不计新增功能通过数 |

成功下载备份正文、解密、预览、第二确认、实际覆盖导入和数据库恢复**均未验证**；本地服务刻意没有可导入备份，不以此环境证明完整恢复成功。长时超时、底层任务取消、返回重进、重启后重进也未验证。后续完整正例需要与同步密码匹配的有效加密备份和安全的本地数据夹具。

### 工具与证据风险

- HDC 有时返回退出码0但文本实际报错：首次安装路径、06号抓屏和23号抓屏均有原始失败日志。06号PNG为零字节，不得作截图证据；06/23号UI树仍可独立复核。有效目标页截图可用 `10-after-ime-exit.png`、`19-configuration-filled.png` 及后续成功采样。
- 弹窗展开动画使早期固定坐标点击未真正取消，23号树仍含 AlertDialog；改为当前文本唯一定位、连续两次稳定 bounds 后点击，25号树确认关闭。未将“命令返回 No Error”当成业务成功。
- 本轮以 HDC UI 树与 Hypium 组件输入取证，不声称已经交付或运行完整 Hypium 回归套件。原生弹窗文字“取消/继续”确实在树中可定位，但没有稳定业务 id；固定坐标不适合作后续可靠回归。
- 当前状态只证明基线现状。分析阶段不改业务代码、不修加载组件、不压制告警、不标记整题 `local_validation_complete`。最终源码指纹与临时资源清理结果另见角色报告末尾及 `workflow/analyze-audit.json`。

### 结束状态与可恢复性

`logs/analyze-baseline/final-integrity.json:5–6` 复核296个 tracked 文件，与本轮批准指纹及构建前内容全部一致；HEAD与Spec/metadata哈希也一致。Git唯一既有tracked差异仍是初始化追加的 `AGENTS.md`。主Agent另以 `workflow/analyze-audit.json` 核对了两份文档结构、15条Spec逐字摘录、31项八维配对以及无新增业务文件。

本次回环服务已正常停止，未强制杀进程（`logs/analyze-baseline/server-final-stop-result.json:5–6`）；最终监听检查为空。本次专用rport及本次Hypium创建的转发已移除，原有其他映射保留，见 `logs/analyze-baseline/port-list-after-final-cleanup.log:1–3`。应用保留本轮虚构配置，自动同步处于关闭状态，便于后续复现实验；恢复验证结束界面见30号证据。运行时配置与用户明确同意的首启设置属于设备状态，未修改工程业务源码。

本阶段交付完成，下一阶段再依据验收矩阵决定方案与实现。U03（新填配置是否必须先保存）、U04（第二确认等待是否仍应显示加载）及未定义的跨生命周期语义仍按假设保留，推荐处理与理由见 `spec/acceptance.md` 第9节；本阶段没有自行作出功能取舍。
