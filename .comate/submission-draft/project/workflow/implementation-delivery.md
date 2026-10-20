# vg-spec8 / 1-do 本地交付

WebDAV「从云端恢复」现在先显示第一层确认，按钮为「取消」「继续」。取消、系统返回或遮罩关闭均不授权恢复；关闭完成后入口可再次使用。仅明确点击本轮「继续」，且确认层关闭后，才进入原有下载、预览和覆盖确认流程。

生产改动为五个文件：SettingsSyncSection、SettingsWebDavConfigPanel（新增）、WebDavRestoreConfirmDialog（新增）、SettingsPage 和 TopNavigation。后两者只增加稳定 id；原有九个业务方法和三个搬移的配置辅助方法正文保持一致。新增/本次功能组件分别为 472、264、51 行。

验收矩阵 A1—A19 均有当前源码的通过证据。主 Agent 另外核对了原始报告、安装清单、连续计数文件、请求时间戳、非空数据库实体快照及 258 项构建输入指纹。

| 检查 | 实际结果 |
| --- | --- |
| clean assembleHap | exit 0；与基线逐条对照，764 条原有 ArkTS 告警，新增 0、移除 0 |
| 安装/冷启动 | 同一新构建 HAP 重装后测试；安装文本成功，bm updateTime 更新；正常入口和冷重启可用 |
| 完整 Hypium 轮 | attempt04-full：4 pass、0 fail、2 skip；跳过的是尚未准备的非空哨兵及其对比 |
| 针对性补测 | attempt05-sentinel：4 pass、0 fail、0 skip；消除前一轮两项跳过，非空实体前后完全一致 |
| 六个唯一测试方法 | 两轮同源码、同 HAP 合并后六项均有真实 pass；不是声称单轮执行六项全部通过 |
| 未继续网络窗口 | 完整轮 91 个、补测轮 47 个计数检查点，累计增量全部为 0 |
| 明确继续正控 | 两轮均在明确继续后实际收到 3 条 HEAD；再开/取消增量为 0 |
| 边界/回归 | 10 轮取消、快速动作、系统返回、遮罩、分区及路由重进、冷启动、跨 125 秒累计窗口、空云端/真实本地空态、20 个空值/空格保存与未保存分支 |
| 源码保真 | 两轮测试前后与冻结版本的 258 项构建输入逐项一致 |

实测命令由各 PowerShell 进程先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`，再执行：

```text
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap
D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project D:/HCUP/vg-spec8 --device 127.0.0.1:5555 --json harness-report.json
D:/HCUP/common/.venv/Scripts/python.exe -m hypium_tests.run_subset
```

测试在日志目录执行，并配置公共 harness 的 PYTHONPATH 与本题运行环境变量。完整复跑入口为 `hypium_tests/run_validation.ps1`；逐次完整命令、起止时间和退出码保存在对应日志目录。初期 hdc 路径误报、Ability 自动发现和滚动 API/视口问题的原始失败均保留，修复的是测试/工具适配，未降低断言或修改生产实现。

- [独立验收报告](verification/implementation-final-01.md)
- [主 Agent 独立证据核对](final-evidence-check.json)
- [汇总自测报告](../logs/selftest.json)（明确标注为多轮真实报告汇总）
- [完整轮原始报告](../logs/implementation-validation/round-01/attempt04-full/harness-report.json)
- [补测原始报告](../logs/implementation-validation/round-01/attempt05-sentinel/harness-report.json)
- [需求复审](requirements/implementation-review-01.md)、[方案](design/implementation-plan-01.md)、[编码交接](implementation/implementation-01.md)

HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`；SHA256 `c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229`。

验证范围限制：未运行官方隐藏测试；D2 之后的完整成功恢复未测；全局自动同步并发未测（主测显式关闭并验证持久化，统计所有请求）。既有 SettingsPage 超过 500 行的技术债、764 条旧告警及原有请求超时不取消底层任务的行为未在本题扩改。设备保留本题测试配置、关闭的自动同步和一个新建哨兵词书；未清除原数据、未恢复未知旧端点。未提交 Git 或赛事成果。
