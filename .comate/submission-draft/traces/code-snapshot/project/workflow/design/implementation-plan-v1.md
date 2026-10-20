# vg-spec13 实施方案 v1

CODEX_THREAD_ID：`01a143bb-a10f-7601-a510-405d234afe12`（方案角色直接读取环境变量）。

状态：已读取开发阶段需求复审 v1，供主 Agent 批准并交编码/验证执行。本文是设计，未宣称构建、设备或自测通过。本角色只写本文，不改生产代码、测试、workflow 状态，不运行构建或设备命令，不派生 Agent。

## 1. 输入、范围与决定

- 本题根为 `D:/HCUP/vg-spec13`；需求为 `spec/requirement.md`，SHA256 `ba156110d18109eecd2627ab66690b293da6cac504caef6650333a9a6e124677`；验收矩阵为 `spec/acceptance.md`，SHA256 `14a95fcf91b40bdc268b2a0552995cf91932067e00d66e17b876de57c9e7c770`。本角色重新计算两者一致。
- 已读 `spec/baseline-notes.md`、`spec-harness/1-do.md`、`spec/metadata.json`、本题有关源码及 `workflow/requirements/implementation-review-v1.md`；复审 SHA256 为 `b6f2c67c11425b087d654a286866c7e584b527f2a5d067d5054958041dabee06`。基线元数据为 `88db8789e28333c7b7dcc8db078f394a262b73c3`。
- 保留 A01–A16、D01–D07，按复审 R01–R10 和 B01–B28 执行。当前输入直接备份；既有校验、防重入、结构性空备份、重启加载已保存配置继续适用。方法、请求数、文件格式、固定展示时长、精确终态句不扩为 Spec 明文。
- 最小充分改动：新增**仅用于手动备份**的进程内控制器；页面渲染真实 `LoadingProgress` 和专属进行文字；手动备份直接等待真实 Promise；管理器只局部修正该备份入口的清理边界与局部配置/路径捕获；配置和冲突动作在备份期间锁定。其它同步操作维持既有流程。
- 不新增备份取消入口、busy 持久化、进程重启任务恢复、后台服务、调度框架或全体 WebDAV 操作的进度系统。离开页面只是撤下观察者，同进程真实备份继续；重入不重发，终结后允许新轮。

## 2. 本题代码证据与数据流

以下行号为阅读时基线，编码后重新定位。

| 位置 | 已确认事实 | 设计影响 |
| --- | --- | --- |
| `pages/SettingsPage.ets:149–168,190–196,447–462` | 页面初始化管理器并填充配置；WebDAV 分区按 `activeSectionId` 条件创建 | 沿原入口；分区销毁重建及退出设置重进均不能依赖子组件本地 busy |
| `pages/settings/SettingsSyncSection.ets:25–44,100–162` | 表单为父页 `@Link`；busy/result 为本地 `@State`；手动备份没有应用当前输入；UI race 为 120 秒且不取消底层 | 捕获当前表单、复用 `setSettings`；备份移除 race；保留实际任务所有者于组件外 |
| 同文件 `:339–396,429–443,533–624` | 现有字段校验未 trim 密码；无稳定 id、无 `LoadingProgress`；多个动作共享“处理中...” | 手动备份校验与经理既有 trim 判定等效；增加稳定 id；专属备份 busy 决定 spinner，不能拿其它动作 busy 冒充 |
| 同文件全文件 699 行 | 已超过本题 AGENTS 的组件文件 500 行上限 | 本轮受影响组件以外置 `@Builder` 提取现有表单/卡片渲染，目标各新增/修改组件文件 ≤500 行 |
| `sync/WebDavSyncManager.ets:107–174,911–1005` | status 可读；无进度订阅；设置缓存和持久化已存在；经理预检在 try 外；导出后任务参数再次读 `this.settings` | 控制器只管理手动备份状态；预检进入 try/finally；首个 await 前复制配置，预检后立即捕获最终备份路径 |
| `sync/WebDavSyncManager.ets:284–344,214–216` | 预检可能无网络；预检通过 manager 的 `remoteLayoutBase/Prefix` 决定上传路径 | 不强制每轮 HEAD；预检完成后保存局部路径，后续导出/加密/上传使用该路径 |
| `sync/webdav/WebDavSyncTask.ets:149–188` | 现成 TaskPool 任务加密后调用真实 `client.put` | 继续此真实链路，不另发无关探针代替上传 |
| 本题 `.setSettings(` 搜索 | 写配置的业务调用仅在 `SettingsSyncSection` 保存与测试连接两处；自动同步不调用它 | 备份期间锁住这两个入口及表单，重入后同样锁住，足以保持现有预检读取的经理配置稳定，无需推广所有 helper 接口 |
| `sync/AutoWebDavSyncManager.ets:32–90`、经理 `:672–688` | 自动同步使用已存配置、走其它备份方法；增量同步已有 SYNCING guard | 手动状态不绑定自动同步；测试隔离自动同步；不改自动同步调度或误计其请求 |

完成后的链路：原设置入口 → 当前表单构造 `WebDavSettings` 快照 → 手动控制器同步置忙并发布 → 校验/现有配置应用与保存 → 原 `backupToCloudInBackground()` → 原预检 → 原本地导出 → 原加密 TaskPool/兼容回退 → 原真实 WebDAV PUT → 经理 finally → 控制器 finally 发布终态。页面只观察控制器；不把生产请求迁到测试服务。

## 3. 文件范围、所有权与接口

生产改动由**编码角色统一拥有**。验证角色只拥有 `hypium_tests/test_*.py`、必要的本题测试 fixture 和验证日志；不得改生产流程来让测试过。方案角色只拥有本文。共享文件不得由多个角色并行改写，发现已有他人改动应适配，不回滚。

| 文件（均相对 `entry/src/main/ets/`） | 必要改动与边界 |
| --- | --- |
| 新 `sync/ManualWebDavBackupController.ets` | 手动备份单例、明确类型的状态快照与监听器、真实 Promise 所有权、输入复制/校验/应用、全路径终态。不持有组件或 AbilityContext，不持久化 busy |
| `pages/settings/SettingsSyncSection.ets` | 接入订阅/注销、当前输入捕获、aggregateBusy guard、真实 spinner/文案与 id；去掉手动备份用的 UI race 包装；保留其它动作现有超时流程 |
| 新 `pages/settings/SettingsWebDavBuilders.ets` | 平移现有输入/密码/开关及卡片的纯渲染 Builder；传显式类型的值与回调；保留标签、样式和回调意义。仅为目标组件降到 500 行以内，不引入新业务状态 |
| `sync/WebDavSyncManager.ets` | 改 `backupToCloudInBackground` 内部：复制设置、扩大 try/finally 覆盖预检及 yield、局部 backupPath、任务参数用快照；私有预检 helper 增加默认配置参数；保持原公开签名、真实上传及返回类型 |
| `pages/SettingsPage.ets` | 仅给原 WebDAV 入口和页内返回加稳定 id；不改变路由、初始化、持久化顺序或其它分区 |

外置 Builder 的精确分组由编码角色按可读性和编译结果确定：优先把现有六个 presentational Builder 连同必要的有名参数接口移入一个 ≤500 行文件；主组件保留动作方法和生命周期。不要只把 699 行拆成另一个超长组件，不为满足数字无关重排业务逻辑。`SettingsPage` 的既有超长状态不是本题扩展重构范围。

控制器最小接口（名称可在同义范围内调整并同步验证）：

- `getInstance(): ManualWebDavBackupController`。
- `getState(): ManualWebDavBackupState`：返回含 `runId: number`、`busy: boolean`、`resultText: string` 的独立状态快照；可加有名 phase 枚举用于内部可读性，不要求测试使用。
- `subscribe(listener: ManualWebDavBackupListener): void` 与 `unsubscribe(listener: ManualWebDavBackupListener): void`，监听类型为明确的 `(state: ManualWebDavBackupState) => void`；subscribe 立即交付当前快照，确保重入即时还原。
- `start(settings: WebDavSettings): Promise<void>`：**在首个 await 前完成 guard、复制输入、置 busy**。运行中再次 start 不执行配置保存、导出或网络，不排队。内部吸收预期失败与异常后发布终态，避免 UI `void start(...)` 产生未处理拒绝。
- 状态中不含密码、配置 JSON、AbilityContext 或组件。类字段声明/构造时初始化；Promise/监听器集合/可空引用均显式类型，不用 `any`、`unknown`、动态属性、`Object.freeze` 或通用动态事件总线。

经理公开方法保持 `backupToCloudInBackground(): Promise<WebDavSyncResult>`；私有 `preflightRemoteRoot(client, settings: WebDavSettings = this.settings)` 增加一个带默认值的配置参数，手动入口显式传快照，其它调用仍用原默认行为。`WebDavClient`、任务参数类型、TaskPool 任务及状态存储接口无需改动。

## 4. 真实异步状态机及不变式

| 当前状态 | 事件 | 动作 | 下一状态 |
| --- | --- | --- | --- |
| Idle/上轮终态 | 点击备份 | 同步 guard；复制点击时输入；递增 runId；发布 busy 和“正在备份到云端...” | Preparing |
| Preparing | 当前输入无效 | 不调用真实 WebDAV，不退回旧配置；记录失败 | 最终清理 → 终态 |
| Preparing | 其它经理操作正在运行 | 沿现有报忙/拒绝语义，不应用新设置、不抢占其 status | 最终清理 → 终态 |
| Preparing | 设置应用/保存成功 | 继续等待原备份 Promise；如保留渲染让步，放在同一 try 内 | Running |
| Preparing | 设置保存 false 或抛错 | 展示失败，禁止偷偷使用旧配置继续网络 | 最终清理 → 终态 |
| Running | 预检/导出/加密/上传仍 pending | busy 保持；不允许第二轮；页面在场时 spinner 和进行文字保持 | Running |
| Preparing/Running | 返回/切分区/后台 | 页面注销观察者；不取消、不重发、不改 busy | 原状态 |
| Preparing/Running | 同进程重入 | 新观察者立即读取本轮快照；恢复 busy、spinner、文字和禁用入口 | 原状态 |
| Running | 成功/返回失败/真实抛错 | 先等原 Promise 实际终结；记录成功或失败；经理与控制器 finally 清理 | 终态（busy=false） |
| 任意进程内状态 | 进程终止再重启 | 新单例空闲；按既有初始化加载已保存配置，不重放手动任务 | Idle |

必须维持：

1. 控制器 busy 表示这一轮尚未终结，不能由 120 秒 `Promise.race` 的拒绝清空；备份不走此 race。底层 HTTP 既有 15/20 秒期限仍可形成真实失败终结，不新增 UI 软超时。
2. 同一轮仅有一个真实备份任务。runId 只作进程内归属与防陈旧结果，不写入服务端数据或暴露测试后门；HTTP 多个目录请求不等于多轮任务。
3. 构造配置、同步上锁、发布忙碌在任何 await 之前；页面快速连点和控制器 guard 双重兜底。
4. `finally` 收尾涵盖配置应用/保存、渲染让步、预检、导出、加密、TaskPool 与网络的所有提前返回和抛错路径。经理只有在自己取得占用后才复位，拒绝其它占用的分支不得清掉别人的 status。
5. 监听器回调异常应隔离记录，不能打断真实操作或阻止清理。发布的是替换后的新状态，组件 `@State` 通过赋值同步，不直接改其嵌套对象。
6. promise 执行体只捕获纯 `WebDavSettings`、经理单例和控制器本身，不捕获页面 `this` 或 AbilityContext。组件调用后不保留一个在 await 完成时写已销毁 UI 的续体。

## 5. 配置、保存与经理最小调整

点击时按既有构造策略：endpoint/username trim；password/syncPassword 保留正文；remoteRoot trim，空白时默认 `/weiyu_sync`；沿既有 `requireRemoteRootExists=true`。控制器再复制为自己拥有的 `WebDavSettings`，不保存 `@Link` 的对象或返回自经理的可变引用。

校验必须等效经理 `requireConfigured`：endpoint、username、password 的 trim 结果非空，syncPassword 的 trim 长度至少 4。校验用 trim 不代表保存密码时修改正文。invalid 当前输入不能回落到旧合法配置；分别覆盖已存在旧配置和首次配置两种前置。

选择复用 `await manager.setSettings(snapshot)` 同时应用与尝试持久化；false/抛错作为本轮失败，不执行上传。不要把页面会改写 `webdavResult` 的 `saveWebDavSettings()` 闭包传入长生命周期控制器。`setSettings` 基线在 store 未就绪时会缓存并返回 true，控制器不能据此声称已经落盘；正常设置页初始化完成后自测重启加载成功，验证若发现未就绪竞态，再在本题初始化就绪边界作证据驱动调整，不先重构存储。Spec 不新增每次点击都必须持久化的独立要求。

配置固定采取“两层最小保证”：

- **页面层锁定**：`aggregateBusy = 本地其它动作 busy || 手动控制器 busy`。手动在途时所有五个输入、密码显隐/配置变更操作及保存/测试/立即同步/恢复均禁用；代码入口还必须 guard，不能只依赖按钮灰掉。分区/路由重入后锁仍由控制器恢复。自动同步开关不写 WebDavSettings，可维持既有能力，但测试必须隔离自动同步归因。
- **经理层捕获**：在手动备份入口首个 await 前用 `new WebDavSettings(...)` 复制经理配置；创建 client 与后续任务参数使用该复制值；`preflightRemoteRoot` 增加可选 `settings: WebDavSettings = this.settings`，手动链路传快照，其内部 key、remoteRoot、requireRemoteRootExists 都读参数；预检完成后立即把 `backupFilePath()` 存为局部常量，再 await 导出/加密。该小范围私有签名调整保持其它调用默认行为，不改造全部同步 helper。探针 helper 使用已经固定的 client/base/prefix，既有错误消息读取的根目录文字因 UI 配置锁也保持稳定；若实现传递同一 remoteRoot 给错误消息，保持可选默认即可。不要在 await 导出后又从 `this.settings` 读账号、密码、端点或根目录。

经理调整将 `this.status = SYNCING` 之后的 client 创建、预检、yield 和原导出上传主体放进同一个 try/catch/finally；预检失败 return 和直接抛错都必须经过 finally 复位 IDLE。校验或其它占用拒绝发生在取得占用前，不复位别人的任务。维持既有成功/失败 `WebDavSyncResult` 和真实上传实现。

以上 UI 锁仍为防冲突保证；预检显式快照补强本轮配置归属。若编码新增其它 setter/解锁编辑，须重新检查共享 remoteLayout 缓存会不会在预检与路径捕获之间被其它并行任务改写，不能只复制上传凭据便认为全部隔离。

## 6. 生命周期、渲染与稳定 id

`aboutToAppear` 注册一个保存为字段的监听器，订阅立即还原当前快照，再执行原自动同步配置加载；避免每次创建匿名函数导致无法移除。`aboutToDisappear` 用同一函数引用注销，并标记组件不可接收后续通知；不取消真实备份、不写 controller busy=false。若原配置加载存在页面销毁后回写，在其异步回写前同样检查挂载标记。无轮询定时器；保留的短渲染让步在任务内部管理。只由存活页面镜像状态，完成时无残留组件引用。

手动操作卡片里，备份按钮附近加入 `LoadingProgress`（建议 20–24vp）及专属 Text；spinner 的条件只看手动备份 busy。进行文字沿用“正在备份到云端...”，终结切到本轮结果或空闲，不能残留进行语义。采用 existing state 赋值驱动 Builder 更新；全局 Builder 不保存 state。滚动到备份按钮时 spinner/文字应处于同一可见卡片区域，不为测试另造页面或全屏遮罩。不增加固定最短展示延时。

| 目标 | 最终约定 id |
| --- | --- |
| 原设置目录 WebDAV 行 | `webdav_settings_entry` |
| 目标分区根容器 | `webdav_settings_section` |
| 五输入 | `webdav_endpoint_input`、`webdav_username_input`、`webdav_password_input`、`webdav_sync_password_input`、`webdav_remote_root_input` |
| 立即备份按钮 | `webdav_backup_button` |
| 真实 ArkUI LoadingProgress | `webdav_backup_loading` |
| 专属备份进行/结果 Text | `webdav_backup_status` |
| 保存/测试/同步/恢复 | `webdav_save_button`、`webdav_test_button`、`webdav_sync_button`、`webdav_restore_button` |
| 原配置结果 Text | `webdav_config_result` |
| 原页内返回 | `settings_back_button` |

id 直接赋给目标原生节点，条件渲染不可生成同屏重复 id。`webdav_backup_status` 显示控制器本轮结果；恢复旧结果如需继续共用区域，可在手动备份无存活时沿既有显示，但不能触发手动 spinner 或被当作本轮网络证据。id 原名与验收矩阵 T1–T9 一致，验证脚本可以据此准备。

## 7. 实现顺序与验证映射

实现顺序：①有名状态/监听类型及手动控制器，确定同步 guard 与无 UI 引用；②经理手动入口 finally/局部快照；③组件订阅、输入捕获、禁用/入口 guard、真实 spinner；④纯 Builder 提取以满足行数和稳定 id；⑤构建及验证按下表。只有真实失败或新证据才扩大改动，不预先改网络/加密/数据库。

所有以下均为**待执行**；编码/验证先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1` 再构建/设备命令。使用本题刚构建的 HAP，每轮自测前先安装，并留 build/install/Hypium/服务端时间线。不要使用别题 HAP。Hypium 按本题 `1-do.md` 继承公共 `HarnessTestCase`；公共目录只读。

| 计划测试组 | 需求覆盖 | 实测要点与证据 |
| --- | --- | --- |
| V01 原入口及直接输入慢速成功 | R01–R06；A01–A16；B17/B27 | 先存 A，改填 B 后直接点备份，期间不保存/测试/同步；只有 B 收到本轮请求。受控合法响应延迟，至少两次采样真实 LoadingProgress 类型、可见区域、进行文字；服务端 pending 与点击/采样使用同一主机时间线，成功有真实加密备份 PUT 强证据 |
| V02 终态与重复 | R07–R09；D01/D04–D07；B11–B13/B28 | 放行响应后 spinner/进行文字退出且按钮可用；再点产生新轮新请求；在途连点/首帧连点最多一个新备份任务；快速成功记录真实时间线，不强制最短毫秒数 |
| V03 输入边界 | R02/R07；B01–B07/B17 | 每字段独立空/空格、密码空白、同步密码 0/1/3/4、默认目录、部分/全空；旧 A 配置和首次配置分别测；invalid 无本轮 WebDAV 请求且终结可操作；不偷偷用 A；默认目录分支按有效配置验证 |
| V04 无数据/首次云目录 | R06/R09；B14–B16 | 沿结构性空数据真实上传；云端无旧备份仍可首次写入；滚动到手动卡片后指示与文字可见；表单分页末页登记不适用 |
| V05 返回/重入/重启 | R07/R08/R10；B08–B10/B24–B25 | 无点击离开无手动请求；在途页内返回、退出设置/系统返回后重入恢复同轮 busy+spinner+文字且不重发；后台不新增备份；成功/失败后重入可新轮；终态重启读取已存配置；在途杀进程重启空闲且不重放。无备份取消入口，B09 登记不适用 |
| V06 失败/真实超时 | R07/R08；D02/D03；B18–B23 | 可控上传非2xx、拒连/离线、401/403/404/409/5xx及真实 HTTP 超时按独立样本；pending 时继续显示，底层真实终结后清理并可重试。预检失败/异常需证明经理不残留占用。移除备份 UI race 后旧120秒软超时分叉登记不适用，不以新假定时器模拟通过 |
| V07 配置与动作冲突 | R02/R08/R09；B26 | 在途尝试编辑字段、保存、测试、同步、恢复，确认锁定且本轮配置不改；其它经理占用时手动备份拒绝，不抢占，不用其请求计 A13；自动同步关闭/独立归因 |
| V08 静态与构建回归 | 工程约束及全部入口 | 新/改组件≤500行，无 any/unknown/动态特性；订阅成对、无组件/Context捕获、手动链路不进race、所有返回经过清理；构建无新增告警；原配置/恢复入口能进入，测试 fixture 与数据不入生产 |

B18/B19 某些导出/加密/TaskPool 异常若缺少可控注入手段，以静态覆盖及明确 `not_run` 登记，不能为了造证据添加生产后门或把未测写通过；受控 fixture 能覆盖的网络失败必须实际测。保留真实 `HEAD`/探针/父目录/备份请求日志，按链路和备份文件归组，不断言固定请求数。记录方法、路径、到达/完成、长度/密文摘要/认证匹配即可，不打印明文密码或认证头。

## 8. 权衡、回退与未解决项

- 采用轻量进程内控制器是覆盖“分区/路由销毁重建后仍在途”的必要最小增量；仅把本地 busy 改到父页不能覆盖退出设置路由，永久 AppStorage busy 又会造成重启假忙。单例只保留手动任务与可移除观察者，终态不含敏感配置。
- 局部经理修正是必要的：只移 UI race 仍不能让预检直接抛错复位经理；只加 finally 仍不能防导出后再读取变更配置。锁定唯一配置写入口加局部快照、一个默认预检参数，比重构全部预检/同步接口范围小。
- 其它操作依然保留基线超时与恢复流程，本题不推广其进度状态；如果独立实测证明其会在手动备份窗口改写配置/占用，回退到方案角色按具体调用点做最小补充，不先全局重写。
- 若 spinner 有 id 但 UI 树类型/可见区域不成立，是实现/布局偏离，先修目标卡片；若重入丢 busy，是订阅/状态所有权偏离，先修 controller↔component；若真实 PUT 从 B 跑到 A，是配置捕获/预检快照/锁定偏离；若本方案锁定前提被代码扩展破坏，属于方案前提失效，须按新增并行调用点最小隔离布局缓存。
- 技术依据：读取 `C:/Users/22580/.codex/skills/arkts-syntax-assistant/SKILL.md` 及 `references/en/typescript-to-arkts-migration-guide.md`（静态类型/有名接口、禁止 any/unknown、动态属性）；读取 `C:/Users/22580/.codex/skills/hmos-arkts-knowledge-retriever/SKILL.md`、`docs/ArkTS-Language-Guide/Concurrency/async-concurrency-overview.md`（Promise 状态、await 和 finally）、`Basic-Syntax/classes.md`（有名类、字段/构造初始化）。检索脚本因该技能副本缺 `references/doc_index.json` 失败，已改读现存原文；未运行安装或修改技能。ArkUI 具体 Builder/生命周期沿本题代码和 AGENTS，最终由编译与设备证明；不假称技能含已核对的 ArkUI API 条目。
- 未访问上游、其它题、题包或初始化总览会话；没有外部网络来源。无须用户决策的阻断项。剩余均为编码和实测事项，尤需实际证明未保存 B 输入、真实 pending 窗口、两种页面重入及经理失败收敛。
