# cml-spec1 独立自测首失败 r1

本轮按主 Agent 正式冻结及 11245 独占授权运行；已停止设备操作，交还修复。未改生产代码、需求或全局状态。

## 已完成的独立前置

- `clean`、`assembleHap` 均退出 0；完整命令/时间/原始日志在 `logs/verification-do-build-run-r1-commands.json` 及对应 `*-clean.log`、`*-assembleHap.log`。
- 独立 debug HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，20,739,858 bytes，SHA256 `751cf14d962ceda900ad9179d90d26e5e769e619558456f1296a073f9dfdfd6b`，记录 `traces/verification-do-r1/independent-hap-r1.json`。与编码包哈希不同，实测始终安装本轮独立产物。
- 安装明确成功，退出 0，bundle updateTime 绑定在 `logs/verification-do-install-run-r1-installed-bundle.log`；runner 前重新安装，记录 `logs/verification-do-run-run-r1-install-current-hap.log`。
- 182 条带文件诊断与基线多重集增删均 0，其他 WARN 行也增删均 0：`traces/verification-do-r1/independent-warning-compare-r1.json`。没有 BuildProfile.ets diff。
- 实际设备 11245，HarmonyOS emulator 6.1.0.115/API23，首屏原始图 1308×2880；正常入口出现四标签、默认首页与顶部领取，没有麦克风弹窗：`traces/verification-do-r1/first.{png,json}`。初始 A1/A2/A3 的实际断言已通过，不以构建替代。

## 业务失败：A4 单次点击分类后回到首页

最小复现脚本：`traces/verification-do-r1/repro-tab-reset.py`，执行退出 0。该脚本只发下面一组应用操作，不使用 Hypium 查找/点击辅助，不运行网络注入或额外手势：

1. `hdc -t 127.0.0.1:11245 shell aa force-stop com.joker.coolmall`
2. `hdc -t 127.0.0.1:11245 shell aa start -a EntryAbility -b com.joker.coolmall`
3. 等待 2 秒，捕获初始树/截图。
4. `hdc -t 127.0.0.1:11245 shell uitest uiInput click 490 2671`（由本次树的 `main_tab_category` bounds 中心计算）。
5. 不再输入，等待 0.5 秒，捕获最终树/截图。

期望：分类为当前活动页且保持选中。实际：同一 `instanceId=main-1792472377459`，根/分页 `selectedIndex=0`，`selectionEpoch` 从 1 变 3；首页 selected=true、分类 selected=false，最终图像仍是首页。A4 为 `fail`，后续依赖点击切页、动画、颜色不能顺带写为通过。

证据（均在 `traces/verification-do-r1/repro-tab-reset-r1/`）：`commands.json` 保存逐 argv、起止时间、退出码和原文，命令均退出 0；`before.json/after.json`、`before.png/after.png`、两个 `*-summary.json`；`source-before.json/source-after.json` 为相同 688 文件，变化 0。另有首轮 Hypium `failure.json/png` 的同样 epoch 1→3 结果。

行为结论证据强度：高（原生单次动作、同实例前后树、截图、源码及 HAP 绑定）。归因假设：`MainPage.ets` 的 `.index(0)` 可能在 vm 提交后重渲染，将 Swiper 重设首页；epoch 1→3 与一次分类提交再首页提交相符。归因证据强度：中（尚未加逐回调埋点或修改验证）。建议退回编码局部修复索引绑定，由主 Agent 决策；修复后新冻结并独立 assemble、安装，再跑全部脚本。

## 独立保留的测试工具故障

- `snapshot_display -f *.png` 在本设备只支持 jpeg，错误文本出现但 hdc 退出 0。失败原文保留在 `logs/verification-do-probe-run-r1-first-screen.log` / `*-recv.log`；正常静态首屏改用 uitest PNG，批量真实帧改为原生 JPEG。执行辅助现在也检查文本 `[Fail]` / `error:`。
- 首轮采样读取 `/proc/uptime` 被设备拒绝，导致时间记录不完整。已终止经命令行身份核验的本题 runner，保留 `logs/selftest-run-r1-interrupted.json`、完整 runner 日志与各 capture-raw.log；这是主动中断，不能宣称整套完成或零失败。工具问题不等于业务通过。
- 已只修测试辅助为 `date +%s.%N`（本设备实测可读），未降低三种真实图标形态、实际引擎帧、有限一次播放、第一帧静止或无新增播放断言；修订后的完整设备套件尚未重跑。业务失败由上述独立原生命令确认，不依赖损坏的帧时钟。

逐 A 的本轮中途状态：`traces/verification-do-r1/a-status-pre-fix-r1.json`。未运行/受阻项没有记为通过；这不是最终验收，也没有官方成绩推测。
