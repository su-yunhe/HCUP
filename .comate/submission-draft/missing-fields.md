# 仍需提供者补充的字段

- `team.version`：**【待补充】**，成果包版本。
- `team.contact`：**【待补充】**，联系人姓名及邮箱/电话。
- `team.freeze_time`：**【待补充】**，北京时间成果冻结时间。
- `team.members[].name`：**【待补充】**，成员实名。
- `team.members[].work`：**【待补充】**，成员实际分工。
- `team.source_guard`：**【待补充】**，提供者的实际来源保护措施声明。
- `task.human_edits`：**【待补充】**，是否人工直接改码及已有证据。
- `task.known_issues`：**【待补充】**，提供者确认的未完成项与已知问题。
- `task.extra_sources`：**【待补充】**，提供者确认的完整额外来源使用声明。
- `task.md_export_dir`：**【待补充】**，IDE侧边栏Markdown导出目录；当前提供原生转换副本。

以上来自../common/spec-harness/team.yaml及spec/submit-input.yaml的空字段；members的name/work为两个原字段。team_id、team_name、stage、task_id已有值。submitted_tasks、attempted_not_submitted、zip_out只属3-package，本阶段不擅填。

客观证据缺口：官方指定reports/build-baselines/cml-spec1.log缺失（本地准备输出已保留）；Comate引擎sessionUuid/客户端扩展字段不存在于当前Codex运行器；模型精确服务构建版本与未暴露参数无法核实。没有用示例UUID或版本替代。当前Codex应用版本仅是现状查询。活跃材料会话最终导出由3-package冻结时补齐，不能称本次时间点副本包含之后事件。
