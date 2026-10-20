"""Controlled, in-memory WebDAV fixture. Never logs credentials or payloads."""
from __future__ import annotations

import json
import select
import socket
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class WebDavFixture:
    def __init__(self, directory: Path, port: int = 18164):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.log_path = directory / "server.jsonl"
        self.records: list[dict] = []
        self.objects: dict[str, bytes] = {}
        self.pending: dict[int, threading.Event] = {}
        self.lock = threading.RLock()
        self.changed = threading.Condition(self.lock)
        self.gated = True
        self.status_override: int | None = None
        self.disconnect = False
        self.sequence = 0
        self.hold_seconds = 28.0
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args) -> None:
                pass

            def handle_request(self) -> None:
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                with fixture.lock:
                    fixture.sequence += 1
                    number = fixture.sequence
                    gate = threading.Event()
                    fixture.pending[number] = gate
                    gated = fixture.gated
                    override = fixture.status_override
                    disconnect = fixture.disconnect
                    hold_seconds = fixture.hold_seconds
                    fixture.log("request", id=number, method=self.command,
                                path=self.path, bodyBytes=len(body),
                                authPresent=bool(self.headers.get("Authorization")))
                if gated:
                    deadline = time.monotonic() + hold_seconds
                    while not gate.wait(0.1) and time.monotonic() < deadline:
                        try:
                            readable, _, _ = select.select([self.connection], [], [], 0)
                            if readable and not self.connection.recv(1, socket.MSG_PEEK):
                                fixture.log("client_closed", id=number, without_response=True)
                                with fixture.lock:
                                    fixture.pending.pop(number, None)
                                self.close_connection = True
                                return
                        except (ConnectionResetError, ConnectionAbortedError, OSError) as error:
                            fixture.log("client_closed", id=number, without_response=True,
                                        error=type(error).__name__)
                            with fixture.lock:
                                fixture.pending.pop(number, None)
                            self.close_connection = True
                            return
                try:
                    if disconnect:
                        self.close_connection = True
                        self.connection.close()
                        fixture.log("disconnect", id=number)
                        return
                    response = b""
                    status = override or 200
                    if override is None:
                        with fixture.lock:
                            if self.command == "PUT":
                                fixture.objects[self.path] = body
                                status = 201
                            elif self.command == "DELETE":
                                fixture.objects.pop(self.path, None)
                                status = 204
                            elif self.command == "MKCOL":
                                status = 201
                            elif self.command == "GET":
                                if self.path in fixture.objects:
                                    response = fixture.objects[self.path]
                                else:
                                    status = 404
                            elif self.command == "HEAD":
                                status = 404 if "." in self.path.rsplit("/", 1)[-1] and self.path not in fixture.objects else 200
                            elif self.command == "PROPFIND":
                                status = 207
                                response = b'<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"></d:multistatus>'
                            elif self.command != "OPTIONS":
                                status = 405
                    self.send_response(status)
                    self.send_header("Content-Length", str(len(response)))
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("DAV", "1, 2")
                    self.end_headers()
                    if self.command != "HEAD":
                        self.wfile.write(response)
                    self.wfile.flush()
                    fixture.log("response", id=number, status=status,
                                method=self.command, path=self.path)
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError) as error:
                    fixture.log("transport_closed", id=number, error=type(error).__name__)
                finally:
                    with fixture.lock:
                        fixture.pending.pop(number, None)

            do_HEAD = do_GET = do_PUT = do_DELETE = do_MKCOL = do_PROPFIND = do_OPTIONS = handle_request

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.log("listening", port=self.port)

    def log(self, event: str, **values) -> dict:
        with self.lock:
            record = {"utc": utc(), "monotonic_ns": time.monotonic_ns(), "event": event, **values}
            self.records.append(record)
            with self.log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            self.changed.notify_all()
            return record

    def configure(self, *, gated: bool = True, status: int | None = None,
                  disconnect: bool = False, empty: bool = False,
                  hold_seconds: float = 28) -> int:
        with self.lock:
            if empty:
                self.objects.clear()
            self.gated = gated
            self.status_override = status
            self.disconnect = disconnect
            self.hold_seconds = hold_seconds
            self.log("configuration", gated=gated, status=status, disconnect=disconnect,
                     empty=empty, after=self.sequence, hold_seconds=hold_seconds)
            return self.sequence

    def requests(self, after: int = 0) -> list[dict]:
        with self.lock:
            return [r.copy() for r in self.records if r["event"] == "request" and r["id"] > after]

    def wait_request(self, after: int, timeout: float = 15) -> dict:
        deadline = time.monotonic() + timeout
        with self.changed:
            while time.monotonic() < deadline:
                records = self.requests(after)
                if records:
                    return records[0]
                self.changed.wait(max(0, deadline - time.monotonic()))
        raise AssertionError(f"No real WebDAV request after {after} within {timeout}s")

    def release(self, number: int) -> None:
        with self.lock:
            self.pending[number].set()
            self.log("release", id=number)

    def release_all(self) -> None:
        with self.lock:
            self.gated = False
            for gate in self.pending.values():
                gate.set()
            self.log("release_all")

    def close(self) -> None:
        self.release_all()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.log("stopped")
