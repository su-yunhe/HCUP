"""Loopback-only, non-restoring WebDAV observation endpoint for vg-spec15."""
import base64
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parent
EXPECTED_AUTH = "Basic " + base64.b64encode(b"spec15-user:BaselineOnly15!").decode("ascii")


def log(kind, **data):
    row = {"time": datetime.now(timezone.utc).isoformat(), "kind": kind, **data}
    with (ROOT / "server-requests.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False), flush=True)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def observe(self):
        state = json.loads((ROOT / "server-state.json").read_text(encoding="utf-8-sig"))
        phase = state["phase"]
        delay = state["delay_seconds"]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        request_id = str(time.time_ns())
        auth_matches = self.headers.get("Authorization") == EXPECTED_AUTH
        log("request_begin", request_id=request_id, phase=phase,
            peer=self.client_address, method=self.command, path=self.path,
            headers={k: v if k.lower() != "authorization" else "<one-time-fictional-basic-auth>"
                     for k, v in self.headers.items()},
            auth_matches=auth_matches, body_length=len(body), delay_seconds=delay)
        time.sleep(delay)
        if not auth_matches:
            status = 401
        elif self.command == "HEAD" and self.path.rstrip("/") == "/baseline-spec15":
            status = 200
        else:
            status = 404
        payload = b"vg-spec15 controlled endpoint: no backup data"
        self.send_response(status)
        self.send_header("Content-Length", str(len(payload) if self.command != "HEAD" else 0))
        self.send_header("Content-Type", "text/plain")
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)
        log("response", request_id=request_id, phase=phase, status=status,
            method=self.command, path=self.path)

    do_HEAD = observe
    do_GET = observe
    do_PUT = observe
    do_DELETE = observe
    do_PROPFIND = observe
    do_MKCOL = observe

    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 18085), Handler)
server.timeout = 1
log("server_start", address="127.0.0.1", port=18085, no_backup_data=True)
while not (ROOT / "server-stop.flag").exists():
    server.handle_request()
server.server_close()
log("server_stop")
