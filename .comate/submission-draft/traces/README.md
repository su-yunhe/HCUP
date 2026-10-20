# 本题轨迹读取说明

本目录在3-package移动到包根`traces/vg-spec1/`。`sessions.json`逐会话列真实Codex原生UUID、父子关系、IDE索引映射、模型/effort、最后token累计值、工具计数、源文件与导出文件SHA、截点及删节行；`filtered-session-index.jsonl`仅含本题已有IDE索引行；`native/*.jsonl`是保留原生事件结构的本题副本；`markdown/*.md`是脚本转写的可见消息/工具副本；`code-snapshot/`保留6份当前变更生产组件；`code-edit-index.json`指向原生修改工具行。

导出器是`tools/export_traces.py`（3-package应保留到任务审计工具目录）。它分别按精确工程路径与精确题号边界检索，候选只读首行metadata；仅纳入cwd精确为本题的会话。其他工作区命中仅计数，不导出正文。初始化总览被排除。Comate store不存在，不冒充Comate sessionUuid/IDE双ID；Codex根会话UUID与sidebar字段仅在session_index实际有相同行时建立对应，子会话只凭thread_spawn映射父子关系。

本副本保留可见实际提示、函数调用/工具输出、失败重试、配置和上下文事件；内部模型推理记录未纳入可见材料，逐会话redactions列出源行号/摘要；本次整理中一次宽匹配检索打印的无关命中元数据亦剔除并登记。Markdown不是IDE“导出本地”的原生导出，用户md_export_dir尚为空。历史项目内已有的本题原生阶段快照也保留在project/traces/native，混合初始化原文不随项目投影携带；旧manifest引用这些被排除的初始化文件时以排除清单为准。

导出不包含整个客户端数据库、auth/config秘密文件。JSONL只表示当时截点，活跃会话末尾可能未写完；最终材料/打包操作仍会产生新事件，需3-package最终冻结时更新本阶段相关会话截点，不能声称包含未来消息。源文件未被修改；正文、提示、工具返回不作有利改写。此为离线本题材料草稿，尚未作全量秘密扫描或对外提交。
