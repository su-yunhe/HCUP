"""Task-local evidence collection; read-only device preparation is an explicit mode."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading

ROOT = Path(__file__).resolve().parents[2]
DEVICE = os.environ.get("HDC_DEVICE", "127.0.0.1:5555")
IGNORED = {"build", "oh_modules", ".hvigor", ".preview", ".git"}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def production_fingerprint() -> dict:
    paths = set()
    for folder in ["AppScope", "entry", "core", "feature", "hvigor"]:
        for current, subdirs, names in os.walk(ROOT / folder):
            subdirs[:] = [name for name in subdirs if name not in IGNORED]
            for name in names:
                paths.add(Path(current, name).relative_to(ROOT).as_posix())
    for path in ROOT.iterdir():
        if path.is_file() and path.suffix in {".json", ".json5", ".ts", ".properties", ".bat"}:
            paths.add(path.name)
    rows = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(paths)}
    digest = hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "root": str(ROOT),
            "sha256": digest, "files": rows}


def run_record(out: Path, label: str, args: list[str], timeout=30, cwd=None) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    def drain(name, stream):
        with (out / (label + "." + name + ".txt")).open("wb") as raw:
            for chunk in iter(stream.readline, b""):
                captured[name].extend(chunk)
                raw.write(chunk)
                raw.flush()
    threads = [threading.Thread(target=drain, args=(name, stream), daemon=True)
               for name, stream in (("stdout", process.stdout), ("stderr", process.stderr))]
    for thread in threads:
        thread.start()
    timed_out = False
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        process.wait()
    for thread in threads:
        thread.join(timeout=5)
    row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": args,
           "exit_code": process.returncode, "timed_out": timed_out,
           "stdout": captured["stdout"].decode("utf-8", errors="replace"),
           "stderr": captured["stderr"].decode("utf-8", errors="replace")}
    write_json(out / (label + ".json"), row)
    return row


def hdc_record(out: Path, label: str, *args: str) -> dict:
    hdc = shutil.which("hdc")
    if not hdc:
        raise RuntimeError("Load both Harmony environment scripts before using this helper")
    return run_record(out, label, [hdc, "-t", DEVICE, *args])


def snapshot(out: Path, label: str) -> dict:
    """Collect UI pixels/tree and exact display/window metadata without app mutation."""
    out.mkdir(parents=True, exist_ok=True)
    label = re.sub(r"[^a-zA-Z0-9_-]", "_", label)
    remote = "/data/local/tmp/cml-spec7-verification-" + label
    rows = []
    for suffix, command in [
        ("layout", ("shell", "uitest", "dumpLayout", "-p", remote + ".json")),
        ("layout-recv", ("file", "recv", remote + ".json", str(out / (label + ".ui.json")))),
        ("screenshot", ("shell", "snapshot_display", "-f", remote + ".jpeg")),
        ("screenshot-recv", ("file", "recv", remote + ".jpeg", str(out / (label + ".jpeg")))),
        ("display", ("shell", "hidumper", "-s", "DisplayManagerService", "-a", "-a")),
        ("window", ("shell", "hidumper", "-s", "WindowManagerService", "-a", "-a")),
    ]:
        rows.append(hdc_record(out, label + "-" + suffix, *command))
    if any(row["exit_code"] != 0 or "[Fail]" in row["stdout"] or "error:" in row["stdout"].lower() for row in rows):
        raise RuntimeError("Snapshot command failed; inspect raw command JSON files")
    for suffix in (".ui.json", ".jpeg"):
        if not (out / (label + suffix)).is_file() or (out / (label + suffix)).stat().st_size == 0:
            raise RuntimeError(f"Snapshot output absent/empty: {label + suffix}")
    return {"label": label, "commands": rows}


def prepare_queries(out: Path) -> None:
    """Only help/environment queries; never rotate, resize, install, start or stop apps."""
    for label, args in [
        ("software", ("shell", "param", "get", "const.product.software.version")),
        ("api", ("shell", "param", "get", "const.ohos.apiversion")),
        ("display", ("shell", "hidumper", "-s", "DisplayManagerService", "-a", "-a")),
        ("windows", ("shell", "hidumper", "-s", "WindowManagerService", "-a", "-a")),
        ("display-help", ("shell", "hidumper", "-s", "DisplayManagerService", "-a", "-h")),
        ("window-help", ("shell", "hidumper", "-s", "WindowManagerService", "-a", "-h")),
        ("uitest-help", ("shell", "uitest", "--help")),
        ("wm-help", ("shell", "wm", "help")),
    ]:
        row = hdc_record(out, label, *args)
        print(f"{label}: exit={row['exit_code']}; {row['stdout'][:160].strip()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare-queries", "fingerprint", "snapshot"])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label", default="manual")
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.relative_to(ROOT)
    if args.mode == "prepare-queries":
        prepare_queries(args.out)
    elif args.mode == "fingerprint":
        write_json(args.out, production_fingerprint())
    else:
        snapshot(args.out, args.label)
