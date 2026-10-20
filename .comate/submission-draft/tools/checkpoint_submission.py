"""Root-coordinator checkpoint, deliberately without self-referencing hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import sys

root=Path(__file__).resolve().parents[3]
path=root/'workflow/state.json'
state=json.loads(path.read_text(encoding='utf-8'))
if not state.get('submission_stage'):
    state['previous_implementation_scope']=state.get('current_scope')
state['current_scope']={
    'request':'2-submit','source':'spec-harness/2-submit.md',
    'business_code_frozen':True,'full_feature_implementation_requested':False,
    'dedicated_session':os.environ.get('CODEX_THREAD_ID'),
    'deliverables':['.comate/submission-draft/ task materials only'],
}
state['submission_stage']={
    'status':sys.argv[1],
    'feature_status_unchanged':'38 pass; 3 blocked (B9-B11)',
    'draft_path':'.comate/submission-draft',
    'independent_validation_report':'.comate/submission-draft/validation/materials-verification.json',
    'patch_validation_report':'.comate/submission-draft/patch-validation.json',
    'source_snapshot':'.comate/submission-draft/traces/code-snapshot/project',
    'source_scope_note':'Exact source freeze is identified by draft/project-manifest.json after this checkpoint; the draft is outside project scope to avoid recursive patch/hash definitions.',
    'human_fields_still_missing':True,'official_submission_performed':False,
    'formal_team_freeze_time':'【待补充】',
}
for key,names in {
    'submission_requirements':['workflow/requirements/submission-review-01.md'],
    'submission_design':['workflow/design/submission-plan-01.md'],
    'submission_implementation':['workflow/implementation/submission-handoff-01.md'],
}.items():
    existing=[]
    for name in names:
        p=root/name
        if p.is_file():
            existing.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
    if existing:
        state['approved_artifacts'][key]=existing
state['updated_at']=datetime.now(timezone.utc).isoformat()
path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'submission_stage':state['submission_stage']['status'],'feature_status':'still partial/blocked'},ensure_ascii=False))
