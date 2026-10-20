"""Render official trace fields using collected facts, without inventing metadata."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'

def main():
    facts = json.loads((OUT / 'evidence-facts.json').read_text(encoding='utf-8'))
    templates = Path('D:/SWE-OpenHarmony/templates')
    (OUT / 'templates').mkdir(exist_ok=True)
    for name in ('submission-checklist.md', 'trace-index.md', 'submission.json'):
        shutil.copy2(templates / name, OUT / 'templates' / name)
    used = [('D:/HarmonyDev/codex/skills/harmony-task-flow/SKILL.md', 'harmony-task-flow/SKILL.md')]
    used += [(f'D:/HarmonyDev/codex/skills/harmony-task-flow/references/{n}.md', f'harmony-task-flow/references/{n}.md') for n in ('local-setup', 'protocol', 'traces')]
    used += [(f'D:/HarmonyDev/codex/agents/{n}.toml', f'agents/{n}.toml') for n in ('harmony_requirements', 'harmony_design', 'harmony_implementation', 'harmony_verification')]
    used += [(str(ROOT / 'AGENTS.md'), 'AGENTS.md')]
    configs = []
    for src, rel in used:
        p = Path(src); dest = OUT / 'traces/config-used' / rel
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, dest)
        configs.append({'source': src, 'copy': dest.relative_to(OUT).as_posix(), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest()})
    (OUT / 'traces/config-used/manifest.json').write_text(json.dumps({'scope': 'Actual 2-submit workflow skill, references and four configured roles; existing development snapshots remain in project/system-config', 'files': configs}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    fields = [x[2:] for x in (templates / 'trace-index.md').read_text(encoding='utf-8').splitlines() if x.startswith('- ')]
    values = [
        '`cml-spec17`。',
        '需求拆解、方案设计、原业务实现/修复、隔离测试及失败复审、当前材料整理；主子会话逐项见下表与 `traces/export-manifest.json`。0-analyze、1-do 的原始事件、失败和未采用方案保留；初始化跨题总览不作为功能开发证据。',
        '`project/logs/prepare-baseline.log` 的 profile=`harmony-cup-build-v1`、changes=[]；执行时间见 `project/workflow/setup-result.json` 的 prepared_at=2026-10-19T07:45:09.347162+00:00，本地构建记录 `project/logs/baseline-build.log`。官方指定 `../../SWE-OpenHarmony/reports/build-baselines/cml-spec17.log` 当前不存在，记录为缺失，不能以本地日志冒充官方报告。',
        'Codex Desktop `26.1013.4894.0`（`traces/client-version.json` 的 Windows AppxPackage）；Codex CLI `0.163.0-alpha.10.2`（原生 session_meta.cli_version）。四个角色的实际 TOML 及 SHA 见 `traces/config-used/manifest.json`；原生记录不另报角色程序版本。Comate 客户端/扩展本题未使用，其 macOS product 路径不存在，不填伪版本。',
        '每会话的模型 ID、effort、最后 token_count 原值见下表与 `evidence-facts.json:native_sessions[].contexts/last_reported_token_info`。模型权重修订/独立 agentInfo/计费总量在原生中未输出：【待补充】（若赛事要求）。不把可见累计计数相加当计费用量。',
        '开发阶段实际快照为 `project/system-config/analysis-20261019T080858Z/`、`project/system-config/do-20261019T131600Z/`；本轮实际加载的 harmony-task-flow、引用、四角色与 AGENTS 在 `traces/config-used/`。原始系统/开发提示在原生 JSONL；实际工具调用名及次数见 `evidence-facts.json:native_sessions[].tool_counts`，不是可用工具列表。',
        '原记录按 analysis 与 do 分版本保存，配置和原因参见 `project/workflow/state.json:config_snapshots_used`、`project/workflow/events.jsonl` 与各快照 manifest。本轮仅材料整理，新采集脚本位于 `tools/`，未改生产配置。公共路径由本题 AGENTS 覆盖 skill 示例路径。',
        '分析主会话 `01a15320-35c3-7341-a387-a8c8cec04015`；实施主会话 `01a15412-7c11-7292-b4ef-1b7d894060a9`；材料主会话 `01a15490-1423-7570-9c1c-98d9a6af515d`。各原生 ID 与过滤索引中对应侧边栏 ID 相等，见下表。',
        '全部相关子会话、角色、父ID、可核实的侧边栏ID见下表及 `traces/export-manifest.json`。子 Agent 没有独立侧边栏行时明确记为未暴露，引用其真实父会话，不能用继承的环境变量冒充子 UUID。',
        '直接读取 UTF-8 JSONL：`traces/native/`；过滤索引 `traces/session-index.filtered.jsonl`；历史原生快照和其他 UI/HTTP/DB/命令证据保留于 `project/traces/`。派生 `traces/markdown/` 按原生行完整显示，用于阅读，不替代 JSONL。会话状态/事件仅为索引。',
        '`project/logs/implementation-build-01.log`、02、03 的真实构建失败与04成功；`project/workflow/verification/do-results-02.md`、`project/logs/do-03/selftest-20261019-212521.json` 的E03/D02失败，fix-02和do-04复验；分析入口失败及重试保留于 `project/logs/local-entry-01/`、`project/traces/local-entry-01/`。原生失败关键词行号仅为检索提示，见 export-manifest，不等同人工判定失败。',
        '提示、工具调用及返回保留于每份原生 JSONL。本题改动快照 `traces/code-snapshots/`；总体交付差异 `changes/final.diff`；构建/自测 `logs/` 与 `project/workflow/verification/do-results-03.md/.json`。原始旧快照、失败截图（包括明确零字节无效截图）和旧HAP保持历史。',
        '`evidence-facts.json:checked_at_utc` 为实际本轮导出时间，使用 `python -B tools/collect_evidence.py` 从原生库按本题路径、题号两维检索并集，复制所选相关完整行。各文件 SHA、源读取字节数/摘要、截尾字节和最后完整事件UTC/北京时间见 export-manifest。当前主会话和活跃子会话均为截至采集时的快照，不含导出后的事件，正式3-package需重新采集。',
        '【待补充】；`../common/spec-harness/team.yaml:freeze_time` 为空。本轮采集/工程快照时间不是团队正式成果冻结时间。',
        '官方 metadata.base_commit=`d6a6ba7480fbd0a30075462e46bb4344a430ba61`；最终本地工程版本为 `changes/project-files.json:version_identifier` 的真实 git-tree OID，工作树未提交，不能把未变化的HEAD当最终版本。生产聚合 SHA256=`2278a77074b39f8d97067beb853d7880bb91d3586dbf228992ffba2d9ccb03b5`。',
        '`changes/final.diff`（`--binary --full-index`）；完整文件集合、大小、SHA256和删除清单 `changes/project-files.json`；二进制逐项 `changes/binary-files.json/.csv`，基线同源文件由blob精确比较列路径；排除清单 `changes/excluded-files.json`，目录边界盘点 `changes/ignore-boundary-audit.json`。',
        '`changes/validation.json` 记录实际本题基线 clone/checkout/git apply --check --binary/应用结果，逐文件全集比对 patch回放、manifest及当前工程；独立复核 `verification/independent-replay.json`、`verification/final-audit.json`。第3阶段必须仅按 project-files.json 清单复制 project/ 且复核摘要，不递归复制材料输出D。',
        '已知用户提示/决策保留于三个主会话；包括无账号调查、允许增本地入口、仅本题模拟器同意输入法基本模式等。实际操作执行者和证据在 `project/workflow/state.json:resolved_questions`、原生工具调用中；不得把Agent工具点击当人工直接改代码。人工成员分工仍【待补充】。',
        '`human-changes.md`；`spec/submit-input.yaml:human_edits` 为空，因此人工直接改码声明【待补充】，不能擅写“无人工直接修改代码”。',
        '【待补充】；若有人工修改，应提供操作人、目的、文件、修改前后标识、差异及当时原始证据。总体 final.diff 不能替代这些证据。',
        '`sources.fragment.md`；官方随包基线声明引 metadata 与 baseline-provenance。本题额外来源用户声明为空【待补充】，已知工具/Skill和代码内依赖在事实表列出，不能从未发现推断完全无额外来源。',
        '`D:/HCUP/cml-spec17`。本题 `project/AGENTS.md`、各角色配置、原生派工限定本题/公共只读/官方模板，并排除相关上游修复历史；团队 source_guard 字段为空【待补充】，不把范围指令等同实际技术隔离证明。',
        '所选 task-owned 原生 JSONL 内容未改写；仅截到最后完整LF作为采集快照并记录差异。跨题初始化总览原文与模拟器运行态排除，未用脱敏掩盖来源。原记录含本机路径/工具元数据；不包含整个客户端数据库。后续若团队做脱敏，须保留范围、原因及摘要映射。',
        '见 `missing-fields.md` 和 `evidence-facts.json:gaps`；Comate记录为本题未使用，独立子侧边栏ID为未暴露，官方baseline报告为缺失。原生未输出的字段不编造。所选已登记本题JSONL已收集；采集后事件需3-package重新快照。侧边栏人工Markdown导出目录未提供；现有Markdown明确是脚本派生副本。',
    ]
    if len(fields) != len(values): raise ValueError((len(fields), len(values)))
    # 3-package moves native records to package-root traces/<task>/.
    values = [v.replace('`traces/', '`../../traces/cml-spec17/') for v in values]
    values[12] += ' 无关搜索命中只保留计数，不导出无关UUID/路径/提示/正文；仅已知初始化总览保留排除ID和理由。本题原生内容不因该派生检索索引清理而改写。'
    lines = ['# 运行记录索引：cml-spec17', '', '本文件按官方模板逐字段填写，最终放在 `tasks/cml-spec17/trace-index.md`。所有 `project/` 路径对应本题工程根；原生素材在包根 `traces/cml-spec17/`，因此本文件使用 `../../traces/cml-spec17/` 的最终包内引用。当前素材仍位于草案 `traces/`，完整 source→package 映射见 `package-layout.json`。evidence-facts及export-manifest内的native/markdown字段是导出时相对于草案D的来源坐标，用同一映射解析。`logs/`、`changes/` 等放在同题材料层。', '']
    for label, value in zip(fields, values): lines += ['- ' + label + ' ' + value, '']
    lines += ['## 会话与双 ID 对照', '', '本题运行器是 Codex，原生 `session_meta.payload.id` 承担独立运行器会话标识。Comate `sessionUuid` 不适用；这里不制造第二套引擎UUID。原生元数据和过滤后的索引逐项给出对应证据。', '', '本题原生实际还含同名易混字段 `session_meta.payload.session_id`：3个主会话该字段等于自身id；12个子会话该字段等于真实parent_thread_id，是父/分组标识，不能冒充独立子UUID。`evidence-facts.json` 中整理器字段 `session_id` 明确取自原生payload.id，并非照抄原生payload.session_id。独立验证保留了误把两字段强制相等的新增探针失败及按原始首行事实修正的记录。', '', '| 原生运行器会话 ID | IDE侧边栏 ID / 父会话 | 角色/路径 | 原始文件 |', '| --- | --- | --- | --- |']
    for r in facts['native_sessions']:
        sidebar = r['sidebar_id'] or ('未暴露独立行；父 `' + str(r.get('parent_thread_id')) + '`')
        package_link = '../../traces/cml-spec17/' + r['native'].removeprefix('traces/')
        lines.append(f"| `{r['session_id']}` | {sidebar} | {r.get('agent_path') or '主会话'} | [{Path(r['native']).name}]({package_link}) |")
    lines += ['', '## 模型与原生用量截点', '', '| 会话 | 原生模型 ID / effort | 最后可见累计 input / output / total token |', '| --- | --- | --- |']
    for r in facts['native_sessions']:
        models = '; '.join(str(c.get('model')) + ' / ' + str(c.get('effort', c.get('reasoning_effort', '未输出'))) for c in r['contexts']) or '【待补充】（原生未输出）'
        info = (r.get('last_reported_token_info') or {}).get('total_token_usage') or {}
        tokens = ' / '.join(str(info.get(k, '未输出')) for k in ('input_tokens', 'output_tokens', 'total_tokens'))
        lines.append(f"| `{r['session_id']}` | {models} | {tokens} |")
    lines += ['', '这些是各会话原生最后一条 token_count 的可见计数，不是计费账单，不跨主子会话相加。具体缓存、reasoning token、last_token_usage保留于事实JSON。', '', '## 任务书版本与历史', '', f"公共任务书所属仓库 `{facts['harness']['repository_root']}`，HEAD `{facts['harness']['commit']}`。同时保存实际读取文件SHA，避免只凭仓库HEAD判断工作树文件。", '', '| 文件 | 公共/本题实际 SHA-256 |', '| --- | --- |']
    for name, h in facts['harness']['taskbooks'].items():
        local = facts['harness']['local_taskbooks'].get(name)
        lines.append(f'| `{name}` | `{h}`；本题副本 {"相同" if h == local else str(local)} |')
    lines += ['', '`spec/history/` 当前不存在，未发现本题历史任务书。字段来源见 evidence-facts.json:harness；没有访问题包其他目录或其他题工程。', '', '## 快照和正式打包约定', '', 'P 为 changes/project-files.json 的完整工程冻结集合；D 为本材料输出 `.comate/submission-draft/`。D 复制到材料层且整体不进入project，消除补丁自包含循环。其他非D的 `.comate/` 过程文件纳入P。有效 spec、hypium_tests、workflow、traces、历史失败及源码快照全部保留；噪声排除逐项说明。第3阶段复制任何不在P内的文件、或P任一字节变动，都须重新冻结并回放补丁。', '']
    (OUT / 'trace-index.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'official_fields': len(fields), 'sessions': len(facts['native_sessions']), 'config_files': len(configs)}, ensure_ascii=False))

if __name__ == '__main__': main()
