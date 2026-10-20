import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('D:/HCUP/vg-spec8')
DRAFT=ROOT/'.comate/submission-draft'
V=DRAFT/'validation'
E=V/'independent-rebuild'
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024): h.update(chunk)
    return h.hexdigest()
reconstruction=load(E/'round03/reconstruction-result.json')
previous=load(E/'material-check-result-before-source-scope-fix.json')
revision=load(E/'revision2-check-result.json')
manifest=load(DRAFT/'changes/project-manifest.json')
assert reconstruction['passed'] and previous['passed'] and revision['passed']
assert sha(DRAFT/'changes/project-manifest.json')==reconstruction['manifest_sha256_after']

requirements=[
 {'id':'C1','requirement':'不得编造，用户空字段保持待补','status':'pass','evidence':'pending-fields.md; auto-facts.md; independent-rebuild/material-check-result-before-source-scope-fix.json'},
 {'id':'C2','requirement':'完整binary差异可应用并对应全部工程真实文件','status':'pass','evidence':'independent-rebuild/round03/reconstruction-result.json; commands.json; 01..08 stdout/stderr logs'},
 {'id':'C3','requirement':'二进制路径、大小、SHA与基线同源声明','status':'pass','evidence':'397项逐字节摘要核对，8项基线同源；文件集修订仅3个文本材料，二进制证据仍适用'},
 {'id':'C4','requirement':'排除构建缓存与Git元数据，公开排除边界','status':'pass','evidence':'changes/exclusions.json; metadata-boundary-fix.json; round03完整文件集合比较；仅递归project/changes/validation派生子树、具名缓存/私有环境/非本题原文排除'},
 {'id':'C5','requirement':'只摘本题主子会话，按目录和题号查找','status':'pass','evidence':'14份native文件逐行JSON/header/records/hash；session-discovery.json父Agent只读元数据反查记录已复核；验证者未自行读全局DB或别题原文'},
 {'id':'C6','requirement':'字面要求Comate引擎sessionUuid与IDE双ID','status':'blocked','evidence':'实际未使用Comate，无法生成该双ID；trace-index已如实给出Codex thread id与可继承session_meta.session_id关系，Codex标识核对pass；官方适用性仍待最终处理'},
 {'id':'C7','requirement':'保留失败、重试与未采用过程','status':'pass','evidence':'756源日志无缺无变，外置另有合法copy-manifest；原生工具记录；本审核失败轮与材料revision1均保留'},
 {'id':'C8','requirement':'记录公共任务书版本与本题历史','status':'pass','evidence':'公共4文件SHA及本题副本均实测相等；spec/history不存在；provenance/taskbook-version.json'},
 {'id':'C9','requirement':'JSON三路径为包内相对路径且后两项为文件','status':'pass','evidence':'submission.json.fragment；project目录、build.md及trace-index.md映射逐项存在'},
 {'id':'C10','requirement':'如实披露来源、人工、脱敏与记录缺失','status':'pass','evidence':'revision2 source scope correction; human-changes.md; trace-index.md; pending-fields.md; redaction ledgers'}
]
pending_human=[
 'team.version','team.contact','team.freeze_time（北京时间正式成果冻结时间）',
 'team.members[].name / work','team.source_guard','task.human_edits','task.known_issues',
 'task.extra_sources','task.md_export_dir',
 '3-package专用：submitted_tasks / attempted_not_submitted / zip_out'
]
known_gaps=[
 'Comate未使用，双ID/Comate扩展版本不适用，不得补造；已提供Codex原生真实映射',
 '官方指定reports/build-baselines/vg-spec8.log不存在；实际project/logs/prepare-baseline.log存在，精确脚本执行时刻仍未核实',
 '独立模型构建版本未取得；OHPM与历史Python精确版本未核实，build.md已标待补；本次审核Python版本不代替历史测试环境',
 '当前主/材料审核原生轨迹为2026-10-16T15:23:39.879380+00:00截点完整行前缀；其后修订及本报告原生尾部需3-package另行保存，不能伪称已在原冻结快照内',
 '混合初始化总览原文与非本题安装前UI按具名规则排除；未证明完整覆盖总览中的全部本题初始化事件',
 '自动自测脚本固定开发机ROOT/manifest门槛已披露；本阶段未修改或重新运行功能测试',
 '官方隐藏测试、D2深层成功恢复/预览取消、并发自动同步未运行；既往本地结果不等于官方成绩'
]
findings=[
 {'id':'F1','initial_status':'fail','final_status':'pass','expected':'Git元数据不属于交付工程，manifest与patch重建一致',
  'actual':'初版manifest1992包含40字节.git工作树指针，而Git补丁重建1991；check/apply本身均0',
  'minimum_reproduction':'第一轮python verify_reconstruction.py；记录在independent-rebuild/reconstruction-result.json（exit1）',
  'cause':'枚举器只排除.git目录，未排除.git文件；父Agent修快照边界与生成器，原工程.git未动',
  'evidence_strength':'直接完整文件集、SHA和独立check/apply，强',
  'resolution':'round02及round03 fresh clone均1991文件全等；旧清单、日志、补丁保留'},
 {'id':'F2','initial_status':'fail','final_status':'pass','expected':'来源声明限定已观察范围，未知人工/额外来源保留待补',
  'actual':'原sources首段无主体限定地保证未从上游获取代码，与空声明及导出边界不相称',
  'minimum_reproduction':'阅读sources.fragment.md旧首段与spec/submit-input.yaml空human_edits/extra_sources；manual-source-scope-finding.json',
  'cause':'材料表述范围过大，不是已证明的受保护来源访问',
  'evidence_strength':'文案与输入直接证据强；不推断隐藏人工行动',
  'resolution':'revision2仅改3个材料/生成器文件，限定已核验AI记录、不保证未知人工来源；round03重建全等'},
 {'id':'T1','kind':'verifier_expectation_error','initial_status':'fail','final_status':'pass',
  'actual':'材料检查器前两轮把合法生成的logs/copy-manifest.json分别误当源日志或project/logs原位文件',
  'resolution':'保留前两轮脚本/JSON/console；按756条原始日志和757条外置日志（含copy-manifest）校验，逐项验证copy-manifest及冻结副本，未删原日志断言'},
 {'id':'T2','kind':'inspection_command_error','status':'fail','resolved_as':'optional file does not exist; no requirement depends on it',
  'actual':'一次Get-Content尝试读取不存在的traces/README.md导致PowerShell exit1；随后使用trace-index已有读取说明。原始工具返回保留于审核原生会话尾部'}
]
checks=previous['checks']
checks['source_scope_disclosure']=revision['source_scope_disclosure']
report={
 'schema_version':1,'task_id':'vg-spec8','reviewer_thread_id':'01a14549-2c5d-70c0-ab26-64feca32bde8',
 'completed_at_utc':datetime.now(timezone.utc).isoformat(),
 'submission_draft_preparation_status':'pass','formal_team_submission_readiness':'blocked',
 'status_note':'本轮2-submit草稿整理与独立校验完成；人工空字段/不适用项按要求披露，不要求用户现在补全才能结束草稿；不能据此声称正式团队包可直接提交。',
 'material_revision':2,'capture_id':manifest['capture_id'],'base_commit':manifest['base_commit'],
 'project':{'files':manifest['file_count'],'bytes':manifest['total_bytes'],'manifest_sha256':sha(DRAFT/'changes/project-manifest.json')},
 'patch':{'bytes':reconstruction['patch_bytes_after'],'sha256':reconstruction['patch_sha256_after'],'check_exit_code':0,'apply_exit_code':0},
 'technical_times':revision['technical_times'],
 'environment':revision['environment'],'environment_entry_loaded_each_powershell_process':True,
 'requirements':requirements,'material_checks':checks,
 'final_reconstruction':reconstruction,
 'revision2_affected_scope_recheck':revision,
 'previous_checks_reuse_reason':'revision1与revision2完整manifest文件集相同，只有3个明示材料/生成器文本文件变化；其他14项材料证据对应字节未变。新版本source范围、258生产指纹、Git边界、完整patch和全部1991文件已重验。',
 'findings_and_retries':findings,'human_pending_fields':pending_human,'known_gaps_or_applicability':known_gaps,
 'not_run':[
   {'item':'本阶段构建、安装、启动、设备/模拟器与功能测试','status':'not_run','reason':'派工明确禁止；仅复核既有结果材料，没有重新证明A1—A19产品行为'},
   {'item':'ZIP打包、上传、邮件、Git提交','status':'not_run','reason':'2-submit范围外，由后续3-package处理'},
   {'item':'verify_supplement.py额外代码快照/模板扩展测试','status':'not_run','reason':'脚本准备后主Agent限定只复验受影响项与完整patch/files，未运行；不将其算通过'}
 ],
 'writes_confined_to':['.comate/submission-draft/validation/independent-review.json','.comate/submission-draft/validation/independent-review.md','.comate/submission-draft/validation/independent-rebuild/'],
 'no_production_spec_state_or_frozen_material_edits_by_verifier':True,
 'retention':{'raw_commands':'independent-rebuild/{round03,round02}/commands.json及编号stdout/stderr；首轮位于independent-rebuild根',
   'failures':'independent-rebuild/reconstruction-result.json; manual-source-scope-finding.json; *attempt01*/*attempt02*; revisions/revision1/',
   'final_checks':'independent-rebuild/round03/reconstruction-result.json; revision2-check-result.json; material-check-result-before-source-scope-fix.json',
   'packaging':'保留独立报告所引用JSON/脚本/命令/原始日志，排除临时baseline clone/.git/缓存；审核原生会话尾部由3-package另存'}
}
(V/'independent-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')

rows='\n'.join(f"| {x['id']} | {x['requirement']} | {x['status']} |" for x in requirements)
md=f'''# vg-spec8 独立材料审核（revision 2）

**2-submit 草稿准备校验 pass；正式团队提交就绪 blocked。** 用户空字段按要求待补，草稿工作已完成。没有重新构建、运行设备或复测产品功能，也没有改生产、Spec、state 或冻结材料；只写本 validation 目录。

最终独立 fresh clone 仅取本地 `base/vg-spec8` / `{manifest['base_commit']}`，禁用全局/系统Git配置及换行、filter等属性。`git apply --check --binary` 与真实 `git apply --binary --whitespace=nowarn` 均 exit 0；脚本 exit 0。冻结工程前后与重建工程的 **1991 文件**路径、大小、SHA-256全部一致。

- 补丁：**{reconstruction['patch_bytes_after']} bytes**，SHA-256 `{reconstruction['patch_sha256_after']}`。
- 工程清单 SHA-256：`{sha(DRAFT/'changes/project-manifest.json')}`；本轮前后未变。
- 258 个生产输入与实现冻结一致，指纹清单 SHA-256 `cff0ff9567ae804b76c12add8b9989e95d37c89c18152b99b3fc3b09f4e85f5f`。
- 官方索引24字段齐全；JSON三路径映射正确、后两项是文件；build.md无私有绝对路径；14份本题native逐行可读且header/行数/hash一致；756条原日志及失败重试逐字节保留；另有合法复制索引；397项二进制摘要正确，8项基线同源。

| 约束 | 核对内容 | 结论 |
| --- | --- | --- |
{rows}

C6 字面Comate双ID无法提供，因为实际使用Codex。真实Codex thread ID与可继承的native session ID已核对并说明；这不构成Comate双ID。官方适用性应在后续提交处理中判断，不能补造。

本审核发现并退回了两项真实问题：初版错误纳入40字节 `.git` 指针（1992/1991不一致）；来源首段超出已核验AI记录范围作全题保证。父Agent分别修正派生边界和3个材料/生成器文件，原工程Git指针未动，业务输入未动；第二轮与最终第三轮均从新clone复验。失败清单、旧补丁、原始命令/日志和来源问题复现记录均保留。日志检查器自身对 `copy-manifest.json` 的两次集合预期错误也保留，没有删除原始日志断言。

技术ID/原生导出开始为 `{manifest['technical_capture_time']}`；本材料修订冻结为 `{manifest['material_revision_frozen_at_utc']}`。二者不同，团队正式冻结时间仍是 **【待补充】**，不得互相代填。

仍需人工补充：版本、联系人、团队正式冻结时间、成员与分工、来源保护声明、人工修改、已知问题、额外来源、IDE Markdown目录；3-package还需团队题目集合与ZIP输出。缺失/不适用项包括Comate双ID、官方指定准备日志、独立模型构建号及历史工具精确版本，均如实披露。原生轨迹只到明确截点，之后修订和本审核尾部须由3-package另存；混合总览原文未提交。

本轮复验只覆盖受影响材料和必要完整补丁/文件/生产指纹检查；其余材料证据通过两版清单逐项确认字节未变而继续适用。既有A1—A19结论仅被当作历史材料引用，本轮功能测试为 not_run，不能据此声称官方成绩。

证据：[最终重建](independent-rebuild/round03/reconstruction-result.json)、[命令及退出码](independent-rebuild/round03/commands.json)、[修订复验](independent-rebuild/revision2-check-result.json)、[24字段等材料检查](independent-rebuild/material-check-result-before-source-scope-fix.json)、[完整机器报告](independent-review.json)。每条Git命令的原始stdout/stderr在同轮目录。后续保留所引用的JSON、脚本和原始日志，排除临时baseline clone、.git和缓存。
'''
(V/'independent-review.md').write_text(md,encoding='utf-8')
print(json.dumps({'submission_draft_preparation_status':'pass','formal_team_submission_readiness':'blocked',
 'project_files':manifest['file_count'],'patch_bytes':reconstruction['patch_bytes_after'],
 'patch_sha256':reconstruction['patch_sha256_after'],'reports':['validation/independent-review.json','validation/independent-review.md']},ensure_ascii=True))
