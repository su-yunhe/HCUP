# vg-spec13 来源片段

随包官方基线：`spec/metadata.json` 的 `88db8789e28333c7b7dcc8db078f394a262b73c3`，基线 bundle 标识 `repo_bundles/vignette-88db8789e2-base.bundle`。本题没有访问该来源项目的修复提交、PR、Issue或其副本；这是本次材料整理的访问事实，不替用户声明历史人工访问情况。

基线准备来源由工程 `workflow/baseline-provenance.json` 记录，bundle SHA-256 为 `50225027e85b86be317d42b8625c9f5ca7760e0b251b9915a4b1bd0eaaa5b9c5`；本阶段只读本题已保存的元数据和记录，未重新访问题包 bundle/specs/metadata。基线原有二进制资源的逐文件路径、大小、SHA-256及同源判断见 `changes/binary-files.json`；新增截图属于本题本地自测证据。

本题已记录的额外通用技术资料：[OpenHarmony 官方 @Builder 文档](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/ui/state-management/arkts-builder.md)。实际检索和修订依据见工程 `workflow/design/final-source-review-v1.md` 与设计主/子会话；原始Gitee读取405失败与随后GitHub原文读取均保留。这里只转录既有来源证据，不声称本次重新访问网页。自动提取的工具输入URL另见 `traces/tool-input-urls.json`，它是候选索引，不能把每个URL都当成实际采用来源。

公共测试工具来自只读 `common/test-harness` 的实际副本 `repro-support/test-harness/`，锁定 Hypium 6.1.0.210；应用开发依赖来源见 `build.md`、工程 `oh-package.json5` / `oh-package-lock.json5`。实际 Skill、角色和工作流配置保存于工程 `system-config/` 既有快照及原生会话指令，不在本阶段重建团队级配置。

用户 `extra_sources` 留空：【待补充】。需要用户披露全部额外来源/代码复用/人工检索及是否访问过受保护内容，不能自动写“无”。团队来源保护正式声明 `source_guard`：【待补充】；可核实的本题限制写在工程 `AGENTS.md`、本题任务书与原生会话指令中。
