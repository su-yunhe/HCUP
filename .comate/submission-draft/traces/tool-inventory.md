# 实际工具和 Skill 证据

| 原生线程 ID | 实际顶层工具调用名及次数 |
| --- | --- |
| `01a1447d-ff45-7802-986d-1bc93f60db1c` | exec=37, spawn_agent=2, send_message=7, wait_agent=1, list_agents=1 |
| `01a1447f-1e68-7d61-8a9c-bdce1f715686` | exec=11, send_message=2 |
| `01a1447f-6645-73d2-853c-540c0da81e11` | exec=30, send_message=7 |
| `01a1448f-dc21-7c42-a6c5-731bc0a5c14e` | exec=74, spawn_agent=4, list_agents=2, send_message=25, sleep=37 |
| `01a14490-c05f-7bf3-a763-fefb443417ae` | exec=10, send_message=1 |
| `01a14491-f121-7960-a9b6-155ce2b272d8` | exec=12, send_message=4 |
| `01a14492-d90e-7c23-aa1e-0deef1467f23` | exec=68, send_message=17, sleep=11 |
| `01a14496-c173-76b3-ac93-888a4286fe9d` | exec=16, send_message=5 |
| `01a144bb-b227-7933-8cef-05d447b96e83` | exec=32, spawn_agent=1, followup_task=1, send_message=2, list_agents=1 |
| `01a144bd-8665-7712-93a5-de24724c416c` | exec=24, send_message=8 |

顶层 `exec` 包含组合调用，具体 `exec_command`、`apply_patch`、`clock` 等及其参数/返回应按原生日志读取，不能将顶层计数当各嵌套工具次数。原生 `custom_tool_call_output` 也完整保留。失败和重试不会因计数方式而省略。

实际读取过的 Skill：`harmony-task-flow`、`hmos-arkts-knowledge-retriever`、`hmos-arkts-syntax-checker`、`arkts-syntax-assistant`；逐会话路径和实际调用行在 `manifest.json` 的 `tool_evidence` 与 `skill_reference_strings`。其中工具目录检索曾缺 `references/doc_index.json`，随后直接读安装包内 ArkTS 语法文档，见编码交接及原始工具返回。初始 `system-config/` 只保留当时已复制的配置，不声称包含每个 Skill 独立目录的完整历史快照；其他实际读取内容仍在原始会话中。

开发各会话与本材料会话的 `turn_context` 均记录模型 `gpt-6.1-sol`、effort=`xhigh`、approval_policy=`never`、sandbox_policy=`danger-full-access`；更细模型修订号未输出。Skill/角色配置实际内容可由工程 `system-config/initial-20261016T113216Z/` 及会话读文件返回交叉定位。
