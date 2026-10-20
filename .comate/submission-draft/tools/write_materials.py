from pathlib import Path
from datetime import datetime,timezone
import collections, hashlib,json,os,subprocess

R=Path(__file__).resolve().parents[3]
O=R/'.comate/submission-draft'
P='tasks/vg-spec1/project/'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(n,s):
    p=O/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n',encoding='utf-8')
def save(n,o):text(n,json.dumps(o,ensure_ascii=False,indent=2))
def main():
    manifest=json.loads((O/'changes/project-manifest.json').read_text(encoding='utf-8'))
    diff=json.loads((O/'audit/diff-validation.json').read_text(encoding='utf-8'))
    sessions=json.loads((O/'traces/sessions.json').read_text(encoding='utf-8'))
    base=manifest['base_commit']; version=manifest['version'];now=datetime.now(timezone.utc).isoformat()
    docs={}
    for name in ['0-analyze.md','1-do.md','2-submit.md','3-package.md']:
        a=R/'spec-harness'/name;b=R.parent/'common/spec-harness'/name
        docs[name]={'project_copy_sha256':sha(a),'common_current_sha256':sha(b),'same':sha(a)==sha(b)}
    top=subprocess.check_output(['git','-C',str(R.parent/'common'),'rev-parse','--show-toplevel']).decode().strip()
    head=subprocess.check_output(['git','-C',str(R.parent/'common'),'rev-parse','HEAD']).decode().strip()
    official={n:sha(Path('D:/SWE-OpenHarmony/templates')/n) for n in ['submission-checklist.md','trace-index.md','submission.json']}
    save('audit/taskbook-versions.json',{'captured_at':now,'common_git_toplevel':top,'common_workspace_commit':head,'note':'common继承上层工作区git；因此同时列四任务书逐文件SHA，不把父仓库提交号当作本题功能提交号。仅核验当前副本，不能重建未留存的历史。','files':docs,'spec_history_exists':(R/'spec/history').exists(),'official_templates_sha256':official,'team_input_sha256':sha(R.parent/'common/spec-harness/team.yaml'),'task_input_sha256':sha(R/'spec/submit-input.yaml')})
    save('submission.json.fragment',{'task_id':'vg-spec1','status':'submitted','project_path':'tasks/vg-spec1/project','build_instructions':'tasks/vg-spec1/build.md','trace_index':'tasks/vg-spec1/trace-index.md'})
    text('solution.fragment.md',f'''# vg-spec1：WebDAV还原确认

本题已完成本地有限计划验收：R01–R28共28条通过，最终采用19项不同计划用例通过，0失败、0跳过。它们不是官方F-point、隐藏测试或官方成绩。依据：`{P}workflow/development-handoff.md`、`{P}workflow/verification/coordinator-final-audit-08.json`、`{P}workflow/requirements/final-coverage-review-07.json`。

设置→WebDAV→从云端恢复入口在校验、下载前显示第一层风险确认，标题“⚠️ 从云端恢复”，正文“本地未同步的学习记录将会丢失”，提供取消和继续。等待、取消、实际边缘手势及框外点击均不进入恢复链；phase/ticket和页面活动状态约束重复交接、旧回调与离页后续跑。继续后沿用基线下载、预览、第二次确认和merge导入语义。6个生产组件均不超过500行，服务、schema、权限及路由未改动。完整改动见 `tasks/vg-spec1/changes/final.diff`。

AI实际参与需求拆解/复审、方案设计、6个生产组件实现、构建、自测、失败分析、测试设施修订和终审；可核对 `{P}workflow/requirements/`、`design/`、`implementation/`、`verification/` 及 `traces/vg-spec1/sessions.json` 中8个开发/分析会话。另5个本次材料会话仅作整理证据。初始化混合总览会话被排除，不作研发证据。模型原生字段为gpt-6.1-sol、effort=xhigh；逐会话版本、工具和token截点值见该JSON，不用重复快照累加。

最终19项来自完整回归13项、继续分支4项、同进程Home温返1项、真实出站隔离1项。完整13项、温返、隔离使用当前HAP SHA256 `a3574072f81f37e14c0f0c1b335673d44e7aa1691c83488a065d4b7c91278a36`。4项继续分支使用旧HAP `435d64b4b825cc85071e60feb617d77f76347973e6ea0570c07c5f22df823954`，旧设备1256×2760；各轮222个生产/构建输入与当前相同，是未变源码回归证据，不声称全19项运行过当前HAP或目标分辨率。额外两项旧补测不重复计数。764条既有ArkTS及原签名警告保留，规范化新增0、缺失0。

真实网络验证采用人工管理员启动的审查后helper，对本题专用模拟器程序副本作动态WFP出站过滤。同NAT路径完成在线GET200/1324字节→过滤中code2300028超时且服务端0到达→三取消→移除后GET200/1324字节。guest仍报告可用/LinkUp，不声称系统LinkDown、离线回调或独立IPv6目标已实测；服务端0到达不等于直接量出应用0请求尝试。清理、过滤器精确NOT_FOUND、helper/controller退出的证据见 `{P}workflow/verification/offline-round-03.json` 及 `tasks/vg-spec1/logs/development-round-02/wfp-offline-round-03/final-audit/audit.json`。

所有失败/重试保留：基线自动同步状态描述纠正、初轮手势坐标及双击预期问题、新实例设施准备失败、Wi-Fi关闭后NAT仍可达、helper05回读失败、06 IPC失败。05缺实际不匹配字段，06缺traceback/filename/winerror，不能反推唯一根因。IME首次声明被Agent误点“同意”的事件已披露；随后停止，用户完成输入法设置后才继续。人工还执行Wi-Fi开关和审查后的管理员启动。入口见 `tasks/vg-spec1/human-changes.md`。这些事实不能反推“无人工直接修改代码”。

未完成项与已知问题（用户声明）：【待补充】。现有证据披露继续后基线Promise.race不取消底层操作的风险；坏密文、空包、预览/导入失败及独立真实120秒超时注入不属于本次承诺计划，未追加通过声明。官方隐藏测试不可见。

团队ID HC2026-111，队名Ghost_London，阶段online；包版本、联系人、成员姓名/分工、团队来源保护声明、成果冻结时间（北京时间）：【待补充】。本题角色约束/路径隔离的实际配置在 `{P}AGENTS.md` 与 `{P}system-config/`；它们不替代用户的来源保护完整性声明。额外来源、人工改码声明和IDE Markdown导出目录仍待用户补充。

本次材料工程快照版本 `{version}`；它是清单摘要，不是新Git提交或团队正式冻结时间。基线 `{base}`。工程交付范围必须遵守 `tasks/vg-spec1/changes/project-manifest.json`：保留源码、spec、hypium_tests、真实过程文件和所有其他已有.comate文件；剔除模拟器运行磁盘/缓存、6个pyc、14份初始化混合会话原文，以及本次submission-draft自身，避免diff递归。排除文件逐项见 `tasks/vg-spec1/audit/excluded-files.json`（3-package须随任务审计材料携带）。该投影已实际应用补丁并全文件比对；不能把它称作未经筛选的本地全目录差异。
''')
    text('sources.fragment.md',f'''# vg-spec1 来源片段

随包基线由 `tasks/vg-spec1/project/spec/metadata.json` 声明：提交 `{base}`，bundle标识 `repo_bundles/vignette-9cbcf7292c-base.bundle`。`{P}workflow/baseline-provenance.json` 保存准备时核对的题包提交 `4ea7779175fc185ed70e8dc515249ec77cd55563` 和bundle SHA256 `c54ce90f52f80624b7d146db2d7c31561d3eeca0d3b1fe337baad423c43f80c2`。本次未重访问题包metadata/specs/bundle或来源项目历史。既有服务、资源、恢复/导入链继承基线；二进制清单 `tasks/vg-spec1/changes/binary-files.json` 按内容摘要标出基线字节同源项，不将它们冒充新增外部素材。

本地prepare记录 `tasks/vg-spec1/logs/prepare-baseline.log` 为profile=harmony-cup-build-v1、dry_run=false、changes=[]；准备完成时间见 `{P}workflow/setup-result.json`。任务书指定的题包 `reports/build-baselines/vg-spec1.log` 不存在；未核对到官方原报告或脚本内容哈希，不能编造脚本精确版本及执行时间。

已登记技术资料及用途如下。这里整理历史记录，不代表本阶段重新联网查证。

| 来源 | 用途与本题证据 |
| --- | --- |
| 本机HarmonyOS API23 SDK声明、ArkTS知识库与Skill资料 | Dialog签名、关闭原因、ArkTS限制；`{P}workflow/design/round-01.md` §7及`{P}system-config/`。 |
| 华为官方ArkUI弹框指南与FAQ | 弹框生命周期与返回手势；同上。部分正文抓取超时，仅用官方搜索摘要辅助，最终签名按SDK与实测。 |
| 华为官方模拟器网络、CLI、屏幕配置、下载页、公开JS及SDK元数据 | 旧版Ethernet行为、替代工具预检；`{P}workflow/design/offline-validation-02.md`、`after-wifi-negative-04.md`，`{P}workflow/implementation/emulator-tool-preflight-02.md`、`public-tool-metadata-03.md`。Emulator26路线未取得可核验下载文件/大小/SHA，不声称下载成功。 |
| Microsoft Learn/WFP、Microsoft维护的通用WinSDK声明 | WFP动态会话、APP_ID/ABI、权限、原生回读及精确清理；`{P}workflow/design/after-wifi-negative-04.md`、`wfp-helper-review-05.md`、`wfp-readback-failure-06.md`。不是本题来源应用的修复代码。 |
| Python/CPython/.NET/Microsoft文件API官方文档和参考源 | 单调时钟、文件共享、异常、IPC重试；`{P}workflow/design/wfp-file-ipc-review-07.md`。 |
| 自研Python Hypium框架、C# WFP辅助工具、合成测试fixture | 工程`test-harness/`、`hypium_tests/`与logs保留实际版本/生成过程；3-package归档共用框架，不把本地工具目录当作可移植构建依赖。 |

精确URL与使用限制保留在表列报告及原生工具记录，不因技能目录内静态链接存在就声称全部已访问。新增二进制主要为本题合成测试快照/截图；其大小SHA逐项列出，具体来源声明仍需结合本题记录及用户extra_sources核对。

用户额外来源完整声明：**【待补充】**（`spec/submit-input.yaml:extra_sources`为空，不得填“无”）。团队来源保护完整声明：**【待补充】**。既有交付报告声明未访问其他题或来源项目相关实现历史；本阶段未把该声明升级为全量原生轨迹的合规审计结论。初始化混合总览不使用、不导出为本题研发记录。
''')
    text('human-changes.md','''# vg-spec1 人工操作与改码索引

人工直接修改代码情况、操作人姓名、修改前后标识及证据：**【待补充】**。题目输入human_edits为空，不能解释成“无人工直接修改代码”。本文件记录已知操作事实，不补造编辑历史。

| 事实 | 原始/当时披露记录（相对本任务目录） |
| --- | --- |
| Agent误点IME首次声明“同意”，随后停止并披露 | `project/workflow/verification/facility-incident-02.md`、`.json`；`logs/development-round-02/ime-preparation-01/root-stop-state/action-disclosure.json` |
| 用户报告输入法设置完成后继续 | `project/workflow/manual-ime-user-completion.json`；相关本题原生主会话 |
| 用户手动关闭/恢复Wi-Fi；NAT仍在线，不能作离线通过 | `logs/development-round-02/manual-offline-round-01/manual-user-action-disconnect*.json`、`manual-user-action-restore.json` |
| 用户启动审查后的管理员helper；05/06失败及最终07均保留 | `project/workflow/network-isolation-user-launch-07.md`；`project/workflow/verification/wfp-attempt-05.json`、`wfp-attempt-06.json`、`offline-round-03.json` |

实际提示、工具操作与返回见最终包根 `traces/vg-spec1/native/`。操作人的身份及其他人工修改完整性由用户补充，不按聊天中“用户”自动推断姓名/成员分工。
''')
    idrows=[]
    for x in sessions['sessions']:
        sid=x['codex_native_session_id'];side=x['codex_sidebar_id']
        idrows.append(f"| `{sid}` | {x['agent']} `{x['agent_path']}` | {'`'+side+'`' if '待补充' not in side else side} | `{x['native_file']}` |")
    text('traces/README.md','''# 本题轨迹读取说明

本目录在3-package移动到包根`traces/vg-spec1/`。`sessions.json`逐会话列真实Codex原生UUID、父子关系、IDE索引映射、模型/effort、最后token累计值、工具计数、源文件与导出文件SHA、截点及删节行；`filtered-session-index.jsonl`仅含本题已有IDE索引行；`native/*.jsonl`是保留原生事件结构的本题副本；`markdown/*.md`是脚本转写的可见消息/工具副本；`code-snapshot/`保留6份当前变更生产组件；`code-edit-index.json`指向原生修改工具行。

导出器是`tools/export_traces.py`（3-package应保留到任务审计工具目录）。它分别按精确工程路径与精确题号边界检索，候选只读首行metadata；仅纳入cwd精确为本题的会话。其他工作区命中仅计数，不导出正文。初始化总览被排除。Comate store不存在，不冒充Comate sessionUuid/IDE双ID；Codex根会话UUID与sidebar字段仅在session_index实际有相同行时建立对应，子会话只凭thread_spawn映射父子关系。

本副本保留可见实际提示、函数调用/工具输出、失败重试、配置和上下文事件；内部模型推理记录未纳入可见材料，逐会话redactions列出源行号/摘要；本次整理中一次宽匹配检索打印的无关命中元数据亦剔除并登记。Markdown不是IDE“导出本地”的原生导出，用户md_export_dir尚为空。历史项目内已有的本题原生阶段快照也保留在project/traces/native，混合初始化原文不随项目投影携带；旧manifest引用这些被排除的初始化文件时以排除清单为准。

导出不包含整个客户端数据库、auth/config秘密文件。JSONL只表示当时截点，活跃会话末尾可能未写完；最终材料/打包操作仍会产生新事件，需3-package最终冻结时更新本阶段相关会话截点，不能声称包含未来消息。源文件未被修改；正文、提示、工具返回不作有利改写。此为离线本题材料草稿，尚未作全量秘密扫描或对外提交。
''')
    fields=[
    ('题目 ID','vg-spec1'),
    ('AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围（每道作答的赛题均须填写）','分析主会话01a148a9…及其需求/基线验证子会话；开发主会话01a148d8…及四角色子会话；需求、方案、编码、构建、自测、失败诊断和终审。完整UUID/事件行见下表、`../../traces/vg-spec1/sessions.json`及`../../traces/vg-spec1/code-edit-index.json`；本次5个材料会话不充当功能开发证据。'),
    ('基线构建准备：脚本配置版本、执行时间及输出记录路径（见 tools/prepare_baseline.py）','`logs/prepare-baseline.log`保存profile=harmony-cup-build-v1、dry_run=false、changes=[]；`project/workflow/setup-result.json`准备完成时间2026-10-17T06:29:31.127547+00:00。这不是脚本起止时间。官方reports/build-baselines/vg-spec1.log缺失；脚本精确内容版本/执行时间【待补充】，不补跑覆盖历史。'),
    ('Agent 名称及版本','Codex Desktop；所有选中原生session_meta.cli_version为0.163.0-alpha.10.2，角色见下表。材料阶段Get-AppxPackage实读Windows OpenAI.Codex安装包版本26.1013.4894.0，证据audit/client-version.json；不推断该GUI版本覆盖全部历史时刻。Harmony角色TOML和Skill按system-config快照SHA标识。本机没有任务书Mac product.json/Comate扩展package.json；相关扩展版本【待补充/不适用】，不把CLI版本当桌面发行号，也不把native source=vscode标签当扩展安装证据。'),
    ('模型名称、版本及运行参数','原生turn_context.model=gpt-6.1-sol、effort=xhigh；模型具体权重版本未输出【待补充】。逐会话token_count.info.total_token_usage最后累计值保存于sessions.json，包含cached_input/output/reasoning计数，非账单、不重复快照求和；未输出的temperature等参数不猜。'),
    ('本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置','`project/system-config/analysis-20261017T072339Z/`、`project/system-config/development-20261017/`，含harmony-task-flow、四角色、ArkTS技能等实际快照；`project/AGENTS.md`本题路径覆盖；原生session_meta.base_instructions及turn_context保存提示，工具逐会话计数见sessions.json。本阶段读取harmony-task-flow及references、四角色配置，只整理材料，实际8项配置快照/版本SHA见`audit/current-config/manifest.json`。`audit/taskbook-versions.json`列当前四任务书/官方模板SHA和common父工作区提交。Comate appliedRuleNames字段不存在【待补充】，不把可用技能目录全当成实际调用清单。'),
    ('运行期间配置变更及原因（无则填“无”）','已有initial/analysis/development快照按阶段保留；工程路径和环境入口由AGENTS覆盖Skill旧示例路径。验证设施逐轮修订、实例/分辨率调整、helper05→06、controller07.1均有workflow报告。本次未改业务/资源/配置/原workflow，只有draft；不能将其填成全程“无”。未留存的配置细节【待补充】。'),
    ('主会话 ID','Codex原生：分析01a148a9-b57c-7b52-9c84-c59330a66ce0；开发01a148d8-5def-7133-8676-f41f3b385ce1；本次材料01a149ca-8abe-77e0-8c8a-d5a67eedee83。三者sidebar同ID对应由filtered-session-index原始行核对。Comate引擎sessionUuid与Comate IDE侧边栏ID均【待补充：本机未找到Comate记录，不能将Codex两个字段冒充映射】。'),
    ('关联会话及子会话 ID','见下表；原生session_meta.source.subagent.thread_spawn.parent_thread_id、agent_role、agent_path给出父子关系。子进程CODEX_SESSION_ID可继承主ID，不能当子原生UUID；已按原生id/CODEX_THREAD_ID核对。'),
    ('解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式','`../../traces/vg-spec1/native/*.jsonl`按行JSON读取；`sessions.json`列哈希/删节/截点；`project/traces/`保留本题阶段证据；`logs/`复制构建、自测、请求及SQLite/Prefs合成快照。完整文件清单见changes/project-manifest.json和audit/log-copy-manifest.json。没有导出整个客户端数据库。'),
    ('失败、重试、未采用的候选方案及选择过程的记录位置','`project/workflow/state.json:failures`、workflow/verification/facility-corrections-01、facility-incident-02、wfp-attempt-05/06、offline-round-03；logs中formal-round-01、manual-full-round-01、manual-offline-round-01、wfp-offline-round-01/02；未取得工具包的Emulator26路线保留。旧失败不改成新通过；05/06原始诊断缺失项保留。'),
    ('实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置','原生JSONL response_item消息与函数调用/返回；code-edit-index按源行定位；当前6组件在code-snapshot；完整差异changes/final.diff；构建自测logs及project/workflow最终报告。'),
    ('导出时间、方法与读取方式',f'本轮生成时刻{now}（UTC，非成果冻结时间）；各会话准确截点见sessions.json.snapshot_at。tools/export_traces.py按工程路径/题号双检索并验证精确cwd，生成JSONL副本和可见Markdown；Markdown不是IDE原生导出，md_export_dir【待补充】。'),
    ('成果冻结时间（北京时间，与 `solution.md` 一致）','【待补充】；团队输入为空，材料采集时间和最终验收完成时间均不代填。'),
    ('官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识',f'基线{base}；HEAD仍为该基线，没有创建功能/提交材料Git提交。最终交付工程投影版本{version}（project-manifest路径+文件SHA的聚合摘要），非新提交；团队版本号【待补充】。'),
    ('基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）','`changes/final.diff`为--binary/--full-index；binary-files.md/.json单列路径、大小SHA及基线同源。涵盖工程投影内新增/修改/删除，含spec、hypium_tests、已有.comate过程文件。84个缓存/模拟器运行文件/混合初始化原文排除项逐项在audit/excluded-files.json，draft自身在工程外归档，不能递归塞回project。'),
    ('与提交源码的对应关系',f'按project-manifest.json的{len(manifest["files"])}文件逐字节复制临时clone、以base checkout，实际git apply --check --binary与git apply --binary退出0；全文件SHA比较0差异、0额外文件、采集期间0源变化。final.diff SHA256 {diff["patch_sha256"]}；详情audit/diff-validation.json。为保留原始CRLF字节未统一换行，apply保留313190行whitespace警告；未改源码。3-package只能按同一manifest复制project，否则本结论失效。'),
    ('人工操作及相关记录位置','`human-changes.md`索引IME误点披露、用户设置完成、Wi-Fi开关、人工管理员启动。对应实际原生提示/返回保留；姓名与完整人工操作补充【待补充】。'),
    ('人工修改索引位置（可使用 `human-changes.md`；无则注明“无人工直接修改代码”）','`human-changes.md`；human_edits为空【待补充】，未写“无人工直接修改代码”。'),
    ('人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置','【待补充】。整体final.diff不能证明每个编辑的人工/AI归属；原生AI改动调用可定位，不推算贡献百分比。'),
    ('公开资料检索与代码复用记录位置，以及 `sources.md` 中的对应来源条目','sources.fragment.md供根sources.md汇总；项目workflow/design/round-01 §7、offline-validation-02、after-wifi-negative-04、wfp-file-ipc-review-07及implementation工具预检列真实URL/限制。用户extra_sources完整声明【待补充】。'),
    ('本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 `solution.md`）','本机工作目录仅作为来源标识：D:/HCUP/vg-spec1（不是构建依赖）；包内工作目录tasks/vg-spec1/project。AGENTS及system-config角色/技能限制访问范围。团队source_guard完整声明【待补充】；不把历史报告声明升级为全轨迹合规审计。'),
    ('脱敏范围（无则填“无”）','导出副本省略不可见内部推理；本次宽匹配检索的外工作区命中元数据剔除，逐会话redactions记源行/摘要；初始化混合会话整文件不导出/不入工程投影。历史本题原生阶段快照仍按原字节保留；源文件未改写。未删失败/未采用方案/来源依据。尚未全量秘密扫描，3-package须最终核对；不提交私钥、auth或整个DB。'),
    ('记录缺失及原因（无则填“无”）','官方基线报告/脚本精确hash及时刻缺失；Comate store/双ID与Mac版本资料缺失（当前是Windows Codex）；Comate扩展版本不可得，历史每一时刻GUI版本未证明，当前Windows安装版本已实读；IDE原生Markdown目录未提供；helper05具体不匹配字段、06 traceback/filename/winerror当时未保存；活跃材料会话仅采集截点、其后尚未发生/未导出事件不在本次快照；初始化总览有意排除。详见sessions.json与pending-fields.md。')]
    lines=['# 运行记录索引','']+[f'- {k}：{v}' for k,v in fields]
    lines+=['','## 本题原生会话表','','| Codex原生UUID | Agent | Codex侧边栏ID（有真实行才填写） | 包根traces/vg-spec1内文件 |','| --- | --- | --- | --- |',*idrows,'','Comate sessionUuid/IDE双ID没有证据时保留待补，不用两份相同Codex UUID冒充。原生source/目标父子关系及tokens详见sessions.json。']
    text('trace-index.md','\n'.join(lines))
    text('pending-fields.md','''# 仍需补充的字段

| 输入 | 未提供字段 | 填写规则 |
| --- | --- | --- |
| common/spec-harness/team.yaml | version、contact、freeze_time（北京时间）、members[].name/work、source_guard | 全部【待补充】；不以材料生成时间代替冻结时间，不自动推断成员/来源保护完整声明。 |
| spec/submit-input.yaml | human_edits、known_issues、extra_sources、md_export_dir | 全部【待补充】；空白不代表无修改/无问题/无额外来源；Markdown转写不冒充IDE导出。 |

以下客观项已经自动查找，现有文件仍不能补齐：Comate sessionUuid/IDE双ID映射（当前实际为Codex）、任务书Mac客户端/Comate扩展版本（当前Windows）、各历史时刻桌面GUI版本、模型未公开的精确权重版本/运行参数、Comate appliedRuleNames、官方基线报告及脚本精确哈希/起止时刻、历史helper05/06缺失诊断字段。当前Windows OpenAI.Codex安装包版本26.1013.4894.0已通过Get-AppxPackage核实，见audit/client-version.json。只能补当时已有真实证据或说明不可得，不补造/不以新日志替代旧记录。

3-package阶段另需填写submitted_tasks、attempted_not_submitted、zip_out；本阶段不选择其他题、不生成团队文件或ZIP。最终冻结时更新本次材料会话截点、核对敏感信息，并按project-manifest复制工程。原manifest引用的14份混合初始化会话已排除，不能把这些引用误报成开发记录缺失。
''')
    text('auto-filled-facts.md',f'''# 已自动填入的事实及出处

| 事实 | 直接出处 |
| --- | --- |
| HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml（输入SHA见audit/taskbook-versions.json） |
| base_commit `{base}` | project/spec/metadata.json；本题HEAD实读；project/workflow/baseline-provenance.json保存准备时来源摘要 |
| 本地准备profile=harmony-cup-build-v1、dry_run=false、changes=[]；准备完成时间 | logs/prepare-baseline.log、project/workflow/setup-result.json；非官方缺失报告替代品 |
| bundleName io.qzz.weiyu、entry/EntryAbility、版本1.0.0 | project/AppScope/app.json5、project/entry/src/main/module.json5 |
| 声明SDK6.0.2(22)、HarmonyOS；Hypium1.0.24/Hamock1.0.0 | project/build-profile.json5、oh-package.json5和锁文件 |
| 构建/安装/启动命令与现有结果 | build.md逐条引用的logs及project脚本 |
| 当前HAP 9121443字节、SHA a3574072f81f37e14c0f0c1b335673d44e7aa1691c83488a065d4b7c91278a36 | 原HAP现存字节；project/workflow/final-validation-fingerprint.json及最终审计/安装manifest |
| 当前222输入一致；28条需求、13+4+1+1用例通过；764既有警告 | project/workflow最终指纹/报告；各run build/exit/hypium/selftest；本阶段只读复核 |
| 旧HAP/分辨率复用边界、真实隔离范围及人工操作 | project/workflow/development-handoff.md、各run原始日志/数据库/报告 |
| 13个本题原生会话；模型gpt-6.1-sol、effort=xhigh、CLI0.163.0-alpha.10.2 | traces/vg-spec1/sessions.json，session_meta/turn_context/token_count/thread_spawn与筛选sidebar原始行 |
| 当前Windows OpenAI.Codex安装包版本26.1013.4894.0 | audit/client-version.json；Get-AppxPackage材料阶段实读，不能倒推全部历史时刻 |
| 工程快照版本 `{version}`、{len(manifest['files'])}文件、diff应用与全字节比对通过 | changes/project-manifest.json、audit/diff-validation.json |
| 二进制路径、字节、SHA及基线同源判定 | changes/binary-files.json/.md；按基线Git blob实际字节SHA比对 |
| common父工作区commit `{head}`，当前四任务书和模板SHA；无spec/history | audit/taskbook-versions.json（目录继承父Git，额外保留逐文件SHA） |

本表未将用户留空字段转为“无”，未推断官方分数或全程无风险。片段及索引采用成果包相对路径；draft在本地是搬运前暂存位置。
''')
    text('delivery-notes.md',f'''# vg-spec1 单题材料交付说明

8类材料已在本目录准备：changes/final.diff、build.md、trace-index.md、sources.fragment.md、solution.fragment.md、submission.json.fragment、traces/、logs/。另附人工操作索引、二进制清单、待补清单、事实出处和audit/工具，以便3-package复核。尚未生成团队级solution/sources/README、system-config汇总、ZIP或对外上传。

差异已在从本题仓库clone的临时目录checkout到`{base}`后，先git apply --check --binary，再实际git apply --binary，均退出0。逐项比对交付清单{len(manifest['files'])}文件SHA，0差异/0额外文件/0采集期间变化。diff为{diff['patch_bytes']}字节，SHA256 `{diff['patch_sha256']}`。保留原始CRLF字节造成apply whitespace警告，原始输出在audit/diff-validation.json，未静默修复内容。

**完整性边界**：本地工程含2GB左右模拟器运行磁盘/缓存及初始化跨题混合会话。官方清单不要求提交运行缓存/无关会话，因此本次明确形成project-manifest交付投影，排除84个此类文件（含6个pyc、14份混合会话原文、64个模拟器运行文件）及本次派生submission-draft目录。所有其余源码、资源、配置、spec、hypium_tests、logs、traces、workflow、system-config、已有其他.comate过程文件都覆盖。没有删除原工程任何文件。**3-package必须按manifest复制project，不能对原目录无过滤递归复制，更不能把含final.diff的draft再嵌入project。** 如果范围改变，必须重新生成并验证diff；不宣称已满足“未经筛选本机目录逐字节全量打包”。

logs为原logs的逐字节副本，排除的只有上述模拟器运行文件/缓存；复制校验见audit/log-copy-manifest.json。所需构建与自测日志齐备，无需为材料再跑构建/设备；官方缺失报告和旧诊断字段不能通过新日志补造。全量日志和原有本题阶段轨迹均保留失败重试。

3-package搬运：build/trace-index/human-changes/changes/logs/pending-fields/auto-filled-facts/delivery-notes/audit/tools放tasks/vg-spec1相应位置；本traces放包根traces/vg-spec1；两个fragment分别汇入根文件，JSON片段合入25题清单；工程仅按project-manifest；validation/为本机临时校验checkout，不进成果包。相对链接在搬运后解释。build.md不依赖本机私有绝对路径；既有自动化脚本含私有路径的限制如实披露。

团队及本题空字段见pending-fields.md。正式成果冻结时间仍【待补充】，当前记录是材料草稿快照。Comate原生资料不存在时已用真实Codex资料说明，未编造双ID/版本。当前活跃材料会话仅采集到traces/sessions.json各自截点，3-package最终冻结时应更新；不得声称当前副本包含未来消息。原生可见副本的内部推理删节、无关检索元数据排除和初始化混合会话排除均有清单；尚未全量敏感信息扫描，本阶段没有对外发送。
''')
    save('audit/submission-state.json',{'task_id':'vg-spec1','phase':'2-submit','status':'draft_prepared_pending_user_fields_and_final_review','created_at':now,'production_changes':False,'original_workflow_unchanged':True,'scope':'materials only; original workflow/state not modified','current_thread_id':os.getenv('CODEX_THREAD_ID'),'sessions':[{k:x.get(k) for k in ['codex_native_session_id','agent','agent_path','parent_thread_id']} for x in sessions['sessions']],'project_version':version,'remaining':['user blank fields','Comate-specific unavailable fields disclosure','final review and snapshot refresh','3-package formal freeze/aggregation only when requested']})
    print(json.dumps({'materials':'written','project_files':len(manifest['files']),'diff_valid':diff['pass'],'sessions':len(sessions['sessions'])}))

if __name__=='__main__':main()
