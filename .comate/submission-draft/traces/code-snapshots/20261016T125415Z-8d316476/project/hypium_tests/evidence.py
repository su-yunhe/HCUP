"""Raw evidence helpers; all paths are restricted to this task."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(os.environ.get("VGSPEC9_EVIDENCE", str(ROOT / "traces/implementation-validation/device")))


def source_fingerprint():
    paths = []
    for folder in (ROOT / "entry/src", ROOT / "AppScope"):
        paths.extend(p for p in folder.rglob("*") if p.is_file())
    paths.extend(p for p in ROOT.iterdir() if p.is_file() and p.suffix in {".json5", ".ts", ".ets"})
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def save(name, value):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def event(kind, **values):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    row = {"epoch": time.time(), "monotonic": time.monotonic(), "event": kind, **values}
    with (OUTPUT / "ui-events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def hdc(*args):
    command = ["hdc"]
    if os.environ.get("HDC_DEVICE"):
        command.extend(["-t", os.environ["HDC_DEVICE"]])
    command.extend(args)
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=60)
    event("command", argv=command, exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
    if proc.returncode:
        raise RuntimeError(f"Command exited {proc.returncode}: {command}: {proc.stdout}{proc.stderr}")
    return proc.stdout


def nodes(tree):
    yield tree.get("attributes", {})
    for child in tree.get("children", []):
        yield from nodes(child)


def capture(name, screenshot=False):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    remote = f"/data/local/tmp/vg-spec9-{name}"
    hdc("shell", "uitest", "dumpLayout", "-p", remote + ".json")
    hdc("file", "recv", remote + ".json", str(OUTPUT / (name + ".json")))
    tree = json.loads((OUTPUT / (name + ".json")).read_text(encoding="utf-8"))
    if screenshot:
        hdc("shell", "uitest", "screenCap", "-p", remote + ".png")
        hdc("file", "recv", remote + ".png", str(OUTPUT / (name + ".png")))
    return list(nodes(tree))
