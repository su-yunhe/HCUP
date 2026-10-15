# spec/

本目录只放**本题专属**内容。通用四阶段任务书不在这里，统一放在：

```
/Users/bress/Documents/code/harmonycup-work/common/spec-harness/
├── 0-analyze.md     阶段 0：验收矩阵 + 基线理解（不改代码）
├── 1-do.md          阶段 1：功能开发 + 自测
├── 2-submit.md      阶段 2：单题提交材料
├── 3-package.md     阶段 3：阶段级打包（跨题，一次）
└── team.yaml        团队级信息（全队共用，填一次）
```

在本工程目录打开 Agent 会话，引用对应阶段的任务书即可，例如：

```
@/Users/bress/Documents/code/harmonycup-work/common/spec-harness/1-do.md 完成这个任务
```

## 本目录文件

| 文件 | 说明 |
| --- | --- |
| `requirement.md` | 本题 Spec 原文，复制自题包 |
| `metadata.json` | 本题 `base_commit` 与基线 bundle，复制自题包 |
| `submit-input.yaml` | 题目级信息，阶段 2 前由你填写 |
| `acceptance.md` | 验收矩阵，阶段 0 产出 |
| `baseline-notes.md` | 基线理解结论，阶段 0 产出 |
| `history/` | 早期实际使用过的任务书，作为过程记录保留（若存在） |
