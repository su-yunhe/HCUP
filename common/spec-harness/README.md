# spec-harness：通用任务书

适用于 `harmonycup-work/` 下全部赛题工程。每道题按四个阶段依次执行，每个阶段把对应文件发给 Agent：

| 阶段 | 任务书 | 在哪个工程目录运行 | 产出 |
| --- | --- | --- | --- |
| 0 分析 | `0-analyze.md` | 本题工程 | 工程内 `spec/acceptance.md`、`spec/baseline-notes.md` |
| 1 开发 | `1-do.md` | 本题工程 | 功能代码、`hypium_tests/`、`logs/` |
| 2 单题材料 | `2-submit.md` | 本题工程 | 工程内 `.comate/submission-draft/` |
| 3 阶段打包 | `3-package.md` | 任意（跨题汇总） | 成果包 ZIP |

阶段 0～2 每题一次，阶段 3 整个比赛阶段一次。

## 发给 Agent 的方式

在**本题工程目录**中打开会话，引用任务书文件即可，例如：

```
@/Users/bress/Documents/code/harmonycup-work/common/spec-harness/1-do.md 完成这个任务
```

任务书中所有"本工程 `spec/...`"都指会话所在工程的 `spec/` 目录。

## 每个工程 spec/ 目录的约定

任务书本身不复制到各工程。各工程 `spec/` 只放本题专属内容：

| 文件 | 由谁产生 | 说明 |
| --- | --- | --- |
| `requirement.md` | 准备阶段复制 | 本题 Spec 原文，复制自题包 `specs/<题目ID>.md` |
| `metadata.json` | 准备阶段复制 | 复制自题包 `metadata/<题目ID>.json` |
| `submit-input.yaml` | 你填写 | 题目级信息，模板见本目录 `submit-input.template.yaml` |
| `acceptance.md` | 阶段 0 产出 | 验收矩阵 |
| `baseline-notes.md` | 阶段 0 产出 | 基线理解结论 |
| `history/` | 归档 | 早期实际使用过的任务书，保留作过程记录 |
| `README.md` | 准备阶段 | 指向本目录的说明 |

团队级信息只填一次：本目录 `team.yaml`。

## 访问隔离

阶段 0～2 的 Agent 只允许访问：本题工程、`harmonycup-work/common/`（只读）、
以及 `2-submit.md` 中明确列出的题包 `templates/` 与本题基线构建日志。
**不得访问题包 `specs/`、`metadata/`、`repo_bundles/`，不得访问其他赛题工程。**
这是本目录与各工程分离存放的前提——本目录内**不得放入任何题目专属内容**（某题的分析、代码、会话信息等）。

## 版本记录

本目录内容变化会影响"实际使用的自定义提示"这一提交项。修改任务书后请记录版本，
各题 `trace-index.md` 需注明实际使用的版本（见 `2-submit.md` 第 8 条要求）。
