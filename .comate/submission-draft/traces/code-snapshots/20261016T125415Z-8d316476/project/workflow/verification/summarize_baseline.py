import collections
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'traces/baseline-analysis'
lines=(OUT/'build-raw.log').read_text(encoding='utf-8-sig').splitlines()
warnings=[]
for i,line in enumerate(lines):
    m=re.search(r'WARN: ArkTS:WARN File: (.+):(\d+):(\d+)$',line)
    if m:
        message=lines[i+1].strip()
        category='deprecated API' if 'has been deprecated' in message else message
        warnings.append({'rawLogLine':i+1,'file':m.group(1).replace('D:/HCUP/vg-spec9/',''),'line':int(m.group(2)),'column':int(m.group(3)),'category':category,'message':message})
(OUT/'build-warning-index.json').write_text(json.dumps(warnings,ensure_ascii=False,indent=2),encoding='utf-8')
cats=collections.Counter(x['category'] for x in warnings)
summary={'fileDiagnostics':len(warnings),'categories':dict(cats),'signingWarning':any('No signingConfig found' in x for x in lines),'arktsCompilerExecuted':any('Finished :entry:default@CompileArkTS' in x for x in lines),'buildSuccessful':any('BUILD SUCCESSFUL' in x for x in lines)}
(OUT/'build-warning-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# Existing baseline warning index','',f'File diagnostics: {len(warnings)}. Non-file warning: No signingConfig found for product default.','', '| Category | Count |','|---|---:|']
md += [f'| {c} | {n} |' for c,n in cats.items()]
md += ['', '| Raw build log line | Source | Message |','|---:|---|---|']
md += [f"| {w['rawLogLine']} | {w['file']}:{w['line']}:{w['column']} | {w['message']} |" for w in warnings]
(OUT/'build-warning-index.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
