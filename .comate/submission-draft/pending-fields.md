# 仍需用户补充的字段

输入空字段均按【待补充】保留，没有以测试时间或 Agent 推断代填。

|输入|字段|用途|
|---|---|---|
|common/spec-harness/team.yaml|version|成果包版本|
|同上|contact|联系人及联系方式|
|同上|freeze_time|团队成果冻结时间（北京时间、精确到分）|
|同上|members[].name|成员姓名|
|同上|members[].work|实际人工分工|
|同上|source_guard|团队实际来源保护措施|
|spec/submit-input.yaml|human_edits|人工是否直接改码；有则操作人、目的、文件、前后版本与原证据|
|同上|known_issues|用户确认的未完成项、已知问题（技术局限已另行披露）|
|同上|extra_sources|用户确认的额外来源（已识别来源仍据实列出）|
|同上|md_export_dir|用户从侧栏原生导出的 Markdown 目录；现有副本是机械转换|

3-package 才使用的 submitted_tasks、attempted_not_submitted、zip_out 未在本阶段代填。

客观记录缺口：指定官方 baseline log 未找到，但本题准备和构建日志可用；未发现 Comate 数据库、macOS product.json 或 Comate 扩展，不能制造 Comate 专有双ID/版本。已提供真实 Codex 引擎UUID与IDE thread ID映射及版本。是否另需指定客户端格式由用户决定。当前活跃会话是导出时快照，不能覆盖未来尾部。sources.fragment.md 中额外标注的许可证/历史事件精确范围属于待核信息，不是已经取得的事实。
