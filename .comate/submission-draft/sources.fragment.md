# sources 片段：sym-combo-customize

（供 `3-package.md` 汇总进根 `sources.md`；同一来源与其他题合并为一条并标注涉及题目。）

## 随包基线声明

- 本题工程以官方题包基线为起点，不是外部素材：`base_commit` `21588d3f75b366c0d8de37b59b5634846ce5f347`（提交说明 “Harmony Cup sanitized baseline snapshot”），基线包 `repo_bundles/symbolu_next-21588d3f75-base.bundle`（出处：`spec/metadata.json`）。工程中 `LICENSE` 为 MIT，版权方 awa Liny。
- 基线自带的全部资源（图标、字体样本 `python_script/HMSymbolVF.ttf`、符号数据 `linysSymbol.ets` 等）均属基线原有内容。**本题 `final.diff` 不含任何新增或修改的二进制资源**，因此没有“复制自基线资源”的二进制需要单列。
- 基线→HEAD 的差异仅 `oh-package-lock.json5`，由基线准备脚本 `ohpm install` 产生（`logs/baseline-prepare.log`）。

## 第三方依赖（来自 `oh-package.json5` / `oh-package-lock.json5`）

| 名称 | 版本 | 获取方式 | 用途 |
| --- | --- | --- | --- |
| `@ohos/hypium` | 1.0.21 | ohpm（`ohpm.openharmony.cn`），devDependency，基线已声明 | 基线自带的测试依赖 |
| `@ohos/hamock` | 1.0.0 | ohpm，devDependency，基线已声明 | 基线自带的测试依赖 |
| HarmonyOS SDK 系统组件 `SegmentButton`、`SymbolGlyph`（`@kit.ArkUI`） | 随 SDK 6.1.0.105（API 23） | DevEco Studio 内置 SDK | 渲染策略分段按钮、符号渲染 |

自测工具（不属于工程运行时）：`hypium==6.1.0.210`（pip，经 `common/test-harness/requirements.txt`），`harmonycup-work/common/test-harness/` 为团队自研自测框架，将由 3-package 放入 `system-config/test-harness/`。

## 额外来源

- 题目级 `extra_sources` 字段：【待补充】（`spec/submit-input.yaml` 不存在，字段未提供，不做推测）。
- 据会话记录（仅限会话表所列两个会话）的核查，仅发现对赛事官网 `swe-openharmony.tech` 的访问（`web_fetch` 3 次、`curl` 1 次，查阅技术答疑与评分规则，非来源项目）；未发现访问来源项目 `symbolu_next` 的提交、PR、Issue、补丁或副本的记录，也未发现从外部复制代码的记录。该结论只覆盖这两个会话，是否访问过受保护内容以人工审查为准。
