# 鸿蒙杯提交材料整理流程（可复用）

> 本文件与具体题目无关，建议移到 `harmonycup-work/` 上级目录或赛题包 `docs/` 下长期维护。
> 本题（jm-spec35）的实际产物见同目录 `build.md`、`trace-index.md`、`sources.md`、`changes/final.diff`，可作为样板。

## 0. 结论先行：两类材料

| 类别 | 内容 | 谁来做 |
| --- | --- | --- |
| A. 可由 AI 全自动产出 | `final.diff`、二进制资源摘要表、`build.md`、`submission.json` 条目、`trace-index.md` 的客观字段、**轨迹文件摘取**、**Agent／模型／客户端版本** | AI，不需要你提供信息 |
| B. 只有你能提供 | 团队信息（team_id／name／version／contact）、成果冻结时间、成员分工、人工修改说明、来源保护措施的实际配置 | 你，AI 代填就是编造 |

判定标准很简单：**能从本机文件里读出来的，都归 A**。
Agent 名称、模型 ID、effort、客户端与扩展版本都记录在会话明细和应用包里（见 1.1 与 3.3），不需要你口述。
B 里剩下的是本机不存在的事实——团队身份、时间决策、人的分工，这些 AI 没有任何依据，编了就是伪造。

`traces/` 是硬性检查项（`check_submission.py` 会校验 `traces/` 与 `system-config/` 下存在非空文件），
而官方核验"检查原始记录是否对应本题及具体研发过程，不只检查文件是否存在"。
这一项曾被当作前置闸门，现已确认原生记录完整落盘、可按题摘取（见第 1 节），不再构成阻塞。

---

## 1. 轨迹记录：两条可用路径（每个阶段确认一次，之后按题摘取）

Comate 同时提供原生落盘记录和界面导出，**两者都要交，作用不同**。

### 1.1 原生记录（规则优先接受的形式）

清单原文："工具支持导出会话数据库时，提交相关数据库记录；否则提交 JSON、JSONL 等原生记录"。
Comate 的原生记录在：

```
~/.comate-engine/store/
├── comate_chat_sessions.jsonl              # 会话索引（append-only，同一会话会有多条历史行）
├── chat_session_<sessionUuid>               # 单会话完整明细 JSON（含全部工具调用与返回）
├── blobs/                                   # 大体积工具返回的外存对象
├── terminals/                               # 终端会话记录
└── <工程名>-<哈希>/、comate_<工程名>-<哈希>/   # 按工作区分目录（tabs.json、recentSkills.json 等）
```

按题目定位会话（工作区目录即工程绝对路径）：

```bash
python3 -c "
import json
rows=[json.loads(l) for l in open('$HOME/.comate-engine/store/comate_chat_sessions.jsonl',encoding='utf-8') if l.strip()]
seen={}
for r in rows:
    if '<题目ID>' in str(r.get('workspaceDirectory','')): seen[r['sessionUuid']]=r
for u,r in seen.items(): print(u, r['source'], r['title'])
"
```

jm-spec35 实测结果：

| sessionUuid | source | 内容 |
| --- | --- | --- |
| `bcf69c06-bb3d-4ef8-863d-2689e210d704` | SpecConversation | 主开发会话「@do.md 完成这个任务」，660 KB，192 次工具调用 |
| `d8a98d05-92ae-48b8-8374-3b3b48689189` | AgentConversation | 同工程内的小会话 |
| `0df7f046-d22e-4ecf-95f0-b3b28ac36f24` | SpecConversation | 测试设计会话（工作区为赛题包，不在工程目录下，容易漏） |

明细文件结构已核对：顶层含 `sessionUuid`、`messages`、`title`、`ctime`/`utime`、`workspaceDirectory`、`workspaceId`、`summary` 等；
`messages` 内每次工具调用都有 `toolName`、`params`、`result`。本题 192 处工具调用、含 5 次 WebFetch 记录均在其中。

**Agent 与模型信息也在这个文件里**，不需要人工回忆。每条 user 消息的 `payload` 含：

```jsonc
"model": { "displayName": "opus 5.5", "modelId": "Opus 5.5_143_69ecd21d...",
           "requestType": "COMATE_MULTIPLE_MODE", "mode": "NORMAL", "effort": "xhigh" },
"agent": { "agentId": 12, "agentName": "Spec", "agentImage": "spec" }
```

assistant 消息还带 `agentInfo`、`tokenUsage`（`contextUsed` / `contextLimit`）、`appliedRuleNames`（生效的规则）。
客户端与扩展版本从应用包读：

```bash
python3 -c "import json;d=json.load(open('/Applications/Comate.app/Contents/Resources/app/product.json'));print(d['nameLong'],d['version'],d['commit'],d['date'])"
python3 -c "import json;d=json.load(open('/Applications/Comate.app/Contents/Resources/app/extensions/baiducomate.comate/package.json'));print(d['name'],d['version'])"
```

注意：**IDE 侧边栏的会话 ID 与引擎 sessionUuid 不是同一个**。
侧边栏 ID（如 `1791947576719-htj3oc4ev8g`）只存在于
`~/Library/Application Support/Comate/User/workspaceStorage/<哈希>/state.vscdb`，
对应的代码改动快照在同目录 `comateAgentEditor/diffInfo/<侧边栏ID>-changes.json`。
`trace-index.md` 建议两个 ID 都写，并说明对应关系。

### 1.2 界面导出（人类可读副本）

侧边栏右上角导出按钮 → 「导出本地」，选目录后生成 `<会话标题>.md`（默认落 `~/Desktop`）。
格式（已核对实现）：`# 标题` + 会话元信息 + `## User` / `## Assistant`，
工具调用序列化为 `### Tool: <名称>` + params JSON + `Output` / `Error` / `Metadata` 小节，
推理与异常分别输出 `Reason` / `Exception` 小节。

**一个需要抽查的限制**：序列化只取每条 assistant 消息 `elements` 的最后一组 children。
多步长回合可能丢失中间工具调用。所以导出后要抽查 Markdown 里的工具调用数量
是否与原生 JSON 的 `toolName` 计数接近；差距明显时，以原生 JSON 为准，Markdown 仅作可读副本。

### 1.3 建议的提交组合

```
traces/<题目ID>/
├── chat_session_<sessionUuid>          # 原生明细（主证据）
├── sessions-index.jsonl                # 从 comate_chat_sessions.jsonl 过滤出本题会话行
├── <会话标题>.md                        # 界面导出的可读副本
└── diffInfo-<侧边栏ID>-changes.json     # 代码改动快照
```

只摘取本题相关会话，不要整盘打包 `~/.comate-engine/store/`——
规则明确不提交整个客户端数据库和无关私人会话。

---

## 3. 你要交给 AI 的输入清单

把下面这张表填好再丢给 AI，AI 就能一次把材料铺完。缺的项 AI 只能留 `【待补充】`。

### 3.1 团队级（整个阶段填一次）

```yaml
team_id: ""            # 无正式ID时用"学校名称—队名"
team_name: ""
stage: online
version: ""            # 如 v1
contact: ""            # 姓名+邮箱/电话
freeze_time: ""        # 成果冻结时间，北京时间，精确到分
members:               # 每人实际参与的环节，用于 solution.md
  - name: ""
    work: "需求分析 / 方案设计 / AI指导 / 代码编写 / 调试 / 材料整理"
source_guard: ""       # 实际采取的来源保护措施；没配就写"未配置"
```

Agent、模型、客户端版本不在这张表里——由 AI 从会话明细与应用包读取（见 1.1）。

### 3.2 题目级（每题填一次）

```yaml
task_id: ""            # 如 jm-spec35
project_dir: ""        # 工程绝对路径
build_log: ""          # logs/build.log 路径（没存就说明，AI 会提醒补跑）
selftest_log: ""       # logs/selftest.json 路径
human_edits: ""        # "无人工直接修改代码" 或逐条列出（谁/为什么/哪些文件/前后标识/证据路径）
known_issues: ""       # 未完成项与已知问题，会写进 solution.md
extra_sources: ""      # 额外来源；无则"无"。**访问过来源项目相关提交的，必须在此写明**
```

会话 ID 和轨迹文件也不用你填——AI 按 `project_dir` 和 `task_id` 去
`~/.comate-engine/store/comate_chat_sessions.jsonl` 里反查即可。
你唯一需要动手的是：如果想要人类可读的 Markdown 副本，去侧边栏点一次「导出本地」并告诉 AI 存到哪了。

### 3.3 AI 自己能查到、不用你填的

- 题目 ID 与 `base_commit`：读 `metadata/<题目ID>.json`
- 基线准备脚本记录：读 `reports/build-baselines/<题目ID>.log`
- 改动文件清单、`final.diff`、二进制资源大小与 SHA-256：读工程 git 状态
- bundleName 与入口 Ability：读 `AppScope/app.json5`、`products/*/src/main/module.json5`
- 依赖与锁文件状况、构建命令与产物路径：读 `oh-package.json5`、`build-profile.json5`
- **会话 ID、轨迹文件路径**：查 `~/.comate-engine/store/comate_chat_sessions.jsonl`
- **Agent 名称、模型 ID、effort、token 用量、生效规则**：读会话明细 `payload.model` / `payload.agent` / `agentInfo` / `tokenUsage` / `appliedRuleNames`
- **客户端与扩展版本**：读 `/Applications/Comate.app/.../product.json` 与扩展 `package.json`
- 本题用到的 Skill 与工具清单、失败重试过程：读会话明细的工具调用序列

---

## 4. 成果包目标结构

```
<包根>/
├── submission.json          # 保留本阶段全部题目，未做的留 not_completed
├── README.md                # 公共环境说明
├── solution.md              # 方案、分工、来源保护、冻结时间
├── sources.md               # 第三方来源；无额外来源也要声明
├── traces/                  # 全部原始轨迹（含失败与重试）
├── system-config/           # 实际用的系统提示、Skill、工作流配置
└── tasks/<题目ID>/
    ├── project/             # 完整工程，不能只给补丁或 HAP
    ├── build.md             # 依赖/构建/安装/启动/初始化
    ├── trace-index.md       # 记录索引
    ├── human-changes.md     # 有人工改码时才需要
    ├── changes/final.diff   # base_commit → 最终版本
    └── logs/                # 构建与自测日志
```

`submission.json` 中三个路径字段都填包内相对路径、用 `/` 分隔，后两项必须是文件路径：

```json
{ "task_id": "jm-spec35", "status": "submitted",
  "project_path": "tasks/jm-spec35/project",
  "build_instructions": "tasks/jm-spec35/build.md",
  "trace_index": "tasks/jm-spec35/trace-index.md" }
```

## 5. 执行顺序

1. 验证轨迹导出（第 1 节）→ 导不出就先解决，别往下走。
2. 停止该题所有 AI 与人工改动，记下冻结时间，打版本标识。
3. 还原构建噪声文件，确认 `git status` 只剩真实改动。
4. 把第 3 节表格交给 AI，让它产出 `final.diff`、资源摘要表、`build.md`、`trace-index.md`、`sources.md`、`submission.json` 条目。
5. 导出轨迹到 `traces/`，复制系统提示与 Skill 到 `system-config/`。
6. 拷贝工程到 `project/`（排除 `build/`、`oh_modules/`、`.hvigor/` 等产物）。
7. 校验：把 `final.diff` 应用到基线的干净 clone 上，确认与 `project/` 一致、且能构建出 HAP。
8. 打包、跑检查、算摘要：

   ```bash
   .venv/bin/python tools/check_submission.py <成果包>.zip
   shasum -a 256 <成果包>.zip && ls -l <成果包>.zip
   ```

9. 发正式提交邮件：阶段、团队 ID、版本号、联系人、下载链接与提取码、文件名、大小、SHA-256。

---

## 6. 给 AI 的提示模板（直接复制改用）

```text
请为题目 <题目ID> 整理提交材料，不要改动业务代码。

工程：<project_dir>
赛题包：<赛题包路径>
基线：读 <赛题包>/metadata/<题目ID>.json 的 base_commit

团队与题目信息（YAML，缺失项标 TODO）：
<粘贴第 3.1 与 3.2 两张表>

请完成：
1. 读 templates/submission-checklist.md 与 templates/trace-index.md，按官方字段组织材料
2. 生成 changes/final.diff（自 base_commit，含新增/修改/删除；二进制另列文件、大小、SHA-256）
3. 生成 build.md（依赖安装、构建、安装、启动、应用标识、必要初始化；不得出现本机私有绝对路径）
4. 生成 trace-index.md，客观字段据实填写，无法确认的标【待补充】
5. 生成 sources.md（随包基线声明 + 额外来源；如访问过来源项目相关提交必须如实披露）
6. 输出 submission.json 中本题条目的 JSON 片段
7. 最后列出仍需我补充的字段清单

硬要求：不得编造会话 ID、版本号、时间、分工等无法从工程和日志中核实的信息；
不确定的一律标【待补充】并在末尾汇总。
```

## 7. 自检清单

- [ ] `submission.json` 保留全部题目，团队四个字段非空，路径都指向包内真实文件
- [ ] `final.diff` 与 `project/` 对应同一冻结版本，新增、删除、二进制变更均覆盖
- [ ] `traces/` 能对应到本题具体研发过程，含失败与重试，不是只留成功记录
- [ ] `system-config/` 即使无自定义项也有配置说明
- [ ] `build.md` 不依赖未提交文件和参赛电脑私有路径
- [ ] 无人工改码的题，已在 `trace-index.md` 注明
- [ ] 脱敏范围与记录缺失已说明；包内无账号密钥、签名私钥
- [ ] `check_submission.py` 通过（注意：它只验结构，不验内容真实与完整）

## 8. 本流程踩过的坑

| 坑 | 后果 | 预防 |
| --- | --- | --- |
| 未限制检索域名，AI 自主抓取来源项目实现提交 | 该题 F-point 全部不计通过 | 开发前配置域名黑名单；写进 `system-config/` |
| 只在文件系统里找轨迹、没看界面导出入口 | 误判"轨迹无法导出"，白担一轮风险 | 原生记录看 `~/.comate-engine/store/`，可读副本用侧边栏「导出本地」 |
| 把侧边栏会话 ID 当成引擎 sessionUuid | 索引对不上明细文件 | 两个 ID 都记，说明对应关系 |
| 只摘工程目录下的会话 | 漏掉工作区为赛题包的会话（如测试设计会话） | 按 `workspaceDirectory` 和题目 ID 两个维度各查一遍 |
| 直接打包整个 `~/.comate-engine/store/` | 违反"不提交整个客户端数据库和无关私人会话" | 只摘本题会话明细与索引行 |
| 构建产物文件混进 diff | diff 噪声大，审核费解 | 打包前 `git checkout --` 还原 |
| 只看终端不存日志 | 构建与自测记录无法回溯 | 全程 `tee` 到 `logs/` |
| 想事后补记录 | 截止后禁止补交，且伪造从重处理 | 边做边留，冻结后只整理不新增 |
