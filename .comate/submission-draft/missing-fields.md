# cml-spec17 待补充字段与客观取证缺项

这是允许留空的提交草案清单；不以“无”替代未提供信息，也不因此停止可完成的自动取证。

## 用户仍需补充

| 输入字段 | 草案值 | 需要的内容 |
| --- | --- | --- |
| team.yaml / version | 【待补充】 | 本次成果包版本 |
| team.yaml / contact | 【待补充】 | 姓名与邮箱/电话 |
| team.yaml / freeze_time | 【待补充】 | 北京时间、精确到分的正式成果冻结时间；不是1-do完成或材料快照时间 |
| team.yaml / members[].name | 【待补充】 | 真实成员姓名 |
| team.yaml / members[].work | 【待补充】 | 成员实际分工；不能用Agent角色代填 |
| team.yaml / source_guard | 【待补充】 | 团队实际采取的来源保护说明 |
| submit-input.yaml / human_edits | 【待补充】 | 明确无人工直接改码，或逐批说明谁/目的/文件/前后标识/当时证据 |
| submit-input.yaml / known_issues | 【待补充】 | 用户补充的未完成/已知问题声明；已有9项not_run与认证后端blocked仍自动披露 |
| submit-input.yaml / extra_sources | 【待补充】 | 额外来源、用途、证据；“无”须由用户明确提供 |
| submit-input.yaml / md_export_dir | 【待补充】 | 用户侧边栏导出的Markdown目录；自动生成便读副本不代填 |

已经提供并保留的团队字段为 `HC2026-111`、`Ghost_London`、`online`。`submitted_tasks`、`attempted_not_submitted`、`zip_out` 只在第3阶段使用，本轮不代填其他题目状态，也不以它们阻止单题材料整理。JSON片段中的submitted是本题拟提交候选，团队列表尚未确认。

## 自动取证的缺项、不适用项与截点

| 项目 | 客观状态和处理 |
| --- | --- |
| 指定官方基线日志 | 允许的 `reports/build-baselines/cml-spec17.log` 精确路径不存在，官方原日志为【待补充】；已有本地prepare-baseline、baseline-build和setup-result单独引用，不冒充官方日志 |
| 基线准备脚本源码版本 | 本地profile为harmony-cup-build-v1，不能据此推出脚本源码版本；该版本【待补充】，本题setup-result另有真实准备时间 |
| Comate sessionUuid、索引、macOS产品/扩展版本 | 不适用：实际使用Codex，未使用Comate；不制造Comate记录 |
| Codex未输出的字段 | appliedRuleNames等字段以原生实际输出为准；字段缺席记“原生未输出”，不解释为未应用规则。未输出的模型内部信息不补造 |
| 原生与侧边栏ID | 以evidence-facts逐会话对应关系和过滤索引为准；未暴露的独立子会话侧边栏条目如实说明，不能抄父ID或制造第二UUID |
| Markdown来源 | 已自动生成者是JSONL派生便读副本，非用户侧边栏导出；用户导出目录仍待补充 |
| 原生记录截点 | snapshot_only=true、includes_future_events=false；最后完整行之后的消息及仍在进行的本轮最终回复不属于该快照，后续以新采集清单更新，不能声明包含未来事件 |
| 工程与材料冻结 | 完整project版本从changes/project-files.json取证，材料记录截点另列；最终用户freeze_time仍待补充，阶段3统一冻结后再核摘要 |
| 受控测试跨机迁移 | 历史脚本含原根目录、设备和环境入口固定配置；本轮未改工具或重跑迁移验证，适配点详见build.md |

其余自动字段、日志/摘要、模型/参数、真实ID、完整diff/二进制清单和回放由本题材料自动取证，不转成用户手填项目。当前能否通过材料终验由独立验证报告判定；草案存在不等于正式提交信息齐全。
