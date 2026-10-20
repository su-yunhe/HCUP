"""Final material consistency checks; no builds, device actions or source edits."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime,timezone
from prepare_materials import excluded

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'.comate/submission-draft'
def load(name): return json.loads((OUT/name).read_text(encoding='utf-8-sig'))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def main():
 checks={}
 required=['changes/final.diff','changes/project-manifest.json','changes/binaries.json','changes/validation.json','build.md','trace-index.md','sources.fragment.md','solution.fragment.md','submission.json.fragment','traces/session-inventory.json','traces/session-index.filtered.jsonl','traces/tool-skill-index.json','taskbook-version.json','runtime-evidence.json','pending-fields.md','facts-and-sources.md','logs-manifest.json','delivery.md']
 checks['required_files']=all((OUT/n).is_file() for n in required)
 manifest=load('changes/project-manifest.json'); expected={x['path']:x for x in manifest['files']}
 checks['project_snapshot_current']=all((ROOT/n).is_file() and sha((ROOT/n).read_bytes())==row['sha256'] for n,row in expected.items())
 names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).split(b'\0')
 actual={x.decode() for x in names if x and not excluded(x.decode()) and (ROOT/x.decode()).is_file()}
 checks['project_snapshot_file_set']=actual==set(expected)
 validation=load('changes/validation.json')
 raw=(OUT/'changes/final.diff').read_bytes()
 checks['diff_digest']=sha(raw)==validation['diff_sha256'] and len(raw)==validation['diff_bytes']
 checks['verified_apply']=validation['pass'] and validation['apply_check_exit_code']==validation['apply_exit_code']==0 and not any(validation[x] for x in ['raw_byte_mismatches','extra','missing'])
 logs=load('logs-manifest.json')
 source_set={p.relative_to(ROOT/'logs').as_posix() for p in (ROOT/'logs').rglob('*') if p.is_file()}
 target_set={p.relative_to(OUT/'logs').as_posix() for p in (OUT/'logs').rglob('*') if p.is_file()}
 checks['logs_complete']=source_set==target_set=={x['path'] for x in logs}
 checks['log_hashes']=all(sha((ROOT/'logs'/x['path']).read_bytes())==sha((OUT/'logs'/x['path']).read_bytes())==x['sha256'] for x in logs)
 checks['binary_hashes']=all(sha((ROOT/x['path']).read_bytes())==x['sha256'] and (ROOT/x['path']).stat().st_size==x['bytes'] for x in load('changes/binaries.json'))
 production=json.loads((ROOT/'workflow/implementation/source-round-02.json').read_text())['production_scope_sha256']
 checks['production_unchanged']=all(sha((ROOT/n).read_bytes())==sha((OUT/'traces/code-snapshot'/n).read_bytes())==h for n,h in production.items())
 template=Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
 index=(OUT/'trace-index.md').read_text(encoding='utf-8')
 fields=[s for s in template.splitlines() if s.startswith('- ')]
 checks['official_fields']=len(fields)==24 and all(any(s.startswith(f+' ') and len(s)>len(f)+1 for s in index.splitlines()) for f in fields)
 checks['portable_build']=not re.search(r'(?i)\b[A-Z]:[/\\]|/Users/|/Applications/|C:\\Users', (OUT/'build.md').read_text(encoding='utf-8'))
 fragment=load('submission.json.fragment')
 paths=[fragment[k] for k in ['project_path','build_instructions','trace_index']]
 checks['json_paths']=paths==['tasks/vg-spec15/project','tasks/vg-spec15/build.md','tasks/vg-spec15/trace-index.md']
 inv=load('traces/session-inventory.json')
 ids=set()
 native_ok=True;md_ok=True
 for row in inv:
  sid=row['native_session_id']; ids.add(sid)
  p=OUT/row['export']; native=p.read_bytes()
  records=[json.loads(line) for line in native.splitlines()]
  native_ok &= sha(native)==row['sha256'] and len(native)==row['bytes'] and records[0]['payload']['id']==sid and not row['parse_errors']
  md=(OUT/row['markdown']).read_text(encoding='utf-8')
  md_ok &= len(re.findall(r'^## 行 ',md,re.M))==len(records)
 checks['native_integrity']=native_ok
 checks['markdown_all_records']=md_ok
 state=json.loads((ROOT/'workflow/state.json').read_text(encoding='utf-8-sig'))
 checks['registered_sessions_exported']={x['session_id'] for x in state['sessions'] if x.get('session_id')}<=ids
 skills=load('traces/tool-skill-index.json')
 checks['tool_skill_index_nonempty']=bool(skills['calls'])
 for call in skills['calls']:
  if call['session_id'] not in ids: checks['tool_skill_index_nonempty']=False
 report={'checked_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'pass':all(checks.values()),
         'project_files':len(expected),'logs':len(logs),'sessions':len(inv),'binary_files':len(load('changes/binaries.json')),
         'note':'No build or device rerun. Full baseline clone/apply evidence is changes/validation.json; these checks audit final files and unchanged production bytes.'}
 (OUT/'final-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
 if not report['pass']: raise SystemExit(1)

if __name__=='__main__':main()
