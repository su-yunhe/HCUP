# 运行记录索引

这是 `cml-spec28` 的 2-submit **材料草稿**。用户已授权在保留 AUTH 限制下整理材料；不将 1-do 改判完成，不决定 submitted 状态，不对外上传。以下字段按官方 `trace-index.md` 模板填写，未核事实明确保留【待补充】。

- 题目 ID：`cml-spec28`。
- AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围（每道作答的赛题均须填写）：0-analyze 需求拆解、基线/运行核对；1-do 方案、编码、构建及独立验证；本轮 preflight、一致性/脚本漂移取证、非 AUTH 边界、09/10 修复、2-submit 材料整理。下表 16 个本题会话覆盖各自 native 第 1 行至快照末行，包含已有失败、重试、工具调用、结果及候选选择；初始化总览不作实现证据。仅保存客户端实际保留记录，不补造未记录信息。
- 基线构建准备：脚本配置版本、执行时间及输出记录路径（见 tools/prepare_baseline.py）：本地 `harmony-cup-build-v1`，`workflow/setup-result.json` 登记 prepared_at=`2026-10-18T11:23:55.178947+00:00`；未将此结果归档时间冒充精确脚本开始/结束时刻。真实本地执行结果 [prepare-baseline.log](project/logs/prepare-baseline.log)、[setup-result.json](project/workflow/setup-result.json)、[baseline-provenance.json](project/workflow/baseline-provenance.json)、`logs/official-preparation-before-fast-forward.patch`；原始基线 assembleHap 日志 `logs/baseline-build.log`，后续独立 clean 基线在 `traces/analysis/baseline-runtime/commands.jsonl` / `baseline-clean-build.log`。原脚本源码/逐次时间若未留存不能推测；官方规定的报告路径未找到的事实见需求材料复审，不以本地日志冒充官方报告。
- Agent 名称及版本：native `session_meta.originator=Codex Desktop`，`cli_version=0.163.0-alpha.10.2`（这是 native/CLI 运行器版本）。材料核查时桌面客户端installedVersion=`26.1013.40934`、build=`20770`、channel=`prod`，证据为任务材料reference/app-version-probe.json（工程内同副本位于project/.comate/submission-draft/reference/）的实际只读工具返回；未由此反推所有旧运行时点桌面版本，也未以 CLI 版本冒充；四原生角色 `harmony_requirements / harmony_design / harmony_implementation / harmony_verification` 与 root 编排的配置、派工、真实工具记录均有保存。
- 模型名称、版本及运行参数：16 会话 `turn_context.model=gpt-6.1-sol`、`effort=xhigh`、provider=`openai`；公开别名背后精确模型构建版本、temperature/top_p/seed【待补充】，未在 native 中明示，不能由默认值推断。`approval_policy=never` 与 `danger-full-access` 等按各会话原始 turn_context 保存，非声称只靠硬性沙箱实现来源隔离。token 使用见下表/manifest，保持 native 累计值与缓存字段；不汇总成计费数。
- 本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置：`system-config/initial-20261018T112051Z/`、`system-config/development-20261018/`，逐文件 SHA 见下表及 manifest。已登记使用 `harmony-task-flow`、`arkts-syntax-assistant`、`hmos-arkts-knowledge-retriever`、`hmos-arkts-syntax-checker`；真实读取/检索调用的 native 行索引见各会话 `skill_tool_input_references`（只提及路径不自动证明执行），方案/实现报告记录实际引用与检索失败。完整 native session_meta.base_instructions、turn_context、world_state、实际提示/调度记录保留；不声称捕获未持久化的系统内部配置。顶层工具统计见下，exec 内嵌的主机/浏览器/构建/设备命令应结合其完整 input/output 读取。
- 运行期间配置变更及原因（无则填“无”）：初始化与开发期四角色 TOML 哈希各自一致；开发期另保存三个 ArkTS skill 文本，作为实际参考配置快照。源/测试/运行 helper 修正与配置阶段变更见 dispatch、09/10方案及失败索引，不与 AI 模型参数变更混淆；导出观测到模型/effort 均相同，不能断言未记录配置绝无变化。2-submit 本轮只整理材料。
- 主会话 ID：分析 `01a14ec1-e3a8-7183-892e-5c5ac3cab727`；开发 `01a14ed6-ebac-7950-be16-b6d4297adb41`；当前 `01a14f53-1fa0-72d2-b947-fa27e7fb37c7`。这些为 Codex 引擎 native UUID。当前 root 独立 app threadId 证据为 [submit-app-thread-proof.json](project/workflow/submit-app-thread-proof.json)，与 native UUID 相同；其余 IDE 侧栏 ID【待补充】，不将 CODEX_THREAD_ID 或共享环境变量自动当 Comate sessionUuid。
- 关联会话及子会话 ID：见下表，state 的重复登记去重、两个早期 null 登记后已有实际 UUID 解析记录；不伪造新 UUID。
- 解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式：本次 [manifest.json](../../traces/cml-spec28/manifest.json) 列每个原件源绝对位置、字节数、SHA256、快照时点及本地 raw/Markdown 相对路径；JSONL UTF-8 每行一事件，Markdown 逐事件完整展示原生 JSON 与可读字符串。它是 **native 派生副本，不是 IDE 侧栏导出**。本题构建/自测原件继续位于 `logs/`、`traces/analysis/`、`traces/fixture-ui/`、`traces/boundary-completion/` 及 `workflow/verification/` 的索引中；SQLite 可只读打开、JSON/JSONL 用 UTF-8、截图直接读取。Comate 指定索引 `C:/Users/22580/.comate-engine/store/comate_chat_sessions.jsonl` 不存在，项目路径 `D:/HCUP/cml-spec28` 和题号 `cml-spec28` 两维检索均无法进行；无 Comate 记录/DB 导出可宣称，未扫描或复制整个客户端数据库。
- 失败、重试、未采用的候选方案及选择过程的记录位置：本页后续“失败与缺口”列具体原件；全 16 会话未以 pass/fail 筛选，原始工具错误与后续修正均保留。旧版本失败不能因最终修复被覆盖或记为通过。
- 实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置：下表所有完整 raw/Markdown，manifest 的 `tool_call_locations` 与 `skill_tool_input_references` 提供行定位；`workflow/dispatch/`、`workflow/design/`、`workflow/implementation/`、`workflow/verification/` 和 `workflow/boundary-completion-final.md/json` 给出按源码/产物对应关系。
- 导出时间、方法与读取方式：见下“导出核验”。`traces/export_native.py` 按 state 已登记 UUID，仅从本题历史 manifest 的精确源路径取 native；核 `session_meta.id/cwd`，按开始大小一次读取原始字节，复制后散列；完整派生每个已存事件，不恢复 native 中已有截断/压缩/加密内容。`traces/finalize_trace_index.py` 校验副本及完善索引。未读取初始化总览正文、未全库扫描、未对外上传。
- 成果冻结时间（北京时间，与 `solution.md` 一致）：【待补充】。本轮及本页是 snapshot_only=true，includes_future_events=false，**导出时点不是正式 freeze_time**，不能用构建结束、文件修改或此页生成时间替代团队冻结声明；root/本角色仍产生后续材料事件。
- 官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识：官方 base=`9a1d608dc89acfc301657c33ce5dd6089cbf9572`；准备后 HEAD=`b75aa21fdb29af1d3d00aa313360da85c6e05e4f`，不能冒充功能最终提交。当前正式10以 [development-frozen-fingerprint-10.json](project/workflow/implementation/development-frozen-fingerprint-10.json) 的 827 源及聚合 `3eaa13107c4b8d83485fa473c8f83a42bedb8498783faa0539de4a9f12c0fa1c` 标识；正式HAP SHA256=`51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229`。成果包版本/最终提交选择【待补充】，正式10不是团队包版本。
- 基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）：由 root 在本 draft 的 `changes/` 统一生成并核验；本角色不生成/修改工程差异。当前生成状态以目录和 root 交接为准，未签核前【待补充】，不把两份09/10局部diff当完整差异。完整工程/二进制摘要/应用标识亦由 root 对应同一冻结版本。
- 与提交源码的对应关系：本题原生记录按时间包含原始基线、开发版本及08→09→10；最终10保留09 LogInterceptor config安全回退和原error传播，10仅将电话输入类型改Normal，VM校验不改。隔离 app-r3/r4/r5 的fixture证据均按版本保存，不能当正式生产AUTH验收。最终完整源码、827清单、HAP及完整差异必须同版；参考 [boundary-completion-final.json](project/workflow/boundary-completion-final.json) / 最终完整性清单。
- 人工操作及相关记录位置：用户提示、边界授权、AUTH保留、运行/环境协调等保留在 root native 与本题派工；`workflow/state.json` 的 development_login、实际设备/runner记录保留登录边界事实。本题 `spec/submit-input.yaml` 的人类完整操作/修改声明未给全，不能凭AI记录替用户断言不存在未登记操作。
- 人工修改索引位置（可使用 `human-changes.md`；无则注明“无人工直接修改代码”）：【待补充】。Root 材料索引待结合用户 human_edits 声明；当前空字段不等于“无人工直接修改代码”。
- 人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置：【待补充】。不根据机器用户名、线程昵称、AI角色或 final.diff 猜人类作者；native 中有证据的AI实际编辑与对应调用可直接查阅。
- 公开资料检索与代码复用记录位置，以及 `sources.md` 中的对应来源条目：本题 [development-sources.json](project/workflow/design/development-sources.json) 记录 `@ibestservices/area-data@0.0.6`、Apache-2.0、官方OHPM元数据/包SHA及本地ArkTS资料；`third_party/area-data-0.0.6/` 保存本题许可/提取数据；09/10方案记录通用ArkTS/TextInput参考。对应 native 保留原检索失败/超时/读取记录。`sources.md` 由 root 整理对应条目；用户完整 extra_sources 声明【待补充】，不能填无。
- 本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 `solution.md`）：`D:/HCUP/cml-spec28`；[AGENTS.md](project/AGENTS.md)、system-config 两期 skill/role 配置、本题 dispatch 限定本题＋只读common，禁止他题工程/上游修复历史/初始化总览正文，不派生范围外子任务。当前导出也遵循该约束，只读获准三官方模板。可核配置事实不替代团队完整 source_guard 声明，该声明【待补充】；`solution.md` 由 root 综合。
- 脱敏范围（无则填“无”）：本次本地 native 原字节未脱敏，未上传。限范围正则扫描未确认明文凭据；3个key形状命中均位于原生加密/opaque值，位置和分类见 manifest，不在本页打印值。原生 session_meta 含账户标识/本机路径，外部打包前仍须按官方规则审阅并登记实际脱敏；公开受控 `fixture28-public-identity` 是fixture常量，不按真实凭证处理。扫描非完整保密审计；不能声称未检出的值绝不存在。
- 记录缺失及原因（无则填“无”）：见下“失败与缺口”、manifest.gaps、需求角色待补字段。桌面版本、旧IDE侧栏ID、Comate缺失、原生加密字段、首失败构建预指纹及旧结果完整字节缺口均保留；不重写旧指纹、不拿后续日志替原记录，也不声称本次快照包含未来材料事件。

## 会话原件及完整派生副本

下表范围为 `workflow/state.json` 实际登记16个去重UUID，各原件 session_meta.cwd 均为本题根。明确排除初始化总览 `01a13fc4-2611-7761-a580-1283e0c70541`，未读其正文。IDE列只有当前root有独立证据；其他格的【待补充】不等于引擎UUID缺失。

| 阶段 / 角色 | Codex 引擎 native UUID | IDE 侧栏 threadId | 本次副本 | JSONL行数 / 最后存储事件时间UTC |
| --- | --- | --- | --- | --- |
| 0-analyze · orchestrator<br>root | `01a14ec1-e3a8-7183-892e-5c5ac3cab727` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-24-52-01a14ec1-e3a8-7183-892e-5c5ac3cab727.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ec1-e3a8-7183-892e-5c5ac3cab727.md) | 528 / 2026-10-18T11:43:17.303Z |
| 0-analyze · harmony_requirements<br>/root/requirements | `01a14ec2-e729-7262-92a5-99ae0252db40` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-25-58-01a14ec2-e729-7262-92a5-99ae0252db40.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ec2-e729-7262-92a5-99ae0252db40.md) | 177 / 2026-10-18T11:39:32.783Z |
| 0-analyze · harmony_design<br>/root/baseline_map | `01a14ec3-18d4-7310-9f0e-28bd504cf73e` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-26-11-01a14ec3-18d4-7310-9f0e-28bd504cf73e.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ec3-18d4-7310-9f0e-28bd504cf73e.md) | 166 / 2026-10-18T11:35:16.799Z |
| 0-analyze · harmony_verification<br>/root/baseline_verify | `01a14ec3-4d6a-7040-abb7-2613d343e7f1` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-26-24-01a14ec3-4d6a-7040-abb7-2613d343e7f1.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ec3-4d6a-7040-abb7-2613d343e7f1.md) | 383 / 2026-10-18T11:38:29.994Z |
| 0-analyze · harmony_implementation<br>/root/analysis_audit | `01a14ecb-afbe-7ef3-99d5-79087c8e5dbb` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-35-34-01a14ecb-afbe-7ef3-99d5-79087c8e5dbb.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ecb-afbe-7ef3-99d5-79087c8e5dbb.md) | 182 / 2026-10-18T11:42:42.680Z |
| 1-do · orchestrator<br>root | `01a14ed6-ebac-7950-be16-b6d4297adb41` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-47-52-01a14ed6-ebac-7950-be16-b6d4297adb41.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ed6-ebac-7950-be16-b6d4297adb41.md) | 2913 / 2026-10-18T13:53:52.978Z |
| 1-do · harmony_design<br>/root/design_dev | `01a14eda-2a6f-7900-8593-f96cac44de1b` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-51-23-01a14eda-2a6f-7900-8593-f96cac44de1b.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14eda-2a6f-7900-8593-f96cac44de1b.md) | 703 / 2026-10-18T13:28:40.404Z |
| 1-do · harmony_requirements<br>/root/requirements_dev | `01a14ed8-3726-70e2-ac31-135779f2341c` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-49-15-01a14ed8-3726-70e2-ac31-135779f2341c.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ed8-3726-70e2-ac31-135779f2341c.md) | 157 / 2026-10-18T11:55:43.990Z |
| 1-do · harmony_verification<br>/root/verify_dev | `01a14edc-838b-71a2-9851-9e3b7840a63b` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-53-56-01a14edc-838b-71a2-9851-9e3b7840a63b.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14edc-838b-71a2-9851-9e3b7840a63b.md) | 1912 / 2026-10-18T13:52:25.389Z |
| 1-do · harmony_implementation<br>/root/implement_dev | `01a14ede-a8fa-7e80-b89a-59f96f52dda0` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T19-56-17-01a14ede-a8fa-7e80-b89a-59f96f52dda0.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14ede-a8fa-7e80-b89a-59f96f52dda0.md) | 1063 / 2026-10-18T13:31:28.630Z |
| 1-do · harmony_requirements<br>/root/requirements_fixture | `01a14f08-476a-7560-9e18-aa4321c0b14b` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T20-41-45-01a14f08-476a-7560-9e18-aa4321c0b14b.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f08-476a-7560-9e18-aa4321c0b14b.md) | 231 / 2026-10-18T13:48:14.503Z |
| 2-submit preflight / boundary / materials · orchestrator<br>root | `01a14f53-1fa0-72d2-b947-fa27e7fb37c7` | 01a14f53-1fa0-72d2-b947-fa27e7fb37c7 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T22-03-30-01a14f53-1fa0-72d2-b947-fa27e7fb37c7.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f53-1fa0-72d2-b947-fa27e7fb37c7.md) | 2540 / 2026-10-19T02:12:50.214Z |
| 2-submit preflight / boundary / materials · harmony_design<br>/root/submit_design | `01a14f55-3f56-7841-af11-d4ab55b3ba1a` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T22-05-49-01a14f55-3f56-7841-af11-d4ab55b3ba1a.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f55-3f56-7841-af11-d4ab55b3ba1a.md) | 595 / 2026-10-19T02:12:58.027Z |
| 2-submit preflight / boundary / materials · harmony_requirements<br>/root/submit_requirements | `01a14f55-1969-7703-8fb7-ef6f5619d6da` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T22-05-39-01a14f55-1969-7703-8fb7-ef6f5619d6da.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f55-1969-7703-8fb7-ef6f5619d6da.md) | 822 / 2026-10-19T02:12:14.107Z |
| 2-submit preflight / boundary / materials · harmony_verification<br>/root/submit_verification | `01a14f55-5f14-7860-976f-10407965f444` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T22-05-57-01a14f55-5f14-7860-976f-10407965f444.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f55-5f14-7860-976f-10407965f444.md) | 2396 / 2026-10-19T02:12:57.834Z |
| 2-submit preflight / boundary / materials · harmony_implementation<br>/root/submit_implementation | `01a14f58-dd63-7fb1-8463-04c83e0cf7e4` | 【待补充】 | [raw](../../traces/cml-spec28/20261019T021256Z/native/rollout-2026-10-18T22-09-46-01a14f58-dd63-7fb1-8463-04c83e0cf7e4.jsonl) / [完整派生 Markdown](../../traces/cml-spec28/20261019T021256Z/markdown/01a14f58-dd63-7fb1-8463-04c83e0cf7e4.md) | 1039 / 2026-10-19T02:12:58.731Z |

## 导出核验

- 本次运行：`20261019T021256Z`；开始 UTC `2026-10-19T02:12:56.892941+00:00`，复制/派生结束 UTC `2026-10-19T02:12:59.491079+00:00`。16 raw 总字节 `55777050`，16 Markdown 总字节 `74635604`，JSONL解析错误0；逐文件 SHA 和完整事件数量复核见 manifest.export_verification。
- 当前root捕获截止 UTC `2026-10-19T02:12:58.305137+00:00`，本实现角色捕获截止 `2026-10-19T02:12:59.193773+00:00`；每个会话另记 source开始/结束大小、mtime、最后已存事件时间。截止后的消息、工具结果、索引整理不在这些raw内，正式打包前需新截点。
- 部分客户端原生字段是 encrypted_content / gAAAA 开头加密字符串。Markdown逐条保留这些原始字段但不解密；不能称为全部提示的可解密IDE正文。若另需IDE明文导出，其当前证据仍【待补充】。含compacted/world_state的原始事件同样保留，不扩充模型未输出的内部思考。
- 顶层实际调用统计：`exec`×1131、`followup_task`×43、`list_agents`×6、`request_user_input_async`×3、`send_message`×427、`sleep`×25、`spawn_agent`×13、`wait_agent`×127。工具清单只是定位辅助，不把静态出现的API名都算已执行；exec内部命令、返回与错误请读对应JSONL/Markdown。
- 导出脚本第一次于 `20261019T021248Z` 因变量列表数量不符失败（`ValueError: too many values to unpack (expected 5)`）；失败原生记录在本实现会话行1032/1033，失败目录原件保留。随后修正后 `20261019T021256Z` 成功，终端结果保存 `workflow/implementation/submit-traces-export-01.log`。未删失败目录或用其不完整副本当成功结果。

## native token记录（不作账单/独立工作量总和）

以下是各会话最后 token_count.info.total_token_usage 的原生累计值，含重复/继承上下文与缓存；不把各行简单相加归算本题实际计费。全部 token_usage_record、每次原始事件、上下文窗口及最后计数时点保存在 manifest 与原件；精确token缺项不补0。

| 引擎UUID | input | cached_input | output | reasoning_output | total | native计数行 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `01a14ec1-e3a8-7183-892e-5c5ac3cab727` | 5311048 | 5191424 | 21678 | 6387 | 5332726 | 527 |
| `01a14ec2-e729-7262-92a5-99ae0252db40` | 1264925 | 1184896 | 34391 | 7334 | 1299316 | 176 |
| `01a14ec3-18d4-7310-9f0e-28bd504cf73e` | 2049036 | 1877120 | 19577 | 2125 | 2068613 | 165 |
| `01a14ec3-4d6a-7040-abb7-2613d343e7f1` | 4928097 | 4800512 | 25949 | 7414 | 4954046 | 382 |
| `01a14ecb-afbe-7ef3-99d5-79087c8e5dbb` | 1765418 | 1644928 | 15610 | 2843 | 1781028 | 181 |
| `01a14ed6-ebac-7950-be16-b6d4297adb41` | 50844206 | 50317440 | 127902 | 69131 | 50972108 | 2912 |
| `01a14eda-2a6f-7900-8593-f96cac44de1b` | 16660434 | 16391040 | 58341 | 12512 | 16718775 | 702 |
| `01a14ed8-3726-70e2-ac31-135779f2341c` | 1528190 | 1417600 | 14217 | 2808 | 1542407 | 156 |
| `01a14edc-838b-71a2-9851-9e3b7840a63b` | 35241270 | 34794880 | 172651 | 63088 | 35413921 | 1911 |
| `01a14ede-a8fa-7e80-b89a-59f96f52dda0` | 26408925 | 26115584 | 100946 | 26851 | 26509871 | 1062 |
| `01a14f08-476a-7560-9e18-aa4321c0b14b` | 2902267 | 2740864 | 19037 | 4827 | 2921304 | 230 |
| `01a14f53-1fa0-72d2-b947-fa27e7fb37c7` | 38298531 | 37825408 | 141189 | 80884 | 38439720 | 2538 |
| `01a14f55-3f56-7841-af11-d4ab55b3ba1a` | 12750786 | 12095360 | 50654 | 13389 | 12801440 | 592 |
| `01a14f55-1969-7703-8fb7-ef6f5619d6da` | 17539437 | 16890880 | 71053 | 20281 | 17610490 | 821 |
| `01a14f55-5f14-7860-976f-10407965f444` | 54435994 | 53798016 | 148710 | 53995 | 54584704 | 2394 |
| `01a14f58-dd63-7fb1-8463-04c83e0cf7e4` | 23196709 | 22393728 | 108619 | 29156 | 23305328 | 1034 |

## 任务书及配置版本

`D:/HCUP/common/.git` 不存在，本次不宣称common有可核独立Git HEAD，以下对四份实际只读任务书保存SHA256；本题 `spec-harness/` 为输入副本，具体任务书来源以本次hash为准。官方模板trace-index SHA256=`d6936aef4500d6a19e4289de8e1455b53200f3113d6445f7e80ccb3c42a4c191`。`spec/history/` 本次不存在；本题保留 requirement/metadata/acceptance，但不能伪造历史目录或旧版需求。

| common/spec-harness任务书 | SHA256 |
| --- | --- |
| 0-analyze.md | `a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a` |
| 1-do.md | `2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d` |
| 2-submit.md | `43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9` |
| 3-package.md | `3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c` |

本题配置文件仅按实际已保存文本登记，完整内容从本题 system-config 读取。原生 session_meta.base_instructions/turn_context 也是实际运行记录；未保存的应用全局配置与服务端模型实现不能追补为已存。

| 本题已保存配置路径 | SHA256 |
| --- | --- |
| `system-config/development-20261018/arkts-syntax-assistant-SKILL.md` | `3819b8534ada65c06d9b30935514232785b2599d5ac06190360938752265f3e2` |
| `system-config/development-20261018/harmony-task-flow-SKILL.md` | `be2e19c305bdc68e904af8cf074186b7eaa582a76db3ca1e854ec8f1434fc3f7` |
| `system-config/development-20261018/harmony_design.toml` | `49da9b49fc63149fa704365387cb8b56fa2db640cfdc8a1cc2df04070672147c` |
| `system-config/development-20261018/harmony_implementation.toml` | `975b3421eeb36f724d7eff6517da003d266ab0da872b68d297a301822f1fee26` |
| `system-config/development-20261018/harmony_requirements.toml` | `d2454861149e9914abc16ad5f617c9cd45d8d9f23e6bdea3b527744aa72f2241` |
| `system-config/development-20261018/harmony_verification.toml` | `349afa65487f83e06630469bcec5dab17db7bede048df68a1f055d106a5567e4` |
| `system-config/development-20261018/hmos-arkts-knowledge-retriever-SKILL.md` | `f46bde5b21ba1b1849c171917885ce4790c32da35790df617bb31e0094190304` |
| `system-config/development-20261018/hmos-arkts-syntax-checker-SKILL.md` | `9746eadf1bdbd14cb418a3aa9f7958d356e896eb14cce2d8569dac484ff3f830` |
| `system-config/initial-20261018T112051Z/agents/harmony_design.toml` | `49da9b49fc63149fa704365387cb8b56fa2db640cfdc8a1cc2df04070672147c` |
| `system-config/initial-20261018T112051Z/agents/harmony_implementation.toml` | `975b3421eeb36f724d7eff6517da003d266ab0da872b68d297a301822f1fee26` |
| `system-config/initial-20261018T112051Z/agents/harmony_requirements.toml` | `d2454861149e9914abc16ad5f617c9cd45d8d9f23e6bdea3b527744aa72f2241` |
| `system-config/initial-20261018T112051Z/agents/harmony_verification.toml` | `349afa65487f83e06630469bcec5dab17db7bede048df68a1f055d106a5567e4` |
| `system-config/initial-20261018T112051Z/environment/toolchain-Enter-HarmonyEnv.ps1` | `53480e4ca2d362f2ab4e5ef476d24b828b0fa8b8b0960a5342aacee7eabd9199` |
| `system-config/initial-20261018T112051Z/environment/workspace-Enter-HarmonyEnv.ps1` | `6ca0e1ef48aa716359a1e9708d1568cbf8879e6b7d4f00b93cde058e2518adbf` |
| `system-config/initial-20261018T112051Z/setup-tools/Adopt-PreparedTaskBranch.py` | `15b0afc0e0d6faff048527fc400cf8ab563a12f293229d0e8bd797039628bf78` |
| `system-config/initial-20261018T112051Z/setup-tools/Finish-TaskPreparation.py` | `f28f7dcf8e8589a99cf9143e0e24048c8e00a4f02697f6da37229b0518ca66e3` |
| `system-config/initial-20261018T112051Z/setup-tools/Initialize-TaskWorktree.py` | `201f1a3882bb2484df9df5f4530b30bbf9840499e034e67cd7b55057955d6e5e` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/agents/openai.yaml` | `6a81c0eb36ca3780114271164f4cee55fbff1003357ede4173ae1b1aac9a9b56` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/references/local-setup.md` | `d1a7b0ba106560d490305e0d4225b89c95b4212a3227fe7ea48cb4e90ca57c3b` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/references/protocol.md` | `c919b8ce7de45e938e7f59981a33ba614f45ed1c87d35a6db81efb7a4d79b894` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/references/traces.md` | `49d79aeaf752c31480918e8429057478952dc47d33a72115453dc558988f0d49` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/scripts/snapshot_traces.py` | `582edd1df05518a2538416464193eab995393668fbce7e6325ec6b6d6fc7c7fb` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/scripts/workflow.py` | `9b4bc901259169e61d35c51012ed667fe87940ba05a4e2de6c8da4db0c75f34e` |
| `system-config/initial-20261018T112051Z/skills/harmony-task-flow/SKILL.md` | `be2e19c305bdc68e904af8cf074186b7eaa582a76db3ca1e854ec8f1434fc3f7` |
| `system-config/initial-20261018T112051Z/skills/hmos-arkts-syntax-checker/SKILL.md` | `9746eadf1bdbd14cb418a3aa9f7958d356e896eb14cce2d8569dac484ff3f830` |

## 失败与缺口

- 正式AUTH仍阻断：最终 formal10-final-02 原始六例1pass＋5AUTHskip、0fail；五项skip不算通过。有限fixture主31＋额外3、旧R3十项、状态45、日志11种分别按版本/层次保留，不合成官方分数，不代替真实鉴权/生产响应/持久化端到端验收。见 `workflow/boundary-completion-final.md/json`、`workflow/verification/boundary-completion-matrix.md/json`、相关run。
- 首次开发失败构建：`workflow/implementation/development-result.json` 与原 `development-build-01.log` 等记录真实错误；缺当时精确全源预构建指纹，不用后续源清单冒充。正式09/10构建成功仍有基线234 ArkTS/175资源诊断，不能写零告警。
- 旧fixture-matrix脚本漂移：`workflow/implementation/boundary-script-drift-01.md/json`、`traces/boundary-completion/audit/` 保留旧登记4c5f8303…与后02b2797d…时间线、原生FileChange及反向精确还原。可证两说明字符串/AST和原console统计；缺独立完整旧结果JSON副本，不能声称逐字节旧结果一致，旧指纹不重写。
- G1初始环境失败：`service-start-01` / `g1-01` 保留 `fport reverse` exit0但stdout实际失败、无Reverse、无业务请求；之后rport语义校验/设备探针以新run记录。见 `workflow/implementation/boundary-entry-diagnosis-01.md`，不归生产新缺陷。
- G4旧超时断言误匹配Request联系人：旧4pass降为流程证据、未取得真超时；delete2 UI TypeError、日志config缺失故障诊断/09修复及严格六例重测均保留。原错误对象/早期全PID缓冲未保存，不能反推adapter确切缺config形状；见 `boundary-delete-timeout-diagnosis-01.md`、09方案/真实源11场景前失败后通过、`g4-r4`相关证据。
- G5旧09电话过滤：旧BC08 fail、BC09原生过滤skip、10 Normal单行修复/回归保留；见 `boundary-phone-diagnosis-01.md`、09/10原始runs。旧08/09源、HAP、失败日志不被10覆盖。
- 正式10首次运行出现coordinator guard skip的原件仍保留；后正确进程环境重跑得到1pass5AUTHskip，不将首轮重命名为通过。
- 本次Comate索引不存在，旧IDE侧栏映射和桌面产品版本无独立证据，原生加密字段不解密，正式冻结时间/人类修改/完整额外来源/团队source_guard等用户字段仍待补。索引仅证明已存记录的范围和对应关系，不能证明未保存/未来事件。

本页链接按官方成果包布局填写，草案检查通过materials-layout.json映射到当前文件；Root/3-package须在最终包再次核对工程、说明、差异和记录的真实路径。本轮没有上传、打包定版或运行新构建/设备验证；状态写入由Root负责。

## Material layout mapping

Links above target the eventual task root `tasks/cml-spec28/trace-index.md`: `project/` is the frozen full project and `../../traces/cml-spec28/` is the separately copied task trace directory. Draft validation resolves these locations through `materials-layout.json`; no other task is accessed. Late material-event snapshots are in draft-relative `traces/materials-final/manifest.json`, mapped to `../../traces/cml-spec28/materials-final/manifest.json` from the packaged task index. They are capture-time copies outside the frozen project to avoid recursive self-export.
