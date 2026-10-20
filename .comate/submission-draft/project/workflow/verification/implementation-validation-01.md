# vg-spec8 实现轮独立验证 01

状态：过程记录已结束，最终结论和逐项证据见 [implementation-final-01.md](implementation-final-01.md)。以下保留当时的进度与工具修正记录，不覆盖历史状态。

## 授权、来源与环境

独立验证会话 `01a14503-a32e-74c1-b3bc-c948f2f304ea`；主 Agent 正式冻结五文件并独占释放设备 `127.0.0.1:5555` 后开始。批准需求 SHA256 `69849e82f4402b87fd1a49cd53631b4a42154d24f3a9fbbc653c2786a98ef057`，方案 SHA256 `9a08f8254c3b1e1159234997b6af011ce35241cbf0ffc6633a021714aaab3dcb`。本题基线 HEAD `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。

证据根 `logs/implementation-validation/round-01/`。所有 PowerShell 进程加载两个指定环境入口；实际 Python 固定为 `D:/HCUP/common/.venv/Scripts/python.exe`，公共 harness 只读。没有改生产代码、Spec、state 或公共框架；只修本题自测工具。

## 已证实的构建与安装

- `build-command.txt` 的 clean assembleHap 完整命令执行退出码 0，`build-clean-assembleHap.log` 记录 BUILD SUCCESSFUL in 16 s 846 ms。
- 构建前本角色捕获 258 个生产/资源/构建输入，逐项与主 Agent `workflow/production-freeze-01.json` 相同，见 `freeze-verification.json`。
- `warning-comparison.json`：基线 764、本轮 764；以诊断消息与归一化源码语句匹配（允许已批准代码搬移造成路径/行号变化），新增 0、移除 0。原 No signingConfig 告警保持。
- 本轮 unsigned HAP SHA256 `c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229`。每次设备自测前均覆盖安装此刚构建产物，检查 Success 文本、bm updateTime 改变和 HAP 哈希，完整证据分别在各 attempt 目录。

## 工具失败与修正（不冒充产品失败）

| 记录 | 实际表现与归因 | 处理与证据边界 |
| --- | --- | --- |
| install-attempt01-path-failure.log | hdc 把 D:/ 形式绝对路径拼入 cwd，输出 Fail 但原始退出码 0；bm updateTime 未变 | 保留反例，改本题工程相对 HAP 路径；安装语义检查加入 Success/Fail 与 updateTime，失败时不运行产品测试。 |
| harness-attempt01.log / harness-report-attempt01.json | UiDriver.start_app(bundle) 不能自动识别主 Ability；停止后未启动，后续入口前置不成立 | 显式 page_name=EntryAbility；未进入恢复步骤，A 项未验证。 |
| attempt02/harness.log / harness-report.json | 当前 Hypium 不存在 scroll_to；保存按钮半截可见、结果区在屏外，不能据找不到结果判产品失败 | 实际 API 签名记录 hypium-actual-api.txt；改有界 UP/DOWN swipe 后重查稳定 id，目标完整处于可用视口才操作，保存结果同样滚入后按 id 精确读原文。 |
| 18989 转发清理早期命令 | rport rm 或带一个含空格的 task 参数不被本机 hdc 接受；输出 Fail 但 exit 0 | 实证正确命令 fport rm tcp:18989 tcp:18989；仅清本题新增转发。hdc helper 检查 Fail 文本语义，保留其余转发。 |

所有自测工具修正后都重新安装同一冻结源码构建的 HAP 再运行。早期失败与 skip 保留，不通过覆盖日志消失，也不计作功能通过。

## 当前实测进度

`attempt03-smoke/test-process.json` exit 0，HarnessTestCase 的两轮 D1 打开/取消（含实际重开）全部断言通过，服务器累计 0，mock 已停止、本题转发删除成功。此短用例不替代完整矩阵。

`attempt04-full` 正在运行完整 Hypium。非空哨兵准备因首页有两个全局箭头被工具拒绝，未写数据；保存前置截图证实真实本地空态，可用于空态边界。待完整轮结束后，按实际唯一“未选择词书”入口修正数据准备，再重新安装并补测非空 A16；当前 A16 仍 blocked，不能据零请求或空数据判通过。

## 判定与限制（待完成）

最终报告将逐项填写 A1—A19 的 pass/fail/blocked/not_run、证据路径和边界；U1—U6 保持实现边界/回归来源，不改成 Spec 明文。D2 没有安全有效备份时为 not_run，不妨碍核心取消需求的独立结论。不运行或声称官方隐藏测试/评分。
