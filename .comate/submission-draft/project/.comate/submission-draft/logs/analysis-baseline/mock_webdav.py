"""Controlled, empty WebDAV observer. Counts requests and always returns 404."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import datetime
import json
import time

LOG = Path(__file__).resolve().parent / "mock-requests.jsonl"


class Observer(BaseHTTPRequestHandler):
    def observe(self):
        # Do not store Authorization or request bodies.
        item = {"time": datetime.now().astimezone().isoformat(), "method": self.command, "path": self.path, "response": 404}
        with LOG.open("a", encoding="utf-8") as output:
            output.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(json.dumps(item, ensure_ascii=False), flush=True)
        # Delay makes request-bound busy UI observable, no local data can be imported.
        time.sleep(8)
        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_HEAD = do_GET = do_PUT = do_POST = do_PROPFIND = do_MKCOL = do_DELETE = do_OPTIONS = observe

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    LOG.touch(exist_ok=True)
    print("Controlled mock WebDAV listening on 127.0.0.1:18988; delayed 404; Authorization excluded", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 18988), Observer).serve_forever()
