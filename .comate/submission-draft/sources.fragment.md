# cml-spec17 来源片段

本片段供第3阶段汇总到成果包根 `sources.md`；当前仅整理本题，未修改团队根文件。

| 来源条目 | 已知事实与用途 | 证据位置（成果包内） |
| --- | --- | --- |
| cml-spec17 官方随包工程基线 | 官方 `metadata.base_commit` 为 `d6a6ba7480fbd0a30075462e46bb4344a430ba61`；`baseline_bundle` 元数据标识为 `repo_bundles/coolmallarkts-d6a6ba7480-base.bundle`。该标识来自本题副本，材料阶段没有读取题包 bundle 或来源项目修复历史 | `tasks/cml-spec17/project/spec/metadata.json`、`tasks/cml-spec17/trace-index.md` |
| 本题需求和原始输入 | 使用本工程 `spec/requirement.md` 与 `inputs/`；本题额外业务策略按批准的有界策略说明，不能升格为 Spec 明确保证 | `tasks/cml-spec17/project/spec/`、`tasks/cml-spec17/project/workflow/requirements/` |
| 材料规格与任务书 | 使用官方三份模板、本题/公共 spec-harness；实际版本与四任务书摘要见自动事实和索引 | `tasks/cml-spec17/trace-index.md`、`tasks/cml-spec17/evidence-facts.json`、`tasks/cml-spec17/project/spec-harness/` |
| 构建依赖、本地验证工具与 AI 配置 | 工程依赖由各模块清单/锁文件说明；本题 test-harness、Hypium测试及 system-config 快照的版本、调用与本题用途由原生轨迹关联。它们不自动证明所有额外来源已声明 | `tasks/cml-spec17/project/oh-package.json5`、`tasks/cml-spec17/project/oh-package-lock.json5`、`tasks/cml-spec17/project/test-harness/`、`tasks/cml-spec17/project/system-config/`、`tasks/cml-spec17/trace-index.md` |
| 新增/改变的二进制及基线同源资源 | 以单列的路径、字节数、SHA-256及基线同内容匹配为准；不以扩展名或补丁存在替代来源判断 | `tasks/cml-spec17/changes/binary-files.json` |
| 用户额外来源声明 `extra_sources` | 【待补充】。用户未提供，不能改写成“无额外来源”；如有复用、检索或来源保护例外，须提供实际来源、用途和对应记录 | 本题 `spec/submit-input.yaml` 空值；详见 `tasks/cml-spec17/missing-fields.md` |

材料阶段观察到的访问限制位于本题 `AGENTS.md`、任务书和配置快照；团队 `source_guard` 声明仍为【待补充】。这些限制的存在不代替用户对实际额外来源、人工操作及团队措施的确认。公开资料检索、工具读取与代码修改的真实事件以本题 Codex 原生 JSONL 为准，不从有限检索推导“全程无额外来源”。
