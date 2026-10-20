# cml-spec7 / 需求角色 / 第 1 轮

范围：本轮仅执行用户选择的 `spec-harness/0-analyze.md` 分析任务，不设计或实现业务功能。允许读取本题 `D:/HCUP/cml-spec7` 的 Spec、metadata、inputs 和基线源码；公共资源仅 `D:/HCUP/common` 只读。禁止其他题目录、题包、上游当前实现和修复历史；不得读取初始化总览会话。不得派生子 Agent。

输入版本：HEAD `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；Spec SHA256 `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9`；metadata SHA256 `cf5f402ae5042331bf332c4173a3b26ddb3c2494cee9976bd2b39106ca0e5a88`。当前无 tracked 源码差异，开始前自行核实。

执行原生 harmony_requirements 角色。可写范围仅 `workflow/requirements/`，不写全局状态、生产代码、测试或 spec 最终文档。你不是唯一在工作的 Agent，不撤销他人改动。主 Agent 最后将批准草稿复制到 `spec/acceptance.md`。

产出 `workflow/requirements/acceptance-draft.md`：严格按 0-analyze 的字段拆分三个场景及概述中的全部原子要求，带 Spec 行号、逐字文案、证据等级、八维信息、可观察的 Hypium 断言和稳定 id（现存或建议补充须区分）。完整覆盖列出的边界，不适用也解释。网络流程按 Spec 与基线事实分别表述，画状态机，不能把基线实现当成明文要求。所有待确认假设单独汇总并给建议，不自行将推导升级为要求。引用基线文件路径和行号。可以记录推荐选择器而不修改代码。

返回草稿路径、覆盖统计、真实歧义、建议后续；说明哪些只静态核对、哪些需要设备验证。提供实际子会话 UUID（如可获得）。
