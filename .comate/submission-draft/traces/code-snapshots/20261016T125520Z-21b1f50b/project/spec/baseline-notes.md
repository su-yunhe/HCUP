# vg-spec9 基线现状

本轮只执行 `spec-harness/0-analyze.md` 的分析阶段，不修改业务代码。记录日期：2026-10-16（Asia/Shanghai）。下文分别标明 **代码实证**、**设备实测** 和 **推断／未验证**；基线存在缺口不等于本轮分析失败，也不代表整题已验收。

## 1. 基线快照与输入

- 基线 HEAD：`a22f32b07bf81c6dde4367e2543ebac29186cbc1`，与 `spec/metadata.json:2` 一致；采用记录 HEAD 的方式，不额外创建 tag。
- Spec SHA-256：`c6236994e253c6de9f6decd99d7c0637620027ac16ce3699154796cba7a5edbf`。
- metadata SHA-256：`496950d171e032fe6f10cf76fd485341f4f293b6f162857d60a46bd98756f660`。
- 本轮开始时，准备阶段 `workflow/setup-code-fingerprint.json` 中 296 个已跟踪文件的文件哈希全部一致。相对 HEAD 已有的 `AGENTS.md` 修改属于准备阶段流程规则；本轮未改该文件，也未改业务源码或构建配置。设备验证另存覆盖 269 个工程相关文件的 `traces/baseline-analysis/source-fingerprint-before.json`。

## 2. 构建、安装与实际操作

使用 `hmos-arkts-syntax-checker` 的构建检查方式；本阶段禁止执行其代码修复步骤。每个构建／设备 PowerShell 进程先加载：

```powershell
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
```

本轮重新构建，未把准备阶段的构建记录当成本轮实测。实际构建命令如下，退出码为 0，编译器实际执行，耗时 16.707 秒：

```powershell
hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

完整命令、退出码和告警见 `traces/baseline-analysis/02-build-command.log:16`、`build-raw.log`、`build-exit.txt`。构建成功的原始证据：`traces/baseline-analysis/build-raw.log:2313`。本轮安装和启动命令如下，退出码均为 0，见 `traces/baseline-analysis/03-device-install.log:60`、`:63`：

```powershell
hdc install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc shell aa force-stop io.qzz.weiyu
hdc shell aa start -a EntryAbility -b io.qzz.weiyu
```

完整既有告警清单见 `traces/baseline-analysis/build-warning-index.md:14`：逐条保存源码路径、行列、消息和原始构建日志行号，供后续新增告警对比；机器可读版为同目录 `build-warning-index.json`。共 759 条文件诊断，分类如下（统计见 `build-warning-summary.json:2`），另有 1 条无签名配置告警；本阶段均只记录，不修复。

| 既有诊断类别 | 数量 |
| --- | ---: |
| `Function may throw exceptions. Special handling is required.` | 505 |
| 弃用 API | 249 |
| `Classes cannot be used as objects (arkts-no-classes-as-obj)` | 2 |
| `Usage of 'ESObject' type is restricted (arkts-limited-esobj)` | 1 |
| `@Prop text` 不可为 optional parameter | 1 |
| `@Prop duration` 不可为 optional parameter | 1 |

本轮 HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`；SHA-256：`6397218e05107233a02eaf9154367af16eed5843b09a1c9ab1224466793364a8`。构建日志存在 `No signingConfig found for product default`（`build-raw.log:2309`），因此产物为 unsigned；本机模拟器安装成功不能替代其他设备的签名要求。

**设备实测入口**：在 `127.0.0.1:5555` 上安装本轮 HAP、启动 `io.qzz.weiyu/EntryAbility`，从首页点击 `⚙`，在设置目录点击 `WebDAV 配置`，到达设置页内部的 WebDAV 分区。证据：`traces/baseline-analysis/launch.json`、`settings-menu.json`、`webdav-initial.json` 及对应 PNG、`navigation-webdav.log`。模拟器保留已有应用数据；本轮启动直接到首页，**首次安装引导未实测**，没有清空应用数据。

**实际环境**：DevEco 6.1.0.860、SDK API 23；Python 实际来自 `D:/HCUP/common/.venv/Scripts/python.exe`，Hypium 6.1.0.210。设备 API 23、系统 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`，截图／窗口树为 1308×2880；具体虚拟机型和 560 DPI 未独立确认，不宣称与正式环境全部一致。环境命令和输出索引见 `workflow/verification/round-01-baseline-evidence.md` 的“基线、环境和产物”节，以及 `traces/baseline-analysis/01-preflight.log`、`03-device-install.log`。

## 3. 入口、路由和返回

| 环节 | 代码实证 | 设备证据／限制 |
| --- | --- | --- |
| 应用入口 | `AppScope/app.json5:3` 的 bundle 为 `io.qzz.weiyu`；`entry/src/main/module.json5:6` 的 mainElement 为 `EntryAbility`；`entry/src/main/ets/entryability/EntryAbility.ets:35` 加载 `pages/Index`。 | 本轮安装和启动成功，见第 2 节。 |
| 首页设置入口 | `entry/src/main/ets/pages/index/components/TopNavigation.ets:70` 显示 `⚙`，`:79` 执行回调；`entry/src/main/ets/pages/Index.ets:325` 调用 `router.pushUrl({ url: 'pages/SettingsPage' })`。 | 已沿此路径实际进入，未使用测试专用路由绕行。 |
| 设置目录 → WebDAV | `entry/src/main/ets/pages/SettingsPage.ets:41` 的项目为 `{ id: 'sync', title: 'WebDAV 配置' }`；`:527` 的点击将 `activeSectionId` 设为 `sync`；`:447` 渲染 `SettingsSyncSection`。路由登记在 `entry/src/main/resources/base/profile/main_pages.json:7`。 | **是 SettingsPage 内分区**；没有独立的 WebDAV 页面路由，也不是弹窗。 |
| 头部返回 | `entry/src/main/ets/pages/SettingsPage.ets:172` 的 `handleHeaderBack()`：在分区时清空 `activeSectionId` 返回设置目录，否则执行 `router.back()`；`:487` 绑定头部箭头。 | 运行中返回、系统返回键行为、返回后重新进入是否准确反映后台任务，待后续专项验证。 |
| 首次引导 | `entry/src/main/ets/pages/Index.ets:115` 的 `maybeShowOnboarding()`，`:131` 查询 `hasSeenOnboarding`，`:136` 跳转 `pages/OnboardingPage`。 | 本轮保留已有数据，首次引导仅代码实证，未验证全新数据状态。 |

## 4. 相关组件、状态、数据和服务

| 对象 | 基线事实及位置 | 对本题的意义 |
| --- | --- | --- |
| 配置状态 | `entry/src/main/ets/pages/SettingsPage.ets:114` 起的 `@State` 包含地址、账号、密码、同步密码、远端目录；`:190` 从 manager 回填；`:448` 起以 `@Link` 参数传给子组件。 | 沿既有配置和数据绑定实现，不另建一份配置或替代入口。 |
| 组件内部状态 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:41` 的结果文字和 `:43` 的 `@State webdavBusy = false`。 | 目标已有忙碌状态，可复用；页面局部状态和 manager 状态是两套变量。 |
| 手动同步动作 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:289` 起的 `webdavSyncNow()`：busy 防重入 → 置 busy → 提示文字 → 延迟 100ms → 保存设置 → 延迟 50ms → `syncIncremental()` → 结果提示 → `finally` 清 busy（`:316`）。`:578` 按钮调用它。 | 已有真实业务调用，不能只新增一个与请求无关的 UI 定时动画。 |
| 同步按钮和反馈 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:578` 在 busy 时改为 `处理中...`；`:585` 禁用按钮；`:567` 展示 `webdavResult`。保存、测试连接、备份、恢复也共用 busy（`:543`、`:553`、`:594`、`:604`）。 | 禁用和文字可以佐证忙碌，不能替代 Spec 要求的 ArkUI `LoadingProgress`。 |
| 设置保存 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:100` 将 endpoint、username、remoteRoot trim 后构造 `WebDavSettings`；`:109` 调用 manager 保存，`:110` 会覆写结果文字。 | 正在同步时的结果文字可能被保存结果覆盖；这是代码风险，实际时序需结合设备证据。 |
| 数据模型 | `entry/src/main/ets/sync/webdav/WebDavCommon.ets:3` 定义 `IDLE / TESTING / SYNCING / RESTORING / ERROR`；`:49` 定义 `WebDavSettings`；`:102` 定义设备、词条／事件同步时间戳等 manifest；`:185` 定义同步结果。 | 已有完整模型，无须为加载组件改变 WebDAV 协议或迁移数据库。 |
| 同步 manager | `entry/src/main/ets/sync/WebDavSyncManager.ets:100` 为单例；`:164` 校验配置；`:672` 的 `syncIncremental()` 在校验和防重入后置 `SYNCING`，`:693` 做远端预检，再处理词条下载／上传、事件下载／上传（`:707`、`:749`、`:791`、`:845`）；`:903` 最终重置 `IDLE`。 | 一次同步可包含多个请求及本地处理；加载生命周期应覆盖整个实际同步流程。 |
| 网络客户端 | `entry/src/main/ets/sync/WebDavSyncManager.ets:177` 用配置创建 `WebDavClient`；`:298` 的预检发送 HEAD。`entry/src/main/ets/sync/webdav/WebDavClient.ets:88` 拼接 endpoint 与 path，`:126` 创建 HTTP 对象，`:149` 发出请求，`:143`／`:144` 配置连接／读取超时。 | 有真实请求实现。HTTP 方法和请求数量取决于数据及预检分支，不是 Spec 新增限制。 |
| 后台执行 | `entry/src/main/ets/sync/webdav/WebDavSyncTask.ets:210` 起执行下载，`:280` 起执行上传；manager 的后台执行与回退见 `entry/src/main/ets/sync/WebDavSyncManager.ets:1087` 起。 | 请求／加密服务继续复用；纯代码阅读不能证明每台设备均成功使用 TaskPool。 |
| 本地存储 | `entry/src/main/ets/utils/WebDavStateStore.ets:63` 使用 `webdav_state_store` Preferences；`:66`、`:72`、`:78` 为 settings、manifest、snapshot 主／备份 key；`:128` 初始化；`:284` 保存 JSON 主副本并 `flush()`。manager 在 `entry/src/main/ets/sync/WebDavSyncManager.ets:132` 初始化和回读配置。 | 保存配置、重新进入和重启后的持久化基线已有代码；本轮不改变存储格式。 |
| 自动同步干扰源 | `entry/src/main/ets/entryability/EntryAbility.ets:53` 前台触发 `tryRun('foreground')`；`entry/src/main/ets/sync/AutoWebDavSyncManager.ets:33` 检查 busy、配置、开关、间隔，`:65` 调用同一 `syncIncremental()`。 | 单看服务端“有请求”不能归因为手动点击；后续测试须关闭自动同步或隔离日志并证明因果。 |

## 5. 可复用实现与缺失能力

**代码实证，可复用**：既有入口、`@State`／`@Link` 配置、`webdavBusy`、`webdavSyncNow()`、防重入、异步 manager、网络与存储链路如上表。工程已有 ArkUI 加载组件用例：`entry/src/main/ets/pages/TaskLoadingOverlay.ets:18` 的 `LoadingProgress()`，可参考其组件和主题用法；是否复用整个全屏 overlay 属于后续方案选择，Spec 没有要求遮罩。

**代码实证，缺失**：目标 `SettingsSyncSection.ets:1` 至文件末尾没有 `LoadingProgress()`，也没有稳定 `.id()`；其 `build()` 在 `:684` 只组合基础配置、自动同步、手动操作卡片。故基线不能以现有的“处理中...”按钮文字满足 Spec 场景一第 4 步。本轮请求进行中的两次 UI 树和截图进一步确认缺失，见第 8 节。

**推断，尚未实测的风险**：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:116` 使用 `Promise.race` 包装 120000ms 超时（`:114`），代码未见配套的底层取消调用；`:315` 的 finally 可能已清 UI busy，而被竞争的后台任务仍在运行。返回导致子组件重新创建也可能使局部 busy 与单例任务不同步。需要延迟／异常／返回再入测试确认，不能把这些推断写成已复现故障。

## 6. 前置环境与本轮验证范围

WebDAV 场景需要设备可访问的服务地址、认证账号／密码、同步密码和可用远端目录；基线配置字段见 `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:439` 至 `:445`，manager 配置校验见 `entry/src/main/ets/sync/WebDavSyncManager.ets:164`。正常入口不依赖云端应用账号登录；这只说明本轮从已有数据进入设置未遇登录门槛，不保证任意环境的外部 WebDAV 服务无需认证。

本地可满足构建、模拟器安装、设置导航，以及使用隔离服务观察请求与延迟状态。实际外部 WebDAV 服务可用性、完整同步成功／数据一致性、重启／返回等边界的结果只按后续证据登记；不得以“本地服务收到一次错误分支请求”宣称完整同步成功。

## 7. 测试可观测性风险

| 目标 | 基线事实 | 后续验收建议 |
| --- | --- | --- |
| 首页入口／设置分区 | `TopNavigation.ets:69` 的图标入口、`SettingsPage.ets:527` 的分区卡片没有专用 id。 | 保留官方既有导航；实现时补静态 id。 |
| 配置输入 | `SettingsSyncSection.ets:356`／`:379` 的通用 TextInput builder 没有 id；两处密码可见按钮均为 `显示`（`:389`）。 | 按字段补唯一 id，不能依赖第 N 个 TextInput 或同名按钮。 |
| 同步按钮／结果 | `SettingsSyncSection.ets:578`、`:568` 没有 id；busy 时五个手动操作按钮均可能为 `处理中...`。 | 以同步按钮固定 id 和 enabled 断言，结合加载组件和网络证据。 |
| 加载组件 | 目标源码未实现 `LoadingProgress`。 | 实现时补加载组件及静态 id；按类型＋可见性断言，截图或同名文字不足以替代。 |
| 设置根节点 | `SettingsPage.ets:565` 有 `settings_` 加主题刷新 token 的动态 id。 | 可辅助界定页面，不能当作各字段或加载状态的稳定选择器。 |
| 自动同步 | 与手动同步共用 manager（第 4 节）。 | 关闭自动同步、独立端点／请求日志窗口，关联点击时间与服务端接收时间。 |

已有 `entry/src/ohosTest/ets/test/WebDavSyncManagerIncremental.test.ets:10` 和 `WebDavStateStore.test.ets:6` 分别覆盖 manager／内存存储场景；本轮未运行这些测试，不能用它们证明 UI 加载与真实服务端请求绑定。验收矩阵见同目录 `acceptance.md`，矩阵是待执行标准，不是通过报告。

## 8. 本轮延迟请求实测与基线判定

**夹具范围**：只使用本轮测试账号／密码和 `http://127.0.0.1:18769`，远端目录 `/vg-spec9-round01`；通过 `hdc rport tcp:18769 tcp:18769` 连接宿主机受控 HTTP 服务。服务核对测试认证头，但故意让 HEAD 延迟 12 秒并返回 403，其他方法立即返回 403。自动同步开关保持关闭。此夹具用于证明真实请求、请求期间忙碌表现和失败后恢复，**不满足“目录可正常同步”的完整成功前置条件**。因此不以本轮失败响应声称 A2 或成功同步主路径通过。

代码与原始命令分别见 `workflow/verification/baseline_probe.py:10`、`baseline_sync_once.py:16`、`traces/baseline-analysis/05-configure-test.log:11`、`06-sync-test-command.log:11`。观察脚本退出码 0 仅表示采集完成，不能解释为 Spec 验收通过。请求最终全集为 `traces/baseline-analysis/webdav-requests.jsonl:1` 至 `:6`；点击与采样时间在 `sync-observations.json`。所有下述时刻均为 2026-10-16、UTC+08:00。

| 时刻／状态 | 实际观察 | 证据 |
| --- | --- | --- |
| 19:41:38 起，点击前 | `立即同步` 可见且 enabled=true；LoadingProgress 数量 0。 | `traces/baseline-analysis/sync-before.json`、`sync-before.png`；`sync-observations.json:2` 起。 |
| 19:41:40.356 | 点击操作返回，随后出现本轮隔离端点请求。 | `sync-observations.json` 的 `clickReturned`；`ui-commands.jsonl` 记录实际点击。 |
| 19:41:40.592 → 19:41:52.593 | 第一个 HEAD `/vg-spec9-round01`，认证头与本轮夹具相符，延迟响应 403。 | `webdav-requests.jsonl:1`、`:2`。 |
| 19:41:41.171、19:41:45.000 | 两次请求未结束窗口均有 5 个 `处理中...` 按钮，全部 enabled=false；实际 `LoadingProgress` 类型节点数均为 0。屏幕上操作区可见且无加载指示器；结果文本为 `✅ WebDAV 设置已保存`，不是同步完成证明。 | `sync-during.json`、`sync-during-second.json` 及对应 PNG；采样时刻在 `sync-observations.json`。源码对应 `SettingsSyncSection.ets:110`、`:578`。 |
| 19:41:52.642 → 19:42:04.643 | 第二个 HEAD，同样延迟 12 秒并返回 403。 | `webdav-requests.jsonl:3`、`:4`。 |
| 19:42:04.710 → 19:42:04.712 | PUT `/vg-spec9-round01/.probe_1792150912648.txt`，认证匹配，返回 403。它属于既有远端目录预检／可写性探测链路，不是用户点了“测试连接”。 | `webdav-requests.jsonl:5`、`:6`；manager 的预检链路见 `entry/src/main/ets/sync/WebDavSyncManager.ets:263`、`:284`。 |
| 19:42:08.511 起最终补采样 | 显示 `⚠️ WebDAV 连接失败：STEP remoteRoot PUT 403: 权限不足（目录可能不可写）`，`立即同步` 恢复 enabled=true，busy 按钮为 0；加载组件仍为 0。 | `sync-final.json`、`sync-final-summary.json`、`sync-final.png`、`sync-final-ui.log`、`sync-final-observations.json`。这是记录的基线文案，不是新增 Spec 文案。 |

**采样纠正**：`sync-observations.json` 中名为 `after` 的样本采于 19:41:55，实际仍处于第二个 HEAD 进行期，故其中 `busyRestoredAfterError=false` 是过早采样的结果，**不能据此认定恢复失败**。原始记录保留，最终恢复结论以 `sync-final` 补采样为准。不能把第一条响应当作整个多请求同步流程结束。

| 验收覆盖 | 基线结论 | 限定 |
| --- | --- | --- |
| A1 既有入口 | `pass` | 已安装本轮 HAP 并沿正常路径实际进入。 |
| A2 可成功同步的配置 | `not_run` | 本轮服务刻意返回 403，不能宣称目录可写或完整成功夹具已准备。 |
| A3／A6／A10 点击，A4 忙碌状态的独立观察 | `pass`（本轮失败路径） | 点击后禁用和文字可证 busy；这并不令 A5／A14 通过。 |
| A8／A9／A12 实际同步流程请求 | `pass`（本轮预检失败路径） | 已观察到正确端点的同轮真实请求，未验证后续词条／事件上传下载成功。完整有效配置主路径仍需另测。 |
| A5／A7／A11 指定加载组件，A14 运行期绑定 | `fail`（本轮失败路径） | 请求在运行、busy 已出现，但源码和运行树均缺实际 `LoadingProgress`。基线功能缺口已复现；成功主路径仍未测。 |
| A13 拒绝“只有 UI 没请求”的反例 | `not_run`（独立反例） | 当前基线实际有请求，不能用它证明测试已覆盖“无请求”反例。 |
| A16 失败结束恢复 | 部分证据，整体 `not_run` | 403 后按钮恢复可操作已实测；加载组件原本不存在，其“出现后消失”、更正配置后的真实重试均未测。 |
| A15 成功终态、A17 无数据、A18 重复／快速点击 | `not_run` | 未覆盖成功夹具、空增量、连续点击。 |
| B1—B15 其余边界与 U1—U6 策略 | 部分边界观察；其余 `not_run`／待用户判断 | 本轮仅实测 B10 中服务端 403 和正常导航；没有把探索覆盖冒充边界穷尽通过。 |

本轮结论为 **分析完成，基线缺少加载组件，整题未实现／未验收**。完整同步成功、认证成功服务的全链路、无数据、包装超时、断网、运行中返回／再入、重启、修改配置、快速连点均未验证。

## 9. 结束状态、完整性和操作限制

- 工程相关 269 个文件的前后指纹完全一致，清单 SHA-256 均为 `7ba986acc0d3c664565d1a3bc42846586cc44d757a3480980cffdbc48b149ff1`。证据：`traces/baseline-analysis/08-final-integrity.log` 和 `source-fingerprint-before.json`／`source-fingerprint-after.json`；Spec／metadata／HAP 哈希亦重新核对。业务代码、测试工程、依赖配置未改。
- 临时本地服务已停止，设备操作已释放。设备最终停在 WebDAV 配置分区的失败结果页；保存了本轮测试端点、目录和测试凭据，自动同步关闭。没有清应用数据，没有猜测或恢复不可读取的旧密码。再次使用本地夹具前须启动服务；后续验收须重新填写有效配置。
- **自动审批限制**：清理本轮端口映射的 `hdc fport rm tcp:18769 tcp:18769` 命令被自动审批拒绝，仅返回 `blocked by policy`。一次加引号的调用被 hdc 解析为含引号的不同规则而返回不存在，没有完成清理；未继续绕过。最终只读 `hdc fport ls` 仍见 `18769 → 18769 [Reverse]`、`9949 → 8012 [Forward]`、`9982 → 8012 [Forward]`；其中前者为本轮服务映射，后两者由本轮 Hypium 连接新增。原有 `9923 → 8012 [Forward]` 不属于本轮，不清理。服务已关闭但映射残留须记录，不宣称环境完全恢复。
- 两份请求的分析交付为 `spec/acceptance.md` 和本文件；调度、原始会话、截图、临时采集脚本、完整告警索引仅作为本地取证记录。不对外提交，不把 `not_run` 计为通过，不推断官方隐藏 F-point 或分值。

独立角色的完整命令／失败／纠正交接见 `workflow/verification/round-01-baseline-evidence.md`。其中保留了输入被键盘遮挡导致的一次采集失败及后续完成输入的证据；这些是测试前置问题，未通过修改业务代码或降低断言处理。
