# 本题轨迹读取方式

`native/<Codex线程UUID>.jsonl` 按行读取JSON，保留原生消息、指令、工具参数/返回、代码编辑、失败、重试及token统计。只有账号标识按 `redaction-policy.json` 脱敏；来源SHA与导出SHA各自记录在 `session-inventory.json`，两者不能混用。

Codex `session_meta.id` 是当前线程/侧边栏UUID，与实际 `CODEX_THREAD_ID` 对应。`session_meta.session_id` 是另一个原生关联字段，子会话可继承根会话值，详见清单的 `codex_engine_session_id`。它们不是Comate产品的 `sessionUuid`，缺失的Comate专属值未伪造。

`markdown/<UUID>.md` 是上述原生记录的逐条JSON包裹副本，用文本编辑器/Markdown查看器读取；由本次工具生成，并非IDE“导出本地”的文件。`session-index.filtered.jsonl`只含本题选中会话的元数据索引；筛选方法/候选数/缺失及排除见 `discovery.json`，没有打包整个客户端库。

`skill-read-index.json`列出工具输入中实际出现的SKILL.md读取动作，给出会话、JSONL行号、工具call_id、时间与实际路径；覆盖观察到的鸿蒙工作流、ArkTS语法、知识库、构建检查与computer-use相关Skill读取。原生注入的角色/系统指令另外保存在session_meta/turn_context中，不声称来自磁盘读取。`tools-used.json`按原生调用名统计，完整调用序列仍须读JSONL；`tool-input-urls.json`是候选URL索引，不代表每个链接都已读取/采用。

`code-snapshot/project/` 是最终提交工程的完整封存副本；manifest是文件集合与SHA的权威索引，六份混题初始化原文及三份Python字节码缓存的排除单独列明。原工程既有轨迹manifest的摘要标识历史原件；若账号字段脱敏，提交副本的新摘要以最终snapshot清单为准。

每次导出是有限时间快照，真实捕获时刻与最后原生记录时刻见清单。它不包含捕获后才产生的主/子会话记录、未来工具输出或最终答复；阶段3停止相关任务后可再次导出本题尾部记录，不能用新记录替换原解题过程。
