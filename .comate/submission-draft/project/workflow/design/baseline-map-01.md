# vg-spec8 静态基线映射 01

## 记录范围与证据口径

- 版本：`baseline-map-01`，本轮仅执行 `spec-harness/0-analyze.md` 的只读代码映射。此文是主 Agent 汇总 `spec/baseline-notes.md` 的中间证据，不是功能方案，也不替代构建、安装和设备操作证据。
- 基线：`spec/metadata.json:2` 指定 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`；本轮只读执行 `git rev-parse HEAD` 得到相同值。未读取 Git 历史、上游仓库、题包、其他题工程或 `agent-system` 历史。
- 输入哈希实读匹配派工：`spec/requirement.md` SHA-256 为 `256038a2336dce8956585ff92c18e7ec9e5cd79d736f7b7f56021dbf646af592`；`spec/metadata.json` SHA-256 为 `92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。
- 原生环境实读：`CODEX_SESSION_ID=01a144eb-32eb-7cb3-b4d6-daea0ae599b7`；`CODEX_THREAD_ID=01a144ec-c5a6-7ce3-9feb-43490f2b2fed`。二者按环境原值记录，不互相替代。
- 下文 `SPEC_EXPLICIT` 表示需求明文，`CODE_EVIDENCE` 表示本题源码静态实证，`INFERENCE` 表示由调用顺序推导的风险或前置条件。没有运行构建、安装、设备、服务端或网络请求；所有设备可达性和运行表现均为**未验证**。
- 不涉及 ArkTS 非 UI API 的外部事实判断；仅追踪源码中的 API 调用，未查询公开技术资料，未使用其他项目代码作参考。

## 核心差异

| 类型 | 结论 | 证据 |
| --- | --- | --- |
| SPEC_EXPLICIT | 点击「从云端恢复」应先打开第一层确认弹窗；「取消」关闭后仍可再次打开；未明确点击「继续」前不得产生任何 WebDAV 请求。 | `spec/requirement.md:7`、`:20`、`:33`、`:37-40` |
| CODE_EVIDENCE | 基线恢复按钮直接执行 busy 包装，再执行下载；仅下载成功、内容非空、预览成功后才调用原生弹窗。该弹窗按钮为「取消」「确认恢复」，没有「继续」。恢复链中没有独立的第一层确认。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:507-516`、`:164-165`、`:140-156`、`:199-222` |
| CODE_EVIDENCE | 已有预览弹窗的取消分支会返回 `WebDavSyncResult.ok('已取消恢复')`，其异常分支也返回同样结果；包装器在 `finally` 中将 `webdavBusy` 还原为 `false`。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:224-230`、`:148-156` |
| INFERENCE | 代码支持“现有预览取消会结束本次包装操作”的判断，但不能据代码认定实际原生弹窗已关闭或按钮已经恢复；更不能把缺失的第一层弹窗推定成“自建 Promise 未 resolve”的现成缺陷。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:215-230`、`:148-156`；原生运行未验证 |

## 实际入口与静态路由链

| 步骤 | CODE_EVIDENCE | 文件与行号 |
| --- | --- | --- |
| 应用入口 | `module.mainElement` 为 `EntryAbility`，`srcEntry` 指向 `./ets/entryability/EntryAbility.ets`。 | `entry/src/main/module.json5:6`、`:29-32` |
| 首屏路由 | `onWindowStageCreate` 调用 `windowStage.loadContent('pages/Index', ...)`。Index 是 `@Entry @Component`。 | `entry/src/main/ets/entryability/EntryAbility.ets:23-41`；`entry/src/main/ets/pages/Index.ets:28-30` |
| 首屏设置入口 | Index 的 `TopNavigation` 接收 `onSettingsClick: () => router.pushUrl({ url: 'pages/SettingsPage' })`；齿轮 `Text('⚙')` 所在 Column 的点击调用该回调。 | `entry/src/main/ets/pages/Index.ets:320-329`；`entry/src/main/ets/pages/index/components/TopNavigation.ets:69-79` |
| 注册的设置页面 | `pages/SettingsPage` 注册在 `main_pages.json`；源码为 `@Entry @Component struct SettingsPage`。 | `entry/src/main/resources/base/profile/main_pages.json:7`；`entry/src/main/ets/pages/SettingsPage.ets:54-56` |
| 设置内 WebDAV 入口 | 设置项目数据中 `id: 'sync'` 的标题为「WebDAV 配置」。普通项目点击只赋值 `activeSectionId = item.id`；只有 `logger` 分支 push 路由。 | `entry/src/main/ets/pages/SettingsPage.ets:35-43`、`:507-512` |
| 显示 WebDAV 操作区 | `activeSectionId` 初始为空；为空显示设置列表，否则执行 `buildSectionContent()`；当值为 `'sync'` 时实例化 `SettingsSyncSection`。 | `entry/src/main/ets/pages/SettingsPage.ets:132`、`:483-525`、`:427-442` |
| 返回层级 | 设置页头部「←」调用 `handleHeaderBack()`；分区内只清空 `activeSectionId`；设置列表层保存普通设置后 `router.back()`。 | `entry/src/main/ets/pages/SettingsPage.ets:172-179`、`:464-467` |

**静态结论**：本题目标是 `pages/SettingsPage` 内部的 WebDAV 配置分区。设置列表项的 `sync` 是数据标识和分区状态，不是单独页面路由，也不是 `Tabs/TabContent`。Index 的当前布局是 TopNavigation 加 Scroll/HomeTabContent，不能仅因组件名包含 `Tab` 而称为底部设置标签。证据：`entry/src/main/ets/pages/Index.ets:320-334`；`entry/src/main/ets/pages/SettingsPage.ets:427-442`、`:483-525`；注册清单 `entry/src/main/resources/base/profile/main_pages.json:2-17`。

**入口前置风险（INFERENCE，设备未验证）**：首次运行可能先显示隐私同意层，或在已同意隐私且未看引导时 push `pages/OnboardingPage`。代码门槛分别为 `checkPrivacyConsent()` 和 `maybeShowOnboarding()`；不能直接声称启动后齿轮立即可点。证据：`entry/src/main/ets/pages/Index.ets:66-72`、`:116-137`、`:285-299`、`:339-355`。

## 组件、状态与数据流

| 所有者 | 已有状态/职责 | 证据 |
| --- | --- | --- |
| SettingsPage | WebDAV endpoint、username、password、syncPassword、remoteRoot、密码显隐，以及自动同步开关/间隔/最近结果均为页面 `@State`；持有管理器和状态存储单例。 | `entry/src/main/ets/pages/SettingsPage.ets:114-129` |
| SettingsPage → SettingsSyncSection | 以上字段通过 `$webdav...` 传入子组件 `@Link`，父子共享当前配置输入；子组件自己的 `webdavResult`、`webdavBackupResult`、`webdavBusy` 是局部 `@State`。 | `entry/src/main/ets/pages/SettingsPage.ets:427-442`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:23-47` |
| SettingsSyncSection | `build()` 顺序构建「基础配置」「自动同步」「手动操作」；恢复属于手动操作卡片，与立即备份同行。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:344-357`、`:371-380`、`:435-443`、`:496-516`、`:587-594` |
| SettingsSyncDialog | 它是设置页用于 JSON 数据展示/粘贴导入的独立覆盖层，`visible/title/message/data/isImport` 由 `@Link` 控制；遮罩、关闭、取消将 `visible=false`。它不是 WebDAV 恢复调用链中的 `promptAction.showDialog`。 | `entry/src/main/ets/pages/SettingsPage.ets:347-352`、`:444-448`、`:540-546`；`entry/src/main/ets/pages/settings/SettingsSyncDialog.ets:7-17`、`:35-46`、`:93-102`、`:118-126`；恢复实际调用 `SettingsSyncSection.ets:215` |
| WebDavSyncManager | 单例维护配置、manifest、远端布局缓存和状态；下载流程将管理器状态设为 RESTORING，再按结果设为 IDLE/ERROR。此状态不同于组件 `webdavBusy`。 | `entry/src/main/ets/sync/WebDavSyncManager.ets:75-100`、`:107-121`、`:471-498`；状态枚举 `entry/src/main/ets/sync/webdav/WebDavCommon.ets:3-8` |

### 基线恢复状态顺序（静态，不代表设备实测）

```text
可用按钮：webdavBusy=false
  --点击「从云端恢复」 [SettingsSyncSection.ets:507-516]-->
webdavRestore() [164-165]
  --> runWebDavBackupAction() [140-148]
      busy=true；结果=「正在处理...」；等待 50 ms
  --> runWithTimeout(fn, 120000) [113-121, 148]
  --> webdavRestoreWithPreview() [199-206]
      先 downloadBackupPlain(false)；再检查成功、明文非空、previewImport 无错误
  --> 原生预览确认 [215-222]（等待期间 busy 仍为 true）
      ├─ index===0：返回 ok('已取消恢复') [224-226]
      ├─ 弹窗/后续 try 内 reject：返回 ok('已取消恢复') [229-230]
      └─ 非 0 返回值：importPlainBackup(download.plain) [228]
  --> 包装器写结果并 toast，或写异常结果 [149-154]
  --> finally busy=false [155-156]
```

- **CODE_EVIDENCE**：五类手动操作按钮都绑定同一个 `webdavBusy`，忙时文本统一变成「处理中...」，且 `.enabled(!this.webdavBusy)`；恢复自身也有包装器的 busy guard。证据：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:141-143`、`:446-465`、`:481-489`、`:497-516`。
- **CODE_EVIDENCE**：当前恢复流程中没有自建“确认 Promise”的 resolver/callback；只有直接 `await promptAction.showDialog` 后按 index 分支。代码没有保存原生弹窗 controller 或 visible 状态。证据：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199-232`。
- **INFERENCE**：若原生弹窗按预期返回 index 0，取消会沿返回值收敛到 finally，因此应恢复按钮可用；快速重复点击在 busy 期间有 UI 禁用和函数 guard 两层阻断。实际弹窗关闭时机、触摸连击表现、原生返回值需设备证据。依据同上和 `SettingsSyncSection.ets:141`、`:514-516`。
- **CODE_EVIDENCE / INFERENCE**：`Promise.race` 的 120 秒窗口包住下载、预览和等待弹窗的全部过程；超时 promise 的定时器没有保存句柄或清除，亦未传递取消信号给操作。因而超时只是先让包装器返回，代码没有显式取消未结束的原操作或原生弹窗；是否发生晚到结果为未验证风险，不能作为已复现缺陷。证据：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:113-121`、`:140-156`、`:199-232`。

## 请求起点和网络调用链

### 恢复入口的实际链路

| 顺序 | CODE_EVIDENCE | 文件与行号 |
| --- | --- | --- |
| 0 | 组件直接调用 `webdavManager.downloadBackupPlain(false)`，在任何恢复确认之前。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199-200` |
| 1 | 管理器先 `requireConfigured()`；endpoint 空、账号/密码空、syncPassword trim 后不足 4 位均提前返回，不创建请求。 | `entry/src/main/ets/sync/WebDavSyncManager.ets:160-170`、`:471-473` |
| 2 | 通过 `createClient()` 创建 WebDavClient，并执行 `preflightRemoteRoot()`。 | `entry/src/main/ets/sync/WebDavSyncManager.ets:173-178`、`:475-484` |
| 3 | 远端布局缓存命中可跳过 preflight 请求；remoteRoot 为 `/` 也可跳过。其他情况先 `client.head(remoteRoot)`；404 时可创建 `.keep` 并复查；再可能探测 PUT/DELETE。 | `entry/src/main/ets/sync/WebDavSyncManager.ets:280-339`、`:345-364`、`:241-246`、`:259-264` |
| 4 | 备份管理器 `downloadBackupPlain` 因 `force=false` 先 HEAD 目标备份；404 时再 HEAD 旧路径；根据冲突检查可能提前返回。 | `entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:68-94`；`entry/src/main/ets/sync/WebDavConflictResolver.ets:10-28` |
| 5 | 继续下载前先导出本地 snapshot 并尝试持久化，然后 `client.get(targetFile)`，成功后解密得到 plain。 | `entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:96-117` |
| 6 | `WebDavClient.head/get` → 私有 `request` → `requestWithRedirect` → `http.createHttp()` → `await request.request(url, options)`；这里是实际网络 API 调用点。 | `entry/src/main/ets/sync/webdav/WebDavClient.ets:33-38`、`:109-123`、`:136-146` |
| 7 | 下载和本地 `previewImport` 成功后才显示已有预览弹窗；确认恢复后才 `importPlainBackup` → `DataSyncManager.importData`。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:200-228`；`entry/src/main/ets/sync/WebDavSyncManager.ets:502-506`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:174-185` |

**请求范围（CODE_EVIDENCE）**：取消前可能已有 HEAD、GET，目录处理和探测分支还可能 PUT/DELETE，因此场景三的“任何 WebDAV 请求”不能只统计备份 GET。`mkcol()` 当前实际调用的是 PUT `.keep`，不能按方法名误记成 HTTP MKCOL。证据：`entry/src/main/ets/sync/WebDavSyncManager.ets:280-339`、`:345-364`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:79-101`；`entry/src/main/ets/sync/webdav/WebDavClient.ets:78-82`。

**可提前结束而无弹窗的分支（CODE_EVIDENCE）**：配置不完整、preflight 失败、远端无备份、远端未更新、下载/解密失败、明文为空或 previewImport 失败都可在 `showDialog` 之前返回。证据：`entry/src/main/ets/sync/WebDavSyncManager.ets:471-498`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:78-117`；`entry/src/main/ets/sync/WebDavConflictResolver.ets:15-25`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:201-208`。

**数据影响（CODE_EVIDENCE）**：已有预览取消分支不会调用 `importPlainBackup`；但此前的下载路径可写本地 snapshot，因此不能把“取消”泛化为“此前没有网络、没有任何本地写入”。预览本身解析 JSON 并查询本地单词来统计新增/更新。证据：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:224-228`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:96-98`；`entry/src/main/ets/sync/DataSyncManager.ets:351-380`。

**路径与客户端（CODE_EVIDENCE）**：目标备份路径由远端布局和 `BACKUP_FILE_NAME` 组合；旧路径由 remoteRoot + `data` + 文件名组合；客户端将 endpoint 尾部斜杠移除，拼接路径，使用 Basic Authorization，连接/读取超时分别为 15/20 秒，并最多处理两次重定向。证据：`entry/src/main/ets/sync/WebDavSyncManager.ets:181-215`；`entry/src/main/ets/sync/webdav/WebDavClient.ets:25-30`、`:85-92`、`:109-111`、`:127-146`、`:164-180`。这些只记录当前写法，不作外部 API 兼容性判断。

## 设置存储和重进相关基线

| CODE_EVIDENCE | 文件与行号 |
| --- | --- |
| 设置页出现后，初始化普通设置、WebDAV 管理器和状态存储，再把管理器配置赋值给页面状态；组件出现时还会读取自动同步设置。 | `entry/src/main/ets/pages/SettingsPage.ets:149-168`、`:190-208`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:53-76` |
| WebDAV 输入通过 TextInput 的 onChange 只改当前 `@Link` 值；「保存设置」构造 `WebDavSettings`，endpoint/username/remoteRoot trim，remoteRoot 空白时使用 `/weiyu_sync`，并设置 requireRemoteRootExists=true。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:99-110`、`:262-277`、`:293-301`、`:353-357`、`:446-454` |
| `WebDavSyncManager.setSettings()` 先替换内存配置、规范化根路径、清空布局缓存，再保存 JSON；store 未 ready 时只缓存且返回 true。initialize 从持久化设置、manifest、snapshot 恢复。 | `entry/src/main/ets/sync/WebDavSyncManager.ets:111-157` |
| `WebDavSettings` 包含 endpoint、username、password、syncPassword、remoteRoot、requireRemoteRootExists，toJSON 将这些字段序列化。 | `entry/src/main/ets/sync/webdav/WebDavCommon.ets:49-98` |
| 存储后端为 Preferences `webdav_state_store`；配置主/备份键为 `webdav_settings_json`、`webdav_settings_json_bak`，另有备份时间；有效备份可回填损坏主项，写入同时更新主、备份、时间并 flush。 | `entry/src/main/ets/utils/WebDavStateStore.ets:62-81`、`:120-131`、`:146-151`、`:261-300` |
| 自动同步设置有单独键，开关/间隔/上传选项变化立即调用存储；默认自动同步开、间隔 6 小时、上传模型开、全量备份关。 | `entry/src/main/ets/utils/WebDavStateStore.ets:84-90`、`:170-213`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:79-84`、`:380-400`、`:409-418` |
| 恢复没有先保存当前输入；它使用管理器已持有的配置。立即同步会先 saveWebDavSettings，测试连接会 setSettings，均与恢复不同。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:164-165`、`:177-187`、`:199-200`、`:234-249` |
| 设置页销毁时保存的是普通 AppSettings/API key；该方法的字段清单不含 WebDAV。不能依靠这条自动保存路径证明 WebDAV 输入已持久化。 | `entry/src/main/ets/pages/SettingsPage.ets:159-160`、`:300-324` |

**INFERENCE**：为解释基线实际已有预览弹窗，必须区分“页面已填但尚未保存”和“管理器已有完整配置”；页面上可见值不必等于恢复实际采用值。重启后的状态还依赖 Preferences 初始化成功，不能仅凭 UI 输入认定已保存。依据 `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:99-110`、`:164-165`、`:199-200`；`entry/src/main/ets/sync/WebDavSyncManager.ets:111-157`。

## 自动同步的独立请求来源

- **CODE_EVIDENCE**：Ability 每次进入前台均异步 initialize 自动同步管理器，再 `tryRun('foreground')`。自动同步有自己的 `busy`，不读取 SettingsSyncSection 的 `webdavBusy`。证据：`entry/src/main/ets/entryability/EntryAbility.ets:49-57`；`entry/src/main/ets/sync/AutoWebDavSyncManager.ets:7-10`、`:21-37`；组件 busy 位于 `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:43`。
- **CODE_EVIDENCE**：`tryRun` 依次检查 context、endpoint/username、自动同步开关、距上次运行间隔；满足后先记录 lastRun/清错误，再执行 `syncIncremental()`，成功后可按开关额外 `backupToCloud()`。证据：`entry/src/main/ets/sync/AutoWebDavSyncManager.ets:28-85`。
- **CODE_EVIDENCE**：增量同步本身可能先 preflight；随后在 TaskPool 运行 executeDownload 等任务，这些任务也使用 WebDavClient 的 GET。恢复预览下载链没有经过这个 executeDownload 任务入口。证据：`entry/src/main/ets/sync/WebDavSyncManager.ets:668-705`；`entry/src/main/ets/sync/webdav/WebDavSyncTask.ets:131-137`；恢复链见 `entry/src/main/ets/sync/WebDavSyncManager.ets:471-491`。
- **INFERENCE**：场景三观测到的服务端请求可能来自独立前台自动同步；配置为空时两条链可均提前结束，得到“零请求”也不能证明目标取消流程正确。验证证据需包含自动同步开关、观察窗口和请求路径/方法。本轮未操作开关、未发请求。依据 `entry/src/main/ets/sync/AutoWebDavSyncManager.ets:28-65`；`entry/src/main/ets/sync/WebDavSyncManager.ets:160-170`、`:471-478`。

## 相似的既有交互（仅定位）

| CODE_EVIDENCE | 可能提供的本题内参考 | 文件与行号 |
| --- | --- | --- |
| 本地备份导入预览 | 直接 await 原生 showDialog；index 0 写「已取消导入」并返回；catch 也归取消；外层 importData finally 复位 importing。与当前恢复预览结构相近。 | `entry/src/main/ets/pages/settings/SettingsBackupSection.ets:109-149`、`:152-191` |
| 粘贴 JSON 的设置弹层 | `@Link visible` 显式控制遮罩和取消关闭，且不持有确认 Promise。用途为数据导入/展示。 | `entry/src/main/ets/pages/settings/SettingsSyncDialog.ets:7-17`、`:35-46`、`:118-126` |
| 设置页导入预览 | 原生 `showDialog` 返回 index 0 就 return，非取消后才 importData。 | `entry/src/main/ets/pages/SettingsPage.ets:355-380` |
| 首页 API 未配置确认 | 已有按钮文字「继续」属于开始学习时的 API 未配置提示，与 WebDAV 恢复无关，不能据此认定恢复已有第一层确认。 | `entry/src/main/ets/pages/index/HomeTabContent.ets:419-432` |

## 缺失能力与稳定选择器风险

| 关联需求/对象 | 基线实证与缺口 | 证据 |
| --- | --- | --- |
| 场景一：第一层确认及取消 | 无请求前第一层确认，亦无该层对应的「取消」「继续」处理；现有的是网络之后的预览确认。现存原生取消是否实际关闭，需设备实测。 | `spec/requirement.md:7-14`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:164-165`、`:199-230` |
| 场景二：取消后再次打开 | 外层 finally 和 enabled 绑定提供现存预览流程的恢复通路，但缺失第一层，因此不能报告 Spec 场景已满足。 | `spec/requirement.md:20-27`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:140-156`、`:507-516` |
| 场景三：未「继续」零请求 | 无前置同意门槛；配置有效且路径可继续时，进入确认前已调用 WebDAV 请求；无网络确认阶段这一能力缺失。 | `spec/requirement.md:33-40`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199-215`；`entry/src/main/ets/sync/WebDavSyncManager.ets:471-484`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:79-101` |
| 齿轮入口 | Text/Column 没有 `.id()`。组件有可见「⚙」，需设备确认可访问树呈现和定位。 | `entry/src/main/ets/pages/index/components/TopNavigation.ets:69-79` |
| WebDAV 配置列表项 | `item.id='sync'` 只是数据字段与 ForEach key，不是组件 id；列表行没有 `.id()`。进入后页头和列表均会使用标题文本，选择器应考虑当前层级。 | `entry/src/main/ets/pages/SettingsPage.ets:40`、`:469-473`、`:487-517` |
| 配置输入/自动同步开关 | 输入、密码输入、Toggle、Select 均无稳定 id；两组密码操作的「显示／隐藏」重复，单靠文字可能歧义。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:262-310`、`:319-336`、`:353-357`、`:393-400` |
| 恢复按钮/处理状态/结果 | 恢复、备份、保存、测试、同步按钮及结果 Text 均无 `.id()`；busy 时多个按钮都显示「处理中...」，恢复按钮文字会消失。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:446-525` |
| 既有原生确认弹窗 | `showDialog` options 只给 title/message/buttons，恢复调用没有组件 id；「取消」也在其他对话框中复用。未核验原生弹窗可访问树。 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:215-222`；`entry/src/main/ets/pages/settings/SettingsSyncDialog.ets:118-126`；`entry/src/main/ets/pages/settings/SettingsBackupSection.ets:164-169` |
| 页面根 | 当前只见 `settings_ + themeRefreshToken` 和 `index_ + themeRefreshToken` 根 id，后缀随主题 token 变化；无法替代目标控件的稳定 id。 | `entry/src/main/ets/pages/SettingsPage.ets:549`；`entry/src/main/ets/pages/Index.ets:360` |

以上 id 缺口是分析事实；若验收需要稳定选择器，则基线属于“需在实现时补 `.id()`”，本轮没有为控件指定新 id、添加实现或作接口承诺。

## 尚未验证或需交主 Agent 复审

1. **设备入口与当前表现未验证**：首启隐私/引导、实际齿轮位置、设置分区和滚动、恢复弹窗是否可达、取消是否关闭及恢复 enabled。代码只提供候选操作链，实际证据由验证角色采集。静态依据：`entry/src/main/ets/pages/Index.ets:116-137`、`:285-299`、`:320-355`；`entry/src/main/ets/pages/SettingsPage.ets:427-442`、`:483-525`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199-230`、`:507-516`。
2. **运行前置环境未验证（INFERENCE）**：基线现有预览要求管理器配置完整、服务端与备份 HEAD/GET 可继续、同步密码能解密且 JSON 预览有效；无账号/服务端/有效备份时未必能走到弹窗。首层无请求确认按 Spec 不应依赖这些下载前置条件，但这属于需求与基线差异，交主 Agent 汇总。依据 `entry/src/main/ets/sync/WebDavSyncManager.ets:160-170`、`:471-498`；`entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:78-117`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:201-208`。
3. **Spec 与基线阶段名称不同**：Spec 明文是“第一层”和「继续」，基线只见下载后的「确认恢复」。不能把现有预览改称 Spec 第一层而掩盖请求顺序差异；需求边界交需求角色/主 Agent 复审。证据：`spec/requirement.md:7`、`:33`；`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199-228`。
4. **构建/告警/安装/服务端计数无本角色证据**：没有运行这些动作，不能以此文给出通过/失败结论；本轮只确认静态 HEAD 与输入哈希，未修改生产代码、测试、state/events 或其他产物。

