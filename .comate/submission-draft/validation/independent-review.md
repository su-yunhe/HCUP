# vg-spec8 独立材料审核（revision 2）

**2-submit 草稿准备校验 pass；正式团队提交就绪 blocked。** 用户空字段按要求待补，草稿工作已完成。没有重新构建、运行设备或复测产品功能，也没有改生产、Spec、state 或冻结材料；只写本 validation 目录。

最终独立 fresh clone 仅取本地 `base/vg-spec8` / `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，禁用全局/系统Git配置及换行、filter等属性。`git apply --check --binary` 与真实 `git apply --binary --whitespace=nowarn` 均 exit 0；脚本 exit 0。冻结工程前后与重建工程的 **1991 文件**路径、大小、SHA-256全部一致。

- 补丁：**299361773 bytes**，SHA-256 `7a88908dc1a6b79c31f3f71bdc100de7a83991f223a64bd6013d3fe83e78eeb2`。
- 工程清单 SHA-256：`444b98d793f8d057a33490bedb3b4f8056b9fd068602e2a7a26c193ffaeb8520`；本轮前后未变。
- 258 个生产输入与实现冻结一致，指纹清单 SHA-256 `cff0ff9567ae804b76c12add8b9989e95d37c89c18152b99b3fc3b09f4e85f5f`。
- 官方索引24字段齐全；JSON三路径映射正确、后两项是文件；build.md无私有绝对路径；14份本题native逐行可读且header/行数/hash一致；756条原日志及失败重试逐字节保留；另有合法复制索引；397项二进制摘要正确，8项基线同源。

| 约束 | 核对内容 | 结论 |
| --- | --- | --- |
| C1 | 不得编造，用户空字段保持待补 | pass |
| C2 | 完整binary差异可应用并对应全部工程真实文件 | pass |
| C3 | 二进制路径、大小、SHA与基线同源声明 | pass |
| C4 | 排除构建缓存与Git元数据，公开排除边界 | pass |
| C5 | 只摘本题主子会话，按目录和题号查找 | pass |
| C6 | 字面要求Comate引擎sessionUuid与IDE双ID | blocked |
| C7 | 保留失败、重试与未采用过程 | pass |
| C8 | 记录公共任务书版本与本题历史 | pass |
| C9 | JSON三路径为包内相对路径且后两项为文件 | pass |
| C10 | 如实披露来源、人工、脱敏与记录缺失 | pass |

C6 字面Comate双ID无法提供，因为实际使用Codex。真实Codex thread ID与可继承的native session ID已核对并说明；这不构成Comate双ID。官方适用性应在后续提交处理中判断，不能补造。

本审核发现并退回了两项真实问题：初版错误纳入40字节 `.git` 指针（1992/1991不一致）；来源首段超出已核验AI记录范围作全题保证。父Agent分别修正派生边界和3个材料/生成器文件，原工程Git指针未动，业务输入未动；第二轮与最终第三轮均从新clone复验。失败清单、旧补丁、原始命令/日志和来源问题复现记录均保留。日志检查器自身对 `copy-manifest.json` 的两次集合预期错误也保留，没有删除原始日志断言。

技术ID/原生导出开始为 `2026-10-16T15:23:39.879380+00:00`；本材料修订冻结为 `2026-10-16T15:40:46.107375+00:00`。二者不同，团队正式冻结时间仍是 **【待补充】**，不得互相代填。

仍需人工补充：版本、联系人、团队正式冻结时间、成员与分工、来源保护声明、人工修改、已知问题、额外来源、IDE Markdown目录；3-package还需团队题目集合与ZIP输出。缺失/不适用项包括Comate双ID、官方指定准备日志、独立模型构建号及历史工具精确版本，均如实披露。原生轨迹只到明确截点，之后修订和本审核尾部须由3-package另存；混合总览原文未提交。

本轮复验只覆盖受影响材料和必要完整补丁/文件/生产指纹检查；其余材料证据通过两版清单逐项确认字节未变而继续适用。既有A1—A19结论仅被当作历史材料引用，本轮功能测试为 not_run，不能据此声称官方成绩。

证据：[最终重建](independent-rebuild/round03/reconstruction-result.json)、[命令及退出码](independent-rebuild/round03/commands.json)、[修订复验](independent-rebuild/revision2-check-result.json)、[24字段等材料检查](independent-rebuild/material-check-result-before-source-scope-fix.json)、[完整机器报告](independent-review.json)。每条Git命令的原始stdout/stderr在同轮目录。后续保留所引用的JSON、脚本和原始日志，排除临时baseline clone、.git和缓存。
