# 返回重进回归及证据有效性

旧版本：source `8e377669fb468989fa2103e2987137d50320f9df9c1937c5cbd2f9ca392ff7a7` / HAP `521ac47d8244aee9709f3de1e2a2bde95f99986d76eac2f0e7a5c453d8aaed8a`。

最小复现：首次从“我的”点击登录入口进入登录主页 → 系统返回 → 等待至少1秒 → 再点击同一真实入口。期望再次进入登录主页；实际停留在“我的”。`logs/verification-phone-suite-02/reentry-after-interruption.jpeg` 来自旧完整测试进程结束后的独立UiDriver单次点击，距前次操作已数分钟，仍复现。关联 D4/E11、A1真实入口可持续使用；不能把后续A2等因前置失败的连锁FAIL当作各显示元素各自未实现。

首次完整轮的 A01 曾标 ok，但其原始树是横移动画过渡帧（页面可见却半屏裁切），随后JPEG实际已返回“我的”，该A01通过作废。原始 `hypium-runner.stdout/stderr.txt` 保留全部输出；只结束精确核实的自身harness子进程，退出码4294967295。测试期间生产未变化，但该轮中断且有测试稳定性问题，不纳入最终通过统计。

受控复现 `logs/verification-navigation-diagnosis-02b/` 重新安装旧HAP，只有一个5555 UiDriver，关键导航步骤前没有外部dumpLayout；steps.json记录首次进入1秒后page/logo=true、返回1秒后entry=true、再点击1.2秒后page/logo=false，native first-entry/reentry.jpeg保留像素。末尾生产指纹断言失败：主调度在此诊断尚未结束时修改MeViewModel，因此该轮不能作为新源码验收证据，原样保留为旧已安装HAP的失败观察，不宣称新版本通过。另02初次诊断native capture_screen误用PNG而被库拒绝，原日志保留，02b修为JPEG。

归因：原MeViewModel持久pending防重依赖嵌套onShown重置，真实返回路径未释放。证据强度：重复点击无导航的像素/树为强；生命周期归因经主调度/方案静态会诊确认。已交主调度路由最小修复，验证角色没有修改生产。

新v1.2：source `26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e` / 独立全量构建HAP `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`。`logs/verification-navigation-smoke-03/selftest.json` 两用例通过（49.787秒）：稳定A01和同一UiDriver内3次重进，包含普通点击、登录区域三连点、实际头像Image三连点。每次返回等1秒，目标连续3样本保持实际窗口满宽，native JPEG、实际UI树与页面截图均确认目标。源码与本轮冻结的测试助手指纹首尾一致。后续正式手机及三类实际窗口证据另见最终报告；该最小回归本身不是41项整题通过证明。
