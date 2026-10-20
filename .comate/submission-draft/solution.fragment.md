# cml-spec1 汇总片段

团队：HC2026-111 / Ghost_London，阶段online；版本、联系人、成员实名分工、团队冻结时间及来源保护声明均【待补充】。这是单题材料草稿，没有上传、邮件或正式赛事提交。

完成内容：四底部标签点击与双向滑动联动、选中状态、有限Lottie动画、离选复位、首页内容/滚动及重复选中回顶、空购物车/未登录状态和冷暖启动。独立run-r4在原模拟器8/8通过，44项本地验收通过（28明文、11派生、5批准策略）。原始报告及命令见tasks/cml-spec1/project/workflow/verification/do-result-r4.md和tasks/cml-spec1/logs/selftest-run-r4.json；未运行官方隐藏用例，无官方评分结论。

AI实际参与：主Agent调度需求、方案、编码、自测四角色，基线探索、失败归因、Swiper索引修复、设备动态采帧、回归与材料审计均有原生记录。gpt-6.1-sol/xhigh和每个分段实际token字段见traces/cml-spec1/native-manifest.json。分析与功能会话分开，本次材料四角色报告不能替代之前解题证据。

未完成项与已知问题（提供者）：【待补充】。已有证据的局限须保留：历史一次LIFECYCLE_TIMEOUT根因未完全排除，改进停止夹具后最终8组未复现；截图工具局部有界重试不重放业务动作；官方隐藏测试不可见；原有182条文件诊断无新增。不存在文本输入/必需联网分支，因此不声称相关注入测试通过。

人工直接改码声明：【待补充】；现有日志中的用户设备选择和权限操作见tasks/cml-spec1/human-changes.md，不推定操作人姓名。额外来源完整声明：【待补充】；已证实的依赖和公开文档查询见根sources.md的cml-spec1来源条目。实际来源边界规则见tasks/cml-spec1/project/AGENTS.md、tasks/cml-spec1/project/system-config/快照；团队source_guard空白仍待确认。本轮范围扫描失误与排除边界公开记于tasks/cml-spec1/trace-index.md及traces/cml-spec1/README.md，不能声明从未触及混合初始化文件的任何字节。

生产冻结：688文件聚合2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c，HAP d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615；本阶段生产文件零变化。完整工程提交快照：11951 文件，完整项目聚合 SHA-256 `e1c8f2286ca9f93ca33bb094356bd415f53efa80a857baf8d2d22ce699ee870a`，包括本题过程文件。差异从基线生成，校验记录见tasks/cml-spec1/validation/patch-validation.json；这不是团队成果冻结时间。

成果冻结时间（北京时间）：【待补充】。3-package负责团队级文件、系统配置汇总和ZIP；应使用本文指定的工程快照及最终导出的本题原生记录，先补齐人工声明，再冻结打包。
