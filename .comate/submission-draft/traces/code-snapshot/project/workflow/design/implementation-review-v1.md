# vg-spec13 实现中审 v1

CODEX_THREAD_ID：`01a143bb-a10f-7601-a510-405d234afe12`（直接读取环境变量）。

结论：**本次限定范围静态检查未发现阻断问题**；控制器和经理手动备份改动符合方案 v1。不是整体实现验收或运行通过。未读取仍在改写的页面，未运行构建、设备或测试；仅新增本文。

检查输入：`workflow/design/implementation-plan-v1.md`、当前 `entry/src/main/ets/sync/ManualWebDavBackupController.ets`、当前 `WebDavSyncManager.ets` 及该文件工作区 diff。来源仅本题，无外部查询。

| 检查 | 观察与结论 |
| --- | --- |
| 无 UI/Context 引用 | 控制器只导入经理及相关数据类型；任务接收纯 `WebDavSettings`，无组件或 AbilityContext 参数、字段、导入。监听器仍须由页面生命周期注销，此次不验证页面 |
| 首 await 前防重入与快照 | `start` 首先检查 `state.busy`，用 `new WebDavSettings(...)` 复制并规范化输入，再发布新 runId/busy；首 await 为 `manager.setSettings(snapshot)`。无效输入独立校验后终结，不回落旧配置 |
| 真实异步与终态 | `start` 直接 await 真正的 `backupToCloudInBackground()`，无 race；其 try/catch/finally 覆盖校验拒绝、经理占用拒绝、保存 false/抛错、yield、备份返回或异常；finally发布 busy=false。未保存 raw Promise 字段不影响现有 async 续体由真实 await 维持，其 busy 记录仍由进程内单例所有 |
| 观察者边界 | `getState()` 返回新状态对象；subscribe 即时通知；unsubscribe 用原函数引用删除；notify 捕获观察者异常，publish 遍历快照。没有在任务 Promise 中捕获某个页面的监听器或 this |
| 经理清理 | 经理取得 SYNCING 后将 client 创建、预检及后续全部放进同一 try/catch/finally。预检失败 return 或直接抛错都经过 finally IDLE；校验/占用拒绝在取得状态之前，不清理他人占用 |
| 配置与路径 | 经理首 await 前复制配置，client 使用复制值；预检显式接收复制值并从参数取 key/remoteRoot/requireRemoteRootExists；完成预检后立即捕获局部 backupPath；导出后的任务参数读取局部设置/路径 |
| TESTING/RESTORING | 已在控制器和经理看到 `status !== IDLE && status !== ERROR` 的占用拒绝，涵盖 TESTING、RESTORING、SYNCING，主 Agent 提出的点已落实 |

剩余闭环前提：页面完成后需验证 aggregateBusy 同时锁定五输入与保存/测试/同步/恢复入口，并在分区/路由重入后恢复此锁；同一监听器须 `aboutToDisappear` 注销。此处的 setter 隔离和共享远端布局安全仍建立在方案规定的页面锁与既有经理操作占用上，不把私有预检参数误认为通用并行隔离改造。运行证据仍需覆盖当前 B 输入直点、真实 pending UI/网络重叠、返回重入及经理失败后重试。

主 Agent 补正规则：方案 v1 中“SettingsPage 既有超长不扩展重构”的表述不能作为用户 AGENTS 每组件文件≤500行规则的豁免。该父页本轮会补入口/返回 id，编码需评估并落实最小纯 UI 提取（优先既有导航、标题 Builder），使受改 `SettingsPage.ets` 同样≤500行；仅平移必要渲染，保持路由、状态及初始化行为。该补正记录于本文，不覆写已批准方案文件及其 hash。

除上述组件行数合规补正，无其它方案调整；无生产或测试文件修改。
