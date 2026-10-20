import collections, hashlib, json, re, subprocess, zipfile
from pathlib import Path
from datetime import datetime, timezone
root=Path.cwd()
out=root/'traces/do-implementation'
out.mkdir(parents=True, exist_ok=True)
def diagnostics(path):
    text=path.read_text(encoding='utf-8-sig',errors='replace')
    return [(m.group(1).replace('\\\\','/'),m.group(2).strip()) for m in re.finditer(r'ArkTS:WARN File: ([^\r\n]+)\r?\n\s*([^\r\n]+)',text)]
baseline=diagnostics(root/'logs/analysis-baseline-assembleHap.log')
current=diagnostics(root/'logs/do-build-r1.log')
diff=list((collections.Counter(current)-collections.Counter(baseline)).elements())
removed=list((collections.Counter(baseline)-collections.Counter(current)).elements())
animations=[]
for p in sorted((root/'feature/main/src/main/resources/rawfile/lottie').glob('*.json')):
    data=json.loads(p.read_text(encoding='utf-8'))
    assert data['op']>data['ip'] and data['fr']>0 and data['w']==64 and data['h']==64
    assert data['layers'] and data['assets']==[]
    animations.append({'path':p.relative_to(root).as_posix(),'frames':data['op']-data['ip'],'fps':data['fr'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
hap=root/'entry/build/default/outputs/default/entry-default-unsigned.hap'
packaged=[]
if hap.exists():
    with zipfile.ZipFile(hap) as z:
        packaged=[n for n in z.namelist() if '/lottie/tab_' in n or '/products/' in n]
result={'captured_at':datetime.now(timezone.utc).isoformat(),'baseline_warning_file_diagnostics':len(baseline),
        'r1_warning_file_diagnostics':len(current),'added_warning_file_diagnostics':diff,'removed_warning_file_diagnostics':removed,
        'animations':animations,'packaged_assets':packaged,'packaged_asset_count':len(packaged),
        'meaning':'Static structure/package and compiler warnings only; no device playback or functional pass claimed.'}
(out/'local-check-r1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
