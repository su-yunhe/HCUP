# 仍需用户补充或确认适用性的字段

所有未提供项保持【待补充】，本轮不以猜测填充。

| 字段 | 来源 | 当前缺口 |
| --- | --- | --- |
| 团队成果包版本 | common/spec-harness/team.yaml: version | 空 |
| 联系人姓名及联系方式 | common/spec-harness/team.yaml: contact | 空 |
| 正式成果冻结时间（北京时间精确到分） | common/spec-harness/team.yaml: freeze_time | 空；不可用快照时间代填 |
| 成员姓名及实际分工 | common/spec-harness/team.yaml: members[].name/work | 空 |
| 实际来源保护措施 | common/spec-harness/team.yaml: source_guard | 空；若确未配置需用户明确声明 |
| 人工直接改代码声明／真实修改证据 | spec/submit-input.yaml: human_edits | 空；如有请给操作人/目的/文件/前后标识/当时证据，如无请明确声明 |
| 未完成项与已知问题声明 | spec/submit-input.yaml: known_issues | 空；已观察到的技术限制已另列，不替用户填无 |
| 完整额外来源使用声明 | spec/submit-input.yaml: extra_sources | 空；不能推断为无 |
| IDE侧边栏Markdown导出目录 | spec/submit-input.yaml: md_export_dir | 空；已提供标注来源的机械Markdown，可由用户判断是否另需侧边栏导出 |
| Comate会话sessionUuid、客户端/扩展版本的适用说明 | 指定Comate库不存在，Windows上指定macOS product.json路径不适用 | 本机未产生；已给Codex原生线程与真实父侧边栏关联，请按实际运行器说明 |
| Codex桌面客户端/IDE扩展精确版本及更细模型修订 | 原生只有CLI 0.162.0-alpha.17.2和模型ID；exe版本字段为空 | 未核实／运行器未输出；不填造 |
| 基线prepare脚本精确版本/起止时间或指定原报告 | 指定reports/build-baselines/vg-spec9.log不存在 | 本题prepare日志及setup结果已保留；不越界补取其他题包目录 |
| 未记录的人工配置/设备操作及可能的跨工作区本题会话 | 当前受限取证只能精确关联本题cwd/登记ID；其他工作区候选不展开 | 请用户仅在实际存在时给本题记录；不要求编造不存在的记录 |

仅阶段3使用的 submitted_tasks、attempted_not_submitted、zip_out 也为空，留给团队打包阶段决定；本轮没有读取其他题。正式冻结前需导出活动材料会话的最终截点，不能用新记录替换原始解题证据。
