"""Controlled HTTP/WebDAV fixture. Never logs Authorization or plaintext content."""
from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


class WebDavFixture:
    def __init__(self, output: Path, port: int):
        self.output = output
        self.port = port
        self.events: list[dict] = []
        self.lock = threading.RLock()
        self.next_request_id = 1
        self.gates: dict[str, threading.Event] = {}
        self.head_gates: dict[str, threading.Event] = {}
        self.auth = "Basic " + base64.b64encode(b"vg13-fixture:fixture-pass").decode()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def handle_dav(self):
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                valid = self.headers.get("Authorization") == owner.auth
                upload = self.command == "PUT" and self.path.endswith("backup.json.enc")
                with owner.lock:
                    number = owner.next_request_id
                    owner.next_request_id += 1
                    gate = next((g for p, g in owner.gates.items() if self.path.startswith(p)), None)
                    head_gate = next((g for p, g in owner.head_gates.items() if self.path.startswith(p)), None)
                owner.record(event="received", request_id=number, method=self.command,
                             path=self.path, length=length, sha256=hashlib.sha256(body).hexdigest(),
                             auth_valid=valid, upload=upload, host=self.headers.get("Host"))
                if upload and gate is not None:
                    owner.record(event="pending", request_id=number, path=self.path)
                    gate.wait(75)
                if self.command == "HEAD" and head_gate is not None:
                    owner.record(event="pending", request_id=number, path=self.path)
                    head_gate.wait(75)
                status = 200
                if not valid:
                    status = 401
                elif upload:
                    status = next((code for code in (401, 403, 404, 409, 500)
                                   if f"/status-{code}/" in self.path), 201)
                elif self.command == "GET":
                    status = 404
                try:
                    self.send_response(status)
                    self.send_header("Content-Length", "0")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    owner.record(event="responded", request_id=number, method=self.command,
                                 path=self.path, status=status)
                except (OSError, ConnectionError) as exc:
                    owner.record(event="response_error", request_id=number, path=self.path,
                                 exception=type(exc).__name__)

            do_HEAD = do_GET = do_PUT = do_DELETE = do_MKCOL = do_PROPFIND = handle_dav

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.record(event="server_started", address=f"127.0.0.1:{self.port}")

    def record(self, **data):
        data["utc"] = utc()
        data["monotonic_ns"] = time.monotonic_ns()
        data["port"] = self.port
        with self.lock:
            self.events.append(data)
            with self.output.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(data, ensure_ascii=False) + "\n")

    def gate(self, prefix: str) -> threading.Event:
        with self.lock:
            event = threading.Event()
            self.gates[prefix] = event
            return event

    def matching(self, prefix: str, event: str = "received") -> list[dict]:
        with self.lock:
            return [dict(row) for row in self.events
                    if row["event"] == event and row.get("path", "").startswith(prefix)]

    def gate_head(self, prefix: str) -> threading.Event:
        with self.lock:
            event = threading.Event()
            self.head_gates[prefix] = event
            return event

    def pending(self, prefix: str) -> list[dict]:
        with self.lock:
            ended = {row.get("request_id") for row in self.events
                     if row["event"] in ("responded", "response_error")}
            return [dict(row) for row in self.matching(prefix, "pending")
                    if row["request_id"] not in ended]

    def close(self):
        for gate in self.gates.values():
            gate.set()
        for gate in self.head_gates.values():
            gate.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.record(event="server_stopped")
