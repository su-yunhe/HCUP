# 仍需补充的字段

| 字段 | 当前值 | 原始输入 | 需要补充 |
| --- | --- | --- | --- |
| `team.version` | 【待补充】 | `common/spec-harness/team.yaml` | 成果包版本 |
| `team.contact` | 【待补充】 | `common/spec-harness/team.yaml` | 联系人姓名及邮箱/电话 |
| `team.freeze_time` | 【待补充】 | `common/spec-harness/team.yaml` | 团队成果冻结时间，北京时间；本地快照时间不能代填 |
| `team.members[].name / work` | 【待补充】 | `common/spec-harness/team.yaml` | 人员及实际分工 |
| `team.source_guard` | 【待补充】 | `common/spec-harness/team.yaml` | 团队来源保护措施声明；本题实际配置另列 |
| `task.human_edits` | 【待补充】 | `spec/submit-input.yaml` | 人工直接改代码声明或逐批证据 |
| `task.known_issues` | 【待补充】 | `spec/submit-input.yaml` | 用户补充的已知问题；本地客观限制另列 |
| `task.extra_sources` | 【待补充】 | `spec/submit-input.yaml` | 额外来源声明；已观察来源另列 |
| `task.md_export_dir` | 【待补充】 | `spec/submit-input.yaml` | IDE侧边栏人工Markdown导出目录；已生成JSONL可读转换副本 |
| `team.submitted_tasks / attempted_not_submitted / zip_out` | 【待补充】 | `common/spec-harness/team.yaml` | 仅3-package使用，不推断团队其他题或输出路径 |

其他缺失/不适用：Comate双ID本次不存在，不能补造；官方指定基线准备日志路径不存在，仅有本题实际准备记录；未取得独立模型构建版本和Comate扩展版本。活跃会话只导出到明确截点，3-package冻结时需保存之后的新记录。

自动测试保留固定开发机ROOT与安装清单门槛，本阶段未改；若需任意目录自动重跑，须另行适配测试脚本。当前手工场景及App构建命令可按build.md复现。
