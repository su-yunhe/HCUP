"""Loopback WebDAV, genuine local-format fixtures and auditable device evidence."""
from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PROJECT = Path(__file__).resolve().parents[1]
RUN_ID = os.environ.get("VG15_RUN", "prepare")
WORD_PREFIX = "spec15proof" + RUN_ID + "x"
OUT = PROJECT / "logs" / "implementation-validation" / ("run-" + RUN_ID)
OUT.mkdir(parents=True, exist_ok=True)
PORT = 18165
BUNDLE = "io.qzz.weiyu"
DEVICE = "127.0.0.1:5555"
PASSWORD = "Fictional 15! "
SYNC_PASSWORD = "SyncFixture15! "
USERNAME = "spec15-fixture"
ALG = "PBKDF2-HMAC-SHA256/AES-256-CTR/HMAC-SHA256"
LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat()


def event(kind, **data):
    row = {"time": now(), "monotonic": time.monotonic(), "kind": kind, **data}
    with LOCK:
        with (OUT / "timeline.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def encrypt(plain: str, password: str = SYNC_PASSWORD) -> str:
    # Deterministic non-secret fixture IV/salt; never used for actual user data.
    salt = bytes(range(16))
    iv = bytes(range(16, 32))
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 10000, 64)
    ctx = Cipher(algorithms.AES(dk[:32]), modes.CTR(iv)).encryptor()
    ct = ctx.update(plain.encode()) + ctx.finalize()
    b64 = lambda b: base64.b64encode(b).decode()
    return json.dumps({"v": 1, "alg": ALG, "salt": b64(salt), "iv": b64(iv),
                       "ct": b64(ct), "mac": b64(hmac.digest(dk[32:], salt + iv + ct, "sha256"))}, separators=(",", ":"))


def decrypt(payload: str, password: str = SYNC_PASSWORD) -> str:
    obj = json.loads(payload)
    assert obj["v"] == 1 and obj["alg"] == ALG
    salt, iv, ct, mac = (base64.b64decode(obj[k]) for k in ("salt", "iv", "ct", "mac"))
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 10000, 64)
    assert hmac.compare_digest(mac, hmac.digest(dk[32:], salt + iv + ct, "sha256"))
    ctx = Cipher(algorithms.AES(dk[:32]), modes.CTR(iv)).decryptor()
    return (ctx.update(ct) + ctx.finalize()).decode()


def fixture(count=1000):
    words = []
    for i in range(count):
        words.append({"id": 0, "word": f"{WORD_PREFIX}{i:04d}", "status": "NEW",
                      "fsrsState": "", "history": "", "definition": "", "definitionSource": "builtin",
                      "dueDate": 0, "createdAt": 1792051200000, "updatedAt": 1792051200000,
                      "bookId": "", "tags": ["vg-spec15-fictional"], "lapseCount": 0,
                      "leechLevel": 0, "errorTags": [], "suspendUntil": 0})
    return json.dumps({"version": "1.0", "timestamp": 1792051200000, "appVersion": "1.0.0",
                       "words": words, "definitions": [], "userBooks": [],
                       "versionControl": "", "fsrsParamsJson": ""}, separators=(",", ":"))


class ControlledDav:
    def __init__(self):
        self.rows = []
        self.active = set()
        self.exports = []
        self.mode = "missing"
        self.name = "unconfigured"
        self.gate = threading.Event()
        self.gate.set()
        self.hold = False
        self.payload = encrypt(fixture())
        self.empty_payload = encrypt(fixture(0))
        self.server = None

    def configure(self, name, mode="missing", hold=False):
        self.name, self.mode, self.hold = name, mode, hold
        self.gate.clear() if hold else self.gate.set()
        event("server_scenario", name=name, mode=mode, hold=hold, cursor=len(self.rows))
        return len(self.rows)

    def release(self):
        event("server_release", scenario=self.name)
        self.gate.set()

    def start(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def observe(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                expected = "Basic " + base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
                auth = self.headers.get("Authorization") == expected
                req = {"request_id": time.time_ns(), "scenario": owner.name,
                       "mode": owner.mode, "method": self.command, "path": self.path,
                       "auth_matches": auth, "body_length": len(body)}
                row = event("request_begin", **req)
                owner.rows.append(row)
                owner.active.add(req["request_id"])
                backup = self.path.endswith(".enc") or "backup" in self.path.lower()
                if owner.hold and backup and self.command == "HEAD":
                    # Bounded by test watchdog; tests explicitly release, not an artificial UI delay.
                    owner.gate.wait(18)
                mode = req["mode"]
                status, data = 200, b""
                if not auth or mode == "unauthorized":
                    status = 401
                elif mode == "forbidden":
                    status = 403
                elif mode == "server_error":
                    status = 503
                elif mode == "disconnect":
                    self.connection.close()
                    event("response_disconnect", **req)
                    owner.active.discard(req["request_id"])
                    return
                elif self.command == "PUT":
                    status = 201
                    if backup:
                        export = json.loads(decrypt(body.decode()))
                        owner.exports.append(export)
                        (OUT / f"export-{len(owner.exports):02d}.json").write_text(json.dumps(export, ensure_ascii=False), encoding="utf-8")
                        event("actual_export_received", words=len(export["words"]), index=len(owner.exports))
                elif self.command == "DELETE":
                    status = 204
                elif backup and mode == "missing":
                    status = 404
                elif self.command == "GET" and backup:
                    values = {"valid": owner.payload, "empty_business": owner.empty_payload,
                              "empty_plain": encrypt(""), "bad_encrypted": "{broken",
                              "bad_preview": encrypt('{"version":"9.9","words":[]}'),
                              "wrong_password": encrypt(fixture(1), "OtherPassword15!")}
                    data = values.get(mode, owner.payload).encode()
                self.send_response(status)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Content-Type", "application/json")
                self.send_header("Last-Modified", "Thu, 01 Jan 2099 00:00:00 GMT")
                self.send_header("ETag", '"spec15-fixture"')
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(data)
                event("response_end", status=status, **req)
                owner.active.discard(req["request_id"])

            do_HEAD = do_GET = do_PUT = do_DELETE = do_PROPFIND = do_MKCOL = observe

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        event("server_start", bind="127.0.0.1", port=PORT)
        (OUT / "fixture.enc.json").write_text(self.payload, encoding="utf-8")
        (OUT / "fixture-manifest.json").write_text(json.dumps({"format_sources": [
            "entry/src/main/ets/sync/webdav/WebDavCrypto.ets", "entry/src/main/ets/sync/DataExportImport.ets"],
            "words": 1000, "first": WORD_PREFIX + "0000", "last": WORD_PREFIX + "0999",
            "cipher_sha256": hashlib.sha256(self.payload.encode()).hexdigest(),
            "plain_sha256": hashlib.sha256(fixture().encode()).hexdigest(),
            "fake_data_only": True}, indent=2), encoding="utf-8")

    def stop(self):
        self.release()
        self.server.shutdown()
        self.server.server_close()
        event("server_stop")


def hdc(args, name="command", timeout=50, check=True):
    command = [shutil.which("hdc"), "-t", DEVICE, *args]
    started = now()
    result = subprocess.run(command, capture_output=True, timeout=timeout)
    output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    path = OUT / f"{name}-{time.time_ns()}.raw.log"
    path.write_text(output, encoding="utf-8")
    event("command", command=command, started=started, exit_code=result.returncode, raw_log=path.name)
    if check and (result.returncode != 0 or "[Fail]" in output or output.startswith("error:")):
        raise RuntimeError(f"hdc failure: {output}")
    return output


def nodes(tree):
    if isinstance(tree, dict):
        if tree.get("attributes"):
            yield tree["attributes"]
        for child in tree.get("children", []):
            yield from nodes(child)
    elif isinstance(tree, list):
        for child in tree:
            yield from nodes(child)


def snapshot(name, screenshot=True):
    stem = f"{name}-{time.time_ns()}"
    local = OUT / f"{stem}.json"
    remote = f"/data/local/tmp/vg-spec15-impl-{stem}.json"
    hdc(["shell", "uitest", "dumpLayout", "-p", remote], stem + "-dump")
    hdc(["file", "recv", remote, str(local)], stem + "-recv")
    tree = json.loads(local.read_text(encoding="utf-8"))
    if screenshot:
        remote_png = remote[:-5] + ".png"
        hdc(["shell", "uitest", "screenCap", "-p", remote_png], stem + "-screen")
        hdc(["file", "recv", remote_png, str(OUT / f"{stem}.png")], stem + "-png")
    event("snapshot", name=name, file=local.name)
    return list(nodes(tree))


def visible(node):
    return node.get("visible") == "true" and any(int(x) > 0 for x in re.findall(r"-?\d+", node.get("bounds", "")))
