# vg-spec8 独立自测最终结论 01

**A1—A19 全部 pass。** 这是冻结源码下的本地自测结论，不是官方隐藏测试或成绩。会话 `01a14503-a32e-74c1-b3bc-c948f2f304ea`；未修改生产代码、Spec、state 或公共框架。

证据根 `R=logs/implementation-validation/round-01`；`R4=R/attempt04-full`，`R5=R/attempt05-sentinel`。机器可读汇总见 [combined-final-report.json](../../logs/implementation-validation/round-01/combined-final-report.json)；主 Agent 独立复核见 [final-evidence-check.json](../final-evidence-check.json) 与 [selftest.json](../../logs/selftest.json)。

## 构建、设备与源码一致性

- `clean assembleHap` exit 0；基线 764/本轮 764 条定位 ArkTS 告警，新增 0。原始命令/日志为 `R/build-command.txt`、`build-clean-assembleHap.log`，比较为 `warning-comparison.json`。
- HAP SHA256：`c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229`。各轮先重新覆盖安装本轮刚构建 HAP；R5 安装 Success 且 bm updateTime `1792160836747→1792161778582`，见 `R5/installation-manifest.json`、`install-command.txt`、`install.log`、`bm-*-install.json`。
- 设备 `127.0.0.1:5555`，emulator `6.1.0.115(SP11DEVC00E115R4P11)`、API 23、1308×2880；公共环境校验无告警，见 `R/environment-check.txt`、`device-api.txt`。不以原始失败的独立 dpi 查询冒充实测 DPI 通过。
- 258 个生产/资源/构建输入与主 Agent 冻结逐项一致，各用例前后及最终无变化。最终指纹 `R/source-fingerprint-final.json` SHA256：`cff0ff9567ae804b76c12add8b9989e95d37c89c18152b99b3fc3b09f4e85f5f`。
- 原始命令、退出码、动作时间戳、UI树/截图、请求日志及当轮测试脚本快照均在各轮目录。正式运行固定 Python `D:/HCUP/common/.venv/Scripts/python.exe`，使用只读公共 `harness.driver.HarnessTestCase` / 原报告器。每个 PowerShell 均加载指定环境入口。

## 多轮结果与网络对照

| 轮次 | 结果 | 说明 |
| --- | --- | --- |
| R4 完整 runner | exit 0；4 pass / 0 fail / 2 skip | 核心、全部20个五字段空/纯空白的已保存/未保存边界、继续正控通过。跳过仅为哨兵数据入口前置及其依赖比较；不计通过。 |
| R5 修正数据前置后的受影响用例 | exit 0；4 pass / 0 fail / 0 skip | 经已核对的首页唯一文字、创建弹层精确hint/层级/组件bounds建立非空哨兵，再执行核心、实体比较及同实例正控。 |

最终6个逻辑方法均有 pass 证据；R4 保留的 smoke/20边界方法与最终脚本正文完全相同，生产输入和 HAP 相同，不重复执行已通过的20边界。早期启动/滚动/安装路径等工具失败保留在过程报告 [implementation-validation-01.md](implementation-validation-01.md)，不算产品失败。

两个连续未授权窗口各约129.5秒，均含10轮取消重开、快速动作、系统返回、分区/路由重进及冷重启；主 Agent 独立检查的138个未授权计数点均为0。服务器记录所有 HTTP 方法，不清空窗口、不执行其它联网动作，自动同步先持久化关闭。各轮独立点击本轮 D1 的 `继续` 后才收到3条真实 HEAD（目录200、两备份路径404），随后原无备份流程收尾、入口恢复可用；再开取消窗口增量仍为0。见 `R4/R5/device-actions.jsonl`、`mock-requests.jsonl`、`counter-continuous-final.json`、`counter-positive-control-final.json`。有限时间/循环是策略，不声明穷尽任意次数或时长；同时独立核对源码 gate 前没有恢复包装器/计时任务。

## 逐需求结论

以下 UI 证据均有同名 `.json` / `.png`，动作和精确文案/enabled断言在对应 `harness.log`、`device-actions.jsonl`。

| 项目 | 结果 | 直接证据 |
| --- | --- | --- |
| A1 正常入口 | pass | R4/R5 的 S0→S1 导航动作、配置区与恢复入口树。 |
| A2 第一层显示 | pass | R5/cycle-00-open；稳定 D1 id 唯一、在请求前显示。 |
| A3 取消可执行 | pass | R5/cycle-00-open 与取消点击；S5 精确“取消”。 |
| A4 取消关闭 | pass | R5/cycle-00-cancel，D1 节点不存在。 |
| A5 回操作区 | pass | R5/cycle-00-cancel，S2可见且后续实际重开，无遮罩。 |
| A6 恢复入口原文 | pass | R5/cycle-00-cancel，S3精确“从云端恢复”。 |
| A7 入口可用 | pass | 同上 enabled=true，结合下一轮点击。 |
| A8 可重新打开 | pass | R5/cycle-01-open 与对应动作。 |
| A9 首开零请求 | pass | R5/counter-cycle-00-open、连续请求日志。 |
| A10 取消过程零请求 | pass | R5/counter-cycle-00-cancel。 |
| A11 重开零请求 | pass | R5/counter-cycle-01-open。 |
| A12 持续未授权零请求 | pass | R4/R5 counter-continuous-final，全部138点独立审计。 |
| A13 反复取消 | pass | R5/cycle-00…09、interleaved-00…04 UI/动作/计数。 |
| A14 快速动作零请求 | pass | R5/rapid-restore-single-dialog、counter-rapid-actions。 |
| A15 明确继续授权 | pass | R5/positive-control-before-continue-open、授权动作时间早于3条HEAD。 |
| A16 本地数据保护 | pass | R5/sentinel-comparison.json：8类业务表实体一致，含1条非空词书哨兵；words/review等表当时为空，不冒称复杂学习数据覆盖。前后实体文件 SHA256 同为 `ec26de7371422fe7554b5b7a29cfc90033a7ffa3e49939176c6ecfadfc2c5506`。 |
| A17 确认/请求状态分离 | pass | 两轮68个 D1 open 树均无 request_loading，网络0；源码授权关闭回调才调用原包装器。 |
| A18 取消后无残留阻塞 | pass | R5各取消后的 enabled/实际重开；无需网络/120s超时解锁。 |
| A19 无叠层残留 | pass | R5快速动作后D1消失、入口可用并能重开；打开树D1单实例。 |

A1—A14 保持明文等级；A15—A19 保持合理推导等级。U1 空/空白先D1、U2 系统返回关闭、U4 生命周期、U6 单实例已回归；U3 仅按批准边界关闭隔离自动同步，未扩改全局同步。U5 仅验证继续后既有无备份/失败流程。**D2预览取消/深层成功恢复、并发自动同步均 not_run**，不伪造深恢复或全局并发结论。

## 清理与交还

`R5/device-actions.jsonl` 保留 `fport rm tcp:18989 tcp:18989` 的真实成功输出及 mock_stopped(count=3)。`R/cleanup-result.json`、`forward-final.txt` 证实18989转发已移除、主机监听数0，显式删除命令只针对18989，原18769反向转发保留。没有停止或删除其它题/其它服务。

设备保留本题测试配置、自动同步关闭和唯一哨兵词书，未删除既存数据或还原未知旧端点。构建生成目录与2个新pyc单独登记，pyc按 `hypium_tests/.gitignore` 局部忽略。完整测试入口仍为 `hypium_tests/test_restore_confirmation.py`；本轮命令保存在各轮 `test-command.txt`，可审阅运行脚本 `hypium_tests/run_validation.ps1`。验证工作结束，停止写入并归还设备；后续交付由主 Agent 处理。
