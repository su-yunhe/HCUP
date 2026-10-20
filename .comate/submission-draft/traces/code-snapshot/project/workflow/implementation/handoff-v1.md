# vg-spec13 实现交接 v1

编码角色真实 `CODEX_THREAD_ID=01a143bf-40f7-7d62-b34c-af46d1698de6`，直接读取环境变量。生产源码已向主 Agent 明确冻结；本文只记录实现和局部检查，整题结论由主 Agent 结合独立验证作出。

## 输入与开工前核对

- 读取本题 `AGENTS.md`、`spec/requirement.md`、`spec/acceptance.md`、`spec/baseline-notes.md`、需求复审 v1 和批准设计 v1，以及本题有关源码；未访问其它题工程、来源修复历史、题包或初始化总览会话。
- `workflow/setup-result.json` 中官方 `baseline_prepare=pass`、`ohpm_install=pass`；首次生产修改前，将 `workflow/implementation-start-code-fingerprint.json` 的全部 tracked 文件 SHA256 与工作树逐项比较，差异为 0。
- 基线 `88db8789e28333c7b7dcc8db078f394a262b73c3`；需求复审 SHA256 `b6f2c67c11425b087d654a286866c7e584b527f2a5d067d5054958041dabee06`；最终批准设计 SHA256 `52c1ecbd06bfc1f55453c961ace20ec7e6a9d8cdce34632be6cb62faaf47162a`，均核对一致。
- 使用 `arkts-syntax-assistant` 与 `hmos-arkts-knowledge-retriever`；读取前者迁移规则、后者现存 Promise/async 文档及函数/语法限制。检索脚本因技能包缺少 `references/doc_index.json` 失败，改用包内现存文档定位，没有安装或修复技能。ArkUI 调用沿本题源码和编译器实证。

## 生产改动与需求覆盖

| 文件 | 改动与覆盖 | 最终行数 |
| --- | --- | --- |
| `entry/src/main/ets/sync/ManualWebDavBackupController.ets`（新增） | 进程内手动备份单例；独立状态快照、可移除监听器、同步 guard/复制输入/置忙；trim 校验、应用并尝试保存当前输入；直接 await 真实管理器 Promise；全路径 finally；通知异常隔离。R02/R03/R07/R08/R10。 | 110 |
| `entry/src/main/ets/pages/settings/SettingsSyncSection.ets` | 订阅即时恢复状态，离页注销；不在任务完成后续体中写已销毁组件；当前表单直接 start；输入、显隐及冲突操作以 aggregate busy 禁用并 guard；原手动 UI race 包装移除。原自动同步配置加载写回前检查 mounted。R01–R10 对应页面接线。 | 400 |
| `entry/src/main/ets/pages/settings/SettingsWebDavBuilders.ets`（新增） | 平移原表单、自动同步与操作卡片的纯渲染；手动按钮附近真实 `LoadingProgress` 24vp 与进行/结果文字；所有约定原生节点 id；spinner 仅由手动 busy 决定。R01/R04/R05/R09。 | 404 |
| `entry/src/main/ets/sync/WebDavSyncManager.ets` | 仅手动后台备份入口与预检可选配置参数：首 await 前复制设置；预检 endpoint/root/requireRoot 来自快照；预检立即捕获上传路径；client、后续加密上传参数使用同一配置；预检/yield 纳入同一 try/catch/finally。R02/R06/R07/R08。 | 1219（服务类，非 UI 组件） |
| `entry/src/main/ets/pages/SettingsPage.ets` | 原导航调用外置 Builder，路由和初始化流程保持；回调含稳定入口与返回 id。配合下一文件满足本题受改组件行数规则。 | 498 |
| `entry/src/main/ets/pages/settings/SettingsNavigationBuilders.ets`（新增） | 经主 Agent 追加授权，平移设置目录、标题和纯标题查询；目录使用带唯一 id key 的 LazyForEach，cachedCount=2。List 内容高度为 7×65vp，禁内部滚动，外层原 Scroll 控制滚动。 | 129 |

R06 继续原 `DataSyncManager.exportData → executeBackupWithEncrypt → WebDavClient.put` 真实链路，没有另建网络实现。控制器的在途状态覆盖配置应用、预检、导出、加密、上传与结果收尾；仅等待真实 Promise 终结才解除 busy。

控制器 `start` 只接收 `WebDavSettings` 数据；状态中无配置密码、Context 或组件。页面只在挂载时注册监听，销毁以同一函数引用注销。再次进入 subscribe 立即交付当前轮快照，不重发原任务；进程终止后的新单例自然空闲。配置通过原 `setSettings` 应用并尝试持久化，沿批准方案允许当前 B 输入替换已存 A。

控制器和手动经理入口均仅允许 IDLE/ERROR 开始，拒绝 TESTING/RESTORING/SYNCING。控制器先检查占用再 setSettings；经理开始前再次检查，拒绝分支不复位其它任务状态。页面恢复确认后增加一次 aggregate guard，防止确认期间出现的手动备份被后续恢复流程抢占。

原手动包装中的 Toast 随该包装移除，终态继续显示在原操作卡片；其它操作的 Toast 和原超时流程保留。新控制器不调用 UI 提示接口。

稳定 id：入口 `webdav_settings_entry`；分区 `webdav_settings_section`；五输入为 `webdav_endpoint_input` / `webdav_username_input` / `webdav_password_input` / `webdav_sync_password_input` / `webdav_remote_root_input`；手动按钮/进度/状态为 `webdav_backup_button` / `webdav_backup_loading` / `webdav_backup_status`；保存、测试、同步、恢复为 `webdav_save_button` / `webdav_test_button` / `webdav_sync_button` / `webdav_restore_button`；配置结果 `webdav_config_result`；返回 `settings_back_button`。id 位于目标原生节点。

## 实际局部检查

每次构建 PowerShell 进程首先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`（该脚本加载公共 Harmony 环境）。复现脚本为 `workflow/implementation/build.ps1`，在本题根运行：先 `ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true`，再执行：

```powershell
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon
```

| 实际操作 | 结果 | 证据 |
| --- | --- | --- |
| 初次依赖安装与 HAP 构建 | install=0；build=0；BUILD SUCCESSFUL in 37 s 382 ms | `logs/implementation-build/20261016-161710-{ohpm,build}.log` 与同前缀 `result.json` |
| 导航 LazyForEach 及最终格式调整后再次安装/构建 | install=0；build=0；BUILD SUCCESSFUL in 8 s 963 ms | `logs/implementation-build/20261016-162014-{ohpm,build}.log` 与同前缀 `result.json` |
| `git diff --check` | 退出 0，输出为空 | `workflow/implementation/implementation-checks-v1.json` |
| 静态类型/行数 | 六个生产文件均无 any/unknown token；四个受改 UI/Builder 文件为 498/400/404/129 行 | 同上报告 |
| 已跟踪文件范围 | 相对开工指纹仅三个已有生产文件变化；另有三个授权新增生产文件；初始化 AGENTS 和他人测试/记录保留 | `workflow/implementation/source-fingerprint-v1.json` |
| 告警比较 | 基线源码诊断 759，本次 754；按文件+消息的多重集比较新增组 0；三个新增生产文件诊断 0 | `logs/implementation-build/warnings-full.json` / `warnings-comparison.json` |

告警差额中，原手动包装移除对应 SettingsSyncSection 的 2 条 deprecated showToast 与 1 条 may-throw；另 2 条来自未修改 `ui/LoadingAnimations.ets` 的可选 @Prop 诊断在本次增量构建未出现，不能称为本改动修复。最终告警应以独立 clean build 为准。759/754 是原始日志中的带源码位置诊断数，不包含 FAQ 或签名配置提示。

两次真实构建均成功，没有构建失败或改断言/跳测试来取得通过。准备期的提取脚本曾因目标片段缩进断言和 SettingsPage 尚为 522 行断言中止，均在目标文件写入前失败；随后只修正本题提取脚本后完成平移。辅助只读命令曾因 Python 默认 GBK 输出 emoji 失败，后续显式设置 UTF-8；技能检索缺文件如前述。工具原始失败输出保留在本子会话记录，对应脚本保留于 `workflow/implementation/`，未伪称这些为业务测试失败。

## 指纹、产物与冻结

- 完整源码指纹：`workflow/implementation/source-fingerprint-v1.json`，含基线所有 tracked 文件及三个授权新增生产文件 SHA256。
- 聚合 SHA256：`8b6683b8ca4fed2eb3e4ab743c0f2028cae4a50ea1b8d7ae08fac77ca4e63db1`。计算方式：对路径→SHA256 字典执行 `json.dumps(..., sort_keys=True, separators=(',', ':'))` 的 UTF-8 再 SHA256。
- 本角色最后构建产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`；SHA256 `7154b877f452d1d1338c027576bafc575e3f72ab551db89cdb558396ab159fa4`；大小见检查报告。独立验证 clean build 会生成自己的产物与新指纹，不能把这份构建记录冒充验证构建。
- 已向主 Agent 发送明确冻结消息；此后无生产源码写入，仅补本文。未修改需求、设计、自测报告或调度状态。

## 独立验证接续与未解决项

本角色未执行设备安装、启动、UI/Hypium 或服务端请求采样，也未运行独立自测；构建与静态检查不等于场景通过。R01–R10 为实现覆盖映射，运行验收由主 Agent 指派验证角色完成。

必要后续实证：当前 B 输入直点请求归属；真实 pending 时两次 LoadingProgress 类型/可见性及中文字；成功/失败和再点；无效输入不回用旧配置；快速连点；分区返回、设置路由退出及系统返回后重入；重启；预检/上传失败与真实网络超时；原配置/恢复入口回归；导航 LazyForEach 可达性和外层滚动。导出/加密/TaskPool 异常若无法实际注入，明确未测，不能把静态 finally 当运行成功。

当前没有已知编译阻断或尚未完成的生产修改。保留本题既有其它动作超时/恢复策略，未推广全局并发框架。发现真实失败后由主 Agent 解冻并回派，编码角色按失败证据修复。
