import datetime
import json
from pathlib import Path
from baseline_ui import OUT,nodes

final=json.loads((OUT/'sync-final.json').read_text(encoding='utf-8'))
ns=list(nodes(final))
commands=[json.loads(x) for x in (OUT/'ui-commands.jsonl').read_text(encoding='utf-8').splitlines()]
final_times=[x['time'] for x in commands if 'dumpLayout' in x['argv'] and any('vg-spec9-sync-final.json' in a for a in x['argv'])]
record={'generated':datetime.datetime.now().astimezone().isoformat(),
        'finalCaptureStarted':final_times[-1] if final_times else None,
        'observationScope':'one manual-sync action; intentionally delayed 403 preflight errors; no successful sync tested',
        'requests':[json.loads(x) for x in (OUT/'webdav-requests.jsonl').read_text(encoding='utf-8').splitlines()],
        'finalSyncButtons':[a for a in ns if a.get('type')=='Button' and a.get('text')=='立即同步'],
        'finalErrorTexts':[a['text'] for a in ns if a.get('text') and '失败' in a['text']],
        'autoSyncEnabled':[a.get('checked') for a in ns if a.get('type')=='Toggle'],
        'originalHelperLimitation':'sync-observations.json after state was captured after only first HEAD response; a second HEAD remained pending; its busyRestoredAfterError=false is an early observation, not a product failure',
        'finalBusyRestoredAfterError':any(a.get('type')=='Button' and a.get('text')=='立即同步' and a.get('enabled')=='true' for a in ns),
        'requiredLoaderObserved':False,
        'successfulSyncFlowTested':False}
(OUT/'sync-final-observations.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='finalSyncButtons'},ensure_ascii=False,indent=2))
