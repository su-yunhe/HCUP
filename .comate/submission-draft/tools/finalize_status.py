"""Summarize completed material checks without changing the frozen source tree."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

out=Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((out/name).read_text(encoding='utf-8-sig'))
def sha(name):
    return hashlib.sha256((out/name).read_bytes()).hexdigest()

final=load('validation/materials-verification.json')
full=load('validation/full-apply-03.json')
patch=load('patch-validation.json')
manifest=load('project-manifest.json')
native=load('traces/session-metadata.json')
facts=load('facts.json')
assert patch['passed'] and not full['counts'].get('fail') and not final['counts'].get('fail')
assert not final['counts'].get('not_run')
assert full['result']=='pass_with_declared_gaps' and final['result']=='pass_with_declared_gaps'
assert sha('validation/full-apply-03.json')=='94a96a73b3e2f54cf657631a0c56b8a919e6baeee36ee2c20ae57a17abdaf496'
result={
    'task_id':'cml-spec7','stage':'2-submit','status':'draft_verified_with_declared_gaps',
    'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
    'application_code_resources_and_build_configuration_unchanged':True,
    'project_version':manifest['final_version'],'snapshot_git_tree':manifest['snapshot_git_tree'],
    'project_file_count':len(manifest['files']),'patch_sha256':patch['patch_sha256'],
    'patch_apply_check_exit_code':0,'patch_apply_exit_code':0,
    'root_patch_report':'patch-validation.json',
    'independent_full_report':{'path':'validation/full-apply-03.json','sha256':sha('validation/full-apply-03.json'),'counts':full['counts']},
    'final_materials_report':{'path':'validation/materials-verification.json','sha256':sha('validation/materials-verification.json'),'counts':final['counts']},
    'native_snapshot_session_count':len(native['sessions']),'native_snapshot_at_utc':native['exported_at_utc'],
    'native_snapshot_note':'The final slice contains substantive independent apply verification and original failed/corrected checks. It does not include this later status-writing operation or future packaging events.',
    'functional_validation':facts['validation']['requirement_counts'],
    'all_functional_requirements_complete':False,'official_score_available':False,
    'formal_freeze_time':'【待补充】','manual_missing_fields':'missing-fields.md',
    'automatically_filled_facts':'auto-filled-facts.md',
    'temporary_clone_policy_result':'temporary-clone-cleanup-rejected.json',
    'package_copy_rules':'assembly-plan.json','formal_package_created':False,'external_submission_performed':False
}
(out/'materials-status.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
