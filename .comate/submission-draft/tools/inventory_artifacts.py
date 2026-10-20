"""Inventory only deliverable task artifacts; never include temporary Git checkouts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os

out=Path(__file__).resolve().parents[1]
plan=json.loads((out/'assembly-plan.json').read_text(encoding='utf-8'))
rows=[]
excluded=[]
for directory, subdirs, names in os.walk(out):
    rel_dir=Path(directory).relative_to(out)
    keep=[]
    for name in subdirs:
        rel=(rel_dir/name).as_posix()+'/'
        if name in plan['exclude_components'] or any(rel.startswith(x) for x in plan['exclude_prefixes']):
            excluded.append(rel)
        else:
            keep.append(name)
    subdirs[:]=keep
    for name in sorted(names):
        rel=(rel_dir/name).as_posix()
        if rel in plan['exclude_files']:
            continue
        p=out/rel
        if p.is_symlink():
            raise RuntimeError('Review symlink before inventory: '+rel)
        h=hashlib.sha256()
        with p.open('rb') as handle:
            for chunk in iter(lambda:handle.read(1024*1024),b''):
                h.update(chunk)
        rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':h.hexdigest()})
rows.sort(key=lambda x:x['path'])
payload={'task_id':'cml-spec7','created_at_utc':datetime.now(timezone.utc).isoformat(),
         'files':rows,'file_count':len(rows),'total_bytes':sum(x['bytes'] for x in rows),
         'excluded_directories':excluded,'self_excluded':'artifact-manifest.json',
         'assembly_plan':'assembly-plan.json','not_formal_team_freeze':True,
         'note':'This index excludes its own bytes and generated validation clones. Source project identity remains project-manifest.json; refresh this artifact inventory after any future material edits.'}
(out/'artifact-manifest.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in payload.items() if k!='files'},ensure_ascii=False))
