"""Evidence and real HTTP observer, scoped to vg-spec8. No device work on import."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = Path(os.environ.get("VG_SPEC8_LOG_DIR", str(ROOT / "logs/implementation-validation/current"))).resolve()
BUNDLE = "io.qzz.weiyu"
PORT = int(os.environ.get("VG_SPEC8_MOCK_PORT", "18989"))
CONFIG = {
    "webdav_endpoint_input": f"http://127.0.0.1:{PORT}/dav/",
    "webdav_username_input": "vg_spec8_verification",
    "webdav_password_input": "local-observer-password",
    "webdav_sync_password_input": "local-sync-password",
    "webdav_root_input": "/vg_spec8_verification",
}
_write_lock = threading.RLock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name: str, value) -> None:
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def record(action: str, **values) -> dict:
    item = {"time": now(), "monotonic": time.monotonic(), "action": action, **values}
    with _write_lock:
        LOG.mkdir(parents=True, exist_ok=True)
        with (LOG / "device-actions.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(json.dumps(item, ensure_ascii=False), flush=True)
    return item


def source_fingerprint() -> list[dict]:
    paths = []
    for folder in [ROOT / "entry/src", ROOT / "AppScope"]:
        if folder.exists():
            paths.extend(path for path in folder.rglob("*") if path.is_file())
    for relative in ["build-profile.json5", "oh-package.json5", "oh-package-lock.json5", "hvigorfile.ts",
                     "entry/build-profile.json5", "entry/oh-package.json5", "entry/hvigorfile.ts",
                     "hvigor/hvigor-config.json5", "code-linter.json5"]:
        path = ROOT / relative
        if path.is_file():
            paths.append(path)
    return [{"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in sorted(set(paths))]


def assert_release() -> dict:
    if os.environ.get("VG_SPEC8_RELEASED") != "yes":
        raise RuntimeError("主 Agent 尚未释放源码锁和共享设备；不得运行设备自测")
    if ROOT != Path("D:/HCUP/vg-spec8").resolve():
        raise RuntimeError("Unexpected project root")
    approved = {"spec/acceptance.md": "69849e82f4402b87fd1a49cd53631b4a42154d24f3a9fbbc653c2786a98ef057",
                "spec/baseline-notes.md": "e72636ed63581533a85d90a4040814a85b33eb3233cb694b2805344b73690556"}
    for relative, expected_hash in approved.items():
        if sha256(ROOT / relative) != expected_hash:
            raise RuntimeError(f"批准输入已变化: {relative}")
    manifest_path = LOG / "installation-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("缺少本轮独立构建/安装证据 installation-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("buildExitCode") != 0 or manifest.get("installExitCode") != 0:
        raise RuntimeError("本轮构建或安装未通过")
    if manifest.get("installSemanticSuccess") is not True:
        raise RuntimeError("安装语义/包更新时间未证实成功；不能只看 hdc 退出码")
    if sha256(Path(manifest["hapPath"])) != manifest["hapSha256"]:
        raise RuntimeError("本轮安装产物哈希已变化")
    expected = json.loads((LOG / "source-fingerprint-before.json").read_text(encoding="utf-8-sig"))
    if source_fingerprint() != expected:
        raise RuntimeError("生产源码/构建输入指纹变化；受影响证据无效，须重新冻结构建安装")
    return manifest


def hdc(device: str, *arguments: str, timeout: float = 30, check: bool = True) -> str:
    from harness.device import find_hdc
    command = [find_hdc(), "-t", device, *arguments]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    semantic_failure = bool(re.search(r"\[Fail\]|\[F\]\[", result.stdout + result.stderr, re.IGNORECASE))
    record("hdc", command=command, exit_code=result.returncode, semantic_failure=semantic_failure, stdout=result.stdout, stderr=result.stderr)
    if check and (result.returncode or semantic_failure):
        raise RuntimeError(f"hdc exit={result.returncode}: {arguments}")
    return result.stdout


def snapshot(device: str, name: str) -> list[dict]:
    for suffix, command in [("json", "dumpLayout"), ("png", "screenCap")]:
        remote = f"/data/local/tmp/vg-spec8-validation-{name}.{suffix}"
        hdc(device, "shell", "uitest", command, "-p", remote)
        hdc(device, "file", "recv", remote, str(LOG / f"{name}.{suffix}"))
    data = json.loads((LOG / f"{name}.json").read_text(encoding="utf-8-sig"))
    return list(walk_tree(data))


def walk_tree(node):
    if isinstance(node, list):
        for child in node:
            yield from walk_tree(child)
    elif isinstance(node, dict):
        if "attributes" in node:
            yield node["attributes"]
        for key in ["children", "windows"]:
            for child in node.get(key, []):
                yield from walk_tree(child)


def learning_snapshot(device: str, name: str) -> dict:
    """Copy only this app's DB while its process is stopped; do not mutate device data."""
    output = hdc(device, "shell", "find", f"/data/app/el2/100/database/{BUNDLE}", "-name", "vignette.db")
    matches = [line.strip() for line in output.splitlines()
               if line.strip().startswith(f"/data/app/el2/100/database/{BUNDLE}/") and line.strip().endswith("/vignette.db")]
    if len(matches) != 1:
        raise RuntimeError(f"本题数据库只读快照前置阻断: {matches}")
    directory = LOG / name
    directory.mkdir(parents=True, exist_ok=True)
    remote = matches[0]
    for suffix in ["", "-wal", "-shm"]:
        hdc(device, "file", "recv", remote + suffix, str(directory / ("vignette.db" + suffix)), check=suffix == "")
    path = directory / "vignette.db"
    tables = ["words", "word_identities", "definitions", "review_events", "user_notebook_words",
              "user_word_books", "user_word_book_words", "system_word_book_words"]
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as connection:
        result = {}
        present = {row[0] for row in connection.execute("select name from sqlite_master where type='table'")}
        for table in tables:
            if table not in present:
                continue
            cursor = connection.execute(f'SELECT * FROM "{table}"')
            columns = [column[0] for column in cursor.description]
            rows = sorted([list(row) for row in cursor.fetchall()], key=lambda row: json.dumps(row, ensure_ascii=False))
            result[table] = {"columns": columns, "rows": rows}
    write_json(name + "-entities.json", result)
    record("learning_snapshot", name=name, tables={key: len(value["rows"]) for key, value in result.items()})
    return result


class MockDav:
    """All HTTP methods are logged. Empty mode has no cloud backup; PUTs can be replayed."""
    def __init__(self, port: int = PORT):
        self.port = port
        self.events = []
        self.files: dict[str, bytes] = {}
        self.mode = "empty"
        self.lock = threading.RLock()
        observer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def observe(self):
                count = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(count) if count else b""
                with observer.lock:
                    exists = self.path in observer.files
                    is_file = "." in self.path.rsplit("/", 1)[-1]
                    status, output = 404, b""
                    if self.command == "PUT":
                        observer.files[self.path] = body
                        status = 201
                    elif self.command == "DELETE":
                        observer.files.pop(self.path, None)
                        status = 204
                    elif self.command in ["HEAD", "GET"] and not is_file:
                        status = 200
                    elif self.command in ["HEAD", "GET"] and observer.mode == "replay" and exists:
                        status, output = 200, observer.files[self.path]
                    elif self.command == "MKCOL":
                        status = 201
                    event = {"time": now(), "monotonic": time.monotonic(), "sequence": len(observer.events) + 1,
                             "method": self.command, "path": self.path, "response": status,
                             "bodyBytes": len(body), "bodySha256": hashlib.sha256(body).hexdigest() if body else None,
                             "mode": observer.mode}
                    observer.events.append(event)
                    LOG.mkdir(parents=True, exist_ok=True)
                    with (LOG / "mock-requests.jsonl").open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
                    if self.command == "PUT" and body:
                        (LOG / f"mock-upload-{event['sequence']:04d}.bin").write_bytes(body)
                self.send_response(status)
                self.send_header("Content-Length", str(len(output)))
                self.send_header("Content-Type", "application/json")
                self.send_header("ETag", '"vg-spec8-local-observer"')
                self.send_header("Last-Modified", "Fri, 16 Oct 2026 00:00:00 GMT")
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD" and output:
                    self.wfile.write(output)

            def __getattr__(self, name):
                if name.startswith("do_"):
                    return self.observe
                raise AttributeError(name)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self) -> None:
        self.thread.start()
        record("mock_started", address="127.0.0.1", port=self.server.server_port)

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        record("mock_stopped", count=self.count())

    def count(self) -> int:
        with self.lock:
            return len(self.events)

    def checkpoint(self, name: str, baseline: int, **values) -> dict:
        with self.lock:
            item = {"time": now(), "name": name, "baseline": baseline, "count": len(self.events),
                    "delta": len(self.events) - baseline, "requests": self.events[baseline:], **values}
        write_json(f"counter-{name}.json", item)
        record("network_checkpoint", **{key: value for key, value in item.items() if key != "requests"})
        return item


def hash_evidence() -> None:
    manifest = []
    for path in sorted(LOG.rglob("*")):
        if path.is_file() and path.name != "evidence-sha256.json":
            manifest.append({"path": path.relative_to(LOG).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size})
    write_json("evidence-sha256.json", manifest)
