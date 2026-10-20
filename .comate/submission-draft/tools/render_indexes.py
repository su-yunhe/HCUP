"""Render the official trace-index fields and an explicit evidence/gap ledger."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.comate/submission-draft'
def load(name): return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def save(name,text): (OUT/name).write_text(text.rstrip()+'\n',encoding='utf-8')
def main():
 v=load('changes/validation.json'); inv=load('traces/session-inventory.json'); books=load('taskbook-version.json')
 logs=load('logs-manifest.json'); runtime=load('runtime-evidence.json')
 root_impl='01a14008-ea04-7d02-b1bf-7b5003a14113'
 root_analysis='01a13fe5-b983-72d0-a4e2-a73266edf4d3'
 current=runtime['thread_id']
 values=[
  'vg-spec15',
  'AI 完成本题需求/边界、基线观察、方案、编码、失败诊断、构建和回归。0-analyze 主会话 '+root_analysis+'，1-do 主会话 '+root_impl+'；四角色及原始行号见下表与 traces/session-inventory.json。本轮 '+current+' 仅整理材料。初始化混合会话只作准备证据。',
  '本地 logs/prepare-baseline.log 记录 profile=harmony-cup-build-v1、dry_run=false、changes=[]；workflow/setup-result.json 记录准备结果时间 2026-10-15T14:03:59.549820+00:00（北京时间 2026-10-15 22:03:59）。原调用见初始化原生记录。官方指定 reports/build-baselines/vg-spec15.log 在允许路径不存在；未伪造官方原件。',
  'Codex Desktop；研发原生 session_meta.cli_version 为 0.162.0-alpha.17.2。本轮 Windows 应用包 OpenAI.Codex 26.1007.2314.0，来自 Get-AppxPackage，详见 runtime-evidence.json；不能据此认定历史客户端包版本。角色定义见工程 system-config/，文件摘要随 project manifest 保存；Comate 客户端/扩展版本无对应安装证据。',
  '各原生 turn_context 实测 model=gpt-6.1-sol，effort=xhigh；逐会话取值、最后累计 tokenUsage、工具调用计数见 traces/session-inventory.json。累计样本不重复相加、不当作计费值；活跃材料会话仅为导出时快照。温度等未输出参数：【待补充】。',
  '工程 system-config/initial-20261015T140117Z/ 与 system-config/implementation-20261015/ 保存实际技能、环境与四角色配置；原始系统/开发者提示和派工在 native JSONL 中。实际技能读取与工具序列可按 JSONL 的 function_call/custom_tool_call 重放阅读，计数见 session-inventory。任务书版本另见 taskbook-version.json 及下表；3-package 负责团队 system-config 汇总。',
  '初始化后保存 implementation-20261015 配置快照以对应 1-do 实际使用技能/角色，未覆盖初始版本。完整变更事实以原生记录和两组快照为准；历史客户端设置变化若未输出则【待补充】，不推断为“无”。本轮无业务或工程配置变更。',
  '分析 '+root_analysis+'；实现 '+root_impl+'；材料 '+current+'。这些 ID 在 Codex 原生 session_meta 和侧边栏 session_index 中相同。Comate 引擎 sessionUuid：【待补充】（此运行器不是 Comate，不能伪造映射）。',
  '见下方会话表及 traces/session-inventory.json。Codex 子会话 native UUID 有据可查；子会话未发现独立侧边栏索引行，不宣称有独立 IDE 会话 ID。子角色环境中的 CODEX_SESSION_ID 可能仍为父 ID，采用 session_meta.id/CODEX_THREAD_ID 识别子会话。',
  '包根 traces/vg-spec15/native/*.jsonl、session-index.filtered.jsonl、session-inventory.json、discovery.json、markdown/*.md、code-snapshot/；工程 project/traces/native/ 保留历次原始快照。JSONL 逐行解析；Markdown 是机械转换阅读副本，不是 IDE 导出。只导出本题匹配会话，没有提交整个客户端数据库。',
  '工程 workflow/state.json.failures、workflow/events.jsonl、workflow/design/diagnosis-01.md、workflow/verification/implementation-round-02.md；logs/implementation-build/ 与 logs/implementation-validation/ 的所有历史轮次、原始输出和脚本快照均保留。run06 脚本部分为按原始补丁重建，明确区别于当时保存的原件，不伪称 contemporaneous hash。',
  '实际提示、工具调用和完整返回见上述 native JSONL；检索/代码修改由原生事件关联 traces/code-snapshot 与工程 workflow/implementation/；构建/自测见 logs/。本轮仅材料导出，不能代替研发当时记录。',
  '导出时间逐文件快照见 session-inventory.json、traces/discovery.json；方法为 tools/collect_traces.py 两维搜索后按本题注册或精确 cwd 选取、复制原生 JSONL、筛选索引行并机械生成 Markdown。源/导出 SHA256 与字节数保留。用户 IDE 导出目录 md_export_dir：【待补充】。',
  '【待补充】。common/spec-harness/team.yaml 的 freeze_time 为空；材料生成/验证时间不当作团队成果冻结时间。',
  BASE_LABEL(v),
  'changes/final.diff，大小 '+str(v['diff_bytes'])+' 字节，SHA256 '+v['diff_sha256']+'；包括新增、修改、删除及 spec/、hypium_tests/、workflow/、logs/、traces/、system-config/、.comate 中非材料目录的过程文件。二进制逐项清单 changes/binaries.json，实际资源保留在 project 对应路径。',
  f"changes/project-manifest.json 定义 {v['raw_byte_comparison_files']} 个完整工程文件的原始字节及聚合 SHA256；changes/validation.json 记录本地 baseline clone、checkout、git apply --check --binary、实际 apply 全部 exit 0，所有文件逐字节一致，无额外/缺失文件。复制 project 时必须按 delivery.md 排除生成的 .comate/submission-draft/，其内容单独搬到成果包材料位置，避免自包含 diff 递归。",
  'workflow/state.json.environment_choices 和分析原生会话记载用户选择应用隐私“同意进入”、输入法全模式。其他人工操作完整声明：【待补充】。',
  '【待补充】。spec/submit-input.yaml.human_edits 留空，不能推断“无人工直接修改代码”。如有人工改码，3-package 前补 human-changes.md 及真实历史证据；本轮不创建伪空差异。',
  '操作人、目的、文件、前后版本、当时原始修改证据均【待补充】，以 human_edits 的后续真实声明为准；final.diff 只证明总体变化。',
  'sources.fragment.md 列随包基线、本地官方 SDK 声明、ArkTS 指南、基线 ImportPage 同源用法和依赖锁来源；原始调用位置已列。extra_sources 留空，完整额外来源声明【待补充】。',
  '实际工作目录 D:/HCUP/vg-spec15，工程根就是本题目录。工程 AGENTS.md、两组技能/角色快照及原生派工保存提示与流程约束；没有把提示约束说成技术隔离。团队 source_guard 声明【待补充】。',
  '本轮复制的原生 JSONL、日志、历史工程轨迹均未改写内容；过滤只用于挑选本题会话/索引行，未裁掉失败和重试。原生记录保留历史机器路径和运行器元数据；build.md 无私有绝对路径依赖。测试凭据为受控服务夹具。正式包的账户标识/路径脱敏如需进行，应在 3-package 中登记范围并重新校验，不能隐去来源依据。',
  '见下方缺失说明与 pending-fields.md：Comate 专属 ID/客户端/扩展字段在 Codex 运行器没有等价字段；官方指定基线报告文件缺失但本地准备/构建原始日志存在；用户 IDE Markdown 导出路径未提供；材料会话仍活跃，快照不含其后的工具和最终回复。未声称记录已封口。'
 ]
 template=Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
 lines=template.splitlines()
 lines[2:2]=['路径约定：本草稿中的 `traces/...` 文件统一搬到成果包根 `traces/vg-spec15/...`；工程记录位于 `tasks/vg-spec15/project/...`；本题 logs/、changes/ 与本索引位于 `tasks/vg-spec15/`。会话清单同时给出当前草稿路径与正式包内路径。', '']
 fields=[i for i,s in enumerate(lines) if s.startswith('- ')]
 assert len(fields)==len(values),(len(fields),len(values))
 for i,value in zip(fields,values): lines[i]+=' '+value
 lines += ['', '## 会话及原生字段', '', '| 阶段/角色 | 原生会话 UUID | 侧边栏 ID | 模型 / effort | 最后累计 total_tokens |', '| --- | --- | --- | --- | --- |']
 state=json.loads((ROOT/'workflow/state.json').read_text(encoding='utf-8-sig'))
 roles={x.get('session_id'):x['role']+' / '+x['agent_id'] for x in state['sessions']}
 for row in inv:
  sid=row['native_session_id'];tokens=(row['last_cumulative_token_usage'] or {}).get('total_tokens','【待补充】')
  lines.append('| '+('初始化（仅准备）' if row['setup_only'] else roles.get(sid,'本题材料子会话'))+' | '+sid+' | '+(row['sidebar_thread_id'] or '无独立索引行')+' | '+', '.join(row['model_ids'])+' / '+', '.join(row['effort_values'])+' | '+str(tokens)+' |')
 lines += ['', '## 任务书版本', '', 'common 的当前 Git 仓库根为 '+str(books['repository_root'])+'，当前 HEAD 为 `'+str(books['current_common_repository_head'])+'`。这是材料查询时的版本，不能反推历史运行的 Git HEAD；本题实际使用的四份任务书以保留副本及下列 SHA-256 标识。', '', '| 文件 | common SHA-256 | 本题副本 SHA-256 |', '| --- | --- | --- |']
 for n,item in books['files'].items(): lines.append('| '+n+' | '+item['common_sha256']+' | '+item['task_copy_sha256']+' |')
 lines += ['', '本题 spec/history/：'+('存在，清单见 taskbook-version.json' if books['history_present'] else '不存在，未补造历史任务书。'), '', '## 两维查询与记录缺口', '',
  'traces/discovery.json 记录按工程绝对路径和题号各查一次的结果。另两个匹配文件属于同一全局环境/总览会话，cwd 为 D:/hongmengcup，不属于本题研发，未读取其正文作实现参考，未复制。初始化会话按本题已登记 ID 保留，只作准备来源。', '',
  'Comate 的 sessionUuid/payload.agent/agentInfo/appliedRuleNames 字段不可用；此处据实提供 Codex 原生 session_meta、turn_context、event_msg.token_count 和工具调用。不得把 Codex ID 改称 Comate ID。历史客户端包版本和未输出的运行参数仍待补充。', '',
  '本地日志齐全，无需为了补材料重跑构建或自测。官方 reports/build-baselines/vg-spec15.log 缺失属于历史官方报告缺口，新的运行无法替代原件。材料会话最终封口需由 3-package 在停止相关任务后再次导出并登记，不影响已有 0-analyze / 1-do 的原生证据。']
 save('trace-index.md','\n'.join(lines))
 save('pending-fields.md','''# 仍需用户补充的字段

以下空值均未推测。来源为 common/spec-harness/team.yaml 与本题 spec/submit-input.yaml。

| 文件 | 字段 | 当前产出处理 |
| --- | --- | --- |
| team.yaml | version、contact、freeze_time | 【待补充】；生成时间没有用作冻结时间 |
| team.yaml | members[0].name、members[0].work | 【待补充】 |
| team.yaml | source_guard | 【待补充】；另据记录说明实际提示约束 |
| submit-input.yaml | human_edits | 【待补充】；不推断无人改码；如有需真实证据 |
| submit-input.yaml | known_issues | 【待补充】；已另列日志中的覆盖限制 |
| submit-input.yaml | extra_sources | 【待补充】；已另列可查来源 |
| submit-input.yaml | md_export_dir | 【待补充】；已提供机械生成 Markdown，未冒称 IDE 导出 |

仅 3-package 使用的 submitted_tasks、attempted_not_submitted、zip_out 也未提供，留待该阶段。本题 JSON 片段的 submitted 是供选用的条目，不替代团队的正式提交选题。

客观证据缺口：Comate 专属 sessionUuid 与客户端/扩展版本未在此 Codex 运行器产生；历史客户端包完整版本、OHPM/Hvigor/JBR 独立版本、未输出的模型参数无法核实。适用时提供原始记录；不适用时由团队最终说明运行器差异，不填造假的 Comate 字段。指定官方 baseline log 缺失，已有本题本地 prepare/build 原始日志，不需要重跑去伪装历史原件。

材料会话导出后仍有活动；3-package 正式冻结时需再次导出本轮材料会话并登记封口。原始研发记录已保留。
''')
 save('facts-and-sources.md',f'''# 已自动填入的事实与出处

| 事实 | 值/结论 | 出处 |
| --- | --- | --- |
| 团队 | HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml |
| 题目与基线 | vg-spec15 / {v['base_commit']} | spec/submit-input.yaml、spec/metadata.json |
| 基线准备 | harmony-cup-build-v1，dry_run=false，changes=[] | logs/prepare-baseline.log、workflow/setup-result.json |
| 应用 | io.qzz.weiyu / entry / EntryAbility | AppScope/app.json5、entry/src/main/module.json5 |
| 正式构建 | clean assembleHap 命令，exit 0，759诊断与基线相同 | logs/implementation-validation/build-round-02/、warning-comparison.json |
| 本地自测 | run09 9通过、0失败、0跳过，exit 0 | logs/implementation-validation/selftest-09.json、selftest-09-command.json |
| 已测 HAP | 8978553字节；481c6f4609aee0370e12331e5200f1a1021886f9b8f9dd4e45289944ee6b56fa | build-round-02/artifacts.json |
| 生产指纹 | 511264d4077a8b570329124dd41c36dae2bceea3e9b10ee5a871f2398bb78b6a | workflow/implementation/source-round-02.json；本轮逐文件复核 |
| 完整工程快照 | {v['raw_byte_comparison_files']}文件；{v['project_snapshot_sha256']} | changes/project-manifest.json |
| 完整差异 | {v['diff_bytes']}字节；{v['diff_sha256']} | changes/final.diff、changes/validation.json |
| 可应用性 | check/apply exit 0，全部文件原始字节一致，无额外/缺失 | 本轮临时基线 clone，changes/validation.json |
| 日志复制 | {len(logs)}份，逐文件SHA256 | logs-manifest.json；原工程 logs/ |
| 二进制 | {v['binary_files']}份，含同源基线及新增过程材料 | changes/binaries.json |
| 会话/模型/effort/token/工具 | {len(inv)}会话，gpt-6.1-sol / xhigh；逐会话原生累计值 | traces/session-inventory.json，原生JSONL |
| 客户端 | 本轮Windows包26.1007.2314.0；原生CLI 0.162.0-alpha.17.2 | runtime-evidence.json、session_meta |
| 任务书 | 当前common父仓库HEAD及四份文件双端SHA256，历史目录不存在 | taskbook-version.json；spec-harness/、common/spec-harness/ |
| 已知来源 | 随包基线、本地SDK声明、ArkTS指南、锁文件依赖 | sources.fragment.md与所列原生调用 |

事实与用户声明分别记录；没有用自动核查推定人工修改、额外来源、已知问题或团队成员分工。没有把本地通过换算成官方成绩。
''')
 save('delivery.md',f'''# vg-spec15 材料交付与校验

本阶段只整理 .comate/submission-draft/；未改变业务代码、资源和配置，未提交赛事成果，未生成团队级根文件或ZIP。workflow 中仅追加本阶段会话与调度记录。

完整差异自官方基线 `{v['base_commit']}` 起生成，含过程文件。最终未提交工作树快照 SHA-256 为 `{v['project_snapshot_sha256']}`，HEAD 仍为基线。采用本题 Git 仓库本地克隆后 checkout 到基线，未读取禁止的题包 bundle/修复来源。`git apply --check --binary` 和实际应用均 exit 0，随后 {v['raw_byte_comparison_files']} 文件 SHA-256 逐字节比对全部一致；额外、缺失、哈希不符均为0。具体命令及CRLF/LF处理见 changes/validation.json，临时克隆已清理。二进制逐项列在 changes/binaries.json；没有新增生产二进制素材。

## 3-package 搬运约定

- build.md、trace-index.md、changes/、logs/ 放入 tasks/vg-spec15/；sources.fragment.md、solution.fragment.md、submission.json.fragment 供团队汇总。
- traces/ 放入包根 traces/vg-spec15/，保留原生记录、过滤索引、Markdown及代码快照；taskbook-version.json、runtime-evidence.json、pending-fields.md、facts-and-sources.md、logs-manifest.json、final-checks.json、record-sensitivity-check.json、本交付说明、audits/ 和 tools/ 一并放入 tasks/vg-spec15/ 供索引审计。tools/ 是本轮原工作区材料生成过程的证据，不是正式构建依赖，也不声明可以在搬运后按原路径直接执行。
- project 必须严格按 changes/project-manifest.json 的文件清单复制本工程；总计 {v['raw_byte_comparison_files']} 文件，原始字节聚合 {v['project_snapshot_sha256']}。保留 spec/、hypium_tests/、workflow/、logs/、traces/、system-config/、spec-harness/、test-harness/ 及清单内其他过程文件。
- 排除 build/、oh_modules/、node_modules/、.hvigor/、__pycache__/、.git、环境缓存和 local.properties；排除生成的 .comate/submission-draft/，因为它的内容已被搬到上述材料位置。其他 .comate/ 文件若在manifest内则必须保留。把 final.diff 再复制进其所描述的 project 会导致自包含递归，不能这样打包。
- 若工程内容在本快照后改变，必须重新生成 final.diff 和清单并重做基线应用及全文件比对；不要继续引用本次摘要。团队正式freeze_time、版本和提交选题仍由用户补充，本次没有虚构冻结。
- 正式打包前停止相关工作，重新导出本轮材料会话末尾；本轮快照不包含导出后的事件。保留所有研发失败、重试、run06重建标识和既有配置版本。
- 自测公共工具及cryptography额外依赖由3-package汇总；现有机器路径脚本只是历史证据，便携复用命令见build.md。

## 材料状态

完整工程差异、二进制清单、原生研发轨迹、过滤索引、Markdown阅读副本、代码快照、{len(logs)}份日志和三类汇总片段已产出。缺失用户字段及运行器差异详见 pending-fields.md；不能将这些材料视为已补齐所有人工声明或已正式提交。

日志齐全，不需要补跑构建/自测。指定官方基线报告缺失，但本地原始准备与构建日志存在；新运行不能替代缺失的历史官方报告。
''')

def BASE_LABEL(v):
 return v['base_commit']+'；最终未提交工作树快照 SHA256 '+v['project_snapshot_sha256']+'（HEAD仍为基线，不能单用HEAD表示最终源码）'

if __name__=='__main__': main()
