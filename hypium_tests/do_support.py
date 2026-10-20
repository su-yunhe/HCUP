"""Evidence helpers. Device commands run only when explicitly invoked by tests."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


PROJECT = Path(__file__).resolve().parents[1]
BUNDLE = "io.qzz.weiyu"


def source_fingerprint() -> dict[str, str]:
    """Include added production sources/resources; exclude generated build trees."""
    candidates: set[Path] = set()
    for root in (PROJECT / "entry/src", PROJECT / "AppScope", PROJECT / "hvigor"):
        if root.exists():
            candidates.update(path for path in root.rglob("*") if path.is_file())
    for pattern in ("*.json", "*.json5", "*.ts"):
        candidates.update(PROJECT.glob(pattern))
    return {path.relative_to(PROJECT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(candidates) if "build" not in path.parts
            and "oh_modules" not in path.parts}


class Evidence:
    def __init__(self, device: str):
        default = PROJECT / "traces/do-verification" / datetime.now().strftime("%Y%m%d-%H%M%S")
        self.root = Path(os.environ.get("VG7_EVIDENCE_DIR", str(default))).resolve()
        if PROJECT not in self.root.parents:
            raise ValueError("Evidence must remain inside this question directory")
        self.root.mkdir(parents=True, exist_ok=True)
        self.device = device
        self.counter = 0

    def write(self, name: str, value) -> None:
        (self.root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    def hdc(self, *args: str, check: bool = True, timeout: int = 30):
        self.counter += 1
        start = datetime.now(timezone.utc).isoformat()
        command = ["hdc", "-t", self.device, *args]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=timeout)
        record = {"start": start, "end": datetime.now(timezone.utc).isoformat(),
                  "command": command, "exit_code": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr}
        self.write(f"command-{self.counter:04d}.json", record)
        if check and result.returncode:
            raise RuntimeError(f"hdc failed ({result.returncode}): {command!r}: {result.stdout}{result.stderr}")
        return result

    def snapshot(self, label: str, screenshot: bool = True) -> dict:
        safe = re.sub(r"[^A-Za-z0-9_-]", "-", label)
        remote = f"/data/local/tmp/vg-spec7-do-{safe}"
        self.hdc("shell", f"uitest dumpLayout -p {remote}.json")
        tree_path = self.root / f"{safe}-tree.json"
        self.hdc("file", "recv", remote + ".json", str(tree_path))
        tree = json.loads(tree_path.read_text(encoding="utf-8-sig"))
        nodes = list(walk(tree))
        self.write(f"{safe}-summary.json", [{key: node.get(key, "") for key in (
            "type", "text", "hint", "id", "bounds", "enabled", "checked", "visible")}
            for node in nodes if node.get("text") or node.get("id") or
            re.search(r"Input|Button|Toggle|Dialog", node.get("type", ""))])
        if screenshot:
            self.hdc("shell", f"uitest screenCap -p {remote}.png")
            self.hdc("file", "recv", remote + ".png", str(self.root / f"{safe}.png"))
        return tree


def walk(tree: dict):
    if "attributes" in tree:
        yield tree["attributes"]
    for child in tree.get("children", []):
        yield from walk(child)


def wait_until(predicate, timeout: float = 20, interval: float = 0.2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(interval)
    return None

