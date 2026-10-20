# cml-spec7 提交材料需求复审 01

结论：可以继续整理**如实披露的单题材料草案**，不能宣称 `1-do` 全部完成、全部自测通过或本题已正式提交。`spec-harness/2-submit.md:5` 的全完成前置尚未满足：当前有效本地矩阵为 **38 pass、3 blocked（B9/B10/B11）**。本次派工明确保留业务现状，仅做材料整理；因此无需为整理材料重开三方登录实现，也无需用户逐项批准。正式成果包、团队汇总、最终提交题目选择、ZIP、上传和邮件均不在本次范围。

角色：`harmony_requirements`；真实 `CODEX_THREAD_ID=01a1590c-9c06-7340-bb4f-14a58f111ec2`。先读角色定义 `D:/HarmonyDev/codex/agents/harmony_requirements.toml`。本角色只新建本报告，不改业务代码、资源、配置、测试、state 或公共文件，不创建子 Agent，不读取初始化总览会话。

## 1. 本次输入与版本证据

以下为本次实际读取/核验的文件字节 SHA-256。输入批准依据是当前真实文件，不是任务书中的示例目录。`workflow/state.json` 在主调度继续登记时会变化，表中仅为本角色读取阶段的捕获值，不冒称其为最终冻结值。

| 文件 | SHA-256 |
| --- | --- |
| `D:/HarmonyDev/codex/agents/harmony_requirements.toml` | `d2454861149e9914abc16ad5f617c9cd45d8d9f23e6bdea3b527744aa72f2241` |
| `spec-harness/2-submit.md` | `43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9` |
| `workflow/state.json`（读取阶段，20633 bytes） | `1c662e93b6cc29b85afb93ade6fb1553b4dcebec8cd75a9f77a964fe77c6fa77` |
| `spec/submit-input.yaml` | `4bc9652f24a90376c1afdbd6369f213b5c1c9e35600b635cf1819103975fd239` |
| `../common/spec-harness/team.yaml` | `2d426ad41bf48e9ee36a2b69b93e41fcec6c2d5c0cd1ccfe8e7be1264710da39` |
| `D:/SWE-OpenHarmony/templates/submission-checklist.md` | `e724ddbe018f4d5c84946418e9cb365b9e9f99543a179c4a1e04b2e290d6b858` |
| `D:/SWE-OpenHarmony/templates/trace-index.md` | `d6936aef4500d6a19e4289de8e1455b53200f3113d6445f7e80ccb3c42a4c191` |
| `D:/SWE-OpenHarmony/templates/submission.json` | `6d101815a88f6d68c3282f833f72d208f0084341c4af8faee9a54994c92c5efd` |
| `spec/metadata.json` | `cf5f402ae5042331bf332c4173a3b26ddb3c2494cee9976bd2b39106ca0e5a88` |
| `workflow/delivery-01.md` | `47cd490fbe8363a15b759d91f8e7a5587e5676ad86d0fca528b58083276cf94e` |
| `workflow/verification/final-verification-03.md` | `b9c02a4cb8f9f911238e227623aba81c12026097fa179c011da8b19b9e0f1d4e` |

`git -C ../common rev-parse --show-toplevel` 返回 `D:/HCUP`，该目录并非独立的 common 仓库；`git -C ../common rev-parse HEAD` 实际返回父工作区提交 `e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac`。据实记录这一点，并补四份任务书内容哈希，避免把父仓库 HEAD 当作已证明的四文件最终内容：

| `../common/spec-harness/` 文件 | SHA-256 |
| --- | --- |
| `0-analyze.md` | `a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a` |
| `1-do.md` | `2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d` |
| `2-submit.md` | `43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9` |
| `3-package.md` | `3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c` |

允许的官方基线准备日志 `D:/SWE-OpenHarmony/reports/build-baselines/cml-spec7.log` 当前不存在；`spec/history/` 当前不存在。这里只检查指定路径，没有扩大到题包其他目录搜寻。已有 `workflow/baseline-provenance.json` 可以证明本地基线登记，不能充当缺失的官方准备脚本原始日志。

## 2. 编号验收清单

位置简称：`S`=`spec-harness/2-submit.md`；`C`=官方 `submission-checklist.md`；`T`=官方 `trace-index.md`；`J`=官方 `submission.json`。以下“待核验”表示材料实现/独立验证角色仍须提供结果，本报告没有代为通过。

| ID | 前置与操作 | 可观察结果及边界 | 原文位置 | 本次结论 |
| --- | --- | --- | --- | --- |
| S01 | 整理前核对 `1-do` 与当前有效回归 | 如实写38 pass/3 blocked；不标全完成；不把阻断改成pass或删除原需求 | S:5；S:65、91；C:14、29 | 全完成前置未满足；授权范围内可整理草案 |
| S02 | 固定材料阶段范围 | 只产出本题草案/汇总片段；业务、资源、配置和测试不变；无团队级新文件、ZIP、外部提交 | S:3、7、9–10、57 | root 应比较阶段前后指纹；本角色只写本报告 |
| S03 | 取真实输入 | 按本题 metadata、git、配置、日志、原生会话自动取事实；空输入字段全部保留 `【待补充】` | S:31–53、76 | 本报告列明已知事实/空字段；禁止推测 |
| S04 | 建立最终交付文件清单后生成完整 diff | 从 metadata 基线到最终工程的新增/修改/删除全覆盖，含 spec、测试、过程文件；二进制用 `--binary`；不只覆盖14个业务变更文件 | S:61、77–81；C:10、12、37、60 | 待材料生成与独立复核 |
| S05 | 从本题本地 git 基线建立临时校验目录 | checkout `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；`git apply --check --binary` 成功；实际 apply 后逐文件比较交付清单的路径、内容哈希与删除项 | S:80–81；C:60、65 | 待独立验证；仅diff语法检查不够 |
| S06 | 生成前检查构建噪声；筛选缓存 | tracked BuildProfile 等已还原；只排除缓存/生成噪声和材料输出，不漏真实工程/原始证据；排除清单与工程、diff一致 | S:78–83；C:35、37 | 既有收尾计数0；材料阶段须再核验，见第4节 |
| S07 | 按交付清单单列二进制资源 | 每项有包内相对路径、bytes、SHA-256、来源；保留实际资源；基线自带复用明确同源 | S:82；C:12 | 待生成清单；SVG文字文件仍需正确纳入diff |
| S08 | 编写 `build.md` | 依赖安装、构建、安装、启动、bundleName、Ability、必要初始化齐全；命令可在交付工程根复现；没有参赛机私有绝对路径或未提交脚本依赖 | S:45–46、62；C:11 | 待校验；开发日志可以保留原路径，build指南须便携 |
| S09 | 逐字段填官方 trace-index | 保留T:3–26的全部字段；每个值有来源；缺失写 `【待补充】` 并解释，不能删字段或填示例值 | S:63、76；T:3–26 | 待逐字段复核 |
| S10 | 建立本题会话选择清单 | 工程绝对路径与题号两个维度交叉核对；包含主/子会话、失败、重试、未采用方案；排除初始化总览与无关会话；不打包整个客户端DB | S:47、67、84–87；C:14、31、35 | 既有本题10会话快照可读；当前材料会话须补入，不读取被排除会话 |
| S11 | 导出轨迹与索引 | 原生JSONL可独立读取，有源哈希、导出时刻、截止事件/ordinal、原始工具调用及结果；过滤索引和Markdown标明由原生记录生成，不能冒充原生或IDE导出 | S:67；T:12–15；C:14、35 | 待本次导出；已有快照不含其后的事件 |
| S12 | 记录实际会话ID体系 | Comate不存在则明确不适用，不造 `sessionUuid`；Codex线程ID、原生记录ID、父子关联据真实字段并解释对应关系；无法核实的独立IDE ID留待补充 | S:86；T:10–11；C:14 | 字段映射见第5节 |
| S13 | 保留失败与重试 | 手机原轮测试error、方向复位导致800vp轮、旧布局/导航故障、无效02b、初次日志缺口、清理拒绝等保留原记录并标有效范围；不把旧失败当当前pass | S:87、91；C:14、62 | 有现成证据；待确认草案拷贝无漏项 |
| S14 | 记模型/工具/配置与任务书版本 | 模型、effort、token计量、Agent/客户端版本有原生字段；规则/Skill由实际提示和调用证明；实际任务书版本/历史有声明 | S:48–52、88–89；T:6–9 | 可据Codex原生映射，不用Comate字段名硬填；四任务书hash已取 |
| S15 | 提供 `sources.fragment.md` | 本题随包基线、额外检索/SDK等已观察事实及索引齐全；人工空白声明仍待补充；不替用户宣称“无额外来源/无违规访问” | S:64、91；C:16、35 | 本题来源记录可引用；输入 extra_sources 为空 |
| S16 | 提供 `solution.fragment.md` | 完成范围、B9–B11未完成、已知限制、AI环节/事件范围和缺失如实披露；本地条目数不当作官方F-point/分数 | S:65、91、97–104；C:13–16、43–49 | 38/3必须可见；原需求和矩阵不降级 |
| S17 | 提供本题 JSON 片段 | 只保留cml-spec7单条；三个路径用 `/` 的包内相对路径，后两项是文件；与3-package最终目录一致；不把官方模板全部其他题拷入本题 | S:66、90；J:51–55；C:9、59 | 3-package题目选择尚未给出；见第6节 |
| S18 | 复制本题logs | 保留实际原始stdout/stderr、JSON、截图、测试代码归档与失效说明；缓存大磁盘按排除清单处理；缺失说明原命令及后补边界 | S:53、68；T:14、26；C:14、49 | 官方准备日志缺失不能靠现在重跑伪造补齐 |
| S19 | 人工操作与改码说明 | human_edits为空则待补充；有人工改码时须给人、原因、文件、前后版本与当时原始证据；总体diff不能代替人工证据 | S:36、91；T:20–22；C:15、20–25 | 不能自动填写“无人工直接修改代码” |
| S20 | 记录缺失、脱敏与导出边界 | 实际列明缺失/原因及脱敏字段；保留代码来源与修改依据；不提交密钥、签名私钥、无关账号/私人会话或仍写入的DB临时文件 | S:91；T:25–26；C:35、43–49 | 待独立检查；缺失不直接等于违规或合格 |
| S21 | 输出两张交接清单 | 单独列“仍需人工补充的字段”与“自动填入事实及出处”；空字段不能变成默认无 | S:70、76 | 本报告第6/7节给出输入，最终草案仍须带此清单 |
| S22 | 冻结与交付校验 | 最终工程、diff、源码快照、测试报告和原始轨迹属于同一声明版本；正式冻结时间来自人工team输入；材料快照时间不能替代它 | T:15–19；C:53、60–62 | 当前freeze_time空；本阶段只有草案切片，不标正式冻结 |

## 3. 1-do 前置冲突与披露文字

直接证据：

- `spec/requirement.md:21` 要求第三方账号快速登录，`:28` 要求微信图标触发微信登录流程；批准验收矩阵 `spec/acceptance.md:80–82` 保留B9/B10/B11，`:133–135` 明确真实流程不可用不得标通过。
- `workflow/verification/final-verification-03.md:3` 写38 pass/3 blocked，`:15–25` 区分原始case与合并矩阵，并保留测试错误和补测；`:66–68` 三项明确blocked。
- `workflow/delivery-01.md:3`、`:50–56` 明确未全完成、用户无账号、无真实授权SDK集成/配置、不冒称官方分数。`workflow/implementation/third-party-setup.md:3、10` 明确只有缺配置反馈，没有真实授权流程。
- 本次读取的 `workflow/state.json:483–505` 记pass=38、`approved_for=local partial delivery with external B9-B11 blockers`、`full_feature_validation_complete=false`。

推荐在 solution片段、build运行限制和trace缺口处保留如下同义事实：

> 本题当前为本地部分完成交付：41项明文原子验收中38项pass，B9/B10/B11因缺少合法第三方应用注册、签名/回调及服务端凭据交换条件而blocked，尚未实现真实微信、QQ、支付宝授权登录流程。现有不可用反馈与恢复不计三项通过。构建、安装、冷启动及已实现范围适用回归通过；该计数不是官方F-point数量或官方成绩。本阶段仅整理材料草案，未正式提交。

这不是放宽Spec：原需求、U2和三项blocked继续有效。既有需求/设计/测试不因进入材料阶段而失效；材料只能新增追溯、交付范围和缺失说明。若后来取得合法接入条件，才由root另行回到方案/实现/真实平台回归，再更新B9–B11及最终源码/HAP/测试指纹。本阶段不得为了满足前置而改测例、改业务或把`blocked`改成`pass`。

## 4. final.diff 自包含递归、工程清单与缓存

**明确要求**：S:77–81的完整范围包含随工程交付的过程文件；C:37同时明确缓存、旧ZIP和无关工程不放成果包。没有理由将全部 `.comate/`、`spec/`、`hypium_tests/` 或 `workflow/` 一刀切排除。

**可据文本与文件关系解决的工程解释**：先定义一个可审计的“成果包 `project/` 文件清单P”，再让diff精确重建P。`.comate/submission-draft/` 是本阶段输出暂存区，内容由3-package映射到 `tasks/cml-spec7/` 的材料位置；不再把它整体嵌套复制进 `project/`。P与diff均排除这个输出目录，其余真实 `.comate/` 文件仍按是否随工程交付决定并写清单。否则 `final.diff` 包含自身、草案副本的diff又包含副本，无法得到有限且一致的最终快照。该解释须写入交付说明/范围清单，不可默默排除过程材料。

建议root和材料/验证角色按以下顺序操作：

1. 固定P的纳入/排除规则与最终路径映射，输出清单、bytes和SHA-256到草案目录；清单自身和校验临时目录位于P之外，避免摘要包含自身。
2. 纳入基线源码、全部真实新增/修改/删除、测试、Spec、输入副本、本题workflow和有效原始证据；使用能收录未跟踪文件的临时索引/快照方式生成diff。当前 `git status` 有多类未跟踪目录，普通 `git diff <base>` 会漏掉它们。
3. 精确排除 `.git/`、本阶段草案输出、已识别的依赖/编译/语言缓存、旧包和任务模拟器生成磁盘；逐路径记录排除原因。不要按 `logs/**`、`traces/**` 或二进制扩展名整体排除，真实截图/JSONL/构建输出也是证据。
4. `logs/verification-emulator/instances/CmlSpec7_Layout` 的 `cache.img`、`cache.img.qcow2`、`sys_prod.img.qcow2`、`system.img.qcow2`、`userdata.img.qcow2`、`vendor.img.qcow2` 已在 `logs/verification-closeout-03/temporary-disk-cleanup-rejected.json` 登记为生成磁盘；从交付清单排除这些缓存副本即可。原磁盘仍保留，不再次删除、不绕过先前自动审批拒绝。保留closeout/拒绝JSON、命令及必要小配置，完整说明测试环境。
5. 将本题原生轨迹按导出截止事件做一次只读切片；不使“记录当前材料导出”反复嵌入同一被重算的工程快照。明确当前切片未包含未来事件，后续材料/打包活动由3-package继续收录，不能在当前阶段宣称已覆盖未来。
6. 从本题本地基线clone/check out后 `git apply --check --binary`，再真实apply；比较P每项路径和SHA以及删除项，不仅比较14个业务文件。核对diff无交付范围外噪声、工程无diff遗漏文件，记录命令、退出码、清单版本和结果。

这是建议的可实施范围约定，不是已执行的patch验证结论。本角色没有生成/应用补丁，也没有删除缓存。若材料实现已经采用别的有限快照结构，仍须证明`project/`与diff逐文件一致并披露自身输出的定位。

## 5. Comate缺失时的Codex字段映射

主调度已告知Comate路径不存在，实际研发工具为Codex。官方C:14接受JSON/JSONL等原生记录或等效完整记录，因此不需要伪造Comate数据库。S:86的“双ID”字段仍应出现，但其中不存在的Comate `sessionUuid` 明确写“不适用：实际使用Codex”；独立IDE侧边栏ID如无可读证据，写 `【待补充：未核实独立IDE ID】`，不能凭空复制一个ID并说已证明两者对应。

已核查的本题原生示例：

- 主会话R：`traces/native/20261020T112004Z-01dcd6ae/2026/10/20/rollout-2026-10-20T18-16-45-01a158d0-416c-75a3-8836-233f0c35fb6f.jsonl`。
- 验证子会话V：同目录 `rollout-2026-10-20T18-19-52-01a158d3-1977-7490-b337-d28df9f59e73.jsonl`。
- 该快照的 `manifest.json` 登记10个专属会话、原路径、导出副本、bytes和SHA，`gaps=[]`，排除初始化总览ID `01a13fc4-2611-7761-a580-1283e0c70541`；`snapshot_only=true`、`includes_future_events=false`。这些仅证明该时刻切片，不证明后来材料会话已导出。

| 所需信息 | Codex真实位置/建议规则 | 已核实示例与限制 |
| --- | --- | --- |
| 本题原生线程ID | `session_meta.payload.id`，再与环境 `CODEX_THREAD_ID`、登记表和文件名交叉核对 | R:1为`01a158d0-...`；V:1的id为`01a158d3-...`。**V的`payload.session_id`却是父会话`01a158d0-...`，不能拿它当子线程自身ID。** |
| 父子关系/角色 | `session_meta.payload.source.subagent.thread_spawn.parent_thread_id`、`agent_path`、`agent_role`；可与顶层payload角色及workflow登记交叉核对 | V:1给父`01a158d0-...`、`/root/verification_do`、`harmony_verification`；昵称不是版本号 |
| Agent/运行时版本 | `session_meta.payload.originator`、`cli_version`、`model_provider`；专用角色提示另引实际文件及hash | R:1为`Codex Desktop`、`0.163.0-alpha.10.2`、`openai`；CLI版本不能冒称桌面App或Comate扩展版本 |
| 模型与effort | 逐条 `turn_context.payload.model`、`effort`，发生变更按事件范围登记 | R:10（ordinal9）为`gpt-6.1-sol`、`xhigh`；不推断不可见模型内部版本，不假定所有会话参数相同 |
| token用量 | `token_usage_record.payload.usage`、`turn_token_usage`、`thread_token_usage`；或`event_msg`/`token_count`中`info.total_token_usage`，写清计量方法与截止事件 | R:20有`thread_id/turn_id/session_id/root_turn_id/response_id`；R:1826为最后可见token_count。累计计数不可逐行求和；多个历史快照不可重复累计；缓存输入是input子项，不额外再加一次。缺失/分叉继承按原口径披露 |
| 实际提示/工具/结果/修改 | 保留完整JSONL的`response_item`、调用/返回、`event_msg`、`inter_agent_communication_metadata`等；派生索引定位原始行/ordinal | 不把`compacted`摘要单独当完整工具证据，也不把Markdown重建副本称原生记录 |
| 生效规则/Skill | 实际提示、工具read调用及返回、角色定义/Skill副本或配置快照和hash | 不能将Comate `appliedRuleNames` 强行映射为虚构字段；“文件存在”不等于曾使用 |
| 导出与对应关系 | 清单记录源线程、可读原生副本、hash、bytes、源末事件/ordinal、导出时刻、过滤规则；本题工程路径和task_id双维度核对 | 禁止读取/导出初始化总览；不复制整个Codex用户DB或无关会话 |

Markdown副本可以自动由JSONL重建，以便阅读；必须注明生成方法、对应原生文件和记录截止位置。`md_export_dir`空白只说明没有提供IDE手工导出路径，不妨碍真实自动副本生成，也不能据此编造一个手工导出目录。

## 6. 仍需人工补充的字段及非人工可解决缺口

**人工输入当前为空，必须保留`【待补充】`：**

| 字段 | 原文位置 | 可继续自动做的工作 |
| --- | --- | --- |
| `human_edits` | `spec/submit-input.yaml:5` | 导出已有AI/人工提示记录，但不能代填“无人工直接修改代码” |
| `known_issues` | 同文件:6 | 自动披露已核实B9–B11与已知测试限制；并注明人工补充仍未提供，不写“无” |
| `extra_sources` | 同文件:7 | 汇总本题已有来源/检索/SDK记录，不能代替人工来源声明或写“无” |
| `md_export_dir` | 同文件:8 | 自动生成可读副本并说明来源，不冒充IDE侧边栏导出 |
| `version`、`contact`、`freeze_time` | `../common/spec-harness/team.yaml:7–9` | 只生成草案；不得用材料生成时间/验证时间代填正式冻结时间 |
| `members[0].name`、`members[0].work` | 同文件:10–12 | AI角色分工可据会话填；真实成员姓名/人工分工不能从本机用户名推断 |
| `source_guard` | 同文件:13 | 可记录实际AGENTS/角色访问约束和工具行为；人工声明仍待补充，不因空白自动写“未配置” |

`team_id=HC2026-111`、`team_name=Ghost_London`、`stage=online`、`task_id=cml-spec7`已提供，可直接使用。`submitted_tasks=[]`、`attempted_not_submitted=[]`、`zip_out=""`（team:15–18）属于3-package，当前不能据空数组推断最终提交选择；无需为继续整理草案提问。

JSON片段建议保留官方本题条目的`status=not_completed`作为当前草案默认，并明确“最终submitted状态由3-package根据真实提交选择统一设置”；本报告不把“未全通过”解释为规则禁止提交该题。若root制作拟提交版本片段，可写真实包内路径 `tasks/cml-spec7/project/`、`tasks/cml-spec7/build.md`、`tasks/cml-spec7/trace-index.md`，并在旁证中标拟定映射/尚未打包，不能把拟定路径说成已存在于正式ZIP。无论最终是否提交评分，已发生的本题研发记录必须保留（C:29）。

**无须问用户、应由材料/验证角色处理的缺口：**

- 官方基线准备日志缺失：在trace索引写指定路径不存在，引用本地真实基线准备/分析日志作为不同证据。现在重跑最多产生新的可复现实验，不能补成原始准备记录。
- 初始化阶段原始hdc stdout捕获缺口：按state和分析报告保留当时工具原生结果、标注的转录及后来完整结果；不能称原记录已完整补回。
- 当前材料会话及子会话尚需新快照、双维度选择核对、原生/派生索引、读取说明、导出截止和脱敏说明；root正在做这些，不要求本角色越权读用户全局会话库。
- 独立IDE ID、桌面App版本等若无证据，明确未核实；可以继续整理，不需为了填满字段猜测。
- 完整diff、二进制清单、排除清单、临时clone/apply及逐文件哈希复核待材料/验证角色执行。本角色未把它们记pass。

## 7. 可自动填入的事实与出处

| 事实 | 可用出处与边界 |
| --- | --- |
| 官方基线 `75fd0066a7fc0c1e8cedb6218df081f86d307f45` | `spec/metadata.json:2`；本地基线登记见`workflow/baseline-provenance.json` |
| 本地38 pass/3 blocked；非官方成绩 | `workflow/verification/final-verification-03.md:3、11、66–68`，`logs/verification-final-03.json`，`workflow/delivery-01.md:3、56` |
| 有效源码聚合SHA `26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e` | 最终验证报告:7；聚合范围为完整生产输入，不能混同14变更文件聚合 |
| 最终验证HAP SHA `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863` | 最终验证报告:7，交接:13–16；是否随project交付另按P清单决定 |
| 已修复布局/导航及测试助手错误均有原始失败与新回归 | 最终验证报告:23–25、89–95，交接:24–32、54；不删除旧轮、不拿失效轮证明当前源码 |
| 三方授权条件缺失，无真实SDK接入/配置 | `workflow/implementation/third-party-setup.md:3–10`、交接:50；不把SDK下载当已接入 |
| 临时生成磁盘未删除、清理被自动审批拒绝 | `logs/verification-closeout-03/temporary-disk-cleanup-rejected.json`；只建议交付排除，不改变原目录 |
| 原生专属会话、排除ID及快照范围 | `traces/native/20261020T112004Z-01dcd6ae/manifest.json`；只覆盖该时刻 |
| 实际Codex模型/effort与运行时CLI版本示例 | 第5节R:1、10；逐会话填真实参数，不外推未读值 |
| 当前任务书版本与输入空字段 | 第1节hash、`spec/submit-input.yaml:4–8`、team:4–18 |

## 8. 交还主调度的下一步

1. 接纳本报告为材料阶段需求依据，同时保持原功能验收/业务冻结与38/3结论；更新state时不要把当前partial误写complete。
2. 材料角色按P清单完成8类指定产物，并在trace-index/solution片段写入前置不满足、Comate不适用、人工空字段、原始缺口、有效/失效轮次及自身输出排除说明。
3. 验证角色独立核对P与完整diff的双向一致性、基线apply、真实二进制摘要、便携build说明、官方trace字段、会话范围与JSON路径；不要修改业务/测试或为材料阶段重跑B9–B11。
4. 本阶段最终交接清楚区分“已完成的材料整理”和“尚缺人工声明/外部条件/后续正式打包”，列出两份清单；无需用户逐项批准即可完成当前可执行工作。

真实未消除项是人工声明、正式提交选择/冻结时间、缺失原始日志/独立ID与外部授权条件；这些不能由需求解释或材料排版制造出来。工程路径错位、Codex字段映射、diff递归及缓存排除均可依据现有证据处理，不构成需要先问用户才能继续的歧义。
