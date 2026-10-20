"""Disposable local delay/error WebDAV fixture and UI configurator, no data clearing."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import datetime
import json
import sys
import time
from baseline_ui import OUT, dump, run

PORT=18769
TEST_USER='baseline-vg-spec9'
TEST_PASS='baseline-test-only'

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def handle_probe(self):
        started=datetime.datetime.now().astimezone().isoformat()
        expect='Basic '+base64.b64encode(f'{TEST_USER}:{TEST_PASS}'.encode()).decode()
        row={'event':'request','time':started,'method':self.command,'path':self.path,'authMatchesFixture':self.headers.get('Authorization')==expect,'delaySeconds':12 if self.command=='HEAD' else 0}
        with (OUT/'webdav-requests.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps(row)+'\n')
        n=int(self.headers.get('Content-Length','0'))
        if n: self.rfile.read(n)
        if self.command=='HEAD': time.sleep(12)
        self.send_response(403)
        self.send_header('Content-Length','0')
        self.end_headers()
        with (OUT/'webdav-requests.jsonl').open('a',encoding='utf-8') as f: f.write(json.dumps({'event':'response','time':datetime.datetime.now().astimezone().isoformat(),'method':self.command,'path':self.path,'status':403})+'\n')
    do_HEAD=handle_probe
    do_GET=handle_probe
    do_PUT=handle_probe
    do_POST=handle_probe
    do_MKCOL=handle_probe
    do_DELETE=handle_probe

if sys.argv[1]=='serve':
    print(f'Delay/error fixture listening on 127.0.0.1:{PORT}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
elif sys.argv[1] in ['configure','finish-config']:
    from hypium import BY,UiDriver
    d=UiDriver.connect(device_sn='127.0.0.1:5555')
    fields=[('https://dav.example.com/dav/',f'http://127.0.0.1:{PORT}'),('username',TEST_USER),('password',TEST_PASS),('sync password','baseline-sync-only'),('/weiyu_sync','/vg-spec9-round01')]
    if sys.argv[1]=='finish-config': fields=fields[-1:]
    for hint,value in fields:
        print(f'Filling fixture input {hint!r}',flush=True)
        d.input_text(BY.type('TextInput').hint(hint),value)
        d.wait(0.2)
        run('shell','uitest','uiInput','keyEvent','Back')
    dump('webdav-test-config',True)
