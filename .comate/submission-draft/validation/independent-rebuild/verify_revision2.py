import hashlib
import json
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone

ROOT = Path('D:/HCUP/vg-spec8')
DRAFT = ROOT / '.comate/submission-draft'
OUT = DRAFT / 'validation/independent-rebuild'

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(1024*1024): h.update(chunk)
    return h.hexdigest()

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

start=datetime.now(timezone.utc).isoformat()
previous=read(DRAFT/'validation/revisions/revision1/project-manifest.json')
current=read(DRAFT/'changes/project-manifest.json')
old={x['path']:x for x in previous['files']}
new={x['path']:x for x in current['files']}
changed=sorted(x for x in set(old)&set(new) if old[x]['sha256'] != new[x]['sha256'] or old[x]['bytes'] != new[x]['bytes'])
expected_changed=sorted(['.comate/submission-draft/sources.fragment.md',
    '.comate/submission-draft/tools/prepare_materials.py', '.comate/submission-draft/tools/freeze_and_diff.py'])
material_copy_failures=[]
for name in expected_changed:
    if not (digest(ROOT/name)==digest(DRAFT/'project'/name)==new[name]['sha256']):
        material_copy_failures.append(name)
sources=(DRAFT/'sources.fragment.md').read_text(encoding='utf-8-sig')
source_scope_pass=(
    '\u5728\u5df2\u6838\u9a8c\u7684AI\u539f\u751f\u8bb0\u5f55\u8303\u56f4\u5185' in sources and
    '\u8fd9\u4e0d\u4ee3\u8868\u5bf9\u672a\u77e5\u4eba\u5de5\u64cd\u4f5c\u6216\u56e2\u961f\u989d\u5916\u6765\u6e90\u7684\u4fdd\u8bc1' in sources and
    'extra_sources' in sources and '\u3010\u5f85\u8865\u5145\u3011' in sources and
    '\u6ca1\u6709\u4ece\u6765\u6e90\u5e94\u7528\u4e0a\u6e38\u5f53\u524d\u5b9e\u73b0\u6216\u76f8\u5173\u4fee\u590d\u5386\u53f2\u83b7\u53d6\u672c\u529f\u80fd\u4ee3\u7801' not in sources)
freeze=read(ROOT/'workflow/production-freeze-01.json')
production_different=[x['path'] for x in freeze if
    not digest(ROOT/x['path'])==digest(DRAFT/'project'/x['path'])==x['sha256']]
official_pending=current['official_team_freeze_time']=='\u3010\u5f85\u8865\u5145\u3011'
different_times=current['technical_capture_time'] != current['material_revision_frozen_at_utc']
current_manifest_sha=digest(DRAFT/'changes/project-manifest.json')
result={'started_at':start,'environment':{'entry':'D:/hongmengcup/Enter-HarmonyEnv.ps1',
    'python':sys.version,'python_executable':sys.executable,'platform':platform.platform()},
    'prior_manifest_sha256':digest(DRAFT/'validation/revisions/revision1/project-manifest.json'),
    'current_manifest_sha256':current_manifest_sha,
    'expected_current_manifest_sha256':'444b98d793f8d057a33490bedb3b4f8056b9fd068602e2a7a26c193ffaeb8520',
    'same_file_set':set(old)==set(new), 'changed_files':changed, 'expected_changed_files':expected_changed,
    'material_copy_failures':material_copy_failures,
    'source_scope_disclosure':{'status':'pass' if source_scope_pass else 'fail',
        'note':'Narrowed to verified AI native records; explicitly does not guarantee unknown human operations or team extra sources'},
    'prior_14_checks_evidence_remains_applicable':set(old)==set(new) and changed==expected_changed,
    'prior_material_check':'material-check-result-before-source-scope-fix.json',
    'production_258':{'status':'pass' if len(freeze)==258 and not production_different else 'fail',
        'files':len(freeze),'different':production_different},
    'technical_times':{'identifier_and_native_export_start':current['technical_capture_time'],
        'later_material_revision_frozen_at_utc':current['material_revision_frozen_at_utc'],
        'official_team_freeze_time':current['official_team_freeze_time']},
    'boundary':{'project_git_absent':not (DRAFT/'project/.git').exists(),
        'original_git_pointer_preserved':(ROOT/'.git').is_file(),
        'original_git_pointer_sha256':digest(ROOT/'.git')},
    'ended_at':datetime.now(timezone.utc).isoformat()}
result['passed']=(result['same_file_set'] and changed==expected_changed and not material_copy_failures
    and source_scope_pass and len(freeze)==258 and not production_different and official_pending and different_times
    and current_manifest_sha==result['expected_current_manifest_sha256']
    and result['boundary']['project_git_absent'] and result['boundary']['original_git_pointer_preserved'])
(OUT/'revision2-check-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
sys.exit(0 if result['passed'] else 1)
