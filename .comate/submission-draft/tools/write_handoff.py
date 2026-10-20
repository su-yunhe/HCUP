"""Describe the exact stage-3 mapping; do not create a team ZIP or root files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.comate/submission-draft'

def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def deliverable(p):
    parts = p.relative_to(OUT).parts
    return not any(x in {'.work', '__pycache__', '.git'} for x in parts) and not (len(parts) > 2 and parts[0] == 'verification' and parts[1].startswith('replay-'))

def main():
    facts = json.loads((OUT / 'evidence-facts.json').read_text(encoding='utf-8'))
    project = json.loads((OUT / 'changes/project-files.json').read_text(encoding='utf-8'))
    checks = {}
    for name in ('changes/validation.json', 'verification/independent-replay.json', 'verification/final-audit.json'):
        p = OUT / name
        checks[name] = json.loads(p.read_text(encoding='utf-8')).get('result', 'see report') if p.exists() else 'pending'
    text = f'''# cml-spec17 单题提交草案

本目录完成2-submit范围的材料整理，供第3阶段汇总。正式团队提交信息仍有待补项；没有生成团队ZIP、上传或发送正式邮件。业务源码、资源和配置沿用1-do最终版本，844文件生产指纹保持一致。

- [仍需用户补充的字段](missing-fields.md)
- [已自动填入的事实及出处](auto-filled-facts.md)
- [构建运行说明](build.md)、[官方模板逐字段记录索引](trace-index.md)
- [完成情况片段](solution.fragment.md)、[来源片段](sources.fragment.md)、[本题清单片段](submission.json.fragment)、[人工修改待确认说明](human-changes.md)
- [完整差异](changes/final.diff)、[完整工程清单](changes/project-files.json)、[二进制资源表](changes/binary-files.csv)、[排除清单](changes/excluded-files.json)
- [主流程真实回放结果](changes/validation.json)、[独立回放结果](verification/independent-replay.json)、[独立材料终验](verification/final-audit.json)

当前完整工程选集{project['file_count']}文件，最终树OID `{project['git_tree_oid']}`；diff为{project['patch_bytes']}字节，SHA-256 `{project['patch_sha256']}`。本题原生采集{len(facts['native_sessions'])}会话，日志副本{len(facts['copied_logs'])}文件；采集时间 `{facts['checked_at_utc']}`，所有副本均为截至该时点的记录，不包含未来事件。当前主会话收尾及最终回复需第3阶段再采集，不能用当前新记录替代历史解题原件。

补丁按当前工作树真实字节生成，并关闭自动行尾转换；因此也记录canonical基线blob与既有checkout的LF/CRLF差异。这不是材料阶段改写业务文件，生产844项实际字节始终匹配1-do指纹。回放保留原字节；git apply 的原始行尾/空白告警未删，退出码与全集摘要为校验依据，不能从这些告警反推业务新增错误。

已运行/待运行状态：{json.dumps(checks, ensure_ascii=False)}。以对应JSON的实际命令、退出码、全集比对为准。生产构建与26个唯一自测方法、42个需求样本、2个普通guard回归沿用1-do的真实记录，本材料阶段没有重跑构建或业务测试。9项额外未测子边界与认证真实后端阻断均保留，不能宣称官方隐藏测试或实际支付交易已通过。

## 第3阶段精确复制约定

工程P是 `changes/project-files.json` 中的完整路径/字节/摘要集合，覆盖业务和spec、hypium_tests、workflow、日志、全部有效traces以及非输出.comate过程文件。复制P到 `tasks/cml-spec17/project/` 前须逐文件核对当前字节与清单，拒绝漂移；不得递归复制当前工作区或只复制业务目录。材料D为整个 `.comate/submission-draft/`，位于project外层，不进入自己的final.diff。此项边界用于阻断补丁自包含循环，其他真实过程文件未因此被整体删除。

按 `package-layout.json`：D内traces移动到包根 `traces/cml-spec17/`；其余材料（包括本说明、日志、changes、tools、verification、事实、官方模板副本和片段）移动到 `tasks/cml-spec17/`。最终trace-index中的 `../../traces/cml-spec17/` 是包内目标引用；当前D中素材仍在 `traces/`。evidence-facts/export-manifest中记录的native/markdown字段是采集时相对D的来源坐标，用layout转换，不把它误作最终相对目标。

三个fragment供团队汇总，不能单独当完整submission.json或团队声明。保留root traces非空的官方要求。本轮不修改团队根solution/sources/README或团队system-config，已使用的本题配置仍在工程原快照和本轮traces/config-used。

只排除：材料输出D本身、Git管理数据、已列举的依赖/构建缓存、本机设置、模拟器实例运行态，以及跨题初始化总览raw。`changes/excluded-files.json` 列{project['excluded_actual_count']}个实际排除项，`changes/ignore-boundary-audit.json` 列忽略规则与裁剪目录。`build-root`源码快照、旧失败HAP/截图/日志全部保留；0字节失败PNG列入二进制清单并标invalid，不算有效截图。

检索派生索引对无关会话只保留命中计数，不导出其UUID、路径、提示或正文；仅已知跨题初始化总览保留排除ID和理由。本题原生JSONL内容不因清理派生检索元数据而改写。

`.work/` 是冻结索引/本题基线clone的临时目录；`verification/replay-*/` 是独立重放临时clone；`__pycache__/` 是材料工具缓存。上述目录均不交付，其脚本/命令stdout/stderr/JSON报告保留。`material-files.json` 提供可交付材料摘要（清单自身不作自引用摘要），`package-layout.json` 给出逐文件最终位置。已有历史manifest中对排除总览文件的引用作为历史事实保留，实际总览原文不交付，也没有读取其正文。

## 缺项与限制

用户空字段详见missing-fields；本题指定的官方baseline报告精确路径不存在，本地prepare-baseline/baseline-build/setup-result作为独立证据引用，不能冒充官方原日志。实际客户端是Codex；Comate会话库、macOS客户端/扩展为不适用。子会话独立侧边栏ID未暴露时记明，模型原生未输出字段不编造。Markdown是原生JSONL的派生阅读副本，用户侧边栏导出目录仍待补充。

正式冻结时间仍为【待补充】，本地工程清单时间与原生导出时间各自为技术快照时间。历史受控测试脚本含原根目录/设备/环境入口固定配置，跨机受控复测需要在独立副本适配并重新取证；生产构建说明使用环境变量和相对路径，本阶段未改历史测试工具来制造可移植性。
'''
    (OUT / 'README.md').write_text(text, encoding='utf-8')
    (OUT / 'handoff.md').write_text(text, encoding='utf-8')
    paths = sorted([p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and deliverable(p)] + ['package-layout.json', 'material-files.json'])
    paths = sorted(set(paths))
    mappings = []
    for p in paths:
        dest = 'traces/cml-spec17/' + p.removeprefix('traces/') if p.startswith('traces/') else 'tasks/cml-spec17/' + p
        mappings.append({'source': p, 'package_destination': dest})
    (OUT / 'package-layout.json').write_text(json.dumps({'task_id': 'cml-spec17', 'draft_source_base': '.comate/submission-draft/',
        'project_manifest': 'changes/project-files.json', 'project_destination': 'tasks/cml-spec17/project/',
        'excluded_material_scratch': ['.work/', '**/__pycache__/', 'verification/replay-*/', '**/.git/'],
        'paths_in_evidence_facts_and_export_manifest': 'draft-relative source coordinates; resolve with mappings', 'mappings': mappings}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = []
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and deliverable(p) and p.name != 'material-files.json':
            files.append({'path': p.relative_to(OUT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)})
    (OUT / 'material-files.json').write_text(json.dumps({'created_at_utc': datetime.now(timezone.utc).isoformat(), 'self_hash_excluded': True, 'files': files}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'material_files': len(files), 'mappings': len(mappings), 'checks': checks}, ensure_ascii=False))

if __name__ == '__main__': main()
