# cml-spec7 / 编码角色 / 分析阶段只读核查

用户当前范围是 `spec-harness/0-analyze.md`，只产出分析文档，**禁止修改业务代码**。本派工覆盖编码角色的基线核查责任，不授权实施或修复。采用原生 harmony_implementation 角色，不生成子 Agent。其他 Agent 正在本题工作，不撤销他人改动。

仅读取本题 `D:/HCUP/cml-spec7` 的 Spec、metadata、基线源码及本题记录；允许 `D:/HCUP/common` 只读公共资源。禁止其他题目录、题包、上游提交/PR/Issue/补丁/已实现版本及其副本，禁止读取初始化总览会话。不要操作共享模拟器；独立自测 Agent 正在构建和设备验证。

输入版本：HEAD `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；Spec SHA256 `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9`；`workflow/analysis-start-fingerprint.json` 记录当前完整 tracked 文件哈希，开始时无 tracked 差异。

可写仅 `workflow/implementation/`；不要写生产代码、Spec、测试或全局 state/events。产出 `workflow/implementation/baseline-code-audit-01.md`，给最终 `spec/baseline-notes.md` 提供可核查的代码事实：

1. 现有进入我的→登录主页面的页面、路由注册、所有跳转调用点，精确文件:行号。
2. 登录主页面、短信、密码、微信/QQ/支付宝、协议/隐私链接的当前实现、状态/数据模型、服务调用和本地持久化。
3. 响应式布局、可复用控件、登录流程、路由管理与 loading 的相近实现。
4. 相比 Spec 缺失的能力、稳定 id 的缺失、同名文本歧义、服务/账号/设备前提。
5. 严格区分代码实证、推断、尚待设备验证；代码读取不冒充实际入口操作证据。

不要泛读无关模块；不对 Spec 歧义自行作最终决定。不设计新功能方案，只建立现状证据。引用相对路径加行号即可，最终交付由主 Agent 转换为可点击绝对路径。返回报告、结论、指纹、原生会话 UUID（如可得）。
