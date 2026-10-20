# 本题会话 ID 对照

本机实际客户端为 Codex Desktop；不存在指定 Comate 库，故没有可核实的 Comate `sessionUuid`，该字段为【待补充／本运行器未产生】。下表保留真实 Codex 原生线程标识及其 IDE 侧边栏关联，不能把它们改称 Comate 字段。主会话 `payload.id` 与过滤索引 `id` 相等；子会话 `payload.id` 是自身 ID，`payload.session_id` 是有侧边栏索引的父会话，`parent_thread_id` 与父调用共同补证。

| 阶段／角色 | Codex 原生线程 ID（引擎等效标识） | IDE 侧边栏 ID | 对应关系 |
| --- | --- | --- | --- |
| orchestrator | `01a1447d-ff45-7802-986d-1bc93f60db1c` | `01a1447d-ff45-7802-986d-1bc93f60db1c` | Native session_meta.payload.id equals the matched sidebar session_index.id. |
| harmony_requirements | `01a1447f-1e68-7d61-8a9c-bdce1f715686` | `01a1447d-ff45-7802-986d-1bc93f60db1c` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| harmony_verification | `01a1447f-6645-73d2-853c-540c0da81e11` | `01a1447d-ff45-7802-986d-1bc93f60db1c` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| orchestrator | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | Native session_meta.payload.id equals the matched sidebar session_index.id. |
| harmony_requirements | `01a14490-c05f-7bf3-a763-fefb443417ae` | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| harmony_design | `01a14491-f121-7960-a9b6-155ce2b272d8` | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| harmony_verification | `01a14492-d90e-7c23-aa1e-0deef1467f23` | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| harmony_implementation | `01a14496-c173-76b3-ac93-888a4286fe9d` | `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |
| orchestrator | `01a144bb-b227-7933-8cef-05d447b96e83` | `01a144bb-b227-7933-8cef-05d447b96e83` | Native session_meta.payload.id equals the matched sidebar session_index.id. |
| harmony_verification | `01a144bd-8665-7712-93a5-de24724c416c` | `01a144bb-b227-7933-8cef-05d447b96e83` | Child payload.id is its native thread ID; payload.session_id maps to the parent sidebar row; no separate child sidebar row. |

原生字段、父子路径、来源文件和哈希见 `manifest.json`；只有本题匹配索引行被复制到 `filtered-session-index.jsonl`。总览初始化会话未导出。
