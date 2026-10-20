# cml-spec7 / 方案角色 / 分析产物复审

用户当前只选择 `spec-harness/0-analyze.md` 阶段。执行原生 harmony_design 角色，但本轮仅评审分析证据与需求可测性，不产出功能实现方案，不授权改业务代码。不创建子 Agent。你不是唯一在工作的 Agent，不撤销他人改动。

允许读取本题 `D:/HCUP/cml-spec7` 的 Spec、metadata、基线源码、当前分析产物；公共资源限 `D:/HCUP/common` 只读。禁止其他题目录、题包、上游当前实现和提交/PR/Issue/补丁/副本，禁止初始化总览会话。可写仅 `workflow/design/`，不写全局状态、生产代码、Spec 或测试；不操作设备。

已批准输入：Spec SHA256 `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9`，HEAD `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；当前业务代码冻结，全部 772 tracked 文件无差异。代码审计版本：`workflow/implementation/baseline-code-audit-01.md` SHA256 `9d4eef7089666400b4bde7a66e7989667d83e300978416fb18bb5b7bafc76600`。

先复审代码审计与 Spec、0-analyze 交付标准：入口链、底层能力和缺失项是否有可靠证据；第三方登录和协议详情等概述要求是否易遗漏；断点、120尺寸、按钮区域宽度等是否存在尚不能从 Spec 唯一确定的内容。需求草稿 `workflow/requirements/acceptance-draft.md` 正在由需求角色完成，主 Agent 将通知可评审版本；届时复审其每个场景步骤、证据等级、八维、边界、稳定选择器及网络状态机是否齐全。不要修改他人草稿。

产出 `workflow/design/analysis-review-01.md`，列出覆盖、可接受结论、需要更正的具体问题及证据。如果草稿尚未发布，先形成代码审计/可测性部分并告知主 Agent，收到需求草稿版本后补齐最终评审结论。不将“当前没实现”混为“需求不适用”；不自行缩减真实 Spec 要求。准确区分运行证据与静态事实；设备证据由独立验证角色提供。

本轮交付的验收标准：两个最终文档（acceptance、baseline-notes）能够支撑后续独立实施和 Hypium 验证，缺口与歧义透明，无业务代码修改。返回评审路径、阻断项/建议、实际原生 CODEX_THREAD_ID。
