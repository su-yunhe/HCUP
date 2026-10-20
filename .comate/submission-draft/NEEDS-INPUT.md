# 仍需用户补充

以下来自输入文件的空字段，未推测，所有正文统一标记【待补充】：

| 来源 | 字段 | 需要的事实 |
| --- | --- | --- |
| common/spec-harness/team.yaml | version | 成果包版本 |
| 同上 | contact | 联系人及联系方式 |
| 同上 | freeze_time | 正式成果冻结北京时间，阶段3统一 |
| 同上 | members[].name / work | 成员姓名及实际分工 |
| 同上 | source_guard | 实际来源保护措施 |
| spec/submit-input.yaml | human_edits | 无人工直接改代码的确认，或操作人/目的/文件/前后版本/原始证据 |
| 同上 | known_issues | 用户确认的未完成项和已知问题；已观测测试限制已另行如实列出 |
| 同上 | extra_sources | 额外来源、复用及人工来源访问情况，不能留空推断“无” |
| 同上 | md_export_dir | 若有IDE导出的Markdown，提供目录；当前附明确标记的派生副本 |

需要补齐或确认的原始记录缺口：指定题包基线准备报告不存在；如持有原报告可补入。Comate专属sessionUuid/客户端/扩展版本没有真实来源，本次用Codex原生证据，不得编造。独立桌面GUI版本、精确后端模型版本和未核实工具独立版本保留待补充，若运行器本来不输出应说明不可获得。

`submitted_tasks`、`attempted_not_submitted`、`zip_out`是阶段3专用字段，本阶段不代填。官方最终成果冻结和完整活跃会话尾部导出也由阶段3在停止相关任务后处理，不得用新记录替代原解题证据。
