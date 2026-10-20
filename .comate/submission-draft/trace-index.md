# 运行记录索引

本索引保留官方模板全部字段，当前为本题材料草案；相对材料路径从 `tasks/cml-spec7/` 读取，工程文件路径从其 `project/` 读取。当前draft中工程副本为 `traces/code-snapshot/project/`。证据最终以各机器清单为准。

- 题目 ID：`cml-spec7`。
- AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围（每道作答的赛题均须填写）：需求拆解/复核、基线审计、方案修订、生产实现/修复、独立构建自测和回归、材料取证。按下面真实角色与原生全文行范围追溯；`workflow/requirements/`、`workflow/design/`、`workflow/implementation/`、`workflow/verification/` 是阶段交接，不能代替原生工具记录。B9–B11仍blocked。
- 基线构建准备：脚本配置版本、执行时间及输出记录路径（见 tools/prepare_baseline.py）：`logs/prepare-baseline.log` 记录 `profile=harmony-cup-build-v1`、`dry_run=false`、本题与基线、`changes=[]`；准备完成登记 `2026-10-20T09:45:41.147840+00:00` 来自 `workflow/setup-result.json`，不是脚本精确起止时刻。官方 `reports/build-baselines/cml-spec7.log` 缺失，版本/路径检查见 `taskbook-versions.json`；不把本地log冒称该官方文件。精确脚本执行起止时间 **【待补充】**。
- Agent 名称及版本：真实工具为 `Codex Desktop`；Windows App包版本 `26.1013.4894.0` 来自 `facts.json.app_package`。原生运行时 `cli_version` 见各会话元数据（当前读取为 `0.163.0-alpha.10.2`），它不是桌面App/Comate扩展版本。角色定义为 `system-config/*/agents/*.toml`，与原生角色字段关联。Comate客户端/扩展版本 **【待补充】 / 不适用：实际工具并非Comate，未发现其索引**。
- 模型名称、版本及运行参数：逐会话 `turn_context.model/effort`、approval/sandbox等见 `traces/session-metadata.json.turn_contexts` 及下表；只填写可见模型ID，不推断内部模型版本。token采用截止时每会话最后可见 `event_msg/token_count.info.total_token_usage`，不逐事件累加，不跨旧快照重复相加；cached input是input子项，reasoning字段按原生口径保留，不能重复加到total。最新 `token_usage_record` 另留源行号与原始口径，活动会话可能晚于token_count；不混合两套计量或宣称最终账单。完整值/截止以机器JSON为准。
- 本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置：本题 `AGENTS.md`、四角色提示及已有 `system-config/initial-20261020T094258Z/`、`system-config/analysis-20261020T095248Z/`、`system-config/implementation-20261020T101847Z/`；实际工作流Skill、ArkTS参考/构建Skill副本和hash见对应清单/文件。工具使用由原生调用/返回证明，包括functions.exec内的shell/read/apply_patch、协作派工、真实构建设备与Hypium、公开通用SDK检索；`traces/session-metadata.json.tools_observed`仅统计外层可见调用，不能覆盖嵌套工具细节。文件存在不自动算已使用；按原生read调用确认。没有新增团队system-config。
- 运行期间配置变更及原因（无则填“无”）：四角色流程和访问范围由任务指令/实际配置副本记录；API/工具链路径按本机环境加载，原.ps1的不可移植限制见 `build.md`。方案布局修订、导航去重、文档测试助手修正、真实大屏旋转顺序修正均有交接和原始轮次。实际提示/配置快照版本见已有system-config及 `workflow/events.jsonl`；未推断缺失的私人全局配置变更。人工全局变更补充 **【待补充】**。
- 主会话 ID：分析 `01a158b5-95c1-7843-be11-cfb16aaa2e74`；实施/回归 `01a158d0-416c-75a3-8836-233f0c35fb6f`；本次材料 `01a1590b-c9f9-7f32-9607-2b3f4c8c38e7`。逐项由原生首行 `payload.id`、本题登记和侧边栏过滤索引证明。
- 关联会话及子会话 ID：见下方完整映射与 `traces/session-metadata.json`。Comate引擎 `sessionUuid` **【待补充】 / 不适用（未发现Comate记录）**；Codex线程与IDE侧边栏ID分别核实。子Agent `payload.session_id` 可能为父主会话，不能替代其自身 `payload.id`；无独立侧边栏行的字段保持待补。
- 解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式：`traces/native/*.jsonl` 为逐行UTF-8原生事件副本；`traces/session-index.filtered.jsonl`仅本题侧边栏索引；`traces/discovery.json`及 `native-discovery-search.json` 保存按工程路径与题号两个维度选择结果；完整构建/设备/测试输出在 `logs/`，逐文件路径/bytes/hash见 `logs-copy-manifest.json`。只导出本题独立记录，不提交整个客户端数据库或无关私人会话。初始化总览 `01a13fc4-2611-7761-a580-1283e0c70541` 按AGENTS排除，未作为功能证据读取。
- 失败、重试、未采用的候选方案及选择过程的记录位置：保留 `workflow/verification/final-verification-03.md`、`workflow/delivery-01.md` 和对应 `logs/verification-*-01/02/03/`；手机原轮1 error及文档补测、旧800vp被误称large后实测1200vp、导航/布局修订、02b并发改源作废、SDK查询失败、磁盘清理自动审批拒绝均可追溯。不能拿失效/跳过证据当当前pass。清理拒绝JSON仍保留，原磁盘未删。
- 实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置：原生JSONL保留消息、工具调用及原返回；机械Markdown逐对象标出原生行号。代码修改交接在 `workflow/implementation/`，方案修订在 `workflow/design/`，第三方研究在 `workflow/provider-research-01.md` / `logs/provider-research-01/`，最终矩阵在 `logs/verification-final-03.json`。`changes/final.diff` 反映完整交付差异，不能替代原生过程。
- 导出时间、方法与读取方式：精确时间以 `traces/session-metadata.json.exported_at_utc` 为准；`tools/export_evidence.py` 只取本题所选原生文件/过滤索引，逐项保存源位置、hash、bytes、字段和快照标记。`traces/markdown/*.md` 是该脚本机械生成的JSONL可读副本，**不是IDE导出**。`md_export_dir` **【待补充】**。下表范围只覆盖当前切片，`snapshot_only=true`、`includes_future_events=false`；当前导出之后事件须由后续打包继续收录。读取JSONL可逐行 `json.loads`，Markdown可直接阅读；源hash和事件行号可互查。
- 成果冻结时间（北京时间，与 `solution.md` 一致）：**【待补充】**（团队 `freeze_time` 为空；材料快照/导出时间不代填正式冻结）。
- 官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识：官方基线 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；Git HEAD仍为基线，未提交改动不能丢失。完整草案交付版本取 `project-manifest.json.final_version` 与 `snapshot_git_tree`；正式团队版本 **【待补充】**，本阶段没有正式提交。
- 基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）：`changes/final.diff`；`changes/changed-files.json`、`binary-files.json`、`resource-files.json` 和完整工程 `project-manifest.json`。补丁校验状态：已通过；完整命令、退出码、逐文件比较与当前摘要见 `patch-validation.json`（`passed=true`）。
- 与提交源码的对应关系：最终拟交project精确复制 `traces/code-snapshot/project/`；按 `project-manifest.json` 每项路径/bytes/SHA-256比对，基线clone后 `git apply --check --binary` 再实际apply和全树比较证据在 `patch-validation.json`。`.comate/submission-draft/`为派生材料，不递归入project；其他真实过程文件按声明清单纳入。缓存/生成磁盘排除及原因见 `project-exclusions.json`。源码/HAP与有效03测试指纹见 `facts.json.validation` 和原始轮次。扩大清单或改源须重新冻结/生成patch，不能把将来的修改视作已覆盖。
- 人工操作及相关记录位置：人工提示在本题原生JSONL消息中；人工操作完整声明 **【待补充】**，原输入 `human_edits` 为空，详见 `human-changes.md`。
- 人工修改索引位置（可使用 `human-changes.md`；无则注明“无人工直接修改代码”）：`human-changes.md`；是否无人工直接改码 **【待补充】**，目前不代填该否定声明。
- 人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置：全部 **【待补充】**，需实际批次与当时证据；总体diff不能代替人工修改归属证明。
- 公开资料检索与代码复用记录位置，以及 `sources.md` 中的对应来源条目：本题 `sources.fragment.md`，待3-package汇入根sources；通用官方SDK实际读取/失败、锁定依赖、基线资源复用与原创正文分别说明。人工 `extra_sources` **【待补充】**。
- 本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 `solution.md`）：实际工作目录 `D:/HCUP/cml-spec7`，交付后为包内 `tasks/cml-spec7/project/`；本题AGENTS/角色及已有system-config限制访问本题、只读公共资源与授权官方模板/本题基线报告，禁止其他题和来源相关修复历史。团队人工 `source_guard` **【待补充】**；实际观察事实见 `solution.fragment.md`、`sources.fragment.md`。
- 脱敏范围（无则填“无”）：当前取证脚本原生副本未做内容脱敏；系统用户名/本地路径保留在原始证据，build指南使用便携相对路径。筛掉无关会话、整个数据库与生成缓存属于选择范围，不冒称内容脱敏；源与副本hash可复核。正式打包敏感信息检查/人工补充 **【待补充】**，不得遮蔽代码来源或修改依据。
- 记录缺失及原因（无则填“无”）：官方指定基线报告不存在；本地准备日志缺独立起止时刻；初始化hdc stdout的Transcript缺口；没有IDE手工Markdown导出；Comate不适用/不存在；部分子Agent独立侧边栏ID未核实；活动会话导出截止后的事件不在切片内；人工声明为空。细项见 `missing-fields.md`、`facts.json.original_record_gaps`。这些缺口没有以新造历史或有利推断补齐。

## 真实ID映射

| Codex线程：payload.id | 原生payload.session_id（不能当子线程ID） | 父线程 | IDE侧边栏ID | 实际角色 |
| --- | --- | --- | --- | --- |
| 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 主会话 / 无父线程字段 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | orchestrator |
| 01a158b7-9d99-7260-95c0-1f8da4f27301 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_requirements |
| 01a158b7-cf4a-7b83-8b86-51f14fe4c556 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_verification |
| 01a158b8-5287-72f1-b1c8-d9a3f6c129b4 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_implementation |
| 01a158bf-f922-7593-823d-2c1460e4f2d4 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 01a158b5-95c1-7843-be11-cfb16aaa2e74 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_design |
| 01a158d0-416c-75a3-8836-233f0c35fb6f | 01a158d0-416c-75a3-8836-233f0c35fb6f | 主会话 / 无父线程字段 | 01a158d0-416c-75a3-8836-233f0c35fb6f | orchestrator |
| 01a158d1-3d40-7092-b3c0-1c60dcb4cd06 | 01a158d0-416c-75a3-8836-233f0c35fb6f | 01a158d0-416c-75a3-8836-233f0c35fb6f | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_requirements |
| 01a158d2-9ec4-7050-87ff-875ea468f5ce | 01a158d0-416c-75a3-8836-233f0c35fb6f | 01a158d0-416c-75a3-8836-233f0c35fb6f | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_design |
| 01a158d3-1977-7490-b337-d28df9f59e73 | 01a158d0-416c-75a3-8836-233f0c35fb6f | 01a158d0-416c-75a3-8836-233f0c35fb6f | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_verification |
| 01a158d7-59c4-7df2-95f7-995b90d6bbee | 01a158d0-416c-75a3-8836-233f0c35fb6f | 01a158d0-416c-75a3-8836-233f0c35fb6f | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_implementation |
| 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 主会话 / 无父线程字段 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | orchestrator |
| 01a1590c-9c06-7340-bb4f-14a58f111ec2 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_requirements |
| 01a1590f-cd99-7df0-9608-5c9d6cece03f | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_design |
| 01a15912-a712-7051-9226-6396f727ba11 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_implementation |
| 01a15914-c10a-7f52-8c6b-5180f42bb365 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | 【待补充】（未找到该原生线程的侧边栏索引行） | harmony_verification |

## 模型参数与累计token口径

| 线程 | 模型/参数（去重turn_context） | input | cached input（input子项） | output | 原生累计total |
| --- | --- | --- | --- | --- | --- |
| 01a158b5-95c1-7843-be11-cfb16aaa2e74 | gpt-6.1-sol / effort=xhigh | 5881396 | 5632000 | 32436 | 5913832 |
| 01a158b7-9d99-7260-95c0-1f8da4f27301 | gpt-6.1-sol / effort=xhigh | 1537672 | 1434624 | 27432 | 1565104 |
| 01a158b7-cf4a-7b83-8b86-51f14fe4c556 | gpt-6.1-sol / effort=xhigh | 5944380 | 5668224 | 30303 | 5974683 |
| 01a158b8-5287-72f1-b1c8-d9a3f6c129b4 | gpt-6.1-sol / effort=xhigh | 1405690 | 1301632 | 15682 | 1421372 |
| 01a158bf-f922-7593-823d-2c1460e4f2d4 | gpt-6.1-sol / effort=xhigh | 944704 | 892800 | 10175 | 954879 |
| 01a158d0-416c-75a3-8836-233f0c35fb6f | gpt-6.1-sol / effort=xhigh | 41876531 | 41115008 | 79772 | 41956303 |
| 01a158d1-3d40-7092-b3c0-1c60dcb4cd06 | gpt-6.1-sol / effort=xhigh | 1741372 | 1618560 | 16364 | 1757736 |
| 01a158d2-9ec4-7050-87ff-875ea468f5ce | gpt-6.1-sol / effort=xhigh | 4168578 | 3895040 | 26920 | 4195498 |
| 01a158d3-1977-7490-b337-d28df9f59e73 | gpt-6.1-sol / effort=xhigh | 27846867 | 27197312 | 103410 | 27950277 |
| 01a158d7-59c4-7df2-95f7-995b90d6bbee | gpt-6.1-sol / effort=xhigh | 4884806 | 4613248 | 19061 | 4903867 |
| 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | gpt-6.1-sol / effort=xhigh | 9696322 | 9531008 | 42888 | 9739210 |
| 01a1590c-9c06-7340-bb4f-14a58f111ec2 | gpt-6.1-sol / effort=xhigh | 868025 | 784896 | 14044 | 882069 |
| 01a1590f-cd99-7df0-9608-5c9d6cece03f | gpt-6.1-sol / effort=xhigh | 1479752 | 1389312 | 17358 | 1497110 |
| 01a15912-a712-7051-9226-6396f727ba11 | gpt-6.1-sol / effort=xhigh | 2412304 | 2323456 | 23389 | 2435693 |
| 01a15914-c10a-7f52-8c6b-5180f42bb365 | gpt-6.1-sol / effort=xhigh | 4958506 | 4840064 | 31069 | 4989575 |

不把上表相加为单一账单：分叉可能继承上下文，不同累计口径/截止事件需保留原生解释。最新 `token_usage_record` 的usage、thread/turn/session/root_turn/response标识和源行号保存在机器JSON及原生文件，不用它覆盖或重算另一口径。

## 原生文件与事件范围

| 线程 | 原生/机械Markdown副本 | 本次切片事件行范围 | 原生副本SHA-256 |
| --- | --- | --- | --- |
| 01a158b5-95c1-7843-be11-cfb16aaa2e74 | `traces/native/01a158b5-95c1-7843-be11-cfb16aaa2e74.jsonl` / `traces/markdown/01a158b5-95c1-7843-be11-cfb16aaa2e74.md` | 1–557（ordinal 0–556） | 43132167c688851633415e98e67faf6294cfbc0e5455dfc6f760725a0e6e9b21 |
| 01a158b7-9d99-7260-95c0-1f8da4f27301 | `traces/native/01a158b7-9d99-7260-95c0-1f8da4f27301.jsonl` / `traces/markdown/01a158b7-9d99-7260-95c0-1f8da4f27301.md` | 1–155（ordinal 0–154） | 57bc6b90707ea6e6dbc8ca5b0243ec550edc40f00d5b74f6c32b0588edf2ea7b |
| 01a158b7-cf4a-7b83-8b86-51f14fe4c556 | `traces/native/01a158b7-cf4a-7b83-8b86-51f14fe4c556.jsonl` / `traces/markdown/01a158b7-cf4a-7b83-8b86-51f14fe4c556.md` | 1–441（ordinal 0–440） | aa55d3e8c4fddb5480ae8daa7aa05c0af0facf7410574fcd12d52b77a1794c53 |
| 01a158b8-5287-72f1-b1c8-d9a3f6c129b4 | `traces/native/01a158b8-5287-72f1-b1c8-d9a3f6c129b4.jsonl` / `traces/markdown/01a158b8-5287-72f1-b1c8-d9a3f6c129b4.md` | 1–141（ordinal 0–140） | 9732cee741a481f6a982191aa3b677315c1d2f58932528b19038d1fe93505c2b |
| 01a158bf-f922-7593-823d-2c1460e4f2d4 | `traces/native/01a158bf-f922-7593-823d-2c1460e4f2d4.jsonl` / `traces/markdown/01a158bf-f922-7593-823d-2c1460e4f2d4.md` | 1–132（ordinal 0–131） | d528b3e53c40783562429665ddd3a4b1d1ef4e4814364040d52f4e33d81fa5d2 |
| 01a158d0-416c-75a3-8836-233f0c35fb6f | `traces/native/01a158d0-416c-75a3-8836-233f0c35fb6f.jsonl` / `traces/markdown/01a158d0-416c-75a3-8836-233f0c35fb6f.md` | 1–1847（ordinal 0–1846） | 35c74e9d1015560a51a1e5d233ba5ee668a989f03ee25dc817a38aaa3a69ff7c |
| 01a158d1-3d40-7092-b3c0-1c60dcb4cd06 | `traces/native/01a158d1-3d40-7092-b3c0-1c60dcb4cd06.jsonl` / `traces/markdown/01a158d1-3d40-7092-b3c0-1c60dcb4cd06.md` | 1–174（ordinal 0–173） | 4f10a2d1d2a6212b6f5a8f30a8d850ec68e8305ed5155720bb67d7bd3348a8b7 |
| 01a158d2-9ec4-7050-87ff-875ea468f5ce | `traces/native/01a158d2-9ec4-7050-87ff-875ea468f5ce.jsonl` / `traces/markdown/01a158d2-9ec4-7050-87ff-875ea468f5ce.md` | 1–328（ordinal 0–327） | 07f5e5a38701855127d9743aec0a5e616fad4f1ad6ddfa67dfcca97ac5fc7130 |
| 01a158d3-1977-7490-b337-d28df9f59e73 | `traces/native/01a158d3-1977-7490-b337-d28df9f59e73.jsonl` / `traces/markdown/01a158d3-1977-7490-b337-d28df9f59e73.md` | 1–1357（ordinal 0–1356） | b49ab8d769fb9f2cde82a7d22aef11cf85c661d5ded4af36cc86b786d7fab558 |
| 01a158d7-59c4-7df2-95f7-995b90d6bbee | `traces/native/01a158d7-59c4-7df2-95f7-995b90d6bbee.jsonl` / `traces/markdown/01a158d7-59c4-7df2-95f7-995b90d6bbee.md` | 1–305（ordinal 0–304） | 9315b6834c92d7838dc7d1f956c2f53bdf167d67f2bcb90cbe43826aa1dfb4d0 |
| 01a1590b-c9f9-7f32-9607-2b3f4c8c38e7 | `traces/native/01a1590b-c9f9-7f32-9607-2b3f4c8c38e7.jsonl` / `traces/markdown/01a1590b-c9f9-7f32-9607-2b3f4c8c38e7.md` | 1–692（ordinal 0–691） | 3c1de86966b4d5ff2027329ea3409a2dc234481346c7910292c95cef9c09e836 |
| 01a1590c-9c06-7340-bb4f-14a58f111ec2 | `traces/native/01a1590c-9c06-7340-bb4f-14a58f111ec2.jsonl` / `traces/markdown/01a1590c-9c06-7340-bb4f-14a58f111ec2.md` | 1–138（ordinal 0–137） | 4c4cca07b3cfae50391b87ee532350e7a466a2cf4f980e050a68874751c378da |
| 01a1590f-cd99-7df0-9608-5c9d6cece03f | `traces/native/01a1590f-cd99-7df0-9608-5c9d6cece03f.jsonl` / `traces/markdown/01a1590f-cd99-7df0-9608-5c9d6cece03f.md` | 1–162（ordinal 0–161） | 8dd2144523b3120f6ac666d0aeb8674082e9d83d3ded075498744ae071502578 |
| 01a15912-a712-7051-9226-6396f727ba11 | `traces/native/01a15912-a712-7051-9226-6396f727ba11.jsonl` / `traces/markdown/01a15912-a712-7051-9226-6396f727ba11.md` | 1–225（ordinal 0–224） | d1e47d41a1d262c928455b0c134f076318f05bb456bd8b8d2f257ef609eff826 |
| 01a15914-c10a-7f52-8c6b-5180f42bb365 | `traces/native/01a15914-c10a-7f52-8c6b-5180f42bb365.jsonl` / `traces/markdown/01a15914-c10a-7f52-8c6b-5180f42bb365.md` | 1–357（ordinal 0–356） | 8d8c0c4e22313040ea07a19b0dcd88ed903fa227dea610f0280041b62431139f |

每个原生文件从首个session_meta到本次导出截止均可读；文件SHA对应本次切片，不承诺活动会话最终结束。脱敏/选择与缺失见官方字段说明。

## 实际任务书版本

`taskbook-versions.json`记录公共目录所属仓库HEAD及真实git顶层：公共spec-harness不是独立仓库，不能把其包含仓库HEAD当成四文件内容版本。四文件逐一校验如下，本题副本与实际公共输入对应；官方模板hash另在该JSON。`spec/history/`当前历史清单为空，没有编造历史版本。

| 实际任务书 | 公共SHA-256 | 本题副本SHA-256 |
| --- | --- | --- |
| spec-harness/0-analyze.md | a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a | a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a |
| spec-harness/1-do.md | 2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d | 2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d |
| spec-harness/2-submit.md | 43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9 | 43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9 |
| spec-harness/3-package.md | 3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c | 3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c |

## 补充取证位置与字节范围

原始人工输入与官方逐字段模板的包内只读副本为 `evidence-inputs/team.yaml`、`evidence-inputs/submit-input.yaml`、`evidence-inputs/templates/`。本材料阶段实际读取的工作流Skill及四角色配置副本/hash在 `evidence-inputs/current-config/manifest.json`；它是本题材料附件，不改团队根system-config。原始公共输入路径用于来源说明，离线核对可直接读取这些随包副本。

`changes/line-ending-only.json`另列既有Windows CRLF与基线LF造成的纯行尾差异；这些既有字节差异纳入exact-bytes补丁，但不计为本材料阶段业务改动。主调度在临时基线clone中设置 `core.autocrlf=false`，以清单内真实字节生成和应用补丁，不改原工程行尾。文件数、清单hash与比较结果以最终机器JSON为准。

本材料阶段沿用同一生产源码的历史构建/设备结论：`current-production-fingerprint.json`与最终03验收完整生产输入SHA一致，没有通过重跑构建制造新证据；根调度的 `git diff --check` 退出0，记录见本次原生会话及材料验证报告。
