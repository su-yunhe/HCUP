# 核心任务

把本阶段全部题目的材料汇总成一个可提交的成果包 ZIP，并完成本地校验。

**本任务不改任何业务代码，也不补做题目。** 只做汇总、校验、打包。

前置：每道已完成的题都应已通过 `spec/2-submit.md` 产出单题材料。
未做或未完成的题不需要材料，但**必须在清单里保留条目**。

# 禁止事项

1. **不得伪造或补造记录**。截止后禁止补交代码和漏交材料，也不能用新产生的记录替代原始解题证据；
   涉嫌伪造或故意隐瞒按章程第 11.1、11.4 条处理，后果重于单题归零。
2. **不得整盘打包客户端数据**。只摘取与本阶段题目相关的会话，不提交整个 `~/.comate-engine/store/`、
   无关私人会话、账号密钥、签名私钥。
3. **不得在材料中出现本机私有绝对路径**作为构建依赖；成果包内路径一律相对、用 `/` 分隔。
4. **不得遮蔽代码来源与修改依据**。可以脱敏，但要说明范围。

# 输入

## 需要我提供的（留空的不要猜）

```yaml
team_id: ""
team_name: ""
stage: "online"
version: ""
contact: ""
freeze_time: ""          # 成果冻结时间，北京时间，精确到分
members:
  - name: ""
    work: ""             # 需求分析 / 方案设计 / AI指导 / 代码编写 / 调试 / 材料整理
source_guard: ""         # 实际采取的来源保护措施；未配置就写"未配置"
submitted_tasks: []      # 本次标记 submitted 的题目ID
attempted_not_submitted: []   # 已尝试但不提交工程的题目ID（仍须提供记录索引）
zip_out: ""              # 成果包输出路径
```

## 你自己去取的

| 信息 | 来源 |
| --- | --- |
| 本阶段全部题目 ID | 题包 `templates/submission.json`（25 题，顺序与条目都要保留） |
| 各题 `base_commit` | 题包 `metadata/<题目ID>.json` |
| 各题单题材料 | 各工程 `.comate/submission-draft/` |
| 各题会话记录 | `~/.comate-engine/store/`，按工程绝对路径与题目 ID 反查 |
| Agent／模型／客户端版本 | 会话明细 `payload.model`、`payload.agent`；应用包 `product.json` 与扩展 `package.json` |
| 系统提示与 Skill 定义 | `~/.comate/skills/`、`~/.agents/skills/`，以及各题 `spec/` 下的任务书 |

# 输出：成果包结构

```
<包根>/
├── submission.json          # 本阶段全部题目；未做的留 not_completed
├── README.md                # 公共环境说明（SDK、DevEco、工具版本、通用构建方式）
├── solution.md              # 团队级：完成情况、人机协作、成员分工、来源保护、配置与变更
├── sources.md               # 团队级：第三方来源；无额外来源也要显式声明
├── traces/<题目ID>/         # 各题会话原生明细 + 过滤后索引行 + Markdown 副本 + 代码改动快照
├── system-config/           # 实际使用的系统提示、Skill 定义、工具与编排配置
└── tasks/<题目ID>/
    ├── project/             # 完整工程（排除 build/、oh_modules/、.hvigor/ 等产物）
    ├── build.md
    ├── trace-index.md
    ├── human-changes.md     # 有人工改码时才需要
    ├── changes/final.diff
    └── logs/                # 构建与自测日志
```

`submission.json` 中每个 submitted 条目：

```json
{ "task_id": "<题目ID>", "status": "submitted",
  "project_path": "tasks/<题目ID>/project",
  "build_instructions": "tasks/<题目ID>/build.md",
  "trace_index": "tasks/<题目ID>/trace-index.md" }
```

# 执行顺序

1. **冻结**。停止本次提交涉及的全部 AI 任务和人工修改，记录冻结时间；各题打版本标识
   （`git tag submit-<题目ID>-v<版本>` 或记录工作树快照摘要）。
2. **核对题目清单**。以题包 `templates/submission.json` 为准，确认 25 个条目齐全、无重复、无多余；
   `submitted` 与 `not_completed` 与实际一致。
3. **汇总单题材料**。把各题 `.comate/submission-draft/` 下的产物搬到 `tasks/<题目ID>/`；
   缺 `final.diff`、`build.md`、`trace-index.md` 或 `logs/` 的，列出来告诉我，不要用空文件凑数。
4. **拷贝工程**到 `tasks/<题目ID>/project/`，排除构建产物与依赖目录，保留源码、资源、配置、
   依赖清单和锁文件。
5. **摘取轨迹**到 `traces/<题目ID>/`：按工程路径和题目 ID 两个维度各查一遍会话
   （测试设计类会话的工作区可能是题包目录，容易漏），含失败与重试记录。
6. **复制配置**到 `system-config/`：各题 `spec/` 任务书、使用到的 Skill 定义、Agent 与模型版本说明。
   即使无自定义项也要写配置说明文件。
7. **写团队级文档**：`README.md`、`solution.md`、`sources.md`。
   `solution.md` 需包含"已尝试但未提交工程的任务"一节，列出题目 ID 与记录索引路径。
8. **逐题校验差异可用性**：把 `final.diff` 应用到该题基线的干净 clone 上
   （`git clone` → `checkout base_commit` → `git apply --check --binary`），确认与 `project/` 一致。
   任一题校验失败就停下报告，不要打包。
9. **打包并校验**：

   ```bash
   cd <包根的父目录> && zip -r "<zip_out>" <包根目录名> -x '*/build/*' '*/oh_modules/*' '*/.hvigor/*'
   cd /Users/bress/Documents/code/SWE-OpenHarmony
   .venv/bin/python tools/check_submission.py "<zip_out>"
   .venv/bin/python tools/submission_checksum.py "<zip_out>"
   ```

10. **输出提交邮件要素**：阶段、团队 ID、版本号、联系人、文件名、大小、SHA-256，
    以及下载链接与提取码的占位（链接由我填）。

# 要求

1. **不得编造**。团队信息、冻结时间、分工只能用我提供的值；其余一律来自真实文件。
   无法核实的标 `【待补充】`并在最后汇总，禁止用示例值占位。
2. **清单必须全量**。25 个条目一个不少，`not_completed` 也要保留；路径字段必须指向包内真实文件，
   后两项必须是文件路径而非说明文字。
3. **每个 submitted 题目**都要有完整工程、`build.md`、`trace-index.md`、`final.diff`；
   不能只交 HAP 或补丁。
4. **`traces/` 与 `system-config/` 必须非空**，这是 `check_submission.py` 的硬性检查项。
5. **二进制资源单列**摘要（路径、大小、SHA-256），复制自基线自带资源的注明同源。
6. **如实披露**来源使用、人工修改、脱敏范围、记录缺失；不确定的交给我判断，不要替我做有利解释。
7. **最后输出三份清单**：仍需我补充的字段、各题材料完整性检查结果、差异可应用性校验结果。

# 背景

本阶段共 25 道赛题。评测分 = 通过的 F-point ÷ 本阶段全部 F-point × 100，
未提交、构建失败、崩溃的检查点都不计通过但计入分母——所以清单里每道题的状态都影响最终分数。

材料本身也会被核验，且核验实质而非文件是否存在：

- 官方逐题核验是否有 AI 实际参与研发，检查原始记录是否对应**本题**的具体研发过程。
- 无法证明某题实际使用 AI 的，该题全部 F-point 不计通过。
- 轨迹显示访问受保护内容的，该题 F-point 不计通过（章程第 5.7、5.8 条）。
- 个别记录缺失但包内其他证据足以核验的，按实际测试结果正常计分，不直接认定作弊。

提交后仍可继续作答，但更新正式成果须重新冻结并生成完整成果包、重新发送正式提交邮件；
不得直接替换已上传包内的文件。未收到新邮件时以最后一次正式提交为准。

本地 `check_submission.py` 只验 ZIP 结构和路径存在性，通过不代表材料合格、源码可构建或功能通过。

