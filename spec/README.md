# cml-spec28 单题资料

本题工程根为当前仓库根，分支为 `cml-spec28`，官方基线为 `9a1d608dc89acfc301657c33ce5dd6089cbf9572`。

- `requirement.md`：官方本题 Spec 原文，与 `../inputs/Spec.md` 一致。
- `metadata.json`：官方本题元数据，与 `../inputs/metadata.json` 一致。
- `submit-input.yaml`：题目级提交信息；未知字段保持空白。

本工程先在官方基线上执行原版基线准备脚本，再核对并接入团队已有的依赖准备提交
`b75aa21fdb29af1d3d00aa313360da85c6e05e4f`。该提交只涉及依赖配置和锁文件，
其中 `ibest-ui-v2` 的 `1.1.3` 配置与官方脚本结果一致；没有引入业务功能改动。
基线准备输出和接入前的配置差异均保留在 `../logs/`，完整说明见 `../workflow/baseline-provenance.json`。

准备结果与后续步骤见 `../workflow/state.json`；依赖安装和基线构建日志位于 `../logs/`。
本次仅准备工程，需求分析产物尚未生成。

在本目录的工程根打开独立会话后，先读取根 `AGENTS.md` 和 `workflow/state.json`，
登记新会话，再按 `harmony-task-flow` 的需求、方案、编码、自测流程推进。
本题采用 HCUP 的 worktree 布局，工程就是当前仓库根，不再建立 `project/` 子目录。

公共任务书与框架位于 `../../common/`，只读引用，不复制进业务源码，也不访问其他题工程。
