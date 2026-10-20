# 仍需用户补充的字段

以下空值均未推测。来源为 common/spec-harness/team.yaml 与本题 spec/submit-input.yaml。

| 文件 | 字段 | 当前产出处理 |
| --- | --- | --- |
| team.yaml | version、contact、freeze_time | 【待补充】；生成时间没有用作冻结时间 |
| team.yaml | members[0].name、members[0].work | 【待补充】 |
| team.yaml | source_guard | 【待补充】；另据记录说明实际提示约束 |
| submit-input.yaml | human_edits | 【待补充】；不推断无人改码；如有需真实证据 |
| submit-input.yaml | known_issues | 【待补充】；已另列日志中的覆盖限制 |
| submit-input.yaml | extra_sources | 【待补充】；已另列可查来源 |
| submit-input.yaml | md_export_dir | 【待补充】；已提供机械生成 Markdown，未冒称 IDE 导出 |

仅 3-package 使用的 submitted_tasks、attempted_not_submitted、zip_out 也未提供，留待该阶段。本题 JSON 片段的 submitted 是供选用的条目，不替代团队的正式提交选题。

客观证据缺口：Comate 专属 sessionUuid 与客户端/扩展版本未在此 Codex 运行器产生；历史客户端包完整版本、OHPM/Hvigor/JBR 独立版本、未输出的模型参数无法核实。适用时提供原始记录；不适用时由团队最终说明运行器差异，不填造假的 Comate 字段。指定官方 baseline log 缺失，已有本题本地 prepare/build 原始日志，不需要重跑去伪装历史原件。

材料会话导出后仍有活动；3-package 正式冻结时需再次导出本轮材料会话并登记封口。原始研发记录已保留。
