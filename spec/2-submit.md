# 核心任务

在本工程中，整理本题的鸿蒙杯成果提交材料，产出到本工程 `.comate/submission-draft/`。

**前置**：`1-do.md` 已完成，构建与自测均通过。

**不要改动任何业务代码、资源和配置。** 本任务只做单题材料整理与校验。

团队级文件（`solution.md`、根 `sources.md`、根 `README.md`、`system-config/`）与成果包打包不在本阶段，
由 `3-package.md` 统一处理；本阶段只产出本题材料，以及供其汇总的片段文件。

材料规格以赛题包的官方模板为准，开工前必须先读（题包 `SWE-OpenHarmony/` 与 `harmonycup-work/` 同级，相对本工程为 `../../SWE-OpenHarmony/`）：
- `../../SWE-OpenHarmony/templates/submission-checklist.md`（材料清单）
- `../../SWE-OpenHarmony/templates/trace-index.md`（记录索引字段）
- `../../SWE-OpenHarmony/templates/submission.json`（任务清单模板）

**访问范围限制**：

| 范围 | 是否允许 |
| --- | --- |
| 本工程目录 | 允许 |
| `harmonycup-work/common/`（只读） | 允许 |
| 题包 `templates/` | 允许，只读 |
| 题包 `reports/build-baselines/<本题ID>.log` | 允许，只读 |
| 题包 `specs/`、`metadata/`、`repo_bundles/` 及其他目录 | **禁止**（本题需求与元数据已在本工程 `spec/`） |
| 其他赛题的工程目录 | **禁止** |
| 本题来源项目中与本题相关的提交、PR、Issue、补丁及其副本 | **禁止** |

# 输入

## 一、需要我提供的（留空的不要猜）

- 团队级信息：`../common/spec-harness/team.yaml`（相对本工程）
- 题目级信息：本工程 `spec/submit-input.yaml`

两个文件中留空的字段一律视为未提供，在产出中标 `【待补充】`，不要推测。

## 二、本次需要整理的会话（我每次填写后再交给你）

严格只整理下表所列会话，范围见要求 5。

| 引擎 sessionUuid | IDE 侧边栏会话 ID（可选） | 用途（可选，如 实现/测试设计/修复） |
| --- | --- | --- |
| aed0652d-3906-4632-8dd6-79c640ec113e |  |  |
| d114e8e5-c419-4b59-8a2d-2cdc504837fe |  |  |
|  |  |  |

表中 sessionUuid 全部为空时，不得自行检索会话补全，`traces/` 与会话相关字段全部标 `【待补充】`，并在交付说明中提醒我补填。

## 三、你自己去取的（不要问我）

| 信息 | 来源 |
| --- | --- |
| `base_commit` | 本工程 `spec/metadata.json` |
| 基线准备脚本记录 | 题包 `reports/build-baselines/<本题ID>.log` |
| 改动清单、`final.diff`、二进制大小与 SHA-256 | 本工程 git 状态 |
| bundleName、入口 Ability | `AppScope/app.json5`、entry 模块的 `src/main/module.json5` |
| 依赖与锁文件、构建命令、产物路径 | `oh-package.json5`、`oh-package-lock.json5`、`build-profile.json5` |
| 轨迹文件路径、会话元信息 | `~/.comate-engine/store/comate_chat_sessions.jsonl` 中**仅限**上文第二节所列 sessionUuid 的记录（只按 ID 取，不按工程路径或题目 ID 搜索） |
| Agent、模型 ID、effort、token 用量、生效规则 | 第二节所列会话的明细 `chat_session_<uuid>` 的 `payload.model` / `payload.agent` / `agentInfo` / `tokenUsage` / `appliedRuleNames` |
| 客户端与扩展版本 | `/Applications/Comate.app/Contents/Resources/app/product.json`、扩展 `package.json` |
| 任务书版本 | `common/spec-harness`：若为 git 仓库记 `git -C <common> rev-parse HEAD`，否则记四个任务书文件的 SHA-256 |
| 本题历史任务书 | 本工程 `spec/history/`（若存在） |
| Skill 与工具清单、失败重试过程 | 会话明细的工具调用序列 |
| 构建与自测日志 | 本工程 `logs/` |
| 成果冻结时间 | 开始整理时执行 `TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M'` 取当前北京时间，精确到分，本次整理只取一次；填入 `trace-index.md`，`3-package.md` 打包时会统一为成果包的冻结时间 |

# 输出

全部产出到本工程 `.comate/submission-draft/`，由 `3-package.md` 汇总进成果包。

| 文件 | 内容要求 |
| --- | --- |
| `changes/final.diff` | 自 `base_commit` 的完整差异，含新增、修改、删除；二进制用 `--binary` |
| `build.md` | 依赖安装、构建、安装、启动、应用标识、必要初始化；不得出现本机私有绝对路径 |
| `trace-index.md` | 按官方模板逐字段填写；客观字段据实填，其余留 `【待补充】` |
| `sources.fragment.md` | 本题的随包基线声明与额外来源，供汇总进根 `sources.md` |
| `solution.fragment.md` | 本题完成情况、未完成项、已知问题、AI 参与环节，供汇总进 `solution.md` |
| `submission.json.fragment` | 本题在任务清单中的 JSON 片段 |
| `traces/` | 第二节所列会话的原生明细 + 过滤后的索引行 + Markdown 副本 + 代码改动快照 |
| `logs/` | 从本工程 `logs/` 复制；缺失则明确告诉我需要补跑哪条命令 |

最后输出两份清单：**仍需我补充的字段**，以及**你已自动填入的事实及其出处**。

# 要求

这些是硬约束，违反任意一条都算任务失败。

1. **不得编造**。会话 ID、版本号、时间、分工、路径一律来自真实文件；无法核实的标 `【待补充】`，禁止用"示例值"占位。
2. **`final.diff` 必须完整且可应用**。范围是 `base_commit` 到提交版本的**全部**改动，
   包括 `spec/`、`hypium_tests/`、`.comate/` 等过程文件——它们会随工程一起放进成果包的 `project/`，
   diff 必须与 `project/` 一一对应，不能只截取业务代码目录。
   校验方式：把基线 clone 到临时目录、`checkout` 到 `base_commit`、`git apply --check --binary`，
   再比对关键文件与工程一致。校验结果写进交付说明。
3. **二进制资源单列**。diff 存不住内容，需另列文件路径、大小、SHA-256；若复制自基线自带资源，注明同源以免被当作外部素材。
4. **diff 不含构建噪声**。生成前确认 `git status` 只剩真实改动（`BuildProfile.ets` 等构建生成文件先还原）。
5. **轨迹只整理我指定的会话**。范围严格等于上文第二节我填写的会话表：
   - 禁止按工程路径、题目 ID、时间或其他条件自行检索、补充会话，即使认为某会话"相关"也不得纳入；
   - 表中的 ID 在 `comate_chat_sessions.jsonl` 或 `chat_session_<uuid>` 中找不到时，如实报告并标 `【待补充】`，不得用其他会话替代；
   - 若发现疑似遗漏的会话，只在交付说明中提示我，由我决定是否加入表中；
   - 禁止整盘打包 `~/.comate-engine/store/`，规则不允许提交整个客户端数据库和无关私人会话。
6. **会话 ID 要写两个**：引擎 `sessionUuid` 与 IDE 侧边栏会话 ID，并说明对应关系。
   `sessionUuid` 取自会话表；侧边栏 ID 优先取表中填写的值，未提供时只可从该会话自身记录中核实，仍无法核实则标 `【待补充】`。
7. **失败与重试必须保留**：会话表内会话的失败与重试过程要完整保留，不能只留成功记录。
8. **任务书版本要记录**：`trace-index.md` 中注明本题实际使用的 `common/spec-harness` 版本，
   以及 `spec/history/` 中的历史任务书（若存在）。
9. **路径规范**：`submission.json` 的三个路径字段填成果包内相对路径、用 `/` 分隔，后两项必须是文件路径。
10. **如实披露**。来源使用情况、人工修改、脱敏范围、记录缺失都按事实写；不确定的交给我判断，不要替我做有利解释。

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
