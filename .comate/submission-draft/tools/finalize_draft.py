"""Record final material integrity without rebuilding or touching source inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[3];O=R/'.comate/submission-draft'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 m=json.loads((O/'changes/project-manifest.json').read_text(encoding='utf-8'))
 mismatches=[x['path'] for x in m['files'] if not (R/x['path']).is_file() or sha(R/x['path'])!=x['sha256']]
 frozen=json.loads((R/'workflow/final-validation-fingerprint.json').read_text(encoding='utf-8'))
 frozen_bad=[]
 for key in ['tracked_files_sha256','build_relevant_untracked_sha256']:
  for n,expected in frozen[key].items():
   if not (R/n).is_file() or sha(R/n)!=expected:frozen_bad.append(n)
 source_diff=subprocess.run(['git','diff','--check'],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 staged=subprocess.check_output(['git','diff','--cached','--binary'],cwd=R)
 requirements=json.loads((O/'audit/requirements-review.json').read_text(encoding='utf-8'))
 independent=json.loads((O/'audit/independent-verification.json').read_text(encoding='utf-8'))
 sessions=json.loads((O/'traces/sessions.json').read_text(encoding='utf-8'))
 export_bad=[]
 for x in sessions['sessions']:
  for key,hkey in [('native_file','export_sha256'),('markdown_file','markdown_sha256')]:
   if sha(O/'traces'/x[key])!=x[hkey]:export_bad.append(x[key])
 core=['build.md','trace-index.md','solution.fragment.md','sources.fragment.md','submission.json.fragment','human-changes.md','pending-fields.md','auto-filled-facts.md','delivery-notes.md','changes/final.diff','changes/project-manifest.json','changes/binary-files.json','traces/sessions.json']
 hashes={n:sha(O/n) for n in core}
 hashes.update({p.relative_to(O).as_posix():sha(p) for p in (O/'audit').rglob('*') if p.is_file() and p.name not in ['final-review.json','submission-state.json']})
 report={'task_id':'vg-spec1','completed_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'2-submit materials, not formal package/upload','project_version':m['version'],'source_files_rechecked':len(m['files']),'source_mismatches':mismatches,'frozen_input_mismatches':frozen_bad,'git_diff_check_exit':source_diff.returncode,'git_diff_check_stdout':source_diff.stdout.decode(errors='replace'),'git_diff_check_stderr':source_diff.stderr.decode(errors='replace'),'original_index_empty_diff':not staged,'export_mismatches':export_bad,'sessions':len(sessions['sessions']),'exported_at':sessions['exported_at'],'document_hashes':hashes,'independent_reports':['audit/requirements-review.json','audit/independent-verification.json'],'pass_material_integrity':not(mismatches or frozen_bad or source_diff.returncode or staged or export_bad),'ready_for_formal_submission':False,'remaining':'User blank fields, formal freeze and final cross-task 3-package validation. Codex/Comate mismatch and missing historical evidence are disclosed, not fabricated.'}
 write(O/'audit/final-review.json',report)
 state=json.loads((O/'audit/submission-state.json').read_text(encoding='utf-8'));state.update({'status':'material_draft_complete_with_disclosed_gaps','completed_at_utc':report['completed_at_utc'],'pass_material_integrity':report['pass_material_integrity'],'ready_for_formal_submission':False,'remaining':['user fields listed in pending-fields.md','formal freeze/3-package only on request','unavailable historical/Comate fields are disclosed; no fabricated substitutes','current material thread snapshot ends at per-session recorded cutoff']});write(O/'audit/submission-state.json',state)
 print(json.dumps({k:report[k] for k in ['pass_material_integrity','source_files_rechecked','source_mismatches','frozen_input_mismatches','sessions','ready_for_formal_submission']},ensure_ascii=False))
if __name__=='__main__':main()
