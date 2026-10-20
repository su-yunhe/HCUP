from pathlib import Path
from hypium_tests.webdav_fixture import WebDavFixture
import urllib.request, threading, time, json
out = Path('logs/implementation-verification/preparation/fixture-smoke.jsonl')
f = WebDavFixture(out, 0)
gate = f.gate('/smoke')
request = urllib.request.Request(f'http://127.0.0.1:{f.port}/smoke/backup.json.enc', data=b'synthetic-encrypted-body', method='PUT', headers={'Authorization':f.auth})
result=[]
thread=threading.Thread(target=lambda: result.append(urllib.request.urlopen(request,timeout=5).status))
thread.start()
for _ in range(50):
    if f.pending('/smoke'): break
    time.sleep(.02)
assert f.pending('/smoke'), 'Fixture did not retain pending request'
assert not result, 'Gate prematurely released'
gate.set(); thread.join(5)
assert result==[201], result
assert not f.pending('/smoke')
f.close()
rows=[json.loads(line) for line in out.read_text().splitlines()]
assert all('Authorization' not in json.dumps(row) for row in rows)
print('fixture_host_smoke=pass; device_not_used=true')
