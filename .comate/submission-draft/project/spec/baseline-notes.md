# vg-spec8 基线现状

本文件仅完成 `spec-harness/0-analyze.md` 的分析任务，不代表功能已实现或通过验收。所有源码路径相对 `D:/HCUP/vg-spec8`。证据分为 **SPEC_EXPLICIT**（需求原文）、**CODE_EVIDENCE**（本题源码）、**RUNTIME_EVIDENCE**（本次重新构建、安装与操作）和 **INFERENCE**（推导）；未实测的内容明确标注。

## 1. 基线快照与分析边界

- HEAD：`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，与 `spec/metadata.json:2` 一致。本轮记录 HEAD，不新增 Git tag、不切换版本。
- Spec SHA-256：`256038a2336dce8956585ff92c18e7ec9e5cd79d736f7b7f56021dbf646af592`；metadata SHA-256：`92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。实读记录：`logs/analysis-baseline/input-hashes.txt`。
- 开始时已有 `AGENTS.md` 修改，以及本题初始化资料等未跟踪文件；没有业务代码差异。开始快照：`logs/analysis-baseline/status-before.txt`、`source-fingerprint-before.json`。结束后的源码指纹核对见第 9 节。
- 只使用本题资料和允许的公共工具。未访问来源项目、题包、其他题工程或初始化总览会话的实现内容。初始 `logs/baseline-build.log` 只作准备记录；本次运行结论以 `logs/analysis-baseline/` 的新证据为准。

## 2. 重新构建、安装与启动

以下是本次已执行命令；每个构建或设备 PowerShell 进程先加载本工作区环境：

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
& D:/HarmonyDev/DevEcoStudio-6.1.0/tools/hvigor/bin/hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell aa force-stop io.qzz.weiyu
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu
```

| 项目 | 本次结果与证据 |
| --- | --- |
| 干净构建 | 成功，exit 0。完整日志 `logs/analysis-baseline/build-clean-assembleHap.log`；命令及结果为 `build-command.txt`、`build-result.json`。未为消除告警修改代码。 |
| 产物 | `entry/build/default/outputs/default/entry-default-unsigned.hap`；SHA-256 `1695ccc7d351472d2472a498ae9ed31a6f75ac11f8a861e20ab2060bc3452d6c`；记录 `logs/analysis-baseline/hap-sha256.txt`。 |
| 安装 | `install -r` 成功，exit 0，保留既有数据；`logs/analysis-baseline/install.log`、`install-result.json`。没有卸载或清空应用。 |
| 启动 | `EntryAbility` 启动成功，exit 0；`logs/analysis-baseline/start.log`、`start-result.json`，首屏截图/UI 树 `01-start.png`、`01-start.json`。 |
| 工具 | DevEco 6.1.0.860；Hvigor 6.23.7，Node v18.20.1，JBR 21.0.8，hdc 3.2.0c，Hypium 6.1.0.210；实读 `logs/analysis-baseline/tool-versions.txt`、`hypium-methods.txt`、`sdk-environment.txt`。 |
| 设备 | `127.0.0.1:5555`；API 23，系统镜像 `6.1.0.115`、1308×2880，版本/分辨率检查与框架内置值一致。机型参数仅返回 emulator，dpi 读取失败，机型及 560dpi **未独立验证**。详见 `logs/analysis-baseline/environment-check.txt`、`device-api.txt`、`device-model.txt`、`device-dpi.txt`；不等于官方评分。 |
| 共享设备 | 安装前发现设备残留另一题测试画面；用户明确答复“可以，当前已空闲”后才安装。本题运行证据从本题 HAP 安装后开始，安装前画面不作本题功能证据。 |

构建使用工程声明的 API 22 兼容/目标版本（`build-profile.json5:7-8`），运行校验使用 API 23 模拟器。**既有告警共 764 条带源码定位的 ArkTS 警告**，逐条包含文件、行列与原文，完整清单：`logs/analysis-baseline/build-warnings.csv` 和 `build-warning-index.txt`；摘要为 `build-warning-summary.txt`。

| 告警类别 | 数量 |
| --- | ---: |
| Function may throw exceptions. Special handling is required. | 498 |
| showToast deprecated | 132 |
| back deprecated | 32 |
| pushUrl deprecated | 27 |
| getContext deprecated | 25 |
| showDialog deprecated | 11 |
| getParams / SetOrCreate deprecated | 6 / 6 |
| decode deprecated | 5 |
| createAudioPlayer / play / src deprecated | 3 / 3 / 3 |
| animateTo / release deprecated | 2 / 2 |
| arkts-no-classes-as-obj | 2 |
| 可选 @Prop text / duration | 1 / 1 |
| arkts-no-globalthis / arkts-limited-esobj | 1 / 1 |
| getLength / encode / setPasteData deprecated | 1 / 1 / 1 |

另有一条 ArkTS FAQ 提示和 `No signingConfig found for product default`。此次生成 unsigned HAP 并成功安装；没有签名配置变更。

## 3. 入口位置与本次操作

**CODE_EVIDENCE：正常入口链**如下；WebDAV 是设置页内部的分区，没有独立的 WebDAV 路由。

| 步骤 | 源码定位 |
| --- | --- |
| Ability 加载首页 `pages/Index` | `entry/src/main/ets/entryability/EntryAbility.ets:23-41`；Ability 声明 `entry/src/main/module.json5:29-32`。 |
| 首页顶部齿轮回调 push `pages/SettingsPage` | `entry/src/main/ets/pages/Index.ets:320-329`；齿轮点击 `entry/src/main/ets/pages/index/components/TopNavigation.ets:69-79`。 |
| 设置列表点击「WebDAV 配置」 | 数据标识 `sync`，`entry/src/main/ets/pages/SettingsPage.ets:40`；点击赋值 `activeSectionId=item.id`，同文件 `507-512`。数据 id 不是 UI id。 |
| 设置内显示同步分区 | `entry/src/main/ets/pages/SettingsPage.ets:427-442` 创建 `SettingsSyncSection`；列表/分区切换为 `483-525`。 |
| 「从云端恢复」 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:507-516`。 |
| 分区返回到设置列表，再返回首页 | `entry/src/main/ets/pages/SettingsPage.ets:172-179`、`464-467`。 |

**RUNTIME_EVIDENCE：本次确实走过正常入口**。安装本题 HAP 后启动到首页，Hypium 点击顶部「⚙」，进入设置列表，再点击「WebDAV 配置」，滚动到手动操作区；首页和设置列表见 `logs/analysis-baseline/01-start.png/.json`、`02-settings.png/.json`，配置和操作区见 `03-sentinel-config.png/.json`、`05b-actions-visible.png/.json`。逐次命令、触摸与时间戳在 `device-actions.jsonl`。这是保留既有数据的覆盖安装，首次安装的隐私/引导路径**未验证**。

本次只用本地哨兵配置：endpoint `http://127.0.0.1:18988/dav/`、测试账号 `vg_spec8_observer`、remoteRoot `/vg_spec8_observation`；密码为本地测试值。未复用旧账号或向旧地址发出测试请求。关闭自动同步并保存测试配置后建立连续观察窗口；本题使用独立 hdc rport 转发到主机 mock。配置状态见 `03-sentinel-config.png/.json`、`05-saved.png/.json`；mock 原码与请求原始日志为 `mock_webdav.py`、`mock-requests.jsonl`。

| 操作/观察 | 本次实际结果 | 证据 |
| --- | --- | --- |
| 点击前建立基点 | mock 请求计数为 0；未点击测试连接、立即同步或立即备份。 | `logs/analysis-baseline/pre-restore-counter.json`；`device-actions.jsonl`。 |
| 首次点击「从云端恢复」 | 2026-10-16 21:50:35（Asia/Shanghai）点击后，21:50:35.637803 服务端收到 `HEAD /dav/vg_spec8_observation`，返回 404。此前和此后均未点击「继续」。非零真实请求同时证明服务可达、计数链路有效，无需把零日志当作联网能力正控。 | `mock-requests.jsonl` 第 1 条；`device-actions.jsonl` 的 restore 点击时间。 |
| 请求进行中的 UI | 没有第一层「取消／继续」弹窗；五个操作按钮均显示「处理中...」且 UI 树 enabled=false，结果区域显示「正在处理...」。 | `06-first-restore-inflight.png`、`06-first-restore-inflight.json`。 |
| 忙时同位置再点 | 该时点计数仍为 1。后续 HEAD、PUT 属于第一次操作的目录预检链，不能据新增计数推定重复触发了第二次恢复。此观察不等于快速连点完整用例已通过。 | `device-actions.jsonl`、`mock-requests.jsonl`；调用依据 `WebDavSyncManager.ets:280-339`。 |
| 首次失败后再次点击恢复 | 首次失败返回后按钮重新可用；再次点击仍直接发请求。两次操作合计 6 个请求（HEAD×4、PUT×2，mock 均返回 404），最终计数记录明确 `continueEverClicked=false`、`cancelEverClicked=false`。这不是“取消后重开”用例。 | `pre-second-restore-counter.json`、`09-second-restore-inflight.png/.json`、`10-final-idle.png/.json`、`final-counter.json`。 |
| 目标取消步骤 | 第一层未出现，无法点击其「取消」、验证取消后重开或反复取消；这些细项标记 `not_run`，前置能力缺失。 | 上述 UI 树/截图；对应验收 A3—A8、A10—A11、A13 等。 |

由此，A1 的正常入口有实测支持；A2 的第一层确认显示不满足，A9 的首次未继续零请求不满足。不能把请求失败后入口恢复可点击当作“取消后入口可用”通过，也不能把未触达的 D2 取消表现当作本题第一层证据。

## 4. 相关组件、模型、状态和持久化

| 对象 | CODE_EVIDENCE：当前位置与写法 |
| --- | --- |
| 配置页面状态 | `entry/src/main/ets/pages/SettingsPage.ets:114-129` 持有 endpoint/username/password/syncPassword/remoteRoot、密码显隐、自动同步开关等 `@State`；`427-442` 以 `$webdav...` 向子组件传递。 |
| 同步区状态 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:23-47` 使用配置 `@Link`，结果与 `webdavBusy` 为局部 `@State`。`446-516` 的保存/连接/同步/备份/恢复共用 busy，忙时都显示「处理中...」并禁用。 |
| 恢复包装 | 同文件 `140-156`：guard → busy=true →「正在处理...」→等待 50ms→执行操作→结果/toast→finally busy=false。`113-121` 用 120 秒 Promise.race 超时包装。 |
| 配置模型 | `entry/src/main/ets/sync/webdav/WebDavCommon.ets:49-98` 的 `WebDavSettings` 包含五项配置及 requireRemoteRootExists，toJSON 序列化。 |
| 管理器 | `entry/src/main/ets/sync/WebDavSyncManager.ets:75-121` 是单例，持有配置、manifest、布局缓存及管理器 status；其 RESTORING/IDLE/ERROR 不等于页面 busy（同文件 `471-498`）。 |
| 配置保存/回填 | 页面初始化读取管理器并赋给 UI：`entry/src/main/ets/pages/SettingsPage.ets:149-168`、`190-208`。保存按钮构造配置并 setSettings：`entry/src/main/ets/pages/settings/SettingsSyncSection.ets:99-110`；管理器写入并清布局缓存：`entry/src/main/ets/sync/WebDavSyncManager.ets:111-121`；初始化读取为同文件 `129-157`。 |
| 本地存储 | `entry/src/main/ets/utils/WebDavStateStore.ets:62-81`、`120-151` 使用 Preferences `webdav_state_store`；`261-300` 对设置 JSON 保存主键、备份键、备份时间并 flush，可从备份回填主项。本轮不改存储策略。 |
| 输入与已保存值差异 | TextInput onChange 只改链接值，`SettingsSyncSection.ets:262-301`；恢复 `164-165`、`199-200` 没有先保存输入，使用管理器已加载的配置。立即同步先保存（`177-187`），测试连接会 setSettings（`234-249`）。 |
| 自动同步 | `entry/src/main/ets/entryability/EntryAbility.ets:49-57` 每次前台触发；`entry/src/main/ets/sync/AutoWebDavSyncManager.ets:28-85` 根据配置、开关、时间间隔执行请求，有独立 busy。开关默认 true、间隔 6 小时，`entry/src/main/ets/utils/WebDavStateStore.ets:170-213`。 |

## 5. 当前恢复顺序、网络服务及可复用交互

**CODE_EVIDENCE：当前顺序**：`SettingsSyncSection.ets:164-165` 的 webdavRestore → `140-156` busy 包装 → `199-200` downloadBackupPlain(false) → `205-208` previewImport → `215-222` 原生「⚠️ 恢复确认」弹窗，按钮「取消」「确认恢复」。这条链没有 Spec 的第一层「取消／继续」确认。

| 阶段 | 源码证据与影响 |
| --- | --- |
| 配置校验 | `entry/src/main/ets/sync/WebDavSyncManager.ets:160-170`、`471-473`；配置不足可直接返回且不出现弹窗，因此无配置测得零请求不能证明取消逻辑正确。 |
| 目录预检 | 同文件 `280-339`、`345-364`：缓存/根目录可跳过，否则可先 HEAD；404/探测分支还可能 PUT/DELETE。只统计 GET 会漏请求。 |
| 下载 | `entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:68-117`：先 HEAD 备份/旧路径，可能保存本地 snapshot，然后 GET 并解密。`96-98` 的本地 snapshot 是确认前可能已有的本地写入。 |
| 网络发送 | `entry/src/main/ets/sync/webdav/WebDavClient.ets:33-38`、`109-146`，最终 `http.createHttp()` / `request.request()`；`78-82` 名为 mkcol 的方法实际 PUT `.keep`。 |
| 已有后置取消 | `entry/src/main/ets/pages/settings/SettingsSyncSection.ets:224-230` 的 index 0 或 catch 返回 `ok('已取消恢复')`，外层 `155-156` finally 复位 busy；静态上没有“自建 Promise 的取消忘记 resolve”证据。此处取消不会撤销此前网络。 |
| 真正导入 | 同文件 `228` 才调用 importPlainBackup；经 `entry/src/main/ets/sync/WebDavSyncManager.ets:502-506` 到 `entry/src/main/ets/sync/webdav/WebDavBackupManager.ets:174-185`。 |

**可复用的本题基线实现**：保留既有 Index→SettingsPage→sync 的入口、父 `@State`/子 `@Link` 配置流、WebDavSyncManager 与 Preferences 存储，以及 busy guard/finally 处理方式；本地备份导入已有原生确认取消结构，可对照 `entry/src/main/ets/pages/settings/SettingsBackupSection.ets:109-191`。这是可复用现状清单，并非已批准实施方案。

两个容易混淆的组件：`entry/src/main/ets/pages/settings/SettingsSyncDialog.ets:7-17` 是 JSON 粘贴导入弹层；`entry/src/main/ets/pages/index/HomeTabContent.ets:419-432` 的「继续」属于首页 API 未配置提示。两者均不证明 WebDAV 第一层确认已经存在。

**INFERENCE，未复现风险**：`SettingsSyncSection.ets:113-121` 的超时不取消原操作，也未清定时器；不能把它记成此次已发生的晚到导入或取消失败。

## 6. 与 Spec 的缺失项

| Spec 目标 | 已有能力与缺口 |
| --- | --- |
| 场景一：第一层确认打开并取消关闭 | Spec `spec/requirement.md:7-14`；基线链 `SettingsSyncSection.ets:199-222` 在下载后才确认，缺少网络前第一层及其取消处理。 |
| 场景二：取消后按钮可再次打开 | Spec `spec/requirement.md:20-27`；已有后置弹窗的 finally/enabled 可复用（`SettingsSyncSection.ets:140-156`、`507-516`），不能据此将第一层重开判为通过。 |
| 场景三：未点击「继续」前零请求 | Spec `spec/requirement.md:33-40`；`SettingsSyncSection.ets:200` 和 `WebDavSyncManager.ets:471-484` 显示缺少网络同意门槛。实际网络观察见第 3 节。 |

## 7. 前置环境与测试数据

- **CODE_EVIDENCE**：设置入口没有本题专用账号登录门槛；首次启动可能有隐私同意或引导，`entry/src/main/ets/pages/Index.ets:116-137`、`285-299`。这与 WebDAV 服务端账号不同。
- **CODE_EVIDENCE**：基线现有后置预览需要已保存的 endpoint、username、password、至少 4 位同步密码（`WebDavSyncManager.ets:160-170`），还需要服务端可读备份、正确解密及合法预览数据（`WebDavBackupManager.ets:68-117`；`SettingsSyncSection.ets:201-208`）。本轮没有真实服务端凭据，也不执行覆盖本地数据的恢复。
- **INFERENCE**：Spec 第一层取消阶段本身不应以下载成功为前置；对无配置/空白配置是否也无条件弹第一层，Spec 未明示，列入 `acceptance.md` 待确认项。
- 场景三必须有可达、可计数的 WebDAV 测试端点，并隔离自动同步；空配置或端点不可达时的零计数不是充分证据。HTTP 方法应全部计入，包括 HEAD、GET、PUT、DELETE 及重定向后的请求。本轮本地 mock 已能收到真实请求，足够暴露提前联网；没有可解密有效备份，不能据此验证 D2 预览或后续成功导入。

## 8. 测试可观测性风险

| 位置 | 风险与依据 |
| --- | --- |
| 首页齿轮/设置列表项 | `TopNavigation.ets:69-79` 和 `SettingsPage.ets:487-517` 无目标稳定 `.id()`；`item.id='sync'` 是数据字段。需在实现时补 `.id()`。 |
| 恢复按钮及结果 | `SettingsSyncSection.ets:446-525` 无 id；busy 时多个按钮同名「处理中...」，恢复原文消失。需在实现时补 `.id()`。 |
| 五项输入/自动同步 | `SettingsSyncSection.ets:262-336`、`353-357`、`380-400` 无 id；「显示／隐藏」重复，单按文本有歧义。需在实现时补 `.id()`。 |
| 恢复确认 | `SettingsSyncSection.ets:215-222` 只提供原生 title/message/buttons，调用处没有组件 id；其他弹层也有「取消」。需对新第一层补可稳定定位的控件，并记录原生弹窗如无法加 id 时的窗口限定选择器。 |
| 根节点 | `SettingsPage.ets:549` 和 `Index.ets:360` 的根 id 带 themeRefreshToken，不应当作稳定目标控件 id。 |

建议选择器名称、观察窗口和逐项断言见 `spec/acceptance.md`；建议 id 尚未写入基线。不得把坐标或同名第 N 个按钮当作最终稳定验收接口。

## 9. 本轮验证范围与记录

本轮已重新构建、安装、启动并实际操作正常入口，完成最小网络反例观察。第一层不存在，依赖它的取消/关闭/反复取消步骤为 `not_run`；空输入/纯空白、有效备份预览、本地哨兵数据不变、120 秒超时、返回重进和应用重启等扩展用例未执行。未运行官方隐藏测试，也不以本次分析或构建成功宣称功能验收通过。

| 当前基线状态 | 验收项 | 判定边界 |
| --- | --- | --- |
| pass | A1 | 仅证明既有正常入口实际可达。 |
| fail | A2、A9、A12、A17 | 第一层缺失、未继续即请求，以及进入实际网络忙态，均有服务端/UI 证据。 |
| not_run | A3—A8、A10—A11、A13—A16、A18—A19；U1—U6 | 取消/重开前置缺失或未安排扩展验证；不能把未测判为通过。 |

观察脚本 `restore-observe` 的退出码为 **1**，因为正确检测出第一层显示和未继续零请求两项断言失败；这与基线构建/安装的退出码 0 分开。对应 `logs/analysis-baseline/restore-test-process-result.json`、`restore-observation-result.json`。观察工具自身曾遇到滚动方向参数大小写及 rport 列表命令错误，保留原始失败后按本地帮助修正（`swipe-actions.log`、`rport-before.txt`），没有改产品代码或放宽 Spec 断言。

开始/结束工程指纹：`logs/analysis-baseline/source-fingerprint-before.json`、`source-fingerprint-after.json`，主 Agent 独立比较的 298 个文件完全一致；`tracked-diff-after.txt` 仍仅列开始前已有差异 `AGENTS.md`，没有业务/构建配置代码修改，也没有新增会参与构建的业务源文件。本阶段业务缺陷仅记录，不修复。

本轮独立验证交接：`workflow/verification/analysis-01.md`；需求复审、静态映射和只读实现审计分别为 `workflow/requirements/analysis-01.md`、`workflow/design/baseline-map-01.md`、`workflow/implementation/read-only-audit-01.md`。这些是过程证据，用户交付文档为本文件和 `spec/acceptance.md`。

本题临时 reverse 转发 `18988` 已移除，其他转发保持原状（`logs/analysis-baseline/forward-before-cleanup.txt`、`forward-after-cleanup.txt`）；主机 mock 已停止，`mock-stop-result.json` 记录 remainingListeners=0。设备保留本题本地哨兵配置，自动同步为关闭状态；没有还原不明旧端点，也没有删除既有学习数据。最终源码一致性检查见 `source-integrity-result.json`。模拟器已可供后续任务使用。
