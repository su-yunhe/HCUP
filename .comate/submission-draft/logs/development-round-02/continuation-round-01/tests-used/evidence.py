"""Audit helpers. These touch only vg-spec1 files and its assigned emulator."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import shutil
import sqlite3
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = "io.qzz.weiyu"
DEVICE = os.environ.get("VG_TEST_DEVICE", "127.0.0.1:11235")
PORT = 28762
DB_DIR = f"/data/app/el2/100/database/{BUNDLE}/entry/rdb"
PREFS = f"/data/app/el2/100/base/{BUNDLE}/haps/entry/preferences/webdav_state_store"
BUSINESS_TABLES = ("words", "word_identities", "review_events", "definitions",
                   "user_word_books", "user_word_book_words", "user_notebook_words",
                   "system_word_book_words", "texts")


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_fingerprint() -> dict[str, str]:
    """No histories or other projects; include untracked production files."""
    paths = []
    for folder in ("entry/src/main", "AppScope", "hvigor"):
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file())
    paths.extend(ROOT / p for p in ("build-profile.json5", "oh-package.json5",
                 "oh-package-lock.json5", "hvigorfile.ts", "entry/build-profile.json5",
                 "entry/hvigorfile.ts", "entry/oh-package.json5"))
    return {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in sorted(set(paths)) if p.is_file()}


class Evidence:
    def __init__(self, folder: Path, device: str = DEVICE):
        self.folder = folder.resolve()
        if not self.folder.is_relative_to(ROOT):
            raise ValueError("Evidence must remain inside vg-spec1")
        self.folder.mkdir(parents=True, exist_ok=True)
        self.device = device

    def command(self, args: list[str], timeout: float = 30, check: bool = True):
        start = utc()
        proc = subprocess.run(args, cwd=ROOT, capture_output=True, timeout=timeout)
        record = {"started_at": start, "finished_at": utc(), "argv": args,
                  "exit_code": proc.returncode,
                  "stdout": proc.stdout.decode("utf-8", errors="replace"),
                  "stderr": proc.stderr.decode("utf-8", errors="replace")}
        with (self.folder / "commands.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        text = record["stdout"] + record["stderr"]
        if check and (proc.returncode or "[Fail]" in text or "Permission denied" in text):
            raise RuntimeError(f"Command failed: {args!r}: {text}")
        return record

    def hdc(self, *args: str, **kwargs):
        return self.command([shutil.which("hdc") or "hdc", "-t", self.device, *args], **kwargs)

    def receive(self, remote: str, path: Path, optional: bool = False) -> bool:
        path.parent.mkdir(parents=True, exist_ok=True)
        result = self.hdc("file", "recv", remote, str(path), check=not optional)
        return path.exists() and "FileTransfer finish" in result["stdout"]

    def screen(self, name: str) -> dict:
        for ext, operation in (("json", "dumpLayout"), ("png", "screenCap")):
            remote = f"/data/local/tmp/vgspec1-dev-{name}.{ext}"
            self.hdc("shell", "uitest", operation, "-p", remote)
            self.receive(remote, self.folder / f"{name}.{ext}")
        return json.loads((self.folder / f"{name}.json").read_text(encoding="utf-8"))

    def db_snapshot(self, name: str) -> dict:
        folder = self.folder / name
        folder.mkdir(parents=True, exist_ok=True)
        # Original copies retained before any sqlite3 replay/checkpoint.
        for suffix in ("", "-wal", "-shm", "-dwr", "-compare"):
            self.receive(f"{DB_DIR}/vignette.db{suffix}", folder / f"raw.db{suffix}", optional=bool(suffix))
        self.receive(PREFS, folder / "webdav_state_store.xml")
        raw_hashes = {p.name: digest(p.read_bytes()) for p in folder.iterdir() if p.is_file()}
        for suffix in ("", "-wal", "-shm"):
            p = folder / f"raw.db{suffix}"
            if p.exists():
                shutil.copyfile(p, folder / f"analysis.db{suffix}")
        con = sqlite3.connect(folder / "analysis.db")
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise AssertionError(f"Inconsistent SQLite snapshot: {integrity}")
        tables = {}
        for table in BUSINESS_TABLES:
            columns = [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]
            if not columns:
                raise AssertionError(f"Missing schema table {table}")
            rows = [dict(zip(columns, r)) for r in con.execute(f'SELECT * FROM "{table}"')]
            tables[table] = sorted(rows, key=lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
        con.close()
        result = {"captured_at": utc(), "integrity_check": integrity,
                  "raw_sha256": raw_hashes, "tables": tables,
                  "business_sha256": digest(json.dumps(tables, sort_keys=True, ensure_ascii=False).encode())}
        write_json(folder / "semantic.json", result)
        return result


def flatten(tree: dict) -> list[dict]:
    result = [tree.get("attributes", {})]
    for child in tree.get("children", []):
        result.extend(flatten(child))
    return result


def read_preferences(path: Path) -> dict[str, str]:
    return {node.attrib.get("key", ""): node.text or "" for node in ET.parse(path).getroot()}


def cloud_backup(password: str = "vg_spec1_sync_1234") -> tuple[dict, bytes]:
    """Fixture format grounded in this task's WebDavCrypto/DataExportImport."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    timestamp = 1700000000000
    state = json.dumps({"difficulty": 9, "stability": 23, "retrievability": .4, "reps": 8, "lapses": 3})
    definition = json.dumps({"word": "vgspec1_conflict", "phonetic": "", "pos": "n.",
        "contextMeaning": "CLOUD_CONFLICT_VALUE", "commonMeanings": [], "source": "local",
        "phrases": [], "examples": [], "frequency": 0, "examTags": []})
    word = {"id": 70002, "word": "vgspec1_conflict", "status": "KNOWN", "fsrsState": state,
            "history": "[]", "definition": definition, "definitionSource": "local",
            "dueDate": timestamp + 86400000, "createdAt": timestamp, "updatedAt": timestamp + 1000,
            "bookId": "user_vgspec1", "tags": ["CLOUD_CONFLICT_VALUE"], "lapseCount": 3,
            "leechLevel": 1, "errorTags": ["cloud"], "suspendUntil": 0}
    plain = {"version": "1.0", "timestamp": timestamp, "appVersion": "1.0.0", "words": [word],
             "definitions": [], "userBooks": [], "versionControl": "", "fsrsParamsJson": ""}
    salt = bytes.fromhex("00112233445566778899aabbccddeeff")
    iv = bytes.fromhex("ffeeddccbbaa99887766554433221100")
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 10000, 64)
    encryptor = Cipher(algorithms.AES(key[:32]), modes.CTR(iv)).encryptor()
    ct = encryptor.update(json.dumps(plain, ensure_ascii=False).encode()) + encryptor.finalize()
    payload = {"v": 1, "alg": "PBKDF2-HMAC-SHA256/AES-256-CTR/HMAC-SHA256"}
    for name, data in (("salt", salt), ("iv", iv), ("ct", ct),
                       ("mac", hmac.new(key[32:], salt + iv + ct, hashlib.sha256).digest())):
        payload[name] = base64.b64encode(data).decode()
    return plain, json.dumps(payload).encode()


def local_fixture() -> dict:
    cloud, _ = cloud_backup()
    word = json.loads(json.dumps(cloud["words"][0]))
    word.update(status="REVIEW", tags=["LOCAL_CONFLICT_VALUE"], lapseCount=1,
                leechLevel=0, errorTags=["local"], updatedAt=1700000000000)
    state = json.dumps({"difficulty": 4, "stability": 7, "retrievability": .8, "reps": 5, "lapses": 1})
    word["fsrsState"] = state
    word["history"] = json.dumps([{"timestamp": 1792220000000, "rating": 3,
        "stateBefore": state, "stateAfter": state, "scheduledDays": 7}])
    definition = json.loads(word["definition"])
    definition["contextMeaning"] = "LOCAL_CONFLICT_VALUE"
    word["definition"] = json.dumps(definition, ensure_ascii=False)
    unique = json.loads(json.dumps(word))
    unique.update(id=70001, word="vgspec1_localonly", tags=["LOCAL_ONLY_RECORD"])
    definition.update(word="vgspec1_localonly", contextMeaning="LOCAL_ONLY_RECORD")
    unique["definition"] = json.dumps(definition, ensure_ascii=False)
    cloud["words"] = [unique, word]
    cloud["userBooks"] = [{"id": "user_vgspec1", "name": "VGSpec1本地哨兵词书",
        "description": "LOCAL_ONLY_BOOK", "category": "其他", "difficulty": "初级",
        "coverColor": '["#a8edea", "#fed6e3"]', "icon": "📓",
        "createdAt": 1700000000000, "updatedAt": 1700000000000}]
    return cloud


class WebDavProbe:
    def __init__(self, folder: Path, port: int = PORT):
        self.folder, self.port = folder, port
        folder.mkdir(parents=True, exist_ok=True)
        self.mode = "success"
        self.requests: list[dict] = []
        self.lock = threading.Lock()
        plain, payload = cloud_backup()
        self.files = {"/weiyu_vignette/backup.json.enc": payload}
        write_json(folder / "cloud-plain.json", plain)
        (folder / "cloud-backup.json.enc").write_bytes(payload)
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, fmt, *args):
                pass

            def process(self):
                started = utc()
                path = urlsplit(self.path).path.rstrip("/") or "/"
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                mode = owner.mode
                record = {"started_at": started, "finished_at": None, "method": self.command,
                          "path": path, "request_bytes": len(body), "body_sha256": digest(body),
                          "status": None, "response_bytes": None, "mode": mode}
                with owner.lock:
                    owner.requests.append(record)
                    with (folder / "requests-started.jsonl").open("a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                status, response = 200, b""
                if mode == "failure":
                    status = 503
                elif mode == "delay":
                    time.sleep(3)  # Facility stress condition, not a product timing requirement.
                    status = 503
                elif self.command == "HEAD":
                    status = 200 if path in ("/", "/weiyu_vignette") or (path in owner.files and mode != "no-backup") else 404
                elif self.command == "GET":
                    status = 503 if mode == "download-failure" else (200 if path in owner.files and mode != "empty" else 404)
                    response = owner.files.get(path, b"") if status == 200 else b""
                elif self.command == "PUT":
                    owner.files[path] = body
                    status = 201
                elif self.command == "DELETE":
                    owner.files.pop(path, None)
                    status = 204
                elif self.command == "MKCOL":
                    status = 201
                elif self.command == "PROPFIND":
                    status = 207
                    response = b'<?xml version="1.0"?><d:multistatus xmlns:d="DAV:"/>'
                else:
                    status = 405
                with owner.lock:
                    record.update(finished_at=utc(), status=status, response_bytes=len(response))
                    with (folder / "requests.jsonl").open("a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                self.send_response(status)
                self.send_header("Content-Length", str(len(response)))
                self.send_header("ETag", '"vgspec1-controlled"')
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(response)

            do_HEAD = do_GET = do_PUT = do_DELETE = do_MKCOL = do_PROPFIND = process

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def window(self, start: int, name: str, started_at: str) -> list[dict]:
        with self.lock:
            requests = list(self.requests[start:])
        write_json(self.folder / f"window-{name}.json", {
            "started_at": started_at, "finished_at": utc(), "start_index": start,
            "end_index": start + len(requests), "requests": requests,
            "total": len(requests), "downloads": sum(r["method"] == "GET" for r in requests)})
        return requests
