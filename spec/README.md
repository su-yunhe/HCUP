# vg-spec7 单题资料

本题工程根为当前仓库根，分支为 `vg-spec7`，官方基线为 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。

- `requirement.md`：官方本题 Spec 原文，与 `../inputs/Spec.md` 一致。
- `metadata.json`：官方本题元数据，与 `../inputs/metadata.json` 一致。
- `submit-input.yaml`：题目级提交信息；未知字段保持空白。

准备结果与后续步骤见 `../workflow/state.json`，基线来源及校验见 `../workflow/baseline-provenance.json`。
准备、依赖安装和基线构建日志位于 `../logs/`。本次仅准备工程，需求分析产物尚未生成。

在本目录的工程根打开独立会话后，先读取根 `AGENTS.md` 和 `workflow/state.json`，
登记新会话，再按 `harmony-task-flow` 的需求、方案、编码、自测流程推进。
本题采用 HCUP 的 worktree 布局，工程就是当前仓库根，不再建立 `project/` 子目录。

公共任务书与框架位于 `../../common/`，只读引用，不复制进业务源码，也不访问其他题工程。
