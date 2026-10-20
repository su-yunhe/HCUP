# vg-spec8 / 1-do 调度

- 请求：用户确认 0-analyze 完成，执行 spec-harness/1-do.md，完成本地实现与验证；不对外提交。
- 基线：HEAD 与 base/vg-spec8 均为 9cbcf7292c8cc46955dc3b522ddbda41c66a61d9；workflow/setup-result.json 证明 prepare_baseline 已通过。已有基线标识足够，无须切换 HEAD。
- 批准输入：spec/requirement.md、spec/metadata.json、spec/acceptance.md (69849e82f4402b87fd1a49cd53631b4a42154d24f3a9fbbc653c2786a98ef057)、spec/baseline-notes.md (e72636ed63581533a85d90a4040814a85b33eb3233cb694b2805344b73690556)。
- 隔离：本题目录；common 只读；本地技能、环境和通用技术文档。禁止其他题工程、题包、上游功能相关代码/修复历史。各角色不再派生子 Agent。
- 需求复审：/root/requirements_review，只写 workflow/requirements/implementation-review-01.md。
- 方案：/root/implementation_design，只写 workflow/design/implementation-plan-01.md。
- 独立验证：/root/independent_verification，拥有 hypium_tests/、logs/implementation-validation/、workflow/verification/implementation-*。初始仅准备，源码冻结且设备明确释放后构建、安装、运行。
- 编码：方案批准后派工，届时登记独占生产文件范围；验证期间停止生产修改。其他角色不得覆盖编码改动。
- U1-U6 选择：空/空白配置先显示 D1，继续后保留原校验；非按钮关闭如被支持则安全取消；自动同步不扩改、测试显式隔离；返回/重启作为回归；D2 保留；D1 单实例。选择不升级为 Spec 明文。
- 验收：A1-A19 对应实现及实测；所有 HTTP 方法持续零请求窗口；独立继续正控；构建/安装/冷启动/自测成功；基线 764 告警无新增；清理仅本轮生成噪声，保留所有既有内容。
- 完整派工文本、工具调用与返回以登记的原生会话 JSONL 为准；本文件是索引，不替代原始记录。
