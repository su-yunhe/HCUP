# vg-spec7 基线现状记录（分析阶段）

记录日期：2026-10-17（Asia/Shanghai）。本次仅执行 [0-analyze.md](D:/HCUP/vg-spec7/spec-harness/0-analyze.md:1)：交付本文和 [acceptance.md](D:/HCUP/vg-spec7/spec/acceptance.md)，不修改业务代码、不修复基线缺陷、不进入功能实现。结论标明 **代码实证／实测／推断／未验证**，不将构建成功当成功能通过。

## 1. 基线快照与输入

| 项目 | 标识与证据 |
| --- | --- |
| 工程根 | `D:/HCUP/vg-spec7`，工程就在当前根目录，没有另建 project 子目录。 |
| 基线 HEAD | `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，与 [metadata.json](D:/HCUP/vg-spec7/spec/metadata.json:2) 一致；选择记录 HEAD，没有新增 tag 或切换提交。 |
| Spec | [requirement.md](D:/HCUP/vg-spec7/spec/requirement.md:1)，SHA-256 `60d2e252f5beb18d17717444480ae925f96fc00696cd8ae276c0c07f3fd72276`。 |
| metadata | SHA-256 `92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。 |
| 准备记录 | [prepare-baseline.log](D:/HCUP/vg-spec7/logs/prepare-baseline.log:1) 记录 harmony-cup-build-v1、changes=[]。只将本题准备日志用于准备状态，不读取初始化总览会话作为功能证据。 |
| 本轮指纹 | [source-integrity.json](D:/HCUP/vg-spec7/traces/analysis-baseline-build/source-integrity.json:1)：299 个已跟踪文件重建前后及准备指纹完全一致；业务源码相对 HEAD 无差异。指纹清单 SHA-256 为 `d696f224cf6fbacd5fbfbabc7af69d5667cd4c34ec7cea44f60736f1d44a33a8`。 |
| 初始差异 | 已存在的 AGENTS.md 工作流说明差异，以及 spec/inputs/workflow/logs 等本题准备记录，不是本次业务修改。起始状态见 [analysis-start-fingerprint.json](D:/HCUP/vg-spec7/workflow/analysis-start-fingerprint.json:1)。 |

## 2. 未修改基线的构建

**实测：完整重建成功，退出码 0，耗时 18.478 秒。** 2026-10-17 10:26:45 至 10:27:04（+08:00），不是仅沿用准备时的旧 HAP。调用记录见 [build-invocation.json](D:/HCUP/vg-spec7/traces/analysis-baseline-build/build-invocation.json:1)，原始输出见 [build.log](D:/HCUP/vg-spec7/traces/analysis-baseline-build/build.log:1)。

在工程根运行的可复现命令：

```powershell
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location -LiteralPath 'D:/HCUP/vg-spec7'
hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

本轮实际使用 DevEco Studio 6.1.0.860 的 hvigorw，`DEVECO_SDK_HOME=D:/HarmonyDev/sdk/api23`；Node、Java、ohpm 路径及版本保留在 [environment.log](D:/HCUP/vg-spec7/traces/analysis-baseline-build/environment.log:1)。工程声明仍是 [build-profile.json5:7](D:/HCUP/vg-spec7/build-profile.json5:7) 的 target/compatible SDK `6.0.2(22)`，未修改为 API 23；运行设备是 API 23。工具安装路径、工程声明和运行版本分别记录，不混为同一版本。

产物：[entry-default-unsigned.hap](D:/HCUP/vg-spec7/entry/build/default/outputs/default/entry-default-unsigned.hap)，9,065,537 字节，SHA-256 `8be50a47fe3ea2cf7595783af35071ac24ed3c775d5f6d677d28eea56eed1307`。工程 [build-profile.json5:3](D:/HCUP/vg-spec7/build-profile.json5:3) signingConfigs 为空；本轮未修改签名配置，也未派生签名包。该模拟器已实际接受此未签名包，不能由此推断真机也允许。

### 已有告警清单

完整 **764 条带文件位置的诊断** 均保留在 [warnings-full.csv](D:/HCUP/vg-spec7/traces/analysis-baseline-build/warnings-full.csv:1) 和 [warnings-full.json](D:/HCUP/vg-spec7/traces/analysis-baseline-build/warnings-full.json:1)，每条含 file、line、column、message、build_log_line；后续应按位置与消息对比，不能只比较总数。分类及逐消息计数见 [warnings-summary.json](D:/HCUP/vg-spec7/traces/analysis-baseline-build/warnings-summary.json:1)。

| 类别 | 数量 | 代表位置（全量以清单为准） |
| --- | --- | --- |
| 异常处理提示 | 498 | [WordBookCatalog.ets:400](D:/HCUP/vg-spec7/entry/src/main/ets/model/WordBookCatalog.ets:400)，Function may throw exceptions. Special handling is required. |
| 废弃 API | 260 | [DataExportImport.ets:515](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataExportImport.ets:515)；包含 showToast 132、back 32、pushUrl 27、getContext 25、showDialog 11、getParams 6、SetOrCreate 6、decode 5、createAudioPlayer/play/src 各 3、animateTo/release 各 2、getLength/encode/setPasteData 各 1。 |
| ESObject 限制 | 1 | [DesignTokens.ets:411](D:/HCUP/vg-spec7/entry/src/main/ets/model/DesignTokens.ets:411)。 |
| globalThis 限制 | 1 | [SecureStorage.ets:154](D:/HCUP/vg-spec7/entry/src/main/ets/utils/SecureStorage.ets:154)。 |
| 类作为对象 | 2 | [UserStateManager.ets:372](D:/HCUP/vg-spec7/entry/src/main/ets/manager/UserStateManager.ets:372)，另一位置见全量清单。 |
| 可选 @Prop | 2 | [LoadingAnimations.ets:225](D:/HCUP/vg-spec7/entry/src/main/ets/ui/LoadingAnimations.ets:225)、第 226 行。 |

此外日志包含 ArkTS FAQ 指引与 `No signingConfig found for product default`，未并入上述文件诊断数。本阶段均只记录，不修复。

## 3. 安装、启动与现有入口

**实测：** 起初 `hdc list targets` 为 [Empty]；检查无占用后启动既有 `HarmonyCup_API23`，连接 `127.0.0.1:5555`。实际安装上述本轮 HAP，启动 `io.qzz.weiyu / EntryAbility` 成功。连接与启动过程保存在 [bootstrap.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/bootstrap.log:1)、[commands.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/commands.jsonl:1)。

设备参数：HarmonyOS 6.1.0 / API 23、镜像 `6.1.0.115(SP11DEVC00E115R4P11)`、1308×2880、560 dpi；[environment-check.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/environment-check.log:1) 的本地框架检查通过。它核对版本和分辨率，不代表执行了官方隐藏测试。

明确指定设备的安装、启动命令：

```powershell
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location -LiteralPath 'D:/HCUP/vg-spec7'
hdc -t 127.0.0.1:5555 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu
```

[reinstall-explicit.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/reinstall-explicit.log:1) 为 install bundle successfully，[relaunch-explicit.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/relaunch-explicit.log:1) 为 start ability successfully，两者退出码均 0，完整参数见追加的 commands.jsonl。早期 device-step.ps1 曾因 PowerShell 隐式位置绑定丢失 -t 的设备值；已修正并重新明确指定设备安装／启动。旧成功输出保留作过程记录，不用旧参数日志证明显式目标设备。

本轮为覆盖安装、保留既有应用数据，不清空、不导入业务数据。既有配置不能作为“基线初始默认值”的运行证据；本题网络验证需通过 UI 换成本题虚拟配置并隔离自动同步。默认开关的判断仅来自源码，见第 4 节。

### 入口：运行操作与源码对应

已通过设备 UI 从首页设置齿轮进入设置，再选择“WebDAV 配置”；相应操作日志和 UI 树在 [click-settings.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/click-settings.log:1)、[open-webdav.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/open-webdav.log:1)、[settings-top-valid-tree.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/settings-top-valid-tree.json:1)。以下跳转点另有代码实证：

| 环节 | 页面／路由／调用点 |
| --- | --- |
| 初始首页 | [EntryAbility.ets:35](D:/HCUP/vg-spec7/entry/src/main/ets/entryability/EntryAbility.ets:35) 加载 `pages/Index`。 |
| 首页设置齿轮 | [TopNavigation.ets:70](D:/HCUP/vg-spec7/entry/src/main/ets/pages/index/components/TopNavigation.ets:70) 的 ⚙，第 79 行触发 onSettingsClick；[Index.ets:323](D:/HCUP/vg-spec7/entry/src/main/ets/pages/Index.ets:323) `router.pushUrl({ url: 'pages/SettingsPage' })`。 |
| 路由登记 | [main_pages.json:7](D:/HCUP/vg-spec7/entry/src/main/resources/base/profile/main_pages.json:7) 的 `pages/SettingsPage`。 |
| WebDAV 菜单项 | [SettingsPage.ets:40](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:40) 的 `id: 'sync'`、标题“WebDAV 配置”；第 491 行显示，第 507／511 行点击后更新 activeSectionId。 |
| 目标内容 | [SettingsPage.ets:427](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:427) 判定 sync，第 428 行创建 `SettingsSyncSection`。**WebDAV 配置是设置页内区段，没有独立路由。** |
| 区段返回 | [SettingsPage.ets:172](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:172) 先清空 activeSectionId 回菜单；已在菜单时第 178 行 router.back()。返回箭头第 464／467 行。以上返回行为本轮未逐项实操。 |
| 另一个“去设置 >”捷径 | [SettingsBackupSection.ets:323](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsBackupSection.ets:323) 调用 navigateToSyncSettings，第 195／197 行传 `section: 'sync'`。代码未找到 SettingsPage 消费该参数，**未验证其直接打开目标区段**，不作为主验收导航。 |

首次启动可能有隐私与引导：[Index.ets:285](D:/HCUP/vg-spec7/entry/src/main/ets/pages/Index.ets:285) 检查隐私、第 293 行显示框；第 343 行同意后检查引导；第 137 行可转 `pages/OnboardingPage`。本轮保留已有数据，未覆盖首次启动分支，不能宣称已测。目标入口链未见应用账号登录检查；WebDAV 认证是另一件事。

## 4. 相关实现现状（代码实证）

### 页面与状态

- 父页 [SettingsPage.ets:114](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:114) 至第 126 行为 WebDAV `@State`，第 429 行起通过双向绑定交给子组件；[SettingsSyncSection.ets:25](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:25) 至第 37 行为对应 `@Link`。
- 子组件 [SettingsSyncSection.ets:41](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:41) 至第 43 行分别是 webdavResult、webdavBackupResult、webdavBusy。没有独立的首个恢复确认 visible 状态，现有框使用原生 promptAction.showDialog Promise。
- 父页 [SettingsPage.ets:163](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:163) 至第 167 行初始化 manager/store 并加载已保存配置；子组件 [第 54 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:54) 加载自动同步设置。

### 恢复调用顺序与副作用

| 顺序 | 源码位置 | 事实 |
| --- | --- | --- |
| 1 | [SettingsSyncSection.ets:507](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:507)、第 516／164 行 | 「从云端恢复」调用 webdavRestore。 |
| 2 | [同文件第 140 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:140) | webdavBusy 防重；第 142／143 行先置忙并显示“正在处理...”，第 145 行等待 50 ms，然后第 148 行运行带超时操作。 |
| 3 | [同文件第 199 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:199) | webdavRestoreWithPreview 在第 200 行先 await downloadBackupPlain(false)，尚未显示确认。 |
| 4 | [WebDavSyncManager.ets:471](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:471)、第 160 行 | 校验已保存配置；无效时可直接失败，不显示恢复框。第 475／477／478 行设 RESTORING、创建客户端、preflightRemoteRoot。 |
| 5 | [WebDavSyncManager.ets:280](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:280)、第 294 行 | 未命中布局缓存、远端 root 非 / 时 HEAD 目录。第 303／305／364 行可能 PUT .keep；第 262／264 行探测可 PUT .probe_* 后 DELETE；实际走哪支取决于服务响应。 |
| 6 | [WebDavBackupManager.ets:79](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:79) | HEAD 当前备份；404 时第 81 行 HEAD 旧路径。第 88 行冲突判断可提前终止；[WebDavConflictResolver.ets:15](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavConflictResolver.ets:15) 处理无备份。 |
| 7 | [WebDavBackupManager.ets:96](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:96) | 先导出本地快照，第 98 行写 snapshot；[DataSyncManager.ets:185](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:185)／第 187 行还更新内存版本和变更记录。它与导入业务数据须区分。 |
| 8 | [WebDavBackupManager.ets:101](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:101)、第 111 行 | GET 备份、用同步密码解密，仍在首个确认之前。 |
| 9 | [SettingsSyncSection.ets:206](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:206) | previewImport；错误可直接返回。 [DataSyncManager.ets:351](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:351) 的预览解析并查库统计，第 366 行查询，不调用导入写入。 |
| 10 | [SettingsSyncSection.ets:215](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:215) | 此时才 showDialog；标题“⚠️ 恢复确认”，第 219／220 行为“取消”／“确认恢复”。**没有 Spec 的「继续」动作。** |
| 11 | [同文件第 225 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:225) | index=0 返回“已取消恢复”；第 228 行才 importPlainBackup；第 229／230 行异常也作取消。 |
| 12 | [同文件第 149 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:149) | 输出结果和 toast，finally 第 155 行清 webdavBusy。 |

因此，**代码实证**是“已有下载后的预览确认，缺少请求前的确认门禁”。取消现有框可阻止导入，却不能撤销之前的请求、下载与快照。服务端无备份、下载／解密／预览失败都可能让现有框完全不出现。没有找到名为 showRestoreDialog 的实际基线方法，后续不要引用不存在的方法名作为改动点。

### 网络服务与数据模型

- `WebDavSettings` 在 [WebDavCommon.ets:49](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavCommon.ets:49) 定义 endpoint、username、password、syncPassword、remoteRoot、requireRemoteRootExists；manifest 在第 102 行记录时间、ETag、同步状态；`WebDavBackupPlainResult` 在第 207 行携带结果和解密明文。
- 当前／旧备份路径由 [WebDavSyncManager.ets:210](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:210)、第 214 行生成；文件名在 [WebDavCommon.ets:250](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavCommon.ets:250) 为 `backup.json.enc`。此链使用 HEAD/GET，未使用 PROPFIND；这只是基线事实，不限定目标实现的 HTTP 方法。
- [WebDavClient.ets:27](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavClient.ets:27) 接收 endpoint 和 Basic Auth；第 33／37 行包装 GET/HEAD，第 85 行拼 URL，第 146 行 `request.request(url, options)` 真正请求；第 140／141 行连接与读取超时为 15／20 秒，第 166 行起最多跟随两次重定向，第 164／176 行释放请求对象。
- [WebDavLogger.ets:57](D:/HCUP/vg-spec7/entry/src/main/ets/utils/WebDavLogger.ets:57) 格式化请求日志，第 62／67 行输出；可辅助归因，不能以“没有日志”代替端点无请求。

### 恢复数据写入

现有确认后的调用链是 [WebDavSyncManager.ets:502](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:502) → [WebDavBackupManager.ets:174](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:174)／第 178 行 → DataSyncManager.importData。具体写入包括：

| 数据 | 代码位置 |
| --- | --- |
| FSRS 参数／算法 | [DataSyncManager.ets:232](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:232)、第 233 行。 |
| 单词插入／更新 | [第 243 行](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:243)、第 254 行。 |
| 释义缓存 | [第 279 行](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:279)。 |
| 词书创建／更新 | [第 297 行](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:297)、第 311 行。 |
| 导入版本 | [第 336 行](D:/HCUP/vg-spec7/entry/src/main/ets/sync/DataSyncManager.ets:336)。 |

RDB 打开在 [DBManager.ets:172](D:/HCUP/vg-spec7/entry/src/main/ets/database/DBManager.ets:172)，相关方法在第 258／270／340／587／595 行转发 repository。以上是源码定位，**本轮没有执行完整导入或做全量数据库前后快照，数据层行为未动态验证。**

### 设置与本地存储

- WebDAV 区域 [SettingsSyncSection.ets:446](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:446) 的保存按钮在第 454 行调用 saveWebDavSettings；[第 99 行](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:99) trim 地址、账号、root，密码与同步密码原值传递；空 root 回退 /weiyu_sync。第 106 行 requireRemoteRootExists=true。
- [WebDavSyncManager.ets:111](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:111) 更新内存配置、清布局缓存，第 120 行写 JSON，本方法不发网络；store 未就绪时第 121 行仍可返回 true，成功提示不等于已证落盘。
- [WebDavStateStore.ets:63](D:/HCUP/vg-spec7/entry/src/main/ets/utils/WebDavStateStore.ets:63) 使用 Preferences `webdav_state_store`；第 66／72／78 行为 settings／manifest／snapshot key；第 284 行起写主值、备份值、时间戳并 flush，第 261 行起可用备份修复。
- **恢复不自动保存当前输入。** [SettingsSyncSection.ets:164](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:164) 直接调用下载链；父页离开时的 [SettingsPage.ets:159](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:159)／第 300 行 saveSettings 只保存普通 AppSettings 和 API key。主验收必须明确 WebDAV 区域保存步骤；未保存 E2 是否使用 E2 属于 acceptance.md 的 U02。
- 默认 root 模型为 [WebDavCommon.ets:62](D:/HCUP/vg-spec7/entry/src/main/ets/sync/webdav/WebDavCommon.ets:62) 的 /weiyu_vignette；父页初值 [SettingsPage.ets:118](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:118) 与保存空值回退为 /weiyu_sync。初始化后会读取管理器设置，不能只看一个初值推断运行有效目录。

### loading、超时与自动同步

页面 webdavBusy 在下载前即置 true；[SettingsSyncSection.ets:446](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:446)、第 456／481／497／507 行五个操作按钮都会显示“处理中...”并禁用，等待现有确认时也忙。管理器在 [WebDavSyncManager.ets:493](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:493) 下载完成后已回 IDLE/ERROR，页面 busy 与网络状态不同。

**静态推断、未实测：** [SettingsSyncSection.ets:113](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:113) 至第 121 行 Promise.race 的 120 秒覆盖整个下载及等待确认，没有清计时器或取消底层工作；长时间停留框可能先清 busy，原流程仍存活。未见恢复相关 aboutToDisappear 清理；离页／超时后任务行为尚未动态验证。不能将 120 秒升级为 Spec 规定。

自动同步是独立干扰源：[EntryAbility.ets:49](D:/HCUP/vg-spec7/entry/src/main/ets/entryability/EntryAbility.ets:49) 至第 54 行前台 tryRun；[AutoWebDavSyncManager.ets:33](D:/HCUP/vg-spec7/entry/src/main/ets/sync/AutoWebDavSyncManager.ets:33) 独立 busy，第 48／53 行检查开关与间隔，第 65 行增量同步，第 75 行可上传全量备份。默认开为 [WebDavStateStore.ets:170](D:/HCUP/vg-spec7/entry/src/main/ets/utils/WebDavStateStore.ets:170) 至第 173 行，默认间隔 6 小时在第 184 行。增量路径还会 [WebDavSyncManager.ets:716](D:/HCUP/vg-spec7/entry/src/main/ets/sync/WebDavSyncManager.ets:716) importIncremental。

因此测试需关闭自动同步、等历史任务结束并单独归因。页面恢复 busy 不等于全局互斥。确认等待时“任何请求”是否要求暂停已有独立任务，保留为 U07，不自行豁免。

## 5. 可复用既有实现

| 能力 | 基线位置与价值 |
| --- | --- |
| 现有页面／导航 | 复用 SettingsPage 的 sync 区段、SettingsSyncSection 及原设置路由，官方测试可沿既有入口进入，无需另起页面。证据见第 3 节。 |
| 下载、解密、预览、导入 | 已有 WebDavSyncManager、WebDavBackupManager、DataSyncManager 和统一结果模型；缺少的是请求前授权阶段，而不是整个恢复能力。证据见第 4 节。 |
| 本地导入确认模式 | [SettingsBackupSection.ets:152](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsBackupSection.ets:152) 预览→第 164 行原生确认→第 174 行取消／第 180 行导入；[SettingsPage.ets:355](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:355) 至第 375 行有类似粘贴导入确认。不能照搬成确认前先网络下载。 |
| 本地弹层 | [SettingsSyncDialog.ets:8](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncDialog.ets:8) 的 @Link visible 与数据，第 44 行遮罩关闭、第 113 行导入回调、第 125 行取消；它是粘贴／导出层，**不是**恢复确认框。 |
| 结果／忙态／持久化 | 现有 WebDavSyncResult、页面 runWebDavBackupAction、Preferences 主备写入可供后续方案评估；120 秒与清理风险需独立考虑。 |

本表仅列可复用现状，本阶段未批准或实施任何代码修改方案。

## 6. Spec 缺失能力

**代码实证：**

1. 缺少先展示本地确认、再允许任何恢复网络行为的阶段（acceptance A07、A09–A11）。现有第 200 行下载在第 215 行弹框之前。
2. 缺少首个确认中的精确「继续」动作（A08、B02）；已有“确认恢复”承担下载后导入确认，不能当作 Spec 要求的首个授权。
3. 因首次确认迟于请求与下载，取消现有框无法满足“尚未继续零请求”的边界。无备份或网络失败还可能完全没有确认框。

这不是“基线完全没有恢复功能”；下载、解密、预览、取消导入与实际导入均已有。运行是否进入各分支见第 9 节，未到达的分支不写作实测失败或通过。

## 7. 前置环境与可满足范围

| 条件 | 本地现状／限制 |
| --- | --- |
| 构建工具和依赖 | 本轮 clean 构建成功；保持原 SDK 声明、配置、锁文件。原始日志见第 2 节。 |
| 设备和安装 | 既有模拟器已启动并实际安装启动本题产物；只在此模拟器验证，真机未验证。 |
| 应用登录 | 入口代码未见登录门禁；本轮既有数据路径实际进入，无需真实账号。首次隐私／引导分支未验证。 |
| WebDAV 服务和账号 | 可使用本地受控 HTTP/WebDAV 夹具与虚拟凭据，端点账本验证请求；不需要真实外部账号。具体可达性与本轮请求结果见第 9 节。 |
| 云端备份 | 证明提前请求／继续后真实发现可用受控 HEAD/404 等响应；要验证现有下载后弹框及完整恢复，需要兼容加密格式、同步密码、可解析备份和差异业务数据。本轮不因没有完整备份而把未测项记通过。 |
| 网络协议 | 本轮本地 HTTP 不代表真实 HTTPS、证书链、重定向、外部服务认证与防火墙均通过；这些未验证。 |
| 权限 | [module.json5:15](D:/HCUP/vg-spec7/entry/src/main/module.json5:15) 声明 INTERNET；第 7 行 deviceTypes=phone。本轮不新增权限。 |

## 8. 测试可观测性风险

- 首页根 [Index.ets:360](D:/HCUP/vg-spec7/entry/src/main/ets/pages/Index.ets:360) 与设置根 [SettingsPage.ets:549](D:/HCUP/vg-spec7/entry/src/main/ets/pages/SettingsPage.ets:549) id 拼接主题 token；设置数据项 id=sync 与 ForEach key 不是组件 id。
- 目标齿轮、菜单项、输入框、自动同步 Toggle、五个操作按钮和结果文字均缺少固定 .id()；后续建议名称与“需在实现时补 .id()”逐项列在 acceptance.md 第 5 节。本阶段未补。
- 恢复入口精确文本可用，包含匹配可能命中 [SettingsSyncSection.ets:561](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:561) 的说明“【从云端恢复】下载云端数据覆盖本地”。忙时五按钮同名“处理中...”，不能唯一选择。
- [SettingsSyncSection.ets:303](D:/HCUP/vg-spec7/entry/src/main/ets/pages/settings/SettingsSyncSection.ets:303) 密码 builder 在第 355／356 行复用，两个“显示／隐藏”同名。确认正文第 212 行也含“继续”，不能把正文命中误判为继续按钮。
- 原生恢复框没有业务固定 id；必须限定当前 Dialog 范围并精确匹配动作。其他本地导入弹层也有“取消／关闭”，不可跨弹层取同名文本。
- UI 树和 Hypium 只能证明控件／交互；零连接、零请求、备份体下载与数据恢复必须配套端点账本及数据／调用观测。有限窗口零条请求不证明无限期无请求。
- 本轮通过设备 CLI、UI 树和截图做操作观测，尚未落地完整 Hypium 回归套件；acceptance.md 中的 Hypium 断言是后续定义，不是已执行结果。

## 9. 本轮核心实操证据

**实测结论：在有效目录、正确虚拟认证且自动同步关闭的情况下，仅点击「从云端恢复」就建立连接并发出备份发现请求，首个确认框没有出现。** 已复现 Spec 的请求时序违例；没有修改代码修复。

### 操作与隔离

设备角色使用本题虚拟账号、密码、同步密码，通过 UI 覆盖四字段及远端目录，点击 **WebDAV 区域** 保存。第一组保存后重启并重进核对字段与自动同步 false，见 [webdav-persisted-valid-tree.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/webdav-persisted-valid-tree.json:1)。未清除应用数据，也未恢复／导入既有业务数据。

两组受控服务分别只监听主机 `127.0.0.1:18987`、`127.0.0.1:18988`，通过本轮 hdc rport 映射供模拟器访问。后者应用地址为 `http://127.0.0.1:18988/vg-spec7-dav`，目录为 `/vg_spec7_baseline_20261017`，认证与虚拟凭据匹配。夹具源 [webdav-fixture.cjs](D:/HCUP/vg-spec7/traces/analysis-baseline-device/webdav-fixture.cjs:1)、[directory-fixture.cjs](D:/HCUP/vg-spec7/traces/analysis-baseline-device/directory-fixture.cjs:1) 保留复现条件，不属于业务代码或正式 Hypium 套件。

自动同步关闭，准备流量与恢复窗口分开；第一组点击前额外观察 5 秒，无应用请求，第二组在点击前同样记录 application_requests=0。[ui-events.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/ui-events.jsonl:1) 为 UI 事件，端点账本使用 UTC（Z），下表换算为 +08:00；不是两套未对齐的时间。

### 第一组：目录返回 404

| 时间（+08:00） | 实际事件 | 原始证据 |
| --- | --- | --- |
| 10:36:53.919 | 仅点击一次「从云端恢复」，没有点击任何继续／确认 | [ui-events.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/ui-events.jsonl:1)、[click-restore404.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/click-restore404.log:1) |
| 10:36:54.248 | 本轮应用 TCP 连接建立 | [endpoint-requests.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/endpoint-requests.jsonl:1) |
| 10:36:54.267 | HEAD `/vg-spec7-dav/vg_spec7_baseline_20261017`，认证头存在 | 同上，request id=4 |
| 10:36:59.278 | 首次 404 后再次 HEAD 同一目录 | 同上，request id=5 |
| 10:37:04.291 | PUT 目录下 `.keep`，同样返回 404 | 同上，request id=6 |
| 最后响应 10:37:09.301 后 | 无确认框；结果“创建目录失败：PUT 404: vg-spec7 fixture: no backup”，五按钮恢复 enabled=true | [restore404-finished-summary.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/restore404-finished-summary.jsonl:1)、[截图](D:/HCUP/vg-spec7/traces/analysis-baseline-device/restore404-finished.png) |

该应用窗口为 **1 个 TCP 连接、3 个请求（2 HEAD + 1 PUT）**；准备控制请求另有 event 类型，不混算为应用请求。请求期间没有确认框，五按钮均禁用并显示“处理中...”，结果显示“正在处理...”，见 [restore404-inflight-tree.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/restore404-inflight-tree.json:1) 与 [截图](D:/HCUP/vg-spec7/traces/analysis-baseline-device/restore404-inflight.png)。

ui-events 的 `observe_end_restore404` 时间为 10:37:02，它只是中途采样标签，早于最终网络响应；**不能用该标签证明网络已结束**。流程结束依据原始 response、连接关闭及 finished UI 快照。

### 第二组：有效目录、正确认证、云端无备份

这组排除了第一组目录不存在的因素。夹具校验虚拟 Basic 认证，目录 HEAD=200，两个备份路径 HEAD=404。保存新端点后，点击前无应用请求；仍只点恢复一次，从未点击继续。

| 时间（+08:00） | 事件／状态 | 原始证据 |
| --- | --- | --- |
| 10:38:48.838 | 点击「从云端恢复」 | [ui-events.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/ui-events.jsonl:1)、[click-restore-valid-directory.log](D:/HCUP/vg-spec7/traces/analysis-baseline-device/click-restore-valid-directory.log:1) |
| 10:38:49.131 | 新应用连接建立 | [directory-endpoint-requests.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/directory-endpoint-requests.jsonl:1) |
| 10:38:49.136 | HEAD 目录，认证匹配，200 | 同上 request id=2 |
| 10:38:49.145 | HEAD `/vg-spec7-dav/vg_spec7_baseline_20261017/backup.json.enc`，认证匹配，404 | 同上 request id=3 |
| 10:38:51.159 | HEAD `/vg-spec7-dav/vg_spec7_baseline_20261017/data/backup.json.enc`，认证匹配，404 | 同上 request id=4 |
| 10:38:53.164 后 | 空备份流程结束，无首个确认；显示“⚠️ 云端暂无备份：云端不存在备份文件，请先在其他设备上创建备份”，按钮恢复可用 | [valid-directory-finished-summary.jsonl](D:/HCUP/vg-spec7/traces/analysis-baseline-device/valid-directory-finished-summary.jsonl:1)、[截图](D:/HCUP/vg-spec7/traces/analysis-baseline-device/valid-directory-finished.png) |

该应用窗口为 **1 个 TCP 连接、3 个 HEAD 请求**，认证均匹配。请求期间无确认框，busy 禁用按钮，见 [valid-directory-inflight-tree.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/valid-directory-inflight-tree.json:1) 及 [截图](D:/HCUP/vg-spec7/traces/analysis-baseline-device/valid-directory-inflight.png)。没有 GET 或导入；不能把空备份路径下“未下载”外推为有备份时也会等待确认。

### 按矩阵标记本轮状态

`pass` 仅限本栏列明的观察范围，不代表整题通过。`blocked` 指当前基线入口无法到达后续动作，不是要求用户为本分析提供凭据；`not_run` 保留未测。

| 验收项 | 本轮状态 | 证据与限制 |
| --- | --- | --- |
| A01 | pass | 实际沿既有首页→设置→WebDAV 区域进入。 |
| A02 | pass | 输入／保存端点，后续相应端口实收请求；第一组重启后核对配置。 |
| A03 | pass | 输入／保存虚拟账号；第二组服务端认证匹配。 |
| A04 | pass | 输入／保存虚拟密码；第二组服务端认证匹配。 |
| A05 | pass（配置前置范围） | 同步密码实际输入／保存并重进核对；未测试该密码解密完整备份，不宣称解密通过。 |
| A06 | pass | 实际点击恢复入口。 |
| A07 | fail（实测） | 两组均在首框出现前发请求；空备份组最终未出现首框。 |
| A08 | fail（代码实证） | 第 215–220 行现有框无「继续」，而是下载后“确认恢复”；本轮空备份分支没有到达该现有框。 |
| A09 | fail（实测） | 两组未继续均建立应用连接。 |
| A10 | fail（实测） | 有效目录组未继续已发送 3 个 HEAD。 |
| A11 | not_run（真实备份下载） | 本轮备份不存在，未 GET；确认前下载／解密的可达代码分支已定位，未用真实加密备份实测。 |
| A12 | not_run（业务数据） | 未做业务数据全量快照或导入开始探针，不把“没有观察到导入”当作通过。 |
| B01 | fail（实测，复用 A07） | 入口不先显示所需确认。 |
| B02 | blocked | 没有可实际点击的首框「继续」。 |
| B03 | blocked | 无法通过指定继续动作启动；提前请求不能冒充本项通过。 |
| B04 | blocked | 本轮请求是授权前请求，不能充当继续后的正向证据。 |
| B05 | blocked（确认后链路） | 虽证实输入端点被使用，尚未验证从「继续」发往该端点的流程。 |
| B06 | blocked（确认后链路） | 已观察真实备份发现，但发生在授权前，不能算目标行为通过。 |
| C07／C09 的无备份／404 子集 | fail（门禁）／实测记录结果恢复 | 无备份与错误分支结果能结束、按钮恢复；仍先联网，不能整体判 pass。 |
| 其余 C01–C12 边界及有备份恢复 | not_run | 空／空格、取消、关闭、连点、已授权返回／重启、认证错误／5xx／超时／断网、完整下载解密导入等未运行。准备时保存后重进不等于这些门禁边界已全部测过。 |

未运行官方隐藏测试、未计算官方成绩，也未完成目标功能的本地验收。当前分析发现不自动触发代码修复；用户限定本阶段不改代码。


### 最终指纹与清理限制

[source-fingerprint-final.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/source-fingerprint-final.json:1) 确认设备操作后 299 个已跟踪文件仍与构建前一致，HEAD 和 Spec 哈希不变。[request-counts.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/request-counts.json:1) 保存两组计数。

18988 夹具通过本机 shutdown 接口优雅关闭；本轮两个 rport 和 Hypium forward 均移除，最终 fport ls 为 [Empty]，应用没有未结束请求。保留本题虚拟配置、共享应用数据及运行中的模拟器。

**清理限制：** 自动审批拒绝了停止旧 18987 夹具的 PowerShell 操作，返回原因仅为 `rejected: blocked by policy`，未绕过拒绝强杀。PID **55348** 仍监听 **127.0.0.1:18987**，设备映射已移除。详见 [cleanup-rejections.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/cleanup-rejections.json:1)、[remaining-fixture-listeners.json](D:/HCUP/vg-spec7/traces/analysis-baseline-device/remaining-fixture-listeners.json:1)。前者为明确标注的诊断摘录，不冒充完整原始工具返回；完整调用在原生会话记录中。这是一项遗留本地进程限制，不将其写成已清理。

## 10. 过程与来源边界

四个真实角色在本题分析范围内分别负责需求拆解、基线结构、未修改构建与独立设备验证，主 Agent 整合两份文档并维护状态。未修改业务代码或为了成功降低断言，未访问题包／其他题工程／上游修复历史，未外部提交或发布。

使用 harmony-task-flow 进行调度，hmos-arkts-syntax-checker 仅执行构建部分；遵守用户“不修代码”优先于技能自动修复建议。hmos-arkts-knowledge-retriever 的 search_docs.py 因本地 references/doc_index.json 缺失而失败，随后直接读取本技能的 [async-concurrency-overview.md](C:/Users/22580/.codex/skills/hmos-arkts-knowledge-retriever/docs/ArkTS-Language-Guide/Concurrency/async-concurrency-overview.md:87) 支撑 await 顺序分析；它不是本题 HTTP 运行证据。没有为缺失索引去检索上游实现。

原始构建与设备操作日志位于 `traces/analysis-baseline-build/`、`traces/analysis-baseline-device/`。主／子会话登记及事件在 [state.json](D:/HCUP/vg-spec7/workflow/state.json:1)、[events.jsonl](D:/HCUP/vg-spec7/workflow/events.jsonl:1)；原生记录快照仅反映导出当时，不宣称包含之后的内容。本阶段结束后只允许后续明确请求再进入设计／编码；不能将当前状态标成目标功能已本地验收。

