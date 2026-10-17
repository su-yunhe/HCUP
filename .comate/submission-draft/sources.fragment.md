# sources 片段：jm-spec7

> 供 `3-package.md` 汇总进根 `sources.md`。留空项为 `【待补充】`。

## 随包基线声明

- 题目：`jm-spec7`
- 随包工程以官方基线 `b2e40f69dde450852d977c9555a9b12d59508c0d` 为起点（`spec/metadata.json` 的 `base_commit`，基线包标识 `repo_bundles/jingmo-for-harmonyos-b2e40f69dd-base.bundle`；提交说明 `Competition baseline snapshot; local signing removed`）。
- 基线工程自带的全部源码、资源、图片（含 `screenshot/`）、依赖清单及锁文件，来源均为官方基线本身，不是团队引入的外部素材。
- 基线工程的项目自述：京墨文库（鸿蒙版），版权人 贺丰宝，协议 MIT（工程根 `LICENSE`、`AppScope/app.json5` 的 `vendor`）。
  这些信息取自工程内文件，本阶段没有访问该项目的任何外部页面。
- 本题相对基线的改动清单见 `tasks/jm-spec7/changes/final.diff`：53 个文件，无二进制文件、无新增图片等资源。

## 依赖与工具

| 名称 | 版本 | 用途 | 获取方式 | 随包 |
| --- | --- | --- | --- | --- |
| tyme4oh | 1.3.9（`^1.3.9`） | 基线已有依赖 | ohpm，`https://ohpm.openharmony.cn/ohpm/`，由 `oh-package-lock.json5` 锁定 | 否（`oh_modules/` 不随包） |
| @ohos/hypium | 1.0.24（devDependencies） | 基线已有测试依赖 | 同上 | 否 |
| DevEco Studio | 6.1.0.860 | 构建、SDK、hdc | 华为官方，本机安装 | 否 |
| SWE-OpenHarmony test-harness 及其 Python 环境 | 版本未记录 `【待补充】` | 运行 `hypium_tests/` 自测 | 赛事题包，经用户同意只读使用（见 `trace-index.md`） | 否 |
| Comate（文心快码）Spec 智能体，模型 opus 5.5 | 客户端 1.108.2、扩展 4.13.4（导出时本机版本） | AI 辅助研发 | 本机已安装 | 否 |

## 额外来源

- 团队声明（`spec/submit-input.yaml` 的 `extra_sources`）：`【待补充】`，该字段为空，我不替团队填「无」。
- 从两个纳入的会话记录能核实的事实：两个会话的工具调用里没有联网检索（无 web fetch／web search）；
  没有从外部复制代码的记录；会话内唯一访问题包目录的是 `SWE-OpenHarmony/test-harness`（经用户在会话中同意，详见 `trace-index.md`）。
- 是否访问过本题来源项目中与本题相关的提交、PR、Issue、补丁及其副本：会话记录中没有这类访问；会话外的情况 `【待补充】`，由团队声明。
