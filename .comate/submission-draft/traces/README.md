# traces/ 说明（sym-combo-customize）

范围仅限会话表所列两个会话：

| 引擎 sessionUuid | IDE 侧边栏会话 ID | 阶段 |
| --- | --- | --- |
| `3533c74c-e720-4295-b5c9-52f73239dd5d` | 【待补充】（查询未得到） | 阶段 0 分析 |
| `b069b19e-996e-4c07-bc76-8ee98441ff63` | 【待补充】（查询未得到） | 阶段 1 开发与自测 |

- `raw/chat_session_<uuid>`：引擎原生会话明细（JSON），原样复制。
- `raw/blobs/chat_session_<uuid>.d/`：明细中 `$blob` 引用的外置内容，文件名为内容 SHA-256；含 `.detail-prev-*` 历史快照。
- `raw/comate_chat_sessions.filtered.jsonl`：从引擎会话索引按 sessionUuid 精确过滤的原始行。
- `md/<uuid>.md`：由明细渲染的 Markdown 副本（脚本生成，非 IDE 导出），含推理、文本、工具调用参数与结果，未删减。
- `code-snapshot/`：`git-state.txt`、`project-files.sha256`、`modified-files/`、`hypium_tests/`。

详细字段说明与失败 / 重试定位见 `tasks/sym-combo-customize/trace-index.md`。
