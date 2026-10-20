# cml-spec1 独立基线设备核验 r3

时间：2026-10-20 11:31–11:48 +08:00。阶段：**分析阶段，验证未修改基线**。r1 的独立 clean / assembleHap 成功及告警清单继续有效；本轮完成实际安装、启动、权限处理、原有主窗口恢复、内容横/纵滑、一次 force-stop 后重启复核。没有修改生产代码、Spec 或构建配置，也没有签名改包。

结论：**运行环境阻断已解除；真实主入口显示通知演示页面，缺少 Spec 四标签导航。** Spec 17 步本轮记 2 fail、15 blocked，零项记 pass。该统计只是本地基线观察，不是官方 F-point 或成绩。权限拒绝造成的系统设置跳转已通过系统最近任务正常返回绕过交互阻挡，未授予麦克风权限，未绕过系统权限校验。

## 1. 设备协调与运行对象

主 Agent 转达用户明确选择“释放一台后使用本题独立实例”，授权正常停止一台既有模拟器，优先 11243。本轮只读取进程命令行确定其为 `CmlSpec17Baseline`（PID 38964），**未读取该题目录或源码、未删除其模拟器、未清应用数据、未手动改其文件**。官方命令 `Emulator.exe -stop CmlSpec17Baseline` 在 03:31:11.716 UTC 返回退出 0 / `Stop emulator CmlSpec17Baseline successfully`。证据 `logs/analysis-baseline-r3-stop-candidate.json`、`stop-result.json`；随后 11243 从在线 target 列表消失。正常停止可能由模拟器自行保存状态，本轮未对该实例做其他操作。

以原 r1 创建的本题实例 `CmlSpec1Baseline` 启动 11245，2GB RAM、Pura 90 Pro Max；命令和 PID 76804 记录 `logs/analysis-baseline-r3-emulator-start-process.json`。使用 `Start-Process -WindowStyle Hidden`，**异步进程退出码未取得，不能记 0**。03:32:40 UTC 的 hdc 在线结果含 11245（`boot-targets.json`）。仅本自测 Agent 操作本题设备，未操作另外三台仍运行的设备。

实际设备：

- target：`127.0.0.1:11245`；API 23（设备 param 返回）；系统 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`。
- 屏幕：截图 PNG 实际 1308×2880；实例配置 PHEMU-FD00 / 560dpi / 6.9 inch。应用日志 viewport density 3.5，等于 560dpi / 160。
- `python -m harness.env_check --device 127.0.0.1:11245` 退出 0，系统版本和分辨率匹配框架对照值，原文 `logs/analysis-baseline-r3-env-check.log`。该工具只核验其实现中的版本/分辨率；配置和 app viewport 为 dpi 的另行证据。

安装前 `aa dump -l` mission 列表为空（`preinstall-missions.json`），不是其他任务同名 bundle 的已安装前台产物。

| 操作 | 命令 | 退出码 / 实际结果 | 原始记录 |
| --- | --- | --- | --- |
| 安装本轮 HAP | `hdc -t 127.0.0.1:11245 install entry/build/default/outputs/default/entry-default-unsigned.hap` | 0 / install bundle successfully | `logs/analysis-baseline-r3-install-unsigned.json`、`.log` |
| 首次启动 | `hdc -t 127.0.0.1:11245 shell aa start -a EntryAbility -b com.joker.coolmall` | 0 / start ability successfully | `logs/analysis-baseline-r3-launch-first.json` |
| 一次应用重启 | `aa force-stop com.joker.coolmall` 后同一 aa start | 两条均 0 | `logs/analysis-baseline-r3-probe-commands.jsonl` 中 restart-permission-stop / -launch |

运行包 SHA256 始终为 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`，19,133,822 bytes，来自本题 r1 独立 clean/build。**unsigned HAP 实际安装成功，无需本地签名**；不再把 r1/r2 未配置签名的潜在风险描述成安装障碍。

## 2. 权限流程与准确时间关系

所有 PowerShell 工具进程加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`，所有设备命令进程另外加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。无麦克风录音、通知演示、登录或领取交易操作。

实际流程：

1. 首次启动显示麦克风对话框 `允许“青商城”访问你的麦克风？` / `使用麦克风录音`，按钮 `不允许` / `允许`。权威当前状态证据为 `permission-before.png`、`permission-before-after.png`、`permission-before.json`；这对截图字节哈希相等。
2. 点击 UI dump 中 `不允许` 的中心 (369,1655)，出现 `麦克风权限` 系统 sheet，`不允许` selected=true，`确定` 按钮待点。证据 `permission-denied.*`。**该文件名只是动作标签，不代表弹窗已消失。**
3. 点击 `确定` (654,2656)，随后实际状态为系统 `Setting.AppDetail`，不是主页面；`permission-deny-confirm.*`。Back 后是 launcher，文件 `settled-home.*` 的名称也只是采集标签，**不作为应用首页证据**。
4. 再 aa start 重新请求，sheet 仍显示不允许已选；关闭 X 后又进入 Settings.AppDetail，证据 `app-resumed.*`、`permission-sheet-close.*`。mission 元数据确认 app BACKGROUND / Settings FOREGROUND（`post-denial-missions.json`），不能把这段过程描述成 app 崩溃。
5. 按主 Agent 指定正常返回分支，用 Hypium 6.1.0.210 `UiDriver.connect(device_sn='127.0.0.1:11245').swipe_to_recent_task()` 打开最近任务；实图 `recent-tasks-after.png` 中有青商城旧主窗口卡片。点击该卡片空白处 (654,2000)，恢复同一 EntryAbility（AbilityRecord 33）到 FOREGROUND，Settings 转后台；证据 `existing-app-window.*` / `restored-app-missions.json`。**麦克风从未点允许。**
6. force-stop 后 aa start 复核仍进入相同拒绝状态 sheet；正常关闭后再通过最近任务恢复本次新建的主窗口，最终 AbilityRecord 39 / PID 8748。对应 `restart-permission.*`、`restart-sheet-close.*`、`restart-recent-tasks.*`、`restarted-app-window.*` 与 `final-missions.json`。

初始 `first.json` 是启动早期 launcher 树，而稍后的 `first.png` 已是 app + 权限框，存在时差，**不作为同屏权威证据**。最早两次 file recv 使用 `D:/...` 本地路径被 hdc 误当相对路径，输出 `[Fail]` 尽管原生退出码 0；已保留失败日志，改用 Windows 相对路径后传输成功。不能只按 exit 0 判定截图存在。

后续 `device_probe.py capture` 对每个稳定状态按“截图 → UI dump → 截图”顺序采集并记录逐命令 UTC（多数间隔 4–6 秒）；不是原子同步截图。权威 app 状态下，前后截图目视一致，app 窗口 UI 文本/类型/坐标也一致。它们用来核对页面状态，**没有用来证明 Lottie 动画播放/不播放**。

## 3. 真实入口、手势与重启观察

本轮未改源代码以导出测试页面，也未用隐藏路由/注入业务代码进入其他页面。启动目标为现有 EntryAbility，页面清单 `entry/src/main/resources/base/profile/main_pages.json` 为 `view/EntryPage`（静态入口配置事实）。

真实无遮挡页面显示：`主页面`、`主页面内容视图`，以及 `申请发送通知权限，未授权则拉起一次二次授权申请`、`预设默认配置`、发送文本/长文本/多行文本/图片消息、下载模板消息、清楚通知、设置角标、清楚角标等按钮。没有 `首页`、`分类`、`购物车`、`我的`，也没有优惠券 `领取`。

| 观察 | 动作及实际结果 | 权威截图 / UI dump |
| --- | --- | --- |
| 恢复已有应用主窗口 | 点击最近任务中的青商城卡片空白处；无遮挡通知演示页 | `traces/baseline-analysis/r3/existing-app-window.png`、`existing-app-window-after.png`、`existing-app-window.json` |
| 内容区向左滑 | `uitest uiInput swipe 1100 2100 200 2100 1200`，退出 0 / No Error；没有切页 | `content-left.png`、`content-left-after.png`、`content-left.json` |
| 内容区上滑以尝试向下浏览 | `uitest uiInput swipe 1050 2200 1050 800 1200`，退出 0 / No Error；内容没有滚动 | `content-up.png`、`content-up-after.png`、`content-up.json` |
| force-stop / aa start 后正常恢复窗口 | 权限拒绝 sheet 再现；最近任务恢复后仍是相同通知演示页 | `restart-permission.*`、`restarted-app-window.png`、`restarted-app-window-after.png`、`restarted-app-window.json` |

手势均在 app 内容区，未触发按钮、系统返回边缘、通知发布或交易。`observed-app-summary.json` 仅从 bundleName=`com.joker.coolmall` 的窗口提取 UI 结果：这四个主页面采样的 app 文本及 bounds 完全相同；四标签文字出现次数均 0；Tabs / TabContent / Swiper / Scroll / List 类型出现次数均 0。这是**运行 UI 树**证据，结合全屏截图支持入口缺失；组件类型本身不作为所有可能实现形式的穷尽证明。

## 4. 逐 Spec 步骤状态

局部编号与原 Spec 场景/步骤对应，供主 Agent 映射正式验收矩阵。前置缺失不伪造坐标点击，不把无图标当作动画静止通过。

| 编号 | 要求 | 状态 | 实际 / 证据及限制 |
| --- | --- | --- | --- |
| S1.1 | 启动主页面有首页、分类、购物车、我的 | fail | 实际通知演示页，四文字均缺失；existing-app-window / restarted-app-window |
| S1.2 | 首页默认选中、上方显示首页内容 | fail | 实际为通知演示内容，没有首页标签和首页内容；同上 |
| S1.3 | 点击分类切换分类页 | blocked | 没有分类标签可点击，未假点屏幕坐标 |
| S1.4 | 分类 Lottie、黑色及其余灰色重置 | blocked | 无底栏/图标前置，动画和颜色未验证 |
| S1.5 | 点击购物车切页并动画 | blocked | 无购物车标签前置 |
| S2.1 | 在首页左滑到分类 | blocked | 正式首页前置不存在；对实际内容区左滑已执行且没有切页，不能当作从首页的完整用例 |
| S2.2 | 分类联动高亮/动画 | blocked | 未能到分类页且无底栏 |
| S2.3 | 再左滑到购物车 | blocked | 分类前置未达成，未伪造下一步 |
| S2.4 | 点击我的切页/动画 | blocked | 无我的标签前置 |
| S3.1 | 首次首页自动 Lottie | blocked | 首启存在权限弹窗且没有首页图标；未采动态图标证据 |
| S3.2 | 我的动画、首页回第一帧静止 | blocked | 无两图标/切页前置 |
| S3.3 | 返回首页重播图标 | blocked | 无首页返回标签；系统任务恢复不是 Spec 的标签返回 |
| S3.4 | 首页内容/文字黑色 | blocked | 不能达成从我的返回首页这一前置 |
| S4.1 | 已选首页，浏览到领取不可见 | blocked | 没有首页/领取；对实际页纵滑无滚动不等于建立了该前置 |
| S4.2 | 点击已选首页 | blocked | 无首页标签，不执行替代坐标点击 |
| S4.3 | 自动回顶、领取重新可见 | blocked | 无滚动首页与领取前置 |
| S4.4 | 保持选中、不切页、不额外重播 | blocked | 无底栏/图标，不能把“未发生”误算负向动画通过 |

动画帧、黑/灰颜色、首次自动播放、离开后复位第一帧、重播次数和重复点击不重播均未获得证据。附加快速重复、边界滑动及网络/数据类扩展本轮 not_run；基线入口缺失已经明确，未扩展无关测试。

## 5. 运行日志与失败归因

- 首启 raw 系统日志：`logs/analysis-baseline-r3-postlaunch-hilog.log`（原始 6000+ 行，工具界面曾截断，但文件保存完整）。其中 PID 3918 的 `Ability onCreate` 见 `initial-app-hilog-signals.txt`；启动输出中的命名转换自检文字不计作 Spec 测试通过。
- 最后一次重启后按实际 PID 8748 读取 `hdc -t 127.0.0.1:11245 shell hilog -x -P 8748`，退出 0，raw 为 `logs/analysis-baseline-r3-app-hilog-final.log` / `.json`。有 onCreate、requestAudioPermission、窗口 onForeground/ON_ACTIVE；有系统 `CONCUR apply qos failed errno=4` 错误与生命周期警告，**未见本次采集中的 FATAL / crash / JS ERROR / uncaught 签名**。
- 本轮未观察 app 自发崩溃。权限流程中 app 转后台是 mission 元数据可见的 Settings 跳转；显式 force-stop 属于本轮操作，不当作自发崩溃。日志是采样范围内结论，不声称全系统从未崩溃。
- Hypium 有 `tracker dependency is not ok` 警告，但指定 11245 的连接和最近任务动作返回，运行退出 0；其报告均留在本题 `traces/baseline-analysis/r3/reports/`。无官方评测器结果。
- 一个可选离线像素比较尝试因 common Python 未装 PIL 未运行，未安装依赖、未据此声称像素或动画断言通过；改用原图目视和原始 UI 树比较。

最小功能失败复现：安装本轮哈希 HAP → aa start → 拒绝权限并关闭后经系统最近任务恢复青商城旧窗口。期望：Spec 四标签底栏和首页内容；实际：通知演示页，无四标签。关联 S1.1 / S1.2，证据强度**强（实际截图 + app 窗口 dump + 重启复现）**。后续点击/动画/回顶受此入口前置阻断。建议退回需求/方案核对主入口接线，再在正式编码阶段实现；本分析阶段不修业务代码，由主 Agent 决策。

## 6. 可复核命令与产物索引

- 全部关键命令汇总：`traces/baseline-analysis/r3/command-index.csv`（UTC、label、命令、exit_code、是否出现 [Fail]、raw record）。
- 索引时间已由 `rebuild_command_index.py` 从未修改的原始 JSON/JSONL 带偏移时间通过 Python datetime 解析，统一为 UTC ISO8601 `Z`；`raw_utc` 列保留原始精度/偏移，`raw_line` 定位 JSONL 行。旧索引因 PowerShell 时间转换混入本地时区且丢失偏移，原样另存 `command-index-v1-mixed-timezones.csv`，不得用于时间判断。索引为派生物，时间和行为以 raw 记录为准；`command-index-rebuild-audit.json` 保存原始记录前后哈希核对及新旧索引哈希，`artifact-manifest.json` 已同步。此修正没有重跑设备、构建或 UI，也不改变需求状态。
- 单条原生命令 JSON / 原文：`logs/analysis-baseline-r3-*.json` / `*.log`。
- 重复截图/转储/点击/滑动/重启命令原文与退出码：`logs/analysis-baseline-r3-probe-commands.jsonl`；每条 stdout 独立 `.log`。
- 可复跑采集脚本：`traces/baseline-analysis/r3/device_probe.py`、`hdc-log.ps1`、`recent_tasks.py`（Hypium 调用及退出记录在 recent-tasks / restart-recent-tasks 日志）。
- 原始截图、dump、派生文本节点清单：同目录各 `<label>.png` / `<label>-after.png` / `<label>.json` / `<label>-nodes.json`。`*.json` 原始树未删除断言或过滤；节点清单/摘要是另存派生物。
- `artifact-manifest.json` 保存上述本轮证据文件 SHA256、字节数与 PNG 实际尺寸；命令退出码和原始 stdout 才是行为证据来源。

## 7. 末尾源码和包指纹

11:45:23 +08:00 再核对全部 677 个 tracked 文件：

- HEAD 仍为 `7014cebd60f2181fac2a36d399ca16b3d6a175ab`。
- 与本轮测试前逐文件 SHA256 比较变化为空；tracked diff 空。
- 测试前与末尾清单文件 SHA256 均为 `3b12ddf59b0a97823f2a78e305e8a0964f4c9e3724ae008fe9bbff33de58837c`。
- HAP SHA256 仍 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`。

原始清单 `traces/baseline-analysis/r3/source-before.json`、`source-after.json`；比较结果 `source-final-comparison.json`。构建生成的 ignored 缓存/产物、Hypium 在本题生成的 reports、设备临时截图/agent 均作为测试工具生成物单独记录，未改生产文件或公共依赖。

操作已冻结，11245 留在无遮挡通知演示主窗口、麦克风保持拒绝，专用模拟器仍运行。无需再请求用户释放设备。本阶段尚未实现的 Spec 功能保留 fail/blocked，不因完成基线分析而改为通过。
