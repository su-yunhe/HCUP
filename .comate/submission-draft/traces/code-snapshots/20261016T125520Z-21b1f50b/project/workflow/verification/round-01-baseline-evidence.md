# vg-spec9 未修改基线独立验证证据

执行角色：baseline_verification；原生会话 `01a1447f-6645-73d2-853c-540c0da81e11`（环境 CODEX_THREAD_ID，保存于 `traces/baseline-analysis/preflight-summary.json`）。执行日期 2026-10-16，时间均为主机 +08:00。仅完成 0-analyze 基线调查，不实现功能，不修改生产代码、Spec 或测试工程。本记录供主 Agent 编写 `spec/acceptance.md`、`spec/baseline-notes.md`；它不是官方测试结果。

## 结论与逐项状态

基线可以构建、覆盖安装和启动。通过正常 UI 进入 WebDAV 配置分区，点击一次「立即同步」能触发真实请求并使按钮忙碌，但真实请求等待期间未渲染 Spec 要求的 ArkUI `LoadingProgress`。错误响应后按钮恢复。成功同步全链路未测试。

| 项目/对应需求 | 状态 | 观察、证据及边界 |
|---|---|---|
| 未修改基线构建、安装、启动（环境前置） | pass | clean 后 CompileArkTS 确实执行；构建、安装、启动均退出 0；见 02、03 日志。不是 Spec 全部通过。 |
| 场景一第 1 步：进入 WebDAV 配置并填写输入 | pass | 首页 ⚙ → 设置 →「WebDAV 配置」；五个配置输入均可填写；见 `launch.json`、`settings-menu.json`、`webdav-initial.json`、`webdav-test-config.json`。仅证明入口和表单可用。 |
| 场景一第 1 步：可完整成功读写的 WebDAV 服务前置 | not_run | 本轮服务是可到达、验证本轮测试 Basic Auth 的 HTTP 延迟错误夹具，主动返回 403；不能把它等同完整可写 WebDAV 或完整同步成功。 |
| 场景一第 2、3 步：手动点击进入忙碌状态 | pass | 一次点击后五个 Button 均为「处理中...」、enabled=false；见 `sync-during.json`、`sync-during-second.json` 和同名 PNG。仅覆盖本轮错误流程。 |
| 场景一第 4 步、场景二第 2 步：ArkUI LoadingProgress | fail | 两个请求中采样的完整树 LoadingProgress 数均为 0，截图亦无加载指示器；`SettingsSyncSection.ets` 全文检索 LoadingProgress 无匹配。负向请求流程中的缺失已复现；成功流程仍未验证。 |
| 场景二第 3、4 步；场景三第 3 步：向配置端点启动真实请求 | pass | 服务实收两次 HEAD 和一次 PUT，均 authMatchesFixture=true；见 `webdav-requests.jsonl`。这只证明同步预检请求已经发生，不证明增量下载/上传成功。 |
| 场景二忙碌状态与实际请求区间相交 | pass | 19:41:40.592 请求开始至 19:41:52.593 首个响应之间的两次 UI 采样均为 busy；完整时间见 `sync-observations.json`、`ui-commands.jsonl`。 |
| 场景二/三要求的加载指示与真实请求绑定整体 | fail | 有真实请求及 busy，但上述 LoadingProgress 缺失，不能将忙碌按钮当作要求的 ArkUI 组件。 |
| 错误结束后 busy 恢复（合理推导） | pass | 19:42:04.712 最后 403 完成后，19:42:08.511 开始捕获的 `sync-final.json` 中五个操作按钮均 enabled=true，立即同步恢复原文案，显示明确错误。 |
| 首次安装隐私/引导路线 | not_run | 保留已有应用数据，冷启动进入 Index。源码可证隐私同意后、hasSeenOnboarding=false 时才 push OnboardingPage；没有重置数据或伪称新安装验证。 |
| 成功同步、成功终态、完整下载/合并/上传 | not_run | 本轮预检 403 提前返回，未进入成功数据链路。 |
| 空/空格配置、取消/离开、重复/快速点击、跨页重进、重启恢复、超时、其他网络错误、同一 busy 下的其他操作 | not_run | 本轮仅必要基线检查；不把源码 guard/finally 当这些运行测试已经通过。 |
| 本轮反向端口清理 | blocked | 自动审批拒绝原始清理命令，服务已停止但映射保留；见后文。 |

## 基线、环境和产物

- HEAD：`a22f32b07bf81c6dde4367e2543ebac29186cbc1`。
- Spec SHA256：`C6236994E253C6DE9F6DECD99D7C0637620027AC16CE3699154796CBA7A5EDBF`。
- metadata SHA256：`496950D171E032FE6F10CF76FD485341F4F293B6F162857D60A46BD98756F660`。
- 生产/配置受跟踪文件清单共 269 项（entry、AppScope、hvigor、material、scripts 和根构建/依赖配置）；前后逐文件 SHA256 相同，差异 0。前后清单 JSON 的 SHA256 均 `7BA986ACC0D3C664565D1A3BC42846586CC44D757A3480980CFFDBC48B149FF1`。见 `source-fingerprint-before.json`、`source-fingerprint-after.json`、`08-final-integrity.log`。
- 初始及最终 `git diff --name-status` 均仅 `M AGENTS.md`，这是已有流程规则；暂存无差异。未生成生产修复。
- Windows PowerShell 7.6.5；DevEco 6.1.0.860；SDK API 23；Node 18.20.1；JBR/OpenJDK 21.0.8；Python 3.12.3，实际 Python 来自 `D:/HCUP/common/.venv/Scripts/python.exe`，Hypium 6.1.0.210。环境脚本 banner 中旧 Python 路径未被用作程序来源。每次 PowerShell 工具进程均加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。
- 本次设备唯一 `127.0.0.1:5555`。安装前前台 `io.qzz.weiyu/EntryAbility`，与本题 AppScope/app.json5 的 bundle 相同。无别题显式占用迹象。API 23；系统 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`；model 参数仅返回 `emulator`，device type=phone；截图/窗口树 1308×2880。DPI 参数查询不存在，具体虚拟机型、560 DPI 未独立确认，不能据此声称完整环境一致。
- HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，8,937,956 字节，SHA256 `6397218E05107233A02EAF9154367AF16EED5843B09A1C9AB1224466793364A8`；未签名，模拟器安装成功。

## 命令、退出码、原始日志

均在 `D:/HCUP/vg-spec9` 执行，每条 PowerShell 进程先加载本题环境脚本；以下路径前缀为 `traces/baseline-analysis/`。

| 动作/命令 | 退出码/结果 | 原始证据 |
|---|---|---|
| git rev-parse HEAD；git status/diff；Get-FileHash；hdc list targets；aa dump --mission-list | 预检进程 0 | `01-preflight.log`、`preflight-summary.json` |
| `hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` | 0，BUILD SUCCESSFUL，CompileArkTS 12.075s，总计 16.707s | `02-build-command.log`、`build-raw.log`、`build-exit.txt` |
| `hdc install -r entry/build/default/outputs/default/entry-default-unsigned.hap` | 0，install bundle successfully | `03-device-install.log` |
| `hdc shell aa force-stop io.qzz.weiyu`；`hdc shell aa start -a EntryAbility -b io.qzz.weiyu` | start=0，均成功文案 | `03-device-install.log` |
| `hdc shell uitest dumpLayout/screenCap ...`；`hdc file recv ...` | 逐条记录 0 及原始响应 | `ui-commands.jsonl`；初始捕获见 `04-ui-initial.log` |
| `python workflow/verification/baseline_probe.py serve` | 已监听，结束时 Ctrl-C，进程退出 1 | 服务标识/脚本及 `webdav-requests.jsonl`；终止原因非业务崩溃 |
| `hdc rport tcp:18769 tcp:18769` | 0，Forwardport result:OK | `05-configure-test.log` |
| `python workflow/verification/baseline_probe.py configure` | 1，最后远端目录输入因键盘遮挡未找到 | `configure-ui-raw.log`、`05-configure-test.log`；是自动化前置失败，未点击同步，非产品缺陷 |
| 收起键盘后 `python workflow/verification/baseline_probe.py finish-config` | 0，完成远端目录输入，未重跑无关字段 | `configure-root-raw.log`、`configure-root-exit.txt` |
| `python workflow/verification/baseline_sync_once.py` | 0（证据采集脚本正常结束；其退出码不代表 Spec 通过） | `06-sync-test-command.log`、`sync-test-raw.log`、`sync-observations.json` |
| 最终额外捕获 `python workflow/verification/baseline_ui.py dump sync-final` | 0 | `sync-final-ui.log`、`ui-commands.jsonl`、`sync-final.json/png` |
| `python workflow/verification/summarize_baseline.py` | 0 | `build-warning-summary.json`、`build-warning-index.md/json` |
| `rg -n 'LoadingProgress|\.id\(' entry/src/main/ets/pages/settings/SettingsSyncSection.ets` | 1，无匹配 | `09-source-runtime-index.log` |
| 最终指纹核对 | 0，269 文件差异 0 | `08-final-integrity.log` |

早期 `hdc file recv` 使用正斜杠绝对 Windows 目标路径时，hdc 错误拼接 cwd 并报告打开文件失败；随后改为本题相对目标，成功取回同一安装前原始 JSON/PNG，保留早期失败于 03 日志。`hdc shell uitest -h` 返回 Illegal argument 并打印帮助；不影响后续使用实际 dumpLayout/screenCap 子命令。工具定位中一次 rg 包含本题 system-config 初始化快照并返回构建命令/skill 片段，未访问初始化总览会话，未以这些片段作为功能证据；功能结论均来自本轮构建、运行与基线源码。

## 完整已有告警

`clean` 后 `CompileArkTS` 实际执行，非全 UP-TO-DATE。统计口径：759 条带 `File:` 的编译诊断，另计 1 条非文件签名告警（不把 FAQ 提示重复计数）。每条源码位置、原始文案、`build-raw.log` 行号完整保存在 `build-warning-index.md/json`。

| 类别 | 数量 |
|---|---:|
| Function may throw exceptions. Special handling is required. | 505 |
| deprecated API（逐 API 原文见完整索引） | 249 |
| Classes cannot be used as objects (arkts-no-classes-as-obj) | 2 |
| Usage of ESObject type is restricted (arkts-limited-esobj) | 1 |
| @Prop text cannot be optional | 1 |
| @Prop duration cannot be optional | 1 |
| No signingConfig found for product default（非文件） | 1 |

本轮未修告警、未改 SDK 声明、未安装/修改项目依赖。

## 实际导航、状态、服务与可观测性

安装前应用已经运行在 WebDAV 配置分区，保留本地数据。初始已有本地端点和非空掩码凭据、远端目录 `/run04/16/fast-double`，页面还残留先前「✅ 备份已上传」文字；它不是本轮成功证据。未访问或调用该旧服务，未读取真实用户密码。重装后 force-stop/start 进入 Index，无隐私/首次引导弹出，首页显示未选择词书。

本轮实际点选首页右上角 ⚙，到设置总览，再点「WebDAV 配置」。目标是 `pages/SettingsPage` 的内部分区，不是独立 WebDAV 路由或弹窗：`Index.ets:325` push `pages/SettingsPage`；`SettingsPage.ets:41` section id=`sync`；`:528` 点击赋值 activeSectionId；`:447` 渲染 SettingsSyncSection。返回逻辑 `SettingsPage.ets:173` 先清分区，再由 `:178` router.back。首次引导的源码前置见 `Index.ets:115`（privacy consent、hasSeenOnboarding），路由调用 `:136`；首次新装 UI 未验证。

输入结构、密码字段、操作卡在 `pages/settings/SettingsSyncSection.ets:348`、`:370`、`:439`、`:538`。运行可按五个唯一 TextInput hint 选择：`https://dav.example.com/dav/`、`username`、`password`、`sync password`、`/weiyu_sync`。目标分区缺少 `.id()`；两个「显示」按钮同名。idle 时「立即同步」唯一，busy 时五个操作按钮全部同名「处理中...」且均无 id；自动化无法仅凭该 busy 文案唯一定位手动同步按钮。普通树还包含系统状态栏，不应按任意第一个 Text/Button 断言。

`SettingsSyncSection.ets:43` 为 `@State webdavBusy`；`:289` 的 webdavSyncNow 先 guard 重入、置 busy，再保存配置并调用 `WebDavSyncManager.syncIncremental()`（`:308`），finally `:316` 清 busy。按钮 `:578` 至 `:586` 绑定该状态。配置保存 `:100` 至 `:111` 把结果文案覆盖成「✅ WebDAV 设置已保存」，因此本轮 busy 时截图中结果文本是已保存；不应将该文字当同步完成。以上为源码事实与本轮截图一致，未测试所有异常/生命周期分支。

实际配置写入通过 WebDavSyncManager.setSettings（`sync/WebDavSyncManager.ets:124`）至 WebDavStateStore；`utils/WebDavStateStore.ets:63` 使用 `webdav_state_store`，`:67` 设置 JSON 及备份 key，`:128` 获取 Preferences，`:150` 保存。无需登录外部账号即可进入 UI。网络由 `WebDavClient.ets:131` 附 Basic Auth，`:143`/`:144` 连接 15s/读取 20s 超时，`:149` request.request。同步启动和预检分别在 `WebDavSyncManager.ets:672`、`:693`。成功路径的数据文件操作本轮未验证。

## 本地延迟错误夹具与缺陷最小复现

夹具脚本 `workflow/verification/baseline_probe.py`，仅监听主机 127.0.0.1:18769，通过本轮新建 rport 暴露给设备。填写本轮独立测试账号、测试密码、测试同步密码、`remoteRoot=/vg-spec9-round01`；未使用原有凭据。所有请求日志仅记录 authMatchesFixture 布尔值，不记录 Authorization 原文。HEAD 等待 12s 后返回 403；PUT 等其他方法立即 403；夹具不提供完整 WebDAV 成功实现。

| 主机时间 +08:00 | 请求/响应 |
|---|---|
| 19:41:40.592918 | HEAD /vg-spec9-round01，请求收到，authMatchesFixture=true |
| 19:41:52.593760 | 第一次 HEAD 响应 403 |
| 19:41:52.642762 | 第二次 HEAD /vg-spec9-round01，authMatchesFixture=true |
| 19:42:04.643987 | 第二次 HEAD 响应 403 |
| 19:42:04.710889 | PUT /vg-spec9-round01/.probe_1792150912648.txt，authMatchesFixture=true |
| 19:42:04.712016 | PUT 响应 403 |

复现操作：在正常设置入口填写上述本地测试配置，向下滚动至「立即同步」，点击一次，在 HEAD 尚未返回时 dumpLayout 并截屏。

- 期望：真实同步请求运行期间存在 ArkUI LoadingProgress，loading 与 busy/请求绑定。
- 实际：`sync-during.json`、`sync-during-second.json` 中 LoadingProgress=0，五个同名忙碌按钮禁用，截图无 loader；服务端确实已有请求。最终 `sync-final.json/png` 显示「⚠️ WebDAV 连接失败：STEP remoteRoot PUT 403: 权限不足（目录可能不可写）」，同步按钮恢复。
- 关联需求：场景一第 4 步、场景二第 2 步及概述、场景三加载反馈与真实请求绑定。
- 归因假设：既有 webdavBusy 只绑定按钮文案/颜色/enabled，目标构建树未包含 LoadingProgress。证据强度高：两次完整 UI 树、截图、真实服务时间线、基线源码相互支持；成功链路、其他屏幕/主题/异常未覆盖。
- 建议：分析完成后由主 Agent 在方案/编码阶段决定将 LoadingProgress 绑定既有忙碌状态并保留真实 syncIncremental 调用；本阶段不修。

采集脚本的已知限制：`baseline_sync_once.py` 在看到第一个服务响应后提前捕获 `sync-after`，此时第二个 HEAD 仍待响应，因此原始 `sync-observations.json` 的 `busyRestoredAfterError=false` 仅为中途采样，不能判定恢复失败。原始证据原样保留，最终结束状态由额外 `sync-final.json/png` 和汇总 `sync-final-observations.json` 确认恢复为 true。不需要重跑已成立的 loader 缺失证据。

## 生成文件、最终状态和清理限制

生成文件：`entry/build/`、`.hvigor/` 构建缓存/HAP；本记录及 `workflow/verification/baseline_*.py`、`summarize_baseline.py`；`traces/baseline-analysis/` 原始日志、指纹、JSON、PNG。Hypium 两次连接自动生成的原 `reports/2026-10-16-19-39-51`、`reports/2026-10-16-19-40-57` 已在确认绝对源/目标均位于本题工作区后移动到 `traces/baseline-analysis/hypium-generated/`，没有删除日志或截图。

设备操作已于本轮证据采集后向主 Agent 释放，不再操作共享设备。应用未卸载、未清数据，停留 WebDAV 配置错误态；最终保存本轮测试端点 `http://127.0.0.1:18769`、本轮测试账号和 `/vg-spec9-round01`，自动同步仍 checked=false；未猜测恢复无法安全取得的旧凭据。临时服务经 Ctrl-C 停止，19:43:20 最终检查 18769 无主机监听。

映射所有权：首次 `hdc fport ls` 只有既有 `tcp:9923 tcp:8012 [Forward]`，不属于本轮。`05-configure-test.log` 记录本轮创建 `hdc rport tcp:18769 tcp:18769` 并退出 0；两次 Hypium 连接日志分别记录自动建立本机 9982、9949 的 UI RPC forward。最终 `08-final-integrity.log` 可见 reverse 18769 和 forward 9923、9949、9982。未删除既有 9923。

清理原始操作 `hdc fport rm tcp:18769 tcp:18769`（以及较窄 `hdc fport rm tcp:18769`）被执行工具自动审批拒绝，工具返回原文核心为：`exec_command failed: CreateProcess { message: "Rejected(... rejected: blocked by policy)" }`，未给出更具体原因或命令退出码；该操作没有执行。一次使用 `hdc fport rm 'tcp:18769 tcp:18769'` 的进程获准运行，但 hdc 返回 `[Fail]Remove forward ruler failed, ruler is not exist "tcp:18769 tcp:18769"`，hdc 进程退出 0，不能把退出 0 当清理成功。后续未绕过审核，映射保留并报告主 Agent 协调；该环境清理阻断不改变已采集的业务证据，也不登记为通过。

测试前后生产指纹一致；没有将未运行项或错误服务流程包装成完整成功同步，没有推断官方隐藏输入、F-point 数量或官方成绩。
