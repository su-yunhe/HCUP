# 核心任务

在本工程中，整理本题的鸿蒙杯成果提交材料，产出到 `.comate/submission-draft/`。

**前置**：`spec/1-do.md` 已完成，构建与自测均通过。

**不要改动任何业务代码、资源和配置。** 本任务只做材料整理与校验。

团队级文件（`solution.md`、`sources.md`、根 `README.md`）与成果包打包不在本阶段，
由 `spec/3-package.md` 统一处理；本阶段只产出本题材料。

材料规格以赛题包的官方模板为准，开工前必须先读：
- `/Users/bress/Documents/code/SWE-OpenHarmony/templates/submission-checklist.md`（材料清单）
- `/Users/bress/Documents/code/SWE-OpenHarmony/templates/trace-index.md`（记录索引字段）
- `/Users/bress/Documents/code/SWE-OpenHarmony/templates/submission.json`（任务清单模板）

**访问范围限制**：本阶段只允许读题包的 `templates/` 目录和本题的
`metadata/<题目ID>.json`、`reports/build-baselines/<题目ID>.log`。
禁止访问 `specs/`（其他题需求）、`repo_bundles/`（其他题基线）和其他赛题的工程目录；
同样禁止访问本题来源项目中与本题相关的提交、PR、Issue、补丁及其副本。

# 输入

## 一、需要我提供的（我填完再给你，留空的不要猜）

```yaml
# 团队级（整个阶段一次）
team_id: "HC2026-111"
team_name: "Ghost_London"
stage: "online"
version: ""
contact: ""
freeze_time: ""          # 成果冻结时间，北京时间，精确到分
members:
  - name: ""
    work: ""             # 需求分析 / 方案设计 / AI指导 / 代码编写 / 调试 / 材料整理
source_guard: ""         # 实际采取的来源保护措施；未配置就写"未配置"

# 题目级（每题一次）
task_id: ""
human_edits: ""          # "无人工直接修改代码" 或逐条：谁/为什么/哪些文件/前后标识/证据路径
known_issues: ""         # 未完成项与已知问题
extra_sources: ""        # 额外来源；无则"无"。访问过来源项目相关提交的必须写明
md_export_dir: ""        # 侧边栏「导出本地」生成的会话 Markdown 所在目录；没导就留空
```

## 二、你自己去取的（不要问我）

| 信息 | 来源 |
| --- | --- |
| `base_commit` | `SWE-OpenHarmony/metadata/<题目ID>.json` |
| 基线准备脚本记录 | `SWE-OpenHarmony/reports/build-baselines/<题目ID>.log` |
| 改动清单、`final.diff`、二进制大小与 SHA-256 | 本工程 git 状态 |
| bundleName、入口 Ability | `AppScope/app.json5`、`products/*/src/main/module.json5` |
| 依赖与锁文件、构建命令、产物路径 | `oh-package.json5`、`build-profile.json5` |
| 会话 ID、轨迹文件路径 | `~/.comate-engine/store/comate_chat_sessions.jsonl`（按工程绝对路径与题目 ID 反查） |
| Agent、模型 ID、effort、token 用量、生效规则 | 会话明细 `chat_session_<uuid>` 的 `payload.model` / `payload.agent` / `agentInfo` / `tokenUsage` / `appliedRuleNames` |
| 客户端与扩展版本 | `/Applications/Comate.app/Contents/Resources/app/product.json`、扩展 `package.json` |
| Skill 与工具清单、失败重试过程 | 会话明细的工具调用序列 |

# 输出

全部产出到 `.comate/submission-draft/`，打包时再按目标结构搬运。

| 文件 | 内容要求 |
| --- | --- |
| `changes/final.diff` | 自 `base_commit` 的完整差异，含新增、修改、删除；二进制用 `--binary` |
| `build.md` | 依赖安装、构建、安装、启动、应用标识、必要初始化；不得出现本机私有绝对路径 |
| `trace-index.md` | 按官方模板逐字段填写；客观字段据实填，其余留 `【待补充】` |
| `sources.md` | 随包基线声明 + 额外来源；无额外来源也要显式声明 |
| `solution.md` | 完成情况、人机协作方式、成员分工、来源保护措施、配置与变更 |
| `submission.json.fragment` | 本题在任务清单中的 JSON 片段 |
| `traces/<题目ID>/` | 本题会话原生明细 + 过滤后的索引行 + Markdown 副本 + 代码改动快照 |
| `system-config/` | 实际使用的系统提示、Skill 定义、工具与编排配置 |
| `logs/` | 构建与自测日志；缺失则明确告诉我需要补跑哪条命令 |

最后输出两份清单：**仍需我补充的字段**，以及**你已自动填入的事实及其出处**。

# 要求

这些是硬约束，违反任意一条都算任务失败。

1. **不得编造**。会话 ID、版本号、时间、分工、路径一律来自真实文件；无法核实的标 `【待补充】`，禁止用"示例值"占位。
2. **`final.diff` 必须可应用**。校验方式：把基线 clone 到临时目录、`checkout` 到 `base_commit`、
   `git apply --check --binary`，再比对关键文件与工程一致。校验结果写进交付说明。
3. **二进制资源单列**。diff 存不住内容，需另列文件路径、大小、SHA-256；若复制自基线自带资源，注明同源以免被当作外部素材。
4. **diff 不含构建噪声**。生成前确认 `git status` 只剩真实改动（`BuildProfile.ets` 等构建生成文件先还原）。
5. **轨迹只摘本题**。按工程路径和题目 ID 两个维度各查一遍（测试设计类会话的工作区可能是赛题包目录，容易漏）；
   禁止整盘打包 `~/.comate-engine/store/`，规则不允许提交整个客户端数据库和无关私人会话。
6. **会话 ID 要写两个**：引擎 `sessionUuid` 与 IDE 侧边栏会话 ID，并说明对应关系。
7. **失败与重试必须保留**，不能只留成功记录。
8. **路径规范**：`submission.json` 的三个路径字段填成果包内相对路径、用 `/` 分隔，后两项必须是文件路径。
9. **如实披露**。来源使用情况、人工修改、脱敏范围、记录缺失都按事实写；不确定的交给我判断，不要替我做有利解释。

# 背景

本工程对应 2026 AI 辅助研发创新大赛（鸿蒙杯）的一道赛题，题包仓库 `gitcode.com/SMAT/SWE-OpenHarmony`。

评分单位是 F-point（可判定的 Hypium 测试方法），线上评测分 = 通过的 F-point ÷ 该阶段总数 × 100。
未提交、构建失败、崩溃的 F-point 都不计通过但计入分母。

材料本身也会被核验，且核验的是实质而非文件是否存在：

- 官方会逐题核验是否有 AI 实际参与研发，检查原始记录是否对应**本题**的具体研发过程。
- 无法证明某题实际使用 AI 的，该题全部 F-point 不计通过。
- **截止后禁止补交**代码、漏交材料，也不能用新产生的记录替代原始解题证据。
- 涉嫌伪造或故意隐瞒按章程第 11.1、11.4 条处理，后果重于单题归零。
- 来源保护：不得访问来源项目中与本题相关的修复提交、合并请求、Issue、补丁及其副本；
  轨迹显示访问受保护内容的，该题 F-point 不计通过（章程第 5.7、5.8 条）。

所以材料整理的目标不是"把目录填满"，而是**让核验者能顺着索引复现本题的真实研发过程**。
本地 `tools/check_submission.py` 只验 ZIP 结构和路径存在性，通过不代表材料合格。

