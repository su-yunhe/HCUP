# vg-spec8 实现方案 01

## 1. 版本、范围与依据

- 方案版本：`implementation-plan-01 / v1`，面向本轮 `spec-harness/1-do.md`，可交编码与独立验证执行。
- 方案 Agent 实际 `CODEX_THREAD_ID=01a14503-4b1d-7e70-943e-a0d57c675547`。唯一写入为本文；未改生产、测试、全局 state/events，未构建或操作设备。
- 基线 `HEAD/base/vg-spec8=9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。已读 `workflow/setup-result.json`，官方准备 `baseline_prepare.result=pass`；不重复准备、不切版本。
- 实读并核对输入：`spec/acceptance.md` SHA-256 `69849e82f4402b87fd1a49cd53631b4a42154d24f3a9fbbc653c2786a98ef057`；`spec/baseline-notes.md` SHA-256 `e72636ed63581533a85d90a4040814a85b33eb3233cb694b2805344b73690556`。需求原件 `spec/requirement.md` 的三场景及 A1—A19 是覆盖基准。
- 定稿已读 `workflow/requirements/implementation-review-01.md`，其 A 项等级、U 项选择和测试隔离边界与本文一致。
- 仅使用本题 spec/workflow/源码/本题基线证据、允许的公共工具与技术文档。未读取其他题工程、题包来源、上游同功能修复、Issue、PR、补丁、初始化总览会话或其副本。
- 本文行号以未改动基线为准；短名 `SettingsSyncSection.ets` 位于 `entry/src/main/ets/pages/settings/`，其他文件在表中给全路径。

## 2. 实现结论与代码证据

在现有恢复入口与 busy 包装器之间新增第一层 D1。D1 仅展示本地确认，没有网络、恢复任务或恢复计时器。点击「取消」关闭并回原分区；只有明确点击本轮「继续」，D1 关闭完成后，才调用原有恢复包装器。下载后的 D2 和现有恢复服务继续使用。

| 基线事实 | 证据 | 方案影响 |
| --- | --- | --- |
| 正常入口是首页齿轮→SettingsPage→`sync` 分区 | `pages/index/components/TopNavigation.ets:69-79`；`pages/SettingsPage.ets:427-442,487-517` | 保留路由和分区，入口只补稳定 id。 |
| 恢复入口直接调用 busy 包装器；包装器先 busy、50 ms 延迟，再创建 120 s 超时并执行下载 | `SettingsSyncSection.ets:113-121,140-165,199-200` | D1 gate 必须放在调用包装器之前，不能把包装器放进“等待确认”的 Promise。 |
| 当前唯一恢复确认出现在下载、预览以后，按钮是「取消／确认恢复」 | 同文件 `199-230` | 它是 D2；保留，不冒充第一层，不把「确认恢复」改为「继续」。 |
| 网络可能先做根目录预检，产生 HEAD/PUT/DELETE 等 | `sync/WebDavSyncManager.ets:280-339,471-491`；`sync/webdav/WebDavBackupManager.ets:68-117` | 用 gate 隔离整个原恢复服务入口；测试统计全部方法、路径和响应状态。 |
| D2 取消已有返回及外层 finally 清 busy | `SettingsSyncSection.ets:224-230,155-156` | 不为未证实的 Promise 悬挂重写 D2。 |
| 自动同步独立于页面 busy，在进入前台时触发 | `entryability/EntryAbility.ets:49-57`；`sync/AutoWebDavSyncManager.ets:28-85` | 本题不扩大全局同步策略；测量必须先关闭并确认持久化、无在途任务。 |
| 当前同步组件 596 行，SettingsPage 551 行，TopNavigation 142 行 | 本轮 `Get-Content(...).Count` | 同步组件新增逻辑前做局部职责拆分；SettingsPage 只补两处 id，不开展整个设置页重构。 |

基线实测已收到未继续的真实请求（两次恢复共 6 条，HEAD×4、PUT×2），见 `spec/baseline-notes.md` 第 3 节及 `logs/analysis-baseline/mock-requests.jsonl`。这是待修差距，不是本方案运行结果。

## 3. 主 Agent 已裁定的 U 项

这些是本轮实现选择，不将 A15—A19 或 U 项改写成 Spec 新明文。

| 项 | 本轮选择 |
| --- | --- |
| U1 | 空、纯空白、未保存输入均先打开 D1；D1 前不做网络或配置保存。继续后沿用管理器已有配置与既有校验，不顺手改变“未保存输入”的恢复语义。 |
| U2 | 点击取消、系统返回、ESC、遮罩关闭等未授权退出统一按取消清理。不新增 X 按钮。 |
| U3 | 保留全局自动同步；独立测试先关闭并确认持久化，等待在途操作结束。结果只能证明隔离前置下本恢复意图无请求，不声称并发自动同步被全局暂停。 |
| U4 | 取消后的返回重进和重启作为回归；瞬时状态仅在组件内存，不持久化确认、授权或 busy。 |
| U5 | 保留 D2 和后续流程；继续后失败收尾、可达 D2 时取消作影响回归，不扩大核心需求为完整恢复成功。 |
| U6 | D1 严格单实例且模态；重复恢复或重复决定仅第一个有效动作生效。标题正文为普通 UI 选择，按钮原文必须「取消」「继续」。 |

## 4. 文件责任与最小拆分

所有生产改动由主 Agent 指定的编码角色统一写入。下列是责任范围，不授权方案角色写代码。

| 文件 | 修改责任与接口 | 预计规模 |
| --- | --- | --- |
| `entry/src/main/ets/pages/settings/SettingsSyncSection.ets` | 保留原 `@Link` 对外接口、配置保存、操作按钮、busy 包装器和 D2；加入局部 enum、单一 D1 controller、确认/关闭/授权处理与销毁清理。基础配置和自动同步区域改为实例化下列配置子组件。补操作区、保存、恢复、结果 id。 | 从 596 行移出约 225 行再加约 90—110 行，目标 <500 行；以最终实数为准。 |
| **新增** `entry/src/main/ets/pages/settings/SettingsWebDavConfigPanel.ets` | 单一 `@Component`；承接原基础配置、自动同步 UI、三个字段 builder、自动同步读取/保存/格式化辅助方法及 interval 常量。`@Link` 接收原 13 项配置/显隐/自动同步状态；通过 `@Link colors: ColorsInterface` 只读使用父颜色，沿用原赋值式状态更新。`WebDavStateStore` 仍是原单例，不新建持久化策略。五输入和开关在此补 id。 | 约 280—330 行，必须 <500。 |
| **新增** `entry/src/main/ets/pages/settings/WebDavRestoreConfirmDialog.ets` | `@CustomDialog`、`@Component`；仅本地标题/说明和两个 Button。接口 `@Link colors: ColorsInterface`，`onCancel: () => void`、`onContinue: () => void`，回调字段有显式初值。父负责 controller.close 和状态转换，Dialog 不调用服务，不创建等待确认的 Promise。 | 约 60—100 行，必须 <500。 |
| `entry/src/main/ets/pages/index/components/TopNavigation.ets` | 齿轮实际点击容器补 `.id('nav_settings_entry')`，保持原回调。 | 1 处属性。 |
| `entry/src/main/ets/pages/SettingsPage.ets` | 设置列表实际点击 Row 补 `.id('settings_section_' + item.id)`；页头返回点击 Text 补 `.id('settings_header_back')`。保留原 `SettingsSyncSection` 接口和路由。 | 2 处属性。 |

配置拆分的精确搬移块：原 `14-21` interval 常量、`53-97` 的 load/save/formatAutoSync、`261-433` 的配置/开关/card builders，以及相应 import/`webdavStateStore` 字段。新配置子组件在自身 `aboutToAppear` 执行原 loadAutoSyncSettings；不额外创建第二次读取。原父 `aboutToAppear` 改为只标记自身活动。SettingsPage 的原初始化不改。

保存配置按钮仍调用父 `saveWebDavSettings()`；输入通过二级 `@Link` 仍写回 SettingsPage。自动同步开关仍只调用原本的存储 setter，调用时机和缺省值不变。禁止为了拆分引入全局状态、全局事件总线、额外配置模型或复制服务。

如父仍略超 500 行，优先把原操作卡中完全静态的“使用说明”提成同目录已有拆分组件中的轻量导出 `@Builder` 并原位调用，保留视觉顺序；不要压缩多行代码伪造行数，也不要扩大到设置页全部分区。SettingsPage 551 行是现存技术债，本轮仅 id 属性改动不代表整仓已经符合 500 行规则；该事实单列，不借本题做无关重构。

本方案不改 `WebDavSyncManager`、`WebDavBackupManager`、`WebDavClient`、`AutoWebDavSyncManager`、`WebDavStateStore`、EntryAbility、模块权限、构建配置或持久化键。D2 的正文、按钮、预览、导入与 finally 顺序保持原样；如因新增告警需要改调用形式，必须先登记原因并限制在当前触及处。

## 5. 显式状态机及生命周期

使用父组件局部 `WebDavRestorePhase` enum，成员 `READY`、`CONFIRM`、`AUTHORIZED`、`BUSY`；`@State private restorePhase: WebDavRestorePhase` 初值 READY，以使按钮 enabled 和结果 id 正常刷新。另以私有 `restoreDialogClosing: boolean=false` 防止退出动效期间重复决定，以普通私有 `isActive: boolean=false` 记录组件活动。已有 `webdavBusy` 继续表示真实操作锁。三个新字段不进入 Preferences/AppStorage。

```text
READY --点击恢复且无 busy--> CONFIRM --取消/关闭并完成退出--> READY
                              |
                              +--明确点击本轮继续--> AUTHORIZED
                                                       |
                                              D1 onDidDisappear
                                                       v
                                                      BUSY
                                                       |
                                              原包装器 finally
                                                       v
                                                      READY
```

CONFIRM 包含正常显示和未授权退出动效阶段：退出完成前仍保持 CONFIRM、closing=true，既不联网也不接受新的决定。AUTHORIZED 只在显式继续到关闭完成之间存在。只有 BUSY 才允许调用原恢复包装器并使 `webdavBusy=true`。其他既有操作使用 `webdavBusy`，不会伪造本恢复 phase。

| 事件/入口 | guard 和状态更新 | 允许调用 | 禁止行为 |
| --- | --- | --- | --- |
| 恢复按钮/openRestoreConfirmation | `isActive && !webdavBusy && phase===READY`；同步先置 CONFIRM、closing=false，再 open | 唯一成员 controller.open | 不保存配置、不下载/预检、不导入、不调用 runWebDavBackupAction/runWithTimeout，不排 50/100 ms 或 120 s 恢复计时器。 |
| CONFIRM 中重复恢复 | 非 READY 直接 return | 无 | 不再创建 controller、弹窗、Promise 或任务。 |
| 取消 Button | 仅 CONFIRM 且 !closing；同步置 closing=true 后 close | 唯一 controller.close | 不授权、不改真实 busy，不发 Toast 伪装完成，不清空配置/已存在结果。 |
| 遮罩/系统返回/ESC | controller 的 cancel 回调将未授权 CONFIRM 标记 closing；由平台完成关闭 | 本地清理 | 不把非按钮退出当继续；无需重复 close 递归。 |
| 继续 Button | 仅 CONFIRM 且 !closing、活动且无 busy；同步置 AUTHORIZED、closing=true，再 close | 唯一 controller.close | 不立即运行包装器，不把已有“打开过/取消过”当授权。 |
| onDidDisappear：非 AUTHORIZED | CONFIRM/销毁取消都归 READY、closing=false；READY/BUSY 的无关回调直接忽略 | 本地复位 | 不做联网；不能对 BUSY 写 busy=false。 |
| onDidDisappear：AUTHORIZED | 再检查 isActive、!webdavBusy；有效才先置 BUSY、清 closing，调用 runAuthorizedRestore；不满足时撤销授权回 READY | 原 `runWebDavBackupAction(() => webdavRestoreWithPreview())` | 不让关闭回调绕过二次 guard。 |
| 原恢复完成/失败/D2取消 | 等待原包装器返回，外层 try/finally 把恢复 phase 归 READY；原包装器负责自己的 busy/result/toast | 原既有流程 | 不重写 D2 或通过结果文案分支决定是否解锁。 |
| open/close 失败 | controller API 有本地 try/catch；open 失败回 READY；close 失败撤销授权回 CONFIRM、closing=false，让仍显示的 D1 可再次取消，不提前发布新轮 READY；记录本地错误 | 本地错误记录 | 不在 catch/finally 继续调用恢复；不新增全局 toast/deprecated 调用。 |

`aboutToAppear` 只置 isActive=true。`aboutToDisappear` 先置 isActive=false；若尚在 CONFIRM 或 AUTHORIZED，则撤销授权（AUTHORIZED 改回 CONFIRM）、closing=true，安全 close。退出完成后 onDidDisappear 才归 READY。它不能在 AUTHORIZED 等待关闭时留下可运行的授权。READY 离开无事可做；已经 BUSY 的原请求生命周期不在本题扩改范围，不声称它被新 D1 取消逻辑中止。

**迟到回调隔离**：旧 D1 的 onDidDisappear 是该轮唯一允许发布 READY 的关闭完成点；在它到达以前 phase 保持 CONFIRM/AUTHORIZED，恢复入口的 guard 禁止新一轮。因此新一轮只能在旧关闭回调同步处理完以后开启，不存在先重开、后被旧关闭回调复位的正常路径。不在取消分支提前 READY，也不在关闭后另排 setTimeout/Promise.resolve 清理。组件销毁回调持有原实例，isActive 与已撤销 phase 双重阻断授权；新组件拥有自己的初值和 controller。若设备发现平台回调顺序不同，以实际证据回退方案，不能用任意等待时间规避。

Controller 在 `@Component` 成员声明时唯一初始化，builder 使用新 Dialog，`isModal=true`、`autoCancel=true`、`showInSubWindow=false`、中心对齐；使用 cancel 和 onDidDisappear 回调即可，不引入会阻拦默认关闭的 onWillDismiss。所有传入回调用箭头保持 this。Dialog 内容用 `@Link colors` 跟随颜色，不将 builder 的 `@Prop` 当作动态同步机制。

## 6. 稳定 `.id()` 合同

下列名称交编码、Hypium 与验收统一使用；本方案阶段尚未写入 UI。id 必须落到实际可操作控件/实际可见内容，不用数据 ForEach key 或 themeRefreshToken 根 id 代替。测试用 `BY.key(...)`，同时断言关键按钮精确文本、可见与 enabled；重渲染后重新查找，不复用已关闭 Dialog 的节点句柄。

| 代号/用途 | 精确 id | 归属与断言 |
| --- | --- | --- |
| S0 首页入口 | `nav_settings_entry` | TopNavigation 齿轮点击容器。 |
| S1 设置分区 | `settings_section_sync` | SettingsPage 数据 `sync` 对应实际点击 Row；由固定前缀+item.id 生成。 |
| S2 配置操作区 | `webdav_config_panel` | SettingsSyncSection 最外 Column，含配置与手动操作。 |
| S3 恢复 | `webdav_restore_button` | 原恢复 Button，空闲原文「从云端恢复」；D1 取消完成后 enabled，实际可重开。 |
| S4 D1 内容 | `webdav_restore_confirm_dialog` | 新 Dialog 根内容 Column；只代表 D1，在 D2 中不存在。 |
| S5 D1 取消 | `webdav_restore_confirm_cancel` | Button，精确「取消」。 |
| S6 D1 继续 | `webdav_restore_confirm_continue` | Button，精确「继续」。 |
| S7 请求状态 | `webdav_restore_request_loading` | 复用原 `Text(webdavBackupResult)`；仅 phase BUSY 且 webdavBusy 时选此固定 id。CONFIRM/AUTHORIZED 不出现此 id。 |
| S8 备份/恢复结果 | `webdav_restore_result` | 同一原结果 Text 在非本恢复 BUSY 时用此 id；仍按原 `webdavBackupResult.length>0` 条件显示。既有旧结果可保留，不规定取消结果文案。 |
| S9 返回 | `settings_header_back` | SettingsPage 现有页头返回 Text。 |
| S10 隔离自动同步 | `webdav_autosync_toggle` | 配置子组件实际 Toggle；UI 树 checked 状态及重进/重启读回用于前置证明。 |
| S11 五输入 | `webdav_endpoint_input`、`webdav_username_input`、`webdav_password_input`、`webdav_sync_password_input`、`webdav_root_input` | 配置子组件的实际 TextInput；字段 builder 增加显式 string id 参数，不用 label 或顺序推算。 |
| 配置保存 | `webdav_save_button` | 原「保存设置」Button，测试显式保存独立 mock 配置。 |
| 配置保存结果 | `webdav_config_result` | 原 `Text(webdavResult)`，按原条件显示；用于保存完成证明，不能冒充网络证据。 |

S7/S8 是同一文本按状态选择两个固定名称，保留原布局和显示条件，不新加 spinner 或额外进度 UI。CONFIRM 中因模态而暂时不可操作背景不构成 A7 失败；A7 在 D1 关闭后判断。恢复按钮可绑定 `!webdavBusy && phase===READY`，其文案仍只由真实 webdavBusy 决定，不能在纯确认态改成“处理中...”。

D1 可建议标题「从云端恢复」，说明继续后下载备份、预览确认后覆盖本地数据；标题和正文不是必须逐字匹配合同。只有两个动作文本是规定值。

D2 仍是原生 promptAction 弹窗，不给 buttons 配置伪造 `.id()`。若回归可达 D2，先从实际 UI dump 记录本应用 bundle/当前焦点窗口，再在同一窗口中定位标题「⚠️ 恢复确认」和「确认恢复」组成的弹窗子树，选择该子树内的「取消」。若 Hypium 无直接层级过滤，使用 dump 验证节点与所属窗口后采用工具支持的精确条件；不得按全局第 N 个「取消」或遗留坐标声称稳定通过。D1 核心用例始终只用专用 id。

## 7. A1—A19 覆盖映射

全部 A 项保留原证据等级。A1—A14 是核心明文/不变量拆分；A15—A19 为合理推导。有限循环数及观察时间是测试策略，不是 Spec 阈值。

| 项 | 方案落点 | 最小可观察验证 |
| --- | --- | --- |
| A1 | 原导航/分区，S0—S3 | 从首页正常入口进入，S2/S3 可见。 |
| A2 | READY→CONFIRM，D1 在包装器前 | 点 S3，S4 存在；S7 不存在且请求 0。 |
| A3 | Dialog 明确取消 Button | S5 精确「取消」、可点击，归属 S4。 |
| A4 | cancel→close→onDidDisappear→READY | 点 S5 后 S4 不存在，不能只看 Toast。 |
| A5 | 模态默认关闭，原操作区保留 | S2 可见，配置输入/恢复入口可交互，无遗留遮罩。 |
| A6 | 取消不启动 busy、不替换入口 | S3 可见且精确「从云端恢复」。 |
| A7 | READY 和原 busy 分开 | S3 enabled；无须等待网络/超时。 |
| A8 | 关闭完成后重新允许 open | 取消后再点 S3，S4/S5 再出现。 |
| A9 | open 路径无服务/包装器/计时器 | 首次 D1 停留，请求累计 0。 |
| A10 | cancel/close 只本地清理 | 取消及之后等待窗口，请求累计 0。 |
| A11 | 每轮重新 CONFIRM，无授权持久化 | 再开 D1 未继续，请求仍为 0。 |
| A12 | 无预授权延迟任务 | CONFIRM、取消后 READY、再开停留均持续 0；配合静态调用路径审计。 |
| A13 | 无轮数相关状态，关闭后可复用 | 连续至少 10 轮开/取消/再开，逐轮 UI 断言，累计 0。 |
| A14 | 同步 guard、唯一 controller、closing 防重复决定 | 快速点击恢复/取消，不点 S6；请求 0，最终可继续操作。 |
| A15 | 唯一 AUTHORIZED 写点是 S6 onClick | 静态核对授权写点；独立对照点本轮 S6 后才允许真实请求。 |
| A16 | import 仍在 gated 原恢复链末端 | 主取消全程本地非空哨兵数据不变；无恢复导入调用路径。 |
| A17 | CONFIRM/AUTHORIZED 的 busy=false，无恢复计时器 | D1 无 S7/真实“正在处理”新增状态；网络 0，静态查 gate 前无任务调度。 |
| A18 | 关闭事件本地复位，不依赖原网络 finally | 取消完成后 S3 enabled 并实际重开；不靠 120 s 超时解锁。 |
| A19 | 单实例、退出期间禁止新轮、销毁撤销待授权 | 快速重复取消最终 S4 消失、S2 可操作、S3 可重开，累计 0。 |

## 8. 实现顺序与交接检查

1. 确认本题官方准备 pass、当前工作区差异属于本题；不还原别人正在写的 workflow 文档。编码前仅修改上表生产范围。
2. 先等价搬移配置和自动同步展示/原辅助方法至 SettingsWebDavConfigPanel，保持父对 SettingsPage 的配置接口不变；补五输入与 Toggle id。检查字段仍双向写回、自动同步没有新增任务或额外初始化。
3. 新增纯展示 D1，补根/取消/继续 id；父加入唯一 controller、局部 phase、closing、active 及完整关闭回调。不引入等待用户决定的 Promise。
4. 把原 webdavRestore 按钮路径改为只打开 D1；原包装器调用移到授权关闭完成分支。原 webdavRestoreWithPreview/D2 和服务调用体保持。最后 finally 复位 restore phase。
5. 补 S0/S1/S2/S3/S7/S8/S9 及保存/配置结果 id，核对空闲和 busy 的固定 id/text/enable 合同。检查同步父、新配置组件、新 D1 均 <500 行。
6. 用本题基线告警清单作对照构建，处理新引入 ArkTS 告警/错误，不靠 suppress、替换 SDK 或全仓迁移消除差异。为新 controller 的可能抛错调用加必要局部处理；新增 UI 提示优先 UIContext.getPromptAction 或直接不用提示。保留原调用不等于允许新增 deprecated 使用。
7. 编码角色完成本地构建和最小手测证据后，独立验证重新构建、安装刚产出的本题 HAP，按下节执行连续网络观察及 UI 场景。最终映射记录每项 pass/fail/not_run，未测不算通过。

## 9. Hypium 独立实测建议与证据

开始任何构建/设备命令前，在该 PowerShell 进程加载 `. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。使用本题 `test-harness` 及允许公共环境，测试代码归验证角色，可放 `hypium_tests/test_webdav_restore_cancel.py`；服务端观察脚本与结果放本题 `logs/implementation-01/`。不修改共享 common 框架，不把测试源码加入业务 HAP。

### 9.1 前置与观察有效性

- 安装本轮实际构建 HAP，记录 HAP SHA-256、源码指纹、build/install/start exit code、设备 API/屏幕环境与开始前 UI dump。不能只运行基线已有 HAP。
- 通过 S0/S1 正常进入；关闭 S10，等待原异步保存完成，返回再进入或重启读回 checked=false；已运行的同步完成后再设 t0。配置输入全部通过 S11 填本题独立 mock 端点/账号/目录，点 webdav_save_button，确认 webdav_config_result 保存成功并读回。禁止复用未知旧 endpoint。
- 可复用本题基线观察器原理：`logs/analysis-baseline/mock_webdav.py` 接收并记录真实 HEAD/GET/PUT/DELETE/PROPFIND/MKCOL/OPTIONS 等，响应 404；实现时可缩短主用例响应时间，另以延迟响应观察继续后的 busy。不得只统计下载 GET、只统计成功响应或事后过滤自动同步请求。
- t0 在第一次恢复点击之前，记录计数基点；整个开/取消/等待/再开过程不清零，保留方法、路径、时间戳、状态码。服务端可达性用独立授权继续对照证明，并与主零请求窗口分开；不能以空配置零请求当充分证据。
- 使用非空、可安全对比的本地哨兵学习/词书数据，前后读回同一业务数据快照；仅比较学习数据，配置/日志写入允许。观察器不记录 Authorization/密码或请求正文。

### 9.2 建议用例集合

| 用例 | 动作与断言 | 对应与结果边界 |
| --- | --- | --- |
| T1 正常取消/重开 | S3→S4/S5/S6；等待；S5；断 S4 不存在、S2 可用、S3 原文且 enabled；再 S3、再取消。全程网络 0。 | A1—A12、A15、A17—A18；必须分开保存 UI 断言。 |
| T2 反复与快速动作 | 至少 10 轮开/取消，逐轮记录关闭/重开与累计计数；再对恢复、取消做短间隔连点，防止事件穿透误点 S6。最后可回操作区、可再开。 | A13—A14、A19；一次取消应清掉本轮唯一层。循环数不是 Spec 上限。 |
| T3 纯等待与本地数据 | 开 D1 停留、取消后停留、再开停留；每段建议 3—5 s，配合静态路径证明 gate 前没有恢复计时器；哨兵前后相同。 | A9—A12、A16—A17。有限等待不宣称证明任意时间；原 120 s 超时不在未授权路径，核心无需为它等待。 |
| T4 空/空白配置 | 在可还原测试配置前提下，输入为空和纯空格分别点击 S3，均先显示 D1，取消可再开，网络 0；保存/未保存两种状态记录清楚。 | U1 选择、A2/A9/A18；之后恢复本题独立 mock 配置再做正控。 |
| T5 非按钮关闭 | 每轮开 D1 后用系统返回；另轮点击遮罩。各自断 S4 消失、S3 原文/enabled、可再开、请求 0。 | U2、A4/A5/A18/A19 推导保障；系统返回不应把确认误授权。 |
| T6 返回与重启 | 取消后 S9 回设置列表再入；再取消后正常停止/重启本应用，从 S0/S1 重进，S10 仍关闭；可开可取消且主窗口请求 0。 | U4 回归。记录重启前后隔离，不把前台自动同步混进主结果。 |
| T7 明确继续正控 | 独立网络窗口开 D1，点击 S6。D1 先消失，原请求/延迟 404 后原结果收尾、S3 可用；请求 >0 证明计数链路有效。快速重复 S6 不得多开恢复。 | A15 授权对照及变更影响回归；不要求恢复成功；其请求不并入取消场景。 |
| T8 D2 可达回归 | 仅在已有安全有效备份可用时，授权后到原 D2，按窗口限定取消，观察原 finally 收尾。没有备份时明确 not_run。 | U5；不因准备不到有效备份阻断明文取消验收，也不报告 D2 已通过。 |

Hypium 使用 `BY.key` 按合同定位；等待关闭用有界轮询 S4 不存在/不可见并再查 S3，避免固定大 sleep。记录 enabled、精确文本和实际重开三个独立结果。UI loading 和哨兵不变均不能替代服务端零请求证据。客户端连接失败而服务器无日志时不能宣称“无尝试”；用可达本地端点与授权正控消除假阴性，必要时补客户端 HTTP 边界证据。

保存至少：构建完整日志及新/旧告警对照、测试脚本、每条测试的退出码、连续 `requests.jsonl`、t0/各点击/关闭/结束时间、关键 UI 树/截图、哨兵前后摘要、自动同步持久化证据、HAP/源文件指纹。关闭临时 mock/本题转发并确认无监听，保留原本其他转发；设备测试状态由主 Agent 记录，不自动恢复未知旧服务端或删除业务数据。

## 10. 技术文档来源、权衡与失败回退

本轮已读 `arkts-syntax-assistant` 与 `hmos-arkts-knowledge-retriever` 技能。后者 `scripts/search_docs.py --query 'enum class Promise async finally'` exit 1，缺少 `references/doc_index.json`；未安装或修复技能。随后直接读取允许本地技术文档，未把检索失败写成验证成功。

| 来源 | 类型与用途 | 访问/匹配结论 |
| --- | --- | --- |
| [OpenHarmony 6.0 官方 CustomDialog API 文档](https://github.com/openharmony/docs/blob/OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md) | 官方技术文档，2026-10-16 查询，限定文档仓库，不涉及应用源码或修复历史。 | controller 成员初始化、模态/遮罩退出、cancel 和关闭完成回调；onDidDisappear 自 API19，低于工程 API22。builder 动态数据用 Link。 |
| `C:/Users/22580/.codex/skills/hmos-arkts-knowledge-retriever/linter-cli/runtime/compiler/declarations/custom_dialog_controller.d.ts` | 技能所带 SDK 类型声明，辅助 API 签名核对，不作为官方运行证据。 | 本地存在 cancel、autoCancel、isModal、onDidDisappear、open、close 声明。 |
| `D:/HCUP/common/skills/hmos-arkts-knowledge-retriever/docs/ArkTS-Language-Guide/Basic-Syntax/enumerations.md`；`initialization.md` | 本地语言指南，直接读取，分别为 Declaring an Enumeration、Default Property Values。 | 局部有限状态 enum、字段显式初值；不生成 any/unknown 或动态对象属性。 |
| `C:/Users/22580/.codex/skills/arkts-syntax-assistant/references/en/typescript-to-arkts-migration-guide.md` | 本地迁移规则，Use Explicit Types Instead of any or unknown，规则 arkts-no-any-unknown。 | 新字段/回调有具体类型，错误使用既有 Error 分支处理。 |
| `test-harness/README.md`、`harness/driver.py` | 本题测试框架说明与实现。 | 本题 Hypium BY.key 合同、有界等待、前置不足 skip/not_run，不将其算通过。 |

**权衡**：CustomDialog 比新增一个原生 showDialog 更便于给 D1、取消、继续配置稳定 id，也避免新增全局 deprecated showDialog 使用；增加一个轻量组件和局部 controller，不引入全局协调。配置拆分约 225 行是为满足本次同步组件 <500 行并保持逻辑聚合；没有借机改变服务与保存规则。默认模态与关闭完成事件提供单实例及安全重开，无需轮询关闭或额外延迟任务。

| 失败证据 | 归因与最小回退 |
| --- | --- |
| 未继续已有请求，静态仍从恢复 Button 或 CONFIRM 路径进入 wrapper/service | 实现偏离 gate；仅修父恢复入口/授权调用点，重新跑 T1—T3；保留原网络服务。 |
| 零网络但取消后按钮忙/不能重开 | 核对是否提前 webdavBusy、未清 closing、onDidDisappear 未归 READY；若实现符合本文但平台关闭回调未到，属方案/API 假设失败，带设备时序回方案改关闭收尾，不加任意 sleep。 |
| 销毁后仍由 Authorized 发请求 | 实现少撤销/少 isActive guard；只改生命周期与授权关闭分支，增加该事件序列回归。 |
| 旧关闭影响新轮 | 核对是否取消时提前发布 READY 或排了异步清理；先恢复“关闭完成才 READY”的串行约束。若完全符合仍复现，按真实生命周期修订 controller 事件隔离。 |
| 输入/保存或自动同步开关读回变化 | 配置拆分偏离；仅修 Link 参数/原辅助方法搬移，不扩大持久化策略。 |
| 请求来自已开启的独立自动同步 | 前置失败，先完整隔离重跑并报告原失败日志；不能过滤请求伪报通过，也不由此扩改全局同步。 |
| 新增 ArkTS 诊断 | 先修新增类型、回调绑定或 controller 异常处理。搬移诊断按原消息/符号对应，不将换文件行号当消除，也不对旧告警做无关全仓修复。 |

未解决的阻塞需求：无。待验证的技术点：当前 SDK 构建零新增诊断、D1 生命周期和 id 在真实 UI 树中的呈现、连续网络零计数、配置拆分后的读写保真。有效备份/D2 深回归可暂为 not_run，但必须明确限制；本方案不声称已经完成功能或测试通过。
