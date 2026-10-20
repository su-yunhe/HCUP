# 本题轨迹读取与范围说明

native/保存本次只摘本题的16个原生文件分段，全部有独立SHA-256；同一主会话的后缀分段同样保留。用Python逐行json.loads读取，tool-call-index.jsonl提供原生文件行号。markdown/是每个JSONL逐行的完整格式化JSON转换副本，保留提示、工具调用、结果、失败及原生事件，不是IDE“导出本地”。未提供md_export_dir的事实仍保留【待补充】。

session_index.filtered.jsonl仅含选中本题ID的真实索引行，能证明三条主会话的侧边栏映射；其余子会话没有侧边栏索引行，保留原生线程ID并将独立侧边栏映射标【待补充】。子记录token_usage_record.session_id有继承父ID的情况，不当作独立引擎UUID。Comate数据库未找到，原生格式没有sessionUuid、payload.agent、appliedRuleNames等Comate字段；按实际格式取证，不伪造同名字段。

模型/effort来自turn_context，token值是各分段最后一个原生token_count.total_token_usage。它是原始运行统计，不跨分段求和作为账单，不把缺少字段视为0。导出时间与最后事件时间逐文件记录；活跃材料会话只含截至导出时的事件，最终3-package冻结还须再次导出。

发现方法：先按原生首行cwd匹配工程路径，再按轻量侧边栏索引题号和获准本题原生文件正文题号核对。非本题工作区候选不复制。必须排除的初始化总览UUID=01a13fc4-2611-7761-a580-1283e0c70541，旧混合快照目录同样不进完整工程。

范围失误如实披露：本阶段最初的题号rg曾扫描整个原生store正文，仅输出命中文件名；后来改成先metadata/轻量索引筛选，再在本题文件正文查询。编码审计曾读取git可见文件前8000字节做二进制判断，未先排除初始化混合快照。均未解析/输出该混合原文作为实现参考、未复制其原生会话到草稿；当前正确采集器已修正。首次Git本地clone默认优化曾复制共享对象库存储，已中断该轮，改用--no-local限定本题分支；未查询这些额外对象作为实现或上游历史参考，旧临时clone不进入交付，清理及重试记录见validation/material-retry-history.json。本阶段审计记录不能替代原解题证据。

code-snapshot/project/是后续3-package的唯一工程复制源；manifest.json列全部文件、摘要和排除项。业务与本题过程文件均保留，排除.git/构建依赖缓存/模拟器磁盘缓存/混合初始化记录/submission-draft自身。排除submission-draft避免补丁自包含递归；staging之外的.comate不排除。失败、截图、重试、失败候选与历史原生快照保留。此解释已公开，不宣称官方逐字豁免staging。

原生副本未脱敏；路径、内部账号ID与工具结果保留。未复制整个客户端DB、凭证文件或签名私钥。打包前核查不能遮蔽来源与修改依据；如需脱敏，说明具体字段和方法，并相应重新校验快照/补丁，不能悄悄改动已核对副本。
