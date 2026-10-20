# vg-spec13 未修改基线实测记录

记录日期：2026-10-16。范围：`spec-harness/0-analyze.md` 分析阶段，未修改业务代码、测试或构建配置。以下 `pass` / `fail` 是本地基线观察，不是官方成绩，也不是整题完成结论。

证据标记：`SPEC_EXPLICIT` 为本题 Spec 明文；`CODE_OBSERVED` 为本题当前源码实证；`RUNTIME_OBSERVED` 为本次设备、服务端或构建实测；`INFERENCE` 为推断；`NOT_VERIFIED` 为未验证。源码行号均对应下述 HEAD；日志行号对应本次保留的原始文件。

## 1. 基线快照、会话与源码完整性

- HEAD / `base_commit`：`88db8789e28333c7b7dcc8db078f394a262b73c3`，与 [metadata.json](metadata.json:2) 一致；没有额外打 tag。
- 验证角色：`/root/baseline`，实际 `CODEX_THREAD_ID=01a1438c-70c8-72b2-b340-732acfb87cb4`。进程环境的 `CODEX_SESSION_ID=01a1438a-e703-72b1-8078-9425872e0989` 继承主会话，不能代替子会话 ID。记录见 [build-meta.json](../logs/baseline-20261016/build-meta.json:1)。
- `RUNTIME_OBSERVED`：本次构建前后各计算 296 个 tracked 文件 SHA-256，完全相同，并与主 Agent 的 `workflow/analysis-start-code-fingerprint.json` 一致；[fingerprint-check.json](../logs/baseline-20261016/fingerprint-check.json:1) 中 `changed_files=[]`。前后原始清单分别为 [source-before.json](../logs/baseline-20261016/source-before.json:1)、[source-after.json](../logs/baseline-20261016/source-after.json:1)，两个清单文件 SHA-256 均为 `c29416207194f1bb1bcdf3d516a7c4c2645c4abd024c152bb1657412cf092334`。
- 构建与设备操作由本角色独占；操作前进程枚举仅见 hdc 服务，没有 Python/Hypium 自动测试进程，没有发现本题日志内占用锁。主 Agent 已协调本会话其他角色不操作设备、不改源码。`git diff --name-only` 仅为初始化已有 `AGENTS.md` 修改；没有回滚他人记录。
- 构建工具生成/刷新 `entry/build/`、`.hvigor/`；清单见 [generated-files.json](../logs/baseline-20261016/generated-files.json:1)。Hypium 生成的报告保留于本次日志目录。未将生成物当作源码修改；工作区状态见 [git-status-after.txt](../logs/baseline-20261016/git-status-after.txt:1)。本角色新增内容仅本文件及 `logs/baseline-20261016/` 原始证据、临时观察脚本。

## 2. 本次构建、安装、启动及完整告警索引

每个 PowerShell 工具进程均先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`；构建/设备命令再加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。后者也会加载前者。Python 明确使用 `D:/HCUP/common/.venv/Scripts/python.exe`，没有读取环境脚本输出中提及的题包目录。

本次实际执行，工作目录 `D:/HCUP/vg-spec13`：

```powershell
. D:/hongmengcup/Enter-HarmonyEnv.ps1
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
hdc -t 127.0.0.1:5555 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu
```

| 操作 | 本次实际结果 | 原始证据 |
| --- | --- | --- |
| 清理并重构建 | `pass`；退出码 `0`，`BUILD SUCCESSFUL in 16 s 667 ms` | [build-raw.log](../logs/baseline-20261016/build-raw.log:2313)、[build-result.json](../logs/baseline-20261016/build-result.json:1) |
| 安装本次 unsigned HAP | `pass`；退出码 `0`，`install bundle successfully` | [device-setup.log](../logs/baseline-20261016/device-setup.log:1)、[install-result.json](../logs/baseline-20261016/install-result.json:1)、[工具输出摘录](../logs/baseline-20261016/device-tool-output-excerpts.txt:1) |
| 启动 `io.qzz.weiyu/EntryAbility` | `pass`；退出码 `0`，`start ability successfully`，首页可见 | [device-start.log](../logs/baseline-20261016/device-start.log:1)、[工具输出摘录](../logs/baseline-20261016/device-tool-output-excerpts.txt:17)、[01-home.png](../logs/baseline-20261016/01-home.png) |
| 通用环境检查 | 退出码 `0`；系统镜像和分辨率匹配框架预设 | [device-start.log](../logs/baseline-20261016/device-start.log:1)、[工具输出摘录](../logs/baseline-20261016/device-tool-output-excerpts.txt:17) |

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`，8,937,956 字节；SHA-256 `d944aa2a16a62c2dc818b5672e3e0ce48bb431b8fe25274393df06372fdabf99`，见 [hap-sha256.json](../logs/baseline-20261016/hap-sha256.json:1)。签名配置为空（[build-profile.json5](../build-profile.json5:3)），实际模拟器正常接受 unsigned HAP，没有改配置或离线签名。早先 `logs/baseline-build.log` 不是本次构建证据。注意：PowerShell transcript 会漏掉直接写控制台的 native stdout；命令及 PS 退出码在 transcript，安装/启动成功字符串及环境输出的原始工具返回在本子会话 trace，另以 [device-tool-output-excerpts.txt](../logs/baseline-20261016/device-tool-output-excerpts.txt:1) 标明 chunk ID 摘录，未将摘录伪称实时 raw stream。

`RUNTIME_OBSERVED`：本次完整构建共有 **759 条带源码位置的 ArkTS warning**，另有 2 条非源码 warning 行（FAQ 提示、无 signingConfig），共 761 条含 `WARN` 的日志行。完整逐条位置、消息和 `raw_log_line` 索引在 [warnings-full.csv](../logs/baseline-20261016/warnings-full.csv:1) / [warnings-full.json](../logs/baseline-20261016/warnings-full.json:1)，没有省略警告；[warnings-summary.json](../logs/baseline-20261016/warnings-summary.json:1) 同时给出原始日志 SHA-256。

| 已有 warning 类别 | 数量 |
| --- | ---: |
| `Function may throw exceptions. Special handling is required.` | 505 |
| deprecated `showToast` | 128 |
| deprecated `back` / `pushUrl` / `getContext` / `showDialog` | 31 / 26 / 19 / 12 |
| deprecated `SetOrCreate` / `getParams` / `decode` | 6 / 6 / 5 |
| deprecated `createAudioPlayer` / `src` / `play` | 3 / 3 / 3 |
| deprecated `animateTo` / `release` | 2 / 2 |
| deprecated `encode` / `setPasteData` / `getLength` | 1 / 1 / 1 |
| `arkts-no-classes-as-obj` / `arkts-limited-esobj` | 2 / 1 |
| `@Prop text` / `@Prop duration` 不能 optional | 1 / 1 |
| FAQ 提示 / 无 signingConfig（不计入 759 条源码诊断） | 1 / 1 |

## 3. 入口、路由和本次实际导航

`RUNTIME_OBSERVED`：本次安装保留了设备已有 Preferences，**不是干净安装**。没有把原先端点/账号或其他历史状态作为本题功能证据，也没有访问旧端点；本次请求证据从覆盖并保存合成配置后开始。首页为“微语单词”，设置入口为右上角 `⚙`。本次实际按：首页 → `⚙` → “设置” → “WebDAV 配置”，随后向上滑动到“手动操作”中的“立即备份”。

| 入口关系 | `CODE_OBSERVED` 路径与调用点 | 本次设备证据 |
| --- | --- | --- |
| Ability → 首页 | [EntryAbility.ets](../entry/src/main/ets/entryability/EntryAbility.ets:35) 调用 `windowStage.loadContent('pages/Index')` | [01-home.json](../logs/baseline-20261016/01-home.json:1) / PNG |
| 齿轮 → 设置路由 | [TopNavigation.ets](../entry/src/main/ets/pages/index/components/TopNavigation.ets:69) 的 `⚙` 容器点击调用回调；[Index.ets](../entry/src/main/ets/pages/Index.ets:325) 使用 `router.pushUrl({ url: 'pages/SettingsPage' })` | [02-settings.json](../logs/baseline-20261016/02-settings.json:1) / [PNG](../logs/baseline-20261016/02-settings.png) |
| 设置 → WebDAV 分区 | [SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:41) 分区项 `id='sync'`；[同文件](../entry/src/main/ets/pages/SettingsPage.ets:527) 点击设置 `activeSectionId=item.id`；[同文件](../entry/src/main/ets/pages/SettingsPage.ets:447) 构造 `SettingsSyncSection` | [03-webdav-initial.json](../logs/baseline-20261016/03-webdav-initial.json:1) / PNG，仅证明导航及初始状态 |
| 立即备份 → 既有备份流程 | [SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:594) 按钮 `.onClick` 调用 `webdavBackup()`；[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:161) 进入包装器和 `backupToCloudInBackground()` | [06-before-backup.json](../logs/baseline-20261016/06-before-backup.json:1)、[observe-backup.log](../logs/baseline-20261016/observe-backup.log:1) |

WebDAV 不是独立路由；它是 `pages/SettingsPage` 下的 `activeSectionId='sync'` 分区。路由配置仍为 [main_pages.json](../entry/src/main/resources/base/profile/main_pages.json:7) 的 `pages/SettingsPage`。分区页头返回先清空 `activeSectionId`，再从设置页返回时才 `router.back()`（[SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:172)）；本次未执行返回/重进验证。

## 4. 页面、状态、数据、网络及存储现状

以下均为 `CODE_OBSERVED`，运行实证另注明：

- 页面表单字段来自父页 `@State`（[SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:114)），以 `@Link` 传给子分区（[SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:25)）。基础配置卡、自动同步卡、手动操作卡由三个 Builder 拼接（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:684)）。输入框 `.onChange` 修改字段，输入本身不保存经理配置（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:348)）。
- 子分区本地状态：`webdavResult`、`webdavBackupResult`、`webdavBusy`（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:41)）。手动备份包装器先检查 busy，再置 busy、赋值“正在备份到云端...”、等待 50ms、等待真实异步操作，`finally` 清 busy（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:141)）。
- busy 期间保存/测试/同步/备份/恢复五个按钮均显示“处理中...”且 `.enabled(!webdavBusy)`（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:543)、[578](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:578)、[594](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:594)）；备份结果文本位于 [同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:618)。本次 UI 树证实这五个按钮被禁用、文字可见。
- UI 包装器超时为 **120000ms**，以 `Promise.race` 实现（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:114)）。该方法没有取消底层操作的代码；`INFERENCE`：超时后 UI busy 可能先恢复，而网络/后台操作仍未完成。**未实测超时**。
- `WebDavSettings` 含 endpoint、username、password、syncPassword、remoteRoot 及 JSON 序列化（[WebDavCommon.ets](../entry/src/main/ets/sync/webdav/WebDavCommon.ets:49)）；`WebDavManifest` 含设备 ID、同步/备份时间戳和 ETag 等状态（[同文件](../entry/src/main/ets/sync/webdav/WebDavCommon.ets:102)）。经理单例持有设置、manifest 和自身 `WebDavSyncStatus`（[WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:71)），与 UI 的 `webdavBusy` 是不同状态变量。
- “保存设置”构造 `WebDavSettings` 并调用经理 `setSettings`（[SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:100)）；经理更新内存并保存 JSON（[WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:115)）。初始化读取本地 JSON，父页从经理装载字段（[同文件](../entry/src/main/ets/sync/WebDavSyncManager.ets:132)、[SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:190)）。
- 本地 WebDAV 状态使用 `@ohos.data.preferences`，存储名 `webdav_state_store`；配置主/备份键为 `webdav_settings_json`、`webdav_settings_json_bak`、`webdav_settings_json_bak_ts`（[WebDavStateStore.ets](../entry/src/main/ets/utils/WebDavStateStore.ets:62)）。`initialize` 使用 `preferences.getPreferences`（[同文件](../entry/src/main/ets/utils/WebDavStateStore.ets:120)），读写入口为 `getSettingsJson` / `saveSettingsJson`（[同文件](../entry/src/main/ets/utils/WebDavStateStore.ets:146)）。本次没有直接读取设备 Preferences 文件，也未验证重启持久化。
- 真实备份经理入口 `backupToCloudInBackground()` 先检查配置和自身同步状态、预检远端目录，进入内部 `try` 后调用 `DataSyncManager.exportData()`，再 `executeTaskWithFallback(executeBackupWithEncrypt, params)`（[WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:911)）。只有进入该内部 `try/finally` 的分支，才由 [finally](../entry/src/main/ets/sync/WebDavSyncManager.ets:1001) 恢复经理 `IDLE`；预检返回失败会提前设为 `ERROR` 并返回，预检抛异常也不经过该 `finally`（[预检位置](../entry/src/main/ets/sync/WebDavSyncManager.ets:930)）。导出使用现有 DBManager（[DataSyncManager.ets](../entry/src/main/ets/sync/DataSyncManager.ets:87)、[导出入口](../entry/src/main/ets/sync/DataSyncManager.ets:140)）。
- `@Concurrent executeBackupWithEncrypt` 执行加密和 PUT（[WebDavSyncTask.ets](../entry/src/main/ets/sync/webdav/WebDavSyncTask.ets:148)）；文件名 `backup.json.enc` 来自 [WebDavCommon.ets](../entry/src/main/ets/sync/webdav/WebDavCommon.ets:250)，远端路径组合见 [WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:214)。
- `WebDavClient` 用 `@ohos.net.http`，构造 Basic Auth，提供 HEAD、GET、PUT 等（[WebDavClient.ets](../entry/src/main/ets/sync/webdav/WebDavClient.ets:27)）；PUT 前检查父目录（[同文件](../entry/src/main/ets/sync/webdav/WebDavClient.ets:41)），HTTP 连接/读取超时为 15000/20000ms（[同文件](../entry/src/main/ets/sync/webdav/WebDavClient.ets:139)）。INTERNET 权限已声明（[module.json5](../entry/src/main/module.json5:15)）。

`RUNTIME_OBSERVED`：本次应用日志记录导出 0 words、0 user word books、277 字符数据，并在 TaskPool 加密为 565 字符后上传；PUT 成功、经理回到 `IDLE`。原文保留于 [app-hilog.log](../logs/baseline-20261016/app-hilog.log:1)，没有把代码调用本身当作发出请求的唯一证据。

## 5. 可复用的既有实现

- 入口和分区沿现有 `Index → SettingsPage → sync`，无需新页面路由；实测入口与上述代码一致。
- `runWebDavBackupAction` 已有 busy 防重入、进行中文字、结果及 finally 恢复，可把真实备份 Promise 和显示状态继续放在同一条调用链（[SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:141)）。这是复用候选，不代表边界行为已验证。
- 已有 `WebDavSyncManager`、`DataSyncManager`、TaskPool 加密/上传和 Preferences 配置保存；本次受控请求确认成功路径存在（第 4 节调用点、第 7 节证据）。
- 本题源码其他页面已有 ArkUI `LoadingProgress()` 样式可参考，例如 [TaskLoadingOverlay.ets](../entry/src/main/ets/pages/TaskLoadingOverlay.ets:18)、[NotebookPage.ets](../entry/src/main/ets/pages/NotebookPage.ets:151)。仅确认代码存在，**未运行这些相近页面**；未复制其他题或上游实现。

## 6. Spec 缺失能力与逐场景基线判定

`SPEC_EXPLICIT`：[requirement.md](requirement.md:7) 要求备份进行时渲染 ArkUI `LoadingProgress`；[场景二](requirement.md:20) 要求进行中的文字；[场景三](requirement.md:33) 要求加载状态绑定真实请求。

| Spec 场景/步骤 | 基线判定 | 证据范围 |
| --- | --- | --- |
| 场景一 1：进入并填写可访问配置 | `pass` | 本次合成端点保存成功，服务端收到有效认证的请求；不是任意配置皆可用 |
| 场景一 2–3：点击“立即备份”，进入忙碌 | `pass` | [observe-backup.log](../logs/baseline-20261016/observe-backup.log:1)、07/08/09/10 UI 树和截图 |
| 场景一 4：忙碌期间显示 ArkUI `LoadingProgress` | **`fail`** | 07/08/09/10 UI 树 `LoadingProgress` 均为 0；09 截图无指示器；备份分区源码未构造该组件 |
| 场景二 1–4：备份操作期间显示忙碌文案 | `pass`，仅本次已保存合成配置的单次成功路径 | 多次离散采样都有五个“处理中...”和“正在备份到云端...”；未证明所有异常/生命周期路径 |
| 场景三 1–4：忙碌状态绑定真实 WebDAV 请求 | `pass`，仅本次已保存合成配置的单次成功路径 | 主机同一 UTC 时钟记录的 09 采样完整落在 PUT 的 received/responded 之间；下列最小复现和时间线 |
| 成功后结果及恢复（合理推导的观察） | `pass`，单次 | [11-settled.json](../logs/baseline-20261016/11-settled.json:1) / PNG：五个按钮重新 enabled，显示“✅ 备份已上传” |
| 仅填写未保存就点击备份 | `not_run` | 仅保存了 04 未保存配置截图，**没有在未保存状态点击备份**。代码路径见下 |
| 空值/纯空格、无配置、错误认证、HTTP 失败/超时、快速连点、取消/关闭、返回重进、重启、操作中离开、不同数据量 | `not_run` | 本次只做未修改基线摸底，不把静态阅读或成功路径外推为通过 |

没有设备/签名环境 `blocked`；整题仍有明确 `fail`，不得将编译成功计为整题通过。

最小失败复现：

1. 安装上述哈希的基线 HAP，启动并按第 3 节进入目标分区。
2. 启动 [webdav-fixture.py](../logs/baseline-20261016/webdav-fixture.py:1)，使用 `hdc -t 127.0.0.1:5555 rport tcp:18173 tcp:18173` 将设备端口转发至本机。fixture 对 HEAD 返回 200；收到备份 PUT 后等待 8 秒，返回 201。
3. UI 填入 endpoint `http://127.0.0.1:18173`、username `vg13-fixture`、password `fixture-pass`、同步密码 `fixture-sync-pass`、目录 `/vg13-baseline`，关闭自动同步并点击“保存设置”。这些都是本次合成凭据。
4. 滚动到手动操作，点击“立即备份”，在服务端 PUT 尚未响应时 dumpLayout / screenCap。实际配置和操作脚本为 [ui-config.py](../logs/baseline-20261016/ui-config.py:1)、[observe-backup.py](../logs/baseline-20261016/observe-backup.py:1)，原始执行日志分别为同名 `.log`。配置与观察脚本退出码均 `0`。

期望：备份仍在执行时，页面包含可见 ArkUI `LoadingProgress`。实际：只有禁用按钮上的“处理中...”和备份结果位置的“正在备份到云端...”；没有 `LoadingProgress`。关联：场景一第 4 步。归因假设：`SettingsSyncSection` 有 busy 状态和文案，Builder 没有构造指示器。证据强度：**强（本次源码＋原始 UI 树＋截图目视检查＋服务端请求时间共同支持）**。截图通过 `view_image` 工具检查，没有声称人类参与操作。建议主 Agent 在后续实现阶段处理该 UI 缺口；当前分析阶段不修代码。

本次主机 UTC 时间线（[fixture-requests.jsonl](../logs/baseline-20261016/fixture-requests.jsonl:1)、[backup-observations.jsonl](../logs/baseline-20261016/backup-observations.jsonl:1)）：

| 事件 | 主机 UTC |
| --- | --- |
| HEAD `/vg13-baseline`，有效认证，200 | 07:16:33.691705 收到 / 33.692705 响应 |
| 上传前 HEAD，同目录，200 | 07:16:38.654484 收到 / 38.655708 响应 |
| PUT `/vg13-baseline/backup.json.enc`，565 字节，有效认证 | **07:16:38.731808 收到** |
| `09-busy-late`：UI 树、截图完整采样区间，仍有忙碌文案，LoadingProgress=0 | **07:16:39.237883–07:16:40.069144** |
| `10-completed` 实际仍是忙碌采样 | 07:16:45.070469–07:16:45.879076 |
| PUT 201 响应 | **07:16:46.732867** |
| 真正完成态 `11-settled` | 07:18:04 后捕获，见 device-finish 日志 |

**`10-completed` 是观察脚本预先取的文件名，实际捕获早于 PUT 响应，不能作为完成态证据。** 真正完成态只使用 11。设备 hilog 时钟与主机约有 2 秒差异，因而重叠判断只比较同一主机 UTC 的服务端和采样日志，没有直接混用 hilog 墙钟。

## 7. 前置环境、受控服务与清理

- `RUNTIME_OBSERVED`：设备 `127.0.0.1:5555`，软件 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`，API `23`，分辨率 `1308×2880`。DevEco 环境脚本显示 6.1.0.860；工程目标/兼容 SDK 是 `6.0.2(22)`（[build-profile.json5](../build-profile.json5:8)）。通用检查仅实测版本和分辨率；**机型名称和 560dpi 没有独立读取确认**，不能由“框架规格一致”文字推导为全部设备参数都已测。
- 不需要应用登录账号即可到达该配置分区并执行本次备份；本次没有登录任何真实服务账号。必须有可访问的端点、账号、密码及同步加密密码；代码对必填项的检查见 [SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:339) 和经理配置检查调用 [WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:915)。
- 本地可以满足本次备份请求/状态观察：fixture 监听 `127.0.0.1:18173`，合成 Basic Auth 校验，目录用 HEAD 200 模拟已存在；仅记录方法、路径、时间、长度、密文 SHA-256 和认证是否匹配，不记录真实外部数据或认证头。fixture 是最小 HTTP/WebDAV 操作端点，**没有验证完整真实 WebDAV 服务兼容性、恢复内容完整性、外网/TLS 或服务商行为**。
- `06-before-backup.json` 的 Toggle `checked=false`，截图也为关闭；本次没有触发“测试连接”或“立即同步”，服务端在备份点击前无应用请求。本次导出日志为 0 单词、0 用户词书；不是丰富测试数据场景。
- 服务启动、rport 添加和清理证据：[fixture-port.log](../logs/baseline-20261016/fixture-port.log:1)、[device-finish.log](../logs/baseline-20261016/device-finish.log:1)、[cleanup-check.log](../logs/baseline-20261016/cleanup-check.log:1)。rport 添加/删除退出码均 `0`；没有删除其他转发规则。
- fixture 停服时先停止 venv launcher PID 49312，其子进程 PID 45880 随即退出；再次停止子进程得到“进程不存在”，该清理 PowerShell 调用退出 `1`，原始错误保留。随后复核退出 `0`：相关 Python 进程 `0`、18173 监听 `0`，本次 reverse rule 已不存在。服务器会话因主动终止退出 `1`，这是清理记录，不是业务备份失败。设备保留本次合成配置且自动同步关闭；未清空设备数据。

辅助工具尝试也如实登记：`wm dump -a` 在该镜像不存在（见 device-setup）；`uitest --help` 返回非法参数但打印用法（见 device-start）；`rport -h` 返回错误参数（见 navigation）。首次创建观察脚本用了相对路径与工作目录重复拼接，Set-Content 在设备操作前失败（工具输出 chunk `db586c`，退出 1），改成正确的当前目录后执行成功。没有发生“连接服务失败后修改业务代码”，也没有未保存配置点击测试；上述均不能计成业务通过/失败。

## 8. 测试可观测性与后续验收风险

- `CODE_OBSERVED`：目标子分区没有 `.id()`；五个输入框、立即备份按钮、状态文本、未来的 spinner 均缺稳定选择器。父页仅根 `.id('settings_' + themeRefreshToken)`（[SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:565)），随主题 token 改变，不适合定位具体控件。`RUNTIME_OBSERVED`：09 UI 树五个 busy Button 的 `id` 都为空。
- 同名“显示”密码按钮出现两次；忙碌时五个按钮全部叫“处理中...”，按文本会歧义。标题也有“WebDAV 配置”，与分区入口同名但处于不同页面状态。本次配置用 TextInput 的 hint，导航/点击使用已观察到的 bounds；坐标仅对此屏幕成立，不是稳定验收选择器。实现阶段宜给必要控件补 `.id()`，本阶段没有补。
- 分区在 `Scroll` 中（[SettingsPage.ets](../entry/src/main/ets/pages/SettingsPage.ets:503)）；初次进入时“立即备份”在屏幕下方，需要滚动。spinner 的后续观察必须保证位于可见区域，不能只证明代码创建了组件。
- `CODE_OBSERVED`：`webdavBackup()` 不调用 `saveWebDavSettings()`（[SettingsSyncSection.ets](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:161)）；与会先保存的 `webdavSyncNow()` 不同（[同文件](../entry/src/main/ets/pages/settings/SettingsSyncSection.ets:289)）。`INFERENCE`：只填写未保存时可能仍使用经理旧配置；本次显式先保存，未验证该歧义，应由需求/方案角色决定验收口径。
- UI 超时、经理状态和后台 I/O 生命周期并非同一状态源，且预检在经理主 try/finally 之前（[WebDavSyncManager.ets](../entry/src/main/ets/sync/WebDavSyncManager.ets:930)）；网络异常、重复操作、离开再进入等路径仅作风险记录，均 `not_run`。不把这些推断写成已复现 bug。
- 本次证据只覆盖保存合成配置后的手动备份成功路径、多个忙碌采样及成功恢复。未执行官方测试、未推断 F-point 数量或成绩；没有用隐藏测试、来源项目修复或其他题工程作参考。
