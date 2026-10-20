from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime, timezone
import base64, hashlib, json, threading, time
ROOT = Path(__file__).resolve().parent
LOCK = threading.Lock()
AUTH = 'Basic ' + base64.b64encode(b'vg13-fixture:fixture-pass').decode()
def record(**data):
    data['utc'] = datetime.now(timezone.utc).isoformat()
    with LOCK, (ROOT / 'fixture-requests.jsonl').open('a', encoding='utf8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
class Dav(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def handle_request(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        allowed = self.headers.get('Authorization') == AUTH
        delay = 8 if self.command == 'PUT' and self.path.endswith('backup.json.enc') else 0
        record(event='received', method=self.command, path=self.path, length=len(body), sha256=hashlib.sha256(body).hexdigest(), auth_valid=allowed, delay_seconds=delay)
        time.sleep(delay)
        status = (404 if self.command == 'GET' else 201 if self.command == 'PUT' else 200) if allowed else 401
        self.send_response(status)
        self.send_header('Content-Length', '0')
        self.send_header('Connection', 'close')
        self.end_headers()
        record(event='responded', method=self.command, path=self.path, status=status)
    do_HEAD = do_GET = do_PUT = do_DELETE = handle_request
    def log_message(self, *_): pass
record(event='server_started', address='127.0.0.1:18173')
try:
    ThreadingHTTPServer(('127.0.0.1', 18173), Dav).serve_forever()
finally:
    record(event='server_stopped')
