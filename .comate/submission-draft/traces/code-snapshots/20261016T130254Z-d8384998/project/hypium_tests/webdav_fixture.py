"""Loopback-only WebDAV fixture that stores actual application PUT bodies.

Every request and response is recorded with wall and monotonic timestamps.
The fixture never fabricates application UI state or bypasses its HTTP client.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit


@dataclass
class Scenario:
    root: str
    mode: str = "success"
    gate_first: bool = True
    delay: float = 0.1
    redirect_hops: int = 0
    files: dict[str, bytes] = field(default_factory=dict)
    directories: set[str] = field(default_factory=set)
    active: dict[int, dict] = field(default_factory=dict)
    requests: list[dict] = field(default_factory=list)
    responses: list[dict] = field(default_factory=list)
    release: threading.Event = field(default_factory=threading.Event)
    gate_used: bool = False


class WebDavFixture:
    USER = "vg-spec9-local-verification"
    PASSWORD = "synthetic-test-password"
    SYNC_PASSWORD = "vg-spec9-synthetic-aes-password"

    def __init__(self, output: Path, port: int = 18769):
        self.output = output
        output.mkdir(parents=True, exist_ok=True)
        self.port = port
        self.scenarios: dict[str, Scenario] = {}
        self.lock = threading.RLock()
        self.sequence = 0
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *_args):
                pass

            def handle_webdav(self):
                owner.handle(self)

            do_HEAD = handle_webdav
            do_GET = handle_webdav
            do_PUT = handle_webdav
            do_DELETE = handle_webdav
            do_MKCOL = handle_webdav
            do_PROPFIND = handle_webdav

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.port = self.server.server_address[1]
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()
        self.log({"event": "fixture_started", "bind": "127.0.0.1", "port": self.port})

    def close(self):
        for scenario in self.scenarios.values():
            scenario.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        self.log({"event": "fixture_stopped"})

    def create(self, label: str, root: str | None = None, **kwargs) -> Scenario:
        root = root or f"/vg-spec9-{label}-{time.time_ns()}"
        scenario = Scenario(root, **kwargs)
        if scenario.mode != "long_tree":
            scenario.directories.add(root)
        with self.lock:
            self.scenarios[root] = scenario
        self.log({"event": "scenario_created", "root": root, "mode": scenario.mode,
                  "delay": scenario.delay, "redirect_hops": scenario.redirect_hops})
        return scenario

    def log(self, row: dict):
        row = {"epoch": time.time(), "monotonic": time.monotonic(), **row}
        with self.lock:
            with (self.output / "webdav-requests.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row

    def handle(self, handler: BaseHTTPRequestHandler):
        parsed = urlsplit(handler.path)
        with self.lock:
            scenario = next((s for root, s in self.scenarios.items()
                             if parsed.path == root or parsed.path.startswith(root + "/") or
                             (s.mode == "long_tree" and parsed.path != "/" and
                              (root.startswith(parsed.path.rstrip("/") + "/") or
                               (parsed.path.endswith("/.keep") and
                                root.startswith(parsed.path.rsplit("/", 1)[0] + "/"))))), None)
            self.sequence += 1
            request_id = self.sequence
        length = int(handler.headers.get("Content-Length", "0"))
        body = handler.rfile.read(length) if length else b""
        expected_auth = "Basic " + base64.b64encode(f"{self.USER}:{self.PASSWORD}".encode()).decode()
        auth_ok = handler.headers.get("Authorization") == expected_auth
        request = self.log({"event": "request", "request_id": request_id,
                            "method": handler.command, "path": handler.path,
                            "root": scenario.root if scenario else None,
                            "auth_matches_fixture": auth_ok, "body_length": len(body),
                            "body_sha256": hashlib.sha256(body).hexdigest(),
                            "content_type": handler.headers.get("Content-Type", "")})
        if scenario:
            with self.lock:
                scenario.requests.append(request)
                scenario.active[request_id] = request
        status, reply, headers = 404, b"", {}
        try:
            if not auth_ok:
                status = 401
                headers["WWW-Authenticate"] = 'Basic realm="vg-spec9-local"'
            elif scenario:
                should_gate = False
                with self.lock:
                    if scenario.gate_first and not scenario.gate_used:
                        scenario.gate_used = True
                        should_gate = True
                if should_gate:
                    # Bounded below the production client's 20 s read timeout.
                    scenario.release.wait(timeout=min(16, max(0, 18 - scenario.delay)))
                time.sleep(scenario.delay)
                hop = int(parse_qs(parsed.query).get("vg_hop", ["0"])[0])
                if hop < scenario.redirect_hops:
                    status = 307
                    headers["Location"] = (f"http://127.0.0.1:{self.port}{parsed.path}?" +
                                           urlencode({"vg_hop": hop + 1}))
                elif scenario.mode in {"forbidden", "server_error"}:
                    status = 403 if scenario.mode == "forbidden" else 500
                elif handler.command == "HEAD":
                    status = 200 if parsed.path in scenario.directories or parsed.path in scenario.files else 404
                elif handler.command == "GET":
                    status = 200 if parsed.path in scenario.files else 404
                    reply = scenario.files.get(parsed.path, b"")
                elif handler.command == "PUT":
                    status = 204 if parsed.path in scenario.files else 201
                    scenario.files[parsed.path] = body
                    if parsed.path.endswith("/.keep"):
                        scenario.directories.add(parsed.path.rsplit("/", 1)[0])
                    (self.output / f"put-{request_id}.bin").write_bytes(body)
                elif handler.command == "DELETE":
                    scenario.files.pop(parsed.path, None)
                    status = 204
                elif handler.command == "MKCOL":
                    status = 201
                headers["ETag"] = '"' + hashlib.sha256(reply).hexdigest() + '"'
            handler.send_response(status)
            handler.send_header("Content-Length", str(len(reply)))
            handler.send_header("Content-Type", "application/octet-stream")
            for key, value in headers.items():
                handler.send_header(key, value)
            handler.end_headers()
            if handler.command != "HEAD" and reply:
                handler.wfile.write(reply)
            handler.wfile.flush()
            response = self.log({"event": "response", "request_id": request_id,
                                 "root": scenario.root if scenario else None,
                                 "method": handler.command, "path": handler.path, "status": status,
                                 "body_length": len(reply)})
            if scenario:
                with self.lock:
                    scenario.responses.append(response)
        except (BrokenPipeError, ConnectionResetError) as error:
            self.log({"event": "connection_closed", "request_id": request_id,
                      "error": type(error).__name__})
        finally:
            if scenario:
                with self.lock:
                    scenario.active.pop(request_id, None)
