# vg-spec8 未修改基线独立核验记录

本轮只执行 `spec-harness/0-analyze.md` 的基线构建、安装与最小设备观察，没有修改业务代码或 Spec。结论是**基线存在需求差距**：正常点击“从云端恢复”后直接进入网络处理，未显示第一层“取消／继续”确认。以下是本地自测证据，不是官方测试或成绩。

## 1. 样本身份和证据有效性

- 工程：`D:/HCUP/vg-spec8`；HEAD：`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，未打新 tag。
- Spec SHA-256：`256038a2336dce8956585ff92c18e7ec9e5cd79d736f7b7f56021dbf646af592`。
- metadata SHA-256：`92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。
- `CODEX_THREAD_ID=01a144ed-37c3-7240-b34d-e526c496efeb`；环境 `CODEX_SESSION_ID=01a144eb-32eb-7cb3-b4d6-daea0ae599b7` 是继承的主会话值，不冒充独立子会话 UUID。
- 主 Agent 协调其他角色只读，本角色独占本题构建/设备操作。测试前后对 298 个受跟踪工程文件逐文件 SHA-256 比较，差异为空，HEAD 相同。证据：`logs/analysis-baseline/source-fingerprint-before.json`、`source-fingerprint-after.json`、`source-integrity-result.json`、`head-before.txt`、`status-before.txt`、`status-after.txt`。
- 测试开始已有 `AGENTS.md` 修改与题目资料/记录的未跟踪目录；没有撤销它们。未将这些准备材料当作功能实现证据。
- 所有 PowerShell 工具进程先执行 `. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。只使用本题资料、源码、复制的 test-harness 和通用环境工具；未访问其他题源码、上游修复历史或题包目录。

## 2. 环境与构建、安装

| 项 | 实际结果 | 原始证据（均在 `logs/analysis-baseline/`） |
| --- | --- | --- |
| 工具 | DevEco Studio 环境标识 6.1.0.860 / API 23；hvigor 6.23.7；Node v18.20.1；OpenJDK 21.0.8；hdc 3.2.0c；Hypium 6.1.0.210；观察脚本使用 `D:/HCUP/common/.venv/Scripts/python.exe` | `tool-versions.txt`、`hypium-methods.txt`、`sdk-environment.txt` |
| 工程 SDK 配置 | `build-profile.json5` 指定 target/compatible `6.0.2(22)`；这是工程配置，设备实际 API 23 | 本题配置文件；`device-api.txt` |
| 清理重建 | `& D:/HarmonyDev/DevEcoStudio-6.1.0/tools/hvigor/bin/hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon`；2026-10-16 21:38:22—21:38:40 +08:00，退出码 **0**，`BUILD SUCCESSFUL in 16 s 720 ms` | `build-command.txt`、`build-clean-assembleHap.log`、`build-result.json` |
| 告警 | 764 条带文件定位的 ArkTS warning；另有 ArkTS FAQ 提示和 `No signingConfig found for product default`。498 条异常处理提示，132 条 showToast deprecated，其他逐条见 CSV，不省略现有告警 | `build-warnings.csv`、`build-warning-index.txt`、`build-warning-summary.txt` |
| HAP | `entry/build/default/outputs/default/entry-default-unsigned.hap`，9,065,537 字节；SHA-256 `1695ccc7d351472d2472a498ae9ed31a6f75ac11f8a861e20ab2060bc3452d6c` | `hap-sha256.txt` |
| 安装 | `hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap`，退出码 **0**，`install bundle successfully`，未卸载或清空数据 | `install-command.txt`、`install.log`、`install-result.json` |
| 启动 | `hdc -t 127.0.0.1:5555 shell aa force-stop io.qzz.weiyu` 输出成功；`hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b io.qzz.weiyu` 退出码 **0**，输出 `start ability successfully` | `force-stop.log`、`start.log`、`start-result.json` |
| 设备 | 仅一个已连接目标 `127.0.0.1:5555`；软件 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`，API 23，1308×2880；model 参数仅返回 emulator，dpi 参数读取失败。test-harness 的版本/分辨率检查报告匹配，但该检查并不独立验证机型/dpi | `hdc-targets.txt`、`environment-check.txt`、`device-api.txt`、`device-model.txt`、`device-dpi.txt` |

安装前的 `00-before-install.*` 与 `window-before-install.txt` **仅用于占用检查**：发现其他测试残留后停止设备写入，由主 Agent 取得用户“可以，当前已空闲”的明确授权才安装本题 HAP。它们不作为本题功能证据。

构建自动产物在 `entry/build/`、`.hvigor/` 等既有忽略目录生成/更新，未作为源码提交。Hypium 报告位于本日志目录 `reports/`；首次运行自动生成于根目录的单个报告子目录已安全迁移到 `logs/analysis-baseline/hypium-initial-report/`。Python 导入生成的本题 harness `__pycache__` 已列于 `tool-generated-pycache.txt`。观察脚本曾因 Hypium 方向参数小写 `up` 失败，错误原样保留于 `swipe-actions.log`；按本地 API 文档修正观察脚本为大写并用已记录的 hdc swipe 完成滚动，不是产品失败或通过证据。早先 `rport ls` 返回 `Incorrect forward command`，随后按 hdc help 使用 `fport ls`，未改其他映射。

## 3. 正常入口、前置配置和观察方法

实际路径：安装的本题 HAP 冷启动首页 → Hypium 点击 `⚙` → 设置列表点击 `WebDAV 配置` → 滚动到“手动操作” → `从云端恢复`。

- 本题启动首页：`01-start.png/json`；设置列表：`02-settings.png/json`。
- 源码入口：`entry/src/main/ets/entryability/EntryAbility.ets:35` 载入 `pages/Index`；`pages/Index.ets:323` 跳转 `pages/SettingsPage`；`pages/index/components/TopNavigation.ets:69` 起为齿轮容器；`pages/SettingsPage.ets:40` 定义 `sync / WebDAV 配置`，`:427` 起渲染 `SettingsSyncSection`，`:507` 起处理列表点击。
- 设备既有五个 WebDAV 配置字段非空，仅记录非空布尔值，未输出旧账号密码，未使用旧云端端点。通过 UI 将它们改为哨兵配置：endpoint `http://127.0.0.1:18988/dav/`，账号 `vg_spec8_observer`，密码 `sentinel-not-a-secret`，同步密码 `sentinel-sync-password`，目录 `/vg_spec8_observation`；这些均为本题公开的临时测试值。
- 自动同步 Toggle 实际 `checked=false`，保存设置显示 `✅ WebDAV 设置已保存`。证据：`03-sentinel-config.png/json`、`05b-actions-visible.png/json`、`05c-saved-confirmed.png/json`、`configure-sentinel.log`、`save-confirmed.log`、`device-actions.jsonl`。未点击测试连接、立即同步或立即备份。
- 本地 `mock_webdav.py` 在主机 127.0.0.1:18988 监听，`hdc ... rport tcp:18988 tcp:18988` 将设备 localhost 请求送达主机。每条到达请求先记时间/方法/路径再延迟 8 秒返回 404；不保存 Authorization 或请求体，不提供可导入备份，不触发真实覆盖。`mock-requests.jsonl` 是独立服务端计数，不以应用日志缺失推断零请求。
- 开始前计数为 0，未点击继续。首个实收 HEAD 与按钮点击时间、UI 状态和后续 PUT 404 页面结果相互对应，构成端点可达性正控；不需要另行点击不存在的“继续”或引入其他请求污染基点。
- 操作、hdc 命令、时间和退出码由 `device-actions.jsonl` 记录；Hypium 操作原日志见 `restore-observation.log`、`second-restore.log` 及日志目录内报告。完整本地框架套件、已有无关单测与官方隐藏测试均 **not_run**。

## 4. 实际发现与最小复现

### F1：首次恢复没有第一层确认，直接请求

1. 用上述哨兵配置关闭自动同步并保存；计数文件为 0（`pre-restore-counter.json`，21:50:30 +08:00）。
2. 21:50:35.373 开始本轮点击 `从云端恢复`，从未点 `继续`。
3. 服务端 21:50:35.637 收到 `HEAD /dav/vg_spec8_observation`，计数从 0 变 1。
4. 21:50:36.809 截图/树显示五个操作按钮均为 `处理中...`、`enabled=false`，另有 `正在处理...`；没有 `取消`/`继续`。证据 `06-first-restore-inflight.png/json`。
5. 21:50:36.937 在原恢复按钮位置再次点击；当时计数仍为 1，`07-repeat-click-inflight.png/json` 保留忙态。不能仅据此宣称完整快速重复取消测试通过。
6. 同一操作随后又产生 HEAD、PUT `.keep`，该批最终 **3** 条请求，页面显示 `⚠️ 创建目录失败：PUT 404: `，恢复按钮重新 `enabled=true`（`08-restore-result.png/json`）。观察脚本 `restore-observe` 以 **退出码 1** 正确报告两个 Spec 断言失败（`restore-test-process-result.json`、`restore-observation-result.json`）。

期望：先显示第一层恢复确认；未明确点击 `继续` 前任何 WebDAV 请求增量均为 0。实际：首层确认不出现，先进入网络 busy 并发出 HEAD/PUT。关联 A2、A9、A12、A17。证据强度：**强**，本题新 HAP、正常 UI、独立服务端计数、截图/tree、同一源码指纹相互支持。

归因假设（强代码支持）：`pages/settings/SettingsSyncSection.ets:164-165` 直接经 `runWebDavBackupAction` 进入恢复；`:140-156` 先设置 busy/结果；`:199-200` 立即调用 `downloadBackupPlain(false)`。`sync/WebDavSyncManager.ets:471-478` 配置校验后即远端预检，`:294` HEAD、`:303-306` 尝试创建；没有第一层授权门槛。`SettingsSyncSection.ets:215-220` 的确认是下载/预览之后的 D2，按钮为 `取消`/`确认恢复`，不等于本题要求的第一层 D1。

### F2：失败返回后可再点，但仍先联网

首次失败后恢复入口确实可用，这只属于**网络失败返回后的基线行为**，不能标记“取消后恢复可用”通过。

第二次点击前计数 **3**（`pre-second-restore-counter.json`）；21:51:59 点击后再次进入忙态，`09-second-restore-inflight.png/json` 无第一层取消/继续；请求依次 HEAD、HEAD、PUT。最终计数 **6 = 4 HEAD + 2 PUT**，未产生 GET，未点击取消/继续，未进入本地恢复覆盖。`10-final-idle.png/json` 显示创建目录失败，按钮 enabled=true，自动同步 checked=false。证据：`mock-requests.jsonl`、`final-counter.json`、`second-restore.log`。

## 5. 按验收矩阵逐项状态

本节引用主 Agent 本轮起草的 `spec/acceptance.md` 编号，仅评价当前未修改基线与实际执行范围；非完整交付验收，不将缺失前置导致未运行的细项包装成 pass。

| 项 | 状态 | 实际证据或未运行原因 |
| --- | --- | --- |
| A1 既有入口 | **pass** | 本题 HAP 首页→设置→WebDAV 操作区实际到达，01/02/05b 截图和 Hypium 操作日志 |
| A2 第一层确认 | **fail** | 两次空闲点击均直接 busy/联网，无 D1，06/09 tree+截图 |
| A3 D1 可执行取消 | **not_run** | D1 前置能力缺失，没有可点击目标；未用 D2 取消替代 |
| A4 取消关闭 | **not_run** | 未能执行 D1 取消 |
| A5 取消返回操作区 | **not_run** | 未能执行 D1 取消 |
| A6 取消后入口可见 | **not_run** | 网络失败后可见不能替代取消后可见 |
| A7 取消后入口可用 | **not_run** | 网络失败后 enabled=true 不能替代取消后可用 |
| A8 取消后重开 D1 | **not_run** | 首次 D1 与取消前置缺失 |
| A9 首次打开前零请求 | **fail** | 点击前 0，未继续即首个 HEAD，首批增至3 |
| A10 取消前中后零请求 | **not_run** | 未执行取消完整窗口，首点已有反例另记A9 |
| A11 取消后再打开累计零请求 | **not_run** | 未执行取消后重开；第二次失败返回后点击另列补充观察 |
| A12 未继续期间持续零请求 | **fail** | 未继续期间仍有延迟的后续 HEAD、PUT；原始计数含时间戳 |
| A13 多轮开取消 | **not_run** | D1 缺失，未执行取消循环 |
| A14 快速开取消网络不变量 | **not_run** | 只做了首次忙态同坐标重复点击，不是完整快速开取消序列 |
| A15 D1 继续授权控件 | **not_run** | D1 缺失；从未点击任何继续 |
| A16 打开取消不覆盖本地数据 | **not_run** | 未设置本地业务哨兵或计算本地数据前后校验，也未执行取消；mock无备份且预检已失败，不能据此冒充完整数据保护验证 |
| A17 确认与真实请求忙态分离 | **fail** | 还没有任何继续授权即5按钮禁用且服务端收到请求，06证据 |
| A18 取消清理阻塞状态 | **not_run** | 没有执行取消，失败finally清理不可替代 |
| A19 重复动作无残留确认/遮罩 | **not_run** | D1缺失，未执行完整快速取消重开 |
| U1—U6 待确认假设 | **not_run** | 本轮不自行批准假设或增加产品要求 |

没有将设备暂时占用记成产品失败或通过。当前结果没有环境阻断项；取消相关未运行来自基线前置能力缺失。没有编造隐藏用例、官方分数或“整题通过”。建议主 Agent 将本题退回**方案/编码阶段**补齐第一层授权与无请求取消路径；本轮分析阶段不修复。

## 6. 清理与最终状态

- 两次请求批次均已结束，mock计数最终6，最后页面空闲，自动同步 `checked=false`。
- `hdc -t 127.0.0.1:5555 fport rm tcp:18988 tcp:18988` 退出码0；`forward-after-cleanup.txt` 已无18988，本题开始前已有的18769 reverse及其他映射均保留。
- 主机监听18988的 Python进程经过 PID/命令行核对，确认为本题 `mock_webdav.py` 后停止；`mock-stop-result.json` 记录 PID48456、停止时间与 remainingListeners=0。
- 设备最终保留本题 localhost 哨兵配置，自动同步关闭；不恢复不明外部端点，不输出或留用旧凭据，未卸载清空数据。
- 清理后源码指纹再次复核仍无变化，见 `source-integrity-result.json`。本角色写入仅为指定核验报告、日志/截图/观察脚本以及上述已登记工具自动产物。

所有证据路径相对工程根 `D:/HCUP/vg-spec8`，本报告之外的正式分析交付由主 Agent 汇总到 `spec/acceptance.md` 和 `spec/baseline-notes.md`。
