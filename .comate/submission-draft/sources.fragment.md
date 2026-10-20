# vg-spec15 来源片段

随包基线：本地 `spec/metadata.json` 的 `base_commit=88db8789e28333c7b7dcc8db078f394a262b73c3`、`baseline_bundle=repo_bundles/vignette-88db8789e2-base.bundle`。工程 provenance 保存 bundle 为 2792680 字节、SHA-256 `50225027e85b86be317d42b8625c9f5ca7760e0b251b9915a4b1bd0eaaa5b9c5`；本阶段没有读取禁止范围内的 bundle 或上游记录。来源项目标识沿用随包基线，不作为允许访问其相关修复的授权。

生产资源目录没有相对基线新增或修改的二进制素材；现有图标、图片等来自同一随包基线。全部二进制路径、大小、SHA-256、基线同源状态见 `changes/binaries.json`。新增截图、测试夹具等为过程材料，不能混称外部生产素材。

可查的研发资料：

- 工程基线 `entry/src/main/ets/pages/ImportPage.ets` 的既有 LoadingProgress 用法，属于同源基线代码。
- 本地官方 SDK `loading_progress.d.ts` 与 `common.d.ts`，用于组件/API 声明核对。
- arkts-syntax-assistant 的 `references/en/typescript-to-arkts-migration-guide.md`。
- hmos-arkts-knowledge-retriever 的 `docs/ArkTS-Language-Guide/Basic-Syntax/{enumerations.md,concurrency.md}`。
- 本题保存的 harmony-task-flow、角色配置和测试框架，原文件位置见工程 `system-config/`、`test-harness/` 及原生调用。

检索证据：工程 `workflow/design/implementation-plan-01.md`；设计会话 `01a1400b-7abd-7632-a99a-998d077941be` 的原生行 88/91、121/124，编码会话 `01a14010-17ed-7062-a72a-a953c7f3e03d` 的行 51/54、58/61；`logs/implementation-build/tool-diagnostics-01.log` 保存检索索引缺失及回退。完整原生记录放在包根 `traces/vg-spec15/native/`。这些指南是本地参考来源，不推定为外网检索或代码直接复制。

依赖来源以工程两级锁文件的 resolved/integrity 为准；OHPM 安装日志保存官方 OHPM 的依赖获取。Python Hypium 与 cryptography 是自测工具依赖，见 build.md；第三方许可证与获取方式由 3-package 汇总进团队配置说明。

用户 `extra_sources` 留空，额外来源完整披露仍为【待补充】。现有方案称未查询外网、已查研发会话工具调用未发现联网检索候选；这只是记录观察，不能替用户保证从未使用其他来源或未访问受保护内容。
