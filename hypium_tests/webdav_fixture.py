"""Controlled WebDAV endpoint with an append-only TCP/HTTP/UI event ledger.

Only test credentials are accepted. No authorization header is persisted. Test
control is through Python methods, never through the observed HTTP listener.
The OS allocates a new loopback port for each instance; the old baseline server
is neither contacted nor reused. This module does not connect to any device.
"""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import threading
import time
from urllib.parse import urlsplit


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._events: list[dict] = []

    def add(self, event: str, **fields) -> dict:
        with self._lock:
            item = {
                "seq": len(self._events) + 1,
                "utc": datetime.now(timezone.utc).isoformat(),
                "monotonic_ns": time.monotonic_ns(),
                "event": event,
                **fields,
            }
            self._events.append(item)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(item, ensure_ascii=False) + "\n")
            return item

    def since(self, seq: int = 0) -> list[dict]:
        with self._lock:
            return [dict(item) for item in self._events if item["seq"] > seq]


class _ObservedServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def get_request(self):
        sock, address = super().get_request()
        owner = self.owner
        with owner._lock:
            connection = owner.ledger.add("tcp_accept", remote_address=address[0],
                                          remote_port=address[1])
            owner._sockets[sock] = connection["seq"]
        return sock, address

    def shutdown_request(self, request):
        with self.owner._lock:
            connection_id = self.owner._sockets.pop(request, None)
        super().shutdown_request(request)
        self.owner.ledger.add("tcp_close", connection_id=connection_id)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, _format, *args):
        # The raw ledger is the sole request log. Never emit Basic credentials.
        pass

    def __getattr__(self, name):
        if name.startswith("do_"):
            return self._dispatch
        raise AttributeError(name)

    def _dispatch(self):
        owner = self.server.owner
        with owner._lock:
            auth_ok = self.headers.get("Authorization", "") == owner._expected_auth
            request = owner.ledger.add(
                "http_request", connection_id=owner._sockets.get(self.connection),
                method=self.command, path=self.path,
                host=self.headers.get("Host", ""), authorization_matches=auth_ok,
                content_length=int(self.headers.get("Content-Length", "0")),
                mode=owner.mode,
            )
            owner.active_requests += 1
        status = 500
        response_bytes = 0
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b""
            path = urlsplit(self.path).path
            status, response = owner.respond(self.command, path, body, auth_ok)
            if owner.delay_seconds:
                owner._closing.wait(owner.delay_seconds)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            # Intentionally omit Last-Modified: a same-device preparation upload
            # must remain retrievable, rather than be skipped as not newer.
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(response)
                response_bytes = len(response)
        except (OSError, ValueError) as error:
            owner.ledger.add("http_response_error", request_id=request["seq"],
                             error_type=type(error).__name__, message=str(error))
        finally:
            owner.ledger.add("http_response", request_id=request["seq"],
                             status=status, body_bytes=response_bytes)
            with owner._lock:
                owner.active_requests -= 1


class WebDavFixture:
    username = "vg_spec7_do"
    password = "vg7-do-fixture-password"
    sync_password = "vg7-do-fixture-sync-password"
    base_path = "/vg-spec7-do-dav"
    remote_root = "/vg_spec7_do"

    def __init__(self, evidence_dir: Path):
        self.evidence_dir = Path(evidence_dir)
        self.ledger = Ledger(self.evidence_dir / "endpoint-events.jsonl")
        self._lock = threading.RLock()
        self._closing = threading.Event()
        self._sockets: dict[socket.socket, int] = {}
        self._files: dict[str, bytes] = {}
        self.active_requests = 0
        self.mode = "empty"
        self.delay_seconds = 0.0
        encoded = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        self._expected_auth = "Basic " + encoded
        self._server = _ObservedServer(("127.0.0.1", 0), _Handler)
        self._server.owner = self
        self.port = self._server.server_port
        self.endpoint = f"http://127.0.0.1:{self.port}{self.base_path}/"
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        name="vg-spec7-do-fixture", daemon=True)
        self._thread.start()
        self.ledger.add("fixture_listen", host="127.0.0.1", port=self.port,
                        endpoint=self.endpoint, control="in_process_only")

    def mark(self, label: str, **fields) -> int:
        return self.ledger.add("ui_event", label=label, **fields)["seq"]

    def set_mode(self, mode: str, delay_seconds: float = 0) -> None:
        if mode not in {"empty", "stored", "unauthorized", "server_error", "invalid_encrypted"}:
            raise ValueError(mode)
        with self._lock:
            self.mode, self.delay_seconds = mode, delay_seconds
        self.ledger.add("fixture_mode", mode=mode, delay_seconds=delay_seconds)

    def respond(self, method: str, path: str, body: bytes, auth_ok: bool):
        with self._lock:
            if not auth_ok or self.mode == "unauthorized":
                return 401, b"fixture unauthorized"
            if not path.startswith(self.base_path + "/"):
                return 404, b"outside configured endpoint"
            if self.mode == "server_error":
                return 500, b"fixture controlled failure"
            is_backup = path.endswith("/backup.json.enc")
            if method == "PUT":
                self._files[path] = body
                if is_backup:
                    name = "uploaded-backup-" + hashlib.sha256(body).hexdigest()[:12] + ".enc"
                    (self.evidence_dir / name).write_bytes(body)
                    self.ledger.add("backup_uploaded", path=path, bytes=len(body),
                                    sha256=hashlib.sha256(body).hexdigest(), artifact=name)
                return 201, b""
            if method == "DELETE":
                self._files.pop(path, None)
                return 204, b""
            if method in {"MKCOL", "OPTIONS"}:
                return 200, b""
            if method in {"HEAD", "GET"}:
                if is_backup:
                    if self.mode == "invalid_encrypted":
                        return 200, b"controlled-invalid-encrypted-backup"
                    if self.mode != "stored" or path not in self._files:
                        return 404, b""
                return 200, self._files.get(path, b"")
            if method == "PROPFIND":
                return 207, b'<?xml version="1.0"?><multistatus xmlns="DAV:"/>'
            return 501, b"fixture unsupported method"

    def observed_since(self, seq: int) -> list[dict]:
        return [event for event in self.ledger.since(seq)
                if event["event"] in {"tcp_accept", "http_request"}]

    def close(self) -> None:
        if self._closing.is_set():
            return
        self.ledger.add("fixture_shutdown_requested")
        self._closing.set()
        self._server.shutdown()
        with self._lock:
            sockets = list(self._sockets)
        for sock in sockets:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        self._server.server_close()
        self._thread.join(timeout=5)
        self.ledger.add("fixture_closed", serving_thread_alive=self._thread.is_alive())

