import datetime
import json
import time
from baseline_ui import OUT,click,dump,nodes

def state(d):
    ns=list(nodes(d))
    return {'loadingProgressCount':sum(a.get('type')=='LoadingProgress' for a in ns),
            'busyButtons':[{'text':a.get('text'),'enabled':a.get('enabled'),'id':a.get('id'),'bounds':a.get('bounds')} for a in ns if a.get('type')=='Button' and a.get('text')=='处理中...'],
            'syncButtons':[{'text':a.get('text'),'enabled':a.get('enabled'),'id':a.get('id')} for a in ns if a.get('type')=='Button' and a.get('text')=='立即同步'],
            'resultTexts':[a.get('text') for a in ns if a.get('text') and ('正在同步' in a['text'] or '失败' in a['text'])]}

r={'started':datetime.datetime.now().astimezone().isoformat()}
r['before']=state(dump('sync-before',True))
click('立即同步')
r['clickReturned']=datetime.datetime.now().astimezone().isoformat()
r['during']=state(dump('sync-during',True))
r['duringCaptured']=datetime.datetime.now().astimezone().isoformat()
time.sleep(3)
r['duringSecond']=state(dump('sync-during-second',True))
r['duringSecondCaptured']=datetime.datetime.now().astimezone().isoformat()
deadline=time.monotonic()+22
while time.monotonic()<deadline:
    text=(OUT/'webdav-requests.jsonl').read_text(encoding='utf-8') if (OUT/'webdav-requests.jsonl').exists() else ''
    if '"event": "response"' in text:
        time.sleep(2)
        break
    time.sleep(0.5)
r['after']=state(dump('sync-after',True))
r['finished']=datetime.datetime.now().astimezone().isoformat()
r['requests']=[json.loads(x) for x in (OUT/'webdav-requests.jsonl').read_text(encoding='utf-8').splitlines()]
r['observations']={'realFixtureRequestObserved':any(x.get('event')=='request' and x.get('authMatchesFixture') for x in r['requests']),
                   'busyObserved':len(r['during']['busyButtons'])>0,
                   'requiredArkuiLoaderObserved':r['during']['loadingProgressCount']>0 or r['duringSecond']['loadingProgressCount']>0,
                   'busyRestoredAfterError':len(r['after']['syncButtons'])==1 and r['after']['syncButtons'][0]['enabled']=='true',
                   'successfulSyncFlowTested':False}
(OUT/'sync-observations.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))
