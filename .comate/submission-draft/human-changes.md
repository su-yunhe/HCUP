# vg-spec13 人工操作与修改索引

`spec/submit-input.yaml:human_edits` 留空：【待补充】。不能据 AI 会话或 Git 差异推断“无人工直接修改代码”。请补充人工操作人、目的、文件、前后版本和当时原始证据；若确认没有直接改代码，由用户填写该声明。

已知人工提示可按主/子会话原生轨迹中的 user 消息读取；AI 改动与失败重试可按 `trace-index.md` 和 `changes/final.diff` 读取。这些记录不自动证明其他人工操作不存在。整体 final.diff 不作为人工贡献归属证明。
