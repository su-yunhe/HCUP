# 仍需补充的字段

| 输入 | 未提供字段 | 填写规则 |
| --- | --- | --- |
| common/spec-harness/team.yaml | version、contact、freeze_time（北京时间）、members[].name/work、source_guard | 全部【待补充】；不以材料生成时间代替冻结时间，不自动推断成员/来源保护完整声明。 |
| spec/submit-input.yaml | human_edits、known_issues、extra_sources、md_export_dir | 全部【待补充】；空白不代表无修改/无问题/无额外来源；Markdown转写不冒充IDE导出。 |

以下客观项已经自动查找，现有文件仍不能补齐：Comate sessionUuid/IDE双ID映射（当前实际为Codex）、任务书Mac客户端/Comate扩展版本（当前Windows）、各历史时刻桌面GUI版本、模型未公开的精确权重版本/运行参数、Comate appliedRuleNames、官方基线报告及脚本精确哈希/起止时刻、历史helper05/06缺失诊断字段。当前Windows OpenAI.Codex安装包版本26.1013.4894.0已通过Get-AppxPackage核实，见audit/client-version.json。只能补当时已有真实证据或说明不可得，不补造/不以新日志替代旧记录。

3-package阶段另需填写submitted_tasks、attempted_not_submitted、zip_out；本阶段不选择其他题、不生成团队文件或ZIP。最终冻结时更新本次材料会话截点、核对敏感信息，并按project-manifest复制工程。原manifest引用的14份混合初始化会话已排除，不能把这些引用误报成开发记录缺失。
