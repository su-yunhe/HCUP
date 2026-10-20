import collections, hashlib, json, re, subprocess
from pathlib import Path
from datetime import datetime, timezone
root=Path.cwd()
out=root/'traces/do-implementation'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
tracked=subprocess.check_output(['git','ls-files','-z']).decode('utf-8').split('\0')
extra=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z','--','feature/main']).decode('utf-8').split('\0')
paths=sorted(set(p for p in tracked+extra if p and (root/p).is_file()))
hashes={p:sha(root/p) for p in paths}
payload=json.dumps(hashes,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
changed=subprocess.check_output(['git','diff','--name-only'],stderr=subprocess.DEVNULL).decode().splitlines()
hap=root/'entry/build/default/outputs/default/entry-default-unsigned.hap'
record={'captured_at':datetime.now(timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
    'scope':'all tracked repository files plus untracked new feature/main production files; excludes tests/workflow/logs',
    'aggregate_algorithm':'SHA256 of JSON file-hash map, ensure_ascii=False, sort_keys=True, separators comma/colon',
    'source_aggregate_sha256':hashlib.sha256(payload).hexdigest(),'files_sha256':hashes,
    'changed_tracked_files':changed,'new_production_files':sorted(p for p in extra if p),
    'hap':{'path':hap.relative_to(root).as_posix(),'bytes':hap.stat().st_size,'sha256':sha(hap)},
    'production_frozen':True}
(out/'source-frozen-r1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
def diagnostics(path):
    text=path.read_text(encoding='utf-8-sig',errors='replace')
    return [(m.group(1),m.group(2).strip()) for m in re.finditer(r'ArkTS:WARN File: ([^\r\n]+)\r?\n\s*([^\r\n]+)',text)]
base=collections.Counter(diagnostics(root/'logs/analysis-baseline-assembleHap.log'))
current=collections.Counter(diagnostics(root/'logs/do-build-r2-debug.log'))
comparison={'baseline_count':sum(base.values()),'current_debug_count':sum(current.values()),
            'added':list((current-base).elements()),'removed':list((base-current).elements())}
(out/'debug-warning-compare-r1.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(paths),'source_aggregate_sha256':record['source_aggregate_sha256'],'hap':record['hap'],'warnings':comparison,'changed':changed,'new':record['new_production_files']},ensure_ascii=False,indent=2))
