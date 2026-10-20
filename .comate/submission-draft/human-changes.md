# cml-spec7 人工操作与修改索引

`spec/submit-input.yaml.human_edits` 为空，人工直接改码声明为 **【待补充】**。目前不能填写“无人工直接修改代码”，也不能由总体diff推算作者或代码占比。

用户已通过本题原生会话提供任务、约束及后续选择；这些人工提示保留在 `traces/native/*.jsonl` 的消息对象，机械可读副本为 `traces/markdown/*.md`，逐会话路径、哈希、事件截止与关联关系见 `traces/session-metadata.json`、`trace-index.md`。提示不自动等于人工直接编辑源码。

若存在人工直接改码，仍需补充每个实际操作批次：操作人、目的、文件、修改前后真实提交/快照/摘要、差异及当时留存的原始编辑历史或记录路径，均为 **【待补充】**。不能在整理阶段制造当时不存在的过程证据。

AI修改、构建和修复的既有证据见 `workflow/implementation/`、`workflow/verification/` 及原生工具调用；`changes/final.diff` 仅证明总体交付差异，不单独证明人工操作。团队 `members[].name/work` 仍为 **【待补充】**，不从设备用户名推断人员。
